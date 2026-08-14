#!/usr/bin/env python3

import math
import unittest
from fractions import Fraction

import numpy as np

from arithmetic_sensing_iv import REFERENCE_COEFFICIENTS
from fixed_degree_arithmetic_sensing import (
    fixed_degree_divisor_coefficients_sieve,
)
from optimized_arithmetic_quadrature import (
    CosineQuadratureDesign,
    cosine_window_kernel,
)
from verified_mellin_certificate import (
    VerifiedDyadicBins,
    binary64_fractions,
    certified_log_bin_integer_boundaries,
    exact_dyadic_convolution_power,
    fraction_to_float_upper,
    verified_kernel_interval_upper,
    verified_cancellation_kernel_interval_upper,
    verified_mellin_bin_count,
    verified_one_factor_log_bins,
    verified_remote_tail_bounds,
)
from verify_mellin_certificate import (
    artifact_document,
    verify_artifact,
)


class VerifiedMellinCertificateTests(unittest.TestCase):
    def test_published_bin_range_is_outward_selected(self) -> None:
        self.assertEqual(
            verified_mellin_bin_count(
                50, 1_000, 5_000, 2, Fraction(1, 100), 192
            ),
            8_246,
        )

    def test_one_factor_dyadic_bins_dominate_exact_integer_masses(self) -> None:
        width = Fraction(1, 10)
        bins = verified_one_factor_log_bins(
            50,
            width,
            sigma=2,
            exact_cutoff=20,
            dyadic_scale_bits=80,
            mpfr_precision=160,
        )
        boundaries, _ = certified_log_bin_integer_boundaries(50, width, 160)
        for index, numerator in enumerate(bins.numerators):
            lower = boundaries[index]
            upper = boundaries[index + 1] - 1
            exact = sum(
                (Fraction(1, norm * norm) for norm in range(lower, upper + 1)),
                Fraction(0),
            )
            self.assertGreaterEqual(Fraction(numerator, 1 << bins.scale_bits), exact)

    def test_kronecker_convolution_matches_naive_exact_power(self) -> None:
        values = (3, 2, 1, 4)
        bins = VerifiedDyadicBins(
            values,
            10,
            1,
            10,
            1,
            128,
            128,
            "test",
        )
        convolution = exact_dyadic_convolution_power(bins, 3)
        expected = np.asarray([1], dtype=object)
        for _ in range(3):
            expected = np.convolve(expected, np.asarray(values, dtype=object))
        self.assertEqual(
            convolution.numerators,
            tuple(int(value) for value in expected[: len(values)]),
        )

    def test_mpfr_kernel_envelope_dominates_dense_samples(self) -> None:
        design = CosineQuadratureDesign(
            5_000, 1_000.0, REFERENCE_COEFFICIENTS.copy()
        )
        lower, upper = 14.01, 14.06
        # These binary fractions lie inside the exact rational enclosure used
        # below, so ordinary evaluations supply a strict regression target.
        from gmpy2 import mpfr

        bound = verified_kernel_interval_upper(
            (mpfr(lower), mpfr(upper)),
            1_000,
            5_000,
            binary64_fractions(REFERENCE_COEFFICIENTS),
            160,
        )
        samples = np.linspace(lower, upper, 1_001)
        observed = float(np.max(np.abs(cosine_window_kernel(samples, design))))
        self.assertGreaterEqual(float(bound), observed)

    def test_mpfr_cancellation_envelope_dominates_dense_samples(self) -> None:
        from gmpy2 import mpfr

        design = CosineQuadratureDesign(
            5_000, 1_000.0, REFERENCE_COEFFICIENTS.copy()
        )
        for lower, upper in [(14.01, 14.10), (31.30, 31.40), (47.0, 47.09)]:
            bound = verified_cancellation_kernel_interval_upper(
                (mpfr(lower), mpfr(upper)),
                1_000,
                5_000,
                binary64_fractions(REFERENCE_COEFFICIENTS),
                160,
            )
            samples = np.linspace(lower, upper, 20_001)
            observed = float(
                np.max(np.abs(cosine_window_kernel(samples, design)))
            )
            self.assertGreaterEqual(float(bound), observed)

    def test_verified_remote_dominates_an_explicit_block(self) -> None:
        width = Fraction(1, 50)
        bins = verified_one_factor_log_bins(
            600,
            width,
            sigma=2,
            exact_cutoff=100,
            dyadic_scale_bits=80,
            mpfr_precision=160,
        )
        convolution = exact_dyadic_convolution_power(bins, 3)
        design = CosineQuadratureDesign(
            300, 500.0, np.asarray([-0.45, 0.04, -0.01])
        )
        remote = verified_remote_tail_bounds(
            bins,
            convolution,
            truncation=100,
            target_maximum=1,
            observation_time=500,
            sample_count=300,
            coefficients=binary64_fractions(design.coefficients),
            sigma=2,
            output_scale_bits=96,
        )
        stop = 20_000
        coefficients = fixed_degree_divisor_coefficients_sieve(stop, 3)
        norms = np.arange(101, stop + 1, dtype=float)
        explicit = float(
            np.dot(
                coefficients[101:] * norms ** (-2.0),
                np.abs(cosine_window_kernel(np.log(1.0 / norms), design)),
            )
        )
        self.assertGreaterEqual(float(remote.upper_fraction(1)), explicit)

    def test_artifact_hash_rejects_tampering(self) -> None:
        certificate = {"small": {"upper": "7/8"}}
        artifact = artifact_document(certificate)
        self.assertTrue(verify_artifact(artifact, certificate)["verified"])
        artifact["certificate"]["small"]["upper"] = "6/8"
        with self.assertRaises(ValueError):
            verify_artifact(artifact, certificate)

    def test_exact_rational_to_float_is_an_upper_endpoint(self) -> None:
        value = Fraction(1, 10)
        upper = fraction_to_float_upper(value)
        self.assertGreaterEqual(Fraction.from_float(upper), value)
        self.assertLess(upper - float(value), math.ulp(upper) * 1.1)


if __name__ == "__main__":
    unittest.main()
