#!/usr/bin/env python3
"""Build or check the formal degree-fourteen time-ensemble certificate."""

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
    VerifiedTimeComponent,
    verified_end_to_end_bound,
    verified_ensemble_finite_tail_bounds,
    verified_ensemble_gram_row_bound,
)
from verify_mellin_certificate import verify_artifact as verify_remote_artifact


SCHEMA = "arithmetic-sensing-v-time-ensemble-v1"
DIRECTORY = Path(__file__).resolve().parent
SHORT_REMOTE_ARTIFACT = (
    DIRECTORY
    / "certificates"
    / "arithmetic_sensing_v_time_ensemble_T500_remote.json"
)
LONG_REMOTE_ARTIFACT = (
    DIRECTORY
    / "certificates"
    / "arithmetic_sensing_v_time_ensemble_T1790_remote.json"
)
DEFAULT_ARTIFACT = (
    DIRECTORY
    / "certificates"
    / "arithmetic_sensing_v_time_ensemble_end_to_end.json"
)
REFERENCE_COMPONENTS = (
    VerifiedTimeComponent(500, 2_500, Fraction(7, 4_096)),
    VerifiedTimeComponent(1_790, 8_950, Fraction(4_089, 4_096)),
)


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _payload_digest(payload: dict[str, object]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode()).hexdigest()


def _dyadic_ceiling(value: Fraction, scale_bits: int) -> int:
    scaled_numerator = value.numerator << scale_bits
    return (scaled_numerator + value.denominator - 1) // value.denominator


def centered_grid_inclusion_offset(
    inner: VerifiedTimeComponent,
    outer: VerifiedTimeComponent,
) -> int:
    """Prove that one centered midpoint grid is a contiguous outer subset."""
    inner_spacing = Fraction(inner.observation_time, inner.sample_count)
    outer_spacing = Fraction(outer.observation_time, outer.sample_count)
    difference = outer.sample_count - inner.sample_count
    if (
        inner_spacing != outer_spacing
        or difference < 0
        or difference % 2
    ):
        raise ValueError("centered midpoint grids are not exactly nested")
    return difference // 2


def _load_remote(
    path: Path,
    component: VerifiedTimeComponent,
    degree: int,
    maximum_norm: int,
    truncation: int,
) -> tuple[dict[str, object], str]:
    with path.open(encoding="utf-8") as handle:
        artifact = json.load(handle)
    certificate = artifact.get("certificate")
    if not isinstance(certificate, dict):
        raise ValueError("remote artifact has no certificate payload")
    result = verify_remote_artifact(artifact, certificate)
    parameters = certificate.get("parameters")
    if not isinstance(parameters, dict):
        raise ValueError("remote artifact parameters are missing")
    expected = {
        "maximum_norm": maximum_norm,
        "truncation": truncation,
        "observation_time": component.observation_time,
        "sample_count": component.sample_count,
        "sigma": 2,
        "kernel_bound_method": "cancellation",
    }
    for name, value in expected.items():
        if parameters.get(name) != value:
            raise ValueError(f"remote parameter {name} does not match")
    entries = certificate.get("degrees")
    if not isinstance(entries, list):
        raise ValueError("remote degree list is missing")
    matches = [
        entry
        for entry in entries
        if isinstance(entry, dict) and entry.get("degree") == degree
    ]
    if len(matches) != 1:
        raise ValueError("remote artifact does not contain the requested degree")
    return matches[0], str(result["formal_certificate_sha256"])


def _combine_remote_entries(
    entries: Sequence[dict[str, object]],
    components: Sequence[VerifiedTimeComponent],
    maximum_norm: int,
    output_scale_bits: int,
) -> tuple[int, ...]:
    if len(entries) != len(components):
        raise ValueError("remote entries and time components disagree")
    results = []
    for target_index in range(maximum_norm):
        value = Fraction()
        for entry, component in zip(entries, components):
            numerators = entry["remote_target_numerators"]
            scale_bits = int(entry["remote_output_scale_bits"])
            value += component.weight * Fraction(
                int(numerators[target_index]), 1 << scale_bits
            )
        results.append(_dyadic_ceiling(value, output_scale_bits))
    return tuple(results)


def build_certificate(
    components: Sequence[VerifiedTimeComponent] = REFERENCE_COMPONENTS,
    remote_paths: Sequence[Path] = (
        SHORT_REMOTE_ARTIFACT,
        LONG_REMOTE_ARTIFACT,
    ),
    degree: int = 14,
    maximum_norm: int = 50,
    truncation: int = 1_000_000,
    arb_precision: int = 128,
    output_scale_bits: int = 128,
    processes: int | None = None,
) -> dict[str, object]:
    """Recompute the finite, Gram, and conservative remote composition."""
    ensemble = tuple(components)
    if len(ensemble) != len(remote_paths):
        raise ValueError("one remote artifact is required per time component")
    outer_index = max(
        range(len(ensemble)),
        key=lambda index: ensemble[index].observation_time,
    )
    outer = ensemble[outer_index]
    inclusion_offsets = [
        centered_grid_inclusion_offset(component, outer)
        for component in ensemble
    ]
    loaded = [
        _load_remote(
            path,
            component,
            degree,
            maximum_norm,
            truncation,
        )
        for path, component in zip(remote_paths, ensemble)
    ]
    remote_entries = [entry for entry, _ in loaded]
    remote_numerators = _combine_remote_entries(
        remote_entries,
        ensemble,
        maximum_norm,
        output_scale_bits,
    )
    finite = verified_ensemble_finite_tail_bounds(
        degree,
        ensemble,
        maximum_norm,
        truncation,
        precision=arb_precision,
        output_scale_bits=output_scale_bits,
        processes=processes,
    )
    gram = verified_ensemble_gram_row_bound(
        ensemble,
        maximum_norm,
        precision=max(arb_precision, 160),
        output_scale_bits=output_scale_bits,
    )
    result = verified_end_to_end_bound(
        finite,
        remote_numerators,
        output_scale_bits,
        gram,
    )
    return {
        "scope": (
            "end-to-end Arb certificate for a positive centered time "
            "ensemble; signed finite and Gram responses are combined before "
            "absolute values, while remote MPFR bounds are combined by the "
            "triangle inequality"
        ),
        "parameters": {
            "degree": degree,
            "maximum_norm": maximum_norm,
            "sigma": 2,
            "truncation": truncation,
            "arb_precision_bits": arb_precision,
            "output_scale_bits": output_scale_bits,
            "component_sample_count_sum": sum(
                component.sample_count for component in ensemble
            ),
            "distinct_sample_count": outer.sample_count,
            "maximum_observation_time": max(
                component.observation_time for component in ensemble
            ),
            "common_sample_spacing": str(
                Fraction(outer.observation_time, outer.sample_count)
            ),
            "outer_component_index": outer_index,
            "centered_grid_inclusion_offsets": inclusion_offsets,
            "components": [
                {
                    "observation_time": component.observation_time,
                    "sample_count": component.sample_count,
                    "weight": str(component.weight),
                }
                for component in ensemble
            ],
        },
        "remote_dependencies": [
            {
                "artifact_name": path.name,
                "formal_certificate_sha256": digest,
            }
            for path, (_, digest) in zip(remote_paths, loaded)
        ],
        "combined_remote": {
            "output_scale_bits": output_scale_bits,
            "target_numerators": [str(value) for value in remote_numerators],
        },
        "finite": {
            "coefficient_sha256": finite.coefficient_sha256,
            "finite_sha256": finite.finite_sha256,
            "output_scale_bits": finite.scale_bits,
            "target_numerators": [str(value) for value in finite.numerators],
            "upper_at_target_1": str(finite.upper_fraction(1)),
            "upper_at_target_10": str(finite.upper_fraction(10)),
            "upper_at_target_50": str(finite.upper_fraction(50)),
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
        "consequence": {
            "maximum_complete_tail": str(result.maximum_tail),
            "worst_tail_target": result.worst_tail_target,
            "coefficient_bound": str(result.coefficient_bound),
            "coefficient_bound_decimal": float(result.coefficient_bound),
            "worst_coefficient_target": result.worst_coefficient_target,
            "integer_rounding_certificate": (
                result.integer_rounding_certificate
            ),
        },
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
        raise ValueError("unknown time-ensemble certificate schema")
    stored = artifact.get("certificate")
    if not isinstance(stored, dict):
        raise ValueError("artifact has no certificate object")
    stored_digest = artifact.get("formal_certificate_sha256")
    if stored_digest != _payload_digest(stored):
        raise ValueError("stored time-ensemble certificate hash is invalid")
    recomputed_digest = _payload_digest(recomputed)
    if stored_digest != recomputed_digest or stored != recomputed:
        raise ValueError("recomputed time-ensemble certificate does not match")
    return {
        "verified": True,
        "schema": SCHEMA,
        "formal_certificate_sha256": recomputed_digest,
        "runtime": {"python_flint": flint.__version__},
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--short-remote", type=Path, default=SHORT_REMOTE_ARTIFACT)
    parser.add_argument("--long-remote", type=Path, default=LONG_REMOTE_ARTIFACT)
    parser.add_argument("--processes", type=int)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--write", type=Path)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    started = time.perf_counter()
    certificate = build_certificate(
        remote_paths=(arguments.short_remote, arguments.long_remote),
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
