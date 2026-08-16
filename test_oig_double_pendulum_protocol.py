from copy import deepcopy
from fractions import Fraction
import unittest
from unittest.mock import patch

import numpy as np

from oig_double_pendulum_protocol import (
    DeclaredPendulumResponseBox,
    PendulumProtocolCandidate,
    SOURCE_COORDINATES,
    TIER1_BOUNDARY,
    build_canonical_double_pendulum_protocol_report,
    common_mass_scale_blindness_control,
    declare_box_from_tier1,
    design_declared_double_pendulum_protocols,
    discover_candidate_response,
    verify_double_pendulum_protocol_report,
)


class DoublePendulumProtocolAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        launch = [Fraction(4, 5), Fraction(-7, 20), 0, 0]
        cls.first = PendulumProtocolCandidate.from_values(
            "launch-A / theta-1 / tau-1", launch, "theta_1", 1
        )
        cls.second = PendulumProtocolCandidate.from_values(
            "launch-A / theta-2 / tau-1", launch, "theta_2", 1
        )
        cls.discoveries = (
            discover_candidate_response(cls.first),
            discover_candidate_response(cls.second),
        )
        cls.boxes = tuple(
            declare_box_from_tier1(candidate, discovery)
            for candidate, discovery in zip(
                (cls.first, cls.second), cls.discoveries
            )
        )
        cls.report = design_declared_double_pendulum_protocols(
            cls.boxes,
            tier1_discoveries=cls.discoveries,
            weight_denominator=2_000,
            dual_vector_scale=20_000,
            exposure_multiplier=4,
        )

    def test_candidate_is_an_explicit_launch_sensor_time_triple(self) -> None:
        record = self.first.declaration()
        self.assertEqual(
            record["launch"]["state_exact"],
            ["4/5", "-7/20", "0/1", "0/1"],
        )
        self.assertEqual(record["sensor"]["name"], "theta_1")
        self.assertEqual(
            record["observation_time"]["dimensionless_tau_exact"], "1/1"
        )
        with self.assertRaisesRegex(ValueError, "unknown sensor"):
            PendulumProtocolCandidate.from_values("bad", [0, 0, 0, 0], "energy", 1)
        with self.assertRaisesRegex(ValueError, "positive"):
            PendulumProtocolCandidate.from_values("bad", [0, 0, 0, 0], "theta_1", 0)
        with self.assertRaisesRegex(TypeError, "binary floating"):
            PendulumProtocolCandidate.from_values("bad", [0.1, 0, 0, 0], "theta_1", 1)

    def test_finite_difference_and_refinement_are_tier1_only(self) -> None:
        discovery = self.discoveries[0]
        self.assertEqual(discovery["claim_tier"], 1)
        self.assertEqual(discovery["source_coordinates"], list(SOURCE_COORDINATES))
        self.assertEqual(discovery["proof_boundary"], TIER1_BOUNDARY)
        self.assertIn("neither enclose", TIER1_BOUNDARY)
        self.assertTrue(
            np.all(np.isfinite(discovery["selected_tier1_response_estimate"]))
        )
        self.assertTrue(
            np.all(np.asarray(discovery["max_refinement_spread_by_source"]) >= 0)
        )
        box = self.boxes[0]
        variants = self.discoveries[0]["response_estimates"]
        for row in variants.values():
            for value, centre, radius in zip(
                row, box.response_centre, box.response_radius
            ):
                self.assertLessEqual(abs(Fraction(str(value)) - centre), radius)

    def test_common_mass_scale_is_a_blind_control_not_a_source(self) -> None:
        control = common_mass_scale_blindness_control(self.first)
        self.assertEqual(
            control["expected_exact_response_in_common_scale_direction"], "0/1"
        )
        self.assertLess(abs(control["central_finite_difference"]), 1.0e-10)
        self.assertNotIn("common_mass_scale", " ".join(SOURCE_COORDINATES))
        exact_control = self.report["common_mass_scale_blindness_control"]
        self.assertEqual(
            exact_control["extended_source_control_vector_exact"],
            ["0/1", "0/1", "1/1"],
        )
        self.assertTrue(
            all(
                row["response_on_control_exact"] == ["0/1"]
                for row in exact_control["candidate_actions_exact"]
            )
        )

    def test_exact_engine_is_conditional_on_declared_rational_boxes(self) -> None:
        robust = self.report["exact_enclosed_design"]["response_box_robustness"]
        self.assertTrue(robust["robust_floor_is_positive"])
        self.assertTrue(
            self.report["conditional_claim"][
                "exact_design_is_conditional_on_box_membership"
            ]
        )
        self.assertFalse(
            self.report["conditional_claim"][
                "double_pendulum_ode_membership_certified"
            ]
        )
        self.assertTrue(
            self.report["independent_verification"]["exact_enclosed_design_verified"]
        )
        self.assertFalse(
            self.report["independent_verification"][
                "double_pendulum_ode_membership_verified"
            ]
        )

    def test_standalone_verifier_uses_no_ode_and_rejects_boundary_tampering(self) -> None:
        forbidden = AssertionError(
            "the exact verifier must not solve the ODE or use a floating eigensolver"
        )
        with (
            patch(
                "oig_double_pendulum_protocol.simulate_double_pendulum",
                side_effect=forbidden,
            ),
            patch("oig_interval_protocol_design.eigh", side_effect=forbidden),
            patch("oig_protocol_design_engine.eigh", side_effect=forbidden),
        ):
            verification = verify_double_pendulum_protocol_report(self.report)
        self.assertTrue(verification["passed"])
        self.assertFalse(verification["double_pendulum_ode_membership_verified"])

        tampered = deepcopy(self.report)
        tampered["conditional_claim"][
            "double_pendulum_ode_membership_certified"
        ] = True
        self.assertFalse(verify_double_pendulum_protocol_report(tampered)["passed"])

        tampered = deepcopy(self.report)
        tampered["candidate_response_boxes"][0]["response_radius_exact"][0][0] = "0/1"
        self.assertFalse(verify_double_pendulum_protocol_report(tampered)["passed"])

    def test_blind_or_negative_box_declarations_are_not_smuggled_into_design(self) -> None:
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            DeclaredPendulumResponseBox.from_values(
                self.first, [1, 0], [Fraction(-1, 10), 0]
            )
        blind = (
            DeclaredPendulumResponseBox.from_values(self.first, [1, 0], [0, 0]),
            DeclaredPendulumResponseBox.from_values(self.second, [2, 0], [0, 0]),
        )
        with self.assertRaisesRegex(ValueError, "full-rank nominal"):
            design_declared_double_pendulum_protocols(blind)

    def test_canonical_library_really_selects_launches_sensors_and_times(self) -> None:
        report = build_canonical_double_pendulum_protocol_report()
        rows = report["exact_enclosed_design"]["protocols"]
        active = [row for row in rows if Fraction(row["budget_share_exact"]) > 0]
        launch_names = {row["name"].split(" / ")[0] for row in active}
        self.assertGreaterEqual(len(launch_names), 2)
        self.assertGreaterEqual(len(active), 2)
        self.assertTrue(
            report["exact_enclosed_design"]["response_box_robustness"][
                "robust_floor_is_positive"
            ]
        )


if __name__ == "__main__":
    unittest.main()
    build_canonical_double_pendulum_protocol_report,
