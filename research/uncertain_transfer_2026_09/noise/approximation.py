"""Rational weighted polynomial proposals for all four allowed degrees.

Moment Gram algebra proposes the polynomials and certifies their norms. The
separate consumer uses the complete physical sample vector directly.
"""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import argparse, importlib.util, json, sys
from flint import arb, ctx

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'research/operational_transfer_2026_09/noise'))
from physical import M, ball, upper, quantize, coefficients
spec=importlib.util.spec_from_file_location('_refined_grid',ROOT/'research/refined_transfer_2026_09/noise/check_approximation.py')
grid_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(grid_module)
actual_grid=grid_module.actual_grid
sys.path.insert(0,str(HERE))

DEGREES=(6,8,10,12)
CUTOFF=32
FREQUENCIES=(Q(1,2),Q(1),Q(2),Q(3))
ETA=Q(4,100000)
MISMATCH=Q(1,1000000)
EPS_A=Q(1,10**14)
EPS_B=Q(1,10**11)


def factor(record,omega):
    omega=Q(omega)
    if omega<0:raise ValueError('negative frequency bound')
    p=record['degree']; rr={r['order']:Q(r['weighted_residual_norm_upper']) for r in record['approximants']}
    mm={int(k):Q(v) for k,v in record['weighted_monomial_norm_upper'].items()}
    odd=sum((rr[k]*omega**k/factorial(k) for k in range(p+1,CUTOFF,2)),Q())+mm[CUTOFF+1]*omega**(CUTOFF+1)/factorial(CUTOFF+1)
    even=sum((rr[k]*omega**k/factorial(k) for k in range(p+2,CUTOFF+1,2)),Q())+mm[CUTOFF+2]*omega**(CUTOFF+2)/factorial(CUTOFF+2)
    return max(odd,even)


def derivative_certificate(bits=320):
    with ctx.workprec(bits):
        n=1000
        z=sum((ball(Q(1,k*k)) for k in range(1,n+1)),arb(0))+ball(Q(1,n))
        l=sum((arb(k).log()/k**2 for k in range(2,n+1)),arb(0))+(arb(n).log()+1)/n
        d=upper(14*z**13*l,30)
    return {'sum_cutoff':n,'zeta2_comparison_upper':str(upper(z,40)),
            'logarithmic_series_comparison_upper':str(upper(l,40)),
            'complete_signal_derivative_upper':str(d),
            'clock_slope_radius':str(EPS_A),'clock_offset_radius':str(EPS_B),
            'maximum_nominal_absolute_time_upper':'890',
            'complete_clock_distortion_radius':str(d*(890*EPS_A+EPS_B))}


def propose(design,bits=320):
    result=[]
    with ctx.workprec(bits):
        w,x=actual_grid(design)
        moments=[arb(1) if k==0 else arb(0) if k%2 else
                 sum((a*t**k for a,t in zip(w,x)),arb(0)) for k in range(2*CUTOFF+5)]
        def inner(p,q):
            return sum((a*b*moments[i+j] for i,a in enumerate(p) for j,b in enumerate(q)),arb(0))
        basis=[[arb(1)]]
        for k in range(1,max(DEGREES)+1):
            p=[arb(0)]*k+[arb(1)]
            for q in basis:
                c=inner(p,q)
                for j,a in enumerate(q):p[j]-=c*a
            n2=inner(p,p)
            if not n2>0:raise ValueError('unresolved positive Gram norm')
            basis.append([a/n2.sqrt() for a in p])
        for degree in DEGREES:
            entries=[]
            for k in range(degree+1,CUTOFF+1):
                pp=[arb(0)]*(degree+1)
                for j,q in enumerate(basis[:degree+1]):
                    if j%2!=k%2:continue
                    c=sum((a*moments[k+i] for i,a in enumerate(q)),arb(0))
                    for i,a in enumerate(q):pp[i]+=c*a
                exact=[quantize(a,50) if j%2==k%2 else Q(0) for j,a in enumerate(pp)]
                residual=[-ball(a) for a in exact]+[arb(0)]*(k-degree)
                residual[k]=arb(1)
                norm2=inner(residual,residual)
                if not norm2>0:raise ValueError('unresolved residual norm')
                entries.append({'order':k,'rational_polynomial':list(map(str,exact)),
                                'weighted_residual_norm_upper':str(upper(norm2.sqrt(),40))})
            result.append({'design':design,'degree':degree,'approximants':entries,
                           'weighted_monomial_norm_upper':{str(k):str(upper(moments[2*k].sqrt(),40)) for k in (CUTOFF+1,CUTOFF+2)},
                           'proposal_bits':bits,'polynomial_digits':50,'norm_digits':40})
    return result


def build(bits=320):
    records=[]
    for design in ('multi','outer'):
        records.extend(propose(design,bits))
        print('built',design,flush=True)
    return {'schema':'clocked-weighted-approximation-v1','measurement_count':M,'tested_degrees':list(DEGREES),
            'even_taylor_cutoff':CUTOFF,'frequency_grid':list(map(str,FREQUENCIES)),
            'physical_window_coefficients':list(map(str,coefficients())),
            'clock_and_derivative':derivative_certificate(bits),
            'sensor_radius':str(ETA),'mismatch_radius':str(MISMATCH),'records':records}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bits',type=int,default=320);p.add_argument('--write',action='store_true')
    a=p.parse_args();doc=build(a.bits)
    if a.write:(HERE/'approximation.json').write_text(json.dumps(doc,indent=2)+'\n')
    print(json.dumps(doc['clock_and_derivative'],indent=2))
    for r in doc['records']:
        print(r['design'],r['degree'],[(str(o),float(factor(r,(1+EPS_A)*o))) for o in FREQUENCIES])
