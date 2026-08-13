import unittest
from fractions import Fraction

from exact_rigidity_certificates import (
    recover_exact_entries,
    solve_unique_rational_system,
    verify_certificate,
)


class ExactRigidityCertificateTests(unittest.TestCase):
    def test_exact_rectangular_solver(self) -> None:
        self.assertEqual(
            solve_unique_rational_system([[2, 0], [0, 3], [2, 3]], [1, 1, 2]),
            [Fraction(1, 2), Fraction(1, 3)],
        )

    def test_recover_short_upper_support(self) -> None:
        self.assertEqual(
            recover_exact_entries([26, 62], 3, "upper"),
            [(27, Fraction(1, 5)), (63, Fraction(1, 5))],
        )

    def test_short_upper_certificate_at_100(self) -> None:
        certificate = verify_certificate(
            3,
            "upper",
            Fraction(8, 5),
            [(27, Fraction(1, 5)), (63, Fraction(1, 5))],
        )
        self.assertTrue(certificate["verified_with_exact_rational_arithmetic"])

    def test_lower_certificate_at_30(self) -> None:
        certificate = verify_certificate(
            3, "lower", Fraction(3, 2), [(8, Fraction(1, 2))]
        )
        self.assertEqual(certificate["support_size"], 1)

    def test_invalid_certificate_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            verify_certificate(3, "upper", Fraction(8, 5), [(27, Fraction(1, 5))])


if __name__ == "__main__":
    unittest.main()
