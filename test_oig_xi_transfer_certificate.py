import unittest

from flint import arb, ctx

import oig_xi_transfer_certificate as xi


class TransferCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_precision = ctx.prec
        ctx.prec = 256
        cls.result = xi.run_certificate(
            max_band=8,
            precision_bits=256,
            maximum_phase_side_length=24,
            include_descriptive=False,
        )

    @classmethod
    def tearDownClass(cls):
        ctx.prec = cls.previous_precision

    def test_complete_certificate_passes(self):
        self.assertTrue(self.result["overall_passed"])
        self.assertTrue(self.result["phase_grid_certificate"]["passed"])
        self.assertTrue(
            self.result["full_neumann_small_grid_certificate"]["passed"]
        )

    def test_phase_grid_first_crossings_are_stable(self):
        expected = {
            ("L2", 1): 5,
            ("H1", 1): 5,
            ("L2", 2): 8,
            ("H1", 2): 8,
            ("L2", 3): 10,
            ("H1", 3): 10,
            ("L2", 4): 12,
            ("H1", 4): 12,
            ("L2", 5): 13,
            ("H1", 5): 14,
            ("L2", 6): 15,
            ("H1", 6): 16,
            ("L2", 7): 17,
            ("H1", 7): 18,
            ("L2", 8): 18,
            ("H1", 8): 19,
        }
        rows = self.result["phase_grid_certificate"]["rows"]
        observed = {
            (row["metric"], row["band_dimension"]): row[
                "first_certified_side_length_in_sequential_search"
            ]["side_length"]
            for row in rows
        }
        self.assertEqual(observed, expected)
        for row in rows:
            first = row["first_certified_side_length_in_sequential_search"]
            self.assertTrue(first["strictly_below_stage_x_floor"])
            self.assertGreater(first["transferred_finite_floor_approx"], 0.0)
            if row["immediate_predecessor"] is not None:
                self.assertFalse(
                    row["immediate_predecessor"][
                        "strictly_below_stage_x_floor"
                    ]
                )

    def test_full_neumann_first_complete_crossing_is_n7(self):
        result = self.result["full_neumann_small_grid_certificate"]
        self.assertEqual(result["first_certified_side_length_in_tested_sequence"], 7)
        for record in result["records"][:-1]:
            self.assertFalse(record["strictly_below_stage_x_floor"])
        self.assertTrue(result["records"][-1]["strictly_below_stage_x_floor"])
        self.assertGreater(
            result["records"][-1]["transferred_finite_floor_approx"], 0.0
        )
        self.assertEqual(
            [
                row["first_certified_side_length_in_tested_sequence"]
                for row in result["metric_certificates"]
            ],
            [7, 7],
        )

    def test_error_bound_is_metric_relative_and_symmetric(self):
        continuum = xi.continuum_lattice_gram(3, 256)
        finite = xi.phase_midpoint_gram(10, 3)
        for row in range(3):
            for column in range(3):
                self.assertEqual(
                    continuum[row, column].str(50, radius=True),
                    continuum[column, row].str(50, radius=True),
                )
                self.assertEqual(
                    finite[row, column].str(50, radius=True),
                    finite[column, row].str(50, radius=True),
                )
        l2 = xi.metric_relative_row_sum_bound(finite, continuum, "L2")
        h1 = xi.metric_relative_row_sum_bound(finite, continuum, "H1")
        self.assertTrue(bool(l2 > 0))
        self.assertTrue(bool(h1 > 0))
        self.assertTrue(bool(h1 < l2))

    def test_negative_controls_reject_shortcuts(self):
        controls = self.result["negative_controls"]
        self.assertTrue(controls["passed"])
        self.assertTrue(controls["coarse_grid_rejected"])
        self.assertTrue(controls["entrywise_max_is_not_the_operator_bound"])
        self.assertTrue(controls["full_model_not_inferred_from_phase_grid"])
        self.assertTrue(controls["binary64_not_used_for_certificate"])

    def test_precision_repetition_preserves_hardest_crossing(self):
        previous = ctx.prec
        try:
            ctx.prec = 320
            continuum = xi.continuum_lattice_gram(8, 320)
            finite = xi.phase_midpoint_gram(18, 8)
            delta = xi.metric_relative_row_sum_bound(finite, continuum, "L2")
            self.assertTrue(bool(delta < xi._q(xi.STAGE_X_LOWER_BOUNDS["L2"][7])))
            predecessor = xi.phase_midpoint_gram(17, 8)
            previous_delta = xi.metric_relative_row_sum_bound(
                predecessor, continuum, "L2"
            )
            self.assertFalse(
                bool(previous_delta < xi._q(xi.STAGE_X_LOWER_BOUNDS["L2"][7]))
            )
        finally:
            ctx.prec = previous

    def test_descriptive_full_model_is_labelled_and_not_promoted(self):
        descriptive = xi.full_neumann_descriptive((31, 63))
        self.assertIn("descriptive evidence only", descriptive["role"])
        records = descriptive["records"]
        self.assertGreater(records[0]["binary64_delta"], records[1]["binary64_delta"])
        self.assertFalse(records[0]["appears_below_floor"])

    def test_guards(self):
        with self.assertRaises(ValueError):
            xi.phase_midpoint_gram(2, 2)
        with self.assertRaises(ValueError):
            xi.metric_relative_row_sum_bound(
                xi.phase_midpoint_gram(3, 1),
                xi.continuum_lattice_gram(1, 256),
                "bad",
            )
        with self.assertRaises(ValueError):
            xi.run_certificate(max_band=9, include_descriptive=False)
        with self.assertRaises(ValueError):
            xi.run_certificate(precision_bits=80, include_descriptive=False)


if __name__ == "__main__":
    unittest.main()
