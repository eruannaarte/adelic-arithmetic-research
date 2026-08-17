#!/usr/bin/env python3
"""Adversarial tests for the reading-complexity Arb certificate."""

from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import flint
from flint import arb_mat

from arithmetic_observability_reading_complexity import (
    AMBIENT_DIMENSION,
    COMPLEX_DETERMINANT_MODULUS_SQUARED_LOWER,
    COMPLEX_FOUR_TIMES,
    FORMAL_PRECISION_BITS,
    INTERVAL_DISPLAY_DIGITS,
    MAX_ARTIFACT_BYTES,
    PARAMETER_POINT,
    REAL_GRAM_FLOOR,
    REAL_TWO_TIMES,
    RESONANCE_CYCLE_MARGIN,
    SCHEMA,
    VANDERMONDE_CHORD_SQUARED_FLOOR,
    VANDERMONDE_TAU,
    _canonical_json,
    _certify_real_gram_floor,
    _read_artifact,
    _validate_resource_tree,
    build_artifact,
    build_payload,
    verify_artifact,
)


ARTIFACT_PATH = Path("arithmetic_observability_reading_complexity_certificate.json")
PINNED_PAYLOAD_SHA256 = (
    "4b652c09feb7d68c6eb10c143086c390ee5f48e7618aee694e174d513804ef8e"
)


def _rehash(artifact: dict[str, object]) -> None:
    artifact["payload_sha256"] = hashlib.sha256(
        _canonical_json(artifact["payload"])
    ).hexdigest()


class ReadingComplexityCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.built = build_artifact()

    def test_pinned_artifact_matches_independent_arb_rebuild(self) -> None:
        stored = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.built)
        verified = verify_artifact(stored)
        self.assertTrue(verified["verified"])
        self.assertTrue(verified["overall_passed"])
        self.assertEqual(verified["intersection_number_combinatorics"], 162)

    def test_two_nonzero_readings_have_certified_full_real_rank(self) -> None:
        section = self.built["payload"]["two_nonzero_time_real_jacobian"]
        certificate = section["gram_floor_certificate"]
        self.assertEqual(section["schedule_exact"], ["1/4", "1/2"])
        self.assertEqual(tuple(REAL_TWO_TIMES), (Fraction(1, 4), Fraction(1, 2)))
        self.assertTrue(section["all_times_nonzero"])
        self.assertEqual(section["jacobian_shape"], [4, 4])
        self.assertEqual(section["positive_parameter_point_exact"], ["1/1", "1/2", "1/1", "2/1"])
        self.assertEqual(tuple(PARAMETER_POINT), (Fraction(1), Fraction(1, 2), Fraction(1), Fraction(2)))
        self.assertTrue(section["jacobian_determinant_certainly_nonzero"])
        self.assertEqual(certificate["floor_exact"], "2/1")
        self.assertEqual(REAL_GRAM_FLOOR, Fraction(2))
        self.assertEqual(certificate["leading_principal_minor_signs"], [1] * 4)
        self.assertTrue(certificate["passed"])
        self.assertTrue(section["passed"])

    def test_real_floor_negative_control_rejects_false_claim(self) -> None:
        gram = arb_mat([[2, 0], [0, 1]])
        valid = _certify_real_gram_floor(gram, Fraction(1, 2))
        invalid = _certify_real_gram_floor(gram, Fraction(3, 2))
        self.assertTrue(valid["passed"])
        self.assertFalse(invalid["passed"])

    def test_four_time_complex_jacobian_is_nonzero(self) -> None:
        section = self.built["payload"]["four_time_complex_sections"]
        self.assertEqual(section["schedule_exact"], ["0/1", "1/10", "1/5", "3/10"])
        self.assertEqual(tuple(COMPLEX_FOUR_TIMES), (Fraction(0), Fraction(1, 10), Fraction(1, 5), Fraction(3, 10)))
        self.assertEqual(section["complex_jacobian_shape"], [4, 4])
        self.assertEqual(
            section["determinant_modulus_squared_lower_exact"], "500000/1"
        )
        self.assertEqual(
            COMPLEX_DETERMINANT_MODULUS_SQUARED_LOWER, Fraction(500_000)
        )
        self.assertTrue(section["determinant_modulus_squared_certainly_above_lower"])
        self.assertTrue(section["passed"])

    def test_four_time_resonance_margin_is_explicit_and_complete(self) -> None:
        certificate = self.built["payload"]["four_time_complex_sections"][
            "basepoint_free_resonance_certificate"
        ]
        self.assertEqual(certificate["root_quotient_indices_mod_4"], [0, 1, 2, 3])
        self.assertTrue(certificate["root_quotient_set_is_all_fourth_roots_exact"])
        self.assertEqual(certificate["pair_axis_record_count"], 18)
        self.assertEqual(len(certificate["records"]), 18)
        self.assertEqual(certificate["cycle_margin_exact"], "1/100")
        self.assertEqual(RESONANCE_CYCLE_MARGIN, Fraction(1, 100))
        self.assertTrue(certificate["every_pair_axis_distance_strictly_above_margin"])
        self.assertTrue(certificate["every_distance_strictly_below_one_eighth_cycle"])
        self.assertTrue(certificate["basepoint_free_finite_input_verified"])

    def test_degree_162_is_exact_combinatorics_not_a_fake_interval_claim(self) -> None:
        degree = self.built["payload"]["four_time_complex_sections"][
            "degree_combinatorics"
        ]
        self.assertEqual(degree["axis_count"], 3)
        self.assertEqual(degree["q4_degree"], 3)
        self.assertEqual(degree["permutation_coefficient"], 6)
        self.assertEqual(degree["degree_power"], 27)
        self.assertEqual(degree["intersection_number_combinatorics"], 162)
        scope = self.built["payload"]["formal_scope"]
        self.assertFalse(scope["topological_finiteness_proved_by_certificate"])
        self.assertFalse(scope["intersection_theory_proved_by_certificate"])

    def test_full_vandermonde_schedule_has_64_distinct_nodes(self) -> None:
        section = self.built["payload"]["full_vandermonde_upper_schedule"]
        self.assertEqual(section["tau_exact"], "1/10")
        self.assertEqual(VANDERMONDE_TAU, Fraction(1, 10))
        self.assertEqual(section["sample_count"], AMBIENT_DIMENSION)
        self.assertEqual(len(section["schedule_exact"]), AMBIENT_DIMENSION)
        self.assertEqual(len(section["node_records"]), AMBIENT_DIMENSION)
        bases = [record["integer_base"] for record in section["node_records"]]
        self.assertEqual(len(set(bases)), AMBIENT_DIMENSION)
        self.assertEqual(section["pair_count"], 2016)
        self.assertEqual(section["squared_chord_floor_exact"], "1/100000")
        self.assertEqual(VANDERMONDE_CHORD_SQUARED_FLOOR, Fraction(1, 100_000))
        self.assertEqual(section["minimum_ratio_exact"], "25/24")
        self.assertEqual(section["minimum_ratio_tie_count"], 6)
        self.assertEqual(section["minimum_pair_indices"], [2, 52])
        self.assertEqual(section["minimum_pair_integer_bases"], [25, 24])
        self.assertEqual(
            section["minimum_pair_selection_rule"],
            "exact ratio, then lexicographic indices",
        )
        self.assertEqual(
            section["minimum_ratio_tie_pairs"],
            sorted(section["minimum_ratio_tie_pairs"]),
        )
        self.assertTrue(section["phase_spread_certainly_below_pi"])
        self.assertTrue(section["every_squared_chord_certainly_above_floor"])
        self.assertTrue(section["vandermonde_nodes_pairwise_distinct_certified"])

    def test_formal_scope_omits_the_unproved_reciprocal_collision(self) -> None:
        scope = self.built["payload"]["formal_scope"]
        self.assertFalse(scope["reciprocal_collision_formally_certified"])
        self.assertFalse(scope["global_injectivity_claimed"])
        self.assertFalse(scope["schedule_optimality_claimed"])
        self.assertFalse(scope["vandermonde_determinant_formula_proved_by_certificate"])

    def test_payload_is_float_free_and_uses_pinned_precision(self) -> None:
        rendered = json.dumps(self.built, sort_keys=True)
        self.assertIsInstance(rendered, str)
        implementation = self.built["payload"]["implementation"]
        self.assertEqual(implementation["arb_precision_bits"], FORMAL_PRECISION_BITS)
        self.assertEqual(implementation["python_flint_version"], flint.__version__)
        self.assertEqual(implementation["flint_version"], flint.__FLINT_VERSION__)
        self.assertEqual(
            implementation["serialized_interval_digits"], INTERVAL_DISPLAY_DIGITS
        )
        self.assertFalse(implementation["binary64_used_for_proof_decisions"])
        self.assertTrue(implementation["all_transcendentals_enclosed_by_arb"])

    def test_precision_resource_limits_are_enforced(self) -> None:
        with self.assertRaisesRegex(ValueError, "resource limits"):
            build_payload(128)
        with self.assertRaisesRegex(ValueError, "resource limits"):
            build_payload(2048)
        with self.assertRaisesRegex(ValueError, "canonical integer"):
            build_payload(True)

    def test_stale_digest_tampering_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["four_time_complex_sections"][
            "determinant_modulus_squared_lower_exact"
        ] = "499999/1"
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            verify_artifact(tampered)

    def test_rehashed_semantic_tampering_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["four_time_complex_sections"]["degree_combinatorics"][
            "intersection_number_combinatorics"
        ] = 161
        _rehash(tampered)
        with self.assertRaisesRegex(ValueError, "independent Arb reconstruction"):
            verify_artifact(tampered)

    def test_parameter_tampering_is_rejected_before_rebuild(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["parameters"]["primes"][2] = 7
        _rehash(tampered)
        with self.assertRaisesRegex(ValueError, "noncanonical prime axes"):
            verify_artifact(tampered)

    def test_duplicate_schedule_entry_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        schedule = tampered["payload"]["full_vandermonde_upper_schedule"][
            "schedule_exact"
        ]
        schedule[1] = schedule[0]
        _rehash(tampered)
        with self.assertRaisesRegex(ValueError, "noncanonical Vandermonde schedule"):
            verify_artifact(tampered)

    def test_duplicate_node_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        nodes = tampered["payload"]["full_vandermonde_upper_schedule"]["node_records"]
        nodes[1] = copy.deepcopy(nodes[0])
        _rehash(tampered)
        with self.assertRaisesRegex(ValueError, "noncanonical Vandermonde node"):
            verify_artifact(tampered)

    def test_rehashed_false_interval_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["two_nonzero_time_real_jacobian"][
            "gram_floor_certificate"
        ]["leading_principal_minor_intervals"][0] = "[0 +/- 0]"
        _rehash(tampered)
        with self.assertRaisesRegex(ValueError, "independent Arb reconstruction"):
            verify_artifact(tampered)

    def test_float_numeric_alias_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["parameters"]["primes"][0] = 2.0
        _rehash(tampered)
        with self.assertRaisesRegex(ValueError, "forbidden floating-point"):
            verify_artifact(tampered)

    def test_boolean_integer_alias_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["parameters"]["axis_count"] = True
        _rehash(tampered)
        with self.assertRaisesRegex(ValueError, "not a canonical integer"):
            verify_artifact(tampered)

    def test_unknown_top_level_field_and_wrong_schema_are_rejected(self) -> None:
        extra = copy.deepcopy(self.built)
        extra["comment"] = "outside the authenticated schema"
        with self.assertRaisesRegex(ValueError, "unexpected top-level"):
            verify_artifact(extra)
        wrong_schema = copy.deepcopy(self.built)
        wrong_schema["schema"] = f"{SCHEMA}-future"
        with self.assertRaisesRegex(ValueError, "unsupported"):
            verify_artifact(wrong_schema)

        extra_payload = copy.deepcopy(self.built)
        extra_payload["payload"]["unauthenticated"] = True
        _rehash(extra_payload)
        with self.assertRaisesRegex(ValueError, "payload has unexpected fields"):
            verify_artifact(extra_payload)

    def test_duplicate_json_keys_are_rejected_at_file_boundary(self) -> None:
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

    def test_nonfinite_float_and_negative_zero_are_rejected_at_file_boundary(self) -> None:
        cases = (
            ('{"value":NaN}', "non-finite JSON constant"),
            ('{"value":2.0}', "floating-point"),
            ('{"value":-0}', "negative-zero"),
        )
        with tempfile.TemporaryDirectory() as directory:
            for index, (text, message) in enumerate(cases):
                path = Path(directory) / f"bad-{index}.json"
                path.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, message):
                    _read_artifact(path)

    def test_file_and_tree_resource_caps_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "oversized.json"
            path.write_bytes(b" " * (MAX_ARTIFACT_BYTES + 1))
            with self.assertRaisesRegex(ValueError, "serialized resource cap"):
                _read_artifact(path)
        with self.assertRaisesRegex(ValueError, "list exceeds the resource cap"):
            _validate_resource_tree([0] * 257)
        nested: object = "leaf"
        for _ in range(20):
            nested = [nested]
        with self.assertRaisesRegex(ValueError, "maximum JSON depth"):
            _validate_resource_tree(nested)

    def test_schema_and_digest_are_pinned(self) -> None:
        self.assertEqual(self.built["schema"], SCHEMA)
        self.assertEqual(self.built["payload_sha256"], PINNED_PAYLOAD_SHA256)
        self.assertEqual(
            self.built["payload_sha256"],
            hashlib.sha256(_canonical_json(self.built["payload"])).hexdigest(),
        )

    def test_cli_write_is_byte_deterministic(self) -> None:
        root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rebuilt.json"
            subprocess.run(
                [
                    sys.executable,
                    str(root / "arithmetic_observability_reading_complexity.py"),
                    "--write",
                    str(path),
                ],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(path.read_bytes(), ARTIFACT_PATH.read_bytes())
            self.assertNotIn(b"\r\n", path.read_bytes())


if __name__ == "__main__":
    unittest.main()
