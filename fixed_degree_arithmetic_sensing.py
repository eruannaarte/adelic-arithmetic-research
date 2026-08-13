#!/usr/bin/env python3
"""Fixed-degree divisor envelopes for deterministic arithmetic sensing.

For every degree-``d`` number field, the ideal-counting coefficients satisfy
``0 <= a_K(n) <= d_d(n)``, where ``zeta(s)^d=sum d_d(n)n^-s``.  This module
turns that classical domination into complete, executable tail certificates
for the positive cosine quadratures developed in Arithmetic Sensing III--IV.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction

import numpy as np
from scipy.special import zeta

from optimized_arithmetic_quadrature import (
    CosineQuadratureDesign,
    centered_cosine_response,
    prealias_limit,
    trigonometric_kernel_interval_bound,
)
from verified_mellin_certificate import (
    exact_dyadic_convolution_power,
    fraction_to_float_upper,
    verified_one_factor_log_bins,
)


@dataclass(frozen=True)
class ZetaLogConvolutionCertificate:
    """Upper log-bin masses for the ``degree``-fold zeta distribution.

    Entry ``q`` bounds the mass of ordered factor tuples whose individual
    log-bin indices sum to ``q``.  Their product logarithm lies in
    ``[q*h, (q+degree)*h)``.  The array is truncated at ``maximum_log``;
    products beyond it are handled by the analytic complete-tail bound.
    """

    degree: int
    sigma: float
    bin_width: float
    maximum_log: float
    upper_masses: np.ndarray
    one_factor_mass_upper: float
    numerical_safety_factor: float
    verification_backend: str = "legacy floating inflation"
    one_factor_sha256: str | None = None
    convolution_sha256: str | None = None


def fixed_degree_divisor_coefficients_sieve(
    maximum_norm: int, degree: int
) -> np.ndarray:
    """Return ``d_degree(n)`` for ``0 <= n <= maximum_norm``.

    The computation iterates the Dirichlet convolution ``d_k=1*d_(k-1)``.
    It is exact while the values fit in IEEE integer precision; the intended
    fixed small degrees and research cutoffs are far inside that range.
    """
    if maximum_norm < 1 or degree < 1:
        raise ValueError("maximum_norm and degree must be positive")
    previous = np.ones(maximum_norm + 1, dtype=np.float64)
    previous[0] = 0.0
    for _ in range(2, degree + 1):
        current = np.zeros(maximum_norm + 1, dtype=np.float64)
        for divisor in range(1, maximum_norm + 1):
            current[divisor::divisor] += previous[
                1 : maximum_norm // divisor + 1
            ]
        previous = current
    return previous


def fixed_degree_tail_l1_from_sieve(
    truncation: int,
    degree: int,
    sigma: float,
    coefficients: np.ndarray | None = None,
) -> float:
    """Exact ``zeta(sigma)^degree`` remainder after the finite sum."""
    if truncation < 1 or degree < 1 or sigma <= 1.0:
        raise ValueError("invalid fixed-degree tail parameters")
    if coefficients is None:
        coefficients = fixed_degree_divisor_coefficients_sieve(
            truncation, degree
        )
    if len(coefficients) <= truncation:
        raise ValueError("coefficient array is too short")
    norms = np.arange(1, truncation + 1, dtype=float)
    partial = float(
        np.dot(coefficients[1 : truncation + 1], norms ** (-sigma))
    )
    return max(0.0, float(zeta(sigma, 1.0)) ** degree - partial)


def fixed_degree_tail_l1_elementary_bound(
    log_cutoff: float, degree: int, sigma: float
) -> float:
    """Remote bound derived from ``D_d(x)<=x(1+log x)^(d-1)``.

    Abel summation reduces the result to an upper incomplete gamma integral.
    For fixed integer degree it is the finite expression evaluated below, so
    no special-function tail or remote sieve is needed.
    """
    if log_cutoff < 0.0 or degree < 1 or sigma <= 1.0:
        raise ValueError("require X>=1, degree>=1, and sigma>1")
    power = degree - 1
    rate = sigma - 1.0
    argument = rate * (1.0 + log_cutoff)
    gamma_polynomial = sum(
        argument**index / math.factorial(index)
        for index in range(power + 1)
    )
    integral = (
        math.exp(-rate * log_cutoff)
        * math.factorial(power)
        * gamma_polynomial
        / rate ** (power + 1)
    )
    return sigma * integral


def one_factor_zeta_log_bin_upper_masses(
    maximum_log: float,
    sigma: float,
    bin_width: float = 0.01,
    exact_cutoff: int = 1_000_000,
    numerical_safety_factor: float = 1e-10,
) -> np.ndarray:
    """Legacy floating upper masses for ``sum n^-sigma`` in logarithmic bins.

    Integers through ``exact_cutoff`` are accumulated explicitly.  Above it,
    monotonicity supplies

    ``sum_(A<=n<=B)n^-sigma <= A^-sigma + integral_A^B x^-sigma dx``.

    The use of ``floor(exp(L))`` and ``ceil(exp(U))`` deliberately includes
    possible boundary integers in adjacent bins.  This small overcount keeps
    the inequality safe under boundary rounding.  New theorem runs use the
    MPFR/dyadic backend in :func:`zeta_log_convolution_certificate`; this
    routine remains available for regression comparisons.
    """
    if maximum_log <= 0.0 or sigma <= 1.0 or bin_width <= 0.0:
        raise ValueError("require positive log range/bin width and sigma>1")
    if exact_cutoff < 1 or numerical_safety_factor < 0.0:
        raise ValueError("invalid exact cutoff or safety factor")
    bin_count = math.ceil(maximum_log / bin_width)
    masses = np.zeros(bin_count, dtype=float)
    enumerated_stop = min(exact_cutoff, math.floor(math.exp(maximum_log)))
    norms = np.arange(1, enumerated_stop + 1, dtype=float)
    indices = np.floor(np.log(norms) / bin_width).astype(int)
    inside = indices < bin_count
    np.add.at(masses, indices[inside], norms[inside] ** (-sigma))

    exact_log_end = math.log(exact_cutoff + 1.0)
    for index in range(bin_count):
        lower_log = index * bin_width
        upper_log = min(maximum_log, (index + 1) * bin_width)
        if upper_log <= exact_log_end:
            continue
        lower = max(exact_cutoff + 1, math.floor(math.exp(lower_log)))
        upper = math.ceil(math.exp(upper_log))
        if upper < lower:
            continue
        integral = (
            lower ** (1.0 - sigma) - upper ** (1.0 - sigma)
        ) / (sigma - 1.0)
        masses[index] += lower ** (-sigma) + integral
    return masses * (1.0 + numerical_safety_factor)


def zeta_log_convolution_certificate(
    maximum_log: float,
    degree: int,
    sigma: float,
    bin_width: float = 0.01,
    exact_cutoff: int = 1_000_000,
    numerical_safety_factor: float | None = None,
) -> ZetaLogConvolutionCertificate:
    """Convolve one-factor log bins into an all-``d_d`` certificate.

    Because ``d_d=1^{*d}``, the weighted coefficient mass is the mass of
    ordered ``d``-tuples under multiplication.  Ordinary convolution of their
    log-bin indices therefore bounds every product bin.  Direct convolution is
    used instead of an FFT so the standard positive dot-product roundoff bound
    can be inflated explicitly at every stage.
    """
    if degree < 1:
        raise ValueError("degree must be positive")
    if numerical_safety_factor is None:
        if float(sigma).is_integer() is False or int(sigma) < 2:
            raise ValueError(
                "verified Mellin bins currently require integral sigma>=2"
            )
        width = Fraction(str(bin_width))
        bin_count = math.ceil(maximum_log / bin_width)
        verified_bins = verified_one_factor_log_bins(
            bin_count,
            width,
            int(sigma),
            exact_cutoff,
            96,
            192,
        )
        convolution = exact_dyadic_convolution_power(verified_bins, degree)
        denominator = 1 << convolution.scale_bits
        upper_masses = np.asarray(
            [
                fraction_to_float_upper(Fraction(value, denominator))
                for value in convolution.numerators
            ]
        )
        one_factor_denominator = 1 << verified_bins.scale_bits
        return ZetaLogConvolutionCertificate(
            degree,
            sigma,
            float(width),
            float(verified_bins.maximum_log),
            upper_masses,
            fraction_to_float_upper(
                Fraction(sum(verified_bins.numerators), one_factor_denominator)
            ),
            0.0,
            "MPFR outward bins plus exact dyadic convolution",
            verified_bins.sha256,
            convolution.sha256,
        )
    one_factor = one_factor_zeta_log_bin_upper_masses(
        maximum_log,
        sigma,
        bin_width,
        exact_cutoff,
        numerical_safety_factor,
    )
    bin_count = len(one_factor)
    convolved = np.asarray([1.0])
    epsilon = np.finfo(float).eps
    for _ in range(degree):
        term_count = min(len(convolved), len(one_factor))
        operations = 2 * term_count + 1
        gamma = operations * epsilon / (1.0 - operations * epsilon)
        convolved = np.convolve(convolved, one_factor)[:bin_count]
        # For a positive dot product, fl(sum)/(1-gamma) is an upper value
        # under the usual IEEE round-to-nearest error model.
        convolved = np.maximum(0.0, convolved) / (1.0 - gamma)
    return ZetaLogConvolutionCertificate(
        degree,
        sigma,
        bin_width,
        maximum_log,
        convolved,
        float(np.sum(one_factor)),
        numerical_safety_factor,
    )


def fixed_degree_mellin_alias_remainder_bound(
    target_norm: int,
    truncation: int,
    design: CosineQuadratureDesign,
    base_remainder: float,
    certificate: ZetaLogConvolutionCertificate,
) -> float:
    """All-alias ``d_d`` remainder from a log-Mellin convolution.

    Every tuple bin is multiplied by a rigorous kernel supremum on the entire
    interval in which its product can lie.  Bins crossing the truncation or the
    analytic remote boundary are included in full, so both boundaries are
    deliberately overcounted rather than silently rounded away.
    """
    if target_norm < 1 or truncation < target_norm:
        raise ValueError("target and truncation are inconsistent")
    if certificate.maximum_log <= math.log(truncation + 1.0):
        raise ValueError("certificate does not extend beyond truncation")
    log_target = math.log(float(target_norm))
    log_truncation = math.log(truncation + 1.0)
    total = 0.0
    for index, mass in enumerate(certificate.upper_masses):
        lower_product_log = index * certificate.bin_width
        upper_product_log = (
            index + certificate.degree
        ) * certificate.bin_width
        if upper_product_log <= log_truncation:
            continue
        lower_frequency = max(0.0, lower_product_log - log_target)
        upper_frequency = upper_product_log - log_target
        if upper_frequency <= 0.0:
            continue
        total += float(mass) * trigonometric_kernel_interval_bound(
            lower_frequency, upper_frequency, design
        )
    total += fixed_degree_tail_l1_elementary_bound(
        certificate.maximum_log,
        certificate.degree,
        certificate.sigma,
    )
    return min(base_remainder, total)


def fixed_degree_alias_aware_remainder_bound(
    target_norm: int,
    truncation: int,
    degree: int,
    sigma: float,
    design: CosineQuadratureDesign,
    base_remainder: float,
) -> float:
    """Complete fixed-degree remainder with pre-alias kernel decay."""
    if target_norm < 1 or truncation < target_norm:
        raise ValueError("target and truncation are inconsistent")
    start_frequency = math.log((truncation + 1.0) / target_norm)
    fundamental = 2.0 * math.pi / design.observation_time
    safe_limit = prealias_limit(design)
    if (
        start_frequency <= design.harmonic_count * fundamental
        or start_frequency >= safe_limit
        or safe_limit <= 0.0
    ):
        return base_remainder
    reciprocal_sum = 1.0 / start_frequency
    for harmonic, coefficient in enumerate(design.coefficients, start=1):
        shift = harmonic * fundamental
        reciprocal_sum += abs(float(coefficient)) * (
            1.0 / (start_frequency + shift)
            + 1.0 / (start_frequency - shift)
        )
    kernel_factor = min(
        1.0, math.pi * reciprocal_sum / design.observation_time
    )
    remote = fixed_degree_tail_l1_elementary_bound(
        math.log(float(target_norm)) + safe_limit, degree, sigma
    )
    return min(base_remainder, kernel_factor * base_remainder + remote)


def fixed_degree_tail_envelope(
    maximum_norm: int,
    degree: int,
    sigma: float,
    truncation: int,
    design: CosineQuadratureDesign,
    coefficients: np.ndarray | None = None,
    chunk_size: int = 100_000,
    remainder_method: str = "prealias",
    mellin_bin_width: float = 0.01,
    mellin_alias_periods: int = 2,
) -> tuple[np.ndarray, float]:
    """Universal complete tail envelope for every degree-``degree`` field."""
    if truncation <= maximum_norm:
        raise ValueError("truncation must exceed maximum_norm")
    if coefficients is None:
        coefficients = fixed_degree_divisor_coefficients_sieve(
            truncation, degree
        )
    if len(coefficients) <= truncation:
        raise ValueError("coefficient array is too short")
    base_remainder = fixed_degree_tail_l1_from_sieve(
        truncation, degree, sigma, coefficients
    )
    mellin_certificate = None
    if remainder_method == "mellin":
        if mellin_alias_periods < 1:
            raise ValueError("mellin_alias_periods must be positive")
        alias_period = (
            2.0 * math.pi * design.sample_count / design.observation_time
        )
        maximum_log = math.log(float(maximum_norm)) + (
            mellin_alias_periods + 0.5
        ) * alias_period
        mellin_certificate = zeta_log_convolution_certificate(
            maximum_log,
            degree,
            sigma,
            mellin_bin_width,
        )
    elif remainder_method != "prealias":
        raise ValueError("remainder_method must be 'prealias' or 'mellin'")
    result = np.zeros(maximum_norm, dtype=float)
    for target_index, target_norm in enumerate(range(1, maximum_norm + 1)):
        subtotal = 0.0
        for start in range(maximum_norm + 1, truncation + 1, chunk_size):
            stop = min(truncation + 1, start + chunk_size)
            tail_norms = np.arange(start, stop, dtype=float)
            weighted = coefficients[start:stop] * tail_norms ** (-sigma)
            frequencies = np.log(target_norm / tail_norms)
            subtotal += float(
                np.dot(
                    weighted,
                    np.abs(centered_cosine_response(frequencies, design)),
                )
            )
        if mellin_certificate is None:
            remainder = fixed_degree_alias_aware_remainder_bound(
                target_norm,
                truncation,
                degree,
                sigma,
                design,
                base_remainder,
            )
        else:
            remainder = fixed_degree_mellin_alias_remainder_bound(
                target_norm,
                truncation,
                design,
                base_remainder,
                mellin_certificate,
            )
        result[target_index] = subtotal + remainder
    return result, base_remainder
