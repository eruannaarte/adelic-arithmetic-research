"""Boundary and scope controls for the three structured transfer gates."""
import unittest
from fractions import Fraction as Q
from transfer import directional_gate,pair_budget,integer_gate


class TransferTests(unittest.TestCase):
    def test_directional_gain_matters(self):
        g=directional_gate(1,100,2,'1/10','1/10',1)
        self.assertTrue(g['passed'])
        self.assertFalse(g['uniform_accuracy'])

    def test_strict_accuracy_boundary(self):
        self.assertFalse(directional_gate(1,100,0,'1/2','1/2',1)['passed'])
        self.assertFalse(directional_gate(1,100,0,1,0,1)['passed'])
        self.assertFalse(directional_gate(0,100,0,0,0,1)['passed'])

    def test_strict_label_boundary(self):
        self.assertFalse(directional_gate(100,2,1,0,0,1)['passed'])

    def test_weighted_source_incidence(self):
        for split in (Q(1,100),Q(1,3),Q(1,2),Q(99,100)):
            self.assertTrue(pair_budget(1,1,1/split,1/(1-split)))
        self.assertFalse(pair_budget(1,1,1,1))
        # Unequal explanation radii still require their own two terms.
        self.assertTrue(pair_budget(1,2,2,8))
        self.assertFalse(pair_budget(1,2,2,2))

    def test_half_integer_boundary(self):
        self.assertTrue(integer_gate(2,0,1,0,'1/9'))
        self.assertFalse(integer_gate(2,0,1,0,'1/8'))
        self.assertFalse(integer_gate(2,1,1,0,0))

    def test_invalid_premises(self):
        for v in (True,0.1,-1):
            with self.assertRaises(ValueError):
                directional_gate(1,100,0,0,v,1)
        with self.assertRaises(ValueError):
            pair_budget(1,1,0,1)
        with self.assertRaises(ValueError):
            integer_gate(2,0,0,0,0)


if __name__=='__main__':
    unittest.main(verbosity=2)
