#!/usr/bin/env python3
"""Stage XI finite-grid transfer certificates for the canonical late core.

The script separates two finite objects which must not be conflated.

``phase_grid``
    The cell-centred spectral quadrature of the *limiting* one-cell lattice
    phase Gram at ``tau=1``.  Every entry and its continuum integral are
    evaluated with Arb balls.  A maximum absolute row sum of the whitened
    error is therefore a rigorous upper bound for

        delta_K(n) = ||S^(-1/2) (G_n-G) S^(-1/2)||_2.

``full_neumann``
    The actual finite cell-centred Neumann model from OIG VIII, including the
    noncommuting path Laplacian and ramp multiplication.  Small grids are
    enclosed by Arb matrix exponentials.  Larger-grid results are explicitly
    descriptive binary64 diagnostics and never decide a certificate.

The certified phase-grid result controls spectral quadrature only.  It is
not a certificate for the full finite dynamics: the gap between these two
objects is precisely the mixed-word / boundary transfer problem left open by
Stage X.  The full-Neumann K=1 certificate below is a first honest instance
where that complete error is smaller than the inherited continuum floor.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import sys
from fractions import Fraction
from typing import Sequence

import numpy as np
from flint import acb, arb, arb_mat, ctx, fmpq

from oig_viii_three_parameter import (
    gaussian_cell_masses,
    scaled_modal_kernel,
    target_coefficients,
)


INTERACTION_STRENGTH = Fraction(4, 5)
LATTICE_TIME = Fraction(1, 1)
MAX_BAND = 8
DEFAULT_PRECISION_BITS = 256

# Exact rational lower bounds copied from the successful Stage X Arb proof
# trace (oig_x_spectral_certificate.py, 256-bit run).  These are theorem
# inputs here: Stage XI only proves that its transfer error is smaller.
STAGE_X_LOWER_BOUNDS: dict[str, tuple[Fraction, ...]] = {
    "L2": tuple(
        Fraction(value)
        for value in (
            "26212947057893025895758970976771535872247657438700072948593/200000000000000000000000000000000000000000000000000000000000000",
            "71575982560691627369082268261831253224317187234411991716471/500000000000000000000000000000000000000000000000000000000000000000",
            "177649699161470441119453670843679003900039241460556517030389/1000000000000000000000000000000000000000000000000000000000000000000000",
            "223907791606773565127337942966556920627433538397147554621613/1000000000000000000000000000000000000000000000000000000000000000000000000",
            "6812079927221629853983170460030926063095319038923421184133/25000000000000000000000000000000000000000000000000000000000000000000000000",
            "241217949477091250882782131024250855121635793231020161491267/1000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "15349603798038749699017529393873212473489243837483219482291/100000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "184249355555519379553475395521602398844374596763922458049413/2500000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        )
    ),
    "H1": tuple(
        Fraction(value)
        for value in (
            "30144780447651282258576472851735601706114729259783270912987/2500000000000000000000000000000000000000000000000000000000000000",
            "177615501105199674392110272222231543772504830490130249386911/50000000000000000000000000000000000000000000000000000000000000000000",
            "201796315787705055454503952724587616145875149677766145940609/100000000000000000000000000000000000000000000000000000000000000000000000",
            "29788649134796875846631286472667141380868235372402004018089/20000000000000000000000000000000000000000000000000000000000000000000000000",
            "1210695313951546325679691183099153681644891479744876934627/1000000000000000000000000000000000000000000000000000000000000000000000000000",
            "77392084465341221495095813286248163852047599058352364291983/100000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "93575379230275480161704217674943646597617743528457861543161/250000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "141494564508648844478970663298312435724336692832327010618701/1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        )
    ),
}


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


def _interval_text(value: arb, digits: int = 24) -> str:
    return value.str(digits, radius=True, more=True)


def phase_profile(mode: int, s: arb) -> arb:
    """Exact affine-ramp phase profile for sqrt(2) cos(k pi x)."""
    if mode < 1:
        raise ValueError("mode must be positive")
    g = _q(INTERACTION_STRENGTH)
    a = g * s
    endpoint = -(-a).expm1() if mode % 2 == 0 else 1 + (-a).exp()
    return (
        arb(2).sqrt()
        * (-s).exp()
        * a
        * endpoint
        / (a**2 + (mode * arb.pi()) ** 2)
    )


def _integral(integrand, precision_bits: int) -> arb:
    value = acb.integral(
        integrand,
        arb(0),
        arb(1),
        rel_tol=arb(2) ** (-(precision_bits - 32)),
        abs_tol=arb(2) ** (-precision_bits),
        eval_limit=30_000,
        depth_limit=30,
    )
    if not bool(value.imag.contains(0)):
        raise ArithmeticError("a real integral acquired nonzero imaginary part")
    return value.real


def continuum_lattice_gram(
    dimension: int, precision_bits: int = DEFAULT_PRECISION_BITS
) -> arb_mat:
    """Normalized one-cell lattice Gram at tau=1."""
    if not 1 <= dimension <= MAX_BAND:
        raise ValueError("dimension must lie in [1,8]")
    result = arb_mat(dimension, dimension)
    coefficient = arb(2).sqrt()
    for row in range(dimension):
        for column in range(row + 1):
            value = coefficient * _integral(
                lambda xi, _: phase_profile(
                    row + 1, 4 * (arb.pi() * xi / 2).sin() ** 2
                )
                * phase_profile(
                    column + 1, 4 * (arb.pi() * xi / 2).sin() ** 2
                ),
                precision_bits,
            )
            result[row, column] = value
            result[column, row] = value
    return result


def phase_midpoint_gram(side_length: int, dimension: int) -> arb_mat:
    """Cell-centred spectral quadrature of the tau=1 lattice phase Gram."""
    if side_length <= dimension:
        raise ValueError("side_length must exceed the source dimension")
    result = arb_mat(dimension, dimension)
    profiles: list[list[arb]] = []
    for cell in range(side_length):
        xi = _q(Fraction(2 * cell + 1, 2 * side_length))
        s = 4 * (arb.pi() * xi / 2).sin() ** 2
        profiles.append([phase_profile(mode, s) for mode in range(1, dimension + 1)])
    coefficient = arb(2).sqrt() / side_length
    for row in range(dimension):
        for column in range(row + 1):
            value = coefficient * sum(
                (samples[row] * samples[column] for samples in profiles), arb(0)
            )
            result[row, column] = value
            result[column, row] = value
    return result


def metric_relative_row_sum_bound(
    finite: arb_mat, continuum: arb_mat, metric: str
) -> arb:
    """Certify spectral norm by the maximum whitened absolute row sum."""
    if metric not in STAGE_X_LOWER_BOUNDS:
        raise ValueError("metric must be L2 or H1")
    if finite.nrows() != finite.ncols() or continuum.nrows() != finite.nrows():
        raise ValueError("Gram dimensions do not agree")
    dimension = finite.nrows()
    diagonal = [
        arb(1)
        if metric == "L2"
        else 1 + ((mode + 1) * arb.pi()) ** 2
        for mode in range(dimension)
    ]
    row_bounds: list[arb] = []
    for row in range(dimension):
        total = arb(0)
        for column in range(dimension):
            error = (finite[row, column] - continuum[row, column]) / (
                diagonal[row] * diagonal[column]
            ).sqrt()
            total += error.abs_upper()
        row_bounds.append(total)
    maximum = row_bounds[0]
    for value in row_bounds[1:]:
        if bool(value > maximum):
            maximum = value
    return maximum


def phase_grid_certificate(
    max_band: int = MAX_BAND,
    precision_bits: int = DEFAULT_PRECISION_BITS,
    maximum_side_length: int = 48,
) -> dict[str, object]:
    """Find the first certified midpoint phase grid for each K and metric."""
    continuum = continuum_lattice_gram(max_band, precision_bits)
    rows: list[dict[str, object]] = []
    for dimension in range(1, max_band + 1):
        finite_cache: dict[int, arb_mat] = {}
        continuum_block = arb_mat(
            [
                [continuum[row, column] for column in range(dimension)]
                for row in range(dimension)
            ]
        )
        for metric in ("L2", "H1"):
            floor = STAGE_X_LOWER_BOUNDS[metric][dimension - 1]
            first: dict[str, object] | None = None
            predecessor: dict[str, object] | None = None
            for side_length in range(dimension + 1, maximum_side_length + 1):
                finite = finite_cache.setdefault(
                    side_length, phase_midpoint_gram(side_length, dimension)
                )
                bound = metric_relative_row_sum_bound(
                    finite, continuum_block, metric
                )
                bound_upper = _exact_dyadic_fraction(bound.upper())
                record = {
                    "side_length": side_length,
                    "delta_upper_exact": _fraction_text(bound_upper),
                    "delta_upper_approx": float(bound_upper),
                    "strictly_below_stage_x_floor": bool(bound < _q(floor)),
                }
                if record["strictly_below_stage_x_floor"]:
                    transferred = floor - bound_upper
                    record["transferred_finite_floor_exact"] = _fraction_text(
                        transferred
                    )
                    record["transferred_finite_floor_approx"] = float(transferred)
                    first = record
                    break
                predecessor = record
            rows.append(
                {
                    "band_dimension": dimension,
                    "metric": metric,
                    "stage_x_lower_bound_exact": _fraction_text(floor),
                    "stage_x_lower_bound_approx": float(floor),
                    "first_certified_side_length_in_sequential_search": first,
                    "immediate_predecessor": predecessor,
                    "search_exhausted": first is None,
                    "passed": first is not None,
                }
            )
    return {
        "object": "cell-centred midpoint quadrature of the limiting lattice phase Gram",
        "chart": "one-cell lattice, tau=1, sqrt(1+tau) normalization",
        "proof": (
            "Arb encloses every finite sum and continuum integral; the maximum "
            "absolute row sum of the source-metric-whitened error bounds its "
            "spectral norm"
        ),
        "does_not_include": [
            "mixed causal words from the finite path generator",
            "finite reflecting-boundary effects",
            "finite target preparation error",
            "finite sensor-frame error",
        ],
        "rows": rows,
        "passed": all(row["passed"] for row in rows),
    }


def _finite_neumann_gram_arb(
    side_length: int,
    dimension: int,
) -> arb_mat:
    """Actual finite Neumann atom Gram, rigorously enclosed by Arb exp."""
    if side_length < 3 or not 1 <= dimension < side_length:
        raise ValueError("invalid side length or source dimension")
    n = side_length
    centre_cell = (n - 1) // 2
    source = arb_mat(n, dimension)
    for cell in range(n):
        x = _q(Fraction(2 * cell + 1, 2 * n))
        for mode in range(1, dimension + 1):
            source[cell, mode - 1] = (arb(2) / n).sqrt() * (
                arb.pi() * mode * x
            ).cos()

    gram = arb_mat(dimension, dimension)
    for target_mode in range(1, n):
        omega = 4 * (arb.pi() * target_mode / (2 * n)).sin() ** 2
        generator = arb_mat(n, n)
        for cell in range(n):
            generator[cell, cell] = (
                1 if cell in (0, n - 1) else 2
            ) + omega * (
                1 + _q(INTERACTION_STRENGTH) * _q(Fraction(2 * cell + 1, 2 * n))
            )
            if cell + 1 < n:
                generator[cell, cell + 1] = -1
                generator[cell + 1, cell] = -1
        propagated = (-generator).exp() * source
        amplitudes = [
            sum((propagated[cell, mode] for cell in range(n)), arb(0))
            for mode in range(dimension)
        ]
        target_x = _q(Fraction(2 * centre_cell + 1, 2 * n))
        beta = (arb(2) / n).sqrt() * (
            arb.pi() * target_mode * target_x
        ).cos()
        for row in range(dimension):
            for column in range(row + 1):
                gram[row, column] += beta**2 * amplitudes[row] * amplitudes[column]
                if row != column:
                    gram[column, row] = gram[row, column]
    return gram * (arb(2).sqrt() / n)


def full_neumann_small_grid_certificate(
    precision_bits: int = DEFAULT_PRECISION_BITS,
) -> dict[str, object]:
    """Certify the first complete K=1 finite-model crossing in both metrics."""
    continuum = continuum_lattice_gram(1, precision_bits)
    finite_by_n = {
        side_length: _finite_neumann_gram_arb(side_length, 1)
        for side_length in range(3, 8)
    }
    metric_certificates = []
    for metric in ("L2", "H1"):
        floor = STAGE_X_LOWER_BOUNDS[metric][0]
        records = []
        first = None
        for side_length, finite in finite_by_n.items():
            bound = metric_relative_row_sum_bound(finite, continuum, metric)
            bound_upper = _exact_dyadic_fraction(bound.upper())
            row = {
                "side_length": side_length,
                "delta_upper_exact": _fraction_text(bound_upper),
                "delta_upper_approx": float(bound_upper),
                "strictly_below_stage_x_floor": bool(bound < _q(floor)),
            }
            if row["strictly_below_stage_x_floor"]:
                transferred = floor - bound_upper
                row["transferred_finite_floor_exact"] = _fraction_text(transferred)
                row["transferred_finite_floor_approx"] = float(transferred)
            records.append(row)
            if row["strictly_below_stage_x_floor"] and first is None:
                first = side_length
        metric_certificates.append(
            {
                "metric": metric,
                "stage_x_lower_bound_exact": _fraction_text(floor),
                "records": records,
                "first_certified_side_length_in_tested_sequence": first,
                "passed": first == 7,
            }
        )

    # Preserve the L2 fields at top level because they are the simplest
    # complete finite-model comparison and convenient for downstream readers.
    l2 = metric_certificates[0]
    return {
        "object": "actual cell-centred finite Neumann dynamics with a central atomic target",
        "band_dimension": 1,
        "metric": "L2",
        "chart_point": "one-cell lattice comparison point tau=1",
        "stage_x_lower_bound_exact": l2["stage_x_lower_bound_exact"],
        "records": l2["records"],
        "first_certified_side_length_in_tested_sequence": l2[
            "first_certified_side_length_in_tested_sequence"
        ],
        "metric_certificates": metric_certificates,
        "proof": "Arb matrix exponentials, Arb continuum integral, and a rigorous metric-relative row-sum norm bound",
        "passed": all(row["passed"] for row in metric_certificates),
    }


def full_neumann_descriptive(
    side_lengths: Sequence[int] = (31, 63, 127, 255, 383, 511),
) -> dict[str, object]:
    """Binary64 K=2 convergence diagnostics, never used as proof."""
    continuum_ball = continuum_lattice_gram(2, DEFAULT_PRECISION_BITS)
    continuum = np.asarray(
        [
            [float(continuum_ball[row, column].mid()) for column in range(2)]
            for row in range(2)
        ]
    )
    floor = float(STAGE_X_LOWER_BOUNDS["L2"][1])
    records = []
    for n in side_lengths:
        kernel = scaled_modal_kernel(n, (1.0,), (1, 2))
        atom = gaussian_cell_masses(n, 0.0, 0.0)
        beta = target_coefficients(atom)
        output = kernel.values[0] * beta[:, None] / math.sqrt(n)
        finite = math.sqrt(2.0) * (output.T @ output)
        delta = float(np.linalg.norm(finite - continuum, ord=2))
        records.append(
            {
                "side_length": n,
                "binary64_delta": delta,
                "binary64_delta_over_stage_x_floor": delta / floor,
                "appears_below_floor": delta < floor,
            }
        )
    return {
        "object": "actual finite Neumann dynamics, K=2",
        "role": "descriptive evidence only; never used to decide a certificate",
        "records": records,
    }


def negative_controls() -> dict[str, object]:
    """Executable controls against false transfer claims."""
    continuum = continuum_lattice_gram(2, DEFAULT_PRECISION_BITS)
    coarse = phase_midpoint_gram(3, 2)
    delta = metric_relative_row_sum_bound(coarse, continuum, "L2")
    floor = STAGE_X_LOWER_BOUNDS["L2"][1]
    absolute_entry_max = max(
        (
            (coarse[row, column] - continuum[row, column]).abs_upper()
            for row in range(2)
            for column in range(2)
        ),
        key=float,
    )
    return {
        "coarse_grid_rejected": not bool(delta < _q(floor)),
        "coarse_grid_delta_interval": _interval_text(delta),
        "coarse_grid_floor_exact": _fraction_text(floor),
        "entrywise_max_is_not_the_operator_bound": bool(
            delta > absolute_entry_max
        ),
        "full_model_not_inferred_from_phase_grid": True,
        "binary64_not_used_for_certificate": True,
        "passed": bool(
            not bool(delta < _q(floor)) and delta > absolute_entry_max
        ),
    }


def run_certificate(
    max_band: int = MAX_BAND,
    precision_bits: int = DEFAULT_PRECISION_BITS,
    maximum_phase_side_length: int = 48,
    include_descriptive: bool = True,
) -> dict[str, object]:
    if not 1 <= max_band <= MAX_BAND:
        raise ValueError("max_band must lie in [1,8]")
    if precision_bits < 160:
        raise ValueError("precision_bits must be at least 160")
    previous = ctx.prec
    ctx.prec = precision_bits
    try:
        phase = phase_grid_certificate(
            max_band, precision_bits, maximum_phase_side_length
        )
        full = full_neumann_small_grid_certificate(precision_bits)
        controls = negative_controls()
        result = {
            "schema_version": "oig-xi-transfer-certificate-v1",
            "status": "rigorous phase-grid transfer and one complete finite-model crossing",
            "environment": {
                "python": sys.version.split()[0],
                "platform": platform.platform(),
                "numpy": np.__version__,
                "python_flint": __import__("flint").__version__,
                "arb_precision_bits": precision_bits,
            },
            "model": {
                "interaction_strength_exact": _fraction_text(INTERACTION_STRENGTH),
                "lattice_time_exact": _fraction_text(LATTICE_TIME),
                "source_ports": list(range(1, max_band + 1)),
                "normalization": "sqrt(1+tau)",
            },
            "phase_grid_certificate": phase,
            "full_neumann_small_grid_certificate": full,
            "negative_controls": controls,
            "proof_boundary": (
                "The phase-grid K<=8 certificate is a quadrature-transfer theorem, "
                "not a full finite-dynamics theorem.  The full finite Neumann "
                "certificate currently closes only K=1 at tau=1.  Uniform tau>=1, "
                "early, boundary, preparation, and sensor errors remain open."
            ),
            "metric_transport_audit": {
                "source_coordinates": (
                    "the same L2-orthonormal cosine coefficients are used on both sides"
                ),
                "finite_source_metric": (
                    "exactly I for L2 by DCT orthogonality; H1 is evaluated with the "
                    "declared continuum source-cost matrix, not a raw Euclidean proxy"
                ),
                "output_metric": (
                    "the finite Gram includes the density-normalized Euclidean output "
                    "metric and the continuum Gram includes its declared integral limit"
                ),
                "claim": (
                    "the certificate compares the resulting source quadratic forms; "
                    "it does not silently identify unequal output coordinate spaces"
                ),
            },
        }
        if include_descriptive:
            result["full_neumann_k2_descriptive"] = full_neumann_descriptive()
        result["overall_passed"] = bool(
            phase["passed"] and full["passed"] and controls["passed"]
        )
        return result
    finally:
        ctx.prec = previous


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-band", type=int, default=MAX_BAND)
    parser.add_argument("--precision-bits", type=int, default=DEFAULT_PRECISION_BITS)
    parser.add_argument("--maximum-phase-side-length", type=int, default=48)
    parser.add_argument("--no-descriptive", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    result = run_certificate(
        args.max_band,
        args.precision_bits,
        args.maximum_phase_side_length,
        not args.no_descriptive,
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
