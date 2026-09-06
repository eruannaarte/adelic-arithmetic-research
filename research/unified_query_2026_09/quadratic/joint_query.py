"""Exact joint quadratic answer-set certificate; inherited complete d2 source."""
from __future__ import annotations
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from math import isqrt
import importlib.util
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PREVIOUS=ROOT/'research/next15_2026_09/quadratic/conditional_query.py'
spec=importlib.util.spec_from_file_location('_unified_query_previous',PREVIOUS)
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)


def indices():
    answer=[]
    for n in range(1,51):
        m=n
        for p in (2,3,5,7):
            while m%p==0:m//=p
        if m==1 and (n%5==0 or n%7==0):answer.append(n)
    return tuple(answer)


INDICES=indices()


def coefficient(n,values):
    if type(n) is not int or n<1 or len(values)!=4 or any(type(a) is not int or a not in range(3) for a in values):
        raise ValueError('invalid local arithmetic input')
    out=1
    for p,a in zip((2,3,5,7),values):
        exponent=0
        while n%p==0:n//=p;exponent+=1
        out*=sum((a-1)**k for k in range(exponent+1))
    if n!=1:raise ValueError('unsupported coefficient')
    return out


def source_bounds():
    source,digest=old.source()
    qs=list(map(F,source['gram_row_upper']));ts=list(map(F,source['complete_tail_upper']))
    q=max(qs);top=max(ts)
    bias=[t+qi*top/(1-q) for t,qi in zip(ts,qs)]
    return source,digest,q,bias


def rational_floor_sqrt(x,scale=10**8):
    if x<=0:raise ValueError('positive squared radius required')
    k=isqrt(x.numerator*scale*scale//x.denominator)
    out=F(k,scale)
    if out*out==x:out-=F(1,scale)
    if out<=0:raise ValueError('radius under reporting resolution')
    return out


def build():
    source,digest,q,bias=source_bounds()
    previous=old.build();old.check(previous)
    anchor2=min((F(1,2)/n**2-bias[n-1])**2*(1-q) for n in (2,3))
    rows=[]
    for a2,a3 in product(range(3),repeat=2):
        templates=[]
        for a5,a7 in product(range(3),repeat=2):
            c=[coefficient(n,(a2,a3,a5,a7)) for n in INDICES]
            templates.append({'a5':a5,'a7':a7,'coefficients':c})
        pairs=[]
        for i,v in enumerate(templates):
            for j in range(i+1,len(templates)):
                w=templates[j]
                if v['a5']==w['a5']:continue
                delta=[F(a-b,n*n) for n,a,b in zip(INDICES,v['coefficients'],w['coefficients'])]
                S=sum((d*d for d in delta),F())
                h=sum((abs(d)*bias[n-1] for n,d in zip(INDICES,delta)),F())
                if S<=2*h:raise ValueError('pair margin not positive')
                radius2=(1-q)*(S/2-h)**2/S
                pairs.append({'i':i,'j':j,'delta':list(map(str,delta)),
                              'squared_distance':str(S),'tail_support':str(h),
                              'radius_squared_sufficient':str(radius2)})
        oldr=F(previous['strata'][3*a2+a3]['radius_squared_sufficient'])
        guarantees=[]
        for i,v in enumerate(templates):
            near=[p for p in pairs if i in (p['i'],p['j'])]
            r2=min(F(p['radius_squared_sufficient']) for p in near)
            eta=rational_floor_sqrt(min(r2,anchor2))
            guarantees.append({'template':i,'a5':v['a5'],'a7':v['a7'],
                               'radius_squared_sufficient':str(r2),'declared_eta':str(eta),
                               'gain_squared_over_Q3':str(r2/oldr),
                               'limiting_other_templates':[p['j'] if p['i']==i else p['i'] for p in near if F(p['radius_squared_sufficient'])==r2]})
        rows.append({'a2':a2,'a3':a3,'templates':templates,'pairs':pairs,
                     'guarantees':guarantees,'Q3_radius_squared':str(oldr)})
    return {'schema':'unified-quadratic-answer-set-v1','source_sha256':digest,
            'sample_count':8900,'indices':list(INDICES),'gram_q':str(q),
            'normalized_tail_bias':list(map(str,bias)),
            'anchor_radius_squared':str(anchor2),
            'noise_metric':'same positive multiscale W as five-path Path4',
            'strata':rows}


def strict_equal(a,b):
    if type(a) is not type(b):return False
    if isinstance(a,dict):return a.keys()==b.keys() and all(strict_equal(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(strict_equal(x,y) for x,y in zip(a,b))
    return a==b


def check(certificate):
    """Rebuild all scientific fields from the separately verified source contract."""
    expected=build()
    if not strict_equal(certificate,expected):raise ValueError('joint certificate differs from exact reconstruction')
    gains=[F(g['gain_squared_over_Q3']) for row in expected['strata'] for g in row['guarantees']]
    if min(gains)<1:raise ValueError('nondecrease claim is false')
    return {'verified':True,'anchor_strata':9,'templates':81,'unequal_query_pairs':243,
            'minimum_gain_squared':str(min(gains)),'maximum_gain_squared':str(max(gains)),
            'source_scope':'actual fields; complete inherited finite/remote tail and Gram premises'}


def answer_set(coefficient_estimates,noise_radius,certificate,numerical_error=None):
    """Return a certified outer answer set; None means anchor certification unavailable.

    Estimates are real coefficients from the exact old sensing inverse, or
    approximations with supplied per-coefficient absolute numerical-error bounds.
    A singleton is a certified answer. Empty means the declared model/budgets are
    inconsistent with these inputs; it is never a valid recovered answer.
    """
    check(certificate)
    eta=F(noise_radius)
    if eta<0 or len(coefficient_estimates)!=50:raise ValueError('invalid input')
    values=[F(x.real if isinstance(x,complex) else x) for x in coefficient_estimates]
    num=[F(x) for x in (numerical_error if numerical_error is not None else [0]*50)]
    if len(num)!=50 or min(num)<0:raise ValueError('invalid numerical error')
    q=F(certificate['gram_q']);bias=list(map(F,certificate['normalized_tail_bias']))
    for n in (2,3):
        slack=F(1,2)/n**2-bias[n-1]-num[n-1]/n**2
        if slack<=0 or eta**2 >= slack**2*(1-q):return None
    a2,a3=round(values[1]),round(values[2])
    if a2 not in range(3) or a3 not in range(3):return set()
    row=certificate['strata'][3*a2+a3]
    z=[values[n-1]/n**2 for n in INDICES]
    survivors=[]
    for i,v in enumerate(row['templates']):
        center=[F(c,n*n) for n,c in zip(INDICES,v['coefficients'])]
        compatible=True
        for pair in row['pairs']:
            if i not in (pair['i'],pair['j']):continue
            delta=list(map(F,pair['delta']))
            value=abs(sum((d*(zz-cc) for d,zz,cc in zip(delta,z,center)),F()))
            h=F(pair['tail_support'])+sum((abs(d)*num[n-1]/n**2 for n,d in zip(INDICES,delta)),F())
            if value>h and (value-h)**2>eta**2*F(pair['squared_distance'])/(1-q):
                compatible=False;break
        if compatible:survivors.append(v['a5'])
    return set(survivors)


def decode(coefficient_estimates,noise_radius,certificate,numerical_error=None):
    answers=answer_set(coefficient_estimates,noise_radius,certificate,numerical_error)
    return next(iter(answers)) if answers is not None and len(answers)==1 else None


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    path=HERE/'certificate.json'
    if a.write:
        cert=build();check(cert);path.write_text(json.dumps(cert,indent=2)+'\n')
    result=check(json.loads(path.read_text()))
    print(json.dumps(result,indent=2))
