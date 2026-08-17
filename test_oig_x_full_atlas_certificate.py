"""Tests for the rigorous OIG X K=2 full-atlas certificate."""

from fractions import Fraction
import unittest

from oig_x_full_atlas_certificate import (
    BOUNDARY_MASS_FLOOR,
    DEFAULT_KAPPA_BOXES_PER_UNIT,
    GLOBAL_LOWER_BOUND,
    GLOBAL_UPPER_BOUND,
    KAPPA_TAIL,
    PIVOT_ORDERS,
    SOURCE_METRIC,
    ramp_scaling_audit,
    run_certificate,
)


class OIGXFullAtlasCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = run_certificate()

    def test_complete_certificate_closes(self):
        self.assertTrue(self.report["verified"])
        self.assertIn(
            "no finite-grid transfer error",
            self.report["scope"],
        )
        self.assertEqual(
            self.report["proof_method"][
                "all_sign_decisions_use_arb_or_exact_rationals"
            ],
            True,
        )
        self.assertTrue(
            self.report["proof_method"]["no_sampled_eigenvalue_inference"]
        )

    def test_exact_basis_metric_and_pivots_are_declared(self):
        model = self.report["model"]
        self.assertEqual(model["dimension"], 2)
        self.assertEqual(model["modulation"], "V(x)=1+(4/5)x")
        self.assertEqual(tuple(model["moment_pivot_orders"]), PIVOT_ORDERS)
        self.assertEqual(
            tuple(tuple(row) for row in model["source_metric"]),
            SOURCE_METRIC,
        )
        self.assertEqual(model["analytic_null_on_source_space"], "zero")

    def test_every_chart_has_a_verified_lower_bound(self):
        self.assertTrue(
            self.report["early_resolved"]["verified_above_global_lower"]
        )
        self.assertTrue(
            self.report["late_charts"]["resolved"][
                "verified_above_global_lower"
            ]
        )
        self.assertTrue(
            self.report["late_charts"]["lattice"][
                "verified_above_global_lower"
            ]
        )
        self.assertTrue(
            self.report["atomic_boundary"]["verified_above_global_lower"]
        )

    def test_boundary_cover_has_no_parameter_gap(self):
        cover = self.report["boundary_mass_cover"]
        expected_per_interval = (
            int(KAPPA_TAIL) * DEFAULT_KAPPA_BOXES_PER_UNIT
        )
        self.assertTrue(cover["verified"])
        self.assertEqual(
            cover["total_boxes_checked"],
            2 * expected_per_interval,
        )
        self.assertEqual(
            cover["mass_floor"],
            f"{BOUNDARY_MASS_FLOOR.numerator}/"
            f"{BOUNDARY_MASS_FLOOR.denominator}",
        )
        for row in cover["intervals"]:
            self.assertEqual(row["finite_cover"], ["0", "3/1"])
            self.assertEqual(row["box_count"], expected_per_interval)
            self.assertTrue(row["verified_above_mass_floor"])
            self.assertGreater(
                row["weakest_box_lower_descriptive"],
                float(BOUNDARY_MASS_FLOOR),
            )

    def test_exact_two_sided_bracket_is_reported(self):
        bracket = self.report["generalized_floor"]
        self.assertEqual(
            bracket["lower"],
            f"{GLOBAL_LOWER_BOUND.numerator}/"
            f"{GLOBAL_LOWER_BOUND.denominator}",
        )
        self.assertEqual(
            bracket["upper"],
            f"{GLOBAL_UPPER_BOUND.numerator}/"
            f"{GLOBAL_UPPER_BOUND.denominator}",
        )
        self.assertLess(GLOBAL_LOWER_BOUND, GLOBAL_UPPER_BOUND)
        self.assertTrue(
            self.report["upper_witness"]["verified_below_global_upper"]
        )
        self.assertEqual(
            self.report["upper_witness"]["source_vector"],
            [1, -15],
        )
        self.assertEqual(
            self.report["upper_witness"]["source_metric_norm_squared"],
            226,
        )

    def test_ramp_degeneracy_exponents_are_exact(self):
        scaling = ramp_scaling_audit()
        self.assertEqual(scaling["moment_determinant_power_in_g"], 3)
        self.assertEqual(
            scaling["endpoint_gram_determinant_power_in_g"],
            6,
        )

    def test_precision_and_cover_guards(self):
        with self.assertRaises(ValueError):
            run_certificate(precision_bits=96)
        with self.assertRaises(ValueError):
            run_certificate(kappa_boxes_per_unit=192)

    def test_certificate_repeats_at_higher_precision(self):
        repeated = run_certificate(
            precision_bits=256,
            kappa_boxes_per_unit=128,
        )
        self.assertTrue(repeated["verified"])
        self.assertEqual(
            repeated["generalized_floor"],
            self.report["generalized_floor"],
        )
        self.assertEqual(
            repeated["boundary_mass_cover"]["total_boxes_checked"],
            2 * int(KAPPA_TAIL) * 128,
        )


if __name__ == "__main__":
    unittest.main()
