#!/usr/bin/env python3
"""Finite checks for the logarithmic valuation geometry of positive rationals.

This is an illustration of exact propositions proved in
LOCAL_GLOBAL_ADELIC_CALIBRATION.md. Floating-point output is not used as proof.
The script deliberately studies the log-valuation skeleton, not the full adele
ring.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from fractions import Fraction
from typing import Iterable, Sequence


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def validate_primes(primes: Sequence[int]) -> None:
    if not primes:
        raise ValueError("at least one prime is required")
    if len(set(primes)) != len(primes):
        raise ValueError("primes must be distinct")
    if not all(is_prime(p) for p in primes):
        raise ValueError("all generators must be prime")


def rational_from_exponents(primes: Sequence[int], exponents: Sequence[int]) -> Fraction:
    value = Fraction(1, 1)
    for prime, exponent in zip(primes, exponents):
        if exponent >= 0:
            value *= prime**exponent
        else:
            value /= prime ** (-exponent)
    return value


def log_embedding(primes: Sequence[int], exponents: Sequence[int]) -> list[float]:
    """Return (log|q|_infinity, log|q|_p for p in primes)."""
    finite_coordinates = [
        -exponent * math.log(prime)
        for prime, exponent in zip(primes, exponents)
    ]
    infinite_coordinate = -sum(finite_coordinates)
    return [infinite_coordinate, *finite_coordinates]


def prime_basis(primes: Sequence[int]) -> list[list[float]]:
    basis: list[list[float]] = []
    for index, prime in enumerate(primes):
        vector = [0.0] * (len(primes) + 1)
        vector[0] = math.log(prime)
        vector[index + 1] = -math.log(prime)
        basis.append(vector)
    return basis


def dot(x: Sequence[float], y: Sequence[float]) -> float:
    return sum(a * b for a, b in zip(x, y))


def gram_matrix(vectors: Sequence[Sequence[float]]) -> list[list[float]]:
    return [[dot(x, y) for y in vectors] for x in vectors]


def determinant(matrix: Sequence[Sequence[float]]) -> float:
    work = [list(row) for row in matrix]
    size = len(work)
    result = 1.0
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(work[row][column]))
        if abs(work[pivot][column]) < 1e-15:
            return 0.0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result *= -1.0
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, size):
            factor = work[row][column] / pivot_value
            for entry in range(column + 1, size):
                work[row][entry] -= factor * work[column][entry]
    return result


def pairwise_angles_degrees(vectors: Sequence[Sequence[float]]) -> list[float]:
    angles: list[float] = []
    for left, right in itertools.combinations(vectors, 2):
        cosine = dot(left, right) / math.sqrt(dot(left, left) * dot(right, right))
        cosine = max(-1.0, min(1.0, cosine))
        angles.append(math.degrees(math.acos(cosine)))
    return angles


def exponent_samples(dimension: int, bound: int) -> Iterable[tuple[int, ...]]:
    return itertools.product(range(-bound, bound + 1), repeat=dimension)


def analyze(primes: Sequence[int], bound: int) -> dict[str, object]:
    validate_primes(primes)
    if bound < 1:
        raise ValueError("bound must be positive")

    basis = prime_basis(primes)
    gram = gram_matrix(basis)
    numeric_determinant = determinant(gram)
    formula_determinant = (len(primes) + 1) * math.prod(
        math.log(prime) ** 2 for prime in primes
    )

    max_product_formula_residual = 0.0
    rationals: set[Fraction] = set()
    closest_nontrivial: dict[str, object] | None = None
    sample_count = 0

    for exponents in exponent_samples(len(primes), bound):
        sample_count += 1
        coordinates = log_embedding(primes, exponents)
        max_product_formula_residual = max(
            max_product_formula_residual, abs(sum(coordinates))
        )
        rational = rational_from_exponents(primes, exponents)
        rationals.add(rational)
        if any(exponents):
            archimedean_size = abs(coordinates[0])
            if closest_nontrivial is None or archimedean_size < closest_nontrivial["absolute_log"]:
                closest_nontrivial = {
                    "exponents": list(exponents),
                    "rational": str(rational),
                    "absolute_log": archimedean_size,
                }

    if len(rationals) != sample_count:
        raise AssertionError("prime-exponent embedding was not injective")

    angles = pairwise_angles_degrees(basis)
    determinant_relative_error = abs(numeric_determinant - formula_determinant) / formula_determinant

    if max_product_formula_residual > 1e-12:
        raise AssertionError("product-formula residual exceeded tolerance")
    if angles and max(abs(angle - 60.0) for angle in angles) > 1e-12:
        raise AssertionError("prime-direction angle identity failed")
    if determinant_relative_error > 1e-12:
        raise AssertionError("Gram determinant identity failed")

    places = ["infinity", *(str(prime) for prime in primes)]
    return {
        "scope": "logarithmic valuation skeleton; not the full adele ring",
        "primes": list(primes),
        "places": places,
        "exponent_bound": bound,
        "sample_count": sample_count,
        "unique_rational_count": len(rationals),
        "maximum_product_formula_residual": max_product_formula_residual,
        "prime_basis_vectors": basis,
        "gram_matrix": gram,
        "pairwise_angles_degrees": angles,
        "gram_determinant_numeric": numeric_determinant,
        "gram_determinant_formula": formula_determinant,
        "gram_determinant_relative_error": determinant_relative_error,
        "fundamental_covolume": math.sqrt(formula_determinant),
        "closest_nontrivial_sample_to_one": closest_nontrivial,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primes", nargs="+", type=int, default=[2, 3, 5])
    parser.add_argument("--bound", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(json.dumps(analyze(args.primes, args.bound), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

