#!/usr/bin/env python3
"""Stage VIII laboratory for the OIG three-parameter comparison.

The three dimensionless parameters are

    n=1/h,  c=epsilon/h,  tau=t/h^2,

with q=t/epsilon^2=tau/c^2 when c>0.  The laboratory compares the exact
finite, density-normalized full-target response with

* the infinite-lattice phase Psi(c,theta,tau), and
* the resolved continuum phase P(q).

The finite response is computed by exact separation of the target Neumann
modes followed by symmetric tridiagonal eigendecomposition on the source.
"Exact" below means an algebraic identity of the declared finite model;
reported numerical values are ordinary floating-point evidence, never
outward-rounded certificates.

The code deliberately includes hostile parameter paths.  In particular it
shows why a comparison cannot be uniform in relative error at null ports,
cannot omit the subcell placement phase at c=O(1), and cannot use either
initial-layer chart when the corresponding physical small-time hypothesis is
removed.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import sys
from dataclasses import dataclass
from functools import lru_cache
from typing import Callable, Iterable, Sequence

import numpy as np
import scipy
from scipy.integrate import quad
from scipy.linalg import eigh_tridiagonal, expm
from scipy.special import ndtr


INTERACTION_STRENGTH = 4.0 / 5.0
DEFAULT_SOURCE_MODES = (1, 2, 3, 4)


def cell_centres(side_length: int) -> np.ndarray:
    """Cell centres (j+1/2)/n."""
    if side_length < 3:
        raise ValueError("side_length must be at least three")
    return (np.arange(side_length, dtype=float) + 0.5) / side_length


def cosine_modes(side_length: int, modes: Sequence[int]) -> np.ndarray:
    """Euclidean-orthonormal cell-centred Neumann cosine modes."""
    indices = tuple(int(mode) for mode in modes)
    if not indices or any(mode < 0 or mode >= side_length for mode in indices):
        raise ValueError("mode indices must be a nonempty subset of [0,n)")
    x = cell_centres(side_length)
    columns = []
    for mode in indices:
        if mode == 0:
            columns.append(np.ones(side_length) / math.sqrt(side_length))
        else:
            columns.append(
                math.sqrt(2.0 / side_length) * np.cos(math.pi * mode * x)
            )
    return np.column_stack(columns)


def lattice_symbol(side_length: int) -> np.ndarray:
    """omega_l=mu_l h^2=4 sin^2(pi l/(2n))."""
    indices = np.arange(side_length, dtype=float)
    return 4.0 * np.sin(math.pi * indices / (2.0 * side_length)) ** 2


def raw_neumann_path(side_length: int) -> np.ndarray:
    """The unscaled path Laplacian L_n=h^2 A_n."""
    matrix = np.zeros((side_length, side_length), dtype=float)
    np.fill_diagonal(matrix, 2.0)
    matrix[0, 0] = matrix[-1, -1] = 1.0
    positions = np.arange(side_length - 1)
    matrix[positions, positions + 1] = -1.0
    matrix[positions + 1, positions] = -1.0
    return matrix


def ramp_modulation(
    side_length: int,
    interaction_strength: float = INTERACTION_STRENGTH,
) -> np.ndarray:
    """Canonical V(x)=1+g x sampled at cell centres."""
    if interaction_strength < 0.0:
        raise ValueError("interaction_strength must be nonnegative")
    return 1.0 + interaction_strength * cell_centres(side_length)


def symmetric_modulation(
    side_length: int,
    interaction_strength: float = INTERACTION_STRENGTH,
) -> np.ndarray:
    """Reflection-symmetric positive control V(x)=1+g(x-1/2)^2."""
    if interaction_strength < 0.0:
        raise ValueError("interaction_strength must be nonnegative")
    return 1.0 + interaction_strength * (cell_centres(side_length) - 0.5) ** 2


def _default_anchor(side_length: int) -> int:
    """Central carrier cell; odd n puts its centre exactly at 1/2."""
    return (side_length - 1) // 2


def preparation_centre(
    side_length: int,
    placement_phase: float = 0.0,
    anchor: int | None = None,
) -> float:
    """Physical centre whose offset from the anchor centre is theta*h."""
    if not -0.5 <= placement_phase <= 0.5:
        raise ValueError("placement_phase must lie in [-1/2,1/2]")
    cell = _default_anchor(side_length) if anchor is None else int(anchor)
    if not 0 <= cell < side_length:
        raise ValueError("anchor is outside the grid")
    centre = (cell + 0.5 + placement_phase) / side_length
    if not 0.0 < centre < 1.0:
        raise ValueError("preparation centre must be interior")
    return centre


def gaussian_cell_masses(
    side_length: int,
    width_ratio: float,
    placement_phase: float = 0.0,
    anchor: int | None = None,
) -> np.ndarray:
    """Conservative cell masses for epsilon/h=c and local phase theta.

    ``c=0`` denotes the declared point-mass convention.  At an exact cell
    boundary it is the symmetric half/half weak limit of an even Gaussian.
    """
    n = side_length
    c = float(width_ratio)
    theta = float(placement_phase)
    if c < 0.0:
        raise ValueError("width_ratio must be nonnegative")
    centre = preparation_centre(n, theta, anchor)
    carrier = _default_anchor(n) if anchor is None else int(anchor)
    if c == 0.0:
        masses = np.zeros(n)
        if math.isclose(theta, 0.5, rel_tol=0.0, abs_tol=1e-15):
            if carrier + 1 >= n:
                raise ValueError("boundary split leaves the grid")
            masses[carrier : carrier + 2] = 0.5
        elif math.isclose(theta, -0.5, rel_tol=0.0, abs_tol=1e-15):
            if carrier == 0:
                raise ValueError("boundary split leaves the grid")
            masses[carrier - 1 : carrier + 1] = 0.5
        else:
            nearest = int(np.argmin(np.abs(cell_centres(n) - centre)))
            masses[nearest] = 1.0
        return masses
    epsilon = c / n
    edges = np.arange(n + 1, dtype=float) / n
    cdf = ndtr((edges - centre) / epsilon)
    masses = np.diff(cdf)
    total = float(np.sum(masses))
    if not total > 0.0:
        raise FloatingPointError("Gaussian mass underflowed")
    masses /= total
    return masses


def gaussian_mass_outside_interval(epsilon: float, centre: float = 0.5) -> float:
    """Untruncated standard-Gaussian mass outside [0,1]."""
    if epsilon <= 0.0 or not 0.0 < centre < 1.0:
        raise ValueError("epsilon and centre must be positive/interior")
    return float(
        ndtr(-centre / epsilon) + ndtr(-(1.0 - centre) / epsilon)
    )


def target_coefficients(probability: np.ndarray) -> np.ndarray:
    """Finite target cosine coefficients beta_l=u_l^T q."""
    masses = np.asarray(probability, dtype=float)
    if masses.ndim != 1 or len(masses) < 3:
        raise ValueError("probability must be a one-dimensional grid vector")
    return cosine_modes(len(masses), range(len(masses))).T @ masses


@dataclass(frozen=True)
class ScaledModalKernel:
    """Finite source coefficients at t=tau*h^2.

    ``values[a,l,b]`` is 1^T exp[-tau_a(L_n+omega_l V_n)] u_{k_b}.
    """

    side_length: int
    lattice_times: np.ndarray
    source_modes: tuple[int, ...]
    modulation: np.ndarray
    values: np.ndarray


def scaled_modal_kernel(
    side_length: int,
    lattice_times: Sequence[float],
    source_modes: Sequence[int] = DEFAULT_SOURCE_MODES,
    modulation: np.ndarray | None = None,
) -> ScaledModalKernel:
    """Exact target-mode reduction, evaluated in floating point."""
    n = int(side_length)
    taus = np.asarray(lattice_times, dtype=float)
    sources = tuple(int(mode) for mode in source_modes)
    if taus.ndim != 1 or len(taus) == 0 or np.any(taus < 0.0):
        raise ValueError("lattice_times must be a nonempty nonnegative vector")
    if any(mode < 1 or mode >= n for mode in sources):
        raise ValueError("source modes must lie in [1,n)")
    potential = ramp_modulation(n) if modulation is None else np.asarray(
        modulation, dtype=float
    )
    if potential.shape != (n,) or np.min(potential) <= 0.0:
        raise ValueError("modulation must be a positive vector of length n")

    diagonal_l = np.full(n, 2.0)
    diagonal_l[[0, -1]] = 1.0
    off_diagonal = np.full(n - 1, -1.0)
    omega = lattice_symbol(n)
    source_matrix = cosine_modes(n, sources)
    ones = np.ones(n)
    values = np.zeros((len(taus), n, len(sources)))

    # l=0 vanishes exactly for every declared nonconstant source.  For small
    # tau use expm1 and the exact identity 1^T u_k=0 to avoid subtracting two
    # nearly equal numbers.  For large tau use exp directly, avoiding the
    # inverse cancellation that expm1 would create as exp -> 0.
    for target_mode in range(1, n):
        eigenvalues, eigenvectors = eigh_tridiagonal(
            diagonal_l + omega[target_mode] * potential,
            off_diagonal,
            check_finite=False,
        )
        coefficients = (ones @ eigenvectors)[:, None] * (
            eigenvectors.T @ source_matrix
        )
        small = taus <= 0.25
        if np.any(small):
            values[small, target_mode, :] = (
                np.expm1(-np.outer(taus[small], eigenvalues)) @ coefficients
            )
        if np.any(~small):
            values[~small, target_mode, :] = (
                np.exp(-np.outer(taus[~small], eigenvalues)) @ coefficients
            )
    return ScaledModalKernel(n, taus, sources, potential.copy(), values)


def response_norms(
    kernel: ScaledModalKernel,
    target_probability: np.ndarray,
) -> np.ndarray:
    """Full density-normalized norm for each time/source."""
    masses = np.asarray(target_probability, dtype=float)
    if masses.shape != (kernel.side_length,):
        raise ValueError("target_probability has the wrong shape")
    beta = target_coefficients(masses)
    return np.linalg.norm(kernel.values * beta[None, :, None], axis=1)


def scaled_response_norms(
    kernel: ScaledModalKernel,
    target_probability: np.ndarray,
) -> np.ndarray:
    """Return ||R_n||/sqrt(n), the finite lattice-chart normalization."""
    return response_norms(kernel, target_probability) / math.sqrt(
        kernel.side_length
    )


def direct_dense_modal_response(
    side_length: int,
    lattice_time: float,
    source_mode: int,
    target_probability: np.ndarray,
    modulation: np.ndarray | None = None,
) -> np.ndarray:
    """Small-n n^2-state control in target cosine coordinates."""
    n = side_length
    potential = ramp_modulation(n) if modulation is None else np.asarray(
        modulation, dtype=float
    )
    raw = raw_neumann_path(n)
    generator = np.kron(raw, np.eye(n)) + np.kron(np.diag(potential), raw)
    source = cosine_modes(n, (source_mode,))[:, 0]
    injection = np.kron(source / math.sqrt(n), target_probability)
    marginal = np.kron(np.ones((1, n)), np.eye(n))
    target_modes = cosine_modes(n, range(n))
    physical = marginal @ expm(-lattice_time * generator) @ injection
    return math.sqrt(n) * target_modes.T @ physical


def ramp_source_profile(
    scaled_target_rate: float | np.ndarray,
    source_mode: int,
    interaction_strength: float = INTERACTION_STRENGTH,
) -> float | np.ndarray:
    """F_k(s)=integral exp[-s(1+gx)] sqrt(2)cos(k pi x) dx."""
    if source_mode < 1 or interaction_strength < 0.0:
        raise ValueError("invalid source mode or interaction strength")
    s = np.asarray(scaled_target_rate, dtype=float)
    a = interaction_strength * s
    denominator = a * a + (math.pi * source_mode) ** 2
    if source_mode % 2:
        endpoint_factor = 1.0 + np.exp(-a)
    else:
        endpoint_factor = -np.expm1(-a)
    result = (
        math.sqrt(2.0)
        * np.exp(-s)
        * a
        * endpoint_factor
        / denominator
    )
    if result.ndim == 0:
        return float(result)
    return result


def gaussian_lattice_weights(
    width_ratio: float,
    placement_phase: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Infinite-lattice cell averages Q_m^(c,theta)."""
    c = float(width_ratio)
    theta = float(placement_phase)
    if c < 0.0 or not -0.5 <= theta <= 0.5:
        raise ValueError("invalid width ratio or placement phase")
    if c == 0.0:
        if math.isclose(abs(theta), 0.5, rel_tol=0.0, abs_tol=1e-15):
            if theta > 0:
                return np.asarray((0, 1)), np.asarray((0.5, 0.5))
            return np.asarray((-1, 0)), np.asarray((0.5, 0.5))
        return np.asarray((0,)), np.asarray((1.0,))
    radius = max(2, int(math.ceil(abs(theta) + 9.0 * c + 0.5)))
    offsets = np.arange(-radius, radius + 1)
    upper = (offsets + 0.5 - theta) / c
    lower = (offsets - 0.5 - theta) / c
    masses = ndtr(upper) - ndtr(lower)
    total = float(np.sum(masses))
    if not total > 0.0:
        raise FloatingPointError("infinite-lattice Gaussian mass underflowed")
    masses /= total
    return offsets, masses


@lru_cache(maxsize=8192)
def lattice_phase_norm(
    lattice_time: float,
    width_ratio: float,
    source_mode: int,
    placement_phase: float = 0.0,
    interaction_strength: float = INTERACTION_STRENGTH,
) -> float:
    """Infinite-lattice phase Psi_(c,theta), by adaptive quadrature."""
    tau = float(lattice_time)
    if tau <= 0.0:
        raise ValueError("lattice_time must be positive")
    offsets, masses = gaussian_lattice_weights(width_ratio, placement_phase)

    def integrand(xi: float) -> float:
        transform = np.exp(1j * math.pi * xi * offsets) @ masses
        scaled_rate = 4.0 * tau * math.sin(math.pi * xi / 2.0) ** 2
        profile = ramp_source_profile(
            scaled_rate, source_mode, interaction_strength
        )
        return float(abs(transform) ** 2 * profile**2)

    value, _ = quad(
        integrand,
        0.0,
        1.0,
        epsabs=2e-12,
        epsrel=2e-12,
        limit=250,
    )
    return math.sqrt(max(value, 0.0))


@lru_cache(maxsize=2048)
def continuum_phase_norm(
    continuum_time_ratio: float,
    source_mode: int,
    interaction_strength: float = INTERACTION_STRENGTH,
) -> float:
    """Resolved continuum phase P_k(q) for a standard Gaussian."""
    q = float(continuum_time_ratio)
    if q <= 0.0:
        raise ValueError("continuum_time_ratio must be positive")

    def integrand(u: float) -> float:
        transform_squared = math.exp(-(math.pi * u) ** 2)
        profile = ramp_source_profile(
            q * (math.pi * u) ** 2, source_mode, interaction_strength
        )
        return transform_squared * profile**2

    value, _ = quad(
        integrand,
        0.0,
        np.inf,
        epsabs=2e-12,
        epsrel=2e-12,
        limit=250,
    )
    return math.sqrt(max(value, 0.0))


@lru_cache(maxsize=64)
def atomic_phase_constant(
    source_mode: int,
    interaction_strength: float = INTERACTION_STRENGTH,
) -> float:
    """C_infinity with P(q)~C_infinity q^-1/4."""

    def integrand(u: float) -> float:
        profile = ramp_source_profile(
            (math.pi * u) ** 2, source_mode, interaction_strength
        )
        return profile**2

    value, _ = quad(
        integrand,
        0.0,
        np.inf,
        epsabs=2e-12,
        epsrel=2e-12,
        limit=250,
    )
    return math.sqrt(max(value, 0.0))


@lru_cache(maxsize=64)
def multiplication_moment(
    order: int,
    source_mode: int,
    interaction_strength: float = INTERACTION_STRENGTH,
) -> float:
    """m_r=integral V(x)^r phi_k(x) dx for the canonical ramp."""
    if order < 0 or source_mode < 1:
        raise ValueError("invalid moment order or source mode")
    value, _ = quad(
        lambda x: (1.0 + interaction_strength * x) ** order
        * math.sqrt(2.0)
        * math.cos(math.pi * source_mode * x),
        0.0,
        1.0,
        epsabs=1e-13,
        epsrel=1e-13,
        limit=100,
    )
    # Reflection makes m_1 exactly zero for even cosine modes of a ramp.
    if order == 1 and source_mode % 2 == 0:
        return 0.0
    return float(value)


def gaussian_even_derivative_norm(order: int) -> float:
    """||eta^(2r)||_2 for the standard normal density."""
    if order < 0:
        raise ValueError("order must be nonnegative")
    return math.sqrt(math.gamma(2 * order + 0.5) / (2.0 * math.pi))


def early_phase_constant(
    source_mode: int,
    interaction_strength: float = INTERACTION_STRENGTH,
) -> tuple[int, float]:
    """Multiplication order and leading Gaussian phase coefficient.

    For the ramp, odd modes have r=1 and even modes have r=2.
    """
    order = 1 if source_mode % 2 else 2
    moment = multiplication_moment(order, source_mode, interaction_strength)
    coefficient = (
        abs(moment)
        / math.factorial(order)
        * gaussian_even_derivative_norm(order)
    )
    return order, coefficient


def safe_relative_error(value: float, reference: float) -> float | None:
    """Relative error, deliberately undefined at an exact null reference."""
    if reference == 0.0:
        return None
    return abs(value - reference) / abs(reference)


def comparison_point(
    kernel: ScaledModalKernel,
    time_index: int,
    width_ratio: float,
    placement_phase: float,
    source_index: int,
) -> dict[str, float | int | None]:
    """One finite/lattice/continuum comparison point."""
    n = kernel.side_length
    tau = float(kernel.lattice_times[time_index])
    mode = int(kernel.source_modes[source_index])
    masses = gaussian_cell_masses(n, width_ratio, placement_phase)
    finite = float(scaled_response_norms(kernel, masses)[time_index, source_index])
    lattice = lattice_phase_norm(tau, width_ratio, mode, placement_phase)
    result: dict[str, float | int | None] = {
        "side_length": n,
        "source_mode": mode,
        "epsilon_over_h": float(width_ratio),
        "t_over_h_squared": tau,
        "placement_phase": float(placement_phase),
        "finite_norm_over_sqrt_n": finite,
        "lattice_phase": lattice,
        "finite_lattice_absolute_error": abs(finite - lattice),
        "finite_lattice_relative_error": safe_relative_error(finite, lattice),
    }
    if width_ratio > 0.0:
        q = tau / width_ratio**2
        continuum = continuum_phase_norm(q, mode)
        finite_continuum = math.sqrt(width_ratio) * finite
        lattice_continuum = math.sqrt(width_ratio) * lattice
        left = abs(finite_continuum - continuum)
        decomposition = abs(finite_continuum - lattice_continuum) + abs(
            lattice_continuum - continuum
        )
        result.update(
            {
                "t_over_epsilon_squared": q,
                "sqrt_epsilon_times_finite_norm": finite_continuum,
                "continuum_phase": continuum,
                "finite_continuum_absolute_error": left,
                "finite_continuum_relative_error": safe_relative_error(
                    finite_continuum, continuum
                ),
                "triangle_decomposition_upper_bound": decomposition,
                "triangle_slack": decomposition - left,
            }
        )
    return result


def _loglog_slope(scales: Sequence[float], errors: Sequence[float]) -> float:
    """Least-squares power p in error approximately scale^p."""
    x = np.asarray(scales, dtype=float)
    y = np.asarray(errors, dtype=float)
    mask = (x > 0.0) & (y > 2e-14) & np.isfinite(y)
    if np.count_nonzero(mask) < 2:
        return float("nan")
    return float(np.polyfit(np.log(x[mask]), np.log(y[mask]), 1)[0])


def exact_identity_audit() -> dict[str, object]:
    """Roundoff checks of identities that are exact in the finite model."""
    n = 7
    tau = 0.17
    mode = 2
    c = 0.73
    theta = 0.31
    q = gaussian_cell_masses(n, c, theta)
    kernel = scaled_modal_kernel(n, (tau,), (mode,))
    beta = target_coefficients(q)
    modal = kernel.values[0, :, 0] * beta
    dense = direct_dense_modal_response(n, tau, mode, q)
    point = comparison_point(kernel, 0, c, theta, 0)

    # Exact finite first jet: -g(1^T D u_k) omega_l beta_l in the scaled
    # clock tau.  Compare it with a centred difference of the reduced
    # semigroup only as a floating check; the displayed formula is algebraic.
    x = cell_centres(n)
    source = cosine_modes(n, (1,))[:, 0]
    moment = float(x @ source)
    jet_formula = -INTERACTION_STRENGTH * moment * lattice_symbol(n) * beta
    delta = 2e-6
    plus = scaled_modal_kernel(n, (delta,), (1,)).values[0, :, 0] * beta
    jet_difference = plus / delta
    return {
        "exact_statements": [
            "target-mode separation of the finite Kronecker generator",
            "full norm is the Euclidean norm of beta_l a_lk",
            "scaled first jet is -g(1^T D u_k) omega_l beta_l",
            "the continuum comparison error obeys the displayed triangle decomposition",
            "constant modulation and reflection-odd/symmetric pairs are exact nulls",
        ],
        "floating_roundoff_checks": {
            "probability_mass_error": abs(float(np.sum(q)) - 1.0),
            "dense_modal_maximum_error": float(np.max(np.abs(dense - modal))),
            "dense_modal_relative_l2_error": float(
                np.linalg.norm(dense - modal) / np.linalg.norm(dense)
            ),
            "first_jet_forward_difference_relative_error": float(
                np.linalg.norm(jet_difference - jet_formula)
                / np.linalg.norm(jet_formula)
            ),
            "triangle_slack": point["triangle_slack"],
        },
    }


def broad_grid_audit(
    side_lengths: Sequence[int] = (31, 63, 127),
    width_ratios: Sequence[float] = (0.05, 0.25, 1.0, 4.0),
    lattice_times: Sequence[float] = (0.003, 0.03, 0.3, 3.0, 30.0),
    source_modes: Sequence[int] = DEFAULT_SOURCE_MODES,
    placement_phases: Sequence[float] = (0.0, 0.25, 0.5),
) -> dict[str, object]:
    """Stress the two phase charts on a rectangular finite grid."""
    rows: list[dict[str, float | int | None]] = []
    per_n = []
    for n in side_lengths:
        kernel = scaled_modal_kernel(n, lattice_times, source_modes)
        start = len(rows)
        for time_index, _tau in enumerate(lattice_times):
            for c in width_ratios:
                for theta in placement_phases:
                    for source_index, _mode in enumerate(source_modes):
                        rows.append(
                            comparison_point(
                                kernel, time_index, c, theta, source_index
                            )
                        )
        local = rows[start:]
        lattice_errors = np.asarray(
            [float(row["finite_lattice_absolute_error"]) for row in local]
        )
        continuum_relative = np.asarray(
            [
                float(row["finite_continuum_relative_error"])
                for row in local
                if row["finite_continuum_relative_error"] is not None
            ]
        )
        per_n.append(
            {
                "side_length": int(n),
                "points": len(local),
                "median_finite_lattice_absolute_error": float(
                    np.median(lattice_errors)
                ),
                "maximum_finite_lattice_absolute_error": float(
                    np.max(lattice_errors)
                ),
                "median_finite_continuum_relative_error": float(
                    np.median(continuum_relative)
                ),
                "maximum_finite_continuum_relative_error": float(
                    np.max(continuum_relative)
                ),
            }
        )
    worst_lattice = max(
        rows, key=lambda row: float(row["finite_lattice_absolute_error"])
    )
    worst_continuum = max(
        rows,
        key=lambda row: float(row["finite_continuum_relative_error"] or 0.0),
    )
    return {
        "grid": {
            "side_lengths": list(map(int, side_lengths)),
            "epsilon_over_h": list(map(float, width_ratios)),
            "t_over_h_squared": list(map(float, lattice_times)),
            "source_modes": list(map(int, source_modes)),
            "placement_phases": list(map(float, placement_phases)),
            "total_points": len(rows),
        },
        "per_side_length": per_n,
        "worst_finite_lattice_absolute_point": worst_lattice,
        "worst_naive_continuum_relative_point": worst_continuum,
        "interpretation": (
            "the lattice reference is the local c=O(1) comparison; the continuum "
            "column is intentionally evaluated everywhere and therefore records "
            "large failures outside the resolved overlap"
        ),
    }


def finite_lattice_rate_audit(
    side_lengths: Sequence[int] = (31, 63, 127, 255),
    width_ratios: Sequence[float] = (0.25, 1.0, 4.0),
    lattice_times: Sequence[float] = (0.03, 0.3, 3.0),
    source_modes: Sequence[int] = (1, 2),
    placement_phases: Sequence[float] = (0.0, 0.5),
) -> dict[str, object]:
    """Empirical h-rates at fixed (c,tau,k,theta)."""
    by_key: dict[tuple[float, float, int, float], list[dict[str, float]]] = {}
    for n in side_lengths:
        kernel = scaled_modal_kernel(n, lattice_times, source_modes)
        for time_index, tau in enumerate(lattice_times):
            for c in width_ratios:
                for theta in placement_phases:
                    masses = gaussian_cell_masses(n, c, theta)
                    finite_all = scaled_response_norms(kernel, masses)
                    for source_index, mode in enumerate(source_modes):
                        finite = float(finite_all[time_index, source_index])
                        reference = lattice_phase_norm(tau, c, mode, theta)
                        key = (float(c), float(tau), int(mode), float(theta))
                        by_key.setdefault(key, []).append(
                            {
                                "side_length": float(n),
                                "absolute_error": abs(finite - reference),
                                "relative_error": abs(finite / reference - 1.0),
                            }
                        )
    fits = []
    for key, values in sorted(by_key.items()):
        ns = [row["side_length"] for row in values]
        absolute = [row["absolute_error"] for row in values]
        fits.append(
            {
                "epsilon_over_h": key[0],
                "t_over_h_squared": key[1],
                "source_mode": key[2],
                "placement_phase": key[3],
                "empirical_power_in_n": _loglog_slope(ns, absolute),
                "first_absolute_error": absolute[0],
                "last_absolute_error": absolute[-1],
                "last_relative_error": values[-1]["relative_error"],
            }
        )
    slopes = np.asarray([row["empirical_power_in_n"] for row in fits])
    return {
        "fit_convention": "absolute error approximately n^p; decay means p<0",
        "side_lengths": list(map(int, side_lengths)),
        "fits": fits,
        "slope_summary": {
            "minimum": float(np.nanmin(slopes)),
            "median": float(np.nanmedian(slopes)),
            "maximum": float(np.nanmax(slopes)),
        },
    }


def lattice_continuum_bridge_rate_audit(
    width_ratios: Sequence[float] = (2.0, 4.0, 8.0, 16.0, 32.0),
    continuum_times: Sequence[float] = (0.03, 0.3, 3.0),
    source_modes: Sequence[int] = (1, 2),
    placement_phases: Sequence[float] = (0.0, 0.5),
) -> dict[str, object]:
    """Empirical c-rate in sqrt(c)Psi(c^2 q)->P(q)."""
    rows = []
    for q in continuum_times:
        for mode in source_modes:
            continuum = continuum_phase_norm(q, mode)
            for theta in placement_phases:
                errors = []
                scaled_values = []
                for c in width_ratios:
                    value = math.sqrt(c) * lattice_phase_norm(
                        c * c * q, c, mode, theta
                    )
                    scaled_values.append(value)
                    errors.append(abs(value - continuum))
                rows.append(
                    {
                        "t_over_epsilon_squared": float(q),
                        "source_mode": int(mode),
                        "placement_phase": float(theta),
                        "continuum_phase": continuum,
                        "scaled_lattice_values": scaled_values,
                        "absolute_errors": errors,
                        "empirical_power_in_c": _loglog_slope(
                            width_ratios, errors
                        ),
                    }
                )
    slopes = [float(row["empirical_power_in_c"]) for row in rows]
    return {
        "identity_under_test": "sqrt(c) Psi_(c,theta)(c^2 q) -> P(q)",
        "width_ratios": list(map(float, width_ratios)),
        "rows": rows,
        "slope_summary": {
            "minimum": float(np.nanmin(slopes)),
            "median": float(np.nanmedian(slopes)),
            "maximum": float(np.nanmax(slopes)),
        },
    }


def joint_resolved_path_audit(
    side_lengths: Sequence[int] = (31, 63, 127, 255),
    width_exponents: Sequence[float] = (0.4, 0.6, 0.8),
    continuum_times: Sequence[float] = (0.03, 0.3, 3.0),
    source_modes: Sequence[int] = (1, 2),
) -> dict[str, object]:
    """Finite-to-continuum evidence along epsilon=n^-alpha."""
    paths: dict[tuple[float, float, int], list[dict[str, float]]] = {}
    for n in side_lengths:
        taus = []
        indexing = []
        for alpha in width_exponents:
            c = n ** (1.0 - alpha)
            for q in continuum_times:
                indexing.append((float(alpha), float(q), c))
                taus.append(c * c * q)
        kernel = scaled_modal_kernel(n, taus, source_modes)
        for time_index, (alpha, q, c) in enumerate(indexing):
            masses = gaussian_cell_masses(n, c, 0.0)
            finite = scaled_response_norms(kernel, masses)[time_index]
            for source_index, mode in enumerate(source_modes):
                scaled = math.sqrt(c) * float(finite[source_index])
                reference = continuum_phase_norm(q, mode)
                key = (alpha, q, int(mode))
                paths.setdefault(key, []).append(
                    {
                        "side_length": float(n),
                        "epsilon_over_h": c,
                        "epsilon": n ** (-alpha),
                        "physical_time": q * n ** (-2.0 * alpha),
                        "absolute_error": abs(scaled - reference),
                        "relative_error": abs(scaled / reference - 1.0),
                    }
                )
    rows = []
    for key, values in sorted(paths.items()):
        ns = [entry["side_length"] for entry in values]
        errors = [entry["absolute_error"] for entry in values]
        rows.append(
            {
                "width_exponent": key[0],
                "t_over_epsilon_squared": key[1],
                "source_mode": key[2],
                "empirical_power_in_n": _loglog_slope(ns, errors),
                "first": values[0],
                "last": values[-1],
            }
        )
    return {
        "path": "epsilon=n^-alpha, t=q epsilon^2",
        "side_lengths": list(map(int, side_lengths)),
        "rows": rows,
    }


def balanced_squared_error_audit(
    side_lengths: Sequence[int] = (31, 63, 127, 255),
    width_exponents: Sequence[float] = (0.4, 0.6, 0.75),
    continuum_times: Sequence[float] = (0.1, 0.5, 2.0),
    source_modes: Sequence[int] = (1, 2),
    placement_phases: Sequence[float] = (0.0, 0.3),
) -> dict[str, object]:
    """Candidate A: balanced resolved squared-norm comparison.

    The residual is

        |epsilon N_h^2-P(q)^2| = |c S_h^2-P(q)^2|,

    where S_h=N_h/sqrt(n).  The centered candidate scale is
    epsilon^2+c^-2.  We also record epsilon^2+c^-1 to detect a first-order
    off-centre mesh term rather than silently fitting it away.
    """
    paths: dict[tuple[float, float, int, float], list[dict[str, float]]] = {}
    for n in side_lengths:
        indexing = []
        taus = []
        for alpha in width_exponents:
            c = n ** (1.0 - alpha)
            for q in continuum_times:
                indexing.append((float(alpha), float(q), c))
                taus.append(c * c * q)
        kernel = scaled_modal_kernel(n, taus, source_modes)
        for time_index, (alpha, q, c) in enumerate(indexing):
            continuum_squared = {
                mode: continuum_phase_norm(q, mode) ** 2
                for mode in source_modes
            }
            epsilon = n ** (-alpha)
            for theta in placement_phases:
                finite = scaled_response_norms(
                    kernel, gaussian_cell_masses(n, c, theta)
                )[time_index]
                for source_index, mode in enumerate(source_modes):
                    finite_squared = c * float(finite[source_index]) ** 2
                    residual = abs(finite_squared - continuum_squared[mode])
                    centered_scale = epsilon**2 + c ** (-2.0)
                    first_order_scale = epsilon**2 + c ** (-1.0)
                    key = (alpha, q, int(mode), float(theta))
                    paths.setdefault(key, []).append(
                        {
                            "side_length": float(n),
                            "epsilon": epsilon,
                            "epsilon_over_h": c,
                            "residual": residual,
                            "epsilon_squared_plus_c_inverse_squared": centered_scale,
                            "epsilon_squared_plus_c_inverse": first_order_scale,
                            "ratio_to_centered_candidate": residual
                            / centered_scale,
                            "ratio_to_first_order_candidate": residual
                            / first_order_scale,
                        }
                    )
    rows = []
    for key, values in sorted(paths.items()):
        ns = [entry["side_length"] for entry in values]
        residuals = [entry["residual"] for entry in values]
        rows.append(
            {
                "width_exponent": key[0],
                "t_over_epsilon_squared": key[1],
                "source_mode": key[2],
                "placement_phase": key[3],
                "empirical_residual_power_in_n": _loglog_slope(ns, residuals),
                "first": values[0],
                "last": values[-1],
            }
        )
    centered_last = [
        row["last"]["ratio_to_centered_candidate"]
        for row in rows
        if row["placement_phase"] == 0.0
    ]
    off_centre_last = [
        row["last"]["ratio_to_centered_candidate"]
        for row in rows
        if row["placement_phase"] != 0.0
    ]
    return {
        "candidate": (
            "|epsilon N_h^2-P(q)^2| <= C_K[epsilon^2+(h/epsilon)^2] "
            "for q in a compact subset, centered conservative preparation"
        ),
        "alternative_off_centre_scale": "epsilon+h/epsilon",
        "side_lengths": list(map(int, side_lengths)),
        "rows": rows,
        "last_ratio_summary": {
            "centered_maximum": float(np.max(centered_last)),
            "off_centre_maximum": float(np.max(off_centre_last)),
        },
    }


def fixed_lattice_squared_error_audit(
    side_lengths: Sequence[int] = (31, 63, 127, 255),
    width_ratios: Sequence[float] = (0.25, 1.0, 4.0),
    lattice_times: Sequence[float] = (0.03, 0.3, 3.0),
    source_modes: Sequence[int] = (1, 2),
    placement_phases: Sequence[float] = (0.0, 0.3, 0.5),
) -> dict[str, object]:
    """Candidate B: fixed-(c,tau) squared lattice comparison.

    Here h N_h^2=S_h^2.  Centered odd grids are tested against O(h^2),
    while nonzero subcell phases are also tested against O(h).
    """
    paths: dict[tuple[float, float, int, float], list[dict[str, float]]] = {}
    for n in side_lengths:
        kernel = scaled_modal_kernel(n, lattice_times, source_modes)
        h = 1.0 / n
        for time_index, tau in enumerate(lattice_times):
            for c in width_ratios:
                for theta in placement_phases:
                    finite = scaled_response_norms(
                        kernel, gaussian_cell_masses(n, c, theta)
                    )[time_index]
                    for source_index, mode in enumerate(source_modes):
                        reference_squared = lattice_phase_norm(
                            tau, c, mode, theta
                        ) ** 2
                        residual = abs(
                            float(finite[source_index]) ** 2 - reference_squared
                        )
                        key = (float(c), float(tau), int(mode), float(theta))
                        paths.setdefault(key, []).append(
                            {
                                "side_length": float(n),
                                "h": h,
                                "residual": residual,
                                "residual_over_h_squared": residual / h**2,
                                "residual_over_h": residual / h,
                            }
                        )
    rows = []
    for key, values in sorted(paths.items()):
        hs = [entry["h"] for entry in values]
        residuals = [entry["residual"] for entry in values]
        rows.append(
            {
                "epsilon_over_h": key[0],
                "t_over_h_squared": key[1],
                "source_mode": key[2],
                "placement_phase": key[3],
                "empirical_residual_power_in_h": _loglog_slope(hs, residuals),
                "first": values[0],
                "last": values[-1],
            }
        )
    phase_summaries = {}
    for theta in placement_phases:
        relevant = [
            row
            for row in rows
            if math.isclose(row["placement_phase"], float(theta))
        ]
        slopes = [row["empirical_residual_power_in_h"] for row in relevant]
        phase_summaries[str(float(theta))] = {
            "minimum_power": float(np.nanmin(slopes)),
            "median_power": float(np.nanmedian(slopes)),
            "maximum_power": float(np.nanmax(slopes)),
            "maximum_last_residual_over_h_squared": float(
                max(row["last"]["residual_over_h_squared"] for row in relevant)
            ),
            "maximum_last_residual_over_h": float(
                max(row["last"]["residual_over_h"] for row in relevant)
            ),
        }
    return {
        "candidate": "|h N_h^2-Psi_(c,theta)(tau)^2|=O(h^2) in the centered odd-n model",
        "side_lengths": list(map(int, side_lengths)),
        "phase_summaries": phase_summaries,
        "rows": rows,
    }


def atomic_joint_squared_error_audit(
    side_lengths: Sequence[int] = (31, 63, 127, 255),
    time_powers: Sequence[float] = (0.5, 1.0, 1.5),
    width_powers: Sequence[float] = (-0.25, 0.0, 0.2),
    source_modes: Sequence[int] = (1, 2),
    placement_phases: Sequence[float] = (0.0, 0.5),
) -> dict[str, object]:
    """Candidate C: joint atomic tail with t->0 and tau->infinity.

    Paths use tau=n^beta and c=n^gamma.  Only gamma<beta/2 is retained,
    ensuring epsilon/sqrt(t)=c/sqrt(tau)->0.
    """
    paths: dict[tuple[float, float, int, float], list[dict[str, float]]] = {}
    for n in side_lengths:
        indexing = []
        taus = []
        for beta in time_powers:
            tau = n**beta
            for gamma in width_powers:
                if gamma >= beta / 2.0:
                    continue
                indexing.append((float(beta), float(gamma), tau, n**gamma))
                taus.append(tau)
        kernel = scaled_modal_kernel(n, taus, source_modes)
        for time_index, (beta, gamma, tau, c) in enumerate(indexing):
            physical_time = tau / n**2
            sqrt_t = math.sqrt(physical_time)
            candidate_scale = sqrt_t + c * c / tau + 1.0 / tau
            for theta in placement_phases:
                finite = scaled_response_norms(
                    kernel, gaussian_cell_masses(n, c, theta)
                )[time_index]
                for source_index, mode in enumerate(source_modes):
                    normalized_squared = math.sqrt(tau) * float(
                        finite[source_index]
                    ) ** 2
                    reference_squared = atomic_phase_constant(mode) ** 2
                    residual = abs(normalized_squared - reference_squared)
                    key = (beta, gamma, int(mode), float(theta))
                    paths.setdefault(key, []).append(
                        {
                            "side_length": float(n),
                            "epsilon_over_h": c,
                            "t_over_h_squared": tau,
                            "physical_time": physical_time,
                            "sqrt_t": sqrt_t,
                            "epsilon_over_sqrt_t_squared": c * c / tau,
                            "h_over_sqrt_t_squared": 1.0 / tau,
                            "candidate_scale": candidate_scale,
                            "residual": residual,
                            "ratio_to_candidate_scale": residual
                            / candidate_scale,
                        }
                    )
    rows = []
    for key, values in sorted(paths.items()):
        ns = [entry["side_length"] for entry in values]
        residuals = [entry["residual"] for entry in values]
        rows.append(
            {
                "tau_power": key[0],
                "c_power": key[1],
                "source_mode": key[2],
                "placement_phase": key[3],
                "empirical_residual_power_in_n": _loglog_slope(ns, residuals),
                "first": values[0],
                "last": values[-1],
            }
        )
    return {
        "candidate": (
            "|sqrt(t) N_h^2-C_infinity^2| <= C[sqrt(t)+"
            "(epsilon/sqrt(t))^2+(h/sqrt(t))^2]"
        ),
        "path": "tau=n^beta, c=n^gamma, gamma<beta/2<1",
        "side_lengths": list(map(int, side_lengths)),
        "rows": rows,
        "maximum_last_ratio_to_candidate_scale": float(
            max(row["last"]["ratio_to_candidate_scale"] for row in rows)
        ),
    }


def early_relative_error_audit(
    side_lengths: Sequence[int] = (63, 127, 255),
    width_exponents: Sequence[float] = (0.4, 0.6),
    early_times: Sequence[float] = (0.001, 0.003, 0.01, 0.03),
    source_modes: Sequence[int] = (1, 2, 3, 4),
    placement_phases: Sequence[float] = (0.0, 0.3),
) -> dict[str, object]:
    """Candidate D: early odd/even relative errors.

    The canonical ramp estimate uses q+c^-2+epsilon^2 for both parities;
    weak form estimates for a general cancelled second-order port may retain
    the older sqrt(q) remainder.  The alternative off-centre denominator
    replaces c^-2 by c^-1.
    """
    rows = []
    for n in side_lengths:
        indexing = []
        taus = []
        for alpha in width_exponents:
            c = n ** (1.0 - alpha)
            for q in early_times:
                indexing.append((float(alpha), float(q), c))
                taus.append(c * c * q)
        kernel = scaled_modal_kernel(n, taus, source_modes)
        for time_index, (alpha, q, c) in enumerate(indexing):
            for theta in placement_phases:
                centre = preparation_centre(n, theta)
                omitted_mass = gaussian_mass_outside_interval(
                    n ** (-alpha), centre
                )
                finite = scaled_response_norms(
                    kernel, gaussian_cell_masses(n, c, theta)
                )[time_index]
                for source_index, mode in enumerate(source_modes):
                    order, coefficient = early_phase_constant(mode)
                    normalized = math.sqrt(c) * float(finite[source_index])
                    leading = coefficient * q**order
                    relative = abs(normalized / leading - 1.0)
                    gamma = (
                        (2.0 + INTERACTION_STRENGTH)
                        * (4.0 * order + 1.0)
                        / 4.0
                    )
                    corrected_relative = abs(
                        normalized / leading - (1.0 - gamma * q)
                    )
                    continuum_term = q
                    epsilon = n ** (-alpha)
                    centered_scale = continuum_term + c ** (-2.0) + epsilon**2
                    first_order_scale = continuum_term + c ** (-1.0) + epsilon**2
                    rows.append(
                        {
                            "side_length": int(n),
                            "width_exponent": alpha,
                            "epsilon_over_h": c,
                            "t_over_epsilon_squared": q,
                            "source_mode": int(mode),
                            "multiplication_order": order,
                            "placement_phase": float(theta),
                            "gaussian_mass_outside_unit_interval": omitted_mass,
                            "relative_error": relative,
                            "exact_ramp_linear_correction_gamma": gamma,
                            "corrected_relative_error": corrected_relative,
                            "candidate_scale": centered_scale,
                            "ratio_to_candidate_scale": relative
                            / centered_scale,
                            "first_order_scale": first_order_scale,
                            "ratio_to_first_order_scale": relative
                            / first_order_scale,
                        }
                    )
    latest_n = max(side_lengths)
    latest = [row for row in rows if row["side_length"] == latest_n]
    summaries = {}
    for parity, predicate in (
        ("odd", lambda mode: mode % 2 == 1),
        ("even", lambda mode: mode % 2 == 0),
    ):
        for theta in placement_phases:
            relevant = [
                row
                for row in latest
                if predicate(row["source_mode"])
                and math.isclose(row["placement_phase"], theta)
            ]
            summaries[f"{parity}_theta_{theta}"] = {
                "maximum_relative_error": float(
                    max(row["relative_error"] for row in relevant)
                ),
                "maximum_ratio_to_candidate_scale": float(
                    max(row["ratio_to_candidate_scale"] for row in relevant)
                ),
                "maximum_ratio_to_first_order_scale": float(
                    max(row["ratio_to_first_order_scale"] for row in relevant)
                ),
            }
    return {
        "candidate": {
            "canonical_ramp": "relative error=O(q+(h/epsilon)^2+epsilon^2)",
            "general_cancelled_port": (
                "a weaker form estimate may retain sqrt(q), and moment "
                "leakage contributes |m_1,h|/q"
            ),
            "off_centre_probe": "replace (h/epsilon)^2 by h/epsilon",
        },
        "rows": rows,
        "latest_side_length_summaries": summaries,
    }


def continuum_endpoint_correction_audit(
    early_times: Sequence[float] = (
        0.0001,
        0.0003,
        0.001,
        0.003,
        0.01,
        0.03,
    ),
    source_modes: Sequence[int] = (1, 2, 3, 4),
) -> dict[str, object]:
    """Check the exact ramp endpoint correction through floating quadrature.

    The analytic expansion is

        P_k(q)/(C_r q^r)=1-gamma_r q+O(q^2),
        gamma_r=(2+g)(4r+1)/4.

    This routine checks the coefficients; it is not the proof of them.
    """
    rows = []
    for mode in source_modes:
        order, coefficient = early_phase_constant(mode)
        gamma = (
            (2.0 + INTERACTION_STRENGTH) * (4.0 * order + 1.0) / 4.0
        )
        uncorrected = []
        corrected = []
        ratios = []
        for q in early_times:
            ratio = continuum_phase_norm(q, mode) / (coefficient * q**order)
            ratios.append(ratio)
            uncorrected.append(abs(ratio - 1.0))
            corrected.append(abs(ratio - (1.0 - gamma * q)))
        rows.append(
            {
                "source_mode": int(mode),
                "multiplication_order": order,
                "gamma": gamma,
                "phase_over_leading_term": ratios,
                "uncorrected_residuals": uncorrected,
                "corrected_residuals": corrected,
                "uncorrected_empirical_power_in_q": _loglog_slope(
                    early_times, uncorrected
                ),
                "corrected_empirical_power_in_q": _loglog_slope(
                    early_times, corrected
                ),
                "smallest_q_gamma_estimate": (
                    1.0 - ratios[0]
                ) / early_times[0],
                "smallest_q_corrected_over_q_squared": corrected[0]
                / early_times[0] ** 2,
            }
        )
    return {
        "exact_formula": "gamma_r=(2+g)(4r+1)/4",
        "interaction_strength": INTERACTION_STRENGTH,
        "early_times": list(map(float, early_times)),
        "rows": rows,
        "status": (
            "gamma is analytic for the Gaussian/ramp profile; the tabulated "
            "powers are ordinary floating quadrature checks"
        ),
    }


def critical_width_preasymptotic_audit(
    side_lengths: Sequence[int] = (63, 127, 255, 511),
    lattice_width_ratios: Sequence[float] = (2.0, 4.0, 8.0, 16.0),
    lattice_time: float = 1.0,
) -> dict[str, object]:
    """Quantify the glacial approach on the r=1 and r=2 critical paths.

    At multiplication order r the critical exponent is
    alpha=4r/(4r+1), hence c=epsilon/h=n^(1/(4r+1)).  A modest lattice
    width c therefore corresponds to n=c^(4r+1), which is already enormous
    for r=2.  The infinite-lattice phase lets us inspect those inaccessible
    effective side lengths without pretending that it is a finite-n run.
    """
    finite_rows = []
    kernel_by_n = {
        n: scaled_modal_kernel(n, (lattice_time,), (1, 2))
        for n in side_lengths
    }
    for mode, order in ((1, 1), (2, 2)):
        alpha = 4.0 * order / (4.0 * order + 1.0)
        _, leading_coefficient = early_phase_constant(mode)
        leading_value = leading_coefficient * lattice_time**order
        for n in side_lengths:
            c = n ** (1.0 / (4.0 * order + 1.0))
            finite_scaled = scaled_response_norms(
                kernel_by_n[n], gaussian_cell_masses(n, c, 0.0)
            )[0, mode - 1]
            finite_full_norm = math.sqrt(n) * float(finite_scaled)
            lattice_full_norm = math.sqrt(n) * lattice_phase_norm(
                lattice_time, c, mode, 0.0
            )
            finite_rows.append(
                {
                    "source_mode": mode,
                    "multiplication_order": order,
                    "critical_width_exponent": alpha,
                    "side_length": int(n),
                    "epsilon_over_h": c,
                    "t_over_epsilon_squared": lattice_time / c**2,
                    "finite_full_norm": finite_full_norm,
                    "lattice_phase_full_norm": lattice_full_norm,
                    "leading_critical_value": leading_value,
                    "finite_relative_error_to_leading_law": abs(
                        finite_full_norm / leading_value - 1.0
                    ),
                    "finite_relative_error_to_lattice_phase": abs(
                        finite_full_norm / lattice_full_norm - 1.0
                    ),
                }
            )

    extrapolated_rows = []
    for mode, order in ((1, 1), (2, 2)):
        power = 4 * order + 1
        _, leading_coefficient = early_phase_constant(mode)
        leading_value = leading_coefficient * lattice_time**order
        for c in lattice_width_ratios:
            equivalent_n = float(c) ** power
            lattice_critical_norm = equivalent_n**0.5 * lattice_phase_norm(
                lattice_time, float(c), mode, 0.0
            )
            extrapolated_rows.append(
                {
                    "source_mode": mode,
                    "multiplication_order": order,
                    "epsilon_over_h": float(c),
                    "equivalent_critical_side_length": equivalent_n,
                    "lattice_extrapolated_critical_norm": lattice_critical_norm,
                    "leading_critical_value": leading_value,
                    "relative_error_to_leading_law": abs(
                        lattice_critical_norm / leading_value - 1.0
                    ),
                }
            )
    return {
        "critical_rule": (
            "alpha=4r/(4r+1), c=n^(1/(4r+1)), and n=c^(4r+1)"
        ),
        "finite_rows": finite_rows,
        "lattice_phase_extrapolation": extrapolated_rows,
        "practical_boundary": (
            "the theorem can be asymptotically correct while every feasible "
            "finite grid remains far from its leading critical constant"
        ),
    }


def null_and_symmetry_controls() -> dict[str, object]:
    """Numerical shadows of exact null identities."""
    n = 63
    taus = (0.001, 0.03, 1.0, 30.0)
    modes = (1, 2, 3, 4)
    q = gaussian_cell_masses(n, 0.7, 0.37)
    constant = scaled_modal_kernel(n, taus, modes, np.ones(n))
    constant_norms = scaled_response_norms(constant, q)
    symmetric = scaled_modal_kernel(n, taus, modes, symmetric_modulation(n))
    symmetric_norms = scaled_response_norms(symmetric, q)
    odd_columns = [index for index, mode in enumerate(modes) if mode % 2]
    even_columns = [index for index, mode in enumerate(modes) if mode % 2 == 0]
    return {
        "exact_nulls": {
            "constant_modulation": (
                "all nonconstant source modes have exactly zero target marginal"
            ),
            "reflection_control": (
                "reflection-odd sources are exactly invisible for symmetric V"
            ),
            "relative_error_warning": (
                "a relative comparison is undefined at either exact null"
            ),
        },
        "floating_residuals": {
            "constant_modulation_maximum_norm": float(
                np.max(np.abs(constant_norms))
            ),
            "symmetric_odd_maximum_norm": float(
                np.max(np.abs(symmetric_norms[:, odd_columns]))
            ),
            "symmetric_even_minimum_norm": float(
                np.min(np.abs(symmetric_norms[:, even_columns]))
            ),
        },
    }


def placement_counterexample(
    side_lengths: Sequence[int] = (31, 63, 127, 255),
    width_ratio: float = 0.05,
    lattice_time: float = 0.01,
) -> dict[str, object]:
    """A placement-blind atom chart has a nonvanishing limiting error."""
    rows = []
    atom_reference = lattice_phase_norm(lattice_time, 0.0, 1, 0.0)
    split_reference = lattice_phase_norm(lattice_time, 0.0, 1, 0.5)
    for n in side_lengths:
        kernel = scaled_modal_kernel(n, (lattice_time,), (1,))
        centre = float(
            scaled_response_norms(
                kernel, gaussian_cell_masses(n, width_ratio, 0.0)
            )[0, 0]
        )
        boundary = float(
            scaled_response_norms(
                kernel, gaussian_cell_masses(n, width_ratio, 0.5)
            )[0, 0]
        )
        rows.append(
            {
                "side_length": int(n),
                "cell_centre_response": centre,
                "cell_boundary_response": boundary,
                "centre_error_to_atom": abs(centre - atom_reference),
                "boundary_error_to_split": abs(boundary - split_reference),
                "boundary_error_to_placement_blind_atom": abs(
                    boundary - atom_reference
                ),
            }
        )
    return {
        "epsilon_over_h": width_ratio,
        "t_over_h_squared": lattice_time,
        "atom_phase_reference": atom_reference,
        "split_phase_reference": split_reference,
        "persistent_atom_split_gap": abs(atom_reference - split_reference),
        "rows": rows,
        "counterexample": (
            "theta=0 tends to a cell atom while theta=1/2 tends to an equal "
            "split as c->0; width and time alone do not select a lattice phase"
        ),
    }


def unresolved_continuum_counterexample(
    side_lengths: Sequence[int] = (31, 63, 127, 255),
    width_ratio: float = 0.05,
    lattice_time: float = 0.1,
) -> dict[str, object]:
    """Continuum dispersion is not uniform down to c<<1 at fixed tau."""
    q = lattice_time / width_ratio**2
    continuum_as_lattice = continuum_phase_norm(q, 1) / math.sqrt(width_ratio)
    lattice = lattice_phase_norm(lattice_time, width_ratio, 1, 0.0)
    rows = []
    for n in side_lengths:
        kernel = scaled_modal_kernel(n, (lattice_time,), (1,))
        finite = float(
            scaled_response_norms(
                kernel, gaussian_cell_masses(n, width_ratio, 0.0)
            )[0, 0]
        )
        rows.append(
            {
                "side_length": int(n),
                "finite_norm_over_sqrt_n": finite,
                "error_to_lattice_phase": abs(finite - lattice),
                "error_to_naive_continuum_phase": abs(
                    finite - continuum_as_lattice
                ),
            }
        )
    return {
        "epsilon_over_h": width_ratio,
        "t_over_h_squared": lattice_time,
        "t_over_epsilon_squared": q,
        "lattice_phase": lattice,
        "continuum_prediction_in_lattice_units": continuum_as_lattice,
        "persistent_chart_gap": abs(lattice - continuum_as_lattice),
        "rows": rows,
        "counterexample": (
            "h/max(epsilon,sqrt(t)) is not small at fixed tau, so continuum "
            "dispersion leaves a nonzero error even as n grows"
        ),
    }


def nonuniform_large_time_counterexample(
    side_lengths: Sequence[int] = (15, 31, 63, 127),
    physical_time: float = 3.0,
) -> dict[str, object]:
    """The infinite-line lattice phase is not uniform when t stays positive."""
    rows = []
    for n in side_lengths:
        tau = physical_time * n**2
        kernel = scaled_modal_kernel(n, (tau,), (1,))
        finite = float(
            scaled_response_norms(kernel, gaussian_cell_masses(n, 0.0, 0.0))[
                0, 0
            ]
        )
        lattice = lattice_phase_norm(tau, 0.0, 1, 0.0)
        rows.append(
            {
                "side_length": int(n),
                "t_over_h_squared": tau,
                "physical_time": physical_time,
                "finite_norm_over_sqrt_n": finite,
                "lattice_phase": lattice,
                "relative_error": abs(finite / lattice - 1.0),
            }
        )
    return {
        "path": "tau=t n^2 with fixed positive t",
        "rows": rows,
        "counterexample": (
            "the lattice phase is an initial-layer/infinite-volume chart; its "
            "uniform use requires t=tau/n^2 -> 0"
        ),
    }


def wandering_phase_counterexample(
    width_ratio: float = 0.08,
    lattice_time: float = 0.01,
    maximum_side_length: int = 600,
) -> dict[str, object]:
    """Fixed irrational y0 produces wandering microscopic phases."""
    y0 = math.sqrt(2.0) / 3.0
    candidates = []
    for n in range(31, maximum_side_length + 1):
        fractional = (n * y0) % 1.0
        theta = fractional - 0.5
        phase = lattice_phase_norm(lattice_time, width_ratio, 1, theta)
        candidates.append((n, theta, phase))
    low = min(candidates, key=lambda row: row[2])
    high = max(candidates, key=lambda row: row[2])
    near_centre = min(candidates, key=lambda row: abs(row[1]))
    near_boundary = max(candidates, key=lambda row: abs(row[1]))
    selected = []
    for n, theta, reference in (near_centre, near_boundary):
        kernel = scaled_modal_kernel(n, (lattice_time,), (1,))
        carrier = int(math.floor(n * y0))
        finite = float(
            scaled_response_norms(
                kernel,
                gaussian_cell_masses(n, width_ratio, theta, anchor=carrier),
            )[0, 0]
        )
        selected.append(
            {
                "side_length": n,
                "placement_phase": theta,
                "finite_norm_over_sqrt_n": finite,
                "phase_reference": reference,
                "absolute_error": abs(finite - reference),
            }
        )
    return {
        "physical_centre": y0,
        "epsilon_over_h": width_ratio,
        "t_over_h_squared": lattice_time,
        "phase_minimum_over_scan": {
            "side_length": low[0],
            "placement_phase": low[1],
            "phase": low[2],
        },
        "phase_maximum_over_scan": {
            "side_length": high[0],
            "placement_phase": high[1],
            "phase": high[2],
        },
        "phase_range": high[2] - low[2],
        "finite_selected_subsequences": selected,
        "counterexample": (
            "without a convergent lattice phase, a fixed physical centre can "
            "have distinct microscopic subsequential constants"
        ),
    }


def run_stage_viii_audit(fast: bool = False) -> dict[str, object]:
    """Run the complete three-parameter computational/adversarial audit."""
    broad_n = (31, 63) if fast else (31, 63, 127)
    rate_n = (31, 63, 127) if fast else (31, 63, 127, 255)
    return {
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
        },
        "declared_parameters": {
            "h": "1/n",
            "c": "epsilon/h",
            "tau": "t/h^2",
            "q": "t/epsilon^2=tau/c^2",
            "finite_lattice_normalization": "||R_n||/sqrt(n)",
            "finite_continuum_normalization": "sqrt(epsilon)||R_n||=sqrt(c)||R_n||/sqrt(n)",
        },
        "exact_identity_audit": exact_identity_audit(),
        "broad_grid": broad_grid_audit(side_lengths=broad_n),
        "finite_to_lattice_rates": finite_lattice_rate_audit(
            side_lengths=rate_n
        ),
        "lattice_to_continuum_bridge_rates": lattice_continuum_bridge_rate_audit(),
        "joint_resolved_paths": joint_resolved_path_audit(side_lengths=rate_n),
        "candidate_bounds": {
            "balanced_resolved_squared": balanced_squared_error_audit(
                side_lengths=rate_n
            ),
            "fixed_lattice_squared": fixed_lattice_squared_error_audit(
                side_lengths=rate_n
            ),
            "atomic_joint_squared": atomic_joint_squared_error_audit(
                side_lengths=rate_n
            ),
            "early_relative_odd_even": early_relative_error_audit(
                side_lengths=tuple(n for n in rate_n if n >= 63)
            ),
            "continuum_endpoint_correction": continuum_endpoint_correction_audit(),
            "critical_width_preasymptotics": critical_width_preasymptotic_audit(
                side_lengths=tuple(n for n in rate_n if n >= 63),
                lattice_width_ratios=(2.0, 4.0, 8.0)
                if fast
                else (2.0, 4.0, 8.0, 16.0),
            ),
        },
        "null_and_symmetry_controls": null_and_symmetry_controls(),
        "counterexamples": {
            "placement_blind": placement_counterexample(rate_n),
            "continuum_below_resolution": unresolved_continuum_counterexample(
                rate_n
            ),
            "lattice_at_fixed_positive_time": nonuniform_large_time_counterexample(),
            "wandering_lattice_phase": wandering_phase_counterexample(
                maximum_side_length=250 if fast else 600
            ),
        },
        "status": {
            "exact_or_analytic": (
                "finite modal identity, first-jet identity, triangle decomposition, "
                "and the two symmetry null controls"
            ),
            "floating_evidence": (
                "all rates, broad-grid extrema, phase-integral values, and "
                "counterexample magnitudes"
            ),
            "not_claimed": (
                "no interval enclosure, no proof inferred from fitted slopes, and "
                "no placement-free or all-time uniform relative theorem"
            ),
        },
    }


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fast", action="store_true")
    return parser.parse_args()


def main() -> None:
    arguments = _parse_arguments()
    print(json.dumps(run_stage_viii_audit(arguments.fast), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
