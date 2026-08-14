"""Regression tests for the Stage VI adversarial continuum controls."""

import math
import unittest

from oig_vi_adversarial_controls import (
    continuum_atom_coefficient,
    continuum_first_modal_response_jet,
    exact_discrete_eigenvalue,
    first_modal_response_jet,
    modal_response_scalar,
    nearest_cell_atom_coefficient,
    shrinking_time_high_mode_gap,
    split_atom_coefficient,
)


class OIGVIAdversarialControlTests(unittest.TestCase):
    def test_smooth_modal_response_is_second_order(self):
        values = {
            n: modal_response_scalar(n, 0.05, "linear")
            for n in (64, 128, 256)
        }
        ratio = abs(values[64] - values[128]) / abs(values[128] - values[256])
        self.assertTrue(3.95 < ratio < 4.05)

    def test_midpoint_sampled_jump_is_only_first_order(self):
        values = {
            n: modal_response_scalar(n, 0.05, "step")
            for n in (64, 128, 256)
        }
        ratio = abs(values[64] - values[128]) / abs(values[128] - values[256])
        self.assertTrue(1.9 < ratio < 2.1)

        exact = continuum_first_modal_response_jet("step")
        errors = [
            abs(first_modal_response_jet(n, "step") - exact)
            for n in (256, 512)
        ]
        self.assertTrue(1.9 < errors[0] / errors[1] < 2.1)

    def test_half_holder_profile_has_intermediate_order(self):
        exact = continuum_first_modal_response_jet("holder_half")
        errors = [
            abs(first_modal_response_jet(n, "holder_half") - exact)
            for n in (2048, 4096)
        ]
        # 2^(3/2) is about 2.828; this rules out both first and second order.
        self.assertTrue(2.5 < errors[0] / errors[1] < 3.1)

    def test_reflection_symmetric_profile_has_an_exact_invisible_parity(self):
        for n in (32, 63, 128):
            response = modal_response_scalar(n, 0.05, "symmetric_quadratic")
            self.assertLess(abs(response), 2e-13)

    def test_atom_order_depends_on_placement_rule(self):
        location = 1 / 3
        exact = continuum_atom_coefficient(location, 1)
        nearest = [
            abs(nearest_cell_atom_coefficient(n, location, 1) - exact)
            for n in (128, 256)
        ]
        split = [
            abs(split_atom_coefficient(n, location, 1) - exact)
            for n in (128, 256)
        ]
        self.assertTrue(1.9 < nearest[0] / nearest[1] < 2.1)
        self.assertTrue(3.8 < split[0] / split[1] < 4.2)

    def test_relabelling_cell_centres_as_endpoints_loses_an_order(self):
        correct = [
            abs(exact_discrete_eigenvalue(n, 1) - math.pi**2)
            for n in (128, 256)
        ]
        relabelled = [
            abs(exact_discrete_eigenvalue(n, 1, 1 / (n - 1)) - math.pi**2)
            for n in (128, 256)
        ]
        self.assertTrue(3.9 < correct[0] / correct[1] < 4.1)
        self.assertTrue(1.9 < relabelled[0] / relabelled[1] < 2.1)

    def test_growing_mode_and_shrinking_time_have_a_constant_gap(self):
        self.assertAlmostEqual(shrinking_time_high_mode_gap(), 0.05053031076549891)


if __name__ == "__main__":
    unittest.main()
