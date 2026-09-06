"""Focused adversarial and model-connected controls (not proof substitutes)."""
from fractions import Fraction as Q
from pathlib import Path
import copy, importlib.util, json, sys, unittest
import numpy as np
from flint import arb, arb_mat, ctx
from check import check
HERE=Path(__file__).resolve().parent

def generator(nx,ny):
    N=nx*ny;H=[[Q(0) for _ in range(N)] for _ in range(N)]
    v=[1+Q(4,5)*Q(2*k+1,2*nx) for k in range(nx)]
    def edge(i,j,c):
        H[i][i]+=c;H[j][j]+=c;H[i][j]-=c;H[j][i]-=c
    for y in range(ny):
        for x in range(nx-1):edge(y*nx+x,y*nx+x+1,Q(1))
    for y in range(ny-1):
        for x in range(nx):edge(y*nx+x,(y+1)*nx+x,v[x])
    return H

class BankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=json.loads((HERE/'evidence.json').read_text())
    def test_published_certificate(self):self.assertTrue(check(self.d))
    def test_forged_noise_and_acquisition_contract(self):
        for kind in ['rows','exponent','floor','noise','moment','count','binding']:
            d=copy.deepcopy(self.d);b=d['banks'][0]
            if kind=='rows':b['indices'][0]+=1
            elif kind=='exponent':b['exponential_upper']='1'
            elif kind=='floor':b['metrics']['L2']['floor_lower']='1'
            elif kind=='noise':b['relative_output_noise']='1/100'
            elif kind=='moment':b['discarded_moment_L2_upper']='0'
            elif kind=='count':b['channel_count']=49
            else:d['placement_sha256']='0'*64
            with self.subTest(kind=kind),self.assertRaises(AssertionError):check(d)
    def test_exact_conjugation_energy_for_noncommuting_graph(self):
        nx,ny=3,7;H=generator(nx,ny);a=Q(4);N=nx*ny
        # Variable V does not commute with the x-path generator.
        self.assertNotEqual(Q(1,1)+Q(4,5)*Q(1,2*nx),Q(1,1)+Q(4,5)*Q(3,2*nx))
        W=[a**(i//nx-3) for i in range(N)];C=Q(9,5)*(a+1/a-2)
        for seed in range(12):
            z=[Q(((i+1)*(seed+3))%13-6,7) for i in range(N)]
            form=sum(z[i]*H[i][j]*W[i]/W[j]*z[j] for i in range(N) for j in range(N))
            self.assertGreaterEqual(form,-C*sum(t*t for t in z))
        # Dropping the transverse shift penalty incorrectly asserts PSD.
        z=[Q(1) for _ in range(N)]
        form=sum(H[i][j]*W[i]/W[j] for i in range(N) for j in range(N))
        self.assertLess(form,0)
    def test_arb_full_generator_tail_control(self):
        ctx.prec=160;nx,ny=3,9;N=nx*ny;H=generator(nx,ny)
        A=arb_mat([[arb(str(t)) for t in row] for row in H]);t=Q(3,2)
        E=(-arb(str(t))*A).exp();j=4;a=Q(2)
        # Whole x-source subspace, rather than a chosen source vector.
        columns=[[E[y*nx+x,j*nx+k] for k in range(nx)] for y in range(ny) for x in range(nx)]
        bound=(2*arb(str(Q(9,5)*t*(a+1/a-2)))).exp()
        for sign in [-1,1]:
            G=[[sum(columns[i][p]*columns[i][q]*arb(str(a**(2*sign*(i//nx-j)))) for i in range(N)) for q in range(nx)] for p in range(nx)]
            # A sufficient Gershgorin PSD bound certifies all source directions.
            for p in range(nx):
                self.assertTrue(bound-G[p][p]-sum(abs(G[p][q]) for q in range(nx) if q!=p)>0)
    def test_tail_moment_envelope(self):
        for a,r in [(Q(4),14),(Q(9,2),15)]:
            for k in range(r,r+101):self.assertLessEqual(k*a**(-2*k),r*a**(-2*r))
    def test_three_row_label_collision(self):
        # Each label alone is perfectly identifiable; together they collide.
        A=np.array([[1.,0.],[0.,1.],[0.,0.]])
        B=np.array([[0.,0.],[1.,0.],[0.,1.]])
        self.assertEqual(np.linalg.matrix_rank(A),2);self.assertEqual(np.linalg.matrix_rank(B),2)
        np.testing.assert_array_equal(A@np.array([0.,1.]),B@np.array([1.,0.]))
    def test_centroid_perturbation_at_extreme_rows(self):
        for b in self.d['banks']:
            I=np.array(b['indices']);m=len(I);nu=float(Q(b['relative_output_noise']))
            for y in [np.ones(m),np.arange(1,m+1,dtype=float),(-1.)**np.arange(m)]:
                e=np.zeros(m);e[-1]=nu*np.linalg.norm(y)
                C=lambda z:float(I@(z*z)/(z@z))
                self.assertLessEqual(abs(C(y+e)-C(y)),float(Q(b['noise_centroid_shift_upper'])))
    def test_zero_source_cannot_identify_target(self):
        # Nonzero signals at distinct actual graph targets can both be hidden
        # by one fixed positive absolute noise budget when amplitude is free.
        from scipy.linalg import expm
        nx,ny=3,9;H=np.array(generator(nx,ny),dtype=float);E=expm(-H)
        x=(np.arange(nx)+.5)/nx
        u=np.sqrt(2/nx)*np.cos(np.pi*x)
        data=[]
        for target in [3,5]:
            v=np.zeros(nx*ny);v[target*nx:(target+1)*nx]=u
            data.append((E@v).reshape(ny,nx).sum(axis=1)/np.sqrt(nx))
        self.assertGreater(np.linalg.norm(data[0]-data[1]),1e-6)
        self.assertTrue(all(np.linalg.norm(y)>1e-6 for y in data))
        eta=1e-8;amplitude=eta/(4*max(np.linalg.norm(y) for y in data))
        for y in data:
            signal=amplitude*y;noise=-signal
            self.assertLess(np.linalg.norm(noise),eta)
            np.testing.assert_array_equal(signal+noise,np.zeros(ny))

if __name__=='__main__':unittest.main()
