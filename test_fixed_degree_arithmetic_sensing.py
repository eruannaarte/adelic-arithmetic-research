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
    fixed_degree_mellin_alias_remainder_bound,
    fixed_degree_tail_l1_elementary_bound,
    fixed_degree_tail_l1_from_sieve,
    one_factor_zeta_log_bin_upper_masses,
    zeta_log_convolution_certificate,
)
from optimized_arithmetic_quadrature import CosineQuadratureDesign


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

    def test_one_factor_log_bins_dominate_exact_masses(self) -> None:
        maximum_log, width, sigma = math.log(10_000), 0.1, 2.0
        upper = one_factor_zeta_log_bin_upper_masses(
            maximum_log, sigma, width, exact_cutoff=100
        )
        exact = np.zeros_like(upper)
        norms = np.arange(1, 10_001, dtype=float)
        indices = np.floor(np.log(norms) / width).astype(int)
        inside = indices < len(exact)
        np.add.at(exact, indices[inside], norms[inside] ** (-sigma))
        self.assertTrue(np.all(upper + 1e-15 >= exact))

    def test_mellin_convolution_mass_covers_exact_degree_three_total(self) -> None:
        degree, sigma = 3, 2.0
        maximum_log = math.log(5_000)
        certificate = zeta_log_convolution_certificate(
            maximum_log,
            degree,
            sigma,
            bin_width=0.05,
            exact_cutoff=100,
        )
        coefficients = fixed_degree_divisor_coefficients_sieve(5_000, degree)
        norms = np.arange(1, 5_001, dtype=float)
        exact = float(np.dot(coefficients[1:], norms ** (-sigma)))
        remote = fixed_degree_tail_l1_elementary_bound(
            maximum_log, degree, sigma
        )
        self.assertGreaterEqual(float(np.sum(certificate.upper_masses)) + remote, exact)

    def test_default_mellin_backend_is_mpfr_dyadic(self) -> None:
        certificate = zeta_log_convolution_certificate(
            math.log(2_000),
            3,
            2.0,
            bin_width=0.05,
            exact_cutoff=100,
        )
        self.assertEqual(
            certificate.verification_backend,
            "MPFR outward bins plus exact dyadic convolution",
        )
        self.assertIsNotNone(certificate.one_factor_sha256)
        self.assertIsNotNone(certificate.convolution_sha256)

    def test_mellin_alias_remainder_dominates_explicit_finite_block(self) -> None:
        degree, sigma, truncation, stop = 3, 2.0, 200, 20_000
        design = CosineQuadratureDesign(
            300, 500.0, np.asarray([-0.45, 0.04, -0.01])
        )
        coefficients = fixed_degree_divisor_coefficients_sieve(stop, degree)
        norms = np.arange(truncation + 1, stop + 1, dtype=float)
        from optimized_arithmetic_quadrature import cosine_window_kernel

        exact_block = float(
            np.dot(
                coefficients[truncation + 1 :] * norms ** (-sigma),
                np.abs(cosine_window_kernel(np.log(1.0 / norms), design)),
            )
        )
        base = float("inf")
        certificate = zeta_log_convolution_certificate(
            math.log(stop) + 2.0,
            degree,
            sigma,
            bin_width=0.02,
            exact_cutoff=1_000,
        )
        bound = fixed_degree_mellin_alias_remainder_bound(
            1, truncation, design, base, certificate
        )
        self.assertGreaterEqual(bound, exact_block)


if __name__ == "__main__":
    unittest.main()
