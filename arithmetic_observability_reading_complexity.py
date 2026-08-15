#!/usr/bin/env python3
"""Arb certificate for finite arithmetic-observability reading schedules.

The frozen model is

    F(C, u; t) = C product_j Q_4(u_j p_j^(-i t)),

on the labelled primes ``(2, 3, 5)``.  This checker certifies only finite,
explicit calculations used by the reading-complexity argument:

* two nonzero complex readings have a full four-real-dimensional Jacobian at
  one positive rational parameter point, with ``J_R^T J_R - 2 I`` positive
  definite;
* the four complex readings at ``0, 1/10, 1/5, 3/10`` have a nonzero complex
  Jacobian at the same point and avoid every fourth-root same-axis resonance;
* the exact Chow-ring combinatorics for the associated tridegree-(3,3,3)
  system give ``3! * 3^3 = 162``;
* the 64 equally spaced readings ``t_m=m/10`` have 64 pairwise distinct
  prime-box Vandermonde nodes, with a certified squared chord separation.

Arb encloses every logarithm, pi, and complex exponential.  Binary floating
point is not used for proof decisions.  The algebraic-geometric implications
of basepoint freeness and the Vandermonde determinant formula remain ordinary
mathematical arguments; this artifact certifies their frozen finite inputs.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Iterable, Sequence

import flint
from flint import acb, acb_mat, arb, arb_mat, ctx, fmpq


SCHEMA = "arithmetic-observability-reading-complexity-v1"
FORMAL_PRECISION_BITS = 256
MIN_PRECISION_BITS = 192
MAX_PRECISION_BITS = 1024

MAX_ARTIFACT_BYTES = 150_000
MAX_CONTAINER_ITEMS = 256
MAX_JSON_DEPTH = 18
MAX_TEXT_FIELD_LENGTH = 1024
MAX_INTEGER_BITS = 1024

PRIMES = (2, 3, 5)
AXIS_COUNT = 3
EXPONENTS_PER_AXIS = 4
POLYNOMIAL_DEGREE = EXPONENTS_PER_AXIS - 1
AMBIENT_DIMENSION = EXPONENTS_PER_AXIS**AXIS_COUNT

PARAMETER_POINT = (
    Fraction(1),
    Fraction(1, 2),
    Fraction(1),
    Fraction(2),
)
REAL_TWO_TIMES = (Fraction(1, 4), Fraction(1, 2))
REAL_GRAM_FLOOR = Fraction(2)

COMPLEX_FOUR_TIMES = (
    Fraction(0),
    Fraction(1, 10),
    Fraction(1, 5),
    Fraction(3, 10),
)
COMPLEX_DETERMINANT_MODULUS_SQUARED_LOWER = Fraction(500_000)
RESONANCE_CYCLE_MARGIN = Fraction(1, 100)
RESONANCE_NEAREST_ZERO_WINDOW = Fraction(1, 8)

VANDERMONDE_TAU = Fraction(1, 10)
VANDERMONDE_SAMPLE_COUNT = AMBIENT_DIMENSION
VANDERMONDE_CHORD_SQUARED_FLOOR = Fraction(1, 100_000)

ENTRY_RADIUS_CAP = Fraction(1, 10**50)
RELATIVE_RADIUS_CAP = Fraction(1, 10**40)
INTERVAL_DISPLAY_DIGITS = 90

_STATES = tuple(itertools.product(range(EXPONENTS_PER_AXIS), repeat=AXIS_COUNT))


def _fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def _parse_fraction_limited(text: str) -> Fraction:
    if not isinstance(text, str) or len(text) > 512 or "/" not in text:
        raise ValueError("fraction is not a bounded canonical string")
    numerator_text, denominator_text = text.split("/", 1)
    try:
        value = Fraction(int(numerator_text), int(denominator_text))
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError("fraction string is malformed") from exc
    if (
        value.numerator.bit_length() > MAX_INTEGER_BITS
        or value.denominator.bit_length() > MAX_INTEGER_BITS
    ):
        raise ValueError("fraction exceeds the formal integer limit")
    if _fraction_text(value) != text:
        raise ValueError("fraction string is not reduced and canonical")
    return value


def _arb_rational(value: Fraction | int) -> arb:
    value = Fraction(value)
    return arb(fmpq(value.numerator, value.denominator))


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _interval_text(value: arb, digits: int = INTERVAL_DISPLAY_DIGITS) -> str:
    return value.str(digits, radius=True, more=True)


def _exact_dyadic_fraction(value: arb) -> Fraction:
    if not value.is_exact():
        raise ValueError("expected an exact Arb endpoint")
    mantissa, exponent = map(int, value.man_exp())
    if exponent >= 0:
        return Fraction(mantissa * 2**exponent, 1)
    return Fraction(mantissa, 2 ** (-exponent))


def _principal_block(matrix: arb_mat, dimension: int) -> arb_mat:
    return arb_mat(
        [
            [matrix[row, column] for column in range(dimension)]
            for row in range(dimension)
        ]
    )


def _radius_audit(values: Iterable[arb], cap: Fraction = ENTRY_RADIUS_CAP) -> dict[str, object]:
    cap_ball = _arb_rational(cap)
    count = 0
    passed = True
    for value in values:
        count += 1
        passed = passed and bool(value.rad() < cap_ball)
    return {
        "quantity_count": count,
        "radius_cap_exact": _fraction_text(cap),
        "every_radius_strictly_below_cap": passed,
    }


def _q4(value: acb) -> acb:
    return acb(1) + value + value * value + value * value * value


def _q4_prime(value: acb) -> acb:
    return acb(1) + 2 * value + 3 * value * value


def complex_jacobian(
    times: Sequence[Fraction],
    point: Sequence[Fraction] = PARAMETER_POINT,
) -> list[list[acb]]:
    """Return d(F(t_l))/d(C,u_2,u_3,u_5) in exact Arb enclosures."""

    if len(point) != AXIS_COUNT + 1 or any(not isinstance(value, Fraction) for value in point):
        raise ValueError("the parameter point must have four exact rational coordinates")
    if any(value <= 0 for value in point):
        raise ValueError("the parameter point must be strictly positive")
    if not times or any(not isinstance(value, Fraction) for value in times):
        raise ValueError("times must be a nonempty exact rational sequence")

    scale = _arb_rational(point[0])
    parameters = tuple(_arb_rational(value) for value in point[1:])
    logarithms = tuple(arb(prime).log() for prime in PRIMES)
    rows: list[list[acb]] = []
    for exact_time in times:
        time = _arb_rational(exact_time)
        nodes = tuple(acb(0, -time * logarithm).exp() for logarithm in logarithms)
        arguments = tuple(nodes[axis] * parameters[axis] for axis in range(AXIS_COUNT))
        factors = tuple(_q4(argument) for argument in arguments)
        factor_product = factors[0] * factors[1] * factors[2]
        derivatives = [factor_product]
        for axis in range(AXIS_COUNT):
            other_product = acb(1)
            for other in range(AXIS_COUNT):
                if other != axis:
                    other_product *= factors[other]
            derivatives.append(
                scale
                * nodes[axis]
                * _q4_prime(arguments[axis])
                * other_product
            )
        rows.append(derivatives)
    return rows


def _realified_rows(rows: Sequence[Sequence[acb]]) -> list[list[arb]]:
    if not rows or any(len(row) != AXIS_COUNT + 1 for row in rows):
        raise ValueError("complex Jacobian rows have the wrong dimension")
    result: list[list[arb]] = []
    for row in rows:
        result.append([value.real for value in row])
        result.append([value.imag for value in row])
    return result


def _certify_real_gram_floor(
    gram: arb_mat,
    floor: Fraction,
) -> dict[str, object]:
    """Certify ``gram - floor I`` positive definite using Sylvester."""

    if gram.nrows() != gram.ncols() or gram.nrows() < 1:
        raise ValueError("Gram matrix must be nonempty and square")
    dimension = gram.nrows()
    identity = arb_mat(
        [
            [1 if row == column else 0 for column in range(dimension)]
            for row in range(dimension)
        ]
    )
    shifted = gram - identity * _arb_rational(floor)
    determinants = [
        _principal_block(shifted, size).det()
        for size in range(1, dimension + 1)
    ]
    signs = [1 if bool(value > 0) else -1 if bool(value < 0) else 0 for value in determinants]
    relative_passes = [
        bool(
            value > 0
            and value.rad() / value.lower() < _arb_rational(RELATIVE_RADIUS_CAP)
        )
        for value in determinants
    ]
    intervals = [_interval_text(value) for value in determinants]
    radius_audit = _radius_audit(
        (
            shifted[row, column]
            for row in range(dimension)
            for column in range(dimension)
        )
    )
    passed = bool(
        all(sign == 1 for sign in signs)
        and all(relative_passes)
        and radius_audit["every_radius_strictly_below_cap"]
    )
    return {
        "method": "direct Arb Sylvester test on J_R^T J_R - L I",
        "dimension": dimension,
        "floor_exact": _fraction_text(floor),
        "leading_principal_minor_signs": signs,
        "leading_principal_minor_intervals": intervals,
        "leading_principal_minor_intervals_sha256": _sha256(intervals),
        "final_minor_lower_endpoint_exact": _fraction_text(
            _exact_dyadic_fraction(determinants[-1].lower())
        ),
        "shift_matrix_radius_audit": radius_audit,
        "relative_radius_cap_exact": _fraction_text(RELATIVE_RADIUS_CAP),
        "every_relative_radius_strictly_below_cap": all(relative_passes),
        "every_leading_principal_minor_certainly_positive": all(
            sign == 1 for sign in signs
        ),
        "passed": passed,
    }


def _build_real_two_reading_section() -> dict[str, object]:
    rows = complex_jacobian(REAL_TWO_TIMES)
    real_rows = _realified_rows(rows)
    if len(real_rows) != 4 or any(len(row) != 4 for row in real_rows):
        raise AssertionError("two complex readings did not produce a 4 by 4 real Jacobian")
    jacobian = arb_mat(real_rows)
    gram = jacobian.transpose() * jacobian
    floor_certificate = _certify_real_gram_floor(gram, REAL_GRAM_FLOOR)
    determinant = jacobian.det()
    determinant_nonzero = bool(determinant < 0 or determinant > 0)
    determinant_relative_radius = determinant.rad() / abs(determinant)
    radius_audit = _radius_audit(value for row in real_rows for value in row)
    passed = bool(
        floor_certificate["passed"]
        and determinant_nonzero
        and determinant_relative_radius < _arb_rational(RELATIVE_RADIUS_CAP)
        and radius_audit["every_radius_strictly_below_cap"]
    )
    return {
        "schedule_exact": [_fraction_text(value) for value in REAL_TWO_TIMES],
        "all_times_nonzero": all(value != 0 for value in REAL_TWO_TIMES),
        "positive_parameter_point_exact": [
            _fraction_text(value) for value in PARAMETER_POINT
        ],
        "parameter_order": ["C", "u_2", "u_3", "u_5"],
        "observation_realification_order": [
            "Re F(1/4)",
            "Im F(1/4)",
            "Re F(1/2)",
            "Im F(1/2)",
        ],
        "jacobian_shape": [4, 4],
        "jacobian_determinant_interval": _interval_text(determinant),
        "jacobian_determinant_certainly_nonzero": determinant_nonzero,
        "jacobian_entry_radius_audit": radius_audit,
        "gram_floor_certificate": floor_certificate,
        "consequence": (
            "the two-reading map has full four-real-dimensional differential "
            "at the declared positive point"
        ),
        "passed": passed,
    }


def _root_quotient_indices() -> tuple[int, ...]:
    roots = tuple(range(1, EXPONENTS_PER_AXIS))
    return tuple(sorted({(left - right) % EXPONENTS_PER_AXIS for left in roots for right in roots}))


def _certify_four_time_resonance_margin() -> dict[str, object]:
    quotient_indices = _root_quotient_indices()
    if quotient_indices != tuple(range(EXPONENTS_PER_AXIS)):
        raise AssertionError("the Q_4 root-quotient set is not all fourth roots")
    records: list[dict[str, object]] = []
    lower_endpoints: list[tuple[Fraction, int]] = []
    all_above = True
    all_inside = True
    all_small_radius = True
    for prime in PRIMES:
        logarithm = arb(prime).log()
        for left, right in itertools.combinations(range(len(COMPLEX_FOUR_TIMES)), 2):
            difference = COMPLEX_FOUR_TIMES[right] - COMPLEX_FOUR_TIMES[left]
            cycles = logarithm * _arb_rational(difference) / (2 * arb.pi())
            above = bool(cycles > _arb_rational(RESONANCE_CYCLE_MARGIN))
            inside = bool(cycles < _arb_rational(RESONANCE_NEAREST_ZERO_WINDOW))
            small_radius = bool(cycles.rad() < _arb_rational(ENTRY_RADIUS_CAP))
            all_above &= above
            all_inside &= inside
            all_small_radius &= small_radius
            record_index = len(records)
            lower_endpoints.append((_exact_dyadic_fraction(cycles.lower()), record_index))
            records.append(
                {
                    "prime": prime,
                    "time_indices": [left, right],
                    "time_difference_exact": _fraction_text(difference),
                    "positive_cycle_distance_interval": _interval_text(cycles),
                    "strictly_above_margin": above,
                    "strictly_inside_nearest_zero_window": inside,
                }
            )
    minimum_lower, minimum_index = min(lower_endpoints)
    passed = bool(all_above and all_inside and all_small_radius)
    return {
        "q4_nontrivial_root_indices_mod_4": [1, 2, 3],
        "root_quotient_indices_mod_4": list(quotient_indices),
        "root_quotient_set_is_all_fourth_roots_exact": True,
        "resonance_rule": "log(p_j)*(t_b-t_a)/(2*pi) belongs to (1/4) Z",
        "pair_axis_record_count": len(records),
        "cycle_margin_exact": _fraction_text(RESONANCE_CYCLE_MARGIN),
        "nearest_zero_window_upper_exact": _fraction_text(
            RESONANCE_NEAREST_ZERO_WINDOW
        ),
        "minimum_cycle_distance_lower_endpoint_exact": _fraction_text(minimum_lower),
        "minimum_record_index": minimum_index,
        "records": records,
        "every_pair_axis_distance_strictly_above_margin": all_above,
        "every_distance_strictly_below_one_eighth_cycle": all_inside,
        "every_interval_radius_strictly_below_cap": all_small_radius,
        "basepoint_free_finite_input_verified": passed,
        "passed": passed,
    }


def _build_complex_four_reading_section() -> dict[str, object]:
    rows = complex_jacobian(COMPLEX_FOUR_TIMES)
    if len(rows) != 4 or any(len(row) != 4 for row in rows):
        raise AssertionError("four complex readings did not produce a 4 by 4 Jacobian")
    determinant = acb_mat(rows).det()
    modulus_squared = determinant.real * determinant.real + determinant.imag * determinant.imag
    determinant_passed = bool(
        modulus_squared
        > _arb_rational(COMPLEX_DETERMINANT_MODULUS_SQUARED_LOWER)
    )
    radius_audit = _radius_audit(
        component
        for row in rows
        for value in row
        for component in (value.real, value.imag)
    )
    resonance = _certify_four_time_resonance_margin()

    permutation_count = math.factorial(AXIS_COUNT)
    degree_power = POLYNOMIAL_DEGREE**AXIS_COUNT
    degree = permutation_count * degree_power
    if (permutation_count, degree_power, degree) != (6, 27, 162):
        raise AssertionError("the frozen Chow-ring degree combinatorics changed")
    passed = bool(
        determinant_passed
        and radius_audit["every_radius_strictly_below_cap"]
        and resonance["passed"]
    )
    return {
        "schedule_exact": [_fraction_text(value) for value in COMPLEX_FOUR_TIMES],
        "positive_parameter_point_exact": [
            _fraction_text(value) for value in PARAMETER_POINT
        ],
        "complex_jacobian_shape": [4, 4],
        "jacobian_determinant_real_interval": _interval_text(determinant.real),
        "jacobian_determinant_imaginary_interval": _interval_text(determinant.imag),
        "jacobian_determinant_modulus_squared_interval": _interval_text(modulus_squared),
        "determinant_modulus_squared_lower_exact": _fraction_text(
            COMPLEX_DETERMINANT_MODULUS_SQUARED_LOWER
        ),
        "determinant_modulus_squared_certainly_above_lower": determinant_passed,
        "jacobian_component_radius_audit": radius_audit,
        "basepoint_free_resonance_certificate": resonance,
        "degree_combinatorics": {
            "axis_count": AXIS_COUNT,
            "q4_degree": POLYNOMIAL_DEGREE,
            "surviving_top_intersection_monomial": "H_1 H_2 H_3",
            "permutation_coefficient": permutation_count,
            "degree_power": degree_power,
            "intersection_number_combinatorics": degree,
            "identity": "3! * 3^3 = 162",
        },
        "consequence": (
            "the frozen finite inputs used by the manuscript's four-section "
            "local-rank, basepoint-free, and degree arguments all pass"
        ),
        "passed": passed,
    }


def _prime_box_node_integer(state: Sequence[int]) -> int:
    if len(state) != AXIS_COUNT:
        raise ValueError("prime-box state has the wrong dimension")
    return math.prod(PRIMES[axis] ** state[axis] for axis in range(AXIS_COUNT))


def _build_vandermonde_section() -> dict[str, object]:
    exact_nodes = tuple(_prime_box_node_integer(state) for state in _STATES)
    exact_distinct = len(set(exact_nodes)) == AMBIENT_DIMENSION
    if not exact_distinct:
        raise AssertionError("unique factorization failed on the frozen prime box")
    tau = _arb_rational(VANDERMONDE_TAU)
    harmonic_nodes = tuple(
        acb(0, -tau * arb(node).log()).exp() for node in exact_nodes
    )
    pair_count = 0
    all_separated = True
    all_small_radius = True
    minimum_ratio: Fraction | None = None
    minimum_ratio_pairs: list[tuple[int, int]] = []
    for right in range(AMBIENT_DIMENSION):
        for left in range(right):
            difference = harmonic_nodes[right] - harmonic_nodes[left]
            squared_chord = (
                difference.real * difference.real
                + difference.imag * difference.imag
            )
            pair_count += 1
            all_separated &= bool(
                squared_chord > _arb_rational(VANDERMONDE_CHORD_SQUARED_FLOOR)
            )
            all_small_radius &= bool(
                squared_chord.rad() < _arb_rational(ENTRY_RADIUS_CAP)
            )
            exact_ratio = Fraction(
                max(exact_nodes[left], exact_nodes[right]),
                min(exact_nodes[left], exact_nodes[right]),
            )
            if minimum_ratio is None or exact_ratio < minimum_ratio:
                minimum_ratio = exact_ratio
                minimum_ratio_pairs = [(left, right)]
            elif exact_ratio == minimum_ratio:
                minimum_ratio_pairs.append((left, right))
    if minimum_ratio is None or not minimum_ratio_pairs:
        raise AssertionError("no Vandermonde node pairs were checked")
    # Every phase separation lies below pi, where 4 sin^2(theta/2) is
    # strictly increasing.  The exact closest positive rational ratio
    # therefore identifies the true chord minimum.  Resolve its exact ties
    # lexicographically, never by implementation-dependent Arb endpoints.
    phase_spread = tau * arb(max(exact_nodes)).log()
    phase_spread_below_pi = bool(phase_spread < arb.pi())
    left, right = min(minimum_ratio_pairs)
    minimum_difference = harmonic_nodes[right] - harmonic_nodes[left]
    minimum_interval = (
        minimum_difference.real * minimum_difference.real
        + minimum_difference.imag * minimum_difference.imag
    )
    minimum_lower = _exact_dyadic_fraction(minimum_interval.lower())
    expected_pair_count = AMBIENT_DIMENSION * (AMBIENT_DIMENSION - 1) // 2
    if pair_count != expected_pair_count:
        raise AssertionError("the Vandermonde pair count is inconsistent")
    times = tuple(VANDERMONDE_TAU * sample for sample in range(VANDERMONDE_SAMPLE_COUNT))
    passed = bool(
        exact_distinct
        and all_separated
        and all_small_radius
        and phase_spread_below_pi
    )
    return {
        "tau_exact": _fraction_text(VANDERMONDE_TAU),
        "schedule_rule": "t_m=m/10 for 0<=m<64",
        "schedule_exact": [_fraction_text(value) for value in times],
        "sample_count": VANDERMONDE_SAMPLE_COUNT,
        "state_order": "lexicographic product(range(4), repeat=3)",
        "node_records": [
            {"state": list(state), "integer_base": node}
            for state, node in zip(_STATES, exact_nodes)
        ],
        "integer_bases_pairwise_distinct_exact": exact_distinct,
        "pair_count": pair_count,
        "squared_chord_floor_exact": _fraction_text(
            VANDERMONDE_CHORD_SQUARED_FLOOR
        ),
        "minimum_squared_chord_lower_endpoint_exact": _fraction_text(minimum_lower),
        "minimum_squared_chord_interval": _interval_text(minimum_interval),
        "minimum_ratio_exact": _fraction_text(minimum_ratio),
        "minimum_ratio_tie_count": len(minimum_ratio_pairs),
        "minimum_ratio_tie_pairs": [list(pair) for pair in minimum_ratio_pairs],
        "minimum_pair_selection_rule": "exact ratio, then lexicographic indices",
        "minimum_pair_indices": [left, right],
        "minimum_pair_integer_bases": [exact_nodes[left], exact_nodes[right]],
        "phase_spread_interval": _interval_text(phase_spread),
        "phase_spread_certainly_below_pi": phase_spread_below_pi,
        "every_squared_chord_certainly_above_floor": all_separated,
        "every_squared_chord_radius_strictly_below_cap": all_small_radius,
        "vandermonde_nodes_pairwise_distinct_certified": passed,
        "consequence": (
            "the standard 64 by 64 power Vandermonde matrix has distinct nodes"
        ),
        "passed": passed,
    }


def build_payload(precision_bits: int = FORMAL_PRECISION_BITS) -> dict[str, object]:
    if type(precision_bits) is not int:
        raise ValueError("precision must be a canonical integer")
    if not MIN_PRECISION_BITS <= precision_bits <= MAX_PRECISION_BITS:
        raise ValueError("precision is outside the formal resource limits")
    with ctx.workprec(precision_bits):
        real_section = _build_real_two_reading_section()
        complex_section = _build_complex_four_reading_section()
        vandermonde_section = _build_vandermonde_section()
    overall = bool(
        real_section["passed"]
        and complex_section["passed"]
        and vandermonde_section["passed"]
    )
    return {
        "parameters": {
            "primes": list(PRIMES),
            "axis_count": AXIS_COUNT,
            "exponents_per_axis": EXPONENTS_PER_AXIS,
            "q4_degree": POLYNOMIAL_DEGREE,
            "ambient_dimension": AMBIENT_DIMENSION,
            "parameter_point_exact": [
                _fraction_text(value) for value in PARAMETER_POINT
            ],
            "parameter_order": ["C", "u_2", "u_3", "u_5"],
        },
        "two_nonzero_time_real_jacobian": real_section,
        "four_time_complex_sections": complex_section,
        "full_vandermonde_upper_schedule": vandermonde_section,
        "implementation": {
            "arb_precision_bits": precision_bits,
            "python_flint_version": flint.__version__,
            "flint_version": flint.__FLINT_VERSION__,
            "serialized_interval_digits": INTERVAL_DISPLAY_DIGITS,
            "all_transcendentals_enclosed_by_arb": True,
            "binary64_used_for_proof_decisions": False,
            "strict_interval_comparisons_only": True,
            "serialized_resource_cap_bytes": MAX_ARTIFACT_BYTES,
        },
        "formal_scope": {
            "claim": (
                "frozen Jacobian ranks, fourth-root resonance separation, "
                "degree arithmetic, and prime-box node separation"
            ),
            "topological_finiteness_proved_by_certificate": False,
            "intersection_theory_proved_by_certificate": False,
            "vandermonde_determinant_formula_proved_by_certificate": False,
            "global_injectivity_claimed": False,
            "schedule_optimality_claimed": False,
            "reciprocal_collision_formally_certified": False,
            "arb_scope": (
                "computer-assisted interval proof conditional on the Arb/FLINT "
                "implementation; not a formal-proof-assistant derivation"
            ),
        },
        "overall_passed": overall,
    }


def build_artifact(precision_bits: int = FORMAL_PRECISION_BITS) -> dict[str, object]:
    payload = build_payload(precision_bits)
    return {
        "schema": SCHEMA,
        "payload": payload,
        "payload_sha256": _sha256(payload),
    }


def _validate_resource_tree(value: object, depth: int = 0) -> None:
    if depth > MAX_JSON_DEPTH:
        raise ValueError("artifact exceeds the maximum JSON depth resource cap")
    if isinstance(value, str):
        if len(value) > MAX_TEXT_FIELD_LENGTH:
            raise ValueError("artifact text exceeds the resource cap")
        return
    if isinstance(value, bool) or value is None:
        return
    if type(value) is int:
        if value.bit_length() > MAX_INTEGER_BITS:
            raise ValueError("artifact integer exceeds the resource cap")
        return
    if isinstance(value, float):
        raise ValueError("artifact contains a forbidden floating-point value")
    if isinstance(value, list):
        if len(value) > MAX_CONTAINER_ITEMS:
            raise ValueError("artifact list exceeds the resource cap")
        for item in value:
            _validate_resource_tree(item, depth + 1)
        return
    if isinstance(value, dict):
        if len(value) > MAX_CONTAINER_ITEMS:
            raise ValueError("artifact object exceeds the resource cap")
        for key, item in value.items():
            if not isinstance(key, str) or len(key) > 128:
                raise ValueError("artifact key violates canonical resource limits")
            _validate_resource_tree(item, depth + 1)
        return
    raise ValueError("artifact contains an unsupported JSON value type")


def _validate_fraction_list(
    values: object,
    expected: Sequence[Fraction],
    label: str,
) -> None:
    if not isinstance(values, list) or len(values) != len(expected):
        raise ValueError(f"{label} violates the exact dimension cap")
    parsed = tuple(_parse_fraction_limited(value) for value in values)
    if parsed != tuple(expected):
        raise ValueError(f"artifact uses a noncanonical {label}")


def _validate_stored_shape(artifact: dict[str, object]) -> None:
    if not isinstance(artifact, dict):
        raise ValueError("artifact must be a JSON object")
    _validate_resource_tree(artifact)
    if set(artifact) != {"schema", "payload", "payload_sha256"}:
        raise ValueError("artifact has unexpected top-level fields")
    if artifact["schema"] != SCHEMA:
        raise ValueError("unsupported reading-complexity schema")
    digest = artifact["payload_sha256"]
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(character not in "0123456789abcdef" for character in digest)
    ):
        raise ValueError("payload digest is not canonical lowercase SHA-256")
    payload = artifact["payload"]
    if not isinstance(payload, dict) or set(payload) != {
        "parameters",
        "two_nonzero_time_real_jacobian",
        "four_time_complex_sections",
        "full_vandermonde_upper_schedule",
        "implementation",
        "formal_scope",
        "overall_passed",
    }:
        raise ValueError("payload has unexpected fields")
    parameters = payload["parameters"]
    if not isinstance(parameters, dict):
        raise ValueError("parameters must be an object")
    primes = parameters.get("primes")
    if primes != list(PRIMES) or not isinstance(primes, list) or not all(
        type(value) is int for value in primes
    ):
        raise ValueError("artifact uses noncanonical prime axes")
    for key, expected in (
        ("axis_count", AXIS_COUNT),
        ("exponents_per_axis", EXPONENTS_PER_AXIS),
        ("q4_degree", POLYNOMIAL_DEGREE),
        ("ambient_dimension", AMBIENT_DIMENSION),
    ):
        if type(parameters.get(key)) is not int or parameters[key] != expected:
            raise ValueError(f"{key} is not a canonical integer")
    _validate_fraction_list(
        parameters.get("parameter_point_exact"), PARAMETER_POINT, "parameter point"
    )

    real_section = payload["two_nonzero_time_real_jacobian"]
    complex_section = payload["four_time_complex_sections"]
    vandermonde = payload["full_vandermonde_upper_schedule"]
    if not isinstance(real_section, dict) or not isinstance(complex_section, dict) or not isinstance(vandermonde, dict):
        raise ValueError("a certificate section is malformed")
    _validate_fraction_list(real_section.get("schedule_exact"), REAL_TWO_TIMES, "real schedule")
    _validate_fraction_list(
        complex_section.get("schedule_exact"), COMPLEX_FOUR_TIMES, "complex schedule"
    )
    for section, dimension in ((real_section, 4),):
        certificate = section.get("gram_floor_certificate")
        if not isinstance(certificate, dict):
            raise ValueError("Gram floor certificate is malformed")
        signs = certificate.get("leading_principal_minor_signs")
        intervals = certificate.get("leading_principal_minor_intervals")
        if not isinstance(signs, list) or len(signs) != dimension or not all(type(value) is int for value in signs):
            raise ValueError("principal-minor sign list violates the resource cap")
        if not isinstance(intervals, list) or len(intervals) != dimension or any(not isinstance(value, str) for value in intervals):
            raise ValueError("principal-minor interval list violates the resource cap")

    resonance = complex_section.get("basepoint_free_resonance_certificate")
    if not isinstance(resonance, dict):
        raise ValueError("resonance certificate is malformed")
    records = resonance.get("records")
    if not isinstance(records, list) or len(records) != 18:
        raise ValueError("resonance record list violates the resource cap")
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("resonance record must be an object")
        indices = record.get("time_indices")
        if (
            not isinstance(indices, list)
            or len(indices) != 2
            or not all(type(value) is int for value in indices)
            or not 0 <= indices[0] < indices[1] < 4
            or type(record.get("prime")) is not int
            or record["prime"] not in PRIMES
            or not isinstance(record.get("positive_cycle_distance_interval"), str)
        ):
            raise ValueError("resonance record violates exact type caps")

    expected_times = tuple(
        VANDERMONDE_TAU * sample for sample in range(VANDERMONDE_SAMPLE_COUNT)
    )
    _validate_fraction_list(vandermonde.get("schedule_exact"), expected_times, "Vandermonde schedule")
    nodes = vandermonde.get("node_records")
    if not isinstance(nodes, list) or len(nodes) != AMBIENT_DIMENSION:
        raise ValueError("Vandermonde node list violates the resource cap")
    stored_bases: list[int] = []
    for expected_state, record in zip(_STATES, nodes):
        if not isinstance(record, dict) or set(record) != {"state", "integer_base"}:
            raise ValueError("Vandermonde node record has unexpected fields")
        state = record["state"]
        base = record["integer_base"]
        if (
            not isinstance(state, list)
            or len(state) != AXIS_COUNT
            or not all(type(value) is int and 0 <= value < EXPONENTS_PER_AXIS for value in state)
            or tuple(state) != expected_state
            or type(base) is not int
            or base != _prime_box_node_integer(expected_state)
        ):
            raise ValueError("artifact uses a noncanonical Vandermonde node")
        stored_bases.append(base)
    if len(set(stored_bases)) != AMBIENT_DIMENSION:
        raise ValueError("artifact contains duplicate Vandermonde nodes")

    implementation = payload["implementation"]
    if not isinstance(implementation, dict):
        raise ValueError("implementation field must be an object")
    precision = implementation.get("arb_precision_bits")
    if type(precision) is not int or not MIN_PRECISION_BITS <= precision <= MAX_PRECISION_BITS:
        raise ValueError("stored precision violates the formal resource cap")
    if precision != FORMAL_PRECISION_BITS:
        raise ValueError("stored artifact does not use the pinned formal precision")
    if len(_canonical_json(artifact)) > MAX_ARTIFACT_BYTES:
        raise ValueError("artifact exceeds the serialized resource cap")


def verify_artifact(artifact: dict[str, object]) -> dict[str, object]:
    """Recompute all interval claims and reject stale or semantic tampering."""

    _validate_stored_shape(artifact)
    payload = artifact["payload"]
    if artifact["payload_sha256"] != _sha256(payload):
        raise ValueError("payload digest mismatch")
    expected = build_artifact(FORMAL_PRECISION_BITS)
    if _canonical_json(artifact) != _canonical_json(expected):
        raise ValueError("artifact does not equal independent Arb reconstruction")
    return {
        "verified": True,
        "schema": SCHEMA,
        "payload_sha256": artifact["payload_sha256"],
        "real_gram_floor_exact": _fraction_text(REAL_GRAM_FLOOR),
        "complex_determinant_modulus_squared_lower_exact": _fraction_text(
            COMPLEX_DETERMINANT_MODULUS_SQUARED_LOWER
        ),
        "intersection_number_combinatorics": 162,
        "vandermonde_node_count": AMBIENT_DIMENSION,
        "overall_passed": expected["payload"]["overall_passed"],
    }


def _strict_object_from_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _reject_nonfinite_json_constant(value: str) -> object:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def _parse_canonical_json_integer(value: str) -> int:
    if value == "-0":
        raise ValueError("negative-zero JSON integer is noncanonical")
    if len(value.lstrip("-")) > 320:
        raise ValueError("JSON integer literal exceeds the formal size limit")
    return int(value)


def _reject_json_float(value: str) -> object:
    raise ValueError(f"JSON floating-point number is forbidden: {value}")


def _read_artifact(path: Path) -> dict[str, object]:
    with path.open("rb") as artifact_file:
        raw = artifact_file.read(MAX_ARTIFACT_BYTES + 1)
    if len(raw) > MAX_ARTIFACT_BYTES:
        raise ValueError("artifact file exceeds the serialized resource cap")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("artifact is not canonical UTF-8 JSON") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_strict_object_from_pairs,
            parse_int=_parse_canonical_json_integer,
            parse_float=_reject_json_float,
            parse_constant=_reject_nonfinite_json_constant,
        )
    except RecursionError as exc:
        raise ValueError("artifact exceeds the JSON nesting limit") from exc
    if not isinstance(value, dict):
        raise ValueError("artifact JSON root must be an object")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--write", type=Path)
    action.add_argument("--verify", type=Path)
    parser.add_argument("--precision-bits", type=int, default=FORMAL_PRECISION_BITS)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()

    if args.verify is not None:
        result = verify_artifact(_read_artifact(args.verify))
    else:
        result = build_artifact(args.precision_bits)
    rendered = json.dumps(
        result, indent=None if args.compact else 2, sort_keys=True
    ) + "\n"
    if args.write is not None:
        args.write.write_bytes(rendered.encode("utf-8"))
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
