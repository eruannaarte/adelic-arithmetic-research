"""Q2: exact rational bounds for an analytic infinite-field infimum theorem."""
from fractions import Fraction as F
from math import isqrt
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent


def sqrt_bounds(x,bits=100):
    x=F(x)
    if x<0:raise ValueError('negative radicand')
    s=1<<bits;k=isqrt(x.numerator*s*s//x.denominator)
    return F(k,s),F(k+1,s)


def build():
    M=100
    partial=sum((F(1,n**8) for n in range(1,M+1)),F())
    zlo=partial+F(1,7*(M+1)**7);zhi=partial+F(1,7*M**7)
    radius=(sqrt_bounds(zlo/2500)[0],sqrt_bounds(zhi/2500)[1])
    approximants=[]
    for N in (50,500,5000,50000):
        extra=F(16,N*N)
        upper=sqrt_bounds(zhi/625+extra)[1]/2
        approximants.append({'prefix_length':N,'distance_squared_excess_upper':str(extra),
                             'half_distance_upper':str(upper)})
    return {'schema':'quadratic-infinite-infimum-v1','metric':'l2 of complete coefficients a(n)/n^2',
            'zeta8_interval':list(map(str,(zlo,zhi))),'critical_closed_radius_interval':list(map(str,radius)),
            'distance_squared_infimum':'zeta(8)/625','infimum_attained_by_field_pair':False,
            'query_uniqueness_at_critical_closed_radius':True,
            'approximating_actual_field_pairs':approximants,
            'uniform_tail_bound':'sum_{n>N} d2(n)^2/n^4 <= zeta(2)^4/N^2 < 16/N^2'}


def check(doc):
    expected=build()
    if doc!=expected:raise ValueError('infinite-geometry rational consequence differs')
    lo,hi=map(F,doc['critical_closed_radius_interval'])
    if not F(2004073,10**8)<lo<hi<F(2004074,10**8):raise ValueError('radius display failed')
    # Exact local divisor inequality, whose universal polynomial proof is in PROOFS.
    for e in range(100):
        if (e+1)*(e+2)*(e+3)//6 < (e+1)**2:raise ValueError('divisor-square inequality failed')
    return {'verified':True,'radius_interval_decimal':[float(lo),float(hi)],
            'radius_endpoint_included':True,'scope':'existence of a query decoder on promised full-sequence data; no efficient algorithm claim'}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    path=HERE/'infinite_geometry.json'
    if a.write:path.write_text(json.dumps(build(),indent=2)+'\n')
    print(json.dumps(check(json.loads(path.read_text())),indent=2))
