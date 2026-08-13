#!/usr/bin/env python3
"""Recover finite Dedekind coefficients from aggregate complex heat traces.

For a known cutoff N and field K, sample the Dirichlet polynomial

    F_N(sigma+it)=sum_{n<=N} a_K(n)n^(-sigma-it),

where a_K(n) counts integral ideals of norm n.  Random-time least squares
recovers the weighted coefficients a_K(n)n^-sigma when the log-integer Fourier
dictionary is sufficiently conditioned.
"""

from __future__ import annotations

import argparse
import json
import math
from typing import Sequence

import numpy as np

from class_group_obstruction import NEGATIVE_FIVE
from quadratic_adelic_geometry import GAUSSIAN, GOLDEN, QuadraticField, factor_integer


def local_ideal_count(field: QuadraticField, prime: int, exponent: int) -> int:
    behavior = field.primes_above(prime)[0].behavior
    if behavior == "split":
        return exponent + 1
    if behavior == "ramified":
        return 1
    if behavior == "inert":
        return 1 if exponent % 2 == 0 else 0
    raise AssertionError("unknown prime behavior")


def ideal_count_coefficients(field: QuadraticField, maximum_norm: int) -> np.ndarray:
    if maximum_norm < 1:
        raise ValueError("maximum_norm must be positive")
    coefficients = np.ones(maximum_norm, dtype=int)
    for n in range(2, maximum_norm + 1):
        value = 1
        for prime, exponent in factor_integer(n):
            value *= local_ideal_count(field, prime, exponent)
        coefficients[n - 1] = value
    return coefficients


def phase_dictionary(maximum_norm: int, times: np.ndarray) -> np.ndarray:
    norms = np.arange(1, maximum_norm + 1, dtype=float)
    return np.exp(-1j * np.outer(times, np.log(norms)))


def finite_trace(
    coefficients: np.ndarray, sigma: float, times: np.ndarray
) -> np.ndarray:
    norms = np.arange(1, len(coefficients) + 1, dtype=float)
    weighted = coefficients * norms ** (-sigma)
    return phase_dictionary(len(coefficients), times) @ weighted


def recover_coefficients(
    observations: np.ndarray, sigma: float, times: np.ndarray, maximum_norm: int
) -> tuple[np.ndarray, np.ndarray, float]:
    dictionary = phase_dictionary(maximum_norm, times)
    weighted, *_ = np.linalg.lstsq(dictionary, observations, rcond=None)
    norms = np.arange(1, maximum_norm + 1, dtype=float)
    recovered = weighted * norms**sigma
    residual = observations - dictionary @ weighted
    return recovered, residual, float(np.linalg.cond(dictionary))


def simulate(
    field: QuadraticField,
    maximum_norm: int,
    sample_count: int,
    observation_time: float,
    sigma: float,
    noise_sigma: float,
    seed: int,
    truth_cutoff: int | None = None,
) -> dict[str, object]:
    if sample_count < maximum_norm:
        raise ValueError("sample_count must be at least maximum_norm")
    if truth_cutoff is None:
        truth_cutoff = maximum_norm
    if truth_cutoff < maximum_norm:
        raise ValueError("truth_cutoff cannot be smaller than the fitted cutoff")
    rng = np.random.default_rng(seed)
    times = np.sort(rng.uniform(0.0, observation_time, sample_count))
    truth = ideal_count_coefficients(field, truth_cutoff)
    clean = finite_trace(truth, sigma, times)
    noise = noise_sigma / math.sqrt(2.0) * (
        rng.normal(size=sample_count) + 1j * rng.normal(size=sample_count)
    )
    observations = clean + noise
    recovered, residual, condition = recover_coefficients(
        observations, sigma, times, maximum_norm
    )
    target = truth[:maximum_norm]
    rounded = np.rint(recovered.real).astype(int)
    exact = bool(np.array_equal(rounded, target))
    return {
        "field": field.name,
        "maximum_norm": maximum_norm,
        "truth_cutoff": truth_cutoff,
        "sample_count": sample_count,
        "observation_time": observation_time,
        "sigma": sigma,
        "noise_sigma": noise_sigma,
        "condition_number": condition,
        "all_integer_coefficients_recovered": exact,
        "correct_coefficient_count": int(np.sum(rounded == target)),
        "maximum_absolute_coefficient_error": float(np.max(np.abs(recovered - target))),
        "relative_trace_residual": float(np.linalg.norm(residual) / np.linalg.norm(observations)),
        "seed": seed,
    }


def success_rate(
    field: QuadraticField,
    maximum_norm: int,
    sample_count: int,
    observation_time: float,
    sigma: float,
    noise_sigma: float,
    trials: int,
    seed_offset: int,
    truth_cutoff: int | None = None,
) -> dict[str, object]:
    runs = [
        simulate(
            field,
            maximum_norm,
            sample_count,
            observation_time,
            sigma,
            noise_sigma,
            seed_offset + trial,
            truth_cutoff,
        )
        for trial in range(trials)
    ]
    return {
        "observation_time": observation_time,
        "noise_sigma": noise_sigma,
        "truth_cutoff": maximum_norm if truth_cutoff is None else truth_cutoff,
        "trials": trials,
        "successes": sum(run["all_integer_coefficients_recovered"] for run in runs),
        "success_rate": sum(run["all_integer_coefficients_recovered"] for run in runs) / trials,
        "mean_condition_number": float(np.mean([run["condition_number"] for run in runs])),
        "mean_correct_coefficient_count": float(
            np.mean([run["correct_coefficient_count"] for run in runs])
        ),
        "mean_maximum_absolute_coefficient_error": float(
            np.mean([run["maximum_absolute_coefficient_error"] for run in runs])
        ),
    }


def analyze(maximum_norm: int, trials: int) -> dict[str, object]:
    field = NEGATIVE_FIVE
    sample_count = 4 * maximum_norm
    sigma = 2.0
    windows = [20.0, 100.0, 300.0, 1_000.0]
    noise_levels = [0.0, 1e-5, 1e-4, 1e-3, 3e-3, 1e-2]
    return {
        "field": field.name,
        "coefficient_meaning": "a_K(n)=number of nonzero integral ideals of norm n",
        "maximum_norm": maximum_norm,
        "sample_count": sample_count,
        "sigma": sigma,
        "initial_coefficients": ideal_count_coefficients(field, min(maximum_norm, 20)).tolist(),
        "window_study_at_noise_1e-6": [
            success_rate(
                field,
                maximum_norm,
                sample_count,
                window,
                sigma,
                1e-6,
                trials,
                seed_offset=index * 10_000,
            )
            for index, window in enumerate(windows)
        ],
        "noise_study_at_T_1000": [
            success_rate(
                field,
                maximum_norm,
                sample_count,
                1_000.0,
                sigma,
                noise,
                trials,
                seed_offset=100_000 + index * 10_000,
            )
            for index, noise in enumerate(noise_levels)
        ],
        "unmodelled_tail_control_at_T_1000": [
            success_rate(
                field,
                maximum_norm,
                sample_count,
                1_000.0,
                sigma,
                0.0,
                trials,
                seed_offset=200_000 + truth_cutoff,
                truth_cutoff=truth_cutoff,
            )
            for truth_cutoff in [maximum_norm, 2 * maximum_norm, 4 * maximum_norm]
        ],
        "identifiability": (
            "a known finite cutoff gives a finite Fourier-Vandermonde inverse; "
            "an uncontrolled infinite tail is model error and can destroy integer recovery"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--maximum-norm", type=int, default=50)
    parser.add_argument("--trials", type=int, default=40)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(json.dumps(analyze(args.maximum_norm, args.trials), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
