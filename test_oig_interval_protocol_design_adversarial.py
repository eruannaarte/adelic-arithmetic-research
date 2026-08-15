"""Adversarial controls for the interval protocol-design wrapper.

These tests focus on report composition: the exact nominal certificate, every
response-box certificate, and the robust-noise consequences must describe one
and the same physical protocol family.
"""

from copy import deepcopy
from fractions import Fraction
import itertools
import unittest

from oig_interval_protocol_design import (
    EnclosedProtocol,
    design_enclosed_protocols,
    response_box_form_bound,
    verify_enclosed_design_report,
)


class IntervalProtocolDesignAdversarialTests(unittest.TestCase):
    @staticmethod
    def _exact_two_axis_report() -> dict[str, object]:
        protocols = (
            EnclosedProtocol.from_rows("first", [[1, 0]], [[0, 0]], [[1]]),
            EnclosedProtocol.from_rows("second", [[0, 1]], [[0, 0]], [[1]]),
        )
        return design_enclosed_protocols(
            protocols,
            [[1, 0], [0, 1]],
            weight_denominator=10_000,
            exposure_multiplier=10,
        )

    def test_entrywise_bound_survives_correlated_precision_and_general_metric(self) -> None:
        protocol = EnclosedProtocol.from_rows(
            "correlated",
            [[1, -2], [3, 1]],
            [[Fraction(1, 10), Fraction(1, 20)], [Fraction(1, 25), Fraction(1, 10)]],
            [[2, -1], [-1, 2]],
        )
        metric = ((Fraction(2), Fraction(1, 2)), (Fraction(1, 2), Fraction(1)))
        record = response_box_form_bound(protocol, metric)
        delta = Fraction(record["metric_relative_information_error_upper_exact"])

        # Convexity is not needed here: this is a direct exact check at all
        # response-box corners and several integer test directions.
        radii = tuple(value for row in protocol.response_radius for value in row)
        centre = tuple(value for row in protocol.response_centre for value in row)
        directions = (
            (Fraction(1), Fraction(0)),
            (Fraction(0), Fraction(1)),
            (Fraction(1), Fraction(1)),
            (Fraction(2), Fraction(-3)),
        )
        w = protocol.noise_precision
        for signs in itertools.product((-1, 1), repeat=4):
            flat = tuple(c + sign * radius for c, sign, radius in zip(centre, signs, radii))
            response = (flat[:2], flat[2:])
            for x in directions:
                nominal_output = tuple(
                    sum(protocol.response_centre[row][column] * x[column] for column in range(2))
                    for row in range(2)
                )
                true_output = tuple(
                    sum(response[row][column] * x[column] for column in range(2))
                    for row in range(2)
                )

                def energy(output: tuple[Fraction, ...]) -> Fraction:
                    return sum(
                        output[row] * w[row][column] * output[column]
                        for row in range(2)
                        for column in range(2)
                    )

                metric_energy = sum(
                    x[row] * metric[row][column] * x[column]
                    for row in range(2)
                    for column in range(2)
                )
                self.assertLess(
                    abs(energy(true_output) - energy(nominal_output)),
                    delta * metric_energy,
                )

    def test_cost_weighted_box_aggregation_reproduces_exactly(self) -> None:
        protocols = (
            EnclosedProtocol.from_rows(
                "cheap-x", [[1, 0]], [[Fraction(1, 1000), 0]], [[1]], cost=1
            ),
            EnclosedProtocol.from_rows(
                "expensive-y", [[0, 2]], [[0, Fraction(1, 500)]], [[1]], cost=3
            ),
        )
        report = design_enclosed_protocols(
            protocols,
            [[2, Fraction(1, 3)], [Fraction(1, 3), 1]],
            weight_denominator=20_000,
        )
        robust = report["response_box_robustness"]
        expected = sum(
            Fraction(row["budget_share_exact"])
            * Fraction(bound["metric_relative_information_error_upper_exact"])
            / Fraction(row["cost_exact"])
            for row, bound in zip(
                report["protocols"], robust["protocol_response_box_certificates"]
            )
        )
        self.assertEqual(
            Fraction(robust["aggregate_metric_relative_information_error_upper_exact"]),
            expected,
        )
        self.assertTrue(verify_enclosed_design_report(report)["passed"])

    def test_verifier_rejects_enclosure_centre_unlinked_from_nominal_protocol(self) -> None:
        report = self._exact_two_axis_report()
        tampered = deepcopy(report)
        zero_centre = EnclosedProtocol.from_rows(
            "first", [[0, 0]], [[0, 0]], [[1]]
        )
        tampered["response_box_robustness"][
            "protocol_response_box_certificates"
        ][0] = response_box_form_bound(zero_centre, [[1, 0], [0, 1]])

        # The declared physical family is now blind in the first direction,
        # while the retained nominal certificate asserts a positive floor.
        self.assertFalse(verify_enclosed_design_report(tampered)["passed"])

    def test_verifier_rejects_enclosure_precision_unlinked_from_nominal_protocol(self) -> None:
        report = self._exact_two_axis_report()
        tampered = deepcopy(report)
        weaker_precision = EnclosedProtocol.from_rows(
            "first", [[1, 0]], [[0, 0]], [[Fraction(1, 100)]]
        )
        tampered["response_box_robustness"][
            "protocol_response_box_certificates"
        ][0] = response_box_form_bound(weaker_precision, [[1, 0], [0, 1]])
        self.assertFalse(verify_enclosed_design_report(tampered)["passed"])

    def test_verifier_checks_each_box_schema_and_exact_decision_flag(self) -> None:
        report = self._exact_two_axis_report()
        for field, value in (
            ("schema_version", "unknown-response-box-schema"),
            ("exact_ldl_decision", False),
        ):
            with self.subTest(field=field):
                tampered = deepcopy(report)
                tampered["response_box_robustness"][
                    "protocol_response_box_certificates"
                ][0][field] = value
                self.assertFalse(verify_enclosed_design_report(tampered)["passed"])

    def test_verifier_reconstructs_and_requires_positive_floor_noise_block(self) -> None:
        report = self._exact_two_axis_report()
        robust = report["response_box_robustness"]
        self.assertTrue(robust["robust_floor_is_positive"])

        mutations = []
        missing = deepcopy(report)
        del missing["response_box_robustness"]["robust_noise_performance"]
        mutations.append(missing)

        wrong_error = deepcopy(report)
        wrong_error["response_box_robustness"]["robust_noise_performance"][
            "continuous_exposure_gaussian_error_rational_upper_exact"
        ] = "0/1"
        mutations.append(wrong_error)

        wrong_amplitude = deepcopy(report)
        wrong_amplitude["response_box_robustness"]["robust_noise_performance"][
            "amplitude_exact"
        ] = "100/1"
        mutations.append(wrong_amplitude)

        wrong_exposure = deepcopy(report)
        wrong_exposure["response_box_robustness"]["robust_noise_performance"][
            "integer_realization_exposure"
        ] += 1
        mutations.append(wrong_exposure)

        for index, tampered in enumerate(mutations):
            with self.subTest(mutation=index):
                self.assertFalse(verify_enclosed_design_report(tampered)["passed"])


if __name__ == "__main__":
    unittest.main()
