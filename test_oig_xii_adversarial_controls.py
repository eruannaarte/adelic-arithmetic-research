import math
import unittest
from fractions import Fraction

import numpy as np
from flint import arb, arb_mat, ctx
from scipy.linalg import expm

import oig_xi_transfer_certificate as xi
import oig_xii_two_port_certificate as xii
from oig_viii_three_parameter import (
    cell_centres,
    cosine_modes,
    direct_dense_modal_response,
    gaussian_cell_masses,
    lattice_symbol,
    preparation_centre,
    ramp_modulation,
    raw_neumann_path,
    scaled_modal_kernel,
    target_coefficients,
)


class TwoPortAdversarialControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_precision = ctx.prec
        # The lowest allowed proof settings are deliberately used here.  The
        # companion certificate tests repeat the result at higher precision.
        cls.certificate = xii.run_certificate(
            precision_bits=160,
            taylor_degree=24,
        )

    @classmethod
    def tearDownClass(cls):
        ctx.prec = cls.previous_precision

    def test_dct_sources_are_orthonormal(self):
        for n in (5, 9, 16):
            source = cosine_modes(n, (1, 2))
            np.testing.assert_allclose(
                source.T @ source,
                np.eye(2),
                rtol=0.0,
                atol=2e-15,
            )

    def test_odd_central_atom_has_exact_parity_pattern(self):
        for n in (5, 9, 15):
            self.assertEqual(preparation_centre(n), 0.5)
            atom = gaussian_cell_masses(n, 0.0, 0.0)
            beta = target_coefficients(atom)
            self.assertAlmostEqual(beta[0], 1 / math.sqrt(n), places=15)
            for mode in range(1, n):
                expected = math.sqrt(2 / n) * math.cos(mode * math.pi / 2)
                self.assertAlmostEqual(beta[mode], expected, places=14)
                if mode % 2:
                    self.assertAlmostEqual(beta[mode], 0.0, places=14)
                else:
                    self.assertAlmostEqual(beta[mode] ** 2, 2 / n, places=14)

    def test_even_default_carrier_is_a_different_target(self):
        n = 8
        centre = preparation_centre(n)
        self.assertEqual(centre, 0.5 - 1 / (2 * n))
        atom = gaussian_cell_masses(n, 0.0, 0.0)
        beta = target_coefficients(atom)
        self.assertGreater(abs(beta[1]), 1e-3)
        with self.assertRaises(ValueError):
            xii.finite_neumann_two_port_gram(n, 32)

    def test_reduced_response_matches_dense_kronecker_model(self):
        for n in (5, 6):
            atom = gaussian_cell_masses(n, 0.0, 0.0)
            beta = target_coefficients(atom)
            reduced = scaled_modal_kernel(n, (1.0,), (1, 2))
            for column, source_mode in enumerate((1, 2)):
                dense = direct_dense_modal_response(
                    n,
                    1.0,
                    source_mode,
                    atom,
                )
                modal = reduced.values[0, :, column] * beta
                np.testing.assert_allclose(dense, modal, rtol=0.0, atol=2e-14)

    def test_full_gram_normalization_matches_independent_formulas(self):
        previous = ctx.prec
        try:
            ctx.prec = 192
            n = 5
            atom = gaussian_cell_masses(n, 0.0, 0.0)
            beta = target_coefficients(atom)
            kernel = scaled_modal_kernel(n, (1.0,), (1, 2))
            response = kernel.values[0] * beta[:, None]
            floating_gram = math.sqrt(2) * (response.T @ response) / n

            taylor_gram, _ = xii.finite_neumann_two_port_gram(n, 32)
            dense_arb = xi._finite_neumann_gram_arb(n, 2)
            for row in range(2):
                for column in range(2):
                    self.assertTrue(
                        taylor_gram[row][column].overlaps(
                            dense_arb[row, column]
                        )
                    )
                    self.assertAlmostEqual(
                        float(taylor_gram[row][column].mid()),
                        floating_gram[row, column],
                        places=14,
                    )
        finally:
            ctx.prec = previous

    def test_centered_shift_and_taylor_tail_dominate_direct_errors(self):
        n = 9
        laplacian = raw_neumann_path(n)
        potential = np.diag(ramp_modulation(n))
        identity = np.eye(n)
        degree = 12
        uniform_tail = float(xii.centered_taylor_operator_tail(degree))

        for target_mode in (1, 4, 8):
            omega = lattice_symbol(n)[target_mode]
            generator = laplacian + omega * potential
            centre = 2.0 + 1.4 * omega
            shifted = generator - centre * identity
            radius = 2.0 + 0.4 * omega
            self.assertLessEqual(
                np.max(np.abs(np.linalg.eigvalsh(shifted))),
                radius + 2e-14,
            )
            self.assertLessEqual(radius, 18 / 5)

            term = identity.copy()
            polynomial = identity.copy()
            for order in range(1, degree + 1):
                term = (-shifted @ term) / order
                polynomial += term
            approximation = math.exp(-centre) * polynomial
            direct_error = np.linalg.norm(
                expm(-generator) - approximation,
                ord=2,
            )
            self.assertLessEqual(direct_error, uniform_tail)

    def test_closed_form_two_by_two_bound_contains_direct_norm(self):
        finite = [
            [xii._q(Fraction(-13, 10)), xii._q(Fraction(-3, 10))],
            [xii._q(Fraction(-3, 10)), xii._q(Fraction(-1, 10))],
        ]
        continuum = arb_mat([[0, 0], [0, 0]])
        bound, error, _ = xii.symmetric_two_by_two_spectral_bound(
            finite,
            continuum,
            "L2",
        )
        direct = np.linalg.norm(
            np.array([[-1.3, -0.3], [-0.3, -0.1]]),
            ord=2,
        )
        self.assertGreaterEqual(float(bound), direct)
        self.assertLess(float(bound) - direct, 2e-15)
        row_sum = float(xii.absolute_row_sum_upper(error))
        self.assertGreaterEqual(row_sum, float(bound))

    def test_entrywise_maximum_can_give_a_false_certificate(self):
        error = np.array([[0.9, 0.9], [0.9, 0.9]])
        floor = 1.0
        self.assertLess(np.max(np.abs(error)), floor)
        self.assertGreater(np.linalg.norm(error, ord=2), floor)

        # The same failure occurs in the actual L2 predecessor enclosure.
        l2 = self.certificate["metric_certificates"][0]
        actual_floor = Fraction(l2["stage_x_late_core_floor_exact"])
        predecessor = l2["records"][0]
        self.assertLess(
            Fraction(predecessor["absolute_entry_max_upper_exact"]),
            actual_floor,
        )
        self.assertGreater(
            Fraction(predecessor["rayleigh_abs_lower_exact"]),
            actual_floor,
        )

    def test_both_adjacent_metric_brackets_and_row_sum_obstruction(self):
        self.assertTrue(self.certificate["overall_passed"])
        expected = {"L2": (343, 345), "H1": (647, 649)}
        for metric_result in self.certificate["metric_certificates"]:
            failed, successful = metric_result["records"]
            self.assertEqual(
                (failed["side_length"], successful["side_length"]),
                expected[metric_result["metric"]],
            )
            self.assertTrue(failed["rayleigh_strictly_above_stage_x_floor"])
            self.assertTrue(successful["strictly_below_stage_x_floor"])
            self.assertTrue(successful["row_sum_bound_is_too_coarse"])

    def test_declared_h1_whitening_is_not_raw_euclidean_error(self):
        finite = [
            [xii._q(Fraction(-13, 10)), xii._q(Fraction(-3, 10))],
            [xii._q(Fraction(-3, 10)), xii._q(Fraction(-1, 10))],
        ]
        continuum = arb_mat([[0, 0], [0, 0]])
        l2, _, _ = xii.symmetric_two_by_two_spectral_bound(
            finite,
            continuum,
            "L2",
        )
        h1, _, _ = xii.symmetric_two_by_two_spectral_bound(
            finite,
            continuum,
            "H1",
        )
        self.assertLess(float(h1), float(l2))

    def test_adjacent_failure_success_does_not_prove_global_first(self):
        # At indices 1 and 2 this artificial error sequence has an adjacent
        # failure/success bracket, yet index 0 already passed.  The logical
        # form of the shortcut is therefore invalid without monotonicity.
        floor = 1.0
        errors = (0.5, 1.1, 0.9)
        self.assertGreater(errors[1], floor)
        self.assertLess(errors[2], floor)
        self.assertLess(errors[0], floor)


if __name__ == "__main__":
    unittest.main()
