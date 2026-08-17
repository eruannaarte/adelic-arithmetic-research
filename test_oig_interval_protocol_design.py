from copy import deepcopy
from fractions import Fraction
import unittest

from oig_interval_protocol_design import (
    EnclosedProtocol,
    design_enclosed_protocols,
    response_box_form_bound,
    verify_enclosed_design_report,
)


class IntervalProtocolDesignTests(unittest.TestCase):
    def test_scalar_box_bound_contains_both_endpoints(self) -> None:
        protocol = EnclosedProtocol.from_rows(
            "scalar", [[2]], [[Fraction(1, 10)]], [[3]]
        )
        record = response_box_form_bound(protocol, [[1]])
        delta = Fraction(
            record["metric_relative_information_error_upper_exact"]
        )
        centre_information = Fraction(12)
        for response in (Fraction(19, 10), Fraction(21, 10)):
            true_information = 3 * response * response
            self.assertLess(abs(true_information - centre_information), delta)

    def test_robust_design_survives_small_response_boxes(self) -> None:
        protocols = (
            EnclosedProtocol.from_rows(
                "first", [[1, 0]], [[Fraction(1, 1000), Fraction(1, 1000)]], [[1]]
            ),
            EnclosedProtocol.from_rows(
                "second", [[0, 1]], [[Fraction(1, 1000), Fraction(1, 1000)]], [[1]]
            ),
        )
        report = design_enclosed_protocols(
            protocols,
            [[1, 0], [0, 1]],
            weight_denominator=10_000,
            exposure_multiplier=10,
        )
        robust = report["response_box_robustness"]
        self.assertTrue(robust["robust_floor_is_positive"])
        self.assertTrue(verify_enclosed_design_report(report)["passed"])
        self.assertIn("robust_noise_performance", robust)

        tampered = deepcopy(report)
        tampered["response_box_robustness"][
            "robust_physical_floor_lower_exact"
        ] = "1/1"
        self.assertFalse(verify_enclosed_design_report(tampered)["passed"])

    def test_zero_radius_has_zero_transfer_cost(self) -> None:
        protocol = EnclosedProtocol.from_rows(
            "exact", [[1, 0], [0, 1]], [[0, 0], [0, 0]], [[1, 0], [0, 1]]
        )
        report = design_enclosed_protocols([protocol], [[1, 0], [0, 1]])
        robust = report["response_box_robustness"]
        self.assertEqual(
            robust["aggregate_metric_relative_information_error_upper_exact"],
            "0/1",
        )

    def test_negative_radius_and_uncertain_blind_quotient_are_rejected(self) -> None:
        invalid = EnclosedProtocol.from_rows(
            "invalid", [[1]], [[-1]], [[1]]
        )
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            response_box_form_bound(invalid, [[1]])

        blind = EnclosedProtocol.from_rows(
            "blind", [[1, 0]], [[0, Fraction(1, 100)]], [[1]]
        )
        with self.assertRaisesRegex(ValueError, "full-rank nominal"):
            design_enclosed_protocols([blind], [[1, 0], [0, 1]])


if __name__ == "__main__":
    unittest.main()
