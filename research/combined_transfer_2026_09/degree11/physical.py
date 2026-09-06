"""Outward reconstruction of the actual 8,900-reading augmented experiment.

Adapted locally from operational_transfer_2026_09/noise/physical.py.
The only mathematical changes are the degree-11 contract and local verified
Schur record loader. All phases, weights and polynomial columns are reconstructed, not loaded from a
floating Gram matrix. Arbitrary exact complex readings and coefficients are
accepted. The old tail certificate supplies only its explicitly bound premises.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import isqrt
import ast, hashlib, importlib.util, json
from flint import acb, acb_mat, arb, ctx, fmpq
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PRIOR=ROOT/'research/transfer_theorem_2026_09/noise'
M=8900


def ball(x):
    x=Q(x)
    return arb(fmpq(x.numerator,x.denominator))


def dyadic(x):
    if not x.is_finite() or not x.is_exact():raise ValueError('nonfinite or inexact endpoint')
    m,e=map(int,x.man_exp())
    return Q(m*2**e) if e>=0 else Q(m,2**(-e))


def upper(x, digits=60):
    v=dyadic(x.upper());scale=10**digits
    return Q(-(-v.numerator*scale//v.denominator),scale)


def quantize(x,digits=50):
    v=dyadic(x.mid());scale=10**digits
    return Q((2*v.numerator*scale+v.denominator)//(2*v.denominator),scale)


def exact(value):
    if type(value) not in (str,int,Q):raise ValueError('use exact rational strings, integers, or Fractions')
    return Q(value)


def parse_pairs(rows,count):
    if type(rows) not in (list,tuple) or len(rows)!=count:raise ValueError('complex vector dimension')
    if any(type(r) not in (list,tuple) or len(r)!=2 for r in rows):raise ValueError('complex pair shape')
    return [(exact(a),exact(b)) for a,b in rows]


def complex_ball(pair):
    return acb(ball(pair[0]),ball(pair[1]))


def encode(rows):
    return [[str(a),str(b)] for a,b in rows]


def digest_pairs(rows):
    return hashlib.sha256(json.dumps(encode(rows),separators=(',',':')).encode()).hexdigest()


def load_prior():
    # The degree-eleven consumer independently rebuilds the Schur consequences.
    spec=importlib.util.spec_from_file_location('_degree_eleven_consumer',HERE/'check.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    document=json.loads((HERE/'evidence.json').read_text())
    module.check(document)
    return document


def correction():
    doc=json.loads((ROOT/'research/next15_2026_09/noise/cycle2_correction.json').read_text())
    if doc['schema']!='noise-midpoint-vector-v1' or doc['denominator']!=10**20:raise ValueError('digital correction contract')
    positive=[(Q(a,doc['denominator']),Q(b,doc['denominator'])) for a,b in doc['positive_complex_numerators']]
    if len(positive)!=M//2:raise ValueError('digital correction size')
    return [(a,-b) for a,b in reversed(positive)]+positive


def coefficients():
    tree=ast.parse((ROOT/'arithmetic_sensing_iv.py').read_text())
    node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REFERENCE_COEFFICIENTS' for t in n.targets))
    result=[Q.from_float(v) for v in ast.literal_eval(node.value.args[0])]
    if len(result)!=8:raise ValueError('physical window dimension')
    return result


def weights(count):
    c=coefficients();out=[]
    for j in range(count):
        angle=arb.pi()*ball(Q(2*j+1,count))
        w=(1+2*sum((ball(a)*(angle*k).cos() for k,a in enumerate(c,1)),arb(0)))/count
        if not w>0:raise ValueError('positive physical weight not established')
        out.append(w)
    if not sum(out,arb(0)).contains(1):raise ValueError('physical weight mass')
    return out


def evaluate(poly,x):
    z=arb(0)
    for c in reversed(poly):z=z*x+c
    return z


class PhysicalModel:
    def __init__(self,design='multi',degree=11,bits=320):
        if design not in ('multi','outer') or type(degree) is not int or degree != 11:raise ValueError('unsupported certified design/degree')
        if type(bits) is not int or bits<128:raise ValueError('at least 128 working bits required; adequacy still checked a posteriori')
        self.design,self.degree,self.bits=design,degree,bits
        self.document=load_prior()
        self.record=next(r for r in self.document['designs'][design]['degrees'] if r['degree']==degree)
        self.floor=1-Q(self.record['augmented_gram_defect'])
        self.correction=correction()
        with ctx.workprec(bits):
            w=weights(M)
            if design=='multi':
                alpha=ball(Q(125,65536));w=[(1-alpha)*a for a in w]
                for j,a in enumerate(weights(2550),3175):w[j]+=alpha*a
            self.w=w
            self.times=[ball(Q(2*j+1-M,10)) for j in range(M)]
            self.x=[ball(Q(2*j+1-M,8900)) for j in range(M)]
            moments=[arb(1) if k==0 else arb(0) if k%2 else sum((a*x**k for a,x in zip(w,self.x)),arb(0)) for k in range(2*degree+1)]
            def inner(a,b):return sum((x*y*moments[i+j] for i,x in enumerate(a) for j,y in enumerate(b)),arb(0))
            polys=[[arb(1)]]
            saved=self.document['designs'][design]['physical_polynomials']['polynomial_coefficients']
            for k in range(1,degree+1):
                r=[arb(0)]*k+[arb(1)]
                for prev in polys:
                    proj=inner(r,prev)
                    for j,v in enumerate(prev):r[j]-=proj*v
                norm2=inner(r,r)
                if not norm2>0:raise ValueError('polynomial basis not resolved')
                polys.append([v/norm2.sqrt() for v in r])
            # Positive-leading orthonormal polynomials are unique. These interval
            # containment checks also bind their coordinates to the tail proof.
            for k,p in enumerate(polys):
                for a,box in zip(p,saved[k]):
                    lo,hi=map(Q,box)
                    if lo==hi==0:
                        if not a.contains(0):raise ValueError('basis parity')
                    elif not (dyadic(a.lower())>=lo and dyadic(a.upper())<=hi):raise ValueError('basis disagrees with complete-tail premise')
            self.polys=polys
            logs=[arb(n).log() for n in range(1,51)]
            rows=[[acb(0,-t*ln).exp() for ln in logs]+[acb(evaluate(p,x)) for p in polys[1:]] for t,x in zip(self.times,self.x)]
            self.X=acb_mat(rows)
            dim=50+degree
            self.XstarW=acb_mat([[rows[j][k].conjugate()*w[j] for j in range(M)] for k in range(dim)])
            self.G=self.XstarW*self.X
            defect=max(upper(sum((abs(self.G[i,j]-int(i==j)) for j in range(dim)),arb(0))) for i in range(dim))
            if not defect<=1-self.floor:raise ValueError('actual Gram does not verify historical lower floor')
            self.actual_gram_defect_upper=defect
            self.Xfloat=np.array([[complex(float(a.real.mid()),float(a.imag.mid())) for a in row] for row in rows])
            self.wfloat=np.array([float(a.mid()) for a in w])
            self.Gfloat=self.Xfloat.conj().T@(self.wfloat[:,None]*self.Xfloat)

    def centered(self,data):
        d=parse_pairs(data,M)
        return d,acb_mat([[complex_ball((a-c,b-e))] for (a,b),(c,e) in zip(d,self.correction)])

    def propose(self,data,method='float'):
        with ctx.workprec(self.bits):
            pairs,z=self.centered(data)
            if method=='float':
                v=np.array([complex(float(a-c),float(b-e)) for (a,b),(c,e) in zip(pairs,self.correction)])
                theta=np.linalg.solve(self.Gfloat,self.Xfloat.conj().T@(self.wfloat*v))
                if not np.isfinite(theta).all():raise ValueError('nonfinite floating proposal')
                return [(Q.from_float(float(a.real)),Q.from_float(float(a.imag))) for a in theta]
            if method!='arb':raise ValueError('unknown proposal method')
            theta=self.G.solve(self.XstarW*z)
            return [(quantize(theta[j,0].real),quantize(theta[j,0].imag)) for j in range(50+self.degree)]

    def residual(self,data,proposal,form='normal'):
        with ctx.workprec(self.bits):
            pairs,z=self.centered(data);theta=parse_pairs(proposal,50+self.degree)
            v=acb_mat([[complex_ball(p)] for p in theta])
            if form=='normal':r=self.G*v-self.XstarW*z
            elif form=='readings':r=self.XstarW*(self.X*v-z)
            else:raise ValueError('unknown residual evaluation')
            # Squaring a symmetric interval around zero can retain a negative
            # lower endpoint. Bound each modulus first, then take a rational
            # square-root upper bound; this also handles an exact zero residual.
            square=sum((upper(abs(r[j,0]))**2 for j in range(50+self.degree)),Q())
            scale=10**60
            k=isqrt(square.numerator*scale*scale//square.denominator)
            radius=Q(k+1,scale)
            return radius,r
