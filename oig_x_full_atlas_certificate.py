#!/usr/bin/env python3
"""Rigorous K=2 full-atlas certificate for Operational Information Geometry.

The proof uses exact rational model data, Arb real-ball arithmetic, analytic
frame bounds, and an outward interval cover of the finite reflecting-boundary
coordinate.  It does not infer a lower bound from sampled eigenvalues.

Declared model
--------------

    V(x) = 1 + (4/5) x,
    phi_k(x) = sqrt(2) cos(k pi x),  k=1,2,
    S = I_2.

The same orthonormal cosine basis is moment adapted: phi_1 has pivot order
one and phi_2 has pivot order two.  The chart Gramians are

    early:    D(q)^-1 Gamma_R(q) D(q)^-1, D=diag(q,q^2), 0<=q<=1;
    resolved: sqrt(1+q) Gamma_R(q), q>=1;
    lattice:  sqrt(1+tau) Gamma_L(tau, delta_0), tau>=1;
    atomic:   Gamma_A(kappa), 0<=kappa<=infinity.

All comparisons that decide the certificate are Arb-ball comparisons with
exact rationals.  Binary64 values in the returned report are descriptive.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
import math
from typing import Sequence

import flint
from flint import arb, ctx, fmpq


DIMENSION = 2
RAMP_STRENGTH = Fraction(4, 5)
SOURCE_BASIS = (
    "sqrt(2) cos(pi x)",
    "sqrt(2) cos(2 pi x)",
)
SOURCE_METRIC = ((1, 0), (0, 1))
PIVOT_ORDERS = (1, 2)

EARLY_U_INTERVALS = (
    (Fraction(1, 5), Fraction(2, 5)),
    (Fraction(11, 20), Fraction(3, 4)),
)
LAPLACE_S_INTERVALS = (
    (Fraction(1, 4), Fraction(1, 2)),
    (Fraction(1, 1), Fraction(3, 2)),
)
LAPLACE_WINDOW = Fraction(3, 2)
BOUNDARY_R_INTERVALS = (
    (Fraction(2, 25), Fraction(11, 50)),
    (Fraction(27, 100), Fraction(1, 2)),
)

KAPPA_TAIL = Fraction(3, 1)
BOUNDARY_MASS_FLOOR = Fraction(1, 100)
GLOBAL_LOWER_BOUND = Fraction(1, 10**19)
GLOBAL_UPPER_BOUND = Fraction(1, 10**6)
UPPER_WITNESS_BOXES = 1024

MINIMUM_PRECISION_BITS = 128
DEFAULT_PRECISION_BITS = 192
DEFAULT_KAPPA_BOXES_PER_UNIT = 256


def _arb_rational(value: Fraction | int) -> arb:
    """Embed an exact rational in Arb."""
    if isinstance(value, int):
        return arb(value)
    return arb(fmpq(value.numerator, value.denominator))


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _display_midpoint(value: arb) -> float:
    """Binary64 display only; never used in a proof decision."""
    return float(value.mid())


def _dyadic_kappa_box(index: int, boxes_per_unit: int) -> arb:
    """Return the exact box [index/n,(index+1)/n] for dyadic n."""
    if boxes_per_unit <= 0 or boxes_per_unit & (boxes_per_unit - 1):
        raise ValueError("kappa boxes per unit must be a positive power of two")
    if index < 0:
        raise ValueError("box index must be nonnegative")
    exponent = boxes_per_unit.bit_length() - 1
    # Midpoint=(2i+1)2^(-exponent-1), radius=2^(-exponent-1).
    return arb(
        (2 * index + 1, -exponent - 1),
        (1, -exponent - 1),
    )


def _ratio_r(s: arb) -> arb:
    """R(s)=F_2(s)/F_1(s) for the canonical ramp/cosine pair."""
    pi = arb.pi()
    a = _arb_rational(RAMP_STRENGTH) * s
    return (a / 2).tanh() * (a * a + pi * pi) / (
        a * a + 4 * pi * pi
    )


def _f1_lower_on_s_interval(lower: Fraction, upper: Fraction) -> arb:
    """Monotone-factor lower bound for F_1 on a positive s interval."""
    if not (Fraction(0) < lower < upper):
        raise ValueError("the Laplace interval must be positive and ordered")
    pi = arb.pi()
    g = _arb_rational(RAMP_STRENGTH)
    lo = _arb_rational(lower)
    hi = _arb_rational(upper)
    # F_1(s)=sqrt(2)e^-s g s(1+e^-gs)/((gs)^2+pi^2).
    return (
        arb(2).sqrt()
        * (-hi).exp()
        * g
        * lo
        / ((g * hi) ** 2 + pi**2)
    )


def _f1_lower_on_r_interval(lower: Fraction, upper: Fraction) -> arb:
    pi = arb.pi()
    lo_s = pi**2 * _arb_rational(lower) ** 2
    hi_s = pi**2 * _arb_rational(upper) ** 2
    g = _arb_rational(RAMP_STRENGTH)
    return (
        arb(2).sqrt()
        * (-hi_s).exp()
        * g
        * lo_s
        / ((g * hi_s) ** 2 + pi**2)
    )


def _boundary_mass(kappa: arb, lower: Fraction, upper: Fraction) -> arb:
    """Exact Arb enclosure of integral_I [1+cos(2 pi kappa r)] dr."""
    pi = arb.pi()
    lo = _arb_rational(lower)
    hi = _arb_rational(upper)
    # The sinc form is analytic at kappa=0 and avoids interval division by 0.
    return (
        hi
        - lo
        + hi * (2 * pi * hi * kappa).sinc()
        - lo * (2 * pi * lo * kappa).sinc()
    )


def _certify_boundary_masses(
    boxes_per_unit: int,
) -> dict[str, object]:
    """Cover 0<=kappa<=3 by Arb boxes and prove the analytic tail."""
    if boxes_per_unit <= 0 or boxes_per_unit & (boxes_per_unit - 1):
        raise ValueError("kappa boxes per unit must be a positive power of two")

    target = _arb_rational(BOUNDARY_MASS_FLOOR)
    box_count = int(KAPPA_TAIL) * boxes_per_unit
    rows = []
    for interval_index, interval in enumerate(BOUNDARY_R_INTERVALS):
        weakest_lower = math.inf
        weakest_index = -1
        for box_index in range(box_count):
            kappa = _dyadic_kappa_box(box_index, boxes_per_unit)
            mass = _boundary_mass(kappa, *interval)
            if not bool(mass > target):
                raise ArithmeticError(
                    "boundary mass interval failed on "
                    f"interval {interval_index}, box {box_index}: {mass}"
                )
            # Descriptive selection only; every proof decision was the Arb
            # comparison above.
            displayed_lower = float(mass.lower())
            if displayed_lower < weakest_lower:
                weakest_lower = displayed_lower
                weakest_index = box_index

        length = interval[1] - interval[0]
        tail_lower = _arb_rational(length) - 1 / (
            arb.pi() * _arb_rational(KAPPA_TAIL)
        )
        if not bool(tail_lower > target):
            raise ArithmeticError(
                f"boundary tail mass failed for interval {interval_index}"
            )

        rows.append(
            {
                "r_interval": [
                    _fraction_text(interval[0]),
                    _fraction_text(interval[1]),
                ],
                "finite_cover": [
                    "0",
                    _fraction_text(KAPPA_TAIL),
                ],
                "box_count": box_count,
                "weakest_box_index_descriptive": weakest_index,
                "weakest_box_lower_descriptive": weakest_lower,
                "tail_lower_interval": str(tail_lower),
                "verified_above_mass_floor": True,
            }
        )

    return {
        "mass_floor": _fraction_text(BOUNDARY_MASS_FLOOR),
        "boxes_per_unit": boxes_per_unit,
        "total_boxes_checked": len(BOUNDARY_R_INTERVALS) * box_count,
        "intervals": rows,
        "tail_inequality": (
            "mass_I(kappa) >= |I|-1/(pi*kappa), kappa>=3"
        ),
        "verified": True,
    }


def _early_frame_floor() -> dict[str, object]:
    """Uniform lower bound for the calibrated resolved Gram on 0<=q<=1."""
    pi = arb.pi()
    g = _arb_rational(RAMP_STRENGTH)
    (u1_lo, u1_hi), (u2_lo, u2_hi) = EARLY_U_INTERVALS

    def a1_lower(lo: Fraction, hi: Fraction) -> arb:
        hi_s = pi**2 * _arb_rational(hi) ** 2
        return (
            arb(2).sqrt()
            * (-hi_s).exp()
            * g
            * pi**2
            * _arb_rational(lo) ** 2
            / ((g * hi_s) ** 2 + pi**2)
        )

    a1_first = a1_lower(u1_lo, u1_hi)
    a1_second = a1_lower(u2_lo, u2_hi)
    maximum_s = pi**2 * _arb_rational(u2_hi) ** 2

    # R'(s)>=g/8 sech^2(g*s_max/2).  Since
    # s_2-s_1 >= pi^2 q (u2_lo^2-u1_hi^2), division by q is harmless.
    derivative_lower = g / 8 / (g * maximum_s / 2).cosh() ** 2
    ratio_gap_after_calibration = (
        pi**2
        * (
            _arb_rational(u2_lo) ** 2
            - _arb_rational(u1_hi) ** 2
        )
        * derivative_lower
    )
    response_determinant_lower = (
        a1_first * a1_second * ratio_gap_after_calibration
    )

    first_mass = (
        _arb_rational(u1_hi - u1_lo)
        * (-(pi * _arb_rational(u1_hi)) ** 2).exp()
    )
    second_mass = (
        _arb_rational(u2_hi - u2_lo)
        * (-(pi * _arb_rational(u2_hi)) ** 2).exp()
    )

    # A_1<=2sqrt(2)g u^2 and
    # A_2<=sqrt(2)g^2 pi^2 u^4/4.
    integral_u4 = 3 / (8 * pi**4 * pi.sqrt())
    integral_u8 = 105 / (32 * pi**8 * pi.sqrt())
    trace_upper = (
        8 * g**2 * integral_u4
        + g**4 * pi**4 / 8 * integral_u8
    )
    floor = (
        response_determinant_lower**2
        * first_mass
        * second_mass
        / trace_upper
    )

    if not bool(floor > _arb_rational(GLOBAL_LOWER_BOUND)):
        raise ArithmeticError(f"early chart floor did not close: {floor}")

    return {
        "q_interval": ["0", "1"],
        "normalization": "D(q)^-1 Gamma_R(q) D(q)^-1",
        "D": ["q", "q^2"],
        "u_intervals": [
            [_fraction_text(value) for value in interval]
            for interval in EARLY_U_INTERVALS
        ],
        "a1_lower_intervals": [str(a1_first), str(a1_second)],
        "ratio_gap_after_calibration_interval": str(
            ratio_gap_after_calibration
        ),
        "response_determinant_lower_interval": str(
            response_determinant_lower
        ),
        "output_mass_lower_intervals": [
            str(first_mass),
            str(second_mass),
        ],
        "trace_upper_interval": str(trace_upper),
        "lambda_floor_interval": str(floor),
        "lambda_floor_approximate": _display_midpoint(floor),
        "verified_above_global_lower": True,
        "endpoint_handling": (
            "the divided columns extend continuously to q=0; all inequalities "
            "were derived after symbolic cancellation of q"
        ),
    }


def _laplace_frame_floor() -> dict[str, object]:
    """Certify the common H_b lower used by both late interior charts."""
    pi = arb.pi()
    (s1_lo, s1_hi), (s2_lo, s2_hi) = LAPLACE_S_INTERVALS

    f1_first = _f1_lower_on_s_interval(s1_lo, s1_hi)
    f1_second = _f1_lower_on_s_interval(s2_lo, s2_hi)
    ratio_gap = _ratio_r(_arb_rational(s2_lo)) - _ratio_r(
        _arb_rational(s1_hi)
    )
    if not bool(ratio_gap > 0):
        raise ArithmeticError(f"Laplace ratio separation failed: {ratio_gap}")

    response_determinant_lower = f1_first * f1_second * ratio_gap
    first_mass = (
        _arb_rational(s1_hi).sqrt()
        - _arb_rational(s1_lo).sqrt()
    ) / pi
    second_mass = (
        _arb_rational(s2_hi).sqrt()
        - _arb_rational(s2_lo).sqrt()
    ) / pi

    # |F_k(s)|<=e^-s because ||sqrt(2)cos(k pi x)||_1<1.
    trace_upper = 1 / (arb(2) * pi).sqrt()
    floor = (
        response_determinant_lower**2
        * first_mass
        * second_mass
        / trace_upper
    )
    if not bool(floor > _arb_rational(GLOBAL_LOWER_BOUND)):
        raise ArithmeticError(f"H_b floor did not close: {floor}")

    return {
        "b": _fraction_text(LAPLACE_WINDOW),
        "s_intervals": [
            [_fraction_text(value) for value in interval]
            for interval in LAPLACE_S_INTERVALS
        ],
        "f1_lower_intervals": [str(f1_first), str(f1_second)],
        "ratio_gap_interval": str(ratio_gap),
        "response_determinant_lower_interval": str(
            response_determinant_lower
        ),
        "measure_mass_lower_intervals": [
            str(first_mass),
            str(second_mass),
        ],
        "trace_upper_interval": str(trace_upper),
        "lambda_floor_interval": str(floor),
        "lambda_floor_approximate": _display_midpoint(floor),
        "verified_above_global_lower": True,
    }


def _late_chart_floors(
    laplace_floor: dict[str, object],
) -> dict[str, object]:
    """Apply the common-window Loewner reductions."""
    pi = arb.pi()
    del pi  # Keeps every transcendental constant constructed under workprec.
    b = _arb_rational(LAPLACE_WINDOW)
    resolved_multiplier = arb(2).sqrt() * (-b).exp()
    if not bool(resolved_multiplier < 1):
        raise ArithmeticError("resolved common-window minimum was misselected")

    # Recompute the exact lower expression rather than parsing a report string.
    (s1_lo, s1_hi), (s2_lo, s2_hi) = LAPLACE_S_INTERVALS
    f1_first = _f1_lower_on_s_interval(s1_lo, s1_hi)
    f1_second = _f1_lower_on_s_interval(s2_lo, s2_hi)
    ratio_gap = _ratio_r(_arb_rational(s2_lo)) - _ratio_r(
        _arb_rational(s1_hi)
    )
    response_determinant_lower = f1_first * f1_second * ratio_gap
    first_mass = (
        _arb_rational(s1_hi).sqrt()
        - _arb_rational(s1_lo).sqrt()
    ) / arb.pi()
    second_mass = (
        _arb_rational(s2_hi).sqrt()
        - _arb_rational(s2_lo).sqrt()
    ) / arb.pi()
    h_floor = (
        response_determinant_lower**2
        * first_mass
        * second_mass
        / (1 / (arb(2) * arb.pi()).sqrt())
    )
    resolved_floor = resolved_multiplier * h_floor
    if not bool(resolved_floor > _arb_rational(GLOBAL_LOWER_BOUND)):
        raise ArithmeticError(
            f"late resolved chart floor did not close: {resolved_floor}"
        )
    if not bool(h_floor > _arb_rational(GLOBAL_LOWER_BOUND)):
        raise ArithmeticError(f"lattice chart floor did not close: {h_floor}")

    return {
        "resolved": {
            "q_interval": ["1", "infinity"],
            "normalization": "sqrt(1+q) Gamma_R(q)",
            "common_window_multiplier_interval": str(resolved_multiplier),
            "lambda_floor_interval": str(resolved_floor),
            "lambda_floor_approximate": _display_midpoint(resolved_floor),
            "verified_above_global_lower": True,
            "tail_reduction": (
                "sqrt(1+q) Gamma_R(q) >= "
                "min(1,sqrt(2)e^-b) H_b for every q>=1"
            ),
        },
        "lattice": {
            "tau_interval": ["1", "infinity"],
            "preparation": "Q=delta_0",
            "normalization": "sqrt(1+tau) Gamma_L(tau,delta_0)",
            "lambda_floor_interval": str(h_floor),
            "lambda_floor_approximate": _display_midpoint(h_floor),
            "verified_above_global_lower": True,
            "tail_reduction": (
                "sqrt(1+tau) Gamma_L(tau,delta_0) >= H_b "
                "for every tau>=1 because b<=4"
            ),
        },
        "interior_atomic_control": {
            "normalization": "Gamma_A(infinity)",
            "lambda_floor_interval": str(h_floor),
            "verified_above_global_lower": True,
            "identity": "Gamma_A(infinity)=H_infinity>=H_b",
        },
    }


def _boundary_frame_floor(
    mass_certificate: dict[str, object],
) -> dict[str, object]:
    """Uniform lower bound for every 0<=kappa<=infinity."""
    del mass_certificate  # Its successful construction is the proof input.
    pi = arb.pi()
    (r1_lo, r1_hi), (r2_lo, r2_hi) = BOUNDARY_R_INTERVALS

    f1_first = _f1_lower_on_r_interval(r1_lo, r1_hi)
    f1_second = _f1_lower_on_r_interval(r2_lo, r2_hi)
    first_s_upper = pi**2 * _arb_rational(r1_hi) ** 2
    second_s_lower = pi**2 * _arb_rational(r2_lo) ** 2
    ratio_gap = _ratio_r(second_s_lower) - _ratio_r(first_s_upper)
    if not bool(ratio_gap > 0):
        raise ArithmeticError(f"boundary ratio separation failed: {ratio_gap}")

    response_determinant_lower = f1_first * f1_second * ratio_gap
    mass_floor = _arb_rational(BOUNDARY_MASS_FLOOR)

    # The boundary weight is at most two and |F_k(pi^2r^2)|<=e^-pi^2r^2.
    trace_upper = (arb(2) / pi).sqrt()
    floor = (
        response_determinant_lower**2
        * mass_floor**2
        / trace_upper
    )
    if not bool(floor > _arb_rational(GLOBAL_LOWER_BOUND)):
        raise ArithmeticError(f"boundary chart floor did not close: {floor}")

    return {
        "kappa_interval": ["0", "infinity"],
        "normalization": "Gamma_A(kappa)",
        "r_intervals": [
            [_fraction_text(value) for value in interval]
            for interval in BOUNDARY_R_INTERVALS
        ],
        "f1_lower_intervals": [str(f1_first), str(f1_second)],
        "ratio_gap_interval": str(ratio_gap),
        "response_determinant_lower_interval": str(
            response_determinant_lower
        ),
        "mass_floor_each_interval": _fraction_text(
            BOUNDARY_MASS_FLOOR
        ),
        "trace_upper_interval": str(trace_upper),
        "lambda_floor_interval": str(floor),
        "lambda_floor_approximate": _display_midpoint(floor),
        "verified_above_global_lower": True,
        "coverage": (
            "Arb boxes cover 0<=kappa<=3; "
            "|I|-1/(pi kappa) covers kappa>=3"
        ),
    }


def _upper_witness() -> dict[str, object]:
    """Enclose the q=1 Rayleigh quotient of the exact vector (1,-15)."""
    pi = arb.pi()
    g = _arb_rational(RAMP_STRENGTH)
    boxes = UPPER_WITNESS_BOXES
    exponent = boxes.bit_length() - 1
    width = arb((1, -exponent))
    integral_upper = arb(0)

    # At q=1, s=pi^2 u^2 and
    #
    # F_1=sqrt(2)e^-s a(1+e^-a)/(a^2+pi^2),
    # F_2=sqrt(2)e^-s a(1-e^-a)/(a^2+4pi^2), a=gs.
    #
    # On each exact dyadic u-box, Arb encloses the complete positive
    # integrand e^-s (F_1-15F_2)^2.  Its absolute upper endpoint times the
    # exact box width is a rigorous upper Riemann enclosure.
    for index in range(boxes):
        u = arb(
            (2 * index + 1, -exponent - 1),
            (1, -exponent - 1),
        )
        s = pi**2 * u**2
        a = g * s
        f1 = (
            arb(2).sqrt()
            * (-s).exp()
            * a
            * (1 + (-a).exp())
            / (a**2 + pi**2)
        )
        f2 = (
            arb(2).sqrt()
            * (-s).exp()
            * a
            * (1 - (-a).exp())
            / (a**2 + 4 * pi**2)
        )
        integrand = (-s).exp() * (f1 - 15 * f2) ** 2
        integral_upper += integrand.abs_upper() * width

    # For u>=1, |F_k(pi^2u^2)|<=e^-pi^2u^2, so the squared
    # (1,-15) response times the Gaussian output weight is at most
    # 256 e^(-3 pi^2 u^2).  The standard Gaussian tail inequality gives
    # integral_1^infinity e^(-a u^2)du <= e^-a/(2a).
    tail_upper = 256 * (-3 * pi**2).exp() / (6 * pi**2)
    numerator_upper = integral_upper + tail_upper
    source_norm_squared = 1 + 15**2
    rayleigh_upper = numerator_upper / source_norm_squared
    target = _arb_rational(GLOBAL_UPPER_BOUND)
    if not bool(rayleigh_upper < target):
        raise ArithmeticError(f"upper witness did not close: {rayleigh_upper}")
    return {
        "chart": "early resolved q=1",
        "source_vector": [1, -15],
        "source_metric_norm_squared": source_norm_squared,
        "finite_u_cover": ["0", "1"],
        "dyadic_box_count": boxes,
        "integral_upper_interval": str(integral_upper),
        "gaussian_tail_upper_interval": str(tail_upper),
        "rayleigh_upper_interval": str(rayleigh_upper),
        "rayleigh_upper_approximate": _display_midpoint(rayleigh_upper),
        "verified_below_global_upper": True,
    }


def ramp_scaling_audit() -> dict[str, int | str]:
    """Exact determinant exponents for the affine-ramp moment flag."""
    moment_determinant_power = DIMENSION * (DIMENSION + 1) // 2
    endpoint_gram_determinant_power = 2 * moment_determinant_power
    return {
        "dimension": DIMENSION,
        "moment_determinant_power_in_g": moment_determinant_power,
        "endpoint_gram_determinant_power_in_g": (
            endpoint_gram_determinant_power
        ),
        "identity": (
            "det M_K(1+g x)=g^(K(K+1)/2) "
            "det(<x^m,phi_k>)"
        ),
    }


def run_certificate(
    precision_bits: int = DEFAULT_PRECISION_BITS,
    kappa_boxes_per_unit: int = DEFAULT_KAPPA_BOXES_PER_UNIT,
) -> dict[str, object]:
    """Run and return the complete proof trace."""
    if precision_bits < MINIMUM_PRECISION_BITS:
        raise ValueError(
            f"at least {MINIMUM_PRECISION_BITS} precision bits are required"
        )
    if (
        kappa_boxes_per_unit <= 0
        or kappa_boxes_per_unit & (kappa_boxes_per_unit - 1)
    ):
        raise ValueError("kappa boxes per unit must be a positive power of two")

    with ctx.workprec(precision_bits):
        mass_certificate = _certify_boundary_masses(
            kappa_boxes_per_unit
        )
        early = _early_frame_floor()
        laplace = _laplace_frame_floor()
        late = _late_chart_floors(laplace)
        boundary = _boundary_frame_floor(mass_certificate)
        upper = _upper_witness()

        lower_target = _arb_rational(GLOBAL_LOWER_BOUND)
        upper_target = _arb_rational(GLOBAL_UPPER_BOUND)
        if not bool(lower_target < upper_target):
            raise ArithmeticError("declared certificate bracket is reversed")

        return {
            "certificate": "OIG-X-K2-full-compact-atlas-v1",
            "verified": True,
            "scope": (
                "continuum Stage IX phase Gramians only; no finite-grid "
                "transfer error is included"
            ),
            "runtime": {
                "python_flint_version": flint.__version__,
                "precision_bits": precision_bits,
                "rounding": "Arb outward real-ball arithmetic",
            },
            "model": {
                "dimension": DIMENSION,
                "modulation": "V(x)=1+(4/5)x",
                "source_basis": list(SOURCE_BASIS),
                "source_metric": [list(row) for row in SOURCE_METRIC],
                "basis_norm": "exact L2(0,1) orthonormality",
                "atlas_metric_note": (
                    "late/lattice/atomic coordinates are raw cosine "
                    "coefficients with S=I; early coordinates are calibrated "
                    "moment coefficients z with S=I and physical raw "
                    "coefficients D(q)^-1 z, equivalently the raw pair "
                    "(Gamma_R(q),D(q)^2) for q>0"
                ),
                "analytic_null_on_source_space": "zero",
                "moment_pivot_orders": list(PIVOT_ORDERS),
                "target": "standard Gaussian in resolved chart",
                "lattice_preparation": "one-cell Q=delta_0",
            },
            "generalized_floor": {
                "lower": _fraction_text(GLOBAL_LOWER_BOUND),
                "upper": _fraction_text(GLOBAL_UPPER_BOUND),
                "meaning": (
                    "lower <= inf over all four declared chart strata of "
                    "lambda_min(G,S) <= upper"
                ),
            },
            "early_resolved": early,
            "common_laplace_gram": laplace,
            "late_charts": late,
            "boundary_mass_cover": mass_certificate,
            "atomic_boundary": boundary,
            "upper_witness": upper,
            "ramp_degeneracy_control": ramp_scaling_audit(),
            "proof_method": {
                "matrix_lower_rule": (
                    "for a 2x2 Gram, lambda_min >= det/trace; "
                    "Andreief gives det >= d^2 mu_1 mu_2"
                ),
                "no_sampled_eigenvalue_inference": True,
                "all_sign_decisions_use_arb_or_exact_rationals": True,
            },
        }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--precision-bits",
        type=int,
        default=DEFAULT_PRECISION_BITS,
    )
    parser.add_argument(
        "--kappa-boxes-per-unit",
        type=int,
        default=DEFAULT_KAPPA_BOXES_PER_UNIT,
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    report = run_certificate(
        precision_bits=arguments.precision_bits,
        kappa_boxes_per_unit=arguments.kappa_boxes_per_unit,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
