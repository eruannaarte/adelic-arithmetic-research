"""Complete continuum dual bound and exact-source vertex design certificate."""
from fractions import Fraction as Q
from itertools import product
from math import prod
from pathlib import Path
import argparse,json
from flint import arb,ctx
from cycle1 import ball,enclosure,endpoint

HERE=Path(__file__).resolve().parent
TIMES=tuple(map(Q,('15.790052','25.962780','28.039208','28.695603','29.332467','29.966619')))
DUAL=((Q(25,24),3,Q(1761,2000)),(Q(27,20),3,Q(239,2000)))
HORIZON=Q(109,5)

def differences():
    rows=[]
    for v in product(range(-3,4),repeat=3):
        x=prod(p**max(a,0) for p,a in zip((2,3,5),v))
        y=prod(p**max(-a,0) for p,a in zip((2,3,5),v))
        if x>y:rows.append((v,Q(x,y),sum(a!=0 for a in v)))
    return rows

def dual_upper(horizon=HORIZON,weights=DUAL,cells=4096):
    horizon=Q(horizon)
    if horizon<=0 or cells<1 or any(Q(w)<0 or Q(r)<=1 or k<1 for r,k,w in weights) or sum(Q(w) for r,k,w in weights)!=1:
        raise ValueError('invalid dual domain')
    valid={(ratio,k) for _,ratio,k in differences()}
    if any((Q(r),k) not in valid for r,k,w in weights):
        raise ValueError('dual term is not an actual model vertex difference')
    terms=[(ball(r).log(),k,ball(w)) for r,k,w in weights]
    best=Q();worst=None
    for i in range(cells):
        lo=horizon*i/cells;hi=horizon*(i+1)/cells
        t=arb(ball((lo+hi)/2),ball((hi-lo)/2))
        g=sum((w*(1-(d*t).cos())/k for d,k,w in terms),arb(0))
        bound=endpoint(g.upper())
        if bound>best:best=bound;worst=i
    return best,worst

def vertex_certificate(times=TIMES):
    times=tuple(map(Q,times))
    if len(times)!=6 or len(set(times))!=6 or min(times)<0:raise ValueError('six distinct nonnegative times required')
    rows=[]
    for v,ratio,k in differences():
        d=ball(ratio).log()
        score=sum((1-(ball(t)*d).cos() for t in times),arb(0))/k
        rows.append({'difference':list(v),'ratio':str(ratio),'changed_factors':k,'floor_squared':enclosure(score)})
    lower=min(Q(r['floor_squared'][0]) for r in rows)
    return {'times':list(map(str,times)),'maximum_time':str(max(times)),
            'all_171_vertex_difference_bounds':rows,'floor_lower':enclosure(ball(lower).sqrt())[0],
            'floor_claim':'103/100','passes':lower>Q(103,100)**2}

def build(precision=256):
    with ctx.workprec(precision):
        ub,worst=dual_upper();v=vertex_certificate()
        assert 6*ub<Q(163,200)**2 and v['passes']
        return {'schema':'harmonic-cycle2-v1','dual':{'horizon':str(HORIZON),'cells':4096,
                 'terms':[{'ratio':str(r),'changed_factors':k,'weight':str(w)} for r,k,w in DUAL],
                 'supremum_upper':enclosure(ball(ub))[1],'floor_upper':enclosure((6*ball(ub)).sqrt())[1],
                 'worst_cell':worst,'floor_target':'163/200','all_schedules_rejected':True},
                 'short_vertex_schedule':v,'scope':'vertex separation is not full product-simplex separation'}

def check(precision=256):
    expected=json.loads((HERE/'cycle2_evidence.json').read_text());actual=build(precision)
    if actual!=expected:raise ValueError('fresh source/continuum proof mismatch')
    return actual

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    if a.write:(HERE/'cycle2_evidence.json').write_text(json.dumps(build(),indent=2)+'\n')
    d=check();print('Cycle2 PASS: complete dual cover and all171 vertex differences')
    print(json.dumps({'dual':d['dual'],'short_vertex_floor':d['short_vertex_schedule']['floor_lower']},indent=2))
