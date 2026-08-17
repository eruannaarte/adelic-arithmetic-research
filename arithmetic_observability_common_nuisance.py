#!/usr/bin/env python3
"""Build and verify the AO-VIII common-nuisance certificate.

The certificate sharpens the Arithmetic Observability VII query bound when
every prefix fibre has the same coefficient box as nuisance.  In that case
the difference of two tails has one signed coefficient in ``[-d_14(k),
d_14(k)]`` at each mode, rather than two independently worst-case absolute
tails.  Consequently the certified erosion is ``eta_n`` instead of
``2*eta_n``.

The finite artifact also proves three complementary facts.

* It evaluates the common-box radius for all fifty AS-V coordinates and
  proves that coordinate 50 is the unique all-prefix bottleneck.
* It proves that the zero-tail ``e_5`` pair is the unique closest pair in the
  integer prefix lattice (up to sign and translation).
* It supplies integral, finitely supported tail witnesses near the first
  log-frequency sampling alias.  These make the true radii at coordinates 5
  and 50 strictly smaller than their zero-tail column obstructions.

General common-box separation and the prefix-lattice argument are manuscript
mathematics.  This executable artifact certifies their frozen rational and
transcendental inputs.
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


SCHEMA = "arithmetic-observability-common-nuisance-v1"
PINNED_PAYLOAD_SHA256 = (
    "96b874899b16e4502d815627c7b722b9ba0332266fb30c8cd4d0579b48ca0cfd"
)
EXPECTED_SOURCE_SCHEMA = "arithmetic-sensing-v-time-ensemble-v1"
EXPECTED_SOURCE_BASENAME = "arithmetic_sensing_v_multiscale_end_to_end.json"
EXPECTED_SOURCE_FILE_SHA256 = (
    "ad03df9d6325512074e6940602c1c888c81abd057a5856d6212f93dc8e780517"
)
EXPECTED_SOURCE_FORMAL_SHA256 = (
    "89b316584d9179c13232ad99b9515067fdf67329e6df3db4c48220d6b8c3ff7b"
)

FORMAL_PRECISION_BITS = 512
MIN_PRECISION_BITS = 384
MAX_PRECISION_BITS = 1024
PINNED_PYTHON_FLINT_VERSION = "0.9.0"
PINNED_FLINT_VERSION = "3.6.0"

SOURCE_DEGREE = 14
SOURCE_MAXIMUM_NORM = 50
SOURCE_SIGMA = 2
SOURCE_OUTPUT_SCALE_BITS = 128
ANCHORS = (1, 2, 3, 5)

MAX_ARTIFACT_BYTES = 500_000
MAX_SOURCE_BYTES = 64_000
MAX_CONTAINER_ITEMS = 2048
MAX_JSON_DEPTH = 28
MAX_TEXT_FIELD_LENGTH = 16_384
MAX_INTEGER_BITS = 8192
INTERVAL_DISPLAY_DIGITS = 110

# The binary64 coefficients used by the pinned AS-IV/AS-V design.  Hex input
# makes their exact binary values independent of decimal parsing choices.
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
COMPONENTS = (
    (510, 2550, Fraction(125, 65_536)),
    (1780, 8900, Fraction(65_411, 65_536)),
)
COMMON_SPACING = Fraction(1, 5)
FIRST_ALIAS_ANGULAR_FREQUENCY = 10  # multiplied by pi

# Each tuple is (mode, ((prime, exponent), ...)).  The tail coefficient is
# exactly d_14(mode), reconstructed from the displayed factorization.
ALIAS_MODES_5 = (
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

ALIAS_MODES_50 = (
    (2_201_575_292_642_880, ((2, 6), (3, 8), (5, 1), (7, 2), (11, 2), (47, 1), (53, 1), (71, 1))),
    (2_201_575_292_928_000, ((2, 19), (3, 4), (5, 3), (11, 1), (37, 1), (1019, 1))),
    (2_201_575_292_461_440, ((2, 7), (3, 4), (5, 1), (7, 1), (17, 1), (19, 1), (43, 1), (191, 1), (2287, 1))),
    (2_201_575_293_665_280, ((2, 14), (3, 2), (5, 1), (13, 1), (19, 1), (41, 1), (71, 1), (4153, 1))),
    (2_201_575_292_167_680, ((2, 9), (3, 3), (5, 1), (11, 1), (13, 2), (17, 1), (239, 1), (4217, 1))),
    (2_201_575_293_514_080, ((2, 5), (3, 2), (5, 1), (11, 2), (17, 1), (29, 1), (37, 1), (43, 1), (89, 1), (181, 1))),
    (2_201_575_293_754_200, ((2, 3), (3, 4), (5, 2), (7, 2), (13, 1), (19, 1), (29, 1), (67, 1), (5779, 1))),
    (2_201_575_292_280_000, ((2, 6), (3, 4), (5, 4), (7, 1), (13, 1), (727, 1), (10271, 1))),
    (2_201_575_292_596_224, ((2, 12), (3, 6), (23, 1), (97, 1), (563, 1), (587, 1))),
    (2_201_575_293_650_304, ((2, 7), (3, 3), (11, 1), (13, 1), (43, 1), (53, 1), (79, 1), (109, 1), (227, 1))),
)

PACKAGE_ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE_PATH = PACKAGE_ROOT / "certificates" / EXPECTED_SOURCE_BASENAME
VERIFIER_PATH = PACKAGE_ROOT / "arithmetic_observability_common_nuisance.py"
TESTS_PATH = PACKAGE_ROOT / "test_arithmetic_observability_common_nuisance.py"
DEFAULT_ARTIFACT_PATH = (
    PACKAGE_ROOT / "arithmetic_observability_common_nuisance_certificate.json"
)


def _fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def _parse_fraction_limited(text: object) -> Fraction:
    if not isinstance(text, str) or len(text) > 8192 or text.count("/") != 1:
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


def _arb_rational(value: Fraction | int) -> arb:
    value = Fraction(value)
    return arb(fmpq(value.numerator, value.denominator))


def _interval_text(value: arb) -> str:
    return value.str(INTERVAL_DISPLAY_DIGITS, radius=True, more=True)


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


def _reject_float(_: str) -> object:
    raise ValueError("JSON floating literals are forbidden")


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


def _validate_json_shape(
    value: object, depth: int = 0, *, allow_floats: bool = False
) -> None:
    if depth > MAX_JSON_DEPTH:
        raise ValueError("JSON nesting exceeds the formal limit")
    if isinstance(value, dict):
        if len(value) > MAX_CONTAINER_ITEMS:
            raise ValueError("JSON object exceeds the formal item limit")
        for key, item in value.items():
            if not isinstance(key, str) or len(key) > MAX_TEXT_FIELD_LENGTH:
                raise ValueError("JSON object key is invalid")
            _validate_json_shape(item, depth + 1, allow_floats=allow_floats)
    elif isinstance(value, list):
        if len(value) > MAX_CONTAINER_ITEMS:
            raise ValueError("JSON array exceeds the formal item limit")
        for item in value:
            _validate_json_shape(item, depth + 1, allow_floats=allow_floats)
    elif isinstance(value, str):
        if len(value) > MAX_TEXT_FIELD_LENGTH:
            raise ValueError("JSON string exceeds the formal limit")
    elif type(value) is float and allow_floats:
        if not math.isfinite(value):
            raise ValueError("JSON contains a nonfinite float")
    elif type(value) not in (int, bool) and value is not None:
        raise ValueError("JSON contains an unsupported scalar")


def _load_json_strict(
    path: Path, maximum_bytes: int, *, allow_floats: bool = False
) -> tuple[dict[str, object], bytes]:
    with path.open("rb") as handle:
        raw = handle.read(maximum_bytes + 1)
    if len(raw) > maximum_bytes:
        raise ValueError("JSON artifact exceeds its formal byte limit")
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("JSON artifact must not use a UTF-8 BOM")
    if (
        b"\r" in raw
        or (raw and not raw.endswith(b"\n"))
        or raw.endswith(b"\n\n")
    ):
        raise ValueError("JSON artifact must use LF and end with exactly one newline")
    try:
        value = json.loads(
            raw.decode("utf-8"),
            parse_int=_parse_json_integer,
            parse_float=float if allow_floats else _reject_float,
            parse_constant=_reject_constant,
            object_pairs_hook=_object_without_duplicates,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("JSON artifact is malformed") from exc
    if not isinstance(value, dict):
        raise ValueError("JSON artifact root must be an object")
    _validate_json_shape(value, allow_floats=allow_floats)
    return value, raw


def _source_exact_inputs(source_path: Path) -> dict[str, object]:
    # The pinned source contains one descriptive binary64 decimal.  Its file
    # hash is checked before any value is trusted, while our own artifact
    # remains float-free.
    source, raw = _load_json_strict(
        source_path, MAX_SOURCE_BYTES, allow_floats=True
    )
    if set(source) != {"certificate", "formal_certificate_sha256", "producer", "schema"}:
        raise ValueError("source artifact has unexpected top-level fields")
    if source.get("schema") != EXPECTED_SOURCE_SCHEMA:
        raise ValueError("source artifact schema mismatch")
    if _sha256_bytes(raw) != EXPECTED_SOURCE_FILE_SHA256:
        raise ValueError("source artifact file digest mismatch")
    certificate = source.get("certificate")
    if not isinstance(certificate, dict):
        raise ValueError("source certificate is missing")
    if source.get("formal_certificate_sha256") != EXPECTED_SOURCE_FORMAL_SHA256:
        raise ValueError("source formal digest mismatch")
    if _sha256(certificate) != EXPECTED_SOURCE_FORMAL_SHA256:
        raise ValueError("source certificate content digest mismatch")
    parameters = certificate.get("parameters")
    finite = certificate.get("finite")
    remote = certificate.get("combined_remote")
    gram = certificate.get("gram")
    consequence = certificate.get("consequence")
    if not all(isinstance(value, dict) for value in (parameters, finite, remote, gram, consequence)):
        raise ValueError("source certificate sections are missing")
    assert isinstance(parameters, dict)
    expected_parameters = {
        "degree": SOURCE_DEGREE,
        "maximum_norm": SOURCE_MAXIMUM_NORM,
        "sigma": SOURCE_SIGMA,
        "output_scale_bits": SOURCE_OUTPUT_SCALE_BITS,
        "common_sample_spacing": str(COMMON_SPACING),
    }
    for name, expected in expected_parameters.items():
        if parameters.get(name) != expected:
            raise ValueError(f"source parameter {name} mismatch")
    expected_components = [
        {"observation_time": time, "sample_count": count, "weight": str(weight)}
        for time, count, weight in COMPONENTS
    ]
    if parameters.get("components") != expected_components:
        raise ValueError("source component schedule mismatch")

    assert isinstance(finite, dict)
    assert isinstance(remote, dict)
    assert isinstance(gram, dict)
    assert isinstance(consequence, dict)
    denominator = 1 << SOURCE_OUTPUT_SCALE_BITS
    finite_numerators = finite.get("target_numerators")
    remote_numerators = remote.get("target_numerators")
    row_numerators = gram.get("row_numerators")
    if not all(
        isinstance(values, list) and len(values) == SOURCE_MAXIMUM_NORM
        for values in (finite_numerators, remote_numerators, row_numerators)
    ):
        raise ValueError("source vectors have invalid length")
    try:
        finite_bounds = tuple(Fraction(int(value), denominator) for value in finite_numerators)
        remote_bounds = tuple(Fraction(int(value), denominator) for value in remote_numerators)
        row_bounds = tuple(Fraction(int(value), denominator) for value in row_numerators)
    except (TypeError, ValueError) as exc:
        raise ValueError("source vector is malformed") from exc
    q = Fraction(str(gram.get("maximum_row_upper")))
    tau = max(a + b for a, b in zip(finite_bounds, remote_bounds))
    if max(row_bounds) != q:
        raise ValueError("source maximum Gram row is inconsistent")
    if Fraction(str(consequence.get("maximum_complete_tail"))) != tau:
        raise ValueError("source maximum complete tail is inconsistent")
    global_eta = Fraction(str(consequence.get("coefficient_bound")))
    if not (0 <= q < 1 and 0 <= tau and 0 <= global_eta < Fraction(1, 2)):
        raise ValueError("source Neumann inputs are invalid")
    return {
        "source_file_sha256": _sha256_bytes(raw),
        "finite_bounds": finite_bounds,
        "remote_bounds": remote_bounds,
        "row_bounds": row_bounds,
        "q": q,
        "tau": tau,
        "global_eta": global_eta,
    }


def _centered_response(frequency: arb, observation_time: int, sample_count: int) -> arb:
    if frequency == 0:
        return arb(1)
    pi = arb.pi()
    coefficients = tuple(
        _arb_rational(Fraction.from_float(float.fromhex(value)))
        for value in WINDOW_COEFFICIENT_HEX
    )
    u = arb(observation_time) * frequency / 2
    bracket = 1 / (sample_count * (u / sample_count).sin())
    for harmonic, coefficient in enumerate(coefficients, start=1):
        bracket += coefficient * (
            1 / (sample_count * ((u + pi * harmonic) / sample_count).sin())
            + 1 / (sample_count * ((u - pi * harmonic) / sample_count).sin())
        )
    result = u.sin() * bracket
    if not result.is_finite():
        raise ArithmeticError("Arb failed to separate a removable alias")
    return result


def _kernel(left: int, right: int) -> arb:
    if left == right:
        return arb(1)
    frequency = (arb(left) / right).log()
    result = arb(0)
    for time, count, weight in COMPONENTS:
        result += _arb_rational(weight) * _centered_response(frequency, time, count)
    return result


def _factorization_product(factors: Sequence[tuple[int, int]]) -> int:
    result = 1
    previous = 1
    for prime, exponent in factors:
        if prime <= previous or exponent < 1:
            raise ValueError("factorization is not canonical")
        # Trial division is sufficient for the small frozen prime factors.
        if prime < 2 or any(prime % divisor == 0 for divisor in range(2, math.isqrt(prime) + 1)):
            raise ValueError("factorization contains a composite base")
        result *= prime**exponent
        previous = prime
    return result


def _d14_from_factors(factors: Sequence[tuple[int, int]]) -> int:
    result = 1
    for _, exponent in factors:
        result *= math.comb(13 + exponent, exponent)
    return result


def _build_common_box_section(inputs: dict[str, object]) -> dict[str, object]:
    finite = inputs["finite_bounds"]
    remote = inputs["remote_bounds"]
    rows = inputs["row_bounds"]
    q = inputs["q"]
    tau = inputs["tau"]
    global_eta = inputs["global_eta"]
    assert isinstance(finite, tuple)
    assert isinstance(remote, tuple)
    assert isinstance(rows, tuple)
    assert isinstance(q, Fraction)
    assert isinstance(tau, Fraction)
    assert isinstance(global_eta, Fraction)

    records: list[dict[str, object]] = []
    radius_squares: dict[int, Fraction] = {}
    generic_radius_squares: dict[int, Fraction] = {}
    eta_values: dict[int, Fraction] = {}
    for n in range(1, SOURCE_MAXIMUM_NORM + 1):
        q_n = rows[n - 1]
        finite_principal = n * n * finite[n - 1]
        remote_principal = n * n * remote[n - 1]
        inverse_coupling = n * n * q_n * tau / (1 - q)
        eta = finite_principal + remote_principal + inverse_coupling
        schur_numerator = 1 - q - q_n * q_n
        schur_factor = schur_numerator / (1 - q)
        kappa_bar_squared = n**4 / schur_factor
        radius_squared = (1 - eta) ** 2 * schur_factor / (4 * n**4)
        generic_radius_squared = (Fraction(1, 2) - eta) ** 2 * schur_factor / n**4
        if not (
            0 <= eta < Fraction(1, 2)
            and schur_numerator > 0
            and radius_squared > generic_radius_squared > 0
        ):
            raise ValueError("common-box row has invalid certified inputs")
        radius = _arb_rational(radius_squared).sqrt()
        eta_values[n] = eta
        radius_squares[n] = radius_squared
        generic_radius_squares[n] = generic_radius_squared
        records.append(
            {
                "coordinate": n,
                "gram_row_upper_exact": _fraction_text(q_n),
                "pair_specific_eta_bound_exact": _fraction_text(eta),
                "finite_decoder_principal_exact": _fraction_text(finite_principal),
                "remote_decoder_principal_exact": _fraction_text(remote_principal),
                "inverse_coupling_exact": _fraction_text(inverse_coupling),
                "decomposition_sums_to_eta": eta == finite_principal + remote_principal + inverse_coupling,
                "certified_bar_kappa_squared_exact": _fraction_text(kappa_bar_squared),
                "common_box_radius_squared_exact": _fraction_text(radius_squared),
                "common_box_radius_interval": _interval_text(radius),
                "common_box_fibre_distance_squared_lower_exact": _fraction_text(4 * radius_squared),
                "generic_two_tail_radius_squared_exact": _fraction_text(generic_radius_squared),
                "common_box_strictly_improves_generic_bound": radius_squared > generic_radius_squared,
            }
        )

    all_bottleneck = min(radius_squares, key=radius_squares.__getitem__)
    anchor_bottleneck = min(ANCHORS, key=radius_squares.__getitem__)
    if all_bottleneck != 50 or anchor_bottleneck != 5:
        raise ValueError("frozen common-box bottlenecks changed")
    if len(set(radius_squares.values())) != SOURCE_MAXIMUM_NORM:
        raise ValueError("common-box row radii are not pairwise distinct")
    if eta_values[50] != global_eta:
        raise ValueError("source global coefficient bound is not row 50")

    old_all_fifty_squared = (
        (Fraction(1, 2) - global_eta) ** 2
        * (1 - q)
        / SOURCE_MAXIMUM_NORM ** (2 * SOURCE_SIGMA)
    )
    all_gain_squared = radius_squares[50] / old_all_fifty_squared
    if not 127**2 < all_gain_squared < 128**2:
        raise ValueError("common-box/all-fifty gain bracket changed")

    decompositions = []
    direct_pairs = []
    for n in (5, 50):
        record = records[n - 1]
        finite_value = _parse_fraction_limited(record["finite_decoder_principal_exact"])
        remote_value = _parse_fraction_limited(record["remote_decoder_principal_exact"])
        decompositions.append(
            {
                "coordinate": n,
                "finite_decoder_principal_exact": record["finite_decoder_principal_exact"],
                "remote_decoder_principal_exact": record["remote_decoder_principal_exact"],
                "inverse_coupling_exact": record["inverse_coupling_exact"],
                "pair_specific_eta_bound_exact": record["pair_specific_eta_bound_exact"],
                "remote_to_finite_ratio_exact": _fraction_text(remote_value / finite_value),
                "remote_term_strictly_dominates_finite_term": remote_value > finite_value,
            }
        )
        eta_direct = finite[n - 1] + remote[n - 1]
        direct_distance_lower = Fraction(1, n**SOURCE_SIGMA) - eta_direct
        direct_radius_lower = direct_distance_lower / 2
        if direct_distance_lower <= 0:
            raise ValueError("direct-column pair has no positive separation")
        direct_pairs.append(
            {
                "coordinate": n,
                "pair": f"fixed prefix difference plus-or-minus e_{n}",
                "unit_column_norm_exact": _fraction_text(
                    Fraction(1, n**SOURCE_SIGMA)
                ),
                "eta_direct_exact": _fraction_text(eta_direct),
                "eta_direct_definition": "finite_n+remote_n",
                "direct_pair_distance_lower_exact": _fraction_text(
                    direct_distance_lower
                ),
                "direct_pair_distance_lower_interval": _interval_text(
                    _arb_rational(direct_distance_lower)
                ),
                "direct_pair_radius_lower_exact": _fraction_text(
                    direct_radius_lower
                ),
                "direct_pair_radius_lower_interval": _interval_text(
                    _arb_rational(direct_radius_lower)
                ),
                "scope": (
                    "pair-specific c_n dual bound; not a lower bound for all "
                    "query-distinct prefix directions"
                ),
            }
        )

    return {
        "definitions": {
            "common_box_difference": "if 0<=b_k,b'_k<=d_14(k), then abs(b_k-b'_k)<=d_14(k)",
            "pair_specific_eta": "eta_n=n^2*(finite_n+remote_n+q_n*tau/(1-q))",
            "common_box_radius_squared": "(1-eta_n)^2*(1-q-q_n^2)/(4*n^4*(1-q))",
            "generic_two_tail_radius_squared": "(1/2-eta_n)^2*(1-q-q_n^2)/(n^4*(1-q))",
        },
        "global_gram_row_upper_exact": _fraction_text(q),
        "global_complete_tail_upper_exact": _fraction_text(tau),
        "coordinate_records": records,
        "unique_four_anchor_bottleneck": anchor_bottleneck,
        "four_anchor_common_box_radius_squared_exact": _fraction_text(radius_squares[5]),
        "four_anchor_common_box_radius_interval": _interval_text(_arb_rational(radius_squares[5]).sqrt()),
        "unique_all_fifty_bottleneck": all_bottleneck,
        "all_fifty_common_box_radius_squared_exact": _fraction_text(radius_squares[50]),
        "all_fifty_common_box_radius_interval": _interval_text(_arb_rational(radius_squares[50]).sqrt()),
        "old_all_fifty_generic_radius_squared_exact": _fraction_text(old_all_fifty_squared),
        "common_to_old_all_fifty_gain_squared_exact": _fraction_text(all_gain_squared),
        "common_to_old_all_fifty_gain_strictly_between": [127, 128],
        "selected_eta_decompositions": decompositions,
        "direct_column_pair_bounds": direct_pairs,
        "all_rows_eta_strictly_below_one_half": all(value < Fraction(1, 2) for value in eta_values.values()),
        "passed": True,
    }


def _build_no_tail_prefix_section(inputs: dict[str, object]) -> dict[str, object]:
    q = inputs["q"]
    rows = inputs["row_bounds"]
    assert isinstance(q, Fraction)
    assert isinstance(rows, tuple)
    q_5 = rows[4]
    minimum_nuisance_norm = Fraction(1, 50**2)
    positive_root = 2 * q_5 / (25 * (1 - q))
    minimum_increment_lower = (
        (1 - q) * minimum_nuisance_norm**2
        - 2 * q_5 * minimum_nuisance_norm / 25
    )
    query_2_or_3_lower_squared = (1 - q) / 3**4
    doubled_5_lower_squared = 4 * (1 - q) / 5**4
    witness_squared = Fraction(1, 5**4)
    passed = (
        positive_root < minimum_nuisance_norm
        and minimum_increment_lower > 0
        and query_2_or_3_lower_squared > witness_squared
        and doubled_5_lower_squared > witness_squared
    )
    if not passed:
        raise ValueError("no-tail prefix-lattice inequalities failed")
    return {
        "model": "the full integer prefix-difference lattice with d_1=0 and no tails",
        "witness": "d=plus-or-minus e_5, up to a feasible base translation",
        "zero_tail_e5_distance_squared_exact": _fraction_text(witness_squared),
        "global_gram_lower_exact": _fraction_text(1 - q),
        "row_5_off_diagonal_l1_upper_exact": _fraction_text(q_5),
        "minimum_nonzero_nuisance_scaled_norm_exact": _fraction_text(minimum_nuisance_norm),
        "nuisance_positive_root_exact": _fraction_text(positive_root),
        "root_strictly_below_lattice_spacing": positive_root < minimum_nuisance_norm,
        "minimum_nuisance_increment_lower_exact": _fraction_text(minimum_increment_lower),
        "minimum_nuisance_increment_strictly_positive": minimum_increment_lower > 0,
        "query_2_or_3_difference_lower_squared_exact": _fraction_text(query_2_or_3_lower_squared),
        "absolute_d5_at_least_two_lower_squared_exact": _fraction_text(doubled_5_lower_squared),
        "both_alternative_cases_strictly_exceed_witness": (
            query_2_or_3_lower_squared > witness_squared
            and doubled_5_lower_squared > witness_squared
        ),
        "formal_consequence": (
            "the zero-tail e_5 pair is the unique closest query-distinct "
            "prefix-lattice direction up to sign and feasible translation; "
            "this statement excludes tails"
        ),
        "passed": passed,
    }


def _build_alias_witness(
    target: int,
    frozen_modes: Sequence[tuple[int, Sequence[tuple[int, int]]]],
    required_improvement: Fraction,
) -> dict[str, object]:
    mode_records: list[dict[str, object]] = []
    amplitudes: list[Fraction] = []
    modes: list[int] = []
    for mode, factor_sequence in frozen_modes:
        factors = tuple((int(prime), int(exponent)) for prime, exponent in factor_sequence)
        if mode <= SOURCE_MAXIMUM_NORM or _factorization_product(factors) != mode:
            raise ValueError("alias mode factorization mismatch")
        coefficient = _d14_from_factors(factors)
        amplitude = Fraction(coefficient, mode**SOURCE_SIGMA)
        modes.append(mode)
        amplitudes.append(amplitude)
        phase_offset = (arb(mode) / target).log() - FIRST_ALIAS_ANGULAR_FREQUENCY * arb.pi()
        target_kernel = _kernel(mode, target)
        if not (
            target_kernel < 0
            and abs(phase_offset) < _arb_rational(Fraction(1, 10**8))
        ):
            raise ValueError("frozen mode is not in the first cancelling alias shell")
        mode_records.append(
            {
                "mode": mode,
                "factorization": [[prime, exponent] for prime, exponent in factors],
                "d14": coefficient,
                "tail_coefficient": coefficient,
                "tail_coefficient_is_integral": True,
                "tail_coefficient_saturates_d14": True,
                "normalized_amplitude_exact": _fraction_text(amplitude),
                "first_alias_phase_offset_interval": _interval_text(phase_offset),
                "target_kernel_interval": _interval_text(target_kernel),
                "target_kernel_strictly_negative": target_kernel < 0,
            }
        )

    target_cross = arb(0)
    for mode, amplitude in zip(modes, amplitudes):
        target_cross += _arb_rational(amplitude) * _kernel(mode, target)
    tail_norm_squared = arb(0)
    for left_mode, left_amplitude in zip(modes, amplitudes):
        for right_mode, right_amplitude in zip(modes, amplitudes):
            tail_norm_squared += (
                _arb_rational(left_amplitude * right_amplitude)
                * _kernel(left_mode, right_mode)
            )
    zero_tail_distance = Fraction(1, target**SOURCE_SIGMA)
    response_squared = (
        _arb_rational(zero_tail_distance**2)
        + 2 * _arb_rational(zero_tail_distance) * target_cross
        + tail_norm_squared
    )
    if not (response_squared > 0):
        raise ValueError("alias response square is not positive")
    distance = response_squared.sqrt()
    radius = distance / 2
    zero_tail_radius = _arb_rational(zero_tail_distance / 2)
    improvement = zero_tail_radius - radius
    improvement_lower = _lower_exact(improvement)
    if not improvement_lower > required_improvement:
        raise ValueError("alias witness improvement is too small")
    if not _upper_exact(radius) < zero_tail_distance / 2:
        raise ValueError("alias witness does not strictly improve the zero-tail upper")

    return {
        "target_coordinate": target,
        "prefix_difference": f"plus e_{target}",
        "tail_assignment": (
            "the e_target fibre uses b_n=d_14(n) at every listed mode; "
            "the comparison fibre and all unlisted modes use zero"
        ),
        "tail_class": "integral nonnegative d_14-dominated tails",
        "continuous_convexity_used": False,
        "mode_count": len(modes),
        "mode_records": mode_records,
        "total_normalized_tail_amplitude_exact": _fraction_text(sum(amplitudes, Fraction())),
        "target_cross_inner_product_interval": _interval_text(target_cross),
        "tail_norm_squared_interval": _interval_text(tail_norm_squared),
        "response_squared_interval": _interval_text(response_squared),
        "response_squared_lower_exact": _fraction_text(_lower_exact(response_squared)),
        "response_squared_upper_exact": _fraction_text(_upper_exact(response_squared)),
        "distance_interval": _interval_text(distance),
        "robust_radius_interval": _interval_text(radius),
        "robust_radius_upper_exact": _fraction_text(_upper_exact(radius)),
        "zero_tail_radius_exact": _fraction_text(zero_tail_distance / 2),
        "zero_tail_minus_alias_radius_interval": _interval_text(improvement),
        "improvement_lower_exact": _fraction_text(improvement_lower),
        "improvement_strictly_above_exact": _fraction_text(required_improvement),
        "strictly_below_zero_tail_upper": _upper_exact(radius) < zero_tail_distance / 2,
        "all_modes_outside_prefix": all(mode > SOURCE_MAXIMUM_NORM for mode in modes),
        "all_tail_coefficients_integral_and_legal": True,
        "passed": True,
    }


def _build_prefix_reduction_section(
    inputs: dict[str, object],
    common_box: dict[str, object],
    alias_5: dict[str, object],
) -> dict[str, object]:
    """Certify a finite reduction for any competitor below the alias upper.

    If ``y=A h+t`` is a common-box fibre difference, the orthogonal
    projection onto the first-fifty column span has recovered coordinates
    ``h+e`` with ``|e_n|<=eta_n``.  Gershgorin therefore gives

        ||y||^2 >= (1-q) sum_n ((|h_n|-eta_n)_+)^2/n^4.

    The e5 term nearly consumes the whole alias-witness budget.  One further
    integer prefix difference at n=4 or 6<=n<=14 exceeds that budget.
    """

    q = inputs["q"]
    assert isinstance(q, Fraction)
    records = common_box.get("coordinate_records")
    if not isinstance(records, list) or len(records) != SOURCE_MAXIMUM_NORM:
        raise ValueError("common-box records missing from prefix reduction")
    eta = {
        int(record["coordinate"]): _parse_fraction_limited(
            record["pair_specific_eta_bound_exact"]
        )
        for record in records
        if isinstance(record, dict)
    }
    if len(eta) != SOURCE_MAXIMUM_NORM:
        raise ValueError("prefix reduction eta vector is incomplete")
    alias_upper_squared = _parse_fraction_limited(
        alias_5["response_squared_upper_exact"]
    )
    schur_factors = {}
    for record in records:
        assert isinstance(record, dict)
        n = int(record["coordinate"])
        kappa_squared = _parse_fraction_limited(
            record["certified_bar_kappa_squared_exact"]
        )
        schur_factors[n] = Fraction(n**4, 1) / kappa_squared

    query_2_squared = (1 - eta[2]) ** 2 * schur_factors[2] / 2**4
    query_3_squared = (1 - eta[3]) ** 2 * schur_factors[3] / 3**4
    doubled_5_squared = (2 - eta[5]) ** 2 * schur_factors[5] / 5**4
    query_reduction_passed = all(
        value > alias_upper_squared
        for value in (query_2_squared, query_3_squared, doubled_5_squared)
    )
    if not query_reduction_passed:
        raise ValueError("query-coordinate prefix reduction failed")

    base_energy = (1 - q) * (1 - eta[5]) ** 2 / 5**4
    excluded_indices = (4, *range(6, 15))
    exclusion_records = []
    for n in excluded_indices:
        projection_lower = base_energy + (1 - q) * (1 - eta[n]) ** 2 / n**4
        if projection_lower <= alias_upper_squared:
            raise ValueError("prefix projection budget no longer excludes a frozen index")
        exclusion_records.append(
            {
                "coordinate": n,
                "projection_energy_lower_exact": _fraction_text(
                    projection_lower
                ),
                "strictly_exceeds_alias_response_upper": True,
                "excess_exact": _fraction_text(
                    projection_lower - alias_upper_squared
                ),
            }
        )

    return {
        "scope": (
            "necessary conditions for any four-anchor query-distinct common-box "
            "fibre pair whose distance is no larger than the certified n=5 "
            "integral-alias witness"
        ),
        "projection_energy_formula": (
            "norm(y)^2 >= (1-q)*sum_n ((abs(h_n)-eta_n)_+)^2/n^4"
        ),
        "alias_response_squared_upper_exact": _fraction_text(
            alias_upper_squared
        ),
        "unit_h2_distance_lower_squared_exact": _fraction_text(query_2_squared),
        "unit_h3_distance_lower_squared_exact": _fraction_text(query_3_squared),
        "absolute_h5_at_least_two_lower_squared_exact": _fraction_text(
            doubled_5_squared
        ),
        "query_coordinate_reduction_passed": query_reduction_passed,
        "necessary_query_coordinates": {
            "h_1": 0,
            "h_2": 0,
            "h_3": 0,
            "absolute_h_5": 1,
        },
        "unit_h5_projection_base_energy_lower_exact": _fraction_text(
            base_energy
        ),
        "excluded_nonquery_prefix_coordinates": list(excluded_indices),
        "excluded_coordinate_records": exclusion_records,
        "unresolved_nonquery_prefix_coordinates": list(range(15, 51)),
        "formal_consequence": (
            "any closer competitor must have h_2=h_3=0, abs(h_5)=1, "
            "and no nonzero prefix difference at n=4 or 6<=n<=14; only "
            "nonquery coordinates 15 through 50 remain for a global search"
        ),
        "exact_global_search_completed": False,
        "passed": True,
    }


def build_payload(source_path: Path = DEFAULT_SOURCE_PATH) -> dict[str, object]:
    _check_environment()
    ctx.prec = FORMAL_PRECISION_BITS
    inputs = _source_exact_inputs(source_path)
    common_box = _build_common_box_section(inputs)
    no_tail = _build_no_tail_prefix_section(inputs)
    alias_5 = _build_alias_witness(5, ALIAS_MODES_5, Fraction(22, 10**13))
    alias_50 = _build_alias_witness(50, ALIAS_MODES_50, Fraction(38, 10**14))
    prefix_reduction = _build_prefix_reduction_section(
        inputs, common_box, alias_5
    )
    return {
        "scope": {
            "positive_tail_model": "one common coefficient box 0<=b_k<=d_14(k) in every fibre",
            "common_box_lower_applies_to": [
                "continuous coefficient boxes",
                "their integral-tail subclasses",
            ],
            "alias_upper_witness_uses": "integral endpoint coefficients only",
            "continuous_convex_zonotope_required_for_alias_witness": False,
            "closest_fibre_status": (
                "strictly improved lower and upper brackets; neither target-5 "
                "nor all-fifty exact closest-fibre radius is claimed"
            ),
        },
        "source": {
            "path_basename": EXPECTED_SOURCE_BASENAME,
            "schema": EXPECTED_SOURCE_SCHEMA,
            "file_sha256": inputs["source_file_sha256"],
            "formal_certificate_sha256": EXPECTED_SOURCE_FORMAL_SHA256,
        },
        "parameters": {
            "degree": SOURCE_DEGREE,
            "maximum_norm": SOURCE_MAXIMUM_NORM,
            "sigma": SOURCE_SIGMA,
            "formal_precision_bits": FORMAL_PRECISION_BITS,
            "common_sample_spacing": str(COMMON_SPACING),
            "first_alias_angular_frequency": "10*pi",
            "components": [
                {"observation_time": time, "sample_count": count, "weight": str(weight)}
                for time, count, weight in COMPONENTS
            ],
            "window_coefficients_binary64_hex": list(WINDOW_COEFFICIENT_HEX),
        },
        "common_box_observability": common_box,
        "no_tail_prefix_lattice": no_tail,
        "integral_alias_witnesses": [alias_5, alias_50],
        "four_anchor_prefix_reduction": prefix_reduction,
        "search_provenance": {
            "status": "non-formal discovery metadata; the frozen witnesses are verified independently",
            "center_formula": "round(target*exp(10*pi))",
            "integer_half_width": 1_000_000,
            "ranking": "d_14(n)/n^2",
            "selected_count_per_target": 10,
            "exhaustive_optimality_claimed": False,
        },
        "formal_consequences": {
            "common_box_removes_generic_factor_two": True,
            "all_fifty_bottleneck_is_coordinate_50": True,
            "zero_tail_e5_is_prefix_lattice_optimum": True,
            "zero_tail_e5_is_full_tail_fibre_optimum": False,
            "integral_tails_strictly_improve_e5_upper": True,
            "integral_tails_strictly_improve_e50_upper": True,
            "exact_closest_fibre_value_determined": False,
        },
        "passed": True,
    }


def artifact_document(payload: dict[str, object]) -> dict[str, object]:
    digest = _sha256(payload)
    if digest != PINNED_PAYLOAD_SHA256:
        raise ValueError("rebuilt payload digest differs from the pinned release")
    return {
        "payload": payload,
        "payload_sha256": digest,
        "producer": {
            "python_flint": PINNED_PYTHON_FLINT_VERSION,
            "flint": PINNED_FLINT_VERSION,
        },
        "reproduction_files": {
            "verifier_basename": VERIFIER_PATH.name,
            "verifier_sha256": _sha256_file(VERIFIER_PATH),
            "tests_basename": TESTS_PATH.name,
            "tests_sha256": _sha256_file(TESTS_PATH),
        },
        "schema": SCHEMA,
    }


def verify_artifact(
    artifact: dict[str, object], source_path: Path = DEFAULT_SOURCE_PATH
) -> dict[str, object]:
    if set(artifact) != {
        "payload",
        "payload_sha256",
        "producer",
        "reproduction_files",
        "schema",
    }:
        raise ValueError("artifact has unexpected top-level fields")
    if artifact.get("schema") != SCHEMA:
        raise ValueError("artifact schema mismatch")
    producer = artifact.get("producer")
    if producer != {
        "python_flint": PINNED_PYTHON_FLINT_VERSION,
        "flint": PINNED_FLINT_VERSION,
    }:
        raise ValueError("artifact producer mismatch")
    expected_reproduction = {
        "verifier_basename": VERIFIER_PATH.name,
        "verifier_sha256": _sha256_file(VERIFIER_PATH),
        "tests_basename": TESTS_PATH.name,
        "tests_sha256": _sha256_file(TESTS_PATH),
    }
    if artifact.get("reproduction_files") != expected_reproduction:
        raise ValueError("artifact reproduction-file digests mismatch")
    payload = artifact.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("artifact payload is missing")
    digest = artifact.get("payload_sha256")
    if not isinstance(digest, str) or digest != _sha256(payload):
        raise ValueError("artifact payload digest mismatch")
    if digest != PINNED_PAYLOAD_SHA256:
        raise ValueError("artifact payload digest is not the pinned release")
    expected = build_payload(source_path)
    # Canonical bytes avoid Python's bool/int equality alias (True == 1).
    if _canonical_json(payload) != _canonical_json(expected):
        raise ValueError("artifact payload does not match independent reconstruction")
    return {
        "schema": SCHEMA,
        "payload_sha256": digest,
        "passed": True,
    }


def load_artifact(
    path: Path = DEFAULT_ARTIFACT_PATH,
) -> tuple[dict[str, object], bytes]:
    artifact, raw = _load_json_strict(path, MAX_ARTIFACT_BYTES)
    if raw != _pretty_json(artifact):
        raise ValueError("artifact is not canonical deterministic JSON")
    return artifact, raw


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=DEFAULT_ARTIFACT_PATH)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE_PATH)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--write", type=Path)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    if arguments.emit or arguments.write is not None:
        result = artifact_document(build_payload(arguments.source))
        serialized = _pretty_json(result)
        if arguments.write is not None:
            arguments.write.parent.mkdir(parents=True, exist_ok=True)
            arguments.write.write_bytes(serialized)
            print(
                json.dumps(
                    {
                        "written": str(arguments.write),
                        "payload_sha256": result["payload_sha256"],
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
        else:
            print(serialized.decode("utf-8"), end="")
        return
    artifact, _ = load_artifact(arguments.certificate)
    print(json.dumps(verify_artifact(artifact, arguments.source), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
