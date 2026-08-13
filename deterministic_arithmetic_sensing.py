#!/usr/bin/env python3
"""Deterministic tapered designs for arithmetic Dirichlet sensing.

The design uses midpoint times on ``[0,T]`` and nonnegative weights ``w_j``.
For the unnormalised phase matrix

    Phi[j,n] = exp(-i t_j log(n)),

weighted least squares has Gram matrix ``G = Phi^* W Phi``.  Its omitted-tail
bias is therefore an exact deterministic kernel calculation, rather than a
random empirical-process term.  A finite divisor-envelope sum plus a rigorous
infinite remainder gives a complete quadratic-field certificate.
"""

from __future__ import annotations

import argparse
import json
import math
from typing import Literal, Sequence

import numpy as np
from scipy.special import zeta


Window = Literal["uniform", "hann"]


def midpoint_times(sample_count: int, observation_time: float) -> np.ndarray:
    if sample_count < 2 or observation_time <= 0:
        raise ValueError("sample_count must be at least two and time positive")
    return (np.arange(sample_count, dtype=float) + 0.5) * (
        observation_time / sample_count
    )


def midpoint_weights(
    sample_count: int, observation_time: float, window: Window = "uniform"
) -> np.ndarray:
    """Nonnegative quadrature weights, normalized to sum to one."""
    times = midpoint_times(sample_count, observation_time)
    if window == "uniform":
        weights = np.ones(sample_count, dtype=float)
    elif window == "hann":
        weights = 1.0 - np.cos(2.0 * math.pi * times / observation_time)
    else:
        raise ValueError(f"unknown window: {window}")
    weights /= np.sum(weights)
    return weights


def uniform_midpoint_kernel(
    frequency: np.ndarray | float, observation_time: float, sample_count: int
):
    """Exact midpoint-grid average of ``exp(i*t*frequency)``.

    The closed form is ``exp(iu) sinc(u)/sinc(u/m)``, where ``u=T*omega/2``
    and both sinc functions use the unnormalised convention.  Explicit alias
    handling makes the formula stable at grid frequencies.
    """
    if sample_count < 2 or observation_time <= 0:
        raise ValueError("sample_count must be at least two and time positive")
    frequencies = np.asarray(frequency, dtype=float)
    u = 0.5 * observation_time * frequencies
    denominator = np.sinc(u / (math.pi * sample_count))
    numerator = np.sinc(u / math.pi)
    regular = np.abs(denominator) > 1e-12
    ratio = np.empty_like(u, dtype=float)
    np.divide(numerator, denominator, out=ratio, where=regular)
    if np.any(~regular):
        aliases = np.rint(u / (math.pi * sample_count)).astype(np.int64)
        ratio = np.where(
            regular,
            ratio,
            (-1.0) ** (aliases * (sample_count - 1)),
        )
    value = np.exp(1j * u) * ratio
    return value.item() if value.ndim == 0 else value


def midpoint_kernel(
    frequency: np.ndarray | float,
    observation_time: float,
    sample_count: int,
    window: Window = "uniform",
):
    """Exact Fourier kernel of a uniform or Hann midpoint design."""
    if window == "uniform":
        return uniform_midpoint_kernel(frequency, observation_time, sample_count)
    if window != "hann":
        raise ValueError(f"unknown window: {window}")
    shift = 2.0 * math.pi / observation_time
    return (
        uniform_midpoint_kernel(frequency, observation_time, sample_count)
        - 0.5
        * uniform_midpoint_kernel(
            np.asarray(frequency) + shift, observation_time, sample_count
        )
        - 0.5
        * uniform_midpoint_kernel(
            np.asarray(frequency) - shift, observation_time, sample_count
        )
    )


def continuous_window_kernel(
    frequency: np.ndarray | float,
    observation_time: float,
    window: Literal["uniform", "triangular", "hann"] = "uniform",
):
    """Characteristic function of three normalized densities on ``[0,T]``."""
    if observation_time <= 0:
        raise ValueError("observation_time must be positive")
    frequencies = np.asarray(frequency, dtype=float)
    u = 0.5 * observation_time * frequencies
    if window == "uniform":
        value = np.exp(1j * u) * np.sinc(u / math.pi)
    elif window == "triangular":
        value = np.exp(1j * u) * np.sinc(u / (2.0 * math.pi)) ** 2
    elif window == "hann":
        shift = 2.0 * math.pi / observation_time
        value = (
            continuous_window_kernel(frequencies, observation_time, "uniform")
            - 0.5
            * continuous_window_kernel(
                frequencies + shift, observation_time, "uniform"
            )
            - 0.5
            * continuous_window_kernel(
                frequencies - shift, observation_time, "uniform"
            )
        )
    else:
        raise ValueError(f"unknown window: {window}")
    return value.item() if value.ndim == 0 else value


def weighted_phase_matrix(maximum_norm: int, times: np.ndarray) -> np.ndarray:
    if maximum_norm < 1 or times.ndim != 1 or len(times) == 0:
        raise ValueError("a positive cutoff and nonempty time vector are required")
    norms = np.arange(1, maximum_norm + 1, dtype=float)
    return np.exp(-1j * np.outer(times, np.log(norms)))


def midpoint_gram(
    maximum_norm: int,
    observation_time: float,
    sample_count: int,
    window: Window = "uniform",
) -> np.ndarray:
    """Exact weighted Gram, evaluated through the closed-form grid kernel."""
    if maximum_norm < 1:
        raise ValueError("maximum_norm must be positive")
    logs = np.log(np.arange(1, maximum_norm + 1, dtype=float))
    frequencies = logs[:, None] - logs[None, :]
    gram = midpoint_kernel(
        frequencies, observation_time, sample_count, window=window
    )
    return (gram + gram.conj().T) / 2.0


def quadratic_divisor_coefficients_sieve(maximum_norm: int) -> np.ndarray:
    """Return ``tau(n)`` for ``0 <= n <= maximum_norm`` by a fast sieve."""
    if maximum_norm < 1:
        raise ValueError("maximum_norm must be positive")
    coefficients = np.zeros(maximum_norm + 1, dtype=np.float64)
    for divisor in range(1, maximum_norm + 1):
        coefficients[divisor::divisor] += 1.0
    return coefficients


def quadratic_tail_l1_from_sieve(
    truncation: int, sigma: float, coefficients: np.ndarray | None = None
) -> float:
    """Exact ``zeta(sigma)^2`` remainder after a finite divisor sum."""
    if sigma <= 1.0 or truncation < 1:
        raise ValueError("sigma must exceed one and truncation be positive")
    if coefficients is None:
        coefficients = quadratic_divisor_coefficients_sieve(truncation)
    if len(coefficients) <= truncation:
        raise ValueError("coefficient array is too short")
    norms = np.arange(1, truncation + 1, dtype=float)
    partial = float(np.dot(coefficients[1 : truncation + 1], norms ** (-sigma)))
    return max(0.0, float(zeta(sigma, 1.0)) ** 2 - partial)


def quadratic_tail_l1_elementary_bound(log_cutoff: float, sigma: float) -> float:
    """Elementary upper bound for ``sum_{n>X} tau(n)n^-sigma``.

    ``log_cutoff`` is ``log(X)``.  Splitting ``tau`` as the divisor-pair sum
    at ``a <= X`` gives an explicit bound of order
    ``X^(1-sigma) log(X)`` without enumerating up to the remote cutoff.
    """
    if sigma <= 1.0 or log_cutoff < 0.0:
        raise ValueError("sigma must exceed one and cutoff must be at least one")
    leading = math.exp((1.0 - sigma) * log_cutoff)
    smaller = math.exp(-sigma * log_cutoff)
    return leading * (
        1.0 + (1.0 + log_cutoff) / (sigma - 1.0)
    ) + float(zeta(sigma, 1.0)) * (
        smaller + leading / (sigma - 1.0)
    )


def alias_aware_tail_remainder_bound(
    target_norm: int,
    truncation: int,
    sigma: float,
    observation_time: float,
    sample_count: int,
    base_remainder: float,
    window: Window,
) -> float:
    """Bound the unenumerated tail using the pre-alias kernel envelope.

    Before half the first grid alias, the midpoint denominator is bounded away
    from zero.  This supplies ``1/log(k/n)`` decay.  The still more remote
    divisor tail is bounded directly by :func:`quadratic_tail_l1_elementary_bound`.
    If the finite truncation has already crossed that safe region, the function
    falls back to the global ``|K| <= 1`` bound.
    """
    if target_norm < 1 or truncation < target_norm:
        raise ValueError("target and truncation are inconsistent")
    start_frequency = math.log((truncation + 1.0) / target_norm)
    half_alias = math.pi * sample_count / observation_time
    if window == "uniform":
        frequency_shift = 0.0
        numerator_constant = math.pi
    elif window == "hann":
        frequency_shift = 2.0 * math.pi / observation_time
        numerator_constant = 2.0 * math.pi
    else:
        raise ValueError(f"unknown window: {window}")
    safe_limit = half_alias - frequency_shift
    denominator_frequency = start_frequency - frequency_shift
    if denominator_frequency <= 0.0 or start_frequency >= safe_limit:
        return base_remainder
    kernel_factor = min(
        1.0,
        numerator_constant / (observation_time * denominator_frequency),
    )
    remote_log_cutoff = math.log(float(target_norm)) + safe_limit
    remote = quadratic_tail_l1_elementary_bound(remote_log_cutoff, sigma)
    return min(base_remainder, kernel_factor * base_remainder + remote)


def deterministic_quadratic_tail_envelope(
    maximum_norm: int,
    sigma: float,
    observation_time: float,
    sample_count: int,
    truncation: int,
    window: Window = "hann",
    coefficients: np.ndarray | None = None,
    alias_aware_remainder: bool = True,
) -> tuple[np.ndarray, float]:
    """Complete target/tail correlation bounds for every quadratic field.

    The tail through ``truncation`` uses the exact discrete kernel.  Beyond it,
    ``|K_w| <= sum(w_j)=1`` supplies the rigorous l1 remainder.  This coarse
    remainder also covers every remote grid alias.
    """
    if truncation <= maximum_norm:
        raise ValueError("truncation must exceed maximum_norm")
    if coefficients is None:
        coefficients = quadratic_divisor_coefficients_sieve(truncation)
    if len(coefficients) <= truncation:
        raise ValueError("coefficient array is too short")
    remainder = quadratic_tail_l1_from_sieve(truncation, sigma, coefficients)
    tail_norms = np.arange(maximum_norm + 1, truncation + 1, dtype=float)
    tail_weights = coefficients[maximum_norm + 1 : truncation + 1] * (
        tail_norms ** (-sigma)
    )
    result = np.empty(maximum_norm, dtype=float)
    for index, target_norm in enumerate(range(1, maximum_norm + 1)):
        frequencies = np.log(target_norm / tail_norms)
        correlations = np.abs(
            midpoint_kernel(
                frequencies, observation_time, sample_count, window=window
            )
        )
        unenumerated = (
            alias_aware_tail_remainder_bound(
                target_norm,
                truncation,
                sigma,
                observation_time,
                sample_count,
                remainder,
                window,
            )
            if alias_aware_remainder
            else remainder
        )
        result[index] = float(np.dot(tail_weights, correlations)) + unenumerated
    return result, remainder


def deterministic_coefficient_bounds(
    gram: np.ndarray, sigma: float, tail_envelope: np.ndarray
) -> np.ndarray:
    maximum_norm = len(tail_envelope)
    if gram.shape != (maximum_norm, maximum_norm):
        raise ValueError("gram and envelope dimensions disagree")
    norms = np.arange(1, maximum_norm + 1, dtype=float)
    return norms**sigma * (np.abs(np.linalg.inv(gram)) @ tail_envelope)


def weighted_noise_covariance(
    maximum_norm: int,
    sigma: float,
    observation_time: float,
    sample_count: int,
    window: Window = "hann",
) -> np.ndarray:
    """Coefficient covariance divided by circular sensor-noise variance."""
    times = midpoint_times(sample_count, observation_time)
    weights = midpoint_weights(sample_count, observation_time, window)
    phase = weighted_phase_matrix(maximum_norm, times)
    gram = phase.conj().T @ (weights[:, None] * phase)
    second = phase.conj().T @ ((weights**2)[:, None] * phase)
    gram_inverse = np.linalg.inv(gram)
    weighted_covariance = gram_inverse @ second @ gram_inverse
    norms = np.arange(1, maximum_norm + 1, dtype=float)
    covariance = (
        norms[:, None] ** sigma
        * weighted_covariance
        * norms[None, :] ** sigma
    )
    return (covariance + covariance.conj().T) / 2.0


def deterministic_gaussian_rounding_failure_bound(
    coefficient_bounds: np.ndarray,
    coefficient_noise_covariance: np.ndarray,
    noise_sigma: float,
) -> float:
    """Union bound for circular complex Gaussian noise after weighted LS."""
    maximum_norm = len(coefficient_bounds)
    if coefficient_noise_covariance.shape != (maximum_norm, maximum_norm):
        raise ValueError("covariance and coefficient bounds disagree")
    if noise_sigma < 0:
        raise ValueError("noise_sigma must be nonnegative")
    if np.any(coefficient_bounds >= 0.5):
        return 1.0
    if noise_sigma == 0:
        return 0.0
    margins = 0.5 - coefficient_bounds
    variances_without_noise = np.maximum(
        0.0, np.real(np.diag(coefficient_noise_covariance))
    )
    exponents = margins**2 / (noise_sigma**2 * variances_without_noise)
    return min(1.0, float(2.0 * np.sum(np.exp(-exponents))))


def finite_weighted_tail_recovery_error(
    target_coefficients: Sequence[float],
    tail_coefficients: Sequence[float],
    sigma: float,
    observation_time: float,
    sample_count: int,
    window: Window = "hann",
) -> dict[str, object]:
    """Exact finite-tail weighted least-squares bias experiment."""
    target = np.asarray(target_coefficients, dtype=float)
    tail = np.asarray(tail_coefficients, dtype=float)
    maximum_norm = len(target)
    times = midpoint_times(sample_count, observation_time)
    weights = midpoint_weights(sample_count, observation_time, window)
    head = weighted_phase_matrix(maximum_norm, times)
    gram = head.conj().T @ (weights[:, None] * head)
    if len(tail):
        tail_norms = np.arange(
            maximum_norm + 1, maximum_norm + len(tail) + 1, dtype=float
        )
        tail_values = np.exp(-1j * np.outer(times, np.log(tail_norms))) @ (
            tail * tail_norms ** (-sigma)
        )
        cross = head.conj().T @ (weights * tail_values)
    else:
        cross = np.zeros(maximum_norm, dtype=complex)
    norms = np.arange(1, maximum_norm + 1, dtype=float)
    error = norms**sigma * np.linalg.solve(gram, cross)
    recovered = target + error
    return {
        "maximum_absolute_error": float(np.max(np.abs(error))),
        "maximum_real_error": float(np.max(np.abs(error.real))),
        "worst_coefficient": int(np.argmax(np.abs(error)) + 1),
        "integer_rounding_succeeds": bool(
            np.array_equal(np.rint(recovered.real).astype(int), target.astype(int))
        ),
        "lambda_min": float(np.linalg.eigvalsh(gram)[0]),
    }


def deterministic_certificate_report(
    maximum_norm: int = 50,
    sigma: float = 2.0,
    observation_time: float = 1_000.0,
    sample_count: int = 1_000,
    truncation: int = 1_000_000,
    window: Window = "hann",
    noise_sigma: float = 0.01,
) -> dict[str, object]:
    coefficients = quadratic_divisor_coefficients_sieve(truncation)
    gram = midpoint_gram(
        maximum_norm, observation_time, sample_count, window=window
    )
    envelope, remainder = deterministic_quadratic_tail_envelope(
        maximum_norm,
        sigma,
        observation_time,
        sample_count,
        truncation,
        window,
        coefficients,
    )
    bounds = deterministic_coefficient_bounds(gram, sigma, envelope)
    noise_covariance = weighted_noise_covariance(
        maximum_norm, sigma, observation_time, sample_count, window
    )
    return {
        "model": "deterministic weighted midpoint arithmetic sensing",
        "window": window,
        "maximum_norm": maximum_norm,
        "sigma": sigma,
        "observation_time": observation_time,
        "sample_count": sample_count,
        "truncation": truncation,
        "effective_sample_count": float(
            1.0
            / np.sum(
                midpoint_weights(sample_count, observation_time, window) ** 2
            )
        ),
        "lambda_min": float(np.linalg.eigvalsh(gram)[0]),
        "infinite_tail_l1_remainder": remainder,
        "worst_tail_coefficient_bound": float(np.max(bounds)),
        "worst_tail_coefficient": int(np.argmax(bounds) + 1),
        "integer_tail_certificate": bool(np.max(bounds) < 0.5),
        "noise_sigma": noise_sigma,
        "gaussian_rounding_failure_bound": (
            deterministic_gaussian_rounding_failure_bound(
                bounds, noise_covariance, noise_sigma
            )
        ),
        "maximum_noise_variance_factor": float(
            np.max(np.real(np.diag(noise_covariance)))
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--maximum-norm", type=int, default=50)
    parser.add_argument("--sigma", type=float, default=2.0)
    parser.add_argument("--observation-time", type=float, default=1_000.0)
    parser.add_argument("--sample-count", type=int, default=1_000)
    parser.add_argument("--truncation", type=int, default=1_000_000)
    parser.add_argument("--window", choices=["uniform", "hann"], default="hann")
    parser.add_argument("--noise-sigma", type=float, default=0.01)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(
        json.dumps(
            deterministic_certificate_report(
                maximum_norm=args.maximum_norm,
                sigma=args.sigma,
                observation_time=args.observation_time,
                sample_count=args.sample_count,
                truncation=args.truncation,
                window=args.window,
                noise_sigma=args.noise_sigma,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
