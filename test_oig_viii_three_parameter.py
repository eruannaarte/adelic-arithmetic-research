#!/usr/bin/env python3

import math
import unittest

import numpy as np

from oig_viii_three_parameter import (
    atomic_joint_squared_error_audit,
    balanced_squared_error_audit,
    comparison_point,
    continuum_endpoint_correction_audit,
    continuum_phase_norm,
    critical_width_preasymptotic_audit,
    direct_dense_modal_response,
    early_phase_constant,
    fixed_lattice_squared_error_audit,
    gaussian_cell_masses,
    gaussian_lattice_weights,
    lattice_continuum_bridge_rate_audit,
    lattice_phase_norm,
    null_and_symmetry_controls,
    nonuniform_large_time_counterexample,
    placement_counterexample,
    response_norms,
    safe_relative_error,
    scaled_modal_kernel,
    scaled_response_norms,
    target_coefficients,
    unresolved_continuum_counterexample,
    wandering_phase_counterexample,
)


class OIGVIIIThreeParameterTests(unittest.TestCase):
    def test_conservative_gaussian_masses_match_declared_point_limits(self) -> None:
        for n in (31, 63):
            for c in (0.0, 0.05, 0.5, 4.0):
                for theta in (0.0, 0.3, 0.5):
                    masses = gaussian_cell_masses(n, c, theta)
                    self.assertAlmostEqual(float(np.sum(masses)), 1.0, places=14)
                    self.assertTrue(np.all(masses >= 0.0))
            atom = gaussian_cell_masses(n, 0.0, 0.0)
            split = gaussian_cell_masses(n, 0.0, 0.5)
            self.assertEqual(int(np.count_nonzero(atom)), 1)
            self.assertEqual(int(np.count_nonzero(split)), 2)
            self.assertTrue(np.allclose(split[split > 0.0], 0.5))

    def test_infinite_lattice_weights_are_probability(self) -> None:
        for c in (0.0, 0.05, 0.5, 4.0):
            for theta in (-0.5, 0.0, 0.27, 0.5):
                offsets, masses = gaussian_lattice_weights(c, theta)
                self.assertEqual(offsets.shape, masses.shape)
                self.assertAlmostEqual(float(np.sum(masses)), 1.0, places=14)
                self.assertTrue(np.all(masses >= 0.0))

    def test_modal_reduction_matches_dense_kronecker_generator(self) -> None:
        n = 7
        tau = 0.17
        mode = 2
        masses = gaussian_cell_masses(n, 0.73, 0.31)
        kernel = scaled_modal_kernel(n, (tau,), (mode,))
        modal = kernel.values[0, :, 0] * target_coefficients(masses)
        dense = direct_dense_modal_response(n, tau, mode, masses)
        # The relative guard below is the meaningful identity check.  Keep
        # this absolute guard portable across BLAS/SciPy implementations.
        self.assertLess(float(np.max(np.abs(modal - dense))), 2e-13)
        self.assertLess(
            float(np.linalg.norm(modal - dense) / np.linalg.norm(dense)),
            3e-12,
        )

    def test_norm_normalizations_are_consistent(self) -> None:
        n = 31
        kernel = scaled_modal_kernel(n, (0.03, 0.3), (1, 2))
        masses = gaussian_cell_masses(n, 1.0, 0.2)
        raw = response_norms(kernel, masses)
        scaled = scaled_response_norms(kernel, masses)
        self.assertLess(float(np.max(np.abs(raw / math.sqrt(n) - scaled))), 1e-15)

    def test_triangle_decomposition_is_an_actual_upper_bound(self) -> None:
        kernel = scaled_modal_kernel(63, (0.03, 0.3, 3.0), (1, 2))
        for time_index in range(3):
            for c in (0.25, 1.0, 4.0):
                for theta in (0.0, 0.5):
                    for source_index in range(2):
                        point = comparison_point(
                            kernel, time_index, c, theta, source_index
                        )
                        self.assertGreaterEqual(point["triangle_slack"], -2e-18)

    def test_fixed_lattice_squared_residual_is_second_order(self) -> None:
        report = fixed_lattice_squared_error_audit(
            (31, 63, 127), (1.0,), (0.3,), (1,), (0.0, 0.3, 0.5)
        )
        for row in report["rows"]:
            self.assertAlmostEqual(
                row["empirical_residual_power_in_h"], 2.0, delta=0.01
            )
            first = row["first"]["residual_over_h_squared"]
            last = row["last"]["residual_over_h_squared"]
            self.assertAlmostEqual(last / first, 1.0, delta=0.01)

    def test_off_centre_conservative_phase_does_not_create_first_order_term(self) -> None:
        report = fixed_lattice_squared_error_audit(
            (31, 63, 127), (0.25, 1.0), (0.03, 0.3), (1, 2), (0.3,)
        )
        powers = [row["empirical_residual_power_in_h"] for row in report["rows"]]
        self.assertGreater(min(powers), 1.97)

    def test_lattice_continuum_bridge_has_inverse_square_rate(self) -> None:
        report = lattice_continuum_bridge_rate_audit(
            (4.0, 8.0, 16.0, 32.0), (0.3,), (1, 2), (0.0, 0.5)
        )
        for row in report["rows"]:
            self.assertAlmostEqual(row["empirical_power_in_c"], -2.0, delta=0.04)

    def test_balanced_squared_candidate_contains_sampled_residuals(self) -> None:
        report = balanced_squared_error_audit(
            (63, 127, 255), (0.6,), (0.1, 0.5, 2.0), (1, 2), (0.0, 0.3)
        )
        for row in report["rows"]:
            self.assertLess(row["last"]["ratio_to_centered_candidate"], 0.001)

    def test_atomic_joint_candidate_contains_sampled_residuals(self) -> None:
        report = atomic_joint_squared_error_audit(
            (31, 63, 127), (1.0,), (-0.25, 0.0), (1, 2), (0.0, 0.5)
        )
        for row in report["rows"]:
            self.assertLess(row["last"]["residual"], row["first"]["residual"])
            self.assertLess(row["last"]["ratio_to_candidate_scale"], 0.001)

    def test_exact_ramp_endpoint_correction_has_quadratic_remainder(self) -> None:
        report = continuum_endpoint_correction_audit()
        expected_gamma = {1: 3.5, 2: 6.3, 3: 3.5, 4: 6.3}
        for row in report["rows"]:
            self.assertEqual(row["gamma"], expected_gamma[row["source_mode"]])
            self.assertAlmostEqual(
                row["smallest_q_gamma_estimate"], row["gamma"], delta=0.004
            )
            self.assertAlmostEqual(
                row["uncorrected_empirical_power_in_q"], 1.0, delta=0.03
            )
            self.assertAlmostEqual(
                row["corrected_empirical_power_in_q"], 2.0, delta=0.04
            )

    def test_odd_even_multiplication_orders_and_early_constants(self) -> None:
        for mode in (1, 3):
            order, coefficient = early_phase_constant(mode)
            self.assertEqual(order, 1)
            ratio = continuum_phase_norm(1e-3, mode) / (coefficient * 1e-3)
            self.assertAlmostEqual(ratio, 1.0, delta=0.004)
        for mode in (2, 4):
            order, coefficient = early_phase_constant(mode)
            self.assertEqual(order, 2)
            ratio = continuum_phase_norm(1e-3, mode) / (coefficient * 1e-6)
            self.assertAlmostEqual(ratio, 1.0, delta=0.007)

    def test_critical_width_slowdown_is_in_the_lattice_phase(self) -> None:
        report = critical_width_preasymptotic_audit(
            (63, 127, 255), (2.0, 4.0, 8.0), 1.0
        )
        finite = report["finite_rows"]
        for mode in (1, 2):
            rows = [row for row in finite if row["source_mode"] == mode]
            leading_errors = [
                row["finite_relative_error_to_leading_law"] for row in rows
            ]
            lattice_errors = [
                row["finite_relative_error_to_lattice_phase"] for row in rows
            ]
            self.assertTrue(
                all(left > right for left, right in zip(leading_errors, leading_errors[1:]))
            )
            self.assertLess(lattice_errors[-1], 0.0004)
        even_c8 = next(
            row
            for row in report["lattice_phase_extrapolation"]
            if row["source_mode"] == 2 and row["epsilon_over_h"] == 8.0
        )
        self.assertEqual(even_c8["equivalent_critical_side_length"], 8.0**9)
        self.assertGreater(even_c8["relative_error_to_leading_law"], 0.10)

    def test_null_and_reflection_controls_are_roundoff_zero(self) -> None:
        report = null_and_symmetry_controls()["floating_residuals"]
        self.assertLess(report["constant_modulation_maximum_norm"], 3e-14)
        self.assertLess(report["symmetric_odd_maximum_norm"], 3e-14)
        self.assertGreater(report["symmetric_even_minimum_norm"], 1e-7)
        self.assertIsNone(safe_relative_error(0.0, 0.0))

    def test_placement_blind_atom_has_persistent_error(self) -> None:
        report = placement_counterexample((31, 63, 127))
        self.assertGreater(report["persistent_atom_split_gap"], 0.003)
        rows = report["rows"]
        correct_errors = [row["boundary_error_to_split"] for row in rows]
        wrong_errors = [
            row["boundary_error_to_placement_blind_atom"] for row in rows
        ]
        self.assertTrue(
            all(left > right for left, right in zip(correct_errors, correct_errors[1:]))
        )
        self.assertGreater(wrong_errors[-1], 0.003)

    def test_continuum_chart_fails_below_mesh_resolution(self) -> None:
        report = unresolved_continuum_counterexample((31, 63, 127))
        rows = report["rows"]
        lattice_errors = [row["error_to_lattice_phase"] for row in rows]
        continuum_errors = [row["error_to_naive_continuum_phase"] for row in rows]
        self.assertTrue(
            all(left > right for left, right in zip(lattice_errors, lattice_errors[1:]))
        )
        self.assertLess(lattice_errors[-1], 3e-6)
        self.assertGreater(continuum_errors[-1], 0.016)

    def test_atom_and_split_phase_are_genuinely_different(self) -> None:
        atom = lattice_phase_norm(0.01, 0.0, 1, 0.0)
        split = lattice_phase_norm(0.01, 0.0, 1, 0.5)
        self.assertGreater(atom / split, 2.4)

    def test_lattice_initial_layer_is_not_uniform_at_fixed_time(self) -> None:
        report = nonuniform_large_time_counterexample((15, 31, 63), 3.0)
        for row in report["rows"]:
            self.assertGreater(row["relative_error"], 0.999999)

    def test_fixed_irrational_centre_has_wandering_phase_subsequences(self) -> None:
        report = wandering_phase_counterexample(maximum_side_length=120)
        self.assertGreater(report["phase_range"], 0.00314)
        for row in report["finite_selected_subsequences"]:
            self.assertLess(row["absolute_error"], 3e-6)


if __name__ == "__main__":
    unittest.main()
