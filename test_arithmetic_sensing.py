#!/usr/bin/env python3

import math
import unittest

import numpy as np

from arithmetic_sensing import (
    dedekind_tail_l1_bound,
    deterministic_recovery_report,
    divisor_coefficients,
    expected_gram,
    finite_tail_recovery_error,
    interval_kernel,
    matrix_chernoff_failure_bound,
    matrix_chernoff_sample_count,
    normalized_phase_dictionary,
    quadratic_tail_energy_bound,
    sampled_gram,
)
from class_group_obstruction import NEGATIVE_FIVE
from global_trace_inversion import ideal_count_coefficients


class ArithmeticSensingTests(unittest.TestCase):
    def test_expected_gram_matches_numerical_quadrature(self) -> None:
        maximum_norm = 5
        observation_time = 17.0
        times = (np.arange(200_000) + 0.5) * observation_time / 200_000
        dictionary = normalized_phase_dictionary(maximum_norm, times)
        empirical = dictionary.conj().T @ dictionary
        np.testing.assert_allclose(
            empirical, expected_gram(maximum_norm, observation_time), atol=2e-9
        )

    def test_interval_kernel_adjacent_mode(self) -> None:
        gap = math.log(51.0 / 50.0)
        self.assertGreater(abs(interval_kernel(gap, 100.0)), 0.8)
        self.assertLess(abs(interval_kernel(gap, 300.0)), 0.1)

    def test_quadratic_dedekind_coefficients_are_divisor_dominated(self) -> None:
        maximum_norm = 200
        ideal_counts = ideal_count_coefficients(NEGATIVE_FIVE, maximum_norm)
        envelope = divisor_coefficients(maximum_norm, 2)
        self.assertTrue(np.all(ideal_counts <= envelope))
        sigma = 2.0
        finite_actual_tail = float(
            np.sum(
                ideal_counts[50:]
                * np.arange(51, maximum_norm + 1, dtype=float) ** (-sigma)
            )
        )
        self.assertLess(finite_actual_tail, dedekind_tail_l1_bound(50, 2, sigma))

    def test_montgomery_vaughan_energy_bound_covers_finite_tail(self) -> None:
        maximum_norm = 20
        truth_cutoff = 200
        sigma = 2.0
        observation_time = 300.0
        coefficients = ideal_count_coefficients(NEGATIVE_FIVE, truth_cutoff)
        tail_norms = np.arange(maximum_norm + 1, truth_cutoff + 1, dtype=float)
        tail_coefficients = coefficients[maximum_norm:] * tail_norms ** (-sigma)
        times = (np.arange(100_000) + 0.5) * observation_time / 100_000
        tail_values = np.exp(-1j * np.outer(times, np.log(tail_norms))) @ tail_coefficients
        numerical_energy = float(np.mean(np.abs(tail_values) ** 2))
        bound = quadratic_tail_energy_bound(
            maximum_norm, sigma, observation_time
        )["energy_bound"]
        self.assertLess(numerical_energy, bound)

    def test_matrix_chernoff_inversion(self) -> None:
        maximum_norm = 12
        population_lambda = float(
            np.linalg.eigvalsh(expected_gram(maximum_norm, 1_000.0))[0]
        )
        samples = matrix_chernoff_sample_count(
            maximum_norm, population_lambda, 0.5, 0.05
        )
        self.assertLessEqual(
            matrix_chernoff_failure_bound(
                maximum_norm, samples, population_lambda, 0.5
            ),
            0.05,
        )

    def test_streamed_gram_matches_materialized_dictionary(self) -> None:
        maximum_norm = 7
        sample_count = 100
        observation_time = 50.0
        seed = 81
        rng = np.random.default_rng(seed)
        times = rng.uniform(0.0, observation_time, sample_count)
        dictionary = normalized_phase_dictionary(maximum_norm, times)
        np.testing.assert_allclose(
            sampled_gram(
                maximum_norm,
                sample_count,
                observation_time,
                seed,
                chunk_size=17,
            ),
            dictionary.conj().T @ dictionary,
            atol=1e-12,
        )

    def test_deterministic_leverage_certificate(self) -> None:
        maximum_norm = 15
        truth = ideal_count_coefficients(NEGATIVE_FIVE, 30)
        rng = np.random.default_rng(713)
        times = rng.uniform(0.0, 1_000.0, 100)
        noise = 1e-5 / math.sqrt(2.0) * (
            rng.normal(size=len(times)) + 1j * rng.normal(size=len(times))
        )
        report = deterministic_recovery_report(
            truth[:maximum_norm], truth[maximum_norm:], 2.0, times, noise
        )
        self.assertTrue(report["all_componentwise_bounds_hold"])
        self.assertLessEqual(
            report["maximum_absolute_error"], report["global_error_bound"]
        )

    def test_streamed_finite_tail_rounding(self) -> None:
        truth = ideal_count_coefficients(NEGATIVE_FIVE, 100)
        report = finite_tail_recovery_error(
            truth[:20], truth[20:], 2.0, 2_000, 2_000.0, seed=912
        )
        self.assertTrue(report["integer_rounding_succeeds"])
        self.assertLess(report["maximum_real_error"], 0.5)


if __name__ == "__main__":
    unittest.main()
