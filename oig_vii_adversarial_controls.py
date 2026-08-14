"""Adversarial controls for the OIG Stage VII mollifier phase diagram.

The controls isolate lattice phase, preparation convention, boundary effects,
rough kernels, high-frequency dispersion, and noncommuting source diffusion.
They are intentionally independent of the canonical Stage VII implementation.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.integrate import quad
from scipy.linalg import eigh_tridiagonal
from scipy.special import ndtr


def cell_centres(n: int) -> np.ndarray:
    if n < 3:
        raise ValueError("n must be at least three")
    return (np.arange(n, dtype=float) + 0.5) / n


def neumann_mode(n: int, mode: int) -> np.ndarray:
    if not 0 <= mode < n:
        raise ValueError("mode must lie in {0,...,n-1}")
    if mode == 0:
        return np.ones(n) / math.sqrt(n)
    return math.sqrt(2 / n) * np.cos(mode * math.pi * cell_centres(n))


def cell_average_gaussian(n: int, epsilon: float, centre: float) -> np.ndarray:
    """Finite-volume masses of a Gaussian, normalized after domain truncation."""

    if epsilon <= 0 or not 0 <= centre <= 1:
        raise ValueError("invalid width or centre")
    boundaries = np.arange(n + 1, dtype=float) / n
    masses = np.diff(ndtr((boundaries - centre) / epsilon))
    total = float(np.sum(masses))
    if not total > 0:
        raise ValueError("Gaussian mass underflowed on the domain")
    return masses / total


def point_sampled_gaussian(n: int, epsilon: float, centre: float) -> np.ndarray:
    """Stable point-sampled Gaussian weights.

    In the subcell limit this selects one cell or an equal adjacent pair,
    depending on the lattice phase of ``centre``.
    """

    if epsilon <= 0 or not 0 <= centre <= 1:
        raise ValueError("invalid width or centre")
    log_weights = -0.5 * ((cell_centres(n) - centre) / epsilon) ** 2
    log_weights -= float(np.max(log_weights))
    weights = np.exp(log_weights)
    return weights / np.sum(weights)


def point_sampled_tent(n: int, epsilon: float, centre: float) -> np.ndarray:
    """Point-sampled compact tent kernel, raising if no centre hits support."""

    if epsilon <= 0 or not 0 <= centre <= 1:
        raise ValueError("invalid width or centre")
    values = np.maximum(1 - np.abs(cell_centres(n) - centre) / epsilon, 0.0)
    total = float(np.sum(values))
    if total == 0:
        raise ValueError("no cell centre lies in the compact kernel support")
    return values / total


def mean_preserving_gaussian_mixture(
    n: int, epsilon: float, centre: float
) -> np.ndarray:
    """A nonsymmetric two-Gaussian kernel whose physical mean is ``centre``."""

    # 3/4*(-0.2)+1/4*(+0.6)=0, but the shape is not reflection symmetric.
    left = cell_average_gaussian(n, epsilon, centre - 0.2 * epsilon)
    right = cell_average_gaussian(n, epsilon, centre + 0.6 * epsilon)
    return 0.75 * left + 0.25 * right


def path_laplacian_on_mass(q: np.ndarray) -> np.ndarray:
    """Apply the positive cell-centred Laplacian to probability masses."""

    q = np.asarray(q, dtype=float)
    n = q.size
    result = np.empty(n, dtype=float)
    result[0] = n**2 * (q[0] - q[1])
    result[-1] = n**2 * (q[-1] - q[-2])
    result[1:-1] = n**2 * (2 * q[1:-1] - q[:-2] - q[2:])
    return result


def ramp_first_jet_norm(q: np.ndarray, coupling: float = 1.0) -> float:
    """Exact full-source-tangent first response-jet Frobenius norm."""

    q = np.asarray(q, dtype=float)
    n = q.size
    if not np.isclose(np.sum(q), 1.0):
        raise ValueError("q must be a probability vector")
    x = cell_centres(n)
    modulation_row_norm = math.sqrt(float(np.sum((x - np.mean(x)) ** 2)))
    return coupling * float(np.linalg.norm(path_laplacian_on_mass(q))) * modulation_row_norm


def adjacent_split_atom(n: int, left_index: int, right_weight: float) -> np.ndarray:
    """Return ``(1-w)e_j+w e_{j+1}`` for an interior adjacent pair."""

    if not 1 <= left_index < n - 2 or not 0 <= right_weight <= 1:
        raise ValueError("an interior adjacent pair and probability weight are required")
    q = np.zeros(n)
    q[left_index] = 1 - right_weight
    q[left_index + 1] = right_weight
    return q


def adjacent_split_laplacian_norm_squared(right_weight: float) -> float:
    """Exact unscaled squared Laplacian norm of an interior two-cell atom."""

    if not 0 <= right_weight <= 1:
        raise ValueError("weight must lie in [0,1]")
    return 1 + 20 * (right_weight - 0.5) ** 2


def density_mode_coefficient(q: np.ndarray, mode: int) -> float:
    """Density-normalized Neumann coefficient of a probability vector."""

    q = np.asarray(q, dtype=float)
    return float(math.sqrt(q.size) * (neumann_mode(q.size, mode) @ q))


def gaussian_resolved_jet_constant() -> float:
    """Limit of ``epsilon^(5/2) * jet`` for a ramp and a standard Gaussian."""

    # ||eta''||_2^2=3/(8 sqrt(pi)); divide its norm by sqrt(12).
    return math.sqrt(1 / (32 * math.sqrt(math.pi)))


def reduced_response_scalar(
    n: int,
    target_mode: int,
    time: float,
    source_mode: int,
    modulation: np.ndarray,
    coupling: float,
) -> float:
    """Return the complete n-mode reduced response scalar."""

    modulation = np.asarray(modulation, dtype=float)
    if modulation.shape != (n,):
        raise ValueError("modulation has the wrong shape")
    mu = 4 * n**2 * math.sin(target_mode * math.pi / (2 * n)) ** 2
    diagonal = np.full(n, 2 * n**2, dtype=float)
    diagonal[[0, -1]] = n**2
    diagonal += mu * (1 + coupling * modulation)
    off_diagonal = np.full(n - 1, -n**2, dtype=float)
    eigenvalues, eigenvectors = eigh_tridiagonal(diagonal, off_diagonal)
    constant = neumann_mode(n, 0)
    source = neumann_mode(n, source_mode)
    weights = (eigenvectors.T @ constant) * (eigenvectors.T @ source)
    return float(weights @ np.exp(-time * eigenvalues))


def lattice_multiplication_limit(
    mode_ratio: float,
    diffusive_time: float,
    source_mode: int = 1,
    coupling: float = 0.8,
) -> float:
    """Fixed-port limit at ``ell/n -> mode_ratio`` and ``t=tau/n^2``."""

    sigma = 4 * diffusive_time * math.sin(math.pi * mode_ratio / 2) ** 2
    value = quad(
        lambda x: math.exp(-sigma * (1 + coupling * x))
        * math.sqrt(2)
        * math.cos(source_mode * math.pi * x),
        0,
        1,
        epsabs=2e-13,
        epsrel=2e-13,
    )[0]
    return float(value)


def naive_continuum_dispersion_limit(
    mode_ratio: float,
    diffusive_time: float,
    source_mode: int = 1,
    coupling: float = 0.8,
) -> float:
    """Incorrect critical-lattice prediction obtained from ``(pi ell)^2``."""

    sigma = diffusive_time * (math.pi * mode_ratio) ** 2
    return float(
        quad(
            lambda x: math.exp(-sigma * (1 + coupling * x))
            * math.sqrt(2)
            * math.cos(source_mode * math.pi * x),
            0,
            1,
            epsabs=2e-13,
            epsrel=2e-13,
        )[0]
    )


def high_source_operator_gap(
    mode_ratio: float, diffusive_time: float
) -> float:
    """Full-operator gap hidden by the fixed-port multiplication limit.

    With zero coupling and source mode ``k=n/2``, source diffusion contributes
    the exponent ``2*tau``.  Multiplication alone omits it.
    """

    sigma = 4 * diffusive_time * math.sin(math.pi * mode_ratio / 2) ** 2
    return math.exp(-sigma) * (1 - math.exp(-2 * diffusive_time))


_BUMP_ASYMMETRY = 0.8
_BUMP_AMPLITUDE = 0.2
_BUMP_NORMALIZATION = math.exp(-4)


def _flat_bump(x: float) -> float:
    if x <= 0 or x >= 1:
        return 0.0
    u = x * (1 - x)
    return math.exp(-1 / u) / _BUMP_NORMALIZATION


def _flat_bump_derivative(x: float) -> float:
    if x <= 0 or x >= 1:
        return 0.0
    u = x * (1 - x)
    return _flat_bump(x) * (1 - 2 * x) / u**2


def all_moment_profile(x: float) -> float:
    """Positive asymmetric profile, equal and flat at both endpoints."""

    return 1 + _BUMP_AMPLITUDE * _flat_bump(x) * (
        1 + _BUMP_ASYMMETRY * (x - 0.5)
    )


def all_moment_source(x: float) -> float:
    """The source ``phi=V'`` for the all-pure-moments counterexample."""

    factor = 1 + _BUMP_ASYMMETRY * (x - 0.5)
    return _BUMP_AMPLITUDE * (
        _flat_bump_derivative(x) * factor
        + _BUMP_ASYMMETRY * _flat_bump(x)
    )


def pure_multiplication_moment(power: int) -> float:
    """Numerically audit ``int V^power V'``, which is exactly zero."""

    if power < 0:
        raise ValueError("power must be nonnegative")
    return float(
        quad(
            lambda x: all_moment_profile(x) ** power * all_moment_source(x),
            0,
            1,
            epsabs=2e-13,
            epsrel=2e-13,
        )[0]
    )


def mixed_third_derivative_coefficient(target_eigenvalue: float = 1.0) -> float:
    """Return ``<1,K^3 phi>`` for the all-moment counterexample.

    For ``phi=V'`` with all derivatives flat at the endpoints, integration by
    parts gives ``<1,K^3 phi>=-(lambda^2/2) int (V')^3`` even though
    ``int V^r phi=0`` for every r.
    """

    cubic = quad(
        lambda x: all_moment_source(x) ** 3,
        0,
        1,
        epsabs=2e-13,
        epsrel=2e-13,
    )[0]
    return float(-0.5 * target_eigenvalue**2 * cubic)


def all_moment_source_norm() -> float:
    """Return the continuum ``L2`` norm of the counterexample source."""

    squared_norm = quad(
        lambda x: all_moment_source(x) ** 2,
        0,
        1,
        epsabs=2e-13,
        epsrel=2e-13,
    )[0]
    return float(math.sqrt(squared_norm))


def normalized_mixed_third_derivative_coefficient(
    target_eigenvalue: float = 1.0,
) -> float:
    """Return ``<1,K^3 phi>`` after normalizing ``phi`` in continuum ``L2``."""

    return mixed_third_derivative_coefficient(
        target_eigenvalue
    ) / all_moment_source_norm()


def critical_alpha(moment_order: int) -> float:
    if moment_order < 1:
        raise ValueError("moment order must be positive")
    return 4 * moment_order / (4 * moment_order + 1)


if __name__ == "__main__":
    n = 1024
    for phase in (0.0, 0.25, 0.5):
        centre = (n // 2 + phase) / n
        q = cell_average_gaussian(n, 0.25 / n, centre)
        print("critical phase", phase, ramp_first_jet_norm(q) / n**2.5)
    print("resolved Gaussian constant", gaussian_resolved_jet_constant())
    print("all pure moments", [pure_multiplication_moment(r) for r in range(1, 7)])
    print("mixed third derivative", mixed_third_derivative_coefficient())
    print("source L2 norm", all_moment_source_norm())
    print(
        "normalized mixed third derivative",
        normalized_mixed_third_derivative_coefficient(),
    )
