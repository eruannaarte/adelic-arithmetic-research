#!/usr/bin/env python3

import unittest
from fractions import Fraction

from robust_rigidity_certificates import certificate_mass, robust_endpoint


class RobustRigidityCertificateTests(unittest.TestCase):
    def test_uniform_defect_at_100(self) -> None:
        lower_entries = [(n, Fraction(1, 7)) for n in [62, 68, 80, 84, 92]]
        upper_entries = [(n, Fraction(1, 5)) for n in [27, 63]]
        defects = {n: Fraction(1, 100) for n, _ in lower_entries + upper_entries}
        self.assertEqual(certificate_mass(lower_entries), Fraction(5, 7))
        self.assertEqual(certificate_mass(upper_entries), Fraction(2, 5))
        self.assertEqual(
            robust_endpoint("lower", Fraction(11, 7), lower_entries, defects),
            Fraction(11, 7) - Fraction(1, 100) * Fraction(5, 7),
        )
        self.assertEqual(
            robust_endpoint("upper", Fraction(8, 5), upper_entries, defects),
            Fraction(8, 5) + Fraction(1, 100) * Fraction(2, 5),
        )

    def test_heterogeneous_defects_are_weighted(self) -> None:
        entries = [(2, Fraction(1, 3)), (5, Fraction(2, 3))]
        defects = {2: Fraction(1, 10), 5: Fraction(1, 100)}
        self.assertEqual(
            robust_endpoint("lower", Fraction(3, 2), entries, defects),
            Fraction(3, 2) - Fraction(1, 30) - Fraction(1, 150),
        )

    def test_negative_defect_rejected(self) -> None:
        with self.assertRaises(ValueError):
            robust_endpoint("lower", Fraction(1), [(1, Fraction(1))], {1: Fraction(-1, 10)})


if __name__ == "__main__":
    unittest.main()
