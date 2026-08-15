#!/usr/bin/env python3
"""Certified two-channel compression of the finite Neumann response field.

The full exactly-centred odd-grid target exposes one whitened output for every
active even target mode.  This module encloses those irrational response rows
with Arb, forms a rational matched sensor frame with only two outputs, and
certifies the information retained for every response in the Arb boxes.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from typing import Sequence

from flint import arb, ctx

from oig_interval_protocol_design import (
    EnclosedProtocol,
    _absolute,
    _response_box_exact_bounds,
    _strict_form_upper,
    _valid_strict_form_upper,
    design_enclosed_protocols,
    response_box_form_bound,
    verify_enclosed_design_report,
)
from oig_protocol_design_engine import (
    QMatrix,
    _fraction_text,
    _inverse,
    _ldl_positive_definite,
    _matmul,
    _matrix_text,
    _primal_lower,
    _scale,
    _shape,
    _subtract,
    _transpose,
    rational_matrix,
)
from oig_xii_two_port_certificate import (
    DEFAULT_TAYLOR_DEGREE,
    _amplitudes_for_target_mode,
    _exact_dyadic_fraction,
    _q,
    _source_ports,
    centered_taylor_operator_tail,
)


Q = Fraction
DEFAULT_SIDE_LENGTH = 345
DEFAULT_PRECISION_BITS = 192


def _identity(dimension: int) -> QMatrix:
    return tuple(
        tuple(Q(int(row == column)) for column in range(dimension))
        for row in range(dimension)
    )


def _diagonal(values: Sequence[Fraction]) -> QMatrix:
    return tuple(
        tuple(value if row == column else Q(0) for column in range(len(values)))
        for row, value in enumerate(values)
    )


def _arb_box(value: arb) -> tuple[Fraction, Fraction]:
    lower = _exact_dyadic_fraction(value.lower())
    upper = _exact_dyadic_fraction(value.upper())
    return (lower + upper) / 2, (upper - lower) / 2


def finite_modal_response_box(
    side_length: int = DEFAULT_SIDE_LENGTH,
    precision_bits: int = DEFAULT_PRECISION_BITS,
    taylor_degree: int = DEFAULT_TAYLOR_DEGREE,
) -> tuple[QMatrix, QMatrix, dict[str, object]]:
    """Enclose every normalized active modal response row at ``tau=1``."""
    if side_length <= 2 or side_length % 2 != 1:
        raise ValueError("side_length must be odd and exceed two")
    if precision_bits < 160:
        raise ValueError("precision_bits must be at least 160")
    if taylor_degree < 24:
        raise ValueError("taylor_degree must be at least 24")
    previous_precision = ctx.prec
    ctx.prec = precision_bits
    try:
        sources = _source_ports(side_length)
        operator_tail = centered_taylor_operator_tail(taylor_degree)
        amplitude_tail = arb(side_length).sqrt() * _q(operator_tail)
        # The complete Gram is sum r_l^T r_l with
        # r_l=sqrt(2 sqrt(2)/n^2) times the unnormalized amplitude row.
        response_scale = (2 * arb(2).sqrt()).sqrt() / side_length
        centres: list[tuple[Fraction, Fraction]] = []
        radii: list[tuple[Fraction, Fraction]] = []
        modes: list[int] = []
        for target_mode in range(2, side_length, 2):
            amplitudes = _amplitudes_for_target_mode(
                side_length,
                target_mode,
                sources,
                taylor_degree,
                amplitude_tail,
            )
            boxes = tuple(_arb_box(response_scale * value) for value in amplitudes)
            centres.append((boxes[0][0], boxes[1][0]))
            radii.append((boxes[0][1], boxes[1][1]))
            modes.append(target_mode)
        return (
            tuple(centres),
            tuple(radii),
            {
                "side_length": side_length,
                "active_even_target_modes": modes,
                "active_mode_count": len(modes),
                "arb_precision_bits": precision_bits,
                "taylor_degree": taylor_degree,
                "operator_tail_exact": _fraction_text(operator_tail),
                "normalization": "each row includes sqrt(2*sqrt(2))/n so R^T R is the complete tau=1 finite Gram",
            },
        )
    finally:
        ctx.prec = previous_precision


def _matched_protocol(
    centre: QMatrix, radius: QMatrix
) -> tuple[EnclosedProtocol, QMatrix, QMatrix]:
    projection_rows = _transpose(centre)
    noise_covariance = _matmul(projection_rows, _transpose(projection_rows))
    noise_precision = _inverse(noise_covariance)
    matched_centre = _matmul(projection_rows, centre)
    matched_radius = _matmul(_absolute(projection_rows), radius)
    protocol = EnclosedProtocol(
        "two-channel rational matched frame",
        matched_centre,
        matched_radius,
        noise_precision,
        Q(1),
    )
    return protocol, projection_rows, noise_covariance


def _second_order_frame_loss_bound(radius: QMatrix, metric: QMatrix) -> dict[str, object]:
    # For P=Rbar^T, the whitened sensor information is the orthogonal
    # projection onto range(Rbar).  Hence the exact loss is
    # Delta^T(I-Pi)Delta <= Delta^T Delta for the actual signed error Delta.
    # Since |Delta x| <= radius |x| entrywise, the diagonal row-sum bound of
    # radius^T radius dominates the resulting quadratic form.  The matrix
    # radius^T radius itself is not asserted to dominate Delta^T Delta in
    # Loewner order.
    quadratic, diagonal = _second_order_frame_loss_matrices(radius)
    delta = _strict_form_upper(diagonal, metric)
    return {
        "radius_quadratic_exact": _matrix_text(quadratic),
        "diagonal_quadratic_bound_exact": _matrix_text(diagonal),
        "metric_relative_frame_loss_upper_exact": _fraction_text(delta),
        "identity": "with Delta=R_true-R_centre, the loss is Delta^T(I-Pi)Delta; |Delta x|<=radius|x| and a diagonal row-sum bound of radius^T radius controls it",
    }


def _second_order_frame_loss_matrices(
    radius: QMatrix,
) -> tuple[QMatrix, QMatrix]:
    """Return the deterministic quadratic and diagonal frame-loss bounds."""
    quadratic = _matmul(_transpose(radius), radius)
    row_sums = tuple(sum(row, Q(0)) for row in quadratic)
    return quadratic, _diagonal(row_sums)


def _metric_record(
    name: str,
    metric: QMatrix,
    full: EnclosedProtocol,
    matched: EnclosedProtocol,
    radius: QMatrix,
    *,
    weight_denominator: int,
) -> dict[str, object]:
    full_centre_gram = _matmul(_transpose(full.response_centre), full.response_centre)
    nominal_full_lower = _primal_lower(full_centre_gram, metric)
    full_box = response_box_form_bound(full, metric)
    full_error = Q(full_box["metric_relative_information_error_upper_exact"])
    full_robust_lower = nominal_full_lower - full_error
    frame_loss = _second_order_frame_loss_bound(radius, metric)
    frame_delta = Q(frame_loss["metric_relative_frame_loss_upper_exact"])
    inherited_matched_lower = full_robust_lower - frame_delta
    direct = design_enclosed_protocols(
        [matched],
        metric,
        weight_denominator=weight_denominator,
        amplitude=1,
        exposure_multiplier=100,
    )
    direct_robust = Q(
        direct["response_box_robustness"]["robust_physical_floor_lower_exact"]
    )
    result = {
        "metric": name,
        "source_metric_exact": _matrix_text(metric),
        "nominal_complete_modal_floor_lower_exact": _fraction_text(
            nominal_full_lower
        ),
        "complete_response_box_error_upper_exact": _fraction_text(full_error),
        "robust_complete_modal_floor_lower_exact": _fraction_text(
            full_robust_lower
        ),
        "matched_frame_loss_certificate": frame_loss,
        "inherited_two_channel_floor_lower_exact": _fraction_text(
            inherited_matched_lower
        ),
        "direct_two_channel_enclosed_design": direct,
        "direct_two_channel_robust_floor_lower_exact": _fraction_text(direct_robust),
        "passed": bool(
            full_robust_lower > 0
            and inherited_matched_lower > 0
            and direct_robust > 0
            and verify_enclosed_design_report(direct)["passed"]
        ),
    }
    return result


def run_matched_frame_certificate(
    side_length: int = DEFAULT_SIDE_LENGTH,
    precision_bits: int = DEFAULT_PRECISION_BITS,
    taylor_degree: int = DEFAULT_TAYLOR_DEGREE,
    weight_denominator: int = 100_000,
) -> dict[str, object]:
    centre, radius, trace = finite_modal_response_box(
        side_length, precision_bits, taylor_degree
    )
    full = EnclosedProtocol(
        "complete whitened modal field",
        centre,
        radius,
        _identity(len(centre)),
        Q(1),
    )
    matched, projection_rows, covariance = _matched_protocol(centre, radius)
    metrics = (
        ("L2", rational_matrix([[1, 0], [0, 1]])),
        (
            "rational H1 majorant",
            rational_matrix([[11, 0], [0, 41]]),
        ),
    )
    records = [
        _metric_record(
            name,
            metric,
            full,
            matched,
            radius,
            weight_denominator=weight_denominator,
        )
        for name, metric in metrics
    ]
    result = {
        "schema_version": "oig-neumann-matched-frame-v1",
        "status": "rigorous Arb-to-rational two-channel finite-sensor certificate",
        "model": trace,
        "full_modal_response_centre_exact": _matrix_text(centre),
        "full_modal_response_radius_exact": _matrix_text(radius),
        "matched_sensor_rows_exact": _matrix_text(projection_rows),
        "matched_sensor_noise_covariance_exact": _matrix_text(covariance),
        "matched_response_centre_exact": _matrix_text(matched.response_centre),
        "matched_response_radius_exact": _matrix_text(matched.response_radius),
        "metric_certificates": records,
        "metric_note": (
            "S=diag(11,41) is a rational upper majorant of both the declared continuum H1 metric "
            "and the natural finite two-mode energy metric, since 4 n^2 sin^2(k pi/(2n)) <= (k pi)^2."
        ),
        "scope_boundary": (
            "The theorem concerns the declared K=2, tau=1, exactly-centred odd-grid model and "
            "two global matched linear sensors. It does not assert locality, hardware realizability, "
            "or robustness to dynamics outside the Arb response boxes."
        ),
        "overall_passed": all(record["passed"] for record in records),
    }
    verification = verify_neumann_matched_frame_report(result)
    if not verification["passed"]:
        raise AssertionError(f"matched-frame self-verification failed: {verification}")
    result["independent_exact_verification"] = verification
    return result


def verify_neumann_matched_frame_report(
    report: dict[str, object],
) -> dict[str, object]:
    """Reconstruct every rational matched-frame and floor-transfer field."""
    try:
        if report.get("schema_version") != "oig-neumann-matched-frame-v1":
            raise ValueError("unknown matched-frame schema")
        centre = rational_matrix(report["full_modal_response_centre_exact"])
        radius = rational_matrix(report["full_modal_response_radius_exact"])
        if _shape(centre) != _shape(radius):
            raise ValueError("full response centre and radius shapes differ")
        if any(value < 0 for row in radius for value in row):
            raise ValueError("a full response radius is negative")
        projection = rational_matrix(report["matched_sensor_rows_exact"])
        if projection != _transpose(centre):
            raise ValueError("matched sensor rows do not reproduce")
        covariance = rational_matrix(report["matched_sensor_noise_covariance_exact"])
        expected_covariance = _matmul(projection, _transpose(projection))
        if covariance != expected_covariance:
            raise ValueError("matched sensor covariance does not reproduce")
        matched_centre = _matmul(projection, centre)
        matched_radius = _matmul(_absolute(projection), radius)
        if _matrix_text(matched_centre) != report["matched_response_centre_exact"]:
            raise ValueError("matched response centre does not reproduce")
        if _matrix_text(matched_radius) != report["matched_response_radius_exact"]:
            raise ValueError("matched response radius does not reproduce")
        full = EnclosedProtocol(
            "complete whitened modal field",
            centre,
            radius,
            _identity(len(centre)),
            Q(1),
        )
        matched = EnclosedProtocol(
            "two-channel rational matched frame",
            matched_centre,
            matched_radius,
            _inverse(covariance),
            Q(1),
        )
        records = report["metric_certificates"]
        if not isinstance(records, list) or not records:
            raise ValueError("metric certificates are missing")
        decisions: list[bool] = []
        for record in records:
            metric = rational_matrix(record["source_metric_exact"])
            full_gram = _matmul(_transpose(centre), centre)
            nominal = Q(record["nominal_complete_modal_floor_lower_exact"])
            if nominal <= 0 or not _ldl_positive_definite(
                _subtract(full_gram, _scale(metric, nominal))
            ):
                raise ValueError(
                    "nominal complete floor fails exact LDL verification"
                )
            _, _, full_diagonal_bound = _response_box_exact_bounds(full, metric)
            full_error = Q(record["complete_response_box_error_upper_exact"])
            if not _valid_strict_form_upper(
                full_diagonal_bound, metric, full_error
            ):
                raise ValueError(
                    "complete response-box upper fails exact LDL verification"
                )
            full_robust = nominal - full_error
            if record["robust_complete_modal_floor_lower_exact"] != _fraction_text(full_robust):
                raise ValueError("robust complete floor does not reproduce")
            reported_frame = record["matched_frame_loss_certificate"]
            frame_quadratic, frame_diagonal = _second_order_frame_loss_matrices(
                radius
            )
            if reported_frame["radius_quadratic_exact"] != _matrix_text(
                frame_quadratic
            ):
                raise ValueError("matched-frame quadratic does not reproduce")
            if reported_frame["diagonal_quadratic_bound_exact"] != _matrix_text(
                frame_diagonal
            ):
                raise ValueError(
                    "matched-frame diagonal bound does not reproduce"
                )
            frame_delta = Q(
                reported_frame["metric_relative_frame_loss_upper_exact"]
            )
            if not _valid_strict_form_upper(
                frame_diagonal, metric, frame_delta
            ):
                raise ValueError(
                    "matched-frame form upper fails exact LDL verification"
                )
            inherited = full_robust - frame_delta
            if record["inherited_two_channel_floor_lower_exact"] != _fraction_text(inherited):
                raise ValueError("inherited two-channel floor does not reproduce")
            direct = record["direct_two_channel_enclosed_design"]
            direct_verification = verify_enclosed_design_report(direct)
            if not direct_verification["passed"]:
                raise ValueError("nested two-channel design does not verify")
            direct_box = direct["response_box_robustness"][
                "protocol_response_box_certificates"
            ][0]
            if direct_box["response_centre_exact"] != _matrix_text(matched.response_centre):
                raise ValueError("nested matched centre differs from the outer frame")
            if direct_box["response_radius_exact"] != _matrix_text(matched.response_radius):
                raise ValueError("nested matched radius differs from the outer frame")
            if direct_box["noise_precision_exact"] != _matrix_text(matched.noise_precision):
                raise ValueError("nested matched precision differs from the outer frame")
            direct_floor = direct["response_box_robustness"][
                "robust_physical_floor_lower_exact"
            ]
            if record["direct_two_channel_robust_floor_lower_exact"] != direct_floor:
                raise ValueError("direct two-channel floor is inconsistent")
            passed = bool(
                full_robust > 0
                and inherited > 0
                and Q(direct_floor) > 0
            )
            if type(record.get("passed")) is not bool or record["passed"] is not passed:
                raise ValueError("a metric pass flag is inconsistent")
            decisions.append(passed)
        if type(report.get("overall_passed")) is not bool or report["overall_passed"] is not all(decisions):
            raise ValueError("overall matched-frame flag is inconsistent")
        return {
            "passed": all(decisions),
            "method": "independent exact-rational reconstruction of matched sensors, covariance, response boxes, frame loss, and both metric floors",
            "metric_count": len(decisions),
        }
    except Exception as error:
        return {"passed": False, "error": str(error)}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--side-length", type=int, default=DEFAULT_SIDE_LENGTH)
    parser.add_argument("--precision-bits", type=int, default=DEFAULT_PRECISION_BITS)
    parser.add_argument("--taylor-degree", type=int, default=DEFAULT_TAYLOR_DEGREE)
    parser.add_argument("--weight-denominator", type=int, default=100_000)
    parser.add_argument("--output")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = run_matched_frame_certificate(
        args.side_length,
        args.precision_bits,
        args.taylor_degree,
        args.weight_denominator,
    )
    payload = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.write("\n")
    else:
        print(payload)
    return 0 if report["overall_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
