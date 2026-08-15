#!/usr/bin/env python3
"""Arb certificate for the canonical full-Segre six-reading design.

The frozen arithmetic model has three labelled prime axes ``(2, 3, 5)``
and four coefficients on each axis.  The six rational acquisition times are
intended to approximate, two rows at a time, the ideal axis phases ``pi/2``
and ``pi`` while keeping the two nontarget axes close to phase zero.

This executable artifact reconstructs all eighteen reduced phases from the
exact rational times and integer windings at 384-bit Arb precision.  It
certifies target errors below ``1/1000``, off-axis errors below ``17/1000``,
and the three explicit algebraic inequalities used by the manuscript's
global full-Segre argument.  The general reconstruction theorem and its
topological lower bound are manuscript mathematics, not mechanized here.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Sequence

import flint
from flint import arb, ctx, fmpq


SCHEMA = "arithmetic-observability-full-segre-v1"
FORMAL_PRECISION_BITS = 384
MIN_PRECISION_BITS = 256
MAX_PRECISION_BITS = 1024
PINNED_PYTHON_FLINT_VERSION = "0.9.0"
PINNED_FLINT_VERSION = "3.6.0"

MAX_ARTIFACT_BYTES = 240_000
MAX_CONTAINER_ITEMS = 256
MAX_JSON_DEPTH = 20
MAX_TEXT_FIELD_LENGTH = 4096
MAX_INTEGER_BITS = 4096
INTERVAL_DISPLAY_DIGITS = 100

PRIMES = (2, 3, 5)
AXIS_COUNT = 3
EXPONENTS_PER_AXIS = 4
READING_COUNT = 6

TIMES = (
    Fraction(90540692, 1000),
    Fraction(220023423, 1000),
    Fraction(27819627, 1000),
    Fraction(94581299, 1000),
    Fraction(18084130, 1000),
    Fraction(75110287, 1000),
)
WINDINGS = (
    (9988, 15831, 23192),
    (24272, 38471, 56359),
    (3069, 4864, 7126),
    (10434, 16537, 24227),
    (1995, 3162, 4632),
    (8286, 13133, 19239),
)
TARGET_AXES = (0, 0, 1, 1, 2, 2)
TARGET_PI_MULTIPLIERS = (
    Fraction(1, 2),
    Fraction(1),
    Fraction(1, 2),
    Fraction(1),
    Fraction(1, 2),
    Fraction(1),
)

TARGET_ERROR_RADIUS = Fraction(1, 1000)
OFF_AXIS_ERROR_RADIUS = Fraction(17, 1000)
PERTURBATION_E_NUMERATOR = 9
PERTURBATION_E_RADICAND = 1202
PERTURBATION_E_DENOMINATOR = 500
PERTURBATION_UPPER = Fraction(5, 8)
FACTOR_FLOOR = Fraction(7901, 10000)
TENSOR_FLOOR = Fraction(4561, 10000)
QUOTIENT_FLOOR = Fraction(291, 12500)
RHO_AMPLIFICATION_UPPER = Fraction(8591, 100)
EPSILON_AMPLIFICATION_UPPER = Fraction(877, 200)
RAW_OPERATOR_NORM_UPPER = Fraction(20)

PACKAGE_ROOT = Path(__file__).resolve().parent
MANUSCRIPT_PATH = PACKAGE_ROOT / "ARITHMETIC_OBSERVABILITY_VI.md"
VERIFIER_PATH = PACKAGE_ROOT / "arithmetic_observability_full_segre.py"
TESTS_PATH = PACKAGE_ROOT / "test_arithmetic_observability_full_segre.py"


def _fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def _parse_fraction_limited(text: object) -> Fraction:
    if not isinstance(text, str) or len(text) > 2048 or "/" not in text:
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
        return Fraction(mantissa * 2**exponent, 1)
    return Fraction(mantissa, 2 ** (-exponent))


def _upper_abs_exact(value: arb) -> Fraction:
    return _exact_dyadic_fraction(abs(value).upper())


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


def _validate_frozen_constants() -> None:
    if len(TIMES) != READING_COUNT or any(type(value) is not Fraction for value in TIMES):
        raise ValueError("times must be six exact Fraction values")
    if len(WINDINGS) != READING_COUNT or any(
        len(row) != AXIS_COUNT or any(type(value) is not int for value in row)
        for row in WINDINGS
    ):
        raise ValueError("windings must be a six by three exact integer array")
    if (
        len(TARGET_AXES) != READING_COUNT
        or any(type(value) is not int or not 0 <= value < AXIS_COUNT for value in TARGET_AXES)
    ):
        raise ValueError("target axes are malformed")
    if len(TARGET_PI_MULTIPLIERS) != READING_COUNT or any(
        type(value) is not Fraction for value in TARGET_PI_MULTIPLIERS
    ):
        raise ValueError("target phase multipliers are malformed")


def _build_phase_design_section() -> dict[str, object]:
    _validate_frozen_constants()
    pi = arb.pi()
    logarithms = tuple(arb(prime).log() for prime in PRIMES)
    records: list[dict[str, object]] = []
    target_upper_bounds: list[Fraction] = []
    off_upper_bounds: list[Fraction] = []
    every_target_passed = True
    every_off_passed = True
    for reading in range(READING_COUNT):
        time = _arb_rational(TIMES[reading])
        target_axis = TARGET_AXES[reading]
        target_multiplier = TARGET_PI_MULTIPLIERS[reading]
        for axis in range(AXIS_COUNT):
            reduced = (
                time * logarithms[axis]
                - 2 * pi * WINDINGS[reading][axis]
            )
            is_target = axis == target_axis
            if is_target:
                expected = _arb_rational(target_multiplier) * pi
                error = reduced - expected
                tolerance = TARGET_ERROR_RADIUS
                target_upper_bounds.append(_upper_abs_exact(error))
            else:
                expected = arb(0)
                error = reduced
                tolerance = OFF_AXIS_ERROR_RADIUS
                off_upper_bounds.append(_upper_abs_exact(error))
            passed = bool(abs(error) < _arb_rational(tolerance))
            if is_target:
                every_target_passed &= passed
            else:
                every_off_passed &= passed
            records.append(
                {
                    "reading_index": reading,
                    "axis_index": axis,
                    "prime": PRIMES[axis],
                    "winding": WINDINGS[reading][axis],
                    "phase_role": "target" if is_target else "off_axis",
                    "target_pi_multiplier_exact": (
                        _fraction_text(target_multiplier) if is_target else "0/1"
                    ),
                    "reduced_phase_interval": _interval_text(reduced),
                    "phase_error_interval": _interval_text(error),
                    "absolute_error_upper_endpoint_exact": _fraction_text(
                        _upper_abs_exact(error)
                    ),
                    "declared_tolerance_exact": _fraction_text(tolerance),
                    "error_certainly_below_declared_tolerance": passed,
                }
            )
    maximum_target = max(target_upper_bounds)
    maximum_off = max(off_upper_bounds)
    target_slack = TARGET_ERROR_RADIUS - maximum_target
    off_slack = OFF_AXIS_ERROR_RADIUS - maximum_off
    passed = bool(
        every_target_passed
        and every_off_passed
        and target_slack > 0
        and off_slack > 0
    )
    return {
        "pi_interval": _interval_text(pi),
        "logarithm_records": [
            {
                "prime": prime,
                "logarithm_interval": _interval_text(logarithm),
            }
            for prime, logarithm in zip(PRIMES, logarithms)
        ],
        "residual_definition": "theta_lj=t_l*log(p_j)-2*pi*n_lj",
        "target_error_definition": "theta_l,target_axis-mu_l*pi",
        "target_error_radius_exact": _fraction_text(TARGET_ERROR_RADIUS),
        "off_axis_error_radius_exact": _fraction_text(OFF_AXIS_ERROR_RADIUS),
        "record_count": len(records),
        "target_record_count": len(target_upper_bounds),
        "off_axis_record_count": len(off_upper_bounds),
        "records": records,
        "maximum_target_absolute_error_upper_endpoint_exact": _fraction_text(
            maximum_target
        ),
        "maximum_off_axis_absolute_error_upper_endpoint_exact": _fraction_text(
            maximum_off
        ),
        "target_error_slack_lower_exact": _fraction_text(target_slack),
        "off_axis_error_slack_lower_exact": _fraction_text(off_slack),
        "every_target_error_certainly_below_radius": every_target_passed,
        "every_off_axis_error_certainly_below_radius": every_off_passed,
        "finite_phase_input_verified": passed,
        "passed": passed,
    }


def _build_analytic_inequalities_section() -> dict[str, object]:
    perturbation = (
        PERTURBATION_E_NUMERATOR
        * arb(PERTURBATION_E_RADICAND).sqrt()
        / PERTURBATION_E_DENOMINATOR
    )
    factor = arb(2).sqrt() - perturbation
    tensor = factor / arb(3).sqrt()
    quotient = factor / (24 * arb(2).sqrt())
    rho_amplification = 2 / quotient
    epsilon_amplification = 2 / tensor
    raw_operator_norm = 8 * arb(6).sqrt()
    perturbation_passed = bool(perturbation < _arb_rational(PERTURBATION_UPPER))
    factor_passed = bool(factor > _arb_rational(FACTOR_FLOOR))
    tensor_passed = bool(tensor > _arb_rational(TENSOR_FLOOR))
    quotient_passed = bool(quotient > _arb_rational(QUOTIENT_FLOOR))
    rho_amplification_passed = bool(
        rho_amplification < _arb_rational(RHO_AMPLIFICATION_UPPER)
    )
    epsilon_amplification_passed = bool(
        epsilon_amplification < _arb_rational(EPSILON_AMPLIFICATION_UPPER)
    )
    raw_operator_norm_passed = bool(
        raw_operator_norm < _arb_rational(RAW_OPERATOR_NORM_UPPER)
    )
    passed = bool(
        perturbation_passed
        and factor_passed
        and tensor_passed
        and quotient_passed
        and rho_amplification_passed
        and epsilon_amplification_passed
        and raw_operator_norm_passed
    )
    return {
        "perturbation_definition": "E=9*sqrt(1202)/500",
        "perturbation_interval": _interval_text(perturbation),
        "perturbation_upper_exact": _fraction_text(PERTURBATION_UPPER),
        "perturbation_certainly_below_upper": perturbation_passed,
        "factor_floor_definition": "sqrt(2)-E",
        "factor_floor_interval": _interval_text(factor),
        "factor_floor_exact": _fraction_text(FACTOR_FLOOR),
        "factor_floor_certainly_above_declared_floor": factor_passed,
        "tensor_floor_definition": "(sqrt(2)-E)/sqrt(3)",
        "tensor_floor_interval": _interval_text(tensor),
        "tensor_floor_exact": _fraction_text(TENSOR_FLOOR),
        "tensor_floor_certainly_above_declared_floor": tensor_passed,
        "quotient_floor_definition": "(sqrt(2)-E)/(24*sqrt(2))",
        "quotient_floor_interval": _interval_text(quotient),
        "quotient_floor_exact": _fraction_text(QUOTIENT_FLOOR),
        "quotient_floor_certainly_above_declared_floor": quotient_passed,
        "rho_amplification_definition": (
            "2/((sqrt(2)-E)/(24*sqrt(2)))"
        ),
        "rho_amplification_interval": _interval_text(rho_amplification),
        "rho_amplification_upper_exact": _fraction_text(
            RHO_AMPLIFICATION_UPPER
        ),
        "rho_amplification_certainly_below_declared_upper": (
            rho_amplification_passed
        ),
        "epsilon_amplification_definition": (
            "2/((sqrt(2)-E)/sqrt(3))"
        ),
        "epsilon_amplification_interval": _interval_text(
            epsilon_amplification
        ),
        "epsilon_amplification_upper_exact": _fraction_text(
            EPSILON_AMPLIFICATION_UPPER
        ),
        "epsilon_amplification_certainly_below_declared_upper": (
            epsilon_amplification_passed
        ),
        "raw_operator_norm_definition": "8*sqrt(6)",
        "raw_operator_norm_interval": _interval_text(raw_operator_norm),
        "raw_operator_norm_upper_exact": _fraction_text(
            RAW_OPERATOR_NORM_UPPER
        ),
        "raw_operator_norm_certainly_below_declared_upper": (
            raw_operator_norm_passed
        ),
        "finite_analytic_inputs_verified": passed,
        "passed": passed,
    }


def build_artifact(precision: int = FORMAL_PRECISION_BITS) -> dict[str, object]:
    _check_environment()
    if type(precision) is not int or not MIN_PRECISION_BITS <= precision <= MAX_PRECISION_BITS:
        raise ValueError("precision must be a bounded canonical integer")
    ctx.prec = precision
    phase = _build_phase_design_section()
    analytic = _build_analytic_inequalities_section()
    passed = bool(phase["passed"] and analytic["passed"])
    payload: dict[str, object] = {
        "parameters": {
            "primes": list(PRIMES),
            "axis_count": AXIS_COUNT,
            "exponents_per_axis": EXPONENTS_PER_AXIS,
            "reading_count": READING_COUNT,
            "times_exact": [_fraction_text(value) for value in TIMES],
            "windings": [list(row) for row in WINDINGS],
            "target_axes": list(TARGET_AXES),
            "target_pi_multipliers_exact": [
                _fraction_text(value) for value in TARGET_PI_MULTIPLIERS
            ],
            "target_error_radius_exact": _fraction_text(TARGET_ERROR_RADIUS),
            "off_axis_error_radius_exact": _fraction_text(OFF_AXIS_ERROR_RADIUS),
        },
        "formal_environment": {
            "precision_bits": precision,
            "python_flint_version": PINNED_PYTHON_FLINT_VERSION,
            "flint_version": PINNED_FLINT_VERSION,
            "interval_backend": "Arb",
        },
        "phase_design": phase,
        "analytic_inequalities": analytic,
        "reproduction_files": {
            "manuscript_basename": MANUSCRIPT_PATH.name,
            "manuscript_sha256": _sha256_file(MANUSCRIPT_PATH),
            "verifier_basename": VERIFIER_PATH.name,
            "verifier_sha256": _sha256_file(VERIFIER_PATH),
            "tests_basename": TESTS_PATH.name,
            "tests_sha256": _sha256_file(TESTS_PATH),
        },
        "finite_certificate_passed": passed,
        "scope": {
            "certifies": (
                "the eighteen finite reduced-phase inclusions and the displayed "
                "algebraic perturbation, factor-floor, tensor-floor, and raw "
                "operator-norm inequalities, together with the quotient and "
                "two amplification consequences"
            ),
            "full_segre_global_reconstruction_theorem_mechanized": False,
            "full_segre_reading_lower_bound_mechanized": False,
            "schedule_optimality_claimed": False,
            "mathematical_model": (
                "three labelled four-state probability factors observed by six "
                "complex harmonic readings"
            ),
        },
    }
    return {"schema": SCHEMA, "payload": payload, "payload_sha256": _sha256(payload)}


def _reject_float(_: str) -> float:
    raise ValueError("artifact contains a forbidden JSON floating-point number")


def _reject_constant(_: str) -> object:
    raise ValueError("artifact contains a forbidden nonfinite JSON constant")


def _parse_json_integer(text: str) -> int:
    if text == "-0":
        raise ValueError("negative-zero JSON integer is noncanonical")
    value = int(text)
    if value.bit_length() > MAX_INTEGER_BITS:
        raise ValueError("JSON integer exceeds the formal size limit")
    return value


def _object_without_duplicates(pairs: Sequence[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("artifact contains a duplicate JSON key")
        result[key] = value
    return result


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
    parsed = tuple(_parse_fraction_limited(value) for value in values)
    if parsed != tuple(expected):
        raise ValueError(f"artifact uses a noncanonical {label}")


def _validate_payload_constants(payload: object) -> None:
    if not isinstance(payload, dict):
        raise ValueError("artifact payload is malformed")
    parameters = payload.get("parameters")
    if not isinstance(parameters, dict):
        raise ValueError("artifact parameters are malformed")
    if parameters.get("primes") != list(PRIMES):
        raise ValueError("artifact uses noncanonical prime axes")
    for key, expected in (
        ("axis_count", AXIS_COUNT),
        ("exponents_per_axis", EXPONENTS_PER_AXIS),
        ("reading_count", READING_COUNT),
    ):
        value = parameters.get(key)
        if type(value) is not int or value != expected:
            raise ValueError(f"artifact uses noncanonical {key}")
    _validate_fraction_list(parameters.get("times_exact"), TIMES, "schedule")
    _validate_fraction_list(
        parameters.get("target_pi_multipliers_exact"),
        TARGET_PI_MULTIPLIERS,
        "target phase multipliers",
    )
    if parameters.get("windings") != [list(row) for row in WINDINGS]:
        raise ValueError("artifact uses noncanonical phase windings")
    if parameters.get("target_axes") != list(TARGET_AXES):
        raise ValueError("artifact uses noncanonical target axes")
    for key, expected in (
        ("target_error_radius_exact", TARGET_ERROR_RADIUS),
        ("off_axis_error_radius_exact", OFF_AXIS_ERROR_RADIUS),
    ):
        if _parse_fraction_limited(parameters.get(key)) != expected:
            raise ValueError(f"artifact uses noncanonical {key}")
    phase = payload.get("phase_design")
    if not isinstance(phase, dict):
        raise ValueError("artifact phase-design section is malformed")
    records = phase.get("records")
    if not isinstance(records, list) or len(records) != READING_COUNT * AXIS_COUNT:
        raise ValueError("artifact phase record list violates the resource cap")
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("artifact phase record must be an object")
        for key in (
            "target_pi_multiplier_exact",
            "absolute_error_upper_endpoint_exact",
            "declared_tolerance_exact",
        ):
            _parse_fraction_limited(record.get(key))
    analytic = payload.get("analytic_inequalities")
    if not isinstance(analytic, dict):
        raise ValueError("artifact analytic section is malformed")
    for key, expected in (
        ("perturbation_upper_exact", PERTURBATION_UPPER),
        ("factor_floor_exact", FACTOR_FLOOR),
        ("tensor_floor_exact", TENSOR_FLOOR),
        ("quotient_floor_exact", QUOTIENT_FLOOR),
        ("rho_amplification_upper_exact", RHO_AMPLIFICATION_UPPER),
        ("epsilon_amplification_upper_exact", EPSILON_AMPLIFICATION_UPPER),
        ("raw_operator_norm_upper_exact", RAW_OPERATOR_NORM_UPPER),
    ):
        if _parse_fraction_limited(analytic.get(key)) != expected:
            raise ValueError(f"artifact uses noncanonical {key}")
    environment = payload.get("formal_environment")
    if not isinstance(environment, dict):
        raise ValueError("artifact environment section is malformed")
    precision = environment.get("precision_bits")
    if type(precision) is not int or precision != FORMAL_PRECISION_BITS:
        raise ValueError("artifact uses a noncanonical formal precision")
    reproduction = payload.get("reproduction_files")
    if not isinstance(reproduction, dict):
        raise ValueError("artifact reproduction-file section is malformed")
    expected_files = {
        "manuscript_basename": MANUSCRIPT_PATH.name,
        "manuscript_sha256": _sha256_file(MANUSCRIPT_PATH),
        "verifier_basename": VERIFIER_PATH.name,
        "verifier_sha256": _sha256_file(VERIFIER_PATH),
        "tests_basename": TESTS_PATH.name,
        "tests_sha256": _sha256_file(TESTS_PATH),
    }
    if reproduction != expected_files:
        raise ValueError("artifact uses noncanonical reproduction-file hashes")


def verify_artifact(path: Path) -> dict[str, object]:
    _check_environment()
    artifact = _load_strict_artifact(path)
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
    _validate_payload_constants(payload)
    expected = build_artifact(FORMAL_PRECISION_BITS)
    if _canonical_json(artifact) != _canonical_json(expected):
        raise ValueError("artifact differs from exact reconstruction")
    return {
        "verified": True,
        "schema": SCHEMA,
        "payload_sha256": digest,
        "phase_record_count": READING_COUNT * AXIS_COUNT,
        "target_record_count": READING_COUNT,
        "off_axis_record_count": READING_COUNT * (AXIS_COUNT - 1),
        "precision_bits": FORMAL_PRECISION_BITS,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--precision", type=int, default=FORMAL_PRECISION_BITS)
    args = parser.parse_args()
    if args.write is not None and args.verify is not None:
        parser.error("--write and --verify are mutually exclusive")
    if args.verify is not None:
        print(json.dumps(verify_artifact(args.verify), indent=2, sort_keys=True))
        return
    artifact = build_artifact(args.precision)
    rendered = _pretty_json(artifact)
    if args.write is None:
        print(rendered.decode("utf-8"), end="")
    else:
        args.write.write_bytes(rendered)


if __name__ == "__main__":
    main()
