#!/usr/bin/env python3

import math
import unittest

import numpy as np
from scipy.linalg import expm

from double_pendulum_dynamics import (
    DoublePendulumParameters,
    IntegrationConfig,
    double_pendulum_rhs,
    simulate_double_pendulum,
)
from double_pendulum_variational import (
    TIER_1_SCOPE,
    PhaseObservationProtocol,
    analyze_phase_protocol,
    angle_slice_source_injection,
    double_pendulum_rhs_jacobian,
    phase_observation_jacobian,
    simulate_double_pendulum_variational,
)
from oig_double_pendulum_atlas import phase_observation


class AnalyticVariationalJacobianTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parameters = DoublePendulumParameters(
            m1=1.3, m2=0.8, l1=1.2, l2=0.7, g=9.81
        )

    def test_rhs_jacobian_matches_multiscale_centered_differences(self) -> None:
        states = (
            np.asarray([0.73, -0.41, 1.2, -0.6]),
            np.asarray([-2.1, 1.4, -3.0, 2.2]),
            np.asarray([1.2, 1.2, 0.1, -0.4]),
        )
        steps = (1.0e-3, 3.0e-4, 1.0e-4, 3.0e-5, 1.0e-5)
        basis = np.eye(4)
        for state in states:
            with self.subTest(state=state.tolist()):
                analytic = double_pendulum_rhs_jacobian(
                    0.0, state, self.parameters
                )
                errors = []
                for step in steps:
                    centered = np.column_stack(
                        [
                            (
                                double_pendulum_rhs(
                                    0.0,
                                    state + step * basis[column],
                                    self.parameters,
                                )
                                - double_pendulum_rhs(
                                    0.0,
                                    state - step * basis[column],
                                    self.parameters,
                                )
                            )
                            / (2.0 * step)
                            for column in range(4)
                        ]
                    )
                    errors.append(float(np.max(np.abs(centered - analytic))))
                self.assertLess(errors[-1], 3.0e-9)
                self.assertLess(errors[-1], errors[0] / 1000.0)
                np.testing.assert_array_equal(
                    analytic[:2],
                    np.asarray(
                        [[0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
                    ),
                )

    def test_phase_observation_jacobian_matches_centered_difference(self) -> None:
        state = np.asarray([0.73, -0.41, 1.2, -0.6])
        scale = 2.3
        step = 1.0e-6
        basis = np.eye(4)
        centered = np.column_stack(
            [
                (
                    phase_observation(
                        state + step * basis[column],
                        angular_velocity_scale=scale,
                    )
                    - phase_observation(
                        state - step * basis[column],
                        angular_velocity_scale=scale,
                    )
                )
                / (2.0 * step)
                for column in range(4)
            ]
        )
        np.testing.assert_allclose(
            phase_observation_jacobian(
                state, angular_velocity_scale=scale
            ),
            centered,
            rtol=2.0e-10,
            atol=8.0e-11,
        )

    def test_equilibrium_jacobian_has_known_normal_frequencies(self) -> None:
        parameters = DoublePendulumParameters(g=9.81)
        jacobian = double_pendulum_rhs_jacobian(
            0.0, np.zeros(4), parameters
        )
        squared_frequencies = np.sort(
            np.real(np.linalg.eigvals(-jacobian[2:, :2]))
        )
        expected = parameters.g * np.asarray(
            [2.0 - math.sqrt(2.0), 2.0 + math.sqrt(2.0)]
        )
        np.testing.assert_allclose(
            squared_frequencies, expected, rtol=2.0e-15, atol=2.0e-15
        )


class IntegratedTangentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parameters = DoublePendulumParameters(
            m1=1.3, m2=0.8, l1=1.2, l2=0.7, g=9.81
        )
        self.config = IntegrationConfig(
            rtol=2.0e-12,
            atol=2.0e-14,
            max_step=0.005,
            energy_drift_tolerance=1.0e-10,
        )

    def test_tangent_matches_multiscale_flow_differences(self) -> None:
        initial = np.asarray([0.7, -0.4, 0.2, -0.1])
        times = np.linspace(0.0, 0.8, 17)
        variational = simulate_double_pendulum_variational(
            initial, times, self.parameters, self.config
        )
        basis = np.eye(4)
        errors = []
        for step in (1.0e-3, 1.0e-4, 1.0e-5):
            columns = []
            for column in range(4):
                positive = simulate_double_pendulum(
                    initial + step * basis[column],
                    times,
                    self.parameters,
                    self.config,
                ).states
                negative = simulate_double_pendulum(
                    initial - step * basis[column],
                    times,
                    self.parameters,
                    self.config,
                ).states
                columns.append((positive - negative) / (2.0 * step))
            centered = np.stack(columns, axis=-1)
            errors.append(
                float(np.max(np.abs(centered - variational.tangents)))
            )
        self.assertLess(errors[-1], 2.0e-9)
        self.assertLess(errors[1], errors[0] / 50.0)
        self.assertLess(errors[2], errors[1] / 20.0)

    def test_time_zero_identity_and_equilibrium_matrix_exponential(self) -> None:
        parameters = DoublePendulumParameters(g=9.81)
        times = np.linspace(0.0, 1.0, 11)
        variational = simulate_double_pendulum_variational(
            np.zeros(4), times, parameters, self.config
        )
        np.testing.assert_array_equal(variational.tangents[0], np.eye(4))
        jacobian = double_pendulum_rhs_jacobian(0.0, np.zeros(4), parameters)
        expected = np.stack([expm(jacobian * time) for time in times])
        np.testing.assert_allclose(
            variational.tangents, expected, rtol=3.0e-13, atol=3.0e-13
        )
        self.assertEqual(variational.evidence_tier, TIER_1_SCOPE)

    def test_tangent_flow_obeys_composition(self) -> None:
        initial = np.asarray([0.7, -0.4, 0.2, -0.1])
        full = simulate_double_pendulum_variational(
            initial, [0.0, 0.35, 0.9], self.parameters, self.config
        )
        second_segment = simulate_double_pendulum_variational(
            full.states[1], [0.35, 0.9], self.parameters, self.config
        )
        np.testing.assert_allclose(
            second_segment.states[-1], full.states[-1], rtol=0.0, atol=3.0e-13
        )
        np.testing.assert_allclose(
            second_segment.tangents[-1] @ full.tangents[1],
            full.tangents[-1],
            rtol=2.0e-12,
            atol=2.0e-12,
        )

    def test_augmented_and_state_only_integrators_agree(self) -> None:
        initial = np.asarray([1.1, -0.7, 0.35, -0.2])
        times = np.linspace(0.0, 1.0, 21)
        variational = simulate_double_pendulum_variational(
            initial, times, self.parameters, self.config
        )
        ordinary = simulate_double_pendulum(
            initial, times, self.parameters, self.config
        )
        np.testing.assert_allclose(
            variational.states, ordinary.states, rtol=0.0, atol=2.0e-12
        )
        self.assertLess(variational.max_scaled_energy_drift, 1.0e-11)


class LocalOIGResponseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = IntegrationConfig(
            rtol=2.0e-12,
            atol=2.0e-14,
            max_step=0.005,
            energy_drift_tolerance=1.0e-10,
        )
        self.trajectory = simulate_double_pendulum_variational(
            [0.7, -0.4, 0.2, -0.1],
            [0.0, 0.15, 0.4],
            config=self.config,
        )

    def test_full_phase_sensor_has_declared_time_zero_gram(self) -> None:
        protocol = PhaseObservationProtocol(
            name="full phase at launch",
            sample_indices=(0,),
            sensor_matrix=np.eye(6),
            output_precision=np.eye(6),
            source_metric=np.eye(4),
            angular_velocity_scale=2.0,
        )
        analysis = analyze_phase_protocol(self.trajectory, protocol)
        np.testing.assert_allclose(
            analysis.information_gram,
            np.diag([1.0, 1.0, 0.25, 0.25]),
            rtol=0.0,
            atol=2.0e-16,
        )
        np.testing.assert_allclose(
            analysis.singular_values, [0.5, 0.5, 1.0, 1.0], atol=2.0e-16
        )
        np.testing.assert_array_equal(analysis.sample_times, [0.0])
        self.assertEqual(analysis.evidence_tier, TIER_1_SCOPE)

    def test_angle_slice_protocol_computes_dq_observation(self) -> None:
        protocol = PhaseObservationProtocol(
            name="two-angle atlas slice at launch",
            sample_indices=(0,),
            sensor_matrix=np.eye(6),
            output_precision=np.eye(6),
            source_metric=np.eye(2),
            source_injection=angle_slice_source_injection(),
            angular_velocity_scale=2.0,
        )
        analysis = analyze_phase_protocol(self.trajectory, protocol)
        self.assertEqual(analysis.response.shape, (6, 2))
        np.testing.assert_allclose(
            analysis.information_gram,
            np.eye(2),
            rtol=0.0,
            atol=2.0e-16,
        )
        np.testing.assert_allclose(analysis.singular_values, [1.0, 1.0])

    def test_source_injection_and_metric_must_describe_one_space(self) -> None:
        with self.assertRaises(ValueError):
            PhaseObservationProtocol(
                name="dimension mismatch",
                sample_indices=(0,),
                sensor_matrix=np.eye(6),
                output_precision=np.eye(6),
                source_metric=np.eye(4),
                source_injection=angle_slice_source_injection(),
            )
        with self.assertRaises(ValueError):
            PhaseObservationProtocol(
                name="rank deficient",
                sample_indices=(0,),
                sensor_matrix=np.eye(6),
                output_precision=np.eye(6),
                source_metric=np.eye(2),
                source_injection=np.zeros((4, 2)),
            )

    def test_output_coordinate_change_preserves_information(self) -> None:
        base = PhaseObservationProtocol(
            name="base",
            sample_indices=(1, 2),
            sensor_matrix=np.eye(6),
            output_precision=np.eye(12),
            source_metric=np.diag([2.0, 3.0, 4.0, 5.0]),
        )
        base_analysis = analyze_phase_protocol(self.trajectory, base)

        transform = np.asarray(
            [
                [2.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.2, 1.1, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.8, 0.0, 0.0, 0.0],
                [0.0, 0.0, -0.3, 1.4, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 1.3, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.4, 0.9],
            ]
        )
        inverse = np.linalg.inv(transform)
        transformed_precision = inverse.T @ inverse
        transformed_precision = 0.5 * (
            transformed_precision + transformed_precision.T
        )
        transformed = PhaseObservationProtocol(
            name="coordinate transformed",
            sample_indices=(1, 2),
            sensor_matrix=transform,
            output_precision=np.kron(np.eye(2), transformed_precision),
            source_metric=base.source_metric,
        )
        transformed_analysis = analyze_phase_protocol(
            self.trajectory, transformed
        )
        np.testing.assert_allclose(
            transformed_analysis.information_gram,
            base_analysis.information_gram,
            rtol=3.0e-15,
            atol=3.0e-15,
        )
        np.testing.assert_allclose(
            transformed_analysis.singular_values,
            base_analysis.singular_values,
            rtol=3.0e-15,
            atol=3.0e-15,
        )

    def test_partial_launch_sensor_exposes_blind_directions(self) -> None:
        first_angle_sensor = np.asarray([[1.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
        protocol = PhaseObservationProtocol(
            name="one scalar launch sensor",
            sample_indices=(0,),
            sensor_matrix=first_angle_sensor,
            output_precision=np.eye(1),
            source_metric=np.eye(4),
        )
        analysis = analyze_phase_protocol(self.trajectory, protocol)
        self.assertEqual(int(np.count_nonzero(analysis.singular_values)), 1)
        self.assertEqual(analysis.weakest_gain, 0.0)

    def test_protocol_rejects_invalid_metric_and_out_of_range_sample(self) -> None:
        with self.assertRaises(ValueError):
            PhaseObservationProtocol(
                name="bad precision",
                sample_indices=(0,),
                sensor_matrix=np.eye(6),
                output_precision=np.diag([1.0, 1.0, 1.0, 1.0, 1.0, -1.0]),
                source_metric=np.eye(4),
            )
        protocol = PhaseObservationProtocol(
            name="out of range",
            sample_indices=(5,),
            sensor_matrix=np.eye(6),
            output_precision=np.eye(6),
            source_metric=np.eye(4),
        )
        with self.assertRaises(ValueError):
            analyze_phase_protocol(self.trajectory, protocol)


if __name__ == "__main__":
    unittest.main()
