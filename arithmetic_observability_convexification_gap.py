#!/usr/bin/env python3
"""Build and verify the AO-X convexification-gap certificate.

This small certificate composes the pinned AO-VIII and AO-IX artifacts.  It
does four things, all independently reproducible at 512-bit Arb precision:

* reconstructs the inverse-free prefix-localization constant from the AO-IX
  Gram and support vectors;
* records the exact finite time lattice behind the symbolic zero-count bound;
* reconstructs the AO-VIII ten-mode target-5 alias witness and proves that one
  additional integral endpoint gives a strictly smaller response; and
* proves that the old ten-mode residual is not stationary in the real c_7
  nuisance direction.

The symbolic trigonometric zero theorem is mathematics, not a numerical
conclusion.  The artifact records its exact hypotheses and degree only.  It
does not claim an exact optimizer, equality of continuous and integral
problems, or realization by a number field.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from typing import Sequence

import flint
from flint import arb, ctx, fmpq

import arithmetic_observability_alias_circle as ao9
import arithmetic_observability_common_nuisance as ao8


SCHEMA = "arithmetic-observability-convexification-gap-v1"
PINNED_PAYLOAD_SHA256 = (
    "fec0b1e43893794839afb4503975ba4f51b0c9c9980e1e43b38710a690e7348c"
)

DIRECTORY = Path(__file__).resolve().parent
VERIFIER_PATH = DIRECTORY / "arithmetic_observability_convexification_gap.py"
TESTS_PATH = DIRECTORY / "test_arithmetic_observability_convexification_gap.py"
DEFAULT_ARTIFACT_PATH = (
    DIRECTORY / "arithmetic_observability_convexification_gap_certificate.json"
)
AO8_ARTIFACT_PATH = (
    DIRECTORY / "arithmetic_observability_common_nuisance_certificate.json"
)
AO9_ARTIFACT_PATH = (
    DIRECTORY / "arithmetic_observability_alias_circle_certificate.json"
)
ASV_SOURCE_PATH = (
    DIRECTORY / "certificates" / "arithmetic_sensing_v_multiscale_end_to_end.json"
)
AO8_VERIFIER_PATH = DIRECTORY / "arithmetic_observability_common_nuisance.py"
AO9_VERIFIER_PATH = DIRECTORY / "arithmetic_observability_alias_circle.py"
AO8_TESTS_PATH = DIRECTORY / "test_arithmetic_observability_common_nuisance.py"
AO9_TESTS_PATH = DIRECTORY / "test_arithmetic_observability_alias_circle.py"
VERIFIED_MELLIN_PATH = DIRECTORY / "verified_mellin_certificate.py"
TRIG_POSITIVITY_PATH = DIRECTORY / "exact_trigonometric_positivity.py"

EXPECTED_AO8_ARTIFACT_SHA256 = (
    "1614d880c92d28ed19a40b2679b311a2cafd09033eb895b7f952750e84a2d63c"
)
EXPECTED_AO8_PAYLOAD_SHA256 = (
    "96b874899b16e4502d815627c7b722b9ba0332266fb30c8cd4d0579b48ca0cfd"
)
EXPECTED_AO9_ARTIFACT_SHA256 = (
    "14167ed603a5c003e07f01f6939fea846707693ab0fc81d515267710f4fb95ad"
)
EXPECTED_AO9_PAYLOAD_SHA256 = (
    "f97fb3a484bb4e598558b47d8217be05f31b63fe1925a854b43aecf216a66c6f"
)
EXPECTED_ASV_SOURCE_SHA256 = (
    "ad03df9d6325512074e6940602c1c888c81abd057a5856d6212f93dc8e780517"
)
EXPECTED_AO8_VERIFIER_SHA256 = (
    "2455f901a0f937bea04162b5166e9b62ace4e9a7b473088df2cc3e5a6380f177"
)
EXPECTED_AO9_VERIFIER_SHA256 = (
    "48b21a06c9687a51f1774e802651570813823eb4d9fda29d0eb60e09f7c8dd00"
)
EXPECTED_AO8_TESTS_SHA256 = (
    "bad33828fb22ae8a2a7ee995c3acf5d8bf76ff5f4b0648f78a87ccddadefe1fe"
)
EXPECTED_AO9_TESTS_SHA256 = (
    "8dd7d601e6242f8c44d08fccab99f9bd67b202d18a9d2de4ce6db016a90db73d"
)
EXPECTED_VERIFIED_MELLIN_SHA256 = (
    "27f36ef566ff629bf9f77c649b657be7e672c61ab9ef7a785b90ec01fdf1ac1f"
)
EXPECTED_TRIG_POSITIVITY_SHA256 = (
    "0ca3f3091a47138179638b0359e7a3b866fbbaddfd4306e84b254455366fb202"
)

PINNED_PYTHON_FLINT_VERSION = "0.9.0"
PINNED_FLINT_VERSION = "3.6.0"
FORMAL_PRECISION_BITS = 512
MAX_ARTIFACT_BYTES = 500_000
MAX_INTEGER_BITS = 8192
MAX_CONTAINER_ITEMS = ao8.MAX_CONTAINER_ITEMS
MAX_JSON_DEPTH = ao8.MAX_JSON_DEPTH
DEGREE = 14
MAXIMUM_NORM = 50
SIGMA = 2
TARGET = 5
PROFILE_COORDINATE = 7
FIRST_ALIAS_MULTIPLE_OF_PI = 10
COMMON_TIME_DENOMINATOR = 10
EFFECTIVE_TRIGONOMETRIC_DEGREE = 8_899
NONQUERY_COORDINATES = (4, *range(6, MAXIMUM_NORM + 1))

# Each entry is (mode, canonical prime factorization).  The first ten entries
# are duplicated deliberately from AO-VIII so this artifact can prove exactly
# what it inherited before appending the frozen rank-11 discovery candidate.
TEN_MODE_FACTORIZATIONS = (
    (220_157_529_292_800, ((2, 18), (3, 4), (5, 2), (11, 1), (37, 1), (1019, 1))),
    (220_157_529_264_288, ((2, 5), (3, 8), (7, 2), (11, 2), (47, 1), (53, 1), (71, 1))),
    (220_157_529_863_040, ((2, 7), (3, 5), (5, 1), (7, 1), (11, 1), (17, 1), (97, 1), (11149, 1))),
    (220_157_528_661_000, ((2, 3), (3, 4), (5, 3), (7, 2), (41, 1), (43, 1), (73, 1), (431, 1))),
    (220_157_530_205_184, ((2, 10), (3, 5), (11, 2), (13, 1), (101, 1), (5569, 1))),
    (220_157_529_984_000, ((2, 10), (3, 3), (5, 3), (7, 3), (185723, 1))),
    (220_157_529_055_200, ((2, 5), (3, 3), (5, 2), (11, 2), (17, 1), (73, 1), (103, 1), (659, 1))),
    (220_157_528_520_384, ((2, 6), (3, 4), (7, 1), (13, 1), (23, 2), (29, 2), (1049, 1))),
    (220_157_528_834_880, ((2, 6), (3, 3), (5, 1), (7, 1), (13, 1), (17, 1), (71, 1), (139, 1), (1669, 1))),
    (220_157_529_177_600, ((2, 9), (3, 2), (5, 2), (7, 1), (17, 2), (41, 1), (23041, 1))),
)
RANK_ELEVEN_MODE = (
    220_157_529_845_760,
    ((2, 12), (3, 3), (5, 1), (13, 1), (67, 1), (331, 1), (1381, 1)),
)
ELEVEN_MODE_FACTORIZATIONS = (*TEN_MODE_FACTORIZATIONS, RANK_ELEVEN_MODE)
EXPECTED_RANK_ELEVEN_D14 = 1_566_233_842_432_000
EXPECTED_RANK_ELEVEN_AMPLITUDE = Fraction(
    30_590_504_735, 946_666_756_792_709_085_339_648
)
EXPECTED_PREFIX_BOUND = Fraction(
    16_688_084_211_890_858_330_028_988_462_516_236_800,
    340_025_198_163_956_948_694_860_099_125_209_204_749,
)
if ao8.MAX_INTEGER_BITS != MAX_INTEGER_BITS:
    raise RuntimeError("inherited strict-parser integer bound changed")


def _fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def _parse_fraction_limited(value: object) -> Fraction:
    return ao8._parse_fraction_limited(value)


def _canonical_json(value: object) -> bytes:
    return ao8._canonical_json(value)


def _pretty_json(value: object) -> bytes:
    return ao8._pretty_json(value)


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _sha256_file(path: Path) -> str:
    return ao8._sha256_file(path)


def _load_json_strict(path: Path, maximum_bytes: int) -> tuple[dict[str, object], bytes]:
    return ao8._load_json_strict(path, maximum_bytes)


def _arb_rational(value: Fraction | int) -> arb:
    value = Fraction(value)
    return arb(fmpq(value.numerator, value.denominator))


def _lower_exact(value: arb) -> Fraction:
    return ao8._lower_exact(value)


def _upper_exact(value: arb) -> Fraction:
    return ao8._upper_exact(value)


def _interval_record(value: arb) -> dict[str, object]:
    lower = _lower_exact(value)
    upper = _upper_exact(value)
    if lower > upper:
        raise ArithmeticError("Arb interval endpoints are reversed")
    return {
        "lower_exact": _fraction_text(lower),
        "upper_exact": _fraction_text(upper),
        "precision_bits": FORMAL_PRECISION_BITS,
    }


def _sqrt_interval_record(value: Fraction) -> dict[str, object]:
    if value < 0:
        raise ValueError("cannot enclose the square root of a negative rational")
    return _interval_record(_arb_rational(value).sqrt())


def _check_environment() -> None:
    if flint.__version__ != PINNED_PYTHON_FLINT_VERSION:
        raise RuntimeError("python-flint version differs from the pinned producer")
    if flint.__FLINT_VERSION__ != PINNED_FLINT_VERSION:
        raise RuntimeError("FLINT version differs from the pinned producer")
    if ctx.threads != 1:
        raise RuntimeError("formal reconstruction requires one FLINT thread")


def _dependency_hashes() -> dict[str, str]:
    return {
        "ao8_artifact_sha256": EXPECTED_AO8_ARTIFACT_SHA256,
        "ao8_payload_sha256": EXPECTED_AO8_PAYLOAD_SHA256,
        "ao8_tests_sha256": EXPECTED_AO8_TESTS_SHA256,
        "ao8_verifier_sha256": EXPECTED_AO8_VERIFIER_SHA256,
        "ao9_artifact_sha256": EXPECTED_AO9_ARTIFACT_SHA256,
        "ao9_payload_sha256": EXPECTED_AO9_PAYLOAD_SHA256,
        "ao9_tests_sha256": EXPECTED_AO9_TESTS_SHA256,
        "ao9_verifier_sha256": EXPECTED_AO9_VERIFIER_SHA256,
        "asv_source_sha256": EXPECTED_ASV_SOURCE_SHA256,
        "exact_trigonometric_positivity_sha256": EXPECTED_TRIG_POSITIVITY_SHA256,
        "verified_mellin_sha256": EXPECTED_VERIFIED_MELLIN_SHA256,
    }


def _load_and_validate_dependencies() -> tuple[dict[str, object], dict[str, object]]:
    expected_files = {
        AO8_ARTIFACT_PATH: EXPECTED_AO8_ARTIFACT_SHA256,
        AO9_ARTIFACT_PATH: EXPECTED_AO9_ARTIFACT_SHA256,
        ASV_SOURCE_PATH: EXPECTED_ASV_SOURCE_SHA256,
        AO8_VERIFIER_PATH: EXPECTED_AO8_VERIFIER_SHA256,
        AO9_VERIFIER_PATH: EXPECTED_AO9_VERIFIER_SHA256,
        AO8_TESTS_PATH: EXPECTED_AO8_TESTS_SHA256,
        AO9_TESTS_PATH: EXPECTED_AO9_TESTS_SHA256,
        VERIFIED_MELLIN_PATH: EXPECTED_VERIFIED_MELLIN_SHA256,
        TRIG_POSITIVITY_PATH: EXPECTED_TRIG_POSITIVITY_SHA256,
    }
    for path, expected in expected_files.items():
        if _sha256_file(path) != expected:
            raise ValueError(f"pinned dependency changed: {path.name}")

    ao8_artifact, _ = ao8.load_artifact(AO8_ARTIFACT_PATH)
    ao9_artifact, _ = ao9.load_artifact(AO9_ARTIFACT_PATH)
    if ao8_artifact.get("payload_sha256") != EXPECTED_AO8_PAYLOAD_SHA256:
        raise ValueError("AO-VIII payload digest changed")
    if ao9_artifact.get("payload_sha256") != EXPECTED_AO9_PAYLOAD_SHA256:
        raise ValueError("AO-IX payload digest changed")
    if not ao8.verify_artifact(ao8_artifact, ASV_SOURCE_PATH).get("passed"):
        raise ValueError("AO-VIII dependency verification failed")
    if not ao9.verify_artifact(
        ao9_artifact, ASV_SOURCE_PATH, AO8_ARTIFACT_PATH
    ).get("passed"):
        raise ValueError("AO-IX dependency verification failed")
    return ao8_artifact, ao9_artifact


def _is_prime_trial(value: int) -> bool:
    if value < 2:
        return False
    return all(value % divisor for divisor in range(2, math.isqrt(value) + 1))


def _factorization_product(factors: Sequence[tuple[int, int]]) -> int:
    result = 1
    previous = 1
    for prime, exponent in factors:
        if type(prime) is not int or type(exponent) is not int:
            raise ValueError("factorization entries must be exact integers")
        if prime <= previous or exponent < 1 or not _is_prime_trial(prime):
            raise ValueError("factorization is not canonical prime-power data")
        result *= prime**exponent
        previous = prime
    return result


def _d14_from_factors(factors: Sequence[tuple[int, int]]) -> int:
    return math.prod(math.comb(13 + exponent, exponent) for _, exponent in factors)


def _kernel(left: int, right: int) -> arb:
    return ao8._kernel(left, right)


def _mode_record(
    mode: int,
    factors: Sequence[tuple[int, int]],
    *,
    discovery_rank: int,
) -> tuple[dict[str, object], Fraction]:
    factors = tuple((prime, exponent) for prime, exponent in factors)
    if mode <= MAXIMUM_NORM or _factorization_product(factors) != mode:
        raise ValueError("alias-mode factorization does not reconstruct its mode")
    coefficient = _d14_from_factors(factors)
    amplitude = Fraction(coefficient, mode**SIGMA)
    phase = (arb(mode) / TARGET).log() - FIRST_ALIAS_MULTIPLE_OF_PI * arb.pi()
    target_kernel = _kernel(mode, TARGET)
    shell = Fraction(1, 10**8)
    if not (abs(phase) < _arb_rational(shell)):
        raise ArithmeticError("alias mode left the certified first-alias shell")
    if not target_kernel < 0:
        raise ArithmeticError("alias mode no longer cancels the target column")
    return (
        {
            "mode": mode,
            "factorization": [[prime, exponent] for prime, exponent in factors],
            "factorization_product_verified": True,
            "d14": coefficient,
            "tail_coefficient": coefficient,
            "tail_coefficient_is_integral": True,
            "tail_coefficient_saturates_legal_endpoint": True,
            "normalized_amplitude_exact": _fraction_text(amplitude),
            "first_alias_phase_offset_outward": _interval_record(phase),
            "first_alias_shell_absolute_bound_exact": _fraction_text(shell),
            "phase_is_strictly_inside_first_alias_shell": True,
            "target_kernel_outward": _interval_record(target_kernel),
            "target_kernel_strictly_negative": True,
            "nonformal_discovery_rank": discovery_rank,
        },
        amplitude,
    )


def _compute_witness(
    frozen_modes: Sequence[tuple[int, Sequence[tuple[int, int]]]],
) -> tuple[dict[str, object], dict[str, object]]:
    records: list[dict[str, object]] = []
    modes: list[int] = []
    amplitudes: list[Fraction] = []
    for rank, (mode, factors) in enumerate(frozen_modes, 1):
        record, amplitude = _mode_record(mode, factors, discovery_rank=rank)
        records.append(record)
        modes.append(mode)
        amplitudes.append(amplitude)
    if len(set(modes)) != len(modes):
        raise ValueError("alias witness repeats a mode")

    target_cross = arb(0)
    for mode, amplitude in zip(modes, amplitudes):
        target_cross += _arb_rational(amplitude) * _kernel(mode, TARGET)
    tail_norm_squared = arb(0)
    for left_mode, left_amplitude in zip(modes, amplitudes):
        for right_mode, right_amplitude in zip(modes, amplitudes):
            tail_norm_squared += (
                _arb_rational(left_amplitude * right_amplitude)
                * _kernel(left_mode, right_mode)
            )
    target_amplitude = Fraction(1, TARGET**SIGMA)
    response_squared = (
        _arb_rational(target_amplitude**2)
        + 2 * _arb_rational(target_amplitude) * target_cross
        + tail_norm_squared
    )
    if not response_squared > 0:
        raise ArithmeticError("alias response square is not positive")
    distance = response_squared.sqrt()
    radius = distance / 2
    if not _upper_exact(radius) < Fraction(1, 2 * TARGET**SIGMA):
        raise ArithmeticError("alias witness does not beat the zero-tail radius")
    record = {
        "target_coordinate": TARGET,
        "prefix_difference": "plus e_5",
        "tail_assignment": (
            "one fibre uses b_n=d_14(n) at every listed mode; the comparison "
            "fibre and all unlisted modes use zero"
        ),
        "tail_class": "integral nonnegative d_14-dominated endpoint tails",
        "mode_count": len(modes),
        "mode_records": records,
        "total_normalized_tail_amplitude_exact": _fraction_text(
            sum(amplitudes, Fraction())
        ),
        "target_cross_inner_product_outward": _interval_record(target_cross),
        "tail_norm_squared_outward": _interval_record(tail_norm_squared),
        "response_squared_outward": _interval_record(response_squared),
        "distance_outward": _interval_record(distance),
        "critical_radius_outward": _interval_record(radius),
        "zero_tail_radius_exact": _fraction_text(Fraction(1, 2 * TARGET**SIGMA)),
        "all_modes_outside_prefix": all(mode > MAXIMUM_NORM for mode in modes),
        "all_tail_coefficients_integral_and_legal": True,
        "continuous_convexity_used": False,
        "passed": True,
    }
    state: dict[str, object] = {
        "modes": tuple(modes),
        "amplitudes": tuple(amplitudes),
        "response_squared": response_squared,
        "distance": distance,
        "radius": radius,
    }
    return record, state


def _strict_rank_eleven_improvement(
    old_state: dict[str, object], new_state: dict[str, object]
) -> dict[str, object]:
    old_squared = old_state["response_squared"]
    new_squared = new_state["response_squared"]
    old_radius = old_state["radius"]
    new_radius = new_state["radius"]
    assert isinstance(old_squared, arb) and isinstance(new_squared, arb)
    assert isinstance(old_radius, arb) and isinstance(new_radius, arb)
    squared_gap_lower = _lower_exact(old_squared) - _upper_exact(new_squared)
    radius_gap_lower = _lower_exact(old_radius) - _upper_exact(new_radius)
    if squared_gap_lower <= 0 or radius_gap_lower <= 0:
        raise ArithmeticError("rank-11 witness improvement is not interval-separated")

    old_modes = old_state["modes"]
    old_amplitudes = old_state["amplitudes"]
    assert isinstance(old_modes, tuple) and isinstance(old_amplitudes, tuple)
    rank_eleven_mode = RANK_ELEVEN_MODE[0]
    rank_eleven_amplitude = EXPECTED_RANK_ELEVEN_AMPLITUDE
    target_cross_kernel = _kernel(TARGET, rank_eleven_mode)
    inner = _arb_rational(Fraction(1, TARGET**SIGMA)) * target_cross_kernel
    cross_kernel_records = []
    for mode, amplitude in zip(old_modes, old_amplitudes):
        cross_kernel = _kernel(mode, rank_eleven_mode)
        inner += _arb_rational(amplitude) * cross_kernel
        cross_kernel_records.append(
            {
                "ten_mode_column": mode,
                "kernel_with_rank_eleven_outward": _interval_record(cross_kernel),
            }
        )
    linear_increment = 2 * _arb_rational(rank_eleven_amplitude) * inner
    quadratic_increment = _arb_rational(rank_eleven_amplitude**2)
    signed_squared_increment = linear_increment + quadratic_increment
    if not signed_squared_increment < 0:
        raise ArithmeticError("direct rank-11 squared increment is not negative")
    direct_new_squared = old_squared + signed_squared_increment
    if not direct_new_squared.overlaps(new_squared):
        raise ArithmeticError("direct and full rank-11 square evaluations disagree")
    direct_decrement = -signed_squared_increment
    if _lower_exact(direct_decrement) <= 0:
        raise ArithmeticError("direct rank-11 decrement is not interval-separated")
    return {
        "old_mode_count": 10,
        "new_mode_count": 11,
        "rank_eleven_mode": rank_eleven_mode,
        "rank_eleven_normalized_amplitude_exact": _fraction_text(
            rank_eleven_amplitude
        ),
        "target_5_kernel_with_rank_eleven_outward": _interval_record(
            target_cross_kernel
        ),
        "ten_mode_cross_kernel_records": cross_kernel_records,
        "old_residual_inner_product_with_rank_eleven_column_outward": (
            _interval_record(inner)
        ),
        "linear_squared_increment_outward": _interval_record(linear_increment),
        "quadratic_squared_increment_exact": _fraction_text(
            rank_eleven_amplitude**2
        ),
        "signed_squared_increment_outward": _interval_record(
            signed_squared_increment
        ),
        "direct_squared_decrement_outward": _interval_record(direct_decrement),
        "direct_squared_decrement_lower_exact": _fraction_text(
            _lower_exact(direct_decrement)
        ),
        "direct_update_identity": (
            "||Delta_10+L_11*c_k11||^2-||Delta_10||^2="
            "2*L_11*<Delta_10,c_k11>_R+L_11^2"
        ),
        "direct_update_overlaps_independent_full_eleven_mode_evaluation": True,
        "squared_distance_gap_lower_exact": _fraction_text(squared_gap_lower),
        "critical_radius_gap_lower_exact": _fraction_text(radius_gap_lower),
        "new_squared_distance_strictly_smaller": True,
        "new_critical_radius_strictly_smaller": True,
        "comparison_uses_disjoint_512_bit_arb_intervals": True,
    }


def _c7_profile(old_state: dict[str, object]) -> dict[str, object]:
    modes = old_state["modes"]
    amplitudes = old_state["amplitudes"]
    response_squared = old_state["response_squared"]
    old_radius = old_state["radius"]
    assert isinstance(modes, tuple) and isinstance(amplitudes, tuple)
    assert isinstance(response_squared, arb) and isinstance(old_radius, arb)

    inner = _arb_rational(Fraction(1, TARGET**SIGMA)) * _kernel(
        TARGET, PROFILE_COORDINATE
    )
    for mode, amplitude in zip(modes, amplitudes):
        inner += _arb_rational(amplitude) * _kernel(mode, PROFILE_COORDINATE)
    if not inner < 0:
        raise ArithmeticError("old residual/c_7 inner product is not strictly negative")
    if _kernel(PROFILE_COORDINATE, PROFILE_COORDINATE) != 1:
        raise ArithmeticError("the c_7 column is not exactly normalized")

    # For Delta + h_7 c_7/7^2, the exact one-variable minimizer is
    # h_7^*=-7^2<Delta,c_7> and the response coefficient is -<Delta,c_7>.
    optimal_response_coefficient = -inner
    optimal_prefix_coefficient = -(PROFILE_COORDINATE**SIGMA) * inner
    profiled_squared = response_squared - inner * inner
    if not profiled_squared > 0:
        raise ArithmeticError("profiled response square is not positive")
    profiled_radius = profiled_squared.sqrt() / 2
    squared_drop = response_squared - profiled_squared
    radius_drop = old_radius - profiled_radius
    if not squared_drop > 0 or not radius_drop > 0:
        raise ArithmeticError("c_7 profiling did not strictly improve the residual")
    if not _upper_exact(abs(optimal_prefix_coefficient)) < 1:
        raise ArithmeticError("profiled c_7 coefficient left the local unit cube")
    return {
        "profile_coordinate": PROFILE_COORDINATE,
        "tail_held_fixed": True,
        "profiled_prefix_class": "continuous real nonquery prefix nuisance",
        "unit_column_norm_squared_exact": "1/1",
        "residual_pairing_definition": "h_7=<Delta_10,c_7>_R",
        "residual_pairing_h7_outward": _interval_record(inner),
        "inner_product_strictly_negative": True,
        "optimal_real_nuisance_response": "w=-h_7*c_7",
        "optimal_real_nuisance_response_coefficient_outward": _interval_record(
            optimal_response_coefficient
        ),
        "corresponding_original_prefix_p7_outward": _interval_record(
            optimal_prefix_coefficient
        ),
        "profile_identity": (
            "min_h ||Delta+(h/49)c_7||^2="
            "||Delta||^2-<Delta,c_7>_R^2"
        ),
        "profiled_response_squared_outward": _interval_record(profiled_squared),
        "profiled_critical_radius_outward": _interval_record(profiled_radius),
        "squared_distance_drop_outward": _interval_record(squared_drop),
        "critical_radius_drop_outward": _interval_record(radius_drop),
        "squared_distance_drop_lower_exact": _fraction_text(_lower_exact(squared_drop)),
        "critical_radius_drop_lower_exact": _fraction_text(_lower_exact(radius_drop)),
        "old_ten_mode_point_not_quotient_stationary": True,
        "legal_integer_prefix_improvement_claimed": False,
        "exact_quotient_optimizer_claimed": False,
    }


def _extract_ao9_exact_inputs(ao9_artifact: dict[str, object]) -> dict[str, object]:
    payload = ao9_artifact.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("AO-IX payload is missing")
    consequences = payload.get("observability_consequences")
    if not isinstance(consequences, dict):
        raise ValueError("AO-IX consequence section is missing")
    records = consequences.get("coordinate_records")
    if not isinstance(records, list) or len(records) != MAXIMUM_NORM:
        raise ValueError("AO-IX coordinate vector is malformed")
    if [record.get("coordinate") for record in records] != list(
        range(1, MAXIMUM_NORM + 1)
    ):
        raise ValueError("AO-IX coordinates are not canonical")
    row_bounds = tuple(
        _parse_fraction_limited(record.get("gram_row_upper_exact"))
        for record in records
    )
    complete = {
        int(record["coordinate"]): _parse_fraction_limited(
            record.get("complete_correlation_upper_exact")
        )
        for record in records
    }
    q = max(row_bounds)
    q5 = row_bounds[TARGET - 1]
    tau_w = max(complete[n] for n in NONQUERY_COORDINATES)
    tau_w_maximizers = [n for n in NONQUERY_COORDINATES if complete[n] == tau_w]
    if _parse_fraction_limited(consequences.get("global_gram_row_upper_exact")) != q:
        raise ValueError("AO-IX global Gram bound does not recompute")
    prefix = consequences.get("prefix_reduction")
    if not isinstance(prefix, dict):
        raise ValueError("AO-IX prefix reduction is missing")
    quotient = prefix.get("uniform_quotient_bound")
    if not isinstance(quotient, dict):
        raise ValueError("AO-IX quotient lower is missing")
    if _parse_fraction_limited(
        quotient.get("row_5_off_diagonal_l1_upper_exact")
    ) != q5:
        raise ValueError("AO-IX q_5 does not recompute")
    if _parse_fraction_limited(
        quotient.get("nonquery_support_maximum_upper_exact")
    ) != tau_w:
        raise ValueError("AO-IX tau_W does not recompute")
    if quotient.get("nonquery_support_maximizers") != tau_w_maximizers:
        raise ValueError("AO-IX tau_W maximizer set does not recompute")
    lower_distance_squared = _parse_fraction_limited(
        quotient.get("quotient_distance_squared_lower_exact")
    )
    lower_radius_squared = _parse_fraction_limited(
        quotient.get("four_anchor_critical_radius_squared_lower_exact")
    )
    if lower_distance_squared != 4 * lower_radius_squared:
        raise ValueError("AO-IX distance/radius lower bounds are inconsistent")
    return {
        "q": q,
        "q5": q5,
        "tau_w": tau_w,
        "tau_w_maximizers": tau_w_maximizers,
        "lower_distance_squared": lower_distance_squared,
        "lower_radius_squared": lower_radius_squared,
        "old_alias_distance_squared_upper": _parse_fraction_limited(
            prefix.get("comparison_upper_squared_exact")
        ),
    }


def _prefix_localization(exact: dict[str, object]) -> dict[str, object]:
    q = exact["q"]
    q5 = exact["q5"]
    tau_w = exact["tau_w"]
    assert isinstance(q, Fraction) and isinstance(q5, Fraction)
    assert isinstance(tau_w, Fraction)
    scaled_bound = (tau_w + q5 / TARGET**SIGMA) / (1 - q)
    prefix_bound = MAXIMUM_NORM**SIGMA * scaled_bound
    if prefix_bound != EXPECTED_PREFIX_BOUND or not prefix_bound < 1:
        raise ArithmeticError("the frozen prefix-localization inequality changed")
    return {
        "real_nonquery_coordinates": list(NONQUERY_COORDINATES),
        "gram_row_defect_q_G_upper_exact": _fraction_text(q),
        "row_5_off_diagonal_l1_upper_exact": _fraction_text(q5),
        "nonquery_support_maximum_upper_exact": _fraction_text(tau_w),
        "nonquery_support_maximizers": exact["tau_w_maximizers"],
        "normalized_nuisance_coefficient_linf_upper_exact": _fraction_text(
            scaled_bound
        ),
        "original_prefix_coefficient_linf_upper_exact": _fraction_text(
            prefix_bound
        ),
        "original_prefix_bound_formula": (
            "P_max=2500*L_W=2500*(tau_W+q_5/25)/(1-q_G)"
        ),
        "original_prefix_bound_strictly_below_one": True,
        "fixed_tail_projection_formula": (
            "alpha(z)=-B^{-1}*C_W^T*(q-z), with p_j=j^2*alpha_j"
        ),
        "normal_equation": "B*alpha=C_W^T*z-g/25",
        "inverse_rule": "||B^{-1}||_infinity<=1/(1-q_G)",
        "scope": (
            "for each legal continuous tail point z, this bounds the unique "
            "unconstrained real W-projection coefficients; it does not round "
            "them to an exact integral optimizer"
        ),
    }


def _symbolic_zero_geometry() -> dict[str, object]:
    components = tuple((time, count) for time, count, _ in ao8.COMPONENTS)
    expected = ((510, 2550), (1780, 8900))
    if components != expected:
        raise ValueError("pinned time components changed")
    records = []
    all_numerators: set[int] = set()
    for observation_time, sample_count in components:
        if sample_count % 2 or Fraction(observation_time, sample_count) != Fraction(1, 5):
            raise ArithmeticError("sample lattice no longer has even count and spacing 1/5")
        numerators = tuple(2 * index + 1 - sample_count for index in range(sample_count))
        if any(value % 2 == 0 for value in numerators):
            raise ArithmeticError("sample lattice contains an even tenth-grid numerator")
        all_numerators.update(numerators)
        records.append(
            {
                "observation_time": observation_time,
                "sample_count": sample_count,
                "sample_spacing_exact": "1/5",
                "time_formula": "t_j=(2*j+1-m)/10",
                "minimum_time_numerator_over_ten": numerators[0],
                "maximum_time_numerator_over_ten": numerators[-1],
                "numerator_step": 2,
                "all_time_numerators_odd": True,
            }
        )
    expected_lattice = set(range(-EFFECTIVE_TRIGONOMETRIC_DEGREE, EFFECTIVE_TRIGONOMETRIC_DEGREE + 1, 2))
    if all_numerators != expected_lattice:
        raise ArithmeticError("effective time lattice is not the full pinned odd grid")
    return {
        "time_components": records,
        "effective_time_lattice": "{r/10: r odd, -8899<=r<=8899}",
        "reduced_phase": "theta=x/10",
        "full_trigonometric_period_in_x": "20*pi",
        "antiperiod_and_absolute_half_period_in_x": "10*pi",
        "exact_antiperiod_rule": "F(x+10*pi)=-F(x)",
        "trigonometric_degree_upper": EFFECTIVE_TRIGONOMETRIC_DEGREE,
        "nonzero_response_zero_phases_modulo_20pi_upper": (
            2 * EFFECTIVE_TRIGONOMETRIC_DEGREE
        ),
        "nonzero_response_zero_phase_classes_modulo_10pi_upper": (
            EFFECTIVE_TRIGONOMETRIC_DEGREE
        ),
        "exceptional_arithmetic_indices_upper": EFFECTIVE_TRIGONOMETRIC_DEGREE,
        "symbolic_reduction": (
            "after multiplication by exp(i*8899*theta), the odd-frequency "
            "Laurent response is a polynomial of degree at most 8899 in "
            "y=exp(2*i*theta)"
        ),
        "arithmetic_phase_injectivity": (
            "if log(k)-log(l)=10*pi*m for positive integers k,l and integer "
            "m, then m=0: for m nonzero, exp(10*pi*m)=(-1)^(-10*m*i) "
            "is transcendental by Gelfond-Schneider and cannot equal k/l"
        ),
        "arithmetic_phase_map": "positive integer k maps to log(k) modulo 10*pi",
        "zero_bound_hypothesis": "the response trigonometric polynomial is not identically zero",
        "identically_zero_case_excluded_from_finite_zero_bound": True,
        "exceptional_indices_effectively_bounded": False,
        "effectivity_caveat": (
            "the qualitative Gelfond-Schneider injectivity and zero count "
            "bound the number of exceptional indices, not their sizes"
        ),
        "numeric_root_search_used": False,
        "formal_role": (
            "exact symbolic degree/zero-count metadata; the executable does "
            "not treat numerical phase samples as a proof of this theorem"
        ),
    }


def _bracket_and_projection_localization(
    exact: dict[str, object], new_state: dict[str, object]
) -> dict[str, object]:
    lower_distance_squared = exact["lower_distance_squared"]
    lower_radius_squared = exact["lower_radius_squared"]
    new_squared = new_state["response_squared"]
    new_radius = new_state["radius"]
    assert isinstance(lower_distance_squared, Fraction)
    assert isinstance(lower_radius_squared, Fraction)
    assert isinstance(new_squared, arb) and isinstance(new_radius, arb)
    upper_distance_squared = _upper_exact(new_squared)
    upper_radius_squared = upper_distance_squared / 4
    upper_radius = _upper_exact(new_radius)
    if not lower_distance_squared < upper_distance_squared:
        raise ArithmeticError("updated lower/upper distance bracket is empty")
    if not lower_radius_squared < upper_radius_squared:
        raise ArithmeticError("updated lower/upper radius bracket is empty")
    localization_squared = upper_distance_squared - lower_distance_squared
    old_alias_upper = exact["old_alias_distance_squared_upper"]
    assert isinstance(old_alias_upper, Fraction)
    if not upper_distance_squared < old_alias_upper:
        raise ArithmeticError("rank-11 upper does not improve the pinned AO-IX upper")
    return {
        "lower_source": "pinned AO-IX inverse-free uniform quotient lower",
        "upper_source": "eleven-mode integral target-5 endpoint witness",
        "quotient_distance_squared_lower_exact": _fraction_text(
            lower_distance_squared
        ),
        "integral_witness_distance_squared_upper_exact": _fraction_text(
            upper_distance_squared
        ),
        "critical_radius_squared_lower_exact": _fraction_text(lower_radius_squared),
        "critical_radius_squared_upper_exact": _fraction_text(upper_radius_squared),
        "critical_radius_lower_outward": _sqrt_interval_record(lower_radius_squared),
        "critical_radius_upper_exact": _fraction_text(upper_radius),
        "old_ao9_integral_witness_distance_squared_upper_exact": _fraction_text(
            old_alias_upper
        ),
        "new_integral_upper_strictly_improves_ao9": True,
        "applies_as_bracket_to_continuous_box_radius": True,
        "applies_as_bracket_to_integral_envelope_radius": True,
        "continuous_and_integral_values_claimed_equal": False,
        "arithmetic_defect_geometry": {
            "model_scope": "independent integral coefficient-envelope responses S_Z",
            "convex_projection": "x_star=P_conv(S_Z)(q)",
            "quotient_distance": "d=||q-x_star||",
            "arithmetic_defect": "eta_arith=dist(x_star,S_Z)",
            "two_sided_inequality": (
                "sqrt(d^2+eta_arith^2)<=dist(q,S_Z)<=d+eta_arith"
            ),
            "integral_equals_convex_distance_iff": "eta_arith=0",
            "arithmetic_defect_exact_value_computed": False,
        },
        "current_convex_projection_localization": {
            "convex_set": (
                "conv(S_Z), equal to the bounded continuous independent-"
                "coefficient-envelope nuisance response set"
            ),
            "target": "q=A*e_5",
            "explicit_alias_response": (
                "s=negative of the eleven-mode tail response, with nonquery "
                "prefix coefficient zero; s belongs to S_Z"
            ),
            "metric_projection": "x_star=P_conv(S_Z)(q)",
            "pythagorean_inequality": (
                "||s-x_star||^2<=||q-s||^2-dist(q,conv(S_Z))^2"
            ),
            "convex_projection_to_alias_distance_squared_upper_exact": _fraction_text(
                localization_squared
            ),
            "convex_projection_to_alias_distance_upper_outward": _sqrt_interval_record(
                localization_squared
            ),
            "coefficientwise_optimizer_identified": False,
            "integral_optimizer_identified": False,
        },
    }


def _validate_inheritance(
    ao8_artifact: dict[str, object],
    old_record: dict[str, object],
    old_state: dict[str, object],
) -> None:
    if tuple(ao8.ALIAS_MODES_5) != TEN_MODE_FACTORIZATIONS:
        raise ValueError("AO-VIII frozen ten-mode tuple changed")
    payload = ao8_artifact.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("AO-VIII payload is missing")
    witnesses = payload.get("integral_alias_witnesses")
    if not isinstance(witnesses, list) or len(witnesses) != 2:
        raise ValueError("AO-VIII witness list is malformed")
    inherited = witnesses[0]
    if not isinstance(inherited, dict) or inherited.get("target_coordinate") != TARGET:
        raise ValueError("AO-VIII target-5 witness is missing")
    if inherited.get("mode_count") != 10 or old_record.get("mode_count") != 10:
        raise ValueError("AO-VIII ten-mode witness count changed")
    inherited_modes = [row.get("mode") for row in inherited.get("mode_records", [])]
    if inherited_modes != [mode for mode, _ in TEN_MODE_FACTORIZATIONS]:
        raise ValueError("AO-VIII ten-mode witness sequence changed")
    response_squared = old_state["response_squared"]
    radius = old_state["radius"]
    assert isinstance(response_squared, arb) and isinstance(radius, arb)
    if _parse_fraction_limited(
        inherited.get("response_squared_lower_exact")
    ) != _lower_exact(response_squared):
        raise ValueError("AO-VIII ten-mode squared lower endpoint changed")
    if _parse_fraction_limited(
        inherited.get("response_squared_upper_exact")
    ) != _upper_exact(response_squared):
        raise ValueError("AO-VIII ten-mode squared upper endpoint changed")
    if _parse_fraction_limited(
        inherited.get("robust_radius_upper_exact")
    ) != _upper_exact(radius):
        raise ValueError("AO-VIII ten-mode radius upper endpoint changed")


def build_payload() -> dict[str, object]:
    _check_environment()
    with ctx.workprec(FORMAL_PRECISION_BITS):
        ao8_artifact, ao9_artifact = _load_and_validate_dependencies()
        exact = _extract_ao9_exact_inputs(ao9_artifact)
        old_record, old_state = _compute_witness(TEN_MODE_FACTORIZATIONS)
        new_record, new_state = _compute_witness(ELEVEN_MODE_FACTORIZATIONS)
        _validate_inheritance(ao8_artifact, old_record, old_state)
        rank_eleven = new_record["mode_records"][-1]
        if (
            rank_eleven["d14"] != EXPECTED_RANK_ELEVEN_D14
            or _parse_fraction_limited(rank_eleven["normalized_amplitude_exact"])
            != EXPECTED_RANK_ELEVEN_AMPLITUDE
        ):
            raise ArithmeticError("rank-11 arithmetic endpoint changed")
        improvement = _strict_rank_eleven_improvement(old_state, new_state)
        profile = _c7_profile(old_state)
        prefix = _prefix_localization(exact)
        zero_geometry = _symbolic_zero_geometry()
        bracket = _bracket_and_projection_localization(exact, new_state)
    return {
        "scope": {
            "formal_tail_model": (
                "degree-fourteen independent coefficient envelope; its integral "
                "tail set is a compact integer-selection image, not asserted "
                "to be a discrete subset of observation space"
            ),
            "integral_upper_witness": True,
            "continuous_lower_relaxation": True,
            "exact_optimizer_identified": False,
            "continuous_integral_equality_claimed": False,
            "number_field_realization_claimed": False,
            "coarse_numerical_optimizer_included": False,
            "rank_label_status": (
                "rank 11 is frozen nonformal discovery provenance; all arithmetic "
                "and inequalities used after selection are formally reconstructed"
            ),
            "symbolic_zero_theorem_numerically_inferred": False,
        },
        "parameters": {
            "degree": DEGREE,
            "maximum_norm": MAXIMUM_NORM,
            "sigma": SIGMA,
            "target_coordinate": TARGET,
            "formal_precision_bits": FORMAL_PRECISION_BITS,
            "first_alias_angular_frequency": "10*pi",
        },
        "dependencies": _dependency_hashes(),
        "fixed_tail_prefix_projection": prefix,
        "symbolic_zero_geometry": zero_geometry,
        "ten_mode_witness": old_record,
        "eleven_mode_witness": new_record,
        "rank_eleven_improvement": improvement,
        "continuous_c7_profile": profile,
        "updated_bracket_and_arithmetic_defect_geometry": bracket,
        "formal_consequences": {
            "prefix_projection_lies_in_open_unit_cube": True,
            "unbounded_quotient_equals_bounded_continuous_prefix_distance": True,
            "unbounded_quotient_equals_distance_to_convex_hull_of_independent_integral_envelope_responses": True,
            "integral_attainment_at_quotient_forces_zero_nonquery_prefix": True,
            "rank_eleven_integral_endpoint_strictly_improves_ten_modes": True,
            "ten_mode_point_is_not_stationary_in_real_c7_direction": True,
            "updated_global_radius_bracket_certified": True,
            "convex_metric_projection_localized_in_observation_space": True,
            "exact_closest_fibre_value_determined": False,
        },
        "passed": True,
    }


def artifact_document(payload: dict[str, object]) -> dict[str, object]:
    digest = _sha256(payload)
    if PINNED_PAYLOAD_SHA256 != "TO_BE_PINNED" and digest != PINNED_PAYLOAD_SHA256:
        raise ValueError("rebuilt payload differs from the pinned theorem")
    return {
        "schema": SCHEMA,
        "producer": {
            "python_flint": PINNED_PYTHON_FLINT_VERSION,
            "flint": PINNED_FLINT_VERSION,
            "flint_threads": 1,
            "arb_precision_bits": FORMAL_PRECISION_BITS,
        },
        "payload_sha256": digest,
        "payload": payload,
        "reproduction_files": {
            "verifier_basename": VERIFIER_PATH.name,
            "verifier_sha256": _sha256_file(VERIFIER_PATH),
            "tests_basename": TESTS_PATH.name,
            "tests_sha256": _sha256_file(TESTS_PATH),
        },
    }


def load_artifact(
    path: Path = DEFAULT_ARTIFACT_PATH,
) -> tuple[dict[str, object], bytes]:
    artifact, raw = _load_json_strict(path, MAX_ARTIFACT_BYTES)
    if raw != _pretty_json(artifact):
        raise ValueError("artifact is not canonical deterministic JSON")
    return artifact, raw


def verify_artifact(artifact: dict[str, object]) -> dict[str, object]:
    _check_environment()
    if set(artifact) != {
        "schema", "producer", "payload_sha256", "payload", "reproduction_files"
    }:
        raise ValueError("artifact top-level structure is invalid")
    if artifact.get("schema") != SCHEMA:
        raise ValueError("artifact schema mismatch")
    expected_producer = {
        "python_flint": PINNED_PYTHON_FLINT_VERSION,
        "flint": PINNED_FLINT_VERSION,
        "flint_threads": 1,
        "arb_precision_bits": FORMAL_PRECISION_BITS,
    }
    if _canonical_json(artifact.get("producer")) != _canonical_json(expected_producer):
        raise ValueError("artifact producer environment mismatch")
    payload = artifact.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("artifact payload is missing")
    digest = _sha256(payload)
    if artifact.get("payload_sha256") != digest:
        raise ValueError("artifact payload digest mismatch")
    if PINNED_PAYLOAD_SHA256 == "TO_BE_PINNED" or digest != PINNED_PAYLOAD_SHA256:
        raise ValueError("artifact payload is not the pinned theorem")
    expected_reproduction = {
        "verifier_basename": VERIFIER_PATH.name,
        "verifier_sha256": _sha256_file(VERIFIER_PATH),
        "tests_basename": TESTS_PATH.name,
        "tests_sha256": _sha256_file(TESTS_PATH),
    }
    if artifact.get("reproduction_files") != expected_reproduction:
        raise ValueError("artifact reproduction-file hashes changed")
    expected_payload = build_payload()
    # Canonical comparison avoids Python's True == 1 alias.
    if _canonical_json(payload) != _canonical_json(expected_payload):
        raise ValueError("artifact payload does not match formal reconstruction")
    return {
        "schema": SCHEMA,
        "payload_sha256": digest,
        "full_reconstruction": True,
        "passed": True,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=DEFAULT_ARTIFACT_PATH)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--write", type=Path)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    if arguments.emit or arguments.write is not None:
        artifact = artifact_document(build_payload())
        serialized = _pretty_json(artifact)
        if arguments.write is not None:
            arguments.write.parent.mkdir(parents=True, exist_ok=True)
            arguments.write.write_bytes(serialized)
            print(
                json.dumps(
                    {
                        "written": str(arguments.write),
                        "payload_sha256": artifact["payload_sha256"],
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
        else:
            print(serialized.decode("utf-8"), end="")
        return
    artifact, _ = load_artifact(arguments.certificate)
    print(json.dumps(verify_artifact(artifact), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
