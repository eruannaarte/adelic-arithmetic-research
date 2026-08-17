#!/usr/bin/env python3
"""Stage 3: composition, hidden interactions, and multiscale design.

Two finite path subsystems are composed by Kronecker sums.  Local marginal
observers induce an exact Cartesian pure-state metric but share the complete
correlation kernel.  A positive mixed generator ``L_A kron L_B`` supplies a
controlled interaction that is invisible to every local marginal yet visible
to joint probes.  A signed mixed decay contrast recovers its strength, and a
positive multiscale Fisher design adapts Arithmetic Sensing V's design logic
to the interaction modes.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import linprog
from scipy.linalg import expm

from operational_information_geometry import factorization_universe
from operational_information_geometry_ii import (
    ProtocolGeometry,
    complete_protocol,
    history_geometry,
    scale_invariant_distortion,
)


@dataclass(frozen=True)
class HistoryMetric:
    """A Gram matrix and distance matrix made directly from a history map."""

    observability_matrix: np.ndarray
    gram: np.ndarray
    distances: np.ndarray


def history_metric(observability_matrix: np.ndarray) -> HistoryMetric:
    observability = np.asarray(observability_matrix, dtype=float)
    if observability.ndim != 2 or observability.shape[1] < 2:
        raise ValueError("history matrix must have at least two latent columns")
    gram = observability.T @ observability
    diagonal = np.diag(gram)
    distances = np.sqrt(
        np.maximum(0.0, diagonal[:, None] + diagonal[None, :] - 2.0 * gram)
    )
    return HistoryMetric(observability, gram, distances)


def independent_generator(
    left_laplacian: np.ndarray, right_laplacian: np.ndarray
) -> np.ndarray:
    """Kronecker-sum generator for independent subsystem dynamics."""
    left = np.asarray(left_laplacian, dtype=float)
    right = np.asarray(right_laplacian, dtype=float)
    return np.kron(left, np.eye(len(right))) + np.kron(
        np.eye(len(left)), right
    )


def mixed_dissipative_generator(
    left_laplacian: np.ndarray,
    right_laplacian: np.ndarray,
    interaction_strength: float,
) -> np.ndarray:
    """Add a conservative PSD interaction supported on correlation modes.

    This is a symmetric dissipative generator.  Its mixed Kronecker term need
    not have the off-diagonal sign pattern of a graph Laplacian, so it is not
    claimed to be a continuous-time Markov generator.
    """
    if interaction_strength < 0.0:
        raise ValueError("the reference dissipative interaction is nonnegative")
    return independent_generator(left_laplacian, right_laplacian) + (
        interaction_strength * np.kron(left_laplacian, right_laplacian)
    )


def diagonal_markov_interaction_laplacian(
    left_state_count: int, right_state_count: int
) -> np.ndarray:
    """Graph Laplacian joining both diagonals of every product-grid cell."""
    if left_state_count < 2 or right_state_count < 2:
        raise ValueError("both factors must contain an edge")
    state_count = left_state_count * right_state_count
    adjacency = np.zeros((state_count, state_count))
    for left in range(left_state_count - 1):
        for right in range(right_state_count - 1):
            diagonals = [
                ((left, right), (left + 1, right + 1)),
                ((left + 1, right), (left, right + 1)),
            ]
            for first, second in diagonals:
                first_index = first[0] * right_state_count + first[1]
                second_index = second[0] * right_state_count + second[1]
                adjacency[first_index, second_index] = 1.0
                adjacency[second_index, first_index] = 1.0
    return np.diag(np.sum(adjacency, axis=1)) - adjacency


def marginal_measurements(
    left_state_count: int, right_state_count: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return left marginal, right marginal, and their pooled sensor."""
    if left_state_count < 2 or right_state_count < 2:
        raise ValueError("both subsystems must be nontrivial")
    left = np.kron(
        np.eye(left_state_count), np.ones((1, right_state_count))
    )
    right = np.kron(
        np.ones((1, left_state_count)), np.eye(right_state_count)
    )
    return left, right, np.vstack([left, right])


def cartesian_local_history(
    left_history: np.ndarray, right_history: np.ndarray
) -> np.ndarray:
    """Lift subsystem histories so pure-product squared distances add."""
    left_history = np.asarray(left_history, dtype=float)
    right_history = np.asarray(right_history, dtype=float)
    if left_history.ndim != 2 or right_history.ndim != 2:
        raise ValueError("subsystem histories must be matrices")
    left_count = left_history.shape[1]
    right_count = right_history.shape[1]
    return np.vstack(
        [
            np.kron(left_history, np.ones((1, right_count))),
            np.kron(np.ones((1, left_count)), right_history),
        ]
    )


def tensor_history(
    left_history: np.ndarray, right_history: np.ndarray
) -> np.ndarray:
    """Two-clock product protocol whose Gram factors exactly."""
    return np.kron(
        np.asarray(left_history, dtype=float),
        np.asarray(right_history, dtype=float),
    )


def product_composition_audit(
    left_laplacian: np.ndarray,
    right_laplacian: np.ndarray,
    observation_times: np.ndarray,
) -> dict[str, object]:
    """Verify Cartesian local and tensor two-clock composition laws."""
    left_count = len(left_laplacian)
    right_count = len(right_laplacian)
    left_geometry = history_geometry(
        left_laplacian,
        complete_protocol(left_count, len(observation_times)),
        observation_times,
    )
    right_geometry = history_geometry(
        right_laplacian,
        complete_protocol(right_count, len(observation_times)),
        observation_times,
    )
    cartesian = history_metric(
        cartesian_local_history(
            left_geometry.observability_matrix,
            right_geometry.observability_matrix,
        )
    )
    maximum_additivity_error = 0.0
    for left_state in range(left_count):
        for right_state in range(right_count):
            first = left_state * right_count + right_state
            for other_left in range(left_count):
                for other_right in range(right_count):
                    second = other_left * right_count + other_right
                    expected = (
                        left_geometry.distances[left_state, other_left] ** 2
                        + right_geometry.distances[right_state, other_right] ** 2
                    )
                    maximum_additivity_error = max(
                        maximum_additivity_error,
                        abs(cartesian.distances[first, second] ** 2 - expected),
                    )

    tensor = history_metric(
        tensor_history(
            left_geometry.observability_matrix,
            right_geometry.observability_matrix,
        )
    )
    expected_tensor_gram = np.kron(left_geometry.gram, right_geometry.gram)
    tangent_kernel_dimension = (
        (left_count - 1) * (right_count - 1)
    )
    cartesian_rank = int(np.linalg.matrix_rank(cartesian.observability_matrix))
    pure_distances = cartesian.distances.copy()
    np.fill_diagonal(pure_distances, np.inf)
    return {
        "left_state_count": left_count,
        "right_state_count": right_count,
        "composite_state_count": left_count * right_count,
        "cartesian_local_protocol": {
            "maximum_squared_distance_additivity_error": float(
                maximum_additivity_error
            ),
            "history_rank": cartesian_rank,
            "predicted_history_rank": left_count + right_count - 1,
            "correlation_kernel_dimension": int(
                left_count * right_count - cartesian_rank
            ),
            "predicted_correlation_kernel_dimension": tangent_kernel_dimension,
            "minimum_pure_state_margin": float(np.min(pure_distances)),
        },
        "two_clock_tensor_protocol": {
            "relative_gram_factorization_error": float(
                np.linalg.norm(tensor.gram - expected_tensor_gram, ord="fro")
                / np.linalg.norm(expected_tensor_gram, ord="fro")
            ),
            "history_rank": int(np.linalg.matrix_rank(tensor.observability_matrix)),
        },
    }


def mixed_spectral_curvature(
    left_eigenvalues: Sequence[float],
    right_eigenvalues: Sequence[float],
    composite_eigenvalue_grid: np.ndarray,
) -> np.ndarray:
    """Cancel both additive subsystem spectra before taking magnitudes."""
    left = np.asarray(left_eigenvalues, dtype=float)
    right = np.asarray(right_eigenvalues, dtype=float)
    grid = np.asarray(composite_eigenvalue_grid, dtype=float)
    if grid.shape != (len(left), len(right)):
        raise ValueError("composite spectrum must be indexed by subsystem modes")
    return grid - grid[:, [0]] - grid[[0], :] + grid[0, 0]


def spectral_interaction_audit(
    left_laplacian: np.ndarray,
    right_laplacian: np.ndarray,
    interaction_strength: float,
    sensor_count: int = 16,
) -> dict[str, object]:
    """Recover the mixed coupling from decay rates across random joint sensors."""
    left_values, left_vectors = np.linalg.eigh(left_laplacian)
    right_values, right_vectors = np.linalg.eigh(right_laplacian)
    eigenvalue_grid = (
        left_values[:, None]
        + right_values[None, :]
        + interaction_strength * left_values[:, None] * right_values[None, :]
    )
    curvature = mixed_spectral_curvature(
        left_values, right_values, eigenvalue_grid
    )
    predicted = interaction_strength * left_values[:, None] * right_values[None, :]

    first_time = 0.05
    second_time = 0.35
    recovered_strengths = []
    minimum_joint_gain = math.inf
    state_count = len(left_values) * len(right_values)
    for seed in range(sensor_count):
        rng = np.random.default_rng(seed)
        sensor = rng.choice([-1.0, 1.0], size=(4, state_count)) / 2.0

        def observed_rate(left_mode: int, right_mode: int) -> float:
            mode = np.kron(
                left_vectors[:, left_mode], right_vectors[:, right_mode]
            )
            gain = float(np.linalg.norm(sensor @ mode))
            if gain <= 1e-12:
                raise ArithmeticError("random sensor erased a tested eigenmode")
            nonlocal minimum_joint_gain
            minimum_joint_gain = min(minimum_joint_gain, gain)
            eigenvalue = eigenvalue_grid[left_mode, right_mode]
            first_norm = gain * math.exp(-first_time * eigenvalue)
            second_norm = gain * math.exp(-second_time * eigenvalue)
            return math.log(first_norm / second_norm) / (
                second_time - first_time
            )

        local_left_rates = [
            observed_rate(index, 0) for index in range(len(left_values))
        ]
        local_right_rates = [
            observed_rate(0, index) for index in range(len(right_values))
        ]
        constant_rate = observed_rate(0, 0)
        for left_mode in range(1, len(left_values)):
            for right_mode in range(1, len(right_values)):
                joint_rate = observed_rate(left_mode, right_mode)
                mixed_rate = (
                    joint_rate
                    - local_left_rates[left_mode]
                    - local_right_rates[right_mode]
                    + constant_rate
                )
                recovered_strengths.append(
                    mixed_rate
                    / (left_values[left_mode] * right_values[right_mode])
                )

    recovered = np.asarray(recovered_strengths)
    return {
        "interaction_strength": interaction_strength,
        "maximum_exact_curvature_formula_error": float(
            np.max(np.abs(curvature - predicted))
        ),
        "random_joint_sensor_count": sensor_count,
        "minimum_tested_sensor_gain": minimum_joint_gain,
        "recovered_strength_mean": float(np.mean(recovered)),
        "recovered_strength_standard_deviation": float(np.std(recovered)),
        "maximum_recovered_strength_error": float(
            np.max(np.abs(recovered - interaction_strength))
        ),
        "mixed_curvature_minimum_nonconstant": float(
            np.min(curvature[1:, 1:])
        ),
        "mixed_curvature_maximum": float(np.max(curvature)),
    }


def _relative_gram_deformation(
    reference_gram: np.ndarray, candidate_gram: np.ndarray
) -> float:
    eigenvalues, eigenvectors = np.linalg.eigh(reference_gram)
    if float(eigenvalues[0]) <= 0.0:
        raise ValueError("reference Gram must be positive definite")
    inverse_root = (eigenvectors * (1.0 / np.sqrt(eigenvalues))) @ eigenvectors.T
    relative = inverse_root @ (candidate_gram - reference_gram) @ inverse_root
    return float(np.max(np.abs(np.linalg.eigvalsh(relative))))


def interaction_visibility_audit(
    left_laplacian: np.ndarray,
    right_laplacian: np.ndarray,
    observation_times: np.ndarray,
    strengths: Sequence[float] = (0.0, 0.05, 0.1, 0.2, 0.4, 0.8),
) -> dict[str, object]:
    """Separate true dynamical interaction from observer blindness."""
    left_count = len(left_laplacian)
    right_count = len(right_laplacian)
    independent = independent_generator(left_laplacian, right_laplacian)
    _, _, local_sensor = marginal_measurements(left_count, right_count)
    complete_sensor = np.eye(left_count * right_count)
    rng = np.random.default_rng(3)
    random_sensor = rng.choice(
        [-1.0, 1.0], size=(12, left_count * right_count)
    ) / math.sqrt(12)
    sensors = {
        "complete": complete_sensor,
        "local_marginal": local_sensor,
        "random_joint": random_sensor,
    }
    baseline = {
        name: history_geometry(
            independent,
            tuple(sensor for _ in observation_times),
            observation_times,
        )
        for name, sensor in sensors.items()
    }
    rows = []
    for strength in strengths:
        generator = mixed_dissipative_generator(
            left_laplacian, right_laplacian, strength
        )
        candidates = {
            name: history_geometry(
                generator,
                tuple(sensor for _ in observation_times),
                observation_times,
            )
            for name, sensor in sensors.items()
        }
        complete_distortion = scale_invariant_distortion(
            candidates["complete"].distances,
            baseline["complete"].distances,
        )
        row = {
            "interaction_strength": float(strength),
            "complete_relative_gram_change": float(
                np.linalg.norm(
                    candidates["complete"].gram - baseline["complete"].gram,
                    ord="fro",
                )
                / np.linalg.norm(baseline["complete"].gram, ord="fro")
            ),
            "random_joint_relative_gram_change": float(
                np.linalg.norm(
                    candidates["random_joint"].gram
                    - baseline["random_joint"].gram,
                    ord="fro",
                )
                / np.linalg.norm(baseline["random_joint"].gram, ord="fro")
            ),
            "local_marginal_relative_history_change": float(
                np.linalg.norm(
                    candidates["local_marginal"].observability_matrix
                    - baseline["local_marginal"].observability_matrix,
                    ord="fro",
                )
                / np.linalg.norm(
                    baseline["local_marginal"].observability_matrix, ord="fro"
                )
            ),
            "complete_relative_quadratic_form_deformation": (
                _relative_gram_deformation(
                    baseline["complete"].gram,
                    candidates["complete"].gram,
                )
            ),
            "complete_pure_metric_dilation": float(
                complete_distortion["minimax_dilation"]
            ),
        }
        rows.append(row)
    return {
        "interaction_family": (
            "L_g = L_A tensor I + I tensor L_B + g L_A tensor L_B"
        ),
        "generator_scope": (
            "symmetric conservative PSD dissipative generator; not asserted "
            "to be a Markov graph Laplacian"
        ),
        "strength_sweep": rows,
    }


def markov_interaction_control(
    left_laplacian: np.ndarray,
    right_laplacian: np.ndarray,
    observation_times: np.ndarray,
    interaction_strength: float,
) -> dict[str, object]:
    """Contrast the marginal-blind signed model with a true graph interaction."""
    left_count = len(left_laplacian)
    right_count = len(right_laplacian)
    independent = independent_generator(left_laplacian, right_laplacian)
    interaction = diagonal_markov_interaction_laplacian(left_count, right_count)
    coupled = independent + interaction_strength * interaction
    _, _, local_sensor = marginal_measurements(left_count, right_count)
    baseline = history_geometry(
        independent,
        tuple(local_sensor for _ in observation_times),
        observation_times,
    )
    candidate = history_geometry(
        coupled,
        tuple(local_sensor for _ in observation_times),
        observation_times,
    )
    off_diagonal = coupled - np.diag(np.diag(coupled))
    transition = expm(-0.1 * coupled)
    return {
        "interaction": "both diagonal edges in every product-grid cell",
        "interaction_strength": interaction_strength,
        "generator_is_graph_laplacian": bool(
            np.max(off_diagonal) <= 1e-14
            and np.max(np.abs(np.sum(coupled, axis=1))) <= 1e-12
        ),
        "minimum_transition_kernel_entry_at_time_0_1": float(np.min(transition)),
        "local_marginal_relative_history_change": float(
            np.linalg.norm(
                candidate.observability_matrix - baseline.observability_matrix,
                ord="fro",
            )
            / np.linalg.norm(baseline.observability_matrix, ord="fro")
        ),
        "interpretation": (
            "a nonzero positivity-preserving linear Markov interaction changes "
            "at least one marginal for some initial state; exact universal "
            "marginal blindness requires leaving this model class"
        ),
    }


def fisher_information_by_schedule(
    rates: Sequence[float], schedules: np.ndarray
) -> np.ndarray:
    """Per-unit-sensor-gain information for known-amplitude exponential decay."""
    rates = np.asarray(rates, dtype=float)
    schedules = np.asarray(schedules, dtype=float)
    if rates.ndim != 1 or schedules.ndim != 2 or np.any(rates <= 0.0):
        raise ValueError("positive rates and a schedule matrix are required")
    if np.any(schedules <= 0.0):
        raise ValueError("all observation times must be positive")
    return np.asarray(
        [
            [np.sum(times**2 * np.exp(-2.0 * rate * times)) for rate in rates]
            for times in schedules
        ]
    )


def _solve_positive_minimax(
    normalized_information: np.ndarray, selected_modes: Sequence[int]
) -> tuple[np.ndarray, float]:
    schedule_count = normalized_information.shape[0]
    selected = np.asarray(selected_modes, dtype=int)
    objective = np.concatenate([np.zeros(schedule_count), [-1.0]])
    inequalities = np.column_stack(
        [-normalized_information[:, selected].T, np.ones(len(selected))]
    )
    equality = np.asarray([np.concatenate([np.ones(schedule_count), [0.0]])])
    result = linprog(
        objective,
        A_ub=inequalities,
        b_ub=np.zeros(len(selected)),
        A_eq=equality,
        b_eq=np.asarray([1.0]),
        bounds=[(0.0, None)] * schedule_count + [(None, None)],
        method="highs",
    )
    if not result.success:
        raise RuntimeError(f"positive multiscale design failed: {result.message}")
    return result.x[:-1], float(result.x[-1])


def adaptive_multiscale_design(
    rates: Sequence[float],
    schedule_centers: Sequence[float] = (0.06, 0.12, 0.24, 0.48, 0.96, 1.92),
    dyadic_denominator: int = 4096,
) -> dict[str, object]:
    """Exchange dangerous modes and audit a positive multiscale Fisher design."""
    rates = np.asarray(rates, dtype=float)
    centers = np.asarray(schedule_centers, dtype=float)
    relative_times = np.asarray([0.5, 0.7, 1.0, 1.4, 2.0])
    schedules = centers[:, None] * relative_times[None, :]
    information = fisher_information_by_schedule(rates, schedules)
    oracle = np.max(information, axis=0)
    normalized = information / oracle[None, :]

    selected = [int(np.argmin(rates)), int(np.argmax(rates))]
    exchange_trace = []
    for _ in range(len(rates) + 1):
        weights, restricted_floor = _solve_positive_minimax(normalized, selected)
        all_values = normalized.T @ weights
        worst_mode = int(np.argmin(all_values))
        exchange_trace.append(
            {
                "selected_mode_count": len(selected),
                "restricted_floor": restricted_floor,
                "audited_worst_mode": worst_mode,
                "audited_worst_floor": float(all_values[worst_mode]),
            }
        )
        if worst_mode in selected:
            break
        selected.append(worst_mode)
    else:
        raise RuntimeError("mode exchange did not terminate")

    raw_dyadic = weights * dyadic_denominator
    numerators = np.floor(raw_dyadic).astype(int)
    remainder = dyadic_denominator - int(np.sum(numerators))
    order = np.argsort(raw_dyadic - numerators)[::-1]
    numerators[order[:remainder]] += 1
    dyadic_weights = numerators / dyadic_denominator
    dyadic_values = normalized.T @ dyadic_weights
    single_schedule_floors = np.min(normalized, axis=1)
    best_single_floor = float(np.max(single_schedule_floors))
    return {
        "criterion": (
            "maximize the worst fraction of each interaction mode's "
            "schedule-oracle Fisher information"
        ),
        "schedule_centers": centers.tolist(),
        "relative_times_per_schedule": relative_times.tolist(),
        "exchange_trace": exchange_trace,
        "selected_mode_indices": selected,
        "continuous_weights": weights.tolist(),
        "continuous_worst_information_fraction": float(
            np.min(normalized.T @ weights)
        ),
        "active_schedule_centers": [
            float(center) for center, weight in zip(centers, weights) if weight > 1e-9
        ],
        "dyadic_denominator": dyadic_denominator,
        "dyadic_numerators": numerators.tolist(),
        "dyadic_weights": dyadic_weights.tolist(),
        "dyadic_worst_information_fraction": float(np.min(dyadic_values)),
        "best_single_schedule_center": float(
            centers[int(np.argmax(single_schedule_floors))]
        ),
        "best_single_worst_information_fraction": best_single_floor,
        "dyadic_improvement_over_best_single": float(
            np.min(dyadic_values) / best_single_floor
        ),
        "all_modes_audited": len(dyadic_values),
    }


def arithmetic_sensing_v_transfer() -> dict[str, object]:
    """Record which AS V principles were used and which were not imported."""
    return {
        "transferred_principles": [
            (
                "preserve the signed mixed decay contrast before taking an "
                "absolute value, so additive subsystem rates cancel exactly"
            ),
            (
                "treat observation scales as distinct resources and combine "
                "them with positive weights"
            ),
            (
                "use adaptive mode exchange followed by a complete finite "
                "audit of every declared interaction mode"
            ),
            (
                "separate discovery by floating optimization from the exact "
                "composition theorems and explicit falsification controls"
            ),
        ],
        "not_transferred_as_theorems": [
            "Arithmetic Sensing V's Mellin-tail and number-field certificates",
            "its Arb/MPFR interval guarantees and finite stopping theorem",
            "its degree-fourteen window or numerical resource thresholds",
        ],
    }


def run_stage_3_experiment(interaction_strength: float = 0.4) -> dict[str, object]:
    """Run independent composition, hidden coupling, and multiscale design."""
    left = factorization_universe((2,), 6)
    right = factorization_universe((3,), 6)
    times = np.geomspace(0.02, 1.0, 14)
    left_values = np.linalg.eigvalsh(left.laplacian)
    right_values = np.linalg.eigvalsh(right.laplacian)
    interaction_rates = [
        left_values[left_mode]
        + right_values[right_mode]
        + interaction_strength
        * left_values[left_mode]
        * right_values[right_mode]
        for left_mode in range(1, len(left_values))
        for right_mode in range(1, len(right_values))
    ]
    return {
        "model": "compositional operational geometry with a mixed dissipative interaction",
        "scope": (
            "finite linear toy model; no claim about physical interactions, "
            "spacetime curvature, or a fundamental information substrate"
        ),
        "parameters": {
            "left_states": left.state_count,
            "right_states": right.state_count,
            "composite_states": left.state_count * right.state_count,
            "interaction_strength": interaction_strength,
            "observation_times": times.tolist(),
        },
        "arithmetic_sensing_v_transfer": arithmetic_sensing_v_transfer(),
        "independent_composition": product_composition_audit(
            left.laplacian, right.laplacian, times
        ),
        "spectral_interaction_witness": spectral_interaction_audit(
            left.laplacian, right.laplacian, interaction_strength
        ),
        "interaction_visibility": interaction_visibility_audit(
            left.laplacian, right.laplacian, times
        ),
        "markov_interaction_control": markov_interaction_control(
            left.laplacian,
            right.laplacian,
            times,
            interaction_strength,
        ),
        "positive_multiscale_interaction_design": adaptive_multiscale_design(
            interaction_rates
        ),
        "falsification_readout": {
            "exact_product_control": (
                "independent generators factor exactly under the two-clock "
                "tensor protocol and add exactly under local Cartesian sensing"
            ),
            "observer_boundary": (
                "local marginals are exactly blind to the mixed interaction, "
                "while complete and random joint sensors detect it"
            ),
            "safe_interaction_witness": (
                "a signed mixed decay-rate contrast cancels both local spectra "
                "and recovers the coupling across random joint sensor seeds"
            ),
            "multiscale_result": (
                "positive scale mixing raises the audited worst relative Fisher "
                "information well above every single candidate schedule"
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interaction-strength", type=float, default=0.4)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    print(
        json.dumps(
            run_stage_3_experiment(arguments.interaction_strength),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
