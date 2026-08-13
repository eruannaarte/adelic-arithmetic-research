#!/usr/bin/env python3
"""Stable recovery certificates for finite Dirichlet data with an omitted tail.

The normalized sensing matrix is

    A[j,n] = m^(-1/2) exp(-i t_j log(n)),  1 <= n <= N.

This module separates three effects:

* conditioning of the sampled log-Fourier dictionary;
* measurement noise;
* bias and sampling fluctuation from the omitted Dirichlet tail.

For quadratic Dedekind zeta functions, coefficientwise domination by the
ordinary divisor function supplies field-uniform analytic tail certificates.
"""

from __future__ import annotations

import argparse
import json
import math
from typing import Sequence

import numpy as np
from scipy.special import zeta

from quadratic_adelic_geometry import factor_integer


def normalized_phase_dictionary(maximum_norm: int, times: np.ndarray) -> np.ndarray:
    if maximum_norm < 1 or times.ndim != 1 or len(times) == 0:
        raise ValueError("a positive cutoff and a nonempty time vector are required")
    norms = np.arange(1, maximum_norm + 1, dtype=float)
    return np.exp(-1j * np.outer(times, np.log(norms))) / math.sqrt(len(times))


def interval_kernel(frequency: np.ndarray | float, observation_time: float):
    """Average of exp(i*t*frequency) for t uniform on [0,T]."""
    if observation_time <= 0:
        raise ValueError("observation_time must be positive")
    frequency_array = np.asarray(frequency, dtype=float)
    value = np.exp(0.5j * observation_time * frequency_array) * np.sinc(
        observation_time * frequency_array / (2.0 * math.pi)
    )
    return value.item() if value.ndim == 0 else value


def expected_gram(maximum_norm: int, observation_time: float) -> np.ndarray:
    """Exact population Gram matrix for independent uniform sample times."""
    if maximum_norm < 1:
        raise ValueError("maximum_norm must be positive")
    logs = np.log(np.arange(1, maximum_norm + 1, dtype=float))
    frequencies = logs[:, None] - logs[None, :]
    gram = interval_kernel(frequencies, observation_time)
    # Remove harmless floating asymmetry before Hermitian eigensolvers.
    return (gram + gram.conj().T) / 2.0


def gershgorin_radius(maximum_norm: int, observation_time: float) -> float:
    gram = expected_gram(maximum_norm, observation_time)
    return float(np.max(np.sum(np.abs(gram), axis=1) - 1.0))


def elementary_gershgorin_lower_bound(
    maximum_norm: int, observation_time: float
) -> float:
    """Closed lower bound 1-4*N*H_(N-1)/T for the population Gram."""
    harmonic = sum(1.0 / index for index in range(1, maximum_norm))
    return 1.0 - 4.0 * maximum_norm * harmonic / observation_time


def matrix_chernoff_failure_bound(
    maximum_norm: int,
    sample_count: int,
    population_lambda_min: float,
    relative_loss: float,
) -> float:
    if not 0.0 < relative_loss < 1.0:
        raise ValueError("relative_loss must lie strictly between zero and one")
    if population_lambda_min <= 0 or sample_count < 1:
        return 1.0
    exponent = (
        -(relative_loss**2)
        * sample_count
        * population_lambda_min
        / (2.0 * maximum_norm)
    )
    return min(1.0, maximum_norm * math.exp(exponent))


def matrix_chernoff_sample_count(
    maximum_norm: int,
    population_lambda_min: float,
    relative_loss: float,
    failure_probability: float,
) -> int:
    if population_lambda_min <= 0:
        raise ValueError("a positive population eigenvalue lower bound is required")
    if not 0.0 < failure_probability < 1.0:
        raise ValueError("failure_probability must lie strictly between zero and one")
    value = (
        2.0
        * maximum_norm
        * math.log(maximum_norm / failure_probability)
        / (relative_loss**2 * population_lambda_min)
    )
    return math.ceil(value)


def divisor_coefficient(n: int, degree: int) -> int:
    """Coefficient d_degree(n) of zeta(s)^degree."""
    if n < 1 or degree < 1:
        raise ValueError("n and degree must be positive")
    result = 1
    for _, exponent in factor_integer(n):
        result *= math.comb(exponent + degree - 1, degree - 1)
    return result


def divisor_coefficients(maximum_norm: int, degree: int) -> np.ndarray:
    return np.asarray(
        [divisor_coefficient(n, degree) for n in range(1, maximum_norm + 1)],
        dtype=float,
    )


def dedekind_tail_l1_bound(maximum_norm: int, degree: int, sigma: float) -> float:
    """Universal degree-d bound sum_(n>N) a_K(n)n^-sigma."""
    if sigma <= 1.0:
        raise ValueError("sigma must exceed one")
    coefficients = divisor_coefficients(maximum_norm, degree)
    norms = np.arange(1, maximum_norm + 1, dtype=float)
    partial = float(np.sum(coefficients * norms ** (-sigma)))
    return max(0.0, float(zeta(sigma, 1.0)) ** degree - partial)


def divisor_square_series(sigma: float) -> float:
    """Dirichlet series sum tau(n)^2 n^-sigma = zeta(sigma)^4/zeta(2sigma)."""
    if sigma <= 1.0:
        raise ValueError("sigma must exceed one")
    return float(zeta(sigma, 1.0)) ** 4 / float(zeta(2.0 * sigma, 1.0))


def divisor_square_tail(maximum_norm: int, sigma: float) -> float:
    coefficients = divisor_coefficients(maximum_norm, 2)
    norms = np.arange(1, maximum_norm + 1, dtype=float)
    partial = float(np.sum(coefficients**2 * norms ** (-sigma)))
    return max(0.0, divisor_square_series(sigma) - partial)


def quadratic_tail_energy_bound(
    maximum_norm: int, sigma: float, observation_time: float
) -> dict[str, float]:
    """Montgomery--Vaughan mean-square bound for a quadratic Dedekind tail.

    For |a_K(n)| <= tau(n), the interval mean of the squared tail is at most

        S0 + (3*pi/T) S1,

    where S0=sum tau(n)^2 n^(-2sigma) and
    S1=sum (n+1)tau(n)^2 n^(-2sigma), both over n>N.
    """
    if sigma <= 1.0:
        raise ValueError("sigma must exceed one")
    s0 = divisor_square_tail(maximum_norm, 2.0 * sigma)
    s1 = divisor_square_tail(maximum_norm, 2.0 * sigma - 1.0) + s0
    bound = s0 + 3.0 * math.pi * s1 / observation_time
    return {"diagonal_tail": s0, "weighted_gap_tail": s1, "energy_bound": bound}


def quadratic_tail_mean_envelope(
    maximum_norm: int,
    sigma: float,
    observation_time: float,
    truncation: int,
) -> np.ndarray:
    """Bounds each target/tail population correlation by a finite sum + remainder."""
    if truncation <= maximum_norm:
        raise ValueError("truncation must exceed maximum_norm")
    tail_norms = np.arange(maximum_norm + 1, truncation + 1, dtype=float)
    envelope_coefficients = divisor_coefficients(truncation, 2)[maximum_norm:]
    weighted = envelope_coefficients * tail_norms ** (-sigma)
    remainder = dedekind_tail_l1_bound(truncation, 2, sigma)
    result = np.empty(maximum_norm, dtype=float)
    for index, norm in enumerate(range(1, maximum_norm + 1)):
        gaps = np.log(tail_norms / norm)
        correlations = np.abs(interval_kernel(gaps, observation_time))
        remainder_correlation = min(
            1.0,
            2.0
            / (observation_time * math.log((truncation + 1.0) / norm)),
        )
        result[index] = float(np.dot(weighted, correlations)) + (
            remainder * remainder_correlation
        )
    return result


def complex_bernstein_deviation(
    uniform_tail_bound: float,
    mean_square_tail_bound: float,
    dimension: int,
    sample_count: int,
    failure_probability: float,
) -> float:
    """Coordinatewise deviation for empirical target/tail correlations.

    With probability at least 1-delta, every one of `dimension` complex
    correlations differs from its population mean by at most the result.
    """
    if uniform_tail_bound < 0 or mean_square_tail_bound < 0:
        raise ValueError("tail bounds must be nonnegative")
    if dimension < 1 or sample_count < 1:
        raise ValueError("dimension and sample_count must be positive")
    if not 0.0 < failure_probability < 1.0:
        raise ValueError("failure_probability must lie strictly between zero and one")
    logarithm = math.log(4.0 * dimension / failure_probability)
    linear = uniform_tail_bound * logarithm / sample_count
    return linear + math.sqrt(
        linear**2 + 4.0 * mean_square_tail_bound * logarithm / sample_count
    )


def empirical_tail_coefficient_bounds(
    times: np.ndarray,
    sigma: float,
    population_correlation_envelope: np.ndarray,
    correlation_deviation: float,
) -> np.ndarray:
    """Data-dependent coefficient bias certificate for the omitted tail."""
    maximum_norm = len(population_correlation_envelope)
    dictionary = normalized_phase_dictionary(maximum_norm, times)
    gram_inverse = np.linalg.inv(dictionary.conj().T @ dictionary)
    correlation_bounds = population_correlation_envelope + correlation_deviation
    norms = np.arange(1, maximum_norm + 1, dtype=float)
    return norms**sigma * (np.abs(gram_inverse) @ correlation_bounds)


def sampled_gram(
    maximum_norm: int,
    sample_count: int,
    observation_time: float,
    seed: int,
    chunk_size: int = 10_000,
) -> np.ndarray:
    """Generate a random-time Gram matrix without storing the full dictionary."""
    if sample_count < 1 or chunk_size < 1:
        raise ValueError("sample_count and chunk_size must be positive")
    rng = np.random.default_rng(seed)
    logs = np.log(np.arange(1, maximum_norm + 1, dtype=float))
    gram = np.zeros((maximum_norm, maximum_norm), dtype=complex)
    remaining = sample_count
    while remaining:
        current = min(chunk_size, remaining)
        times = rng.uniform(0.0, observation_time, current)
        phases = np.exp(-1j * np.outer(times, logs))
        gram += phases.conj().T @ phases
        remaining -= current
    gram /= sample_count
    return (gram + gram.conj().T) / 2.0


def finite_tail_recovery_error(
    target_coefficients: np.ndarray,
    tail_coefficients: np.ndarray,
    sigma: float,
    sample_count: int,
    observation_time: float,
    seed: int,
    chunk_size: int = 2_000,
) -> dict[str, object]:
    """Stream an exact finite-tail least-squares bias experiment."""
    target = np.asarray(target_coefficients, dtype=float)
    tail = np.asarray(tail_coefficients, dtype=float)
    maximum_norm = len(target)
    head_norms = np.arange(1, maximum_norm + 1, dtype=float)
    tail_norms = np.arange(
        maximum_norm + 1, maximum_norm + len(tail) + 1, dtype=float
    )
    head_logs = np.log(head_norms)
    tail_logs = np.log(tail_norms)
    tail_weights = tail * tail_norms ** (-sigma)
    gram = np.zeros((maximum_norm, maximum_norm), dtype=complex)
    cross = np.zeros(maximum_norm, dtype=complex)
    rng = np.random.default_rng(seed)
    remaining = sample_count
    while remaining:
        current = min(chunk_size, remaining)
        times = rng.uniform(0.0, observation_time, current)
        head = np.exp(-1j * np.outer(times, head_logs))
        tail_values = np.exp(-1j * np.outer(times, tail_logs)) @ tail_weights
        gram += head.conj().T @ head
        cross += head.conj().T @ tail_values
        remaining -= current
    gram /= sample_count
    cross /= sample_count
    coefficient_error = head_norms**sigma * np.linalg.solve(gram, cross)
    recovered = target + coefficient_error
    return {
        "maximum_absolute_error": float(np.max(np.abs(coefficient_error))),
        "maximum_real_error": float(np.max(np.abs(coefficient_error.real))),
        "worst_coefficient": int(np.argmax(np.abs(coefficient_error)) + 1),
        "integer_rounding_succeeds": bool(
            np.array_equal(np.rint(recovered.real).astype(int), target.astype(int))
        ),
        "lambda_min": float(np.linalg.eigvalsh(gram)[0]),
    }


def tail_coefficient_bounds_from_gram(
    gram: np.ndarray,
    sigma: float,
    population_correlation_envelope: np.ndarray,
    correlation_deviation: float,
) -> np.ndarray:
    maximum_norm = len(population_correlation_envelope)
    if gram.shape != (maximum_norm, maximum_norm):
        raise ValueError("gram and correlation envelope dimensions disagree")
    gram_inverse = np.linalg.inv(gram)
    correlation_bounds = population_correlation_envelope + correlation_deviation
    norms = np.arange(1, maximum_norm + 1, dtype=float)
    return norms**sigma * (np.abs(gram_inverse) @ correlation_bounds)


def gaussian_rounding_failure_bound_from_gram(
    gram: np.ndarray,
    sample_count: int,
    sigma: float,
    noise_sigma: float,
    tail_coefficient_bounds: np.ndarray,
) -> float:
    maximum_norm = len(tail_coefficient_bounds)
    if gram.shape != (maximum_norm, maximum_norm):
        raise ValueError("gram and tail bound dimensions disagree")
    if np.any(tail_coefficient_bounds >= 0.5):
        return 1.0
    if noise_sigma < 0:
        raise ValueError("noise_sigma must be nonnegative")
    if noise_sigma == 0:
        return 0.0
    gram_inverse = np.linalg.inv(gram)
    leverage = np.real(np.diag(gram_inverse))
    norms = np.arange(1, maximum_norm + 1, dtype=float)
    margins = 0.5 - tail_coefficient_bounds
    exponents = (
        sample_count
        * margins**2
        / (noise_sigma**2 * norms ** (2.0 * sigma) * leverage)
    )
    return min(1.0, float(2.0 * np.sum(np.exp(-exponents))))


def gaussian_rounding_failure_bound(
    times: np.ndarray,
    sigma: float,
    noise_sigma: float,
    tail_coefficient_bounds: np.ndarray,
) -> float:
    """Conditional union bound for rounding real integer coefficients.

    Noise is circular complex Gaussian with E|eta_j|^2=noise_sigma^2.
    """
    maximum_norm = len(tail_coefficient_bounds)
    dictionary = normalized_phase_dictionary(maximum_norm, times)
    return gaussian_rounding_failure_bound_from_gram(
        dictionary.conj().T @ dictionary,
        len(times),
        sigma,
        noise_sigma,
        tail_coefficient_bounds,
    )


def deterministic_recovery_report(
    target_coefficients: Sequence[float],
    tail_coefficients: Sequence[float],
    sigma: float,
    times: np.ndarray,
    noise: np.ndarray,
) -> dict[str, object]:
    """Verify exact least-squares perturbation identities and leverage bounds."""
    target = np.asarray(target_coefficients, dtype=float)
    tail = np.asarray(tail_coefficients, dtype=float)
    maximum_norm = len(target)
    if len(noise) != len(times):
        raise ValueError("noise and times must have the same length")
    dictionary = normalized_phase_dictionary(maximum_norm, times)
    gram = dictionary.conj().T @ dictionary
    gram_inverse = np.linalg.inv(gram)
    weighted_target = target * np.arange(1, maximum_norm + 1) ** (-sigma)
    normalized_observations = dictionary @ weighted_target
    if len(tail):
        tail_norms = np.arange(maximum_norm + 1, maximum_norm + len(tail) + 1)
        tail_dictionary = (
            np.exp(-1j * np.outer(times, np.log(tail_norms)))
            / math.sqrt(len(times))
        )
        normalized_tail = tail_dictionary @ (tail * tail_norms ** (-sigma))
    else:
        normalized_tail = np.zeros(len(times), dtype=complex)
    normalized_noise = noise / math.sqrt(len(times))
    recovered_weighted, *_ = np.linalg.lstsq(
        dictionary,
        normalized_observations + normalized_tail + normalized_noise,
        rcond=None,
    )
    norms = np.arange(1, maximum_norm + 1, dtype=float)
    recovered = recovered_weighted * norms**sigma
    coefficient_error = recovered - target
    leverage = np.sqrt(np.maximum(0.0, np.real(np.diag(gram_inverse))))
    componentwise_bound = norms**sigma * leverage * (
        np.linalg.norm(normalized_tail) + np.linalg.norm(normalized_noise)
    )
    lambda_min = float(np.linalg.eigvalsh(gram)[0])
    global_bound = maximum_norm**sigma * (
        np.linalg.norm(normalized_tail) + np.linalg.norm(normalized_noise)
    ) / math.sqrt(lambda_min)
    return {
        "lambda_min": lambda_min,
        "condition_number": float(np.linalg.cond(dictionary)),
        "maximum_absolute_error": float(np.max(np.abs(coefficient_error))),
        "global_error_bound": float(global_bound),
        "componentwise_bounds": componentwise_bound.tolist(),
        "componentwise_errors": np.abs(coefficient_error).tolist(),
        "all_componentwise_bounds_hold": bool(
            np.all(np.abs(coefficient_error) <= componentwise_bound + 1e-10)
        ),
    }


def conditioning_study(
    maximum_norm: int, sample_count: int, trials: int
) -> list[dict[str, object]]:
    result = []
    for window_index, observation_time in enumerate([100.0, 300.0, 1_000.0, 3_000.0]):
        population = expected_gram(maximum_norm, observation_time)
        population_lambda = max(0.0, float(np.linalg.eigvalsh(population)[0]))
        radius = gershgorin_radius(maximum_norm, observation_time)
        empirical_lambdas = []
        for trial in range(trials):
            rng = np.random.default_rng(10_000 * window_index + trial)
            times = rng.uniform(0.0, observation_time, sample_count)
            dictionary = normalized_phase_dictionary(maximum_norm, times)
            empirical_lambdas.append(
                max(0.0, float(np.linalg.eigvalsh(dictionary.conj().T @ dictionary)[0]))
            )
        sample_requirement = (
            matrix_chernoff_sample_count(
                maximum_norm, population_lambda, 0.5, 0.05
            )
            if population_lambda > 1e-12
            else None
        )
        result.append(
            {
                "observation_time": observation_time,
                "population_lambda_min": population_lambda,
                "gershgorin_radius": radius,
                "gershgorin_lower_bound": 1.0 - radius,
                "elementary_lower_bound": elementary_gershgorin_lower_bound(
                    maximum_norm, observation_time
                ),
                "mean_empirical_lambda_min": float(np.mean(empirical_lambdas)),
                "minimum_empirical_lambda_min": float(np.min(empirical_lambdas)),
                "chernoff_samples_for_half_population_lambda_at_95_percent": sample_requirement,
            }
        )
    return result


def analyze(maximum_norm: int, sample_count: int, trials: int) -> dict[str, object]:
    sigma = 2.0
    tail_truncation = max(20_000, 200 * maximum_norm)
    uniform_tail = dedekind_tail_l1_bound(maximum_norm, 2, sigma)
    tail_tables = []
    for observation_time in [300.0, 1_000.0, 3_000.0, 10_000.0]:
        population = expected_gram(maximum_norm, observation_time)
        population_inverse = np.linalg.inv(population)
        correlation_envelope = quadratic_tail_mean_envelope(
            maximum_norm, sigma, observation_time, tail_truncation
        )
        norms = np.arange(1, maximum_norm + 1, dtype=float)
        population_bias = norms**sigma * (
            np.abs(population_inverse) @ correlation_envelope
        )
        energy = quadratic_tail_energy_bound(
            maximum_norm, sigma, observation_time
        )
        deviation = complex_bernstein_deviation(
            uniform_tail,
            energy["energy_bound"],
            maximum_norm,
            sample_count,
            0.05,
        )
        tail_tables.append(
            {
                "observation_time": observation_time,
                "uniform_tail_bound": uniform_tail,
                **energy,
                "population_correlation_l2_envelope": float(
                    np.linalg.norm(correlation_envelope)
                ),
                "worst_population_coefficient_bias_bound": float(
                    np.max(population_bias)
                ),
                "finite_sample_correlation_deviation_at_95_percent": deviation,
            }
        )
    adjacent_gap = math.log((maximum_norm + 1.0) / maximum_norm)
    certificate_time = 10_000.0
    certificate_envelope = quadratic_tail_mean_envelope(
        maximum_norm, sigma, certificate_time, tail_truncation
    )
    certificate_energy = quadratic_tail_energy_bound(
        maximum_norm, sigma, certificate_time
    )["energy_bound"]
    finite_sample_certificates = []
    for certificate_samples in [200, 1_000, 5_000, 20_000, 100_000, 500_000]:
        deviation = complex_bernstein_deviation(
            uniform_tail,
            certificate_energy,
            maximum_norm,
            certificate_samples,
            0.05,
        )
        gram = sampled_gram(
            maximum_norm,
            certificate_samples,
            certificate_time,
            seed=900_000 + certificate_samples,
        )
        coefficient_bounds = tail_coefficient_bounds_from_gram(
            gram, sigma, certificate_envelope, deviation
        )
        finite_sample_certificates.append(
            {
                "sample_count": certificate_samples,
                "correlation_deviation": deviation,
                "lambda_min": float(np.linalg.eigvalsh(gram)[0]),
                "worst_tail_coefficient_bound": float(
                    np.max(coefficient_bounds)
                ),
                "integer_tail_certificate": bool(
                    np.max(coefficient_bounds) < 0.5
                ),
                "rounding_failure_bound_at_noise_0.01": (
                    gaussian_rounding_failure_bound_from_gram(
                        gram,
                        certificate_samples,
                        sigma,
                        0.01,
                        coefficient_bounds,
                    )
                ),
            }
        )
    held_out_truth_cutoff = max(2_000, 40 * maximum_norm)
    from class_group_obstruction import NEGATIVE_FIVE
    from global_trace_inversion import ideal_count_coefficients

    held_out_truth = ideal_count_coefficients(NEGATIVE_FIVE, held_out_truth_cutoff)
    held_out_tail_runs = [
        finite_tail_recovery_error(
            held_out_truth[:maximum_norm],
            held_out_truth[maximum_norm:],
            sigma,
            200_000,
            certificate_time,
            seed=2_000_000 + seed,
        )
        for seed in range(5)
    ]
    certificate_samples = 500_000
    certificate_deviation = complex_bernstein_deviation(
        uniform_tail,
        certificate_energy,
        maximum_norm,
        certificate_samples,
        0.05,
    )
    certificate_seed_runs = []
    for seed in range(20):
        gram = sampled_gram(
            maximum_norm,
            certificate_samples,
            certificate_time,
            seed=1_500_000 + seed,
        )
        coefficient_bounds = tail_coefficient_bounds_from_gram(
            gram, sigma, certificate_envelope, certificate_deviation
        )
        certificate_seed_runs.append(
            {
                "seed": seed,
                "lambda_min": float(np.linalg.eigvalsh(gram)[0]),
                "worst_tail_coefficient_bound": float(
                    np.max(coefficient_bounds)
                ),
                "integer_tail_certificate": bool(
                    np.max(coefficient_bounds) < 0.5
                ),
                "rounding_failure_bound_at_noise_0.01": (
                    gaussian_rounding_failure_bound_from_gram(
                        gram,
                        certificate_samples,
                        sigma,
                        0.01,
                        coefficient_bounds,
                    )
                ),
            }
        )
    return {
        "model": "random-time log-Fourier sensing with a quadratic Dedekind tail",
        "maximum_norm": maximum_norm,
        "sample_count": sample_count,
        "trials": trials,
        "sigma": sigma,
        "conditioning_study": conditioning_study(
            maximum_norm, sample_count, trials
        ),
        "quadratic_tail_study": tail_tables,
        "first_omitted_mode_correlations": [
            {
                "observation_time": observation_time,
                "absolute_correlation": float(
                    abs(interval_kernel(adjacent_gap, observation_time))
                ),
            }
            for observation_time in [100.0, 300.0, 1_000.0, 3_000.0]
        ],
        "finite_sample_tail_certificates_at_T_10000": finite_sample_certificates,
        "held_out_Q_sqrt_minus_5_tail_experiment": {
            "truth_cutoff": held_out_truth_cutoff,
            "sample_count": 200_000,
            "runs": held_out_tail_runs,
        },
        "held_out_certificate_seed_study": {
            "observation_time": certificate_time,
            "sample_count": certificate_samples,
            "tail_confidence": 0.95,
            "certified_runs": sum(
                run["integer_tail_certificate"]
                for run in certificate_seed_runs
            ),
            "trials": len(certificate_seed_runs),
            "minimum_worst_tail_coefficient_bound": min(
                run["worst_tail_coefficient_bound"]
                for run in certificate_seed_runs
            ),
            "maximum_worst_tail_coefficient_bound": max(
                run["worst_tail_coefficient_bound"]
                for run in certificate_seed_runs
            ),
            "maximum_noise_rounding_failure_bound": max(
                run["rounding_failure_bound_at_noise_0.01"]
                for run in certificate_seed_runs
            ),
            "runs": certificate_seed_runs,
        },
        "interpretation": (
            "conditioning, measurement noise, population tail bias, and finite-sample "
            "tail fluctuation are separate certificate terms; the adjacent omitted "
            "frequency shows why the controlling resolution scale is T/N"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--maximum-norm", type=int, default=50)
    parser.add_argument("--sample-count", type=int, default=200)
    parser.add_argument("--trials", type=int, default=40)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(
        json.dumps(
            analyze(args.maximum_norm, args.sample_count, args.trials),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
