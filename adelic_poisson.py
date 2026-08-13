#!/usr/bin/env python3
"""Exact character checks and high-precision adelic Poisson verification.

The identity tested is the adelic Poisson formula for

    f_{t,M}(x) = exp(-pi*t*x_infinity^2) 1_{M Zhat}(x_f).

Its diagonal sums reduce exactly to

    theta(t*M^2) = 1/(M*sqrt(t)) theta(1/(t*M^2)).

The proof is in RATIONAL_ADELES_AND_POISSON.md. Numerical output verifies a
proved identity and is not itself the proof.
"""

from __future__ import annotations

import argparse
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from typing import Iterable


def prime_factors(n: int) -> list[int]:
    """Return the distinct prime factors of a positive integer."""
    if n < 1:
        raise ValueError("n must be positive")
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            factors.append(divisor)
            while n % divisor == 0:
                n //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if n > 1:
        factors.append(n)
    return factors


def valuation(n: int, p: int) -> int:
    """Return v_p(n) for a nonzero integer n."""
    if n == 0:
        raise ValueError("valuation of zero is infinite")
    n = abs(n)
    result = 0
    while n % p == 0:
        result += 1
        n //= p
    return result


def p_adic_fractional_part(q: Fraction, p: int) -> Fraction:
    """Return the standard rational representative {q}_p in [0,1).

    It is characterized by q - {q}_p belonging to Z_p and by having a
    p-power denominator. Since Fraction is reduced, negative p-adic valuation
    occurs precisely when p divides q.denominator.
    """
    if q == 0:
        return Fraction(0, 1)
    k = valuation(q.denominator, p)
    if k == 0:
        return Fraction(0, 1)
    modulus = p**k
    denominator_unit = q.denominator // modulus
    residue = (q.numerator * pow(denominator_unit, -1, modulus)) % modulus
    return Fraction(residue, modulus)


def global_character_exponent(q: Fraction) -> Fraction:
    """Return -q + sum_p {q}_p, an exact integer for rational q.

    With psi_infinity(x)=exp(-2*pi*i*x) and
    psi_p(x)=exp(2*pi*i*{x}_p), this proves that the product character is one
    on the diagonal copy of Q.
    """
    exponent = -q
    for p in prime_factors(q.denominator):
        exponent += p_adic_fractional_part(q, p)
    if exponent.denominator != 1:
        raise AssertionError("global additive-character cancellation failed")
    return exponent


def gauss_legendre_pi(digits: int) -> Decimal:
    """Compute pi with guard digits using the Gauss-Legendre algorithm."""
    if digits < 10:
        raise ValueError("digits must be at least 10")
    with localcontext() as context:
        context.prec = digits + 15
        one = Decimal(1)
        two = Decimal(2)
        four = Decimal(4)
        a = one
        b = one / two.sqrt()
        t = one / four
        multiplier = one
        iterations = max(5, digits.bit_length() + 1)
        for _ in range(iterations):
            next_a = (a + b) / two
            b = (a * b).sqrt()
            t -= multiplier * (a - next_a) ** 2
            a = next_a
            multiplier *= two
        result = (a + b) ** 2 / (four * t)
        context.prec = digits
        return +result


def theta_with_tail(coefficient: Decimal, pi: Decimal, tolerance: Decimal) -> tuple[Decimal, Decimal, int]:
    """Compute theta(a)=sum_Z exp(-pi*a*n^2) with a tail bound.

    After summing through |n| <= N, monotonicity and an integral estimate give

        omitted tail <= exp(-pi*a*N^2)/(pi*a*N).
    """
    if coefficient <= 0:
        raise ValueError("theta coefficient must be positive")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    n = 1
    while True:
        tail = (-pi * coefficient * n * n).exp() / (pi * coefficient * n)
        if tail <= tolerance:
            break
        n += 1
    value = Decimal(1)
    for index in range(1, n + 1):
        value += 2 * (-pi * coefficient * index * index).exp()
    return value, tail, n


def verify_poisson(t_text: str, modulus: int, digits: int) -> dict[str, object]:
    if modulus < 1:
        raise ValueError("modulus must be positive")
    if digits < 20:
        raise ValueError("digits must be at least 20")

    with localcontext() as context:
        context.prec = digits + 20
        t = Decimal(t_text)
        if t <= 0:
            raise ValueError("t must be positive")
        pi = gauss_legendre_pi(digits + 12)
        tolerance = Decimal(10) ** (-(digits + 2))
        m = Decimal(modulus)
        left_coefficient = t * m * m
        right_coefficient = Decimal(1) / left_coefficient
        prefactor = Decimal(1) / (m * t.sqrt())

        left, left_tail, left_terms = theta_with_tail(
            left_coefficient, pi, tolerance
        )
        right_theta, right_tail_unscaled, right_terms = theta_with_tail(
            right_coefficient, pi, tolerance / prefactor
        )
        right = prefactor * right_theta
        right_tail = prefactor * right_tail_unscaled
        residual = abs(left - right)
        combined_tail_bound = left_tail + right_tail

        display = digits
        return {
            "scope": "Gaussian times compact-open adelic test function",
            "parameters": {"t": str(t), "M": modulus, "digits": digits},
            "identity": "theta(t*M^2) = (M*sqrt(t))^-1 theta((t*M^2)^-1)",
            "left": format(left, f".{display}g"),
            "right": format(right, f".{display}g"),
            "absolute_residual": format(residual, ".8e"),
            "combined_analytic_tail_bound": format(combined_tail_bound, ".8e"),
            "left_positive_terms": left_terms,
            "right_positive_terms": right_terms,
            "note": "The symbolic Poisson proof is primary; this is a numerical verification with analytic truncation bounds.",
        }


def character_samples(values: Iterable[Fraction]) -> list[dict[str, str]]:
    return [
        {
            "q": str(q),
            "global_character_exponent": str(global_character_exponent(q)),
            "product_character": "1 exactly",
        }
        for q in values
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--t", default="0.37", help="positive decimal Gaussian scale")
    parser.add_argument("--modulus", "-M", type=int, default=6)
    parser.add_argument("--digits", type=int, default=60)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = verify_poisson(args.t, args.modulus, args.digits)
    report["global_character_samples"] = character_samples(
        [Fraction(1, 2), Fraction(5, 6), Fraction(11, 6), Fraction(-17, 60)]
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

