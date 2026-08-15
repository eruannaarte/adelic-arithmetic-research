#!/usr/bin/env python3
"""Arb certificate for the canonical three-reading global-design experiment.

The frozen arithmetic model has ``r=3``, ``s=4``, and labelled prime axes
``(2, 3, 5)``.  This artifact certifies two complementary finite inputs for
Arithmetic Observability V.

First, it checks a rational phase-separated three-reading design.  Its three
diagonal phases remain in ``(7/10,1)`` and its six off-diagonal phases remain
in ``(-1/25,1/25)`` even when each time is independently perturbed by
``1/1000``.  It also verifies the explicit trigonometric and torus-width
inequalities used by the manuscript's global-injectivity proof.

Second, it checks a fixed and a parameterized Krawczyk inclusion for the
centered reciprocal system near the schedule ``(1, 2, 3)``.  The latter is
uniform on an exact dyadic schedule box, providing finite interval evidence
for an open chamber of reciprocal collisions.

Every proof decision involving pi, logarithms, trigonometric functions, or
hyperbolic functions uses Arb at the pinned precision.  The global-injection
theorem, the Krawczyk theorem, and the reciprocal-collision implication are
ordinary manuscript mathematics, not formalized by this executable artifact.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Iterable, Sequence

import flint
from flint import acb, arb, arb_mat, ctx, fmpq


SCHEMA = "arithmetic-observability-global-design-v1"
FORMAL_PRECISION_BITS = 384
MIN_PRECISION_BITS = 256
MAX_PRECISION_BITS = 1024
PINNED_PYTHON_FLINT_VERSION = "0.9.0"
PINNED_FLINT_VERSION = "3.6.0"

MAX_ARTIFACT_BYTES = 200_000
MAX_CONTAINER_ITEMS = 256
MAX_JSON_DEPTH = 20
MAX_TEXT_FIELD_LENGTH = 2048
MAX_INTEGER_BITS = 4096
INTERVAL_DISPLAY_DIGITS = 100

PRIMES = (2, 3, 5)
AXIS_COUNT = 3
EXPONENTS_PER_AXIS = 4

PHASE_DIAGONAL_LOWER = Fraction(7, 10)
PHASE_DIAGONAL_UPPER = Fraction(1)
PHASE_OFF_DIAGONAL_RADIUS = Fraction(1, 25)
PHASE_TIME_RADIUS = Fraction(1, 1000)
PHASE_TIMES = (
    Fraction(245943, 1000),
    Fraction(140531, 500),
    Fraction(120104, 125),
)
PHASE_WINDINGS = (
    (27, 43, 63),
    (31, 49, 72),
    (106, 168, 246),
)

LEAKAGE_UPPER = Fraction(21, 100)
KAPPA_FLOOR = Fraction(6, 25)
SINE_TWO_LOWER = Fraction(9, 10)
RAW_AND_CHORD_FLOOR = Fraction(2, 15)
TORUS_GAP_FLOOR = Fraction(6, 25)
TORUS_WIDTH = Fraction(81, 25)

ROOT_CENTER_DECIMALS = (
    "-2.311649500081883325980686276574019654442114638435401550980892589734352848278032788120155354655681247750132154312858",
    "-0.4996823392786411764958911757908930373239537317278304382953588815203287347291700628228447642132821973868085019753478",
    "0.2844776759098668296344536391250881849580502822975826540240558228390510698937638973816834576804294670090486113846873",
)
ROOT_CENTER = tuple(Fraction(value) for value in ROOT_CENTER_DECIMALS)
COLLISION_TIMES = (Fraction(1), Fraction(2), Fraction(3))

# Decimal strings denote exact rationals.  They are a frozen approximation to
# the inverse of D_x F at the declared center; no binary float is involved.
APPROXIMATE_INVERSE_DECIMALS = (
    (
        "0.050450521518740096800129775014759685080019631632993205718460441442927450145806334699341528496077052370808279382",
        "-0.63566342586956777532624697836951162531416368376701633767140858449929594026146521411175446860252609506008948448",
        "0.30780351781527505567856993527926891200996140850039768889312665729952738569571296847839821145722153941962755183",
    ),
    (
        "-0.016175836392706834247273913052353361858718477604969726455647554398351122140541747413294163918638113953320613238",
        "0.043090761282378987402268142064400018670481512139801332409617642867528478553327438339849437506704660831756813136",
        "-0.02155559776227766224591443497920251312171927636680206181782625289221118383084384356267989604269360201397988631",
    ),
    (
        "0.0067160660656065373586725507926475494663303416152752017699394386023730059131892592945511989389656740577465981263",
        "-0.04199328761383076922869851054666477240477525762649662617757298786110282096030478038210165826156257547017758869",
        "0.038695105408704599086112952240474143719006568180524225920184213562280885549507455500091257605676587869609285816",
    ),
)
APPROXIMATE_INVERSE = tuple(
    tuple(Fraction(value) for value in row)
    for row in APPROXIMATE_INVERSE_DECIMALS
)

FIXED_ROOT_RADIUS = Fraction(1, 2**280)
PARAMETER_X_RADIUS = Fraction(1, 2**14)
PARAMETER_TIME_RADIUS = Fraction(1, 2**24)
FIXED_FUNCTION_ABSOLUTE_CAP = Fraction(1, 10**100)
PARAMETER_FUNCTION_ABSOLUTE_CAP = Fraction(1, 10**4)


def _fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def _parse_fraction_limited(text: str) -> Fraction:
    if not isinstance(text, str) or len(text) > 1536 or "/" not in text:
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


def _ball(center: Fraction | int, radius: Fraction | int = 0) -> arb:
    center = Fraction(center)
    radius = Fraction(radius)
    if radius < 0:
        raise ValueError("ball radius must be nonnegative")
    if radius == 0:
        return _arb_rational(center)
    return arb(fmpq(center.numerator, center.denominator), _arb_rational(radius))


def _add_error(value: arb, radius: Fraction) -> arb:
    if radius < 0:
        raise ValueError("error radius must be nonnegative")
    return value + arb(0, _arb_rational(radius))


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def _pretty_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


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


def _upper_abs_exact(value: arb) -> Fraction:
    return _exact_dyadic_fraction(abs(value).upper())


def _radius_audit(values: Iterable[arb], cap: Fraction) -> dict[str, object]:
    cap_ball = _arb_rational(cap)
    count = 0
    passed = True
    for value in values:
        count += 1
        passed &= bool(value.rad() < cap_ball)
    return {
        "quantity_count": count,
        "radius_cap_exact": _fraction_text(cap),
        "every_radius_strictly_below_cap": passed,
    }


def _check_environment() -> None:
    if flint.__version__ != PINNED_PYTHON_FLINT_VERSION:
        raise RuntimeError(
            "python-flint environment mismatch: expected "
            f"{PINNED_PYTHON_FLINT_VERSION}, got {flint.__version__}"
        )
    if flint.__FLINT_VERSION__ != PINNED_FLINT_VERSION:
        raise RuntimeError(
            "FLINT environment mismatch: expected "
            f"{PINNED_FLINT_VERSION}, got {flint.__FLINT_VERSION__}"
        )


def _phase_center_times(
    times: Sequence[Fraction] = PHASE_TIMES,
) -> tuple[arb, arb, arb]:
    if len(times) != AXIS_COUNT or any(type(value) is not Fraction for value in times):
        raise ValueError("phase times must be three exact Fraction values")
    return tuple(_arb_rational(value) for value in times)  # type: ignore[return-value]


def _build_phase_design_section(
    time_radius: Fraction = PHASE_TIME_RADIUS,
    times: Sequence[Fraction] = PHASE_TIMES,
    windings: Sequence[Sequence[int]] = PHASE_WINDINGS,
) -> dict[str, object]:
    if type(time_radius) is not Fraction or time_radius < 0:
        raise ValueError("phase time radius must be a nonnegative exact Fraction")
    if len(windings) != AXIS_COUNT or any(
        len(row) != AXIS_COUNT or any(type(value) is not int for value in row)
        for row in windings
    ):
        raise ValueError("phase windings must be a 3 by 3 exact integer array")
    pi = arb.pi()
    logarithms = tuple(arb(prime).log() for prime in PRIMES)
    centers = _phase_center_times(times)
    perturbed_times = tuple(
        _add_error(center, time_radius) for center in centers
    )
    records: list[dict[str, object]] = []
    every_central_inside = True
    every_robust_inside = True
    robust_off_upper_bounds: list[Fraction] = []
    robust_diagonal_lower_bounds: list[Fraction] = []
    robust_diagonal_upper_bounds: list[Fraction] = []
    for reading in range(AXIS_COUNT):
        for axis in range(AXIS_COUNT):
            winding = windings[reading][axis]
            central_residual = (
                centers[reading] * logarithms[axis]
                - 2 * pi * winding
            )
            robust_residual = (
                perturbed_times[reading] * logarithms[axis]
                - 2 * pi * winding
            )
            role = "diagonal" if reading == axis else "off_diagonal"
            if reading == axis:
                central_inside = bool(
                    central_residual > _arb_rational(PHASE_DIAGONAL_LOWER)
                    and central_residual < _arb_rational(PHASE_DIAGONAL_UPPER)
                )
                robust_inside = bool(
                    robust_residual > _arb_rational(PHASE_DIAGONAL_LOWER)
                    and robust_residual < _arb_rational(PHASE_DIAGONAL_UPPER)
                )
                robust_diagonal_lower_bounds.append(
                    _exact_dyadic_fraction(robust_residual.lower())
                )
                robust_diagonal_upper_bounds.append(
                    _exact_dyadic_fraction(robust_residual.upper())
                )
                robust_upper: Fraction | None = None
            else:
                central_inside = bool(
                    abs(central_residual)
                    < _arb_rational(PHASE_OFF_DIAGONAL_RADIUS)
                )
                robust_inside = bool(
                    abs(robust_residual)
                    < _arb_rational(PHASE_OFF_DIAGONAL_RADIUS)
                )
                robust_upper = _upper_abs_exact(robust_residual)
                robust_off_upper_bounds.append(robust_upper)
            every_central_inside &= central_inside
            every_robust_inside &= robust_inside
            records.append(
                {
                    "reading_index": reading,
                    "axis_index": axis,
                    "prime": PRIMES[axis],
                    "winding": winding,
                    "phase_role": role,
                    "central_reduced_residual_interval": _interval_text(
                        central_residual
                    ),
                    "central_residual_certainly_inside_declared_box": central_inside,
                    "perturbed_reduced_residual_interval": _interval_text(
                        robust_residual
                    ),
                    "perturbed_absolute_residual_upper_endpoint_exact": (
                        None if robust_upper is None else _fraction_text(robust_upper)
                    ),
                    "perturbed_residual_certainly_inside_declared_box": robust_inside,
                }
            )
    maximum_off_upper = max(robust_off_upper_bounds)
    minimum_diagonal_lower = min(robust_diagonal_lower_bounds)
    maximum_diagonal_upper = max(robust_diagonal_upper_bounds)
    off_slack = PHASE_OFF_DIAGONAL_RADIUS - maximum_off_upper
    diagonal_lower_slack = minimum_diagonal_lower - PHASE_DIAGONAL_LOWER
    diagonal_upper_slack = PHASE_DIAGONAL_UPPER - maximum_diagonal_upper
    passed = bool(
        every_central_inside
        and every_robust_inside
        and off_slack > 0
        and diagonal_lower_slack > 0
        and diagonal_upper_slack > 0
    )
    return {
        "diagonal_phase_lower_exact": _fraction_text(PHASE_DIAGONAL_LOWER),
        "diagonal_phase_upper_exact": _fraction_text(PHASE_DIAGONAL_UPPER),
        "off_diagonal_absolute_phase_upper_exact": _fraction_text(
            PHASE_OFF_DIAGONAL_RADIUS
        ),
        "time_perturbation_radius_exact": _fraction_text(time_radius),
        "center_times_exact": [_fraction_text(value) for value in times],
        "windings": [list(row) for row in windings],
        "center_time_intervals": [_interval_text(value) for value in centers],
        "perturbed_time_intervals": [
            _interval_text(value) for value in perturbed_times
        ],
        "residual_definition": "theta_lj=log(p_j)*t_l-2*pi*n_lj",
        "residual_record_count": len(records),
        "residual_records": records,
        "maximum_perturbed_off_diagonal_absolute_residual_upper_endpoint_exact": _fraction_text(
            maximum_off_upper
        ),
        "minimum_perturbed_diagonal_residual_lower_endpoint_exact": _fraction_text(
            minimum_diagonal_lower
        ),
        "maximum_perturbed_diagonal_residual_upper_endpoint_exact": _fraction_text(
            maximum_diagonal_upper
        ),
        "robust_off_diagonal_slack_lower_exact": _fraction_text(off_slack),
        "robust_diagonal_lower_slack_exact": _fraction_text(
            diagonal_lower_slack
        ),
        "robust_diagonal_upper_slack_exact": _fraction_text(
            diagonal_upper_slack
        ),
        "every_center_residual_certainly_inside_declared_box": every_central_inside,
        "every_residual_certainly_inside_declared_box_throughout_time_box": (
            every_robust_inside
        ),
        "finite_phase_input_verified": passed,
        "passed": passed,
    }


def _build_analytic_inequalities_section() -> dict[str, object]:
    off_radius = _arb_rational(PHASE_OFF_DIAGONAL_RADIUS)
    diagonal_lower = _arb_rational(PHASE_DIAGONAL_LOWER)
    leakage = 2 * (off_radius / 2).tan() + 4 * off_radius.tan()
    kappa = diagonal_lower.sin() - 2 * leakage
    sine_two = arb(2).sin()
    raw_floor_passed = bool(kappa > _arb_rational(RAW_AND_CHORD_FLOOR))
    chord_floor = 2 * (kappa / 2).sin()
    chord_floor_passed = bool(
        chord_floor > _arb_rational(RAW_AND_CHORD_FLOOR)
    )
    raw_output_floor = sine_two * chord_floor
    raw_output_floor_passed = bool(
        raw_output_floor > _arb_rational(RAW_AND_CHORD_FLOOR)
    )
    width = _arb_rational(TORUS_WIDTH)
    width_below_full_turn = bool(width < 2 * arb.pi())
    gap = 2 * arb.pi() - width
    sine_two_passed = bool(sine_two > _arb_rational(SINE_TWO_LOWER))
    leakage_passed = bool(leakage < _arb_rational(LEAKAGE_UPPER))
    kappa_passed = bool(kappa > _arb_rational(KAPPA_FLOOR))
    gap_passed = bool(gap > _arb_rational(TORUS_GAP_FLOOR))
    passed = bool(
        sine_two_passed
        and leakage_passed
        and kappa_passed
        and raw_floor_passed
        and chord_floor_passed
        and raw_output_floor_passed
        and width_below_full_turn
        and gap_passed
    )
    return {
        "sine_two_interval": _interval_text(sine_two),
        "sine_two_lower_exact": _fraction_text(SINE_TWO_LOWER),
        "sine_two_certainly_above_lower": sine_two_passed,
        "leakage_definition": "M=2*tan(1/50)+4*tan(1/25)",
        "leakage_interval": _interval_text(leakage),
        "leakage_upper_exact": _fraction_text(LEAKAGE_UPPER),
        "leakage_certainly_below_upper": leakage_passed,
        "kappa_definition": "kappa=sin(7/10)-2*M",
        "kappa_interval": _interval_text(kappa),
        "kappa_floor_exact": _fraction_text(KAPPA_FLOOR),
        "kappa_certainly_above_floor": kappa_passed,
        "raw_distinguishability_floor_exact": _fraction_text(
            RAW_AND_CHORD_FLOOR
        ),
        "raw_kappa_certainly_above_distinguishability_floor": raw_floor_passed,
        "chord_definition": "2*sin(kappa/2)",
        "chord_interval": _interval_text(chord_floor),
        "chord_certainly_above_distinguishability_floor": chord_floor_passed,
        "raw_output_floor_definition": "sin(2)*2*sin(kappa/2)",
        "raw_output_floor_interval": _interval_text(raw_output_floor),
        "raw_output_floor_certainly_above_distinguishability_floor": (
            raw_output_floor_passed
        ),
        "torus_width_definition": "W=81/25",
        "torus_width_exact": _fraction_text(TORUS_WIDTH),
        "torus_width_certainly_below_two_pi": width_below_full_turn,
        "torus_gap_definition": "2*pi-W",
        "torus_gap_interval": _interval_text(gap),
        "torus_gap_floor_exact": _fraction_text(TORUS_GAP_FLOOR),
        "torus_gap_certainly_above_floor": gap_passed,
        "finite_analytic_inputs_verified": passed,
        "passed": passed,
    }


def _h4(x: arb, theta: arb) -> acb:
    argument = acb(x, -theta)
    return 2 * (3 * argument / 2).cosh() + 2 * (argument / 2).cosh()


def _dh4(x: arb, theta: arb) -> acb:
    argument = acb(x, -theta)
    return 3 * (3 * argument / 2).sinh() + (argument / 2).sinh()


def centered_system_and_jacobian(
    x_values: Sequence[arb],
    times: Sequence[arb],
) -> tuple[list[arb], list[list[arb]]]:
    """Return F_l=Im product_j H_4(x_j,log(p_j)t_l) and D_x F."""

    if len(x_values) != AXIS_COUNT or len(times) != AXIS_COUNT:
        raise ValueError("the centered system requires three x values and times")
    logarithms = tuple(arb(prime).log() for prime in PRIMES)
    values: list[arb] = []
    rows: list[list[arb]] = []
    for time in times:
        factors = tuple(
            _h4(x_values[axis], logarithms[axis] * time)
            for axis in range(AXIS_COUNT)
        )
        derivatives = tuple(
            _dh4(x_values[axis], logarithms[axis] * time)
            for axis in range(AXIS_COUNT)
        )
        product = factors[0] * factors[1] * factors[2]
        values.append(product.imag)
        derivative_row: list[arb] = []
        for axis in range(AXIS_COUNT):
            other_product = acb(1)
            for other in range(AXIS_COUNT):
                if other != axis:
                    other_product *= factors[other]
            derivative_row.append((derivatives[axis] * other_product).imag)
        rows.append(derivative_row)
    return values, rows


def _matrix_vector(values: Sequence[arb]) -> arb_mat:
    return arb_mat([[value] for value in values])


def _identity(dimension: int) -> arb_mat:
    return arb_mat(
        [
            [1 if row == column else 0 for column in range(dimension)]
            for row in range(dimension)
        ]
    )


def _fraction_det3(matrix: Sequence[Sequence[Fraction]]) -> Fraction:
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise ValueError("determinant input must be 3 by 3")
    return (
        matrix[0][0]
        * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1]
        * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2]
        * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def _krawczyk_inclusion(
    x_radius: Fraction,
    time_radius: Fraction,
) -> dict[str, object]:
    if x_radius <= 0 or time_radius < 0:
        raise ValueError("Krawczyk radii must have x>0 and time>=0")
    x_center = tuple(_arb_rational(value) for value in ROOT_CENTER)
    x_box = tuple(_ball(value, x_radius) for value in ROOT_CENTER)
    time_center = tuple(_arb_rational(value) for value in COLLISION_TIMES)
    time_box = tuple(_ball(value, time_radius) for value in COLLISION_TIMES)
    function_at_center, _ = centered_system_and_jacobian(x_center, time_box)
    _, jacobian_box = centered_system_and_jacobian(x_box, time_box)
    exact_inverse = arb_mat(
        [[_arb_rational(value) for value in row] for row in APPROXIMATE_INVERSE]
    )
    centered_domain = _matrix_vector(
        [_ball(Fraction(0), x_radius) for _ in range(AXIS_COUNT)]
    )
    correction = exact_inverse * _matrix_vector(function_at_center)
    defect = _identity(AXIS_COUNT) - exact_inverse * arb_mat(jacobian_box)
    krawczyk_centered = -correction + defect * centered_domain
    radius_ball = _arb_rational(x_radius)
    inclusions: list[bool] = []
    ratios: list[arb] = []
    intervals: list[str] = []
    absolute_upper_endpoints: list[Fraction] = []
    interior_slacks: list[Fraction] = []
    for axis in range(AXIS_COUNT):
        value = krawczyk_centered[axis, 0]
        included = bool(
            value.lower() > -radius_ball and value.upper() < radius_ball
        )
        inclusions.append(included)
        ratios.append(abs(value) / radius_ball)
        intervals.append(_interval_text(value))
        absolute_upper = _upper_abs_exact(value)
        absolute_upper_endpoints.append(absolute_upper)
        interior_slacks.append(x_radius - absolute_upper)
    all_coordinates_away_from_zero = all(
        bool(value < 0 or value > 0) for value in x_box
    )
    function_absolute_cap = (
        FIXED_FUNCTION_ABSOLUTE_CAP
        if time_radius == 0
        else PARAMETER_FUNCTION_ABSOLUTE_CAP
    )
    function_absolute_checks = [
        bool(abs(value) < _arb_rational(function_absolute_cap))
        for value in function_at_center
    ]
    function_radius_cap = Fraction(1, 10**70) if time_radius == 0 else Fraction(1)
    function_radius_audit = _radius_audit(function_at_center, function_radius_cap)
    passed = bool(
        all(inclusions)
        and all(slack > 0 for slack in interior_slacks)
        and all_coordinates_away_from_zero
        and all(function_absolute_checks)
        and function_radius_audit["every_radius_strictly_below_cap"]
    )
    return {
        "x_radius_exact": _fraction_text(x_radius),
        "time_radius_exact": _fraction_text(time_radius),
        "x_box_intervals": [_interval_text(value) for value in x_box],
        "time_center_exact": [_fraction_text(value) for value in COLLISION_TIMES],
        "time_box_intervals": [_interval_text(value) for value in time_box],
        "function_absolute_value_cap_exact": _fraction_text(
            function_absolute_cap
        ),
        "function_absolute_value_coordinate_checks": function_absolute_checks,
        "every_function_absolute_value_strictly_below_cap": all(
            function_absolute_checks
        ),
        "function_radius_audit": function_radius_audit,
        "krawczyk_centered_intervals": intervals,
        "krawczyk_absolute_upper_endpoints_exact": [
            _fraction_text(value) for value in absolute_upper_endpoints
        ],
        "krawczyk_interior_slacks_exact": [
            _fraction_text(value) for value in interior_slacks
        ],
        "krawczyk_absolute_over_x_radius_intervals": [
            _interval_text(value) for value in ratios
        ],
        "coordinate_interior_inclusions": inclusions,
        "krawczyk_image_strictly_inside_x_box": all(inclusions),
        "every_x_box_coordinate_certainly_away_from_zero": (
            all_coordinates_away_from_zero
        ),
        "passed": passed,
    }


def _build_krawczyk_section() -> dict[str, object]:
    determinant = _fraction_det3(APPROXIMATE_INVERSE)
    if determinant == 0:
        raise AssertionError("the exact rational approximate inverse is singular")
    fixed = _krawczyk_inclusion(FIXED_ROOT_RADIUS, Fraction(0))
    parameterized = _krawczyk_inclusion(
        PARAMETER_X_RADIUS, PARAMETER_TIME_RADIUS
    )
    root_sum_box = sum(
        (_ball(value, PARAMETER_X_RADIUS) for value in ROOT_CENTER),
        arb(0),
    )
    root_sum_certainly_negative = bool(root_sum_box < 0)
    passed = bool(
        fixed["passed"]
        and parameterized["passed"]
        and determinant != 0
        and root_sum_certainly_negative
    )
    return {
        "system": (
            "F_l(x,T)=Im product_j H_4(x_j,log(p_j)*T_l), "
            "H_4(x,theta)=2*cosh(3*(x-i*theta)/2)+2*cosh((x-i*theta)/2)"
        ),
        "variable_order": ["x_2", "x_3", "x_5"],
        "root_center_full_decimal_exact": list(ROOT_CENTER_DECIMALS),
        "root_center_fraction_exact": [
            _fraction_text(value) for value in ROOT_CENTER
        ],
        "approximate_inverse_full_decimal_exact": [
            list(row) for row in APPROXIMATE_INVERSE_DECIMALS
        ],
        "approximate_inverse_fraction_exact": [
            [_fraction_text(value) for value in row]
            for row in APPROXIMATE_INVERSE
        ],
        "approximate_inverse_determinant_exact": _fraction_text(determinant),
        "approximate_inverse_nonsingular_exact": determinant != 0,
        "fixed_schedule_root_localization": fixed,
        "uniform_schedule_chamber": parameterized,
        "parameter_x_radius_exact": _fraction_text(PARAMETER_X_RADIUS),
        "parameter_time_radius_exact": _fraction_text(PARAMETER_TIME_RADIUS),
        "parameter_root_sum_interval": _interval_text(root_sum_box),
        "parameter_root_sum_certainly_negative": root_sum_certainly_negative,
        "finite_krawczyk_inclusions_verified": passed,
        "conditional_manuscript_consequence": (
            "applying the parameterized Krawczyk theorem and the reciprocal "
            "identity gives at least one distinct positive reciprocal "
            "collision for every schedule in the declared open time chamber"
        ),
        "passed": passed,
    }


def build_payload(precision_bits: int = FORMAL_PRECISION_BITS) -> dict[str, object]:
    if type(precision_bits) is not int:
        raise ValueError("precision must be a canonical integer")
    if not MIN_PRECISION_BITS <= precision_bits <= MAX_PRECISION_BITS:
        raise ValueError("precision is outside the formal resource limits")
    _check_environment()
    with ctx.workprec(precision_bits):
        phase_design = _build_phase_design_section()
        analytic = _build_analytic_inequalities_section()
        krawczyk = _build_krawczyk_section()
    overall = bool(
        phase_design["passed"] and analytic["passed"] and krawczyk["passed"]
    )
    return {
        "parameters": {
            "primes": list(PRIMES),
            "axis_count": AXIS_COUNT,
            "exponents_per_axis": EXPONENTS_PER_AXIS,
            "phase_times_exact": [
                _fraction_text(value) for value in PHASE_TIMES
            ],
            "phase_diagonal_lower_exact": _fraction_text(
                PHASE_DIAGONAL_LOWER
            ),
            "phase_diagonal_upper_exact": _fraction_text(
                PHASE_DIAGONAL_UPPER
            ),
            "phase_off_diagonal_radius_exact": _fraction_text(
                PHASE_OFF_DIAGONAL_RADIUS
            ),
            "phase_time_radius_exact": _fraction_text(PHASE_TIME_RADIUS),
            "collision_time_center_exact": [
                _fraction_text(value) for value in COLLISION_TIMES
            ],
            "fixed_root_radius_exact": _fraction_text(FIXED_ROOT_RADIUS),
            "parameter_x_radius_exact": _fraction_text(PARAMETER_X_RADIUS),
            "parameter_time_radius_exact": _fraction_text(
                PARAMETER_TIME_RADIUS
            ),
        },
        "phase_separated_design": phase_design,
        "analytic_inequalities": analytic,
        "reciprocal_collision_krawczyk": krawczyk,
        "implementation": {
            "arb_precision_bits": precision_bits,
            "python_flint_version": flint.__version__,
            "flint_version": flint.__FLINT_VERSION__,
            "python_flint_version_pin": PINNED_PYTHON_FLINT_VERSION,
            "flint_version_pin": PINNED_FLINT_VERSION,
            "serialized_interval_digits": INTERVAL_DISPLAY_DIGITS,
            "all_transcendentals_enclosed_by_arb": True,
            "binary64_used_for_proof_decisions": False,
            "strict_interval_comparisons_only": True,
            "serialized_resource_cap_bytes": MAX_ARTIFACT_BYTES,
            "deterministic_encoding": "UTF-8, sorted keys, indent 2, LF newline",
        },
        "formal_scope": {
            "finite_interval_evidence_certified": (
                "nine robust phase residual inclusions, explicit analytic "
                "inequalities, and fixed plus parameterized Krawczyk inclusions"
            ),
            "global_injectivity_theorem_proved_by_certificate": False,
            "phase_separation_theorem_proved_by_certificate": False,
            "krawczyk_theorem_proved_by_certificate": False,
            "reciprocal_identity_proved_by_certificate": False,
            "open_chamber_noninjectivity_theorem_proved_by_certificate": False,
            "schedule_optimality_claimed": False,
            "proof_assistant_derivation": False,
            "arb_scope": (
                "computer-assisted interval proof conditional on the pinned "
                "Arb/FLINT implementation"
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
            if not isinstance(key, str) or len(key) > 160:
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
        raise ValueError("unsupported global-design schema")
    digest = artifact["payload_sha256"]
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(character not in "0123456789abcdef" for character in digest)
    ):
        raise ValueError("payload digest is not canonical lowercase SHA-256")
    payload = artifact["payload"]
    expected_payload_keys = {
        "parameters",
        "phase_separated_design",
        "analytic_inequalities",
        "reciprocal_collision_krawczyk",
        "implementation",
        "formal_scope",
        "overall_passed",
    }
    if not isinstance(payload, dict) or set(payload) != expected_payload_keys:
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
    ):
        if type(parameters.get(key)) is not int or parameters[key] != expected:
            raise ValueError(f"{key} is not a canonical integer")
    for key, expected in (
        ("phase_diagonal_lower_exact", PHASE_DIAGONAL_LOWER),
        ("phase_diagonal_upper_exact", PHASE_DIAGONAL_UPPER),
        ("phase_off_diagonal_radius_exact", PHASE_OFF_DIAGONAL_RADIUS),
        ("phase_time_radius_exact", PHASE_TIME_RADIUS),
        ("fixed_root_radius_exact", FIXED_ROOT_RADIUS),
        ("parameter_x_radius_exact", PARAMETER_X_RADIUS),
        ("parameter_time_radius_exact", PARAMETER_TIME_RADIUS),
    ):
        if _parse_fraction_limited(parameters.get(key)) != expected:
            raise ValueError(f"artifact uses noncanonical {key}")
    _validate_fraction_list(
        parameters.get("phase_times_exact"),
        PHASE_TIMES,
        "phase schedule",
    )
    _validate_fraction_list(
        parameters.get("collision_time_center_exact"),
        COLLISION_TIMES,
        "collision schedule",
    )

    phase = payload["phase_separated_design"]
    if not isinstance(phase, dict):
        raise ValueError("phase-design section is malformed")
    windings = phase.get("windings")
    if windings != [list(row) for row in PHASE_WINDINGS]:
        raise ValueError("artifact uses noncanonical phase windings")
    if not isinstance(windings, list) or any(
        not isinstance(row, list)
        or len(row) != AXIS_COUNT
        or not all(type(value) is int for value in row)
        for row in windings
    ):
        raise ValueError("phase windings violate exact integer typing")
    _validate_fraction_list(
        phase.get("center_times_exact"), PHASE_TIMES, "phase schedule"
    )
    records = phase.get("residual_records")
    if not isinstance(records, list) or len(records) != 9:
        raise ValueError("phase residual record list violates the resource cap")
    for expected_index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError("phase residual record must be an object")
        reading, axis = divmod(expected_index, AXIS_COUNT)
        if (
            type(record.get("reading_index")) is not int
            or record["reading_index"] != reading
            or type(record.get("axis_index")) is not int
            or record["axis_index"] != axis
            or type(record.get("prime")) is not int
            or record["prime"] != PRIMES[axis]
            or type(record.get("winding")) is not int
            or record["winding"] != PHASE_WINDINGS[reading][axis]
        ):
            raise ValueError("phase residual record has noncanonical indices")

    krawczyk = payload["reciprocal_collision_krawczyk"]
    if not isinstance(krawczyk, dict):
        raise ValueError("Krawczyk section is malformed")
    if krawczyk.get("root_center_full_decimal_exact") != list(
        ROOT_CENTER_DECIMALS
    ):
        raise ValueError("artifact uses a noncanonical root center")
    _validate_fraction_list(
        krawczyk.get("root_center_fraction_exact"),
        ROOT_CENTER,
        "root center",
    )
    inverse = krawczyk.get("approximate_inverse_fraction_exact")
    if not isinstance(inverse, list) or len(inverse) != AXIS_COUNT:
        raise ValueError("approximate inverse violates the dimension cap")
    for row, expected in zip(inverse, APPROXIMATE_INVERSE):
        _validate_fraction_list(row, expected, "approximate inverse row")
    for key, x_radius, time_radius, function_absolute_cap in (
        (
            "fixed_schedule_root_localization",
            FIXED_ROOT_RADIUS,
            Fraction(0),
            FIXED_FUNCTION_ABSOLUTE_CAP,
        ),
        (
            "uniform_schedule_chamber",
            PARAMETER_X_RADIUS,
            PARAMETER_TIME_RADIUS,
            PARAMETER_FUNCTION_ABSOLUTE_CAP,
        ),
    ):
        section = krawczyk.get(key)
        if not isinstance(section, dict):
            raise ValueError(f"{key} is malformed")
        if _parse_fraction_limited(section.get("x_radius_exact")) != x_radius:
            raise ValueError(f"{key} has a noncanonical x radius")
        if _parse_fraction_limited(section.get("time_radius_exact")) != time_radius:
            raise ValueError(f"{key} has a noncanonical time radius")
        if (
            _parse_fraction_limited(
                section.get("function_absolute_value_cap_exact")
            )
            != function_absolute_cap
        ):
            raise ValueError(f"{key} has a noncanonical function absolute cap")
        function_checks = section.get(
            "function_absolute_value_coordinate_checks"
        )
        if (
            not isinstance(function_checks, list)
            or len(function_checks) != AXIS_COUNT
            or not all(type(value) is bool for value in function_checks)
        ):
            raise ValueError(
                f"{key} function absolute checks violate exact typing"
            )
        inclusions = section.get("coordinate_interior_inclusions")
        if (
            not isinstance(inclusions, list)
            or len(inclusions) != AXIS_COUNT
            or not all(type(value) is bool for value in inclusions)
        ):
            raise ValueError(f"{key} inclusion list violates exact typing")

    implementation = payload["implementation"]
    if not isinstance(implementation, dict):
        raise ValueError("implementation field must be an object")
    precision = implementation.get("arb_precision_bits")
    if type(precision) is not int or precision != FORMAL_PRECISION_BITS:
        raise ValueError("stored artifact does not use the pinned precision")
    if implementation.get("python_flint_version") != PINNED_PYTHON_FLINT_VERSION:
        raise ValueError("stored artifact has the wrong python-flint pin")
    if implementation.get("flint_version") != PINNED_FLINT_VERSION:
        raise ValueError("stored artifact has the wrong FLINT pin")
    if type(payload.get("overall_passed")) is not bool:
        raise ValueError("overall_passed must be a JSON boolean")
    if len(_pretty_json(artifact)) > MAX_ARTIFACT_BYTES:
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
        "phase_residual_record_count": 9,
        "phase_time_radius_exact": _fraction_text(PHASE_TIME_RADIUS),
        "parameter_time_radius_exact": _fraction_text(PARAMETER_TIME_RADIUS),
        "parameter_x_radius_exact": _fraction_text(PARAMETER_X_RADIUS),
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
    if len(value.lstrip("-")) > 1235:
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
    _validate_resource_tree(value)
    if raw != _pretty_json(value):
        raise ValueError("artifact is not in the canonical deterministic JSON encoding")
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
    if args.write is not None:
        # Artifact files always use the one accepted canonical encoding.
        args.write.write_bytes(_pretty_json(result))
    else:
        rendered = (
            json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n"
            if args.compact
            else _pretty_json(result).decode("utf-8")
        )
        print(rendered, end="")


if __name__ == "__main__":
    main()
