#!/usr/bin/env python3
"""Stage IX numerical laboratory for growing-band OIG response Gramians.

The finite model is the declared cell-centred, one-way parabolic model used in
Stages VI--VIII.  This file is intentionally import-clean and self-contained:
it reimplements the small amount of modal machinery that it needs instead of
depending on a previous research script.

For source modes 1,...,K the laboratory assembles the full target-density
response matrix

    R_h(t)[ell,k] = beta_ell <1, exp[-t K_{ell,h}] phi_k>_h.

It then studies stacked response Gramians in the resolved, lattice, atomic,
and reflecting-boundary charts.  Two issues are kept separate:

* atlas accuracy, measured against the multiplication-only high-target-rate
  reference and governed by the source diffusion number
  delta_K=t*mu_{K,h}=tau*omega_{K,h}; and
* inverse stability, measured by the singular spectrum of a calibrated
  protocol operator.

The exact finite modal reduction and the declared symmetry/null statements are
algebraic.  Every fitted slope, numerical rank, and collapse table is ordinary
floating-point evidence, not an outward-rounded certificate or a proof of a
growing-band theorem.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import sys
from dataclasses import dataclass
from typing import Sequence

import mpmath as mp
import numpy as np
import scipy
from scipy.linalg import eigh_tridiagonal, expm
from scipy.special import ndtr


INTERACTION_STRENGTH = 4.0 / 5.0
DEFAULT_TIME_MULTIPLIERS = (0.25, 0.5, 1.0, 2.0, 4.0)


def cell_centres(side_length: int) -> np.ndarray:
    """Return the cell centres (j+1/2)/n."""
    if side_length < 3:
        raise ValueError("side_length must be at least three")
    return (np.arange(side_length, dtype=float) + 0.5) / side_length


def cosine_modes(side_length: int, modes: Sequence[int]) -> np.ndarray:
    """Euclidean-orthonormal cell-centred Neumann cosine modes."""
    indices = tuple(int(mode) for mode in modes)
    if not indices or any(mode < 0 or mode >= side_length for mode in indices):
        raise ValueError("modes must be a nonempty subset of [0,n)")
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
    """Return omega_k=h^2 mu_{k,h}=4 sin^2(pi k/(2n))."""
    indices = np.arange(side_length, dtype=float)
    return 4.0 * np.sin(math.pi * indices / (2.0 * side_length)) ** 2


def physical_eigenvalues(side_length: int) -> np.ndarray:
    """Eigenvalues mu_{k,h}=n^2 omega_k of the physical path generator."""
    return side_length**2 * lattice_symbol(side_length)


def raw_neumann_path(side_length: int) -> np.ndarray:
    """The unscaled reflecting path Laplacian L_n=h^2 A_h."""
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
    """Canonical positive ramp V(x)=1+g x."""
    if interaction_strength < 0.0:
        raise ValueError("interaction_strength must be nonnegative")
    return 1.0 + interaction_strength * cell_centres(side_length)


def constant_modulation(side_length: int, value: float = 1.4) -> np.ndarray:
    """Positive constant control, for which every nonconstant port is null."""
    if value <= 0.0:
        raise ValueError("value must be positive")
    return np.full(side_length, float(value))


def symmetric_modulation(
    side_length: int,
    interaction_strength: float = INTERACTION_STRENGTH,
) -> np.ndarray:
    """Reflection-symmetric control V(x)=1+g(x-1/2)^2."""
    if interaction_strength < 0.0:
        raise ValueError("interaction_strength must be nonnegative")
    return 1.0 + interaction_strength * (cell_centres(side_length) - 0.5) ** 2


def gaussian_cell_masses(
    side_length: int,
    width_ratio: float,
    placement_phase: float = 0.0,
    anchor: int | None = None,
) -> np.ndarray:
    """Conservative Gaussian cell masses for c=epsilon/h.

    ``c=0`` is the declared atom convention.  ``placement_phase=1/2`` is
    represented by the symmetric two-cell weak limit.
    """
    n = int(side_length)
    c = float(width_ratio)
    theta = float(placement_phase)
    if c < 0.0 or not -0.5 <= theta <= 0.5:
        raise ValueError("invalid width ratio or placement phase")
    carrier = (n - 1) // 2 if anchor is None else int(anchor)
    if not 0 <= carrier < n:
        raise ValueError("anchor is outside the grid")
    centre = (carrier + 0.5 + theta) / n
    if not 0.0 < centre < 1.0:
        raise ValueError("preparation centre must be interior")

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


def boundary_atom_masses(
    side_length: int,
    physical_time: float,
    boundary_ratio: float,
) -> tuple[np.ndarray, float]:
    """Atom nearest y=kappa*sqrt(t), with its achieved boundary ratio."""
    n = int(side_length)
    t = float(physical_time)
    kappa = float(boundary_ratio)
    if t <= 0.0 or kappa < 0.0:
        raise ValueError("physical_time must be positive and kappa nonnegative")
    desired = kappa * math.sqrt(t)
    anchor = int(round(n * desired - 0.5))
    anchor = min(max(anchor, 0), n - 1)
    masses = gaussian_cell_masses(n, 0.0, 0.0, anchor)
    achieved = ((anchor + 0.5) / n) / math.sqrt(t)
    return masses, achieved


def target_coefficients(probability: np.ndarray) -> np.ndarray:
    """Finite target coefficients in the Euclidean cosine convention."""
    masses = np.asarray(probability, dtype=float)
    if masses.ndim != 1 or len(masses) < 3:
        raise ValueError("probability must be a one-dimensional grid vector")
    if np.any(masses < 0.0) or not math.isclose(
        float(np.sum(masses)), 1.0, rel_tol=0.0, abs_tol=2e-13
    ):
        raise ValueError("probability must be nonnegative and normalized")
    return cosine_modes(len(masses), range(len(masses))).T @ masses


@dataclass(frozen=True)
class BandModalKernel:
    """Finite modal source responses in the scaled clock tau=t/h^2."""

    side_length: int
    lattice_times: np.ndarray
    source_modes: tuple[int, ...]
    modulation: np.ndarray
    source_basis: np.ndarray
    values: np.ndarray


def scaled_band_kernel(
    side_length: int,
    lattice_times: Sequence[float],
    source_modes: Sequence[int],
    modulation: np.ndarray | None = None,
) -> BandModalKernel:
    """Exact target-mode reduction, evaluated by tridiagonal spectral sums.

    ``values[a,l,b]`` equals
    ``1^T exp[-tau_a(L_n+omega_l V_n)] u_{k_b}``.
    """
    n = int(side_length)
    taus = np.asarray(lattice_times, dtype=float)
    sources = tuple(int(mode) for mode in source_modes)
    if taus.ndim != 1 or len(taus) == 0 or np.any(taus < 0.0):
        raise ValueError("lattice_times must be a nonempty nonnegative vector")
    if not sources or len(set(sources)) != len(sources):
        raise ValueError("source_modes must be nonempty and distinct")
    if any(mode < 1 or mode >= n for mode in sources):
        raise ValueError("source modes must lie in [1,n)")
    potential = (
        ramp_modulation(n)
        if modulation is None
        else np.asarray(modulation, dtype=float)
    )
    if potential.shape != (n,) or np.min(potential) <= 0.0:
        raise ValueError("modulation must be a positive vector of length n")

    diagonal_l = np.full(n, 2.0)
    diagonal_l[[0, -1]] = 1.0
    off_diagonal = np.full(n - 1, -1.0)
    omega = lattice_symbol(n)
    source_basis = cosine_modes(n, sources)
    ones = np.ones(n)
    values = np.zeros((len(taus), n, len(sources)))

    # l=0 and tau=0 are algebraic nulls for nonconstant source modes.  The
    # explicit zeros avoid manufacturing a false rank from roundoff.
    active_times = taus > 0.0
    for target_mode in range(1, n):
        eigenvalues, eigenvectors = eigh_tridiagonal(
            diagonal_l + omega[target_mode] * potential,
            off_diagonal,
            check_finite=False,
        )
        coefficients = (ones @ eigenvectors)[:, None] * (
            eigenvectors.T @ source_basis
        )
        small = active_times & (taus <= 0.25)
        if np.any(small):
            values[small, target_mode, :] = (
                np.expm1(-np.outer(taus[small], eigenvalues)) @ coefficients
            )
        large = active_times & ~small
        if np.any(large):
            values[large, target_mode, :] = (
                np.exp(-np.outer(taus[large], eigenvalues)) @ coefficients
            )
    return BandModalKernel(
        n,
        taus.copy(),
        sources,
        potential.copy(),
        source_basis.copy(),
        values,
    )


def response_matrix(
    kernel: BandModalKernel,
    target_probability: np.ndarray,
    time_index: int,
) -> np.ndarray:
    """Full density-normalized target response matrix at one time."""
    if not 0 <= int(time_index) < len(kernel.lattice_times):
        raise IndexError("time_index is outside the kernel")
    beta = target_coefficients(target_probability)
    if len(beta) != kernel.side_length:
        raise ValueError("target probability has the wrong side length")
    return beta[:, None] * kernel.values[int(time_index)]


def multiplication_reference_matrix(
    kernel: BandModalKernel,
    target_probability: np.ndarray,
    time_index: int,
) -> np.ndarray:
    """Discrete multiplication-only reference with source diffusion removed.

    This reference retains the exact finite target symbol, preparation
    coefficients, ramp samples, and source cosine samples.  Its only change is
    ``exp[-tau(L+omega V)] -> exp[-tau omega V]``.  It therefore isolates the
    source-diffusion obstruction without mixing in quadrature or symbol error.
    """
    index = int(time_index)
    if not 0 <= index < len(kernel.lattice_times):
        raise IndexError("time_index is outside the kernel")
    tau = float(kernel.lattice_times[index])
    if tau == 0.0:
        return np.zeros((kernel.side_length, len(kernel.source_modes)))
    beta = target_coefficients(target_probability)
    rates = tau * lattice_symbol(kernel.side_length)
    multiplication = np.exp(-np.outer(rates, kernel.modulation))
    return beta[:, None] * (multiplication @ kernel.source_basis)


def direct_dense_response_matrix(
    side_length: int,
    lattice_time: float,
    source_modes: Sequence[int],
    target_probability: np.ndarray,
    modulation: np.ndarray | None = None,
) -> np.ndarray:
    """Small-n n^2-state control, returned in target cosine coordinates."""
    n = int(side_length)
    potential = (
        ramp_modulation(n)
        if modulation is None
        else np.asarray(modulation, dtype=float)
    )
    raw = raw_neumann_path(n)
    generator = np.kron(raw, np.eye(n)) + np.kron(np.diag(potential), raw)
    evolution = expm(-float(lattice_time) * generator)
    marginal = np.kron(np.ones((1, n)), np.eye(n))
    target_basis = cosine_modes(n, range(n))
    source_basis = cosine_modes(n, source_modes)
    columns = []
    for source in source_basis.T:
        injection = np.kron(source / math.sqrt(n), target_probability)
        physical = marginal @ evolution @ injection
        columns.append(math.sqrt(n) * target_basis.T @ physical)
    return np.column_stack(columns)


def source_metric_factors(
    side_length: int,
    source_modes: Sequence[int],
    sobolev_order: float = 0.0,
) -> np.ndarray:
    """Square-root diagonal of the discrete H^s source metric."""
    order = float(sobolev_order)
    if order < 0.0:
        raise ValueError("sobolev_order must be nonnegative")
    modes = np.asarray(tuple(int(k) for k in source_modes), dtype=int)
    if modes.ndim != 1 or len(modes) == 0:
        raise ValueError("source_modes must be nonempty")
    if np.any(modes < 1) or np.any(modes >= side_length):
        raise ValueError("source mode outside the grid")
    mu = physical_eigenvalues(side_length)[modes]
    return (1.0 + mu) ** (order / 2.0)


def output_metric_factors(
    side_length: int,
    negative_sobolev_order: float = 0.0,
) -> np.ndarray:
    """Square-root diagonal of the target H^{-r} output metric."""
    order = float(negative_sobolev_order)
    if order < 0.0:
        raise ValueError("negative_sobolev_order must be nonnegative")
    mu = physical_eigenvalues(side_length)
    return (1.0 + mu) ** (-order / 2.0)


def calibrate_operator(
    matrix: np.ndarray,
    side_length: int,
    source_modes: Sequence[int],
    chart_scale: float = 1.0,
    source_sobolev_order: float = 0.0,
    output_negative_order: float = 0.0,
) -> np.ndarray:
    """Represent a response between unit source/output metric coordinates."""
    response = np.asarray(matrix, dtype=float)
    modes = tuple(int(mode) for mode in source_modes)
    if response.shape != (side_length, len(modes)):
        raise ValueError("matrix shape does not match side length/source modes")
    if chart_scale <= 0.0:
        raise ValueError("chart_scale must be positive")
    source = source_metric_factors(side_length, modes, source_sobolev_order)
    output = output_metric_factors(side_length, output_negative_order)
    return float(chart_scale) * output[:, None] * response / source[None, :]


def stacked_protocol_operator(
    kernel: BandModalKernel,
    target_probabilities: Sequence[np.ndarray] | np.ndarray,
    chart_scales: Sequence[float] | float,
    source_sobolev_order: float = 0.0,
    output_negative_order: float = 0.0,
    multiplication_reference: bool = False,
) -> np.ndarray:
    """Stack equally weighted observation times into one protocol operator."""
    count = len(kernel.lattice_times)
    if isinstance(target_probabilities, np.ndarray) and target_probabilities.ndim == 1:
        targets = [target_probabilities] * count
    else:
        targets = list(target_probabilities)
    if np.isscalar(chart_scales):
        scales = [float(chart_scales)] * count
    else:
        scales = [float(value) for value in chart_scales]
    if len(targets) != count or len(scales) != count:
        raise ValueError("one target and scale are required per observation time")
    blocks = []
    weight = 1.0 / math.sqrt(count)
    builder = (
        multiplication_reference_matrix if multiplication_reference else response_matrix
    )
    for index, (target, scale) in enumerate(zip(targets, scales)):
        blocks.append(
            weight
            * calibrate_operator(
                builder(kernel, target, index),
                kernel.side_length,
                kernel.source_modes,
                scale,
                source_sobolev_order,
                output_negative_order,
            )
        )
    return np.vstack(blocks)


def singular_summary(matrix: np.ndarray) -> dict[str, object]:
    """Singular spectrum and a deliberately labelled floating rank."""
    operator = np.asarray(matrix, dtype=float)
    if operator.ndim != 2 or min(operator.shape) == 0:
        raise ValueError("matrix must be nonempty and two-dimensional")
    singular = np.linalg.svd(operator, compute_uv=False)
    largest = float(singular[0])
    tolerance = float(max(operator.shape) * np.finfo(float).eps * largest)
    resolved = singular[singular > tolerance]
    rank = int(len(resolved))
    smallest_resolved = float(resolved[-1]) if rank else 0.0
    raw_smallest = float(singular[-1])
    return {
        "singular_values": [float(value) for value in singular],
        "largest_singular_value": largest,
        "raw_smallest_singular_value": raw_smallest,
        "numerical_rank_tolerance": tolerance,
        "numerically_resolved_rank": rank,
        "smallest_numerically_resolved_singular_value": smallest_resolved,
        "raw_condition_number": (
            float(largest / raw_smallest) if raw_smallest > 0.0 else None
        ),
        "stable_rank": (
            float(np.sum(singular**2) / largest**2) if largest > 0.0 else 0.0
        ),
        "gram_eigenvalues_from_svd": [
            float(value * value) for value in singular[::-1]
        ],
    }


def _relative_norm_error(value: np.ndarray, reference: np.ndarray) -> float | None:
    denominator = float(np.linalg.norm(reference))
    if denominator == 0.0:
        return None
    return float(np.linalg.norm(value - reference) / denominator)


def _operator_relative_error(value: np.ndarray, reference: np.ndarray) -> float | None:
    denominator = float(np.linalg.norm(reference, 2))
    if denominator == 0.0:
        return None
    return float(np.linalg.norm(value - reference, 2) / denominator)


def exact_and_symmetry_controls() -> dict[str, object]:
    """Dense/modal identity, Gram identity, and declared null controls."""
    n = 7
    tau = 0.17
    modes = (1, 2, 3)
    target = gaussian_cell_masses(n, 0.73, 0.31)
    kernel = scaled_band_kernel(n, (tau,), modes)
    modal = response_matrix(kernel, target, 0)
    dense = direct_dense_response_matrix(n, tau, modes, target)

    protocol = calibrate_operator(modal, n, modes)
    gram = protocol.T @ protocol
    singular = np.linalg.svd(protocol, compute_uv=False)
    gram_eigenvalues = np.linalg.eigvalsh(gram)[::-1]

    zero_kernel = scaled_band_kernel(n, (0.0,), modes)
    constant_kernel = scaled_band_kernel(
        31,
        (0.03, 0.3, 3.0),
        tuple(range(1, 9)),
        constant_modulation(31),
    )
    symmetric_kernel = scaled_band_kernel(
        31,
        (0.03, 0.3, 3.0),
        tuple(range(1, 9)),
        symmetric_modulation(31),
    )
    symmetric_target = gaussian_cell_masses(31, 1.0, 0.0)
    symmetric_response = np.stack(
        [response_matrix(symmetric_kernel, symmetric_target, index) for index in range(3)]
    )
    odd_columns = symmetric_response[:, :, 0::2]
    even_columns = symmetric_response[:, :, 1::2]

    return {
        "exact_statements": [
            "target-mode separation of the finite Kronecker generator",
            "Gamma=A^*A and its eigenvalues are the squared singular values of A",
            "all nonconstant sources vanish at time zero",
            "constant modulation makes every nonconstant source exactly invisible",
            "reflection-symmetric modulation makes reflection-odd cosine sources exactly invisible",
        ],
        "floating_checks": {
            "dense_modal_maximum_error": float(np.max(np.abs(modal - dense))),
            "dense_modal_relative_frobenius_error": float(
                np.linalg.norm(modal - dense) / np.linalg.norm(dense)
            ),
            "gram_singular_square_maximum_error": float(
                np.max(np.abs(gram_eigenvalues - singular**2))
            ),
            "explicit_time_zero_maximum": float(np.max(np.abs(zero_kernel.values))),
            "constant_modulation_maximum_response": float(
                np.max(np.abs(constant_kernel.values))
            ),
            "symmetric_odd_maximum_response": float(np.max(np.abs(odd_columns))),
            "symmetric_even_minimum_column_norm": float(
                min(
                    np.linalg.norm(even_columns[:, :, index])
                    for index in range(even_columns.shape[2])
                )
            ),
        },
    }


def _chart_target_and_scale(
    chart: str,
    side_length: int,
    lattice_time: float,
) -> tuple[np.ndarray, float, dict[str, float]]:
    """One target/normalization point for a declared asymptotic chart."""
    n = int(side_length)
    tau = float(lattice_time)
    t = tau / n**2
    if chart == "lattice":
        return gaussian_cell_masses(n, 1.0, 0.23), n ** (-0.5), {
            "epsilon_over_h": 1.0,
            "physical_time": t,
        }
    if chart == "resolved":
        c = math.sqrt(n)
        epsilon = c / n
        return gaussian_cell_masses(n, c, 0.23), math.sqrt(epsilon), {
            "epsilon_over_h": c,
            "physical_time": t,
            "t_over_epsilon_squared": t / epsilon**2,
        }
    if chart == "atomic":
        return gaussian_cell_masses(n, 0.0, 0.23), t**0.25, {
            "epsilon_over_h": 0.0,
            "physical_time": t,
        }
    if chart == "boundary":
        target, achieved = boundary_atom_masses(n, t, 1.0)
        return target, t**0.25, {
            "epsilon_over_h": 0.0,
            "physical_time": t,
            "boundary_distance_over_sqrt_t": achieved,
        }
    if chart == "boundary_endpoint":
        return gaussian_cell_masses(n, 0.0, 0.0, 0), t**0.25, {
            "epsilon_over_h": 0.0,
            "physical_time": t,
            "boundary_distance_over_sqrt_t": 0.5 / (n * math.sqrt(t)),
        }
    raise ValueError(f"unknown chart: {chart}")


def chart_bandwidth_audit(
    side_lengths: Sequence[int] = (63, 127, 255),
) -> dict[str, object]:
    """Cutoff experiment isolating delta_K=t mu_{K,h}."""
    rows: list[dict[str, object]] = []
    for n_value in side_lengths:
        n = int(n_value)
        physical_bands = sorted(
            {
                1,
                2,
                4,
                max(1, int(round(0.25 * math.sqrt(n)))),
                max(1, int(round(1.50 * math.sqrt(n)))),
            }
        )
        lattice_bands = sorted(
            {
                1,
                2,
                4,
                max(1, int(round(0.10 * n))),
                max(1, int(round(0.30 * n))),
            }
        )
        physical_kernel = scaled_band_kernel(n, (float(n),), range(1, max(physical_bands) + 1))
        lattice_kernel = scaled_band_kernel(n, (0.3,), range(1, max(lattice_bands) + 1))

        for chart in ("resolved", "atomic", "boundary"):
            target, scale, metadata = _chart_target_and_scale(chart, n, float(n))
            exact = response_matrix(physical_kernel, target, 0)
            reference = multiplication_reference_matrix(physical_kernel, target, 0)
            for band in physical_bands:
                exact_band = scale * exact[:, :band]
                reference_band = scale * reference[:, :band]
                column_errors = [
                    _relative_norm_error(exact[:, index], reference[:, index])
                    for index in range(band)
                ]
                summary = singular_summary(exact_band)
                rows.append(
                    {
                        "chart": chart,
                        "side_length": n,
                        "source_band": band,
                        "source_diffusion_number": float(
                            n * lattice_symbol(n)[band]
                        ),
                        "last_column_relative_error": column_errors[-1],
                        "worst_column_relative_error": max(
                            float(value) for value in column_errors if value is not None
                        ),
                        "band_operator_relative_error": _operator_relative_error(
                            exact_band, reference_band
                        ),
                        "raw_smallest_singular_value": summary[
                            "raw_smallest_singular_value"
                        ],
                        "numerically_resolved_rank": summary[
                            "numerically_resolved_rank"
                        ],
                        **metadata,
                    }
                )

        target, scale, metadata = _chart_target_and_scale("lattice", n, 0.3)
        exact = response_matrix(lattice_kernel, target, 0)
        reference = multiplication_reference_matrix(lattice_kernel, target, 0)
        for band in lattice_bands:
            exact_band = scale * exact[:, :band]
            reference_band = scale * reference[:, :band]
            column_errors = [
                _relative_norm_error(exact[:, index], reference[:, index])
                for index in range(band)
            ]
            summary = singular_summary(exact_band)
            rows.append(
                {
                    "chart": "lattice",
                    "side_length": n,
                    "source_band": band,
                    "source_diffusion_number": float(
                        0.3 * lattice_symbol(n)[band]
                    ),
                    "last_column_relative_error": column_errors[-1],
                    "worst_column_relative_error": max(
                        float(value) for value in column_errors if value is not None
                    ),
                    "band_operator_relative_error": _operator_relative_error(
                        exact_band, reference_band
                    ),
                    "raw_smallest_singular_value": summary[
                        "raw_smallest_singular_value"
                    ],
                    "numerically_resolved_rank": summary[
                        "numerically_resolved_rank"
                    ],
                    **metadata,
                }
            )

    fixed_band = [row for row in rows if row["source_band"] == 2]
    physical_critical = [
        row
        for row in rows
        if row["chart"] in ("resolved", "atomic", "boundary")
        and row["source_band"]
        == max(1, int(round(0.25 * math.sqrt(int(row["side_length"])))))
    ]
    lattice_critical = [
        row
        for row in rows
        if row["chart"] == "lattice"
        and row["source_band"] == max(1, int(round(0.30 * int(row["side_length"]))))
    ]
    return {
        "rows": rows,
        "fixed_band_K2": fixed_band,
        "critical_physical_band_K_approximately_quarter_sqrt_n": physical_critical,
        "critical_lattice_band_K_approximately_0.30n": lattice_critical,
        "interpretation": (
            "fixed K drives delta_K to zero; K proportional to sqrt(n) on the "
            "resolved/atomic clocks and K proportional to n on the lattice clock "
            "keeps delta_K nonzero and leaves a persistent last-port error"
        ),
    }


def _protocol_chart_data(
    chart: str,
    side_length: int,
    lattice_times: Sequence[float],
) -> tuple[Sequence[np.ndarray] | np.ndarray, list[float]]:
    n = int(side_length)
    if chart == "lattice":
        target = gaussian_cell_masses(n, 1.0, 0.23)
        return target, [n ** (-0.5)] * len(lattice_times)
    if chart == "resolved":
        c = math.sqrt(n)
        target = gaussian_cell_masses(n, c, 0.23)
        return target, [math.sqrt(c / n)] * len(lattice_times)
    if chart == "atomic":
        target = gaussian_cell_masses(n, 0.0, 0.23)
        return target, [float(tau / n**2) ** 0.25 for tau in lattice_times]
    if chart == "boundary_endpoint":
        target = gaussian_cell_masses(n, 0.0, 0.0, 0)
        return target, [float(tau / n**2) ** 0.25 for tau in lattice_times]
    raise ValueError(f"unknown protocol chart: {chart}")


def gramian_growth_audit(
    side_length: int = 255,
    maximum_band: int = 14,
    bands: Sequence[int] = (2, 4, 6, 8, 10, 12, 14),
) -> dict[str, object]:
    """Multi-time weighted Gramians under three metric calibrations."""
    n = int(side_length)
    requested = tuple(sorted(set(int(value) for value in bands)))
    if not requested or requested[-1] > maximum_band or maximum_band >= n:
        raise ValueError("invalid bands or maximum_band")
    modes = tuple(range(1, maximum_band + 1))
    lattice_times = tuple(0.3 * value for value in DEFAULT_TIME_MULTIPLIERS)
    physical_times = tuple(float(n) * value for value in DEFAULT_TIME_MULTIPLIERS)
    lattice_kernel = scaled_band_kernel(n, lattice_times, modes)
    physical_kernel = scaled_band_kernel(n, physical_times, modes)
    metrics = {
        "L2_source_to_L2_output": (0.0, 0.0),
        "H1_source_to_L2_output": (1.0, 0.0),
        "L2_source_to_HminusHalf_output": (0.0, 0.5),
    }
    rows: list[dict[str, object]] = []
    for chart in ("lattice", "resolved", "atomic", "boundary_endpoint"):
        kernel = lattice_kernel if chart == "lattice" else physical_kernel
        targets, scales = _protocol_chart_data(chart, n, kernel.lattice_times)
        for metric_name, (source_order, output_order) in metrics.items():
            operator = stacked_protocol_operator(
                kernel,
                targets,
                scales,
                source_order,
                output_order,
            )
            for band in requested:
                block = operator[:, :band]
                summary = singular_summary(block)
                last_column = float(np.linalg.norm(block[:, -1]))
                smallest = float(summary["raw_smallest_singular_value"])
                rows.append(
                    {
                        "chart": chart,
                        "metric": metric_name,
                        "side_length": n,
                        "source_band": band,
                        "largest_singular_value": summary["largest_singular_value"],
                        "raw_smallest_singular_value": smallest,
                        "smallest_gram_eigenvalue_from_svd": smallest**2,
                        "numerically_resolved_rank": summary[
                            "numerically_resolved_rank"
                        ],
                        "stable_rank": summary["stable_rank"],
                        "last_column_norm_upper_bound": last_column,
                        "smallest_over_last_column_bound": (
                            smallest / last_column if last_column > 0.0 else None
                        ),
                    }
                )
    return {
        "observation_time_multipliers": list(DEFAULT_TIME_MULTIPLIERS),
        "equal_time_weights": 1.0 / len(DEFAULT_TIME_MULTIPLIERS),
        "metric_definitions": {
            "H1_source": "divide mode k by sqrt(1+mu_kh) in unit-metric coordinates",
            "HminusHalf_output": "multiply target mode ell by (1+mu_ellh)^(-1/4)",
            "chart_scalars": (
                "n^-1/2 in the lattice chart, sqrt(epsilon) in the resolved "
                "chart, and t^(1/4) in atomic/boundary charts"
            ),
        },
        "rows": rows,
        "interpretation": (
            "time stacking delays but does not remove singular-value collapse; "
            "a stronger H1 source norm and a weaker H^-1/2 output norm cannot "
            "manufacture a uniform lower frame bound"
        ),
    }


def _loglog_slope(scales: Sequence[float], values: Sequence[float]) -> float:
    x = np.asarray(scales, dtype=float)
    y = np.asarray(values, dtype=float)
    mask = (x > 0.0) & (y > 0.0) & np.isfinite(y)
    if np.count_nonzero(mask) < 2:
        return float("nan")
    return float(np.polyfit(np.log(x[mask]), np.log(y[mask]), 1)[0])


def multiplication_column_decay_audit(
    side_length: int = 511,
    maximum_band: int = 64,
    minimum_fit_mode: int = 16,
) -> dict[str, object]:
    """High-k column envelope of the multiplication-only chart operator."""
    n = int(side_length)
    max_band = int(maximum_band)
    modes = tuple(range(1, max_band + 1))
    # Only the source basis/modulation fields are needed for the reference;
    # using tau=0 avoids unnecessary positive-time spectral work here.
    shell = BandModalKernel(
        n,
        np.asarray((0.0,)),
        modes,
        ramp_modulation(n),
        cosine_modes(n, modes),
        np.zeros((1, n, max_band)),
    )
    configurations = {
        "lattice": (0.3, gaussian_cell_masses(n, 1.0, 0.23), n ** (-0.5)),
        "resolved": (
            float(n),
            gaussian_cell_masses(n, math.sqrt(n), 0.23),
            n ** (-0.25),
        ),
        "atomic": (
            float(n),
            gaussian_cell_masses(n, 0.0, 0.23),
            n ** (-0.25),
        ),
        "boundary_endpoint": (
            float(n),
            gaussian_cell_masses(n, 0.0, 0.0, 0),
            n ** (-0.25),
        ),
    }
    rows = []
    indices = np.arange(1, max_band + 1)
    for chart, (tau, target, scale) in configurations.items():
        kernel = BandModalKernel(
            shell.side_length,
            np.asarray((tau,)),
            shell.source_modes,
            shell.modulation,
            shell.source_basis,
            shell.values,
        )
        reference = multiplication_reference_matrix(kernel, target, 0)
        for source_order in (0.0, 1.0):
            calibrated = calibrate_operator(
                reference,
                n,
                modes,
                scale,
                source_order,
                0.0,
            )
            norms = np.linalg.norm(calibrated, axis=0)
            for parity_name, parity in (("odd", 1), ("even", 0)):
                mask = (indices >= minimum_fit_mode) & (indices % 2 == parity)
                rows.append(
                    {
                        "chart": chart,
                        "source_sobolev_order": source_order,
                        "parity": parity_name,
                        "minimum_fit_mode": minimum_fit_mode,
                        "maximum_fit_mode": max_band,
                        "empirical_column_norm_power_in_k": _loglog_slope(
                            indices[mask], norms[mask]
                        ),
                        "last_same_parity_mode": int(indices[mask][-1]),
                        "last_same_parity_column_norm": float(norms[mask][-1]),
                    }
                )
    return {
        "rows": rows,
        "analytic_upper_bound": (
            "sigma_min(A_K) <= ||A_K e_K||.  For the ramp multiplication "
            "profile, |F_k(s)| has a k^-2 envelope; H^s unit coordinates add "
            "k^-s.  Thus these reference Gramians cannot have a K-uniform "
            "positive lower bound."
        ),
        "proof_boundary": (
            "the matrix inequality and explicit ramp envelope are analytic; "
            "the fitted powers in this table are floating-point evidence"
        ),
    }


def boundary_endpoint_gain_audit(
    side_lengths: Sequence[int] = (63, 127, 255),
    source_band: int = 4,
) -> dict[str, object]:
    """Check the endpoint square-root-of-two gain on a finite source band."""
    rows = []
    for n_value in side_lengths:
        n = int(n_value)
        taus = tuple(float(n) * value for value in (0.5, 1.0, 2.0))
        kernel = scaled_band_kernel(n, taus, range(1, source_band + 1))
        scales = [float(tau / n**2) ** 0.25 for tau in taus]
        central = gaussian_cell_masses(n, 0.0, 0.23)
        endpoint = gaussian_cell_masses(n, 0.0, 0.0, 0)
        central_operator = stacked_protocol_operator(kernel, central, scales)
        endpoint_operator = stacked_protocol_operator(kernel, endpoint, scales)
        central_singular = np.linalg.svd(central_operator, compute_uv=False)
        endpoint_singular = np.linalg.svd(endpoint_operator, compute_uv=False)
        ratios = endpoint_singular / central_singular
        rows.append(
            {
                "side_length": n,
                "source_band": source_band,
                "largest_singular_value_ratio_endpoint_over_interior": float(
                    ratios[0]
                ),
                "singular_value_ratios_endpoint_over_interior": [
                    float(value) for value in ratios
                ],
                "distance_of_largest_ratio_from_sqrt_two": float(
                    abs(ratios[0] - math.sqrt(2.0))
                ),
            }
        )
    return {
        "rows": rows,
        "reference_ratio": math.sqrt(2.0),
        "interpretation": (
            "the endpoint doubles the leading squared response constant, so a "
            "fixed finite response operator is expected to acquire a sqrt(2) "
            "singular-value factor in the atomic limit"
        ),
    }


def continuum_kernel_value(
    summed_modulation: mp.mpf,
    chart: str,
    *,
    q: mp.mpf | float = 1.0,
    lattice_time: mp.mpf | float = 1.0,
    boundary_ratio: mp.mpf | float = 1.0,
) -> mp.mpf:
    """Exact continuum Gram kernel Phi(A) for the four declared charts."""
    A = mp.mpf(summed_modulation)
    if A <= 0:
        raise ValueError("summed_modulation must be positive")
    if chart == "resolved":
        q_value = mp.mpf(q)
        if q_value < 0:
            raise ValueError("q must be nonnegative")
        return 1 / (2 * mp.sqrt(mp.pi) * mp.sqrt(1 + q_value * A))
    if chart == "atomic":
        return 1 / (2 * mp.sqrt(mp.pi * A))
    if chart == "lattice_atom":
        tau = mp.mpf(lattice_time)
        if tau <= 0:
            raise ValueError("lattice_time must be positive")
        return mp.exp(-2 * tau * A) * mp.besseli(0, 2 * tau * A)
    if chart == "boundary_atomic":
        kappa = mp.mpf(boundary_ratio)
        if kappa < 0:
            raise ValueError("boundary_ratio must be nonnegative")
        return (1 + mp.exp(-(kappa**2) / A)) / (
            2 * mp.sqrt(mp.pi * A)
        )
    raise ValueError(f"unknown continuum chart: {chart}")


def _mp_quadrature_basis(
    maximum_band: int,
    quadrature_order: int,
) -> tuple[list[mp.mpf], list[mp.mpf], mp.matrix]:
    nodes_raw, weights_raw = mp.gauss_quadrature(quadrature_order, "legendre")
    nodes = [(nodes_raw[index] + 1) / 2 for index in range(quadrature_order)]
    weights = [weights_raw[index] / 2 for index in range(quadrature_order)]
    basis = mp.matrix(quadrature_order, maximum_band)
    for row, x in enumerate(nodes):
        for mode in range(1, maximum_band + 1):
            basis[row, mode - 1] = mp.sqrt(2) * mp.cos(mp.pi * mode * x)
    return nodes, weights, basis


def _mp_continuum_gram(
    nodes: Sequence[mp.mpf],
    weights: Sequence[mp.mpf],
    basis: mp.matrix,
    chart: str,
    *,
    q: mp.mpf | float = 1.0,
    lattice_time: mp.mpf | float = 1.0,
    boundary_ratio: mp.mpf | float = 1.0,
) -> mp.matrix:
    """High-precision Gauss--Legendre assembly of X^* Phi(Vx+Vy) X."""
    order = len(nodes)
    weighted_kernel = mp.matrix(order, order)
    strength = mp.mpf(str(INTERACTION_STRENGTH))
    modulation = [1 + strength * x for x in nodes]
    for left in range(order):
        for right in range(order):
            weighted_kernel[left, right] = (
                weights[left]
                * weights[right]
                * continuum_kernel_value(
                    modulation[left] + modulation[right],
                    chart,
                    q=q,
                    lattice_time=lattice_time,
                    boundary_ratio=boundary_ratio,
                )
            )
    return basis.T * weighted_kernel * basis


def _mp_prefix_singular_values(
    gram: mp.matrix,
    source_band: int,
) -> list[mp.mpf]:
    block = gram[:source_band, :source_band]
    eigenvalues, _ = mp.eigsy(block)
    values = []
    for index in range(source_band - 1, -1, -1):
        value = eigenvalues[index]
        # A negative value many orders below the matrix scale can only be a
        # numerical quadrature/eigensolver residual.  Do not silently repair a
        # material negative eigenvalue.
        if value < 0:
            scale = max(abs(eigenvalues[source_band - 1]), mp.mpf(1))
            if abs(value) > mp.eps * scale * 1000:
                raise ArithmeticError("high-precision Gram lost positivity")
            value = mp.mpf(0)
        values.append(mp.sqrt(value))
    return values


def _mp_log_slope(
    scales: Sequence[mp.mpf],
    values: Sequence[mp.mpf],
) -> mp.mpf:
    x = [mp.log(value) for value in scales]
    y = [mp.log(value) for value in values]
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    return sum((a - x_mean) * (b - y_mean) for a, b in zip(x, y)) / sum(
        (a - x_mean) ** 2 for a in x
    )


def _mp_scientific(value: mp.mpf, digits: int = 14) -> str:
    return mp.nstr(value, digits, min_fixed=0, max_fixed=0)


def _mp_condition_from_gram(gram: mp.matrix) -> mp.mpf:
    singular = _mp_prefix_singular_values(gram, gram.rows)
    if singular[-1] == 0:
        return mp.inf
    return singular[0] / singular[-1]


def _mp_moment_matrix(
    nodes: Sequence[mp.mpf],
    weights: Sequence[mp.mpf],
    basis: mp.matrix,
    source_band: int,
) -> mp.matrix:
    """E[r-1,k-1]=(-1)^r/r! integral V^r phi_k."""
    strength = mp.mpf(str(INTERACTION_STRENGTH))
    matrix = mp.matrix(source_band, source_band)
    for order in range(1, source_band + 1):
        for mode in range(source_band):
            matrix[order - 1, mode] = sum(
                weights[index]
                * ((-1) ** order)
                * (1 + strength * nodes[index]) ** order
                / mp.factorial(order)
                * basis[index, mode]
                for index in range(len(nodes))
            )
    return matrix


def continuum_kernel_high_precision_audit(
    maximum_band: int = 10,
    early_band: int = 4,
    quadrature_order: int = 64,
    decimal_precision: int = 100,
) -> dict[str, object]:
    """Test exact chart kernels, early fans, rank loss, and preconditioning."""
    max_band = int(maximum_band)
    early_k = int(early_band)
    if not 1 <= early_k <= max_band:
        raise ValueError("early_band must lie in [1,maximum_band]")
    if quadrature_order < 2 * max_band + 8:
        raise ValueError("quadrature_order is too small for the requested band")

    with mp.workdps(decimal_precision):
        nodes, weights, basis = _mp_quadrature_basis(
            max_band, quadrature_order
        )

        # Independent one-dimensional phase integrals verify the four kernel
        # reductions and their normalizations before any spectral claim is
        # read from the assembled matrices.
        def profile(scaled_rate: mp.mpf, mode: int) -> mp.mpf:
            strength = mp.mpf(str(INTERACTION_STRENGTH))
            a = strength * scaled_rate
            return (
                mp.sqrt(2)
                * mp.exp(-scaled_rate)
                * a
                * (1 - ((-1) ** mode) * mp.exp(-a))
                / (a**2 + (mode * mp.pi) ** 2)
            )

        identity_specs = {
            "resolved_gaussian": (
                "resolved",
                {"q": mp.mpf("0.7")},
                lambda u, left, right: mp.exp(-(mp.pi * u) ** 2)
                * profile(mp.mpf("0.7") * (mp.pi * u) ** 2, left)
                * profile(mp.mpf("0.7") * (mp.pi * u) ** 2, right),
                (mp.mpf(0), mp.inf),
            ),
            "atomic": (
                "atomic",
                {},
                lambda u, left, right: profile((mp.pi * u) ** 2, left)
                * profile((mp.pi * u) ** 2, right),
                (mp.mpf(0), mp.inf),
            ),
            "lattice_atom": (
                "lattice_atom",
                {"lattice_time": mp.mpf("0.7")},
                lambda xi, left, right: profile(
                    4
                    * mp.mpf("0.7")
                    * mp.sin(mp.pi * xi / 2) ** 2,
                    left,
                )
                * profile(
                    4
                    * mp.mpf("0.7")
                    * mp.sin(mp.pi * xi / 2) ** 2,
                    right,
                ),
                (mp.mpf(0), mp.mpf(1)),
            ),
            "boundary_atomic": (
                "boundary_atomic",
                {"boundary_ratio": mp.mpf("0.8")},
                lambda u, left, right: (
                    1 + mp.cos(2 * mp.pi * mp.mpf("0.8") * u)
                )
                * profile((mp.pi * u) ** 2, left)
                * profile((mp.pi * u) ** 2, right),
                (mp.mpf(0), mp.inf),
            ),
        }
        kernel_identity_rows = []
        for name, (chart, keywords, integrand, interval) in identity_specs.items():
            kernel_gram = _mp_continuum_gram(
                nodes, weights, basis[:, :2], chart, **keywords
            )
            maximum_error = mp.mpf(0)
            maximum_relative = mp.mpf(0)
            for left in (1, 2):
                for right in (1, 2):
                    direct = mp.quad(
                        lambda variable: integrand(variable, left, right),
                        list(interval),
                    )
                    error = abs(kernel_gram[left - 1, right - 1] - direct)
                    maximum_error = max(maximum_error, error)
                    if direct != 0:
                        maximum_relative = max(
                            maximum_relative, error / abs(direct)
                        )
            kernel_identity_rows.append(
                {
                    "chart": name,
                    "maximum_absolute_error": _mp_scientific(maximum_error),
                    "maximum_relative_error": _mp_scientific(maximum_relative),
                }
            )

        q_values = [mp.mpf(value) for value in ("0.02", "0.01", "0.005", "0.0025")]
        early_grams = [
            _mp_continuum_gram(
                nodes,
                weights,
                basis[:, :early_k],
                "resolved",
                q=q,
            )
            for q in q_values
        ]
        early_singular = [
            _mp_prefix_singular_values(gram, early_k) for gram in early_grams
        ]
        early_rows = []
        for index in range(early_k):
            values = [singular[index] for singular in early_singular]
            local_powers = [
                mp.log(values[position + 1] / values[position])
                / mp.log(q_values[position + 1] / q_values[position])
                for position in range(len(q_values) - 1)
            ]
            early_rows.append(
                {
                    "singular_index": index + 1,
                    "predicted_power_in_q": index + 1,
                    "fitted_power_in_q": float(_mp_log_slope(q_values, values)),
                    "last_dyadic_power_in_q": float(local_powers[-1]),
                    "singular_values": [_mp_scientific(value) for value in values],
                }
            )
        determinants = []
        for singular in early_singular:
            determinant = mp.mpf(1)
            for value in singular:
                determinant *= value**2
            determinants.append(determinant)
        determinant_local_power = mp.log(determinants[-1] / determinants[-2]) / mp.log(
            q_values[-1] / q_values[-2]
        )

        chart_specs = {
            "balanced_resolved_q1": ("resolved", {"q": mp.mpf(1)}),
            "atomic": ("atomic", {}),
            "lattice_atom_tau1": (
                "lattice_atom",
                {"lattice_time": mp.mpf(1)},
            ),
            "boundary_atomic_kappa1": (
                "boundary_atomic",
                {"boundary_ratio": mp.mpf(1)},
            ),
        }
        chart_grams: dict[str, mp.matrix] = {}
        decay_rows = []
        effective_rank_rows = []
        resolution_rows = []
        noise_levels = [
            mp.mpf(value)
            for value in ("1e-2", "1e-4", "1e-6", "1e-8", "1e-10", "1e-12")
        ]
        for name, (chart, keywords) in chart_specs.items():
            gram = _mp_continuum_gram(
                nodes, weights, basis, chart, **keywords
            )
            chart_grams[name] = gram
            prefix_minima = []
            for band in range(1, max_band + 1):
                singular = _mp_prefix_singular_values(gram, band)
                minimum = singular[-1]
                prefix_minima.append(minimum)
                decay_rows.append(
                    {
                        "chart": name,
                        "source_band": band,
                        "smallest_singular_value": _mp_scientific(minimum),
                        "successive_smallest_ratio": (
                            float(minimum / prefix_minima[-2])
                            if band > 1
                            else None
                        ),
                    }
                )
            full_singular = _mp_prefix_singular_values(gram, max_band)
            for noise in noise_levels:
                threshold = noise * full_singular[0]
                effective_rank_rows.append(
                    {
                        "chart": name,
                        "source_band": max_band,
                        "relative_noise_floor": float(noise),
                        "effective_rank": sum(
                            1 for value in full_singular if value >= threshold
                        ),
                    }
                )
            if name in ("balanced_resolved_q1", "atomic"):
                for band, minimum in enumerate(prefix_minima, start=1):
                    n_required = minimum ** (-mp.mpf("0.5"))
                    resolution_rows.append(
                        {
                            "chart": name,
                            "source_band": band,
                            "smallest_singular_value": _mp_scientific(minimum),
                            "n_where_h_squared_equals_sigma_min": _mp_scientific(
                                n_required
                            ),
                            "log_n_threshold_per_mode": float(
                                mp.log(n_required) / band
                            ),
                        }
                    )

        # Quantify where IEEE double precision reports a false numerical null.
        double_rows = []
        for name, gram in chart_grams.items():
            gram_float = np.asarray(
                [[float(gram[row, col]) for col in range(max_band)] for row in range(max_band)]
            )
            eigen_float = np.linalg.eigvalsh(gram_float)
            tolerance = float(
                max_band * np.finfo(float).eps * max(abs(eigen_float[-1]), 1e-300)
            )
            double_rows.append(
                {
                    "chart": name,
                    "source_band": max_band,
                    "high_precision_positive_rank": max_band,
                    "double_gram_numerical_rank": int(np.count_nonzero(eigen_float > tolerance)),
                    "double_smallest_eigenvalue": float(eigen_float[0]),
                    "double_rank_tolerance": tolerance,
                }
            )

        # Critical fan: physical singulars are epsilon^-1/2 sigma_j(q), with
        # epsilon=h^alpha and q=h^(2-2alpha) on t=h^2.
        alphas = [
            mp.mpf(4 * index) / (4 * index + 1)
            for index in range(1, early_k + 1)
        ]
        if mp.mpf("0.9") not in alphas:
            alphas.append(mp.mpf("0.9"))
        critical_rows = []
        for alpha in sorted(alphas):
            h_values = [q ** (1 / (2 - 2 * alpha)) for q in q_values]
            predicted_nonvanishing = sum(
                1
                for index in range(1, early_k + 1)
                if 2 * index - alpha * (2 * index + mp.mpf("0.5")) <= 0
            )
            for index in range(1, early_k + 1):
                predicted = 2 * index - alpha * (2 * index + mp.mpf("0.5"))
                physical = [
                    h ** (-alpha / 2) * early_singular[position][index - 1]
                    for position, h in enumerate(h_values)
                ]
                critical_rows.append(
                    {
                        "alpha": float(alpha),
                        "singular_index": index,
                        "predicted_power_in_h": float(predicted),
                        "fitted_power_in_h": float(
                            _mp_log_slope(h_values, physical)
                        ),
                        "predicted_nonvanishing_dimension_at_this_alpha": predicted_nonvanishing,
                    }
                )

        # A moment coordinate can remove much of the early q hierarchy, but
        # only by using source vectors with enormous L2 norm.
        moment_k = early_k
        moment = _mp_moment_matrix(
            nodes, weights, basis, moment_k
        )
        inverse_moment = moment**-1
        identity_residual = max(
            abs((moment * inverse_moment)[row, col] - (1 if row == col else 0))
            for row in range(moment_k)
            for col in range(moment_k)
        )
        q_control = mp.mpf("0.005")
        gram_control = early_grams[q_values.index(q_control)]
        moment_gram = inverse_moment.T * gram_control * inverse_moment
        q_scaling = mp.diag(
            [q_control ** (-order) for order in range(1, moment_k + 1)]
        )
        preconditioner = inverse_moment * q_scaling
        preconditioned_gram = preconditioner.T * gram_control * preconditioner
        source_column_norms = [
            mp.sqrt(sum(preconditioner[row, col] ** 2 for row in range(moment_k)))
            for col in range(moment_k)
        ]
        normalizer = mp.diag([1 / value for value in source_column_norms])
        normalized_preconditioned_gram = (
            normalizer.T * preconditioned_gram * normalizer
        )

        return {
            "decimal_precision": decimal_precision,
            "gauss_legendre_order": quadrature_order,
            "exact_kernel_formulas": {
                "resolved_gaussian": "Phi_q(A)=1/[2 sqrt(pi) sqrt(1+q A)]",
                "atomic": "Phi(A)=1/[2 sqrt(pi A)]",
                "lattice_atom": "Phi_tau(A)=exp(-2 tau A) I_0(2 tau A)",
                "boundary_atomic": "Phi_kappa(A)=Phi(A)[1+exp(-kappa^2/A)]",
                "summed_modulation": "A=V(x)+V(y)",
            },
            "kernel_identity_controls": kernel_identity_rows,
            "early_singular_fan": {
                "source_band": early_k,
                "q_values": [float(value) for value in q_values],
                "rows": early_rows,
                "determinant_gram_predicted_power": early_k * (early_k + 1),
                "determinant_gram_fitted_power": float(
                    _mp_log_slope(q_values, determinants)
                ),
                "determinant_gram_last_dyadic_power": float(
                    determinant_local_power
                ),
            },
            "balanced_atomic_exponential_decay": decay_rows,
            "effective_rank_vs_relative_noise": effective_rank_rows,
            "double_precision_rank_loss": double_rows,
            "critical_resolution_fan": {
                "physical_law": "epsilon^-1/2 sigma_j(q), epsilon=h^alpha, q=h^(2-2alpha)",
                "critical_exponents": [
                    float(mp.mpf(4 * index) / (4 * index + 1))
                    for index in range(1, early_k + 1)
                ],
                "rows": critical_rows,
            },
            "logarithmic_band_resolution_audit": {
                "rows": resolution_rows,
                "interpretation": (
                    "if the smallest singular value continues to decay "
                    "geometrically in K, comparison with a polynomial h^2 "
                    "operator error puts the resolvable cutoff at K=O(log n); "
                    "K=o(log n) is the conservative separation.  This is a "
                    "conditional numerical audit, not a proved uniform rate."
                ),
            },
            "moment_preconditioning_control": {
                "source_band": moment_k,
                "q": float(q_control),
                "moment_inverse_identity_residual": _mp_scientific(
                    identity_residual
                ),
                "original_response_condition_number": _mp_scientific(
                    _mp_condition_from_gram(gram_control)
                ),
                "moment_basis_condition_number": _mp_scientific(
                    _mp_condition_from_gram(moment_gram)
                ),
                "q_rescaled_moment_basis_condition_number": _mp_scientific(
                    _mp_condition_from_gram(preconditioned_gram)
                ),
                "q_rescaled_source_L2_column_norms": [
                    _mp_scientific(value) for value in source_column_norms
                ],
                "condition_after_L2_normalizing_preconditioned_ports": _mp_scientific(
                    _mp_condition_from_gram(normalized_preconditioned_gram)
                ),
                "interpretation": (
                    "moment/q preconditioning improves the response matrix only "
                    "by spending very large source L2 norm; normalizing those "
                    "ports restores the physical conditioning penalty"
                ),
            },
            "proof_boundary": [
                "The four Phi formulas follow by exact Gaussian integration or the Bessel identity.",
                "The tables use high-precision quadrature/eigendecomposition and are numerical evidence.",
                "Geometric singular decay is observed for this analytic ramp; a two-sided all-K theorem is not proved here.",
                "Effective rank depends on the declared metric and relative noise threshold.",
            ],
        }


def finite_sampling_rank_control(
    side_length: int = 31,
    source_band: int = 8,
    sample_counts: Sequence[int] = (1, 2, 4, 6, 8),
) -> dict[str, object]:
    """Exact rank cap for finitely many scalar modal observations."""
    n = int(side_length)
    K = int(source_band)
    times = (0.03, 0.1, 0.3, 1.0)
    kernel = scaled_band_kernel(n, times, range(1, K + 1))
    target = gaussian_cell_masses(n, 1.0, 0.23)
    responses = [response_matrix(kernel, target, index) for index in range(len(times))]
    observation_pairs = (
        (0, 1),
        (0, 2),
        (1, 1),
        (1, 3),
        (2, 2),
        (2, 4),
        (3, 3),
        (3, 5),
    )
    sampled = np.vstack(
        [responses[time_index][target_mode, :] for time_index, target_mode in observation_pairs]
    )
    rows = []
    for count_value in sample_counts:
        count = int(count_value)
        if not 1 <= count <= len(observation_pairs):
            raise ValueError("sample count outside the declared observation list")
        operator = sampled[:count]
        singular = np.linalg.svd(operator, compute_uv=False)
        tolerance = max(operator.shape) * np.finfo(float).eps * singular[0]
        numerical_rank = int(np.count_nonzero(singular > tolerance))
        gram_eigenvalues = np.linalg.eigvalsh(operator.T @ operator)
        forced_nullity = max(K - count, 0)
        null_residual = (
            float(np.max(np.abs(gram_eigenvalues[:forced_nullity])))
            if forced_nullity
            else 0.0
        )
        rows.append(
            {
                "scalar_sample_count": count,
                "source_band": K,
                "exact_rank_upper_bound": min(count, K),
                "exact_nullity_lower_bound": forced_nullity,
                "floating_numerical_rank": numerical_rank,
                "maximum_forced_null_gram_residual": null_residual,
            }
        )
    return {
        "rows": rows,
        "exact_statement": (
            "an M by K scalar observation matrix has rank at most M, hence its "
            "K by K Gram has nullity at least K-M when M<K"
        ),
        "interpretation": (
            "full target-density observation supplies many output coordinates; "
            "a theorem for finitely sampled sensors must separately respect this "
            "dimension cap"
        ),
    }


def mixed_word_resolution_diagnostic(
    source_bands: Sequence[int] = (3, 4, 6, 8),
    nominal_side_lengths: Sequence[float] = (1e3, 1e6, 1e12),
    lattice_time: float = 1.0,
) -> dict[str, object]:
    """Scale-only audit of the finite mixed-word error at the critical fan.

    This function does not pretend to simulate grids of size 10^12.  It only
    evaluates the declared asymptotic monomials so the separation demanded by
    a future proof is visible numerically.
    """
    tau = float(lattice_time)
    if tau <= 0.0:
        raise ValueError("lattice_time must be positive")
    rows = []
    for band_value in source_bands:
        band = int(band_value)
        if band < 3:
            raise ValueError("mixed-word diagnostic is declared for K>=3")
        alpha = 4.0 * band / (4.0 * band + 1.0)
        for n_value in nominal_side_lengths:
            n = float(n_value)
            if n <= 1.0:
                raise ValueError("nominal side lengths must exceed one")
            h = 1.0 / n
            epsilon = h**alpha
            physical_time = tau * h**2
            q = physical_time / epsilon**2
            mixed_relative_scale = physical_time * band**2 / q ** (band - 1)
            rows.append(
                {
                    "source_band": band,
                    "critical_alpha": alpha,
                    "nominal_side_length": n,
                    "epsilon_over_h": epsilon / h,
                    "q": q,
                    "mixed_word_relative_scale_tK2_over_q_to_Kminus1": mixed_relative_scale,
                }
            )
    return {
        "rows": rows,
        "required_future_bound": "t K^2 / q^(K-1) -> 0 for the Kth early singular direction",
        "interpretation": (
            "controlling preparation moments or K*epsilon alone is insufficient: "
            "source-diffusion causal words enter before the very small Kth "
            "singular scale.  At the critical fan the mixed-word monomial falls "
            "quickly, while epsilon/h grows extremely slowly as K increases."
        ),
        "proof_boundary": (
            "these are evaluations of an adversarial error monomial, not a "
            "finite-grid convergence experiment and not a proved remainder bound"
        ),
    }


def run_lab(fast: bool = False) -> dict[str, object]:
    """Run the complete laboratory and return a JSON-serializable report."""
    if fast:
        side_lengths = (63, 127)
        gram_n, gram_k, gram_bands = 127, 10, (2, 4, 6, 8, 10)
        decay_n, decay_k, decay_start = 255, 32, 8
        boundary_ns = (63, 127)
        hp_band, hp_quad, hp_dps = 8, 48, 80
    else:
        side_lengths = (63, 127, 255)
        gram_n, gram_k, gram_bands = 255, 14, (2, 4, 6, 8, 10, 12, 14)
        decay_n, decay_k, decay_start = 511, 64, 16
        boundary_ns = (63, 127, 255)
        hp_band, hp_quad, hp_dps = 10, 64, 100
    return {
        "title": "OIG IX growing-band response Gramian laboratory",
        "status": (
            "exact finite identities plus reproducible floating-point evidence; "
            "not a proof of the full growing-band theorem"
        ),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
            "fast_mode": bool(fast),
        },
        "metric_calibration": {
            "source_L2": "orthonormal cosine coefficients",
            "source_Hs": "sum_k (1+mu_kh)^s |a_k|^2",
            "output_L2": "full target-density cosine norm",
            "output_Hminus_r": "sum_l (1+mu_lh)^(-r) |y_l|^2",
            "chart_normalizations": {
                "lattice": "n^-1/2",
                "resolved": "sqrt(epsilon)",
                "atomic_and_boundary": "t^(1/4)",
            },
        },
        "exact_and_symmetry_controls": exact_and_symmetry_controls(),
        "source_diffusion_cutoff": chart_bandwidth_audit(side_lengths),
        "weighted_gramians": gramian_growth_audit(
            gram_n, gram_k, gram_bands
        ),
        "multiplication_column_decay": multiplication_column_decay_audit(
            decay_n, decay_k, decay_start
        ),
        "boundary_endpoint_gain": boundary_endpoint_gain_audit(boundary_ns),
        "exact_continuum_kernel_audit": continuum_kernel_high_precision_audit(
            hp_band, 4, hp_quad, hp_dps
        ),
        "finite_sampling_rank_control": finite_sampling_rank_control(),
        "mixed_word_resolution_diagnostic": mixed_word_resolution_diagnostic(),
        "evidence_boundary": [
            "No floating numerical rank is promoted to an exact rank statement.",
            "No positive K-uniform lower frame bound is claimed.",
            "The cutoff collapse suggests delta_K=t mu_Kh as a sufficient small parameter; necessity in every weighted topology is not proved here.",
            "The ramp k^-2 column envelope is modulation-specific and does not classify rough or nonsmooth modulations.",
            "The laboratory belongs only to the declared parabolic toy model.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fast",
        action="store_true",
        help="run a smaller deterministic audit",
    )
    args = parser.parse_args()
    json.dump(run_lab(args.fast), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
