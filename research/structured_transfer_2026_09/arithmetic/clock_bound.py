"""Complete affine-clock bounds from one physical log(2) phase correlation.

Every positive integer belongs to precisely one pair (m,2m) with v2(m)
even. No arithmetic coefficients or logarithmic tails are truncated.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import comb, isqrt
import argparse, hashlib, json, sys, time
from flint import acb, arb, ctx

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PRIOR=ROOT/'research/uncertain_transfer_2026_09/noise'
sys.path.insert(0,str(ROOT/'research/operational_transfer_2026_09/noise'))
from physical import ball,upper,dyadic,weights,M

def lower(x,digits=55):
    q=dyadic(x.lower());s=10**digits
    return Q(q.numerator*s//q.denominator,s)

def sqrt_up(q,digits=55):
    q=Q(q)
    if q<0:raise ValueError('nonnegative radicand required')
    s=10**digits;k=isqrt(q.numerator*s*s//q.denominator)
    return Q(k,s) if Q(k*k,s*s)==q else Q(k+1,s)

def ratio_mass_data():
    n=1000
    z=sum((ball(Q(1,k*k)) for k in range(1,n+1)),arb(0))
    l=sum((arb(k).log()/k**2 for k in range(2,n+1)),arb(0))
    l2=sum((arb(k).log()**2/k**2 for k in range(2,n+1)),arb(0))
    zu=z+ball(Q(1,n));zl=z+ball(Q(1,n+1))
    lu=l+(arb(n).log()+1)/n
    ll=l+(arb(n+1).log()+1)/(n+1)
    l2u=l2+(arb(n).log()**2+2*arb(n).log()+2)/n
    log2=arb(2).log()
    zo=3*zl/4
    lo=3*ll/4-log2*zu/4
    if not lo>0:raise ValueError('odd logarithmic series positivity')
    odd_mass_lower=lower(zo**14)
    odd_derivative_lower=lower(14*zo**13*lo)
    c2=upper(14*log2/4)
    rows=[]
    for k in range(0,40,2):
        rlo=Q(k+14,4*(k+1))
        rhi=Q(35,6) if k==0 else Q(k+14,4*k)
        q=min(rlo/(1+rlo)**2,rhi/(1+rhi)**2)
        mass=arb(0)
        for j in (k,k+1):
            mass+=ball(Q(comb(j+13,13),4**j))*(ball(odd_derivative_lower)+j*log2*ball(odd_mass_lower))
        if k==0:mass-=ball(c2)
        mass_lower=lower(mass)
        if mass_lower<=0:raise ValueError('pair mass positive lower bound')
        rows.append({'even_valuation':k,'ratio_lower':str(rlo),'ratio_upper':str(rhi),
                     'minimum_pair_product_fraction':str(q),'complete_pair_derivative_mass_lower':str(mass_lower)})
    return {'elementary_sum_cutoff':n,
            'second_derivative_upper':str(upper(14*zu**13*l2u+182*zu**12*lu**2)),
            'exception_c2_upper':str(c2),'odd_mass_lower':str(odd_mass_lower),
            'odd_derivative_mass_lower':str(odd_derivative_lower),'valuation_classes':rows}

def generate(bits=256):
    started=time.perf_counter()
    if type(bits) is not int or bits<128:raise ValueError('precision must be an integer at least 128')
    prior=json.loads((PRIOR/'approximation.json').read_text())
    derivative=Q(prior['clock_and_derivative']['complete_signal_derivative_upper'])
    records=[]
    with ctx.workprec(bits):
        masses=ratio_mass_data()
        for design in ('multi','outer'):
            w=weights(M)
            if design=='multi':
                alpha=ball(Q(125,65536));w=[(1-alpha)*a for a in w]
                for j,v in enumerate(weights(2550),3175):w[j]+=alpha*v
            t=[ball(Q(2*j+1-M,10)) for j in range(M)]
            phase=[acb(0,x*arb(2).log()).exp() for x in t]
            correlations=[];s2=arb(0);s4=arb(0)
            for sa,sb in ((1,1),(1,-1),(-1,1),(-1,-1)):
                direction=[sa*x/1000+sb for x in t]
                norm2=sum((ww*d*d for ww,d in zip(w,direction)),arb(0))
                norm4=sum((ww*d**4 for ww,d in zip(w,direction)),arb(0))
                corr=sum((ww*d*d*z for ww,d,z in zip(w,direction,phase)),acb(0))
                correlations.append({'slope_sign':sa,'offset_sign':sb,
                                     'normalized_phase_correlation_upper':str(upper(abs(corr)/norm2))})
                if sa==sb==1:s2=norm2;s4=norm4
            gamma=max(Q(c['normalized_phase_correlation_upper']) for c in correlations)
            if not 0<=gamma<1:raise ValueError('strict decorrelation not verified')
            q0=Q(210,1681);f0=sqrt_up(1-2*(1-gamma)*q0)
            paired=f0*derivative+(1-f0)*Q(masses['exception_c2_upper'])
            factors=[]
            for row in masses['valuation_classes']:
                q=Q(row['minimum_pair_product_fraction'])
                f=sqrt_up(1-2*(1-gamma)*q)
                if f>f0:raise ValueError('class bound weaker than global factor')
                paired-=(f0-f)*Q(row['complete_pair_derivative_mass_lower'])
                factors.append({'even_valuation':row['even_valuation'],'pair_norm_factor_upper':str(f)})
            norm2_upper=upper(s2);norm4_upper=upper(s4)
            weighted_length=sqrt_up(norm2_upper)
            fourth_length=sqrt_up(norm4_upper)
            linear=paired*weighted_length/Q(10**11)
            quadratic=Q(masses['second_derivative_upper'])*fourth_length/Q(2*10**22)
            records.append({'design':design,'clock_corners':correlations,
                 'normalized_direction_squared_norm_upper':str(norm2_upper),
                 'normalized_direction_fourth_moment_upper':str(norm4_upper),
                 'maximum_phase_correlation_upper':str(gamma),'global_pair_norm_factor_upper':str(f0),
                 'valuation_norm_factors':factors,'complete_paired_derivative_norm_upper':str(paired),
                 'linear_clock_coefficient':str(linear),'quadratic_clock_coefficient':str(quadratic),
                 'weighted_pointwise_clock_coefficient':str(derivative*weighted_length/Q(10**11)),
                 'prior_pointwise_clock_coefficient':str(derivative*Q(189,10**13))})
    return {'schema':'complete-paired-affine-clock-v1','bits':bits,'measurement_count':M,
            'base_slope_radius':'1/100000000000000','base_offset_radius':'1/100000000000',
            'complete_first_derivative_upper':str(derivative),'complete_mass_data':masses,
            'records':records,'prior_approximation_sha256':hashlib.sha256((PRIOR/'approximation.json').read_bytes()).hexdigest(),
            'producer_wall_seconds':time.perf_counter()-started,
            'source_class':'all integer coefficients 0<=a(n)<=d_14(n), a(1)=1, including every n>=1'}

def radius(record,multiplier):
    if type(multiplier) not in (str,int,Q):raise ValueError('exact nonnegative multiplier required')
    m=Q(multiplier)
    if m<0:raise ValueError('negative clock uncertainty')
    return m*Q(record['linear_clock_coefficient'])+m*m*Q(record['quadratic_clock_coefficient'])

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--bits',type=int,default=256);parser.add_argument('--write',action='store_true')
    args=parser.parse_args();doc=generate(args.bits)
    if args.write:(HERE/'clock_bound.json').write_text(json.dumps(doc,indent=2)+'\n')
    print(json.dumps(doc,indent=2))
