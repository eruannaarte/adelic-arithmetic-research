"""Independent outward consumer: actual sample sums and complete series tails.

No producer, saved weights, phase samples, or derivative masses are imported.
The supplemental zeta power-series check is independent of the elementary
positive-sum comparisons used for the certificate.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import comb
import argparse, hashlib, importlib.util, json
from flint import arb, arb_series, ctx, fmpq

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PRIOR=ROOT/'research/uncertain_transfer_2026_09/noise'
spec=importlib.util.spec_from_file_location('_reviewed_grid',ROOT/'research/refined_transfer_2026_09/noise/check_approximation.py')
grid=importlib.util.module_from_spec(spec);spec.loader.exec_module(grid)

def q(v):
    if type(v) not in (str,int,Q):raise ValueError('exact rational metadata required')
    return Q(v)
def b(v):
    z=q(v);return arb(fmpq(z.numerator,z.denominator))
def endpoint(v,which='upper'):
    z=getattr(v,which)()
    if not z.is_exact() or not z.is_finite():raise ValueError('invalid interval endpoint')
    n,e=map(int,z.man_exp());return Q(n*2**e) if e>=0 else Q(n,2**(-e))
def require_upper(actual,saved):
    if endpoint(actual)>q(saved):raise ValueError('false outward upper bound')
def require_lower(actual,saved):
    if endpoint(actual,'lower')<q(saved):raise ValueError('false outward lower bound')

def check(doc,bits=384):
    if type(bits) is not int or bits<128:raise ValueError('integer precision at least128 required')
    if doc['schema']!='complete-paired-affine-clock-v1' or type(doc['measurement_count']) is not int or doc['measurement_count']!=8900:raise ValueError('measurement contract')
    if q(doc['base_slope_radius'])!=Q(1,10**14) or q(doc['base_offset_radius'])!=Q(1,10**11):raise ValueError('clock contract')
    if doc['prior_approximation_sha256']!=hashlib.sha256((PRIOR/'approximation.json').read_bytes()).hexdigest():raise ValueError('prior binding')
    prior=json.loads((PRIOR/'approximation.json').read_text())
    D=q(prior['clock_and_derivative']['complete_signal_derivative_upper'])
    if q(doc['complete_first_derivative_upper'])!=D:raise ValueError('first derivative binding')
    masses=doc['complete_mass_data'];n=masses['elementary_sum_cutoff']
    if type(n) is not int or n!=1000:raise ValueError('elementary sum contract')
    if [r['even_valuation'] for r in masses['valuation_classes']]!=list(range(0,40,2)) or any(type(r['even_valuation']) is not int for r in masses['valuation_classes']):raise ValueError('valuation coverage')
    if [r['design'] for r in doc['records']]!=['multi','outer']:raise ValueError('window coverage')
    records=[]
    with ctx.workprec(bits):
        z=sum((b(Q(1,j*j)) for j in range(1,n+1)),arb(0))
        l=sum((arb(j).log()/j**2 for j in range(2,n+1)),arb(0))
        l2=sum((arb(j).log()**2/j**2 for j in range(2,n+1)),arb(0))
        zu=z+b(Q(1,n));zl=z+b(Q(1,n+1))
        lu=l+(arb(n).log()+1)/n;ll=l+(arb(n+1).log()+1)/(n+1)
        l2u=l2+(arb(n).log()**2+2*arb(n).log()+2)/n
        require_upper(14*zu**13*lu,D)
        require_upper(14*zu**13*l2u+182*zu**12*lu**2,masses['second_derivative_upper'])
        c2=14*arb(2).log()/4;require_upper(c2,masses['exception_c2_upper'])
        require_lower((3*zl/4)**14,masses['odd_mass_lower'])
        require_lower(14*(3*zl/4)**13*(3*ll/4-arb(2).log()*zu/4),masses['odd_derivative_mass_lower'])
        for row in masses['valuation_classes']:
            k=row['even_valuation'];rl=Q(k+14,4*(k+1));rh=Q(35,6) if k==0 else Q(k+14,4*k)
            qr=min(rl/(1+rl)**2,rh/(1+rh)**2)
            if q(row['ratio_lower'])!=rl or q(row['ratio_upper'])!=rh or q(row['minimum_pair_product_fraction'])!=qr or qr<Q(210,1681):raise ValueError('pair ratio formula')
            mass=sum((b(Q(comb(j+13,13),4**j))*(b(masses['odd_derivative_mass_lower'])+j*arb(2).log()*b(masses['odd_mass_lower'])) for j in (k,k+1)),arb(0))
            if k==0:mass-=b(masses['exception_c2_upper'])
            if q(row['complete_pair_derivative_mass_lower'])<=0:raise ValueError('positive mass required')
            require_lower(mass,row['complete_pair_derivative_mass_lower'])
        # Independent special-function route: no finite tail comparison here.
        zeta=arb_series([2,1],3).zeta();power=zeta**14
        require_upper(-power[1],D);require_upper(2*power[2],masses['second_derivative_upper'])
        exact_odd_mass=(3*zeta[0]/4)**14
        exact_odd_derivative=14*(3*zeta[0]/4)**13*(-3*zeta[1]/4-arb(2).log()*zeta[0]/4)
        require_lower(exact_odd_mass,masses['odd_mass_lower']);require_lower(exact_odd_derivative,masses['odd_derivative_mass_lower'])
        for r in doc['records']:
            w,x=grid.actual_grid(r['design']);t=[xx*890 for xx in x]
            c=[(tt*arb(2).log()).cos() for tt in t];s=[(tt*arb(2).log()).sin() for tt in t]
            if [(a['slope_sign'],a['offset_sign']) for a in r['clock_corners']]!=[(1,1),(1,-1),(-1,1),(-1,-1)] or any(type(a[k]) is not int for a in r['clock_corners'] for k in ('slope_sign','offset_sign')):raise ValueError('all clock corners required')
            for corner in r['clock_corners']:
                d=[corner['slope_sign']*tt/1000+corner['offset_sign'] for tt in t]
                s2=sum((ww*dd**2 for ww,dd in zip(w,d)),arb(0));s4=sum((ww*dd**4 for ww,dd in zip(w,d)),arb(0))
                real=sum((ww*dd**2*cc for ww,dd,cc in zip(w,d,c)),arb(0));imag=sum((ww*dd**2*ss for ww,dd,ss in zip(w,d,s)),arb(0))
                # Squared comparison avoids importing the producer's sqrt routine.
                gamma=q(corner['normalized_phase_correlation_upper'])
                if gamma<0 or gamma>=1:raise ValueError('correlation range')
                if not (b(gamma)**2*s2**2-real**2-imag**2)>0:raise ValueError('phase correlation not verified')
                require_upper(s2,r['normalized_direction_squared_norm_upper']);require_upper(s4,r['normalized_direction_fourth_moment_upper'])
            gamma=max(q(a['normalized_phase_correlation_upper']) for a in r['clock_corners'])
            if q(r['maximum_phase_correlation_upper'])!=gamma:raise ValueError('corner maximum')
            f0=q(r['global_pair_norm_factor_upper'])
            if not 0<f0<1 or f0*f0<1-2*(1-gamma)*Q(210,1681):raise ValueError('global pair factor')
            factors=r['valuation_norm_factors']
            if [a['even_valuation'] for a in factors]!=list(range(0,40,2)):raise ValueError('factor coverage')
            paired=f0*D+(1-f0)*q(masses['exception_c2_upper'])
            for row,factor in zip(masses['valuation_classes'],factors):
                f=q(factor['pair_norm_factor_upper'])
                if f<0 or f>f0 or f*f<1-2*(1-gamma)*q(row['minimum_pair_product_fraction']):raise ValueError('class pair factor')
                paired-=(f0-f)*q(row['complete_pair_derivative_mass_lower'])
            if q(r['complete_paired_derivative_norm_upper'])!=paired or not 0<paired<D:raise ValueError('complete paired charge')
            linear=q(r['linear_clock_coefficient']);quad=q(r['quadratic_clock_coefficient'])
            if linear<0 or linear**2*10**22<paired**2*q(r['normalized_direction_squared_norm_upper']):raise ValueError('linear clock coefficient')
            if quad<0 or quad**2*4*10**44<q(masses['second_derivative_upper'])**2*q(r['normalized_direction_fourth_moment_upper']):raise ValueError('nonlinear remainder coefficient')
            weighted=q(r['weighted_pointwise_clock_coefficient'])
            if weighted**2*10**22<D**2*q(r['normalized_direction_squared_norm_upper']):raise ValueError('weighted baseline')
            if q(r['prior_pointwise_clock_coefficient'])!=D*Q(189,10**13):raise ValueError('prior pointwise baseline')
            if not linear+quad<weighted<q(r['prior_pointwise_clock_coefficient']):raise ValueError('strict weighted and phase gains')
            records.append({'design':r['design'],'base_complete_clock_radius':str(linear+quad),
                            'sixtyfold_clock_radius':str(60*linear+3600*quad),'verified':True})
    return {'schema':'complete-paired-affine-clock-checked-v1','verified':True,'bits':bits,
            'actual_clock_corner_phase_checks':8,'complete_valuation_classes':20,
            'independent_zeta_derivative_crosscheck':True,'records':records,
            'clock_bound_sha256':hashlib.sha256((HERE/'clock_bound.json').read_bytes()).hexdigest()}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bits',type=int,default=384);p.add_argument('--write',action='store_true')
    a=p.parse_args();r=check(json.loads((HERE/'clock_bound.json').read_text()),a.bits)
    if a.write:(HERE/'checked_clock.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))
