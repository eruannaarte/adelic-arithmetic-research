"""Executable controls for the OIG IX growing-band adversarial audit.

These tests check exact algebraic obstructions and stable numerical
illustrations.  They do not replace the compactness proofs in the audit.
"""

from __future__ import annotations

import unittest

import numpy as np
from numpy.polynomial.legendre import leggauss


def ramp_phase(k: int, s: np.ndarray, g: float = 0.8) -> np.ndarray:
    """Exact Stage VIII ramp phase F_k(s)."""

    s = np.asarray(s, dtype=float)
    numerator = np.sqrt(2.0) * np.exp(-s) * g * s
    numerator *= 1.0 - ((-1.0) ** k) * np.exp(-g * s)
    return numerator / ((g * s) ** 2 + (k * np.pi) ** 2)


def gauss_interval(a: float, b: float, order: int = 480):
    nodes, weights = leggauss(order)
    x = 0.5 * (b - a) * nodes + 0.5 * (a + b)
    w = 0.5 * (b - a) * weights
    return x, w


def atomic_norm(values: np.ndarray, weights: np.ndarray) -> float:
    return float(np.sqrt(np.sum(weights * np.abs(values) ** 2)))


class OIGIXAdversarialControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # exp(-pi^2 r^2) makes the omitted tail far below double precision.
        cls.r, cls.rw = gauss_interval(0.0, 4.0)
        cls.s = (np.pi * cls.r) ** 2

    def test_symmetric_modulation_has_exact_odd_nulls(self):
        n = 256
        x = (np.arange(n) + 0.5) / n
        modulation = 1.0 + (x - 0.5) ** 2
        for k in (1, 3, 9, 31):
            port = np.sqrt(2.0) * np.cos(k * np.pi * x)
            for s in (0.1, 0.7, 3.0):
                phase = np.mean(np.exp(-s * modulation) * port)
                self.assertLess(abs(phase), 2.0e-15)

    def test_finite_sampling_rank_is_row_limited(self):
        sample_s = np.array([0.15, 0.4, 0.9, 1.8])
        matrix = np.column_stack(
            [ramp_phase(k, sample_s) for k in range(1, 10)]
        )
        singular = np.linalg.svd(matrix, compute_uv=False)
        self.assertEqual(np.linalg.matrix_rank(matrix, tol=1.0e-12), 4)
        self.assertEqual(len(singular), 4)
        # Nine proposed ports and four scalar samples leave at least five
        # exact source null directions, even though all four row singulars
        # are nonzero.
        self.assertGreater(singular[-1], 1.0e-9)

    def test_ramp_columns_decay_and_hminus2_pair_collapses(self):
        column_scaled = []
        pair_norms = []
        hminus2_norms = []
        for k in (20, 40, 80):
            fk = ramp_phase(k, self.s)
            fk2 = ramp_phase(k + 2, self.s)
            column_scaled.append(k**2 * atomic_norm(fk, self.rw))

            c0 = (k * np.pi) ** 2
            c1 = ((k + 2) * np.pi) ** 2
            pair = c0 * fk - c1 * fk2
            pair_norms.append(atomic_norm(pair, self.rw))
            hminus2_norms.append(
                np.sqrt(
                    c0**2 / (1.0 + (k * np.pi) ** 2) ** 2
                    + c1**2 / (1.0 + ((k + 2) * np.pi) ** 2) ** 2
                )
            )

        # k^2 ||F_k|| approaches a positive parity-dependent constant.
        self.assertLess(abs(column_scaled[-1] / column_scaled[-2] - 1.0), 0.01)
        # The H^{-2} source size stays nonzero while the leading phase
        # profiles cancel and the response tends rapidly to zero.
        self.assertGreater(min(hminus2_norms), 1.3)
        self.assertLess(pair_norms[-1], 0.18 * pair_norms[0])

    def test_early_phase_has_high_order_moment_null_direction(self):
        x, xw = gauss_interval(0.0, 1.0, order=320)
        k_values = np.arange(1, 7)
        ports = np.sqrt(2.0) * np.cos(np.pi * np.outer(x, k_values))
        modulation = 1.0 + 0.8 * x

        # Four nontrivial moment constraints on six source coefficients.
        moments = np.vstack(
            [
                np.sum(xw[:, None] * modulation[:, None] ** m * ports, axis=0)
                for m in range(1, 5)
            ]
        )
        _, _, vh = np.linalg.svd(moments)
        null_basis = vh[4:].T

        fifth = np.sum(
            xw[:, None] * modulation[:, None] ** 5 * ports, axis=0
        )
        coefficients = null_basis @ (null_basis.T @ fifth)
        coefficients /= np.linalg.norm(coefficients)

        self.assertLess(np.linalg.norm(moments @ coefficients), 2.0e-13)
        self.assertGreater(abs(fifth @ coefficients), 1.0e-7)

        source = ports @ coefficients

        def laplace(sample_s: float) -> float:
            return float(np.sum(xw * np.exp(-sample_s * modulation) * source))

        # With moments 0 through 4 cancelled (mean zero is exact for the
        # cosine band), the first surviving term is order s^5.
        ratio = abs(laplace(0.10) / laplace(0.05))
        self.assertGreater(ratio, 25.0)
        self.assertLess(ratio, 36.0)

    def test_fixed_band_singular_values_follow_the_causal_flag(self):
        # A Gaussian Fourier weight is used only as a clean nonvanishing
        # resolved-chart weight.  The theorem needs an interval of support,
        # not this particular kernel.
        u, uw = gauss_interval(0.0, 4.0, order=300)
        x, xw = gauss_interval(0.0, 1.0, order=260)
        ports = np.sqrt(2.0) * np.cos(
            np.pi * np.outer(x, np.arange(1, 5))
        )
        modulation = 1.0 + 0.8 * x

        def singular_values(q: float) -> np.ndarray:
            phase = (
                np.exp(
                    -np.pi**2
                    * q
                    * u[:, None] ** 2
                    * modulation[None, :]
                )
                * xw[None, :]
            ) @ ports
            weighted = (
                np.sqrt(uw)[:, None]
                * np.exp(-0.5 * (np.pi * u) ** 2)[:, None]
                * phase
            )
            return np.linalg.svd(weighted, compute_uv=False)

        coarse = singular_values(0.0125)
        fine = singular_values(0.00625)
        ratios = fine / coarse
        expected = 0.5 ** np.arange(1, 5)

        # Halving q multiplies the ordered singular values by
        # 2^{-1}, 2^{-2}, 2^{-3}, and 2^{-4}, up to finite-q corrections.
        np.testing.assert_allclose(ratios, expected, rtol=0.12, atol=0.0)

    def test_a_finite_boundary_sample_can_hit_a_carrier_zero(self):
        r0 = 0.73
        kappa = 1.0 / (2.0 * r0)
        weight = 1.0 + np.cos(2.0 * np.pi * kappa * r0)
        self.assertLess(abs(weight), 2.0e-15)

        # At a midpoint target, every odd cosine target sensor is deleted.
        odd_modes = np.arange(1, 20, 2)
        carrier = np.cos(odd_modes * np.pi * 0.5)
        self.assertLess(np.max(np.abs(carrier)), 4.0e-15)


if __name__ == "__main__":
    unittest.main()
