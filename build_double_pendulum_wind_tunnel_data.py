"""Build the compact, provenance-linked data bundle for the OIG wind tunnel.

The browser never pretends to reproduce the expensive Arb certificates.  This
builder verifies (when requested), hashes, and extracts the publication-safe
parts of the committed artifacts into one deterministic JavaScript bundle.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "website" / "double-pendulum-oig-wind-tunnel"
DEFAULT_OUTPUT = WEB_DIR / "wind-tunnel-data.js"

ARTIFACTS = {
    "state_atlas": ROOT / "artifacts" / "double_pendulum_operational_atlas_stage1.json",
    "variational_atlas": ROOT / "artifacts" / "double_pendulum_variational_atlas_13x13_t4_tier1.json",
    "persistence": ROOT / "artifacts" / "double_pendulum_persistence_13x13_t4_tier1.json",
    "grouped_library": ROOT / "artifacts" / "double_pendulum_grouped_protocol_tier1.json",
    "two_row_floor": ROOT / "artifacts" / "double_pendulum_physical_positive_floor.json",
    "grouped_clock_floor": ROOT / "artifacts" / "double_pendulum_grouped_physical_clock_floor.json",
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path.name} must contain a JSON object")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction_decimal(text: str) -> float:
    numerator, denominator = text.split("/", 1)
    return int(numerator) / int(denominator)


def _threshold_row(rows: list[dict[str, Any]], comparison: str, threshold: float) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in rows:
        record = row.get(comparison)
        if not isinstance(record, dict):
            continue
        overlaps = record.get("threshold_overlap")
        if not isinstance(overlaps, list):
            continue
        match = next(
            (item for item in overlaps if float(item.get("threshold", -1.0)) == threshold),
            None,
        )
        if match is None:
            continue
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


def _candidate_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for row in report["scalar_observation_library"]:
        exact = row["declared_rational_point"]
        result.append(
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
    return result


def _artifact_verifiers() -> dict[str, Callable[[dict[str, Any]], dict[str, Any]]]:
    from oig_double_pendulum_grouped_protocol import verify_grouped_protocol_report
    from oig_double_pendulum_grouped_validated_transfer import (
        verify_grouped_physical_clock_floor_certificate,
    )
    from oig_double_pendulum_lab import verify_atlas_lab_report
    from oig_double_pendulum_persistence import verify_persistence_report
    from oig_double_pendulum_validated_transfer import (
        verify_physical_positive_floor_certificate,
    )
    from oig_double_pendulum_variational_atlas import (
        verify_variational_angle_slice_atlas_report,
    )

    return {
        "state_atlas": verify_atlas_lab_report,
        "variational_atlas": verify_variational_angle_slice_atlas_report,
        "persistence": verify_persistence_report,
        "grouped_library": verify_grouped_protocol_report,
        "two_row_floor": verify_physical_positive_floor_certificate,
        "grouped_clock_floor": verify_grouped_physical_clock_floor_certificate,
    }


def build_payload(*, verify_sources: bool = False) -> dict[str, Any]:
    reports = {name: _load(path) for name, path in ARTIFACTS.items()}
    verification: dict[str, Any] = {}
    if verify_sources:
        verifiers = _artifact_verifiers()
        if set(verifiers) != set(ARTIFACTS):
            missing = sorted(set(ARTIFACTS) - set(verifiers))
            extra = sorted(set(verifiers) - set(ARTIFACTS))
            raise ValueError(f"artifact verifier coverage mismatch: missing={missing}, extra={extra}")
        for name, verifier in verifiers.items():
            outcome = verifier(reports[name])
            if outcome.get("passed") is not True:
                raise ValueError(f"source artifact {name} did not verify: {outcome}")
            verification[name] = outcome

    state = reports["state_atlas"]
    variation = reports["variational_atlas"]
    persistence = reports["persistence"]
    grouped = reports["grouped_library"]
    two_row = reports["two_row_floor"]
    clock = reports["grouped_clock_floor"]

    grouped_floor = clock["theorem"]["sharp_physical_clock_profiled_floor_lower_exact"]
    two_row_floor = two_row["robust_physical_floor_lower_exact"]
    payload = {
        "schemaVersion": "oig-double-pendulum-wind-tunnel-data-v1",
        "generatedFromVerifiedSources": verify_sources,
        "provenance": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": _sha256(path),
                "verified": verification.get(name, {}).get("passed", False),
            }
            for name, path in ARTIFACTS.items()
        },
        "stateAtlas": {
            "parameters": state["parameters"],
            "run": state["run"],
            "summary": state["atlas_summary"],
            "acceptanceStatus": state["acceptance_status"],
            "resolvedCellCount": state["resolved_cell_count"],
            "unresolvedCellCount": state["unresolved_cell_count"],
            "maxEnergyDrift": state["maximum_sampled_scaled_energy_drift"],
            "fields": {
                "logStretch": state["raw_fields"]["grid_edge_log_stretch"],
                "initialEnergy": state["raw_fields"]["initial_energy"],
                "lowStretchMask": state["raw_fields"]["resolved_low_stretch_no_sampled_full_turn_mask"],
                "componentLabels": state["raw_fields"]["connected_region_labels"],
            },
            "proofBoundary": state["proof_boundary"],
        },
        "variationalAtlas": {
            "angles1": variation["grid"]["theta1_centres"],
            "angles2": variation["grid"]["theta2_centres"],
            "summary": variation["summary"],
            "fields": {
                "weakestGain": variation["fields"]["selected_weakest_local_gain"],
                "strongestGain": variation["fields"]["selected_strongest_local_gain"],
                "resolvedMask": variation["fields"]["resolved_mask"],
            },
            "proofBoundary": variation["proof_boundary"],
        },
        "persistence": {
            "threshold": persistence["config"]["reference_threshold"],
            "resolution": _threshold_row(
                persistence["resolution_study"]["runs"],
                "comparison_to_highest_resolution",
                0.5,
            ),
            "shifts": _threshold_row(
                persistence["shift_study"]["runs"],
                "comparison_to_unshifted",
                0.5,
            ),
            "cadence": _threshold_row(
                persistence["cadence_study"]["runs"],
                "comparison_to_densest",
                0.5,
            ),
            "energyAssociation": persistence["baseline_energy_association"],
            "proofBoundary": persistence["proof_boundary"],
        },
        "candidateLibrary": {
            "sourceCoordinates": ["u = log(m2/m1)", "v = log(l2/l1)"],
            "rows": _candidate_rows(grouped),
            "groups": grouped["grouped_protocol_library"],
            "selected": grouped["selected_designs"]["cost_weighted_clock_only"],
            "minimumWitness": grouped["selected_designs"]["minimum_clock_only"],
            "proofBoundary": grouped["proof_boundary"],
        },
        "certificates": {
            "twoRowNoNuisance": {
                "floorExact": two_row_floor,
                "floorDecimal": _fraction_decimal(two_row_floor),
                "scopeFlags": two_row["scope_flags"],
                "scopeBoundary": two_row["scope_boundary"],
            },
            "groupedSharedClock": {
                "floorExact": grouped_floor,
                "floorDecimal": _fraction_decimal(grouped_floor),
                "simpleFloorExact": clock["theorem"]["simple_human_readable_floor_lower_exact"],
                "mixture": clock["fixed_grouped_mixture"],
                "boxSummary": clock["outward_box_summary"],
                "scopeFlags": clock["scope_flags"],
                "scopeBoundary": clock["scope_boundary"],
                "evidenceTier": clock["evidence_tier"],
            },
        },
        "interfaceBoundary": {
            "live": "Browser RK4 and local finite differences; immediate and falsifiable, not certified.",
            "refined": "Independent adaptive Dormand–Prince outcome and held-out perturbation checks.",
            "certified": "Committed outward Arb/Picard–Taylor boxes plus exact rational OIG verification for the fixed A+B model experiment only.",
        },
    }
    return payload


def render_javascript(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return (
        "/* Generated by build_double_pendulum_wind_tunnel_data.py; do not edit. */\n"
        "(function(root){\"use strict\";const data="
        + encoded
        + ";if(typeof module!==\"undefined\"&&module.exports){module.exports=data;}"
        "else{root.OIGWindTunnelData=data;}})(typeof globalThis!==\"undefined\"?globalThis:this);\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify-sources", action="store_true")
    parser.add_argument("--check", action="store_true", help="fail if the output is stale")
    args = parser.parse_args()
    rendered = render_javascript(build_payload(verify_sources=args.verify_sources))
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"stale wind-tunnel bundle: {args.output}")
        print(f"fresh: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.output} ({len(rendered)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
