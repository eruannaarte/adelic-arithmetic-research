#!/usr/bin/env python3
"""Stage VII laboratory for the smooth-to-atomic mollifier phase diagram.

The finite model is exactly the cell-centred Neumann path model used in OIG
Stages V and VI.  A unit-mass Gaussian target preparation, centred at 1/2,
is represented by *cell averages*.  The source is a fixed, continuum-unit
cosine mode and the reported output is the complete density-normalized target
response norm (all target modes, not a fixed-band projection).

There are two joint limits:

* resolved mollifier: eps/h -> infinity, t=q eps^2;
* lattice mollifier: eps/h -> c, t=tau h^2.

The associated phase functions are computed independently from closed scalar
integrals.  Exact finite identities (modal reduction and the first causal jet)
are separated from floating-point convergence evidence.  High-precision
quadrature audits the phase-function constants, but is not described as an
outward-rounded certificate.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import sys
from dataclasses import dataclass
from typing import Iterable, Sequence

import mpmath as mp
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.linalg import eigh_tridiagonal, expm
from scipy.optimize import minimize_scalar
from scipy.special import ndtr


INTERACTION_STRENGTH = 4.0 / 5.0
SOURCE_MODE = 1
TARGET_CENTRE = 0.5


def cell_centres(side_length: int) -> np.ndarray:
    """Cell centres x_j=(j+1/2)/n."""
    if side_length < 3:
        raise ValueError("side_length must be at least three")
    return (np.arange(side_length, dtype=float) + 0.5) / side_length


def cosine_modes(side_length: int, modes: Sequence[int]) -> np.ndarray:
    """Euclidean-orthonormal cell-centred Neumann cosine modes."""
    indices = tuple(int(mode) for mode in modes)
    if any(mode < 0 or mode >= side_length for mode in indices):
        raise ValueError("mode indices must lie in [0,n)")
    x = cell_centres(side_length)
    columns = []
    for mode in indices:
        if mode == 0:
            columns.append(np.ones(side_length) / math.sqrt(side_length))
        else:
            columns.append(
                math.sqrt(2.0 / side_length)
                * np.cos(math.pi * mode * x)
            )
    return np.column_stack(columns)


def path_eigenvalues(side_length: int) -> np.ndarray:
    """Exact spectrum of n^2 times the unweighted path Laplacian."""
    modes = np.arange(side_length, dtype=float)
    return (
        4.0
        * side_length**2
        * np.sin(math.pi * modes / (2.0 * side_length)) ** 2
    )


def scaled_path_laplacian(side_length: int) -> np.ndarray:
    """Dense A_n=n^2 L_n, used only in small direct controls."""
    n = side_length
    matrix = np.zeros((n, n), dtype=float)
    np.fill_diagonal(matrix, 2.0)
    matrix[0, 0] = matrix[-1, -1] = 1.0
    off = np.arange(n - 1)
    matrix[off, off + 1] = -1.0
    matrix[off + 1, off] = -1.0
    return n**2 * matrix


def path_laplacian_action(values: np.ndarray) -> np.ndarray:
    """Apply A_n without forming a dense matrix."""
    vector = np.asarray(values, dtype=float)
    if vector.ndim != 1 or len(vector) < 3:
        raise ValueError("a one-dimensional vector of length at least three is required")
    n = len(vector)
    result = np.empty_like(vector)
    result[0] = vector[0] - vector[1]
    result[-1] = vector[-1] - vector[-2]
    result[1:-1] = 2.0 * vector[1:-1] - vector[:-2] - vector[2:]
    return n**2 * result


def gaussian_cell_average(
    side_length: int,
    epsilon: float,
    centre: float = TARGET_CENTRE,
) -> np.ndarray:
    """Probability masses of a centred Gaussian in the n cells.

    The continuum density is proportional to

        exp(-(y-centre)^2/(2 eps^2))/(sqrt(2 pi) eps)

    on [0,1].  Division by the captured mass makes the finite vector sum to
    one even when eps is not small compared with the boundary distance.
    ``epsilon=0`` denotes its point-mass limit in the nearest cell.
    """
    if side_length < 3 or epsilon < 0.0 or not 0.0 < centre < 1.0:
        raise ValueError("invalid Gaussian cell-average parameters")
    n = side_length
    if epsilon == 0.0:
        cells = cell_centres(n)
        result = np.zeros(n)
        result[int(np.argmin(np.abs(cells - centre)))] = 1.0
        return result
    edges = np.arange(n + 1, dtype=float) / n
    cdf = ndtr((edges - centre) / epsilon)
    masses = np.diff(cdf)
    total = float(np.sum(masses))
    if not total > 0.0:
        raise FloatingPointError("Gaussian mass underflowed on the interval")
    masses /= total
    # Restore reflection symmetry at the declared centre against last-bit CDF
    # subtraction asymmetry.  This changes only floating roundoff.
    if centre == 0.5:
        masses = 0.5 * (masses + masses[::-1])
        masses /= np.sum(masses)
    return masses


def target_cosine_coefficients(probability: np.ndarray) -> np.ndarray:
    """Return beta_l=u_l^T q in the finite orthonormal cosine basis."""
    q = np.asarray(probability, dtype=float)
    modes = cosine_modes(len(q), range(len(q)))
    return modes.T @ q


def discrete_source_moment(side_length: int, source_mode: int) -> float:
    """Return 1^T D_n u_{k,n}."""
    mode = cosine_modes(side_length, (source_mode,))[:, 0]
    return float(cell_centres(side_length) @ mode)


def continuum_source_moment(source_mode: int) -> float:
    """Return integral_0^1 x phi_k(x) dx exactly in floating form."""
    if source_mode < 1:
        raise ValueError("the source mode must be positive")
    if source_mode % 2 == 0:
        return 0.0
    return -2.0 * math.sqrt(2.0) / (math.pi * source_mode) ** 2


def exact_first_jet_norm(
    side_length: int,
    epsilon: float,
    source_mode: int = SOURCE_MODE,
    interaction_strength: float = INTERACTION_STRENGTH,
) -> float:
    """Exact finite full-target first-response derivative norm.

    In the density-normalized protocol the source/output sqrt(n) factors
    cancel, and the derivative is the rank-one vector

        -g (1^T D u_k) A_n q.
    """
    q = gaussian_cell_average(side_length, epsilon)
    moment = discrete_source_moment(side_length, source_mode)
    return float(
        interaction_strength * abs(moment) * np.linalg.norm(path_laplacian_action(q))
    )


def gaussian_second_derivative_norm() -> float:
    """Exact ||eta''||_2 for the standard normal density on R."""
    return math.sqrt(3.0 / (8.0 * math.sqrt(math.pi)))


def resolved_first_jet_constant(
    source_mode: int = SOURCE_MODE,
    interaction_strength: float = INTERACTION_STRENGTH,
) -> float:
    """Limit of eps^(5/2) times the resolved first-jet norm."""
    return (
        interaction_strength
        * abs(continuum_source_moment(source_mode))
        * gaussian_second_derivative_norm()
    )


@dataclass(frozen=True)
class ModalKernel:
    """Target-mode scalar response before multiplication by target beta_l."""

    side_length: int
    times: np.ndarray
    source_modes: tuple[int, ...]
    values: np.ndarray  # shape (time, target mode, source mode)


def modal_response_kernel(
    side_length: int,
    times: Sequence[float],
    source_modes: Sequence[int] = (SOURCE_MODE,),
    interaction_strength: float = INTERACTION_STRENGTH,
) -> ModalKernel:
    """Compute 1^T exp(-t K_l,n) u_k by tridiagonal eigendecomposition."""
    n = side_length
    time_array = np.asarray(times, dtype=float)
    sources = tuple(int(mode) for mode in source_modes)
    if n < 3 or time_array.ndim != 1 or np.any(time_array < 0.0):
        raise ValueError("invalid side length or time array")
    if len(time_array) == 0 or any(mode < 1 or mode >= n for mode in sources):
        raise ValueError("at least one valid nonstationary source mode is required")
    if interaction_strength < 0.0:
        raise ValueError("interaction_strength must be nonnegative")

    x = cell_centres(n)
    source_matrix = cosine_modes(n, sources)
    ones = np.ones(n)
    diagonal = np.full(n, 2.0 * n**2)
    diagonal[[0, -1]] = n**2
    off_diagonal = np.full(n - 1, -float(n**2))
    target_rates = path_eigenvalues(n)
    values = np.zeros((len(time_array), n, len(sources)))

    # l=0 is exactly zero on every mass-zero source mode.  For l>0, subtract
    # the identity inside the spectral sum.  Since 1^T u_k=0 exactly in the
    # model, expm1 avoids catastrophic cancellation at t=O(n^-2).
    for target_mode in range(1, n):
        reduced_diagonal = diagonal + target_rates[target_mode] * (
            1.0 + interaction_strength * x
        )
        eigenvalues, eigenvectors = eigh_tridiagonal(
            reduced_diagonal,
            off_diagonal,
            check_finite=False,
        )
        left = ones @ eigenvectors
        right = eigenvectors.T @ source_matrix
        spectral_coefficients = left[:, None] * right
        values[:, target_mode, :] = (
            np.expm1(-np.outer(time_array, eigenvalues))
            @ spectral_coefficients
        )
    return ModalKernel(n, time_array, sources, values)


def response_norms(
    kernel: ModalKernel,
    target_probability: np.ndarray,
) -> np.ndarray:
    """Full density-normalized target L2 norm for every time/source."""
    q = np.asarray(target_probability, dtype=float)
    if q.shape != (kernel.side_length,):
        raise ValueError("target vector has the wrong side length")
    beta = target_cosine_coefficients(q)
    modal_response = kernel.values * beta[None, :, None]
    return np.linalg.norm(modal_response, axis=1)


def direct_dense_response(
    side_length: int,
    times: Sequence[float],
    epsilon: float,
    source_modes: Sequence[int] = (SOURCE_MODE,),
    interaction_strength: float = INTERACTION_STRENGTH,
) -> np.ndarray:
    """Small-n n^2-state control, returned in target cosine coordinates."""
    n = side_length
    a = scaled_path_laplacian(n)
    identity = np.eye(n)
    d = np.diag(cell_centres(n))
    generator = np.kron(a, identity) + np.kron(
        identity + interaction_strength * d,
        a,
    )
    q = gaussian_cell_average(n, epsilon)
    sources = cosine_modes(n, source_modes)
    injections = np.column_stack(
        [
            np.kron(sources[:, column] / math.sqrt(n), q)
            for column in range(len(source_modes))
        ]
    )
    marginal = np.kron(np.ones((1, n)), identity)
    target_modes = cosine_modes(n, range(n))
    rows = []
    for time in times:
        physical = marginal @ expm(-float(time) * generator) @ injections
        rows.append(math.sqrt(n) * target_modes.T @ physical)
    return np.asarray(rows)


def limiting_source_profile(
    scaled_target_rate: float | np.ndarray,
    source_mode: int = SOURCE_MODE,
    interaction_strength: float = INTERACTION_STRENGTH,
) -> float | np.ndarray:
    """Closed high-target-mode profile F_k(s).

    F_k(s)=int_0^1 exp[-s(1+gx)] phi_k(x) dx.
    """
    s = np.asarray(scaled_target_rate, dtype=float)
    a = interaction_strength * s
    denominator = a * a + (math.pi * source_mode) ** 2
    if source_mode % 2:
        numerator_factor = 1.0 + np.exp(-a)
    else:
        numerator_factor = -np.expm1(-a)
    result = (
        math.sqrt(2.0)
        * np.exp(-s)
        * a
        * numerator_factor
        / denominator
    )
    if result.ndim == 0:
        return float(result)
    return result


def gaussian_fourier(frequency: float | np.ndarray) -> float | np.ndarray:
    """Fourier transform of the standard normal density."""
    frequency_array = np.asarray(frequency, dtype=float)
    result = np.exp(-0.5 * frequency_array**2)
    if result.ndim == 0:
        return float(result)
    return result


def continuum_phase_norm(
    time_ratio: float,
    source_mode: int = SOURCE_MODE,
    interaction_strength: float = INTERACTION_STRENGTH,
) -> float:
    """Resolved phase P(q), where sqrt(eps)||R(q eps^2)|| -> P(q)."""
    if time_ratio <= 0.0:
        raise ValueError("time_ratio must be positive")

    def integrand(z: float) -> float:
        transform = math.exp(-0.5 * (math.pi * z) ** 2)
        profile = limiting_source_profile(
            time_ratio * (math.pi * z) ** 2,
            source_mode,
            interaction_strength,
        )
        return transform * transform * profile * profile

    value, _ = quad(
        integrand,
        0.0,
        np.inf,
        epsabs=2e-13,
        epsrel=2e-13,
        limit=300,
    )
    return math.sqrt(max(value, 0.0))


def atomic_phase_constant(
    source_mode: int = SOURCE_MODE,
    interaction_strength: float = INTERACTION_STRENGTH,
) -> float:
    """C_atom such that P(q)~C_atom q^-1/4 as q->infinity."""

    def integrand(u: float) -> float:
        profile = limiting_source_profile(
            (math.pi * u) ** 2,
            source_mode,
            interaction_strength,
        )
        return profile * profile

    value, _ = quad(
        integrand,
        0.0,
        np.inf,
        epsabs=2e-13,
        epsrel=2e-13,
        limit=300,
    )
    return math.sqrt(max(value, 0.0))


def limiting_lattice_weights(width_ratio: float) -> tuple[np.ndarray, np.ndarray]:
    """Infinite-grid Gaussian cell masses for eps/h=c.

    Returns integer cell offsets and normalized masses.  The omitted normal
    tail is below double precision at the chosen cutoff.  c=0 is the atom.
    """
    c = float(width_ratio)
    if c < 0.0:
        raise ValueError("width_ratio must be nonnegative")
    if c == 0.0:
        return np.asarray([0], dtype=int), np.asarray([1.0])
    radius = max(1, int(math.ceil(9.0 * c + 0.5)))
    offsets = np.arange(-radius, radius + 1, dtype=int)
    upper = (offsets + 0.5) / c
    lower = (offsets - 0.5) / c
    masses = ndtr(upper) - ndtr(lower)
    masses = 0.5 * (masses + masses[::-1])
    masses /= np.sum(masses)
    return offsets, masses


def lattice_filter(
    normalized_frequency: float | np.ndarray,
    width_ratio: float,
) -> float | np.ndarray:
    """B_c(pi xi)=sum_r Q_c(r) cos(pi xi r)."""
    xi = np.asarray(normalized_frequency, dtype=float)
    offsets, masses = limiting_lattice_weights(width_ratio)
    flattened = xi.reshape(-1)
    values = np.cos(math.pi * flattened[:, None] * offsets[None, :]) @ masses
    result = values.reshape(xi.shape)
    if result.ndim == 0:
        return float(result)
    return result


def lattice_phase_norm(
    lattice_time: float,
    width_ratio: float,
    source_mode: int = SOURCE_MODE,
    interaction_strength: float = INTERACTION_STRENGTH,
) -> float:
    """Lattice phase Psi_c(tau), with ||R(tau h^2)||/sqrt(n)->Psi."""
    if lattice_time <= 0.0 or width_ratio < 0.0:
        raise ValueError("invalid lattice phase parameters")
    offsets, masses = limiting_lattice_weights(width_ratio)

    def integrand(xi: float) -> float:
        target_filter = float(
            np.cos(math.pi * xi * offsets) @ masses
        )
        spectral_rate = 4.0 * lattice_time * math.sin(
            math.pi * xi / 2.0
        ) ** 2
        profile = limiting_source_profile(
            spectral_rate,
            source_mode,
            interaction_strength,
        )
        return target_filter * target_filter * profile * profile

    value, _ = quad(
        integrand,
        0.0,
        1.0,
        epsabs=2e-13,
        epsrel=2e-13,
        limit=300,
    )
    return math.sqrt(max(value, 0.0))


def lattice_atom_small_time_constant(
    source_mode: int = SOURCE_MODE,
    interaction_strength: float = INTERACTION_STRENGTH,
) -> float:
    """Exact coefficient Psi_0(tau)~C_lattice tau for odd k."""
    return (
        interaction_strength
        * abs(continuum_source_moment(source_mode))
        * math.sqrt(6.0)
    )


def _mp_source_profile(s: mp.mpf, source_mode: int, g: mp.mpf) -> mp.mpf:
    if s == 0:
        return mp.mpf("0")
    a = g * s
    sign = -1 if source_mode % 2 else 1
    return (
        mp.sqrt(2)
        * mp.exp(-s)
        * a
        * (1 - sign * mp.exp(-a))
        / (a * a + (mp.pi * source_mode) ** 2)
    )


def high_precision_constants(decimal_digits: int = 60) -> dict[str, object]:
    """Independent high-precision quadrature of exact phase constants."""
    if decimal_digits < 30:
        raise ValueError("at least 30 decimal digits are required")
    with mp.workdps(decimal_digits):
        g = mp.mpf(4) / 5
        k = SOURCE_MODE
        source_moment = 2 * mp.sqrt(2) / (mp.pi * k) ** 2
        eta_second = mp.sqrt(3 / (8 * mp.sqrt(mp.pi)))
        jet = g * source_moment * eta_second
        lattice = g * source_moment * mp.sqrt(6)
        atom_squared = mp.quad(
            lambda u: _mp_source_profile((mp.pi * u) ** 2, k, g) ** 2,
            [0, 1, mp.inf],
        )
        atom = mp.sqrt(atom_squared)
        double_atom = atomic_phase_constant()
        return {
            "decimal_digits": decimal_digits,
            "resolved_first_jet_constant": mp.nstr(jet, decimal_digits),
            "lattice_atom_small_time_constant": mp.nstr(
                lattice, decimal_digits
            ),
            "atomic_large_time_constant": mp.nstr(atom, decimal_digits),
            "double_atomic_large_time_constant": double_atom,
            "double_vs_high_precision_atomic_constant_error": abs(
                double_atom - float(atom)
            ),
        }


def normalization_and_dense_audit() -> dict[str, object]:
    """Audit cell masses, source/output normalization, and modal reduction."""
    n = 7
    epsilon = 0.11
    times = (0.0, 1.0e-4, 0.003, 0.05)
    sources = (1, 2, 3)
    q = gaussian_cell_average(n, epsilon)
    modes = cosine_modes(n, range(n))
    kernel = modal_response_kernel(n, times, sources)
    beta = modes.T @ q
    modal = kernel.values * beta[None, :, None]
    dense = direct_dense_response(n, times, epsilon, sources)
    difference = dense - modal
    source_probability = cosine_modes(n, sources) / math.sqrt(n)
    source_density = n * source_probability
    h = 1.0 / n
    return {
        "side_length": n,
        "epsilon": epsilon,
        "target_probability_mass_error": abs(float(np.sum(q)) - 1.0),
        "target_reflection_error": float(np.max(np.abs(q - q[::-1]))),
        "dct_orthonormality_error": float(
            np.linalg.norm(modes.T @ modes - np.eye(n), ord=np.inf)
        ),
        "source_density_gram_error": float(
            np.linalg.norm(
                h * source_density.T @ source_density - np.eye(len(sources)),
                ord=np.inf,
            )
        ),
        "maximum_dense_modal_entry_error": float(np.max(np.abs(difference))),
        "relative_dense_modal_frobenius_error": float(
            np.linalg.norm(difference) / np.linalg.norm(dense[1:])
        ),
        "time_zero_response_norm": float(np.linalg.norm(modal[0])),
    }


def first_jet_scaling_audit(
    side_lengths: Sequence[int] = (127, 255, 511, 1023, 2047),
    width_exponent: float = 0.6,
) -> dict[str, object]:
    """Resolved eps/h->infinity audit of eps^-5/2 first-jet scaling."""
    constant = resolved_first_jet_constant()
    rows = []
    for n in side_lengths:
        epsilon = n ** (-width_exponent)
        value = exact_first_jet_norm(n, epsilon)
        scaled = epsilon**2.5 * value
        rows.append(
            {
                "side_length": int(n),
                "epsilon": epsilon,
                "epsilon_over_h": n * epsilon,
                "first_jet_norm": value,
                "epsilon_to_5_over_2_times_norm": scaled,
                "relative_error_to_exact_constant": abs(scaled / constant - 1.0),
            }
        )
    return {
        "width_rule": f"epsilon=n^-{width_exponent}",
        "exact_continuum_constant": constant,
        "exact_identity": "||R'_n(0)||=g|1^T D u_k| ||A_n q||",
        "rows": rows,
    }


def continuum_crossover_audit(
    time_ratios: Sequence[float] = (
        0.001,
        0.003,
        0.01,
        0.03,
        0.1,
        0.3,
        1.0,
        3.0,
        10.0,
        30.0,
        100.0,
    ),
) -> dict[str, object]:
    """Compute P(q) and its q and q^-1/4 asymptotes."""
    small_constant = resolved_first_jet_constant()
    large_constant = atomic_phase_constant()
    rows = []
    for ratio in time_ratios:
        phase = continuum_phase_norm(ratio)
        small_prediction = small_constant * ratio
        large_prediction = large_constant * ratio ** (-0.25)
        rows.append(
            {
                "time_over_epsilon_squared": float(ratio),
                "phase_norm": phase,
                "ratio_to_t_epsilon_minus_5_over_2_asymptote": (
                    phase / small_prediction
                ),
                "ratio_to_t_minus_1_over_4_asymptote": phase / large_prediction,
            }
        )
    return {
        "small_time_exact_constant": small_constant,
        "large_time_phase_constant": large_constant,
        "interpretation": (
            "||R(t)||=epsilon^-1/2 P(t/epsilon^2); hence P(q)~C0 q "
            "gives C0 t epsilon^-5/2 and P(q)~Cinf q^-1/4 gives "
            "Cinf t^-1/4"
        ),
        "rows": rows,
    }


def resolved_discrete_collapse_audit(
    side_lengths: Sequence[int] = (127, 255, 511),
    time_ratios: Sequence[float] = (0.03, 0.1, 0.3, 1.0, 3.0),
    width_exponent: float = 0.6,
) -> dict[str, object]:
    """Compare exact finite response with the resolved continuum phase P."""
    phase = np.asarray([continuum_phase_norm(ratio) for ratio in time_ratios])
    rows = []
    for n in side_lengths:
        epsilon = n ** (-width_exponent)
        times = epsilon**2 * np.asarray(time_ratios, dtype=float)
        kernel = modal_response_kernel(n, times)
        norms = response_norms(kernel, gaussian_cell_average(n, epsilon))[:, 0]
        scaled = math.sqrt(epsilon) * norms
        relative = np.abs(scaled - phase) / phase
        rows.append(
            {
                "side_length": int(n),
                "epsilon": epsilon,
                "epsilon_over_h": n * epsilon,
                "scaled_response": scaled.tolist(),
                "phase_reference": phase.tolist(),
                "relative_errors": relative.tolist(),
                "maximum_relative_error": float(np.max(relative)),
            }
        )
    return {
        "width_rule": f"epsilon=n^-{width_exponent}",
        "time_ratios": list(map(float, time_ratios)),
        "scaling": "sqrt(epsilon)||R(q epsilon^2)|| -> P(q)",
        "rows": rows,
    }


def lattice_phase_audit(
    side_lengths: Sequence[int] = (63, 127, 255, 511),
    width_ratios: Sequence[float] = (0.0, 0.5, 1.0, 2.0, 4.0),
    lattice_times: Sequence[float] = (0.03, 0.1, 0.3, 1.0, 3.0, 10.0),
) -> dict[str, object]:
    """Audit h^-1/2 scaling for eps/h=c and t/h^2=tau."""
    references = {
        float(c): np.asarray([lattice_phase_norm(tau, c) for tau in lattice_times])
        for c in width_ratios
    }
    rows = []
    for n in side_lengths:
        times = np.asarray(lattice_times, dtype=float) / n**2
        kernel = modal_response_kernel(n, times)
        for c in width_ratios:
            epsilon = float(c) / n
            norms = response_norms(
                kernel,
                gaussian_cell_average(n, epsilon),
            )[:, 0]
            scaled = norms / math.sqrt(n)
            reference = references[float(c)]
            relative = np.abs(scaled - reference) / reference
            rows.append(
                {
                    "side_length": int(n),
                    "epsilon_over_h": float(c),
                    "scaled_response": scaled.tolist(),
                    "phase_reference": reference.tolist(),
                    "relative_errors": relative.tolist(),
                    "maximum_relative_error": float(np.max(relative)),
                }
            )
    atom_rows = []
    atom_constant = lattice_atom_small_time_constant()
    atom_large = atomic_phase_constant()
    for tau in (0.001, 0.003, 0.01, 0.03, 0.1, 1.0, 10.0, 100.0):
        phase = lattice_phase_norm(tau, 0.0)
        atom_rows.append(
            {
                "lattice_time": tau,
                "phase_norm": phase,
                "ratio_to_small_time_linear_asymptote": phase / (atom_constant * tau),
                "ratio_to_large_time_tau_minus_quarter_asymptote": (
                    phase / (atom_large * tau ** (-0.25))
                ),
            }
        )
    return {
        "lattice_times": list(map(float, lattice_times)),
        "scaling": "||R(tau h^2)||/sqrt(n) -> Psi_c(tau)",
        "equivalent": "||R(tau h^2)|| is asymptotic to h^-1/2 Psi_c(tau)",
        "atom_small_time_exact_constant": atom_constant,
        "atom_large_time_constant": atom_large,
        "rows": rows,
        "atom_crossover": atom_rows,
    }


def vanishing_width_ratio_audit(
    side_lengths: Sequence[int] = (63, 127, 255, 511),
    lattice_times: Sequence[float] = (0.1, 1.0, 10.0),
) -> dict[str, object]:
    """Audit eps/h->0 by comparison with the exact central-cell atom."""
    rows = []
    for n in side_lengths:
        c = n ** (-0.25)
        times = np.asarray(lattice_times, dtype=float) / n**2
        kernel = modal_response_kernel(n, times)
        narrow = response_norms(
            kernel,
            gaussian_cell_average(n, c / n),
        )[:, 0]
        atom = response_norms(kernel, gaussian_cell_average(n, 0.0))[:, 0]
        relative = np.abs(narrow - atom) / atom
        central_mass = gaussian_cell_average(n, c / n)[(n - 1) // 2]
        rows.append(
            {
                "side_length": int(n),
                "epsilon_over_h": c,
                "central_cell_mass": float(central_mass),
                "relative_response_errors_to_atom": relative.tolist(),
                "maximum_relative_error": float(np.max(relative)),
            }
        )
    return {
        "width_rule": "epsilon/h=n^-1/4",
        "lattice_times": list(map(float, lattice_times)),
        "rows": rows,
    }


def bridge_audit(
    continuum_time_ratios: Sequence[float] = (0.1, 1.0, 10.0),
    width_ratios: Sequence[float] = (2.0, 4.0, 8.0, 16.0, 32.0),
) -> dict[str, object]:
    """Audit sqrt(c) Psi_c(c^2 q) -> P(q)."""
    continuum = {
        float(q): continuum_phase_norm(q) for q in continuum_time_ratios
    }
    rows = []
    for c in width_ratios:
        scaled = []
        relative = []
        for q in continuum_time_ratios:
            value = math.sqrt(c) * lattice_phase_norm(c * c * q, c)
            scaled.append(value)
            relative.append(abs(value / continuum[float(q)] - 1.0))
        rows.append(
            {
                "epsilon_over_h": float(c),
                "scaled_lattice_phase": scaled,
                "continuum_phase": [
                    continuum[float(q)] for q in continuum_time_ratios
                ],
                "relative_errors": relative,
                "maximum_relative_error": max(relative),
            }
        )
    return {
        "continuum_time_ratios": list(map(float, continuum_time_ratios)),
        "identity": "sqrt(c) Psi_c(c^2 q) -> P(q)",
        "squared_form": "c Psi_c(c^2 q)^2 -> P(q)^2",
        "rows": rows,
    }


def phase_peak_audit(
    width_ratios: Sequence[float] = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0),
) -> dict[str, object]:
    """Locate the maximum-response ridge across the lattice phase diagram."""
    continuum_optimizer = minimize_scalar(
        lambda ratio: -continuum_phase_norm(float(ratio)),
        bounds=(0.01, 10.0),
        method="bounded",
        options={"xatol": 1e-10},
    )
    continuum_time = float(continuum_optimizer.x)
    continuum_peak = float(-continuum_optimizer.fun)
    rows = []
    for c in width_ratios:
        optimizer = minimize_scalar(
            lambda tau: -lattice_phase_norm(float(tau), float(c)),
            bounds=(0.001, max(100.0, 10.0 * float(c) ** 2)),
            method="bounded",
            options={"xatol": 1e-9},
        )
        tau_peak = float(optimizer.x)
        peak = float(-optimizer.fun)
        row = {
            "epsilon_over_h": float(c),
            "lattice_time_at_peak": tau_peak,
            "phase_peak": peak,
        }
        if c > 0.0:
            row.update(
                {
                    "tau_peak_over_c_squared": tau_peak / float(c) ** 2,
                    "sqrt_c_times_peak": math.sqrt(float(c)) * peak,
                    "relative_peak_time_error_to_continuum": abs(
                        tau_peak / float(c) ** 2 / continuum_time - 1.0
                    ),
                    "relative_peak_height_error_to_continuum": abs(
                        math.sqrt(float(c)) * peak / continuum_peak - 1.0
                    ),
                }
            )
        rows.append(row)
    return {
        "continuum_time_ratio_at_peak": continuum_time,
        "continuum_phase_peak": continuum_peak,
        "large_c_ridge": (
            "tau_peak/c^2 -> q_peak and sqrt(c) Psi_peak -> P_peak"
        ),
        "rows": rows,
    }


def even_source_control() -> dict[str, object]:
    """Even k has a quadratic, rather than linear, early causal profile."""
    samples = (1e-4, 3e-4, 1e-3, 3e-3)
    odd = np.asarray([limiting_source_profile(s, 1) for s in samples])
    even = np.asarray([limiting_source_profile(s, 2) for s in samples])
    odd_orders = np.log(odd[1:] / odd[:-1]) / np.log(
        np.asarray(samples[1:]) / np.asarray(samples[:-1])
    )
    even_orders = np.log(even[1:] / even[:-1]) / np.log(
        np.asarray(samples[1:]) / np.asarray(samples[:-1])
    )
    return {
        "scaled_target_rates": list(samples),
        "odd_mode_profile": odd.tolist(),
        "even_mode_profile": even.tolist(),
        "odd_local_orders": odd_orders.tolist(),
        "even_local_orders": even_orders.tolist(),
        "meaning": (
            "the advertised t epsilon^-5/2 law is for odd source modes; "
            "reflection selection cancels its coefficient for even modes"
        ),
    }


def run_stage_vii_audit(fast: bool = False) -> dict[str, object]:
    """Run the complete reproducible Stage VII computational audit."""
    resolved_sides = (127, 255) if fast else (127, 255, 511)
    lattice_sides = (63, 127, 255) if fast else (63, 127, 255, 511)
    return {
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "mpmath": mp.__version__,
            "platform": platform.platform(),
        },
        "declared_model": {
            "cells": "x_j=(j+1/2)/n, h=1/n, odd n keeps centre 1/2 exact",
            "generator": "G_n=A_n tensor I+(I+(4/5)D_n) tensor A_n",
            "target": "cell averages of a Gaussian centred at 1/2",
            "source_mode": SOURCE_MODE,
            "response_norm": (
                "complete density-normalized target L2 norm; no target-band cutoff"
            ),
        },
        "normalization_and_dense_modal": normalization_and_dense_audit(),
        "high_precision_constants": high_precision_constants(50 if fast else 60),
        "first_jet_scaling": first_jet_scaling_audit(
            (127, 255, 511, 1023) if fast else (127, 255, 511, 1023, 2047)
        ),
        "continuum_crossover": continuum_crossover_audit(),
        "resolved_discrete_collapse": resolved_discrete_collapse_audit(
            resolved_sides
        ),
        "lattice_phase": lattice_phase_audit(lattice_sides),
        "vanishing_width_ratio": vanishing_width_ratio_audit(lattice_sides),
        "lattice_to_continuum_bridge": bridge_audit(),
        "maximum_response_ridge": phase_peak_audit(),
        "even_source_control": even_source_control(),
        "status": {
            "exact_or_analytic": (
                "finite modal reduction; normalization cancellation; Gaussian "
                "cell-average formula; finite first-jet identity; closed F_k; "
                "Gaussian Fourier/H2 constants; phase-limit formulas and their "
                "small/large-ratio exponents"
            ),
            "high_precision_not_interval": (
                f"{50 if fast else 60}-digit quadrature independently checks "
                "the scalar phase constants"
            ),
            "floating_evidence": (
                "finite-n convergence to both phase functions and the bridge between them"
            ),
            "not_claimed": (
                "no outward-rounded enclosure of the improper phase integrals and "
                "no uniform error bound over all simultaneous paths (h,eps,t)"
            ),
        },
    }


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fast", action="store_true")
    return parser.parse_args()


def main() -> None:
    arguments = _parse_arguments()
    print(json.dumps(run_stage_vii_audit(arguments.fast), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
