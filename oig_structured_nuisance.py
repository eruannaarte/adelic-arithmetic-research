#!/usr/bin/env python3
"""Exact certificates for fixed-response structured additive nuisances.

The finite nuisance body is the rational zonotope

    Z_F = {V x : |x_j| <= d_j}.

For a query response ``q``, an optional additive nuisance subspace
``range(B)``, and an exact positive observation-noise precision ``Omega``,
the certified separation is

    inf_{alpha, z in Z} ||q + B alpha - z||_Omega.

The checker uses the squared primal/dual pair from Arithmetic Observability
VIII--X.  A declared remote support upper extends a finite zonotope dual
witness to a countably generated zonoid.  The response vector, generators,
and nuisance basis are fixed exact rational inputs; response-matrix
uncertainty is deliberately outside this module's scope.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from typing import Sequence

from oig_protocol_design_engine import _inverse, _ldl_positive_definite


Q = Fraction
ExactScalar = int | str | Fraction
QVector = tuple[Fraction, ...]
QMatrix = tuple[tuple[Fraction, ...], ...]
SCHEMA_VERSION = "oig-structured-additive-nuisance-v1"


def _q(value: ExactScalar) -> Fraction:
    if isinstance(value, bool):
        raise TypeError("Boolean values are not exact scalar declarations")
    if isinstance(value, float):
        raise TypeError(
            "binary floating inputs are not exact declarations; use a decimal string or Fraction"
        )
    return Q(value)


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _vector(values: Sequence[ExactScalar], *, name: str) -> QVector:
    result = tuple(_q(value) for value in values)
    if not result:
        raise ValueError(f"{name} must be nonempty")
    return result


def _matrix(
    rows: Sequence[Sequence[ExactScalar]],
    *,
    name: str,
    expected_rows: int | None = None,
    allow_zero_columns: bool = False,
) -> QMatrix:
    result = tuple(tuple(_q(value) for value in row) for row in rows)
    if not result:
        raise ValueError(f"{name} must have at least one row")
    if expected_rows is not None and len(result) != expected_rows:
        raise ValueError(f"{name} has the wrong row count")
    width = len(result[0])
    if width == 0 and not allow_zero_columns:
        raise ValueError(f"{name} must have at least one column")
    if any(len(row) != width for row in result):
        raise ValueError(f"{name} rows have inconsistent lengths")
    return result


def _vector_text(vector: QVector) -> list[str]:
    return [_fraction_text(value) for value in vector]


def _matrix_text(matrix: QMatrix) -> list[list[str]]:
    return [_vector_text(row) for row in matrix]


def _dot(left: QVector, right: QVector) -> Fraction:
    if len(left) != len(right):
        raise ValueError("vector dimensions do not agree")
    return sum((a * b for a, b in zip(left, right)), Q(0))


def _add(left: QVector, right: QVector) -> QVector:
    if len(left) != len(right):
        raise ValueError("vector dimensions do not agree")
    return tuple(a + b for a, b in zip(left, right))


def _subtract(left: QVector, right: QVector) -> QVector:
    if len(left) != len(right):
        raise ValueError("vector dimensions do not agree")
    return tuple(a - b for a, b in zip(left, right))


def _matvec(matrix: QMatrix, vector: QVector) -> QVector:
    if len(matrix[0]) != len(vector):
        raise ValueError("matrix and vector dimensions do not agree")
    return tuple(_dot(row, vector) for row in matrix)


def _identity(dimension: int) -> QMatrix:
    return tuple(
        tuple(Q(int(row == column)) for column in range(dimension))
        for row in range(dimension)
    )


def _symmetric(matrix: QMatrix) -> bool:
    return len(matrix) == len(matrix[0]) and all(
        matrix[row][column] == matrix[column][row]
        for row in range(len(matrix))
        for column in range(row)
    )


def _transpose_matvec(matrix: QMatrix, vector: QVector) -> QVector:
    if len(matrix) != len(vector):
        raise ValueError("matrix and vector dimensions do not agree")
    return tuple(
        sum((matrix[row][column] * vector[row] for row in range(len(matrix))), Q(0))
        for column in range(len(matrix[0]))
    )


def finite_zonotope_support(
    generators: Sequence[Sequence[ExactScalar]],
    coefficient_radii: Sequence[ExactScalar],
    direction: Sequence[ExactScalar],
) -> dict[str, object]:
    """Return the exact support and an attaining coefficient vector.

    ``generators`` is stored by rows: its columns are the zonotope
    generators.  The body is ``{V x: |x_j| <= d_j}``.
    """
    u = _vector(direction, name="direction")
    matrix = _matrix(generators, name="generators", expected_rows=len(u))
    radii = tuple(_q(value) for value in coefficient_radii)
    if len(radii) != len(matrix[0]):
        raise ValueError("one coefficient radius is required per generator")
    if any(value < 0 for value in radii):
        raise ValueError("coefficient radii must be nonnegative")
    pairings = _transpose_matvec(matrix, u)
    maximizing = tuple(
        radius if pairing > 0 else -radius if pairing < 0 else Q(0)
        for radius, pairing in zip(radii, pairings)
    )
    support = sum(
        (radius * abs(pairing) for radius, pairing in zip(radii, pairings)),
        Q(0),
    )
    exposed_point = _matvec(matrix, maximizing)
    if _dot(u, exposed_point) != support:
        raise AssertionError("support witness does not attain its exact value")
    return {
        "finite_support_exact": _fraction_text(support),
        "direction_generator_pairings_exact": _vector_text(pairings),
        "maximizing_coefficients_exact": _vector_text(maximizing),
        "exposed_point_exact": _vector_text(exposed_point),
        "attainment_verified_exactly": True,
    }


def entrywise_box_support_upper(
    generators: Sequence[Sequence[ExactScalar]],
    coefficient_radii: Sequence[ExactScalar],
    direction: Sequence[ExactScalar],
) -> dict[str, object]:
    """Return the coordinate-box relaxation and its exact support.

    This intentionally forgets the shared generator coefficients.  It is a
    valid outer relaxation, useful as a control, but can be strictly larger
    than the correlation-preserving zonotope support.
    """
    u = _vector(direction, name="direction")
    matrix = _matrix(generators, name="generators", expected_rows=len(u))
    radii = tuple(_q(value) for value in coefficient_radii)
    if len(radii) != len(matrix[0]):
        raise ValueError("one coefficient radius is required per generator")
    if any(value < 0 for value in radii):
        raise ValueError("coefficient radii must be nonnegative")
    coordinate_radii = tuple(
        sum(
            (abs(matrix[row][column]) * radii[column] for column in range(len(radii))),
            Q(0),
        )
        for row in range(len(matrix))
    )
    support = sum(
        (abs(value) * radius for value, radius in zip(u, coordinate_radii)),
        Q(0),
    )
    exact = Q(finite_zonotope_support(matrix, radii, u)["finite_support_exact"])
    if support < exact:
        raise AssertionError("an entrywise relaxation cannot reduce support")
    return {
        "coordinate_radii_exact": _vector_text(coordinate_radii),
        "entrywise_box_support_upper_exact": _fraction_text(support),
        "finite_zonotope_support_exact": _fraction_text(exact),
        "correlation_loss_exact": _fraction_text(support - exact),
        "outer_relaxation_verified_exactly": True,
    }


def _effective_tail_support(
    direction: QVector,
    norm_remainder: Fraction | None,
    directional_support: Fraction | None,
) -> tuple[Fraction, Fraction | None, str]:
    # If sum_tail d_k ||v_k|| <= R, then h_tail(u) <= R ||u||_2
    # <= R ||u||_1.  The final expression is rational.
    l1_bound = (
        None
        if norm_remainder is None
        else norm_remainder * sum((abs(value) for value in direction), Q(0))
    )
    if l1_bound is None and directional_support is None:
        return Q(0), None, "finite zonotope; no omitted tail premise"
    if l1_bound is None:
        assert directional_support is not None
        return directional_support, None, "declared direction-specific support bound"
    if directional_support is None:
        return l1_bound, l1_bound, "l1 consequence of the declared norm remainder"
    return (
        min(l1_bound, directional_support),
        l1_bound,
        "minimum of the declared directional and l1 norm-remainder bounds",
    )


def _build_certificate(
    *,
    name: str,
    query_response: Sequence[ExactScalar],
    generators: Sequence[Sequence[ExactScalar]],
    coefficient_radii: Sequence[ExactScalar],
    primal_coefficients: Sequence[ExactScalar],
    dual_direction: Sequence[ExactScalar],
    nuisance_basis: Sequence[Sequence[ExactScalar]] | None,
    primal_nuisance_coefficients: Sequence[ExactScalar] | None,
    observation_precision: Sequence[Sequence[ExactScalar]] | None,
    tail_norm_remainder_upper: ExactScalar | None,
    tail_directional_support_upper: ExactScalar | None,
    tail_provenance: str,
) -> dict[str, object]:
    query = _vector(query_response, name="query response")
    dimension = len(query)
    matrix = _matrix(generators, name="generators", expected_rows=dimension)
    generator_count = len(matrix[0])
    radii = tuple(_q(value) for value in coefficient_radii)
    coefficients = tuple(_q(value) for value in primal_coefficients)
    direction = _vector(dual_direction, name="dual direction")
    if len(direction) != dimension:
        raise ValueError("dual direction has the wrong dimension")
    if len(radii) != generator_count or len(coefficients) != generator_count:
        raise ValueError("generator, radius, and primal coefficient counts differ")
    if any(value < 0 for value in radii):
        raise ValueError("coefficient radii must be nonnegative")
    if any(abs(value) > radius for value, radius in zip(coefficients, radii)):
        raise ValueError("primal zonotope coefficients violate their bounds")

    if observation_precision is None:
        precision = _identity(dimension)
    else:
        precision = _matrix(
            observation_precision,
            name="observation precision",
            expected_rows=dimension,
        )
    if len(precision[0]) != dimension or not _symmetric(precision):
        raise ValueError("observation precision must be square and symmetric")
    if not _ldl_positive_definite(precision):
        raise ValueError("observation precision must be positive definite")
    precision_inverse = _inverse(precision)

    if nuisance_basis is None:
        basis = tuple(tuple() for _ in range(dimension))
    else:
        basis = _matrix(
            nuisance_basis,
            name="nuisance basis",
            expected_rows=dimension,
            allow_zero_columns=True,
        )
    nuisance_dimension = len(basis[0])
    if nuisance_dimension:
        nuisance_gram = tuple(
            tuple(
                sum(
                    (
                        basis[row][left] * basis[row][right]
                        for row in range(dimension)
                    ),
                    Q(0),
                )
                for right in range(nuisance_dimension)
            )
            for left in range(nuisance_dimension)
        )
        if not _ldl_positive_definite(nuisance_gram):
            raise ValueError("nuisance basis columns must be linearly independent")
    if primal_nuisance_coefficients is None:
        nuisance_coefficients = tuple(Q(0) for _ in range(nuisance_dimension))
    else:
        nuisance_coefficients = tuple(
            _q(value) for value in primal_nuisance_coefficients
        )
    if len(nuisance_coefficients) != nuisance_dimension:
        raise ValueError("one primal nuisance coefficient is required per basis column")

    tail_norm = (
        None
        if tail_norm_remainder_upper is None
        else _q(tail_norm_remainder_upper)
    )
    tail_directional = (
        None
        if tail_directional_support_upper is None
        else _q(tail_directional_support_upper)
    )
    if (tail_norm is not None and tail_norm < 0) or (
        tail_directional is not None and tail_directional < 0
    ):
        raise ValueError("tail remainder bounds must be nonnegative")
    has_tail_premise = tail_norm is not None or tail_directional is not None
    if has_tail_premise and not tail_provenance.strip():
        raise ValueError("a declared tail remainder requires provenance")

    orthogonality = _transpose_matvec(basis, direction)
    if any(orthogonality):
        raise ValueError("dual direction is not exactly orthogonal to the nuisance span")

    support_record = finite_zonotope_support(matrix, radii, direction)
    finite_support = Q(support_record["finite_support_exact"])
    effective_tail, l1_tail, tail_method = _effective_tail_support(
        direction, tail_norm, tail_directional
    )

    zonotope_point = _matvec(matrix, coefficients)
    nuisance_point = _matvec(basis, nuisance_coefficients)
    residual = _subtract(_add(query, nuisance_point), zonotope_point)
    primal_squared = _dot(residual, _matvec(precision, residual))
    primal_half_squared = primal_squared / 2
    dual_norm_squared = _dot(direction, _matvec(precision_inverse, direction))
    dual_numerator = _dot(direction, query) - finite_support - effective_tail
    positive_dual_numerator = max(Q(0), dual_numerator)
    norm_dual_distance_squared_lower = (
        Q(0)
        if dual_norm_squared == 0
        else positive_dual_numerator**2 / dual_norm_squared
    )
    dual_raw = (
        dual_numerator - dual_norm_squared / 2
    )
    dual_nonnegative = max(Q(0), dual_raw)
    support_slack = finite_support - _dot(direction, zonotope_point)
    dual_representer = _matvec(precision_inverse, direction)
    residual_mismatch = _subtract(residual, dual_representer)
    residual_mismatch_half_squared = (
        _dot(residual_mismatch, _matvec(precision, residual_mismatch)) / 2
    )
    gap = residual_mismatch_half_squared + support_slack + effective_tail
    if support_slack < 0:
        raise AssertionError("a feasible point exceeded the finite support")
    if primal_half_squared - dual_raw != gap:
        raise AssertionError("the exact primal-dual gap identity failed")
    distance_squared_lower = max(
        norm_dual_distance_squared_lower, 2 * dual_nonnegative
    )

    point_or_quotient = "point-to-zonoid" if nuisance_dimension == 0 else "query-response quotient"
    report = {
        "schema_version": SCHEMA_VERSION,
        "name": str(name),
        "certificate_kind": point_or_quotient,
        "status": "exact rational structured-additive-nuisance certificate",
        "problem": {
            "observation_dimension": dimension,
            "finite_generator_count": generator_count,
            "nuisance_subspace_dimension": nuisance_dimension,
            "query_response_exact": _vector_text(query),
            "finite_generators_by_rows_exact": _matrix_text(matrix),
            "coefficient_radii_exact": _vector_text(radii),
            "nuisance_basis_by_rows_exact": _matrix_text(basis),
            "observation_noise_precision_exact": _matrix_text(precision),
        },
        "witnesses": {
            "primal_zonotope_coefficients_exact": _vector_text(coefficients),
            "primal_nuisance_coefficients_exact": _vector_text(nuisance_coefficients),
            "dual_direction_exact": _vector_text(direction),
        },
        "finite_zonotope_support_certificate": support_record,
        "tail_remainder": {
            "model": "countably generated absolutely summable zonoid tail",
            "declared_norm_remainder_upper_exact": (
                None if tail_norm is None else _fraction_text(tail_norm)
            ),
            "declared_directional_support_upper_exact": (
                None
                if tail_directional is None
                else _fraction_text(tail_directional)
            ),
            "l1_derived_directional_support_upper_exact": (
                None if l1_tail is None else _fraction_text(l1_tail)
            ),
            "effective_directional_support_upper_exact": _fraction_text(effective_tail),
            "effective_bound_method": tail_method,
            "provenance": tail_provenance,
            "external_analytic_assumption": has_tail_premise,
            "required_meaning": (
                "when present, the norm premise bounds sum d_k||v_k||_2; when present, "
                "the directional premise bounds omitted support in the serialized dual direction"
            ),
        },
        "exact_calculation": {
            "primal_zonotope_point_exact": _vector_text(zonotope_point),
            "primal_nuisance_point_exact": _vector_text(nuisance_point),
            "primal_residual_exact": _vector_text(residual),
            "dual_nuisance_orthogonality_exact": _vector_text(orthogonality),
            "dual_precision_representer_exact": _vector_text(dual_representer),
            "finite_support_slack_exact": _fraction_text(support_slack),
            "residual_dual_mismatch_half_squared_exact": _fraction_text(
                residual_mismatch_half_squared
            ),
            "primal_half_squared_upper_exact": _fraction_text(primal_half_squared),
            "dual_linear_separation_numerator_exact": _fraction_text(
                dual_numerator
            ),
            "dual_norm_squared_exact": _fraction_text(dual_norm_squared),
            "norm_dual_distance_squared_lower_exact": _fraction_text(
                norm_dual_distance_squared_lower
            ),
            "dual_half_squared_lower_raw_exact": _fraction_text(dual_raw),
            "dual_half_squared_lower_nonnegative_exact": _fraction_text(
                dual_nonnegative
            ),
            "primal_dual_gap_upper_exact": _fraction_text(gap),
            "distance_squared_lower_exact": _fraction_text(distance_squared_lower),
            "distance_squared_upper_exact": _fraction_text(primal_squared),
            "critical_equal_noise_radius_squared_lower_exact": _fraction_text(
                distance_squared_lower / 4
            ),
            "dual_feasible_exactly": True,
            "primal_feasible_exactly": True,
            "gap_identity_verified_exactly": True,
            "squared_dual_gap_closes_exactly": gap == 0,
            "positive_separation_certified": distance_squared_lower > 0,
            "exact_optimum_certified": distance_squared_lower == primal_squared,
        },
        "interpretation": (
            "The distance is from the fixed query response plus the declared additive nuisance span "
            "to the fixed-response structured nuisance zonoid in the norm induced by the declared noise "
            "precision. Equal norm-bounded noise balls remain "
            "disjoint whenever their squared radius is strictly below the certified critical-radius square."
        ),
        "scope_boundary": (
            "This certificate preserves correlations induced by shared nuisance coefficients. It assumes "
            "the query response, generator matrix, nuisance basis, and noise norm are fixed exactly. It does "
            "not cover uncertainty in any response matrix, generator direction, calibration, or metric. "
            "Nonzero infinite-tail bounds are externally supplied analytic premises whose use, but not truth, "
            "is checked by this finite JSON verifier."
        ),
    }
    return report


def certify_structured_nuisance_separation(
    *,
    name: str,
    query_response: Sequence[ExactScalar],
    generators: Sequence[Sequence[ExactScalar]],
    coefficient_radii: Sequence[ExactScalar],
    primal_coefficients: Sequence[ExactScalar],
    dual_direction: Sequence[ExactScalar],
    nuisance_basis: Sequence[Sequence[ExactScalar]] | None = None,
    primal_nuisance_coefficients: Sequence[ExactScalar] | None = None,
    observation_precision: Sequence[Sequence[ExactScalar]] | None = None,
    tail_norm_remainder_upper: ExactScalar | None = None,
    tail_directional_support_upper: ExactScalar | None = None,
    tail_provenance: str = "finite zonotope; no omitted tail",
) -> dict[str, object]:
    """Build and independently verify a structured nuisance certificate."""
    report = _build_certificate(
        name=name,
        query_response=query_response,
        generators=generators,
        coefficient_radii=coefficient_radii,
        primal_coefficients=primal_coefficients,
        dual_direction=dual_direction,
        nuisance_basis=nuisance_basis,
        primal_nuisance_coefficients=primal_nuisance_coefficients,
        observation_precision=observation_precision,
        tail_norm_remainder_upper=tail_norm_remainder_upper,
        tail_directional_support_upper=tail_directional_support_upper,
        tail_provenance=tail_provenance,
    )
    verification = verify_structured_nuisance_report(report)
    if not verification["passed"]:
        raise AssertionError(f"structured nuisance self-verification failed: {verification}")
    report["independent_verification"] = verification
    return report


def _parse_fraction_text(value: object, *, name: str) -> Fraction:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a canonical fraction string")
    result = Q(value)
    if _fraction_text(result) != value:
        raise ValueError(f"{name} is not canonically encoded")
    return result


def _parse_vector_text(values: object, *, name: str) -> QVector:
    if not isinstance(values, list):
        raise ValueError(f"{name} must be a JSON list")
    return tuple(
        _parse_fraction_text(value, name=f"{name}[{index}]")
        for index, value in enumerate(values)
    )


def _parse_matrix_text(values: object, *, name: str) -> QMatrix:
    if not isinstance(values, list):
        raise ValueError(f"{name} must be a JSON list")
    rows = tuple(
        _parse_vector_text(row, name=f"{name}[{index}]")
        for index, row in enumerate(values)
    )
    if not rows or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError(f"{name} has invalid shape")
    return rows


def _strict_json_equal(left: object, right: object) -> bool:
    """Compare JSON-like objects without identifying booleans with integers."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            _strict_json_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            _strict_json_equal(a, b) for a, b in zip(left, right)
        )
    return left == right


def verify_structured_nuisance_report(report: dict[str, object]) -> dict[str, object]:
    """Reconstruct every finite theorem field from exact serialized inputs."""
    try:
        if report.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unknown structured nuisance schema")
        problem = report["problem"]
        witnesses = report["witnesses"]
        tail = report["tail_remainder"]
        if not isinstance(problem, dict) or not isinstance(witnesses, dict) or not isinstance(tail, dict):
            raise ValueError("malformed structured nuisance blocks")
        dimension = problem["observation_dimension"]
        generator_count = problem["finite_generator_count"]
        nuisance_dimension = problem["nuisance_subspace_dimension"]
        if any(type(value) is not int for value in (dimension, generator_count, nuisance_dimension)):
            raise ValueError("reported dimensions must be JSON integers")

        query = _parse_vector_text(problem["query_response_exact"], name="query response")
        generators = _parse_matrix_text(
            problem["finite_generators_by_rows_exact"], name="generators"
        )
        radii = _parse_vector_text(problem["coefficient_radii_exact"], name="radii")
        basis = _parse_matrix_text(
            problem["nuisance_basis_by_rows_exact"], name="nuisance basis"
        )
        precision = _parse_matrix_text(
            problem["observation_noise_precision_exact"],
            name="observation noise precision",
        )
        coefficients = _parse_vector_text(
            witnesses["primal_zonotope_coefficients_exact"],
            name="primal zonotope coefficients",
        )
        nuisance_coefficients = _parse_vector_text(
            witnesses["primal_nuisance_coefficients_exact"],
            name="primal nuisance coefficients",
        )
        direction = _parse_vector_text(
            witnesses["dual_direction_exact"], name="dual direction"
        )
        norm_text = tail["declared_norm_remainder_upper_exact"]
        tail_norm = (
            None
            if norm_text is None
            else _parse_fraction_text(norm_text, name="tail norm remainder")
        )
        directional_text = tail["declared_directional_support_upper_exact"]
        tail_directional = (
            None
            if directional_text is None
            else _parse_fraction_text(directional_text, name="tail directional support")
        )
        if len(query) != dimension or len(generators) != dimension or len(basis) != dimension:
            raise ValueError("reported observation dimension is inconsistent")
        if len(generators[0]) != generator_count or len(radii) != generator_count:
            raise ValueError("reported generator count is inconsistent")
        if len(basis[0]) != nuisance_dimension:
            raise ValueError("reported nuisance dimension is inconsistent")

        rebuilt = _build_certificate(
            name=str(report["name"]),
            query_response=query,
            generators=generators,
            coefficient_radii=radii,
            primal_coefficients=coefficients,
            dual_direction=direction,
            nuisance_basis=basis,
            primal_nuisance_coefficients=nuisance_coefficients,
            observation_precision=precision,
            tail_norm_remainder_upper=tail_norm,
            tail_directional_support_upper=tail_directional,
            tail_provenance=str(tail["provenance"]),
        )
        submitted = {
            key: value for key, value in report.items() if key != "independent_verification"
        }
        if not _strict_json_equal(submitted, rebuilt):
            differing = sorted(
                key
                for key in set(submitted) | set(rebuilt)
                if not _strict_json_equal(submitted.get(key), rebuilt.get(key))
            )
            raise ValueError(
                "structured nuisance report does not reproduce; differing top-level fields: "
                + ", ".join(differing)
            )
        verification = {
            "passed": True,
            "method": "independent exact-rational reconstruction of support, feasibility, bounds, and gap",
            "distance_squared_lower_exact": rebuilt["exact_calculation"][
                "distance_squared_lower_exact"
            ],
            "distance_squared_upper_exact": rebuilt["exact_calculation"][
                "distance_squared_upper_exact"
            ],
        }
        embedded = report.get("independent_verification")
        if embedded is not None and not _strict_json_equal(embedded, verification):
            raise ValueError("embedded independent verification block is inconsistent")
        return verification
    except Exception as error:
        return {"passed": False, "error": str(error)}


def _demo_payload() -> dict[str, object]:
    """Build the deterministic demonstration payload without its outer check."""
    point = certify_structured_nuisance_separation(
        name="point versus rectangle zonotope",
        query_response=[3, 1],
        generators=[[1, 0], [0, 1]],
        coefficient_radii=[1, "1/2"],
        primal_coefficients=[1, "1/2"],
        dual_direction=[2, "1/2"],
    )
    quotient = certify_structured_nuisance_separation(
        name="query response after profiling one additive nuisance direction",
        query_response=[3, 2],
        generators=[[0], [1]],
        coefficient_radii=[1],
        primal_coefficients=[1],
        dual_direction=[0, 1],
        nuisance_basis=[[1], [0]],
        primal_nuisance_coefficients=[-3],
    )
    tail = certify_structured_nuisance_separation(
        name="finite prefix with a declared countable-tail support remainder",
        query_response=[3, 1],
        generators=[[1], [0]],
        coefficient_radii=[1],
        primal_coefficients=[1],
        dual_direction=[1, 0],
        tail_norm_remainder_upper="1/10",
        tail_directional_support_upper="1/20",
        tail_provenance="demo premise: omitted support in direction (1,0) is at most 1/20",
    )
    correlation = entrywise_box_support_upper(
        [[1], [1]], [1], [1, -1]
    )
    return {
        "schema_version": "oig-structured-additive-nuisance-demo-v1",
        "point_certificate": point,
        "query_response_certificate": quotient,
        "countable_tail_interface_certificate": tail,
        "correlation_control": correlation,
    }


def verify_structured_nuisance_demo_report(
    report: dict[str, object],
) -> dict[str, object]:
    """Verify the pinned multi-certificate demonstration JSON."""
    try:
        if report.get("schema_version") != "oig-structured-additive-nuisance-demo-v1":
            raise ValueError("unknown structured nuisance demo schema")
        for field in (
            "point_certificate",
            "query_response_certificate",
            "countable_tail_interface_certificate",
        ):
            certificate = report.get(field)
            if not isinstance(certificate, dict):
                raise ValueError(f"missing demo certificate {field}")
            verification = verify_structured_nuisance_report(certificate)
            if not verification["passed"]:
                raise ValueError(f"demo certificate {field} fails: {verification}")
        rebuilt = _demo_payload()
        submitted = {
            key: value for key, value in report.items() if key != "independent_verification"
        }
        if not _strict_json_equal(submitted, rebuilt):
            raise ValueError("pinned structured nuisance demo does not reproduce")
        verification = {
            "passed": True,
            "method": "independent reconstruction of all three certificates and the correlation control",
        }
        embedded = report.get("independent_verification")
        if embedded is not None and not _strict_json_equal(embedded, verification):
            raise ValueError("embedded demo verification block is inconsistent")
        return verification
    except Exception as error:
        return {"passed": False, "error": str(error)}


def demo_certificates() -> dict[str, object]:
    """Return self-verifying point, quotient, tail, and correlation controls."""
    report = _demo_payload()
    verification = verify_structured_nuisance_demo_report(report)
    if not verification["passed"]:
        raise AssertionError(f"structured nuisance demo verification failed: {verification}")
    report["independent_verification"] = verification
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output")
    parser.add_argument("--verify")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.verify:
        with open(args.verify, "r", encoding="utf-8") as handle:
            submitted = json.load(handle)
        verification = verify_structured_nuisance_demo_report(submitted)
        print(json.dumps(verification, indent=2, sort_keys=True))
        return 0 if verification["passed"] else 1
    report = demo_certificates()
    payload = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.write("\n")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "SCHEMA_VERSION",
    "certify_structured_nuisance_separation",
    "demo_certificates",
    "entrywise_box_support_upper",
    "finite_zonotope_support",
    "verify_structured_nuisance_demo_report",
    "verify_structured_nuisance_report",
]
