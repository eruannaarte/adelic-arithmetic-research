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

from arithmetic_observability_discrete_queries import (
    ALL_COORDINATE_GAIN_CEILING,
    ALL_COORDINATE_GAIN_FLOOR,
    ANCHORS,
    COLLISION_COORDINATE_BOUND,
    CORE_VERTEX_NORMS,
    EXPECTED_SOURCE_FILE_SHA256,
    EXPECTED_SOURCE_FORMAL_SHA256,
    FORMAL_PRECISION_BITS,
    MAX_ARTIFACT_BYTES,
    MAX_SOURCE_BYTES,
    PINNED_FLINT_VERSION,
    PINNED_PYTHON_FLINT_VERSION,
    SCHEMA,
    SCHUR_GAIN_CEILING,
    SCHUR_GAIN_FLOOR,
    SINGULAR_VALUE_FLOOR,
    TAIL_MODES,
    TAIL_WEIGHTS,
    TIMES,
    _canonical_json,
    _factor_integer,
    _generalized_divisor_count,
    _load_strict_artifact,
    _outside_prime_box,
    _pretty_json,
    _read_source,
    build_artifact,
    verify_artifact,
)


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "arithmetic_observability_discrete_queries.py"
CERTIFICATE = ROOT / "arithmetic_observability_discrete_queries_certificate.json"
SOURCE = ROOT / "certificates" / "arithmetic_sensing_v_multiscale_end_to_end.json"


class DiscreteQueryCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.built = build_artifact()
        cls.checked_in = json.loads(CERTIFICATE.read_text(encoding="utf-8"))

    def _write_bytes(self, raw: bytes, basename: str = "artifact.json") -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / basename
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
        self.assertEqual(result["anchor_count"], 4)
        self.assertEqual(result["tail_mode_count"], 6)

    def test_source_file_and_formal_payload_are_pinned(self) -> None:
        section = self.built["payload"]["localized_integer_queries"]["source"]
        self.assertEqual(section["file_sha256"], EXPECTED_SOURCE_FILE_SHA256)
        self.assertEqual(
            section["formal_certificate_sha256"],
            EXPECTED_SOURCE_FORMAL_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            EXPECTED_SOURCE_FILE_SHA256,
        )

    def test_localized_neumann_formulas_are_exact(self) -> None:
        localized = self.built["payload"]["localized_integer_queries"]
        q = Fraction(localized["global_gram_row_upper_exact"])
        tau = Fraction(localized["global_complete_tail_upper_exact"])
        records = localized["anchor_records"]
        self.assertEqual([record["anchor"] for record in records], list(ANCHORS))
        for record in records:
            n = record["anchor"]
            tau_n = Fraction(record["complete_tail_upper_exact"])
            q_n = Fraction(record["gram_row_upper_exact"])
            bound = n * n * (tau_n + q_n * tau / (1 - q))
            margin = Fraction(1, 2) - bound
            conservative = margin * margin * (1 - q) / n**4
            schur_factor = (1 - q - q_n * q_n) / (1 - q)
            certified_bar_kappa_squared = n**4 / schur_factor
            schur = margin * margin * schur_factor / n**4
            self.assertEqual(
                Fraction(record["localized_coefficient_bound_exact"]), bound
            )
            self.assertEqual(Fraction(record["rounding_margin_exact"]), margin)
            self.assertEqual(
                Fraction(record["sufficient_noise_radius_squared_exact"]),
                conservative,
            )
            self.assertEqual(Fraction(record["schur_factor_exact"]), schur_factor)
            self.assertGreater(Fraction(record["schur_numerator_exact"]), 0)
            self.assertTrue(record["schur_numerator_certainly_positive"])
            self.assertEqual(
                Fraction(record["certified_bar_kappa_squared_exact"]),
                certified_bar_kappa_squared,
            )
            self.assertEqual(
                Fraction(record["schur_sufficient_noise_radius_squared_exact"]),
                schur,
            )
            self.assertGreater(1 - q - q_n * q_n, 0)
            self.assertGreater(schur, conservative)
            self.assertEqual(
                Fraction(
                    record[
                        "anisotropic_unit_separation_weight_squared_lower_exact"
                    ]
                ),
                4 * schur,
            )

    def test_frozen_localized_bounds_match_independent_decimals(self) -> None:
        records = self.built["payload"]["localized_integer_queries"][
            "anchor_records"
        ]
        expected_bounds = (
            0.0005413328049489775,
            0.0015462579530286659,
            0.003024321925803098,
            0.007064832945650593,
        )
        expected_conservative = (
            0.4992698983160089,
            0.12456633824408053,
            0.05519864973703505,
            0.01970995454849109,
        )
        expected_schur = (
            0.4994586671950448,
            0.12461343551173978,
            0.055219519786019924,
            0.019717406682172978,
        )
        for record, bound, conservative, schur in zip(
            records, expected_bounds, expected_conservative, expected_schur
        ):
            self.assertAlmostEqual(
                float(Fraction(record["localized_coefficient_bound_exact"])),
                bound,
                places=18,
            )
            self.assertAlmostEqual(
                float(
                    Fraction(record["sufficient_noise_radius_squared_exact"])
                )
                ** 0.5,
                conservative,
                places=15,
            )
            self.assertAlmostEqual(
                float(
                    Fraction(
                        record["schur_sufficient_noise_radius_squared_exact"]
                    )
                )
                ** 0.5,
                schur,
                places=15,
            )

    def test_n5_is_the_unique_exact_bottleneck(self) -> None:
        localized = self.built["payload"]["localized_integer_queries"]
        self.assertEqual(localized["unique_bottleneck_anchor"], 5)
        self.assertEqual(localized["unique_schur_bottleneck_anchor"], 5)
        records = localized["anchor_records"]
        conservative = [
            Fraction(record["sufficient_noise_radius_squared_exact"])
            for record in records
        ]
        schur = [
            Fraction(record["schur_sufficient_noise_radius_squared_exact"])
            for record in records
        ]
        self.assertEqual(conservative[-1], min(conservative))
        self.assertEqual(schur[-1], min(schur))
        self.assertEqual(len(set(conservative)), len(conservative))
        self.assertEqual(len(set(schur)), len(schur))

    def test_n5_upper_obstruction_gives_near_sharp_bracket(self) -> None:
        localized = self.built["payload"]["localized_integer_queries"]
        upper = localized["query_upper_obstruction"]
        lower_squared = Fraction(localized["schur_bottleneck_radius_squared_exact"])
        self.assertEqual(upper["anchor"], 5)
        self.assertIn("full AS-V coefficient-envelope", upper["model"])
        self.assertIn("not the smaller", upper["model"])
        self.assertEqual(
            Fraction(upper["inter_fibre_distance_upper_exact"]), Fraction(1, 25)
        )
        self.assertEqual(
            Fraction(upper["robust_noise_radius_upper_exact"]), Fraction(1, 50)
        )
        self.assertEqual(
            Fraction(upper["robust_noise_radius_upper_squared_exact"]),
            Fraction(1, 2500),
        )
        self.assertLess(lower_squared, Fraction(1, 2500))
        self.assertTrue(upper["schur_sufficient_lower_strictly_below_upper"])
        self.assertIn("not an exact minimax", upper["status"])

    def test_localized_gain_brackets_are_strict(self) -> None:
        localized = self.built["payload"]["localized_integer_queries"]
        conservative_gain_squared = Fraction(
            localized["localized_to_all_fifty_gain_squared_exact"]
        )
        schur_gain_squared = Fraction(
            localized["schur_localized_to_all_fifty_gain_squared_exact"]
        )
        self.assertGreater(
            conservative_gain_squared, ALL_COORDINATE_GAIN_FLOOR**2
        )
        self.assertLess(
            conservative_gain_squared, ALL_COORDINATE_GAIN_CEILING**2
        )
        self.assertGreater(schur_gain_squared, SCHUR_GAIN_FLOOR**2)
        self.assertLess(schur_gain_squared, SCHUR_GAIN_CEILING**2)
        self.assertTrue(localized["gain_lower_inequality_verified"])
        self.assertTrue(localized["gain_upper_inequality_verified"])
        self.assertTrue(localized["schur_gain_lower_inequality_verified"])
        self.assertTrue(localized["schur_gain_upper_inequality_verified"])

    def test_tail_modes_have_exact_d14_weights_and_lie_off_box(self) -> None:
        section = self.built["payload"]["continuous_tail_obstruction"]
        records = section["mode_records"]
        self.assertEqual([record["mode"] for record in records], list(TAIL_MODES))
        for record, mode, weight in zip(records, TAIL_MODES, TAIL_WEIGHTS):
            factors = _factor_integer(mode)
            divisor_count = _generalized_divisor_count(mode, 14)
            self.assertEqual(record["d14_exact"], divisor_count)
            self.assertEqual(Fraction(record["weight_exact"]), weight)
            self.assertEqual(weight, Fraction(divisor_count, mode * mode))
            self.assertTrue(_outside_prime_box(factors))
            self.assertTrue(record["outside_core_prime_box"])

    def test_continuous_response_matrix_and_sylvester_witness(self) -> None:
        section = self.built["payload"]["continuous_tail_obstruction"]
        matrix = section["response_matrix_intervals"]
        self.assertEqual(len(matrix), 6)
        self.assertTrue(all(len(row) == 6 for row in matrix))
        minors = section["leading_principal_minor_records"]
        self.assertEqual([record["order"] for record in minors], list(range(1, 7)))
        self.assertTrue(all(record["certainly_positive"] for record in minors))
        self.assertTrue(
            all(
                Fraction(record["determinant_lower_endpoint_exact"]) > 0
                for record in minors
            )
        )
        self.assertTrue(section["sylvester_positive_definite_verified"])
        self.assertEqual(
            Fraction(section["smallest_singular_value_certainly_above_exact"]),
            SINGULAR_VALUE_FLOOR,
        )

    def test_core_diameter_is_strictly_inside_tail_ball(self) -> None:
        section = self.built["payload"]["continuous_tail_obstruction"]
        self.assertEqual(section["diameter_chain"], "2*sqrt(3)<7/2<5")
        self.assertTrue(section["diameter_chain_verified"])
        self.assertEqual(
            Fraction(section["normalized_core_reading_diameter_rational_upper_exact"]),
            Fraction(7, 2),
        )

    def test_explicit_collision_correction_is_strictly_interior(self) -> None:
        collision = self.built["payload"]["continuous_tail_obstruction"][
            "explicit_collision"
        ]
        self.assertEqual(collision["core_vertex_norms"], list(CORE_VERTEX_NORMS))
        self.assertEqual(collision["core_vertex_exponents"], [[0, 0, 0], [3, 3, 3]])
        self.assertEqual(collision["queried_p1_values_exact"], ["1/1", "0/1"])
        self.assertFalse(collision["queried_p1_is_fixed"])
        self.assertEqual(collision["certified_sign_pattern"], [-1, 1, 1, 1, -1, 1])
        self.assertTrue(
            collision["all_correction_coordinates_strictly_inside_envelope"]
        )
        records = collision["correction_records"]
        self.assertEqual([record["mode"] for record in records], list(TAIL_MODES))
        self.assertTrue(
            all(
                Fraction(record["absolute_upper_endpoint_exact"])
                < COLLISION_COORDINATE_BOUND
                for record in records
            )
        )
        self.assertTrue(
            all(record["absolute_value_certainly_below_one_third"] for record in records)
        )
        self.assertTrue(
            all(record["contains_zero"] for record in collision["enclosed_solve_residual_records"])
        )

    def test_scope_distinguishes_query_integrality_from_tail_relaxation(self) -> None:
        payload = self.built["payload"]
        scope = payload["formal_scope"]
        consequence = payload["localized_integer_queries"]["formal_consequence"]
        self.assertFalse(scope["integer_tail_model_replaced_by_continuous_tail"])
        self.assertFalse(scope["tail_integrality_required"])
        self.assertIn("only the queried", scope["positive_integrality_assumption"])
        self.assertTrue(scope["continuous_tail_claim_is_a_separate_relaxation"])
        self.assertTrue(
            scope[
                "local_vanishing_radius_obstruction_requires_interval_valued_query"
            ]
        )
        self.assertFalse(
            scope[
                "explicit_full_envelope_collision_requires_interval_valued_query"
            ]
        )
        self.assertTrue(
            scope[
                "explicit_full_envelope_collision_allows_unit_spaced_query_values"
            ]
        )
        self.assertTrue(scope["continuous_obstruction_does_not_fix_a1"])
        self.assertFalse(scope["exact_minimax_radius_claimed"])
        self.assertIn("sufficient", scope["all_fifty_comparison_status"])
        self.assertTrue(consequence["queried_prefix_unit_spacing_required"])
        self.assertFalse(consequence["literal_integrality_required"])
        self.assertFalse(consequence["nonquery_prefix_integrality_required"])
        self.assertFalse(consequence["tail_integrality_required"])
        self.assertIn("continuous", consequence["tail_requirement"])

    def test_environment_and_reproduction_hashes_are_pinned(self) -> None:
        payload = self.built["payload"]
        environment = payload["formal_environment"]
        self.assertEqual(environment["precision_bits"], FORMAL_PRECISION_BITS)
        self.assertEqual(
            environment["python_flint_version"], PINNED_PYTHON_FLINT_VERSION
        )
        self.assertEqual(environment["flint_version"], PINNED_FLINT_VERSION)
        reproduction = payload["reproduction_files"]
        self.assertEqual(
            reproduction["verifier_sha256"], hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
        )
        self.assertEqual(
            reproduction["tests_sha256"], hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        )

    def test_cli_write_and_verify_are_deterministic(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        output = Path(directory.name) / "certificate.json"
        write = subprocess.run(
            [sys.executable, str(SCRIPT), "--write", str(output)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(write.returncode, 0, write.stderr)
        self.assertEqual(output.read_bytes(), CERTIFICATE.read_bytes())
        verify = subprocess.run(
            [sys.executable, str(SCRIPT), "--verify", str(output)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(verify.returncode, 0, verify.stderr)
        result = json.loads(verify.stdout)
        self.assertTrue(result["verified"])
        self.assertEqual(result["unique_bottleneck_anchor"], 5)

    def test_cli_rejects_mutually_exclusive_actions(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--write",
                "unused.json",
                "--verify",
                str(CERTIFICATE),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mutually exclusive", result.stderr)

    def test_source_digest_tampering_is_rejected(self) -> None:
        raw = SOURCE.read_bytes()
        index = raw.find(b'"degree": 14')
        self.assertGreaterEqual(index, 0)
        mutated = raw[:index] + raw[index:].replace(b'"degree": 14', b'"degree": 15', 1)
        path = self._write_bytes(mutated, SOURCE.name)
        with self.assertRaisesRegex(ValueError, "source certificate file digest mismatch"):
            build_artifact(path)

    def test_payload_digest_tampering_is_rejected(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload"]["parameters"]["source_degree"] = 15
        with self.assertRaisesRegex(ValueError, "payload digest mismatch"):
            verify_artifact(self._write_artifact(artifact))

    def test_semantic_tampering_with_refreshed_digest_is_rejected(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload"]["parameters"]["source_degree"] = 15
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "noncanonical source_degree"):
            verify_artifact(self._write_artifact(artifact))

    def test_tail_weight_tampering_with_refreshed_digest_is_rejected(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload"]["continuous_tail_obstruction"]["mode_records"][0][
            "weight_exact"
        ] = "1/1"
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "tail weight is noncanonical"):
            verify_artifact(self._write_artifact(artifact))

    def test_schema_and_top_level_fields_are_strict(self) -> None:
        artifact = self._semantic_mutation()
        artifact["schema"] = "wrong"
        with self.assertRaisesRegex(ValueError, "schema is not canonical"):
            verify_artifact(self._write_artifact(artifact))
        artifact = self._semantic_mutation()
        artifact["extra"] = None
        with self.assertRaisesRegex(ValueError, "unexpected top-level fields"):
            verify_artifact(self._write_artifact(artifact))

    def test_digest_shape_is_strict(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload_sha256"] = "A" * 64
        with self.assertRaisesRegex(ValueError, "canonical lowercase SHA-256"):
            verify_artifact(self._write_artifact(artifact))

    def test_noncanonical_fraction_is_rejected(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload"]["continuous_tail_obstruction"]["times_exact"][0] = "491886/2000"
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "not reduced and canonical"):
            verify_artifact(self._write_artifact(artifact))

    def test_duplicate_json_key_is_rejected(self) -> None:
        raw = CERTIFICATE.read_bytes().replace(
            b'  "schema":', b'  "schema": "duplicate",\n  "schema":', 1
        )
        with self.assertRaisesRegex(ValueError, "duplicate key"):
            verify_artifact(self._write_bytes(raw))

    def test_json_float_alias_is_rejected(self) -> None:
        raw = CERTIFICATE.read_bytes().replace(
            b'"reading_count": 3', b'"reading_count": 3.0', 1
        )
        with self.assertRaisesRegex(ValueError, "forbidden JSON floating-point"):
            verify_artifact(self._write_bytes(raw))

    def test_boolean_integer_alias_is_rejected(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload"]["parameters"]["reading_count"] = True
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "noncanonical reading_count"):
            verify_artifact(self._write_artifact(artifact))

    def test_negative_zero_and_nonfinite_are_rejected(self) -> None:
        raw = CERTIFICATE.read_bytes().replace(
            b'"reading_count": 3', b'"reading_count": -0', 1
        )
        with self.assertRaisesRegex(ValueError, "negative-zero"):
            verify_artifact(self._write_bytes(raw))
        raw = CERTIFICATE.read_bytes().replace(
            b'"reading_count": 3', b'"reading_count": NaN', 1
        )
        with self.assertRaisesRegex(ValueError, "forbidden nonfinite"):
            verify_artifact(self._write_bytes(raw))

    def test_crlf_bom_and_final_newline_are_rejected(self) -> None:
        raw = CERTIFICATE.read_bytes()
        with self.assertRaisesRegex(ValueError, "LF line endings"):
            verify_artifact(self._write_bytes(raw.replace(b"\n", b"\r\n")))
        with self.assertRaisesRegex(ValueError, "UTF-8 BOM"):
            verify_artifact(self._write_bytes(b"\xef\xbb\xbf" + raw))
        with self.assertRaisesRegex(ValueError, "exactly one LF"):
            verify_artifact(self._write_bytes(raw[:-1]))
        with self.assertRaisesRegex(ValueError, "exactly one LF"):
            verify_artifact(self._write_bytes(raw + b"\n"))

    def test_noncanonical_json_whitespace_is_rejected(self) -> None:
        raw = json.dumps(
            self.built, sort_keys=True, separators=(",", ":")
        ).encode("utf-8") + b"\n"
        with self.assertRaisesRegex(ValueError, "canonical deterministic JSON"):
            verify_artifact(self._write_bytes(raw))

    def test_text_list_and_artifact_resource_caps_are_enforced(self) -> None:
        artifact = self._semantic_mutation()
        artifact["payload"]["oversized_text"] = "x" * 8193
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "text violates the resource cap"):
            verify_artifact(self._write_artifact(artifact))
        artifact = self._semantic_mutation()
        artifact["payload"]["oversized_list"] = [None] * 513
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "list violates the resource cap"):
            verify_artifact(self._write_artifact(artifact))
        with self.assertRaisesRegex(ValueError, "byte resource cap"):
            verify_artifact(self._write_bytes(b" " * (MAX_ARTIFACT_BYTES + 1)))

    def test_artifact_and_source_loaders_use_bounded_reads(self) -> None:
        artifact_calls: list[object] = []

        class ArtifactReader:
            def __enter__(self) -> "ArtifactReader":
                return self

            def __exit__(self, *args: object) -> None:
                return None

            def read(self, size: int = -1) -> bytes:
                artifact_calls.append(size)
                return b" " * size

        class ArtifactPath:
            def open(self, mode: str) -> ArtifactReader:
                artifact_calls.append(mode)
                return ArtifactReader()

        with self.assertRaisesRegex(ValueError, "byte resource cap"):
            _load_strict_artifact(ArtifactPath())  # type: ignore[arg-type]
        self.assertEqual(artifact_calls, ["rb", MAX_ARTIFACT_BYTES + 1])

        source_calls: list[object] = []

        class SourceReader:
            def __enter__(self) -> "SourceReader":
                return self

            def __exit__(self, *args: object) -> None:
                return None

            def read(self, size: int = -1) -> bytes:
                source_calls.append(size)
                return b" " * size

        class SourcePath:
            def open(self, mode: str) -> SourceReader:
                source_calls.append(mode)
                return SourceReader()

        with self.assertRaisesRegex(ValueError, "byte resource cap"):
            _read_source(SourcePath())  # type: ignore[arg-type]
        self.assertEqual(source_calls, ["rb", MAX_SOURCE_BYTES + 1])

    def test_json_depth_cap_is_enforced(self) -> None:
        artifact = self._semantic_mutation()
        nested: dict[str, object] = {}
        cursor = nested
        for _ in range(26):
            child: dict[str, object] = {}
            cursor["x"] = child
            cursor = child
        artifact["payload"]["nested"] = nested
        self._refresh_digest(artifact)
        with self.assertRaisesRegex(ValueError, "maximum JSON depth"):
            verify_artifact(self._write_artifact(artifact))

    def test_precision_resource_cap_and_boolean_alias_are_enforced(self) -> None:
        with self.assertRaisesRegex(ValueError, "bounded canonical integer"):
            build_artifact(precision=255)
        with self.assertRaisesRegex(ValueError, "bounded canonical integer"):
            build_artifact(precision=1025)
        with self.assertRaisesRegex(ValueError, "bounded canonical integer"):
            build_artifact(precision=True)


if __name__ == "__main__":
    unittest.main()
