#!/usr/bin/env python3

import unittest
from fractions import Fraction

from number_field_spectral_system import exact_local_prime_ideal_factor
from quadratic_adelic_geometry import GAUSSIAN, GOLDEN


class NumberFieldSpectralSystemTests(unittest.TestCase):
    def test_gaussian_split_inert_ramified_factors(self) -> None:
        # 2 ramifies, 3 is inert, and 5 splits in Q(i).
        self.assertEqual(exact_local_prime_ideal_factor(GAUSSIAN, 2, 2), Fraction(4, 3))
        self.assertEqual(exact_local_prime_ideal_factor(GAUSSIAN, 3, 2), Fraction(81, 80))
        self.assertEqual(
            exact_local_prime_ideal_factor(GAUSSIAN, 5, 2), Fraction(25, 24) ** 2
        )

    def test_golden_split_inert_ramified_factors(self) -> None:
        # 2 is inert, 5 ramifies, and 11 splits in Q(sqrt(5)).
        self.assertEqual(exact_local_prime_ideal_factor(GOLDEN, 2, 2), Fraction(16, 15))
        self.assertEqual(exact_local_prime_ideal_factor(GOLDEN, 5, 2), Fraction(25, 24))
        self.assertEqual(
            exact_local_prime_ideal_factor(GOLDEN, 11, 2), Fraction(121, 120) ** 2
        )


if __name__ == "__main__":
    unittest.main()
