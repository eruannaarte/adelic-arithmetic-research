#!/usr/bin/env python3
"""Compact demonstration of model-aware quotient robustness certificates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from oig_robust_model_quotient import (
    certify_combined_model_design,
    certify_nominal_blind_uncertainty,
    certify_quotient_tube_pair,
    certify_response_tube_pair,
    certify_tangent_kernel_angle,
    verify_robust_model_report,
)


DEMO_SECANT_PROVENANCE = "the demo model is the declared two-point codebook with this sole nonzero secant"


def _build_demo_payload() -> dict[str, object]:
    response = [[1, 0, 0], [0, 1, 0]]
    source_metric = [[1, 0, 0], [0, 4, 0], [0, 0, 9]]
    output_metric = [[1, 0], [0, 1]]
    secant = [3, 4, 5]
    tangent = [[1, 0], [0, 1], [1, 1]]
    response_radius = [[0, 0, "1/100"], [0, 0, "1/50"]]
    aggregate_information = [[1, 0, 0], [0, 1, 0], [0, 0, 0]]

    return {
        "schema_version": "oig-robust-model-quotient-demo-v1",
        "pair_quotient_tube": certify_quotient_tube_pair(
            response,
            source_metric,
            secant,
            source_radius=1,
            quotient_noise_radius="1/2",
        ),
        "pair_raw_tube": certify_response_tube_pair(
            response,
            source_metric,
            output_metric,
            secant,
            source_radius=1,
            data_noise_radius=1,
        ),
        "tangent_angle": certify_tangent_kernel_angle(
            response, source_metric, tangent
        ),
        "nominal_null": certify_nominal_blind_uncertainty(
            response,
            response_radius,
            source_metric,
            output_metric,
            blind_source_radius=2,
            query_matrix=[[1, 0, 0]],
            model_secants=[secant],
            model_secants_exhaustive=True,
            model_secants_provenance=DEMO_SECANT_PROVENANCE,
        ),
        "combined_target": certify_combined_model_design(
            response,
            source_metric,
            aggregate_information,
            [secant],
            [tangent],
            response_radius=response_radius,
            output_metric=output_metric,
            blind_source_radius=2,
            query_matrix=[[1, 0, 0]],
            model_secants_exhaustive=True,
            model_secants_provenance=DEMO_SECANT_PROVENANCE,
        ),
    }


def verify_robust_model_demo_report(report: dict[str, object]) -> dict[str, object]:
    """Verify every serialized component and their common demo declarations."""
    try:
        if type(report) is not dict:
            raise TypeError("demo report must be a JSON object")
        if report.get("schema_version") != "oig-robust-model-quotient-demo-v1":
            raise ValueError("unknown robust model demo schema")
        components = (
            "pair_quotient_tube",
            "pair_raw_tube",
            "tangent_angle",
            "nominal_null",
            "combined_target",
        )
        allowed = {"schema_version", *components, "independent_verification"}
        extra = set(report) - allowed
        missing = {"schema_version", *components} - set(report)
        if extra or missing:
            raise ValueError(f"demo field mismatch missing={sorted(missing)} extra={sorted(extra)}")
        for name in components:
            verification = verify_robust_model_report(report[name])
            if verification.get("passed") is not True:
                raise ValueError(f"{name} failed: {verification.get('error')}")

        quotient_pair = report["pair_quotient_tube"]
        raw_pair = report["pair_raw_tube"]
        tangent = report["tangent_angle"]
        blind = report["nominal_null"]
        combined = report["combined_target"]
        if not (
            quotient_pair["response_exact"]
            == raw_pair["response_exact"]
            == tangent["response_exact"]
            == blind["response_centre_exact"]
            == combined["response_exact"]
        ):
            raise ValueError("demo response declarations are incoherent")
        if not (
            quotient_pair["source_metric_exact"]
            == raw_pair["source_metric_exact"]
            == tangent["source_metric_exact"]
            == blind["source_metric_exact"]
            == combined["source_metric_exact"]
        ):
            raise ValueError("demo source metrics are incoherent")
        if not (
            raw_pair["output_metric_exact"]
            == blind["output_metric_exact"]
            == combined["output_metric_exact"]
        ):
            raise ValueError("demo output metrics are incoherent")
        if quotient_pair["secant_exact"] != combined["model_secants_exact"][0]:
            raise ValueError("demo pair is not the combined model secant")
        if tangent["tangent_basis_exact"] != combined["tangent_bases_exact"][0]:
            raise ValueError("demo tangent is not the combined tangent")
        if blind["response_radius_exact"] != combined["response_radius_exact"]:
            raise ValueError("demo response-radius declarations are incoherent")
        if blind["query_matrix_exact"] != combined["query_matrix_exact"]:
            raise ValueError("demo query declarations are incoherent")

        result = {
            "passed": True,
            "schema_version": "oig-robust-model-quotient-demo-verification-v1",
            "components_verified": list(components),
            "method": "strict per-schema exact reconstruction plus cross-component declaration checks",
        }
        embedded = report.get("independent_verification")
        if embedded is not None:
            if json.dumps(embedded, sort_keys=True, separators=(",", ":")) != json.dumps(
                result, sort_keys=True, separators=(",", ":")
            ):
                raise ValueError("embedded demo verification block is inconsistent")
        return result
    except Exception as error:
        return {"passed": False, "error": str(error)}


def run_demo() -> dict[str, object]:
    report = _build_demo_payload()
    verification = verify_robust_model_demo_report(report)
    if verification.get("passed") is not True:
        raise AssertionError(f"demo self-verification failed: {verification}")
    report["independent_verification"] = verification
    final_verification = verify_robust_model_demo_report(report)
    if final_verification.get("passed") is not True:
        raise AssertionError(f"embedded demo verification failed: {final_verification}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--output", help="write a newly generated self-verified JSON report")
    actions.add_argument("--verify", help="strictly verify an existing JSON report")
    args = parser.parse_args()
    if args.verify:
        with open(args.verify, "r", encoding="utf-8") as handle:
            report = json.load(handle)
        verification = verify_robust_model_demo_report(report)
        print(json.dumps(verification, indent=2, sort_keys=True))
        if verification.get("passed") is not True:
            raise SystemExit(1)
        return
    report = run_demo()
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
