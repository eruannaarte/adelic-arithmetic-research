#!/usr/bin/env python3
"""Pinned proof chain for the Arithmetic-Atlas protocol-engine integration.

The report composes four independently verified finite certificates:

* a finite library of query-compatible gain protocols;
* shared versus independently refit nuisance semantics;
* structured correlated additive nuisance; and
* model-aware quotient robustness.

It is a deterministic integration demonstrator, not a claim that the pinned
toy protocols exhaust any physical experiment family.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
from typing import Sequence

from oig_query_candidate_library import (
    QueryCandidate,
    certify_query_candidate_library,
    verify_query_candidate_library_report,
)
from oig_query_protocol_design import QueryProtocol
from oig_robust_model_quotient_demo import (
    run_demo as run_robust_demo,
    verify_robust_model_demo_report,
)
from oig_robust_model_quotient import (
    certify_response_tube_pair,
    verify_robust_model_report,
)
from oig_structured_nuisance import (
    certify_structured_nuisance_separation,
    demo_certificates as structured_nuisance_demo,
    verify_structured_nuisance_demo_report,
    verify_structured_nuisance_report,
)


SCHEMA_VERSION = "oig-atlas-protocol-integration-v1"


def _strict_json_equal(left: object, right: object) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            _strict_json_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            _strict_json_equal(a, b) for a, b in zip(left, right)
        )
    return left == right


def _gain_library() -> dict[str, object]:
    candidates = (
        QueryCandidate.single_model(
            "unit gain", [[1]], None, [[1]], [[1]], [[1]], [[1]]
        ),
        QueryCandidate.single_model(
            "double gain", [[2]], None, [[1]], [[1]], [[1]], [[1]]
        ),
        QueryCandidate.single_model(
            "blind control", [[0]], None, [[1]], [[1]], [[1]], [[1]]
        ),
    )
    return certify_query_candidate_library(candidates)


def _shared_nuisance_library() -> dict[str, object]:
    protocols = (
        QueryProtocol.from_rows("first", [[1]], [[1]], [[1]]),
        QueryProtocol.from_rows("second", [[2]], [[1]], [[1]]),
    )
    shared = QueryCandidate.shared_mixture(
        "one nuisance shared across protocols",
        protocols,
        ["1/2", "1/2"],
        [[1]],
        [[1]],
        [[1]],
    )
    independent = QueryCandidate.independent_mixture(
        "one nuisance refit per protocol",
        protocols,
        ["1/2", "1/2"],
        [[1]],
        [[1]],
        [[1]],
    )
    return certify_query_candidate_library((shared, independent))


def _build_payload() -> dict[str, object]:
    gain = _gain_library()
    nuisance_semantics = _shared_nuisance_library()
    structured = structured_nuisance_demo()
    robust = run_robust_demo()
    selected_structured = certify_structured_nuisance_separation(
        name="selected double-gain protocol against correlated differential nuisance",
        query_response=[2],
        generators=[[1]],
        coefficient_radii=["1/2"],
        primal_coefficients=["1/2"],
        dual_direction=[1],
    )
    selected_tube = certify_response_tube_pair(
        [[2]],
        [[1]],
        [[1]],
        [1],
        source_radius=0,
        data_noise_radius="1/2",
    )

    gain_selection = gain["selection"]
    nuisance_selection = nuisance_semantics["selection"]
    correlation = structured["correlation_control"]
    combined = robust["combined_target"]
    selected_child = gain["candidates"][
        gain_selection["selected_candidate_index"]
    ]["query_certificate"]
    selected_response = selected_child["declared_observation_exact"]
    selected_secant = selected_tube["secant_exact"]
    induced_value = (
        Fraction(selected_response[0][0]) * Fraction(selected_secant[0])
    )
    induced_response_difference = [
        f"{induced_value.numerator}/{induced_value.denominator}"
    ]
    ledger = {
        "gain_library_unique_winner": (
            gain_selection["selected_candidate_name"] == "double gain"
            and gain_selection["unique_winner_certified"] is True
        ),
        "shared_nuisance_is_identifiable_while_independent_refit_is_not": (
            nuisance_selection["selected_candidate_name"]
            == "one nuisance shared across protocols"
            and nuisance_semantics["identifiable_candidate_count"] == 1
        ),
        "structured_correlation_strictly_improves_support": (
            correlation["correlation_loss_exact"] == "2/1"
        ),
        "robust_geometry_obligations_pass": (
            combined["combined_target_passed"] is True
        ),
        "response_box_information_composition_remains_external": (
            "Response-box information-form loss remains an external certificate"
            in combined["warning"]
        ),
        "selected_protocol_declaration_is_shared_across_followthrough": (
            selected_response == selected_tube["response_exact"]
            == [["2/1"]]
            and selected_structured["problem"]["query_response_exact"]
            == induced_response_difference
            == ["2/1"]
        ),
        "selected_protocol_metrics_are_shared_across_followthrough": (
            selected_child["declared_source_metric_exact"]
            == selected_tube["source_metric_exact"]
            == [["1/1"]]
            and selected_child["declared_output_metric_exact"]
            == selected_tube["output_metric_exact"]
            == selected_structured["problem"][
                "observation_noise_precision_exact"
            ]
            == [["1/1"]]
        ),
        "selected_protocol_survives_declared_structured_nuisance": (
            selected_structured["exact_calculation"][
                "positive_separation_certified"
            ]
            is True
            and selected_structured["exact_calculation"][
                "exact_optimum_certified"
            ]
            is True
        ),
        "selected_protocol_pair_is_disjoint_at_declared_noise": (
            selected_tube["certified_disjoint"] is True
        ),
        "selected_protocol_remains_disjoint_under_structured_nuisance_and_declared_noise": (
            Fraction(selected_tube["data_noise_radius_exact"]) ** 2
            < Fraction(
                selected_structured["exact_calculation"][
                    "critical_equal_noise_radius_squared_lower_exact"
                ]
            )
        ),
    }
    ledger["all_pinned_integration_obligations_pass"] = all(ledger.values())
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "self-verifying Arithmetic-Atlas protocol integration demonstrator",
        "query_gain_library": gain,
        "shared_vs_independent_nuisance_library": nuisance_semantics,
        "structured_nuisance": structured,
        "robust_model_geometry": robust,
        "selected_protocol_structured_separation": selected_structured,
        "selected_protocol_response_tube": selected_tube,
        "integration_ledger": ledger,
        "proof_boundary": (
            "This pinned report proves exact finite rational statements for its embedded "
            "candidate libraries and nuisance/model declarations. External physical-model "
            "enclosure, remote-tail truth, model-family exhaustiveness, and response-box "
            "information transfer remain separately declared obligations."
        ),
    }


def _verification_payload() -> dict[str, object]:
    return {
        "passed": True,
        "schema_version": "oig-atlas-protocol-integration-verification-v1",
        "components_verified": [
            "query_gain_library",
            "shared_vs_independent_nuisance_library",
            "structured_nuisance",
            "robust_model_geometry",
            "selected_protocol_structured_separation",
            "selected_protocol_response_tube",
            "integration_ledger",
        ],
        "method": (
            "strict child reconstruction followed by deterministic pinned-report "
            "and cross-layer ledger reconstruction"
        ),
    }


def _verify_atlas_protocol_integration_report(
    report: dict[str, object],
    *,
    require_embedded: bool,
) -> dict[str, object]:
    """Strictly reconstruct every child and the pinned integration ledger."""
    try:
        if type(report) is not dict:
            raise TypeError("integration report must be a JSON object")
        allowed = {
            "schema_version",
            "status",
            "query_gain_library",
            "shared_vs_independent_nuisance_library",
            "structured_nuisance",
            "robust_model_geometry",
            "selected_protocol_structured_separation",
            "selected_protocol_response_tube",
            "integration_ledger",
            "proof_boundary",
            "independent_verification",
        }
        required = (
            allowed
            if require_embedded
            else allowed - {"independent_verification"}
        )
        if set(report) - allowed or required - set(report):
            raise ValueError("integration report has missing or surplus fields")
        if report.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unknown integration schema")

        child_checks = (
            verify_query_candidate_library_report(report["query_gain_library"]),
            verify_query_candidate_library_report(
                report["shared_vs_independent_nuisance_library"]
            ),
            verify_structured_nuisance_demo_report(report["structured_nuisance"]),
            verify_robust_model_demo_report(report["robust_model_geometry"]),
            verify_structured_nuisance_report(
                report["selected_protocol_structured_separation"]
            ),
            verify_robust_model_report(report["selected_protocol_response_tube"]),
        )
        if any(check.get("passed") is not True for check in child_checks):
            raise ValueError(f"one or more child certificates failed: {child_checks}")

        rebuilt = _build_payload()
        submitted = {
            key: value
            for key, value in report.items()
            if key != "independent_verification"
        }
        if not _strict_json_equal(submitted, rebuilt):
            raise ValueError("pinned integration report does not reproduce exactly")

        verification = _verification_payload()
        embedded = report.get("independent_verification")
        if require_embedded and embedded is None:
            raise ValueError("embedded integration verification is required")
        if embedded is not None and not _strict_json_equal(embedded, verification):
            raise ValueError("embedded integration verification is inconsistent")
        return verification
    except Exception as error:
        return {"passed": False, "error": str(error)}


def verify_atlas_protocol_integration_report(
    report: dict[str, object],
) -> dict[str, object]:
    """Strictly verify a sealed serialized integration report."""
    return _verify_atlas_protocol_integration_report(
        report, require_embedded=True
    )


def run_integration_demo() -> dict[str, object]:
    report = _build_payload()
    verification = _verify_atlas_protocol_integration_report(
        report, require_embedded=False
    )
    if verification.get("passed") is not True:
        raise AssertionError(f"integration self-verification failed: {verification}")
    report["independent_verification"] = verification
    final = verify_atlas_protocol_integration_report(report)
    if final.get("passed") is not True:
        raise AssertionError(f"embedded integration verification failed: {final}")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--output")
    action.add_argument("--verify")
    args = parser.parse_args(argv)

    if args.verify:
        with open(args.verify, "r", encoding="utf-8") as handle:
            report = json.load(handle)
        verification = verify_atlas_protocol_integration_report(report)
        print(json.dumps(verification, indent=2, sort_keys=True))
        return 0 if verification.get("passed") is True else 1

    report = run_integration_demo()
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "SCHEMA_VERSION",
    "run_integration_demo",
    "verify_atlas_protocol_integration_report",
]
