"""Independent complete-vector verification of all weighted norm bounds.

Loads the previously reviewed physical window reconstruction but no new
producer code, moment matrix, projected basis, or saved numerical weights.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse, importlib.util, json, hashlib
from flint import arb, ctx, fmpq

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('_old_window_consumer',ROOT/'research/refined_transfer_2026_09/noise/check_approximation.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)


def rational(v):
    if type(v) not in (Q,str,int):raise ValueError('exact rational required')
    return Q(v)


def b(v):
    q=rational(v);return arb(fmpq(q.numerator,q.denominator))


def upper_endpoint(v):
    v=v.upper()
    if not v.is_exact() or not v.is_finite():raise ValueError('bad outward endpoint')
    n,e=map(int,v.man_exp());return Q(n*2**e) if e>=0 else Q(n,2**(-e))


def check_clock(c,bits=384):
    if type(c['sum_cutoff']) is not int or c['sum_cutoff']!=1000 or rational(c['clock_slope_radius'])!=Q(1,10**14) or rational(c['clock_offset_radius'])!=Q(1,10**11):raise ValueError('clock contract')
    if rational(c['maximum_nominal_absolute_time_upper'])!=890:raise ValueError('time domain')
    with ctx.workprec(bits):
        n=1000
        z=sum((b(Q(1,k*k)) for k in range(1,n+1)),arb(0))+b(Q(1,n))
        l=sum((arb(k).log()*b(Q(1,k*k)) for k in range(2,n+1)),arb(0))+(arb(n).log()+1)/n
        if upper_endpoint(z)>rational(c['zeta2_comparison_upper']) or upper_endpoint(l)>rational(c['logarithmic_series_comparison_upper']):raise ValueError('infinite-series comparison')
        if upper_endpoint(14*z**13*l)>rational(c['complete_signal_derivative_upper']):raise ValueError('derivative upper')
    expected=rational(c['complete_signal_derivative_upper'])*(890*Q(1,10**14)+Q(1,10**11))
    if rational(c['complete_clock_distortion_radius'])!=expected:raise ValueError('clock charge')
    return {'verified':True,'complete_signal_derivative_upper':c['complete_signal_derivative_upper'],
            'complete_clock_distortion_radius':str(expected)}


def check_document(doc,bits=384):
    if type(bits) is not int or bits<128:raise ValueError('integer precision at least128 required')
    if doc['schema']!='clocked-weighted-approximation-v1' or type(doc['measurement_count']) is not int or doc['measurement_count']!=8900:raise ValueError('schema or measurement count')
    if any(type(v) is not int for v in doc['tested_degrees']) or doc['tested_degrees']!=[6,8,10,12] or type(doc['even_taylor_cutoff']) is not int or doc['even_taylor_cutoff']!=32:raise ValueError('degree contract')
    if doc['frequency_grid']!=['1/2','1','2','3']:raise ValueError('frequency grid')
    if rational(doc['sensor_radius'])!=Q(4,10**5) or rational(doc['mismatch_radius'])!=Q(1,10**6):raise ValueError('uncertainty contract')
    if list(map(rational,doc['physical_window_coefficients']))!=old.physical_coefficients():raise ValueError('physical coefficient binding')
    if [(r['design'],r['degree']) for r in doc['records']]!=[(d,p) for d in ('multi','outer') for p in (6,8,10,12)]:raise ValueError('design coverage')
    if any(type(r['degree']) is not int or any(type(a['order']) is not int for a in r['approximants']) for r in doc['records']):raise ValueError('integer degree metadata required')
    count=0;moment_count=0
    with ctx.workprec(bits):
        for design in ('multi','outer'):
            w,x=old.actual_grid(design)
            powers=[]
            for t in x:
                row=[arb(1)]
                for k in range(1,69):row.append(row[-1]*t)
                powers.append(row)
            for r in (r for r in doc['records'] if r['design']==design):
                p=r['degree']
                if [a['order'] for a in r['approximants']]!=list(range(p+1,33)):raise ValueError('approximant coverage')
                for entry in r['approximants']:
                    k=entry['order'];poly=list(map(rational,entry['rational_polynomial']))
                    if len(poly)!=p+1 or any(c for j,c in enumerate(poly) if j%2!=k%2):raise ValueError('degree or parity')
                    norm=rational(entry['weighted_residual_norm_upper'])
                    if norm<=0:raise ValueError('norm positivity')
                    coeff=list(map(b,poly));n2=arb(0)
                    for ww,pp in zip(w,powers):
                        residual=pp[k]-sum((c*pp[j] for j,c in enumerate(coeff)),arb(0))
                        n2+=ww*residual*residual
                    if upper_endpoint(n2)>norm*norm:raise ValueError('false complete-vector residual norm')
                    count+=1
                if sorted(r['weighted_monomial_norm_upper'])!=['33','34']:raise ValueError('complete Taylor remainder channels')
                for key,value in r['weighted_monomial_norm_upper'].items():
                    k=int(key);norm=rational(value)
                    n2=sum((ww*pp[2*k] for ww,pp in zip(w,powers)),arb(0))
                    if norm<=0 or upper_endpoint(n2)>norm*norm:raise ValueError('false weighted moment bound')
                    moment_count+=1
    return {'schema':'clocked-weighted-checked-v1','verified':True,'bits':bits,
            'full_vector_polynomial_norm_bounds':count,'complete_remainder_moment_bounds':moment_count,
            'clock':check_clock(doc['clock_and_derivative'],bits)}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bits',type=int,default=384);p.add_argument('--write',action='store_true')
    a=p.parse_args();path=HERE/'approximation.json';result=check_document(json.loads(path.read_text()),a.bits)
    result['approximation_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    if a.write:(HERE/'checked_approximation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
