import math
import unittest

from adelic_log_geometry import (
    analyze,
    determinant,
    gram_matrix,
    log_embedding,
    prime_basis,
    rational_from_exponents,
)


class AdelicLogGeometryTests(unittest.TestCase):
    def test_product_formula(self) -> None:
        coordinates = log_embedding([2, 3, 5], [4, -3, 2])
        self.assertAlmostEqual(sum(coordinates), 0.0, places=14)

    def test_rational_reconstruction(self) -> None:
        self.assertEqual(str(rational_from_exponents([2, 3, 5], [2, -1, 1])), "20/3")

    def test_prime_directions_make_sixty_degrees(self) -> None:
        vectors = prime_basis([2, 3])
        cosine = sum(x * y for x, y in zip(*vectors)) / math.prod(
            math.sqrt(sum(entry * entry for entry in vector)) for vector in vectors
        )
        self.assertAlmostEqual(cosine, 0.5, places=14)

    def test_gram_determinant(self) -> None:
        primes = [2, 3, 5, 7]
        numeric = determinant(gram_matrix(prime_basis(primes)))
        formula = (len(primes) + 1) * math.prod(math.log(p) ** 2 for p in primes)
        self.assertAlmostEqual(numeric / formula, 1.0, places=13)

    def test_integrated_analysis(self) -> None:
        result = analyze([2, 3, 5], 2)
        self.assertEqual(result["sample_count"], 125)
        self.assertEqual(result["unique_rational_count"], 125)


if __name__ == "__main__":
    unittest.main()

