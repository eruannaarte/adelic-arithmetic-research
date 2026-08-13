import random
import unittest
from decimal import Decimal, localcontext
from fractions import Fraction

from adelic_poisson import (
    gauss_legendre_pi,
    global_character_exponent,
    p_adic_fractional_part,
    verify_poisson,
)


class AdelicPoissonTests(unittest.TestCase):
    def test_p_adic_fractional_parts(self) -> None:
        self.assertEqual(p_adic_fractional_part(Fraction(5, 6), 2), Fraction(1, 2))
        self.assertEqual(p_adic_fractional_part(Fraction(5, 6), 3), Fraction(1, 3))
        self.assertEqual(p_adic_fractional_part(Fraction(5, 6), 5), Fraction(0, 1))

    def test_global_character_is_trivial_on_rationals(self) -> None:
        generator = random.Random(20260812)
        for _ in range(500):
            numerator = generator.randint(-10_000, 10_000)
            denominator = generator.randint(1, 2_000)
            exponent = global_character_exponent(Fraction(numerator, denominator))
            self.assertEqual(exponent.denominator, 1)

    def test_pi(self) -> None:
        with localcontext() as context:
            context.prec = 55
            pi = gauss_legendre_pi(50)
            expected = Decimal("3.1415926535897932384626433832795028841971693993751")
            self.assertLess(abs(pi - expected), Decimal("1e-49"))

    def test_self_dual_gaussian(self) -> None:
        report = verify_poisson("1", 1, 50)
        self.assertLess(Decimal(report["absolute_residual"]), Decimal("1e-48"))

    def test_scaled_adelic_poisson(self) -> None:
        for t, modulus in [("0.37", 6), ("2.5", 5), ("0.0125", 12)]:
            report = verify_poisson(t, modulus, 50)
            self.assertLess(Decimal(report["absolute_residual"]), Decimal("1e-47"))


if __name__ == "__main__":
    unittest.main()

