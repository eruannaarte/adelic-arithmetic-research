#!/usr/bin/env python3

import math
import unittest
from fractions import Fraction

from spectral_adelic_system import (
    bosonic_partition,
    energy_variance,
    exact_bosonic_partition,
    fermionic_partition,
    fermionic_supertrace,
    local_p_adic_zeta_partial,
    local_p_adic_zeta_tail_bound,
    mean_energy,
    occupation_energy,
    occupation_integer,
    prime_power_partial,
    prime_power_tail_bound,
    truncated_occupation_sum,
)


class SpectralAdelicSystemTests(unittest.TestCase):
    def test_unique_factorization_energy(self) -> None:
        primes = [2, 3, 5]
        occupations = [3, 2, 1]
        self.assertEqual(occupation_integer(primes, occupations), 360)
        self.assertAlmostEqual(occupation_energy(primes, occupations), math.log(360))

    def test_exact_finite_euler_product(self) -> None:
        primes = [2, 3, 5, 7]
        expected = Fraction(4, 3) * Fraction(9, 8) * Fraction(25, 24) * Fraction(49, 48)
        self.assertEqual(exact_bosonic_partition(primes, 2), expected)
        self.assertAlmostEqual(bosonic_partition(primes, 2).real, float(expected))

    def test_truncated_fock_sum_converges_from_below(self) -> None:
        primes = [2, 3]
        exact = exact_bosonic_partition(primes, 2)
        previous = Fraction(0)
        for cutoff in range(5):
            current = truncated_occupation_sum(primes, 2, cutoff)
            self.assertGreater(current, previous)
            self.assertLess(current, exact)
            previous = current

    def test_p_adic_shell_is_same_geometric_series(self) -> None:
        partial = local_p_adic_zeta_partial(3, 2, 8).real
        exact = 1.0 / (1.0 - 3 ** -2)
        self.assertLessEqual(
            abs(exact - partial), local_p_adic_zeta_tail_bound(3, 2, 8) + 1e-15
        )

    def test_prime_power_signal_is_log_derivative(self) -> None:
        primes = [2, 3, 5, 7]
        partial = prime_power_partial(primes, 2, 12)
        exact = mean_energy(primes, 2)
        self.assertLessEqual(
            exact - partial, prime_power_tail_bound(primes, 2, 12) + 1e-15
        )
        self.assertGreater(energy_variance(primes, 2), 0)

    def test_fermionic_identities(self) -> None:
        primes = [2, 3, 5, 7]
        s = 1.7 + 0.4j
        boson = bosonic_partition(primes, s)
        self.assertAlmostEqual(
            abs(fermionic_partition(primes, s) - boson / bosonic_partition(primes, 2 * s)),
            0.0,
            places=12,
        )
        self.assertAlmostEqual(
            abs(fermionic_supertrace(primes, s) - 1 / boson), 0.0, places=12
        )


if __name__ == "__main__":
    unittest.main()
