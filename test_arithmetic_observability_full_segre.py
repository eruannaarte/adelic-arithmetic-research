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

from arithmetic_observability_full_segre import (
    AXIS_COUNT,
    FACTOR_FLOOR,
    FORMAL_PRECISION_BITS,
    MAX_ARTIFACT_BYTES,
    OFF_AXIS_ERROR_RADIUS,
    QUOTIENT_FLOOR,
    RHO_AMPLIFICATION_UPPER,
    EPSILON_AMPLIFICATION_UPPER,
    PINNED_FLINT_VERSION,
    PINNED_PYTHON_FLINT_VERSION,
    PRIMES,
    READING_COUNT,
    SCHEMA,
    TARGET_AXES,
    TARGET_ERROR_RADIUS,
    TARGET_PI_MULTIPLIERS,
    TENSOR_FLOOR,
    TIMES,
    WINDINGS,
    _canonical_json,
    _load_strict_artifact,
    _pretty_json,
    build_artifact,
    verify_artifact,
)


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "arithmetic_observability_full_segre.py"
CERTIFICATE = ROOT / "arithmetic_observability_full_segre_certificate.json"


class FullSegreCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.built = build_artifact()
        cls.checked_in = json.loads(CERTIFICATE.read_text(encoding="utf-8"))

    def _write_bytes(self, raw: bytes) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "artifact.json"
        path.write_bytes(raw)
        return path

    def _write_artifact(self, artifact: dict[str, object]) -> Path:
        return self._write_bytes(_pretty_json(artifact))

    def _refresh_digest(self, artifact: dict[str, object]) -> None:
        artifact["payload_sha256"] = hashlib.sha256(
            _canonical_json(artifact["payload"])
        ).hexdigest()

    def _semantic_mutation(self) -> dict[str, object]:
        return copy.deepcopy(self.built)

    def test_checked_in_artifact_is_exact_reconstruction(self) -> None:
        self.assertEqual(
            _canonical_json(self.checked_in), _canonical_json(self.built)
        )
        result = verify_artifact(CERTIFICATE)
        self.assertTrue(result["verified"])
        self.assertEqual(result["schema"], SCHEMA)
        self.assertEqual(result["phase_record_count"], 18)

    def test_schedule_windings_and_targets_are_pinned(self) -> None:
        parameters = self.built["payload"]["parameters"]
        self.assertEqual(
            parameters["times_exact"],
            [f"{value.numerator}/{value.denominator}" for value in TIMES],
        )
        self.assertEqual(parameters["windings"], [list(row) for row in WINDINGS])
        self.assertEqual(parameters["target_axes"], list(TARGET_AXES))
        self.assertEqual(
            parameters["target_pi_multipliers_exact"],
            [
                f"{value.numerator}/{value.denominator}"
                for value in TARGET_PI_MULTIPLIERS
            ],
        )
        self.assertEqual(WINDINGS[3][1], 16537)
        self.assertEqual(TARGET_PI_MULTIPLIERS[3], Fraction(1))

    def test_all_eighteen_phase_inclusions_are_strict(self) -> None:
        phase = self.built["payload"]["phase_design"]
        records = phase["records"]
        self.assertEqual(len(records), READING_COUNT * AXIS_COUNT)
        self.assertEqual(
            sum(record["phase_role"] == "target" for record in records),
            READING_COUNT,
        )
        self.assertEqual(
            sum(record["phase_role"] == "off_axis" for record in records),
            READING_COUNT * (AXIS_COUNT - 1),
        )
        self.assertTrue(
            all(record["error_certainly_below_declared_tolerance"] for record in records)
        )
        self.assertGreater(Fraction(phase["target_error_slack_lower_exact"]), 0)
        self.assertGreater(Fraction(phase["off_axis_error_slack_lower_exact"]), 0)
        self.assertLess(
            Fraction(phase["maximum_target_absolute_error_upper_endpoint_exact"]),
            TARGET_ERROR_RADIUS,
        )
        self.assertLess(
            Fraction(phase["maximum_off_axis_absolute_error_upper_endpoint_exact"]),
            OFF_AXIS_ERROR_RADIUS,
        )
        self.assertIn("pi_interval", phase)
        self.assertEqual(
            [record["prime"] for record in phase["logarithm_records"]],
            list(PRIMES),
        )
        self.assertTrue(
            all("logarithm_interval" in record for record in phase["logarithm_records"])
        )

    def test_phase_records_have_canonical_indices_and_primes(self) -> None:
        records = self.built["payload"]["phase_design"]["records"]
        for index, record in enumerate(records):
            reading, axis = divmod(index, AXIS_COUNT)
            self.assertEqual(record["reading_index"], reading)
            self.assertEqual(record["axis_index"], axis)
            self.assertEqual(record["prime"], PRIMES[axis])
            self.assertEqual(record["winding"], WINDINGS[reading][axis])

    def test_algebraic_floors_have_strict_margins(self) -> None:
        analytic = self.built["payload"]["analytic_inequalities"]
        self.assertEqual(analytic["perturbation_definition"], "E=9*sqrt(1202)/500")
        self.assertEqual(analytic["factor_floor_exact"], "7901/10000")
        self.assertEqual(analytic["tensor_floor_exact"], "4561/10000")
        self.assertEqual(analytic["quotient_floor_exact"], "291/12500")
        self.assertEqual(analytic["rho_amplification_upper_exact"], "8591/100")
        self.assertEqual(analytic["epsilon_amplification_upper_exact"], "877/200")
        self.assertEqual(
            analytic["rho_amplification_definition"],
            "2/((sqrt(2)-E)/(24*sqrt(2)))",
        )
        self.assertEqual(
            analytic["epsilon_amplification_definition"],
            "2/((sqrt(2)-E)/sqrt(3))",
        )
        self.assertTrue(analytic["perturbation_certainly_below_upper"])
        self.assertTrue(analytic["factor_floor_certainly_above_declared_floor"])
        self.assertTrue(analytic["tensor_floor_certainly_above_declared_floor"])
        self.assertTrue(analytic["quotient_floor_certainly_above_declared_floor"])
        self.assertTrue(
            analytic["rho_amplification_certainly_below_declared_upper"]
        )
        self.assertTrue(
            analytic["epsilon_amplification_certainly_below_declared_upper"]
        )
        self.assertEqual(analytic["raw_operator_norm_definition"], "8*sqrt(6)")
        self.assertEqual(analytic["raw_operator_norm_upper_exact"], "20/1")
        self.assertTrue(
            analytic["raw_operator_norm_certainly_below_declared_upper"]
        )
        self.assertEqual(FACTOR_FLOOR, Fraction(7901, 10000))
        self.assertEqual(TENSOR_FLOOR, Fraction(4561, 10000))
        self.assertEqual(QUOTIENT_FLOOR, Fraction(291, 12500))
        self.assertEqual(RHO_AMPLIFICATION_UPPER, Fraction(8591, 100))
        self.assertEqual(EPSILON_AMPLIFICATION_UPPER, Fraction(877, 200))

    def test_formal_scope_does_not_mechanize_general_theorems(self) -> None:
        scope = self.built["payload"]["scope"]
        self.assertFalse(scope["full_segre_global_reconstruction_theorem_mechanized"])
        self.assertFalse(scope["full_segre_reading_lower_bound_mechanized"])
        self.assertFalse(scope["schedule_optimality_claimed"])

    def test_formal_environment_is_pinned(self) -> None:
        environment = self.built["payload"]["formal_environment"]
        self.assertEqual(environment["precision_bits"], FORMAL_PRECISION_BITS)
        self.assertEqual(
            environment["python_flint_version"], PINNED_PYTHON_FLINT_VERSION
        )
        self.assertEqual(environment["flint_version"], PINNED_FLINT_VERSION)

    def test_reproduction_file_hashes_bind_the_package(self) -> None:
        reproduction = self.built["payload"]["reproduction_files"]
        for basename_key, digest_key in (
            ("manuscript_basename", "manuscript_sha256"),
            ("verifier_basename", "verifier_sha256"),
            ("tests_basename", "tests_sha256"),
        ):
            path = ROOT / reproduction[basename_key]
            self.assertTrue(path.is_file())
            self.assertEqual(
                reproduction[digest_key], hashlib.sha256(path.read_bytes()).hexdigest()
            )

    def test_write_is_byte_identical(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        output = Path(directory.name) / "regenerated.json"
        subprocess.run(
            [sys.executable, str(SCRIPT), "--write", str(output)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(output.read_bytes(), CERTIFICATE.read_bytes())

    def test_cli_verify_succeeds(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--verify", str(CERTIFICATE)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertTrue(result["verified"])
        self.assertEqual(result["off_axis_record_count"], 12)

    def test_payload_tamper_without_digest_refresh_is_rejected(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload"]["finite_certificate_passed"] = False
        with self.assertRaisesRegex(ValueError, "payload digest mismatch"):
            verify_artifact(self._write_artifact(artifact))

    def test_time_tamper_with_refreshed_digest_is_rejected(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload"]["parameters"]["times_exact"][0] = "90540693/1000"
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "noncanonical schedule"):
            verify_artifact(self._write_artifact(artifact))

    def test_winding_tamper_with_refreshed_digest_is_rejected(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload"]["parameters"]["windings"][3][1] = 16538
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "noncanonical phase windings"):
            verify_artifact(self._write_artifact(artifact))

    def test_target_axis_tamper_with_refreshed_digest_is_rejected(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload"]["parameters"]["target_axes"][0] = 1
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "noncanonical target axes"):
            verify_artifact(self._write_artifact(artifact))

    def test_nonreduced_fraction_alias_is_rejected(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload"]["parameters"]["target_error_radius_exact"] = "2/2000"
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "not reduced and canonical"):
            verify_artifact(self._write_artifact(artifact))

    def test_analytic_floor_tamper_is_rejected(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload"]["analytic_inequalities"]["factor_floor_exact"] = "4/5"
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "noncanonical factor_floor_exact"):
            verify_artifact(self._write_artifact(artifact))

    def test_recomputed_interval_tamper_is_rejected(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload"]["analytic_inequalities"]["factor_floor_interval"] = "[1 +/- 0]"
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "differs from exact reconstruction"):
            verify_artifact(self._write_artifact(artifact))

    def test_reproduction_hash_tamper_is_rejected(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload"]["reproduction_files"]["tests_sha256"] = "0" * 64
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "reproduction-file hashes"):
            verify_artifact(self._write_artifact(artifact))

    def test_unexpected_top_level_field_is_rejected(self) -> None:
        artifact = self._semantic_mutation()
        artifact["extra"] = None
        with self.assertRaisesRegex(ValueError, "unexpected top-level fields"):
            verify_artifact(self._write_artifact(artifact))

    def test_duplicate_json_key_is_rejected(self) -> None:
        raw = CERTIFICATE.read_bytes()
        raw = raw.replace(b'  "schema":', b'  "schema": "duplicate",\n  "schema":', 1)
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            verify_artifact(self._write_bytes(raw))

    def test_json_float_alias_is_rejected(self) -> None:
        raw = CERTIFICATE.read_bytes().replace(
            b'"axis_count": 3', b'"axis_count": 3.0', 1
        )
        with self.assertRaisesRegex(ValueError, "forbidden JSON floating-point"):
            verify_artifact(self._write_bytes(raw))

    def test_boolean_integer_alias_is_rejected(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload"]["parameters"]["axis_count"] = True
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "noncanonical axis_count"):
            verify_artifact(self._write_artifact(artifact))

    def test_negative_zero_integer_is_rejected(self) -> None:
        raw = CERTIFICATE.read_bytes().replace(
            b'"axis_count": 3', b'"axis_count": -0', 1
        )
        with self.assertRaisesRegex(ValueError, "negative-zero"):
            verify_artifact(self._write_bytes(raw))

    def test_nonfinite_json_constant_is_rejected(self) -> None:
        raw = CERTIFICATE.read_bytes().replace(
            b'"axis_count": 3', b'"axis_count": NaN', 1
        )
        with self.assertRaisesRegex(ValueError, "forbidden nonfinite"):
            verify_artifact(self._write_bytes(raw))

    def test_crlf_and_bom_are_rejected(self) -> None:
        raw = CERTIFICATE.read_bytes()
        with self.assertRaisesRegex(ValueError, "LF line endings"):
            verify_artifact(self._write_bytes(raw.replace(b"\n", b"\r\n")))
        with self.assertRaisesRegex(ValueError, "UTF-8 BOM"):
            verify_artifact(self._write_bytes(b"\xef\xbb\xbf" + raw))

    def test_final_newline_is_strict(self) -> None:
        raw = CERTIFICATE.read_bytes()
        with self.assertRaisesRegex(ValueError, "exactly one LF"):
            verify_artifact(self._write_bytes(raw[:-1]))
        with self.assertRaisesRegex(ValueError, "exactly one LF"):
            verify_artifact(self._write_bytes(raw + b"\n"))

    def test_noncanonical_json_whitespace_is_rejected(self) -> None:
        artifact = self._semantic_mutation()
        raw = json.dumps(artifact, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        with self.assertRaisesRegex(ValueError, "canonical deterministic JSON"):
            verify_artifact(self._write_bytes(raw))

    def test_text_and_list_resource_caps_are_enforced(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload"]["oversized_text"] = "x" * 4097
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "text violates the resource cap"):
            verify_artifact(self._write_artifact(artifact))
        artifact = self._semantic_mutation()
        artifact["payload"]["oversized_list"] = [None] * 257
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "list violates the resource cap"):
            verify_artifact(self._write_artifact(artifact))

    def test_oversized_artifact_is_rejected(self) -> None:
        oversized = b" " * (MAX_ARTIFACT_BYTES + 1)
        with self.assertRaisesRegex(ValueError, "byte resource cap"):
            verify_artifact(self._write_bytes(oversized))

    def test_artifact_loader_uses_a_bounded_read(self) -> None:
        calls: list[object] = []

        class GuardedReader:
            def __enter__(self) -> "GuardedReader":
                return self

            def __exit__(self, *args: object) -> None:
                return None

            def read(self, size: int = -1) -> bytes:
                calls.append(size)
                if size != MAX_ARTIFACT_BYTES + 1:
                    raise AssertionError("artifact reader was not bounded")
                return b" " * size

        class GuardedPath:
            def open(self, mode: str) -> GuardedReader:
                calls.append(mode)
                return GuardedReader()

        with self.assertRaisesRegex(ValueError, "byte resource cap"):
            _load_strict_artifact(GuardedPath())  # type: ignore[arg-type]
        self.assertEqual(calls, ["rb", MAX_ARTIFACT_BYTES + 1])

    def test_json_depth_cap_is_enforced(self) -> None:
        artifact = self._semantic_mutation()
        nested: dict[str, object] = {}
        cursor = nested
        for _ in range(22):
            child: dict[str, object] = {}
            cursor["x"] = child
            cursor = child
        artifact["payload"]["nested"] = nested
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "maximum JSON depth"):
            verify_artifact(self._write_artifact(artifact))

    def test_precision_resource_cap_is_enforced(self) -> None:
        with self.assertRaisesRegex(ValueError, "bounded canonical integer"):
            build_artifact(255)
        with self.assertRaisesRegex(ValueError, "bounded canonical integer"):
            build_artifact(1025)
        with self.assertRaisesRegex(ValueError, "bounded canonical integer"):
            build_artifact(True)


if __name__ == "__main__":
    unittest.main()
