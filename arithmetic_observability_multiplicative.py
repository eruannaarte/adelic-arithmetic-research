#!/usr/bin/env python3
"""Exact certificate for multiplicative arithmetic observability.

The fixed canonical model has three labelled prime axes, four exponent states
per axis, and ambient dimension 64.  Every proof decision is made with
integers or :class:`fractions.Fraction`; binary floating point and external
packages are not used.

The certificate checks four logically distinct facts.

* Two complementary marginals reconstruct every factor of a normalized
  product tensor, while one marginal has an explicit probability collision.
* A signed free-scale geometric collision caused by ``Q_4(-1)=0`` lies in the
  full three-factor mean-zero interaction space.
* At the uniform product, the calibrated marginal pullback has the exact
  generalized spectra claimed for all-three, two-axis, and one-axis designs.
* One binary rational example attains the sharp two-margin total-variation
  modulus and supplies the common-midpoint minimax lower-bound witness.

The JSON loader rejects duplicate keys, floating-point literals, non-finite
constants, and negative zero before semantic verification.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Iterable, Sequence


SCHEMA = "arithmetic-observability-normalized-product-v1"
PRIMES = (2, 3, 5)
AXIS_COUNT = 3
EXPONENTS_PER_AXIS = 4
AMBIENT_DIMENSION = EXPONENTS_PER_AXIS**AXIS_COUNT
SELECTED_AXES = (0, 1)

MAX_ARTIFACT_BYTES = 100_000
MAX_CONTAINER_ITEMS = 256
MAX_JSON_DEPTH = 16
MAX_TEXT_FIELD_LENGTH = 512
MAX_INTEGER_BITS = 256
MAX_FORMAL_DIMENSION = 256

UNIFORM_FACTOR = (Fraction(1, 4),) * 4
CANONICAL_FACTORS = (
    (Fraction(1, 10), Fraction(1, 5), Fraction(3, 10), Fraction(2, 5)),
    (Fraction(2, 5), Fraction(3, 10), Fraction(1, 5), Fraction(1, 10)),
    (Fraction(1, 8), Fraction(1, 8), Fraction(1, 4), Fraction(1, 2)),
)
COLLISION_FACTOR_PLUS = (
    Fraction(3, 8),
    Fraction(1, 8),
    Fraction(1, 4),
    Fraction(1, 4),
)
COLLISION_FACTOR_MINUS = (
    Fraction(1, 8),
    Fraction(3, 8),
    Fraction(1, 4),
    Fraction(1, 4),
)

FREE_SCALE_LEFT = (15, (0, -1, -1))
FREE_SCALE_RIGHT = (1, (2, -1, -1))

TV_EPSILON_A = Fraction(1, 8)
TV_EPSILON_B = Fraction(1, 6)

CONTRAST_COLUMNS = (
    (1, 0, 0, -1),
    (0, 1, 0, -1),
    (0, 0, 1, -1),
)
CONTRAST_METRIC = (
    (2, 1, 1),
    (1, 2, 1),
    (1, 1, 2),
)


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _parse_fraction_limited(text: str) -> Fraction:
    if not isinstance(text, str) or len(text) > 64 or "/" not in text:
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


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _fraction_vector_payload(values: Sequence[Fraction]) -> list[str]:
    return [_fraction_text(value) for value in values]


def _fraction_matrix_payload(
    matrix: Sequence[Sequence[Fraction]],
) -> list[list[str]]:
    return [_fraction_vector_payload(row) for row in matrix]


def exponent_states(r: int, s: int) -> tuple[tuple[int, ...], ...]:
    if type(r) is not int or type(s) is not int or r < 1 or s < 2:
        raise ValueError("state dimensions must be canonical positive integers")
    if s**r > MAX_FORMAL_DIMENSION:
        raise ValueError("declared tensor exceeds the formal dimension cap")
    return tuple(itertools.product(range(s), repeat=r))


def _validate_probability_factor(factor: Sequence[Fraction], s: int) -> None:
    if len(factor) != s or any(not isinstance(value, Fraction) for value in factor):
        raise ValueError("factor has the wrong exact type or dimension")
    if any(value < 0 for value in factor) or sum(factor, Fraction(0)) != 1:
        raise ValueError("factor is not an exact probability vector")


def tensor_product(factors: Sequence[Sequence[Fraction]]) -> list[Fraction]:
    """Return a lexicographically ordered exact tensor product."""

    if not factors:
        return [Fraction(1)]
    s = len(factors[0])
    if s < 1 or any(len(factor) != s for factor in factors):
        raise ValueError("tensor factors have inconsistent dimensions")
    return [
        math.prod(
            (Fraction(factors[axis][state]) for axis, state in enumerate(alpha)),
            start=Fraction(1),
        )
        for alpha in exponent_states(len(factors), s)
    ]


def complementary_marginal(
    tensor: Sequence[Fraction], r: int, s: int, axis: int
) -> list[Fraction]:
    """Sum one axis for a tensor with at least two axes."""

    if type(r) is not int or r < 2:
        raise ValueError("a complementary marginal requires at least two axes")
    states = exponent_states(r, s)
    if len(tensor) != len(states):
        raise ValueError("tensor has the wrong ambient dimension")
    if type(axis) is not int or not 0 <= axis < r:
        raise ValueError("marginal axis is out of range")
    reduced_states = exponent_states(r - 1, s)
    reduced_index = {state: index for index, state in enumerate(reduced_states)}
    result = [Fraction(0) for _ in reduced_states]
    for alpha, value in zip(states, tensor):
        beta = alpha[:axis] + alpha[axis + 1 :]
        result[reduced_index[beta]] += Fraction(value)
    return result


def factor_from_complementary_marginal(
    marginal: Sequence[Fraction],
    observed_axis: int,
    factor_axis: int,
    r: int,
    s: int,
) -> list[Fraction]:
    """Recover one retained factor by further marginalization."""

    if observed_axis == factor_axis:
        raise ValueError("the omitted factor is not present in this marginal")
    if not 0 <= observed_axis < r or not 0 <= factor_axis < r:
        raise ValueError("axis is out of range")
    reduced_states = exponent_states(r - 1, s)
    if len(marginal) != len(reduced_states):
        raise ValueError("complementary marginal has the wrong dimension")
    retained_axes = tuple(axis for axis in range(r) if axis != observed_axis)
    position = retained_axes.index(factor_axis)
    result = [Fraction(0) for _ in range(s)]
    for beta, value in zip(reduced_states, marginal):
        result[beta[position]] += Fraction(value)
    return result


def reconstruct_product_from_two_marginals(
    marginals: dict[int, Sequence[Fraction]], r: int, s: int
) -> tuple[list[list[Fraction]], list[Fraction]]:
    """Reconstruct factors, assuming the marginals come from a product source."""

    if len(marginals) != 2 or any(type(axis) is not int for axis in marginals):
        raise ValueError("exactly two labelled marginals are required")
    observed_axes = tuple(sorted(marginals))
    if observed_axes[0] == observed_axes[1] or not all(
        0 <= axis < r for axis in observed_axes
    ):
        raise ValueError("two distinct in-range axes are required")
    factors: list[list[Fraction]] = []
    for factor_axis in range(r):
        candidates = [
            factor_from_complementary_marginal(
                marginals[axis], axis, factor_axis, r, s
            )
            for axis in observed_axes
            if axis != factor_axis
        ]
        if not candidates:
            raise AssertionError("two distinct axes failed to cover one factor")
        if any(candidate != candidates[0] for candidate in candidates[1:]):
            raise ValueError("the supplied marginals have inconsistent factors")
        _validate_probability_factor(candidates[0], s)
        factors.append(candidates[0])
    return factors, tensor_product(factors)


def l1_distance(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    if len(left) != len(right):
        raise ValueError("distance vectors have different dimensions")
    return sum((abs(Fraction(a) - Fraction(b)) for a, b in zip(left, right)), Fraction(0))


def total_variation(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    return l1_distance(left, right) / 2


def geometric_factor(parameter: int, s: int = EXPONENTS_PER_AXIS) -> list[int]:
    if type(parameter) is not int:
        raise ValueError("geometric parameter must be an exact integer")
    return [parameter**power for power in range(s)]


def geometric_sum(parameter: int, s: int = EXPONENTS_PER_AXIS) -> int:
    return sum(geometric_factor(parameter, s))


def free_scale_geometric_tensor(
    scale: int, parameters: Sequence[int], s: int = EXPONENTS_PER_AXIS
) -> list[Fraction]:
    if type(scale) is not int or type(parameters) not in (tuple, list):
        raise ValueError("free-scale data must use canonical integer types")
    factors = [geometric_factor(parameter, s) for parameter in parameters]
    return [scale * value for value in tensor_product(factors)]


def _transpose(matrix: Sequence[Sequence[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix)]


def _dot(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    if len(left) != len(right):
        raise ValueError("dot-product vectors have different dimensions")
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def _gram_from_columns(columns: Sequence[Sequence[Fraction]]) -> list[list[Fraction]]:
    return [[_dot(left, right) for right in columns] for left in columns]


def _determinant(matrix: Sequence[Sequence[Fraction]]) -> Fraction:
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("determinant requires a square matrix")
    work = [[Fraction(value) for value in row] for row in matrix]
    determinant = Fraction(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant = -determinant
        pivot_value = work[column][column]
        determinant *= pivot_value
        for row in range(column + 1, size):
            if not work[row][column]:
                continue
            factor = work[row][column] / pivot_value
            for entry in range(column, size):
                work[row][entry] -= factor * work[column][entry]
    return determinant


def uniform_tangent_columns(r: int, s: int) -> list[list[Fraction]]:
    """Columns of d(Phi) at the uniform product in contrast coordinates."""

    states = exponent_states(r, s)
    contrasts: list[list[int]] = []
    for coordinate in range(s - 1):
        vector = [0 for _ in range(s)]
        vector[coordinate] = 1
        vector[-1] = -1
        contrasts.append(vector)
    columns: list[list[Fraction]] = []
    uniform_multiplier = Fraction(1, s ** (r - 1))
    for factor_axis in range(r):
        for contrast in contrasts:
            columns.append(
                [
                    uniform_multiplier * contrast[alpha[factor_axis]]
                    for alpha in states
                ]
            )
    return columns


def calibrated_projector_apply(
    vector: Sequence[Fraction], r: int, s: int, axis: int
) -> list[Fraction]:
    """Apply P_j=s^(-1) M_j^* M_j using exact marginal operations."""

    marginal = complementary_marginal(vector, r, s, axis)
    reduced_states = exponent_states(r - 1, s)
    reduced_index = {state: index for index, state in enumerate(reduced_states)}
    result: list[Fraction] = []
    for alpha in exponent_states(r, s):
        beta = alpha[:axis] + alpha[axis + 1 :]
        result.append(marginal[reduced_index[beta]] / s)
    return result


def tangent_source_metric(r: int, s: int) -> list[list[Fraction]]:
    return _gram_from_columns(uniform_tangent_columns(r, s))


def tangent_pullback_gram(
    weights: Sequence[Fraction], r: int, s: int
) -> list[list[Fraction]]:
    if len(weights) != r or any(not isinstance(weight, Fraction) for weight in weights):
        raise ValueError("one exact weight per axis is required")
    if any(weight < 0 for weight in weights) or sum(weights, Fraction(0)) != 1:
        raise ValueError("weights must be nonnegative and sum exactly to one")
    columns = uniform_tangent_columns(r, s)
    projected = [
        [calibrated_projector_apply(column, r, s, axis) for column in columns]
        for axis in range(r)
    ]
    dimension = len(columns)
    return [
        [
            sum(
                (
                    weights[axis] * _dot(columns[row], projected[axis][column])
                    for axis in range(r)
                ),
                Fraction(0),
            )
            for column in range(dimension)
        ]
        for row in range(dimension)
    ]


def _spectrum_payload(block_eigenvalues: Sequence[Fraction], multiplicity: int) -> list[dict[str, object]]:
    counts = Counter(block_eigenvalues)
    return [
        {
            "eigenvalue": _fraction_text(eigenvalue),
            "multiplicity": counts[eigenvalue] * multiplicity,
        }
        for eigenvalue in sorted(counts)
    ]


def certify_tangent_design(
    name: str, weights: Sequence[Fraction], r: int, s: int
) -> dict[str, object]:
    metric = tangent_source_metric(r, s)
    gram = tangent_pullback_gram(weights, r, s)
    q = s - 1
    block_values = tuple(1 - weight for weight in weights)
    expected = [
        [
            block_values[row // q] * metric[row][column]
            if row // q == column // q
            else Fraction(0)
            for column in range(r * q)
        ]
        for row in range(r * q)
    ]
    if gram != expected:
        raise AssertionError("tangent Gram does not have the predicted exact blocks")
    return {
        "name": name,
        "weights": _fraction_vector_payload(tuple(weights)),
        "factor_block_generalized_eigenvalues": _fraction_vector_payload(block_values),
        "generalized_spectrum": _spectrum_payload(block_values, q),
        "generalized_floor": _fraction_text(min(block_values)),
        "tangent_rank": sum(q for value in block_values if value != 0),
        "pullback_gram_sha256": _sha256(_fraction_matrix_payload(gram)),
        "exact_block_identity_verified": True,
    }


def _mean(left: Sequence[Fraction], right: Sequence[Fraction]) -> list[Fraction]:
    if len(left) != len(right):
        raise ValueError("mean vectors have different dimensions")
    return [(a + b) / 2 for a, b in zip(left, right)]


def _build_normalized_product_section() -> dict[str, object]:
    factors = [list(factor) for factor in CANONICAL_FACTORS]
    for factor in factors:
        _validate_probability_factor(factor, EXPONENTS_PER_AXIS)
    tensor = tensor_product(factors)
    marginals = [
        complementary_marginal(tensor, AXIS_COUNT, EXPONENTS_PER_AXIS, axis)
        for axis in range(AXIS_COUNT)
    ]
    expected_marginals = [
        tensor_product(factors[:axis] + factors[axis + 1 :])
        for axis in range(AXIS_COUNT)
    ]
    if marginals != expected_marginals:
        raise AssertionError("exact complementary marginal identity failed")
    reconstructed_factors, reconstructed_tensor = reconstruct_product_from_two_marginals(
        {axis: marginals[axis] for axis in SELECTED_AXES},
        AXIS_COUNT,
        EXPONENTS_PER_AXIS,
    )
    if reconstructed_factors != factors or reconstructed_tensor != tensor:
        raise AssertionError("two-axis exact product reconstruction failed")
    return {
        "canonical_factors": [_fraction_vector_payload(factor) for factor in factors],
        "product_tensor_sha256": _sha256(_fraction_vector_payload(tensor)),
        "complementary_marginal_sha256_by_axis": [
            _sha256(_fraction_vector_payload(marginal)) for marginal in marginals
        ],
        "marginal_identity_verified_all_axes": True,
        "selected_reconstruction_axes": list(SELECTED_AXES),
        "reconstructed_factors": [
            _fraction_vector_payload(factor) for factor in reconstructed_factors
        ],
        "reconstructed_tensor_sha256": _sha256(
            _fraction_vector_payload(reconstructed_tensor)
        ),
        "two_axis_reconstruction_exact": True,
        "normalized_product_dimension": AXIS_COUNT * (EXPONENTS_PER_AXIS - 1),
        "two_axis_ambient_common_kernel_dimension": (
            (EXPONENTS_PER_AXIS - 1) ** 2
            * EXPONENTS_PER_AXIS ** (AXIS_COUNT - 2)
        ),
    }


def _build_probability_collision_section() -> dict[str, object]:
    factors_plus = [list(COLLISION_FACTOR_PLUS), list(UNIFORM_FACTOR), list(UNIFORM_FACTOR)]
    factors_minus = [list(COLLISION_FACTOR_MINUS), list(UNIFORM_FACTOR), list(UNIFORM_FACTOR)]
    tensor_plus = tensor_product(factors_plus)
    tensor_minus = tensor_product(factors_minus)
    hidden_plus = complementary_marginal(
        tensor_plus, AXIS_COUNT, EXPONENTS_PER_AXIS, 0
    )
    hidden_minus = complementary_marginal(
        tensor_minus, AXIS_COUNT, EXPONENTS_PER_AXIS, 0
    )
    revealing_plus = complementary_marginal(
        tensor_plus, AXIS_COUNT, EXPONENTS_PER_AXIS, 1
    )
    revealing_minus = complementary_marginal(
        tensor_minus, AXIS_COUNT, EXPONENTS_PER_AXIS, 1
    )
    if tensor_plus == tensor_minus or hidden_plus != hidden_minus or revealing_plus == revealing_minus:
        raise AssertionError("declared probability collision is invalid")
    difference = [left - right for left, right in zip(tensor_plus, tensor_minus)]
    squared_l2 = _dot(difference, difference)
    tv = total_variation(tensor_plus, tensor_minus)
    if squared_l2 != Fraction(1, 128) or tv != Fraction(1, 4):
        raise AssertionError("declared collision diagnostics are inconsistent")
    return {
        "observed_axis": 0,
        "revealing_axis": 1,
        "hidden_factor_plus": _fraction_vector_payload(COLLISION_FACTOR_PLUS),
        "hidden_factor_minus": _fraction_vector_payload(COLLISION_FACTOR_MINUS),
        "shared_uniform_factors": 2,
        "tensor_plus_sha256": _sha256(_fraction_vector_payload(tensor_plus)),
        "tensor_minus_sha256": _sha256(_fraction_vector_payload(tensor_minus)),
        "common_observed_marginal_sha256": _sha256(
            _fraction_vector_payload(hidden_plus)
        ),
        "revealing_marginal_plus_sha256": _sha256(
            _fraction_vector_payload(revealing_plus)
        ),
        "revealing_marginal_minus_sha256": _sha256(
            _fraction_vector_payload(revealing_minus)
        ),
        "source_squared_l2_distance": _fraction_text(squared_l2),
        "source_total_variation": _fraction_text(tv),
        "one_axis_collision_exact": True,
        "hidden_factor_fibre_dimension": EXPONENTS_PER_AXIS - 1,
        "one_axis_ambient_kernel_dimension": (
            (EXPONENTS_PER_AXIS - 1)
            * EXPONENTS_PER_AXIS ** (AXIS_COUNT - 1)
        ),
    }


def _build_free_scale_section() -> dict[str, object]:
    left_scale, left_parameters = FREE_SCALE_LEFT
    right_scale, right_parameters = FREE_SCALE_RIGHT
    left = free_scale_geometric_tensor(left_scale, left_parameters)
    right = free_scale_geometric_tensor(right_scale, right_parameters)
    left_marginals = [
        complementary_marginal(left, AXIS_COUNT, EXPONENTS_PER_AXIS, axis)
        for axis in range(AXIS_COUNT)
    ]
    right_marginals = [
        complementary_marginal(right, AXIS_COUNT, EXPONENTS_PER_AXIS, axis)
        for axis in range(AXIS_COUNT)
    ]
    if left == right or left_marginals != right_marginals:
        raise AssertionError("declared free-scale exceptional collision is invalid")
    difference = [Fraction(a - b) for a, b in zip(left, right)]
    first_difference_factor = [14, -2, -4, -8]
    root_factor = geometric_factor(-1)
    factored_difference = tensor_product(
        [first_difference_factor, root_factor, root_factor]
    )
    if difference != factored_difference:
        raise AssertionError("free-scale collision difference factorization failed")
    factor_sums = [sum(first_difference_factor), sum(root_factor), sum(root_factor)]
    zero_marginals = [
        complementary_marginal(
            difference, AXIS_COUNT, EXPONENTS_PER_AXIS, axis
        )
        for axis in range(AXIS_COUNT)
    ]
    if factor_sums != [0, 0, 0] or any(any(marginal) for marginal in zero_marginals):
        raise AssertionError("free-scale difference is not in the top interaction")
    squared_l2 = _dot(difference, difference)
    if squared_l2 != 4480:
        raise AssertionError("free-scale collision norm is inconsistent")
    return {
        "left": {"scale": left_scale, "parameters": list(left_parameters)},
        "right": {"scale": right_scale, "parameters": list(right_parameters)},
        "geometric_sums_left": [
            geometric_sum(parameter) for parameter in left_parameters
        ],
        "geometric_sums_right": [
            geometric_sum(parameter) for parameter in right_parameters
        ],
        "scaled_geometric_sums_left": [
            left_scale * geometric_sum(parameter) for parameter in left_parameters
        ],
        "scaled_geometric_sums_right": [
            right_scale * geometric_sum(parameter) for parameter in right_parameters
        ],
        "tensor_left_sha256": _sha256([int(value) for value in left]),
        "tensor_right_sha256": _sha256([int(value) for value in right]),
        "common_marginal_sha256_by_axis": [
            _sha256([int(value) for value in marginal])
            for marginal in left_marginals
        ],
        "difference_factorization": [first_difference_factor, root_factor, root_factor],
        "difference_factor_sums": factor_sums,
        "difference_sha256": _sha256([int(value) for value in difference]),
        "difference_squared_l2": _fraction_text(squared_l2),
        "all_axis_collision_exact": True,
        "difference_in_full_mean_zero_interaction": True,
    }


def _build_tv_witness_section() -> dict[str, object]:
    point = [Fraction(1), Fraction(0), Fraction(0), Fraction(0)]
    # The a-factor moves mass 2*epsilon_b and the b-factor moves 2*epsilon_a.
    moved_a = [1 - 2 * TV_EPSILON_B, 2 * TV_EPSILON_B, Fraction(0), Fraction(0)]
    moved_b = [1 - 2 * TV_EPSILON_A, 2 * TV_EPSILON_A, Fraction(0), Fraction(0)]
    p_zero = tensor_product([point, point, point])
    p_moved = tensor_product([moved_a, moved_b, point])
    margin_zero_a = complementary_marginal(
        p_zero, AXIS_COUNT, EXPONENTS_PER_AXIS, 0
    )
    margin_moved_a = complementary_marginal(
        p_moved, AXIS_COUNT, EXPONENTS_PER_AXIS, 0
    )
    margin_zero_b = complementary_marginal(
        p_zero, AXIS_COUNT, EXPONENTS_PER_AXIS, 1
    )
    margin_moved_b = complementary_marginal(
        p_moved, AXIS_COUNT, EXPONENTS_PER_AXIS, 1
    )
    d_a = total_variation(margin_zero_a, margin_moved_a)
    d_b = total_variation(margin_zero_b, margin_moved_b)
    source_tv = total_variation(p_zero, p_moved)
    modulus = d_a + d_b - d_a * d_b
    if (
        d_a != 2 * TV_EPSILON_A
        or d_b != 2 * TV_EPSILON_B
        or source_tv != modulus
    ):
        raise AssertionError("sharp total-variation witness is inconsistent")
    midpoint_a = _mean(margin_zero_a, margin_moved_a)
    midpoint_b = _mean(margin_zero_b, margin_moved_b)
    midpoint_distances = (
        total_variation(midpoint_a, margin_zero_a),
        total_variation(midpoint_a, margin_moved_a),
        total_variation(midpoint_b, margin_zero_b),
        total_variation(midpoint_b, margin_moved_b),
    )
    if midpoint_distances != (
        TV_EPSILON_A,
        TV_EPSILON_A,
        TV_EPSILON_B,
        TV_EPSILON_B,
    ):
        raise AssertionError("common-midpoint observation radii are inconsistent")
    half_source = source_tv / 2
    minimax_formula = (
        TV_EPSILON_A
        + TV_EPSILON_B
        - 2 * TV_EPSILON_A * TV_EPSILON_B
    )
    if half_source != minimax_formula:
        raise AssertionError("common-midpoint lower-bound formula is inconsistent")
    return {
        "selected_axes": list(SELECTED_AXES),
        "epsilon_a": _fraction_text(TV_EPSILON_A),
        "epsilon_b": _fraction_text(TV_EPSILON_B),
        "moved_factor_a": _fraction_vector_payload(moved_a),
        "moved_factor_b": _fraction_vector_payload(moved_b),
        "margin_tv_d_a": _fraction_text(d_a),
        "margin_tv_d_b": _fraction_text(d_b),
        "source_total_variation": _fraction_text(source_tv),
        "sharp_modulus_rhs": _fraction_text(modulus),
        "sharp_modulus_equality_verified": True,
        "common_midpoint_a_sha256": _sha256(_fraction_vector_payload(midpoint_a)),
        "common_midpoint_b_sha256": _sha256(_fraction_vector_payload(midpoint_b)),
        "common_midpoint_endpoint_distances": _fraction_vector_payload(
            midpoint_distances
        ),
        "half_source_total_variation": _fraction_text(half_source),
        "minimax_lower_formula": _fraction_text(minimax_formula),
        "common_midpoint_lower_witness_verified": True,
    }


def _build_tangent_section() -> dict[str, object]:
    r = AXIS_COUNT
    s = EXPONENTS_PER_AXIS
    columns = uniform_tangent_columns(r, s)
    metric = tangent_source_metric(r, s)
    expected_one_axis_metric = [list(row) for row in CONTRAST_METRIC]
    expected_metric = [
        [
            Fraction(expected_one_axis_metric[row % 3][column % 3], s ** (r - 1))
            if row // 3 == column // 3
            else Fraction(0)
            for column in range(9)
        ]
        for row in range(9)
    ]
    if metric != expected_metric or _determinant(metric) != Fraction(1, 2**30):
        raise AssertionError("uniform product source metric is inconsistent")
    action: list[list[int]] = []
    for observed_axis in range(r):
        row: list[int] = []
        for factor_axis in range(r):
            block = columns[factor_axis * (s - 1) : (factor_axis + 1) * (s - 1)]
            projected = [
                calibrated_projector_apply(column, r, s, observed_axis)
                for column in block
            ]
            expected = (
                [[Fraction(0) for _ in column] for column in block]
                if observed_axis == factor_axis
                else block
            )
            if projected != expected:
                raise AssertionError("calibrated projector tangent action failed")
            row.append(0 if observed_axis == factor_axis else 1)
        action.append(row)
    designs = {
        "all_three_uniform": certify_tangent_design(
            "all three axes with uniform weights",
            (Fraction(1, 3),) * 3,
            r,
            s,
        ),
        "two_axis_half": certify_tangent_design(
            "axes zero and one with half weights",
            (Fraction(1, 2), Fraction(1, 2), Fraction(0)),
            r,
            s,
        ),
        "one_axis": certify_tangent_design(
            "axis zero only",
            (Fraction(1), Fraction(0), Fraction(0)),
            r,
            s,
        ),
    }
    return {
        "uniform_factor": _fraction_vector_payload(UNIFORM_FACTOR),
        "factor_contrast_columns": [list(column) for column in CONTRAST_COLUMNS],
        "one_factor_contrast_metric": [list(row) for row in CONTRAST_METRIC],
        "factor_tangent_dimension": len(columns),
        "source_metric_rule": "ambient coefficient Euclidean metric pulled back by dPhi",
        "source_metric_coordinate_matrix": _fraction_matrix_payload(metric),
        "source_metric_determinant": _fraction_text(_determinant(metric)),
        "source_metric_sha256": _sha256(_fraction_matrix_payload(metric)),
        "calibrated_marginal_rule": "P_j=R_j^*R_j=(1/s) M_j^* M_j",
        "projector_action_on_factor_blocks": action,
        "designs": designs,
    }


def build_payload() -> dict[str, object]:
    if AMBIENT_DIMENSION > MAX_FORMAL_DIMENSION:
        raise ValueError("canonical model exceeds the formal resource cap")
    payload = {
        "parameters": {
            "prime_axes": list(PRIMES),
            "axis_count": AXIS_COUNT,
            "exponents_per_axis": EXPONENTS_PER_AXIS,
            "ambient_dimension": AMBIENT_DIMENSION,
            "ambient_full_interaction_dimension": (
                EXPONENTS_PER_AXIS - 1
            ) ** AXIS_COUNT,
            "state_order": "lexicographic product(range(4), repeat=3)",
            "marginal_calibration": "R_j=s^(-1/2) M_j",
        },
        "normalized_product_reconstruction": _build_normalized_product_section(),
        "one_axis_probability_collision": _build_probability_collision_section(),
        "free_scale_exceptional_collision": _build_free_scale_section(),
        "sharp_tv_witness": _build_tv_witness_section(),
        "uniform_product_tangent_geometry": _build_tangent_section(),
        "implementation": {
            "arithmetic": "integers and fractions.Fraction only",
            "binary64_used_for_proof_decisions": False,
            "external_packages_required": False,
            "serialized_resource_cap_bytes": MAX_ARTIFACT_BYTES,
        },
        "formal_scope": {
            "normalized_model": "labelled nonnegative unit-sum rank-one tensors",
            "free_scale_model": "signed integer geometric factors v_4(u)",
            "raw_resonant_noise_geometry_certified": False,
            "calibrated_marginal_geometry_certified": True,
            "claim": (
                "exact structured reconstruction, collisions, TV witnesses, "
                "and uniform-product pullback geometry on the finite prime box"
            ),
        },
        "overall_passed": True,
    }
    return payload


def build_artifact() -> dict[str, object]:
    payload = build_payload()
    return {"schema": SCHEMA, "payload": payload, "payload_sha256": _sha256(payload)}


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


def _validate_stored_shape(artifact: dict[str, object]) -> None:
    if not isinstance(artifact, dict):
        raise ValueError("artifact must be a JSON object")
    _validate_resource_tree(artifact)
    if set(artifact) != {"schema", "payload", "payload_sha256"}:
        raise ValueError("artifact has unexpected top-level fields")
    if artifact["schema"] != SCHEMA:
        raise ValueError("unsupported normalized-product schema")
    digest = artifact["payload_sha256"]
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(character not in "0123456789abcdef" for character in digest)
    ):
        raise ValueError("payload digest is not canonical lowercase SHA-256")
    payload = artifact["payload"]
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    expected_keys = {
        "parameters",
        "normalized_product_reconstruction",
        "one_axis_probability_collision",
        "free_scale_exceptional_collision",
        "sharp_tv_witness",
        "uniform_product_tangent_geometry",
        "implementation",
        "formal_scope",
        "overall_passed",
    }
    if set(payload) != expected_keys:
        raise ValueError("payload has unexpected fields")
    parameters = payload.get("parameters")
    if not isinstance(parameters, dict):
        raise ValueError("parameters must be an object")
    if parameters.get("prime_axes") != list(PRIMES) or not all(
        type(value) is int for value in parameters.get("prime_axes", [])
    ):
        raise ValueError("artifact uses noncanonical prime axes")
    for key, expected in (
        ("axis_count", AXIS_COUNT),
        ("exponents_per_axis", EXPONENTS_PER_AXIS),
        ("ambient_dimension", AMBIENT_DIMENSION),
    ):
        if type(parameters.get(key)) is not int or parameters[key] != expected:
            raise ValueError(f"{key} is not a canonical integer")
    reconstruction = payload.get("normalized_product_reconstruction")
    if not isinstance(reconstruction, dict):
        raise ValueError("normalized reconstruction section is malformed")
    factors = reconstruction.get("canonical_factors")
    if (
        not isinstance(factors, list)
        or len(factors) != AXIS_COUNT
        or any(not isinstance(factor, list) or len(factor) != EXPONENTS_PER_AXIS for factor in factors)
    ):
        raise ValueError("canonical factor list violates the resource cap")
    for factor in factors:
        parsed = [_parse_fraction_limited(value) for value in factor]
        _validate_probability_factor(parsed, EXPONENTS_PER_AXIS)
    tangent = payload.get("uniform_product_tangent_geometry")
    if not isinstance(tangent, dict):
        raise ValueError("tangent geometry section is malformed")
    metric = tangent.get("source_metric_coordinate_matrix")
    if (
        not isinstance(metric, list)
        or len(metric) != 9
        or any(not isinstance(row, list) or len(row) != 9 for row in metric)
    ):
        raise ValueError("source metric violates the exact dimension cap")
    for row in metric:
        for value in row:
            _parse_fraction_limited(value)
    designs = tangent.get("designs")
    if not isinstance(designs, dict) or set(designs) != {
        "all_three_uniform",
        "two_axis_half",
        "one_axis",
    }:
        raise ValueError("tangent design set is noncanonical")
    for design in designs.values():
        if not isinstance(design, dict):
            raise ValueError("tangent design record must be an object")
        weights = design.get("weights")
        spectrum = design.get("generalized_spectrum")
        if not isinstance(weights, list) or len(weights) != AXIS_COUNT:
            raise ValueError("design weight list violates the resource cap")
        parsed_weights = [_parse_fraction_limited(value) for value in weights]
        if any(weight < 0 for weight in parsed_weights) or sum(parsed_weights, Fraction(0)) != 1:
            raise ValueError("design weights are not an exact probability vector")
        if not isinstance(spectrum, list) or not 1 <= len(spectrum) <= AXIS_COUNT:
            raise ValueError("generalized spectrum violates the resource cap")
    if len(_canonical_json(artifact)) > MAX_ARTIFACT_BYTES:
        raise ValueError("artifact exceeds the serialized resource cap")


def verify_artifact(artifact: dict[str, object]) -> dict[str, object]:
    """Rebuild every exact claim and reject stale or semantic tampering."""

    _validate_stored_shape(artifact)
    payload = artifact["payload"]
    if artifact["payload_sha256"] != _sha256(payload):
        raise ValueError("payload digest mismatch")
    expected = build_artifact()
    if _canonical_json(artifact) != _canonical_json(expected):
        raise ValueError("artifact does not equal independent exact reconstruction")
    designs = expected["payload"]["uniform_product_tangent_geometry"]["designs"]
    return {
        "verified": True,
        "schema": SCHEMA,
        "payload_sha256": artifact["payload_sha256"],
        "normalized_product_dimension": 9,
        "two_axis_tangent_floor": designs["two_axis_half"]["generalized_floor"],
        "all_axis_tangent_floor": designs["all_three_uniform"]["generalized_floor"],
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
    if len(value.lstrip("-")) > 80:
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
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    if args.verify is not None:
        result = verify_artifact(_read_artifact(args.verify))
    else:
        result = build_artifact()
    rendered = json.dumps(result, indent=None if args.compact else 2, sort_keys=True) + "\n"
    if args.write is not None:
        args.write.write_bytes(rendered.encode("utf-8"))
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
