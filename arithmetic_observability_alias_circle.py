#!/usr/bin/env python3
"""Build and verify the AO-IX fine alias-circle certificate.

The remote degree-fourteen tail is binned at logarithmic width ``10^-4``.
One-factor dyadic upper masses are convolved exactly with FLINT, while every
aligned response interval is enclosed with directed MPFR arithmetic.  The two
positive time components are combined by the triangle inequality and all 50
target sums are extracted from one exact polynomial cross-correlation.

Normal verification is intentionally light: it validates the pinned payload,
dependencies, and every exact arithmetic consequence.  ``--recompute`` (or
``--write``) reconstructs the expensive kernel table and convolution hashes.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys
import time
from typing import Sequence

import flint
from flint import arb, fmpq, fmpz_poly
import gmpy2

from exact_trigonometric_positivity import rational_continuum_certificate

from arithmetic_observability_common_nuisance import (
    DEFAULT_SOURCE_PATH,
    MAX_ARTIFACT_BYTES,
    MAX_INTEGER_BITS,
    _canonical_json,
    _fraction_text,
    _load_json_strict,
    _parse_fraction_limited,
    _pretty_json,
    _sha256,
    _sha256_file,
    _source_exact_inputs,
)
from verified_mellin_certificate import (
    _alias_period_interval,
    _directed_context,
    _dyadic_ceiling,
    _fraction_upper,
    _log_integer_interval,
    _lower_mpfr,
    _pi_interval,
    _positive_interval_add,
    _shifted_frequency_interval,
    _signed_interval_scale,
    _upper_mpfr,
    verified_elementary_tail_upper,
    verified_one_factor_log_bins,
)


SCHEMA = "arithmetic-observability-alias-circle-v1"
PINNED_PAYLOAD_SHA256 = (
    "f97fb3a484bb4e598558b47d8217be05f31b63fe1925a854b43aecf216a66c6f"
)

DIRECTORY = Path(__file__).resolve().parent
VERIFIER_PATH = DIRECTORY / "arithmetic_observability_alias_circle.py"
TESTS_PATH = DIRECTORY / "test_arithmetic_observability_alias_circle.py"
DEFAULT_ARTIFACT_PATH = (
    DIRECTORY / "arithmetic_observability_alias_circle_certificate.json"
)
DEFAULT_AO8_PATH = (
    DIRECTORY / "arithmetic_observability_common_nuisance_certificate.json"
)
VERIFIED_MELLIN_PATH = DIRECTORY / "verified_mellin_certificate.py"
AO8_VERIFIER_PATH = DIRECTORY / "arithmetic_observability_common_nuisance.py"
TRIG_POSITIVITY_PATH = DIRECTORY / "exact_trigonometric_positivity.py"

EXPECTED_SOURCE_SHA256 = (
    "ad03df9d6325512074e6940602c1c888c81abd057a5856d6212f93dc8e780517"
)
EXPECTED_AO8_FILE_SHA256 = (
    "1614d880c92d28ed19a40b2679b311a2cafd09033eb895b7f952750e84a2d63c"
)
EXPECTED_AO8_PAYLOAD_SHA256 = (
    "96b874899b16e4502d815627c7b722b9ba0332266fb30c8cd4d0579b48ca0cfd"
)
EXPECTED_MELLIN_VERIFIER_SHA256 = (
    "27f36ef566ff629bf9f77c649b657be7e672c61ab9ef7a785b90ec01fdf1ac1f"
)
EXPECTED_AO8_VERIFIER_SHA256 = (
    "2455f901a0f937bea04162b5166e9b62ace4e9a7b473088df2cc3e5a6380f177"
)
EXPECTED_TRIG_POSITIVITY_SHA256 = (
    "0ca3f3091a47138179638b0359e7a3b866fbbaddfd4306e84b254455366fb202"
)
EXPECTED_FINE_CONVOLUTION_SHA256 = (
    "634458ec1ff0d2caa8e208ccbcccca717bd435ad8cbb74fb1e458a268d98738d"
)
EXPECTED_ELEMENTARY_TAIL_OUTPUT_NUMERATOR = 11_819_567_522_467_401_254_327_978_268

DEGREE = 14
MAXIMUM_NORM = 50
TRUNCATION = 1_000_000
SIGMA = 2
BIN_DENOMINATOR = 10_000
BIN_WIDTH = Fraction(1, BIN_DENOMINATOR)
BIN_COUNT = 824_600
MAXIMUM_LOG = Fraction(4_123, 50)
ONE_FACTOR_SCALE_BITS = 96
CONVOLUTION_SCALE_BITS = ONE_FACTOR_SCALE_BITS * DEGREE
KERNEL_SCALE_BITS = 128
MIXING_SCALE_BITS = 16
COMBINED_KERNEL_SCALE_BITS = KERNEL_SCALE_BITS + MIXING_SCALE_BITS
OUTPUT_SCALE_BITS = 128
MPFR_PRECISION_BITS = 192
ARB_PRECISION_BITS = 512
COMPONENTS = ((510, 2_550, 125), (1_780, 8_900, 65_411))
ANCHORS = (1, 2, 3, 5)
MAX_ARTIFACT_BYTES_AO9 = 400_000
WINDOW_COEFFICIENT_HEX = (
    "-0x1.40b90e12d4b94p-1",
    "0x1.dad77cf46f8c8p-4",
    "0x1.b14fcaf749a4ep-10",
    "0x1.379754c620fcep-7",
    "-0x1.4bb35fcb82d98p-11",
    "-0x1.14ee054dce996p-13",
    "0x1.9dae5b7e282d1p-12",
    "-0x1.3cdbb1073429ep-12",
)
WINDOW_COEFFICIENTS = tuple(
    Fraction.from_float(float.fromhex(value)) for value in WINDOW_COEFFICIENT_HEX
)
WINDOW_A0 = Fraction(1) + 2 * sum(WINDOW_COEFFICIENTS, Fraction())
WINDOW_S2 = sum(
    abs(coefficient) * harmonic**2
    for harmonic, coefficient in enumerate(WINDOW_COEFFICIENTS, 1)
)
EXPECTED_WINDOW_A0 = Fraction(6_781_931_884_467, 576_460_752_303_423_488)
EXPECTED_WINDOW_S2 = Fraction(
    24_283_045_757_518_484_661, 18_446_744_073_709_551_616
)
if WINDOW_A0 != EXPECTED_WINDOW_A0 or WINDOW_S2 != EXPECTED_WINDOW_S2:
    raise RuntimeError("self-contained binary64 window moments changed")
if any(weight < 0 for _, _, weight in COMPONENTS) or sum(
    weight for _, _, weight in COMPONENTS
) != 1 << MIXING_SCALE_BITS:
    raise RuntimeError("positive component mixture changed")


def _ceil_div_power_of_two(value: int, shift: int) -> int:
    if value < 0 or shift < 0:
        raise ValueError("dyadic ceiling input is invalid")
    if shift == 0:
        return value
    return (value + (1 << shift) - 1) >> shift


def _hash_fixed_unsigned(values: Sequence[int], width: int) -> str:
    if width < 1:
        raise ValueError("hash width must be positive")
    digest = hashlib.sha256()
    digest.update(len(values).to_bytes(8, "little"))
    digest.update(width.to_bytes(4, "little"))
    limit = 1 << (8 * width)
    for value in values:
        integer = int(value)
        if integer < 0 or integer >= limit:
            raise ValueError("fixed-width hash input is out of range")
        digest.update(integer.to_bytes(width, "little"))
    return digest.hexdigest()


def _hash_fmpz_poly(poly: fmpz_poly, length: int) -> tuple[str, int]:
    maximum_bits = max(1, max(int(poly[index]).bit_length() for index in range(length)))
    width = (maximum_bits + 7) // 8
    digest = hashlib.sha256()
    digest.update(length.to_bytes(8, "little"))
    digest.update(width.to_bytes(4, "little"))
    for index in range(length):
        value = int(poly[index])
        if value < 0:
            raise ValueError("convolution coefficient became negative")
        digest.update(value.to_bytes(width, "little"))
    return digest.hexdigest(), width


def _continuum_positivity_record() -> dict[str, object]:
    """Reconstruct the exact Sturm certificate behind the unit kernel cap."""
    weight_numerators = [weight for _, _, weight in COMPONENTS]
    if any(weight < 0 for weight in weight_numerators) or sum(
        weight_numerators
    ) != 1 << MIXING_SCALE_BITS:
        raise ArithmeticError("component mixture is not positive normalized")
    if any(samples <= len(WINDOW_COEFFICIENTS) for _, samples, _ in COMPONENTS):
        raise ArithmeticError("sample grid does not annihilate window harmonics")
    certificate = rational_continuum_certificate(
        WINDOW_COEFFICIENTS, Fraction(9, 10**6), Fraction(5, 2)
    )
    if not certificate.certified:
        raise ArithmeticError("exact window-density positivity proof failed")
    return {
        "method": "exact rational Sturm sequences on x=cos(theta)",
        "strict_density_lower_exact": _fraction_text(certificate.lower_bound),
        "strict_density_upper_exact": _fraction_text(certificate.upper_bound),
        "lower_boundary_root_count": certificate.lower_root_count,
        "upper_boundary_root_count": certificate.upper_root_count,
        "lower_variations_at_minus_one": certificate.lower_variations_at_minus_one,
        "lower_variations_at_plus_one": certificate.lower_variations_at_plus_one,
        "upper_variations_at_minus_one": certificate.upper_variations_at_minus_one,
        "upper_variations_at_plus_one": certificate.upper_variations_at_plus_one,
        "lower_value_at_minus_one_exact": _fraction_text(
            certificate.lower_value_at_minus_one
        ),
        "lower_value_at_plus_one_exact": _fraction_text(
            certificate.lower_value_at_plus_one
        ),
        "upper_value_at_minus_one_exact": _fraction_text(
            certificate.upper_value_at_minus_one
        ),
        "upper_value_at_plus_one_exact": _fraction_text(
            certificate.upper_value_at_plus_one
        ),
        "lower_value_at_zero_exact": _fraction_text(
            certificate.lower_value_at_zero
        ),
        "upper_value_at_zero_exact": _fraction_text(
            certificate.upper_value_at_zero
        ),
        "component_weight_numerators": weight_numerators,
        "component_weight_denominator": 1 << MIXING_SCALE_BITS,
        "component_weight_numerator_sum": sum(weight_numerators),
        "component_weights_nonnegative": True,
        "all_sample_counts_exceed_window_degree": True,
        "component_normalization_exact": True,
        "consequence": (
            "each component is the Fourier transform of a positive normalized "
            "discrete measure, hence abs(K)<=1; their positive mixture also "
            "has cap one"
        ),
        "certified": True,
    }


def _exact_arb_endpoint(value: arb) -> Fraction:
    if not value.is_exact():
        raise ValueError("expected an exact Arb endpoint")
    mantissa, exponent = map(int, value.man_exp())
    if exponent >= 0:
        return Fraction(mantissa * 2**exponent)
    return Fraction(mantissa, 2 ** (-exponent))


def _arb_sqrt_record(value: Fraction) -> dict[str, object]:
    if value <= 0:
        raise ValueError("radical input must be positive")
    previous_precision = flint.ctx.prec
    try:
        flint.ctx.prec = ARB_PRECISION_BITS
        interval = arb(fmpq(value.numerator, value.denominator)).sqrt()
        lower = _exact_arb_endpoint(interval.lower())
        upper = _exact_arb_endpoint(interval.upper())
    finally:
        flint.ctx.prec = previous_precision
    if not lower * lower <= value <= upper * upper:
        raise ArithmeticError("Arb square-root enclosure is invalid")
    return {
        "precision_bits": ARB_PRECISION_BITS,
        "lower_exact": _fraction_text(lower),
        "upper_exact": _fraction_text(upper),
    }


def _corrected_distance_to_alias_lower(
    shifted_frequency: tuple[object, object],
    alias_period: tuple[object, object],
    precision: int,
):
    """Directed lower distance from a positive interval to ``q*period``.

    The product endpoint paired with a subtraction must be rounded in the
    opposite direction: lower(x-qP) subtracts an *upper* product, while
    upper(x-qP) subtracts a *lower* product.  This is intentionally local to
    AO-IX because the older helper used same-direction multiplication.
    """
    if shifted_frequency[0] <= 0:
        raise ValueError("verified remote frequencies must stay positive")
    downward = _directed_context(precision, gmpy2.RoundDown)
    upward = _directed_context(precision, gmpy2.RoundUp)
    quotient_lower = downward.div(shifted_frequency[0], alias_period[1])
    quotient_upper = upward.div(shifted_frequency[1], alias_period[0])
    first = int(gmpy2.floor(quotient_lower)) - 1
    last = int(gmpy2.floor(quotient_upper)) + 2
    best = None
    for alias_index in range(max(0, first), last + 1):
        product_upper = upward.mul(alias_index, alias_period[1])
        product_lower = downward.mul(alias_index, alias_period[0])
        difference_lower = downward.sub(
            shifted_frequency[0], product_upper
        )
        difference_upper = upward.sub(
            shifted_frequency[1], product_lower
        )
        if difference_lower <= 0 <= difference_upper:
            return gmpy2.mpfr(0)
        if difference_lower > 0:
            distance = difference_lower
        else:
            distance = downward.sub(0, difference_upper)
        best = distance if best is None or distance < best else best
    if best is None:
        raise ArithmeticError("failed to locate a nearest sampling alias")
    return best


def _corrected_dirichlet_upper(
    pi_upper: object,
    observation_time: int,
    distance_lower: object,
    precision: int,
):
    """Upper ``pi/(T*distance)`` with the denominator rounded downward."""
    if observation_time < 1 or distance_lower <= 0:
        raise ValueError("Dirichlet denominator inputs must be positive")
    downward = _directed_context(precision, gmpy2.RoundDown)
    upward = _directed_context(precision, gmpy2.RoundUp)
    denominator_lower = downward.mul(observation_time, distance_lower)
    return upward.div(pi_upper, denominator_lower)


def _corrected_derivative_upper(
    sample_count: int,
    sine_distance_lower: object,
    precision: int,
):
    """Upper ``1/(m*sin(distance)^2)`` via a lower denominator."""
    if sample_count < 2 or sine_distance_lower <= 0:
        raise ValueError("derivative denominator inputs must be positive")
    downward = _directed_context(precision, gmpy2.RoundDown)
    upward = _directed_context(precision, gmpy2.RoundUp)
    square_lower = downward.mul(sine_distance_lower, sine_distance_lower)
    denominator_lower = downward.mul(sample_count, square_lower)
    return upward.div(1, denominator_lower)


def _corrected_shifted_dirichlet_kernel_upper(
    frequency: tuple[object, object],
    observation_time: int,
    sample_count: int,
    coefficients: Sequence[Fraction],
    precision: int = MPFR_PRECISION_BITS,
):
    """Coefficient-weighted shifted-Dirichlet envelope with safe rounding."""
    if frequency[0] < 0 or frequency[1] < frequency[0]:
        raise ValueError("invalid nonnegative frequency interval")
    alias_period = _alias_period_interval(sample_count, observation_time, precision)
    pi_upper = _pi_interval(precision)[1]
    upward = _directed_context(precision, gmpy2.RoundUp)

    def uniform_upper(shift: int):
        shifted = _shifted_frequency_interval(
            frequency, shift, observation_time, precision
        )
        distance = _corrected_distance_to_alias_lower(
            shifted, alias_period, precision
        )
        if distance == 0:
            return gmpy2.mpfr(1)
        return min(
            gmpy2.mpfr(1),
            _corrected_dirichlet_upper(
                pi_upper, observation_time, distance, precision
            ),
        )

    total = uniform_upper(0)
    for harmonic, coefficient in enumerate(coefficients, start=1):
        magnitude = _fraction_upper(
            abs(coefficient.numerator), coefficient.denominator, precision
        )
        shifted_sum = upward.add(
            uniform_upper(harmonic), uniform_upper(-harmonic)
        )
        total = upward.add(total, upward.mul(magnitude, shifted_sum))
    return min(gmpy2.mpfr(1), total)


def _corrected_cancellation_kernel_upper(
    frequency: tuple[object, object],
    observation_time: int,
    sample_count: int,
    coefficients: Sequence[Fraction],
    precision: int = MPFR_PRECISION_BITS,
):
    """Correctly rounded midpoint/first-derivative csc-bracket envelope."""
    if frequency[0] < 0 or frequency[1] < frequency[0]:
        raise ValueError("invalid nonnegative frequency interval")
    downward = _directed_context(precision, gmpy2.RoundDown)
    nearest = _directed_context(precision, gmpy2.RoundToNearest)
    upward = _directed_context(precision, gmpy2.RoundUp)
    alias_period = _alias_period_interval(sample_count, observation_time, precision)
    scale_lower = downward.div(observation_time, 2 * sample_count)
    scale_upper = upward.div(observation_time, 2 * sample_count)
    center_terms: dict[int, tuple[object, object]] = {}
    variation_terms: dict[int, object] = {}
    for shift in range(-len(coefficients), len(coefficients) + 1):
        shifted = _shifted_frequency_interval(
            frequency, shift, observation_time, precision
        )
        distance_frequency = _corrected_distance_to_alias_lower(
            shifted, alias_period, precision
        )
        if distance_frequency == 0:
            return gmpy2.mpfr(1)
        argument_lower = downward.mul(scale_lower, shifted[0])
        argument_upper = upward.mul(scale_upper, shifted[1])
        argument_center = nearest.div(
            nearest.add(argument_lower, argument_upper), 2
        )
        radius = max(
            upward.sub(argument_center, argument_lower),
            upward.sub(argument_upper, argument_center),
        )
        sine_lower = downward.sin(argument_center)
        sine_upper = upward.sin(argument_center)
        if sine_lower <= 0 <= sine_upper:
            return gmpy2.mpfr(1)
        denominator_upper = upward.mul(sample_count, sine_upper)
        denominator_lower = downward.mul(sample_count, sine_lower)
        center_terms[shift] = (
            downward.div(1, denominator_upper),
            upward.div(1, denominator_lower),
        )
        distance_argument = downward.mul(scale_lower, distance_frequency)
        sine_distance = downward.sin(distance_argument)
        if sine_distance <= 0:
            return gmpy2.mpfr(1)
        derivative = _corrected_derivative_upper(
            sample_count, sine_distance, precision
        )
        variation_terms[shift] = upward.mul(radius, derivative)

    center_interval = center_terms[0]
    variation = variation_terms[0]
    for harmonic, coefficient in enumerate(coefficients, start=1):
        paired_center = _positive_interval_add(
            center_terms[harmonic], center_terms[-harmonic], precision
        )
        scaled_center = _signed_interval_scale(
            paired_center, coefficient, precision
        )
        center_interval = _positive_interval_add(
            center_interval, scaled_center, precision
        )
        paired_variation = upward.add(
            variation_terms[harmonic], variation_terms[-harmonic]
        )
        variation = upward.add(
            variation,
            upward.mul(gmpy2.mpq(abs(coefficient.numerator), coefficient.denominator), paired_variation),
        )
    center_absolute = max(
        upward.sub(0, center_interval[0]), center_interval[1]
    )
    return min(gmpy2.mpfr(1), upward.add(center_absolute, variation))


def _load_ao8(path: Path) -> tuple[dict[str, object], bytes]:
    value, raw = _load_json_strict(path, MAX_ARTIFACT_BYTES)
    if hashlib.sha256(raw).hexdigest() != EXPECTED_AO8_FILE_SHA256:
        raise ValueError("AO-VIII dependency file digest mismatch")
    if value.get("payload_sha256") != EXPECTED_AO8_PAYLOAD_SHA256:
        raise ValueError("AO-VIII payload dependency mismatch")
    payload = value.get("payload")
    if not isinstance(payload, dict) or _sha256(payload) != EXPECTED_AO8_PAYLOAD_SHA256:
        raise ValueError("AO-VIII payload content mismatch")
    parameters = payload.get("parameters")
    if (
        not isinstance(parameters, dict)
        or parameters.get("window_coefficients_binary64_hex")
        != list(WINDOW_COEFFICIENT_HEX)
    ):
        raise ValueError("AO-VIII window-coefficient inheritance mismatch")
    return payload, raw


def _certified_target_cells() -> tuple[int, ...]:
    cells: list[int] = []
    for target in range(1, MAXIMUM_NORM + 1):
        lower, upper = _log_integer_interval(target, MPFR_PRECISION_BITS)
        candidate = int(math.floor(math.log(target) * BIN_DENOMINATOR))
        cell_lower = Fraction(candidate, BIN_DENOMINATOR)
        cell_upper = Fraction(candidate + 1, BIN_DENOMINATOR)
        if not (
            _upper_mpfr(cell_lower, MPFR_PRECISION_BITS) <= lower
            and upper <= _lower_mpfr(cell_upper, MPFR_PRECISION_BITS)
        ):
            raise ArithmeticError("a target logarithm did not fit its aligned cell")
        cells.append(candidate)
    if cells[0] != 0 or cells[-1] != 39_120:
        raise ArithmeticError("aligned target-cell endpoints changed")
    return tuple(cells)


def _first_retained_convolution_index() -> int:
    log_cutoff_lower, log_cutoff_upper = _log_integer_interval(
        TRUNCATION + 1, MPFR_PRECISION_BITS
    )
    estimate = int(math.floor(math.log(TRUNCATION + 1) * BIN_DENOMINATOR)) - DEGREE
    index = max(0, estimate - 2)
    while (
        _upper_mpfr((index + DEGREE) * BIN_WIDTH, MPFR_PRECISION_BITS)
        <= log_cutoff_lower
    ):
        index += 1
    previous_endpoint_upper = _upper_mpfr(
        (index - 1 + DEGREE) * BIN_WIDTH, MPFR_PRECISION_BITS
    )
    first_endpoint_lower = _lower_mpfr(
        (index + DEGREE) * BIN_WIDTH, MPFR_PRECISION_BITS
    )
    if not (
        index == 138_142
        and previous_endpoint_upper <= log_cutoff_lower
        and log_cutoff_upper < first_endpoint_lower
    ):
        raise ArithmeticError("retained convolution boundary proof changed")
    return index


def _build_exact_convolution(verbose: bool = False) -> tuple[object, fmpz_poly, dict[str, object]]:
    started = time.perf_counter()
    bins = verified_one_factor_log_bins(
        BIN_COUNT,
        BIN_WIDTH,
        SIGMA,
        TRUNCATION,
        ONE_FACTOR_SCALE_BITS,
        MPFR_PRECISION_BITS,
    )
    if bins.maximum_log != MAXIMUM_LOG:
        raise ArithmeticError("fine-bin logarithmic endpoint changed")
    one_factor_seconds = time.perf_counter() - started
    polynomial = fmpz_poly(list(bins.numerators))
    powered = polynomial.pow_trunc(DEGREE, BIN_COUNT)
    convolution_seconds = time.perf_counter() - started - one_factor_seconds
    digest, width = _hash_fmpz_poly(powered, BIN_COUNT)
    if digest != EXPECTED_FINE_CONVOLUTION_SHA256 or width != 169:
        raise ArithmeticError("independently audited fine convolution changed")
    if verbose:
        print(
            f"fine convolution: bins={BIN_COUNT} one-factor={one_factor_seconds:.3f}s "
            f"power={convolution_seconds:.3f}s width={width}",
            file=sys.stderr,
            flush=True,
        )
    metadata = {
        "one_factor_sha256": bins.sha256,
        "one_factor_scale_bits": bins.scale_bits,
        "one_factor_boundary_precision_maximum_bits": bins.boundary_precision_maximum,
        "convolution_sha256": digest,
        "convolution_fixed_width_bytes": width,
        "convolution_scale_bits": CONVOLUTION_SCALE_BITS,
    }
    return bins, powered, metadata


def _build_kernel_table(
    first_index: int,
    target_cells: Sequence[int],
    *,
    verbose: bool = False,
) -> tuple[list[int], dict[str, object]]:
    shifts = tuple(cell + 1 for cell in target_cells)
    maximum_shift = max(shifts)
    minimum_shift = min(shifts)
    mass_length = BIN_COUNT - first_index
    kernel_minimum_index = first_index - maximum_shift
    kernel_length = mass_length + maximum_shift - minimum_shift
    kernel_maximum_index = kernel_minimum_index + kernel_length - 1
    final_endpoint = Fraction(
        kernel_maximum_index + DEGREE + 1, BIN_DENOMINATOR
    )
    if (
        kernel_minimum_index != 99_021
        or kernel_length != 725_578
        or kernel_maximum_index != 824_598
        or final_endpoint != Fraction(824_613, 10_000)
        or final_endpoint <= MAXIMUM_LOG
    ):
        raise ArithmeticError("aligned kernel coverage changed")
    coefficients = WINDOW_COEFFICIENTS
    combined: list[int] = []
    component_values: list[list[int]] = [[], []]
    unit_cap_counts = [0, 0]
    started = time.perf_counter()
    for local_index in range(kernel_length):
        index = kernel_minimum_index + local_index
        frequency = (
            _lower_mpfr(Fraction(index, BIN_DENOMINATOR), MPFR_PRECISION_BITS),
            _upper_mpfr(Fraction(index + DEGREE + 1, BIN_DENOMINATOR), MPFR_PRECISION_BITS),
        )
        numerators: list[int] = []
        for component_index, (observation_time, sample_count, _) in enumerate(COMPONENTS):
            cancellation_upper = _corrected_cancellation_kernel_upper(
                frequency,
                observation_time,
                sample_count,
                coefficients,
                MPFR_PRECISION_BITS,
            )
            shifted_dirichlet_upper = _corrected_shifted_dirichlet_kernel_upper(
                frequency,
                observation_time,
                sample_count,
                coefficients,
                MPFR_PRECISION_BITS,
            )
            upper = min(cancellation_upper, shifted_dirichlet_upper)
            numerator = _dyadic_ceiling(
                upper, KERNEL_SCALE_BITS, MPFR_PRECISION_BITS
            )
            if not 0 <= numerator <= 1 << KERNEL_SCALE_BITS:
                raise ArithmeticError("formal kernel upper left the positivity cap")
            numerators.append(numerator)
            component_values[component_index].append(numerator)
            unit_cap_counts[component_index] += numerator == 1 << KERNEL_SCALE_BITS
        combined.append(
            COMPONENTS[0][2] * numerators[0]
            + COMPONENTS[1][2] * numerators[1]
        )
        if verbose and (local_index + 1) % 50_000 == 0:
            elapsed = time.perf_counter() - started
            print(
                f"formal kernel intervals: {local_index + 1}/{kernel_length} "
                f"({elapsed:.1f}s)",
                file=sys.stderr,
                flush=True,
            )
    component_hashes = [
        _hash_fixed_unsigned(values, 17) for values in component_values
    ]
    combined_hash = _hash_fixed_unsigned(combined, 19)
    metadata = {
        "aligned_interval_index_minimum": kernel_minimum_index,
        "aligned_interval_index_maximum": kernel_maximum_index,
        "aligned_interval_count": kernel_length,
        "aligned_interval_width_exact": _fraction_text(
            Fraction(DEGREE + 1, BIN_DENOMINATOR)
        ),
        "aligned_interval_final_endpoint_exact": _fraction_text(final_endpoint),
        "component_kernel_scale_bits": KERNEL_SCALE_BITS,
        "component_table_fixed_width_bytes": 17,
        "component_table_sha256": component_hashes,
        "component_unit_cap_interval_counts": unit_cap_counts,
        "combined_kernel_scale_bits": COMBINED_KERNEL_SCALE_BITS,
        "combined_table_fixed_width_bytes": 19,
        "combined_table_sha256": combined_hash,
        "combination_rule": "125*U_510+65411*U_1780 over 2^144",
        "component_envelope_rule": (
            "minimum of the cancellation csc-bracket enclosure and the "
            "coefficient-weighted shifted-Dirichlet enclosure"
        ),
        "kernel_seconds_descriptive": time.perf_counter() - started,
    }
    return combined, metadata


def _exact_cross_correlations(
    mass: fmpz_poly,
    kernel: Sequence[int],
    offsets: Sequence[int],
) -> tuple[tuple[int, ...], float]:
    """Return ``sum_i mass[i]*kernel[i+offset]`` by one exact product.

    Out-of-range kernel indices contribute zero.  Supporting signed offsets
    makes the reversal convention independently testable on impulses.
    """
    kernel_length = len(kernel)
    reversed_kernel = fmpz_poly(list(reversed(kernel)))
    started = time.perf_counter()
    full_length = len(mass) + kernel_length - 1
    required_length = max(
        (kernel_length - 1 - int(offset) + 1 for offset in offsets),
        default=0,
    )
    required_length = min(full_length, max(0, required_length))
    correlation = mass.mul_low(reversed_kernel, required_length)
    elapsed = time.perf_counter() - started
    values: list[int] = []
    for offset in offsets:
        coefficient_index = kernel_length - 1 - int(offset)
        values.append(
            int(correlation[coefficient_index])
            if 0 <= coefficient_index < len(correlation)
            else 0
        )
    return tuple(values), elapsed


def _build_remote_vector(verbose: bool = False) -> tuple[tuple[int, ...], dict[str, object]]:
    target_cells = _certified_target_cells()
    first_index = _first_retained_convolution_index()
    elementary = verified_elementary_tail_upper(
        MAXIMUM_LOG, DEGREE, SIGMA, MPFR_PRECISION_BITS
    )
    elementary_numerator = _dyadic_ceiling(
        elementary, OUTPUT_SCALE_BITS, MPFR_PRECISION_BITS
    )
    if elementary_numerator != EXPECTED_ELEMENTARY_TAIL_OUTPUT_NUMERATOR:
        raise ArithmeticError("formal elementary-tail numerator changed")
    bins, convolution, convolution_metadata = _build_exact_convolution(verbose)
    del bins
    combined, kernel_metadata = _build_kernel_table(
        first_index, target_cells, verbose=verbose
    )
    maximum_shift = max(cell + 1 for cell in target_cells)
    mass = convolution.right_shift(first_index)
    del convolution
    if verbose:
        print("exact mass/kernel cross-correlation starting", file=sys.stderr, flush=True)
    kernel_length = int(kernel_metadata["aligned_interval_count"])
    total_scale = CONVOLUTION_SCALE_BITS + COMBINED_KERNEL_SCALE_BITS
    shift_to_output = total_scale - OUTPUT_SCALE_BITS
    offsets = tuple(maximum_shift - (cell + 1) for cell in target_cells)
    selected, correlation_seconds = _exact_cross_correlations(
        mass, combined, offsets
    )
    del combined
    outputs: list[int] = []
    raw_correlations: list[int] = []
    for raw in selected:
        if raw < 0:
            raise ArithmeticError("cross-correlation became negative")
        raw_correlations.append(raw)
        outputs.append(
            _ceil_div_power_of_two(raw, shift_to_output)
            + elementary_numerator
        )
    raw_width = max(
        1, (max(value.bit_length() for value in raw_correlations) + 7) >> 3
    )
    if verbose:
        print(
            f"cross-correlation={correlation_seconds:.3f}s",
            file=sys.stderr,
            flush=True,
        )
    metadata = {
        **convolution_metadata,
        **{key: value for key, value in kernel_metadata.items() if not key.endswith("_descriptive")},
        "first_retained_convolution_index": first_index,
        "retained_convolution_count": BIN_COUNT - first_index,
        "target_log_cell_indices": list(target_cells),
        "target_shift_definition": "s_n=floor(10000*log(n))+1",
        "cross_correlation_total_scale_bits": total_scale,
        "cross_correlation_selected_sha256": _hash_fixed_unsigned(
            raw_correlations, raw_width
        ),
        "cross_correlation_selected_fixed_width_bytes": raw_width,
        "selected_cross_correlation_numerators": [
            str(value) for value in raw_correlations
        ],
        "elementary_tail_output_numerator": elementary_numerator,
        "elementary_tail_output_scale_bits": OUTPUT_SCALE_BITS,
        "terminal_tail_addition_count": 1,
        "terminal_tail_added_after_component_mixing": True,
        "retained_bin_terminal_tail_overlap": (
            "deliberate safe overcount: retained tuple bins can extend above "
            "maximum_log while the analytic tail also begins at maximum_log"
        ),
        "remote_output_scale_bits": OUTPUT_SCALE_BITS,
    }
    return tuple(outputs), metadata


def _consequences(
    remote_numerators: Sequence[int], source_path: Path, ao8_path: Path
) -> dict[str, object]:
    if len(remote_numerators) != MAXIMUM_NORM:
        raise ValueError("fine remote vector has invalid length")
    inputs = _source_exact_inputs(source_path)
    ao8, _ = _load_ao8(ao8_path)
    finite = inputs["finite_bounds"]
    rows = inputs["row_bounds"]
    q = inputs["q"]
    assert isinstance(finite, tuple) and isinstance(rows, tuple)
    assert isinstance(q, Fraction)
    remote = tuple(
        Fraction(int(value), 1 << OUTPUT_SCALE_BITS)
        for value in remote_numerators
    )
    complete = tuple(a + b for a, b in zip(finite, remote))
    tau = max(complete)
    records: list[dict[str, object]] = []
    radii: dict[int, Fraction] = {}
    eta_values: dict[int, Fraction] = {}
    for n in range(1, MAXIMUM_NORM + 1):
        q_n = rows[n - 1]
        eta = n * n * (
            complete[n - 1] + q_n * tau / (1 - q)
        )
        schur = (1 - q - q_n * q_n) / (1 - q)
        radius_squared = (1 - eta) ** 2 * schur / (4 * n**4)
        if not 0 <= eta < 1 or schur <= 0 or radius_squared <= 0:
            raise ArithmeticError("fine observability consequence failed")
        eta_values[n] = eta
        radii[n] = radius_squared
        records.append(
            {
                "coordinate": n,
                "finite_correlation_upper_exact": _fraction_text(finite[n - 1]),
                "fine_remote_correlation_upper_exact": _fraction_text(remote[n - 1]),
                "complete_correlation_upper_exact": _fraction_text(complete[n - 1]),
                "gram_row_upper_exact": _fraction_text(q_n),
                "fine_pair_specific_eta_exact": _fraction_text(eta),
                "fine_common_box_radius_squared_exact": _fraction_text(radius_squared),
            }
        )
    anchor_bottleneck = min(ANCHORS, key=radii.__getitem__)
    all_bottleneck = min(radii, key=radii.__getitem__)
    if anchor_bottleneck != 5 or all_bottleneck != 50:
        raise ArithmeticError("fine-bin bottleneck changed")
    prefix = ao8.get("four_anchor_prefix_reduction")
    if not isinstance(prefix, dict):
        raise ValueError("AO-VIII prefix dependency is absent")
    if (
        prefix.get("query_coordinate_reduction_passed") is not True
        or prefix.get("necessary_query_coordinates")
        != {"h_1": 0, "h_2": 0, "h_3": 0, "absolute_h_5": 1}
    ):
        raise ValueError("AO-VIII query-branch reduction changed")
    alias_upper = _parse_fraction_limited(prefix.get("alias_response_squared_upper_exact"))
    base = (1 - q) * (1 - eta_values[5]) ** 2 / 5**4
    excluded: list[int] = []
    margins: list[dict[str, object]] = []
    for n in (4, *range(6, MAXIMUM_NORM + 1)):
        lower = base + (1 - q) * (1 - eta_values[n]) ** 2 / n**4
        if lower > alias_upper:
            excluded.append(n)
            margins.append(
                {
                    "coordinate": n,
                    "unit_projection_lower_squared_exact": _fraction_text(lower),
                    "excess_over_alias_upper_exact": _fraction_text(lower - alias_upper),
                }
            )
    unresolved = [n for n in range(4, MAXIMUM_NORM + 1) if n != 5 and n not in excluded]

    # A single Schur-residual direction bounds the whole remaining real
    # nonquery prefix span, and hence its integer subclass.  For the principal
    # Gram block B on W={4,6,...,50}, ||B-I||_1<=q and ||g||_1<=q_5 give
    # ||B^-1 g||_1<=q_5/(1-q).  The same row bound gives
    # gamma^2>=s_5=1-q_5^2/(1-q).
    nonquery_coordinates = (4, *range(6, MAXIMUM_NORM + 1))
    q_5 = rows[4]
    s_5 = 1 - q_5 * q_5 / (1 - q)
    beta_l1_upper = q_5 / (1 - q)
    tau_5 = complete[4]
    tau_w = max(complete[n - 1] for n in nonquery_coordinates)
    tau_w_maximizers = [
        n for n in nonquery_coordinates if complete[n - 1] == tau_w
    ]
    quotient_support_penalty = tau_5 + tau_w * beta_l1_upper
    positive_numerator = s_5 / 25 - quotient_support_penalty
    if s_5 <= 0 or positive_numerator <= 0:
        raise ArithmeticError("finite Schur quotient lower bound is not positive")
    quotient_distance_squared = positive_numerator**2 / s_5
    quotient_radius_squared = quotient_distance_squared / 4
    alias_radius_squared_upper = alias_upper / 4
    if quotient_radius_squared >= alias_radius_squared_upper:
        raise ArithmeticError("quotient lower bound contradicts the integral witness")
    quotient_radius_interval = _arb_sqrt_record(quotient_radius_squared)
    alias_radius_interval = _arb_sqrt_record(alias_radius_squared_upper)
    old_common = ao8.get("common_box_observability")
    if not isinstance(old_common, dict):
        raise ValueError("AO-VIII common-box dependency is absent")
    old_records = old_common.get("coordinate_records")
    if not isinstance(old_records, list) or len(old_records) != MAXIMUM_NORM:
        raise ValueError("AO-VIII coordinate records are malformed")
    improvements = []
    for n in (5, 50):
        old_eta = _parse_fraction_limited(old_records[n - 1].get("pair_specific_eta_bound_exact"))
        improvements.append(
            {
                "coordinate": n,
                "old_eta_exact": _fraction_text(old_eta),
                "fine_eta_exact": _fraction_text(eta_values[n]),
                "old_to_fine_eta_ratio_exact": _fraction_text(old_eta / eta_values[n]),
            }
        )
    return {
        "global_gram_row_upper_exact": _fraction_text(q),
        "fine_complete_tail_maximum_exact": _fraction_text(tau),
        "fine_complete_tail_unique_maximizer": 1 + max(
            range(MAXIMUM_NORM), key=complete.__getitem__
        ),
        "coordinate_records": records,
        "unique_four_anchor_bottleneck": anchor_bottleneck,
        "four_anchor_radius_squared_exact": _fraction_text(radii[anchor_bottleneck]),
        "unique_all_fifty_bottleneck": all_bottleneck,
        "all_fifty_radius_squared_exact": _fraction_text(radii[all_bottleneck]),
        "selected_eta_improvements": improvements,
        "prefix_reduction": {
            "comparison_upper_squared_exact": _fraction_text(alias_upper),
            "unit_h5_base_projection_squared_exact": _fraction_text(base),
            "excluded_nonquery_coordinates": excluded,
            "excluded_coordinate_records": margins,
            "unresolved_nonquery_coordinates": unresolved,
            "uniform_quotient_bound": {
                "nonquery_coordinates": list(nonquery_coordinates),
                "ao8_query_branch_reduction_inherited": True,
                "realified_real_symmetric_gram": True,
                "principal_gram_inverse_rule": (
                    "for the real symmetric principal Gram B, "
                    "norm_1(B-I)=norm_infinity(B-I)<=q and "
                    "norm_1(g)<=q_5, hence norm_1(beta)<=q_5/(1-q)"
                ),
                "row_5_off_diagonal_l1_upper_exact": _fraction_text(q_5),
                "schur_residual_squared_lower_exact": _fraction_text(s_5),
                "beta_l1_upper_exact": _fraction_text(beta_l1_upper),
                "target_5_support_upper_exact": _fraction_text(tau_5),
                "nonquery_support_maximum_upper_exact": _fraction_text(tau_w),
                "nonquery_support_maximizers": tau_w_maximizers,
                "quotient_support_penalty_upper_exact": _fraction_text(
                    quotient_support_penalty
                ),
                "positive_distance_numerator_exact": _fraction_text(
                    positive_numerator
                ),
                "quotient_distance_squared_lower_exact": _fraction_text(
                    quotient_distance_squared
                ),
                "four_anchor_critical_radius_squared_lower_exact": _fraction_text(
                    quotient_radius_squared
                ),
                "four_anchor_critical_radius_lower_outward": (
                    quotient_radius_interval
                ),
                "integral_alias_radius_squared_upper_exact": _fraction_text(
                    alias_radius_squared_upper
                ),
                "integral_alias_radius_upper_outward": alias_radius_interval,
                "squared_bracket_width_exact": _fraction_text(
                    alias_radius_squared_upper - quotient_radius_squared
                ),
                "applies_to_all_real_nonquery_prefixes": True,
                "applies_to_all_integer_nonquery_prefixes": True,
                "global_nonquery_prefix_branch_bounded": True,
                "exact_minimizer_identified": False,
            },
            "global_closest_fibre_search_completed": False,
        },
    }


def build_payload(
    source_path: Path = DEFAULT_SOURCE_PATH,
    ao8_path: Path = DEFAULT_AO8_PATH,
    *,
    verbose: bool = False,
) -> dict[str, object]:
    if flint.__version__ != "0.9.0" or flint.__FLINT_VERSION__ != "3.6.0":
        raise RuntimeError("python-flint/FLINT environment mismatch")
    if flint.ctx.threads != 1:
        raise RuntimeError("formal FLINT reconstruction requires exactly one thread")
    if gmpy2.version() != "2.3.1" or gmpy2.mpfr_version() != "MPFR 4.2.2":
        raise RuntimeError("gmpy2/MPFR environment mismatch")
    if _sha256_file(source_path) != EXPECTED_SOURCE_SHA256:
        raise ValueError("source AS-V artifact digest mismatch")
    if _sha256_file(VERIFIED_MELLIN_PATH) != EXPECTED_MELLIN_VERIFIER_SHA256:
        raise ValueError("verified Mellin implementation digest mismatch")
    if _sha256_file(AO8_VERIFIER_PATH) != EXPECTED_AO8_VERIFIER_SHA256:
        raise ValueError("AO-VIII verifier dependency digest mismatch")
    if _sha256_file(TRIG_POSITIVITY_PATH) != EXPECTED_TRIG_POSITIVITY_SHA256:
        raise ValueError("exact positivity implementation digest mismatch")
    _load_ao8(ao8_path)
    positivity = _continuum_positivity_record()
    remote, formal = _build_remote_vector(verbose)
    consequences = _consequences(remote, source_path, ao8_path)
    return {
        "scope": {
            "tail_class": "common signed degree-fourteen coefficient box",
            "remote_statement": "formal upper bounds for every k>1000000",
            "kernel_combination": "positive-component triangle inequality",
            "closest_fibre_status": (
                "global lower/upper radius bracket certified; exact minimizer "
                "not identified"
            ),
            "quadratic_cauchy_pilot_included_as_formal_result": False,
        },
        "parameters": {
            "degree": DEGREE,
            "maximum_norm": MAXIMUM_NORM,
            "sigma": SIGMA,
            "truncation": TRUNCATION,
            "bin_width": _fraction_text(BIN_WIDTH),
            "bin_count": BIN_COUNT,
            "maximum_log": _fraction_text(MAXIMUM_LOG),
            "mpfr_precision_bits": MPFR_PRECISION_BITS,
            "window_coefficients_binary64_hex": list(WINDOW_COEFFICIENT_HEX),
            "window_a0_exact": _fraction_text(WINDOW_A0),
            "window_S2_exact": _fraction_text(WINDOW_S2),
            "components": [
                {
                    "observation_time": time_value,
                    "sample_count": samples,
                    "weight": _fraction_text(Fraction(weight, 1 << MIXING_SCALE_BITS)),
                }
                for time_value, samples, weight in COMPONENTS
            ],
        },
        "dependencies": {
            "asv_source_sha256": EXPECTED_SOURCE_SHA256,
            "ao8_artifact_sha256": EXPECTED_AO8_FILE_SHA256,
            "ao8_payload_sha256": EXPECTED_AO8_PAYLOAD_SHA256,
            "verified_mellin_sha256": EXPECTED_MELLIN_VERIFIER_SHA256,
            "ao8_verifier_sha256": EXPECTED_AO8_VERIFIER_SHA256,
            "exact_trigonometric_positivity_sha256": (
                EXPECTED_TRIG_POSITIVITY_SHA256
            ),
        },
        "formal_remote": {
            **formal,
            "target_numerators": [str(value) for value in remote],
        },
        "away_from_poles": {
            "aligned_frequency_interval_exact": _fraction_text(
                Fraction(DEGREE + 1, BIN_DENOMINATOR)
            ),
            "off_pole_rule": (
                "minimum of: midpoint csc bracket plus directed first-derivative "
                "remainder, and a coefficient-weighted shifted-Dirichlet envelope; "
                "each shifted denominator uses a directed positive alias distance"
            ),
            "pole_rule": "return the global positive-measure cap abs(K)<=1",
            "all_intervals_covered_by_off_pole_or_cap": True,
            "product_bin_span_exact": _fraction_text(DEGREE * BIN_WIDTH),
            "target_log_cell_span_exact": _fraction_text(BIN_WIDTH),
            "positive_measure_certificate": positivity,
        },
        "observability_consequences": consequences,
        "negative_results": {
            "global_cauchy_route_rejected": True,
            "reason": (
                "the unfiltered post-million mass is too large; the quadratic "
                "pilot is intentionally excluded from this formal payload"
            ),
        },
        "passed": True,
    }


def artifact_document(payload: dict[str, object]) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "producer": {
            "python_flint": flint.__version__,
            "flint": flint.__FLINT_VERSION__,
            "gmpy2": gmpy2.version(),
            "mpfr": gmpy2.mpfr_version(),
            "flint_threads": flint.ctx.threads,
        },
        "payload_sha256": _sha256(payload),
        "payload": payload,
        "reproduction_files": {
            "verifier_basename": VERIFIER_PATH.name,
            "verifier_sha256": _sha256_file(VERIFIER_PATH),
            "tests_basename": TESTS_PATH.name,
            "tests_sha256": _sha256_file(TESTS_PATH),
        },
    }


def load_artifact(path: Path = DEFAULT_ARTIFACT_PATH) -> tuple[dict[str, object], bytes]:
    value, raw = _load_json_strict(path, MAX_ARTIFACT_BYTES_AO9)
    if raw != _pretty_json(value):
        raise ValueError("artifact is not canonical deterministic JSON")
    return value, raw


def _validate_fast_payload(
    payload: dict[str, object], source_path: Path, ao8_path: Path
) -> None:
    expected_keys = {
        "scope", "parameters", "dependencies", "formal_remote",
        "away_from_poles", "observability_consequences", "negative_results", "passed"
    }
    if set(payload) != expected_keys or payload.get("passed") is not True:
        raise ValueError("payload structure is invalid")
    parameters = payload.get("parameters")
    remote = payload.get("formal_remote")
    dependencies = payload.get("dependencies")
    away_from_poles = payload.get("away_from_poles")
    if not all(
        isinstance(value, dict)
        for value in (parameters, remote, dependencies, away_from_poles)
    ):
        raise ValueError("formal payload sections are missing")
    assert (
        isinstance(parameters, dict)
        and isinstance(remote, dict)
        and isinstance(dependencies, dict)
        and isinstance(away_from_poles, dict)
    )
    required_parameters = {
        "degree": DEGREE,
        "maximum_norm": MAXIMUM_NORM,
        "sigma": SIGMA,
        "truncation": TRUNCATION,
        "bin_width": _fraction_text(BIN_WIDTH),
        "bin_count": BIN_COUNT,
        "maximum_log": _fraction_text(MAXIMUM_LOG),
        "mpfr_precision_bits": MPFR_PRECISION_BITS,
        "window_coefficients_binary64_hex": list(WINDOW_COEFFICIENT_HEX),
        "window_a0_exact": _fraction_text(WINDOW_A0),
        "window_S2_exact": _fraction_text(WINDOW_S2),
        "components": [
            {
                "observation_time": time_value,
                "sample_count": samples,
                "weight": _fraction_text(
                    Fraction(weight, 1 << MIXING_SCALE_BITS)
                ),
            }
            for time_value, samples, weight in COMPONENTS
        ],
    }
    for key, expected in required_parameters.items():
        if parameters.get(key) != expected:
            raise ValueError(f"formal parameter {key} mismatch")
    parsed_coefficients = parameters.get("window_coefficients_binary64_hex")
    if parsed_coefficients != list(WINDOW_COEFFICIENT_HEX):
        raise ValueError("self-contained window coefficients changed")
    recomputed_coefficients = tuple(
        Fraction.from_float(float.fromhex(value)) for value in parsed_coefficients
    )
    recomputed_a0 = Fraction(1) + 2 * sum(recomputed_coefficients, Fraction())
    recomputed_s2 = sum(
        abs(value) * harmonic**2
        for harmonic, value in enumerate(recomputed_coefficients, 1)
    )
    if (
        _parse_fraction_limited(parameters.get("window_a0_exact")) != recomputed_a0
        or _parse_fraction_limited(parameters.get("window_S2_exact")) != recomputed_s2
    ):
        raise ValueError("stored exact window moments do not recompute")
    expected_dependencies = {
        "asv_source_sha256": EXPECTED_SOURCE_SHA256,
        "ao8_artifact_sha256": EXPECTED_AO8_FILE_SHA256,
        "ao8_payload_sha256": EXPECTED_AO8_PAYLOAD_SHA256,
        "verified_mellin_sha256": EXPECTED_MELLIN_VERIFIER_SHA256,
        "ao8_verifier_sha256": EXPECTED_AO8_VERIFIER_SHA256,
        "exact_trigonometric_positivity_sha256": (
            EXPECTED_TRIG_POSITIVITY_SHA256
        ),
    }
    if dependencies != expected_dependencies:
        raise ValueError("formal dependency map mismatch")
    if _sha256_file(source_path) != EXPECTED_SOURCE_SHA256:
        raise ValueError("source dependency changed")
    if _sha256_file(ao8_path) != EXPECTED_AO8_FILE_SHA256:
        raise ValueError("AO-VIII dependency changed")
    if _sha256_file(VERIFIED_MELLIN_PATH) != EXPECTED_MELLIN_VERIFIER_SHA256:
        raise ValueError("verified Mellin implementation dependency changed")
    if _sha256_file(AO8_VERIFIER_PATH) != EXPECTED_AO8_VERIFIER_SHA256:
        raise ValueError("AO-VIII verifier implementation dependency changed")
    if _sha256_file(TRIG_POSITIVITY_PATH) != EXPECTED_TRIG_POSITIVITY_SHA256:
        raise ValueError("exact positivity implementation dependency changed")
    if (
        away_from_poles.get("positive_measure_certificate")
        != _continuum_positivity_record()
    ):
        raise ValueError("positive-measure cap certificate changed")
    hashes = [
        remote.get("one_factor_sha256"), remote.get("convolution_sha256"),
        remote.get("combined_table_sha256"), remote.get("cross_correlation_selected_sha256"),
    ]
    component_hashes = remote.get("component_table_sha256")
    if not isinstance(component_hashes, list) or len(component_hashes) != 2:
        raise ValueError("component table hashes are malformed")
    hashes.extend(component_hashes)
    if any(not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value) for value in hashes):
        raise ValueError("formal hash field is malformed")
    numerators = remote.get("target_numerators")
    if not isinstance(numerators, list) or len(numerators) != MAXIMUM_NORM:
        raise ValueError("remote vector is malformed")
    parsed: list[int] = []
    for value in numerators:
        if not isinstance(value, str) or not value.isdigit() or (len(value) > 1 and value[0] == "0"):
            raise ValueError("remote numerator is noncanonical")
        integer = int(value)
        if integer.bit_length() > MAX_INTEGER_BITS:
            raise ValueError("remote numerator is oversized")
        parsed.append(integer)
    raw_text = remote.get("selected_cross_correlation_numerators")
    if not isinstance(raw_text, list) or len(raw_text) != MAXIMUM_NORM:
        raise ValueError("selected exact cross-correlations are malformed")
    raw_values: list[int] = []
    for value in raw_text:
        if not isinstance(value, str) or not value.isdigit() or (len(value) > 1 and value[0] == "0"):
            raise ValueError("cross-correlation numerator is noncanonical")
        integer = int(value)
        if integer.bit_length() > MAX_INTEGER_BITS:
            raise ValueError("cross-correlation numerator is oversized")
        raw_values.append(integer)
    raw_width = remote.get("cross_correlation_selected_fixed_width_bytes")
    if type(raw_width) is not int or not 1 <= raw_width <= 1024:
        raise ValueError("cross-correlation hash width is invalid")
    if _hash_fixed_unsigned(raw_values, raw_width) != remote.get("cross_correlation_selected_sha256"):
        raise ValueError("selected cross-correlation hash does not recompute")
    elementary_numerator = remote.get("elementary_tail_output_numerator")
    if type(elementary_numerator) is not int or elementary_numerator < 0:
        raise ValueError("elementary tail numerator is invalid")
    if (
        remote.get("terminal_tail_addition_count") != 1
        or remote.get("terminal_tail_added_after_component_mixing") is not True
    ):
        raise ValueError("terminal tail composition metadata changed")
    expected_remote = [
        _ceil_div_power_of_two(
            value,
            CONVOLUTION_SCALE_BITS + COMBINED_KERNEL_SCALE_BITS - OUTPUT_SCALE_BITS,
        )
        + elementary_numerator
        for value in raw_values
    ]
    if parsed != expected_remote:
        raise ValueError("remote vector is not the exact once-composed correlation")
    expected_consequences = _consequences(parsed, source_path, ao8_path)
    if _canonical_json(payload.get("observability_consequences")) != _canonical_json(expected_consequences):
        raise ValueError("stored observability consequences do not recompute")


def verify_artifact(
    artifact: dict[str, object],
    source_path: Path = DEFAULT_SOURCE_PATH,
    ao8_path: Path = DEFAULT_AO8_PATH,
    *,
    recompute: bool = False,
    verbose: bool = False,
) -> dict[str, object]:
    if set(artifact) != {"schema", "producer", "payload_sha256", "payload", "reproduction_files"}:
        raise ValueError("artifact top-level structure is invalid")
    if artifact.get("schema") != SCHEMA:
        raise ValueError("artifact schema mismatch")
    expected_producer = {
        "python_flint": "0.9.0",
        "flint": "3.6.0",
        "gmpy2": "2.3.1",
        "mpfr": "MPFR 4.2.2",
        "flint_threads": 1,
    }
    if _canonical_json(artifact.get("producer")) != _canonical_json(expected_producer):
        raise ValueError("artifact producer environment mismatch")
    current_producer = {
        "python_flint": flint.__version__,
        "flint": flint.__FLINT_VERSION__,
        "gmpy2": gmpy2.version(),
        "mpfr": gmpy2.mpfr_version(),
        "flint_threads": flint.ctx.threads,
    }
    if current_producer != expected_producer:
        raise RuntimeError("current verifier environment is not the pinned producer")
    payload = artifact.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("artifact payload is missing")
    digest = _sha256(payload)
    if artifact.get("payload_sha256") != digest:
        raise ValueError("artifact payload digest mismatch")
    if PINNED_PAYLOAD_SHA256 != "TO_BE_PINNED" and digest != PINNED_PAYLOAD_SHA256:
        raise ValueError("artifact payload differs from the pinned theorem")
    reproduction = artifact.get("reproduction_files")
    if not isinstance(reproduction, dict):
        raise ValueError("reproduction map is missing")
    expected_reproduction = {
        "verifier_basename": VERIFIER_PATH.name,
        "verifier_sha256": _sha256_file(VERIFIER_PATH),
        "tests_basename": TESTS_PATH.name,
        "tests_sha256": _sha256_file(TESTS_PATH),
    }
    if reproduction != expected_reproduction:
        raise ValueError("reproduction file digest mismatch")
    _validate_fast_payload(payload, source_path, ao8_path)
    if recompute:
        rebuilt = build_payload(source_path, ao8_path, verbose=verbose)
        if _canonical_json(rebuilt) != _canonical_json(payload):
            raise ValueError("full fine-bin reconstruction differs from artifact")
    return {
        "schema": SCHEMA,
        "payload_sha256": digest,
        "full_reconstruction": recompute,
        "passed": True,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=DEFAULT_ARTIFACT_PATH)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE_PATH)
    parser.add_argument("--ao8", type=Path, default=DEFAULT_AO8_PATH)
    parser.add_argument("--recompute", action="store_true")
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    if arguments.write is not None:
        payload = build_payload(arguments.source, arguments.ao8, verbose=True)
        artifact = artifact_document(payload)
        arguments.write.write_bytes(_pretty_json(artifact))
        print(json.dumps({"written": str(arguments.write), "payload_sha256": artifact["payload_sha256"]}, indent=2))
        return
    artifact, _ = load_artifact(arguments.certificate)
    result = verify_artifact(
        artifact,
        arguments.source,
        arguments.ao8,
        recompute=arguments.recompute,
        verbose=arguments.verbose or arguments.recompute,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
