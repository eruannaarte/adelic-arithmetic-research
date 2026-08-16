"""Adversarial tests for the outward double-pendulum ODE transfer."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import math
import json
from pathlib import Path
import unittest

from flint import arb, ctx

from double_pendulum_dynamics import DoublePendulumParameters, double_pendulum_rhs
from oig_double_pendulum_protocol import canonical_protocol_candidates
import oig_double_pendulum_validated_transfer as validated


Q = Fraction


class ValidatedTransferPrimitiveTests(unittest.TestCase):
    def test_augmented_rhs_contains_state_rhs_and_parameter_partials(self) -> None:
        target = validated.active_protocol_targets()[0]
        with ctx.workprec(180):
            state = tuple(validated._arb_fraction(value) for value in target.launch)
            result = validated.augmented_rhs(tuple(state) + (arb(0),) * 8)
            base = double_pendulum_rhs(
                0.0,
                [float(value) for value in target.launch],
                DoublePendulumParameters(m1=1, m2=1, l1=1, l2=1, g=1),
            )
            for enclosure, expected in zip(result[:4], base):
                self.assertLess(abs(float(enclosure.mid()) - float(expected)), 2e-14)

            epsilon = 1.0e-6
            numerical_columns = []
            for coordinate in range(2):
                shifted = []
                for sign in (1.0, -1.0):
                    u = sign * epsilon if coordinate == 0 else 0.0
                    v = sign * epsilon if coordinate == 1 else 0.0
                    shifted.append(
                        double_pendulum_rhs(
                            0.0,
                            [float(value) for value in target.launch],
                            DoublePendulumParameters(
                                m1=1.0,
                                m2=math.exp(u),
                                l1=1.0,
                                l2=math.exp(v),
                                g=1.0,
                            ),
                        )
                    )
                numerical_columns.append(
                    (shifted[0] - shifted[1]) / (2.0 * epsilon)
                )
            for enclosure, expected in zip(result[4:8], numerical_columns[0]):
                self.assertLess(abs(float(enclosure.mid()) - float(expected)), 2e-9)
            for enclosure, expected in zip(result[8:12], numerical_columns[1]):
                self.assertLess(abs(float(enclosure.mid()) - float(expected)), 2e-9)

    def test_taylor_defect_bound_contains_direct_samples(self) -> None:
        config = validated.ValidatedTransferConfig()
        target = validated.active_protocol_targets()[0]
        with ctx.workprec(config.precision_bits):
            midpoint = [validated._arb_fraction(value) for value in target.launch]
            midpoint.extend(arb(0) for _ in range(8))
            polynomials = validated._taylor_polynomial(
                midpoint, config.taylor_order
            )
            h = validated._arb_fraction(config.step_size)
            bounds = validated._residual_bounds(polynomials, h)
        # Re-evaluate sample residuals at substantially higher precision so
        # the independent audit's own rounding radius is below the proved
        # defect bound (some kinematic residuals are identically zero).
        with ctx.workprec(400):
            for time in (Q(0), config.step_size / 3, config.step_size):
                argument = validated._arb_fraction(time)
                values = [
                    validated._polynomial_value(row, argument)
                    for row in polynomials
                ]
                derivatives = [
                    validated._polynomial_value(
                        [degree * coefficient for degree, coefficient in enumerate(row)][1:],
                        argument,
                    )
                    for row in polynomials
                ]
                residual = [
                    derivative - rhs
                    for derivative, rhs in zip(
                        derivatives, validated.augmented_rhs(values)
                    )
                ]
                for bound, sample in zip(bounds, residual):
                    if bound == 0:
                        self.assertTrue(sample.contains(0))
                    else:
                        self.assertTrue(-bound < sample and sample < bound)

    def test_configuration_rejects_binary_float_proof_controls(self) -> None:
        with self.assertRaises(ValueError):
            validated.ValidatedTransferConfig(step_size=0.01)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            validated.ValidatedTransferConfig(tube_inflation=1.2)  # type: ignore[arg-type]


class ValidatedTransferCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.transfer = validated.build_validated_transfer_report()
        cls.physical = validated.build_physical_positive_floor_certificate()

    def test_two_active_response_boxes_are_physically_enclosed(self) -> None:
        self.assertEqual(self.transfer["status"], "proved")
        self.assertIs(
            self.transfer["all_active_declared_box_memberships_certified"], True
        )
        self.assertEqual(len(self.transfer["protocols"]), 2)
        for row in self.transfer["protocols"]:
            self.assertEqual(row["status"], "proved")
            self.assertIs(row["declared_box_membership_certified"], True)
            self.assertTrue(all(row["declared_box_membership_by_source"]))
            self.assertIs(row["inclusion_slack_is_strictly_positive"], True)
            target = next(
                item
                for item in validated.active_protocol_targets()
                if item.name == row["name"]
            )
            for index, (enclosure, centre, radius) in enumerate(
                zip(
                    row["response_enclosure"],
                    target.declared_centre,
                    target.declared_radius,
                )
            ):
                expected = min(
                    Q(enclosure["lower_exact"]) - (centre - radius),
                    (centre + radius) - Q(enclosure["upper_exact"]),
                )
                self.assertGreater(expected, 0)
                self.assertEqual(
                    row["declared_box_inclusion_slack_exact"][index],
                    validated._fraction_text(expected),
                )
            self.assertLess(row["maximum_endpoint_radius_upper"], 1e-8)

    def test_stricter_outward_refinement_control_also_closes(self) -> None:
        refined = validated.build_validated_transfer_report(
            validated.ValidatedTransferConfig(
                precision_bits=192,
                taylor_order=9,
                step_size=Q(1, 200),
            )
        )
        self.assertEqual(refined["status"], "proved")
        for baseline, stricter in zip(
            self.transfer["protocols"], refined["protocols"]
        ):
            self.assertIs(stricter["declared_box_membership_certified"], True)
            for baseline_ball, stricter_ball in zip(
                baseline["response_enclosure"], stricter["response_enclosure"]
            ):
                self.assertGreaterEqual(
                    Q(stricter_ball["lower_exact"]), Q(baseline_ball["lower_exact"])
                )
                self.assertLessEqual(
                    Q(stricter_ball["upper_exact"]), Q(baseline_ball["upper_exact"])
                )

    def test_exact_enclosed_protocol_interface_preserves_declarations(self) -> None:
        protocols = validated.validated_active_enclosed_protocols()
        targets = validated.active_protocol_targets()
        self.assertEqual(tuple(row.name for row in protocols), tuple(t.name for t in targets))
        self.assertEqual(protocols[0].response_centre, (targets[0].declared_centre,))
        self.assertEqual(protocols[1].response_radius, (targets[1].declared_radius,))
        self.assertEqual(tuple(row.cost for row in protocols), (Q(1), Q(5, 4)))

    def test_active_constants_crosslink_to_canonical_library_and_artifact(self) -> None:
        targets = validated.active_protocol_targets()
        canonical = {row.name: row for row in canonical_protocol_candidates()}
        for target in targets:
            candidate = canonical[target.name]
            self.assertEqual(candidate.launch, target.launch)
            self.assertEqual(candidate.sensor, target.sensor)
            self.assertEqual(candidate.observation_time_tau, target.terminal_time)

        artifact_path = Path(__file__).with_name("artifacts") / (
            "double_pendulum_protocol_design_conditional.json"
        )
        artifact = json.loads(artifact_path.read_text())
        box_rows = {
            row["candidate"]["name"]: row
            for row in artifact["candidate_response_boxes"]
        }
        design_rows = {
            row["name"]: row for row in artifact["exact_enclosed_design"]["protocols"]
        }
        expected_shares = ("4589/10000", "5411/10000")
        for target, expected_share in zip(targets, expected_shares):
            box = box_rows[target.name]
            self.assertEqual(
                box["response_centre_exact"],
                [[validated._fraction_text(value) for value in target.declared_centre]],
            )
            self.assertEqual(
                box["response_radius_exact"],
                [[validated._fraction_text(value) for value in target.declared_radius]],
            )
            self.assertEqual(
                design_rows[target.name]["budget_share_exact"], expected_share
            )

    def test_composition_closes_the_physical_positive_floor(self) -> None:
        self.assertEqual(self.physical["status"], "proved")
        self.assertIs(self.physical["physical_positive_floor_certified"], True)
        self.assertEqual(
            self.physical["robust_physical_floor_lower_exact"],
            "195932905640268820789/2500000000000000000000",
        )
        verification = validated.verify_physical_positive_floor_certificate(
            self.physical
        )
        self.assertIs(verification["passed"], True)
        self.assertIs(verification["physical_positive_floor_verified"], True)
        flags = self.physical["scope_flags"]
        self.assertIs(flags["declared_dimensionless_model_floor_certified"], True)
        for name in (
            "seven_candidate_selection_certified",
            "seven_candidate_efficiency_certified",
            "parameter_neighborhood_uniformity_certified",
            "empirical_model_adequacy_certified",
            "hardware_calibration_certified",
        ):
            self.assertIs(flags[name], False)
        self.assertIn(
            "declared nonlinear dimensionless double-pendulum equations",
            self.physical["physical_scope_definition"],
        )

    def test_committed_physical_artifact_is_fresh_and_strictly_verified(self) -> None:
        path = Path(__file__).with_name("artifacts") / (
            "double_pendulum_physical_positive_floor.json"
        )
        committed = json.loads(path.read_text())
        self.assertEqual(committed, self.physical)
        self.assertIs(
            validated.verify_physical_positive_floor_certificate(committed)["passed"],
            True,
        )

    def test_report_is_invariant_to_ambient_flint_precision(self) -> None:
        previous_precision = ctx.prec
        try:
            ctx.prec = 320
            rebuilt = validated.build_physical_positive_floor_certificate()
        finally:
            ctx.prec = previous_precision
        self.assertEqual(rebuilt, self.physical)
        self.assertEqual(ctx.prec, previous_precision)

    def test_failed_picard_gate_is_unresolved_not_promoted(self) -> None:
        weak = validated.ValidatedTransferConfig(
            precision_bits=100,
            taylor_order=3,
            step_size=Q(1, 4),
            maximum_tube_iterations=1,
        )
        report = validated.build_validated_transfer_report(weak)
        self.assertEqual(report["status"], "unresolved")
        self.assertIs(report["enclosed_protocol_transfer_ready"], False)
        self.assertTrue(
            all(row["declared_box_membership_certified"] is False for row in report["protocols"])
        )
        with self.assertRaises(validated.StepValidationError):
            validated.validated_active_enclosed_protocols(weak)
        physical = validated.build_physical_positive_floor_certificate(weak)
        self.assertEqual(physical["status"], "unresolved")
        self.assertIs(physical["exact_active_enclosed_design"], None)

    def test_transfer_verifier_rejects_forged_membership_and_enclosure(self) -> None:
        forged = deepcopy(self.transfer)
        forged["protocols"][0]["response_enclosure"][0]["lower_exact"] = "0/1"
        self.assertIs(
            validated.verify_validated_transfer_report(forged)["passed"], False
        )

        forged = deepcopy(self.transfer)
        forged["scope_flags"]["hardware_calibration_certified"] = 0
        self.assertIs(
            validated.verify_validated_transfer_report(forged)["passed"], False
        )
        forged = deepcopy(self.transfer)
        forged["protocols"][1]["maximum_picard_tube_iterations"] = 0
        self.assertIs(
            validated.verify_validated_transfer_report(forged)["passed"], False
        )

    def test_composed_verifier_rejects_forged_floor_or_child(self) -> None:
        forged = deepcopy(self.physical)
        forged["robust_physical_floor_lower_exact"] = "1/1"
        self.assertIs(
            validated.verify_physical_positive_floor_certificate(forged)["passed"],
            False,
        )

        forged = deepcopy(self.physical)
        forged["physical_positive_floor_certified"] = 1
        self.assertIs(
            validated.verify_physical_positive_floor_certificate(forged)["passed"],
            False,
        )
        forged = deepcopy(self.physical)
        forged["scope_flags"]["hardware_calibration_certified"] = 0
        self.assertIs(
            validated.verify_physical_positive_floor_certificate(forged)["passed"],
            False,
        )
        forged = deepcopy(self.physical)
        forged["exact_active_enclosed_design"]["response_box_robustness"][
            "robust_floor_is_positive"
        ] = False
        self.assertIs(
            validated.verify_physical_positive_floor_certificate(forged)["passed"],
            False,
        )


if __name__ == "__main__":
    unittest.main()
