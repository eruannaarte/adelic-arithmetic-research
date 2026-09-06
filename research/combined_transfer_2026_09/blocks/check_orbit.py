"""Independent consumer: full actual-grid sums, exact tails, zeta crosscheck.

No orbit producer, saved phases, saved weights or numerical Gram are imported.
The physical windows are rebuilt from original literal binary coefficients.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import comb
import argparse,hashlib,importlib.util,json,time
from flint import arb,arb_series,ctx,fmpq
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PRIOR=ROOT/'research/structured_transfer_2026_09/arithmetic'
spec=importlib.util.spec_from_file_location('_independent_window',ROOT/'research/refined_transfer_2026_09/noise/check_approximation.py')
grid=importlib.util.module_from_spec(spec);spec.loader.exec_module(grid)

def q(x):
    if type(x) not in (str,int,Q):raise ValueError('exact rational metadata required')
    return Q(x)
def b(x):
    v=q(x);return arb(fmpq(v.numerator,v.denominator))
def endpoint(x,side='upper'):
    a=getattr(x,side)()
    if not a.is_exact() or not a.is_finite():raise ValueError('invalid ball endpoint')
    m,e=map(int,a.man_exp());return Q(m*2**e) if e>=0 else Q(m,2**(-e))
def require_upper(actual,bound):
    if endpoint(actual)>q(bound):raise ValueError('invalid outward upper bound')
def sqrt_certificate(root,value):
    if q(root)<0 or q(root)**2<q(value):raise ValueError('false square-root bound')

def check(doc,bits=384):
    start=time.perf_counter()
    if type(bits) is not int or bits<128:raise ValueError('integer precision at least 128')
    if doc['schema']!='complete-orbit-affine-clock-v1' or type(doc['measurement_count']) is not int or doc['measurement_count']!=8900:raise ValueError('measurement contract')
    if doc['source_class']!='all integers 0<=a(n)<=d_14(n), a(1)=1, every n>=1':raise ValueError('source contract')
    if q(doc['base_slope_radius'])!=Q(1,10**14) or q(doc['base_offset_radius'])!=Q(1,10**11):raise ValueError('clock contract')
    if type(doc['predeclared_consequence_multiplier']) is not int or doc['predeclared_consequence_multiplier']!=120:raise ValueError('predeclared consequence')
    if doc['prior_pair_certificate_sha256']!=hashlib.sha256((PRIOR/'clock_bound.json').read_bytes()).hexdigest():raise ValueError('prior comparison binding')
    old=json.loads((PRIOR/'clock_bound.json').read_text())
    if [r['design'] for r in doc['records']]!=['multi','outer']:raise ValueError('window coverage')
    tail=doc['complete_valuation_tail'];K=tail['block_length']
    if type(K) is not int or K!=32:raise ValueError('finite block contract')
    u=[Q(comb(k+13,13),4**k) for k in range(K)]
    if list(map(q,tail['envelope_weights']))!=u:raise ValueError('multiplicative envelope')
    U2=sum(v*v for v in u);V2=sum(k*k*v*v for k,v in enumerate(u))
    if q(tail['envelope_squared_mass'])!=U2 or q(tail['weighted_envelope_squared_mass'])!=V2:raise ValueError('finite envelope mass')
    uK=Q(comb(K+13,13),4**K);r=Q(K+14,4*(K+1))
    if q(tail['first_omitted_envelope_weight'])!=uK or q(tail['omitted_ratio_upper'])!=r or not 0<r<1:raise ValueError('omitted ratio')
    Tu=uK/(1-r);Tk=uK*(K/(1-r)+r/(1-r)**2)
    if q(tail['omitted_envelope_mass_upper'])!=Tu or q(tail['omitted_weighted_envelope_mass_upper'])!=Tk:raise ValueError('complete geometric tail')
    series=doc['complete_series'];N=series['elementary_sum_cutoff']
    if type(N) is not int or N!=1000:raise ValueError('elementary series contract')
    # Reject structural corruption before the expensive actual-grid replay.
    for rec in doc['records']:
        if [(c['slope_sign'],c['offset_sign']) for c in rec['clock_corners']]!=[(1,1),(1,-1),(-1,1),(-1,-1)]:raise ValueError('clock corner coverage')
        for c in rec['clock_corners']:
            if any(type(c[k]) is not int for k in ('slope_sign','offset_sign')):raise ValueError('clock signs')
            if [v['lag'] for v in c['correlations']]!=list(range(1,K)) or any(type(v['lag']) is not int for v in c['correlations']):raise ValueError('phase lag coverage')
            if any(not 0<q(v['normalized_absolute_correlation_upper'])<1 for v in c['correlations']):raise ValueError('strict correlation interval')
    outcomes=[]
    with ctx.workprec(bits):
        z=sum((b(Q(1,n*n)) for n in range(1,N+1)),arb())
        L=sum((arb(n).log()/n**2 for n in range(2,N+1)),arb())
        L2=sum((arb(n).log()**2/n**2 for n in range(2,N+1)),arb())
        zu=z+b(Q(1,N));zl=z+b(Q(1,N+1));Lu=L+(arb(N).log()+1)/N
        L2u=L2+(arb(N).log()**2+2*arb(N).log()+2)/N
        v=arb(2).log();Zo=3*zu/4;Lo=3*Lu/4-v*zl/4
        require_upper(Zo**14,series['odd_mass_upper'])
        require_upper(14*Zo**13*Lo,series['odd_derivative_mass_upper'])
        require_upper(v,series['log_two_upper'])
        require_upper(14*zu**13*L2u+182*zu**12*Lu**2,series['second_derivative_upper'])
        # Independent accepted Arb special-function route verifies the complete
        # generating series without the elementary finite sums.
        zs=arb_series([2,1],3).zeta();p=zs**14
        require_upper((3*zs[0]/4)**14,series['odd_mass_upper'])
        require_upper(14*(3*zs[0]/4)**13*(-3*zs[1]/4-v*zs[0]/4),series['odd_derivative_mass_upper'])
        require_upper(2*p[2],series['second_derivative_upper'])
        for rec in doc['records']:
            w,x=grid.actual_grid(rec['design']);t=[xx*890 for xx in x]
            corner_data=[]
            for c in rec['clock_corners']:
                d=[c['slope_sign']*tt/1000+c['offset_sign'] for tt in t]
                wd2=[ww*dd**2 for ww,dd in zip(w,d)]
                s2=sum(wd2,arb());s4=sum((ww*dd**4 for ww,dd in zip(w,d)),arb())
                require_upper(s2,rec['normalized_direction_squared_norm_upper'])
                require_upper(s4,rec['normalized_direction_fourth_moment_upper'])
                corner_data.append((wd2,s2))
            for lag in range(1,K):
                angle=[lag*tt*v for tt in t]
                cs=[a.cos() for a in angle];sn=[a.sin() for a in angle]
                for c,(wd2,s2) in zip(rec['clock_corners'],corner_data):
                    real=sum((a*c for a,c in zip(wd2,cs)),arb());imag=sum((a*s for a,s in zip(wd2,sn)),arb())
                    gamma=q(c['correlations'][lag-1]['normalized_absolute_correlation_upper'])
                    if not (b(gamma)**2*s2**2-real**2-imag**2)>0:raise ValueError('actual phase correlation bound false')
            gamma=[max(q(c['correlations'][lag-1]['normalized_absolute_correlation_upper']) for c in rec['clock_corners']) for lag in range(1,K)]
            if list(map(q,rec['maximum_correlations']))!=gamma:raise ValueError('corner maximum')
            lam=1+2*sum(gamma,Q())
            if q(rec['gram_operator_upper'])!=lam:raise ValueError('Gram operator inequality')
            sqrt_certificate(rec['sqrt_gram_operator_upper'],lam)
            sqrt_certificate(rec['envelope_l2_upper'],U2)
            sqrt_certificate(rec['weighted_envelope_l2_upper'],V2)
            O=q(series['odd_mass_upper']);O1=q(series['odd_derivative_mass_upper']);lv=q(series['log_two_upper'])
            B=q(rec['sqrt_gram_operator_upper'])*(O1*q(rec['envelope_l2_upper'])+lv*O*q(rec['weighted_envelope_l2_upper']))+O1*Tu+lv*O*Tk
            if q(rec['complete_orbit_derivative_norm_upper'])!=B:raise ValueError('complete orbit formula')
            linear=q(rec['linear_clock_coefficient']);quad=q(rec['quadratic_clock_coefficient'])
            if linear<=0 or linear**2*10**22<B**2*q(rec['normalized_direction_squared_norm_upper']):raise ValueError('linear coefficient')
            if quad<=0 or quad**2*4*10**44<q(series['second_derivative_upper'])**2*q(rec['normalized_direction_fourth_moment_upper']):raise ValueError('nonlinear coefficient')
            oldrec=next(r for r in old['records'] if r['design']==rec['design'])
            for new,oldkey in [('prior_pair_linear_clock_coefficient','linear_clock_coefficient'),('prior_pair_quadratic_clock_coefficient','quadratic_clock_coefficient'),('prior_pointwise_clock_coefficient','prior_pointwise_clock_coefficient')]:
                if q(rec[new])!=q(oldrec[oldkey]):raise ValueError('historical comparison identity')
            previous=q(rec['prior_pair_linear_clock_coefficient'])+q(rec['prior_pair_quadratic_clock_coefficient'])
            if not linear+quad<Q(47,100)*previous:raise ValueError('stated phase block gain')
            outcomes.append({'design':rec['design'],'base_complete_clock_radius':str(linear+quad),
              'h120_complete_clock_radius':str(120*linear+14400*quad),'verified':True})
    return {'schema':'complete-orbit-affine-clock-checked-v1','verified':True,'bits':bits,
      'actual_corner_lag_checks':248,'block_length':K,'all_odd_starting_integers_included':True,
      'all_omitted_valuations_included':True,'independent_zeta_derivative_crosscheck':True,
      'orbit_bound_sha256':hashlib.sha256((HERE/'orbit_bound.json').read_bytes()).hexdigest(),
      'wall_seconds':time.perf_counter()-start,'records':outcomes}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bits',type=int,default=384);p.add_argument('--write',action='store_true');a=p.parse_args()
    doc=check(json.loads((HERE/'orbit_bound.json').read_text()),a.bits)
    if a.write:(HERE/'checked_orbit.json').write_text(json.dumps(doc,indent=2)+'\n')
    print(json.dumps(doc,indent=2))
