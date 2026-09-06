import copy,json,unittest
from fractions import Fraction as Q
from pathlib import Path
import checker as ch
import synthesize,calibration
from test_preparation import replay
HERE=Path(__file__).resolve().parent
load=lambda f:json.loads((HERE/f).read_text())

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=load('cycle2_region.json');cls.n=load('nominal.json');cls.c=load('cycle2_certificate.json')
    def test_source_replay(self):replay(self.r)
    def test_frozen_fixed_decoder_certificate(self):
        self.assertTrue(synthesize.verify(self.r,self.n,self.c))
        self.assertEqual(calibration.build(self.r,self.n,self.c),load('cycle2_calibration.json'))
        for d in self.c['designs'].values():self.assertFalse(d['target_passes'])
        for d in load('cycle2_calibration.json')['designs'].values():
            self.assertTrue(d['synthesized']['revised_target_passes']);self.assertFalse(d['least_squares']['revised_target_passes'])
    def test_boundary_both_sides(self):
        for design in load('cycle2_calibration.json')['designs'].values():
            for d in design.values():
                rho=Q(d['maximum_preparation_radius']);eta=Q(d['noise']);delta=Q(d['target'])
                k=list(map(Q,d['row_contraction']));h=list(map(Q,d['preparation_gain']));c=list(map(Q,d['noise_gain']))
                lhs=lambda x:[delta*ki+2*(x*hi+eta*ci) for ki,hi,ci in zip(k,h,c)]
                self.assertTrue(all(x<=delta for x in lhs(rho)));self.assertTrue(any(x>delta for x in lhs(rho+Q(1,10**12))))
    def test_invalid_decoder_and_source_bindings(self):
        bad=copy.deepcopy(self.c);b=bad['designs']['selected_AB']['ingredients']['b'];b[0][0]=str(Q(b[0][0])+Q(1,10**8))
        with self.assertRaises(ValueError):synthesize.verify(self.r,self.n,bad)
        bad=copy.deepcopy(self.c);bad['rho']='1/100'
        with self.assertRaises(ValueError):synthesize.verify(self.r,self.n,bad)
        bad=copy.deepcopy(self.c);bad['designs']['selected_AB']['shares']=['1/2','1/2','0']
        with self.assertRaises(ValueError):synthesize.verify(self.r,self.n,bad)
    def test_nominal_preparation_derivative_is_insufficient(self):
        f=lambda s,p:s+s*p
        self.assertEqual(f(Q(2,5),0),f(Q(8,25),Q(1,4)))
        self.assertNotEqual(Q(2,5),Q(8,25))
        self.assertEqual(Q(0),0) # D_p f at s=0
    def test_row_gate_can_improve_worst_row_gate(self):
        # Valid diagonal linear comparison: the worst k and worst forcing occur in different rows.
        R=[[Q(9,10),Q(0)],[Q(0),Q(0)]];v=[Q(1,10),Q(1)]
        self.assertTrue(all(sum(r)+vi<=1 for r,vi in zip(R,v)))
        self.assertEqual(max(v)/(1-max(map(sum,R))),10)
        x=ch.matmul(ch.inverse([[1-R[0][0],0],[0,1]]),[[v[0]],[v[1]]])
        self.assertEqual(x,[[1],[1]])

if __name__=='__main__':unittest.main(verbosity=2)
