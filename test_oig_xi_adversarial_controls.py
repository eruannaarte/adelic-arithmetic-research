"""Exact small controls for the OIG XI finite-transfer audit.

These tests falsify common shortcuts.  They do not certify a physical
finite-grid experiment.
"""

import cmath
import math
import unittest

import numpy as np


def generalized_floor(gram, metric):
    """Smallest generalized eigenvalue for positive-definite metric."""
    chol = np.linalg.cholesky(metric)
    inverse = np.linalg.inv(chol)
    normalized = inverse @ gram @ inverse.T
    return float(np.linalg.eigvalsh(normalized)[0])


class OIGXIAdversarialControls(unittest.TestCase):
    def test_zero_euclidean_gram_error_can_hide_metric_collapse(self):
        h = 1.0e-3
        gram = np.eye(2)
        continuum_metric = np.eye(2)
        finite_metric = np.diag([1.0, h**-2])

        self.assertEqual(np.linalg.norm(gram - gram), 0.0)
        self.assertAlmostEqual(
            generalized_floor(gram, continuum_metric),
            1.0,
        )
        self.assertAlmostEqual(
            generalized_floor(gram, finite_metric),
            h**2,
        )

    def test_pair_form_lower_bound_includes_metric_error(self):
        continuum_metric = np.eye(2)
        finite_metric = np.diag([1.2, 0.8])
        continuum_gram = np.diag([0.5, 2.0])
        finite_gram = continuum_gram - 0.1 * np.eye(2)

        continuum_floor = 0.5
        gram_error = 0.1
        metric_error = 0.2
        certified = (
            (continuum_floor - gram_error) / (1.0 + metric_error)
        )
        actual = generalized_floor(finite_gram, finite_metric)

        self.assertAlmostEqual(actual, certified)
        self.assertGreater(actual, 0.0)

    def test_response_level_perturbation_bound(self):
        continuum = np.diag([2.0, 1.0])
        perturbation = np.array([[0.0, 0.1], [0.0, 0.0]])
        finite = continuum + perturbation
        epsilon = np.linalg.norm(perturbation, 2)

        continuum_floor = np.linalg.svd(
            continuum, compute_uv=False
        )[-1]
        finite_floor = np.linalg.svd(finite, compute_uv=False)[-1]

        self.assertGreaterEqual(
            finite_floor + 1.0e-15,
            continuum_floor - epsilon,
        )
        self.assertGreaterEqual(
            finite_floor**2 + 1.0e-15,
            (continuum_floor - epsilon) ** 2,
        )

    def test_lower_moment_leakage_is_amplified_by_calibration(self):
        h = 1.0e-3
        q = h**2
        raw = np.diag([q, q**2])
        calibration = np.diag([q**-1, q**-2])
        leakage = np.zeros((2, 2))
        leakage[0, 1] = h**2

        raw_error = np.linalg.norm(leakage, 2)
        calibrated_error = np.linalg.norm(leakage @ calibration, 2)

        self.assertAlmostEqual(raw_error, h**2)
        self.assertAlmostEqual(calibrated_error, h**2 / q**2)
        self.assertGreater(calibrated_error, 1.0e5)
        self.assertTrue(
            np.allclose(raw @ calibration, np.eye(2))
        )

    def test_restricted_A_norm_does_not_control_mixed_words(self):
        diffusion = np.array([[1.0, -1.0], [-1.0, 1.0]])
        multiplication = np.diag([0.0, 1.0])
        conserved = np.ones(2)
        source = np.ones(2)

        self.assertTrue(np.allclose(diffusion @ source, 0.0))
        self.assertTrue(np.allclose(conserved @ diffusion, 0.0))

        mixed = (
            conserved
            @ multiplication
            @ diffusion
            @ multiplication
            @ source
        )
        self.assertAlmostEqual(float(mixed), 1.0)

    def test_weak_target_convergence_misses_growing_frequency(self):
        n = 1000
        h = 1.0 / n
        growing_frequency = math.pi / h
        continuum_multiplier = 1.0 + 0.0j
        shifted_multiplier = cmath.exp(
            -1j * growing_frequency * h
        )

        self.assertAlmostEqual(
            abs(shifted_multiplier - continuum_multiplier),
            2.0,
        )
        self.assertLess(h, 0.002)

    def test_uncontrolled_boundary_coordinate_has_order_one_error(self):
        hankel_argument = 2.0
        interior = 1.0 / (
            2.0 * math.sqrt(math.pi * hankel_argument)
        )
        at_boundary = (
            1.0 + math.exp(0.0)
        ) / (2.0 * math.sqrt(math.pi * hankel_argument))

        self.assertAlmostEqual(at_boundary, 2.0 * interior)
        self.assertAlmostEqual(at_boundary - interior, interior)

    def test_sensor_count_does_not_imply_sensor_frame(self):
        continuum_response = np.eye(2)
        two_sensors = np.array([[1.0, 0.0], [1.0, 0.0]])
        sensed_gram = (
            continuum_response.T
            @ two_sensors.T
            @ two_sensors
            @ continuum_response
        )

        self.assertEqual(two_sensors.shape[0], 2)
        self.assertEqual(np.linalg.matrix_rank(two_sensors), 1)
        self.assertAlmostEqual(np.linalg.eigvalsh(sensed_gram)[0], 0.0)

    def test_output_calibration_does_not_create_information(self):
        q = 0.1
        response = np.diag([q, q**2])
        noise = np.eye(2)
        output_gain = np.diag([q**-1, q**-2])

        displayed_response = output_gain @ response
        transformed_noise = output_gain @ noise @ output_gain.T
        correct_information = (
            displayed_response.T
            @ np.linalg.inv(transformed_noise)
            @ displayed_response
        )
        original_information = response.T @ response
        naive_information = displayed_response.T @ displayed_response

        self.assertTrue(
            np.allclose(correct_information, original_information)
        )
        self.assertTrue(np.allclose(naive_information, np.eye(2)))
        self.assertFalse(
            np.allclose(naive_information, original_information)
        )

    def test_growing_mode_dispersion_fails_when_kh_is_fixed(self):
        n = 1000
        h = 1.0 / n
        mode = n // 2
        finite_symbol = (
            4.0
            / h**2
            * math.sin(mode * math.pi * h / 2.0) ** 2
        )
        continuum_symbol = (mode * math.pi) ** 2
        ratio = finite_symbol / continuum_symbol

        self.assertAlmostEqual(mode * h, 0.5)
        self.assertAlmostEqual(ratio, 8.0 / math.pi**2)
        self.assertGreater(abs(ratio - 1.0), 0.18)


if __name__ == "__main__":
    unittest.main()
