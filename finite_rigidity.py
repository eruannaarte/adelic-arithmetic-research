#!/usr/bin/env python3
"""Finite-order rigidity of multiplicatively additive numerical coordinates.

Let E(n) be defined by prime weights E(p), extended by E(mn)=E(m)+E(n).
We normalize E(2)=log(2) and impose E(n+1) >= E(n) for 1 <= n < N.
Linear programming then finds the smallest and largest admissible E(p).

The infinite version is a classical rigidity theorem: a monotone completely
additive arithmetic function is c*log(n).  This experiment asks how quickly
finite constraints force that limit.  SciPy is required for scipy.optimize.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import sys

import numpy as np
import scipy
from scipy.optimize import linprog
from scipy.sparse import csr_matrix


def primes_up_to(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[:2] = b"\x00\x00"
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            start = p * p
            sieve[start : limit + 1 : p] = b"\x00" * (
                ((limit - start) // p) + 1
            )
    return [n for n, is_prime in enumerate(sieve) if is_prime]


def exponent_matrix(limit: int, primes: list[int]) -> csr_matrix:
    """Rows are unique prime-exponent vectors for 1,...,limit."""
    prime_index = {p: index for index, p in enumerate(primes)}
    smallest_prime_factor = list(range(limit + 1))
    for p in primes:
        if p * p > limit:
            break
        if smallest_prime_factor[p] != p:
            continue
        for multiple in range(p * p, limit + 1, p):
            if smallest_prime_factor[multiple] == multiple:
                smallest_prime_factor[multiple] = p

    rows: list[int] = []
    columns: list[int] = []
    exponents: list[float] = []
    for n in range(2, limit + 1):
        remaining = n
        while remaining > 1:
            p = smallest_prime_factor[remaining]
            exponent = 0
            while remaining % p == 0:
                exponent += 1
                remaining //= p
            rows.append(n - 1)
            columns.append(prime_index[p])
            exponents.append(float(exponent))
    return csr_matrix(
        (exponents, (rows, columns)),
        shape=(limit, len(primes)),
        dtype=float,
    )


def solve_bounds(limit: int, target_primes: list[int]) -> dict[str, object]:
    primes = primes_up_to(limit)
    index = {p: i for i, p in enumerate(primes)}
    values = exponent_matrix(limit, primes)

    # E(n) <= E(n+1), expressed in scipy's A_ub x <= b_ub form.
    adjacent_constraints = values[:-1] - values[1:]
    upper_bounds = np.zeros(limit - 1)
    normalization = csr_matrix(
        ([1.0], ([0], [index[2]])), shape=(1, len(primes)), dtype=float
    )
    normalized_value = np.array([math.log(2.0)])
    unrestricted = [(None, None)] * len(primes)

    results: dict[str, object] = {}
    for p in target_primes:
        if p not in index:
            continue
        objective = np.zeros(len(primes))
        objective[index[p]] = 1.0
        minimum = linprog(
            objective,
            A_ub=adjacent_constraints,
            b_ub=upper_bounds,
            A_eq=normalization,
            b_eq=normalized_value,
            bounds=unrestricted,
            method="highs",
        )
        maximum = linprog(
            -objective,
            A_ub=adjacent_constraints,
            b_ub=upper_bounds,
            A_eq=normalization,
            b_eq=normalized_value,
            bounds=unrestricted,
            method="highs",
        )
        if not minimum.success or not maximum.success:
            raise RuntimeError(
                f"LP failed for p={p}: {minimum.message}; {maximum.message}"
            )
        lower = float(minimum.fun)
        upper = float(-maximum.fun)
        truth = math.log(p)
        results[str(p)] = {
            "lower": lower,
            "log_p": truth,
            "upper": upper,
            "interval_width": upper - lower,
            "relative_width": (upper - lower) / truth,
            "contains_log_p": lower - 1e-10 <= truth <= upper + 1e-10,
            "lower_witness_min_constraint_slack": float(
                np.min(minimum.ineqlin.residual)
            ),
            "upper_witness_min_constraint_slack": float(
                np.min(maximum.ineqlin.residual)
            ),
        }

    return {
        "limit": limit,
        "variables_prime_weights": len(primes),
        "adjacent_order_constraints": limit - 1,
        "bounds": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limits", type=int, nargs="+", default=[30, 100, 300, 1000, 3000]
    )
    parser.add_argument(
        "--primes", type=int, nargs="+", default=[3, 5, 7, 11, 13]
    )
    args = parser.parse_args()
    output = {
        "hypothesis_tested": (
            "Finite multiplication-additivity plus ordinary order increasingly "
            "forces the logarithmic coordinate."
        ),
        "normalization": "E(2)=log(2)",
        "non_strict_note": (
            "The LP uses the closed constraints E(n+1)>=E(n); strict monotonicity "
            "has the same infima and suprema when approached from the interior."
        ),
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "runs": [solve_bounds(limit, args.primes) for limit in args.limits],
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
