#!/usr/bin/env python3

import unittest
from fractions import Fraction

from redundant_rigidity_backbones import (
    availability_probability,
    mass,
    optimize_certificate,
    verify_minimum_mass,
    verify_n80_obstruction,
)


class RedundantRigidityBackboneTests(unittest.TestCase):
    def test_minimum_mass_lower_at_100(self) -> None:
        entries = optimize_certificate(100, "lower", Fraction(11, 7))
        self.assertIsNotNone(entries)
        self.assertEqual(mass(entries), Fraction(3, 7))
        self.assertEqual(
            verify_minimum_mass(100, "lower", Fraction(11, 7), entries),
            Fraction(3, 7),
        )

    def test_minimum_mass_upper_at_100(self) -> None:
        entries = optimize_certificate(100, "upper", Fraction(8, 5))
        self.assertIsNotNone(entries)
        self.assertEqual(
            verify_minimum_mass(100, "upper", Fraction(8, 5), entries),
            Fraction(2, 5),
        )

    def test_edge_disjoint_upper_alternative(self) -> None:
        primary = optimize_certificate(100, "upper", Fraction(8, 5))
        self.assertIsNotNone(primary)
        alternative = optimize_certificate(
            100, "upper", Fraction(8, 5), {n for n, _ in primary}
        )
        self.assertIsNotNone(alternative)
        self.assertFalse({n for n, _ in primary} & {n for n, _ in alternative})

    def test_n80_is_critical_for_sharp_lower(self) -> None:
        self.assertIsNone(optimize_certificate(100, "lower", Fraction(11, 7), {80}))
        self.assertEqual(verify_n80_obstruction(), Fraction(1))

    def test_redundancy_improves_availability(self) -> None:
        lower = [{26, 64, 80}, {24, 80}]
        upper = [{27, 63}, {57, 75, 87, 99}]
        probability = 0.8
        redundant = availability_probability(lower, upper, probability)
        self.assertGreater(redundant, probability**5)


if __name__ == "__main__":
    unittest.main()
