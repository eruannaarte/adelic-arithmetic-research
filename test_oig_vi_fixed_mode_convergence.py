#!/usr/bin/env python3

import math
import unittest

import numpy as np

from oig_vi_fixed_mode_convergence import (
    SOURCE_MODES,
    continuum_galerkin_tail_audit,
    continuum_multiplication_entry,
    dense_modal_agreement_audit,
    discrete_first_jet,
    discrete_multiplication_entry,
    empirical_full_response_convergence,
    first_jet_convergence_audit,
    fixed_block_semigroup_theorem_audit,
    high_precision_response_audit,
    interval_fixed_block_expansion_audit,
    normalization_audit,
)


class OIGVIFixedModeConvergenceTests(unittest.TestCase):
    def test_normalization_removes_all_trivial_n_scaling(self) -> None:
        report = normalization_audit(32)
        self.assertLess(report["maximum_dct_orthonormality_error"], 3e-15)
        self.assertLess(report["maximum_source_density_l2_gram_error"], 3e-15)
        self.assertLess(report["source_probability_column_sums_maximum"], 2e-15)
        self.assertLess(report["target_probability_mass_error"], 2e-15)
        self.assertGreater(report["target_probability_minimum"], 0.0)
        self.assertAlmostEqual(
            report["density_normalized_target_coefficient"], 0.4, places=14
        )
        self.assertLess(report["response_at_time_zero_norm"], 2e-15)

    def test_closed_midpoint_formula_matches_direct_sums(self) -> None:
        n = 17
        x = (np.arange(n) + 0.5) / n
        for left in range(7):
            left_values = (
                np.ones(n)
                if left == 0
                else math.sqrt(2.0) * np.cos(math.pi * left * x)
            )
            for right in range(7):
                right_values = (
                    np.ones(n)
                    if right == 0
                    else math.sqrt(2.0) * np.cos(math.pi * right * x)
                )
                direct = float(np.mean(x * left_values * right_values))
                closed = discrete_multiplication_entry(n, left, right)
                self.assertAlmostEqual(direct, closed, places=14)

    def test_multiplication_parity_exposes_second_order_midpoint_error(self) -> None:
        for left in range(6):
            for right in range(6):
                continuum = continuum_multiplication_entry(left, right)
                coarse = discrete_multiplication_entry(32, left, right)
                fine = discrete_multiplication_entry(64, left, right)
                if (left + right) % 2 == 0:
                    self.assertAlmostEqual(coarse, continuum, places=14)
                    self.assertAlmostEqual(fine, continuum, places=14)
                else:
                    coarse_scaled = 32**2 * (coarse - continuum)
                    fine_scaled = 64**2 * (fine - continuum)
                    expected = (
                        (1.0 if left == 0 else math.sqrt(2.0))
                        * (1.0 if right == 0 else math.sqrt(2.0))
                        / 12.0
                    )
                    self.assertLess(abs(fine_scaled - expected), abs(coarse_scaled - expected))

    def test_dense_joint_and_modal_reduction_agree(self) -> None:
        report = dense_modal_agreement_audit((6, 7), (0.001, 0.02, 0.2))
        self.assertLess(report["maximum_absolute_entry_error"], 8e-16)
        self.assertTrue(
            all(row["relative_frobenius_error"] < 8e-14 for row in report["rows"])
        )

    def test_full_response_has_reference_and_reference_free_order_two(self) -> None:
        report = empirical_full_response_convergence(
            (8, 16, 32, 64, 128), continuum_cutoff=128
        )
        self.assertAlmostEqual(report["log_log_fitted_history_order"], 2.0, delta=0.004)
        self.assertAlmostEqual(report["log_log_fitted_gram_order"], 2.0, delta=0.006)
        for row in report["reference_free_cauchy_rows"]:
            self.assertAlmostEqual(row["reference_free_cauchy_order"], 2.0, delta=0.006)
        scaled = [row["n_squared_times_history_error"] for row in report["rows"]]
        self.assertLess(max(scaled) - min(scaled), 0.003)

    def test_high_precision_recomputation_confirms_rate_and_roundoff(self) -> None:
        report = high_precision_response_audit(
            (8, 16, 32), continuum_cutoff=40, decimal_digits=50
        )
        self.assertLess(
            max(
                row["maximum_double_vs_high_precision_entry_error_float"]
                for row in report["rows"]
            ),
            2e-15,
        )
        for row in report["doubling_orders"]:
            self.assertAlmostEqual(row["observed_order"], 2.0, delta=0.004)

    def test_first_jet_has_exact_even_parity_and_proved_error_bound(self) -> None:
        report = first_jet_convergence_audit((8, 16, 32, 64, 128))
        for row in report["rows"]:
            self.assertEqual(row["maximum_even_absolute_value"], 0.0)
            self.assertLessEqual(row["bound_violation"], 0.0)
        self.assertEqual(discrete_first_jet(32, 2), 0.0)
        errors = [row["maximum_odd_relative_error"] for row in report["rows"]]
        self.assertTrue(all(left > right for left, right in zip(errors, errors[1:])))

    def test_outward_fixed_block_expansion_certificate_passes(self) -> None:
        report = interval_fixed_block_expansion_audit((8, 16, 32, 64))
        self.assertTrue(report["all_bounds_verified"])
        self.assertTrue(all(row["first_bound_verified"] for row in report["rows"]))
        self.assertTrue(
            all(row["remainder_bound_verified"] for row in report["rows"])
        )

    def test_proved_tail_and_fixed_block_bounds_cover_computations(self) -> None:
        tail = continuum_galerkin_tail_audit((16, 32, 64), reference_cutoff=128)
        self.assertTrue(
            all(row["empirical_difference_below_tail_bound"] for row in tail["rows"])
        )
        self.assertTrue(
            all(
                left["rigorous_history_tail_bound"]
                > right["rigorous_history_tail_bound"]
                for left, right in zip(tail["rows"], tail["rows"][1:])
            )
        )
        fixed = fixed_block_semigroup_theorem_audit((8, 16, 32, 64))
        self.assertTrue(fixed["all_bounds_verified"])
        remainders = [
            row["n_squared_response_remainder"] for row in fixed["rows"]
        ]
        self.assertTrue(
            all(left > right for left, right in zip(remainders, remainders[1:]))
        )
        scaled_remainders = [
            row["n_fourth_scaled_response_remainder"] for row in fixed["rows"]
        ]
        self.assertLess(max(scaled_remainders) - min(scaled_remainders), 0.03)


if __name__ == "__main__":
    unittest.main()
