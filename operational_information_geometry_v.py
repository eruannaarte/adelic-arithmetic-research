#!/usr/bin/env python3
"""Stage V: continuum scaling and operational scale flow.

Finite path factors are placed at cell centers of the unit interval.  Their
combinatorial Laplacians are rescaled by ``n**2``; interventions and marginal
outputs are normalized as probability-density perturbations; graph distance is
divided by ``n``.  The resulting laboratory audits spectral convergence,
noncommuting dimension limits, directed-response convergence, parity selection
in the first causal jet, and the continuum failure of the raw uniformization
jump-count cone.
"""

from __future__ import annotations

import argparse
import json
import math
from typing import Sequence

import numpy as np
from scipy.linalg import expm
from scipy.sparse import csr_matrix, diags, eye, kron
from scipy.sparse.linalg import expm_multiply
from scipy.stats import poisson

from operational_information_geometry_ii import mixture_tangent_basis


def path_laplacian(side_length: int, sparse: bool = False) -> np.ndarray | csr_matrix:
    """Return the combinatorial Laplacian of the n-vertex path."""
    if side_length < 2:
        raise ValueError("side_length must be at least two")
    diagonal = np.concatenate(
        ([1.0], np.full(side_length - 2, 2.0), [1.0])
    )
    if sparse:
        return diags(
            [-np.ones(side_length - 1), diagonal, -np.ones(side_length - 1)],
            [-1, 0, 1],
            format="csr",
        )
    return (
        np.diag(diagonal)
        + np.diag(-np.ones(side_length - 1), 1)
        + np.diag(-np.ones(side_length - 1), -1)
    )


def cell_centers(side_length: int) -> np.ndarray:
    """Cell-centered coordinates on the unit interval."""
    if side_length < 2:
        raise ValueError("side_length must be at least two")
    return (np.arange(side_length, dtype=float) + 0.5) / side_length


def cosine_modes(
    side_length: int, mode_indices: Sequence[int]
) -> np.ndarray:
    """Return consistently oriented orthonormal Neumann path eigenmodes."""
    modes = np.asarray(mode_indices, dtype=int)
    if modes.ndim != 1 or np.any(modes < 0) or np.any(modes >= side_length):
        raise ValueError("mode indices must lie between zero and n-1")
    positions = np.arange(side_length, dtype=float) + 0.5
    columns = []
    for mode in modes:
        if mode == 0:
            columns.append(np.ones(side_length) / math.sqrt(side_length))
        else:
            columns.append(
                math.sqrt(2.0 / side_length)
                * np.cos(math.pi * mode * positions / side_length)
            )
    return np.column_stack(columns)


def scaled_path_eigenvalues(side_length: int) -> np.ndarray:
    """Exact eigenvalues of ``n**2`` times the n-path Laplacian."""
    modes = np.arange(side_length, dtype=float)
    return 4.0 * side_length**2 * np.sin(
        math.pi * modes / (2.0 * side_length)
    ) ** 2


def path_spectral_convergence_audit(
    side_lengths: Sequence[int] = (6, 8, 12, 16, 24, 32, 48, 64),
    mode_count: int = 5,
) -> dict[str, object]:
    """Audit the exact O(n^-2) low-mode eigenvalue bound."""
    if mode_count < 1 or any(side <= mode_count for side in side_lengths):
        raise ValueError("every path must contain all requested nonzero modes")
    continuum = (math.pi * np.arange(1, mode_count + 1)) ** 2
    rows = []
    for side_length in side_lengths:
        discrete = scaled_path_eigenvalues(side_length)[1 : mode_count + 1]
        errors = continuum - discrete
        bounds = (
            math.pi**4
            * np.arange(1, mode_count + 1, dtype=float) ** 4
            / (12.0 * side_length**2)
        )
        rows.append(
            {
                "side_length": int(side_length),
                "scaled_eigenvalues": discrete.tolist(),
                "maximum_absolute_error": float(np.max(errors)),
                "maximum_theorem_bound": float(np.max(bounds)),
                "maximum_bound_violation": float(np.max(errors - bounds)),
                "first_mode_relative_error": float(errors[0] / continuum[0]),
            }
        )
    return {
        "exact_formula": "mu_n,k = 4 n^2 sin^2(pi k/(2n))",
        "continuum_limit": "pi^2 k^2 (Neumann unit interval)",
        "proved_error_bound": (
            "0 <= pi^2 k^2 - mu_n,k <= pi^4 k^4/(12 n^2)"
        ),
        "mode_count": mode_count,
        "rows": rows,
    }


def transient_spectral_dimension(
    scaled_axis_eigenvalues: Sequence[float],
    factor_count: int,
    physical_time: float,
) -> float:
    """Stage-I-compatible spectral dimension with stationarity removed."""
    eigenvalues = np.asarray(scaled_axis_eigenvalues, dtype=float)
    if factor_count < 1 or physical_time <= 0.0 or len(eigenvalues) < 2:
        raise ValueError("need a nontrivial spectrum, factors, and positive time")
    weights = np.exp(-physical_time * eigenvalues)
    one_axis_trace = float(np.sum(weights))
    transient_trace = one_axis_trace**factor_count - 1.0
    if transient_trace <= 0.0:
        raise ArithmeticError("transient heat trace underflowed")
    energy_trace = (
        factor_count
        * float(eigenvalues @ weights)
        * one_axis_trace ** (factor_count - 1)
    )
    return 2.0 * physical_time * energy_trace / transient_trace


def continuum_transient_spectral_dimension(
    factor_count: int,
    physical_time: float,
    tolerance: float = 1e-16,
) -> float:
    """Evaluate the limiting Neumann heat-trace profile by a finite tail cut."""
    if factor_count < 1 or physical_time <= 0.0:
        raise ValueError("factor_count and physical_time must be positive")
    maximum_mode = max(
        8,
        int(
            math.ceil(
                math.sqrt(-math.log(tolerance) / (math.pi**2 * physical_time))
            )
        ),
    )
    values = (math.pi * np.arange(maximum_mode + 1, dtype=float)) ** 2
    return transient_spectral_dimension(values, factor_count, physical_time)


def spectral_dimension_scale_flow(
    side_lengths: Sequence[int] = (16, 32, 64, 128, 256, 512),
    factor_counts: Sequence[int] = (1, 2, 3),
    mesoscopic_exponent: float = 1.5,
) -> dict[str, object]:
    """Audit the window n^-2 << tau << 1 and noncommuting limits."""
    if not 0.0 < mesoscopic_exponent < 2.0:
        raise ValueError("mesoscopic_exponent must lie between zero and two")
    rows = []
    for side_length in side_lengths:
        physical_time = side_length ** (-mesoscopic_exponent)
        eigenvalues = scaled_path_eigenvalues(side_length)
        rows.append(
            {
                "side_length": int(side_length),
                "physical_time": float(physical_time),
                "lattice_separation_ratio_n2_tau": float(
                    side_length**2 * physical_time
                ),
                "dimension_estimates": {
                    str(factors): transient_spectral_dimension(
                        eigenvalues, factors, physical_time
                    )
                    for factors in factor_counts
                },
            }
        )

    fixed_side = 32
    small_times = (1e-4, 1e-5, 1e-6, 1e-7)
    fixed_eigenvalues = scaled_path_eigenvalues(fixed_side)
    finite_small_time = [
        {
            "physical_time": time,
            "three_factor_dimension": transient_spectral_dimension(
                fixed_eigenvalues, 3, time
            ),
        }
        for time in small_times
    ]
    fixed_physical_times = (0.002, 0.005, 0.01, 0.02)
    continuum_rows = []
    for time in fixed_physical_times:
        limiting = continuum_transient_spectral_dimension(3, time)
        continuum_rows.append(
            {
                "physical_time": time,
                "continuum_three_factor_dimension": limiting,
                "finite_side_estimates": {
                    str(side): transient_spectral_dimension(
                        scaled_path_eigenvalues(side), 3, time
                    )
                    for side in (16, 32, 64, 128)
                },
            }
        )
    return {
        "transient_trace": (
            "Theta_n,d(tau) = (sum_k exp(-tau mu_n,k))^d - 1"
        ),
        "mesoscopic_condition": "n^-2 << tau_n << 1",
        "mesoscopic_exponent": mesoscopic_exponent,
        "mesoscopic_rows": rows,
        "fixed_n_small_time_rows": finite_small_time,
        "fixed_time_continuum_rows": continuum_rows,
        "noncommuting_limits": (
            "fixed n then tau->0 gives dimension 0; taking n->infinity in "
            "the mesoscopic window and then tau->0 gives the factor count"
        ),
    }


def normalized_directed_response_history(
    side_length: int,
    observation_times: Sequence[float],
    source_mode_count: int = 5,
    target_mode: int = 1,
    interaction_strength: float = 0.8,
    background_amplitude: float = 0.4,
) -> np.ndarray:
    """Return the continuum-normalized A-to-B response on fixed cosine modes.

    The target background density is ``1 + a sqrt(2) cos(l pi y)``.  The
    returned row at each time is the coefficient of the normalized target mode
    generated by unit L2-density source-mode interventions.
    """
    if not 1 <= source_mode_count < side_length:
        raise ValueError("source_mode_count must lie between one and n-1")
    if not 1 <= target_mode < side_length:
        raise ValueError("target_mode must lie between one and n-1")
    if interaction_strength < 0.0:
        raise ValueError("interaction_strength must be nonnegative")
    if abs(background_amplitude) * math.sqrt(2.0) >= 1.0:
        raise ValueError("the declared target background must stay positive")
    times = np.asarray(observation_times, dtype=float)
    if times.ndim != 1 or len(times) == 0 or np.any(times < 0.0):
        raise ValueError("nonnegative observation times are required")

    laplacian = np.asarray(path_laplacian(side_length), dtype=float)
    positions = cell_centers(side_length)
    target_rate = scaled_path_eigenvalues(side_length)[target_mode]
    reduced_generator = (
        side_length**2 * laplacian
        + target_rate
        * np.diag(1.0 + interaction_strength * positions)
    )
    source_modes = cosine_modes(
        side_length, range(1, source_mode_count + 1)
    )
    ones = np.ones(side_length)
    return np.asarray(
        [
            background_amplitude
            / math.sqrt(side_length)
            * (ones @ expm(-float(time) * reduced_generator) @ source_modes)
            for time in times
        ]
    )


def continuum_first_response_derivative(
    source_mode_count: int,
    target_mode: int = 1,
    interaction_strength: float = 0.8,
    background_amplitude: float = 0.4,
) -> np.ndarray:
    """Exact continuum first-jet parity selection rule."""
    values = []
    for mode in range(1, source_mode_count + 1):
        if mode % 2 == 0:
            values.append(0.0)
        else:
            values.append(
                2.0
                * math.sqrt(2.0)
                * background_amplitude
                * interaction_strength
                * target_mode**2
                / mode**2
            )
    return np.asarray(values)


def discrete_first_response_derivative(
    side_length: int,
    source_mode_count: int = 5,
    target_mode: int = 1,
    interaction_strength: float = 0.8,
    background_amplitude: float = 0.4,
) -> np.ndarray:
    """Exact first derivative of the finite normalized response."""
    positions = cell_centers(side_length)
    modes = cosine_modes(side_length, range(1, source_mode_count + 1))
    target_rate = scaled_path_eigenvalues(side_length)[target_mode]
    return (
        -background_amplitude
        * interaction_strength
        * target_rate
        / math.sqrt(side_length)
        * (np.ones(side_length) @ np.diag(positions) @ modes)
    )


def directed_response_scale_flow(
    side_lengths: Sequence[int] = (6, 8, 12, 16, 24, 32, 48, 64, 96, 128),
    source_mode_count: int = 5,
    reference_side_length: int = 512,
) -> dict[str, object]:
    """Audit convergence of density-normalized directed response Gramians."""
    times = np.geomspace(0.001, 0.5, 30)
    reference_history = normalized_directed_response_history(
        reference_side_length, times, source_mode_count
    )
    reference_gram = reference_history.T @ reference_history
    continuum_derivative = continuum_first_response_derivative(source_mode_count)
    rows = []
    for side_length in side_lengths:
        history = normalized_directed_response_history(
            side_length, times, source_mode_count
        )
        gram = history.T @ history
        singular_values = np.linalg.svd(history, compute_uv=False)
        derivative = discrete_first_response_derivative(
            side_length, source_mode_count
        )
        rows.append(
            {
                "side_length": int(side_length),
                "response_frobenius_norm": float(
                    np.linalg.norm(history, ord="fro")
                ),
                "relative_gram_error_against_reference": float(
                    np.linalg.norm(gram - reference_gram, ord="fro")
                    / np.linalg.norm(reference_gram, ord="fro")
                ),
                "response_singular_values": singular_values.tolist(),
                "response_condition_number": float(
                    singular_values[0] / singular_values[-1]
                ),
                "first_derivative": derivative.tolist(),
                "maximum_first_derivative_limit_error": float(
                    np.max(np.abs(derivative - continuum_derivative))
                ),
                "even_mode_first_derivative_maximum": float(
                    np.max(np.abs(derivative[1::2]))
                ),
            }
        )
    return {
        "normalization": {
            "generator": "n^2 L_n",
            "source_probability_injection": "n^-1/2 times L2 cosine mode",
            "target_density_observation": "n^1/2 times probability marginal",
            "target_background_density": "1 + 0.4 sqrt(2) cos(pi y)",
        },
        "observation_times": times.tolist(),
        "source_mode_count": source_mode_count,
        "reference_side_length": reference_side_length,
        "continuum_first_derivative": continuum_derivative.tolist(),
        "selection_rule": (
            "the first causal derivative vanishes on every even source cosine "
            "mode and equals 2 sqrt(2) a g l^2/k^2 on odd modes"
        ),
        "rows": rows,
    }


def sparse_scaled_one_way_generator(
    side_length: int, interaction_strength: float = 0.8
) -> csr_matrix:
    """Sparse n^2-scaled two-dimensional one-way Markov generator."""
    if interaction_strength < 0.0:
        raise ValueError("interaction_strength must be nonnegative")
    laplacian = path_laplacian(side_length, sparse=True)
    identity = eye(side_length, format="csr")
    modulation = diags(cell_centers(side_length), format="csr")
    return side_length**2 * (
        kron(laplacian, identity, format="csr")
        + kron(identity + interaction_strength * modulation, laplacian, format="csr")
    )


def _effective_radius(
    distribution: np.ndarray,
    distances: np.ndarray,
    leakage_tolerance: float,
) -> int:
    maximum_distance = int(np.max(distances))
    for radius in range(maximum_distance + 1):
        if float(np.sum(distribution[distances > radius])) <= leakage_tolerance:
            return radius
    return maximum_distance


def causal_cone_scale_flow(
    side_lengths: Sequence[int] = (16, 24, 32, 48, 64, 96),
    physical_times: Sequence[float] = (0.001, 0.002, 0.005, 0.01),
    interaction_strength: float = 0.8,
    leakage_tolerance: float = 0.01,
) -> dict[str, object]:
    """Track actual physical radii and the raw Poisson jump-count envelope."""
    if not 0.0 < leakage_tolerance < 1.0:
        raise ValueError("leakage_tolerance must lie between zero and one")
    rows = []
    for side_length in side_lengths:
        generator = sparse_scaled_one_way_generator(
            side_length, interaction_strength
        )
        source_left = side_length // 2
        source_right = side_length // 2
        source = source_left * side_length + source_right
        initial = np.zeros(side_length**2)
        initial[source] = 1.0
        left = np.arange(side_length)[:, None]
        right = np.arange(side_length)[None, :]
        graph_distances = (
            np.abs(left - source_left) + np.abs(right - source_right)
        ).ravel()
        eccentricity = int(np.max(graph_distances))
        uniformization_rate = float(np.max(generator.diagonal()))
        for time in physical_times:
            distribution = np.asarray(
                expm_multiply(-float(time) * generator, initial)
            )
            distribution = np.maximum(distribution, 0.0)
            distribution /= np.sum(distribution)
            actual_radius = _effective_radius(
                distribution, graph_distances, leakage_tolerance
            )
            poisson_radius = int(
                poisson.ppf(1.0 - leakage_tolerance, uniformization_rate * time)
            )
            rows.append(
                {
                    "side_length": int(side_length),
                    "physical_time": float(time),
                    "actual_graph_radius": actual_radius,
                    "actual_physical_radius": actual_radius / side_length,
                    "poisson_graph_radius": poisson_radius,
                    "poisson_physical_radius": poisson_radius / side_length,
                    "graph_eccentricity": eccentricity,
                    "graph_physical_eccentricity": eccentricity / side_length,
                    "poisson_bound_is_domain_trivial": bool(
                        poisson_radius >= eccentricity
                    ),
                    "mass_error": float(abs(np.sum(distribution) - 1.0)),
                }
            )
    rate_ratios = []
    for side_length in side_lengths:
        generator = sparse_scaled_one_way_generator(
            side_length, interaction_strength
        )
        rate_ratios.append(
            {
                "side_length": int(side_length),
                "uniformization_rate_over_n_squared": float(
                    np.max(generator.diagonal()) / side_length**2
                ),
            }
        )
    return {
        "distance_normalization": "physical L1 distance = graph distance / n",
        "leakage_tolerance": leakage_tolerance,
        "rows": rows,
        "rate_scaling": rate_ratios,
        "proved_asymptotic_boundary": (
            "Lambda_n is asymptotic to (4+2g)n^2, so the raw Poisson "
            "99-percent radius divided by n grows like (4+2g)n tau and "
            "eventually exceeds the O(1) domain eccentricity at every fixed "
            "positive physical time"
        ),
        "interpretation": (
            "the actual leakage radius has a diffusive continuum scale, but "
            "the Stage-IV jump-count envelope becomes domain-trivial; a "
            "displacement-sensitive heat-kernel bound is required"
        ),
    }


def fixed_generator_amplitude_linearity_audit() -> dict[str, object]:
    """Show that initial-state interventions have no nonlinear amplitude jet."""
    side_length = 16
    times = np.geomspace(0.001, 0.5, 20)
    unit_history = normalized_directed_response_history(side_length, times, 3)
    amplitudes = (-2.0, -1.0, 0.0, 1.0, 2.0)
    histories = {amplitude: amplitude * unit_history for amplitude in amplitudes}
    second_difference = histories[1.0] - 2.0 * histories[0.0] + histories[-1.0]
    return {
        "maximum_second_amplitude_difference": float(
            np.max(np.abs(second_difference))
        ),
        "exact_statement": (
            "for fixed linear L, M exp(-tL)(p0 + epsilon J u) is affine in "
            "epsilon, so every amplitude derivative of order at least two is zero"
        ),
        "required_extension": (
            "nonlinear causal curvature requires intervention-dependent or "
            "state-dependent generators, not only larger initial perturbations"
        ),
    }


def modulation_symmetry_audit(
    side_length: int = 6,
    interaction_strength: float = 0.8,
) -> dict[str, object]:
    """Exhibit response-rank loss caused by an unbroken source symmetry.

    Reflection-symmetric modulation commutes with the path reflection.  Since
    the target marginal is reflection-invariant, every reflection-odd source
    intervention is then invisible for every observation time.
    """
    if side_length < 4 or side_length % 2:
        raise ValueError("the audit uses an even side length of at least four")
    laplacian = np.asarray(path_laplacian(side_length), dtype=float)
    identity = np.eye(side_length)
    tangent = mixture_tangent_basis(side_length)
    target_background = identity[:, 0, None]
    source_intervention = np.kron(tangent, target_background)
    target_marginal = np.kron(np.ones((1, side_length)), identity)
    times = np.geomspace(0.01, 2.0, 20)

    half = np.linspace(0.0, 1.0, side_length // 2)
    symmetric_profile = np.concatenate([half, half[::-1]])
    linear_profile = np.linspace(0.0, 1.0, side_length)
    reflection = np.fliplr(identity)
    odd_basis = np.column_stack(
        [
            (identity[:, index] - identity[:, side_length - 1 - index])
            / math.sqrt(2.0)
            for index in range(side_length // 2)
        ]
    )

    def history(profile: np.ndarray, intervention: np.ndarray) -> np.ndarray:
        generator = (
            np.kron(laplacian, identity)
            + np.kron(identity, laplacian)
            + interaction_strength * np.kron(np.diag(profile), laplacian)
        )
        return np.vstack(
            [
                target_marginal
                @ expm(-float(time) * generator)
                @ intervention
                for time in times
            ]
        )

    symmetric_history = history(symmetric_profile, source_intervention)
    linear_history = history(linear_profile, source_intervention)
    odd_history = history(
        symmetric_profile, np.kron(odd_basis, target_background)
    )
    symmetric_singular = np.linalg.svd(symmetric_history, compute_uv=False)
    linear_singular = np.linalg.svd(linear_history, compute_uv=False)
    threshold = 1e-11
    exact_rank_witness: dict[str, object] | None = None
    if side_length == 6 and interaction_strength == 0.8:
        # For g=4/5 and d=(0,1/2,1,1,1/2,0), five times the
        # generator is integral.  In difference coordinates E=(e_i-e_5), the
        # selected order-one/order-two minor of the scaled jet is exactly 32.
        # Undoing one factor 5 from order one and two factors from order two
        # gives the nonzero rational determinant 32/125.
        integer_laplacian = np.asarray(laplacian, dtype=np.int64)
        integer_profile = np.asarray([0, 2, 4, 4, 2, 0], dtype=np.int64)
        scaled_generator = (
            5 * np.kron(integer_laplacian, np.eye(6, dtype=np.int64))
            + 5 * np.kron(np.eye(6, dtype=np.int64), integer_laplacian)
            + np.kron(np.diag(integer_profile), integer_laplacian)
        )
        difference_basis = np.zeros((6, 5), dtype=np.int64)
        difference_basis[:5, :] = np.eye(5, dtype=np.int64)
        difference_basis[5, :] = -1
        integer_point = np.zeros((6, 1), dtype=np.int64)
        integer_point[0, 0] = 1
        integer_intervention = np.kron(difference_basis, integer_point)
        integer_marginal = np.kron(
            np.ones((1, 6), dtype=np.int64), np.eye(6, dtype=np.int64)
        )
        order_one = integer_marginal @ scaled_generator @ integer_intervention
        order_two = (
            integer_marginal
            @ scaled_generator
            @ scaled_generator
            @ integer_intervention
        )
        selected = np.asarray(
            [order_one[0, [1, 2]], order_two[0, [1, 2]]], dtype=np.int64
        )
        scaled_determinant = int(
            selected[0, 0] * selected[1, 1]
            - selected[0, 1] * selected[1, 0]
        )
        exact_rank_witness = {
            "scaled_integer_minor_determinant": scaled_determinant,
            "unscaled_minor_determinant": f"{scaled_determinant}/125",
            "jet_orders": [1, 2],
            "stacked_row_indices_zero_based": [0, 6],
            "difference_basis_columns_zero_based": [1, 2],
        }

    return {
        "symmetric_profile": symmetric_profile.tolist(),
        "linear_profile": linear_profile.tolist(),
        "symmetric_response_singular_values": symmetric_singular.tolist(),
        "symmetric_response_rank": int(np.sum(symmetric_singular > threshold)),
        "linear_response_rank": int(np.sum(linear_singular > threshold)),
        "reflection_odd_tangent_dimension": side_length // 2,
        "maximum_reflection_odd_response": float(np.max(np.abs(odd_history))),
        "exact_rank_lower_witness": exact_rank_witness,
        "generator_reflection_commutator_norm": float(
            np.linalg.norm(reflection @ laplacian - laplacian @ reflection)
        ),
        "modulation_reflection_commutator_norm": float(
            np.linalg.norm(
                reflection @ np.diag(symmetric_profile)
                - np.diag(symmetric_profile) @ reflection
            )
        ),
        "theorem": (
            "if a source symmetry commutes with both L_A and D_A while the "
            "target marginal is symmetry-invariant, its nontrivial source "
            "representations are all-time invisible"
        ),
        "interpretation": (
            "one-way response does not imply source identifiability; symmetry "
            "breaking or an explicit cyclicity condition is required"
        ),
    }


def equilibrium_path_sensor_audit(
    side_length: int = 6,
    interaction_strength: float = 0.8,
) -> dict[str, object]:
    """Show that a path-activity sensor survives endpoint-marginal silence.

    The source intervention is tensorized with the uniform stationary target
    profile.  Target endpoint marginals are then exactly silent, but the target
    jump intensity records the source-dependent clock speed.
    """
    if side_length < 2:
        raise ValueError("side_length must be at least two")
    if interaction_strength < 0.0:
        raise ValueError("interaction_strength must be nonnegative")
    laplacian = np.asarray(path_laplacian(side_length), dtype=float)
    identity = np.eye(side_length)
    profile = cell_centers(side_length)
    tangent = mixture_tangent_basis(side_length)
    stationary_target = np.ones((side_length, 1)) / side_length
    intervention = np.kron(tangent, stationary_target)
    target_marginal = np.kron(np.ones((1, side_length)), identity)
    generator = (
        np.kron(laplacian, identity)
        + np.kron(identity, laplacian)
        + interaction_strength * np.kron(np.diag(profile), laplacian)
    )
    target_degrees = np.diag(laplacian)
    joint_jump_intensity = np.kron(
        1.0 + interaction_strength * profile, target_degrees
    )[None, :]
    mean_target_degree = float(np.mean(target_degrees))
    times = np.geomspace(0.01, 2.0, 20)
    endpoint_history = np.vstack(
        [
            target_marginal @ expm(-float(time) * generator) @ intervention
            for time in times
        ]
    )
    full_count_rate_history = np.vstack(
        [
            joint_jump_intensity
            @ expm(-float(time) * generator)
            @ intervention
            for time in times
        ]
    )
    reduced_count_rate_history = np.vstack(
        [
            interaction_strength
            * mean_target_degree
            * profile[None, :]
            @ expm(-float(time) * laplacian)
            @ tangent
            for time in times
        ]
    )
    singular_values = np.linalg.svd(
        full_count_rate_history, compute_uv=False
    )
    return {
        "endpoint_marginal_response_norm": float(
            np.linalg.norm(endpoint_history, ord="fro")
        ),
        "path_jump_rate_response_norm": float(
            np.linalg.norm(full_count_rate_history, ord="fro")
        ),
        "path_jump_rate_singular_values": singular_values.tolist(),
        "path_jump_rate_response_rank": int(np.sum(singular_values > 1e-11)),
        "modal_reduction_error": float(
            np.max(
                np.abs(full_count_rate_history - reduced_count_rate_history)
            )
        ),
        "exact_formula": (
            "delta r_B(t) = g * mean_degree(B) * d^T exp(-t L_A) h"
        ),
        "interpretation": (
            "stationary factorized target preparation is silent to endpoint "
            "marginals, not to trajectory observables such as jump activity"
        ),
    }


def conjugate_port_reciprocity_audit(
    side_length: int = 6,
    interaction_strength: float = 0.8,
) -> dict[str, object]:
    """Verify reciprocity for adjoint ports of a reversible propagator."""
    if side_length < 2:
        raise ValueError("side_length must be at least two")
    laplacian = np.asarray(path_laplacian(side_length), dtype=float)
    identity = np.eye(side_length)
    profile = cell_centers(side_length)
    generator = (
        np.kron(laplacian, identity)
        + np.kron(identity, laplacian)
        + interaction_strength * np.kron(np.diag(profile), laplacian)
    )
    tangent = mixture_tangent_basis(side_length)
    left_marginal = np.kron(identity, np.ones((1, side_length)))
    right_marginal = np.kron(np.ones((1, side_length)), identity)
    left_sensor = tangent.T @ left_marginal
    right_sensor = tangent.T @ right_marginal
    left_injection = left_sensor.T
    right_injection = right_sensor.T
    times = np.geomspace(0.01, 2.0, 20)
    maximum_error = 0.0
    response_norm = 0.0
    localized_forward_norm = 0.0
    localized_reverse_norm = 0.0
    point = identity[:, 0, None]
    localized_left_injection = np.kron(tangent, point)
    localized_right_injection = np.kron(point, tangent)
    for time in times:
        propagator = expm(-float(time) * generator)
        left_to_right = right_sensor @ propagator @ left_injection
        right_to_left = left_sensor @ propagator @ right_injection
        maximum_error = max(
            maximum_error,
            float(np.max(np.abs(left_to_right - right_to_left.T))),
        )
        response_norm += float(np.linalg.norm(left_to_right, ord="fro") ** 2)
        localized_forward_norm += float(
            np.linalg.norm(
                right_sensor @ propagator @ localized_left_injection,
                ord="fro",
            )
            ** 2
        )
        localized_reverse_norm += float(
            np.linalg.norm(
                left_sensor @ propagator @ localized_right_injection,
                ord="fro",
            )
            ** 2
        )
    return {
        "maximum_reciprocity_error": maximum_error,
        "stacked_cross_response_norm": math.sqrt(response_norm),
        "localized_forward_response_norm": math.sqrt(localized_forward_norm),
        "localized_reverse_response_norm": math.sqrt(localized_reverse_norm),
        "theorem": (
            "for symmetric K_t and adjoint ports J_A=C_A^T, J_B=C_B^T, "
            "C_B K_t J_A = (C_A K_t J_B)^T"
        ),
        "interpretation": (
            "the Stage-IV arrow uses localized nonconjugate preparations; "
            "reversible microscopic dynamics remains reciprocal at conjugate ports"
        ),
    }


def run_stage_5_experiment() -> dict[str, object]:
    """Run the complete continuum and scale-flow audit."""
    return {
        "model": (
            "cell-centered Neumann path products with continuum-normalized "
            "directed interventions"
        ),
        "scope": (
            "finite-difference and finite-mode continuum evidence; no claim "
            "about physical spacetime, relativistic propagation, or a "
            "fundamental information substrate"
        ),
        "renormalization_dictionary": {
            "coordinate": "x_j = (j+1/2)/n",
            "generator": "L_n -> n^2 L_n",
            "graph_time": "t_graph = n^2 tau",
            "probability_to_density_output": "M -> sqrt(n) M",
            "density_mode_to_probability_injection": "U -> U/sqrt(n)",
            "physical_graph_distance": "d_graph -> d_graph/n",
        },
        "path_spectral_convergence": path_spectral_convergence_audit(),
        "spectral_dimension_scale_flow": spectral_dimension_scale_flow(),
        "directed_response_scale_flow": directed_response_scale_flow(),
        "causal_cone_scale_flow": causal_cone_scale_flow(),
        "nonlinear_intervention_boundary": fixed_generator_amplitude_linearity_audit(),
        "modulation_symmetry_boundary": modulation_symmetry_audit(),
        "equilibrium_path_sensor": equilibrium_path_sensor_audit(),
        "conjugate_port_reciprocity": conjugate_port_reciprocity_audit(),
        "falsification_readout": {
            "unscaled_limit": (
                "holding the combinatorial generator and graph time fixed "
                "freezes low modes as n grows; n^2 scaling is necessary"
            ),
            "dimension_order_of_limits": (
                "finite-state ultraviolet dimension is zero; product dimension "
                "appears only after lattice separation"
            ),
            "response_normalization": (
                "unscaled delta backgrounds do not define a stable L2 continuum "
                "response, so a positive smooth target density is declared"
            ),
            "cone_failure": (
                "the exact Stage-IV Poisson bound remains true but becomes "
                "continuum-trivial"
            ),
            "nonlinearity_failure": (
                "larger initial perturbations cannot create second-order "
                "response while the generator stays linear and fixed"
            ),
            "identifiability_failure": (
                "a directed channel can retain an exact invisible source "
                "subspace when the modulation preserves a source symmetry"
            ),
            "stationary_protocol_boundary": (
                "stationary tensor-product target preparation hides the arrow "
                "from endpoint marginals but not from target path activity"
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    return argparse.ArgumentParser(description=__doc__).parse_args()


def main() -> None:
    parse_args()
    print(json.dumps(run_stage_5_experiment(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
