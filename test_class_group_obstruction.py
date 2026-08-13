#!/usr/bin/env python3

import unittest

from class_group_obstruction import (
    NEGATIVE_FIVE,
    analyze,
    determinantal_divisor,
    selected_prime_ideals,
    smith_invariants_full_column_rank,
)


class ClassGroupObstructionTests(unittest.TestCase):
    def test_smith_invariants(self) -> None:
        matrix = [[2, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 0]]
        self.assertEqual(smith_invariants_full_column_rank(matrix, 3), [1, 1, 2])
        self.assertEqual(determinantal_divisor(matrix, 3), 2)

    def test_prime_above_two_is_nonprincipal_but_square_is_principal(self) -> None:
        p2 = selected_prime_ideals()[0]
        self.assertEqual(p2.norm, 2)
        self.assertEqual(
            p2.ideal**2, NEGATIVE_FIVE.principal_ideal(NEGATIVE_FIVE.element(2))
        )
        self.assertFalse(
            any(a * a + 5 * b * b == 2 for a in range(-2, 3) for b in range(-2, 3))
        )

    def test_integrated_report(self) -> None:
        report = analyze()
        self.assertEqual(report["smith_invariants"], [1, 1, 2])
        self.assertEqual(report["principal_lattice_index"], 2)


if __name__ == "__main__":
    unittest.main()
