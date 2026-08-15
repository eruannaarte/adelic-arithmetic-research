#!/usr/bin/env python3
"""Proof-producing local Arb cover for the K=2 lattice-time transfer.

The checker encloses a whole rational tau interval around one rational centre.
It evaluates Taylor coefficients of the *difference* between the complete
finite noncommuting Neumann Gram and the continuum lattice Gram.  This retains
the cancellation that is destroyed by evaluating the two families as
unrelated interval boxes.

All certificate decisions use Arb balls and exact Stage X rational floors.
Binary64 is used only when serializing human-readable approximations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from fractions import Fraction

from flint import acb, arb, ctx, fmpq

from oig_xi_transfer_certificate import STAGE_X_LOWER_BOUNDS


INTERACTION_STRENGTH = Fraction(4, 5)
BAND_DIMENSION = 2
DEFAULT_PRECISION_BITS = 256
DEFAULT_EXPONENTIAL_DEGREE = 48
DEFAULT_TAU_ORDER = 18
DEFAULT_SIDE_LENGTH = 1001
DEFAULT_CENTRE = Fraction(11, 10)
DEFAULT_RADIUS = Fraction(1, 10)


def _q(value: Fraction | int) -> arb:
    if isinstance(value, int):
        return arb(value)
    return arb(fmpq(value.numerator, value.denominator))


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _exact_dyadic_fraction(value: arb) -> Fraction:
    if not bool(value.rad() == 0):
        raise ValueError("expected an exact Arb endpoint")
    mantissa, exponent = map(int, value.man_exp())
    if exponent >= 0:
        return Fraction(mantissa * 2**exponent, 1)
    return Fraction(mantissa, 2 ** (-exponent))


def _symmetric_ball(radius: arb) -> arb:
    if not bool(radius >= 0):
        raise ArithmeticError("negative remainder radius")
    return arb.union(-radius.upper(), radius.upper())


def _series_add(left: list[arb], right: list[arb]) -> list[arb]:
    return [a + b for a, b in zip(left, right, strict=True)]


def _series_scale(series: list[arb], scalar: arb) -> list[arb]:
    return [scalar * value for value in series]


def _series_mul(left: list[arb], right: list[arb]) -> list[arb]:
    order = min(len(left), len(right))
    return [
        sum((left[k] * right[n - k] for k in range(n + 1)), arb(0))
        for n in range(order)
    ]


def _series_inverse(series: list[arb]) -> list[arb]:
    # During acb.integral's analyticity checks the complex xi box can contain
    # a removable zero of the closed-form phase denominator.  Returning an
    # indeterminate enclosure lets Arb subdivide that box, just as in the
    # Stage XI phase integrator; raising here would abort valid subdivision.
    result = [1 / series[0]]
    for n in range(1, len(series)):
        result.append(
            -sum(
                (series[k] * result[n - k] for k in range(1, n + 1)),
                arb(0),
            )
            / series[0]
        )
    return result


def _series_exp(series: list[arb]) -> list[arb]:
    result = [series[0].exp()]
    for n in range(1, len(series)):
        result.append(
            sum(
                (k * series[k] * result[n - k] for k in range(1, n + 1)),
                arb(0),
            )
            / n
        )
    return result


def _series_sqrt(series: list[arb]) -> list[arb]:
    root = series[0].sqrt()
    if bool(root.contains(0)):
        raise ZeroDivisionError("square-root series has zero constant term")
    result = [root]
    for n in range(1, len(series)):
        cross = sum(
            (result[k] * result[n - k] for k in range(1, n)), arb(0)
        )
        result.append((series[n] - cross) / (2 * root))
    return result


def _normalization_series(centre: Fraction, order: int) -> list[arb]:
    base = [_q(1 + centre), arb(1)] + [arb(0)] * (order - 1)
    return _series_sqrt(base)


def _phase_series(
    mode: int, centre: Fraction, omega: arb, order: int
) -> list[arb]:
    """Taylor series of F_k((centre+delta) omega) in delta."""
    tau = [_q(centre), arb(1)] + [arb(0)] * (order - 1)
    s = _series_scale(tau, omega)
    a = _series_scale(s, _q(INTERACTION_STRENGTH))
    negative_s = _series_scale(s, arb(-1))
    negative_a = _series_scale(a, arb(-1))
    exp_s = _series_exp(negative_s)
    exp_a = _series_exp(negative_a)
    parity = -1 if mode % 2 else 1
    endpoint = [arb(1) - parity * exp_a[0]] + [
        -parity * exp_a[index] for index in range(1, order + 1)
    ]
    numerator = _series_mul(_series_mul(exp_s, a), endpoint)
    denominator = _series_mul(a, a)
    denominator[0] += (mode * arb.pi()) ** 2
    return _series_scale(
        _series_mul(numerator, _series_inverse(denominator)), arb(2).sqrt()
    )


def continuum_gram_series(
    centre: Fraction,
    tau_order: int,
    precision_bits: int,
) -> list[list[list[arb]]]:
    """Rigorous Taylor coefficients of the normalized continuum Gram."""
    raw = [
        [[arb(0), arb(0)], [arb(0), arb(0)]]
        for _ in range(tau_order + 1)
    ]

    for row in range(2):
        for column in range(row + 1):
            for coefficient in range(tau_order + 1):
                def integrand(xi, _):
                    omega = 4 * (arb.pi() * xi / 2).sin() ** 2
                    left = _phase_series(
                        row + 1, centre, omega, tau_order
                    )
                    right = _phase_series(
                        column + 1, centre, omega, tau_order
                    )
                    return _series_mul(left, right)[coefficient]

                value = acb.integral(
                    integrand,
                    arb(0),
                    arb(1),
                    rel_tol=arb(2) ** (-(precision_bits - 40)),
                    abs_tol=arb(2) ** (-(precision_bits - 16)),
                    eval_limit=40_000,
                    depth_limit=32,
                )
                if not bool(value.imag.contains(0)):
                    raise ArithmeticError("continuum integral became nonreal")
                raw[coefficient][row][column] = value.real
                raw[coefficient][column][row] = value.real

    normalization = _normalization_series(centre, tau_order)
    result = [
        [[arb(0), arb(0)], [arb(0), arb(0)]]
        for _ in range(tau_order + 1)
    ]
    for row in range(2):
        for column in range(2):
            values = _series_mul(
                normalization,
                [raw[q][row][column] for q in range(tau_order + 1)],
            )
            for q, value in enumerate(values):
                result[q][row][column] = value
    return result


def _source_ports(side_length: int) -> tuple[list[arb], list[arb]]:
    scale = (arb(2) / side_length).sqrt()
    ports: list[list[arb]] = [[], []]
    for cell in range(side_length):
        x = _q(Fraction(2 * cell + 1, 2 * side_length))
        ports[0].append(scale * (arb.pi() * x).cos())
        ports[1].append(scale * (2 * arb.pi() * x).cos())
    return ports[0], ports[1]


def _apply_tridiagonal(
    state: list[arb], diagonal: list[arb], *, negate: bool
) -> list[arb]:
    result: list[arb] = []
    for cell, value in enumerate(state):
        updated = diagonal[cell] * value
        if cell:
            updated -= state[cell - 1]
        if cell + 1 < len(state):
            updated -= state[cell + 1]
        result.append(-updated if negate else updated)
    return result


def _mode_response_series(
    side_length: int,
    target_mode: int,
    sources: tuple[list[arb], list[arb]],
    centre: Fraction,
    tau_order: int,
    exponential_degree: int,
) -> tuple[list[arb], list[arb], dict[str, arb]]:
    n = side_length
    omega = 4 * (arb.pi() * target_mode / (2 * n)).sin() ** 2
    spectral_centre = 2 + _q(Fraction(7, 5)) * omega
    rho = 2 + _q(Fraction(2, 5)) * omega

    generator_diagonal: list[arb] = []
    shifted_diagonal: list[arb] = []
    for cell in range(n):
        laplacian_diagonal = 1 if cell in (0, n - 1) else 2
        x = _q(Fraction(2 * cell + 1, 2 * n))
        modulation = 1 + _q(INTERACTION_STRENGTH) * x
        diagonal = laplacian_diagonal + omega * modulation
        generator_diagonal.append(diagonal)
        shifted_diagonal.append(diagonal - spectral_centre)

    tau0 = _q(centre)
    polynomial_states: list[list[arb]] = [list(sources[0]), list(sources[1])]
    totals: list[list[arb]] = [list(sources[0]), list(sources[1])]
    for degree in range(1, exponential_degree + 1):
        for port in range(2):
            polynomial_states[port] = [
                tau0 * value / degree
                for value in _apply_tridiagonal(
                    polynomial_states[port], shifted_diagonal, negate=True
                )
            ]
            for cell in range(n):
                totals[port][cell] += polynomial_states[port][cell]

    exponential_factor = (-tau0 * spectral_centre).exp()
    base_states = [
        [exponential_factor * value for value in totals[port]]
        for port in range(2)
    ]

    tail = (
        (-tau0 * omega).exp()
        * (tau0 * rho) ** (exponential_degree + 1)
        / math.factorial(exponential_degree + 1)
    ).upper()
    generator_norm = (4 + _q(Fraction(9, 5)) * omega).upper()

    result: list[list[arb]] = [[], []]
    derivative_states = base_states
    factorial = 1
    norm_power = arb(1)
    for order in range(tau_order + 1):
        if order:
            factorial *= order
            norm_power *= generator_norm
            derivative_states = [
                [value / order for value in _apply_tridiagonal(
                    derivative_states[port], generator_diagonal, negate=True
                )]
                for port in range(2)
            ]
        coefficient_tail = tail * norm_power / factorial
        remainder = _symmetric_ball(coefficient_tail)
        for port in range(2):
            amplitude = sum(derivative_states[port], arb(0)) / arb(n).sqrt()
            result[port].append(amplitude + remainder)
    return result[0], result[1], {
        "omega": omega,
        "operator_tail": tail,
        "generator_norm": generator_norm,
    }


def finite_gram_series(
    side_length: int,
    centre: Fraction,
    tau_order: int,
    exponential_degree: int,
) -> tuple[list[list[list[arb]]], dict[str, object]]:
    """Rigorous Taylor coefficients of the complete finite Neumann Gram."""
    if side_length <= 2 or side_length % 2 != 1:
        raise ValueError("side_length must be odd and exceed two")
    sources = _source_ports(side_length)
    raw = [
        [[arb(0), arb(0)], [arb(0), arb(0)]]
        for _ in range(tau_order + 1)
    ]
    largest_tail = arb(0)
    largest_generator_norm = arb(0)
    for target_mode in range(2, side_length, 2):
        first, second, trace = _mode_response_series(
            side_length,
            target_mode,
            sources,
            centre,
            tau_order,
            exponential_degree,
        )
        if bool(trace["operator_tail"] > largest_tail):
            largest_tail = trace["operator_tail"]
        if bool(trace["generator_norm"] > largest_generator_norm):
            largest_generator_norm = trace["generator_norm"]
        products = (
            _series_mul(first, first),
            _series_mul(first, second),
            _series_mul(second, second),
        )
        for order in range(tau_order + 1):
            factor = arb(2) / side_length
            raw[order][0][0] += factor * products[0][order]
            raw[order][0][1] += factor * products[1][order]
            raw[order][1][0] += factor * products[1][order]
            raw[order][1][1] += factor * products[2][order]

    normalization = _normalization_series(centre, tau_order)
    result = [
        [[arb(0), arb(0)], [arb(0), arb(0)]]
        for _ in range(tau_order + 1)
    ]
    for row in range(2):
        for column in range(2):
            values = _series_mul(
                normalization,
                [raw[q][row][column] for q in range(tau_order + 1)],
            )
            for q, value in enumerate(values):
                result[q][row][column] = value
    return result, {
        "target_modes_retained": (side_length - 1) // 2,
        "largest_operator_tail": largest_tail.str(20, radius=True, more=True),
        "largest_generator_norm": largest_generator_norm.str(
            20, radius=True, more=True
        ),
    }


def _normalization_derivative_bound(
    derivative: int, lower: Fraction, upper: Fraction
) -> arb:
    if derivative == 0:
        return (1 + _q(upper)).sqrt()
    falling = Fraction(1, 1)
    for index in range(derivative):
        falling *= Fraction(1, 2) - index
    base = 1 + _q(lower)
    return _q(abs(falling)) * base.sqrt() / base**derivative


def gram_derivative_entry_bound(
    derivative: int,
    lower: Fraction,
    upper: Fraction,
    generator_norm: Fraction,
) -> arb:
    """Uniform bound on one entry of the normalized Gram derivative."""
    total = arb(0)
    twice_norm = 2 * _q(generator_norm)
    for normalization_order in range(derivative + 1):
        total += (
            math.comb(derivative, normalization_order)
            * _normalization_derivative_bound(
                normalization_order, lower, upper
            )
            * twice_norm ** (derivative - normalization_order)
        )
    return total


def _metric_diagonals(
    metric: str, side_length: int
) -> tuple[tuple[arb, arb], tuple[arb, arb]]:
    continuum = (1 + arb.pi() ** 2, 1 + (2 * arb.pi()) ** 2)
    if metric == "L2":
        identity = (arb(1), arb(1))
        return identity, identity
    if metric == "declared_H1":
        return continuum, continuum
    if metric == "natural_discrete_H1":
        n = side_length
        finite = tuple(
            1 + n**2 * 4 * (arb.pi() * mode / (2 * n)).sin() ** 2
            for mode in (1, 2)
        )
        return (finite[0], finite[1]), continuum
    raise ValueError("unknown metric")


def _evaluate_metric_error(
    finite: list[list[list[arb]]],
    continuum: list[list[list[arb]]],
    delta: arb,
    radius: Fraction,
    lower: Fraction,
    upper: Fraction,
    side_length: int,
    metric: str,
) -> tuple[list[list[arb]], arb, tuple[arb, arb], list[list[arb]]]:
    finite_metric, continuum_metric = _metric_diagonals(metric, side_length)
    error = [[arb(0), arb(0)], [arb(0), arb(0)]]
    derivative = len(finite)
    finite_bound = gram_derivative_entry_bound(
        derivative, lower, upper, Fraction(56, 5)
    )
    continuum_bound = gram_derivative_entry_bound(
        derivative, lower, upper, Fraction(36, 5)
    )
    remainder_scale = _q(radius) ** derivative / math.factorial(derivative)
    remainder_matrix = [[arb(0), arb(0)], [arb(0), arb(0)]]

    for row in range(2):
        for column in range(2):
            value = arb(0)
            for order in range(len(finite) - 1, -1, -1):
                finite_coefficient = finite[order][row][column] / (
                    finite_metric[row] * finite_metric[column]
                ).sqrt()
                continuum_coefficient = continuum[order][row][column] / (
                    continuum_metric[row] * continuum_metric[column]
                ).sqrt()
                value = value * delta + finite_coefficient - continuum_coefficient
            entry_remainder = remainder_scale * (
                finite_bound
                / (finite_metric[row] * finite_metric[column]).sqrt()
                + continuum_bound
                / (continuum_metric[row] * continuum_metric[column]).sqrt()
            )
            remainder_matrix[row][column] = entry_remainder
            error[row][column] = value + _symmetric_ball(entry_remainder)

    a = error[0][0]
    b = (error[0][1] + error[1][0]) / 2
    d = error[1][1]
    discriminant = ((a - d) ** 2 + 4 * b**2).sqrt()
    eigenvalues = ((a + d - discriminant) / 2, (a + d + discriminant) / 2)
    upper = max(
        (_exact_dyadic_fraction(value.abs_upper()) for value in eigenvalues)
    )
    return error, _q(upper), eigenvalues, remainder_matrix


def run_cover(
    *,
    side_length: int = DEFAULT_SIDE_LENGTH,
    centre: Fraction = DEFAULT_CENTRE,
    radius: Fraction = DEFAULT_RADIUS,
    precision_bits: int = DEFAULT_PRECISION_BITS,
    exponential_degree: int = DEFAULT_EXPONENTIAL_DEGREE,
    tau_order: int = DEFAULT_TAU_ORDER,
) -> dict[str, object]:
    if side_length <= 2 or side_length % 2 != 1:
        raise ValueError("side_length must be odd and exceed two")
    if radius <= 0 or centre - radius < 1:
        raise ValueError("cover must have positive radius and lie in tau>=1")
    if precision_bits < 160:
        raise ValueError("precision_bits must be at least 160")
    if exponential_degree < 32:
        raise ValueError("exponential_degree must be at least 32")
    if tau_order < 2:
        raise ValueError("tau_order must be at least two")

    previous_precision = ctx.prec
    ctx.prec = precision_bits
    try:
        finite, finite_trace = finite_gram_series(
            side_length, centre, tau_order, exponential_degree
        )
        continuum = continuum_gram_series(centre, tau_order, precision_bits)
        lower = centre - radius
        upper = centre + radius
        delta = arb.union(-_q(radius), _q(radius))
        records: list[dict[str, object]] = []
        for metric, floor_name in (
            ("L2", "L2"),
            ("declared_H1", "H1"),
            ("natural_discrete_H1", "H1"),
        ):
            error, norm_upper_ball, eigenvalues, remainder_matrix = (
                _evaluate_metric_error(
                    finite,
                    continuum,
                    delta,
                    radius,
                    lower,
                    upper,
                    side_length,
                    metric,
                )
            )
            norm_upper = _exact_dyadic_fraction(norm_upper_ball.upper())
            floor = STAGE_X_LOWER_BOUNDS[floor_name][BAND_DIMENSION - 1]
            passed = bool(norm_upper_ball < _q(floor))
            records.append(
                {
                    "metric": metric,
                    "stage_x_floor_exact": _fraction_text(floor),
                    "stage_x_floor_approx": float(floor),
                    "spectral_error_upper_exact": _fraction_text(norm_upper),
                    "spectral_error_upper_approx": float(norm_upper),
                    "transferred_floor_exact": (
                        _fraction_text(floor - norm_upper) if passed else None
                    ),
                    "transferred_floor_approx": (
                        float(floor - norm_upper) if passed else None
                    ),
                    "error_matrix_intervals": [
                        [entry.str(24, radius=True, more=True) for entry in row]
                        for row in error
                    ],
                    "eigenvalue_intervals": [
                        value.str(24, radius=True, more=True)
                        for value in eigenvalues
                    ],
                    "tau_taylor_entry_remainders": [
                        [
                            value.str(20, radius=True, more=True)
                            for value in row
                        ]
                        for row in remainder_matrix
                    ],
                    "passed": passed,
                }
            )
        floor_payload = "|".join(
            f"{record['metric']}:{record['stage_x_floor_exact']}"
            for record in records
        )
        result = {
            "schema_version": "oig-uniform-lattice-arb-cover-v1",
            "status": "rigorous local compact-tau full-Neumann cover",
            "environment": {
                "python": sys.version.split()[0],
                "platform": platform.platform(),
                "python_flint": __import__("flint").__version__,
                "arb_precision_bits": precision_bits,
            },
            "model": {
                "side_length": side_length,
                "band_dimension": BAND_DIMENSION,
                "interaction_strength_exact": _fraction_text(
                    INTERACTION_STRENGTH
                ),
                "tau_interval_exact": [
                    _fraction_text(lower),
                    _fraction_text(upper),
                ],
                "tau_centre_exact": _fraction_text(centre),
                "tau_radius_exact": _fraction_text(radius),
                "target": "one exactly central cell on an odd grid",
                "finite_generator": "L_n + omega_(n,l) V_n, no phase surrogate",
                "normalization": "sqrt(1+tau)",
            },
            "proof_method": {
                "tau_taylor_order": tau_order,
                "finite_exponential_degree": exponential_degree,
                "finite_value_enclosure": (
                    "Arb centred B=A-cI operator polynomial at rational tau centre"
                ),
                "tau_dependence": (
                    "Arb Taylor coefficients of the finite-continuum difference"
                ),
                "tau_remainder": (
                    "global derivative majorants from contraction, "
                    "||A_n||<=56/5 and ||omega V||<=36/5"
                ),
                "spectral_norm": "closed symmetric 2x2 eigenvalue enclosure",
                "binary64_decides_no_inequality": True,
                "continuum_integrator": {
                    "relative_tolerance_power_of_two": -(precision_bits - 40),
                    "absolute_tolerance_power_of_two": -(precision_bits - 16),
                    "evaluation_limit": 40_000,
                    "depth_limit": 32,
                    "reality_premise": "the explicit integrand is real on the real xi interval; the complex integrator is used only for validated quadrature",
                },
            },
            "stage_x_floor_provenance": {
                "module": "oig_xi_transfer_certificate.py",
                "symbol": "STAGE_X_LOWER_BOUNDS",
                "band_dimension": BAND_DIMENSION,
                "used_floor_sha256": hashlib.sha256(
                    floor_payload.encode("utf-8")
                ).hexdigest(),
            },
            "finite_trace": finite_trace,
            "metric_certificates": records,
            "overall_passed": all(record["passed"] for record in records),
        }
        verification = verify_cover_report(result)
        if not verification["passed"]:
            raise AssertionError(f"cover self-verification failed: {verification}")
        result["independent_exact_verification"] = verification
        return result
    finally:
        ctx.prec = previous_precision


def _parse_fraction(text: str) -> Fraction:
    return Fraction(text)


def verify_cover_report(report: dict[str, object]) -> dict[str, object]:
    """Recheck every rational transfer decision without trusting booleans."""
    try:
        if report.get("schema_version") != "oig-uniform-lattice-arb-cover-v1":
            raise ValueError("unknown compact-cover schema")
        records = report["metric_certificates"]
        if not isinstance(records, list) or not records:
            raise ValueError("metric certificates are missing")
        decisions: list[bool] = []
        floor_payload_rows: list[str] = []
        for record in records:
            floor = Fraction(record["stage_x_floor_exact"])
            error = Fraction(record["spectral_error_upper_exact"])
            passed = error < floor
            decisions.append(passed)
            floor_payload_rows.append(f"{record['metric']}:{record['stage_x_floor_exact']}")
            if type(record.get("passed")) is not bool or record["passed"] is not passed:
                raise ValueError("a compact-cover decision flag is inconsistent")
            expected_margin = floor - error if passed else None
            expected_text = _fraction_text(expected_margin) if passed else None
            if record.get("transferred_floor_exact") != expected_text:
                raise ValueError("a transferred-floor field is inconsistent")
        if type(report.get("overall_passed")) is not bool or report["overall_passed"] is not all(decisions):
            raise ValueError("overall compact-cover decision is inconsistent")
        provenance = report["stage_x_floor_provenance"]
        payload = "|".join(floor_payload_rows)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        if provenance.get("used_floor_sha256") != digest:
            raise ValueError("Stage X floor provenance digest is inconsistent")
        if provenance.get("band_dimension") != BAND_DIMENSION:
            raise ValueError("Stage X floor band dimension is inconsistent")
        return {
            "passed": all(decisions),
            "method": "independent exact-rational replay of all compact-cover floor decisions and premise digest",
            "metric_count": len(decisions),
        }
    except Exception as error:
        return {"passed": False, "error": str(error)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--side-length", type=int, default=DEFAULT_SIDE_LENGTH)
    parser.add_argument("--centre", type=_parse_fraction, default=DEFAULT_CENTRE)
    parser.add_argument("--radius", type=_parse_fraction, default=DEFAULT_RADIUS)
    parser.add_argument("--precision-bits", type=int, default=DEFAULT_PRECISION_BITS)
    parser.add_argument(
        "--exponential-degree", type=int, default=DEFAULT_EXPONENTIAL_DEGREE
    )
    parser.add_argument("--tau-order", type=int, default=DEFAULT_TAU_ORDER)
    parser.add_argument("--output")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    result = run_cover(
        side_length=args.side_length,
        centre=args.centre,
        radius=args.radius,
        precision_bits=args.precision_bits,
        exponential_degree=args.exponential_degree,
        tau_order=args.tau_order,
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
