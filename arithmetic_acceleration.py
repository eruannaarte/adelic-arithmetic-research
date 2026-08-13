#!/usr/bin/env python3
"""Compare two-prime Diophantine rigidity with the full adjacent-integer LP.

The full bounds are exact rational dual certificates reconstructed from a
floating-point-selected sparse support.  Run with the SciPy-enabled Python
environment described in exact_rigidity_certificates.py.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction

from exact_rigidity_certificates import extract
from two_prime_rigidity import exact_interval, serialize_fraction


def comparison(limit: int, target_prime: int = 3) -> dict[str, object]:
    if target_prime != 3:
        raise NotImplementedError("the two-prime comparison currently uses generators 2 and 3")
    two_prime = exact_interval(limit)
    certified = extract(limit, target_prime, 10**12)
    lower = Fraction(certified["certificates"][0]["endpoint"])
    upper = Fraction(certified["certificates"][1]["endpoint"])
    full_width = upper - lower
    two_prime_width = two_prime["width"]
    assert isinstance(two_prime_width, Fraction)
    return {
        "limit": limit,
        "two_prime_interval": [
            serialize_fraction(two_prime["lower"]),
            serialize_fraction(two_prime["upper"]),
        ],
        "two_prime_width": serialize_fraction(two_prime_width),
        "full_certified_interval": [
            serialize_fraction(lower),
            serialize_fraction(upper),
        ],
        "full_certified_width": serialize_fraction(full_width),
        "full_certified_width_decimal": float(full_width),
        "two_prime_to_full_width_ratio": float(two_prime_width / full_width),
        "limit_times_full_width": float(limit * full_width),
        "dual_support_sizes": [
            certificate["support_size"] for certificate in certified["certificates"]
        ],
    }


def analyze(limits: list[int]) -> dict[str, object]:
    return {
        "normalization": "E(2)=1; target E(3)",
        "two_prime_layer": "all order relations among 3-smooth numbers through the cutoff",
        "full_layer": "all adjacent inequalities E(n)<=E(n+1) through the cutoff",
        "proof_status": (
            "every displayed full bound has an exactly verified nonnegative "
            "rational dual certificate; numerical optimization is used only "
            "to locate its sparse support"
        ),
        "runs": [comparison(limit) for limit in limits],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--limits", nargs="+", type=int, default=[30, 100, 300, 1_000, 3_000, 10_000]
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(json.dumps(analyze(args.limits), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
