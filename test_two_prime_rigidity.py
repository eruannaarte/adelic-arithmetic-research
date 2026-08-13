import unittest
from fractions import Fraction

from two_prime_rigidity import exact_interval


def smooth_numbers(height: int) -> list[tuple[int, int, int]]:
    result = []
    power_two = 1
    exponent_two = 0
    while power_two <= height:
        value = power_two
        exponent_three = 0
        while value <= height:
            result.append((value, exponent_two, exponent_three))
            value *= 3
            exponent_three += 1
        power_two *= 2
        exponent_two += 1
    return sorted(result)


class TwoPrimeRigidityTests(unittest.TestCase):
    def test_interval_contains_truth_by_exact_power_comparisons(self) -> None:
        for height in [10, 30, 100, 1_000, 1_000_000]:
            result = exact_interval(height)
            lower = result["lower"]
            upper = result["upper"]
            self.assertLess(2**lower.numerator, 3**lower.denominator)
            self.assertGreater(2**upper.numerator, 3**upper.denominator)

    def test_all_smooth_comparisons_reduce_to_same_interval(self) -> None:
        for height in [30, 100, 300, 1_000]:
            numbers = smooth_numbers(height)
            lower = Fraction(0, 1)
            upper = None
            for (_, a, b), (_, c, d) in zip(numbers, numbers[1:]):
                if b == d:
                    continue
                bound = Fraction(c - a, b - d)
                if b > d:
                    upper = bound if upper is None else min(upper, bound)
                else:
                    lower = max(lower, bound)
            exact = exact_interval(height)
            self.assertEqual(lower, exact["lower"])
            self.assertEqual(upper, exact["upper"])

    def test_known_interval(self) -> None:
        result = exact_interval(1_000_000)
        self.assertEqual(result["lower"], Fraction(19, 12))
        self.assertEqual(result["upper"], Fraction(8, 5))


if __name__ == "__main__":
    unittest.main()
