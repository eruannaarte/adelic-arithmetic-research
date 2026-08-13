#!/usr/bin/env python3
"""Build or independently check the Arithmetic Sensing V MPFR certificate."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import time
from fractions import Fraction
from pathlib import Path
from typing import Sequence

import gmpy2
import numpy as np

from arithmetic_sensing_iv import REFERENCE_COEFFICIENTS
from deterministic_arithmetic_sensing import deterministic_coefficient_bounds
from fixed_degree_arithmetic_sensing import (
    fixed_degree_divisor_coefficients_sieve,
    fixed_degree_tail_l1_from_sieve,
)
from optimized_arithmetic_quadrature import (
    centered_cosine_response,
    cosine_window_gram,
)
from arithmetic_sensing_v import design_for_time
from verified_mellin_certificate import (
    binary64_fractions,
    exact_dyadic_convolution_power,
    fraction_to_float_upper,
    verified_mellin_bin_count,
    verified_one_factor_log_bins,
    verified_remote_tail_bounds,
)


SCHEMA = "arithmetic-sensing-v-verified-mellin-v1"
DEFAULT_ARTIFACT = (
    Path(__file__).resolve().parent
    / "certificates"
    / "arithmetic_sensing_v_verified_mellin.json"
)
REFERENCE_COMPLETE_BOUNDS = {
    5: 0.007750682334570224,
    8: 0.3762810835558778,
    9: 1.136788856603709,
}


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _payload_digest(certificate: dict[str, object]) -> str:
    return hashlib.sha256(_canonical_json(certificate).encode()).hexdigest()


def _formal_projection(certificate: dict[str, object]) -> dict[str, object]:
    """Remove explicitly hybrid observations from the signed formal payload."""
    formal = copy.deepcopy(certificate)
    degrees = formal.get("degrees")
    if isinstance(degrees, list):
        for entry in degrees:
            if isinstance(entry, dict):
                entry.pop("hybrid_complete_report", None)
    return formal


def _hybrid_complete_report(
    degree: int,
    remote_numerators: Sequence[int],
    remote_scale_bits: int,
    maximum_norm: int,
    truncation: int,
) -> dict[str, object]:
    """Combine the proved remote upper with the pre-existing finite audit.

    Only the remote component is an MPFR/dyadic formal certificate.  The
    million-term finite kernel evaluation and Gram inversion remain binary64
    computations and are labelled accordingly in the returned payload.
    """
    design = design_for_time()
    coefficients = fixed_degree_divisor_coefficients_sieve(truncation, degree)
    base_remainder = fixed_degree_tail_l1_from_sieve(
        truncation, degree, 2.0, coefficients
    )
    envelope = np.empty(maximum_norm, dtype=float)
    finite = np.empty(maximum_norm, dtype=float)
    for target_index, target_norm in enumerate(range(1, maximum_norm + 1)):
        subtotal = 0.0
        for start in range(maximum_norm + 1, truncation + 1, 100_000):
            stop = min(truncation + 1, start + 100_000)
            norms = np.arange(start, stop, dtype=float)
            weights = coefficients[start:stop] * norms ** (-2.0)
            frequencies = np.log(target_norm / norms)
            subtotal += float(
                np.dot(
                    weights,
                    np.abs(centered_cosine_response(frequencies, design)),
                )
            )
        remote = fraction_to_float_upper(
            Fraction(remote_numerators[target_index], 1 << remote_scale_bits)
        )
        finite[target_index] = subtotal
        envelope[target_index] = subtotal + remote
    gram = cosine_window_gram(maximum_norm, design)
    bounds = deterministic_coefficient_bounds(gram, 2.0, envelope)
    maximum_index = int(np.argmax(bounds))
    complete = float(bounds[maximum_index])
    reference = REFERENCE_COMPLETE_BOUNDS.get(degree)
    return {
        "status": "hybrid: formal remote tail; binary64 finite sum and Gram inverse",
        "global_l1_remainder_before_kernel_decay": base_remainder,
        "largest_finite_million_term_component": float(np.max(finite)),
        "worst_target_norm": maximum_index + 1,
        "worst_complete_coefficient_bound": complete,
        "integer_rounding_certificate_under_hybrid_audit": complete < 0.5,
        "arithmetic_sensing_v_reference_bound": reference,
        "change_from_reference": None if reference is None else complete - reference,
    }


def build_certificate(
    degrees: Sequence[int] = (5, 8, 9),
    maximum_norm: int = 50,
    truncation: int = 1_000_000,
    bin_width: Fraction = Fraction(1, 100),
    dyadic_bin_bits: int = 96,
    output_bits: int = 128,
    mpfr_precision: int = 192,
    include_hybrid_report: bool = True,
) -> dict[str, object]:
    """Recompute the complete compact certificate payload from first principles."""
    if not degrees or any(degree < 1 for degree in degrees):
        raise ValueError("at least one positive degree is required")
    observation_time = 1_000
    sample_count = 5_000
    alias_periods = 2
    bin_count = verified_mellin_bin_count(
        maximum_norm,
        observation_time,
        sample_count,
        alias_periods,
        bin_width,
        mpfr_precision,
    )
    bins = verified_one_factor_log_bins(
        bin_count,
        bin_width,
        2,
        truncation,
        dyadic_bin_bits,
        mpfr_precision,
    )
    window = binary64_fractions(REFERENCE_COEFFICIENTS)
    degree_payloads = []
    for degree in degrees:
        convolution = exact_dyadic_convolution_power(bins, degree)
        remote = verified_remote_tail_bounds(
            bins,
            convolution,
            truncation,
            maximum_norm,
            observation_time,
            sample_count,
            window,
            2,
            output_bits,
        )
        entry: dict[str, object] = {
            "degree": degree,
            "convolution_scale_bits": convolution.scale_bits,
            "convolution_coefficient_bytes": convolution.coefficient_bytes,
            "convolution_sha256": convolution.sha256,
            "remote_output_scale_bits": remote.scale_bits,
            "remote_target_numerators": [str(value) for value in remote.numerators],
            "remote_sha256": remote.sha256,
            "remote_upper_at_target_1": str(remote.upper_fraction(1)),
            "remote_upper_at_target_10": str(remote.upper_fraction(10)),
            "remote_upper_at_target_50": str(remote.upper_fraction(50)),
        }
        if include_hybrid_report:
            entry["hybrid_complete_report"] = _hybrid_complete_report(
                degree,
                remote.numerators,
                remote.scale_bits,
                maximum_norm,
                truncation,
            )
        degree_payloads.append(entry)
    return {
        "scope": (
            "formal MPFR/dyadic upper certificate for k>truncation; the "
            "reported complete bound remains hybrid where explicitly labelled"
        ),
        "parameters": {
            "maximum_norm": maximum_norm,
            "sigma": 2,
            "observation_time": observation_time,
            "sample_count": sample_count,
            "truncation": truncation,
            "alias_periods_before_elementary_tail": alias_periods,
            "bin_width": str(bin_width),
            "bin_count": bin_count,
            "maximum_log": str(bins.maximum_log),
            "mpfr_precision_bits": mpfr_precision,
            "one_factor_dyadic_scale_bits": dyadic_bin_bits,
            "remote_output_scale_bits": output_bits,
            "window_coefficients_binary64_hex": [
                float(value).hex() for value in REFERENCE_COEFFICIENTS
            ],
        },
        "one_factor": {
            "sha256": bins.sha256,
            "boundary_precision_maximum_bits": bins.boundary_precision_maximum,
            "dyadic_numerator_sum": str(sum(bins.numerators)),
            "dyadic_scale_bits": bins.scale_bits,
        },
        "degrees": degree_payloads,
    }


def artifact_document(certificate: dict[str, object]) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "producer": {
            "gmpy2": gmpy2.version(),
            "mpfr": gmpy2.mpfr_version(),
        },
        "formal_certificate_sha256": _payload_digest(
            _formal_projection(certificate)
        ),
        "certificate": certificate,
    }


def verify_artifact(
    artifact: dict[str, object], recomputed: dict[str, object]
) -> dict[str, object]:
    if artifact.get("schema") != SCHEMA:
        raise ValueError("unknown certificate schema")
    stored = artifact.get("certificate")
    if not isinstance(stored, dict):
        raise ValueError("artifact has no certificate object")
    stored_formal = _formal_projection(stored)
    recomputed_formal = _formal_projection(recomputed)
    stored_digest = artifact.get("formal_certificate_sha256")
    if stored_digest != _payload_digest(stored_formal):
        raise ValueError("stored formal certificate hash is invalid")
    recomputed_digest = _payload_digest(recomputed_formal)
    if stored_digest != recomputed_digest or stored_formal != recomputed_formal:
        raise ValueError("recomputed formal certificate does not match the artifact")
    return {
        "verified": True,
        "schema": SCHEMA,
        "formal_certificate_sha256": recomputed_digest,
        "runtime": {
            "gmpy2": gmpy2.version(),
            "mpfr": gmpy2.mpfr_version(),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--certificate", type=Path, default=DEFAULT_ARTIFACT
    )
    parser.add_argument(
        "--degrees",
        default="5,8,9",
        help="comma-separated degrees; must match the artifact when checking",
    )
    parser.add_argument(
        "--emit",
        action="store_true",
        help="print a newly computed artifact instead of checking a file",
    )
    parser.add_argument(
        "--skip-hybrid-report",
        action="store_true",
        help="omit the binary64 finite/Gram continuation report",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    degrees = tuple(int(value) for value in arguments.degrees.split(","))
    started = time.perf_counter()
    certificate = build_certificate(
        degrees=degrees,
        include_hybrid_report=not arguments.skip_hybrid_report,
    )
    if arguments.emit:
        result: dict[str, object] = artifact_document(certificate)
    else:
        with arguments.certificate.open(encoding="utf-8") as handle:
            artifact = json.load(handle)
        result = verify_artifact(artifact, certificate)
        result["elapsed_seconds"] = time.perf_counter() - started
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
