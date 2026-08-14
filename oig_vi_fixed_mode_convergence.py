#!/usr/bin/env python3
"""Stage VI audit of fixed-mode directed-response convergence.

This laboratory uses the cell-centred Neumann model from OIG Stage V with

* source modes k=1,...,5;
* target background rho(y)=1+(2/5)sqrt(2) cos(pi y);
* target mode ell=1;
* interaction strength g=4/5; and
* nine exact rational positive observation times.

It separates four levels of evidence:

1. exact normalization and dense/modal identities;
2. high-precision convergence measurements;
3. analytic O(n^-2) expansions on every fixed modal block; and
4. a rigorous Galerkin-tail bound proving continuum convergence after the
   limits n->infinity and then P->infinity.

The observed full response has a clean second-order rate.  The fixed-block
theorem plus tail bound proves convergence, but this file does not claim that
the two estimates by themselves prove a uniform full-history O(n^-2) rate.
That rate is established separately in OIG_VI_FIXED_MODE_RESPONSE_THEOREM.md
by a lumped-mass finite-element argument.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import sys
from fractions import Fraction
from typing import Iterable, Sequence

import mpmath as mp
import numpy as np
import flint
import scipy
from flint import arb, arb_mat, ctx, fmpq
from scipy.linalg import eigh, expm, expm_frechet


AMPLITUDE = Fraction(2, 5)
INTERACTION_STRENGTH = Fraction(4, 5)
TARGET_MODE = 1
SOURCE_MODES = (1, 2, 3, 4, 5)
OBSERVATION_TIMES = (
    Fraction(1, 1000),
    Fraction(1, 500),
    Fraction(1, 200),
    Fraction(1, 100),
    Fraction(1, 50),
    Fraction(1, 20),
    Fraction(1, 10),
    Fraction(1, 5),
    Fraction(1, 2),
)


def _mode_scale(mode: int) -> float:
    return 1.0 if mode == 0 else math.sqrt(2.0)


def cosine_mode_samples(
    side_length: int, mode_indices: Sequence[int]
) -> np.ndarray:
    """Return orthonormal cell-centred Neumann cosine samples."""
    if side_length < 2:
        raise ValueError("side_length must be at least two")
    modes = tuple(int(mode) for mode in mode_indices)
    if any(mode < 0 or mode >= side_length for mode in modes):
        raise ValueError("mode indices must lie between zero and n-1")
    cells = np.arange(side_length, dtype=float) + 0.5
    columns = []
    for mode in modes:
        if mode == 0:
            columns.append(np.ones(side_length) / math.sqrt(side_length))
        else:
            columns.append(
                math.sqrt(2.0 / side_length)
                * np.cos(math.pi * mode * cells / side_length)
            )
    return np.column_stack(columns)


def scaled_path_eigenvalue(side_length: int, mode: int) -> float:
    """Return mu_n,k=4n^2 sin^2(pi k/(2n))."""
    if side_length < 2 or not 0 <= mode < side_length:
        raise ValueError("invalid side length or mode")
    return 4.0 * side_length**2 * math.sin(
        math.pi * mode / (2.0 * side_length)
    ) ** 2


def _continuum_cosine_integral(mode: int) -> float:
    """Return integral_0^1 x cos(mode*pi*x) dx."""
    if mode == 0:
        return 0.5
    return (((-1) ** mode) - 1.0) / (math.pi * mode) ** 2


def _discrete_cosine_midpoint(side_length: int, mode: int) -> float:
    """Return n^-1 sum_j x_j cos(mode*pi*x_j) in closed form."""
    if mode == 0:
        return 0.5
    if not 0 < mode < 2 * side_length:
        raise ValueError("closed form requires 0 < mode < 2n")
    if mode % 2 == 0:
        return 0.0
    angle = math.pi * mode / (2.0 * side_length)
    return -math.cos(angle) / (
        2.0 * side_length**2 * math.sin(angle) ** 2
    )


def continuum_multiplication_entry(left_mode: int, right_mode: int) -> float:
    """Return <phi_p,x phi_q> in the continuum Neumann cosine basis."""
    if left_mode < 0 or right_mode < 0:
        raise ValueError("modes must be nonnegative")
    return (
        _mode_scale(left_mode)
        * _mode_scale(right_mode)
        / 2.0
        * (
            _continuum_cosine_integral(abs(left_mode - right_mode))
            + _continuum_cosine_integral(left_mode + right_mode)
        )
    )


def discrete_multiplication_entry(
    side_length: int, left_mode: int, right_mode: int
) -> float:
    """Return the exact cell-midpoint sum <phi_p,x phi_q>_n."""
    if min(left_mode, right_mode) < 0 or max(left_mode, right_mode) >= side_length:
        raise ValueError("discrete modes must lie between zero and n-1")
    return (
        _mode_scale(left_mode)
        * _mode_scale(right_mode)
        / 2.0
        * (
            _discrete_cosine_midpoint(
                side_length, abs(left_mode - right_mode)
            )
            + _discrete_cosine_midpoint(side_length, left_mode + right_mode)
        )
    )


def continuum_modal_generator(
    maximum_mode: int,
    target_mode: int = TARGET_MODE,
    interaction_strength: float = float(INTERACTION_STRENGTH),
) -> np.ndarray:
    """Return the continuum cosine-Galerkin response generator."""
    if maximum_mode < max(SOURCE_MODES) or target_mode < 1:
        raise ValueError("modal cutoff must contain all declared modes")
    modes = np.arange(maximum_mode + 1, dtype=float)
    eigenvalues = (math.pi * modes) ** 2
    target_rate = (math.pi * target_mode) ** 2
    multiplication = np.asarray(
        [
            [
                continuum_multiplication_entry(left, right)
                for right in range(maximum_mode + 1)
            ]
            for left in range(maximum_mode + 1)
        ]
    )
    return (
        np.diag(eigenvalues + target_rate)
        + target_rate * interaction_strength * multiplication
    )


def discrete_modal_generator(
    side_length: int,
    maximum_mode: int | None = None,
    target_mode: int = TARGET_MODE,
    interaction_strength: float = float(INTERACTION_STRENGTH),
) -> np.ndarray:
    """Return the finite response generator in its exact DCT basis."""
    if maximum_mode is None:
        maximum_mode = side_length - 1
    if not max(SOURCE_MODES) <= maximum_mode < side_length:
        raise ValueError("modal cutoff must contain sources and be below n")
    modes = np.arange(maximum_mode + 1)
    eigenvalues = np.asarray(
        [scaled_path_eigenvalue(side_length, int(mode)) for mode in modes]
    )
    target_rate = scaled_path_eigenvalue(side_length, target_mode)
    multiplication = np.asarray(
        [
            [
                discrete_multiplication_entry(side_length, left, right)
                for right in range(maximum_mode + 1)
            ]
            for left in range(maximum_mode + 1)
        ]
    )
    return (
        np.diag(eigenvalues + target_rate)
        + target_rate * interaction_strength * multiplication
    )


def _history_from_modal_generator(
    generator: np.ndarray,
    observation_times: Sequence[float],
    source_modes: Sequence[int] = SOURCE_MODES,
    amplitude: float = float(AMPLITUDE),
) -> np.ndarray:
    values, vectors = eigh(np.asarray(generator, dtype=float), check_finite=True)
    left = vectors[0, :]
    right = vectors[np.asarray(source_modes, dtype=int), :].T
    return np.asarray(
        [
            amplitude * ((left * np.exp(-float(time) * values)) @ right)
            for time in observation_times
        ]
    )


def discrete_response_history(
    side_length: int,
    observation_times: Sequence[float] = tuple(map(float, OBSERVATION_TIMES)),
) -> np.ndarray:
    """Return the complete finite fixed-mode response via modal reduction."""
    return _history_from_modal_generator(
        discrete_modal_generator(side_length), observation_times
    )


def continuum_galerkin_response_history(
    maximum_mode: int,
    observation_times: Sequence[float] = tuple(map(float, OBSERVATION_TIMES)),
) -> np.ndarray:
    """Return a continuum cosine-Galerkin fixed-mode response history."""
    return _history_from_modal_generator(
        continuum_modal_generator(maximum_mode), observation_times
    )


def normalization_audit(side_length: int = 32) -> dict[str, object]:
    """Audit every density/probability normalization used in the response."""
    if side_length <= max(SOURCE_MODES):
        raise ValueError("side length must contain the declared source modes")
    all_modes = cosine_mode_samples(side_length, (0,) + SOURCE_MODES)
    source = cosine_mode_samples(side_length, SOURCE_MODES)
    target = cosine_mode_samples(side_length, (TARGET_MODE,))[:, 0]
    uniform = np.ones(side_length) / side_length
    background = uniform + float(AMPLITUDE) / math.sqrt(side_length) * target
    source_probability = source / math.sqrt(side_length)
    source_density_samples = side_length * source_probability
    source_density_gram = source_density_samples.T @ source_density_samples / side_length
    target_coefficient = float(target @ background)
    return {
        "side_length": side_length,
        "maximum_dct_orthonormality_error": float(
            np.max(np.abs(all_modes.T @ all_modes - np.eye(all_modes.shape[1])))
        ),
        "maximum_source_density_l2_gram_error": float(
            np.max(np.abs(source_density_gram - np.eye(len(SOURCE_MODES))))
        ),
        "source_probability_column_sums_maximum": float(
            np.max(np.abs(np.sum(source_probability, axis=0)))
        ),
        "target_probability_mass_error": float(abs(np.sum(background) - 1.0)),
        "target_probability_minimum": float(np.min(background)),
        "target_mode_probability_coefficient": target_coefficient,
        "density_normalized_target_coefficient": float(
            math.sqrt(side_length) * target_coefficient
        ),
        "declared_amplitude": float(AMPLITUDE),
        "response_at_time_zero_norm": float(
            np.linalg.norm(discrete_response_history(side_length, (0.0,)))
        ),
        "normalization_identity": (
            "source probability=U_k/sqrt(n), target density coefficient="
            "sqrt(n)<u_l,p_B>, so the reduced response is "
            "a e_0^T exp(-tK_n) e_k"
        ),
    }


def _path_laplacian(side_length: int) -> np.ndarray:
    diagonal = np.r_[1.0, np.full(side_length - 2, 2.0), 1.0]
    return (
        np.diag(diagonal)
        - np.diag(np.ones(side_length - 1), 1)
        - np.diag(np.ones(side_length - 1), -1)
    )


def dense_joint_response_history(
    side_length: int,
    observation_times: Sequence[float] = tuple(map(float, OBSERVATION_TIMES)),
) -> np.ndarray:
    """Return the same response from the dense n^2-state construction."""
    n = side_length
    if n <= max(SOURCE_MODES):
        raise ValueError("dense audit requires all five source modes")
    laplacian = n**2 * _path_laplacian(n)
    positions = (np.arange(n, dtype=float) + 0.5) / n
    target = cosine_mode_samples(n, (TARGET_MODE,))[:, 0]
    source = cosine_mode_samples(n, SOURCE_MODES)
    background = (
        np.ones(n) / n + float(AMPLITUDE) / math.sqrt(n) * target
    )
    generator = (
        np.kron(laplacian, np.eye(n))
        + np.kron(np.eye(n), laplacian)
        + float(INTERACTION_STRENGTH)
        * np.kron(np.diag(positions), laplacian)
    )
    injection = np.kron(source / math.sqrt(n), background[:, None])
    target_density_port = np.kron(np.ones((1, n)), (math.sqrt(n) * target)[None, :])
    return np.vstack(
        [
            target_density_port
            @ expm(-float(time) * generator)
            @ injection
            for time in observation_times
        ]
    )


def dense_modal_agreement_audit(
    side_lengths: Sequence[int] = (6, 7, 8),
    observation_times: Sequence[float] = (0.001, 0.01, 0.1, 0.5),
) -> dict[str, object]:
    """Compare the n^2 dense response with the n-mode reduction."""
    rows = []
    for side_length in side_lengths:
        dense = dense_joint_response_history(side_length, observation_times)
        modal = discrete_response_history(side_length, observation_times)
        difference = dense - modal
        rows.append(
            {
                "side_length": int(side_length),
                "maximum_absolute_entry_error": float(np.max(np.abs(difference))),
                "relative_frobenius_error": float(
                    np.linalg.norm(difference)
                    / max(np.linalg.norm(dense), np.finfo(float).tiny)
                ),
            }
        )
    return {
        "rows": rows,
        "maximum_absolute_entry_error": max(
            row["maximum_absolute_entry_error"] for row in rows
        ),
        "identity": (
            "target-mode conjugation block-diagonalizes the n^2 generator; "
            "the comparison audits implementation and normalization"
        ),
    }


def continuum_galerkin_tail_row_bound(
    maximum_mode: int,
    physical_time: float,
    source_mode_count: int = len(SOURCE_MODES),
) -> float:
    """Bound the response-row error from discarding modes above P.

    With P the projection onto modes 0,...,maximum_mode, the off-block part of
    multiplication by x has norm at most 1/2.  A two-step block-Duhamel bound
    gives the stated expression.
    """
    if maximum_mode < max(SOURCE_MODES) or physical_time < 0.0:
        raise ValueError("invalid cutoff or time")
    target_rate = (math.pi * TARGET_MODE) ** 2
    high_gap = (math.pi * (maximum_mode + 1)) ** 2
    off_block = target_rate * float(INTERACTION_STRENGTH) / 2.0
    if physical_time == 0.0:
        return 0.0
    bracket = physical_time - (-math.expm1(-high_gap * physical_time)) / high_gap
    operator_bound = (
        off_block**2
        * math.exp(-target_rate * physical_time)
        / high_gap
        * max(0.0, bracket)
    )
    return float(AMPLITUDE) * math.sqrt(source_mode_count) * operator_bound


def continuum_galerkin_tail_audit(
    cutoffs: Sequence[int] = (16, 32, 64, 128, 256),
    reference_cutoff: int = 512,
) -> dict[str, object]:
    """Compare Galerkin stabilization with a rigorous analytic tail envelope."""
    times = tuple(map(float, OBSERVATION_TIMES))
    reference = continuum_galerkin_response_history(reference_cutoff, times)
    rows = []
    for cutoff in cutoffs:
        history = continuum_galerkin_response_history(cutoff, times)
        row_bounds = [
            continuum_galerkin_tail_row_bound(cutoff, time) for time in times
        ]
        history_bound = float(np.linalg.norm(row_bounds))
        actual_difference = float(np.linalg.norm(history - reference))
        gram = history.T @ history
        gram_bound = history_bound * (
            2.0 * float(np.linalg.norm(history)) + history_bound
        )
        rows.append(
            {
                "maximum_mode": int(cutoff),
                "difference_from_empirical_reference": actual_difference,
                "rigorous_history_tail_bound": history_bound,
                "empirical_difference_below_tail_bound": bool(
                    actual_difference <= history_bound
                ),
                "rigorous_gram_tail_bound": gram_bound,
                "history_frobenius_norm": float(np.linalg.norm(history)),
                "gram_frobenius_norm": float(np.linalg.norm(gram)),
            }
        )
    return {
        "reference_cutoff": reference_cutoff,
        "rows": rows,
        "proved_bound": (
            "a sqrt(m) b^2 exp(-lambda t)/nu * "
            "[t-(1-exp(-nu t))/nu], b=lambda g/2, "
            "nu=pi^2(P+1)^2"
        ),
        "scope": (
            "the bound encloses the unknown infinite-dimensional tail; the "
            "difference to a larger Galerkin matrix is shown only as a check"
        ),
    }


def empirical_full_response_convergence(
    side_lengths: Sequence[int] = (
        8,
        12,
        16,
        24,
        32,
        48,
        64,
        96,
        128,
        192,
        256,
    ),
    continuum_cutoff: int = 256,
) -> dict[str, object]:
    """Estimate convergence orders without promoting them to a proof."""
    times = tuple(map(float, OBSERVATION_TIMES))
    reference = continuum_galerkin_response_history(continuum_cutoff, times)
    reference_gram = reference.T @ reference
    histories: dict[int, np.ndarray] = {}
    rows = []
    for side_length in side_lengths:
        history = discrete_response_history(side_length, times)
        histories[int(side_length)] = history
        gram = history.T @ history
        history_error = float(
            np.linalg.norm(history - reference) / np.linalg.norm(reference)
        )
        gram_error = float(
            np.linalg.norm(gram - reference_gram) / np.linalg.norm(reference_gram)
        )
        rows.append(
            {
                "side_length": int(side_length),
                "relative_history_error_against_galerkin_reference": history_error,
                "relative_gram_error_against_galerkin_reference": gram_error,
                "n_squared_times_history_error": side_length**2 * history_error,
                "n_squared_times_gram_error": side_length**2 * gram_error,
            }
        )

    row_by_side = {row["side_length"]: row for row in rows}
    doubling_rows = []
    for side_length in side_lengths:
        side = int(side_length)
        if 2 * side not in histories:
            continue
        left = row_by_side[side]
        right = row_by_side[2 * side]
        extrapolated = (4.0 * histories[2 * side] - histories[side]) / 3.0
        doubling_rows.append(
            {
                "side_length_pair": [side, 2 * side],
                "observed_history_order": float(
                    math.log(
                        left["relative_history_error_against_galerkin_reference"]
                        / right[
                            "relative_history_error_against_galerkin_reference"
                        ],
                        2.0,
                    )
                ),
                "observed_gram_order": float(
                    math.log(
                        left["relative_gram_error_against_galerkin_reference"]
                        / right["relative_gram_error_against_galerkin_reference"],
                        2.0,
                    )
                ),
                "richardson_history_relative_error": float(
                    np.linalg.norm(extrapolated - reference)
                    / np.linalg.norm(reference)
                ),
            }
        )

    cauchy_rows = []
    for side_length in side_lengths:
        side = int(side_length)
        if 2 * side not in histories or 4 * side not in histories:
            continue
        first = float(np.linalg.norm(histories[side] - histories[2 * side]))
        second = float(
            np.linalg.norm(histories[2 * side] - histories[4 * side])
        )
        cauchy_rows.append(
            {
                "side_lengths": [side, 2 * side, 4 * side],
                "reference_free_cauchy_order": math.log(first / second, 2.0),
            }
        )

    fit_rows = [row for row in rows if row["side_length"] >= 16]
    history_slope = np.polyfit(
        np.log([row["side_length"] for row in fit_rows]),
        np.log(
            [
                row["relative_history_error_against_galerkin_reference"]
                for row in fit_rows
            ]
        ),
        1,
    )[0]
    gram_slope = np.polyfit(
        np.log([row["side_length"] for row in fit_rows]),
        np.log(
            [
                row["relative_gram_error_against_galerkin_reference"]
                for row in fit_rows
            ]
        ),
        1,
    )[0]
    return {
        "continuum_galerkin_reference_cutoff": continuum_cutoff,
        "observation_times_exact": [
            f"{time.numerator}/{time.denominator}" for time in OBSERVATION_TIMES
        ],
        "rows": rows,
        "doubling_rows": doubling_rows,
        "reference_free_cauchy_rows": cauchy_rows,
        "log_log_fitted_history_order": float(-history_slope),
        "log_log_fitted_gram_order": float(-gram_slope),
        "epistemic_status": (
            "empirical full-response rate; the reference is a stabilized "
            "Galerkin calculation, not an interval enclosure of the continuum"
        ),
    }


def continuum_first_jet(mode: int) -> float:
    """Return the exact continuum first response derivative."""
    if mode < 1:
        raise ValueError("source mode must be positive")
    if mode % 2 == 0:
        return 0.0
    return (
        2.0
        * math.sqrt(2.0)
        * float(AMPLITUDE)
        * float(INTERACTION_STRENGTH)
        * TARGET_MODE**2
        / mode**2
    )


def discrete_first_jet(side_length: int, mode: int) -> float:
    """Return the closed finite-n first derivative for one source mode."""
    if not 1 <= mode < side_length:
        raise ValueError("invalid source mode")
    if mode % 2 == 0:
        return 0.0
    return (
        2.0
        * math.sqrt(2.0)
        * float(AMPLITUDE)
        * float(INTERACTION_STRENGTH)
        * scaled_path_eigenvalue(side_length, TARGET_MODE)
        / scaled_path_eigenvalue(side_length, mode)
        * math.cos(math.pi * mode / (2.0 * side_length))
    )


def first_jet_relative_error_bound(side_length: int, odd_mode: int) -> float:
    """Return a proved elementary relative-error bound for an odd mode."""
    if odd_mode % 2 == 0 or not 1 <= odd_mode < side_length:
        raise ValueError("an odd source mode below n is required")
    x = math.pi * odd_mode / (2.0 * side_length)
    y = math.pi * TARGET_MODE / (2.0 * side_length)
    upper = (1.0 - x**2 / 6.0) ** -2
    lower = (1.0 - y**2 / 3.0) * (1.0 - x**2 / 2.0)
    return max(upper - 1.0, 1.0 - lower)


def first_jet_convergence_audit(
    side_lengths: Sequence[int] = (8, 16, 32, 64, 128, 256),
) -> dict[str, object]:
    """Audit exact parity and the proved O(n^-2) jet bound."""
    rows = []
    for side_length in side_lengths:
        values = [
            discrete_first_jet(side_length, mode) for mode in SOURCE_MODES
        ]
        limits = [continuum_first_jet(mode) for mode in SOURCE_MODES]
        odd_relative_errors = []
        bounds = []
        for mode, value, limit in zip(SOURCE_MODES, values, limits):
            if mode % 2:
                odd_relative_errors.append(abs(value / limit - 1.0))
                bounds.append(first_jet_relative_error_bound(side_length, mode))
        rows.append(
            {
                "side_length": int(side_length),
                "finite_first_jet": values,
                "maximum_odd_relative_error": max(odd_relative_errors),
                "maximum_proved_relative_error_bound": max(bounds),
                "bound_violation": max(
                    error - bound
                    for error, bound in zip(odd_relative_errors, bounds)
                ),
                "maximum_even_absolute_value": max(
                    abs(values[index]) for index in (1, 3)
                ),
            }
        )
    return {
        "continuum_first_jet": [
            continuum_first_jet(mode) for mode in SOURCE_MODES
        ],
        "exact_odd_mode_formula": (
            "d_n,k=2 sqrt(2) a g (mu_n,ell/mu_n,k) "
            "cos(k pi/(2n)); d_n,k=0 for even k"
        ),
        "proved_relative_bound": (
            "max((1-x^2/6)^(-2)-1, "
            "1-(1-y^2/3)(1-x^2/2)), "
            "x=k pi/(2n), y=ell pi/(2n)"
        ),
        "rows": rows,
    }


def _mp_mode_scale(mode: int) -> mp.mpf:
    return mp.mpf(1) if mode == 0 else mp.sqrt(2)


def _mp_continuum_i(mode: int) -> mp.mpf:
    if mode == 0:
        return mp.mpf(1) / 2
    return (mp.mpf((-1) ** mode) - 1) / (mp.pi * mode) ** 2


def _mp_discrete_i(side_length: int, mode: int) -> mp.mpf:
    if mode == 0:
        return mp.mpf(1) / 2
    if mode % 2 == 0:
        return mp.mpf(0)
    angle = mp.pi * mode / (2 * side_length)
    return -mp.cos(angle) / (2 * side_length**2 * mp.sin(angle) ** 2)


def _mp_modal_generator(side_length: int | None, maximum_mode: int) -> mp.matrix:
    dimension = maximum_mode + 1
    matrix = mp.matrix(dimension)
    strength = mp.mpf(INTERACTION_STRENGTH.numerator) / INTERACTION_STRENGTH.denominator
    if side_length is None:
        rates = [(mp.pi * mode) ** 2 for mode in range(dimension)]
        target_rate = (mp.pi * TARGET_MODE) ** 2
        integral = _mp_continuum_i
    else:
        rates = [
            4
            * side_length**2
            * mp.sin(mp.pi * mode / (2 * side_length)) ** 2
            for mode in range(dimension)
        ]
        target_rate = rates[TARGET_MODE]
        integral = lambda mode: _mp_discrete_i(side_length, mode)
    for left in range(dimension):
        for right in range(dimension):
            multiplication = (
                _mp_mode_scale(left)
                * _mp_mode_scale(right)
                / 2
                * (integral(abs(left - right)) + integral(left + right))
            )
            matrix[left, right] = target_rate * strength * multiplication
            if left == right:
                matrix[left, right] += rates[left] + target_rate
    return matrix


def _mp_history(generator: mp.matrix) -> list[list[mp.mpf]]:
    values, vectors = mp.eigsy(generator)
    amplitude = mp.mpf(AMPLITUDE.numerator) / AMPLITUDE.denominator
    rows = []
    for rational_time in OBSERVATION_TIMES:
        time = mp.mpf(rational_time.numerator) / rational_time.denominator
        row = []
        for source_mode in SOURCE_MODES:
            value = mp.mpf(0)
            for eigenmode in range(generator.rows):
                value += (
                    vectors[0, eigenmode]
                    * mp.exp(-time * values[eigenmode])
                    * vectors[source_mode, eigenmode]
                )
            row.append(amplitude * value)
        rows.append(row)
    return rows


def _mp_frobenius(matrix: Sequence[Sequence[mp.mpf]]) -> mp.mpf:
    return mp.sqrt(sum(value * value for row in matrix for value in row))


def high_precision_response_audit(
    side_lengths: Sequence[int] = (8, 16, 32, 64),
    continuum_cutoff: int = 64,
    decimal_digits: int = 70,
) -> dict[str, object]:
    """Recompute selected responses with arbitrary-precision eigensolvers."""
    if decimal_digits < 40:
        raise ValueError("at least 40 decimal digits are required")
    rows = []
    with mp.workdps(decimal_digits):
        reference = _mp_history(_mp_modal_generator(None, continuum_cutoff))
        reference_norm = _mp_frobenius(reference)
        for side_length in side_lengths:
            if side_length <= max(SOURCE_MODES):
                raise ValueError("all side lengths must contain source modes")
            history = _mp_history(
                _mp_modal_generator(side_length, side_length - 1)
            )
            difference = [
                [value - target for value, target in zip(row, reference_row)]
                for row, reference_row in zip(history, reference)
            ]
            relative = _mp_frobenius(difference) / reference_norm
            double_history = discrete_response_history(
                side_length, tuple(map(float, OBSERVATION_TIMES))
            )
            maximum_double_error = max(
                abs(history[row][column] - double_history[row, column])
                for row in range(len(OBSERVATION_TIMES))
                for column in range(len(SOURCE_MODES))
            )
            rows.append(
                {
                    "side_length": int(side_length),
                    "relative_error_against_high_precision_galerkin": mp.nstr(
                        relative, 30
                    ),
                    "relative_error_float": float(relative),
                    "maximum_double_vs_high_precision_entry_error": mp.nstr(
                        maximum_double_error, 12
                    ),
                    "maximum_double_vs_high_precision_entry_error_float": float(
                        maximum_double_error
                    ),
                }
            )
    row_by_side = {row["side_length"]: row for row in rows}
    orders = []
    for side_length in side_lengths:
        side = int(side_length)
        if 2 * side in row_by_side:
            orders.append(
                {
                    "side_length_pair": [side, 2 * side],
                    "observed_order": math.log(
                        row_by_side[side]["relative_error_float"]
                        / row_by_side[2 * side]["relative_error_float"],
                        2.0,
                    ),
                }
            )
    return {
        "decimal_digits": decimal_digits,
        "continuum_galerkin_cutoff": continuum_cutoff,
        "rows": rows,
        "doubling_orders": orders,
        "scope": (
            "high precision controls floating roundoff; finite Galerkin "
            "truncation is controlled separately by the analytic tail bound"
        ),
    }


def _arb_fraction(value: Fraction | int) -> arb:
    if isinstance(value, int):
        return arb(value)
    return arb(fmpq(value.numerator, value.denominator))


def _arb_mode_scale(mode: int) -> arb:
    return arb(1) if mode == 0 else arb(2).sqrt()


def _arb_continuum_i(mode: int) -> arb:
    if mode == 0:
        return _arb_fraction(Fraction(1, 2))
    return arb(((-1) ** mode) - 1) / (arb(mode) * arb.pi()) ** 2


def _arb_discrete_i(side_length: int, mode: int) -> arb:
    if mode == 0:
        return _arb_fraction(Fraction(1, 2))
    if mode % 2 == 0:
        return arb(0)
    angle = arb.pi() * mode / (2 * side_length)
    return -angle.cos() / (2 * side_length**2 * angle.sin() ** 2)


def _arb_fixed_block(side_length: int | None, maximum_mode: int) -> arb_mat:
    dimension = maximum_mode + 1
    matrix = arb_mat(dimension, dimension)
    strength = _arb_fraction(INTERACTION_STRENGTH)
    if side_length is None:
        rates = [(arb.pi() * mode) ** 2 for mode in range(dimension)]
        target_rate = (arb.pi() * TARGET_MODE) ** 2
        integral = _arb_continuum_i
    else:
        rates = [
            4
            * side_length**2
            * (arb.pi() * mode / (2 * side_length)).sin() ** 2
            for mode in range(dimension)
        ]
        target_rate = rates[TARGET_MODE]
        integral = lambda mode: _arb_discrete_i(side_length, mode)
    for left in range(dimension):
        for right in range(dimension):
            multiplication = (
                _arb_mode_scale(left)
                * _arb_mode_scale(right)
                / 2
                * (integral(abs(left - right)) + integral(left + right))
            )
            matrix[left, right] = target_rate * strength * multiplication
            if left == right:
                matrix[left, right] += rates[left] + target_rate
    return matrix


def _arb_asymptotic_correction(maximum_mode: int) -> arb_mat:
    """Return E_P in K_n,P=K_P+n^-2 E_P+O(n^-4)."""
    dimension = maximum_mode + 1
    matrix = arb_mat(dimension, dimension)
    pi = arb.pi()
    target = (pi * TARGET_MODE) ** 2
    strength = _arb_fraction(INTERACTION_STRENGTH)
    for left in range(dimension):
        left_rate = (pi * left) ** 2
        for right in range(dimension):
            multiplication = (
                _arb_mode_scale(left)
                * _arb_mode_scale(right)
                / 2
                * (
                    _arb_continuum_i(abs(left - right))
                    + _arb_continuum_i(left + right)
                )
            )
            midpoint_coefficient = (
                _arb_mode_scale(left) * _arb_mode_scale(right) / 12
                if (left + right) % 2
                else arb(0)
            )
            value = (
                -(target**2) / 12 * strength * multiplication
                + target * strength * midpoint_coefficient
            )
            if left == right:
                value += -(left_rate**2) / 12 - (target**2) / 12
            matrix[left, right] = value
    return matrix


def fixed_block_asymptotic_correction(maximum_mode: int = 5) -> np.ndarray:
    """Return E_P in K_n,P=K_P+n^-2 E_P+O_P(n^-4)."""
    dimension = maximum_mode + 1
    matrix = np.zeros((dimension, dimension))
    target = (math.pi * TARGET_MODE) ** 2
    strength = float(INTERACTION_STRENGTH)
    for left in range(dimension):
        left_rate = (math.pi * left) ** 2
        for right in range(dimension):
            multiplication = continuum_multiplication_entry(left, right)
            midpoint_coefficient = (
                _mode_scale(left) * _mode_scale(right) / 12.0
                if (left + right) % 2
                else 0.0
            )
            value = (
                -(target**2) / 12.0 * strength * multiplication
                + target * strength * midpoint_coefficient
            )
            if left == right:
                value += -(left_rate**2) / 12.0 - (target**2) / 12.0
            matrix[left, right] = value
    return matrix


def _arb_frobenius(matrix: arb_mat) -> arb:
    total = arb(0)
    for value in matrix.entries():
        total += value * value
    return total.sqrt()


def interval_fixed_block_expansion_audit(
    side_lengths: Sequence[int] = (8, 12, 16, 24, 32, 48, 64, 96, 128),
    maximum_mode: int = 5,
    precision_bits: int = 192,
) -> dict[str, object]:
    """Outward-certify finite instances of the fixed-block expansion."""
    if precision_bits < 128:
        raise ValueError("at least 128 bits are required")
    first_cap = Fraction(6000)
    remainder_cap = Fraction(50000)
    rows = []
    with ctx.workprec(precision_bits):
        continuum = _arb_fixed_block(None, maximum_mode)
        correction = _arb_asymptotic_correction(maximum_mode)
        for side_length in side_lengths:
            if side_length <= maximum_mode or 2 * maximum_mode >= 2 * side_length:
                raise ValueError("side length must exceed the fixed cutoff")
            finite = _arb_fixed_block(int(side_length), maximum_mode)
            difference = finite - continuum
            scaled = difference * side_length**2
            remainder = (scaled - correction) * side_length**2
            scaled_norm = _arb_frobenius(scaled)
            remainder_norm = _arb_frobenius(remainder)
            rows.append(
                {
                    "side_length": int(side_length),
                    "n_squared_block_error_interval": str(scaled_norm),
                    "n_fourth_remainder_interval": str(remainder_norm),
                    "n_squared_block_error_approximate": float(scaled_norm.mid()),
                    "n_fourth_remainder_approximate": float(
                        remainder_norm.mid()
                    ),
                    "first_bound_verified": bool(
                        scaled_norm < _arb_fraction(first_cap)
                    ),
                    "remainder_bound_verified": bool(
                        remainder_norm < _arb_fraction(remainder_cap)
                    ),
                }
            )
    return {
        "precision_bits": precision_bits,
        "maximum_mode": maximum_mode,
        "exact_first_bound": f"{first_cap.numerator}/{first_cap.denominator}",
        "exact_remainder_bound": (
            f"{remainder_cap.numerator}/{remainder_cap.denominator}"
        ),
        "all_bounds_verified": all(
            row["first_bound_verified"] and row["remainder_bound_verified"]
            for row in rows
        ),
        "expansion": (
            "K_n,P=K_P+n^-2 E_P+O_P(n^-4), derived from the exact "
            "sine eigenvalues and midpoint cosine sums"
        ),
        "rows": rows,
        "scope": (
            "outward certification of the declared finite n list; the "
            "symbolic fixed-P big-O expansion is analytic"
        ),
    }


def fixed_block_semigroup_theorem_audit(
    side_lengths: Sequence[int] = (8, 16, 32, 64, 128),
    maximum_mode: int = 5,
) -> dict[str, object]:
    """Compare fixed-block histories with the explicit n^-2 perturbation bound."""
    times = tuple(map(float, OBSERVATION_TIMES))
    continuum = _history_from_modal_generator(
        continuum_modal_generator(maximum_mode), times
    )
    continuum_generator = continuum_modal_generator(maximum_mode)
    generator_correction = fixed_block_asymptotic_correction(maximum_mode)
    leading_history_correction = np.asarray(
        [
            float(AMPLITUDE)
            * expm_frechet(
                -time * continuum_generator,
                -time * generator_correction,
                compute_expm=False,
            )[0, np.asarray(SOURCE_MODES)]
            for time in times
        ]
    )
    rows = []
    block_constant = 6000.0
    for side_length in side_lengths:
        finite = _history_from_modal_generator(
            discrete_modal_generator(side_length, maximum_mode), times
        )
        actual = float(np.linalg.norm(finite - continuum))
        scaled_response_remainder = (
            side_length**2 * (finite - continuum) - leading_history_correction
        )
        contraction_rate = min(
            scaled_path_eigenvalue(side_length, TARGET_MODE),
            (math.pi * TARGET_MODE) ** 2,
        )
        row_bounds = [
            float(AMPLITUDE)
            * math.sqrt(len(SOURCE_MODES))
            * time
            * math.exp(-contraction_rate * time)
            * block_constant
            / side_length**2
            for time in times
        ]
        bound = float(np.linalg.norm(row_bounds))
        rows.append(
            {
                "side_length": int(side_length),
                "actual_fixed_block_history_error": actual,
                "proved_history_error_bound": bound,
                "bound_verified": actual <= bound,
                "n_squared_actual_error": side_length**2 * actual,
                "n_squared_response_remainder": float(
                    np.linalg.norm(scaled_response_remainder)
                ),
                "n_fourth_scaled_response_remainder": float(
                    side_length**2 * np.linalg.norm(scaled_response_remainder)
                ),
            }
        )
    return {
        "maximum_mode": maximum_mode,
        "leading_history_correction_frobenius_norm": float(
            np.linalg.norm(leading_history_correction)
        ),
        "rows": rows,
        "proved_statement": (
            "for each audited n, ||K_n,P-K_P||_2 <= 6000/n^2; "
            "Duhamel contraction gives each response-row error <= "
            "a sqrt(5) t exp(-min(lambda_n,lambda)t) 6000/n^2"
        ),
        "all_bounds_verified": all(row["bound_verified"] for row in rows),
    }


def run_stage_vi_audit(fast: bool = False) -> dict[str, object]:
    """Run the complete Stage VI fixed-mode convergence audit."""
    empirical_sides = (
        (8, 16, 32, 64, 128)
        if fast
        else (8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256)
    )
    high_precision_sides = (8, 16, 32) if fast else (8, 16, 32, 64)
    return {
        "stage": "Operational Information Geometry VI",
        "target": "fixed-mode directed-response convergence",
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "mpmath": mp.__version__,
            "python_flint": flint.__version__,
            "platform": platform.platform(),
        },
        "declared_data": {
            "source_modes": list(SOURCE_MODES),
            "target_mode": TARGET_MODE,
            "background": "rho_B(y)=1+(2/5)sqrt(2)cos(pi y)",
            "interaction_strength": "4/5",
            "observation_times": [
                f"{time.numerator}/{time.denominator}"
                for time in OBSERVATION_TIMES
            ],
            "cell_centres": "x_j=(j+1/2)/n",
        },
        "normalization": normalization_audit(),
        "dense_modal_agreement": dense_modal_agreement_audit((6, 7)),
        "high_precision": high_precision_response_audit(
            high_precision_sides,
            continuum_cutoff=64 if not fast else 48,
            decimal_digits=60 if fast else 70,
        ),
        "empirical_full_response": empirical_full_response_convergence(
            empirical_sides, continuum_cutoff=128 if fast else 256
        ),
        "continuum_galerkin_tail": continuum_galerkin_tail_audit(
            (16, 32, 64, 128) if fast else (16, 32, 64, 128, 256),
            reference_cutoff=256 if fast else 512,
        ),
        "first_causal_jet": first_jet_convergence_audit(),
        "interval_fixed_block_expansion": interval_fixed_block_expansion_audit(),
        "fixed_block_semigroup": fixed_block_semigroup_theorem_audit(),
        "conclusion": {
            "proved": (
                "exact normalization and modal reduction; exact cosine-sum "
                "formula; O(n^-2) first-jet bound; O_P(n^-2) response "
                "convergence on every fixed modal block; explicit continuum "
                "Galerkin tail bound; convergence after n then P limits"
            ),
            "computed": (
                "the complete finite response and its Gram converge at order "
                "2.000 to displayed precision, confirmed with 70-digit "
                "arithmetic and reference-free Cauchy quotients"
            ),
        "not_proved_by_this_laboratory": (
            "the block-tail bounds do not by themselves yield the observed "
            "uniform full-history O(n^-2) rate; the companion analytic memo "
            "proves it by a lumped-mass finite-element argument"
            ),
        },
    }


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fast", action="store_true")
    return parser.parse_args()


def main() -> None:
    arguments = _parse_arguments()
    print(json.dumps(run_stage_vi_audit(arguments.fast), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
