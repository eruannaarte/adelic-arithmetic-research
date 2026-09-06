"""Degree-eight approximation of a compact sinusoidal family in physical W.

The proposal layer builds rational polynomials. The proof layer only needs their
full-vector weighted residual bounds; it does not assume the proposals optimal.
"""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import argparse, hashlib, json, sys
from flint import arb, ctx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT/'research/operational_transfer_2026_09/noise'))
from physical import M, ball, dyadic, upper, quantize, weights, evaluate, coefficients

DEGREE = 8
ORDERS = tuple(range(9,21))
FREQUENCY_LIMIT = Q(1)


def weighted_grid(design):
    if design not in ('multi','outer'):
        raise ValueError('unsupported physical design')
    w=weights(M)
    if design=='multi':
        a=ball(Q(125,65536));w=[(1-a)*v for v in w]
        for j,v in enumerate(weights(2550),3175):w[j]+=a*v
    x=[ball(Q(2*j+1-M,M)) for j in range(M)]
    return w,x


def basis(w,x):
    moments=[arb(1) if k==0 else arb(0) if k%2 else
             sum((a*t**k for a,t in zip(w,x)),arb(0))
             for k in range(2*DEGREE+1)]
    def inner(p,q):
        return sum((a*b*moments[i+j] for i,a in enumerate(p)
                    for j,b in enumerate(q)),arb(0))
    polys=[[arb(1)]]
    for k in range(1,DEGREE+1):
        p=[arb(0)]*k+[arb(1)]
        for q in polys:
            a=inner(p,q)
            for j,v in enumerate(q):p[j]-=a*v
        n2=inner(p,p)
        if not n2>0:raise ValueError('unresolved polynomial basis')
        polys.append([a/n2.sqrt() for a in p])
    return polys


def rounded_up(x,digits=30):
    return upper(x,digits)


def propose(design,bits=256):
    with ctx.workprec(bits):
        w,x=weighted_grid(design);polys=basis(w,x)
        values=[[evaluate(p,t) for t in x] for p in polys]
        records=[]
        for k in ORDERS:
            monomial=[t**k for t in x]
            p=[arb(0)]*(DEGREE+1)
            for j,q in enumerate(polys):
                if j%2!=k%2:continue
                c=sum((a*v*z for a,v,z in zip(w,monomial,values[j])),arb(0))
                for i,z in enumerate(q):p[i]+=c*z
            # The certificate proves this fixed rational approximation directly.
            exact=[quantize(a,40) if j%2==k%2 else Q(0) for j,a in enumerate(p)]
            pp=[ball(a) for a in exact]
            residual=[v-evaluate(pp,t) for v,t in zip(monomial,x)]
            norm2=sum((a*r*r for a,r in zip(w,residual)),arb(0))
            if not norm2>0:raise ValueError('residual norm not resolved')
            records.append({'order':k,'rational_polynomial':list(map(str,exact)),
                            'weighted_residual_norm_upper':str(rounded_up(norm2.sqrt()))})
        norms={str(k):str(rounded_up(sum((a*t**(2*k) for a,t in zip(w,x)),arb(0)).sqrt()))
               for k in (9,21,22)}
    q={r['order']:Q(r['weighted_residual_norm_upper']) for r in records}
    odd=sum((q[k]/factorial(k) for k in range(9,20,2)),Q())+Q(norms['21'])/factorial(21)
    even=sum((q[k]/factorial(k) for k in range(10,21,2)),Q())+Q(norms['22'])/factorial(22)
    return {'design':design,'approximants':records,'weighted_monomial_norm_upper':norms,
            'pointwise_taylor_factor':str(Q(1,factorial(9))),
            'weighted_taylor_factor':str(Q(norms['9'])/factorial(9)),
            'odd_projected_factor':str(odd),'even_projected_factor':str(even),
            'uniform_phase_frequency_factor':str(max(odd,even)),
            'projection_proposal_precision_bits':bits,
            'approximation_coefficients_decimal_places':40,
            'norm_bound_decimal_places':30}


def build(bits=256):
    records=[propose(d,bits) for d in ('multi','outer')]
    return {'schema':'weighted-sinusoidal-approximation-v1','measurement_count':M,
            'degree':DEGREE,'normalized_time':'x=t/890',
            'family':'A*sin(omega*x+phi), |A|<=B, real phi, real |omega|<=1',
            'frequency_limit':'1','weights':'unchanged physical cosine windows; sum=1; exact even symmetry',
            'physical_window_coefficients':list(map(str,coefficients())),
            'designs':records,
            'premise':'The physical drift belongs to the stated family plus an unrestricted polynomial of degree at most eight.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bits',type=int,default=256);p.add_argument('--write',action='store_true')
    a=p.parse_args();result=build(a.bits)
    if a.write:(HERE/'approximation.json').write_text(json.dumps(result,indent=2)+'\n')
    for r in result['designs']:
        f=Q(r['uniform_phase_frequency_factor'])
        print(r['design'], 'uniform factor',float(f),'pointwise gain',float(Q(r['pointwise_taylor_factor'])/f),
              'weighted Taylor gain',float(Q(r['weighted_taylor_factor'])/f),flush=True)
