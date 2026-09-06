"""Exact vertex-gap classification and outward universal acquisition bounds."""
from fractions import Fraction as Q
from itertools import product
from math import prod
from pathlib import Path
import argparse,json
from flint import arb,fmpq,ctx

HERE=Path(__file__).resolve().parent
PRIMES=(2,3,5)
STATES=4

def ball(x):
    x=Q(x);return arb(fmpq(x.numerator,x.denominator))

def endpoint(x):
    if not x.is_finite() or not x.is_exact():raise ValueError('finite exact endpoint required')
    m,e=map(int,x.man_exp())
    return Q(m*2**e) if e>=0 else Q(m,2**(-e))

def enclosure(x,scale=10**12):
    lo,hi=endpoint(x.lower()),endpoint(x.upper())
    return [str(Q(lo.numerator*scale//lo.denominator,scale)),
            str(Q(-((-hi.numerator*scale)//hi.denominator),scale))]

def classify():
    result={k:[] for k in range(1,4)}
    for v in product(range(-3,4),repeat=3):
        x=prod(p**max(a,0) for p,a in zip(PRIMES,v))
        y=prod(p**max(-a,0) for p,a in zip(PRIMES,v))
        if x<=y:continue
        result[sum(a!=0 for a in v)].append((Q(x,y),v))
    return {str(k):{'oriented_differences':len(rows),
                    'minimum_ratio':str(min(rows)[0]),
                    'difference':list(min(rows)[1])} for k,rows in result.items()}

def time_bound(c,k,ratio,m=6):
    c=Q(c);ratio=Q(ratio)
    if m<1 or k<1 or ratio<=1 or c<0 or c*c*k>2*m:
        raise ValueError('invalid time-bound domain')
    return 2*(ball(c)*(ball(k)/ball(2*m)).sqrt()).asin()/ball(ratio).log()

def build(precision=256):
    with ctx.workprec(precision):
        classes=classify();c=Q(163,200);m=6
        for k,row in classes.items():
            row['required_time']=enclosure(time_bound(c,int(k),Q(row['minimum_ratio']),m))
        strongest=time_bound(c,3,Q(25,24),m)
        old=(ball(c)*(ball(20)/m).sqrt()).root(3)/arb(2).log()
        T=20;delta=ball(Q(25,24)).log()
        assert 0<T*delta/2<arb.pi()/2
        cap=2*(T*delta/2).sin()
        assert cap<ball(c)
        assert strongest>20 and strongest>12*old
        return {'schema':'harmonic-cycle1-v1','model':{'primes':list(PRIMES),'states':STATES,'readings':m,'factor_floor_target':str(c)},
                'classes':classes,'strongest_time_lower':enclosure(strongest),
                'previous_cubic_time_lower':enclosure(old),'improvement_ratio':enclosure(strongest/old),
                'witness':{'numerator_vertex':[0,0,2],'denominator_vertex':[3,1,0],
                           'integer_labels':[25,24],'changed_factors':3,'factor_distance_squared':'6'},
                'time20_floor_upper':enclosure(cap),'time20_rejected_for_target':True}

def check(path=HERE/'cycle1_evidence.json',precision=256):
    expected=json.loads(Path(path).read_text());actual=build(precision)
    if actual!=expected:raise ValueError('fresh model-to-certificate mismatch')
    return actual

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--precision',type=int,default=256)
    a=p.parse_args();path=HERE/'cycle1_evidence.json'
    if a.write:path.write_text(json.dumps(build(a.precision),indent=2)+'\n')
    d=check(path,a.precision)
    print('Cycle1 PASS: exact 171-ratio classification and outward acquisition bounds')
    print(json.dumps({k:d[k] for k in ('strongest_time_lower','previous_cubic_time_lower','improvement_ratio','time20_floor_upper')},indent=2))
