"""Complete affine-clock bounds using 32-term multiplicative 2-adic blocks.

All odd starting integers are retained through complete positive series; all
omitted valuations receive explicit geometric-tail charges.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import comb,isqrt
import argparse,hashlib,json,sys,time
from flint import acb,arb,ctx
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PRIOR=ROOT/'research/structured_transfer_2026_09/arithmetic'
sys.path.insert(0,str(ROOT/'research/operational_transfer_2026_09/noise'))
from physical import ball,upper,weights,M
K=32

def sqrt_up(q,digits=55):
    q=Q(q);s=10**digits
    if q<0:raise ValueError('negative radicand')
    k=isqrt(q.numerator*s*s//q.denominator)
    return Q(k,s) if Q(k*k,s*s)==q else Q(k+1,s)

def exact_tails():
    u=[Q(comb(k+13,13),4**k) for k in range(K)]
    uK=Q(comb(K+13,13),4**K);r=Q(K+14,4*(K+1))
    return {'block_length':K,'envelope_weights':list(map(str,u)),
      'envelope_squared_mass':str(sum(v*v for v in u)),
      'weighted_envelope_squared_mass':str(sum(k*k*v*v for k,v in enumerate(u))),
      'first_omitted_envelope_weight':str(uK),'omitted_ratio_upper':str(r),
      'omitted_envelope_mass_upper':str(uK/(1-r)),
      'omitted_weighted_envelope_mass_upper':str(uK*(K/(1-r)+r/(1-r)**2))}

def series_data():
    N=1000
    z=sum((ball(Q(1,n*n)) for n in range(1,N+1)),arb())
    L=sum((arb(n).log()/n**2 for n in range(2,N+1)),arb())
    L2=sum((arb(n).log()**2/n**2 for n in range(2,N+1)),arb())
    zu=z+ball(Q(1,N));zl=z+ball(Q(1,N+1))
    Lu=L+(arb(N).log()+1)/N
    L2u=L2+(arb(N).log()**2+2*arb(N).log()+2)/N
    v=arb(2).log();Zo=3*zu/4;Lo=3*Lu/4-v*zl/4
    return {'elementary_sum_cutoff':N,'odd_mass_upper':str(upper(Zo**14)),
      'odd_derivative_mass_upper':str(upper(14*Zo**13*Lo)),
      'log_two_upper':str(upper(v)),
      'second_derivative_upper':str(upper(14*zu**13*L2u+182*zu**12*Lu**2))}

def generate(bits=256):
    if type(bits) is not int or bits<128:raise ValueError('integer precision at least 128')
    start=time.perf_counter();rows=[]
    with ctx.workprec(bits):
        tail=exact_tails();series=series_data()
        for design in ('multi','outer'):
            w=weights(M)
            if design=='multi':
                a=ball(Q(125,65536));w=[(1-a)*v for v in w]
                for j,v in enumerate(weights(2550),3175):w[j]+=a*v
            t=[ball(Q(2*j+1-M,10)) for j in range(M)]
            # Actual sampled phases, not an equidistribution assumption.
            phases=[[acb(0,x*d*arb(2).log()).exp() for x in t] for d in range(1,K)]
            corners=[];s2s=[];s4s=[]
            for sa,sb in ((1,1),(1,-1),(-1,1),(-1,-1)):
                direction=[sa*x/1000+sb for x in t]
                wd2=[ww*d*d for ww,d in zip(w,direction)]
                s2=sum(wd2,arb());s4=sum((ww*d**4 for ww,d in zip(w,direction)),arb())
                correlations=[]
                for lag,phase in enumerate(phases,1):
                    z=sum((a*b for a,b in zip(wd2,phase)),acb())
                    correlations.append({'lag':lag,'normalized_absolute_correlation_upper':str(upper(abs(z)/s2))})
                corners.append({'slope_sign':sa,'offset_sign':sb,'correlations':correlations})
                s2s.append(upper(s2));s4s.append(upper(s4))
            gammas=[max(Q(c['correlations'][d-1]['normalized_absolute_correlation_upper']) for c in corners) for d in range(1,K)]
            # Gershgorin/2ab<=a^2+b^2: sum both sides, including valid extra terms.
            lam=1+2*sum(gammas,Q())
            u2=Q(tail['envelope_squared_mass']);ku2=Q(tail['weighted_envelope_squared_mass'])
            Tu=Q(tail['omitted_envelope_mass_upper']);Tk=Q(tail['omitted_weighted_envelope_mass_upper'])
            O=Q(series['odd_mass_upper']);O1=Q(series['odd_derivative_mass_upper']);v=Q(series['log_two_upper'])
            B=sqrt_up(lam)*(O1*sqrt_up(u2)+v*O*sqrt_up(ku2))+O1*Tu+v*O*Tk
            s2=max(s2s);s4=max(s4s)
            linear=B*sqrt_up(s2)/10**11
            quad=Q(series['second_derivative_upper'])*sqrt_up(s4)/(2*10**22)
            old=next(r for r in json.loads((PRIOR/'clock_bound.json').read_text())['records'] if r['design']==design)
            rows.append({'design':design,'clock_corners':corners,
              'maximum_correlations':list(map(str,gammas)),'gram_operator_upper':str(lam),
              'normalized_direction_squared_norm_upper':str(s2),
              'normalized_direction_fourth_moment_upper':str(s4),
              'sqrt_gram_operator_upper':str(sqrt_up(lam)),
              'envelope_l2_upper':str(sqrt_up(u2)),'weighted_envelope_l2_upper':str(sqrt_up(ku2)),
              'complete_orbit_derivative_norm_upper':str(B),
              'linear_clock_coefficient':str(linear),'quadratic_clock_coefficient':str(quad),
              'prior_pair_linear_clock_coefficient':old['linear_clock_coefficient'],
              'prior_pair_quadratic_clock_coefficient':old['quadratic_clock_coefficient'],
              'prior_pointwise_clock_coefficient':old['prior_pointwise_clock_coefficient']})
    return {'schema':'complete-orbit-affine-clock-v1','bits':bits,'measurement_count':M,
      'base_slope_radius':'1/100000000000000','base_offset_radius':'1/100000000000',
      'predeclared_consequence_multiplier':120,'complete_series':series,'complete_valuation_tail':tail,
      'records':rows,'prior_pair_certificate_sha256':hashlib.sha256((PRIOR/'clock_bound.json').read_bytes()).hexdigest(),
      'producer_wall_seconds':time.perf_counter()-start,
      'source_class':'all integers 0<=a(n)<=d_14(n), a(1)=1, every n>=1'}

def radius(record,multiplier):
    if type(multiplier) not in (str,int,Q):raise ValueError('exact nonnegative multiplier required')
    h=Q(multiplier)
    if h<0:raise ValueError('nonnegative clock multiplier')
    return h*Q(record['linear_clock_coefficient'])+h*h*Q(record['quadratic_clock_coefficient'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bits',type=int,default=256);p.add_argument('--write',action='store_true');a=p.parse_args()
    doc=generate(a.bits)
    if a.write:(HERE/'orbit_bound.json').write_text(json.dumps(doc,indent=2)+'\n')
    print(json.dumps({'bits':a.bits,'seconds':doc['producer_wall_seconds'],'records':[
      {'design':r['design'],'base_radius':float(radius(r,1)),'h120_radius':float(radius(r,120)),
       'derivative':float(Q(r['complete_orbit_derivative_norm_upper'])),
       'gram_operator':float(Q(r['gram_operator_upper']))} for r in doc['records']]},indent=2))
