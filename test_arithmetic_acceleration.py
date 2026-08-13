#!/usr/bin/env python3

import unittest
from fractions import Fraction

from arithmetic_acceleration import comparison


class ArithmeticAccelerationTests(unittest.TestCase):
    def test_cutoff_30_full_network_beats_two_prime_model(self) -> None:
        report = comparison(30)
        self.assertEqual(report["two_prime_width"], "1/2")
        self.assertEqual(report["full_certified_width"], "1/6")
        self.assertEqual(report["two_prime_to_full_width_ratio"], 3.0)

    def test_cutoff_100_short_certificates(self) -> None:
        report = comparison(100)
        self.assertEqual(report["full_certified_interval"], ["11/7", "8/5"])
        self.assertEqual(report["dual_support_sizes"], [5, 2])
        self.assertEqual(Fraction(report["full_certified_width"]), Fraction(1, 35))


if __name__ == "__main__":
    unittest.main()
