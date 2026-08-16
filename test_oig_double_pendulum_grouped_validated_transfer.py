"""Adversarial tests for the outward grouped shared-clock certificate."""

from __future__ import annotations

from contextlib import redirect_stdout
from copy import deepcopy
from fractions import Fraction
import io
import json
from pathlib import Path
import unittest

from flint import ctx

from oig_double_pendulum_protocol import canonical_protocol_candidates
import oig_double_pendulum_grouped_validated_transfer as grouped
import oig_double_pendulum_validated_transfer as validated


Q = Fraction


class RationalIntervalPrimitiveTests(unittest.TestCase):
    def test_exact_interval_operations_are_outward(self) -> None:
        left = grouped.RationalInterval(Q(-2), Q(3))
        right = grouped.RationalInterval(Q(4), Q(5))
        self.assertEqual(left + right, grouped.RationalInterval(Q(2), Q(8)))
        self.assertEqual(left - right, grouped.RationalInterval(Q(-7), Q(-1)))
        self.assertEqual(left * right, grouped.RationalInterval(Q(-10), Q(15)))
        positive = grouped.RationalInterval(Q(2), Q(4))
        self.assertEqual(
            positive.reciprocal(), grouped.RationalInterval(Q(1, 4), Q(1, 2))
        )
        with self.assertRaises(ZeroDivisionError):
            left.reciprocal()

    def test_selected_rows_crosslink_to_canonical_library_and_costs(self) -> None:
        canonical = {row.name: row for row in canonical_protocol_candidates()}
        selected = grouped.selected_observations()
        self.assertEqual(len(selected), 5)
        self.assertEqual(
            tuple(row.candidate.name for row in selected),
            tuple(row.name for row in canonical_protocol_candidates()[:5]),
        )
        for row in selected:
            self.assertEqual(row.candidate, canonical[row.candidate.name])
        self.assertEqual(
            tuple(row.physical_weight for row in selected),
            (Q(4, 21), Q(4, 21), Q(4, 21), Q(4, 27), Q(4, 27)),
        )


class GroupedPhysicalClockCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = grouped.build_grouped_physical_clock_floor_certificate()

    def test_all_five_state_parameter_and_clock_boxes_are_outward(self) -> None:
        report = self.report
        self.assertEqual(report["status"], "proved")
        self.assertEqual(report["evidence_tier"], grouped.EVIDENCE_TIER)
        self.assertIs(report["all_five_outward_joint_boxes_certified"], True)
        observations = report["observations"]
        self.assertEqual(len(observations), 5)
        for row in observations:
            self.assertIs(row["outward_joint_box_certified"], True)
            entries = row["joint_augmented_row_outer_box_exact"]["entries"]
            self.assertEqual(len(entries), 3)
            for entry in entries:
                interval = grouped.RationalInterval.from_record(entry)
                self.assertLess(interval.lower, interval.upper)
            output = grouped.RationalInterval.from_record(
                row["sensor_output_outer_box_exact"]
            )
            self.assertLess(output.lower, output.upper)
            self.assertGreater(row["validated_step_count"], 0)
            self.assertGreaterEqual(row["maximum_picard_tube_iterations"], 1)

    def test_serialized_box_widths_and_clock_denominator_are_small_and_positive(self) -> None:
        summary = self.report["outward_box_summary"]
        self.assertEqual(
            summary["maximum_parameter_response_half_width_exact"],
            "144353/2000000000000000",
        )
        self.assertEqual(
            summary["maximum_shared_clock_response_half_width_exact"],
            "7769/250000000000000",
        )
        self.assertLess(summary["maximum_parameter_response_half_width_decimal"], 8e-11)
        self.assertLess(summary["maximum_shared_clock_response_half_width_decimal"], 4e-11)
        denominator = grouped.RationalInterval.from_record(
            self.report["exact_rational_interval_profile"][
                "clock_information_outer_interval_exact"
            ]
        )
        self.assertGreater(denominator.lower, Q(3, 2))

    def test_exact_interval_ldl_proves_both_uniform_floors(self) -> None:
        exact = self.report["exact_rational_interval_profile"]
        for name, floor in (
            ("simple_floor_certificate", grouped.SIMPLE_FLOOR),
            ("sharp_floor_certificate", grouped.SHARP_FLOOR),
        ):
            child = exact[name]
            self.assertEqual(
                child["candidate_profiled_floor_exact"],
                grouped._fraction_text(floor),
            )
            self.assertIs(child["all_interval_ldl_pivots_strictly_positive"], True)
            self.assertIs(child["sampled_eigenvalue_used_for_decision"], False)
            self.assertTrue(all(Q(value) > 0 for value in child["strict_lower_pivot_margins_exact"]))
        self.assertGreater(grouped.SHARP_FLOOR, grouped.SIMPLE_FLOOR)
        theorem = self.report["theorem"]
        self.assertEqual(
            theorem["sharp_physical_clock_profiled_floor_lower_exact"],
            "180269/10000000",
        )
        self.assertIs(theorem["positive_two_source_floor_certified"], True)

    def test_profiled_information_interval_matches_independent_exact_reconstruction(self) -> None:
        verification = grouped._exact_algebra_verification(self.report)
        self.assertIs(verification["passed"], True)
        profile = self.report["exact_rational_interval_profile"][
            "clock_profiled_information_outer_interval_exact"
        ]
        entries = [
            grouped.RationalInterval.from_record(profile[0][0]),
            grouped.RationalInterval.from_record(profile[0][1]),
            grouped.RationalInterval.from_record(profile[1][1]),
        ]
        self.assertTrue(Q(24, 1000) < entries[0].lower < entries[0].upper < Q(25, 1000))
        self.assertTrue(Q(6, 1000) < entries[1].lower < entries[1].upper < Q(7, 1000))
        self.assertTrue(Q(23, 1000) < entries[2].lower < entries[2].upper < Q(24, 1000))

    def test_stricter_picard_taylor_run_lies_inside_default_boxes(self) -> None:
        refined = grouped.build_grouped_physical_clock_floor_certificate(
            validated.ValidatedTransferConfig(
                precision_bits=192,
                taylor_order=9,
                step_size=Q(1, 200),
            )
        )
        self.assertEqual(refined["status"], "proved")
        for baseline, stronger in zip(
            self.report["observations"], refined["observations"]
        ):
            for baseline_box, stronger_box in zip(
                baseline["joint_augmented_row_outer_box_exact"]["entries"],
                stronger["joint_augmented_row_outer_box_exact"]["entries"],
            ):
                outer = grouped.RationalInterval.from_record(baseline_box)
                inner = grouped.RationalInterval.from_record(stronger_box)
                self.assertLessEqual(outer.lower, inner.lower)
                self.assertLessEqual(inner.upper, outer.upper)

    def test_scope_does_not_promote_preparation_selection_or_hardware(self) -> None:
        flags = self.report["scope_flags"]
        self.assertIs(flags["exact_launch_preparation_assumed"], True)
        for name in (
            "launch_preparation_error_bounded",
            "finite_clock_dilation_amplitude_certified",
            "parameter_neighborhood_uniformity_certified",
            "candidate_selection_transfer_certified",
            "finite_grid_optimality_certified",
            "empirical_model_adequacy_certified",
            "hardware_calibration_certified",
        ):
            self.assertIs(flags[name], False)
        self.assertIn("dimensionless nonlinear double-pendulum", self.report["physical_scope_definition"])

    def test_strict_verifier_rejects_forged_floor_box_and_scope(self) -> None:
        forged = deepcopy(self.report)
        forged["exact_rational_interval_profile"]["sharp_floor_certificate"][
            "candidate_profiled_floor_exact"
        ] = "1/1"
        self.assertIs(
            grouped.verify_grouped_physical_clock_floor_certificate(forged)["passed"],
            False,
        )
        forged = deepcopy(self.report)
        forged["observations"][0]["joint_augmented_row_outer_box_exact"]["entries"][0][
            "lower_exact"
        ] = "0/1"
        self.assertIs(
            grouped.verify_grouped_physical_clock_floor_certificate(forged)["passed"],
            False,
        )
        forged = deepcopy(self.report)
        forged["scope_flags"]["hardware_calibration_certified"] = True
        self.assertIs(
            grouped.verify_grouped_physical_clock_floor_certificate(forged)["passed"],
            False,
        )

    def test_weak_picard_controls_cannot_emit_a_certificate(self) -> None:
        weak = validated.ValidatedTransferConfig(
            precision_bits=100,
            taylor_order=3,
            step_size=Q(1, 4),
            maximum_tube_iterations=1,
        )
        with self.assertRaises(validated.StepValidationError):
            grouped.build_grouped_physical_clock_floor_certificate(weak)

    def test_committed_artifact_is_fresh_and_cli_verifies(self) -> None:
        path = Path(__file__).with_name("artifacts") / (
            "double_pendulum_grouped_physical_clock_floor.json"
        )
        committed = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(committed, self.report)
        verification = grouped.verify_grouped_physical_clock_floor_certificate(committed)
        self.assertIs(verification["passed"], True)
        output = io.StringIO()
        with redirect_stdout(output):
            status = grouped.main(["--verify", str(path)])
        self.assertEqual(status, 0)
        self.assertIs(json.loads(output.getvalue())["passed"], True)

    def test_report_is_invariant_to_ambient_flint_precision(self) -> None:
        previous_precision = ctx.prec
        try:
            ctx.prec = 320
            rebuilt = grouped.build_grouped_physical_clock_floor_certificate()
        finally:
            ctx.prec = previous_precision
        self.assertEqual(rebuilt, self.report)
        self.assertEqual(ctx.prec, previous_precision)


if __name__ == "__main__":
    unittest.main()
