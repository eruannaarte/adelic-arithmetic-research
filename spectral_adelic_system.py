#!/usr/bin/env python3
"""Finite arithmetic Fock systems and their adelic local factors.

For a finite set S of primes, assign one bosonic occupation number k_p>=0 to
each p and Hamiltonian energy sum_p k_p log(p).  The heat trace is the finite
Euler product.  This is an exact encoding of unique factorization, not a model
whose eigenvalues are Riemann-zero ordinates.
"""

from __future__ import annotations

import argparse
import cmath
import json
import math
from fractions import Fraction
from itertools import product
from typing import Callable, Iterable, Sequence


def primes_up_to(limit: int) -> list[int]:
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[:2] = b"\x00\x00"
    for prime in range(2, math.isqrt(limit) + 1):
        if sieve[prime]:
            start = prime * prime
            sieve[start : limit + 1 : prime] = b"\x00" * (
                (limit - start) // prime + 1
            )
    return [value for value, flag in enumerate(sieve) if flag]


def validate_primes(primes: Sequence[int]) -> None:
    if len(set(primes)) != len(primes):
        raise ValueError("prime modes must be distinct")
    for value in primes:
        if value < 2 or any(value % divisor == 0 for divisor in range(2, math.isqrt(value) + 1)):
            raise ValueError(f"{value} is not prime")


def occupation_integer(primes: Sequence[int], occupations: Sequence[int]) -> int:
    validate_primes(primes)
    if len(primes) != len(occupations) or any(value < 0 for value in occupations):
        raise ValueError("occupations must be nonnegative and match the prime modes")
    result = 1
    for prime, occupation in zip(primes, occupations):
        result *= prime**occupation
    return result


def occupation_energy(primes: Sequence[int], occupations: Sequence[int]) -> float:
    integer = occupation_integer(primes, occupations)
    return math.log(integer)


def bosonic_partition(primes: Sequence[int], s: complex) -> complex:
    validate_primes(primes)
    if s.real <= 0:
        raise ValueError("the finite bosonic heat trace needs Re(s)>0")
    result = 1.0 + 0.0j
    for prime in primes:
        result /= 1.0 - cmath.exp(-s * math.log(prime))
    return result


def exact_bosonic_partition(primes: Sequence[int], integer_s: int) -> Fraction:
    validate_primes(primes)
    if integer_s <= 0:
        raise ValueError("integer_s must be positive")
    result = Fraction(1)
    for prime in primes:
        power = prime**integer_s
        result *= Fraction(power, power - 1)
    return result


def fermionic_partition(primes: Sequence[int], s: complex) -> complex:
    validate_primes(primes)
    result = 1.0 + 0.0j
    for prime in primes:
        result *= 1.0 + cmath.exp(-s * math.log(prime))
    return result


def fermionic_supertrace(primes: Sequence[int], s: complex) -> complex:
    validate_primes(primes)
    result = 1.0 + 0.0j
    for prime in primes:
        result *= 1.0 - cmath.exp(-s * math.log(prime))
    return result


def twisted_bosonic_trace(
    primes: Sequence[int], s: complex, twist: Callable[[int], complex]
) -> complex:
    validate_primes(primes)
    if s.real <= 0:
        raise ValueError("the finite twisted heat trace needs Re(s)>0")
    result = 1.0 + 0.0j
    for prime in primes:
        local_twist = complex(twist(prime))
        if abs(local_twist) > 1.0 + 1e-12:
            raise ValueError("local twists must have modulus at most one")
        result /= 1.0 - local_twist * cmath.exp(-s * math.log(prime))
    return result


def character_mod_four(value: int) -> int:
    if value % 2 == 0:
        return 0
    return 1 if value % 4 == 1 else -1


def local_p_adic_zeta_partial(prime: int, s: complex, maximum_valuation: int) -> complex:
    """Shell sum for 1_{Z_p} with vol(Z_p^x,d^x x)=1."""
    validate_primes([prime])
    if maximum_valuation < 0:
        raise ValueError("maximum valuation must be nonnegative")
    return sum(
        cmath.exp(-s * valuation * math.log(prime))
        for valuation in range(maximum_valuation + 1)
    )


def local_p_adic_zeta_tail_bound(prime: int, sigma: float, maximum_valuation: int) -> float:
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    ratio = prime ** (-sigma)
    return ratio ** (maximum_valuation + 1) / (1.0 - ratio)


def mean_energy(primes: Sequence[int], sigma: float) -> float:
    """Canonical expectation -d/dsigma log Z_S(sigma)."""
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    return sum(math.log(prime) / (prime**sigma - 1.0) for prime in primes)


def energy_variance(primes: Sequence[int], sigma: float) -> float:
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    return sum(
        math.log(prime) ** 2 * prime**sigma / (prime**sigma - 1.0) ** 2
        for prime in primes
    )


def prime_power_partial(
    primes: Sequence[int], sigma: float, maximum_power: int
) -> float:
    if maximum_power < 1:
        raise ValueError("maximum power must be positive")
    return sum(
        math.log(prime) * prime ** (-sigma * power)
        for prime in primes
        for power in range(1, maximum_power + 1)
    )


def prime_power_tail_bound(
    primes: Sequence[int], sigma: float, maximum_power: int
) -> float:
    return sum(
        math.log(prime)
        * prime ** (-sigma * (maximum_power + 1))
        / (1.0 - prime ** (-sigma))
        for prime in primes
    )


def archimedean_gaussian_factor(sigma: float) -> float:
    """Integral_Rx exp(-pi*x^2)|x|^sigma d^x x."""
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    return math.pi ** (-sigma / 2.0) * math.gamma(sigma / 2.0)


def truncated_occupation_sum(
    primes: Sequence[int], sigma: int, maximum_occupation: int
) -> Fraction:
    if sigma <= 0 or maximum_occupation < 0:
        raise ValueError("invalid truncation")
    result = Fraction(0)
    for occupations in product(range(maximum_occupation + 1), repeat=len(primes)):
        result += Fraction(1, occupation_integer(primes, occupations) ** sigma)
    return result


def analyze(prime_limit: int, sigma: float, maximum_shell: int) -> dict[str, object]:
    primes = primes_up_to(prime_limit)
    s = complex(sigma, 0.0)
    partition = bosonic_partition(primes, s)
    fermionic = fermionic_partition(primes, s)
    supertrace = fermionic_supertrace(primes, s)
    mean = mean_energy(primes, sigma)
    power_partial = prime_power_partial(primes, sigma, maximum_shell)
    power_tail = prime_power_tail_bound(primes, sigma, maximum_shell)
    local_checks = []
    for prime in primes:
        partial = local_p_adic_zeta_partial(prime, s, maximum_shell)
        exact = 1.0 / (1.0 - prime ** (-sigma))
        local_checks.append(
            {
                "prime": prime,
                "partial_shell_sum": partial.real,
                "euler_factor": exact,
                "absolute_residual": abs(exact - partial),
                "tail_bound": local_p_adic_zeta_tail_bound(
                    prime, sigma, maximum_shell
                ),
            }
        )
    return {
        "prime_limit": prime_limit,
        "primes": primes,
        "sigma": sigma,
        "bosonic_partition": partition.real,
        "exact_partition_when_sigma_is_integer": (
            str(exact_bosonic_partition(primes, int(sigma)))
            if sigma.is_integer()
            else None
        ),
        "fermionic_partition": fermionic.real,
        "fermionic_identity_residual": abs(
            fermionic - partition / bosonic_partition(primes, 2.0 * s)
        ),
        "fermionic_supertrace": supertrace.real,
        "inverse_bosonic_residual": abs(supertrace - 1.0 / partition),
        "mean_energy": mean,
        "energy_variance": energy_variance(primes, sigma),
        "prime_power_partial": power_partial,
        "prime_power_tail_bound": power_tail,
        "mean_energy_minus_prime_power_partial": mean - power_partial,
        "archimedean_gaussian_factor": archimedean_gaussian_factor(sigma),
        "finite_tate_product": archimedean_gaussian_factor(sigma)
        * partition.real,
        "mod_four_twisted_trace": twisted_bosonic_trace(
            primes, s, character_mod_four
        ).real,
        "local_p_adic_shell_checks": local_checks,
        "interpretation": (
            "occupation k_p equals valuation v_p; the local heat trace and the "
            "multiplicative p-adic shell integral are the same geometric series"
        ),
        "zero_warning": (
            "this positive Hamiltonian encodes Euler factors in its heat trace; "
            "its eigenvalues are log(n), not Riemann-zero ordinates"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prime-limit", type=int, default=19)
    parser.add_argument("--sigma", type=float, default=2.0)
    parser.add_argument("--maximum-shell", type=int, default=12)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(
        json.dumps(
            analyze(args.prime_limit, args.sigma, args.maximum_shell),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
