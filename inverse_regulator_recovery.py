#!/usr/bin/env python3
"""Recover the Q(sqrt(5)) regulator from a noisy Archimedean unit channel.

For the fundamental unit phi, the normalized real logarithmic embedding is
(R,-R), R=log(phi).  Observing powers phi^k gives a one-parameter linear
regression.  Finite ideal data alone sees every unit as the unit ideal and
cannot perform this direct lattice-spacing reconstruction.
"""

from __future__ import annotations

import argparse
import json
import math

import numpy as np


PHI = (1.0 + math.sqrt(5.0)) / 2.0
TRUE_REGULATOR = math.log(PHI)


def estimate_regulator_from_log_embeddings(
    powers: np.ndarray, first_logs: np.ndarray, second_logs: np.ndarray
) -> float:
    if powers.ndim != 1 or first_logs.shape != powers.shape or second_logs.shape != powers.shape:
        raise ValueError("powers and embedding logs must be matching vectors")
    if np.any(powers <= 0):
        raise ValueError("positive unit powers are required")
    differences = first_logs - second_logs
    return float(np.dot(powers, differences) / (2.0 * np.dot(powers, powers)))


def analytic_standard_deviation(powers: np.ndarray, embedding_noise_sigma: float) -> float:
    if embedding_noise_sigma < 0:
        raise ValueError("noise sigma must be nonnegative")
    return float(embedding_noise_sigma / math.sqrt(2.0 * np.dot(powers, powers)))


def simulate(maximum_power: int, noise_sigma: float, seed: int) -> dict[str, object]:
    if maximum_power < 1:
        raise ValueError("maximum_power must be positive")
    powers = np.arange(1, maximum_power + 1, dtype=float)
    rng = np.random.default_rng(seed)
    first = powers * TRUE_REGULATOR + rng.normal(0.0, noise_sigma, maximum_power)
    second = -powers * TRUE_REGULATOR + rng.normal(0.0, noise_sigma, maximum_power)
    estimate = estimate_regulator_from_log_embeddings(powers, first, second)
    return {
        "maximum_power": maximum_power,
        "embedding_noise_sigma": noise_sigma,
        "estimate": estimate,
        "truth": TRUE_REGULATOR,
        "absolute_error": abs(estimate - TRUE_REGULATOR),
        "analytic_standard_deviation": analytic_standard_deviation(
            powers, noise_sigma
        ),
        "seed": seed,
    }


def monte_carlo(
    maximum_power: int, noise_sigma: float, trials: int, seed_offset: int
) -> dict[str, object]:
    runs = [
        simulate(maximum_power, noise_sigma, seed_offset + trial)
        for trial in range(trials)
    ]
    errors = np.asarray([run["estimate"] - TRUE_REGULATOR for run in runs])
    powers = np.arange(1, maximum_power + 1, dtype=float)
    predicted = analytic_standard_deviation(powers, noise_sigma)
    return {
        "maximum_power": maximum_power,
        "embedding_noise_sigma": noise_sigma,
        "trials": trials,
        "bias": float(np.mean(errors)),
        "empirical_standard_deviation": float(np.std(errors, ddof=1)),
        "root_mean_square_error": float(np.sqrt(np.mean(errors**2))),
        "analytic_standard_deviation": predicted,
        "empirical_to_predicted_std_ratio": (
            float(np.std(errors, ddof=1) / predicted) if predicted else None
        ),
    }


def analyze(trials: int) -> dict[str, object]:
    maximum_powers = [1, 2, 4, 8, 16, 32]
    noise_sigma = 0.1
    return {
        "field": "Q(sqrt(5))",
        "fundamental_unit": "phi=(1+sqrt(5))/2",
        "true_regulator": TRUE_REGULATOR,
        "measurement": (
            "labelled logarithms of the two real embeddings of phi^k, "
            "each with independent Gaussian noise"
        ),
        "noise_sigma": noise_sigma,
        "power_study": [
            monte_carlo(
                maximum_power,
                noise_sigma,
                trials,
                seed_offset=maximum_power * 100_000,
            )
            for maximum_power in maximum_powers
        ],
        "direct_nonidentifiability_without_archimedean_data": (
            "for every unit u, (u)=O_K and |N(u)|=1; unit principal-ideal "
            "and absolute-norm observations are therefore constant"
        ),
        "scope_warning": (
            "the analytic residue of a Dedekind zeta function can contain the "
            "regulator through the class-number formula; the nonidentifiability "
            "statement concerns direct unit-lattice recovery from ideal labels"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=2000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(json.dumps(analyze(args.trials), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
