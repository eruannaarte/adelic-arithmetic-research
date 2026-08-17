"""Exact regression checks for the explicit uniform-lattice schedules.

The analytic audit is in OIG_UNIFORM_LATTICE_EXPLICIT_CONSTANTS_AUDIT.md.
These tests deliberately use only integers and Fraction arithmetic for every
published threshold decision.  Irrational constants are checked only through
the same direction-safe rational inequalities used in the manuscript.
"""

from fractions import Fraction as F
import unittest


class ExplicitUniformLatticeConstantTests(unittest.TestCase):
    def test_direction_safe_response_constant_arithmetic(self) -> None:
        # C_sqrt(t) < 86/5 and C_h < 629/125.
        self.assertEqual(F(37, 25) * 10 + F(12, 5), F(86, 5))
        self.assertEqual(F(37, 25) * F(17, 5), F(629, 125))
        self.assertEqual(F(86, 5) + F(629, 125), F(2779, 125))
        self.assertLess(F(2779, 125), 23)

        # K^2 < 19712/9025 < (37/25)^2.
        self.assertLess(F(19712, 9025), F(37, 25) ** 2)

        # B^2 < 2[(11/10)^2+(21/10)^2] < (17/5)^2.
        b_squared_upper = 2 * (F(11, 10) ** 2 + F(21, 10) ** 2)
        self.assertLess(b_squared_upper, F(17, 5) ** 2)

    def test_low_atomic_tail_constant(self) -> None:
        # C_low = 63 sqrt(2)/(800 sqrt(pi)).  Since pi > 3, compare
        # its squared upper bound exactly against (3/40)^2.
        c_low_squared_upper = F(63**2 * 2, 800**2 * 3)
        self.assertLess(c_low_squared_upper, F(3, 40) ** 2)

    def test_high_tail_rational_weakenings(self) -> None:
        # Use g^2=16/25, sqrt(2)<10/7, e^{-4}<(7/19)^4,
        # and 1/pi<1/3 exactly as in the manuscript.
        c_high_l_upper = 32 * F(16, 25) * F(10, 7) * F(7, 19) ** 4
        c_high_a_upper = F(16, 25) * F(1, 3) * F(20, 7) * F(7, 19) ** 4
        self.assertLess(c_high_l_upper, F(27, 50))
        self.assertLess(c_high_a_upper, F(3, 250))
        self.assertLess(F(3, 40) + F(27, 50) + F(3, 250), F(2, 3))

    def test_direct_floor_schedules(self) -> None:
        ell_l2 = F(14315, 10**11)  # 1.4315e-7
        ell_h1 = F(35523, 10**13)  # 3.5523e-9
        self.assertLess(F(23, 322_000_000), ell_l2 / 2)
        self.assertLess(F(23, 10 * 1_300_000_000), ell_h1 / 2)

    def test_joint_atomic_schedules(self) -> None:
        ell_l2 = F(14315, 10**11)
        ell_h1 = F(35523, 10**13)

        # Finite-to-continuum allocation: one quarter of the floor.
        self.assertLess(F(23, 643_000_000), ell_l2 / 4)
        self.assertLess(F(23, 10 * 2_590_000_000), ell_h1 / 4)

        # Continuum-to-atomic allocation: one quarter of the floor.
        self.assertLess(F(2, 3 * 18_629_000), ell_l2 / 4)
        self.assertLess(F(1, 15 * 75_069_000), ell_h1 / 4)

    def test_published_thresholds_are_ceiling_safe(self) -> None:
        ell_l2 = F(14315, 10**11)
        ell_h1 = F(35523, 10**13)

        # Exact real lower thresholds before taking the published integer
        # ceilings.  Cross multiplication avoids floating point entirely.
        self.assertLess(F(92, 1) / ell_l2, 643_000_000)
        self.assertLess(F(46, 5) / ell_h1, 2_590_000_000)
        self.assertLess(F(8, 3) / ell_l2, 18_629_000)
        self.assertLess(F(4, 15) / ell_h1, 75_069_000)


if __name__ == "__main__":
    unittest.main()
