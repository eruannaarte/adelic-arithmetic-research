#!/usr/bin/env python3
"""Explore the resonance-aware nested time ensemble from Arithmetic Sensing V."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from fractions import Fraction

import numpy as np

from arithmetic_sensing_iv import REFERENCE_COEFFICIENTS
from degree_fourteen_resource_law import (
    MAXIMUM_NORM,
    TRUNCATION,
    ResourceLawWorkspace,
    prepare_workspace,
    resource_proxy,
)
from fixed_degree_arithmetic_sensing import (
    fixed_degree_mellin_alias_remainder_bound,
)
from optimized_arithmetic_quadrature import (
    CosineQuadratureDesign,
    centered_cosine_response,
    cosine_window_weights,
)


SHORT_TIME = 500
SHORT_SAMPLES = 2_500
LONG_TIME = 1_790
LONG_SAMPLES = 8_950
SHORT_WEIGHT = Fraction(7, 4_096)


@dataclass(frozen=True)
class EnsembleProxy:
    coefficient_bound: float
    worst_coefficient_target: int
    maximum_complete_tail: float
    worst_tail_target: int
    gram_row_defect: float
    target_50_tail: float
    target_50_gram_row: float

    @property
    def certified_by_proxy(self) -> bool:
        return self.coefficient_bound < 0.5


def reference_designs() -> tuple[CosineQuadratureDesign, ...]:
    return (
        CosineQuadratureDesign(
            SHORT_SAMPLES,
            float(SHORT_TIME),
            REFERENCE_COEFFICIENTS.copy(),
        ),
        CosineQuadratureDesign(
            LONG_SAMPLES,
            float(LONG_TIME),
            REFERENCE_COEFFICIENTS.copy(),
        ),
    )


def reference_weights() -> tuple[float, float]:
    alpha = float(SHORT_WEIGHT)
    return alpha, 1.0 - alpha


def centered_grid_inclusion_offset() -> int:
    short_spacing = Fraction(SHORT_TIME, SHORT_SAMPLES)
    long_spacing = Fraction(LONG_TIME, LONG_SAMPLES)
    difference = LONG_SAMPLES - SHORT_SAMPLES
    if short_spacing != long_spacing or difference < 0 or difference % 2:
        raise ArithmeticError("the published grids are not exactly nested")
    return difference // 2


def combined_outer_grid_weights() -> np.ndarray:
    """Materialize the positive ensemble weights on 8,950 distinct times."""
    short, long = reference_designs()
    alpha, beta = reference_weights()
    weights = beta * cosine_window_weights(long)
    offset = centered_grid_inclusion_offset()
    weights[offset : offset + SHORT_SAMPLES] += (
        alpha * cosine_window_weights(short)
    )
    return weights


def _ensemble_response(
    frequencies: np.ndarray,
    designs: tuple[CosineQuadratureDesign, ...],
    weights: tuple[float, ...],
) -> np.ndarray:
    return sum(
        weight * centered_cosine_response(frequencies, design)
        for weight, design in zip(weights, designs)
    )


def ensemble_proxy(
    workspace: ResourceLawWorkspace,
    targets: tuple[int, ...] = tuple(range(1, MAXIMUM_NORM + 1)),
) -> EnsembleProxy:
    """Evaluate the hybrid ensemble theorem on the declared target set."""
    designs = reference_designs()
    mixing = reference_weights()
    tails: dict[int, float] = {}
    for target in targets:
        frequencies = np.log(target / workspace.finite_norms)
        response = _ensemble_response(frequencies, designs, mixing)
        finite = float(np.dot(workspace.finite_weights, np.abs(response)))
        remote = sum(
            weight
            * fixed_degree_mellin_alias_remainder_bound(
                target,
                TRUNCATION,
                design,
                workspace.base_remainder,
                workspace.mellin_certificate,
                "cancellation",
            )
            for weight, design in zip(mixing, designs)
        )
        tails[target] = finite + remote
    logs = np.log(np.arange(1, MAXIMUM_NORM + 1, dtype=float))
    frequency_matrix = logs[:, None] - logs[None, :]
    gram = _ensemble_response(frequency_matrix, designs, mixing)
    rows = np.sum(np.abs(gram - np.eye(MAXIMUM_NORM)), axis=1)
    defect = float(np.max(rows))
    maximum_tail_target = max(tails, key=tails.__getitem__)
    maximum_tail = tails[maximum_tail_target]
    coefficient_bounds = {
        target: target**2
        * (tails[target] + rows[target - 1] * maximum_tail / (1.0 - defect))
        for target in targets
    }
    worst_target = max(coefficient_bounds, key=coefficient_bounds.__getitem__)
    return EnsembleProxy(
        coefficient_bounds[worst_target],
        worst_target,
        maximum_tail,
        maximum_tail_target,
        defect,
        tails.get(50, float("nan")),
        float(rows[49]),
    )


def resonance_attribution(
    workspace: ResourceLawWorkspace,
    observation_time: int,
    target: int = 50,
    count: int = 10,
) -> list[dict[str, object]]:
    design = CosineQuadratureDesign(
        5 * observation_time,
        float(observation_time),
        REFERENCE_COEFFICIENTS.copy(),
    )
    frequencies = np.log(target / workspace.finite_norms)
    responses = centered_cosine_response(frequencies, design)
    terms = workspace.finite_weights * np.abs(responses)
    indices = np.argpartition(terms, -count)[-count:]
    indices = indices[np.argsort(terms[indices])[::-1]]
    finite_total = float(np.sum(terms))
    return [
        {
            "tail_norm": int(workspace.finite_norms[index]),
            "ratio": f"{int(workspace.finite_norms[index])}/{target}",
            "divisor_coefficient": int(
                workspace.divisor_coefficients[
                    int(workspace.finite_norms[index])
                ]
            ),
            "centered_response": float(responses[index]),
            "weighted_absolute_contribution": float(terms[index]),
            "share_of_finite_tail": float(terms[index] / finite_total),
        }
        for index in indices
    ]


def reference_report(all_targets: bool = False) -> dict[str, object]:
    workspace = prepare_workspace()
    short, long = reference_designs()
    omega = np.log(51.0 / 50.0)
    short_response = float(centered_cosine_response(omega, short))
    long_response = float(centered_cosine_response(omega, long))
    ideal_weight = -long_response / (short_response - long_response)
    combined_response = float(
        _ensemble_response(
            np.asarray([omega]),
            (short, long),
            reference_weights(),
        )[0]
    )
    proxy_targets = (
        tuple(range(1, MAXIMUM_NORM + 1)) if all_targets else (1, 50)
    )
    proxy = ensemble_proxy(workspace, proxy_targets)
    outer_weights = combined_outer_grid_weights()
    return {
        "nested_grid": {
            "common_spacing": str(Fraction(SHORT_TIME, SHORT_SAMPLES)),
            "short_inclusion_offset": centered_grid_inclusion_offset(),
            "distinct_sample_count": LONG_SAMPLES,
            "maximum_observation_time": LONG_TIME,
            "weight_sum": float(np.sum(outer_weights)),
            "minimum_weight": float(np.min(outer_weights)),
            "effective_sample_count": float(1.0 / np.sum(outer_weights**2)),
        },
        "dominant_mode_design": {
            "ratio": "51/50",
            "short_response": short_response,
            "long_response": long_response,
            "ideal_short_weight": ideal_weight,
            "dyadic_short_weight": str(SHORT_WEIGHT),
            "combined_response": combined_response,
            "suppression_factor_from_long_window": (
                abs(long_response) / abs(combined_response)
            ),
        },
        "ensemble_proxy": asdict(proxy),
        "single_long_window_proxy": asdict(
            resource_proxy(LONG_TIME, LONG_SAMPLES, workspace)
        ),
        "resonance_attribution": {
            "T=1100": resonance_attribution(workspace, 1_100, count=5),
            "T=1200": resonance_attribution(workspace, 1_200, count=5),
        },
        "scope": (
            "all 50 targets" if all_targets else "localized targets 1 and 50"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--all-targets",
        action="store_true",
        help="evaluate every target rather than the localized 1/50 proxy",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    print(
        json.dumps(
            reference_report(arguments.all_targets),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
