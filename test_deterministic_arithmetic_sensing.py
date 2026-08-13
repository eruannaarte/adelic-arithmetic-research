#!/usr/bin/env python3

import math
import unittest

import numpy as np

from arithmetic_sensing import divisor_coefficients
from deterministic_arithmetic_sensing import (
    alias_aware_tail_remainder_bound,
    deterministic_certificate_report,
    finite_weighted_tail_recovery_error,
    midpoint_gram,
    midpoint_kernel,
    midpoint_times,
    midpoint_weights,
    quadratic_divisor_coefficients_sieve,
    quadratic_tail_l1_elementary_bound,
    quadratic_tail_l1_from_sieve,
    weighted_phase_matrix,
)
from class_group_obstruction import NEGATIVE_FIVE
from global_trace_inversion import ideal_count_coefficients


class DeterministicArithmeticSensingTests(unittest.TestCase):
    def test_closed_grid_kernels_match_direct_sums(self) -> None:
        sample_count = 127
        observation_time = 91.0
        frequencies = np.asarray([0.0, 0.013, -0.7, 3.2])
        times = midpoint_times(sample_count, observation_time)
        for window in ["uniform", "hann"]:
            weights = midpoint_weights(sample_count, observation_time, window)
            direct = np.exp(1j * np.outer(frequencies, times)) @ weights
            np.testing.assert_allclose(
                midpoint_kernel(
                    frequencies, observation_time, sample_count, window
                ),
                direct,
                atol=2e-13,
            )

    def test_alias_value_is_handled_exactly(self) -> None:
        sample_count = 20
        observation_time = 10.0
        frequency = 2.0 * math.pi * sample_count / observation_time
        times = midpoint_times(sample_count, observation_time)
        direct = np.mean(np.exp(1j * frequency * times))
        self.assertAlmostEqual(
            abs(midpoint_kernel(frequency, observation_time, sample_count)),
            abs(direct),
            places=12,
        )

    def test_kernel_gram_matches_materialized_weighted_dictionary(self) -> None:
        maximum_norm = 12
        sample_count = 311
        observation_time = 240.0
        times = midpoint_times(sample_count, observation_time)
        phase = weighted_phase_matrix(maximum_norm, times)
        for window in ["uniform", "hann"]:
            weights = midpoint_weights(sample_count, observation_time, window)
            direct = phase.conj().T @ (weights[:, None] * phase)
            np.testing.assert_allclose(
                midpoint_gram(
                    maximum_norm, observation_time, sample_count, window
                ),
                direct,
                atol=2e-12,
            )

    def test_divisor_sieve_and_remote_tail_bound(self) -> None:
        truncation = 200
        sigma = 2.0
        coefficients = quadratic_divisor_coefficients_sieve(truncation)
        np.testing.assert_array_equal(
            coefficients[1:], divisor_coefficients(truncation, 2)
        )
        exact_tail = quadratic_tail_l1_from_sieve(
            truncation, sigma, coefficients
        )
        self.assertLessEqual(
            exact_tail,
            quadratic_tail_l1_elementary_bound(math.log(truncation), sigma),
        )

    def test_alias_aware_remainder_is_a_strict_improvement_when_safe(self) -> None:
        truncation = 100_000
        sigma = 2.0
        coefficients = quadratic_divisor_coefficients_sieve(truncation)
        base = quadratic_tail_l1_from_sieve(truncation, sigma, coefficients)
        improved = alias_aware_tail_remainder_bound(
            20, truncation, sigma, 1_000.0, 5_000, base, "hann"
        )
        self.assertGreater(improved, 0.0)
        self.assertLess(improved, base / 10.0)

    def test_complete_hann_tail_certificate_and_held_out_recovery(self) -> None:
        report = deterministic_certificate_report(
            maximum_norm=20,
            sigma=2.0,
            observation_time=1_000.0,
            sample_count=5_000,
            truncation=100_000,
            window="hann",
            noise_sigma=0.0,
        )
        self.assertTrue(report["integer_tail_certificate"])
        self.assertLess(report["worst_tail_coefficient_bound"], 0.01)

        truth = ideal_count_coefficients(NEGATIVE_FIVE, 200)
        recovery = finite_weighted_tail_recovery_error(
            truth[:20], truth[20:], 2.0, 1_000.0, 5_000, "hann"
        )
        self.assertTrue(recovery["integer_rounding_succeeds"])
        self.assertLess(
            recovery["maximum_absolute_error"],
            report["worst_tail_coefficient_bound"],
        )


if __name__ == "__main__":
    unittest.main()
