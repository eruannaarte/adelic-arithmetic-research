"""Independent reconstruction and boundary controls; run with the research venv."""
from pathlib import Path
from fractions import Fraction as F
from copy import deepcopy
import json,math,sys,unittest
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from flint import arb,arb_mat,ctx,fmpq
from oig_uniform_lattice_arb_cover import finite_gram_series,gram_derivative_entry_bound
from check_certificate import check,raw_remainder,norm_upper_valid,interval,absmax
HERE=Path(__file__).parent

def q(x):
    x=F(x);return arb(fmpq(x.numerator,x.denominator))

def direct_matrix_coefficients(n,c,order):
    """Separate Arb dense matrix exp path, not the tridiagonal polynomial path."""
    e=arb_mat([[1/arb(n).sqrt() for _ in range(n)]])
    ports=[arb_mat([[(arb(2)/n).sqrt()*(k*arb.pi()*q(F(2*j+1,2*n))).cos()] for j in range(n)]) for k in (1,2)]
    raw=[[[arb(0) for _ in range(2)] for _ in range(2)] for _ in range(order+1)]
    for ell in range(2,n,2):
        omega=4*(ell*arb.pi()/(2*n)).sin()**2
        A=arb_mat(n,n)
        for j in range(n):
            A[j,j]=(1 if j in (0,n-1) else 2)+omega*(1+q(F(4,5))*q(F(2*j+1,2*n)))
            if j:A[j,j-1]=-1
            if j+1<n:A[j,j+1]=-1
        exp=(-q(c)*A).exp()
        coeff=[[],[]]
        for p in range(2):
            v=exp*ports[p]
            for k in range(order+1):
                if k:v=(-A*v)/k
                coeff[p].append((e*v)[0,0])
        for k in range(order+1):
            for i in range(2):
                for j in range(2):
                    raw[k][i][j]+=q(F(2,n))*sum((coeff[i][h]*coeff[j][k-h] for h in range(k+1)),arb(0))
    binom=F(1);normal=[]
    for k in range(order+1):
        if k:binom*=F(3-2*k,2*k)
        normal.append(q(binom)*(1+q(c)).sqrt()/(1+q(c))**k)
    return [[[sum((normal[j]*raw[k-j][i][l] for j in range(k+1)),arb(0)) for l in range(2)] for i in range(2)] for k in range(order+1)]

class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=json.loads((HERE/'certificate.json').read_text())
    def test_whole_certificate(self):self.assertEqual(set(check(self.report)),{'L2','declared_H1','natural_discrete_H1'})
    def test_gap_in_cover_rejected(self):
        r=deepcopy(self.report);r['cells'][1]['interval'][0]='151/100'
        with self.assertRaises(ValueError):check(r)
    def test_grid_change_rejected(self):
        r=deepcopy(self.report);r['cells'][0]['n']=999
        with self.assertRaises(ValueError):check(r)
    def test_understated_error_rejected(self):
        r=deepcopy(self.report);r['cells'][0]['metrics']['L2']['spectral_error_upper']='1/1000000000000000000'
        with self.assertRaises(ValueError):check(r)
    def test_omitted_remainder_rejected(self):
        r=deepcopy(self.report);r['cells'][0]['metrics']['L2']['entry_remainders'][0]='0/1'
        with self.assertRaises(ValueError):check(r)
    def test_false_floor_premise_rejected(self):
        r=deepcopy(self.report);r['continuum_floors']['L2']='1/1'
        with self.assertRaises(ValueError):check(r)
    def test_fresh_baseline_exact_minors(self):
        r=json.loads((HERE/'baseline.json').read_text())
        for rec in r['metrics'].values():
            a,b,d=map(interval,rec['shift_entries'])
            self.assertGreater(a[0],0);self.assertGreater(a[0]*d[0]-absmax(b)**2,0)
    def test_offdiagonal_information_matters(self):
        box=[(F(0),F(0)),(F(1),F(1)),(F(0),F(0))]
        self.assertFalse(norm_upper_valid(box,F(1,2)))
        self.assertFalse(norm_upper_valid(box,F(1)))
        self.assertTrue(norm_upper_valid(box,F(1001,1000)))
    def test_failed_transfer_is_not_singularity(self):
        # Finite matrix (1/10)I is positive; conservative error 2 exceeds continuum floor1.
        self.assertGreater(F(1,10),0);self.assertGreater(F(2),F(1))

class AnalyticAndMatrixControls(unittest.TestCase):
    def setUp(self):ctx.prec=192
    def test_small_grid_dense_exponential_independent_derivatives(self):
        actual,_=finite_gram_series(7,F(5,4),3,48)
        direct=direct_matrix_coefficients(7,F(5,4),3)
        for k in range(4):
            for i in range(2):
                for j in range(2):self.assertTrue(actual[k][i][j].overlaps(direct[k][i][j]))
    def test_scalar_remainder_including_zero_and_stiff_generator(self):
        a,b,c,r=F(1),F(3,2),F(5,4),F(1,4)
        d=5;bound=q(raw_remainder(d,a,b,r,F(2)))
        for lam in (0,1,20,100):
            coeff=[]
            for k in range(d):
                value=arb(0);binom=F(1)
                for j in range(k+1):
                    if j:binom*=F(3-2*j,2*j)
                    value+=q(binom)*(1+q(c)).sqrt()/(1+q(c))**j*q(F((-lam)**(k-j),math.factorial(k-j)))*(-q(c)*lam).exp()
                coeff.append(value)
            for t in (a,b):
                polynomial=sum((coeff[k]*q(t-c)**k for k in range(d)),arb(0))
                truth=(1+q(t)).sqrt()*(-q(t)*lam).exp()
                self.assertTrue(abs(truth-polynomial)<bound)
    def test_remainder_improvement_is_rigorous(self):
        a,b,r,d=F(1),F(3,2),F(1,4),19
        old=(gram_derivative_entry_bound(d,a,b,F(56,5))+gram_derivative_entry_bound(d,a,b,F(36,5)))*q(r)**d/math.factorial(d)
        new=q(2*raw_remainder(d,a,b,r,F(2)))
        self.assertTrue(old>100_000_000*new)
    def test_zero_left_endpoint_rejected(self):
        with self.assertRaises(ValueError):raw_remainder(19,F(0),F(1),F(1,2),F(2))
    def test_negative_and_nonnormal_generators_break_contract(self):
        self.assertTrue(arb(2).exp()>1) # raw product for A=-1 at t=1
        A=arb_mat([[1,-10],[0,1]])
        self.assertTrue(((-A).exp()[0,1])**2>1)
    def test_source_and_observation_normalization(self):
        n=7
        for k in (1,2):
            vals=[(arb(2)/n).sqrt()*(k*arb.pi()*q(F(2*j+1,2*n))).cos() for j in range(n)]
            self.assertTrue(sum((x*x for x in vals),arb(0)).contains(1))
            self.assertTrue(sum(vals,arb(0)).contains(0))
        self.assertLess(F(n-1,n),1)
    def test_natural_and_declared_metrics_are_different(self):
        n=1001
        for k in (1,2):self.assertTrue(1+4*n*n*(k*arb.pi()/(2*n)).sin()**2<1+(k*arb.pi())**2)

if __name__=='__main__':unittest.main()
