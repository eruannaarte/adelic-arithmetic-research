#!/usr/bin/env python3

import unittest

import numpy as np

from inverse_regulator_recovery import TRUE_REGULATOR
from unknown_unit_lattice import exact_observed_spacing, recover_lattice_spacing


class UnknownUnitLatticeTests(unittest.TestCase):
    def test_exact_primitive_sample_recovers_fundamental_spacing(self) -> None:
        powers = np.asarray([6, 10, 15])
        report = recover_lattice_spacing(powers * TRUE_REGULATOR, 15, 0.0)
        self.assertAlmostEqual(report["recovered_spacing"], TRUE_REGULATOR, places=10)

    def test_imprimitive_sample_recovers_only_sublattice(self) -> None:
        powers = [6, 10, 14]
        self.assertAlmostEqual(exact_observed_spacing(powers, TRUE_REGULATOR), 2 * TRUE_REGULATOR)
        report = recover_lattice_spacing(np.asarray(powers) * TRUE_REGULATOR, 14, 0.0)
        self.assertAlmostEqual(report["recovered_spacing"], 2 * TRUE_REGULATOR, places=10)

    def test_seeded_noisy_primitive_recovery(self) -> None:
        rng = np.random.default_rng(9)
        observations = np.asarray([6, 10, 15]) * TRUE_REGULATOR + rng.normal(0, 0.002, 3)
        report = recover_lattice_spacing(observations, 15, 0.002)
        self.assertLess(abs(report["recovered_spacing"] - TRUE_REGULATOR), 0.01)


if __name__ == "__main__":
    unittest.main()
