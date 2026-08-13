#!/usr/bin/env python3
"""Noisy recovery of sparse logarithmic prime modes from finite time samples.

The measured one-particle signal is

    y(t_j) = sum_p a_p exp(-i*t_j*log(p)) + noise_j.

Candidate frequencies log(p) are assumed known. Orthogonal Matching Pursuit
then asks which prime modes are active. This tests finite observability and
noise sensitivity; it does not discover primes from no prior dictionary.
"""

from __future__ import annotations

import argparse
import json
import math
from typing import Sequence

import numpy as np

from spectral_adelic_system import primes_up_to


def measurement_matrix(primes: Sequence[int], times: np.ndarray) -> np.ndarray:
    if times.ndim != 1:
        raise ValueError("times must be one-dimensional")
    frequencies = np.log(np.asarray(primes, dtype=float))
    return np.exp(-1j * np.outer(times, frequencies))


def mutual_coherence(matrix: np.ndarray) -> float:
    norms = np.linalg.norm(matrix, axis=0)
    if np.any(norms == 0):
        raise ValueError("dictionary contains a zero column")
    normalized = matrix / norms
    gram = np.abs(normalized.conj().T @ normalized)
    np.fill_diagonal(gram, 0.0)
    return float(np.max(gram)) if gram.size else 0.0


def coherence_sparsity_threshold(coherence: float) -> float:
    """Largest strict sparsity threshold from mu < 1/(2K-1)."""
    if coherence < 0 or coherence > 1:
        raise ValueError("coherence must lie in [0,1]")
    if coherence == 0:
        return math.inf
    return (1.0 + 1.0 / coherence) / 2.0


def coherence_guarantee(
    candidate_primes: Sequence[int],
    sample_count: int,
    observation_time: float,
    sparsity: int,
    seed: int,
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    times = np.sort(rng.uniform(0.0, observation_time, sample_count))
    matrix = measurement_matrix(candidate_primes, times)
    coherence = mutual_coherence(matrix)
    threshold = coherence_sparsity_threshold(coherence)
    return {
        "sample_count": sample_count,
        "observation_time": observation_time,
        "seed": seed,
        "mutual_coherence": coherence,
        "sparsity": sparsity,
        "strict_sparsity_threshold": threshold,
        "uniform_noiseless_omp_guarantee": sparsity < threshold,
        "equivalent_inequality": f"{coherence} < 1/{2 * sparsity - 1}",
    }


def orthogonal_matching_pursuit(
    matrix: np.ndarray, observations: np.ndarray, sparsity: int
) -> tuple[np.ndarray, list[int], np.ndarray]:
    row_count, column_count = matrix.shape
    if observations.shape != (row_count,):
        raise ValueError("observation shape does not match the measurement matrix")
    if sparsity < 1 or sparsity > min(row_count, column_count):
        raise ValueError("invalid sparsity")

    norms = np.linalg.norm(matrix, axis=0)
    normalized = matrix / norms
    residual = observations.astype(complex, copy=True)
    support: list[int] = []
    coefficients = np.empty(0, dtype=complex)
    for _ in range(sparsity):
        correlations = np.abs(normalized.conj().T @ residual)
        correlations[support] = -1.0
        chosen = int(np.argmax(correlations))
        support.append(chosen)
        coefficients, *_ = np.linalg.lstsq(matrix[:, support], observations, rcond=None)
        residual = observations - matrix[:, support] @ coefficients

    estimate = np.zeros(column_count, dtype=complex)
    estimate[support] = coefficients
    return estimate, support, residual


def minimum_log_frequency_gap(primes: Sequence[int]) -> float:
    frequencies = np.sort(np.log(np.asarray(primes, dtype=float)))
    if len(frequencies) < 2:
        return math.inf
    return float(np.min(np.diff(frequencies)))


def simulate(
    candidate_primes: Sequence[int],
    active_primes: Sequence[int],
    sample_count: int,
    observation_time: float,
    noise_sigma: float,
    seed: int,
) -> dict[str, object]:
    candidates = list(candidate_primes)
    if not set(active_primes) <= set(candidates):
        raise ValueError("every active prime must occur in the candidate dictionary")
    if len(set(active_primes)) != len(active_primes):
        raise ValueError("active primes must be distinct")
    if sample_count < len(active_primes):
        raise ValueError("sample count must be at least the sparsity")
    if observation_time <= 0 or noise_sigma < 0:
        raise ValueError("invalid observation time or noise level")

    rng = np.random.default_rng(seed)
    times = np.sort(rng.uniform(0.0, observation_time, size=sample_count))
    matrix = measurement_matrix(candidates, times)
    truth = np.zeros(len(candidates), dtype=complex)
    active_indices = [candidates.index(prime) for prime in active_primes]
    # Positive unit coefficients are the sparse one-particle trace weights.
    truth[active_indices] = 1.0
    clean = matrix @ truth
    noise = noise_sigma / math.sqrt(2.0) * (
        rng.normal(size=sample_count) + 1j * rng.normal(size=sample_count)
    )
    observations = clean + noise
    estimate, recovered_indices, residual = orthogonal_matching_pursuit(
        matrix, observations, len(active_primes)
    )
    recovered_primes = [candidates[index] for index in recovered_indices]
    coefficient_error = np.linalg.norm(estimate - truth) / np.linalg.norm(truth)
    signal_to_noise = (
        math.inf if np.linalg.norm(noise) == 0 else np.linalg.norm(clean) / np.linalg.norm(noise)
    )
    return {
        "candidate_count": len(candidates),
        "active_primes": sorted(active_primes),
        "recovered_primes": sorted(recovered_primes),
        "exact_support_recovery": set(recovered_primes) == set(active_primes),
        "sample_count": sample_count,
        "observation_time": observation_time,
        "noise_sigma": noise_sigma,
        "signal_to_noise_norm_ratio": float(signal_to_noise),
        "relative_coefficient_error": float(coefficient_error),
        "relative_residual": float(np.linalg.norm(residual) / np.linalg.norm(observations)),
        "dictionary_mutual_coherence": mutual_coherence(matrix),
        "minimum_candidate_log_gap": minimum_log_frequency_gap(candidates),
        "fourier_resolution_proxy_2pi_over_T": 2.0 * math.pi / observation_time,
        "seed": seed,
    }


def success_rate(
    candidate_primes: Sequence[int],
    active_primes: Sequence[int],
    sample_count: int,
    observation_time: float,
    noise_sigma: float,
    trials: int,
    seed_offset: int = 0,
) -> dict[str, object]:
    runs = [
        simulate(
            candidate_primes,
            active_primes,
            sample_count,
            observation_time,
            noise_sigma,
            seed_offset + trial,
        )
        for trial in range(trials)
    ]
    return {
        "observation_time": observation_time,
        "sample_count": sample_count,
        "noise_sigma": noise_sigma,
        "trials": trials,
        "successes": sum(run["exact_support_recovery"] for run in runs),
        "success_rate": sum(run["exact_support_recovery"] for run in runs) / trials,
        "mean_mutual_coherence": float(
            np.mean([run["dictionary_mutual_coherence"] for run in runs])
        ),
        "mean_relative_coefficient_error": float(
            np.mean([run["relative_coefficient_error"] for run in runs])
        ),
        "fourier_resolution_proxy_2pi_over_T": 2.0 * math.pi / observation_time,
    }


def analyze(
    prime_limit: int,
    active_primes: Sequence[int],
    sample_count: int,
    noise_sigma: float,
    trials: int,
) -> dict[str, object]:
    candidates = primes_up_to(prime_limit)
    windows = [5.0, 15.0, 40.0, 100.0, 250.0]
    noise_levels = [0.0, 0.02, 0.1, 0.5, 2.0, 4.0]
    sample_counts = [8, 12, 16, 24, 32, sample_count]
    return {
        "signal": "sum_p a_p exp(-i t log(p)) plus complex Gaussian noise",
        "candidate_primes": candidates,
        "active_primes": list(active_primes),
        "method": "orthogonal matching pursuit with a known log-prime dictionary",
        "single_run": simulate(
            candidates,
            active_primes,
            sample_count,
            windows[-1],
            noise_sigma,
            20260812,
        ),
        "deterministic_coherence_certificate": coherence_guarantee(
            candidates, 512, 1_000.0, len(active_primes), 20260812
        ),
        "observation_window_study": [
            success_rate(
                candidates,
                active_primes,
                sample_count,
                window,
                noise_sigma,
                trials,
                seed_offset=10_000 * index,
            )
            for index, window in enumerate(windows)
        ],
        "noise_study_at_T_250": [
            success_rate(
                candidates,
                active_primes,
                sample_count,
                250.0,
                noise,
                trials,
                seed_offset=100_000 + 10_000 * index,
            )
            for index, noise in enumerate(noise_levels)
        ],
        "sample_count_study_at_T_250": [
            success_rate(
                candidates,
                active_primes,
                count,
                250.0,
                noise_sigma,
                trials,
                seed_offset=200_000 + 10_000 * index,
            )
            for index, count in enumerate(sample_counts)
        ],
        "minimum_candidate_log_gap": minimum_log_frequency_gap(candidates),
        "limitations": [
            "candidate frequencies log(p) are supplied in advance",
            "the Fourier/Vandermonde dictionary is not the random Gaussian ensemble of standard OMP theorems",
            "success rates are finite Monte Carlo evidence, not recovery guarantees",
            "nearby large primes require longer observation windows because their log frequencies crowd",
            "regular sampling grids can create aliases; the experiment uses randomized sample times",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prime-limit", type=int, default=97)
    parser.add_argument("--active-primes", nargs="+", type=int, default=[73, 79, 83, 89])
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--noise", type=float, default=0.02)
    parser.add_argument("--trials", type=int, default=40)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(
        json.dumps(
            analyze(
                args.prime_limit,
                args.active_primes,
                args.samples,
                args.noise,
                args.trials,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
