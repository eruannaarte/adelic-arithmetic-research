"""Controls for the omitted odd degree, complete channels and computed inverse."""
from copy import deepcopy
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import importlib.util,json,unittest
from check import check
from budget import factor,profile,operation_counts
from physical import PhysicalModel
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def document():return json.loads((HERE/'evidence.json').read_text())

class DegreeElevenTests(unittest.TestCase):
    def test_valid_complete_certificate(self):
        self.assertTrue(check()['verified'])
    def test_reject_changed_complete_bias(self):
        d=document();d['designs']['multi']['degrees'][0]['complete_coefficient_bias_upper'][49]='0'
        with self.assertRaises(ValueError):check(d)
    def test_reject_incomplete_taylor_channels(self):
        d=document();d['approximations'][0]['approximants'].pop()
        with self.assertRaises(ValueError):check(d)
    def test_reject_degree_twelve_even_leak(self):
        d=document();d['approximations'][0]['approximants'][0]['rational_polynomial'].append('1')
        with self.assertRaises(ValueError):check(d)
    def test_general_parity_formula_at_odd_degree(self):
        r=document()['approximations'][0];omega=Q(3)
        parts={0:Q(),1:Q()}
        for e in reversed(r['approximants']):
            k=e['order'];parts[k%2]+=Q(e['weighted_residual_norm_upper'])*omega**k/factorial(k)
        for k in (33,34):parts[k%2]+=Q(r['weighted_monomial_norm_upper'][str(k)])*omega**k/factorial(k)
        self.assertEqual(factor(r,omega),max(parts.values()))
        self.assertEqual(factor(r,0),0)
        with self.assertRaises(ValueError):factor(r,-1)
        with self.assertRaises(ValueError):factor(r,3.0)
    def test_fixed_and_smaller_amplitude_contract(self):
        d=document();clock=json.loads((ROOT/'research/structured_transfer_2026_09/arithmetic/clock_bound.json').read_text())
        for name in ('multi','outer'):
            a=next(a for a in d['approximations'] if a['design']==name);cr=next(a for a in clock['records'] if a['design']==name);r=d['designs'][name]['degrees'][0]
            self.assertEqual(profile(r,a,cr)['passing_gates'],32)
            self.assertTrue(profile(r,a,cr,amplitude=500)['all_49_strict_rounding_gates'])
            with self.assertRaises(ValueError):profile(r,a,cr,rho=-1)
            wrong=deepcopy(cr);wrong['design']='outer' if name=='multi' else 'multi'
            with self.assertRaises(ValueError):profile(r,a,wrong)
    def test_dimension_and_dense_operation_counts(self):
        c=operation_counts();self.assertEqual(c['augmented_complex_dimension'],61)
        self.assertEqual(c['classical_full_gram_complex_multiply_accumulates'],33116900)

class ActualInverseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=PhysicalModel('multi',11,256)
        cls.data=json.loads((HERE/'data_B500.json').read_text())['readings']
        cls.saved=json.loads((HERE/'result_multi_B500.json').read_text())
        s=importlib.util.spec_from_file_location('_degree11_test_verifier',ROOT/'research/operational_transfer_2026_09/noise/certify.py')
        cls.verifier=importlib.util.module_from_spec(s);s.loader.exec_module(cls.verifier)
    def test_actual_bad_proposal_rejected(self):
        proposal=deepcopy(self.saved['proposal']);proposal[1][0]=str(Q(proposal[1][0])+Q(1,100))
        nu=Q(self.saved['certificate']['nonpolynomial_drift_radius'])
        r=self.verifier.verify(self.model,self.data,proposal,Q(4,10**5),nu,True)
        self.assertEqual(r['status'],'not_certified')
        self.assertGreater(Q(r['normal_residual_upper']),Q(1,1000))
    def test_missing_raw_reading_rejected(self):
        with self.assertRaises(ValueError):self.model.residual(self.data[:-1],self.saved['proposal'])

if __name__=='__main__':unittest.main()
