#!/usr/bin/env python3

import json
import unittest
from fractions import Fraction
from pathlib import Path

import numpy as np

from arithmetic_multiscale_sensing import (
    DangerousMode,
    NestedScale,
    RationalMultiscaleDesign,
    centered_grid_inclusion_offset,
    dyadic_rationalize,
    materialize_outer_grid_weights,
    proportional_scales,
    reference_design,
    response_matrix,
    search_sparse_supports,
    solve_positive_minimax,
)
from verify_end_to_end_certificate import (
    verify_artifact as verify_single_artifact,
)
from verify_time_ensemble_certificate import verify_artifact


class ArithmeticMultiscaleSensingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scales = (
            NestedScale(20, 100),
            NestedScale(40, 200),
            NestedScale(60, 300),
        )
        self.modes = (
            DangerousMode(10, 11, 0.3, 0.0, 0.0),
            DangerousMode(10, 12, 0.2, 0.0, 0.0),
        )

    def test_proportional_scales_are_exactly_nested(self) -> None:
        scales = proportional_scales(20, 60, 20)
        self.assertEqual(
            [scale.spacing for scale in scales], [Fraction(1, 5)] * 3
        )
        self.assertEqual(
            centered_grid_inclusion_offset(scales[0], scales[2]), 100
        )

    def test_minimax_matches_independent_realized_objective(self) -> None:
        result = solve_positive_minimax(self.scales, self.modes)
        signatures = response_matrix(self.scales, self.modes)
        combined = signatures @ np.asarray(result.weights)
        realized = sum(
            mode.arithmetic_weight * abs(value)
            for mode, value in zip(self.modes, combined)
        )
        self.assertAlmostEqual(sum(result.weights), 1.0, places=12)
        self.assertGreaterEqual(min(result.weights), 0.0)
        self.assertAlmostEqual(result.objective, realized, places=11)

    def test_remote_cost_is_included_in_target_epigraph(self) -> None:
        remote = {10: (0.2, 0.1, 0.3)}
        result = solve_positive_minimax(self.scales, self.modes, remote)
        self.assertAlmostEqual(
            result.objective, result.target_upper_bounds[0][1], places=11
        )

    def test_sparse_search_obeys_required_outer_scale(self) -> None:
        results = search_sparse_supports(
            self.scales,
            self.modes,
            support_size=2,
            required_scale=self.scales[-1],
        )
        self.assertEqual(len(results), 2)
        self.assertTrue(
            all(self.scales[-1] in result.scales for result in results)
        )
        self.assertLessEqual(results[0].objective, results[1].objective)

    def test_dyadic_rounding_is_positive_and_exactly_normalized(self) -> None:
        weights = dyadic_rationalize((0.001907, 0.998093), 16)
        self.assertEqual(
            weights,
            (Fraction(125, 65_536), Fraction(65_411, 65_536)),
        )
        self.assertEqual(sum(weights, Fraction()), 1)

    def test_reference_measure_uses_only_outer_grid(self) -> None:
        design = reference_design()
        weights = materialize_outer_grid_weights(design)
        self.assertEqual(len(weights), 8_900)
        self.assertGreater(float(np.min(weights)), 0.0)
        self.assertAlmostEqual(float(np.sum(weights)), 1.0, places=15)
        self.assertEqual(
            centered_grid_inclusion_offset(
                NestedScale(510, 2_550), NestedScale(1_780, 8_900)
            ),
            3_175,
        )

    def test_non_nested_design_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            RationalMultiscaleDesign(
                (NestedScale(10, 50), NestedScale(20, 99)),
                (Fraction(1, 2), Fraction(1, 2)),
            )

    def test_formal_multiscale_artifact_is_hash_valid_and_certifies(self) -> None:
        path = (
            Path(__file__).resolve().parent
            / "certificates"
            / "arithmetic_sensing_v_multiscale_end_to_end.json"
        )
        with path.open(encoding="utf-8") as handle:
            artifact = json.load(handle)
        certificate = artifact["certificate"]
        self.assertTrue(verify_artifact(artifact, certificate)["verified"])
        self.assertEqual(
            artifact["formal_certificate_sha256"],
            "89b316584d9179c13232ad99b9515067fdf67329e6df3db4c48220d6b8c3ff7b",
        )
        self.assertEqual(
            certificate["parameters"]["distinct_sample_count"], 8_900
        )
        self.assertEqual(
            certificate["parameters"]["centered_grid_inclusion_offsets"],
            [3_175, 0],
        )
        self.assertTrue(
            certificate["consequence"]["integer_rounding_certificate"]
        )
        self.assertEqual(
            [
                dependency["formal_certificate_sha256"]
                for dependency in certificate["remote_dependencies"]
            ],
            [
                "c7f86fc51a19355ac882f3ede53d3870ed298eb5e09dc713259b5b5736d46409",
                "d515a57c8484649a7618912b9be08ebf49318cbe240df8cff2ff81e38194a4d7",
            ],
        )
        self.assertLess(
            certificate["consequence"]["coefficient_bound_decimal"], 0.5
        )

    def test_same_grid_single_window_control_does_not_certify(self) -> None:
        path = (
            Path(__file__).resolve().parent
            / "certificates"
            / "arithmetic_sensing_v_multiscale_T1780_single_end_to_end.json"
        )
        with path.open(encoding="utf-8") as handle:
            artifact = json.load(handle)
        certificate = artifact["certificate"]
        self.assertTrue(
            verify_single_artifact(artifact, certificate)["verified"]
        )
        self.assertEqual(
            artifact["formal_certificate_sha256"],
            "723d3069d31e927dadd5e1eddd28decd9d2a05b2ac3f1bd5d77706c4cc7222aa",
        )
        degree = certificate["degrees"][0]
        self.assertFalse(degree["integer_rounding_certificate"])
        self.assertGreater(degree["coefficient_bound_decimal"], 0.5)


if __name__ == "__main__":
    unittest.main()
