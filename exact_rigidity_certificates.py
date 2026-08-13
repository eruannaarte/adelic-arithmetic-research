#!/usr/bin/env python3
"""Extract exact rational dual certificates from the finite-rigidity LP.

Run this with an environment containing NumPy and SciPy, for example:

    python exact_rigidity_certificates.py

Each certificate is verified again with fractions and integer prime-exponent
vectors. The final proof does not depend on floating-point feasibility.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction


def factorization(n: int) -> dict[int, int]:
    factors: dict[int, int] = {}
    divisor = 2
    while divisor * divisor <= n:
        while n % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            n //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def adjacent_row(n: int) -> dict[int, int]:
    row = factorization(n)
    for prime, exponent in factorization(n + 1).items():
        row[prime] = row.get(prime, 0) - exponent
        if row[prime] == 0:
            del row[prime]
    return row


def combine_certificate(entries: list[tuple[int, Fraction]]) -> dict[int, Fraction]:
    combined: dict[int, Fraction] = {}
    for n, multiplier in entries:
        if multiplier < 0:
            raise ValueError("certificate multipliers must be nonnegative")
        for prime, coefficient in adjacent_row(n).items():
            combined[prime] = combined.get(prime, Fraction()) + multiplier * coefficient
            if combined[prime] == 0:
                del combined[prime]
    return combined


def solve_unique_rational_system(
    coefficients: list[list[int]], right_hand_side: list[int]
) -> list[Fraction]:
    """Solve an overdetermined exact system, rejecting free variables.

    HiGHS normally returns a sparse basic dual solution. Its support identifies
    the adjacent inequalities, but independently rationalizing the floating
    multipliers is fragile at large cutoffs. Once the support is known, recover
    the multipliers from the integer prime-exponent equations themselves.
    """
    if len(coefficients) != len(right_hand_side):
        raise ValueError("row and right-hand-side counts differ")
    variable_count = len(coefficients[0]) if coefficients else 0
    work = [
        [*(Fraction(value) for value in row), Fraction(rhs)]
        for row, rhs in zip(coefficients, right_hand_side)
    ]
    pivot_for_column: dict[int, int] = {}
    pivot_row = 0
    for column in range(variable_count):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [value / pivot_value for value in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                value - factor * pivot_entry
                for value, pivot_entry in zip(work[row], work[pivot_row])
            ]
        pivot_for_column[column] = pivot_row
        pivot_row += 1
        if pivot_row == len(work):
            break

    for row in work:
        if not any(row[:variable_count]) and row[-1]:
            raise AssertionError("the floating dual support is exactly inconsistent")
    if len(pivot_for_column) != variable_count:
        raise AssertionError("the floating dual support does not determine a unique exact solution")
    return [work[pivot_for_column[column]][-1] for column in range(variable_count)]


def recover_exact_entries(
    support_rows: list[int], target_prime: int, direction: str
) -> list[tuple[int, Fraction]]:
    adjacent = [adjacent_row(row_index + 1) for row_index in support_rows]
    equation_primes = sorted(
        {prime for row in adjacent for prime in row if prime != 2}
    )
    target_coefficient = -1 if direction == "lower" else 1
    coefficients = [
        [row.get(prime, 0) for row in adjacent] for prime in equation_primes
    ]
    right_hand_side = [
        target_coefficient if prime == target_prime else 0
        for prime in equation_primes
    ]
    multipliers = solve_unique_rational_system(coefficients, right_hand_side)
    if any(multiplier < 0 for multiplier in multipliers):
        raise AssertionError("exact recovery made a dual multiplier negative")
    return [
        (row_index + 1, multiplier)
        for row_index, multiplier in zip(support_rows, multipliers)
        if multiplier
    ]


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def verify_certificate(
    target_prime: int,
    direction: str,
    endpoint: Fraction,
    entries: list[tuple[int, Fraction]],
) -> dict[str, object]:
    combined = combine_certificate(entries)
    if direction == "lower":
        expected = {2: endpoint, target_prime: Fraction(-1)}
        implication = f"E({target_prime}) >= {fraction_text(endpoint)} E(2)"
    elif direction == "upper":
        expected = {2: -endpoint, target_prime: Fraction(1)}
        implication = f"E({target_prime}) <= {fraction_text(endpoint)} E(2)"
    else:
        raise ValueError("direction must be lower or upper")
    if combined != expected:
        raise AssertionError(f"invalid certificate: got {combined}, expected {expected}")
    return {
        "direction": direction,
        "endpoint": fraction_text(endpoint),
        "decimal": float(endpoint),
        "support_size": len(entries),
        "implication": implication,
        "exact_combination": {str(prime): fraction_text(value) for prime, value in sorted(combined.items())},
        "entries": [
            {
                "n": n,
                "inequality": f"E({n}) <= E({n + 1})",
                "multiplier": fraction_text(multiplier),
            }
            for n, multiplier in entries
        ],
        "verified_with_exact_rational_arithmetic": True,
    }


def extract(limit: int, target_prime: int, max_denominator: int) -> dict[str, object]:
    try:
        import numpy as np
        from scipy.optimize import linprog
        from scipy.sparse import csr_matrix

        import finite_rigidity as finite
    except ImportError as error:
        raise RuntimeError("NumPy and SciPy are required for extraction") from error

    primes = finite.primes_up_to(limit)
    index = {prime: column for column, prime in enumerate(primes)}
    if target_prime not in index:
        raise ValueError("target prime exceeds cutoff")
    values = finite.exponent_matrix(limit, primes)
    constraints = values[:-1] - values[1:]
    equality = csr_matrix(
        ([1.0], ([0], [index[2]])), shape=(1, len(primes)), dtype=float
    )
    variable_bounds = [(None, None)] * len(primes)

    certificates: list[dict[str, object]] = []
    for direction, objective_sign in [("lower", 1.0), ("upper", -1.0)]:
        objective = np.zeros(len(primes))
        objective[index[target_prime]] = objective_sign
        result = linprog(
            objective,
            A_ub=constraints,
            b_ub=np.zeros(limit - 1),
            A_eq=equality,
            b_eq=np.ones(1),
            bounds=variable_bounds,
            method="highs",
        )
        if not result.success:
            raise RuntimeError(result.message)
        endpoint_float = float(result.fun if direction == "lower" else -result.fun)
        dual_multipliers = -result.ineqlin.marginals
        support = [index for index, value in enumerate(dual_multipliers) if value > 1e-9]
        entries = recover_exact_entries(support, target_prime, direction)
        # Derive the endpoint from the exact reconstructed dual identity rather
        # than independently rationalizing the floating objective. The latter
        # can prefer an unnecessarily large binary-float approximant when a
        # generous denominator cap is used.
        combined = combine_certificate(entries)
        if set(combined) != {2, target_prime}:
            raise AssertionError(f"dual reconstruction left auxiliary coordinates: {combined}")
        if direction == "lower" and combined[target_prime] == -1:
            endpoint = combined[2]
        elif direction == "upper" and combined[target_prime] == 1:
            endpoint = -combined[2]
        else:
            raise AssertionError(f"dual reconstruction has wrong target coefficient: {combined}")
        certificate = verify_certificate(target_prime, direction, endpoint, entries)
        certificate["solver_endpoint_before_rational_reconstruction"] = endpoint_float
        certificate["solver_gap_from_exact_endpoint"] = endpoint_float - float(endpoint)
        certificates.append(certificate)

    lower = Fraction(certificates[0]["endpoint"])
    upper = Fraction(certificates[1]["endpoint"])
    return {
        "limit": limit,
        "normalization": "E(2)=1",
        "target_prime": target_prime,
        "certificates": certificates,
        "certified_width": fraction_text(upper - lower),
        "certified_width_decimal": float(upper - lower),
        "note": "Each bound follows from a nonnegative rational combination of adjacent order inequalities; all auxiliary prime coordinates cancel exactly.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limits", nargs="+", type=int, default=[100, 1_000, 10_000])
    parser.add_argument("--target-prime", type=int, default=3)
    parser.add_argument("--max-denominator", type=int, default=10**12)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(
        json.dumps(
            [
                extract(limit, args.target_prime, args.max_denominator)
                for limit in args.limits
            ],
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
