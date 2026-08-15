import math
import unittest
from fractions import Fraction

from flint import ctx

import oig_xi_transfer_certificate as xi
import oig_xii_two_port_certificate as xii


class TwoPortFiniteTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_precision = ctx.prec
        cls.result_192 = xii.run_certificate(
            precision_bits=192,
            taylor_degree=32,
        )

    @classmethod
    def tearDownClass(cls):
        ctx.prec = cls.previous_precision

    def test_both_metric_certificates_pass(self):
        result = self.result_192
        self.assertTrue(result["overall_passed"])
        self.assertEqual(
            [row["metric"] for row in result["metric_certificates"]],
            ["L2", "H1"],
        )
        self.assertTrue(all(row["passed"] for row in result["metric_certificates"]))

    def test_exact_adjacent_odd_grid_crossings(self):
        expected = {"L2": (343, 345), "H1": (647, 649)}
        for certificate in self.result_192["metric_certificates"]:
            predecessor, success = certificate["records"]
            self.assertEqual(
                (predecessor["side_length"], success["side_length"]),
                expected[certificate["metric"]],
            )
            self.assertEqual(success["side_length"] - predecessor["side_length"], 2)
            self.assertTrue(predecessor["rayleigh_strictly_above_stage_x_floor"])
            self.assertTrue(success["strictly_below_stage_x_floor"])
            self.assertGreater(
                Fraction(success["transferred_finite_floor_exact"]),
                0,
            )

    def test_stage_x_floors_are_carried_as_exact_rationals(self):
        for certificate in self.result_192["metric_certificates"]:
            metric = certificate["metric"]
            self.assertEqual(
                Fraction(certificate["stage_x_late_core_floor_exact"]),
                xi.STAGE_X_LOWER_BOUNDS[metric][1],
            )

    def test_predecessors_are_rejected_by_rayleigh_lower_bounds(self):
        expected_vectors = {"L2": [4, 1], "H1": [8, 1]}
        for certificate in self.result_192["metric_certificates"]:
            floor = Fraction(certificate["stage_x_late_core_floor_exact"])
            predecessor = certificate["records"][0]
            self.assertEqual(
                predecessor["rayleigh_vector"],
                expected_vectors[certificate["metric"]],
            )
            self.assertGreater(
                Fraction(predecessor["rayleigh_abs_lower_exact"]),
                floor,
            )

    def test_exact_two_by_two_norm_is_essential_control(self):
        controls = self.result_192["negative_controls"]
        self.assertTrue(controls["row_sum_fails_where_exact_2x2_norm_succeeds"])
        self.assertTrue(controls["entrywise_max_fails_where_rayleigh_rejects"])
        for certificate in self.result_192["metric_certificates"]:
            floor = Fraction(certificate["stage_x_late_core_floor_exact"])
            predecessor = certificate["records"][0]
            success = certificate["records"][1]
            self.assertLess(
                Fraction(predecessor["absolute_entry_max_upper_exact"]),
                floor,
            )
            self.assertTrue(predecessor["entrywise_max_would_false_certify"])
            self.assertGreater(
                Fraction(success["absolute_row_sum_upper_exact"]),
                floor,
            )
            self.assertLess(
                Fraction(success["spectral_norm_upper_exact"]),
                floor,
            )

    def test_centered_taylor_tail_is_exact_and_decreases(self):
        tail32 = xii.centered_taylor_operator_tail(32)
        self.assertEqual(
            tail32,
            Fraction(18, 5) ** 33 / math.factorial(33),
        )
        self.assertGreater(tail32, 0)
        self.assertLess(xii.centered_taylor_operator_tail(33), tail32)
        for certificate in self.result_192["metric_certificates"]:
            for record in certificate["records"]:
                self.assertEqual(Fraction(record["operator_tail_exact"]), tail32)

    def test_small_grid_agrees_with_direct_arb_matrix_exponential(self):
        previous = ctx.prec
        try:
            ctx.prec = 256
            taylor, trace = xii.finite_neumann_two_port_gram(5, 32)
            direct = xi._finite_neumann_gram_arb(5, 2)
            self.assertEqual(trace["target_modes_retained"], 2)
            for row in range(2):
                for column in range(2):
                    self.assertTrue(taylor[row][column].overlaps(direct[row, column]))
        finally:
            ctx.prec = previous

    def test_precision_repetition_preserves_both_decisions(self):
        repeated = xii.run_certificate(
            precision_bits=256,
            taylor_degree=32,
        )
        self.assertTrue(repeated["overall_passed"])
        for low, high in zip(
            self.result_192["metric_certificates"],
            repeated["metric_certificates"],
        ):
            self.assertEqual(low["metric"], high["metric"])
            self.assertTrue(high["records"][0]["rayleigh_strictly_above_stage_x_floor"])
            self.assertTrue(high["records"][1]["strictly_below_stage_x_floor"])
            self.assertAlmostEqual(
                low["records"][1]["spectral_norm_upper_approx"],
                high["records"][1]["spectral_norm_upper_approx"],
                places=18,
            )

    def test_scope_and_proof_boundary_are_explicit(self):
        result = self.result_192
        self.assertIn("one-cell lattice point tau=1", result["scope_boundary"])
        self.assertIn("not a full-atlas", result["scope_boundary"])
        self.assertTrue(result["proof_method"]["binary64_decides_no_inequality"])
        self.assertTrue(result["negative_controls"]["noncommuting_generator_retained"])
        for certificate in result["metric_certificates"]:
            for record in certificate["records"]:
                self.assertIn("even only", record["target_mode_parity"])

    def test_guards(self):
        with self.assertRaises(ValueError):
            xii.finite_neumann_two_port_gram(344, 32)
        with self.assertRaises(ValueError):
            xii.centered_taylor_operator_tail(0)
        with self.assertRaises(ValueError):
            xii.run_certificate(precision_bits=80)
        with self.assertRaises(ValueError):
            xii.run_certificate(taylor_degree=12)
        with self.assertRaises(ValueError):
            xii.run_certificate(l2_predecessor=345, l2_successful_grid=343)


if __name__ == "__main__":
    unittest.main()
