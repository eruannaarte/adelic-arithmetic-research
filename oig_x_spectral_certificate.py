#!/usr/bin/env python3
"""Rigorous finite-band spectral certificates for the Stage IX phase Grams.

This laboratory has two deliberately separate parts.

* Arb ball arithmetic proves generalized-metric statements.  A lower bound
  is accepted only when every leading principal minor of ``G - L S`` is
  certainly positive.  An upper bound is a rational Rayleigh witness whose
  Arb enclosure is certainly below the reported rational number.
* NumPy and mpmath values are descriptive cross-checks.  They never decide a
  certificate, and numerical whitening is used only to discover witnesses.

The continuous result is not a parameter grid.  For the standard Gaussian
resolved chart, the one-cell lattice chart, and the interior atomic chart,
the normalized Grams on

    q >= 1,       tau >= 1,       and the atomic endpoint

all dominate an explicit truncated Laplace Gram.  This gives a continuum
late-atlas lower bound through K=8.  The early calibrated endpoint, general
lattice preparations, and the full reflecting-boundary family are outside
the proved continuous scope; fixed representatives are certified separately.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from fractions import Fraction
from typing import Iterable, Sequence

import mpmath as mp
import numpy as np
from flint import acb, arb, arb_mat, ctx, fmpq


INTERACTION_STRENGTH = Fraction(4, 5)
TRUNCATION_LIMIT = Fraction(40, 1)
MAX_CERTIFIED_BAND = 8
DEFAULT_PRECISION_BITS = 320
DEFAULT_QUADRATURE_ORDER = 80
FAST_QUADRATURE_ORDER = 48
RADIUS_CAP = Fraction(1, 10**34)

# These rational cutoffs were selected before the certificate run from a
# finite exploratory scan.  No optimality claim is made or needed.
COMMON_CORE_CUTOFFS = {
    1: Fraction(1, 1),
    2: Fraction(7, 4),
    3: Fraction(21, 8),
    4: Fraction(7, 2),
    5: Fraction(4, 1),
    6: Fraction(4, 1),
    7: Fraction(4, 1),
    8: Fraction(4, 1),
}

EFFECTIVE_RANK_THRESHOLDS = tuple(
    Fraction(1, 10**power) for power in (4, 8, 12, 16, 20, 24, 28)
)

FIXED_CHARTS = (
    "resolved_q1_normalized",
    "lattice_tau1_atom_normalized",
    "atomic_interior",
    "boundary_kappa1",
)


def _arb_rational(value: Fraction | int) -> arb:
    """Embed an exact rational in an outward-rounded Arb ball."""
    if isinstance(value, int):
        return arb(value)
    return arb(fmpq(value.numerator, value.denominator))


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _fraction_from_exact_dyadic(value: arb) -> Fraction:
    """Convert an exact Arb floating-point endpoint to a Python Fraction."""
    if not bool(value.rad() == 0):
        raise ValueError("expected an exact Arb endpoint")
    mantissa, exponent = value.man_exp()
    mantissa = int(mantissa)
    exponent = int(exponent)
    if exponent >= 0:
        return Fraction(mantissa * 2**exponent, 1)
    return Fraction(mantissa, 2 ** (-exponent))


def _ceil_fraction(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def _interval_text(value: arb, digits: int = 24) -> str:
    return value.str(digits, radius=True, more=True)


def _mp_from_arb_midpoint(value: arb, digits: int) -> mp.mpf:
    return mp.mpf(value.mid().str(digits, radius=False, more=True))


def truncated_laplace_kernel(A: arb, cutoff: Fraction | arb) -> arb:
    r"""Return K_b(A)=erf(sqrt(A b))/(2 sqrt(pi A)) in Arb."""
    b = cutoff if isinstance(cutoff, arb) else _arb_rational(cutoff)
    return (A * b).sqrt().erf() / (2 * (arb.pi() * A).sqrt())


def _phase_profile(mode: int, s: arb | acb) -> arb | acb:
    r"""Exact affine-ramp phase profile for sqrt(2) cos(k pi x)."""
    if mode < 1:
        raise ValueError("the certified source modes start at one")
    g = _arb_rational(INTERACTION_STRENGTH)
    pi = arb.pi()
    exponential = (-g * s).exp()
    if mode % 2 == 0:
        parity_factor = -(-g * s).expm1()  # 1-exp(-g s), stably at s=0
    else:
        parity_factor = 1 + exponential
    return (
        arb(2).sqrt()
        * (-s).exp()
        * (g * s)
        * parity_factor
        / ((g * s) ** 2 + (mode * pi) ** 2)
    )


def _integral(
    integrand,
    precision_bits: int,
) -> arb:
    tolerance = arb(2) ** (-(precision_bits - 32))
    result = acb.integral(
        integrand,
        arb(0),
        arb(1),
        rel_tol=tolerance,
        abs_tol=arb(2) ** (-precision_bits),
        eval_limit=20_000,
        depth_limit=30,
    )
    if not bool(result.imag.contains(0)):
        raise ArithmeticError("a real phase integral acquired nonzero imaginary part")
    return result.real


def _with_symmetric_error(value: arb, error: arb) -> arb:
    """Enlarge a ball by a proved nonnegative absolute error."""
    if not bool(error >= 0):
        raise ValueError("error bound must be certainly nonnegative")
    return arb(value.mid(), value.rad() + error.abs_upper())


def _common_core_entry(
    row_mode: int,
    column_mode: int,
    cutoff: Fraction,
    precision_bits: int,
) -> arb:
    b = _arb_rational(cutoff)
    coefficient = b.sqrt() / arb.pi()
    base = _integral(
        lambda r, _: _phase_profile(row_mode, b * r * r)
        * _phase_profile(column_mode, b * r * r),
        precision_bits,
    )

    # For b >= log(sqrt(2)), the resolved multiplier lower bound on q>=1 is
    # c_R(b)=sqrt(2) exp(-b).  Every declared cutoff satisfies this condition.
    resolved_constant = arb(2).sqrt() * (-b).exp()
    return resolved_constant * coefficient * base


def _fixed_chart_entry(
    chart: str,
    row_mode: int,
    column_mode: int,
    precision_bits: int,
) -> tuple[arb, arb]:
    B = _arb_rational(TRUNCATION_LIMIT)
    pi = arb.pi()
    zero = arb(0)

    if chart == "resolved_q1_normalized":
        coefficient = (2 * B).sqrt() / pi
        integral = _integral(
            lambda r, _: (-B * r * r).exp()
            * _phase_profile(row_mode, B * r * r)
            * _phase_profile(column_mode, B * r * r),
            precision_bits,
        )
        tail = (
            arb(2).sqrt()
            * (-3 * B).exp()
            / (6 * pi * B.sqrt())
        )
    elif chart == "lattice_tau1_atom_normalized":
        coefficient = arb(2).sqrt()
        integral = _integral(
            lambda r, _: _phase_profile(
                row_mode, 4 * (pi * r / 2).sin() ** 2
            )
            * _phase_profile(
                column_mode, 4 * (pi * r / 2).sin() ** 2
            ),
            precision_bits,
        )
        tail = zero
    elif chart == "atomic_interior":
        coefficient = B.sqrt() / pi
        integral = _integral(
            lambda r, _: _phase_profile(row_mode, B * r * r)
            * _phase_profile(column_mode, B * r * r),
            precision_bits,
        )
        tail = (-2 * B).exp() / (4 * pi * B.sqrt())
    elif chart == "boundary_kappa1":
        coefficient = B.sqrt() / pi
        integral = _integral(
            lambda r, _: (1 + (2 * B.sqrt() * r).cos())
            * _phase_profile(row_mode, B * r * r)
            * _phase_profile(column_mode, B * r * r),
            precision_bits,
        )
        tail = (-2 * B).exp() / (2 * pi * B.sqrt())
    else:
        raise ValueError(f"unknown fixed chart: {chart}")

    return _with_symmetric_error(coefficient * integral, tail), tail


def _symmetric_matrix(
    dimension: int,
    entry_builder,
) -> arb_mat:
    matrix = arb_mat(dimension, dimension)
    for row in range(dimension):
        for column in range(row + 1):
            value = entry_builder(row + 1, column + 1)
            matrix[row, column] = value
            matrix[column, row] = value
    return matrix


def _principal_block(matrix: arb_mat, dimension: int) -> arb_mat:
    return arb_mat(
        [[matrix[row, column] for column in range(dimension)] for row in range(dimension)]
    )


def source_metric(metric: str, dimension: int) -> arb_mat:
    """Return the declared L2 or continuum H1 source-cost Gram."""
    if metric not in {"L2", "H1"}:
        raise ValueError("metric must be L2 or H1")
    pi = arb.pi()
    result = arb_mat(dimension, dimension)
    for index in range(dimension):
        if metric == "L2":
            result[index, index] = 1
        else:
            mode = index + 1
            result[index, index] = 1 + (mode * pi) ** 2
    return result


def _leading_principal_determinants(matrix: arb_mat) -> list[arb]:
    dimension = matrix.nrows()
    return [
        _principal_block(matrix, size).det() for size in range(1, dimension + 1)
    ]


def certify_generalized_lower_bound(
    gram: arb_mat,
    metric: arb_mat,
    lower_bound: Fraction,
) -> dict[str, object]:
    r"""Certify G-LS positive definite directly by Sylvester's criterion."""
    if gram.nrows() != gram.ncols() or metric.nrows() != gram.nrows():
        raise ValueError("gram and metric dimensions do not match")
    L = _arb_rational(lower_bound)
    shifted = gram - metric * L
    determinants = _leading_principal_determinants(shifted)
    signs = [1 if bool(value > 0) else -1 if bool(value < 0) else 0 for value in determinants]
    return {
        "method": "direct Sylvester test on the interval matrix G - L S",
        "lower_bound_exact": _fraction_text(lower_bound),
        "leading_principal_minor_signs": signs,
        "leading_principal_minor_intervals": [
            _interval_text(value) for value in determinants
        ],
        "every_leading_principal_minor_certainly_positive": all(
            sign == 1 for sign in signs
        ),
        "passed": all(sign == 1 for sign in signs),
    }


def _rayleigh_interval(
    gram: arb_mat,
    metric: arb_mat,
    witness: Sequence[int],
) -> arb:
    dimension = gram.nrows()
    if len(witness) != dimension or not any(witness):
        raise ValueError("witness has the wrong dimension or is zero")
    numerator = arb(0)
    denominator = arb(0)
    for row in range(dimension):
        for column in range(dimension):
            numerator += witness[row] * gram[row, column] * witness[column]
            denominator += witness[row] * metric[row, column] * witness[column]
    if not bool(denominator > 0):
        raise ArithmeticError("source metric is not certainly positive on witness")
    return numerator / denominator


def _mp_matrix_from_arb_midpoints(matrix: arb_mat, digits: int) -> mp.matrix:
    return mp.matrix(
        [
            [_mp_from_arb_midpoint(matrix[row, column], digits) for column in range(matrix.ncols())]
            for row in range(matrix.nrows())
        ]
    )


def _mp_generalized_eigenpair_from_arb(
    gram: arb_mat,
    metric_name: str,
    digits: int,
) -> tuple[mp.mpf, list[mp.mpf]]:
    """Descriptive eigensolve used only to discover a rational witness."""
    dimension = gram.nrows()
    matrix = _mp_matrix_from_arb_midpoints(gram, digits)
    diagonal = [
        mp.mpf(1)
        if metric_name == "L2"
        else mp.mpf(1) + ((index + 1) * mp.pi) ** 2
        for index in range(dimension)
    ]
    whitened = mp.matrix(dimension)
    for row in range(dimension):
        for column in range(dimension):
            whitened[row, column] = matrix[row, column] / mp.sqrt(
                diagonal[row] * diagonal[column]
            )
    values, vectors = mp.eigsy(whitened)
    original_vector = [
        vectors[index, 0] / mp.sqrt(diagonal[index]) for index in range(dimension)
    ]
    return values[0], original_vector


def _integer_witness(vector: Sequence[mp.mpf], scale: int = 10**24) -> tuple[int, ...]:
    maximum = max(abs(value) for value in vector)
    if maximum == 0:
        raise ArithmeticError("numerical eigensolver returned a zero vector")
    witness = tuple(int(mp.nint(scale * value / maximum)) for value in vector)
    if not any(witness):
        raise ArithmeticError("integer rounding erased the witness")
    first_nonzero = next(value for value in witness if value)
    if first_nonzero < 0:
        witness = tuple(-value for value in witness)
    return witness


def _upper_certificate(
    gram: arb_mat,
    metric: arb_mat,
    witness: Sequence[int],
    precision_bits: int,
) -> dict[str, object]:
    quotient = _rayleigh_interval(gram, metric, witness)
    if not bool(quotient > 0):
        raise ArithmeticError("Rayleigh witness is not certainly positive")
    endpoint = _fraction_from_exact_dyadic(quotient.upper())
    slack = endpoint / 2**40 + Fraction(1, 2**precision_bits)
    upper = endpoint + slack
    passed = bool(quotient < _arb_rational(upper))
    return {
        "method": "integer-vector Rayleigh witness checked in Arb",
        "witness": [str(value) for value in witness],
        "rayleigh_interval": _interval_text(quotient),
        "upper_bound_exact": _fraction_text(upper),
        "rayleigh_certainly_below_upper": passed,
        "passed": passed,
    }


def _lower_candidate_from_mpmath(value: mp.mpf) -> Fraction:
    if not value > 0:
        raise ArithmeticError("descriptive minimum eigenvalue is not positive")
    return Fraction(mp.nstr(value * mp.mpf("0.45"), 60))


def _certified_bracket(
    gram: arb_mat,
    metric_name: str,
    precision_bits: int,
) -> tuple[dict[str, object], mp.mpf]:
    metric = source_metric(metric_name, gram.nrows())
    descriptive_value, vector = _mp_generalized_eigenpair_from_arb(
        gram, metric_name, max(80, precision_bits // 3)
    )
    lower = _lower_candidate_from_mpmath(descriptive_value)
    lower_certificate = certify_generalized_lower_bound(gram, metric, lower)
    attempts = 0
    while not lower_certificate["passed"] and attempts < 12:
        lower /= 2
        lower_certificate = certify_generalized_lower_bound(gram, metric, lower)
        attempts += 1
    if not lower_certificate["passed"]:
        raise ArithmeticError("could not certify a positive generalized lower bound")

    witness = _integer_witness(vector)
    upper_certificate = _upper_certificate(
        gram, metric, witness, precision_bits
    )
    if not upper_certificate["passed"]:
        raise ArithmeticError("could not certify the rational Rayleigh upper bound")

    result = {
        "metric": metric_name,
        "lower_bound_exact": lower_certificate["lower_bound_exact"],
        "upper_bound_exact": upper_certificate["upper_bound_exact"],
        "lower_bound_approx": float(lower),
        "upper_bound_approx": float(
            Fraction(upper_certificate["upper_bound_exact"])
        ),
        "generalized_shift_certificate": lower_certificate,
        "rayleigh_upper_certificate": upper_certificate,
        "discovery_eigenvalue": mp.nstr(descriptive_value, 30),
        "passed": bool(lower_certificate["passed"] and upper_certificate["passed"]),
    }
    return result, descriptive_value


def _generalized_inertia(
    gram: arb_mat,
    metric: arb_mat,
    threshold: Fraction,
) -> dict[str, object]:
    shifted = gram - metric * _arb_rational(threshold)
    determinants = _leading_principal_determinants(shifted)
    signs = [1]
    intervals = []
    for determinant in determinants:
        intervals.append(_interval_text(determinant, 16))
        if bool(determinant > 0):
            signs.append(1)
        elif bool(determinant < 0):
            signs.append(-1)
        else:
            signs.append(0)
    certified = 0 not in signs
    if certified:
        negative = sum(left != right for left, right in zip(signs, signs[1:]))
        above = gram.nrows() - negative
    else:
        negative = None
        above = None
    return {
        "threshold_exact": _fraction_text(threshold),
        "threshold_approx": float(threshold),
        "leading_minor_signs_with_delta0": signs,
        "leading_minor_intervals": intervals,
        "certified": certified,
        "negative_shift_inertia": negative,
        "generalized_eigenvalues_strictly_above_threshold": above,
    }


def _effective_rank_table(
    gram: arb_mat,
    metric: arb_mat,
) -> list[dict[str, object]]:
    return [
        _generalized_inertia(gram, metric, threshold)
        for threshold in EFFECTIVE_RANK_THRESHOLDS
    ]


def _radius_audit(matrices: Iterable[arb_mat]) -> dict[str, object]:
    cap = _arb_rational(RADIUS_CAP)
    count = 0
    maximum = 0.0
    every_below = True
    for matrix in matrices:
        for value in matrix.entries():
            count += 1
            radius = value.rad()
            maximum = max(maximum, float(radius))
            every_below = every_below and bool(radius < cap)
    return {
        "entry_count": count,
        "approximate_maximum_total_radius": maximum,
        "exact_total_radius_cap": _fraction_text(RADIUS_CAP),
        "every_total_radius_strictly_below_cap": every_below,
    }


def _mp_phase_profile(mode: int, s: mp.mpf) -> mp.mpf:
    g = mp.mpf(4) / 5
    if mode % 2 == 0:
        parity_factor = -mp.expm1(-g * s)
    else:
        parity_factor = 1 + mp.exp(-g * s)
    return (
        mp.sqrt(2)
        * mp.exp(-s)
        * g
        * s
        * parity_factor
        / ((g * s) ** 2 + (mode * mp.pi) ** 2)
    )


def _mp_gauss_legendre(order: int) -> tuple[list[mp.mpf], list[mp.mpf]]:
    nodes, weights = mp.gauss_quadrature(order, "legendre")
    return (
        [(nodes[index] + 1) / 2 for index in range(order)],
        [weights[index] / 2 for index in range(order)],
    )


def _mp_phase_matrix(
    chart: str,
    dimension: int,
    nodes: Sequence[mp.mpf],
    weights: Sequence[mp.mpf],
    cutoff: Fraction | None = None,
) -> mp.matrix:
    B = mp.mpf(TRUNCATION_LIMIT.numerator) / TRUNCATION_LIMIT.denominator
    if chart == "common_core":
        if cutoff is None:
            raise ValueError("common core requires a cutoff")
        b = mp.mpf(cutoff.numerator) / cutoff.denominator
        coefficient = mp.sqrt(2) * mp.exp(-b) * mp.sqrt(b) / mp.pi

        def sample(mode: int, r: mp.mpf) -> mp.mpf:
            return _mp_phase_profile(mode, b * r * r)

        multiplier = lambda r: mp.mpf(1)
    elif chart == "resolved_q1_normalized":
        coefficient = mp.sqrt(2 * B) / mp.pi
        sample = lambda mode, r: _mp_phase_profile(mode, B * r * r)
        multiplier = lambda r: mp.exp(-B * r * r)
    elif chart == "lattice_tau1_atom_normalized":
        coefficient = mp.sqrt(2)
        sample = lambda mode, r: _mp_phase_profile(
            mode, 4 * mp.sin(mp.pi * r / 2) ** 2
        )
        multiplier = lambda r: mp.mpf(1)
    elif chart == "atomic_interior":
        coefficient = mp.sqrt(B) / mp.pi
        sample = lambda mode, r: _mp_phase_profile(mode, B * r * r)
        multiplier = lambda r: mp.mpf(1)
    elif chart == "boundary_kappa1":
        coefficient = mp.sqrt(B) / mp.pi
        sample = lambda mode, r: _mp_phase_profile(mode, B * r * r)
        multiplier = lambda r: 1 + mp.cos(2 * mp.sqrt(B) * r)
    else:
        raise ValueError(f"unknown mpmath chart: {chart}")

    values = [[sample(mode + 1, r) for mode in range(dimension)] for r in nodes]
    matrix = mp.matrix(dimension)
    for row in range(dimension):
        for column in range(row + 1):
            value = coefficient * mp.fsum(
                weight
                * multiplier(node)
                * samples[row]
                * samples[column]
                for node, weight, samples in zip(nodes, weights, values)
            )
            matrix[row, column] = value
            matrix[column, row] = value
    return matrix


def _descriptive_generalized_minimum(
    matrix: mp.matrix,
    metric_name: str,
) -> tuple[mp.mpf, float]:
    dimension = matrix.rows
    diagonal = [
        mp.mpf(1)
        if metric_name == "L2"
        else 1 + ((index + 1) * mp.pi) ** 2
        for index in range(dimension)
    ]
    whitened = mp.matrix(dimension)
    binary64 = np.empty((dimension, dimension), dtype=float)
    for row in range(dimension):
        for column in range(dimension):
            value = matrix[row, column] / mp.sqrt(diagonal[row] * diagonal[column])
            whitened[row, column] = value
            binary64[row, column] = float(value)
    values, _ = mp.eigsy(whitened)
    return values[0], float(np.linalg.eigvalsh(binary64)[0])


def _comparison_record(
    matrix: mp.matrix,
    metric_name: str,
    lower: Fraction,
    upper: Fraction,
) -> dict[str, object]:
    high_precision, binary64 = _descriptive_generalized_minimum(matrix, metric_name)
    inside = mp.mpf(lower.numerator) / lower.denominator < high_precision < (
        mp.mpf(upper.numerator) / upper.denominator
    )
    relative_error = (
        abs(mp.mpf(binary64) - high_precision) / abs(high_precision)
        if high_precision != 0
        else mp.inf
    )
    return {
        "mpmath_digits": mp.mp.dps,
        "mpmath_minimum": mp.nstr(high_precision, 35),
        "binary64_minimum": binary64,
        "binary64_relative_error_vs_mpmath": mp.nstr(relative_error, 12),
        "mpmath_value_strictly_inside_arb_bracket": bool(inside),
        "role": "descriptive cross-check only",
    }


def _noise_budget(lower: Fraction, upper: Fraction) -> dict[str, object]:
    """Rigorous repeat bracket for a declared Gaussian testing example."""
    sigma = Fraction(1, 1000)
    amplitude = Fraction(1, 1)
    alpha = Fraction(1, 20)
    z = arb(2).sqrt() * _arb_rational(Fraction(9, 10)).erfinv()
    constant = (
        4
        * _arb_rational(sigma) ** 2
        * z**2
        / _arb_rational(amplitude) ** 2
    )
    sufficient_ratio = constant / _arb_rational(lower)
    necessary_ratio = constant / _arb_rational(upper)
    sufficient = _ceil_fraction(
        _fraction_from_exact_dyadic(sufficient_ratio.upper())
    )
    necessary = _ceil_fraction(
        _fraction_from_exact_dyadic(necessary_ratio.lower())
    )
    sufficient_verified = bool(
        _arb_rational(lower) * sufficient > constant
        or _arb_rational(lower) * sufficient == constant
    )
    return {
        "model": "simple Gaussian discrimination in the declared source/output metrics",
        "amplitude_exact": _fraction_text(amplitude),
        "noise_sigma_exact": _fraction_text(sigma),
        "one_sided_error_alpha_exact": _fraction_text(alpha),
        "normal_quantile_interval": _interval_text(z),
        "necessary_uniform_repeats_at_least": necessary,
        "sufficient_uniform_repeats_at_most": sufficient,
        "necessary_ratio_interval": _interval_text(necessary_ratio),
        "sufficient_ratio_interval": _interval_text(sufficient_ratio),
        "sufficient_inequality_verified_in_arb": sufficient_verified,
        "interpretation": (
            "the atlas upper witness gives the necessary lower repeat count; "
            "the continuum common-core lower bound gives the sufficient count"
        ),
        "passed": bool(necessary <= sufficient and sufficient_verified),
    }


def _certificate_bounds(row: dict[str, object]) -> tuple[Fraction, Fraction]:
    return Fraction(row["lower_bound_exact"]), Fraction(row["upper_bound_exact"])


def run_spectral_certificate(
    max_band: int = MAX_CERTIFIED_BAND,
    precision_bits: int = DEFAULT_PRECISION_BITS,
    fast: bool = False,
) -> dict[str, object]:
    """Run the complete deterministic Stage X finite-band certificate."""
    if not 1 <= max_band <= MAX_CERTIFIED_BAND:
        raise ValueError(f"max_band must lie in [1,{MAX_CERTIFIED_BAND}]")
    if precision_bits < 160:
        raise ValueError("precision_bits must be at least 160")

    previous_precision = ctx.prec
    previous_mp_dps = mp.mp.dps
    ctx.prec = precision_bits
    mp.mp.dps = max(80, precision_bits // 3)
    quadrature_order = FAST_QUADRATURE_ORDER if fast else DEFAULT_QUADRATURE_ORDER
    try:
        fixed_matrices: dict[str, arb_mat] = {}
        tail_bounds: dict[str, arb] = {}
        for chart in FIXED_CHARTS:
            per_entry_tails: list[arb] = []

            def entry(row_mode: int, column_mode: int, chart_name: str = chart) -> arb:
                value, tail = _fixed_chart_entry(
                    chart_name, row_mode, column_mode, precision_bits
                )
                per_entry_tails.append(tail)
                return value

            fixed_matrices[chart] = _symmetric_matrix(max_band, entry)
            tail_bounds[chart] = max(
                per_entry_tails, key=lambda value: float(value.mid())
            )

        nodes, weights = _mp_gauss_legendre(quadrature_order)
        mp_fixed = {
            chart: _mp_phase_matrix(chart, max_band, nodes, weights)
            for chart in FIXED_CHARTS
        }

        common_matrices: dict[int, arb_mat] = {}
        common_mp: dict[int, mp.matrix] = {}
        for dimension in range(1, max_band + 1):
            cutoff = COMMON_CORE_CUTOFFS[dimension]
            common_matrices[dimension] = _symmetric_matrix(
                dimension,
                lambda row_mode, column_mode, b=cutoff: _common_core_entry(
                    row_mode, column_mode, b, precision_bits
                ),
            )
            common_mp[dimension] = _mp_phase_matrix(
                "common_core", dimension, nodes, weights, cutoff
            )

        fixed_rows: list[dict[str, object]] = []
        fixed_lookup: dict[tuple[str, int, str], dict[str, object]] = {}
        for chart in FIXED_CHARTS:
            for dimension in range(1, max_band + 1):
                gram = _principal_block(fixed_matrices[chart], dimension)
                mp_gram = mp.matrix(
                    [
                        [mp_fixed[chart][row, column] for column in range(dimension)]
                        for row in range(dimension)
                    ]
                )
                for metric_name in ("L2", "H1"):
                    bracket, _ = _certified_bracket(
                        gram, metric_name, precision_bits
                    )
                    lower, upper = _certificate_bounds(bracket)
                    metric = source_metric(metric_name, dimension)
                    row = {
                        "chart": chart,
                        "band_dimension": dimension,
                        **bracket,
                        "effective_rank": _effective_rank_table(gram, metric),
                        "comparison": _comparison_record(
                            mp_gram, metric_name, lower, upper
                        ),
                    }
                    row["passed"] = bool(
                        row["passed"]
                        and row["comparison"][
                            "mpmath_value_strictly_inside_arb_bracket"
                        ]
                        and all(
                            rank["certified"] for rank in row["effective_rank"]
                        )
                    )
                    fixed_rows.append(row)
                    fixed_lookup[(chart, dimension, metric_name)] = row

        uniform_rows: list[dict[str, object]] = []
        for dimension in range(1, max_band + 1):
            cutoff = COMMON_CORE_CUTOFFS[dimension]
            core = common_matrices[dimension]
            for metric_name in ("L2", "H1"):
                core_bracket, _ = _certified_bracket(
                    core, metric_name, precision_bits
                )
                core_lower, core_upper = _certificate_bounds(core_bracket)
                covered_witness_rows = [
                    fixed_lookup[(chart, dimension, metric_name)]
                    for chart in FIXED_CHARTS[:3]
                ]
                best_witness_row = min(
                    covered_witness_rows,
                    key=lambda row: Fraction(row["upper_bound_exact"]),
                )
                atlas_upper = Fraction(best_witness_row["upper_bound_exact"])
                metric = source_metric(metric_name, dimension)
                comparison = _comparison_record(
                    common_mp[dimension], metric_name, core_lower, core_upper
                )
                effective_rank = _effective_rank_table(core, metric)
                noise = _noise_budget(core_lower, atlas_upper)
                cutoff_ball = _arb_rational(cutoff)
                resolved_constant = arb(2).sqrt() * (-cutoff_ball).exp()
                row = {
                    "band_dimension": dimension,
                    "metric": metric_name,
                    "cutoff_b_exact": _fraction_text(cutoff),
                    "resolved_domination_constant_interval": _interval_text(
                        resolved_constant
                    ),
                    "atlas_lower_bound_exact": _fraction_text(core_lower),
                    "atlas_upper_bound_exact": _fraction_text(atlas_upper),
                    "atlas_lower_bound_approx": float(core_lower),
                    "atlas_upper_bound_approx": float(atlas_upper),
                    "atlas_upper_witness_chart": best_witness_row["chart"],
                    "common_core_spectral_bracket": core_bracket,
                    "uniform_effective_rank_lower_bound": effective_rank,
                    "comparison": comparison,
                    "noise_budget": noise,
                    "generalized_metric_proof": (
                        "the reported lower bound is proved by G_core-L*S "
                        "positive definite, followed by Loewner domination"
                    ),
                }
                row["passed"] = bool(
                    core_bracket["passed"]
                    and comparison["mpmath_value_strictly_inside_arb_bracket"]
                    and all(rank["certified"] for rank in effective_rank)
                    and noise["passed"]
                    and core_lower < atlas_upper
                )
                uniform_rows.append(row)

        matrices_for_radius = list(fixed_matrices.values()) + list(
            common_matrices.values()
        )
        radius = _radius_audit(matrices_for_radius)
        tail_report = {
            chart: {
                "per_entry_absolute_tail_bound_interval": _interval_text(bound),
                "tail_is_zero": bool(bound == 0),
            }
            for chart, bound in tail_bounds.items()
        }

        scope = {
            "continuous_late_atlas": {
                "resolved": (
                    "standard Gaussian, sqrt(1+q)-normalized Gram, every q>=1"
                ),
                "lattice": (
                    "one-cell Q=delta_0, sqrt(1+tau)-normalized Gram, every tau>=1"
                ),
                "atomic": "interior atomic endpoint",
                "parameter_sampling_used_for_lower_bound": False,
                "common_core": (
                    "c_R(b) H_b, where c_R(b)=sqrt(2) exp(-b) and "
                    "H_b=(2 pi)^-1 integral_0^b s^-1/2 F(s)^*F(s) ds"
                ),
                "dominance_proof": (
                    "resolved: min over q>=1 and 0<=s<=b of "
                    "sqrt((1+q)/q) exp(-s/q) is min(1,sqrt(2)exp(-b)); "
                    "lattice: 2sqrt(1+tau)/sqrt(4tau-s)>=1 for tau>=1, "
                    "0<=s<=b<=4; atomic: its integral contains [0,b]"
                ),
            },
            "fixed_point_certificates": list(FIXED_CHARTS),
            "excluded_from_continuous_claim": [
                "the calibrated early resolved interval q in [0,1]",
                "general lattice preparations Q other than the one-cell atom",
                "the full boundary parameter family kappa in [0,infinity]",
                "finite-h phase remainders and any K tending to infinity",
                "bands K greater than eight",
            ],
            "boundary_and_early_assessment": (
                "A full boundary cover can in principle combine finite kappa "
                "boxes with the analytic kappa tail, but is not certified here. "
                "The q=0 endpoint additionally needs a rigorously constructed "
                "moment-adapted basis and scaled analytic remainder oracle; point "
                "chart arithmetic is not a substitute for that endpoint proof."
            ),
        }

        all_rows_pass = all(row["passed"] for row in uniform_rows) and all(
            row["passed"] for row in fixed_rows
        )
        return {
            "schema_version": "oig-x-spectral-certificate-v1",
            "status": "rigorous finite-K certificate",
            "environment": {
                "python": sys.version.split()[0],
                "platform": platform.platform(),
                "numpy": np.__version__,
                "mpmath": mp.__version__,
                "python_flint": __import__("flint").__version__,
                "arb_precision_bits": precision_bits,
                "mpmath_working_digits": mp.mp.dps,
                "gauss_legendre_order_descriptive_only": quadrature_order,
            },
            "model": {
                "modulation": "V(x)=1+(4/5)x",
                "ports": "phi_k(x)=sqrt(2) cos(k pi x), k=1,...,K",
                "exact_structural_null": (
                    "trivial on these bands because the affine ramp is strictly monotone"
                ),
                "output_metric": (
                    "the Stage IX phase-output L2 metric; the noise example declares "
                    "scalar white Gaussian variance separately"
                ),
                "source_metrics": {
                    "L2": "S=I",
                    "H1": "S_kk=1+(k pi)^2",
                },
                "full_integral_truncation_B_exact": _fraction_text(
                    TRUNCATION_LIMIT
                ),
                "truncated_kernel": (
                    "K_b(A)=erf(sqrt(A b))/(2 sqrt(pi A))"
                ),
            },
            "scope": scope,
            "tail_bounds": tail_report,
            "uniform_late_atlas_certificates": uniform_rows,
            "fixed_chart_certificates": fixed_rows,
            "radius_audit": radius,
            "proof_boundary": {
                "arb_decisions": (
                    "interval integration, analytic entrywise tails, direct "
                    "generalized shifts, Sylvester signs, inertia, and rational "
                    "Rayleigh witnesses"
                ),
                "descriptive_only": (
                    "mpmath quadrature/eigensolves and binary64 eigensolves"
                ),
                "no_asymptotic_claim": True,
            },
            "overall_passed": bool(
                all_rows_pass
                and radius["every_total_radius_strictly_below_cap"]
            ),
        }
    finally:
        ctx.prec = previous_precision
        mp.mp.dps = previous_mp_dps


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-band", type=int, default=MAX_CERTIFIED_BAND, choices=range(1, 9)
    )
    parser.add_argument(
        "--precision-bits", type=int, default=DEFAULT_PRECISION_BITS
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="use a smaller descriptive mpmath quadrature (Arb proof unchanged)",
    )
    parser.add_argument("--output", help="write JSON to this path instead of stdout")
    parser.add_argument("--compact", action="store_true", help="emit compact JSON")
    return parser.parse_args()


def main() -> None:
    arguments = _parse_arguments()
    report = run_spectral_certificate(
        max_band=arguments.max_band,
        precision_bits=arguments.precision_bits,
        fast=arguments.fast,
    )
    payload = json.dumps(
        report,
        indent=None if arguments.compact else 2,
        sort_keys=True,
    )
    if arguments.output:
        with open(arguments.output, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.write("\n")
    else:
        print(payload)
    if not report["overall_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
