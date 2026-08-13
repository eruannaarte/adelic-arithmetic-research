#!/usr/bin/env python3

import unittest

from interacting_prime_modes import (
    exact_infinite_free_partition,
    exact_truncated_free_partition,
    exact_truncated_joint_partition,
    numeric_joint_statistics,
)


class InteractingPrimeModeTests(unittest.TestCase):
    def test_zero_interaction_factorizes_at_every_truncation(self) -> None:
        for cutoff in [0, 1, 3, 8]:
            self.assertEqual(
                exact_truncated_joint_partition(2, 3, 2, 1, cutoff),
                exact_truncated_free_partition(2, 3, 2, cutoff),
            )

    def test_repulsive_interaction_has_exact_strict_deficit(self) -> None:
        interacting = exact_truncated_joint_partition(2, 3, 2, 2, 4)
        free = exact_truncated_free_partition(2, 3, 2, 4)
        self.assertLess(interacting, free)
        self.assertLess(free, exact_infinite_free_partition(2, 3, 2))

    def test_mixed_covariance_and_factorization_defect_detect_interaction(self) -> None:
        free = numeric_joint_statistics(2, 3, 1.5, 0.0)
        interacting = numeric_joint_statistics(2, 3, 1.5, 0.8)
        self.assertAlmostEqual(free["log_factorization_defect"], 0.0, places=13)
        self.assertAlmostEqual(free["mixed_occupation_covariance"], 0.0, places=13)
        self.assertLess(interacting["log_factorization_defect"], 0.0)
        self.assertLess(interacting["mixed_occupation_covariance"], 0.0)

    def test_one_scalar_trace_has_free_effective_energy(self) -> None:
        report = numeric_joint_statistics(2, 3, 2.0, 0.7)
        self.assertGreater(report["effective_second_energy_from_one_scalar_trace"], 0.0)
        self.assertNotAlmostEqual(
            report["effective_second_energy_from_one_scalar_trace"],
            report["true_second_energy"],
        )


if __name__ == "__main__":
    unittest.main()
