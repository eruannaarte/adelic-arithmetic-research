"""Executable adversarial controls for OIG Stage X certification.

These tests expose invalid numerical shortcuts.  They are deliberately small
and do not claim to implement interval arithmetic or certify the Stage IX
atlas.
"""

from decimal import Decimal, localcontext
from fractions import Fraction
import math
import unittest

import numpy as np


def generalized_eigenvalues_diagonal_metric(gram, metric):
    """Generalized eigenvalues when metric is positive diagonal."""
    diagonal = np.diag(metric)
    if np.any(diagonal <= 0):
        raise ValueError("metric must be positive diagonal")
    inverse_sqrt = np.diag(1.0 / np.sqrt(diagonal))
    normalized = inverse_sqrt @ gram @ inverse_sqrt
    return np.linalg.eigvalsh(normalized)


def exact_ldl_pivots(matrix):
    """Exact no-pivot LDL pivots for a symmetric Fraction matrix."""
    n = len(matrix)
    lower = [
        [Fraction(int(i == j), 1) for j in range(n)]
        for i in range(n)
    ]
    pivots = [Fraction(0, 1) for _ in range(n)]

    for j in range(n):
        pivot = matrix[j][j]
        for k in range(j):
            pivot -= lower[j][k] * lower[j][k] * pivots[k]
        if pivot == 0:
            raise ZeroDivisionError("zero exact LDL pivot")
        pivots[j] = pivot

        for i in range(j + 1, n):
            value = matrix[i][j]
            for k in range(j):
                value -= lower[i][k] * lower[j][k] * pivots[k]
            lower[i][j] = value / pivot

    return pivots


class OIGXAdversarialControls(unittest.TestCase):
    def test_coordinate_whitening_does_not_change_generalized_floor(self):
        epsilon = 1.0e-4
        gram = np.diag([1.0, epsilon**2])
        metric = np.eye(2)
        calibration = np.diag([1.0, 1.0 / epsilon])

        calibrated_gram = calibration.T @ gram @ calibration
        calibrated_metric = calibration.T @ metric @ calibration

        self.assertTrue(np.allclose(calibrated_gram, np.eye(2)))
        original = generalized_eigenvalues_diagonal_metric(gram, metric)
        calibrated = generalized_eigenvalues_diagonal_metric(
            calibrated_gram, calibrated_metric
        )
        self.assertTrue(np.allclose(original, calibrated))
        self.assertAlmostEqual(calibrated[0], epsilon**2)

    def test_finite_grid_misses_an_arbitrarily_narrow_dip(self):
        grid = np.linspace(0.0, 1.0, 21)
        center = 0.5 * (grid[7] + grid[8])
        delta = 1.0e-30

        sampled = delta + (grid - center) ** 2
        true_minimum = delta

        self.assertGreater(sampled.min(), 6.0e-4)
        self.assertEqual(true_minimum, delta)
        self.assertGreater(sampled.min() / true_minimum, 1.0e20)

    def test_entrywise_endpoint_eigenvalues_do_not_enclose_interval(self):
        lower = np.array(
            [
                [2.0, 0.25548882, -0.08607100],
                [0.25548882, 2.0, -1.40896198],
                [-0.08607100, -1.40896198, 2.0],
            ]
        )
        upper = np.array(
            [
                [2.0, 1.17513321, 0.81983103],
                [1.17513321, 2.0, 0.62089529],
                [0.81983103, 0.62089529, 2.0],
            ]
        )
        mixed = np.array(
            [
                [2.0, 1.17513321, 0.81983103],
                [1.17513321, 2.0, -1.40896198],
                [0.81983103, -1.40896198, 2.0],
            ]
        )

        self.assertGreater(np.linalg.eigvalsh(lower)[0], 0.5)
        self.assertGreater(np.linalg.eigvalsh(upper)[0], 0.7)
        self.assertLess(np.linalg.eigvalsh(mixed)[0], -0.2)

        indices = np.triu_indices(3, 1)
        self.assertTrue(np.all(mixed[indices] >= lower[indices]))
        self.assertTrue(np.all(mixed[indices] <= upper[indices]))

    def test_exact_hilbert_spd_can_have_false_binary64_rank(self):
        n = 13
        exact_hilbert = [
            [Fraction(1, i + j + 1) for j in range(n)]
            for i in range(n)
        ]
        pivots = exact_ldl_pivots(exact_hilbert)
        self.assertTrue(all(pivot > 0 for pivot in pivots))

        floating_hilbert = np.array(
            [
                [1.0 / (i + j + 1.0) for j in range(n)]
                for i in range(n)
            ]
        )
        floating_rank = np.linalg.matrix_rank(floating_hilbert)
        floating_minimum = np.linalg.eigvalsh(floating_hilbert)[0]

        self.assertLess(floating_rank, n)
        self.assertLess(floating_minimum, 1.0e-17)

    def test_positive_exponential_underflows_in_binary64(self):
        self.assertEqual(math.exp(-800.0), 0.0)
        with localcontext() as context:
            context.prec = 60
            exact_sign_control = Decimal(-800).exp()
        self.assertGreater(exact_sign_control, Decimal(0))

    def test_boundary_cosine_does_not_dominate_common_window(self):
        """The interior H_b lower cannot be assigned to every boundary."""

        def gaussian_half_integral(rate):
            return 1.0 / (2.0 * math.sqrt(math.pi * rate))

        def truncated_half_integral(rate, window):
            return (
                math.erf(math.sqrt(rate * window))
                / (2.0 * math.sqrt(math.pi * rate))
            )

        kappa = 1.607
        interior = (
            gaussian_half_integral(2.0)
            - 2.0 * gaussian_half_integral(3.0)
            + gaussian_half_integral(4.0)
        )
        cosine_correction = (
            gaussian_half_integral(2.0) * math.exp(-(kappa**2) / 2.0)
            - 2.0
            * gaussian_half_integral(3.0)
            * math.exp(-(kappa**2) / 3.0)
            + gaussian_half_integral(4.0) * math.exp(-(kappa**2) / 4.0)
        )
        boundary = interior + cosine_correction
        common_window = (
            truncated_half_integral(2.0, 1.0)
            - 2.0 * truncated_half_integral(3.0, 1.0)
            + truncated_half_integral(4.0, 1.0)
        )

        self.assertGreater(boundary, 0.0)
        self.assertLess(boundary, common_window)
        self.assertAlmostEqual(boundary / interior, 0.3960945, places=6)

    def test_target_contrast_and_finite_sensors_collapse_floors(self):
        base_gram = np.diag([2.0, 0.5, 0.1])
        alpha = 1.0e-7
        contrast_gram = alpha**2 * base_gram
        self.assertAlmostEqual(
            np.linalg.eigvalsh(contrast_gram)[0],
            alpha**2 * 0.1,
        )

        sensor_matrix = np.array(
            [
                [1.0, 0.0, 1.0, 2.0, -1.0],
                [0.0, 1.0, 1.0, -1.0, 2.0],
                [1.0, 1.0, 0.0, 1.0, 1.0],
            ]
        )
        sensed_gram = sensor_matrix.T @ sensor_matrix
        self.assertEqual(np.linalg.matrix_rank(sensor_matrix), 3)
        self.assertEqual(5 - np.linalg.matrix_rank(sensor_matrix), 2)
        self.assertLess(abs(np.linalg.eigvalsh(sensed_gram)[0]), 1.0e-12)

    def test_midpoint_minus_radius_is_a_valid_box_lower_control(self):
        """Certify G(theta)=[[2,theta],[theta,1]] on [-1/2,1/2]."""

        def gram(theta):
            return np.array([[2.0, theta], [theta, 1.0]])

        edges = np.linspace(-0.5, 0.5, 18)
        local_bounds = []
        for left, right in zip(edges[:-1], edges[1:]):
            midpoint = 0.5 * (left + right)
            radius = 0.5 * (right - left)

            # The derivative matrix [[0,1],[1,0]] has operator norm one.
            midpoint_floor = np.linalg.eigvalsh(gram(midpoint))[0]
            local_bounds.append(midpoint_floor - radius)

        certified_floor = min(local_bounds)
        dense_parameters = np.linspace(-0.5, 0.5, 10001)
        true_grid_floor = min(
            np.linalg.eigvalsh(gram(theta))[0]
            for theta in dense_parameters
        )

        self.assertGreater(certified_floor, 0.7)
        self.assertLessEqual(certified_floor, true_grid_floor)


if __name__ == "__main__":
    unittest.main()
