"""Tier-1 variational dynamics and local OIG responses for a double pendulum.

The state convention is ``[theta1, theta2, omega1, omega2]``.  Along a
numerically integrated state trajectory ``z(t)``, the initial-state tangent
matrix ``Phi(t)`` solves

    Phi'(t) = Df(z(t)) Phi(t),     Phi(t0) = I.

``Df`` is evaluated analytically from the Euler--Lagrange mass system.  The
module also differentiates the seam-free phase observation and assembles a
declared finite-time response matrix and pullback information Gram after an
explicit source-to-initial-state injection. This keeps the two-angle atlas
slice distinct from full four-state recovery.

All conclusions here are Tier 1: adaptive integration, refinement, and
finite-difference agreement are numerical audits, not outward enclosures of
the exact nonlinear flow.  The returned matrices must not be supplied to an
exact OIG theorem as physical enclosures unless a separate validated transfer
proves that containment premise.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import eigh

from double_pendulum_dynamics import (
    DEFAULT_INTEGRATION_CONFIG,
    DEFAULT_PARAMETERS,
    DoublePendulumParameters,
    EnergyDriftError,
    IntegrationConfig,
    double_pendulum_rhs,
    mass_matrix,
    total_energy,
)


Array = np.ndarray
TIER_1_SCOPE = "tier_1_numerical_not_outward_validated"


def angle_slice_source_injection() -> Array:
    """Return ``D_q z0`` for ``z0=(theta1,theta2,0,0)``."""

    return np.asarray(
        [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0], [0.0, 0.0]],
        dtype=float,
    )


def _readonly_float_array(value: Array | Sequence[float]) -> Array:
    result = np.array(value, dtype=float, copy=True)
    result.setflags(write=False)
    return result


def _state(state: Array | Sequence[float]) -> Array:
    result = np.asarray(state, dtype=float)
    if result.shape != (4,) or not np.all(np.isfinite(result)):
        raise ValueError(
            "state must be a finite vector [theta1, theta2, omega1, omega2]"
        )
    return result


def _observation_times(times: Array | Sequence[float]) -> Array:
    result = np.asarray(times, dtype=float)
    if result.ndim != 1 or len(result) < 2:
        raise ValueError("observation_times must contain at least two entries")
    if not np.all(np.isfinite(result)) or result[0] < 0.0:
        raise ValueError("observation_times must be finite and nonnegative")
    if np.any(np.diff(result) <= 0.0):
        raise ValueError("observation_times must be strictly increasing")
    return result


def _symmetric_positive_definite(value: Array, name: str) -> Array:
    matrix = np.asarray(value, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} must be finite")
    scale = max(1.0, float(np.linalg.norm(matrix, ord=np.inf)))
    if not np.allclose(matrix, matrix.T, rtol=0.0, atol=1.0e-13 * scale):
        raise ValueError(f"{name} must be symmetric")
    symmetric = 0.5 * (matrix + matrix.T)
    try:
        np.linalg.cholesky(symmetric)
    except np.linalg.LinAlgError as error:
        raise ValueError(f"{name} must be positive definite") from error
    return _readonly_float_array(symmetric)


def double_pendulum_rhs_jacobian(
    time: float,
    state: Array | Sequence[float],
    parameters: DoublePendulumParameters = DEFAULT_PARAMETERS,
) -> Array:
    """Return the analytic ``4 x 4`` Jacobian of the first-order vector field.

    If ``M(q) a = f(q, omega)``, differentiation gives

    ``d a = M(q)^(-1) (d f - (d M) a)``.

    This identity avoids differentiating an expanded quotient formula and
    retains the same nonsingular mass-matrix convention as the dynamics
    implementation.
    """

    if not math.isfinite(float(time)):
        raise ValueError("time must be finite")
    theta1, theta2, omega1, omega2 = _state(state)
    delta = theta1 - theta2
    sine_delta = math.sin(delta)
    cosine_delta = math.cos(delta)
    coupling = parameters.m2 * parameters.l1 * parameters.l2
    gravity1 = (parameters.m1 + parameters.m2) * parameters.g * parameters.l1
    gravity2 = parameters.m2 * parameters.g * parameters.l2

    matrix = mass_matrix(theta1, theta2, parameters)
    accelerations = double_pendulum_rhs(
        time, [theta1, theta2, omega1, omega2], parameters
    )[2:]

    dmatrix_theta1 = np.asarray(
        [[0.0, -coupling * sine_delta], [-coupling * sine_delta, 0.0]]
    )
    dmatrix_theta2 = -dmatrix_theta1

    dforcing = (
        np.asarray(
            [
                -coupling * cosine_delta * omega2**2
                - gravity1 * math.cos(theta1),
                coupling * cosine_delta * omega1**2,
            ]
        ),
        np.asarray(
            [
                coupling * cosine_delta * omega2**2,
                -coupling * cosine_delta * omega1**2
                - gravity2 * math.cos(theta2),
            ]
        ),
        np.asarray([0.0, 2.0 * coupling * sine_delta * omega1]),
        np.asarray([-2.0 * coupling * sine_delta * omega2, 0.0]),
    )
    dmatrices = (
        dmatrix_theta1,
        dmatrix_theta2,
        np.zeros((2, 2)),
        np.zeros((2, 2)),
    )

    jacobian = np.zeros((4, 4), dtype=float)
    jacobian[0, 2] = 1.0
    jacobian[1, 3] = 1.0
    for column in range(4):
        right_hand_side = (
            dforcing[column] - dmatrices[column] @ accelerations
        )
        jacobian[2:, column] = np.linalg.solve(matrix, right_hand_side)
    if not np.all(np.isfinite(jacobian)):
        raise FloatingPointError("variational Jacobian is non-finite")
    return jacobian


def phase_observation_jacobian(
    state: Array | Sequence[float],
    *,
    angular_velocity_scale: float = 1.0,
) -> Array:
    """Differentiate the seam-free six-coordinate phase observation."""

    theta1, theta2, _omega1, _omega2 = _state(state)
    angular_velocity_scale = float(angular_velocity_scale)
    if (
        not math.isfinite(angular_velocity_scale)
        or angular_velocity_scale <= 0.0
    ):
        raise ValueError("angular_velocity_scale must be finite and positive")
    inverse_scale = 1.0 / angular_velocity_scale
    return np.asarray(
        [
            [math.cos(theta1), 0.0, 0.0, 0.0],
            [-math.sin(theta1), 0.0, 0.0, 0.0],
            [0.0, math.cos(theta2), 0.0, 0.0],
            [0.0, -math.sin(theta2), 0.0, 0.0],
            [0.0, 0.0, inverse_scale, 0.0],
            [0.0, 0.0, 0.0, inverse_scale],
        ],
        dtype=float,
    )


@dataclass(frozen=True)
class DoublePendulumVariationalTrajectory:
    """State and initial-state tangent matrices on a declared output grid."""

    times: Array
    states: Array
    tangents: Array
    energies: Array
    parameters: DoublePendulumParameters
    integration_config: IntegrationConfig
    nfev: int
    accepted_step_count: int
    energy_audit_sample_count: int
    max_absolute_energy_drift: float
    max_scaled_energy_drift: float
    solver_message: str
    evidence_tier: str = TIER_1_SCOPE

    def __post_init__(self) -> None:
        times = _readonly_float_array(self.times)
        states = _readonly_float_array(self.states)
        tangents = _readonly_float_array(self.tangents)
        energies = _readonly_float_array(self.energies)
        if times.ndim != 1 or len(times) < 2 or np.any(np.diff(times) <= 0.0):
            raise ValueError("times must be a strictly increasing vector")
        if states.shape != (len(times), 4):
            raise ValueError("states must have shape (time, 4)")
        if tangents.shape != (len(times), 4, 4):
            raise ValueError("tangents must have shape (time, 4, 4)")
        if energies.shape != (len(times),):
            raise ValueError("energies must have shape (time,)")
        if not (
            np.all(np.isfinite(times))
            and np.all(np.isfinite(states))
            and np.all(np.isfinite(tangents))
            and np.all(np.isfinite(energies))
        ):
            raise ValueError("trajectory arrays must be finite")
        if not np.array_equal(tangents[0], np.eye(4)):
            raise ValueError("the first tangent matrix must be the identity")
        if self.nfev < 1 or self.accepted_step_count < 1:
            raise ValueError("invalid solver work metadata")
        if self.energy_audit_sample_count < len(times):
            raise ValueError("energy audit cannot contain fewer points than output")
        for name in ("max_absolute_energy_drift", "max_scaled_energy_drift"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and nonnegative")
            object.__setattr__(self, name, value)
        if self.evidence_tier != TIER_1_SCOPE:
            raise ValueError("variational trajectories are Tier-1 numerical evidence")
        object.__setattr__(self, "times", times)
        object.__setattr__(self, "states", states)
        object.__setattr__(self, "tangents", tangents)
        object.__setattr__(self, "energies", energies)

    @property
    def duration(self) -> float:
        return float(self.times[-1] - self.times[0])


def simulate_double_pendulum_variational(
    initial_state: Array | Sequence[float],
    observation_times: Array | Sequence[float],
    parameters: DoublePendulumParameters = DEFAULT_PARAMETERS,
    config: IntegrationConfig = DEFAULT_INTEGRATION_CONFIG,
) -> DoublePendulumVariationalTrajectory:
    """Integrate the nonlinear state and its ``4 x 4`` tangent matrix jointly."""

    state0 = _state(initial_state)
    times = _observation_times(observation_times)
    augmented0 = np.concatenate((state0, np.eye(4).reshape(-1)))

    def augmented_rhs(time: float, augmented: Array) -> Array:
        state = augmented[:4]
        tangent = augmented[4:].reshape(4, 4)
        derivative = double_pendulum_rhs(time, state, parameters)
        tangent_derivative = (
            double_pendulum_rhs_jacobian(time, state, parameters) @ tangent
        )
        return np.concatenate((derivative, tangent_derivative.reshape(-1)))

    solution = solve_ivp(
        augmented_rhs,
        (float(times[0]), float(times[-1])),
        augmented0,
        method="DOP853",
        rtol=config.rtol,
        atol=config.atol,
        max_step=config.max_step,
        dense_output=True,
    )
    if not solution.success or solution.sol is None:
        raise RuntimeError(f"variational integration failed: {solution.message}")

    sampled = np.asarray(solution.sol(times).T, dtype=float)
    states = sampled[:, :4]
    tangents = sampled[:, 4:].reshape(len(times), 4, 4)
    states[0] = state0
    tangents[0] = np.eye(4)
    if not np.all(np.isfinite(sampled)):
        raise RuntimeError("variational integration returned non-finite values")

    accepted_times = np.asarray(solution.t, dtype=float)
    midpoint_times = 0.5 * (accepted_times[:-1] + accepted_times[1:])
    audit_times = np.unique(np.concatenate((accepted_times, midpoint_times, times)))
    audit_states = np.asarray(solution.sol(audit_times).T[:, :4], dtype=float)
    audit_states[0] = state0
    audit_energies = total_energy(audit_states, parameters)
    initial_energy = float(total_energy(state0, parameters))
    maximum_absolute_drift = float(
        np.max(np.abs(audit_energies - initial_energy))
    )
    energy_scale = max(abs(initial_energy), parameters.characteristic_energy)
    maximum_scaled_drift = maximum_absolute_drift / energy_scale
    if (
        config.energy_drift_tolerance is not None
        and maximum_scaled_drift > config.energy_drift_tolerance
    ):
        raise EnergyDriftError(
            maximum_scaled_drift, config.energy_drift_tolerance
        )

    return DoublePendulumVariationalTrajectory(
        times=times,
        states=states,
        tangents=tangents,
        energies=total_energy(states, parameters),
        parameters=parameters,
        integration_config=config,
        nfev=int(solution.nfev),
        accepted_step_count=max(1, len(accepted_times) - 1),
        energy_audit_sample_count=len(audit_times),
        max_absolute_energy_drift=maximum_absolute_drift,
        max_scaled_energy_drift=maximum_scaled_drift,
        solver_message=str(solution.message),
    )


@dataclass(frozen=True)
class PhaseObservationProtocol:
    """A finite schedule and linear sensor acting on the phase embedding."""

    name: str
    sample_indices: tuple[int, ...]
    sensor_matrix: Array
    output_precision: Array
    source_metric: Array
    source_injection: Array = field(default_factory=lambda: np.eye(4))
    angular_velocity_scale: float = 1.0
    cost: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("protocol name must be nonempty")
        indices: list[int] = []
        for index in self.sample_indices:
            if isinstance(index, (bool, np.bool_)) or not isinstance(
                index, (int, np.integer)
            ):
                raise ValueError("sample indices must be integers")
            if int(index) < 0:
                raise ValueError("sample indices must be nonnegative")
            indices.append(int(index))
        if not indices:
            raise ValueError("sample_indices must be nonempty")
        sensor = np.asarray(self.sensor_matrix, dtype=float)
        if sensor.ndim != 2 or sensor.shape[1] != 6 or sensor.shape[0] < 1:
            raise ValueError("sensor_matrix must have shape (outputs, 6)")
        if not np.all(np.isfinite(sensor)):
            raise ValueError("sensor_matrix must be finite")
        output_dimension = len(indices) * sensor.shape[0]
        precision = _symmetric_positive_definite(
            self.output_precision, "output_precision"
        )
        if precision.shape != (output_dimension, output_dimension):
            raise ValueError("output_precision has the wrong protocol dimension")
        injection = np.asarray(self.source_injection, dtype=float)
        if (
            injection.ndim != 2
            or injection.shape[0] != 4
            or injection.shape[1] < 1
            or not np.all(np.isfinite(injection))
        ):
            raise ValueError("source_injection must have finite shape (4, source_dimension)")
        if np.linalg.matrix_rank(injection) != injection.shape[1]:
            raise ValueError("source_injection must have full column rank")
        source = _symmetric_positive_definite(self.source_metric, "source_metric")
        if source.shape != (injection.shape[1], injection.shape[1]):
            raise ValueError("source_metric and source_injection dimensions differ")
        scale = float(self.angular_velocity_scale)
        cost = float(self.cost)
        if not math.isfinite(scale) or scale <= 0.0:
            raise ValueError("angular_velocity_scale must be finite and positive")
        if not math.isfinite(cost) or cost <= 0.0:
            raise ValueError("cost must be finite and positive")
        object.__setattr__(self, "sample_indices", tuple(indices))
        object.__setattr__(self, "sensor_matrix", _readonly_float_array(sensor))
        object.__setattr__(self, "output_precision", precision)
        object.__setattr__(self, "source_metric", source)
        object.__setattr__(self, "source_injection", _readonly_float_array(injection))
        object.__setattr__(self, "angular_velocity_scale", scale)
        object.__setattr__(self, "cost", cost)


@dataclass(frozen=True)
class LocalOIGAnalysis:
    """Numerical local response, Gram, and metric-relative singular values."""

    protocol_name: str
    sample_indices: tuple[int, ...]
    sample_times: Array
    response: Array
    information_gram: Array
    generalized_eigenvalues: Array
    singular_values: Array
    evidence_tier: str = TIER_1_SCOPE

    def __post_init__(self) -> None:
        sample_times = _readonly_float_array(self.sample_times)
        response = _readonly_float_array(self.response)
        gram = _readonly_float_array(self.information_gram)
        eigenvalues = _readonly_float_array(self.generalized_eigenvalues)
        singular_values = _readonly_float_array(self.singular_values)
        if sample_times.shape != (len(self.sample_indices),):
            raise ValueError("sample_times and sample_indices disagree")
        if response.ndim != 2 or response.shape[1] < 1:
            raise ValueError("response must have at least one source column")
        source_dimension = response.shape[1]
        if gram.shape != (source_dimension, source_dimension):
            raise ValueError("information Gram and response source dimensions differ")
        if eigenvalues.shape != (source_dimension,) or singular_values.shape != (
            source_dimension,
        ):
            raise ValueError("local spectra and response source dimensions differ")
        if not np.all(np.isfinite(response)) or not np.all(np.isfinite(gram)):
            raise ValueError("response and Gram must be finite")
        if np.any(eigenvalues < 0.0) or np.any(singular_values < 0.0):
            raise ValueError("local spectrum must be nonnegative")
        if not np.allclose(
            singular_values * singular_values,
            eigenvalues,
            rtol=1.0e-12,
            atol=1.0e-14,
        ):
            raise ValueError("singular values must square to the eigenvalues")
        if self.evidence_tier != TIER_1_SCOPE:
            raise ValueError("local OIG analysis is Tier-1 numerical evidence")
        object.__setattr__(self, "sample_times", sample_times)
        object.__setattr__(self, "response", response)
        object.__setattr__(self, "information_gram", gram)
        object.__setattr__(self, "generalized_eigenvalues", eigenvalues)
        object.__setattr__(self, "singular_values", singular_values)

    @property
    def weakest_gain(self) -> float:
        return float(self.singular_values[0])

    @property
    def strongest_gain(self) -> float:
        return float(self.singular_values[-1])


def stacked_phase_response(
    trajectory: DoublePendulumVariationalTrajectory,
    protocol: PhaseObservationProtocol,
) -> Array:
    """Assemble ``dY/du=(dY/dz0)J`` for the declared source injection ``J``."""

    if any(index >= len(trajectory.times) for index in protocol.sample_indices):
        raise ValueError("a protocol sample index lies outside the trajectory")
    blocks = []
    for index in protocol.sample_indices:
        observation_jacobian = phase_observation_jacobian(
            trajectory.states[index],
            angular_velocity_scale=protocol.angular_velocity_scale,
        )
        blocks.append(
            protocol.sensor_matrix
            @ observation_jacobian
            @ trajectory.tangents[index]
            @ protocol.source_injection
        )
    return np.vstack(blocks)


def analyze_phase_protocol(
    trajectory: DoublePendulumVariationalTrajectory,
    protocol: PhaseObservationProtocol,
) -> LocalOIGAnalysis:
    """Compute the Tier-1 pullback information and generalized gains."""

    response = stacked_phase_response(trajectory, protocol)
    gram = response.T @ protocol.output_precision @ response
    gram = 0.5 * (gram + gram.T)
    eigenvalues = np.asarray(
        eigh(gram, protocol.source_metric, eigvals_only=True, check_finite=True),
        dtype=float,
    )
    scale = max(1.0, float(np.linalg.norm(gram, ord=2)))
    negative_tolerance = 256.0 * np.finfo(float).eps * scale
    if float(np.min(eigenvalues)) < -negative_tolerance:
        raise ArithmeticError("computed information Gram has a negative eigenvalue")
    eigenvalues = np.maximum(eigenvalues, 0.0)
    return LocalOIGAnalysis(
        protocol_name=protocol.name,
        sample_indices=protocol.sample_indices,
        sample_times=trajectory.times[list(protocol.sample_indices)],
        response=response,
        information_gram=gram,
        generalized_eigenvalues=eigenvalues,
        singular_values=np.sqrt(eigenvalues),
    )


__all__ = [
    "DoublePendulumVariationalTrajectory",
    "LocalOIGAnalysis",
    "PhaseObservationProtocol",
    "TIER_1_SCOPE",
    "analyze_phase_protocol",
    "angle_slice_source_injection",
    "double_pendulum_rhs_jacobian",
    "phase_observation_jacobian",
    "simulate_double_pendulum_variational",
    "stacked_phase_response",
]
