"""Adverse full-certificate controls and independent complete-query checks."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import json,unittest
from orbit_bound import radius
from check_orbit import check
from consequences import premises,check_saved_budget,run
HERE=Path(__file__).resolve().parent

class OrbitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.doc=json.loads((HERE/'orbit_bound.json').read_text())
    def test_actual_grid_complete_source_replay(self):
        self.assertTrue(check(self.doc)['verified'])
        for r in self.doc['records']:
            old=Q(r['prior_pair_linear_clock_coefficient'])+Q(r['prior_pair_quadratic_clock_coefficient'])
            self.assertLess(radius(r,1),Q(47,100)*old)
    def test_missing_phase_lag_rejected(self):
        d=deepcopy(self.doc);d['records'][0]['clock_corners'][0]['correlations'].pop()
        with self.assertRaises(ValueError):check(d)
    def test_missing_clock_corner_rejected(self):
        d=deepcopy(self.doc);d['records'][1]['clock_corners'].pop()
        with self.assertRaises(ValueError):check(d)
    def test_discarded_infinite_valuation_tail_rejected(self):
        d=deepcopy(self.doc);d['complete_valuation_tail']['omitted_envelope_mass_upper']='0'
        with self.assertRaises(ValueError):check(d)
    def test_false_decorrelation_rejected(self):
        d=deepcopy(self.doc);d['records'][0]['clock_corners'][0]['correlations'][0]['normalized_absolute_correlation_upper']='1/10000000000000000000000000000000000000000'
        with self.assertRaises(ValueError):check(d)
    def test_underclaimed_complete_odd_mass_rejected(self):
        d=deepcopy(self.doc);d['complete_series']['odd_mass_upper']='1'
        with self.assertRaises(ValueError):check(d)
    def test_missing_nonlinear_remainder_rejected(self):
        d=deepcopy(self.doc);d['records'][0]['quadratic_clock_coefficient']='0'
        with self.assertRaises(ValueError):check(d)
    def test_exact_clock_domain(self):
        self.assertEqual(radius(self.doc['records'][0],0),0)
        for h in (-1,True,0.5):
            with self.assertRaises(ValueError):radius(self.doc['records'][0],h)
    def test_fake_rounding_certificate_rejected(self):
        lookup=premises();r=json.loads((HERE/'result_outer_h120.json').read_text())['prior_pair_comparison']
        self.assertFalse(check_saved_budget(r,*lookup('outer',12,'pair')))
        r=deepcopy(r);r['all_49_strict_rounding_gates']=True
        with self.assertRaises(ValueError):check_saved_budget(r,*lookup('outer',12,'pair'))
    def test_h120_actual_queries_and_exact_boundaries(self):
        result=run(False);self.assertTrue(result['verified'])
        self.assertEqual([r['largest_passing_integer_multiplier'] for r in result['integer_multiplier_boundaries']],[827,385,170,79])
        self.assertTrue(all(r['all_49_integers_recovered'] for r in result['actual_h120_results']))

if __name__=='__main__':unittest.main(verbosity=2)
