#!/usr/bin/env python3
"""Tier-1 persistence laboratory for the Double-Pendulum Operational Atlas.

The laboratory compares finite-time grid-edge log-stretch fields after
periodic bilinear transport to one declared common evaluation grid.  It
separates four questions:

* resolution and grid-origin sensitivity;
* threshold-filtration stability;
* cadence sensitivity of the finite observation feature; and
* continuation as the declared observation horizon changes.

Horizon continuation is a scientific parameter study, not a numerical
pass/fail gate.  Every result remains Tier 1: adaptive ODE integration and
field resampling do not outwardly enclose the exact flow or its derivative.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import platform
from typing import Iterable, Sequence

import numpy as np
import scipy
from scipy.stats import rankdata

from double_pendulum_dynamics import (
    DoublePendulumParameters,
    IntegrationConfig,
    simulate_double_pendulum,
    total_energy,
)
from oig_double_pendulum_atlas import (
    build_operational_atlas,
    toroidal_connected_components,
)


Array = np.ndarray
SCHEMA_VERSION = "oig-double-pendulum-tier1-persistence-v1"
TIER1_BOUNDARY = (
    "This report compares reproducible finite numerical fields. Periodic "
    "resampling, energy diagnostics, and solver gates are not outward "
    "enclosures of the exact nonlinear flow. Grid and cadence studies assess "
    "numerical sensitivity; horizon continuation describes different declared "
    "protocols and is never a numerical pass/fail test. Common-grid "
    "filtrations concern only the scalar log-stretch field; sampled-turn masks "
    "remain categorical source-grid diagnostics and are never interpolated."
)


def _finite(value: float, name: str) -> float:
    if isinstance(value, (bool, np.bool_)) or not isinstance(
        value, (int, float, np.integer, np.floating)
    ):
        raise ValueError(f"{name} must be a JSON-style real number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(value: float, name: str) -> float:
    result = _finite(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def _shift(value: Sequence[float], name: str) -> tuple[float, float]:
    if len(value) != 2:
        raise ValueError(f"{name} must have two coordinates")
    return (_finite(value[0], f"{name}[0]"), _finite(value[1], f"{name}[1]"))


def _duration_count(duration: float, interval: float, name: str) -> int:
    ratio = duration / interval
    rounded = round(ratio)
    if abs(ratio - rounded) > 1.0e-10 * max(1.0, abs(ratio)):
        raise ValueError(f"{name} must divide the duration to numerical tolerance")
    return int(rounded) + 1


@dataclass(frozen=True)
class PersistenceLabConfig:
    """Declaration of the canonical family of Tier-1 comparisons."""

    baseline_side: int = 7
    resolution_sides: tuple[int, ...] = (5, 7, 9)
    shift_variants: tuple[tuple[float, float], ...] = (
        (0.0, 0.0),
        (0.5, 0.0),
        (0.0, 0.5),
        (0.5, 0.5),
    )
    common_side: int = 21
    common_shift: tuple[float, float] = (0.25, 0.25)
    baseline_duration: float = 2.0
    horizon_variants: tuple[float, ...] = (1.0, 2.0, 3.0)
    observation_interval: float = 0.05
    feature_interval: float = 0.25
    cadence_feature_counts: tuple[int, ...] = (5, 9, 17, 41)
    thresholds: tuple[float, ...] = (0.0, 0.5, 1.0, 1.5, 2.0)
    reference_threshold: float = 0.5
    energy_bin_count: int = 4

    def __post_init__(self) -> None:
        if type(self.baseline_side) is not int or self.baseline_side < 3:
            raise ValueError("baseline_side must be an integer at least three")
        if type(self.common_side) is not int or self.common_side < 3:
            raise ValueError("common_side must be an integer at least three")
        sides = tuple(self.resolution_sides)
        if (
            not sides
            or any(type(side) is not int or side < 3 for side in sides)
            or len(set(sides)) != len(sides)
            or self.baseline_side not in sides
        ):
            raise ValueError("resolution_sides must uniquely include baseline_side")
        shifts = tuple(_shift(value, "shift_variants") for value in self.shift_variants)
        if not shifts or len(set(shifts)) != len(shifts) or (0.0, 0.0) not in shifts:
            raise ValueError("shift_variants must uniquely include (0,0)")
        common_shift = _shift(self.common_shift, "common_shift")
        duration = _positive(self.baseline_duration, "baseline_duration")
        horizons = tuple(
            _positive(value, "horizon_variants") for value in self.horizon_variants
        )
        if (
            not horizons
            or len(set(horizons)) != len(horizons)
            or duration not in horizons
        ):
            raise ValueError("horizon_variants must uniquely include baseline_duration")
        observation_interval = _positive(
            self.observation_interval, "observation_interval"
        )
        feature_interval = _positive(self.feature_interval, "feature_interval")
        for horizon in horizons:
            _duration_count(horizon, observation_interval, "observation_interval")
            _duration_count(horizon, feature_interval, "feature_interval")
        cadence = tuple(self.cadence_feature_counts)
        baseline_observations = _duration_count(
            duration, observation_interval, "observation_interval"
        )
        baseline_features = _duration_count(
            duration, feature_interval, "feature_interval"
        )
        if (
            not cadence
            or any(
                type(count) is not int
                or count < 2
                or count > baseline_observations
                for count in cadence
            )
            or len(set(cadence)) != len(cadence)
            or baseline_features not in cadence
        ):
            raise ValueError(
                "cadence_feature_counts must uniquely include the baseline count"
            )
        thresholds = tuple(_finite(value, "threshold") for value in self.thresholds)
        if not thresholds or any(
            right <= left for left, right in zip(thresholds, thresholds[1:])
        ):
            raise ValueError("thresholds must be nonempty and strictly increasing")
        reference = _finite(self.reference_threshold, "reference_threshold")
        if reference not in thresholds:
            raise ValueError("reference_threshold must be one declared threshold")
        if type(self.energy_bin_count) is not int or self.energy_bin_count < 2:
            raise ValueError("energy_bin_count must be an integer at least two")
        object.__setattr__(self, "resolution_sides", sides)
        object.__setattr__(self, "shift_variants", shifts)
        object.__setattr__(self, "common_shift", common_shift)
        object.__setattr__(self, "baseline_duration", duration)
        object.__setattr__(self, "horizon_variants", horizons)
        object.__setattr__(self, "observation_interval", observation_interval)
        object.__setattr__(self, "feature_interval", feature_interval)
        object.__setattr__(self, "cadence_feature_counts", cadence)
        object.__setattr__(self, "thresholds", thresholds)
        object.__setattr__(self, "reference_threshold", reference)

    @property
    def baseline_observation_count(self) -> int:
        return _duration_count(
            self.baseline_duration,
            self.observation_interval,
            "observation_interval",
        )

    @property
    def baseline_feature_count(self) -> int:
        return _duration_count(
            self.baseline_duration, self.feature_interval, "feature_interval"
        )


@dataclass(frozen=True)
class FieldRunSpec:
    """One shifted-grid, horizon, and cadence declaration."""

    name: str
    side: int
    shift: tuple[float, float]
    duration: float
    observation_count: int
    feature_sample_count: int
    roles: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("run name must be nonempty")
        if type(self.side) is not int or self.side < 3:
            raise ValueError("run side must be an integer at least three")
        shift = _shift(self.shift, "run shift")
        duration = _positive(self.duration, "run duration")
        if type(self.observation_count) is not int or self.observation_count < 3:
            raise ValueError("observation_count must be an integer at least three")
        if (
            type(self.feature_sample_count) is not int
            or not 2 <= self.feature_sample_count <= self.observation_count
        ):
            raise ValueError("feature_sample_count lies outside the observation grid")
        roles = tuple(self.roles)
        allowed = {"baseline", "resolution", "shift", "cadence", "horizon"}
        if not roles or len(set(roles)) != len(roles) or not set(roles) <= allowed:
            raise ValueError("run roles are invalid")
        object.__setattr__(self, "shift", shift)
        object.__setattr__(self, "duration", duration)
        object.__setattr__(self, "roles", roles)


def shifted_cell_centred_torus_grid(
    side: int,
    shift: Sequence[float] = (0.0, 0.0),
) -> tuple[Array, Array, Array]:
    """Return a cell-centred grid shifted by fractions of one source cell.

    Angles are retained on an unwrapped representative interval. The dynamics
    is exactly periodic in both angles, while retaining a monotone axis avoids
    introducing an artificial sorting seam in interpolation.
    """

    if type(side) is not int or side < 3:
        raise ValueError("side must be an integer at least three")
    shift_1, shift_2 = _shift(shift, "shift")
    spacing = 2.0 * np.pi / side
    axis_1 = -np.pi + (np.arange(side, dtype=float) + 0.5 + shift_1) * spacing
    axis_2 = -np.pi + (np.arange(side, dtype=float) + 0.5 + shift_2) * spacing
    theta_1, theta_2 = np.meshgrid(axis_1, axis_2, indexing="ij")
    initial = np.stack(
        (theta_1, theta_2, np.zeros_like(theta_1), np.zeros_like(theta_1)),
        axis=-1,
    )
    return axis_1, axis_2, initial


def _fractional_source_indices(
    target_axis: Array,
    source_side: int,
    source_shift: float,
) -> tuple[Array, Array, Array]:
    spacing = 2.0 * np.pi / source_side
    origin = -np.pi + (0.5 + source_shift) * spacing
    coordinate = np.mod((target_axis - origin) / spacing, source_side)
    nearest = np.rint(coordinate)
    coordinate = np.where(
        np.abs(coordinate - nearest) <= 4.0e-13 * source_side,
        nearest,
        coordinate,
    )
    lower_unwrapped = np.floor(coordinate).astype(int)
    fraction = coordinate - lower_unwrapped
    lower = lower_unwrapped % source_side
    upper = (lower + 1) % source_side
    return lower, upper, fraction


def periodic_bilinear_resample(
    field: Array | Sequence[Sequence[float]],
    *,
    source_shift: Sequence[float] = (0.0, 0.0),
    target_side: int,
    target_shift: Sequence[float] = (0.0, 0.0),
) -> Array:
    """Resample a square scalar torus field onto one declared target grid."""

    values = np.asarray(field, dtype=float)
    if values.ndim != 2 or values.shape[0] != values.shape[1]:
        raise ValueError("field must be a square scalar grid")
    if values.shape[0] < 3 or not np.all(np.isfinite(values)):
        raise ValueError("field must be finite with side at least three")
    if type(target_side) is not int or target_side < 3:
        raise ValueError("target_side must be an integer at least three")
    source_shift_1, source_shift_2 = _shift(source_shift, "source_shift")
    target_shift_1, target_shift_2 = _shift(target_shift, "target_shift")
    target_axis_1, target_axis_2, _ = shifted_cell_centred_torus_grid(
        target_side, (target_shift_1, target_shift_2)
    )
    lower_1, upper_1, fraction_1 = _fractional_source_indices(
        target_axis_1, values.shape[0], source_shift_1
    )
    lower_2, upper_2, fraction_2 = _fractional_source_indices(
        target_axis_2, values.shape[1], source_shift_2
    )
    f1 = fraction_1[:, None]
    f2 = fraction_2[None, :]
    lower_lower = values[np.ix_(lower_1, lower_2)]
    upper_lower = values[np.ix_(upper_1, lower_2)]
    lower_upper = values[np.ix_(lower_1, upper_2)]
    upper_upper = values[np.ix_(upper_1, upper_2)]
    return (
        (1.0 - f1) * (1.0 - f2) * lower_lower
        + f1 * (1.0 - f2) * upper_lower
        + (1.0 - f1) * f2 * lower_upper
        + f1 * f2 * upper_upper
    )


def threshold_filtration(
    field: Array | Sequence[Sequence[float]],
    thresholds: Iterable[float],
) -> list[dict[str, object]]:
    """Return torus-component summaries of nested scalar sublevel sets."""

    values = np.asarray(field, dtype=float)
    if values.ndim != 2 or values.shape[0] != values.shape[1]:
        raise ValueError("field must be a square scalar grid")
    if not np.all(np.isfinite(values)):
        raise ValueError("field must be finite")
    declared = tuple(_finite(value, "threshold") for value in thresholds)
    if not declared or any(
        right <= left for left, right in zip(declared, declared[1:])
    ):
        raise ValueError("thresholds must be strictly increasing")
    records: list[dict[str, object]] = []
    cell_count = values.size
    previous_count = -1
    for threshold in declared:
        mask = values <= threshold
        active_count = int(np.count_nonzero(mask))
        if active_count < previous_count:
            raise AssertionError("sublevel filtration is not nested")
        previous_count = active_count
        _, sizes = toroidal_connected_components(mask)
        records.append(
            {
                "threshold": threshold,
                "active_cell_count": active_count,
                "active_fraction": active_count / cell_count,
                "component_count": len(sizes),
                "component_sizes": list(sizes),
                "largest_component_fraction": (
                    (sizes[0] / cell_count) if sizes else 0.0
                ),
            }
        )
    return records


def _correlation(left: Array, right: Array) -> float:
    a = np.asarray(left, dtype=float).reshape(-1)
    b = np.asarray(right, dtype=float).reshape(-1)
    if a.shape != b.shape or not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise ValueError("correlation inputs must be equal-sized finite arrays")
    a_scale = float(np.std(a))
    b_scale = float(np.std(b))
    if a_scale == 0.0 or b_scale == 0.0:
        return 1.0 if np.array_equal(a, b) else 0.0
    return float(np.corrcoef(a, b)[0, 1])


def field_comparison(
    reference: Array,
    candidate: Array,
    thresholds: Sequence[float],
) -> dict[str, object]:
    """Compare two scalar fields already living on one common torus grid."""

    left = np.asarray(reference, dtype=float)
    right = np.asarray(candidate, dtype=float)
    if left.shape != right.shape or left.ndim != 2 or left.shape[0] != left.shape[1]:
        raise ValueError("comparison fields must share one square grid")
    if not np.all(np.isfinite(left)) or not np.all(np.isfinite(right)):
        raise ValueError("comparison fields must be finite")
    difference = right - left
    threshold_rows = []
    for threshold in thresholds:
        declared = _finite(threshold, "threshold")
        left_mask = left <= declared
        right_mask = right <= declared
        intersection = int(np.count_nonzero(left_mask & right_mask))
        union = int(np.count_nonzero(left_mask | right_mask))
        threshold_rows.append(
            {
                "threshold": declared,
                "reference_active_count": int(np.count_nonzero(left_mask)),
                "candidate_active_count": int(np.count_nonzero(right_mask)),
                "intersection_count": intersection,
                "union_count": union,
                "jaccard": (intersection / union) if union else 1.0,
            }
        )
    return {
        "maximum_absolute_difference": float(np.max(np.abs(difference))),
        "rms_difference": float(np.sqrt(np.mean(difference * difference))),
        "mean_signed_difference": float(np.mean(difference)),
        "pearson_correlation": _correlation(left, right),
        "threshold_overlap": threshold_rows,
    }


def energy_association(
    initial_energy: Array,
    field: Array,
    *,
    bin_count: int,
    reference_threshold: float,
) -> dict[str, object]:
    """Describe, without causal language, how a field varies across energy bins."""

    energy = np.asarray(initial_energy, dtype=float)
    values = np.asarray(field, dtype=float)
    if energy.shape != values.shape or energy.ndim != 2:
        raise ValueError("energy and field must share one two-dimensional grid")
    if not np.all(np.isfinite(energy)) or not np.all(np.isfinite(values)):
        raise ValueError("energy-association inputs must be finite")
    if type(bin_count) is not int or bin_count < 2:
        raise ValueError("bin_count must be an integer at least two")
    threshold = _finite(reference_threshold, "reference_threshold")
    flat_energy = energy.reshape(-1)
    flat_values = values.reshape(-1)
    edges = np.quantile(flat_energy, np.linspace(0.0, 1.0, bin_count + 1))
    assignments = np.searchsorted(edges[1:-1], flat_energy, side="right")
    bins: list[dict[str, object]] = []
    for index in range(bin_count):
        selected = assignments == index
        count = int(np.count_nonzero(selected))
        if count:
            energy_values = flat_energy[selected]
            field_values = flat_values[selected]
            record: dict[str, object] = {
                "bin": index,
                "count": count,
                "energy_minimum": float(np.min(energy_values)),
                "energy_maximum": float(np.max(energy_values)),
                "field_mean": float(np.mean(field_values)),
                "field_median": float(np.median(field_values)),
                "field_q10": float(np.quantile(field_values, 0.10)),
                "field_q90": float(np.quantile(field_values, 0.90)),
                "below_reference_threshold_fraction": float(
                    np.mean(field_values <= threshold)
                ),
            }
        else:
            record = {
                "bin": index,
                "count": 0,
                "energy_minimum": None,
                "energy_maximum": None,
                "field_mean": None,
                "field_median": None,
                "field_q10": None,
                "field_q90": None,
                "below_reference_threshold_fraction": None,
            }
        bins.append(record)
    return {
        "interpretation": (
            "Descriptive association only; energy bins neither prove nor remove a "
            "dynamical mechanism."
        ),
        "reference_threshold": threshold,
        "pearson_energy_field": _correlation(flat_energy, flat_values),
        "spearman_energy_field": _correlation(
            rankdata(flat_energy, method="average"),
            rankdata(flat_values, method="average"),
        ),
        "energy_quantile_edges": [float(value) for value in edges],
        "bins": bins,
    }


def _run_plan(config: PersistenceLabConfig) -> tuple[FieldRunSpec, ...]:
    baseline_name = "baseline"
    specs: dict[str, FieldRunSpec] = {}

    def add(spec: FieldRunSpec) -> None:
        if spec.name in specs:
            raise AssertionError(f"duplicate persistence run name {spec.name}")
        specs[spec.name] = spec

    add(
        FieldRunSpec(
            baseline_name,
            config.baseline_side,
            (0.0, 0.0),
            config.baseline_duration,
            config.baseline_observation_count,
            config.baseline_feature_count,
            ("baseline", "resolution", "shift", "cadence", "horizon"),
        )
    )
    for side in config.resolution_sides:
        if side == config.baseline_side:
            continue
        add(
            FieldRunSpec(
                f"resolution-side-{side}",
                side,
                (0.0, 0.0),
                config.baseline_duration,
                config.baseline_observation_count,
                config.baseline_feature_count,
                ("resolution",),
            )
        )
    for shift_1, shift_2 in config.shift_variants:
        if (shift_1, shift_2) == (0.0, 0.0):
            continue
        add(
            FieldRunSpec(
                f"shift-{shift_1:g}-{shift_2:g}",
                config.baseline_side,
                (shift_1, shift_2),
                config.baseline_duration,
                config.baseline_observation_count,
                config.baseline_feature_count,
                ("shift",),
            )
        )
    for duration in config.horizon_variants:
        if duration == config.baseline_duration:
            continue
        add(
            FieldRunSpec(
                f"horizon-{duration:g}",
                config.baseline_side,
                (0.0, 0.0),
                duration,
                _duration_count(
                    duration, config.observation_interval, "observation_interval"
                ),
                _duration_count(
                    duration, config.feature_interval, "feature_interval"
                ),
                ("horizon",),
            )
        )
    for count in config.cadence_feature_counts:
        if count == config.baseline_feature_count:
            continue
        add(
            FieldRunSpec(
                f"cadence-{count}",
                config.baseline_side,
                (0.0, 0.0),
                config.baseline_duration,
                config.baseline_observation_count,
                count,
                ("cadence",),
            )
        )
    return tuple(specs.values())


def _feature_indices(observation_count: int, feature_count: int) -> tuple[int, ...]:
    values = np.linspace(0, observation_count - 1, feature_count, dtype=int)
    indices = tuple(int(value) for value in values)
    if len(set(indices)) != len(indices):
        raise ValueError("feature cadence produces duplicate observation indices")
    return indices


def _simulate_states(
    spec: FieldRunSpec,
    parameters: DoublePendulumParameters,
    integration: IntegrationConfig,
) -> tuple[Array, Array, float, Array]:
    _, _, initial = shifted_cell_centred_torus_grid(spec.side, spec.shift)
    times = np.linspace(0.0, spec.duration, spec.observation_count)
    states = np.empty((spec.observation_count, spec.side, spec.side, 4), dtype=float)
    maximum_energy_drift = 0.0
    for row in range(spec.side):
        for column in range(spec.side):
            trajectory = simulate_double_pendulum(
                initial[row, column], times, parameters, integration
            )
            states[:, row, column] = trajectory.states
            maximum_energy_drift = max(
                maximum_energy_drift, trajectory.max_scaled_energy_drift
            )
    return times, states, maximum_energy_drift, np.asarray(
        total_energy(initial, parameters), dtype=float
    )


def _run_record(
    spec: FieldRunSpec,
    *,
    states: Array,
    maximum_energy_drift: float,
    initial_energy: Array,
    config: PersistenceLabConfig,
    parameters: DoublePendulumParameters,
) -> dict[str, object]:
    indices = _feature_indices(spec.observation_count, spec.feature_sample_count)
    atlas = build_operational_atlas(
        states,
        sample_indices=indices,
        log_stretch_threshold=config.reference_threshold,
        angular_velocity_scale=parameters.characteristic_angular_speed,
    )
    source = atlas.log_stretch
    common = periodic_bilinear_resample(
        source,
        source_shift=spec.shift,
        target_side=config.common_side,
        target_shift=config.common_shift,
    )
    no_sampled_turn = (
        (atlas.first_sampled_turn_excursion_arm_1 < 0)
        & (atlas.first_sampled_turn_excursion_arm_2 < 0)
    )
    source_marked = (source <= config.reference_threshold) & no_sampled_turn
    return {
        "name": spec.name,
        "spec": asdict(spec),
        "feature_sample_indices": list(indices),
        "source_log_stretch": source.tolist(),
        "common_log_stretch": common.tolist(),
        "source_initial_energy": initial_energy.tolist(),
        "maximum_sampled_scaled_energy_drift": maximum_energy_drift,
        "source_no_sampled_full_turn_mask": no_sampled_turn.tolist(),
        "source_no_sampled_full_turn_fraction": float(np.mean(no_sampled_turn)),
        "source_reference_threshold_marked_count": int(
            np.count_nonzero(source_marked)
        ),
        "threshold_filtration_on_common_grid": threshold_filtration(
            common, config.thresholds
        ),
    }


def _record_map(records: Sequence[dict[str, object]]) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for row in records:
        name = row.get("name")
        if not isinstance(name, str) or name in result:
            raise ValueError("persistence run names must be unique strings")
        result[name] = row
    return result


def _common_field(row: dict[str, object]) -> Array:
    return np.asarray(row["common_log_stretch"], dtype=float)


def _study_ledgers(
    records: Sequence[dict[str, object]], config: PersistenceLabConfig
) -> dict[str, object]:
    rows = _record_map(records)
    baseline = rows["baseline"]
    baseline_field = _common_field(baseline)

    resolution_names = [
        "baseline" if side == config.baseline_side else f"resolution-side-{side}"
        for side in sorted(config.resolution_sides)
    ]
    resolution_reference = max(
        resolution_names,
        key=lambda name: int(rows[name]["spec"]["side"]),  # type: ignore[index]
    )
    resolution_field = _common_field(rows[resolution_reference])
    resolution = {
        "interpretation": (
            "All fields are compared after declared periodic bilinear transport "
            "to the common grid; this is a Tier-1 discretization study."
        ),
        "reference_run": resolution_reference,
        "runs": [
            {
                "name": name,
                "side": rows[name]["spec"]["side"],  # type: ignore[index]
                "comparison_to_highest_resolution": field_comparison(
                    resolution_field, _common_field(rows[name]), config.thresholds
                ),
            }
            for name in resolution_names
        ],
    }

    shift_names = [
        "baseline"
        if shift == (0.0, 0.0)
        else f"shift-{shift[0]:g}-{shift[1]:g}"
        for shift in config.shift_variants
    ]
    shift = {
        "interpretation": (
            "Grid-origin sensitivity on the same resolution and horizon; no "
            "component identity is assumed across shifted samples."
        ),
        "reference_run": "baseline",
        "runs": [
            {
                "name": name,
                "shift": list(rows[name]["spec"]["shift"]),  # type: ignore[index]
                "comparison_to_unshifted": field_comparison(
                    baseline_field, _common_field(rows[name]), config.thresholds
                ),
            }
            for name in shift_names
        ],
    }

    cadence_names = [
        "baseline"
        if count == config.baseline_feature_count
        else f"cadence-{count}"
        for count in sorted(config.cadence_feature_counts)
    ]
    cadence_reference = max(
        cadence_names,
        key=lambda name: int(rows[name]["spec"]["feature_sample_count"]),  # type: ignore[index]
    )
    cadence_field = _common_field(rows[cadence_reference])
    cadence = {
        "interpretation": (
            "Equal-RMS finite schedules are distinct declared observation "
            "protocols; comparison to the densest schedule is descriptive "
            "cadence sensitivity, not an enclosure error bound."
        ),
        "reference_run": cadence_reference,
        "runs": [
            {
                "name": name,
                "feature_sample_count": rows[name]["spec"][  # type: ignore[index]
                    "feature_sample_count"
                ],
                "comparison_to_densest": field_comparison(
                    cadence_field, _common_field(rows[name]), config.thresholds
                ),
            }
            for name in cadence_names
        ],
    }

    horizon_names = [
        "baseline"
        if duration == config.baseline_duration
        else f"horizon-{duration:g}"
        for duration in sorted(config.horizon_variants)
    ]
    continuation_rows: list[dict[str, object]] = []
    for index, name in enumerate(horizon_names):
        row: dict[str, object] = {
            "name": name,
            "duration": rows[name]["spec"]["duration"],  # type: ignore[index]
            "threshold_filtration": rows[name][
                "threshold_filtration_on_common_grid"
            ],
        }
        if index > 0:
            previous = horizon_names[index - 1]
            row["comparison_to_previous_horizon"] = field_comparison(
                _common_field(rows[previous]),
                _common_field(rows[name]),
                config.thresholds,
            )
        continuation_rows.append(row)
    horizon = {
        "interpretation": (
            "Horizon changes the operational geometry by definition, so these are "
            "different declared protocols. Their continuation/lifetime observations "
            "carry no numerical passed flag."
        ),
        "has_numerical_pass_fail_status": False,
        "runs": continuation_rows,
    }
    return {
        "resolution_study": resolution,
        "shift_study": shift,
        "cadence_study": cadence,
        "horizon_continuation": horizon,
    }


def _parameter_record(parameters: DoublePendulumParameters) -> dict[str, float]:
    return {
        "m1": parameters.m1,
        "m2": parameters.m2,
        "l1": parameters.l1,
        "l2": parameters.l2,
        "g": parameters.g,
    }


def _integration_record(config: IntegrationConfig) -> dict[str, object]:
    return {
        "rtol": config.rtol,
        "atol": config.atol,
        "max_step": config.max_step,
        "energy_drift_tolerance": config.energy_drift_tolerance,
    }


def _verification_payload(run_count: int) -> dict[str, object]:
    return {
        "passed": True,
        "claim_tier": 1,
        "run_count": run_count,
        "common_grid_resampling_reconstructed": True,
        "study_ledgers_reconstructed": True,
        "declared_ode_to_fields_verified": False,
        "outward_flow_enclosure_verified": False,
        "method": (
            "strict schema validation of serialized Tier-1 source fields plus "
            "reconstruction of periodic common-grid transport, mask summaries, "
            "filtrations, comparisons, and energy bins"
        ),
    }


def build_persistence_report(
    config: PersistenceLabConfig = PersistenceLabConfig(),
    parameters: DoublePendulumParameters = DoublePendulumParameters(),
    integration: IntegrationConfig = IntegrationConfig(
        rtol=1.0e-9,
        atol=1.0e-11,
        max_step=0.02,
        energy_drift_tolerance=1.0e-7,
    ),
) -> dict[str, object]:
    """Run the deterministic Tier-1 persistence family."""

    if integration.energy_drift_tolerance is None:
        raise ValueError("the persistence laboratory requires an energy gate")
    specs = _run_plan(config)
    state_cache: dict[
        tuple[int, tuple[float, float], float, int], tuple[Array, Array, float, Array]
    ] = {}
    records: list[dict[str, object]] = []
    for spec in specs:
        key = (spec.side, spec.shift, spec.duration, spec.observation_count)
        if key not in state_cache:
            state_cache[key] = _simulate_states(spec, parameters, integration)
        _times, states, maximum_energy_drift, initial_energy = state_cache[key]
        records.append(
            _run_record(
                spec,
                states=states,
                maximum_energy_drift=maximum_energy_drift,
                initial_energy=initial_energy,
                config=config,
                parameters=parameters,
            )
        )
    studies = _study_ledgers(records, config)
    baseline = _record_map(records)["baseline"]
    association = energy_association(
        np.asarray(baseline["source_initial_energy"], dtype=float),
        np.asarray(baseline["source_log_stretch"], dtype=float),
        bin_count=config.energy_bin_count,
        reference_threshold=config.reference_threshold,
    )
    report: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "claim_tier": 1,
        "status": "tier1_persistence_diagnostic",
        "state_convention": ["theta1", "theta2", "omega1", "omega2"],
        "parameters": _parameter_record(parameters),
        "integration": _integration_record(integration),
        "config": asdict(config),
        "common_evaluation_grid": {
            "topology": "cell-centred product torus",
            "side": config.common_side,
            "shift_in_common_cells": list(config.common_shift),
            "transport": "periodic bilinear interpolation of scalar log-stretch",
            "categorical_component_identities_transferred": False,
            "categorical_source_masks_transported": False,
        },
        "runs": records,
        **studies,
        "baseline_energy_association": association,
        "proof_boundary": TIER1_BOUNDARY,
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }
    verification = verify_persistence_report(report)
    if verification.get("passed") is not True:
        raise AssertionError(f"persistence self-verification failed: {verification}")
    report["internal_consistency_verification"] = verification
    return report


def build_canonical_persistence_report() -> dict[str, object]:
    """Build the bounded-runtime canonical persistence report."""

    return build_persistence_report()


def research_persistence_config() -> PersistenceLabConfig:
    """Return the atlas-matched persistence declaration used for research.

    This larger preset shares the main portrait's ``N=13``, ``T=4`` and nine
    equal-RMS feature samples, then surrounds it by the resolution, origin,
    cadence, threshold, energy, and horizon controls needed to interpret that
    portrait. It is intentionally opt-in because it is substantially slower
    than the bounded canonical smoke report.
    """

    return PersistenceLabConfig(
        baseline_side=13,
        resolution_sides=(9, 13, 17),
        shift_variants=((0.0, 0.0), (0.5, 0.0), (0.0, 0.5), (0.5, 0.5)),
        common_side=51,
        common_shift=(0.25, 0.25),
        baseline_duration=4.0,
        horizon_variants=(2.0, 4.0, 6.0),
        observation_interval=0.05,
        feature_interval=0.5,
        cadence_feature_counts=(5, 9, 17, 41, 81),
        thresholds=(0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5),
        reference_threshold=0.5,
        energy_bin_count=5,
    )


def build_research_persistence_report() -> dict[str, object]:
    """Build the atlas-matched, opt-in persistence report."""

    return build_persistence_report(research_persistence_config())


def _same_json(left: object, right: object) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            _same_json(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            _same_json(a, b) for a, b in zip(left, right)
        )
    return left == right


def _numeric_grid(value: object, side: int, name: str) -> Array:
    if not isinstance(value, list) or len(value) != side:
        raise ValueError(f"{name} must contain {side} rows")
    rows = []
    for row in value:
        if not isinstance(row, list) or len(row) != side:
            raise ValueError(f"{name} has an invalid row")
        parsed = []
        for entry in row:
            if isinstance(entry, bool) or not isinstance(entry, (int, float)):
                raise ValueError(f"{name} entries must be JSON numbers")
            parsed.append(_finite(entry, name))
        rows.append(parsed)
    return np.asarray(rows, dtype=float)


def _boolean_grid(value: object, side: int, name: str) -> Array:
    if not isinstance(value, list) or len(value) != side:
        raise ValueError(f"{name} must contain {side} rows")
    rows = []
    for row in value:
        if not isinstance(row, list) or len(row) != side:
            raise ValueError(f"{name} has an invalid row")
        if any(type(entry) is not bool for entry in row):
            raise ValueError(f"{name} entries must be JSON booleans")
        rows.append(row)
    return np.asarray(rows, dtype=bool)


def _config_from_record(record: object) -> PersistenceLabConfig:
    if not isinstance(record, dict):
        raise ValueError("config must be an object")
    expected_keys = {
        "baseline_side",
        "resolution_sides",
        "shift_variants",
        "common_side",
        "common_shift",
        "baseline_duration",
        "horizon_variants",
        "observation_interval",
        "feature_interval",
        "cadence_feature_counts",
        "thresholds",
        "reference_threshold",
        "energy_bin_count",
    }
    if set(record) != expected_keys:
        raise ValueError("config keys are inconsistent")
    return PersistenceLabConfig(
        baseline_side=record.get("baseline_side"),  # type: ignore[arg-type]
        resolution_sides=tuple(record.get("resolution_sides", ())),  # type: ignore[arg-type]
        shift_variants=tuple(
            tuple(value) for value in record.get("shift_variants", ())  # type: ignore[union-attr]
        ),
        common_side=record.get("common_side"),  # type: ignore[arg-type]
        common_shift=tuple(record.get("common_shift", ())),  # type: ignore[arg-type]
        baseline_duration=record.get("baseline_duration"),  # type: ignore[arg-type]
        horizon_variants=tuple(record.get("horizon_variants", ())),  # type: ignore[arg-type]
        observation_interval=record.get("observation_interval"),  # type: ignore[arg-type]
        feature_interval=record.get("feature_interval"),  # type: ignore[arg-type]
        cadence_feature_counts=tuple(
            record.get("cadence_feature_counts", ())  # type: ignore[arg-type]
        ),
        thresholds=tuple(record.get("thresholds", ())),  # type: ignore[arg-type]
        reference_threshold=record.get("reference_threshold"),  # type: ignore[arg-type]
        energy_bin_count=record.get("energy_bin_count"),  # type: ignore[arg-type]
    )


def _spec_from_record(record: object) -> FieldRunSpec:
    if not isinstance(record, dict):
        raise ValueError("run spec must be an object")
    if set(record) != {
        "name",
        "side",
        "shift",
        "duration",
        "observation_count",
        "feature_sample_count",
        "roles",
    }:
        raise ValueError("run spec keys are inconsistent")
    return FieldRunSpec(
        name=record.get("name"),  # type: ignore[arg-type]
        side=record.get("side"),  # type: ignore[arg-type]
        shift=tuple(record.get("shift", ())),  # type: ignore[arg-type]
        duration=record.get("duration"),  # type: ignore[arg-type]
        observation_count=record.get("observation_count"),  # type: ignore[arg-type]
        feature_sample_count=record.get("feature_sample_count"),  # type: ignore[arg-type]
        roles=tuple(record.get("roles", ())),  # type: ignore[arg-type]
    )


def verify_persistence_report(report: dict[str, object]) -> dict[str, object]:
    """Reconstruct the serialized Tier-1 comparison ledger without an ODE solve."""

    try:
        if not isinstance(report, dict) or report.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unknown persistence report schema")
        required_top_level = {
            "schema_version",
            "claim_tier",
            "status",
            "state_convention",
            "parameters",
            "integration",
            "config",
            "common_evaluation_grid",
            "runs",
            "resolution_study",
            "shift_study",
            "cadence_study",
            "horizon_continuation",
            "baseline_energy_association",
            "proof_boundary",
            "environment",
        }
        if set(report) not in (
            required_top_level,
            required_top_level | {"internal_consistency_verification"},
        ):
            raise ValueError("top-level persistence report keys are inconsistent")
        if type(report.get("claim_tier")) is not int or report.get("claim_tier") != 1:
            raise ValueError("persistence report must declare Tier 1")
        if report.get("status") != "tier1_persistence_diagnostic":
            raise ValueError("persistence status is inconsistent")
        if report.get("state_convention") != [
            "theta1",
            "theta2",
            "omega1",
            "omega2",
        ]:
            raise ValueError("state convention is inconsistent")
        if report.get("proof_boundary") != TIER1_BOUNDARY:
            raise ValueError("Tier-1 proof boundary is missing")
        config = _config_from_record(report.get("config"))
        parameters_record = report.get("parameters")
        if not isinstance(parameters_record, dict) or set(parameters_record) != {
            "m1",
            "m2",
            "l1",
            "l2",
            "g",
        }:
            raise ValueError("physical parameter declaration is inconsistent")
        parameters = DoublePendulumParameters(
            **{
                key: _positive(value, f"parameters.{key}")
                for key, value in parameters_record.items()
            }
        )
        expected_common = {
            "topology": "cell-centred product torus",
            "side": config.common_side,
            "shift_in_common_cells": list(config.common_shift),
            "transport": "periodic bilinear interpolation of scalar log-stretch",
            "categorical_component_identities_transferred": False,
            "categorical_source_masks_transported": False,
        }
        if not _same_json(report.get("common_evaluation_grid"), expected_common):
            raise ValueError("common evaluation grid is inconsistent")
        integration_record = report.get("integration")
        if not isinstance(integration_record, dict) or set(integration_record) != {
            "rtol",
            "atol",
            "max_step",
            "energy_drift_tolerance",
        }:
            raise ValueError("integration declaration is missing")
        gate = integration_record.get("energy_drift_tolerance")
        if gate is None:
            raise ValueError("persistence report disabled the energy gate")
        integration = IntegrationConfig(
            rtol=_positive(integration_record.get("rtol"), "integration.rtol"),
            atol=_positive(integration_record.get("atol"), "integration.atol"),
            max_step=_positive(
                integration_record.get("max_step"), "integration.max_step"
            ),
            energy_drift_tolerance=_positive(gate, "energy_drift_tolerance"),
        )
        energy_gate = float(integration.energy_drift_tolerance)
        environment = report.get("environment")
        if (
            not isinstance(environment, dict)
            or set(environment) != {"python", "numpy", "scipy"}
            or any(not isinstance(value, str) or not value for value in environment.values())
        ):
            raise ValueError("environment declaration is inconsistent")

        serialized_runs = report.get("runs")
        if not isinstance(serialized_runs, list):
            raise ValueError("runs must be a list")
        expected_specs = {spec.name: spec for spec in _run_plan(config)}
        reconstructed_rows: list[dict[str, object]] = []
        seen: set[str] = set()
        for row in serialized_runs:
            if not isinstance(row, dict):
                raise ValueError("run row must be an object")
            if set(row) != {
                "name",
                "spec",
                "feature_sample_indices",
                "source_log_stretch",
                "common_log_stretch",
                "source_initial_energy",
                "maximum_sampled_scaled_energy_drift",
                "source_no_sampled_full_turn_mask",
                "source_no_sampled_full_turn_fraction",
                "source_reference_threshold_marked_count",
                "threshold_filtration_on_common_grid",
            }:
                raise ValueError("run row keys are inconsistent")
            spec = _spec_from_record(row.get("spec"))
            if spec.name in seen or spec.name not in expected_specs:
                raise ValueError("run name is duplicated or undeclared")
            seen.add(spec.name)
            if spec != expected_specs[spec.name] or row.get("name") != spec.name:
                raise ValueError("run spec differs from the declared plan")
            expected_indices = list(
                _feature_indices(spec.observation_count, spec.feature_sample_count)
            )
            serialized_indices = row.get("feature_sample_indices")
            if (
                not isinstance(serialized_indices, list)
                or any(type(value) is not int for value in serialized_indices)
                or serialized_indices != expected_indices
            ):
                raise ValueError("feature indices are inconsistent")
            source = _numeric_grid(
                row.get("source_log_stretch"), spec.side, "source_log_stretch"
            )
            common = _numeric_grid(
                row.get("common_log_stretch"),
                config.common_side,
                "common_log_stretch",
            )
            initial_energy = _numeric_grid(
                row.get("source_initial_energy"), spec.side, "source_initial_energy"
            )
            _, _, initial_states = shifted_cell_centred_torus_grid(
                spec.side, spec.shift
            )
            expected_energy = np.asarray(
                total_energy(initial_states, parameters), dtype=float
            )
            if not np.array_equal(initial_energy, expected_energy):
                raise ValueError("initial-energy field does not reconstruct")
            expected_resample = periodic_bilinear_resample(
                source,
                source_shift=spec.shift,
                target_side=config.common_side,
                target_shift=config.common_shift,
            )
            if not np.array_equal(common, expected_resample):
                raise ValueError("common-grid field does not reconstruct")
            drift = row.get("maximum_sampled_scaled_energy_drift")
            if isinstance(drift, bool) or not isinstance(drift, (int, float)):
                raise ValueError("energy drift must be a JSON number")
            parsed_drift = _finite(drift, "maximum energy drift")
            if parsed_drift < 0.0 or parsed_drift > energy_gate:
                raise ValueError("energy drift violates the declared gate")
            no_turn_mask = _boolean_grid(
                row.get("source_no_sampled_full_turn_mask"),
                spec.side,
                "source_no_sampled_full_turn_mask",
            )
            no_turn = row.get("source_no_sampled_full_turn_fraction")
            if isinstance(no_turn, bool) or not isinstance(no_turn, (int, float)):
                raise ValueError("no-turn fraction must be a JSON number")
            parsed_no_turn = _finite(no_turn, "no-turn fraction")
            expected_no_turn = float(np.mean(no_turn_mask))
            if parsed_no_turn != expected_no_turn:
                raise ValueError("no-turn fraction does not reconstruct from its mask")
            marked_count = row.get("source_reference_threshold_marked_count")
            if type(marked_count) is not int:
                raise ValueError("source marked count must be a JSON integer")
            expected_marked_count = int(
                np.count_nonzero(
                    (source <= config.reference_threshold) & no_turn_mask
                )
            )
            if marked_count != expected_marked_count:
                raise ValueError("source marked count does not reconstruct")
            expected_filtration = threshold_filtration(common, config.thresholds)
            if not _same_json(
                row.get("threshold_filtration_on_common_grid"),
                expected_filtration,
            ):
                raise ValueError("threshold filtration does not reconstruct")
            reconstructed_rows.append(
                {
                    "name": spec.name,
                    "spec": asdict(spec),
                    "feature_sample_indices": expected_indices,
                    "source_log_stretch": source.tolist(),
                    "common_log_stretch": common.tolist(),
                    "source_initial_energy": initial_energy.tolist(),
                    "maximum_sampled_scaled_energy_drift": parsed_drift,
                    "source_no_sampled_full_turn_mask": no_turn_mask.tolist(),
                    "source_no_sampled_full_turn_fraction": parsed_no_turn,
                    "source_reference_threshold_marked_count": expected_marked_count,
                    "threshold_filtration_on_common_grid": expected_filtration,
                }
            )
        if seen != set(expected_specs):
            raise ValueError("run plan is incomplete")

        expected_studies = _study_ledgers(reconstructed_rows, config)
        for key, value in expected_studies.items():
            if not _same_json(report.get(key), value):
                raise ValueError(f"{key} does not reconstruct")
        baseline = _record_map(reconstructed_rows)["baseline"]
        expected_association = energy_association(
            np.asarray(baseline["source_initial_energy"], dtype=float),
            np.asarray(baseline["source_log_stretch"], dtype=float),
            bin_count=config.energy_bin_count,
            reference_threshold=config.reference_threshold,
        )
        if not _same_json(report.get("baseline_energy_association"), expected_association):
            raise ValueError("energy association does not reconstruct")
        expected_verification = _verification_payload(len(reconstructed_rows))
        embedded = report.get("internal_consistency_verification")
        if embedded is not None and not _same_json(embedded, expected_verification):
            raise ValueError("embedded verification is inconsistent")
        return expected_verification
    except Exception as error:
        return {
            "passed": False,
            "claim_tier": 1,
            "declared_ode_to_fields_verified": False,
            "outward_flow_enclosure_verified": False,
            "error": str(error),
        }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument(
        "--research",
        action="store_true",
        help="run the slower N=13,T=4 atlas-matched persistence family",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    if arguments.verify is not None:
        if arguments.output is not None or arguments.research:
            raise ValueError("--verify cannot be combined with --output or --research")
        report = json.loads(arguments.verify.read_text(encoding="utf-8"))
        verification = verify_persistence_report(report)
        print(json.dumps(verification, indent=2, sort_keys=True))
        return 0 if verification.get("passed") is True else 1
    report = (
        build_research_persistence_report()
        if arguments.research
        else build_canonical_persistence_report()
    )
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if arguments.output is None:
        print(payload, end="")
    else:
        arguments.output.write_text(payload, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "FieldRunSpec",
    "PersistenceLabConfig",
    "SCHEMA_VERSION",
    "TIER1_BOUNDARY",
    "build_canonical_persistence_report",
    "build_persistence_report",
    "build_research_persistence_report",
    "energy_association",
    "field_comparison",
    "main",
    "periodic_bilinear_resample",
    "research_persistence_config",
    "shifted_cell_centred_torus_grid",
    "threshold_filtration",
    "verify_persistence_report",
]
