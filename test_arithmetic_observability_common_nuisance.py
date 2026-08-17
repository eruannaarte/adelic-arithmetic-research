from __future__ import annotations

import copy
from fractions import Fraction
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from arithmetic_observability_common_nuisance import (
    ANCHORS,
    DEFAULT_ARTIFACT_PATH,
    DEFAULT_SOURCE_PATH,
    MAX_ARTIFACT_BYTES,
    MAX_CONTAINER_ITEMS,
    MAX_JSON_DEPTH,
    PINNED_PAYLOAD_SHA256,
    SCHEMA,
    SOURCE_MAXIMUM_NORM,
    TESTS_PATH,
    VERIFIER_PATH,
    _canonical_json,
    _load_json_strict,
    _parse_fraction_limited,
    _pretty_json,
    _sha256,
    _sha256_file,
    artifact_document,
    build_payload,
    load_artifact,
    verify_artifact,
)


class CommonNuisanceCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.artifact, cls.raw = load_artifact(DEFAULT_ARTIFACT_PATH)
        cls.payload = cls.artifact["payload"]
        assert isinstance(cls.payload, dict)
        cls.common = cls.payload["common_box_observability"]
        cls.records = cls.common["coordinate_records"]
        cls.aliases = {
            witness["target_coordinate"]: witness
            for witness in cls.payload["integral_alias_witnesses"]
        }

    def test_committed_artifact_is_canonical_and_reproducible(self) -> None:
        self.assertEqual(self.raw, _pretty_json(self.artifact))
        expected = artifact_document(build_payload(DEFAULT_SOURCE_PATH))
        self.assertEqual(_canonical_json(self.artifact), _canonical_json(expected))
        self.assertEqual(
            self.artifact["payload_sha256"],
            "96b874899b16e4502d815627c7b722b9ba0332266fb30c8cd4d0579b48ca0cfd",
        )
        self.assertEqual(PINNED_PAYLOAD_SHA256, self.artifact["payload_sha256"])

    def test_strict_verifier_accepts_committed_artifact(self) -> None:
        result = verify_artifact(self.artifact, DEFAULT_SOURCE_PATH)
        self.assertTrue(result["passed"])
        self.assertEqual(result["schema"], SCHEMA)
        self.assertEqual(result["payload_sha256"], self.artifact["payload_sha256"])

    def test_reproduction_file_digests_pin_verifier_and_tests(self) -> None:
        reproduction = self.artifact["reproduction_files"]
        self.assertEqual(reproduction["verifier_basename"], VERIFIER_PATH.name)
        self.assertEqual(reproduction["tests_basename"], TESTS_PATH.name)
        self.assertEqual(reproduction["verifier_sha256"], _sha256_file(VERIFIER_PATH))
        self.assertEqual(reproduction["tests_sha256"], _sha256_file(TESTS_PATH))

    def test_all_fifty_common_box_rows_recompute_exactly(self) -> None:
        q = Fraction(self.common["global_gram_row_upper_exact"])
        self.assertEqual(len(self.records), SOURCE_MAXIMUM_NORM)
        for expected_n, record in enumerate(self.records, 1):
            self.assertEqual(record["coordinate"], expected_n)
            eta = Fraction(record["pair_specific_eta_bound_exact"])
            q_n = Fraction(record["gram_row_upper_exact"])
            finite = Fraction(record["finite_decoder_principal_exact"])
            remote = Fraction(record["remote_decoder_principal_exact"])
            coupling = Fraction(record["inverse_coupling_exact"])
            self.assertEqual(eta, finite + remote + coupling)
            schur_factor = (1 - q - q_n * q_n) / (1 - q)
            expected_radius_squared = (
                (1 - eta) ** 2 * schur_factor / (4 * expected_n**4)
            )
            self.assertEqual(
                Fraction(record["common_box_radius_squared_exact"]),
                expected_radius_squared,
            )
            generic = (
                (Fraction(1, 2) - eta) ** 2
                * schur_factor
                / expected_n**4
            )
            self.assertEqual(
                Fraction(record["generic_two_tail_radius_squared_exact"]),
                generic,
            )
            self.assertGreater(expected_radius_squared, generic)

    def test_declared_bottlenecks_are_exact_minima(self) -> None:
        radii = {
            record["coordinate"]: Fraction(
                record["common_box_radius_squared_exact"]
            )
            for record in self.records
        }
        self.assertEqual(min(radii, key=radii.__getitem__), 50)
        self.assertEqual(
            min(ANCHORS, key=radii.__getitem__),
            5,
        )
        self.assertEqual(self.common["unique_all_fifty_bottleneck"], 50)
        self.assertEqual(self.common["unique_four_anchor_bottleneck"], 5)
        self.assertEqual(
            Fraction(self.common["all_fifty_common_box_radius_squared_exact"]),
            radii[50],
        )
        self.assertEqual(
            Fraction(self.common["four_anchor_common_box_radius_squared_exact"]),
            radii[5],
        )

    def test_all_fifty_gain_is_between_127_and_128(self) -> None:
        gain_squared = Fraction(
            self.common["common_to_old_all_fifty_gain_squared_exact"]
        )
        self.assertGreater(gain_squared, 127**2)
        self.assertLess(gain_squared, 128**2)
        self.assertEqual(
            self.common["common_to_old_all_fifty_gain_strictly_between"],
            [127, 128],
        )

    def test_selected_eta_decompositions_are_exact(self) -> None:
        selected = {
            record["coordinate"]: record
            for record in self.common["selected_eta_decompositions"]
        }
        self.assertEqual(set(selected), {5, 50})
        for n, record in selected.items():
            finite = Fraction(record["finite_decoder_principal_exact"])
            remote = Fraction(record["remote_decoder_principal_exact"])
            coupling = Fraction(record["inverse_coupling_exact"])
            eta = Fraction(record["pair_specific_eta_bound_exact"])
            self.assertEqual(eta, finite + remote + coupling)
            self.assertEqual(
                Fraction(record["remote_to_finite_ratio_exact"]),
                remote / finite,
            )
            self.assertGreater(remote, finite, n)

    def test_direct_column_pair_bounds_bracket_alias_witnesses(self) -> None:
        pairs = {
            record["coordinate"]: record
            for record in self.common["direct_column_pair_bounds"]
        }
        self.assertEqual(set(pairs), {5, 50})
        for n, record in pairs.items():
            eta_direct = Fraction(record["eta_direct_exact"])
            column = Fraction(1, n**2)
            radius_lower = Fraction(record["direct_pair_radius_lower_exact"])
            self.assertEqual(radius_lower, (column - eta_direct) / 2)
            alias_upper = Fraction(self.aliases[n]["robust_radius_upper_exact"])
            self.assertLess(radius_lower, alias_upper)
            self.assertLess(alias_upper, Fraction(1, 2 * n**2))
            self.assertIn("pair-specific", record["scope"])

    def test_no_tail_e5_prefix_lattice_proof_has_positive_margin(self) -> None:
        section = self.payload["no_tail_prefix_lattice"]
        spacing = Fraction(section["minimum_nonzero_nuisance_scaled_norm_exact"])
        root = Fraction(section["nuisance_positive_root_exact"])
        increment = Fraction(section["minimum_nuisance_increment_lower_exact"])
        witness = Fraction(section["zero_tail_e5_distance_squared_exact"])
        self.assertEqual(spacing, Fraction(1, 2500))
        self.assertLess(root, spacing)
        self.assertGreater(increment, 0)
        self.assertEqual(witness, Fraction(1, 625))
        self.assertGreater(
            Fraction(section["query_2_or_3_difference_lower_squared_exact"]),
            witness,
        )
        self.assertGreater(
            Fraction(section["absolute_d5_at_least_two_lower_squared_exact"]),
            witness,
        )
        self.assertTrue(section["passed"])

    def test_alias_factorizations_and_d14_values_are_exact(self) -> None:
        for target, witness in self.aliases.items():
            self.assertEqual(witness["mode_count"], 10)
            for record in witness["mode_records"]:
                product = 1
                d14 = 1
                previous = 1
                for prime, exponent in record["factorization"]:
                    self.assertGreater(prime, previous)
                    product *= prime**exponent
                    d14 *= math.comb(13 + exponent, exponent)
                    previous = prime
                self.assertEqual(product, record["mode"])
                self.assertEqual(d14, record["d14"])
                self.assertEqual(record["tail_coefficient"], d14)
                self.assertEqual(
                    Fraction(record["normalized_amplitude_exact"]),
                    Fraction(d14, record["mode"] ** 2),
                )
                self.assertGreater(record["mode"], SOURCE_MAXIMUM_NORM)
            self.assertEqual(witness["target_coordinate"], target)

    def test_integral_alias_witnesses_strictly_improve_zero_tail(self) -> None:
        thresholds = {5: Fraction(22, 10**13), 50: Fraction(38, 10**14)}
        for target, witness in self.aliases.items():
            radius_upper = Fraction(witness["robust_radius_upper_exact"])
            zero = Fraction(witness["zero_tail_radius_exact"])
            improvement = Fraction(witness["improvement_lower_exact"])
            self.assertLess(radius_upper, zero)
            self.assertGreater(improvement, thresholds[target])
            self.assertTrue(witness["strictly_below_zero_tail_upper"])
            self.assertTrue(witness["all_tail_coefficients_integral_and_legal"])
            self.assertFalse(witness["continuous_convexity_used"])
            self.assertEqual(
                witness["tail_class"],
                "integral nonnegative d_14-dominated tails",
            )

    def test_prefix_reduction_excludes_exactly_the_certified_early_modes(self) -> None:
        section = self.payload["four_anchor_prefix_reduction"]
        alias_upper = Fraction(section["alias_response_squared_upper_exact"])
        self.assertEqual(
            section["necessary_query_coordinates"],
            {"h_1": 0, "h_2": 0, "h_3": 0, "absolute_h_5": 1},
        )
        self.assertGreater(
            Fraction(section["unit_h2_distance_lower_squared_exact"]),
            alias_upper,
        )
        self.assertGreater(
            Fraction(section["unit_h3_distance_lower_squared_exact"]),
            alias_upper,
        )
        self.assertGreater(
            Fraction(section["absolute_h5_at_least_two_lower_squared_exact"]),
            alias_upper,
        )
        expected_excluded = [4, *range(6, 15)]
        self.assertEqual(section["excluded_nonquery_prefix_coordinates"], expected_excluded)
        self.assertEqual(section["unresolved_nonquery_prefix_coordinates"], list(range(15, 51)))
        for record in section["excluded_coordinate_records"]:
            self.assertGreater(
                Fraction(record["projection_energy_lower_exact"]),
                alias_upper,
            )
            self.assertGreater(Fraction(record["excess_exact"]), 0)
        self.assertFalse(section["exact_global_search_completed"])

    def test_scope_distinguishes_integral_and_continuous_tails(self) -> None:
        scope = self.payload["scope"]
        consequences = self.payload["formal_consequences"]
        self.assertIn("continuous coefficient boxes", scope["common_box_lower_applies_to"])
        self.assertTrue(
            any(
                "integral-tail subclasses" in label
                for label in scope["common_box_lower_applies_to"]
            )
        )
        self.assertEqual(scope["alias_upper_witness_uses"], "integral endpoint coefficients only")
        self.assertFalse(scope["continuous_convex_zonotope_required_for_alias_witness"])
        self.assertFalse(consequences["zero_tail_e5_is_full_tail_fibre_optimum"])
        self.assertFalse(consequences["exact_closest_fibre_value_determined"])

    def test_search_metadata_makes_no_optimality_claim(self) -> None:
        search = self.payload["search_provenance"]
        self.assertEqual(search["integer_half_width"], 1_000_000)
        self.assertEqual(search["selected_count_per_target"], 10)
        self.assertFalse(search["exhaustive_optimality_claimed"])
        self.assertIn("non-formal", search["status"])

    def test_fraction_parser_rejects_noncanonical_and_oversized_values(self) -> None:
        self.assertEqual(_parse_fraction_limited("3/7"), Fraction(3, 7))
        for value in ("6/14", "3", "1/0", True, "01/2", "1/+2"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    _parse_fraction_limited(value)
        with self.assertRaises(ValueError):
            _parse_fraction_limited("1" * 9000 + "/1")

    def test_tampered_digest_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.artifact)
        tampered["payload_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            verify_artifact(tampered, DEFAULT_SOURCE_PATH)

    def test_rehashed_bool_for_integer_substitution_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.artifact)
        tampered["payload"]["common_box_observability"]["coordinate_records"][49][
            "coordinate"
        ] = True
        tampered["payload_sha256"] = _sha256(tampered["payload"])
        with self.assertRaises(ValueError):
            verify_artifact(tampered, DEFAULT_SOURCE_PATH)

    def test_rehashed_alias_factor_tamper_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.artifact)
        record = tampered["payload"]["integral_alias_witnesses"][0]["mode_records"][0]
        record["d14"] += 1
        tampered["payload_sha256"] = _sha256(tampered["payload"])
        with self.assertRaises(ValueError):
            verify_artifact(tampered, DEFAULT_SOURCE_PATH)

    def test_unexpected_top_level_field_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.artifact)
        tampered["extra"] = False
        with self.assertRaises(ValueError):
            verify_artifact(tampered, DEFAULT_SOURCE_PATH)

    def test_loader_rejects_duplicate_float_nonfinite_and_non_lf_json(self) -> None:
        cases = (
            b'{"a":1,"a":2}\n',
            b'{"a":1.25}\n',
            b'{"a":NaN}\n',
            b'{"a":-0}\n',
            b'\xef\xbb\xbf{"a":1}\n',
            b'{"a":1}\r\n',
            b'{"a":1}\n\n',
            b'{"a":1}',
        )
        for raw in cases:
            with self.subTest(raw=raw):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "bad.json"
                    path.write_bytes(raw)
                    with self.assertRaises(ValueError):
                        _load_json_strict(path, 100)

    def test_loader_applies_byte_bound_before_json_parsing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large.json"
            path.write_bytes(b"{" + b" " * MAX_ARTIFACT_BYTES + b"}\n")
            with self.assertRaisesRegex(ValueError, "byte limit"):
                _load_json_strict(path, MAX_ARTIFACT_BYTES)

    def test_artifact_loader_rejects_noncanonical_whitespace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spaced.json"
            path.write_bytes((json.dumps(self.artifact) + "\n").encode("utf-8"))
            with self.assertRaisesRegex(ValueError, "canonical deterministic"):
                load_artifact(path)

    def test_loader_requests_only_maximum_plus_one_bytes(self) -> None:
        class GuardedReader:
            def __init__(self) -> None:
                self.sizes: list[int] = []

            def __enter__(self) -> "GuardedReader":
                return self

            def __exit__(self, *_: object) -> None:
                return None

            def read(self, size: int = -1) -> bytes:
                if size < 0:
                    raise AssertionError("unbounded read attempted")
                self.sizes.append(size)
                return b" " * size

        class FakePath:
            def __init__(self, reader: GuardedReader) -> None:
                self.reader = reader

            def open(self, mode: str) -> GuardedReader:
                self.assert_mode = mode
                return self.reader

        reader = GuardedReader()
        path = FakePath(reader)
        with self.assertRaisesRegex(ValueError, "byte limit"):
            _load_json_strict(path, 37)  # type: ignore[arg-type]
        self.assertEqual(reader.sizes, [38])
        self.assertEqual(path.assert_mode, "rb")

    def test_loader_rejects_depth_container_and_integer_resource_excess(self) -> None:
        too_deep = ("[" * (MAX_JSON_DEPTH + 2) + "0" + "]" * (MAX_JSON_DEPTH + 2) + "\n").encode()
        too_wide = (
            "[" + ",".join("0" for _ in range(MAX_CONTAINER_ITEMS + 1)) + "]\n"
        ).encode()
        huge_integer = ("{\"a\":" + "1" * 3000 + "}\n").encode()
        for raw in (too_deep, too_wide, huge_integer):
            with self.subTest(length=len(raw)):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "resource.json"
                    path.write_bytes(raw)
                    with self.assertRaises(ValueError):
                        _load_json_strict(path, 20_000)

    def test_pinned_source_file_is_required(self) -> None:
        source = json.loads(DEFAULT_SOURCE_PATH.read_text(encoding="utf-8"))
        source["certificate"]["parameters"]["degree"] = 13
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.json"
            path.write_bytes(
                (json.dumps(source, indent=2, sort_keys=True) + "\n").encode("utf-8")
            )
            with self.assertRaisesRegex(ValueError, "file digest"):
                build_payload(path)

    def test_cli_verifies_committed_certificate(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).with_name("arithmetic_observability_common_nuisance.py")),
                "--certificate",
                str(DEFAULT_ARTIFACT_PATH),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertTrue(result["passed"])
        self.assertEqual(result["schema"], SCHEMA)

    def test_cli_external_write_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "rebuilt.json"
            subprocess.run(
                [
                    sys.executable,
                    str(
                        Path(__file__).with_name(
                            "arithmetic_observability_common_nuisance.py"
                        )
                    ),
                    "--source",
                    str(DEFAULT_SOURCE_PATH),
                    "--write",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(output.read_bytes(), self.raw)


if __name__ == "__main__":
    unittest.main()
