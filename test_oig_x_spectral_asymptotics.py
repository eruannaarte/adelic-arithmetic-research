"""Focused controls for the non-certified OIG X asymptotic laboratory."""

import unittest

import mpmath as mp

from oig_x_spectral_asymptotics import (
    cosine_moment,
    lattice_gram,
    nested_ratio,
    run_audit,
    source_pivot_ratio,
    truncated_laplace_gram,
)


class OIGXSpectralAsymptoticTests(unittest.TestCase):
    def test_moment_recurrence_matches_quadrature(self):
        with mp.workdps(60):
            for degree, mode in ((1, 1), (2, 2), (5, 3), (8, 4)):
                direct = mp.quad(
                    lambda x: x**degree * mp.cos(mode * mp.pi * x),
                    [0, 1],
                )
                error = abs(cosine_moment(degree, mode) - direct)
                self.assertLess(error, mp.mpf("1e-50"))

    def test_source_pivot_ratio_reproduces_reference(self):
        with mp.workdps(90):
            value = source_pivot_ratio(10)
            self.assertLess(abs(value - mp.mpf("0.217383837671205")), mp.mpf("2e-15"))

    def test_truncated_laplace_ratio_reproduces_reference(self):
        with mp.workdps(80):
            gram = truncated_laplace_gram(8, 1, quadrature_order=72)
            value = nested_ratio(gram, 8)
            self.assertLess(abs(value - mp.mpf("0.0436584")), mp.mpf("8e-7"))

    def test_lattice_ratio_scales_with_strength(self):
        with mp.workdps(70):
            low = nested_ratio(lattice_gram(7, 1, mp.mpf("0.4"), 64), 7)
            high = nested_ratio(lattice_gram(7, 1, mp.mpf("0.8"), 64), 7)
            self.assertGreater(high / low, mp.mpf("1.85"))
            self.assertLess(high / low, mp.mpf("2.15"))

    def test_report_keeps_conjecture_boundary(self):
        report = run_audit(maximum_band=4, digits=55, quadrature_order=32)
        self.assertIn("not a proof", report["status"])
        self.assertEqual(
            report["theorem_boundary"]["ratio_constants"],
            "numerical conjecture",
        )


if __name__ == "__main__":
    unittest.main()
