"""Strict reproduction and provenance checks for the OIG wind tunnel.

The browser demo deliberately mixes three evidence levels.  These tests keep
that presentation honest: the live browser calculation may be approximate,
the refined outcome may be numerical, and the certified badge may only refer
to the exact fixed-model theorem copied from the committed source artifacts.
"""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest import mock

import build_double_pendulum_wind_tunnel_data as builder


ROOT = Path(__file__).resolve().parent
APP_DIR = ROOT / "website" / "double-pendulum-oig-wind-tunnel"
INDEX = APP_DIR / "index.html"
DATA_BUNDLE = APP_DIR / "wind-tunnel-data.js"


class _LocalAssetParser(HTMLParser):
    """Collect browser-loaded assets without needing an HTML dependency."""

    def __init__(self) -> None:
        super().__init__()
        self.scripts: list[str] = []
        self.stylesheets: list[str] = []
        self.media: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        values = dict(attrs)
        if tag == "script" and values.get("src"):
            self.scripts.append(values["src"] or "")
        if (
            tag == "link"
            and "stylesheet" in (values.get("rel") or "").lower().split()
            and values.get("href")
        ):
            self.stylesheets.append(values["href"] or "")
        if tag in {"img", "audio", "video", "source", "iframe"}:
            for attribute in ("src", "poster"):
                if values.get(attribute):
                    self.media.append(values[attribute] or "")


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected a JSON object in {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolved_local_reference(reference: str) -> Path | None:
    """Resolve a browser reference, returning None for anchors and data URLs."""

    if reference.startswith(("#", "data:")):
        return None
    path_part = reference.split("?", 1)[0].split("#", 1)[0]
    return (APP_DIR / path_part).resolve()


class DoublePendulumWindTunnelReproductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = builder.build_payload(verify_sources=True)
        cls.rendered = builder.render_javascript(cls.payload)

    def test_verifier_coverage_is_complete_and_verified_bundle_fails_closed(self) -> None:
        verifiers = builder._artifact_verifiers()
        self.assertEqual(
            set(verifiers),
            set(builder.ARTIFACTS),
            "every browser-visible source must have a scientific verifier",
        )
        self.assertTrue(self.payload["generatedFromVerifiedSources"])
        provenance = self.payload["provenance"]
        self.assertEqual(set(provenance), set(builder.ARTIFACTS))
        self.assertTrue(
            all(record["verified"] is True for record in provenance.values()),
            "the aggregate verified flag must never hide an unverified source",
        )
        self.assertEqual(
            self.payload["generatedFromVerifiedSources"],
            all(record["verified"] is True for record in provenance.values()),
        )

    def test_provenance_hashes_paths_and_extracted_arrays_match_sources(self) -> None:
        provenance = self.payload["provenance"]
        for name, source_path in builder.ARTIFACTS.items():
            record = provenance[name]
            self.assertEqual(record["path"], str(source_path.relative_to(ROOT)))
            self.assertRegex(record["sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(record["sha256"], _sha256(source_path))

        state = _read_json(builder.ARTIFACTS["state_atlas"])
        extracted_state = self.payload["stateAtlas"]
        self.assertEqual(extracted_state["parameters"], state["parameters"])
        self.assertEqual(extracted_state["run"], state["run"])
        self.assertEqual(extracted_state["summary"], state["atlas_summary"])
        self.assertEqual(
            extracted_state["fields"]["logStretch"],
            state["raw_fields"]["grid_edge_log_stretch"],
        )
        self.assertEqual(
            extracted_state["fields"]["initialEnergy"],
            state["raw_fields"]["initial_energy"],
        )
        self.assertEqual(
            extracted_state["fields"]["lowStretchMask"],
            state["raw_fields"][
                "resolved_low_stretch_no_sampled_full_turn_mask"
            ],
        )
        self.assertEqual(
            extracted_state["fields"]["componentLabels"],
            state["raw_fields"]["connected_region_labels"],
        )
        self.assertEqual(
            extracted_state["acceptanceStatus"], state["acceptance_status"]
        )
        self.assertEqual(
            extracted_state["resolvedCellCount"], state["resolved_cell_count"]
        )
        self.assertEqual(
            extracted_state["unresolvedCellCount"], state["unresolved_cell_count"]
        )
        self.assertEqual(
            extracted_state["maxEnergyDrift"],
            state["maximum_sampled_scaled_energy_drift"],
        )
        self.assertEqual(extracted_state["proofBoundary"], state["proof_boundary"])

        variation = _read_json(builder.ARTIFACTS["variational_atlas"])
        extracted_variation = self.payload["variationalAtlas"]
        self.assertEqual(
            extracted_variation["angles1"], variation["grid"]["theta1_centres"]
        )
        self.assertEqual(
            extracted_variation["angles2"], variation["grid"]["theta2_centres"]
        )
        self.assertEqual(
            extracted_variation["fields"]["weakestGain"],
            variation["fields"]["selected_weakest_local_gain"],
        )
        self.assertEqual(
            extracted_variation["fields"]["strongestGain"],
            variation["fields"]["selected_strongest_local_gain"],
        )
        self.assertEqual(
            extracted_variation["fields"]["resolvedMask"],
            variation["fields"]["resolved_mask"],
        )
        self.assertEqual(extracted_variation["summary"], variation["summary"])
        self.assertEqual(
            extracted_variation["proofBoundary"], variation["proof_boundary"]
        )

        # The two None-valued seam cells must remain unresolved in the browser;
        # silently filling them would turn missing numerical evidence into data.
        resolved = extracted_variation["fields"]["resolvedMask"]
        weakest = extracted_variation["fields"]["weakestGain"]
        strongest = extracted_variation["fields"]["strongestGain"]
        unresolved = [
            (row, column)
            for row in range(len(resolved))
            for column in range(len(resolved[row]))
            if not bool(resolved[row][column])
        ]
        self.assertEqual(unresolved, [(0, 12), (12, 0)])
        for row, column in unresolved:
            self.assertIsNone(weakest[row][column])
            self.assertIsNone(strongest[row][column])

    def test_persistence_extraction_matches_declared_half_threshold_rows(self) -> None:
        source = _read_json(builder.ARTIFACTS["persistence"])
        extracted = self.payload["persistence"]

        def expected_rows(
            rows: list[dict[str, object]], comparison: str
        ) -> list[dict[str, object]]:
            result = []
            for row in rows:
                record = row[comparison]
                match = next(
                    item
                    for item in record["threshold_overlap"]
                    if float(item["threshold"]) == 0.5
                )
                compact = {
                    key: row[key]
                    for key in ("name", "side", "shift", "feature_sample_count")
                    if key in row
                }
                compact.update(
                    {
                        "jaccard": match["jaccard"],
                        "candidateActive": match["candidate_active_count"],
                        "referenceActive": match["reference_active_count"],
                    }
                )
                result.append(compact)
            return result

        self.assertEqual(extracted["threshold"], source["config"]["reference_threshold"])
        self.assertEqual(
            extracted["resolution"],
            expected_rows(
                source["resolution_study"]["runs"],
                "comparison_to_highest_resolution",
            ),
        )
        self.assertEqual(
            extracted["shifts"],
            expected_rows(
                source["shift_study"]["runs"], "comparison_to_unshifted"
            ),
        )
        self.assertEqual(
            extracted["cadence"],
            expected_rows(
                source["cadence_study"]["runs"], "comparison_to_densest"
            ),
        )
        self.assertEqual(
            extracted["energyAssociation"], source["baseline_energy_association"]
        )
        self.assertEqual(extracted["proofBoundary"], source["proof_boundary"])

    def test_candidate_library_is_an_exact_projection_not_a_browser_recompute(self) -> None:
        source = _read_json(builder.ARTIFACTS["grouped_library"])
        expected_rows = []
        for row in source["scalar_observation_library"]:
            exact = row["declared_rational_point"]
            expected_rows.append(
                {
                    "name": row["name"],
                    "launch": row["launch_exact"],
                    "sensor": row["sensor"],
                    "tau": row["observation_time_tau_exact"],
                    "cost": row["legacy_scalar_cost_exact"],
                    "parameterResponse": exact["parameter_response_exact"],
                    "clockResponse": exact["clock_response_exact"],
                    "tier1ControlsPassed": row["tier1_controls_passed"],
                }
            )
        library = self.payload["candidateLibrary"]
        self.assertEqual(library["rows"], expected_rows)
        self.assertEqual(library["groups"], source["grouped_protocol_library"])
        self.assertEqual(
            library["selected"],
            source["selected_designs"]["cost_weighted_clock_only"],
        )
        self.assertEqual(
            library["minimumWitness"],
            source["selected_designs"]["minimum_clock_only"],
        )
        self.assertEqual(len(library["rows"]), 7)

    def test_certificates_preserve_exact_floors_and_all_scope_exclusions(self) -> None:
        two_source = _read_json(builder.ARTIFACTS["two_row_floor"])
        grouped_source = _read_json(builder.ARTIFACTS["grouped_clock_floor"])
        two = self.payload["certificates"]["twoRowNoNuisance"]
        grouped = self.payload["certificates"]["groupedSharedClock"]

        self.assertEqual(
            two["floorExact"], two_source["robust_physical_floor_lower_exact"]
        )
        self.assertEqual(two["scopeFlags"], two_source["scope_flags"])
        self.assertEqual(two["scopeBoundary"], two_source["scope_boundary"])
        self.assertEqual(
            grouped["floorExact"],
            grouped_source["theorem"][
                "sharp_physical_clock_profiled_floor_lower_exact"
            ],
        )
        self.assertEqual(
            grouped["simpleFloorExact"],
            grouped_source["theorem"][
                "simple_human_readable_floor_lower_exact"
            ],
        )
        self.assertEqual(grouped["scopeFlags"], grouped_source["scope_flags"])
        self.assertEqual(
            grouped["scopeBoundary"], grouped_source["scope_boundary"]
        )
        self.assertEqual(grouped["mixture"], grouped_source["fixed_grouped_mixture"])

        for excluded in (
            "empirical_model_adequacy_certified",
            "hardware_calibration_certified",
            "parameter_neighborhood_uniformity_certified",
            "seven_candidate_selection_certified",
            "seven_candidate_efficiency_certified",
        ):
            self.assertFalse(two["scopeFlags"][excluded], excluded)
        for excluded in (
            "candidate_selection_transfer_certified",
            "empirical_model_adequacy_certified",
            "finite_clock_dilation_amplitude_certified",
            "finite_grid_optimality_certified",
            "hardware_calibration_certified",
            "launch_preparation_error_bounded",
            "parameter_neighborhood_uniformity_certified",
        ):
            self.assertFalse(grouped["scopeFlags"][excluded], excluded)
        self.assertTrue(grouped["scopeFlags"]["exact_launch_preparation_assumed"])
        self.assertEqual(
            grouped["evidenceTier"],
            "tier_3_fixed_model_local_nuisance_profile_certificate",
        )

    def test_evidence_tiers_are_explicitly_noninterchangeable(self) -> None:
        boundary = self.payload["interfaceBoundary"]
        self.assertEqual(set(boundary), {"live", "refined", "certified"})
        self.assertIn("not certified", boundary["live"].lower())
        self.assertIn("independent", boundary["refined"].lower())
        self.assertIn("fixed A+B model experiment only", boundary["certified"])

    def test_unverified_build_is_visibly_unverified(self) -> None:
        unverified = builder.build_payload(verify_sources=False)
        self.assertFalse(unverified["generatedFromVerifiedSources"])
        self.assertTrue(
            all(
                record["verified"] is False
                for record in unverified["provenance"].values()
            )
        )

    def test_semantically_tampered_source_is_rejected_before_extraction(self) -> None:
        state_path = builder.ARTIFACTS["state_atlas"]
        tampered = _read_json(state_path)
        tampered["resolved_cell_count"] += 1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / state_path.name
            path.write_text(json.dumps(tampered), encoding="utf-8")
            paths = dict(builder.ARTIFACTS)
            paths["state_atlas"] = path
            with mock.patch.object(builder, "ARTIFACTS", paths):
                with self.assertRaisesRegex(ValueError, "state_atlas did not verify"):
                    builder.build_payload(verify_sources=True)

    def test_committed_bundle_is_deterministic_and_fresh(self) -> None:
        self.assertEqual(
            builder.render_javascript(self.payload),
            builder.render_javascript(builder.build_payload(verify_sources=True)),
        )
        self.assertTrue(DATA_BUNDLE.exists(), "generated browser data is missing")
        self.assertEqual(DATA_BUNDLE.read_text(encoding="utf-8"), self.rendered)
        self.assertTrue(
            self.rendered.startswith(
                "/* Generated by build_double_pendulum_wind_tunnel_data.py; do not edit. */"
            )
        )
        self.assertNotIn("NaN", self.rendered)
        self.assertNotIn("Infinity", self.rendered)

    def test_page_loads_only_committed_local_assets_in_dependency_order(self) -> None:
        self.assertTrue(INDEX.exists(), "wind-tunnel index.html is missing")
        html = INDEX.read_text(encoding="utf-8")
        parser = _LocalAssetParser()
        parser.feed(html)
        self.assertEqual(
            parser.scripts,
            ["wind-tunnel-data.js", "wind-tunnel-core.js", "wind-tunnel.js"],
            "data and numerical core must load before the interface",
        )
        self.assertEqual(parser.stylesheets, ["wind-tunnel.css"])
        app_root = APP_DIR.resolve()
        for reference in parser.scripts + parser.stylesheets + parser.media:
            self.assertNotRegex(reference, r"^(?:[a-z][a-z0-9+.-]*:)?//")
            target = _resolved_local_reference(reference)
            if target is None:
                continue
            self.assertTrue(
                target == app_root or app_root in target.parents,
                f"asset escapes the self-contained app: {reference}",
            )
            self.assertTrue(target.is_file(), f"missing local asset: {reference}")

    def test_certificate_shell_is_unverified_until_provenance_promotes_it(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        tier = re.search(
            r"<[^>]+\bid=[\"']certified-tier[\"'][^>]*>", html, re.IGNORECASE
        )
        status = re.search(
            r"<output[^>]+\bid=[\"']certified-tier-status[\"'][^>]*>"
            r"(?P<text>.*?)</output>",
            html,
            re.IGNORECASE | re.DOTALL,
        )
        self.assertIsNotNone(tier, "certified evidence tier is missing")
        self.assertIsNotNone(status, "certified evidence status is missing")
        initial_tag = tier.group(0).lower()
        initial_text = re.sub(r"<[^>]+>", "", status.group("text")).strip().lower()
        self.assertNotIn("is-certified", initial_tag)
        self.assertNotIn('data-state="verified"', initial_tag)
        self.assertNotIn("verified artifact", initial_text)

        app_source = (APP_DIR / "wind-tunnel.js").read_text(encoding="utf-8")
        self.assertIn("generatedFromVerifiedSources", app_source)
        self.assertIn("provenance", app_source)
        self.assertIn("completeVerifiedProvenance", app_source)
        canonical_keys = {
            "grouped_clock_floor", "grouped_library", "persistence",
            "state_atlas", "two_row_floor", "variational_atlas",
        }
        declared_keys = set(
            re.findall(
                r'"(grouped_clock_floor|grouped_library|persistence|state_atlas|two_row_floor|variational_atlas)"',
                app_source,
            )
        )
        self.assertEqual(declared_keys, canonical_keys)
        self.assertRegex(app_source, r"keys\.length\s*===\s*CERTIFIED_PROVENANCE_KEYS\.length")
        self.assertRegex(app_source, r"Object\.hasOwn\(provenance,\s*key\)")
        self.assertRegex(app_source, r"provenance\[key\]\.verified\s*===\s*true")

    def test_browser_sources_have_no_network_runtime_or_remote_dependencies(self) -> None:
        source_files = [
            INDEX,
            APP_DIR / "wind-tunnel.css",
            APP_DIR / "wind-tunnel-data.js",
            APP_DIR / "wind-tunnel-core.js",
            APP_DIR / "ensemble-worker.js",
            APP_DIR / "wind-tunnel.js",
        ]
        self.assertTrue(source_files)
        for path in source_files:
            self.assertTrue(path.is_file(), f"missing browser asset {path.name}")
        remote_url = re.compile(r"(?:https?:)?//[^\s'\"<>)]+", re.IGNORECASE)
        network_api = re.compile(
            r"\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\s*\("
        )
        import_scripts = re.compile(r"\bimportScripts\s*\(([^)]*)\)")
        dynamic_import = re.compile(r"\bimport\s*\(")
        for path in source_files:
            text = path.read_text(encoding="utf-8")
            # createElementNS requires this literal namespace identifier; it
            # is not dereferenced and therefore is not a network dependency.
            dependency_text = text.replace("http://www.w3.org/2000/svg", "")
            self.assertIsNone(
                remote_url.search(dependency_text), f"remote URL in {path.name}"
            )
            if path.suffix == ".js":
                self.assertIsNone(
                    network_api.search(text), f"network API in {path.name}"
                )
                worker_imports = import_scripts.findall(text)
                if path.name == "ensemble-worker.js":
                    self.assertEqual(
                        worker_imports,
                        ['"./wind-tunnel-core.js"'],
                        "worker may import only the committed local core",
                    )
                else:
                    self.assertEqual(
                        worker_imports, [], f"unexpected worker import in {path.name}"
                    )
                self.assertIsNone(
                    dynamic_import.search(text), f"dynamic import in {path.name}"
                )


if __name__ == "__main__":
    unittest.main()
