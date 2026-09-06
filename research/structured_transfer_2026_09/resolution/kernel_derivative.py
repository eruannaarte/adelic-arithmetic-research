"""Reconstruct d/dg of the exact finite-x, periodic-y diffusion kernel."""
from fractions import Fraction as Q
from pathlib import Path
from math import factorial
import argparse, json, importlib.util
from flint import arb, ctx
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]/'transfer_theorem_2026_09/resolution/kernel.py'
spec=importlib.util.spec_from_file_location('_potential_original_kernel',BASE)
k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k)

def build(bits=256):
    with ctx.workprec(bits):
        nx=1001; period=64; order=32; degree=80
        x=[k.A(Q(2*i+1,2*nx)) for i in range(nx)]
        ports=[[(arb(2)/nx).sqrt()*(mode*arb.pi()*xx).cos() for xx in x] for mode in (1,2)]
        out=[[[arb(0) for _ in range(order+1)] for _ in (0,1)] for d in range(27)]
        for mode in range(1,period//2+1):
            omega=4*(arb.pi()*mode/period).sin()**2
            c=2+k.A(Q(7,5))*omega; rad=2+k.A(Q(2,5))*omega
            diag=[(1 if i in (0,nx-1) else 2)+omega*(1+k.A(Q(4,5))*xx) for i,xx in enumerate(x)]
            shifted=[v-c for v in diag]; deriv=[omega*xx for xx in x]
            states=[p[:] for p in ports]; dstates=[[arb(0) for _ in x] for p in ports]
            totals=[p[:] for p in ports]; dtotals=[[arb(0) for _ in x] for p in ports]
            for n in range(1,degree+1):
                for port in (0,1):
                    temp=k.action(dstates[port],shifted)
                    dstates[port]=[k.A(k.CENTER)*(v-d*s)/n for v,d,s in zip(temp,deriv,states[port])]
                    states[port]=[k.A(k.CENTER)*v/n for v in k.action(states[port],shifted)]
                    totals[port]=[a+b for a,b in zip(totals[port],states[port])]
                    dtotals[port]=[a+b for a,b in zip(dtotals[port],dstates[port])]
            decay=(-k.A(k.CENTER)*c).exp()
            states=[[decay*v for v in row] for row in totals]
            dstates=[[decay*v for v in row] for row in dtotals]
            tail=(-k.A(k.CENTER)*omega).exp()*(k.A(k.CENTER)*rad)**81/factorial(81)
            dtail=omega*k.A(k.CENTER)*(-k.A(k.CENTER)*omega).exp()*(k.A(k.CENTER)*rad)**80/factorial(80)
            norm=4+k.A(Q(9,5))*omega
            coeff=[[],[]]
            for n in range(order+1):
                if n:
                    dstates=[[ (v-d*s)/n for v,d,s in zip(k.action(ds,diag),deriv,st)] for ds,st in zip(dstates,states)]
                    states=[[v/n for v in k.action(st,diag)] for st in states]
                err=dtail*norm**n/factorial(n)
                if n:err+=tail*omega*norm**(n-1)/factorial(n-1)
                for port in (0,1):
                    coeff[port].append(sum(dstates[port],arb(0))/arb(nx).sqrt()+arb(0,err.abs_upper()))
            for d in range(27):
                weight=arb(2)/64*(2*arb.pi()*mode*d/64).cos() if mode<32 else k.A(Q((-1)**d,64))
                for port in (0,1):
                    for n in range(33):out[d][port][n]+=weight*coeff[port][n]
        return {'schema':'potential-derivative-kernel-v1','model':{'nx':1001,'period':64,'g':'4/5','center':'3/2','order':32,'exponential_degree':80,'maximum_distance':26,'source_modes':[1,2]},'coefficient_export_grid':'1/1000000000000000000000000000000','coefficient_intervals':[[[k.enclosure(v) for v in p] for p in d] for d in out]}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--bits',type=int,default=256);a=p.parse_args()
    result=build(a.bits);path=HERE/'kernel_derivative.json'
    if a.write:path.write_text(json.dumps(result,indent=2)+'\n')
    else:
        if result!=json.loads(path.read_text()):raise ValueError('full derivative replay differs')
    print(json.dumps({'verified':True,'precision_bits':a.bits,'coefficients':27*2*33}))
