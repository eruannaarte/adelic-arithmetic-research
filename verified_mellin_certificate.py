#!/usr/bin/env python3
"""Outward-rounded certificates for the remote log-Mellin sensing tail.

This module replaces the empirical multiplicative safety margin used in
Arithmetic Sensing V.  MPFR supplies correctly directed transcendental and
arithmetic operations.  Each one-factor bin is then rounded upward to a dyadic
rational, and every Dirichlet-convolution coefficient is computed exactly by
carry-free integer polynomial multiplication.

The current checker deliberately supports integral ``sigma >= 2``.  This
covers the published ``sigma=2`` experiment and makes every power-sum term an
exact rational before its final outward conversion.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from typing import Iterable, Sequence

import gmpy2
from gmpy2 import mpfr, mpq, mpz


@dataclass(frozen=True)
class VerifiedDyadicBins:
    """Exact dyadic upper masses with common denominator ``2**scale_bits``."""

    numerators: tuple[int, ...]
    scale_bits: int
    bin_width_numerator: int
    bin_width_denominator: int
    exact_cutoff: int
    mpfr_precision: int
    boundary_precision_maximum: int
    sha256: str

    @property
    def bin_count(self) -> int:
        return len(self.numerators)

    @property
    def maximum_log(self) -> Fraction:
        return Fraction(
            self.bin_count * self.bin_width_numerator,
            self.bin_width_denominator,
        )


@dataclass(frozen=True)
class ExactDyadicConvolution:
    """Initial coefficients of an exact power of a dyadic-bin polynomial."""

    degree: int
    numerators: tuple[int, ...]
    scale_bits: int
    coefficient_bytes: int
    sha256: str


@dataclass(frozen=True)
class VerifiedRemoteTail:
    """Per-target outward upper bounds, stored as exact dyadic rationals."""

    degree: int
    target_maximum: int
    numerators: tuple[int, ...]
    scale_bits: int
    convolution_sha256: str
    sha256: str

    def upper_fraction(self, target_norm: int) -> Fraction:
        if not 1 <= target_norm <= self.target_maximum:
            raise ValueError("target norm is outside the certificate")
        return Fraction(self.numerators[target_norm - 1], 1 << self.scale_bits)


def _context(precision: int, rounding: int) -> gmpy2.context:
    if precision < 64:
        raise ValueError("MPFR precision must be at least 64 bits")
    return gmpy2.context(gmpy2.context(), precision=precision, round=rounding)


@lru_cache(maxsize=None)
def _directed_context(precision: int, rounding: int) -> gmpy2.context:
    """Reusable explicit-operation context for the inner alias loop."""
    return _context(precision, rounding)


def _mpq(value: Fraction | int) -> mpq:
    if isinstance(value, int):
        return mpq(value)
    return mpq(value.numerator, value.denominator)


def _upper_mpfr(value: Fraction | int, precision: int) -> mpfr:
    with _context(precision, gmpy2.RoundUp):
        return mpfr(_mpq(value))


def _lower_mpfr(value: Fraction | int, precision: int) -> mpfr:
    with _context(precision, gmpy2.RoundDown):
        return mpfr(_mpq(value))


def _dyadic_ceiling(value: mpfr, scale_bits: int, precision: int) -> int:
    if value < 0 or scale_bits < 1:
        raise ValueError("dyadic upper conversion requires a nonnegative value")
    with _context(precision, gmpy2.RoundUp):
        scaled = gmpy2.mul_2exp(value, scale_bits)
        return int(gmpy2.ceil(scaled))


def _hash_integer_vector(values: Sequence[int]) -> str:
    maximum_bits = max(1, max((value.bit_length() for value in values), default=1))
    width = (maximum_bits + 7) // 8
    digest = hashlib.sha256()
    digest.update(len(values).to_bytes(8, "little"))
    digest.update(width.to_bytes(4, "little"))
    for value in values:
        if value < 0:
            raise ValueError("certificate integers must be nonnegative")
        digest.update(value.to_bytes(width, "little"))
    return digest.hexdigest()


def certified_exponential_ceiling(
    exponent: Fraction,
    initial_precision: int = 192,
    maximum_precision: int = 3_072,
) -> tuple[int, int]:
    """Return ``ceil(exp(exponent))`` and the precision certifying it.

    Downward and upward MPFR evaluations must have the same integer ceiling.
    If they do not, precision doubles.  The zero exponent is handled exactly.
    """
    if exponent == 0:
        return 1, initial_precision
    precision = initial_precision
    exact_exponent = _mpq(exponent)
    while precision <= maximum_precision:
        with _context(precision, gmpy2.RoundDown):
            lower = gmpy2.exp(mpfr(exact_exponent))
        with _context(precision, gmpy2.RoundUp):
            upper = gmpy2.exp(mpfr(exact_exponent))
        lower_ceiling = int(gmpy2.ceil(lower))
        upper_ceiling = int(gmpy2.ceil(upper))
        if lower_ceiling == upper_ceiling:
            return lower_ceiling, precision
        precision *= 2
    raise ArithmeticError("could not certify an exponential-bin boundary")


def certified_log_bin_integer_boundaries(
    bin_count: int,
    bin_width: Fraction,
    precision: int = 192,
) -> tuple[tuple[int, ...], int]:
    """Return exact integer ceilings of all exponential bin boundaries."""
    if bin_count < 1 or bin_width <= 0:
        raise ValueError("bin count and width must be positive")
    boundaries = []
    maximum_used = precision
    for index in range(bin_count + 1):
        boundary, used = certified_exponential_ceiling(
            index * bin_width, precision
        )
        boundaries.append(boundary)
        maximum_used = max(maximum_used, used)
    if any(right < left for left, right in zip(boundaries, boundaries[1:])):
        raise ArithmeticError("certified exponential boundaries are not monotone")
    return tuple(boundaries), maximum_used


def _exact_integral_test_upper(
    lower: int, upper: int, sigma: int
) -> mpq:
    """Exact rational integral-test bound for an inclusive integer interval."""
    if lower < 1 or upper < lower or sigma < 2:
        raise ValueError("invalid integral-test interval")
    leading = mpq(1, mpz(lower) ** sigma)
    integral = (
        mpq(1, mpz(lower) ** (sigma - 1))
        - mpq(1, mpz(upper) ** (sigma - 1))
    ) / (sigma - 1)
    return leading + integral


@lru_cache(maxsize=16)
def verified_one_factor_log_bins(
    bin_count: int,
    bin_width: Fraction = Fraction(1, 100),
    sigma: int = 2,
    exact_cutoff: int = 1_000_000,
    dyadic_scale_bits: int = 96,
    mpfr_precision: int = 192,
) -> VerifiedDyadicBins:
    """Construct MPFR-outward, then exactly dyadic, zeta-factor bin masses."""
    if sigma < 2 or exact_cutoff < 1:
        raise ValueError("require integral sigma>=2 and a positive exact cutoff")
    if dyadic_scale_bits < 32:
        raise ValueError("dyadic scale is too small for a useful certificate")
    boundaries, maximum_boundary_precision = certified_log_bin_integer_boundaries(
        bin_count, bin_width, mpfr_precision
    )
    numerators: list[int] = []
    with _context(mpfr_precision, gmpy2.RoundUp):
        for left, right_ceiling in zip(boundaries[:-1], boundaries[1:]):
            right = right_ceiling - 1
            total = mpfr(0)
            explicit_left = max(1, left)
            explicit_right = min(right, exact_cutoff)
            for norm in range(explicit_left, explicit_right + 1):
                total += mpfr(1) / (mpz(norm) ** sigma)
            remote_left = max(left, exact_cutoff + 1)
            if right >= remote_left:
                total += mpfr(
                    _exact_integral_test_upper(remote_left, right, sigma)
                )
            numerators.append(
                _dyadic_ceiling(total, dyadic_scale_bits, mpfr_precision)
            )
    values = tuple(numerators)
    return VerifiedDyadicBins(
        values,
        dyadic_scale_bits,
        bin_width.numerator,
        bin_width.denominator,
        exact_cutoff,
        mpfr_precision,
        maximum_boundary_precision,
        _hash_integer_vector(values),
    )


@lru_cache(maxsize=32)
def exact_dyadic_convolution_power(
    bins: VerifiedDyadicBins, degree: int
) -> ExactDyadicConvolution:
    """Compute the first ``bin_count`` coefficients of the exact ``degree`` power.

    Coefficients are packed as digits in a power-of-two base larger than the
    total coefficient mass to the requested power.  Python's arbitrary-precision
    integer multiplication then performs an exact, carry-free convolution.
    """
    if degree < 1:
        raise ValueError("degree must be positive")
    total = sum(bins.numerators)
    coefficient_bound = total**degree
    coefficient_bytes = max(1, (coefficient_bound.bit_length() + 7) // 8)
    encoded = int.from_bytes(
        b"".join(
            value.to_bytes(coefficient_bytes, "little")
            for value in bins.numerators
        ),
        "little",
    )
    powered = encoded**degree
    output_count = degree * (bins.bin_count - 1) + 1
    packed = powered.to_bytes(output_count * coefficient_bytes, "little")
    values = tuple(
        int.from_bytes(
            packed[
                coefficient_bytes * index : coefficient_bytes * (index + 1)
            ],
            "little",
        )
        for index in range(bins.bin_count)
    )
    del packed
    return ExactDyadicConvolution(
        degree,
        values,
        bins.scale_bits * degree,
        coefficient_bytes,
        _hash_integer_vector(values),
    )


def _positive_interval_add(
    left: tuple[mpfr, mpfr], right: tuple[mpfr, mpfr], precision: int
) -> tuple[mpfr, mpfr]:
    with _context(precision, gmpy2.RoundDown):
        lower = left[0] + right[0]
    with _context(precision, gmpy2.RoundUp):
        upper = left[1] + right[1]
    return lower, upper


def _positive_interval_scale(
    interval: tuple[mpfr, mpfr], scalar: Fraction, precision: int
) -> tuple[mpfr, mpfr]:
    if scalar < 0:
        raise ValueError("positive interval scaling requires a nonnegative scalar")
    exact_scalar = _mpq(scalar)
    with _context(precision, gmpy2.RoundDown):
        lower = interval[0] * mpfr(exact_scalar)
    with _context(precision, gmpy2.RoundUp):
        upper = interval[1] * mpfr(exact_scalar)
    return lower, upper


def _log_integer_interval(value: int, precision: int) -> tuple[mpfr, mpfr]:
    if value < 1:
        raise ValueError("logarithm input must be positive")
    with _context(precision, gmpy2.RoundDown):
        lower = gmpy2.log(mpfr(value))
    with _context(precision, gmpy2.RoundUp):
        upper = gmpy2.log(mpfr(value))
    return lower, upper


@lru_cache(maxsize=None)
def _pi_interval(precision: int) -> tuple[mpfr, mpfr]:
    with _context(precision, gmpy2.RoundDown):
        lower = gmpy2.const_pi()
    with _context(precision, gmpy2.RoundUp):
        upper = gmpy2.const_pi()
    return lower, upper


@lru_cache(maxsize=None)
def _shift_offset_interval(
    shift: int,
    observation_time: int,
    precision: int,
) -> tuple[mpfr, mpfr]:
    pi_lower, pi_upper = _pi_interval(precision)
    if shift >= 0:
        with _context(precision, gmpy2.RoundDown):
            lower = 2 * shift * pi_lower / observation_time
        with _context(precision, gmpy2.RoundUp):
            upper = 2 * shift * pi_upper / observation_time
    else:
        with _context(precision, gmpy2.RoundDown):
            lower = 2 * shift * pi_upper / observation_time
        with _context(precision, gmpy2.RoundUp):
            upper = 2 * shift * pi_lower / observation_time
    return lower, upper


def _shifted_frequency_interval(
    frequency: tuple[mpfr, mpfr],
    shift: int,
    observation_time: int,
    precision: int,
) -> tuple[mpfr, mpfr]:
    offset = _shift_offset_interval(shift, observation_time, precision)
    downward = _directed_context(precision, gmpy2.RoundDown)
    upward = _directed_context(precision, gmpy2.RoundUp)
    return downward.add(frequency[0], offset[0]), upward.add(
        frequency[1], offset[1]
    )


@lru_cache(maxsize=None)
def _alias_period_interval(
    sample_count: int, observation_time: int, precision: int
) -> tuple[mpfr, mpfr]:
    pi_lower, pi_upper = _pi_interval(precision)
    with _context(precision, gmpy2.RoundDown):
        lower = 2 * sample_count * pi_lower / observation_time
    with _context(precision, gmpy2.RoundUp):
        upper = 2 * sample_count * pi_upper / observation_time
    return lower, upper


@lru_cache(maxsize=None)
def _fraction_upper(numerator: int, denominator: int, precision: int) -> mpfr:
    with _context(precision, gmpy2.RoundUp):
        return mpfr(mpq(numerator, denominator))


def _distance_to_alias_lower(
    shifted_frequency: tuple[mpfr, mpfr],
    alias_period: tuple[mpfr, mpfr],
    precision: int,
) -> mpfr:
    """Directed lower bound for distance from an interval to the alias lattice."""
    if shifted_frequency[0] <= 0:
        raise ValueError("verified remote frequencies must stay positive")
    downward = _directed_context(precision, gmpy2.RoundDown)
    upward = _directed_context(precision, gmpy2.RoundUp)
    quotient_lower = downward.div(shifted_frequency[0], alias_period[1])
    quotient_upper = upward.div(shifted_frequency[1], alias_period[0])
    first = int(gmpy2.floor(quotient_lower)) - 1
    last = int(gmpy2.floor(quotient_upper)) + 2
    best: mpfr | None = None
    for alias_index in range(max(0, first), last + 1):
        difference_lower = downward.sub(
            shifted_frequency[0], downward.mul(alias_index, alias_period[1])
        )
        difference_upper = upward.sub(
            shifted_frequency[1], upward.mul(alias_index, alias_period[0])
        )
        if difference_lower <= 0 <= difference_upper:
            return mpfr(0)
        if difference_lower > 0:
            distance = difference_lower
        else:
            distance = downward.sub(0, difference_upper)
        best = distance if best is None or distance < best else best
    if best is None:
        raise ArithmeticError("failed to locate a nearest sampling alias")
    return best


def verified_kernel_interval_upper(
    frequency: tuple[mpfr, mpfr],
    observation_time: int,
    sample_count: int,
    coefficients: Sequence[Fraction],
    precision: int = 192,
) -> mpfr:
    """Outward upper envelope for the positive cosine midpoint kernel."""
    if frequency[0] < 0 or frequency[1] < frequency[0]:
        raise ValueError("invalid nonnegative frequency interval")
    alias_period = _alias_period_interval(
        sample_count, observation_time, precision
    )
    pi_upper = _pi_interval(precision)[1]
    upward = _directed_context(precision, gmpy2.RoundUp)

    def uniform_upper(shift: int) -> mpfr:
        shifted = _shifted_frequency_interval(
            frequency, shift, observation_time, precision
        )
        distance = _distance_to_alias_lower(shifted, alias_period, precision)
        if distance == 0:
            return mpfr(1)
        value = upward.div(
            pi_upper, upward.mul(observation_time, distance)
        )
        return min(mpfr(1), value)

    total = uniform_upper(0)
    for harmonic, coefficient in enumerate(coefficients, start=1):
        magnitude = _fraction_upper(
            abs(coefficient.numerator), coefficient.denominator, precision
        )
        shifted_sum = upward.add(
            uniform_upper(harmonic), uniform_upper(-harmonic)
        )
        total = upward.add(total, upward.mul(magnitude, shifted_sum))
    return min(mpfr(1), total)


def verified_elementary_tail_upper(
    maximum_log: Fraction,
    degree: int,
    sigma: int,
    precision: int = 192,
) -> mpfr:
    """Outward MPFR evaluation of the elementary complete ``d_d`` tail."""
    if maximum_log < 0 or degree < 1 or sigma < 2:
        raise ValueError("invalid fixed-degree tail parameters")
    power = degree - 1
    rate = sigma - 1
    argument = rate * (1 + maximum_log)
    polynomial = sum(
        argument**index / math.factorial(index)
        for index in range(power + 1)
    )
    rational_factor = Fraction(
        sigma * math.factorial(power), rate ** (power + 1)
    ) * polynomial
    exponent = -rate * maximum_log
    with _context(precision, gmpy2.RoundUp):
        exponential = gmpy2.exp(mpfr(_mpq(exponent)))
        return mpfr(_mpq(rational_factor)) * exponential


def verified_remote_tail_bounds(
    bins: VerifiedDyadicBins,
    convolution: ExactDyadicConvolution,
    truncation: int,
    target_maximum: int,
    observation_time: int,
    sample_count: int,
    coefficients: Sequence[Fraction],
    sigma: int = 2,
    output_scale_bits: int = 128,
) -> VerifiedRemoteTail:
    """Certify every post-truncation alias plus the analytic remote tail."""
    if convolution.degree < 1 or convolution.scale_bits != (
        bins.scale_bits * convolution.degree
    ):
        raise ValueError("bin and convolution scales disagree")
    if truncation < target_maximum or target_maximum < 1:
        raise ValueError("target and truncation parameters are inconsistent")
    precision = bins.mpfr_precision
    width = Fraction(bins.bin_width_numerator, bins.bin_width_denominator)
    log_truncation = _log_integer_interval(truncation + 1, precision)
    remote = verified_elementary_tail_upper(
        bins.maximum_log, convolution.degree, sigma, precision
    )
    outputs: list[int] = []
    downward = _directed_context(precision, gmpy2.RoundDown)
    upward = _directed_context(precision, gmpy2.RoundUp)
    for target_norm in range(1, target_maximum + 1):
        log_target = _log_integer_interval(target_norm, precision)
        total = mpfr(0)
        for index, numerator in enumerate(convolution.numerators):
            upper_log_exact = (index + convolution.degree) * width
            # Only skip a bin when its upper edge is proved below log(M+1).
            if _upper_mpfr(upper_log_exact, precision) <= log_truncation[0]:
                continue
            lower_log_exact = index * width
            lower_log = downward.div(
                lower_log_exact.numerator, lower_log_exact.denominator
            )
            upper_log = upward.div(
                upper_log_exact.numerator, upper_log_exact.denominator
            )
            frequency_lower = max(
                mpfr(0), downward.sub(lower_log, log_target[1])
            )
            frequency_upper = upward.sub(upper_log, log_target[0])
            kernel = verified_kernel_interval_upper(
                (frequency_lower, frequency_upper),
                observation_time,
                sample_count,
                coefficients,
                precision,
            )
            mass = upward.div(numerator, mpz(1) << convolution.scale_bits)
            total = upward.add(total, upward.mul(mass, kernel))
        total = upward.add(total, remote)
        outputs.append(_dyadic_ceiling(total, output_scale_bits, precision))
    values = tuple(outputs)
    return VerifiedRemoteTail(
        convolution.degree,
        target_maximum,
        values,
        output_scale_bits,
        convolution.sha256,
        _hash_integer_vector(values),
    )


def binary64_fractions(values: Iterable[float]) -> tuple[Fraction, ...]:
    """Return the exact rational values stored by a binary64 coefficient vector."""
    return tuple(Fraction.from_float(float(value)) for value in values)


def verified_mellin_bin_count(
    target_maximum: int,
    observation_time: int,
    sample_count: int,
    alias_periods: int,
    bin_width: Fraction,
    precision: int = 192,
) -> int:
    """Outwardly choose enough bins for the declared alias-period cutoff."""
    if (
        target_maximum < 1
        or observation_time < 1
        or sample_count < 2
        or alias_periods < 1
        or bin_width <= 0
    ):
        raise ValueError("invalid Mellin range parameters")
    upward = _directed_context(precision, gmpy2.RoundUp)
    log_target = _log_integer_interval(target_maximum, precision)[1]
    alias_upper = _alias_period_interval(
        sample_count, observation_time, precision
    )[1]
    multiplier = mpq(2 * alias_periods + 1, 2)
    maximum_log = upward.add(
        log_target, upward.mul(multiplier, alias_upper)
    )
    quotient = upward.div(
        maximum_log, upward.div(bin_width.numerator, bin_width.denominator)
    )
    return int(gmpy2.ceil(quotient))


def fraction_to_float_upper(value: Fraction) -> float:
    """Convert a nonnegative exact rational to a binary64 upper endpoint."""
    if value < 0:
        raise ValueError("upper conversion requires a nonnegative rational")
    result = float(value)
    if Fraction.from_float(result) < value:
        result = math.nextafter(result, math.inf)
    return result
