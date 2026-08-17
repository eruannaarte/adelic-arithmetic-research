#!/usr/bin/env python3
"""Derive an exact distinguishability-radius bracket from Arithmetic Sensing V.

This checker does not redo the expensive Arb reconstruction.  It consumes the
already formal AS-V artifact, pins its file and formal-certificate digests, and
checks the exact-rational bridge consequence independently.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path


SCHEMA = "arithmetic-observability-asv-fibre-bridge-v1"
EXPECTED_SOURCE_SCHEMA = "arithmetic-sensing-v-time-ensemble-v1"
EXPECTED_FORMAL_DIGEST = "89b316584d9179c13232ad99b9515067fdf67329e6df3db4c48220d6b8c3ff7b"


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def _sha256_payload(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sqrt_decimal(
    value: Fraction,
    *,
    direction: str,
    significant_digits: int = 17,
    work_digits: int = 50,
) -> str:
    if direction not in {"lower", "upper"}:
        raise ValueError("decimal direction must be lower or upper")
    with localcontext() as context:
        context.prec = work_digits
        decimal_value = Decimal(value.numerator) / Decimal(value.denominator)
        root = decimal_value.sqrt()
        quantum = Decimal(1).scaleb(root.adjusted() - significant_digits + 1)
        rounding = ROUND_FLOOR if direction == "lower" else ROUND_CEILING
        outward = root.quantize(quantum, rounding=rounding)
        exact_candidate = Fraction(outward)
        exact_step = Fraction(quantum.copy_abs())
        if direction == "lower":
            while exact_candidate * exact_candidate > value:
                exact_candidate -= exact_step
        else:
            while exact_candidate * exact_candidate < value:
                exact_candidate += exact_step
        outward = Decimal(exact_candidate.numerator) / Decimal(exact_candidate.denominator)
        return format(outward, f".{significant_digits - 1}e")


def derive_payload(source_path: Path) -> dict[str, object]:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if source.get("schema") != EXPECTED_SOURCE_SCHEMA:
        raise ValueError("unexpected source schema")
    declared_formal_digest = source.get("formal_certificate_sha256")
    if declared_formal_digest != EXPECTED_FORMAL_DIGEST:
        raise ValueError("unexpected AS-V formal certificate digest")
    certificate = source.get("certificate")
    if not isinstance(certificate, dict):
        raise ValueError("missing AS-V certificate")
    if _sha256_payload(certificate) != declared_formal_digest:
        raise ValueError("AS-V certificate content digest mismatch")
    parameters = certificate["parameters"]
    if (
        parameters["degree"],
        parameters["maximum_norm"],
        parameters["sigma"],
        parameters["distinct_sample_count"],
    ) != (14, 50, 2, 8900):
        raise ValueError("unexpected AS-V model parameters")

    consequence = certificate["consequence"]
    gram = certificate["gram"]
    if not consequence["integer_rounding_certificate"]:
        raise ValueError("source artifact does not certify integer rounding")
    tail_bound = Fraction(consequence["coefficient_bound"])
    row_defect = Fraction(gram["maximum_row_upper"])
    if not Fraction(0) <= tail_bound < Fraction(1, 2):
        raise ValueError("tail consequence must be below one half")
    if not Fraction(0) <= row_defect < 1:
        raise ValueError("Gram row defect must be below one")

    maximum_norm = parameters["maximum_norm"]
    sigma = parameters["sigma"]
    margin = 1 - 2 * tail_bound
    coefficient_scale_squared = Fraction(maximum_norm ** (2 * sigma))
    separation_lower_squared = margin * margin * (1 - row_defect) / coefficient_scale_squared
    robust_radius_lower_squared = separation_lower_squared / 4
    separation_upper_squared = Fraction(1, maximum_norm ** (2 * sigma))
    robust_radius_upper_squared = separation_upper_squared / 4

    return {
        "source": {
            "path_basename": source_path.name,
            "file_sha256": _sha256_file(source_path),
            "formal_certificate_sha256": source["formal_certificate_sha256"],
            "schema": source["schema"],
        },
        "parameters": {
            "degree": parameters["degree"],
            "maximum_norm": maximum_norm,
            "sigma": sigma,
            "distinct_sample_count": parameters["distinct_sample_count"],
            "admissible_prefixes": (
                "nonnegative integer vectors coefficientwise dominated by d_14 through N"
            ),
            "admissible_tails": "coefficientwise dominated by d_14 as in the source artifact",
        },
        "exact_inputs": {
            "tail_reconstruction_bound": _fraction_text(tail_bound),
            "twice_tail_margin": _fraction_text(margin),
            "maximum_gram_row_defect_upper": _fraction_text(row_defect),
        },
        "exact_consequence": {
            "inter_fibre_distance_lower_squared": _fraction_text(separation_lower_squared),
            "robust_noise_radius_lower_squared": _fraction_text(robust_radius_lower_squared),
            "inter_fibre_distance_upper_squared": _fraction_text(separation_upper_squared),
            "robust_noise_radius_upper_squared": _fraction_text(robust_radius_upper_squared),
            "lower_distance_decimal": _sqrt_decimal(
                separation_lower_squared, direction="lower"
            ),
            "lower_radius_decimal": _sqrt_decimal(
                robust_radius_lower_squared, direction="lower"
            ),
            "upper_distance_decimal": _sqrt_decimal(
                separation_upper_squared, direction="upper"
            ),
            "upper_radius_decimal": _sqrt_decimal(
                robust_radius_upper_squared, direction="upper"
            ),
        },
        "logic": {
            "lower": "(1-2B)^2(1-q)/N^(2 sigma)",
            "upper": "two zero-tail prefixes differing by one unit at n=N",
            "status": "certified bracket, not the exact closest-fibre distance",
        },
    }


def build_artifact(source_path: Path) -> dict[str, object]:
    payload = derive_payload(source_path)
    return {"schema": SCHEMA, "payload": payload, "payload_sha256": _sha256_payload(payload)}


def verify_artifact(artifact_path: Path, source_path: Path) -> dict[str, object]:
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if set(artifact) != {"schema", "payload", "payload_sha256"}:
        raise ValueError("unexpected bridge artifact fields")
    if artifact["schema"] != SCHEMA:
        raise ValueError("unexpected bridge schema")
    if artifact["payload_sha256"] != _sha256_payload(artifact["payload"]):
        raise ValueError("bridge payload digest mismatch")
    expected = derive_payload(source_path)
    if _canonical_json(artifact["payload"]) != _canonical_json(expected):
        raise ValueError("bridge artifact differs from exact reconstruction")
    return {
        "verified": True,
        "schema": SCHEMA,
        "payload_sha256": artifact["payload_sha256"],
        "lower_radius_decimal": expected["exact_consequence"]["lower_radius_decimal"],
        "upper_radius_decimal": expected["exact_consequence"]["upper_radius_decimal"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("certificates/arithmetic_sensing_v_multiscale_end_to_end.json"),
    )
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify is not None:
        result = verify_artifact(args.verify, args.source)
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    artifact = build_artifact(args.source)
    rendered = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    if args.write is None:
        print(rendered, end="")
    else:
        args.write.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
