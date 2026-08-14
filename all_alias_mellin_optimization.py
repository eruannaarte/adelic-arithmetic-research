#!/usr/bin/env python3
"""All-alias degree-nine window search for Arithmetic Sensing V.

This is deliberately separated into a search layer and a certification layer.
The search objective contains every explicitly enumerated term through the
million-term cutoff and every log-Mellin bin through the declared two-alias
range.  A candidate is accepted only after the ordinary independent tail,
Gram, and exact continuum-positivity checks are rerun.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from fractions import Fraction

import numpy as np
from scipy.optimize import minimize

from arithmetic_sensing_iv import REFERENCE_COEFFICIENTS
from deterministic_arithmetic_sensing import deterministic_coefficient_bounds
from exact_trigonometric_positivity import rational_continuum_certificate
from fixed_degree_arithmetic_sensing import (
    fixed_degree_divisor_coefficients_sieve,
    fixed_degree_tail_envelope,
    fixed_degree_tail_l1_elementary_bound,
    fixed_degree_tail_l1_from_sieve,
    zeta_log_convolution_certificate,
)
from optimized_arithmetic_quadrature import (
    CosineQuadratureDesign,
    centered_response_components,
    continuous_density_extrema,
    cosine_window_gram,
)


# The result of the joint target-49/50 all-alias run recorded in the paper.
# Decimal strings are retained so continuum positivity can be checked over Q.
ALL_ALIAS_DEGREE_NINE_COEFFICIENT_STRINGS = (
    "-0.6264146955471602",
    "0.11592301462359696",
    "0.0016545222416823374",
    "0.009510801153787815",
    "-0.0006316498798685098",
    "-0.0001316789270583388",
    "0.0003943240799222973",
    "-0.0002996383748447402",
)
ALL_ALIAS_DEGREE_NINE_COEFFICIENTS = np.asarray(
    [float(value) for value in ALL_ALIAS_DEGREE_NINE_COEFFICIENT_STRINGS]
)


@dataclass(frozen=True)
class TargetAllAliasData:
    """Affine finite responses and cancellation-aware Mellin envelopes."""

    target_norm: int
    finite_weights: np.ndarray
    finite_base: np.ndarray
    finite_basis: np.ndarray
    remote_masses: np.ndarray
    remote_center_base: np.ndarray
    remote_center_basis: np.ndarray
    remote_variation_base: np.ndarray
    remote_variation_basis: np.ndarray
    remote_alias_fallback: np.ndarray
    elementary_remote: float
    base_remainder: float

    def envelope(self, coefficients: np.ndarray) -> float:
        finite = float(
            np.dot(
                self.finite_weights,
                np.abs(self.finite_base + self.finite_basis @ coefficients),
            )
        )
        bracket = np.abs(
            self.remote_center_base
            + self.remote_center_basis @ coefficients
        )
        variation = (
            self.remote_variation_base
            + self.remote_variation_basis @ np.abs(coefficients)
        )
        kernel = np.minimum(1.0, bracket + variation)
        kernel[self.remote_alias_fallback] = 1.0
        remote = float(np.dot(self.remote_masses, kernel)) + self.elementary_remote
        return finite + min(self.base_remainder, remote)


def _cancellation_affine_data(
    lower_frequency: np.ndarray,
    upper_frequency: np.ndarray,
    observation_time: float,
    sample_count: int,
    harmonic_count: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Vectorized affine form of the cancellation interval theorem."""
    midpoint_u = 0.25 * observation_time * (
        lower_frequency + upper_frequency
    )
    half_width_u = 0.25 * observation_time * (
        upper_frequency - lower_frequency
    )
    center_terms: dict[int, np.ndarray] = {}
    variation_terms: dict[int, np.ndarray] = {}
    fallback = np.zeros(len(lower_frequency), dtype=bool)
    for shift in range(-harmonic_count, harmonic_count + 1):
        argument = (midpoint_u + math.pi * shift) / sample_count
        argument_half_width = half_width_u / sample_count
        remainder = (argument + 0.5 * math.pi) % math.pi - 0.5 * math.pi
        distance = np.maximum(0.0, np.abs(remainder) - argument_half_width)
        danger = distance <= 16.0 * np.finfo(float).eps
        fallback |= danger
        safe_distance = np.where(danger, 0.5 * math.pi, distance)
        safe_sine = np.where(danger, 1.0, np.sin(argument))
        center_terms[shift] = 1.0 / (sample_count * safe_sine)
        variation_terms[shift] = half_width_u / (
            sample_count**2 * np.sin(safe_distance) ** 2
        )
    center_basis = np.column_stack(
        [
            center_terms[harmonic] + center_terms[-harmonic]
            for harmonic in range(1, harmonic_count + 1)
        ]
    )
    variation_basis = np.column_stack(
        [
            variation_terms[harmonic] + variation_terms[-harmonic]
            for harmonic in range(1, harmonic_count + 1)
        ]
    )
    return (
        center_terms[0],
        center_basis,
        variation_terms[0],
        variation_basis,
        fallback,
    )


def prepare_all_alias_objective(
    degree: int = 9,
    targets: tuple[int, ...] = (49, 50),
    maximum_norm: int = 50,
    sigma: float = 2.0,
    truncation: int = 1_000_000,
    observation_time: float = 1_000.0,
    sample_count: int = 5_000,
    harmonic_count: int = 8,
    bin_width: float = 0.01,
    alias_periods: int = 2,
) -> list[TargetAllAliasData]:
    """Precompute the actual finite-plus-all-alias search objective."""
    if any(target < 1 or target > maximum_norm for target in targets):
        raise ValueError("optimization targets must lie in the recovered range")
    divisor = fixed_degree_divisor_coefficients_sieve(truncation, degree)
    base_remainder = fixed_degree_tail_l1_from_sieve(
        truncation, degree, sigma, divisor
    )
    alias_period = 2.0 * math.pi * sample_count / observation_time
    maximum_log = math.log(float(maximum_norm)) + (
        alias_periods + 0.5
    ) * alias_period
    mellin = zeta_log_convolution_certificate(
        maximum_log, degree, sigma, bin_width
    )
    elementary = fixed_degree_tail_l1_elementary_bound(
        mellin.maximum_log, degree, sigma
    )
    indices = np.arange(len(mellin.upper_masses), dtype=float)
    upper_product_log = (indices + degree) * mellin.bin_width
    retained = upper_product_log > math.log(truncation + 1.0)
    indices = indices[retained]
    masses = mellin.upper_masses[retained]
    lower_product_log = indices * mellin.bin_width
    upper_product_log = (indices + degree) * mellin.bin_width

    finite_norms = np.arange(maximum_norm + 1, truncation + 1, dtype=float)
    finite_weights = divisor[maximum_norm + 1 : truncation + 1] * (
        finite_norms ** (-sigma)
    )
    output: list[TargetAllAliasData] = []
    for target in targets:
        frequencies = np.log(target / finite_norms)
        finite_base, finite_basis = centered_response_components(
            frequencies,
            observation_time,
            sample_count,
            harmonic_count,
        )
        log_target = math.log(float(target))
        lower_frequency = np.maximum(0.0, lower_product_log - log_target)
        upper_frequency = upper_product_log - log_target
        affine = _cancellation_affine_data(
            lower_frequency,
            upper_frequency,
            observation_time,
            sample_count,
            harmonic_count,
        )
        output.append(
            TargetAllAliasData(
                target,
                finite_weights,
                finite_base,
                finite_basis,
                masses,
                *affine,
                elementary,
                base_remainder,
            )
        )
    return output


def all_alias_objective(
    coefficients: np.ndarray,
    prepared: list[TargetAllAliasData],
    sigma: float = 2.0,
) -> float:
    """Worst target-scaled finite-plus-all-alias tail proxy."""
    values = [
        data.target_norm**sigma * data.envelope(coefficients)
        for data in prepared
    ]
    return float(max(values))


def search_all_alias_window(
    prepared: list[TargetAllAliasData],
    initial: np.ndarray = REFERENCE_COEFFICIENTS,
    maximum_iterations: int = 250,
) -> tuple[np.ndarray, dict[str, object]]:
    """Search the nonsmooth objective; return a candidate, never a proof.

    Powell is used only as a reproducible candidate generator.  Positivity,
    density, conditioning, and the full 50-target result are checked again by
    independent routines after the search.
    """

    def penalized(candidate: np.ndarray) -> float:
        extrema = continuous_density_extrema(candidate)
        design = CosineQuadratureDesign(5_000, 1_000.0, candidate)
        gram = cosine_window_gram(50, design)
        lambda_min = float(np.linalg.eigvalsh(gram)[0])
        violation = (
            max(0.0, 9e-6 - extrema["minimum"]) ** 2
            + max(0.0, extrema["maximum"] - 2.499999999) ** 2
            + max(0.0, 0.981 - lambda_min) ** 2
        )
        return all_alias_objective(candidate, prepared) + 1e8 * violation

    result = minimize(
        penalized,
        np.asarray(initial, dtype=float),
        method="Powell",
        bounds=[(-1.0, 1.0)] * len(initial),
        options={"maxiter": maximum_iterations, "xtol": 1e-10, "ftol": 1e-11},
    )
    return np.asarray(result.x), {
        "success": bool(result.success),
        "message": str(result.message),
        "evaluations": int(result.nfev),
        "iterations": int(result.nit),
        "penalized_objective": float(result.fun),
    }


def exact_candidate_positivity_report() -> dict[str, object]:
    certificate = rational_continuum_certificate(
        ALL_ALIAS_DEGREE_NINE_COEFFICIENT_STRINGS,
        "0.0000099",
        "2.499999999",
    )
    representation_errors = [
        abs(Fraction.from_float(float(binary)) - Fraction(decimal))
        for binary, decimal in zip(
            ALL_ALIAS_DEGREE_NINE_COEFFICIENTS,
            ALL_ALIAS_DEGREE_NINE_COEFFICIENT_STRINGS,
        )
    ]
    density_perturbation = 2 * sum(representation_errors, Fraction(0))
    return {
        "strict_lower_bound": str(certificate.lower_bound),
        "strict_upper_bound": str(certificate.upper_bound),
        "lower_root_count": certificate.lower_root_count,
        "upper_root_count": certificate.upper_root_count,
        "binary64_density_perturbation_bound": str(density_perturbation),
        "binary64_strict_lower_bound": float(
            certificate.lower_bound - density_perturbation
        ),
        "binary64_strict_upper_bound": float(
            certificate.upper_bound + density_perturbation
        ),
        "certified": certificate.certified,
    }


def complete_candidate_report() -> dict[str, object]:
    """Independently recompute all 50 degree-nine candidate bounds."""
    design = CosineQuadratureDesign(
        5_000, 1_000.0, ALL_ALIAS_DEGREE_NINE_COEFFICIENTS.copy()
    )
    divisor = fixed_degree_divisor_coefficients_sieve(1_000_000, 9)
    envelope, _ = fixed_degree_tail_envelope(
        50,
        9,
        2.0,
        1_000_000,
        design,
        divisor,
        remainder_method="mellin",
    )
    gram = cosine_window_gram(50, design)
    bounds = deterministic_coefficient_bounds(gram, 2.0, envelope)
    return {
        "degree": 9,
        "worst_complete_coefficient_bound": float(np.max(bounds)),
        "worst_target_norm": int(np.argmax(bounds) + 1),
        "integer_rounding_certificate": bool(np.max(bounds) < 0.5),
        "lambda_min": float(np.linalg.eigvalsh(gram)[0]),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--objective-audit", action="store_true")
    parser.add_argument("--search", action="store_true")
    parser.add_argument("--complete-certificate", action="store_true")
    parser.add_argument("--maximum-iterations", type=int, default=250)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    report: dict[str, object] = {
        "recorded_candidate_coefficients": ALL_ALIAS_DEGREE_NINE_COEFFICIENTS.tolist(),
        "exact_candidate_positivity": exact_candidate_positivity_report(),
    }
    prepared = None
    if arguments.objective_audit or arguments.search:
        prepared = prepare_all_alias_objective()
        report["reference_joint_objective"] = all_alias_objective(
            REFERENCE_COEFFICIENTS, prepared
        )
        report["recorded_candidate_joint_objective"] = all_alias_objective(
            ALL_ALIAS_DEGREE_NINE_COEFFICIENTS, prepared
        )
    if arguments.search:
        assert prepared is not None
        candidate, search = search_all_alias_window(
            prepared, maximum_iterations=arguments.maximum_iterations
        )
        report["search"] = search
        report["searched_coefficients"] = candidate.tolist()
        report["searched_joint_objective"] = all_alias_objective(
            candidate, prepared
        )
    if arguments.complete_certificate:
        report["complete_candidate_certificate"] = complete_candidate_report()
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
