"""Adversarial controls for OIG Stage VI continuum-limit claims.

This module deliberately isolates distinctions which are easy to blur:

* fixed modal matrix elements versus a full operator norm;
* qualitative Mosco convergence versus a quantitative second-order rate;
* a nearest-cell atom versus a moment-preserving two-cell atom;
* the cell-centred spacing ``h=1/n`` versus relabelling the same matrix with
  ``h=1/(n-1)``;
* fixed modes/times versus modes and times that scale with the mesh.

The functions do not modify any Stage I--V implementation.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.integrate import quad


def cell_centres(n: int) -> np.ndarray:
    """Return the centres of the ``n`` equal cells in ``[0,1]``."""

    if n < 2:
        raise ValueError("n must be at least two")
    return (np.arange(n, dtype=float) + 0.5) / n


def neumann_mode(n: int, mode: int) -> np.ndarray:
    """Euclidean-normalized cell-centred Neumann cosine mode."""

    if not 0 <= mode < n:
        raise ValueError("mode must lie in {0,...,n-1}")
    if mode == 0:
        return np.ones(n) / math.sqrt(n)
    return math.sqrt(2 / n) * np.cos(mode * math.pi * cell_centres(n))


def exact_discrete_eigenvalue(n: int, mode: int, spacing: float | None = None) -> float:
    """Eigenvalue of the path Laplacian under a chosen spacing convention."""

    if not 0 <= mode < n:
        raise ValueError("mode must lie in {0,...,n-1}")
    h = 1 / n if spacing is None else float(spacing)
    return 4 * math.sin(mode * math.pi / (2 * n)) ** 2 / h**2


def modulation_values(n: int, kind: str, alpha: float = 1 / 3) -> np.ndarray:
    """Profiles used to falsify regularity-free rate claims."""

    x = cell_centres(n)
    if kind == "linear":
        return x
    if kind == "step":
        return (x < alpha).astype(float)
    if kind == "holder_half":
        return np.abs(x - alpha) ** 0.5
    if kind == "symmetric_quadratic":
        return (x - 0.5) ** 2
    raise ValueError(f"unknown modulation kind: {kind}")


def first_modal_response_jet(
    n: int,
    kind: str,
    *,
    source_mode: int = 1,
    transverse_mode: int = 1,
    target_amplitude: float = 0.2,
    coupling: float = 0.6,
    alpha: float = 1 / 3,
) -> float:
    """Exact discrete derivative of the constant-output modal response at zero."""

    d = modulation_values(n, kind, alpha)
    phi = math.sqrt(2) * np.cos(source_mode * math.pi * cell_centres(n))
    mu = exact_discrete_eigenvalue(n, transverse_mode)
    return -target_amplitude * coupling * mu * float(np.mean(d * phi))


def continuum_first_modal_response_jet(
    kind: str,
    *,
    source_mode: int = 1,
    transverse_mode: int = 1,
    target_amplitude: float = 0.2,
    coupling: float = 0.6,
    alpha: float = 1 / 3,
) -> float:
    """Continuum jet for the linear, jump, and half-Holder profiles."""

    k = source_mode
    if kind == "linear":
        integral = math.sqrt(2) * (((-1) ** k) - 1) / (k * math.pi) ** 2
    elif kind == "step":
        integral = math.sqrt(2) * math.sin(k * math.pi * alpha) / (k * math.pi)
    elif kind == "holder_half":
        integrand = lambda x: (
            abs(x - alpha) ** 0.5
            * math.sqrt(2)
            * math.cos(k * math.pi * x)
        )
        # Split at the cusp so the two smooth-side quadratures are stable.
        integral = quad(integrand, 0, alpha, epsabs=1e-13, epsrel=1e-13)[0]
        integral += quad(integrand, alpha, 1, epsabs=1e-13, epsrel=1e-13)[0]
    else:
        raise ValueError("continuum control is not implemented for this profile")
    lam = (transverse_mode * math.pi) ** 2
    return -target_amplitude * coupling * lam * integral


def modal_response_scalar(
    n: int,
    time: float,
    kind: str,
    *,
    source_mode: int = 1,
    observable_mode: int = 0,
    transverse_mode: int = 1,
    coupling: float = 0.6,
    alpha: float = 1 / 3,
) -> float:
    """Compute ``<phi_r, exp(-t K_{ell,n}) phi_k>`` without modal truncation."""

    if time < 0:
        raise ValueError("time must be nonnegative")
    d = modulation_values(n, kind, alpha)
    mu = exact_discrete_eigenvalue(n, transverse_mode)
    diagonal = np.full(n, 2 * n**2, dtype=float)
    diagonal[[0, -1]] = n**2
    diagonal += mu * (1 + coupling * d)
    off_diagonal = np.full(n - 1, -n**2, dtype=float)
    eigenvalues, eigenvectors = eigh_tridiagonal(diagonal, off_diagonal)
    source = neumann_mode(n, source_mode)
    observable = neumann_mode(n, observable_mode)
    weights = (eigenvectors.T @ observable) * (eigenvectors.T @ source)
    return float(weights @ np.exp(-time * eigenvalues))


def nearest_cell_atom_coefficient(n: int, location: float, mode: int) -> float:
    """Density-normalized fixed modal coefficient of a nearest-cell atom."""

    if not 0 < location < 1:
        raise ValueError("this control uses an interior atom")
    index = min(int(math.floor(n * location)), n - 1)
    # sqrt(n) times the Euclidean DCT coefficient of e_index.
    return float(math.sqrt(n) * neumann_mode(n, mode)[index])


def split_atom_coefficient(n: int, location: float, mode: int) -> float:
    """Modal coefficient of a two-cell atom preserving mass and first moment."""

    if not 1 / (2 * n) < location < 1 - 1 / (2 * n):
        raise ValueError("location must be bracketed by two cell centres")
    x = cell_centres(n)
    left = int(math.floor(n * location - 0.5))
    right = left + 1
    right_weight = (location - x[left]) / (x[right] - x[left])
    values = math.sqrt(n) * neumann_mode(n, mode)
    return float((1 - right_weight) * values[left] + right_weight * values[right])


def continuum_atom_coefficient(location: float, mode: int) -> float:
    """Coefficient of ``delta_location`` against a Neumann mode."""

    if mode == 0:
        return 1.0
    return math.sqrt(2) * math.cos(mode * math.pi * location)


def shrinking_time_high_mode_gap() -> float:
    """Nonzero full-band gap for ``k=n/2`` and ``t_n=n^-2``.

    For even ``n``, the discrete exponent is exactly ``2`` while the continuum
    exponent is ``pi^2/4``.  The value is independent of ``n``.
    """

    return abs(math.exp(-2) - math.exp(-(math.pi**2) / 4))


def audit_tables() -> dict[str, list[dict[str, float]]]:
    """Return compact numerical tables used in the adversarial memo."""

    grids = (32, 64, 128, 256, 512)
    response: list[dict[str, float]] = []
    for kind in ("linear", "step"):
        values = {
            n: modal_response_scalar(n, 0.05, kind)
            for n in (*grids, 1024)
        }
        for n in grids:
            difference = abs(values[n] - values[2 * n])
            next_difference = abs(values[2 * n] - values[4 * n]) if n <= 256 else math.nan
            response.append(
                {
                    "kind": kind,
                    "n": float(n),
                    "difference_n_2n": difference,
                    "doubling_ratio": difference / next_difference,
                }
            )

    atoms: list[dict[str, float]] = []
    location = 1 / 3
    exact = continuum_atom_coefficient(location, 1)
    for n in grids:
        atoms.append(
            {
                "n": float(n),
                "nearest_error": abs(nearest_cell_atom_coefficient(n, location, 1) - exact),
                "split_error": abs(split_atom_coefficient(n, location, 1) - exact),
            }
        )
    return {"response": response, "atoms": atoms}


if __name__ == "__main__":
    import pprint

    pprint.pp(audit_tables())
    print("shrinking-time high-mode gap:", shrinking_time_high_mode_gap())
