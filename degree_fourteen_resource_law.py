#!/usr/bin/env python3
"""Reproduce the Arithmetic Sensing V degree-fourteen resource law.

The exploratory layer is intentionally separate from the formal artifacts.
It uses the same exact-dyadic Mellin masses but binary64 finite responses to
locate candidate transitions.  The adjacent transition points published in
the manuscript are then independently certified by
``verify_end_to_end_certificate.py``.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

import numpy as np

from arithmetic_sensing_iv import REFERENCE_COEFFICIENTS
from fixed_degree_arithmetic_sensing import (
    fixed_degree_divisor_coefficients_sieve,
    fixed_degree_mellin_alias_remainder_bound,
    fixed_degree_tail_l1_from_sieve,
    zeta_log_convolution_certificate,
)
from optimized_arithmetic_quadrature import (
    CosineQuadratureDesign,
    centered_cosine_response,
    cosine_window_gram,
)


DEGREE = 14
MAXIMUM_NORM = 50
TRUNCATION = 1_000_000
BIN_WIDTH = 0.01
REMOTE_BIN_COUNT = 8_246


@dataclass(frozen=True)
class ResourcePoint:
    observation_time: int
    sample_count: int
    coefficient_bound: float
    maximum_complete_tail: float
    target_50_tail: float
    gram_row_defect: float
    target_50_gram_row: float

    @property
    def certified_by_proxy(self) -> bool:
        return self.coefficient_bound < 0.5


@dataclass(frozen=True)
class ResourceLawWorkspace:
    divisor_coefficients: np.ndarray
    finite_norms: np.ndarray
    finite_weights: np.ndarray
    base_remainder: float
    mellin_certificate: object


def prepare_workspace() -> ResourceLawWorkspace:
    coefficients = fixed_degree_divisor_coefficients_sieve(
        TRUNCATION, DEGREE
    )
    norms = np.arange(MAXIMUM_NORM + 1, TRUNCATION + 1, dtype=float)
    weights = coefficients[MAXIMUM_NORM + 1 :] * norms ** (-2.0)
    base_remainder = fixed_degree_tail_l1_from_sieve(
        TRUNCATION, DEGREE, 2.0, coefficients
    )
    # Match the fixed R=82.46 formal resource artifacts exactly.
    maximum_log = REMOTE_BIN_COUNT * BIN_WIDTH
    mellin = zeta_log_convolution_certificate(
        maximum_log, DEGREE, 2.0, BIN_WIDTH
    )
    return ResourceLawWorkspace(
        coefficients, norms, weights, base_remainder, mellin
    )


def resource_proxy(
    observation_time: int,
    sample_count: int,
    workspace: ResourceLawWorkspace,
) -> ResourcePoint:
    """Compute the localized Neumann proxy at targets 1 and 50.

    The published scans verified after spot checks that target 1 maximizes the
    unscaled tail and target 50 maximizes the coefficient consequence.  Formal
    artifacts independently recompute all 50 targets at each boundary point.
    """
    design = CosineQuadratureDesign(
        sample_count,
        float(observation_time),
        REFERENCE_COEFFICIENTS.copy(),
    )
    tails = []
    for target in (1, 50):
        finite = float(
            np.dot(
                workspace.finite_weights,
                np.abs(
                    centered_cosine_response(
                        np.log(target / workspace.finite_norms), design
                    )
                ),
            )
        )
        remote = fixed_degree_mellin_alias_remainder_bound(
            target,
            TRUNCATION,
            design,
            workspace.base_remainder,
            workspace.mellin_certificate,
            "cancellation",
        )
        tails.append(finite + remote)
    gram = cosine_window_gram(MAXIMUM_NORM, design)
    off_diagonal = np.abs(gram - np.eye(MAXIMUM_NORM))
    row_sums = np.sum(off_diagonal, axis=1)
    defect = float(np.max(row_sums))
    target_50_row = float(row_sums[-1])
    bound = MAXIMUM_NORM**2 * (
        tails[1] + target_50_row * max(tails) / (1.0 - defect)
    )
    return ResourcePoint(
        observation_time,
        sample_count,
        bound,
        max(tails),
        tails[1],
        defect,
        target_50_row,
    )


def sampling_boundary(
    workspace: ResourceLawWorkspace,
    observation_time: int = 1_000,
    lower: int = 10_000,
    upper: int = 15_000,
) -> tuple[ResourcePoint, ResourcePoint]:
    """Locate the first pass on the tested monotone fixed-time interval."""
    while upper - lower > 1:
        middle = (lower + upper) // 2
        if resource_proxy(observation_time, middle, workspace).certified_by_proxy:
            upper = middle
        else:
            lower = middle
    return (
        resource_proxy(observation_time, lower, workspace),
        resource_proxy(observation_time, upper, workspace),
    )


def proportional_time_scan(
    workspace: ResourceLawWorkspace,
    lower_time: int = 1_000,
    upper_time: int = 3_000,
    sampling_ratio: int = 5,
) -> dict[str, object]:
    points = [
        resource_proxy(time, sampling_ratio * time, workspace)
        for time in range(lower_time, upper_time + 1)
    ]
    crossings = [
        (left, right)
        for left, right in zip(points, points[1:])
        if (left.coefficient_bound - 0.5)
        * (right.coefficient_bound - 0.5)
        <= 0.0
    ]
    best = min(points, key=lambda point: point.coefficient_bound)
    return {
        "crossings": [
            [left.__dict__, right.__dict__] for left, right in crossings
        ],
        "best_point": best.__dict__,
        "all_points_after_last_crossing_pass": bool(
            crossings
            and all(
                point.certified_by_proxy
                for point in points[
                    crossings[-1][1].observation_time - lower_time :
                ]
            )
        ),
    }


def density_limit_study(
    workspace: ResourceLawWorkspace,
    observation_time: int = 1_000,
) -> list[dict[str, object]]:
    return [
        resource_proxy(observation_time, sample_count, workspace).__dict__
        for sample_count in (
            5_000,
            10_000,
            14_690,
            14_691,
            15_000,
            20_000,
            50_000,
            100_000,
            1_000_000_000,
        )
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sampling-boundary", action="store_true")
    parser.add_argument("--time-scan", action="store_true")
    parser.add_argument("--density-study", action="store_true")
    parser.add_argument("--all", action="store_true")
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    workspace = prepare_workspace()
    report: dict[str, object] = {}
    if arguments.sampling_boundary or arguments.all:
        fail, passed = sampling_boundary(workspace)
        report["sampling_boundary"] = {
            "last_failure": fail.__dict__,
            "first_success": passed.__dict__,
        }
    if arguments.time_scan or arguments.all:
        report["proportional_time_scan"] = proportional_time_scan(workspace)
    if arguments.density_study or arguments.all:
        report["density_limit_study"] = density_limit_study(workspace)
    if not report:
        report["published_boundary_points"] = [
            resource_proxy(1_000, 14_690, workspace).__dict__,
            resource_proxy(1_000, 14_691, workspace).__dict__,
            resource_proxy(1_892, 9_460, workspace).__dict__,
            resource_proxy(1_893, 9_465, workspace).__dict__,
        ]
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
