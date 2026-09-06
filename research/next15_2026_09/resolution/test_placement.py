"""Independent exact graph-walk and dense semigroup controls."""
from fractions import Fraction as Q
from copy import deepcopy
from pathlib import Path
import json,unittest
from flint import fmpq,fmpq_mat,arb,arb_mat,ctx
from placement import build,placement_bound
from check_placement import check


def graph(nx=2,ny=11):
    size=ny*nx*nx
    A=fmpq_mat(size,size)
    def idx(y,a,b):return y*nx*nx+a*nx+b
    def edge(i,j,w):
        A[i,i]+=w;A[j,j]+=w;A[i,j]-=w;A[j,i]-=w
    for y in range(ny):
        for a in range(nx):
            for b in range(nx):
                i=idx(y,a,b)
                if a+1<nx:edge(i,idx(y,a+1,b),fmpq(1))
                if b+1<nx:edge(i,idx(y,a,b+1),fmpq(1))
                if y+1<ny:
                    w=2+fmpq(4,5)*(fmpq(2*a+1,2*nx)+fmpq(2*b+1,2*nx))
                    edge(i,idx(y+1,a,b),w)
    return A


class PlacementTests(unittest.TestCase):
    def test_exact_certificate_and_threshold(self):
        c=build();self.assertTrue(check(c));self.assertEqual(c['depth'],41)
        with self.assertRaises(AssertionError):
            d=deepcopy(c);d['matrix_error_upper']='0';check(d)
        self.assertGreater(placement_bound(40),min(Q(r['central_floor']) for r in c['metrics'].values())/100)

    def test_locality_moments_and_boundary_counterexample(self):
        A=graph();size=A.nrows();P=fmpq_mat(size,size)
        for i in range(size):
            for j in range(size):P[i,j]=(1 if i==j else 0)-A[i,j]/fmpq(56,5)
        self.assertTrue(all(P[i,j]>=0 for i in range(size) for j in range(size)))
        self.assertTrue(all(sum(P[i,j] for j in range(size))==1 for i in range(size)))
        R=fmpq_mat(size,size)
        for i in range(size):R[i,i]=1
        for k in range(6):
            equal=all(R[8+a,8+b]==R[20+a,20+b] for a in range(4) for b in range(4))
            self.assertEqual(equal,k<=4)
            R=R*P
        self.assertTrue(any(P[a,b]!=P[20+a,20+b] for a in range(4) for b in range(4)))

    def test_dense_arb_exponential(self):
        ctx.prec=192;A=graph();size=A.nrows();M=arb_mat(size,size)
        for i in range(size):
            for j in range(size):M[i,j]=-arb(A[i,j])/10
        H=M.exp();bound=placement_bound(2,Q(1,10))/4
        # Production error includes 2 ports and normalization2; divide by4
        # for the raw per-entry semigroup block bound tested here.
        for a in range(4):
            for b in range(4):self.assertTrue(abs(H[8+a,8+b]-H[20+a,20+b])<arb(fmpq(bound.numerator,bound.denominator)))

    def test_invalid_domains(self):
        for d,t in [(-1,Q(2)),(0,Q(2)),(41,Q(-1))]:
            with self.assertRaises(ValueError):placement_bound(d,t)


if __name__=='__main__':unittest.main()
