#!/usr/bin/env python3
"""Fixed-degree divisor envelopes for deterministic arithmetic sensing.

For every degree-``d`` number field, the ideal-counting coefficients satisfy
``0 <= a_K(n) <= d_d(n)``, where ``zeta(s)^d=sum d_d(n)n^-s``.  This module
turns that classical domination into complete, executable tail certificates
for the positive cosine quadratures developed in Arithmetic Sensing III--IV.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.special import zeta

from optimized_arithmetic_quadrature import (
    CosineQuadratureDesign,
    centered_cosine_response,
    prealias_limit,
)


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
        result[target_index] = subtotal + fixed_degree_alias_aware_remainder_bound(
            target_norm,
            truncation,
            degree,
            sigma,
            design,
            base_remainder,
        )
    return result, base_remainder
