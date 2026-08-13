#!/usr/bin/env python3
"""Reproducible numerical checks for the Math Google Drive audit.

These experiments test consequences of the valid "numerical lens" ideas.  They
do not attempt to certify any open conjecture from finite computation.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter


def primes_up_to(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    if limit >= 0:
        sieve[0] = 0
    if limit >= 1:
        sieve[1] = 0
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            start = p * p
            sieve[start : limit + 1 : p] = b"\x00" * (
                ((limit - start) // p) + 1
            )
    return [n for n, is_prime in enumerate(sieve) if is_prime]


def prime_density_experiment(limit: int) -> dict[str, object]:
    """Measure gaps after the Li-density change of coordinate.

    The Simpson-rule expression is d_P(p,q) = integral_p^q dt/log(t).  It is
    more faithful to the document's lens than the first-order g/log(p).
    """
    primes = primes_up_to(limit)
    records: list[tuple[int, int, int, float, float]] = []
    for p, q in zip(primes, primes[1:]):
        if p <= 2:
            continue
        gap = q - p
        midpoint = (p + q) / 2.0
        intrinsic_gap = (gap / 6.0) * (
            1.0 / math.log(p)
            + 4.0 / math.log(midpoint)
            + 1.0 / math.log(q)
        )
        records.append((p, q, gap, gap / math.log(p), intrinsic_gap))

    cutoffs = [10**3, 10**4, 10**5, 10**6, limit]
    bins: list[dict[str, object]] = []
    lower = 3
    for upper in cutoffs:
        if upper <= lower:
            continue
        selected = [r for r in records if lower <= r[0] < upper]
        if selected:
            normalized = [r[3] for r in selected]
            intrinsic = [r[4] for r in selected]
            bins.append(
                {
                    "p_range": [lower, upper],
                    "count": len(selected),
                    "mean_gap_over_log_p": statistics.fmean(normalized),
                    "sd_gap_over_log_p": statistics.pstdev(normalized),
                    "mean_Li_coordinate_gap": statistics.fmean(intrinsic),
                    "sd_Li_coordinate_gap": statistics.pstdev(intrinsic),
                }
            )
        lower = upper

    max_record = max(records, key=lambda r: r[3])
    return {
        "limit": limit,
        "prime_count": len(primes),
        "interpretation": (
            "The Li lens makes the mean gap roughly unit-scale, but the "
            "dispersion and exceptional gaps remain."
        ),
        "bins": bins,
        "largest_observed_gap_over_log_p": {
            "p": max_record[0],
            "next_prime": max_record[1],
            "ordinary_gap": max_record[2],
            "gap_over_log_p": max_record[3],
            "Li_coordinate_gap": max_record[4],
        },
    }


def v2(n: int) -> int:
    return (n & -n).bit_length() - 1


def accelerated_collatz_step(odd_n: int) -> tuple[int, int]:
    value = 3 * odd_n + 1
    exponent = v2(value)
    return value >> exponent, exponent


def correlation(xs: list[float], ys: list[float]) -> float:
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    covariance = statistics.fmean(
        (x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)
    )
    variance_x = statistics.fmean((x - mean_x) ** 2 for x in xs)
    variance_y = statistics.fmean((y - mean_y) ** 2 for y in ys)
    return covariance / math.sqrt(variance_x * variance_y)


def collatz_lens_experiment(limit: int, orbit_steps: int) -> dict[str, object]:
    exponents: list[int] = []
    log_changes: list[float] = []
    counts: Counter[int] = Counter()
    for n in range(3, limit + 1, 2):
        next_n, exponent = accelerated_collatz_step(n)
        exponents.append(exponent)
        counts[exponent] += 1
        log_changes.append(math.log(next_n / n))

    pair_x: list[float] = []
    pair_y: list[float] = []
    starts_below_by_window = 0
    completed_starts = 0
    sample_limit = min(limit, 200_001)
    sampled_starts = 0
    for start in range(3, sample_limit + 1, 2):
        sampled_starts += 1
        n = start
        trajectory_exponents: list[int] = []
        for _ in range(orbit_steps):
            if n == 1:
                break
            n, exponent = accelerated_collatz_step(n)
            trajectory_exponents.append(exponent)
        for first, second in zip(trajectory_exponents, trajectory_exponents[1:]):
            pair_x.append(float(first))
            pair_y.append(float(second))
        if len(trajectory_exponents) == orbit_steps:
            completed_starts += 1
        if n < start:
            starts_below_by_window += 1

    total = len(exponents)
    distribution = {
        str(k): {
            "empirical_probability": counts[k] / total,
            "ideal_residue_probability": 2.0 ** (-k),
        }
        for k in sorted(counts)
        if k <= 12
    }
    return {
        "odd_start_limit": limit,
        "one_step_samples": total,
        "accelerated_rule": "U(n)=(3n+1)/2^v2(3n+1) for odd n",
        "identity": (
            "log(U(n)/n)=log(3+1/n)-v2(3n+1)*log(2)"
        ),
        "mean_v2": statistics.fmean(exponents),
        "mean_log_change": statistics.fmean(log_changes),
        "independent_residue_heuristic_log_change": math.log(3.0 / 4.0),
        "fraction_of_one_steps_that_increase": sum(x > 0 for x in log_changes)
        / total,
        "v2_distribution_through_12": distribution,
        "successive_v2_sample_correlation": correlation(pair_x, pair_y),
        "orbit_window": {
            "accelerated_steps": orbit_steps,
            "sampled_starts": sampled_starts,
            "starts_with_full_window": completed_starts,
            "fraction_below_start_or_at_one_by_window": (
                starts_below_by_window / sampled_starts
                if sampled_starts
                else None
            ),
        },
        "interpretation": (
            "The multiplicative/2-adic lens exposes a negative average log "
            "drift, but roughly half of individual odd steps increase. The "
            "unproved issue is controlling dependent residue choices along "
            "every orbit, not computing the average drift."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prime-limit", type=int, default=5_000_000)
    parser.add_argument("--collatz-limit", type=int, default=1_000_001)
    parser.add_argument("--orbit-steps", type=int, default=30)
    args = parser.parse_args()

    result = {
        "finite_computation_warning": (
            "These results illustrate transformations and heuristics; they do "
            "not prove or disprove any open problem."
        ),
        "prime_density": prime_density_experiment(args.prime_limit),
        "collatz": collatz_lens_experiment(
            args.collatz_limit, args.orbit_steps
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
