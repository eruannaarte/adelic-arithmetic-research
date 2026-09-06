"""Exact complete recovery gates with a selectable shared clock rectangle."""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('_inherited_family_budget',ROOT/'research/uncertain_transfer_2026_09/noise/budget.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
factor=old.factor

def profile(prior,approx,clock_record,multiplier=1,rho=Q(1,10**30),old_clock=False):
    multiplier=old.exact(multiplier);rho=old.exact(rho)
    if multiplier<0 or rho<0 or type(old_clock) is not bool:raise ValueError('nonnegative exact uncertainties and boolean comparison flag required')
    p=approx['degree']
    if type(p) is not int or p not in (6,8,10,12) or prior['degree']!=p:raise ValueError('tested degree binding')
    if approx['design']!=clock_record['design']:raise ValueError('physical window binding')
    f=1-Q(prior['augmented_gram_defect']);sf=old.sqrt_lower(f)
    biases=list(map(Q,prior['complete_coefficient_bias_upper']))
    if len(biases)!=50 or min(biases)<0:raise ValueError('complete arithmetic-tail dimensions')
    eps_a=multiplier/Q(10**14);eps_b=multiplier/Q(10**11)
    omega=Q(3)*(1+eps_a);family=4000*factor(approx,omega)
    timing=(multiplier*Q(clock_record['prior_pointwise_clock_coefficient']) if old_clock else
            multiplier*Q(clock_record['linear_clock_coefficient'])+multiplier**2*Q(clock_record['quadratic_clock_coefficient']))
    total=Q(4,10**5)+Q(1,10**6)+timing+family+Q(1,10**20)
    errors=[];gates=[]
    for n in range(2,51):
        margin=Q(1,2)-biases[n-1]-n*n*rho/f
        gates.append(margin>0 and n**4*total**2<margin**2*f)
        errors.append(biases[n-1]+n*n*(total/sf+rho/f))
    return {'design':approx['design'],'degree':p,'clock_multiplier':str(multiplier),
            'clock_slope_radius':str(eps_a),'clock_offset_radius':str(eps_b),
            'effective_frequency_upper':str(omega),'amplitude_upper':'4000',
            'sensor_radius':'1/25000','mismatch_radius':'1/1000000','digital_correction_radius':'1/100000000000000000000',
            'clock_radius':str(timing),'family_radius':str(family),'complete_reading_radius':str(total),
            'normal_residual_upper':str(rho),'gram_floor':str(f),
            'complete_coefficient_error_bounds':list(map(str,errors)),
            'complete_coefficient_error_maximum':str(max(errors)),
            'passing_gates':sum(gates),'all_49_strict_rounding_gates':all(gates),
            'uses_prior_pointwise_clock_bound':old_clock}

def operation_counts(degree):
    if type(degree) is not int or degree not in (6,8,10,12):raise ValueError('tested integer degree required')
    m=8900;d=50+degree
    return {'measurement_count':m,'augmented_complex_dimension':d,
            'forward_matrix_complex_entries':m*d,
            'stored_X_XstarW_and_Gram_complex_entries':2*m*d+d*d,
            'classical_full_gram_complex_multiply_accumulates':m*d*d,
            'classical_rhs_complex_multiply_accumulates':m*d,
            'dense_solve_asymptotic_arithmetic_order':'O(d^3)',
            'counts_meaning':'Declared classical dense arithmetic counts; Arb may use other matrix algorithms. Timings include interval arithmetic and setup, and are not inferred from these counts.'}
