"""Artifact-level audit for the canonical double-pendulum OIG design."""

from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from oig_double_pendulum_protocol import (
    SOURCE_COORDINATES,
    TIER1_BOUNDARY,
    canonical_protocol_candidates,
    verify_double_pendulum_protocol_report,
)


ARTIFACT = (
    Path(__file__).resolve().parent
    / "artifacts"
    / "double_pendulum_protocol_design_conditional.json"
)


class DoublePendulumProtocolArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_artifact_pins_the_full_seven_candidate_library(self) -> None:
        expected = [candidate.declaration() for candidate in canonical_protocol_candidates()]
        boxes = self.report["candidate_response_boxes"]
        discoveries = self.report["tier1_discovery_only"]
        self.assertEqual(len(boxes), 7)
        self.assertEqual(len(discoveries), 7)
        self.assertEqual([row["candidate"] for row in boxes], expected)
        self.assertEqual([row["candidate"] for row in discoveries], expected)
        self.assertTrue(
            all(row["source_coordinates"] == list(SOURCE_COORDINATES) for row in boxes)
        )
        self.assertTrue(
            all(
                row["claim_tier"] == 1
                and row["proof_boundary"] == TIER1_BOUNDARY
                for row in discoveries
            )
        )

    def test_exact_design_selects_two_specific_multi_launch_protocols(self) -> None:
        rows = self.report["exact_enclosed_design"]["protocols"]
        active = [row for row in rows if Fraction(row["budget_share_exact"]) > 0]
        self.assertEqual(
            [
                (
                    row["name"],
                    row["budget_share_exact"],
                    row["cost_exact"],
                    row["physical_weight_exact"],
                )
                for row in active
            ],
            [
                (
                    "launch-A / theta-2 / tau-1",
                    "4589/10000",
                    "1/1",
                    "4589/10000",
                ),
                (
                    "launch-B / scaled-omega-1 / tau-5/4",
                    "5411/10000",
                    "5/4",
                    "5411/12500",
                ),
            ],
        )
        self.assertEqual(
            sum(Fraction(row["budget_share_exact"]) for row in rows), Fraction(1)
        )
        self.assertEqual(
            {row["name"].split(" / ")[0] for row in active},
            {"launch-A", "launch-B"},
        )

        declarations = {
            row["candidate"]["name"]: row["candidate"]
            for row in self.report["candidate_response_boxes"]
        }
        first = declarations[active[0]["name"]]
        second = declarations[active[1]["name"]]
        self.assertEqual(first["launch"]["state_exact"], ["4/5", "-7/20", "0/1", "0/1"])
        self.assertEqual(first["sensor"]["name"], "theta_2")
        self.assertEqual(first["observation_time"]["dimensionless_tau_exact"], "1/1")
        self.assertEqual(second["launch"]["state_exact"], ["-3/5", "9/10", "0/1", "0/1"])
        self.assertEqual(second["sensor"]["name"], "scaled_omega_1")
        self.assertEqual(second["observation_time"]["dimensionless_tau_exact"], "5/4")

    def test_artifact_verifies_exactly_without_replaying_tier1_numerics(self) -> None:
        forbidden = AssertionError("artifact verification must remain exact-only")
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
        self.assertEqual(verification["candidate_count"], 7)
        self.assertTrue(verification["exact_enclosed_design_verified"])
        self.assertFalse(verification["tier1_numerics_recomputed"])
        self.assertFalse(verification["double_pendulum_ode_membership_verified"])

    def test_positive_floor_is_only_conditional_on_the_declared_boxes(self) -> None:
        conditional = self.report["conditional_claim"]
        self.assertEqual(
            conditional,
            {
                "double_pendulum_ode_membership_certified": False,
                "exact_design_is_conditional_on_box_membership": True,
                "response_boxes_are_declared_assumptions": True,
                "tier1_discovery_promoted_to_enclosure": False,
            },
        )
        robust = self.report["exact_enclosed_design"]["response_box_robustness"]
        self.assertTrue(robust["robust_floor_is_positive"])
        self.assertEqual(
            robust["robust_physical_floor_lower_exact"],
            "195932905640268820789/2500000000000000000000",
        )
        self.assertGreater(Fraction(robust["robust_physical_floor_lower_exact"]), 0)
        self.assertIn("does not certify", robust["proof_boundary"])

        control = self.report["common_mass_scale_blindness_control"]
        self.assertEqual(control["declared_exact_response_column"], "0/1")
        self.assertEqual(len(control["candidate_actions_exact"]), 7)
        self.assertTrue(
            all(
                row["response_on_control_exact"] == ["0/1"]
                for row in control["candidate_actions_exact"]
            )
        )

    def test_artifact_boundary_tampering_is_rejected(self) -> None:
        tampered = deepcopy(self.report)
        tampered["conditional_claim"]["double_pendulum_ode_membership_certified"] = True
        self.assertFalse(verify_double_pendulum_protocol_report(tampered)["passed"])

        tampered = deepcopy(self.report)
        tampered["candidate_response_boxes"][4]["candidate"]["sensor"]["name"] = "theta_1"
        self.assertFalse(verify_double_pendulum_protocol_report(tampered)["passed"])


if __name__ == "__main__":
    unittest.main()
