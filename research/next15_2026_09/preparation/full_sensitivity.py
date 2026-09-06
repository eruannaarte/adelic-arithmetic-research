"""Outward full launch-sensitivity enclosure; see PROOFS.md for trust scope.

Picard--Taylor construction adapted from the preserved Path 1 preparation.py
and original oig_double_pendulum_validated_transfer.py; new six-direction dual
and 31-dimensional system certify signed preparation correlations.
"""
from __future__ import annotations
import argparse,hashlib,json,sys,time
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from flint import arb,arb_series,ctx
import oig_double_pendulum_validated_transfer as base
from oig_double_pendulum_protocol import canonical_protocol_candidates

class Dual:
    def __init__(self,value,gradient): self.value=value;self.gradient=tuple(gradient)
    def coerce(self,x): return x if isinstance(x,Dual) else Dual(x,[self.value*0]*6)
    def __add__(self,x):
        x=self.coerce(x);return Dual(self.value+x.value,[a+b for a,b in zip(self.gradient,x.gradient)])
    __radd__=__add__
    def __neg__(self):return Dual(-self.value,[-a for a in self.gradient])
    def __sub__(self,x):return self+-self.coerce(x)
    def __rsub__(self,x):return self.coerce(x)+-self
    def __mul__(self,x):
        x=self.coerce(x);return Dual(self.value*x.value,[a*x.value+self.value*b for a,b in zip(self.gradient,x.gradient)])
    __rmul__=__mul__
    def reciprocal(self):
        r=1/self.value;return Dual(r,[-a*r*r for a in self.gradient])
    def __truediv__(self,x):return self*self.coerce(x).reciprocal()
    def __rtruediv__(self,x):return self.coerce(x)*self.reciprocal()
    def sin(self):return Dual(self.value.sin(),[self.value.cos()*a for a in self.gradient])
    def cos(self):return Dual(self.value.cos(),[-self.value.sin()*a for a in self.gradient])
    def exp(self):
        e=self.value.exp();return Dual(e,[e*a for a in self.gradient])

def rhs(y):
    """z4, six derivatives z4 (u,v,prep4), constants u,v,epsilon."""
    zero=y[0]*0;one=zero+1
    z=[Dual(y[j],[y[4+4*k+j] for k in range(6)]) for j in range(4)]
    u=Dual(y[28],[one,zero,zero,zero,zero,zero]);v=Dual(y[29],[zero,one,zero,zero,zero,zero])
    speed=Dual(y[30].exp(),[zero]*6);m=u.exp();l=v.exp()
    a,b,c,d=z;sn=(a-b).sin();cs=(a-b).cos()
    m11=1+m;m12=m*l*cs;m22=m*l*l
    f1=-m*l*sn*d*d-(1+m)*a.sin();f2=m*l*sn*c*c-m*l*b.sin()
    det=m11*m22-m12*m12
    zz=[speed*c,speed*d,speed*(m22*f1-m12*f2)/det,speed*(-m12*f1+m11*f2)/det]
    return tuple([p.value for p in zz]+[p.gradient[k] for k in range(6) for p in zz]+[zero]*3)

def polynomial(mid,order):
    prec=order+1;cur=[arb_series([x],prec=prec) for x in mid]
    for _ in range(order):
        zz=rhs(cur);nxt=[]
        for initial,d in zip(mid,zz):
            cc=d.integral().coeffs()[:prec]
            if cc:cc[0]+=initial
            else:cc=[initial]
            nxt.append(arb_series(cc,prec=prec))
        cur=nxt
    return [[c.mid() for c in (list(s.coeffs())+[arb(0)]*prec)[:prec]] for s in cur]


def defect(polys,h):
    order=len(polys[0])-1;prec=order+1
    pp=[arb_series(c,prec=prec) for c in polys]
    rr=[p.derivative()-f for p,f in zip(pp,rhs(pp))]
    t=arb(h/2,(h/2).abs_upper())
    pp1=[base._compose_polynomial_series(c,t,prec) for c in polys]
    dd=[base._compose_polynomial_series([i*c[i] for i in range(1,len(c))],t,prec) for c in polys]
    r1=[d-f for d,f in zip(dd,rhs(pp1))]
    result=[]
    for a,b in zip(rr,r1):
        ac=a.coeffs();bc=b.coeffs()
        bound=sum((base._magnitude(ac[k] if k<len(ac) else arb(0))*h**k for k in range(order)),arb(0))
        bound+=base._magnitude(bc[order] if order<len(bc) else arb(0))*h**order
        result.append(bound.abs_upper())
    return result


def jacobian(box):
    yy=[base.IntervalJet.variable(v,j,len(box)) for j,v in enumerate(box)]
    return [[base._magnitude(g) for g in v.gradient] for v in rhs(yy)]


def step(initial,hq,config):
    h=base._arb_fraction(hq);mid=[x.mid() for x in initial]
    pol=polynomial(mid,config.taylor_order)
    p0=[base._polynomial_value(c,arb(0)) for c in pol]
    p1=[base._polynomial_value(c,h) for c in pol]
    ti=arb(h/2,(h/2).abs_upper());pr=[base._polynomial_value(c,ti) for c in pol]
    dd=defect(pol,h)
    bb=[(base._magnitude(x-y)+h*d).abs_upper() for x,y,d in zip(initial,p0,dd)]
    inflation=base._arb_fraction(config.tube_inflation);tiny=arb('1e-45')
    rho=[(inflation*b+tiny).abs_upper() for b in bb]
    for iteration in range(1,config.maximum_tube_iterations+1):
        tube=[arb(v.mid(),v.rad()+r) for v,r in zip(pr,rho)]
        aa=jacobian(tube)
        target=[(b+h*sum((a*r for a,r in zip(row,rho)),arb(0))).abs_upper() for b,row in zip(bb,aa)]
        if all(base._strictly_dominates(r,t) for r,t in zip(rho,target)):
            end=tuple(arb(v.mid(),v.rad()+t) for v,t in zip(p1,target))
            return end,iteration
        rho=[r if base._strictly_dominates(r,t) else (inflation*t).abs_upper() for r,t in zip(rho,target)]
    raise base.StepValidationError('31-dimensional Picard tube did not close: '+str([(i,str(r),str(t)) for i,(r,t) in enumerate(zip(rho,target)) if not base._strictly_dominates(r,t)]))


def interval(a,den=10**18):
    lo,hi=base._rational_outer_interval(a,den)
    return [str(lo),str(hi)]


def build(radius=Q(1,10000),prep_radius=Q(1,1000000),step_size=Q(1,100),bits=160,order=8):
    if radius<0 or prep_radius<0:raise ValueError('radii must be nonnegative')
    config=base.ValidatedTransferConfig(precision_bits=bits,taylor_order=order,step_size=step_size,maximum_tube_iterations=40)
    rows=[];started=time.monotonic();allc=canonical_protocol_candidates()
    with ctx.workprec(bits):
        for launch in dict.fromkeys(c.launch for c in allc):
            candidates=[c for c in allc if c.launch==launch]
            current=tuple([arb(base._arb_fraction(x),base._arb_fraction(prep_radius)) for x in launch]+[arb(0)]*8+[arb(int(i==j)) for i in range(4) for j in range(4)]+[arb(0,base._arb_fraction(radius))]*3)
            elapsed=Q(0);steps=0;maxit=0
            for terminal in sorted({c.observation_time_tau for c in candidates}):
                while elapsed<terminal:
                    h=min(step_size,terminal-elapsed)
                    current,it=step(current,h,config);elapsed+=h;steps+=1;maxit=max(maxit,it)
                ff=rhs(current)
                for c in candidates:
                    if c.observation_time_tau!=terminal:continue
                    j={'theta_1':0,'theta_2':1,'scaled_omega_1':2,'scaled_omega_2':3}[c.sensor]
                    row=[current[4+j],current[8+j],base._arb_fraction(terminal)*ff[j]]
                    rows.append({'name':c.name,'launch':[str(x) for x in launch],'time':str(terminal),'sensor':c.sensor,'cost':str(c.cost),'jacobian':[interval(x) for x in row],'preparation_jacobian':[interval(current[12+4*k+j]) for k in range(4)],'output':interval(current[j]),'validated_steps':steps,'maximum_tube_iterations':maxit})
            print(f'validated {candidates[0].name.split(" /")[0]}: {steps} steps',file=sys.stderr,flush=True)
    rows.sort(key=lambda r:next(i for i,c in enumerate(allc) if c.name==r['name']))
    return {'schema':'shared-preparation-jacobian-v1','parameter_box_radius':str(radius),'preparation_box_radius':str(prep_radius),'preparation_coordinates':['theta1','theta2','scaled_omega1','scaled_omega2'],'preparation_incidence':'one unknown preparation vector per launch, shared across its readings','source_coordinates':['u','v','epsilon'],'clock_structure':'one epsilon shared globally; actual time exp(epsilon)*tau','config':{'precision_bits':bits,'order':order,'step':str(step_size)},'rows':rows,'elapsed_seconds':time.monotonic()-started,'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).resolve(),ROOT/'oig_double_pendulum_validated_transfer.py',ROOT/'oig_double_pendulum_protocol.py']}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--radius',default='1/10000');ap.add_argument('--preparation',default='1/1000000');ap.add_argument('--step',default='1/100');ap.add_argument('--bits',type=int,default=160);ap.add_argument('--order',type=int,default=8);ap.add_argument('--output',required=True)
    a=ap.parse_args();p=Path(a.output)
    if p.exists():raise FileExistsError(p)
    report=build(Q(a.radius),Q(a.preparation),Q(a.step),a.bits,a.order)
    with p.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'output':str(p),'elapsed_seconds':report['elapsed_seconds']}))
if __name__=='__main__':main()
