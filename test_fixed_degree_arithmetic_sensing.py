#!/usr/bin/env python3

import math
import unittest

import numpy as np

from deterministic_arithmetic_sensing import (
    quadratic_divisor_coefficients_sieve,
    quadratic_tail_l1_from_sieve,
)
from fixed_degree_arithmetic_sensing import (
    fixed_degree_divisor_coefficients_sieve,
    fixed_degree_tail_l1_elementary_bound,
    fixed_degree_tail_l1_from_sieve,
)


class FixedDegreeArithmeticSensingTests(unittest.TestCase):
    def test_degree_two_sieve_matches_quadratic_sieve(self) -> None:
        np.testing.assert_array_equal(
            fixed_degree_divisor_coefficients_sieve(2_000, 2),
            quadratic_divisor_coefficients_sieve(2_000),
        )

    def test_first_degree_three_coefficients(self) -> None:
        coefficients = fixed_degree_divisor_coefficients_sieve(10, 3)
        np.testing.assert_array_equal(
            coefficients[1:],
            np.asarray([1, 3, 3, 6, 3, 9, 3, 10, 6, 9]),
        )

    def test_degree_two_zeta_remainder_matches_existing_code(self) -> None:
        coefficients = fixed_degree_divisor_coefficients_sieve(20_000, 2)
        self.assertAlmostEqual(
            fixed_degree_tail_l1_from_sieve(20_000, 2, 2.0, coefficients),
            quadratic_tail_l1_from_sieve(20_000, 2.0, coefficients),
            places=14,
        )

    def test_elementary_tail_dominates_exact_finite_block(self) -> None:
        cutoff, stop, degree, sigma = 500, 50_000, 4, 2.0
        coefficients = fixed_degree_divisor_coefficients_sieve(stop, degree)
        norms = np.arange(cutoff + 1, stop + 1, dtype=float)
        exact_block = float(
            np.dot(coefficients[cutoff + 1 :], norms ** (-sigma))
        )
        bound = fixed_degree_tail_l1_elementary_bound(
            math.log(cutoff), degree, sigma
        )
        self.assertGreater(bound, exact_block)


if __name__ == "__main__":
    unittest.main()
