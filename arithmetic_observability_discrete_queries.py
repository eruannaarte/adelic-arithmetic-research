#!/usr/bin/env python3
"""Strict AO-VII certificate for integer queries and continuous tail failure.

The first half of this executable artifact consumes the pinned Arithmetic
Sensing V multiscale certificate.  It reconstructs, using exact rational
arithmetic, the localized Neumann coefficient bounds

    B_n = n^2 (tau_n + q_n tau/(1-q))

and the corresponding sufficient observation-noise radii for the arithmetic
query coordinates n in {1, 2, 3, 5}.

The second half is independent of that large source computation.  At the
canonical three-reading schedule from Arithmetic Observability V it evaluates
an explicit six-column continuous d_14-tail response matrix in 384-bit Arb.
Sylvester's criterion proves W W^T > 25 I.  The same calculation encloses the
unique six-mode correction for a frozen pair of distinct product vertices and
proves that every normalized correction coordinate has absolute value below
1/3.  Thus the finite artifact certifies the numerical inputs to both the
integer-query stability theorem and the continuous-relaxation obstruction.

The general Neumann, zonotope, and exact-collision deductions are manuscript
mathematics.  This artifact certifies their frozen exact and transcendental
inputs; it does not claim to mechanize those general theorems.
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
from flint import arb, arb_mat, ctx, fmpq


SCHEMA = "arithmetic-observability-discrete-queries-v1"
EXPECTED_SOURCE_SCHEMA = "arithmetic-sensing-v-time-ensemble-v1"
EXPECTED_SOURCE_BASENAME = "arithmetic_sensing_v_multiscale_end_to_end.json"
EXPECTED_SOURCE_FILE_SHA256 = (
    "ad03df9d6325512074e6940602c1c888c81abd057a5856d6212f93dc8e780517"
)
EXPECTED_SOURCE_FORMAL_SHA256 = (
    "89b316584d9179c13232ad99b9515067fdf67329e6df3db4c48220d6b8c3ff7b"
)

FORMAL_PRECISION_BITS = 384
MIN_PRECISION_BITS = 256
MAX_PRECISION_BITS = 1024
PINNED_PYTHON_FLINT_VERSION = "0.9.0"
PINNED_FLINT_VERSION = "3.6.0"

MAX_ARTIFACT_BYTES = 240_000
MAX_SOURCE_BYTES = 64_000
MAX_CONTAINER_ITEMS = 512
MAX_JSON_DEPTH = 24
MAX_TEXT_FIELD_LENGTH = 8192
MAX_INTEGER_BITS = 4096
INTERVAL_DISPLAY_DIGITS = 100

SOURCE_DEGREE = 14
SOURCE_MAXIMUM_NORM = 50
SOURCE_SIGMA = 2
SOURCE_DISTINCT_SAMPLE_COUNT = 8900
SOURCE_OUTPUT_SCALE_BITS = 128
ANCHORS = (1, 2, 3, 5)
ALL_COORDINATE_GAIN_FLOOR = 24_989
ALL_COORDINATE_GAIN_CEILING = 24_990
SCHUR_GAIN_FLOOR = 24_998
SCHUR_GAIN_CEILING = 24_999

# Arithmetic Observability V, Section 6.
TIMES = (
    Fraction(245_943, 1000),
    Fraction(281_062, 1000),
    Fraction(960_832, 1000),
)
TAIL_MODES = (64, 144, 168, 240, 768, 2880)
TAIL_WEIGHTS = (
    Fraction(6783, 1024),
    Fraction(20825, 1728),
    Fraction(35, 9),
    Fraction(5831, 720),
    Fraction(79135, 16384),
    Fraction(110789, 23040),
)
PRIME_BOX_PRIMES = (2, 3, 5)
PRIME_BOX_MAX_EXPONENT = 3
CORE_VERTEX_NORMS = (1, 27_000)
SINGULAR_VALUE_FLOOR = Fraction(5)
COLLISION_COORDINATE_BOUND = Fraction(1, 3)
CORE_DIAMETER_RATIONAL_UPPER = Fraction(7, 2)

PACKAGE_ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE_PATH = (
    PACKAGE_ROOT / "certificates" / EXPECTED_SOURCE_BASENAME
)
VERIFIER_PATH = PACKAGE_ROOT / "arithmetic_observability_discrete_queries.py"
TESTS_PATH = PACKAGE_ROOT / "test_arithmetic_observability_discrete_queries.py"


def _fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def _parse_fraction_limited(text: object) -> Fraction:
    if not isinstance(text, str) or len(text) > 4096 or text.count("/") != 1:
        raise ValueError("fraction is not a bounded canonical string")
    numerator_text, denominator_text = text.split("/", 1)
    try:
        value = Fraction(int(numerator_text), int(denominator_text))
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError("fraction string is malformed") from exc
    if (
        value.numerator.bit_length() > MAX_INTEGER_BITS
        or value.denominator.bit_length() > MAX_INTEGER_BITS
    ):
        raise ValueError("fraction exceeds the formal integer limit")
    if _fraction_text(value) != text:
        raise ValueError("fraction string is not reduced and canonical")
    return value


def _arb_rational(value: Fraction | int) -> arb:
    value = Fraction(value)
    return arb(fmpq(value.numerator, value.denominator))


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def _pretty_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _interval_text(value: arb, digits: int = INTERVAL_DISPLAY_DIGITS) -> str:
    return value.str(digits, radius=True, more=True)


def _exact_dyadic_fraction(value: arb) -> Fraction:
    if not value.is_exact():
        raise ValueError("expected an exact Arb endpoint")
    mantissa, exponent = map(int, value.man_exp())
    if exponent >= 0:
        return Fraction(mantissa * 2**exponent)
    return Fraction(mantissa, 2 ** (-exponent))


def _lower_exact(value: arb) -> Fraction:
    return _exact_dyadic_fraction(value.lower())


def _upper_exact(value: arb) -> Fraction:
    return _exact_dyadic_fraction(value.upper())


def _upper_abs_exact(value: arb) -> Fraction:
    return _upper_exact(abs(value))


def _check_environment() -> None:
    if flint.__version__ != PINNED_PYTHON_FLINT_VERSION:
        raise RuntimeError(
            "python-flint environment mismatch: expected "
            f"{PINNED_PYTHON_FLINT_VERSION}, got {flint.__version__}"
        )
    if flint.__FLINT_VERSION__ != PINNED_FLINT_VERSION:
        raise RuntimeError(
            "FLINT environment mismatch: expected "
            f"{PINNED_FLINT_VERSION}, got {flint.__FLINT_VERSION__}"
        )


def _reject_constant(_: str) -> object:
    raise ValueError("JSON contains a forbidden nonfinite constant")


def _parse_json_integer(text: str) -> int:
    if text == "-0":
        raise ValueError("negative-zero JSON integer is noncanonical")
    value = int(text)
    if value.bit_length() > MAX_INTEGER_BITS:
        raise ValueError("JSON integer exceeds the formal size limit")
    return value


def _object_without_duplicates(
    pairs: Sequence[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON contains a duplicate key")
        result[key] = value
    return result


def _read_source(source_path: Path) -> tuple[dict[str, object], bytes]:
    with source_path.open("rb") as handle:
        raw = handle.read(MAX_SOURCE_BYTES + 1)
    if len(raw) > MAX_SOURCE_BYTES:
        raise ValueError("source certificate exceeds the byte resource cap")
    if _sha256_bytes(raw) != EXPECTED_SOURCE_FILE_SHA256:
        raise ValueError("source certificate file digest mismatch")
    try:
        source = json.loads(
            raw.decode("utf-8", errors="strict"),
            parse_int=_parse_json_integer,
            parse_constant=_reject_constant,
            object_pairs_hook=_object_without_duplicates,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("source certificate is malformed") from exc
    if not isinstance(source, dict):
        raise ValueError("source certificate root must be an object")
    return source, raw


def _require_int(value: object, expected: int, label: str) -> int:
    if type(value) is not int or value != expected:
        raise ValueError(f"source uses unexpected {label}")
    return value


def _require_bool(value: object, expected: bool, label: str) -> bool:
    if type(value) is not bool or value is not expected:
        raise ValueError(f"source uses unexpected {label}")
    return value


def _source_exact_inputs(source_path: Path) -> dict[str, object]:
    source, raw = _read_source(source_path)
    if source.get("schema") != EXPECTED_SOURCE_SCHEMA:
        raise ValueError("source certificate schema mismatch")
    if source.get("formal_certificate_sha256") != EXPECTED_SOURCE_FORMAL_SHA256:
        raise ValueError("source formal-certificate digest mismatch")
    certificate = source.get("certificate")
    if not isinstance(certificate, dict):
        raise ValueError("source certificate payload is missing")
    if _sha256(certificate) != EXPECTED_SOURCE_FORMAL_SHA256:
        raise ValueError("source formal-certificate content digest mismatch")

    parameters = certificate.get("parameters")
    finite = certificate.get("finite")
    remote = certificate.get("combined_remote")
    gram = certificate.get("gram")
    consequence = certificate.get("consequence")
    if not all(
        isinstance(section, dict)
        for section in (parameters, finite, remote, gram, consequence)
    ):
        raise ValueError("source exact-input sections are malformed")
    assert isinstance(parameters, dict)
    assert isinstance(finite, dict)
    assert isinstance(remote, dict)
    assert isinstance(gram, dict)
    assert isinstance(consequence, dict)

    _require_int(parameters.get("degree"), SOURCE_DEGREE, "degree")
    _require_int(
        parameters.get("maximum_norm"), SOURCE_MAXIMUM_NORM, "maximum norm"
    )
    _require_int(parameters.get("sigma"), SOURCE_SIGMA, "sigma")
    _require_int(
        parameters.get("distinct_sample_count"),
        SOURCE_DISTINCT_SAMPLE_COUNT,
        "distinct sample count",
    )
    _require_int(
        parameters.get("output_scale_bits"),
        SOURCE_OUTPUT_SCALE_BITS,
        "output scale",
    )
    _require_int(
        finite.get("output_scale_bits"),
        SOURCE_OUTPUT_SCALE_BITS,
        "finite output scale",
    )
    _require_int(
        remote.get("output_scale_bits"),
        SOURCE_OUTPUT_SCALE_BITS,
        "remote output scale",
    )
    _require_int(
        gram.get("output_scale_bits"),
        SOURCE_OUTPUT_SCALE_BITS,
        "Gram output scale",
    )
    _require_bool(
        consequence.get("integer_rounding_certificate"),
        True,
        "integer-rounding flag",
    )

    denominator = 2**SOURCE_OUTPUT_SCALE_BITS

    def numerator_vector(section: dict[str, object], label: str) -> tuple[int, ...]:
        values = section.get("target_numerators")
        if not isinstance(values, list) or len(values) != SOURCE_MAXIMUM_NORM:
            raise ValueError(f"source {label} vector is malformed")
        parsed: list[int] = []
        for value in values:
            if not isinstance(value, str) or not value.isascii() or not value.isdigit():
                raise ValueError(f"source {label} numerator is noncanonical")
            integer = int(value)
            if integer.bit_length() > MAX_INTEGER_BITS:
                raise ValueError(f"source {label} numerator is too large")
            if str(integer) != value:
                raise ValueError(f"source {label} numerator is noncanonical")
            parsed.append(integer)
        return tuple(parsed)

    finite_numerators = numerator_vector(finite, "finite-tail")
    remote_numerators = numerator_vector(remote, "remote-tail")
    row_values = gram.get("row_numerators")
    if not isinstance(row_values, list) or len(row_values) != SOURCE_MAXIMUM_NORM:
        raise ValueError("source Gram-row vector is malformed")
    row_numerators: list[int] = []
    for value in row_values:
        if not isinstance(value, str) or not value.isascii() or not value.isdigit():
            raise ValueError("source Gram-row numerator is noncanonical")
        integer = int(value)
        if str(integer) != value or integer.bit_length() > MAX_INTEGER_BITS:
            raise ValueError("source Gram-row numerator is noncanonical")
        row_numerators.append(integer)

    finite_bounds = tuple(Fraction(value, denominator) for value in finite_numerators)
    remote_bounds = tuple(Fraction(value, denominator) for value in remote_numerators)
    complete_bounds = tuple(
        finite_value + remote_value
        for finite_value, remote_value in zip(finite_bounds, remote_bounds)
    )
    row_bounds = tuple(Fraction(value, denominator) for value in row_numerators)
    q = Fraction(str(gram.get("maximum_row_upper")))
    tau = max(complete_bounds)
    if max(row_bounds) != q:
        raise ValueError("source maximum Gram row is inconsistent")
    if Fraction(str(consequence.get("maximum_complete_tail"))) != tau:
        raise ValueError("source maximum complete tail is inconsistent")
    global_coefficient_bound = Fraction(str(consequence.get("coefficient_bound")))
    if not (0 <= q < 1 and 0 <= tau and 0 <= global_coefficient_bound < Fraction(1, 2)):
        raise ValueError("source does not supply valid Neumann inputs")

    return {
        "source_file_sha256": _sha256_bytes(raw),
        "source_formal_sha256": EXPECTED_SOURCE_FORMAL_SHA256,
        "finite_bounds": finite_bounds,
        "remote_bounds": remote_bounds,
        "complete_bounds": complete_bounds,
        "row_bounds": row_bounds,
        "q": q,
        "tau": tau,
        "global_coefficient_bound": global_coefficient_bound,
    }


def _build_localized_neumann_section(source_path: Path) -> dict[str, object]:
    inputs = _source_exact_inputs(source_path)
    complete_bounds = inputs["complete_bounds"]
    finite_bounds = inputs["finite_bounds"]
    remote_bounds = inputs["remote_bounds"]
    row_bounds = inputs["row_bounds"]
    q = inputs["q"]
    tau = inputs["tau"]
    global_coefficient_bound = inputs["global_coefficient_bound"]
    assert isinstance(complete_bounds, tuple)
    assert isinstance(finite_bounds, tuple)
    assert isinstance(remote_bounds, tuple)
    assert isinstance(row_bounds, tuple)
    assert isinstance(q, Fraction)
    assert isinstance(tau, Fraction)
    assert isinstance(global_coefficient_bound, Fraction)

    records: list[dict[str, object]] = []
    radius_squares: dict[int, Fraction] = {}
    schur_radius_squares: dict[int, Fraction] = {}
    for n in ANCHORS:
        tau_n = complete_bounds[n - 1]
        q_n = row_bounds[n - 1]
        bound = n * n * (tau_n + q_n * tau / (1 - q))
        margin = Fraction(1, 2) - bound
        radius_squared = margin * margin * (1 - q) / n**4
        schur_factor = (1 - q - q_n * q_n) / (1 - q)
        schur_numerator = 1 - q - q_n * q_n
        certified_bar_kappa_squared = n**4 * (1 - q) / schur_numerator
        schur_radius_squared = margin * margin * schur_factor / n**4
        distance_squared = 4 * radius_squared
        schur_distance_squared = 4 * schur_radius_squared
        if not (
            0 <= bound < Fraction(1, 2)
            and radius_squared > 0
            and schur_radius_squared > radius_squared
            and schur_numerator > 0
        ):
            raise ValueError("localized Neumann query has no positive margin")
        radius = _arb_rational(radius_squared).sqrt()
        distance = 2 * radius
        schur_radius = _arb_rational(schur_radius_squared).sqrt()
        schur_distance = 2 * schur_radius
        radius_squares[n] = radius_squared
        schur_radius_squares[n] = schur_radius_squared
        records.append(
            {
                "anchor": n,
                "finite_tail_upper_exact": _fraction_text(finite_bounds[n - 1]),
                "remote_tail_upper_exact": _fraction_text(remote_bounds[n - 1]),
                "complete_tail_upper_exact": _fraction_text(tau_n),
                "gram_row_upper_exact": _fraction_text(q_n),
                "localized_coefficient_bound_exact": _fraction_text(bound),
                "localized_coefficient_bound_interval": _interval_text(
                    _arb_rational(bound)
                ),
                "rounding_margin_exact": _fraction_text(margin),
                "coefficient_bound_certainly_below_one_half": bound < Fraction(1, 2),
                "sufficient_noise_radius_squared_exact": _fraction_text(
                    radius_squared
                ),
                "sufficient_noise_radius_interval": _interval_text(radius),
                "query_fibre_distance_lower_squared_exact": _fraction_text(
                    distance_squared
                ),
                "query_fibre_distance_lower_interval": _interval_text(distance),
                "schur_factor_exact": _fraction_text(schur_factor),
                "schur_numerator_exact": _fraction_text(schur_numerator),
                "schur_numerator_certainly_positive": schur_numerator > 0,
                "certified_bar_kappa_squared_exact": _fraction_text(
                    certified_bar_kappa_squared
                ),
                "schur_sufficient_noise_radius_squared_exact": _fraction_text(
                    schur_radius_squared
                ),
                "schur_sufficient_noise_radius_interval": _interval_text(
                    schur_radius
                ),
                "schur_query_fibre_distance_lower_squared_exact": _fraction_text(
                    schur_distance_squared
                ),
                "schur_query_fibre_distance_lower_interval": _interval_text(
                    schur_distance
                ),
                "anisotropic_unit_separation_weight_squared_lower_exact": (
                    _fraction_text(schur_distance_squared)
                ),
                "anisotropic_unit_separation_weight_interval": _interval_text(
                    schur_distance
                ),
                "schur_bound_strictly_improves_conservative_bound": (
                    schur_radius_squared > radius_squared
                ),
            }
        )

    bottleneck = min(ANCHORS, key=radius_squares.__getitem__)
    if bottleneck != 5 or len(set(radius_squares.values())) != len(ANCHORS):
        raise ValueError("frozen query bottleneck is not uniquely n=5")
    schur_bottleneck = min(ANCHORS, key=schur_radius_squares.__getitem__)
    if schur_bottleneck != 5 or len(set(schur_radius_squares.values())) != len(ANCHORS):
        raise ValueError("frozen Schur query bottleneck is not uniquely n=5")
    all_coordinate_radius_squared = (
        (Fraction(1, 2) - global_coefficient_bound) ** 2
        * (1 - q)
        / SOURCE_MAXIMUM_NORM ** (2 * SOURCE_SIGMA)
    )
    bottleneck_gain_squared = radius_squares[bottleneck] / all_coordinate_radius_squared
    lower_gain_passed = (
        radius_squares[bottleneck]
        > ALL_COORDINATE_GAIN_FLOOR**2 * all_coordinate_radius_squared
    )
    upper_gain_passed = (
        radius_squares[bottleneck]
        < ALL_COORDINATE_GAIN_CEILING**2 * all_coordinate_radius_squared
    )
    if not (lower_gain_passed and upper_gain_passed):
        raise ValueError("frozen localized/global gain bracket failed")
    schur_gain_squared = (
        schur_radius_squares[schur_bottleneck] / all_coordinate_radius_squared
    )
    schur_gain_lower_passed = (
        schur_radius_squares[schur_bottleneck]
        > SCHUR_GAIN_FLOOR**2 * all_coordinate_radius_squared
    )
    schur_gain_upper_passed = (
        schur_radius_squares[schur_bottleneck]
        < SCHUR_GAIN_CEILING**2 * all_coordinate_radius_squared
    )
    query_upper_radius = Fraction(1, 2 * bottleneck**SOURCE_SIGMA)
    query_upper_distance = 2 * query_upper_radius
    query_bracket_passed = (
        schur_radius_squares[schur_bottleneck] < query_upper_radius**2
    )
    if not (
        schur_gain_lower_passed
        and schur_gain_upper_passed
        and query_bracket_passed
    ):
        raise ValueError("frozen Schur gain or query upper bracket failed")

    return {
        "source": {
            "path_basename": EXPECTED_SOURCE_BASENAME,
            "schema": EXPECTED_SOURCE_SCHEMA,
            "file_sha256": inputs["source_file_sha256"],
            "formal_certificate_sha256": inputs["source_formal_sha256"],
        },
        "definitions": {
            "complete_tail": "tau_n=finite_n+remote_n",
            "global_tail": "tau=max_j tau_j",
            "global_gram_row": "q=max_j q_j",
            "localized_bound": "B_n=n^2*(tau_n+q_n*tau/(1-q))",
            "sufficient_noise_radius_squared": "eps_n^2=(1/2-B_n)^2*(1-q)/n^4",
            "schur_factor": "s_n=(1-q-q_n^2)/(1-q)",
            "schur_sufficient_noise_radius_squared": (
                "eps_n,Schur^2=(1/2-B_n)^2*s_n/n^4"
            ),
            "query_fibre_distance_lower": "2*eps_n",
            "certified_bar_kappa": (
                "bar_kappa_n^2=n^4*(1-q)/(1-q-q_n^2), with kappa_n<=bar_kappa_n"
            ),
            "anisotropic_lattice_fibre_geometry": (
                "certified gauge max_n (abs(Delta_n)-2*B_n)_+/bar_kappa_n"
            ),
        },
        "global_gram_row_upper_exact": _fraction_text(q),
        "global_complete_tail_upper_exact": _fraction_text(tau),
        "anchor_records": records,
        "unique_bottleneck_anchor": bottleneck,
        "bottleneck_radius_squared_exact": _fraction_text(radius_squares[bottleneck]),
        "unique_schur_bottleneck_anchor": schur_bottleneck,
        "schur_bottleneck_radius_squared_exact": _fraction_text(
            schur_radius_squares[schur_bottleneck]
        ),
        "all_fifty_global_coefficient_bound_exact": _fraction_text(
            global_coefficient_bound
        ),
        "all_fifty_sufficient_radius_squared_exact": _fraction_text(
            all_coordinate_radius_squared
        ),
        "localized_to_all_fifty_gain_squared_exact": _fraction_text(
            bottleneck_gain_squared
        ),
        "localized_radius_gain_strictly_above": ALL_COORDINATE_GAIN_FLOOR,
        "localized_radius_gain_strictly_below": ALL_COORDINATE_GAIN_CEILING,
        "gain_lower_inequality_verified": lower_gain_passed,
        "gain_upper_inequality_verified": upper_gain_passed,
        "schur_localized_to_all_fifty_gain_squared_exact": _fraction_text(
            schur_gain_squared
        ),
        "schur_localized_radius_gain_strictly_above": SCHUR_GAIN_FLOOR,
        "schur_localized_radius_gain_strictly_below": SCHUR_GAIN_CEILING,
        "schur_gain_lower_inequality_verified": schur_gain_lower_passed,
        "schur_gain_upper_inequality_verified": schur_gain_upper_passed,
        "query_upper_obstruction": {
            "anchor": bottleneck,
            "model": (
                "the full AS-V coefficient-envelope prefix class, not the smaller "
                "multiplicative product-core family"
            ),
            "witness": (
                "two zero-tail prefixes equal except for one unit at n=5"
            ),
            "inter_fibre_distance_upper_exact": _fraction_text(
                query_upper_distance
            ),
            "robust_noise_radius_upper_exact": _fraction_text(
                query_upper_radius
            ),
            "robust_noise_radius_upper_squared_exact": _fraction_text(
                query_upper_radius**2
            ),
            "schur_sufficient_lower_strictly_below_upper": query_bracket_passed,
            "status": (
                "upper obstruction paired with a sufficient lower bound; "
                "not an exact minimax determination"
            ),
        },
        "formal_consequence": {
            "positive_result": (
                "each queried unit-spaced prefix coordinate is stably distinguishable "
                "at its recorded Schur sufficient radius"
            ),
            "queried_prefix_unit_spacing_required": True,
            "literal_integrality_required": False,
            "nonquery_prefix_integrality_required": False,
            "tail_integrality_required": False,
            "tail_requirement": (
                "the AS-V finite-plus-remote correlation bounds and coefficientwise "
                "domination class; tail coefficients may be continuous"
            ),
            "n5_status": (
                "Schur sufficient lower radius versus a 1/50 zero-tail upper "
                "obstruction; not an exact minimax value"
            ),
        },
        "all_anchor_rounding_margins_positive": all(
            record["coefficient_bound_certainly_below_one_half"]
            for record in records
        ),
        "passed": True,
    }


def _factor_integer(value: int) -> dict[int, int]:
    if type(value) is not int or value < 1:
        raise ValueError("factorization input must be a positive integer")
    remainder = value
    factor = 2
    result: dict[int, int] = {}
    while factor * factor <= remainder:
        exponent = 0
        while remainder % factor == 0:
            remainder //= factor
            exponent += 1
        if exponent:
            result[factor] = exponent
        factor = 3 if factor == 2 else factor + 2
    if remainder > 1:
        result[remainder] = result.get(remainder, 0) + 1
    product = math.prod(prime**exponent for prime, exponent in result.items())
    if product != value:
        raise ValueError("integer factorization reconstruction failed")
    return result


def _generalized_divisor_count(value: int, degree: int) -> int:
    factors = _factor_integer(value)
    return math.prod(
        math.comb(exponent + degree - 1, degree - 1)
        for exponent in factors.values()
    )


def _outside_prime_box(factors: dict[int, int]) -> bool:
    return any(prime not in PRIME_BOX_PRIMES for prime in factors) or any(
        factors.get(prime, 0) > PRIME_BOX_MAX_EXPONENT
        for prime in PRIME_BOX_PRIMES
    )


def _realified_phasor(time: Fraction, mode: int) -> tuple[arb, arb]:
    theta = _arb_rational(time) * arb(mode).log()
    return theta.cos(), -theta.sin()


def _arb_matrix_rows(matrix: arb_mat) -> list[list[arb]]:
    return [
        [matrix[row, column] for column in range(matrix.ncols())]
        for row in range(matrix.nrows())
    ]


def _build_tail_matrix() -> tuple[arb_mat, list[dict[str, object]]]:
    columns: list[list[arb]] = []
    mode_records: list[dict[str, object]] = []
    for mode, expected_weight in zip(TAIL_MODES, TAIL_WEIGHTS):
        factors = _factor_integer(mode)
        divisor_count = _generalized_divisor_count(mode, SOURCE_DEGREE)
        weight = Fraction(divisor_count, mode * mode)
        if weight != expected_weight:
            raise ValueError("frozen d_14 tail weight is inconsistent")
        if not _outside_prime_box(factors):
            raise ValueError("frozen tail mode lies in the core prime box")
        column: list[arb] = []
        for time in TIMES:
            real, imaginary = _realified_phasor(time, mode)
            column.extend((_arb_rational(weight) * real, _arb_rational(weight) * imaginary))
        columns.append(column)
        mode_records.append(
            {
                "mode": mode,
                "prime_factorization": [
                    [prime, exponent] for prime, exponent in sorted(factors.items())
                ],
                "d14_exact": divisor_count,
                "weight_definition": "d_14(n)/n^2",
                "weight_exact": _fraction_text(weight),
                "outside_core_prime_box": True,
            }
        )
    rows = [
        [columns[column][row] for column in range(len(columns))]
        for row in range(2 * len(TIMES))
    ]
    return arb_mat(rows), mode_records


def _leading_principal(matrix: arb_mat, order: int) -> arb_mat:
    return arb_mat(
        [
            [matrix[row, column] for column in range(order)]
            for row in range(order)
        ]
    )


def _build_continuous_tail_section() -> dict[str, object]:
    matrix, mode_records = _build_tail_matrix()
    if matrix.nrows() != 6 or matrix.ncols() != 6:
        raise ValueError("frozen tail witness is not six by six")
    gram = matrix * matrix.transpose()
    shifted = arb_mat(
        [
            [
                gram[row, column]
                - (_arb_rational(SINGULAR_VALUE_FLOOR**2) if row == column else arb(0))
                for column in range(6)
            ]
            for row in range(6)
        ]
    )
    minor_records: list[dict[str, object]] = []
    all_positive = True
    for order in range(1, 7):
        determinant = _leading_principal(shifted, order).det()
        positive = bool(determinant > 0)
        all_positive &= positive
        minor_records.append(
            {
                "order": order,
                "determinant_interval": _interval_text(determinant),
                "determinant_lower_endpoint_exact": _fraction_text(
                    _lower_exact(determinant)
                ),
                "certainly_positive": positive,
            }
        )
    if not all_positive:
        raise ValueError("tail witness failed the strict Sylvester test")

    core_left, core_right = CORE_VERTEX_NORMS
    difference_entries: list[arb] = []
    for time in TIMES:
        left_real, left_imag = _realified_phasor(time, core_left)
        right_real, right_imag = _realified_phasor(time, core_right)
        difference_entries.extend((left_real - right_real, left_imag - right_imag))
    difference = arb_mat([[entry] for entry in difference_entries])
    correction = matrix.solve(-difference)
    correction_records: list[dict[str, object]] = []
    correction_bounded = True
    sign_pattern: list[int] = []
    for index in range(6):
        value = correction[index, 0]
        bounded = bool(abs(value) < _arb_rational(COLLISION_COORDINATE_BOUND))
        correction_bounded &= bounded
        if bool(value > 0):
            sign = 1
        elif bool(value < 0):
            sign = -1
        else:
            raise ValueError("collision correction sign is not certified")
        sign_pattern.append(sign)
        correction_records.append(
            {
                "mode": TAIL_MODES[index],
                "normalized_correction_interval": _interval_text(value),
                "absolute_upper_endpoint_exact": _fraction_text(
                    _upper_abs_exact(value)
                ),
                "sign": sign,
                "absolute_value_certainly_below_one_third": bounded,
            }
        )
    if not correction_bounded:
        raise ValueError("collision correction exceeds its tail envelope")
    residual = matrix * correction + difference
    residual_records: list[dict[str, object]] = []
    for index, value in enumerate(sum(_arb_matrix_rows(residual), [])):
        contains_zero = bool(value.contains(0))
        if not contains_zero:
            raise ValueError("enclosed collision solve has a nonzero residual")
        residual_records.append(
            {
                "realified_coordinate": index,
                "residual_interval": _interval_text(value),
                "contains_zero": contains_zero,
            }
        )

    core_diameter = 2 * arb(3).sqrt()
    core_diameter_passed = bool(
        core_diameter < _arb_rational(CORE_DIAMETER_RATIONAL_UPPER)
        and _arb_rational(CORE_DIAMETER_RATIONAL_UPPER)
        < _arb_rational(SINGULAR_VALUE_FLOOR)
    )
    if not core_diameter_passed:
        raise ValueError("normalized-core diameter comparison failed")

    return {
        "model": {
            "core": (
                "normalized nonnegative coefficient tensors on the labelled "
                "4-by-4-by-4 prime box, read as sum_n p_n*n^(-it)"
            ),
            "continuous_query_scope": (
                "the normalized product core is continuously variable, including "
                "its queried coordinate p_1; this is not a fixed-a_1 obstruction"
            ),
            "continuous_tail": (
                "real tail harmonic amplitudes c_n with 0<=c_n<=d_14(n)/n^2"
            ),
            "tail_difference_coordinates": (
                "x_n=(c_n-c'_n)/(d_14(n)/n^2), hence x in [-1,1]^6"
            ),
            "realification_order": "Re(t_1),Im(t_1),Re(t_2),Im(t_2),Re(t_3),Im(t_3)",
            "phasor_convention": "n^(-it)=cos(t*log(n))-i*sin(t*log(n))",
        },
        "times_exact": [_fraction_text(time) for time in TIMES],
        "core_prime_box": {
            "primes": list(PRIME_BOX_PRIMES),
            "exponents": "0<=alpha_j<=3",
        },
        "mode_records": mode_records,
        "response_matrix_intervals": [
            [_interval_text(value) for value in row]
            for row in _arb_matrix_rows(matrix)
        ],
        "gram_definition": "G=W*W^T",
        "shifted_gram_definition": "G-25*I",
        "leading_principal_minor_records": minor_records,
        "sylvester_positive_definite_verified": all_positive,
        "smallest_singular_value_certainly_above_exact": _fraction_text(
            SINGULAR_VALUE_FLOOR
        ),
        "zonotope_consequence": (
            "W[-epsilon,epsilon]^6 contains every Euclidean vector of norm "
            "at most 5*epsilon because sigma_min(W)>5"
        ),
        "normalized_core_reading_diameter_interval": _interval_text(core_diameter),
        "normalized_core_reading_diameter_rational_upper_exact": _fraction_text(
            CORE_DIAMETER_RATIONAL_UPPER
        ),
        "diameter_chain": "2*sqrt(3)<7/2<5",
        "diameter_chain_verified": core_diameter_passed,
        "explicit_collision": {
            "core_vertex_norms": list(CORE_VERTEX_NORMS),
            "core_vertex_exponents": [[0, 0, 0], [3, 3, 3]],
            "queried_p1_values_exact": ["1/1", "0/1"],
            "queried_p1_is_fixed": False,
            "difference_definition": "d=H(delta_1)-H(delta_27000)",
            "correction_definition": "x is the unique exact solution W*x=-d",
            "tail_pair_definition": (
                "c_n=(d_14(n)/n^2)*max(x_n,0), "
                "c'_n=(d_14(n)/n^2)*max(-x_n,0)"
            ),
            "collision_identity": "H(delta_1+c)=H(delta_27000+c')",
            "normalized_coordinate_bound_exact": _fraction_text(
                COLLISION_COORDINATE_BOUND
            ),
            "correction_records": correction_records,
            "certified_sign_pattern": sign_pattern,
            "all_correction_coordinates_strictly_inside_envelope": correction_bounded,
            "enclosed_solve_residual_records": residual_records,
            "exact_collision_inputs_verified": correction_bounded,
        },
        "passed": bool(all_positive and correction_bounded and core_diameter_passed),
    }


def build_artifact(
    source_path: Path = DEFAULT_SOURCE_PATH,
    precision: int = FORMAL_PRECISION_BITS,
) -> dict[str, object]:
    _check_environment()
    if type(precision) is not int or not MIN_PRECISION_BITS <= precision <= MAX_PRECISION_BITS:
        raise ValueError("precision must be a bounded canonical integer")
    ctx.prec = precision
    localized = _build_localized_neumann_section(source_path)
    continuous = _build_continuous_tail_section()
    passed = bool(localized["passed"] and continuous["passed"])
    payload: dict[str, object] = {
        "parameters": {
            "source_degree": SOURCE_DEGREE,
            "source_maximum_norm": SOURCE_MAXIMUM_NORM,
            "source_sigma": SOURCE_SIGMA,
            "source_distinct_sample_count": SOURCE_DISTINCT_SAMPLE_COUNT,
            "source_output_scale_bits": SOURCE_OUTPUT_SCALE_BITS,
            "query_anchors": list(ANCHORS),
            "reading_count": len(TIMES),
            "tail_mode_count": len(TAIL_MODES),
        },
        "formal_environment": {
            "precision_bits": precision,
            "python_flint_version": PINNED_PYTHON_FLINT_VERSION,
            "flint_version": PINNED_FLINT_VERSION,
            "interval_backend": "Arb",
        },
        "localized_integer_queries": localized,
        "continuous_tail_obstruction": continuous,
        "reproduction_files": {
            "verifier_basename": VERIFIER_PATH.name,
            "verifier_sha256": _sha256_file(VERIFIER_PATH),
            "tests_basename": TESTS_PATH.name,
            "tests_sha256": _sha256_file(TESTS_PATH),
        },
        "finite_certificate_passed": passed,
        "formal_scope": {
            "certifies": (
                "the exact localized Neumann inputs and consequences at anchors "
                "1,2,3,5; the strict six-mode Sylvester witness; and an Arb "
                "enclosure of a strict interior correction producing the frozen "
                "continuous-tail collision"
            ),
            "localized_neumann_theorem_mechanized": False,
            "zonotope_ball_theorem_mechanized": False,
            "integer_tail_model_replaced_by_continuous_tail": False,
            "positive_integrality_assumption": (
                "only the queried prefix coordinates require unit spacing; "
                "nonquery prefix coordinates and all dominated tails may be continuous"
            ),
            "tail_integrality_required": False,
            "continuous_tail_claim_is_a_separate_relaxation": True,
            "local_vanishing_radius_obstruction_requires_interval_valued_query": True,
            "explicit_full_envelope_collision_requires_interval_valued_query": False,
            "explicit_full_envelope_collision_allows_unit_spaced_query_values": True,
            "continuous_obstruction_does_not_fix_a1": True,
            "exact_minimax_radius_claimed": False,
            "all_fifty_comparison_status": (
                "ratio between two certified sufficient lower radii, not exact minimax values"
            ),
        },
    }
    return {"schema": SCHEMA, "payload": payload, "payload_sha256": _sha256(payload)}


def _reject_float(_: str) -> float:
    raise ValueError("artifact contains a forbidden JSON floating-point number")


def _audit_tree(value: object, depth: int = 0) -> None:
    if depth > MAX_JSON_DEPTH:
        raise ValueError("artifact exceeds the maximum JSON depth")
    if isinstance(value, dict):
        if len(value) > MAX_CONTAINER_ITEMS:
            raise ValueError("artifact object violates the resource cap")
        for key, item in value.items():
            if type(key) is not str or len(key) > MAX_TEXT_FIELD_LENGTH:
                raise ValueError("artifact key violates the resource cap")
            _audit_tree(item, depth + 1)
    elif isinstance(value, list):
        if len(value) > MAX_CONTAINER_ITEMS:
            raise ValueError("artifact list violates the resource cap")
        for item in value:
            _audit_tree(item, depth + 1)
    elif isinstance(value, str):
        if len(value) > MAX_TEXT_FIELD_LENGTH:
            raise ValueError("artifact text violates the resource cap")
    elif value is None or type(value) is bool:
        return
    elif type(value) is int:
        if value.bit_length() > MAX_INTEGER_BITS:
            raise ValueError("artifact integer violates the resource cap")
    else:
        raise ValueError("artifact contains an unsupported JSON value")


def _load_strict_artifact(path: Path) -> dict[str, object]:
    with path.open("rb") as handle:
        raw = handle.read(MAX_ARTIFACT_BYTES + 1)
    if len(raw) > MAX_ARTIFACT_BYTES:
        raise ValueError("artifact exceeds the byte resource cap")
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("artifact must not contain a UTF-8 BOM")
    if b"\r" in raw:
        raise ValueError("artifact must use LF line endings")
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise ValueError("artifact must end in exactly one LF")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("artifact is not canonical UTF-8 JSON") from exc
    try:
        artifact = json.loads(
            text,
            parse_int=_parse_json_integer,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
            object_pairs_hook=_object_without_duplicates,
        )
    except json.JSONDecodeError as exc:
        raise ValueError("artifact is malformed JSON") from exc
    if not isinstance(artifact, dict):
        raise ValueError("artifact root must be an object")
    _audit_tree(artifact)
    if raw != _pretty_json(artifact):
        raise ValueError("artifact is not in canonical deterministic JSON encoding")
    return artifact


def _validate_fraction_list(
    values: object, expected: Sequence[Fraction], label: str
) -> None:
    if not isinstance(values, list) or len(values) != len(expected):
        raise ValueError(f"artifact uses a malformed {label}")
    if tuple(_parse_fraction_limited(value) for value in values) != tuple(expected):
        raise ValueError(f"artifact uses a noncanonical {label}")


def _validate_payload_constants(payload: object, source_path: Path) -> None:
    if not isinstance(payload, dict):
        raise ValueError("artifact payload is malformed")
    parameters = payload.get("parameters")
    if not isinstance(parameters, dict):
        raise ValueError("artifact parameters are malformed")
    expected_integer_parameters = {
        "source_degree": SOURCE_DEGREE,
        "source_maximum_norm": SOURCE_MAXIMUM_NORM,
        "source_sigma": SOURCE_SIGMA,
        "source_distinct_sample_count": SOURCE_DISTINCT_SAMPLE_COUNT,
        "source_output_scale_bits": SOURCE_OUTPUT_SCALE_BITS,
        "reading_count": len(TIMES),
        "tail_mode_count": len(TAIL_MODES),
    }
    for key, expected in expected_integer_parameters.items():
        value = parameters.get(key)
        if type(value) is not int or value != expected:
            raise ValueError(f"artifact uses noncanonical {key}")
    if parameters.get("query_anchors") != list(ANCHORS):
        raise ValueError("artifact uses noncanonical query anchors")

    localized = payload.get("localized_integer_queries")
    continuous = payload.get("continuous_tail_obstruction")
    environment = payload.get("formal_environment")
    reproduction = payload.get("reproduction_files")
    if not all(
        isinstance(section, dict)
        for section in (localized, continuous, environment, reproduction)
    ):
        raise ValueError("artifact has a malformed formal section")
    assert isinstance(localized, dict)
    assert isinstance(continuous, dict)
    assert isinstance(environment, dict)
    assert isinstance(reproduction, dict)
    if (
        type(environment.get("precision_bits")) is not int
        or environment.get("precision_bits") != FORMAL_PRECISION_BITS
    ):
        raise ValueError("artifact uses a noncanonical formal precision")
    source = localized.get("source")
    if not isinstance(source, dict):
        raise ValueError("artifact source section is malformed")
    if source.get("file_sha256") != EXPECTED_SOURCE_FILE_SHA256:
        raise ValueError("artifact source file digest is noncanonical")
    if source.get("formal_certificate_sha256") != EXPECTED_SOURCE_FORMAL_SHA256:
        raise ValueError("artifact source formal digest is noncanonical")
    records = localized.get("anchor_records")
    if not isinstance(records, list) or len(records) != len(ANCHORS):
        raise ValueError("artifact anchor records are malformed")
    for index, record in enumerate(records):
        if (
            not isinstance(record, dict)
            or type(record.get("anchor")) is not int
            or record.get("anchor") != ANCHORS[index]
        ):
            raise ValueError("artifact anchor record is noncanonical")
        for key in (
            "finite_tail_upper_exact",
            "remote_tail_upper_exact",
            "complete_tail_upper_exact",
            "gram_row_upper_exact",
            "localized_coefficient_bound_exact",
            "rounding_margin_exact",
            "sufficient_noise_radius_squared_exact",
            "query_fibre_distance_lower_squared_exact",
            "schur_factor_exact",
            "schur_numerator_exact",
            "certified_bar_kappa_squared_exact",
            "schur_sufficient_noise_radius_squared_exact",
            "schur_query_fibre_distance_lower_squared_exact",
            "anisotropic_unit_separation_weight_squared_lower_exact",
        ):
            _parse_fraction_limited(record.get(key))
        if type(record.get("schur_numerator_certainly_positive")) is not bool:
            raise ValueError("artifact Schur positivity flag is noncanonical")
    _validate_fraction_list(continuous.get("times_exact"), TIMES, "reading times")
    mode_records = continuous.get("mode_records")
    if not isinstance(mode_records, list) or len(mode_records) != len(TAIL_MODES):
        raise ValueError("artifact tail-mode records are malformed")
    for index, record in enumerate(mode_records):
        if (
            not isinstance(record, dict)
            or type(record.get("mode")) is not int
            or record.get("mode") != TAIL_MODES[index]
        ):
            raise ValueError("artifact tail mode is noncanonical")
        if _parse_fraction_limited(record.get("weight_exact")) != TAIL_WEIGHTS[index]:
            raise ValueError("artifact tail weight is noncanonical")
    if _parse_fraction_limited(
        continuous.get("smallest_singular_value_certainly_above_exact")
    ) != SINGULAR_VALUE_FLOOR:
        raise ValueError("artifact singular-value floor is noncanonical")
    expected_reproduction = {
        "verifier_basename": VERIFIER_PATH.name,
        "verifier_sha256": _sha256_file(VERIFIER_PATH),
        "tests_basename": TESTS_PATH.name,
        "tests_sha256": _sha256_file(TESTS_PATH),
    }
    if reproduction != expected_reproduction:
        raise ValueError("artifact uses noncanonical reproduction-file hashes")
    # Re-read the pinned source during verification even before exact rebuild.
    _source_exact_inputs(source_path)


def verify_artifact(
    artifact_path: Path,
    source_path: Path = DEFAULT_SOURCE_PATH,
) -> dict[str, object]:
    _check_environment()
    artifact = _load_strict_artifact(artifact_path)
    if set(artifact) != {"schema", "payload", "payload_sha256"}:
        raise ValueError("artifact has unexpected top-level fields")
    if artifact.get("schema") != SCHEMA:
        raise ValueError("artifact schema is not canonical")
    payload = artifact.get("payload")
    digest = artifact.get("payload_sha256")
    if not isinstance(digest, str) or len(digest) != 64 or any(
        character not in "0123456789abcdef" for character in digest
    ):
        raise ValueError("payload digest is not canonical lowercase SHA-256")
    if digest != _sha256(payload):
        raise ValueError("payload digest mismatch")
    _validate_payload_constants(payload, source_path)
    expected = build_artifact(source_path, FORMAL_PRECISION_BITS)
    if _canonical_json(artifact) != _canonical_json(expected):
        raise ValueError("artifact differs from exact reconstruction")
    return {
        "verified": True,
        "schema": SCHEMA,
        "payload_sha256": digest,
        "anchor_count": len(ANCHORS),
        "tail_mode_count": len(TAIL_MODES),
        "precision_bits": FORMAL_PRECISION_BITS,
        "unique_bottleneck_anchor": 5,
        "continuous_tail_singular_value_floor": _fraction_text(
            SINGULAR_VALUE_FLOOR
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE_PATH)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--precision", type=int, default=FORMAL_PRECISION_BITS)
    args = parser.parse_args()
    if args.write is not None and args.verify is not None:
        parser.error("--write and --verify are mutually exclusive")
    if args.verify is not None:
        print(
            json.dumps(
                verify_artifact(args.verify, args.source), indent=2, sort_keys=True
            )
        )
        return
    artifact = build_artifact(args.source, args.precision)
    rendered = _pretty_json(artifact)
    if args.write is None:
        print(rendered.decode("utf-8"), end="")
    else:
        args.write.write_bytes(rendered)


if __name__ == "__main__":
    main()
