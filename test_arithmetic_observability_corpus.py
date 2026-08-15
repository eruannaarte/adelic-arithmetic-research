#!/usr/bin/env python3
"""Hostile regression tests for the AO corpus manifest."""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest import mock

import arithmetic_observability_corpus as corpus


class CorpusManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = corpus.expected_payload()

    def _temporary_json(self, raw: bytes) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name) / "hostile.json"
        path.write_bytes(raw)
        return directory, path

    def _temporary_artifact(self, artifact: dict[str, object]) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        return self._temporary_json(corpus._pretty_json(artifact))

    def test_01_schema_and_payload_pin(self) -> None:
        self.assertEqual(corpus.SCHEMA, "arithmetic-observability-corpus-v1")
        self.assertEqual(corpus._payload_sha256(self.payload), corpus.PINNED_PAYLOAD_SHA256)

    def test_02_committed_manifest_verifies(self) -> None:
        artifact = corpus.verify_artifact()
        self.assertEqual(artifact["payload"], self.payload)

    def test_03_full_reconstruction_matches_committed_manifest(self) -> None:
        artifact, raw = corpus._load_json_strict(corpus.DEFAULT_ARTIFACT_PATH)
        self.assertEqual(corpus.build_artifact(), artifact)
        self.assertEqual(raw, corpus._pretty_json(artifact))

    def test_04_payload_is_float_free(self) -> None:
        stack = [self.payload]
        while stack:
            value = stack.pop()
            self.assertNotIsInstance(value, float)
            if isinstance(value, dict):
                stack.extend(value.values())
            elif isinstance(value, list):
                stack.extend(value)

    def test_05_counts_are_exact(self) -> None:
        self.assertEqual(len(self.payload["manuscripts"]), 10)
        self.assertEqual(len(self.payload["formal_packages"]), 11)
        triplet_paths = {
            binding["path"]
            for package in self.payload["formal_packages"]
            for binding in package["files"].values()
        }
        self.assertEqual(len(triplet_paths), 33)

    def test_06_all_manuscripts_are_mapped(self) -> None:
        manuscripts = {item["id"] for item in self.payload["manuscripts"]}
        covered = {
            manuscript
            for package in self.payload["formal_packages"]
            for manuscript in package["manuscript_ids"]
        }
        self.assertEqual(covered, manuscripts)

    def test_07_manuscript_hashes_and_theorem_anchors(self) -> None:
        corpus._validate_manuscripts(self.payload)

    def test_08_all_upstream_schemas_and_payload_hashes(self) -> None:
        corpus._validate_packages(self.payload)

    def test_09_external_dependencies_recompute(self) -> None:
        corpus._validate_external_dependencies(self.payload)

    def test_10_atlas_is_one_way_pinned(self) -> None:
        atlas = self.payload["atlas"]
        self.assertEqual(atlas["sha256"], "b381d3f9424de5ed5e6cfe35c27093ee2ce38b08d742299bfe7a1ee7a55db10f")
        self.assertEqual(atlas["bytes"], 23_993)
        self.assertIn("no corpus artifact hash", atlas["binding_direction"])
        corpus._validate_file(atlas)

    def test_11_dependency_dag_is_exact_and_acyclic(self) -> None:
        corpus._validate_dag(self.payload)

    def test_12_cycle_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "cycle"):
            corpus._assert_acyclic(["a", "b", "c"], [["a", "b"], ["b", "c"], ["c", "a"]])

    def test_13_unknown_dependency_node_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown node"):
            corpus._assert_acyclic(["a"], [["a", "missing"]])

    def test_14_duplicate_dependency_edge_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicated"):
            corpus._assert_acyclic(["a", "b"], [["a", "b"], ["a", "b"]])

    def test_15_logical_and_formal_edge_types(self) -> None:
        logical = self.payload["dependency_dag"]["logical_manuscript_edges"]
        formal = self.payload["dependency_dag"]["formal_artifact_edges"]
        self.assertNotIn(["AO-VII", "AO-V"], logical)
        self.assertEqual(self.payload["dependency_dag"]["schedule_provenance_only_edge"], ["AO-VII", "AO-V"])
        self.assertIn(["PKG-full-segre", "AO-VI"], formal)
        self.assertIn(["PKG-convexification-gap", "PKG-alias-circle"], formal)

    def test_16_goal_requirement_keys_are_complete(self) -> None:
        self.assertEqual(
            set(self.payload["goal_requirement_evidence"]),
            {"definitions", "framework", "exact_equivalence", "stability", "reconstruction", "obstruction", "geometry", "nontrivial_models", "reproducibility"},
        )
        corpus._validate_evidence(self.payload)

    def test_17_every_evidence_theorem_resolves(self) -> None:
        known = {
            theorem
            for record in corpus.MANUSCRIPTS
            for theorem in record["theorem_anchors"]
        }
        cited = {
            theorem
            for item in self.payload["goal_requirement_evidence"].values()
            for theorem in item["theorem_ids"]
        }
        self.assertTrue(cited <= known)
        self.assertTrue(cited)

    def test_18_unknown_evidence_theorem_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["goal_requirement_evidence"]["framework"]["theorem_ids"].append("AO-X.99.99")
        with self.assertRaisesRegex(ValueError, "theorem evidence"):
            corpus._validate_evidence(mutated)

    def test_19_evidence_vocabulary_is_closed(self) -> None:
        self.assertEqual(self.payload["evidence_vocabulary"], list(corpus.EVIDENCE_VOCABULARY))
        mutated = copy.deepcopy(self.payload)
        mutated["goal_requirement_evidence"]["geometry"]["evidence_types"] = ["numerical-impression"]
        with self.assertRaisesRegex(ValueError, "evidence vocabulary"):
            corpus._validate_evidence(mutated)

    def test_20_observational_equivalence_and_confusability_differ(self) -> None:
        terminology = self.payload["corpus"]["terminology"]
        self.assertIn("common quotient", terminology["observational_equivalence"])
        self.assertIn("not asserted to be transitive", terminology["confusability"])
        self.assertIn("compact integer-selection image", terminology["tail_set"])

    def test_21_model_taxonomy_preserves_boundaries(self) -> None:
        corpus._validate_models(self.payload)
        by_id = {item["id"]: item for item in self.payload["model_taxonomy"]}
        self.assertEqual(by_id["arithmetic-realizability-boundary"]["status"], "nonclaim-boundary")
        self.assertEqual(by_id["continuous-common-box"]["status"], "relaxation-model")
        self.assertIn("independent envelopes", by_id["independent-integral-envelope"]["scope"])

    def test_22_ao_ix_and_x_declare_continuous_box(self) -> None:
        by_id = {item["id"]: item for item in self.payload["manuscripts"]}
        self.assertIn("continuous-common-box", by_id["AO-IX"]["model_ids"])
        self.assertIn("continuous-common-box", by_id["AO-X"]["model_ids"])
        self.assertIn("arithmetic-realizability-boundary", by_id["AO-X"]["model_ids"])

    def test_23_convexification_scope_does_not_overclaim_mechanization(self) -> None:
        package = next(item for item in self.payload["formal_packages"] if item["id"] == "PKG-convexification-gap")
        self.assertIn("finite prefix/envelope inputs", package["formal_scope"])
        self.assertIn("remain manuscript mathematics", package["formal_scope"])
        self.assertNotIn("Exact convexification identities", package["formal_scope"])

    def test_24_prime_box_legacy_layout_is_explicit(self) -> None:
        package = next(item for item in self.payload["formal_packages"] if item["id"] == "PKG-prime-box")
        self.assertEqual(package["artifact_regeneration"], "semantic-only-legacy-byte-layout")

    def test_25_legacy_parser_scope_is_explicit(self) -> None:
        caveats = "\n".join(self.payload["resource_and_platform_caveats"])
        self.assertIn("do not themselves provide bounded strict JSON parsers", caveats)
        self.assertIn("corpus ingestion", caveats)

    def test_26_formal_nonclaims_are_explicit(self) -> None:
        nonclaims = self.payload["formal_scope"]["nonclaims"]
        self.assertIn("the manifest does not mechanize every theorem in the manuscripts", nonclaims)
        self.assertIn("convex-hull equality is scoped to independent coefficient envelopes only", nonclaims)
        self.assertIn("independent integer selections do not imply number-field or global arithmetic realizability", nonclaims)

    def test_27_strict_parser_rejects_duplicate_keys(self) -> None:
        directory, path = self._temporary_json(b'{"x":1,"x":2}\n')
        with directory, self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            corpus._load_json_strict(path)

    def test_28_strict_parser_rejects_floats(self) -> None:
        directory, path = self._temporary_json(b'{"x":1.25}\n')
        with directory, self.assertRaisesRegex(ValueError, "floating-point"):
            corpus._load_json_strict(path)

    def test_29_legacy_reader_accepts_only_finite_decimals(self) -> None:
        directory, path = self._temporary_json(b'{"x":1.25}\n')
        with directory:
            parsed, _ = corpus._load_json_legacy_finite(path)
            self.assertEqual(parsed["x"], 1.25)
        directory, path = self._temporary_json(b'{"x":NaN}\n')
        with directory, self.assertRaisesRegex(ValueError, "non-finite"):
            corpus._load_json_legacy_finite(path)

    def test_30_strict_parser_rejects_bom_crlf_and_extra_lf(self) -> None:
        for raw, message in (
            (b'\xef\xbb\xbf{}\n', "BOM"),
            (b'{}\r\n', "CR"),
            (b'{}\n\n', "exactly one LF"),
        ):
            with self.subTest(raw=raw):
                directory, path = self._temporary_json(raw)
                with directory, self.assertRaisesRegex(ValueError, message):
                    corpus._load_json_strict(path)

    def test_31_strict_parser_rejects_oversized_integer(self) -> None:
        directory, path = self._temporary_json(b'{"x":' + b"9" * 1_301 + b'}\n')
        with directory, self.assertRaisesRegex(ValueError, "decimal bound"):
            corpus._load_json_strict(path)

    def test_32_strict_parser_rejects_excessive_depth(self) -> None:
        depth = corpus.MAX_JSON_DEPTH + 2
        raw = ("[" * depth + "0" + "]" * depth + "\n").encode("ascii")
        directory, path = self._temporary_json(raw)
        with directory, self.assertRaisesRegex(ValueError, "depth bound"):
            corpus._load_json_strict(path)

    def test_33_bounded_reader_requests_at_most_cap_plus_one(self) -> None:
        class FakeReader:
            def __init__(self) -> None:
                self.calls: list[int] = []

            def __enter__(self):
                return self

            def __exit__(self, *_: object) -> None:
                return None

            def read(self, size: int) -> bytes:
                self.calls.append(size)
                return b"x" * size

        fake = FakeReader()
        with mock.patch.object(corpus, "_open_regular", return_value=fake):
            with self.assertRaisesRegex(ValueError, "byte bound"):
                corpus._read_bounded_regular(Path("hostile"), 17)
        self.assertEqual(fake.calls, [18])

    def test_34_strict_parser_rejects_oversized_file(self) -> None:
        directory, path = self._temporary_json(b" " * 129)
        with directory, self.assertRaisesRegex(ValueError, "byte bound"):
            corpus._load_json_strict(path, maximum_bytes=128)

    def test_34b_digest_accepts_cap_and_rejects_cap_plus_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            exact = Path(directory) / "exact"
            excess = Path(directory) / "excess"
            exact.write_bytes(b"x" * 128)
            excess.write_bytes(b"x" * 129)
            self.assertEqual(corpus._sha256_file(exact, 128), hashlib.sha256(b"x" * 128).hexdigest())
            with self.assertRaisesRegex(ValueError, "byte bound"):
                corpus._sha256_file(excess, 128)

    @unittest.skipUnless(hasattr(os, "symlink"), "platform has no symlink support")
    def test_35_symlink_input_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.json"
            target.write_bytes(b"{}\n")
            link = root / "link.json"
            try:
                link.symlink_to(target)
            except OSError as exc:
                self.skipTest(f"symlink creation is unavailable: {exc}")
            with self.assertRaisesRegex(ValueError, "symlink"):
                corpus._load_json_strict(link)
            with self.assertRaisesRegex(ValueError, "symlink"):
                corpus._sha256_file(link)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "platform has no FIFO support")
    def test_36_nonregular_input_is_rejected_without_opening(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fifo = Path(directory) / "pipe"
            os.mkfifo(fifo)
            self.assertTrue(stat.S_ISFIFO(fifo.stat(follow_symlinks=False).st_mode))
            with self.assertRaisesRegex(ValueError, "non-regular"):
                corpus._load_json_strict(fifo)

    def test_37_payload_mutation_without_rehash_is_rejected(self) -> None:
        artifact = copy.deepcopy(corpus.verify_artifact())
        artifact["payload"]["corpus"]["manuscript_count"] = 9
        directory, path = self._temporary_artifact(artifact)
        with directory, self.assertRaisesRegex(ValueError, "payload digest mismatch"):
            corpus.verify_artifact(path)

    def test_38_payload_mutation_with_rehash_is_rejected_by_pin(self) -> None:
        artifact = copy.deepcopy(corpus.verify_artifact())
        artifact["payload"]["corpus"]["manuscript_count"] = 9
        artifact["payload_sha256"] = corpus._payload_sha256(artifact["payload"])
        directory, path = self._temporary_artifact(artifact)
        with directory, self.assertRaisesRegex(ValueError, "pinned verifier digest"):
            corpus.verify_artifact(path)

    def test_39_top_level_extension_is_rejected(self) -> None:
        artifact = copy.deepcopy(corpus.verify_artifact())
        artifact["surprise"] = True
        directory, path = self._temporary_artifact(artifact)
        with directory, self.assertRaisesRegex(ValueError, "top-level keys"):
            corpus.verify_artifact(path)

    def test_40_noncanonical_manifest_layout_is_rejected(self) -> None:
        artifact = corpus.verify_artifact()
        raw = corpus._canonical_json(artifact) + b"\n"
        directory, path = self._temporary_json(raw)
        with directory, self.assertRaisesRegex(ValueError, "canonical pretty"):
            corpus.verify_artifact(path)

    def test_41_reproduction_hash_mutation_is_rejected(self) -> None:
        artifact = copy.deepcopy(corpus.verify_artifact())
        artifact["reproduction_files"]["tests"]["sha256"] = "0" * 64
        directory, path = self._temporary_artifact(artifact)
        with directory, self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            corpus.verify_artifact(path)

    def test_41b_reproduction_binding_extension_is_rejected(self) -> None:
        artifact = copy.deepcopy(corpus.verify_artifact())
        artifact["reproduction_files"]["tests"]["comment"] = "unhashed extension"
        directory, path = self._temporary_artifact(artifact)
        with directory, self.assertRaisesRegex(ValueError, "binding keys"):
            corpus.verify_artifact(path)

    def test_42_dependency_file_hash_mutation_is_rejected(self) -> None:
        binding = copy.deepcopy(self.payload["formal_packages"][0]["files"]["verifier"])
        with mock.patch.object(corpus, "_sha256_file", return_value="0" * 64):
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                corpus._validate_file(binding)

    def test_43_wrong_upstream_payload_hash_is_rejected(self) -> None:
        package = copy.deepcopy(self.payload["formal_packages"][0])
        package["payload_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "recorded payload mismatch"):
            corpus._validate_upstream_artifact(package)

    def test_44_deterministic_write_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            corpus.write_artifact(first)
            corpus.write_artifact(second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(first.read_bytes(), corpus.DEFAULT_ARTIFACT_PATH.read_bytes())

    def test_45_manifest_is_ascii_lf_and_single_terminated(self) -> None:
        raw = corpus.DEFAULT_ARTIFACT_PATH.read_bytes()
        raw.decode("ascii", errors="strict")
        self.assertNotIn(b"\r", raw)
        self.assertTrue(raw.endswith(b"\n"))
        self.assertFalse(raw.endswith(b"\n\n"))

    def test_46_payload_avoids_self_hash_circularity(self) -> None:
        text = corpus._canonical_json(self.payload).decode("ascii")
        self.assertNotIn(corpus.VERIFIER_PATH.name, text)
        self.assertNotIn(corpus.TESTS_PATH.name, text)
        self.assertNotIn(corpus.DEFAULT_ARTIFACT_PATH.name, text)

    def test_47_only_full_segre_upstream_binds_its_manuscript_hash(self) -> None:
        bound = [
            package["id"] for package in self.payload["formal_packages"]
            if package["upstream_artifact_binds_manuscript_hash"]
        ]
        self.assertEqual(bound, ["PKG-full-segre"])

    def test_48_every_package_has_schema_payload_scope_and_runtime(self) -> None:
        for package in self.payload["formal_packages"]:
            with self.subTest(package=package["id"]):
                self.assertRegex(package["schema"], r"^arithmetic-observability-.+-v1$")
                self.assertRegex(package["payload_sha256"], r"^[0-9a-f]{64}$")
                self.assertTrue(package["formal_scope"])
                self.assertTrue(package["runtime"])

    def test_49_reproduction_bindings_match_current_source_and_tests(self) -> None:
        artifact = corpus.verify_artifact()
        for role, path in (("verifier", corpus.VERIFIER_PATH), ("tests", corpus.TESTS_PATH)):
            binding = artifact["reproduction_files"][role]
            self.assertEqual(binding["bytes"], path.stat().st_size)
            self.assertEqual(binding["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
