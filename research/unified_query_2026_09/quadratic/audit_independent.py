"""Independent exact field, template and pair audit; does not call build()."""
from fractions import Fraction as Q
from itertools import product, combinations
from math import isqrt
from pathlib import Path
import importlib.util, json, sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def factor(n):
    out=[]
    p=2
    while p*p<=n:
        if n%p==0:
            e=0
            while n%p==0:n//=p;e+=1
            out.append((p,e))
        p+=1
    if n>1:out.append((n,1))
    return out


def character(D,n):
    result=1
    for p,e in factor(n):
        if D%p==0:return 0
        if p==2:c=1 if D%8 in (1,7) else -1
        else:
            residue=pow(D%p,(p-1)//2,p)
            assert residue in (1,p-1)
            c=1 if residue==1 else -1
        result*=c**e
    return result


def coefficient(D,n):
    return sum(character(D,k) for k in range(1,n+1) if n%k==0)


def fields():
    """Exact positive fundamental discriminants, with trial-division checks."""
    found={}
    for d in range(2,100001):
        if any(e>1 for _,e in factor(d)):continue
        D=d if d%4==1 else 4*d
        pattern=tuple(1+character(D,p) for p in (2,3,5,7))
        if pattern not in found:
            found[pattern]={'radicand':d,'D':D,'radicand_factorization':factor(d),
                            'prefix':[coefficient(D,n) for n in range(1,51)]}
        if len(found)==81:break
    assert set(found)==set(product(range(3),repeat=4))
    return found


def run():
    certificate=json.loads((HERE/'certificate.json').read_text())
    source=json.loads((ROOT/'research/five_paths_2026_09/path4_realizability/certificate.json').read_text())
    spec=importlib.util.spec_from_file_location('audit_actual_sensor_checker',
        ROOT/'research/five_paths_2026_09/path4_realizability/check_certificate.py')
    verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
    verifier.check(source)
    qs=list(map(Q,source['gram_row_upper']));ts=list(map(Q,source['complete_tail_upper']))
    q=max(qs);bt=max(ts);bias=[t+s*bt/(1-q) for s,t in zip(qs,ts)]
    assert certificate['normalized_tail_bias']==list(map(str,bias))
    assert certificate['gram_q']==str(q)
    I=tuple(n for n in range(1,51)
            if (n%5==0 or n%7==0) and all(p in (2,3,5,7) for p,e in factor(n)))
    assert certificate['indices']==list(I)
    field=fields()
    anchors=min((Q(1,2*n*n)-bias[n-1])**2*(1-q) for n in (2,3))
    assert all(bias[n-1]<Q(1,2*n*n) for n in (2,3))
    assert anchors==Q(certificate['anchor_radius_squared'])
    oldI=(5,10,15,20,30,40,45)
    gains=[];anchor_ratios=[];pair_count=0;seen=[]
    for row in certificate['strata']:
        a2,a3=row['a2'],row['a3'];seen.append((a2,a3))
        patterns=[(a2,a3,a5,a7) for a5,a7 in product(range(3),repeat=2)]
        values=[field[p]['prefix'] for p in patterns]
        for p,v,actual in zip(patterns,row['templates'],values):
            assert (v['a5'],v['a7'])==p[2:]
            assert v['coefficients']==[actual[n-1] for n in I]
        independent={}
        for left,right in combinations(range(9),2):
            if patterns[left][2]==patterns[right][2]:continue
            delta=[Q(values[left][n-1]-values[right][n-1],n*n) for n in I]
            norm2=sum(d*d for d in delta)
            support=sum(abs(d)*bias[n-1] for n,d in zip(I,delta))
            assert norm2>2*support
            radius=(1-q)*(norm2/2-support)**2/norm2
            independent[left,right]=(delta,norm2,support,radius)
        assert len(independent)==27
        assert {(p['i'],p['j']) for p in row['pairs']}==set(independent)
        for p in row['pairs']:
            delta,norm2,support,radius=independent[p['i'],p['j']]
            assert p['delta']==list(map(str,delta))
            assert Q(p['squared_distance'])==norm2
            assert Q(p['tail_support'])==support
            assert Q(p['radius_squared_sufficient'])==radius
            pair_count+=1
        # Prior Q3 comparison reconstructed from the actual field's 2,3 part.
        D=field[patterns[0]]['D']
        c=[coefficient(D,n//5) for n in oldI]
        J=sum(Q(v*v,n**4) for n,v in zip(oldI,c))
        h=sum(Q(v,n*n)*bias[n-1] for n,v in zip(oldI,c))
        oldr=(1-q)*(J/2-h)**2/J
        assert oldr==Q(row['Q3_radius_squared'])
        for i,g in enumerate(row['guarantees']):
            r2=min(v[-1] for pair,v in independent.items() if i in pair)
            assert Q(g['radius_squared_sufficient'])==r2
            assert Q(g['gain_squared_over_Q3'])==r2/oldr>=1
            eta=Q(g['declared_eta'])
            assert eta>0 and eta*eta<min(r2,anchors)
            gains.append(r2/oldr);anchor_ratios.append(eta*eta/anchors)
        for i in [0,3]:assert Q(row['guarantees'][i]['gain_squared_over_Q3'])==1
    assert seen==list(product(range(3),repeat=2))
    assert pair_count==243
    assert max(gains)>Q(1004,1000)**2
    witnesses=[{'pattern':list(k),**v} for k,v in sorted(field.items())]
    return {'status':'independent exact audit passed; no producer build imported',
            'actual_positive_fundamental_discriminants':witnesses,
            'witness_count':len(witnesses),'maximum_witness_discriminant':max(v['D'] for v in field.values()),
            'exact_unequal_query_pairs_checked':pair_count,
            'minimum_gain_squared':str(min(gains)),'maximum_gain_squared':str(max(gains)),
            'maximum_declared_noise_squared_to_anchor_limit_ratio':str(max(anchor_ratios))}


if __name__=='__main__':
    data=run()
    if '--write' in sys.argv:(HERE/'audit_independent.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({k:v for k,v in data.items() if k!='actual_positive_fundamental_discriminants'},indent=2))
