"""Robust exact design for entrywise-enclosed irrational response maps.

An ``EnclosedProtocol`` declares a rational centre ``R`` and a nonnegative
rational radius matrix ``E``.  The physical response may be any
``R_true`` satisfying ``|R_true-R| <= E`` entrywise.  The module turns this
box into a metric-relative information-form error and attaches it to the
exact rational protocol-design certificate.

The box bound is deliberately elementary and outward: no floating-point
quantity decides a theorem field.  Numerical generalized eigensolvers only
propose rational form bounds, which exact LDL elimination then verifies.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from scipy.linalg import eigh

from oig_protocol_design_engine import (
    ExactScalar,
    QMatrix,
    RationalProtocol,
    _add,
    _float_matrix,
    _fraction_text,
    _ldl_positive_definite,
    _matmul,
    _matrix_text,
    _q,
    _scale,
    _shape,
    _subtract,
    _transpose,
    design_protocols,
    rational_matrix,
    verify_design_report,
)


Q = Fraction


def _absolute(matrix: QMatrix) -> QMatrix:
    return tuple(tuple(abs(value) for value in row) for row in matrix)


def _diagonal(values: Sequence[Fraction]) -> QMatrix:
    return tuple(
        tuple(value if row == column else Q(0) for column in range(len(values)))
        for row, value in enumerate(values)
    )


def _zero(matrix: QMatrix) -> bool:
    return all(value == 0 for row in matrix for value in row)


def _strict_form_upper(bound: QMatrix, metric: QMatrix) -> Fraction:
    """Find an exact ``delta`` with ``bound < delta*metric``.

    Floating point proposes the scale.  Exact rational LDL is the only
    acceptance test.  The exact-zero bound is returned as zero.
    """
    if _zero(bound):
        return Q(0)
    proposal = float(
        eigh(_float_matrix(bound), _float_matrix(metric), eigvals_only=True)[-1]
    )
    candidate = Q(str(max(proposal, 0.0) * 1.001 + 1e-300)).limit_denominator(
        10**80
    )
    for _ in range(256):
        if candidate > 0 and _ldl_positive_definite(
            _subtract(_scale(metric, candidate), bound)
        ):
            return candidate
        candidate = 2 * candidate if candidate else Q(1, 10**80)
    raise ArithmeticError("could not certify the response-box form bound")


@dataclass(frozen=True)
class EnclosedProtocol:
    """A response protocol with an exact rational entrywise enclosure."""

    name: str
    response_centre: QMatrix
    response_radius: QMatrix
    noise_precision: QMatrix
    cost: Fraction = Q(1)

    @classmethod
    def from_rows(
        cls,
        name: str,
        response_centre: Sequence[Sequence[ExactScalar]],
        response_radius: Sequence[Sequence[ExactScalar]],
        noise_precision: Sequence[Sequence[ExactScalar]],
        cost: ExactScalar = 1,
    ) -> "EnclosedProtocol":
        return cls(
            name,
            rational_matrix(response_centre),
            rational_matrix(response_radius),
            rational_matrix(noise_precision),
            _q(cost),
        )

    def nominal(self) -> RationalProtocol:
        return RationalProtocol(
            self.name, self.response_centre, self.noise_precision, self.cost
        )


def response_box_form_bound(
    protocol: EnclosedProtocol,
    source_metric: Sequence[Sequence[ExactScalar]],
) -> dict[str, object]:
    """Certify ``|A_true-A_centre| <= delta*S`` as quadratic forms.

    If ``D=R_true-R`` and ``|D|<=E``, then entrywise

    ``|A_true-A| <= |R|^T|W|E + E^T|W||R| + E^T|W|E = B``.

    The diagonal matrix whose entries are the row sums of the symmetric
    nonnegative matrix ``B`` dominates ``|x|^T B |x|`` by
    ``2|x_i x_j| <= x_i^2+x_j^2``.  The final metric-relative comparison is
    verified by exact rational LDL.
    """
    metric = rational_matrix(source_metric)
    rows, columns = _shape(protocol.response_centre)
    if _shape(protocol.response_radius) != (rows, columns):
        raise ValueError("response centre and radius shapes differ")
    if any(value < 0 for row in protocol.response_radius for value in row):
        raise ValueError("response radii must be nonnegative")
    if _shape(metric) != (columns, columns):
        raise ValueError("source metric has the wrong dimension")
    nominal = protocol.nominal()
    # This validates cost, output dimension, and positive noise precision.
    from oig_protocol_design_engine import information_matrix

    information_matrix(nominal)
    if not _ldl_positive_definite(metric):
        raise ValueError("source metric must be positive definite")

    centre_abs = _absolute(protocol.response_centre)
    radius = protocol.response_radius
    precision_abs = _absolute(protocol.noise_precision)
    cross = _matmul(
        _transpose(centre_abs), _matmul(precision_abs, radius)
    )
    quadratic = _matmul(_transpose(radius), _matmul(precision_abs, radius))
    entry_bound = _add(_add(cross, _transpose(cross)), quadratic)
    row_sums = tuple(sum(row, Q(0)) for row in entry_bound)
    diagonal_bound = _diagonal(row_sums)
    delta = _strict_form_upper(diagonal_bound, metric)
    return {
        "schema_version": "oig-response-box-form-bound-v1",
        "response_centre_exact": _matrix_text(protocol.response_centre),
        "response_radius_exact": _matrix_text(protocol.response_radius),
        "noise_precision_exact": _matrix_text(protocol.noise_precision),
        "source_metric_exact": _matrix_text(metric),
        "entrywise_information_bound_exact": _matrix_text(entry_bound),
        "diagonal_quadratic_bound_exact": _matrix_text(diagonal_bound),
        "metric_relative_information_error_upper_exact": _fraction_text(delta),
        "exact_ldl_decision": True,
        "meaning": "for every enclosed response, -delta*S <= A_true-A_centre <= delta*S",
    }


def _noise_upper(floor: Fraction, amplitude: Fraction, exposure: int) -> Fraction:
    if floor <= 0:
        raise ValueError("a robust noise bound requires a positive floor")
    return Q(4, 1) / (Q(8, 1) + exposure * amplitude * amplitude * floor)


def design_enclosed_protocols(
    protocols: Sequence[EnclosedProtocol],
    source_metric: Sequence[Sequence[ExactScalar]],
    *,
    weight_denominator: int = 100_000,
    dual_vector_scale: int = 10**8,
    amplitude: ExactScalar = 1,
    exposure_multiplier: int = 100,
) -> dict[str, object]:
    """Design nominal protocols and transfer the certificate to every box.

    The current robust wrapper requires no common blind direction in the
    nominal finite source coordinates.  Exact structural quotients remain
    available through ``design_protocols`` itself, but uncertain activation
    of a nominally blind direction is a different robust-quotient problem.
    """
    if not protocols:
        raise ValueError("at least one enclosed protocol is required")
    metric = rational_matrix(source_metric)
    nominal = tuple(protocol.nominal() for protocol in protocols)
    report = design_protocols(
        nominal,
        metric,
        weight_denominator=weight_denominator,
        dual_vector_scale=dual_vector_scale,
        amplitude=amplitude,
        exposure_multiplier=exposure_multiplier,
    )
    if report["exact_blind_dimension"] != 0:
        raise ValueError(
            "robust response-box transfer currently requires a full-rank nominal source frame"
        )

    bounds = tuple(response_box_form_bound(protocol, metric) for protocol in protocols)
    shares = tuple(Q(row["budget_share_exact"]) for row in report["protocols"])
    costs = tuple(protocol.cost for protocol in protocols)
    deltas = tuple(
        Q(bound["metric_relative_information_error_upper_exact"])
        for bound in bounds
    )
    aggregate = sum(
        (share * delta / cost for share, delta, cost in zip(shares, deltas, costs)),
        Q(0),
    )
    nominal_lower = Q(report["certificate"]["primal_generalized_floor_lower_exact"])
    robust_lower = nominal_lower - aggregate
    exact_amplitude = _q(amplitude)
    robust_block: dict[str, object] = {
        "schema_version": "oig-enclosed-protocol-design-v1",
        "protocol_response_box_certificates": list(bounds),
        "aggregate_metric_relative_information_error_upper_exact": _fraction_text(
            aggregate
        ),
        "nominal_floor_lower_exact": _fraction_text(nominal_lower),
        "robust_physical_floor_lower_exact": _fraction_text(robust_lower),
        "robust_floor_is_positive": robust_lower > 0,
        "proof_boundary": (
            "The robust floor holds for every response in the declared entrywise rational boxes. "
            "It does not certify that an external numerical model lies in those boxes."
        ),
    }
    if robust_lower > 0:
        realization = report["noise_performance"]["integer_realization"]
        realized_exposure = realization["realized_budget_multiplier"]
        robust_block["robust_noise_performance"] = {
            "amplitude_exact": _fraction_text(exact_amplitude),
            "continuous_exposure_gaussian_error_rational_upper_exact": _fraction_text(
                _noise_upper(robust_lower, exact_amplitude, exposure_multiplier)
            ),
            "integer_realization_exposure": realized_exposure,
            "integer_realization_gaussian_error_rational_upper_exact": _fraction_text(
                _noise_upper(robust_lower, exact_amplitude, realized_exposure)
            ),
        }
    report["response_box_robustness"] = robust_block
    verification = verify_enclosed_design_report(report)
    if not verification["passed"]:
        raise AssertionError(f"enclosed-design self-verification failed: {verification}")
    report["response_box_independent_verification"] = verification
    return report


def verify_enclosed_design_report(report: dict[str, object]) -> dict[str, object]:
    """Independently reconstruct the exact response-box transfer fields."""
    try:
        base = verify_design_report(report)
        if not base["passed"]:
            raise ValueError("the embedded nominal design certificate fails")
        robust = report["response_box_robustness"]
        if robust["schema_version"] != "oig-enclosed-protocol-design-v1":
            raise ValueError("unknown response-box design schema")
        metric = rational_matrix(report["declared_source_metric"])
        rows = report["protocols"]
        bound_rows = robust["protocol_response_box_certificates"]
        if len(rows) != len(bound_rows):
            raise ValueError("response-box certificate count is inconsistent")
        deltas: list[Fraction] = []
        shares: list[Fraction] = []
        costs: list[Fraction] = []
        for row, bound in zip(rows, bound_rows):
            if bound.get("schema_version") != "oig-response-box-form-bound-v1":
                raise ValueError("unknown response-box certificate schema")
            if bound.get("exact_ldl_decision") is not True:
                raise ValueError("response-box LDL decision flag is inconsistent")
            if bound["response_centre_exact"] != row["response_exact"]:
                raise ValueError("response-box centre differs from the nominal protocol")
            if bound["noise_precision_exact"] != row["noise_precision_exact"]:
                raise ValueError("response-box precision differs from the nominal protocol")
            enclosure = EnclosedProtocol.from_rows(
                str(row["name"]),
                bound["response_centre_exact"],
                bound["response_radius_exact"],
                bound["noise_precision_exact"],
                row["cost_exact"],
            )
            if bound["source_metric_exact"] != _matrix_text(metric):
                raise ValueError("response-box metric differs from the design metric")
            rebuilt = response_box_form_bound(enclosure, metric)
            for field in (
                "entrywise_information_bound_exact",
                "diagonal_quadratic_bound_exact",
                "metric_relative_information_error_upper_exact",
            ):
                if rebuilt[field] != bound[field]:
                    raise ValueError(f"response-box field {field} does not reproduce")
            deltas.append(Q(bound["metric_relative_information_error_upper_exact"]))
            shares.append(Q(row["budget_share_exact"]))
            costs.append(Q(row["cost_exact"]))
        aggregate = sum(
            (share * delta / cost for share, delta, cost in zip(shares, deltas, costs)),
            Q(0),
        )
        nominal = Q(report["certificate"]["primal_generalized_floor_lower_exact"])
        physical = nominal - aggregate
        if robust["aggregate_metric_relative_information_error_upper_exact"] != _fraction_text(aggregate):
            raise ValueError("aggregate response-box error does not reproduce")
        if robust["nominal_floor_lower_exact"] != _fraction_text(nominal):
            raise ValueError("nominal robust-design floor is inconsistent")
        if robust["robust_physical_floor_lower_exact"] != _fraction_text(physical):
            raise ValueError("robust physical floor does not reproduce")
        if robust["robust_floor_is_positive"] is not (physical > 0):
            raise ValueError("robust floor flag is inconsistent")
        noise = robust.get("robust_noise_performance")
        if physical > 0:
            if not isinstance(noise, dict):
                raise ValueError("positive robust floor lacks a robust noise certificate")
            amplitude = Q(noise["amplitude_exact"])
            approximate_exposure = report["noise_performance"][
                "approximate_design_measure"
            ]["continuous_budget_exposure_multiplier"]
            realized_exposure = report["noise_performance"]["integer_realization"][
                "realized_budget_multiplier"
            ]
            if type(approximate_exposure) is not int or type(realized_exposure) is not int:
                raise ValueError("robust noise exposures must be JSON integers")
            if noise["integer_realization_exposure"] != realized_exposure:
                raise ValueError("robust integer exposure is inconsistent")
            if noise["continuous_exposure_gaussian_error_rational_upper_exact"] != _fraction_text(
                _noise_upper(physical, amplitude, approximate_exposure)
            ):
                raise ValueError("robust continuous-exposure noise bound is inconsistent")
            if noise["integer_realization_gaussian_error_rational_upper_exact"] != _fraction_text(
                _noise_upper(physical, amplitude, realized_exposure)
            ):
                raise ValueError("robust integer-realization noise bound is inconsistent")
        elif noise is not None:
            raise ValueError("nonpositive robust floor cannot carry a robust noise bound")
        return {
            "passed": True,
            "method": "independent exact-rational reconstruction of every response box and the aggregate robust floor",
            "robust_physical_floor_lower_exact": _fraction_text(physical),
        }
    except Exception as error:
        return {"passed": False, "error": str(error)}


__all__ = [
    "EnclosedProtocol",
    "design_enclosed_protocols",
    "response_box_form_bound",
    "verify_enclosed_design_report",
]
