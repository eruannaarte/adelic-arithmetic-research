#!/usr/bin/env python3

import unittest

from finite_number_field_reconstruction import (
    GAUSSIAN,
    GOLDEN,
    elements_in_box,
    field_snapshot,
)


class FiniteNumberFieldReconstructionTests(unittest.TestCase):
    def test_box_uses_one_representative_modulo_sign(self) -> None:
        elements = elements_in_box(GAUSSIAN, 2)
        self.assertEqual(len(elements), 12)
        self.assertNotIn(GAUSSIAN.element(-1, 0), elements)

    def test_gaussian_small_box_synchronizes_active_places(self) -> None:
        report = field_snapshot(GAUSSIAN, 2)
        self.assertEqual(report["nullity"], 1)
        self.assertGreater(report["rational_integer_only_nullity_on_same_places"], 1)

    def test_golden_small_box_synchronizes_active_places(self) -> None:
        report = field_snapshot(GOLDEN, 2)
        self.assertEqual(report["nullity"], 1)
        self.assertGreater(report["rational_integer_only_nullity_on_same_places"], 1)

    def test_witness_count_is_rank(self) -> None:
        for field in (GAUSSIAN, GOLDEN):
            report = field_snapshot(field, 3)
            self.assertEqual(report["greedy_spanning_witness_count"], report["rank"])


if __name__ == "__main__":
    unittest.main()
