#!/usr/bin/env python3
"""Operational geometry from finite dynamics and restricted measurements.

The latent states of the reference toy universe are the smooth integers

    n = product_i p_i**a_i,          0 <= a_i < side_length.

Allowed transitions multiply or divide by one generating prime.  No spatial
coordinates are supplied to the observer.  A family of linear measurements of
the heat evolution is stacked into an observability map ``O``; the induced
distance is

    d(x, y) = ||O(x-y)||_2,          G = O.T @ O.

The file also constructs degree-preserving rewired controls and evaluates
locality, spectral dimension, stable observable modes, propagation, and
Gaussian discrimination bounds.  It is a finite mathematical toy model, not a
claim about physical spacetime or quantum fields.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
from scipy.special import ndtr
from scipy.stats import spearmanr


@dataclass(frozen=True)
class FiniteUniverse:
    """A finite state set with undirected allowed-transition relations."""

    labels: tuple[int, ...]
    coordinates: np.ndarray
    edges: tuple[tuple[int, int], ...]
    adjacency: np.ndarray
    laplacian: np.ndarray

    @property
    def state_count(self) -> int:
        return len(self.labels)


@dataclass(frozen=True)
class OperationalGeometry:
    """The finite observable-history embedding and its induced geometry."""

    observation_times: np.ndarray
    measurement_matrix: np.ndarray
    observability_matrix: np.ndarray
    gram: np.ndarray
    distances: np.ndarray
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray


def _is_prime(value: int) -> bool:
    if value < 2:
        return False
    for divisor in range(2, math.isqrt(value) + 1):
        if value % divisor == 0:
            return False
    return True


def _universe_from_edges(
    labels: Sequence[int],
    coordinates: np.ndarray,
    edges: Iterable[tuple[int, int]],
) -> FiniteUniverse:
    state_count = len(labels)
    canonical = tuple(sorted({tuple(sorted(edge)) for edge in edges}))
    adjacency = np.zeros((state_count, state_count), dtype=float)
    for left, right in canonical:
        if left == right or left < 0 or right >= state_count:
            raise ValueError("invalid universe edge")
        adjacency[left, right] = 1.0
        adjacency[right, left] = 1.0
    laplacian = np.diag(np.sum(adjacency, axis=1)) - adjacency
    return FiniteUniverse(
        tuple(int(label) for label in labels),
        np.asarray(coordinates, dtype=int),
        canonical,
        adjacency,
        laplacian,
    )


def factorization_universe(
    primes: Sequence[int] = (2, 3, 5), side_length: int = 6
) -> FiniteUniverse:
    """Build a box of smooth integers with single-prime transition edges."""
    primes = tuple(int(prime) for prime in primes)
    if side_length < 2 or not primes or len(set(primes)) != len(primes):
        raise ValueError("need distinct primes and side_length at least two")
    if any(not _is_prime(prime) for prime in primes):
        raise ValueError("every generator must be prime")
    coordinate_tuples = list(
        itertools.product(range(side_length), repeat=len(primes))
    )
    index = {coordinate: position for position, coordinate in enumerate(coordinate_tuples)}
    labels = []
    edges = []
    for coordinate in coordinate_tuples:
        label = math.prod(
            prime**exponent for prime, exponent in zip(primes, coordinate)
        )
        labels.append(label)
        for axis in range(len(primes)):
            if coordinate[axis] + 1 < side_length:
                neighbor = list(coordinate)
                neighbor[axis] += 1
                edges.append((index[coordinate], index[tuple(neighbor)]))
    return _universe_from_edges(labels, np.asarray(coordinate_tuples), edges)


def is_connected(state_count: int, edges: Sequence[tuple[int, int]]) -> bool:
    neighbors: list[list[int]] = [[] for _ in range(state_count)]
    for left, right in edges:
        neighbors[left].append(right)
        neighbors[right].append(left)
    visited = {0}
    queue = [0]
    for state in queue:
        for neighbor in neighbors[state]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return len(visited) == state_count


def _rewire_once(
    edges: Sequence[tuple[int, int]], swap_count: int, seed: int
) -> tuple[tuple[tuple[int, int], ...], int]:
    rng = np.random.default_rng(seed)
    edge_set = {tuple(sorted(edge)) for edge in edges}
    edge_list = sorted(edge_set)
    completed = 0
    attempts = 0
    maximum_attempts = max(10_000, 100 * swap_count)
    while completed < swap_count and attempts < maximum_attempts:
        attempts += 1
        first_index, second_index = rng.choice(len(edge_list), 2, replace=False)
        left, right = edge_list[int(first_index)]
        other_left, other_right = edge_list[int(second_index)]
        if len({left, right, other_left, other_right}) < 4:
            continue
        if rng.random() < 0.5:
            replacements = [
                tuple(sorted((left, other_right))),
                tuple(sorted((other_left, right))),
            ]
        else:
            replacements = [
                tuple(sorted((left, other_left))),
                tuple(sorted((right, other_right))),
            ]
        if (
            replacements[0] == replacements[1]
            or any(edge in edge_set for edge in replacements)
            or any(a == b for a, b in replacements)
        ):
            continue
        edge_set.remove(edge_list[int(first_index)])
        edge_set.remove(edge_list[int(second_index)])
        edge_set.update(replacements)
        edge_list[int(first_index)] = replacements[0]
        edge_list[int(second_index)] = replacements[1]
        completed += 1
    return tuple(sorted(edge_set)), completed


def degree_preserving_control(
    universe: FiniteUniverse,
    swap_multiplier: int = 20,
    seed: int = 1,
    maximum_retries: int = 16,
) -> FiniteUniverse:
    """Randomize relations while preserving every vertex degree and connectivity."""
    if swap_multiplier < 1 or maximum_retries < 1:
        raise ValueError("control parameters must be positive")
    swap_count = swap_multiplier * len(universe.edges)
    original_degrees = np.sum(universe.adjacency, axis=1)
    for retry in range(maximum_retries):
        control_edges, completed = _rewire_once(
            universe.edges, swap_count, seed + 1_009 * retry
        )
        if completed != swap_count or not is_connected(
            universe.state_count, control_edges
        ):
            continue
        control = _universe_from_edges(
            universe.labels, universe.coordinates, control_edges
        )
        if not np.array_equal(
            np.sum(control.adjacency, axis=1), original_degrees
        ):
            raise AssertionError("degree-preserving rewire changed the degrees")
        return control
    raise RuntimeError("could not construct a connected rewired control")


def rademacher_measurements(
    state_count: int, channel_count: int, seed: int = 20_260_813
) -> np.ndarray:
    """Coordinate-free signed coarse measurements with normalized row scale."""
    if state_count < 2 or not 1 <= channel_count <= state_count:
        raise ValueError("invalid measurement dimensions")
    rng = np.random.default_rng(seed)
    return rng.choice([-1.0, 1.0], size=(channel_count, state_count)) / math.sqrt(
        channel_count
    )


def operational_geometry(
    laplacian: np.ndarray,
    measurement_matrix: np.ndarray,
    observation_times: Sequence[float],
) -> OperationalGeometry:
    """Build ``O``, ``G=O.T@O``, and all pure-state operational distances."""
    laplacian = np.asarray(laplacian, dtype=float)
    measurement_matrix = np.asarray(measurement_matrix, dtype=float)
    times = np.asarray(observation_times, dtype=float)
    state_count = len(laplacian)
    if laplacian.shape != (state_count, state_count):
        raise ValueError("laplacian must be square")
    if measurement_matrix.ndim != 2 or measurement_matrix.shape[1] != state_count:
        raise ValueError("measurement matrix and state count disagree")
    if times.ndim != 1 or len(times) == 0 or np.any(times < 0.0):
        raise ValueError("observation times must be a nonempty nonnegative vector")
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
    blocks = []
    for time in times:
        heat = (eigenvectors * np.exp(-time * eigenvalues)) @ eigenvectors.T
        blocks.append(measurement_matrix @ heat)
    observability = np.vstack(blocks)
    gram = observability.T @ observability
    diagonal = np.diag(gram)
    squared_distances = (
        diagonal[:, None] + diagonal[None, :] - 2.0 * gram
    )
    distances = np.sqrt(np.maximum(0.0, squared_distances))
    return OperationalGeometry(
        times,
        measurement_matrix,
        observability,
        gram,
        distances,
        eigenvalues,
        eigenvectors,
    )


def all_pairs_graph_distances(universe: FiniteUniverse) -> np.ndarray:
    """Unweighted shortest-path distances, used only for post-hoc auditing."""
    result = np.full(
        (universe.state_count, universe.state_count),
        universe.state_count + 1,
        dtype=int,
    )
    neighbors = [np.flatnonzero(row).tolist() for row in universe.adjacency]
    for source in range(universe.state_count):
        result[source, source] = 0
        queue = [source]
        for state in queue:
            for neighbor in neighbors[state]:
                if result[source, neighbor] > universe.state_count:
                    result[source, neighbor] = result[source, state] + 1
                    queue.append(neighbor)
    return result


def exponent_manhattan_distances(coordinates: np.ndarray) -> np.ndarray:
    coordinates = np.asarray(coordinates, dtype=int)
    return np.sum(
        np.abs(coordinates[:, None, :] - coordinates[None, :, :]), axis=2
    )


def pairwise_spearman(first: np.ndarray, second: np.ndarray) -> float:
    if first.shape != second.shape or first.ndim != 2 or first.shape[0] != first.shape[1]:
        raise ValueError("pairwise matrices must be equally sized and square")
    upper = np.triu_indices(len(first), 1)
    return float(spearmanr(first[upper], second[upper]).statistic)


def edge_locality_auc(universe: FiniteUniverse, distances: np.ndarray) -> float:
    """Probability that a random transition edge is nearer than a nonedge."""
    edge_values = np.asarray(
        [distances[left, right] for left, right in universe.edges]
    )
    nonedge_mask = np.triu(1.0 - universe.adjacency, 1) > 0.0
    nonedge_values = np.sort(distances[nonedge_mask])
    lower = np.searchsorted(nonedge_values, edge_values, side="left")
    upper = np.searchsorted(nonedge_values, edge_values, side="right")
    greater = len(nonedge_values) - upper
    equal = upper - lower
    return float(np.mean((greater + 0.5 * equal) / len(nonedge_values)))


def spectral_dimension_profile(
    eigenvalues: Sequence[float], times: Sequence[float]
) -> tuple[np.ndarray, np.ndarray]:
    """Finite heat-trace spectral dimension after removing stationarity."""
    eigenvalues = np.asarray(eigenvalues, dtype=float)
    times = np.asarray(times, dtype=float)
    if len(eigenvalues) < 2 or len(times) < 3 or np.any(times <= 0.0):
        raise ValueError("need a nontrivial spectrum and positive time grid")
    heat = np.mean(np.exp(-np.outer(times, eigenvalues)), axis=1) - 1.0 / len(
        eigenvalues
    )
    heat = np.maximum(heat, np.finfo(float).tiny)
    dimension = -2.0 * np.gradient(np.log(heat), np.log(times))
    return heat, dimension


def spectral_dimension_estimate(
    eigenvalues: Sequence[float],
    profile_times: Sequence[float],
    window: tuple[float, float] = (1.0, 3.0),
) -> tuple[float, float]:
    """Median spectral dimension and median absolute plateau deviation."""
    times = np.asarray(profile_times, dtype=float)
    _, dimension = spectral_dimension_profile(eigenvalues, times)
    selected = (times >= window[0]) & (times <= window[1])
    if np.count_nonzero(selected) < 3:
        raise ValueError("spectral window contains too few samples")
    estimate = float(np.median(dimension[selected]))
    dispersion = float(np.median(np.abs(dimension[selected] - estimate)))
    return estimate, dispersion


def stable_observable_subspaces(
    geometry: OperationalGeometry,
    minimum_half_life: float = 2.0,
    minimum_observation_energy: float = 0.1,
    eigenvalue_tolerance: float = 1e-9,
) -> list[dict[str, object]]:
    """Audit stable eigenspaces without choosing a basis inside degeneracies.

    The singular values of ``O`` restricted to a degenerate Laplacian
    eigenspace are invariant under an orthogonal change of eigenbasis.  This is
    the correct object for counting observable directions; inspecting the
    energy of individual numerical eigenvectors is not basis invariant.
    """
    eigenvalues = geometry.eigenvalues
    groups: list[tuple[int, int]] = []
    start = 0
    for stop in range(1, len(eigenvalues) + 1):
        if stop == len(eigenvalues) or not math.isclose(
            float(eigenvalues[stop]),
            float(eigenvalues[start]),
            rel_tol=eigenvalue_tolerance,
            abs_tol=eigenvalue_tolerance,
        ):
            groups.append((start, stop))
            start = stop

    results: list[dict[str, object]] = []
    for start, stop in groups:
        group_eigenvalues = eigenvalues[start:stop]
        if float(np.max(group_eigenvalues)) <= 1e-12:
            continue
        minimum_group_half_life = math.log(2.0) / float(
            np.max(group_eigenvalues)
        )
        restricted_history = (
            geometry.observability_matrix @ geometry.eigenvectors[:, start:stop]
        )
        energy_eigenvalues = np.linalg.svd(
            restricted_history, compute_uv=False
        ) ** 2
        observable_dimension = int(
            np.count_nonzero(energy_eigenvalues >= minimum_observation_energy)
        )
        if (
            minimum_group_half_life >= minimum_half_life
            and observable_dimension > 0
        ):
            results.append(
                {
                    "eigenspace_start_index": int(start),
                    "eigenspace_multiplicity": int(stop - start),
                    "generator_eigenvalue": float(np.mean(group_eigenvalues)),
                    "minimum_half_life": minimum_group_half_life,
                    "observation_energy_eigenvalues": [
                        float(value) for value in energy_eigenvalues
                    ],
                    "physicalized_dimension": observable_dimension,
                }
            )
    return results


def stable_observable_modes(
    geometry: OperationalGeometry,
    minimum_half_life: float = 2.0,
    minimum_observation_energy: float = 0.1,
    eigenvalue_tolerance: float = 1e-9,
) -> list[dict[str, float]]:
    """Return basis-invariant observable directions in stable eigenspaces."""
    directions = []
    for subspace in stable_observable_subspaces(
        geometry,
        minimum_half_life,
        minimum_observation_energy,
        eigenvalue_tolerance,
    ):
        for energy in subspace["observation_energy_eigenvalues"]:
            if float(energy) >= minimum_observation_energy:
                directions.append(
                    {
                        "eigenspace_start_index": int(
                            subspace["eigenspace_start_index"]
                        ),
                        "eigenspace_multiplicity": int(
                            subspace["eigenspace_multiplicity"]
                        ),
                        "generator_eigenvalue": float(
                            subspace["generator_eigenvalue"]
                        ),
                        "half_life": float(subspace["minimum_half_life"]),
                        "observation_energy": float(energy),
                    }
                )
    return directions


def binary_gaussian_error(distance: float, noise_standard_deviation: float) -> float:
    """Exact equal-prior error for two signatures under isotropic Gaussian noise."""
    if distance < 0.0 or noise_standard_deviation <= 0.0:
        raise ValueError("distance must be nonnegative and noise positive")
    return float(ndtr(-distance / (2.0 * noise_standard_deviation)))


def nearest_signature_union_bound(
    distances: np.ndarray, noise_standard_deviation: float
) -> np.ndarray:
    """Coordinatewise union bound for nearest-signature classification."""
    if noise_standard_deviation <= 0.0:
        raise ValueError("noise standard deviation must be positive")
    probabilities = ndtr(-distances / (2.0 * noise_standard_deviation))
    np.fill_diagonal(probabilities, 0.0)
    return np.minimum(1.0, np.sum(probabilities, axis=1))


def operational_propagation_exponent(
    geometry: OperationalGeometry,
    start_state: int,
    propagation_times: Sequence[float],
    fit_window: tuple[float, float] = (0.03, 0.2),
) -> tuple[float, np.ndarray]:
    """Fit ``R(t) ~ t^alpha`` using radius in the derived operational metric."""
    times = np.asarray(propagation_times, dtype=float)
    if not 0 <= start_state < len(geometry.distances) or np.any(times <= 0.0):
        raise ValueError("invalid propagation experiment")
    radii = []
    source_coordinates = geometry.eigenvectors[start_state, :]
    for time in times:
        distribution = (
            geometry.eigenvectors * np.exp(-time * geometry.eigenvalues)
        ) @ source_coordinates
        distribution = np.maximum(0.0, distribution)
        distribution /= np.sum(distribution)
        radii.append(
            math.sqrt(
                float(
                    np.dot(
                        distribution,
                        geometry.distances[start_state, :] ** 2,
                    )
                )
            )
        )
    radii_array = np.asarray(radii)
    selected = (times >= fit_window[0]) & (times <= fit_window[1])
    exponent = float(
        np.polyfit(np.log(times[selected]), np.log(radii_array[selected]), 1)[0]
    )
    return exponent, radii_array


def _geometry_report(
    universe: FiniteUniverse,
    measurement_matrix: np.ndarray,
    observation_times: np.ndarray,
    hidden_exponent_distances: np.ndarray,
) -> tuple[dict[str, object], OperationalGeometry]:
    compressed = operational_geometry(
        universe.laplacian, measurement_matrix, observation_times
    )
    full = operational_geometry(
        universe.laplacian, np.eye(universe.state_count), observation_times
    )
    graph_distances = all_pairs_graph_distances(universe)
    profile_times = np.geomspace(0.03, 20.0, 120)
    dimension, plateau_deviation = spectral_dimension_estimate(
        compressed.eigenvalues, profile_times
    )
    pure_distances = compressed.distances.copy()
    np.fill_diagonal(pure_distances, np.inf)
    margins = np.min(pure_distances, axis=1)
    noise = float(np.min(margins) / 8.0)
    error_bounds = nearest_signature_union_bound(compressed.distances, noise)
    singular_values = np.linalg.svd(
        compressed.observability_matrix, compute_uv=False
    )
    modes = stable_observable_modes(compressed)
    return (
        {
            "compressed_vs_full_distance_spearman": pairwise_spearman(
                compressed.distances, full.distances
            ),
            "compressed_vs_own_graph_distance_spearman": pairwise_spearman(
                compressed.distances, graph_distances
            ),
            "compressed_vs_original_exponent_distance_spearman": pairwise_spearman(
                compressed.distances, hidden_exponent_distances
            ),
            "full_vs_own_graph_distance_spearman": pairwise_spearman(
                full.distances, graph_distances
            ),
            "edge_locality_auc": edge_locality_auc(universe, compressed.distances),
            "spectral_dimension_1_to_3": dimension,
            "spectral_dimension_plateau_mad": plateau_deviation,
            "spectral_gap": float(compressed.eigenvalues[1]),
            "stable_observable_mode_count": len(modes),
            "stable_observable_modes": modes,
            "minimum_pure_state_margin": float(np.min(margins)),
            "declared_noise_standard_deviation": noise,
            "worst_nearest_signature_error_union_bound": float(
                np.max(error_bounds)
            ),
            "observability_numerical_rank": int(
                np.linalg.matrix_rank(compressed.observability_matrix)
            ),
            "observability_smallest_singular_value": float(singular_values[-1]),
            "observability_condition_number": float(
                singular_values[0] / singular_values[-1]
            ),
        },
        compressed,
    )


def _summary(values: Sequence[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    return {
        "mean": float(np.mean(array)),
        "standard_deviation": float(np.std(array)),
        "minimum": float(np.min(array)),
        "median": float(np.median(array)),
        "maximum": float(np.max(array)),
    }


def run_reference_experiment(
    control_count: int = 32,
    measurement_seed: int = 20_260_813,
) -> dict[str, object]:
    """Run the Stage 1 factorization universe and matched-control audit."""
    if control_count < 1:
        raise ValueError("at least one control is required")
    universe = factorization_universe()
    measurements = rademacher_measurements(
        universe.state_count, 32, measurement_seed
    )
    observation_times = np.geomspace(1.0, 8.0, 14)
    hidden_distances = exponent_manhattan_distances(universe.coordinates)
    arithmetic_report, arithmetic_geometry = _geometry_report(
        universe, measurements, observation_times, hidden_distances
    )
    center_coordinate = tuple([2] * universe.coordinates.shape[1])
    center_state = int(
        np.flatnonzero(
            np.all(universe.coordinates == np.asarray(center_coordinate), axis=1)
        )[0]
    )
    propagation_times = np.geomspace(0.03, 4.0, 60)
    exponent, _ = operational_propagation_exponent(
        arithmetic_geometry, center_state, propagation_times
    )
    arithmetic_report["early_operational_propagation_exponent"] = exponent

    representative_control = degree_preserving_control(universe, seed=1)
    representative_report, _ = _geometry_report(
        representative_control,
        measurements,
        observation_times,
        hidden_distances,
    )

    profile_times = np.geomspace(0.03, 20.0, 120)
    control_dimensions = []
    control_plateau_deviations = []
    control_gaps = []
    control_slow_mode_counts = []
    for seed in range(1, control_count + 1):
        control = degree_preserving_control(universe, seed=seed)
        eigenvalues = np.linalg.eigvalsh(control.laplacian)
        dimension, deviation = spectral_dimension_estimate(
            eigenvalues, profile_times
        )
        control_dimensions.append(dimension)
        control_plateau_deviations.append(deviation)
        control_gaps.append(float(eigenvalues[1]))
        control_slow_mode_counts.append(int(np.sum(eigenvalues[1:] <= 0.5)))

    channel_sweep: dict[str, dict[str, float]] = {}
    full_geometry = operational_geometry(
        universe.laplacian, np.eye(universe.state_count), observation_times
    )
    for channel_count in [4, 8, 16, 32, 64]:
        correlations = []
        for seed in range(16):
            candidate = operational_geometry(
                universe.laplacian,
                rademacher_measurements(universe.state_count, channel_count, seed),
                observation_times,
            )
            correlations.append(
                pairwise_spearman(candidate.distances, full_geometry.distances)
            )
        channel_sweep[str(channel_count)] = {
            "mean_compressed_vs_full_spearman": float(np.mean(correlations)),
            "standard_deviation": float(np.std(correlations)),
        }

    expected_edges = (
        universe.coordinates.shape[1]
        * (6 - 1)
        * 6 ** (universe.coordinates.shape[1] - 1)
    )
    return {
        "model": "finite operational geometry from factorization diffusion",
        "scope": (
            "mathematical toy model; no inference about physical spacetime, "
            "quantum fields, or the substrate of reality"
        ),
        "parameters": {
            "generating_primes": [2, 3, 5],
            "exponents_per_prime": 6,
            "state_count": universe.state_count,
            "edge_count": len(universe.edges),
            "expected_cartesian_product_edge_count": expected_edges,
            "measurement_channels": 32,
            "observation_times": observation_times.tolist(),
            "control_count": control_count,
            "degree_preserving_swaps_per_edge": 20,
        },
        "arithmetic_factorization_universe": arithmetic_report,
        "representative_degree_preserving_control": representative_report,
        "control_ensemble": {
            "spectral_dimension_1_to_3": _summary(control_dimensions),
            "spectral_dimension_plateau_mad": _summary(
                control_plateau_deviations
            ),
            "spectral_gap": _summary(control_gaps),
            "slow_nonconstant_modes_lambda_at_most_0_5": _summary(
                control_slow_mode_counts
            ),
        },
        "measurement_channel_sweep": channel_sweep,
        "falsification_readout": {
            "generic_result": (
                "both the factorization graph and rewired controls make their "
                "actual transition edges operationally local"
            ),
            "structure_specific_result": (
                "degree-preserving rewiring destroys the three-dimensional "
                "spectral plateau, the three slow prime-direction modes, and "
                "most alignment with the hidden exponent coordinates"
            ),
            "important_failure": (
                "pure states are robustly separated at the declared noise, "
                "but arbitrary mixture inversion is extremely ill-conditioned"
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controls", type=int, default=32)
    parser.add_argument("--measurement-seed", type=int, default=20_260_813)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    print(
        json.dumps(
            run_reference_experiment(arguments.controls, arguments.measurement_seed),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
