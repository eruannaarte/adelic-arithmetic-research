from pathlib import Path
from fractions import Fraction as Q
from math import comb
import copy, json, unittest
from budget import profile,factor
from check_approximation import check_clock,check_document

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


class UncertaintyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.approx=json.loads((HERE/'approximation.json').read_text())
        cls.prior=json.loads((ROOT/'research/transfer_theorem_2026_09/noise/evidence.json').read_text())
        cls.clock=Q(cls.approx['clock_and_derivative']['complete_clock_distortion_radius'])

    def test_zero_frequency_and_powerlaw(self):
        for r in self.approx['records']:
            self.assertEqual(factor(r,0),0)
            for omega in (Q(1,10),Q(1,2),Q(3,4),Q(1)):
                self.assertLessEqual(factor(r,omega),omega**(r['degree']+1)*factor(r,1))

    def test_invalid_family_data_rejected(self):
        r=self.approx['records'][0]
        for v in (-1,0.5,True):
            with self.assertRaises(ValueError):factor(r,v)
        bad=copy.deepcopy(r);bad['approximants'].pop()
        with self.assertRaises(ValueError):factor(bad,1)
        bad=copy.deepcopy(r);bad['weighted_monomial_norm_upper'].pop('34')
        with self.assertRaises(ValueError):factor(bad,1)

    def test_clock_contract_and_false_derivative_rejected(self):
        c=self.approx['clock_and_derivative']
        self.assertTrue(check_clock(c)['verified'])
        for key,value in [('complete_signal_derivative_upper','1'),('clock_slope_radius','0'),('complete_clock_distortion_radius','0')]:
            bad=copy.deepcopy(c);bad[key]=value
            with self.assertRaises(ValueError):check_clock(bad)

    def test_inexact_metadata_rejected_before_numeric_validation(self):
        for key,value in [('measurement_count',8900.0),('tested_degrees',[6.0,8,10,12]),('even_taylor_cutoff',32.0)]:
            bad=copy.deepcopy(self.approx);bad[key]=value
            with self.assertRaises(ValueError):check_document(bad)
        bad=copy.deepcopy(self.approx);bad['records'][0]['degree']=6.0
        with self.assertRaises(ValueError):check_document(bad)
        for bits in (True,384.0,0):
            with self.assertRaises(ValueError):check_document(self.approx,bits)
        bad=copy.deepcopy(self.approx['clock_and_derivative']);bad['sum_cutoff']=1000.0
        with self.assertRaises(ValueError):check_clock(bad)

    def test_affine_polynomial_closure_at_unbounded_scale(self):
        a=1+Q(1,10**14);b=Q(1,890*10**11)
        for p in (6,8,10,12):
            beta=[Q(10**100,k+1) for k in range(p+1)]
            composed=[sum((beta[k]*comb(k,j)*a**j*b**(k-j) for k in range(j,p+1)),Q()) for j in range(p+1)]
            for x in (Q(-1),Q(-7,13),Q(),Q(17,19),Q(1)):
                lhs=sum((v*(a*x+b)**k for k,v in enumerate(beta)),Q())
                rhs=sum((v*x**k for k,v in enumerate(composed)),Q())
                self.assertEqual(lhs,rhs)

    def test_nonaffine_jitter_leaks_linear_nuisance(self):
        eps=Q(1,10**20)
        for p in (6,8,10,12):
            # The (p+1)th divided finite difference annihilates every p-degree
            # nominal polynomial but detects one tiny acquisition-time spike.
            for amplitude in (Q(1),Q(10**40)):
                samples=[amplitude*(Q(j)+eps*(j==0)) for j in range(p+2)]
                difference=sum(((-1)**(p+1-j)*comb(p+1,j)*v for j,v in enumerate(samples)),Q())
                self.assertEqual(abs(difference),amplitude*eps)

    def test_complete_budget_controls(self):
        for design in ('multi','outer'):
            r=next(r for r in self.approx['records'] if r['design']==design and r['degree']==12)
            prior=next(r for r in self.prior['designs'][design]['degrees'] if r['degree']==12)
            saved=json.loads((HERE/('result_'+design+'_12.json')).read_text())
            rho=Q(saved['certificate']['normal_residual_upper'])
            good=profile(prior,r,rho,3,4000,self.clock)
            self.assertTrue(good['all_49_strict_rounding_gates'])
            self.assertFalse(profile(prior,r,rho,3,10000,self.clock)['all_49_strict_rounding_gates'])
            self.assertFalse(profile(prior,r,Q(1,100),3,4000,self.clock)['all_49_strict_rounding_gates'])
            self.assertFalse(profile(prior,r,rho,3,4000,Q(1,1000))['all_49_strict_rounding_gates'])

    def test_separate_mismatch_not_inferred_from_residual(self):
        r=self.approx['records'][-1]
        prior=self.prior['designs']['outer']['degrees'][-1]
        good=profile(prior,r,Q(),3,4000,self.clock)
        bad=profile(prior,r,Q(),3,4000,self.clock,mismatch=Q(1,1000))
        self.assertTrue(good['all_49_strict_rounding_gates'])
        self.assertFalse(bad['all_49_strict_rounding_gates'])


if __name__=='__main__':unittest.main()
