"""Independent hostile controls for the validated pendulum transfer lane.

These tests intentionally exercise the proof through routes that differ from
the production artifact test: independent analytic sensitivity equations,
alternate exact time partitions and Taylor orders, an explicit reconstruction
of the Picard gate after interval wrapping, and direct exact arithmetic on the
composed two-row information certificate.
"""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import unittest

from flint import arb, ctx
import numpy as np

from oig_double_pendulum_parameter_sensitivity import (
    dimensionless_rhs,
    dimensionless_rhs_log_ratio_jacobian,
    dimensionless_rhs_state_jacobian,
)
import oig_double_pendulum_validated_transfer as validated


Q = Fraction


def _record_interval(record: dict[str, object]) -> tuple[Fraction, Fraction]:
    return Q(record["lower_exact"]), Q(record["upper_exact"])


def _information_from_report(
    report: dict[str, object],
) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    result = [[Q(0), Q(0)], [Q(0), Q(0)]]
    for row in report["protocols"]:  # type: ignore[index]
        weight = Q(row["physical_weight_exact"])
        response = tuple(Q(value) for value in row["response_exact"][0])
        for i in range(2):
            for j in range(2):
                result[i][j] += weight * response[i] * response[j]
    return (tuple(result[0]), tuple(result[1]))  # type: ignore[return-value]


class ValidatedTransferEquationAudit(unittest.TestCase):
    def test_augmented_blocks_match_independent_analytic_equations(self) -> None:
        # Nonzero sensitivities are important here: this checks the homogeneous
        # D_z F S term as well as the inhomogeneous D_(u,v) F forcing and the
        # production module's block ordering.
        cases = (
            (
                (0.37, -0.81, 1.14, -0.42),
                (0.21, -0.33, 0.57, 0.19),
                (-0.72, 0.11, 0.04, 0.83),
            ),
            (
                (-1.22, 0.64, -0.73, 1.51),
                (1.03, 0.17, -0.28, 0.61),
                (0.39, -0.92, 0.75, -0.16),
            ),
            (
                (2.01, -1.77, 2.25, -1.94),
                (-0.44, 0.68, 1.21, -0.37),
                (0.52, 0.31, -0.89, 1.08),
            ),
        )
        with ctx.workprec(220):
            for state, sensitivity_u, sensitivity_v in cases:
                values = tuple(
                    arb(str(value))
                    for value in state + sensitivity_u + sensitivity_v
                )
                observed = np.asarray(
                    [float(value.mid()) for value in validated.augmented_rhs(values)]
                )
                z = np.asarray(state)
                su = np.asarray(sensitivity_u)
                sv = np.asarray(sensitivity_v)
                base = dimensionless_rhs(0.0, z, 0.0, 0.0)
                state_jacobian = dimensionless_rhs_state_jacobian(
                    0.0, z, 0.0, 0.0
                )
                source_jacobian = dimensionless_rhs_log_ratio_jacobian(
                    0.0, z, 0.0, 0.0
                )
                expected = np.concatenate(
                    (
                        base,
                        state_jacobian @ su + source_jacobian[:, 0],
                        state_jacobian @ sv + source_jacobian[:, 1],
                    )
                )
                self.assertLess(float(np.max(np.abs(observed - expected))), 3e-13)

    def test_response_indices_have_the_declared_source_and_sensor_order(self) -> None:
        first, second = validated.active_protocol_targets()
        self.assertEqual(first.response_indices(), (5, 9))
        self.assertEqual(second.response_indices(), (6, 10))
        self.assertEqual(
            validated.SOURCE_COORDINATES,
            (
                "log_mass_ratio=log(m2/m1)",
                "log_length_ratio=log(l2/l1)",
            ),
        )


class ValidatedTransferPicardAudit(unittest.TestCase):
    @staticmethod
    def _wrapped_initial(step_count: int) -> tuple[arb, ...]:
        config = validated.ValidatedTransferConfig()
        target = validated.active_protocol_targets()[1]
        current = tuple(
            [validated._arb_fraction(value) for value in target.launch]
            + [arb(0)] * 8
        )
        for _ in range(step_count):
            current = validated._validated_step(
                current, config.step_size, config
            ).endpoint
        return current

    def test_picard_gate_and_endpoint_radius_after_wrapping(self) -> None:
        config = validated.ValidatedTransferConfig()
        with ctx.workprec(config.precision_bits):
            initial = self._wrapped_initial(60)
            h = validated._arb_fraction(config.step_size)
            midpoint = [value.mid() for value in initial]
            polynomials = validated._taylor_polynomial(
                midpoint, config.taylor_order
            )
            at_zero = [
                validated._polynomial_value(row, arb(0))
                for row in polynomials
            ]
            at_end = [
                validated._polynomial_value(row, h) for row in polynomials
            ]
            time_interval = arb(h / 2, (h / 2).abs_upper())
            polynomial_ranges = [
                validated._polynomial_value(row, time_interval)
                for row in polynomials
            ]
            residual = validated._residual_bounds(polynomials, h)
            base = [
                (
                    validated._magnitude(value - polynomial)
                    + h * defect
                ).abs_upper()
                for value, polynomial, defect in zip(
                    initial, at_zero, residual
                )
            ]
            inflation = validated._arb_fraction(config.tube_inflation)
            tiny = arb(
                0,
                arb(f"1e-{max(20, config.precision_bits // 4)}"),
            )
            rho = [
                (inflation * bound + tiny.rad()).abs_upper()
                for bound in base
            ]
            accepted_target: list[arb] | None = None
            accepted_iteration = 0
            for iteration in range(
                1, config.maximum_tube_iterations + 1
            ):
                tube = [
                    arb(value.mid(), value.rad() + radius.abs_upper())
                    for value, radius in zip(polynomial_ranges, rho)
                ]
                jacobian = validated._box_jacobian_magnitudes(tube)
                target = [
                    (
                        bound
                        + h
                        * sum(
                            (
                                entry * radius
                                for entry, radius in zip(row, rho)
                            ),
                            arb(0),
                        )
                    ).abs_upper()
                    for bound, row in zip(base, jacobian)
                ]
                if all(
                    validated._strictly_dominates(radius, needed)
                    for radius, needed in zip(rho, target)
                ):
                    accepted_target = target
                    accepted_iteration = iteration
                    break
                rho = [
                    (
                        inflation
                        * (needed if radius < needed else radius)
                    ).abs_upper()
                    for radius, needed in zip(rho, target)
                ]

            self.assertIsNotNone(accepted_target)
            production = validated._validated_step(
                initial, config.step_size, config
            )
            self.assertEqual(
                production.tube_iterations, accepted_iteration
            )
            assert accepted_target is not None
            for endpoint, polynomial, error in zip(
                production.endpoint, at_end, accepted_target
            ):
                required = arb(
                    polynomial.mid(), polynomial.rad() + error.abs_upper()
                )
                self.assertTrue(endpoint.contains(required))

            # A deliberately quarter-sized tube must not pass the same gate.
            # This is a negative control against accidentally omitting the
            # initial/defect term or reversing the containment comparison.
            shrunken = [radius / 4 for radius in rho]
            shrunken_tube = [
                arb(value.mid(), value.rad() + radius.abs_upper())
                for value, radius in zip(polynomial_ranges, shrunken)
            ]
            shrunken_jacobian = validated._box_jacobian_magnitudes(
                shrunken_tube
            )
            shrunken_target = [
                (
                    bound
                    + h
                    * sum(
                        (
                            entry * radius
                            for entry, radius in zip(row, shrunken)
                        ),
                        arb(0),
                    )
                ).abs_upper()
                for bound, row in zip(base, shrunken_jacobian)
            ]
            self.assertFalse(
                all(
                    validated._strictly_dominates(radius, needed)
                    for radius, needed in zip(shrunken, shrunken_target)
                )
            )

    def test_wrapped_step_taylor_remainder_contains_dense_samples(self) -> None:
        config = validated.ValidatedTransferConfig()
        with ctx.workprec(config.precision_bits):
            initial = self._wrapped_initial(60)
            polynomials = validated._taylor_polynomial(
                [value.mid() for value in initial], config.taylor_order
            )
            h = validated._arb_fraction(config.step_size)
            bounds = validated._residual_bounds(polynomials, h)

        # Sampling is only a hostile regression control; the theorem is the
        # interval Taylor remainder used above.  Higher precision keeps the
        # sampler's own rounding balls below the certified defect bounds.
        with ctx.workprec(400):
            for numerator in range(17):
                time = config.step_size * Q(numerator, 16)
                argument = validated._arb_fraction(time)
                values = [
                    validated._polynomial_value(row, argument)
                    for row in polynomials
                ]
                derivatives = [
                    validated._polynomial_value(
                        [
                            degree * coefficient
                            for degree, coefficient in enumerate(row)
                        ][1:],
                        argument,
                    )
                    for row in polynomials
                ]
                residual = [
                    derivative - rhs
                    for derivative, rhs in zip(
                        derivatives, validated.augmented_rhs(values)
                    )
                ]
                for bound, sample in zip(bounds, residual):
                    if bound == 0:
                        self.assertTrue(sample.contains(0))
                    else:
                        self.assertTrue(-bound < sample and sample < bound)


class ValidatedTransferPartitionAndCompositionAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.default = validated.build_physical_positive_floor_certificate()
        cls.finer = validated.build_validated_transfer_report(
            validated.ValidatedTransferConfig(
                precision_bits=192,
                taylor_order=8,
                step_size=Q(1, 125),
            )
        )
        cls.higher_order = validated.build_validated_transfer_report(
            validated.ValidatedTransferConfig(
                precision_bits=192,
                taylor_order=9,
                step_size=Q(1, 80),
            )
        )

    def test_independent_exact_partitions_prove_overlapping_enclosures(self) -> None:
        baseline = self.default["validated_transfer"]
        reports = (baseline, self.finer, self.higher_order)
        self.assertEqual(
            [row["validated_step_count"] for row in reports[0]["protocols"]],
            [100, 125],
        )
        self.assertEqual(
            [row["validated_step_count"] for row in reports[1]["protocols"]],
            [125, 157],
        )
        self.assertEqual(
            [row["validated_step_count"] for row in reports[2]["protocols"]],
            [80, 100],
        )
        for report in reports:
            self.assertEqual(report["status"], "proved")
        for protocol_index in range(2):
            for source_index in range(2):
                intervals = [
                    _record_interval(
                        report["protocols"][protocol_index][
                            "response_enclosure"
                        ][source_index]
                    )
                    for report in reports
                ]
                self.assertLess(
                    max(lower for lower, _ in intervals),
                    min(upper for _, upper in intervals),
                )

    def test_serialized_outer_hulls_are_strictly_inside_declared_boxes(self) -> None:
        transfer = self.default["validated_transfer"]
        targets = validated.active_protocol_targets()
        for row, target in zip(transfer["protocols"], targets):
            for enclosure, centre, radius in zip(
                row["response_enclosure"],
                target.declared_centre,
                target.declared_radius,
            ):
                lower, upper = _record_interval(enclosure)
                self.assertLess(centre - radius, lower)
                self.assertLess(lower, upper)
                self.assertLess(upper, centre + radius)

        with ctx.workprec(160):
            self.assertFalse(
                validated._strict_ball_subset_of_rational_interval(
                    arb(1), Q(1), Q(2)
                )
            )
            self.assertTrue(
                validated._strict_ball_subset_of_rational_interval(
                    arb("3/2"), Q(1), Q(2)
                )
            )

    def test_exact_two_row_composition_has_a_positive_ldl_margin(self) -> None:
        child = self.default["exact_active_enclosed_design"]
        robustness = child["response_box_robustness"]
        nominal_floor = Q(robustness["nominal_floor_lower_exact"])
        aggregate_error = Q(
            robustness[
                "aggregate_metric_relative_information_error_upper_exact"
            ]
        )
        robust_floor = Q(robustness["robust_physical_floor_lower_exact"])
        self.assertEqual(robust_floor, nominal_floor - aggregate_error)
        self.assertGreater(robust_floor, 0)

        shares = [Q(row["budget_share_exact"]) for row in child["protocols"]]
        self.assertEqual(sum(shares, Q(0)), Q(1))
        for row in child["protocols"]:
            self.assertEqual(
                Q(row["physical_weight_exact"]),
                Q(row["budget_share_exact"]) / Q(row["cost_exact"]),
            )

        information = _information_from_report(child)
        shifted00 = information[0][0] - nominal_floor
        shifted11 = information[1][1] - nominal_floor
        determinant = shifted00 * shifted11 - information[0][1] ** 2
        self.assertGreater(shifted00, 0)
        self.assertGreater(determinant, 0)
        self.assertEqual(
            self.default["robust_physical_floor_lower_exact"],
            validated._fraction_text(robust_floor),
        )

    def test_scope_promotion_and_transfer_tampering_fail_closed(self) -> None:
        forged = deepcopy(self.default)
        forged["scope_flags"]["seven_candidate_selection_certified"] = True
        self.assertIs(
            validated.verify_physical_positive_floor_certificate(forged)[
                "passed"
            ],
            False,
        )

        forged = deepcopy(self.default)
        forged["validated_transfer"]["protocols"][0][
            "declared_response_radius_exact"
        ][0] = "1/1"
        self.assertIs(
            validated.verify_physical_positive_floor_certificate(forged)[
                "passed"
            ],
            False,
        )


if __name__ == "__main__":
    unittest.main()
