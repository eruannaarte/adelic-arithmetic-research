#!/usr/bin/env python3
"""Stage IV: interventions, directed response, and approximate causal cones.

The module separates three notions that passive geometry can conflate:

* symmetric state-space diffusion;
* directed subsystem response under declared interventions; and
* finite-speed propagation in the graph underlying a Markov generator.

Continuous-time Markov evolution has no strict finite propagation cone on a
connected finite graph.  Uniformization nevertheless gives an exact Poisson
tail envelope.  A finite causal-jet test, based on Cayley--Hamilton, also
certifies when an intervention-response channel vanishes for every time.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import deque
from typing import Sequence

import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize
from scipy.stats import poisson

from operational_information_geometry import factorization_universe
from operational_information_geometry_ii import mixture_tangent_basis
from operational_information_geometry_iii import (
    diagonal_markov_interaction_laplacian,
    independent_generator,
    marginal_measurements,
)


# Freeze the binary64 candidate grid used for the published Stage IV design.
# NumPy's geomspace can differ by a few ulps across platforms because its
# logarithm/exponential path depends on the system math library.  Hexadecimal
# literals make the finite optimization problem exactly reproducible.
STAGE_IV_REFERENCE_TIME_HEX = (
    "0x1.0624dd2f1a9fcp-10",
    "0x1.1b3d3c907e0fap-10",
    "0x1.32082fde119bap-10",
    "0x1.4aa8afbcf09f9p-10",
    "0x1.65448541bd769p-10",
    "0x1.820483ea2bff4p-10",
    "0x1.a114c840df8d2p-10",
    "0x1.c2a4fb8bb8505p-10",
    "0x1.e6e89cec68366p-10",
    "0x1.070ba831c13dbp-9",
    "0x1.1c369a17a04cbp-9",
    "0x1.33159e847c52cp-9",
    "0x1.4bcbcce765cb8p-9",
    "0x1.667f0f993ab76p-9",
    "0x1.83585e093bb26p-9",
    "0x1.a283fb980ff79p-9",
    "0x1.c431bb81a8f52p-9",
    "0x1.e8954a3e38de9p-9",
    "0x1.07f33e656921fp-8",
    "0x1.1d30d329ab067p-8",
    "0x1.3423fa608fa39p-8",
    "0x1.4cefea5e37e5cp-8",
    "0x1.67baaedd072e3p-8",
    "0x1.84ad635d6ff06p-8",
    "0x1.a3f472384e4ffp-8",
    "0x1.c5bfd8c49658ap-8",
    "0x1.ea4370f8e4f0cp-8",
    "0x1.08dba07cf65a3p-7",
    "0x1.1e2be887e7967p-7",
    "0x1.3533444322c22p-7",
    "0x1.4e1509030c691p-7",
    "0x1.68f76400f0d54p-7",
    "0x1.860394ee3544dp-7",
    "0x1.a5662d3e39df8p-7",
    "0x1.c74f548807339p-7",
    "0x1.ebf31268b26e4p-7",
    "0x1.09c4cf2bea740p-6",
    "0x1.1f27daf449809p-6",
    "0x1.36437cfdc4be9p-6",
    "0x1.4f3b29b84f7abp-6",
    "0x1.6a352ff99c4c6p-6",
    "0x1.875af3c3e0260p-6",
    "0x1.a6d92dc76c835p-6",
    "0x1.c8e0300090fffp-6",
    "0x1.eda42fdb0be25p-6",
    "0x1.0aaecb2665065p-5",
    "0x1.2024ab316f0b2p-5",
    "0x1.3754a562bd297p-5",
    "0x1.50624d6134970p-5",
    "0x1.6b7413bc85958p-5",
    "0x1.88b380e7adc20p-5",
    "0x1.a84d74f27b8bfp-5",
    "0x1.ca726c63d8e47p-5",
    "0x1.ef56ca9e81637p-5",
    "0x1.0b999521243d0p-4",
    "0x1.21225a02a1d43p-4",
    "0x1.3866be450cb44p-4",
    "0x1.518a74e1b741dp-4",
    "0x1.6cb4104000d2fp-4",
    "0x1.8a0d3d63c4cb5p-4",
    "0x1.a9c303def8983p-4",
    "0x1.cc060ae894a4cp-4",
    "0x1.f10ae402c993fp-4",
    "0x1.0c852dd185647p-3",
    "0x1.2220e82bd7681p-3",
    "0x1.3979c8786dd4fp-3",
    "0x1.52b3a11e9bb74p-3",
    "0x1.6df5267b3b058p-3",
    "0x1.8b682a4336475p-3",
    "0x1.ab39dbad72746p-3",
    "0x1.cd9b0cc68b92ap-3",
    "0x1.f2c07d58c2a7ep-3",
    "0x1.0d7195ed85758p-2",
    "0x1.23205671b1d90p-2",
    "0x1.3a8dc4d1556a9p-2",
    "0x1.53ddd2fd6f9a8p-2",
    "0x1.6f3757663acb5p-2",
    "0x1.8cc44891fe5acp-2",
    "0x1.acb1fd7f75f9cp-2",
    "0x1.cf317336977bfp-2",
    "0x1.f47797f273661p-2",
    "0x1.0e5ece2bc1a2dp-1",
    "0x1.2420a5998057fp-1",
    "0x1.3ba2b424f35efp-1",
    "0x1.55090b648aa93p-1",
    "0x1.707aa3f9e1203p-1",
    "0x1.8e21995d051b4p-1",
    "0x1.ae2b6a778eec0p-1",
    "0x1.d0c93f72a59f7p-1",
    "0x1.f63035230c312p-1",
    "0x1.0f4cd74377e45p+0",
    "0x1.2521d6693fcafp+0",
    "0x1.3cb89749334e0p+0",
    "0x1.56354b3b0f6cep+0",
    "0x1.71bf0d2fea1bdp+0",
    "0x1.8f801db21f5bcp+0",
    "0x1.afa623b948dd2p+0",
    "0x1.d26272b5b79e0p+0",
    "0x1.f7ea563ee8094p+0",
    "0x1.103bb1ec87867p+1",
    "0x1.2623e9a79b68bp+1",
    "0x1.3dcf6f14bd29ep+1",
    "0x1.57629368ebebap+1",
    "0x1.73049402edb55p+1",
    "0x1.90dfd6a00f80cp+1",
    "0x1.b1222a69300aap+1",
    "0x1.d3fd0e3be46c4p+1",
    "0x1.f9a5fc9b8d96dp+1",
    "0x1.112b5edf71b7ap+2",
    "0x1.2726e01bed4f5p+2",
    "0x1.3ee73c5ef5dfap+2",
    "0x1.5890e4d6da5e3p+2",
    "0x1.744b396e60839p+2",
    "0x1.9240c536864ddp+2",
    "0x1.b29f7facd2431p+2",
    "0x1.d5991342594a7p+2",
    "0x1.fb63298fb030bp+2",
    "0x1.121bded55a15bp+3",
    "0x1.282aba8e3f207p+3",
    "0x1.4000000000000p+3",
)

STAGE_IV_REFERENCE_DYADIC_NUMERATORS = {
    62: 963,
    76: 71,
    77: 669,
    87: 1289,
    105: 294,
    106: 810,
}


def stage_iv_reference_time_grid() -> np.ndarray:
    """Return the platform-independent published binary64 time grid."""
    return np.asarray(
        [float.fromhex(value) for value in STAGE_IV_REFERENCE_TIME_HEX],
        dtype=float,
    )


def one_way_rate_modulation_generator(
    left_laplacian: np.ndarray,
    right_laplacian: np.ndarray,
    interaction_strength: float,
    modulation: Sequence[float] | None = None,
) -> np.ndarray:
    """Return a Markov generator in which A modulates B's transition rate.

    The generator is

    ``L_A kron I + I kron L_B + g D_A kron L_B``.

    For a nonnegative diagonal ``D_A`` and graph Laplacians ``L_A,L_B``, this
    is again a graph Laplacian.  Its A marginal is autonomous, while its B
    marginal can depend on the distribution of A.
    """
    left = np.asarray(left_laplacian, dtype=float)
    right = np.asarray(right_laplacian, dtype=float)
    if left.ndim != 2 or left.shape[0] != left.shape[1]:
        raise ValueError("left_laplacian must be square")
    if right.ndim != 2 or right.shape[0] != right.shape[1]:
        raise ValueError("right_laplacian must be square")
    if interaction_strength < 0.0:
        raise ValueError("interaction_strength must be nonnegative")
    if modulation is None:
        values = np.linspace(0.0, 1.0, len(left))
    else:
        values = np.asarray(modulation, dtype=float)
    if values.shape != (len(left),) or np.any(values < 0.0):
        raise ValueError("modulation must be one nonnegative value per A state")
    return independent_generator(left, right) + interaction_strength * np.kron(
        np.diag(values), right
    )


def localized_intervention_maps(
    left_state_count: int,
    right_state_count: int,
    left_background: int = 0,
    right_background: int = 0,
) -> dict[str, np.ndarray]:
    """Construct mass-preserving subsystem interventions and marginal sensors.

    An A intervention varies A in its simplex tangent while holding B at a
    declared background state; a B intervention is defined analogously.
    """
    if not 0 <= left_background < left_state_count:
        raise ValueError("invalid left background")
    if not 0 <= right_background < right_state_count:
        raise ValueError("invalid right background")
    left_basis = mixture_tangent_basis(left_state_count)
    right_basis = mixture_tangent_basis(right_state_count)
    left_point = np.eye(left_state_count)[:, left_background, None]
    right_point = np.eye(right_state_count)[:, right_background, None]
    left_marginal, right_marginal, _ = marginal_measurements(
        left_state_count, right_state_count
    )
    return {
        "left_marginal": left_marginal,
        "right_marginal": right_marginal,
        "left_intervention": np.kron(left_basis, right_point),
        "right_intervention": np.kron(left_point, right_basis),
    }


def response_blocks(
    generator: np.ndarray,
    measurement: np.ndarray,
    intervention: np.ndarray,
    observation_times: Sequence[float],
) -> tuple[np.ndarray, ...]:
    """Return ``M exp(-tL) J`` at every declared observation time."""
    generator = np.asarray(generator, dtype=float)
    measurement = np.asarray(measurement, dtype=float)
    intervention = np.asarray(intervention, dtype=float)
    times = np.asarray(observation_times, dtype=float)
    state_count = len(generator)
    if generator.shape != (state_count, state_count):
        raise ValueError("generator must be square")
    if measurement.ndim != 2 or measurement.shape[1] != state_count:
        raise ValueError("measurement has the wrong latent dimension")
    if intervention.ndim != 2 or intervention.shape[0] != state_count:
        raise ValueError("intervention has the wrong latent dimension")
    if times.ndim != 1 or len(times) == 0 or np.any(times < 0.0):
        raise ValueError("nonnegative observation times are required")
    return tuple(
        measurement @ expm(-float(time) * generator) @ intervention
        for time in times
    )


def _rank_condition(
    matrix: np.ndarray,
    absolute_tolerance: float = 1e-11,
    relative_tolerance: float = 1e-10,
) -> dict[str, float | int | None]:
    singular_values = np.linalg.svd(np.asarray(matrix, dtype=float), compute_uv=False)
    if len(singular_values) == 0:
        return {
            "rank": 0,
            "minimum_active_singular_value": None,
            "maximum_singular_value": 0.0,
            "active_subspace_condition_number": None,
        }
    threshold = max(absolute_tolerance, relative_tolerance * singular_values[0])
    rank = int(np.sum(singular_values > threshold))
    if rank == 0:
        minimum = None
        condition = None
    else:
        minimum = float(singular_values[rank - 1])
        condition = float(singular_values[0] / singular_values[rank - 1])
    return {
        "rank": rank,
        "minimum_active_singular_value": minimum,
        "maximum_singular_value": float(singular_values[0]),
        "active_subspace_condition_number": condition,
    }


def response_summary(blocks: Sequence[np.ndarray]) -> dict[str, object]:
    """Summarize the strength and recoverable rank of a response history."""
    if len(blocks) == 0:
        raise ValueError("at least one response block is required")
    history = np.vstack(blocks)
    rank = _rank_condition(history)
    return {
        "maximum_instantaneous_frobenius_norm": float(
            max(np.linalg.norm(block, ord="fro") for block in blocks)
        ),
        "stacked_history_frobenius_norm": float(np.linalg.norm(history, ord="fro")),
        "history_rank": rank["rank"],
        "intervention_dimension": int(history.shape[1]),
        "minimum_active_singular_value": rank["minimum_active_singular_value"],
        "active_subspace_condition_number": rank[
            "active_subspace_condition_number"
        ],
    }


def causal_jet_audit(
    generator: np.ndarray,
    measurement: np.ndarray,
    intervention: np.ndarray,
    characteristic_time: float = 0.1,
    maximum_order: int | None = None,
) -> dict[str, object]:
    """Audit the finite Taylor jet ``M L^k J`` of a response channel.

    Cayley--Hamilton makes orders 0 through ``N-1`` a complete vanishing test
    for an N-dimensional latent generator.  Characteristic-time and factorial
    scaling stabilize the numerical rank audit without changing exact ranks.
    """
    generator = np.asarray(generator, dtype=float)
    measurement = np.asarray(measurement, dtype=float)
    intervention = np.asarray(intervention, dtype=float)
    state_count = len(generator)
    if characteristic_time <= 0.0:
        raise ValueError("characteristic_time must be positive")
    if maximum_order is None:
        maximum_order = state_count - 1
    if not 0 <= maximum_order <= state_count - 1:
        raise ValueError("maximum_order must lie between zero and N-1")

    power_applied = intervention.copy()
    blocks = []
    cumulative_ranks = []
    scaled_norms = []
    first_nonzero_order = None
    full_rank_order = None
    for order in range(maximum_order + 1):
        if order > 0:
            power_applied = generator @ power_applied
        block = (
            characteristic_time**order
            / math.factorial(order)
            * (measurement @ power_applied)
        )
        blocks.append(block)
        norm = float(np.linalg.norm(block, ord="fro"))
        scaled_norms.append(norm)
        if first_nonzero_order is None and norm > 1e-11:
            first_nonzero_order = order
        rank = int(_rank_condition(np.vstack(blocks))["rank"])
        cumulative_ranks.append(rank)
        if full_rank_order is None and rank == intervention.shape[1]:
            full_rank_order = order

    return {
        "latent_dimension": state_count,
        "orders_audited": maximum_order + 1,
        "characteristic_time": characteristic_time,
        "first_numerically_nonzero_order": first_nonzero_order,
        "first_full_intervention_rank_order": full_rank_order,
        "final_cumulative_rank": cumulative_ranks[-1],
        "maximum_scaled_coefficient_norm": float(max(scaled_norms)),
        "numerically_vanishing_through_cayley_hamilton": bool(
            max(scaled_norms) <= 1e-11 and maximum_order == state_count - 1
        ),
        "early_cumulative_ranks": cumulative_ranks[: min(8, len(cumulative_ranks))],
        "early_scaled_coefficient_norms": scaled_norms[
            : min(8, len(scaled_norms))
        ],
    }


def _markov_laplacian_audit(generator: np.ndarray) -> dict[str, object]:
    generator = np.asarray(generator, dtype=float)
    off_diagonal = generator - np.diag(np.diag(generator))
    return {
        "is_symmetric": bool(np.max(np.abs(generator - generator.T)) <= 1e-12),
        "symmetry_error": float(np.linalg.norm(generator - generator.T, ord="fro")),
        "maximum_off_diagonal_entry": float(np.max(off_diagonal)),
        "maximum_absolute_row_sum": float(np.max(np.abs(np.sum(generator, axis=1)))),
        "maximum_absolute_column_sum": float(
            np.max(np.abs(np.sum(generator, axis=0)))
        ),
        "is_markov_graph_laplacian": bool(
            np.max(off_diagonal) <= 1e-13
            and np.max(np.abs(np.sum(generator, axis=0))) <= 1e-12
        ),
    }


def directed_response_audit(
    left_laplacian: np.ndarray,
    right_laplacian: np.ndarray,
    observation_times: Sequence[float],
    reciprocal_strength: float = 0.4,
    directed_strength: float = 0.8,
) -> dict[str, object]:
    """Compare independent, reciprocal, and exactly one-way Markov controls."""
    left_count = len(left_laplacian)
    right_count = len(right_laplacian)
    if left_count != right_count:
        raise ValueError("the reference directional comparison uses equal factors")
    maps = localized_intervention_maps(left_count, right_count)
    independent = independent_generator(left_laplacian, right_laplacian)
    reciprocal = independent + reciprocal_strength * (
        diagonal_markov_interaction_laplacian(left_count, right_count)
    )
    directed = one_way_rate_modulation_generator(
        left_laplacian, right_laplacian, directed_strength
    )
    models = {
        "independent": independent,
        "reciprocal_diagonal_edge": reciprocal,
        "one_way_rate_modulation": directed,
    }
    rows: dict[str, object] = {}
    for name, generator in models.items():
        left_to_right = response_blocks(
            generator,
            maps["right_marginal"],
            maps["left_intervention"],
            observation_times,
        )
        right_to_left = response_blocks(
            generator,
            maps["left_marginal"],
            maps["right_intervention"],
            observation_times,
        )
        forward_norm = float(np.linalg.norm(np.vstack(left_to_right), ord="fro"))
        reverse_norm = float(np.linalg.norm(np.vstack(right_to_left), ord="fro"))
        denominator = forward_norm + reverse_norm
        rows[name] = {
            "generator_audit": _markov_laplacian_audit(generator),
            "A_to_B": response_summary(left_to_right),
            "B_to_A": response_summary(right_to_left),
            "signed_directionality_index": (
                0.0 if denominator <= 1e-14 else (forward_norm - reverse_norm) / denominator
            ),
            "causal_jets": {
                "A_to_B": causal_jet_audit(
                    generator,
                    maps["right_marginal"],
                    maps["left_intervention"],
                ),
                "B_to_A": causal_jet_audit(
                    generator,
                    maps["left_marginal"],
                    maps["right_intervention"],
                ),
            },
        }
    rows["exact_zero_certificates"] = {
        "independent_both_directions": (
            "semigroup factorization and zero-sum tangent interventions"
        ),
        "one_way_B_to_A": (
            "M_A L_arrow = L_A M_A, hence M_A exp(-t L_arrow) J_B = 0"
        ),
        "one_way_A_to_B_first_derivative": (
            "-g (1^T D_A B_A) tensor (L_B e_b), nonzero for the declared "
            "background and nonconstant modulation"
        ),
    }
    return rows


def _directed_graph_distances(transition: np.ndarray, source: int) -> np.ndarray:
    """Shortest directed distances for column-vector Markov evolution."""
    state_count = len(transition)
    distances = np.full(state_count, np.inf)
    distances[source] = 0.0
    queue: deque[int] = deque([source])
    while queue:
        current = queue.popleft()
        neighbors = np.flatnonzero(transition[:, current] > 1e-14)
        for neighbor in neighbors:
            if neighbor == current:
                continue
            if not np.isfinite(distances[neighbor]):
                distances[neighbor] = distances[current] + 1.0
                queue.append(int(neighbor))
    return distances


def uniformization_cone_audit(
    generator: np.ndarray,
    source: int,
    observation_times: Sequence[float] = (0.02, 0.05, 0.1, 0.2, 0.5, 1.0),
    leakage_tolerance: float = 0.01,
    reference_time: float = 0.2,
) -> dict[str, object]:
    """Compare exact propagated mass with the uniformization Poisson envelope."""
    generator = np.asarray(generator, dtype=float)
    state_count = len(generator)
    if generator.shape != (state_count, state_count) or not 0 <= source < state_count:
        raise ValueError("invalid generator or source")
    if not 0.0 < leakage_tolerance < 1.0:
        raise ValueError("leakage_tolerance must lie strictly between zero and one")
    rate = float(np.max(np.diag(generator)))
    if rate <= 0.0:
        raise ValueError("a nontrivial Markov generator is required")
    transition = np.eye(state_count) - generator / rate
    if np.min(transition) < -1e-13:
        raise ValueError("uniformized transition matrix is not nonnegative")
    distances = _directed_graph_distances(transition, source)
    if np.any(~np.isfinite(distances)):
        raise ValueError("the reference cone audit requires a reachable state graph")
    integer_distances = distances.astype(int)
    diameter_from_source = int(np.max(integer_distances))

    time_rows = []
    maximum_bound_violation = 0.0
    for time in observation_times:
        distribution = expm(-float(time) * generator)[:, source]
        actual_radius = diameter_from_source
        for radius in range(diameter_from_source + 1):
            leakage = float(np.sum(distribution[integer_distances > radius]))
            if leakage <= leakage_tolerance:
                actual_radius = radius
                break
        poisson_radius = 0
        mean = rate * float(time)
        while poisson.sf(poisson_radius, mean) > leakage_tolerance:
            poisson_radius += 1
        guaranteed_radius = min(poisson_radius, diameter_from_source)
        for threshold in range(1, diameter_from_source + 1):
            actual = float(np.sum(distribution[integer_distances >= threshold]))
            bound = float(poisson.sf(threshold - 1, mean))
            maximum_bound_violation = max(maximum_bound_violation, actual - bound)
        time_rows.append(
            {
                "time": float(time),
                "poisson_mean": mean,
                "actual_99_percent_radius": actual_radius,
                "poisson_99_percent_radius": poisson_radius,
                "graph_capped_guaranteed_radius": guaranteed_radius,
                "strictly_positive_state_count": int(np.sum(distribution > 0.0)),
                "minimum_transition_probability": float(np.min(distribution)),
            }
        )

    reference_distribution = expm(-reference_time * generator)[:, source]
    threshold_rows = []
    for threshold in range(1, diameter_from_source + 1):
        threshold_rows.append(
            {
                "minimum_graph_distance": threshold,
                "actual_mass": float(
                    np.sum(reference_distribution[integer_distances >= threshold])
                ),
                "poisson_tail_bound": float(
                    poisson.sf(threshold - 1, rate * reference_time)
                ),
            }
        )
    shells = [
        int(np.sum(integer_distances == distance))
        for distance in range(diameter_from_source + 1)
    ]
    return {
        "uniformization_rate": rate,
        "transition_minimum_entry": float(np.min(transition)),
        "transition_maximum_column_sum_error": float(
            np.max(np.abs(np.sum(transition, axis=0) - 1.0))
        ),
        "source_index": source,
        "source_graph_eccentricity": diameter_from_source,
        "distance_shell_state_counts": shells,
        "leakage_tolerance": leakage_tolerance,
        "effective_radius_by_time": time_rows,
        "reference_time": reference_time,
        "reference_tail_table": threshold_rows,
        "maximum_poisson_bound_violation": float(maximum_bound_violation),
        "strict_finite_cone": False,
        "interpretation": (
            "continuous time permits arbitrarily many jumps, so the cone is a "
            "Poisson-tail leakage envelope rather than an exact support cutoff"
        ),
    }


def passive_interventional_audit(
    generators: dict[str, np.ndarray],
    observation_times: Sequence[float],
    maps: dict[str, np.ndarray],
) -> dict[str, object]:
    """Contrast passive local reconstruction with directed response channels."""
    local_sensor = np.vstack([maps["left_marginal"], maps["right_marginal"]])
    state_count = next(iter(generators.values())).shape[0]
    probability_tangent = mixture_tangent_basis(state_count)
    rows = {}
    for name, generator in generators.items():
        passive = np.vstack(
            [local_sensor @ expm(-float(time) * generator) for time in observation_times]
        )
        passive_rank = _rank_condition(passive)
        tangent_rank = _rank_condition(passive @ probability_tangent)
        forward = np.vstack(
            response_blocks(
                generator,
                maps["right_marginal"],
                maps["left_intervention"],
                observation_times,
            )
        )
        reverse = np.vstack(
            response_blocks(
                generator,
                maps["left_marginal"],
                maps["right_intervention"],
                observation_times,
            )
        )
        rows[name] = {
            "passive_local_history_rank": passive_rank["rank"],
            "passive_blind_dimension": int(
                generator.shape[0] - int(passive_rank["rank"])
            ),
            "passive_minimum_active_singular_value": passive_rank[
                "minimum_active_singular_value"
            ],
            "passive_active_subspace_condition_number": passive_rank[
                "active_subspace_condition_number"
            ],
            "probability_tangent_history_rank": tangent_rank["rank"],
            "probability_tangent_blind_dimension": int(
                state_count - 1 - int(tangent_rank["rank"])
            ),
            "probability_tangent_minimum_singular_value": tangent_rank[
                "minimum_active_singular_value"
            ],
            "probability_tangent_condition_number": tangent_rank[
                "active_subspace_condition_number"
            ],
            "A_to_B_interventional_rank": _rank_condition(forward)["rank"],
            "B_to_A_interventional_rank": _rank_condition(reverse)["rank"],
        }
    return rows


def _relative_response_dilation(
    reference_gram: np.ndarray, candidate_gram: np.ndarray
) -> float | None:
    values, vectors = np.linalg.eigh(reference_gram)
    if values[0] <= 0.0:
        raise ValueError("reference response Gram must be positive definite")
    inverse_root = (vectors * (1.0 / np.sqrt(values))) @ vectors.T
    relative_values = np.linalg.eigvalsh(
        inverse_root @ candidate_gram @ inverse_root
    )
    if relative_values[0] <= 1e-10:
        return None
    return float(math.sqrt(relative_values[-1] / relative_values[0]))


def protocol_invariance_audit(
    generator: np.ndarray,
    measurement: np.ndarray,
    intervention: np.ndarray,
    observation_times: Sequence[float],
    channel_counts: Sequence[int] = (1, 2, 3, 4, 6),
    seed_count: int = 32,
) -> dict[str, object]:
    """Test response geometry under repeated and refreshed sensor compression."""
    blocks = response_blocks(
        generator, measurement, intervention, observation_times
    )
    complete_history = np.vstack(blocks)
    reference_gram = complete_history.T @ complete_history
    reference_rank = _rank_condition(complete_history)
    output_count = blocks[0].shape[0]
    rows = []
    for channel_count in channel_counts:
        if not 1 <= channel_count <= output_count:
            raise ValueError("invalid compressed channel count")
        for refreshed in (False, True):
            dilations = []
            full_rank_count = 0
            for seed in range(seed_count):
                rng = np.random.default_rng(seed)

                def sample_sensor() -> np.ndarray:
                    return rng.choice(
                        [-1.0, 1.0], size=(channel_count, output_count)
                    ) / math.sqrt(channel_count)

                repeated_sensor = None if refreshed else sample_sensor()
                compressed_blocks = []
                for block in blocks:
                    sensor = sample_sensor() if refreshed else repeated_sensor
                    compressed_blocks.append(sensor @ block)
                compressed = np.vstack(compressed_blocks)
                if _rank_condition(compressed)["rank"] == intervention.shape[1]:
                    full_rank_count += 1
                candidate_gram = compressed.T @ compressed
                dilation = _relative_response_dilation(
                    reference_gram, candidate_gram
                )
                if dilation is not None:
                    dilations.append(dilation)
            rows.append(
                {
                    "channels_per_time": int(channel_count),
                    "sensor_refresh": "independent_each_time" if refreshed else "repeated",
                    "full_rank_fraction": full_rank_count / seed_count,
                    "finite_dilation_fraction": len(dilations) / seed_count,
                    "median_scale_free_response_dilation": (
                        float(np.median(dilations)) if dilations else None
                    ),
                    "ninety_percentile_scale_free_response_dilation": (
                        float(np.quantile(dilations, 0.9)) if dilations else None
                    ),
                }
            )
    return {
        "reference_response_rank": reference_rank["rank"],
        "reference_response_gram_condition_number": float(
            np.linalg.cond(reference_gram)
        ),
        "random_seed_count": seed_count,
        "protocol_rows": rows,
        "interpretation": (
            "sufficiently rich compressed protocols preserve the directed "
            "response subspace up to finite distortion; refreshing sparse "
            "sensors improves the worst bottleneck"
        ),
    }


def intervention_background_audit(
    generator: np.ndarray,
    left_state_count: int,
    right_state_count: int,
    observation_times: Sequence[float],
) -> dict[str, object]:
    """Test whether the directed channel persists across target backgrounds."""
    pure_rows = []
    for right_background in range(right_state_count):
        maps = localized_intervention_maps(
            left_state_count,
            right_state_count,
            right_background=right_background,
        )
        history = np.vstack(
            response_blocks(
                generator,
                maps["right_marginal"],
                maps["left_intervention"],
                observation_times,
            )
        )
        rank = _rank_condition(history)
        pure_rows.append(
            {
                "right_background_state": right_background,
                "response_norm": float(np.linalg.norm(history, ord="fro")),
                "response_rank": rank["rank"],
                "minimum_singular_value": rank["minimum_active_singular_value"],
                "response_condition_number": rank[
                    "active_subspace_condition_number"
                ],
            }
        )

    left_basis = mixture_tangent_basis(left_state_count)
    stationary_right = np.ones((right_state_count, 1)) / right_state_count
    stationary_intervention = np.kron(left_basis, stationary_right)
    _, right_marginal, _ = marginal_measurements(
        left_state_count, right_state_count
    )
    stationary_history = np.vstack(
        response_blocks(
            generator,
            right_marginal,
            stationary_intervention,
            observation_times,
        )
    )
    return {
        "pure_target_backgrounds": pure_rows,
        "all_pure_backgrounds_have_full_forward_rank": bool(
            all(row["response_rank"] == left_state_count - 1 for row in pure_rows)
        ),
        "stationary_uniform_target_background": {
            "response_norm": float(np.linalg.norm(stationary_history, ord="fro")),
            "response_rank": _rank_condition(stationary_history)["rank"],
        },
        "interpretation": (
            "the structural arrow means B never influences A and A can "
            "influence B; endpoint B marginals are silent when the A "
            "intervention is tensorized with a stationary B profile"
        ),
    }


def positive_multiscale_response_design(
    generator: np.ndarray,
    measurement: np.ndarray,
    intervention: np.ndarray,
    candidate_times: Sequence[float] | None = None,
    dyadic_denominator: int = 4096,
) -> dict[str, object]:
    """Design positive time weights for the weakest response direction.

    This solves a floating E-optimal design over a declared finite time grid,
    rounds the result to dyadic weights, audits every candidate time, and builds
    a floating dual upper witness in the computed two-dimensional minimum
    eigenspace.  It is not an outward-rounded interval certificate.
    """
    using_reference_grid = candidate_times is None
    if using_reference_grid:
        times = stage_iv_reference_time_grid()
    else:
        times = np.asarray(candidate_times, dtype=float)
    if times.ndim != 1 or len(times) < 2 or np.any(times <= 0.0):
        raise ValueError("at least two positive candidate times are required")
    if dyadic_denominator < 1:
        raise ValueError("dyadic_denominator must be positive")
    blocks = response_blocks(generator, measurement, intervention, times)
    information = np.asarray([block.T @ block for block in blocks])
    candidate_count = len(times)
    objective_scale = 1e9

    def objective_and_gradient(weights: np.ndarray) -> tuple[float, np.ndarray]:
        gram = np.tensordot(weights, information, axes=(0, 0))
        values, vectors = np.linalg.eigh(gram)
        weakest = vectors[:, 0]
        gradient = np.einsum(
            "i,tij,j->t", weakest, information, weakest
        )
        return -objective_scale * float(values[0]), -objective_scale * gradient

    if using_reference_grid and dyadic_denominator == 4096:
        # A certified feasible design is a stable warm start for the nonsmooth
        # minimum-eigenvalue objective.  A uniform start can stall in some
        # SciPy SLSQP releases even though the mathematical problem is fixed.
        initial = np.asarray(
            [
                STAGE_IV_REFERENCE_DYADIC_NUMERATORS.get(index, 0)
                / dyadic_denominator
                for index in range(candidate_count)
            ]
        )
    else:
        initial = np.ones(candidate_count) / candidate_count
    primal = minimize(
        lambda weights: objective_and_gradient(weights)[0],
        initial,
        jac=lambda weights: objective_and_gradient(weights)[1],
        method="SLSQP",
        bounds=[(0.0, 1.0)] * candidate_count,
        constraints=[
            {
                "type": "eq",
                "fun": lambda weights: float(np.sum(weights) - 1.0),
                "jac": lambda weights: np.ones(candidate_count),
            }
        ],
        options={"ftol": 1e-12, "maxiter": 5000},
    )
    if not primal.success:
        raise RuntimeError(f"response design failed: {primal.message}")
    weights = np.maximum(primal.x, 0.0)
    weights /= np.sum(weights)
    gram = np.tensordot(weights, information, axes=(0, 0))
    eigenvalues, eigenvectors = np.linalg.eigh(gram)
    primal_floor = float(eigenvalues[0])

    # Construct a dual witness Z=V H V^T, with tr(H)=1 and H positive.
    # For every design w, lambda_min(G(w)) <= tr(ZG(w)) <= mu if
    # tr(ZA_t)<=mu for every candidate information matrix A_t.
    weak_vectors = eigenvectors[:, :2]
    restricted = np.einsum(
        "ia,tij,jb->tab", weak_vectors, information, weak_vectors
    )
    restricted_scaled = objective_scale * restricted

    def dual_sensitivities(candidate: np.ndarray) -> np.ndarray:
        first, cross, _ = candidate
        return (
            first * restricted_scaled[:, 0, 0]
            + 2.0 * cross * restricted_scaled[:, 0, 1]
            + (1.0 - first) * restricted_scaled[:, 1, 1]
        )

    dual = minimize(
        lambda candidate: candidate[2],
        np.asarray([0.5, 0.0, -primal.fun]),
        method="SLSQP",
        bounds=[(0.0, 1.0), (-0.5, 0.5), (0.0, None)],
        constraints=[
            {
                "type": "ineq",
                "fun": lambda candidate: (
                    candidate[2] - dual_sensitivities(candidate)
                ),
            },
            {
                "type": "ineq",
                "fun": lambda candidate: (
                    candidate[0] * (1.0 - candidate[0])
                    - candidate[1] ** 2
                ),
            },
        ],
        options={"ftol": 1e-13, "maxiter": 10000},
    )
    if not dual.success:
        raise RuntimeError(f"response design dual audit failed: {dual.message}")
    maximum_dual_sensitivity = float(np.max(dual_sensitivities(dual.x)))
    dual_upper = max(float(dual.x[2]), maximum_dual_sensitivity) / objective_scale
    dual_matrix = np.asarray(
        [[dual.x[0], dual.x[1]], [dual.x[1], 1.0 - dual.x[0]]]
    )

    raw_numerators = weights * dyadic_denominator
    numerators = np.floor(raw_numerators).astype(int)
    remainder = dyadic_denominator - int(np.sum(numerators))
    rounding_order = np.argsort(raw_numerators - numerators)[::-1]
    numerators[rounding_order[:remainder]] += 1
    dyadic_weights = numerators / dyadic_denominator
    dyadic_gram = np.tensordot(dyadic_weights, information, axes=(0, 0))
    dyadic_eigenvalues = np.linalg.eigvalsh(dyadic_gram)
    # Squaring the smallest singular value of each response block is more
    # accurate here than diagonalizing its extremely ill-conditioned Gram.
    single_floors = np.asarray(
        [np.linalg.svd(block, compute_uv=False)[-1] ** 2 for block in blocks]
    )
    uniform_floor = float(
        np.linalg.eigvalsh(np.mean(information, axis=0))[0]
    )
    active = np.flatnonzero(numerators)
    return {
        "criterion": (
            "maximize the weakest eigenvalue of the positively weighted "
            "A-to-B response Gram over the declared finite time grid"
        ),
        "candidate_time_count": candidate_count,
        "candidate_time_minimum": float(times[0]),
        "candidate_time_maximum": float(times[-1]),
        "floating_primal_floor": primal_floor,
        "floating_dual_upper_bound": dual_upper,
        "relative_primal_dual_gap": float(
            (dual_upper - primal_floor) / primal_floor
        ),
        "dual_two_by_two_minimum_eigenvalue": float(
            np.linalg.eigvalsh(dual_matrix)[0]
        ),
        "maximum_dual_constraint_excess": float(
            max(0.0, maximum_dual_sensitivity - float(dual.x[2]))
            / objective_scale
        ),
        "dyadic_denominator": dyadic_denominator,
        "dyadic_active_times": [float(times[index]) for index in active],
        "dyadic_active_numerators": [int(numerators[index]) for index in active],
        "dyadic_floor": float(dyadic_eigenvalues[0]),
        "dyadic_fraction_of_floating_upper_bound": float(
            dyadic_eigenvalues[0] / dual_upper
        ),
        "dyadic_gram_condition_number": float(
            dyadic_eigenvalues[-1] / dyadic_eigenvalues[0]
        ),
        "uniform_candidate_grid_floor": uniform_floor,
        "dyadic_improvement_over_uniform_grid": float(
            dyadic_eigenvalues[0] / uniform_floor
        ),
        "best_single_time": float(times[int(np.argmax(single_floors))]),
        "best_single_time_floor": float(np.max(single_floors)),
        "dyadic_improvement_over_best_single_time": float(
            dyadic_eigenvalues[0] / np.max(single_floors)
        ),
        "certificate_scope": (
            "finite-grid floating primal/dual audit with exact dyadic primal "
            "weights; the separate oig_iv_certificate.py checker supplies an "
            "outward-rounded rational/Arb certificate"
        ),
    }


def run_stage_4_experiment(
    reciprocal_strength: float = 0.4,
    directed_strength: float = 0.8,
    protocol_seeds: int = 32,
) -> dict[str, object]:
    """Run the Stage IV intervention, jet, propagation, and protocol audits."""
    left = factorization_universe((2,), 6)
    right = factorization_universe((3,), 6)
    times = np.geomspace(0.01, 2.0, 20)
    independent = independent_generator(left.laplacian, right.laplacian)
    reciprocal = independent + reciprocal_strength * (
        diagonal_markov_interaction_laplacian(6, 6)
    )
    directed = one_way_rate_modulation_generator(
        left.laplacian, right.laplacian, directed_strength
    )
    maps = localized_intervention_maps(6, 6)
    return {
        "model": "interventional operational geometry on two six-state factors",
        "scope": (
            "finite linear Markov toy model; directed response is relative to "
            "the declared subsystem partition, interventions, and measurements; "
            "no claim about relativistic causality or fundamental physics"
        ),
        "parameters": {
            "left_states": 6,
            "right_states": 6,
            "composite_states": 36,
            "reciprocal_strength": reciprocal_strength,
            "directed_strength": directed_strength,
            "observation_times": times.tolist(),
            "protocol_seed_count": protocol_seeds,
        },
        "directed_response": directed_response_audit(
            left.laplacian,
            right.laplacian,
            times,
            reciprocal_strength,
            directed_strength,
        ),
        "passive_vs_interventional": passive_interventional_audit(
            {
                "independent": independent,
                "reciprocal_diagonal_edge": reciprocal,
                "one_way_rate_modulation": directed,
            },
            times,
            maps,
        ),
        "uniformization_causal_cone": uniformization_cone_audit(
            directed, source=2 * 6 + 2
        ),
        "compressed_protocol_invariance": protocol_invariance_audit(
            directed,
            maps["right_marginal"],
            maps["left_intervention"],
            times,
            seed_count=protocol_seeds,
        ),
        "intervention_background_robustness": intervention_background_audit(
            directed, 6, 6, times
        ),
        "positive_multiscale_response_design": positive_multiscale_response_design(
            directed,
            maps["right_marginal"],
            maps["left_intervention"],
        ),
        "adjacent_multiscale_certificate_decision": {
            "required_for_stage_iv": False,
            "reason": (
                "the Stage IV theorems use exact matrix identities, a complete "
                "Cayley-Hamilton jet, and a uniformization tail; none depends "
                "on Stage III's optimized four-scale design"
            ),
            "new_adjacent_results_pursued_instead": [
                "finite causal-jet vanishing and rank certificate",
                (
                    "finite-grid E-optimal response schedule with a dyadic "
                    "primal design and floating dual upper witness"
                ),
            ],
        },
        "falsification_readout": {
            "zero_coupling_control": (
                "independent dynamics has zero cross-response in both directions"
            ),
            "reciprocal_control": (
                "the diagonal-edge interaction activates both cross-directions"
            ),
            "directional_result": (
                "the rate-modulation generator is symmetric and Markov, yet its "
                "declared subsystem response is exactly A-to-B only"
            ),
            "cone_boundary": (
                "continuous-time propagation has no strict graph cone, but all "
                "measured leakage obeys the exact Poisson uniformization bound"
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reciprocal-strength", type=float, default=0.4)
    parser.add_argument("--directed-strength", type=float, default=0.8)
    parser.add_argument("--protocol-seeds", type=int, default=32)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    print(
        json.dumps(
            run_stage_4_experiment(
                arguments.reciprocal_strength,
                arguments.directed_strength,
                arguments.protocol_seeds,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
