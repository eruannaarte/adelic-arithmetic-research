#!/usr/bin/env python3

import json
import unittest
from pathlib import Path

import numpy as np

from time_ensemble_design import (
    LONG_SAMPLES,
    SHORT_SAMPLES,
    centered_grid_inclusion_offset,
    combined_outer_grid_weights,
    reference_designs,
    reference_weights,
)
from optimized_arithmetic_quadrature import centered_cosine_response
from verify_end_to_end_certificate import (
    verify_artifact as verify_single_artifact,
)
from verify_time_ensemble_certificate import verify_artifact


class TimeEnsembleDesignTests(unittest.TestCase):
    def test_short_grid_is_exactly_nested(self) -> None:
        offset = centered_grid_inclusion_offset()
        self.assertEqual(offset, 3_225)
        # Five times twice a centered grid point is an integer.  Compare those
        # exact integer coordinates rather than two binary64 construction paths.
        short_coordinates = 2 * np.arange(SHORT_SAMPLES) - (
            SHORT_SAMPLES - 1
        )
        long_coordinates = 2 * np.arange(LONG_SAMPLES) - (
            LONG_SAMPLES - 1
        )
        np.testing.assert_array_equal(
            long_coordinates[offset : offset + SHORT_SAMPLES],
            short_coordinates,
        )

    def test_combined_outer_weights_are_positive_and_normalized(self) -> None:
        weights = combined_outer_grid_weights()
        self.assertEqual(len(weights), LONG_SAMPLES)
        self.assertGreater(float(np.min(weights)), 0.0)
        self.assertAlmostEqual(float(np.sum(weights)), 1.0, places=15)

    def test_materialized_weights_match_centered_ensemble_kernel(self) -> None:
        weights = combined_outer_grid_weights()
        outer_times = (
            np.arange(LONG_SAMPLES) - (LONG_SAMPLES - 1) / 2.0
        ) / 5.0
        frequencies = np.asarray([0.01, 0.1, np.log(51.0 / 50.0)])
        direct = weights @ np.exp(
            1j * np.outer(outer_times, frequencies)
        )
        designs = reference_designs()
        mixing = reference_weights()
        expected = sum(
            weight * centered_cosine_response(frequencies, design)
            for weight, design in zip(mixing, designs)
        )
        np.testing.assert_allclose(direct, expected, atol=2e-13, rtol=0.0)

    def test_dyadic_weight_suppresses_dominant_mode(self) -> None:
        short, long = reference_designs()
        alpha, beta = reference_weights()
        frequency = np.log(51.0 / 50.0)
        short_response = float(centered_cosine_response(frequency, short))
        long_response = float(centered_cosine_response(frequency, long))
        combined = alpha * short_response + beta * long_response
        self.assertLess(abs(combined), abs(long_response) / 190.0)

    def test_published_artifact_is_hash_valid_and_certifies(self) -> None:
        path = (
            Path(__file__).resolve().parent
            / "certificates"
            / "arithmetic_sensing_v_time_ensemble_end_to_end.json"
        )
        with path.open(encoding="utf-8") as handle:
            artifact = json.load(handle)
        certificate = artifact["certificate"]
        self.assertTrue(verify_artifact(artifact, certificate)["verified"])
        self.assertEqual(
            artifact["formal_certificate_sha256"],
            "1cc643118a3aad8e31e621c0c913742975723b47263199f1e0aeb598d8d1036e",
        )
        parameters = certificate["parameters"]
        self.assertEqual(parameters["distinct_sample_count"], 8_950)
        self.assertEqual(parameters["maximum_observation_time"], 1_790)
        self.assertEqual(
            parameters["centered_grid_inclusion_offsets"], [3_225, 0]
        )
        self.assertTrue(
            certificate["consequence"]["integer_rounding_certificate"]
        )
        self.assertLess(
            certificate["consequence"]["coefficient_bound_decimal"],
            0.5,
        )
        self.assertEqual(
            [
                dependency["formal_certificate_sha256"]
                for dependency in certificate["remote_dependencies"]
            ],
            [
                "d21502db2d2418c049d64e4d0dbd2ce733293ee834e32fe82c401c8c50d87ec0",
                "470cf6021d2320ce175d449875de61037922ab9c884474aa3446212985abcbb7",
            ],
        )

    def test_same_grid_single_window_control_does_not_certify(self) -> None:
        path = (
            Path(__file__).resolve().parent
            / "certificates"
            / "arithmetic_sensing_v_time_ensemble_T1790_single_end_to_end.json"
        )
        with path.open(encoding="utf-8") as handle:
            artifact = json.load(handle)
        self.assertTrue(
            verify_single_artifact(artifact, artifact["certificate"])[
                "verified"
            ]
        )
        self.assertEqual(
            artifact["formal_certificate_sha256"],
            "215ca087bc9e29de1b81cbfa8ee6171fb4dfadb2a2e7dbc3b61e6f0b9d57e7f2",
        )
        degree = artifact["certificate"]["degrees"][0]
        self.assertFalse(degree["integer_rounding_certificate"])
        self.assertGreater(degree["coefficient_bound_decimal"], 0.5)


if __name__ == "__main__":
    unittest.main()
