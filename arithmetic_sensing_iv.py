#!/usr/bin/env python3
"""Reproduce the principal Arithmetic Sensing IV certificates and studies.

The default report evaluates the published continuum-certified design.  The
``--degree-study`` and ``--ratio-study`` flags run the more expensive fixed-
degree and re-optimization experiments described in ``ARITHMETIC_SENSING_IV``.
"""

from __future__ import annotations

import argparse
import json
import math

import numpy as np

from arithmetic_indistinguishability import perlis_two_adic_local_probe
from deterministic_arithmetic_sensing import (
    deterministic_coefficient_bounds,
    quadratic_divisor_coefficients_sieve,
    quadratic_tail_l1_from_sieve,
)
from fixed_degree_arithmetic_sensing import (
    fixed_degree_divisor_coefficients_sieve,
    fixed_degree_tail_envelope,
)
from optimized_arithmetic_quadrature import (
    CosineQuadratureDesign,
    continuous_density_extrema,
    cosine_quadratic_tail_envelope,
    cosine_window_gram,
    cosine_window_weights,
    fejer_riesz_certificate,
    finite_divisor_tail_proxy,
    optimize_cosine_quadrature,
    prealias_limit,
    trigonometric_alias_band_remainder_bound,
)


REFERENCE_COEFFICIENTS = np.asarray(
    [
        -0.626411857413006,
        0.11592816172103249,
        0.0016529529219241504,
        0.009509006875539596,
        -0.0006326688393882172,
        -0.00013205040380077627,
        0.00039451702458319105,
        -0.00030217949865822015,
    ]
)


def reference_design(sample_count: int = 5_000) -> CosineQuadratureDesign:
    return CosineQuadratureDesign(
        sample_count, 1_000.0, REFERENCE_COEFFICIENTS.copy()
    )


def reference_report(certificate_truncation: int = 1_000_000) -> dict[str, object]:
    """Recompute the continuum, alias-band, and complete quadratic audit."""
    design = reference_design()
    coefficient_margin = 5e-9
    lower_factor = fejer_riesz_certificate(
        design.coefficients, constant=1.0 - coefficient_margin
    )
    upper_factor = fejer_riesz_certificate(
        -design.coefficients, constant=1.5 - coefficient_margin
    )
    error_multiplier = 2 * design.harmonic_count + 1
    coefficients = quadratic_divisor_coefficients_sieve(
        certificate_truncation
    )
    base_remainder = quadratic_tail_l1_from_sieve(
        certificate_truncation, 2.0, coefficients
    )
    alias_remainders = {
        str(target): trigonometric_alias_band_remainder_bound(
            target,
            certificate_truncation,
            2.0,
            design,
            base_remainder,
        )
        for target in [1, 10, 50]
    }
    envelope, _ = cosine_quadratic_tail_envelope(
        50, 2.0, certificate_truncation, design, coefficients
    )
    gram = cosine_window_gram(50, design)
    bounds = deterministic_coefficient_bounds(gram, 2.0, envelope)
    weights = cosine_window_weights(design)
    return {
        "parameters": {
            "maximum_norm": 50,
            "sigma": 2.0,
            "observation_time": 1_000.0,
            "sample_count": 5_000,
            "harmonics": 8,
            "certificate_truncation": certificate_truncation,
        },
        "coefficients": design.coefficients.tolist(),
        "continuous_extrema": continuous_density_extrema(
            design.coefficients
        ),
        "lower_factor_residual": lower_factor.residual,
        "upper_factor_residual": upper_factor.residual,
        "certified_density_floor": (
            coefficient_margin - error_multiplier * lower_factor.residual
        ),
        "certified_cap_gap": (
            coefficient_margin - error_multiplier * upper_factor.residual
        ),
        "effective_sample_count": float(1.0 / np.sum(weights**2)),
        "lambda_min": float(np.linalg.eigvalsh(gram)[0]),
        "prealias_limit": prealias_limit(design),
        "global_l1_remainder": base_remainder,
        "alias_band_remainders": alias_remainders,
        "worst_complete_coefficient_bound": float(np.max(bounds)),
        "worst_coefficient": int(np.argmax(bounds) + 1),
        "held_out_301_to_1000": float(
            np.max(finite_divisor_tail_proxy(50, 2.0, 301, 1_000, design))
        ),
        "held_out_1001_to_5000": float(
            np.max(finite_divisor_tail_proxy(50, 2.0, 1_001, 5_000, design))
        ),
        "local_probe": perlis_two_adic_local_probe(33),
    }


def degree_study(certificate_truncation: int = 1_000_000) -> list[dict[str, object]]:
    """Run the universal degree-2 through degree-5 envelope study."""
    design = reference_design()
    gram = cosine_window_gram(50, design)
    results = []
    for degree in range(2, 6):
        coefficients = fixed_degree_divisor_coefficients_sieve(
            certificate_truncation, degree
        )
        envelope, base_remainder = fixed_degree_tail_envelope(
            50,
            degree,
            2.0,
            certificate_truncation,
            design,
            coefficients,
        )
        bounds = deterministic_coefficient_bounds(gram, 2.0, envelope)
        results.append(
            {
                "degree": degree,
                "global_l1_remainder": base_remainder,
                "worst_complete_coefficient_bound": float(np.max(bounds)),
                "worst_coefficient": int(np.argmax(bounds) + 1),
                "integer_rounding_certificate": bool(np.max(bounds) < 0.5),
            }
        )
    return results


def ratio_study(
    ratios: tuple[float, ...] = (4.42, 4.5, 5.0, 6.0),
    design_tail_cutoff: int = 150,
    certificate_truncation: int = 1_000_000,
) -> list[dict[str, object]]:
    """Jointly re-optimize weights on a certified discrete ``m/T`` grid."""
    envelope_coefficients = quadratic_divisor_coefficients_sieve(
        certificate_truncation
    )
    required = math.log(certificate_truncation + 1.0)
    results = []
    for ratio in ratios:
        sample_count = round(1_000.0 * ratio)
        design, optimization = optimize_cosine_quadrature(
            50,
            2.0,
            1_000.0,
            sample_count,
            8,
            design_tail_cutoff,
            0.98,
            2.5,
        )
        envelope, _ = cosine_quadratic_tail_envelope(
            50,
            2.0,
            certificate_truncation,
            design,
            envelope_coefficients,
        )
        bounds = deterministic_coefficient_bounds(
            cosine_window_gram(50, design), 2.0, envelope
        )
        results.append(
            {
                "ratio": ratio,
                "sample_count": sample_count,
                "prealias_limit": prealias_limit(design),
                "million_term_prealias_certificate": bool(
                    prealias_limit(design) > required
                ),
                "coefficients": design.coefficients.tolist(),
                "finite_objective": optimization[
                    "objective_finite_tail_proxy"
                ],
                "effective_sample_count": optimization[
                    "effective_sample_count"
                ],
                "lambda_min": optimization["lambda_min"],
                "worst_complete_coefficient_bound": float(np.max(bounds)),
            }
        )
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate-truncation", type=int, default=1_000_000)
    parser.add_argument("--degree-study", action="store_true")
    parser.add_argument("--ratio-study", action="store_true")
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    report: dict[str, object] = {
        "reference": reference_report(arguments.certificate_truncation)
    }
    if arguments.degree_study:
        report["degree_study"] = degree_study(
            arguments.certificate_truncation
        )
    if arguments.ratio_study:
        report["ratio_study"] = ratio_study(
            certificate_truncation=arguments.certificate_truncation
        )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
