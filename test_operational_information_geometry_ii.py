#!/usr/bin/env python3

import dataclasses
import unittest

import numpy as np

from operational_information_geometry import (
    factorization_universe,
    stable_observable_subspaces,
)
from operational_information_geometry_ii import (
    axis_blind_audit,
    axis_blind_measurements,
    complete_protocol,
    history_geometry,
    mixture_stability,
    mixture_tangent_basis,
    project_to_simplex,
    rademacher_protocol,
    run_stage_2_experiment,
    scale_invariant_distortion,
)


class OperationalInformationGeometryIITests(unittest.TestCase):
    def test_scale_invariant_distortion_ignores_global_units(self) -> None:
        distances = np.asarray(
            [[0.0, 1.0, 2.0], [1.0, 0.0, 3.0], [2.0, 3.0, 0.0]]
        )
        report = scale_invariant_distortion(7.0 * distances, distances)
        self.assertAlmostEqual(report["minimax_dilation"], 1.0)
        self.assertAlmostEqual(report["log_rms_distortion"], 0.0)
        self.assertAlmostEqual(report["minimax_global_scale"], 1.0 / 7.0)

    def test_tangent_basis_is_orthonormal_and_sum_free(self) -> None:
        basis = mixture_tangent_basis(12)
        np.testing.assert_allclose(basis.T @ basis, np.eye(11), atol=1e-13)
        np.testing.assert_allclose(np.ones(12) @ basis, 0.0, atol=1e-13)

    def test_stable_subspace_count_is_invariant_under_degenerate_rotation(self) -> None:
        universe = factorization_universe()
        times = np.geomspace(1.0, 8.0, 14)
        geometry = history_geometry(
            universe.laplacian,
            rademacher_protocol(universe.state_count, 32, len(times), 7, False),
            times,
        )
        original = stable_observable_subspaces(geometry)
        rng = np.random.default_rng(10)
        rotation, _ = np.linalg.qr(rng.normal(size=(3, 3)))
        eigenvectors = geometry.eigenvectors.copy()
        eigenvectors[:, 1:4] = eigenvectors[:, 1:4] @ rotation
        rotated = dataclasses.replace(geometry, eigenvectors=eigenvectors)
        changed = stable_observable_subspaces(rotated)
        self.assertEqual(original[0]["physicalized_dimension"], 3)
        self.assertEqual(changed[0]["physicalized_dimension"], 3)
        np.testing.assert_allclose(
            original[0]["observation_energy_eigenvalues"],
            changed[0]["observation_energy_eigenvalues"],
            rtol=1e-12,
        )

    def test_axis_blind_sensor_exactly_collapses_its_fibers(self) -> None:
        universe = factorization_universe()
        times = np.geomspace(0.02, 1.0, 10)
        matrix = axis_blind_measurements(universe.coordinates, 32, 0, 4)
        geometry = history_geometry(
            universe.laplacian, tuple(matrix for _ in times), times
        )
        reduced = np.delete(universe.coordinates, 0, axis=1)
        left = int(np.flatnonzero(np.all(reduced == [2, 3], axis=1))[0])
        same_fiber = np.flatnonzero(np.all(reduced == [2, 3], axis=1))
        for right in same_fiber:
            self.assertLess(
                np.linalg.norm(
                    geometry.observability_matrix[:, left]
                    - geometry.observability_matrix[:, right]
                ),
                1e-12,
            )
        subspaces = stable_observable_subspaces(geometry)
        self.assertEqual(
            sum(item["physicalized_dimension"] for item in subspaces), 2
        )

    def test_combined_axis_blind_protocols_separate_pure_states_not_mixtures(self) -> None:
        universe = factorization_universe()
        audit = axis_blind_audit(
            universe.coordinates,
            universe.laplacian,
            np.geomspace(0.02, 1.0, 10),
        )["combined_axis_blind_protocols"]
        self.assertEqual(audit["history_rank"], 91)
        self.assertEqual(audit["expected_history_rank"], 91)
        self.assertGreater(audit["pure_state_minimum_margin"], 1.0)
        self.assertEqual(audit["mixture_tangent_kernel_dimension"], 125)
        self.assertLess(audit["explicit_collision_signature_gap"], 1e-12)
        self.assertTrue(audit["collision_mixtures_are_nonnegative"])

    def test_early_refreshed_protocol_stabilizes_mixture_tangent(self) -> None:
        universe = factorization_universe()
        times = np.geomspace(0.02, 1.0, 14)
        repeated = history_geometry(
            universe.laplacian,
            rademacher_protocol(universe.state_count, 32, len(times), 19, False),
            times,
        )
        refreshed = history_geometry(
            universe.laplacian,
            rademacher_protocol(universe.state_count, 32, len(times), 19, True),
            times,
        )
        repeated_stability = mixture_stability(repeated)
        refreshed_stability = mixture_stability(refreshed)
        self.assertEqual(refreshed_stability["numerical_rank"], 215)
        self.assertLess(refreshed_stability["condition_number"], 20.0)
        self.assertGreater(
            repeated_stability["condition_number"]
            / refreshed_stability["condition_number"],
            1e6,
        )

    def test_simplex_projection_is_feasible_and_does_not_hurt_true_simplex_point(self) -> None:
        vector = np.asarray([1.2, -0.2, 0.4, -0.1])
        truth = np.asarray([0.7, 0.0, 0.3, 0.0])
        projected = project_to_simplex(vector)
        self.assertTrue(np.all(projected >= 0.0))
        self.assertAlmostEqual(float(np.sum(projected)), 1.0)
        self.assertLessEqual(
            np.linalg.norm(projected - truth), np.linalg.norm(vector - truth)
        )

    def test_small_stage_2_report_preserves_main_boundaries(self) -> None:
        report = run_stage_2_experiment(protocol_count=2)
        early = report["random_protocol_ensembles"]["early_refreshed_q32"]
        repeated = report["random_protocol_ensembles"]["early_repeated_q32"]
        self.assertLess(
            early["against_complete_observation"]["minimax_dilation"]["median"],
            repeated["against_complete_observation"]["minimax_dilation"]["median"],
        )
        self.assertEqual(
            report["adversarial_axis_blind_audit"]
            ["combined_axis_blind_protocols"]
            ["mixture_tangent_kernel_dimension"],
            125,
        )
        recovered = report["adjacent_mixture_recovery"]["protocols"]
        self.assertLess(
            recovered["early_refreshed"]["simulated_simplex_projected_l2_rmse"],
            0.12,
        )
        self.assertGreater(
            recovered["stage_1_late_repeated"]
            ["simulated_simplex_projected_l2_rmse"],
            0.9,
        )


if __name__ == "__main__":
    unittest.main()
