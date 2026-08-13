#!/usr/bin/env python3

import json
import unittest
from pathlib import Path

from degree_fourteen_resource_law import ResourcePoint
from verify_end_to_end_certificate import verify_artifact


class DegreeFourteenResourceLawTests(unittest.TestCase):
    def _artifact(self, name: str) -> dict[str, object]:
        path = Path(__file__).resolve().parent / "certificates" / name
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)

    def test_resource_point_threshold_is_strict(self) -> None:
        failure = ResourcePoint(1_000, 14_690, 0.5, 0.0, 0.0, 0.0, 0.0)
        success = ResourcePoint(
            1_000, 14_691, 0.5 - 1e-12, 0.0, 0.0, 0.0, 0.0
        )
        self.assertFalse(failure.certified_by_proxy)
        self.assertTrue(success.certified_by_proxy)

    def test_published_sampling_pair_straddles_half(self) -> None:
        failure = self._artifact(
            "arithmetic_sensing_v_degree14_m14690_end_to_end.json"
        )
        success = self._artifact(
            "arithmetic_sensing_v_degree14_m14691_end_to_end.json"
        )
        self.assertTrue(
            verify_artifact(failure, failure["certificate"])["verified"]
        )
        self.assertTrue(
            verify_artifact(success, success["certificate"])["verified"]
        )
        failure_degree = failure["certificate"]["degrees"][0]
        success_degree = success["certificate"]["degrees"][0]
        self.assertFalse(failure_degree["integer_rounding_certificate"])
        self.assertTrue(success_degree["integer_rounding_certificate"])
        self.assertGreater(failure_degree["coefficient_bound_decimal"], 0.5)
        self.assertLess(success_degree["coefficient_bound_decimal"], 0.5)
        self.assertEqual(
            failure["formal_certificate_sha256"],
            "bdcf19c1916cf5bdb8c20a2d159e41cc73b9c97f4ebf2a4da68726534be25756",
        )
        self.assertEqual(
            success["formal_certificate_sha256"],
            "02164e418f144cf8f96645da79a914964af3c3dc4df7a2a2cd2de63da3e7a194",
        )
        self.assertEqual(
            (
                failure["certificate"]["parameters"]["observation_time"],
                failure["certificate"]["parameters"]["sample_count"],
            ),
            (1_000, 14_690),
        )
        self.assertEqual(
            (
                success["certificate"]["parameters"]["observation_time"],
                success["certificate"]["parameters"]["sample_count"],
            ),
            (1_000, 14_691),
        )

    def test_published_time_pair_straddles_half(self) -> None:
        failure = self._artifact(
            "arithmetic_sensing_v_degree14_T1892_end_to_end.json"
        )
        success = self._artifact(
            "arithmetic_sensing_v_degree14_T1893_end_to_end.json"
        )
        self.assertTrue(
            verify_artifact(failure, failure["certificate"])["verified"]
        )
        self.assertTrue(
            verify_artifact(success, success["certificate"])["verified"]
        )
        self.assertFalse(
            failure["certificate"]["degrees"][0][
                "integer_rounding_certificate"
            ]
        )
        self.assertTrue(
            success["certificate"]["degrees"][0][
                "integer_rounding_certificate"
            ]
        )
        self.assertEqual(
            failure["formal_certificate_sha256"],
            "85ce1bea72b18d89f4f295e49ff827969a48971741827fa4d3b38d0dbbb5f9e1",
        )
        self.assertEqual(
            success["formal_certificate_sha256"],
            "06cb07c5fc52f798fefcda66f0ebca10996aaa6a21b13e14c1b208de36ffac16",
        )
        self.assertEqual(
            (
                failure["certificate"]["parameters"]["observation_time"],
                failure["certificate"]["parameters"]["sample_count"],
            ),
            (1_892, 9_460),
        )
        self.assertEqual(
            (
                success["certificate"]["parameters"]["observation_time"],
                success["certificate"]["parameters"]["sample_count"],
            ),
            (1_893, 9_465),
        )


if __name__ == "__main__":
    unittest.main()
