#!/usr/bin/env python3

import copy
import json
import unittest
from fractions import Fraction
from pathlib import Path

from verify_residual_stopping_certificate import verify_artifact


class ResidualStoppingEnvelopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = (
            Path(__file__).resolve().parent
            / "certificates"
            / "arithmetic_sensing_v_residual_stopping.json"
        )
        with path.open(encoding="utf-8") as handle:
            cls.artifact = json.load(handle)

    def test_published_artifact_closes_declared_finite_supports(self) -> None:
        certificate = self.artifact["certificate"]
        self.assertTrue(
            verify_artifact(self.artifact, certificate)["verified"]
        )
        self.assertEqual(
            self.artifact["formal_certificate_sha256"],
            "5e098d01666af97a9535e466bd9d12e723a72c069af659c82a3a980a9b29bb53",
        )
        self.assertEqual(
            certificate["selected_mode_screen"]["survivor_times"],
            [440, 480, 490, 500, 520],
        )
        consequence = certificate["consequence"]
        self.assertTrue(consequence["finite_mode_stopping_certificate"])
        self.assertTrue(
            consequence["all_competing_pair_supports_eliminated"]
        )
        self.assertEqual(consequence["closest_competing_time"], 500)
        self.assertGreater(
            float(Fraction(consequence["full_support_separation"])),
            5.08e-7,
        )

    def test_infeasible_special_dual_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.artifact)
        tampered["certificate"]["full_tail_duals"][0][
            "special_dual_value"
        ] = "2"
        with self.assertRaises(ValueError):
            verify_artifact(tampered, tampered["certificate"])


if __name__ == "__main__":
    unittest.main()
