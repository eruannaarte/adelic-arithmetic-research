"""Adverse checks for the new mathematical certificate boundary."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import json, unittest
from check_approximation import check_document, family_factor, drift_radius
from consequences import check as check_consequences

HERE=Path(__file__).resolve().parent


class WeightedFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.doc=json.loads((HERE/'approximation.json').read_text())

    def test_both_physical_designs_verify(self):
        result=check_document(self.doc,192)
        self.assertEqual(result['polynomial_residual_bounds_checked'],24)
        for r in result['designs']:
            self.assertGreater(Q(r['pointwise_gain']),2020)
            self.assertLess(Q(r['amplitude_20000_radius']),Q(3,100000))

    def test_understated_norm_rejected(self):
        bad=deepcopy(self.doc);entry=bad['designs'][0]['approximants'][0]
        entry['weighted_residual_norm_upper']=str(Q(entry['weighted_residual_norm_upper'])/2)
        with self.assertRaisesRegex(ValueError,'false weighted residual'):check_document(bad,192)

    def test_wrong_parity_rejected(self):
        bad=deepcopy(self.doc);bad['designs'][0]['approximants'][0]['rational_polynomial'][0]='1/1000000000'
        with self.assertRaisesRegex(ValueError,'parity'):check_document(bad,192)

    def test_missing_complete_remainder_rejected(self):
        bad=deepcopy(self.doc);del bad['designs'][0]['weighted_monomial_norm_upper']['21']
        with self.assertRaisesRegex(ValueError,'remainder coverage'):check_document(bad,192)

    def test_wrong_physical_window_rejected(self):
        bad=deepcopy(self.doc);bad['physical_window_coefficients'][0]='0'
        with self.assertRaisesRegex(ValueError,'physical coefficient'):check_document(bad,192)

    def test_frequency_contract_and_zero_frequency(self):
        r=self.doc['designs'][0]
        self.assertEqual(family_factor(r,0),0)
        self.assertLessEqual(family_factor(r,Q(1,2)),family_factor(r)/512)
        with self.assertRaises(ValueError):family_factor(r,Q(1001,1000))
        with self.assertRaises(ValueError):family_factor(r,-1)
        with self.assertRaises(ValueError):family_factor(r,0.5)
        with self.assertRaises(ValueError):drift_radius(r,-1)

    def test_full_arithmetic_error_budget(self):
        result=check_consequences()
        self.assertEqual(result['integer_gates_checked'],98)
        self.assertTrue(all(r['old_pointwise_failed_gates']>0 for r in result['designs']))


if __name__=='__main__':unittest.main(verbosity=2)
