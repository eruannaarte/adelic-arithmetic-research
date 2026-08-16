"""Outward Picard--Taylor transfer for the two active pendulum protocols.

This module closes a very specific premise left open by
``oig_double_pendulum_protocol``: at the nominal dimensionless parameters

    u = log(m2/m1) = 0,   v = log(l2/l1) = 0,

it encloses the two parameter-response rows used with nonzero design weight.
The implementation is deliberately independent of SciPy's ODE solvers.

The accepted-step theorem is a validated defect/Picard argument.  On a step
``[0,h]`` let ``p`` be an arbitrary polynomial, let ``X0`` enclose the true
initial value, and let ``rho`` be a componentwise error radius.  If ``B``
contains ``p([0,h]) + [-rho,rho]``, interval automatic differentiation gives
``A_ij >= sup_B |D_j F_i|``, and an outward Taylor calculation gives
``d_i >= sup_[0,h] |p'_i-F_i(p)|``.  The componentwise inequality

    rad(X0-p(0)) + h d + h A rho <= rho                         (1)

makes the integral Picard operator self-mapping on the tube.  Standard local
existence and uniqueness then imply that the exact solution stays in the
tube, and the left side of (1) is also a valid endpoint error radius about
``p(h)``.  A step is rejected unless (1) is proved with Arb ball arithmetic.

The state is augmented by the exact first parameter sensitivities, so this is
an enclosure of the derivative of the nonlinear flow, not a finite-difference
surrogate.  Ordinary interval evaluation of an unvalidated Runge--Kutta
trajectory is nowhere used as a proof step.

Limitations are explicit.  The certificate is pointwise at ``(u,v)=(0,0)``,
uses the fixed dimensionless representative ``m1=l1=g=1``, and covers only the
two named launch/sensor/time protocols.  It does not enclose a parameter
neighbourhood or the other five discovery candidates.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
import json
import math
from pathlib import Path
from typing import Generic, Sequence, TypeVar

from flint import arb, arb_series, ctx

from oig_interval_protocol_design import (
    EnclosedProtocol,
    design_enclosed_protocols,
    verify_enclosed_design_report,
)


Q = Fraction
SCHEMA_VERSION = "oig-double-pendulum-validated-transfer-v1"
PHYSICAL_CERTIFICATE_SCHEMA_VERSION = (
    "oig-double-pendulum-physical-positive-floor-v1"
)
METHOD = "outward-arb-picard-taylor-self-mapping-v1"
SOURCE_COORDINATES = (
    "log_mass_ratio=log(m2/m1)",
    "log_length_ratio=log(l2/l1)",
)


T = TypeVar("T")


def _zero_like(value: T) -> T:
    return value * 0  # type: ignore[return-value,operator]


def _one_like(value: T) -> T:
    return _zero_like(value) + 1  # type: ignore[return-value,operator]


def _sin(value: T) -> T:
    return value.sin()  # type: ignore[no-any-return,union-attr]


def _cos(value: T) -> T:
    return value.cos()  # type: ignore[no-any-return,union-attr]


def _exp(value: T) -> T:
    return value.exp()  # type: ignore[no-any-return,union-attr]


@dataclass(frozen=True)
class ParameterDual(Generic[T]):
    """Two-direction forward derivative, nestable over interval AD objects."""

    value: T
    du: T
    dv: T

    @classmethod
    def constant(cls, value: T) -> "ParameterDual[T]":
        zero = _zero_like(value)
        return cls(value, zero, zero)

    def _coerce(self, other: object) -> "ParameterDual[T]":
        if isinstance(other, ParameterDual):
            return other
        value = self.value * 0 + other  # type: ignore[operator]
        return ParameterDual.constant(value)

    def __add__(self, other: object) -> "ParameterDual[T]":
        right = self._coerce(other)
        return ParameterDual(
            self.value + right.value,  # type: ignore[operator]
            self.du + right.du,  # type: ignore[operator]
            self.dv + right.dv,  # type: ignore[operator]
        )

    __radd__ = __add__

    def __neg__(self) -> "ParameterDual[T]":
        return ParameterDual(-self.value, -self.du, -self.dv)  # type: ignore[operator]

    def __sub__(self, other: object) -> "ParameterDual[T]":
        return self + (-self._coerce(other))

    def __rsub__(self, other: object) -> "ParameterDual[T]":
        return self._coerce(other) - self

    def __mul__(self, other: object) -> "ParameterDual[T]":
        right = self._coerce(other)
        return ParameterDual(
            self.value * right.value,  # type: ignore[operator]
            self.du * right.value + self.value * right.du,  # type: ignore[operator]
            self.dv * right.value + self.value * right.dv,  # type: ignore[operator]
        )

    __rmul__ = __mul__

    def reciprocal(self) -> "ParameterDual[T]":
        inverse = 1 / self.value  # type: ignore[operator]
        inverse_squared = inverse * inverse  # type: ignore[operator]
        return ParameterDual(
            inverse,
            -self.du * inverse_squared,  # type: ignore[operator]
            -self.dv * inverse_squared,  # type: ignore[operator]
        )

    def __truediv__(self, other: object) -> "ParameterDual[T]":
        return self * self._coerce(other).reciprocal()

    def __rtruediv__(self, other: object) -> "ParameterDual[T]":
        return self._coerce(other) / self

    def sin(self) -> "ParameterDual[T]":
        sine = _sin(self.value)
        cosine = _cos(self.value)
        return ParameterDual(sine, cosine * self.du, cosine * self.dv)  # type: ignore[operator]

    def cos(self) -> "ParameterDual[T]":
        cosine = _cos(self.value)
        minus_sine = -_sin(self.value)
        return ParameterDual(
            cosine,
            minus_sine * self.du,  # type: ignore[operator]
            minus_sine * self.dv,  # type: ignore[operator]
        )

    def exp(self) -> "ParameterDual[T]":
        exponential = _exp(self.value)
        return ParameterDual(
            exponential,
            exponential * self.du,  # type: ignore[operator]
            exponential * self.dv,  # type: ignore[operator]
        )


@dataclass(frozen=True)
class IntervalJet:
    """First-order interval AD jet for a twelve-dimensional box."""

    value: arb
    gradient: tuple[arb, ...]

    @classmethod
    def variable(cls, value: arb, index: int, dimension: int) -> "IntervalJet":
        if not 0 <= index < dimension:
            raise IndexError("jet variable index is outside its dimension")
        return cls(
            value,
            tuple(arb(1 if column == index else 0) for column in range(dimension)),
        )

    @classmethod
    def constant(cls, value: arb, dimension: int) -> "IntervalJet":
        return cls(value, tuple(arb(0) for _ in range(dimension)))

    def _coerce(self, other: object) -> "IntervalJet":
        if isinstance(other, IntervalJet):
            if len(other.gradient) != len(self.gradient):
                raise ValueError("jet dimensions differ")
            return other
        return IntervalJet.constant(self.value * 0 + other, len(self.gradient))

    def __add__(self, other: object) -> "IntervalJet":
        right = self._coerce(other)
        return IntervalJet(
            self.value + right.value,
            tuple(a + b for a, b in zip(self.gradient, right.gradient)),
        )

    __radd__ = __add__

    def __neg__(self) -> "IntervalJet":
        return IntervalJet(-self.value, tuple(-value for value in self.gradient))

    def __sub__(self, other: object) -> "IntervalJet":
        return self + (-self._coerce(other))

    def __rsub__(self, other: object) -> "IntervalJet":
        return self._coerce(other) - self

    def __mul__(self, other: object) -> "IntervalJet":
        right = self._coerce(other)
        return IntervalJet(
            self.value * right.value,
            tuple(
                left_d * right.value + self.value * right_d
                for left_d, right_d in zip(self.gradient, right.gradient)
            ),
        )

    __rmul__ = __mul__

    def reciprocal(self) -> "IntervalJet":
        inverse = 1 / self.value
        inverse_squared = inverse * inverse
        return IntervalJet(
            inverse,
            tuple(-value * inverse_squared for value in self.gradient),
        )

    def __truediv__(self, other: object) -> "IntervalJet":
        return self * self._coerce(other).reciprocal()

    def __rtruediv__(self, other: object) -> "IntervalJet":
        return self._coerce(other) / self

    def sin(self) -> "IntervalJet":
        sine = self.value.sin()
        cosine = self.value.cos()
        return IntervalJet(sine, tuple(cosine * value for value in self.gradient))

    def cos(self) -> "IntervalJet":
        cosine = self.value.cos()
        minus_sine = -self.value.sin()
        return IntervalJet(
            cosine, tuple(minus_sine * value for value in self.gradient)
        )

    def exp(self) -> "IntervalJet":
        exponential = self.value.exp()
        return IntervalJet(
            exponential, tuple(exponential * value for value in self.gradient)
        )


def augmented_rhs(values: Sequence[T]) -> tuple[T, ...]:
    """Evaluate state plus exact ``u,v`` sensitivity dynamics.

    ``values`` has order ``z, d_u z, d_v z`` with four entries per block.
    The generic scalar may be an Arb ball, an Arb power series, or a nested
    interval AD jet.
    """

    if len(values) != 12:
        raise ValueError("augmented state must have dimension twelve")
    exemplar = values[0]
    zero = _zero_like(exemplar)
    one = _one_like(exemplar)
    dual_one = ParameterDual.constant(one)
    state = tuple(
        ParameterDual(values[index], values[4 + index], values[8 + index])
        for index in range(4)
    )
    u = ParameterDual(zero, one, zero)
    v = ParameterDual(zero, zero, one)
    mass2 = u.exp()
    length2 = v.exp()

    theta1, theta2, omega1, omega2 = state
    delta = theta1 - theta2
    sine_delta = delta.sin()
    cosine_delta = delta.cos()

    m11 = dual_one + mass2
    m12 = mass2 * length2 * cosine_delta
    m22 = mass2 * length2 * length2
    forcing1 = (
        -mass2 * length2 * sine_delta * omega2 * omega2
        - (dual_one + mass2) * theta1.sin()
    )
    forcing2 = (
        mass2 * length2 * sine_delta * omega1 * omega1
        - mass2 * length2 * theta2.sin()
    )
    determinant = m11 * m22 - m12 * m12
    alpha1 = (m22 * forcing1 - m12 * forcing2) / determinant
    alpha2 = (-m12 * forcing1 + m11 * forcing2) / determinant
    derivatives = (omega1, omega2, alpha1, alpha2)
    return tuple(
        [entry.value for entry in derivatives]
        + [entry.du for entry in derivatives]
        + [entry.dv for entry in derivatives]
    )


@dataclass(frozen=True)
class ValidatedTransferConfig:
    precision_bits: int = 160
    taylor_order: int = 8
    step_size: Fraction = Q(1, 100)
    tube_inflation: Fraction = Q(6, 5)
    maximum_tube_iterations: int = 12

    def __post_init__(self) -> None:
        if type(self.precision_bits) is not int or self.precision_bits < 80:
            raise ValueError("precision_bits must be an integer at least 80")
        if type(self.taylor_order) is not int or not 3 <= self.taylor_order <= 20:
            raise ValueError("taylor_order must lie between 3 and 20")
        if type(self.step_size) is not Fraction or self.step_size <= 0:
            raise ValueError("step_size must be a positive Fraction")
        if type(self.tube_inflation) is not Fraction or self.tube_inflation <= 1:
            raise ValueError("tube_inflation must be a Fraction greater than one")
        if (
            type(self.maximum_tube_iterations) is not int
            or self.maximum_tube_iterations < 1
        ):
            raise ValueError("maximum_tube_iterations must be positive")


@dataclass(frozen=True)
class ProtocolTarget:
    name: str
    launch: tuple[Fraction, Fraction, Fraction, Fraction]
    sensor: str
    terminal_time: Fraction
    declared_centre: tuple[Fraction, Fraction]
    declared_radius: tuple[Fraction, Fraction]

    def response_indices(self) -> tuple[int, int]:
        state_index = {
            "theta_1": 0,
            "theta_2": 1,
            "scaled_omega_1": 2,
            "scaled_omega_2": 3,
        }.get(self.sensor)
        if state_index is None:
            raise ValueError("unsupported target sensor")
        return 4 + state_index, 8 + state_index


def active_protocol_targets() -> tuple[ProtocolTarget, ProtocolTarget]:
    """Return the two protocols carrying nonzero weight in the exact design."""

    return (
        ProtocolTarget(
            "launch-A / theta-2 / tau-1",
            (Q(4, 5), Q(-7, 20), Q(0), Q(0)),
            "theta_2",
            Q(1),
            (Q(265, 3136), Q(-4041, 8894)),
            (Q(101, 100000), Q(101, 100000)),
        ),
        ProtocolTarget(
            "launch-B / scaled-omega-1 / tau-5/4",
            (Q(-3, 5), Q(9, 10), Q(0), Q(0)),
            "scaled_omega_1",
            Q(5, 4),
            (Q(2357, 5025), Q(13, 3140)),
            (Q(101, 100000), Q(101, 100000)),
        ),
    )


def _arb_fraction(value: Fraction) -> arb:
    return arb(f"{value.numerator}/{value.denominator}")


def _symmetric_ball(midpoint: arb, radius: arb) -> arb:
    return arb(midpoint.mid(), radius.abs_upper())


def _magnitude(value: arb) -> arb:
    if not value.is_finite():
        raise StepValidationError("interval evaluation produced a non-finite ball")
    return value.abs_upper()


def _upper_bound_maximum(values: Sequence[arb]) -> arb:
    """Return a proved upper bound for a finite list of nonnegative balls."""

    result = arb(0)
    for value in values:
        candidate = value.abs_upper()
        if result < candidate:
            result = candidate
        elif not candidate < result:
            # The order is interval-indeterminate.  Addition is a conservative
            # upper bound for the maximum and avoids a floating proof decision.
            result = (result + candidate).abs_upper()
    return result


def _polynomial_value(coefficients: Sequence[arb], argument: arb) -> arb:
    result = arb(0)
    for coefficient in reversed(coefficients):
        result = result * argument + coefficient
    return result


def _compose_polynomial_series(
    coefficients: Sequence[arb], centre: arb, precision: int
) -> arb_series:
    variable = arb_series([centre, arb(1)], prec=precision)
    result = arb_series([arb(0)], prec=precision)
    for coefficient in reversed(coefficients):
        result = result * variable + coefficient
    return result


def _taylor_polynomial(midpoint: Sequence[arb], order: int) -> list[list[arb]]:
    precision = order + 1
    current = [arb_series([value], prec=precision) for value in midpoint]
    for _ in range(order):
        right_hand_side = augmented_rhs(current)
        updated: list[arb_series] = []
        for initial, derivative in zip(midpoint, right_hand_side):
            integrated = derivative.integral()
            coefficients = integrated.coeffs()[:precision]
            if coefficients:
                coefficients[0] = coefficients[0] + initial
            else:
                coefficients = [initial]
            updated.append(arb_series(coefficients, prec=precision))
        current = updated
    result: list[list[arb]] = []
    for series in current:
        coefficients = list(series.coeffs())
        coefficients.extend(arb(0) for _ in range(precision - len(coefficients)))
        # Fix one actual polynomial: Arb midpoints are exact dyadic values.
        # The later residual calculation outwardly encloses this polynomial;
        # it never treats coefficient uncertainty as an unproved trajectory.
        result.append([coefficient.mid() for coefficient in coefficients[:precision]])
    return result


def _residual_bounds(polynomials: Sequence[Sequence[arb]], h: arb) -> list[arb]:
    order = len(polynomials[0]) - 1
    precision = order + 1
    zero_series = [
        arb_series(list(coefficients), prec=precision) for coefficients in polynomials
    ]
    zero_rhs = augmented_rhs(zero_series)
    zero_residual = [
        polynomial.derivative() - rhs
        for polynomial, rhs in zip(zero_series, zero_rhs)
    ]

    time_interval = arb(h / 2, (h / 2).abs_upper())
    shifted = [
        _compose_polynomial_series(coefficients, time_interval, precision)
        for coefficients in polynomials
    ]
    shifted_derivatives = [
        _compose_polynomial_series(
            [index * coefficient for index, coefficient in enumerate(coefficients)][1:],
            time_interval,
            precision,
        )
        for coefficients in polynomials
    ]
    shifted_rhs = augmented_rhs(shifted)
    shifted_residual = [
        derivative - rhs
        for derivative, rhs in zip(shifted_derivatives, shifted_rhs)
    ]

    bounds: list[arb] = []
    for at_zero, over_step in zip(zero_residual, shifted_residual):
        total = arb(0)
        zero_coefficients = at_zero.coeffs()
        for degree in range(order):
            coefficient = (
                zero_coefficients[degree]
                if degree < len(zero_coefficients)
                else arb(0)
            )
            total += _magnitude(coefficient) * h**degree
        high_coefficients = over_step.coeffs()
        highest = (
            high_coefficients[order]
            if order < len(high_coefficients)
            else arb(0)
        )
        total += _magnitude(highest) * h**order
        bounds.append(total.abs_upper())
    return bounds


def _box_jacobian_magnitudes(box: Sequence[arb]) -> list[list[arb]]:
    dimension = len(box)
    jets = [IntervalJet.variable(value, index, dimension) for index, value in enumerate(box)]
    result = augmented_rhs(jets)
    return [
        [_magnitude(value) for value in component.gradient]
        for component in result
    ]


def _component_radii(boxes: Sequence[arb]) -> list[arb]:
    return [value.rad().abs_upper() for value in boxes]


def _strictly_dominates(left: arb, right: arb) -> bool:
    """Return whether nonnegative ``left`` is proved at least ``right``."""

    return bool(right < left or (right == 0 and not left < 0))


class StepValidationError(RuntimeError):
    """Raised when no Picard self-mapping tube is proved for a step."""


@dataclass(frozen=True)
class ValidatedStep:
    endpoint: tuple[arb, ...]
    tube_iterations: int
    maximum_endpoint_radius: arb
    maximum_tube_radius: arb


def _validated_step(
    initial: Sequence[arb], h_fraction: Fraction, config: ValidatedTransferConfig
) -> ValidatedStep:
    if len(initial) != 12:
        raise ValueError("validated step requires twelve initial enclosures")
    h = _arb_fraction(h_fraction)
    midpoint = [value.mid() for value in initial]
    polynomials = _taylor_polynomial(midpoint, config.taylor_order)
    at_zero = [_polynomial_value(row, arb(0)) for row in polynomials]
    at_end = [_polynomial_value(row, h) for row in polynomials]
    time_interval = arb(h / 2, (h / 2).abs_upper())
    polynomial_ranges = [
        _polynomial_value(row, time_interval) for row in polynomials
    ]
    residual = _residual_bounds(polynomials, h)
    initial_error = [
        _magnitude(value - polynomial)
        for value, polynomial in zip(initial, at_zero)
    ]
    base = [
        (error + h * defect).abs_upper()
        for error, defect in zip(initial_error, residual)
    ]
    inflation = _arb_fraction(config.tube_inflation)
    tiny = arb(0, arb(f"1e-{max(20, config.precision_bits // 4)}"))
    rho = [
        (inflation * bound + tiny.rad()).abs_upper()
        for bound in base
    ]

    for iteration in range(1, config.maximum_tube_iterations + 1):
        tube = [
            arb(value.mid(), value.rad() + radius.abs_upper())
            for value, radius in zip(polynomial_ranges, rho)
        ]
        jacobian = _box_jacobian_magnitudes(tube)
        target = [
            (
                bound
                + h
                * sum(
                    (entry * radius for entry, radius in zip(row, rho)),
                    arb(0),
                )
            ).abs_upper()
            for bound, row in zip(base, jacobian)
        ]
        if all(
            _strictly_dominates(radius, needed)
            for radius, needed in zip(rho, target)
        ):
            endpoint = tuple(
                _symmetric_ball(value, value.rad() + needed)
                for value, needed in zip(at_end, target)
            )
            return ValidatedStep(
                endpoint,
                iteration,
                _upper_bound_maximum(
                    [_magnitude(value.rad()) for value in endpoint]
                ),
                _upper_bound_maximum(rho),
            )
        rho = [
            (inflation * (needed if radius < needed else radius)).abs_upper()
            for radius, needed in zip(rho, target)
        ]
    raise StepValidationError(
        "Picard tube self-mapping inequality was not proved within the "
        f"declared {config.maximum_tube_iterations} iterations"
    )


@dataclass(frozen=True)
class ValidatedTrajectory:
    terminal: tuple[arb, ...]
    step_count: int
    maximum_tube_iterations: int
    maximum_endpoint_radius: arb
    maximum_tube_radius: arb


def validated_augmented_trajectory(
    launch: Sequence[Fraction],
    terminal_time: Fraction,
    config: ValidatedTransferConfig = ValidatedTransferConfig(),
) -> ValidatedTrajectory:
    """Enclose the nominal state and both exact parameter sensitivities."""

    if len(launch) != 4 or any(type(value) is not Fraction for value in launch):
        raise TypeError("launch must contain exactly four Fractions")
    if type(terminal_time) is not Fraction or terminal_time <= 0:
        raise TypeError("terminal_time must be a positive Fraction")
    quotient, remainder = divmod(terminal_time, config.step_size)
    step_sizes = [config.step_size] * int(quotient)
    if remainder:
        step_sizes.append(remainder)
    if not step_sizes or sum(step_sizes, Q(0)) != terminal_time:
        raise AssertionError("internal rational time partition failed")

    with ctx.workprec(config.precision_bits):
        current: tuple[arb, ...] = tuple(
            [_arb_fraction(value) for value in launch] + [arb(0)] * 8
        )
        maximum_iterations = 0
        maximum_endpoint_radius = arb(0)
        maximum_tube_radius = arb(0)
        for h in step_sizes:
            step = _validated_step(current, h, config)
            current = step.endpoint
            maximum_iterations = max(maximum_iterations, step.tube_iterations)
            maximum_endpoint_radius = _upper_bound_maximum(
                [maximum_endpoint_radius, step.maximum_endpoint_radius]
            )
            maximum_tube_radius = _upper_bound_maximum(
                [maximum_tube_radius, step.maximum_tube_radius]
            )
        return ValidatedTrajectory(
            current,
            len(step_sizes),
            maximum_iterations,
            maximum_endpoint_radius,
            maximum_tube_radius,
        )


def _strict_ball_subset_of_rational_interval(
    value: arb, lower: Fraction, upper: Fraction
) -> bool:
    return bool(_arb_fraction(lower) < value and value < _arb_fraction(upper))


def _rational_outer_interval(value: arb, denominator: int = 10**18) -> tuple[Fraction, Fraction]:
    """Create and verify a conservative fixed-denominator rational hull."""

    if type(denominator) is not int or denominator < 1:
        raise ValueError("denominator must be a positive integer")
    approximate_lower = math.floor(float(value.lower()) * denominator) - 2
    approximate_upper = math.ceil(float(value.upper()) * denominator) + 2
    lower = Q(approximate_lower, denominator)
    upper = Q(approximate_upper, denominator)
    while not _arb_fraction(lower) < value:
        lower -= Q(1, denominator)
    while not value < _arb_fraction(upper):
        upper += Q(1, denominator)
    return lower, upper


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _strict_json_equal(left: object, right: object) -> bool:
    """Compare JSON-shaped values without Python's bool/int equivalence."""

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


def _ball_record(value: arb) -> dict[str, object]:
    lower, upper = _rational_outer_interval(value)
    return {
        "lower_exact": _fraction_text(lower),
        "upper_exact": _fraction_text(upper),
        "decimal_midpoint": float(value.mid()),
        "decimal_radius_upper": float(value.rad().abs_upper()),
    }


def validate_protocol_target(
    target: ProtocolTarget,
    config: ValidatedTransferConfig = ValidatedTransferConfig(),
) -> dict[str, object]:
    # ``validated_augmented_trajectory`` already performs the ODE proof under
    # the declared precision.  Keep the subsequent ball comparisons,
    # rational hull construction, and decimal serialization under that same
    # precision as well.  Otherwise an unrelated caller that changes the
    # process-global Flint context can change an otherwise identical report.
    with ctx.workprec(config.precision_bits):
        trajectory = validated_augmented_trajectory(
            target.launch, target.terminal_time, config
        )
        response = tuple(
            trajectory.terminal[index] for index in target.response_indices()
        )
        response_records = [_ball_record(value) for value in response]
        memberships = tuple(
            _strict_ball_subset_of_rational_interval(
                value, centre - radius, centre + radius
            )
            for value, centre, radius in zip(
                response, target.declared_centre, target.declared_radius
            )
        )
        slack = tuple(
            min(
                Q(record["lower_exact"]) - (centre - radius),
                (centre + radius) - Q(record["upper_exact"]),
            )
            for record, centre, radius in zip(
                response_records, target.declared_centre, target.declared_radius
            )
        )
        certified = all(memberships) and all(value > 0 for value in slack)
        return {
            "status": "proved" if certified else "unresolved",
            "unresolved_reason": (
                None
                if certified
                else "an outward response enclosure is not contained in the declared box"
            ),
            "name": target.name,
            "launch_exact": [_fraction_text(value) for value in target.launch],
            "sensor": target.sensor,
            "terminal_time_exact": _fraction_text(target.terminal_time),
            "response_enclosure": response_records,
            "declared_response_centre_exact": [
                _fraction_text(value) for value in target.declared_centre
            ],
            "declared_response_radius_exact": [
                _fraction_text(value) for value in target.declared_radius
            ],
            "declared_box_membership_by_source": list(memberships),
            "declared_box_inclusion_slack_exact": [
                _fraction_text(value) for value in slack
            ],
            "inclusion_slack_is_strictly_positive": all(value > 0 for value in slack),
            "declared_box_membership_certified": certified,
            "validated_step_count": trajectory.step_count,
            "maximum_picard_tube_iterations": trajectory.maximum_tube_iterations,
            "maximum_endpoint_radius_upper": float(
                trajectory.maximum_endpoint_radius.abs_upper()
            ),
            "maximum_tube_radius_upper": float(
                trajectory.maximum_tube_radius.abs_upper()
            ),
        }


def _unresolved_target_record(target: ProtocolTarget, error: Exception) -> dict[str, object]:
    return {
        "status": "unresolved",
        "unresolved_reason": str(error),
        "name": target.name,
        "launch_exact": [_fraction_text(value) for value in target.launch],
        "sensor": target.sensor,
        "terminal_time_exact": _fraction_text(target.terminal_time),
        "response_enclosure": None,
        "declared_response_centre_exact": [
            _fraction_text(value) for value in target.declared_centre
        ],
        "declared_response_radius_exact": [
            _fraction_text(value) for value in target.declared_radius
        ],
        "declared_box_membership_by_source": [False, False],
        "declared_box_inclusion_slack_exact": None,
        "inclusion_slack_is_strictly_positive": False,
        "declared_box_membership_certified": False,
        "validated_step_count": 0,
        "maximum_picard_tube_iterations": 0,
        "maximum_endpoint_radius_upper": None,
        "maximum_tube_radius_upper": None,
    }


def attempt_protocol_target(
    target: ProtocolTarget,
    config: ValidatedTransferConfig = ValidatedTransferConfig(),
) -> dict[str, object]:
    """Return ``unresolved`` rather than promote a failed validation attempt."""

    try:
        return validate_protocol_target(target, config)
    except (StepValidationError, ArithmeticError, ZeroDivisionError) as error:
        return _unresolved_target_record(target, error)


def _config_record(config: ValidatedTransferConfig) -> dict[str, object]:
    return {
        "precision_bits": config.precision_bits,
        "taylor_order": config.taylor_order,
        "step_size_exact": _fraction_text(config.step_size),
        "tube_inflation_exact": _fraction_text(config.tube_inflation),
        "maximum_tube_iterations": config.maximum_tube_iterations,
    }


def build_validated_transfer_report(
    config: ValidatedTransferConfig = ValidatedTransferConfig(),
) -> dict[str, object]:
    protocols = [attempt_protocol_target(target, config) for target in active_protocol_targets()]
    passed = all(row["declared_box_membership_certified"] is True for row in protocols)
    return {
        "schema_version": SCHEMA_VERSION,
        "method": METHOD,
        "status": "proved" if passed else "unresolved",
        "source_coordinates": list(SOURCE_COORDINATES),
        "nominal_parameter_point_exact": {"u": "0/1", "v": "0/1"},
        "dimensionless_representative_exact": {
            "m1": "1/1",
            "m2": "exp(u)",
            "l1": "1/1",
            "l2": "exp(v)",
            "g": "1/1",
        },
        "configuration": _config_record(config),
        "proof_dependency_contract": {
            "outward_ball_arithmetic": "python-flint>=0.9,<0.10 (Arb)",
            "exact_rational_arithmetic": "Python fractions.Fraction",
            "ordinary_scipy_ode_solver_used_in_proof": False,
            "install_command": "python -m pip install -r requirements.txt",
        },
        "protocols": protocols,
        "all_active_declared_box_memberships_certified": passed,
        "enclosed_protocol_transfer_ready": passed,
        "scope_flags": {
            "two_active_protocol_responses_at_nominal_point_certified": passed,
            "seven_candidate_selection_certified": False,
            "seven_candidate_efficiency_certified": False,
            "parameter_neighborhood_uniformity_certified": False,
            "empirical_model_adequacy_certified": False,
            "hardware_calibration_certified": False,
        },
        "theorem_obligations": {
            "outward_scalar_arithmetic": "Arb balls at the declared precision",
            "state_and_parameter_sensitivity_ode": "joint 12-dimensional forward system",
            "step_existence_and_containment": "componentwise Picard self-mapping inequality",
            "defect_bound": "Taylor theorem with interval coefficient over every step",
            "flow_to_box_link": "strict inclusion in each declared rational response box",
        },
        "scope_boundary": (
            "Pointwise nominal-parameter transfer for exactly the two active protocols; "
            "no parameter-neighbourhood enclosure and no claim for the five inactive candidates. "
            "The word physical refers only to the declared nonlinear dimensionless "
            "double-pendulum model, not empirical hardware or nature."
        ),
    }


def validated_active_enclosed_protocols(
    config: ValidatedTransferConfig = ValidatedTransferConfig(),
) -> tuple[EnclosedProtocol, EnclosedProtocol]:
    """Return the exact-engine inputs only after physical membership is proved.

    The returned rational boxes are byte-for-byte the active declarations used
    by the conditional protocol engine.  Arb does not propose replacement
    centres or radii; it proves that the physical response belongs to these
    already-declared boxes.
    """

    report = build_validated_transfer_report(config)
    if report["all_active_declared_box_memberships_certified"] is not True:
        raise StepValidationError(
            "active response boxes cannot be exported to EnclosedProtocol: "
            "validated physical membership is unresolved"
        )
    costs = (Q(1), Q(5, 4))
    return tuple(
        EnclosedProtocol.from_rows(
            target.name,
            [target.declared_centre],
            [target.declared_radius],
            [[Q(1)]],
            cost,
        )
        for target, cost in zip(active_protocol_targets(), costs)
    )  # type: ignore[return-value]


def build_physical_positive_floor_certificate(
    config: ValidatedTransferConfig = ValidatedTransferConfig(),
) -> dict[str, object]:
    """Compose outward ODE membership with the exact rational OIG theorem."""

    transfer = build_validated_transfer_report(config)
    if transfer["all_active_declared_box_memberships_certified"] is not True:
        return {
            "schema_version": PHYSICAL_CERTIFICATE_SCHEMA_VERSION,
            "status": "unresolved",
            "validated_transfer": transfer,
            "exact_active_enclosed_design": None,
            "physical_positive_floor_certified": False,
            "physical_scope_definition": (
                "physical means the exact response of the declared nonlinear "
                "dimensionless double-pendulum equations; it does not mean that "
                "the equations, calibration, or apparatus have been empirically validated"
            ),
            "scope_flags": {
                "declared_dimensionless_model_floor_certified": False,
                "seven_candidate_selection_certified": False,
                "seven_candidate_efficiency_certified": False,
                "parameter_neighborhood_uniformity_certified": False,
                "empirical_model_adequacy_certified": False,
                "hardware_calibration_certified": False,
            },
            "unresolved_reason": (
                "at least one active physical response-box membership was not proved"
            ),
        }
    enclosed = tuple(
        EnclosedProtocol.from_rows(
            target.name,
            [target.declared_centre],
            [target.declared_radius],
            [[Q(1)]],
            cost,
        )
        for target, cost in zip(active_protocol_targets(), (Q(1), Q(5, 4)))
    )
    exact_design = design_enclosed_protocols(
        enclosed,
        [[Q(1), Q(0)], [Q(0), Q(1)]],
        weight_denominator=10_000,
        dual_vector_scale=100_000,
        amplitude=Q(1),
        exposure_multiplier=10,
    )
    robust = exact_design["response_box_robustness"]
    floor = Q(robust["robust_physical_floor_lower_exact"])
    passed = bool(
        exact_design["overall_passed"] is True
        and robust["robust_floor_is_positive"] is True
        and floor > 0
    )
    return {
        "schema_version": PHYSICAL_CERTIFICATE_SCHEMA_VERSION,
        "status": "proved" if passed else "unresolved",
        "validated_transfer": transfer,
        "exact_active_enclosed_design": exact_design,
        "robust_physical_floor_lower_exact": _fraction_text(floor),
        "physical_positive_floor_certified": passed,
        "physical_scope_definition": (
            "physical means the exact response of the declared nonlinear "
            "dimensionless double-pendulum equations; it does not mean that "
            "the equations, calibration, or apparatus have been empirically validated"
        ),
        "scope_flags": {
            "declared_dimensionless_model_floor_certified": passed,
            "two_active_protocol_fixed_mixture_certified": passed,
            "seven_candidate_selection_certified": False,
            "seven_candidate_efficiency_certified": False,
            "parameter_neighborhood_uniformity_certified": False,
            "empirical_model_adequacy_certified": False,
            "hardware_calibration_certified": False,
        },
        "logical_composition": (
            "outward ODE response membership AND exact for-all-response-in-box "
            "design theorem imply the nominal physical double-pendulum floor"
        ),
        "scope_boundary": (
            "The floor concerns the declared dimensionless model for the two-protocol "
            "experiment at u=v=0; it is not a uniform parameter-neighbourhood, "
            "model-adequacy, calibration, or hardware statement."
        ),
        "reproduction_commands": [
            "python -m pip install -r requirements.txt",
            "python oig_double_pendulum_validated_transfer.py --physical-output artifacts/double_pendulum_physical_positive_floor.json",
            "python oig_double_pendulum_validated_transfer.py --verify-physical artifacts/double_pendulum_physical_positive_floor.json",
            "python -m unittest -v test_oig_double_pendulum_validated_transfer.py",
        ],
        "unresolved_reason": None if passed else "exact active design floor is not positive",
    }


def verify_physical_positive_floor_certificate(
    report: dict[str, object],
) -> dict[str, object]:
    """Independently recompute both premises of the composed theorem."""

    try:
        if (
            not isinstance(report, dict)
            or report.get("schema_version") != PHYSICAL_CERTIFICATE_SCHEMA_VERSION
        ):
            raise ValueError("unknown physical positive-floor schema")
        transfer = report.get("validated_transfer")
        child = report.get("exact_active_enclosed_design")
        if not isinstance(transfer, dict) or not isinstance(child, dict):
            raise ValueError("certificate is missing one of its two proof premises")
        transfer_verification = verify_validated_transfer_report(transfer)
        if transfer_verification.get("passed") is not True:
            raise ValueError("outward ODE membership premise fails verification")
        child_verification = verify_enclosed_design_report(child)
        if child_verification.get("passed") is not True:
            raise ValueError("exact enclosed-design premise fails verification")
        floor = Q(
            child["response_box_robustness"][  # type: ignore[index]
                "robust_physical_floor_lower_exact"
            ]
        )
        if floor <= 0 or report.get("robust_physical_floor_lower_exact") != _fraction_text(floor):
            raise ValueError("reported composed physical floor is not the positive child floor")
        rebuilt = build_physical_positive_floor_certificate(
            ValidatedTransferConfig(
                precision_bits=transfer["configuration"]["precision_bits"],  # type: ignore[index]
                taylor_order=transfer["configuration"]["taylor_order"],  # type: ignore[index]
                step_size=Q(transfer["configuration"]["step_size_exact"]),  # type: ignore[index]
                tube_inflation=Q(
                    transfer["configuration"]["tube_inflation_exact"]  # type: ignore[index]
                ),
                maximum_tube_iterations=transfer["configuration"][  # type: ignore[index]
                    "maximum_tube_iterations"
                ],
            )
        )
        if not _strict_json_equal(rebuilt, report):
            raise ValueError("composed certificate does not equal independent recomputation")
        return {
            "passed": True,
            "physical_positive_floor_verified": True,
            "robust_physical_floor_lower_exact": _fraction_text(floor),
            "method": "outward ODE membership composed with exact rational box theorem",
        }
    except Exception as error:
        return {
            "passed": False,
            "physical_positive_floor_verified": False,
            "error": str(error),
        }


def verify_validated_transfer_report(report: dict[str, object]) -> dict[str, object]:
    """Recompute the outward proof; never trust embedded pass fields."""

    try:
        if not isinstance(report, dict) or report.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unknown validated-transfer schema")
        configuration = report.get("configuration")
        if not isinstance(configuration, dict):
            raise ValueError("missing validated-transfer configuration")
        config = ValidatedTransferConfig(
            precision_bits=configuration.get("precision_bits"),  # type: ignore[arg-type]
            taylor_order=configuration.get("taylor_order"),  # type: ignore[arg-type]
            step_size=Q(configuration.get("step_size_exact")),  # type: ignore[arg-type]
            tube_inflation=Q(configuration.get("tube_inflation_exact")),  # type: ignore[arg-type]
            maximum_tube_iterations=configuration.get("maximum_tube_iterations"),  # type: ignore[arg-type]
        )
        rebuilt = build_validated_transfer_report(config)
        if not _strict_json_equal(rebuilt, report):
            raise ValueError("serialized report does not equal an independent recomputation")
        if rebuilt["all_active_declared_box_memberships_certified"] is not True:
            raise ValueError("one or more physical response-box memberships remain unresolved")
        return {
            "passed": True,
            "method": METHOD,
            "active_protocol_count": 2,
            "physical_response_box_membership_verified": True,
            "enclosed_protocol_transfer_ready": True,
        }
    except Exception as error:
        return {
            "passed": False,
            "physical_response_box_membership_verified": False,
            "enclosed_protocol_transfer_ready": False,
            "error": str(error),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--output", type=Path)
    action.add_argument("--verify", type=Path)
    action.add_argument("--physical-output", type=Path)
    action.add_argument("--verify-physical", type=Path)
    parser.add_argument("--step-denominator", type=int, default=100)
    parser.add_argument("--taylor-order", type=int, default=8)
    parser.add_argument("--precision-bits", type=int, default=160)
    args = parser.parse_args()
    if args.verify is not None:
        report = json.loads(args.verify.read_text())
        verification = verify_validated_transfer_report(report)
        print(json.dumps(verification, indent=2, sort_keys=True))
        raise SystemExit(0 if verification.get("passed") is True else 1)
    if args.verify_physical is not None:
        report = json.loads(args.verify_physical.read_text())
        verification = verify_physical_positive_floor_certificate(report)
        print(json.dumps(verification, indent=2, sort_keys=True))
        raise SystemExit(0 if verification.get("passed") is True else 1)
    config = ValidatedTransferConfig(
        precision_bits=args.precision_bits,
        taylor_order=args.taylor_order,
        step_size=Q(1, args.step_denominator),
    )
    report = (
        build_physical_positive_floor_certificate(config)
        if args.physical_output is not None
        else build_validated_transfer_report(config)
    )
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    output = args.physical_output if args.physical_output is not None else args.output
    if output is None:
        print(rendered, end="")
    else:
        output.write_text(rendered)


if __name__ == "__main__":
    main()
