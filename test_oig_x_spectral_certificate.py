"""Focused tests for the Stage X Arb spectral certificate."""

from __future__ import annotations

import json
import unittest
from fractions import Fraction

from flint import arb_mat

from oig_x_spectral_certificate import (
    FIXED_CHARTS,
    certify_generalized_lower_bound,
    run_spectral_certificate,
)


class TestOIGXSpectralCertificate(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run_spectral_certificate(
            max_band=4,
            precision_bits=224,
            fast=True,
        )

    def test_complete_certificate_passes(self) -> None:
        self.assertTrue(self.report["overall_passed"])
        self.assertTrue(
            self.report["radius_audit"][
                "every_total_radius_strictly_below_cap"
            ]
        )
        json.dumps(self.report, sort_keys=True)

    def test_continuous_scope_is_not_a_parameter_grid(self) -> None:
        scope = self.report["scope"]["continuous_late_atlas"]
        self.assertFalse(scope["parameter_sampling_used_for_lower_bound"])
        self.assertIn("q>=1", scope["resolved"])
        self.assertIn("tau>=1", scope["lattice"])
        self.assertEqual(scope["atomic"], "interior atomic endpoint")
        exclusions = " ".join(
            self.report["scope"]["excluded_from_continuous_claim"]
        )
        self.assertIn("early", exclusions)
        self.assertIn("boundary", exclusions)
        self.assertIn("general lattice", exclusions)

    def test_uniform_generalized_bounds_are_direct(self) -> None:
        rows = self.report["uniform_late_atlas_certificates"]
        self.assertEqual(len(rows), 8)
        for row in rows:
            lower = Fraction(row["atlas_lower_bound_exact"])
            upper = Fraction(row["atlas_upper_bound_exact"])
            self.assertGreater(lower, 0)
            self.assertLess(lower, upper)
            shift = row["common_core_spectral_bracket"][
                "generalized_shift_certificate"
            ]
            self.assertIn("G - L S", shift["method"])
            self.assertTrue(
                shift["every_leading_principal_minor_certainly_positive"]
            )
            self.assertTrue(all(sign == 1 for sign in shift[
                "leading_principal_minor_signs"
            ]))

    def test_every_fixed_chart_has_an_arb_bracket(self) -> None:
        rows = self.report["fixed_chart_certificates"]
        observed = {row["chart"] for row in rows}
        self.assertEqual(observed, set(FIXED_CHARTS))
        self.assertEqual(len(rows), len(FIXED_CHARTS) * 4 * 2)
        for row in rows:
            self.assertTrue(row["passed"])
            self.assertTrue(row["generalized_shift_certificate"]["passed"])
            self.assertTrue(row["rayleigh_upper_certificate"]["passed"])
            self.assertTrue(
                row["comparison"][
                    "mpmath_value_strictly_inside_arb_bracket"
                ]
            )

    def test_effective_rank_is_certified_and_monotone(self) -> None:
        for row in self.report["uniform_late_atlas_certificates"]:
            ranks = row["uniform_effective_rank_lower_bound"]
            self.assertTrue(all(item["certified"] for item in ranks))
            counts = [
                item["generalized_eigenvalues_strictly_above_threshold"]
                for item in ranks
            ]
            self.assertEqual(counts, sorted(counts))
            self.assertTrue(
                all(0 <= count <= row["band_dimension"] for count in counts)
            )

    def test_noise_budget_has_verified_order(self) -> None:
        for row in self.report["uniform_late_atlas_certificates"]:
            budget = row["noise_budget"]
            self.assertTrue(budget["passed"])
            self.assertTrue(budget["sufficient_inequality_verified_in_arb"])
            self.assertLessEqual(
                budget["necessary_uniform_repeats_at_least"],
                budget["sufficient_uniform_repeats_at_most"],
            )

    def test_sylvester_check_rejects_an_invalid_generalized_bound(self) -> None:
        gram = arb_mat([[2, 0], [0, 1]])
        metric = arb_mat([[1, 0], [0, 4]])
        valid = certify_generalized_lower_bound(
            gram, metric, Fraction(1, 5)
        )
        invalid = certify_generalized_lower_bound(
            gram, metric, Fraction(1, 3)
        )
        self.assertTrue(valid["passed"])
        self.assertFalse(invalid["passed"])


if __name__ == "__main__":
    unittest.main()
