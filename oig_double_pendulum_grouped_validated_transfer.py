#!/usr/bin/env python3
"""Outward transfer for the selected grouped protocol with shared clock nuisance.

This module composes two rigorous statements at the nominal point

    u = log(m2/m1) = 0,    v = log(l2/l1) = 0.

First, the Arb Picard--Taylor integrator from
``oig_double_pendulum_validated_transfer`` encloses the exact nonlinear state
and its two exact parameter sensitivities for five observations in launch
groups A and B.  The shared log-clock response is evaluated outwardly from the
same terminal state box using

    b_i = tau_i * d y_i / d tau_i.

Second, exact rational interval arithmetic encloses the augmented Gram matrix

    J = sum_i w_i [b_i, h_iu, h_iv]^T [b_i, h_iu, h_iv],

where the fixed grouped shares are (2/3, 1/3, 0), the group costs are
(7/2, 9/4, 5/2), and all five declared scalar noise precisions are one.  A
no-pivot interval LDL calculation proves

    J - diag(0, L, L) > 0.

Because the first pivot is the positive clock information, the Schur
complement theorem then proves that the clock-profiled two-source information
has floor strictly greater than L.  Both L=9/500 and the sharper
L=180269/10000000 are certified without sampled eigenvalues.

The theorem is deliberately narrow.  Preparation is exact, the clock model is
the local linear response to one unrestricted shared dilation, and "physical"
means only the exact response of the declared dimensionless nonlinear model.
There is no hardware, model-discrepancy, finite-clock-amplitude, parameter-
neighbourhood, or finite-grid optimality claim.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
import json
from pathlib import Path
from typing import Sequence

from flint import arb, ctx

from oig_double_pendulum_protocol import (
    PendulumProtocolCandidate,
    canonical_protocol_candidates,
)
import oig_double_pendulum_validated_transfer as validated


Q = Fraction
SCHEMA_VERSION = "oig-double-pendulum-grouped-physical-clock-floor-v1"
METHOD = "outward-arb-picard-taylor-plus-exact-rational-interval-ldl-v1"
EVIDENCE_TIER = "tier_3_fixed_model_local_nuisance_profile_certificate"
RATIONAL_HULL_DENOMINATOR = 10**15
SIMPLE_FLOOR = Q(9, 500)
SHARP_FLOOR = Q(180269, 10_000_000)

SOURCE_COORDINATES = (
    "u=log(m2/m1)",
    "v=log(l2/l1)",
)
AUGMENTED_COORDINATES = (
    "shared_log_clock_dilation",
    "u=log(m2/m1)",
    "v=log(l2/l1)",
)

GROUP_DECLARATIONS = (
    {
        "name": "launch-A grouped trajectory",
        "budget_share": Q(2, 3),
        "cost": Q(7, 2),
        "member_names": (
            "launch-A / theta-1 / tau-1",
            "launch-A / theta-2 / tau-1",
            "launch-A / scaled-omega-2 / tau-3/2",
        ),
    },
    {
        "name": "launch-B grouped trajectory",
        "budget_share": Q(1, 3),
        "cost": Q(9, 4),
        "member_names": (
            "launch-B / theta-1 / tau-3/4",
            "launch-B / scaled-omega-1 / tau-5/4",
        ),
    },
    {
        "name": "launch-C grouped trajectory",
        "budget_share": Q(0),
        "cost": Q(5, 2),
        "member_names": (),
    },
)

PHYSICAL_SCOPE_DEFINITION = (
    "Physical means the exact local parameter and clock response of the declared "
    "dimensionless nonlinear double-pendulum equations with m1=l1=g=1, "
    "m2=exp(u), and l2=exp(v). It does not mean that the equations, apparatus, "
    "calibration, noise model, or launch preparation have been empirically validated."
)

SCOPE_BOUNDARY = (
    "The theorem is pointwise at u=v=0 for the fixed grouped shares (2/3,1/3,0). "
    "It profiles one local unrestricted shared log-clock column after stacking all "
    "five outputs. Launch preparation is exact. The within-group output metric is "
    "the declared diagonal unit-precision metric. No parameter neighbourhood, "
    "finite clock-dilation amplitude, preparation error, model discrepancy, hardware "
    "calibration, candidate-selection transfer, grid optimality, or efficiency claim "
    "is made."
)

_SENSOR_INDEX = {
    "theta_1": 0,
    "theta_2": 1,
    "scaled_omega_1": 2,
    "scaled_omega_2": 3,
}


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


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


@dataclass(frozen=True)
class RationalInterval:
    """Closed exact rational interval with elementary outward operations."""

    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if type(self.lower) is not Fraction or type(self.upper) is not Fraction:
            raise TypeError("rational interval endpoints must be Fractions")
        if self.lower > self.upper:
            raise ValueError("rational interval endpoints are reversed")

    @classmethod
    def point(cls, value: Fraction) -> "RationalInterval":
        if type(value) is not Fraction:
            raise TypeError("an interval point must be a Fraction")
        return cls(value, value)

    def _coerce(self, other: object) -> "RationalInterval":
        if isinstance(other, RationalInterval):
            return other
        return RationalInterval.point(Q(other))  # type: ignore[arg-type]

    def __add__(self, other: object) -> "RationalInterval":
        right = self._coerce(other)
        return RationalInterval(self.lower + right.lower, self.upper + right.upper)

    __radd__ = __add__

    def __neg__(self) -> "RationalInterval":
        return RationalInterval(-self.upper, -self.lower)

    def __sub__(self, other: object) -> "RationalInterval":
        return self + (-self._coerce(other))

    def __rsub__(self, other: object) -> "RationalInterval":
        return self._coerce(other) - self

    def __mul__(self, other: object) -> "RationalInterval":
        right = self._coerce(other)
        products = (
            self.lower * right.lower,
            self.lower * right.upper,
            self.upper * right.lower,
            self.upper * right.upper,
        )
        return RationalInterval(min(products), max(products))

    __rmul__ = __mul__

    def reciprocal(self) -> "RationalInterval":
        if self.lower <= 0 <= self.upper:
            raise ZeroDivisionError("cannot invert an interval containing zero")
        return RationalInterval(1 / self.upper, 1 / self.lower)

    def __truediv__(self, other: object) -> "RationalInterval":
        return self * self._coerce(other).reciprocal()

    def record(self) -> dict[str, str]:
        return {
            "lower_exact": _fraction_text(self.lower),
            "upper_exact": _fraction_text(self.upper),
        }

    @classmethod
    def from_record(cls, record: object) -> "RationalInterval":
        if not isinstance(record, dict) or set(record) != {
            "lower_exact",
            "upper_exact",
        }:
            raise ValueError("malformed rational interval record")
        return cls(Q(record["lower_exact"]), Q(record["upper_exact"]))


@dataclass(frozen=True)
class SelectedObservation:
    candidate: PendulumProtocolCandidate
    group_name: str
    group_share: Fraction
    group_cost: Fraction

    @property
    def physical_weight(self) -> Fraction:
        return self.candidate.noise_precision * self.group_share / self.group_cost


def selected_observations() -> tuple[SelectedObservation, ...]:
    """Resolve the fixed five-output mixture against the canonical library."""

    candidates = {row.name: row for row in canonical_protocol_candidates()}
    selected: list[SelectedObservation] = []
    for group in GROUP_DECLARATIONS[:2]:
        names = group["member_names"]
        share = group["budget_share"]
        cost = group["cost"]
        if not isinstance(names, tuple) or type(share) is not Fraction or type(cost) is not Fraction:
            raise AssertionError("internal exact group declaration is malformed")
        members = tuple(candidates[name] for name in names)
        if sum((row.cost for row in members), Q(0)) != cost:
            raise AssertionError("group cost is not the sum of its scalar member costs")
        if any(row.noise_precision != 1 for row in members):
            raise AssertionError("this theorem expects the declared unit precisions")
        if any(row.launch != members[0].launch for row in members):
            raise AssertionError("a grouped protocol contains different launches")
        selected.extend(
            SelectedObservation(row, str(group["name"]), share, cost)
            for row in members
        )
    if len(selected) != 5:
        raise AssertionError("the fixed grouped mixture must contain five observations")
    if sum((Q(group["budget_share"]) for group in GROUP_DECLARATIONS), Q(0)) != 1:
        raise AssertionError("group budget shares do not sum to one")
    return tuple(selected)


def _outward_interval(value: arb) -> RationalInterval:
    lower, upper = validated._rational_outer_interval(  # type: ignore[attr-defined]
        value, RATIONAL_HULL_DENOMINATOR
    )
    if not (
        validated._arb_fraction(lower) < value  # type: ignore[attr-defined]
        and value < validated._arb_fraction(upper)  # type: ignore[attr-defined]
    ):
        raise ArithmeticError("fixed-denominator rational hull is not outward")
    return RationalInterval(lower, upper)


def _config_record(config: validated.ValidatedTransferConfig) -> dict[str, object]:
    return {
        "precision_bits": config.precision_bits,
        "taylor_order": config.taylor_order,
        "step_size_exact": _fraction_text(config.step_size),
        "tube_inflation_exact": _fraction_text(config.tube_inflation),
        "maximum_tube_iterations": config.maximum_tube_iterations,
        "rational_outer_hull_denominator_before_reduction": RATIONAL_HULL_DENOMINATOR,
    }


def _config_from_record(record: object) -> validated.ValidatedTransferConfig:
    if not isinstance(record, dict):
        raise ValueError("missing validated-transfer configuration")
    expected_keys = {
        "precision_bits",
        "taylor_order",
        "step_size_exact",
        "tube_inflation_exact",
        "maximum_tube_iterations",
        "rational_outer_hull_denominator_before_reduction",
    }
    if set(record) != expected_keys:
        raise ValueError("validated-transfer configuration fields changed")
    if record["rational_outer_hull_denominator_before_reduction"] != RATIONAL_HULL_DENOMINATOR:
        raise ValueError("unknown rational hull denominator")
    return validated.ValidatedTransferConfig(
        precision_bits=record["precision_bits"],  # type: ignore[arg-type]
        taylor_order=record["taylor_order"],  # type: ignore[arg-type]
        step_size=Q(record["step_size_exact"]),
        tube_inflation=Q(record["tube_inflation_exact"]),
        maximum_tube_iterations=record["maximum_tube_iterations"],  # type: ignore[arg-type]
    )


def _observation_records_at_current_precision(
    config: validated.ValidatedTransferConfig,
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    trajectory_cache: dict[
        tuple[tuple[Fraction, ...], Fraction], validated.ValidatedTrajectory
    ] = {}
    for selected in selected_observations():
        candidate = selected.candidate
        key = (candidate.launch, candidate.observation_time_tau)
        trajectory = trajectory_cache.get(key)
        if trajectory is None:
            trajectory = validated.validated_augmented_trajectory(
                candidate.launch, candidate.observation_time_tau, config
            )
            trajectory_cache[key] = trajectory
        sensor_index = _SENSOR_INDEX[candidate.sensor]
        with ctx.workprec(config.precision_bits):
            terminal_rhs = validated.augmented_rhs(trajectory.terminal)
            output = trajectory.terminal[sensor_index]
            response_u = trajectory.terminal[4 + sensor_index]
            response_v = trajectory.terminal[8 + sensor_index]
            clock = (
                validated._arb_fraction(candidate.observation_time_tau)  # type: ignore[attr-defined]
                * terminal_rhs[sensor_index]
            )
            output_box = _outward_interval(output)
            response_u_box = _outward_interval(response_u)
            response_v_box = _outward_interval(response_v)
            clock_box = _outward_interval(clock)
        records.append(
            {
                "name": candidate.name,
                "group_name": selected.group_name,
                "launch_exact": [_fraction_text(value) for value in candidate.launch],
                "sensor": candidate.sensor,
                "sensor_state_index": sensor_index,
                "observation_time_tau_exact": _fraction_text(
                    candidate.observation_time_tau
                ),
                "noise_precision_exact": _fraction_text(candidate.noise_precision),
                "legacy_scalar_cost_exact": _fraction_text(candidate.cost),
                "group_budget_share_exact": _fraction_text(selected.group_share),
                "group_cost_exact": _fraction_text(selected.group_cost),
                "physical_scalar_weight_exact": _fraction_text(
                    selected.physical_weight
                ),
                "sensor_output_outer_box_exact": output_box.record(),
                "parameter_response_outer_box_exact": {
                    "coordinates": list(SOURCE_COORDINATES),
                    "u": response_u_box.record(),
                    "v": response_v_box.record(),
                },
                "shared_clock_response_outer_box_exact": clock_box.record(),
                "joint_augmented_row_outer_box_exact": {
                    "coordinates": list(AUGMENTED_COORDINATES),
                    "entries": [
                        clock_box.record(),
                        response_u_box.record(),
                        response_v_box.record(),
                    ],
                    "semantics": (
                        "one Cartesian outer box; discarded trajectory correlations "
                        "make the subsequent interval theorem conservative"
                    ),
                },
                "clock_chain_rule": (
                    "at epsilon=0, d y(tau*exp(epsilon))/d epsilon "
                    "= tau*d y/d tau"
                ),
                "validated_step_count": trajectory.step_count,
                "maximum_picard_tube_iterations": trajectory.maximum_tube_iterations,
                "maximum_endpoint_radius_upper": float(
                    trajectory.maximum_endpoint_radius.abs_upper()
                ),
                "maximum_tube_radius_upper": float(
                    trajectory.maximum_tube_radius.abs_upper()
                ),
                "outward_joint_box_certified": True,
            }
        )
    return records


def _observation_records(
    config: validated.ValidatedTransferConfig,
) -> list[dict[str, object]]:
    """Build serialized rows solely at the certificate's declared precision.

    The validated trajectories retain Arb balls after their local precision
    context exits.  Their conversion to rational hulls and decimal audit
    fields must therefore be scoped too; otherwise ambient ``flint.ctx.prec``
    state left by an unrelated repository test can alter the JSON artifact.
    """

    with ctx.workprec(config.precision_bits):
        return _observation_records_at_current_precision(config)


def _zero_interval() -> RationalInterval:
    return RationalInterval.point(Q(0))


def _rows_from_records(
    records: Sequence[dict[str, object]],
) -> tuple[tuple[RationalInterval, RationalInterval, RationalInterval], ...]:
    rows = []
    for record in records:
        joint = record.get("joint_augmented_row_outer_box_exact")
        if not isinstance(joint, dict) or joint.get("coordinates") != list(
            AUGMENTED_COORDINATES
        ):
            raise ValueError("an augmented observation row has wrong coordinates")
        entries = joint.get("entries")
        if not isinstance(entries, list) or len(entries) != 3:
            raise ValueError("an augmented observation row must have three boxes")
        rows.append(tuple(RationalInterval.from_record(value) for value in entries))
    return tuple(rows)  # type: ignore[return-value]


def _weights_from_records(records: Sequence[dict[str, object]]) -> tuple[Fraction, ...]:
    weights = tuple(Q(record["physical_scalar_weight_exact"]) for record in records)
    if any(value <= 0 for value in weights):
        raise ValueError("every selected scalar observation must have positive weight")
    return weights


def _augmented_gram(
    rows: Sequence[Sequence[RationalInterval]],
    weights: Sequence[Fraction],
) -> tuple[tuple[RationalInterval, ...], ...]:
    if len(rows) != len(weights) or not rows:
        raise ValueError("augmented rows and weights are inconsistent")
    result = [[_zero_interval() for _ in range(3)] for _ in range(3)]
    for row, weight in zip(rows, weights):
        if len(row) != 3 or weight <= 0:
            raise ValueError("malformed weighted augmented row")
        for left in range(3):
            for right in range(3):
                result[left][right] = (
                    result[left][right] + weight * row[left] * row[right]
                )
    matrix = tuple(tuple(row) for row in result)
    if any(matrix[i][j] != matrix[j][i] for i in range(3) for j in range(3)):
        raise AssertionError("augmented interval Gram lost symmetry")
    return matrix


def _matrix_record(
    matrix: Sequence[Sequence[RationalInterval]],
) -> list[list[dict[str, str]]]:
    return [[entry.record() for entry in row] for row in matrix]


def _matrix_from_record(record: object) -> tuple[tuple[RationalInterval, ...], ...]:
    if not isinstance(record, list) or len(record) != 3:
        raise ValueError("interval matrix must have three rows")
    matrix = []
    for row in record:
        if not isinstance(row, list) or len(row) != 3:
            raise ValueError("interval matrix must be three by three")
        matrix.append(tuple(RationalInterval.from_record(value) for value in row))
    return tuple(matrix)


def _profile_information_interval(
    gram: Sequence[Sequence[RationalInterval]],
) -> tuple[tuple[RationalInterval, RationalInterval], ...]:
    d = gram[0][0]
    if d.lower <= 0:
        raise ArithmeticError("shared-clock information is not strictly positive")
    s00 = gram[1][1] - gram[0][1] * gram[0][1] / d
    s01 = gram[1][2] - gram[0][1] * gram[0][2] / d
    s11 = gram[2][2] - gram[0][2] * gram[0][2] / d
    return ((s00, s01), (s01, s11))


def _profile_matrix_record(
    matrix: Sequence[Sequence[RationalInterval]],
) -> list[list[dict[str, str]]]:
    return [[entry.record() for entry in row] for row in matrix]


def _interval_ldl_certificate(
    gram: Sequence[Sequence[RationalInterval]], floor: Fraction
) -> dict[str, object]:
    """Prove ``J-diag(0,floor,floor)`` positive definite by interval LDL."""

    if type(floor) is not Fraction or floor <= 0:
        raise ValueError("floor must be a positive Fraction")
    pivot_clock = gram[0][0]
    if pivot_clock.lower <= 0:
        raise ArithmeticError("clock pivot interval is not positive")
    schur_uu = (
        gram[1][1]
        - floor
        - gram[0][1] * gram[0][1] / pivot_clock
    )
    schur_uv = gram[1][2] - gram[0][1] * gram[0][2] / pivot_clock
    schur_vv = (
        gram[2][2]
        - floor
        - gram[0][2] * gram[0][2] / pivot_clock
    )
    if schur_uu.lower <= 0:
        raise ArithmeticError("second interval LDL pivot is not positive")
    final_pivot = schur_vv - schur_uv * schur_uv / schur_uu
    passed = bool(
        pivot_clock.lower > 0
        and schur_uu.lower > 0
        and final_pivot.lower > 0
    )
    return {
        "candidate_profiled_floor_exact": _fraction_text(floor),
        "block_tested": "J - diag(0,L,L)",
        "clock_pivot_outer_interval_exact": pivot_clock.record(),
        "source_schur_after_clock_outer_interval_exact": [
            [schur_uu.record(), schur_uv.record()],
            [schur_uv.record(), schur_vv.record()],
        ],
        "second_ldl_pivot_outer_interval_exact": schur_uu.record(),
        "third_ldl_pivot_outer_interval_exact": final_pivot.record(),
        "strict_lower_pivot_margins_exact": [
            _fraction_text(pivot_clock.lower),
            _fraction_text(schur_uu.lower),
            _fraction_text(final_pivot.lower),
        ],
        "all_interval_ldl_pivots_strictly_positive": passed,
        "sampled_eigenvalue_used_for_decision": False,
        "logical_implication": (
            "uniform block positivity and the positive clock pivot imply by the "
            "exact Schur-complement theorem that every enclosed clock-profiled "
            "two-source information form is strictly greater than L times identity"
        ),
    }


def _group_records() -> list[dict[str, object]]:
    return [
        {
            "name": str(group["name"]),
            "budget_share_exact": _fraction_text(Q(group["budget_share"])),
            "group_cost_exact": _fraction_text(Q(group["cost"])),
            "physical_batch_weight_exact": _fraction_text(
                Q(group["budget_share"]) / Q(group["cost"])
            ),
            "active": Q(group["budget_share"]) > 0,
            "validated_member_names": list(group["member_names"]),
        }
        for group in GROUP_DECLARATIONS
    ]


def _outward_box_summary(
    records: Sequence[dict[str, object]],
) -> dict[str, object]:
    parameter_half_widths: list[Fraction] = []
    clock_half_widths: list[Fraction] = []
    output_half_widths: list[Fraction] = []
    for record in records:
        parameter = record["parameter_response_outer_box_exact"]
        if not isinstance(parameter, dict):
            raise ValueError("parameter-response box is missing")
        for coordinate in ("u", "v"):
            interval = RationalInterval.from_record(parameter[coordinate])
            parameter_half_widths.append((interval.upper - interval.lower) / 2)
        clock = RationalInterval.from_record(
            record["shared_clock_response_outer_box_exact"]
        )
        output = RationalInterval.from_record(record["sensor_output_outer_box_exact"])
        clock_half_widths.append((clock.upper - clock.lower) / 2)
        output_half_widths.append((output.upper - output.lower) / 2)
    maximum_parameter = max(parameter_half_widths)
    maximum_clock = max(clock_half_widths)
    maximum_output = max(output_half_widths)
    return {
        "rational_outer_box_half_width_definition": "(upper-lower)/2",
        "maximum_parameter_response_half_width_exact": _fraction_text(
            maximum_parameter
        ),
        "maximum_parameter_response_half_width_decimal": float(maximum_parameter),
        "maximum_shared_clock_response_half_width_exact": _fraction_text(
            maximum_clock
        ),
        "maximum_shared_clock_response_half_width_decimal": float(maximum_clock),
        "maximum_sensor_output_half_width_exact": _fraction_text(maximum_output),
        "maximum_sensor_output_half_width_decimal": float(maximum_output),
        "maximum_trajectory_endpoint_radius_upper": max(
            float(record["maximum_endpoint_radius_upper"]) for record in records
        ),
        "maximum_picard_tube_radius_upper": max(
            float(record["maximum_tube_radius_upper"]) for record in records
        ),
    }


def _exact_algebra_verification(report: dict[str, object]) -> dict[str, object]:
    observations = report.get("observations")
    if not isinstance(observations, list) or len(observations) != 5:
        raise ValueError("the certificate must contain five observations")
    rows = _rows_from_records(observations)
    weights = _weights_from_records(observations)
    gram = _augmented_gram(rows, weights)
    serialized = report.get("exact_rational_interval_profile")
    if not isinstance(serialized, dict):
        raise ValueError("missing exact interval profile")
    serialized_gram = _matrix_from_record(
        serialized.get("augmented_gram_outer_interval_exact")
    )
    if serialized_gram != gram:
        raise ValueError("augmented Gram interval does not reproduce from row boxes")
    profile = _profile_information_interval(gram)
    if serialized.get("clock_profiled_information_outer_interval_exact") != _profile_matrix_record(
        profile
    ):
        raise ValueError("profiled information interval does not reproduce")
    simple = _interval_ldl_certificate(gram, SIMPLE_FLOOR)
    sharp = _interval_ldl_certificate(gram, SHARP_FLOOR)
    if serialized.get("simple_floor_certificate") != simple:
        raise ValueError("simple interval LDL certificate does not reproduce")
    if serialized.get("sharp_floor_certificate") != sharp:
        raise ValueError("sharp interval LDL certificate does not reproduce")
    if simple["all_interval_ldl_pivots_strictly_positive"] is not True:
        raise ValueError("simple floor interval LDL proof failed")
    if sharp["all_interval_ldl_pivots_strictly_positive"] is not True:
        raise ValueError("sharp floor interval LDL proof failed")
    return {
        "passed": True,
        "augmented_gram_recomputed_from_outward_boxes": True,
        "shared_clock_profile_recomputed_exactly": True,
        "simple_floor_exact": _fraction_text(SIMPLE_FLOOR),
        "sharp_floor_exact": _fraction_text(SHARP_FLOOR),
        "exact_interval_ldl_pivots_verified": True,
    }


def build_grouped_physical_clock_floor_certificate(
    config: validated.ValidatedTransferConfig = validated.ValidatedTransferConfig(),
) -> dict[str, object]:
    """Build the outward five-row response and nuisance-profiled floor theorem."""

    observations = _observation_records(config)
    rows = _rows_from_records(observations)
    weights = _weights_from_records(observations)
    gram = _augmented_gram(rows, weights)
    profile = _profile_information_interval(gram)
    simple = _interval_ldl_certificate(gram, SIMPLE_FLOOR)
    sharp = _interval_ldl_certificate(gram, SHARP_FLOOR)
    passed = bool(
        all(row["outward_joint_box_certified"] is True for row in observations)
        and simple["all_interval_ldl_pivots_strictly_positive"] is True
        and sharp["all_interval_ldl_pivots_strictly_positive"] is True
    )
    report: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "method": METHOD,
        "status": "proved" if passed else "unresolved",
        "evidence_tier": EVIDENCE_TIER,
        "source_model": {
            "coordinates": list(SOURCE_COORDINATES),
            "base_point_exact": ["0/1", "0/1"],
            "dimensionless_representative": (
                "m1=l1=g=1, m2=exp(u), l2=exp(v), "
                "tau=t*sqrt(g/l1), nu=dtheta/dtau"
            ),
            "query": "the full identity query in (u,v)",
        },
        "shared_clock_nuisance": {
            "parameter": "one unrestricted local log-clock dilation epsilon",
            "time_rule": "tau_actual=exp(epsilon)*tau_declared",
            "linear_response_at_epsilon_zero": "tau*d(sensor output)/d tau",
            "scope": (
                "one column is shared across every repetition, output, and active "
                "group and is profiled only after all five weighted rows are stacked"
            ),
            "finite_epsilon_nonlinear_robustness_claimed": False,
        },
        "validated_transfer_configuration": _config_record(config),
        "proof_dependency_contract": {
            "outward_scalar_arithmetic": "python-flint>=0.9,<0.10 (Arb)",
            "exact_interval_and_ldl_arithmetic": "Python fractions.Fraction",
            "ordinary_scipy_ode_solver_used_in_proof": False,
            "sampled_eigenvalue_used_in_floor_decision": False,
            "install_command": "python -m pip install -r requirements.txt",
        },
        "fixed_grouped_mixture": {
            "groups": _group_records(),
            "budget_shares_exact": ["2/3", "1/3", "0/1"],
            "active_output_count": 5,
            "batch_weight_rule": (
                "budget_share/group_cost multiplies the full within-group output metric"
            ),
            "within_group_output_metric": (
                "diagonal with the five canonical scalar noise precisions, all equal "
                "to one; this declares independent scalar readout noise"
            ),
            "candidate_selection_or_grid_optimality_claimed": False,
        },
        "observations": observations,
        "outward_box_summary": _outward_box_summary(observations),
        "all_five_outward_joint_boxes_certified": all(
            row["outward_joint_box_certified"] is True for row in observations
        ),
        "exact_rational_interval_profile": {
            "augmented_coordinate_order": list(AUGMENTED_COORDINATES),
            "augmented_gram_formula": (
                "J=sum_i w_i [b_i,h_iu,h_iv]^T[b_i,h_iu,h_iv]"
            ),
            "augmented_gram_outer_interval_exact": _matrix_record(gram),
            "clock_information_outer_interval_exact": gram[0][0].record(),
            "clock_profiled_information_outer_interval_exact": _profile_matrix_record(
                profile
            ),
            "interval_semantics": (
                "exact Cartesian rational interval arithmetic; every discarded "
                "correlation only enlarges the certified set"
            ),
            "simple_floor_certificate": simple,
            "sharp_floor_certificate": sharp,
        },
        "theorem": {
            "simple_human_readable_floor_lower_exact": _fraction_text(SIMPLE_FLOOR),
            "sharp_physical_clock_profiled_floor_lower_exact": _fraction_text(
                SHARP_FLOOR
            ),
            "strict_inequality": (
                "lambda_min(I_profiled)>180269/10000000>9/500 for every "
                "response-and-clock row in the five outward boxes"
            ),
            "source_metric_exact": [["1/1", "0/1"], ["0/1", "1/1"]],
            "positive_two_source_floor_certified": passed,
            "proof": (
                "exact rational interval enclosure of J, followed by a no-pivot "
                "interval LDL proof of J-diag(0,L,L)>0 and the exact Schur theorem"
            ),
        },
        "physical_scope_definition": PHYSICAL_SCOPE_DEFINITION,
        "scope_flags": {
            "declared_dimensionless_model_five_row_transfer_certified": passed,
            "fixed_grouped_mixture_shared_clock_floor_certified": passed,
            "exact_launch_preparation_assumed": True,
            "launch_preparation_error_bounded": False,
            "finite_clock_dilation_amplitude_certified": False,
            "parameter_neighborhood_uniformity_certified": False,
            "candidate_selection_transfer_certified": False,
            "finite_grid_optimality_certified": False,
            "empirical_model_adequacy_certified": False,
            "hardware_calibration_certified": False,
        },
        "scope_boundary": SCOPE_BOUNDARY,
        "reproduction_commands": [
            "python -m pip install -r requirements.txt",
            "python oig_double_pendulum_grouped_validated_transfer.py --output artifacts/double_pendulum_grouped_physical_clock_floor.json",
            "python oig_double_pendulum_grouped_validated_transfer.py --verify artifacts/double_pendulum_grouped_physical_clock_floor.json",
            "python -m unittest -v test_oig_double_pendulum_grouped_validated_transfer.py",
        ],
        "strict_internal_verification": {
            "passed": passed,
            "outward_ode_rows_recomputed": True,
            "exact_interval_gram_recomputed": True,
            "exact_interval_ldl_recomputed": True,
        },
    }
    algebra = _exact_algebra_verification(report)
    if algebra["passed"] is not True:
        raise AssertionError("internal exact algebra verification failed")
    return report


def verify_grouped_physical_clock_floor_certificate(
    report: dict[str, object],
) -> dict[str, object]:
    """Strictly reconstruct the outward ODE and exact interval proof artifact."""

    ode_recomputed = False
    algebra_verified = False
    try:
        if not isinstance(report, dict) or report.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unknown grouped physical clock-floor schema")
        if report.get("method") != METHOD or report.get("evidence_tier") != EVIDENCE_TIER:
            raise ValueError("proof method or evidence tier changed")
        if report.get("status") != "proved":
            raise ValueError("only a proved certificate can verify")
        if report.get("physical_scope_definition") != PHYSICAL_SCOPE_DEFINITION:
            raise ValueError("physical scope definition changed")
        if report.get("scope_boundary") != SCOPE_BOUNDARY:
            raise ValueError("scope boundary changed")
        flags = report.get("scope_flags")
        if not isinstance(flags, dict):
            raise ValueError("scope flags are missing")
        required_false = (
            "launch_preparation_error_bounded",
            "finite_clock_dilation_amplitude_certified",
            "parameter_neighborhood_uniformity_certified",
            "candidate_selection_transfer_certified",
            "finite_grid_optimality_certified",
            "empirical_model_adequacy_certified",
            "hardware_calibration_certified",
        )
        if any(flags.get(name) is not False for name in required_false):
            raise ValueError("a forbidden scope flag was promoted")
        if flags.get("exact_launch_preparation_assumed") is not True:
            raise ValueError("exact-preparation assumption was removed")
        algebra = _exact_algebra_verification(report)
        algebra_verified = algebra["passed"] is True
        config = _config_from_record(report.get("validated_transfer_configuration"))
        rebuilt = build_grouped_physical_clock_floor_certificate(config)
        ode_recomputed = True
        if not _strict_json_equal(report, rebuilt):
            raise ValueError("certificate differs from strict outward recomputation")
        return {
            "passed": True,
            "outward_ode_and_sensitivity_rows_recomputed": True,
            "shared_clock_rows_recomputed": True,
            "exact_rational_interval_gram_recomputed": True,
            "exact_interval_ldl_pivots_verified": True,
            "simple_floor_lower_exact": _fraction_text(SIMPLE_FLOOR),
            "sharp_floor_lower_exact": _fraction_text(SHARP_FLOOR),
            "preparation_error_bound_verified": False,
            "hardware_or_model_adequacy_verified": False,
        }
    except Exception as error:
        return {
            "passed": False,
            "outward_ode_and_sensitivity_rows_recomputed": ode_recomputed,
            "exact_rational_interval_algebra_verified": algebra_verified,
            "preparation_error_bound_verified": False,
            "hardware_or_model_adequacy_verified": False,
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
        verification = verify_grouped_physical_clock_floor_certificate(report)
        print(json.dumps(verification, indent=2, sort_keys=True))
        return 0 if verification["passed"] else 1
    report = build_grouped_physical_clock_floor_certificate()
    if args.output is not None:
        _write_json(args.output, report)
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "AUGMENTED_COORDINATES",
    "EVIDENCE_TIER",
    "GROUP_DECLARATIONS",
    "METHOD",
    "PHYSICAL_SCOPE_DEFINITION",
    "RATIONAL_HULL_DENOMINATOR",
    "RationalInterval",
    "SCHEMA_VERSION",
    "SCOPE_BOUNDARY",
    "SHARP_FLOOR",
    "SIMPLE_FLOOR",
    "build_grouped_physical_clock_floor_certificate",
    "selected_observations",
    "verify_grouped_physical_clock_floor_certificate",
]
