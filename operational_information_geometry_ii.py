#!/usr/bin/env python3
"""Stage 2: protocol invariance and stable mixture recovery.

This module compares operational geometries across sensor seeds, measurement
budgets, and time schedules.  It also constructs exact axis-blind protocols,
computes their common kernel, and tests an adjacent remedy for arbitrary-mixture
recovery: early observations with independently refreshed sensor channels.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.stats import spearmanr

from operational_information_geometry import (
    factorization_universe,
    stable_observable_subspaces,
)


@dataclass(frozen=True)
class ProtocolGeometry:
    """Observable-history geometry for fixed or time-varying sensors."""

    observation_times: np.ndarray
    measurement_matrices: tuple[np.ndarray, ...]
    observability_matrix: np.ndarray
    gram: np.ndarray
    distances: np.ndarray
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray


def history_geometry(
    laplacian: np.ndarray,
    measurement_matrices: Sequence[np.ndarray],
    observation_times: Sequence[float],
) -> ProtocolGeometry:
    """Construct history geometry when the sensor may change at every time."""
    laplacian = np.asarray(laplacian, dtype=float)
    times = np.asarray(observation_times, dtype=float)
    matrices = tuple(np.asarray(matrix, dtype=float) for matrix in measurement_matrices)
    state_count = len(laplacian)
    if laplacian.shape != (state_count, state_count):
        raise ValueError("laplacian must be square")
    if len(matrices) != len(times) or len(times) == 0 or np.any(times < 0.0):
        raise ValueError("one sensor matrix is required at every nonnegative time")
    if any(matrix.ndim != 2 or matrix.shape[1] != state_count for matrix in matrices):
        raise ValueError("every sensor matrix must act on the latent state space")

    eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
    blocks = []
    for matrix, time in zip(matrices, times):
        heat = (eigenvectors * np.exp(-time * eigenvalues)) @ eigenvectors.T
        blocks.append(matrix @ heat)
    observability = np.vstack(blocks)
    gram = observability.T @ observability
    diagonal = np.diag(gram)
    squared_distances = diagonal[:, None] + diagonal[None, :] - 2.0 * gram
    distances = np.sqrt(np.maximum(0.0, squared_distances))
    return ProtocolGeometry(
        times,
        matrices,
        observability,
        gram,
        distances,
        eigenvalues,
        eigenvectors,
    )


def rademacher_protocol(
    state_count: int,
    channel_count: int,
    time_count: int,
    seed: int,
    time_varying: bool,
) -> tuple[np.ndarray, ...]:
    """Generate repeated or independently refreshed normalized sign sensors."""
    if not 1 <= channel_count <= state_count or time_count < 1:
        raise ValueError("invalid protocol dimensions")
    rng = np.random.default_rng(seed)

    def sample() -> np.ndarray:
        return rng.choice(
            [-1.0, 1.0], size=(channel_count, state_count)
        ) / math.sqrt(channel_count)

    if time_varying:
        return tuple(sample() for _ in range(time_count))
    matrix = sample()
    return tuple(matrix for _ in range(time_count))


def complete_protocol(
    state_count: int, time_count: int
) -> tuple[np.ndarray, ...]:
    identity = np.eye(state_count)
    return tuple(identity for _ in range(time_count))


def axis_blind_measurements(
    coordinates: np.ndarray,
    channel_count: int,
    erased_axis: int,
    seed: int,
) -> np.ndarray:
    """Sensors constant along one factor and therefore blind to that factor."""
    coordinates = np.asarray(coordinates, dtype=int)
    if coordinates.ndim != 2 or not 0 <= erased_axis < coordinates.shape[1]:
        raise ValueError("invalid coordinates or erased axis")
    side_values = np.unique(coordinates[:, erased_axis])
    if not np.array_equal(side_values, np.arange(len(side_values))):
        raise ValueError("axis coordinates must be a contiguous zero-based range")
    reduced = np.delete(coordinates, erased_axis, axis=1)
    keys = [tuple(row) for row in reduced]
    classes = {key: index for index, key in enumerate(sorted(set(keys)))}
    rng = np.random.default_rng(seed)
    reduced_matrix = rng.choice(
        [-1.0, 1.0], size=(channel_count, len(classes))
    ) / math.sqrt(channel_count * len(side_values))
    return np.column_stack([reduced_matrix[:, classes[key]] for key in keys])


def scale_invariant_distortion(
    candidate_distances: np.ndarray, reference_distances: np.ndarray
) -> dict[str, float]:
    """Compare finite metrics after removing one global distance scale.

    The minimax dilation is ``K=max(ratio)/min(ratio)``.  After the optimal
    symmetric rescaling, every ratio lies in ``[1/sqrt(K), sqrt(K)]``.
    """
    if (
        candidate_distances.shape != reference_distances.shape
        or candidate_distances.ndim != 2
        or candidate_distances.shape[0] != candidate_distances.shape[1]
    ):
        raise ValueError("distance matrices must be equally sized and square")
    upper = np.triu_indices(len(candidate_distances), 1)
    candidate = candidate_distances[upper]
    reference = reference_distances[upper]
    if np.any(reference <= 0.0) or np.any(candidate <= 0.0):
        raise ValueError("all distinct reference and candidate distances must be positive")
    ratios = candidate / reference
    minimum_ratio = float(np.min(ratios))
    maximum_ratio = float(np.max(ratios))
    dilation = maximum_ratio / minimum_ratio
    minimax_scale = 1.0 / math.sqrt(minimum_ratio * maximum_ratio)
    log_scale = float(np.exp(-np.mean(np.log(ratios))))
    log_residuals = np.log(log_scale * ratios)
    return {
        "spearman": float(spearmanr(candidate, reference).statistic),
        "minimax_dilation": dilation,
        "optimal_symmetric_lower_factor": 1.0 / math.sqrt(dilation),
        "optimal_symmetric_upper_factor": math.sqrt(dilation),
        "minimax_global_scale": minimax_scale,
        "log_least_squares_global_scale": log_scale,
        "log_rms_distortion": float(np.sqrt(np.mean(log_residuals**2))),
    }


def mixture_tangent_basis(state_count: int) -> np.ndarray:
    """Return an orthonormal Helmert basis for vectors whose entries sum to zero."""
    if state_count < 2:
        raise ValueError("at least two states are required")
    basis = np.zeros((state_count, state_count - 1))
    for column in range(1, state_count):
        normalizer = math.sqrt(column * (column + 1))
        basis[:column, column - 1] = 1.0 / normalizer
        basis[column, column - 1] = -column / normalizer
    return basis


def mixture_stability(
    geometry: ProtocolGeometry,
    numerical_tolerance: float | None = None,
) -> dict[str, float | int | None]:
    """Condition the history map on the probability-simplex tangent space."""
    tangent = mixture_tangent_basis(len(geometry.distances))
    restricted = geometry.observability_matrix @ tangent
    singular_values = np.linalg.svd(restricted, compute_uv=False)
    if numerical_tolerance is None:
        numerical_tolerance = (
            max(restricted.shape)
            * np.finfo(float).eps
            * float(singular_values[0])
        )
    rank = int(np.count_nonzero(singular_values > numerical_tolerance))
    full_rank = rank == tangent.shape[1]
    if not full_rank:
        return {
            "tangent_dimension": int(tangent.shape[1]),
            "numerical_rank": rank,
            "smallest_singular_value": None,
            "condition_number": None,
            "gaussian_l2_rmse_amplification": None,
        }
    return {
        "tangent_dimension": int(tangent.shape[1]),
        "numerical_rank": rank,
        "smallest_singular_value": float(singular_values[-1]),
        "condition_number": float(singular_values[0] / singular_values[-1]),
        "gaussian_l2_rmse_amplification": float(
            np.sqrt(np.sum(1.0 / singular_values**2))
        ),
    }


def project_to_simplex(vector: Sequence[float]) -> np.ndarray:
    """Euclidean projection onto nonnegative vectors with unit sum."""
    vector = np.asarray(vector, dtype=float)
    if vector.ndim != 1 or len(vector) == 0:
        raise ValueError("simplex projection requires a nonempty vector")
    ordered = np.sort(vector)[::-1]
    cumulative = np.cumsum(ordered)
    candidates = ordered - (cumulative - 1.0) / np.arange(1, len(vector) + 1)
    positive = np.flatnonzero(candidates > 0.0)
    if len(positive) == 0:
        raise ArithmeticError("simplex projection threshold was not found")
    rho = int(positive[-1])
    threshold = (cumulative[rho] - 1.0) / (rho + 1)
    return np.maximum(vector - threshold, 0.0)


def affine_mixture_recovery(
    geometry: ProtocolGeometry, observations: np.ndarray
) -> np.ndarray:
    """Least-squares recovery under the affine unit-sum constraint."""
    state_count = len(geometry.distances)
    tangent = mixture_tangent_basis(state_count)
    center = np.full(state_count, 1.0 / state_count)
    restricted = geometry.observability_matrix @ tangent
    coefficients = np.linalg.lstsq(
        restricted,
        observations - geometry.observability_matrix @ center,
        rcond=None,
    )[0]
    return center + tangent @ coefficients


def _numeric_summary(values: Sequence[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    return {
        "mean": float(np.mean(array)),
        "standard_deviation": float(np.std(array)),
        "minimum": float(np.min(array)),
        "median": float(np.median(array)),
        "maximum": float(np.max(array)),
    }


def protocol_ensemble_audit(
    laplacian: np.ndarray,
    observation_times: np.ndarray,
    channel_count: int,
    protocol_count: int,
    time_varying: bool,
) -> dict[str, object]:
    """Compare seeded random protocols with complete observation and each other."""
    state_count = len(laplacian)
    complete = history_geometry(
        laplacian,
        complete_protocol(state_count, len(observation_times)),
        observation_times,
    )
    distortions = []
    stabilities = []
    candidate_distances = []
    for seed in range(protocol_count):
        geometry = history_geometry(
            laplacian,
            rademacher_protocol(
                state_count,
                channel_count,
                len(observation_times),
                seed,
                time_varying,
            ),
            observation_times,
        )
        distortions.append(
            scale_invariant_distortion(geometry.distances, complete.distances)
        )
        stabilities.append(mixture_stability(geometry))
        candidate_distances.append(geometry.distances)

    pair_distortions = [
        scale_invariant_distortion(
            candidate_distances[index], candidate_distances[index + 1]
        )
        for index in range(0, protocol_count - 1, 2)
    ]
    full_rank = [
        stability
        for stability in stabilities
        if stability["numerical_rank"] == stability["tangent_dimension"]
    ]
    return {
        "channel_count": channel_count,
        "protocol_count": protocol_count,
        "sensor_refresh": "independent_at_each_time"
        if time_varying
        else "same_matrix_at_every_time",
        "against_complete_observation": {
            "spearman": _numeric_summary([item["spearman"] for item in distortions]),
            "minimax_dilation": _numeric_summary(
                [item["minimax_dilation"] for item in distortions]
            ),
            "log_rms_distortion": _numeric_summary(
                [item["log_rms_distortion"] for item in distortions]
            ),
        },
        "seeded_protocol_pairs": {
            "pair_count": len(pair_distortions),
            "spearman": _numeric_summary(
                [item["spearman"] for item in pair_distortions]
            ),
            "minimax_dilation": _numeric_summary(
                [item["minimax_dilation"] for item in pair_distortions]
            ),
        },
        "mixture_tangent": {
            "full_numerical_rank_fraction": len(full_rank) / protocol_count,
            "numerical_rank": _numeric_summary(
                [float(item["numerical_rank"]) for item in stabilities]
            ),
            "full_rank_condition_number": _numeric_summary(
                [float(item["condition_number"]) for item in full_rank]
            )
            if full_rank
            else None,
            "full_rank_smallest_singular_value": _numeric_summary(
                [float(item["smallest_singular_value"]) for item in full_rank]
            )
            if full_rank
            else None,
        },
    }


def _geometry_from_observability(
    observability: np.ndarray,
    template: ProtocolGeometry,
) -> ProtocolGeometry:
    gram = observability.T @ observability
    diagonal = np.diag(gram)
    distances = np.sqrt(
        np.maximum(0.0, diagonal[:, None] + diagonal[None, :] - 2.0 * gram)
    )
    return ProtocolGeometry(
        template.observation_times,
        tuple(),
        observability,
        gram,
        distances,
        template.eigenvalues,
        template.eigenvectors,
    )


def axis_blind_audit(
    coordinates: np.ndarray,
    laplacian: np.ndarray,
    observation_times: np.ndarray,
    channel_count: int = 32,
) -> dict[str, object]:
    """Erase each factor exactly, then characterize the common blind subspace."""
    state_count, factor_count = coordinates.shape
    geometries = []
    per_axis = []
    for axis in range(factor_count):
        matrix = axis_blind_measurements(
            coordinates, channel_count, axis, seed=100 + axis
        )
        geometry = history_geometry(
            laplacian,
            tuple(matrix for _ in observation_times),
            observation_times,
        )
        geometries.append(geometry)
        reduced = np.delete(coordinates, axis, axis=1)
        within_fiber = []
        for left in range(state_count):
            for right in range(left + 1, state_count):
                if np.array_equal(reduced[left], reduced[right]):
                    within_fiber.append(
                        np.linalg.norm(
                            geometry.observability_matrix[:, left]
                            - geometry.observability_matrix[:, right]
                        )
                    )
        subspaces = stable_observable_subspaces(geometry)
        per_axis.append(
            {
                "erased_axis": axis,
                "history_rank": int(
                    np.linalg.matrix_rank(geometry.observability_matrix)
                ),
                "maximum_within_fiber_signature_distance": float(
                    np.max(within_fiber)
                ),
                "physicalized_slow_dimension": int(
                    sum(item["physicalized_dimension"] for item in subspaces)
                ),
            }
        )

    aggregate_observability = np.vstack(
        [geometry.observability_matrix for geometry in geometries]
    )
    aggregate = _geometry_from_observability(aggregate_observability, geometries[0])
    pure_distances = aggregate.distances.copy()
    np.fill_diagonal(pure_distances, np.inf)
    tangent_stability = mixture_stability(aggregate)

    side_length = len(np.unique(coordinates[:, 0]))
    expected_common_kernel = (side_length - 1) ** factor_count
    contrast = np.asarray(
        [1.0, -1.0] + [0.0] * (side_length - 2), dtype=float
    )
    hidden_interaction = np.prod(contrast[coordinates], axis=1)
    center = np.full(state_count, 1.0 / state_count)
    collision_amplitude = 0.5 / state_count
    mixture_plus = center + collision_amplitude * hidden_interaction
    mixture_minus = center - collision_amplitude * hidden_interaction
    collision_gap = np.linalg.norm(
        aggregate_observability @ (mixture_plus - mixture_minus)
    )

    return {
        "per_axis": per_axis,
        "combined_axis_blind_protocols": {
            "history_rank": int(np.linalg.matrix_rank(aggregate_observability)),
            "expected_history_rank": state_count - expected_common_kernel,
            "pure_state_minimum_margin": float(np.min(pure_distances)),
            "mixture_tangent_rank": int(tangent_stability["numerical_rank"]),
            "mixture_tangent_kernel_dimension": int(
                tangent_stability["tangent_dimension"]
                - tangent_stability["numerical_rank"]
            ),
            "expected_common_kernel_dimension": expected_common_kernel,
            "explicit_collision_l2_separation": float(
                np.linalg.norm(mixture_plus - mixture_minus)
            ),
            "explicit_collision_signature_gap": float(collision_gap),
            "collision_mixtures_are_nonnegative": bool(
                np.all(mixture_plus >= 0.0) and np.all(mixture_minus >= 0.0)
            ),
        },
    }


def mixture_recovery_audit(
    laplacian: np.ndarray,
    protocol_count: int = 200,
    noise_standard_deviation: float = 0.01,
    seed: int = 20_260_813,
) -> dict[str, object]:
    """Compare Stage 1 with early fixed and early refreshed observations."""
    state_count = len(laplacian)
    schedules = {
        "stage_1_late_repeated": (np.geomspace(1.0, 8.0, 14), False),
        "early_repeated": (np.geomspace(0.02, 1.0, 14), False),
        "early_refreshed": (np.geomspace(0.02, 1.0, 14), True),
    }
    geometries = {
        name: history_geometry(
            laplacian,
            rademacher_protocol(
                state_count, 32, len(times), seed, time_varying
            ),
            times,
        )
        for name, (times, time_varying) in schedules.items()
    }
    rng = np.random.default_rng(77_031)
    mixtures = rng.dirichlet(np.ones(state_count), size=protocol_count)
    noises = rng.normal(
        0.0,
        noise_standard_deviation,
        size=(protocol_count, 32 * 14),
    )
    report: dict[str, object] = {}
    for name, geometry in geometries.items():
        affine_errors = []
        projected_errors = []
        for mixture, noise in zip(mixtures, noises):
            observations = geometry.observability_matrix @ mixture + noise
            affine = affine_mixture_recovery(geometry, observations)
            projected = project_to_simplex(affine)
            affine_errors.append(float(np.linalg.norm(affine - mixture)))
            projected_errors.append(float(np.linalg.norm(projected - mixture)))
        stability = mixture_stability(geometry)
        predicted_rmse = (
            noise_standard_deviation
            * float(stability["gaussian_l2_rmse_amplification"])
            if stability["gaussian_l2_rmse_amplification"] is not None
            else None
        )
        report[name] = {
            "stability": stability,
            "predicted_affine_gaussian_l2_rmse": predicted_rmse,
            "simulated_affine_l2_rmse": float(
                np.sqrt(np.mean(np.asarray(affine_errors) ** 2))
            ),
            "simulated_simplex_projected_l2_rmse": float(
                np.sqrt(np.mean(np.asarray(projected_errors) ** 2))
            ),
        }
    return {
        "noise_standard_deviation_per_history_coordinate": noise_standard_deviation,
        "dense_dirichlet_mixture_trials": protocol_count,
        "protocols": report,
    }


def run_stage_2_experiment(protocol_count: int = 16) -> dict[str, object]:
    """Run the complete protocol-invariance and adjacent recovery audit."""
    if protocol_count < 2:
        raise ValueError("at least two protocols are required")
    universe = factorization_universe()
    schedules = {
        "early": np.geomspace(0.02, 1.0, 14),
        "broad": np.geomspace(0.02, 8.0, 14),
        "stage_1": np.geomspace(1.0, 8.0, 14),
        "late": np.geomspace(2.0, 16.0, 14),
    }

    complete_geometries = {
        name: history_geometry(
            universe.laplacian,
            complete_protocol(universe.state_count, len(times)),
            times,
        )
        for name, times in schedules.items()
    }
    schedule_comparisons = {}
    for left, right in itertools.combinations(schedules, 2):
        schedule_comparisons[f"{left}_vs_{right}"] = scale_invariant_distortion(
            complete_geometries[left].distances,
            complete_geometries[right].distances,
        )

    ensembles = {}
    for schedule_name in ["early", "stage_1"]:
        for refreshed in [False, True]:
            refresh_name = "refreshed" if refreshed else "repeated"
            for channel_count in [8, 16, 32, 64]:
                key = f"{schedule_name}_{refresh_name}_q{channel_count}"
                ensembles[key] = protocol_ensemble_audit(
                    universe.laplacian,
                    schedules[schedule_name],
                    channel_count,
                    protocol_count,
                    refreshed,
                )

    return {
        "model": "protocol invariance and mixture stability on the factorization universe",
        "scope": "finite operational toy model; no claim of observer-independent physical geometry",
        "parameters": {
            "state_count": universe.state_count,
            "factor_count": universe.coordinates.shape[1],
            "side_length": 6,
            "times_per_protocol": 14,
            "protocols_per_ensemble": protocol_count,
            "channel_counts": [8, 16, 32, 64],
        },
        "complete_observer_schedule_comparisons": schedule_comparisons,
        "random_protocol_ensembles": ensembles,
        "adversarial_axis_blind_audit": axis_blind_audit(
            universe.coordinates, universe.laplacian, schedules["early"]
        ),
        "adjacent_mixture_recovery": mixture_recovery_audit(universe.laplacian),
        "falsification_readout": {
            "supported": (
                "within a fixed schedule, independently refreshed random sensors "
                "concentrate around the complete pure-state geometry as channels grow"
            ),
            "rejected": (
                "arbitrary time schedules and adversarial sensor classes do not "
                "induce one observer-independent geometry"
            ),
            "new_obstruction": (
                "three axis-blind protocols separate every pure state yet share a "
                "125-dimensional kernel on mixture differences"
            ),
            "adjacent_remedy": (
                "early independently refreshed sensors change arbitrary-mixture "
                "recovery from catastrophic conditioning to a finite stable regime"
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocols", type=int, default=16)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    print(
        json.dumps(
            run_stage_2_experiment(arguments.protocols),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
