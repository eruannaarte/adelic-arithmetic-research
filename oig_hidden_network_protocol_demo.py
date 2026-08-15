"""Exact protocol-design demo on a nonreversible hidden Markov network."""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from typing import Sequence

from oig_protocol_design_engine import (
    RationalProtocol,
    design_protocols,
    exponential_time_response,
    rational_matrix,
)


def hidden_cycle_laplacian():
    """A conservative, irreducible, non-symmetric four-state Laplacian."""
    return rational_matrix(
        [
            [1, 0, -1, 0],
            [-1, 3, 0, Fraction(-1, 2)],
            [0, -2, 1, 0],
            [0, -1, 0, Fraction(1, 2)],
        ]
    )


def tangent_injection():
    """Three mass-preserving source coordinates relative to state three."""
    return rational_matrix(
        [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [-1, -1, -1],
        ]
    )


def tangent_source_metric():
    return rational_matrix([[2, 1, 1], [1, 2, 1], [1, 1, 2]])


def candidate_protocols() -> tuple[RationalProtocol, ...]:
    laplacian = hidden_cycle_laplacian()
    injection = tangent_injection()
    declarations = (
        ("state-0 fast", [[1, 0, 0, 0]], 4, [[1]], 1),
        ("state-3 slow", [[0, 0, 0, 1]], 1, [[2]], 2),
        ("middle aggregate", [[0, 1, 1, 0]], Fraction(1, 2), [[1]], 1),
        ("state-1 medium", [[0, 1, 0, 0]], 2, [[1]], Fraction(3, 2)),
        (
            "paired occupancy",
            [[1, 0, 0, 0], [0, 0, 1, 0]],
            1,
            [[2, 0], [0, 1]],
            3,
        ),
    )
    protocols = []
    for name, sensor, rate, precision, cost in declarations:
        response = exponential_time_response(
            laplacian,
            injection,
            sensor,
            rate,
        )
        protocols.append(
            RationalProtocol(
                name,
                response,
                rational_matrix(precision),
                Fraction(cost),
            )
        )
    return tuple(protocols)


def run_demo(weight_denominator: int = 100_000) -> dict[str, object]:
    protocols = candidate_protocols()
    report = design_protocols(
        protocols,
        tangent_source_metric(),
        weight_denominator=weight_denominator,
        dual_vector_scale=10**8,
        amplitude=1,
        exposure_multiplier=100,
    )
    report["benchmark"] = {
        "name": "four-state nonreversible hidden cycle with a side branch",
        "dynamics": "continuous-time Markov chain observed at independent exponential times",
        "response_identity": "E[C exp(-T L) J] = C alpha(alpha I+L)^-1 J",
        "laplacian_is_non_symmetric": True,
        "laplacian_columns_sum_exactly_to_zero": True,
        "interventions_preserve_total_mass": True,
        "candidate_count": len(protocols),
    }
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weight-denominator", type=int, default=100_000)
    parser.add_argument("--output")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    report = run_demo(arguments.weight_denominator)
    payload = json.dumps(report, indent=2, sort_keys=True)
    if arguments.output:
        with open(arguments.output, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.write("\n")
    else:
        print(payload)
    return 0 if report["overall_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
