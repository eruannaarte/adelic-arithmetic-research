#!/usr/bin/env python3

import math
import unittest

import numpy as np

from inverse_regulator_recovery import (
    TRUE_REGULATOR,
    analytic_standard_deviation,
    estimate_regulator_from_log_embeddings,
    monte_carlo,
)


class InverseRegulatorRecoveryTests(unittest.TestCase):
    def test_noiseless_recovery(self) -> None:
        powers = np.arange(1, 8, dtype=float)
        estimate = estimate_regulator_from_log_embeddings(
            powers, powers * TRUE_REGULATOR, -powers * TRUE_REGULATOR
        )
        self.assertAlmostEqual(estimate, TRUE_REGULATOR, places=15)

    def test_analytic_standard_deviation(self) -> None:
        powers = np.asarray([1.0, 2.0, 3.0])
        self.assertAlmostEqual(
            analytic_standard_deviation(powers, 0.2),
            0.2 / math.sqrt(2.0 * 14.0),
        )

    def test_monte_carlo_matches_prediction(self) -> None:
        report = monte_carlo(8, 0.1, 4000, 700_000)
        self.assertLess(abs(report["empirical_to_predicted_std_ratio"] - 1.0), 0.05)
        self.assertLess(abs(report["bias"]), 0.001)


if __name__ == "__main__":
    unittest.main()
