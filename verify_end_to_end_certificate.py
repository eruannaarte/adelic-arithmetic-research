#!/usr/bin/env python3
"""Build or check the end-to-end Arithmetic Sensing V certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from fractions import Fraction
from pathlib import Path
from typing import Sequence

import flint

from verified_end_to_end_certificate import (
    verified_end_to_end_bound,
    verified_finite_tail_bounds,
    verified_gram_row_bound,
)
from verify_mellin_certificate import verify_artifact as verify_remote_artifact


SCHEMA = "arithmetic-sensing-v-end-to-end-v1"
ROOT = Path(__file__).resolve().parent
DEFAULT_REMOTE_ARTIFACT = (
    ROOT / "certificates" / "arithmetic_sensing_v_cancellation_frontier.json"
)
DEFAULT_ARTIFACT = (
    ROOT / "certificates" / "arithmetic_sensing_v_end_to_end.json"
)


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _payload_digest(payload: dict[str, object]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode()).hexdigest()


def _load_verified_remote(path: Path) -> tuple[dict[str, object], str]:
    with path.open(encoding="utf-8") as handle:
        artifact = json.load(handle)
    certificate = artifact.get("certificate")
    if not isinstance(certificate, dict):
        raise ValueError("remote artifact has no certificate payload")
    result = verify_remote_artifact(artifact, certificate)
    parameters = certificate.get("parameters")
    if not isinstance(parameters, dict) or parameters.get(
        "kernel_bound_method"
    ) != "cancellation":
        raise ValueError("end-to-end certificate requires cancellation bounds")
    return certificate, str(result["formal_certificate_sha256"])


def _remote_degree_map(
    certificate: dict[str, object], degrees: Sequence[int]
) -> dict[int, dict[str, object]]:
    entries = certificate.get("degrees")
    if not isinstance(entries, list):
        raise ValueError("remote artifact has no degree list")
    mapping = {
        int(entry["degree"]): entry
        for entry in entries
        if isinstance(entry, dict) and "degree" in entry
    }
    missing = [degree for degree in degrees if degree not in mapping]
    if missing:
        raise ValueError(f"remote artifact is missing degrees {missing}")
    return mapping


def build_certificate(
    degrees: Sequence[int] = (13, 14),
    remote_artifact_path: Path = DEFAULT_REMOTE_ARTIFACT,
    maximum_norm: int = 50,
    truncation: int = 1_000_000,
    observation_time: int = 1_000,
    sample_count: int = 5_000,
    arb_precision: int = 128,
    output_scale_bits: int = 128,
    processes: int | None = None,
) -> dict[str, object]:
    """Recompute every finite ball sum and its inverse-free consequence."""
    if not degrees or any(degree < 1 for degree in degrees):
        raise ValueError("at least one positive degree is required")
    remote, remote_digest = _load_verified_remote(remote_artifact_path)
    remote_parameters = remote.get("parameters")
    if not isinstance(remote_parameters, dict):
        raise ValueError("remote parameters are missing")
    expected = {
        "maximum_norm": maximum_norm,
        "truncation": truncation,
        "observation_time": observation_time,
        "sample_count": sample_count,
        "sigma": 2,
    }
    for name, value in expected.items():
        if remote_parameters.get(name) != value:
            raise ValueError(f"remote parameter {name} does not match")
    remote_degrees = _remote_degree_map(remote, degrees)
    gram = verified_gram_row_bound(
        maximum_norm,
        observation_time,
        sample_count,
        precision=max(arb_precision, 160),
        output_scale_bits=output_scale_bits,
    )
    degree_payloads: list[dict[str, object]] = []
    for degree in degrees:
        finite = verified_finite_tail_bounds(
            degree,
            maximum_norm,
            truncation,
            observation_time,
            sample_count,
            precision=arb_precision,
            output_scale_bits=output_scale_bits,
            processes=processes,
        )
        remote_entry = remote_degrees[degree]
        remote_numerators = tuple(
            int(value) for value in remote_entry["remote_target_numerators"]
        )
        remote_scale_bits = int(remote_entry["remote_output_scale_bits"])
        result = verified_end_to_end_bound(
            finite,
            remote_numerators,
            remote_scale_bits,
            gram,
        )
        degree_payloads.append(
            {
                "degree": degree,
                "coefficient_sha256": finite.coefficient_sha256,
                "finite_sha256": finite.finite_sha256,
                "finite_output_scale_bits": finite.scale_bits,
                "finite_target_numerators": [
                    str(value) for value in finite.numerators
                ],
                "finite_upper_at_target_1": str(finite.upper_fraction(1)),
                "finite_upper_at_target_10": str(finite.upper_fraction(10)),
                "finite_upper_at_target_50": str(finite.upper_fraction(50)),
                "remote_sha256": remote_entry["remote_sha256"],
                "maximum_complete_tail": str(result.maximum_tail),
                "worst_tail_target": result.worst_tail_target,
                "coefficient_bound": str(result.coefficient_bound),
                "coefficient_bound_decimal": float(result.coefficient_bound),
                "worst_coefficient_target": (
                    result.worst_coefficient_target
                ),
                "integer_rounding_certificate": (
                    result.integer_rounding_certificate
                ),
            }
        )
    return {
        "scope": (
            "end-to-end Arb finite-tail and inverse-free Gram certificate, "
            "composed with the separately reconstructible directed-MPFR "
            "cancellation artifact"
        ),
        "parameters": {
            "maximum_norm": maximum_norm,
            "sigma": 2,
            "observation_time": observation_time,
            "sample_count": sample_count,
            "truncation": truncation,
            "arb_precision_bits": arb_precision,
            "finite_output_scale_bits": output_scale_bits,
        },
        "remote_dependency": {
            "artifact_name": remote_artifact_path.name,
            "formal_certificate_sha256": remote_digest,
        },
        "gram": {
            "arb_precision_bits": gram.arb_precision,
            "output_scale_bits": gram.scale_bits,
            "row_numerators": [str(value) for value in gram.row_numerators],
            "maximum_row_numerator": str(gram.numerator),
            "maximum_row_upper": str(gram.upper_fraction),
            "sha256": gram.sha256,
            "neumann_inverse_norm_upper": str(
                Fraction(1, 1) / (1 - gram.upper_fraction)
            ),
        },
        "degrees": degree_payloads,
    }


def artifact_document(certificate: dict[str, object]) -> dict[str, object]:
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
        raise ValueError("unknown end-to-end certificate schema")
    stored = artifact.get("certificate")
    if not isinstance(stored, dict):
        raise ValueError("artifact has no certificate object")
    stored_digest = artifact.get("formal_certificate_sha256")
    if stored_digest != _payload_digest(stored):
        raise ValueError("stored end-to-end certificate hash is invalid")
    recomputed_digest = _payload_digest(recomputed)
    if stored_digest != recomputed_digest or stored != recomputed:
        raise ValueError("recomputed certificate does not match the artifact")
    return {
        "verified": True,
        "schema": SCHEMA,
        "formal_certificate_sha256": recomputed_digest,
        "runtime": {"python_flint": flint.__version__},
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument(
        "--remote-certificate", type=Path, default=DEFAULT_REMOTE_ARTIFACT
    )
    parser.add_argument("--degrees", default="13,14")
    parser.add_argument("--processes", type=int)
    parser.add_argument("--observation-time", type=int, default=1_000)
    parser.add_argument("--sample-count", type=int, default=5_000)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--write", type=Path)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    degrees = tuple(int(value) for value in arguments.degrees.split(","))
    started = time.perf_counter()
    certificate = build_certificate(
        degrees,
        arguments.remote_certificate,
        observation_time=arguments.observation_time,
        sample_count=arguments.sample_count,
        processes=arguments.processes,
    )
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
