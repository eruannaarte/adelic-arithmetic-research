#!/usr/bin/env python3
"""Exact class-group and principal-divisor lattice for Q(sqrt(-5)).

The selected prime ideals above 2 and 3 are all nonprincipal.  Principal
divisors supported on them form an index-two sublattice with Smith invariants
(1,1,2), making the class obstruction visible in finite integer data.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from functools import reduce
from typing import Sequence

from quadratic_adelic_geometry import QuadraticField, minkowski_bound


NEGATIVE_FIVE = QuadraticField("Q(sqrt(-5))", "sqrt(-5)", 0, 5, 0, 1)


def integer_determinant(matrix: Sequence[Sequence[int]]) -> int:
    size = len(matrix)
    if size == 0:
        return 1
    if any(len(row) != size for row in matrix):
        raise ValueError("determinant needs a square matrix")
    if size == 1:
        return matrix[0][0]
    return sum(
        (-1) ** column
        * matrix[0][column]
        * integer_determinant(
            [row[:column] + row[column + 1 :] for row in matrix[1:]]
        )
        for column in range(size)
    )


def determinantal_divisor(matrix: Sequence[Sequence[int]], size: int) -> int:
    if size == 0:
        return 1
    row_count = len(matrix)
    column_count = len(matrix[0]) if matrix else 0
    minors = []
    for rows in itertools.combinations(range(row_count), size):
        for columns in itertools.combinations(range(column_count), size):
            minor = [[matrix[row][column] for column in columns] for row in rows]
            minors.append(abs(integer_determinant(minor)))
    return reduce(math.gcd, minors, 0)


def smith_invariants_full_column_rank(
    matrix: Sequence[Sequence[int]], column_count: int
) -> list[int]:
    deltas = [determinantal_divisor(matrix, size) for size in range(column_count + 1)]
    if deltas[-1] == 0:
        raise ValueError("matrix does not have full column rank")
    return [deltas[index] // deltas[index - 1] for index in range(1, len(deltas))]


def selected_prime_ideals():
    p2 = NEGATIVE_FIVE.primes_above(2)[0]
    p3 = NEGATIVE_FIVE.primes_above(3)
    return [p2, *p3]


def divisor_vector(element, primes) -> list[int]:
    factors = NEGATIVE_FIVE.factor_principal(element)
    factor_map = {prime.ideal: exponent for prime, exponent in factors}
    if any(prime not in primes for prime, _ in factors):
        raise ValueError("element has divisor support outside the selected primes")
    return [factor_map.get(prime.ideal, 0) for prime in primes]


def analyze() -> dict[str, object]:
    primes = selected_prime_ideals()
    elements = [
        NEGATIVE_FIVE.element(2),
        NEGATIVE_FIVE.element(3),
        NEGATIVE_FIVE.element(1, 1),
        NEGATIVE_FIVE.element(1, -1),
    ]
    relation_matrix = [divisor_vector(element, primes) for element in elements]
    invariants = smith_invariants_full_column_rank(relation_matrix, len(primes))
    p2 = primes[0]
    if p2.ideal**2 != NEGATIVE_FIVE.principal_ideal(NEGATIVE_FIVE.element(2)):
        raise AssertionError("the prime above 2 did not square to (2)")
    return {
        "field": NEGATIVE_FIVE.name,
        "integral_basis": "1,sqrt(-5)",
        "discriminant": NEGATIVE_FIVE.discriminant,
        "minkowski_bound": str(minkowski_bound(NEGATIVE_FIVE)),
        "class_number_proof": [
            "every ideal class has an integral ideal of norm at most 2sqrt(20)/pi<3",
            "the only possible nontrivial class is represented by the unique prime ideal P2 of norm 2",
            "P2 is nonprincipal because a^2+5b^2=2 has no integer solution",
            "P2^2=(2), so P2 has class order 2 and the class number is exactly 2",
        ],
        "selected_prime_ideals": [
            {"label": prime.label, "norm": prime.norm, "basis": prime.ideal.basis}
            for prime in primes
        ],
        "principal_elements": [str(element) for element in elements],
        "principal_divisor_matrix": relation_matrix,
        "smith_invariants": invariants,
        "principal_lattice_index": math.prod(invariants),
        "quotient": "Z/2Z",
        "parity_description": (
            "the principal divisor vectors are exactly the triples with even coordinate sum"
        ),
        "isolated_prime_delay": (
            "a principal divisor supported only at P2 has even exponent; exponent 2 is first, via (2)=P2^2"
        ),
    }


def parse_args() -> argparse.Namespace:
    return argparse.ArgumentParser(description=__doc__).parse_args()


def main() -> None:
    parse_args()
    print(json.dumps(analyze(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
