import unittest
from fractions import Fraction as F
from transfer import (profile_form, lifting_witness, identity, multiply,
                      quadratic, scalar_boundary_squared, strict_scalar_gate,
                      pair_gate, inverse_gate, continuous_cell_gate,
                      normal_residual_error_bound)


class TransferTests(unittest.TestCase):
    def test_correlated_retained_noise_uses_minimum_lift(self):
        w = [[F(2, 3), F(-1, 3)], [F(-1, 3), F(2, 3)]]
        r, b = [[1, 0]], [[], []]
        form = profile_form(w, r, b)
        self.assertEqual(form["retained_noise_form"], [[F(1, 2)]])
        self.assertNotEqual(form["retained_noise_form"][0][0], w[0][0])
        witness = lifting_witness(w, r, b, [1])
        self.assertEqual(witness["noise"], [1, F(1, 2)])
        self.assertEqual(witness["noise_squared"], F(1, 2))

    def test_shared_nuisance_lifting_is_attained(self):
        w, r, b = [[1, 0], [0, 4]], identity(2), [[1], [1]]
        expected = [[F(4, 5), F(-4, 5)], [F(-4, 5), F(4, 5)]]
        self.assertEqual(profile_form(w, r, b)["retained_profile_form"], expected)
        for a in range(-3, 4):
            for c in range(-3, 4):
                wit = lifting_witness(w, r, b, [a, c])
                self.assertEqual([x+y for x, y in zip(wit["noise"], wit["retained_nuisance"])], [a, c])
                self.assertEqual(wit["noise_squared"], quadratic(expected, [a, c]))
                # Every alternative shared nuisance costs at least the minimum.
                for z in (-2, -1, 0, 1, 2):
                    self.assertGreaterEqual(quadratic(w, [a-z, c-z]), wit["noise_squared"])

    def test_dropping_shared_reference_destroys_query(self):
        w, b = identity(2), [[1], [1]]
        full = profile_form(w, identity(2), b)["full_profile_form"]
        restricted = profile_form(w, [[1, 0]], b)["full_profile_form"]
        self.assertEqual(quadratic(full, [1, 0]), F(1, 2))
        self.assertEqual(quadratic(restricted, [1, 0]), 0)
        # Two full inputs with the same retained first coordinate have different
        # first coordinates after full nuisance removal: order cannot be reused.
        self.assertNotEqual(multiply(full, [[0], [0]])[0], multiply(full, [[0], [2]])[0])

    def test_commuting_restriction_need_not_reconstruct_full_quotient(self):
        w, b = identity(3), [[0], [1], [0]]
        r = [[1, 0, 0], [0, 1, 0]]
        full = profile_form(w, identity(3), b)["full_profile_form"]
        partial = profile_form(w, r, b)["full_profile_form"]
        self.assertEqual(partial, [[1, 0, 0], [0, 0, 0], [0, 0, 0]])
        self.assertEqual(full, [[1, 0, 0], [0, 0, 0], [0, 0, 1]])
        self.assertEqual(multiply(r, full), [[1, 0, 0], [0, 0, 0]])

    def test_rank_deficient_nuisance_and_redundant_reading_contract(self):
        a = profile_form(identity(2), identity(2), [[1], [1]])
        b = profile_form(identity(2), identity(2), [[1, 2, 0], [1, 2, 0]])
        self.assertEqual(a["full_profile_form"], b["full_profile_form"])
        with self.assertRaises(ValueError):
            profile_form(identity(2), [[1, 0], [1, 0]], [[], []])

    def test_invalid_metric_and_inexact_scalar_rejected(self):
        for w in ([[1, 2], [0, 1]], [[1, 0], [0, 0]], [[1, 2], [2, 1]]):
            with self.assertRaises(ValueError):
                profile_form(w, identity(2), [[], []])
        for value in (True, 0.1):
            with self.assertRaises(TypeError):
                scalar_boundary_squared(1, value, 1)

    def test_scalar_closed_endpoint_and_zero_gain(self):
        self.assertEqual(scalar_boundary_squared(3, 1, 4)["boundary_squared"], F(1, 4))
        self.assertTrue(strict_scalar_gate(3, 1, 4, F(49, 100)))
        self.assertFalse(strict_scalar_gate(3, 1, 4, F(1, 2)))
        self.assertTrue(strict_scalar_gate(3, 1, 0, 10**30))
        self.assertFalse(strict_scalar_gate(1, 1, 0, 0))

    def test_pair_gate_has_actual_endpoint_collision(self):
        # Orthogonal one-column images have block Gram I. At deltas 3/5,4/5
        # the Cauchy-Schwarz endpoint is attained by source amplitudes 3/5,4/5.
        a, b = F(3, 5), F(4, 5)
        p, q, y = [a, 0], [0, b], [F(48, 125), F(36, 125)]
        self.assertEqual(sum((y[i]-p[i])**2 for i in range(2)), (a*a)**2)
        self.assertEqual(sum((y[i]-q[i])**2 for i in range(2)), (b*b)**2)
        self.assertFalse(pair_gate(1, a, b))
        self.assertTrue(pair_gate(1, a-F(1, 1000), b))
        self.assertTrue(inverse_gate(1, F(1, 1001), F(1, 1000)))
        self.assertFalse(inverse_gate(1, F(1, 1000), F(1, 1000)))

    def test_continuous_cell_signs_before_squaring(self):
        self.assertTrue(continuous_cell_gate(9, 1, 4))
        self.assertFalse(continuous_cell_gate(8, 1, 4))
        self.assertFalse(continuous_cell_gate(0, 1, 1))
        self.assertTrue(continuous_cell_gate(1, 0, 1))

    def test_normal_residual_accounts_for_weak_direction(self):
        # A=diag(2,1/10), y=(2,1/10), proposed=(1,0): true source=(1,1).
        # Normal residual=(0,1/100), mu=1/100 gives exactly unit solve error.
        self.assertEqual(normal_residual_error_bound(F(1, 100), F(1, 100)), 1)
        with self.assertRaises(ValueError):
            normal_residual_error_bound(0, 1)

    def test_query_class_saturation_differs_from_source_saturation(self):
        points = [(-1, -1), (-1, 1), (1, 0)]
        query = lambda p: p[0]
        for y in points:
            full_answers = {query(y)}
            retained_answers = {query(p) for p in points if p[0] == y[0]}
            self.assertEqual(full_answers, retained_answers)
        self.assertEqual(len([p for p in points if p[0] == -1]), 2)
        # Exact source recovery was lost although this coarser query survives.

    def test_unbounded_leak_and_convexified_query_counterexamples(self):
        leakage = F(1, 10**12)
        for proposed_budget in (1, 100, 10**6):
            nuisance = (proposed_budget+1)/leakage
            self.assertGreater(abs(leakage*nuisance), proposed_budget)
        responses = {-1: 0, 1: 0, 0: 1}
        self.assertEqual(len(responses), 3)  # All exact responses identify q.
        self.assertEqual((-1+1)/2, 0)  # Convexifying q=0 creates a false alias.


if __name__ == "__main__":
    unittest.main()
