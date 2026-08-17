import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from fractions import Fraction

from arithmetic_observability_asv_bridge import (
    SCHEMA,
    build_artifact,
    derive_payload,
    verify_artifact,
)


SOURCE = Path("certificates/arithmetic_sensing_v_multiscale_end_to_end.json")
ARTIFACT = Path("arithmetic_observability_asv_bridge_certificate.json")


class ArithmeticSensingBridgeTests(unittest.TestCase):
    def test_pinned_artifact_verifies(self):
        result = verify_artifact(ARTIFACT, SOURCE)
        self.assertTrue(result["verified"])
        self.assertEqual(result["schema"], SCHEMA)
        self.assertEqual(result["lower_radius_decimal"], "7.8873507724418666e-7")
        self.assertEqual(result["upper_radius_decimal"], "2.0000000000000000e-4")

    def test_exact_bracket_has_correct_order(self):
        consequence = derive_payload(SOURCE)["exact_consequence"]
        lower_num, lower_den = map(
            int, consequence["robust_noise_radius_lower_squared"].split("/")
        )
        upper_num, upper_den = map(
            int, consequence["robust_noise_radius_upper_squared"].split("/")
        )
        self.assertLess(lower_num * upper_den, upper_num * lower_den)

    def test_displayed_decimals_are_exactly_outward(self):
        consequence = derive_payload(SOURCE)["exact_consequence"]
        for decimal_key, squared_key in (
            ("lower_distance_decimal", "inter_fibre_distance_lower_squared"),
            ("lower_radius_decimal", "robust_noise_radius_lower_squared"),
        ):
            candidate = Fraction(consequence[decimal_key])
            exact_square = Fraction(consequence[squared_key])
            self.assertLessEqual(candidate * candidate, exact_square)
        for decimal_key, squared_key in (
            ("upper_distance_decimal", "inter_fibre_distance_upper_squared"),
            ("upper_radius_decimal", "robust_noise_radius_upper_squared"),
        ):
            candidate = Fraction(consequence[decimal_key])
            exact_square = Fraction(consequence[squared_key])
            self.assertGreaterEqual(candidate * candidate, exact_square)

    def test_source_parameters_are_pinned(self):
        payload = derive_payload(SOURCE)
        self.assertEqual(payload["parameters"]["degree"], 14)
        self.assertEqual(payload["parameters"]["maximum_norm"], 50)
        self.assertEqual(payload["parameters"]["sigma"], 2)
        self.assertEqual(payload["parameters"]["distinct_sample_count"], 8900)

    def test_recomputed_artifact_matches_builder(self):
        stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(stored, build_artifact(SOURCE))

    def test_payload_tampering_with_stale_hash_is_rejected(self):
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        artifact["payload"]["exact_consequence"]["upper_radius_decimal"] = "0"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tampered.json"
            path.write_text(json.dumps(artifact), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                verify_artifact(path, SOURCE)

    def test_payload_tampering_with_recomputed_hash_is_rejected(self):
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        artifact["payload"]["exact_consequence"]["upper_radius_decimal"] = "0"
        canonical = json.dumps(
            artifact["payload"], sort_keys=True, separators=(",", ":")
        ).encode("ascii")
        artifact["payload_sha256"] = hashlib.sha256(canonical).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tampered.json"
            path.write_text(json.dumps(artifact), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exact reconstruction"):
                verify_artifact(path, SOURCE)

    def test_numeric_alias_tampering_is_rejected(self):
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        artifact["payload"]["parameters"]["degree"] = 14.0
        canonical = json.dumps(
            artifact["payload"], sort_keys=True, separators=(",", ":")
        ).encode("ascii")
        artifact["payload_sha256"] = hashlib.sha256(canonical).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tampered.json"
            path.write_text(json.dumps(artifact), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exact reconstruction"):
                verify_artifact(path, SOURCE)

    def test_source_formal_digest_tampering_is_rejected(self):
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        source["formal_certificate_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.json"
            path.write_text(json.dumps(source), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "formal certificate digest"):
                derive_payload(path)

    def test_source_rounding_claim_tampering_breaks_content_digest(self):
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        source["certificate"]["consequence"]["integer_rounding_certificate"] = False
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.json"
            path.write_text(json.dumps(source), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "content digest"):
                derive_payload(path)

    def test_used_source_value_tampering_is_rejected(self):
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        source["certificate"]["gram"]["maximum_row_upper"] = "0/1"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.json"
            path.write_text(json.dumps(source), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "content digest"):
                derive_payload(path)


if __name__ == "__main__":
    unittest.main()
