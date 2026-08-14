#!/usr/bin/env python3

import json
import unittest
from fractions import Fraction
from pathlib import Path

from adaptive_multiscale_exchange import (
    OUTER_SCALE,
    ExactPairCertificate,
    RationalPairProblem,
    ResponseInterval,
    build_support_frontier,
    solve_exact_pair_problem,
    verify_exact_pair_certificate,
)
from arithmetic_multiscale_sensing import NestedScale
from verify_adaptive_multiscale_certificate import verify_artifact


class AdaptiveMultiscaleExchangeTests(unittest.TestCase):
    def test_exact_pair_primal_and_dual_agree(self) -> None:
        exact_one = ResponseInterval(Fraction(1), Fraction(1))
        exact_minus_one = ResponseInterval(Fraction(-1), Fraction(-1))
        problem = RationalPairProblem(
            NestedScale(2, 10),
            NestedScale(4, 20),
            1,
            (2, 3),
            (Fraction(1), Fraction(1, 2)),
            (exact_one, exact_one),
            (exact_minus_one, exact_one),
        )
        certificate = solve_exact_pair_problem(problem)
        self.assertEqual(certificate.short_weight, Fraction(1, 2))
        self.assertEqual(certificate.midpoint_objective, Fraction(1, 2))
        self.assertEqual(certificate.midpoint_dual_lower, Fraction(1, 2))
        self.assertEqual(certificate.robust_dual_lower, Fraction(1, 2))
        self.assertEqual(certificate.robust_primal_upper, Fraction(1, 2))

    def test_tampered_dual_certificate_is_rejected(self) -> None:
        exact_one = ResponseInterval(Fraction(1), Fraction(1))
        exact_minus_one = ResponseInterval(Fraction(-1), Fraction(-1))
        problem = RationalPairProblem(
            NestedScale(2, 10),
            NestedScale(4, 20),
            1,
            (2,),
            (Fraction(1),),
            (exact_one,),
            (exact_minus_one,),
        )
        certificate = solve_exact_pair_problem(problem)
        tampered = ExactPairCertificate(
            certificate.short_weight,
            certificate.midpoint_objective,
            (Fraction(2),),
            certificate.midpoint_dual_lower,
            certificate.robust_dual_lower,
            certificate.robust_primal_upper,
        )
        with self.assertRaises(ValueError):
            verify_exact_pair_certificate(problem, tampered)

    def test_arb_frontier_separates_510_from_nearby_competitors(self) -> None:
        modes = (51, 52, 54, 55, 56, 72, 80, 90, 96, 128, 144, 160, 216, 240)
        short_scales = tuple(
            NestedScale(time, 5 * time) for time in (490, 500, 510, 520)
        )
        frontier = build_support_frontier(
            modes,
            short_scales=short_scales,
            outer_scale=OUTER_SCALE,
            precision=128,
        )
        self.assertEqual(frontier.winner_problem.short_scale.observation_time, 510)
        self.assertEqual(frontier.runner_up_time, 500)
        self.assertGreater(float(frontier.support_separation), 5.1e-7)
        self.assertLess(float(frontier.support_separation), 5.2e-7)
        self.assertGreater(
            frontier.runner_up_robust_lower,
            frontier.winner.robust_primal_upper,
        )
        self.assertGreater(float(frontier.published_support_separation), 5e-7)

    def test_published_adaptive_artifact_is_exactly_valid(self) -> None:
        path = (
            Path(__file__).resolve().parent
            / "certificates"
            / "arithmetic_sensing_v_adaptive_multiscale.json"
        )
        with path.open(encoding="utf-8") as handle:
            artifact = json.load(handle)
        certificate = artifact["certificate"]
        self.assertTrue(verify_artifact(artifact, certificate)["verified"])
        self.assertEqual(
            artifact["formal_certificate_sha256"],
            "01d385eb6d02bc9302b4f161183e0ee097768109f949e750fc6ec67a38b1726f",
        )
        consequence = certificate["consequence"]
        self.assertTrue(consequence["unique_support_certificate"])
        self.assertEqual(consequence["winner_short_time"], 510)
        self.assertEqual(consequence["runner_up_short_time"], 500)
        self.assertGreater(
            float(Fraction(consequence["published_support_separation"])),
            5e-7,
        )
        self.assertEqual(
            {step["short_time"] for step in certificate["exchange"]},
            {510},
        )


if __name__ == "__main__":
    unittest.main()
