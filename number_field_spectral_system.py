#!/usr/bin/env python3
"""Prime-ideal Fock factors for the two Stage 4 quadratic fields.

Each prime ideal P is a bosonic mode of energy log N(P).  Splitting therefore
creates multiple modes, inertia multiplies the energy by the residue degree,
and ramification affects the relation with (p) but not the number of local
Dedekind-zeta factors.
"""

from __future__ import annotations

import argparse
import cmath
import json
import math
from fractions import Fraction
from typing import Sequence

from quadratic_adelic_geometry import GAUSSIAN, GOLDEN, QuadraticField, is_prime


def validate_rational_primes(primes: Sequence[int]) -> None:
    if len(set(primes)) != len(primes) or not all(is_prime(prime) for prime in primes):
        raise ValueError("a distinct list of rational primes is required")


def local_prime_ideal_factor(field: QuadraticField, prime: int, s: complex) -> complex:
    if s.real <= 0:
        raise ValueError("finite prime-ideal heat traces need Re(s)>0")
    result = 1.0 + 0.0j
    for prime_ideal in field.primes_above(prime):
        result /= 1.0 - cmath.exp(-s * math.log(prime_ideal.norm))
    return result


def exact_local_prime_ideal_factor(
    field: QuadraticField, prime: int, integer_s: int
) -> Fraction:
    if integer_s <= 0:
        raise ValueError("integer_s must be positive")
    result = Fraction(1)
    for prime_ideal in field.primes_above(prime):
        norm_power = prime_ideal.norm**integer_s
        result *= Fraction(norm_power, norm_power - 1)
    return result


def finite_prime_ideal_partition(
    field: QuadraticField, rational_primes: Sequence[int], s: complex
) -> complex:
    validate_rational_primes(rational_primes)
    result = 1.0 + 0.0j
    for prime in rational_primes:
        result *= local_prime_ideal_factor(field, prime, s)
    return result


def splitting_mode_report(
    field: QuadraticField, rational_primes: Sequence[int], sigma: float
) -> list[dict[str, object]]:
    report = []
    for prime in rational_primes:
        ideals = field.primes_above(prime)
        report.append(
            {
                "rational_prime": prime,
                "behavior": ideals[0].behavior,
                "mode_count": len(ideals),
                "modes": [
                    {
                        "prime_ideal": ideal.label,
                        "residue_degree": ideal.residue_degree,
                        "ramification_index": ideal.ramification_index,
                        "norm": ideal.norm,
                        "energy": math.log(ideal.norm),
                    }
                    for ideal in ideals
                ],
                "local_partition": local_prime_ideal_factor(
                    field, prime, complex(sigma)
                ).real,
                "exact_local_partition": str(
                    exact_local_prime_ideal_factor(field, prime, int(sigma))
                )
                if sigma.is_integer()
                else None,
            }
        )
    return report


def analyze(rational_primes: Sequence[int], sigma: float) -> dict[str, object]:
    validate_rational_primes(rational_primes)
    return {
        field.name: {
            "signature": [field.real_places, field.complex_places],
            "finite_prime_ideal_partition": finite_prime_ideal_partition(
                field, rational_primes, complex(sigma)
            ).real,
            "rational_local_factors": splitting_mode_report(
                field, rational_primes, sigma
            ),
        }
        for field in (GAUSSIAN, GOLDEN)
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primes", nargs="+", type=int, default=[2, 3, 5, 7, 11])
    parser.add_argument("--sigma", type=float, default=2.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(json.dumps(analyze(args.primes, args.sigma), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
