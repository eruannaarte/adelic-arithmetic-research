#!/usr/bin/env python3

import math
import unittest

from oig_viii_three_parameter import (
    atomic_phase_constant,
    gaussian_cell_masses,
    response_norms,
    scaled_modal_kernel,
)


class OIGVIIIAdversarialControls(unittest.TestCase):
    def test_joint_boundary_image_factor_and_interior_constant(self) -> None:
        """First-cell and central atoms approach factors two and one."""
        boundary_ratios = []
        interior_ratios = []
        constant_squared = atomic_phase_constant(1) ** 2

        for side_length, lattice_time in ((63, 4.0), (127, 8.0), (255, 16.0)):
            kernel = scaled_modal_kernel(
                side_length, (lattice_time,), (1,)
            )
            physical_time = lattice_time / side_length**2
            prefactor = math.sqrt(physical_time) / constant_squared

            boundary = gaussian_cell_masses(
                side_length, 0.0, 0.0, anchor=0
            )
            central = gaussian_cell_masses(
                side_length, 0.0, 0.0, anchor=(side_length - 1) // 2
            )
            boundary_norm = response_norms(kernel, boundary)[0, 0]
            central_norm = response_norms(kernel, central)[0, 0]
            boundary_ratios.append(prefactor * boundary_norm**2)
            interior_ratios.append(prefactor * central_norm**2)

        self.assertTrue(
            all(
                abs(right - 2.0) < abs(left - 2.0)
                for left, right in zip(boundary_ratios, boundary_ratios[1:])
            )
        )
        self.assertTrue(
            all(
                abs(right - 1.0) < abs(left - 1.0)
                for left, right in zip(interior_ratios, interior_ratios[1:])
            )
        )
        self.assertLess(abs(boundary_ratios[-1] - 2.0), 0.021)
        self.assertLess(abs(interior_ratios[-1] - 1.0), 0.005)


if __name__ == "__main__":
    unittest.main()
