"""Exact consequences of complete arithmetic tails and declared uncertainties."""
from fractions import Fraction as Q
from math import factorial, isqrt


def exact(v):
    if type(v) not in (Q,str,int):raise ValueError('exact rational required')
    return Q(v)


def sqrt_lower(q):
    q=exact(q)
    if q<=0:raise ValueError('positive Gram floor required')
    scale=10**60
    return Q(isqrt(q.numerator*scale*scale//q.denominator),scale)


def factor(record,omega):
    omega=exact(omega)
    if omega<0:raise ValueError('nonnegative frequency upper bound required')
    p=record['degree']
    if type(p) is not int or p not in (6,8,10,12):raise ValueError('supported integer degree required')
    rr={a['order']:exact(a['weighted_residual_norm_upper']) for a in record['approximants']}
    if sorted(rr)!=list(range(p+1,33)) or any(x<0 for x in rr.values()):raise ValueError('residual coverage')
    mm={int(k):exact(v) for k,v in record['weighted_monomial_norm_upper'].items()}
    if sorted(mm)!=[33,34] or min(mm.values())<0:raise ValueError('Taylor remainder coverage')
    odd=sum((rr[k]*omega**k/Q(factorial(k)) for k in range(p+1,32,2)),Q())+mm[33]*omega**33/Q(factorial(33))
    even=sum((rr[k]*omega**k/Q(factorial(k)) for k in range(p+2,33,2)),Q())+mm[34]*omega**34/Q(factorial(34))
    return max(odd,even)


def profile(prior,approx,rho,omega,amplitude,clock,eta=Q(4,10**5),mismatch=Q(1,10**6)):
    rho,omega,amplitude,clock,eta,mismatch=map(exact,(rho,omega,amplitude,clock,eta,mismatch))
    if min(rho,omega,amplitude,clock,eta,mismatch)<0:raise ValueError('negative uncertainty or residual')
    if prior['degree']!=approx['degree']:raise ValueError('degree mismatch')
    f=1-exact(prior['augmented_gram_defect']);sf=sqrt_lower(f)
    biases=list(map(exact,prior['complete_coefficient_bias_upper']))
    if len(biases)!=50 or min(biases)<0:raise ValueError('complete-tail bias dimensions/sign')
    kw=factor(approx,(1+Q(1,10**14))*omega)
    family=amplitude*kw
    total=eta+mismatch+clock+family+Q(1,10**20)
    reserve=min((Q(1,2)-biases[n-1]-n*n*rho/f)*sf/n**2 for n in range(2,51))-eta-mismatch-clock-Q(1,10**20)
    gates=[];errors=[]
    for n in range(2,51):
        margin=Q(1,2)-biases[n-1]-n*n*rho/f
        gates.append(margin>0 and n**4*total**2<margin**2*f)
        errors.append(biases[n-1]+n*n*(total/sf+rho/f))
    return {'design':approx['design'],'degree':approx['degree'],'frequency_upper':str(omega),
            'effective_frequency_upper':str((1+Q(1,10**14))*omega),
            'amplitude_upper':str(amplitude),'weighted_family_factor':str(kw),
            'sensor_radius':str(eta),'mismatch_radius':str(mismatch),'clock_radius':str(clock),
            'family_radius':str(family),'normal_residual_upper':str(rho),'gram_floor':str(f),
            'complete_bias_maximum':str(max(biases[1:])),
            'sufficient_family_radius_limit':str(reserve),
            'strict_sufficient_amplitude_limit':str(reserve/kw) if kw else None,
            'complete_coefficient_error_maximum':str(max(errors)),
            'all_49_strict_rounding_gates':all(gates),'passing_gates':sum(gates)}
