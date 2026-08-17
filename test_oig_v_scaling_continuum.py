"""Independent tests for the OIG Stage V scaling laboratory."""

import math
import unittest

import numpy as np
from scipy.linalg import expm

from oig_v_scaling_continuum import (
    causal_jet_rank_upper_bound,
    cell_centres,
    closed_form_first_jet_norm,
    diffusive_l1_radius,
    diffusive_l1_tail_bound,
    directed_cell_generator_sparse,
    exact_path_eigenvalues,
    first_causal_jet_norm,
    path_graph_laplacian,
    propagation_scaling_audit,
    reduced_response_singular_values,
    target_background,
    thermodynamic_flattening_audit,
    uniformization_rate,
)
from operational_information_geometry_ii import mixture_tangent_basis


class OIGVScalingContinuumTests(unittest.TestCase):
    def test_exact_path_spectrum_and_cell_centered_second_order_convergence(self):
        for n in (5, 8, 13):
            computed = np.linalg.eigvalsh(path_graph_laplacian(n))
            np.testing.assert_allclose(
                computed, exact_path_eigenvalues(n), atol=2e-14
            )

        error_16 = abs(exact_path_eigenvalues(16, 1 / 16)[1] / np.pi**2 - 1)
        error_32 = abs(exact_path_eigenvalues(32, 1 / 32)[1] / np.pi**2 - 1)
        self.assertTrue(3.9 < error_16 / error_32 < 4.1)

    def test_backgrounds_are_probabilities_and_uniform_is_silent(self):
        for kind in ("delta", "centered_delta", "smooth_cosine", "uniform"):
            q = target_background(12, kind)
            self.assertGreaterEqual(float(np.min(q)), 0.0)
            self.assertLess(abs(np.sum(q) - 1.0), 1e-14)
        self.assertLess(first_causal_jet_norm(12, "uniform"), 1e-11)

    def test_first_jet_closed_forms_and_asymptotics(self):
        for n in (6, 12, 32):
            self.assertTrue(
                np.isclose(
                    first_causal_jet_norm(n, "delta"),
                    closed_form_first_jet_norm(n, "delta"),
                    rtol=2e-13,
                )
            )
            self.assertTrue(
                np.isclose(
                    first_causal_jet_norm(n, "smooth_cosine"),
                    closed_form_first_jet_norm(n, "smooth_cosine"),
                    rtol=2e-13,
                )
            )

        n = 128
        delta_scaled = first_causal_jet_norm(n, "delta") / n**2.5
        smooth = first_causal_jet_norm(n, "smooth_cosine")
        self.assertLess(abs(delta_scaled - 0.8 / math.sqrt(2)), 3e-5)
        self.assertLess(
            abs(smooth - 0.8 * 0.5 * np.pi**2 / math.sqrt(24)), 7e-5
        )

    def test_modal_response_reduction_matches_dense_composite_calculation(self):
        n = 4
        times = np.array([0.03, 0.2, 0.7])
        strength = 0.8
        laplacian = path_graph_laplacian(n, 1 / n)
        modulation = np.diag(cell_centres(n))
        generator = (
            np.kron(laplacian, np.eye(n))
            + np.kron(np.eye(n), laplacian)
            + strength * np.kron(modulation, laplacian)
        )
        _, eigenvectors = np.linalg.eigh(laplacian)
        source = eigenvectors[:, 1:]
        q = target_background(n, "smooth_cosine")
        injection = np.kron(source, q[:, None])
        measurement = np.kron(np.ones((1, n)), np.eye(n))
        dense_history = np.vstack(
            [measurement @ expm(-time * generator) @ injection for time in times]
        )
        dense_singular = np.linalg.svd(dense_history, compute_uv=False)
        reduced_singular = reduced_response_singular_values(
            n, times, "smooth_cosine", strength, source_mode_count=n - 1
        )
        np.testing.assert_allclose(
            dense_singular, reduced_singular, rtol=2e-11, atol=1e-13
        )

    def test_causal_jet_modal_rank_bound_has_two_regimes(self):
        self.assertEqual(
            [causal_jet_rank_upper_bound(20, r, 1) for r in range(1, 5)],
            [1, 2, 3, 4],
        )
        self.assertEqual(
            [causal_jet_rank_upper_bound(20, r, 19) for r in range(1, 5)],
            [1, 3, 6, 10],
        )
        self.assertEqual(causal_jet_rank_upper_bound(6, 3, 5), 5)

    def test_sparse_generator_rate_and_markov_structure(self):
        for n in (8, 16):
            generator = directed_cell_generator_sparse(n).toarray()
            off_diagonal = generator - np.diag(np.diag(generator))
            self.assertLessEqual(float(np.max(off_diagonal)), 0.0)
            self.assertLess(float(np.max(np.abs(np.sum(generator, axis=0)))), 1e-10)
            self.assertTrue(
                np.isclose(np.max(np.diag(generator)), uniformization_rate(n))
            )

    def test_diffusive_radius_converges_and_bounds_computed_leakage(self):
        continuum = math.sqrt(4 * 2.8 * 0.005 * math.log(400))
        radius_32 = diffusive_l1_radius(0.005, 1 / 32)
        radius_128 = diffusive_l1_radius(0.005, 1 / 128)
        self.assertLess(
            abs(radius_128 - continuum), abs(radius_32 - continuum)
        )

        audit = propagation_scaling_audit((12, 24), time=0.005)
        self.assertLessEqual(audit["maximum_poisson_bound_violation"], 2e-12)
        self.assertLessEqual(audit["maximum_diffusive_bound_violation"], 2e-12)
        for row in audit["rows"]:
            self.assertLessEqual(
                row["actual_physical_radius"],
                row["diffusive_bennett_physical_radius"],
            )
            tail_at_bound = diffusive_l1_tail_bound(
                row["diffusive_bennett_physical_radius"],
                0.005,
                row["spacing"],
            )
            self.assertLess(abs(tail_at_bound - 0.01), 2e-11)

    def test_expanding_domain_stretched_profile_flattens_as_one_over_n(self):
        audit = thermodynamic_flattening_audit((8, 16, 32))
        expected = 0.8 * math.sqrt(3)
        for row in audit["rows"]:
            self.assertLess(
                abs(row["n_times_localized_first_jet_norm"] - expected), 2e-13
            )


if __name__ == "__main__":
    unittest.main()
