#!/usr/bin/env python3
"""Independent stdlib rational reconstruction of a Path-5 Taylor certificate.

Arb coefficient enclosures and metric intervals are the numerical premises;
this checker proves their polynomial, remainder, spectral and cover consequences.
Run generate_certificate.py to regenerate the premises from the declared model.
"""
from fractions import Fraction as F
import json
import sys

METRICS = ('L2', 'declared_H1', 'natural_discrete_H1')
L2_FLOOR=F('71575982560691627369082268261831253224317187234411991716471/500000000000000000000000000000000000000000000000000000000000000000')
H1_FLOOR=F('177615501105199674392110272222231543772504830490130249386911/50000000000000000000000000000000000000000000000000000000000000000000')

def qtext(x):
    x=F(x)
    return f'{x.numerator}/{x.denominator}'

def interval(x):
    if not isinstance(x,list) or len(x)!=2: raise ValueError('interval shape')
    a,b=map(F,x)
    if a>b: raise ValueError('reversed interval')
    return a,b

def enc(x): return [qtext(x[0]),qtext(x[1])]
def plus(x,y): return x[0]+y[0],x[1]+y[1]
def times(x,y):
    z=[a*b for a in x for b in y]
    return min(z),max(z)
def scale(x,c): return times(x,(c,c))
def absmax(x): return max(abs(x[0]),abs(x[1]))

def raw_remainder(d,a,b,r,root_upper):
    """ONE normalized Gram entry, using |raw derivative k| <= k!/a^k."""
    d=int(d);a=F(a);b=F(b);r=F(r);root_upper=F(root_upper)
    if d<1 or not 0<a<=b or not 0<r or root_upper<=0 or root_upper**2<1+b:
        raise ValueError('invalid remainder premises')
    coeff=F(1); total=F(0)
    for j in range(d+1):
        if j: coeff*=F(3-2*j,2*j)
        total+=abs(coeff)/(1+a)**j/a**(d-j)
    return root_upper*r**d*total

def polynomial_box(coefficients,delta):
    v=(F(0),F(0))
    for c in reversed(coefficients): v=plus(times(v,delta),interval(c))
    return v

def symmetric_error_box(record,cell):
    a,b=map(F,cell['interval']); centre=F(cell['centre']); r=F(cell['radius'])
    if centre-r!=a or centre+r!=b: raise ValueError('centre/radius mismatch')
    d=int(cell['order'])+1
    scalar=raw_remainder(d,a,b,r,F(cell['sqrt_normalization_upper']))
    result=[]
    for idx in range(3):
        coeff=record['difference_coefficients'][idx]
        if len(coeff)!=d: raise ValueError('wrong polynomial degree')
        finite_inverse=interval(record['inverse_metric_products_finite'][idx])
        continuum_inverse=interval(record['inverse_metric_products_continuum'][idx])
        if finite_inverse[0]<=0 or continuum_inverse[0]<=0: raise ValueError('nonpositive whitening')
        rem=scalar*(finite_inverse[1]+continuum_inverse[1])
        if F(record['entry_remainders'][idx])!=rem: raise ValueError('wrong Taylor remainder')
        poly=polynomial_box(coeff,(-r,r))
        error=plus(poly,(-rem,rem))
        if enc(error)!=record['error_box'][idx]: raise ValueError('wrong polynomial box')
        result.append(error)
    return result

def norm_upper_valid(box,U):
    """Every symmetric [[a,b],[b,d]] in box obeys -UI < E < UI."""
    U=F(U);a,b,d=box
    if U<=0:return False
    bmax=absmax(b)
    for sign in (-1,1):
        # minimum diagonal of U I + sign E
        x=U+(a[0] if sign==1 else -a[1])
        y=U+(d[0] if sign==1 else -d[1])
        if x<=0 or y<=0 or x*y<=bmax*bmax:return False
    return True

def choose_norm_upper(box):
    a,b,d=box;lo=F(0)
    hi=max(absmax(a)+absmax(b),absmax(d)+absmax(b))+F(1,10**30)
    assert norm_upper_valid(box,hi)
    for _ in range(96):
        mid=(lo+hi)/2
        if norm_upper_valid(box,mid):hi=mid
        else:lo=mid
    # Human-readable conservative decimal, accepted again exactly.
    units=(hi*10**20).__ceil__()+1
    hi=F(units,10**20)
    assert norm_upper_valid(box,hi)
    return hi

def check(report):
    if report['schema']!='path5-resolution-taylor-v1':raise ValueError('schema')
    model=report['model']
    if model!={'n':1001,'K':2,'g':'4/5','target':'exact central cell','normalization':'sqrt(1+tau)','output_metric':'Euclidean modal energy'}:
        raise ValueError('unexpected model')
    cells=report['cells']
    if not cells:raise ValueError('empty cover')
    left,right=map(F,report['covered_interval']);cursor=left
    floors={k:F(v) for k,v in report['continuum_floors'].items()}
    if floors!={'L2':L2_FLOOR,'declared_H1':H1_FLOOR,'natural_discrete_H1':H1_FLOOR}:
        raise ValueError('wrong inherited continuum floor premises')
    all_bounds={m:[] for m in METRICS}
    for cell in cells:
        if cell['n']!=model['n'] or cell['finite_trace']['target_modes_retained']!=500:
            raise ValueError('wrong finite grid or modal count')
        a,b=map(F,cell['interval'])
        if a!=cursor or b<=a:raise ValueError('cover gap, overlap or wrong order')
        cursor=b
        if set(cell['metrics'])!=set(METRICS):raise ValueError('metric mismatch')
        for m in METRICS:
            rec=cell['metrics'][m];box=symmetric_error_box(rec,cell)
            U=F(rec['spectral_error_upper'])
            if not norm_upper_valid(box,U):raise ValueError('invalid spectral enclosure')
            floor=floors[m]
            if U>=floor:raise ValueError('transfer does not close')
            if F(rec['transferred_floor'])!=floor-U:raise ValueError('bad floor')
            all_bounds[m].append(U)
    if cursor!=right:raise ValueError('cover endpoint mismatch')
    result={m:{'error_upper':qtext(max(all_bounds[m])), 'floor_lower':qtext(floors[m]-max(all_bounds[m]))} for m in METRICS}
    if report['uniform_bounds']!=result:raise ValueError('bad aggregate')
    return result

if __name__=='__main__':
    p=sys.argv[1] if len(sys.argv)>1 else str(__import__('pathlib').Path(__file__).with_name('certificate.json'))
    r=json.load(open(p));result=check(r)
    print('PASS: exact Taylor remainders, interval Horner arithmetic, robust 2x2 spectral inequalities, metric floors and continuous cover.')
    for k,v in result.items(): print(k, 'error_upper_display=',float(F(v['error_upper'])),'floor_lower_display=',float(F(v['floor_lower'])))
