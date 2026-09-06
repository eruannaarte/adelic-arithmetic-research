"""Outward whole-time bounds for jointly incident clock and potential directions."""
from fractions import Fraction as Q
from pathlib import Path
from math import factorial
import argparse, json, hashlib, time
from flint import arb, arb_poly, ctx, fmpq
HERE=Path(__file__).resolve().parent
OLD=HERE.parents[1]/'transfer_theorem_2026_09/resolution'
BANK=(-15,-7,-1,1,7,15)
H=DG=Q(1,10**8)
ETA=Q(3,10**8); RHO=XI=Q(1,10**9)
MU=Q(361,256*10**9)

def A(q):
    q=Q(q);return arb(fmpq(q.numerator,q.denominator))
def endpoint(a):
    m,e=map(int,a.man_exp());return Q(m*2**e) if e>=0 else Q(m,2**(-e))
def upper(a):return endpoint(a.upper())
def lower(a):return endpoint(a.lower())
def ceil(a,digits=30):
    q=upper(a);s=10**digits;return Q(-(-q.numerator*s//q.denominator),s)
def coeff(path):
    obj=json.loads(path.read_text())
    return [[[sum(map(Q,b))/2 for b in p] for p in d] for d in obj['coefficient_intervals']]
def polynomials():
    p=coeff(OLD/'kernel.json');q=coeff(HERE.parents[1]/'structured_transfer_2026_09/resolution/kernel_derivative.json')
    return p,q

def evaluate(poly,interval,centered=False):
    if not centered:return poly(interval)
    # Independent centered expansion is used by the consumer.
    c=interval.mid();r=arb(0,interval.rad())
    value=arb(0);derivative=poly
    for n in range(len(poly)):
        value+=derivative(c)*r**n/factorial(n)
        derivative=derivative.derivative()
    return value

def build(bits=256, subdivisions=128, centered=False):
    started=time.perf_counter();records=[]
    with ctx.workprec(bits):
        p,q=polynomials();worst={k:arb(0) for k in ('joint_forward','joint_inverse','time_forward','potential_forward','time_inverse','potential_inverse')}
        for label in range(-10,11):
            P=[[arb_poly([A(v) for v in p[abs(sensor-label)][port]]) for port in (0,1)] for sensor in BANK]
            D=[[v.derivative() for v in row] for row in P]
            V=[[arb_poly([A(v) for v in q[abs(sensor-label)][port]]) for port in (0,1)] for sensor in BANK]
            G=[[sum((row[i]*row[j] for row in P),arb_poly()) for j in (0,1)] for i in (0,1)]
            T=[[sum((r[i]*d[j] for r,d in zip(P,D)),arb_poly()) for j in (0,1)] for i in (0,1)]
            B=[[sum((r[i]*d[j] for r,d in zip(P,V)),arb_poly()) for j in (0,1)] for i in (0,1)]
            det=G[0][0]*G[1][1]-G[0][1]*G[1][0]
            adj=[[G[1][1],-G[0][1]],[-G[1][0],G[0][0]]]
            NT=[[sum((adj[i][k]*T[k][j] for k in (0,1)),arb_poly()) for j in (0,1)] for i in (0,1)]
            NB=[[sum((adj[i][k]*B[k][j] for k in (0,1)),arb_poly()) for j in (0,1)] for i in (0,1)]
            for cell in range(subdivisions):
                lo=Q(1)+Q(cell,subdivisions);hi=lo+Q(1,subdivisions)
                t=A((lo+hi)/2)+arb(0,A((hi-lo)/2));z=t-A(Q(3,2));beta=1/(4*(1+t));alpha=(1+t).sqrt().sqrt()
                ev=lambda a:evaluate(a,z,centered)
                de=ev(det)
                if not de>0:raise ValueError(('nonpositive Gram determinant enclosure',label,cell))
                time_inv=[[ev(NT[i][j])/de+beta*int(i==j) for j in (0,1)] for i in (0,1)]
                pot_inv=[[ev(NB[i][j])/de for j in (0,1)] for i in (0,1)]
                time_map=[[alpha*(ev(d)+beta*ev(v)) for d,v in zip(dr,pr)] for dr,pr in zip(D,P)]
                pot_map=[[alpha*ev(v) for v in row] for row in V]
                frob=lambda matrix:sum((abs(v).upper()**2 for row in matrix for v in row),arb(0)).sqrt()
                bounds={'time_forward':frob(time_map),'potential_forward':frob(pot_map),'time_inverse':frob(time_inv),'potential_inverse':frob(pot_inv)}
                for space,x,y in [('forward',time_map,pot_map),('inverse',time_inv,pot_inv)]:
                    vals=[frob([[A(H)*v+sign*A(DG)*w for v,w in zip(a,b)] for a,b in zip(x,y)]) for sign in (-1,1)]
                    bounds['joint_'+space]=A(max(upper(v) for v in vals))
                rec={'target':label+500,'time_cell':[str(lo),str(hi)],'bounds':{k:str(ceil(v)) for k,v in bounds.items()}}
                records.append(rec)
                for key,value in bounds.items():
                    if upper(value)>upper(worst[key]):worst[key]=A(upper(value))
        result={'schema':'spatial-structured-directions-v1','bank_rows':[x+500 for x in BANK],'nominal_g':'4/5','time_interval':['1','2'],'clock_radius':str(H),'potential_radius':str(DG),'subdivisions':subdivisions,'precision_bits':bits,'method':'outward polynomial Gram numerators and determinant; common rectangle corners; Frobenius operator upper bounds','global_bounds':{k:str(ceil(v)) for k,v in worst.items()},'records':records,'premise_sha256':{str(path.relative_to(HERE.parents[2])):hashlib.sha256(path.read_bytes()).hexdigest() for path in (OLD/'kernel.json',HERE.parents[1]/'structured_transfer_2026_09/resolution/kernel_derivative.json')},'runtime_seconds':time.perf_counter()-started}
        return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--bits',type=int,default=256);p.add_argument('--subdivisions',type=int,default=128);p.add_argument('--centered',action='store_true');a=p.parse_args()
    result=build(a.bits,a.subdivisions,a.centered)
    if a.write:(HERE/'directions.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
