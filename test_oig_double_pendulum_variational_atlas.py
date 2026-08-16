from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from double_pendulum_dynamics import IntegrationConfig
from double_pendulum_variational import (
    analyze_phase_protocol,
    simulate_double_pendulum_variational,
)
from oig_double_pendulum_variational_atlas import (
    PROOF_BOUNDARY,
    VariationalAngleSliceAtlasConfig,
    angle_slice_rms_protocol,
    main,
    run_variational_angle_slice_atlas,
    verify_variational_angle_slice_atlas_report,
)


class VariationalAngleSliceAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = VariationalAngleSliceAtlasConfig(
            side=3,
            duration=0.45,
            observation_count=13,
            feature_sample_count=4,
            sample_weights=(1.0, 2.0, 3.0, 4.0),
            spot_check_cells=((0, 0), (1, 1)),
        )
        cls.coarse = IntegrationConfig(
            rtol=1.0e-8,
            atol=1.0e-10,
            max_step=0.03,
            energy_drift_tolerance=1.0e-6,
        )
        cls.report = run_variational_angle_slice_atlas(
            cls.config, coarse_integration=cls.coarse
        )

    def test_rms_precision_matches_weighted_feature_pullback(self) -> None:
        times = np.asarray([0.0, 0.1, 0.2])
        trajectory = simulate_double_pendulum_variational(
            [0.3, -0.4, 0.0, 0.0], times, config=self.coarse.refined()
        )
        weights = np.asarray([0.2, 0.3, 0.5])
        protocol = angle_slice_rms_protocol(
            sample_indices=(0, 1, 2),
            sample_weights=weights,
            angular_velocity_scale=trajectory.parameters.characteristic_angular_speed,
        )
        analysis = analyze_phase_protocol(trajectory, protocol)
        weighted_response = analysis.response * np.repeat(np.sqrt(weights), 6)[:, None]
        np.testing.assert_allclose(
            analysis.information_gram,
            weighted_response.T @ weighted_response,
            rtol=2.0e-15,
            atol=2.0e-15,
        )
        np.testing.assert_array_equal(
            protocol.source_injection,
            [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0], [0.0, 0.0]],
        )

    def test_grid_has_local_gain_and_coarse_fine_gram_fields(self) -> None:
        fields = self.report["fields"]
        self.assertEqual(np.asarray(fields["resolved_mask"]).shape, (3, 3))
        self.assertEqual(
            np.asarray(fields["fine_information_gram"], dtype=float).shape,
            (3, 3, 2, 2),
        )
        self.assertEqual(
            np.asarray(fields["coarse_information_gram"], dtype=float).shape,
            (3, 3, 2, 2),
        )
        self.assertEqual(
            np.asarray(fields["selected_weakest_local_gain"], dtype=float).shape,
            (3, 3),
        )
        weakest = np.asarray(fields["selected_weakest_local_gain"], dtype=float)
        strongest = np.asarray(fields["selected_strongest_local_gain"], dtype=float)
        self.assertTrue(np.all(weakest > 0.0))
        self.assertTrue(np.all(strongest >= weakest))
        self.assertEqual(self.report["summary"]["resolved_cell_count"], 9)

    def test_protocol_serializes_rms_feature_geometry(self) -> None:
        protocol = self.report["protocol"]
        self.assertEqual(
            protocol["source_injection"],
            [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0], [0.0, 0.0]],
        )
        self.assertEqual(protocol["source_metric"], [[1.0, 0.0], [0.0, 1.0]])
        np.testing.assert_allclose(
            protocol["normalized_sample_weights"], [0.1, 0.2, 0.3, 0.4]
        )
        self.assertEqual(
            protocol["output_precision_rule"],
            "diag(normalized_sample_weights) kron I_6",
        )

    def test_selected_centered_differences_pass_against_variational_grams(self) -> None:
        checks = self.report["centered_finite_difference_spot_checks"]
        self.assertEqual([(row["row"], row["column"]) for row in checks], [(0, 0), (1, 1)])
        self.assertTrue(all(row["passed"] for row in checks))
        self.assertTrue(
            all(row["response_relative_discrepancy"] < 2.0e-7 for row in checks)
        )
        self.assertTrue(
            all(row["gram_relative_discrepancy"] < 3.0e-7 for row in checks)
        )
        self.assertTrue(
            all(
                row["weakest_gain_relative_discrepancy"] < 3.0e-7
                and row["strongest_gain_relative_discrepancy"] < 3.0e-7
                for row in checks
            )
        )

    def test_failed_refinement_is_unresolved_and_selected_gain_is_masked(self) -> None:
        strict = VariationalAngleSliceAtlasConfig(
            side=3,
            duration=0.3,
            observation_count=9,
            feature_sample_count=3,
            state_relative_tolerance=1.0e-30,
            tangent_relative_tolerance=1.0e-30,
            response_relative_tolerance=1.0e-30,
            gram_relative_tolerance=1.0e-30,
            finite_difference_response_relative_tolerance=1.0e-30,
            finite_difference_gram_relative_tolerance=1.0e-30,
            spot_check_cells=((0, 0),),
        )
        report = run_variational_angle_slice_atlas(
            strict, coarse_integration=self.coarse
        )
        self.assertGreater(report["summary"]["unresolved_cell_count"], 0)
        mask = np.asarray(report["fields"]["unresolved_mask"], dtype=bool)
        weakest = np.asarray(
            report["fields"]["selected_weakest_local_gain"], dtype=object
        )
        self.assertTrue(all(weakest[cell] is None for cell in zip(*np.nonzero(mask))))
        self.assertEqual(
            len(report["unresolved_cells"]),
            report["summary"]["unresolved_cell_count"],
        )

    def test_report_is_json_safe_and_keeps_tier1_boundary(self) -> None:
        payload = json.dumps(self.report, allow_nan=False)
        self.assertIn("variational-angle-slice-atlas", payload)
        self.assertEqual(self.report["claim_tier"], 1)
        self.assertEqual(self.report["proof_boundary"], PROOF_BOUNDARY)
        self.assertIn("not an outward", PROOF_BOUNDARY)
        self.assertNotIn("exact_enclosed_design", self.report)

    def test_strict_verifier_passes_without_replaying_dynamics(self) -> None:
        forbidden = AssertionError("the report verifier must not replay dynamics")
        with (
            patch(
                "oig_double_pendulum_variational_atlas.simulate_double_pendulum",
                side_effect=forbidden,
            ),
            patch(
                "oig_double_pendulum_variational_atlas.simulate_double_pendulum_variational",
                side_effect=forbidden,
            ),
        ):
            verification = verify_variational_angle_slice_atlas_report(self.report)
        self.assertTrue(verification["passed"], verification)
        self.assertFalse(verification["ode_or_variational_system_replayed"])
        self.assertFalse(verification["physical_flow_enclosure_verified"])
        self.assertFalse(verification["exact_oig_certificate_verified"])

    def test_verifier_rejects_masks_gates_spots_summaries_and_boundary_tampering(self) -> None:
        cases = []

        tampered = deepcopy(self.report)
        tampered["fields"]["unresolved_mask"][0][0] = 1
        cases.append(tampered)

        tampered = deepcopy(self.report)
        tampered["fields"]["selected_weakest_local_gain"][0][0] = None
        cases.append(tampered)

        tampered = deepcopy(self.report)
        actual = tampered["fields"][
            "weakest_gain_refinement_relative_discrepancy"
        ][0][0]
        tampered["configuration"]["weakest_gain_relative_tolerance"] = actual / 2.0
        tampered["acceptance"]["weakest_gain_relative_tolerance"] = actual / 2.0
        cases.append(tampered)

        tampered = deepcopy(self.report)
        tampered["centered_finite_difference_spot_checks"][0]["passed"] = False
        cases.append(tampered)

        tampered = deepcopy(self.report)
        tampered["summary"]["weakest_gain_quantiles_over_resolved_cells"]["q50"] += 1.0
        cases.append(tampered)

        tampered = deepcopy(self.report)
        tampered["proof_boundary"] = "numerically exact"
        cases.append(tampered)

        for index, candidate in enumerate(cases):
            with self.subTest(tamper=index):
                verification = verify_variational_angle_slice_atlas_report(candidate)
                self.assertFalse(verification["passed"], verification)
                self.assertFalse(verification["ode_or_variational_system_replayed"])

    def test_verifier_reconstructs_gram_and_gain_discrepancies(self) -> None:
        tampered = deepcopy(self.report)
        tampered["fields"]["gram_refinement_relative_discrepancy"][0][0] *= 2.0
        self.assertFalse(
            verify_variational_angle_slice_atlas_report(tampered)["passed"]
        )

        tampered = deepcopy(self.report)
        tampered["centered_finite_difference_spot_checks"][0][
            "finite_difference_response"
        ][0][0] += 0.25
        self.assertFalse(
            verify_variational_angle_slice_atlas_report(tampered)["passed"]
        )

        tampered = deepcopy(self.report)
        tampered["centered_finite_difference_spot_checks"][0][
            "weakest_gain_relative_discrepancy"
        ] *= 2.0
        self.assertFalse(
            verify_variational_angle_slice_atlas_report(tampered)["passed"]
        )

    def test_verifier_rejects_bool_claims_and_nonnumeric_matrix_entries(self) -> None:
        tampered = deepcopy(self.report)
        tampered["claim_tier"] = True
        self.assertFalse(
            verify_variational_angle_slice_atlas_report(tampered)["passed"]
        )

        tampered = deepcopy(self.report)
        tampered["protocol"]["source_injection"][0][0] = "1.0"
        self.assertFalse(
            verify_variational_angle_slice_atlas_report(tampered)["passed"]
        )

        tampered = deepcopy(self.report)
        tampered["fields"]["fine_information_gram"][0][0][0][0] = True
        self.assertFalse(
            verify_variational_angle_slice_atlas_report(tampered)["passed"]
        )

        tampered = deepcopy(self.report)
        tampered["fields"][
            "strongest_gain_refinement_relative_discrepancy"
        ][0][0] *= 2.0
        self.assertFalse(
            verify_variational_angle_slice_atlas_report(tampered)["passed"]
        )

    def test_cli_verify_and_disabled_energy_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(json.dumps(self.report), encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                status = main(["--verify", str(path)])
            self.assertEqual(status, 0)
            verification = json.loads(output.getvalue())
            self.assertTrue(verification["passed"])
            self.assertFalse(verification["ode_or_variational_system_replayed"])

        with self.assertRaisesRegex(ValueError, "energy-drift gate"):
            run_variational_angle_slice_atlas(
                VariationalAngleSliceAtlasConfig(
                    side=3,
                    duration=0.2,
                    observation_count=7,
                    feature_sample_count=3,
                ),
                coarse_integration=IntegrationConfig(
                    rtol=1.0e-8,
                    atol=1.0e-10,
                    max_step=0.03,
                    energy_drift_tolerance=None,
                ),
            )

    def test_finite_difference_exception_report_roundtrips(self) -> None:
        config = VariationalAngleSliceAtlasConfig(
            side=3,
            duration=0.2,
            observation_count=7,
            feature_sample_count=3,
            spot_check_cells=((0, 0),),
        )
        with patch(
            "oig_double_pendulum_variational_atlas.simulate_double_pendulum",
            side_effect=RuntimeError("forced perturbation failure"),
        ):
            report = run_variational_angle_slice_atlas(
                config, coarse_integration=self.coarse
            )
        check = report["centered_finite_difference_spot_checks"][0]
        self.assertFalse(check["passed"])
        self.assertEqual(
            check["status"],
            "finite-difference error: RuntimeError: forced perturbation failure",
        )
        self.assertIn(
            "finite_difference_error:RuntimeError:forced perturbation failure",
            report["unresolved_cells"][0]["reasons"],
        )
        verification = verify_variational_angle_slice_atlas_report(report)
        self.assertTrue(verification["passed"], verification)

    def test_parameters_environment_norms_and_spot_scope_are_explicit(self) -> None:
        self.assertEqual(set(self.report["parameters"]), {"m1", "m2", "l1", "l2", "g"})
        self.assertEqual(
            set(self.report["environment"]), {"python", "numpy", "scipy", "platform"}
        )
        norms = self.report["acceptance"]["discrepancy_norms"]
        self.assertIn("||G_coarse-G_fine||_F", norms["information_gram"])
        self.assertIn("sigma_min", norms["weakest_gain"])
        self.assertIn("only at declared spots", norms["finite_difference_response"])
        self.assertIn(
            "not at every resolved grid cell",
            self.report["acceptance"]["finite_difference_scope"],
        )

    def test_committed_13x13_t4_report_verifies_with_two_unresolved_cells(self) -> None:
        path = (
            Path(__file__).resolve().parent
            / "artifacts"
            / "double_pendulum_variational_atlas_13x13_t4_tier1.json"
        )
        report = json.loads(path.read_text(encoding="utf-8"))
        verification = verify_variational_angle_slice_atlas_report(report)
        self.assertTrue(verification["passed"], verification)
        self.assertEqual(verification["side"], 13)
        self.assertEqual(report["summary"]["resolved_cell_count"], 167)
        self.assertEqual(report["summary"]["unresolved_cell_count"], 2)
        self.assertFalse(report["summary"]["all_requested_spot_checks_passed"])

    def test_invalid_weights_and_spot_cells_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            VariationalAngleSliceAtlasConfig(
                side=3,
                feature_sample_count=3,
                sample_weights=(1.0, 2.0),
            )
        with self.assertRaisesRegex(ValueError, "strictly positive"):
            VariationalAngleSliceAtlasConfig(
                side=3,
                feature_sample_count=3,
                sample_weights=(1.0, 0.0, 1.0),
            )
        with self.assertRaises(ValueError):
            VariationalAngleSliceAtlasConfig(side=3, spot_check_cells=((3, 0),))


if __name__ == "__main__":
    unittest.main()
