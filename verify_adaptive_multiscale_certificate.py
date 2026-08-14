#!/usr/bin/env python3
"""Build or check the adaptive multiscale support-optimality artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from fractions import Fraction
from pathlib import Path

import flint

from adaptive_multiscale_exchange import (
    FORMAL_PRECISION,
    OUTER_SCALE,
    PUBLISHED_SHORT_WEIGHT,
    SHORT_SCALES,
    ExchangeStep,
    ExactPairCertificate,
    RationalPairProblem,
    ResponseInterval,
    adaptive_mode_exchange,
    build_support_frontier,
    interval_objective_upper,
    verify_exact_pair_certificate,
)
from arithmetic_multiscale_sensing import NestedScale
from degree_fourteen_resource_law import prepare_workspace
from verified_end_to_end_certificate import (
    exact_fixed_degree_coefficients_uint64,
)


SCHEMA = "arithmetic-sensing-v-adaptive-multiscale-v1"
DIRECTORY = Path(__file__).resolve().parent
DEFAULT_ARTIFACT = (
    DIRECTORY
    / "certificates"
    / "arithmetic_sensing_v_adaptive_multiscale.json"
)
FORMAL_RECOVERY_DIGEST = (
    "89b316584d9179c13232ad99b9515067fdf67329e6df3db4c48220d6b8c3ff7b"
)


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _payload_digest(payload: dict[str, object]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode()).hexdigest()


def _interval_payload(value: ResponseInterval) -> list[str]:
    return [str(value.lower), str(value.upper)]


def _certificate_payload(value: ExactPairCertificate) -> dict[str, object]:
    return {
        "short_weight": str(value.short_weight),
        "midpoint_objective": str(value.midpoint_objective),
        "dual_variables": [str(item) for item in value.dual_variables],
        "midpoint_dual_lower": str(value.midpoint_dual_lower),
        "robust_dual_lower": str(value.robust_dual_lower),
        "robust_primal_upper": str(value.robust_primal_upper),
    }


def _exchange_payload(value: ExchangeStep) -> dict[str, object]:
    return {
        "iteration": value.iteration,
        "selected_tail_norms": list(value.selected_tail_norms),
        "short_time": value.short_time,
        "short_weight": value.short_weight,
        "restricted_objective": value.restricted_objective,
        "complete_target_finite_plus_remote": (
            value.complete_target_finite_plus_remote
        ),
        "added_tail_norms": list(value.added_tail_norms),
        "added_contributions": list(value.added_contributions),
    }


def _parse_interval(value: object) -> ResponseInterval:
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("response interval must have two endpoints")
    return ResponseInterval(Fraction(value[0]), Fraction(value[1]))


def _parse_pair(
    payload: dict[str, object],
    target_norm: int,
    tail_norms: tuple[int, ...],
    arithmetic_weights: tuple[Fraction, ...],
    outer_scale: NestedScale,
    outer_responses: tuple[ResponseInterval, ...],
) -> tuple[RationalPairProblem, ExactPairCertificate]:
    short_time = int(payload["short_time"])
    short_sample_count = int(payload["short_sample_count"])
    raw_responses = payload["short_response_intervals"]
    raw_certificate = payload["certificate"]
    if not isinstance(raw_responses, list) or not isinstance(
        raw_certificate, dict
    ):
        raise ValueError("pair payload is malformed")
    problem = RationalPairProblem(
        NestedScale(short_time, short_sample_count),
        outer_scale,
        target_norm,
        tail_norms,
        arithmetic_weights,
        tuple(_parse_interval(value) for value in raw_responses),
        outer_responses,
    )
    certificate = ExactPairCertificate(
        Fraction(raw_certificate["short_weight"]),
        Fraction(raw_certificate["midpoint_objective"]),
        tuple(Fraction(value) for value in raw_certificate["dual_variables"]),
        Fraction(raw_certificate["midpoint_dual_lower"]),
        Fraction(raw_certificate["robust_dual_lower"]),
        Fraction(raw_certificate["robust_primal_upper"]),
    )
    verify_exact_pair_certificate(problem, certificate)
    return problem, certificate


def build_certificate() -> dict[str, object]:
    """Recompute discovery, Arb intervals, and every exact rational dual."""
    workspace = prepare_workspace()
    exchange = adaptive_mode_exchange(workspace)
    tail_norms = exchange[-1].selected_tail_norms
    frontier = build_support_frontier(
        tail_norms,
        short_scales=SHORT_SCALES,
        outer_scale=OUTER_SCALE,
        precision=FORMAL_PRECISION,
    )
    pairs = [(frontier.winner_problem, frontier.winner)] + list(
        frontier.competitors
    )
    pairs.sort(key=lambda item: item[0].short_scale.observation_time)
    reference_problem = pairs[0][0]
    return {
        "scope": (
            "binary64 adaptive mode discovery; exact-rational primal/dual "
            "certificates weakened over Arb intervals prove support selection "
            "only for the declared finite mode set and two-scale candidate set"
        ),
        "parameters": {
            "degree": 14,
            "target_norm": reference_problem.target_norm,
            "outer_time": OUTER_SCALE.observation_time,
            "outer_sample_count": OUTER_SCALE.sample_count,
            "short_times": [
                scale.observation_time for scale in SHORT_SCALES
            ],
            "common_sample_spacing": "1/5",
            "exchange_iterations": len(exchange),
            "exchange_batch_size": 4,
            "arb_precision_bits": FORMAL_PRECISION,
            "pair_support_count": len(pairs),
            "published_short_weight": str(PUBLISHED_SHORT_WEIGHT),
        },
        "exchange": [_exchange_payload(step) for step in exchange],
        "finite_problem": {
            "tail_norms": list(tail_norms),
            "arithmetic_weights": [
                str(value) for value in reference_problem.arithmetic_weights
            ],
            "outer_response_intervals": [
                _interval_payload(value)
                for value in reference_problem.outer_responses
            ],
            "pairs": [
                {
                    "short_time": problem.short_scale.observation_time,
                    "short_sample_count": problem.short_scale.sample_count,
                    "short_response_intervals": [
                        _interval_payload(value)
                        for value in problem.short_responses
                    ],
                    "certificate": _certificate_payload(certificate),
                }
                for problem, certificate in pairs
            ],
        },
        "consequence": {
            "winner_short_time": (
                frontier.winner_problem.short_scale.observation_time
            ),
            "winner_midpoint_weight": str(frontier.winner.short_weight),
            "winner_midpoint_objective": str(
                frontier.winner.midpoint_objective
            ),
            "winner_robust_lower": str(frontier.winner.robust_dual_lower),
            "winner_robust_upper": str(frontier.winner.robust_primal_upper),
            "runner_up_short_time": frontier.runner_up_time,
            "runner_up_robust_lower": str(frontier.runner_up_robust_lower),
            "optimized_support_separation": str(frontier.support_separation),
            "published_weight_upper": str(frontier.published_weight_upper),
            "published_support_separation": str(
                frontier.published_support_separation
            ),
            "unique_support_certificate": True,
        },
        "recovery_dependency": {
            "artifact_name": "arithmetic_sensing_v_multiscale_end_to_end.json",
            "formal_certificate_sha256": FORMAL_RECOVERY_DIGEST,
            "logical_role": (
                "independent all-target recovery theorem; not a premise of "
                "the finite support-optimality certificate"
            ),
        },
    }


def _validate_certificate(certificate: dict[str, object]) -> None:
    parameters = certificate.get("parameters")
    finite = certificate.get("finite_problem")
    consequence = certificate.get("consequence")
    dependency = certificate.get("recovery_dependency")
    exchange = certificate.get("exchange")
    if not all(
        isinstance(value, dict)
        for value in (parameters, finite, consequence, dependency)
    ):
        raise ValueError("adaptive certificate sections are missing")
    if not isinstance(exchange, list) or not exchange:
        raise ValueError("adaptive exchange trace is missing")
    assert isinstance(parameters, dict)
    assert isinstance(finite, dict)
    assert isinstance(consequence, dict)
    assert isinstance(dependency, dict)
    target_norm = int(parameters["target_norm"])
    tail_norms = tuple(int(value) for value in finite["tail_norms"])
    arithmetic_weights = tuple(
        Fraction(value) for value in finite["arithmetic_weights"]
    )
    coefficients = exact_fixed_degree_coefficients_uint64(
        max(tail_norms), int(parameters["degree"])
    )
    expected_weights = tuple(
        Fraction(int(coefficients[norm]), norm * norm) for norm in tail_norms
    )
    if arithmetic_weights != expected_weights:
        raise ValueError("stored arithmetic weights are not exact d_14(k)/k^2")
    outer_scale = NestedScale(
        int(parameters["outer_time"]),
        int(parameters["outer_sample_count"]),
    )
    if outer_scale.sample_count != 5 * outer_scale.observation_time:
        raise ValueError("outer grid does not have the declared spacing")
    outer_responses = tuple(
        _parse_interval(value)
        for value in finite["outer_response_intervals"]
    )
    raw_pairs = finite["pairs"]
    if not isinstance(raw_pairs, list):
        raise ValueError("pair list is missing")
    pairs = [
        _parse_pair(
            value,
            target_norm,
            tail_norms,
            arithmetic_weights,
            outer_scale,
            outer_responses,
        )
        for value in raw_pairs
        if isinstance(value, dict)
    ]
    if len(pairs) != int(parameters["pair_support_count"]):
        raise ValueError("pair-support count does not match")
    expected_times = tuple(int(value) for value in parameters["short_times"])
    observed_times = tuple(
        problem.short_scale.observation_time for problem, _ in pairs
    )
    if observed_times != expected_times:
        raise ValueError("pair supports do not match the declared time grid")
    if any(
        problem.short_scale.sample_count
        != 5 * problem.short_scale.observation_time
        for problem, _ in pairs
    ):
        raise ValueError("a short grid does not have the declared spacing")
    selected = None
    for index, step in enumerate(exchange):
        if not isinstance(step, dict) or int(step["iteration"]) != index:
            raise ValueError("exchange iterations are malformed")
        current = tuple(int(value) for value in step["selected_tail_norms"])
        added = tuple(int(value) for value in step["added_tail_norms"])
        if selected is not None and current != tuple(sorted(selected)):
            raise ValueError("exchange mode sets do not propagate")
        selected = set(current)
        selected.update(added)
    if tuple(int(value) for value in exchange[-1]["selected_tail_norms"]) != (
        tail_norms
    ):
        raise ValueError("formal mode set is not the last solved exchange set")
    winner_time = int(consequence["winner_short_time"])
    winner_matches = [
        item
        for item in pairs
        if item[0].short_scale.observation_time == winner_time
    ]
    if len(winner_matches) != 1:
        raise ValueError("declared winner is not unique in the pair list")
    winner_problem, winner = winner_matches[0]
    competitors = [
        item for item in pairs if item[0].short_scale.observation_time != winner_time
    ]
    runner_problem, runner = min(
        competitors, key=lambda item: item[1].robust_dual_lower
    )
    separation = runner.robust_dual_lower - winner.robust_primal_upper
    published_upper = interval_objective_upper(
        winner_problem, Fraction(parameters["published_short_weight"])
    )
    published_separation = runner.robust_dual_lower - published_upper
    expected = {
        "winner_midpoint_weight": winner.short_weight,
        "winner_midpoint_objective": winner.midpoint_objective,
        "winner_robust_lower": winner.robust_dual_lower,
        "winner_robust_upper": winner.robust_primal_upper,
        "runner_up_robust_lower": runner.robust_dual_lower,
        "optimized_support_separation": separation,
        "published_weight_upper": published_upper,
        "published_support_separation": published_separation,
    }
    for name, value in expected.items():
        if Fraction(consequence[name]) != value:
            raise ValueError(f"stored consequence {name} is incorrect")
    if int(consequence["runner_up_short_time"]) != (
        runner_problem.short_scale.observation_time
    ):
        raise ValueError("stored runner-up time is incorrect")
    if separation <= 0 or published_separation <= 0:
        raise ValueError("declared support is not rigorously separated")
    if consequence.get("unique_support_certificate") is not True:
        raise ValueError("unique-support flag is absent")
    if dependency.get("formal_certificate_sha256") != FORMAL_RECOVERY_DIGEST:
        raise ValueError("recovery dependency hash is incorrect")


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
        raise ValueError("unknown adaptive multiscale certificate schema")
    stored = artifact.get("certificate")
    if not isinstance(stored, dict):
        raise ValueError("artifact has no certificate object")
    _validate_certificate(stored)
    _validate_certificate(recomputed)
    stored_digest = artifact.get("formal_certificate_sha256")
    if stored_digest != _payload_digest(stored):
        raise ValueError("stored adaptive certificate hash is invalid")
    recomputed_digest = _payload_digest(recomputed)
    if stored_digest != recomputed_digest or stored != recomputed:
        raise ValueError("recomputed adaptive certificate does not match")
    return {
        "verified": True,
        "schema": SCHEMA,
        "formal_certificate_sha256": recomputed_digest,
        "runtime": {"python_flint": flint.__version__},
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--write", type=Path)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    started = time.perf_counter()
    certificate = build_certificate()
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
