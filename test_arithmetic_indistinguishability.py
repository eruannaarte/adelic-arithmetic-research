#!/usr/bin/env python3

import unittest

from arithmetic_indistinguishability import (
    adversarial_ambiguity_radius,
    direct_singleton_dirichlet_distance,
    perlis_degree_eight_collision,
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


if __name__ == "__main__":
    unittest.main()
