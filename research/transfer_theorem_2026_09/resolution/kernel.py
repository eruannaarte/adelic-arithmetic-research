"""Outward periodic-transverse, full finite-x Taylor map reconstruction."""
from fractions import Fraction as Q
from pathlib import Path
from math import factorial
import argparse,json
from flint import arb,fmpq,ctx

HERE=Path(__file__).resolve().parent
NX=1001;PERIOD=64;ORDER=32;EXP_DEGREE=80;MAX_DISTANCE=26
CENTER=Q(3,2);SCALE=10**30


def A(value):
    q=Q(value);return arb(fmpq(q.numerator,q.denominator))


def endpoint(value):
    if not value.is_exact() or not value.is_finite():raise ValueError('exact finite endpoint required')
    m,e=map(int,value.man_exp())
    return Q(m*2**e) if e>=0 else Q(m,2**(-e))


def enclosure(value):
    lo,hi=endpoint(value.lower()),endpoint(value.upper())
    floor=Q(lo.numerator*SCALE//lo.denominator,SCALE)
    ceil=Q(-(-hi.numerator*SCALE//hi.denominator),SCALE)
    if ceil-floor>Q(1,SCALE):raise ValueError('coefficient too wide at export grid')
    return [str(floor),str(ceil)]


def action(state,diag):
    out=[]
    for i,s in enumerate(state):
        v=diag[i]*s
        if i:v-=state[i-1]
        if i+1<len(state):v-=state[i+1]
        out.append(-v)
    return out


def build(precision=192,nx=NX,period=PERIOD,order=ORDER,degree=EXP_DEGREE,max_distance=MAX_DISTANCE):
    if precision<160:raise ValueError('at least 160 working bits required')
    with ctx.workprec(precision):
        x=[A(Q(2*i+1,2*nx)) for i in range(nx)]
        ports=[[(arb(2)/nx).sqrt()*(k*arb.pi()*xx).cos() for xx in x] for k in (1,2)]
        result=[[[arb(0) for _ in range(order+1)] for k in range(2)] for d in range(max_distance+1)]
        for mode in range(1,period//2+1):
            omega=4*(arb.pi()*mode/period).sin()**2
            c=2+A(Q(7,5))*omega;rho=2+A(Q(2,5))*omega
            diag=[(1 if i in (0,nx-1) else 2)+omega*(1+A(Q(4,5))*xx) for i,xx in enumerate(x)]
            shifted=[v-c for v in diag]
            states=[p[:] for p in ports];totals=[p[:] for p in ports]
            for k in range(1,degree+1):
                for port in range(2):
                    states[port]=[A(CENTER)*v/k for v in action(states[port],shifted)]
                    totals[port]=[a+b for a,b in zip(totals[port],states[port])]
            expc=(-A(CENTER)*c).exp()
            states=[[expc*v for v in row] for row in totals]
            tail=(-A(CENTER)*omega).exp()*(A(CENTER)*rho)**(degree+1)/factorial(degree+1)
            norm=4+A(Q(9,5))*omega
            mode_coeff=[[],[]]
            for k in range(order+1):
                if k:
                    states=[[v/k for v in action(row,diag)] for row in states]
                radius=(tail*norm**k/factorial(k)).abs_upper()
                for port in range(2):
                    mode_coeff[port].append(sum(states[port],arb(0))/arb(nx).sqrt()+arb(0,radius))
            for d in range(max_distance+1):
                multiplier=((arb(2)/period)*(2*arb.pi()*mode*d/period).cos()
                            if mode<period//2 else A(Q((-1)**d,period)))
                for port in range(2):
                    for k in range(order+1):result[d][port][k]+=multiplier*mode_coeff[port][k]
        boxes=[[[enclosure(v) for v in row] for row in d] for d in result]
        return {'schema':'periodic-transverse-taylor-v1','model':{'nx':nx,'period':period,'source_modes':[1,2],
                 'g':'4/5','center':str(CENTER),'order':order,'exponential_degree':degree,
                 'maximum_distance':max_distance,'output':'unnormalized global-x average; multiply by (1+tau)^(1/4)'},
                'coefficient_intervals':boxes,'coefficient_export_grid':str(Q(1,SCALE)),
                'zero_mode':'exactly zero by cosine-source mean','parity':'kernel(-d)=kernel(d)'}


def check(precision=192):
    data=build(precision)
    saved=json.loads((HERE/'kernel.json').read_text())
    if data!=saved:raise ValueError('full physical kernel replay differs')
    return data


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--precision',type=int,default=192);a=p.parse_args()
    if a.write:(HERE/'kernel.json').write_text(json.dumps(build(a.precision),indent=2)+'\n')
    data=check(a.precision)
    print('PASS full finite-x periodic kernel, all 27 displacements, two sources and 33 coefficients, precision',a.precision)
