"""Tests for the proof-producing compact-tau Arb cover."""

from __future__ import annotations

import unittest
from fractions import Fraction

from flint import arb, ctx, fmpq

from oig_uniform_lattice_arb_cover import (
    DEFAULT_CENTRE,
    DEFAULT_RADIUS,
    DEFAULT_SIDE_LENGTH,
    DEFAULT_TAU_ORDER,
    _phase_series,
    _series_exp,
    gram_derivative_entry_bound,
    run_cover,
    verify_cover_report,
)


class ArbSeriesUnitTests(unittest.TestCase):
    def test_exponential_series(self) -> None:
        series = _series_exp([arb(0), arb(1), arb(0), arb(0)])
        self.assertTrue(bool(series[0] == 1))
        self.assertTrue(bool(series[1] == 1))
        self.assertTrue(series[2].contains(arb(fmpq(1, 2))))
        self.assertTrue(series[3].contains(arb(fmpq(1, 6))))

    def test_phase_series_constant_matches_tau_one_reference(self) -> None:
        previous = ctx.prec
        ctx.prec = 192
        try:
            omega = arb(1)
            first = _phase_series(1, Fraction(1), omega, 3)
            second = _phase_series(2, Fraction(1), omega, 3)
            self.assertAlmostEqual(float(first[0]), 0.05739725270822891, places=16)
            self.assertAlmostEqual(float(second[0]), 0.005712930520442258, places=17)
        finally:
            ctx.prec = previous

    def test_derivative_majorant_increases_with_generator_norm(self) -> None:
        previous = ctx.prec
        ctx.prec = 192
        try:
            finite = gram_derivative_entry_bound(
                6, Fraction(1), Fraction(6, 5), Fraction(56, 5)
            )
            continuum = gram_derivative_entry_bound(
                6, Fraction(1), Fraction(6, 5), Fraction(36, 5)
            )
            self.assertTrue(bool(finite > continuum > 0))
        finally:
            ctx.prec = previous

    def test_invalid_even_grid_is_rejected_before_computation(self) -> None:
        with self.assertRaises(ValueError):
            run_cover(side_length=1000)


class FullCompactCoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # One proof run is shared by all assertions.  The 192-bit repetition
        # is independent of the canonical 256-bit command recorded in the
        # report and makes precision stability part of the test suite.
        cls.certificate = run_cover(precision_bits=192)

    def test_default_cover_is_exactly_one_to_six_fifths(self) -> None:
        self.assertEqual(DEFAULT_SIDE_LENGTH, 1001)
        self.assertEqual(DEFAULT_CENTRE - DEFAULT_RADIUS, Fraction(1))
        self.assertEqual(DEFAULT_CENTRE + DEFAULT_RADIUS, Fraction(6, 5))
        self.assertEqual(DEFAULT_TAU_ORDER, 18)
        self.assertEqual(
            self.certificate["model"]["tau_interval_exact"], ["1/1", "6/5"]
        )

    def test_all_three_metric_transfers_are_certified(self) -> None:
        self.assertTrue(self.certificate["overall_passed"])
        self.assertTrue(verify_cover_report(self.certificate)["passed"])
        records = {
            row["metric"]: row
            for row in self.certificate["metric_certificates"]
        }
        self.assertEqual(
            set(records), {"L2", "declared_H1", "natural_discrete_H1"}
        )
        self.assertTrue(all(row["passed"] for row in records.values()))

    def test_directed_error_bounds_retain_margin(self) -> None:
        records = {
            row["metric"]: row
            for row in self.certificate["metric_certificates"]
        }
        self.assertLess(records["L2"]["spectral_error_upper_approx"], 2.0e-8)
        self.assertLess(
            records["declared_H1"]["spectral_error_upper_approx"], 1.8e-9
        )
        self.assertLess(
            records["natural_discrete_H1"]["spectral_error_upper_approx"],
            1.7e-9,
        )
        self.assertTrue(
            all(row["transferred_floor_approx"] > 0 for row in records.values())
        )
        for row in records.values():
            floor = Fraction(row["stage_x_floor_exact"])
            error = Fraction(row["spectral_error_upper_exact"])
            margin = Fraction(row["transferred_floor_exact"])
            self.assertGreater(floor, error)
            self.assertEqual(margin, floor - error)

    def test_certificate_uses_full_noncommuting_model_and_no_binary64_decision(
        self,
    ) -> None:
        method = self.certificate["proof_method"]
        self.assertTrue(method["binary64_decides_no_inequality"])
        self.assertIn(
            "L_n + omega_(n,l) V_n",
            self.certificate["model"]["finite_generator"],
        )
        self.assertEqual(
            self.certificate["finite_trace"]["target_modes_retained"], 500
        )


if __name__ == "__main__":
    unittest.main()
