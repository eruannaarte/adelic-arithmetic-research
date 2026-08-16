import unittest

import numpy as np

from oig_double_pendulum_atlas import (
    build_operational_atlas,
    cell_centred_torus_grid,
    first_sampled_full_turn_excursion_indices,
    grid_edge_operational_log_stretch,
    phase_observation,
    toroidal_connected_components,
    trajectory_feature,
    wrap_angle,
)


class DoublePendulumAtlasPrimitiveTests(unittest.TestCase):
    def test_phase_observation_identifies_angle_seam(self):
        state = np.array([0.37, -1.1, -0.2, 0.4])
        shifted = state.copy()
        shifted[[0, 1]] += 2.0 * np.pi
        np.testing.assert_allclose(phase_observation(state), phase_observation(shifted), atol=2e-15)
        self.assertAlmostEqual(float(wrap_angle(np.pi)), -np.pi)

    def test_cell_grid_has_no_duplicated_seam(self):
        first, second, states = cell_centred_torus_grid(7)
        self.assertEqual(states.shape, (7, 7, 4))
        self.assertTrue(np.all(np.diff(first) > 0))
        self.assertTrue(np.all(first > -np.pi))
        self.assertTrue(np.all(first < np.pi))
        np.testing.assert_array_equal(first, second)

    def test_trajectory_feature_is_weight_normalized(self):
        values = np.zeros((3, 2, 2, 4))
        values[2, ..., 0] = np.pi / 2
        feature = trajectory_feature(values, (0, 2), sample_weights=(1, 3))
        self.assertEqual(feature.shape, (2, 2, 12))
        # Each phase observation has four unit-circle coordinates, independent of velocity.
        np.testing.assert_allclose(np.sum(feature * feature, axis=-1), 2.0)

    def test_first_full_turn_is_a_finite_horizon_event(self):
        values = np.zeros((5, 2, 2, 4))
        values[:, 0, 0, 0] = np.linspace(0, 2.1 * np.pi, 5)
        values[:, 1, 1, 1] = np.linspace(0, -2.2 * np.pi, 5)
        first, second = first_sampled_full_turn_excursion_indices(values)
        self.assertEqual(first[0, 0], 4)
        self.assertEqual(second[1, 1], 4)
        self.assertEqual(first[1, 1], -1)

    def test_toroidal_components_join_across_seam(self):
        mask = np.zeros((5, 5), dtype=bool)
        mask[0, 2] = True
        mask[-1, 2] = True
        mask[2, 2:4] = True
        labels, sizes = toroidal_connected_components(mask)
        self.assertEqual(sizes, (2, 2))
        self.assertEqual(labels[0, 2], labels[-1, 2])
        self.assertNotEqual(labels[0, 2], labels[2, 2])

    def test_constant_features_have_vanishing_stretch(self):
        features = np.zeros((6, 6, 4))
        stretch = grid_edge_operational_log_stretch(features, side=6)
        self.assertTrue(np.all(stretch < -700))

    def test_build_atlas_declares_threshold_and_scope(self):
        values = np.zeros((4, 5, 5, 4))
        atlas = build_operational_atlas(
            values,
            sample_indices=(0, 3),
            log_stretch_threshold=0.0,
        )
        self.assertTrue(np.all(atlas.low_stretch_no_sampled_full_turn_mask))
        with self.assertRaises(ValueError):
            trajectory_feature(values, (0.0, 3.0))
        with self.assertRaises(ValueError):
            atlas.log_stretch[0, 0] = 1.0
        self.assertEqual(atlas.component_sizes, (25,))
        summary = atlas.summary()
        self.assertEqual(
            summary["low_stretch_no_sampled_full_turn_cell_count"], 25
        )
        self.assertIn("not a Lyapunov-stability", summary["interpretation_boundary"])


if __name__ == "__main__":
    unittest.main()
