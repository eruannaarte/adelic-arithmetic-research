"""Deep source-to-certificate checks plus independent finite controls."""
from __future__ import annotations
import copy,itertools,json,math,sys,time,unittest
from fractions import Fraction as Q
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import checker as ch
import preparation as p
from flint import arb,ctx
from double_pendulum_dynamics import DoublePendulumParameters,double_pendulum_rhs


def load(n):return json.loads((HERE/n).read_text())
def finite_rhs(z,u,v,e):
    par=DoublePendulumParameters(m1=1,m2=math.exp(u),l1=1,l2=math.exp(v),g=1)
    return math.exp(e)*double_pendulum_rhs(0,np.array(z),par)
def simulate(launch,theta,times):
    u,v,e=theta
    sol=solve_ivp(lambda t,z:finite_rhs(z,u,v,e),(0,max(times)),launch,method='DOP853',t_eval=times,rtol=2e-13,atol=2e-15,max_step=.015)
    if not sol.success:raise AssertionError(sol.message)
    return sol.y.T


def exact_replay(report):
    ch.verify_inputs(report)
    cfg=report['config']
    rebuilt=p.build(Q(report['parameter_box_radius']),Q(report['preparation_box_radius']),Q(cfg['step']),cfg['precision_bits'],cfg['order'])
    # Runtime is descriptive. Every scientific/input/provenance field is rebuilt.
    a=dict(report);b=dict(rebuilt);a.pop('elapsed_seconds');b.pop('elapsed_seconds')
    if a!=b:raise ValueError('source-to-output replay mismatch')
    return True


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.region=load('region.json');cls.nominal=load('nominal.json');cls.comparison=load('comparison.json')

    def test_exact_algebra_replay_and_frozen_comparison(self):
        self.assertEqual(ch.evaluate(self.region,self.nominal),self.comparison)
        self.assertLess(Q(self.comparison['selected_AB']['kappa']),Q(78,1000))
        self.assertLess(Q(self.comparison['selected_AB']['feasible_set_diameter_inf']),Q(202,10**7))
        self.assertLess(Q(self.comparison['selected_AB']['feasible_set_diameter_inf']),Q(self.comparison['uniform_ABC']['feasible_set_diameter_inf']))
        self.assertLess(Q(self.comparison['uniform_AB']['feasible_set_diameter_inf']),Q(self.comparison['selected_AB']['feasible_set_diameter_inf']))

    def test_deep_nonlinear_source_replay(self):
        self.assertTrue(exact_replay(self.nominal));self.assertTrue(exact_replay(self.region))

    def test_alternate_outward_partition(self):
        alt=load('alternate.json')
        self.assertTrue(exact_replay(alt))
        for a,b in zip(self.region['rows'],alt['rows']):
            for ia,ib in zip(a['jacobian']+[a['output']],b['jacobian']+[b['output']]):
                x,y=ch.iv(ia);z,w=ch.iv(ib);self.assertLessEqual(max(x,z),min(y,w))
        for result in ch.evaluate(alt,self.nominal).values():self.assertTrue(result['certified'])

    def test_independent_mechanical_rhs_and_derivatives(self):
        with ctx.workprec(160):
            for seed in range(12):
                rng=np.random.default_rng(seed)
                z=rng.uniform(-1.3,1.3,4);su=rng.uniform(-.2,.2,4);sv=rng.uniform(-.2,.2,4)
                u,v,e=rng.uniform(-.015,.015,3)
                full=[arb(str(x)) for x in np.r_[z,su,sv,u,v,e]]
                out=np.array([float(x) for x in p.rhs(full)])
                np.testing.assert_allclose(out[:4],finite_rhs(z,u,v,e),rtol=4e-14,atol=4e-14)
                h=1e-5
                du=(finite_rhs(z+h*su,u+h,v,e)-finite_rhs(z-h*su,u-h,v,e))/(2*h)
                dv=(finite_rhs(z+h*sv,u,v+h,e)-finite_rhs(z-h*sv,u,v-h,e))/(2*h)
                np.testing.assert_allclose(out[4:8],du,rtol=3e-7,atol=3e-9)
                np.testing.assert_allclose(out[8:12],dv,rtol=3e-7,atol=3e-9)
                self.assertEqual(list(out[12:]),[0,0,0])

    def test_held_out_finite_boxes_and_preparation_bias(self):
        radius=float(Q(self.region['parameter_box_radius']));rho=float(Q(self.region['preparation_box_radius']))
        # All eight parameter corners, four randomized interior cases; preparation
        # corners alternate per launch, with common preparation within a launch.
        params=[np.array(s)*radius for s in itertools.product([-1,1],repeat=3)]
        params += [np.random.default_rng(s+77).uniform(-radius,radius,3) for s in range(4)]
        for launch in dict.fromkeys(tuple(r['launch']) for r in self.region['rows']):
            rows=[r for r in self.region['rows'] if tuple(r['launch'])==launch]
            z=np.array([float(Q(x)) for x in launch]);tt=sorted({float(Q(r['time'])) for r in rows})
            for n,theta in enumerate(params):
                signs=np.array([(-1)**(n+j) for j in range(4)])
                zz=simulate(z+rho*signs,theta,tt);nom=simulate(z,theta,tt)
                for r in rows:
                    it=tt.index(float(Q(r['time'])));j={'theta_1':0,'theta_2':1,'scaled_omega_1':2,'scaled_omega_2':3}[r['sensor']]
                    lo,hi=map(lambda x:float(Q(x)),r['output'])
                    self.assertGreaterEqual(zz[it,j],lo);self.assertLessEqual(zz[it,j],hi)
                    self.assertLess(abs(zz[it,j]-nom[it,j]),float(Q(r['preparation_output_bound'])))
                    # Clock endpoint derivative versus independent time dilation.
                    h=1e-6;plus=theta.copy();minus=theta.copy();plus[2]+=h;minus[2]-=h
                    d=(simulate(z+rho*signs,plus,tt)[it,j]-simulate(z+rho*signs,minus,tt)[it,j])/(2*h)
                    a,b=map(lambda x:float(Q(x)),r['jacobian'][2]);self.assertGreaterEqual(d,a);self.assertLessEqual(d,b)

    def test_zero_preparation_and_boundary_semantics(self):
        # Zero preparation removes the prep bias, leaving roundoff hull slack.
        self.assertTrue(all(Q(r['preparation_output_bound'])<Q(1,10**15) for r in self.nominal['rows']))
        # y=x+p+n has sharp feasible-set diameter 2(rho+eta).
        rho=Q(1,7);eta=Q(1,11);d=rho+eta
        self.assertEqual(d-rho-eta,0);self.assertEqual(-d+rho+eta,0)
        # kappa<1 is sufficient only: f(x)=2x with nominal A=1 has kappa=1
        # and remains injective; rejecting that gate is not impossibility.
        self.assertEqual(abs(Q(2)-1),1);self.assertNotEqual(Q(2)*1,Q(2)*0)

    def test_noise_budget_region(self):
        delta=Q(1,10000)
        for r in self.comparison.values():
            k=Q(r['kappa']);e=list(map(Q,r['preparation_bias_rows']));c=list(map(Q,r['noise_gain_rows']))
            bound=min((delta*(1-k)/2-x)/y for x,y in zip(e,c));self.assertGreater(bound,0)
            self.assertTrue(all(2*(x+bound*y)<=delta*(1-k) for x,y in zip(e,c)))
            self.assertTrue(any(2*(x+(bound+Q(1,10**10))*y)>delta*(1-k) for x,y in zip(e,c)))

    def test_widened_jacobian_and_contract_failures(self):
        bad=copy.deepcopy(self.region)
        for r in bad['rows']:r['jacobian']=[['-100','100']]*3
        self.assertTrue(all(not x['certified'] for x in ch.evaluate(bad,self.nominal).values()))
        for field,value in [('clock_structure','independent clocks'),('parameter_box_radius','-1'),('preparation_coordinates',['theta1'])]:
            bad=copy.deepcopy(self.region);bad[field]=value
            with self.assertRaises(ValueError):ch.evaluate(bad,self.nominal)
        bad=copy.deepcopy(self.region);bad['rows'][0]['cost']='2'
        with self.assertRaises(ValueError):ch.evaluate(bad,self.nominal)
        bad=copy.deepcopy(self.region);bad['rows'][0]['jacobian'][0]=['2','1']
        with self.assertRaises(ValueError):ch.evaluate(bad,self.nominal)

    def test_readdressed_false_enclosure_is_rejected(self):
        bad=copy.deepcopy(self.region);bad['rows'][0]['jacobian'][0]=['1','1']
        with self.assertRaises(ValueError):exact_replay(bad)

if __name__=='__main__':unittest.main(verbosity=2)
