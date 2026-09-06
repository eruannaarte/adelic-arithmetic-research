from fractions import Fraction as F
from itertools import product
import unittest
from directional import strict_radius_squared,slab_contains


class DirectionalTests(unittest.TestCase):
    def test_scalar_closed_interval_overlap_boundary(self):
        # Two centers0,3; asymmetric nuisance intervals[-1/4,1/2]
        # and[-1,1/4], with scalar error radius eta.
        # Oriented from second center to first: gap3-1-1/2=3/2.
        r2=strict_radius_squared(3,1,F(1,2),1)
        self.assertEqual(r2,F(9,16))
        for eta in (F(1,2),F(3,4),1):
            first=(-F(1,4)-eta,F(1,2)+eta)
            second=(2-eta,F(13,4)+eta)
            overlap=max(first[0],second[0])<=min(first[1],second[1])
            self.assertEqual(overlap,eta*eta>=r2)

    def test_shared_nuisance_cancels_before_support(self):
        # y=(x+p,p), ell=(1,-1). Shared p vanishes identically.
        for x,p in product((F(-2),F(0),F(3)),repeat=2):
            self.assertEqual((x+p)-p,x)
        # Independent p1,p2 change the same statistic and cannot be removed.
        self.assertNotEqual((0+1)-(-1),0)

    def test_correlated_noise_uses_one_dual_norm(self):
        # ell=(3,4), Euclidean unit error: gain exactly5, not3+4.
        self.assertTrue(slab_contains(5,0,0,25,1))
        self.assertFalse(slab_contains(F(5001,1000),0,0,25,1))
        self.assertEqual(F(3)*F(3,5)+F(4)*F(4,5),5)

    def test_zero_gain_and_one_sided_support(self):
        self.assertTrue(slab_contains(F(-1,4),F(1,4),F(1,2),0,0))
        self.assertTrue(slab_contains(F(1,2),F(1,4),F(1,2),0,1))
        self.assertFalse(slab_contains(-1,F(1,4),F(1,2),0,100))

    def test_translation_preserves_finite_answer_sets(self):
        centers={0:(F(0),F(1)),1:(F(3),F(4))};c=F(7,3);eta=F(3,4)
        for y in (F(k,4) for k in range(-5,23)):
            before={q for q,points in centers.items() if any(abs(y-v)<=eta for v in points)}
            after={q for q,points in centers.items() if any(abs((y-c)-(v-c))<=eta for v in points)}
            self.assertEqual(before,after)

    def test_invalid_contracts_and_closed_slab_endpoint(self):
        for args in ((0,0,0,1),(1,1,0,1),(1,-1,0,1),(1,0,0,0)):
            with self.assertRaises(ValueError):strict_radius_squared(*args)
        with self.assertRaises(ValueError):slab_contains(0,0,0,1,-1)
        self.assertTrue(slab_contains(F(3,2),F(1,2),F(1,2),1,1))


if __name__=='__main__':unittest.main(verbosity=2)
