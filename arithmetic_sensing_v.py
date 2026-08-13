#!/usr/bin/env python3
"""Reproduce Arithmetic Sensing V exact and fixed-degree certificates."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction

import numpy as np

from arithmetic_indistinguishability import perlis_two_adic_moment_channel
from arithmetic_sensing_iv import REFERENCE_COEFFICIENTS
from deterministic_arithmetic_sensing import (
    deterministic_coefficient_bounds,
    deterministic_gaussian_rounding_failure_bound,
    quadratic_divisor_coefficients_sieve,
)
from exact_trigonometric_positivity import rational_continuum_certificate
from fixed_degree_arithmetic_sensing import (
    fixed_degree_divisor_coefficients_sieve,
    fixed_degree_tail_envelope,
)
from optimized_arithmetic_quadrature import (
    CosineQuadratureDesign,
    cosine_noise_covariance,
    cosine_quadratic_tail_envelope,
    cosine_window_gram,
    cosine_window_weights,
    optimize_cosine_quadrature,
)


REFERENCE_COEFFICIENT_STRINGS = [
    "-0.626411857413006",
    "0.11592816172103249",
    "0.0016529529219241504",
    "0.009509006875539596",
    "-0.0006326688393882172",
    "-0.00013205040380077627",
    "0.00039451702458319105",
    "-0.00030217949865822015",
]


def design_for_time(
    observation_time: float = 1_000.0, sampling_ratio: float = 5.0
) -> CosineQuadratureDesign:
    return CosineQuadratureDesign(
        round(observation_time * sampling_ratio),
        observation_time,
        REFERENCE_COEFFICIENTS.copy(),
    )


def exact_positivity_report() -> dict[str, object]:
    certificate = rational_continuum_certificate(
        REFERENCE_COEFFICIENT_STRINGS,
        "0.00001",
        "2.499999995",
    )
    representation_errors = [
        abs(Fraction.from_float(float(value)) - Fraction(text))
        for value, text in zip(
            REFERENCE_COEFFICIENTS, REFERENCE_COEFFICIENT_STRINGS
        )
    ]
    density_perturbation = 2 * sum(representation_errors, Fraction(0))
    return {
        "coefficient_interpretation": "displayed decimals treated exactly as rationals",
        "strict_lower_bound": str(certificate.lower_bound),
        "strict_upper_bound": str(certificate.upper_bound),
        "lower_boundary_root_count_on_minus1_plus1": certificate.lower_root_count,
        "upper_boundary_root_count_on_minus1_plus1": certificate.upper_root_count,
        "exact_float_density_perturbation_bound": str(density_perturbation),
        "float_density_perturbation_bound_decimal": float(density_perturbation),
        "float_strict_lower_bound": float(
            certificate.lower_bound - density_perturbation
        ),
        "float_strict_upper_bound": float(
            certificate.upper_bound + density_perturbation
        ),
        "exact_sturm_certificate": certificate.certified,
    }


def fixed_degree_report(
    degree: int,
    observation_time: float = 1_000.0,
    sampling_ratio: float = 5.0,
    certificate_truncation: int = 1_000_000,
    bin_width: float = 0.01,
) -> dict[str, object]:
    design = design_for_time(observation_time, sampling_ratio)
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
        remainder_method="mellin",
        mellin_bin_width=bin_width,
    )
    gram = cosine_window_gram(50, design)
    bounds = deterministic_coefficient_bounds(gram, 2.0, envelope)
    return {
        "degree": degree,
        "observation_time": observation_time,
        "sample_count": design.sample_count,
        "sampling_ratio": sampling_ratio,
        "certificate_truncation": certificate_truncation,
        "mellin_bin_width": bin_width,
        "global_l1_remainder_before_kernel_decay": base_remainder,
        "lambda_min": float(np.linalg.eigvalsh(gram)[0]),
        "worst_complete_coefficient_bound": float(np.max(bounds)),
        "worst_coefficient": int(np.argmax(bounds) + 1),
        "integer_rounding_certificate": bool(np.max(bounds) < 0.5),
    }


def degree_study(
    certificate_truncation: int = 1_000_000,
    bin_width: float = 0.01,
) -> list[dict[str, object]]:
    return [
        fixed_degree_report(
            degree,
            certificate_truncation=certificate_truncation,
            bin_width=bin_width,
        )
        for degree in range(2, 11)
    ]


def bin_resolution_study(
    certificate_truncation: int = 1_000_000,
) -> list[dict[str, object]]:
    return [
        fixed_degree_report(
            5,
            certificate_truncation=certificate_truncation,
            bin_width=bin_width,
        )
        for bin_width in [0.1, 0.05, 0.02, 0.01, 0.005, 0.0025]
    ]


def degree_aware_optimizer_study(
    certificate_truncation: int = 1_000_000,
    bin_width: float = 0.01,
) -> list[dict[str, object]]:
    degree = 9
    design_cutoff = 150
    design_envelope = fixed_degree_divisor_coefficients_sieve(
        design_cutoff, degree
    )
    certificate_coefficients = fixed_degree_divisor_coefficients_sieve(
        certificate_truncation, degree
    )
    results = []
    for harmonic_count in [8, 10, 12]:
        design, optimization = optimize_cosine_quadrature(
            maximum_norm=50,
            sigma=2.0,
            observation_time=1_000.0,
            sample_count=5_000,
            harmonic_count=harmonic_count,
            design_tail_cutoff=design_cutoff,
            gershgorin_lower_bound=0.98,
            density_cap=2.5,
            design_envelope_coefficients=design_envelope,
        )
        envelope, _ = fixed_degree_tail_envelope(
            50,
            degree,
            2.0,
            certificate_truncation,
            design,
            certificate_coefficients,
            remainder_method="mellin",
            mellin_bin_width=bin_width,
        )
        gram = cosine_window_gram(50, design)
        bounds = deterministic_coefficient_bounds(gram, 2.0, envelope)
        results.append(
            {
                "degree": degree,
                "harmonic_count": harmonic_count,
                "design_tail_cutoff": design_cutoff,
                "finite_objective": optimization[
                    "objective_finite_tail_proxy"
                ],
                "cosine_coefficients": design.coefficients.tolist(),
                "lambda_min": float(np.linalg.eigvalsh(gram)[0]),
                "worst_complete_coefficient_bound": float(np.max(bounds)),
                "integer_rounding_certificate": bool(np.max(bounds) < 0.5),
            }
        )
    return results


def degree_nine_time_study(
    certificate_truncation: int = 1_000_000,
    bin_width: float = 0.01,
) -> list[dict[str, object]]:
    return [
        fixed_degree_report(
            9,
            observation_time=observation_time,
            sampling_ratio=5.0,
            certificate_truncation=certificate_truncation,
            bin_width=bin_width,
        )
        for observation_time in [
            1_000.0,
            1_250.0,
            1_500.0,
            1_750.0,
            2_000.0,
            2_300.0,
            2_400.0,
            2_450.0,
            2_500.0,
            3_000.0,
        ]
    ]


def quadratic_noise_study(
    certificate_truncation: int = 1_000_000,
) -> list[dict[str, object]]:
    coefficients = quadratic_divisor_coefficients_sieve(
        certificate_truncation
    )
    results = []
    for sample_count in [50_000, 60_000, 67_000, 67_200, 70_000, 80_000, 100_000]:
        design = CosineQuadratureDesign(
            sample_count, 1_000.0, REFERENCE_COEFFICIENTS.copy()
        )
        envelope, _ = cosine_quadratic_tail_envelope(
            50,
            2.0,
            certificate_truncation,
            design,
            coefficients,
        )
        bounds = deterministic_coefficient_bounds(
            cosine_window_gram(50, design), 2.0, envelope
        )
        covariance = cosine_noise_covariance(50, 2.0, design)
        weights = cosine_window_weights(design)
        results.append(
            {
                "sample_count": sample_count,
                "sampling_ratio": sample_count / 1_000.0,
                "effective_sample_count": float(1.0 / np.sum(weights**2)),
                "worst_complete_tail_bound": float(np.max(bounds)),
                "gaussian_failure_bound_at_noise_0.01": (
                    deterministic_gaussian_rounding_failure_bound(
                        bounds, covariance, 0.01
                    )
                ),
            }
        )
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate-truncation", type=int, default=1_000_000)
    parser.add_argument("--bin-width", type=float, default=0.01)
    parser.add_argument("--degree", type=int, default=5)
    parser.add_argument("--degree-study", action="store_true")
    parser.add_argument("--bin-study", action="store_true")
    parser.add_argument("--degree-aware-study", action="store_true")
    parser.add_argument("--degree-nine-time-study", action="store_true")
    parser.add_argument("--noise-study", action="store_true")
    parser.add_argument("--all", action="store_true")
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    report: dict[str, object] = {
        "exact_continuum_positivity": exact_positivity_report(),
        "reference_fixed_degree": fixed_degree_report(
            arguments.degree,
            certificate_truncation=arguments.certificate_truncation,
            bin_width=arguments.bin_width,
        ),
        "quantitative_local_channel": perlis_two_adic_moment_channel(33),
    }
    if arguments.degree_study or arguments.all:
        report["degree_study"] = degree_study(
            arguments.certificate_truncation, arguments.bin_width
        )
    if arguments.bin_study or arguments.all:
        report["bin_resolution_study"] = bin_resolution_study(
            arguments.certificate_truncation
        )
    if arguments.degree_aware_study or arguments.all:
        report["degree_aware_optimizer_study"] = degree_aware_optimizer_study(
            arguments.certificate_truncation, arguments.bin_width
        )
    if arguments.degree_nine_time_study or arguments.all:
        report["degree_nine_time_study"] = degree_nine_time_study(
            arguments.certificate_truncation, arguments.bin_width
        )
    if arguments.noise_study or arguments.all:
        report["quadratic_noise_study"] = quadratic_noise_study(
            arguments.certificate_truncation
        )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
