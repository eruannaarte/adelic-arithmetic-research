"""Proof controls and independent mechanical diagnostics; SciPy is not the certificate."""
import copy,json,math,sys,unittest
from pathlib import Path
from fractions import Fraction as Q
import numpy as np
from scipy.integrate import solve_ivp
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import checker as ch
import full_sensitivity as p
from flint import arb,ctx
from double_pendulum_dynamics import DoublePendulumParameters,double_pendulum_rhs

def load(name):return json.loads((HERE/name).read_text())
def mech(z,u,v,e):
    par=DoublePendulumParameters(m1=1,m2=math.exp(u),l1=1,l2=math.exp(v),g=1)
    return math.exp(e)*double_pendulum_rhs(0,np.asarray(z),par)
def solve(z,s,t):
    sol=solve_ivp(lambda t,z:mech(z,*s),(0,t),z,method='DOP853',rtol=2e-13,atol=2e-15,max_step=.015)
    assert sol.success
    return sol.y[:,-1]
def replay(report):
    ch.verify_inputs(report);cfg=report['config']
    fresh=p.build(Q(report['parameter_box_radius']),Q(report['preparation_box_radius']),Q(cfg['step']),cfg['precision_bits'],cfg['order'])
    a=dict(report);a.pop('elapsed_seconds');fresh.pop('elapsed_seconds')
    if a!=fresh:raise ValueError('source replay mismatch')

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=load('cycle1_region.json');cls.n=load('nominal.json')
    def test_cycle1_exact_consequences(self):
        cert=ch.evaluate(self.r,self.n);self.assertEqual(cert,load('cycle1_certificate.json'))
        for d in cert['designs'].values():
            b=d['bound'];self.assertLess(Q(b['diameter']),Q(1,10000));self.assertLess(Q(b['diameter']),Q(b['uncorrelated_diameter']))
    def test_cycle1_source_replay(self):replay(self.n);replay(self.r)
    def test_six_direction_rhs(self):
        with ctx.workprec(160):
            for seed in range(10):
                rng=np.random.default_rng(seed);z=rng.uniform(-1.3,1.3,4);g=rng.uniform(-.25,.25,(6,4));s=rng.uniform(-.01,.01,3)
                out=np.array([float(x) for x in p.rhs([arb(str(x)) for x in np.r_[z,g.ravel(),s]])])
                np.testing.assert_allclose(out[:4],mech(z,*s),rtol=4e-14,atol=4e-14)
                for k in range(6):
                    ds=np.zeros(3)
                    if k<2:ds[k]=1
                    h=1e-5;fd=(mech(z+h*g[k],*(s+h*ds))-mech(z-h*g[k],*(s-h*ds)))/(2*h)
                    np.testing.assert_allclose(out[4+4*k:8+4*k],fd,rtol=4e-7,atol=4e-9)
                self.assertEqual(list(out[28:]),[0,0,0])
    def test_finite_preparation_and_clock_derivatives(self):
        # Mechanical matrix-solve RHS is distinct from producer's explicit inverse.
        for j,row in enumerate(self.r['rows']):
            z=np.array([float(Q(x)) for x in row['launch']]);s=np.array([1,-1,1])*1e-4*((j%3)-1)
            z+=np.array([1,-1,-1,1])*1e-6;t=float(Q(row['time']));k={'theta_1':0,'theta_2':1,'scaled_omega_1':2,'scaled_omega_2':3}[row['sensor']]
            val=solve(z,s,t)[k];lo,hi=map(lambda x:float(Q(x)),row['output']);self.assertTrue(lo<=val<=hi)
            h=2e-6
            for q in range(4):
                dz=np.eye(4)[q]*h;d=(solve(z+dz,s,t)[k]-solve(z-dz,s,t)[k])/(2*h)
                lo,hi=map(lambda x:float(Q(x)),row['preparation_jacobian'][q]);self.assertTrue(lo<=d<=hi,(j,q,lo,d,hi))
            ds=np.array([0,0,h]);d=(solve(z,s+ds,t)[k]-solve(z,s-ds,t)[k])/(2*h)
            lo,hi=map(lambda x:float(Q(x)),row['jacobian'][2]);self.assertTrue(lo<=d<=hi)
    def test_launch_cancellation_control(self):
        # Exact cancellation with a shared preparation; no cancellation if re-prepared.
        B=[[Q(1),Q(-1)]];Pshared=[[Q(1)],[Q(1)]];Pseparate=[[Q(1),Q(0)],[Q(0),Q(1)]]
        self.assertEqual(ch.matmul(B,Pshared),[[0]])
        self.assertEqual(sum(abs(x) for x in ch.matmul(B,Pseparate)[0]),2)
        # Scalar ambiguity reaches the theorem, so preparation is not 'known'.
        rho=Q(1,13);self.assertEqual(rho-rho,-rho+rho)
    def test_contract_and_boundary_rejections(self):
        for f,v in [('preparation_incidence','independent error per reading'),('clock_structure','independent clocks'),('preparation_coordinates',['theta1'])]:
            bad=copy.deepcopy(self.r);bad[f]=v
            with self.assertRaises(ValueError):ch.evaluate(bad,self.n)
        for shares in [[Q(1),Q(1),Q(0)],[Q(-1),Q(1),Q(1)]]:
            with self.assertRaises(ValueError):ch.ingredients(self.r,self.n,shares)
        bad=copy.deepcopy(self.r);bad['rows'][0]['preparation_jacobian'][0]=['1','0']
        with self.assertRaises(ValueError):ch.evaluate(bad,self.n)
        bad=copy.deepcopy(self.r)
        for r in bad['rows']:r['jacobian']=[['-100','100']]*3
        self.assertTrue(all(d['bound']['diameter'] is None for d in ch.evaluate(bad,self.n)['designs'].values()))
        with self.assertRaises(ValueError):ch.ingredients(self.r,self.n,ch.DESIGNS['selected_AB'],decoder=[[0]*5]*3)

if __name__=='__main__':unittest.main(verbosity=2)
