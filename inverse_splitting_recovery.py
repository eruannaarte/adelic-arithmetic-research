#!/usr/bin/env python3
"""Recover quadratic prime splitting from labelled noisy local heat traces.

For T=p^{-s}, the three unramified/ramified quadratic templates are

    split:    (1-T)^-2
    ramified: (1-T)^-1
    inert:    (1-T^2)^-1.

The exact first two local Dirichlet coefficients distinguish the behaviors.
The noisy experiment classifies sampled log-factors by nearest template.
"""

from __future__ import annotations

import argparse
import json
import math
from typing import Sequence

import numpy as np

from quadratic_adelic_geometry import GAUSSIAN, GOLDEN, QuadraticField
from spectral_adelic_system import primes_up_to


BEHAVIORS = ("split", "ramified", "inert")


def exact_first_coefficients(behavior: str) -> tuple[int, int]:
    """Return coefficients of T and T^2 in the local Euler series."""
    if behavior == "split":
        return 2, 3
    if behavior == "ramified":
        return 1, 1
    if behavior == "inert":
        return 0, 1
    raise ValueError("unknown quadratic splitting behavior")


def behavior_from_coefficients(coefficient_p: int, coefficient_p2: int) -> str:
    lookup = {
        exact_first_coefficients(behavior): behavior for behavior in BEHAVIORS
    }
    try:
        return lookup[(coefficient_p, coefficient_p2)]
    except KeyError as error:
        raise ValueError("the coefficients are not a quadratic local template") from error


def log_local_template(prime: int, betas: np.ndarray, behavior: str) -> np.ndarray:
    t = np.exp(-betas * math.log(prime))
    if behavior == "split":
        return -2.0 * np.log1p(-t)
    if behavior == "ramified":
        return -np.log1p(-t)
    if behavior == "inert":
        return -np.log1p(-(t * t))
    raise ValueError("unknown behavior")


def classify_local_trace(
    prime: int, betas: np.ndarray, observed_log_factors: np.ndarray
) -> tuple[str, dict[str, float], float]:
    residuals = {
        behavior: float(
            np.linalg.norm(
                observed_log_factors - log_local_template(prime, betas, behavior)
            )
        )
        for behavior in BEHAVIORS
    }
    ordering = sorted(residuals, key=residuals.get)
    return ordering[0], residuals, residuals[ordering[1]] - residuals[ordering[0]]


def true_behavior(field: QuadraticField, prime: int) -> str:
    return field.primes_above(prime)[0].behavior


def simulate_field(
    field: QuadraticField,
    primes: Sequence[int],
    betas: np.ndarray,
    noise_sigma: float,
    seed: int,
) -> dict[str, object]:
    if noise_sigma < 0:
        raise ValueError("noise_sigma must be nonnegative")
    rng = np.random.default_rng(seed)
    rows = []
    for prime in primes:
        truth = true_behavior(field, prime)
        clean = log_local_template(prime, betas, truth)
        observed = clean + rng.normal(0.0, noise_sigma, size=len(betas))
        recovered, residuals, margin = classify_local_trace(prime, betas, observed)
        rows.append(
            {
                "prime": prime,
                "truth": truth,
                "recovered": recovered,
                "correct": recovered == truth,
                "classification_margin": margin,
                "template_residuals": residuals,
            }
        )
    return {
        "field": field.name,
        "noise_sigma": noise_sigma,
        "prime_count": len(primes),
        "correct": sum(row["correct"] for row in rows),
        "accuracy": sum(row["correct"] for row in rows) / len(rows),
        "rows": rows,
    }


def monte_carlo_accuracy(
    field: QuadraticField,
    primes: Sequence[int],
    betas: np.ndarray,
    noise_sigma: float,
    trials: int,
    seed_offset: int,
) -> dict[str, object]:
    runs = [
        simulate_field(field, primes, betas, noise_sigma, seed_offset + trial)
        for trial in range(trials)
    ]
    total = trials * len(primes)
    correct = sum(run["correct"] for run in runs)
    return {
        "field": field.name,
        "noise_sigma": noise_sigma,
        "trials": trials,
        "classified_prime_instances": total,
        "correct": correct,
        "accuracy": correct / total,
    }


def analyze(prime_limit: int, trials: int) -> dict[str, object]:
    primes = primes_up_to(prime_limit)
    betas = np.asarray([0.25, 0.4, 0.7, 1.1, 1.6], dtype=float)
    noise_levels = [0.0, 0.002, 0.01, 0.03, 0.1]
    return {
        "exact_coefficient_classifier": {
            behavior: list(exact_first_coefficients(behavior))
            for behavior in BEHAVIORS
        },
        "observed_quantity": "labelled log local Euler factor at each rational prime",
        "betas": betas.tolist(),
        "prime_limit": prime_limit,
        "fields": {
            field.name: [
                monte_carlo_accuracy(
                    field,
                    primes,
                    betas,
                    noise,
                    trials,
                    seed_offset=field.discriminant**2 * 100_000 + index * 10_000,
                )
                for index, noise in enumerate(noise_levels)
            ]
            for field in (GAUSSIAN, GOLDEN)
        },
        "identifiability_boundary": (
            "the classifier assumes rational-prime-labelled local responses; "
            "a few aggregate global trace values do not identify their local factorization"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prime-limit", type=int, default=97)
    parser.add_argument("--trials", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(json.dumps(analyze(args.prime_limit, args.trials), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
