#!/usr/bin/env python3
"""Build or check the complete finite-mode support-stopping artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from fractions import Fraction
from pathlib import Path

import flint

from residual_stopping_envelope import build_stopping_report


SCHEMA = "arithmetic-sensing-v-residual-stopping-v1"
DIRECTORY = Path(__file__).resolve().parent
DEFAULT_ARTIFACT = (
    DIRECTORY
    / "certificates"
    / "arithmetic_sensing_v_residual_stopping.json"
)
ADAPTIVE_DIGEST = (
    "01d385eb6d02bc9302b4f161183e0ee097768109f949e750fc6ec67a38b1726f"
)
RECOVERY_DIGEST = (
    "89b316584d9179c13232ad99b9515067fdf67329e6df3db4c48220d6b8c3ff7b"
)


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _payload_digest(payload: dict[str, object]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode()).hexdigest()


def _validate_certificate(certificate: dict[str, object]) -> None:
    parameters = certificate.get("parameters")
    dependencies = certificate.get("dependencies")
    screen = certificate.get("selected_mode_screen")
    duals = certificate.get("full_tail_duals")
    consequence = certificate.get("consequence")
    if not all(
        isinstance(value, dict)
        for value in (parameters, dependencies, screen, consequence)
    ) or not isinstance(duals, list):
        raise ValueError("residual-stopping certificate sections are missing")
    assert isinstance(parameters, dict)
    assert isinstance(dependencies, dict)
    assert isinstance(screen, dict)
    assert isinstance(consequence, dict)
    if int(parameters["truncation"]) != 1_000_000:
        raise ValueError("residual certificate has the wrong truncation")
    candidate_times = tuple(
        int(value) for value in parameters["candidate_short_times"]
    )
    if candidate_times != tuple(range(300, 801, 10)):
        raise ValueError("candidate support grid is incorrect")
    survivor_times = tuple(int(value) for value in screen["survivor_times"])
    if survivor_times != (440, 480, 490, 500, 520):
        raise ValueError("selected-mode survivor set is incorrect")
    if int(screen["screened_support_count"]) != 45:
        raise ValueError("selected-mode screen count is incorrect")
    winner_upper = Fraction(consequence["published_full_finite_upper"])
    parsed_duals = []
    for value in duals:
        if not isinstance(value, dict):
            raise ValueError("full-tail dual entry is malformed")
        special = Fraction(value["special_dual_value"])
        short_lower = Fraction(value["short_score_lower"])
        outer_lower = Fraction(value["outer_score_lower"])
        complete = Fraction(value["complete_dual_lower"])
        if abs(special) > 1:
            raise ValueError("special dual value lies outside [-1,1]")
        if complete != min(short_lower, outer_lower):
            raise ValueError("full-tail dual minimum is incorrect")
        sign_hash = value.get("sign_sha256")
        if not isinstance(sign_hash, str) or len(sign_hash) != 64:
            raise ValueError("full-tail dual sign hash is malformed")
        parsed_duals.append((int(value["short_time"]), complete))
    if tuple(time_value for time_value, _ in parsed_duals) != survivor_times:
        raise ValueError("full-tail duals do not match the survivor set")
    closest_time, closest_lower = min(parsed_duals, key=lambda item: item[1])
    separation = closest_lower - winner_upper
    if closest_time != int(consequence["closest_competing_time"]):
        raise ValueError("closest full-tail competitor is incorrect")
    if closest_lower != Fraction(consequence["closest_competing_full_lower"]):
        raise ValueError("closest full-tail lower bound is incorrect")
    if separation != Fraction(consequence["full_support_separation"]):
        raise ValueError("full support separation is incorrect")
    if separation <= 0:
        raise ValueError("full-tail support separation is not strict")
    if consequence.get("all_competing_pair_supports_eliminated") is not True:
        raise ValueError("competitor-elimination flag is absent")
    if consequence.get("finite_mode_stopping_certificate") is not True:
        raise ValueError("finite stopping flag is absent")
    selected_dependency = dependencies.get("selected_mode_support_artifact")
    recovery_dependency = dependencies.get("published_full_finite_upper_artifact")
    if not isinstance(selected_dependency, dict) or not isinstance(
        recovery_dependency, dict
    ):
        raise ValueError("residual dependencies are malformed")
    if selected_dependency.get("formal_certificate_sha256") != ADAPTIVE_DIGEST:
        raise ValueError("adaptive dependency hash is incorrect")
    if recovery_dependency.get("formal_certificate_sha256") != RECOVERY_DIGEST:
        raise ValueError("recovery dependency hash is incorrect")


def build_certificate(processes: int | None = None) -> dict[str, object]:
    certificate = build_stopping_report(processes)
    _validate_certificate(certificate)
    return certificate


def artifact_document(certificate: dict[str, object]) -> dict[str, object]:
    _validate_certificate(certificate)
    return {
        "schema": SCHEMA,
        "producer": {"python_flint": flint.__version__},
        "formal_certificate_sha256": _payload_digest(certificate),
        "certificate": certificate,
    }


def verify_artifact(
    artifact: dict[str, object], recomputed: dict[str, object]
) -> dict[str, object]:
    if artifact.get("schema") != SCHEMA:
        raise ValueError("unknown residual-stopping certificate schema")
    stored = artifact.get("certificate")
    if not isinstance(stored, dict):
        raise ValueError("artifact has no certificate object")
    _validate_certificate(stored)
    _validate_certificate(recomputed)
    stored_digest = artifact.get("formal_certificate_sha256")
    if stored_digest != _payload_digest(stored):
        raise ValueError("stored residual-stopping hash is invalid")
    recomputed_digest = _payload_digest(recomputed)
    if stored_digest != recomputed_digest or stored != recomputed:
        raise ValueError("recomputed residual-stopping certificate differs")
    return {
        "verified": True,
        "schema": SCHEMA,
        "formal_certificate_sha256": recomputed_digest,
        "runtime": {"python_flint": flint.__version__},
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--processes", type=int)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--write", type=Path)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    started = time.perf_counter()
    certificate = build_certificate(arguments.processes)
    if arguments.emit or arguments.write is not None:
        result: dict[str, object] = artifact_document(certificate)
    else:
        with arguments.certificate.open(encoding="utf-8") as handle:
            artifact = json.load(handle)
        result = verify_artifact(artifact, certificate)
        result["elapsed_seconds"] = time.perf_counter() - started
    serialized = json.dumps(result, indent=2, sort_keys=True)
    if arguments.write is not None:
        arguments.write.parent.mkdir(parents=True, exist_ok=True)
        arguments.write.write_text(serialized + "\n", encoding="utf-8")
        print(
            json.dumps(
                {
                    "written": str(arguments.write),
                    "formal_certificate_sha256": result[
                        "formal_certificate_sha256"
                    ],
                    "elapsed_seconds": time.perf_counter() - started,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(serialized)


if __name__ == "__main__":
    main()
