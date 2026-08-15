#!/usr/bin/env python3
"""Adversarial tests for the harmonic-completion Arb artifact."""

from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from flint import acb, arb_mat, ctx

from arithmetic_observability_harmonic_completion import (
    COMPLETION_TIMES,
    FORMAL_PRECISION_BITS,
    FULL_RAW_REAL_FLOOR,
    NEAR_DFT_FROBENIUS_UPPER,
    NEAR_DFT_RMS_GRAM_FLOOR,
    NEAR_DFT_SCALE_FREE_GRAM_FLOOR,
    ONE_AXIS_CONTRAST_COLUMNS,
    ONE_AXIS_CONTRAST_METRIC,
    RESTRICTED_REAL_FLOOR,
    SCHEMA,
    _canonical_json,
    _certify_real_generalized_floor,
    _real_source_gram,
    _read_artifact,
    build_artifact,
    build_payload,
    restricted_source_metric,
    verify_artifact,
)


ARTIFACT_PATH = Path("arithmetic_observability_harmonic_completion_certificate.json")


class HarmonicCompletionCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.built = build_artifact()

    def test_pinned_artifact_matches_fresh_arb_reconstruction(self) -> None:
        stored = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.built)
        verification = verify_artifact(stored)
        self.assertTrue(verification["verified"])
        self.assertTrue(verification["overall_passed"])

    def test_real_restricted_floor_and_normalization_are_pinned(self) -> None:
        section = self.built["payload"]["restricted_real_completion"]
        certificate = section["certificate"]
        self.assertEqual(section["complex_row_weight_exact"], "1/14")
        self.assertEqual(certificate["floor_exact"], "1/25")
        self.assertEqual(RESTRICTED_REAL_FLOOR, Fraction(1, 25))
        self.assertEqual(certificate["dimension"], 27)
        self.assertEqual(certificate["leading_principal_minor_signs"], [1] * 27)
        self.assertTrue(certificate["passed"])

    def test_full_uniform_raw_floor_and_normalization_are_pinned(self) -> None:
        section = self.built["payload"]["full_uniform_raw_real_operator"]
        certificate = section["certificate"]
        self.assertEqual(section["complex_row_weight_exact"], "1/62")
        self.assertIn("uniform RMS", section["observation_norm"])
        self.assertEqual(section["preprocessing"], "none; no inverse-Vandermonde calibration is used")
        self.assertEqual(certificate["floor_exact"], "1/500")
        self.assertEqual(FULL_RAW_REAL_FLOOR, Fraction(1, 500))
        self.assertEqual(certificate["dimension"], 64)
        self.assertEqual(certificate["leading_principal_minor_signs"], [1] * 64)
        self.assertTrue(certificate["passed"])

    def test_near_dft_component_has_rigorous_perturbation_margins(self) -> None:
        certificate = self.built["payload"]["complex_near_dft_completion"]
        self.assertEqual(len(certificate["schedule"]), 27)
        self.assertEqual(len(certificate["residual_records"]), 27)
        self.assertTrue(certificate["exact_fourier_basis_and_ideal_matrix_verified"])
        self.assertTrue(certificate["all_nearest_integer_windings_certified"])
        self.assertTrue(certificate["frobenius_error_certainly_below_upper"])
        self.assertEqual(
            certificate["frobenius_error_upper_exact"],
            f"{NEAR_DFT_FROBENIUS_UPPER.numerator}/{NEAR_DFT_FROBENIUS_UPPER.denominator}",
        )
        self.assertEqual(
            certificate["scale_free_gram_floor_exact"],
            f"{NEAR_DFT_SCALE_FREE_GRAM_FLOOR.numerator}/{NEAR_DFT_SCALE_FREE_GRAM_FLOOR.denominator}",
        )
        self.assertEqual(
            certificate["rms_time_gram_floor_exact"],
            f"{NEAR_DFT_RMS_GRAM_FLOOR.numerator}/{NEAR_DFT_RMS_GRAM_FLOOR.denominator}",
        )
        self.assertTrue(certificate["exact_rational_implications_verified"])
        self.assertTrue(certificate["passed"])

    def test_exact_cent_schedule_is_canonical_and_strictly_increasing(self) -> None:
        self.assertEqual(len(COMPLETION_TIMES), 14)
        self.assertEqual(COMPLETION_TIMES[0], Fraction(1279, 100))
        self.assertEqual(COMPLETION_TIMES[-1], Fraction(8953, 50))
        self.assertTrue(
            all(left < right for left, right in zip(COMPLETION_TIMES, COMPLETION_TIMES[1:]))
        )
        self.assertTrue(all((100 * value).denominator == 1 for value in COMPLETION_TIMES))

    def test_integer_contrast_basis_has_the_declared_exact_metric(self) -> None:
        computed = tuple(
            tuple(sum(left[a] * right[a] for a in range(4)) for right in ONE_AXIS_CONTRAST_COLUMNS)
            for left in ONE_AXIS_CONTRAST_COLUMNS
        )
        self.assertEqual(computed, ONE_AXIS_CONTRAST_METRIC)
        self.assertTrue(all(sum(column) == 0 for column in ONE_AXIS_CONTRAST_COLUMNS))
        metric = restricted_source_metric()
        self.assertEqual(metric.nrows(), 27)
        self.assertEqual(metric.ncols(), 27)
        self.assertTrue(metric.det() > 0)

    def test_real_source_gram_uses_both_complex_quadratures(self) -> None:
        with ctx.workprec(FORMAL_PRECISION_BITS):
            gram = _real_source_gram([[acb(1, 2)]])
        self.assertTrue(gram[0, 0].contains(5))
        self.assertFalse(gram[0, 0].contains(1))

    def test_sylvester_negative_control_rejects_false_floor(self) -> None:
        gram = arb_mat([[2, 0], [0, 1]])
        metric = arb_mat([[1, 0], [0, 1]])
        valid = _certify_real_generalized_floor(gram, metric, Fraction(1, 2))
        invalid = _certify_real_generalized_floor(gram, metric, Fraction(3, 2))
        self.assertTrue(valid["passed"])
        self.assertFalse(invalid["passed"])

    def test_payload_is_json_serializable_and_uses_pinned_precision(self) -> None:
        json.dumps(self.built, sort_keys=True)
        self.assertEqual(
            self.built["payload"]["implementation"]["arb_precision_bits"],
            FORMAL_PRECISION_BITS,
        )
        self.assertFalse(
            self.built["payload"]["implementation"]["binary64_used_for_proof_decisions"]
        )

    def test_too_little_or_excessive_precision_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "resource limits"):
            build_payload(128)
        with self.assertRaisesRegex(ValueError, "resource limits"):
            build_payload(2048)
        with self.assertRaisesRegex(ValueError, "canonical integer"):
            build_payload(True)

    def test_stale_digest_tampering_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["restricted_real_completion"]["certificate"]["floor_exact"] = "1/26"
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            verify_artifact(tampered)

    def test_rehashed_semantic_tampering_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["full_uniform_raw_real_operator"]["certificate"]["floor_exact"] = "1/501"
        tampered["payload_sha256"] = hashlib.sha256(
            _canonical_json(tampered["payload"])
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "independent Arb reconstruction"):
            verify_artifact(tampered)

    def test_numeric_alias_tampering_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["parameters"]["primes"][0] = 2.0
        tampered["payload_sha256"] = hashlib.sha256(
            _canonical_json(tampered["payload"])
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "noncanonical prime axes"):
            verify_artifact(tampered)

    def test_schedule_tampering_is_rejected_before_reconstruction(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["parameters"]["completion_times_exact"][0] = "13/1"
        tampered["payload_sha256"] = hashlib.sha256(
            _canonical_json(tampered["payload"])
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "noncanonical completion schedule"):
            verify_artifact(tampered)

    def test_unknown_top_level_field_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["comment"] = "not covered by the schema"
        with self.assertRaisesRegex(ValueError, "unexpected top-level"):
            verify_artifact(tampered)

    def test_duplicate_json_keys_are_rejected_at_the_file_boundary(self) -> None:
        text = (
            '{"schema":"attacker","schema":"'
            + SCHEMA
            + '","payload":{},"payload_sha256":"'
            + "0" * 64
            + '"}'
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON object key"):
                _read_artifact(path)

    def test_nonfinite_json_numbers_are_rejected_at_the_file_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nonfinite.json"
            path.write_text('{"value":NaN}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-finite JSON constant"):
                _read_artifact(path)

    def test_negative_zero_is_rejected_at_the_file_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "negative-zero.json"
            path.write_text('{"value":-0}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "negative-zero"):
                _read_artifact(path)

    def test_json_floats_are_rejected_at_the_file_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "float.json"
            path.write_text('{"value":2.0}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "floating-point"):
                _read_artifact(path)

    def test_resource_caps_reject_oversized_evidence_lists(self) -> None:
        tampered = copy.deepcopy(self.built)
        signs = tampered["payload"]["restricted_real_completion"]["certificate"]["leading_principal_minor_signs"]
        signs.append(1)
        tampered["payload_sha256"] = hashlib.sha256(
            _canonical_json(tampered["payload"])
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "resource cap"):
            verify_artifact(tampered)

    def test_schema_is_exactly_pinned(self) -> None:
        self.assertEqual(self.built["schema"], SCHEMA)
        tampered = copy.deepcopy(self.built)
        tampered["schema"] = f"{SCHEMA}-future"
        with self.assertRaisesRegex(ValueError, "unsupported"):
            verify_artifact(tampered)


if __name__ == "__main__":
    unittest.main()
