#!/usr/bin/env python3

import math
import unittest

import numpy as np

from oig_vii_mollifier_phase import (
    INTERACTION_STRENGTH,
    atomic_phase_constant,
    bridge_audit,
    continuum_crossover_audit,
    continuum_phase_norm,
    cosine_modes,
    exact_first_jet_norm,
    first_jet_scaling_audit,
    gaussian_cell_average,
    high_precision_constants,
    lattice_atom_small_time_constant,
    lattice_phase_audit,
    lattice_phase_norm,
    limiting_source_profile,
    modal_response_kernel,
    normalization_and_dense_audit,
    path_eigenvalues,
    phase_peak_audit,
    resolved_discrete_collapse_audit,
    response_norms,
    target_cosine_coefficients,
    vanishing_width_ratio_audit,
)


class OIGVIIMollifierPhaseTests(unittest.TestCase):
    def test_cell_averages_are_probability_and_reflection_symmetric(self) -> None:
        for n in (31, 63, 127):
            for epsilon in (0.0, 0.2 / n, 1.0 / n, n ** (-0.6)):
                q = gaussian_cell_average(n, epsilon)
                self.assertAlmostEqual(float(np.sum(q)), 1.0, places=15)
                self.assertLess(float(np.max(np.abs(q - q[::-1]))), 2e-16)
                self.assertTrue(np.all(q >= 0.0))

    def test_dense_joint_generator_and_modal_reduction_agree(self) -> None:
        report = normalization_and_dense_audit()
        self.assertLess(report["target_probability_mass_error"], 2e-16)
        self.assertLess(report["target_reflection_error"], 2e-16)
        self.assertLess(report["dct_orthonormality_error"], 2e-15)
        self.assertLess(report["source_density_gram_error"], 1e-15)
        # Dense expm/eigendecomposition paths use different BLAS kernels;
        # retain a tight roundoff guard without making the test CPU-specific.
        self.assertLess(report["maximum_dense_modal_entry_error"], 2e-14)
        self.assertLess(report["relative_dense_modal_frobenius_error"], 3e-14)
        self.assertEqual(report["time_zero_response_norm"], 0.0)

    def test_exact_first_jet_identity_matches_target_modal_formula(self) -> None:
        n = 63
        epsilon = n ** (-0.6)
        q = gaussian_cell_average(n, epsilon)
        beta = target_cosine_coefficients(q)
        rates = path_eigenvalues(n)
        source = cosine_modes(n, (1,))[:, 0]
        moment = float(((np.arange(n) + 0.5) / n) @ source)
        modal_derivative = -INTERACTION_STRENGTH * moment * rates * beta
        exact = exact_first_jet_norm(n, epsilon)
        self.assertAlmostEqual(np.linalg.norm(modal_derivative), exact, places=10)

    def test_resolved_first_jet_has_epsilon_minus_five_halves_scaling(self) -> None:
        report = first_jet_scaling_audit((127, 255, 511, 1023))
        errors = [row["relative_error_to_exact_constant"] for row in report["rows"]]
        self.assertTrue(all(left > right for left, right in zip(errors, errors[1:])))
        self.assertLess(errors[-1], 0.0013)
        ratios = [row["epsilon_over_h"] for row in report["rows"]]
        self.assertTrue(all(left < right for left, right in zip(ratios, ratios[1:])))

    def test_continuum_phase_has_both_predicted_asymptotes(self) -> None:
        report = continuum_crossover_audit((0.001, 0.01, 1.0, 10.0, 100.0))
        early = report["rows"][0]
        late = report["rows"][-1]
        self.assertAlmostEqual(
            early["ratio_to_t_epsilon_minus_5_over_2_asymptote"],
            1.0,
            delta=0.004,
        )
        self.assertAlmostEqual(
            late["ratio_to_t_minus_1_over_4_asymptote"],
            1.0,
            delta=0.006,
        )
        self.assertGreater(report["rows"][2]["phase_norm"], report["rows"][1]["phase_norm"])
        self.assertGreater(report["rows"][2]["phase_norm"], report["rows"][3]["phase_norm"])

    def test_high_precision_constant_agrees_with_double_quadrature(self) -> None:
        report = high_precision_constants(40)
        self.assertLess(
            report["double_vs_high_precision_atomic_constant_error"],
            2e-16,
        )
        self.assertAlmostEqual(
            float(report["atomic_large_time_constant"]),
            atomic_phase_constant(),
            places=15,
        )

    def test_lattice_phase_is_h_minus_one_half_limit(self) -> None:
        report = lattice_phase_audit(
            (31, 63, 127),
            (0.0, 1.0),
            (0.1, 1.0, 10.0),
        )
        for c in (0.0, 1.0):
            rows = [row for row in report["rows"] if row["epsilon_over_h"] == c]
            errors = [row["maximum_relative_error"] for row in rows]
            self.assertTrue(all(left > right for left, right in zip(errors, errors[1:])))
            self.assertLess(errors[-1], 0.0033)

    def test_atom_lattice_phase_has_linear_and_quarter_power_ends(self) -> None:
        early_tau = 0.001
        late_tau = 100.0
        early = lattice_phase_norm(early_tau, 0.0)
        late = lattice_phase_norm(late_tau, 0.0)
        self.assertAlmostEqual(
            early / (lattice_atom_small_time_constant() * early_tau),
            1.0,
            delta=0.005,
        )
        self.assertAlmostEqual(
            late / (atomic_phase_constant() * late_tau ** (-0.25)),
            1.0,
            delta=0.002,
        )

    def test_lattice_and_continuum_phases_match_in_overlap(self) -> None:
        report = bridge_audit((0.1, 1.0, 10.0), (2.0, 4.0, 8.0, 16.0))
        errors = [row["maximum_relative_error"] for row in report["rows"]]
        self.assertTrue(all(left > right for left, right in zip(errors, errors[1:])))
        self.assertLess(errors[-1], 0.0008)

    def test_peak_ridge_converges_to_resolved_phase_peak(self) -> None:
        report = phase_peak_audit((1.0, 2.0, 4.0, 8.0))
        time_errors = [
            row["relative_peak_time_error_to_continuum"]
            for row in report["rows"]
        ]
        height_errors = [
            row["relative_peak_height_error_to_continuum"]
            for row in report["rows"]
        ]
        self.assertTrue(
            all(left > right for left, right in zip(time_errors, time_errors[1:]))
        )
        self.assertTrue(
            all(left > right for left, right in zip(height_errors, height_errors[1:]))
        )
        self.assertLess(time_errors[-1], 0.0012)
        self.assertLess(height_errors[-1], 7e-5)

    def test_direct_resolved_response_collapses_to_continuum_phase(self) -> None:
        report = resolved_discrete_collapse_audit(
            (63, 127),
            (0.1, 1.0),
        )
        errors = [row["maximum_relative_error"] for row in report["rows"]]
        self.assertGreater(errors[0], errors[1])
        self.assertLess(errors[-1], 0.016)

    def test_epsilon_over_h_to_zero_converges_to_atom(self) -> None:
        report = vanishing_width_ratio_audit((63, 127, 255), (0.1, 1.0))
        errors = [row["maximum_relative_error"] for row in report["rows"]]
        masses = [row["central_cell_mass"] for row in report["rows"]]
        self.assertTrue(all(left > right for left, right in zip(errors, errors[1:])))
        self.assertTrue(all(left < right for left, right in zip(masses, masses[1:])))
        self.assertLess(errors[-1], 0.075)

    def test_even_source_removes_the_linear_early_profile(self) -> None:
        scales = np.asarray((1e-4, 3e-4, 1e-3))
        odd = np.asarray([limiting_source_profile(s, 1) for s in scales])
        even = np.asarray([limiting_source_profile(s, 2) for s in scales])
        odd_order = math.log(odd[-1] / odd[0]) / math.log(scales[-1] / scales[0])
        even_order = math.log(even[-1] / even[0]) / math.log(scales[-1] / scales[0])
        self.assertAlmostEqual(odd_order, 1.0, delta=0.002)
        self.assertAlmostEqual(even_order, 2.0, delta=0.002)

    def test_response_norm_is_all_target_modes_not_a_fixed_band(self) -> None:
        n = 63
        epsilon = 1.0 / n
        times = (0.1 / n**2, 1.0 / n**2)
        kernel = modal_response_kernel(n, times)
        q = gaussian_cell_average(n, epsilon)
        full = response_norms(kernel, q)[:, 0]
        beta = target_cosine_coefficients(q)
        truncated = np.linalg.norm(
            kernel.values[:, :8, 0] * beta[None, :8],
            axis=1,
        )
        self.assertTrue(np.all(full > truncated))


if __name__ == "__main__":
    unittest.main()
