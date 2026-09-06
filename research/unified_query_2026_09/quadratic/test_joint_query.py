from copy import deepcopy
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import importlib.util
import json
import sys
import unittest
import numpy as np
import joint_query as j

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from arithmetic_sensing_iv import REFERENCE_COEFFICIENTS
spec=importlib.util.spec_from_file_location('_joint_geometry',ROOT/'research/next15_2026_09/quadratic/geometry.py')
geometry=importlib.util.module_from_spec(spec);spec.loader.exec_module(geometry)


class JointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cert=json.loads((Path(__file__).parent/'certificate.json').read_text())

    def test_exact_pair_and_template_coverage(self):
        self.assertTrue(j.check(self.cert)['verified'])
        self.assertEqual(j.INDICES,(5,7,10,14,15,20,21,25,28,30,35,40,42,45,49,50))
        for row in self.cert['strata']:
            self.assertEqual(len(row['pairs']),27)
            pairs={(p['i'],p['j']) for p in row['pairs']}
            self.assertEqual(pairs,{(i,k) for i in range(9) for k in range(i+1,9) if i//3!=k//3})

    def test_independent_actual_arithmetic_prefixes_and_decoding(self):
        for row in self.cert['strata']:
            for v,g in zip(row['templates'],row['guarantees']):
                signs={p:-1 for p in geometry.PRIMES}
                signs.update({2:row['a2']-1,3:row['a3']-1,5:v['a5']-1,7:v['a7']-1})
                coefficients=geometry.prefix(signs)
                self.assertEqual([coefficients[n-1] for n in j.INDICES],v['coefficients'])
                self.assertEqual(j.decode(coefficients,F(g['declared_eta']),self.cert),v['a5'])

    def test_exact_margins_gains_and_unimproved_worst_case(self):
        for row in self.cert['strata']:
            for g in row['guarantees']:
                eta=F(g['declared_eta']);r2=F(g['radius_squared_sufficient'])
                self.assertLess(eta**2,min(r2,F(self.cert['anchor_radius_squared'])))
                self.assertGreaterEqual(F(g['gain_squared_over_Q3']),1)
            # With a7 inert, q0 and q1 have exactly the original Q3 boundary.
            for i in (0,3):self.assertEqual(F(row['guarantees'][i]['gain_squared_over_Q3']),1)
        largest=self.cert['strata'][0]['guarantees'][8]
        self.assertGreater(F(largest['gain_squared_over_Q3']),F(1004,1000)**2)
        self.assertEqual(F(self.cert['strata'][8]['guarantees'][8]['declared_eta']),F(233281,10**7))

    def test_actual_reused_grid_covariance_and_query_noise(self):
        m=8900;t=(2*np.arange(m)+1-m)/10
        def window(n):
            angle=np.pi*(2*np.arange(n)+1)/n
            return (1+2*sum(float(c)*np.cos(k*angle) for k,c in enumerate(REFERENCE_COEFFICIENTS,1)))/n
        outer=window(m);inner=np.zeros(m);inner[3175:5725]=window(2550)
        w=(125*inner+65411*outer)/65536
        Phi=np.exp(-1j*t[:,None]*np.log(np.arange(1,51))[None,:])
        G=Phi.conj().T@(w[:,None]*Phi)
        A=np.linalg.solve(G,Phi.conj().T*w)
        n2=np.arange(1,51,dtype=float)**2
        q=float(F(self.cert['gram_q']))
        for row in (self.cert['strata'][0],self.cert['strata'][4],self.cert['strata'][8]):
            for index in (2,5,8):
                v=row['templates'][index];g=row['guarantees'][index]
                near=[p for p in row['pairs'] if index in (p['i'],p['j'])]
                pair=min(near,key=lambda p:F(p['radius_squared_sufficient']))
                direction=np.zeros(50);direction[np.array(j.INDICES)-1]=[float(F(x)) for x in pair['delta']]
                raw=direction@A;gain=np.sqrt(np.sum(np.abs(raw)**2/w))
                self.assertLessEqual(gain,np.sqrt(float(F(pair['squared_distance']))/(1-q)))
                eta=F(g['declared_eta']);eps=float(eta)*raw.conj()/w/gain
                self.assertAlmostEqual(np.sqrt(np.sum(w*np.abs(eps)**2)),float(eta),places=13)
                signs={p:-1 for p in geometry.PRIMES};signs.update({2:row['a2']-1,3:row['a3']-1,5:v['a5']-1,7:v['a7']-1})
                source=np.array(geometry.prefix(signs),float)
                # Finite-part operator diagnostic; complete field tails remain in the theorem.
                estimate=n2*(A@(Phi@(source/n2)+eps))
                self.assertEqual(j.decode(list(map(complex,estimate)),eta,self.cert),v['a5'])

    def test_ambiguity_and_anchor_abstention(self):
        row=self.cert['strata'][0]
        a=[F(0)]*50;b=[F(0)]*50
        for n,x,y in zip(j.INDICES,row['templates'][0]['coefficients'],row['templates'][3]['coefficients']):
            a[n-1]=F(x);b[n-1]=F(y)
        midpoint=[(x+y)/2 for x,y in zip(a,b)]
        answers=j.answer_set(midpoint,F(201,10000),self.cert)
        self.assertTrue({0,1}.issubset(answers));self.assertIsNone(j.decode(midpoint,F(201,10000),self.cert))
        self.assertIsNone(j.answer_set(a,1,self.cert))

    def test_numerical_error_is_charged_and_invalid_inputs_rejected(self):
        signs={p:-1 for p in geometry.PRIMES};signs[5]=1
        a=list(map(F,geometry.prefix(signs)))
        error=[F(0)]*50;error[4]=F(1,100)
        approximate=a.copy();approximate[4]+=error[4]
        self.assertEqual(j.decode(approximate,F(1,100),self.cert,error),2)
        error[1]=1
        self.assertIsNone(j.decode(approximate,F(1,100),self.cert,error))
        for bad in ([-1]*50,[0]*49):
            with self.assertRaises(ValueError):j.decode(a,0,self.cert,bad)
        with self.assertRaises(ValueError):j.decode(a,-1,self.cert)

    def test_direct_decode_rejects_forged_certificates(self):
        for field in ('coverage','nonlinear','tail','radius','metric','type'):
            bad=deepcopy(self.cert)
            if field=='coverage':bad['strata'][0]['pairs'].pop()
            elif field=='nonlinear':bad['strata'][0]['templates'][8]['coefficients'][j.INDICES.index(25)]=1
            elif field=='tail':bad['normalized_tail_bias'][0]='0'
            elif field=='radius':bad['strata'][0]['guarantees'][0]['declared_eta']='1'
            elif field=='type':bad['strata'][0]['templates'][0]['a5']=False
            else:bad['noise_metric']='independent decoded coefficients'
            with self.assertRaises(ValueError):j.decode([0]*50,0,bad)


if __name__=='__main__':unittest.main(verbosity=2)
