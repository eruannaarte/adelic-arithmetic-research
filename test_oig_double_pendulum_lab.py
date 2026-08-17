import copy
import unittest

import numpy as np

from double_pendulum_dynamics import DoublePendulumParameters, IntegrationConfig
from oig_double_pendulum_lab import (
    AtlasRunConfig,
    run_atlas_lab,
    verify_atlas_lab_report,
)


class DoublePendulumAtlasLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report, cls.atlas = run_atlas_lab(
            AtlasRunConfig(
                side=5,
                duration=0.4,
                observation_count=17,
                feature_sample_count=5,
                log_stretch_threshold=2.0,
                refinement_scaled_state_tolerance=2e-7,
            ),
            DoublePendulumParameters(),
            IntegrationConfig(
                rtol=1e-8,
                atol=1e-10,
                max_step=0.04,
                energy_drift_tolerance=1e-7,
            ),
        )

    def test_simulator_to_atlas_state_convention_is_end_to_end(self):
        self.assertEqual(
            self.report["state_convention"],
            ["theta1", "theta2", "omega1", "omega2"],
        )
        self.assertEqual(self.atlas.feature.shape[:2], (5, 5))
        self.assertEqual(self.atlas.feature.shape[-1], 30)
        self.assertTrue(np.all(np.isfinite(self.atlas.feature)))

    def test_numerical_quality_ledger_is_explicit(self):
        self.assertTrue(self.report["all_refinement_audits_passed"])
        self.assertLess(self.report["maximum_sampled_scaled_energy_drift"], 1e-7)
        self.assertEqual(len(self.report["refinement_audits"]), 25)
        self.assertTrue(
            all(
                row["sampled_full_turn_events_consistent"]
                for row in self.report["refinement_audits"]
            )
        )

    def test_raw_fields_and_interpretation_boundary_are_serialized(self):
        raw = self.report["raw_fields"]
        self.assertEqual(np.asarray(raw["grid_edge_log_stretch"]).shape, (5, 5))
        self.assertEqual(np.asarray(raw["initial_energy"]).shape, (5, 5))
        boundary = self.report["proof_boundary"]
        self.assertIn("not an interval enclosure", boundary)
        self.assertIn("not a Jacobian singular value", boundary)

    def test_report_self_verifies_and_raw_tampering_is_rejected(self):
        self.assertTrue(verify_atlas_lab_report(self.report)["passed"])
        self.assertFalse(
            self.report["internal_consistency_verification"][
                "physical_flow_enclosure_verified"
            ]
        )
        hostile = copy.deepcopy(self.report)
        hostile["raw_fields"][
            "resolved_low_stretch_no_sampled_full_turn_mask"
        ][0][0] ^= 1
        self.assertFalse(verify_atlas_lab_report(hostile)["passed"])

    def test_forged_gate_and_fractional_turn_index_are_rejected(self):
        forged = copy.deepcopy(self.report)
        forged["refinement_audits"][0]["max_scaled_state_discrepancy"] = 999.0
        self.assertFalse(verify_atlas_lab_report(forged)["passed"])
        fractional = copy.deepcopy(self.report)
        fractional["raw_fields"]["sampled_turn_excursion_arm_1"][0][0] = -1.7
        self.assertFalse(verify_atlas_lab_report(fractional)["passed"])

    def test_cross_field_and_metadata_tampering_are_rejected(self):
        mutations = []

        component = copy.deepcopy(self.report)
        component["refinement_audits"][0]["max_component_discrepancy"][2] = 999.0
        mutations.append(component)

        invalid_sentinel = copy.deepcopy(self.report)
        invalid_sentinel["raw_fields"]["sampled_turn_excursion_arm_1"][0][0] = -2
        mutations.append(invalid_sentinel)

        unlinked_turns = copy.deepcopy(self.report)
        unlinked_turns["refinement_audits"][0][
            "coarse_first_sampled_full_turn_indices"
        ] = [-999, -999]
        unlinked_turns["refinement_audits"][0][
            "fine_first_sampled_full_turn_indices"
        ] = [-999, -999]
        mutations.append(unlinked_turns)

        energy = copy.deepcopy(self.report)
        energy["raw_fields"]["initial_energy"] = np.zeros((5, 5)).tolist()
        energy["initial_energy_range"] = [0.0, 0.0]
        energy["reflection_audit"]["initial_energy_max_absolute_discrepancy"] = 0.0
        mutations.append(energy)

        embedded = copy.deepcopy(self.report)
        embedded["internal_consistency_verification"][
            "physical_flow_enclosure_verified"
        ] = True
        mutations.append(embedded)

        metadata = copy.deepcopy(self.report)
        metadata["dynamics_variant"] = "invented dissipative model"
        mutations.append(metadata)

        environment = copy.deepcopy(self.report)
        environment["environment"]["scipy"] = "unknown"
        mutations.append(environment)

        boolean_count = copy.deepcopy(self.report)
        boolean_count["unresolved_cell_count"] = False
        mutations.append(boolean_count)

        boolean_angle = copy.deepcopy(self.report)
        centre = next(
            row
            for row in boolean_angle["refinement_audits"]
            if row["initial_angles"] == [0.0, 0.0]
        )
        centre["initial_angles"] = [False, False]
        mutations.append(boolean_angle)

        negative_reflection = copy.deepcopy(self.report)
        negative_reflection["reflection_audit"]["tolerance"] = -1.0
        negative_reflection["reflection_audit"]["passed"] = False
        mutations.append(negative_reflection)

        for hostile in mutations:
            with self.subTest(error=verify_atlas_lab_report(hostile).get("error")):
                self.assertFalse(verify_atlas_lab_report(hostile)["passed"])


if __name__ == "__main__":
    unittest.main()
