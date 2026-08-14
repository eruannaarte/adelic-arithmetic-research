#!/usr/bin/env python3

import unittest

import numpy as np

from all_alias_mellin_optimization import (
    ALL_ALIAS_DEGREE_NINE_COEFFICIENTS,
    _cancellation_affine_data,
    exact_candidate_positivity_report,
)
from optimized_arithmetic_quadrature import (
    CosineQuadratureDesign,
    cancellation_kernel_interval_bound,
)


class AllAliasMellinOptimizationTests(unittest.TestCase):
    def test_vectorized_affine_envelope_matches_scalar_theorem(self) -> None:
        lower = np.asarray([14.01, 31.30, 47.00])
        upper = np.asarray([14.10, 31.40, 47.09])
        affine = _cancellation_affine_data(lower, upper, 1_000.0, 5_000, 8)
        center_base, center_basis, var_base, var_basis, fallback = affine
        candidate = ALL_ALIAS_DEGREE_NINE_COEFFICIENTS
        values = np.minimum(
            1.0,
            np.abs(center_base + center_basis @ candidate)
            + var_base
            + var_basis @ np.abs(candidate),
        )
        values[fallback] = 1.0
        design = CosineQuadratureDesign(5_000, 1_000.0, candidate)
        expected = np.asarray(
            [
                cancellation_kernel_interval_bound(lo, hi, design)
                for lo, hi in zip(lower, upper)
            ]
        )
        np.testing.assert_allclose(values, expected, rtol=2e-13, atol=2e-15)

    def test_recorded_candidate_has_exact_continuum_certificate(self) -> None:
        report = exact_candidate_positivity_report()
        self.assertTrue(report["certified"])
        self.assertEqual(report["lower_root_count"], 0)
        self.assertEqual(report["upper_root_count"], 0)
        self.assertGreater(report["binary64_strict_lower_bound"], 0.0)
        self.assertLess(report["binary64_strict_upper_bound"], 2.5)


if __name__ == "__main__":
    unittest.main()
