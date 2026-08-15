#!/usr/bin/env python3
"""Exact certificate kernel for the prime-box observability model.

The formal layer uses only integers and ``fractions.Fraction``.  Floating
point is used only by the optional raw-Vandermonde diagnostic; it is never
part of certificate verification.
"""

from __future__ import annotations

import argparse
import cmath
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Iterable, Sequence


SCHEMA = "arithmetic-observability-prime-box-v1"
MAX_FORMAL_DIMENSION = 256
MAX_FORMAL_PRIME = 1_000_000
MAX_FORMAL_WEIGHT_BITS = 256


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def _fraction_text(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def _parse_fraction(text: str) -> Fraction:
    numerator, denominator = text.split("/", 1)
    return Fraction(int(numerator), int(denominator))


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def validate_parameters(
    primes: Sequence[int], s: int, weights: Sequence[Fraction]
) -> None:
    if not isinstance(s, int) or isinstance(s, bool):
        raise ValueError("s must be an integer")
    if s < 2:
        raise ValueError("s must be at least two")
    if len(primes) < 2:
        raise ValueError("at least two prime axes are required")
    if len(primes) > 6 or s ** len(primes) > MAX_FORMAL_DIMENSION:
        raise ValueError("declared prime box exceeds the formal dimension limit")
    if any(
        not isinstance(p, int)
        or isinstance(p, bool)
        or p > MAX_FORMAL_PRIME
        for p in primes
    ):
        raise ValueError("prime axes exceed the formal integer limit")
    if len(set(primes)) != len(primes) or not all(_is_prime(p) for p in primes):
        raise ValueError("prime axes must be distinct primes")
    if len(weights) != len(primes):
        raise ValueError("one protocol weight is required per prime")
    if any(weight <= 0 for weight in weights):
        raise ValueError("all protocol weights must be positive")
    if any(
        weight.numerator.bit_length() > MAX_FORMAL_WEIGHT_BITS
        or weight.denominator.bit_length() > MAX_FORMAL_WEIGHT_BITS
        for weight in weights
    ):
        raise ValueError("protocol weight exceeds the formal rational limit")
    if sum(weights, Fraction(0)) != 1:
        raise ValueError("protocol weights must sum exactly to one")


def exponent_box(r: int, s: int) -> list[tuple[int, ...]]:
    return list(itertools.product(range(s), repeat=r))


def marginal_projector(
    r: int, s: int, axis: int
) -> list[list[Fraction]]:
    """Return M_axis^* M_axis for M=s^(-1/2) times marginal summation."""

    if not 0 <= axis < r:
        raise ValueError("axis out of range")
    states = exponent_box(r, s)
    projector: list[list[Fraction]] = []
    for alpha in states:
        row: list[Fraction] = []
        reduced_alpha = alpha[:axis] + alpha[axis + 1 :]
        for beta in states:
            reduced_beta = beta[:axis] + beta[axis + 1 :]
            row.append(Fraction(1, s) if reduced_alpha == reduced_beta else Fraction(0))
        projector.append(row)
    return projector


def pooled_gram(
    primes: Sequence[int], s: int, weights: Sequence[Fraction]
) -> list[list[Fraction]]:
    validate_parameters(primes, s, weights)
    r = len(primes)
    dimension = s**r
    gram = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    for axis, weight in enumerate(weights):
        projector = marginal_projector(r, s, axis)
        for row in range(dimension):
            for column in range(dimension):
                gram[row][column] += weight * projector[row][column]
    return gram


def _matrix_payload(matrix: Sequence[Sequence[Fraction]]) -> list[list[str]]:
    return [[_fraction_text(value) for value in row] for row in matrix]


def predicted_spectrum(
    weights: Sequence[Fraction], s: int
) -> list[dict[str, object]]:
    """Return the exact ANOVA eigenspaces, one entry per subset of axes."""

    r = len(weights)
    entries: list[dict[str, object]] = []
    for size in range(r + 1):
        for subset in itertools.combinations(range(r), size):
            subset_set = set(subset)
            eigenvalue = sum(
                (weights[j] for j in range(r) if j not in subset_set), Fraction(0)
            )
            entries.append(
                {
                    "mean_zero_axes": list(subset),
                    "eigenvalue": _fraction_text(eigenvalue),
                    "multiplicity": (s - 1) ** size,
                }
            )
    return entries


def _tensor_collision(r: int, s: int) -> list[int]:
    factor = (1, -1) + (0,) * (s - 2)
    return [math.prod(factor[a] for a in alpha) for alpha in exponent_box(r, s)]


def _matvec(
    matrix: Sequence[Sequence[Fraction]], vector: Sequence[Fraction]
) -> list[Fraction]:
    return [
        sum((entry * value for entry, value in zip(row, vector)), Fraction(0))
        for row in matrix
    ]


def _squared_form(
    matrix: Sequence[Sequence[Fraction]], vector: Sequence[Fraction]
) -> Fraction:
    image = _matvec(matrix, vector)
    return sum((x * y for x, y in zip(vector, image)), Fraction(0))


def _validate_exact_eigenbasis(
    gram: Sequence[Sequence[Fraction]], weights: Sequence[Fraction], s: int
) -> str:
    """Check a rational tensor eigenbasis and return its canonical digest."""

    r = len(weights)
    factor_basis: list[list[int]] = [[1] * s]
    for index in range(s - 1):
        contrast = [0] * s
        contrast[index] = 1
        contrast[-1] = -1
        factor_basis.append(contrast)
    states = exponent_box(r, s)
    eigenbasis: list[list[int]] = []
    for choices in itertools.product(range(s), repeat=r):
        vector = [
            math.prod(factor_basis[choice][alpha] for choice, alpha in zip(choices, state))
            for state in states
        ]
        mean_zero_axes = {axis for axis, choice in enumerate(choices) if choice != 0}
        eigenvalue = sum(
            (weights[axis] for axis in range(r) if axis not in mean_zero_axes),
            Fraction(0),
        )
        image = _matvec(gram, [Fraction(value) for value in vector])
        expected = [eigenvalue * value for value in vector]
        if image != expected:
            raise AssertionError("declared tensor vector is not an exact Gram eigenvector")
        eigenbasis.append(vector)
    if len(eigenbasis) != s**r:
        raise AssertionError("tensor eigenbasis has the wrong size")
    return _sha256(eigenbasis)


def pure_distance_squared(
    alpha: Sequence[int], beta: Sequence[int], s: int, weights: Sequence[Fraction]
) -> Fraction:
    if len(alpha) != len(beta) or len(alpha) != len(weights):
        raise ValueError("state and weight dimensions do not match")
    differing = {j for j, (a, b) in enumerate(zip(alpha, beta)) if a != b}
    if not differing:
        return Fraction(0)
    if len(differing) == 1:
        hidden_axis = next(iter(differing))
        visible_weight = 1 - weights[hidden_axis]
    else:
        visible_weight = Fraction(1)
    return Fraction(2, s) * visible_weight


def build_payload(
    primes: Sequence[int] = (2, 3, 5),
    s: int = 4,
    weights: Sequence[Fraction] | None = None,
) -> dict[str, object]:
    r = len(primes)
    if weights is None:
        weights = tuple(Fraction(1, r) for _ in range(r))
    weights = tuple(weights)
    validate_parameters(primes, s, weights)

    gram = pooled_gram(primes, s, weights)
    spectrum = predicted_spectrum(weights, s)
    eigenbasis_sha256 = _validate_exact_eigenbasis(gram, weights, s)
    dimension = s**r
    kernel_dimension = (s - 1) ** r
    positive_floor = min(weights)
    collision = _tensor_collision(r, s)
    collision_fraction = [Fraction(value, s**r) for value in collision]
    if any(_matvec(gram, collision_fraction)):
        raise AssertionError("the declared full-interaction collision is observable")

    p_plus = [2 + value for value in collision]
    p_minus = [2 - value for value in collision]
    probability_denominator = 2 * dimension
    if min(p_plus + p_minus) < 0:
        raise AssertionError("collision probabilities are not nonnegative")
    if sum(p_plus) != probability_denominator or sum(p_minus) != probability_denominator:
        raise AssertionError("collision probabilities do not sum to one")

    adjacent_alpha = (0,) * r
    adjacent_beta = (1,) + (0,) * (r - 1)
    remote_beta = tuple(1 for _ in range(r))

    return {
        "parameters": {
            "primes": list(primes),
            "exponents_per_axis": s,
            "weights": [_fraction_text(weight) for weight in weights],
            "samples_per_resonant_protocol": s ** (r - 1),
            "trace_line_real_part": 0,
            "output_calibration": "inverse-Vandermonde then root-s normalized marginal",
        },
        "exact_geometry": {
            "ambient_dimension": dimension,
            "observable_rank": dimension - kernel_dimension,
            "common_kernel_dimension": kernel_dimension,
            "simplex_tangent_quotient_dimension": dimension - kernel_dimension - 1,
            "positive_spectral_floor": _fraction_text(positive_floor),
            "minimax_noise_amplification_squared": _fraction_text(1 / positive_floor),
            "uniform_weight_e_optimal_floor": _fraction_text(Fraction(1, r)),
            "spectrum_by_anova_subspace": spectrum,
            "gram_sha256": _sha256(_matrix_payload(gram)),
            "exact_tensor_eigenbasis_sha256": eigenbasis_sha256,
        },
        "pure_monomial_geometry": {
            "one_axis_distance_squared_example": _fraction_text(
                pure_distance_squared(adjacent_alpha, adjacent_beta, s, weights)
            ),
            "two_or_more_axis_distance_squared_example": _fraction_text(
                pure_distance_squared(adjacent_alpha, remote_beta, s, weights)
            ),
            "rule": (
                "2/s times total weight, except the sole differing-axis "
                "protocol contributes zero"
            ),
        },
        "exact_probability_collision": {
            "vector_rule": "h=(1,-1,0,...,0) tensor-power r",
            "p_plus_numerators_sha256": _sha256(p_plus),
            "p_minus_numerators_sha256": _sha256(p_minus),
            "numerator_range": [min(p_plus + p_minus), max(p_plus + p_minus)],
            "common_denominator": probability_denominator,
            "difference_l2_squared": _fraction_text(Fraction(2**r, s ** (2 * r))),
            "difference_total_variation": _fraction_text(Fraction(2 ** (r - 1), s**r)),
            "collision_vector_sha256": _sha256(collision),
            "pooled_distance_squared": "0/1",
        },
        "formal_scope": {
            "raw_sample_noise_geometry_certified": False,
            "vandermonde_node_distinctness": "proved symbolically by unique factorization",
            "claim": "exact equivalence and calibrated quotient geometry on the finite prime box",
        },
    }


def build_artifact(
    primes: Sequence[int] = (2, 3, 5),
    s: int = 4,
    weights: Sequence[Fraction] | None = None,
) -> dict[str, object]:
    payload = build_payload(primes, s, weights)
    return {"schema": SCHEMA, "payload": payload, "payload_sha256": _sha256(payload)}


def verify_artifact(artifact: dict[str, object]) -> dict[str, object]:
    if set(artifact) != {"schema", "payload", "payload_sha256"}:
        raise ValueError("artifact has unexpected top-level fields")
    if artifact["schema"] != SCHEMA:
        raise ValueError("unsupported schema")
    payload = artifact["payload"]
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    if artifact["payload_sha256"] != _sha256(payload):
        raise ValueError("payload digest mismatch")
    parameters = payload.get("parameters")
    if not isinstance(parameters, dict):
        raise ValueError("missing parameters")
    raw_primes = parameters.get("primes")
    raw_s = parameters.get("exponents_per_axis")
    raw_weights = parameters.get("weights")
    if (
        not isinstance(raw_primes, list)
        or not all(type(prime) is int for prime in raw_primes)
        or type(raw_s) is not int
        or not isinstance(raw_weights, list)
        or not all(isinstance(weight, str) for weight in raw_weights)
    ):
        raise ValueError("parameters do not use canonical JSON types")
    primes = tuple(raw_primes)
    s = raw_s
    weights = tuple(_parse_fraction(text) for text in raw_weights)
    expected = build_payload(primes, s, weights)
    if _canonical_json(payload) != _canonical_json(expected):
        raise ValueError("artifact does not equal exact reconstruction")
    return {
        "verified": True,
        "schema": SCHEMA,
        "payload_sha256": artifact["payload_sha256"],
        "ambient_dimension": expected["exact_geometry"]["ambient_dimension"],
        "observable_rank": expected["exact_geometry"]["observable_rank"],
        "common_kernel_dimension": expected["exact_geometry"][
            "common_kernel_dimension"
        ],
    }


def raw_vandermonde_diagnostics(
    primes: Sequence[int] = (2, 3, 5), s: int = 4
) -> list[dict[str, float | int]]:
    """Descriptive binary64 conditioning of the uncalibrated trace samples."""

    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - optional diagnostic only
        raise RuntimeError("NumPy is required only for raw diagnostics") from exc
    diagnostics: list[dict[str, float | int]] = []
    r = len(primes)
    for axis, prime in enumerate(primes):
        other_axes = [j for j in range(r) if j != axis]
        beta = list(itertools.product(range(s), repeat=r - 1))
        nodes = []
        for exponents in beta:
            ratio = sum(
                exponent * math.log(primes[j]) / math.log(prime)
                for exponent, j in zip(exponents, other_axes)
            )
            nodes.append(cmath.exp(-2j * math.pi * ratio))
        count = len(nodes)
        vandermonde = np.asarray(
            [[node**m for node in nodes] for m in range(count)], dtype=complex
        ) / math.sqrt(count)
        singular_values = np.linalg.svd(vandermonde, compute_uv=False)
        diagnostics.append(
            {
                "prime": prime,
                "nodes": count,
                "sigma_min": float(singular_values[-1]),
                "sigma_max": float(singular_values[0]),
                "condition_number": float(singular_values[0] / singular_values[-1]),
            }
        )
    return diagnostics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--raw-diagnostics", action="store_true")
    args = parser.parse_args()

    if args.verify is not None:
        artifact = json.loads(args.verify.read_text(encoding="utf-8"))
        print(json.dumps(verify_artifact(artifact), indent=2, sort_keys=True))
        return

    artifact = build_artifact()
    if args.raw_diagnostics:
        artifact["descriptive_binary64_raw_vandermonde"] = raw_vandermonde_diagnostics()
    rendered = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    if args.write is not None:
        args.write.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
