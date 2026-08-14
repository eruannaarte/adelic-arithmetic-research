#!/usr/bin/env python3

import math
import unittest

import numpy as np

from deterministic_arithmetic_sensing import midpoint_times
from optimized_arithmetic_quadrature import (
    cancellation_kernel_interval_bound,
    CosineQuadratureDesign,
    continuous_density_extrema,
    cosine_window_gram,
    cosine_window_kernel,
    cosine_window_weights,
    exact_alias_magnitude,
    fejer_riesz_certificate,
    finite_divisor_tail_proxy,
    finite_cosine_tail_recovery_error,
    optimize_cosine_quadrature,
    quadratic_divisor_interval_l1_bound,
    trigonometric_alias_band_remainder_bound,
    trigonometric_kernel_interval_bound,
)
from class_group_obstruction import NEGATIVE_FIVE
from global_trace_inversion import ideal_count_coefficients


class OptimizedArithmeticQuadratureTests(unittest.TestCase):
    def test_cosine_kernel_matches_direct_positive_design(self) -> None:
        design = CosineQuadratureDesign(
            211, 317.0, np.asarray([-0.45, 0.04, -0.01])
        )
        frequencies = np.asarray([0.0, 0.013, -0.9, 2.7])
        times = midpoint_times(design.sample_count, design.observation_time)
        weights = cosine_window_weights(design)
        direct = np.exp(1j * np.outer(frequencies, times)) @ weights
        np.testing.assert_allclose(
            cosine_window_kernel(frequencies, design), direct, atol=3e-13
        )

    def test_every_weight_design_has_unit_grid_alias(self) -> None:
        design = CosineQuadratureDesign(
            211, 317.0, np.asarray([-0.45, 0.04, -0.01])
        )
        self.assertAlmostEqual(exact_alias_magnitude(design), 1.0, places=12)
        self.assertAlmostEqual(exact_alias_magnitude(design, 3), 1.0, places=12)

    def test_optimizer_enforces_positivity_and_conditioning(self) -> None:
        design, report = optimize_cosine_quadrature(
            maximum_norm=10,
            sigma=2.0,
            observation_time=500.0,
            sample_count=300,
            harmonic_count=3,
            design_tail_cutoff=50,
            gershgorin_lower_bound=0.9,
            density_cap=2.5,
        )
        weights = cosine_window_weights(design)
        self.assertGreaterEqual(float(np.min(weights)), -1e-12)
        self.assertAlmostEqual(float(np.sum(weights)), 1.0, places=13)
        self.assertLessEqual(report["maximum_density"], 2.5 + 1e-8)
        self.assertGreaterEqual(report["continuous_minimum_density"], -1e-9)
        self.assertLessEqual(report["continuous_maximum_density"], 2.5 + 1e-9)
        self.assertLess(report["lower_fejer_riesz_residual"], 1e-8)
        self.assertLess(report["upper_fejer_riesz_residual"], 1e-8)
        self.assertGreater(report["certified_continuous_density_floor"], 0.0)
        self.assertGreater(report["certified_continuous_cap_gap"], 0.0)
        self.assertGreaterEqual(
            report["gershgorin_lower_bound"], 0.9 - 1e-8
        )
        self.assertGreater(
            float(np.linalg.eigvalsh(cosine_window_gram(10, design))[0]), 0.9
        )

    def test_optimizer_accepts_custom_nonnegative_tail_envelope(self) -> None:
        envelope = np.ones(41)
        envelope[0] = 0.0
        _, report = optimize_cosine_quadrature(
            maximum_norm=8,
            sigma=2.0,
            observation_time=300.0,
            sample_count=200,
            harmonic_count=2,
            design_tail_cutoff=40,
            gershgorin_lower_bound=0.85,
            density_cap=2.5,
            design_envelope_coefficients=envelope,
        )
        self.assertEqual(
            report["design_envelope"],
            "caller-supplied nonnegative envelope",
        )

    def test_published_eight_harmonic_design_is_positive_and_well_conditioned(self) -> None:
        design = CosineQuadratureDesign(
            5_000,
            1_000.0,
            np.asarray(
                [
                    -0.6264119552599481,
                    0.11592827656905959,
                    0.0016529449271752857,
                    0.009509011347396578,
                    -0.0006326825432905279,
                    -0.00013204968142858147,
                    0.0003945156501662514,
                    -0.0003021786328145067,
                ]
            ),
        )
        weights = cosine_window_weights(design)
        gram = cosine_window_gram(50, design)
        self.assertGreaterEqual(float(np.min(weights)), -1e-12)
        self.assertGreater(float(np.linalg.eigvalsh(gram)[0]), 0.981)
        self.assertLess(exact_alias_magnitude(design) - 1.0, 1e-10)
        truth = ideal_count_coefficients(NEGATIVE_FIVE, 200)
        recovery = finite_cosine_tail_recovery_error(
            truth[:50], truth[50:], 2.0, design
        )
        self.assertTrue(recovery["integer_rounding_succeeds"])
        self.assertLess(recovery["maximum_absolute_error"], 0.001)

    def test_continuous_extrema_and_fejer_riesz_factorization(self) -> None:
        coefficients = np.asarray([-0.45, 0.04, -0.01])
        extrema = continuous_density_extrema(coefficients)
        grid = np.linspace(0.0, 2.0 * math.pi, 200_001)
        sampled = 1.0 + 2.0 * np.cos(
            np.outer(grid, np.arange(1, 4))
        ) @ coefficients
        self.assertAlmostEqual(extrema["minimum"], float(sampled.min()), places=8)
        self.assertAlmostEqual(extrema["maximum"], float(sampled.max()), places=8)
        certificate = fejer_riesz_certificate(coefficients)
        self.assertLess(certificate.residual, 1e-10)

    def test_published_design_is_positive_on_the_full_interval(self) -> None:
        coefficients = np.asarray(
            [
                -0.6264119552599481,
                0.11592827656905959,
                0.0016529449271752857,
                0.009509011347396578,
                -0.0006326825432905279,
                -0.00013204968142858147,
                0.0003945156501662514,
                -0.0003021786328145067,
            ]
        )
        extrema = continuous_density_extrema(coefficients)
        self.assertGreater(extrema["minimum"], 1e-5)
        self.assertLess(extrema["maximum"], 2.500001)
        self.assertLess(fejer_riesz_certificate(coefficients).residual, 1e-10)

    def test_divisor_interval_bound_dominates_exact_sum(self) -> None:
        sigma = 2.0
        lower, upper = 1_000, 1_700
        tau = np.zeros(upper + 1)
        for divisor in range(1, upper + 1):
            tau[divisor::divisor] += 1.0
        exact = float(
            np.dot(
                tau[lower + 1 : upper + 1],
                np.arange(lower + 1, upper + 1, dtype=float) ** (-sigma),
            )
        )
        bound = quadratic_divisor_interval_l1_bound(
            math.log(lower), math.log(upper), sigma
        )
        self.assertGreaterEqual(bound, exact)
        self.assertLess(bound, 3.0 * exact)

    def test_kernel_interval_bound_dominates_dense_sample(self) -> None:
        design = CosineQuadratureDesign(
            211, 317.0, np.asarray([-0.45, 0.04, -0.01])
        )
        lower, upper = 0.17, 0.23
        frequencies = np.linspace(lower, upper, 100_001)
        exact = float(np.max(np.abs(cosine_window_kernel(frequencies, design))))
        bound = trigonometric_kernel_interval_bound(lower, upper, design)
        self.assertGreaterEqual(bound + 1e-14, exact)

    def test_cancellation_interval_bound_dominates_dense_samples(self) -> None:
        design = CosineQuadratureDesign(
            5_000,
            1_000.0,
            np.asarray(
                [
                    -0.626411857413006,
                    0.11592816172103249,
                    0.0016529529219241504,
                    0.009509006875539596,
                    -0.0006326688393882172,
                    -0.00013205040380077627,
                    0.00039451702458319105,
                    -0.00030217949865822015,
                ]
            ),
        )
        for lower, upper in [(14.01, 14.10), (31.30, 31.40), (47.0, 47.09)]:
            bound = cancellation_kernel_interval_bound(lower, upper, design)
            frequencies = np.linspace(lower, upper, 20_001)
            exact = float(
                np.max(np.abs(cosine_window_kernel(frequencies, design)))
            )
            self.assertGreaterEqual(bound + 1e-14, exact)

    def test_cancellation_bound_improves_remote_pre_alias_interval(self) -> None:
        design = CosineQuadratureDesign(
            5_000, 1_000.0, np.asarray([-0.62, 0.11, 0.002, 0.009])
        )
        cancellation = cancellation_kernel_interval_bound(14.01, 14.10, design)
        triangle = trigonometric_kernel_interval_bound(14.01, 14.10, design)
        self.assertLess(cancellation, triangle)

    def test_alias_band_remainder_improves_global_l1_tail(self) -> None:
        design = CosineQuadratureDesign(
            5_000, 1_000.0, np.asarray([-0.5])
        )
        truncation = 100_000
        from deterministic_arithmetic_sensing import (
            quadratic_divisor_coefficients_sieve,
            quadratic_tail_l1_from_sieve,
        )

        coefficients = quadratic_divisor_coefficients_sieve(truncation)
        base = quadratic_tail_l1_from_sieve(truncation, 2.0, coefficients)
        bound = trigonometric_alias_band_remainder_bound(
            50,
            truncation,
            2.0,
            design,
            base,
            alias_periods=1,
            bins_per_alias=256,
        )
        self.assertGreaterEqual(bound, 0.0)
        self.assertLess(bound, base)

    def test_held_out_tail_proxy_matches_direct_sum(self) -> None:
        design = CosineQuadratureDesign(
            211, 317.0, np.asarray([-0.45, 0.04, -0.01])
        )
        coefficients = np.zeros(41)
        for divisor in range(1, 41):
            coefficients[divisor::divisor] += 1.0
        proxy = finite_divisor_tail_proxy(
            5, 2.0, 6, 40, design, coefficients
        )
        tail = np.arange(6, 41, dtype=float)
        direct = []
        for target in range(1, 6):
            direct.append(
                target**2
                * np.dot(
                    coefficients[6:] * tail ** (-2.0),
                    np.abs(cosine_window_kernel(np.log(target / tail), design)),
                )
            )
        np.testing.assert_allclose(proxy, direct, atol=2e-15)


if __name__ == "__main__":
    unittest.main()
