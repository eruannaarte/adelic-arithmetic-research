#!/usr/bin/env python3
"""Convex positive trigonometric-window design for arithmetic sensing.

The weights on the midpoint grid are parameterized by a short cosine series,

    w_j = m^(-1) [1 + 2 sum_(r=1)^H c_r cos(2*pi*r*t_j/T)].

Positivity, a pointwise density cap, a Gershgorin conditioning guarantee, and
an arithmetic boundary-tail objective are all linear after auxiliary absolute
value variables are introduced.  The resulting finite design problem is a
linear program solved by HiGHS.  Every reported infinite-tail certificate is
then recomputed independently from the realized weights and an analytic
alias-safe remainder; LP optimality is never substituted for the theorem.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np
from numpy.polynomial import Chebyshev
from scipy import sparse
from scipy.optimize import linprog

from deterministic_arithmetic_sensing import (
    deterministic_coefficient_bounds,
    deterministic_gaussian_rounding_failure_bound,
    midpoint_times,
    quadratic_divisor_coefficients_sieve,
    quadratic_tail_l1_elementary_bound,
    quadratic_tail_l1_from_sieve,
    uniform_midpoint_kernel,
    weighted_phase_matrix,
)


@dataclass(frozen=True)
class CosineQuadratureDesign:
    sample_count: int
    observation_time: float
    coefficients: np.ndarray

    @property
    def harmonic_count(self) -> int:
        return len(self.coefficients)


@dataclass(frozen=True)
class FejerRieszCertificate:
    """Numerical realization of an exact Fejer--Riesz certificate.

    ``factor_coefficients`` are in increasing powers and certify

        a_0 + 2 sum_(r=1)^H a_r cos(r theta)
            = |sum_(r=0)^H q_r exp(i r theta)|^2.

    The identity is checked coefficient by coefficient; ``residual`` records
    the largest reconstruction error from floating-point root factorization.
    """

    constant_coefficient: float
    cosine_coefficients: np.ndarray
    factor_coefficients: np.ndarray
    residual: float


def continuous_density_extrema(
    coefficients: Sequence[float], constant: float = 1.0
) -> dict[str, float]:
    """Return all-interval extrema of a real cosine polynomial.

    With ``x=cos(theta)``, the density becomes an ordinary Chebyshev
    polynomial on ``[-1,1]``.  Its extrema therefore occur at the endpoints
    or at the real roots of its derivative.  This avoids a sampled-grid
    positivity test.
    """
    cosine_coefficients = np.asarray(coefficients, dtype=float)
    polynomial = Chebyshev(
        np.concatenate(([constant], 2.0 * cosine_coefficients))
    )
    roots = polynomial.deriv().roots()
    real_roots = np.real(roots[np.abs(np.imag(roots)) <= 1e-9])
    critical = real_roots[(real_roots >= -1.0) & (real_roots <= 1.0)]
    points = np.concatenate(([-1.0, 1.0], critical))
    values = np.asarray(polynomial(points), dtype=float)
    minimum_index = int(np.argmin(values))
    maximum_index = int(np.argmax(values))
    return {
        "minimum": float(values[minimum_index]),
        "minimum_x": float(points[minimum_index]),
        "minimum_theta": float(math.acos(np.clip(points[minimum_index], -1.0, 1.0))),
        "maximum": float(values[maximum_index]),
        "maximum_x": float(points[maximum_index]),
        "maximum_theta": float(math.acos(np.clip(points[maximum_index], -1.0, 1.0))),
    }


def fejer_riesz_certificate(
    coefficients: Sequence[float],
    constant: float = 1.0,
    tolerance: float = 2e-7,
) -> FejerRieszCertificate:
    """Construct and verify a Fejer--Riesz spectral factor.

    Strictly positive inputs have exactly one root from each reciprocal pair
    inside the unit disk.  Selecting those roots constructs the minimum-phase
    factor.  The returned residual is an independent coefficient-level check,
    not a sampled comparison of function values.
    """
    cosine_coefficients = np.asarray(coefficients, dtype=float)
    if constant <= 0.0:
        raise ValueError("constant Fourier coefficient must be positive")
    extrema = continuous_density_extrema(cosine_coefficients, constant)
    if extrema["minimum"] < -tolerance:
        raise ValueError("cosine polynomial is negative on the unit circle")
    degree = len(cosine_coefficients)
    if degree == 0:
        factor = np.asarray([math.sqrt(constant)])
    else:
        # Coefficients of z^H p(z), in increasing powers of z.
        self_reciprocal = np.concatenate(
            (cosine_coefficients[::-1], [constant], cosine_coefficients)
        )
        roots = np.roots(self_reciprocal[::-1])
        selected = roots[np.argsort(np.abs(roots))[:degree]]
        factor = np.poly(selected)[::-1]
        if np.max(np.abs(np.imag(factor))) <= 1e-8:
            factor = np.real(factor)
        factor = factor * math.sqrt(
            constant / float(np.sum(np.abs(factor) ** 2))
        )
    reconstructed = np.asarray(
        [
            np.sum(factor[lag:] * np.conjugate(factor[: degree + 1 - lag]))
            for lag in range(degree + 1)
        ]
    )
    expected = np.concatenate(([constant], cosine_coefficients))
    residual = float(np.max(np.abs(reconstructed - expected)))
    if residual > tolerance:
        raise ValueError(
            f"spectral factor reconstruction residual {residual} exceeds tolerance"
        )
    return FejerRieszCertificate(
        constant,
        cosine_coefficients,
        np.asarray(factor),
        residual,
    )


def cosine_window_weights(design: CosineQuadratureDesign) -> np.ndarray:
    """Materialize the normalized positive midpoint weights of a design."""
    if design.sample_count < 2 or design.observation_time <= 0:
        raise ValueError("sample_count must be at least two and time positive")
    if design.harmonic_count >= design.sample_count:
        raise ValueError("harmonic count must be below sample count")
    times = midpoint_times(design.sample_count, design.observation_time)
    harmonics = np.arange(1, design.harmonic_count + 1, dtype=float)
    angles = 2.0 * math.pi * np.outer(
        times / design.observation_time, harmonics
    )
    density = 1.0 + 2.0 * np.cos(angles) @ design.coefficients
    # Only roundoff-sized negative values are clipped.  Material negativity is
    # rejected so an optimizer failure cannot masquerade as a positive design.
    if float(np.min(density)) < -1e-9:
        raise ValueError("cosine coefficients do not define nonnegative weights")
    density = np.maximum(0.0, density)
    weights = density / design.sample_count
    weights /= np.sum(weights)
    return weights


def cosine_window_kernel(
    frequency: np.ndarray | float, design: CosineQuadratureDesign
):
    """Exact midpoint kernel of the cosine-series design."""
    frequencies = np.asarray(frequency, dtype=float)
    centered = centered_cosine_response(frequencies, design)
    value = np.exp(0.5j * design.observation_time * frequencies) * centered
    return value.item() if value.ndim == 0 else value


def centered_cosine_response(
    frequency: np.ndarray | float, design: CosineQuadratureDesign
):
    """Real response after removing the universal phase ``exp(i*T*w/2)``.

    All shifted uniform kernels are evaluated in one vectorized array.  This is
    algebraically identical to :func:`cosine_window_kernel` but substantially
    faster for million-term tail certificates.
    """
    frequencies = np.asarray(frequency, dtype=float)
    original_shape = frequencies.shape
    flat = frequencies.reshape(-1)
    u = 0.5 * design.observation_time * flat
    shifts = np.arange(-design.harmonic_count, design.harmonic_count + 1)
    shifted_u = u[:, None] + math.pi * shifts[None, :]
    denominator = np.sinc(
        shifted_u / (math.pi * design.sample_count)
    )
    numerator = np.sinc(shifted_u / math.pi)
    ratios = np.empty_like(shifted_u)
    regular = np.abs(denominator) > 1e-12
    np.divide(numerator, denominator, out=ratios, where=regular)
    if np.any(~regular):
        aliases = np.rint(
            shifted_u / (math.pi * design.sample_count)
        ).astype(np.int64)
        ratios = np.where(
            regular,
            ratios,
            (-1.0) ** (aliases * (design.sample_count - 1)),
        )
    multipliers = np.empty(2 * design.harmonic_count + 1, dtype=float)
    for index, shift in enumerate(shifts):
        if shift == 0:
            multipliers[index] = 1.0
        else:
            multipliers[index] = (
                design.coefficients[abs(shift) - 1] * (-1.0) ** abs(shift)
            )
    response = (ratios @ multipliers).reshape(original_shape)
    return response.item() if response.ndim == 0 else response


def centered_response_components(
    frequencies: np.ndarray,
    observation_time: float,
    sample_count: int,
    harmonic_count: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Return affine data ``R(omega)=base+basis@c`` for the real response."""
    frequencies = np.asarray(frequencies, dtype=float)
    centering = np.exp(-0.5j * observation_time * frequencies)
    base = np.real(
        centering
        * uniform_midpoint_kernel(frequencies, observation_time, sample_count)
    )
    basis = np.empty((len(frequencies), harmonic_count), dtype=float)
    fundamental = 2.0 * math.pi / observation_time
    for harmonic in range(1, harmonic_count + 1):
        shifted = uniform_midpoint_kernel(
            frequencies + harmonic * fundamental,
            observation_time,
            sample_count,
        ) + uniform_midpoint_kernel(
            frequencies - harmonic * fundamental,
            observation_time,
            sample_count,
        )
        basis[:, harmonic - 1] = np.real(centering * shifted)
    return base, basis


def cosine_window_gram(maximum_norm: int, design: CosineQuadratureDesign) -> np.ndarray:
    if maximum_norm < 1:
        raise ValueError("maximum_norm must be positive")
    logs = np.log(np.arange(1, maximum_norm + 1, dtype=float))
    frequencies = logs[:, None] - logs[None, :]
    gram = cosine_window_kernel(frequencies, design)
    return (gram + gram.conj().T) / 2.0


def exact_alias_magnitude(design: CosineQuadratureDesign, alias_index: int = 1) -> float:
    """Magnitude at a grid alias; mathematically it is always one."""
    if alias_index == 0:
        raise ValueError("use a nonzero alias index")
    frequency = (
        2.0
        * math.pi
        * alias_index
        * design.sample_count
        / design.observation_time
    )
    return float(abs(cosine_window_kernel(frequency, design)))


def prealias_limit(design: CosineQuadratureDesign) -> float:
    """Frequency below which every shifted uniform kernel is pre-alias."""
    fundamental = 2.0 * math.pi / design.observation_time
    return (
        math.pi * design.sample_count / design.observation_time
        - design.harmonic_count * fundamental
    )


_EULER_GAMMA = 0.5772156649015329


def quadratic_divisor_interval_l1_bound(
    log_lower: float, log_upper: float, sigma: float
) -> float:
    """Bound ``sum_(exp(L)<n<=exp(U)) tau(n)n^-sigma``.

    Dirichlet's hyperbola identity and elementary harmonic-number bounds give,
    for ``x >= 4``,

        x log x + (2 gamma - 1)x - 4 sqrt(x) - 4 <= D(x)
        D(x) <= x log x + (2 gamma - 1)x + 3 sqrt(x) + 1,

    where ``D(x)=sum_(n<=x) tau(n)``.  Abel summation with the lower endpoint
    estimate and the upper integrand estimate yields the interval bound.  The
    log-domain formula remains stable at remote aliases that cannot be sieved.
    """
    if sigma <= 1.0 or log_lower < math.log(4.0) or log_upper < log_lower:
        raise ValueError("require sigma>1 and 4<=lower<=upper")
    if log_upper == log_lower:
        return 0.0
    exponent = sigma - 1.0

    def power(rate: float, logarithm: float) -> float:
        return math.exp(-rate * logarithm)

    lower_main = power(exponent, log_lower) * (
        log_lower + 2.0 * _EULER_GAMMA - 1.0
    )
    lower_scaled = max(
        0.0,
        lower_main
        - 4.0 * power(sigma - 0.5, log_lower)
        - 4.0 * power(sigma, log_lower),
    )
    upper_scaled = power(exponent, log_upper) * (
        log_upper + 2.0 * _EULER_GAMMA - 1.0
    ) + 3.0 * power(sigma - 0.5, log_upper) + power(
        sigma, log_upper
    )

    lower_exp = power(exponent, log_lower)
    upper_exp = power(exponent, log_upper)
    integral_log = lower_exp * (
        log_lower / exponent + 1.0 / exponent**2
    ) - upper_exp * (log_upper / exponent + 1.0 / exponent**2)
    integral_constant = (lower_exp - upper_exp) / exponent
    square_root_integral = (
        power(sigma - 0.5, log_lower)
        - power(sigma - 0.5, log_upper)
    ) / (sigma - 0.5)
    unit_integral = (
        power(sigma, log_lower) - power(sigma, log_upper)
    ) / sigma
    integral_upper = (
        integral_log
        + (2.0 * _EULER_GAMMA - 1.0) * integral_constant
        + 3.0 * square_root_integral
        + unit_integral
    )
    return max(0.0, upper_scaled - lower_scaled + sigma * integral_upper)


def trigonometric_kernel_interval_bound(
    lower_frequency: float,
    upper_frequency: float,
    design: CosineQuadratureDesign,
) -> float:
    """Rigorous supremum envelope for ``|K(omega)|`` on an interval.

    Each shifted uniform midpoint kernel is bounded by
    ``min(1, pi/(T*distance_to_alias))``.  The triangle inequality combines
    the finite cosine shifts, while positivity of the realized quadrature
    supplies the final global cap ``|K|<=1``.
    """
    if lower_frequency < 0.0 or upper_frequency < lower_frequency:
        raise ValueError("invalid nonnegative frequency interval")
    alias_period = (
        2.0 * math.pi * design.sample_count / design.observation_time
    )
    fundamental = 2.0 * math.pi / design.observation_time
    center = 0.5 * (lower_frequency + upper_frequency)
    half_width = 0.5 * (upper_frequency - lower_frequency)

    def uniform_bound(shift: int) -> float:
        shifted_center = center + shift * fundamental
        centered_remainder = (
            (shifted_center + 0.5 * alias_period) % alias_period
        ) - 0.5 * alias_period
        distance = max(0.0, abs(centered_remainder) - half_width)
        if distance == 0.0:
            return 1.0
        return min(1.0, math.pi / (design.observation_time * distance))

    result = uniform_bound(0)
    for harmonic, coefficient in enumerate(design.coefficients, start=1):
        result += abs(float(coefficient)) * (
            uniform_bound(harmonic) + uniform_bound(-harmonic)
        )
    return min(1.0, result)


def trigonometric_alias_band_remainder_bound(
    target_norm: int,
    truncation: int,
    sigma: float,
    design: CosineQuadratureDesign,
    base_remainder: float,
    alias_periods: int = 2,
    bins_per_alias: int = 2_048,
) -> float:
    """All-alias remainder bound using log-frequency bands.

    The unenumerated integers are partitioned by ``v=log(k/target_norm)``.
    On each band we multiply a rigorous midpoint-kernel supremum by an Abel
    bound for its divisor mass.  After the requested number of full alias
    periods, the remaining mass is paid once with the elementary tail bound.
    """
    if target_norm < 1 or truncation < max(4, target_norm):
        raise ValueError("target and truncation are inconsistent")
    if alias_periods < 1 or bins_per_alias < 8:
        raise ValueError("alias partition is too small")
    start_frequency = math.log(float(truncation) / target_norm)
    alias_period = (
        2.0 * math.pi * design.sample_count / design.observation_time
    )
    end_frequency = (alias_periods + 0.5) * alias_period
    if start_frequency >= end_frequency:
        return base_remainder
    step = alias_period / bins_per_alias
    first_index = math.floor(start_frequency / step) + 1
    last_index = math.ceil(end_frequency / step)
    interior = np.arange(first_index, last_index, dtype=float) * step
    boundaries = np.concatenate(
        ([start_frequency], interior[interior < end_frequency], [end_frequency])
    )
    log_target = math.log(float(target_norm))
    total = 0.0
    for lower, upper in zip(boundaries[:-1], boundaries[1:]):
        kernel_bound = trigonometric_kernel_interval_bound(
            float(lower), float(upper), design
        )
        interval_mass = quadratic_divisor_interval_l1_bound(
            log_target + float(lower), log_target + float(upper), sigma
        )
        total += kernel_bound * interval_mass
    total += quadratic_tail_l1_elementary_bound(
        log_target + end_frequency, sigma
    )
    return min(base_remainder, total)


def trigonometric_alias_aware_remainder_bound(
    target_norm: int,
    truncation: int,
    sigma: float,
    design: CosineQuadratureDesign,
    base_remainder: float,
) -> float:
    """Rigorous all-alias remainder for a cosine-series midpoint window."""
    return trigonometric_alias_band_remainder_bound(
        target_norm,
        truncation,
        sigma,
        design,
        base_remainder,
    )


def cosine_quadratic_tail_envelope(
    maximum_norm: int,
    sigma: float,
    truncation: int,
    design: CosineQuadratureDesign,
    coefficients: np.ndarray | None = None,
    chunk_size: int = 100_000,
) -> tuple[np.ndarray, float]:
    """Complete universal quadratic tail envelope for a cosine design."""
    if truncation <= maximum_norm:
        raise ValueError("truncation must exceed maximum_norm")
    if coefficients is None:
        coefficients = quadratic_divisor_coefficients_sieve(truncation)
    if len(coefficients) <= truncation:
        raise ValueError("coefficient array is too short")
    base_remainder = quadratic_tail_l1_from_sieve(
        truncation, sigma, coefficients
    )
    result = np.zeros(maximum_norm, dtype=float)
    for target_index, target_norm in enumerate(range(1, maximum_norm + 1)):
        subtotal = 0.0
        for start in range(maximum_norm + 1, truncation + 1, chunk_size):
            stop = min(truncation + 1, start + chunk_size)
            tail_norms = np.arange(start, stop, dtype=float)
            weighted = coefficients[start:stop] * tail_norms ** (-sigma)
            frequencies = np.log(target_norm / tail_norms)
            subtotal += float(
                np.dot(weighted, np.abs(centered_cosine_response(frequencies, design)))
            )
        result[target_index] = subtotal + (
            trigonometric_alias_aware_remainder_bound(
                target_norm,
                truncation,
                sigma,
                design,
                base_remainder,
            )
        )
    return result, base_remainder


def cosine_noise_covariance(
    maximum_norm: int, sigma: float, design: CosineQuadratureDesign
) -> np.ndarray:
    times = midpoint_times(design.sample_count, design.observation_time)
    weights = cosine_window_weights(design)
    phase = weighted_phase_matrix(maximum_norm, times)
    gram = phase.conj().T @ (weights[:, None] * phase)
    second = phase.conj().T @ ((weights**2)[:, None] * phase)
    gram_inverse = np.linalg.inv(gram)
    normalized_covariance = gram_inverse @ second @ gram_inverse
    norms = np.arange(1, maximum_norm + 1, dtype=float)
    covariance = (
        norms[:, None] ** sigma
        * normalized_covariance
        * norms[None, :] ** sigma
    )
    return (covariance + covariance.conj().T) / 2.0


def finite_cosine_tail_recovery_error(
    target_coefficients: Sequence[float],
    tail_coefficients: Sequence[float],
    sigma: float,
    design: CosineQuadratureDesign,
) -> dict[str, object]:
    """Exact finite-tail weighted least-squares bias via the design kernel."""
    target = np.asarray(target_coefficients, dtype=float)
    tail = np.asarray(tail_coefficients, dtype=float)
    maximum_norm = len(target)
    gram = cosine_window_gram(maximum_norm, design)
    target_norms = np.arange(1, maximum_norm + 1, dtype=float)
    if len(tail):
        tail_norms = np.arange(
            maximum_norm + 1, maximum_norm + len(tail) + 1, dtype=float
        )
        weighted_tail = tail * tail_norms ** (-sigma)
        cross = np.empty(maximum_norm, dtype=complex)
        for index, target_norm in enumerate(target_norms):
            cross[index] = np.dot(
                weighted_tail,
                cosine_window_kernel(np.log(target_norm / tail_norms), design),
            )
    else:
        cross = np.zeros(maximum_norm, dtype=complex)
    error = target_norms**sigma * np.linalg.solve(gram, cross)
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


def finite_divisor_tail_proxy(
    maximum_norm: int,
    sigma: float,
    lower_tail_norm: int,
    upper_tail_norm: int,
    design: CosineQuadratureDesign,
    coefficients: np.ndarray | None = None,
    chunk_size: int = 100_000,
) -> np.ndarray:
    """Exact divisor-weighted correlation envelope on a finite held-out band."""
    if (
        maximum_norm < 1
        or lower_tail_norm <= maximum_norm
        or upper_tail_norm < lower_tail_norm
        or sigma <= 1.0
    ):
        raise ValueError("invalid held-out tail band")
    if coefficients is None:
        coefficients = quadratic_divisor_coefficients_sieve(upper_tail_norm)
    if len(coefficients) <= upper_tail_norm:
        raise ValueError("coefficient array is too short")
    result = np.zeros(maximum_norm, dtype=float)
    for target_index, target_norm in enumerate(range(1, maximum_norm + 1)):
        subtotal = 0.0
        for start in range(
            lower_tail_norm, upper_tail_norm + 1, chunk_size
        ):
            stop = min(upper_tail_norm + 1, start + chunk_size)
            tail_norms = np.arange(start, stop, dtype=float)
            weighted = coefficients[start:stop] * tail_norms ** (-sigma)
            frequencies = np.log(target_norm / tail_norms)
            subtotal += float(
                np.dot(
                    weighted,
                    np.abs(centered_cosine_response(frequencies, design)),
                )
            )
        result[target_index] = target_norm**sigma * subtotal
    return result


def _absolute_value_constraints(
    basis: np.ndarray,
    base: np.ndarray,
    variable_count: int,
    coefficient_slice: slice,
    auxiliary_slice: slice,
) -> tuple[sparse.csr_matrix, np.ndarray]:
    count = len(base)
    rows = np.arange(count)
    selector = sparse.csr_matrix(
        (-np.ones(count), (rows, rows)), shape=(count, count)
    )
    left = sparse.csr_matrix(basis)
    blocks_positive = []
    blocks_negative = []
    cursor = 0
    for start, stop in [
        (0, coefficient_slice.start),
        (coefficient_slice.start, coefficient_slice.stop),
        (coefficient_slice.stop, auxiliary_slice.start),
        (auxiliary_slice.start, auxiliary_slice.stop),
        (auxiliary_slice.stop, variable_count),
    ]:
        width = stop - start
        if start == coefficient_slice.start and stop == coefficient_slice.stop:
            blocks_positive.append(left)
            blocks_negative.append(-left)
        elif start == auxiliary_slice.start and stop == auxiliary_slice.stop:
            blocks_positive.append(selector)
            blocks_negative.append(selector)
        elif width:
            zero = sparse.csr_matrix((count, width))
            blocks_positive.append(zero)
            blocks_negative.append(zero)
        cursor = stop
    if cursor != variable_count:
        raise AssertionError("constraint block construction failed")
    matrix = sparse.vstack(
        [sparse.hstack(blocks_positive), sparse.hstack(blocks_negative)],
        format="csr",
    )
    return matrix, np.concatenate([-base, base])


def optimize_cosine_quadrature(
    maximum_norm: int = 50,
    sigma: float = 2.0,
    observation_time: float = 1_000.0,
    sample_count: int = 5_000,
    harmonic_count: int = 4,
    design_tail_cutoff: int = 500,
    gershgorin_lower_bound: float = 0.98,
    density_cap: float = 2.5,
    continuous_density_margin: float = 1e-8,
    maximum_continuum_rounds: int = 20,
) -> tuple[CosineQuadratureDesign, dict[str, object]]:
    """Solve the positive-window design LP and certify the full continuum.

    The frequency-response and conditioning constraints are finite.  Density
    positivity and the cap are semi-infinite constraints.  We solve them by
    exact separation: each LP candidate is converted to a Chebyshev
    polynomial, all derivative roots are inspected, and every violating
    extremum is added as a cut.  At termination, Fejer--Riesz factors certify
    both ``density >= 0`` and ``density <= density_cap`` on the entire period.
    """
    if maximum_norm < 2 or design_tail_cutoff <= maximum_norm:
        raise ValueError("cutoffs are inconsistent")
    if sigma <= 1.0 or observation_time <= 0 or sample_count < 2:
        raise ValueError("invalid sensing parameters")
    if harmonic_count < 1 or harmonic_count >= sample_count // 2:
        raise ValueError("invalid harmonic count")
    if not 0.0 < gershgorin_lower_bound < 1.0:
        raise ValueError("Gershgorin lower bound must lie in (0,1)")
    if density_cap < 1.0:
        raise ValueError("density_cap must be at least one")
    if continuous_density_margin < 0.0 or 2.0 * continuous_density_margin >= density_cap:
        raise ValueError("invalid continuous density margin")
    if maximum_continuum_rounds < 1:
        raise ValueError("maximum_continuum_rounds must be positive")

    target_pairs = [
        (left, right)
        for left in range(1, maximum_norm + 1)
        for right in range(left + 1, maximum_norm + 1)
    ]
    target_frequencies = np.asarray(
        [math.log(right / left) for left, right in target_pairs], dtype=float
    )
    target_base, target_basis = centered_response_components(
        target_frequencies,
        observation_time,
        sample_count,
        harmonic_count,
    )

    tail_targets = np.repeat(
        np.arange(1, maximum_norm + 1, dtype=int),
        design_tail_cutoff - maximum_norm,
    )
    tail_norms_one = np.arange(
        maximum_norm + 1, design_tail_cutoff + 1, dtype=int
    )
    tail_norms = np.tile(tail_norms_one, maximum_norm)
    tail_frequencies = np.log(tail_norms / tail_targets)
    tail_base, tail_basis = centered_response_components(
        tail_frequencies,
        observation_time,
        sample_count,
        harmonic_count,
    )

    target_count = len(target_pairs)
    tail_count = len(tail_frequencies)
    coefficient_slice = slice(0, harmonic_count)
    target_auxiliary_slice = slice(
        harmonic_count, harmonic_count + target_count
    )
    tail_auxiliary_slice = slice(
        target_auxiliary_slice.stop, target_auxiliary_slice.stop + tail_count
    )
    objective_index = tail_auxiliary_slice.stop
    variable_count = objective_index + 1

    target_absolute_matrix, target_absolute_rhs = _absolute_value_constraints(
        target_basis,
        target_base,
        variable_count,
        coefficient_slice,
        target_auxiliary_slice,
    )
    tail_absolute_matrix, tail_absolute_rhs = _absolute_value_constraints(
        tail_basis,
        tail_base,
        variable_count,
        coefficient_slice,
        tail_auxiliary_slice,
    )

    incidence_rows: list[int] = []
    incidence_columns: list[int] = []
    for pair_index, (left, right) in enumerate(target_pairs):
        incidence_rows.extend([left - 1, right - 1])
        incidence_columns.extend([pair_index, pair_index])
    incidence = sparse.csr_matrix(
        (
            np.ones(len(incidence_rows)),
            (incidence_rows, incidence_columns),
        ),
        shape=(maximum_norm, target_count),
    )
    conditioning_matrix = sparse.hstack(
        [
            sparse.csr_matrix((maximum_norm, harmonic_count)),
            incidence,
            sparse.csr_matrix((maximum_norm, tail_count + 1)),
        ],
        format="csr",
    )
    conditioning_rhs = np.full(
        maximum_norm, 1.0 - gershgorin_lower_bound
    )

    envelope_coefficients = quadratic_divisor_coefficients_sieve(
        design_tail_cutoff
    )
    aggregation_scale = 10_000.0
    aggregate_rows = np.repeat(
        np.arange(maximum_norm), design_tail_cutoff - maximum_norm
    )
    aggregate_columns = np.arange(tail_count)
    aggregate_values = (
        aggregation_scale
        * tail_targets.astype(float) ** sigma
        * envelope_coefficients[tail_norms]
        * tail_norms.astype(float) ** (-sigma)
    )
    aggregation = sparse.csr_matrix(
        (aggregate_values, (aggregate_rows, aggregate_columns)),
        shape=(maximum_norm, tail_count),
    )
    objective_column = sparse.csr_matrix(
        (-np.ones(maximum_norm), (np.arange(maximum_norm), np.zeros(maximum_norm))),
        shape=(maximum_norm, 1),
    )
    tail_objective_matrix = sparse.hstack(
        [
            sparse.csr_matrix((maximum_norm, harmonic_count + target_count)),
            aggregation,
            objective_column,
        ],
        format="csr",
    )
    tail_objective_rhs = np.zeros(maximum_norm)

    harmonics = np.arange(1, harmonic_count + 1, dtype=float)
    finite_inequality_matrix = sparse.vstack(
        [
            target_absolute_matrix,
            tail_absolute_matrix,
            conditioning_matrix,
            tail_objective_matrix,
        ],
        format="csr",
    )
    finite_inequality_rhs = np.concatenate(
        [
            target_absolute_rhs,
            tail_absolute_rhs,
            conditioning_rhs,
            tail_objective_rhs,
        ]
    )
    objective = np.zeros(variable_count)
    objective[objective_index] = 1.0
    bounds = (
        [(None, None)] * harmonic_count
        + [(0.0, 1.0)] * (target_count + tail_count)
        + [(0.0, None)]
    )
    # A small seed grid initializes the exchange method.  These are not the
    # certificate: the exact extrema separation and spectral factors below are.
    density_angles = list(
        np.linspace(0.0, 2.0 * math.pi, 8 * harmonic_count + 1, endpoint=False)
    ) + [math.pi]
    continuum_cuts = 0
    solution = None
    extrema = None
    for continuum_round in range(1, maximum_continuum_rounds + 1):
        density_cosines = np.cos(np.outer(density_angles, harmonics))
        positivity_left = sparse.hstack(
            [
                sparse.csr_matrix(-2.0 * density_cosines),
                sparse.csr_matrix(
                    (len(density_angles), variable_count - harmonic_count)
                ),
            ],
            format="csr",
        )
        density_left = sparse.hstack(
            [
                sparse.csr_matrix(2.0 * density_cosines),
                sparse.csr_matrix(
                    (len(density_angles), variable_count - harmonic_count)
                ),
            ],
            format="csr",
        )
        inequality_matrix = sparse.vstack(
            [finite_inequality_matrix, positivity_left, density_left],
            format="csr",
        )
        inequality_rhs = np.concatenate(
            [
                finite_inequality_rhs,
                np.full(len(density_angles), 1.0 - continuous_density_margin),
                np.full(
                    len(density_angles),
                    density_cap - 1.0 - continuous_density_margin,
                ),
            ]
        )
        solution = linprog(
            objective,
            A_ub=inequality_matrix,
            b_ub=inequality_rhs,
            bounds=bounds,
            method="highs",
            options={
                "dual_feasibility_tolerance": 1e-9,
                "primal_feasibility_tolerance": 1e-9,
            },
        )
        if not solution.success:
            raise RuntimeError(f"quadrature LP failed: {solution.message}")
        candidate = np.asarray(solution.x[coefficient_slice], dtype=float)
        extrema = continuous_density_extrema(candidate)
        violations: list[float] = []
        if extrema["minimum"] < continuous_density_margin - 5e-10:
            violations.append(extrema["minimum_theta"])
        if extrema["maximum"] > density_cap - continuous_density_margin + 5e-10:
            violations.append(extrema["maximum_theta"])
        if not violations:
            break
        density_angles.extend(violations)
        continuum_cuts += len(violations)
    else:
        raise RuntimeError("continuum density exchange method did not converge")
    assert solution is not None and extrema is not None
    design = CosineQuadratureDesign(
        sample_count,
        observation_time,
        np.asarray(solution.x[coefficient_slice], dtype=float),
    )
    weights = cosine_window_weights(design)
    gram = cosine_window_gram(maximum_norm, design)
    radius = float(np.max(np.sum(np.abs(gram), axis=1) - 1.0))
    factor_margin = 0.5 * continuous_density_margin
    lower_factor = fejer_riesz_certificate(
        design.coefficients, constant=1.0 - factor_margin
    )
    upper_factor = fejer_riesz_certificate(
        -design.coefficients,
        constant=density_cap - 1.0 - factor_margin,
    )
    factor_error_multiplier = 2 * harmonic_count + 1
    lower_certified_floor = (
        factor_margin - factor_error_multiplier * lower_factor.residual
    )
    upper_certified_gap = (
        factor_margin - factor_error_multiplier * upper_factor.residual
    )
    if lower_certified_floor <= 0.0 or upper_certified_gap <= 0.0:
        raise RuntimeError("Fejer--Riesz residual is too large for certification")
    report = {
        "solver_status": solution.message,
        "objective_finite_tail_proxy": float(
            solution.x[objective_index] / aggregation_scale
        ),
        "cosine_coefficients": design.coefficients.tolist(),
        "minimum_weight": float(np.min(weights)),
        "maximum_density": float(sample_count * np.max(weights)),
        "continuous_minimum_density": extrema["minimum"],
        "continuous_maximum_density": extrema["maximum"],
        "continuum_exchange_rounds": continuum_round,
        "continuum_extremum_cuts": continuum_cuts,
        "lower_fejer_riesz_residual": lower_factor.residual,
        "upper_fejer_riesz_residual": upper_factor.residual,
        "fejer_riesz_factor_margin": factor_margin,
        "certified_continuous_density_floor": lower_certified_floor,
        "certified_continuous_cap_gap": upper_certified_gap,
        "lower_fejer_riesz_factor": np.real_if_close(
            lower_factor.factor_coefficients
        ).tolist(),
        "upper_fejer_riesz_factor": np.real_if_close(
            upper_factor.factor_coefficients
        ).tolist(),
        "effective_sample_count": float(1.0 / np.sum(weights**2)),
        "lambda_min": float(np.linalg.eigvalsh(gram)[0]),
        "gershgorin_radius": radius,
        "gershgorin_lower_bound": 1.0 - radius,
        "required_gershgorin_lower_bound": gershgorin_lower_bound,
        "first_alias_frequency": float(
            2.0 * math.pi * sample_count / observation_time
        ),
        "first_alias_magnitude": exact_alias_magnitude(design),
        "prealias_limit": prealias_limit(design),
        "design_tail_cutoff": design_tail_cutoff,
    }
    return design, report


def complete_design_report(
    maximum_norm: int = 50,
    sigma: float = 2.0,
    observation_time: float = 1_000.0,
    sample_count: int = 5_000,
    harmonic_count: int = 4,
    design_tail_cutoff: int = 500,
    certificate_truncation: int = 1_000_000,
    gershgorin_lower_bound: float = 0.98,
    density_cap: float = 2.5,
    noise_sigma: float = 0.01,
) -> dict[str, object]:
    design, optimization = optimize_cosine_quadrature(
        maximum_norm,
        sigma,
        observation_time,
        sample_count,
        harmonic_count,
        design_tail_cutoff,
        gershgorin_lower_bound,
        density_cap,
    )
    envelope_coefficients = quadratic_divisor_coefficients_sieve(
        certificate_truncation
    )
    envelope, base_remainder = cosine_quadratic_tail_envelope(
        maximum_norm,
        sigma,
        certificate_truncation,
        design,
        envelope_coefficients,
    )
    gram = cosine_window_gram(maximum_norm, design)
    bounds = deterministic_coefficient_bounds(gram, sigma, envelope)
    noise_covariance = cosine_noise_covariance(maximum_norm, sigma, design)
    safe_required = math.log(float(certificate_truncation + 1))
    return {
        "model": "LP-optimized positive trigonometric midpoint quadrature",
        "maximum_norm": maximum_norm,
        "sigma": sigma,
        "observation_time": observation_time,
        "sample_count": sample_count,
        "harmonic_count": harmonic_count,
        "certificate_truncation": certificate_truncation,
        "finite_certificate_is_prealias_for_all_targets": bool(
            prealias_limit(design) > safe_required
        ),
        "minimum_prealias_limit_required": safe_required,
        "infinite_tail_l1_remainder_before_kernel_decay": base_remainder,
        "worst_complete_tail_coefficient_bound": float(np.max(bounds)),
        "worst_coefficient": int(np.argmax(bounds) + 1),
        "integer_tail_certificate": bool(np.max(bounds) < 0.5),
        "noise_sigma": noise_sigma,
        "gaussian_rounding_failure_bound": (
            deterministic_gaussian_rounding_failure_bound(
                bounds, noise_covariance, noise_sigma
            )
        ),
        "optimization": optimization,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--maximum-norm", type=int, default=50)
    parser.add_argument("--sigma", type=float, default=2.0)
    parser.add_argument("--observation-time", type=float, default=1_000.0)
    parser.add_argument("--sample-count", type=int, default=5_000)
    parser.add_argument("--harmonics", type=int, default=4)
    parser.add_argument("--design-tail-cutoff", type=int, default=500)
    parser.add_argument("--certificate-truncation", type=int, default=1_000_000)
    parser.add_argument("--gershgorin-lower-bound", type=float, default=0.98)
    parser.add_argument("--density-cap", type=float, default=2.5)
    parser.add_argument("--noise-sigma", type=float, default=0.01)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    print(
        json.dumps(
            complete_design_report(
                arguments.maximum_norm,
                arguments.sigma,
                arguments.observation_time,
                arguments.sample_count,
                arguments.harmonics,
                arguments.design_tail_cutoff,
                arguments.certificate_truncation,
                arguments.gershgorin_lower_bound,
                arguments.density_cap,
                arguments.noise_sigma,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
