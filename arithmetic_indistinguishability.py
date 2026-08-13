#!/usr/bin/env python3
"""Explicit lower bounds and collisions for arithmetic sensing.

Two distinct mechanisms are kept separate:

* nearby one-mode nonnegative integer Dirichlet polynomials have overlapping
  deterministic noise balls at a computable positive radius;
* Perlis' arithmetically equivalent number fields have exactly equal Dedekind
  zeta functions, so aggregate zeta traces cannot identify the field even with
  infinite noiseless data.
"""

from __future__ import annotations

import argparse
import json
import math

import numpy as np

from deterministic_arithmetic_sensing import (
    midpoint_kernel,
    midpoint_times,
    midpoint_weights,
)


def singleton_dirichlet_distance(
    first_norm: int,
    second_norm: int,
    sigma: float,
    observation_time: float,
    sample_count: int,
    window: str = "hann",
) -> float:
    """Distance between ``1+n^-s`` and ``1+k^-s`` response vectors.

    The shared constant coefficient cancels, so this is also the distance
    between coefficient vectors ``e_n`` and ``e_k``.
    """
    if first_norm < 1 or second_norm < 1 or first_norm == second_norm:
        raise ValueError("two distinct positive norms are required")
    if sigma <= 1.0:
        raise ValueError("sigma must exceed one")
    first_amplitude = first_norm ** (-sigma)
    second_amplitude = second_norm ** (-sigma)
    frequency = math.log(first_norm / second_norm)
    correlation = midpoint_kernel(
        frequency, observation_time, sample_count, window=window
    )
    squared_distance = (
        first_amplitude**2
        + second_amplitude**2
        - 2.0 * first_amplitude * second_amplitude * float(np.real(correlation))
    )
    return math.sqrt(max(0.0, squared_distance))


def direct_singleton_dirichlet_distance(
    first_norm: int,
    second_norm: int,
    sigma: float,
    observation_time: float,
    sample_count: int,
    window: str = "hann",
) -> float:
    """Materialized check of :func:`singleton_dirichlet_distance`."""
    times = midpoint_times(sample_count, observation_time)
    weights = midpoint_weights(sample_count, observation_time, window)
    first = first_norm ** (-sigma) * np.exp(-1j * times * math.log(first_norm))
    second = second_norm ** (-sigma) * np.exp(-1j * times * math.log(second_norm))
    return float(np.sqrt(np.dot(weights, np.abs(first - second) ** 2)))


def adversarial_ambiguity_radius(response_distance: float) -> float:
    """Largest common radius certified by the midpoint of two responses."""
    if response_distance < 0:
        raise ValueError("distance must be nonnegative")
    return 0.5 * response_distance


def _is_rational_square_integer(value: int) -> bool:
    if value < 0:
        return False
    root = math.isqrt(value)
    return root * root == value


def perlis_degree_eight_collision(parameter: int = 3) -> dict[str, object]:
    """Metadata for Perlis' explicit degree-eight zeta collision.

    If each of ``+/-a`` and ``+/-2a`` is a nonsquare in Q, the fields generated
    by roots of ``x^8-a`` and ``x^8-16a`` are nonisomorphic but have identical
    Dedekind zeta functions.  This function checks the elementary hypothesis;
    the arithmetic-equivalence conclusion is the cited theorem, not a numerical
    inference made by this program.
    """
    if parameter == 0:
        raise ValueError("parameter must be nonzero")
    candidates = [parameter, -parameter, 2 * parameter, -2 * parameter]
    hypothesis = all(not _is_rational_square_integer(value) for value in candidates)
    if not hypothesis:
        raise ValueError("Perlis' nonsquare hypothesis is not satisfied")
    return {
        "parameter": parameter,
        "first_polynomial": f"x^8 - ({parameter})",
        "second_polynomial": f"x^8 - ({16 * parameter})",
        "degree": 8,
        "nonisomorphic": True,
        "dedekind_zeta_functions_equal": True,
        "aggregate_trace_distance": 0.0,
        "consequence": (
            "no decoder using only the complete Dedekind zeta response can "
            "identify the number field up to isomorphism"
        ),
        "theorem_source": (
            "R. Perlis, On the equation zeta_K(s)=zeta_K'(s), "
            "J. Number Theory 9 (1977), 342-360"
        ),
    }


def analyze(
    maximum_norm: int = 50,
    sigma: float = 2.0,
    observation_time: float = 1_000.0,
    sample_count: int = 5_000,
    window: str = "hann",
) -> dict[str, object]:
    distance = singleton_dirichlet_distance(
        maximum_norm,
        maximum_norm + 1,
        sigma,
        observation_time,
        sample_count,
        window,
    )
    return {
        "finite_coefficient_model": (
            "normalized nonnegative integer Dirichlet polynomials 1+n^-s"
        ),
        "first_norm": maximum_norm,
        "second_norm": maximum_norm + 1,
        "sigma": sigma,
        "observation_time": observation_time,
        "sample_count": sample_count,
        "window": window,
        "weighted_response_distance": distance,
        "adversarial_ambiguity_radius": adversarial_ambiguity_radius(distance),
        "field_isomorphism_collision": perlis_degree_eight_collision(3),
        "scope_warning": (
            "the singleton pair is not asserted to be a pair of Dedekind zeta "
            "functions; the Perlis pair is an exact number-field collision but "
            "has identical coefficient sequences"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--maximum-norm", type=int, default=50)
    parser.add_argument("--sigma", type=float, default=2.0)
    parser.add_argument("--observation-time", type=float, default=1_000.0)
    parser.add_argument("--sample-count", type=int, default=5_000)
    parser.add_argument("--window", choices=["uniform", "hann"], default="hann")
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    print(
        json.dumps(
            analyze(
                arguments.maximum_norm,
                arguments.sigma,
                arguments.observation_time,
                arguments.sample_count,
                arguments.window,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
