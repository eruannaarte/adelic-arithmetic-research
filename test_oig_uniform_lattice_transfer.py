"""Tests for the descriptive general-tau OIG transfer laboratory."""

from __future__ import annotations

import math
import unittest

import numpy as np
from scipy.integrate import quad

from oig_uniform_lattice_transfer import (
    INTERACTION_STRENGTH,
    atomic_tail_gram,
    conservative_tau_lipschitz_bound,
    continuum_cost_diagonal,
    continuum_gram,
    finite_neumann_gram,
    leading_error_matrix,
    natural_discrete_cost_diagonal,
    phase_profile,
    source_ports,
    target_coefficients,
    transfer_error,
)


class AnalyticObjectTests(unittest.TestCase):
    def test_closed_phase_profile_matches_spatial_quadrature(self) -> None:
        for mode in (1, 2):
            for s in (0.01, 0.5, 4.0, 17.0):
                direct = math.sqrt(2.0) * quad(
                    lambda x: math.exp(
                        -s * (1.0 + INTERACTION_STRENGTH * x)
                    )
                    * math.cos(mode * math.pi * x),
                    0.0,
                    1.0,
                    epsabs=1.0e-14,
                    epsrel=1.0e-14,
                )[0]
                self.assertAlmostEqual(phase_profile(mode, s), direct, places=13)

    def test_tau_one_continuum_reference(self) -> None:
        expected = np.array(
            [
                [1.4436726272958192e-3, 1.4248593559583728e-4],
                [1.4248593559583728e-4, 1.9870014487449490e-5],
            ]
        )
        np.testing.assert_allclose(continuum_gram(1.0), expected, rtol=2e-12)

    def test_general_tau_coefficient_recovers_stage_xii(self) -> None:
        expected = np.array(
            [
                [-0.01598629511482710915, -0.003908677177631584465],
                [-0.003908677177631584465, -0.000871634196112061576],
            ]
        )
        np.testing.assert_allclose(leading_error_matrix(1.0), expected, rtol=2e-13)

    def test_atomic_tail_is_positive_definite(self) -> None:
        eigenvalues = np.linalg.eigvalsh(atomic_tail_gram())
        self.assertGreater(eigenvalues[0], 0.0)


class DiscreteStructureTests(unittest.TestCase):
    def test_source_ports_are_orthonormal(self) -> None:
        ports = source_ports(17)
        np.testing.assert_allclose(ports.T @ ports, np.eye(2), atol=2e-15)
        np.testing.assert_allclose(ports.sum(axis=0), np.zeros(2), atol=2e-15)

    def test_exact_centre_annihilates_odd_target_modes(self) -> None:
        coefficients = target_coefficients(17)
        self.assertLess(np.max(np.abs(coefficients[1::2])), 2e-15)
        np.testing.assert_allclose(
            coefficients[2::2] ** 2, np.full(8, 2.0 / 17.0), atol=2e-15
        )

    def test_even_one_cell_target_is_not_exactly_centred(self) -> None:
        coefficients = target_coefficients(16)
        self.assertGreater(np.max(np.abs(coefficients[1::2])), 1e-2)

    def test_parity_shortcut_matches_full_sum(self) -> None:
        shortcut = finite_neumann_gram(21, 2.0, exploit_exact_centre=True)
        full = finite_neumann_gram(21, 2.0, exploit_exact_centre=False)
        np.testing.assert_allclose(shortcut, full, atol=2e-17, rtol=2e-13)

    def test_low_spectrum_matches_krylov(self) -> None:
        krylov = finite_neumann_gram(31, 12.0, method="krylov")
        low = finite_neumann_gram(31, 12.0, method="low_spectrum")
        np.testing.assert_allclose(low, krylov, atol=3e-16, rtol=2e-11)

    def test_tau_one_finite_reference_matches_stage_xii(self) -> None:
        expected = np.array(
            [
                [1.4081512865226744e-3, 1.3414998235311597e-4],
                [1.3414998235311597e-4, 1.8056128805807903e-5],
            ]
        )
        np.testing.assert_allclose(
            finite_neumann_gram(21, 1.0), expected, atol=8e-19, rtol=2e-13
        )

    def test_natural_discrete_h1_cost_converges_quadratically(self) -> None:
        continuum = continuum_cost_diagonal()
        errors = []
        for n in (31, 61, 121):
            discrete = natural_discrete_cost_diagonal(n)
            errors.append(float(np.max(np.abs(discrete - continuum))))
        self.assertGreater(errors[0] / errors[1], 3.5)
        self.assertGreater(errors[1] / errors[2], 3.5)


class ResolutionLawTests(unittest.TestCase):
    def test_compact_tau_transfer_is_second_order(self) -> None:
        for tau in (1.0, 4.0):
            continuum = continuum_gram(tau)
            errors = []
            for n in (31, 61):
                finite = finite_neumann_gram(n, tau)
                errors.append(
                    transfer_error(
                        finite, continuum, metric="L2", side_length=n
                    )
                )
            self.assertGreater(errors[0] / errors[1], 3.4)

    def test_scaled_compact_error_approaches_explicit_coefficient(self) -> None:
        tau = 2.0
        continuum = continuum_gram(tau)
        coefficient = leading_error_matrix(tau)
        residuals = []
        for n in (41, 81):
            finite = finite_neumann_gram(n, tau)
            residuals.append(
                float(np.linalg.norm(n * n * (finite - continuum) - coefficient, 2))
            )
        self.assertGreater(residuals[0], 2.0 * residuals[1])

    def test_fixed_n_fails_in_the_tau_tail(self) -> None:
        tail_norm = float(np.linalg.norm(atomic_tail_gram(), ord=2))
        errors = []
        finite_norms = []
        for tau in (64.0, 256.0):
            continuum = continuum_gram(tau)
            finite = finite_neumann_gram(15, tau)
            errors.append(float(np.linalg.norm(finite - continuum, ord=2)))
            finite_norms.append(float(np.linalg.norm(finite, ord=2)))
        self.assertLess(finite_norms[-1], 1e-20)
        self.assertLess(abs(errors[-1] - tail_norm), 3e-6)
        self.assertGreater(errors[-1], 20.0 * errors[0] / 25.0)

    def test_joint_resolution_n_over_sqrt_tau(self) -> None:
        rows = []
        for tau, n in ((4.0, 35), (16.0, 97), (64.0, 273)):
            continuum = continuum_gram(tau)
            finite = finite_neumann_gram(n, tau)
            error = float(np.linalg.norm(finite - continuum, ord=2))
            rows.append((tau, n, error, error * n * n / tau))
        self.assertGreater(rows[0][2], rows[1][2])
        self.assertGreater(rows[1][2], rows[2][2])
        # The scaled error settles toward a nonzero large-tau coefficient.
        self.assertLess(max(row[3] for row in rows), 1.2e-2)
        self.assertGreater(min(row[3] for row in rows), 8.5e-3)

    def test_continuum_tail_has_inverse_tau_correction(self) -> None:
        tail = atomic_tail_gram()
        scaled = []
        for tau in (64.0, 256.0):
            error = float(np.linalg.norm(continuum_gram(tau) - tail, ord=2))
            scaled.append(tau * error)
        self.assertLess(abs(scaled[1] / scaled[0] - 1.0), 0.01)

    def test_natural_h1_transfer_converges(self) -> None:
        continuum = continuum_gram(2.0)
        errors = []
        for n in (31, 61):
            finite = finite_neumann_gram(n, 2.0)
            errors.append(
                transfer_error(
                    finite,
                    continuum,
                    metric="natural_discrete_H1",
                    side_length=n,
                )
            )
        self.assertGreater(errors[0] / errors[1], 3.4)

    def test_cover_lipschitz_bound_dominates_sampled_derivative(self) -> None:
        bound_one = conservative_tau_lipschitz_bound(1.0)
        radius = 1.0e-4
        plus = finite_neumann_gram(15, 1.0 + radius) - continuum_gram(
            1.0 + radius
        )
        minus = finite_neumann_gram(15, 1.0 - radius) - continuum_gram(
            1.0 - radius
        )
        sampled_derivative = float(np.linalg.norm(plus - minus, 2)) / (2 * radius)
        self.assertGreater(bound_one, sampled_derivative)
        self.assertTrue(math.isfinite(bound_one))


if __name__ == "__main__":
    unittest.main()
