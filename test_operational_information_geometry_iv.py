#!/usr/bin/env python3

import unittest

import numpy as np

from operational_information_geometry import factorization_universe
from operational_information_geometry_iii import (
    diagonal_markov_interaction_laplacian,
    independent_generator,
)
from operational_information_geometry_iv import (
    causal_jet_audit,
    directed_response_audit,
    intervention_background_audit,
    localized_intervention_maps,
    one_way_rate_modulation_generator,
    passive_interventional_audit,
    positive_multiscale_response_design,
    protocol_invariance_audit,
    response_blocks,
    run_stage_4_experiment,
    uniformization_cone_audit,
)


class OperationalInformationGeometryIVTests(unittest.TestCase):
    def setUp(self) -> None:
        self.left = factorization_universe((2,), 6)
        self.right = factorization_universe((3,), 6)
        self.times = np.geomspace(0.01, 2.0, 20)
        self.maps = localized_intervention_maps(6, 6)

    def test_interventions_preserve_mass_and_have_zero_cross_marginal(self) -> None:
        left_intervention = self.maps["left_intervention"]
        right_intervention = self.maps["right_intervention"]
        np.testing.assert_allclose(np.sum(left_intervention, axis=0), 0.0, atol=1e-14)
        np.testing.assert_allclose(np.sum(right_intervention, axis=0), 0.0, atol=1e-14)
        np.testing.assert_allclose(
            self.maps["right_marginal"] @ left_intervention, 0.0, atol=1e-14
        )
        np.testing.assert_allclose(
            self.maps["left_marginal"] @ right_intervention, 0.0, atol=1e-14
        )

    def test_rate_modulation_is_symmetric_markov_but_macro_directional(self) -> None:
        generator = one_way_rate_modulation_generator(
            self.left.laplacian, self.right.laplacian, 0.8
        )
        off_diagonal = generator - np.diag(np.diag(generator))
        np.testing.assert_allclose(generator, generator.T, atol=1e-14)
        self.assertLessEqual(float(np.max(off_diagonal)), 0.0)
        np.testing.assert_allclose(np.sum(generator, axis=0), 0.0, atol=1e-13)

        # The exact autonomy identity behind the zero B-to-A channel.
        np.testing.assert_allclose(
            self.maps["left_marginal"] @ generator,
            self.left.laplacian @ self.maps["left_marginal"],
            atol=2e-14,
        )
        forward = np.vstack(
            response_blocks(
                generator,
                self.maps["right_marginal"],
                self.maps["left_intervention"],
                self.times,
            )
        )
        reverse = np.vstack(
            response_blocks(
                generator,
                self.maps["left_marginal"],
                self.maps["right_intervention"],
                self.times,
            )
        )
        self.assertGreater(float(np.linalg.norm(forward)), 0.3)
        self.assertLess(float(np.linalg.norm(reverse)), 2e-14)

    def test_independent_and_reciprocal_falsification_controls(self) -> None:
        report = directed_response_audit(
            self.left.laplacian, self.right.laplacian, self.times
        )
        independent = report["independent"]
        reciprocal = report["reciprocal_diagonal_edge"]
        directed = report["one_way_rate_modulation"]
        self.assertEqual(independent["A_to_B"]["history_rank"], 0)
        self.assertEqual(independent["B_to_A"]["history_rank"], 0)
        self.assertGreater(reciprocal["A_to_B"]["stacked_history_frobenius_norm"], 0.17)
        self.assertGreater(reciprocal["B_to_A"]["stacked_history_frobenius_norm"], 0.17)
        self.assertAlmostEqual(reciprocal["signed_directionality_index"], 0.0, places=12)
        self.assertGreater(directed["signed_directionality_index"], 0.999999999)

    def test_causal_jet_gives_finite_zero_and_full_rank_certificates(self) -> None:
        independent = independent_generator(
            self.left.laplacian, self.right.laplacian
        )
        directed = one_way_rate_modulation_generator(
            self.left.laplacian, self.right.laplacian, 0.8
        )
        zero_jet = causal_jet_audit(
            independent,
            self.maps["right_marginal"],
            self.maps["left_intervention"],
        )
        forward_jet = causal_jet_audit(
            directed,
            self.maps["right_marginal"],
            self.maps["left_intervention"],
        )
        reverse_jet = causal_jet_audit(
            directed,
            self.maps["left_marginal"],
            self.maps["right_intervention"],
        )
        self.assertTrue(zero_jet["numerically_vanishing_through_cayley_hamilton"])
        self.assertEqual(forward_jet["first_numerically_nonzero_order"], 1)
        self.assertEqual(forward_jet["first_full_intervention_rank_order"], 3)
        self.assertEqual(forward_jet["early_cumulative_ranks"][:4], [0, 1, 3, 5])
        self.assertTrue(reverse_jet["numerically_vanishing_through_cayley_hamilton"])

    def test_uniformization_poisson_tail_bounds_every_distance_shell(self) -> None:
        generator = one_way_rate_modulation_generator(
            self.left.laplacian, self.right.laplacian, 0.8
        )
        report = uniformization_cone_audit(generator, source=14)
        self.assertAlmostEqual(report["uniformization_rate"], 5.28, places=12)
        self.assertEqual(report["distance_shell_state_counts"], [1, 4, 8, 10, 8, 4, 1])
        self.assertEqual(report["source_graph_eccentricity"], 6)
        self.assertLessEqual(report["maximum_poisson_bound_violation"], 1e-14)
        self.assertFalse(report["strict_finite_cone"])
        for row in report["reference_tail_table"]:
            self.assertLessEqual(
                row["actual_mass"], row["poisson_tail_bound"] + 1e-14
            )
        self.assertTrue(
            all(
                row["strictly_positive_state_count"] == 36
                for row in report["effective_radius_by_time"]
            )
        )

    def test_interaction_can_expose_passive_modes_without_stability(self) -> None:
        independent = independent_generator(
            self.left.laplacian, self.right.laplacian
        )
        reciprocal = independent + 0.4 * diagonal_markov_interaction_laplacian(6, 6)
        directed = one_way_rate_modulation_generator(
            self.left.laplacian, self.right.laplacian, 0.8
        )
        report = passive_interventional_audit(
            {
                "independent": independent,
                "reciprocal": reciprocal,
                "directed": directed,
            },
            self.times,
            self.maps,
        )
        self.assertEqual(report["independent"]["passive_local_history_rank"], 11)
        self.assertEqual(report["reciprocal"]["passive_local_history_rank"], 27)
        self.assertEqual(report["directed"]["passive_local_history_rank"], 36)
        self.assertGreater(
            report["directed"]["passive_active_subspace_condition_number"], 5e7
        )
        self.assertEqual(report["independent"]["probability_tangent_history_rank"], 10)
        self.assertEqual(report["reciprocal"]["probability_tangent_history_rank"], 26)
        self.assertEqual(report["directed"]["probability_tangent_history_rank"], 35)
        self.assertGreater(
            report["directed"]["probability_tangent_condition_number"], 3.6e7
        )
        self.assertEqual(report["directed"]["B_to_A_interventional_rank"], 0)

    def test_refreshed_compression_preserves_response_more_reliably(self) -> None:
        generator = one_way_rate_modulation_generator(
            self.left.laplacian, self.right.laplacian, 0.8
        )
        report = protocol_invariance_audit(
            generator,
            self.maps["right_marginal"],
            self.maps["left_intervention"],
            self.times,
            channel_counts=(1, 2, 6),
            seed_count=32,
        )
        rows = {
            (row["channels_per_time"], row["sensor_refresh"]): row
            for row in report["protocol_rows"]
        }
        self.assertEqual(report["reference_response_rank"], 5)
        self.assertLess(rows[(1, "repeated")]["full_rank_fraction"], 1.0)
        self.assertEqual(rows[(1, "independent_each_time")]["full_rank_fraction"], 1.0)
        self.assertLess(
            rows[(1, "independent_each_time")][
                "median_scale_free_response_dilation"
            ],
            rows[(1, "repeated")]["median_scale_free_response_dilation"],
        )
        self.assertLess(
            rows[(6, "independent_each_time")][
                "median_scale_free_response_dilation"
            ],
            1.5,
        )

    def test_direction_survives_pure_backgrounds_but_is_silent_at_equilibrium(self) -> None:
        generator = one_way_rate_modulation_generator(
            self.left.laplacian, self.right.laplacian, 0.8
        )
        report = intervention_background_audit(generator, 6, 6, self.times)
        self.assertTrue(report["all_pure_backgrounds_have_full_forward_rank"])
        self.assertGreater(
            min(row["response_norm"] for row in report["pure_target_backgrounds"]),
            0.34,
        )
        self.assertEqual(
            report["stationary_uniform_target_background"]["response_rank"], 0
        )
        self.assertLess(
            report["stationary_uniform_target_background"]["response_norm"],
            2e-14,
        )

    def test_positive_multiscale_design_has_primal_dual_audit(self) -> None:
        generator = one_way_rate_modulation_generator(
            self.left.laplacian, self.right.laplacian, 0.8
        )
        report = positive_multiscale_response_design(
            generator,
            self.maps["right_marginal"],
            self.maps["left_intervention"],
        )
        self.assertEqual(sum(report["dyadic_active_numerators"]), 4096)
        self.assertEqual(len(report["dyadic_active_times"]), 6)
        self.assertLess(report["relative_primal_dual_gap"], 1e-5)
        self.assertGreater(report["dual_two_by_two_minimum_eigenvalue"], 0.16)
        self.assertGreater(report["dyadic_fraction_of_floating_upper_bound"], 0.999)
        self.assertGreater(report["dyadic_improvement_over_uniform_grid"], 2.4)
        self.assertGreater(
            report["dyadic_improvement_over_best_single_time"], 1.4e6
        )

    def test_reference_report_preserves_scope_and_adjacent_target_boundary(self) -> None:
        report = run_stage_4_experiment(protocol_seeds=4)
        self.assertIn("no claim", report["scope"])
        self.assertFalse(
            report["adjacent_multiscale_certificate_decision"][
                "required_for_stage_iv"
            ]
        )
        self.assertFalse(report["uniformization_causal_cone"]["strict_finite_cone"])


if __name__ == "__main__":
    unittest.main()
