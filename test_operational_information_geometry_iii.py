#!/usr/bin/env python3

import unittest

import numpy as np
from scipy.linalg import expm

from operational_information_geometry import factorization_universe
from operational_information_geometry_iii import (
    adaptive_multiscale_design,
    cartesian_local_history,
    diagonal_markov_interaction_laplacian,
    history_metric,
    independent_generator,
    interaction_visibility_audit,
    marginal_measurements,
    markov_interaction_control,
    mixed_dissipative_generator,
    mixed_spectral_curvature,
    product_composition_audit,
    run_stage_3_experiment,
    spectral_interaction_audit,
    tensor_history,
)


class OperationalInformationGeometryIIITests(unittest.TestCase):
    def setUp(self) -> None:
        self.left = factorization_universe((2,), 6)
        self.right = factorization_universe((3,), 6)

    def test_independent_semigroup_factors_exactly(self) -> None:
        generator = independent_generator(
            self.left.laplacian, self.right.laplacian
        )
        time = 0.37
        expected = np.kron(
            expm(-time * self.left.laplacian),
            expm(-time * self.right.laplacian),
        )
        np.testing.assert_allclose(expm(-time * generator), expected, atol=2e-14)

    def test_cartesian_and_tensor_history_laws(self) -> None:
        rng = np.random.default_rng(8)
        left_history = rng.normal(size=(7, 3))
        right_history = rng.normal(size=(5, 4))
        cartesian = history_metric(
            cartesian_local_history(left_history, right_history)
        )
        left_metric = history_metric(left_history)
        right_metric = history_metric(right_history)
        for left, right, other_left, other_right in [
            (0, 0, 1, 2),
            (2, 3, 0, 1),
            (1, 2, 1, 0),
        ]:
            first = left * 4 + right
            second = other_left * 4 + other_right
            self.assertAlmostEqual(
                cartesian.distances[first, second] ** 2,
                left_metric.distances[left, other_left] ** 2
                + right_metric.distances[right, other_right] ** 2,
                places=12,
            )

        tensor = history_metric(tensor_history(left_history, right_history))
        np.testing.assert_allclose(
            tensor.gram,
            np.kron(left_metric.gram, right_metric.gram),
            atol=2e-12,
        )

    def test_local_composition_has_exact_correlation_kernel(self) -> None:
        report = product_composition_audit(
            self.left.laplacian,
            self.right.laplacian,
            np.geomspace(0.02, 1.0, 8),
        )
        local = report["cartesian_local_protocol"]
        self.assertLess(local["maximum_squared_distance_additivity_error"], 1e-12)
        self.assertEqual(local["history_rank"], 11)
        self.assertEqual(local["correlation_kernel_dimension"], 25)
        tensor = report["two_clock_tensor_protocol"]
        self.assertLess(tensor["relative_gram_factorization_error"], 1e-12)

    def test_mixed_generator_is_psd_conservative_and_marginal_blind(self) -> None:
        generator = mixed_dissipative_generator(
            self.left.laplacian, self.right.laplacian, 0.4
        )
        self.assertGreaterEqual(float(np.linalg.eigvalsh(generator)[0]), -1e-12)
        np.testing.assert_allclose(np.sum(generator, axis=1), 0.0, atol=1e-13)
        left_marginal, right_marginal, _ = marginal_measurements(6, 6)
        interaction = np.kron(self.left.laplacian, self.right.laplacian)
        np.testing.assert_allclose(left_marginal @ interaction, 0.0, atol=1e-13)
        np.testing.assert_allclose(right_marginal @ interaction, 0.0, atol=1e-13)

    def test_true_markov_interaction_is_positive_and_changes_marginals(self) -> None:
        interaction = diagonal_markov_interaction_laplacian(6, 6)
        off_diagonal = interaction - np.diag(np.diag(interaction))
        self.assertLessEqual(float(np.max(off_diagonal)), 0.0)
        report = markov_interaction_control(
            self.left.laplacian,
            self.right.laplacian,
            np.geomspace(0.02, 1.0, 8),
            0.4,
        )
        self.assertTrue(report["generator_is_graph_laplacian"])
        self.assertGreaterEqual(
            report["minimum_transition_kernel_entry_at_time_0_1"], -1e-14
        )
        self.assertGreater(report["local_marginal_relative_history_change"], 0.1)

    def test_mixed_spectral_curvature_cancels_additive_parts(self) -> None:
        left_values = np.linalg.eigvalsh(self.left.laplacian)
        right_values = np.linalg.eigvalsh(self.right.laplacian)
        strength = 0.4
        grid = (
            left_values[:, None]
            + right_values[None, :]
            + strength * left_values[:, None] * right_values[None, :]
        )
        curvature = mixed_spectral_curvature(left_values, right_values, grid)
        np.testing.assert_allclose(
            curvature,
            strength * left_values[:, None] * right_values[None, :],
            atol=2e-14,
        )
        self.assertTrue(np.allclose(curvature[0, :], 0.0))
        self.assertTrue(np.allclose(curvature[:, 0], 0.0))

    def test_random_joint_sensors_recover_interaction_strength(self) -> None:
        report = spectral_interaction_audit(
            self.left.laplacian, self.right.laplacian, 0.4, sensor_count=4
        )
        self.assertLess(report["maximum_exact_curvature_formula_error"], 1e-13)
        self.assertLess(report["maximum_recovered_strength_error"], 1e-12)

    def test_local_history_is_blind_while_joint_history_changes(self) -> None:
        report = interaction_visibility_audit(
            self.left.laplacian,
            self.right.laplacian,
            np.geomspace(0.02, 1.0, 8),
            strengths=(0.0, 0.4),
        )
        coupled = report["strength_sweep"][1]
        self.assertLess(coupled["local_marginal_relative_history_change"], 1e-12)
        self.assertGreater(coupled["complete_relative_gram_change"], 0.08)
        self.assertGreater(coupled["random_joint_relative_gram_change"], 0.08)

    def test_adaptive_multiscale_design_beats_every_single_scale(self) -> None:
        left_values = np.linalg.eigvalsh(self.left.laplacian)
        right_values = np.linalg.eigvalsh(self.right.laplacian)
        rates = [
            left_values[i] + right_values[j] + 0.4 * left_values[i] * right_values[j]
            for i in range(1, 6)
            for j in range(1, 6)
        ]
        report = adaptive_multiscale_design(rates)
        self.assertEqual(sum(report["dyadic_numerators"]), 4096)
        self.assertGreater(report["dyadic_improvement_over_best_single"], 2.5)
        self.assertEqual(report["all_modes_audited"], 25)
        self.assertEqual(len(report["active_schedule_centers"]), 4)

    def test_reference_report_keeps_scope_and_falsification_controls(self) -> None:
        report = run_stage_3_experiment(0.4)
        self.assertIn("no claim", report["scope"])
        self.assertEqual(
            report["independent_composition"]["cartesian_local_protocol"]
            ["correlation_kernel_dimension"],
            25,
        )
        self.assertGreater(
            report["positive_multiscale_interaction_design"]
            ["dyadic_improvement_over_best_single"],
            2.5,
        )


if __name__ == "__main__":
    unittest.main()
