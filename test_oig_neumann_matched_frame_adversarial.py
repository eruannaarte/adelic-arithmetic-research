"""Independent adversarial controls for the Neumann matched-frame certificate.

These tests concentrate on identities that are easy to obscure in a large
JSON artifact: the finite-Gram normalization, the induced noise covariance,
the absolute-value step in the second-order loss estimate, and top-level
tamper detection.
"""

from copy import deepcopy
from fractions import Fraction
import unittest

from flint import arb, ctx

import oig_neumann_matched_frame as matched_module
from oig_neumann_matched_frame import (
    _second_order_frame_loss_bound,
    finite_modal_response_box,
    run_matched_frame_certificate,
)
from oig_protocol_design_engine import (
    _inverse,
    _matmul,
    _transpose,
    rational_matrix,
)
from oig_xii_two_port_certificate import (
    _exact_dyadic_fraction,
    finite_neumann_two_port_gram,
)


Q = Fraction


def _matrix_from_text(rows):
    return tuple(tuple(Q(value) for value in row) for row in rows)


def _interval_product(left, right, *, same_variable=False):
    left_lower, left_upper = left
    right_lower, right_upper = right
    if same_variable:
        upper = max(left_lower * left_lower, left_upper * left_upper)
        lower = Q(0) if left_lower <= 0 <= left_upper else min(
            left_lower * left_lower, left_upper * left_upper
        )
        return lower, upper
    products = (
        left_lower * right_lower,
        left_lower * right_upper,
        left_upper * right_lower,
        left_upper * right_upper,
    )
    return min(products), max(products)


class NeumannMatchedFrameAdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run_matched_frame_certificate()

    def test_row_normalization_encloses_independently_assembled_gram(self) -> None:
        """The row scale must reproduce the Stage-XII finite Gram."""
        side_length = 5
        precision = 192
        degree = 24
        centre, radius, _ = finite_modal_response_box(
            side_length, precision, degree
        )
        previous_precision = ctx.prec
        ctx.prec = precision
        try:
            gram, _ = finite_neumann_two_port_gram(side_length, degree)
            gram_endpoints = tuple(
                tuple(
                    (
                        _exact_dyadic_fraction(gram[row][column].lower()),
                        _exact_dyadic_fraction(gram[row][column].upper()),
                    )
                    for column in range(2)
                )
                for row in range(2)
            )
        finally:
            ctx.prec = previous_precision

        coordinate_boxes = tuple(
            tuple(
                (centre[row][column] - radius[row][column],
                 centre[row][column] + radius[row][column])
                for column in range(2)
            )
            for row in range(len(centre))
        )
        for output_row in range(2):
            for output_column in range(2):
                products = tuple(
                    _interval_product(
                        box[output_row],
                        box[output_column],
                        same_variable=output_row == output_column,
                    )
                    for box in coordinate_boxes
                )
                box_lower = sum((pair[0] for pair in products), Q(0))
                box_upper = sum((pair[1] for pair in products), Q(0))
                arb_lower, arb_upper = gram_endpoints[output_row][output_column]
                # These are independent outward evaluations of the same
                # normalized expression.  Neither enclosure need contain
                # the other, but disjoint intervals would expose a scale or
                # parity mismatch.
                self.assertLessEqual(box_lower, arb_upper)
                self.assertLessEqual(arb_lower, box_upper)

    def test_matched_noise_and_information_identities_are_exact(self) -> None:
        centre = _matrix_from_text(
            self.report["full_modal_response_centre_exact"]
        )
        projection = _matrix_from_text(
            self.report["matched_sensor_rows_exact"]
        )
        covariance = _matrix_from_text(
            self.report["matched_sensor_noise_covariance_exact"]
        )
        matched_centre = _matrix_from_text(
            self.report["matched_response_centre_exact"]
        )
        self.assertEqual(projection, _transpose(centre))
        self.assertEqual(covariance, _matmul(projection, _transpose(projection)))
        self.assertEqual(matched_centre, _matmul(projection, centre))
        matched_information = _matmul(
            _transpose(matched_centre),
            _matmul(_inverse(covariance), matched_centre),
        )
        self.assertEqual(matched_information, _matmul(_transpose(centre), centre))

    def test_absolute_value_diagonal_is_essential_to_frame_loss_bound(self) -> None:
        """Radius^T radius alone is not a Loewner bound for signed errors."""
        radius = rational_matrix([[1, 1]])
        hostile_error = rational_matrix([[1, -1]])
        radius_quadratic = _matmul(_transpose(radius), radius)
        error_quadratic = _matmul(_transpose(hostile_error), hostile_error)
        difference = tuple(
            tuple(
                radius_quadratic[row][column] - error_quadratic[row][column]
                for column in range(2)
            )
            for row in range(2)
        )
        self.assertLess(
            difference[0][0] * difference[1][1] - difference[0][1] ** 2,
            0,
        )

        certificate = _second_order_frame_loss_bound(
            radius, rational_matrix([[1, 0], [0, 1]])
        )
        diagonal = _matrix_from_text(
            certificate["diagonal_quadratic_bound_exact"]
        )
        self.assertEqual(diagonal, rational_matrix([[2, 0], [0, 2]]))
        # D-E^T E is positive semidefinite in this worst sign pattern.
        residual = tuple(
            tuple(
                diagonal[row][column] - error_quadratic[row][column]
                for column in range(2)
            )
            for row in range(2)
        )
        self.assertGreaterEqual(residual[0][0], 0)
        self.assertGreaterEqual(residual[1][1], 0)
        self.assertGreaterEqual(
            residual[0][0] * residual[1][1] - residual[0][1] ** 2,
            0,
        )

    def test_h1_majorant_direction_is_outward_certified(self) -> None:
        previous_precision = ctx.prec
        ctx.prec = 192
        try:
            side_length = self.report["model"]["side_length"]
            for mode, majorant in ((1, 11), (2, 41)):
                natural = 1 + 4 * side_length**2 * (
                    arb.pi() * mode / (2 * side_length)
                ).sin() ** 2
                continuum = 1 + (mode * arb.pi()) ** 2
                self.assertTrue(bool(natural < continuum))
                self.assertTrue(bool(continuum < majorant))
        finally:
            ctx.prec = previous_precision

    def test_top_level_tampering_is_rejected_when_verifier_is_available(self) -> None:
        verifier = getattr(
            matched_module, "verify_neumann_matched_frame_report", None
        )
        if verifier is None:
            self.skipTest(
                "top-level matched-frame verifier is a required follow-up"
            )
        tampered = deepcopy(self.report)
        tampered["metric_certificates"][0][
            "inherited_two_channel_floor_lower_exact"
        ] = "999/1"
        self.assertFalse(verifier(tampered)["passed"])


if __name__ == "__main__":
    unittest.main()
