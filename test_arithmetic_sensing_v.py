#!/usr/bin/env python3

import unittest

from arithmetic_sensing_v import exact_positivity_report


class ArithmeticSensingVTests(unittest.TestCase):
    def test_exact_reference_certificate(self) -> None:
        report = exact_positivity_report()
        self.assertTrue(report["exact_sturm_certificate"])
        self.assertEqual(report["lower_boundary_root_count_on_minus1_plus1"], 0)
        self.assertEqual(report["upper_boundary_root_count_on_minus1_plus1"], 0)
        self.assertLess(report["float_density_perturbation_bound_decimal"], 5.11e-17)
        self.assertGreater(report["float_strict_lower_bound"], 9.9999999999e-6)


if __name__ == "__main__":
    unittest.main()
