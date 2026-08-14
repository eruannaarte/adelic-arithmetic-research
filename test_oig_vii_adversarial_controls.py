"""Tests for the Stage VII mollifier falsification controls."""

import math
import unittest

import numpy as np

from oig_vii_adversarial_controls import (
    adjacent_split_atom,
    adjacent_split_laplacian_norm_squared,
    all_moment_profile,
    all_moment_source_norm,
    cell_average_gaussian,
    critical_alpha,
    density_mode_coefficient,
    gaussian_resolved_jet_constant,
    high_source_operator_gap,
    lattice_multiplication_limit,
    mean_preserving_gaussian_mixture,
    mixed_third_derivative_coefficient,
    naive_continuum_dispersion_limit,
    normalized_mixed_third_derivative_coefficient,
    path_laplacian_on_mass,
    point_sampled_gaussian,
    point_sampled_tent,
    pure_multiplication_moment,
    ramp_first_jet_norm,
    reduced_response_scalar,
)


class OIGVIIAdversarialControlTests(unittest.TestCase):
    def test_interior_boundary_and_split_atoms_have_different_constants(self):
        n = 2048
        interior = np.zeros(n)
        interior[n // 2] = 1
        boundary = np.zeros(n)
        boundary[0] = 1
        split = adjacent_split_atom(n, n // 2, 0.5)
        scale = n**2.5
        self.assertAlmostEqual(
            ramp_first_jet_norm(interior) / scale, 1 / math.sqrt(2), places=6
        )
        self.assertAlmostEqual(
            ramp_first_jet_norm(boundary) / scale, 1 / math.sqrt(6), places=6
        )
        self.assertAlmostEqual(
            ramp_first_jet_norm(split) / scale, 1 / math.sqrt(12), places=6
        )

    def test_two_cell_constant_depends_continuously_on_phase(self):
        for weight in (0.0, 0.2, 0.5, 0.8, 1.0):
            q = adjacent_split_atom(128, 60, weight)
            unscaled = np.linalg.norm(
                # Divide out n^2 from the scaled path Laplacian.
                path_laplacian_on_mass(q)
            ) / 128**2
            self.assertAlmostEqual(
                unscaled**2,
                adjacent_split_laplacian_norm_squared(weight),
                places=12,
            )

    def test_critical_cell_average_retains_lattice_phase(self):
        n = 1024
        width = 0.25 / n
        at_boundary = cell_average_gaussian(n, width, 0.5)
        at_centre = cell_average_gaussian(n, width, 0.5 + 0.5 / n)
        left = ramp_first_jet_norm(at_boundary) / n**2.5
        right = ramp_first_jet_norm(at_centre) / n**2.5
        self.assertGreater(abs(right - left), 0.3)

    def test_subcell_point_sampling_bifurcates_and_compact_sampling_can_fail(self):
        n = 256
        width = 0.05 / n
        boundary = point_sampled_gaussian(n, width, 0.5)
        centre = point_sampled_gaussian(n, width, 0.5 + 0.5 / n)
        self.assertAlmostEqual(float(np.max(boundary)), 0.5, places=12)
        self.assertAlmostEqual(float(np.max(centre)), 1.0, places=12)
        with self.assertRaises(ValueError):
            point_sampled_tent(n, 0.25 / n, 0.5)

    def test_resolved_smooth_gaussian_has_the_predicted_constant(self):
        n = 1024
        epsilon = 0.04
        q = cell_average_gaussian(n, epsilon, 0.5)
        scaled = epsilon**2.5 * ramp_first_jet_norm(q)
        self.assertLess(abs(scaled - gaussian_resolved_jet_constant()), 4e-5)

    def test_nonsymmetric_mean_preserving_kernel_breaks_parity_coefficients(self):
        n = 512
        epsilon = 0.04
        symmetric = cell_average_gaussian(n, epsilon, 0.5)
        asymmetric = mean_preserving_gaussian_mixture(n, epsilon, 0.5)
        self.assertLess(abs(density_mode_coefficient(symmetric, 3)), 2e-14)
        self.assertGreater(abs(density_mode_coefficient(asymmetric, 3)), 5e-4)

    def test_fixed_port_critical_limit_uses_lattice_dispersion(self):
        n = 256
        ratio = 0.5
        tau = 0.7
        value = reduced_response_scalar(
            n,
            n // 2,
            tau / n**2,
            1,
            (np.arange(n) + 0.5) / n,
            0.8,
        )
        lattice = lattice_multiplication_limit(ratio, tau)
        continuum = naive_continuum_dispersion_limit(ratio, tau)
        self.assertLess(abs(value - lattice), 4e-6)
        self.assertGreater(abs(value - continuum), 9e-3)

    def test_multiplication_reduction_is_not_full_operator_norm(self):
        self.assertGreater(high_source_operator_gap(0.5, 0.7), 0.1)

    def test_zero_coupling_and_reflection_null_sources_are_exact_controls(self):
        n = 128
        x = (np.arange(n) + 0.5) / n
        zero_coupling = reduced_response_scalar(n, 37, 0.3 / n**2, 1, x, 0.0)
        symmetric = reduced_response_scalar(
            n, 37, 0.3 / n**2, 1, (x - 0.5) ** 2, 0.8
        )
        self.assertLess(abs(zero_coupling), 2e-13)
        self.assertLess(abs(symmetric), 2e-13)

    def test_all_pure_moments_can_vanish_while_a_mixed_jet_survives(self):
        self.assertTrue(all_moment_profile(0.5) > 1)
        for power in range(1, 7):
            self.assertLess(abs(pure_multiplication_moment(power)), 2e-12)
        self.assertGreater(abs(mixed_third_derivative_coefficient()), 1e-2)
        self.assertAlmostEqual(all_moment_source_norm(), 0.517628923226115, places=12)
        self.assertGreater(
            abs(normalized_mixed_third_derivative_coefficient()), 2e-2
        )

    def test_declared_critical_exponent_is_algebraically_correct(self):
        self.assertEqual(critical_alpha(1), 4 / 5)
        self.assertEqual(critical_alpha(2), 8 / 9)


if __name__ == "__main__":
    unittest.main()
