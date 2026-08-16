"""Regression checks for the committed double-pendulum research artifacts."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import unittest

from oig_double_pendulum_lab import verify_atlas_lab_report
from oig_double_pendulum_grouped_protocol import verify_grouped_protocol_report
from oig_double_pendulum_grouped_validated_transfer import (
    verify_grouped_physical_clock_floor_certificate,
)
from oig_double_pendulum_parameter_sensitivity import (
    verify_parameter_sensitivity_report,
)
from oig_double_pendulum_persistence import verify_persistence_report
from oig_double_pendulum_protocol import verify_double_pendulum_protocol_report
from oig_double_pendulum_render import render_atlas_svg
from oig_double_pendulum_structured_nuisance import (
    verify_structured_physical_nuisance_report,
)
from oig_double_pendulum_validated_transfer import (
    verify_physical_positive_floor_certificate,
)
from oig_double_pendulum_variational_atlas import (
    verify_variational_angle_slice_atlas_report,
)


ROOT = Path(__file__).resolve().parent
ATLAS_PATH = ROOT / "artifacts" / "double_pendulum_operational_atlas_stage1.json"
PROTOCOL_PATH = (
    ROOT / "artifacts" / "double_pendulum_protocol_design_conditional.json"
)
SVG_PATH = ROOT / "artifacts" / "double_pendulum_operational_atlas_stage1.svg"
PERSISTENCE_PATH = (
    ROOT / "artifacts" / "double_pendulum_persistence_13x13_t4_tier1.json"
)
PERSISTENCE_SMOKE_PATH = (
    ROOT / "artifacts" / "double_pendulum_persistence_tier1.json"
)
VARIATIONAL_ATLAS_PATH = (
    ROOT
    / "artifacts"
    / "double_pendulum_variational_atlas_13x13_t4_tier1.json"
)
VARIATIONAL_ATLAS_SMOKE_PATH = (
    ROOT / "artifacts" / "double_pendulum_variational_atlas_tier1.json"
)
PARAMETER_SENSITIVITY_PATH = (
    ROOT / "artifacts" / "double_pendulum_parameter_sensitivity_tier1.json"
)
PHYSICAL_POSITIVE_FLOOR_PATH = (
    ROOT / "artifacts" / "double_pendulum_physical_positive_floor.json"
)
STRUCTURED_PHYSICAL_NUISANCE_PATH = (
    ROOT / "artifacts" / "double_pendulum_structured_physical_nuisance.json"
)
GROUPED_PROTOCOL_PATH = (
    ROOT / "artifacts" / "double_pendulum_grouped_protocol_tier1.json"
)
GROUPED_PHYSICAL_CLOCK_FLOOR_PATH = (
    ROOT / "artifacts" / "double_pendulum_grouped_physical_clock_floor.json"
)


class CommittedDoublePendulumArtifactTests(unittest.TestCase):
    def test_provisional_tier1_atlas_is_complete_and_internally_consistent(self) -> None:
        report = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
        verification = verify_atlas_lab_report(report)
        self.assertTrue(verification["passed"], verification)
        self.assertEqual(report["claim_tier"], 1)
        self.assertEqual(report["acceptance_status"], "provisional_tier1")
        self.assertEqual(report["resolved_cell_count"], 169)
        self.assertEqual(report["unresolved_cell_count"], 0)
        self.assertEqual(len(report["refinement_audits"]), 169)
        self.assertTrue(report["all_refinement_audits_passed"])
        self.assertTrue(report["reflection_audit"]["passed"])
        self.assertLessEqual(
            max(
                row["max_scaled_state_discrepancy"]
                for row in report["refinement_audits"]
            ),
            report["run"]["refinement_scaled_state_tolerance"],
        )
        self.assertFalse(verification["declared_ode_to_raw_array_link_verified"])
        self.assertFalse(verification["physical_flow_enclosure_verified"])

    def test_previous_seam_failures_are_now_explicitly_resolved(self) -> None:
        report = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
        audits = {
            (row["row"], row["column"]): row
            for row in report["refinement_audits"]
        }
        for cell in ((0, 12), (12, 0)):
            self.assertIn(cell, audits)
            self.assertTrue(audits[cell]["passed"])
            self.assertLessEqual(
                audits[cell]["max_scaled_state_discrepancy"],
                report["run"]["refinement_scaled_state_tolerance"],
            )

    def test_conditional_protocol_certificate_uses_multiple_launches(self) -> None:
        report = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
        verification = verify_double_pendulum_protocol_report(report)
        self.assertTrue(verification["passed"], verification)
        self.assertEqual(verification["candidate_count"], 7)
        protocols = report["exact_enclosed_design"]["protocols"]
        active = [
            row for row in protocols if Fraction(row["physical_weight_exact"]) > 0
        ]
        active_launches = {row["name"].split(" / ", 1)[0] for row in active}
        self.assertGreaterEqual(len(active_launches), 2)
        robustness = report["exact_enclosed_design"]["response_box_robustness"]
        self.assertTrue(robustness["robust_floor_is_positive"])
        self.assertGreater(
            Fraction(robustness["robust_physical_floor_lower_exact"]), 0
        )
        self.assertFalse(verification["double_pendulum_ode_membership_verified"])

    def test_atlas_matched_persistence_ledger_verifies(self) -> None:
        report = json.loads(PERSISTENCE_PATH.read_text(encoding="utf-8"))
        verification = verify_persistence_report(report)
        self.assertTrue(verification["passed"], verification)
        self.assertEqual(verification["run_count"], 12)
        self.assertFalse(verification["declared_ode_to_fields_verified"])
        self.assertFalse(verification["outward_flow_enclosure_verified"])
        config = report["config"]
        self.assertEqual(config["baseline_side"], 13)
        self.assertEqual(config["baseline_duration"], 4.0)
        self.assertEqual(config["resolution_sides"], [9, 13, 17])
        self.assertFalse(
            report["horizon_continuation"]["has_numerical_pass_fail_status"]
        )
        source_counts = {
            row["name"]: row["source_reference_threshold_marked_count"]
            for row in report["runs"]
        }
        self.assertEqual(source_counts["baseline"], 7)
        self.assertEqual(source_counts["resolution-side-9"], 3)
        self.assertEqual(source_counts["resolution-side-17"], 11)
        self.assertEqual(
            [
                source_counts["shift-0.5-0"],
                source_counts["shift-0-0.5"],
                source_counts["shift-0.5-0.5"],
            ],
            [4, 4, 8],
        )

    def test_bounded_persistence_smoke_artifact_verifies(self) -> None:
        report = json.loads(PERSISTENCE_SMOKE_PATH.read_text(encoding="utf-8"))
        verification = verify_persistence_report(report)
        self.assertTrue(verification["passed"], verification)
        self.assertEqual(verification["run_count"], 11)
        self.assertFalse(verification["declared_ode_to_fields_verified"])

    def test_variational_atlas_masks_the_two_unresolved_seam_cells(self) -> None:
        report = json.loads(VARIATIONAL_ATLAS_PATH.read_text(encoding="utf-8"))
        verification = verify_variational_angle_slice_atlas_report(report)
        self.assertTrue(verification["passed"], verification)
        self.assertEqual(report["claim_tier"], 1)
        self.assertEqual(report["summary"]["cell_count"], 169)
        self.assertEqual(report["summary"]["resolved_cell_count"], 167)
        self.assertEqual(report["summary"]["unresolved_cell_count"], 2)
        self.assertEqual(
            {(row["row"], row["column"]) for row in report["unresolved_cells"]},
            {(0, 12), (12, 0)},
        )
        for row in report["unresolved_cells"]:
            self.assertIn("finite_difference_spot_check_failed", row["reasons"])
        fields = report["fields"]
        for row, column in ((0, 12), (12, 0)):
            self.assertFalse(fields["resolved_mask"][row][column])
            self.assertIsNone(fields["selected_weakest_local_gain"][row][column])
            self.assertIsNone(fields["selected_strongest_local_gain"][row][column])
        self.assertFalse(verification["ode_or_variational_system_replayed"])
        self.assertFalse(verification["physical_flow_enclosure_verified"])
        self.assertFalse(verification["exact_oig_certificate_verified"])

    def test_bounded_variational_smoke_artifact_verifies(self) -> None:
        report = json.loads(
            VARIATIONAL_ATLAS_SMOKE_PATH.read_text(encoding="utf-8")
        )
        verification = verify_variational_angle_slice_atlas_report(report)
        self.assertTrue(verification["passed"], verification)
        self.assertEqual(verification["side"], 7)
        self.assertFalse(verification["physical_flow_enclosure_verified"])

    def test_analytic_parameter_sensitivity_artifact_recomputes(self) -> None:
        report = json.loads(PARAMETER_SENSITIVITY_PATH.read_text(encoding="utf-8"))
        verification = verify_parameter_sensitivity_report(report)
        self.assertTrue(verification["passed"], verification)
        self.assertTrue(verification["tier1_numerics_recomputed"])
        self.assertTrue(verification["analytic_sensitivity_gates_verified"])
        self.assertFalse(verification["outward_validation_verified"])
        self.assertFalse(verification["exact_response_box_membership_verified"])

    def test_declared_model_physical_floor_artifact_recomputes(self) -> None:
        report = json.loads(
            PHYSICAL_POSITIVE_FLOOR_PATH.read_text(encoding="utf-8")
        )
        verification = verify_physical_positive_floor_certificate(report)
        self.assertTrue(verification["passed"], verification)
        self.assertTrue(verification["physical_positive_floor_verified"])
        self.assertEqual(
            report["robust_physical_floor_lower_exact"],
            "195932905640268820789/2500000000000000000000",
        )
        self.assertTrue(
            report["scope_flags"]["declared_dimensionless_model_floor_certified"]
        )
        for excluded_claim in (
            "seven_candidate_selection_certified",
            "seven_candidate_efficiency_certified",
            "parameter_neighborhood_uniformity_certified",
            "empirical_model_adequacy_certified",
            "hardware_calibration_certified",
        ):
            self.assertFalse(report["scope_flags"][excluded_claim])

    def test_structured_physical_nuisance_obstruction_verifies(self) -> None:
        report = json.loads(
            STRUCTURED_PHYSICAL_NUISANCE_PATH.read_text(encoding="utf-8")
        )
        verification = verify_structured_physical_nuisance_report(report)
        self.assertTrue(verification["passed"], verification)
        self.assertFalse(
            verification[
                "current_two_scalar_protocols_full_nuisance_floor_positive"
            ]
        )
        self.assertFalse(verification["ode_or_variational_system_replayed"])
        self.assertFalse(verification["outward_ode_nuisance_validation_verified"])

    def test_grouped_protocol_constructively_restores_full_query_rank(self) -> None:
        report = json.loads(GROUPED_PROTOCOL_PATH.read_text(encoding="utf-8"))
        verification = verify_grouped_protocol_report(report)
        self.assertTrue(verification["passed"], verification)
        self.assertTrue(
            verification[
                "positive_clock_profiled_floor_verified_for_declared_point_model"
            ]
        )
        selected = report["selected_designs"]["cost_weighted_clock_only"]
        self.assertEqual(selected["budget_shares_exact"], ["2/3", "1/3", "0/1"])
        self.assertGreater(
            Fraction(selected["positive_floor"]["profiled_floor_lower_exact"]),
            Fraction(18, 1000),
        )
        self.assertEqual(report["rank_theorem"]["selected_clock_output_count"], 5)
        self.assertEqual(
            report["rank_theorem"]["selected_clock_effective_rank_exact"], 2
        )
        self.assertFalse(verification["outward_ode_validation_verified"])
        self.assertFalse(verification["preparation_error_bound_verified"])

    def test_grouped_shared_clock_floor_is_outwardly_certified(self) -> None:
        report = json.loads(
            GROUPED_PHYSICAL_CLOCK_FLOOR_PATH.read_text(encoding="utf-8")
        )
        verification = verify_grouped_physical_clock_floor_certificate(report)
        self.assertTrue(verification["passed"], verification)
        self.assertEqual(
            verification["sharp_floor_lower_exact"], "180269/10000000"
        )
        self.assertTrue(
            report["scope_flags"][
                "declared_dimensionless_model_five_row_transfer_certified"
            ]
        )
        self.assertTrue(
            report["scope_flags"][
                "fixed_grouped_mixture_shared_clock_floor_certified"
            ]
        )
        self.assertTrue(report["scope_flags"]["exact_launch_preparation_assumed"])
        for excluded_claim in (
            "launch_preparation_error_bounded",
            "finite_clock_dilation_amplitude_certified",
            "parameter_neighborhood_uniformity_certified",
            "candidate_selection_transfer_certified",
            "finite_grid_optimality_certified",
            "empirical_model_adequacy_certified",
            "hardware_calibration_certified",
        ):
            self.assertFalse(report["scope_flags"][excluded_claim])

    def test_svg_is_derived_from_the_same_grid_contract(self) -> None:
        report = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
        svg = SVG_PATH.read_text(encoding="utf-8")
        self.assertIn("Double-pendulum operational atlas", svg)
        self.assertEqual(svg.count("<g><title>theta1="), 169)
        self.assertIn("Tier 1 numerical portrait", svg)
        self.assertEqual(svg, render_atlas_svg(report))


if __name__ == "__main__":
    unittest.main()
