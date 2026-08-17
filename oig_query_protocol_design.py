"""Exact query-directed certificates with a shared linear nuisance.

The finite real model is

    y = H x + B z + eta,

with exact rational source, data, and query metrics.  The nuisance is removed
by an exact metric-orthogonal projector.  Query identifiability and the
factorization of ``L`` through the profiled response are decided by rational
linear algebra.  Floating generalized eigensolvers only propose a sharp
rational bracket for the minimax amplification; exact LDL and an exact
Rayleigh witness make the theorem decisions.

The protocol-mixture entry point treats one nuisance vector as shared across
all active protocols.  It certifies a declared rational mixture; it does not
claim that profiling commutes with mixing or that the mixture is optimal.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Sequence

import numpy as np
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


_QUERY_INTERPRETATION = (
    "For data-noise radius epsilon, the exact minimax query error is "
    "kappa*epsilon; the true kappa squared lies in the certified rational interval."
)


def _proof_boundary(model_kind: str) -> str:
    nuisance_scope = {
        "single_experiment": "the declared unrestricted linear nuisance",
        "shared_nuisance_protocol_mixture": (
            "one declared unrestricted nuisance shared across the active protocols"
        ),
        "independent_nuisance_protocol_mixture": (
            "one declared unrestricted nuisance independently re-fit in each active protocol"
        ),
    }.get(model_kind)
    if nuisance_scope is None:
        raise ValueError("unknown query model kind")
    return (
        "This certificate proves a finite-dimensional real rational linear theorem for "
        f"the declared metrics, response, query, and {nuisance_scope}. It does not prove "
        "that an external physical or continuum model is enclosed by these data."
    )


def _zero(matrix: QMatrix) -> bool:
    return all(value == 0 for row in matrix for value in row)


def _matrix_vector(matrix: QMatrix, vector: Sequence[Fraction]) -> tuple[Fraction, ...]:
    if _shape(matrix)[1] != len(vector):
        raise ValueError("matrix and vector dimensions do not agree")
    return tuple(
        sum((value * coordinate for value, coordinate in zip(row, vector)), Q(0))
        for row in matrix
    )


def _vector_text(vector: Sequence[Fraction]) -> list[str]:
    return [_fraction_text(value) for value in vector]


def _strict_json_equal(left: object, right: object) -> bool:
    """Compare JSON-like data without identifying booleans with integers."""
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


def _descriptive_sqrt(value: Fraction) -> float | None:
    """Return a finite display-only square root, or ``None`` on overflow."""
    try:
        result = math.sqrt(float(value))
    except (OverflowError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _block_diagonal(blocks: Sequence[QMatrix]) -> QMatrix:
    if not blocks:
        raise ValueError("at least one block is required")
    sizes = []
    for block in blocks:
        rows, columns = _shape(block)
        if rows != columns:
            raise ValueError("diagonal blocks must be square")
        sizes.append(rows)
    total = sum(sizes)
    result = [[Q(0) for _ in range(total)] for _ in range(total)]
    offset = 0
    for block, size in zip(blocks, sizes):
        for row in range(size):
            for column in range(size):
                result[offset + row][offset + column] = block[row][column]
        offset += size
    return tuple(tuple(row) for row in result)


def _column_basis(matrix: QMatrix) -> QMatrix | None:
    """Return a deterministic exact basis for the column space."""
    rows, _ = _shape(matrix)
    basis_rows = _row_basis(_transpose(matrix), rows)
    return _transpose(basis_rows) if basis_rows else None


def _nullspace_basis(matrix: QMatrix) -> tuple[tuple[Fraction, ...], ...]:
    """Exact rational nullspace basis, one vector for each free column."""
    rows, columns = _shape(matrix)
    work = [list(row) for row in matrix]
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]), None
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [value / divisor for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    value - factor * reference
                    for value, reference in zip(work[row], work[pivot_row])
                ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == rows:
            break

    free_columns = [column for column in range(columns) if column not in pivot_columns]
    basis = []
    for free in free_columns:
        vector = [Q(0) for _ in range(columns)]
        vector[free] = Q(1)
        for row, pivot in enumerate(pivot_columns):
            vector[pivot] = -work[row][free]
        basis.append(tuple(vector))
    return tuple(basis)


def _profile_nuisance(
    observation: QMatrix,
    nuisance: QMatrix | None,
    output_metric: QMatrix,
) -> tuple[QMatrix | None, QMatrix, QMatrix, QMatrix]:
    """Return basis, exact W-projector, effective response, and profile Gram."""
    output_dimension, _ = _shape(observation)
    if nuisance is None:
        basis = None
        projector = _identity(output_dimension)
    else:
        if _shape(nuisance)[0] != output_dimension:
            raise ValueError("nuisance response has the wrong output dimension")
        basis = _column_basis(nuisance)
        if basis is None:
            projector = _identity(output_dimension)
        else:
            moment = _matmul(
                _transpose(basis), _matmul(output_metric, basis)
            )
            projector = _subtract(
                _identity(output_dimension),
                _matmul(
                    basis,
                    _matmul(
                        _inverse(moment),
                        _matmul(_transpose(basis), output_metric),
                    ),
                ),
            )
    effective = _matmul(projector, observation)
    information = _matmul(
        _transpose(effective), _matmul(output_metric, effective)
    )
    return basis, projector, effective, information


def _strict_generalized_upper(numerator: QMatrix, denominator: QMatrix) -> Fraction:
    """Find exact ``upper`` with ``numerator < upper*denominator``."""
    if _zero(numerator):
        return Q(0)
    # Every generalized eigenvalue is an eigenvalue of denominator^-1*numerator.
    # Its spectral radius is bounded by the exact maximum absolute row sum.
    # Adding one makes the bound strict and avoids any dependence on a
    # floating eigensolver, including for rationals outside binary64 range.
    transformed = _matmul(_inverse(denominator), numerator)
    row_bound = max(
        sum((abs(value) for value in row), Q(0)) for row in transformed
    )
    upper = row_bound + 1
    if not _ldl_positive_definite(
        _subtract(_scale(denominator, upper), numerator)
    ):
        raise ArithmeticError("exact row-sum upper failed its LDL verification")

    # Tighten the portable exact bound without reintroducing a float
    # dependency.  The final dyadic endpoint remains an outward upper bound
    # because only endpoints whose shifted form is exactly positive definite
    # are accepted as ``upper``.
    lower = Q(0)
    for _ in range(96):
        midpoint = (lower + upper) / 2
        if midpoint > 0 and _ldl_positive_definite(
            _subtract(_scale(denominator, midpoint), numerator)
        ):
            upper = midpoint
        else:
            lower = midpoint
    return upper


def _rayleigh_lower_witness(
    numerator: QMatrix, denominator: QMatrix, vector_scale: int
) -> tuple[Fraction, tuple[Fraction, ...]]:
    if type(vector_scale) is not int or vector_scale < 1:
        raise ValueError("vector scale must be a positive integer")
    integers: tuple[Fraction, ...] | None = None
    try:
        _, vectors = eigh(
            _float_matrix(numerator), _float_matrix(denominator), check_finite=True
        )
        vector = np.asarray(vectors[:, -1], dtype=float)
        largest = float(np.max(np.abs(vector)))
        if math.isfinite(largest) and largest > 0:
            proposed = tuple(
                Q(int(round(value / largest * vector_scale))) for value in vector
            )
            if any(proposed):
                integers = proposed
    except (ArithmeticError, OverflowError, ValueError):
        integers = None
    if integers is None:
        # Exact coordinate fallback.  It may be loose but always supplies a
        # valid nonzero Rayleigh witness because the denominator is positive
        # definite and the nonzero PSD numerator has a positive diagonal.
        dimension = len(numerator)
        index = max(
            range(dimension),
            key=lambda item: numerator[item][item] / denominator[item][item],
        )
        integers = tuple(Q(int(item == index)) for item in range(dimension))
    if not any(integers):
        raise ArithmeticError("rationalized amplification witness vanished")
    numerator_value = _matrix_vector(numerator, integers)
    denominator_value = _matrix_vector(denominator, integers)
    rayleigh_numerator = sum(
        (left * right for left, right in zip(integers, numerator_value)), Q(0)
    )
    rayleigh_denominator = sum(
        (left * right for left, right in zip(integers, denominator_value)), Q(0)
    )
    if rayleigh_denominator <= 0:
        raise ArithmeticError("amplification witness has nonpositive data energy")
    return rayleigh_numerator / rayleigh_denominator, integers


def _parse_nuisance(
    rows: object, output_dimension: int, declared_dimension: int
) -> QMatrix | None:
    if declared_dimension == 0:
        if rows is not None:
            raise ValueError("zero-dimensional nuisance must be serialized as null")
        return None
    matrix = rational_matrix(rows)  # type: ignore[arg-type]
    if _shape(matrix) != (output_dimension, declared_dimension):
        raise ValueError("serialized nuisance dimensions are inconsistent")
    return matrix


def _validate_model(
    observation: QMatrix,
    nuisance: QMatrix | None,
    source_metric: QMatrix,
    output_metric: QMatrix,
    query: QMatrix,
    query_metric: QMatrix,
) -> tuple[int, int, int, int]:
    output_dimension, source_dimension = _shape(observation)
    query_dimension, query_source_dimension = _shape(query)
    if query_source_dimension != source_dimension:
        raise ValueError("query and observation source dimensions differ")
    if _shape(source_metric) != (source_dimension, source_dimension):
        raise ValueError("source metric has the wrong dimension")
    if _shape(output_metric) != (output_dimension, output_dimension):
        raise ValueError("output metric has the wrong dimension")
    if _shape(query_metric) != (query_dimension, query_dimension):
        raise ValueError("query metric has the wrong dimension")
    if not _ldl_positive_definite(source_metric):
        raise ValueError("source metric must be symmetric positive definite")
    if not _ldl_positive_definite(output_metric):
        raise ValueError("output metric must be symmetric positive definite")
    if not _ldl_positive_definite(query_metric):
        raise ValueError("query metric must be symmetric positive definite")
    nuisance_dimension = 0
    if nuisance is not None:
        if _shape(nuisance)[0] != output_dimension:
            raise ValueError("nuisance response has the wrong output dimension")
        nuisance_dimension = _shape(nuisance)[1]
    return source_dimension, output_dimension, query_dimension, nuisance_dimension


def _build_query_report(
    observation: QMatrix,
    nuisance: QMatrix | None,
    source_metric: QMatrix,
    output_metric: QMatrix,
    query: QMatrix,
    query_metric: QMatrix,
    *,
    model_kind: str,
    vector_scale: int,
    protocol_mixture: dict[str, object] | None = None,
) -> dict[str, object]:
    dimensions = _validate_model(
        observation, nuisance, source_metric, output_metric, query, query_metric
    )
    source_dimension, output_dimension, query_dimension, nuisance_dimension = dimensions
    basis, projector, effective, profile_information = _profile_nuisance(
        observation, nuisance, output_metric
    )
    nuisance_rank = 0 if basis is None else _shape(basis)[1]
    coordinates = _row_basis(effective, source_dimension)
    effective_rank = len(coordinates)
    nullspace = _nullspace_basis(effective)
    counterexample = next(
        (vector for vector in nullspace if any(_matrix_vector(query, vector))),
        None,
    )
    identifiable = counterexample is None

    report: dict[str, object] = {
        "schema_version": "oig-query-protocol-certificate-v1",
        "status": "exact finite-linear query certificate",
        "model_kind": model_kind,
        "source_dimension": source_dimension,
        "output_dimension": output_dimension,
        "query_dimension": query_dimension,
        "declared_nuisance_dimension": nuisance_dimension,
        "nuisance_rank": nuisance_rank,
        "effective_response_rank": effective_rank,
        "declared_observation_exact": _matrix_text(observation),
        "declared_nuisance_response_exact": (
            None if nuisance is None else _matrix_text(nuisance)
        ),
        "declared_source_metric_exact": _matrix_text(source_metric),
        "declared_output_metric_exact": _matrix_text(output_metric),
        "declared_query_exact": _matrix_text(query),
        "declared_query_metric_exact": _matrix_text(query_metric),
        "nuisance_elimination": {
            "nuisance_basis_exact": None if basis is None else _matrix_text(basis),
            "metric_orthogonal_projector_exact": _matrix_text(projector),
            "effective_response_exact": _matrix_text(effective),
            "profiled_information_exact": _matrix_text(profile_information),
            "projector_idempotent_exact": _matmul(projector, projector) == projector,
            "projector_is_output_metric_self_adjoint_exact": (
                _matmul(_transpose(projector), output_metric)
                == _matmul(output_metric, projector)
            ),
            "projector_annihilates_nuisance_exact": (
                nuisance is None or _zero(_matmul(projector, nuisance))
            ),
        },
        "identifiability": {
            "query_identifiable_exact": identifiable,
            "kernel_condition_exact": identifiable,
            "kernel_counterexample_exact": (
                None if counterexample is None else _vector_text(counterexample)
            ),
        },
        "proof_boundary": _proof_boundary(model_kind),
        "report_valid": True,
    }
    if protocol_mixture is not None:
        report["protocol_mixture"] = protocol_mixture

    if not identifiable:
        report["factorization_and_minimax"] = {
            "kind": "unidentifiable-unbounded-source",
            "factorization_exists": False,
            "zero_noise_minimax_error": "infinite",
            "reason": "ker(effective_response) is not contained in ker(query)",
        }
    elif effective_rank == 0:
        decoder = _zeros(query_dimension, output_dimension)
        if not _zero(query):
            raise AssertionError("zero effective response cannot identify a nonzero query")
        report["factorization_and_minimax"] = {
            "kind": "identifiable-zero-query",
            "factorization_exists": True,
            "decoder_exact": _matrix_text(decoder),
            "decoder_times_effective_response_equals_query_exact": True,
            "decoder_annihilates_nuisance_exact": True,
            "minimax_amplification_squared_lower_exact": "0/1",
            "minimax_amplification_squared_upper_exact": "0/1",
            "minimax_amplification_exactly_zero": True,
        }
    else:
        coordinate_matrix = tuple(coordinates)
        source_inverse = _inverse(source_metric)
        moment = _matmul(
            coordinate_matrix,
            _matmul(source_inverse, _transpose(coordinate_matrix)),
        )
        quotient_source_metric = _inverse(moment)
        injection = _matmul(
            source_inverse,
            _matmul(_transpose(coordinate_matrix), quotient_source_metric),
        )
        if _matmul(coordinate_matrix, injection) != _identity(effective_rank):
            raise AssertionError("source quotient injection is not a right inverse")
        reduced_response = _matmul(effective, injection)
        reduced_query = _matmul(query, injection)
        data_gram = _matmul(
            _transpose(reduced_response),
            _matmul(output_metric, reduced_response),
        )
        query_form = _matmul(
            _transpose(reduced_query), _matmul(query_metric, reduced_query)
        )
        if not _ldl_positive_definite(data_gram):
            raise AssertionError("effective quotient data Gram is not positive definite")
        decoder = _matmul(
            reduced_query,
            _matmul(
                _inverse(data_gram),
                _matmul(_transpose(reduced_response), output_metric),
            ),
        )
        if _matmul(decoder, effective) != query:
            raise AssertionError("exact query factorization failed")
        if _matmul(decoder, observation) != query:
            raise AssertionError("raw-observation decoder does not reproduce the query")
        if nuisance is not None and not _zero(_matmul(decoder, nuisance)):
            raise AssertionError("query decoder does not annihilate the nuisance")

        if _zero(query_form):
            lower = upper = Q(0)
            witness: tuple[Fraction, ...] | None = None
            exact_zero = True
        else:
            lower, witness = _rayleigh_lower_witness(
                query_form, data_gram, vector_scale
            )
            upper = _strict_generalized_upper(query_form, data_gram)
            if lower > upper:
                raise AssertionError("amplification lower bound exceeds its upper bound")
            exact_zero = False
        report["factorization_and_minimax"] = {
            "kind": "identifiable-query-factorization",
            "factorization_exists": True,
            "quotient_row_coordinates_exact": _matrix_text(coordinate_matrix),
            "quotient_injection_exact": _matrix_text(injection),
            "quotient_source_metric_exact": _matrix_text(quotient_source_metric),
            "reduced_effective_response_exact": _matrix_text(reduced_response),
            "reduced_query_exact": _matrix_text(reduced_query),
            "reduced_data_gram_exact": _matrix_text(data_gram),
            "reduced_query_form_exact": _matrix_text(query_form),
            "decoder_exact": _matrix_text(decoder),
            "decoder_times_effective_response_equals_query_exact": True,
            "decoder_times_raw_observation_equals_query_exact": True,
            "decoder_annihilates_nuisance_exact": True,
            "amplification_lower_witness_exact": (
                None if witness is None else _vector_text(witness)
            ),
            "minimax_amplification_squared_lower_exact": _fraction_text(lower),
            "minimax_amplification_squared_upper_exact": _fraction_text(upper),
            "upper_shift_positive_by_exact_ldl": (upper > 0),
            "minimax_amplification_exactly_zero": exact_zero,
            "interpretation": _QUERY_INTERPRETATION,
            "descriptive_amplification_lower": _descriptive_sqrt(lower),
            "descriptive_amplification_upper": _descriptive_sqrt(upper),
        }

    verification = _verify_query_protocol_report(report, require_embedded=False)
    if not verification["passed"]:
        raise AssertionError(f"query-certificate self-verification failed: {verification}")
    report["independent_exact_verification"] = verification
    sealed = verify_query_protocol_report(report)
    if not sealed["passed"]:
        raise AssertionError(f"sealed query-certificate verification failed: {sealed}")
    return report


def certify_query_model(
    observation: Sequence[Sequence[ExactScalar]],
    nuisance_response: Sequence[Sequence[ExactScalar]] | None,
    source_metric: Sequence[Sequence[ExactScalar]],
    output_metric: Sequence[Sequence[ExactScalar]],
    query: Sequence[Sequence[ExactScalar]],
    query_metric: Sequence[Sequence[ExactScalar]],
    *,
    amplification_vector_scale: int = 10**8,
) -> dict[str, object]:
    """Certify one exact finite query problem with an unrestricted nuisance."""
    h = rational_matrix(observation)
    nuisance = None if nuisance_response is None else rational_matrix(nuisance_response)
    return _build_query_report(
        h,
        nuisance,
        rational_matrix(source_metric),
        rational_matrix(output_metric),
        rational_matrix(query),
        rational_matrix(query_metric),
        model_kind="single_experiment",
        vector_scale=amplification_vector_scale,
    )


@dataclass(frozen=True)
class QueryProtocol:
    """One exact protocol participating in a shared-nuisance mixture."""

    name: str
    response: QMatrix
    nuisance_response: QMatrix | None
    output_metric: QMatrix
    cost: Fraction = Q(1)

    @classmethod
    def from_rows(
        cls,
        name: str,
        response: Sequence[Sequence[ExactScalar]],
        nuisance_response: Sequence[Sequence[ExactScalar]] | None,
        output_metric: Sequence[Sequence[ExactScalar]],
        cost: ExactScalar = 1,
    ) -> "QueryProtocol":
        return cls(
            str(name),
            rational_matrix(response),
            None if nuisance_response is None else rational_matrix(nuisance_response),
            rational_matrix(output_metric),
            _q(cost),
        )


def _validate_query_protocol(protocol: QueryProtocol) -> tuple[int, int, int]:
    outputs, sources = _shape(protocol.response)
    if _shape(protocol.output_metric) != (outputs, outputs):
        raise ValueError("protocol output metric has the wrong dimension")
    if not _ldl_positive_definite(protocol.output_metric):
        raise ValueError("protocol output metric must be symmetric positive definite")
    if protocol.cost <= 0:
        raise ValueError("protocol cost must be positive")
    nuisance_dimension = 0
    if protocol.nuisance_response is not None:
        if _shape(protocol.nuisance_response)[0] != outputs:
            raise ValueError("protocol nuisance response has the wrong output dimension")
        nuisance_dimension = _shape(protocol.nuisance_response)[1]
    return outputs, sources, nuisance_dimension


def _assemble_protocol_mixture(
    protocols: Sequence[QueryProtocol], budget_shares: Sequence[Fraction]
) -> tuple[QMatrix, QMatrix | None, QMatrix, QMatrix, tuple[Fraction, ...], tuple[int, ...]]:
    if not protocols:
        raise ValueError("at least one query protocol is required")
    if len(protocols) != len(budget_shares):
        raise ValueError("protocol and budget-share counts differ")
    if any(share < 0 for share in budget_shares):
        raise ValueError("budget shares must be nonnegative")
    if sum(budget_shares, Q(0)) != 1:
        raise ValueError("budget shares must sum exactly to one")
    declared = tuple(_validate_query_protocol(protocol) for protocol in protocols)
    source_dimension = declared[0][1]
    nuisance_dimension = declared[0][2]
    if any(item[1] != source_dimension for item in declared):
        raise ValueError("protocol source dimensions differ")
    if any(item[2] != nuisance_dimension for item in declared):
        raise ValueError("shared nuisance dimensions differ")
    physical = tuple(
        share / protocol.cost for protocol, share in zip(protocols, budget_shares)
    )
    active = tuple(index for index, weight in enumerate(physical) if weight > 0)
    if not active:
        raise ValueError("the protocol mixture has no active protocol")

    observation_rows = tuple(
        row for index in active for row in protocols[index].response
    )
    observation = tuple(tuple(row) for row in observation_rows)
    if nuisance_dimension:
        nuisance_rows = tuple(
            row
            for index in active
            for row in protocols[index].nuisance_response  # type: ignore[union-attr]
        )
        nuisance: QMatrix | None = tuple(tuple(row) for row in nuisance_rows)
    else:
        nuisance = None
    weighted_metrics = tuple(
        _scale(protocols[index].output_metric, physical[index]) for index in active
    )
    output_metric = _block_diagonal(weighted_metrics)

    unprofiled = _zeros(source_dimension, source_dimension)
    for protocol, weight in zip(protocols, physical):
        information = _matmul(
            _transpose(protocol.response),
            _matmul(protocol.output_metric, protocol.response),
        )
        unprofiled = _add(unprofiled, _scale(information, weight))
    return observation, nuisance, output_metric, unprofiled, physical, active


def _assemble_independent_nuisance_mixture(
    protocols: Sequence[QueryProtocol], budget_shares: Sequence[Fraction]
) -> tuple[
    QMatrix,
    QMatrix | None,
    QMatrix,
    QMatrix,
    QMatrix,
    tuple[Fraction, ...],
    tuple[int, ...],
]:
    """Assemble a mixture whose nuisance is independently re-fit per protocol."""
    if not protocols:
        raise ValueError("at least one query protocol is required")
    if len(protocols) != len(budget_shares):
        raise ValueError("protocol and budget-share counts differ")
    if any(share < 0 for share in budget_shares):
        raise ValueError("budget shares must be nonnegative")
    if sum(budget_shares, Q(0)) != 1:
        raise ValueError("budget shares must sum exactly to one")
    declared = tuple(_validate_query_protocol(protocol) for protocol in protocols)
    source_dimension = declared[0][1]
    if any(item[1] != source_dimension for item in declared):
        raise ValueError("protocol source dimensions differ")
    physical = tuple(
        share / protocol.cost for protocol, share in zip(protocols, budget_shares)
    )
    active = tuple(index for index, weight in enumerate(physical) if weight > 0)
    if not active:
        raise ValueError("the protocol mixture has no active protocol")

    observation = tuple(
        tuple(row)
        for index in active
        for row in protocols[index].response
    )
    output_sizes = tuple(declared[index][0] for index in active)
    nuisance_sizes = tuple(declared[index][2] for index in active)
    total_outputs = sum(output_sizes)
    total_nuisance = sum(nuisance_sizes)
    if total_nuisance:
        nuisance_work = [
            [Q(0) for _ in range(total_nuisance)] for _ in range(total_outputs)
        ]
        output_offset = 0
        nuisance_offset = 0
        for index, output_size, nuisance_size in zip(
            active, output_sizes, nuisance_sizes
        ):
            local = protocols[index].nuisance_response
            if nuisance_size and local is None:
                raise AssertionError("declared nuisance dimension lost its matrix")
            for row in range(output_size):
                for column in range(nuisance_size):
                    nuisance_work[output_offset + row][nuisance_offset + column] = (  # type: ignore[index]
                        local[row][column]  # type: ignore[index]
                    )
            output_offset += output_size
            nuisance_offset += nuisance_size
        nuisance: QMatrix | None = tuple(tuple(row) for row in nuisance_work)
    else:
        nuisance = None
    output_metric = _block_diagonal(
        tuple(
            _scale(protocols[index].output_metric, physical[index])
            for index in active
        )
    )

    unprofiled = _zeros(source_dimension, source_dimension)
    individually_profiled = _zeros(source_dimension, source_dimension)
    for protocol, weight in zip(protocols, physical):
        information = _matmul(
            _transpose(protocol.response),
            _matmul(protocol.output_metric, protocol.response),
        )
        unprofiled = _add(unprofiled, _scale(information, weight))
        _, _, _, profiled = _profile_nuisance(
            protocol.response, protocol.nuisance_response, protocol.output_metric
        )
        individually_profiled = _add(
            individually_profiled, _scale(profiled, weight)
        )
    _, _, _, assembled_profiled = _profile_nuisance(
        observation, nuisance, output_metric
    )
    if assembled_profiled != individually_profiled:
        raise AssertionError(
            "independent-nuisance block assembly did not reproduce the linear profile sum"
        )
    return (
        observation,
        nuisance,
        output_metric,
        unprofiled,
        individually_profiled,
        physical,
        active,
    )


def certify_query_protocol_mixture(
    protocols: Sequence[QueryProtocol],
    budget_shares: Sequence[ExactScalar],
    source_metric: Sequence[Sequence[ExactScalar]],
    query: Sequence[Sequence[ExactScalar]],
    query_metric: Sequence[Sequence[ExactScalar]],
    *,
    amplification_vector_scale: int = 10**8,
) -> dict[str, object]:
    """Certify a rational mixture with one nuisance vector shared by all protocols.

    A budget share ``p_i`` and cost ``c_i`` give physical weight ``p_i/c_i``.
    The active protocol outputs are stacked and their output metrics are scaled
    by these physical weights before the *common* nuisance is profiled.
    """
    exact_shares = tuple(_q(value) for value in budget_shares)
    observation, nuisance, output_metric, unprofiled, physical, active = (
        _assemble_protocol_mixture(protocols, exact_shares)
    )
    mixture: dict[str, object] = {
        "schema_version": "oig-query-shared-nuisance-mixture-v1",
        "nuisance_semantics": "one shared nuisance vector across every active protocol",
        "composition_rule": (
            "stack active responses and nuisance maps; scale each output metric by "
            "budget_share/cost; profile the shared nuisance only after assembly"
        ),
        "protocols": [
            {
                "name": protocol.name,
                "response_exact": _matrix_text(protocol.response),
                "nuisance_response_exact": (
                    None
                    if protocol.nuisance_response is None
                    else _matrix_text(protocol.nuisance_response)
                ),
                "output_metric_exact": _matrix_text(protocol.output_metric),
                "cost_exact": _fraction_text(protocol.cost),
                "budget_share_exact": _fraction_text(share),
                "physical_weight_exact": _fraction_text(weight),
            }
            for protocol, share, weight in zip(protocols, exact_shares, physical)
        ],
        "active_protocol_indices": list(active),
        "inactive_zero_share_protocols_omitted_from_assembly": True,
        "unprofiled_information_sum_exact": _matrix_text(unprofiled),
        "warning": (
            "With a shared nuisance, profiling generally does not commute with summing "
            "individually profiled protocol information forms."
        ),
    }
    return _build_query_report(
        observation,
        nuisance,
        rational_matrix(source_metric),
        output_metric,
        rational_matrix(query),
        rational_matrix(query_metric),
        model_kind="shared_nuisance_protocol_mixture",
        vector_scale=amplification_vector_scale,
        protocol_mixture=mixture,
    )


def certify_query_independent_nuisance_mixture(
    protocols: Sequence[QueryProtocol],
    budget_shares: Sequence[ExactScalar],
    source_metric: Sequence[Sequence[ExactScalar]],
    query: Sequence[Sequence[ExactScalar]],
    query_metric: Sequence[Sequence[ExactScalar]],
    *,
    amplification_vector_scale: int = 10**8,
) -> dict[str, object]:
    """Certify a mixture whose nuisance is re-fit independently per protocol.

    In this model the assembled nuisance response is block diagonal.  Exact
    profiling therefore commutes with the cost-weighted protocol sum, so the
    resulting information forms are compatible with ordinary linear E-design.
    """
    exact_shares = tuple(_q(value) for value in budget_shares)
    assembled = _assemble_independent_nuisance_mixture(protocols, exact_shares)
    (
        observation,
        nuisance,
        output_metric,
        unprofiled,
        individually_profiled,
        physical,
        active,
    ) = assembled
    mixture: dict[str, object] = {
        "schema_version": "oig-query-independent-nuisance-mixture-v1",
        "nuisance_semantics": "one independently re-fit nuisance vector per active protocol",
        "composition_rule": (
            "stack active responses; block-diagonalize active nuisance maps; scale each "
            "output metric by budget_share/cost; exact profiled information then adds linearly"
        ),
        "protocols": [
            {
                "name": protocol.name,
                "response_exact": _matrix_text(protocol.response),
                "nuisance_response_exact": (
                    None
                    if protocol.nuisance_response is None
                    else _matrix_text(protocol.nuisance_response)
                ),
                "output_metric_exact": _matrix_text(protocol.output_metric),
                "cost_exact": _fraction_text(protocol.cost),
                "budget_share_exact": _fraction_text(share),
                "physical_weight_exact": _fraction_text(weight),
            }
            for protocol, share, weight in zip(protocols, exact_shares, physical)
        ],
        "active_protocol_indices": list(active),
        "inactive_zero_share_protocols_omitted_from_assembly": True,
        "unprofiled_information_sum_exact": _matrix_text(unprofiled),
        "individually_profiled_information_sum_exact": _matrix_text(
            individually_profiled
        ),
        "profiled_information_adds_linearly_exact": True,
        "e_design_compatibility": (
            "For this independent-refit nuisance model, the candidate profiled information "
            "forms enter linearly with physical weights budget_share/cost."
        ),
    }
    return _build_query_report(
        observation,
        nuisance,
        rational_matrix(source_metric),
        output_metric,
        rational_matrix(query),
        rational_matrix(query_metric),
        model_kind="independent_nuisance_protocol_mixture",
        vector_scale=amplification_vector_scale,
        protocol_mixture=mixture,
    )


def _parse_mixture_and_reassemble(
    block: object,
) -> tuple[QMatrix, QMatrix | None, QMatrix, QMatrix]:
    if not isinstance(block, dict):
        raise ValueError("protocol-mixture block is missing")
    schema = block.get("schema_version")
    if schema not in (
        "oig-query-shared-nuisance-mixture-v1",
        "oig-query-independent-nuisance-mixture-v1",
    ):
        raise ValueError("unknown query protocol-mixture schema")
    shared = schema == "oig-query-shared-nuisance-mixture-v1"
    expected_semantics = (
        "one shared nuisance vector across every active protocol"
        if shared
        else "one independently re-fit nuisance vector per active protocol"
    )
    if block.get("nuisance_semantics") != expected_semantics:
        raise ValueError("shared-nuisance semantics are inconsistent")
    expected_rule = (
        (
            "stack active responses and nuisance maps; scale each output metric by "
            "budget_share/cost; profile the shared nuisance only after assembly"
        )
        if shared
        else (
            "stack active responses; block-diagonalize active nuisance maps; scale each "
            "output metric by budget_share/cost; exact profiled information then adds linearly"
        )
    )
    if block.get("composition_rule") != expected_rule:
        raise ValueError("protocol-mixture composition rule is inconsistent")
    if block.get("inactive_zero_share_protocols_omitted_from_assembly") is not True:
        raise ValueError("zero-share omission flag is inconsistent")
    rows = block.get("protocols")
    if not isinstance(rows, list) or not rows:
        raise ValueError("protocol-mixture declarations are missing")
    protocols = []
    shares = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("a protocol-mixture row is malformed")
        response = rational_matrix(row["response_exact"])
        outputs, _ = _shape(response)
        nuisance_rows = row["nuisance_response_exact"]
        nuisance = None if nuisance_rows is None else rational_matrix(nuisance_rows)
        if nuisance is not None and _shape(nuisance)[0] != outputs:
            raise ValueError("a mixture nuisance response has the wrong output dimension")
        protocol = QueryProtocol(
            str(row["name"]),
            response,
            nuisance,
            rational_matrix(row["output_metric_exact"]),
            Q(row["cost_exact"]),
        )
        share = Q(row["budget_share_exact"])
        expected_physical = share / protocol.cost
        if row["physical_weight_exact"] != _fraction_text(expected_physical):
            raise ValueError("mixture physical and budget weights disagree")
        protocols.append(protocol)
        shares.append(share)
    if shared:
        assembled = _assemble_protocol_mixture(tuple(protocols), tuple(shares))
        observation, nuisance, output_metric, unprofiled, _, active = assembled
        individually_profiled = None
    else:
        independent = _assemble_independent_nuisance_mixture(
            tuple(protocols), tuple(shares)
        )
        (
            observation,
            nuisance,
            output_metric,
            unprofiled,
            individually_profiled,
            _,
            active,
        ) = independent
    reported_active = block.get("active_protocol_indices")
    if not isinstance(reported_active, list) or any(type(value) is not int for value in reported_active):
        raise ValueError("active protocol indices must be JSON integers")
    if reported_active != list(active):
        raise ValueError("active protocol indices do not reproduce")
    if block.get("unprofiled_information_sum_exact") != _matrix_text(unprofiled):
        raise ValueError("unprofiled mixture information does not reproduce")
    if not shared:
        if block.get("individually_profiled_information_sum_exact") != _matrix_text(
            individually_profiled  # type: ignore[arg-type]
        ):
            raise ValueError("individually profiled information sum does not reproduce")
        if block.get("profiled_information_adds_linearly_exact") is not True:
            raise ValueError("linear profiled-information theorem flag is inconsistent")
    return observation, nuisance, output_metric, unprofiled


def _finish_query_verification(
    report: dict[str, object],
    verification: dict[str, object],
    *,
    require_embedded: bool,
) -> dict[str, object]:
    embedded_present = "independent_exact_verification" in report
    if require_embedded and not embedded_present:
        raise ValueError("independent exact verification block is missing")
    if embedded_present and not _strict_json_equal(
        report["independent_exact_verification"], verification
    ):
        raise ValueError("embedded independent exact verification is inconsistent")
    return verification


def _verify_query_protocol_report(
    report: dict[str, object], *, require_embedded: bool
) -> dict[str, object]:
    """Reconstruct every theorem field, optionally requiring a sealed report."""
    try:
        def exact_integer(value: object, label: str) -> int:
            if type(value) is not int:
                raise ValueError(f"{label} must be a JSON integer")
            return value

        if report.get("schema_version") != "oig-query-protocol-certificate-v1":
            raise ValueError("unknown query certificate schema")
        if report.get("status") != "exact finite-linear query certificate":
            raise ValueError("query certificate status is inconsistent")
        if report.get("report_valid") is not True:
            raise ValueError("query report-valid flag is inconsistent")
        model_kind = report.get("model_kind")
        if model_kind not in (
            "single_experiment",
            "shared_nuisance_protocol_mixture",
            "independent_nuisance_protocol_mixture",
        ):
            raise ValueError("unknown query model kind")
        expected_top_keys = {
            "schema_version",
            "status",
            "model_kind",
            "source_dimension",
            "output_dimension",
            "query_dimension",
            "declared_nuisance_dimension",
            "nuisance_rank",
            "effective_response_rank",
            "declared_observation_exact",
            "declared_nuisance_response_exact",
            "declared_source_metric_exact",
            "declared_output_metric_exact",
            "declared_query_exact",
            "declared_query_metric_exact",
            "nuisance_elimination",
            "identifiability",
            "factorization_and_minimax",
            "proof_boundary",
            "report_valid",
        }
        if model_kind != "single_experiment":
            expected_top_keys.add("protocol_mixture")
        if "independent_exact_verification" in report:
            expected_top_keys.add("independent_exact_verification")
        if set(report) != expected_top_keys:
            raise ValueError("query report has missing or unexpected top-level fields")
        if report.get("proof_boundary") != _proof_boundary(str(model_kind)):
            raise ValueError("query proof boundary is inconsistent")

        observation = rational_matrix(report["declared_observation_exact"])  # type: ignore[arg-type]
        source_metric = rational_matrix(report["declared_source_metric_exact"])  # type: ignore[arg-type]
        output_metric = rational_matrix(report["declared_output_metric_exact"])  # type: ignore[arg-type]
        query = rational_matrix(report["declared_query_exact"])  # type: ignore[arg-type]
        query_metric = rational_matrix(report["declared_query_metric_exact"])  # type: ignore[arg-type]
        source_dimension = exact_integer(report["source_dimension"], "source dimension")
        output_dimension = exact_integer(report["output_dimension"], "output dimension")
        query_dimension = exact_integer(report["query_dimension"], "query dimension")
        nuisance_dimension = exact_integer(
            report["declared_nuisance_dimension"], "declared nuisance dimension"
        )
        nuisance = _parse_nuisance(
            report["declared_nuisance_response_exact"],
            output_dimension,
            nuisance_dimension,
        )
        expected_dimensions = _validate_model(
            observation,
            nuisance,
            source_metric,
            output_metric,
            query,
            query_metric,
        )
        if expected_dimensions != (
            source_dimension,
            output_dimension,
            query_dimension,
            nuisance_dimension,
        ):
            raise ValueError("reported query-model dimensions are inconsistent")

        if model_kind in (
            "shared_nuisance_protocol_mixture",
            "independent_nuisance_protocol_mixture",
        ):
            mixed_h, mixed_b, mixed_w, _ = _parse_mixture_and_reassemble(
                report.get("protocol_mixture")
            )
            if mixed_h != observation or mixed_b != nuisance or mixed_w != output_metric:
                raise ValueError("assembled protocol mixture differs from the declared model")
            expected_schema = (
                "oig-query-shared-nuisance-mixture-v1"
                if model_kind == "shared_nuisance_protocol_mixture"
                else "oig-query-independent-nuisance-mixture-v1"
            )
            if report["protocol_mixture"].get("schema_version") != expected_schema:  # type: ignore[union-attr]
                raise ValueError("model kind and protocol-mixture schema disagree")
        elif "protocol_mixture" in report:
            raise ValueError("single-experiment report contains a protocol-mixture block")

        basis, projector, effective, information = _profile_nuisance(
            observation, nuisance, output_metric
        )
        nuisance_rank = 0 if basis is None else _shape(basis)[1]
        coordinates = _row_basis(effective, source_dimension)
        effective_rank = len(coordinates)
        if exact_integer(report["nuisance_rank"], "nuisance rank") != nuisance_rank:
            raise ValueError("nuisance rank does not reproduce")
        if exact_integer(report["effective_response_rank"], "effective rank") != effective_rank:
            raise ValueError("effective response rank does not reproduce")
        elimination = report.get("nuisance_elimination")
        if not isinstance(elimination, dict):
            raise ValueError("nuisance-elimination block is missing")
        if set(elimination) != {
            "nuisance_basis_exact",
            "metric_orthogonal_projector_exact",
            "effective_response_exact",
            "profiled_information_exact",
            "projector_idempotent_exact",
            "projector_is_output_metric_self_adjoint_exact",
            "projector_annihilates_nuisance_exact",
        }:
            raise ValueError("nuisance-elimination block has an invalid schema")
        expected_basis = None if basis is None else _matrix_text(basis)
        if elimination.get("nuisance_basis_exact") != expected_basis:
            raise ValueError("nuisance basis does not reproduce")
        for field, expected in (
            ("metric_orthogonal_projector_exact", _matrix_text(projector)),
            ("effective_response_exact", _matrix_text(effective)),
            ("profiled_information_exact", _matrix_text(information)),
        ):
            if elimination.get(field) != expected:
                raise ValueError(f"nuisance field {field} does not reproduce")
        required_elimination_flags = (
            "projector_idempotent_exact",
            "projector_is_output_metric_self_adjoint_exact",
            "projector_annihilates_nuisance_exact",
        )
        if any(elimination.get(field) is not True for field in required_elimination_flags):
            raise ValueError("a nuisance-elimination theorem flag is inconsistent")

        nullspace = _nullspace_basis(effective)
        counterexample = next(
            (vector for vector in nullspace if any(_matrix_vector(query, vector))),
            None,
        )
        identifiable = counterexample is None
        identification = report.get("identifiability")
        if not isinstance(identification, dict):
            raise ValueError("identifiability block is missing")
        if set(identification) != {
            "query_identifiable_exact",
            "kernel_condition_exact",
            "kernel_counterexample_exact",
        }:
            raise ValueError("identifiability block has an invalid schema")
        if identification.get("query_identifiable_exact") is not identifiable:
            raise ValueError("query-identifiability flag is inconsistent")
        if identification.get("kernel_condition_exact") is not identifiable:
            raise ValueError("kernel-condition flag is inconsistent")
        expected_counterexample = (
            None if counterexample is None else _vector_text(counterexample)
        )
        if identification.get("kernel_counterexample_exact") != expected_counterexample:
            raise ValueError("kernel counterexample does not reproduce")

        certificate = report.get("factorization_and_minimax")
        if not isinstance(certificate, dict):
            raise ValueError("factorization/minimax block is missing")
        if not identifiable:
            if set(certificate) != {
                "kind",
                "factorization_exists",
                "zero_noise_minimax_error",
                "reason",
            }:
                raise ValueError("unidentifiable-query block has an invalid schema")
            if certificate.get("kind") != "unidentifiable-unbounded-source":
                raise ValueError("unidentifiable minimax kind is inconsistent")
            if certificate.get("factorization_exists") is not False:
                raise ValueError("unidentifiable factorization flag is inconsistent")
            if certificate.get("zero_noise_minimax_error") != "infinite":
                raise ValueError("unidentifiable minimax conclusion is inconsistent")
            if certificate.get("reason") != (
                "ker(effective_response) is not contained in ker(query)"
            ):
                raise ValueError("unidentifiable-query reason is inconsistent")
            return _finish_query_verification(report, {
                "passed": True,
                "method": "exact rational nuisance profiling and kernel counterexample",
                "query_identifiable": False,
            }, require_embedded=require_embedded)

        if effective_rank == 0:
            if set(certificate) != {
                "kind",
                "factorization_exists",
                "decoder_exact",
                "decoder_times_effective_response_equals_query_exact",
                "decoder_annihilates_nuisance_exact",
                "minimax_amplification_squared_lower_exact",
                "minimax_amplification_squared_upper_exact",
                "minimax_amplification_exactly_zero",
            }:
                raise ValueError("zero-query block has an invalid schema")
            if certificate.get("kind") != "identifiable-zero-query":
                raise ValueError("zero-query certificate kind is inconsistent")
            decoder = rational_matrix(certificate["decoder_exact"])  # type: ignore[arg-type]
            if decoder != _zeros(query_dimension, output_dimension) or not _zero(query):
                raise ValueError("zero-query decoder does not reproduce")
            if certificate.get("factorization_exists") is not True:
                raise ValueError("zero-query factorization flag is inconsistent")
            if certificate.get("minimax_amplification_squared_lower_exact") != "0/1":
                raise ValueError("zero-query lower amplification is inconsistent")
            if certificate.get("minimax_amplification_squared_upper_exact") != "0/1":
                raise ValueError("zero-query upper amplification is inconsistent")
            if certificate.get("minimax_amplification_exactly_zero") is not True:
                raise ValueError("zero-query amplification flag is inconsistent")
            for field in (
                "decoder_times_effective_response_equals_query_exact",
                "decoder_annihilates_nuisance_exact",
            ):
                if certificate.get(field) is not True:
                    raise ValueError("a zero-query theorem flag is inconsistent")
            return _finish_query_verification(report, {
                "passed": True,
                "method": "exact rational verification of the trivial identifiable query",
                "query_identifiable": True,
                "amplification_squared_lower_exact": "0/1",
                "amplification_squared_upper_exact": "0/1",
            }, require_embedded=require_embedded)

        if set(certificate) != {
            "kind",
            "factorization_exists",
            "quotient_row_coordinates_exact",
            "quotient_injection_exact",
            "quotient_source_metric_exact",
            "reduced_effective_response_exact",
            "reduced_query_exact",
            "reduced_data_gram_exact",
            "reduced_query_form_exact",
            "decoder_exact",
            "decoder_times_effective_response_equals_query_exact",
            "decoder_times_raw_observation_equals_query_exact",
            "decoder_annihilates_nuisance_exact",
            "amplification_lower_witness_exact",
            "minimax_amplification_squared_lower_exact",
            "minimax_amplification_squared_upper_exact",
            "upper_shift_positive_by_exact_ldl",
            "minimax_amplification_exactly_zero",
            "interpretation",
            "descriptive_amplification_lower",
            "descriptive_amplification_upper",
        }:
            raise ValueError("identifiable-query block has an invalid schema")
        if certificate.get("kind") != "identifiable-query-factorization":
            raise ValueError("identifiable-query certificate kind is inconsistent")
        if certificate.get("interpretation") != _QUERY_INTERPRETATION:
            raise ValueError("query minimax interpretation is inconsistent")

        coordinate_matrix = tuple(coordinates)
        source_inverse = _inverse(source_metric)
        quotient_metric = _inverse(
            _matmul(
                coordinate_matrix,
                _matmul(source_inverse, _transpose(coordinate_matrix)),
            )
        )
        injection = _matmul(
            source_inverse,
            _matmul(_transpose(coordinate_matrix), quotient_metric),
        )
        reduced_response = _matmul(effective, injection)
        reduced_query = _matmul(query, injection)
        data_gram = _matmul(
            _transpose(reduced_response),
            _matmul(output_metric, reduced_response),
        )
        query_form = _matmul(
            _transpose(reduced_query), _matmul(query_metric, reduced_query)
        )
        expected_matrices = (
            ("quotient_row_coordinates_exact", coordinate_matrix),
            ("quotient_injection_exact", injection),
            ("quotient_source_metric_exact", quotient_metric),
            ("reduced_effective_response_exact", reduced_response),
            ("reduced_query_exact", reduced_query),
            ("reduced_data_gram_exact", data_gram),
            ("reduced_query_form_exact", query_form),
        )
        for field, expected in expected_matrices:
            if certificate.get(field) != _matrix_text(expected):
                raise ValueError(f"factorization field {field} does not reproduce")
        decoder = _matmul(
            reduced_query,
            _matmul(
                _inverse(data_gram),
                _matmul(_transpose(reduced_response), output_metric),
            ),
        )
        if certificate.get("decoder_exact") != _matrix_text(decoder):
            raise ValueError("exact query decoder does not reproduce")
        if _matmul(decoder, effective) != query or _matmul(decoder, observation) != query:
            raise ValueError("query factorization does not verify")
        if nuisance is not None and not _zero(_matmul(decoder, nuisance)):
            raise ValueError("query decoder does not annihilate the nuisance")
        required_factor_flags = (
            "factorization_exists",
            "decoder_times_effective_response_equals_query_exact",
            "decoder_times_raw_observation_equals_query_exact",
            "decoder_annihilates_nuisance_exact",
        )
        if any(certificate.get(field) is not True for field in required_factor_flags):
            raise ValueError("a query-factorization theorem flag is inconsistent")

        lower = Q(certificate["minimax_amplification_squared_lower_exact"])
        upper = Q(certificate["minimax_amplification_squared_upper_exact"])
        if _zero(query_form):
            if lower != 0 or upper != 0:
                raise ValueError("zero query form has nonzero amplification")
            if certificate.get("amplification_lower_witness_exact") is not None:
                raise ValueError("zero query form has a spurious lower witness")
            if certificate.get("minimax_amplification_exactly_zero") is not True:
                raise ValueError("zero amplification flag is inconsistent")
            if certificate.get("upper_shift_positive_by_exact_ldl") is not False:
                raise ValueError("zero amplification LDL flag is inconsistent")
        else:
            witness_rows = certificate.get("amplification_lower_witness_exact")
            if not isinstance(witness_rows, list) or len(witness_rows) != effective_rank:
                raise ValueError("amplification witness has the wrong dimension")
            witness = tuple(Q(value) for value in witness_rows)
            if not any(witness):
                raise ValueError("amplification witness vanishes")
            numerator_vector = _matrix_vector(query_form, witness)
            denominator_vector = _matrix_vector(data_gram, witness)
            numerator_value = sum(
                (left * right for left, right in zip(witness, numerator_vector)), Q(0)
            )
            denominator_value = sum(
                (left * right for left, right in zip(witness, denominator_vector)), Q(0)
            )
            if denominator_value <= 0 or lower != numerator_value / denominator_value:
                raise ValueError("amplification lower witness does not reproduce")
            if upper <= 0 or not _ldl_positive_definite(
                _subtract(_scale(data_gram, upper), query_form)
            ):
                raise ValueError("amplification upper shift is not positive definite")
            if lower > upper:
                raise ValueError("amplification bracket is reversed")
            if certificate.get("upper_shift_positive_by_exact_ldl") is not True:
                raise ValueError("amplification upper-LDL flag is inconsistent")
            if certificate.get("minimax_amplification_exactly_zero") is not False:
                raise ValueError("nonzero amplification flag is inconsistent")
        return _finish_query_verification(report, {
            "passed": True,
            "method": (
                "exact rational reconstruction of the nuisance quotient, kernel condition, "
                "query factorization, and minimax amplification bracket"
            ),
            "query_identifiable": True,
            "amplification_squared_lower_exact": _fraction_text(lower),
            "amplification_squared_upper_exact": _fraction_text(upper),
        }, require_embedded=require_embedded)
    except Exception as error:
        return {"passed": False, "error": str(error)}


def verify_query_protocol_report(report: dict[str, object]) -> dict[str, object]:
    """Verify a sealed query report, including its embedded result block."""
    return _verify_query_protocol_report(report, require_embedded=True)


__all__ = [
    "QueryProtocol",
    "certify_query_model",
    "certify_query_independent_nuisance_mixture",
    "certify_query_protocol_mixture",
    "verify_query_protocol_report",
]
