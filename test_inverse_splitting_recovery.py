#!/usr/bin/env python3

import unittest

import numpy as np

from inverse_splitting_recovery import (
    behavior_from_coefficients,
    classify_local_trace,
    exact_first_coefficients,
    log_local_template,
)


class InverseSplittingRecoveryTests(unittest.TestCase):
    def test_exact_coefficient_pairs_classify(self) -> None:
        for behavior in ("split", "ramified", "inert"):
            self.assertEqual(
                behavior_from_coefficients(*exact_first_coefficients(behavior)),
                behavior,
            )

    def test_invalid_coefficient_pair_rejected(self) -> None:
        with self.assertRaises(ValueError):
            behavior_from_coefficients(2, 2)

    def test_noiseless_templates_recover(self) -> None:
        betas = np.asarray([0.25, 0.5, 1.0, 2.0])
        for behavior in ("split", "ramified", "inert"):
            observed = log_local_template(97, betas, behavior)
            recovered, residuals, margin = classify_local_trace(97, betas, observed)
            self.assertEqual(recovered, behavior)
            self.assertAlmostEqual(residuals[behavior], 0.0)
            self.assertGreater(margin, 0.0)


if __name__ == "__main__":
    unittest.main()
