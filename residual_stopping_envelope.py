#!/usr/bin/env python3
"""Close the finite-mode stopping problem for the declared pair supports.

Selected-mode Arb duals screen most candidate supports against the published
T=510 full finite upper bound.  The few survivors receive million-term Arb
dual audits.  Together these two layers prove that the published support and
weight beat every competing declared pair support on the complete target-50
finite tail through one million.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np
from flint import arb, ctx

from adaptive_multiscale_exchange import (
    FORMAL_PRECISION,
    OUTER_SCALE,
    PUBLISHED_SHORT_WEIGHT,
    build_pair_problem,
)
from arithmetic_sensing_iv import REFERENCE_COEFFICIENTS
from arithmetic_multiscale_sensing import NestedScale
from optimized_arithmetic_quadrature import centered_cosine_response
from verified_end_to_end_certificate import (
    _arb_fraction,
    _centered_response,
    _arf_fraction,
    exact_fixed_degree_coefficients_uint64,
)
from verify_adaptive_multiscale_certificate import (
    verify_artifact as verify_adaptive_artifact,
)
from verify_time_ensemble_certificate import (
    verify_artifact as verify_recovery_artifact,
)


DIRECTORY = Path(__file__).resolve().parent
ADAPTIVE_ARTIFACT = (
    DIRECTORY
    / "certificates"
    / "arithmetic_sensing_v_adaptive_multiscale.json"
)
RECOVERY_ARTIFACT = (
    DIRECTORY
    / "certificates"
    / "arithmetic_sensing_v_multiscale_end_to_end.json"
)
TRUNCATION = 1_000_000
TARGET_NORM = 50
DEGREE = 14


@dataclass(frozen=True)
class BinaryDualDesign:
    short_time: int
    breakpoint_weight: Fraction
    special_dual_value: Fraction
    negative_sign_count: int
    sign_sha256: str
    packed_signs: bytes


@dataclass(frozen=True)
class FullTailDualBound:
    short_time: int
    breakpoint_weight: Fraction
    special_dual_value: Fraction
    negative_sign_count: int
    sign_sha256: str
    short_score_lower: Fraction
    outer_score_lower: Fraction
    complete_dual_lower: Fraction


_WORKER_COEFFICIENTS: np.ndarray | None = None
_WORKER_WINDOW: tuple[Fraction, ...] | None = None


def _load_verified_dependency(
    path: Path,
    verifier: Callable[[dict[str, object], dict[str, object]], object],
) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        artifact = json.load(handle)
    certificate = artifact.get("certificate")
    if not isinstance(certificate, dict):
        raise ValueError(f"dependency {path.name} has no certificate")
    verifier(artifact, certificate)
    return artifact


def _hash_signs(packed: bytes, count: int) -> str:
    digest = hashlib.sha256()
    digest.update(count.to_bytes(8, "little"))
    digest.update(packed)
    return digest.hexdigest()


def _binary_dual_designs(
    short_times: Sequence[int], coefficients: np.ndarray
) -> tuple[BinaryDualDesign, ...]:
    norms = np.arange(TARGET_NORM + 1, TRUNCATION + 1, dtype=float)
    frequencies = np.log(norms / float(TARGET_NORM))
    arithmetic_weights = (
        coefficients[TARGET_NORM + 1 :].astype(float) / norms**2
    )
    outer_response = centered_cosine_response(
        frequencies, OUTER_SCALE.design()
    )
    designs = []
    for short_time in short_times:
        short_scale = NestedScale(short_time, 5 * short_time)
        problem = build_pair_problem(
            short_scale,
            (TARGET_NORM + 1,),
            outer_scale=OUTER_SCALE,
            target_norm=TARGET_NORM,
            degree=DEGREE,
            precision=FORMAL_PRECISION,
        )
        short_midpoint = problem.short_responses[0].midpoint
        outer_midpoint = problem.outer_responses[0].midpoint
        breakpoint = -outer_midpoint / (short_midpoint - outer_midpoint)
        short_response = centered_cosine_response(
            frequencies, short_scale.design()
        )
        realized = (
            float(breakpoint) * short_response
            + (1.0 - float(breakpoint)) * outer_response
        )
        negative = np.signbit(realized)
        signed = np.where(negative, -1.0, 1.0)
        difference = short_response - outer_response
        fixed_slope = float(
            np.dot(
                arithmetic_weights[1:] * signed[1:],
                difference[1:],
            )
        )
        special_slope = float(arithmetic_weights[0] * difference[0])
        special_dual = Fraction.from_float(-fixed_slope / special_slope)
        if abs(special_dual) > 1:
            raise ArithmeticError("full-tail special dual value is infeasible")
        packed = np.packbits(
            negative.astype(np.uint8), bitorder="little"
        ).tobytes()
        designs.append(
            BinaryDualDesign(
                short_time,
                breakpoint,
                special_dual,
                int(np.count_nonzero(negative)),
                _hash_signs(packed, len(negative)),
                packed,
            )
        )
    return tuple(designs)


def _initialize_worker(coefficients: np.ndarray) -> None:
    global _WORKER_COEFFICIENTS, _WORKER_WINDOW
    _WORKER_COEFFICIENTS = coefficients
    _WORKER_WINDOW = tuple(
        Fraction.from_float(float(value)) for value in REFERENCE_COEFFICIENTS
    )


def _full_tail_dual_worker(design: BinaryDualDesign) -> FullTailDualBound:
    if _WORKER_COEFFICIENTS is None or _WORKER_WINDOW is None:
        raise RuntimeError("full-tail dual worker was not initialized")
    count = TRUNCATION - TARGET_NORM
    negative = np.unpackbits(
        np.frombuffer(design.packed_signs, dtype=np.uint8),
        bitorder="little",
    )[:count]
    if _hash_signs(design.packed_signs, count) != design.sign_sha256:
        raise ValueError("packed dual sign vector hash does not match")
    ctx.prec = FORMAL_PRECISION
    pi = arb.pi()
    window = tuple(_arb_fraction(value) for value in _WORKER_WINDOW)
    short_score = arb(0)
    outer_score = arb(0)
    short_scale = NestedScale(design.short_time, 5 * design.short_time)
    for index, tail_norm in enumerate(
        range(TARGET_NORM + 1, TRUNCATION + 1)
    ):
        frequency = (arb(tail_norm) / TARGET_NORM).log()
        short_response = _centered_response(
            frequency,
            short_scale.observation_time,
            short_scale.sample_count,
            window,
            pi,
        )
        outer_response = _centered_response(
            frequency,
            OUTER_SCALE.observation_time,
            OUTER_SCALE.sample_count,
            window,
            pi,
        )
        coefficient = arb(int(_WORKER_COEFFICIENTS[tail_norm])) / (
            tail_norm * tail_norm
        )
        if tail_norm == TARGET_NORM + 1:
            dual = _arb_fraction(design.special_dual_value)
        else:
            dual = arb(-1 if negative[index] else 1)
        short_score += coefficient * dual * short_response
        outer_score += coefficient * dual * outer_response
    short_lower = _arf_fraction(short_score.lower())
    outer_lower = _arf_fraction(outer_score.lower())
    return FullTailDualBound(
        design.short_time,
        design.breakpoint_weight,
        design.special_dual_value,
        design.negative_sign_count,
        design.sign_sha256,
        short_lower,
        outer_lower,
        min(short_lower, outer_lower),
    )


def verified_full_tail_dual_bounds(
    short_times: Sequence[int], processes: int | None = None
) -> tuple[FullTailDualBound, ...]:
    """Construct million-term Arb dual lower bounds for candidate supports."""
    times = tuple(int(value) for value in short_times)
    if not times or len(set(times)) != len(times):
        raise ValueError("short times must be a nonempty distinct sequence")
    coefficients = exact_fixed_degree_coefficients_uint64(TRUNCATION, DEGREE)
    designs = _binary_dual_designs(times, coefficients)
    if processes is None:
        processes = min(len(times), 8)
    if processes < 1:
        raise ValueError("process count must be positive")
    if processes == 1:
        _initialize_worker(coefficients)
        results = [_full_tail_dual_worker(design) for design in designs]
    else:
        context = multiprocessing.get_context("spawn")
        with context.Pool(
            processes,
            initializer=_initialize_worker,
            initargs=(coefficients,),
        ) as pool:
            results = pool.map(_full_tail_dual_worker, designs)
    results.sort(key=lambda value: value.short_time)
    return tuple(results)


def _pair_selected_lowers(
    adaptive: dict[str, object]
) -> dict[int, Fraction]:
    certificate = adaptive["certificate"]
    finite = certificate["finite_problem"]
    return {
        int(pair["short_time"]): Fraction(
            pair["certificate"]["robust_dual_lower"]
        )
        for pair in finite["pairs"]
    }


def build_stopping_report(processes: int | None = None) -> dict[str, object]:
    adaptive = _load_verified_dependency(
        ADAPTIVE_ARTIFACT, verify_adaptive_artifact
    )
    recovery = _load_verified_dependency(
        RECOVERY_ARTIFACT, verify_recovery_artifact
    )
    winner_upper = Fraction(
        recovery["certificate"]["finite"]["upper_at_target_50"]
    )
    selected_lowers = _pair_selected_lowers(adaptive)
    competitors = {
        time: lower for time, lower in selected_lowers.items() if time != 510
    }
    survivors = tuple(
        sorted(time for time, lower in competitors.items() if lower <= winner_upper)
    )
    screened = {
        time: lower for time, lower in competitors.items() if lower > winner_upper
    }
    expected_survivors = (440, 480, 490, 500, 520)
    if survivors != expected_survivors:
        raise ArithmeticError("selected-mode screen changed unexpectedly")
    full_bounds = verified_full_tail_dual_bounds(survivors, processes)
    if any(bound.complete_dual_lower <= winner_upper for bound in full_bounds):
        raise ArithmeticError("a full-tail survivor was not eliminated")
    closest_full = min(full_bounds, key=lambda value: value.complete_dual_lower)
    closest_screened_time, closest_screened_lower = min(
        screened.items(), key=lambda item: item[1]
    )
    return {
        "scope": (
            "complete target-50 finite-tail stopping certificate over the "
            "declared pair-support family; selected-mode Arb duals screen 45 "
            "supports and million-term Arb duals eliminate the five survivors"
        ),
        "parameters": {
            "degree": DEGREE,
            "target_norm": TARGET_NORM,
            "truncation": TRUNCATION,
            "outer_time": OUTER_SCALE.observation_time,
            "outer_sample_count": OUTER_SCALE.sample_count,
            "published_short_time": 510,
            "published_short_weight": str(PUBLISHED_SHORT_WEIGHT),
            "candidate_short_times": sorted(selected_lowers),
            "arb_precision_bits": FORMAL_PRECISION,
            "dual_sign_source": (
                "binary64 sign choice used only to construct feasible +/-1 "
                "dual variables; validity does not assume the signs are correct"
            ),
        },
        "dependencies": {
            "selected_mode_support_artifact": {
                "name": ADAPTIVE_ARTIFACT.name,
                "formal_certificate_sha256": adaptive[
                    "formal_certificate_sha256"
                ],
            },
            "published_full_finite_upper_artifact": {
                "name": RECOVERY_ARTIFACT.name,
                "formal_certificate_sha256": recovery[
                    "formal_certificate_sha256"
                ],
            },
        },
        "selected_mode_screen": {
            "screened_support_count": len(screened),
            "survivor_times": list(survivors),
            "closest_screened_time": closest_screened_time,
            "closest_screened_lower": str(closest_screened_lower),
            "screen_margin": str(closest_screened_lower - winner_upper),
        },
        "full_tail_duals": [
            {
                **asdict(bound),
                "breakpoint_weight": str(bound.breakpoint_weight),
                "special_dual_value": str(bound.special_dual_value),
                "short_score_lower": str(bound.short_score_lower),
                "outer_score_lower": str(bound.outer_score_lower),
                "complete_dual_lower": str(bound.complete_dual_lower),
            }
            for bound in full_bounds
        ],
        "consequence": {
            "published_full_finite_upper": str(winner_upper),
            "closest_competing_time": closest_full.short_time,
            "closest_competing_full_lower": str(
                closest_full.complete_dual_lower
            ),
            "full_support_separation": str(
                closest_full.complete_dual_lower - winner_upper
            ),
            "all_competing_pair_supports_eliminated": True,
            "finite_mode_stopping_certificate": True,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processes", type=int)
    parser.add_argument("--compact", action="store_true")
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    print(
        json.dumps(
            build_stopping_report(arguments.processes),
            indent=None if arguments.compact else 2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
