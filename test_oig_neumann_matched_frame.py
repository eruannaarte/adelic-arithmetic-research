from fractions import Fraction
import math
import unittest

from oig_interval_protocol_design import verify_enclosed_design_report
from oig_neumann_matched_frame import (
    finite_modal_response_box,
    run_matched_frame_certificate,
)


class NeumannMatchedFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run_matched_frame_certificate()

    def test_default_two_channel_certificate_closes(self) -> None:
        self.assertTrue(self.report["overall_passed"])
        self.assertEqual(self.report["model"]["active_mode_count"], 172)
        for record in self.report["metric_certificates"]:
            self.assertTrue(record["passed"])
            self.assertGreater(
                Fraction(record["inherited_two_channel_floor_lower_exact"]), 0
            )
            self.assertTrue(
                verify_enclosed_design_report(
                    record["direct_two_channel_enclosed_design"]
                )["passed"]
            )

    def test_matched_frame_loss_is_second_order_tiny(self) -> None:
        l2 = self.report["metric_certificates"][0]
        loss = Fraction(
            l2["matched_frame_loss_certificate"][
                "metric_relative_frame_loss_upper_exact"
            ]
        )
        full_error = Fraction(l2["complete_response_box_error_upper_exact"])
        self.assertLess(loss, Fraction(1, 10**30))
        self.assertLess(loss, full_error)

    def test_rational_h1_metric_majorizes_natural_two_mode_cost(self) -> None:
        n = self.report["model"]["side_length"]
        for mode, majorant in ((1, 11), (2, 41)):
            natural = 1 + 4 * n * n * math.sin(mode * math.pi / (2 * n)) ** 2
            self.assertLess(natural, majorant)

    def test_modal_box_requires_exact_centre_parity(self) -> None:
        with self.assertRaisesRegex(ValueError, "odd"):
            finite_modal_response_box(10)


if __name__ == "__main__":
    unittest.main()
