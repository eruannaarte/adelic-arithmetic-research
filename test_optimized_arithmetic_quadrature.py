#!/usr/bin/env python3

import math
import unittest

import numpy as np

from deterministic_arithmetic_sensing import midpoint_times
from optimized_arithmetic_quadrature import (
    CosineQuadratureDesign,
    cosine_window_gram,
    cosine_window_kernel,
    cosine_window_weights,
    exact_alias_magnitude,
    finite_cosine_tail_recovery_error,
    optimize_cosine_quadrature,
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
        self.assertGreaterEqual(
            report["gershgorin_lower_bound"], 0.9 - 1e-8
        )
        self.assertGreater(
            float(np.linalg.eigvalsh(cosine_window_gram(10, design))[0]), 0.9
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


if __name__ == "__main__":
    unittest.main()
