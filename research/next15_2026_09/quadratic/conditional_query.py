"""Q3: nine-stratum finite sensor query with complete inherited d2 tails."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from math import isqrt
import hashlib
import importlib.util
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=ROOT/'research/five_paths_2026_09/path4_realizability/certificate.json'
INDICES=(5,10,15,20,30,40,45)
SOURCE_CHECKER=ROOT/'research/five_paths_2026_09/path4_realizability/check_certificate.py'
_VERIFIED_SOURCE_DIGESTS=set()


def source():
    # Read immutable bytes and parse a new document on EVERY call. A caller can
    # mutate its returned object without poisoning any later source validation.
    data=SOURCE.read_bytes();doc=json.loads(data);digest=hashlib.sha256(data).hexdigest()
    if doc['schema']!='quadratic-query-v1' or doc['maximum_norm']!=50 or doc['sample_count']!=8900:
        raise ValueError('wrong sensor/tail source')
    if digest not in _VERIFIED_SOURCE_DIGESTS:
        spec=importlib.util.spec_from_file_location('_conditional_inherited_checker',SOURCE_CHECKER)
        if spec is None or spec.loader is None:raise ValueError('inherited source checker unavailable')
        verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
        verifier.check(doc)
        # The inherited stdlib checker rebuilds the measurement, positivity,
        # remote-tail and consequence contracts. Finite/Gram outward inputs
        # still have the separate, explicitly recorded full-producer replay.
        _VERIFIED_SOURCE_DIGESTS.add(digest)
    return doc,digest


def coefficients(a2,a3):
    if type(a2) is not int or type(a3) is not int or a2 not in range(3) or a3 not in range(3):raise ValueError('bad arithmetic stratum')
    x,y=a2-1,a3-1
    return [1,a2,a3,1+x+x*x,a2*a3,1+x+x*x+x**3,1+y+y*y]


def build():
    doc,digest=source();B=list(map(F,doc['consequence']['bias_upper']));q=F(doc['consequence']['q'])
    out=[]
    for a2,a3 in product(range(3),repeat=2):
        c=coefficients(a2,a3)
        J=sum((F(v*v,n**4) for n,v in zip(INDICES,c)),F())
        alpha=[F(v,n**4)/J for n,v in zip(INDICES,c)]
        bias=sum((w*B[n-1] for n,w in zip(INDICES,alpha)),F())
        radius2=(F(1,2)-bias)**2*(1-q)*J
        scale=100000
        k=isqrt(radius2.numerator*scale*scale//radius2.denominator)
        eta=F(k,scale)
        oldJ=sum((F(v*v,n**4) for n,v in zip((5,20,45),(1,c[3],c[6]))),F())
        oldbias=sum((F(v,n**4)/oldJ*B[n-1] for n,v in zip((5,20,45),(1,c[3],c[6]))),F())
        oldradius2=(F(1,2)-oldbias)**2*(1-q)*oldJ
        anchor2=min((F(1,2)-B[n-1])**2*(1-q)/n**4 for n in (2,3))
        if bias>=F(1,2) or min(B[1],B[2])<0 or max(B[1],B[2])>=F(1,2) or not eta**2<min(radius2,anchor2):
            raise ValueError('strict query or anchor guarantee failed')
        out.append({'a2':a2,'a3':a3,'multipliers':c,'J':str(J),'alpha':list(map(str,alpha)),
                    'bias_upper':str(bias),'radius_squared_sufficient':str(radius2),'declared_eta':str(eta),
                    'old_three_coordinate_radius_squared':str(oldradius2),'gain_squared':str(radius2/oldradius2)})
    return {'schema':'quadratic-conditional-query-v1','source_sha256':digest,'sensor_samples':8900,
            'noise_metric':'same positive multiscale W as five-path Path4','indices':list(INDICES),'strata':out}


def check(result):
    doc,digest=source()
    if result['schema']!='quadratic-conditional-query-v1' or result['source_sha256']!=digest or result['sensor_samples']!=8900:
        raise ValueError('wrong conditional source binding')
    if result['noise_metric']!='same positive multiscale W as five-path Path4' or result['indices']!=list(INDICES):raise ValueError('metric/coordinate mismatch')
    # Reconstruct bias directly from the full source vectors, not its stored final bias.
    ts=list(map(F,doc['complete_tail_upper']));qs=list(map(F,doc['gram_row_upper']))
    if len(ts)!=50 or len(qs)!=50 or min(ts)<0 or min(qs)<0 or max(qs)>=1:raise ValueError('bad source bounds')
    q=max(qs);top=max(ts)
    B=[n*n*(t+qi*top/(1-q)) for n,(t,qi) in enumerate(zip(ts,qs),1)]
    seen=[]
    for row in result['strata']:
        a2,a3=row['a2'],row['a3'];seen.append((a2,a3))
        if (type(a2),type(a3))!=(int,int) or a2 not in range(3) or a3 not in range(3):raise ValueError('bad stratum')
        # Independently form a(m) from the 2,3 prime powers of each multiplier.
        cs=[]
        for n in INDICES:
            m=n//5;v=1
            for p,a in ((2,a2),(3,a3)):
                e=0
                while m%p==0:m//=p;e+=1
                v*=sum((a-1)**j for j in range(e+1))
            if m!=1:raise ValueError('multiplier not smooth')
            cs.append(v)
        if row['multipliers']!=cs:raise ValueError('arithmetic incidence failed')
        alpha=list(map(F,row['alpha']))
        if len(alpha)!=7 or any(a<0 for a in alpha):raise ValueError('bad affine query')
        J=sum((F(c*c,n**4) for n,c in zip(INDICES,cs)),F())
        if sum((a*c for a,c in zip(alpha,cs)),F())!=1:raise ValueError('query not normalized')
        gain=sum((n**4*a*a for n,a in zip(INDICES,alpha)),F())
        if gain!=1/J or F(row['J'])!=J:raise ValueError('noise optimum not attained')
        bias=sum((a*B[n-1] for n,a in zip(INDICES,alpha)),F())
        radius2=(F(1,2)-bias)**2*(1-q)/gain
        eta=F(row['declared_eta'])
        if F(row['bias_upper'])!=bias or F(row['radius_squared_sufficient'])!=radius2 or bias>=F(1,2) or eta<=0 or eta**2>=radius2:
            raise ValueError('query margin false')
        for n in (2,3):
            if not B[n-1]<F(1,2) or eta**2 >= (F(1,2)-B[n-1])**2*(1-q)/n**4:raise ValueError('anchor may be wrong')
        oldpairs=((5,1),(20,cs[3]),(45,cs[6]))
        oldJ=sum((F(c*c,n**4) for n,c in oldpairs),F())
        oldB=sum((F(c,n**4)*B[n-1]/oldJ for n,c in oldpairs),F())
        oldr=(F(1,2)-oldB)**2*(1-q)*oldJ
        if F(row['old_three_coordinate_radius_squared'])!=oldr or F(row['gain_squared'])!=radius2/oldr:
            raise ValueError('comparison changed its premises')
        if radius2<oldr:raise ValueError('claimed nondecrease fails')
    if seen!=list(product(range(3),repeat=2)):raise ValueError('incomplete stratum cover')
    return {'verified':True,'strata':9,'declared_radii':[[r['a2'],r['a3'],r['declared_eta']] for r in result['strata']],
            'complete_tail_premise':'independently recheck/replay the bound source; no finite-support assumption'}


def decode(coefficient_estimates,noise_radius,certificate):
    """Verify the supplied certificate, then make the exact rational final decision.

    Upstream numerical estimation error must satisfy the declared input contract.
    No cached mutable certificate is used: every lookup follows a fresh check.
    """
    check(certificate)
    noise_radius=F(noise_radius)
    if len(coefficient_estimates)!=50 or noise_radius<0:raise ValueError('bad estimates/noise')
    real=[F(z.real if isinstance(z,complex) else z) for z in coefficient_estimates]
    # Global anchor certification uses the largest declared radius across the nine cases.
    maxeta=max(F(r['declared_eta']) for r in certificate['strata'])
    if noise_radius>maxeta:return None
    a2=round(real[1]);a3=round(real[2])
    if a2 not in range(3) or a3 not in range(3):return None
    row=certificate['strata'][3*a2+a3]
    if noise_radius>F(row['declared_eta']):return None
    z=sum((F(w)*real[n-1] for n,w in zip(INDICES,row['alpha'])),F())
    label=round(z)
    return label if label in range(3) else None


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    path=HERE/'conditional_query.json'
    if a.write:
        doc=build();check(doc);path.write_text(json.dumps(doc,indent=2)+'\n')
    print(json.dumps(check(json.loads(path.read_text())),indent=2))
