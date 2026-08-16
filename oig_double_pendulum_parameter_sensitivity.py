#!/usr/bin/env python3
"""Tier-1 analytic log-ratio sensitivities for two active OIG protocols.

The independent variable is the dimensionless time

    tau = t * sqrt(g / l1),

and the velocity coordinates are ``nu_i = d theta_i / d tau``.  After
dividing the mechanics by ``m1 * g * l1``, the vector field depends only on

    u = log(m2 / m1),    v = log(l2 / l1).

For a fixed, parameter-independent launch, the state sensitivity matrix
``S = D_(u,v) z`` solves the inhomogeneous tangent equation

    S' = D_z F(z; u, v) S + D_(u,v) F(z; u, v),    S(0) = 0.

Both derivatives on the right are analytic.  The integration, refinement,
and finite-difference comparisons remain Tier-1 numerical evidence: this
module does not outwardly enclose the exact flow or its parameter derivative.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
import json
import math
from pathlib import Path
from typing import Sequence

import numpy as np
from scipy.integrate import solve_ivp

from double_pendulum_dynamics import (
    DoublePendulumParameters,
    EnergyDriftError,
    IntegrationConfig,
    double_pendulum_rhs,
    mass_matrix,
    simulate_double_pendulum,
    total_energy,
)
from double_pendulum_variational import double_pendulum_rhs_jacobian
from oig_double_pendulum_protocol import (
    PendulumProtocolCandidate,
    canonical_protocol_candidates,
)


Array = np.ndarray
SCHEMA_VERSION = "oig-double-pendulum-parameter-sensitivity-v1"
TIER_1_SCOPE = "tier_1_numerical_not_outward_validated"
SOURCE_COORDINATES = (
    "u=log(m2/m1)",
    "v=log(l2/l1)",
)
ACTIVE_PROTOCOL_NAMES = (
    "launch-A / theta-2 / tau-1",
    "launch-B / scaled-omega-1 / tau-5/4",
)
PROOF_BOUNDARY = (
    "Analytic variational equations, DOP853 integration, solver refinement, "
    "and multiscale centred differences are Tier-1 numerical evidence. They "
    "do not provide outward containment of the exact state or parameter "
    "sensitivity and do not certify membership in an exact response box."
)


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _state(value: Array | Sequence[float]) -> Array:
    result = np.asarray(value, dtype=float)
    if result.shape != (4,) or not np.all(np.isfinite(result)):
        raise ValueError(
            "dimensionless_state must be [theta1, theta2, nu1, nu2]"
        )
    return result


def _times(value: Array | Sequence[float]) -> Array:
    result = np.asarray(value, dtype=float)
    if (
        result.ndim != 1
        or len(result) < 2
        or not np.all(np.isfinite(result))
        or result[0] < 0.0
        or np.any(np.diff(result) <= 0.0)
    ):
        raise ValueError(
            "dimensionless_times must be finite, nonnegative, and strictly increasing"
        )
    return result


def _readonly(value: Array | Sequence[float]) -> Array:
    result = np.array(value, dtype=float, copy=True)
    result.setflags(write=False)
    return result


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _integration_record(config: IntegrationConfig) -> dict[str, object]:
    return {
        "method": "DOP853",
        "rtol": config.rtol,
        "atol": config.atol,
        "max_step_in_tau": config.max_step,
        "sampled_scaled_energy_drift_tolerance": config.energy_drift_tolerance,
    }


def dimensionless_parameters(
    log_mass_ratio: float,
    log_length_ratio: float,
) -> DoublePendulumParameters:
    """Return the normalized representative ``m1=l1=g=1``.

    Any positive common mass scale produces the same vector field.  Physical
    length and gravity scales are removed by ``tau`` and ``nu``.
    """

    u = _finite(log_mass_ratio, "log_mass_ratio")
    v = _finite(log_length_ratio, "log_length_ratio")
    try:
        mass_ratio = math.exp(u)
        length_ratio = math.exp(v)
    except OverflowError as error:
        raise ValueError("log-ratios must exponentiate to finite values") from error
    if not math.isfinite(mass_ratio) or not math.isfinite(length_ratio):
        raise ValueError("log-ratios must exponentiate to finite values")
    return DoublePendulumParameters(
        m1=1.0,
        m2=mass_ratio,
        l1=1.0,
        l2=length_ratio,
        g=1.0,
    )


def dimensionless_rhs(
    tau: float,
    dimensionless_state: Array | Sequence[float],
    log_mass_ratio: float,
    log_length_ratio: float,
) -> Array:
    """Evaluate ``d(theta1,theta2,nu1,nu2)/d tau``."""

    return double_pendulum_rhs(
        _finite(tau, "tau"),
        _state(dimensionless_state),
        dimensionless_parameters(log_mass_ratio, log_length_ratio),
    )


def dimensionless_rhs_state_jacobian(
    tau: float,
    dimensionless_state: Array | Sequence[float],
    log_mass_ratio: float,
    log_length_ratio: float,
) -> Array:
    """Return the analytic ``D_z F`` in dimensionless coordinates."""

    return double_pendulum_rhs_jacobian(
        _finite(tau, "tau"),
        _state(dimensionless_state),
        dimensionless_parameters(log_mass_ratio, log_length_ratio),
    )


def dimensionless_rhs_log_ratio_jacobian(
    tau: float,
    dimensionless_state: Array | Sequence[float],
    log_mass_ratio: float,
    log_length_ratio: float,
) -> Array:
    """Return the analytic ``4 x 2`` matrix ``D_(u,v) F``.

    With ``r=exp(u)``, ``rho=exp(v)``, ``delta=theta1-theta2``, write
    ``M a = b``.  For ``p`` equal to either log-ratio,

        d_p a = M^{-1} (d_p b - (d_p M) a).

    The two leading rows vanish because ``theta' = nu`` has no explicit
    parameter dependence.
    """

    _finite(tau, "tau")
    theta1, theta2, nu1, nu2 = _state(dimensionless_state)
    parameters = dimensionless_parameters(log_mass_ratio, log_length_ratio)
    r = parameters.m2
    rho = parameters.l2
    delta = theta1 - theta2
    sine_delta = math.sin(delta)
    cosine_delta = math.cos(delta)

    matrix = mass_matrix(theta1, theta2, parameters)
    accelerations = double_pendulum_rhs(
        tau, [theta1, theta2, nu1, nu2], parameters
    )[2:]

    matrix_u = np.asarray(
        [
            [r, r * rho * cosine_delta],
            [r * rho * cosine_delta, r * rho**2],
        ],
        dtype=float,
    )
    matrix_v = np.asarray(
        [
            [0.0, r * rho * cosine_delta],
            [r * rho * cosine_delta, 2.0 * r * rho**2],
        ],
        dtype=float,
    )
    forcing_u = np.asarray(
        [
            -r * rho * sine_delta * nu2**2 - r * math.sin(theta1),
            r * rho * sine_delta * nu1**2 - r * rho * math.sin(theta2),
        ],
        dtype=float,
    )
    forcing_v = np.asarray(
        [
            -r * rho * sine_delta * nu2**2,
            r * rho * sine_delta * nu1**2 - r * rho * math.sin(theta2),
        ],
        dtype=float,
    )
    result = np.zeros((4, 2), dtype=float)
    result[2:, 0] = np.linalg.solve(
        matrix, forcing_u - matrix_u @ accelerations
    )
    result[2:, 1] = np.linalg.solve(
        matrix, forcing_v - matrix_v @ accelerations
    )
    if not np.all(np.isfinite(result)):
        raise FloatingPointError("log-ratio forcing Jacobian is non-finite")
    return result


@dataclass(frozen=True)
class LogRatioSensitivityTrajectory:
    """State and ``D_(u,v) state`` sampled on a declared tau grid."""

    times_tau: Array
    states: Array
    sensitivities: Array
    energies: Array
    log_mass_ratio: float
    log_length_ratio: float
    integration_config: IntegrationConfig
    nfev: int
    accepted_step_count: int
    energy_audit_sample_count: int
    max_absolute_energy_drift: float
    max_scaled_energy_drift: float
    solver_message: str
    evidence_tier: str = TIER_1_SCOPE

    def __post_init__(self) -> None:
        times = _readonly(self.times_tau)
        states = _readonly(self.states)
        sensitivities = _readonly(self.sensitivities)
        energies = _readonly(self.energies)
        if times.ndim != 1 or len(times) < 2 or np.any(np.diff(times) <= 0.0):
            raise ValueError("times_tau must be a strictly increasing vector")
        if states.shape != (len(times), 4):
            raise ValueError("states must have shape (time, 4)")
        if sensitivities.shape != (len(times), 4, 2):
            raise ValueError("sensitivities must have shape (time, 4, 2)")
        if energies.shape != (len(times),):
            raise ValueError("energies must have shape (time,)")
        if not all(
            np.all(np.isfinite(value))
            for value in (times, states, sensitivities, energies)
        ):
            raise ValueError("trajectory arrays must be finite")
        if not np.array_equal(sensitivities[0], np.zeros((4, 2))):
            raise ValueError("fixed launches require zero initial sensitivity")
        if self.nfev < 1 or self.accepted_step_count < 1:
            raise ValueError("invalid solver work metadata")
        if self.energy_audit_sample_count < len(times):
            raise ValueError("energy audit cannot contain fewer points than output")
        for name in (
            "log_mass_ratio",
            "log_length_ratio",
            "max_absolute_energy_drift",
            "max_scaled_energy_drift",
        ):
            value = _finite(getattr(self, name), name)
            if name.startswith("max_") and value < 0.0:
                raise ValueError(f"{name} must be nonnegative")
            object.__setattr__(self, name, value)
        if self.evidence_tier != TIER_1_SCOPE:
            raise ValueError("parameter sensitivities are Tier-1 evidence")
        object.__setattr__(self, "times_tau", times)
        object.__setattr__(self, "states", states)
        object.__setattr__(self, "sensitivities", sensitivities)
        object.__setattr__(self, "energies", energies)


DEFAULT_SENSITIVITY_INTEGRATION = IntegrationConfig(
    rtol=1.0e-10,
    atol=1.0e-12,
    max_step=0.01,
    energy_drift_tolerance=1.0e-9,
)


def simulate_log_ratio_sensitivities(
    initial_dimensionless_state: Array | Sequence[float],
    observation_times_tau: Array | Sequence[float],
    *,
    log_mass_ratio: float = 0.0,
    log_length_ratio: float = 0.0,
    integration: IntegrationConfig = DEFAULT_SENSITIVITY_INTEGRATION,
) -> LogRatioSensitivityTrajectory:
    """Integrate the state and analytic inhomogeneous sensitivity jointly."""

    state0 = _state(initial_dimensionless_state)
    times = _times(observation_times_tau)
    u = _finite(log_mass_ratio, "log_mass_ratio")
    v = _finite(log_length_ratio, "log_length_ratio")
    parameters = dimensionless_parameters(u, v)
    augmented0 = np.concatenate((state0, np.zeros(8, dtype=float)))

    def augmented_rhs(tau: float, augmented: Array) -> Array:
        state = augmented[:4]
        sensitivity = augmented[4:].reshape(4, 2)
        state_derivative = double_pendulum_rhs(tau, state, parameters)
        sensitivity_derivative = (
            double_pendulum_rhs_jacobian(tau, state, parameters) @ sensitivity
            + dimensionless_rhs_log_ratio_jacobian(tau, state, u, v)
        )
        return np.concatenate(
            (state_derivative, sensitivity_derivative.reshape(-1))
        )

    solution = solve_ivp(
        augmented_rhs,
        (float(times[0]), float(times[-1])),
        augmented0,
        method="DOP853",
        rtol=integration.rtol,
        atol=integration.atol,
        max_step=integration.max_step,
        dense_output=True,
    )
    if not solution.success or solution.sol is None:
        raise RuntimeError(f"parameter-sensitivity integration failed: {solution.message}")
    sampled = np.asarray(solution.sol(times).T, dtype=float)
    states = sampled[:, :4]
    sensitivities = sampled[:, 4:].reshape(len(times), 4, 2)
    states[0] = state0
    sensitivities[0] = np.zeros((4, 2), dtype=float)
    if not np.all(np.isfinite(sampled)):
        raise RuntimeError("parameter-sensitivity integration returned non-finite values")

    accepted_times = np.asarray(solution.t, dtype=float)
    midpoint_times = 0.5 * (accepted_times[:-1] + accepted_times[1:])
    audit_times = np.unique(np.concatenate((accepted_times, midpoint_times, times)))
    audit_states = np.asarray(solution.sol(audit_times).T[:, :4], dtype=float)
    audit_states[0] = state0
    audit_energies = total_energy(audit_states, parameters)
    initial_energy = float(total_energy(state0, parameters))
    max_absolute_drift = float(np.max(np.abs(audit_energies - initial_energy)))
    energy_scale = max(abs(initial_energy), parameters.characteristic_energy)
    max_scaled_drift = max_absolute_drift / energy_scale
    if (
        integration.energy_drift_tolerance is not None
        and max_scaled_drift > integration.energy_drift_tolerance
    ):
        raise EnergyDriftError(
            max_scaled_drift, integration.energy_drift_tolerance
        )
    return LogRatioSensitivityTrajectory(
        times_tau=times,
        states=states,
        sensitivities=sensitivities,
        energies=total_energy(states, parameters),
        log_mass_ratio=u,
        log_length_ratio=v,
        integration_config=integration,
        nfev=int(solution.nfev),
        accepted_step_count=max(1, len(accepted_times) - 1),
        energy_audit_sample_count=len(audit_times),
        max_absolute_energy_drift=max_absolute_drift,
        max_scaled_energy_drift=max_scaled_drift,
        solver_message=str(solution.message),
    )


def canonical_active_protocols() -> tuple[PendulumProtocolCandidate, ...]:
    """Return the two nonzero protocols selected by the conditional engine."""

    by_name = {candidate.name: candidate for candidate in canonical_protocol_candidates()}
    try:
        return tuple(by_name[name] for name in ACTIVE_PROTOCOL_NAMES)
    except KeyError as error:
        raise RuntimeError("the canonical active protocol library changed") from error


def _candidate_launch(candidate: PendulumProtocolCandidate) -> Array:
    return np.asarray([float(value) for value in candidate.launch], dtype=float)


def _sensor_index(candidate: PendulumProtocolCandidate) -> int:
    return {
        "theta_1": 0,
        "theta_2": 1,
        "scaled_omega_1": 2,
        "scaled_omega_2": 3,
    }[candidate.sensor]


def analytic_protocol_response(
    candidate: PendulumProtocolCandidate,
    *,
    log_mass_ratio: float = 0.0,
    log_length_ratio: float = 0.0,
    integration: IntegrationConfig = DEFAULT_SENSITIVITY_INTEGRATION,
) -> tuple[Array, LogRatioSensitivityTrajectory]:
    """Return the one-by-two analytic response of a scalar candidate."""

    tau = float(candidate.observation_time_tau)
    trajectory = simulate_log_ratio_sensitivities(
        _candidate_launch(candidate),
        [0.0, tau],
        log_mass_ratio=log_mass_ratio,
        log_length_ratio=log_length_ratio,
        integration=integration,
    )
    return trajectory.sensitivities[-1, _sensor_index(candidate)].copy(), trajectory


def _dimensionless_observation(
    candidate: PendulumProtocolCandidate,
    log_mass_ratio: float,
    log_length_ratio: float,
    integration: IntegrationConfig,
) -> tuple[float, float]:
    parameters = dimensionless_parameters(log_mass_ratio, log_length_ratio)
    tau = float(candidate.observation_time_tau)
    trajectory = simulate_double_pendulum(
        _candidate_launch(candidate),
        [0.0, tau],
        parameters,
        integration,
    )
    return (
        float(trajectory.states[-1, _sensor_index(candidate)]),
        float(trajectory.max_scaled_energy_drift),
    )


def centered_protocol_response(
    candidate: PendulumProtocolCandidate,
    step: float,
    *,
    log_mass_ratio: float = 0.0,
    log_length_ratio: float = 0.0,
    integration: IntegrationConfig = DEFAULT_SENSITIVITY_INTEGRATION,
) -> tuple[Array, float]:
    """Independent centred-difference response for a declared log step."""

    h = _finite(step, "step")
    if h <= 0.0:
        raise ValueError("step must be positive")
    base = [
        _finite(log_mass_ratio, "log_mass_ratio"),
        _finite(log_length_ratio, "log_length_ratio"),
    ]
    response = np.zeros(2, dtype=float)
    max_energy_drift = 0.0
    for coordinate in range(2):
        outputs = []
        for sign in (1.0, -1.0):
            point = list(base)
            point[coordinate] += sign * h
            output, drift = _dimensionless_observation(
                candidate, point[0], point[1], integration
            )
            outputs.append(output)
            max_energy_drift = max(max_energy_drift, drift)
        response[coordinate] = (outputs[0] - outputs[1]) / (2.0 * h)
    return response, max_energy_drift


def physical_similarity_state(
    candidate: PendulumProtocolCandidate,
    *,
    log_mass_ratio: float = 0.0,
    log_length_ratio: float = 0.0,
    common_mass_scale: float = 1.0,
    first_length: float = 1.0,
    gravity: float = 1.0,
    integration: IntegrationConfig = DEFAULT_SENSITIVITY_INTEGRATION,
) -> tuple[Array, float]:
    """Integrate a physical representative and return its final tau-state.

    The launch velocities are interpreted as ``nu``.  They are converted to
    physical angular velocities by ``omega=nu*sqrt(g/l1)``; the final result
    is converted back by ``nu=omega*sqrt(l1/g)``.
    """

    common = _finite(common_mass_scale, "common_mass_scale")
    first_length = _finite(first_length, "first_length")
    gravity = _finite(gravity, "gravity")
    if common <= 0.0 or first_length <= 0.0 or gravity <= 0.0:
        raise ValueError("physical scales must be positive")
    u = _finite(log_mass_ratio, "log_mass_ratio")
    v = _finite(log_length_ratio, "log_length_ratio")
    parameters = DoublePendulumParameters(
        m1=common,
        m2=common * math.exp(u),
        l1=first_length,
        l2=first_length * math.exp(v),
        g=gravity,
    )
    launch = _candidate_launch(candidate).copy()
    launch[2:] *= math.sqrt(gravity / first_length)
    final_time = float(candidate.observation_time_tau) * math.sqrt(
        first_length / gravity
    )
    trajectory = simulate_double_pendulum(
        launch, [0.0, final_time], parameters, integration
    )
    final = trajectory.states[-1].copy()
    final[2:] *= math.sqrt(first_length / gravity)
    return final, float(trajectory.max_scaled_energy_drift)


def _candidate_exact_record(candidate: PendulumProtocolCandidate) -> dict[str, object]:
    return {
        "name": candidate.name,
        "launch_dimensionless_exact": [
            _fraction_text(value) for value in candidate.launch
        ],
        "sensor": candidate.sensor,
        "observation_time_tau_exact": _fraction_text(
            candidate.observation_time_tau
        ),
    }


@dataclass(frozen=True)
class ParameterSensitivityReportConfig:
    """Reproducible controls for the canonical Tier-1 report."""

    log_mass_ratio: float = 0.0
    log_length_ratio: float = 0.0
    finite_difference_steps: tuple[float, ...] = (
        8.0e-4,
        4.0e-4,
        2.0e-4,
        1.0e-4,
    )
    integration: IntegrationConfig = DEFAULT_SENSITIVITY_INTEGRATION
    analytic_refinement_tolerance: float = 2.0e-9
    finite_difference_tolerance: float = 8.0e-8
    similarity_tolerance: float = 2.0e-9

    def __post_init__(self) -> None:
        _finite(self.log_mass_ratio, "log_mass_ratio")
        _finite(self.log_length_ratio, "log_length_ratio")
        steps = tuple(_finite(value, "finite_difference_step") for value in self.finite_difference_steps)
        if len(steps) < 3 or any(value <= 0.0 for value in steps):
            raise ValueError("at least three positive finite-difference steps are required")
        if any(later >= earlier for earlier, later in zip(steps, steps[1:])):
            raise ValueError("finite-difference steps must be strictly decreasing")
        for name in (
            "analytic_refinement_tolerance",
            "finite_difference_tolerance",
            "similarity_tolerance",
        ):
            value = _finite(getattr(self, name), name)
            if value <= 0.0:
                raise ValueError(f"{name} must be positive")
            object.__setattr__(self, name, value)
        object.__setattr__(self, "finite_difference_steps", steps)


def _report_config_record(config: ParameterSensitivityReportConfig) -> dict[str, object]:
    return {
        "base_log_ratios": {
            "log_mass_ratio": config.log_mass_ratio,
            "log_length_ratio": config.log_length_ratio,
        },
        "finite_difference_steps": list(config.finite_difference_steps),
        "integration": _integration_record(config.integration),
        "refined_integration": _integration_record(config.integration.refined()),
        "gates": {
            "max_analytic_solver_refinement_discrepancy": config.analytic_refinement_tolerance,
            "max_smallest_step_finite_difference_discrepancy": config.finite_difference_tolerance,
            "max_dimensionless_similarity_discrepancy": config.similarity_tolerance,
        },
    }


def build_parameter_sensitivity_report(
    config: ParameterSensitivityReportConfig = ParameterSensitivityReportConfig(),
) -> dict[str, object]:
    """Build the canonical, artifact-ready Tier-1 sensitivity report."""

    refined = config.integration.refined()
    protocols = []
    all_passed = True
    max_energy_drift = 0.0
    for candidate in canonical_active_protocols():
        coarse_response, coarse_trajectory = analytic_protocol_response(
            candidate,
            log_mass_ratio=config.log_mass_ratio,
            log_length_ratio=config.log_length_ratio,
            integration=config.integration,
        )
        response, trajectory = analytic_protocol_response(
            candidate,
            log_mass_ratio=config.log_mass_ratio,
            log_length_ratio=config.log_length_ratio,
            integration=refined,
        )
        refinement_error = np.abs(response - coarse_response)
        finite_differences = []
        for step in config.finite_difference_steps:
            estimate, drift = centered_protocol_response(
                candidate,
                step,
                log_mass_ratio=config.log_mass_ratio,
                log_length_ratio=config.log_length_ratio,
                integration=refined,
            )
            max_energy_drift = max(max_energy_drift, drift)
            finite_differences.append(
                {
                    "step": step,
                    "response": estimate.tolist(),
                    "absolute_discrepancy_from_analytic": np.abs(
                        estimate - response
                    ).tolist(),
                    "max_absolute_discrepancy": float(
                        np.max(np.abs(estimate - response))
                    ),
                }
            )
        smallest_fd_error = finite_differences[-1]["max_absolute_discrepancy"]
        passed = bool(
            float(np.max(refinement_error))
            <= config.analytic_refinement_tolerance
            and float(smallest_fd_error) <= config.finite_difference_tolerance
        )
        all_passed = all_passed and passed
        max_energy_drift = max(
            max_energy_drift,
            coarse_trajectory.max_scaled_energy_drift,
            trajectory.max_scaled_energy_drift,
        )
        protocols.append(
            {
                "candidate": _candidate_exact_record(candidate),
                "analytic_equation": "S'=D_z F S + D_(u,v) F; S(0)=0",
                "refined_analytic_response": response.tolist(),
                "coarse_analytic_response": coarse_response.tolist(),
                "absolute_solver_refinement_discrepancy": refinement_error.tolist(),
                "max_absolute_solver_refinement_discrepancy": float(
                    np.max(refinement_error)
                ),
                "finite_difference_comparisons": finite_differences,
                "gates_passed": passed,
            }
        )

    physical_variants = (
        ("common-mass-low", 0.2, 1.0, 1.0),
        ("common-mass-high", 5.0, 1.0, 1.0),
        ("length-gravity-a", 1.0, 0.4, 3.2),
        ("length-gravity-b", 1.0, 2.5, 7.7),
        ("all-scales", 3.0, 1.7, 4.6),
    )
    similarity_rows = []
    maximum_similarity_discrepancy = 0.0
    for candidate in canonical_active_protocols():
        normalized, normalized_drift = physical_similarity_state(
            candidate,
            log_mass_ratio=config.log_mass_ratio,
            log_length_ratio=config.log_length_ratio,
            integration=refined,
        )
        max_energy_drift = max(max_energy_drift, normalized_drift)
        variants = []
        for name, common, first_length, gravity in physical_variants:
            state, drift = physical_similarity_state(
                candidate,
                log_mass_ratio=config.log_mass_ratio,
                log_length_ratio=config.log_length_ratio,
                common_mass_scale=common,
                first_length=first_length,
                gravity=gravity,
                integration=refined,
            )
            discrepancy = float(np.max(np.abs(state - normalized)))
            maximum_similarity_discrepancy = max(
                maximum_similarity_discrepancy, discrepancy
            )
            max_energy_drift = max(max_energy_drift, drift)
            variants.append(
                {
                    "name": name,
                    "common_mass_scale": common,
                    "first_length": first_length,
                    "gravity": gravity,
                    "max_absolute_tau_state_discrepancy": discrepancy,
                }
            )
        similarity_rows.append(
            {
                "candidate_name": candidate.name,
                "physical_representatives": variants,
            }
        )
    similarity_passed = bool(
        maximum_similarity_discrepancy <= config.similarity_tolerance
    )
    all_passed = all_passed and similarity_passed

    report = {
        "schema_version": SCHEMA_VERSION,
        "claim_tier": 1,
        "status": "resolved" if all_passed else "unresolved",
        "evidence_tier": TIER_1_SCOPE,
        "source_model": {
            "coordinates": list(SOURCE_COORDINATES),
            "base_point": [config.log_mass_ratio, config.log_length_ratio],
            "dimension": 2,
            "common_mass_scale_in_source": False,
        },
        "dimensionless_convention": {
            "time": "tau=t*sqrt(g/l1)",
            "velocities": "nu_i=omega_i*sqrt(l1/g)=d theta_i/d tau",
            "normalized_representative": "m1=l1=g=1; m2=exp(u); l2=exp(v)",
            "fixed_tau_endpoint_has_no_parameter_endpoint_term": True,
        },
        "analytic_parameter_derivative": {
            "acceleration_rule": "d_p a=M^{-1}(d_p b-(d_p M)a)",
            "sensitivity_rule": "S'=D_z F S+D_(u,v)F; S(0)=0",
            "parameter_forcing_is_analytic": True,
        },
        "configuration": _report_config_record(config),
        "active_protocols": protocols,
        "common_mass_and_dimensionless_similarity_control": {
            "structural_common_mass_identity": (
                "m1,m2 -> c*m1,c*m2 multiplies M and b by c, so a and "
                "D_log(c) F are unchanged; the exact common-scale response is zero"
            ),
            "exact_common_mass_response": ["0/1"],
            "physical_time_rule": "t=tau*sqrt(l1/g)",
            "physical_velocity_rule": "omega=nu*sqrt(g/l1)",
            "protocols": similarity_rows,
            "max_absolute_tau_state_discrepancy": maximum_similarity_discrepancy,
            "gate_passed": similarity_passed,
        },
        "maximum_sampled_scaled_energy_drift": max_energy_drift,
        "outward_validation": {
            "state_enclosed": False,
            "parameter_sensitivity_enclosed": False,
            "exact_response_box_membership_certified": False,
        },
        "proof_boundary": PROOF_BOUNDARY,
    }
    report["internal_recomputation_verification"] = {
        "passed": all_passed,
        "method": (
            "analytic inhomogeneous sensitivity integration, stricter-solver "
            "comparison, multiscale independent centred differences, and "
            "physical-scale similarity integrations"
        ),
        "tier1_numerics_recomputed": True,
        "outward_validation_performed": False,
    }
    return report


def verify_parameter_sensitivity_report(
    report: dict[str, object],
    config: ParameterSensitivityReportConfig = ParameterSensitivityReportConfig(),
) -> dict[str, object]:
    """Recompute the canonical Tier-1 report and compare it strictly.

    This is a numerical provenance check, not an outward verifier.
    """

    try:
        expected = build_parameter_sensitivity_report(config)
        if report != expected:
            raise ValueError("report does not reproduce from the declared configuration")
        if report.get("status") != "resolved":
            raise ValueError("the canonical Tier-1 gates are unresolved")
        return {
            "passed": True,
            "tier1_numerics_recomputed": True,
            "analytic_sensitivity_gates_verified": True,
            "dimensionless_similarity_gates_verified": True,
            "outward_validation_verified": False,
            "exact_response_box_membership_verified": False,
        }
    except Exception as error:
        return {
            "passed": False,
            "tier1_numerics_recomputed": True,
            "outward_validation_verified": False,
            "exact_response_box_membership_verified": False,
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
        verification = verify_parameter_sensitivity_report(report)
        print(json.dumps(verification, indent=2, sort_keys=True))
        return 0 if verification.get("passed") is True else 1
    report = build_parameter_sensitivity_report()
    if args.output is not None:
        _write_json(args.output, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("status") == "resolved" else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ACTIVE_PROTOCOL_NAMES",
    "DEFAULT_SENSITIVITY_INTEGRATION",
    "LogRatioSensitivityTrajectory",
    "PROOF_BOUNDARY",
    "ParameterSensitivityReportConfig",
    "SCHEMA_VERSION",
    "SOURCE_COORDINATES",
    "TIER_1_SCOPE",
    "analytic_protocol_response",
    "build_parameter_sensitivity_report",
    "canonical_active_protocols",
    "centered_protocol_response",
    "dimensionless_parameters",
    "dimensionless_rhs",
    "dimensionless_rhs_log_ratio_jacobian",
    "dimensionless_rhs_state_jacobian",
    "physical_similarity_state",
    "simulate_log_ratio_sensitivities",
    "verify_parameter_sensitivity_report",
]
