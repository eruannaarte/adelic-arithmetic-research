#!/usr/bin/env python3
"""Cross-mode interactions as countermodels to Euler factorization.

For two modes p,q add the repulsive energy

    J N_p N_q,  J=log(r), r>=1.

At integer beta, finite occupation sums are exact rational numbers.  When
r>1, every jointly occupied state is suppressed and the joint partition no
longer equals the product of its free local factors.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction

import numpy as np


def exact_truncated_joint_partition(
    prime: int,
    other_prime: int,
    integer_beta: int,
    interaction_base: int,
    maximum_occupation: int,
) -> Fraction:
    if min(prime, other_prime, integer_beta, interaction_base) < 1:
        raise ValueError("positive parameters are required")
    if maximum_occupation < 0:
        raise ValueError("maximum occupation must be nonnegative")
    return sum(
        (
            Fraction(
                1,
                prime ** (integer_beta * first)
                * other_prime ** (integer_beta * second)
                * interaction_base ** (integer_beta * first * second),
            )
            for first in range(maximum_occupation + 1)
            for second in range(maximum_occupation + 1)
        ),
        Fraction(),
    )


def exact_truncated_free_partition(
    prime: int, other_prime: int, integer_beta: int, maximum_occupation: int
) -> Fraction:
    left = sum(
        (Fraction(1, prime ** (integer_beta * value)) for value in range(maximum_occupation + 1)),
        Fraction(),
    )
    right = sum(
        (Fraction(1, other_prime ** (integer_beta * value)) for value in range(maximum_occupation + 1)),
        Fraction(),
    )
    return left * right


def exact_infinite_free_partition(
    prime: int, other_prime: int, integer_beta: int
) -> Fraction:
    p_power = prime**integer_beta
    q_power = other_prime**integer_beta
    return Fraction(p_power, p_power - 1) * Fraction(q_power, q_power - 1)


def numeric_joint_statistics(
    prime: int,
    other_prime: int,
    beta: float,
    interaction_strength: float,
    maximum_occupation: int = 100,
) -> dict[str, float]:
    occupations = np.arange(maximum_occupation + 1, dtype=float)
    first, second = np.meshgrid(occupations, occupations, indexing="ij")
    energy = (
        first * math.log(prime)
        + second * math.log(other_prime)
        + interaction_strength * first * second
    )
    weights = np.exp(-beta * energy)
    partition = float(np.sum(weights))
    probabilities = weights / partition
    mean_first = float(np.sum(first * probabilities))
    mean_second = float(np.sum(second * probabilities))
    covariance = float(
        np.sum(first * second * probabilities) - mean_first * mean_second
    )
    free_partition = 1.0 / (
        (1.0 - prime ** (-beta)) * (1.0 - other_prime ** (-beta))
    )
    log_factorization_defect = math.log(partition / free_partition)
    # At one beta the aggregate scalar can always be mimicked by changing the
    # second free energy while keeping the first local factor fixed.
    effective_boltzmann = 1.0 - 1.0 / (
        partition * (1.0 - prime ** (-beta))
    )
    effective_second_energy = -math.log(effective_boltzmann) / beta
    return {
        "joint_partition": partition,
        "free_partition": free_partition,
        "log_factorization_defect": log_factorization_defect,
        "mean_first_occupation": mean_first,
        "mean_second_occupation": mean_second,
        "mixed_occupation_covariance": covariance,
        "effective_second_energy_from_one_scalar_trace": effective_second_energy,
        "true_second_energy": math.log(other_prime),
    }


def analyze(
    prime: int,
    other_prime: int,
    integer_beta: int,
    interaction_base: int,
    maximum_occupation: int,
) -> dict[str, object]:
    interacting = exact_truncated_joint_partition(
        prime,
        other_prime,
        integer_beta,
        interaction_base,
        maximum_occupation,
    )
    free_truncated = exact_truncated_free_partition(
        prime, other_prime, integer_beta, maximum_occupation
    )
    free_infinite = exact_infinite_free_partition(prime, other_prime, integer_beta)
    exact_deficit_lower_bound = free_truncated - interacting
    omitted_free_tail = free_infinite - free_truncated
    betas = [0.7, 1.0, 1.5, 2.0, 3.0]
    interaction_strength = math.log(interaction_base)
    statistics = [
        {
            "beta": beta,
            **numeric_joint_statistics(
                prime, other_prime, beta, interaction_strength
            ),
        }
        for beta in betas
    ]
    return {
        "modes": [prime, other_prime],
        "interaction": f"log({interaction_base}) N_{prime} N_{other_prime}",
        "integer_beta": integer_beta,
        "maximum_occupation": maximum_occupation,
        "exact_truncated_interacting_partition": str(interacting),
        "exact_truncated_free_partition": str(free_truncated),
        "strict_factorization_deficit_lower_bound": str(exact_deficit_lower_bound),
        "strict_factorization_deficit_lower_bound_decimal": float(
            exact_deficit_lower_bound
        ),
        "free_omitted_tail_upper_bound": str(omitted_free_tail),
        "interacting_infinite_partition_interval": [
            float(interacting),
            float(interacting + omitted_free_tail),
        ],
        "beta_study": statistics,
        "identifiability_boundary": (
            "one aggregate partition value is reproduced exactly by a free "
            "two-mode model with a beta-dependent effective second energy; "
            "local traces, multiple temperatures, or mixed cumulants are needed"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prime", type=int, default=2)
    parser.add_argument("--other-prime", type=int, default=3)
    parser.add_argument("--integer-beta", type=int, default=2)
    parser.add_argument("--interaction-base", type=int, default=2)
    parser.add_argument("--maximum-occupation", type=int, default=12)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(
        json.dumps(
            analyze(
                args.prime,
                args.other_prime,
                args.integer_beta,
                args.interaction_base,
                args.maximum_occupation,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
