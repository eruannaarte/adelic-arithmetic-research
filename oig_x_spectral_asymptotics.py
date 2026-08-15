#!/usr/bin/env python3
"""High-precision evidence for the OIG X factorial-spectrum conjecture.

This module regenerates representative entries and scaling controls for the
numerical tables in ``OIG_X_SPECTRAL_ASYMPTOTICS.md``.  It is deliberately
not an interval certificate: mpmath quadrature and eigendecomposition provide
conjecture evidence, while the factorial upper and explicit lower bounds are
analytic theorems proved in the memo.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys

import mpmath as mp


# Keep the default as text so mp.mpf constructs it inside the active workdps
# context instead of freezing an import-time binary-precision approximation.
DEFAULT_STRENGTH = "0.8"


def cosine_moment(order: int, mode: int) -> mp.mpf:
    """Return integral_0^1 x^order cos(mode*pi*x) dx by exact recurrence."""
    if order < 0:
        raise ValueError("order must be nonnegative")
    if mode < 1:
        raise ValueError("mode must be positive")
    if order == 0:
        return mp.mpf(0)
    denominator = (mode * mp.pi) ** 2
    previous_even = mp.mpf(0)
    previous_odd = ((-1) ** mode - 1) / denominator
    if order == 1:
        return previous_odd
    values = [previous_even, previous_odd]
    for degree in range(2, order + 1):
        value = (
            degree * ((-1) ** mode) / denominator
            - degree * (degree - 1) * values[degree - 2] / denominator
        )
        values.append(value)
    return values[order]


def moment_matrix(band: int) -> mp.matrix:
    """Rows are powers 1..band and columns are normalized cosine ports."""
    if band < 1:
        raise ValueError("band must be positive")
    return mp.matrix(
        [
            [mp.sqrt(2) * cosine_moment(order, mode)
             for mode in range(1, band + 1)]
            for order in range(1, band + 1)
        ]
    )


def final_moment_pivot(band: int) -> mp.mpf:
    """Last row-QR pivot of the square moment matrix."""
    matrix = moment_matrix(band)
    numerator = abs(mp.det(matrix))
    if band == 1:
        return numerator
    prefix = mp.matrix(band - 1, band)
    for row in range(band - 1):
        for column in range(band):
            prefix[row, column] = matrix[row, column]
    denominator_squared = mp.det(prefix * prefix.T)
    if denominator_squared <= 0:
        raise ArithmeticError("moment-prefix Gram lost positivity")
    return numerator / mp.sqrt(denominator_squared)


def source_pivot_ratio(band: int) -> mp.mpf:
    if band < 2:
        raise ValueError("band must be at least two")
    return final_moment_pivot(band) / final_moment_pivot(band - 1)


def ramp_phase(mode: int, scale: mp.mpf, strength: mp.mpf) -> mp.mpf:
    """Exact F_k(scale)=integral exp[-scale*(1+g*x)] phi_k(x) dx."""
    a = strength * scale
    return (
        mp.sqrt(2)
        * mp.exp(-scale)
        * a
        * (1 - ((-1) ** mode) * mp.exp(-a))
        / (a * a + (mode * mp.pi) ** 2)
    )


def _legendre_rule(order: int) -> tuple[list[mp.mpf], list[mp.mpf]]:
    if order < 8:
        raise ValueError("quadrature order must be at least eight")
    nodes, weights = mp.gauss_quadrature(order, "legendre")
    return [nodes[i] for i in range(order)], [weights[i] for i in range(order)]


def truncated_laplace_gram(
    band: int,
    cutoff: mp.mpf | float,
    strength: mp.mpf | float | str = DEFAULT_STRENGTH,
    quadrature_order: int = 96,
) -> mp.matrix:
    """Assemble H_b after s=b*r^2 removes the square-root endpoint."""
    b = mp.mpf(cutoff)
    g = mp.mpf(strength)
    if b <= 0 or g <= 0:
        raise ValueError("cutoff and strength must be positive")
    nodes, weights = _legendre_rule(quadrature_order)
    gram = mp.matrix(band, band)
    for node, weight in zip(nodes, weights):
        r = (node + 1) / 2
        s = b * r * r
        mass = weight * mp.sqrt(b) / (2 * mp.pi)
        response = [ramp_phase(k, s, g) for k in range(1, band + 1)]
        for left in range(band):
            for right in range(left, band):
                contribution = mass * response[left] * response[right]
                gram[left, right] += contribution
                if left != right:
                    gram[right, left] += contribution
    return gram


def lattice_gram(
    band: int,
    lattice_time: mp.mpf | float,
    strength: mp.mpf | float | str = DEFAULT_STRENGTH,
    quadrature_order: int = 96,
) -> mp.matrix:
    """Assemble the one-cell lattice Gram in dtheta/pi output measure."""
    tau = mp.mpf(lattice_time)
    g = mp.mpf(strength)
    if tau <= 0 or g <= 0:
        raise ValueError("lattice time and strength must be positive")
    nodes, weights = _legendre_rule(quadrature_order)
    gram = mp.matrix(band, band)
    for node, weight in zip(nodes, weights):
        theta = mp.pi * (node + 1) / 2
        scale = tau * 4 * mp.sin(theta / 2) ** 2
        mass = weight / 2
        response = [ramp_phase(k, scale, g) for k in range(1, band + 1)]
        for left in range(band):
            for right in range(left, band):
                contribution = mass * response[left] * response[right]
                gram[left, right] += contribution
                if left != right:
                    gram[right, left] += contribution
    return gram


def _smallest_singular(gram: mp.matrix, band: int) -> mp.mpf:
    block = gram[:band, :band]
    eigenvalues, _ = mp.eigsy(block)
    value = eigenvalues[0]
    scale = max(abs(eigenvalues[-1]), mp.mpf(1))
    if value < 0 and abs(value) <= 1000 * mp.eps * scale:
        value = mp.mpf(0)
    if value <= 0:
        raise ArithmeticError("high-precision Gram lost positive definiteness")
    return mp.sqrt(value)


def nested_ratio(gram: mp.matrix, band: int) -> mp.mpf:
    """Return band*sigma_band(E_band)/sigma_{band-1}(E_{band-1})."""
    if band < 2 or gram.rows < band or gram.cols < band:
        raise ValueError("Gram must contain a band of dimension at least two")
    return (
        band
        * _smallest_singular(gram, band)
        / _smallest_singular(gram, band - 1)
    )


def _text(value: mp.mpf, digits: int = 18) -> str:
    return mp.nstr(value, digits, min_fixed=0, max_fixed=0)


def run_audit(
    maximum_band: int = 12,
    digits: int = 100,
    quadrature_order: int = 96,
) -> dict[str, object]:
    """Return a JSON-ready, explicitly non-certified conjecture audit."""
    if maximum_band < 4:
        raise ValueError("maximum_band must be at least four")
    if digits < 50:
        raise ValueError("digits must be at least fifty")
    with mp.workdps(digits):
        default_strength = mp.mpf(DEFAULT_STRENGTH)
        pivot_bands = sorted(set([4, min(10, maximum_band), maximum_band]))
        pivot_rows = [
            {
                "band": band,
                "ratio": _text(source_pivot_ratio(band)),
            }
            for band in pivot_bands
            if band >= 2
        ]
        phase_rows = []
        for cutoff in (mp.mpf(1), mp.mpf(4)):
            gram = truncated_laplace_gram(
                maximum_band,
                cutoff,
                quadrature_order=quadrature_order,
            )
            phase_rows.append(
                {
                    "cutoff_b": _text(cutoff),
                    "band": maximum_band,
                    "K_sigmaK_over_sigmaKminus1": _text(
                        nested_ratio(gram, maximum_band)
                    ),
                    "conjectured_limit": _text(
                        default_strength * cutoff / (6 * mp.pi)
                    ),
                }
            )
        lattice_rows = []
        for strength, tau in (
            (mp.mpf("0.4"), mp.mpf(1)),
            (mp.mpf("0.8"), mp.mpf(1)),
            (mp.mpf("0.8"), mp.mpf(2)),
        ):
            gram = lattice_gram(
                maximum_band,
                tau,
                strength,
                quadrature_order,
            )
            lattice_rows.append(
                {
                    "strength_g": _text(strength),
                    "lattice_time_tau": _text(tau),
                    "band": maximum_band,
                    "K_sigmaK_over_sigmaKminus1": _text(
                        nested_ratio(gram, maximum_band)
                    ),
                    "conjectured_limit": _text(
                        2 * strength * tau / (3 * mp.pi)
                    ),
                }
            )
        return {
            "title": "OIG X spectral-asymptotic conjecture audit",
            "status": (
                "high-precision numerical evidence only; not an interval "
                "certificate and not a proof of the ratio limits"
            ),
            "environment": {
                "python": platform.python_version(),
                "mpmath": mp.__version__,
                "working_digits": digits,
                "quadrature_order": quadrature_order,
            },
            "source_pivot_limit_candidate": _text(2 / (3 * mp.pi)),
            "source_pivot_ratios": pivot_rows,
            "truncated_laplace_ratios": phase_rows,
            "lattice_scaling_controls": lattice_rows,
            "theorem_boundary": {
                "factorial_upper": "proved analytically in the memo",
                "explicit_lower": "proved analytically in the memo",
                "ratio_constants": "numerical conjecture",
            },
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--maximum-band", type=int, default=12)
    parser.add_argument("--digits", type=int, default=100)
    parser.add_argument("--quadrature-order", type=int, default=96)
    args = parser.parse_args()
    json.dump(
        run_audit(args.maximum_band, args.digits, args.quadrature_order),
        fp=sys.stdout,
        indent=2,
        sort_keys=True,
    )
    print()


if __name__ == "__main__":
    main()
