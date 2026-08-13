import unittest
from decimal import Decimal

from quadratic_adelic_geometry import (
    GAUSSIAN,
    GOLDEN,
    archimedean_and_selfdual_report,
    calibration_rank_report,
    golden_regulator,
    minkowski_bound,
)


class QuadraticAdelicGeometryTests(unittest.TestCase):
    def test_ring_arithmetic(self) -> None:
        i = GAUSSIAN.element(0, 1)
        self.assertEqual((i * i).coordinates(), (-1, 0))
        phi = GOLDEN.element(0, 1)
        self.assertEqual((phi * phi).coordinates(), (1, 1))
        self.assertEqual(phi.norm, -1)

    def test_prime_decomposition_gaussian(self) -> None:
        expectations = {2: "ramified", 3: "inert", 5: "split", 13: "split"}
        for p, behavior in expectations.items():
            primes = GAUSSIAN.primes_above(p)
            self.assertEqual(primes[0].behavior, behavior)
            product = GAUSSIAN.unit_ideal()
            for prime in primes:
                product *= prime.ideal ** prime.ramification_index
            self.assertEqual(product, GAUSSIAN.principal_ideal(GAUSSIAN.element(p)))

    def test_prime_decomposition_golden(self) -> None:
        expectations = {2: "inert", 3: "inert", 5: "ramified", 11: "split", 19: "split"}
        for p, behavior in expectations.items():
            primes = GOLDEN.primes_above(p)
            self.assertEqual(primes[0].behavior, behavior)
            product = GOLDEN.unit_ideal()
            for prime in primes:
                product *= prime.ideal ** prime.ramification_index
            self.assertEqual(product, GOLDEN.principal_ideal(GOLDEN.element(p)))

    def test_exact_principal_ideal_factorization(self) -> None:
        samples = [
            GAUSSIAN.element(1, 1),
            GAUSSIAN.element(2, 1),
            GAUSSIAN.element(7, 4),
            GOLDEN.element(-1, 2),
            GOLDEN.element(2, 0),
            GOLDEN.element(-4, 1),
        ]
        for alpha in samples:
            factors = alpha.field.factor_principal(alpha)
            norm = 1
            product = alpha.field.unit_ideal()
            for prime, exponent in factors:
                norm *= prime.norm**exponent
                product *= prime.ideal**exponent
            self.assertEqual(norm, abs(alpha.norm))
            self.assertEqual(product, alpha.field.principal_ideal(alpha))

    def test_minkowski_class_number_bounds(self) -> None:
        self.assertLess(minkowski_bound(GAUSSIAN), Decimal(2))
        self.assertLess(minkowski_bound(GOLDEN), Decimal(2))
        self.assertGreater(minkowski_bound(GAUSSIAN), Decimal(1))
        self.assertGreater(minkowski_bound(GOLDEN), Decimal(1))

    def test_unit_lattice_and_regulator(self) -> None:
        report = golden_regulator(60)
        self.assertLess(abs(Decimal(report["sum"])), Decimal("1e-58"))
        expected = Decimal("0.481211825059603447497758913424368423135184334385660519661018")
        self.assertLess(abs(Decimal(report["regulator"]) - expected), Decimal("1e-59"))

    def test_selfdual_global_volume(self) -> None:
        for field in [GAUSSIAN, GOLDEN]:
            report = archimedean_and_selfdual_report(field, 60)
            self.assertLess(
                abs(Decimal(report["global_selfdual_quotient_volume"]) - Decimal(1)),
                Decimal("1e-59"),
            )

    def test_finite_calibration_matrices_have_one_scale(self) -> None:
        gaussian_primes = [
            GAUSSIAN.primes_above(2)[0],
            GAUSSIAN.primes_above(3)[0],
            *GAUSSIAN.primes_above(5),
        ]
        gaussian_elements = [
            GAUSSIAN.element(1, 1),
            GAUSSIAN.element(3),
            GAUSSIAN.element(2, 1),
            GAUSSIAN.element(2, -1),
        ]
        golden_primes = [
            GOLDEN.primes_above(2)[0],
            GOLDEN.primes_above(5)[0],
            *GOLDEN.primes_above(11),
        ]
        golden_elements = [
            GOLDEN.element(0, 1),
            GOLDEN.element(2),
            GOLDEN.element(-1, 2),
            GOLDEN.element(-4, 1),
            GOLDEN.element(-3, -1),
        ]
        for report in [
            calibration_rank_report(GAUSSIAN, gaussian_elements, gaussian_primes),
            calibration_rank_report(GOLDEN, golden_elements, golden_primes),
        ]:
            self.assertEqual(report["nullity"], 1)
            self.assertLess(report["maximum_product_formula_residual"], 1e-12)


if __name__ == "__main__":
    unittest.main()
