import copy
import json
from pathlib import Path
import unittest

import numpy as np

from double_pendulum_dynamics import (
    DoublePendulumParameters,
    double_pendulum_rhs,
)
from oig_double_pendulum_parameter_sensitivity import (
    ACTIVE_PROTOCOL_NAMES,
    DEFAULT_SENSITIVITY_INTEGRATION,
    PROOF_BOUNDARY,
    SCHEMA_VERSION,
    TIER_1_SCOPE,
    analytic_protocol_response,
    build_parameter_sensitivity_report,
    canonical_active_protocols,
    centered_protocol_response,
    dimensionless_rhs,
    dimensionless_rhs_log_ratio_jacobian,
    physical_similarity_state,
    simulate_log_ratio_sensitivities,
    verify_parameter_sensitivity_report,
)
from oig_numerical_replay import numerically_equivalent_json


class AnalyticParameterForcingTests(unittest.TestCase):
    def test_log_ratio_forcing_matches_multiscale_centered_differences(self):
        cases = (
            ([0.4, -0.7, 0.8, -0.3], 0.2, -0.1),
            ([-1.2, 0.5, -0.4, 1.1], -0.3, 0.4),
            ([2.2, -2.4, 1.7, -1.3], 0.5, -0.6),
        )
        steps = (1.0e-3, 5.0e-4, 2.5e-4, 1.25e-4, 6.25e-5)
        for state, u, v in cases:
            analytic = dimensionless_rhs_log_ratio_jacobian(0.0, state, u, v)
            errors = []
            for step in steps:
                columns = []
                for coordinate in range(2):
                    plus = [u, v]
                    minus = [u, v]
                    plus[coordinate] += step
                    minus[coordinate] -= step
                    columns.append(
                        (
                            dimensionless_rhs(0.0, state, *plus)
                            - dimensionless_rhs(0.0, state, *minus)
                        )
                        / (2.0 * step)
                    )
                finite_difference = np.column_stack(columns)
                errors.append(float(np.max(np.abs(finite_difference - analytic))))
            self.assertLess(errors[-1], 3.0e-9)
            for earlier, later in zip(errors, errors[1:]):
                self.assertLess(later, 0.27 * earlier)

    def test_common_mass_scale_is_an_exact_vector_field_blind_direction(self):
        state = np.asarray([0.7, -0.4, 1.2, -0.8])
        reference = double_pendulum_rhs(
            0.0,
            state,
            DoublePendulumParameters(m1=1.0, m2=1.7, l1=1.4, l2=0.8, g=7.1),
        )
        for common_scale in (0.2, 3.0, 11.0):
            scaled = double_pendulum_rhs(
                0.0,
                state,
                DoublePendulumParameters(
                    m1=common_scale,
                    m2=1.7 * common_scale,
                    l1=1.4,
                    l2=0.8,
                    g=7.1,
                ),
            )
            np.testing.assert_allclose(scaled, reference, rtol=2.0e-15, atol=2.0e-15)


class IntegratedParameterSensitivityTests(unittest.TestCase):
    def test_active_protocol_contract_is_exact(self):
        protocols = canonical_active_protocols()
        self.assertEqual(tuple(candidate.name for candidate in protocols), ACTIVE_PROTOCOL_NAMES)
        self.assertEqual(protocols[0].sensor, "theta_2")
        self.assertEqual(protocols[0].observation_time_tau.numerator, 1)
        self.assertEqual(protocols[0].observation_time_tau.denominator, 1)
        self.assertEqual(protocols[1].sensor, "scaled_omega_1")
        self.assertEqual(protocols[1].observation_time_tau.numerator, 5)
        self.assertEqual(protocols[1].observation_time_tau.denominator, 4)

    def test_fixed_launch_sensitivity_matches_multiscale_flow_differences(self):
        refined = DEFAULT_SENSITIVITY_INTEGRATION.refined()
        for candidate in canonical_active_protocols():
            analytic, trajectory = analytic_protocol_response(
                candidate, integration=refined
            )
            self.assertTrue(np.array_equal(trajectory.sensitivities[0], np.zeros((4, 2))))
            errors = []
            for step in (8.0e-4, 4.0e-4, 2.0e-4, 1.0e-4):
                finite_difference, _drift = centered_protocol_response(
                    candidate, step, integration=refined
                )
                errors.append(float(np.max(np.abs(finite_difference - analytic))))
            self.assertLess(errors[-1], 8.0e-9)
            for earlier, later in zip(errors, errors[1:]):
                self.assertLess(later, 0.27 * earlier)

    def test_responses_reproduce_the_prior_discovery_values(self):
        expected = (
            np.asarray([0.08450255098685355, -0.4543512456345322]),
            np.asarray([0.4690547376806631, 0.004140129367113943]),
        )
        refined = DEFAULT_SENSITIVITY_INTEGRATION.refined()
        for candidate, prior in zip(canonical_active_protocols(), expected):
            analytic, _trajectory = analytic_protocol_response(
                candidate, integration=refined
            )
            np.testing.assert_allclose(analytic, prior, rtol=0.0, atol=8.0e-9)

    def test_physical_time_and_velocity_scalings_recover_the_tau_state(self):
        refined = DEFAULT_SENSITIVITY_INTEGRATION.refined()
        variants = (
            (0.2, 1.0, 1.0),
            (5.0, 1.0, 1.0),
            (1.0, 0.4, 3.2),
            (1.0, 2.5, 7.7),
            (3.0, 1.7, 4.6),
        )
        for candidate in canonical_active_protocols():
            reference, _ = physical_similarity_state(
                candidate, integration=refined
            )
            for common_mass, first_length, gravity in variants:
                state, _ = physical_similarity_state(
                    candidate,
                    common_mass_scale=common_mass,
                    first_length=first_length,
                    gravity=gravity,
                    integration=refined,
                )
                np.testing.assert_allclose(state, reference, rtol=0.0, atol=2.0e-12)

    def test_parameter_sensitivity_trajectory_rejects_nonfixed_launch_shape(self):
        with self.assertRaises(ValueError):
            simulate_log_ratio_sensitivities([0.0, 0.0, 0.0], [0.0, 1.0])


class ParameterSensitivityReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_parameter_sensitivity_report()

    def test_report_resolves_all_declared_tier1_gates(self):
        report = self.report
        self.assertEqual(report["schema_version"], SCHEMA_VERSION)
        self.assertEqual(report["status"], "resolved")
        self.assertEqual(report["evidence_tier"], TIER_1_SCOPE)
        self.assertEqual(report["proof_boundary"], PROOF_BOUNDARY)
        self.assertTrue(all(row["gates_passed"] for row in report["active_protocols"]))
        self.assertTrue(
            report["common_mass_and_dimensionless_similarity_control"]["gate_passed"]
        )

    def test_report_preserves_the_outward_validation_boundary(self):
        outward = self.report["outward_validation"]
        self.assertFalse(outward["state_enclosed"])
        self.assertFalse(outward["parameter_sensitivity_enclosed"])
        self.assertFalse(outward["exact_response_box_membership_certified"])
        self.assertFalse(
            self.report["internal_recomputation_verification"]["outward_validation_performed"]
        )

    def test_recomputing_verifier_accepts_fresh_report_and_rejects_tampering(self):
        verification = verify_parameter_sensitivity_report(self.report)
        self.assertTrue(verification["passed"])
        self.assertFalse(verification["outward_validation_verified"])
        attacked = copy.deepcopy(self.report)
        attacked["active_protocols"][0]["refined_analytic_response"][0] += 1.0e-4
        rejected = verify_parameter_sensitivity_report(attacked)
        self.assertFalse(rejected["passed"])

    def test_canonical_artifact_is_fresh(self):
        path = Path("artifacts/double_pendulum_parameter_sensitivity_tier1.json")
        stored = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(numerically_equivalent_json(stored, self.report))


if __name__ == "__main__":
    unittest.main()
