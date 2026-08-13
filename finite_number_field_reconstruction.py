#!/usr/bin/env python3
"""Finite-height reconstruction experiments for the Stage 4 quadratic fields.

For every nonzero alpha=a+b*omega in a coefficient box, form its product-
formula row

    (log |sigma_v(alpha)|)_v, (-ord_P(alpha) log N(P))_P.

The unknowns are hypothetical local calibration scales.  Every row annihilates
the common-scale vector.  Thus nullity one means that the sampled principal-
element relations already force all *active* places to have one common scale.

Ideal factorization is exact.  Floating point enters only in Archimedean logs
and numerical rank, whose tolerance stability is explicitly audited.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from typing import Iterable, Sequence

from quadratic_adelic_geometry import (
    GAUSSIAN,
    GOLDEN,
    PrimeIdeal,
    QuadraticField,
    QuadraticInteger,
    archimedean_logs,
    matrix_rank,
)


def element_key(alpha: QuadraticInteger) -> tuple[int, int, int, int]:
    return max(abs(alpha.a), abs(alpha.b)), abs(alpha.norm), alpha.a, alpha.b


def elements_in_box(field: QuadraticField, bound: int) -> list[QuadraticInteger]:
    """One representative of each pair {alpha,-alpha} with H_coeff<=bound."""
    if bound < 1:
        raise ValueError("bound must be positive")
    result = []
    for a in range(-bound, bound + 1):
        for b in range(-bound, bound + 1):
            if a < 0 or (a == 0 and b <= 0):
                continue
            result.append(field.element(a, b))
    return sorted(result, key=element_key)


def prime_key(prime: PrimeIdeal) -> tuple[int, int]:
    return prime.rational_prime, -1 if prime.root is None else prime.root


@dataclass(frozen=True)
class RelationData:
    alpha: QuadraticInteger
    arch_logs: tuple[float, ...]
    factors: tuple[tuple[PrimeIdeal, int], ...]


def relation_data(elements: Iterable[QuadraticInteger]) -> list[RelationData]:
    return [
        RelationData(
            alpha,
            tuple(archimedean_logs(alpha)),
            tuple(alpha.field.factor_principal(alpha)),
        )
        for alpha in elements
    ]


def active_primes(relations: Sequence[RelationData]) -> list[PrimeIdeal]:
    return sorted(
        {prime for relation in relations for prime, _ in relation.factors},
        key=prime_key,
    )


def row_for(relation: RelationData, primes: Sequence[PrimeIdeal]) -> list[float]:
    factor_map = {prime: exponent for prime, exponent in relation.factors}
    return [*relation.arch_logs] + [
        -factor_map.get(prime, 0) * math.log(prime.norm) for prime in primes
    ]


def stable_rank(rows: Sequence[Sequence[float]]) -> tuple[int, dict[str, int]]:
    ranks = {
        "1e-09": matrix_rank(rows, 1e-9),
        "1e-10": matrix_rank(rows, 1e-10),
        "1e-11": matrix_rank(rows, 1e-11),
        "1e-12": matrix_rank(rows, 1e-12),
    }
    if len(set(ranks.values())) != 1:
        raise AssertionError(f"rank was not tolerance-stable: {ranks}")
    return next(iter(ranks.values())), ranks


def greedy_rank_witnesses(
    relations: Sequence[RelationData], primes: Sequence[PrimeIdeal]
) -> tuple[list[RelationData], int]:
    chosen: list[RelationData] = []
    rows: list[list[float]] = []
    rank = 0
    for relation in relations:
        candidate = row_for(relation, primes)
        next_rank = matrix_rank([*rows, candidate], 1e-11)
        if next_rank > rank:
            chosen.append(relation)
            rows.append(candidate)
            rank = next_rank
    return chosen, rank


def field_snapshot(field: QuadraticField, bound: int) -> dict[str, object]:
    relations = relation_data(elements_in_box(field, bound))
    primes = active_primes(relations)
    rows = [row_for(relation, primes) for relation in relations]
    column_count = field.real_places + field.complex_places + len(primes)
    rank, tolerance_audit = stable_rank(rows)
    witnesses, witness_rank = greedy_rank_witnesses(relations, primes)
    if witness_rank != rank:
        raise AssertionError("greedy witnesses did not span the sampled row space")

    rational_rows = [
        row_for(relation, primes) for relation in relations if relation.alpha.b == 0
    ]
    rational_rank, rational_tolerance_audit = stable_rank(rational_rows)
    maximum_residual = max(abs(sum(row)) for row in rows)
    common_scale_residual = max(
        abs(sum(row)) / max(1.0, max(map(abs, row))) for row in rows
    )

    return {
        "coefficient_height_bound": bound,
        "sampled_elements_modulo_sign": len(relations),
        "archimedean_places": field.real_places + field.complex_places,
        "active_finite_places": len(primes),
        "active_place_labels": [
            *[
                f"arch_{index + 1}"
                for index in range(field.real_places + field.complex_places)
            ],
            *[prime.label for prime in primes],
        ],
        "rank": rank,
        "nullity": column_count - rank,
        "rank_tolerance_audit": tolerance_audit,
        "maximum_product_formula_residual": maximum_residual,
        "maximum_scaled_product_formula_residual": common_scale_residual,
        "greedy_spanning_witness_count": len(witnesses),
        "greedy_spanning_witnesses": [
            {
                "element": str(relation.alpha),
                "coordinates": [relation.alpha.a, relation.alpha.b],
                "norm": relation.alpha.norm,
                "prime_support": [prime.label for prime, _ in relation.factors],
            }
            for relation in witnesses
        ],
        "rational_integer_only_rank": rational_rank,
        "rational_integer_only_nullity_on_same_places": column_count - rational_rank,
        "rational_integer_rank_tolerance_audit": rational_tolerance_audit,
    }


def analyze(bounds: Sequence[int]) -> dict[str, object]:
    return {
        "method": (
            "finite principal-element product-formula rows; active finite places "
            "are exactly those occurring in the sampled factorizations"
        ),
        "interpretation": (
            "nullity one means the sampled data synchronize every active local "
            "calibration up to one common scale"
        ),
        "warning": (
            "rank is a tolerance-audited numerical statement about exact ideal "
            "factorizations and floating Archimedean logarithms, not an exact "
            "symbolic rank proof"
        ),
        "fields": {
            field.name: [field_snapshot(field, bound) for bound in bounds]
            for field in (GAUSSIAN, GOLDEN)
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bounds", nargs="+", type=int, default=[1, 2, 3, 4, 6, 8])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(json.dumps(analyze(args.bounds), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
