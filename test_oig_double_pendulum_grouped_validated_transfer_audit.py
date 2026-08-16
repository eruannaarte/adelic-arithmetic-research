"""Hostile independent audit of the grouped outward shared-clock transfer.

The production verifier is intentionally not used as the primary algebraic
oracle here.  This module reconstructs interval Grams and Schur complements
with a separate exact interval type, checks the claimed floor through a direct
two-by-two uniform LDL inequality, exercises a different exact time partition,
and contrasts global, group-refit, and scalar-refit clock semantics.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
import json
from pathlib import Path
import unittest

from flint import arb, ctx
import numpy as np

import oig_double_pendulum_grouped_validated_transfer as production
from oig_double_pendulum_protocol import canonical_protocol_candidates
import oig_double_pendulum_validated_transfer as validated


Q = Fraction
AUDIT_FLOOR = Q(180269, 10_000_000)
FALSE_HIGH_FLOOR = Q(18027, 1_000_000)


@dataclass(frozen=True)
class AuditInterval:
    """Small exact closed interval implementation independent of production."""

    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if type(self.lower) is not Fraction or type(self.upper) is not Fraction:
            raise TypeError("audit interval endpoints must be exact Fractions")
        if self.lower > self.upper:
            raise ValueError("audit interval endpoints are reversed")

    @classmethod
    def point(cls, value: Fraction) -> "AuditInterval":
        return cls(value, value)

    @classmethod
    def record(cls, value: object) -> "AuditInterval":
        if not isinstance(value, dict) or set(value) != {"lower_exact", "upper_exact"}:
            raise ValueError("malformed interval record")
        return cls(Q(value["lower_exact"]), Q(value["upper_exact"]))

    @property
    def midpoint(self) -> Fraction:
        return (self.lower + self.upper) / 2

    def __add__(self, other: "AuditInterval") -> "AuditInterval":
        return AuditInterval(self.lower + other.lower, self.upper + other.upper)

    def __neg__(self) -> "AuditInterval":
        return AuditInterval(-self.upper, -self.lower)

    def __sub__(self, other: "AuditInterval") -> "AuditInterval":
        return self + (-other)

    def __mul__(self, other: "AuditInterval") -> "AuditInterval":
        products = (
            self.lower * other.lower,
            self.lower * other.upper,
            self.upper * other.lower,
            self.upper * other.upper,
        )
        return AuditInterval(min(products), max(products))

    def scale(self, value: Fraction) -> "AuditInterval":
        if value >= 0:
            return AuditInterval(value * self.lower, value * self.upper)
        return AuditInterval(value * self.upper, value * self.lower)

    def divide_positive(self, other: "AuditInterval") -> "AuditInterval":
        if other.lower <= 0:
            raise ArithmeticError("audit refuses a denominator not bounded away from zero")
        return self * AuditInterval(1 / other.upper, 1 / other.lower)


def _zero() -> AuditInterval:
    return AuditInterval.point(Q(0))


def _observation_rows(
    report: dict[str, object],
) -> tuple[tuple[AuditInterval, AuditInterval, AuditInterval], ...]:
    rows = []
    for observation in report["observations"]:  # type: ignore[index]
        joint = observation["joint_augmented_row_outer_box_exact"]
        if joint["coordinates"] != list(production.AUGMENTED_COORDINATES):
            raise AssertionError("audit found an augmented-coordinate permutation")
        rows.append(tuple(AuditInterval.record(value) for value in joint["entries"]))
    return tuple(rows)  # type: ignore[return-value]


def _weights(report: dict[str, object]) -> tuple[Fraction, ...]:
    return tuple(
        Q(observation["physical_scalar_weight_exact"])
        for observation in report["observations"]  # type: ignore[index]
    )


def _interval_gram(
    rows: tuple[tuple[AuditInterval, AuditInterval, AuditInterval], ...],
    weights: tuple[Fraction, ...],
) -> tuple[tuple[AuditInterval, ...], ...]:
    result = [[_zero() for _ in range(3)] for _ in range(3)]
    for row, weight in zip(rows, weights):
        for left in range(3):
            for right in range(3):
                result[left][right] = result[left][right] + (
                    row[left] * row[right]
                ).scale(weight)
    return tuple(tuple(row) for row in result)


def _profile(
    gram: tuple[tuple[AuditInterval, ...], ...],
) -> tuple[tuple[AuditInterval, AuditInterval], ...]:
    denominator = gram[0][0]
    if denominator.lower <= 0:
        raise ArithmeticError("shared-clock denominator is not proved positive")
    correction_uu = (gram[0][1] * gram[0][1]).divide_positive(denominator)
    correction_uv = (gram[0][1] * gram[0][2]).divide_positive(denominator)
    correction_vv = (gram[0][2] * gram[0][2]).divide_positive(denominator)
    return (
        (gram[1][1] - correction_uu, gram[1][2] - correction_uv),
        (gram[1][2] - correction_uv, gram[2][2] - correction_vv),
    )


def _uniform_two_by_two_ldl(
    profile: tuple[tuple[AuditInterval, AuditInterval], ...],
    floor: Fraction,
) -> bool:
    first = profile[0][0].lower - floor
    second = profile[1][1].lower - floor
    off_diagonal_magnitude = max(
        abs(profile[0][1].lower), abs(profile[0][1].upper)
    )
    return bool(
        first > 0
        and second > 0
        and first * second > off_diagonal_magnitude * off_diagonal_magnitude
    )


def _interval_matrix_records(
    matrix: tuple[tuple[AuditInterval, ...], ...]
) -> list[list[dict[str, str]]]:
    return [
        [
            {
                "lower_exact": f"{entry.lower.numerator}/{entry.lower.denominator}",
                "upper_exact": f"{entry.upper.numerator}/{entry.upper.denominator}",
            }
            for entry in row
        ]
        for row in matrix
    ]


def _midpoint_point_gram(
    rows: tuple[tuple[AuditInterval, AuditInterval, AuditInterval], ...],
    weights: tuple[Fraction, ...],
) -> tuple[tuple[Fraction, ...], ...]:
    result = [[Q(0) for _ in range(3)] for _ in range(3)]
    for row, weight in zip(rows, weights):
        point = tuple(entry.midpoint for entry in row)
        for left in range(3):
            for right in range(3):
                result[left][right] += weight * point[left] * point[right]
    return tuple(tuple(row) for row in result)


def _point_profile(
    gram: tuple[tuple[Fraction, ...], ...]
) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    denominator = gram[0][0]
    if denominator <= 0:
        raise ArithmeticError("point clock denominator is nonpositive")
    return (
        (
            gram[1][1] - gram[0][1] * gram[0][1] / denominator,
            gram[1][2] - gram[0][1] * gram[0][2] / denominator,
        ),
        (
            gram[1][2] - gram[0][1] * gram[0][2] / denominator,
            gram[2][2] - gram[0][2] * gram[0][2] / denominator,
        ),
    )


def _floating_floor(
    rows: tuple[tuple[AuditInterval, AuditInterval, AuditInterval], ...],
    weights: tuple[Fraction, ...],
    nuisance_partition: str,
) -> float:
    point = np.asarray(
        [[float(entry.midpoint) for entry in row] for row in rows], dtype=float
    )
    clock = point[:, :1]
    response = point[:, 1:]
    metric = np.diag([float(value) for value in weights])
    if nuisance_partition == "global":
        nuisance = clock
    elif nuisance_partition == "by_group":
        nuisance = np.zeros((5, 2), dtype=float)
        nuisance[:3, 0] = clock[:3, 0]
        nuisance[3:, 1] = clock[3:, 0]
    elif nuisance_partition == "by_scalar":
        nuisance = np.eye(5)
    else:
        raise ValueError("unknown nuisance partition")
    moment = nuisance.T @ metric @ nuisance
    projector = np.eye(5) - nuisance @ np.linalg.inv(moment) @ nuisance.T @ metric
    information = response.T @ metric @ projector @ response
    information = 0.5 * (information + information.T)
    return float(np.linalg.eigvalsh(information)[0])


def _overlap(left: AuditInterval, right: AuditInterval) -> bool:
    return max(left.lower, right.lower) < min(left.upper, right.upper)


class GroupedValidatedTransferHostileAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = production.build_grouped_physical_clock_floor_certificate()
        cls.rows = _observation_rows(cls.report)
        cls.weights = _weights(cls.report)
        cls.gram = _interval_gram(cls.rows, cls.weights)
        cls.profile = _profile(cls.gram)

        cls.alternate_config = validated.ValidatedTransferConfig(
            precision_bits=192,
            taylor_order=9,
            step_size=Q(1, 125),
        )
        cls.alternate_trajectories = {}
        for selected in production.selected_observations():
            candidate = selected.candidate
            key = (candidate.launch, candidate.observation_time_tau)
            if key not in cls.alternate_trajectories:
                cls.alternate_trajectories[key] = validated.validated_augmented_trajectory(
                    candidate.launch,
                    candidate.observation_time_tau,
                    cls.alternate_config,
                )

    def test_independent_interval_gram_and_profile_match_serialization(self) -> None:
        serialized = self.report["exact_rational_interval_profile"]
        self.assertEqual(
            _interval_matrix_records(self.gram),
            serialized["augmented_gram_outer_interval_exact"],
        )
        self.assertEqual(
            _interval_matrix_records(self.profile),
            serialized["clock_profiled_information_outer_interval_exact"],
        )
        self.assertGreater(self.gram[0][0].lower, Q(3, 2))

    def test_direct_uniform_two_by_two_ldl_proves_claimed_floor(self) -> None:
        # This is a different proof path from production's sequential 3x3
        # interval LDL: first form a full interval Schur complement, then use
        # a worst-case exact 2x2 determinant inequality.
        self.assertTrue(_uniform_two_by_two_ldl(self.profile, AUDIT_FLOOR))
        self.assertEqual(AUDIT_FLOOR, production.SHARP_FLOOR)

        # The slightly larger value is genuinely false even at the Cartesian
        # box midpoint, so the audit has a nearby rejecting control rather
        # than merely checking that some positive number passes.
        point_profile = _point_profile(_midpoint_point_gram(self.rows, self.weights))
        shifted_first = point_profile[0][0] - FALSE_HIGH_FLOOR
        shifted_second = point_profile[1][1] - FALSE_HIGH_FLOOR
        shifted_determinant = (
            shifted_first * shifted_second - point_profile[0][1] ** 2
        )
        self.assertLess(shifted_determinant, 0)
        self.assertFalse(_uniform_two_by_two_ldl(self.profile, FALSE_HIGH_FLOOR))

    def test_cost_scaling_and_zero_share_incidence_are_exact(self) -> None:
        self.assertEqual(
            self.weights,
            (Q(4, 21), Q(4, 21), Q(4, 21), Q(4, 27), Q(4, 27)),
        )
        self.assertEqual(sum(self.weights, Q(0)), Q(164, 189))
        names = [row["name"] for row in self.report["observations"]]
        self.assertEqual(
            names,
            [candidate.name for candidate in canonical_protocol_candidates()[:5]],
        )
        self.assertTrue(all("launch-C" not in name for name in names))
        groups = self.report["fixed_grouped_mixture"]["groups"]
        self.assertEqual(groups[2]["budget_share_exact"], "0/1")
        self.assertIs(groups[2]["active"], False)

        correct = _floating_floor(self.rows, self.weights, "global")
        wrong_weights = (Q(2, 3),) * 3 + (Q(1, 3),) * 2
        incorrectly_unscaled = _floating_floor(self.rows, wrong_weights, "global")
        self.assertAlmostEqual(correct, 0.01802692111, places=10)
        self.assertGreater(abs(incorrectly_unscaled - correct), 0.03)

    def test_shared_group_refit_and_scalar_refit_are_distinct_models(self) -> None:
        shared = _floating_floor(self.rows, self.weights, "global")
        group_refit = _floating_floor(self.rows, self.weights, "by_group")
        scalar_refit = _floating_floor(self.rows, self.weights, "by_scalar")
        self.assertAlmostEqual(shared, 0.01802692111, places=10)
        self.assertAlmostEqual(group_refit, 0.00898593, places=7)
        self.assertLess(group_refit, shared)
        self.assertAlmostEqual(scalar_refit, 0.0, places=13)
        self.assertIn(
            "one column is shared across every repetition",
            self.report["shared_clock_nuisance"]["scope"],
        )

    def test_denominator_zero_and_nearby_false_floor_fail_closed(self) -> None:
        hostile_rows = tuple(
            (
                AuditInterval(Q(-1), Q(1)),
                row[1],
                row[2],
            )
            for row in self.rows
        )
        hostile_gram = _interval_gram(hostile_rows, self.weights)
        self.assertLessEqual(hostile_gram[0][0].lower, 0)
        with self.assertRaises(ArithmeticError):
            _profile(hostile_gram)

        forged = deepcopy(self.report)
        for observation in forged["observations"]:
            observation["joint_augmented_row_outer_box_exact"]["entries"][0] = {
                "lower_exact": "-1/1",
                "upper_exact": "1/1",
            }
        verification = production.verify_grouped_physical_clock_floor_certificate(forged)
        self.assertIs(verification["passed"], False)

    def test_alternate_exact_partition_overlaps_every_H_and_clock_box(self) -> None:
        expected_steps = [125, 125, 188, 94, 157]
        selected = production.selected_observations()
        for index, (declared, observation) in enumerate(
            zip(selected, self.report["observations"])
        ):
            candidate = declared.candidate
            trajectory = self.alternate_trajectories[
                (candidate.launch, candidate.observation_time_tau)
            ]
            self.assertEqual(trajectory.step_count, expected_steps[index])
            sensor_index = observation["sensor_state_index"]
            with ctx.workprec(self.alternate_config.precision_bits):
                rhs = validated.augmented_rhs(trajectory.terminal)
                if sensor_index in (0, 1):
                    self.assertTrue(
                        (rhs[sensor_index] - trajectory.terminal[2 + sensor_index]).contains(0)
                    )
                clock = (
                    validated._arb_fraction(candidate.observation_time_tau)
                    * rhs[sensor_index]
                )
                alternate_values = (
                    clock,
                    trajectory.terminal[4 + sensor_index],
                    trajectory.terminal[8 + sensor_index],
                )
                alternate_boxes = []
                for value in alternate_values:
                    lower, upper = validated._rational_outer_interval(value, 10**18)
                    alternate_boxes.append(AuditInterval(lower, upper))
            production_boxes = tuple(
                AuditInterval.record(value)
                for value in observation["joint_augmented_row_outer_box_exact"]["entries"]
            )
            for production_box, alternate_box in zip(
                production_boxes, alternate_boxes
            ):
                self.assertTrue(_overlap(production_box, alternate_box))

    def test_scope_is_local_per_model_and_does_not_absorb_other_uncertainty(self) -> None:
        flags = self.report["scope_flags"]
        self.assertIs(flags["exact_launch_preparation_assumed"], True)
        for name in (
            "launch_preparation_error_bounded",
            "finite_clock_dilation_amplitude_certified",
            "parameter_neighborhood_uniformity_certified",
            "candidate_selection_transfer_certified",
            "finite_grid_optimality_certified",
            "empirical_model_adequacy_certified",
            "hardware_calibration_certified",
        ):
            self.assertIs(flags[name], False)
        self.assertEqual(self.report["source_model"]["base_point_exact"], ["0/1", "0/1"])
        self.assertIn("profiles one local unrestricted shared log-clock", self.report["scope_boundary"])

    def test_canonical_artifact_strictly_verifies_when_present(self) -> None:
        path = (
            Path(__file__).resolve().parent
            / "artifacts"
            / "double_pendulum_grouped_physical_clock_floor.json"
        )
        if not path.is_file():
            self.skipTest("production artifact is still being finalized")
        committed = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(committed, self.report)
        self.assertTrue(
            production.verify_grouped_physical_clock_floor_certificate(committed)[
                "passed"
            ]
        )


if __name__ == "__main__":
    unittest.main()
