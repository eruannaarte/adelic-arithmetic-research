"""Full-model replay and adverse controls for the uniform collision family."""
from copy import deepcopy
from fractions import Fraction as Q
from itertools import combinations, product
from math import prod
import cmath
import json
import math
import unittest
from flint import arb, ctx
import uniform_collision as u


class UniformCollisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = json.loads((u.HERE / 'inputs.json').read_text())

    def test_factored_full_parameter_box_at_two_precisions(self):
        self.assertEqual(u.check(256), u.check(384))

    def test_independent_integer_label_full_box_at_two_precisions(self):
        self.assertEqual(u.check(256, independent=True), u.check(384, independent=True))

    def test_factored_and_expanded_point_values_and_all_derivatives(self):
        with ctx.workprec(256):
            x = list(map(u.ball, self.inputs['coordinates']))
            t = list(map(u.ball, self.inputs['times']))
            for pair in zip(u.model(x, t, self.inputs['active']), u.expanded_model(x, t, self.inputs['active'])):
                a, b = pair
                for i in range(a.nrows()):
                    for j in range(a.ncols()):
                        self.assertTrue((a[i, j] - b[i, j]).contains(0))

    def test_source_derivative_exact_centered_coordinate_identity(self):
        with ctx.workprec(256):
            x = list(map(u.ball, self.inputs['coordinates']))
            t = list(map(u.ball, self.inputs['times']))
            active = self.inputs['active']
            _, J, _ = u.model(x, t, active)
            h = u.ball('1/10000')
            for j, index in enumerate(active):
                xp, xm = x.copy(), x.copy()
                xp[index] += h
                xm[index] -= h
                fp, _, _ = u.model(xp, t, active)
                fm, _, _ = u.model(xm, t, active)
                for i in range(12):
                    self.assertTrue(((fp[i, 0] - fm[i, 0]) / (2 * h) - J[i, j]).contains(0))

    def test_all_vertex_pairs_with_independent_lipschitz_control(self):
        # An independent raw complex response control: every normalized
        # vertex-pair squared distance has derivative at most delta/k
        # in one time, hence 6 epsilon delta/k over the time box.
        vertices = list(product(range(4), repeat=3))
        times = list(map(lambda v: float(Q(v)), self.inputs['times']))
        epsilon = float(Q(self.inputs['time_radius']))
        labels = {v: prod(p ** a for p, a in zip(u.PRIMES, v)) for v in vertices}
        readings = {v: [cmath.exp(-1j * t * math.log(labels[v])) for t in times] for v in vertices}
        lower = float('inf')
        for a, b in combinations(vertices, 2):
            k = sum(i != j for i, j in zip(a, b))
            value = sum(abs(x - y) ** 2 for x, y in zip(readings[a], readings[b])) / (2 * k)
            delta = abs(math.log(labels[a] / labels[b]))
            lower = min(lower, value - 6 * epsilon * delta / k)
        self.assertGreater(lower, 1.03 ** 2 + 1e-7)

    def test_frozen_scalar_and_bit_queries(self):
        d = u.check()['query_obstruction']
        a, b, gap = Q(d['first_answer']), Q(d['second_answer']), Q(d['answer_gap'])
        self.assertEqual(b - a, gap)
        self.assertLess(a, Q(1, 2))
        self.assertGreater(b, Q(1, 2))
        self.assertGreater(gap / 2, Q(2748, 10000))
        for estimate in (Q(0), Q(1), Q(1, 2), (a + b) / 2):
            self.assertGreaterEqual(max(abs(estimate - a), abs(estimate - b)), gap / 2)
        altered = deepcopy(self.inputs)
        altered['active'][0] = 3
        with self.assertRaises(ValueError):
            u.build(altered)

    def test_exact_exported_consequences_and_forged_values(self):
        d = u.check()
        u.check_consequences(d)
        for field, value in (('contraction_upper', '1'), ('moving_center_residual_upper', '1'),
                             ('minimum_probability_lower', '0'), ('factor_distance_squared_lower', '0'),
                             ('vertex_floor_squared_lower', '0')):
            forged = deepcopy(d)
            forged[field] = value
            with self.assertRaises(ValueError):
                u.check_consequences(forged)
        forged = deepcopy(d)
        forged['query_obstruction']['answer_gap'] = '1'
        with self.assertRaises(ValueError):
            u.check_consequences(forged)

    def test_oversized_box_and_false_recovery_claims_are_rejected(self):
        for field, value in (('time_radius', '1/1000'), ('root_radius', '1/100'),
                             ('probability_claim', '1/10'), ('separation_claim', '1'),
                             ('vertex_floor_claim', '11/10')):
            altered = deepcopy(self.inputs)
            altered[field] = value
            with self.assertRaises(ValueError):
                u.build(altered)

    def test_moving_center_is_needed_by_this_frozen_certificate(self):
        altered = deepcopy(self.inputs)
        altered['predictor'] = [['0'] * 6 for _ in range(12)]
        with self.assertRaises(ValueError):
            u.build(altered)

    def test_malformed_domains_and_singular_preconditioner(self):
        for field, value in (('time_radius', '0'), ('root_radius', '-1'),
                             ('active', [0] * 12), ('predictor', [['0']]),
                             ('preconditioner', [['0'] * 12 for _ in range(12)])):
            altered = deepcopy(self.inputs)
            altered[field] = value
            with self.assertRaises(ValueError):
                u.build(altered)


if __name__ == '__main__':
    unittest.main(verbosity=2)
