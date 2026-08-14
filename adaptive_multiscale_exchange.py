#!/usr/bin/env python3
"""Adaptive arithmetic-mode exchange and exact pair-support certificates.

The exchange loop is a binary64 discovery procedure.  Its selected finite
problem is then rebuilt with Arb response intervals.  Exact rational primal
and dual witnesses certify each two-scale support, while interval weakening
turns the dual witnesses into rigorous lower bounds for the true responses.
The resulting theorem concerns only the declared finite mode and scale sets;
the separate end-to-end certificate remains the recovery theorem.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Sequence

import numpy as np

from arithmetic_multiscale_sensing import (
    DangerousMode,
    NestedScale,
    proportional_scales,
    search_sparse_supports,
)
from degree_fourteen_resource_law import (
    TRUNCATION,
    ResourceLawWorkspace,
    prepare_workspace,
)
from fixed_degree_arithmetic_sensing import (
    fixed_degree_mellin_alias_remainder_bound,
)
from optimized_arithmetic_quadrature import centered_cosine_response
from verified_end_to_end_certificate import (
    exact_fixed_degree_coefficients_uint64,
    verified_centered_response_interval,
)


TARGET_NORM = 50
OUTER_SCALE = NestedScale(1_780, 8_900)
SHORT_SCALES = proportional_scales(300, 800)
INITIAL_TAIL_NORMS = (51, 52)
REFERENCE_EXCHANGE_ITERATIONS = 4
REFERENCE_BATCH_SIZE = 4
FORMAL_PRECISION = 192
PUBLISHED_SHORT_WEIGHT = Fraction(125, 65_536)


@dataclass(frozen=True)
class ExchangeStep:
    iteration: int
    selected_tail_norms: tuple[int, ...]
    short_time: int
    short_weight: float
    restricted_objective: float
    complete_target_finite_plus_remote: float
    added_tail_norms: tuple[int, ...]
    added_contributions: tuple[float, ...]


@dataclass(frozen=True)
class ResponseInterval:
    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if self.lower > self.upper:
            raise ValueError("response interval endpoints are reversed")

    @property
    def midpoint(self) -> Fraction:
        return (self.lower + self.upper) / 2

    @property
    def width(self) -> Fraction:
        return self.upper - self.lower

    def signed_lower(self, multiplier: Fraction) -> Fraction:
        if multiplier >= 0:
            return multiplier * self.lower
        return multiplier * self.upper


@dataclass(frozen=True)
class RationalPairProblem:
    short_scale: NestedScale
    outer_scale: NestedScale
    target_norm: int
    tail_norms: tuple[int, ...]
    arithmetic_weights: tuple[Fraction, ...]
    short_responses: tuple[ResponseInterval, ...]
    outer_responses: tuple[ResponseInterval, ...]

    def __post_init__(self) -> None:
        lengths = {
            len(self.tail_norms),
            len(self.arithmetic_weights),
            len(self.short_responses),
            len(self.outer_responses),
        }
        if lengths != {len(self.tail_norms)} or not self.tail_norms:
            raise ValueError("pair-problem vectors disagree")
        if any(weight <= 0 for weight in self.arithmetic_weights):
            raise ValueError("arithmetic weights must be positive")


@dataclass(frozen=True)
class ExactPairCertificate:
    short_weight: Fraction
    midpoint_objective: Fraction
    dual_variables: tuple[Fraction, ...]
    midpoint_dual_lower: Fraction
    robust_dual_lower: Fraction
    robust_primal_upper: Fraction


@dataclass(frozen=True)
class SupportFrontier:
    winner: ExactPairCertificate
    winner_problem: RationalPairProblem
    competitors: tuple[tuple[RationalPairProblem, ExactPairCertificate], ...]
    runner_up_time: int
    runner_up_robust_lower: Fraction
    support_separation: Fraction
    published_weight_upper: Fraction
    published_support_separation: Fraction


def _mode(
    workspace: ResourceLawWorkspace, tail_norm: int, target_norm: int
) -> DangerousMode:
    first = int(workspace.finite_norms[0])
    index = tail_norm - first
    if index < 0 or index >= len(workspace.finite_norms):
        raise ValueError("tail norm is outside the finite workspace")
    return DangerousMode(
        target_norm,
        tail_norm,
        float(workspace.finite_weights[index]),
        0.0,
        0.0,
    )


def _remote_bounds(
    workspace: ResourceLawWorkspace,
    scales: Sequence[NestedScale],
    target_norm: int,
) -> tuple[float, ...]:
    return tuple(
        fixed_degree_mellin_alias_remainder_bound(
            target_norm,
            TRUNCATION,
            scale.design(),
            workspace.base_remainder,
            workspace.mellin_certificate,
            "cancellation",
        )
        for scale in scales
    )


def adaptive_mode_exchange(
    workspace: ResourceLawWorkspace,
    short_scales: Sequence[NestedScale] = SHORT_SCALES,
    outer_scale: NestedScale = OUTER_SCALE,
    target_norm: int = TARGET_NORM,
    initial_tail_norms: Sequence[int] = INITIAL_TAIL_NORMS,
    iterations: int = REFERENCE_EXCHANGE_ITERATIONS,
    batch_size: int = REFERENCE_BATCH_SIZE,
) -> tuple[ExchangeStep, ...]:
    """Alternate sparse positive design with worst omitted-mode discovery."""
    if iterations < 1 or batch_size < 1:
        raise ValueError("iterations and batch size must be positive")
    candidates = tuple(short_scales) + (outer_scale,)
    remotes = _remote_bounds(workspace, candidates, target_norm)
    remote_map = {target_norm: remotes}
    selected = set(int(value) for value in initial_tail_norms)
    norms = workspace.finite_norms
    frequencies = np.log(norms / float(target_norm))
    steps = []
    for iteration in range(iterations):
        current = tuple(sorted(selected))
        modes = tuple(_mode(workspace, norm, target_norm) for norm in current)
        result = search_sparse_supports(
            candidates,
            modes,
            support_size=2,
            remote_bounds=remote_map,
            required_scale=outer_scale,
            limit=1,
        )[0]
        short_scale = result.scales[0]
        short_weight = result.weights[0]
        outer_weight = result.weights[1]
        response = (
            short_weight
            * centered_cosine_response(frequencies, short_scale.design())
            + outer_weight
            * centered_cosine_response(frequencies, outer_scale.design())
        )
        contributions = workspace.finite_weights * np.abs(response)
        finite = float(np.sum(contributions))
        short_index = candidates.index(short_scale)
        complete = finite + (
            short_weight * remotes[short_index]
            + outer_weight * remotes[-1]
        )
        available = np.ones(len(norms), dtype=bool)
        for norm in selected:
            available[norm - int(norms[0])] = False
        indices = np.flatnonzero(available)
        count = min(batch_size, len(indices))
        added_indices = indices[
            np.argpartition(contributions[indices], -count)[-count:]
        ]
        added_indices = added_indices[
            np.argsort(contributions[added_indices])[::-1]
        ]
        added_norms = tuple(int(norms[index]) for index in added_indices)
        steps.append(
            ExchangeStep(
                iteration,
                current,
                short_scale.observation_time,
                short_weight,
                result.objective,
                complete,
                added_norms,
                tuple(float(contributions[index]) for index in added_indices),
            )
        )
        selected.update(added_norms)
    return tuple(steps)


def build_pair_problem(
    short_scale: NestedScale,
    tail_norms: Sequence[int],
    outer_scale: NestedScale = OUTER_SCALE,
    target_norm: int = TARGET_NORM,
    degree: int = 14,
    precision: int = FORMAL_PRECISION,
) -> RationalPairProblem:
    """Rebuild a finite support problem with exact weights and Arb intervals."""
    norms = tuple(int(value) for value in tail_norms)
    coefficients = exact_fixed_degree_coefficients_uint64(max(norms), degree)
    arithmetic_weights = tuple(
        Fraction(int(coefficients[norm]), norm * norm) for norm in norms
    )
    short_responses = tuple(
        ResponseInterval(
            *verified_centered_response_interval(
                target_norm,
                norm,
                short_scale.observation_time,
                short_scale.sample_count,
                precision=precision,
            )
        )
        for norm in norms
    )
    outer_responses = tuple(
        ResponseInterval(
            *verified_centered_response_interval(
                target_norm,
                norm,
                outer_scale.observation_time,
                outer_scale.sample_count,
                precision=precision,
            )
        )
        for norm in norms
    )
    return RationalPairProblem(
        short_scale,
        outer_scale,
        target_norm,
        norms,
        arithmetic_weights,
        short_responses,
        outer_responses,
    )


def _midpoint_objective(
    problem: RationalPairProblem, short_weight: Fraction
) -> Fraction:
    outer_weight = 1 - short_weight
    return sum(
        coefficient
        * abs(
            short_weight * short.midpoint
            + outer_weight * outer.midpoint
        )
        for coefficient, short, outer in zip(
            problem.arithmetic_weights,
            problem.short_responses,
            problem.outer_responses,
        )
    )


def _candidate_breakpoints(problem: RationalPairProblem) -> tuple[Fraction, ...]:
    points = {Fraction(), Fraction(1)}
    for short, outer in zip(
        problem.short_responses, problem.outer_responses
    ):
        delta = short.midpoint - outer.midpoint
        if delta:
            point = -outer.midpoint / delta
            if 0 <= point <= 1:
                points.add(point)
    return tuple(sorted(points))


def _choose_free_dual_variables(
    coefficients: Sequence[Fraction],
    fixed_slope: Fraction,
    desired_slope: Fraction,
) -> tuple[Fraction, ...]:
    """Choose values in [-1,1] whose weighted slope reaches the target."""
    target = desired_slope - fixed_slope
    result = []
    for index, coefficient in enumerate(coefficients):
        remaining = sum(abs(value) for value in coefficients[index + 1 :])
        capacity = abs(coefficient)
        lower = max(-capacity, target - remaining)
        upper = min(capacity, target + remaining)
        if lower > upper:
            raise ArithmeticError("dual subgradient interval is infeasible")
        contribution = min(max(target, lower), upper)
        result.append(
            Fraction() if coefficient == 0 else contribution / coefficient
        )
        target -= contribution
    if target:
        raise ArithmeticError("dual subgradient construction did not close")
    return tuple(result)


def solve_exact_pair_problem(
    problem: RationalPairProblem,
) -> ExactPairCertificate:
    """Solve the midpoint rational LP and weaken its dual over Arb intervals."""
    points = _candidate_breakpoints(problem)
    objective, short_weight = min(
        (_midpoint_objective(problem, point), point) for point in points
    )
    outer_weight = 1 - short_weight
    dual: list[Fraction | None] = []
    free_indices = []
    slope_coefficients = []
    fixed_slope = Fraction()
    for index, (coefficient, short, outer) in enumerate(
        zip(
            problem.arithmetic_weights,
            problem.short_responses,
            problem.outer_responses,
        )
    ):
        short_value = short.midpoint
        outer_value = outer.midpoint
        realized = short_weight * short_value + outer_weight * outer_value
        slope_coefficient = coefficient * (short_value - outer_value)
        if realized > 0:
            value: Fraction | None = Fraction(1)
        elif realized < 0:
            value = Fraction(-1)
        else:
            value = None
            free_indices.append(index)
            slope_coefficients.append(slope_coefficient)
        dual.append(value)
        if value is not None:
            fixed_slope += slope_coefficient * value
    slope_radius = sum(abs(value) for value in slope_coefficients)
    slope_lower = fixed_slope - slope_radius
    slope_upper = fixed_slope + slope_radius
    if 0 < short_weight < 1:
        if not slope_lower <= 0 <= slope_upper:
            raise ArithmeticError("interior optimum has no zero subgradient")
        desired_slope = Fraction()
    elif short_weight == 0:
        if slope_upper < 0:
            raise ArithmeticError("left endpoint violates optimality")
        desired_slope = max(Fraction(), slope_lower)
    else:
        if slope_lower > 0:
            raise ArithmeticError("right endpoint violates optimality")
        desired_slope = min(Fraction(), slope_upper)
    free_values = _choose_free_dual_variables(
        slope_coefficients, fixed_slope, desired_slope
    )
    for index, value in zip(free_indices, free_values):
        dual[index] = value
    dual_values = tuple(value for value in dual if value is not None)
    if len(dual_values) != len(problem.tail_norms):
        raise ArithmeticError("dual vector is incomplete")
    midpoint_short_score = sum(
        coefficient * value * response.midpoint
        for coefficient, value, response in zip(
            problem.arithmetic_weights, dual_values, problem.short_responses
        )
    )
    midpoint_outer_score = sum(
        coefficient * value * response.midpoint
        for coefficient, value, response in zip(
            problem.arithmetic_weights, dual_values, problem.outer_responses
        )
    )
    midpoint_lower = min(midpoint_short_score, midpoint_outer_score)
    robust_short_score = sum(
        coefficient * response.signed_lower(value)
        for coefficient, value, response in zip(
            problem.arithmetic_weights, dual_values, problem.short_responses
        )
    )
    robust_outer_score = sum(
        coefficient * response.signed_lower(value)
        for coefficient, value, response in zip(
            problem.arithmetic_weights, dual_values, problem.outer_responses
        )
    )
    robust_lower = min(robust_short_score, robust_outer_score)
    robust_upper = interval_objective_upper(problem, short_weight)
    certificate = ExactPairCertificate(
        short_weight,
        objective,
        dual_values,
        midpoint_lower,
        robust_lower,
        robust_upper,
    )
    verify_exact_pair_certificate(problem, certificate)
    return certificate


def interval_objective_upper(
    problem: RationalPairProblem, short_weight: Fraction
) -> Fraction:
    """Upper-bound selected-mode leakage at one exact feasible weight."""
    if not 0 <= short_weight <= 1:
        raise ValueError("short weight must lie in the probability interval")
    outer_weight = 1 - short_weight
    total = Fraction()
    for coefficient, short, outer in zip(
        problem.arithmetic_weights,
        problem.short_responses,
        problem.outer_responses,
    ):
        lower = short_weight * short.lower + outer_weight * outer.lower
        upper = short_weight * short.upper + outer_weight * outer.upper
        total += coefficient * max(abs(lower), abs(upper))
    return total


def verify_exact_pair_certificate(
    problem: RationalPairProblem, certificate: ExactPairCertificate
) -> None:
    """Check a primal/dual pair using exact rational arithmetic only."""
    if len(certificate.dual_variables) != len(problem.tail_norms):
        raise ValueError("dual vector length does not match the problem")
    if not 0 <= certificate.short_weight <= 1:
        raise ValueError("primal weight is infeasible")
    if any(abs(value) > 1 for value in certificate.dual_variables):
        raise ValueError("dual variable lies outside [-1,1]")
    objective = _midpoint_objective(problem, certificate.short_weight)
    if objective != certificate.midpoint_objective:
        raise ValueError("midpoint primal objective is incorrect")
    short_score = sum(
        coefficient * value * response.midpoint
        for coefficient, value, response in zip(
            problem.arithmetic_weights,
            certificate.dual_variables,
            problem.short_responses,
        )
    )
    outer_score = sum(
        coefficient * value * response.midpoint
        for coefficient, value, response in zip(
            problem.arithmetic_weights,
            certificate.dual_variables,
            problem.outer_responses,
        )
    )
    midpoint_lower = min(short_score, outer_score)
    if midpoint_lower != certificate.midpoint_dual_lower:
        raise ValueError("midpoint dual objective is incorrect")
    if midpoint_lower != objective:
        raise ValueError("midpoint primal and dual objectives do not agree")
    robust_short = sum(
        coefficient * response.signed_lower(value)
        for coefficient, value, response in zip(
            problem.arithmetic_weights,
            certificate.dual_variables,
            problem.short_responses,
        )
    )
    robust_outer = sum(
        coefficient * response.signed_lower(value)
        for coefficient, value, response in zip(
            problem.arithmetic_weights,
            certificate.dual_variables,
            problem.outer_responses,
        )
    )
    if min(robust_short, robust_outer) != certificate.robust_dual_lower:
        raise ValueError("robust dual lower bound is incorrect")
    robust_upper = interval_objective_upper(
        problem, certificate.short_weight
    )
    if robust_upper != certificate.robust_primal_upper:
        raise ValueError("robust primal upper bound is incorrect")
    if certificate.robust_dual_lower > certificate.robust_primal_upper:
        raise ValueError("robust bounds are inconsistent")


def build_support_frontier(
    tail_norms: Sequence[int],
    short_scales: Sequence[NestedScale] = SHORT_SCALES,
    outer_scale: NestedScale = OUTER_SCALE,
    precision: int = FORMAL_PRECISION,
) -> SupportFrontier:
    """Formally separate the best declared two-scale support from all others."""
    pairs = []
    for scale in short_scales:
        problem = build_pair_problem(
            scale,
            tail_norms,
            outer_scale=outer_scale,
            precision=precision,
        )
        pairs.append((problem, solve_exact_pair_problem(problem)))
    winner_problem, winner = min(
        pairs, key=lambda item: item[1].midpoint_objective
    )
    competitors = tuple(
        item for item in pairs if item[0].short_scale != winner_problem.short_scale
    )
    runner_problem, runner = min(
        competitors, key=lambda item: item[1].robust_dual_lower
    )
    separation = runner.robust_dual_lower - winner.robust_primal_upper
    if separation <= 0:
        raise ArithmeticError("Arb intervals do not separate the best support")
    published_upper = interval_objective_upper(
        winner_problem, PUBLISHED_SHORT_WEIGHT
    )
    published_separation = runner.robust_dual_lower - published_upper
    if published_separation <= 0:
        raise ArithmeticError("published dyadic weight loses support separation")
    return SupportFrontier(
        winner,
        winner_problem,
        competitors,
        runner_problem.short_scale.observation_time,
        runner.robust_dual_lower,
        separation,
        published_upper,
        published_separation,
    )


def reference_report() -> dict[str, object]:
    workspace = prepare_workspace()
    exchange = adaptive_mode_exchange(workspace)
    selected = exchange[-1].selected_tail_norms
    frontier = build_support_frontier(selected)
    return {
        "scope": (
            "binary64 adaptive discovery followed by exact-rational dual "
            "verification over Arb response intervals for the declared finite "
            "mode and two-scale support sets"
        ),
        "exchange": [asdict(step) for step in exchange],
        "formal_mode_set": list(selected),
        "winner": {
            "short_time": frontier.winner_problem.short_scale.observation_time,
            "midpoint_optimal_weight": str(frontier.winner.short_weight),
            "midpoint_objective": str(frontier.winner.midpoint_objective),
            "midpoint_objective_decimal": float(
                frontier.winner.midpoint_objective
            ),
            "robust_lower": str(frontier.winner.robust_dual_lower),
            "robust_upper": str(frontier.winner.robust_primal_upper),
            "published_dyadic_weight": str(PUBLISHED_SHORT_WEIGHT),
            "published_weight_upper": str(frontier.published_weight_upper),
        },
        "runner_up": {
            "short_time": frontier.runner_up_time,
            "robust_lower": str(frontier.runner_up_robust_lower),
        },
        "support_separation": str(frontier.support_separation),
        "support_separation_decimal": float(frontier.support_separation),
        "published_support_separation": str(
            frontier.published_support_separation
        ),
        "published_support_separation_decimal": float(
            frontier.published_support_separation
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compact", action="store_true")
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
