"""Double-pendulum parameter-identification adapter for the exact OIG engine.

The adapter has a deliberately hard epistemic boundary.  Numerical ODE solves,
finite differences, and refinement comparisons are Tier-1 discovery evidence.
They may be used to *declare* convenient rational response boxes, but they do
not prove that the derivative of the exact flow lies in those boxes.  Once a
box is declared, :func:`design_enclosed_protocols` proves a conditional exact
statement for every response matrix in that box.

Each protocol is an experimental triple: a launch state, a sensor, and a
dimensionless observation time.  The identifiable source coordinates are

``u = log(m2/m1)`` and ``v = log(l2/l1)``.

Common multiplication of both masses is retained as a blindness control and
is not silently included in the identifiable source space.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
import json
import math
from pathlib import Path
from typing import Sequence

import numpy as np

from double_pendulum_dynamics import (
    DoublePendulumParameters,
    IntegrationConfig,
    simulate_double_pendulum,
)
from oig_interval_protocol_design import (
    EnclosedProtocol,
    design_enclosed_protocols,
    verify_enclosed_design_report,
)
from oig_protocol_design_engine import ExactScalar, rational_matrix


Q = Fraction
SCHEMA_VERSION = "oig-double-pendulum-protocol-adapter-v1"
DISCOVERY_SCHEMA_VERSION = "oig-double-pendulum-response-discovery-v1"
COMMON_SCALE_SCHEMA_VERSION = "oig-double-pendulum-common-mass-scale-control-v1"

SOURCE_COORDINATES = (
    "log_mass_ratio=log(m2/m1)",
    "log_length_ratio=log(l2/l1)",
)

TIER1_BOUNDARY = (
    "Floating ODE integration, finite differences, and solver refinement are "
    "Tier-1 discovery evidence only. They neither enclose the exact nonlinear "
    "flow nor prove that its response derivative belongs to a declared box."
)
PROOF_BOUNDARY = (
    "The exact child proves protocol-design guarantees for every response in "
    "the explicitly declared rational boxes. This adapter verifier does not "
    "verify, and the report does not claim, that the double-pendulum ODE or its "
    "parameter derivatives lie in those boxes."
)

_SENSOR_DEFINITIONS = {
    "theta_1": "unwrapped absolute theta_1 (dimensionless radians)",
    "theta_2": "unwrapped absolute theta_2 (dimensionless radians)",
    "scaled_omega_1": "sqrt(l1/g) times omega_1",
    "scaled_omega_2": "sqrt(l1/g) times omega_2",
}


def _q(value: ExactScalar) -> Fraction:
    if isinstance(value, float):
        raise TypeError("exact declarations reject binary floating-point values")
    return Fraction(value)


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _matrix_text(matrix: Sequence[Sequence[Fraction]]) -> list[list[str]]:
    return [[_fraction_text(value) for value in row] for row in matrix]


def _finite_positive(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


@dataclass(frozen=True)
class PendulumProtocolCandidate:
    """Exact declaration of a launch/sensor/time experimental protocol."""

    name: str
    launch: tuple[Fraction, Fraction, Fraction, Fraction]
    sensor: str
    observation_time_tau: Fraction
    noise_precision: Fraction = Q(1)
    cost: Fraction = Q(1)

    @classmethod
    def from_values(
        cls,
        name: str,
        launch: Sequence[ExactScalar],
        sensor: str,
        observation_time_tau: ExactScalar,
        *,
        noise_precision: ExactScalar = 1,
        cost: ExactScalar = 1,
    ) -> "PendulumProtocolCandidate":
        if not isinstance(name, str) or not name.strip():
            raise ValueError("a candidate name must be nonempty")
        if len(launch) != 4:
            raise ValueError("launch must be [theta1, theta2, omega1, omega2]")
        exact_launch = tuple(_q(value) for value in launch)
        if sensor not in _SENSOR_DEFINITIONS:
            raise ValueError(f"unknown sensor {sensor!r}")
        tau = _q(observation_time_tau)
        precision = _q(noise_precision)
        exact_cost = _q(cost)
        if tau <= 0:
            raise ValueError("observation_time_tau must be positive")
        if precision <= 0 or exact_cost <= 0:
            raise ValueError("noise precision and cost must be positive")
        return cls(
            name.strip(),
            exact_launch,  # type: ignore[arg-type]
            sensor,
            tau,
            precision,
            exact_cost,
        )

    def declaration(self) -> dict[str, object]:
        return {
            "name": self.name,
            "launch": {
                "state_convention": ["theta1", "theta2", "omega1", "omega2"],
                "state_exact": [_fraction_text(value) for value in self.launch],
            },
            "sensor": {
                "name": self.sensor,
                "dimensionless_output_definition": _SENSOR_DEFINITIONS[self.sensor],
            },
            "observation_time": {
                "dimensionless_tau_exact": _fraction_text(self.observation_time_tau),
                "physical_time_rule": "t=tau*sqrt(l1/g)",
            },
            "noise_precision_exact": _fraction_text(self.noise_precision),
            "cost_exact": _fraction_text(self.cost),
        }


@dataclass(frozen=True)
class DeclaredPendulumResponseBox:
    """An exact conditional response box attached to an explicit protocol."""

    candidate: PendulumProtocolCandidate
    response_centre: tuple[Fraction, Fraction]
    response_radius: tuple[Fraction, Fraction]

    @classmethod
    def from_values(
        cls,
        candidate: PendulumProtocolCandidate,
        response_centre: Sequence[ExactScalar],
        response_radius: Sequence[ExactScalar],
    ) -> "DeclaredPendulumResponseBox":
        if len(response_centre) != 2 or len(response_radius) != 2:
            raise ValueError("responses must have the two declared source coordinates")
        centre = tuple(_q(value) for value in response_centre)
        radius = tuple(_q(value) for value in response_radius)
        if any(value < 0 for value in radius):
            raise ValueError("response radii must be nonnegative")
        return cls(candidate, centre, radius)  # type: ignore[arg-type]

    def enclosed_protocol(self) -> EnclosedProtocol:
        return EnclosedProtocol.from_rows(
            self.candidate.name,
            [self.response_centre],
            [self.response_radius],
            [[self.candidate.noise_precision]],
            self.candidate.cost,
        )

    def record(self) -> dict[str, object]:
        return {
            "candidate": self.candidate.declaration(),
            "source_coordinates": list(SOURCE_COORDINATES),
            "response_centre_exact": _matrix_text((self.response_centre,)),
            "response_radius_exact": _matrix_text((self.response_radius,)),
            "box_status": "exact rational declaration; external ODE membership unproved",
        }


def canonical_protocol_candidates() -> tuple[PendulumProtocolCandidate, ...]:
    """Return a finite launch/sensor/time library for nonlinear identification."""
    launch_a = (Q(4, 5), Q(-7, 20), Q(0), Q(0))
    launch_b = (Q(-3, 5), Q(9, 10), Q(0), Q(0))
    launch_c = (Q(6, 5), Q(2, 5), Q(0), Q(0))
    return (
        PendulumProtocolCandidate.from_values(
            "launch-A / theta-1 / tau-1", launch_a, "theta_1", 1
        ),
        PendulumProtocolCandidate.from_values(
            "launch-A / theta-2 / tau-1", launch_a, "theta_2", 1
        ),
        PendulumProtocolCandidate.from_values(
            "launch-A / scaled-omega-2 / tau-3/2",
            launch_a,
            "scaled_omega_2",
            Q(3, 2),
            cost=Q(3, 2),
        ),
        PendulumProtocolCandidate.from_values(
            "launch-B / theta-1 / tau-3/4",
            launch_b,
            "theta_1",
            Q(3, 4),
        ),
        PendulumProtocolCandidate.from_values(
            "launch-B / scaled-omega-1 / tau-5/4",
            launch_b,
            "scaled_omega_1",
            Q(5, 4),
            cost=Q(5, 4),
        ),
        PendulumProtocolCandidate.from_values(
            "launch-C / theta-2 / tau-1", launch_c, "theta_2", 1
        ),
        PendulumProtocolCandidate.from_values(
            "launch-C / scaled-omega-2 / tau-3/2",
            launch_c,
            "scaled_omega_2",
            Q(3, 2),
            cost=Q(3, 2),
        ),
    )


def _parameters(
    log_mass_ratio: float,
    log_length_ratio: float,
    *,
    log_common_mass_scale: float = 0.0,
) -> DoublePendulumParameters:
    """Dimensionless representative of the declared source coordinates."""
    values = (log_mass_ratio, log_length_ratio, log_common_mass_scale)
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("log-parameters must be finite")
    common = math.exp(float(log_common_mass_scale))
    return DoublePendulumParameters(
        m1=common,
        m2=common * math.exp(float(log_mass_ratio)),
        l1=1.0,
        l2=math.exp(float(log_length_ratio)),
        g=1.0,
    )


def _observe(
    candidate: PendulumProtocolCandidate,
    parameters: DoublePendulumParameters,
    integration: IntegrationConfig,
) -> tuple[float, float]:
    tau = float(candidate.observation_time_tau)
    physical_time = tau * math.sqrt(parameters.l1 / parameters.g)
    trajectory = simulate_double_pendulum(
        [float(value) for value in candidate.launch],
        [0.0, physical_time],
        parameters,
        integration,
    )
    final = trajectory.states[-1]
    if candidate.sensor == "theta_1":
        observation = final[0]
    elif candidate.sensor == "theta_2":
        observation = final[1]
    elif candidate.sensor == "scaled_omega_1":
        observation = math.sqrt(parameters.l1 / parameters.g) * final[2]
    elif candidate.sensor == "scaled_omega_2":
        observation = math.sqrt(parameters.l1 / parameters.g) * final[3]
    else:  # guarded by the exact candidate constructor
        raise AssertionError("unsupported sensor")
    return float(observation), float(trajectory.max_scaled_energy_drift)


def _central_response(
    candidate: PendulumProtocolCandidate,
    *,
    base_log_mass_ratio: float,
    base_log_length_ratio: float,
    step: float,
    integration: IntegrationConfig,
) -> tuple[list[float], float]:
    response: list[float] = []
    maximum_energy_drift = 0.0
    base = [float(base_log_mass_ratio), float(base_log_length_ratio)]
    for coordinate in range(2):
        outputs: list[float] = []
        for sign in (1.0, -1.0):
            shifted = list(base)
            shifted[coordinate] += sign * step
            value, drift = _observe(
                candidate,
                _parameters(shifted[0], shifted[1]),
                integration,
            )
            outputs.append(value)
            maximum_energy_drift = max(maximum_energy_drift, drift)
        response.append((outputs[0] - outputs[1]) / (2.0 * step))
    return response, maximum_energy_drift


def discover_candidate_response(
    candidate: PendulumProtocolCandidate,
    *,
    base_log_mass_ratio: float = 0.0,
    base_log_length_ratio: float = 0.0,
    finite_difference_step: float = 2.0e-4,
    integration: IntegrationConfig = IntegrationConfig(
        rtol=1.0e-9,
        atol=1.0e-11,
        max_step=0.02,
        energy_drift_tolerance=1.0e-7,
    ),
) -> dict[str, object]:
    """Discover a two-coordinate response with two numerical refinements.

    The returned data are intentionally not accepted directly by the exact
    engine.  :func:`declare_box_from_tier1` performs the explicit transition
    from numerical evidence to a conditional rational declaration.
    """
    step = _finite_positive(finite_difference_step, "finite_difference_step")
    if not math.isfinite(float(base_log_mass_ratio)) or not math.isfinite(
        float(base_log_length_ratio)
    ):
        raise ValueError("base log-ratios must be finite")
    refined = integration.refined()
    coarse_step, coarse_drift = _central_response(
        candidate,
        base_log_mass_ratio=base_log_mass_ratio,
        base_log_length_ratio=base_log_length_ratio,
        step=step,
        integration=integration,
    )
    coarse_half, half_drift = _central_response(
        candidate,
        base_log_mass_ratio=base_log_mass_ratio,
        base_log_length_ratio=base_log_length_ratio,
        step=step / 2.0,
        integration=integration,
    )
    refined_half, refined_drift = _central_response(
        candidate,
        base_log_mass_ratio=base_log_mass_ratio,
        base_log_length_ratio=base_log_length_ratio,
        step=step / 2.0,
        integration=refined,
    )
    estimates = (coarse_step, coarse_half, refined_half)
    spread = [
        max(abs(row[column] - refined_half[column]) for row in estimates)
        for column in range(2)
    ]
    return {
        "schema_version": DISCOVERY_SCHEMA_VERSION,
        "claim_tier": 1,
        "status": "unverified numerical discovery evidence",
        "candidate": candidate.declaration(),
        "source_coordinates": list(SOURCE_COORDINATES),
        "base_log_ratios": {
            "log_mass_ratio": float(base_log_mass_ratio),
            "log_length_ratio": float(base_log_length_ratio),
        },
        "finite_difference_steps": [step, step / 2.0],
        "response_estimates": {
            "coarse_step": coarse_step,
            "coarse_half_step": coarse_half,
            "refined_solver_half_step": refined_half,
        },
        "selected_tier1_response_estimate": refined_half,
        "max_refinement_spread_by_source": spread,
        "maximum_sampled_scaled_energy_drift": max(
            coarse_drift, half_drift, refined_drift
        ),
        "proof_boundary": TIER1_BOUNDARY,
    }


def _ceil_to_grid(value: Fraction, denominator: int) -> Fraction:
    if type(denominator) is not int or denominator < 1:
        raise ValueError("grid denominator must be a positive integer")
    scaled = value * denominator
    quotient, remainder = divmod(scaled.numerator, scaled.denominator)
    return Q(quotient + int(remainder != 0), denominator)


def declare_box_from_tier1(
    candidate: PendulumProtocolCandidate,
    discovery: dict[str, object],
    *,
    centre_denominator: int = 10_000,
    radius_denominator: int = 100_000,
    declared_padding: ExactScalar = Q(1, 1000),
) -> DeclaredPendulumResponseBox:
    """Declare a rational box containing the serialized Tier-1 cross-checks.

    Containment of these finite numerical values is not containment of the
    exact ODE response.  ``declared_padding`` is an assumption margin, not an
    a-posteriori validated numerical error bound.
    """
    if discovery.get("schema_version") != DISCOVERY_SCHEMA_VERSION:
        raise ValueError("unknown Tier-1 response discovery schema")
    if discovery.get("claim_tier") != 1 or discovery.get("proof_boundary") != TIER1_BOUNDARY:
        raise ValueError("the discovery record lacks its Tier-1 boundary")
    if discovery.get("candidate") != candidate.declaration():
        raise ValueError("the discovery record belongs to a different candidate")
    if discovery.get("source_coordinates") != list(SOURCE_COORDINATES):
        raise ValueError("the discovery source coordinates differ")
    if type(centre_denominator) is not int or centre_denominator < 1:
        raise ValueError("centre_denominator must be a positive integer")
    padding = _q(declared_padding)
    if padding < 0:
        raise ValueError("declared_padding must be nonnegative")

    estimate = discovery["selected_tier1_response_estimate"]
    rows = discovery["response_estimates"]
    if not isinstance(estimate, list) or len(estimate) != 2 or not isinstance(rows, dict):
        raise ValueError("malformed Tier-1 response data")
    variants = tuple(rows.get(key) for key in (
        "coarse_step", "coarse_half_step", "refined_solver_half_step"
    ))
    if any(not isinstance(row, list) or len(row) != 2 for row in variants):
        raise ValueError("malformed Tier-1 refinement variants")
    flat = [float(value) for row in variants for value in row]  # type: ignore[union-attr]
    if not all(math.isfinite(value) for value in flat):
        raise ValueError("Tier-1 response values must be finite")

    centre = tuple(
        Q(str(float(value))).limit_denominator(centre_denominator)
        for value in estimate
    )
    radius: list[Fraction] = []
    for column in range(2):
        serialized = [
            Q(str(float(row[column])))  # type: ignore[index]
            for row in variants
        ]
        needed = max(abs(value - centre[column]) for value in serialized) + padding
        radius.append(_ceil_to_grid(needed, radius_denominator))
    return DeclaredPendulumResponseBox(candidate, centre, tuple(radius))  # type: ignore[arg-type]


def common_mass_scale_blindness_control(
    candidate: PendulumProtocolCandidate,
    *,
    log_mass_ratio: float = 0.0,
    log_length_ratio: float = 0.0,
    log_scale_step: float = 0.2,
    integration: IntegrationConfig = IntegrationConfig(
        rtol=1.0e-9,
        atol=1.0e-11,
        max_step=0.02,
        energy_drift_tolerance=1.0e-7,
    ),
) -> dict[str, object]:
    """Numerically probe the analytically blind common mass-scale direction."""
    step = _finite_positive(log_scale_step, "log_scale_step")
    outputs: list[float] = []
    drifts: list[float] = []
    for sign in (1.0, -1.0):
        value, drift = _observe(
            candidate,
            _parameters(
                log_mass_ratio,
                log_length_ratio,
                log_common_mass_scale=sign * step,
            ),
            integration,
        )
        outputs.append(value)
        drifts.append(drift)
    return {
        "schema_version": COMMON_SCALE_SCHEMA_VERSION,
        "claim_tier": 1,
        "candidate": candidate.declaration(),
        "log_scale_step": step,
        "central_finite_difference": (outputs[0] - outputs[1]) / (2.0 * step),
        "paired_observations": outputs,
        "maximum_sampled_scaled_energy_drift": max(drifts),
        "structural_reason": (
            "m1,m2 -> c*m1,c*m2 multiplies both M(theta) and f(theta,omega) "
            "by c, so M^{-1}f and every supported state sensor are unchanged"
        ),
        "expected_exact_response_in_common_scale_direction": "0/1",
        "proof_boundary": TIER1_BOUNDARY,
    }


def _source_record() -> dict[str, object]:
    return {
        "coordinates": list(SOURCE_COORDINATES),
        "dimension": 2,
        "dimensionless": True,
        "metric_exact": [["1/1", "0/1"], ["0/1", "1/1"]],
    }


def _common_scale_exact_record(boxes: Sequence[DeclaredPendulumResponseBox]) -> dict[str, object]:
    return {
        "omitted_coordinate": "log_common_mass_scale=log(c), m1,m2 -> c*m1,c*m2",
        "structural_identity": "M -> c*M and f -> c*f, hence M^{-1}f is unchanged",
        "declared_exact_response_column": "0/1",
        "extended_source_control_vector_exact": ["0/1", "0/1", "1/1"],
        "candidate_actions_exact": [
            {"name": box.candidate.name, "response_on_control_exact": ["0/1"]}
            for box in boxes
        ],
        "control_conclusion": (
            "common mass scale is a declared blind direction and is excluded "
            "from the two-dimensional identifiable design quotient"
        ),
    }


def _conditional_claim() -> dict[str, object]:
    return {
        "response_boxes_are_declared_assumptions": True,
        "exact_design_is_conditional_on_box_membership": True,
        "double_pendulum_ode_membership_certified": False,
        "tier1_discovery_promoted_to_enclosure": False,
    }


def _candidate_from_record(record: object) -> PendulumProtocolCandidate:
    if not isinstance(record, dict):
        raise ValueError("candidate declaration must be an object")
    launch = record.get("launch")
    sensor = record.get("sensor")
    observation = record.get("observation_time")
    if not isinstance(launch, dict) or not isinstance(sensor, dict) or not isinstance(observation, dict):
        raise ValueError("candidate lacks launch, sensor, or observation time")
    candidate = PendulumProtocolCandidate.from_values(
        str(record.get("name")),
        launch.get("state_exact", ()),
        str(sensor.get("name")),
        observation.get("dimensionless_tau_exact"),  # type: ignore[arg-type]
        noise_precision=record.get("noise_precision_exact"),  # type: ignore[arg-type]
        cost=record.get("cost_exact"),  # type: ignore[arg-type]
    )
    if candidate.declaration() != record:
        raise ValueError("candidate declaration does not reproduce strictly")
    return candidate


def _verification_payload(candidate_count: int) -> dict[str, object]:
    return {
        "passed": True,
        "exact_enclosed_design_verified": True,
        "declared_box_adapter_verified": True,
        "candidate_count": candidate_count,
        "double_pendulum_ode_membership_verified": False,
        "tier1_numerics_recomputed": False,
        "method": (
            "exact child verification and strict rational adapter reconstruction; "
            "no ODE solve or floating finite-difference acceptance"
        ),
    }


def verify_double_pendulum_protocol_report(report: dict[str, object]) -> dict[str, object]:
    """Verify the conditional exact child without asserting ODE membership."""
    try:
        if not isinstance(report, dict) or report.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unknown double-pendulum protocol adapter schema")
        if report.get("source_model") != _source_record():
            raise ValueError("source-coordinate declaration is inconsistent")
        if report.get("conditional_claim") != _conditional_claim():
            raise ValueError("conditional claim boundary is inconsistent")
        if report.get("proof_boundary") != PROOF_BOUNDARY:
            raise ValueError("proof boundary is inconsistent")

        rows = report.get("candidate_response_boxes")
        if not isinstance(rows, list) or not rows:
            raise ValueError("candidate_response_boxes must be nonempty")
        boxes: list[DeclaredPendulumResponseBox] = []
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("a response-box row is malformed")
            candidate = _candidate_from_record(row.get("candidate"))
            if row.get("source_coordinates") != list(SOURCE_COORDINATES):
                raise ValueError("a response box uses different source coordinates")
            centre_matrix = rational_matrix(row.get("response_centre_exact"))  # type: ignore[arg-type]
            radius_matrix = rational_matrix(row.get("response_radius_exact"))  # type: ignore[arg-type]
            if len(centre_matrix) != 1 or len(centre_matrix[0]) != 2:
                raise ValueError("a response centre has the wrong shape")
            if len(radius_matrix) != 1 or len(radius_matrix[0]) != 2:
                raise ValueError("a response radius has the wrong shape")
            box = DeclaredPendulumResponseBox.from_values(
                candidate, centre_matrix[0], radius_matrix[0]
            )
            if box.record() != row:
                raise ValueError("a response-box declaration does not reproduce")
            boxes.append(box)
        if len({box.candidate.name for box in boxes}) != len(boxes):
            raise ValueError("candidate names must be unique")

        if report.get("common_mass_scale_blindness_control") != _common_scale_exact_record(boxes):
            raise ValueError("common mass-scale blindness control is inconsistent")
        child = report.get("exact_enclosed_design")
        if not isinstance(child, dict):
            raise ValueError("exact enclosed-design child is missing")
        child_verification = verify_enclosed_design_report(child)
        if child_verification.get("passed") is not True:
            raise ValueError("exact enclosed-design child fails verification")
        if child.get("declared_source_metric") != _source_record()["metric_exact"]:
            raise ValueError("child source metric differs from the adapter metric")
        child_protocols = child.get("protocols")
        child_bounds = child.get("response_box_robustness", {}).get(  # type: ignore[union-attr]
            "protocol_response_box_certificates"
        )
        if not isinstance(child_protocols, list) or not isinstance(child_bounds, list):
            raise ValueError("child protocol declarations are malformed")
        if len(child_protocols) != len(boxes) or len(child_bounds) != len(boxes):
            raise ValueError("child and adapter candidate counts differ")
        for box, protocol, bound in zip(boxes, child_protocols, child_bounds):
            if not isinstance(protocol, dict) or not isinstance(bound, dict):
                raise ValueError("child protocol row is malformed")
            expected_centre = _matrix_text((box.response_centre,))
            expected_radius = _matrix_text((box.response_radius,))
            if (
                protocol.get("name") != box.candidate.name
                or protocol.get("response_exact") != expected_centre
                or protocol.get("noise_precision_exact")
                != [[_fraction_text(box.candidate.noise_precision)]]
                or protocol.get("cost_exact") != _fraction_text(box.candidate.cost)
                or bound.get("response_centre_exact") != expected_centre
                or bound.get("response_radius_exact") != expected_radius
            ):
                raise ValueError("child response box differs from adapter declaration")

        discoveries = report.get("tier1_discovery_only")
        if not isinstance(discoveries, list):
            raise ValueError("tier1_discovery_only must be a list")
        declarations = {box.candidate.name: box.candidate.declaration() for box in boxes}
        for discovery in discoveries:
            if not isinstance(discovery, dict):
                raise ValueError("a Tier-1 discovery record is malformed")
            candidate = discovery.get("candidate")
            name = candidate.get("name") if isinstance(candidate, dict) else None
            if (
                discovery.get("schema_version") != DISCOVERY_SCHEMA_VERSION
                or discovery.get("claim_tier") != 1
                or discovery.get("status") != "unverified numerical discovery evidence"
                or discovery.get("source_coordinates") != list(SOURCE_COORDINATES)
                or discovery.get("proof_boundary") != TIER1_BOUNDARY
                or candidate != declarations.get(name)
            ):
                raise ValueError("a Tier-1 discovery record crosses the proof boundary")

        expected = _verification_payload(len(boxes))
        embedded = report.get("independent_verification")
        if embedded is not None and embedded != expected:
            raise ValueError("embedded adapter verification does not reproduce")
        return expected
    except Exception as error:
        return {
            "passed": False,
            "double_pendulum_ode_membership_verified": False,
            "error": str(error),
        }


def design_declared_double_pendulum_protocols(
    boxes: Sequence[DeclaredPendulumResponseBox],
    *,
    tier1_discoveries: Sequence[dict[str, object]] = (),
    weight_denominator: int = 10_000,
    dual_vector_scale: int = 100_000,
    amplitude: ExactScalar = 1,
    exposure_multiplier: int = 10,
) -> dict[str, object]:
    """Run exact OIG design conditionally on declared rational response boxes."""
    declared = tuple(boxes)
    if not declared:
        raise ValueError("at least one declared response box is required")
    if len({box.candidate.name for box in declared}) != len(declared):
        raise ValueError("candidate names must be unique")
    child = design_enclosed_protocols(
        [box.enclosed_protocol() for box in declared],
        [[1, 0], [0, 1]],
        weight_denominator=weight_denominator,
        dual_vector_scale=dual_vector_scale,
        amplitude=amplitude,
        exposure_multiplier=exposure_multiplier,
    )
    report: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "status": "exact conditional design over declared double-pendulum response boxes",
        "source_model": _source_record(),
        "candidate_response_boxes": [box.record() for box in declared],
        "common_mass_scale_blindness_control": _common_scale_exact_record(declared),
        "tier1_discovery_only": deepcopy(list(tier1_discoveries)),
        "exact_enclosed_design": child,
        "conditional_claim": _conditional_claim(),
        "proof_boundary": PROOF_BOUNDARY,
    }
    verification = verify_double_pendulum_protocol_report(report)
    if verification.get("passed") is not True:
        raise AssertionError(f"adapter self-verification failed: {verification}")
    report["independent_verification"] = verification
    return report


def build_canonical_double_pendulum_protocol_report() -> dict[str, object]:
    """Run the canonical Tier-1 discovery and exact conditional design chain."""
    candidates = canonical_protocol_candidates()
    discoveries = tuple(discover_candidate_response(candidate) for candidate in candidates)
    boxes = tuple(
        declare_box_from_tier1(candidate, discovery)
        for candidate, discovery in zip(candidates, discoveries)
    )
    return design_declared_double_pendulum_protocols(
        boxes, tier1_discoveries=discoveries
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    if arguments.verify is not None:
        if arguments.output is not None:
            raise ValueError("--output and --verify cannot be combined")
        report = json.loads(arguments.verify.read_text(encoding="utf-8"))
        verification = verify_double_pendulum_protocol_report(report)
        print(json.dumps(verification, indent=2, sort_keys=True))
        return 0 if verification.get("passed") is True else 1
    report = build_canonical_double_pendulum_protocol_report()
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if arguments.output is None:
        print(payload, end="")
    else:
        arguments.output.write_text(payload, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "COMMON_SCALE_SCHEMA_VERSION",
    "DISCOVERY_SCHEMA_VERSION",
    "DeclaredPendulumResponseBox",
    "PendulumProtocolCandidate",
    "PROOF_BOUNDARY",
    "SCHEMA_VERSION",
    "SOURCE_COORDINATES",
    "TIER1_BOUNDARY",
    "build_canonical_double_pendulum_protocol_report",
    "canonical_protocol_candidates",
    "common_mass_scale_blindness_control",
    "declare_box_from_tier1",
    "design_declared_double_pendulum_protocols",
    "discover_candidate_response",
    "main",
    "verify_double_pendulum_protocol_report",
]
