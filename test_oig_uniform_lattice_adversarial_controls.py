#!/usr/bin/env python3
"""Adversarial controls for a proposed uniform late-lattice transfer.

These tests do not certify a new positive theorem.  They encode logical and
normalization obstructions that any such theorem/certificate must survive.
"""

import math
import unittest

import numpy as np

from oig_viii_three_parameter import (
    atomic_phase_constant,
    gaussian_cell_masses,
    lattice_phase_norm,
    lattice_symbol,
    scaled_modal_kernel,
    target_coefficients,
)


class UniformLatticeAdversarialControls(unittest.TestCase):
    def test_fixed_grid_loses_every_positive_late_floor(self) -> None:
        """The fixed-n limit and the joint atomic limit do not commute."""
        n = 9
        tau = 10_000.0
        atom = gaussian_cell_masses(n, 0.0, 0.0)
        beta = target_coefficients(atom)
        kernel = scaled_modal_kernel(n, (tau,), (1, 2))
        response = kernel.values[0] * beta[:, None]

        # This is exactly the Stage-XII normalization at general tau:
        # sqrt(1+tau) h times the density-response Gram.
        finite_gram = math.sqrt(1.0 + tau) / n * (response.T @ response)
        self.assertLess(np.linalg.norm(finite_gram, ord=2), 1e-100)

        # The continuum interior-atomic form is nonzero.  Consequently no
        # fixed n can transfer its positive floor uniformly to tau=infinity.
        self.assertGreater(atomic_phase_constant(1) ** 2, 1e-4)

    def test_protocol_normalization_is_sqrt_one_plus_tau_h_N_squared(self) -> None:
        """Euclidean DCT and density formulas agree only with the h factor."""
        n = 11
        tau = 1.7
        atom = gaussian_cell_masses(n, 0.0, 0.0)
        beta_euclidean = target_coefficients(atom)
        kernel = scaled_modal_kernel(n, (tau,), (1, 2))
        amplitudes_euclidean = kernel.values[0]

        euclidean_response_gram = (
            (amplitudes_euclidean * beta_euclidean[:, None]).T
            @ (amplitudes_euclidean * beta_euclidean[:, None])
        )

        # beta_density=sqrt(n) beta_E and a_density=a_E/sqrt(n), so their
        # product, and hence N^2, equals the Euclidean response expression.
        beta_density = math.sqrt(n) * beta_euclidean
        amplitudes_density = amplitudes_euclidean / math.sqrt(n)
        density_gram = (
            (amplitudes_density * beta_density[:, None]).T
            @ (amplitudes_density * beta_density[:, None])
        )
        np.testing.assert_allclose(
            euclidean_response_gram, density_gram, rtol=0.0, atol=2e-16
        )

        protocol_from_density = math.sqrt(1.0 + tau) * density_gram / n
        protocol_from_euclidean = (
            math.sqrt(1.0 + tau) * euclidean_response_gram / n
        )
        np.testing.assert_allclose(
            protocol_from_density,
            protocol_from_euclidean,
            rtol=0.0,
            atol=2e-16,
        )

        # Omitting h changes the Gram by the unbounded factor n.
        omitted_h = math.sqrt(1.0 + tau) * density_gram
        np.testing.assert_allclose(
            omitted_h, n * protocol_from_density, rtol=2e-15, atol=1e-18
        )

    def test_odd_atom_and_even_symmetric_split_are_distinct_at_finite_tau(self) -> None:
        atom = lattice_phase_norm(1.0, 0.0, 1, 0.0) ** 2
        split = lattice_phase_norm(1.0, 0.0, 1, 0.5) ** 2
        normalized_gap = math.sqrt(2.0) * abs(atom - split)
        self.assertGreater(normalized_gap, 3e-4)

        # The preparation dependence is forgotten only asymptotically.
        atom_late = math.sqrt(101.0) * lattice_phase_norm(
            100.0, 0.0, 1, 0.0
        ) ** 2
        split_late = math.sqrt(101.0) * lattice_phase_norm(
            100.0, 0.0, 1, 0.5
        ) ** 2
        self.assertLess(abs(atom_late - split_late), normalized_gap)

    def test_natural_discrete_h1_is_not_continuum_h1(self) -> None:
        n = 17
        omega = lattice_symbol(n)
        discrete = np.diag([1.0 + n * n * omega[1], 1.0 + n * n * omega[2]])
        continuum = np.diag([1.0 + math.pi**2, 1.0 + 4.0 * math.pi**2])
        self.assertTrue(np.all(np.diag(discrete) < np.diag(continuum)))

        gram = np.array([[2.0, 0.3], [0.3, 1.0]])

        def whiten(matrix: np.ndarray, metric: np.ndarray) -> np.ndarray:
            root_inv = np.diag(1.0 / np.sqrt(np.diag(metric)))
            return root_inv @ matrix @ root_inv

        # Even with identical finite/continuum Grams, changing the metric
        # changes the generalized spectral matrix.  A Gram-only error misses
        # this term.
        metric_change = whiten(gram, discrete) - whiten(gram, continuum)
        self.assertGreater(np.linalg.norm(metric_change, ord=2), 1e-5)

        # Since S_n <= S, the old continuum floor is a safe lower floor for
        # the comparison Gram with S_n, but the transfer error must use S_n.
        old_floor = np.min(np.linalg.eigvalsh(whiten(gram, continuum)))
        discrete_floor = np.min(np.linalg.eigvalsh(whiten(gram, discrete)))
        self.assertGreaterEqual(discrete_floor, old_floor)

    def test_two_diagonal_port_bounds_do_not_control_the_gram(self) -> None:
        # An error form may vanish on both basis ports while being large on a
        # linear combination.  Stage VIII must be uniform on the whole source
        # unit sphere (or explicitly bilinearized) before it is a K=2 bound.
        error = np.array([[0.0, 1.0], [1.0, 0.0]])
        e1 = np.array([1.0, 0.0])
        e2 = np.array([0.0, 1.0])
        self.assertEqual(float(e1 @ error @ e1), 0.0)
        self.assertEqual(float(e2 @ error @ e2), 0.0)
        self.assertEqual(np.linalg.norm(error, ord=2), 1.0)
        diagonal = (e1 + e2) / math.sqrt(2.0)
        self.assertAlmostEqual(float(diagonal @ error @ diagonal), 1.0)

    def test_point_samples_do_not_certify_an_interval(self) -> None:
        samples = (1.0, 1.5, 2.0)

        def hidden_peak(tau: float) -> float:
            value = 1.0
            for point in samples:
                value *= (tau - point) ** 2
            return value

        self.assertTrue(all(hidden_peak(point) == 0.0 for point in samples))
        self.assertGreater(hidden_peak(1.25), 0.0)

        # Endpoint lower bounds do not control an interior spectral dip.
        endpoint_safe = lambda tau: (tau - 1.5) ** 2
        self.assertGreater(endpoint_safe(1.0), 0.2)
        self.assertGreater(endpoint_safe(2.0), 0.2)
        self.assertEqual(endpoint_safe(1.5), 0.0)

    def test_tau_one_taylor_tail_is_not_uniform_on_a_larger_interval(self) -> None:
        degree = 32
        tau_one = 3.6 ** (degree + 1) / math.factorial(degree + 1)
        tau_four = (4.0 * 3.6) ** (degree + 1) / math.factorial(degree + 1)
        self.assertLess(tau_one, 3e-19)
        self.assertGreater(tau_four, 1.0)

    def test_floor_transfer_requires_error_strictly_below_the_floor(self) -> None:
        continuum_floor = 0.1
        finite_gram = np.diag([0.08, 2.0])
        continuum_gram = np.diag([0.1, 2.0])
        error = np.linalg.norm(finite_gram - continuum_gram, ord=2)
        self.assertGreater(np.min(np.linalg.eigvalsh(finite_gram)), 0.0)
        self.assertLess(error, continuum_floor)
        self.assertAlmostEqual(
            np.min(np.linalg.eigvalsh(finite_gram)),
            continuum_floor - error,
        )

        # Tail convergence without a quantitative strict inequality does not
        # itself yield a proof-producing transferred floor.
        uncertified_error_bound = 0.11
        self.assertGreaterEqual(uncertified_error_bound, continuum_floor)


if __name__ == "__main__":
    unittest.main()
