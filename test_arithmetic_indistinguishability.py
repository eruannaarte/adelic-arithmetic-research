#!/usr/bin/env python3

import unittest

from arithmetic_indistinguishability import (
    adversarial_ambiguity_radius,
    direct_singleton_dirichlet_distance,
    perlis_degree_eight_collision,
    perlis_two_adic_moment_channel,
    perlis_two_adic_local_probe,
    singleton_dirichlet_distance,
)


class ArithmeticIndistinguishabilityTests(unittest.TestCase):
    def test_closed_singleton_distance_matches_direct_design(self) -> None:
        for window in ["uniform", "hann"]:
            closed = singleton_dirichlet_distance(
                50, 51, 2.0, 1_000.0, 5_000, window
            )
            direct = direct_singleton_dirichlet_distance(
                50, 51, 2.0, 1_000.0, 5_000, window
            )
            self.assertAlmostEqual(closed, direct, places=14)
            self.assertGreater(adversarial_ambiguity_radius(closed), 0.0)

    def test_perlis_pair_is_an_exact_aggregate_collision(self) -> None:
        collision = perlis_degree_eight_collision(3)
        self.assertTrue(collision["nonisomorphic"])
        self.assertTrue(collision["dedekind_zeta_functions_equal"])
        self.assertEqual(collision["aggregate_trace_distance"], 0.0)

    def test_perlis_hypothesis_rejects_square_parameter(self) -> None:
        with self.assertRaises(ValueError):
            perlis_degree_eight_collision(1)

    def test_enriched_two_adic_probe_breaks_zeta_collision(self) -> None:
        probe = perlis_two_adic_local_probe(33)
        self.assertTrue(probe["dedekind_zeta_functions_equal"])
        self.assertEqual(probe["shared_residue_degrees"], [1, 1, 1, 1])
        self.assertEqual(probe["first_factor_degrees"], [1, 1, 2, 4])
        self.assertEqual(probe["second_factor_degrees"], [2, 2, 2, 2])
        self.assertTrue(probe["first_factorization_identity_verified"])
        self.assertTrue(probe["second_factorization_identity_verified"])
        self.assertTrue(probe["enriched_two_adic_channel_separates_pair"])
        self.assertFalse(probe["aggregate_zeta_channel_separates_pair"])

    def test_second_local_dimension_moment_is_first_separator(self) -> None:
        channel = perlis_two_adic_moment_channel(33)
        self.assertEqual(channel["first_separating_moment_order"], 2)
        self.assertEqual(channel["first_separating_responses"], [22, 16])
        self.assertEqual(channel["response_distance"], 6)
        self.assertEqual(channel["adversarial_ambiguity_radius"], 3.0)


if __name__ == "__main__":
    unittest.main()
