"""Operational atlas primitives for double-pendulum trajectory ensembles.

This module deliberately separates *dynamics* from *interpretation*.  A
trajectory integrator supplies an array whose final axis is
``(theta_1, theta_2, omega_1, omega_2)``.  The functions below then construct
periodic observation embeddings, finite-horizon rotation events, local
operational stretching, and torus-aware connected components.

The word ``stable`` is always qualified by a finite observation horizon and a
declared threshold.  Nothing here promotes a grid image to a theorem about
Lyapunov stability, infinite-time dynamics, or synchronization between
independent simulations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np


Array = np.ndarray


def _states(values: Array | Sequence[float]) -> Array:
    result = np.asarray(values, dtype=float)
    if result.shape[-1:] != (4,):
        raise ValueError("states must end in (theta_1, theta_2, omega_1, omega_2)")
    if not np.all(np.isfinite(result)):
        raise ValueError("states must be finite")
    return result


def wrap_angle(angle: Array | float) -> Array:
    """Return angles in ``[-pi, pi)`` with the circle seam identified."""
    values = np.asarray(angle, dtype=float)
    return (values + np.pi) % (2.0 * np.pi) - np.pi


def torus_angle_distance(left: Array, right: Array) -> Array:
    """Geodesic product-torus distance for arrays ending in two angles."""
    a = np.asarray(left, dtype=float)
    b = np.asarray(right, dtype=float)
    if a.shape != b.shape or a.shape[-1:] != (2,):
        raise ValueError("angle arrays must have the same shape and end in two coordinates")
    delta = wrap_angle(a - b)
    return np.linalg.norm(delta, axis=-1)


def cell_centred_torus_grid(side: int) -> tuple[Array, Array, Array]:
    """Return a seam-free ``side x side`` grid on the initial-angle torus.

    The same one-dimensional cell centres are used for both absolute arm
    angles.  Endpoints are excluded, so no physical configuration is counted
    twice at the ``-pi/pi`` seam.
    """
    if type(side) is not int or side < 3:
        raise ValueError("side must be an integer at least three")
    angles = -np.pi + (np.arange(side, dtype=float) + 0.5) * (2.0 * np.pi / side)
    theta_1, theta_2 = np.meshgrid(angles, angles, indexing="ij")
    initial = np.stack((theta_1, theta_2, np.zeros_like(theta_1), np.zeros_like(theta_2)), axis=-1)
    return angles, angles.copy(), initial


def phase_observation(
    states: Array | Sequence[float],
    *,
    angular_velocity_scale: float = 1.0,
) -> Array:
    """Embed phase states without introducing an artificial angle seam.

    The observation is

    ``(sin theta1, cos theta1, sin theta2, cos theta2,
       omega1/scale, omega2/scale)``.

    ``angular_velocity_scale`` is part of the declared output metric, not a
    fitted quantity.
    """
    values = _states(states)
    if not np.isfinite(angular_velocity_scale) or angular_velocity_scale <= 0:
        raise ValueError("angular_velocity_scale must be finite and positive")
    theta_1, theta_2, omega_1, omega_2 = np.moveaxis(values, -1, 0)
    return np.stack(
        (
            np.sin(theta_1),
            np.cos(theta_1),
            np.sin(theta_2),
            np.cos(theta_2),
            omega_1 / angular_velocity_scale,
            omega_2 / angular_velocity_scale,
        ),
        axis=-1,
    )


def trajectory_feature(
    trajectories: Array,
    sample_indices: Sequence[int],
    *,
    sample_weights: Sequence[float] | None = None,
    angular_velocity_scale: float = 1.0,
) -> Array:
    """Return a weighted, flattened finite-time observation feature.

    ``trajectories`` has shape ``(time, ..., 4)``.  Weight normalization makes
    the Euclidean feature distance an RMS distance over the declared samples.
    """
    values = _states(trajectories)
    if values.ndim < 2:
        raise ValueError("trajectories must include a time axis")
    declared_indices = tuple(sample_indices)
    if any(
        isinstance(value, (bool, np.bool_))
        or not isinstance(value, (int, np.integer))
        for value in declared_indices
    ):
        raise ValueError("sample_indices must contain integers without truncation")
    indices = np.asarray(declared_indices, dtype=int)
    if indices.ndim != 1 or len(indices) == 0:
        raise ValueError("sample_indices must be a nonempty one-dimensional sequence")
    if np.any(indices < 0) or np.any(indices >= len(values)):
        raise ValueError("a sample index lies outside the trajectory")
    if sample_weights is None:
        weights = np.ones(len(indices), dtype=float)
    else:
        weights = np.asarray(tuple(sample_weights), dtype=float)
        if weights.shape != indices.shape:
            raise ValueError("sample_weights and sample_indices must have equal length")
        if np.any(~np.isfinite(weights)) or np.any(weights < 0) or not np.any(weights > 0):
            raise ValueError("sample weights must be finite, nonnegative, and not all zero")
    weights = weights / np.sum(weights)
    observed = phase_observation(
        values[indices], angular_velocity_scale=angular_velocity_scale
    )
    weighted = observed * np.sqrt(weights).reshape(
        (len(indices),) + (1,) * (observed.ndim - 1)
    )
    # Move ensemble axes ahead of the sampled-observation axes before flattening.
    ensemble_shape = weighted.shape[1:-1]
    permutation = tuple(range(1, weighted.ndim - 1)) + (0, weighted.ndim - 1)
    return np.transpose(weighted, permutation).reshape(ensemble_shape + (-1,))


def first_sampled_full_turn_excursion_indices(trajectories: Array) -> tuple[Array, Array]:
    """Return first samples whose net angular excursion reaches one full turn.

    Angles produced by the dynamics are treated as unwrapped generalized
    coordinates. A value of ``-1`` means no *sampled* displacement of one full
    turn relative to the initial angle occurred. A crossing and return between
    samples is not detected; a dense-output or event enclosure is required for
    a certified rotation-count statement.
    """
    values = _states(trajectories)
    if values.ndim < 2:
        raise ValueError("trajectories must include a time axis")
    angles = np.take(values, (0, 1), axis=-1)
    changes = np.abs(angles - angles[0])
    crossed = changes >= 2.0 * np.pi
    outputs: list[Array] = []
    for arm in range(2):
        mask = crossed[..., arm]
        any_crossing = np.any(mask, axis=0)
        first = np.argmax(mask, axis=0).astype(int)
        outputs.append(np.where(any_crossing, first, -1))
    return outputs[0], outputs[1]


def grid_edge_operational_log_stretch(features: Array, *, side: int) -> Array:
    """Maximum axis-neighbour feature stretch on a periodic square grid.

    The denominator is the geodesic separation ``2*pi/side`` between adjacent
    initial conditions. This is neither a Lyapunov exponent nor the largest
    singular value of the local response Jacobian: oblique directions may be
    more amplified than either sampled grid edge.
    """
    values = np.asarray(features, dtype=float)
    if values.shape[:2] != (side, side) or values.ndim != 3:
        raise ValueError("features must have shape (side, side, feature_dimension)")
    if np.any(~np.isfinite(values)):
        raise ValueError("features must be finite")
    initial_spacing = 2.0 * np.pi / side
    distances = []
    for axis in (0, 1):
        for shift in (-1, 1):
            difference = values - np.roll(values, shift=shift, axis=axis)
            distances.append(np.linalg.norm(difference, axis=-1) / initial_spacing)
    maximum = np.maximum.reduce(distances)
    return np.log(np.maximum(maximum, np.finfo(float).tiny))


def toroidal_connected_components(mask: Array) -> tuple[Array, tuple[int, ...]]:
    """Label four-neighbour components while identifying opposite grid edges."""
    active = np.asarray(mask, dtype=bool)
    if active.ndim != 2 or active.shape[0] != active.shape[1]:
        raise ValueError("mask must be a square two-dimensional array")
    side = active.shape[0]
    labels = np.full(active.shape, -1, dtype=int)
    components: list[list[tuple[int, int]]] = []
    for row in range(side):
        for column in range(side):
            if not active[row, column] or labels[row, column] >= 0:
                continue
            label = len(components)
            stack = [(row, column)]
            labels[row, column] = label
            cells: list[tuple[int, int]] = []
            while stack:
                current = stack.pop()
                cells.append(current)
                r, c = current
                for neighbour in (
                    ((r - 1) % side, c),
                    ((r + 1) % side, c),
                    (r, (c - 1) % side),
                    (r, (c + 1) % side),
                ):
                    if active[neighbour] and labels[neighbour] < 0:
                        labels[neighbour] = label
                        stack.append(neighbour)
            components.append(cells)

    # Relabel by descending size, with the first row-major cell breaking ties.
    order = sorted(
        range(len(components)),
        key=lambda index: (-len(components[index]), min(components[index])),
    )
    relabel = {old: new for new, old in enumerate(order)}
    for cell in zip(*np.nonzero(active)):
        labels[cell] = relabel[int(labels[cell])]
    sizes = tuple(len(components[old]) for old in order)
    return labels, sizes


@dataclass(frozen=True)
class OperationalAtlas:
    """Finite-horizon atlas with every interpretive threshold declared."""

    feature: Array
    log_stretch: Array
    first_sampled_turn_excursion_arm_1: Array
    first_sampled_turn_excursion_arm_2: Array
    low_stretch_no_sampled_full_turn_mask: Array
    component_labels: Array
    component_sizes: tuple[int, ...]
    log_stretch_threshold: float

    def __post_init__(self) -> None:
        feature = np.array(self.feature, dtype=float, copy=True)
        stretch = np.array(self.log_stretch, dtype=float, copy=True)
        turn_1 = np.array(
            self.first_sampled_turn_excursion_arm_1, dtype=int, copy=True
        )
        turn_2 = np.array(
            self.first_sampled_turn_excursion_arm_2, dtype=int, copy=True
        )
        mask = np.array(
            self.low_stretch_no_sampled_full_turn_mask, dtype=bool, copy=True
        )
        labels = np.array(self.component_labels, dtype=int, copy=True)
        if feature.ndim != 3:
            raise ValueError("feature must have shape (side, side, dimension)")
        side = feature.shape[0]
        if feature.shape[1] != side or any(
            values.shape != (side, side)
            for values in (stretch, turn_1, turn_2, mask, labels)
        ):
            raise ValueError("atlas fields must share one square grid")
        if not np.all(np.isfinite(feature)) or not np.all(np.isfinite(stretch)):
            raise ValueError("atlas floating fields must be finite")
        threshold = float(self.log_stretch_threshold)
        if not np.isfinite(threshold):
            raise ValueError("log-stretch threshold must be finite")
        for values in (feature, stretch, turn_1, turn_2, mask, labels):
            values.setflags(write=False)
        object.__setattr__(self, "feature", feature)
        object.__setattr__(self, "log_stretch", stretch)
        object.__setattr__(self, "first_sampled_turn_excursion_arm_1", turn_1)
        object.__setattr__(self, "first_sampled_turn_excursion_arm_2", turn_2)
        object.__setattr__(self, "low_stretch_no_sampled_full_turn_mask", mask)
        object.__setattr__(self, "component_labels", labels)
        object.__setattr__(self, "component_sizes", tuple(int(v) for v in self.component_sizes))
        object.__setattr__(self, "log_stretch_threshold", threshold)

    @property
    def side(self) -> int:
        return int(self.low_stretch_no_sampled_full_turn_mask.shape[0])

    def summary(self) -> dict[str, object]:
        finite = self.log_stretch[np.isfinite(self.log_stretch)]
        return {
            "schema_version": "oig-double-pendulum-operational-atlas-summary-v1",
            "side": self.side,
            "cell_count": self.side * self.side,
            "low_stretch_no_sampled_full_turn_cell_count": int(
                np.count_nonzero(self.low_stretch_no_sampled_full_turn_mask)
            ),
            "low_stretch_no_sampled_full_turn_fraction": float(
                np.mean(self.low_stretch_no_sampled_full_turn_mask)
            ),
            "connected_low_stretch_region_count": len(self.component_sizes),
            "component_sizes": list(self.component_sizes),
            "log_stretch_threshold": float(self.log_stretch_threshold),
            "log_stretch_quantiles": {
                "q10": float(np.quantile(finite, 0.10)),
                "q50": float(np.quantile(finite, 0.50)),
                "q90": float(np.quantile(finite, 0.90)),
            },
            "interpretation_boundary": (
                "The mask means no sampled full-turn excursion and grid-edge operational "
                "log-stretch at or below the declared finite-horizon threshold. It is not "
                "a Lyapunov-stability, synchronization, mutual-indistinguishability, or "
                "rotation-count claim; connected threshold regions need not be equivalence classes."
            ),
        }


def build_operational_atlas(
    trajectories: Array,
    *,
    sample_indices: Iterable[int],
    log_stretch_threshold: float,
    angular_velocity_scale: float = 1.0,
) -> OperationalAtlas:
    """Construct the finite-horizon operational atlas from a square ensemble."""
    values = _states(trajectories)
    if values.ndim != 4 or values.shape[1] != values.shape[2]:
        raise ValueError("trajectories must have shape (time, side, side, 4)")
    if not np.isfinite(log_stretch_threshold):
        raise ValueError("log_stretch_threshold must be finite")
    side = values.shape[1]
    feature = trajectory_feature(
        values,
        tuple(sample_indices),
        angular_velocity_scale=angular_velocity_scale,
    )
    stretch = grid_edge_operational_log_stretch(feature, side=side)
    first_1, first_2 = first_sampled_full_turn_excursion_indices(values)
    low_stretch_no_sampled_full_turn = (
        (stretch <= log_stretch_threshold) & (first_1 < 0) & (first_2 < 0)
    )
    labels, sizes = toroidal_connected_components(low_stretch_no_sampled_full_turn)
    return OperationalAtlas(
        feature=feature,
        log_stretch=stretch,
        first_sampled_turn_excursion_arm_1=first_1,
        first_sampled_turn_excursion_arm_2=first_2,
        low_stretch_no_sampled_full_turn_mask=low_stretch_no_sampled_full_turn,
        component_labels=labels,
        component_sizes=sizes,
        log_stretch_threshold=float(log_stretch_threshold),
    )


__all__ = [
    "OperationalAtlas",
    "build_operational_atlas",
    "cell_centred_torus_grid",
    "first_sampled_full_turn_excursion_indices",
    "grid_edge_operational_log_stretch",
    "phase_observation",
    "torus_angle_distance",
    "toroidal_connected_components",
    "trajectory_feature",
    "wrap_angle",
]
