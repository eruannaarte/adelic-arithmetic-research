"""Meaningful exact/model and boundary controls for adaptive harmonic cycles."""
from fractions import Fraction as Q
from copy import deepcopy
from itertools import combinations,product
from math import prod
import cmath,math,unittest
import cycle1 as c1
import cycle2 as c2
import cycle3 as c3
from flint import arb,acb,ctx

class Cycle1Tests(unittest.TestCase):
    def test_full_reconstruction_and_precision(self):
        self.assertEqual(c1.check(),c1.build(384))

    def test_independent_all_vertex_pairs(self):
        # Independent enumeration of actual sources, not difference vectors.
        vertices=list(product(range(4),repeat=3));best={1:None,2:None,3:None}
        for a,b in combinations(vertices,2):
            x=prod(p**v for p,v in zip((2,3,5),a));y=prod(p**v for p,v in zip((2,3,5),b))
            k=sum(x!=y for x,y in zip(a,b));r=Q(max(x,y),min(x,y))
            best[k]=r if best[k] is None else min(best[k],r)
        self.assertEqual(best,{1:Q(2),2:Q(27,25),3:Q(25,24)})
        self.assertEqual({k:Q(v['minimum_ratio']) for k,v in c1.classify().items()}, {str(k):v for k,v in best.items()})

    def test_raw_model_pair_identity_and_universal_cap(self):
        a=(0,0,2);b=(3,1,0);delta=math.log(25/24)
        def response(v,t):return prod(cmath.exp(-1j*t*k*math.log(p)) for k,p in zip(v,(2,3,5)))
        for t in (0,.1,1,10,20):
            self.assertAlmostEqual(abs(response(a,t)-response(b,t)),2*abs(math.sin(t*delta/2)),places=12)
        for seed in range(20):
            tt=[20*((seed+1)*(j+3)%97)/97 for j in range(6)]
            raw=math.sqrt(sum(abs(response(a,t)-response(b,t))**2 for t in tt))/math.sqrt(6)
            self.assertLessEqual(raw,2*math.sin(10*delta)+1e-12)

    def test_necessary_not_sufficient_and_domain_boundaries(self):
        # Universal horizon cap at T=55 exceeds target, yet this legal six-time
        # schedule is exactly blind to the first factor by the analytic identity.
        self.assertGreater(2*math.sin(55*math.log(25/24)/2),.815)
        times=[2*math.pi*j/math.log(2) for j in range(1,7)]
        self.assertLess(max(times),55)
        self.assertTrue(all(abs(cmath.exp(-1j*t*math.log(2))-1)<1e-13 for t in times))
        self.assertTrue(c1.time_bound(0,3,Q(25,24)).contains(0))
        for c,k,ratio,m in ((-1,3,Q(25,24),6),(3,3,Q(25,24),6),(1,0,Q(2),6),(1,1,Q(1),6),(1,1,Q(2),0)):
            with self.assertRaises(ValueError):c1.time_bound(c,k,ratio,m)

class Cycle2Tests(unittest.TestCase):
    def test_complete_dual_cover_and_vertex_replay(self):
        self.assertEqual(c2.check(),c2.build(384))

    def test_independent_raw_all_2016_pairs(self):
        d=c2.check()['short_vertex_schedule'];floor=float(Q(d['floor_lower']))
        vertices=list(product(range(4),repeat=3));times=list(map(float,c2.TIMES))
        readings={v:[prod(cmath.exp(-1j*t*a*math.log(p)) for p,a in zip((2,3,5),v)) for t in times] for v in vertices}
        found=10.
        for a,b in combinations(vertices,2):
            k=sum(x!=y for x,y in zip(a,b))
            f=math.sqrt(sum(abs(x-y)**2 for x,y in zip(readings[a],readings[b]))/(2*k))
            found=min(found,f)
            self.assertGreater(f+1e-11,floor)
        self.assertLess(found,1.034);self.assertGreater(found,1.033)

    def test_different_dual_majorant_and_grid_check(self):
        # Center values plus a global Lipschitz allowance independently upper
        # bound every time cell, without interval cosine evaluation on a box.
        target=.815**2/6;T=float(c2.HORIZON);N=30000
        L=sum(float(w)*math.log(float(r))/k for r,k,w in c2.DUAL)
        maximum=max(sum(float(w)*(1-math.cos((i+.5)*T/N*math.log(float(r))))/k for r,k,w in c2.DUAL) for i in range(N))
        self.assertLess(maximum+L*T/(2*N)+1e-13,target)

    def test_dual_and_design_negative_domains(self):
        for weights in (((Q(25,24),3,Q(-1)),),((Q(25,24),3,Q(1,2)),),((Q(1),3,Q(1)),),((Q(7,6),3,Q(1)),),((Q(25,24),2,Q(1)),)):
            with self.assertRaises(ValueError):c2.dual_upper(weights=weights)
        with self.assertRaises(ValueError):c2.vertex_certificate([0]*6)
        blind=tuple(Q(i) for i in range(6))
        self.assertFalse(c2.vertex_certificate(blind)['passes'])

class Cycle3Tests(unittest.TestCase):
    def test_complete_interval_existence_and_refinement(self):
        self.assertTrue(c3.check()['strict_gates_pass'])
        self.assertTrue(c3.check(384)['strict_gates_pass'])

    def test_independent_full_integer_label_expansion(self):
        d=c3.check();x=[c1.ball(Q(v)) for v in d['inputs']['coordinates']]
        with ctx.workprec(192):
            q,r=c3.sources(x);E=c3.coefficients();F,_=c3.response_and_jacobian(x,E,d['inputs']['active'])
            for it,t in enumerate(c2.TIMES):
                expanded=acb(0)
                for a in product(range(4),repeat=3):
                    label=prod(p**v for p,v in zip((2,3,5),a))
                    phase=acb(0,-c1.ball(t)*arb(label).log()).exp()
                    amplitude=q[0][a[0]]*q[1][a[1]]*q[2][a[2]]-r[0][a[0]]*r[1][a[1]]*r[2][a[2]]
                    expanded+=amplitude*phase
                self.assertTrue((expanded.real-F[it]).contains(0))
                self.assertTrue((expanded.imag-F[it+6]).contains(0))

    def test_jacobian_against_independent_finite_difference(self):
        d=c3.check();active=d['inputs']['active'];x=list(map(lambda s:c1.ball(Q(s)),d['inputs']['coordinates']));E=c3.coefficients()
        _,J=c3.response_and_jacobian(x,E,active);h=Q(1,10**6)
        for column,index in enumerate(active):
            xp=x.copy();xm=x.copy();xp[index]+=c1.ball(h);xm[index]-=c1.ball(h)
            fp,_=c3.response_and_jacobian(xp,E,active);fm,_=c3.response_and_jacobian(xm,E,active)
            # In one source coordinate this multilinear response is affine;
            # this centered difference is exact analytically, not asymptotic.
            for i in range(12):self.assertTrue(((fp[i]-fm[i])/(2*c1.ball(h))-J[i][column]).contains(0))

    def test_interval_domains_and_adversarial_claims(self):
        inp=c3.check()['inputs']
        for field,val in (('radius','-1'),('active',[0]*12),('minimum_probability_claim','1/4'),('separation_claim','1'),('radius','1/100')):
            bad=deepcopy(inp);bad[field]=val
            with self.assertRaises(ValueError):c3.build(bad)
        bad=deepcopy(inp);bad['times'][0]='0'
        with self.assertRaises(ValueError):c3.build(bad)

    def test_exact_contraction_and_separation_consequences(self):
        d=c3.check();L=Q(d['contraction_norm_upper']);e=Q(d['preconditioned_residual_upper']);rho=Q(d['box_radius'])
        self.assertLess(L,1);self.assertLess(e+L*rho,rho)
        self.assertGreater(Q(d['minimum_probability_lower']),Q(7,100))
        self.assertGreater(Q(d['factor_distance_squared_lower']),Q(79,100)**2)

if __name__=='__main__':unittest.main(verbosity=2)
