#!/usr/bin/env python3

import unittest

import numpy as np

from operational_information_geometry_v import (
    causal_cone_scale_flow,
    continuum_first_response_derivative,
    conjugate_port_reciprocity_audit,
    cosine_modes,
    directed_response_scale_flow,
    discrete_first_response_derivative,
    equilibrium_path_sensor_audit,
    fixed_generator_amplitude_linearity_audit,
    modulation_symmetry_audit,
    path_laplacian,
    path_spectral_convergence_audit,
    scaled_path_eigenvalues,
    sparse_scaled_one_way_generator,
    spectral_dimension_scale_flow,
    transient_spectral_dimension,
)


class OperationalInformationGeometryVTests(unittest.TestCase):
    def test_cell_center_cosines_diagonalize_scaled_path_laplacian(self) -> None:
        side_length = 17
        modes = cosine_modes(side_length, range(side_length))
        eigenvalues = scaled_path_eigenvalues(side_length)
        np.testing.assert_allclose(modes.T @ modes, np.eye(side_length), atol=2e-14)
        np.testing.assert_allclose(
            side_length**2 * path_laplacian(side_length) @ modes,
            modes * eigenvalues,
            atol=2e-12,
        )

    def test_low_mode_spectral_error_obeys_rigorous_n_minus_two_bound(self) -> None:
        report = path_spectral_convergence_audit((8, 16, 32, 64), 5)
        rows = report["rows"]
        self.assertTrue(all(row["maximum_bound_violation"] <= 0.0 for row in rows))
        errors = [row["first_mode_relative_error"] for row in rows]
        self.assertTrue(all(left > right for left, right in zip(errors, errors[1:])))
        self.assertLess(errors[-1], 2.1e-4)

    def test_spectral_dimension_limits_do_not_commute(self) -> None:
        report = spectral_dimension_scale_flow((32, 64, 128, 256, 512), (1, 2, 3))
        mesoscopic = report["mesoscopic_rows"]
        self.assertGreater(mesoscopic[-1]["dimension_estimates"]["3"], 2.96)
        self.assertGreater(mesoscopic[-1]["dimension_estimates"]["2"], 1.97)
        fixed_n = report["fixed_n_small_time_rows"]
        self.assertTrue(
            all(
                left["three_factor_dimension"] > right["three_factor_dimension"]
                for left, right in zip(fixed_n, fixed_n[1:])
            )
        )
        self.assertLess(fixed_n[-1]["three_factor_dimension"], 0.002)

    def test_transient_dimension_is_additive_in_mesoscopic_product_limit(self) -> None:
        side_length = 512
        time = side_length ** -1.5
        spectrum = scaled_path_eigenvalues(side_length)
        one = transient_spectral_dimension(spectrum, 1, time)
        three = transient_spectral_dimension(spectrum, 3, time)
        self.assertAlmostEqual(one, 1.0, delta=0.03)
        self.assertAlmostEqual(three, 3.0, delta=0.04)

    def test_first_causal_jet_has_exact_continuum_parity_selection(self) -> None:
        continuum = continuum_first_response_derivative(5)
        self.assertEqual(continuum[1], 0.0)
        self.assertEqual(continuum[3], 0.0)
        coarse = discrete_first_response_derivative(32, 5)
        fine = discrete_first_response_derivative(128, 5)
        self.assertLess(
            float(np.max(np.abs(fine - continuum))),
            float(np.max(np.abs(coarse - continuum))) / 10.0,
        )
        self.assertLess(float(np.max(np.abs(fine - continuum))), 7e-5)
        self.assertLess(float(np.max(np.abs(fine[1::2]))), 2e-15)

    def test_normalized_directed_response_gram_converges(self) -> None:
        report = directed_response_scale_flow(
            side_lengths=(16, 32, 64),
            source_mode_count=5,
            reference_side_length=256,
        )
        rows = report["rows"]
        errors = [row["relative_gram_error_against_reference"] for row in rows]
        self.assertTrue(all(left > right for left, right in zip(errors, errors[1:])))
        self.assertLess(errors[-1], 2e-4)
        self.assertTrue(all(len(row["response_singular_values"]) == 5 for row in rows))
        self.assertTrue(all(row["response_singular_values"][-1] > 0.0 for row in rows))

    def test_scaled_one_way_generator_is_conservative_markov_laplacian(self) -> None:
        generator = sparse_scaled_one_way_generator(12).toarray()
        off_diagonal = generator - np.diag(np.diag(generator))
        np.testing.assert_allclose(generator, generator.T, atol=1e-13)
        np.testing.assert_allclose(np.sum(generator, axis=0), 0.0, atol=2e-12)
        self.assertLessEqual(float(np.max(off_diagonal)), 0.0)
        self.assertGreaterEqual(float(np.linalg.eigvalsh(generator)[0]), -2e-12)

    def test_poisson_jump_cone_becomes_trivial_but_actual_radius_stabilizes(self) -> None:
        report = causal_cone_scale_flow(
            side_lengths=(24, 48, 96),
            physical_times=(0.005,),
        )
        rows = report["rows"]
        actual = [row["actual_physical_radius"] for row in rows]
        poisson = [row["poisson_physical_radius"] for row in rows]
        self.assertLess(max(actual) - min(actual), 0.03)
        self.assertTrue(all(left < right for left, right in zip(poisson, poisson[1:])))
        self.assertTrue(rows[-1]["poisson_bound_is_domain_trivial"])
        self.assertLess(max(row["mass_error"] for row in rows), 1e-13)

    def test_fixed_linear_generator_has_no_nonlinear_amplitude_jet(self) -> None:
        report = fixed_generator_amplitude_linearity_audit()
        self.assertEqual(report["maximum_second_amplitude_difference"], 0.0)
        self.assertIn("intervention-dependent", report["required_extension"])

    def test_symmetric_modulation_hides_reflection_odd_sources(self) -> None:
        report = modulation_symmetry_audit()
        self.assertEqual(report["symmetric_response_rank"], 2)
        self.assertEqual(report["linear_response_rank"], 5)
        self.assertEqual(report["reflection_odd_tangent_dimension"], 3)
        self.assertEqual(
            report["exact_rank_lower_witness"]["scaled_integer_minor_determinant"],
            32,
        )
        self.assertEqual(
            report["exact_rank_lower_witness"]["unscaled_minor_determinant"],
            "32/125",
        )
        self.assertLess(report["maximum_reflection_odd_response"], 2e-15)
        self.assertEqual(report["generator_reflection_commutator_norm"], 0.0)
        self.assertEqual(report["modulation_reflection_commutator_norm"], 0.0)

    def test_path_activity_detects_arrow_at_stationary_target(self) -> None:
        report = equilibrium_path_sensor_audit()
        self.assertLess(report["endpoint_marginal_response_norm"], 2e-14)
        self.assertGreater(report["path_jump_rate_response_norm"], 0.1)
        self.assertGreaterEqual(report["path_jump_rate_response_rank"], 2)
        self.assertLess(report["modal_reduction_error"], 2e-14)

    def test_adjoint_ports_restore_reciprocity(self) -> None:
        report = conjugate_port_reciprocity_audit()
        self.assertLess(report["stacked_cross_response_norm"], 2e-14)
        self.assertGreater(report["localized_forward_response_norm"], 0.25)
        self.assertLess(report["localized_reverse_response_norm"], 2e-14)
        self.assertLess(report["maximum_reciprocity_error"], 2e-14)


if __name__ == "__main__":
    unittest.main()
