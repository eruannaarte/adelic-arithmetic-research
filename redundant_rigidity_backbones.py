#!/usr/bin/env python3
"""Minimum-mass and redundant exact rigidity backbones at cutoff 100.

The endpoint is fixed and a nonnegative LP minimizes the certificate l1 mass,
which is exactly its uniform-defect amplification. Additional solves exclude
selected comparisons to search for alternative backbones.
"""

from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction
from typing import Sequence

from exact_rigidity_certificates import (
    adjacent_row,
    combine_certificate,
    solve_unique_rational_system,
    verify_certificate,
)


# Exact feasible dual points for the cutoff-100 l1 programs.  If z is such a
# point, <a_n,z> <= 1 for every adjacent-comparison row a_n, so weak duality
# gives <target,z> <= sum_n y_n for every nonnegative certificate y.
MINIMUM_MASS_DUALS: dict[str, dict[int, Fraction]] = {
    "lower": {
        2: Fraction(1, 6),
        3: Fraction(-1, 6),
        5: Fraction(-1, 3),
        13: Fraction(1, 3),
        37: Fraction(-1),
        41: Fraction(1),
        53: Fraction(-1, 3),
        59: Fraction(-5, 6),
        61: Fraction(7, 6),
        67: Fraction(4, 3),
        71: Fraction(7, 6),
        73: Fraction(-5, 6),
        79: Fraction(4, 3),
        83: Fraction(1, 6),
        89: Fraction(-1, 2),
        97: Fraction(-1, 3),
    },
    "upper": {
        2: Fraction(-1, 5),
        3: Fraction(2, 25),
        7: Fraction(-9, 25),
        37: Fraction(-31, 25),
        41: Fraction(13, 25),
        53: Fraction(-7, 5),
        59: Fraction(-6, 5),
        61: Fraction(4, 5),
        67: Fraction(3, 5),
        71: Fraction(14, 25),
        73: Fraction(-36, 25),
        79: Fraction(1, 5),
        83: Fraction(-17, 25),
        89: Fraction(-8, 5),
        97: Fraction(-48, 25),
    },
}


# A Farkas separator for the lower target after comparison n=80 is deleted.
# It has <a_n,z> <= 0 on every remaining cutoff-100 row, while its pairing
# with (11/7)e_2-e_3 is 1.  Hence that target cannot lie in the remaining
# nonnegative comparison cone.
N80_FARKAS_WITNESS = {
    prime: Fraction(value)
    for prime, value in {
        2: 161,
        3: 252,
        5: 371,
        7: 448,
        11: 553,
        13: 595,
        17: 651,
        19: 679,
        23: 721,
        29: 770,
        31: 791,
        37: 826,
        41: 861,
        43: 861,
        47: 882,
        53: 917,
        59: 931,
        61: 952,
        67: 973,
        71: 987,
        73: 987,
        79: 1015,
        83: 1022,
        89: 1036,
        97: 1057,
    }.items()
}


def row_pairing(row: dict[int, int], witness: dict[int, Fraction]) -> Fraction:
    return sum(
        (Fraction(exponent) * witness.get(prime, Fraction()))
        for prime, exponent in row.items()
    )


def target_pairing(
    direction: str, endpoint: Fraction, witness: dict[int, Fraction]
) -> Fraction:
    if direction == "lower":
        return endpoint * witness.get(2, Fraction()) - witness.get(3, Fraction())
    if direction == "upper":
        return witness.get(3, Fraction()) - endpoint * witness.get(2, Fraction())
    raise ValueError("direction must be lower or upper")


def verify_minimum_mass(
    limit: int,
    direction: str,
    endpoint: Fraction,
    entries: Sequence[tuple[int, Fraction]],
) -> Fraction:
    """Prove optimality by exact primal/dual equality."""
    if limit != 100 or direction not in MINIMUM_MASS_DUALS:
        raise ValueError("an exact dual witness is stored only for cutoff 100")
    verify_certificate(3, direction, endpoint, entries)
    witness = MINIMUM_MASS_DUALS[direction]
    if any(row_pairing(adjacent_row(n), witness) > 1 for n in range(1, limit)):
        raise AssertionError("stored dual witness is infeasible")
    dual_value = target_pairing(direction, endpoint, witness)
    if mass(entries) != dual_value:
        raise AssertionError("primal and dual objectives do not agree")
    return dual_value


def verify_n80_obstruction() -> Fraction:
    """Prove exactly that n=80 is required for the cutoff-100 lower target."""
    if any(
        row_pairing(adjacent_row(n), N80_FARKAS_WITNESS) > 0
        for n in range(1, 100)
        if n != 80
    ):
        raise AssertionError("stored Farkas witness does not separate the cone")
    separated_value = target_pairing(
        "lower", Fraction(11, 7), N80_FARKAS_WITNESS
    )
    if separated_value <= 0:
        raise AssertionError("stored Farkas witness does not separate the target")
    return separated_value


def optimize_certificate(
    limit: int,
    direction: str,
    endpoint: Fraction,
    excluded: set[int] | None = None,
) -> list[tuple[int, Fraction]] | None:
    try:
        import numpy as np
        from scipy.optimize import linprog

        from finite_rigidity import exponent_matrix, primes_up_to
    except ImportError as error:
        raise RuntimeError("NumPy and SciPy are required") from error

    excluded = set() if excluded is None else excluded
    primes = primes_up_to(limit)
    prime_index = {prime: index for index, prime in enumerate(primes)}
    values = exponent_matrix(limit, primes)
    transpose = (values[:-1] - values[1:]).T.tocsr()
    target = np.zeros(len(primes))
    target[prime_index[3]] = -1.0 if direction == "lower" else 1.0
    target[prime_index[2]] = float(endpoint if direction == "lower" else -endpoint)
    result = linprog(
        np.ones(limit - 1),
        A_eq=transpose,
        b_eq=target,
        bounds=[
            (0.0, 0.0) if n in excluded else (0.0, None)
            for n in range(1, limit)
        ],
        method="highs",
    )
    if not result.success:
        return None
    support_rows = [index for index, value in enumerate(result.x) if value > 1e-9]
    rows = [adjacent_row(index + 1) for index in support_rows]
    coefficients = [
        [row.get(prime, 0) for row in rows] for prime in primes
    ]
    exact_target = [Fraction() for _ in primes]
    exact_target[prime_index[3]] = Fraction(-1 if direction == "lower" else 1)
    exact_target[prime_index[2]] = endpoint if direction == "lower" else -endpoint
    multipliers = solve_unique_rational_system(coefficients, exact_target)
    entries = [
        (index + 1, multiplier)
        for index, multiplier in zip(support_rows, multipliers)
        if multiplier
    ]
    if any(multiplier < 0 for _, multiplier in entries):
        raise AssertionError("exact reconstruction made a multiplier negative")
    verify_certificate(3, direction, endpoint, entries)
    return entries


def mass(entries: Sequence[tuple[int, Fraction]]) -> Fraction:
    return sum((multiplier for _, multiplier in entries), Fraction())


def serialize(entries: Sequence[tuple[int, Fraction]]) -> list[dict[str, object]]:
    return [
        {"n": n, "inequality": f"E({n})<=E({n + 1})", "multiplier": str(multiplier)}
        for n, multiplier in entries
    ]


def availability_probability(
    lower_supports: Sequence[set[int]],
    upper_supports: Sequence[set[int]],
    observation_probability: float,
) -> float:
    universe = sorted(set().union(*lower_supports, *upper_supports))
    result = 0.0
    for flags in itertools.product([False, True], repeat=len(universe)):
        observed = {edge for edge, flag in zip(universe, flags) if flag}
        if not any(support <= observed for support in lower_supports):
            continue
        if not any(support <= observed for support in upper_supports):
            continue
        count = len(observed)
        result += observation_probability**count * (
            1.0 - observation_probability
        ) ** (len(universe) - count)
    return result


def analyze() -> dict[str, object]:
    limit = 100
    lower_endpoint = Fraction(11, 7)
    upper_endpoint = Fraction(8, 5)
    lower_primary = optimize_certificate(limit, "lower", lower_endpoint)
    upper_primary = optimize_certificate(limit, "upper", upper_endpoint)
    assert lower_primary is not None and upper_primary is not None
    lower_alternative = optimize_certificate(limit, "lower", lower_endpoint, {26})
    upper_alternative = optimize_certificate(
        limit, "upper", upper_endpoint, {n for n, _ in upper_primary}
    )
    assert lower_alternative is not None and upper_alternative is not None
    lower_without_critical = optimize_certificate(limit, "lower", lower_endpoint, {80})
    lower_optimum = verify_minimum_mass(
        limit, "lower", lower_endpoint, lower_primary
    )
    upper_optimum = verify_minimum_mass(
        limit, "upper", upper_endpoint, upper_primary
    )
    n80_separation = verify_n80_obstruction()

    lower_supports = [
        {n for n, _ in lower_primary},
        {n for n, _ in lower_alternative},
    ]
    upper_supports = [
        {n for n, _ in upper_primary},
        {n for n, _ in upper_alternative},
    ]
    loose_backup = [(8, Fraction(1, 2))]
    verify_certificate(3, "lower", Fraction(3, 2), loose_backup)
    return {
        "limit": limit,
        "sharp_interval": [str(lower_endpoint), str(upper_endpoint)],
        "minimum_mass_lower": {
            "entries": serialize(lower_primary),
            "mass": str(mass(lower_primary)),
            "previous_extracted_mass": "5/7",
            "mass_reduction_fraction": "2/5",
            "exact_dual_optimum": str(lower_optimum),
        },
        "alternative_sharp_lower": {
            "entries": serialize(lower_alternative),
            "mass": str(mass(lower_alternative)),
        },
        "critical_lower_comparisons": sorted(set.intersection(*lower_supports)),
        "sharp_lower_feasible_without_n80": lower_without_critical is not None,
        "exact_n80_farkas_separation": str(n80_separation),
        "looser_disjoint_lower_backup": {
            "endpoint": "3/2",
            "entries": serialize(loose_backup),
        },
        "minimum_mass_upper": {
            "entries": serialize(upper_primary),
            "mass": str(mass(upper_primary)),
            "exact_dual_optimum": str(upper_optimum),
        },
        "edge_disjoint_sharp_upper": {
            "entries": serialize(upper_alternative),
            "mass": str(mass(upper_alternative)),
        },
        "redundant_exact_pair_availability": [
            {
                "per_comparison_observation_probability": probability,
                "primary_pair_only": probability
                ** (len(lower_supports[0]) + len(upper_supports[0])),
                "with_discovered_alternatives": availability_probability(
                    lower_supports, upper_supports, probability
                ),
            }
            for probability in [0.8, 0.9, 0.95, 0.99]
        ],
        "interpretation": (
            "l1 minimization reduces adversarial defect amplification; "
            "alternative supports improve missing-edge survival, but n=80 is "
            "unavoidable for the sharp lower endpoint at this cutoff"
        ),
    }


def parse_args() -> argparse.Namespace:
    return argparse.ArgumentParser(description=__doc__).parse_args()


def main() -> None:
    parse_args()
    print(json.dumps(analyze(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
