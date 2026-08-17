#!/usr/bin/env python3
"""Structured physical-nuisance controls for two active pendulum protocols.

The pointwise parameter-response transfer supplies two scalar protocol rows for
the source coordinates

    u = log(m2/m1),   v = log(l2/l1).

This module adds the smallest local nuisance model that distinguishes

* one clock dilation shared by every launch;
* multiplicative sensor calibration (both an optimistic common-gain model and
  the physically distinct gain-per-sensor control); and
* initial-angle preparation errors refitted independently at each launch.

The nuisance columns are analytic functions of a terminal state and its
initial-state tangent.  Their numerical evaluation and rationalization are
Tier-1 discovery only.  Exact query and structured-nuisance children prove
finite rational linear statements conditional on the serialized point
declarations; they do not outwardly validate the ODE nuisance columns.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
from typing import Sequence

import numpy as np

from double_pendulum_dynamics import (
    DoublePendulumParameters,
    IntegrationConfig,
    double_pendulum_rhs,
)
from double_pendulum_variational import simulate_double_pendulum_variational
from oig_double_pendulum_parameter_sensitivity import canonical_active_protocols
from oig_query_protocol_design import (
    QueryProtocol,
    certify_query_independent_nuisance_mixture,
    certify_query_protocol_mixture,
    verify_query_protocol_report,
)
from oig_structured_nuisance import (
    certify_structured_nuisance_separation,
    verify_structured_nuisance_report,
)
from oig_numerical_replay import (
    REPLAY_ABSOLUTE_TOLERANCE,
    REPLAY_RELATIVE_TOLERANCE,
    replay_float_equal,
)


Q = Fraction
SCHEMA_VERSION = "oig-double-pendulum-structured-physical-nuisance-v1"
TIER_1_SCOPE = "tier_1_numerical_not_outward_validated"
RATIONALIZATION_MAX_DENOMINATOR = 10**9

ACTIVE_NAMES = (
    "launch-A / theta-2 / tau-1",
    "launch-B / scaled-omega-1 / tau-5/4",
)
SOURCE_COORDINATES = ("u=log(m2/m1)", "v=log(l2/l1)")
SOURCE_RESPONSE_CENTRE = (
    (Q(265, 3136), Q(-4041, 8894)),
    (Q(2357, 5025), Q(13, 3140)),
)
BUDGET_SHARES = (Q(4589, 10000), Q(5411, 10000))
COSTS = (Q(1), Q(5, 4))

DIMENSIONLESS_PARAMETERS = DoublePendulumParameters(
    m1=1.0, m2=1.0, l1=1.0, l2=1.0, g=1.0
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
    "tangent_relative": 1.0e-8,
    "nuisance_column_relative": 1.0e-8,
    "rationalization_absolute": 1.0e-8,
}

PROOF_BOUNDARY = (
    "The already established pointwise transfer concerns the two physical-source "
    "response boxes at u=v=0. The new clock, gain, and preparation columns here "
    "are evaluated by floating variational integration and are not outwardly "
    "enclosed. Exact child certificates therefore apply only to the explicitly "
    "declared rational finite linear model; they do not prove that the nonlinear "
    "ODE nuisance response equals, or lies near, those declarations."
)

THEOREM_STATEMENT = (
    "For an invertible two-by-two physical response H, profiling any nonzero "
    "shared scalar nuisance b leaves rank one and hence zero full two-source "
    "information floor; the exactly lost source direction is H^{-1}b and the "
    "surviving query row space is {w^T H : w^T b=0}. Two independent shared "
    "nuisance columns span the complete two-output space and destroy every "
    "nonzero query. Independently refitted preparation errors also destroy every "
    "query whenever each scalar protocol has one nonzero local preparation "
    "derivative, because their block-local ranges span both output coordinates."
)


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _parse_fraction(value: object, name: str) -> Fraction:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a canonical fraction string")
    result = Q(value)
    if _fraction_text(result) != value:
        raise ValueError(f"{name} is not canonically encoded")
    return result


def _matrix_text(matrix: Sequence[Sequence[Fraction]]) -> list[list[str]]:
    return [[_fraction_text(value) for value in row] for row in matrix]


def _vector_text(vector: Sequence[Fraction]) -> list[str]:
    return [_fraction_text(value) for value in vector]


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


def _numeric(value: object, name: str) -> float:
    if isinstance(value, bool) or type(value) not in (int, float):
        raise ValueError(f"{name} must be a JSON number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _numeric_array(value: object, shape: tuple[int, ...], name: str) -> np.ndarray:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a JSON array")

    def convert(item: object, path: str) -> object:
        if isinstance(item, list):
            return [convert(child, f"{path}[{index}]") for index, child in enumerate(item)]
        return _numeric(item, path)

    result = np.asarray(convert(value, name), dtype=float)
    if result.shape != shape:
        raise ValueError(f"{name} has shape {result.shape}, expected {shape}")
    return result


def _rationalize(value: float) -> Fraction:
    if not math.isfinite(float(value)):
        raise ValueError("cannot rationalize a non-finite value")
    return Q(float(value)).limit_denominator(RATIONALIZATION_MAX_DENOMINATOR)


def _relative_discrepancy(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.linalg.norm(left - right) / max(1.0, float(np.linalg.norm(right))))


def _integration_record(config: IntegrationConfig) -> dict[str, object]:
    return {
        "method": "DOP853 joint state/initial-state-tangent integration",
        "rtol": config.rtol,
        "atol": config.atol,
        "max_step_in_tau": config.max_step,
        "sampled_scaled_energy_drift_tolerance": config.energy_drift_tolerance,
    }


def _sensor_index(sensor: str) -> int:
    return {
        "theta_1": 0,
        "theta_2": 1,
        "scaled_omega_1": 2,
        "scaled_omega_2": 3,
    }[sensor]


def _terminal_record(candidate: object, config: IntegrationConfig) -> dict[str, object]:
    launch = np.asarray([float(value) for value in candidate.launch], dtype=float)
    tau = float(candidate.observation_time_tau)
    trajectory = simulate_double_pendulum_variational(
        launch,
        [0.0, tau],
        DIMENSIONLESS_PARAMETERS,
        config,
    )
    state = np.asarray(trajectory.states[-1], dtype=float)
    tangent = np.asarray(trajectory.tangents[-1], dtype=float)
    rhs = np.asarray(double_pendulum_rhs(tau, state, DIMENSIONLESS_PARAMETERS), dtype=float)
    index = _sensor_index(candidate.sensor)
    output = float(state[index])
    clock = float(tau * rhs[index])
    preparation = np.asarray(tangent[index, :2], dtype=float)
    return {
        "terminal_state": state.tolist(),
        "terminal_rhs_dz_dtau": rhs.tolist(),
        "terminal_initial_state_tangent": tangent.tolist(),
        "sensor_output": output,
        "clock_log_dilation_column_entry": clock,
        "common_log_gain_column_entry": output,
        "initial_angle_preparation_row": preparation.tolist(),
        "max_scaled_energy_drift": float(trajectory.max_scaled_energy_drift),
        "accepted_step_count": int(trajectory.accepted_step_count),
        "nfev": int(trajectory.nfev),
    }


def _invert_2x2(matrix: Sequence[Sequence[Fraction]]) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    a, b = matrix[0]
    c, d = matrix[1]
    determinant = a * d - b * c
    if determinant == 0:
        raise ValueError("matrix is singular")
    return ((d / determinant, -b / determinant), (-c / determinant, a / determinant))


def _matvec_2x2(
    matrix: Sequence[Sequence[Fraction]], vector: Sequence[Fraction]
) -> tuple[Fraction, Fraction]:
    return (
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1],
    )


def _row_times_matrix(
    row: Sequence[Fraction], matrix: Sequence[Sequence[Fraction]]
) -> tuple[Fraction, Fraction]:
    return (
        row[0] * matrix[0][0] + row[1] * matrix[1][0],
        row[0] * matrix[0][1] + row[1] * matrix[1][1],
    )


def _query_protocols(
    nuisance_rows: Sequence[Sequence[Fraction]] | None,
) -> tuple[QueryProtocol, QueryProtocol]:
    protocols = []
    for index, name in enumerate(ACTIVE_NAMES):
        nuisance = None if nuisance_rows is None else [nuisance_rows[index]]
        protocols.append(
            QueryProtocol.from_rows(
                name,
                [SOURCE_RESPONSE_CENTRE[index]],
                nuisance,
                [[1]],
                cost=COSTS[index],
            )
        )
    return tuple(protocols)  # type: ignore[return-value]


def _query_shared(
    nuisance_rows: Sequence[Sequence[Fraction]] | None,
    query: Sequence[Sequence[Fraction]],
) -> dict[str, object]:
    return certify_query_protocol_mixture(
        _query_protocols(nuisance_rows),
        BUDGET_SHARES,
        [[1, 0], [0, 1]],
        query,
        [[Q(int(row == column)) for column in range(len(query))] for row in range(len(query))],
    )


def _query_independent(
    nuisance_rows: Sequence[Sequence[Fraction]],
    query: Sequence[Sequence[Fraction]],
) -> dict[str, object]:
    return certify_query_independent_nuisance_mixture(
        _query_protocols(nuisance_rows),
        BUDGET_SHARES,
        [[1, 0], [0, 1]],
        query,
        [[Q(int(row == column)) for column in range(len(query))] for row in range(len(query))],
    )


def _structured_zero(
    name: str,
    query_response: Sequence[Fraction],
    basis: Sequence[Sequence[Fraction]],
) -> dict[str, object]:
    inverse = _invert_2x2(basis)
    cancelling = _matvec_2x2(inverse, query_response)
    return certify_structured_nuisance_separation(
        name=name,
        query_response=query_response,
        generators=[[0], [0]],
        coefficient_radii=[0],
        primal_coefficients=[0],
        dual_direction=[0, 0],
        nuisance_basis=basis,
        primal_nuisance_coefficients=[-cancelling[0], -cancelling[1]],
    )


def _conditional_exact_analysis(
    clock: tuple[Fraction, Fraction],
    gain: tuple[Fraction, Fraction],
    preparation: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]],
) -> dict[str, object]:
    response_inverse = _invert_2x2(SOURCE_RESPONSE_CENTRE)
    response_determinant = (
        SOURCE_RESPONSE_CENTRE[0][0] * SOURCE_RESPONSE_CENTRE[1][1]
        - SOURCE_RESPONSE_CENTRE[0][1] * SOURCE_RESPONSE_CENTRE[1][0]
    )
    shared_matrix = ((clock[0], gain[0]), (clock[1], gain[1]))
    shared_determinant = clock[0] * gain[1] - gain[0] * clock[1]
    if shared_determinant == 0:
        raise ValueError("declared clock and common-gain columns must be independent")
    if any(not any(row) for row in preparation):
        raise ValueError("each declared preparation row must be nonzero")
    if gain[0] == 0 or gain[1] == 0:
        raise ValueError("sensor-specific gain control requires nonzero outputs")

    identity_query = ((Q(1), Q(0)), (Q(0), Q(1)))
    clock_rows = ((clock[0],), (clock[1],))
    gain_rows = ((gain[0],), (gain[1],))
    shared_rows = (
        (clock[0], gain[0]),
        (clock[1], gain[1]),
    )

    clock_annihilator = (clock[1], -clock[0])
    gain_annihilator = (gain[1], -gain[0])
    clock_surviving_query = _row_times_matrix(clock_annihilator, SOURCE_RESPONSE_CENTRE)
    gain_surviving_query = _row_times_matrix(gain_annihilator, SOURCE_RESPONSE_CENTRE)

    query_children = {
        "nominal_full_source": _query_shared(None, identity_query),
        "shared_clock_full_source": _query_shared(clock_rows, identity_query),
        "shared_clock_surviving_query": _query_shared(
            clock_rows, (clock_surviving_query,)
        ),
        "shared_common_gain_full_source": _query_shared(gain_rows, identity_query),
        "shared_common_gain_surviving_query": _query_shared(
            gain_rows, (gain_surviving_query,)
        ),
        "shared_clock_and_common_gain_full_source": _query_shared(
            shared_rows, identity_query
        ),
        "independent_angle_preparation_full_source": _query_independent(
            preparation, identity_query
        ),
        "sensor_specific_gain_full_source": _query_independent(
            gain_rows, identity_query
        ),
    }

    clock_confounded_source = _matvec_2x2(response_inverse, clock)
    gain_confounded_source = _matvec_2x2(response_inverse, gain)
    structured_children = {
        "shared_clock_survivor": certify_structured_nuisance_separation(
            name="clock-orthogonal output displacement survives",
            query_response=clock_annihilator,
            generators=[[0], [0]],
            coefficient_radii=[0],
            primal_coefficients=[0],
            dual_direction=clock_annihilator,
            nuisance_basis=[[clock[0]], [clock[1]]],
            primal_nuisance_coefficients=[0],
        ),
        "shared_clock_exact_confounding": certify_structured_nuisance_separation(
            name="clock column is exactly confounded",
            query_response=clock,
            generators=[[0], [0]],
            coefficient_radii=[0],
            primal_coefficients=[0],
            dual_direction=[0, 0],
            nuisance_basis=[[clock[0]], [clock[1]]],
            primal_nuisance_coefficients=[-1],
        ),
        "clock_and_gain_span_all_outputs": _structured_zero(
            "clock and common gain cancel a physical displacement",
            (SOURCE_RESPONSE_CENTRE[0][0], SOURCE_RESPONSE_CENTRE[1][0]),
            shared_matrix,
        ),
        "independent_preparation_span_all_outputs": _structured_zero(
            "independent scalar-row preparation nuisance cancels every output",
            (SOURCE_RESPONSE_CENTRE[0][0], SOURCE_RESPONSE_CENTRE[1][0]),
            ((Q(1), Q(0)), (Q(0), Q(1))),
        ),
    }

    return {
        "model_status": "exact rational linear theorem conditional on declared nuisance columns",
        "source_response_centre_exact": _matrix_text(SOURCE_RESPONSE_CENTRE),
        "source_response_determinant_exact": _fraction_text(response_determinant),
        "source_response_rank": 2,
        "declared_columns_exact": {
            "shared_clock_log_dilation": _vector_text(clock),
            "shared_common_log_gain": _vector_text(gain),
            "per_launch_initial_angle_preparation_rows": _matrix_text(preparation),
            "clock_and_common_gain_by_rows": _matrix_text(shared_matrix),
            "clock_and_common_gain_determinant_exact": _fraction_text(shared_determinant),
        },
        "exact_confoundings": {
            "clock_lost_source_direction_H_inverse_b": _vector_text(clock_confounded_source),
            "gain_lost_source_direction_H_inverse_b": _vector_text(gain_confounded_source),
            "clock_surviving_query_row": _vector_text(clock_surviving_query),
            "gain_surviving_query_row": _vector_text(gain_surviving_query),
            "identity_H_times_H_inverse_b_checks": True,
        },
        "rank_and_floor_conclusions": {
            "nominal_effective_rank": 2,
            "shared_clock_effective_rank": 1,
            "shared_clock_full_two_source_floor_positive": False,
            "shared_clock_one_dimensional_query_survives": True,
            "shared_common_gain_effective_rank": 1,
            "shared_common_gain_full_two_source_floor_positive": False,
            "shared_common_gain_one_dimensional_query_survives": True,
            "clock_and_common_gain_effective_rank": 0,
            "clock_and_common_gain_any_nonzero_query_survives": False,
            "independent_preparation_effective_rank": 0,
            "independent_preparation_any_nonzero_query_survives": False,
            "sensor_specific_gain_effective_rank": 0,
            "sensor_specific_gain_any_nonzero_query_survives": False,
        },
        "query_engine_children": query_children,
        "structured_nuisance_children": structured_children,
        "conditional_scope": (
            "Exact ranks, confoundings, factorization decisions, and separation bounds "
            "hold for the fixed rational center response and fixed rational nuisance "
            "columns serialized here. No child encloses an ODE nuisance derivative or "
            "jointly propagates the established physical response boxes."
        ),
    }


def build_structured_physical_nuisance_report() -> dict[str, object]:
    """Build Tier-1 nuisance discovery and conditional exact controls."""

    candidates = canonical_active_protocols()
    if tuple(candidate.name for candidate in candidates) != ACTIVE_NAMES:
        raise RuntimeError("canonical active protocol definitions changed")

    protocol_records: list[dict[str, object]] = []
    clock_exact: list[Fraction] = []
    gain_exact: list[Fraction] = []
    preparation_exact: list[tuple[Fraction, Fraction]] = []
    for index, candidate in enumerate(candidates):
        coarse = _terminal_record(candidate, COARSE_INTEGRATION)
        fine = _terminal_record(candidate, FINE_INTEGRATION)
        coarse_state = np.asarray(coarse["terminal_state"], dtype=float)
        fine_state = np.asarray(fine["terminal_state"], dtype=float)
        coarse_tangent = np.asarray(coarse["terminal_initial_state_tangent"], dtype=float)
        fine_tangent = np.asarray(fine["terminal_initial_state_tangent"], dtype=float)
        coarse_columns = np.asarray(
            [
                coarse["clock_log_dilation_column_entry"],
                coarse["common_log_gain_column_entry"],
                *coarse["initial_angle_preparation_row"],
            ],
            dtype=float,
        )
        fine_columns = np.asarray(
            [
                fine["clock_log_dilation_column_entry"],
                fine["common_log_gain_column_entry"],
                *fine["initial_angle_preparation_row"],
            ],
            dtype=float,
        )
        discrepancies = {
            "state_relative": _relative_discrepancy(coarse_state, fine_state),
            "tangent_relative": _relative_discrepancy(coarse_tangent, fine_tangent),
            "nuisance_column_relative": _relative_discrepancy(coarse_columns, fine_columns),
        }
        declared = tuple(_rationalize(value) for value in fine_columns)
        rationalization_errors = [
            abs(float(value) - float(exact)) for value, exact in zip(fine_columns, declared)
        ]
        discovery_passed = (
            discrepancies["state_relative"] <= REFINEMENT_GATES["state_relative"]
            and discrepancies["tangent_relative"] <= REFINEMENT_GATES["tangent_relative"]
            and discrepancies["nuisance_column_relative"]
            <= REFINEMENT_GATES["nuisance_column_relative"]
            and max(rationalization_errors) <= REFINEMENT_GATES["rationalization_absolute"]
            and coarse["max_scaled_energy_drift"]
            <= COARSE_INTEGRATION.energy_drift_tolerance
            and fine["max_scaled_energy_drift"]
            <= FINE_INTEGRATION.energy_drift_tolerance
        )
        clock_exact.append(declared[0])
        gain_exact.append(declared[1])
        preparation_exact.append((declared[2], declared[3]))
        protocol_records.append(
            {
                "name": candidate.name,
                "launch_exact": [_fraction_text(value) for value in candidate.launch],
                "sensor": candidate.sensor,
                "observation_time_tau_exact": _fraction_text(candidate.observation_time_tau),
                "cost_exact": _fraction_text(COSTS[index]),
                "budget_share_exact": _fraction_text(BUDGET_SHARES[index]),
                "physical_source_response_centre_exact": _vector_text(
                    SOURCE_RESPONSE_CENTRE[index]
                ),
                "analytic_local_columns": {
                    "shared_clock_log_dilation": "c_i=tau_i * d y_i/d tau",
                    "shared_common_log_gain": "a_i=y_i for y_measured=exp(kappa)*y_i",
                    "per_launch_initial_angle_preparation": (
                        "p_i=e_sensor^T Phi_i(tau_i) J_theta, "
                        "J_theta=[e_theta1,e_theta2]"
                    ),
                },
                "coarse": coarse,
                "fine": fine,
                "refinement_discrepancies": discrepancies,
                "declared_rational_point_columns": {
                    "shared_clock_log_dilation_exact": _fraction_text(declared[0]),
                    "shared_common_log_gain_exact": _fraction_text(declared[1]),
                    "initial_angle_preparation_row_exact": _vector_text(declared[2:]),
                    "rationalization_absolute_errors": rationalization_errors,
                    "status": "conditional point declaration; not an outward enclosure",
                },
                "tier1_controls_passed": discovery_passed,
            }
        )

    conditional = _conditional_exact_analysis(
        tuple(clock_exact),  # type: ignore[arg-type]
        tuple(gain_exact),  # type: ignore[arg-type]
        tuple(preparation_exact),  # type: ignore[arg-type]
    )
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "minimal structured-physical-nuisance extension",
        "evidence_tier": TIER_1_SCOPE,
        "source_model": {
            "coordinates": list(SOURCE_COORDINATES),
            "dimensionless_convention": (
                "m1=l1=g=1, m2=exp(u), l2=exp(v), tau=t*sqrt(g/l1), "
                "nu=dtheta/dtau"
            ),
            "clock_convention": (
                "epsilon is a shared scheduling dilation: actual terminal tau is "
                "exp(epsilon) times declared tau; dimensionless sensor units are held fixed"
            ),
            "calibration_convention": (
                "kappa is a small log multiplicative gain; a common-gain model is an "
                "optimistic control, while distinct theta2 and nu1 sensors receive "
                "independent gain parameters in the sensor-specific control"
            ),
            "preparation_convention": (
                "each launch independently refits errors in initial theta1 and theta2; "
                "initial dimensionless velocities remain fixed at zero"
            ),
            "common_mass_scale_blindness": (
                "m1,m2 -> c*m1,c*m2 leaves the normalized vector field unchanged and "
                "is excluded before this nuisance analysis"
            ),
        },
        "integration": {
            "parameters": {"m1": 1.0, "m2": 1.0, "l1": 1.0, "l2": 1.0, "g": 1.0},
            "coarse": _integration_record(COARSE_INTEGRATION),
            "fine": _integration_record(FINE_INTEGRATION),
            "refinement_norms": {
                "state_relative": "||z_c-z_f||_2/max(1,||z_f||_2)",
                "tangent_relative": "||Phi_c-Phi_f||_F/max(1,||Phi_f||_F)",
                "nuisance_column_relative": "||n_c-n_f||_2/max(1,||n_f||_2)",
            },
            "gates": dict(REFINEMENT_GATES),
            "rationalization_max_denominator": RATIONALIZATION_MAX_DENOMINATOR,
        },
        "protocols": protocol_records,
        "all_tier1_controls_passed": all(
            bool(record["tier1_controls_passed"]) for record in protocol_records
        ),
        "theorem": {
            "statement": THEOREM_STATEMENT,
            "minimum_dimension_consequence": (
                "With d=2 physical sources and r independent unrestricted shared "
                "nuisance directions, m scalar outputs require m-r>=2 for a possible "
                "positive full-source floor. Independently refitted local nuisance must "
                "first be removed launch by launch; one scalar output cannot survive a "
                "single nonzero local nuisance derivative."
            ),
            "present_two_scalar_protocols_sufficient_for_full_source_with_nuisance": False,
        },
        "conditional_exact_analysis": conditional,
        "proof_boundary": PROOF_BOUNDARY,
        "outward_ode_nuisance_validation_claimed": False,
    }
    verification = verify_structured_physical_nuisance_report(report)
    if not verification["passed"]:
        raise AssertionError(f"generated nuisance report fails verification: {verification}")
    report["independent_verification"] = verification
    return report


def _expected_protocol_declaration(index: int) -> dict[str, object]:
    candidate = canonical_active_protocols()[index]
    return {
        "name": candidate.name,
        "launch_exact": [_fraction_text(value) for value in candidate.launch],
        "sensor": candidate.sensor,
        "observation_time_tau_exact": _fraction_text(candidate.observation_time_tau),
        "cost_exact": _fraction_text(COSTS[index]),
        "budget_share_exact": _fraction_text(BUDGET_SHARES[index]),
        "physical_source_response_centre_exact": _vector_text(SOURCE_RESPONSE_CENTRE[index]),
        "analytic_local_columns": {
            "shared_clock_log_dilation": "c_i=tau_i * d y_i/d tau",
            "shared_common_log_gain": "a_i=y_i for y_measured=exp(kappa)*y_i",
            "per_launch_initial_angle_preparation": (
                "p_i=e_sensor^T Phi_i(tau_i) J_theta, "
                "J_theta=[e_theta1,e_theta2]"
            ),
        },
    }


def _verify_terminal_record(
    record: object,
    *,
    candidate: object,
    config: IntegrationConfig,
    name: str,
) -> tuple[np.ndarray, np.ndarray]:
    if not isinstance(record, dict):
        raise ValueError(f"{name} must be an object")
    required = {
        "terminal_state",
        "terminal_rhs_dz_dtau",
        "terminal_initial_state_tangent",
        "sensor_output",
        "clock_log_dilation_column_entry",
        "common_log_gain_column_entry",
        "initial_angle_preparation_row",
        "max_scaled_energy_drift",
        "accepted_step_count",
        "nfev",
    }
    if set(record) != required:
        raise ValueError(f"{name} fields differ from schema")
    state = _numeric_array(record["terminal_state"], (4,), f"{name}.terminal_state")
    rhs = _numeric_array(record["terminal_rhs_dz_dtau"], (4,), f"{name}.rhs")
    tangent = _numeric_array(
        record["terminal_initial_state_tangent"], (4, 4), f"{name}.tangent"
    )
    index = _sensor_index(candidate.sensor)
    tau = float(candidate.observation_time_tau)
    reconstructed_rhs = np.asarray(
        double_pendulum_rhs(tau, state, DIMENSIONLESS_PARAMETERS), dtype=float
    )
    if not np.allclose(
        rhs,
        reconstructed_rhs,
        rtol=REPLAY_RELATIVE_TOLERANCE,
        atol=REPLAY_ABSOLUTE_TOLERANCE,
    ):
        raise ValueError(f"{name} terminal RHS does not reconstruct from state")
    output = _numeric(record["sensor_output"], f"{name}.sensor_output")
    clock = _numeric(record["clock_log_dilation_column_entry"], f"{name}.clock")
    gain = _numeric(record["common_log_gain_column_entry"], f"{name}.gain")
    preparation = _numeric_array(
        record["initial_angle_preparation_row"], (2,), f"{name}.preparation"
    )
    if not replay_float_equal(
        output, float(state[index])
    ) or not replay_float_equal(gain, output):
        raise ValueError(f"{name} gain column does not equal the sensor output")
    if not replay_float_equal(clock, float(tau * rhs[index])):
        raise ValueError(f"{name} clock column does not equal tau*dy/dtau")
    if not np.allclose(
        preparation,
        tangent[index, :2],
        rtol=REPLAY_RELATIVE_TOLERANCE,
        atol=REPLAY_ABSOLUTE_TOLERANCE,
    ):
        raise ValueError(f"{name} preparation row does not come from the tangent")
    drift = _numeric(record["max_scaled_energy_drift"], f"{name}.energy drift")
    if config.energy_drift_tolerance is None or drift < 0 or drift > config.energy_drift_tolerance:
        raise ValueError(f"{name} sampled energy gate failed or was disabled")
    for integer_field in ("accepted_step_count", "nfev"):
        value = record[integer_field]
        if type(value) is not int or value < 1:
            raise ValueError(f"{name}.{integer_field} must be a positive integer")
    columns = np.asarray([clock, gain, *preparation], dtype=float)
    return state, np.concatenate((tangent.reshape(-1), columns))


def verify_structured_physical_nuisance_report(
    report: dict[str, object],
) -> dict[str, object]:
    """Verify serialized algebra and exact children without replaying the ODE."""

    try:
        if not isinstance(report, dict) or report.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unknown structured physical nuisance schema")
        root_fields = {
            "schema_version",
            "status",
            "evidence_tier",
            "source_model",
            "integration",
            "protocols",
            "all_tier1_controls_passed",
            "theorem",
            "conditional_exact_analysis",
            "proof_boundary",
            "outward_ode_nuisance_validation_claimed",
        }
        submitted_root_fields = set(report)
        if submitted_root_fields not in (root_fields, root_fields | {"independent_verification"}):
            raise ValueError("root fields differ from the strict schema")
        if report.get("status") != "minimal structured-physical-nuisance extension":
            raise ValueError("unexpected report status")
        if report.get("evidence_tier") != TIER_1_SCOPE:
            raise ValueError("the report must remain Tier-1")
        if report.get("proof_boundary") != PROOF_BOUNDARY:
            raise ValueError("proof boundary changed")
        if report.get("outward_ode_nuisance_validation_claimed") is not False:
            raise ValueError("an outward ODE nuisance claim is forbidden")
        integration = report.get("integration")
        if not isinstance(integration, dict):
            raise ValueError("integration block is missing")
        expected_integration = {
            "parameters": {"m1": 1.0, "m2": 1.0, "l1": 1.0, "l2": 1.0, "g": 1.0},
            "coarse": _integration_record(COARSE_INTEGRATION),
            "fine": _integration_record(FINE_INTEGRATION),
            "refinement_norms": {
                "state_relative": "||z_c-z_f||_2/max(1,||z_f||_2)",
                "tangent_relative": "||Phi_c-Phi_f||_F/max(1,||Phi_f||_F)",
                "nuisance_column_relative": "||n_c-n_f||_2/max(1,||n_f||_2)",
            },
            "gates": dict(REFINEMENT_GATES),
            "rationalization_max_denominator": RATIONALIZATION_MAX_DENOMINATOR,
        }
        if not _strict_json_equal(integration, expected_integration):
            raise ValueError("integration declarations or gates changed")

        protocols = report.get("protocols")
        if not isinstance(protocols, list) or len(protocols) != 2:
            raise ValueError("exactly two active protocol records are required")
        candidates = canonical_active_protocols()
        clock: list[Fraction] = []
        gain: list[Fraction] = []
        preparation: list[tuple[Fraction, Fraction]] = []
        all_passed = True
        for index, (raw, candidate) in enumerate(zip(protocols, candidates)):
            if not isinstance(raw, dict):
                raise ValueError("protocol record must be an object")
            expected_prefix = _expected_protocol_declaration(index)
            expected_protocol_fields = set(expected_prefix) | {
                "coarse",
                "fine",
                "refinement_discrepancies",
                "declared_rational_point_columns",
                "tier1_controls_passed",
            }
            if set(raw) != expected_protocol_fields:
                raise ValueError(f"protocol {index} fields differ from the strict schema")
            for key, value in expected_prefix.items():
                if not _strict_json_equal(raw.get(key), value):
                    raise ValueError(f"protocol {index} declaration changed at {key}")
            coarse_state, coarse_augmented = _verify_terminal_record(
                raw.get("coarse"), candidate=candidate, config=COARSE_INTEGRATION,
                name=f"protocol[{index}].coarse",
            )
            fine_state, fine_augmented = _verify_terminal_record(
                raw.get("fine"), candidate=candidate, config=FINE_INTEGRATION,
                name=f"protocol[{index}].fine",
            )
            # The augmented vectors contain tangent then the four nuisance entries.
            coarse_tangent = coarse_augmented[:16].reshape(4, 4)
            fine_tangent = fine_augmented[:16].reshape(4, 4)
            coarse_columns = coarse_augmented[16:]
            fine_columns = fine_augmented[16:]
            expected_discrepancies = {
                "state_relative": _relative_discrepancy(coarse_state, fine_state),
                "tangent_relative": _relative_discrepancy(coarse_tangent, fine_tangent),
                "nuisance_column_relative": _relative_discrepancy(coarse_columns, fine_columns),
            }
            raw_discrepancies = raw.get("refinement_discrepancies")
            if not isinstance(raw_discrepancies, dict) or set(raw_discrepancies) != set(expected_discrepancies):
                raise ValueError(f"protocol {index} refinement discrepancies malformed")
            for field, expected in expected_discrepancies.items():
                if not replay_float_equal(
                    _numeric(raw_discrepancies[field], f"protocol[{index}].{field}"),
                    expected,
                ):
                    raise ValueError(f"protocol {index} {field} does not reconstruct")

            declaration = raw.get("declared_rational_point_columns")
            if not isinstance(declaration, dict) or set(declaration) != {
                "shared_clock_log_dilation_exact",
                "shared_common_log_gain_exact",
                "initial_angle_preparation_row_exact",
                "rationalization_absolute_errors",
                "status",
            }:
                raise ValueError(f"protocol {index} rational declaration malformed")
            exact_values = tuple(_rationalize(value) for value in fine_columns)
            if declaration["shared_clock_log_dilation_exact"] != _fraction_text(exact_values[0]):
                raise ValueError(f"protocol {index} clock rationalization changed")
            if declaration["shared_common_log_gain_exact"] != _fraction_text(exact_values[1]):
                raise ValueError(f"protocol {index} gain rationalization changed")
            if declaration["initial_angle_preparation_row_exact"] != _vector_text(exact_values[2:]):
                raise ValueError(f"protocol {index} preparation rationalization changed")
            if declaration["status"] != "conditional point declaration; not an outward enclosure":
                raise ValueError(f"protocol {index} declaration status changed")
            errors = _numeric_array(
                declaration["rationalization_absolute_errors"], (4,),
                f"protocol[{index}].rationalization_errors",
            )
            expected_errors = np.asarray(
                [abs(float(value) - float(exact)) for value, exact in zip(fine_columns, exact_values)]
            )
            if not np.allclose(
                errors,
                expected_errors,
                rtol=REPLAY_RELATIVE_TOLERANCE,
                atol=REPLAY_ABSOLUTE_TOLERANCE,
            ):
                raise ValueError(f"protocol {index} rationalization errors do not reconstruct")
            passed = (
                expected_discrepancies["state_relative"] <= REFINEMENT_GATES["state_relative"]
                and expected_discrepancies["tangent_relative"] <= REFINEMENT_GATES["tangent_relative"]
                and expected_discrepancies["nuisance_column_relative"]
                <= REFINEMENT_GATES["nuisance_column_relative"]
                and float(np.max(errors)) <= REFINEMENT_GATES["rationalization_absolute"]
            )
            if raw.get("tier1_controls_passed") is not passed:
                raise ValueError(f"protocol {index} Tier-1 pass flag is inconsistent")
            all_passed = all_passed and passed
            clock.append(exact_values[0])
            gain.append(exact_values[1])
            preparation.append((exact_values[2], exact_values[3]))

        if report.get("all_tier1_controls_passed") is not all_passed:
            raise ValueError("aggregate Tier-1 pass flag is inconsistent")
        if not all_passed:
            raise ValueError("Tier-1 refinement controls did not pass")

        theorem = report.get("theorem")
        expected_theorem = {
            "statement": THEOREM_STATEMENT,
            "minimum_dimension_consequence": (
                "With d=2 physical sources and r independent unrestricted shared "
                "nuisance directions, m scalar outputs require m-r>=2 for a possible "
                "positive full-source floor. Independently refitted local nuisance must "
                "first be removed launch by launch; one scalar output cannot survive a "
                "single nonzero local nuisance derivative."
            ),
            "present_two_scalar_protocols_sufficient_for_full_source_with_nuisance": False,
        }
        if not _strict_json_equal(theorem, expected_theorem):
            raise ValueError("theorem statement or dimension consequence changed")

        exact = _conditional_exact_analysis(
            tuple(clock),  # type: ignore[arg-type]
            tuple(gain),  # type: ignore[arg-type]
            tuple(preparation),  # type: ignore[arg-type]
        )
        if not _strict_json_equal(report.get("conditional_exact_analysis"), exact):
            raise ValueError("conditional exact analysis does not reconstruct")
        for child in exact["query_engine_children"].values():
            if not verify_query_protocol_report(child)["passed"]:
                raise ValueError("a query-engine child failed independent verification")
        for child in exact["structured_nuisance_children"].values():
            if not verify_structured_nuisance_report(child)["passed"]:
                raise ValueError("a structured-nuisance child failed independent verification")

        expected_source_model = {
            "coordinates": list(SOURCE_COORDINATES),
            "dimensionless_convention": (
                "m1=l1=g=1, m2=exp(u), l2=exp(v), tau=t*sqrt(g/l1), "
                "nu=dtheta/dtau"
            ),
            "clock_convention": (
                "epsilon is a shared scheduling dilation: actual terminal tau is "
                "exp(epsilon) times declared tau; dimensionless sensor units are held fixed"
            ),
            "calibration_convention": (
                "kappa is a small log multiplicative gain; a common-gain model is an "
                "optimistic control, while distinct theta2 and nu1 sensors receive "
                "independent gain parameters in the sensor-specific control"
            ),
            "preparation_convention": (
                "each launch independently refits errors in initial theta1 and theta2; "
                "initial dimensionless velocities remain fixed at zero"
            ),
            "common_mass_scale_blindness": (
                "m1,m2 -> c*m1,c*m2 leaves the normalized vector field unchanged and "
                "is excluded before this nuisance analysis"
            ),
        }
        if not _strict_json_equal(report.get("source_model"), expected_source_model):
            raise ValueError("source or nuisance conventions changed")
        verification = {
            "passed": True,
            "method": (
                "strict reconstruction of analytic serialized local-column formulas, "
                "refinement gates, rational declarations, exact rank/confounding algebra, "
                "and all exact child certificates"
            ),
            "ode_or_variational_system_replayed": False,
            "outward_ode_nuisance_validation_verified": False,
            "current_two_scalar_protocols_full_nuisance_floor_positive": False,
        }
        embedded = report.get("independent_verification")
        if embedded is not None and not _strict_json_equal(embedded, verification):
            raise ValueError("embedded independent verification is inconsistent")
        return verification
    except Exception as error:
        return {"passed": False, "error": str(error)}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.verify is not None:
        with args.verify.open("r", encoding="utf-8") as handle:
            report = json.load(handle)
        result = verify_structured_physical_nuisance_report(report)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["passed"] else 1
    report = build_structured_physical_nuisance_report()
    payload = json.dumps(report, indent=2, sort_keys=True)
    if args.output is None:
        print(payload)
    else:
        args.output.write_text(payload + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "SCHEMA_VERSION",
    "TIER_1_SCOPE",
    "build_structured_physical_nuisance_report",
    "verify_structured_physical_nuisance_report",
]
