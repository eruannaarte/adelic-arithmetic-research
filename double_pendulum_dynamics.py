#!/usr/bin/env python3
"""Audited numerical dynamics for a planar point-mass double pendulum.

This module supplies the mechanical foundation for the Double-Pendulum
Operational Atlas.  It deliberately models *one uncoupled pendulum per initial
condition*: similarity between independently simulated trajectories is an
operational comparison, not physical synchronization.

Conventions
-----------
The rods are massless, the joints are frictionless, and ``m1`` and ``m2`` are
point masses at the first and second bobs.  The state is

    y = [theta1, theta2, omega1, omega2],

where both angles are absolute (not relative), are measured from the downward
vertical, and increase toward positive horizontal displacement.  Thus

    r1 = (l1 sin(theta1), -l1 cos(theta1)),
    r2 = r1 + (l2 sin(theta2), -l2 cos(theta2)).

Writing ``delta = theta1 - theta2``, the Euler--Lagrange equations are

    M(theta) @ [alpha1, alpha2] = f(theta, omega),

with

    M11 = (m1 + m2) l1^2,
    M12 = M21 = m2 l1 l2 cos(delta),
    M22 = m2 l2^2,

and

    f1 = -m2 l1 l2 sin(delta) omega2^2
         -(m1 + m2) g l1 sin(theta1),
    f2 = +m2 l1 l2 sin(delta) omega1^2
         -m2 g l2 sin(theta2).

For positive masses and lengths,

    det(M) = m2 l1^2 l2^2 (m1 + m2 sin(delta)^2) > 0,

so the symmetric mass matrix is positive definite in every configuration.  We
solve that matrix equation directly instead of using cancellation-prone closed
forms.  Integration uses SciPy's adaptive eighth-order DOP853 method, retains
unwrapped angles, audits the conserved energy at accepted steps and midpoints,
and can reject a trajectory whose sampled energy drift exceeds a declared
tolerance.  ``refinement_diagnostic`` is a numerical consistency check, not a
formal enclosure of the exact flow.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.integrate import solve_ivp


@dataclass(frozen=True)
class DoublePendulumParameters:
    """Physical parameters for two point masses on massless rigid rods."""

    m1: float = 1.0
    m2: float = 1.0
    l1: float = 1.0
    l2: float = 1.0
    g: float = 9.81

    def __post_init__(self) -> None:
        for name in ("m1", "m2", "l1", "l2", "g"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and strictly positive")
            object.__setattr__(self, name, value)

    @property
    def characteristic_energy(self) -> float:
        """A positive gravitational scale used to normalize energy drift."""

        return self.g * ((self.m1 + self.m2) * self.l1 + self.m2 * self.l2)

    @property
    def characteristic_angular_speed(self) -> float:
        """A conservative state-error scale for angular velocities."""

        return math.sqrt(self.g / min(self.l1, self.l2))


@dataclass(frozen=True)
class IntegrationConfig:
    """Adaptive-integration and sampled-invariant controls.

    ``energy_drift_tolerance`` bounds the maximum sampled absolute energy
    change divided by the larger of the initial-energy magnitude and the
    characteristic gravitational energy.  Set it to ``None`` only when the
    caller intentionally wants diagnostics without an enforcement gate.
    """

    rtol: float = 1.0e-10
    atol: float = 1.0e-12
    max_step: float = 0.02
    energy_drift_tolerance: float | None = 1.0e-8

    def __post_init__(self) -> None:
        for name in ("rtol", "atol", "max_step"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and strictly positive")
            object.__setattr__(self, name, value)
        if self.rtol >= 1.0:
            raise ValueError("rtol must be smaller than one")
        if self.energy_drift_tolerance is not None:
            tolerance = float(self.energy_drift_tolerance)
            if not math.isfinite(tolerance) or tolerance <= 0.0:
                raise ValueError(
                    "energy_drift_tolerance must be positive or None"
                )
            object.__setattr__(self, "energy_drift_tolerance", tolerance)

    def refined(
        self,
        tolerance_factor: float = 0.1,
        max_step_factor: float = 0.5,
    ) -> "IntegrationConfig":
        """Return a stricter configuration for a same-grid refinement check."""

        tolerance_factor = float(tolerance_factor)
        max_step_factor = float(max_step_factor)
        if not 0.0 < tolerance_factor < 1.0:
            raise ValueError("tolerance_factor must lie strictly between zero and one")
        if not 0.0 < max_step_factor < 1.0:
            raise ValueError("max_step_factor must lie strictly between zero and one")
        return IntegrationConfig(
            rtol=self.rtol * tolerance_factor,
            atol=self.atol * tolerance_factor,
            max_step=self.max_step * max_step_factor,
            energy_drift_tolerance=self.energy_drift_tolerance,
        )


class EnergyDriftError(RuntimeError):
    """Raised when a trajectory fails its declared sampled energy audit."""

    def __init__(self, measured: float, tolerance: float) -> None:
        self.measured = float(measured)
        self.tolerance = float(tolerance)
        super().__init__(
            "sampled scaled energy drift "
            f"{self.measured:.6e} exceeds tolerance {self.tolerance:.6e}"
        )


def _readonly_float_array(value: np.ndarray | Sequence[float]) -> np.ndarray:
    result = np.array(value, dtype=float, copy=True)
    result.setflags(write=False)
    return result


@dataclass(frozen=True)
class DoublePendulumTrajectory:
    """A trajectory sampled on declared observation times with audit metadata."""

    times: np.ndarray
    states: np.ndarray
    energies: np.ndarray
    parameters: DoublePendulumParameters
    integration_config: IntegrationConfig
    nfev: int
    accepted_step_count: int
    energy_audit_sample_count: int
    max_absolute_energy_drift: float
    max_scaled_energy_drift: float
    solver_message: str

    def __post_init__(self) -> None:
        times = _readonly_float_array(self.times)
        states = _readonly_float_array(self.states)
        energies = _readonly_float_array(self.energies)
        if times.ndim != 1 or len(times) < 2:
            raise ValueError("trajectory times must be a vector with at least two entries")
        if states.shape != (len(times), 4):
            raise ValueError("trajectory states must have shape (time, 4)")
        if energies.shape != (len(times),):
            raise ValueError("trajectory energies must have shape (time,)")
        if not (
            np.all(np.isfinite(times))
            and np.all(np.isfinite(states))
            and np.all(np.isfinite(energies))
        ):
            raise ValueError("trajectory arrays must be finite")
        if np.any(np.diff(times) <= 0.0):
            raise ValueError("trajectory times must be strictly increasing")
        if self.nfev < 1 or self.accepted_step_count < 1:
            raise ValueError("invalid solver work metadata")
        if self.energy_audit_sample_count < len(times):
            raise ValueError("energy audit cannot contain fewer points than the output")
        for name in ("max_absolute_energy_drift", "max_scaled_energy_drift"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and nonnegative")
            object.__setattr__(self, name, value)
        object.__setattr__(self, "times", times)
        object.__setattr__(self, "states", states)
        object.__setattr__(self, "energies", energies)

    @property
    def duration(self) -> float:
        return float(self.times[-1] - self.times[0])

    @property
    def positions(self) -> np.ndarray:
        """Cartesian bob positions with shape ``(time, bob, xy)``."""

        return bob_positions(self.states, self.parameters)


@dataclass(frozen=True)
class RefinementDiagnostic:
    """Same-observation-grid comparison of a coarse and refined integration.

    Periodic phase error and unwrapped angular error are recorded separately.
    This prevents agreement modulo ``2*pi`` from concealing disagreement in a
    full-turn excursion label used by the operational atlas.
    """

    coarse: DoublePendulumTrajectory
    fine: DoublePendulumTrajectory
    max_component_discrepancy: np.ndarray
    max_unwrapped_angle_discrepancy: np.ndarray
    coarse_first_sampled_full_turn_indices: np.ndarray
    fine_first_sampled_full_turn_indices: np.ndarray
    max_scaled_state_discrepancy: float
    scaled_state_tolerance: float

    def __post_init__(self) -> None:
        discrepancy = _readonly_float_array(self.max_component_discrepancy)
        if discrepancy.shape != (4,) or np.any(discrepancy < 0.0):
            raise ValueError("component discrepancy must be a nonnegative 4-vector")
        unwrapped = _readonly_float_array(self.max_unwrapped_angle_discrepancy)
        if unwrapped.shape != (2,) or np.any(unwrapped < 0.0):
            raise ValueError("unwrapped angle discrepancy must be a nonnegative 2-vector")
        coarse_turns = np.array(
            self.coarse_first_sampled_full_turn_indices, dtype=int, copy=True
        )
        fine_turns = np.array(
            self.fine_first_sampled_full_turn_indices, dtype=int, copy=True
        )
        if coarse_turns.shape != (2,) or fine_turns.shape != (2,):
            raise ValueError("sampled full-turn indices must be integer 2-vectors")
        coarse_turns.setflags(write=False)
        fine_turns.setflags(write=False)
        if not np.array_equal(self.coarse.times, self.fine.times):
            raise ValueError("refinement trajectories must share observation times")
        scaled = float(self.max_scaled_state_discrepancy)
        tolerance = float(self.scaled_state_tolerance)
        if not math.isfinite(scaled) or scaled < 0.0:
            raise ValueError("scaled discrepancy must be finite and nonnegative")
        if not math.isfinite(tolerance) or tolerance <= 0.0:
            raise ValueError("scaled state tolerance must be finite and positive")
        object.__setattr__(self, "max_component_discrepancy", discrepancy)
        object.__setattr__(self, "max_unwrapped_angle_discrepancy", unwrapped)
        object.__setattr__(
            self, "coarse_first_sampled_full_turn_indices", coarse_turns
        )
        object.__setattr__(self, "fine_first_sampled_full_turn_indices", fine_turns)
        object.__setattr__(self, "max_scaled_state_discrepancy", scaled)
        object.__setattr__(self, "scaled_state_tolerance", tolerance)

    @property
    def sampled_full_turn_events_consistent(self) -> bool:
        return bool(
            np.array_equal(
                self.coarse_first_sampled_full_turn_indices,
                self.fine_first_sampled_full_turn_indices,
            )
        )

    @property
    def passed(self) -> bool:
        """Whether phase, unwrapped-angle, and sampled-event checks all pass."""

        return bool(
            self.max_scaled_state_discrepancy <= self.scaled_state_tolerance
            and np.max(self.max_unwrapped_angle_discrepancy)
            <= self.scaled_state_tolerance
            and self.sampled_full_turn_events_consistent
        )


DEFAULT_PARAMETERS = DoublePendulumParameters()
DEFAULT_INTEGRATION_CONFIG = IntegrationConfig()


def _single_state(state: Sequence[float] | np.ndarray) -> np.ndarray:
    result = np.asarray(state, dtype=float)
    if result.shape != (4,) or not np.all(np.isfinite(result)):
        raise ValueError("state must be a finite vector [theta1, theta2, omega1, omega2]")
    return result


def _state_array(states: Sequence[float] | np.ndarray) -> np.ndarray:
    result = np.asarray(states, dtype=float)
    if result.ndim < 1 or result.shape[-1] != 4:
        raise ValueError("states must have final dimension four")
    if not np.all(np.isfinite(result)):
        raise ValueError("states must be finite")
    return result


def _observation_times(times: Sequence[float] | np.ndarray) -> np.ndarray:
    result = np.asarray(times, dtype=float)
    if result.ndim != 1 or len(result) < 2:
        raise ValueError("observation_times must contain at least two entries")
    if not np.all(np.isfinite(result)) or result[0] < 0.0:
        raise ValueError("observation_times must be finite and nonnegative")
    if np.any(np.diff(result) <= 0.0):
        raise ValueError("observation_times must be strictly increasing")
    return result


def mass_matrix(
    theta1: float,
    theta2: float,
    parameters: DoublePendulumParameters = DEFAULT_PARAMETERS,
) -> np.ndarray:
    """Return the symmetric positive-definite angular mass matrix."""

    theta1 = float(theta1)
    theta2 = float(theta2)
    if not math.isfinite(theta1) or not math.isfinite(theta2):
        raise ValueError("angles must be finite")
    delta = theta1 - theta2
    cross = parameters.m2 * parameters.l1 * parameters.l2 * math.cos(delta)
    return np.asarray(
        [
            [(parameters.m1 + parameters.m2) * parameters.l1**2, cross],
            [cross, parameters.m2 * parameters.l2**2],
        ],
        dtype=float,
    )


def double_pendulum_rhs(
    time: float,
    state: Sequence[float] | np.ndarray,
    parameters: DoublePendulumParameters = DEFAULT_PARAMETERS,
) -> np.ndarray:
    """Evaluate the first-order conservative double-pendulum ODE.

    ``time`` is present for ODE-solver compatibility; the autonomous vector
    field does not otherwise use it.
    """

    if not math.isfinite(float(time)):
        raise ValueError("time must be finite")
    theta1, theta2, omega1, omega2 = _single_state(state)
    delta = theta1 - theta2
    coupling = parameters.m2 * parameters.l1 * parameters.l2 * math.sin(delta)
    forcing = np.asarray(
        [
            -coupling * omega2**2
            - (parameters.m1 + parameters.m2)
            * parameters.g
            * parameters.l1
            * math.sin(theta1),
            coupling * omega1**2
            - parameters.m2 * parameters.g * parameters.l2 * math.sin(theta2),
        ],
        dtype=float,
    )
    accelerations = np.linalg.solve(
        mass_matrix(theta1, theta2, parameters), forcing
    )
    return np.asarray([omega1, omega2, *accelerations], dtype=float)


def total_energy(
    states: Sequence[float] | np.ndarray,
    parameters: DoublePendulumParameters = DEFAULT_PARAMETERS,
) -> np.ndarray:
    """Evaluate kinetic plus gravitational potential energy.

    The potential zero is the suspension height.  A single state returns a
    zero-dimensional array; an array with shape ``(..., 4)`` returns ``(...)``.
    """

    values = _state_array(states)
    theta1 = values[..., 0]
    theta2 = values[..., 1]
    omega1 = values[..., 2]
    omega2 = values[..., 3]
    delta = theta1 - theta2
    kinetic = (
        0.5 * (parameters.m1 + parameters.m2) * parameters.l1**2 * omega1**2
        + 0.5 * parameters.m2 * parameters.l2**2 * omega2**2
        + parameters.m2
        * parameters.l1
        * parameters.l2
        * np.cos(delta)
        * omega1
        * omega2
    )
    potential = (
        -(parameters.m1 + parameters.m2)
        * parameters.g
        * parameters.l1
        * np.cos(theta1)
        - parameters.m2 * parameters.g * parameters.l2 * np.cos(theta2)
    )
    return np.asarray(kinetic + potential, dtype=float)


def bob_positions(
    states: Sequence[float] | np.ndarray,
    parameters: DoublePendulumParameters = DEFAULT_PARAMETERS,
) -> np.ndarray:
    """Return Cartesian positions with final dimensions ``(bob, xy)``."""

    values = _state_array(states)
    theta1 = values[..., 0]
    theta2 = values[..., 1]
    x1 = parameters.l1 * np.sin(theta1)
    y1 = -parameters.l1 * np.cos(theta1)
    x2 = x1 + parameters.l2 * np.sin(theta2)
    y2 = y1 - parameters.l2 * np.cos(theta2)
    first = np.stack((x1, y1), axis=-1)
    second = np.stack((x2, y2), axis=-1)
    return np.stack((first, second), axis=-2)


def simulate_double_pendulum(
    initial_state: Sequence[float] | np.ndarray,
    observation_times: Sequence[float] | np.ndarray,
    parameters: DoublePendulumParameters = DEFAULT_PARAMETERS,
    config: IntegrationConfig = DEFAULT_INTEGRATION_CONFIG,
) -> DoublePendulumTrajectory:
    """Integrate one pendulum and sample it at the declared observation times.

    ``initial_state`` is the state at ``observation_times[0]``.  Energy is
    audited at solver-accepted endpoints, their midpoints, and all requested
    observation times.  The audit is empirical; it is not an interval proof.
    """

    state0 = _single_state(initial_state)
    times = _observation_times(observation_times)

    solution = solve_ivp(
        lambda time, state: double_pendulum_rhs(time, state, parameters),
        (float(times[0]), float(times[-1])),
        state0,
        method="DOP853",
        rtol=config.rtol,
        atol=config.atol,
        max_step=config.max_step,
        dense_output=True,
    )
    if not solution.success or solution.sol is None:
        raise RuntimeError(f"double-pendulum integration failed: {solution.message}")

    sampled_states = np.asarray(solution.sol(times).T, dtype=float)
    sampled_states[0] = state0
    if not np.all(np.isfinite(sampled_states)):
        raise RuntimeError("double-pendulum integration returned non-finite states")

    accepted_times = np.asarray(solution.t, dtype=float)
    midpoint_times = 0.5 * (accepted_times[:-1] + accepted_times[1:])
    audit_times = np.unique(np.concatenate((accepted_times, midpoint_times, times)))
    audit_states = np.asarray(solution.sol(audit_times).T, dtype=float)
    audit_states[0] = state0
    audit_energies = total_energy(audit_states, parameters)
    initial_energy = float(total_energy(state0, parameters))
    max_absolute_drift = float(np.max(np.abs(audit_energies - initial_energy)))
    energy_scale = max(abs(initial_energy), parameters.characteristic_energy)
    max_scaled_drift = max_absolute_drift / energy_scale

    if (
        config.energy_drift_tolerance is not None
        and max_scaled_drift > config.energy_drift_tolerance
    ):
        raise EnergyDriftError(max_scaled_drift, config.energy_drift_tolerance)

    sampled_energies = total_energy(sampled_states, parameters)
    return DoublePendulumTrajectory(
        times=times,
        states=sampled_states,
        energies=sampled_energies,
        parameters=parameters,
        integration_config=config,
        nfev=int(solution.nfev),
        accepted_step_count=max(1, len(accepted_times) - 1),
        energy_audit_sample_count=len(audit_times),
        max_absolute_energy_drift=max_absolute_drift,
        max_scaled_energy_drift=max_scaled_drift,
        solver_message=str(solution.message),
    )


def _first_sampled_full_turn_indices(states: np.ndarray) -> np.ndarray:
    """First sampled absolute one-turn excursions for the two unwrapped angles."""

    excursions = np.abs(states[:, :2] - states[0, :2])
    crossed = excursions >= 2.0 * math.pi
    indices = np.full(2, -1, dtype=int)
    for arm in range(2):
        locations = np.flatnonzero(crossed[:, arm])
        if len(locations):
            indices[arm] = int(locations[0])
    return indices


def refinement_diagnostic(
    initial_state: Sequence[float] | np.ndarray,
    observation_times: Sequence[float] | np.ndarray,
    parameters: DoublePendulumParameters = DEFAULT_PARAMETERS,
    coarse_config: IntegrationConfig = DEFAULT_INTEGRATION_CONFIG,
    fine_config: IntegrationConfig | None = None,
    scaled_state_tolerance: float = 1.0e-7,
) -> RefinementDiagnostic:
    """Compare two integrations on the same declared observation grid.

    Phase-angle discrepancies are reduced modulo ``2*pi`` for the operational
    state metric, while unwrapped discrepancies and first sampled full-turn
    excursion indices are checked independently.  Angular-velocity differences
    are normalized by ``sqrt(g / min(l1, l2))``.  Passing this diagnostic shows
    consistency under the declared refinement, not a rigorous error bound or a
    continuous-time event enclosure.
    """

    scaled_state_tolerance = float(scaled_state_tolerance)
    if not math.isfinite(scaled_state_tolerance) or scaled_state_tolerance <= 0.0:
        raise ValueError("scaled_state_tolerance must be finite and positive")
    if fine_config is None:
        fine_config = coarse_config.refined()
    if (
        fine_config.rtol > coarse_config.rtol
        or fine_config.atol > coarse_config.atol
        or fine_config.max_step > coarse_config.max_step
    ):
        raise ValueError("fine_config must be no looser than coarse_config")
    if not (
        fine_config.rtol < coarse_config.rtol
        or fine_config.atol < coarse_config.atol
        or fine_config.max_step < coarse_config.max_step
    ):
        raise ValueError("fine_config must tighten at least one integration control")
    if coarse_config.energy_drift_tolerance is not None and (
        fine_config.energy_drift_tolerance is None
        or fine_config.energy_drift_tolerance
        > coarse_config.energy_drift_tolerance
    ):
        raise ValueError("fine_config energy gate must be no looser than the coarse gate")

    coarse = simulate_double_pendulum(
        initial_state, observation_times, parameters, coarse_config
    )
    fine = simulate_double_pendulum(
        initial_state, observation_times, parameters, fine_config
    )
    unwrapped_difference = coarse.states - fine.states
    phase_difference = unwrapped_difference.copy()
    phase_difference[:, :2] = np.arctan2(
        np.sin(phase_difference[:, :2]), np.cos(phase_difference[:, :2])
    )
    component_discrepancy = np.max(np.abs(phase_difference), axis=0)
    unwrapped_angle_discrepancy = np.max(
        np.abs(unwrapped_difference[:, :2]), axis=0
    )
    component_scales = np.asarray(
        [
            1.0,
            1.0,
            parameters.characteristic_angular_speed,
            parameters.characteristic_angular_speed,
        ]
    )
    scaled_discrepancy = float(
        np.max(np.abs(phase_difference) / component_scales[None, :])
    )
    return RefinementDiagnostic(
        coarse=coarse,
        fine=fine,
        max_component_discrepancy=component_discrepancy,
        max_unwrapped_angle_discrepancy=unwrapped_angle_discrepancy,
        coarse_first_sampled_full_turn_indices=_first_sampled_full_turn_indices(
            coarse.states
        ),
        fine_first_sampled_full_turn_indices=_first_sampled_full_turn_indices(
            fine.states
        ),
        max_scaled_state_discrepancy=scaled_discrepancy,
        scaled_state_tolerance=scaled_state_tolerance,
    )


__all__ = [
    "DEFAULT_INTEGRATION_CONFIG",
    "DEFAULT_PARAMETERS",
    "DoublePendulumParameters",
    "DoublePendulumTrajectory",
    "EnergyDriftError",
    "IntegrationConfig",
    "RefinementDiagnostic",
    "bob_positions",
    "double_pendulum_rhs",
    "mass_matrix",
    "refinement_diagnostic",
    "simulate_double_pendulum",
    "total_energy",
]
