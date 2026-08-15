from fractions import Fraction
import unittest

from oig_protocol_design_engine import (
    RationalProtocol,
    certify_frame_loss,
    design_protocols,
    exact_observable_quotient,
    exponential_time_response,
    information_matrix,
    rational_matrix,
    verify_design_report,
    verify_frame_loss_report,
)
from oig_hidden_network_protocol_demo import run_demo


class ProtocolDesignEngineTests(unittest.TestCase):
    def test_noise_precision_enters_information_exactly(self) -> None:
        protocol = RationalProtocol.from_rows(
            "scaled sensor",
            [[0, 2, 0]],
            [[Fraction(1, 4)]],
        )
        self.assertEqual(
            information_matrix(protocol),
            rational_matrix([[0, 0, 0], [0, 1, 0], [0, 0, 0]]),
        )

    def test_exact_quotient_removes_common_blind_direction(self) -> None:
        protocols = [
            RationalProtocol.from_rows("first", [[1, 0, 0]], [[1]]),
            RationalProtocol.from_rows("second", [[0, 2, 0]], [[Fraction(1, 4)]]),
        ]
        quotient = exact_observable_quotient(
            protocols,
            rational_matrix([[1, 0, 0], [0, 4, 0], [0, 0, 9]]),
        )
        self.assertEqual(len(quotient.source_metric), 2)
        self.assertEqual(quotient.source_metric, rational_matrix([[1, 0], [0, 4]]))
        self.assertEqual(
            quotient.injection,
            rational_matrix([[1, 0], [0, 1], [0, 0]]),
        )

    def test_single_isometric_protocol_has_exact_unit_bracket(self) -> None:
        protocol = RationalProtocol.from_rows(
            "complete finite frame",
            [[1, 0, 0], [0, 2, 0]],
            [[1, 0], [0, 1]],
        )
        report = design_protocols(
            [protocol],
            [[1, 0, 0], [0, 4, 0], [0, 0, 9]],
            weight_denominator=100,
        )
        self.assertTrue(report["overall_passed"])
        self.assertEqual(report["exact_blind_dimension"], 1)
        self.assertEqual(report["protocols"][0]["budget_share_exact"], "1/1")
        self.assertEqual(report["certificate"]["dual_optimum_upper_exact"], "1/1")
        lower = Fraction(report["certificate"]["primal_generalized_floor_lower_exact"])
        self.assertGreater(lower, Fraction(99, 100))
        self.assertLess(lower, 1)
        self.assertTrue(verify_design_report(report)["passed"])

    def test_cost_aware_design_balances_generalized_directions(self) -> None:
        protocols = [
            RationalProtocol.from_rows("cheap first", [[1, 0, 0]], [[1]], cost=1),
            RationalProtocol.from_rows("second", [[0, 2, 0]], [[Fraction(1, 4)]], cost=1),
        ]
        report = design_protocols(
            protocols,
            [[1, 0, 0], [0, 4, 0], [0, 0, 9]],
            weight_denominator=10_000,
        )
        shares = [Fraction(row["budget_share_exact"]) for row in report["protocols"]]
        self.assertEqual(sum(shares), 1)
        self.assertLess(abs(shares[0] - Fraction(1, 5)), Fraction(1, 1000))
        self.assertLess(abs(shares[1] - Fraction(4, 5)), Fraction(1, 1000))
        floor = Fraction(report["certificate"]["primal_generalized_floor_lower_exact"])
        self.assertGreater(floor, Fraction(19, 100))
        self.assertTrue(report["certificate"]["budget_exactly_one"])
        self.assertGreater(
            Fraction(report["certificate"]["certified_efficiency_lower_exact"]),
            Fraction(19, 100),
        )

    def test_frame_loss_is_an_exact_metric_relative_form_bound(self) -> None:
        record = certify_frame_loss(
            [[2, 0], [0, 1]],
            [[Fraction(3, 2), 0], [0, Fraction(3, 4)]],
            [[1, 0], [0, 1]],
            inherited_floor=1,
        )
        loss = Fraction(record["frame_loss_upper_exact"])
        self.assertGreater(loss, Fraction(1, 2))
        self.assertLess(loss, Fraction(51, 100))
        self.assertTrue(record["frame_preserves_positive_floor"])
        self.assertEqual(
            Fraction(record["transferred_form_bound_exact"]),
            1 - loss,
        )
        self.assertTrue(verify_frame_loss_report(record)["passed"])
        tampered = dict(record)
        tampered["sensed_information_exact"] = [["0/1", "0/1"], ["0/1", "0/1"]]
        self.assertFalse(verify_frame_loss_report(tampered)["passed"])
        negative = certify_frame_loss(
            [[2, 0], [0, 1]],
            [[0, 0], [0, 0]],
            [[1, 0], [0, 1]],
            inherited_floor="1/10",
        )
        self.assertLess(Fraction(negative["transferred_form_bound_exact"]), 0)
        self.assertFalse(negative["frame_preserves_positive_floor"])

    def test_all_blind_and_invalid_noise_models_are_rejected(self) -> None:
        blind = RationalProtocol.from_rows("blind", [[0, 0]], [[1]])
        with self.assertRaisesRegex(ValueError, "exactly blind"):
            exact_observable_quotient([blind], rational_matrix([[1, 0], [0, 1]]))

        invalid = RationalProtocol.from_rows("invalid", [[1, 0]], [[0]])
        with self.assertRaisesRegex(ValueError, "positive definite"):
            design_protocols([invalid], [[1, 0], [0, 1]])
        with self.assertRaisesRegex(TypeError, "not exact declarations"):
            RationalProtocol.from_rows("float", [[0.1, 0]], [[1]])

    def test_noise_consequence_has_exact_and_descriptive_bounds(self) -> None:
        protocol = RationalProtocol.from_rows("complete", [[1, 0], [0, 1]], [[1, 0], [0, 1]])
        report = design_protocols(
            [protocol],
            [[1, 0], [0, 1]],
            amplitude=2,
            exposure_multiplier=16,
        )
        noise = report["noise_performance"]["approximate_design_measure"]
        self.assertIn("certified", noise["role"])
        self.assertLess(noise["descriptive_exact_gaussian_error"], 1e-4)
        self.assertLess(
            Fraction(noise["gaussian_error_rational_upper_exact"]),
            Fraction(1, 10),
        )
        with self.assertRaisesRegex(ValueError, "noise parameters"):
            design_protocols([protocol], [[1, 0], [0, 1]], amplitude="-1")
        with self.assertRaisesRegex(ValueError, "noise parameters"):
            design_protocols(
                [protocol],
                [[1, 0], [0, 1]],
                exposure_multiplier=Fraction(3, 2),  # type: ignore[arg-type]
            )

    def test_exponential_time_ctmc_response_is_exact(self) -> None:
        response = exponential_time_response(
            [[1, -1], [-1, 1]],
            [[1], [-1]],
            [[1, 0]],
            1,
        )
        self.assertEqual(response, rational_matrix([[Fraction(1, 3)]]))

        with self.assertRaisesRegex(ValueError, "conserve total mass"):
            exponential_time_response(
                [[1, 0], [0, 1]],
                [[1], [-1]],
                [[1, 0]],
                1,
            )
        with self.assertRaisesRegex(ValueError, "nonpositive off-diagonal"):
            exponential_time_response(
                [[-1, 1], [1, -1]],
                [[1], [-1]],
                [[1, 0]],
                1,
            )

    def test_nonreversible_hidden_network_demo_is_certified(self) -> None:
        report = run_demo(100_000)
        self.assertTrue(report["overall_passed"])
        self.assertEqual(report["observable_quotient_dimension"], 3)
        self.assertEqual(report["exact_blind_dimension"], 0)
        self.assertTrue(report["benchmark"]["laplacian_is_non_symmetric"])
        lower = Fraction(report["certificate"]["primal_generalized_floor_lower_exact"])
        upper = Fraction(report["certificate"]["dual_optimum_upper_exact"])
        self.assertLess(upper, Fraction(21, 20) * lower)
        self.assertTrue(verify_design_report(report)["passed"])
        report["certificate"]["primal_generalized_floor_lower_exact"] = "1/1"
        self.assertFalse(verify_design_report(report)["passed"])


if __name__ == "__main__":
    unittest.main()
