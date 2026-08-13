#!/usr/bin/env python3

import unittest

import numpy as np

from class_group_obstruction import NEGATIVE_FIVE
from global_trace_inversion import (
    finite_trace,
    ideal_count_coefficients,
    recover_coefficients,
    simulate,
)


class GlobalTraceInversionTests(unittest.TestCase):
    def test_initial_negative_five_coefficients(self) -> None:
        coefficients = ideal_count_coefficients(NEGATIVE_FIVE, 6)
        self.assertEqual(coefficients.tolist(), [1, 1, 2, 1, 1, 2])

    def test_noiseless_well_conditioned_recovery(self) -> None:
        report = simulate(NEGATIVE_FIVE, 30, 120, 600.0, 2.0, 0.0, 17)
        self.assertTrue(report["all_integer_coefficients_recovered"])
        self.assertLess(report["maximum_absolute_coefficient_error"], 1e-9)

    def test_direct_trace_round_trip(self) -> None:
        coefficients = ideal_count_coefficients(NEGATIVE_FIVE, 12)
        times = np.linspace(0.0, 500.0, 60) + np.linspace(0.0, 0.1, 60) ** 2
        observations = finite_trace(coefficients, 1.5, times)
        recovered, residual, _ = recover_coefficients(observations, 1.5, times, 12)
        np.testing.assert_allclose(recovered, coefficients, atol=1e-9)
        self.assertLess(np.linalg.norm(residual), 1e-10)


if __name__ == "__main__":
    unittest.main()
