#!/usr/bin/env python3
"""Adversarial tests for the Arithmetic Observability V Arb certificate."""

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
from flint import ctx

from arithmetic_observability_global_design import (
    APPROXIMATE_INVERSE,
    AXIS_COUNT,
    COLLISION_TIMES,
    FIXED_FUNCTION_ABSOLUTE_CAP,
    FIXED_ROOT_RADIUS,
    FORMAL_PRECISION_BITS,
    INTERVAL_DISPLAY_DIGITS,
    KAPPA_FLOOR,
    LEAKAGE_UPPER,
    MAX_ARTIFACT_BYTES,
    PARAMETER_TIME_RADIUS,
    PARAMETER_FUNCTION_ABSOLUTE_CAP,
    PARAMETER_X_RADIUS,
    PHASE_DIAGONAL_LOWER,
    PHASE_DIAGONAL_UPPER,
    PHASE_OFF_DIAGONAL_RADIUS,
    PHASE_TIME_RADIUS,
    PHASE_TIMES,
    PHASE_WINDINGS,
    PINNED_FLINT_VERSION,
    PINNED_PYTHON_FLINT_VERSION,
    RAW_AND_CHORD_FLOOR,
    ROOT_CENTER,
    ROOT_CENTER_DECIMALS,
    SCHEMA,
    SINE_TWO_LOWER,
    TORUS_GAP_FLOOR,
    TORUS_WIDTH,
    _build_phase_design_section,
    _canonical_json,
    _fraction_det3,
    _krawczyk_inclusion,
    _read_artifact,
    _validate_resource_tree,
    build_artifact,
    build_payload,
    verify_artifact,
)


ARTIFACT_PATH = Path("arithmetic_observability_global_design_certificate.json")
PINNED_PAYLOAD_SHA256 = (
    "ef58b99b5a1377878a7b9fd770c6a16fa5961bb46af40d74f0697e7f0454f2ab"
)


def _rehash(artifact: dict[str, object]) -> None:
    artifact["payload_sha256"] = hashlib.sha256(
        _canonical_json(artifact["payload"])
    ).hexdigest()


class GlobalDesignCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.built = build_artifact()

    def test_pinned_artifact_matches_independent_arb_rebuild(self) -> None:
        stored = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.built)
        verified = verify_artifact(stored)
        self.assertTrue(verified["verified"])
        self.assertTrue(verified["overall_passed"])
        self.assertEqual(verified["phase_residual_record_count"], 9)

    def test_rational_good_schedule_and_windings_are_pinned(self) -> None:
        phase = self.built["payload"]["phase_separated_design"]
        self.assertEqual(
            tuple(PHASE_TIMES),
            (
                Fraction(245943, 1000),
                Fraction(140531, 500),
                Fraction(120104, 125),
            ),
        )
        self.assertEqual(
            tuple(PHASE_WINDINGS),
            ((27, 43, 63), (31, 49, 72), (106, 168, 246)),
        )
        self.assertEqual(
            phase["center_times_exact"],
            ["245943/1000", "140531/500", "120104/125"],
        )
        self.assertEqual(phase["windings"], [list(row) for row in PHASE_WINDINGS])
        self.assertEqual(phase["time_perturbation_radius_exact"], "1/1000")
        self.assertEqual(PHASE_TIME_RADIUS, Fraction(1, 1000))

    def test_all_nine_phase_residual_boxes_are_robust(self) -> None:
        phase = self.built["payload"]["phase_separated_design"]
        records = phase["residual_records"]
        self.assertEqual(phase["residual_record_count"], 9)
        self.assertEqual(len(records), 9)
        self.assertEqual(
            {(record["reading_index"], record["axis_index"]) for record in records},
            {(reading, axis) for reading in range(3) for axis in range(3)},
        )
        self.assertEqual(
            [record["phase_role"] for record in records].count("diagonal"), 3
        )
        self.assertEqual(
            [record["phase_role"] for record in records].count("off_diagonal"),
            6,
        )
        self.assertTrue(
            all(
                record["perturbed_residual_certainly_inside_declared_box"]
                for record in records
            )
        )
        self.assertTrue(
            phase[
                "every_residual_certainly_inside_declared_box_throughout_time_box"
            ]
        )
        self.assertTrue(phase["finite_phase_input_verified"])
        self.assertTrue(phase["passed"])

    def test_phase_box_constants_have_exact_types_and_values(self) -> None:
        phase = self.built["payload"]["phase_separated_design"]
        self.assertEqual(PHASE_DIAGONAL_LOWER, Fraction(7, 10))
        self.assertEqual(PHASE_DIAGONAL_UPPER, Fraction(1))
        self.assertEqual(PHASE_OFF_DIAGONAL_RADIUS, Fraction(1, 25))
        self.assertEqual(phase["diagonal_phase_lower_exact"], "7/10")
        self.assertEqual(phase["diagonal_phase_upper_exact"], "1/1")
        self.assertEqual(phase["off_diagonal_absolute_phase_upper_exact"], "1/25")
        self.assertGreater(Fraction(phase["robust_off_diagonal_slack_lower_exact"]), 0)
        self.assertGreater(Fraction(phase["robust_diagonal_lower_slack_exact"]), 0)
        self.assertGreater(Fraction(phase["robust_diagonal_upper_slack_exact"]), 0)

    def test_larger_good_schedule_perturbation_is_a_negative_control(self) -> None:
        with ctx.workprec(FORMAL_PRECISION_BITS):
            negative = _build_phase_design_section(Fraction(1, 100))
        self.assertFalse(negative["passed"])
        self.assertFalse(
            negative[
                "every_residual_certainly_inside_declared_box_throughout_time_box"
            ]
        )

    def test_all_analytic_inequalities_are_directly_certified(self) -> None:
        analytic = self.built["payload"]["analytic_inequalities"]
        self.assertEqual(LEAKAGE_UPPER, Fraction(21, 100))
        self.assertEqual(KAPPA_FLOOR, Fraction(6, 25))
        self.assertEqual(SINE_TWO_LOWER, Fraction(9, 10))
        self.assertEqual(TORUS_WIDTH, Fraction(81, 25))
        self.assertEqual(TORUS_GAP_FLOOR, Fraction(6, 25))
        self.assertTrue(analytic["sine_two_certainly_above_lower"])
        self.assertTrue(analytic["leakage_certainly_below_upper"])
        self.assertTrue(analytic["kappa_certainly_above_floor"])
        self.assertTrue(analytic["torus_width_certainly_below_two_pi"])
        self.assertTrue(analytic["torus_gap_certainly_above_floor"])
        self.assertTrue(analytic["passed"])

    def test_raw_output_product_not_merely_its_factors_is_certified(self) -> None:
        analytic = self.built["payload"]["analytic_inequalities"]
        self.assertEqual(RAW_AND_CHORD_FLOOR, Fraction(2, 15))
        self.assertEqual(
            analytic["raw_output_floor_definition"],
            "sin(2)*2*sin(kappa/2)",
        )
        self.assertTrue(
            analytic[
                "raw_output_floor_certainly_above_distinguishability_floor"
            ]
        )
        self.assertTrue(
            analytic["chord_certainly_above_distinguishability_floor"]
        )

    def test_fixed_schedule_has_a_strict_krawczyk_localization(self) -> None:
        section = self.built["payload"]["reciprocal_collision_krawczyk"][
            "fixed_schedule_root_localization"
        ]
        self.assertEqual(FIXED_ROOT_RADIUS, Fraction(1, 2**280))
        self.assertEqual(section["time_radius_exact"], "0/1")
        self.assertEqual(section["x_radius_exact"], f"1/{2**280}")
        self.assertEqual(section["coordinate_interior_inclusions"], [True] * 3)
        self.assertEqual(FIXED_FUNCTION_ABSOLUTE_CAP, Fraction(1, 10**100))
        self.assertEqual(
            section["function_absolute_value_cap_exact"], f"1/{10**100}"
        )
        self.assertEqual(
            section["function_absolute_value_coordinate_checks"], [True] * 3
        )
        self.assertTrue(
            section["every_function_absolute_value_strictly_below_cap"]
        )
        self.assertNotIn(
            "function_at_x_center_over_time_box_intervals", section
        )
        self.assertTrue(section["krawczyk_image_strictly_inside_x_box"])
        self.assertTrue(
            all(Fraction(value) > 0 for value in section["krawczyk_interior_slacks_exact"])
        )
        self.assertTrue(section["passed"])

    def test_parameterized_bad_chamber_uses_the_pinned_dyadic_box(self) -> None:
        krawczyk = self.built["payload"]["reciprocal_collision_krawczyk"]
        section = krawczyk["uniform_schedule_chamber"]
        self.assertEqual(PARAMETER_X_RADIUS, Fraction(1, 2**14))
        self.assertEqual(PARAMETER_TIME_RADIUS, Fraction(1, 2**24))
        self.assertEqual(section["x_radius_exact"], "1/16384")
        self.assertEqual(section["time_radius_exact"], "1/16777216")
        self.assertEqual(section["time_center_exact"], ["1/1", "2/1", "3/1"])
        self.assertEqual(tuple(COLLISION_TIMES), (Fraction(1), Fraction(2), Fraction(3)))
        self.assertEqual(PARAMETER_FUNCTION_ABSOLUTE_CAP, Fraction(1, 10**4))
        self.assertEqual(section["function_absolute_value_cap_exact"], "1/10000")
        self.assertEqual(
            section["function_absolute_value_coordinate_checks"], [True] * 3
        )
        self.assertTrue(
            section["every_function_absolute_value_strictly_below_cap"]
        )
        self.assertNotIn(
            "function_at_x_center_over_time_box_intervals", section
        )
        self.assertEqual(section["coordinate_interior_inclusions"], [True] * 3)
        self.assertTrue(section["krawczyk_image_strictly_inside_x_box"])
        self.assertTrue(
            all(Fraction(value) > 0 for value in section["krawczyk_interior_slacks_exact"])
        )
        self.assertTrue(section["every_x_box_coordinate_certainly_away_from_zero"])
        self.assertTrue(section["passed"])
        self.assertTrue(krawczyk["parameter_root_sum_certainly_negative"])
        self.assertTrue(krawczyk["finite_krawczyk_inclusions_verified"])

    def test_large_time_box_is_a_krawczyk_negative_control(self) -> None:
        with ctx.workprec(FORMAL_PRECISION_BITS):
            negative = _krawczyk_inclusion(
                PARAMETER_X_RADIUS, Fraction(1, 100_000)
            )
        self.assertFalse(negative["passed"])
        self.assertFalse(negative["krawczyk_image_strictly_inside_x_box"])
        self.assertNotEqual(negative["coordinate_interior_inclusions"], [True] * 3)

    def test_root_center_and_exact_rational_inverse_are_frozen(self) -> None:
        section = self.built["payload"]["reciprocal_collision_krawczyk"]
        self.assertEqual(
            section["root_center_full_decimal_exact"], list(ROOT_CENTER_DECIMALS)
        )
        self.assertEqual(tuple(Fraction(value) for value in ROOT_CENTER_DECIMALS), ROOT_CENTER)
        self.assertLess(ROOT_CENTER[0], 0)
        self.assertLess(ROOT_CENTER[1], 0)
        self.assertGreater(ROOT_CENTER[2], 0)
        determinant = _fraction_det3(APPROXIMATE_INVERSE)
        self.assertNotEqual(determinant, 0)
        self.assertEqual(
            Fraction(section["approximate_inverse_determinant_exact"]), determinant
        )
        self.assertTrue(section["approximate_inverse_nonsingular_exact"])

    def test_formal_scope_separates_finite_evidence_from_theorems(self) -> None:
        scope = self.built["payload"]["formal_scope"]
        self.assertFalse(scope["global_injectivity_theorem_proved_by_certificate"])
        self.assertFalse(scope["phase_separation_theorem_proved_by_certificate"])
        self.assertFalse(scope["krawczyk_theorem_proved_by_certificate"])
        self.assertFalse(scope["reciprocal_identity_proved_by_certificate"])
        self.assertFalse(
            scope["open_chamber_noninjectivity_theorem_proved_by_certificate"]
        )
        self.assertFalse(scope["schedule_optimality_claimed"])
        self.assertFalse(scope["proof_assistant_derivation"])

    def test_payload_is_float_free_and_environment_is_pinned(self) -> None:
        rendered = json.dumps(self.built, sort_keys=True)
        self.assertIsInstance(rendered, str)
        implementation = self.built["payload"]["implementation"]
        self.assertEqual(implementation["arb_precision_bits"], FORMAL_PRECISION_BITS)
        self.assertEqual(implementation["python_flint_version"], flint.__version__)
        self.assertEqual(implementation["flint_version"], flint.__FLINT_VERSION__)
        self.assertEqual(
            implementation["python_flint_version_pin"],
            PINNED_PYTHON_FLINT_VERSION,
        )
        self.assertEqual(implementation["flint_version_pin"], PINNED_FLINT_VERSION)
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
        tampered["payload"]["analytic_inequalities"]["kappa_floor_exact"] = "5/25"
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            verify_artifact(tampered)

    def test_rehashed_semantic_tampering_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["phase_separated_design"][
            "finite_phase_input_verified"
        ] = False
        _rehash(tampered)
        with self.assertRaisesRegex(ValueError, "independent Arb reconstruction"):
            verify_artifact(tampered)

    def test_parameter_and_winding_tampering_is_rejected_before_rebuild(self) -> None:
        parameter = copy.deepcopy(self.built)
        parameter["payload"]["parameters"]["phase_times_exact"][0] = "245944/1001"
        _rehash(parameter)
        with self.assertRaisesRegex(ValueError, "noncanonical phase schedule"):
            verify_artifact(parameter)

        winding = copy.deepcopy(self.built)
        winding["payload"]["phase_separated_design"]["windings"][0][0] = 28
        _rehash(winding)
        with self.assertRaisesRegex(ValueError, "noncanonical phase windings"):
            verify_artifact(winding)

    def test_root_and_inverse_tampering_is_rejected_before_rebuild(self) -> None:
        root = copy.deepcopy(self.built)
        root["payload"]["reciprocal_collision_krawczyk"][
            "root_center_full_decimal_exact"
        ][0] = ROOT_CENTER_DECIMALS[0] + "0"
        _rehash(root)
        with self.assertRaisesRegex(ValueError, "noncanonical root center"):
            verify_artifact(root)

        inverse = copy.deepcopy(self.built)
        inverse["payload"]["reciprocal_collision_krawczyk"][
            "approximate_inverse_fraction_exact"
        ][0][0] = "1/1"
        _rehash(inverse)
        with self.assertRaisesRegex(ValueError, "noncanonical approximate inverse"):
            verify_artifact(inverse)

    def test_rehashed_false_interval_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["reciprocal_collision_krawczyk"][
            "uniform_schedule_chamber"
        ]["krawczyk_centered_intervals"][0] = "[0 +/- 0]"
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

    def test_nonreduced_fraction_alias_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["parameters"]["phase_diagonal_upper_exact"] = "2/2"
        _rehash(tampered)
        with self.assertRaisesRegex(ValueError, "not reduced and canonical"):
            verify_artifact(tampered)

    def test_unknown_fields_and_wrong_schema_are_rejected(self) -> None:
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

    def test_noncanonical_json_whitespace_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "compact.json"
            path.write_text(json.dumps(self.built, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "canonical deterministic JSON"):
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
        for _ in range(22):
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

    def test_cli_write_and_verify_are_byte_deterministic(self) -> None:
        root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rebuilt.json"
            subprocess.run(
                [
                    sys.executable,
                    str(root / "arithmetic_observability_global_design.py"),
                    "--write",
                    str(path),
                    "--compact",
                ],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(path.read_bytes(), ARTIFACT_PATH.read_bytes())
            self.assertNotIn(b"\r\n", path.read_bytes())
            verified = subprocess.run(
                [
                    sys.executable,
                    str(root / "arithmetic_observability_global_design.py"),
                    "--verify",
                    str(path),
                    "--compact",
                ],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn('"verified":true', verified.stdout)


if __name__ == "__main__":
    unittest.main()
