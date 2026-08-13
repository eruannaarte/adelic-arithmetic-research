#!/usr/bin/env python3

import unittest

import numpy as np

from sparse_prime_mode_recovery import (
    coherence_guarantee,
    coherence_sparsity_threshold,
    measurement_matrix,
    mutual_coherence,
    simulate,
)
from spectral_adelic_system import primes_up_to


class SparsePrimeModeRecoveryTests(unittest.TestCase):
    def test_coherence_threshold(self) -> None:
        self.assertEqual(coherence_sparsity_threshold(0.2), 3.0)
        report = coherence_guarantee(primes_up_to(97), 512, 1_000.0, 4, 20260812)
        self.assertTrue(report["uniform_noiseless_omp_guarantee"])

    def test_noiseless_support_recovery(self) -> None:
        report = simulate(primes_up_to(47), [2, 5, 11], 32, 80.0, 0.0, 7)
        self.assertTrue(report["exact_support_recovery"])
        self.assertLess(report["relative_coefficient_error"], 1e-12)

    def test_seeded_noisy_support_recovery(self) -> None:
        report = simulate(primes_up_to(97), [73, 79, 83, 89], 64, 250.0, 0.02, 20260812)
        self.assertTrue(report["exact_support_recovery"])
        self.assertLess(report["relative_coefficient_error"], 0.02)

    def test_longer_scaled_window_reduces_coherence(self) -> None:
        primes = primes_up_to(97)
        # Random sampling avoids the exact aliases that a regular time grid can
        # create even when its total observation window is long.
        base_times = np.sort(np.random.default_rng(0).uniform(0.0, 1.0, 128))
        short = mutual_coherence(measurement_matrix(primes, 5.0 * base_times))
        long = mutual_coherence(measurement_matrix(primes, 250.0 * base_times))
        self.assertLess(long, short)

    def test_rejects_unknown_active_prime(self) -> None:
        with self.assertRaises(ValueError):
            simulate(primes_up_to(19), [23], 10, 20.0, 0.0, 1)


if __name__ == "__main__":
    unittest.main()
