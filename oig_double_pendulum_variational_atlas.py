#!/usr/bin/env python3
"""Tier-1 local-gain atlas on the double-pendulum initial-angle slice.

Every grid cell launches ``(theta1, theta2, 0, 0)``.  The source coordinates
are the two initial angles, injected with
``double_pendulum_variational.angle_slice_source_injection``.  The observation
protocol is exactly the RMS phase feature used by the operational atlas:
unweighted stacked phase-response blocks with output precision
``diag(sample_weights) kron I_6``.

Coarse and fine state/tangent integrations, responses, and information Grams
are compared cell by cell.  A failed comparison is marked unresolved and its
selected gain fields are omitted.  Selected cells also receive independent
centered finite-difference checks of the complete RMS trajectory feature.

This module is numerical Tier-1 evidence.  It makes no outward enclosure,
Lyapunov, infinite-time, or exact OIG-certificate claim.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import platform
from typing import Sequence

import numpy as np
import scipy

from double_pendulum_dynamics import (
    DoublePendulumParameters,
    IntegrationConfig,
    simulate_double_pendulum,
)
from double_pendulum_variational import (
    TIER_1_SCOPE,
    PhaseObservationProtocol,
    analyze_phase_protocol,
    angle_slice_source_injection,
    simulate_double_pendulum_variational,
)
from oig_double_pendulum_atlas import (
    cell_centred_torus_grid,
    trajectory_feature,
)


Array = np.ndarray
SCHEMA_VERSION = "oig-double-pendulum-variational-angle-slice-atlas-v1"
PROOF_BOUNDARY = (
    "All gains, Grams, refinement decisions, and finite-difference checks are "
    "Tier-1 floating-point evidence. Coarse/fine agreement is not an outward "
    "error enclosure, and unresolved masking is not a proof that resolved "
    "cells contain the exact flow response. No Lyapunov, infinite-time, or "
    "exact OIG-certificate claim is made."
)


@dataclass(frozen=True)
class VariationalAngleSliceAtlasConfig:
    """Finite grid, RMS observation, and numerical acceptance declaration."""

    side: int = 7
    duration: float = 2.0
    observation_count: int = 41
    feature_sample_count: int = 9
    sample_weights: tuple[float, ...] | None = None
    state_relative_tolerance: float = 2.0e-7
    tangent_relative_tolerance: float = 2.0e-6
    response_relative_tolerance: float = 2.0e-6
    gram_relative_tolerance: float = 4.0e-6
    weakest_gain_relative_tolerance: float = 2.0e-6
    strongest_gain_relative_tolerance: float = 2.0e-6
    finite_difference_step: float = 1.0e-5
    finite_difference_response_relative_tolerance: float = 2.0e-5
    finite_difference_gram_relative_tolerance: float = 4.0e-5
    finite_difference_weakest_gain_relative_tolerance: float = 2.0e-5
    finite_difference_strongest_gain_relative_tolerance: float = 2.0e-5
    spot_check_cells: tuple[tuple[int, int], ...] = ()

    def __post_init__(self) -> None:
        if type(self.side) is not int or self.side < 3:
            raise ValueError("side must be an integer at least three")
        if type(self.observation_count) is not int or self.observation_count < 3:
            raise ValueError("observation_count must be an integer at least three")
        if (
            type(self.feature_sample_count) is not int
            or not 2 <= self.feature_sample_count <= self.observation_count
        ):
            raise ValueError("feature_sample_count lies outside the observation grid")
        for name in (
            "duration",
            "state_relative_tolerance",
            "tangent_relative_tolerance",
            "response_relative_tolerance",
            "gram_relative_tolerance",
            "weakest_gain_relative_tolerance",
            "strongest_gain_relative_tolerance",
            "finite_difference_step",
            "finite_difference_response_relative_tolerance",
            "finite_difference_gram_relative_tolerance",
            "finite_difference_weakest_gain_relative_tolerance",
            "finite_difference_strongest_gain_relative_tolerance",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")
            object.__setattr__(self, name, value)
        if self.sample_weights is not None:
            weights = tuple(float(value) for value in self.sample_weights)
            if len(weights) != self.feature_sample_count:
                raise ValueError("sample_weights must match feature_sample_count")
            if (
                any(not math.isfinite(value) or value <= 0.0 for value in weights)
            ):
                raise ValueError(
                    "sample_weights must be finite and strictly positive for "
                    "the positive-definite protocol precision"
                )
            object.__setattr__(self, "sample_weights", weights)
        cells: list[tuple[int, int]] = []
        for cell in self.spot_check_cells:
            if (
                not isinstance(cell, tuple)
                or len(cell) != 2
                or any(type(index) is not int for index in cell)
                or any(index < 0 or index >= self.side for index in cell)
            ):
                raise ValueError("spot_check_cells must contain in-grid integer pairs")
            cells.append(cell)
        if len(set(cells)) != len(cells):
            raise ValueError("spot_check_cells must be unique")
        object.__setattr__(self, "spot_check_cells", tuple(cells))


def _sample_indices(config: VariationalAngleSliceAtlasConfig) -> tuple[int, ...]:
    values = np.linspace(
        0,
        config.observation_count - 1,
        config.feature_sample_count,
        dtype=int,
    )
    result = tuple(int(value) for value in values)
    if len(set(result)) != len(result):
        raise AssertionError("feature sample construction produced duplicates")
    return result


def _normalized_weights(config: VariationalAngleSliceAtlasConfig) -> Array:
    if config.sample_weights is None:
        weights = np.ones(config.feature_sample_count, dtype=float)
    else:
        weights = np.asarray(config.sample_weights, dtype=float)
    return weights / float(np.sum(weights))


def angle_slice_rms_protocol(
    *,
    sample_indices: Sequence[int],
    sample_weights: Sequence[float],
    angular_velocity_scale: float,
) -> PhaseObservationProtocol:
    """Declare the local protocol whose metric equals ``trajectory_feature``.

    ``trajectory_feature`` multiplies sample ``k`` by ``sqrt(w_k)`` and uses
    the Euclidean output metric.  Leaving response blocks unweighted and using
    ``diag(w) kron I_6`` as output precision gives the identical pullback Gram.
    """
    indices = tuple(sample_indices)
    weights = np.asarray(tuple(sample_weights), dtype=float)
    if weights.shape != (len(indices),):
        raise ValueError("sample weights and indices must have equal length")
    if (
        np.any(~np.isfinite(weights))
        or np.any(weights <= 0.0)
    ):
        raise ValueError("sample weights must be finite and strictly positive")
    weights = weights / float(np.sum(weights))
    return PhaseObservationProtocol(
        name="full-phase RMS angle-slice protocol",
        sample_indices=indices,
        sensor_matrix=np.eye(6),
        output_precision=np.kron(np.diag(weights), np.eye(6)),
        source_metric=np.eye(2),
        source_injection=angle_slice_source_injection(),
        angular_velocity_scale=angular_velocity_scale,
    )


def _integration_record(config: IntegrationConfig) -> dict[str, object]:
    return {
        "method": "DOP853 with joint state/tangent integration",
        "rtol": config.rtol,
        "atol": config.atol,
        "max_step": config.max_step,
        "energy_drift_tolerance": config.energy_drift_tolerance,
    }


def _parameter_record(parameters: DoublePendulumParameters) -> dict[str, float]:
    return {
        "m1": parameters.m1,
        "m2": parameters.m2,
        "l1": parameters.l1,
        "l2": parameters.l2,
        "g": parameters.g,
    }


def _environment_record() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
    }


def _discrepancy_norm_record() -> dict[str, str]:
    return {
        "state": (
            "||D^{-1}(z_coarse-z_fine)||_F / "
            "max(1,||D^{-1}z_fine||_F), D=diag(1,1,omega_scale,omega_scale)"
        ),
        "tangent": "||Phi_coarse-Phi_fine||_F / max(1,||Phi_fine||_F)",
        "weighted_response": "||R_coarse-R_fine||_F / max(1,||R_fine||_F)",
        "information_gram": "||G_coarse-G_fine||_F / max(1,||G_fine||_F)",
        "weakest_gain": "|sigma_min_coarse-sigma_min_fine| / sigma_min_fine",
        "strongest_gain": "|sigma_max_coarse-sigma_max_fine| / sigma_max_fine",
        "finite_difference_response": (
            "||R_FD-R_fine||_F / max(1,||R_fine||_F), evaluated only at declared spots"
        ),
        "finite_difference_gram": (
            "||G_FD-G_fine||_F / max(1,||G_fine||_F), evaluated only at declared spots"
        ),
        "finite_difference_weakest_gain": (
            "|sigma_min_FD-sigma_min_fine| / sigma_min_fine, evaluated only at declared spots"
        ),
        "finite_difference_strongest_gain": (
            "|sigma_max_FD-sigma_max_fine| / sigma_max_fine, evaluated only at declared spots"
        ),
    }


def _relative_difference(left: Array, right: Array) -> float:
    difference = float(np.linalg.norm(np.asarray(left) - np.asarray(right)))
    reference = max(1.0, float(np.linalg.norm(np.asarray(right))))
    return difference / reference


def _positive_scalar_relative_difference(coarse: float, fine: float) -> float:
    if not math.isfinite(coarse) or not math.isfinite(fine) or fine <= 0.0:
        raise ValueError("gain refinement requires finite positive fine gain")
    return abs(coarse - fine) / fine


def _gram_gains(gram: Array) -> tuple[float, float]:
    matrix = np.asarray(gram, dtype=float)
    eigenvalues = np.linalg.eigvalsh(matrix)
    scale = max(1.0, float(np.linalg.norm(matrix, ord=2)))
    if float(eigenvalues[0]) < -2.0e-11 * scale:
        raise ValueError("a numerical response Gram has a negative eigenvalue")
    gains = np.sqrt(np.maximum(eigenvalues, 0.0))
    if gains[0] <= 0.0:
        raise ValueError("gain-relative comparison requires positive weakest gain")
    return float(gains[0]), float(gains[1])


def _scaled_state_difference(
    coarse: Array,
    fine: Array,
    angular_velocity_scale: float,
) -> float:
    scale = np.asarray([1.0, 1.0, angular_velocity_scale, angular_velocity_scale])
    difference = (np.asarray(coarse) - np.asarray(fine)) / scale
    reference = np.asarray(fine) / scale
    return float(np.linalg.norm(difference) / max(1.0, np.linalg.norm(reference)))


def _weighted_response(response: Array, weights: Array) -> Array:
    values = np.asarray(response, dtype=float)
    if values.shape[0] != 6 * len(weights):
        raise ValueError("response dimension does not match RMS sample weights")
    return values * np.repeat(np.sqrt(weights), 6)[:, None]


def _rms_feature(
    states: Array,
    sample_indices: Sequence[int],
    weights: Array,
    angular_velocity_scale: float,
) -> Array:
    return trajectory_feature(
        np.asarray(states),
        tuple(sample_indices),
        sample_weights=weights,
        angular_velocity_scale=angular_velocity_scale,
    )


def _default_spot_cells(side: int) -> tuple[tuple[int, int], ...]:
    candidates = ((0, 0), (side // 2, side // 2), (0, side - 1), (side - 1, 0))
    return tuple(dict.fromkeys(candidates))


def _json_grid(values: Array, resolved: Array | None = None) -> list[object]:
    array = np.asarray(values)
    if resolved is None:
        resolved = np.ones(array.shape[:2], dtype=bool)
    rows: list[object] = []
    for row in range(array.shape[0]):
        columns: list[object] = []
        for column in range(array.shape[1]):
            if not bool(resolved[row, column]):
                columns.append(None)
            else:
                value = array[row, column]
                columns.append(
                    float(value) if np.ndim(value) == 0 else np.asarray(value).tolist()
                )
        rows.append(columns)
    return rows


def _quantiles(values: Array) -> dict[str, float] | None:
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if len(finite) == 0:
        return None
    return {
        "q10": float(np.quantile(finite, 0.10)),
        "q50": float(np.quantile(finite, 0.50)),
        "q90": float(np.quantile(finite, 0.90)),
    }


def _configuration_record(
    config: VariationalAngleSliceAtlasConfig,
) -> dict[str, object]:
    return {
        "side": config.side,
        "duration": config.duration,
        "observation_count": config.observation_count,
        "feature_sample_count": config.feature_sample_count,
        "sample_weights": (
            None if config.sample_weights is None else list(config.sample_weights)
        ),
        "state_relative_tolerance": config.state_relative_tolerance,
        "tangent_relative_tolerance": config.tangent_relative_tolerance,
        "response_relative_tolerance": config.response_relative_tolerance,
        "gram_relative_tolerance": config.gram_relative_tolerance,
        "weakest_gain_relative_tolerance": config.weakest_gain_relative_tolerance,
        "strongest_gain_relative_tolerance": config.strongest_gain_relative_tolerance,
        "finite_difference_step": config.finite_difference_step,
        "finite_difference_response_relative_tolerance": (
            config.finite_difference_response_relative_tolerance
        ),
        "finite_difference_gram_relative_tolerance": (
            config.finite_difference_gram_relative_tolerance
        ),
        "finite_difference_weakest_gain_relative_tolerance": (
            config.finite_difference_weakest_gain_relative_tolerance
        ),
        "finite_difference_strongest_gain_relative_tolerance": (
            config.finite_difference_strongest_gain_relative_tolerance
        ),
        "spot_check_cells": [list(cell) for cell in config.spot_check_cells],
    }


def run_variational_angle_slice_atlas(
    config: VariationalAngleSliceAtlasConfig = VariationalAngleSliceAtlasConfig(),
    parameters: DoublePendulumParameters = DoublePendulumParameters(),
    coarse_integration: IntegrationConfig = IntegrationConfig(
        rtol=1.0e-8,
        atol=1.0e-10,
        max_step=0.03,
        energy_drift_tolerance=1.0e-6,
    ),
) -> dict[str, object]:
    """Compute and audit the finite Tier-1 variational angle-slice atlas."""
    if coarse_integration.energy_drift_tolerance is None:
        raise ValueError(
            "the variational atlas requires an enabled sampled energy-drift gate"
        )
    fine_integration = coarse_integration.refined()
    theta_1, theta_2, initial_grid = cell_centred_torus_grid(config.side)
    times = np.linspace(0.0, config.duration, config.observation_count)
    indices = _sample_indices(config)
    weights = _normalized_weights(config)
    velocity_scale = parameters.characteristic_angular_speed
    protocol = angle_slice_rms_protocol(
        sample_indices=indices,
        sample_weights=weights,
        angular_velocity_scale=velocity_scale,
    )

    shape = (config.side, config.side)
    resolved = np.zeros(shape, dtype=bool)
    coarse_weakest = np.full(shape, np.nan)
    coarse_strongest = np.full(shape, np.nan)
    fine_weakest = np.full(shape, np.nan)
    fine_strongest = np.full(shape, np.nan)
    coarse_grams = np.full(shape + (2, 2), np.nan)
    fine_grams = np.full(shape + (2, 2), np.nan)
    state_discrepancy = np.full(shape, np.nan)
    tangent_discrepancy = np.full(shape, np.nan)
    response_discrepancy = np.full(shape, np.nan)
    gram_discrepancy = np.full(shape, np.nan)
    weakest_gain_discrepancy = np.full(shape, np.nan)
    strongest_gain_discrepancy = np.full(shape, np.nan)
    coarse_energy_drift = np.full(shape, np.nan)
    fine_energy_drift = np.full(shape, np.nan)
    failure_reasons: dict[tuple[int, int], list[str]] = {}
    fine_weighted_responses: dict[tuple[int, int], Array] = {}

    for row in range(config.side):
        for column in range(config.side):
            cell = (row, column)
            initial = initial_grid[row, column]
            reasons: list[str] = []
            try:
                coarse = simulate_double_pendulum_variational(
                    initial, times, parameters, coarse_integration
                )
                fine = simulate_double_pendulum_variational(
                    initial, times, parameters, fine_integration
                )
                coarse_analysis = analyze_phase_protocol(coarse, protocol)
                fine_analysis = analyze_phase_protocol(fine, protocol)
                coarse_weighted = _weighted_response(coarse_analysis.response, weights)
                fine_weighted = _weighted_response(fine_analysis.response, weights)

                coarse_weakest[cell] = coarse_analysis.weakest_gain
                coarse_strongest[cell] = coarse_analysis.strongest_gain
                fine_weakest[cell] = fine_analysis.weakest_gain
                fine_strongest[cell] = fine_analysis.strongest_gain
                coarse_grams[cell] = coarse_analysis.information_gram
                fine_grams[cell] = fine_analysis.information_gram
                coarse_energy_drift[cell] = coarse.max_scaled_energy_drift
                fine_energy_drift[cell] = fine.max_scaled_energy_drift
                state_discrepancy[cell] = _scaled_state_difference(
                    coarse.states, fine.states, velocity_scale
                )
                tangent_discrepancy[cell] = _relative_difference(
                    coarse.tangents, fine.tangents
                )
                response_discrepancy[cell] = _relative_difference(
                    coarse_weighted, fine_weighted
                )
                gram_discrepancy[cell] = _relative_difference(
                    coarse_analysis.information_gram,
                    fine_analysis.information_gram,
                )
                weakest_gain_discrepancy[cell] = _positive_scalar_relative_difference(
                    coarse_analysis.weakest_gain, fine_analysis.weakest_gain
                )
                strongest_gain_discrepancy[cell] = _positive_scalar_relative_difference(
                    coarse_analysis.strongest_gain, fine_analysis.strongest_gain
                )
                checks = (
                    ("state_refinement", state_discrepancy[cell], config.state_relative_tolerance),
                    ("tangent_refinement", tangent_discrepancy[cell], config.tangent_relative_tolerance),
                    ("response_refinement", response_discrepancy[cell], config.response_relative_tolerance),
                    ("gram_refinement", gram_discrepancy[cell], config.gram_relative_tolerance),
                    (
                        "weakest_gain_refinement",
                        weakest_gain_discrepancy[cell],
                        config.weakest_gain_relative_tolerance,
                    ),
                    (
                        "strongest_gain_refinement",
                        strongest_gain_discrepancy[cell],
                        config.strongest_gain_relative_tolerance,
                    ),
                )
                reasons.extend(
                    f"{name}={value:.6e}>{threshold:.6e}"
                    for name, value, threshold in checks
                    if value > threshold
                )
                fine_weighted_responses[cell] = fine_weighted
            except Exception as error:
                reasons.append(f"integration_or_analysis_error:{type(error).__name__}:{error}")
            if reasons:
                failure_reasons[cell] = reasons
            else:
                resolved[cell] = True

    requested_spots = (
        config.spot_check_cells
        if config.spot_check_cells
        else _default_spot_cells(config.side)
    )
    spot_checks: list[dict[str, object]] = []
    source_basis = np.eye(2)
    for row, column in requested_spots:
        cell = (row, column)
        record: dict[str, object] = {
            "row": row,
            "column": column,
            "initial_angles": [
                float(initial_grid[row, column, 0]),
                float(initial_grid[row, column, 1]),
            ],
            "centered_difference_step": config.finite_difference_step,
        }
        if cell not in fine_weighted_responses:
            record.update(
                {
                    "passed": False,
                    "status": "unresolved because the variational comparison is unavailable",
                }
            )
            resolved[cell] = False
            failure_reasons.setdefault(cell, []).append("finite_difference_check_unavailable")
            spot_checks.append(record)
            continue
        try:
            columns: list[Array] = []
            for direction in range(2):
                features: list[Array] = []
                for sign in (1.0, -1.0):
                    initial = initial_grid[row, column].copy()
                    initial[:2] += (
                        sign * config.finite_difference_step * source_basis[direction]
                    )
                    trajectory = simulate_double_pendulum(
                        initial, times, parameters, fine_integration
                    )
                    features.append(
                        _rms_feature(
                            trajectory.states,
                            indices,
                            weights,
                            velocity_scale,
                        )
                    )
                columns.append(
                    (features[0] - features[1])
                    / (2.0 * config.finite_difference_step)
                )
            finite_difference_response = np.column_stack(columns)
            variational_response = fine_weighted_responses[cell]
            finite_difference_gram = (
                finite_difference_response.T @ finite_difference_response
            )
            response_error = _relative_difference(
                finite_difference_response, variational_response
            )
            gram_error = _relative_difference(
                finite_difference_gram, fine_grams[cell]
            )
            finite_difference_gains = _gram_gains(finite_difference_gram)
            variational_gains = _gram_gains(fine_grams[cell])
            weakest_gain_error = _positive_scalar_relative_difference(
                finite_difference_gains[0], variational_gains[0]
            )
            strongest_gain_error = _positive_scalar_relative_difference(
                finite_difference_gains[1], variational_gains[1]
            )
            passed = bool(
                response_error
                <= config.finite_difference_response_relative_tolerance
                and gram_error <= config.finite_difference_gram_relative_tolerance
                and weakest_gain_error
                <= config.finite_difference_weakest_gain_relative_tolerance
                and strongest_gain_error
                <= config.finite_difference_strongest_gain_relative_tolerance
            )
            record.update(
                {
                    "passed": passed,
                    "status": (
                        "spot check passed"
                        if passed
                        else "finite-difference disagreement"
                    ),
                    "response_relative_discrepancy": response_error,
                    "gram_relative_discrepancy": gram_error,
                    "weakest_gain_relative_discrepancy": weakest_gain_error,
                    "strongest_gain_relative_discrepancy": strongest_gain_error,
                    "finite_difference_response": finite_difference_response.tolist(),
                    "variational_fine_response": variational_response.tolist(),
                    "finite_difference_gram": finite_difference_gram.tolist(),
                    "variational_fine_gram": fine_grams[cell].tolist(),
                }
            )
            if not passed:
                resolved[cell] = False
                failure_reasons.setdefault(cell, []).append(
                    "finite_difference_spot_check_failed"
                )
        except Exception as error:
            resolved[cell] = False
            failure_reasons.setdefault(cell, []).append(
                f"finite_difference_error:{type(error).__name__}:{error}"
            )
            record.update(
                {
                    "passed": False,
                    "status": f"finite-difference error: {type(error).__name__}: {error}",
                }
            )
        spot_checks.append(record)

    selected_weakest = np.where(resolved, fine_weakest, np.nan)
    selected_strongest = np.where(resolved, fine_strongest, np.nan)
    unresolved_rows = [
        {
            "row": row,
            "column": column,
            "initial_angles": [
                float(initial_grid[row, column, 0]),
                float(initial_grid[row, column, 1]),
            ],
            "reasons": failure_reasons.get((row, column), ["unresolved without reason"]),
        }
        for row in range(config.side)
        for column in range(config.side)
        if not resolved[row, column]
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "claim_tier": 1,
        "evidence_tier": TIER_1_SCOPE,
        "status": "finite Tier-1 variational initial-angle atlas",
        "configuration": _configuration_record(config),
        "parameters": _parameter_record(parameters),
        "environment": _environment_record(),
        "grid": {
            "topology": "cell-centred product torus",
            "row_coordinate": "initial theta1",
            "column_coordinate": "initial theta2",
            "theta1_centres": theta_1.tolist(),
            "theta2_centres": theta_2.tolist(),
            "initial_velocities": [0.0, 0.0],
        },
        "protocol": {
            "source_coordinates": ["initial theta1", "initial theta2"],
            "source_injection": protocol.source_injection.tolist(),
            "source_metric": protocol.source_metric.tolist(),
            "phase_sensor": "identity on (sin theta1, cos theta1, sin theta2, cos theta2, omega1/scale, omega2/scale)",
            "angular_velocity_scale": velocity_scale,
            "observation_times": times.tolist(),
            "feature_sample_indices": list(indices),
            "feature_sample_times": times[list(indices)].tolist(),
            "normalized_sample_weights": weights.tolist(),
            "output_precision_rule": "diag(normalized_sample_weights) kron I_6",
            "rms_feature_equivalence": (
                "The information Gram equals the Euclidean pullback Gram of "
                "trajectory_feature with the same samples, weights, and velocity scale."
            ),
        },
        "integration": {
            "coarse": _integration_record(coarse_integration),
            "fine": _integration_record(fine_integration),
        },
        "acceptance": {
            "state_relative_tolerance": config.state_relative_tolerance,
            "tangent_relative_tolerance": config.tangent_relative_tolerance,
            "response_relative_tolerance": config.response_relative_tolerance,
            "gram_relative_tolerance": config.gram_relative_tolerance,
            "weakest_gain_relative_tolerance": config.weakest_gain_relative_tolerance,
            "strongest_gain_relative_tolerance": config.strongest_gain_relative_tolerance,
            "finite_difference_response_relative_tolerance": config.finite_difference_response_relative_tolerance,
            "finite_difference_gram_relative_tolerance": config.finite_difference_gram_relative_tolerance,
            "finite_difference_weakest_gain_relative_tolerance": (
                config.finite_difference_weakest_gain_relative_tolerance
            ),
            "finite_difference_strongest_gain_relative_tolerance": (
                config.finite_difference_strongest_gain_relative_tolerance
            ),
            "discrepancy_norms": _discrepancy_norm_record(),
            "finite_difference_scope": (
                "centered finite differences are evaluated only at the declared "
                "spot-check cells, not at every resolved grid cell"
            ),
            "decision_rule": (
                "A cell is resolved only when every coarse/fine gate passes and, "
                "if selected, its centered finite-difference spot check passes."
            ),
        },
        "fields": {
            "resolved_mask": resolved.astype(int).tolist(),
            "unresolved_mask": (~resolved).astype(int).tolist(),
            "selected_weakest_local_gain": _json_grid(selected_weakest, resolved),
            "selected_strongest_local_gain": _json_grid(selected_strongest, resolved),
            "coarse_weakest_local_gain": _json_grid(coarse_weakest, np.isfinite(coarse_weakest)),
            "coarse_strongest_local_gain": _json_grid(coarse_strongest, np.isfinite(coarse_strongest)),
            "fine_weakest_local_gain": _json_grid(fine_weakest, np.isfinite(fine_weakest)),
            "fine_strongest_local_gain": _json_grid(fine_strongest, np.isfinite(fine_strongest)),
            "coarse_information_gram": _json_grid(coarse_grams, np.isfinite(coarse_grams).all(axis=(-2, -1))),
            "fine_information_gram": _json_grid(fine_grams, np.isfinite(fine_grams).all(axis=(-2, -1))),
            "state_refinement_relative_discrepancy": _json_grid(state_discrepancy, np.isfinite(state_discrepancy)),
            "tangent_refinement_relative_discrepancy": _json_grid(tangent_discrepancy, np.isfinite(tangent_discrepancy)),
            "response_refinement_relative_discrepancy": _json_grid(response_discrepancy, np.isfinite(response_discrepancy)),
            "gram_refinement_relative_discrepancy": _json_grid(gram_discrepancy, np.isfinite(gram_discrepancy)),
            "weakest_gain_refinement_relative_discrepancy": _json_grid(
                weakest_gain_discrepancy, np.isfinite(weakest_gain_discrepancy)
            ),
            "strongest_gain_refinement_relative_discrepancy": _json_grid(
                strongest_gain_discrepancy, np.isfinite(strongest_gain_discrepancy)
            ),
            "coarse_sampled_scaled_energy_drift": _json_grid(coarse_energy_drift, np.isfinite(coarse_energy_drift)),
            "fine_sampled_scaled_energy_drift": _json_grid(fine_energy_drift, np.isfinite(fine_energy_drift)),
        },
        "centered_finite_difference_spot_checks": spot_checks,
        "unresolved_cells": unresolved_rows,
        "summary": {
            "cell_count": config.side * config.side,
            "resolved_cell_count": int(np.count_nonzero(resolved)),
            "unresolved_cell_count": int(np.count_nonzero(~resolved)),
            "weakest_gain_quantiles_over_resolved_cells": _quantiles(selected_weakest),
            "strongest_gain_quantiles_over_resolved_cells": _quantiles(selected_strongest),
            "all_requested_spot_checks_passed": all(
                bool(row["passed"]) for row in spot_checks
            ),
        },
        "proof_boundary": PROOF_BOUNDARY,
    }


def _strict_keys(value: object, expected: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError(f"{label} has an unknown or incomplete schema")
    return value


def _strict_equal(left: object, right: object) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            _strict_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            _strict_equal(a, b) for a, b in zip(left, right)
        )
    return bool(left == right)


def _finite_number(value: object, label: str, *, nonnegative: bool = False) -> float:
    if isinstance(value, bool) or type(value) not in (int, float):
        raise ValueError(f"{label} must be a JSON number")
    result = float(value)
    if not math.isfinite(result) or (nonnegative and result < 0.0):
        raise ValueError(f"{label} has an invalid numerical value")
    return result


def _mask_grid(value: object, side: int, label: str) -> Array:
    if not isinstance(value, list) or len(value) != side:
        raise ValueError(f"{label} has the wrong row count")
    result = np.empty((side, side), dtype=bool)
    for row, values in enumerate(value):
        if not isinstance(values, list) or len(values) != side:
            raise ValueError(f"{label} has the wrong column count")
        for column, entry in enumerate(values):
            if type(entry) is not int or entry not in (0, 1):
                raise ValueError(f"{label} entries must be JSON integers 0 or 1")
            result[row, column] = bool(entry)
    return result


def _scalar_grid(value: object, side: int, label: str) -> Array:
    if not isinstance(value, list) or len(value) != side:
        raise ValueError(f"{label} has the wrong row count")
    result = np.full((side, side), np.nan)
    for row, values in enumerate(value):
        if not isinstance(values, list) or len(values) != side:
            raise ValueError(f"{label} has the wrong column count")
        for column, entry in enumerate(values):
            if entry is not None:
                result[row, column] = _finite_number(
                    entry, f"{label}[{row},{column}]"
                )
    return result


def _numeric_matrix(
    value: object, shape: tuple[int, int], label: str
) -> Array:
    rows, columns = shape
    if not isinstance(value, list) or len(value) != rows:
        raise ValueError(f"{label} must have shape {shape}")
    result = np.empty(shape, dtype=float)
    for row, values in enumerate(value):
        if not isinstance(values, list) or len(values) != columns:
            raise ValueError(f"{label} must have shape {shape}")
        for column, entry in enumerate(values):
            result[row, column] = _finite_number(
                entry, f"{label}[{row},{column}]"
            )
    return result


def _matrix_grid(value: object, side: int, label: str) -> Array:
    if not isinstance(value, list) or len(value) != side:
        raise ValueError(f"{label} has the wrong row count")
    result = np.full((side, side, 2, 2), np.nan)
    for row, values in enumerate(value):
        if not isinstance(values, list) or len(values) != side:
            raise ValueError(f"{label} has the wrong column count")
        for column, entry in enumerate(values):
            if entry is None:
                continue
            matrix = _numeric_matrix(
                entry, (2, 2), f"{label}[{row},{column}]"
            )
            scale = max(1.0, float(np.linalg.norm(matrix, ord=np.inf)))
            if not np.allclose(matrix, matrix.T, rtol=0.0, atol=2.0e-13 * scale):
                raise ValueError(f"{label}[{row},{column}] is not symmetric")
            result[row, column] = 0.5 * (matrix + matrix.T)
    return result


def _matrix2(value: object, label: str) -> Array:
    return _numeric_matrix(value, (2, 2), label)


def _verify_integration_record(value: object, label: str) -> dict[str, object]:
    record = _strict_keys(
        value,
        {"method", "rtol", "atol", "max_step", "energy_drift_tolerance"},
        label,
    )
    if record["method"] != "DOP853 with joint state/tangent integration":
        raise ValueError(f"{label} uses an unknown integration method")
    for name in ("rtol", "atol", "max_step"):
        if _finite_number(record[name], f"{label}.{name}") <= 0.0:
            raise ValueError(f"{label}.{name} must be positive")
    tolerance = record["energy_drift_tolerance"]
    if tolerance is None:
        raise ValueError(f"{label}.energy_drift_tolerance may not be disabled")
    if _finite_number(tolerance, f"{label}.energy_drift_tolerance") <= 0.0:
        raise ValueError(f"{label}.energy_drift_tolerance must be positive")
    return record


def _gain_matches_gram(weakest: float, strongest: float, gram: Array) -> bool:
    eigenvalues = np.linalg.eigvalsh(gram)
    scale = max(1.0, float(np.linalg.norm(gram, ord=2)))
    if float(eigenvalues[0]) < -2.0e-11 * scale:
        return False
    expected = np.sqrt(np.maximum(eigenvalues, 0.0))
    return bool(
        math.isclose(weakest, float(expected[0]), rel_tol=3.0e-9, abs_tol=3.0e-10)
        and math.isclose(
            strongest, float(expected[1]), rel_tol=3.0e-9, abs_tol=3.0e-10
        )
    )


def _verification_payload(side: int) -> dict[str, object]:
    return {
        "passed": True,
        "schema_version": "oig-double-pendulum-variational-angle-slice-atlas-verification-v1",
        "side": side,
        "internal_report_consistency_verified": True,
        "ode_or_variational_system_replayed": False,
        "physical_flow_enclosure_verified": False,
        "exact_oig_certificate_verified": False,
        "method": (
            "strict reconstruction of the serialized configuration, dimensions, "
            "gates, masks, spot decisions, and summaries without ODE replay"
        ),
    }


def verify_variational_angle_slice_atlas_report(
    report: dict[str, object],
) -> dict[str, object]:
    """Strictly verify internal Tier-1 report logic without replaying the ODE."""
    try:
        top = _strict_keys(
            report,
            {
                "schema_version",
                "claim_tier",
                "evidence_tier",
                "status",
                "configuration",
                "parameters",
                "environment",
                "grid",
                "protocol",
                "integration",
                "acceptance",
                "fields",
                "centered_finite_difference_spot_checks",
                "unresolved_cells",
                "summary",
                "proof_boundary",
            },
            "variational atlas report",
        )
        if top["schema_version"] != SCHEMA_VERSION:
            raise ValueError("unknown variational atlas schema version")
        if (
            type(top["claim_tier"]) is not int
            or top["claim_tier"] != 1
            or top["evidence_tier"] != TIER_1_SCOPE
            or top["status"] != "finite Tier-1 variational initial-angle atlas"
        ):
            raise ValueError("Tier-1 status declaration is inconsistent")
        if top["proof_boundary"] != PROOF_BOUNDARY:
            raise ValueError("negative proof boundary is missing or altered")

        raw_config = _strict_keys(
            top["configuration"],
            set(_configuration_record(VariationalAngleSliceAtlasConfig())),
            "configuration",
        )
        config_values = dict(raw_config)
        weights = config_values["sample_weights"]
        if weights is not None:
            if not isinstance(weights, (list, tuple)):
                raise ValueError("configuration.sample_weights must be a sequence or null")
            config_values["sample_weights"] = tuple(weights)
        raw_spots = config_values["spot_check_cells"]
        if not isinstance(raw_spots, (list, tuple)):
            raise ValueError("configuration.spot_check_cells must be a sequence")
        config_values["spot_check_cells"] = tuple(
            tuple(cell) if isinstance(cell, (list, tuple)) else cell
            for cell in raw_spots
        )
        config = VariationalAngleSliceAtlasConfig(**config_values)  # type: ignore[arg-type]
        if not _strict_equal(dict(raw_config), _configuration_record(config)):
            raise ValueError("configuration does not reproduce canonically")
        side = config.side

        parameter_record = _strict_keys(
            top["parameters"], {"m1", "m2", "l1", "l2", "g"}, "parameters"
        )
        for name in ("m1", "m2", "l1", "l2", "g"):
            if _finite_number(parameter_record[name], f"parameters.{name}") <= 0.0:
                raise ValueError(f"parameters.{name} must be positive")
        parameters = DoublePendulumParameters(**parameter_record)  # type: ignore[arg-type]
        if not _strict_equal(parameter_record, _parameter_record(parameters)):
            raise ValueError("physical parameters do not reproduce canonically")
        environment = _strict_keys(
            top["environment"], {"python", "numpy", "scipy", "platform"}, "environment"
        )
        if any(not isinstance(value, str) or not value for value in environment.values()):
            raise ValueError("environment values must be nonempty provenance strings")

        expected_theta_1, expected_theta_2, _ = cell_centred_torus_grid(side)
        grid = _strict_keys(
            top["grid"],
            {
                "topology",
                "row_coordinate",
                "column_coordinate",
                "theta1_centres",
                "theta2_centres",
                "initial_velocities",
            },
            "grid",
        )
        if (
            grid["topology"] != "cell-centred product torus"
            or grid["row_coordinate"] != "initial theta1"
            or grid["column_coordinate"] != "initial theta2"
            or not _strict_equal(grid["initial_velocities"], [0.0, 0.0])
            or not _strict_equal(grid["theta1_centres"], expected_theta_1.tolist())
            or not _strict_equal(grid["theta2_centres"], expected_theta_2.tolist())
        ):
            raise ValueError("grid declaration does not reproduce")

        protocol = _strict_keys(
            top["protocol"],
            {
                "source_coordinates",
                "source_injection",
                "source_metric",
                "phase_sensor",
                "angular_velocity_scale",
                "observation_times",
                "feature_sample_indices",
                "feature_sample_times",
                "normalized_sample_weights",
                "output_precision_rule",
                "rms_feature_equivalence",
            },
            "protocol",
        )
        expected_times = np.linspace(0.0, config.duration, config.observation_count)
        expected_indices = _sample_indices(config)
        expected_weights = _normalized_weights(config)
        injection = _numeric_matrix(
            protocol["source_injection"], (4, 2), "protocol.source_injection"
        )
        metric = _numeric_matrix(
            protocol["source_metric"], (2, 2), "protocol.source_metric"
        )
        if (
            not _strict_equal(
                protocol["source_coordinates"], ["initial theta1", "initial theta2"]
            )
            or not np.array_equal(injection, angle_slice_source_injection())
            or not np.array_equal(metric, np.eye(2))
            or protocol["phase_sensor"]
            != "identity on (sin theta1, cos theta1, sin theta2, cos theta2, omega1/scale, omega2/scale)"
            or not _strict_equal(protocol["observation_times"], expected_times.tolist())
            or not _strict_equal(
                protocol["feature_sample_indices"], list(expected_indices)
            )
            or not _strict_equal(
                protocol["feature_sample_times"],
                expected_times[list(expected_indices)].tolist(),
            )
            or not _strict_equal(
                protocol["normalized_sample_weights"], expected_weights.tolist()
            )
            or protocol["output_precision_rule"]
            != "diag(normalized_sample_weights) kron I_6"
            or protocol["rms_feature_equivalence"]
            != "The information Gram equals the Euclidean pullback Gram of trajectory_feature with the same samples, weights, and velocity scale."
        ):
            raise ValueError("RMS angle-slice protocol declaration does not reproduce")
        if _finite_number(
            protocol["angular_velocity_scale"], "protocol.angular_velocity_scale"
        ) != parameters.characteristic_angular_speed:
            raise ValueError("protocol angular-velocity scale differs from parameters")
        output_dimension = 6 * len(expected_indices)
        if output_dimension != 6 * config.feature_sample_count:
            raise AssertionError("protocol output dimension changed unexpectedly")

        integration = _strict_keys(top["integration"], {"coarse", "fine"}, "integration")
        coarse_integration = _verify_integration_record(
            integration["coarse"], "integration.coarse"
        )
        fine_integration = _verify_integration_record(
            integration["fine"], "integration.fine"
        )
        for name, factor in (("rtol", 0.1), ("atol", 0.1), ("max_step", 0.5)):
            if not math.isclose(
                float(fine_integration[name]),
                factor * float(coarse_integration[name]),
                rel_tol=2.0e-15,
                abs_tol=0.0,
            ):
                raise ValueError("fine integration is not the declared strict refinement")
        if fine_integration["energy_drift_tolerance"] != coarse_integration[
            "energy_drift_tolerance"
        ]:
            raise ValueError("coarse and fine energy gates differ unexpectedly")

        acceptance = _strict_keys(
            top["acceptance"],
            {
                "state_relative_tolerance",
                "tangent_relative_tolerance",
                "response_relative_tolerance",
                "gram_relative_tolerance",
                "weakest_gain_relative_tolerance",
                "strongest_gain_relative_tolerance",
                "finite_difference_response_relative_tolerance",
                "finite_difference_gram_relative_tolerance",
                "finite_difference_weakest_gain_relative_tolerance",
                "finite_difference_strongest_gain_relative_tolerance",
                "discrepancy_norms",
                "finite_difference_scope",
                "decision_rule",
            },
            "acceptance",
        )
        expected_acceptance = {
            "state_relative_tolerance": config.state_relative_tolerance,
            "tangent_relative_tolerance": config.tangent_relative_tolerance,
            "response_relative_tolerance": config.response_relative_tolerance,
            "gram_relative_tolerance": config.gram_relative_tolerance,
            "weakest_gain_relative_tolerance": config.weakest_gain_relative_tolerance,
            "strongest_gain_relative_tolerance": config.strongest_gain_relative_tolerance,
            "finite_difference_response_relative_tolerance": config.finite_difference_response_relative_tolerance,
            "finite_difference_gram_relative_tolerance": config.finite_difference_gram_relative_tolerance,
            "finite_difference_weakest_gain_relative_tolerance": (
                config.finite_difference_weakest_gain_relative_tolerance
            ),
            "finite_difference_strongest_gain_relative_tolerance": (
                config.finite_difference_strongest_gain_relative_tolerance
            ),
            "discrepancy_norms": _discrepancy_norm_record(),
            "finite_difference_scope": (
                "centered finite differences are evaluated only at the declared "
                "spot-check cells, not at every resolved grid cell"
            ),
            "decision_rule": (
                "A cell is resolved only when every coarse/fine gate passes and, "
                "if selected, its centered finite-difference spot check passes."
            ),
        }
        if not _strict_equal(acceptance, expected_acceptance):
            raise ValueError("acceptance declaration differs from configuration")

        fields = _strict_keys(
            top["fields"],
            {
                "resolved_mask",
                "unresolved_mask",
                "selected_weakest_local_gain",
                "selected_strongest_local_gain",
                "coarse_weakest_local_gain",
                "coarse_strongest_local_gain",
                "fine_weakest_local_gain",
                "fine_strongest_local_gain",
                "coarse_information_gram",
                "fine_information_gram",
                "state_refinement_relative_discrepancy",
                "tangent_refinement_relative_discrepancy",
                "response_refinement_relative_discrepancy",
                "gram_refinement_relative_discrepancy",
                "weakest_gain_refinement_relative_discrepancy",
                "strongest_gain_refinement_relative_discrepancy",
                "coarse_sampled_scaled_energy_drift",
                "fine_sampled_scaled_energy_drift",
            },
            "fields",
        )
        resolved = _mask_grid(fields["resolved_mask"], side, "resolved_mask")
        unresolved = _mask_grid(fields["unresolved_mask"], side, "unresolved_mask")
        if not np.array_equal(unresolved, ~resolved):
            raise ValueError("resolved and unresolved masks are not complements")

        scalar_names = (
            "selected_weakest_local_gain",
            "selected_strongest_local_gain",
            "coarse_weakest_local_gain",
            "coarse_strongest_local_gain",
            "fine_weakest_local_gain",
            "fine_strongest_local_gain",
            "state_refinement_relative_discrepancy",
            "tangent_refinement_relative_discrepancy",
            "response_refinement_relative_discrepancy",
            "gram_refinement_relative_discrepancy",
            "weakest_gain_refinement_relative_discrepancy",
            "strongest_gain_refinement_relative_discrepancy",
            "coarse_sampled_scaled_energy_drift",
            "fine_sampled_scaled_energy_drift",
        )
        scalars = {
            name: _scalar_grid(fields[name], side, name) for name in scalar_names
        }
        coarse_grams = _matrix_grid(
            fields["coarse_information_gram"], side, "coarse_information_gram"
        )
        fine_grams = _matrix_grid(
            fields["fine_information_gram"], side, "fine_information_gram"
        )

        base_pass = np.zeros((side, side), dtype=bool)
        threshold_reasons: dict[tuple[int, int], list[str]] = {}
        for row in range(side):
            for column in range(side):
                cell = (row, column)
                values = {name: scalars[name][cell] for name in scalar_names}
                data_ready = bool(
                    all(
                        math.isfinite(values[name])
                        for name in (
                            "coarse_weakest_local_gain",
                            "coarse_strongest_local_gain",
                            "fine_weakest_local_gain",
                            "fine_strongest_local_gain",
                            "state_refinement_relative_discrepancy",
                            "tangent_refinement_relative_discrepancy",
                            "response_refinement_relative_discrepancy",
                            "gram_refinement_relative_discrepancy",
                            "weakest_gain_refinement_relative_discrepancy",
                            "strongest_gain_refinement_relative_discrepancy",
                            "coarse_sampled_scaled_energy_drift",
                            "fine_sampled_scaled_energy_drift",
                        )
                    )
                    and np.all(np.isfinite(coarse_grams[cell]))
                    and np.all(np.isfinite(fine_grams[cell]))
                )
                if data_ready:
                    for name in (
                        "coarse_weakest_local_gain",
                        "coarse_strongest_local_gain",
                        "fine_weakest_local_gain",
                        "fine_strongest_local_gain",
                        "state_refinement_relative_discrepancy",
                        "tangent_refinement_relative_discrepancy",
                        "response_refinement_relative_discrepancy",
                        "gram_refinement_relative_discrepancy",
                        "weakest_gain_refinement_relative_discrepancy",
                        "strongest_gain_refinement_relative_discrepancy",
                        "coarse_sampled_scaled_energy_drift",
                        "fine_sampled_scaled_energy_drift",
                    ):
                        if values[name] < 0.0:
                            raise ValueError(f"{name}[{row},{column}] is negative")
                    if (
                        values["coarse_strongest_local_gain"]
                        < values["coarse_weakest_local_gain"]
                        or values["fine_strongest_local_gain"]
                        < values["fine_weakest_local_gain"]
                        or not _gain_matches_gram(
                            values["coarse_weakest_local_gain"],
                            values["coarse_strongest_local_gain"],
                            coarse_grams[cell],
                        )
                        or not _gain_matches_gram(
                            values["fine_weakest_local_gain"],
                            values["fine_strongest_local_gain"],
                            fine_grams[cell],
                        )
                    ):
                        raise ValueError(f"gain/Gram inconsistency at cell {cell}")
                    expected_weak_gain_error = _positive_scalar_relative_difference(
                        values["coarse_weakest_local_gain"],
                        values["fine_weakest_local_gain"],
                    )
                    expected_strong_gain_error = _positive_scalar_relative_difference(
                        values["coarse_strongest_local_gain"],
                        values["fine_strongest_local_gain"],
                    )
                    if (
                        values["gram_refinement_relative_discrepancy"]
                        != _relative_difference(coarse_grams[cell], fine_grams[cell])
                        or
                        values["weakest_gain_refinement_relative_discrepancy"]
                        != expected_weak_gain_error
                        or values["strongest_gain_refinement_relative_discrepancy"]
                        != expected_strong_gain_error
                    ):
                        raise ValueError(
                            f"gain refinement discrepancy does not reproduce at {cell}"
                        )
                    comparisons = (
                        (
                            "state_refinement",
                            values["state_refinement_relative_discrepancy"],
                            config.state_relative_tolerance,
                        ),
                        (
                            "tangent_refinement",
                            values["tangent_refinement_relative_discrepancy"],
                            config.tangent_relative_tolerance,
                        ),
                        (
                            "response_refinement",
                            values["response_refinement_relative_discrepancy"],
                            config.response_relative_tolerance,
                        ),
                        (
                            "gram_refinement",
                            values["gram_refinement_relative_discrepancy"],
                            config.gram_relative_tolerance,
                        ),
                        (
                            "weakest_gain_refinement",
                            values[
                                "weakest_gain_refinement_relative_discrepancy"
                            ],
                            config.weakest_gain_relative_tolerance,
                        ),
                        (
                            "strongest_gain_refinement",
                            values[
                                "strongest_gain_refinement_relative_discrepancy"
                            ],
                            config.strongest_gain_relative_tolerance,
                        ),
                    )
                    reasons = [
                        f"{name}={value:.6e}>{threshold:.6e}"
                        for name, value, threshold in comparisons
                        if value > threshold
                    ]
                    coarse_energy_gate = coarse_integration["energy_drift_tolerance"]
                    fine_energy_gate = fine_integration["energy_drift_tolerance"]
                    energy_pass = bool(
                        (
                            coarse_energy_gate is None
                            or values["coarse_sampled_scaled_energy_drift"]
                            <= float(coarse_energy_gate)
                        )
                        and (
                            fine_energy_gate is None
                            or values["fine_sampled_scaled_energy_drift"]
                            <= float(fine_energy_gate)
                        )
                    )
                    base_pass[cell] = not reasons and energy_pass
                    threshold_reasons[cell] = reasons
                selected_weak = values["selected_weakest_local_gain"]
                selected_strong = values["selected_strongest_local_gain"]
                if resolved[cell]:
                    if (
                        not math.isfinite(selected_weak)
                        or not math.isfinite(selected_strong)
                        or selected_weak != values["fine_weakest_local_gain"]
                        or selected_strong != values["fine_strongest_local_gain"]
                    ):
                        raise ValueError(f"resolved selected gains do not equal fine gains at {cell}")
                elif math.isfinite(selected_weak) or math.isfinite(selected_strong):
                    raise ValueError(f"unresolved selected gains are not null at {cell}")

        raw_spot_checks = top["centered_finite_difference_spot_checks"]
        if not isinstance(raw_spot_checks, list):
            raise ValueError("spot checks must be a list")
        expected_spots = (
            config.spot_check_cells
            if config.spot_check_cells
            else _default_spot_cells(side)
        )
        if len(raw_spot_checks) != len(expected_spots):
            raise ValueError("spot-check count differs from the declared schedule")
        spot_pass: dict[tuple[int, int], bool] = {}
        spot_failure_reason: dict[tuple[int, int], str] = {}
        for expected_cell, raw in zip(expected_spots, raw_spot_checks):
            if not isinstance(raw, dict):
                raise ValueError("a spot-check record is malformed")
            row, column = expected_cell
            if (
                type(raw.get("row")) is not int
                or type(raw.get("column")) is not int
                or raw.get("row") != row
                or raw.get("column") != column
                or not _strict_equal(
                    raw.get("initial_angles"),
                    [float(expected_theta_1[row]), float(expected_theta_2[column])],
                )
                or raw.get("centered_difference_step") != config.finite_difference_step
                or type(raw.get("passed")) is not bool
            ):
                raise ValueError("spot-check declaration does not reproduce")
            full_keys = {
                "row",
                "column",
                "initial_angles",
                "centered_difference_step",
                "passed",
                "status",
                "response_relative_discrepancy",
                "gram_relative_discrepancy",
                "weakest_gain_relative_discrepancy",
                "strongest_gain_relative_discrepancy",
                "finite_difference_response",
                "variational_fine_response",
                "finite_difference_gram",
                "variational_fine_gram",
            }
            if set(raw) == full_keys:
                response_error = _finite_number(
                    raw["response_relative_discrepancy"],
                    "spot response discrepancy",
                    nonnegative=True,
                )
                gram_error = _finite_number(
                    raw["gram_relative_discrepancy"],
                    "spot Gram discrepancy",
                    nonnegative=True,
                )
                weakest_gain_error = _finite_number(
                    raw["weakest_gain_relative_discrepancy"],
                    "spot weakest-gain discrepancy",
                    nonnegative=True,
                )
                strongest_gain_error = _finite_number(
                    raw["strongest_gain_relative_discrepancy"],
                    "spot strongest-gain discrepancy",
                    nonnegative=True,
                )
                finite_difference_response = _numeric_matrix(
                    raw["finite_difference_response"],
                    (output_dimension, 2),
                    "finite-difference response",
                )
                variational_response = _numeric_matrix(
                    raw["variational_fine_response"],
                    (output_dimension, 2),
                    "spot variational response",
                )
                finite_difference_gram = _matrix2(
                    raw["finite_difference_gram"], "finite-difference Gram"
                )
                variational_gram = _matrix2(
                    raw["variational_fine_gram"], "spot variational Gram"
                )
                if not np.array_equal(variational_gram, fine_grams[expected_cell]):
                    raise ValueError("spot-check variational Gram differs from its grid field")
                if response_error != _relative_difference(
                    finite_difference_response, variational_response
                ):
                    raise ValueError("spot response discrepancy does not reproduce")
                if not np.allclose(
                    finite_difference_response.T @ finite_difference_response,
                    finite_difference_gram,
                    rtol=3.0e-13,
                    atol=3.0e-13
                    * max(1.0, float(np.linalg.norm(finite_difference_gram))),
                ):
                    raise ValueError("finite-difference response and Gram disagree")
                if not np.allclose(
                    variational_response.T @ variational_response,
                    variational_gram,
                    rtol=3.0e-13,
                    atol=3.0e-13 * max(1.0, float(np.linalg.norm(variational_gram))),
                ):
                    raise ValueError("variational response and Gram disagree")
                if not np.allclose(
                    finite_difference_gram,
                    finite_difference_gram.T,
                    rtol=0.0,
                    atol=2.0e-12 * max(1.0, np.linalg.norm(finite_difference_gram, ord=np.inf)),
                ):
                    raise ValueError("finite-difference Gram is not symmetric")
                finite_scale = max(
                    1.0, float(np.linalg.norm(finite_difference_gram, ord=2))
                )
                if float(np.linalg.eigvalsh(finite_difference_gram)[0]) < (
                    -2.0e-11 * finite_scale
                ):
                    raise ValueError("finite-difference Gram is not positive semidefinite")
                if gram_error != _relative_difference(
                    finite_difference_gram, variational_gram
                ):
                    raise ValueError("spot Gram discrepancy does not reproduce")
                finite_difference_gains = _gram_gains(finite_difference_gram)
                variational_gains = _gram_gains(variational_gram)
                if weakest_gain_error != _positive_scalar_relative_difference(
                    finite_difference_gains[0], variational_gains[0]
                ):
                    raise ValueError("spot weakest-gain discrepancy does not reproduce")
                if strongest_gain_error != _positive_scalar_relative_difference(
                    finite_difference_gains[1], variational_gains[1]
                ):
                    raise ValueError("spot strongest-gain discrepancy does not reproduce")
                expected_pass = bool(
                    response_error
                    <= config.finite_difference_response_relative_tolerance
                    and gram_error <= config.finite_difference_gram_relative_tolerance
                    and weakest_gain_error
                    <= config.finite_difference_weakest_gain_relative_tolerance
                    and strongest_gain_error
                    <= config.finite_difference_strongest_gain_relative_tolerance
                )
                expected_status = (
                    "spot check passed"
                    if expected_pass
                    else "finite-difference disagreement"
                )
                if raw["passed"] is not expected_pass or raw["status"] != expected_status:
                    raise ValueError("spot-check pass flag does not follow its tolerances")
                if not expected_pass:
                    spot_failure_reason[expected_cell] = (
                        "finite_difference_spot_check_failed"
                    )
            else:
                minimal = {
                    "row",
                    "column",
                    "initial_angles",
                    "centered_difference_step",
                    "passed",
                    "status",
                }
                if set(raw) != minimal or raw["passed"] is not False:
                    raise ValueError("spot-check error record has an unknown schema")
                if not isinstance(raw["status"], str) or not (
                    raw["status"].startswith("unresolved because")
                    or raw["status"].startswith("finite-difference error:")
                ):
                    raise ValueError("spot-check error status is inconsistent")
                if raw["status"] == (
                    "unresolved because the variational comparison is unavailable"
                ):
                    spot_failure_reason[expected_cell] = (
                        "finite_difference_check_unavailable"
                    )
                elif raw["status"].startswith("finite-difference error: "):
                    detail = raw["status"].removeprefix("finite-difference error: ")
                    error_type, separator, message = detail.partition(": ")
                    if not separator or not error_type or not message:
                        raise ValueError("spot-check error detail is malformed")
                    spot_failure_reason[expected_cell] = (
                        f"finite_difference_error:{error_type}:{message}"
                    )
                else:
                    raise ValueError("unknown minimal spot-check status")
            spot_pass[expected_cell] = bool(raw["passed"])

        expected_resolved = base_pass.copy()
        for cell, passed in spot_pass.items():
            expected_resolved[cell] &= passed
        if not np.array_equal(resolved, expected_resolved):
            raise ValueError("resolved mask does not reproduce from the serialized gates")

        raw_unresolved = top["unresolved_cells"]
        if not isinstance(raw_unresolved, list):
            raise ValueError("unresolved_cells must be a list")
        expected_unresolved = list(zip(*np.nonzero(~resolved)))
        if len(raw_unresolved) != len(expected_unresolved):
            raise ValueError("unresolved-cell list and mask counts differ")
        for raw, raw_cell in zip(raw_unresolved, expected_unresolved):
            cell = (int(raw_cell[0]), int(raw_cell[1]))
            row, column = cell
            record = _strict_keys(
                raw, {"row", "column", "initial_angles", "reasons"}, "unresolved cell"
            )
            if (
                record["row"] != row
                or record["column"] != column
                or record["initial_angles"]
                != [float(expected_theta_1[row]), float(expected_theta_2[column])]
                or not isinstance(record["reasons"], list)
                or not record["reasons"]
                or any(not isinstance(reason, str) or not reason for reason in record["reasons"])
            ):
                raise ValueError("unresolved-cell record is inconsistent")
            reasons = list(record["reasons"])
            if np.all(np.isfinite(fine_grams[cell])):
                expected_reasons = list(threshold_reasons.get(cell, []))
                if cell in spot_pass and not spot_pass[cell]:
                    expected_reasons.append(spot_failure_reason[cell])
                if reasons != expected_reasons:
                    raise ValueError("unresolved-cell reasons do not reproduce")
            elif not any(
                reason.startswith("integration_or_analysis_error:")
                for reason in reasons
            ):
                raise ValueError("missing integration/analysis failure reason")

        selected_weakest = scalars["selected_weakest_local_gain"]
        selected_strongest = scalars["selected_strongest_local_gain"]
        expected_summary = {
            "cell_count": side * side,
            "resolved_cell_count": int(np.count_nonzero(resolved)),
            "unresolved_cell_count": int(np.count_nonzero(~resolved)),
            "weakest_gain_quantiles_over_resolved_cells": _quantiles(selected_weakest),
            "strongest_gain_quantiles_over_resolved_cells": _quantiles(selected_strongest),
            "all_requested_spot_checks_passed": all(spot_pass.values()),
        }
        summary = _strict_keys(top["summary"], set(expected_summary), "summary")
        if not _strict_equal(summary, expected_summary):
            raise ValueError("summary or gain quantiles do not reproduce")
        return _verification_payload(side)
    except Exception as error:
        return {
            "passed": False,
            "ode_or_variational_system_replayed": False,
            "physical_flow_enclosure_verified": False,
            "exact_oig_certificate_verified": False,
            "error": str(error),
        }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--side", type=int, default=7)
    parser.add_argument("--duration", type=float, default=2.0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    if arguments.verify is not None:
        if arguments.output is not None:
            raise ValueError("--output and --verify cannot be combined")
        report = json.loads(arguments.verify.read_text(encoding="utf-8"))
        verification = verify_variational_angle_slice_atlas_report(report)
        print(json.dumps(verification, indent=2, sort_keys=True))
        return 0 if verification.get("passed") is True else 1
    report = run_variational_angle_slice_atlas(
        VariationalAngleSliceAtlasConfig(
            side=arguments.side,
            duration=arguments.duration,
        )
    )
    verification = verify_variational_angle_slice_atlas_report(report)
    if verification.get("passed") is not True:
        raise AssertionError(f"generated variational atlas fails verification: {verification}")
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if arguments.output is None:
        print(payload, end="")
    else:
        arguments.output.write_text(payload, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PROOF_BOUNDARY",
    "SCHEMA_VERSION",
    "VariationalAngleSliceAtlasConfig",
    "angle_slice_rms_protocol",
    "main",
    "run_variational_angle_slice_atlas",
    "verify_variational_angle_slice_atlas_report",
]
