#!/usr/bin/env python3
"""Tier-1 grouped double-pendulum protocols with shared clock nuisance.

The seven scalar candidates already used by the double-pendulum adapter are
batched by their exact launch.  A batch is one grouped protocol: all of its
declared sensor/time readouts are acquired together and receive one common
repetition weight.  Across every active group the scheduling error is one
shared log clock dilation ``epsilon``,

    tau_actual = exp(epsilon) tau_declared,

so the nuisance derivative of a scalar readout is ``tau * d y / d tau``.
The two query coordinates remain

    u = log(m2/m1),    v = log(l2/l1).

State, analytic parameter sensitivities, and clock rows are computed by the
dimensionless variational model.  They are refined numerically and then
rounded to fixed rational point declarations.  The existing exact query
engine proves positive nuisance-profiled floors for those finite rational
declarations.  No result here outwardly encloses the nonlinear ODE, its
parameter derivative, or its clock derivative.

Preparation is exact in this first constructive milestone.  Initial-state
errors are neither hidden nor profiled; adding them changes the model and is
left to a separately bounded or independently observed preparation layer.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
import json
import math
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

from double_pendulum_dynamics import IntegrationConfig
from oig_double_pendulum_parameter_sensitivity import (
    dimensionless_rhs,
    simulate_log_ratio_sensitivities,
)
from oig_double_pendulum_protocol import (
    PendulumProtocolCandidate,
    canonical_protocol_candidates,
)
from oig_query_protocol_design import (
    QueryProtocol,
    certify_query_protocol_mixture,
    verify_query_protocol_report,
)


Q = Fraction
SCHEMA_VERSION = "oig-double-pendulum-grouped-protocol-v1"
TIER_1_SCOPE = "tier_1_analytic_variational_numerics_not_outward_validated"
DECLARATION_DENOMINATOR = 1_000_000
SEARCH_DENOMINATOR = 12
SOURCE_COORDINATES = (
    "u=log(m2/m1)",
    "v=log(l2/l1)",
)

COARSE_INTEGRATION = IntegrationConfig(
    rtol=1.0e-10,
    atol=1.0e-12,
    max_step=0.01,
    energy_drift_tolerance=1.0e-9,
)
FINE_INTEGRATION = IntegrationConfig(
    rtol=1.0e-12,
    atol=1.0e-14,
    max_step=0.005,
    energy_drift_tolerance=1.0e-9,
)
REFINEMENT_GATES = {
    "state_relative": 1.0e-9,
    "parameter_sensitivity_relative": 1.0e-8,
    "clock_state_vector_relative": 1.0e-8,
    "point_rationalization_absolute": 5.1e-7,
}

GROUP_DEFINITIONS = (
    (
        "launch-A grouped trajectory",
        (
            "launch-A / theta-1 / tau-1",
            "launch-A / theta-2 / tau-1",
            "launch-A / scaled-omega-2 / tau-3/2",
        ),
    ),
    (
        "launch-B grouped trajectory",
        (
            "launch-B / theta-1 / tau-3/4",
            "launch-B / scaled-omega-1 / tau-5/4",
        ),
    ),
    (
        "launch-C grouped trajectory",
        (
            "launch-C / theta-2 / tau-1",
            "launch-C / scaled-omega-2 / tau-3/2",
        ),
    ),
)

PROOF_BOUNDARY = (
    "The analytic inhomogeneous parameter-sensitivity solve, state solve, clock "
    "chain rule, solver refinement, and fixed-grid rationalization are Tier-1 "
    "numerical provenance. The exact query children prove finite rational linear "
    "statements only for the serialized point declarations. They do not prove "
    "that the exact double-pendulum flow or any physical response belongs to "
    "those declarations, and they do not include launch-preparation error."
)

GROUPING_SEMANTICS = (
    "Each group fixes one exact launch and collects every listed sensor/time "
    "readout as one inseparable batch. A budget share p_g and conservative "
    "additive group cost c_g give repetition weight p_g/c_g on the entire "
    "within-group output metric. One clock-dilation parameter is global across "
    "all repetitions, observations, and active group types and is profiled only "
    "after stacking."
)

COMMON_GAIN_SCOPE = (
    "Secondary optimistic control: one log multiplicative gain is shared by "
    "every dimensionless output, even across angle and scaled-velocity channels. "
    "It is not a sensor-specific calibration model."
)

_SENSOR_INDEX = {
    "theta_1": 0,
    "theta_2": 1,
    "scaled_omega_1": 2,
    "scaled_omega_2": 3,
}


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _vector_text(values: Sequence[Fraction]) -> list[str]:
    return [_fraction_text(value) for value in values]


def _matrix_text(values: Sequence[Sequence[Fraction]]) -> list[list[str]]:
    return [_vector_text(row) for row in values]


def _strict_json_equal(left: object, right: object) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            _strict_json_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            _strict_json_equal(a, b) for a, b in zip(left, right)
        )
    return left == right


def _quantize(value: float) -> Fraction:
    if not math.isfinite(float(value)):
        raise ValueError("cannot rationalize a non-finite value")
    return Q(int(round(float(value) * DECLARATION_DENOMINATOR)), DECLARATION_DENOMINATOR)


def _relative_discrepancy(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.linalg.norm(left - right) / max(1.0, float(np.linalg.norm(right))))


def _integration_record(config: IntegrationConfig) -> dict[str, object]:
    return {
        "method": "DOP853 joint dimensionless state/parameter-sensitivity integration",
        "rtol": config.rtol,
        "atol": config.atol,
        "max_step_in_tau": config.max_step,
        "sampled_scaled_energy_drift_tolerance": config.energy_drift_tolerance,
    }


def _candidate_record(
    candidate: PendulumProtocolCandidate,
    config: IntegrationConfig,
) -> dict[str, object]:
    tau = float(candidate.observation_time_tau)
    launch = np.asarray([float(value) for value in candidate.launch], dtype=float)
    trajectory = simulate_log_ratio_sensitivities(
        launch,
        [0.0, tau],
        log_mass_ratio=0.0,
        log_length_ratio=0.0,
        integration=config,
    )
    state = np.asarray(trajectory.states[-1], dtype=float)
    sensitivity = np.asarray(trajectory.sensitivities[-1], dtype=float)
    rhs = np.asarray(dimensionless_rhs(tau, state, 0.0, 0.0), dtype=float)
    clock_vector = tau * rhs
    sensor_index = _SENSOR_INDEX[candidate.sensor]
    return {
        "terminal_state": state.tolist(),
        "terminal_parameter_sensitivity_D_state_D_uv": sensitivity.tolist(),
        "terminal_rhs_D_state_D_tau": rhs.tolist(),
        "clock_log_dilation_state_response_tau_times_rhs": clock_vector.tolist(),
        "selected_sensor_output": float(state[sensor_index]),
        "selected_parameter_response_row": sensitivity[sensor_index].tolist(),
        "selected_clock_response": float(clock_vector[sensor_index]),
        "selected_common_gain_response": float(state[sensor_index]),
        "max_scaled_energy_drift": float(trajectory.max_scaled_energy_drift),
        "accepted_step_count": int(trajectory.accepted_step_count),
        "nfev": int(trajectory.nfev),
    }


def _observation_records() -> tuple[list[dict[str, object]], tuple[PendulumProtocolCandidate, ...]]:
    candidates = canonical_protocol_candidates()
    records: list[dict[str, object]] = []
    for candidate in candidates:
        coarse = _candidate_record(candidate, COARSE_INTEGRATION)
        fine = _candidate_record(candidate, FINE_INTEGRATION)
        coarse_state = np.asarray(coarse["terminal_state"], dtype=float)
        fine_state = np.asarray(fine["terminal_state"], dtype=float)
        coarse_sensitivity = np.asarray(
            coarse["terminal_parameter_sensitivity_D_state_D_uv"], dtype=float
        )
        fine_sensitivity = np.asarray(
            fine["terminal_parameter_sensitivity_D_state_D_uv"], dtype=float
        )
        coarse_clock = np.asarray(
            coarse["clock_log_dilation_state_response_tau_times_rhs"], dtype=float
        )
        fine_clock = np.asarray(
            fine["clock_log_dilation_state_response_tau_times_rhs"], dtype=float
        )
        discrepancies = {
            "state_relative": _relative_discrepancy(coarse_state, fine_state),
            "parameter_sensitivity_relative": _relative_discrepancy(
                coarse_sensitivity, fine_sensitivity
            ),
            "clock_state_vector_relative": _relative_discrepancy(coarse_clock, fine_clock),
        }
        response_float = tuple(float(value) for value in fine["selected_parameter_response_row"])
        clock_float = float(fine["selected_clock_response"])
        gain_float = float(fine["selected_common_gain_response"])
        response_exact = tuple(_quantize(value) for value in response_float)
        clock_exact = _quantize(clock_float)
        gain_exact = _quantize(gain_float)
        errors = {
            "parameter_response": [
                abs(value - float(exact))
                for value, exact in zip(response_float, response_exact)
            ],
            "clock_response": abs(clock_float - float(clock_exact)),
            "common_gain_response": abs(gain_float - float(gain_exact)),
        }
        maximum_error = max(
            *errors["parameter_response"],
            errors["clock_response"],
            errors["common_gain_response"],
        )
        gates_passed = bool(
            discrepancies["state_relative"] <= REFINEMENT_GATES["state_relative"]
            and discrepancies["parameter_sensitivity_relative"]
            <= REFINEMENT_GATES["parameter_sensitivity_relative"]
            and discrepancies["clock_state_vector_relative"]
            <= REFINEMENT_GATES["clock_state_vector_relative"]
            and maximum_error <= REFINEMENT_GATES["point_rationalization_absolute"]
            and float(coarse["max_scaled_energy_drift"])
            <= COARSE_INTEGRATION.energy_drift_tolerance
            and float(fine["max_scaled_energy_drift"])
            <= FINE_INTEGRATION.energy_drift_tolerance
        )
        records.append(
            {
                "name": candidate.name,
                "launch_exact": _vector_text(candidate.launch),
                "sensor": candidate.sensor,
                "sensor_state_index": _SENSOR_INDEX[candidate.sensor],
                "observation_time_tau_exact": _fraction_text(
                    candidate.observation_time_tau
                ),
                "noise_precision_exact": _fraction_text(candidate.noise_precision),
                "legacy_scalar_cost_exact": _fraction_text(candidate.cost),
                "coarse": coarse,
                "fine": fine,
                "refinement_discrepancies": discrepancies,
                "declared_rational_point": {
                    "parameter_response_exact": _vector_text(response_exact),
                    "clock_response_exact": _fraction_text(clock_exact),
                    "common_gain_response_exact": _fraction_text(gain_exact),
                    "fixed_denominator_before_reduction": DECLARATION_DENOMINATOR,
                    "absolute_errors": errors,
                    "status": "conditional rational point; not an ODE enclosure",
                },
                "tier1_controls_passed": gates_passed,
            }
        )
    return records, candidates


@dataclass(frozen=True)
class _GroupedPoint:
    name: str
    member_names: tuple[str, ...]
    response: tuple[tuple[Fraction, Fraction], ...]
    clock: tuple[Fraction, ...]
    gain: tuple[Fraction, ...]
    output_metric: tuple[tuple[Fraction, ...], ...]
    cost: Fraction


def _identity_metric(precisions: Sequence[Fraction]) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(precision if row == column else Q(0) for column in range(len(precisions)))
        for row, precision in enumerate(precisions)
    )


def _group_records(
    observations: Sequence[dict[str, object]],
    candidates: Sequence[PendulumProtocolCandidate],
) -> tuple[list[dict[str, object]], tuple[_GroupedPoint, ...]]:
    by_name = {candidate.name: (candidate, observations[index]) for index, candidate in enumerate(candidates)}
    records: list[dict[str, object]] = []
    points: list[_GroupedPoint] = []
    for name, member_names in GROUP_DEFINITIONS:
        selected = [by_name[member_name] for member_name in member_names]
        launch = selected[0][0].launch
        if any(candidate.launch != launch for candidate, _ in selected):
            raise RuntimeError("group members do not share one exact launch")
        response = tuple(
            tuple(Q(value) for value in record["declared_rational_point"]["parameter_response_exact"])
            for _, record in selected
        )
        clock = tuple(
            Q(record["declared_rational_point"]["clock_response_exact"])
            for _, record in selected
        )
        gain = tuple(
            Q(record["declared_rational_point"]["common_gain_response_exact"])
            for _, record in selected
        )
        precisions = tuple(candidate.noise_precision for candidate, _ in selected)
        metric = _identity_metric(precisions)
        cost = sum((candidate.cost for candidate, _ in selected), Q(0))
        point = _GroupedPoint(
            name=name,
            member_names=tuple(member_names),
            response=response,  # type: ignore[arg-type]
            clock=clock,
            gain=gain,
            output_metric=metric,
            cost=cost,
        )
        points.append(point)
        times = tuple(candidate.observation_time_tau for candidate, _ in selected)
        sensors = tuple(candidate.sensor for candidate, _ in selected)
        records.append(
            {
                "name": name,
                "launch_exact": _vector_text(launch),
                "member_names": list(member_names),
                "output_count": len(member_names),
                "distinct_time_count": len(set(times)),
                "distinct_sensor_count": len(set(sensors)),
                "is_multi_time": len(set(times)) > 1,
                "is_multi_sensor": len(set(sensors)) > 1,
                "response_exact": _matrix_text(response),
                "shared_clock_nuisance_response_exact": _matrix_text(
                    tuple((value,) for value in clock)
                ),
                "shared_clock_and_common_gain_nuisance_response_exact": _matrix_text(
                    tuple((clock_value, gain_value) for clock_value, gain_value in zip(clock, gain))
                ),
                "output_metric_exact": _matrix_text(metric),
                "group_cost_exact": _fraction_text(cost),
                "cost_rule": (
                    "conservative sum of legacy scalar-candidate costs; no shared-run discount"
                ),
                "batch_repetition_semantics": (
                    "one repetition acquires every member output and scales the whole "
                    "group output metric by one physical repetition weight"
                ),
            }
        )
    return records, tuple(points)


def _rank(matrix: Sequence[Sequence[Fraction]]) -> int:
    if not matrix:
        return 0
    work = [list(row) for row in matrix]
    rows = len(work)
    columns = len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [value / divisor for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    value - factor * reference
                    for value, reference in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def _nuisance_rows(group: _GroupedPoint, include_common_gain: bool) -> tuple[tuple[Fraction, ...], ...]:
    if include_common_gain:
        return tuple((clock, gain) for clock, gain in zip(group.clock, group.gain))
    return tuple((clock,) for clock in group.clock)


def _all_budget_shares(denominator: int) -> Iterable[tuple[Fraction, Fraction, Fraction]]:
    for first in range(denominator + 1):
        for second in range(denominator - first + 1):
            third = denominator - first - second
            yield (Q(first, denominator), Q(second, denominator), Q(third, denominator))


def _profiled_floor_estimate(
    groups: Sequence[_GroupedPoint],
    shares: Sequence[Fraction],
    *,
    include_common_gain: bool,
) -> tuple[float, int, int, int]:
    active = [index for index, share in enumerate(shares) if share > 0]
    response_exact = tuple(row for index in active for row in groups[index].response)
    nuisance_exact = tuple(
        row
        for index in active
        for row in _nuisance_rows(groups[index], include_common_gain)
    )
    nuisance_rank = _rank(nuisance_exact)
    augmented = tuple(
        tuple(nuisance_row) + tuple(response_row)
        for nuisance_row, response_row in zip(nuisance_exact, response_exact)
    )
    effective_rank = _rank(augmented) - nuisance_rank
    output_count = len(response_exact)

    response = np.asarray(response_exact, dtype=float)
    nuisance = np.asarray(nuisance_exact, dtype=float)
    weights: list[float] = []
    for index in active:
        group = groups[index]
        physical_weight = float(shares[index] / group.cost)
        weights.extend(
            physical_weight * float(group.output_metric[row][row])
            for row in range(len(group.response))
        )
    square_root_weight = np.sqrt(np.asarray(weights, dtype=float))
    weighted_response = square_root_weight[:, None] * response
    weighted_nuisance = square_root_weight[:, None] * nuisance
    if weighted_nuisance.size:
        u, singular_values, _ = np.linalg.svd(weighted_nuisance, full_matrices=False)
        tolerance = max(weighted_nuisance.shape) * np.finfo(float).eps * singular_values[0]
        numerical_rank = int(np.count_nonzero(singular_values > tolerance))
        basis = u[:, :numerical_rank]
        effective = weighted_response - basis @ (basis.T @ weighted_response)
    else:
        effective = weighted_response
    information = effective.T @ effective
    estimate = float(np.linalg.eigvalsh(0.5 * (information + information.T))[0])
    if effective_rank < 2:
        estimate = 0.0
    elif estimate < 0.0 and abs(estimate) <= 1.0e-12:
        estimate = 0.0
    return estimate, effective_rank, nuisance_rank, output_count


def _search_grid(
    groups: Sequence[_GroupedPoint],
    *,
    include_common_gain: bool,
) -> dict[str, object]:
    evaluations: list[dict[str, object]] = []
    for shares in _all_budget_shares(SEARCH_DENOMINATOR):
        estimate, effective_rank, nuisance_rank, output_count = _profiled_floor_estimate(
            groups, shares, include_common_gain=include_common_gain
        )
        evaluations.append(
            {
                "budget_shares_exact": _vector_text(shares),
                "active_group_indices": [index for index, share in enumerate(shares) if share > 0],
                "active_output_count": output_count,
                "nuisance_rank_exact": nuisance_rank,
                "effective_response_rank_exact": effective_rank,
                "descriptive_profiled_floor_estimate": estimate,
            }
        )
    selected_index = max(
        range(len(evaluations)),
        key=lambda index: evaluations[index]["descriptive_profiled_floor_estimate"],
    )
    selected = evaluations[selected_index]
    leaderboard = sorted(
        evaluations,
        key=lambda record: record["descriptive_profiled_floor_estimate"],
        reverse=True,
    )[:10]
    return {
        "nuisance_model": (
            "one shared clock dilation plus one optimistic shared common gain"
            if include_common_gain
            else "one shared clock dilation"
        ),
        "grid_denominator": SEARCH_DENOMINATOR,
        "enumeration_rule": (
            "all nonnegative three-group budget shares with integer numerators "
            "summing to the grid denominator"
        ),
        "evaluated_share_count": len(evaluations),
        "score": (
            "smallest eigenvalue of the numerically profiled information form "
            "for the fixed rational point declarations and cost weights p_g/c_g"
        ),
        "ordering_status": (
            "deterministic binary64 discovery ordering; selected design receives "
            "a separate exact query-engine certificate, but grid optimality is not "
            "claimed as an exact theorem"
        ),
        "selected_evaluation_index": selected_index,
        "selected": selected,
        "leaderboard": leaderboard,
        "evaluations": evaluations,
    }


def _query_protocols(
    groups: Sequence[_GroupedPoint],
    *,
    include_common_gain: bool,
) -> tuple[QueryProtocol, ...]:
    return tuple(
        QueryProtocol.from_rows(
            group.name,
            group.response,
            _nuisance_rows(group, include_common_gain),
            group.output_metric,
            cost=group.cost,
        )
        for group in groups
    )


def _query_child(
    groups: Sequence[_GroupedPoint],
    shares: Sequence[Fraction],
    *,
    include_common_gain: bool,
) -> dict[str, object]:
    return certify_query_protocol_mixture(
        _query_protocols(groups, include_common_gain=include_common_gain),
        shares,
        [[1, 0], [0, 1]],
        [[1, 0], [0, 1]],
        [[1, 0], [0, 1]],
    )


def _floor_record(child: dict[str, object]) -> dict[str, object]:
    factorization = child["factorization_and_minimax"]
    if factorization["kind"] != "identifiable-query-factorization":
        raise ValueError("the selected grouped protocol does not identify both queries")
    amplification_lower = Q(factorization["minimax_amplification_squared_lower_exact"])
    amplification_upper = Q(factorization["minimax_amplification_squared_upper_exact"])
    if amplification_upper <= 0:
        raise ValueError("positive amplification upper bound is required")
    floor_lower = 1 / amplification_upper
    floor_upper = None if amplification_lower <= 0 else 1 / amplification_lower
    return {
        "identity_query_relation": (
            "profiled floor = 1/(minimax identity-query amplification squared)"
        ),
        "profiled_floor_lower_exact": _fraction_text(floor_lower),
        "profiled_floor_upper_exact": (
            None if floor_upper is None else _fraction_text(floor_upper)
        ),
        "descriptive_profiled_floor_lower": float(floor_lower),
        "strictly_positive_exact": floor_lower > 0,
    }


def _selected_shares(search: dict[str, object]) -> tuple[Fraction, Fraction, Fraction]:
    return tuple(Q(value) for value in search["selected"]["budget_shares_exact"])  # type: ignore[return-value]


def build_grouped_protocol_report() -> dict[str, object]:
    """Build the finite grouped library and its conditional exact children."""

    observations, candidates = _observation_records()
    groups_serialized, groups = _group_records(observations, candidates)
    if not all(record["tier1_controls_passed"] for record in observations):
        raise RuntimeError("a grouped-protocol Tier-1 numerical control failed")

    clock_search = _search_grid(groups, include_common_gain=False)
    clock_gain_search = _search_grid(groups, include_common_gain=True)
    minimum_clock_shares = (Q(1), Q(0), Q(0))
    selected_clock_shares = _selected_shares(clock_search)
    selected_clock_gain_shares = _selected_shares(clock_gain_search)

    minimum_clock_child = _query_child(
        groups, minimum_clock_shares, include_common_gain=False
    )
    selected_clock_child = _query_child(
        groups, selected_clock_shares, include_common_gain=False
    )
    selected_clock_gain_child = _query_child(
        groups, selected_clock_gain_shares, include_common_gain=True
    )
    children = {
        "minimum_three_output_launch_A_clock_only": minimum_clock_child,
        "selected_cost_weighted_clock_only": selected_clock_child,
        "secondary_selected_clock_and_common_gain": selected_clock_gain_child,
    }
    for child in children.values():
        verification = verify_query_protocol_report(child)
        if not verification["passed"]:
            raise AssertionError(f"exact query child failed verification: {verification}")
        if child["effective_response_rank"] != 2:
            raise AssertionError("a declared positive-floor child lost full query rank")

    clock_output_count = int(clock_search["selected"]["active_output_count"])
    gain_output_count = int(clock_gain_search["selected"]["active_output_count"])
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "constructive positive grouped-protocol floor",
        "evidence_tier": TIER_1_SCOPE,
        "source_model": {
            "coordinates": list(SOURCE_COORDINATES),
            "base_point_exact": ["0/1", "0/1"],
            "dimensionless_convention": (
                "m1=l1=g=1, m2=exp(u), l2=exp(v), tau=t*sqrt(g/l1), "
                "nu=dtheta/dtau"
            ),
            "query": "the full two-dimensional identity query in (u,v)",
        },
        "experimental_semantics": {
            "grouping": GROUPING_SEMANTICS,
            "shared_clock": (
                "one unrestricted epsilon with tau_actual=exp(epsilon)*tau_declared; "
                "epsilon is global across repetitions and group types, and its local "
                "response is tau*d(sensor output)/d tau"
            ),
            "local_linearization": (
                "all state, tangent, parameter, clock, and gain rows are evaluated "
                "locally at (u,v,epsilon,kappa)=(0,0,0,0), with kappa present "
                "only in the secondary common-gain model"
            ),
            "output_noise_metric": (
                "the within-group metric is diagonal with each legacy scalar noise "
                "precision on its diagonal; this declares independent scalar readout "
                "noise before the common batch repetition factor p_g/c_g"
            ),
            "preparation": (
                "launch coordinates are exact declarations; no preparation nuisance "
                "is profiled and no preparation-error bound is claimed"
            ),
            "secondary_common_gain": COMMON_GAIN_SCOPE,
        },
        "integration_and_declaration": {
            "coarse": _integration_record(COARSE_INTEGRATION),
            "fine": _integration_record(FINE_INTEGRATION),
            "refinement_norms": {
                "state_relative": "||z_c-z_f||_2/max(1,||z_f||_2)",
                "parameter_sensitivity_relative": "||S_c-S_f||_F/max(1,||S_f||_F)",
                "clock_state_vector_relative": "||c_c-c_f||_2/max(1,||c_f||_2)",
            },
            "gates": dict(REFINEMENT_GATES),
            "point_declaration_rule": (
                "round each fine scalar response to the nearest multiple of "
                f"1/{DECLARATION_DENOMINATOR}; this is not an enclosure"
            ),
        },
        "scalar_observation_library": observations,
        "all_tier1_controls_passed": True,
        "grouped_protocol_library": groups_serialized,
        "finite_library_scope": {
            "legacy_scalar_candidate_count": len(observations),
            "group_count": len(groups),
            "group_names": [group.name for group in groups],
            "only_declared_launches_sensors_and_times_searched": True,
            "continuous_launch_time_sensor_optimization_claimed": False,
        },
        "rank_theorem": {
            "clock_only": (
                "For d=2 and one rank-one unrestricted shared nuisance, m-r>=d "
                "requires m>=3. Full query rank holds exactly when rank([B H])-rank(B)=2."
            ),
            "clock_and_common_gain": (
                "For d=2 and two independent shared nuisance columns, m>=4 is "
                "necessary and rank([B H])-rank(B)=2 is sufficient."
            ),
            "minimum_three_output_launch_A_effective_rank_exact": minimum_clock_child[
                "effective_response_rank"
            ],
            "minimum_output_condition_is_constructively_attained": True,
            "selected_clock_output_count": clock_output_count,
            "selected_clock_effective_rank_exact": selected_clock_child[
                "effective_response_rank"
            ],
            "secondary_gain_selected_output_count": gain_output_count,
            "secondary_gain_effective_rank_exact": selected_clock_gain_child[
                "effective_response_rank"
            ],
        },
        "rational_grid_search": {
            "clock_only": clock_search,
            "clock_and_optimistic_common_gain": clock_gain_search,
        },
        "selected_designs": {
            "minimum_clock_only": {
                "budget_shares_exact": _vector_text(minimum_clock_shares),
                "positive_floor": _floor_record(minimum_clock_child),
            },
            "cost_weighted_clock_only": {
                "budget_shares_exact": _vector_text(selected_clock_shares),
                "positive_floor": _floor_record(selected_clock_child),
            },
            "secondary_clock_and_common_gain": {
                "budget_shares_exact": _vector_text(selected_clock_gain_shares),
                "positive_floor": _floor_record(selected_clock_gain_child),
                "scope": COMMON_GAIN_SCOPE,
            },
        },
        "exact_query_engine_children": children,
        "outward_validation": {
            "state_enclosed": False,
            "parameter_sensitivity_enclosed": False,
            "clock_response_enclosed": False,
            "rational_point_membership_certified": False,
            "preparation_error_bounded": False,
        },
        "proof_boundary": PROOF_BOUNDARY,
        "internal_recomputation_verification": {
            "passed": True,
            "tier1_numerics_recomputed": True,
            "finite_rational_grid_recomputed": True,
            "exact_query_children_verified": True,
            "outward_validation_performed": False,
        },
    }
    return report


def verify_grouped_protocol_report(report: dict[str, object]) -> dict[str, object]:
    """Strictly recompute the Tier-1 report and verify every exact child."""

    recomputed = False
    try:
        if not isinstance(report, dict) or report.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unknown grouped-protocol schema")
        if report.get("status") != "constructive positive grouped-protocol floor":
            raise ValueError("unexpected grouped-protocol status")
        if report.get("evidence_tier") != TIER_1_SCOPE:
            raise ValueError("the report must remain Tier-1")
        if report.get("proof_boundary") != PROOF_BOUNDARY:
            raise ValueError("proof boundary changed")
        outward = report.get("outward_validation")
        if not isinstance(outward, dict) or any(value is not False for value in outward.values()):
            raise ValueError("an outward or preparation-bound claim is forbidden")
        expected = build_grouped_protocol_report()
        recomputed = True
        if not _strict_json_equal(report, expected):
            raise ValueError("report does not strictly reproduce from the canonical finite library")
        children = report.get("exact_query_engine_children")
        if not isinstance(children, dict) or len(children) != 3:
            raise ValueError("exact query children are missing")
        for child in children.values():
            verification = verify_query_protocol_report(child)
            if not verification["passed"]:
                raise ValueError("an exact query child failed verification")
        return {
            "passed": True,
            "tier1_numerics_recomputed": True,
            "finite_rational_grid_recomputed": True,
            "exact_query_children_verified": True,
            "positive_clock_profiled_floor_verified_for_declared_point_model": True,
            "outward_ode_validation_verified": False,
            "preparation_error_bound_verified": False,
        }
    except Exception as error:
        return {
            "passed": False,
            "tier1_numerics_recomputed": recomputed,
            "finite_rational_grid_recomputed": recomputed,
            "outward_ode_validation_verified": False,
            "preparation_error_bound_verified": False,
            "error": str(error),
        }


def _write_json(path: Path, report: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args(argv)
    if args.verify is not None:
        report = json.loads(args.verify.read_text(encoding="utf-8"))
        verification = verify_grouped_protocol_report(report)
        print(json.dumps(verification, indent=2, sort_keys=True))
        return 0 if verification["passed"] else 1
    report = build_grouped_protocol_report()
    if args.output is not None:
        _write_json(args.output, report)
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "COMMON_GAIN_SCOPE",
    "GROUP_DEFINITIONS",
    "GROUPING_SEMANTICS",
    "PROOF_BOUNDARY",
    "SCHEMA_VERSION",
    "SEARCH_DENOMINATOR",
    "SOURCE_COORDINATES",
    "TIER_1_SCOPE",
    "build_grouped_protocol_report",
    "verify_grouped_protocol_report",
]
