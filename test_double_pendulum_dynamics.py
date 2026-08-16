#!/usr/bin/env python3

import math
import unittest
from dataclasses import replace
from unittest.mock import patch

import numpy as np

from double_pendulum_dynamics import (
    DoublePendulumParameters,
    EnergyDriftError,
    IntegrationConfig,
    bob_positions,
    double_pendulum_rhs,
    mass_matrix,
    refinement_diagnostic,
    simulate_double_pendulum,
    total_energy,
)


class DoublePendulumMechanicsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parameters = DoublePendulumParameters(
            m1=1.3, m2=0.8, l1=1.2, l2=0.7, g=9.81
        )

    def test_parameters_and_integration_controls_reject_invalid_values(self) -> None:
        for keyword in ("m1", "m2", "l1", "l2", "g"):
            with self.subTest(parameter=keyword):
                with self.assertRaises(ValueError):
                    DoublePendulumParameters(**{keyword: 0.0})
        with self.assertRaises(ValueError):
            IntegrationConfig(rtol=1.0)
        with self.assertRaises(ValueError):
            IntegrationConfig(atol=float("nan"))
        with self.assertRaises(ValueError):
            IntegrationConfig(max_step=-1.0)
        with self.assertRaises(ValueError):
            IntegrationConfig(energy_drift_tolerance=0.0)

    def test_mass_matrix_is_uniformly_symmetric_positive_definite(self) -> None:
        p = self.parameters
        for theta1 in np.linspace(-2.0 * math.pi, 2.0 * math.pi, 17):
            for theta2 in np.linspace(-math.pi, math.pi, 11):
                matrix = mass_matrix(theta1, theta2, p)
                np.testing.assert_array_equal(matrix, matrix.T)
                self.assertGreater(float(np.linalg.eigvalsh(matrix)[0]), 0.0)
                delta = theta1 - theta2
                expected_determinant = (
                    p.m2
                    * p.l1**2
                    * p.l2**2
                    * (p.m1 + p.m2 * math.sin(delta) ** 2)
                )
                self.assertAlmostEqual(
                    float(np.linalg.det(matrix)), expected_determinant, places=13
                )

    def test_rhs_obeys_the_euler_lagrange_matrix_equation(self) -> None:
        p = self.parameters
        state = np.asarray([0.73, -0.41, 1.2, -0.6])
        theta1, theta2, omega1, omega2 = state
        derivative = double_pendulum_rhs(2.7, state, p)
        delta = theta1 - theta2
        coupling = p.m2 * p.l1 * p.l2 * math.sin(delta)
        declared_forcing = np.asarray(
            [
                -coupling * omega2**2
                - (p.m1 + p.m2) * p.g * p.l1 * math.sin(theta1),
                coupling * omega1**2 - p.m2 * p.g * p.l2 * math.sin(theta2),
            ]
        )
        np.testing.assert_allclose(derivative[:2], state[2:], rtol=0.0, atol=0.0)
        np.testing.assert_allclose(
            mass_matrix(theta1, theta2, p) @ derivative[2:],
            declared_forcing,
            rtol=2.0e-15,
            atol=2.0e-15,
        )

    def test_energy_derivative_vanishes_along_the_vector_field(self) -> None:
        p = self.parameters
        states = (
            np.asarray([0.73, -0.41, 1.2, -0.6]),
            np.asarray([-2.1, 1.4, -3.0, 2.2]),
            np.asarray([math.pi / 2.0, -math.pi / 3.0, 0.1, 4.0]),
        )
        for state in states:
            theta1, theta2, omega1, omega2 = state
            delta = theta1 - theta2
            cross = p.m2 * p.l1 * p.l2
            angular_gradient = np.asarray(
                [
                    -cross * math.sin(delta) * omega1 * omega2
                    + (p.m1 + p.m2) * p.g * p.l1 * math.sin(theta1),
                    cross * math.sin(delta) * omega1 * omega2
                    + p.m2 * p.g * p.l2 * math.sin(theta2),
                ]
            )
            velocity_gradient = mass_matrix(theta1, theta2, p) @ state[2:]
            energy_gradient = np.concatenate((angular_gradient, velocity_gradient))
            energy_rate = float(
                energy_gradient @ double_pendulum_rhs(0.0, state, p)
            )
            self.assertAlmostEqual(energy_rate, 0.0, places=12)

    def test_equal_unit_pendulum_has_known_linearized_frequencies(self) -> None:
        p = DoublePendulumParameters(g=9.81)
        epsilon = 1.0e-6
        acceleration_jacobian = np.empty((2, 2))
        for column in range(2):
            positive = np.zeros(4)
            negative = np.zeros(4)
            positive[column] = epsilon
            negative[column] = -epsilon
            acceleration_jacobian[:, column] = (
                double_pendulum_rhs(0.0, positive, p)[2:]
                - double_pendulum_rhs(0.0, negative, p)[2:]
            ) / (2.0 * epsilon)
        squared_frequencies = np.sort(
            np.real(np.linalg.eigvals(-acceleration_jacobian))
        )
        expected = p.g * np.asarray([2.0 - math.sqrt(2.0), 2.0 + math.sqrt(2.0)])
        np.testing.assert_allclose(squared_frequencies, expected, rtol=2.0e-12)

    def test_positions_respect_both_rigid_rod_lengths(self) -> None:
        p = self.parameters
        states = np.asarray(
            [
                [0.0, 0.0, 0.0, 0.0],
                [math.pi / 2.0, -math.pi / 2.0, 4.0, -3.0],
                [0.7, -2.4, -1.0, 2.0],
            ]
        )
        positions = bob_positions(states, p)
        self.assertEqual(positions.shape, (3, 2, 2))
        np.testing.assert_allclose(
            np.linalg.norm(positions[:, 0, :], axis=1), p.l1, rtol=2.0e-15
        )
        np.testing.assert_allclose(
            np.linalg.norm(positions[:, 1, :] - positions[:, 0, :], axis=1),
            p.l2,
            rtol=2.0e-15,
        )
        np.testing.assert_allclose(
            positions[0], [[0.0, -p.l1], [0.0, -(p.l1 + p.l2)]], atol=0.0
        )

    def test_dynamics_and_energy_are_two_pi_periodic_in_each_angle(self) -> None:
        state = np.asarray([0.4, -1.7, 0.8, -0.2])
        shifted = state + np.asarray([4.0 * math.pi, -6.0 * math.pi, 0.0, 0.0])
        np.testing.assert_allclose(
            double_pendulum_rhs(0.0, state, self.parameters),
            double_pendulum_rhs(0.0, shifted, self.parameters),
            rtol=2.0e-14,
            atol=2.0e-14,
        )
        self.assertAlmostEqual(
            float(total_energy(state, self.parameters)),
            float(total_energy(shifted, self.parameters)),
            places=13,
        )


class DoublePendulumSimulationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parameters = DoublePendulumParameters()
        self.config = IntegrationConfig(
            rtol=2.0e-11,
            atol=2.0e-13,
            max_step=0.01,
            energy_drift_tolerance=1.0e-10,
        )

    def test_equilibrium_remains_stationary(self) -> None:
        times = np.linspace(0.0, 2.0, 41)
        trajectory = simulate_double_pendulum(
            [0.0, 0.0, 0.0, 0.0], times, self.parameters, self.config
        )
        np.testing.assert_array_equal(trajectory.states, np.zeros((len(times), 4)))
        self.assertEqual(trajectory.max_absolute_energy_drift, 0.0)
        self.assertFalse(trajectory.states.flags.writeable)
        self.assertFalse(trajectory.times.flags.writeable)

    def test_nonlinear_trajectory_passes_sampled_energy_audit(self) -> None:
        times = np.linspace(0.0, 5.0, 251)
        trajectory = simulate_double_pendulum(
            [1.1, -0.7, 0.35, -0.2], times, self.parameters, self.config
        )
        self.assertEqual(trajectory.states.shape, (251, 4))
        self.assertEqual(trajectory.positions.shape, (251, 2, 2))
        self.assertGreater(trajectory.energy_audit_sample_count, len(times))
        self.assertLess(
            trajectory.max_scaled_energy_drift,
            0.5 * self.config.energy_drift_tolerance,
        )
        self.assertLessEqual(
            float(np.max(np.abs(trajectory.energies - trajectory.energies[0]))),
            trajectory.max_absolute_energy_drift,
        )

    def test_time_reversal_returns_to_the_initial_state(self) -> None:
        times = np.linspace(0.0, 2.0, 101)
        initial = np.asarray([0.7, -0.4, 0.2, -0.1])
        forward = simulate_double_pendulum(
            initial, times, self.parameters, self.config
        )
        reversed_initial = forward.states[-1].copy()
        reversed_initial[2:] *= -1.0
        backward = simulate_double_pendulum(
            reversed_initial, times, self.parameters, self.config
        )
        expected = initial.copy()
        expected[2:] *= -1.0
        np.testing.assert_allclose(backward.states[-1], expected, atol=2.0e-10)

    def test_refinement_diagnostic_compares_the_same_observation_grid(self) -> None:
        times = np.linspace(0.0, 2.0, 81)
        coarse = IntegrationConfig(
            rtol=1.0e-8,
            atol=1.0e-10,
            max_step=0.03,
            energy_drift_tolerance=1.0e-6,
        )
        diagnostic = refinement_diagnostic(
            [0.9, -0.2, 0.4, -0.3],
            times,
            self.parameters,
            coarse_config=coarse,
            scaled_state_tolerance=1.0e-7,
        )
        self.assertTrue(diagnostic.passed)
        self.assertTrue(diagnostic.sampled_full_turn_events_consistent)
        np.testing.assert_array_equal(diagnostic.coarse.times, times)
        np.testing.assert_array_equal(diagnostic.fine.times, times)
        self.assertLess(diagnostic.max_scaled_state_discrepancy, 1.0e-8)
        self.assertLess(float(np.max(diagnostic.max_unwrapped_angle_discrepancy)), 1.0e-8)
        np.testing.assert_array_equal(
            diagnostic.coarse_first_sampled_full_turn_indices,
            diagnostic.fine_first_sampled_full_turn_indices,
        )

    def test_refinement_diagnostic_does_not_hide_a_full_turn_disagreement(self) -> None:
        times = np.linspace(0.0, 0.5, 11)
        config = IntegrationConfig(max_step=0.01)
        reference = simulate_double_pendulum(
            [0.2, -0.1, 0.0, 0.0], times, self.parameters, config
        )
        shifted_states = reference.states.copy()
        shifted_states[:, 0] += 2.0 * math.pi
        phase_equivalent = replace(reference, states=shifted_states)
        with patch(
            "double_pendulum_dynamics.simulate_double_pendulum",
            side_effect=(reference, phase_equivalent),
        ):
            diagnostic = refinement_diagnostic(
                reference.states[0],
                times,
                self.parameters,
                coarse_config=config,
                fine_config=config.refined(),
            )
        self.assertLess(diagnostic.max_scaled_state_discrepancy, 1.0e-14)
        self.assertAlmostEqual(
            diagnostic.max_unwrapped_angle_discrepancy[0], 2.0 * math.pi
        )
        self.assertTrue(diagnostic.sampled_full_turn_events_consistent)
        self.assertFalse(diagnostic.passed)

    def test_declared_energy_gate_rejects_an_underresolved_trajectory(self) -> None:
        loose = IntegrationConfig(
            rtol=1.0e-2,
            atol=1.0e-4,
            max_step=1.0,
            energy_drift_tolerance=1.0e-8,
        )
        with self.assertRaises(EnergyDriftError):
            simulate_double_pendulum(
                [1.4, -0.9, 1.0, -0.7],
                np.linspace(0.0, 8.0, 33),
                self.parameters,
                loose,
            )

    def test_simulation_rejects_ambiguous_or_nonfinite_inputs(self) -> None:
        with self.assertRaises(ValueError):
            simulate_double_pendulum([0.0, 0.0, 0.0], [0.0, 1.0])
        with self.assertRaises(ValueError):
            simulate_double_pendulum([0.0, 0.0, 0.0, 0.0], [0.0])
        with self.assertRaises(ValueError):
            simulate_double_pendulum(
                [0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.5]
            )
        with self.assertRaises(ValueError):
            simulate_double_pendulum(
                [0.0, 0.0, float("nan"), 0.0], [0.0, 1.0]
            )

    def test_refinement_rejects_an_identical_or_weaker_energy_configuration(self) -> None:
        times = np.linspace(0.0, 0.2, 5)
        with self.assertRaises(ValueError):
            refinement_diagnostic(
                [0.2, -0.1, 0.0, 0.0],
                times,
                self.parameters,
                coarse_config=self.config,
                fine_config=self.config,
            )
        weaker_energy = IntegrationConfig(
            rtol=self.config.rtol / 10,
            atol=self.config.atol / 10,
            max_step=self.config.max_step / 2,
            energy_drift_tolerance=None,
        )
        with self.assertRaises(ValueError):
            refinement_diagnostic(
                [0.2, -0.1, 0.0, 0.0],
                times,
                self.parameters,
                coarse_config=self.config,
                fine_config=weaker_energy,
            )


if __name__ == "__main__":
    unittest.main()
