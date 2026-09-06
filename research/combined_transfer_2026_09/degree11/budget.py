"""Exact degree-eleven gates; odd/even cutoff logic supports either parity."""
from fractions import Fraction as Q
from math import factorial,isqrt

def exact(value):
    if type(value) not in (Q,str,int):raise ValueError('exact rational value required')
    return Q(value)

def factor(record,omega):
    omega=exact(omega)
    if omega<0 or type(record['degree']) is not int or record['degree']!=11:raise ValueError('degree eleven, nonnegative frequency required')
    rows=record['approximants']
    if [a['order'] for a in rows]!=list(range(12,33)):raise ValueError('missing complete Taylor channel')
    rr={a['order']:Q(a['weighted_residual_norm_upper']) for a in rows}
    mm={int(k):Q(v) for k,v in record['weighted_monomial_norm_upper'].items()}
    if sorted(mm)!=[33,34] or min(list(rr.values())+list(mm.values()))<0:raise ValueError('invalid complete residual bound')
    odd=sum((rr[k]*omega**k/factorial(k) for k in range(13,32,2)),Q())+mm[33]*omega**33/factorial(33)
    even=sum((rr[k]*omega**k/factorial(k) for k in range(12,33,2)),Q())+mm[34]*omega**34/factorial(34)
    return max(odd,even)

def profile(record,approx,clock,rho=Q(1,10**30),amplitude=4000):
    if record['degree']!=11 or approx['degree']!=11:raise ValueError('degree binding')
    if approx.get('design') not in ('multi','outer') or record.get('design')!=approx['design'] or clock.get('design')!=approx['design']:raise ValueError('physical window binding')
    rho=exact(rho);amplitude=exact(amplitude)
    if min(rho,amplitude)<0:raise ValueError('nonnegative budgets required')
    f=1-Q(record['augmented_gram_defect'])
    if f<=0:raise ValueError('positive Gram floor required')
    scale=10**60;sf=Q(isqrt(f.numerator*scale*scale//f.denominator),scale)
    biases=list(map(Q,record['complete_coefficient_bias_upper']))
    if len(biases)!=50 or min(biases)<0:raise ValueError('complete bias vector required')
    kw=factor(approx,3*(1+Q(1,10**14)));family=amplitude*kw
    timing=Q(clock['linear_clock_coefficient'])+Q(clock['quadratic_clock_coefficient'])
    total=Q(4,10**5)+Q(1,10**6)+timing+family+Q(1,10**20)
    gates=[];errors=[]
    for n in range(2,51):
        margin=Q(1,2)-biases[n-1]-n*n*rho/f
        gates.append(margin>0 and n**4*total**2<margin**2*f)
        errors.append(biases[n-1]+n*n*(total/sf+rho/f))
    reserve=min((Q(1,2)-biases[n-1]-n*n*rho/f)*sf/n**2 for n in range(2,51))-Q(4,10**5)-Q(1,10**6)-timing-Q(1,10**20)
    return {'design':approx['design'],'degree':11,'amplitude_upper':str(amplitude),
        'frequency_upper':'3','clock_slope_radius':'1/100000000000000','clock_offset_radius':'1/100000000000',
        'gram_floor':str(f),'weighted_family_factor':str(kw),'family_radius':str(family),
        'clock_radius':str(timing),'sensor_radius':'1/25000','mismatch_radius':'1/1000000',
        'normal_residual_upper':str(rho),'complete_reading_radius':str(total),
        'complete_coefficient_error_bounds':list(map(str,errors)),
        'complete_coefficient_error_maximum':str(max(errors)),
        'strict_sufficient_amplitude_limit':str(reserve/kw),'passing_gates':sum(gates),
        'all_49_strict_rounding_gates':all(gates)}

def operation_counts():
    m,d=8900,61
    return {'measurement_count':m,'augmented_complex_dimension':d,'forward_matrix_complex_entries':m*d,
        'stored_X_XstarW_and_Gram_complex_entries':2*m*d+d*d,
        'classical_full_gram_complex_multiply_accumulates':m*d*d,
        'classical_rhs_complex_multiply_accumulates':m*d,'dense_solve_order':'O(d^3)',
        'meaning':'Classical dense arithmetic counts, not interval timings or a cross-machine benchmark.'}
