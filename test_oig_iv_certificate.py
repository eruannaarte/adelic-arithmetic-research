#!/usr/bin/env python3

import unittest
from fractions import Fraction

from oig_iv_certificate import (
    BINARY64_GRID_SHA256,
    DUAL_FACTOR,
    DUAL_NORMALIZER,
    DUAL_UPPER_BOUND,
    PRIMAL_DENOMINATOR,
    PRIMAL_LOWER_BOUND,
    PRIMAL_NUMERATORS,
    TANGENT_METRIC,
    run_interval_certificate,
)


class OIGIVIntervalCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run_interval_certificate()

    def test_exact_primal_is_a_feasible_dyadic_probability_design(self) -> None:
        self.assertEqual(PRIMAL_DENOMINATOR, 4096)
        self.assertEqual(sum(PRIMAL_NUMERATORS.values()), PRIMAL_DENOMINATOR)
        self.assertEqual(len(PRIMAL_NUMERATORS), 6)
        self.assertTrue(all(value > 0 for value in PRIMAL_NUMERATORS.values()))

    def test_dual_psd_and_metric_trace_are_exact_integer_identities(self) -> None:
        exact_metric_trace = sum(
            DUAL_FACTOR[row][factor_column]
            * TANGENT_METRIC[row][column]
            * DUAL_FACTOR[column][factor_column]
            for factor_column in range(2)
            for row in range(5)
            for column in range(5)
        )
        self.assertEqual(exact_metric_trace, DUAL_NORMALIZER)
        self.assertEqual(
            DUAL_NORMALIZER, 1_208_925_819_615_549_701_407_998
        )
        self.assertEqual(len(DUAL_FACTOR), 5)
        self.assertTrue(all(len(row) == 2 for row in DUAL_FACTOR))

    def test_rational_bracket_is_narrow_and_ordered(self) -> None:
        self.assertIsInstance(PRIMAL_LOWER_BOUND, Fraction)
        self.assertIsInstance(DUAL_UPPER_BOUND, Fraction)
        self.assertLess(PRIMAL_LOWER_BOUND, DUAL_UPPER_BOUND)
        relative_width = (
            DUAL_UPPER_BOUND - PRIMAL_LOWER_BOUND
        ) / PRIMAL_LOWER_BOUND
        self.assertLess(float(relative_width), 1.1e-4)

    def test_both_exact_grid_interpretations_are_certified(self) -> None:
        self.assertTrue(self.report["all_requested_grids_certified"])
        self.assertEqual(len(self.report["grid_certificates"]), 2)
        for grid in self.report["grid_certificates"]:
            self.assertEqual(grid["candidate_count"], 120)
            self.assertTrue(grid["certificate_passed"])
            self.assertTrue(grid["primal"]["sylvester_positive_definite"])
            self.assertTrue(
                grid["primal"]["all_declared_minor_margins_verified"]
            )
            self.assertTrue(
                grid["dual"]["all_candidate_constraints_strictly_verified"]
            )
            self.assertTrue(
                grid["dual"]["all_candidate_slacks_above_declared_bound"]
            )
            self.assertEqual(
                grid["dual"]["closest_candidate_index_zero_based"], 62
            )

    def test_every_declared_roundoff_radius_cap_is_verified(self) -> None:
        for grid in self.report["grid_certificates"]:
            for audit in grid["construction_radius_audits"].values():
                self.assertTrue(audit["every_radius_strictly_below_cap"])
            self.assertTrue(
                grid["primal"]["gram_radius_audit"][
                    "every_radius_strictly_below_cap"
                ]
            )
            self.assertTrue(
                grid["primal"]["determinant_radius_audit"][
                    "every_radius_strictly_below_cap"
                ]
            )
            self.assertTrue(
                grid["dual"]["sensitivity_radius_audit"][
                    "every_radius_strictly_below_cap"
                ]
            )

    def test_binary64_grid_is_frozen_by_a_nonempty_digest(self) -> None:
        digest = self.report["computed_binary64_grid_sha256_of_hex_lines"]
        self.assertEqual(digest, BINARY64_GRID_SHA256)
        self.assertTrue(self.report["binary64_grid_digest_matches_declared"])
        self.assertEqual(
            self.report["binary64_endpoint_hex"],
            ["0x1.0624dd2f1a9fcp-10", "0x1.4000000000000p+3"],
        )

    def test_too_little_precision_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            run_interval_certificate(precision_bits=96, grids=("canonical",))


if __name__ == "__main__":
    unittest.main()
