"""Proof-oriented protocol design for finite partially observed networks.

The engine accepts exact rational response matrices, output-noise precision
matrices, protocol costs, and a source-cost metric.  It removes the common
blind subspace exactly, optimizes a descriptive E-optimal design, rationalizes
that design, and returns exact primal/dual certificates for the resulting
generalized information floor.

Floating-point optimization discovers candidates only.  Every theorem field
in the returned report is decided by ``fractions.Fraction`` arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Iterable, Sequence

import numpy as np
from scipy.linalg import eigh
from scipy.optimize import minimize
from scipy.special import ndtr


Q = Fraction
QMatrix = tuple[tuple[Fraction, ...], ...]
ExactScalar = int | str | Fraction


def _q(value: ExactScalar) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, float):
        raise TypeError(
            "binary floating inputs are not exact declarations; use a decimal string or Fraction"
        )
    return Fraction(value)


def rational_matrix(rows: Sequence[Sequence[ExactScalar]]) -> QMatrix:
    matrix = tuple(tuple(_q(value) for value in row) for row in rows)
    if not matrix or not matrix[0]:
        raise ValueError("a matrix must be nonempty")
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("matrix rows have inconsistent lengths")
    return matrix


def _shape(matrix: QMatrix) -> tuple[int, int]:
    return len(matrix), len(matrix[0])


def _zeros(rows: int, columns: int) -> QMatrix:
    return tuple(tuple(Q(0) for _ in range(columns)) for _ in range(rows))


def _identity(dimension: int) -> QMatrix:
    return tuple(
        tuple(Q(int(row == column)) for column in range(dimension))
        for row in range(dimension)
    )


def _transpose(matrix: QMatrix) -> QMatrix:
    rows, columns = _shape(matrix)
    return tuple(tuple(matrix[row][column] for row in range(rows)) for column in range(columns))


def _matmul(left: QMatrix, right: QMatrix) -> QMatrix:
    left_rows, shared = _shape(left)
    right_rows, right_columns = _shape(right)
    if shared != right_rows:
        raise ValueError("matrix dimensions do not agree")
    return tuple(
        tuple(
            sum((left[row][index] * right[index][column] for index in range(shared)), Q(0))
            for column in range(right_columns)
        )
        for row in range(left_rows)
    )


def _add(left: QMatrix, right: QMatrix) -> QMatrix:
    if _shape(left) != _shape(right):
        raise ValueError("matrix dimensions do not agree")
    return tuple(
        tuple(left[row][column] + right[row][column] for column in range(len(left[0])))
        for row in range(len(left))
    )


def _subtract(left: QMatrix, right: QMatrix) -> QMatrix:
    if _shape(left) != _shape(right):
        raise ValueError("matrix dimensions do not agree")
    return tuple(
        tuple(left[row][column] - right[row][column] for column in range(len(left[0])))
        for row in range(len(left))
    )


def _scale(matrix: QMatrix, scalar: Fraction) -> QMatrix:
    return tuple(tuple(scalar * value for value in row) for row in matrix)


def _symmetric(matrix: QMatrix) -> bool:
    rows, columns = _shape(matrix)
    return rows == columns and all(
        matrix[row][column] == matrix[column][row]
        for row in range(rows)
        for column in range(row)
    )


def _inverse(matrix: QMatrix) -> QMatrix:
    rows, columns = _shape(matrix)
    if rows != columns:
        raise ValueError("only square matrices can be inverted")
    augmented = [list(matrix[row]) + list(_identity(rows)[row]) for row in range(rows)]
    for pivot_column in range(rows):
        pivot = next(
            (row for row in range(pivot_column, rows) if augmented[row][pivot_column]),
            None,
        )
        if pivot is None:
            raise ValueError("matrix is singular")
        augmented[pivot_column], augmented[pivot] = augmented[pivot], augmented[pivot_column]
        divisor = augmented[pivot_column][pivot_column]
        augmented[pivot_column] = [value / divisor for value in augmented[pivot_column]]
        for row in range(rows):
            if row == pivot_column:
                continue
            factor = augmented[row][pivot_column]
            if factor:
                augmented[row] = [
                    value - factor * reference
                    for value, reference in zip(augmented[row], augmented[pivot_column])
                ]
    return tuple(tuple(row[rows:]) for row in augmented)


def _row_basis(rows: Iterable[Sequence[Fraction]], width: int) -> QMatrix:
    work = [list(row) for row in rows if any(row)]
    if any(len(row) != width for row in work):
        raise ValueError("row width does not match the source dimension")
    pivot_row = 0
    for column in range(width):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [value / divisor for value in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    value - factor * reference
                    for value, reference in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == len(work):
            break
    return tuple(tuple(row) for row in work[:pivot_row])


def _ldl_positive_definite(matrix: QMatrix) -> bool:
    if not _symmetric(matrix):
        return False
    dimension = len(matrix)
    lower = [[Q(0) for _ in range(dimension)] for _ in range(dimension)]
    diagonal = [Q(0) for _ in range(dimension)]
    for row in range(dimension):
        residual = matrix[row][row] - sum(
            lower[row][index] ** 2 * diagonal[index] for index in range(row)
        )
        if residual <= 0:
            return False
        diagonal[row] = residual
        lower[row][row] = Q(1)
        for target in range(row + 1, dimension):
            numerator = matrix[target][row] - sum(
                lower[target][index] * lower[row][index] * diagonal[index]
                for index in range(row)
            )
            lower[target][row] = numerator / diagonal[row]
    return True


def _trace_product(left: QMatrix, right: QMatrix) -> Fraction:
    if _shape(left) != _shape(right):
        raise ValueError("matrix dimensions do not agree")
    dimension = len(left)
    return sum(
        (left[row][column] * right[column][row] for row in range(dimension) for column in range(dimension)),
        Q(0),
    )


def _float_matrix(matrix: QMatrix) -> np.ndarray:
    return np.asarray([[float(value) for value in row] for row in matrix], dtype=float)


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _matrix_text(matrix: QMatrix) -> list[list[str]]:
    return [[_fraction_text(value) for value in row] for row in matrix]


@dataclass(frozen=True)
class RationalProtocol:
    """One finite observation protocol in exact coordinates."""

    name: str
    response: QMatrix
    noise_precision: QMatrix
    cost: Fraction = Q(1)

    @classmethod
    def from_rows(
        cls,
        name: str,
        response: Sequence[Sequence[ExactScalar]],
        noise_precision: Sequence[Sequence[ExactScalar]],
        cost: ExactScalar = 1,
    ) -> "RationalProtocol":
        return cls(name, rational_matrix(response), rational_matrix(noise_precision), _q(cost))


@dataclass(frozen=True)
class QuotientModel:
    row_coordinates: QMatrix
    injection: QMatrix
    source_metric: QMatrix
    protocol_information: tuple[QMatrix, ...]


def information_matrix(protocol: RationalProtocol) -> QMatrix:
    response_rows, source_dimension = _shape(protocol.response)
    if _shape(protocol.noise_precision) != (response_rows, response_rows):
        raise ValueError("noise precision has the wrong dimension")
    if protocol.cost <= 0:
        raise ValueError("protocol cost must be positive")
    if not _ldl_positive_definite(protocol.noise_precision):
        raise ValueError("noise precision must be symmetric positive definite")
    result = _matmul(
        _transpose(protocol.response),
        _matmul(protocol.noise_precision, protocol.response),
    )
    if _shape(result) != (source_dimension, source_dimension):
        raise AssertionError("information construction changed source dimension")
    return result


def exponential_time_response(
    laplacian: Sequence[Sequence[ExactScalar]],
    intervention: Sequence[Sequence[ExactScalar]],
    sensor: Sequence[Sequence[ExactScalar]],
    rate: ExactScalar,
) -> QMatrix:
    """Return the exact response observed at an exponential random time.

    With column probabilities evolving as ``p(t)=exp(-tL)p(0)`` and
    ``T~Exp(rate)`` independent of the chain,

        E[C p(T)] = C * rate * (rate I + L)^-1 * p(0).

    The routine is useful for exact rational hidden-network benchmarks: it
    retains genuine continuous-time Markov dynamics without approximating a
    matrix exponential by floating point.
    """
    generator = rational_matrix(laplacian)
    injection = rational_matrix(intervention)
    observation = rational_matrix(sensor)
    alpha = _q(rate)
    state_count, columns = _shape(generator)
    if state_count != columns:
        raise ValueError("the Markov Laplacian must be square")
    if alpha <= 0:
        raise ValueError("the exponential observation rate must be positive")
    if _shape(injection)[0] != state_count or _shape(observation)[1] != state_count:
        raise ValueError("state dimensions do not agree")
    if any(sum((generator[row][column] for row in range(state_count)), Q(0)) != 0 for column in range(state_count)):
        raise ValueError("the column Markov Laplacian must conserve total mass")
    if any(
        generator[row][column] > 0
        for row in range(state_count)
        for column in range(state_count)
        if row != column
    ):
        raise ValueError("a Markov Laplacian must have nonpositive off-diagonal entries")
    resolvent = _inverse(_add(_scale(_identity(state_count), alpha), generator))
    return _matmul(observation, _matmul(_scale(resolvent, alpha), injection))


def exact_observable_quotient(
    protocols: Sequence[RationalProtocol], source_metric: QMatrix
) -> QuotientModel:
    """Remove the common response kernel and descend source cost exactly.

    If ``C`` is a row basis of all response maps, quotient coordinates are
    ``y=C u``.  The minimum-cost representative is

        ``u = S^-1 C^T (C S^-1 C^T)^-1 y``.

    This construction is coordinate invariant and keeps every protocol
    response unchanged on equivalence classes.
    """
    if not protocols:
        raise ValueError("at least one protocol is required")
    dimension = _shape(protocols[0].response)[1]
    if _shape(source_metric) != (dimension, dimension):
        raise ValueError("source metric has the wrong dimension")
    if not _ldl_positive_definite(source_metric):
        raise ValueError("source metric must be symmetric positive definite")
    if any(_shape(protocol.response)[1] != dimension for protocol in protocols):
        raise ValueError("protocol source dimensions do not agree")

    coordinates = _row_basis(
        (row for protocol in protocols for row in protocol.response), dimension
    )
    if not coordinates:
        raise ValueError("every declared protocol is exactly blind")
    source_inverse = _inverse(source_metric)
    moment = _matmul(coordinates, _matmul(source_inverse, _transpose(coordinates)))
    quotient_metric = _inverse(moment)
    injection = _matmul(
        source_inverse,
        _matmul(_transpose(coordinates), quotient_metric),
    )
    if _matmul(coordinates, injection) != _identity(len(coordinates)):
        raise AssertionError("quotient injection is not a right inverse")

    quotient_information = []
    for protocol in protocols:
        reduced_response = _matmul(protocol.response, injection)
        reduced = RationalProtocol(
            protocol.name,
            reduced_response,
            protocol.noise_precision,
            protocol.cost,
        )
        quotient_information.append(information_matrix(reduced))
    return QuotientModel(
        coordinates,
        injection,
        quotient_metric,
        tuple(quotient_information),
    )


def _simplex_rationalization(weights: np.ndarray, denominator: int) -> tuple[Fraction, ...]:
    if denominator < 1:
        raise ValueError("weight denominator must be positive")
    clipped = np.maximum(np.asarray(weights, dtype=float), 0.0)
    if not np.isfinite(clipped).all() or clipped.sum() <= 0:
        raise ValueError("optimizer returned invalid weights")
    clipped /= clipped.sum()
    scaled = clipped * denominator
    counts = np.floor(scaled).astype(int)
    remainder = denominator - int(counts.sum())
    order = np.argsort(-(scaled - counts))
    counts[order[:remainder]] += 1
    return tuple(Q(int(count), denominator) for count in counts)


def _design_gram(
    information: Sequence[QMatrix], costs: Sequence[Fraction], budget_weights: Sequence[Fraction]
) -> QMatrix:
    dimension = len(information[0])
    result = _zeros(dimension, dimension)
    for candidate, cost, budget_weight in zip(information, costs, budget_weights):
        result = _add(result, _scale(candidate, budget_weight / cost))
    return result


def _generalized_minimum(gram: QMatrix, metric: QMatrix) -> tuple[float, np.ndarray]:
    values, vectors = eigh(_float_matrix(gram), _float_matrix(metric), check_finite=True)
    return float(values[0]), np.asarray(vectors[:, 0], dtype=float)


def _optimize_budget_weights(
    information: Sequence[QMatrix], costs: Sequence[Fraction], metric: QMatrix
) -> np.ndarray:
    candidates = [
        _float_matrix(_scale(matrix, Q(1) / cost))
        for matrix, cost in zip(information, costs)
    ]
    metric_float = _float_matrix(metric)
    count = len(candidates)

    def objective(weights: np.ndarray) -> float:
        gram = sum((weight * matrix for weight, matrix in zip(weights, candidates)), np.zeros_like(candidates[0]))
        return -float(eigh(gram, metric_float, eigvals_only=True, subset_by_index=[0, 0])[0])

    constraints = {"type": "eq", "fun": lambda weights: float(np.sum(weights) - 1.0)}
    starts = [np.full(count, 1.0 / count)]
    starts.extend(np.eye(count))
    best = None
    for start in starts:
        result = minimize(
            objective,
            start,
            method="SLSQP",
            bounds=[(0.0, 1.0)] * count,
            constraints=constraints,
            options={"ftol": 1e-13, "maxiter": 2000},
        )
        if result.success and (best is None or result.fun < best.fun):
            best = result
    if best is None:
        raise ArithmeticError("descriptive E-optimal search did not converge")
    return np.maximum(best.x, 0.0) / np.maximum(best.x, 0.0).sum()


def _primal_lower(gram: QMatrix, metric: QMatrix) -> Fraction:
    minimum, _ = _generalized_minimum(gram, metric)
    if minimum <= 0:
        raise ArithmeticError("rationalized design has no positive information floor")
    candidate = Q(str(0.999 * minimum)).limit_denominator(10**18)
    for _ in range(80):
        if candidate > 0 and _ldl_positive_definite(_subtract(gram, _scale(metric, candidate))):
            return candidate
        candidate /= 2
    raise ArithmeticError("could not certify a positive primal floor")


def _dual_upper(
    gram: QMatrix,
    information: Sequence[QMatrix],
    costs: Sequence[Fraction],
    metric: QMatrix,
    vector_scale: int,
) -> tuple[Fraction, tuple[tuple[int, ...], ...], QMatrix]:
    dimension = len(metric)
    metric_float = _float_matrix(metric)
    candidate_float = [
        _float_matrix(_scale(candidate, Q(1) / cost))
        for candidate, cost in zip(information, costs)
    ]
    lower_indices = [(row, column) for row in range(dimension) for column in range(row + 1)]

    def unpack(parameters: np.ndarray) -> np.ndarray:
        factor = np.zeros((dimension, dimension), dtype=float)
        norm = float(np.linalg.norm(parameters))
        if norm <= 1e-15:
            return factor
        for value, (row, column) in zip(parameters / norm, lower_indices):
            factor[row, column] = value
        return factor

    def objective(parameters: np.ndarray) -> float:
        factor = unpack(parameters)
        witness = factor @ factor.T
        denominator = float(np.trace(metric_float @ witness))
        if denominator <= 1e-15:
            return 1e100
        return max(float(np.trace(candidate @ witness)) / denominator for candidate in candidate_float)

    starts: list[np.ndarray] = []
    inverse_cholesky = np.linalg.cholesky(np.linalg.inv(metric_float))
    starts.append(np.asarray([inverse_cholesky[row, column] for row, column in lower_indices]))
    _, weak_vector = _generalized_minimum(gram, metric)
    rank_one = np.zeros((dimension, dimension), dtype=float)
    rank_one[:, 0] = weak_vector
    starts.append(np.asarray([rank_one[row, column] for row, column in lower_indices]))
    generator = np.random.default_rng(20260814)
    starts.extend(generator.normal(size=len(lower_indices)) for _ in range(6))

    discovered: list[np.ndarray] = []
    for start in starts:
        result = minimize(
            objective,
            start,
            method="Powell",
            options={"xtol": 1e-12, "ftol": 1e-13, "maxiter": 10_000},
        )
        if result.success:
            discovered.append(unpack(result.x))
    if not discovered:
        raise ArithmeticError("dual factor discovery did not converge")

    best: tuple[Fraction, tuple[tuple[int, ...], ...], QMatrix] | None = None
    for factor in discovered:
        integers = tuple(
            tuple(int(round(factor[row, column] * vector_scale)) for column in range(dimension))
            for row in range(dimension)
        )
        if not any(value for row in integers for value in row):
            continue
        integer_matrix = tuple(tuple(Q(value) for value in row) for row in integers)
        raw_witness = _matmul(integer_matrix, _transpose(integer_matrix))
        denominator = _trace_product(metric, raw_witness)
        if denominator <= 0:
            continue
        witness = _scale(raw_witness, Q(1) / denominator)
        sensitivities = [
            _trace_product(candidate, witness) / cost
            for candidate, cost in zip(information, costs)
        ]
        record = (max(sensitivities), integers, witness)
        if best is None or record[0] < best[0]:
            best = record
    if best is None:
        raise ArithmeticError("every rationalized dual factor vanished")
    if _trace_product(metric, best[2]) != 1:
        raise AssertionError("dual witness does not have unit metric trace")
    return best


def _noise_record(
    floor: Fraction, amplitude: Fraction, exposure_multiplier: int
) -> dict[str, object]:
    if (
        amplitude <= 0
        or not isinstance(exposure_multiplier, int)
        or isinstance(exposure_multiplier, bool)
        or exposure_multiplier < 1
    ):
        raise ValueError("noise parameters must be positive")
    separation_squared = exposure_multiplier * amplitude * amplitude * floor
    separation = math.sqrt(float(separation_squared))
    gaussian_error_rational_upper = Q(4) / (8 + separation_squared)
    report: dict[str, object] = {
        "role": "certified consequence of the floor under the already-whitened unit-covariance Gaussian model",
        "amplitude_exact": _fraction_text(amplitude),
        "continuous_budget_exposure_multiplier": exposure_multiplier,
        "certified_squared_separation_lower_exact": _fraction_text(separation_squared),
        "gaussian_error_rational_upper_exact": _fraction_text(
            gaussian_error_rational_upper
        ),
        "gaussian_error_rational_upper_method": (
            "Q(d/2)<=exp(-d^2/8)/2<=4/(8+d^2)"
        ),
        "descriptive_exact_gaussian_error": float(ndtr(-separation / 2)),
        "formula": "Phi(-amplitude*sqrt(exposure_multiplier*floor)/2)",
    }
    return report


def design_protocols(
    protocols: Sequence[RationalProtocol],
    source_metric: Sequence[Sequence[ExactScalar]],
    *,
    weight_denominator: int = 10**6,
    dual_vector_scale: int = 10**7,
    amplitude: int | str | Fraction = 1,
    exposure_multiplier: int = 1,
) -> dict[str, object]:
    """Discover a protocol mixture and exactly bracket E-optimality."""
    metric = rational_matrix(source_metric)
    exact_amplitude = _q(amplitude)
    quotient = exact_observable_quotient(protocols, metric)
    costs = tuple(protocol.cost for protocol in protocols)
    discovered = _optimize_budget_weights(
        quotient.protocol_information, costs, quotient.source_metric
    )
    budget_weights = _simplex_rationalization(discovered, weight_denominator)
    gram = _design_gram(quotient.protocol_information, costs, budget_weights)
    lower = _primal_lower(gram, quotient.source_metric)
    upper, dual_factor, dual_witness = _dual_upper(
        gram,
        quotient.protocol_information,
        costs,
        quotient.source_metric,
        dual_vector_scale,
    )
    if lower > upper:
        raise AssertionError("primal lower bound exceeds dual upper bound")
    physical_weights = tuple(weight / cost for weight, cost in zip(budget_weights, costs))
    exact_budget = sum(
        (cost * weight for cost, weight in zip(costs, physical_weights)), Q(0)
    )
    if exact_budget != 1:
        raise AssertionError("rationalized design violates its budget")

    realization_multiplier = math.lcm(
        *(weight.denominator for weight in physical_weights)
    )
    realized_exposure = realization_multiplier * math.ceil(
        exposure_multiplier / realization_multiplier
    )
    realization_counts = tuple(
        int(realized_exposure * weight) for weight in physical_weights
    )

    report: dict[str, object] = {
        "schema_version": "oig-protocol-design-engine-v1",
        "status": "exact quotient and exact rational primal/dual certificate",
        "source_dimension": len(metric),
        "observable_quotient_dimension": len(quotient.source_metric),
        "exact_blind_dimension": len(metric) - len(quotient.source_metric),
        "declared_source_metric": _matrix_text(metric),
        "quotient_row_coordinates": _matrix_text(quotient.row_coordinates),
        "quotient_injection": _matrix_text(quotient.injection),
        "quotient_source_metric": _matrix_text(quotient.source_metric),
        "quotient_protocol_information": [
            _matrix_text(matrix) for matrix in quotient.protocol_information
        ],
        "protocols": [
            {
                "name": protocol.name,
                "cost_exact": _fraction_text(protocol.cost),
                "response_exact": _matrix_text(protocol.response),
                "noise_precision_exact": _matrix_text(protocol.noise_precision),
                "budget_share_exact": _fraction_text(budget_weight),
                "physical_weight_exact": _fraction_text(weight),
            }
            for protocol, budget_weight, weight in zip(protocols, budget_weights, physical_weights)
        ],
        "certificate": {
            "primal_generalized_floor_lower_exact": _fraction_text(lower),
            "dual_optimum_upper_exact": _fraction_text(upper),
            "certified_optimality_gap_upper_exact": _fraction_text(upper - lower),
            "certified_efficiency_lower_exact": _fraction_text(lower / upper),
            "primal_shift_positive_by_exact_ldl": True,
            "dual_witness_integer_factor": [list(row) for row in dual_factor],
            "dual_witness_exact": _matrix_text(dual_witness),
            "rationalized_design_gram_exact": _matrix_text(gram),
            "dual_witness_psd_by_exact_factorization": True,
            "dual_metric_trace_exactly_one": _trace_product(quotient.source_metric, dual_witness) == 1,
            "budget_exactly_one": exact_budget == 1,
        },
        "noise_performance": {
            "approximate_design_measure": _noise_record(
                lower, exact_amplitude, exposure_multiplier
            ),
            "integer_realization": {
                **_noise_record(lower, exact_amplitude, realized_exposure),
                "minimum_budget_multiplier_exactly_realizing_weights": realization_multiplier,
                "realized_budget_multiplier": realized_exposure,
                "protocol_counts": list(realization_counts),
                "requested_multiplier_was_exactly_realizable": (
                    exposure_multiplier % realization_multiplier == 0
                ),
            },
        },
        "proof_boundary": (
            "Floating point is used only to discover weights and a dual vector. "
            "The exact certificate covers the declared rational finite protocols; "
            "binary floating matrix declarations are rejected. "
            "It does not by itself certify continuum-to-finite model transfer or "
            "the completeness of the candidate protocol list."
        ),
        "overall_passed": bool(lower > 0 and upper >= lower and exact_budget == 1),
    }
    verification = verify_design_report(report)
    if not verification["passed"]:
        raise AssertionError(f"self-verification failed: {verification}")
    report["independent_exact_verification"] = verification
    return report


def verify_design_report(report: dict[str, object]) -> dict[str, object]:
    """Independently recheck every exact theorem field in an engine report."""
    try:
        def exact_json_integer(value: object, label: str) -> int:
            if type(value) is not int:
                raise ValueError(f"{label} must be a JSON integer")
            return value

        if report.get("schema_version") != "oig-protocol-design-engine-v1":
            raise ValueError("unknown report schema")
        metric = rational_matrix(report["declared_source_metric"])  # type: ignore[arg-type]
        protocol_rows = report["protocols"]  # type: ignore[assignment]
        if not isinstance(protocol_rows, list) or not protocol_rows:
            raise ValueError("protocol declarations are missing")
        protocols = tuple(
            RationalProtocol(
                str(row["name"]),
                rational_matrix(row["response_exact"]),
                rational_matrix(row["noise_precision_exact"]),
                Q(row["cost_exact"]),
            )
            for row in protocol_rows
        )
        quotient = exact_observable_quotient(protocols, metric)
        expected_dimensions = (
            len(metric),
            len(quotient.source_metric),
            len(metric) - len(quotient.source_metric),
        )
        reported_dimensions = (
            exact_json_integer(report["source_dimension"], "source dimension"),
            exact_json_integer(
                report["observable_quotient_dimension"], "quotient dimension"
            ),
            exact_json_integer(report["exact_blind_dimension"], "blind dimension"),
        )
        if reported_dimensions != expected_dimensions:
            raise ValueError("reported source/quotient dimensions are inconsistent")
        if _matrix_text(quotient.row_coordinates) != report["quotient_row_coordinates"]:
            raise ValueError("quotient row coordinates do not reproduce")
        if _matrix_text(quotient.injection) != report["quotient_injection"]:
            raise ValueError("quotient injection does not reproduce")
        if _matrix_text(quotient.source_metric) != report["quotient_source_metric"]:
            raise ValueError("quotient source metric does not reproduce")
        if [
            _matrix_text(matrix) for matrix in quotient.protocol_information
        ] != report["quotient_protocol_information"]:
            raise ValueError("quotient information matrices do not reproduce")

        costs = tuple(protocol.cost for protocol in protocols)
        shares = tuple(Q(row["budget_share_exact"]) for row in protocol_rows)
        physical = tuple(Q(row["physical_weight_exact"]) for row in protocol_rows)
        if any(weight < 0 for weight in shares + physical):
            raise ValueError("a reported design weight is negative")
        if any(weight != share / cost for weight, share, cost in zip(physical, shares, costs)):
            raise ValueError("physical and budget weights disagree")
        if sum(shares, Q(0)) != 1:
            raise ValueError("budget shares do not sum to one")
        gram = _design_gram(quotient.protocol_information, costs, shares)
        certificate = report["certificate"]  # type: ignore[assignment]
        if not isinstance(certificate, dict):
            raise ValueError("certificate block is missing")
        if _matrix_text(gram) != certificate["rationalized_design_gram_exact"]:
            raise ValueError("design Gram does not reproduce")

        lower = Q(certificate["primal_generalized_floor_lower_exact"])
        upper = Q(certificate["dual_optimum_upper_exact"])
        if lower <= 0 or not _ldl_positive_definite(
            _subtract(gram, _scale(quotient.source_metric, lower))
        ):
            raise ValueError("primal generalized floor does not verify")

        factor_rows = certificate["dual_witness_integer_factor"]
        factor = rational_matrix(factor_rows)  # type: ignore[arg-type]
        raw_witness = _matmul(factor, _transpose(factor))
        denominator = _trace_product(quotient.source_metric, raw_witness)
        if denominator <= 0:
            raise ValueError("dual factor vanishes")
        witness = _scale(raw_witness, Q(1) / denominator)
        if _matrix_text(witness) != certificate["dual_witness_exact"]:
            raise ValueError("dual witness does not reproduce")
        sensitivities = [
            _trace_product(candidate, witness) / cost
            for candidate, cost in zip(quotient.protocol_information, costs)
        ]
        if max(sensitivities) != upper:
            raise ValueError("dual optimum upper does not reproduce")
        if certificate["certified_optimality_gap_upper_exact"] != _fraction_text(upper - lower):
            raise ValueError("optimality gap field is inconsistent")
        if certificate["certified_efficiency_lower_exact"] != _fraction_text(lower / upper):
            raise ValueError("efficiency field is inconsistent")
        required_true_flags = (
            "primal_shift_positive_by_exact_ldl",
            "dual_witness_psd_by_exact_factorization",
            "dual_metric_trace_exactly_one",
            "budget_exactly_one",
        )
        if any(certificate.get(field) is not True for field in required_true_flags):
            raise ValueError("a theorem decision flag is inconsistent")

        noise = report["noise_performance"]  # type: ignore[assignment]
        if not isinstance(noise, dict):
            raise ValueError("noise block is missing")
        for key in ("approximate_design_measure", "integer_realization"):
            row = noise[key]
            amplitude = Q(row["amplitude_exact"])
            exposure = exact_json_integer(
                row["continuous_budget_exposure_multiplier"], "noise exposure"
            )
            expected = _noise_record(lower, amplitude, exposure)
            for field in (
                "certified_squared_separation_lower_exact",
                "gaussian_error_rational_upper_exact",
            ):
                if row[field] != expected[field]:
                    raise ValueError(f"noise field {field} does not reproduce")
        realized = noise["integer_realization"]
        multiplier = math.lcm(*(weight.denominator for weight in physical))
        reported_multiplier = exact_json_integer(
            realized["minimum_budget_multiplier_exactly_realizing_weights"],
            "realization multiplier",
        )
        if reported_multiplier != multiplier:
            raise ValueError("integer realization multiplier is not minimal")
        realized_exposure = exact_json_integer(
            realized["realized_budget_multiplier"], "realized exposure"
        )
        if realized_exposure % multiplier:
            raise ValueError("reported integer exposure does not realize all weights")
        exact_counts = [realized_exposure * weight for weight in physical]
        if any(count.denominator != 1 for count in exact_counts):
            raise ValueError("a reported protocol count is fractional")
        expected_counts = [count.numerator for count in exact_counts]
        reported_counts = realized["protocol_counts"]
        if not isinstance(reported_counts, list) or any(
            type(count) is not int for count in reported_counts
        ):
            raise ValueError("protocol counts must be JSON integers")
        if reported_counts != expected_counts:
            raise ValueError("integer protocol counts do not reproduce")
        if sum((cost * count for cost, count in zip(costs, expected_counts)), Q(0)) != realized_exposure:
            raise ValueError("integer realization violates the cost budget")
        requested_exposure = exact_json_integer(
            noise["approximate_design_measure"]["continuous_budget_exposure_multiplier"],
            "requested exposure",
        )
        expected_realized_exposure = multiplier * math.ceil(
            requested_exposure / multiplier
        )
        if realized_exposure != expected_realized_exposure:
            raise ValueError(
                "integer realization is not the least realizable exposure at or above the request"
            )
        realized_flag = realized["requested_multiplier_was_exactly_realizable"]
        if type(realized_flag) is not bool or realized_flag != (
            requested_exposure % multiplier == 0
        ):
            raise ValueError("requested-realizable flag is inconsistent")

        passed = bool(
            report.get("overall_passed") is True
            and lower <= upper
            and _trace_product(quotient.source_metric, witness) == 1
            and report.get("status")
            == "exact quotient and exact rational primal/dual certificate"
        )
        return {
            "passed": passed,
            "method": "independent exact-rational reconstruction of quotient, design, primal, dual, noise, and integer realization",
            "primal_lower_exact": _fraction_text(lower),
            "dual_upper_exact": _fraction_text(upper),
        }
    except Exception as error:  # A verifier reports malformed/tampered evidence.
        return {"passed": False, "error": str(error)}


def certify_frame_loss(
    full_information: Sequence[Sequence[ExactScalar]],
    sensed_information: Sequence[Sequence[ExactScalar]],
    source_metric: Sequence[Sequence[ExactScalar]],
    *,
    inherited_floor: ExactScalar | None = None,
) -> dict[str, object]:
    """Certify ``sensed >= full - delta*S`` in exact rational arithmetic."""
    full = rational_matrix(full_information)
    sensed = rational_matrix(sensed_information)
    metric = rational_matrix(source_metric)
    if _shape(full) != _shape(sensed) or _shape(full) != _shape(metric):
        raise ValueError("frame matrices and source metric must have equal shape")
    if not _ldl_positive_definite(metric):
        raise ValueError("source metric must be positive definite")
    loss = _subtract(full, sensed)
    maximum = float(eigh(_float_matrix(loss), _float_matrix(metric), eigvals_only=True)[-1])
    candidate = Q(str(max(0.0, maximum) * 1.001 + 1e-15)).limit_denominator(10**18)
    for _ in range(80):
        if candidate > 0 and _ldl_positive_definite(_subtract(_scale(metric, candidate), loss)):
            break
        candidate = 2 * candidate if candidate else Q(1, 10**18)
    else:
        raise ArithmeticError("could not certify the sensor-frame loss")
    record: dict[str, object] = {
        "schema_version": "oig-finite-frame-loss-v1",
        "full_information_exact": _matrix_text(full),
        "sensed_information_exact": _matrix_text(sensed),
        "source_metric_exact": _matrix_text(metric),
        "frame_loss_upper_exact": _fraction_text(candidate),
        "finite_frame_form_bound_certified_by_exact_ldl": True,
        "meaning": "sensed_information >= full_information - frame_loss_upper*source_metric",
    }
    if inherited_floor is not None:
        floor = _q(inherited_floor)
        transferred = floor - candidate
        record.update(
            {
                "inherited_floor_exact": _fraction_text(floor),
                "transferred_form_bound_exact": _fraction_text(transferred),
                "frame_preserves_positive_floor": transferred > 0,
            }
        )
    verification = verify_frame_loss_report(record)
    if not verification["passed"]:
        raise AssertionError(f"frame-loss self-verification failed: {verification}")
    record["independent_exact_verification"] = verification
    return record


def verify_frame_loss_report(record: dict[str, object]) -> dict[str, object]:
    """Reconstruct and verify a standalone finite-frame loss certificate."""
    try:
        if record.get("schema_version") != "oig-finite-frame-loss-v1":
            raise ValueError("unknown frame-loss schema")
        full = rational_matrix(record["full_information_exact"])  # type: ignore[arg-type]
        sensed = rational_matrix(record["sensed_information_exact"])  # type: ignore[arg-type]
        metric = rational_matrix(record["source_metric_exact"])  # type: ignore[arg-type]
        if _shape(full) != _shape(sensed) or _shape(full) != _shape(metric):
            raise ValueError("frame-loss matrices have inconsistent shapes")
        if not _ldl_positive_definite(metric):
            raise ValueError("frame-loss source metric is not positive definite")
        delta = Q(record["frame_loss_upper_exact"])
        if delta <= 0 or not _ldl_positive_definite(
            _subtract(_scale(metric, delta), _subtract(full, sensed))
        ):
            raise ValueError("frame-loss form bound does not verify")
        if record.get("finite_frame_form_bound_certified_by_exact_ldl") is not True:
            raise ValueError("frame-loss theorem flag is inconsistent")
        if "inherited_floor_exact" in record:
            floor = Q(record["inherited_floor_exact"])
            transferred = floor - delta
            if record.get("transferred_form_bound_exact") != _fraction_text(transferred):
                raise ValueError("transferred frame floor is inconsistent")
            if record.get("frame_preserves_positive_floor") is not (transferred > 0):
                raise ValueError("frame positivity flag is inconsistent")
        return {
            "passed": True,
            "method": "independent exact-rational reconstruction of the metric-relative frame-loss form bound",
            "frame_loss_upper_exact": _fraction_text(delta),
        }
    except Exception as error:
        return {"passed": False, "error": str(error)}


__all__ = [
    "QMatrix",
    "QuotientModel",
    "RationalProtocol",
    "certify_frame_loss",
    "design_protocols",
    "exponential_time_response",
    "exact_observable_quotient",
    "information_matrix",
    "rational_matrix",
    "verify_design_report",
    "verify_frame_loss_report",
]
