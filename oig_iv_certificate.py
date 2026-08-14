#!/usr/bin/env python3
"""Outward-rounded certificate for the Stage IV finite-grid E-design.

The floating optimization in ``operational_information_geometry_iv.py`` found
a six-time dyadic design for the A-to-B response of the 6 x 6 rate-modulated
product chain.  This module does *not* repeat that optimization.  It checks a
fixed rational primal design and a fixed rational dual witness using Arb ball
arithmetic.

Two grids are certified:

* the canonical geometric grid t_i = 10**(-3 + 4 i / 119); and
* the exact dyadic rational values of the binary64 NumPy grid used by the
  original experiment.

All decisions used by the certificate are comparisons between Arb balls and
exact rationals.  Midpoints in the JSON report are descriptive only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from typing import Iterable, Sequence

import numpy as np
import flint
from flint import arb, arb_mat, ctx, fmpq

from operational_information_geometry_iv import STAGE_IV_REFERENCE_TIME_HEX


STATE_COUNT = 6
TANGENT_DIMENSION = STATE_COUNT - 1
CANDIDATE_COUNT = 120
BINARY64_GRID_SHA256 = (
    "1ba037c6f66f515a0cb3513fb5b177e5f74c0eeb8d0f75778511f7f052dec00e"
)

# Exact dyadic primal.  Indices are zero-based and refer to either declared
# 120-point grid.  The numerator sum is exactly 4096.
PRIMAL_DENOMINATOR = 4096
PRIMAL_NUMERATORS = {
    62: 963,
    76: 71,
    77: 669,
    87: 1289,
    105: 294,
    106: 810,
}

# Rational tangent coordinates use E=(e_0-e_5,...,e_4-e_5).  The Euclidean
# source norm is u^T Q u with the exact Gram Q=E^T E.
TANGENT_METRIC = tuple(
    tuple(2 if row == column else 1 for column in range(TANGENT_DIMENSION))
    for row in range(TANGENT_DIMENSION)
)

# Exact integer factor for the rational generalized-dual witness
#
#                  B B^T
#            Z = ---------,       S = tr(B B^T Q).
#                    S
#
# Thus Z is positive semidefinite and tr(ZQ)=1 by exact integer arithmetic.
DUAL_FACTOR = (
    (-83_192_408_875, 105_456_840_882),
    (213_863_105_956, -399_443_523_170),
    (-118_297_442_349, 672_776_519_441),
    (-185_640_175_907, -579_962_301_934),
    (292_803_378_790, 218_679_629_676),
)
DUAL_NORMALIZER = sum(
    DUAL_FACTOR[row][factor_column]
    * TANGENT_METRIC[row][column]
    * DUAL_FACTOR[column][factor_column]
    for factor_column in range(2)
    for row in range(TANGENT_DIMENSION)
    for column in range(TANGENT_DIMENSION)
)

# Exact rational objective bracket.  Decimal strings are used only to make the
# intended scale legible; Fraction makes the represented values exact.
PRIMAL_LOWER_BOUND = Fraction("0.000000004982412")
DUAL_UPPER_BOUND = Fraction("0.000000004982942")

# Extra rational margins checked by Arb, beyond the sign comparisons needed by
# the proof.  The five entries correspond to the leading principal minors of
# G_primal - PRIMAL_LOWER_BOUND Q.
PRINCIPAL_MINOR_LOWER_BOUNDS = tuple(
    Fraction(value)
    for value in ("1e-2", "7e-8", "1e-13", "4e-25", "1e-40")
)
DUAL_SLACK_LOWER_BOUND = Fraction("8e-16")

# Every recorded ball radius is required to lie below this exact rational cap.
# It bounds numerical enclosure width, not model or statistical uncertainty.
NUMERICAL_RADIUS_CAP = Fraction("1e-54")


def _arb_rational(value: Fraction | int) -> arb:
    """Embed an exact Python rational in an enclosing Arb ball."""
    if isinstance(value, int):
        return arb(value)
    return arb(fmpq(value.numerator, value.denominator))


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _approx_midpoint(value: arb) -> float:
    """Return a display-only binary64 approximation to an Arb midpoint."""
    return float(value.mid())


def _path_laplacian_entries(side_length: int) -> list[list[int]]:
    laplacian = [[0 for _ in range(side_length)] for _ in range(side_length)]
    for left in range(side_length - 1):
        right = left + 1
        laplacian[left][left] += 1
        laplacian[right][right] += 1
        laplacian[left][right] -= 1
        laplacian[right][left] -= 1
    return laplacian


def _exact_model_matrices() -> tuple[arb_mat, arb_mat, arb_mat]:
    """Build the exact declared generator, marginal, and rational injection.

    The generator is

        P6 kron I + diag(1 + 4 a / 25) kron P6,  a=0,...,5.

    This is Stage IV's strength g=4/5 and modulation d_a=a/5, written
    directly over the rationals instead of imported through binary64 arrays.
    """
    side = STATE_COUNT
    joint = side * side
    path = _path_laplacian_entries(side)
    entries = [[arb(0) for _ in range(joint)] for _ in range(joint)]

    # P6 kron I.
    for left in range(side):
        for other_left in range(side):
            for right in range(side):
                entries[left * side + right][other_left * side + right] += path[
                    left
                ][other_left]

    # diag(1 + 4a/25) kron P6.
    for left in range(side):
        rate = _arb_rational(Fraction(25 + 4 * left, 25))
        for right in range(side):
            for other_right in range(side):
                entries[left * side + right][left * side + other_right] += (
                    rate * path[right][other_right]
                )
    generator = arb_mat(entries)

    # B-marginal M_B = 1_A^T kron I_B.
    measurement = arb_mat(side, joint)
    for right in range(side):
        for left in range(side):
            measurement[right, left * side + right] = 1

    # J_A = E_A kron e_0 with E=(e_0-e_5,...,e_4-e_5).  Unlike the
    # orthonormal Helmert basis used to discover the design, this injection and
    # its metric Q=E^T E are entirely rational.
    intervention = arb_mat(joint, side - 1)
    for column in range(side - 1):
        intervention[column * side, column] = 1
        intervention[(side - 1) * side, column] = -1
    return generator, measurement, intervention


def _canonical_geometric_times() -> tuple[arb, ...]:
    """Return balls enclosing the exact numbers 10**(-3 + 4i/119)."""
    return tuple(
        arb(10) ** fmpq(-3 * 119 + 4 * index, 119)
        for index in range(CANDIDATE_COUNT)
    )


def _binary64_reference_times() -> tuple[tuple[arb, ...], str, tuple[str, ...]]:
    """Return exact balls for the frozen published binary64 candidate grid."""
    hex_values = STAGE_IV_REFERENCE_TIME_HEX
    digest = hashlib.sha256("\n".join(hex_values).encode("ascii")).hexdigest()
    times = []
    for hex_value in hex_values:
        value = float.fromhex(hex_value)
        numerator, denominator = float(value).as_integer_ratio()
        times.append(_arb_rational(Fraction(numerator, denominator)))
    return tuple(times), digest, hex_values


def _radius_audit(values: Iterable[arb]) -> dict[str, object]:
    """Check every radius against the cap without interval max heuristics.

    Comparing two overlapping radius balls is not a reliable way to select a
    rigorous maximum.  The proof therefore checks each radius separately.  A
    binary64 maximum of their midpoints is included only as a descriptive
    scale indicator.
    """
    cap = _arb_rational(NUMERICAL_RADIUS_CAP)
    count = 0
    all_below = True
    approximate_maximum = 0.0
    for value in values:
        count += 1
        radius = value.rad()
        all_below = all_below and bool(radius < cap)
        approximate_maximum = max(approximate_maximum, _approx_midpoint(radius))
    return {
        "quantity_count": count,
        "approximate_maximum_radius": approximate_maximum,
        "exact_radius_cap": _fraction_text(NUMERICAL_RADIUS_CAP),
        "every_radius_strictly_below_cap": all_below,
    }


def _information_matrices(
    generator: arb_mat,
    measurement: arb_mat,
    intervention: arb_mat,
    times: Sequence[arb],
) -> tuple[list[arb_mat], dict[str, dict[str, object]]]:
    information: list[arb_mat] = []
    response_entries: list[arb] = []
    information_entries: list[arb] = []
    for time in times:
        response = measurement * (generator * (-time)).exp() * intervention
        candidate = response.transpose() * response
        information.append(candidate)
        response_entries.extend(response.entries())
        information_entries.extend(candidate.entries())
    return information, {
        "time": _radius_audit(times),
        "response": _radius_audit(response_entries),
        "information": _radius_audit(information_entries),
    }


def _primal_audit(information: Sequence[arb_mat]) -> dict[str, object]:
    dimension = TANGENT_DIMENSION
    gram = arb_mat(dimension, dimension)
    for index, numerator in PRIMAL_NUMERATORS.items():
        gram += information[index] * _arb_rational(
            Fraction(numerator, PRIMAL_DENOMINATOR)
        )

    # In rational tangent coordinates the E-optimal constraint is the
    # generalized inequality G - z Q >= 0, Q=E^T E.
    shifted = arb_mat(
        [
            [
                gram[row, column]
                - _arb_rational(PRIMAL_LOWER_BOUND)
                * TANGENT_METRIC[row][column]
                for column in range(dimension)
            ]
            for row in range(dimension)
        ]
    )
    minors = []
    all_positive = True
    all_above_declared_margins = True
    determinant_intervals: list[arb] = []
    for size, declared_lower in enumerate(PRINCIPAL_MINOR_LOWER_BOUNDS, start=1):
        principal = arb_mat(
            [[shifted[row, column] for column in range(size)] for row in range(size)]
        )
        determinant = principal.det()
        certainly_positive = bool(determinant > 0)
        above_declared = bool(determinant > _arb_rational(declared_lower))
        all_positive = all_positive and certainly_positive
        all_above_declared_margins = (
            all_above_declared_margins and above_declared
        )
        determinant_intervals.append(determinant)
        minors.append(
            {
                "order": size,
                "interval": str(determinant),
                "approximate_midpoint": _approx_midpoint(determinant),
                "declared_exact_lower_margin": _fraction_text(declared_lower),
                "certainly_above_declared_margin": above_declared,
            }
        )

    return {
        "denominator": PRIMAL_DENOMINATOR,
        "active_indices_zero_based": list(PRIMAL_NUMERATORS),
        "active_numerators": list(PRIMAL_NUMERATORS.values()),
        "numerator_sum": sum(PRIMAL_NUMERATORS.values()),
        "weights_are_exactly_feasible": bool(
            sum(PRIMAL_NUMERATORS.values()) == PRIMAL_DENOMINATOR
            and all(value >= 0 for value in PRIMAL_NUMERATORS.values())
        ),
        "exact_objective_lower_bound": _fraction_text(PRIMAL_LOWER_BOUND),
        "objective_lower_bound_decimal": float(PRIMAL_LOWER_BOUND),
        "leading_principal_minors": minors,
        "sylvester_positive_definite": all_positive,
        "all_declared_minor_margins_verified": all_above_declared_margins,
        "gram_radius_audit": _radius_audit(gram.entries()),
        "determinant_radius_audit": _radius_audit(determinant_intervals),
    }


def _dual_sensitivity(candidate: arb_mat) -> arb:
    """Evaluate tr((BB^T/S) A) as sum_c b_c^T A b_c / S."""
    total = arb(0)
    for factor_column in range(2):
        for row in range(TANGENT_DIMENSION):
            for column in range(TANGENT_DIMENSION):
                total += (
                    DUAL_FACTOR[row][factor_column]
                    * candidate[row, column]
                    * DUAL_FACTOR[column][factor_column]
                )
    return total / arb(DUAL_NORMALIZER)


def _dual_audit(information: Sequence[arb_mat]) -> dict[str, object]:
    upper = _arb_rational(DUAL_UPPER_BOUND)
    declared_slack = _arb_rational(DUAL_SLACK_LOWER_BOUND)
    all_constraints = True
    all_slacks = True
    sensitivities: list[arb] = []
    closest_index = -1
    closest_sensitivity: arb | None = None
    smallest_midpoint_slack = float("inf")
    for index, candidate in enumerate(information):
        sensitivity = _dual_sensitivity(candidate)
        sensitivities.append(sensitivity)
        slack = upper - sensitivity
        all_constraints = all_constraints and bool(sensitivity < upper)
        all_slacks = all_slacks and bool(slack > declared_slack)
        midpoint_slack = _approx_midpoint(slack)
        if midpoint_slack < smallest_midpoint_slack:
            smallest_midpoint_slack = midpoint_slack
            closest_index = index
            closest_sensitivity = sensitivity

    assert closest_sensitivity is not None
    exact_metric_trace_numerator = sum(
        DUAL_FACTOR[row][factor_column]
        * TANGENT_METRIC[row][column]
        * DUAL_FACTOR[column][factor_column]
        for factor_column in range(2)
        for row in range(TANGENT_DIMENSION)
        for column in range(TANGENT_DIMENSION)
    )
    return {
        "integer_factor": [list(row) for row in DUAL_FACTOR],
        "normalizer": DUAL_NORMALIZER,
        "exact_metric_trace_numerator": exact_metric_trace_numerator,
        "exact_tangent_metric": [list(row) for row in TANGENT_METRIC],
        "exact_psd_factorization": "Z = B B^T / normalizer",
        "metric_trace_is_exactly_one": (
            exact_metric_trace_numerator == DUAL_NORMALIZER
        ),
        "positive_semidefinite_by_factorization": True,
        "exact_objective_upper_bound": _fraction_text(DUAL_UPPER_BOUND),
        "objective_upper_bound_decimal": float(DUAL_UPPER_BOUND),
        "constraints_audited": len(information),
        "all_candidate_constraints_strictly_verified": all_constraints,
        "declared_exact_slack_lower_bound": _fraction_text(
            DUAL_SLACK_LOWER_BOUND
        ),
        "all_candidate_slacks_above_declared_bound": all_slacks,
        "closest_candidate_index_zero_based": closest_index,
        "closest_candidate_sensitivity_interval": str(closest_sensitivity),
        "approximate_smallest_slack": smallest_midpoint_slack,
        "sensitivity_radius_audit": _radius_audit(sensitivities),
    }


def _certify_one_grid(label: str, times: Sequence[arb]) -> dict[str, object]:
    if len(times) != CANDIDATE_COUNT:
        raise ValueError("the certificate requires exactly 120 candidate times")
    generator, measurement, intervention = _exact_model_matrices()
    information, radius_audits = _information_matrices(
        generator, measurement, intervention, times
    )
    primal = _primal_audit(information)
    dual = _dual_audit(information)
    radius_pass = all(
        audit["every_radius_strictly_below_cap"]
        for audit in radius_audits.values()
    )
    passed = bool(
        primal["weights_are_exactly_feasible"]
        and primal["sylvester_positive_definite"]
        and primal["all_declared_minor_margins_verified"]
        and primal["gram_radius_audit"]["every_radius_strictly_below_cap"]
        and primal["determinant_radius_audit"][
            "every_radius_strictly_below_cap"
        ]
        and dual["metric_trace_is_exactly_one"]
        and dual["positive_semidefinite_by_factorization"]
        and dual["all_candidate_constraints_strictly_verified"]
        and dual["all_candidate_slacks_above_declared_bound"]
        and dual["sensitivity_radius_audit"]["every_radius_strictly_below_cap"]
        and radius_pass
    )
    return {
        "grid": label,
        "candidate_count": len(times),
        "primal": primal,
        "dual": dual,
        "construction_radius_audits": radius_audits,
        "certificate_passed": passed,
    }


def run_interval_certificate(
    precision_bits: int = 192,
    grids: Sequence[str] = ("canonical", "binary64"),
) -> dict[str, object]:
    """Run the complete outward-rounded finite-grid certificate.

    ``canonical`` certifies the exact algebraic grid
    ``10**(-3 + 4i/119)``.  ``binary64`` certifies the exact dyadic values
    frozen from the original NumPy expression in the Stage IV implementation.
    """
    if precision_bits < 128:
        raise ValueError("at least 128 bits are required for the declared margins")
    requested = tuple(grids)
    invalid = set(requested) - {"canonical", "binary64"}
    if invalid or not requested:
        raise ValueError("grids must be a nonempty subset of canonical,binary64")

    rows = []
    binary_digest = None
    binary_endpoint_hex = None
    binary_digest_matches_declared = None
    with ctx.workprec(precision_bits):
        for grid in requested:
            if grid == "canonical":
                rows.append(
                    _certify_one_grid(
                        "exact t_i = 10^(-3 + 4i/119)",
                        _canonical_geometric_times(),
                    )
                )
            else:
                times, binary_digest, hex_values = _binary64_reference_times()
                binary_endpoint_hex = [hex_values[0], hex_values[-1]]
                binary_digest_matches_declared = (
                    binary_digest == BINARY64_GRID_SHA256
                )
                rows.append(
                    _certify_one_grid(
                        "frozen exact binary64 values from numpy.geomspace",
                        times,
                    )
                )

    relative_width = (DUAL_UPPER_BOUND - PRIMAL_LOWER_BOUND) / PRIMAL_LOWER_BOUND
    report = {
        "certificate": (
            "outward-rounded primal/dual bracket for the Stage IV finite-grid "
            "positive multiscale A-to-B response design"
        ),
        "arb_precision_bits": precision_bits,
        "python_flint_version": flint.__version__,
        "numpy_version": np.__version__,
        "model": (
            "P6 kron I + diag(1+4a/25) kron P6, rational A tangent "
            "basis (e_i-e_5) at B state 0, complete B-marginal response, "
            "generalized source metric Q=E^T E"
        ),
        "exact_optimum_bracket": {
            "lower": _fraction_text(PRIMAL_LOWER_BOUND),
            "upper": _fraction_text(DUAL_UPPER_BOUND),
            "lower_decimal": float(PRIMAL_LOWER_BOUND),
            "upper_decimal": float(DUAL_UPPER_BOUND),
            "absolute_width": _fraction_text(
                DUAL_UPPER_BOUND - PRIMAL_LOWER_BOUND
            ),
            "relative_width": float(relative_width),
            "certified_primal_fraction_of_upper": float(
                PRIMAL_LOWER_BOUND / DUAL_UPPER_BOUND
            ),
        },
        "declared_binary64_grid_sha256_of_hex_lines": BINARY64_GRID_SHA256,
        "computed_binary64_grid_sha256_of_hex_lines": binary_digest,
        "binary64_grid_digest_matches_declared": binary_digest_matches_declared,
        "binary64_endpoint_hex": binary_endpoint_hex,
        "grid_certificates": rows,
        "all_requested_grids_certified": bool(
            rows
            and all(row["certificate_passed"] for row in rows)
            and (
                "binary64" not in requested
                or binary_digest_matches_declared is True
            )
        ),
        "scope": (
            "computer-assisted proof for two declared 120-point grids only; "
            "it is not a continuum-time optimum, a formal-proof-assistant "
            "derivation, or a bound on model/statistical uncertainty"
        ),
    }
    return report


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--precision-bits", type=int, default=192)
    parser.add_argument(
        "--grid",
        choices=("both", "canonical", "binary64"),
        default="both",
    )
    return parser.parse_args()


def main() -> None:
    arguments = _parse_arguments()
    grids = (
        ("canonical", "binary64")
        if arguments.grid == "both"
        else (arguments.grid,)
    )
    report = run_interval_certificate(arguments.precision_bits, grids)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
