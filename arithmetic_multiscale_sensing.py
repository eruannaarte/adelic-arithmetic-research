#!/usr/bin/env python3
"""Positive multiscale design for arithmetic log-frequency sensing.

This is a discovery layer, not a replacement for the Arb/MPFR certificate.
It detects large omitted arithmetic modes, embeds candidate centered windows
as response signatures, and solves a finite positive minimax problem.  A
candidate is publishable only after exact rationalization and independent
evaluation by ``verify_time_ensemble_certificate.py``.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Mapping, Sequence

import numpy as np
from scipy.optimize import linprog

from arithmetic_sensing_iv import REFERENCE_COEFFICIENTS
from degree_fourteen_resource_law import (
    TRUNCATION,
    ResourceLawWorkspace,
    prepare_workspace,
)
from fixed_degree_arithmetic_sensing import (
    fixed_degree_mellin_alias_remainder_bound,
)
from optimized_arithmetic_quadrature import (
    CosineQuadratureDesign,
    centered_cosine_response,
    cosine_window_weights,
)


@dataclass(frozen=True, order=True)
class NestedScale:
    """One centered midpoint grid in a common nested-grid family."""

    observation_time: int
    sample_count: int

    def __post_init__(self) -> None:
        if self.observation_time < 1 or self.sample_count < 2:
            raise ValueError("time must be positive and sample count at least two")

    @property
    def spacing(self) -> Fraction:
        return Fraction(self.observation_time, self.sample_count)

    def design(self) -> CosineQuadratureDesign:
        return CosineQuadratureDesign(
            self.sample_count,
            float(self.observation_time),
            REFERENCE_COEFFICIENTS.copy(),
        )


@dataclass(frozen=True)
class DangerousMode:
    """One explicitly enumerated omitted ratio and its arithmetic weight."""

    target_norm: int
    tail_norm: int
    arithmetic_weight: float
    baseline_response: float
    weighted_contribution: float

    @property
    def ratio(self) -> str:
        return f"{self.tail_norm}/{self.target_norm}"

    @property
    def log_frequency(self) -> float:
        return math.log(self.tail_norm / self.target_norm)


@dataclass(frozen=True)
class PositiveMinimaxResult:
    """Numerical optimum of the declared finite response-signature LP."""

    scales: tuple[NestedScale, ...]
    weights: tuple[float, ...]
    objective: float
    target_upper_bounds: tuple[tuple[int, float], ...]
    status: str

    @property
    def active_components(self) -> tuple[tuple[NestedScale, float], ...]:
        return tuple(
            (scale, weight)
            for scale, weight in zip(self.scales, self.weights)
            if weight > 1e-9
        )


@dataclass(frozen=True)
class RationalMultiscaleDesign:
    """Exact positive weights on exactly nested centered grids."""

    scales: tuple[NestedScale, ...]
    weights: tuple[Fraction, ...]

    def __post_init__(self) -> None:
        if len(self.scales) != len(self.weights) or not self.scales:
            raise ValueError("one weight is required per scale")
        if any(weight < 0 for weight in self.weights):
            raise ValueError("multiscale weights must be nonnegative")
        if sum(self.weights, Fraction()) != 1:
            raise ValueError("multiscale weights must sum exactly to one")
        validate_nested_scales(self.scales)

    @property
    def outer_scale(self) -> NestedScale:
        return max(self.scales, key=lambda scale: scale.sample_count)


def proportional_scales(
    lower_time: int,
    upper_time: int,
    step: int = 10,
    sampling_ratio: int = 5,
) -> tuple[NestedScale, ...]:
    """Return parity-compatible grids with common spacing ``1/ratio``."""
    if lower_time < 1 or upper_time < lower_time or step < 1:
        raise ValueError("invalid time interval")
    if sampling_ratio < 1:
        raise ValueError("sampling ratio must be positive")
    scales = tuple(
        NestedScale(time, sampling_ratio * time)
        for time in range(lower_time, upper_time + 1, step)
    )
    validate_nested_scales(scales)
    return scales


def centered_grid_inclusion_offset(
    inner: NestedScale, outer: NestedScale
) -> int:
    """Return the exact central-subgrid offset, or reject non-nesting grids."""
    difference = outer.sample_count - inner.sample_count
    if (
        inner.spacing != outer.spacing
        or difference < 0
        or difference % 2
    ):
        raise ValueError("centered midpoint grids are not exactly nested")
    return difference // 2


def validate_nested_scales(scales: Sequence[NestedScale]) -> None:
    """Check that every scale is an exact contiguous subset of the largest."""
    if not scales:
        raise ValueError("at least one scale is required")
    if len(set(scales)) != len(scales):
        raise ValueError("candidate scales must be distinct")
    outer = max(scales, key=lambda scale: scale.sample_count)
    for scale in scales:
        centered_grid_inclusion_offset(scale, outer)


def detect_dangerous_modes(
    workspace: ResourceLawWorkspace,
    baseline_scale: NestedScale,
    target_norms: Sequence[int] = (50,),
    count_per_target: int = 8,
    maximum_tail_norm: int | None = None,
) -> tuple[DangerousMode, ...]:
    """Rank explicit tail terms by their realized baseline contribution."""
    if count_per_target < 1:
        raise ValueError("count_per_target must be positive")
    available_maximum = int(workspace.finite_norms[-1])
    tail_maximum = (
        available_maximum
        if maximum_tail_norm is None
        else min(maximum_tail_norm, available_maximum)
    )
    design = baseline_scale.design()
    found: list[DangerousMode] = []
    for target in target_norms:
        first = int(workspace.finite_norms[0])
        if target < 1 or target >= first:
            raise ValueError("target must lie below the explicit tail range")
        start = first - int(workspace.finite_norms[0])
        stop = tail_maximum - int(workspace.finite_norms[0]) + 1
        norms = workspace.finite_norms[start:stop]
        arithmetic_weights = workspace.finite_weights[start:stop]
        responses = centered_cosine_response(
            np.log(norms / float(target)), design
        )
        contributions = arithmetic_weights * np.abs(responses)
        count = min(count_per_target, len(contributions))
        indices = np.argpartition(contributions, -count)[-count:]
        indices = indices[np.argsort(contributions[indices])[::-1]]
        found.extend(
            DangerousMode(
                target,
                int(norms[index]),
                float(arithmetic_weights[index]),
                float(responses[index]),
                float(contributions[index]),
            )
            for index in indices
        )
    return tuple(
        sorted(
            found,
            key=lambda mode: mode.weighted_contribution,
            reverse=True,
        )
    )


def response_matrix(
    scales: Sequence[NestedScale], modes: Sequence[DangerousMode]
) -> np.ndarray:
    """Map each nested window to its signed dangerous-mode signature."""
    if not scales or not modes:
        raise ValueError("at least one scale and one mode are required")
    validate_nested_scales(scales)
    frequencies = np.asarray([mode.log_frequency for mode in modes])
    return np.column_stack(
        [
            centered_cosine_response(frequencies, scale.design())
            for scale in scales
        ]
    )


def solve_positive_minimax(
    scales: Sequence[NestedScale],
    modes: Sequence[DangerousMode],
    remote_bounds: Mapping[int, Sequence[float]] | None = None,
) -> PositiveMinimaxResult:
    """Minimize the worst selected-target leakage by a positive ensemble.

    For every selected mode an epigraph variable encloses the absolute signed
    ensemble response.  For each target, the weighted sum of those epigraphs
    plus an optional componentwise remote upper bound is constrained by one
    common objective variable.  The resulting problem is a linear program.
    """
    scale_tuple = tuple(scales)
    mode_tuple = tuple(modes)
    signatures = response_matrix(scale_tuple, mode_tuple)
    scale_count = len(scale_tuple)
    mode_count = len(mode_tuple)
    targets = tuple(sorted({mode.target_norm for mode in mode_tuple}))
    variable_count = scale_count + mode_count + 1
    rho_index = variable_count - 1
    objective = np.zeros(variable_count)
    objective[rho_index] = 1.0
    inequalities: list[np.ndarray] = []
    right_sides: list[float] = []
    for mode_index in range(mode_count):
        for sign in (-1.0, 1.0):
            row = np.zeros(variable_count)
            row[:scale_count] = sign * signatures[mode_index]
            row[scale_count + mode_index] = -1.0
            inequalities.append(row)
            right_sides.append(0.0)
    for target in targets:
        row = np.zeros(variable_count)
        for mode_index, mode in enumerate(mode_tuple):
            if mode.target_norm == target:
                row[scale_count + mode_index] = mode.arithmetic_weight
        if remote_bounds is not None and target in remote_bounds:
            values = np.asarray(remote_bounds[target], dtype=float)
            if values.shape != (scale_count,) or np.any(values < 0):
                raise ValueError("remote bounds must be nonnegative per scale")
            row[:scale_count] = values
        row[rho_index] = -1.0
        inequalities.append(row)
        right_sides.append(0.0)
    equality = np.zeros((1, variable_count))
    equality[0, :scale_count] = 1.0
    solution = linprog(
        objective,
        A_ub=np.asarray(inequalities),
        b_ub=np.asarray(right_sides),
        A_eq=equality,
        b_eq=np.ones(1),
        bounds=[(0.0, None)] * variable_count,
        method="highs",
    )
    if not solution.success:
        raise ArithmeticError(f"positive minimax LP failed: {solution.message}")
    weights = np.asarray(solution.x[:scale_count])
    target_bounds = []
    combined = signatures @ weights
    for target in targets:
        selected = np.asarray(
            [mode.target_norm == target for mode in mode_tuple]
        )
        finite = sum(
            mode_tuple[index].arithmetic_weight * abs(combined[index])
            for index in np.flatnonzero(selected)
        )
        remote = 0.0
        if remote_bounds is not None and target in remote_bounds:
            remote = float(np.dot(weights, remote_bounds[target]))
        target_bounds.append((target, float(finite + remote)))
    return PositiveMinimaxResult(
        scale_tuple,
        tuple(float(weight) for weight in weights),
        float(solution.fun),
        tuple(target_bounds),
        str(solution.message),
    )


def search_sparse_supports(
    scales: Sequence[NestedScale],
    modes: Sequence[DangerousMode],
    support_size: int,
    remote_bounds: Mapping[int, Sequence[float]] | None = None,
    required_scale: NestedScale | None = None,
    limit: int | None = None,
) -> tuple[PositiveMinimaxResult, ...]:
    """Enumerate small supports and rank their exact finite LP optima."""
    scale_tuple = tuple(scales)
    if support_size < 1 or support_size > len(scale_tuple):
        raise ValueError("invalid support size")
    if required_scale is not None and required_scale not in scale_tuple:
        raise ValueError("required scale is absent")
    ranked = []
    for indices in itertools.combinations(range(len(scale_tuple)), support_size):
        subset = tuple(scale_tuple[index] for index in indices)
        if required_scale is not None and required_scale not in subset:
            continue
        subset_remote = None
        if remote_bounds is not None:
            subset_remote = {
                target: tuple(values[index] for index in indices)
                for target, values in remote_bounds.items()
            }
        ranked.append(solve_positive_minimax(subset, modes, subset_remote))
    ranked.sort(key=lambda result: result.objective)
    return tuple(ranked if limit is None else ranked[:limit])


def dyadic_rationalize(
    weights: Sequence[float], scale_bits: int = 16
) -> tuple[Fraction, ...]:
    """Round a probability vector to nonnegative dyadics with exact sum one."""
    values = np.asarray(weights, dtype=float)
    if (
        scale_bits < 1
        or values.ndim != 1
        or len(values) == 0
        or np.any(values < 0)
        or not np.isclose(float(np.sum(values)), 1.0, atol=1e-8)
    ):
        raise ValueError("weights must be a nonnegative probability vector")
    denominator = 1 << scale_bits
    scaled = values / float(np.sum(values)) * denominator
    numerators = np.floor(scaled).astype(np.int64)
    remainder = denominator - int(np.sum(numerators))
    order = np.argsort(-(scaled - numerators))
    numerators[order[:remainder]] += 1
    return tuple(Fraction(int(value), denominator) for value in numerators)


def materialize_outer_grid_weights(
    design: RationalMultiscaleDesign,
) -> np.ndarray:
    """Realize the multiscale measure on its one distinct outer sample grid."""
    outer = design.outer_scale
    weights = np.zeros(outer.sample_count)
    for scale, mixing_weight in zip(design.scales, design.weights):
        offset = centered_grid_inclusion_offset(scale, outer)
        local = cosine_window_weights(scale.design())
        weights[offset : offset + scale.sample_count] += (
            float(mixing_weight) * local
        )
    return weights


def reference_design() -> RationalMultiscaleDesign:
    """The degree-fourteen candidate promoted to formal verification."""
    return RationalMultiscaleDesign(
        (NestedScale(510, 2_550), NestedScale(1_780, 8_900)),
        (Fraction(125, 65_536), Fraction(65_411, 65_536)),
    )


def reference_report() -> dict[str, object]:
    """Reproduce dangerous-mode discovery and the sparse finite LP report."""
    workspace = prepare_workspace()
    outer = NestedScale(1_780, 8_900)
    modes = detect_dangerous_modes(
        workspace, outer, target_norms=(50,), count_per_target=8
    )
    candidates = proportional_scales(300, 800) + (outer,)
    remote_bounds = {
        50: tuple(
            fixed_degree_mellin_alias_remainder_bound(
                50,
                TRUNCATION,
                scale.design(),
                workspace.base_remainder,
                workspace.mellin_certificate,
                "cancellation",
            )
            for scale in candidates
        )
    }
    sparse = search_sparse_supports(
        candidates,
        modes,
        support_size=2,
        remote_bounds=remote_bounds,
        required_scale=outer,
        limit=5,
    )
    exact = reference_design()
    outer_weights = materialize_outer_grid_weights(exact)
    return {
        "scope": (
            "binary64 discovery report; formal validity is supplied only by "
            "the separate Arb/MPFR artifact"
        ),
        "dangerous_modes": [
            {
                **asdict(mode),
                "ratio": mode.ratio,
                "share_of_selected_contribution": (
                    mode.weighted_contribution
                    / sum(item.weighted_contribution for item in modes)
                ),
            }
            for mode in modes
        ],
        "best_sparse_supports": [
            {
                "objective": result.objective,
                "components": [
                    {
                        "observation_time": scale.observation_time,
                        "sample_count": scale.sample_count,
                        "weight": weight,
                    }
                    for scale, weight in result.active_components
                ],
            }
            for result in sparse
        ],
        "promoted_rational_design": {
            "components": [
                {
                    "observation_time": scale.observation_time,
                    "sample_count": scale.sample_count,
                    "weight": str(weight),
                }
                for scale, weight in zip(exact.scales, exact.weights)
            ],
            "distinct_sample_count": exact.outer_scale.sample_count,
            "minimum_outer_weight": float(np.min(outer_weights)),
            "weight_sum": float(np.sum(outer_weights)),
            "effective_sample_count": float(1.0 / np.sum(outer_weights**2)),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--compact", action="store_true", help="emit JSON without indentation"
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    print(
        json.dumps(
            reference_report(),
            indent=None if arguments.compact else 2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
