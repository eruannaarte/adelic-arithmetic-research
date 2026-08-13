#!/usr/bin/env python3

import unittest

from arithmetic_sensing_iv import REFERENCE_COEFFICIENTS, reference_design
from optimized_arithmetic_quadrature import (
    continuous_density_extrema,
    fejer_riesz_certificate,
    prealias_limit,
)


class ArithmeticSensingIVTests(unittest.TestCase):
    def test_reference_design_has_continuum_margin(self) -> None:
        design = reference_design()
        extrema = continuous_density_extrema(design.coefficients)
        self.assertGreater(extrema["minimum"], 1e-5)
        self.assertLessEqual(extrema["maximum"], 2.5 - 9e-9)
        self.assertGreater(prealias_limit(design), 13.8156)

    def test_margin_shifted_factors_give_positive_residual_floor(self) -> None:
        margin = 5e-9
        lower = fejer_riesz_certificate(
            REFERENCE_COEFFICIENTS, constant=1.0 - margin
        )
        upper = fejer_riesz_certificate(
            -REFERENCE_COEFFICIENTS, constant=1.5 - margin
        )
        multiplier = 2 * len(REFERENCE_COEFFICIENTS) + 1
        self.assertGreater(margin - multiplier * lower.residual, 0.0)
        self.assertGreater(margin - multiplier * upper.residual, 0.0)


if __name__ == "__main__":
    unittest.main()
