#!/usr/bin/env python3
"""Proof-producing two-port finite-Neumann transfer at ``tau=1``.

This checker treats the *actual* cell-centred Neumann generator

    A_{n,l} = L_n + omega_{n,l} V_n,

so the noncommuting diffusion--modulation words are retained.  It does not
form a large floating-point matrix exponential.  Instead, for every target
mode it evaluates a centred Taylor polynomial with Arb ball arithmetic and
adds a proved operator-norm tail.

The certificate is intentionally local: two cosine source ports, the
one-cell lattice chart point ``tau=1``, modulation ``V(x)=1+4x/5``, and the
exactly centred atomic target on odd grids.  It is not a uniform statement
over the late chart or the full OIG atlas.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import sys
from fractions import Fraction

from flint import arb, ctx, fmpq

from oig_xi_transfer_certificate import (
    STAGE_X_LOWER_BOUNDS,
    continuum_lattice_gram,
)


INTERACTION_STRENGTH = Fraction(4, 5)
LATTICE_TIME = Fraction(1, 1)
BAND_DIMENSION = 2
DEFAULT_PRECISION_BITS = 256
DEFAULT_TAYLOR_DEGREE = 32
FAILED_ODD_PREDECESSOR = 343
CERTIFIED_ODD_GRID = 345
FAILED_H1_ODD_PREDECESSOR = 647
CERTIFIED_H1_ODD_GRID = 649

# A rational vector close to the negative eigendirection at n=343.  Its
# Rayleigh quotient proves that the predecessor's true spectral error is
# larger than the inherited Stage X floor; this is stronger than merely
# observing that an upper-bound test did not pass.
PREDECESSOR_RAYLEIGH_VECTOR = (4, 1)
H1_PREDECESSOR_RAYLEIGH_VECTOR = (8, 1)


def _q(value: Fraction | int) -> arb:
    if isinstance(value, int):
        return arb(value)
    return arb(fmpq(value.numerator, value.denominator))


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _exact_dyadic_fraction(value: arb) -> Fraction:
    """Convert an exact Arb endpoint to the represented dyadic rational."""
    if not bool(value.rad() == 0):
        raise ValueError("expected an exact Arb endpoint")
    mantissa, exponent = map(int, value.man_exp())
    if exponent >= 0:
        return Fraction(mantissa * 2**exponent, 1)
    return Fraction(mantissa, 2 ** (-exponent))


def _symmetric_error_radius(radius: arb) -> arb:
    """Return an outward interval containing ``[-radius, radius]``."""
    if not bool(radius >= 0):
        raise ArithmeticError("a remainder radius became negative")
    return arb.union(-radius, radius)


def centered_taylor_operator_tail(degree: int) -> Fraction:
    """Uniform operator tail for every target mode.

    The path Laplacian obeys ``0 <= L_n <= 4 I`` and
    ``I <= V_n <= (9/5) I``.  For ``0 <= omega <= 4``, put

        c = 2 + (7/5) omega,    B = A-cI.

    Then ``||B|| <= rho = 2+(2/5)omega <= 18/5``.  Taylor's theorem gives

        ||e^{-A} - e^{-c} sum_{r=0}^m (-B)^r/r!||
        <= e^{-c} e^rho rho^(m+1)/(m+1)!
        =  e^{-omega} rho^(m+1)/(m+1)!
        <= (18/5)^(m+1)/(m+1)!.

    The returned number is exact and rational.
    """
    if degree < 1:
        raise ValueError("Taylor degree must be positive")
    return Fraction(18, 5) ** (degree + 1) / math.factorial(degree + 1)


def _source_ports(side_length: int) -> tuple[list[arb], list[arb]]:
    """The two exact DCT cosine ports, enclosed entry by entry by Arb."""
    scale = (arb(2) / side_length).sqrt()
    first: list[arb] = []
    second: list[arb] = []
    for cell in range(side_length):
        x = _q(Fraction(2 * cell + 1, 2 * side_length))
        first.append(scale * (arb.pi() * x).cos())
        second.append(scale * (2 * arb.pi() * x).cos())
    return first, second


def _amplitudes_for_target_mode(
    side_length: int,
    target_mode: int,
    sources: tuple[list[arb], list[arb]],
    degree: int,
    amplitude_tail: arb,
) -> tuple[arb, arb]:
    """Enclose ``1^T exp(-A_{n,l}) u_k`` for ``k=1,2``.

    Every polynomial operation is performed in Arb.  The only analytic
    remainder is the symmetric interval ``amplitude_tail``, obtained from
    the exact operator tail and ``||1||_2=sqrt(n)``, ``||u_k||_2=1``.
    """
    n = side_length
    omega = 4 * (arb.pi() * target_mode / (2 * n)).sin() ** 2
    centre = 2 + _q(Fraction(7, 5)) * omega

    state0 = list(sources[0])
    state1 = list(sources[1])
    total0 = list(state0)
    total1 = list(state1)

    diagonal: list[arb] = []
    for cell in range(n):
        laplacian_diagonal = 1 if cell in (0, n - 1) else 2
        x = _q(Fraction(2 * cell + 1, 2 * n))
        modulation = 1 + _q(INTERACTION_STRENGTH) * x
        diagonal.append(laplacian_diagonal + omega * modulation - centre)

    # If ``state`` is (-B)^(r-1)u/(r-1)!, the update below is
    # (-B)^r u/r!.  B is tridiagonal with off-diagonal entries -1.
    for order in range(1, degree + 1):
        next0: list[arb] = []
        next1: list[arb] = []
        for cell in range(n):
            value0 = -diagonal[cell] * state0[cell]
            value1 = -diagonal[cell] * state1[cell]
            if cell:
                value0 += state0[cell - 1]
                value1 += state1[cell - 1]
            if cell + 1 < n:
                value0 += state0[cell + 1]
                value1 += state1[cell + 1]
            next0.append(value0 / order)
            next1.append(value1 / order)
        for cell in range(n):
            total0[cell] += next0[cell]
            total1[cell] += next1[cell]
        state0, state1 = next0, next1

    exponential_centre = (-centre).exp()
    amplitude0 = exponential_centre * sum(total0, arb(0))
    amplitude1 = exponential_centre * sum(total1, arb(0))
    remainder_ball = _symmetric_error_radius(amplitude_tail)
    return amplitude0 + remainder_ball, amplitude1 + remainder_ball


def finite_neumann_two_port_gram(
    side_length: int,
    degree: int = DEFAULT_TAYLOR_DEGREE,
) -> tuple[list[list[arb]], dict[str, object]]:
    """Enclose the complete two-port finite Gram on an odd centred grid."""
    if side_length <= BAND_DIMENSION or side_length % 2 != 1:
        raise ValueError("side_length must be odd and exceed two")
    if degree < 1:
        raise ValueError("Taylor degree must be positive")

    n = side_length
    sources = _source_ports(n)
    operator_tail = centered_taylor_operator_tail(degree)
    # Keep the square root in Arb, but the underlying operator tail itself is
    # the exact rational returned above.
    amplitude_tail_ball = arb(n).sqrt() * _q(operator_tail)

    gram00 = arb(0)
    gram01 = arb(0)
    gram11 = arb(0)

    # For odd n the target cell is exactly x=1/2.  Hence beta_l=0 for odd l
    # and beta_l^2=2/n for even l.  Applying these identities exactly both
    # reduces work and avoids asking a transcendental enclosure to rediscover
    # a symbolic zero.
    for target_mode in range(2, n, 2):
        amplitude0, amplitude1 = _amplitudes_for_target_mode(
            n,
            target_mode,
            sources,
            degree,
            amplitude_tail_ball,
        )
        gram00 += amplitude0 * amplitude0
        gram01 += amplitude0 * amplitude1
        gram11 += amplitude1 * amplitude1

    coefficient = 2 * arb(2).sqrt() / (n * n)
    gram = [
        [coefficient * gram00, coefficient * gram01],
        [coefficient * gram01, coefficient * gram11],
    ]
    trace = {
        "side_length": n,
        "target_modes_retained": (n - 1) // 2,
        "target_mode_parity": "even only; odd modes vanish exactly at x=1/2",
        "taylor_degree": degree,
        "operator_tail_exact": _fraction_text(operator_tail),
        "operator_tail_approx": float(operator_tail),
        "amplitude_tail_interval": amplitude_tail_ball.str(
            24, radius=True, more=True
        ),
    }
    return gram, trace


def symmetric_two_by_two_spectral_bound(
    finite: list[list[arb]], continuum, metric: str = "L2"
) -> tuple[arb, list[list[arb]], tuple[arb, arb]]:
    """Return a rigorous upper bound for the whitened symmetric 2x2 error."""
    raw_error = [
        [finite[row][column] - continuum[row, column] for column in range(2)]
        for row in range(2)
    ]
    if metric == "L2":
        metric_diagonal = (arb(1), arb(1))
    elif metric == "H1":
        metric_diagonal = (
            1 + arb.pi() ** 2,
            1 + (2 * arb.pi()) ** 2,
        )
    else:
        raise ValueError("metric must be L2 or H1")
    error = [
        [
            raw_error[row][column]
            / (metric_diagonal[row] * metric_diagonal[column]).sqrt()
            for column in range(2)
        ]
        for row in range(2)
    ]
    a = error[0][0]
    b = (error[0][1] + error[1][0]) / 2
    d = error[1][1]
    discriminant = ((a - d) ** 2 + 4 * b**2).sqrt()
    eigenvalues = ((a + d - discriminant) / 2, (a + d + discriminant) / 2)
    upper_candidates = [
        _exact_dyadic_fraction(value.abs_upper()) for value in eigenvalues
    ]
    selected = max(upper_candidates)
    return _q(selected), error, eigenvalues


def predecessor_rayleigh_lower(
    error: list[list[arb]], vector: tuple[int, int] = PREDECESSOR_RAYLEIGH_VECTOR
) -> arb:
    """Lower-bound ``|v^T E v|/(v^T v)`` for the fixed rational vector."""
    x, y = vector
    quotient = -(
        x * x * error[0][0]
        + x * y * (error[0][1] + error[1][0])
        + y * y * error[1][1]
    ) / (x * x + y * y)
    return quotient


def absolute_row_sum_upper(error: list[list[arb]]) -> Fraction:
    """Exact dyadic upper endpoint of the interval absolute-row-sum bound."""
    candidates: list[Fraction] = []
    for row in error:
        candidates.append(
            sum(
                (_exact_dyadic_fraction(entry.abs_upper()) for entry in row),
                Fraction(0),
            )
        )
    return max(candidates)


def absolute_entry_max_upper(error: list[list[arb]]) -> Fraction:
    """Exact dyadic upper endpoint of the largest interval-entry magnitude."""
    return max(
        _exact_dyadic_fraction(entry.abs_upper())
        for row in error
        for entry in row
    )


def _gram_intervals(gram: list[list[arb]]) -> list[list[str]]:
    return [
        [entry.str(28, radius=True, more=True) for entry in row] for row in gram
    ]


def _metric_certificate(
    metric: str,
    predecessor: int,
    successful_grid: int,
    rayleigh_vector: tuple[int, int],
    continuum,
    taylor_degree: int,
) -> dict[str, object]:
    """Build one metric-relative predecessor/success enclosure pair."""
    floor = STAGE_X_LOWER_BOUNDS[metric][BAND_DIMENSION - 1]

    predecessor_gram, predecessor_trace = finite_neumann_two_port_gram(
        predecessor, taylor_degree
    )
    predecessor_upper, predecessor_error, predecessor_eigenvalues = (
        symmetric_two_by_two_spectral_bound(
            predecessor_gram, continuum, metric
        )
    )
    rayleigh = predecessor_rayleigh_lower(predecessor_error, rayleigh_vector)
    rayleigh_lower = _exact_dyadic_fraction(rayleigh.lower())
    predecessor_rejected = bool(rayleigh > _q(floor))
    predecessor_row_sum = absolute_row_sum_upper(predecessor_error)
    predecessor_entry_max = absolute_entry_max_upper(predecessor_error)

    success_gram, success_trace = finite_neumann_two_port_gram(
        successful_grid, taylor_degree
    )
    success_upper_ball, success_error, success_eigenvalues = (
        symmetric_two_by_two_spectral_bound(success_gram, continuum, metric)
    )
    success_upper = _exact_dyadic_fraction(success_upper_ball.upper())
    success = bool(success_upper_ball < _q(floor))
    transferred_floor = floor - success_upper
    success_row_sum = absolute_row_sum_upper(success_error)

    records = [
        {
            **predecessor_trace,
            "role": "rigorously rejected immediate odd-grid predecessor",
            "spectral_norm_upper_exact": _fraction_text(
                _exact_dyadic_fraction(predecessor_upper.upper())
            ),
            "spectral_norm_upper_approx": float(predecessor_upper.upper()),
            "rayleigh_vector": list(rayleigh_vector),
            "rayleigh_abs_lower_exact": _fraction_text(rayleigh_lower),
            "rayleigh_abs_lower_approx": float(rayleigh_lower),
            "rayleigh_strictly_above_stage_x_floor": predecessor_rejected,
            "absolute_row_sum_upper_exact": _fraction_text(predecessor_row_sum),
            "absolute_row_sum_upper_approx": float(predecessor_row_sum),
            "absolute_entry_max_upper_exact": _fraction_text(
                predecessor_entry_max
            ),
            "absolute_entry_max_upper_approx": float(predecessor_entry_max),
            "entrywise_max_would_false_certify": bool(
                predecessor_entry_max < floor and predecessor_rejected
            ),
            "error_gram_intervals": _gram_intervals(predecessor_error),
            "eigenvalue_intervals": [
                value.str(28, radius=True, more=True)
                for value in predecessor_eigenvalues
            ],
        },
        {
            **success_trace,
            "role": "rigorously certified two-port finite transfer",
            "spectral_norm_upper_exact": _fraction_text(success_upper),
            "spectral_norm_upper_approx": float(success_upper),
            "strictly_below_stage_x_floor": success,
            "transferred_finite_floor_exact": _fraction_text(transferred_floor),
            "transferred_finite_floor_approx": float(transferred_floor),
            "absolute_row_sum_upper_exact": _fraction_text(success_row_sum),
            "absolute_row_sum_upper_approx": float(success_row_sum),
            "row_sum_bound_is_too_coarse": success_row_sum > floor,
            "error_gram_intervals": _gram_intervals(success_error),
            "eigenvalue_intervals": [
                value.str(28, radius=True, more=True)
                for value in success_eigenvalues
            ],
        },
    ]
    return {
        "metric": metric,
        "source_cost": (
            "S=I"
            if metric == "L2"
            else "S=diag(1+pi^2, 1+4pi^2), the declared continuum H1 cost"
        ),
        "stage_x_late_core_floor_exact": _fraction_text(floor),
        "stage_x_late_core_floor_approx": float(floor),
        "records": records,
        "negative_controls": {
            "predecessor_is_rigorously_rejected": predecessor_rejected,
            "row_sum_fails_where_exact_2x2_norm_succeeds": bool(
                success_row_sum > floor and success
            ),
            "entrywise_max_fails_where_rayleigh_rejects": bool(
                predecessor_entry_max < floor and predecessor_rejected
            ),
        },
        "passed": bool(
            predecessor_rejected and success and transferred_floor > 0
        ),
    }


def run_certificate(
    precision_bits: int = DEFAULT_PRECISION_BITS,
    taylor_degree: int = DEFAULT_TAYLOR_DEGREE,
    l2_predecessor: int = FAILED_ODD_PREDECESSOR,
    l2_successful_grid: int = CERTIFIED_ODD_GRID,
    h1_predecessor: int = FAILED_H1_ODD_PREDECESSOR,
    h1_successful_grid: int = CERTIFIED_H1_ODD_GRID,
) -> dict[str, object]:
    """Prove adjacent odd-grid crossings in both declared source metrics."""
    if precision_bits < 160:
        raise ValueError("precision_bits must be at least 160")
    if taylor_degree < 24:
        raise ValueError("certificate Taylor degree must be at least 24")
    grids = (
        l2_predecessor,
        l2_successful_grid,
        h1_predecessor,
        h1_successful_grid,
    )
    if any(grid % 2 != 1 for grid in grids):
        raise ValueError("all grids must be odd so the target is exactly centred")
    if (
        l2_predecessor >= l2_successful_grid
        or h1_predecessor >= h1_successful_grid
    ):
        raise ValueError("predecessor must be smaller than the successful grid")

    previous_precision = ctx.prec
    ctx.prec = precision_bits
    try:
        continuum = continuum_lattice_gram(BAND_DIMENSION, precision_bits)
        metric_certificates = [
            _metric_certificate(
                "L2",
                l2_predecessor,
                l2_successful_grid,
                PREDECESSOR_RAYLEIGH_VECTOR,
                continuum,
                taylor_degree,
            ),
            _metric_certificate(
                "H1",
                h1_predecessor,
                h1_successful_grid,
                H1_PREDECESSOR_RAYLEIGH_VECTOR,
                continuum,
                taylor_degree,
            ),
        ]

        return {
            "schema_version": "oig-xii-two-port-finite-transfer-v1",
            "status": "rigorous complete two-port finite-Neumann crossing at one lattice point",
            "environment": {
                "python": sys.version.split()[0],
                "platform": platform.platform(),
                "python_flint": __import__("flint").__version__,
                "arb_precision_bits": precision_bits,
            },
            "model": {
                "interaction_strength_exact": _fraction_text(
                    INTERACTION_STRENGTH
                ),
                "lattice_time_exact": _fraction_text(LATTICE_TIME),
                "band_dimension": BAND_DIMENSION,
                "source_ports": [1, 2],
                "source_metrics": [
                    "L2 coefficient metric S=I",
                    "declared continuum H1 cost S=diag(1+pi^2,1+4pi^2)",
                ],
                "target": "central atomic cell, exactly x=1/2 on odd grids",
                "normalization": "sqrt(1+tau)=sqrt(2)",
            },
            "proof_method": {
                "finite_dynamics": (
                    "Arb centred-Taylor actions of the noncommuting tridiagonal "
                    "matrices L_n+omega V_n"
                ),
                "remainder": (
                    "exact rational spectral Taylor tail from 0<=L_n<=4I, "
                    "I<=V_n<=9I/5, and 0<=omega<=4"
                ),
                "continuum": "Arb validated integral from the Stage XI checker",
                "norm": "closed-form symmetric 2x2 eigenvalue enclosure",
                "predecessor": (
                    "fixed integer Rayleigh vectors (4,1) in L2 and (8,1) "
                    "after H1 whitening, with directed lower endpoints above "
                    "the respective exact floors"
                ),
                "binary64_decides_no_inequality": True,
            },
            "metric_certificates": metric_certificates,
            "scope_boundary": (
                "This proves K=2 only at the one-cell lattice point tau=1, "
                "for the declared L2 and continuum-H1 source metrics and "
                "exactly centred atomic target. It is not uniform in tau and "
                "is not a full-atlas finite-grid theorem."
            ),
            "negative_controls": {
                "both_predecessors_are_rigorously_rejected": all(
                    row["negative_controls"][
                        "predecessor_is_rigorously_rejected"
                    ]
                    for row in metric_certificates
                ),
                "target_parity_used_exactly": True,
                "noncommuting_generator_retained": True,
                "binary64_not_used_for_proof": True,
                "row_sum_fails_where_exact_2x2_norm_succeeds": all(
                    row["negative_controls"][
                        "row_sum_fails_where_exact_2x2_norm_succeeds"
                    ]
                    for row in metric_certificates
                ),
                "entrywise_max_fails_where_rayleigh_rejects": all(
                    row["negative_controls"][
                        "entrywise_max_fails_where_rayleigh_rejects"
                    ]
                    for row in metric_certificates
                ),
            },
            "overall_passed": all(row["passed"] for row in metric_certificates),
        }
    finally:
        ctx.prec = previous_precision


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--precision-bits", type=int, default=DEFAULT_PRECISION_BITS)
    parser.add_argument("--taylor-degree", type=int, default=DEFAULT_TAYLOR_DEGREE)
    parser.add_argument("--l2-predecessor", type=int, default=FAILED_ODD_PREDECESSOR)
    parser.add_argument("--l2-successful-grid", type=int, default=CERTIFIED_ODD_GRID)
    parser.add_argument(
        "--h1-predecessor", type=int, default=FAILED_H1_ODD_PREDECESSOR
    )
    parser.add_argument(
        "--h1-successful-grid", type=int, default=CERTIFIED_H1_ODD_GRID
    )
    parser.add_argument("--output")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    result = run_certificate(
        args.precision_bits,
        args.taylor_degree,
        args.l2_predecessor,
        args.l2_successful_grid,
        args.h1_predecessor,
        args.h1_successful_grid,
    )
    payload = json.dumps(result, indent=None if args.compact else 2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")
    else:
        print(payload)
    if not result["overall_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
