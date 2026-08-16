#!/usr/bin/env python3

from copy import deepcopy
import json
import unittest

import numpy as np

from double_pendulum_dynamics import DoublePendulumParameters, IntegrationConfig
from oig_double_pendulum_persistence import (
    PersistenceLabConfig,
    TIER1_BOUNDARY,
    build_persistence_report,
    energy_association,
    field_comparison,
    periodic_bilinear_resample,
    research_persistence_config,
    shifted_cell_centred_torus_grid,
    threshold_filtration,
    verify_persistence_report,
)


class PersistencePrimitiveTests(unittest.TestCase):
    def test_shifted_grid_retains_state_order_and_unique_periodic_cells(self) -> None:
        first, second, states = shifted_cell_centred_torus_grid(7, (0.5, -0.25))
        self.assertEqual(states.shape, (7, 7, 4))
        np.testing.assert_array_equal(
            states[..., 0], np.broadcast_to(first[:, None], (7, 7))
        )
        np.testing.assert_array_equal(
            states[..., 1], np.broadcast_to(second[None, :], (7, 7))
        )
        np.testing.assert_array_equal(states[..., 2:], np.zeros((7, 7, 2)))
        self.assertTrue(np.all(np.diff(first) > 0.0))
        self.assertTrue(np.all(np.diff(second) > 0.0))
        self.assertAlmostEqual(first[-1] - first[0], 12.0 * np.pi / 7.0)

    def test_periodic_bilinear_resampling_is_identity_on_same_grid(self) -> None:
        source = np.arange(25.0).reshape(5, 5)
        copied = periodic_bilinear_resample(
            source,
            source_shift=(0.25, -0.2),
            target_side=5,
            target_shift=(0.25, -0.2),
        )
        np.testing.assert_array_equal(copied, source)
        constant = periodic_bilinear_resample(
            np.full((5, 5), 3.7),
            source_shift=(0.5, 0.0),
            target_side=13,
            target_shift=(-0.3, 0.4),
        )
        np.testing.assert_allclose(constant, 3.7, rtol=0.0, atol=9.0e-16)

    def test_threshold_filtration_is_nested_and_torus_aware(self) -> None:
        field = np.full((5, 5), 2.0)
        field[0, 2] = 0.0
        field[-1, 2] = 0.0
        records = threshold_filtration(field, (-1.0, 0.0, 2.0))
        self.assertEqual([row["active_cell_count"] for row in records], [0, 2, 25])
        self.assertEqual(records[1]["component_sizes"], [2])
        self.assertEqual(records[-1]["component_sizes"], [25])

    def test_field_comparison_reports_threshold_overlap(self) -> None:
        reference = np.asarray([[0.0, 1.0], [2.0, 3.0]])
        candidate = np.asarray([[0.0, 2.0], [1.0, 3.0]])
        comparison = field_comparison(reference, candidate, (0.5, 1.5))
        self.assertEqual(comparison["threshold_overlap"][0]["jaccard"], 1.0)
        self.assertEqual(comparison["threshold_overlap"][1]["jaccard"], 1 / 3)
        self.assertGreater(comparison["rms_difference"], 0.0)

    def test_energy_association_bins_cover_every_cell(self) -> None:
        energy = np.arange(16.0).reshape(4, 4)
        field = (2.0 * energy + 1.0)[::-1]
        report = energy_association(
            energy, field, bin_count=4, reference_threshold=10.0
        )
        self.assertEqual(sum(row["count"] for row in report["bins"]), 16)
        self.assertEqual(len(report["energy_quantile_edges"]), 5)
        self.assertIn("Descriptive association only", report["interpretation"])

    def test_research_preset_matches_the_main_atlas_contract(self) -> None:
        config = research_persistence_config()
        self.assertEqual(config.baseline_side, 13)
        self.assertEqual(config.baseline_duration, 4.0)
        self.assertEqual(config.baseline_observation_count, 81)
        self.assertEqual(config.baseline_feature_count, 9)
        self.assertEqual(config.resolution_sides, (9, 13, 17))
        self.assertEqual(config.horizon_variants, (2.0, 4.0, 6.0))
        self.assertEqual(config.cadence_feature_counts, (5, 9, 17, 41, 81))


class PersistenceReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = PersistenceLabConfig(
            baseline_side=3,
            resolution_sides=(3, 4),
            shift_variants=((0.0, 0.0), (0.5, 0.5)),
            common_side=6,
            common_shift=(0.25, 0.25),
            baseline_duration=0.4,
            horizon_variants=(0.2, 0.4, 0.6),
            observation_interval=0.1,
            feature_interval=0.2,
            cadence_feature_counts=(2, 3, 5),
            thresholds=(-1.0, 0.0, 1.0, 2.0, 3.0),
            reference_threshold=1.0,
            energy_bin_count=3,
        )
        cls.report = build_persistence_report(
            cls.config,
            DoublePendulumParameters(),
            IntegrationConfig(
                rtol=1.0e-8,
                atol=1.0e-10,
                max_step=0.03,
                energy_drift_tolerance=1.0e-7,
            ),
        )

    def test_report_uses_one_declared_common_evaluation_grid(self) -> None:
        common = self.report["common_evaluation_grid"]
        self.assertEqual(common["side"], 6)
        self.assertEqual(common["shift_in_common_cells"], [0.25, 0.25])
        self.assertFalse(common["categorical_component_identities_transferred"])
        self.assertFalse(common["categorical_source_masks_transported"])
        for row in self.report["runs"]:
            self.assertEqual(np.asarray(row["common_log_stretch"]).shape, (6, 6))
            source = np.asarray(row["source_log_stretch"])
            mask = np.asarray(row["source_no_sampled_full_turn_mask"])
            self.assertEqual(mask.shape, source.shape)
            self.assertEqual(mask.dtype, np.bool_)
            self.assertEqual(
                row["source_no_sampled_full_turn_fraction"], float(np.mean(mask))
            )
            self.assertEqual(
                row["source_reference_threshold_marked_count"],
                int(
                    np.count_nonzero(
                        (source <= self.config.reference_threshold) & mask
                    )
                ),
            )
            self.assertEqual(
                len(row["threshold_filtration_on_common_grid"]),
                len(self.config.thresholds),
            )

    def test_resolution_shift_and_cadence_ledgers_are_separate(self) -> None:
        self.assertEqual(
            {row["side"] for row in self.report["resolution_study"]["runs"]},
            {3, 4},
        )
        self.assertEqual(len(self.report["shift_study"]["runs"]), 2)
        self.assertEqual(
            {
                row["feature_sample_count"]
                for row in self.report["cadence_study"]["runs"]
            },
            {2, 3, 5},
        )
        for study, comparison_key in (
            ("resolution_study", "comparison_to_highest_resolution"),
            ("shift_study", "comparison_to_unshifted"),
            ("cadence_study", "comparison_to_densest"),
        ):
            self.assertTrue(
                all(comparison_key in row for row in self.report[study]["runs"])
            )

    def test_horizon_is_continuation_without_a_pass_fail_gate(self) -> None:
        continuation = self.report["horizon_continuation"]
        self.assertFalse(continuation["has_numerical_pass_fail_status"])
        self.assertIn("different declared protocols", continuation["interpretation"])
        self.assertEqual(
            [row["duration"] for row in continuation["runs"]],
            [0.2, 0.4, 0.6],
        )
        self.assertTrue(all("passed" not in row for row in continuation["runs"]))
        self.assertNotIn("comparison_to_previous_horizon", continuation["runs"][0])
        self.assertIn("comparison_to_previous_horizon", continuation["runs"][1])

    def test_report_is_tier1_and_survives_json_roundtrip(self) -> None:
        self.assertEqual(self.report["claim_tier"], 1)
        self.assertEqual(self.report["proof_boundary"], TIER1_BOUNDARY)
        verification = verify_persistence_report(self.report)
        self.assertTrue(verification["passed"], verification)
        self.assertFalse(verification["declared_ode_to_fields_verified"])
        self.assertFalse(verification["outward_flow_enclosure_verified"])
        roundtrip = json.loads(json.dumps(self.report))
        self.assertTrue(verify_persistence_report(roundtrip)["passed"])

    def test_tampered_common_field_and_horizon_semantics_are_rejected(self) -> None:
        tampered = deepcopy(self.report)
        tampered["runs"][0]["common_log_stretch"][0][0] += 0.1
        self.assertFalse(verify_persistence_report(tampered)["passed"])

        tampered = deepcopy(self.report)
        tampered["horizon_continuation"]["has_numerical_pass_fail_status"] = True
        self.assertFalse(verify_persistence_report(tampered)["passed"])

        tampered = deepcopy(self.report)
        tampered["parameters"]["g"] += 0.1
        self.assertFalse(verify_persistence_report(tampered)["passed"])

        tampered = deepcopy(self.report)
        tampered["runs"][0]["source_no_sampled_full_turn_fraction"] = 0.123456
        self.assertFalse(verify_persistence_report(tampered)["passed"])

        tampered = deepcopy(self.report)
        tampered["runs"][0]["source_reference_threshold_marked_count"] += 1
        self.assertFalse(verify_persistence_report(tampered)["passed"])

        tampered = deepcopy(self.report)
        tampered["physical_flow_certified"] = True
        self.assertFalse(verify_persistence_report(tampered)["passed"])

    def test_numeric_strings_and_boolean_integers_are_rejected(self) -> None:
        tampered = deepcopy(self.report)
        tampered["parameters"]["g"] = str(tampered["parameters"]["g"])
        self.assertFalse(verify_persistence_report(tampered)["passed"])

        tampered = deepcopy(self.report)
        tampered["integration"]["rtol"] = str(tampered["integration"]["rtol"])
        self.assertFalse(verify_persistence_report(tampered)["passed"])

        tampered = deepcopy(self.report)
        tampered["config"]["reference_threshold"] = str(
            tampered["config"]["reference_threshold"]
        )
        self.assertFalse(verify_persistence_report(tampered)["passed"])

        tampered = deepcopy(self.report)
        tampered["runs"][0]["spec"]["duration"] = str(
            tampered["runs"][0]["spec"]["duration"]
        )
        self.assertFalse(verify_persistence_report(tampered)["passed"])

        tampered = deepcopy(self.report)
        # False compares equal to integer zero unless the schema checks types.
        tampered["runs"][0]["feature_sample_indices"][0] = False
        self.assertFalse(verify_persistence_report(tampered)["passed"])

        tampered = deepcopy(self.report)
        tampered["runs"][0]["spec"]["observation_count"] = True
        self.assertFalse(verify_persistence_report(tampered)["passed"])


if __name__ == "__main__":
    unittest.main()
