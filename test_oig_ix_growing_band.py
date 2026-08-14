#!/usr/bin/env python3

import math
import unittest

import mpmath as mp
import numpy as np

from oig_ix_growing_band import (
    boundary_atom_masses,
    boundary_endpoint_gain_audit,
    calibrate_operator,
    chart_bandwidth_audit,
    constant_modulation,
    continuum_kernel_high_precision_audit,
    continuum_kernel_value,
    cosine_modes,
    exact_and_symmetry_controls,
    finite_sampling_rank_control,
    gaussian_cell_masses,
    gramian_growth_audit,
    lattice_symbol,
    multiplication_column_decay_audit,
    multiplication_reference_matrix,
    output_metric_factors,
    physical_eigenvalues,
    response_matrix,
    scaled_band_kernel,
    singular_summary,
    source_metric_factors,
    mixed_word_resolution_diagnostic,
)


class OIGIXGrowingBandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.controls = exact_and_symmetry_controls()
        cls.cutoff = chart_bandwidth_audit((63, 127, 255))
        cls.gramians = gramian_growth_audit(
            127, 10, (2, 4, 6, 8, 10)
        )
        cls.decay = multiplication_column_decay_audit(255, 32, 8)
        cls.boundary = boundary_endpoint_gain_audit((63, 127, 255), 4)
        cls.high_precision = continuum_kernel_high_precision_audit(
            8, 4, 48, 80
        )
        cls.sampling = finite_sampling_rank_control()
        cls.mixed = mixed_word_resolution_diagnostic()

    def test_cosine_basis_and_path_spectrum_are_calibrated(self) -> None:
        for n in (7, 31):
            basis = cosine_modes(n, range(n))
            self.assertLess(
                float(np.max(np.abs(basis.T @ basis - np.eye(n)))), 2e-14
            )
            mu = physical_eigenvalues(n)
            self.assertTrue(np.allclose(mu, n**2 * lattice_symbol(n)))
            self.assertEqual(float(mu[0]), 0.0)

    def test_preparations_are_conservative_and_boundary_ratio_is_reported(self) -> None:
        for c in (0.0, 0.2, 1.0, 8.0):
            masses = gaussian_cell_masses(63, c, 0.23)
            self.assertAlmostEqual(float(np.sum(masses)), 1.0, places=14)
            self.assertTrue(np.all(masses >= 0.0))
        masses, achieved = boundary_atom_masses(255, 1.0 / 255, 1.0)
        self.assertEqual(int(np.count_nonzero(masses)), 1)
        self.assertAlmostEqual(float(np.sum(masses)), 1.0, places=15)
        self.assertLess(abs(achieved - 1.0), 0.04)

    def test_modal_band_reduction_matches_dense_kronecker_model(self) -> None:
        checks = self.controls["floating_checks"]
        self.assertLess(checks["dense_modal_maximum_error"], 5e-15)
        self.assertLess(checks["dense_modal_relative_frobenius_error"], 3e-13)

    def test_gram_eigenvalues_are_squared_singular_values(self) -> None:
        checks = self.controls["floating_checks"]
        self.assertLess(checks["gram_singular_square_maximum_error"], 3e-18)

    def test_time_zero_constant_and_reflection_nulls(self) -> None:
        checks = self.controls["floating_checks"]
        self.assertEqual(checks["explicit_time_zero_maximum"], 0.0)
        self.assertLess(checks["constant_modulation_maximum_response"], 5e-14)
        self.assertLess(checks["symmetric_odd_maximum_response"], 5e-14)
        self.assertGreater(checks["symmetric_even_minimum_column_norm"], 1e-5)

    def test_multiplication_reference_removes_only_source_diffusion(self) -> None:
        n = 31
        modes = (1, 2, 3)
        target = gaussian_cell_masses(n, 1.0, 0.23)
        zero = scaled_band_kernel(n, (0.0,), modes)
        self.assertEqual(
            float(np.max(np.abs(multiplication_reference_matrix(zero, target, 0)))),
            0.0,
        )
        constant = scaled_band_kernel(
            n, (0.3,), modes, constant_modulation(n)
        )
        # Both the exact and multiplication-only responses are algebraic nulls
        # for a constant potential and nonconstant sources.
        self.assertLess(
            float(np.max(np.abs(response_matrix(constant, target, 0)))), 2e-14
        )
        self.assertLess(
            float(
                np.max(
                    np.abs(multiplication_reference_matrix(constant, target, 0))
                )
            ),
            2e-14,
        )

    def test_source_and_output_metric_factors_have_declared_direction(self) -> None:
        source_l2 = source_metric_factors(63, (1, 2, 3), 0.0)
        source_h1 = source_metric_factors(63, (1, 2, 3), 1.0)
        output_l2 = output_metric_factors(63, 0.0)
        output_hminus = output_metric_factors(63, 0.5)
        self.assertTrue(np.all(source_l2 == 1.0))
        self.assertTrue(np.all(np.diff(source_h1) > 0.0))
        self.assertTrue(np.all(output_l2 == 1.0))
        self.assertTrue(np.all(np.diff(output_hminus) < 0.0))

    def test_smallest_singular_value_obeys_last_column_upper_bound(self) -> None:
        n = 31
        modes = tuple(range(1, 7))
        kernel = scaled_band_kernel(n, (0.3,), modes)
        target = gaussian_cell_masses(n, 1.0, 0.23)
        operator = calibrate_operator(
            response_matrix(kernel, target, 0), n, modes, n ** (-0.5)
        )
        summary = singular_summary(operator)
        self.assertLessEqual(
            summary["raw_smallest_singular_value"],
            float(np.linalg.norm(operator[:, -1])) * (1.0 + 1e-12),
        )

    def test_fixed_band_drives_source_diffusion_error_down_in_every_chart(self) -> None:
        for chart in ("resolved", "atomic", "boundary", "lattice"):
            rows = [
                row
                for row in self.cutoff["fixed_band_K2"]
                if row["chart"] == chart
            ]
            errors = [row["last_column_relative_error"] for row in rows]
            deltas = [row["source_diffusion_number"] for row in rows]
            self.assertTrue(
                all(left > right for left, right in zip(errors, errors[1:]))
            )
            self.assertTrue(
                all(left > right for left, right in zip(deltas, deltas[1:]))
            )
            # The sampled small-delta response is approximately delta/2.
            self.assertGreater(errors[-1] / deltas[-1], 0.40)
            self.assertLess(errors[-1] / deltas[-1], 0.55)

    def test_critical_band_has_persistent_source_diffusion_error(self) -> None:
        physical = self.cutoff[
            "critical_physical_band_K_approximately_quarter_sqrt_n"
        ]
        for chart in ("resolved", "atomic", "boundary"):
            errors = [
                row["last_column_relative_error"]
                for row in physical
                if row["chart"] == chart
            ]
            self.assertLess(max(errors) - min(errors), 0.04)
            self.assertGreater(min(errors), 0.24)
        lattice = self.cutoff["critical_lattice_band_K_approximately_0.30n"]
        errors = [row["last_column_relative_error"] for row in lattice]
        self.assertLess(max(errors) - min(errors), 0.004)
        self.assertGreater(min(errors), 0.11)

    def test_weighted_protocol_gramians_lose_their_lower_frame_bound(self) -> None:
        for chart in ("lattice", "resolved", "atomic", "boundary_endpoint"):
            for metric in (
                "L2_source_to_L2_output",
                "H1_source_to_L2_output",
                "L2_source_to_HminusHalf_output",
            ):
                rows = [
                    row
                    for row in self.gramians["rows"]
                    if row["chart"] == chart and row["metric"] == metric
                ]
                minima = [row["raw_smallest_singular_value"] for row in rows]
                self.assertTrue(
                    all(left > right for left, right in zip(minima, minima[1:]))
                )
                self.assertLess(minima[-1], minima[0] * 1e-3)
                self.assertTrue(
                    all(row["smallest_over_last_column_bound"] <= 1.0 + 1e-10 for row in rows)
                )

    def test_ramp_reference_columns_have_k_minus_two_and_h1_k_minus_three_envelopes(self) -> None:
        for row in self.decay["rows"]:
            expected = -2.0 - row["source_sobolev_order"]
            self.assertAlmostEqual(
                row["empirical_column_norm_power_in_k"], expected, delta=0.03
            )

    def test_endpoint_gain_converges_to_square_root_two(self) -> None:
        rows = self.boundary["rows"]
        distances = [row["distance_of_largest_ratio_from_sqrt_two"] for row in rows]
        self.assertTrue(
            all(left > right for left, right in zip(distances, distances[1:]))
        )
        self.assertLess(distances[-1], 0.003)

    def test_exact_continuum_kernel_specializations(self) -> None:
        with mp.workdps(50):
            A = mp.mpf("2.7")
            atomic = continuum_kernel_value(A, "atomic")
            self.assertAlmostEqual(
                float(continuum_kernel_value(A, "resolved", q=0)),
                float(1 / (2 * mp.sqrt(mp.pi))),
                places=15,
            )
            self.assertAlmostEqual(
                float(continuum_kernel_value(A, "boundary_atomic", boundary_ratio=0)),
                float(2 * atomic),
                places=15,
            )
            far = continuum_kernel_value(A, "boundary_atomic", boundary_ratio=20)
            self.assertAlmostEqual(float(far / atomic), 1.0, places=14)
            lattice = continuum_kernel_value(A, "lattice_atom", lattice_time=0.7)
            self.assertGreater(float(lattice), 0.0)

    def test_high_precision_early_singular_fan_and_determinant(self) -> None:
        fan = self.high_precision["early_singular_fan"]
        for row in fan["rows"]:
            self.assertAlmostEqual(
                row["last_dyadic_power_in_q"],
                row["predicted_power_in_q"],
                delta=0.06,
            )
        self.assertAlmostEqual(
            fan["determinant_gram_last_dyadic_power"],
            fan["determinant_gram_predicted_power"],
            delta=0.25,
        )

    def test_kernel_gram_matches_independent_phase_integrals(self) -> None:
        for row in self.high_precision["kernel_identity_controls"]:
            self.assertLess(float(row["maximum_relative_error"]), 1e-50)

    def test_balanced_and_atomic_smallest_singular_values_decay_geometrically(self) -> None:
        rows = self.high_precision["balanced_atomic_exponential_decay"]
        balanced = [
            row["successive_smallest_ratio"]
            for row in rows
            if row["chart"] == "balanced_resolved_q1"
            and row["source_band"] >= 5
        ]
        atomic = [
            row["successive_smallest_ratio"]
            for row in rows
            if row["chart"] == "atomic" and row["source_band"] >= 5
        ]
        self.assertTrue(all(0.04 < value < 0.05 for value in balanced))
        self.assertTrue(all(0.055 < value < 0.065 for value in atomic))

    def test_high_precision_exposes_double_precision_false_nulls(self) -> None:
        for row in self.high_precision["double_precision_rank_loss"]:
            self.assertEqual(row["high_precision_positive_rank"], 8)
            self.assertLess(row["double_gram_numerical_rank"], 8)

    def test_critical_fan_hits_each_predicted_alpha(self) -> None:
        rows = self.high_precision["critical_resolution_fan"]["rows"]
        for index in range(1, 5):
            alpha = 4 * index / (4 * index + 1)
            row = next(
                item
                for item in rows
                if item["singular_index"] == index
                and abs(item["alpha"] - alpha) < 1e-12
            )
            self.assertAlmostEqual(row["predicted_power_in_h"], 0.0, places=14)
            self.assertAlmostEqual(row["fitted_power_in_h"], 0.0, delta=0.02)
            self.assertEqual(
                row["predicted_nonvanishing_dimension_at_this_alpha"], index
            )

    def test_noise_effective_rank_is_monotone_but_not_full(self) -> None:
        rows = [
            row
            for row in self.high_precision["effective_rank_vs_relative_noise"]
            if row["chart"] == "balanced_resolved_q1"
        ]
        ranks = [row["effective_rank"] for row in rows]
        self.assertTrue(
            all(left <= right for left, right in zip(ranks, ranks[1:]))
        )
        self.assertLess(ranks[0], 8)
        self.assertGreater(ranks[-1], ranks[0])

    def test_moment_preconditioning_records_its_source_norm_cost(self) -> None:
        control = self.high_precision["moment_preconditioning_control"]
        original = float(control["original_response_condition_number"])
        preconditioned = float(
            control["q_rescaled_moment_basis_condition_number"]
        )
        renormalized = float(
            control["condition_after_L2_normalizing_preconditioned_ports"]
        )
        norms = [float(value) for value in control["q_rescaled_source_L2_column_norms"]]
        self.assertLess(preconditioned, original / 1e5)
        self.assertGreater(max(norms), 1e12)
        self.assertGreater(renormalized, preconditioned * 1e3)
        self.assertLess(float(control["moment_inverse_identity_residual"]), 1e-60)

    def test_finite_scalar_sampling_obeys_exact_dimension_cap(self) -> None:
        for row in self.sampling["rows"]:
            self.assertLessEqual(
                row["floating_numerical_rank"], row["exact_rank_upper_bound"]
            )
            self.assertLess(row["maximum_forced_null_gram_residual"], 1e-20)

    def test_mixed_word_scale_decreases_but_resolution_is_slow(self) -> None:
        for band in (3, 4, 6, 8):
            rows = [
                row for row in self.mixed["rows"] if row["source_band"] == band
            ]
            mixed = [
                row["mixed_word_relative_scale_tK2_over_q_to_Kminus1"]
                for row in rows
            ]
            resolution = [row["epsilon_over_h"] for row in rows]
            self.assertTrue(
                all(left > right for left, right in zip(mixed, mixed[1:]))
            )
            self.assertTrue(
                all(left < right for left, right in zip(resolution, resolution[1:]))
            )
        high_band_last = next(
            row
            for row in self.mixed["rows"]
            if row["source_band"] == 8 and row["nominal_side_length"] == 1e12
        )
        self.assertLess(high_band_last["epsilon_over_h"], 2.4)


if __name__ == "__main__":
    unittest.main()
