"""Adverse certificate and complete-query checks; no floating search oracle."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import json, unittest
from check_clock import check
from clock_bound import radius
from budget import profile,operation_counts
from consequences import check as check_consequences

HERE=Path(__file__).resolve().parent

class ClockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.document=json.loads((HERE/'clock_bound.json').read_text())

    def test_complete_clock_and_exact_gain(self):
        self.assertTrue(check(self.document)['verified'])
        for row in self.document['records']:
            self.assertLess(radius(row,1),Q(402,1000)*Q(row['prior_pointwise_clock_coefficient']))
            self.assertLess(radius(row,1),Q(732,1000)*Q(row['weighted_pointwise_clock_coefficient']))

    def test_incomplete_shared_clock_corners_rejected(self):
        doc=deepcopy(self.document);doc['records'][0]['clock_corners'].pop()
        with self.assertRaises(ValueError):check(doc)

    def test_false_decorrelation_rejected(self):
        doc=deepcopy(self.document);doc['records'][0]['clock_corners'][0]['normalized_phase_correlation_upper']='0'
        with self.assertRaises(ValueError):check(doc)

    def test_missing_nonlinear_clock_remainder_rejected(self):
        doc=deepcopy(self.document);doc['records'][0]['quadratic_clock_coefficient']='0'
        with self.assertRaises(ValueError):check(doc)

    def test_overclaimed_complete_mass_rejected(self):
        doc=deepcopy(self.document);doc['complete_mass_data']['valuation_classes'][2]['complete_pair_derivative_mass_lower']='999999999'
        with self.assertRaises(ValueError):check(doc)

    def test_bad_envelope_ratio_rejected(self):
        doc=deepcopy(self.document);doc['complete_mass_data']['valuation_classes'][1]['ratio_upper']='1'
        with self.assertRaises(ValueError):check(doc)

    def test_exact_clock_boundary_and_cost_contract(self):
        row=self.document['records'][0]
        self.assertEqual(radius(row,0),0)
        for value in (-1,True,0.5):
            with self.assertRaises(ValueError):radius(row,value)
        with self.assertRaises(ValueError):operation_counts(True)
        with self.assertRaises(ValueError):operation_counts(11)
        self.assertEqual(operation_counts(12)['augmented_complex_dimension'],62)

    def test_complete_degree_and_clock_consequences(self):
        result=check_consequences()
        self.assertTrue(result['verified'])
        self.assertFalse(result['outcomes'][1]['prior_pointwise_bound_also_passes'])
        self.assertTrue(all(r['sixtyfold_all_49_integers'] for r in result['outcomes']))

if __name__=='__main__':unittest.main(verbosity=2)
