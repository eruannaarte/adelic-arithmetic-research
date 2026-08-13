#!/usr/bin/env python3
"""Recover an unknown rank-one unit lattice from unlabelled noisy samples.

Scalar projections have the form z_i=k_i R+noise_i with unknown positive
integers k_i.  In exact data the generated lattice spacing is gcd(k_i)R, so the
fundamental regulator R is identifiable precisely when gcd(k_i)=1.
"""

from __future__ import annotations

import argparse
import json
import math
from functools import reduce
from typing import Sequence

import numpy as np

from inverse_regulator_recovery import TRUE_REGULATOR


def exact_observed_spacing(powers: Sequence[int], regulator: float) -> float:
    if not powers or any(power <= 0 for power in powers):
        raise ValueError("positive powers are required")
    return reduce(math.gcd, powers) * regulator


def recover_lattice_spacing(
    observations: np.ndarray,
    maximum_multiplier: int,
    noise_sigma: float,
    tolerance_multiplier: float = 3.0,
) -> dict[str, object]:
    if observations.ndim != 1 or len(observations) == 0:
        raise ValueError("a nonempty observation vector is required")
    if maximum_multiplier < 1 or noise_sigma < 0:
        raise ValueError("invalid multiplier bound or noise")
    absolute = np.sort(np.abs(observations))
    tolerance = max(tolerance_multiplier * noise_sigma, 1e-12)
    candidates: list[tuple[float, float, np.ndarray]] = []
    for observation in absolute:
        for multiplier in range(1, maximum_multiplier + 1):
            spacing = observation / multiplier
            if spacing <= 0:
                continue
            integers = np.rint(absolute / spacing).astype(int)
            if np.any(integers < 1) or np.any(integers > maximum_multiplier):
                continue
            # Refit the common spacing after assigning integer multipliers.
            fitted = float(np.dot(integers, absolute) / np.dot(integers, integers))
            residual = float(np.sqrt(np.mean((absolute - integers * fitted) ** 2)))
            if residual <= tolerance:
                candidates.append((fitted, residual, integers))
    if not candidates:
        raise RuntimeError("no lattice spacing fits the supplied noise tolerance")
    # Exact submultiples always fit a lattice. The primitive lattice is the
    # largest compatible spacing, subject to the known multiplier bound.
    spacing, residual, integers = max(candidates, key=lambda item: item[0])
    return {
        "recovered_spacing": spacing,
        "assigned_multipliers": integers.tolist(),
        "root_mean_square_residual": residual,
        "accepted_tolerance": tolerance,
        "candidate_count": len(candidates),
    }


def simulate(
    powers: Sequence[int], noise_sigma: float, maximum_multiplier: int, seed: int
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    observations = np.asarray(powers, dtype=float) * TRUE_REGULATOR + rng.normal(
        0.0, noise_sigma, len(powers)
    )
    recovered = recover_lattice_spacing(
        observations, maximum_multiplier, noise_sigma
    )
    target_spacing = exact_observed_spacing(powers, TRUE_REGULATOR)
    relative_error = abs(recovered["recovered_spacing"] - target_spacing) / target_spacing
    return {
        "powers": list(powers),
        "power_gcd": reduce(math.gcd, powers),
        "noise_sigma": noise_sigma,
        "fundamental_regulator": TRUE_REGULATOR,
        "identifiable_observed_spacing": target_spacing,
        "fundamental_regulator_identifiable": reduce(math.gcd, powers) == 1,
        "relative_spacing_error": relative_error,
        "success_within_five_percent": relative_error < 0.05,
        "seed": seed,
        **recovered,
    }


def success_rate(
    powers: Sequence[int], noise_sigma: float, trials: int, seed_offset: int
) -> dict[str, object]:
    runs = [
        simulate(powers, noise_sigma, max(powers), seed_offset + trial)
        for trial in range(trials)
    ]
    return {
        "powers": list(powers),
        "power_gcd": reduce(math.gcd, powers),
        "noise_sigma": noise_sigma,
        "trials": trials,
        "successes_within_five_percent": sum(
            run["success_within_five_percent"] for run in runs
        ),
        "success_rate": sum(run["success_within_five_percent"] for run in runs)
        / trials,
        "mean_relative_spacing_error": float(
            np.mean([run["relative_spacing_error"] for run in runs])
        ),
    }


def analyze(trials: int) -> dict[str, object]:
    primitive = [6, 10, 15]
    imprimitive = [6, 10, 14]
    noise_levels = [0.0, 0.0005, 0.002, 0.01, 0.03]
    return {
        "exact_theorem": (
            "unlabelled exact samples k_i R generate spacing gcd(k_i)R; "
            "the fundamental regulator is identifiable iff gcd(k_i)=1"
        ),
        "primitive_sample": {
            "powers": primitive,
            "gcd": reduce(math.gcd, primitive),
            "noise_study": [
                success_rate(primitive, noise, trials, index * 10_000)
                for index, noise in enumerate(noise_levels)
            ],
        },
        "imprimitive_sample": {
            "powers": imprimitive,
            "gcd": reduce(math.gcd, imprimitive),
            "exact_observed_spacing": exact_observed_spacing(
                imprimitive, TRUE_REGULATOR
            ),
            "warning": (
                "these samples identify 2R, not R; without a primitive sample "
                "or external bound the sublattice is indistinguishable"
            ),
        },
        "algorithm": (
            "bounded integer assignment plus least-squares refit, choosing the "
            "largest spacing compatible with the supplied noise tolerance"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=500)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(json.dumps(analyze(args.trials), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
