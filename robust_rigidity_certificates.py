#!/usr/bin/env python3
"""Robust Stage 5 bounds when adjacent order inequalities have defects.

If a certificate has multipliers y_n>=0 and the observed system only guarantees

    E(n)-E(n+1) <= delta_n,

then its exact endpoint worsens by sum_n y_n delta_n.  This script extracts the
exact rational backbones and reports their noise amplification and missing-data
survival probabilities.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from typing import Mapping

from exact_rigidity_certificates import extract


def certificate_entries(certificate: Mapping[str, object]) -> list[tuple[int, Fraction]]:
    entries = certificate["entries"]
    assert isinstance(entries, list)
    return [
        (int(entry["n"]), Fraction(str(entry["multiplier"])))
        for entry in entries
    ]


def certificate_mass(entries: list[tuple[int, Fraction]]) -> Fraction:
    return sum((multiplier for _, multiplier in entries), Fraction())


def robust_endpoint(
    direction: str,
    endpoint: Fraction,
    entries: list[tuple[int, Fraction]],
    defects: Mapping[int, Fraction],
) -> Fraction:
    budget = sum(
        (multiplier * defects.get(n, Fraction()) for n, multiplier in entries),
        Fraction(),
    )
    if any(defect < 0 for defect in defects.values()):
        raise ValueError("defect bounds must be nonnegative")
    if direction == "lower":
        return endpoint - budget
    if direction == "upper":
        return endpoint + budget
    raise ValueError("direction must be lower or upper")


def analyze_limit(
    limit: int, uniform_defect: Fraction, observation_probabilities: list[float]
) -> dict[str, object]:
    extracted = extract(limit, 3, 10**12)
    certificates = extracted["certificates"]
    lower_certificate, upper_certificate = certificates
    lower_entries = certificate_entries(lower_certificate)
    upper_entries = certificate_entries(upper_certificate)
    lower = Fraction(str(lower_certificate["endpoint"]))
    upper = Fraction(str(upper_certificate["endpoint"]))
    lower_mass = certificate_mass(lower_entries)
    upper_mass = certificate_mass(upper_entries)
    defects = {
        n: uniform_defect for n, _ in [*lower_entries, *upper_entries]
    }
    robust_lower = robust_endpoint("lower", lower, lower_entries, defects)
    robust_upper = robust_endpoint("upper", upper, upper_entries, defects)
    exact_width = upper - lower
    robust_width = robust_upper - robust_lower
    union_support = {n for n, _ in [*lower_entries, *upper_entries]}
    total_mass = lower_mass + upper_mass
    return {
        "limit": limit,
        "exact_interval": [str(lower), str(upper)],
        "exact_width": str(exact_width),
        "uniform_defect": str(uniform_defect),
        "robust_interval": [str(robust_lower), str(robust_upper)],
        "robust_width": str(robust_width),
        "robust_width_decimal": float(robust_width),
        "support_sizes": [len(lower_entries), len(upper_entries)],
        "union_support_size": len(union_support),
        "certificate_masses": [str(lower_mass), str(upper_mass)],
        "total_noise_amplification": str(total_mass),
        "uniform_defect_that_doubles_width": str(exact_width / total_mass),
        "independent_observation_survival": [
            {
                "per_inequality_observation_probability": probability,
                "probability_both_displayed_certificates_are_available": probability
                ** len(union_support),
            }
            for probability in observation_probabilities
        ],
    }


def analyze(limits: list[int], uniform_defect: Fraction) -> dict[str, object]:
    return {
        "defective_order_model": "E(n)-E(n+1)<=delta_n",
        "robust_theorem": (
            "a nonnegative certificate worsens by exactly its weighted defect "
            "budget sum_n y_n delta_n"
        ),
        "normalization": "E(2)=1",
        "runs": [
            analyze_limit(limit, uniform_defect, [0.8, 0.9, 0.95, 0.99])
            for limit in limits
        ],
        "warning": (
            "these are rigorous envelopes for the selected exact certificates; "
            "they need not be optimal among all certificates after noise is introduced"
        ),
    }


def parse_fraction(text: str) -> Fraction:
    value = Fraction(text)
    if value < 0:
        raise argparse.ArgumentTypeError("defect must be nonnegative")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limits", nargs="+", type=int, default=[30, 100, 300, 1000, 3000, 10000])
    parser.add_argument("--uniform-defect", type=parse_fraction, default=Fraction(1, 10_000))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(json.dumps(analyze(args.limits, args.uniform_defect), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
