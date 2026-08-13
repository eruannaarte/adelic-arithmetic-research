#!/usr/bin/env python3
"""Exact quadratic-ring and ideal checks for Stage 4.

The two supported fields are Q(i) and Q(sqrt(5)), represented as Z[omega] with

    omega^2 - T*omega + U = 0.

All algebraic-integer and ideal operations are exact. Decimal arithmetic is
used only for Archimedean embeddings, regulators, and displayed volume checks.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from decimal import Decimal, localcontext
from functools import reduce
from typing import Iterable, Sequence


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return nonnegative g and x,y with x*a+y*b=g."""
    if a == 0 and b == 0:
        return 0, 0, 0
    old_r, r = abs(a), abs(b)
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_r, old_s * (1 if a >= 0 else -1), old_t * (1 if b >= 0 else -1)


def bezout_list(values: Sequence[int]) -> tuple[int, list[int]]:
    g = 0
    coefficients: list[int] = []
    for value in values:
        next_g, scale_old, scale_new = extended_gcd(g, value)
        coefficients = [scale_old * coefficient for coefficient in coefficients]
        coefficients.append(scale_new)
        g = next_g
    return g, coefficients


def determinant(left: tuple[int, int], right: tuple[int, int]) -> int:
    return left[0] * right[1] - left[1] * right[0]


def column_hnf(generators: Sequence[tuple[int, int]]) -> tuple[tuple[int, int], tuple[int, int]]:
    """Canonical basis (a,0),(b,d), with a,d>0 and 0<=b<a."""
    if len(generators) < 2:
        raise ValueError("a full rank lattice needs at least two generators")
    minors = [
        abs(determinant(generators[i], generators[j]))
        for i in range(len(generators))
        for j in range(i + 1, len(generators))
    ]
    index = reduce(math.gcd, minors, 0)
    if index == 0:
        raise ValueError("generators do not span a full rank lattice")
    y_gcd, coefficients = bezout_list([vector[1] for vector in generators])
    if y_gcd == 0:
        raise ValueError("full rank lattice has zero second-coordinate projection")
    horizontal = index // y_gcd
    x_lift = sum(coefficient * vector[0] for coefficient, vector in zip(coefficients, generators))
    diagonal = x_lift % horizontal
    basis = ((horizontal, 0), (diagonal, y_gcd))

    # Audit that the canonical lattice contains every input generator.
    for x, y in generators:
        if y % y_gcd or (x - (y // y_gcd) * diagonal) % horizontal:
            raise AssertionError("HNF reconstruction lost a generator")
    return basis


@dataclass(frozen=True)
class QuadraticField:
    name: str
    symbol: str
    trace_omega: int
    norm_omega: int
    real_places: int
    complex_places: int

    @property
    def discriminant(self) -> int:
        return self.trace_omega**2 - 4 * self.norm_omega

    def element(self, a: int, b: int = 0) -> "QuadraticInteger":
        return QuadraticInteger(self, a, b)

    @property
    def one(self) -> "QuadraticInteger":
        return self.element(1, 0)

    def unit_ideal(self) -> "Ideal":
        return Ideal(self, ((1, 0), (0, 1)))

    def principal_ideal(self, alpha: "QuadraticInteger") -> "Ideal":
        self._check_element(alpha)
        if alpha.is_zero:
            raise ValueError("zero does not generate a full-rank nonzero ideal")
        a, b = alpha.a, alpha.b
        alpha_omega = (-self.norm_omega * b, a + self.trace_omega * b)
        return Ideal.from_generators(self, [(a, b), alpha_omega])

    def polynomial_mod(self, x: int, p: int) -> int:
        return (x * x - self.trace_omega * x + self.norm_omega) % p

    def primes_above(self, p: int) -> list["PrimeIdeal"]:
        if not is_prime(p):
            raise ValueError("p must be a rational prime")
        roots = [x for x in range(p) if self.polynomial_mod(x, p) == 0]
        if not roots:
            ideal = self.principal_ideal(self.element(p))
            return [PrimeIdeal(p, None, 1, 2, ideal, "inert")]
        if len(roots) == 1:
            root = roots[0]
            ideal = Ideal.from_generators(self, [(p, 0), (-root, 1)])
            return [PrimeIdeal(p, root, 2, 1, ideal, "ramified")]
        return [
            PrimeIdeal(
                p,
                root,
                1,
                1,
                Ideal.from_generators(self, [(p, 0), (-root, 1)]),
                "split",
            )
            for root in roots
        ]

    def factor_principal(self, alpha: "QuadraticInteger") -> list[tuple["PrimeIdeal", int]]:
        self._check_element(alpha)
        if alpha.is_zero:
            raise ValueError("zero has no finite prime-ideal factorization")
        absolute_norm = abs(alpha.norm)
        if absolute_norm == 1:
            return []
        factors: list[tuple[PrimeIdeal, int]] = []
        for p, _ in factor_integer(absolute_norm):
            for prime_ideal in self.primes_above(p):
                exponent = 0
                power = prime_ideal.ideal
                while power.contains(alpha):
                    exponent += 1
                    power = power * prime_ideal.ideal
                if exponent:
                    factors.append((prime_ideal, exponent))

        reconstructed = self.unit_ideal()
        reconstructed_norm = 1
        for prime_ideal, exponent in factors:
            reconstructed = reconstructed * (prime_ideal.ideal**exponent)
            reconstructed_norm *= prime_ideal.norm**exponent
        principal = self.principal_ideal(alpha)
        if reconstructed != principal:
            raise AssertionError("prime-ideal factors did not reconstruct the principal ideal")
        if reconstructed_norm != absolute_norm:
            raise AssertionError("ideal-norm factorization did not match element norm")
        return factors

    def _check_element(self, alpha: "QuadraticInteger") -> None:
        if alpha.field != self:
            raise ValueError("element belongs to another field")


@dataclass(frozen=True)
class QuadraticInteger:
    field: QuadraticField
    a: int
    b: int

    @property
    def is_zero(self) -> bool:
        return self.a == 0 and self.b == 0

    @property
    def norm(self) -> int:
        t, u = self.field.trace_omega, self.field.norm_omega
        return self.a * self.a + t * self.a * self.b + u * self.b * self.b

    @property
    def trace(self) -> int:
        return 2 * self.a + self.field.trace_omega * self.b

    def conjugate(self) -> "QuadraticInteger":
        return self.field.element(self.a + self.field.trace_omega * self.b, -self.b)

    def __mul__(self, other: "QuadraticInteger") -> "QuadraticInteger":
        if self.field != other.field:
            raise ValueError("cannot multiply elements from different fields")
        t, u = self.field.trace_omega, self.field.norm_omega
        return self.field.element(
            self.a * other.a - u * self.b * other.b,
            self.a * other.b + self.b * other.a + t * self.b * other.b,
        )

    def __pow__(self, exponent: int) -> "QuadraticInteger":
        if exponent < 0:
            raise ValueError("negative powers need field fractions")
        result = self.field.one
        base = self
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent //= 2
        return result

    def coordinates(self) -> tuple[int, int]:
        return self.a, self.b

    def __str__(self) -> str:
        if self.b == 0:
            return str(self.a)
        return f"{self.a}{self.b:+d}*{self.field.symbol}"


@dataclass(frozen=True)
class Ideal:
    field: QuadraticField
    basis: tuple[tuple[int, int], tuple[int, int]]

    def __post_init__(self) -> None:
        canonical = column_hnf(self.basis)
        if canonical != self.basis:
            object.__setattr__(self, "basis", canonical)

    @classmethod
    def from_generators(
        cls, field: QuadraticField, generators: Sequence[tuple[int, int]]
    ) -> "Ideal":
        return cls(field, column_hnf(generators))

    @property
    def norm(self) -> int:
        return abs(determinant(*self.basis))

    def contains(self, alpha: QuadraticInteger) -> bool:
        self.field._check_element(alpha)
        (horizontal, _), (diagonal, vertical) = self.basis
        x, y = alpha.coordinates()
        return y % vertical == 0 and (x - (y // vertical) * diagonal) % horizontal == 0

    def __mul__(self, other: "Ideal") -> "Ideal":
        if self.field != other.field:
            raise ValueError("cannot multiply ideals from different fields")
        products: list[tuple[int, int]] = []
        for x in self.basis:
            left = self.field.element(*x)
            for y in other.basis:
                products.append((left * self.field.element(*y)).coordinates())
        result = Ideal.from_generators(self.field, products)
        if result.norm != self.norm * other.norm:
            raise AssertionError("ideal norm was not multiplicative")
        return result

    def __pow__(self, exponent: int) -> "Ideal":
        if exponent < 0:
            raise ValueError("negative integral-ideal powers are fractional ideals")
        result = self.field.unit_ideal()
        base = self
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent //= 2
        return result

    def __str__(self) -> str:
        return f"Ideal{self.basis}"


@dataclass(frozen=True)
class PrimeIdeal:
    rational_prime: int
    root: int | None
    ramification_index: int
    residue_degree: int
    ideal: Ideal
    behavior: str

    @property
    def norm(self) -> int:
        return self.rational_prime**self.residue_degree

    @property
    def label(self) -> str:
        if self.root is None:
            return f"({self.rational_prime})"
        return f"({self.rational_prime}, {self.ideal.field.symbol}-{self.root})"


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def factor_integer(n: int) -> list[tuple[int, int]]:
    n = abs(n)
    if n < 1:
        raise ValueError("factorization needs a nonzero integer")
    factors: list[tuple[int, int]] = []
    p = 2
    while p * p <= n:
        exponent = 0
        while n % p == 0:
            exponent += 1
            n //= p
        if exponent:
            factors.append((p, exponent))
        p = 3 if p == 2 else p + 2
    if n > 1:
        factors.append((n, 1))
    return factors


GAUSSIAN = QuadraticField("Q(i)", "i", 0, 1, 0, 1)
GOLDEN = QuadraticField("Q(sqrt(5))", "phi", 1, -1, 2, 0)


def decomposition_report(field: QuadraticField, primes: Iterable[int]) -> list[dict[str, object]]:
    report: list[dict[str, object]] = []
    for p in primes:
        ideals = field.primes_above(p)
        reconstructed = field.unit_ideal()
        for prime_ideal in ideals:
            reconstructed = reconstructed * (prime_ideal.ideal ** prime_ideal.ramification_index)
        if reconstructed != field.principal_ideal(field.element(p)):
            raise AssertionError("prime decomposition did not reconstruct (p)")
        report.append(
            {
                "p": p,
                "behavior": ideals[0].behavior,
                "prime_ideals": [
                    {
                        "label": prime_ideal.label,
                        "root": prime_ideal.root,
                        "e": prime_ideal.ramification_index,
                        "f": prime_ideal.residue_degree,
                        "norm": prime_ideal.norm,
                        "basis": prime_ideal.ideal.basis,
                    }
                    for prime_ideal in ideals
                ],
            }
        )
    return report


def factorization_report(elements: Iterable[QuadraticInteger]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for alpha in elements:
        factors = alpha.field.factor_principal(alpha)
        result.append(
            {
                "element": str(alpha),
                "trace": alpha.trace,
                "norm": alpha.norm,
                "principal_ideal_basis": alpha.field.principal_ideal(alpha).basis,
                "factorization": [
                    {"prime_ideal": prime.label, "norm": prime.norm, "exponent": exponent}
                    for prime, exponent in factors
                ],
            }
        )
    return result


def minkowski_bound(field: QuadraticField, digits: int = 40) -> Decimal:
    """M_K=(4/pi)^r2 * n!/n^n * sqrt(|D|), here n=2."""
    from adelic_poisson import gauss_legendre_pi

    with localcontext() as context:
        context.prec = digits + 10
        pi = gauss_legendre_pi(digits + 5)
        result = Decimal(abs(field.discriminant)).sqrt() / Decimal(2)
        if field.complex_places:
            result *= (Decimal(4) / pi) ** field.complex_places
        context.prec = digits
        return +result


def archimedean_and_selfdual_report(field: QuadraticField, digits: int = 50) -> dict[str, str]:
    with localcontext() as context:
        context.prec = digits + 10
        sqrt_discriminant = Decimal(abs(field.discriminant)).sqrt()
        ordinary_arch_covolume = sqrt_discriminant / (Decimal(2) ** field.complex_places)
        complex_measure_multiplier = Decimal(2) ** field.complex_places
        selfdual_arch_covolume = ordinary_arch_covolume * complex_measure_multiplier
        finite_integer_volume = Decimal(1) / sqrt_discriminant
        global_covolume = selfdual_arch_covolume * finite_integer_volume
        context.prec = digits
        return {
            "ordinary_archimedean_covolume": str(+ordinary_arch_covolume),
            "complex_selfdual_measure_multiplier": str(+complex_measure_multiplier),
            "selfdual_archimedean_covolume": str(+selfdual_arch_covolume),
            "finite_integer_adele_volume": str(+finite_integer_volume),
            "global_selfdual_quotient_volume": str(+global_covolume),
        }


def golden_regulator(digits: int = 50) -> dict[str, str]:
    with localcontext() as context:
        context.prec = digits + 10
        sqrt5 = Decimal(5).sqrt()
        phi = (Decimal(1) + sqrt5) / Decimal(2)
        conjugate = abs((Decimal(1) - sqrt5) / Decimal(2))
        log_phi = phi.ln()
        log_conjugate = conjugate.ln()
        context.prec = digits
        return {
            "fundamental_unit": "phi=(1+sqrt(5))/2",
            "norm": "-1",
            "log_embedding": f"({+log_phi}, {+log_conjugate})",
            "sum": str(+(log_phi + log_conjugate)),
            "regulator": str(+log_phi),
        }


def matrix_rank(rows: Sequence[Sequence[float]], tolerance: float = 1e-11) -> int:
    work = [list(row) for row in rows]
    if not work:
        return 0
    row_count, column_count = len(work), len(work[0])
    pivot_row = 0
    for column in range(column_count):
        pivot = max(range(pivot_row, row_count), key=lambda row: abs(work[row][column]))
        if abs(work[pivot][column]) <= tolerance:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        for entry in range(column, column_count):
            work[pivot_row][entry] /= pivot_value
        for row in range(row_count):
            if row == pivot_row:
                continue
            factor = work[row][column]
            for entry in range(column, column_count):
                work[row][entry] -= factor * work[pivot_row][entry]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def archimedean_logs(alpha: QuadraticInteger) -> list[float]:
    field = alpha.field
    if field.real_places == 2:
        root_disc = math.sqrt(field.discriminant)
        omega_1 = (field.trace_omega + root_disc) / 2
        omega_2 = (field.trace_omega - root_disc) / 2
        return [math.log(abs(alpha.a + alpha.b * omega_1)), math.log(abs(alpha.a + alpha.b * omega_2))]
    if field.complex_places == 1:
        return [math.log(abs(alpha.norm))]
    raise NotImplementedError("only the two Stage 4 quadratic signatures are supported")


def calibration_rank_report(
    field: QuadraticField,
    elements: Sequence[QuadraticInteger],
    finite_primes: Sequence[PrimeIdeal],
) -> dict[str, object]:
    labels = [f"arch_{index + 1}" for index in range(field.real_places + field.complex_places)]
    labels.extend(prime.label for prime in finite_primes)
    rows: list[list[float]] = []
    for alpha in elements:
        factor_map = {prime.ideal: exponent for prime, exponent in field.factor_principal(alpha)}
        row = archimedean_logs(alpha)
        row.extend(
            -factor_map.get(prime.ideal, 0) * math.log(prime.norm)
            for prime in finite_primes
        )
        rows.append(row)
    maximum_product_formula_residual = max(abs(sum(row)) for row in rows)
    rank = matrix_rank(rows)
    return {
        "places": labels,
        "constraint_rows": rows,
        "rank": rank,
        "nullity": len(labels) - rank,
        "maximum_product_formula_residual": maximum_product_formula_residual,
        "interpretation": "nullity one means the sampled unit/principal relations leave only a common local scale",
    }


def analyze() -> dict[str, object]:
    prime_sample = [2, 3, 5, 7, 11, 13, 19]
    gaussian_elements = [
        GAUSSIAN.element(1, 1),
        GAUSSIAN.element(2, 1),
        GAUSSIAN.element(3, 0),
        GAUSSIAN.element(7, 4),
    ]
    golden_elements = [
        GOLDEN.element(0, 1),
        GOLDEN.element(-1, 2),
        GOLDEN.element(2, 0),
        GOLDEN.element(-4, 1),
        GOLDEN.element(-3, -1),
    ]
    gaussian_calibration_elements = [
        GAUSSIAN.element(1, 1),
        GAUSSIAN.element(3),
        GAUSSIAN.element(2, 1),
        GAUSSIAN.element(2, -1),
    ]
    gaussian_calibration_primes = [
        GAUSSIAN.primes_above(2)[0],
        GAUSSIAN.primes_above(3)[0],
        *GAUSSIAN.primes_above(5),
    ]
    golden_calibration_elements = [
        GOLDEN.element(0, 1),
        GOLDEN.element(2),
        GOLDEN.element(-1, 2),
        GOLDEN.element(-4, 1),
        GOLDEN.element(-3, -1),
    ]
    golden_calibration_primes = [
        GOLDEN.primes_above(2)[0],
        GOLDEN.primes_above(5)[0],
        *GOLDEN.primes_above(11),
    ]
    return {
        "scope": "exact arithmetic in Z[i] and Z[phi], plus displayed Archimedean decimals",
        "Q(i)": {
            "discriminant": GAUSSIAN.discriminant,
            "signature": [GAUSSIAN.real_places, GAUSSIAN.complex_places],
            "minkowski_bound": str(minkowski_bound(GAUSSIAN)),
            "class_number_conclusion": "1 because every ideal class has norm <= 4/pi < 2",
            "prime_decomposition": decomposition_report(GAUSSIAN, prime_sample),
            "principal_factorizations": factorization_report(gaussian_elements),
            "selfdual_volume": archimedean_and_selfdual_report(GAUSSIAN),
            "unit_group": "{+1,-1,+i,-i}; regulator convention 1",
            "finite_calibration_matrix": calibration_rank_report(
                GAUSSIAN, gaussian_calibration_elements, gaussian_calibration_primes
            ),
        },
        "Q(sqrt(5))": {
            "integral_basis": "1, phi where phi^2-phi-1=0",
            "discriminant": GOLDEN.discriminant,
            "signature": [GOLDEN.real_places, GOLDEN.complex_places],
            "minkowski_bound": str(minkowski_bound(GOLDEN)),
            "class_number_conclusion": "1 because every ideal class has norm <= sqrt(5)/2 < 2",
            "prime_decomposition": decomposition_report(GOLDEN, prime_sample),
            "principal_factorizations": factorization_report(golden_elements),
            "unit_lattice": golden_regulator(),
            "selfdual_volume": archimedean_and_selfdual_report(GOLDEN),
            "finite_calibration_matrix": calibration_rank_report(
                GOLDEN, golden_calibration_elements, golden_calibration_primes
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    return argparse.ArgumentParser(description=__doc__).parse_args()


def main() -> None:
    parse_args()
    print(json.dumps(analyze(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
