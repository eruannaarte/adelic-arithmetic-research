#!/usr/bin/env python3

import unittest
from fractions import Fraction

from exact_trigonometric_positivity import (
    cosine_density_power_polynomial,
    rational_continuum_certificate,
)


REFERENCE_COEFFICIENT_STRINGS = [
    "-0.626411857413006",
    "0.11592816172103249",
    "0.0016529529219241504",
    "0.009509006875539596",
    "-0.0006326688393882172",
    "-0.00013205040380077627",
    "0.00039451702458319105",
    "-0.00030217949865822015",
]


class ExactTrigonometricPositivityTests(unittest.TestCase):
    def test_chebyshev_conversion_is_exact(self) -> None:
        # 1 + 2a*T1 + 2b*T2 = (1-2b) + 2a*x + 4b*x^2.
        polynomial = cosine_density_power_polynomial(
            [Fraction(1, 3), Fraction(1, 5)]
        )
        self.assertEqual(
            polynomial,
            [Fraction(3, 5), Fraction(2, 3), Fraction(4, 5)],
        )

    def test_reference_window_has_exact_rational_strict_bounds(self) -> None:
        certificate = rational_continuum_certificate(
            REFERENCE_COEFFICIENT_STRINGS,
            "0.00001",
            "2.499999995",
        )
        self.assertTrue(certificate.certified)
        self.assertEqual(certificate.lower_root_count, 0)
        self.assertEqual(certificate.upper_root_count, 0)

    def test_crossing_polynomial_is_not_certified(self) -> None:
        # 1+2*cos(theta) crosses zero twice on the circle; in x it has one
        # root in [-1,1].
        certificate = rational_continuum_certificate(["1"], "0", "4")
        self.assertFalse(certificate.certified)
        self.assertEqual(certificate.lower_root_count, 1)

    def test_endpoint_equality_is_not_a_strict_certificate(self) -> None:
        # 1+cos(theta) is nonnegative but attains zero at x=-1.
        certificate = rational_continuum_certificate([Fraction(1, 2)], "0", "3")
        self.assertFalse(certificate.certified)
        self.assertEqual(certificate.lower_value_at_minus_one, 0)


if __name__ == "__main__":
    unittest.main()
