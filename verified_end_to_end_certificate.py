#!/usr/bin/env python3
"""Ball-arithmetic finite and Gram certificates for Arithmetic Sensing V.

The remote log-Mellin term is certified separately by
``verified_mellin_certificate.py``.  This module closes the two remaining
hybrid steps:

* every explicitly enumerated response from ``N+1`` through ``M`` is summed
  with Arb real-ball arithmetic;
* the numerical Gram inverse is replaced by a Neumann-series row-norm bound.

Together with a verified remote vector, these give an end-to-end upper bound
without trusting binary64 transcendental evaluations or a numerical inverse.
"""

from __future__ import annotations

import hashlib
import multiprocessing
import os
from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

import numpy as np
from flint import arb, ctx

from arithmetic_sensing_iv import REFERENCE_COEFFICIENTS


@dataclass(frozen=True)
class VerifiedFiniteTail:
    """Per-target finite-tail upper endpoints on a common dyadic scale."""

    degree: int
    maximum_norm: int
    truncation: int
    numerators: tuple[int, ...]
    scale_bits: int
    coefficient_sha256: str
    finite_sha256: str
    arb_precision: int

    def upper_fraction(self, target_norm: int) -> Fraction:
        if not 1 <= target_norm <= self.maximum_norm:
            raise ValueError("target norm is outside the certificate")
        return Fraction(self.numerators[target_norm - 1], 1 << self.scale_bits)


@dataclass(frozen=True)
class VerifiedGramRowBound:
    """Outward upper bound for ``max_i sum_(j!=i)|G_ij|``."""

    maximum_norm: int
    numerator: int
    scale_bits: int
    row_numerators: tuple[int, ...]
    sha256: str
    arb_precision: int

    @property
    def upper_fraction(self) -> Fraction:
        return Fraction(self.numerator, 1 << self.scale_bits)


@dataclass(frozen=True)
class VerifiedEndToEndBound:
    """Exact rational consequence of finite, remote, and Gram upper bounds."""

    degree: int
    maximum_tail: Fraction
    gram_defect: Fraction
    coefficient_bound: Fraction
    worst_tail_target: int
    worst_coefficient_target: int

    @property
    def integer_rounding_certificate(self) -> bool:
        return self.coefficient_bound < Fraction(1, 2)


@dataclass(frozen=True)
class VerifiedTimeComponent:
    """One positive component of a centered multi-time sensing measure."""

    observation_time: int
    sample_count: int
    weight: Fraction


def _validate_time_ensemble(
    components: Sequence[VerifiedTimeComponent],
) -> tuple[VerifiedTimeComponent, ...]:
    result = tuple(components)
    if not result or any(
        component.observation_time < 1
        or component.sample_count < 2
        or component.weight <= 0
        for component in result
    ):
        raise ValueError("time components must have positive parameters")
    if sum((component.weight for component in result), Fraction()) != 1:
        raise ValueError("time-component weights must sum exactly to one")
    return result


def _hash_unsigned_vector(values: Sequence[int], width: int | None = None) -> str:
    if any(value < 0 for value in values):
        raise ValueError("hash input must be nonnegative")
    if width is None:
        maximum_bits = max(
            1, max((value.bit_length() for value in values), default=1)
        )
        width = (maximum_bits + 7) // 8
    digest = hashlib.sha256()
    digest.update(len(values).to_bytes(8, "little"))
    digest.update(width.to_bytes(4, "little"))
    for value in values:
        digest.update(int(value).to_bytes(width, "little"))
    return digest.hexdigest()


def exact_fixed_degree_coefficients_uint64(
    maximum_norm: int, degree: int
) -> np.ndarray:
    """Compute ``d_degree(n)`` with checked unsigned-integer convolution."""
    if maximum_norm < 1 or degree < 1:
        raise ValueError("maximum norm and degree must be positive")
    previous = np.ones(maximum_norm + 1, dtype=np.uint64)
    previous[0] = 0
    for _ in range(2, degree + 1):
        current = np.zeros(maximum_norm + 1, dtype=np.uint64)
        for divisor in range(1, maximum_norm + 1):
            destination = current[divisor::divisor]
            addition = previous[1 : maximum_norm // divisor + 1]
            updated = destination + addition
            if np.any(updated < destination):
                raise OverflowError("uint64 generalized-divisor sieve overflow")
            destination[:] = updated
        previous = current
    return previous


def _arb_fraction(value: Fraction) -> arb:
    return arb(value.numerator) / value.denominator


def _arb_binary64(value: float) -> arb:
    return _arb_fraction(Fraction.from_float(float(value)))


def _arb_upper_dyadic_numerator(value: arb, scale_bits: int) -> int:
    if scale_bits < 1 or not value.is_finite() or value < 0:
        raise ValueError("a finite nonnegative ball is required")
    mantissa, exponent = value.upper().man_exp()
    mantissa = int(mantissa)
    exponent = int(exponent) + scale_bits
    if exponent >= 0:
        return mantissa << exponent
    denominator = 1 << (-exponent)
    return (mantissa + denominator - 1) // denominator


def _centered_response(
    frequency: arb,
    observation_time: int,
    sample_count: int,
    coefficients: Sequence[arb],
    pi: arb,
) -> arb:
    """Signed common-numerator response evaluated in real-ball arithmetic."""
    u = arb(observation_time) * frequency / 2
    bracket = 1 / (sample_count * (u / sample_count).sin())
    for harmonic, coefficient in enumerate(coefficients, start=1):
        bracket += coefficient * (
            1
            / (
                sample_count
                * ((u + pi * harmonic) / sample_count).sin()
            )
            + 1
            / (
                sample_count
                * ((u - pi * harmonic) / sample_count).sin()
            )
        )
    result = u.sin() * bracket
    if not result.is_finite():
        raise ArithmeticError("ball precision did not separate a removable alias")
    return result


def _centered_response_absolute(
    frequency: arb,
    observation_time: int,
    sample_count: int,
    coefficients: Sequence[arb],
    pi: arb,
) -> arb:
    return abs(
        _centered_response(
            frequency,
            observation_time,
            sample_count,
            coefficients,
            pi,
        )
    )


_WORKER_COEFFICIENTS: np.ndarray | None = None
_WORKER_PARAMETERS: tuple[int, int, int, int, int, tuple[Fraction, ...]] | None = None
_WORKER_ENSEMBLE_PARAMETERS: tuple[
    int,
    int,
    int,
    int,
    tuple[Fraction, ...],
    tuple[VerifiedTimeComponent, ...],
] | None = None


def _initialize_finite_worker(
    coefficients: np.ndarray,
    maximum_norm: int,
    truncation: int,
    observation_time: int,
    sample_count: int,
    precision: int,
    output_scale_bits: int,
    window: tuple[Fraction, ...],
) -> None:
    global _WORKER_COEFFICIENTS, _WORKER_PARAMETERS
    _WORKER_COEFFICIENTS = coefficients
    _WORKER_PARAMETERS = (
        maximum_norm,
        truncation,
        observation_time,
        sample_count,
        precision,
        output_scale_bits,
        window,
    )


def _finite_target_worker(target_norm: int) -> tuple[int, int]:
    if _WORKER_COEFFICIENTS is None or _WORKER_PARAMETERS is None:
        raise RuntimeError("finite-tail worker was not initialized")
    (
        maximum_norm,
        truncation,
        observation_time,
        sample_count,
        precision,
        output_scale_bits,
        window,
    ) = _WORKER_PARAMETERS
    if not 1 <= target_norm <= maximum_norm:
        raise ValueError("target norm is outside the finite certificate")
    ctx.prec = precision
    pi = arb.pi()
    arb_window = tuple(_arb_fraction(value) for value in window)
    total = arb(0)
    for tail_norm in range(maximum_norm + 1, truncation + 1):
        frequency = (arb(tail_norm) / target_norm).log()
        response = _centered_response_absolute(
            frequency,
            observation_time,
            sample_count,
            arb_window,
            pi,
        )
        weight = arb(int(_WORKER_COEFFICIENTS[tail_norm])) / (
            tail_norm * tail_norm
        )
        total += weight * response
    return target_norm, _arb_upper_dyadic_numerator(total, output_scale_bits)


def _initialize_ensemble_finite_worker(
    coefficients: np.ndarray,
    maximum_norm: int,
    truncation: int,
    precision: int,
    output_scale_bits: int,
    window: tuple[Fraction, ...],
    components: tuple[VerifiedTimeComponent, ...],
) -> None:
    global _WORKER_COEFFICIENTS, _WORKER_ENSEMBLE_PARAMETERS
    _WORKER_COEFFICIENTS = coefficients
    _WORKER_ENSEMBLE_PARAMETERS = (
        maximum_norm,
        truncation,
        precision,
        output_scale_bits,
        window,
        components,
    )


def _ensemble_finite_target_worker(target_norm: int) -> tuple[int, int]:
    if _WORKER_COEFFICIENTS is None or _WORKER_ENSEMBLE_PARAMETERS is None:
        raise RuntimeError("ensemble finite-tail worker was not initialized")
    (
        maximum_norm,
        truncation,
        precision,
        output_scale_bits,
        window,
        components,
    ) = _WORKER_ENSEMBLE_PARAMETERS
    if not 1 <= target_norm <= maximum_norm:
        raise ValueError("target norm is outside the finite certificate")
    ctx.prec = precision
    pi = arb.pi()
    arb_window = tuple(_arb_fraction(value) for value in window)
    arb_weights = tuple(_arb_fraction(component.weight) for component in components)
    total = arb(0)
    for tail_norm in range(maximum_norm + 1, truncation + 1):
        frequency = (arb(tail_norm) / target_norm).log()
        response = arb(0)
        for weight, component in zip(arb_weights, components):
            response += weight * _centered_response(
                frequency,
                component.observation_time,
                component.sample_count,
                arb_window,
                pi,
            )
        coefficient_weight = arb(int(_WORKER_COEFFICIENTS[tail_norm])) / (
            tail_norm * tail_norm
        )
        total += coefficient_weight * abs(response)
    return target_norm, _arb_upper_dyadic_numerator(total, output_scale_bits)


def verified_finite_tail_bounds(
    degree: int,
    maximum_norm: int = 50,
    truncation: int = 1_000_000,
    observation_time: int = 1_000,
    sample_count: int = 5_000,
    window_coefficients: Sequence[float] = REFERENCE_COEFFICIENTS,
    precision: int = 128,
    output_scale_bits: int = 128,
    processes: int | None = None,
) -> VerifiedFiniteTail:
    """Enclose every explicitly enumerated tail correlation with Arb."""
    if truncation <= maximum_norm or precision < 64 or output_scale_bits < 32:
        raise ValueError("invalid finite-tail certificate parameters")
    coefficients = exact_fixed_degree_coefficients_uint64(truncation, degree)
    coefficient_values = tuple(int(value) for value in coefficients)
    coefficient_sha256 = _hash_unsigned_vector(coefficient_values, 8)
    window = tuple(
        Fraction.from_float(float(value)) for value in window_coefficients
    )
    initializer_arguments = (
        coefficients,
        maximum_norm,
        truncation,
        observation_time,
        sample_count,
        precision,
        output_scale_bits,
        window,
    )
    if processes is None:
        processes = min(maximum_norm, max(1, min(8, os.cpu_count() or 1)))
    if processes < 1:
        raise ValueError("process count must be positive")
    if processes == 1:
        _initialize_finite_worker(*initializer_arguments)
        pairs = [
            _finite_target_worker(target)
            for target in range(1, maximum_norm + 1)
        ]
    else:
        context = multiprocessing.get_context("spawn")
        with context.Pool(
            processes,
            initializer=_initialize_finite_worker,
            initargs=initializer_arguments,
        ) as pool:
            pairs = pool.map(_finite_target_worker, range(1, maximum_norm + 1))
    pairs.sort()
    numerators = tuple(value for _, value in pairs)
    return VerifiedFiniteTail(
        degree,
        maximum_norm,
        truncation,
        numerators,
        output_scale_bits,
        coefficient_sha256,
        _hash_unsigned_vector(numerators),
        precision,
    )


def verified_ensemble_finite_tail_bounds(
    degree: int,
    components: Sequence[VerifiedTimeComponent],
    maximum_norm: int = 50,
    truncation: int = 1_000_000,
    window_coefficients: Sequence[float] = REFERENCE_COEFFICIENTS,
    precision: int = 128,
    output_scale_bits: int = 128,
    processes: int | None = None,
) -> VerifiedFiniteTail:
    """Enclose finite tails after signed cancellation across time windows."""
    ensemble = _validate_time_ensemble(components)
    if truncation <= maximum_norm or precision < 64 or output_scale_bits < 32:
        raise ValueError("invalid finite-tail certificate parameters")
    coefficients = exact_fixed_degree_coefficients_uint64(truncation, degree)
    coefficient_values = tuple(int(value) for value in coefficients)
    coefficient_sha256 = _hash_unsigned_vector(coefficient_values, 8)
    window = tuple(
        Fraction.from_float(float(value)) for value in window_coefficients
    )
    if any(component.sample_count <= len(window) for component in ensemble):
        raise ValueError("harmonic count must be below every sample count")
    initializer_arguments = (
        coefficients,
        maximum_norm,
        truncation,
        precision,
        output_scale_bits,
        window,
        ensemble,
    )
    if processes is None:
        processes = min(maximum_norm, max(1, min(8, os.cpu_count() or 1)))
    if processes < 1:
        raise ValueError("process count must be positive")
    if processes == 1:
        _initialize_ensemble_finite_worker(*initializer_arguments)
        pairs = [
            _ensemble_finite_target_worker(target)
            for target in range(1, maximum_norm + 1)
        ]
    else:
        context = multiprocessing.get_context("spawn")
        with context.Pool(
            processes,
            initializer=_initialize_ensemble_finite_worker,
            initargs=initializer_arguments,
        ) as pool:
            pairs = pool.map(
                _ensemble_finite_target_worker,
                range(1, maximum_norm + 1),
            )
    pairs.sort()
    numerators = tuple(value for _, value in pairs)
    return VerifiedFiniteTail(
        degree,
        maximum_norm,
        truncation,
        numerators,
        output_scale_bits,
        coefficient_sha256,
        _hash_unsigned_vector(numerators),
        precision,
    )


def verified_gram_row_bound(
    maximum_norm: int = 50,
    observation_time: int = 1_000,
    sample_count: int = 5_000,
    window_coefficients: Sequence[float] = REFERENCE_COEFFICIENTS,
    precision: int = 160,
    output_scale_bits: int = 128,
) -> VerifiedGramRowBound:
    """Enclose the Gram row defect and eliminate numerical inversion."""
    if maximum_norm < 2 or precision < 64 or output_scale_bits < 32:
        raise ValueError("invalid Gram certificate parameters")
    ctx.prec = precision
    pi = arb.pi()
    window = tuple(_arb_binary64(value) for value in window_coefficients)
    rows: list[int] = []
    for left in range(1, maximum_norm + 1):
        total = arb(0)
        for right in range(1, maximum_norm + 1):
            if left == right:
                continue
            larger = max(left, right)
            smaller = min(left, right)
            frequency = (arb(larger) / smaller).log()
            total += _centered_response_absolute(
                frequency,
                observation_time,
                sample_count,
                window,
                pi,
            )
        rows.append(_arb_upper_dyadic_numerator(total, output_scale_bits))
    numerator = max(rows)
    return VerifiedGramRowBound(
        maximum_norm,
        numerator,
        output_scale_bits,
        tuple(rows),
        _hash_unsigned_vector(rows),
        precision,
    )


def verified_ensemble_gram_row_bound(
    components: Sequence[VerifiedTimeComponent],
    maximum_norm: int = 50,
    window_coefficients: Sequence[float] = REFERENCE_COEFFICIENTS,
    precision: int = 160,
    output_scale_bits: int = 128,
) -> VerifiedGramRowBound:
    """Enclose Gram row defects after signed multi-time cancellation."""
    ensemble = _validate_time_ensemble(components)
    if maximum_norm < 2 or precision < 64 or output_scale_bits < 32:
        raise ValueError("invalid Gram certificate parameters")
    ctx.prec = precision
    pi = arb.pi()
    window = tuple(_arb_binary64(value) for value in window_coefficients)
    if any(component.sample_count <= len(window) for component in ensemble):
        raise ValueError("harmonic count must be below every sample count")
    weights = tuple(_arb_fraction(component.weight) for component in ensemble)
    rows: list[int] = []
    for left in range(1, maximum_norm + 1):
        total = arb(0)
        for right in range(1, maximum_norm + 1):
            if left == right:
                continue
            larger = max(left, right)
            smaller = min(left, right)
            frequency = (arb(larger) / smaller).log()
            response = arb(0)
            for weight, component in zip(weights, ensemble):
                response += weight * _centered_response(
                    frequency,
                    component.observation_time,
                    component.sample_count,
                    window,
                    pi,
                )
            total += abs(response)
        rows.append(_arb_upper_dyadic_numerator(total, output_scale_bits))
    numerator = max(rows)
    return VerifiedGramRowBound(
        maximum_norm,
        numerator,
        output_scale_bits,
        tuple(rows),
        _hash_unsigned_vector(rows),
        precision,
    )


def verified_end_to_end_bound(
    finite: VerifiedFiniteTail,
    remote_numerators: Sequence[int],
    remote_scale_bits: int,
    gram: VerifiedGramRowBound,
    sigma: int = 2,
) -> VerifiedEndToEndBound:
    """Apply the exact Neumann-series consequence to two verified vectors."""
    if sigma < 1 or finite.maximum_norm != gram.maximum_norm:
        raise ValueError("incompatible end-to-end parameters")
    if len(remote_numerators) != finite.maximum_norm:
        raise ValueError("remote and finite target counts disagree")
    gram_defect = gram.upper_fraction
    if gram_defect >= 1:
        raise ArithmeticError("Gram row defect does not certify invertibility")
    tails = [
        finite.upper_fraction(target)
        + Fraction(remote_numerators[target - 1], 1 << remote_scale_bits)
        for target in range(1, finite.maximum_norm + 1)
    ]
    worst_index = max(range(len(tails)), key=tails.__getitem__)
    maximum_tail = tails[worst_index]
    component_bounds = [
        tail
        + Fraction(gram.row_numerators[index], 1 << gram.scale_bits)
        * maximum_tail
        / (1 - gram_defect)
        for index, tail in enumerate(tails)
    ]
    coefficient_bounds = [
        (index + 1) ** sigma * value
        for index, value in enumerate(component_bounds)
    ]
    worst_coefficient_index = max(
        range(len(coefficient_bounds)), key=coefficient_bounds.__getitem__
    )
    coefficient_bound = coefficient_bounds[worst_coefficient_index]
    return VerifiedEndToEndBound(
        finite.degree,
        maximum_tail,
        gram_defect,
        coefficient_bound,
        worst_index + 1,
        worst_coefficient_index + 1,
    )
