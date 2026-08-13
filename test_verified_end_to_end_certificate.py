#!/usr/bin/env python3

import unittest
import json
from fractions import Fraction
from pathlib import Path

import numpy as np

from arithmetic_sensing_iv import REFERENCE_COEFFICIENTS
from fixed_degree_arithmetic_sensing import (
    fixed_degree_divisor_coefficients_sieve,
)
from optimized_arithmetic_quadrature import (
    CosineQuadratureDesign,
    centered_cosine_response,
    cosine_window_gram,
)
from verified_end_to_end_certificate import (
    exact_fixed_degree_coefficients_uint64,
    verified_end_to_end_bound,
    verified_finite_tail_bounds,
    verified_gram_row_bound,
)
from verify_end_to_end_certificate import artifact_document, verify_artifact


class VerifiedEndToEndCertificateTests(unittest.TestCase):
    def test_checked_uint64_sieve_matches_existing_small_sieve(self) -> None:
        exact = exact_fixed_degree_coefficients_uint64(300, 7)
        existing = fixed_degree_divisor_coefficients_sieve(300, 7)
        np.testing.assert_array_equal(exact, existing)

    def test_arb_finite_tail_dominates_binary64_direct_sum(self) -> None:
        degree = 4
        maximum_norm = 5
        truncation = 300
        certificate = verified_finite_tail_bounds(
            degree,
            maximum_norm,
            truncation,
            observation_time=100,
            sample_count=50,
            precision=96,
            output_scale_bits=80,
            processes=1,
        )
        coefficients = fixed_degree_divisor_coefficients_sieve(
            truncation, degree
        )
        design = CosineQuadratureDesign(
            50, 100.0, REFERENCE_COEFFICIENTS.copy()
        )
        norms = np.arange(maximum_norm + 1, truncation + 1, dtype=float)
        weights = coefficients[maximum_norm + 1 :] * norms ** (-2.0)
        for target in range(1, maximum_norm + 1):
            direct = float(
                np.dot(
                    weights,
                    np.abs(centered_cosine_response(np.log(norms / target), design)),
                )
            )
            # The comparison target itself is a binary64 sum and may round a
            # few ulps upward; Arb encloses the exact mathematical sum.
            self.assertGreaterEqual(
                float(certificate.upper_fraction(target)) + 2e-14, direct
            )

    def test_arb_gram_row_bound_dominates_binary64_matrix(self) -> None:
        design = CosineQuadratureDesign(
            50, 100.0, REFERENCE_COEFFICIENTS.copy()
        )
        matrix = cosine_window_gram(8, design)
        observed = float(
            np.max(np.sum(np.abs(matrix - np.eye(len(matrix))), axis=1))
        )
        certificate = verified_gram_row_bound(
            8,
            100,
            50,
            precision=96,
            output_scale_bits=80,
        )
        self.assertGreaterEqual(
            float(certificate.upper_fraction) + 2e-14, observed
        )

    def test_neumann_consequence_is_exact_rational_arithmetic(self) -> None:
        finite = verified_finite_tail_bounds(
            3,
            maximum_norm=3,
            truncation=80,
            observation_time=100,
            sample_count=50,
            precision=96,
            output_scale_bits=80,
            processes=1,
        )
        gram = verified_gram_row_bound(
            3, 100, 50, precision=96, output_scale_bits=80
        )
        remote = [1, 2, 3]
        result = verified_end_to_end_bound(finite, remote, 80, gram)
        tails = [
            finite.upper_fraction(target) + Fraction(remote[target - 1], 1 << 80)
            for target in range(1, 4)
        ]
        self.assertEqual(result.maximum_tail, max(tails))
        expected_components = [
            tail
            + Fraction(gram.row_numerators[index], 1 << 80)
            * max(tails)
            / (1 - gram.upper_fraction)
            for index, tail in enumerate(tails)
        ]
        expected_coefficients = [
            (index + 1) ** 2 * value
            for index, value in enumerate(expected_components)
        ]
        self.assertEqual(result.coefficient_bound, max(expected_coefficients))

    def test_artifact_hash_rejects_tampering(self) -> None:
        certificate = {"formal": {"upper": "7/8"}}
        artifact = artifact_document(certificate)
        self.assertTrue(verify_artifact(artifact, certificate)["verified"])
        artifact["certificate"]["formal"]["upper"] = "6/8"
        with self.assertRaises(ValueError):
            verify_artifact(artifact, certificate)

    def test_published_artifact_records_the_formal_frontier(self) -> None:
        path = (
            Path(__file__).resolve().parent
            / "certificates"
            / "arithmetic_sensing_v_end_to_end.json"
        )
        with path.open(encoding="utf-8") as handle:
            artifact = json.load(handle)
        self.assertTrue(
            verify_artifact(artifact, artifact["certificate"])["verified"]
        )
        degrees = {
            entry["degree"]: entry
            for entry in artifact["certificate"]["degrees"]
        }
        self.assertTrue(degrees[13]["integer_rounding_certificate"])
        self.assertFalse(degrees[14]["integer_rounding_certificate"])
        self.assertEqual(degrees[13]["worst_coefficient_target"], 50)


if __name__ == "__main__":
    unittest.main()
