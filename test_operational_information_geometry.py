#!/usr/bin/env python3

import math
import unittest

import numpy as np

from operational_information_geometry import (
    binary_gaussian_error,
    degree_preserving_control,
    edge_locality_auc,
    factorization_universe,
    operational_geometry,
    pairwise_spearman,
    rademacher_measurements,
    run_reference_experiment,
    spectral_dimension_estimate,
    stable_observable_modes,
)


class OperationalInformationGeometryTests(unittest.TestCase):
    def test_factorization_universe_is_a_cartesian_prime_box(self) -> None:
        universe = factorization_universe((2, 3), 4)
        self.assertEqual(universe.state_count, 16)
        self.assertEqual(len(universe.edges), 2 * 3 * 4)
        self.assertEqual(len(set(universe.labels)), universe.state_count)
        self.assertTrue(np.allclose(universe.laplacian, universe.laplacian.T))
        self.assertTrue(np.allclose(np.sum(universe.laplacian, axis=1), 0.0))

    def test_degree_preserving_control_preserves_declared_nuisances(self) -> None:
        universe = factorization_universe((2, 3, 5), 4)
        control = degree_preserving_control(universe, swap_multiplier=5, seed=7)
        np.testing.assert_array_equal(
            np.sum(universe.adjacency, axis=1),
            np.sum(control.adjacency, axis=1),
        )
        self.assertEqual(universe.labels, control.labels)
        np.testing.assert_array_equal(universe.coordinates, control.coordinates)
        self.assertNotEqual(universe.edges, control.edges)

    def test_observable_history_induces_the_declared_gram_distance(self) -> None:
        universe = factorization_universe((2, 3), 3)
        measurements = rademacher_measurements(universe.state_count, 4, seed=2)
        geometry = operational_geometry(
            universe.laplacian, measurements, [0.5, 1.0, 2.0]
        )
        self.assertGreaterEqual(
            float(np.linalg.eigvalsh(geometry.gram)[0]), -1e-12
        )
        for left, right in [(0, 1), (2, 7), (3, 8)]:
            direct = np.linalg.norm(
                geometry.observability_matrix[:, left]
                - geometry.observability_matrix[:, right]
            )
            self.assertAlmostEqual(
                geometry.distances[left, right], direct, places=13
            )

    def test_indistinguishable_states_are_quotiented(self) -> None:
        laplacian = np.zeros((2, 2))
        geometry = operational_geometry(
            laplacian, np.asarray([[1.0, 1.0]]), [0.0, 1.0]
        )
        self.assertAlmostEqual(geometry.distances[0, 1], 0.0)
        self.assertEqual(np.linalg.matrix_rank(geometry.observability_matrix), 1)

    def test_factorization_spectrum_has_one_slow_mode_per_prime_direction(self) -> None:
        universe = factorization_universe((2, 3, 5), 6)
        eigenvalues = np.linalg.eigvalsh(universe.laplacian)
        expected_gap = 2.0 - 2.0 * math.cos(math.pi / 6.0)
        self.assertAlmostEqual(eigenvalues[1], expected_gap, places=12)
        self.assertEqual(np.count_nonzero(np.isclose(eigenvalues, expected_gap)), 3)

    def test_spectral_dimension_and_stable_modes_recover_three_directions(self) -> None:
        universe = factorization_universe((2, 3, 5), 6)
        measurements = rademacher_measurements(universe.state_count, 32)
        geometry = operational_geometry(
            universe.laplacian, measurements, np.geomspace(1.0, 8.0, 14)
        )
        dimension, deviation = spectral_dimension_estimate(
            geometry.eigenvalues, np.geomspace(0.03, 20.0, 120)
        )
        self.assertGreater(dimension, 2.8)
        self.assertLess(dimension, 3.1)
        self.assertLess(deviation, 0.1)
        self.assertEqual(len(stable_observable_modes(geometry)), 3)

    def test_compressed_geometry_recovers_locality(self) -> None:
        universe = factorization_universe((2, 3, 5), 5)
        times = np.geomspace(1.0, 6.0, 10)
        compressed = operational_geometry(
            universe.laplacian,
            rademacher_measurements(universe.state_count, 24),
            times,
        )
        full = operational_geometry(
            universe.laplacian, np.eye(universe.state_count), times
        )
        self.assertGreater(
            pairwise_spearman(compressed.distances, full.distances), 0.85
        )
        self.assertGreater(edge_locality_auc(universe, compressed.distances), 0.98)

    def test_binary_gaussian_error_has_expected_two_sigma_value(self) -> None:
        self.assertAlmostEqual(
            binary_gaussian_error(4.0, 1.0), 0.022750131948179195
        )

    def test_small_reference_audit_preserves_the_falsification_boundary(self) -> None:
        report = run_reference_experiment(control_count=4)
        arithmetic = report["arithmetic_factorization_universe"]
        control = report["representative_degree_preserving_control"]
        self.assertGreater(arithmetic["edge_locality_auc"], 0.99)
        self.assertGreater(control["edge_locality_auc"], 0.95)
        self.assertGreater(
            arithmetic["compressed_vs_original_exponent_distance_spearman"],
            control["compressed_vs_original_exponent_distance_spearman"],
        )
        self.assertEqual(arithmetic["stable_observable_mode_count"], 3)
        self.assertGreater(
            report["control_ensemble"]["spectral_dimension_1_to_3"]["minimum"],
            5.0,
        )


if __name__ == "__main__":
    unittest.main()
