#!/usr/bin/env python3
"""Proof-producing Arb certificate for prime-box harmonic completion.

The model is the real ``2^a 3^b 5^c`` coefficient box with
``0 <= a,b,c < 4``.  The existing prime-resonant protocols have a
27-dimensional top-interaction kernel.  This checker proves three fixed,
explicit statements.

* Fourteen exact-cent harmonic times observe that real kernel with generalized
  Gram floor ``1/25`` when the added block is RMS-normalized by ``1/sqrt(14)``.
* The same fourteen times, appended to all 48 *raw* resonant readings and
  uniformly RMS-normalized across the resulting 62 complex traces, give a
  full real-source Gram floor ``1/500``.
* A separate 27-time near-DFT schedule observes the complexified kernel.  An
  Arb phase-residual/Frobenius argument certifies a scale-free Gram floor
  ``(24/25)^2`` and an RMS-time Gram floor ``9/4``.

Every time, prime, basis, normalization, and comparison is exact.  Arb
encloses ``log``, ``pi``, and all complex exponentials.  Binary floating point
is not used by any proof decision.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable, Sequence

import flint
from flint import acb, arb, arb_mat, ctx, fmpq


SCHEMA = "arithmetic-observability-harmonic-completion-v1"
FORMAL_PRECISION_BITS = 256
MIN_PRECISION_BITS = 192
MAX_PRECISION_BITS = 1024
MAX_ARTIFACT_BYTES = 200_000
MAX_TEXT_FIELD_LENGTH = 512
MAX_NEAR_DFT_N = 2_000_000

PRIMES = (2, 3, 5)
EXPONENTS_PER_AXIS = 4
RESONANT_SAMPLES_PER_AXIS = 16
COMPLETION_TIMES = tuple(
    Fraction(1279 * multiplier, 100) for multiplier in range(1, 15)
)
RESTRICTED_REAL_FLOOR = Fraction(1, 25)
FULL_RAW_REAL_FLOOR = Fraction(1, 500)

# Exact integer coordinates for W={x in R^4: sum(x)=0}:
# C=(e_0-e_3,e_1-e_3,e_2-e_3).  The top interaction basis is C tensor^3.
ONE_AXIS_CONTRAST_COLUMNS = (
    (1, 0, 0, -1),
    (0, 1, 0, -1),
    (0, 0, 1, -1),
)
ONE_AXIS_CONTRAST_METRIC = (
    (2, 1, 1),
    (1, 2, 1),
    (1, 1, 2),
)

# The 27-time complex schedule is indexed by k=(k1,k2,k3) in {1,2,3}^3.
# Its exact time is 2*pi*(n_k+k1/4)/log(2).  These integers were discovered by
# a finite torus search; the certificate only checks the frozen schedule.
NEAR_DFT_N = {
    1: (
        (1_661_137, 645_383, 1_111_112),
        (568_452, 1_034_181, 1_348_196),
        (1_035_255, 19_501, 255_511),
    ),
    2: (
        (37_928, 1_833_426, 587_953),
        (1_756_495, 740_741, 976_751),
        (663_810, 977_825, 1_443_554),
    ),
    3: (
        (996_252, 1_232_262, 1_775_996),
        (1_463_055, 1_699_065, 683_311),
        (370_370, 606_380, 1_150_114),
    ),
}
NEAR_DFT_FROBENIUS_UPPER = Fraction(81, 500)
NEAR_DFT_SCALE_FREE_SINGULAR_LOWER = Fraction(3919, 4000)
NEAR_DFT_SCALE_FREE_GRAM_FLOOR = Fraction(24**2, 25**2)
NEAR_DFT_RMS_GRAM_FLOOR = Fraction(9, 4)

ENTRY_RADIUS_CAP = Fraction(1, 10**60)
DETERMINANT_RELATIVE_RADIUS_CAP = Fraction(1, 10**8)

_K_INDICES = tuple(itertools.product(range(3), repeat=3))
_AMBIENT_STATES = tuple(itertools.product(range(4), repeat=3))


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _parse_fraction_limited(text: str) -> Fraction:
    if not isinstance(text, str) or len(text) > 64 or "/" not in text:
        raise ValueError("fraction is not a bounded canonical string")
    numerator_text, denominator_text = text.split("/", 1)
    value = Fraction(int(numerator_text), int(denominator_text))
    if value.denominator <= 0:
        raise ValueError("fraction denominator must be positive")
    if (
        value.numerator.bit_length() > 64
        or value.denominator.bit_length() > 64
    ):
        raise ValueError("fraction exceeds the formal integer limit")
    if _fraction_text(value) != text:
        raise ValueError("fraction string is not reduced and canonical")
    return value


def _arb_rational(value: Fraction | int) -> arb:
    if isinstance(value, int):
        return arb(value)
    return arb(fmpq(value.numerator, value.denominator))


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _interval_text(value: arb, digits: int = 24) -> str:
    return value.str(digits, radius=True, more=True)


def _exact_dyadic_fraction(value: arb) -> Fraction:
    if not value.is_exact():
        raise ValueError("expected an exact Arb endpoint")
    mantissa, exponent = map(int, value.man_exp())
    if exponent >= 0:
        return Fraction(mantissa * 2**exponent, 1)
    return Fraction(mantissa, 2 ** (-exponent))


def _exact_arb_integer(value: arb) -> int:
    exact = _exact_dyadic_fraction(value)
    if exact.denominator != 1:
        raise ArithmeticError("Arb value is exact but not integral")
    return exact.numerator


def _matrix_payload(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [list(row) for row in matrix]


def _source_basis_descriptor() -> dict[str, object]:
    descriptor = {
        "ambient_state_order": "lexicographic product(range(4), repeat=3)",
        "restricted_coordinate_order": (
            "lexicographic product(range(3), repeat=3)"
        ),
        "one_axis_integer_columns": [
            list(column) for column in ONE_AXIS_CONTRAST_COLUMNS
        ],
        "one_axis_metric": _matrix_payload(ONE_AXIS_CONTRAST_METRIC),
        "tensor_rule": "B = C tensor C tensor C",
        "source_metric_rule": "S = (C^T C) tensor (C^T C) tensor (C^T C)",
    }
    return {
        **descriptor,
        "descriptor_sha256": _sha256(descriptor),
    }


def _validate_source_basis_exactly() -> None:
    columns = ONE_AXIS_CONTRAST_COLUMNS
    if any(sum(column) != 0 for column in columns):
        raise AssertionError("a declared contrast does not lie in the mean-zero space")
    computed = tuple(
        tuple(sum(left[a] * right[a] for a in range(4)) for right in columns)
        for left in columns
    )
    if computed != ONE_AXIS_CONTRAST_METRIC:
        raise AssertionError("the declared exact source metric is inconsistent")
    if len(set(columns)) != 3:
        raise AssertionError("the declared contrast columns are not distinct")


def restricted_source_metric() -> arb_mat:
    """Return the exact 27-by-27 Gram of ``C tensor C tensor C``."""

    _validate_source_basis_exactly()
    result = arb_mat(27, 27)
    for row, left in enumerate(_K_INDICES):
        for column, right in enumerate(_K_INDICES):
            result[row, column] = (
                ONE_AXIS_CONTRAST_METRIC[left[0]][right[0]]
                * ONE_AXIS_CONTRAST_METRIC[left[1]][right[1]]
                * ONE_AXIS_CONTRAST_METRIC[left[2]][right[2]]
            )
    return result


def _restricted_metric_exact_payload() -> list[list[int]]:
    return [
        [
            ONE_AXIS_CONTRAST_METRIC[left[0]][right[0]]
            * ONE_AXIS_CONTRAST_METRIC[left[1]][right[1]]
            * ONE_AXIS_CONTRAST_METRIC[left[2]][right[2]]
            for right in _K_INDICES
        ]
        for left in _K_INDICES
    ]


def _completion_restricted_rows() -> list[list[acb]]:
    """Return the 14-by-27 complex response in exact contrast coordinates."""

    logs = tuple(arb(prime).log() for prime in PRIMES)
    scale = arb(len(COMPLETION_TIMES)).sqrt()
    rows: list[list[acb]] = []
    for exact_time in COMPLETION_TIMES:
        time = _arb_rational(exact_time)
        one_axis: list[list[acb]] = []
        for logarithm in logs:
            node = acb(0, -time * logarithm).exp()
            powers = (acb(1), node, node * node, node * node * node)
            one_axis.append([powers[index] - powers[3] for index in range(3)])
        rows.append(
            [
                one_axis[0][a] * one_axis[1][b] * one_axis[2][c] / scale
                for a, b, c in _K_INDICES
            ]
        )
    return rows


def _raw_full_rows() -> list[list[acb]]:
    """Return all 62 raw trace rows with uniform RMS weight ``1/62``."""

    logs = tuple(arb(prime).log() for prime in PRIMES)
    scale = arb(62).sqrt()
    rows: list[list[acb]] = []

    # At a p_j-resonant time, the alpha_j phase is exactly one.  Removing it
    # algebraically avoids a dependency loss from evaluating log(p_j)/log(p_j)
    # as two correlated Arb balls.
    for axis in range(3):
        for sample in range(RESONANT_SAMPLES_PER_AXIS):
            row: list[acb] = []
            for alpha in _AMBIENT_STATES:
                ratio_sum = sum(
                    (
                        alpha[other] * logs[other] / logs[axis]
                        for other in range(3)
                        if other != axis
                    ),
                    arb(0),
                )
                phase = -2 * arb.pi() * sample * ratio_sum
                row.append(acb(0, phase).exp() / scale)
            rows.append(row)

    for exact_time in COMPLETION_TIMES:
        time = _arb_rational(exact_time)
        row = []
        for alpha in _AMBIENT_STATES:
            frequency = sum(
                (alpha[axis] * logs[axis] for axis in range(3)), arb(0)
            )
            row.append(acb(0, -time * frequency).exp() / scale)
        rows.append(row)

    if len(rows) != 62:
        raise AssertionError("the declared full raw operator does not have 62 rows")
    return rows


def _real_source_gram(rows: Sequence[Sequence[acb]]) -> arb_mat:
    """Return ``Re(A^* A)`` for a complex observation of real sources."""

    if not rows or not rows[0]:
        raise ValueError("observation rows must be nonempty")
    dimension = len(rows[0])
    if any(len(row) != dimension for row in rows):
        raise ValueError("observation rows have inconsistent lengths")
    gram = arb_mat(dimension, dimension)
    for row_index in range(dimension):
        for column_index in range(row_index + 1):
            value = sum(
                (
                    row[row_index].conjugate() * row[column_index]
                    for row in rows
                ),
                acb(0),
            ).real
            gram[row_index, column_index] = value
            gram[column_index, row_index] = value
    return gram


def _principal_block(matrix: arb_mat, dimension: int) -> arb_mat:
    return arb_mat(
        [
            [matrix[row, column] for column in range(dimension)]
            for row in range(dimension)
        ]
    )


def _radius_audit(values: Iterable[arb], cap: Fraction) -> dict[str, object]:
    cap_ball = _arb_rational(cap)
    count = 0
    all_below = True
    for value in values:
        count += 1
        all_below = all_below and bool(value.rad() < cap_ball)
    return {
        "quantity_count": count,
        "radius_cap_exact": _fraction_text(cap),
        "every_radius_strictly_below_cap": all_below,
    }


def _certify_real_generalized_floor(
    gram: arb_mat,
    metric: arb_mat,
    floor: Fraction,
) -> dict[str, object]:
    """Certify ``gram - floor*metric`` positive definite by Sylvester."""

    if (
        gram.nrows() != gram.ncols()
        or metric.nrows() != gram.nrows()
        or metric.ncols() != gram.ncols()
    ):
        raise ValueError("Gram and source metric dimensions do not match")
    shifted = gram - metric * _arb_rational(floor)
    determinants = [
        _principal_block(shifted, dimension).det()
        for dimension in range(1, shifted.nrows() + 1)
    ]
    signs = [1 if bool(value > 0) else -1 if bool(value < 0) else 0 for value in determinants]
    intervals = [_interval_text(value) for value in determinants]
    relative_radius_passes = [
        bool(
            value > 0
            and value.rad() / value.lower()
            < _arb_rational(DETERMINANT_RELATIVE_RADIUS_CAP)
        )
        for value in determinants
    ]
    matrix_radius_audit = _radius_audit(
        (
            shifted[row, column]
            for row in range(shifted.nrows())
            for column in range(shifted.ncols())
        ),
        ENTRY_RADIUS_CAP,
    )
    passed = bool(
        all(sign == 1 for sign in signs)
        and all(relative_radius_passes)
        and matrix_radius_audit["every_radius_strictly_below_cap"]
    )
    return {
        "method": "direct Arb Sylvester test on Re(A^* A) - L S",
        "dimension": shifted.nrows(),
        "floor_exact": _fraction_text(floor),
        "leading_principal_minor_signs": signs,
        "leading_principal_minor_intervals": intervals,
        "leading_principal_minor_intervals_sha256": _sha256(intervals),
        "final_minor_lower_endpoint_exact": _fraction_text(
            _exact_dyadic_fraction(determinants[-1].lower())
        ),
        "shift_matrix_radius_audit": matrix_radius_audit,
        "determinant_relative_radius_cap_exact": _fraction_text(
            DETERMINANT_RELATIVE_RADIUS_CAP
        ),
        "every_determinant_relative_radius_strictly_below_cap": all(
            relative_radius_passes
        ),
        "every_leading_principal_minor_certainly_positive": all(
            sign == 1 for sign in signs
        ),
        "passed": passed,
    }


def _near_dft_schedule_payload() -> list[dict[str, object]]:
    return [
        {
            "target_phase_indices": [k1, k2, k3],
            "n": NEAR_DFT_N[k1][k2 - 1][k3 - 1],
            "time_rule": "2*pi*(n+k1/4)/log(2)",
        }
        for k1, k2, k3 in itertools.product((1, 2, 3), repeat=3)
    ]


def _validate_near_dft_basis_and_schedule_exactly() -> None:
    """Check the finite Fourier algebra and bounded integer schedule exactly."""

    fourth_roots = ((1, 0), (0, 1), (-1, 0), (0, -1))
    for target in (1, 2, 3):
        for column in (1, 2, 3):
            real = 0
            imaginary = 0
            for exponent in range(4):
                root = fourth_roots[(exponent * (column - target)) % 4]
                real += root[0]
                imaginary += root[1]
            expected = (4, 0) if target == column else (0, 0)
            if (real, imaginary) != expected:
                raise AssertionError("the declared Fourier contrasts are inconsistent")

    if set(NEAR_DFT_N) != {1, 2, 3}:
        raise AssertionError("the near-DFT schedule has the wrong outer indices")
    values: list[int] = []
    for k1 in (1, 2, 3):
        matrix = NEAR_DFT_N[k1]
        if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
            raise AssertionError("the near-DFT integer table is not 3 by 3")
        values.extend(value for row in matrix for value in row)
    if (
        len(values) != 27
        or len(set(values)) != 27
        or any(type(value) is not int for value in values)
        or any(not 0 <= value <= MAX_NEAR_DFT_N for value in values)
    ):
        raise AssertionError("the near-DFT integer schedule violates its exact cap")


def _certify_near_dft_completion() -> dict[str, object]:
    """Certify the complexified-kernel schedule by phase residuals.

    The complex Fourier contrasts are

        q_l(a) = exp(2*pi*i*a*l/4)/2,  l=1,2,3.

    At the ideal target phases the restricted 27-by-27 response is exactly
    ``8 I``.  Projection is contractive and ``|exp(-ix)-1| <= |x|``; hence
    the enumerated phase residual sum bounds the Frobenius perturbation.
    """

    _validate_near_dft_basis_and_schedule_exactly()
    logs = tuple(arb(prime).log() for prime in PRIMES)
    total_squared_error = arb(0)
    residual_records: list[dict[str, object]] = []
    all_nearest_windings_certified = True

    for k1, k2, k3 in itertools.product((1, 2, 3), repeat=3):
        targets = (k1, k2, k3)
        n = NEAR_DFT_N[k1][k2 - 1][k3 - 1]
        residuals: list[arb] = []
        windings: list[int] = []
        cycle_intervals: list[str] = []
        for axis in range(3):
            if axis == 0:
                unreduced_cycles = arb(n)
            else:
                unreduced_cycles = (
                    (arb(n) + _arb_rational(Fraction(k1, 4)))
                    * logs[axis]
                    / logs[0]
                    - _arb_rational(Fraction(targets[axis], 4))
                )
            winding_ball = (
                unreduced_cycles + _arb_rational(Fraction(1, 2))
            ).floor()
            winding = _exact_arb_integer(winding_ball)
            cycle_residual = unreduced_cycles - winding
            nearest = bool(
                cycle_residual > _arb_rational(Fraction(-1, 2))
                and cycle_residual < _arb_rational(Fraction(1, 2))
            )
            all_nearest_windings_certified &= nearest
            residuals.append(2 * arb.pi() * cycle_residual)
            windings.append(winding)
            cycle_intervals.append(_interval_text(cycle_residual, 18))

        row_squared_error = arb(0)
        for alpha in _AMBIENT_STATES:
            phase_error = sum(
                (alpha[axis] * residuals[axis] for axis in range(3)),
                arb(0),
            )
            row_squared_error += phase_error**2
        total_squared_error += row_squared_error
        residual_records.append(
            {
                "target_phase_indices": [k1, k2, k3],
                "n": n,
                "nearest_integer_windings": windings,
                "cycle_residual_intervals": cycle_intervals,
                "row_error_squared_upper_interval": _interval_text(
                    row_squared_error
                ),
            }
        )

    frobenius_error = total_squared_error.sqrt()
    frobenius_passed = bool(
        frobenius_error < _arb_rational(NEAR_DFT_FROBENIUS_UPPER)
    )
    singular_implication = (
        Fraction(8) - NEAR_DFT_FROBENIUS_UPPER
        == Fraction(3919, 500)
        and Fraction(3919, 500) / 8
        == NEAR_DFT_SCALE_FREE_SINGULAR_LOWER
        and NEAR_DFT_SCALE_FREE_SINGULAR_LOWER
        > Fraction(24, 25)
        and Fraction(3919, 500) ** 2 / 27
        > NEAR_DFT_RMS_GRAM_FLOOR
    )
    passed = bool(
        all_nearest_windings_certified
        and frobenius_passed
        and singular_implication
    )
    return {
        "method": (
            "Arb phase residuals plus projection contraction, "
            "|exp(-ix)-1|<=|x|, a Frobenius bound, and Weyl's inequality"
        ),
        "complex_source_basis": (
            "q_l(a)=exp(2*pi*i*a*l/4)/2 for l=1,2,3, tensor cubed"
        ),
        "ideal_restricted_matrix": "8 I_27",
        "exact_fourier_basis_and_ideal_matrix_verified": True,
        "schedule": _near_dft_schedule_payload(),
        "schedule_sha256": _sha256(_near_dft_schedule_payload()),
        "residual_records": residual_records,
        "residual_records_sha256": _sha256(residual_records),
        "all_nearest_integer_windings_certified": (
            all_nearest_windings_certified
        ),
        "frobenius_error_interval": _interval_text(frobenius_error),
        "frobenius_error_upper_exact": _fraction_text(
            NEAR_DFT_FROBENIUS_UPPER
        ),
        "frobenius_error_certainly_below_upper": frobenius_passed,
        "scale_free_normalization": "restricted matrix divided by exact 8",
        "scale_free_singular_lower_exact": _fraction_text(
            NEAR_DFT_SCALE_FREE_SINGULAR_LOWER
        ),
        "scale_free_gram_floor_exact": _fraction_text(
            NEAR_DFT_SCALE_FREE_GRAM_FLOOR
        ),
        "rms_time_normalization": "each of 27 complex rows divided by sqrt(27)",
        "rms_time_gram_floor_exact": _fraction_text(
            NEAR_DFT_RMS_GRAM_FLOOR
        ),
        "exact_rational_implications_verified": singular_implication,
        "passed": passed,
    }


def build_payload(precision_bits: int = FORMAL_PRECISION_BITS) -> dict[str, object]:
    if type(precision_bits) is not int:
        raise ValueError("precision must be a canonical integer")
    if not MIN_PRECISION_BITS <= precision_bits <= MAX_PRECISION_BITS:
        raise ValueError("precision is outside the formal resource limits")
    _validate_source_basis_exactly()
    _validate_near_dft_basis_and_schedule_exactly()

    source_metric_exact = _restricted_metric_exact_payload()
    completion_time_text = [_fraction_text(value) for value in COMPLETION_TIMES]
    parameters = {
        "primes": list(PRIMES),
        "exponents_per_axis": EXPONENTS_PER_AXIS,
        "ambient_real_dimension": 64,
        "real_top_interaction_dimension": 27,
        "completion_time_rule": "t_m=1279*m/100 for 1<=m<=14",
        "completion_times_exact": completion_time_text,
        "completion_times_sha256": _sha256(completion_time_text),
        "resonant_time_rule": "2*pi*m/log(p_j) for 0<=m<16 and j=1,2,3",
        "raw_resonant_complex_trace_count": 48,
        "raw_completion_complex_trace_count": 14,
        "raw_total_complex_trace_count": 62,
    }

    with ctx.workprec(precision_bits):
        restricted_gram = _real_source_gram(_completion_restricted_rows())
        restricted_certificate = _certify_real_generalized_floor(
            restricted_gram,
            restricted_source_metric(),
            RESTRICTED_REAL_FLOOR,
        )
        full_raw_gram = _real_source_gram(_raw_full_rows())
        ambient_metric = arb_mat(
            [
                [1 if row == column else 0 for column in range(64)]
                for row in range(64)
            ]
        )
        full_raw_certificate = _certify_real_generalized_floor(
            full_raw_gram,
            ambient_metric,
            FULL_RAW_REAL_FLOOR,
        )
        near_dft_certificate = _certify_near_dft_completion()

    overall = bool(
        restricted_certificate["passed"]
        and full_raw_certificate["passed"]
        and near_dft_certificate["passed"]
    )
    return {
        "parameters": parameters,
        "source_basis": {
            **_source_basis_descriptor(),
            "restricted_metric_sha256": _sha256(source_metric_exact),
            "exact_zero_sum_and_metric_identities_verified": True,
        },
        "restricted_real_completion": {
            "source": "real top interaction W tensor W tensor W",
            "observation_norm": (
                "(1/14) sum_{m=1}^{14} |F_c(1279*m/100)|^2"
            ),
            "complex_row_weight_exact": "1/14",
            "source_metric": "S=B^T B in exact integer contrast coordinates",
            "certificate": restricted_certificate,
            "consequence": (
                "the added block is injective on the old real kernel and its "
                "worst-case squared amplification is strictly below 25"
            ),
        },
        "full_uniform_raw_real_operator": {
            "source": "all real coefficient arrays on the 64-state prime box",
            "observation_norm": (
                "uniform RMS over all 62 raw complex traces: (1/62) sum |y_l|^2"
            ),
            "complex_row_weight_exact": "1/62",
            "preprocessing": "none; no inverse-Vandermonde calibration is used",
            "source_metric": "ambient Euclidean I_64",
            "certificate": full_raw_certificate,
            "consequence": (
                "the 48 raw resonant readings plus 14 raw completion readings "
                "are injective on real sources and have squared amplification "
                "strictly below 500"
            ),
        },
        "complex_near_dft_completion": near_dft_certificate,
        "implementation": {
            "arb_precision_bits": precision_bits,
            "python_flint_version": flint.__version__,
            "all_transcendentals_enclosed_by_arb": True,
            "binary64_used_for_proof_decisions": False,
            "strict_interval_comparisons_only": True,
        },
        "formal_scope": {
            "claim": (
                "finite exact-time harmonic completion for the declared "
                "2^a 3^b 5^c box and declared RMS noise geometries"
            ),
            "clock_jitter_certified": False,
            "off_box_tail_certified": False,
            "complex_full_raw_62-trace_floor_certified": False,
            "schedule_optimality_claimed": False,
            "arb_scope": (
                "computer-assisted interval proof conditional on the Arb/FLINT "
                "implementation; not a formal-proof-assistant derivation"
            ),
        },
        "overall_passed": overall,
    }


def build_artifact(precision_bits: int = FORMAL_PRECISION_BITS) -> dict[str, object]:
    payload = build_payload(precision_bits)
    return {
        "schema": SCHEMA,
        "payload": payload,
        "payload_sha256": _sha256(payload),
    }


def _validate_stored_shape(artifact: dict[str, object]) -> None:
    if not isinstance(artifact, dict):
        raise ValueError("artifact must be a JSON object")
    if set(artifact) != {"schema", "payload", "payload_sha256"}:
        raise ValueError("artifact has unexpected top-level fields")
    if artifact["schema"] != SCHEMA:
        raise ValueError("unsupported harmonic-completion schema")
    digest = artifact["payload_sha256"]
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(character not in "0123456789abcdef" for character in digest)
    ):
        raise ValueError("payload digest is not canonical lowercase SHA-256")
    payload = artifact["payload"]
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    expected_payload_keys = {
        "parameters",
        "source_basis",
        "restricted_real_completion",
        "full_uniform_raw_real_operator",
        "complex_near_dft_completion",
        "implementation",
        "formal_scope",
        "overall_passed",
    }
    if set(payload) != expected_payload_keys:
        raise ValueError("payload has unexpected fields")
    parameters = payload.get("parameters")
    if not isinstance(parameters, dict):
        raise ValueError("parameters must be an object")
    times = parameters.get("completion_times_exact")
    if not isinstance(times, list) or len(times) != 14:
        raise ValueError("completion time list violates the resource cap")
    parsed_times = tuple(_parse_fraction_limited(value) for value in times)
    if parsed_times != COMPLETION_TIMES:
        raise ValueError("artifact uses a noncanonical completion schedule")
    stored_primes = parameters.get("primes")
    if (
        not isinstance(stored_primes, list)
        or len(stored_primes) != 3
        or not all(type(prime) is int for prime in stored_primes)
        or stored_primes != [2, 3, 5]
    ):
        raise ValueError("artifact uses noncanonical prime axes")
    if (
        type(parameters.get("exponents_per_axis")) is not int
        or parameters["exponents_per_axis"] != EXPONENTS_PER_AXIS
    ):
        raise ValueError("exponent count is not a canonical integer")
    implementation = payload.get("implementation")
    if not isinstance(implementation, dict):
        raise ValueError("implementation field must be an object")
    precision = implementation.get("arb_precision_bits")
    if type(precision) is not int or not MIN_PRECISION_BITS <= precision <= MAX_PRECISION_BITS:
        raise ValueError("stored precision violates the formal resource cap")
    if precision != FORMAL_PRECISION_BITS:
        raise ValueError("stored artifact does not use the pinned formal precision")

    near_dft = payload.get("complex_near_dft_completion")
    if not isinstance(near_dft, dict):
        raise ValueError("near-DFT certificate must be an object")
    schedule = near_dft.get("schedule")
    residuals = near_dft.get("residual_records")
    if not isinstance(schedule, list) or len(schedule) != 27:
        raise ValueError("near-DFT schedule violates the resource cap")
    if not isinstance(residuals, list) or len(residuals) != 27:
        raise ValueError("near-DFT residual trace violates the resource cap")
    for expected, stored in zip(_near_dft_schedule_payload(), schedule):
        if not isinstance(stored, dict) or set(stored) != {
            "target_phase_indices",
            "n",
            "time_rule",
        }:
            raise ValueError("near-DFT schedule record has unexpected fields")
        targets = stored.get("target_phase_indices")
        if (
            not isinstance(targets, list)
            or len(targets) != 3
            or not all(type(value) is int for value in targets)
            or type(stored.get("n")) is not int
            or not 0 <= stored["n"] <= MAX_NEAR_DFT_N
        ):
            raise ValueError("near-DFT schedule record violates exact type caps")
        if stored != expected:
            raise ValueError("artifact uses a noncanonical near-DFT schedule")
    for record in residuals:
        if not isinstance(record, dict):
            raise ValueError("near-DFT residual record must be an object")
        cycles = record.get("cycle_residual_intervals")
        windings = record.get("nearest_integer_windings")
        if (
            not isinstance(cycles, list)
            or len(cycles) != 3
            or any(
                not isinstance(value, str)
                or len(value) > MAX_TEXT_FIELD_LENGTH
                for value in cycles
            )
            or not isinstance(windings, list)
            or len(windings) != 3
            or not all(type(value) is int for value in windings)
        ):
            raise ValueError("near-DFT residual record violates exact type caps")

    for section_name, dimension in (
        ("restricted_real_completion", 27),
        ("full_uniform_raw_real_operator", 64),
    ):
        section = payload.get(section_name)
        if not isinstance(section, dict) or not isinstance(section.get("certificate"), dict):
            raise ValueError("a real certificate section is malformed")
        certificate = section["certificate"]
        signs = certificate.get("leading_principal_minor_signs")
        intervals = certificate.get("leading_principal_minor_intervals")
        if not isinstance(signs, list) or len(signs) != dimension:
            raise ValueError("principal-minor sign list violates the resource cap")
        if not isinstance(intervals, list) or len(intervals) != dimension:
            raise ValueError("principal-minor interval list violates the resource cap")
        if any(
            not isinstance(value, str) or len(value) > MAX_TEXT_FIELD_LENGTH
            for value in intervals
        ):
            raise ValueError("principal-minor interval text exceeds the resource cap")

    if len(_canonical_json(artifact)) > MAX_ARTIFACT_BYTES:
        raise ValueError("artifact exceeds the serialized resource cap")


def verify_artifact(artifact: dict[str, object]) -> dict[str, object]:
    """Recompute the fixed interval proof and reject any semantic tampering."""

    _validate_stored_shape(artifact)
    payload = artifact["payload"]
    if artifact["payload_sha256"] != _sha256(payload):
        raise ValueError("payload digest mismatch")
    expected = build_artifact(FORMAL_PRECISION_BITS)
    if _canonical_json(artifact) != _canonical_json(expected):
        raise ValueError("artifact does not equal independent Arb reconstruction")
    return {
        "verified": True,
        "schema": SCHEMA,
        "payload_sha256": artifact["payload_sha256"],
        "restricted_real_floor_exact": _fraction_text(RESTRICTED_REAL_FLOOR),
        "full_raw_real_floor_exact": _fraction_text(FULL_RAW_REAL_FLOOR),
        "near_dft_scale_free_gram_floor_exact": _fraction_text(
            NEAR_DFT_SCALE_FREE_GRAM_FLOOR
        ),
        "overall_passed": expected["payload"]["overall_passed"],
    }


def _strict_object_from_pairs(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    """Build one JSON object while rejecting ambiguous duplicate keys."""

    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _reject_nonfinite_json_constant(value: str) -> object:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def _parse_canonical_json_integer(value: str) -> int:
    if value == "-0":
        raise ValueError("negative-zero JSON integer is noncanonical")
    return int(value)


def _reject_json_float(value: str) -> object:
    raise ValueError(f"JSON floating-point number is forbidden: {value}")


def _read_artifact(path: Path) -> dict[str, object]:
    if path.stat().st_size > MAX_ARTIFACT_BYTES:
        raise ValueError("artifact file exceeds the serialized resource cap")
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_strict_object_from_pairs,
        parse_int=_parse_canonical_json_integer,
        parse_float=_reject_json_float,
        parse_constant=_reject_nonfinite_json_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("artifact JSON root must be an object")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--write", type=Path)
    action.add_argument("--verify", type=Path)
    parser.add_argument(
        "--precision-bits", type=int, default=FORMAL_PRECISION_BITS
    )
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()

    if args.verify is not None:
        result = verify_artifact(_read_artifact(args.verify))
    else:
        result = build_artifact(args.precision_bits)
    rendered = json.dumps(
        result, indent=None if args.compact else 2, sort_keys=True
    ) + "\n"
    if args.write is not None:
        args.write.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
