#!/usr/bin/env python3
"""Exact finite certificates for model-aware quotient robustness.

This module complements the ambient E-optimal protocol engine.  It asks
whether a declared model survives the common observation kernel, how source
tubes reduce quotient separation, how the model tangent meets the kernel,
and whether interval response uncertainty preserves a nominal quotient.

All declared inputs and theorem decisions use ``fractions.Fraction``.
Floating generalized eigensolvers only propose strict rational form bounds;
exact LDL elimination is the acceptance test.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd, isfinite, isqrt
from typing import Sequence

from scipy.linalg import eigh

from oig_protocol_design_engine import (
    ExactScalar,
    QMatrix,
    _add,
    _float_matrix,
    _fraction_text,
    _identity,
    _inverse,
    _ldl_positive_definite,
    _matmul,
    _matrix_text,
    _q,
    _row_basis,
    _scale,
    _shape,
    _subtract,
    _transpose,
    _zeros,
    rational_matrix,
)


Q = Fraction


def _vector(values: Sequence[ExactScalar], dimension: int, name: str) -> tuple[Fraction, ...]:
    result = tuple(_q(value) for value in values)
    if len(result) != dimension:
        raise ValueError(f"{name} has the wrong dimension")
    return result


def _column(values: Sequence[Fraction]) -> QMatrix:
    return tuple((value,) for value in values)


def _flatten_column(matrix: QMatrix) -> tuple[Fraction, ...]:
    if _shape(matrix)[1] != 1:
        raise ValueError("expected a column vector")
    return tuple(row[0] for row in matrix)


def _quadratic(matrix: QMatrix, vector: Sequence[Fraction]) -> Fraction:
    column = _column(vector)
    return _matmul(_transpose(column), _matmul(matrix, column))[0][0]


def _absolute(matrix: QMatrix) -> QMatrix:
    return tuple(tuple(abs(value) for value in row) for row in matrix)


def _diagonal(values: Sequence[Fraction]) -> QMatrix:
    return tuple(
        tuple(value if row == column else Q(0) for column in range(len(values)))
        for row, value in enumerate(values)
    )


def _zero(matrix: QMatrix) -> bool:
    return all(value == 0 for row in matrix for value in row)


def _rank(matrix: QMatrix) -> int:
    rows, columns = _shape(matrix)
    return len(_row_basis(matrix, columns)) if rows else 0


def _nullspace_columns(matrix: QMatrix) -> QMatrix:
    """Return a rational column basis for the right nullspace."""
    rows, columns = _shape(matrix)
    reduced = _row_basis(matrix, columns) if rows else tuple()
    pivot_columns: list[int] = []
    for row in reduced:
        pivot = next(index for index, value in enumerate(row) if value)
        pivot_columns.append(pivot)
    free_columns = [column for column in range(columns) if column not in pivot_columns]
    if not free_columns:
        return _zeros(columns, 0)
    basis: list[list[Fraction]] = []
    for free in free_columns:
        vector = [Q(0) for _ in range(columns)]
        vector[free] = Q(1)
        for row, pivot in zip(reduced, pivot_columns):
            vector[pivot] = -row[free]
        basis.append(vector)
    return tuple(
        tuple(basis[column][row] for column in range(len(basis)))
        for row in range(columns)
    )


def _sqrt_bounds(value: Fraction, bits: int = 96) -> tuple[Fraction, Fraction]:
    """Directed dyadic bounds on the square root of a nonnegative rational."""
    if type(bits) is not int or bits < 1:
        raise ValueError("square-root precision must be a positive integer")
    if value < 0:
        raise ValueError("cannot bound the square root of a negative rational")
    if value == 0:
        return Q(0), Q(0)
    scale = 1 << bits
    scaled_floor = (value.numerator * scale * scale) // value.denominator
    lower_integer = isqrt(scaled_floor)
    lower = Q(lower_integer, scale)
    if lower * lower == value:
        return lower, lower
    return lower, Q(lower_integer + 1, scale)


def _strict_form_lower(numerator: QMatrix, denominator: QMatrix) -> Fraction:
    """Return exact L>0 with numerator-L*denominator positive definite."""
    if _shape(numerator) != _shape(denominator) or not _ldl_positive_definite(denominator):
        raise ValueError("generalized form dimensions or denominator are invalid")
    if not _ldl_positive_definite(numerator):
        return Q(0)
    if len(numerator) == 1:
        return numerator[0][0] / denominator[0][0]
    try:
        proposal = float(
            eigh(
                _float_matrix(numerator),
                _float_matrix(denominator),
                eigvals_only=True,
            )[0]
        )
        if not isfinite(proposal):
            raise OverflowError("floating generalized eigenvalue is nonfinite")
        candidate = Q(
            str(max(proposal, 0.0) * (1.0 - 1.0e-8))
        ).limit_denominator(10**60)
    except (ArithmeticError, OverflowError, ValueError):
        # The reciprocal generalized eigenvalues are the nonnegative
        # eigenvalues of numerator^-1*denominator.  Their largest value is at
        # most the exact trace, hence 1/(trace+1) is a strict positive lower
        # bound for lambda_min(numerator, denominator).  Exact LDL below is
        # still the theorem decision.
        numerator_inverse = _inverse(numerator)
        reciprocal_trace = sum(
            (
                numerator_inverse[row][column] * denominator[column][row]
                for row in range(len(numerator))
                for column in range(len(numerator))
            ),
            Q(0),
        )
        if reciprocal_trace < 0:
            raise ArithmeticError("positive forms produced a negative reciprocal trace")
        candidate = 1 / (reciprocal_trace + 1)
    for _ in range(256):
        if candidate > 0 and _ldl_positive_definite(
            _subtract(numerator, _scale(denominator, candidate))
        ):
            return candidate
        candidate /= 2
    raise ArithmeticError("could not certify a positive generalized form lower bound")


def _strict_form_upper(numerator: QMatrix, denominator: QMatrix) -> Fraction:
    """Return exact U>=0 with U*denominator-numerator positive definite."""
    if _shape(numerator) != _shape(denominator) or not _ldl_positive_definite(denominator):
        raise ValueError("generalized form dimensions or denominator are invalid")
    if _zero(numerator):
        return Q(0)
    if len(numerator) == 1:
        return numerator[0][0] / denominator[0][0]
    try:
        proposal = float(
            eigh(
                _float_matrix(numerator),
                _float_matrix(denominator),
                eigvals_only=True,
            )[-1]
        )
        if not isfinite(proposal):
            raise OverflowError("floating generalized eigenvalue is nonfinite")
        candidate = Q(
            str(max(proposal, 0.0) * (1.0 + 1.0e-8) + 1.0e-300)
        ).limit_denominator(10**60)
    except (ArithmeticError, OverflowError, ValueError):
        # For a positive-semidefinite numerator, every generalized eigenvalue
        # is nonnegative and is bounded above by
        # tr(denominator^-1*numerator).  This exact fallback avoids making
        # theorem production depend on binary64 range.
        denominator_inverse = _inverse(denominator)
        trace = sum(
            (
                denominator_inverse[row][column] * numerator[column][row]
                for row in range(len(numerator))
                for column in range(len(numerator))
            ),
            Q(0),
        )
        candidate = max(trace, Q(0)) + 1
    for _ in range(256):
        if candidate > 0 and _ldl_positive_definite(
            _subtract(_scale(denominator, candidate), numerator)
        ):
            return candidate
        candidate = 2 * candidate if candidate else Q(1, 10**60)
    raise ArithmeticError("could not certify a generalized form upper bound")


def _form_lower_report(numerator: QMatrix, denominator: QMatrix) -> dict[str, object]:
    lower = _strict_form_lower(numerator, denominator)
    if lower == 0:
        return {
            "positive": False,
            "lower_exact": "0/1",
            "lower_kind": "exact zero or no positive strict certificate",
        }
    exact_one_dimensional = len(numerator) == 1
    return {
        "positive": True,
        "lower_exact": _fraction_text(lower),
        "lower_kind": "exact" if exact_one_dimensional else "strict exact-rational LDL lower",
        "exact_ldl_decision": True,
    }


@dataclass(frozen=True)
class ExactQuotient:
    """The minimum-source-cost quotient determined by a response row space."""

    response: QMatrix
    source_metric: QMatrix
    row_coordinates: QMatrix
    quotient_metric: QMatrix
    injection: QMatrix
    projection: QMatrix
    blind_basis: QMatrix


def exact_model_quotient(
    response: Sequence[Sequence[ExactScalar]],
    source_metric: Sequence[Sequence[ExactScalar]],
) -> ExactQuotient:
    matrix = rational_matrix(response)
    metric = rational_matrix(source_metric)
    rows, dimension = _shape(matrix)
    if rows < 1:
        raise ValueError("response must have at least one row")
    if _shape(metric) != (dimension, dimension):
        raise ValueError("source metric has the wrong dimension")
    if not _ldl_positive_definite(metric):
        raise ValueError("source metric must be symmetric positive definite")
    coordinates = _row_basis(matrix, dimension)
    if not coordinates:
        raise ValueError("the declared response is identically zero")
    source_inverse = _inverse(metric)
    quotient_metric = _inverse(
        _matmul(coordinates, _matmul(source_inverse, _transpose(coordinates)))
    )
    injection = _matmul(
        source_inverse,
        _matmul(_transpose(coordinates), quotient_metric),
    )
    projection = _matmul(injection, coordinates)
    if _matmul(coordinates, injection) != _identity(len(coordinates)):
        raise AssertionError("minimum-cost injection is not a right inverse")
    blind_basis = _nullspace_columns(coordinates)
    if _shape(blind_basis)[1] and not _zero(_matmul(matrix, blind_basis)):
        raise AssertionError("computed blind basis is not in the response kernel")
    return ExactQuotient(
        matrix,
        metric,
        coordinates,
        quotient_metric,
        injection,
        projection,
        blind_basis,
    )


def quotient_distance_squared(
    quotient: ExactQuotient, secant: Sequence[ExactScalar]
) -> Fraction:
    dimension = _shape(quotient.response)[1]
    vector = _vector(secant, dimension, "secant")
    coordinates = _flatten_column(_matmul(quotient.row_coordinates, _column(vector)))
    return _quadratic(quotient.quotient_metric, coordinates)


def _minimum_representative(
    quotient: ExactQuotient, secant: Sequence[Fraction]
) -> tuple[Fraction, ...]:
    coordinates = _matmul(quotient.row_coordinates, _column(secant))
    return _flatten_column(_matmul(quotient.injection, coordinates))


def certify_quotient_tube_pair(
    response: Sequence[Sequence[ExactScalar]],
    source_metric: Sequence[Sequence[ExactScalar]],
    secant: Sequence[ExactScalar],
    *,
    source_radius: ExactScalar,
    quotient_noise_radius: ExactScalar = 0,
    sqrt_bits: int = 96,
) -> dict[str, object]:
    """Certify the exact equal-radius tube gap in the induced quotient norm.

    The two source balls both have radius ``source_radius``.  Optional data
    noise is assumed to lie in the response range and to be bounded in the
    source-induced quotient norm.  Under precisely that declaration, the
    separation gap is ``(d_Q-2*rho-2*epsilon_Q)_+``.
    """
    quotient = exact_model_quotient(response, source_metric)
    dimension = _shape(quotient.response)[1]
    vector = _vector(secant, dimension, "secant")
    rho = _q(source_radius)
    epsilon = _q(quotient_noise_radius)
    if rho < 0 or epsilon < 0:
        raise ValueError("tube radii must be nonnegative")
    distance_squared = quotient_distance_squared(quotient, vector)
    distance_lower, distance_upper = _sqrt_bounds(distance_squared, sqrt_bits)
    erosion = 2 * (rho + epsilon)
    overlap = distance_squared <= erosion * erosion
    gap_lower = Q(0) if overlap else max(Q(0), distance_lower - erosion)
    gap_upper = Q(0) if overlap else distance_upper - erosion
    representative = _minimum_representative(quotient, vector)
    source_only_overlap = distance_squared <= (2 * rho) ** 2
    witness: dict[str, object] | None = None
    if source_only_overlap:
        left_error = tuple(-value / 2 for value in representative)
        right_error = tuple(value / 2 for value in representative)
        witness = {
            "minimum_representative_exact": [_fraction_text(value) for value in representative],
            "left_source_error_exact": [_fraction_text(value) for value in left_error],
            "right_source_error_exact": [_fraction_text(value) for value in right_error],
            "witness_norm_squared_exact": _fraction_text(distance_squared / 4),
        }
    return {
        "schema_version": "oig-quotient-tube-pair-v1",
        "response_exact": _matrix_text(quotient.response),
        "source_metric_exact": _matrix_text(quotient.source_metric),
        "sqrt_bits": sqrt_bits,
        "quotient_rank": len(quotient.row_coordinates),
        "blind_dimension": _shape(quotient.blind_basis)[1],
        "secant_exact": [_fraction_text(value) for value in vector],
        "quotient_distance_squared_exact": _fraction_text(distance_squared),
        "quotient_distance_lower_exact": _fraction_text(distance_lower),
        "quotient_distance_upper_exact": _fraction_text(distance_upper),
        "source_radius_exact": _fraction_text(rho),
        "quotient_noise_radius_exact": _fraction_text(epsilon),
        "erosion_exact": _fraction_text(erosion),
        "response_tubes_overlap_exactly": overlap,
        "quotient_gap_lower_exact": _fraction_text(gap_lower),
        "quotient_gap_upper_exact": _fraction_text(gap_upper),
        "source_only_overlap_witness": witness,
        "theorem": "gap_Q=(dist_S(secant,ker H)-2*rho-2*epsilon_Q)_+",
    }


def certify_response_tube_pair(
    response: Sequence[Sequence[ExactScalar]],
    source_metric: Sequence[Sequence[ExactScalar]],
    output_metric: Sequence[Sequence[ExactScalar]],
    secant: Sequence[ExactScalar],
    *,
    source_radius: ExactScalar,
    data_noise_radius: ExactScalar,
    sqrt_bits: int = 96,
) -> dict[str, object]:
    """Give exact overlap or conservative disjointness certificates in Y norm.

    At zero data noise the quotient criterion is exact.  With simultaneous
    source and ordinary output noise, this routine returns a sound three-way
    result: certified overlap, certified disjointness, or undecided.
    """
    quotient = exact_model_quotient(response, source_metric)
    matrix = quotient.response
    rows, dimension = _shape(matrix)
    metric_y = rational_matrix(output_metric)
    if _shape(metric_y) != (rows, rows) or not _ldl_positive_definite(metric_y):
        raise ValueError("output metric must be positive definite with response-row dimension")
    _sqrt_bounds(Q(0), sqrt_bits)
    vector = _vector(secant, dimension, "secant")
    rho = _q(source_radius)
    epsilon = _q(data_noise_radius)
    if rho < 0 or epsilon < 0:
        raise ValueError("tube radii must be nonnegative")

    information = _matmul(_transpose(matrix), _matmul(metric_y, matrix))
    centre_squared = _quadratic(information, vector)
    centre_lower, centre_upper = _sqrt_bounds(centre_squared, sqrt_bits)
    gain_squared_upper = _strict_form_upper(information, quotient.source_metric)
    _, gain_upper = _sqrt_bounds(gain_squared_upper, sqrt_bits)
    image_erosion_upper = 2 * rho * gain_upper + 2 * epsilon

    quotient_squared = quotient_distance_squared(quotient, vector)
    source_overlap = quotient_squared <= (2 * rho) ** 2
    noise_only_overlap = centre_squared <= (2 * epsilon) ** 2
    certified_overlap = source_overlap or noise_only_overlap
    if epsilon == 0:
        certified_disjoint = not source_overlap
    elif rho == 0:
        certified_disjoint = not noise_only_overlap
    else:
        certified_disjoint = centre_lower > image_erosion_upper
    if certified_overlap and certified_disjoint:
        raise AssertionError("overlap and disjointness certificates contradicted")
    if certified_overlap:
        status = "certified_overlap"
    elif certified_disjoint:
        status = "certified_disjoint"
    else:
        status = "undecided_by_conservative_raw_bound"
    return {
        "schema_version": "oig-raw-response-tube-pair-v1",
        "response_exact": _matrix_text(matrix),
        "source_metric_exact": _matrix_text(quotient.source_metric),
        "output_metric_exact": _matrix_text(metric_y),
        "secant_exact": [_fraction_text(value) for value in vector],
        "sqrt_bits": sqrt_bits,
        "status": status,
        "raw_centre_distance_squared_exact": _fraction_text(centre_squared),
        "raw_centre_distance_lower_exact": _fraction_text(centre_lower),
        "raw_centre_distance_upper_exact": _fraction_text(centre_upper),
        "source_to_output_gain_squared_upper_exact": _fraction_text(gain_squared_upper),
        "source_to_output_gain_upper_exact": _fraction_text(gain_upper),
        "raw_image_erosion_upper_exact": _fraction_text(image_erosion_upper),
        "source_radius_exact": _fraction_text(rho),
        "data_noise_radius_exact": _fraction_text(epsilon),
        "source_only_overlap_exact": source_overlap,
        "noise_only_overlap_exact": noise_only_overlap,
        "certified_overlap": certified_overlap,
        "certified_disjoint": certified_disjoint,
        "decision_is_exact": epsilon == 0 or rho == 0,
        "proof_boundary": (
            "For positive ordinary data noise, an undecided result is not an overlap claim. "
            "Exact two-noise geometry is a convex trust-region problem unless noise is declared in quotient norm."
        ),
    }


def certify_finite_quotient_secants(
    response: Sequence[Sequence[ExactScalar]],
    source_metric: Sequence[Sequence[ExactScalar]],
    secants: Sequence[Sequence[ExactScalar]],
    *,
    source_radius: ExactScalar = 0,
    quotient_noise_radius: ExactScalar = 0,
    sqrt_bits: int = 96,
) -> dict[str, object]:
    """Certify quotient separation and exact tube loss for a finite secant set."""
    if not secants:
        raise ValueError("at least one nonzero secant is required")
    quotient = exact_model_quotient(response, source_metric)
    dimension = _shape(quotient.response)[1]
    rho = _q(source_radius)
    epsilon = _q(quotient_noise_radius)
    if rho < 0 or epsilon < 0:
        raise ValueError("tube radii must be nonnegative")
    erosion = 2 * (rho + epsilon)
    records: list[dict[str, object]] = []
    minimum_ratio_squared: Fraction | None = None
    all_separated = True
    minimum_gap_lower: Fraction | None = None
    for index, secant in enumerate(secants):
        vector = _vector(secant, dimension, f"secant {index}")
        ambient_squared = _quadratic(quotient.source_metric, vector)
        if ambient_squared <= 0:
            raise ValueError("secants must be nonzero")
        distance_squared = quotient_distance_squared(quotient, vector)
        ratio_squared = distance_squared / ambient_squared
        distance_lower, distance_upper = _sqrt_bounds(distance_squared, sqrt_bits)
        overlap = distance_squared <= erosion * erosion
        gap_lower = Q(0) if overlap else max(Q(0), distance_lower - erosion)
        gap_upper = Q(0) if overlap else distance_upper - erosion
        all_separated = all_separated and distance_squared > 0
        minimum_ratio_squared = (
            ratio_squared
            if minimum_ratio_squared is None
            else min(minimum_ratio_squared, ratio_squared)
        )
        minimum_gap_lower = gap_lower if minimum_gap_lower is None else min(minimum_gap_lower, gap_lower)
        records.append(
            {
                "index": index,
                "secant_exact": [_fraction_text(value) for value in vector],
                "ambient_norm_squared_exact": _fraction_text(ambient_squared),
                "quotient_distance_squared_exact": _fraction_text(distance_squared),
                "quotient_ratio_squared_exact": _fraction_text(ratio_squared),
                "tube_overlap_exact": overlap,
                "eroded_gap_lower_exact": _fraction_text(gap_lower),
                "eroded_gap_upper_exact": _fraction_text(gap_upper),
            }
        )
    assert minimum_ratio_squared is not None and minimum_gap_lower is not None
    alpha_lower, alpha_upper = _sqrt_bounds(minimum_ratio_squared, sqrt_bits)
    return {
        "schema_version": "oig-finite-quotient-secants-v1",
        "response_exact": _matrix_text(quotient.response),
        "source_metric_exact": _matrix_text(quotient.source_metric),
        "secant_declarations_exact": [
            record["secant_exact"] for record in records
        ],
        "sqrt_bits": sqrt_bits,
        "family_size": len(records),
        "finite_family_is_quotient_separated": all_separated,
        "minimum_quotient_ratio_squared_exact": _fraction_text(minimum_ratio_squared),
        "minimum_quotient_ratio_lower_exact": _fraction_text(alpha_lower),
        "minimum_quotient_ratio_upper_exact": _fraction_text(alpha_upper),
        "source_radius_exact": _fraction_text(rho),
        "quotient_noise_radius_exact": _fraction_text(epsilon),
        "common_separation_erosion_exact": _fraction_text(erosion),
        "minimum_eroded_gap_lower_exact": _fraction_text(minimum_gap_lower),
        "secants": records,
        "proof_boundary": "This is a global model certificate only when the supplied finite secant set is exhaustive.",
    }


def certify_tangent_kernel_angle(
    response: Sequence[Sequence[ExactScalar]],
    source_metric: Sequence[Sequence[ExactScalar]],
    tangent_basis: Sequence[Sequence[ExactScalar]],
    *,
    sqrt_bits: int = 96,
) -> dict[str, object]:
    """Certify the smallest tangent--kernel principal angle in source metric."""
    quotient = exact_model_quotient(response, source_metric)
    tangent = rational_matrix(tangent_basis)
    dimension, tangent_dimension = _shape(tangent)
    if dimension != _shape(quotient.response)[1]:
        raise ValueError("tangent basis has the wrong ambient dimension")
    tangent_metric = _matmul(_transpose(tangent), _matmul(quotient.source_metric, tangent))
    if not _ldl_positive_definite(tangent_metric):
        raise ValueError("tangent columns must be linearly independent")
    reduced_tangent = _matmul(quotient.row_coordinates, tangent)
    quotient_tangent = _matmul(
        _transpose(reduced_tangent),
        _matmul(quotient.quotient_metric, reduced_tangent),
    )
    rank = _rank(reduced_tangent)
    transverse = rank == tangent_dimension
    kernel_witness: dict[str, object] | None = None
    if not transverse:
        coefficient_basis = _nullspace_columns(reduced_tangent)
        coefficients = tuple(row[0] for row in coefficient_basis)
        ambient_witness = _flatten_column(_matmul(tangent, _column(coefficients)))
        kernel_witness = {
            "tangent_coefficients_exact": [_fraction_text(value) for value in coefficients],
            "ambient_tangent_kernel_vector_exact": [
                _fraction_text(value) for value in ambient_witness
            ],
        }
        lower = Q(0)
        upper = Q(0)
        amplification_upper: str | None = None
        lower_kind = "exact"
    else:
        lower = _strict_form_lower(quotient_tangent, tangent_metric)
        upper = min(
            quotient_tangent[index][index] / tangent_metric[index][index]
            for index in range(tangent_dimension)
        )
        _, amplification = _sqrt_bounds(1 / lower, sqrt_bits)
        amplification_upper = _fraction_text(amplification)
        lower_kind = "exact" if tangent_dimension == 1 else "strict exact-rational LDL lower"
    mu_lower, _ = _sqrt_bounds(lower, sqrt_bits)
    _, mu_upper = _sqrt_bounds(upper, sqrt_bits)
    return {
        "schema_version": "oig-tangent-kernel-angle-v1",
        "response_exact": _matrix_text(quotient.response),
        "source_metric_exact": _matrix_text(quotient.source_metric),
        "tangent_basis_exact": _matrix_text(tangent),
        "sqrt_bits": sqrt_bits,
        "ambient_dimension": dimension,
        "tangent_dimension": tangent_dimension,
        "quotient_rank_on_tangent": rank,
        "tangent_is_transverse_to_kernel": transverse,
        "tangent_metric_exact": _matrix_text(tangent_metric),
        "quotient_tangent_form_exact": _matrix_text(quotient_tangent),
        "mu_squared_lower_exact": _fraction_text(lower),
        "mu_squared_upper_exact": _fraction_text(upper),
        "mu_squared_lower_kind": lower_kind,
        "mu_lower_exact": _fraction_text(mu_lower),
        "mu_upper_exact": _fraction_text(mu_upper),
        "mismatch_amplification_upper_exact": amplification_upper,
        "kernel_witness": kernel_witness,
        "theorem": "linearized source-mismatch minimax radius is rho/mu",
    }


def certify_nominal_blind_uncertainty(
    response_centre: Sequence[Sequence[ExactScalar]],
    response_radius: Sequence[Sequence[ExactScalar]],
    source_metric: Sequence[Sequence[ExactScalar]],
    output_metric: Sequence[Sequence[ExactScalar]],
    *,
    blind_source_radius: ExactScalar | None = None,
    query_matrix: Sequence[Sequence[ExactScalar]] | None = None,
    model_secants: Sequence[Sequence[ExactScalar]] | None = None,
    model_secants_exhaustive: bool = False,
    model_secants_provenance: str | None = None,
    sqrt_bits: int = 96,
) -> dict[str, object]:
    """Audit nominal blind directions under an independent entrywise box.

    Because the symmetric response box contains its centre, uncertain
    activation can never produce a positive *uniform* information floor on a
    nominal blind direction.  Either the box preserves the blind subspace, or
    its amplitude must be bounded and its leakage treated as additional data
    uncertainty.
    """
    quotient = exact_model_quotient(response_centre, source_metric)
    radius = rational_matrix(response_radius)
    rows, dimension = _shape(quotient.response)
    if _shape(radius) != (rows, dimension):
        raise ValueError("response radius has the wrong shape")
    if any(value < 0 for row in radius for value in row):
        raise ValueError("response radii must be nonnegative")
    metric_y = rational_matrix(output_metric)
    if _shape(metric_y) != (rows, rows) or not _ldl_positive_definite(metric_y):
        raise ValueError("output metric must be positive definite with response-row dimension")
    _sqrt_bounds(Q(0), sqrt_bits)
    blind_radius_declaration = (
        None if blind_source_radius is None else _q(blind_source_radius)
    )
    if blind_radius_declaration is not None and blind_radius_declaration < 0:
        raise ValueError("blind source radius must be nonnegative")
    blind_dimension = _shape(quotient.blind_basis)[1]
    if type(model_secants_exhaustive) is not bool:
        raise TypeError("model_secants_exhaustive must be a boolean")
    if model_secants_provenance is not None and (
        not isinstance(model_secants_provenance, str)
        or not model_secants_provenance.strip()
    ):
        raise ValueError("model secant provenance must be a nonempty string when supplied")
    if model_secants_exhaustive and (
        model_secants is None
        or not model_secants
        or not isinstance(model_secants_provenance, str)
        or not model_secants_provenance.strip()
    ):
        raise ValueError("exhaustive model secants require a nonempty list and proof provenance")
    query_serialized = None
    query_insensitive = False
    if query_matrix is not None:
        query = rational_matrix(query_matrix)
        if _shape(query)[1] != dimension:
            raise ValueError("query matrix has the wrong source dimension")
        query_insensitive = blind_dimension == 0 or _zero(
            _matmul(query, quotient.blind_basis)
        )
        query_serialized = _matrix_text(query)
    secants_exclude_blind_collisions = False
    secants_serialized = None
    if model_secants is not None:
        if not model_secants:
            raise ValueError("a declared finite model-secant list cannot be empty")
        secants_exclude_blind_collisions = all(
            quotient_distance_squared(quotient, secant) > 0
            for secant in model_secants
        )
        secants_serialized = [
            [_fraction_text(value) for value in _vector(secant, dimension, "model secant")]
            for secant in model_secants
        ]
    secants_prove_task_irrelevance = (
        model_secants_exhaustive and secants_exclude_blind_collisions
    )
    if blind_dimension == 0:
        return {
            "schema_version": "oig-nominal-blind-uncertainty-v1",
            "response_centre_exact": _matrix_text(quotient.response),
            "response_radius_exact": _matrix_text(radius),
            "source_metric_exact": _matrix_text(quotient.source_metric),
            "output_metric_exact": _matrix_text(metric_y),
            "query_matrix_exact": query_serialized,
            "model_secants_exact": secants_serialized,
            "model_secants_exhaustive": model_secants_exhaustive,
            "model_secants_provenance": model_secants_provenance,
            "blind_source_radius_exact": (
                None if blind_radius_declaration is None else _fraction_text(blind_radius_declaration)
            ),
            "sqrt_bits": sqrt_bits,
            "blind_dimension": 0,
            "box_preserves_nominal_blind_subspace": True,
            "quotient_family_stable": True,
            "worst_case_blind_information_floor_exact": "0/1",
            "blind_leakage_gain_squared_upper_exact": "0/1",
            "blind_leakage_gain_upper_exact": "0/1",
            "bounded_blind_leakage_radius_upper_exact": "0/1",
            "query_is_insensitive_to_nominal_kernel": query_insensitive,
            "declared_model_secants_exclude_kernel_collisions": secants_exclude_blind_collisions,
            "exhaustive_model_secants_prove_task_irrelevance": secants_prove_task_irrelevance,
            "nominal_null_task_irrelevant": True,
            "nominal_null_safe_to_ignore": True,
            "quotient_rule": "no nominal blind directions are present",
        }

    leakage_envelope = _matmul(radius, _absolute(quotient.blind_basis))
    preserves = _zero(leakage_envelope)
    entry_form = _matmul(
        _transpose(leakage_envelope),
        _matmul(_absolute(metric_y), leakage_envelope),
    )
    row_sums = tuple(sum(row, Q(0)) for row in entry_form)
    diagonal_bound = _diagonal(row_sums)
    blind_metric = _matmul(
        _transpose(quotient.blind_basis),
        _matmul(quotient.source_metric, quotient.blind_basis),
    )
    gain_squared_upper = _strict_form_upper(diagonal_bound, blind_metric)
    _, gain_upper = _sqrt_bounds(gain_squared_upper, sqrt_bits)
    if blind_radius_declaration is None:
        blind_radius = None
        leakage_radius = None
    else:
        blind_radius = blind_radius_declaration
        leakage_radius = blind_radius * gain_upper
    if preserves:
        rule = "the response box preserves the nominal quotient exactly"
    elif blind_radius is None:
        rule = (
            "the nominal quotient is not uniform over the response box; an unbounded blind component "
            "makes quotient predictions uncontrolled"
        )
    else:
        rule = (
            "retain the nominal quotient, but treat bounded blind-component leakage as additional "
            "output uncertainty; never count uncertain activation as guaranteed information"
        )
    task_irrelevant = query_insensitive or secants_prove_task_irrelevance
    return {
        "schema_version": "oig-nominal-blind-uncertainty-v1",
        "response_centre_exact": _matrix_text(quotient.response),
        "response_radius_exact": _matrix_text(radius),
        "source_metric_exact": _matrix_text(quotient.source_metric),
        "output_metric_exact": _matrix_text(metric_y),
        "query_matrix_exact": query_serialized,
        "model_secants_exact": secants_serialized,
        "model_secants_exhaustive": model_secants_exhaustive,
        "model_secants_provenance": model_secants_provenance,
        "sqrt_bits": sqrt_bits,
        "blind_dimension": blind_dimension,
        "blind_basis_exact": _matrix_text(quotient.blind_basis),
        "blind_metric_exact": _matrix_text(blind_metric),
        "leakage_envelope_exact": _matrix_text(leakage_envelope),
        "leakage_diagonal_form_bound_exact": _matrix_text(diagonal_bound),
        "box_preserves_nominal_blind_subspace": preserves,
        "quotient_family_stable": preserves,
        "worst_case_blind_information_floor_exact": "0/1",
        "blind_leakage_gain_squared_upper_exact": _fraction_text(gain_squared_upper),
        "blind_leakage_gain_upper_exact": _fraction_text(gain_upper),
        "blind_source_radius_exact": None if blind_radius is None else _fraction_text(blind_radius),
        "bounded_blind_leakage_radius_upper_exact": (
            None if leakage_radius is None else _fraction_text(leakage_radius)
        ),
        "query_is_insensitive_to_nominal_kernel": query_insensitive,
        "declared_model_secants_exclude_kernel_collisions": secants_exclude_blind_collisions,
        "exhaustive_model_secants_prove_task_irrelevance": secants_prove_task_irrelevance,
        "nominal_null_task_irrelevant": task_irrelevant,
        "nominal_null_safe_to_ignore": task_irrelevant,
        "quotient_rule": rule,
        "critical_fact": "the centre response is an admissible member of the symmetric box",
        "query_relevance_rule": (
            "Task irrelevance requires exact ker(H) subset ker(L) or an exhaustive model-secant proof. "
            "Full-family null preservation proves structural quotient stability only."
        ),
    }


def certify_nominal_null_relevance(
    response: Sequence[Sequence[ExactScalar]],
    source_metric: Sequence[Sequence[ExactScalar]],
    *,
    query_matrix: Sequence[Sequence[ExactScalar]] | None = None,
    model_secants: Sequence[Sequence[ExactScalar]] | None = None,
    response_radius: Sequence[Sequence[ExactScalar]] | None = None,
    model_secants_exhaustive: bool = False,
    model_secants_provenance: str | None = None,
) -> dict[str, object]:
    """Apply the exact query/model/family rule before discarding a nullspace."""
    quotient = exact_model_quotient(response, source_metric)
    rows, dimension = _shape(quotient.response)
    blind_dimension = _shape(quotient.blind_basis)[1]
    if type(model_secants_exhaustive) is not bool:
        raise TypeError("model_secants_exhaustive must be a boolean")
    if model_secants_provenance is not None and (
        not isinstance(model_secants_provenance, str)
        or not model_secants_provenance.strip()
    ):
        raise ValueError("model secant provenance must be a nonempty string when supplied")
    if model_secants_exhaustive and (
        model_secants is None
        or not model_secants
        or not isinstance(model_secants_provenance, str)
        or not model_secants_provenance.strip()
    ):
        raise ValueError("exhaustive model secants require a nonempty list and proof provenance")
    query_serialized = None
    query_insensitive: bool | None = None
    if query_matrix is not None:
        query = rational_matrix(query_matrix)
        if _shape(query)[1] != dimension:
            raise ValueError("query matrix has the wrong source dimension")
        query_insensitive = _zero(_matmul(query, quotient.blind_basis))
        query_serialized = _matrix_text(query)
    model_excludes: bool | None = None
    secants_serialized = None
    if model_secants is not None:
        if not model_secants:
            raise ValueError("a declared finite model-secant list cannot be empty")
        model_excludes = all(
            quotient_distance_squared(quotient, secant) > 0 for secant in model_secants
        )
        secants_serialized = [
            [_fraction_text(value) for value in _vector(secant, dimension, "model secant")]
            for secant in model_secants
        ]
    family_preserves: bool | None = None
    if response_radius is not None:
        radius = rational_matrix(response_radius)
        if _shape(radius) != (rows, dimension):
            raise ValueError("response radius has the wrong shape")
        if any(value < 0 for row in radius for value in row):
            raise ValueError("response radii must be nonnegative")
        family_preserves = _zero(_matmul(radius, _absolute(quotient.blind_basis)))
        radius_serialized = _matrix_text(radius)
    else:
        radius_serialized = None
    exhaustive_model_proof = model_secants_exhaustive and model_excludes is True
    task_irrelevant = blind_dimension == 0 or query_insensitive is True or exhaustive_model_proof
    return {
        "schema_version": "oig-nominal-null-relevance-v1",
        "response_exact": _matrix_text(quotient.response),
        "source_metric_exact": _matrix_text(quotient.source_metric),
        "query_matrix_exact": query_serialized,
        "model_secants_exact": secants_serialized,
        "response_radius_exact": radius_serialized,
        "model_secants_exhaustive": model_secants_exhaustive,
        "model_secants_provenance": model_secants_provenance,
        "blind_dimension": blind_dimension,
        "blind_basis_exact": _matrix_text(quotient.blind_basis),
        "kernel_is_subset_of_query_kernel": query_insensitive,
        "declared_model_secants_exclude_kernel_collisions": model_excludes,
        "exhaustive_model_secants_prove_task_irrelevance": exhaustive_model_proof,
        "entire_response_box_preserves_nominal_null": family_preserves,
        "quotient_family_stable": family_preserves,
        "nominal_null_task_irrelevant": task_irrelevant,
        "nominal_null_safe_to_ignore": task_irrelevant,
        "rule": (
            "Task irrelevance requires exact ker(H) subset ker(L) or an exhaustive model-secant proof. "
            "Full-family null preservation proves structural quotient stability only."
        ),
        "finite_model_warning": (
            "The secant alternative is global only when the supplied list is an exhaustive difference set."
        ),
    }


def _primitive_integer_vector(vector: Sequence[Fraction]) -> tuple[int, ...]:
    denominator = 1
    for value in vector:
        denominator = denominator * value.denominator // gcd(denominator, value.denominator)
    integers = [value.numerator * (denominator // value.denominator) for value in vector]
    divisor = 0
    for value in integers:
        divisor = gcd(divisor, abs(value))
    if divisor == 0:
        raise ValueError("cannot primitive-normalize the zero vector")
    integers = [value // divisor for value in integers]
    first = next(value for value in integers if value)
    if first < 0:
        integers = [-value for value in integers]
    return tuple(integers)


def certify_rational_lattice_trichotomy(
    response: Sequence[Sequence[ExactScalar]],
    lattice_basis: Sequence[Sequence[ExactScalar]],
    output_metric: Sequence[Sequence[ExactScalar]],
    *,
    sqrt_bits: int = 96,
) -> dict[str, object]:
    """Decide AO-I's lattice trichotomy for an exact rational lattice map.

    The columns of ``lattice_basis`` generate the declared lattice.  For
    rational data, real rank deficiency always supplies a rational and hence
    integer kernel vector, so the unstable-but-injective middle regime cannot
    occur.  That regime requires an irrational map plus a separate exact
    integer-kernel argument.
    """
    matrix = rational_matrix(response)
    basis = rational_matrix(lattice_basis)
    rows, source_dimension = _shape(matrix)
    if _shape(basis)[0] != source_dimension:
        raise ValueError("lattice basis has the wrong ambient dimension")
    lattice_rank = _shape(basis)[1]
    basis_gram = _matmul(_transpose(basis), basis)
    if not _ldl_positive_definite(basis_gram):
        raise ValueError("lattice-basis columns must be linearly independent")
    metric_y = rational_matrix(output_metric)
    if _shape(metric_y) != (rows, rows) or not _ldl_positive_definite(metric_y):
        raise ValueError("output metric must be positive definite with response-row dimension")
    image = _matmul(matrix, basis)
    real_rank = _rank(image)
    if real_rank < lattice_rank:
        null_basis = _nullspace_columns(image)
        rational_witness = tuple(row[0] for row in null_basis)
        integer_witness = _primitive_integer_vector(rational_witness)
        image_witness = _flatten_column(_matmul(image, _column(tuple(Q(x) for x in integer_witness))))
        if any(image_witness):
            raise AssertionError("integer collision witness is not in the image kernel")
        return {
            "schema_version": "oig-rational-lattice-trichotomy-v1",
            "response_exact": _matrix_text(matrix),
            "lattice_basis_exact": _matrix_text(basis),
            "output_metric_exact": _matrix_text(metric_y),
            "sqrt_bits": sqrt_bits,
            "regime": "exact_integer_collision",
            "lattice_rank": lattice_rank,
            "real_image_rank": real_rank,
            "integer_kernel_witness": list(integer_witness),
            "uniform_separation_lower_exact": "0/1",
            "middle_regime_excluded_by_rationality": True,
        }
    image_gram = _matmul(_transpose(image), _matmul(metric_y, image))
    squared_lower = _strict_form_lower(image_gram, _identity(lattice_rank))
    separation_lower, _ = _sqrt_bounds(squared_lower, sqrt_bits)
    return {
        "schema_version": "oig-rational-lattice-trichotomy-v1",
        "response_exact": _matrix_text(matrix),
        "lattice_basis_exact": _matrix_text(basis),
        "output_metric_exact": _matrix_text(metric_y),
        "sqrt_bits": sqrt_bits,
        "regime": "stable_lattice_observability",
        "lattice_rank": lattice_rank,
        "real_image_rank": real_rank,
        "integer_kernel_witness": None,
        "uniform_separation_squared_lower_exact": _fraction_text(squared_lower),
        "uniform_separation_lower_exact": _fraction_text(separation_lower),
        "middle_regime_excluded_by_rationality": True,
        "proof_boundary": (
            "For irrational response entries, real-rank-deficient but integer-kernel-free maps belong to AO-I regime 2; "
            "this rational checker deliberately does not guess that integer-kernel fact numerically."
        ),
    }


def classify_lattice_trichotomy_from_exact_predicates(
    *,
    lattice_rank: int,
    real_image_rank: int,
    integer_kernel_status: str,
    proof_reference: str,
) -> dict[str, object]:
    """Compose AO-I's trichotomy with an external exact integer-kernel proof.

    This interface is needed for irrational maps: rank is a real-linear fact,
    while absence of a nonzero integer kernel is Diophantine and must not be
    guessed from floating residuals.  ``proof_reference`` identifies the
    external exact argument; this function checks logical consistency only.
    """
    if lattice_rank < 1 or not 0 <= real_image_rank <= lattice_rank:
        raise ValueError("lattice and real-image ranks are inconsistent")
    if integer_kernel_status not in {"collision_proved", "kernel_free_proved"}:
        raise ValueError("integer kernel status must be backed by an exact proved predicate")
    if not proof_reference.strip():
        raise ValueError("an external exact proof reference is required")
    if real_image_rank == lattice_rank:
        if integer_kernel_status == "collision_proved":
            raise ValueError("full real column rank is incompatible with an integer collision")
        regime = "stable_lattice_observability"
        consequence = "the image lattice is discrete and has positive uniform separation"
    elif real_image_rank == 0 and integer_kernel_status == "kernel_free_proved":
        raise ValueError("a positive-rank lattice mapped to zero has an immediate integer collision")
    elif integer_kernel_status == "collision_proved":
        regime = "exact_integer_collision"
        consequence = "two distinct lattice targets have identical data"
    else:
        regime = "exact_injective_but_zero_uniform_separation"
        consequence = "infinite-precision identification holds, but every positive uniform noise radius fails"
    return {
        "schema_version": "oig-lattice-trichotomy-composition-v1",
        "regime": regime,
        "lattice_rank": lattice_rank,
        "real_image_rank": real_image_rank,
        "integer_kernel_status": integer_kernel_status,
        "external_exact_proof_reference": proof_reference,
        "consequence": consequence,
        "proof_boundary": "No floating residual may substitute for the referenced exact integer-kernel proof.",
    }


def certify_combined_model_design(
    response: Sequence[Sequence[ExactScalar]],
    source_metric: Sequence[Sequence[ExactScalar]],
    aggregate_information: Sequence[Sequence[ExactScalar]],
    model_secants: Sequence[Sequence[ExactScalar]],
    tangent_bases: Sequence[Sequence[Sequence[ExactScalar]]],
    *,
    response_radius: Sequence[Sequence[ExactScalar]] | None = None,
    output_metric: Sequence[Sequence[ExactScalar]] | None = None,
    blind_source_radius: ExactScalar | None = None,
    query_matrix: Sequence[Sequence[ExactScalar]] | None = None,
    model_secants_exhaustive: bool = False,
    model_secants_provenance: str | None = None,
    sqrt_bits: int = 96,
) -> dict[str, object]:
    """Audit an E-optimal candidate against model-aware quotient obligations.

    The return value is a vector certificate, not an arbitrarily scalarized
    objective.  Ambient information, finite secant separation, local tangent
    transversality, and uncertain blind leakage have different operational
    units and should be constrained or compared by a declared Pareto rule.
    """
    quotient = exact_model_quotient(response, source_metric)
    information = rational_matrix(aggregate_information)
    _sqrt_bounds(Q(0), sqrt_bits)
    if response_radius is None and output_metric is not None:
        raise ValueError("output metric without a response radius is unused and ambiguous")
    if response_radius is None and blind_source_radius is not None:
        raise ValueError("blind source radius requires a response uncertainty declaration")
    dimension = _shape(quotient.response)[1]
    if _shape(information) != (dimension, dimension):
        raise ValueError("aggregate information has the wrong dimension")
    if information != _transpose(information):
        raise ValueError("aggregate information must be symmetric")
    if _shape(quotient.blind_basis)[1] and not _zero(
        _matmul(information, quotient.blind_basis)
    ):
        raise ValueError("aggregate nominal information does not respect the declared response kernel")
    reduced_information = _matmul(
        _transpose(quotient.injection),
        _matmul(information, quotient.injection),
    )
    information_lower = _strict_form_lower(reduced_information, quotient.quotient_metric)
    secant_report = certify_finite_quotient_secants(
        response, source_metric, model_secants, sqrt_bits=sqrt_bits
    )
    tangent_reports = [
        certify_tangent_kernel_angle(
            response, source_metric, tangent, sqrt_bits=sqrt_bits
        )
        for tangent in tangent_bases
    ]
    relevance_report = certify_nominal_null_relevance(
        response,
        source_metric,
        query_matrix=query_matrix,
        model_secants=model_secants,
        response_radius=response_radius,
        model_secants_exhaustive=model_secants_exhaustive,
        model_secants_provenance=model_secants_provenance,
    )
    if response_radius is None:
        blind_report: dict[str, object] | None = None
        blind_rule_satisfied = True
    else:
        if output_metric is None:
            raise ValueError("output metric is required with a response radius")
        blind_report = certify_nominal_blind_uncertainty(
            response,
            response_radius,
            source_metric,
            output_metric,
            blind_source_radius=blind_source_radius,
            query_matrix=query_matrix,
            model_secants=model_secants,
            model_secants_exhaustive=model_secants_exhaustive,
            model_secants_provenance=model_secants_provenance,
            sqrt_bits=sqrt_bits,
        )
        blind_rule_satisfied = bool(
            blind_report["box_preserves_nominal_blind_subspace"]
            or blind_report["blind_dimension"] == 0
            or blind_source_radius is not None
        )
    tangents_transverse = all(
        bool(report["tangent_is_transverse_to_kernel"]) for report in tangent_reports
    )
    obligations = {
        "positive_information_on_nominal_quotient": information_lower > 0,
        "declared_finite_secants_avoid_kernel": bool(
            secant_report["finite_family_is_quotient_separated"]
        ),
        "declared_tangents_avoid_kernel": tangents_transverse,
        "uncertain_blind_direction_rule_satisfied": blind_rule_satisfied,
        "nominal_null_relevance_rule_satisfied": bool(
            relevance_report["nominal_null_safe_to_ignore"]
        ),
    }
    return {
        "schema_version": "oig-combined-model-design-v1",
        "response_exact": _matrix_text(quotient.response),
        "source_metric_exact": _matrix_text(quotient.source_metric),
        "aggregate_information_exact": _matrix_text(information),
        "model_secants_exact": secant_report["secant_declarations_exact"],
        "tangent_bases_exact": [
            _matrix_text(rational_matrix(tangent)) for tangent in tangent_bases
        ],
        "response_radius_exact": (
            None if response_radius is None else _matrix_text(rational_matrix(response_radius))
        ),
        "output_metric_exact": (
            None if output_metric is None else _matrix_text(rational_matrix(output_metric))
        ),
        "blind_source_radius_exact": (
            None if blind_source_radius is None else _fraction_text(_q(blind_source_radius))
        ),
        "query_matrix_exact": (
            None if query_matrix is None else _matrix_text(rational_matrix(query_matrix))
        ),
        "model_secants_exhaustive": model_secants_exhaustive,
        "model_secants_provenance": model_secants_provenance,
        "sqrt_bits": sqrt_bits,
        "source_dimension": dimension,
        "quotient_dimension": len(quotient.row_coordinates),
        "blind_dimension": _shape(quotient.blind_basis)[1],
        "quotient_information_exact": _matrix_text(reduced_information),
        "quotient_information_floor_lower_exact": _fraction_text(information_lower),
        "quotient_information_floor_lower_kind": (
            "exact" if len(reduced_information) == 1 else "strict exact-rational LDL lower"
        ),
        "finite_secant_certificate": secant_report,
        "tangent_certificates": tangent_reports,
        "blind_uncertainty_certificate": blind_report,
        "nominal_null_relevance_certificate": relevance_report,
        "obligations": obligations,
        "combined_target_passed": all(obligations.values()),
        "design_target": (
            "partial model-geometry audit: quotient information floor, quotient-secant floor, "
            "tangent angle, nominal-null relevance, and blind-leakage safety"
        ),
        "warning": (
            "A positive E-optimal quotient floor alone does not prove latent-model identifiability; "
            "the model may contain a secant or tangent direction in the discarded common kernel. "
            "Response-box information-form loss remains an external certificate and is not computed here."
        ),
    }


def _strict_report_difference(actual: object, expected: object, path: str = "$") -> str | None:
    """Return the first strict JSON-tree mismatch, including scalar types."""
    if type(actual) is not type(expected):
        return f"{path}: type {type(actual).__name__} != {type(expected).__name__}"
    if isinstance(expected, dict):
        actual_keys = set(actual)
        expected_keys = set(expected)
        if actual_keys != expected_keys:
            missing = sorted(expected_keys - actual_keys)
            extra = sorted(actual_keys - expected_keys)
            return f"{path}: key mismatch missing={missing} extra={extra}"
        for key in sorted(expected):
            difference = _strict_report_difference(actual[key], expected[key], f"{path}.{key}")
            if difference is not None:
                return difference
        return None
    if isinstance(expected, list):
        if len(actual) != len(expected):
            return f"{path}: length {len(actual)} != {len(expected)}"
        for index, (actual_value, expected_value) in enumerate(zip(actual, expected)):
            difference = _strict_report_difference(
                actual_value, expected_value, f"{path}[{index}]"
            )
            if difference is not None:
                return difference
        return None
    if actual != expected:
        return f"{path}: {actual!r} != {expected!r}"
    return None


def _serialized_positive_integer(report: dict[str, object], field: str) -> int:
    value = report[field]
    if type(value) is not int or value < 1:
        raise ValueError(f"{field} must be a positive JSON integer")
    return value


def _serialized_boolean(report: dict[str, object], field: str) -> bool:
    value = report[field]
    if type(value) is not bool:
        raise ValueError(f"{field} must be a JSON boolean")
    return value


def _rebuild_robust_model_report(report: dict[str, object]) -> dict[str, object]:
    """Rebuild one certificate solely from its serialized declarations."""
    if type(report) is not dict:
        raise TypeError("a robust certificate must be a JSON object")
    schema = report.get("schema_version")
    if type(schema) is not str:
        raise ValueError("schema_version must be a JSON string")

    if schema == "oig-quotient-tube-pair-v1":
        return certify_quotient_tube_pair(
            report["response_exact"],
            report["source_metric_exact"],
            report["secant_exact"],
            source_radius=report["source_radius_exact"],
            quotient_noise_radius=report["quotient_noise_radius_exact"],
            sqrt_bits=_serialized_positive_integer(report, "sqrt_bits"),
        )
    if schema == "oig-raw-response-tube-pair-v1":
        return certify_response_tube_pair(
            report["response_exact"],
            report["source_metric_exact"],
            report["output_metric_exact"],
            report["secant_exact"],
            source_radius=report["source_radius_exact"],
            data_noise_radius=report["data_noise_radius_exact"],
            sqrt_bits=_serialized_positive_integer(report, "sqrt_bits"),
        )
    if schema == "oig-finite-quotient-secants-v1":
        return certify_finite_quotient_secants(
            report["response_exact"],
            report["source_metric_exact"],
            report["secant_declarations_exact"],
            source_radius=report["source_radius_exact"],
            quotient_noise_radius=report["quotient_noise_radius_exact"],
            sqrt_bits=_serialized_positive_integer(report, "sqrt_bits"),
        )
    if schema == "oig-tangent-kernel-angle-v1":
        return certify_tangent_kernel_angle(
            report["response_exact"],
            report["source_metric_exact"],
            report["tangent_basis_exact"],
            sqrt_bits=_serialized_positive_integer(report, "sqrt_bits"),
        )
    if schema == "oig-nominal-blind-uncertainty-v1":
        exhaustive = _serialized_boolean(report, "model_secants_exhaustive")
        return certify_nominal_blind_uncertainty(
            report["response_centre_exact"],
            report["response_radius_exact"],
            report["source_metric_exact"],
            report["output_metric_exact"],
            blind_source_radius=report["blind_source_radius_exact"],
            query_matrix=report["query_matrix_exact"],
            model_secants=report["model_secants_exact"],
            model_secants_exhaustive=exhaustive,
            model_secants_provenance=report["model_secants_provenance"],
            sqrt_bits=_serialized_positive_integer(report, "sqrt_bits"),
        )
    if schema == "oig-nominal-null-relevance-v1":
        exhaustive = _serialized_boolean(report, "model_secants_exhaustive")
        return certify_nominal_null_relevance(
            report["response_exact"],
            report["source_metric_exact"],
            query_matrix=report["query_matrix_exact"],
            model_secants=report["model_secants_exact"],
            response_radius=report["response_radius_exact"],
            model_secants_exhaustive=exhaustive,
            model_secants_provenance=report["model_secants_provenance"],
        )
    if schema == "oig-rational-lattice-trichotomy-v1":
        return certify_rational_lattice_trichotomy(
            report["response_exact"],
            report["lattice_basis_exact"],
            report["output_metric_exact"],
            sqrt_bits=_serialized_positive_integer(report, "sqrt_bits"),
        )
    if schema == "oig-lattice-trichotomy-composition-v1":
        lattice_rank = report["lattice_rank"]
        real_rank = report["real_image_rank"]
        if type(lattice_rank) is not int or type(real_rank) is not int:
            raise ValueError("lattice ranks must be JSON integers")
        return classify_lattice_trichotomy_from_exact_predicates(
            lattice_rank=lattice_rank,
            real_image_rank=real_rank,
            integer_kernel_status=report["integer_kernel_status"],
            proof_reference=report["external_exact_proof_reference"],
        )
    if schema == "oig-combined-model-design-v1":
        exhaustive = _serialized_boolean(report, "model_secants_exhaustive")
        return certify_combined_model_design(
            report["response_exact"],
            report["source_metric_exact"],
            report["aggregate_information_exact"],
            report["model_secants_exact"],
            report["tangent_bases_exact"],
            response_radius=report["response_radius_exact"],
            output_metric=report["output_metric_exact"],
            blind_source_radius=report["blind_source_radius_exact"],
            query_matrix=report["query_matrix_exact"],
            model_secants_exhaustive=exhaustive,
            model_secants_provenance=report["model_secants_provenance"],
            sqrt_bits=_serialized_positive_integer(report, "sqrt_bits"),
        )
    raise ValueError(f"unknown robust certificate schema {schema!r}")


def verify_robust_model_report(report: dict[str, object]) -> dict[str, object]:
    """Strictly verify a serialized robust certificate from exact inputs."""
    try:
        rebuilt = _rebuild_robust_model_report(report)
        difference = _strict_report_difference(report, rebuilt)
        if difference is not None:
            raise ValueError(difference)
        return {
            "passed": True,
            "schema_version": report["schema_version"],
            "method": "strict exact-declaration reconstruction with type- and field-complete comparison",
        }
    except Exception as error:
        return {"passed": False, "error": str(error)}


def verify_combined_model_design_report(report: dict[str, object]) -> dict[str, object]:
    """Strict schema-specific verifier for the combined model-design report."""
    if type(report) is not dict or report.get("schema_version") != "oig-combined-model-design-v1":
        return {"passed": False, "error": "expected oig-combined-model-design-v1"}
    return verify_robust_model_report(report)


__all__ = [
    "ExactQuotient",
    "certify_combined_model_design",
    "classify_lattice_trichotomy_from_exact_predicates",
    "certify_finite_quotient_secants",
    "certify_nominal_blind_uncertainty",
    "certify_nominal_null_relevance",
    "certify_quotient_tube_pair",
    "certify_response_tube_pair",
    "certify_rational_lattice_trichotomy",
    "certify_tangent_kernel_angle",
    "exact_model_quotient",
    "quotient_distance_squared",
    "verify_combined_model_design_report",
    "verify_robust_model_report",
]
