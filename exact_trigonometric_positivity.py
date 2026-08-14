#!/usr/bin/env python3
"""Exact rational positivity certificates for cosine-series densities.

The floating Fejer--Riesz factors in Arithmetic Sensing IV are useful spectral
certificates.  This module adds a logically independent exact layer.  Decimal
coefficients are treated as rational numbers, the cosine series is converted
to a polynomial in ``x=cos(theta)``, and a Sturm sequence proves that the
polynomial cannot cross declared rational lower or upper bounds on ``[-1,1]``.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence


Polynomial = list[Fraction]


def _trim(polynomial: Polynomial) -> Polynomial:
    result = polynomial[:]
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result or [Fraction(0)]


def _add(left: Polynomial, right: Polynomial) -> Polynomial:
    size = max(len(left), len(right))
    result = [Fraction(0)] * size
    for index in range(size):
        result[index] = (
            left[index] if index < len(left) else Fraction(0)
        ) + (right[index] if index < len(right) else Fraction(0))
    return _trim(result)


def _scale(polynomial: Polynomial, scalar: Fraction) -> Polynomial:
    return _trim([scalar * coefficient for coefficient in polynomial])


def _multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            result[left_index + right_index] += left_value * right_value
    return _trim(result)


def _derivative(polynomial: Polynomial) -> Polynomial:
    if len(polynomial) == 1:
        return [Fraction(0)]
    return _trim(
        [index * polynomial[index] for index in range(1, len(polynomial))]
    )


def _divmod_polynomial(
    dividend: Polynomial, divisor: Polynomial
) -> tuple[Polynomial, Polynomial]:
    divisor = _trim(divisor)
    if divisor == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    remainder = _trim(dividend)
    quotient = [Fraction(0)] * max(1, len(remainder) - len(divisor) + 1)
    while remainder != [0] and len(remainder) >= len(divisor):
        offset = len(remainder) - len(divisor)
        factor = remainder[-1] / divisor[-1]
        quotient[offset] += factor
        for index, value in enumerate(divisor):
            remainder[index + offset] -= factor * value
        remainder = _trim(remainder)
    return _trim(quotient), remainder


def _evaluate(polynomial: Polynomial, point: Fraction) -> Fraction:
    result = Fraction(0)
    for coefficient in reversed(polynomial):
        result = result * point + coefficient
    return result


def cosine_density_power_polynomial(
    coefficients: Sequence[str | int | Fraction],
    constant: str | int | Fraction = 1,
) -> Polynomial:
    """Convert ``constant+2 sum c_r T_r(x)`` to the power basis exactly."""
    rational_coefficients = [Fraction(value) for value in coefficients]
    density = [Fraction(constant)]
    if not rational_coefficients:
        return density
    previous = [Fraction(1)]
    current = [Fraction(0), Fraction(1)]
    for harmonic, coefficient in enumerate(rational_coefficients, start=1):
        if harmonic == 1:
            chebyshev = current
        else:
            following = _add(
                _scale(_multiply([Fraction(0), Fraction(1)], current), 2),
                _scale(previous, -1),
            )
            previous, current = current, following
            chebyshev = current
        density = _add(density, _scale(chebyshev, 2 * coefficient))
    return _trim(density)


def sturm_sequence(polynomial: Polynomial) -> list[Polynomial]:
    """Return the exact Sturm sequence of a nonconstant rational polynomial."""
    polynomial = _trim(polynomial)
    derivative = _derivative(polynomial)
    if derivative == [0]:
        raise ValueError("Sturm sequence requires a nonconstant polynomial")
    sequence = [polynomial, derivative]
    while sequence[-1] != [0]:
        _, remainder = _divmod_polynomial(sequence[-2], sequence[-1])
        if remainder == [0]:
            break
        sequence.append(_scale(remainder, -1))
    return sequence


def _sign_variations(sequence: Sequence[Polynomial], point: Fraction) -> int:
    signs = []
    for polynomial in sequence:
        value = _evaluate(polynomial, point)
        if value != 0:
            signs.append(1 if value > 0 else -1)
    return sum(left != right for left, right in zip(signs[:-1], signs[1:]))


@dataclass(frozen=True)
class RationalContinuumCertificate:
    lower_bound: Fraction
    upper_bound: Fraction
    lower_root_count: int
    upper_root_count: int
    lower_variations_at_minus_one: int
    lower_variations_at_plus_one: int
    upper_variations_at_minus_one: int
    upper_variations_at_plus_one: int
    lower_value_at_minus_one: Fraction
    lower_value_at_plus_one: Fraction
    upper_value_at_minus_one: Fraction
    upper_value_at_plus_one: Fraction
    lower_value_at_zero: Fraction
    upper_value_at_zero: Fraction

    @property
    def certified(self) -> bool:
        return (
            self.lower_root_count == 0
            and self.upper_root_count == 0
            and self.lower_value_at_minus_one > 0
            and self.lower_value_at_plus_one > 0
            and self.upper_value_at_minus_one > 0
            and self.upper_value_at_plus_one > 0
            and self.lower_value_at_zero > 0
            and self.upper_value_at_zero > 0
        )


def rational_continuum_certificate(
    coefficients: Sequence[str | int | Fraction],
    lower_bound: str | int | Fraction,
    upper_bound: str | int | Fraction,
) -> RationalContinuumCertificate:
    """Prove ``lower_bound < p(theta) < upper_bound`` by Sturm's theorem."""
    lower = Fraction(lower_bound)
    upper = Fraction(upper_bound)
    if lower >= upper:
        raise ValueError("lower bound must be below upper bound")
    density = cosine_density_power_polynomial(coefficients)
    lower_polynomial = _add(density, [-lower])
    upper_polynomial = _add(_scale(density, -1), [upper])
    lower_sequence = sturm_sequence(lower_polynomial)
    upper_sequence = sturm_sequence(upper_polynomial)
    minus_one = Fraction(-1)
    plus_one = Fraction(1)
    lower_minus = _sign_variations(lower_sequence, minus_one)
    lower_plus = _sign_variations(lower_sequence, plus_one)
    upper_minus = _sign_variations(upper_sequence, minus_one)
    upper_plus = _sign_variations(upper_sequence, plus_one)
    return RationalContinuumCertificate(
        lower,
        upper,
        lower_minus - lower_plus,
        upper_minus - upper_plus,
        lower_minus,
        lower_plus,
        upper_minus,
        upper_plus,
        _evaluate(lower_polynomial, minus_one),
        _evaluate(lower_polynomial, plus_one),
        _evaluate(upper_polynomial, minus_one),
        _evaluate(upper_polynomial, plus_one),
        _evaluate(lower_polynomial, Fraction(0)),
        _evaluate(upper_polynomial, Fraction(0)),
    )
