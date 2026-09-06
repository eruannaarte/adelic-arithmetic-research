"""Independent rational consequences, reading/proposal bindings, and controls."""
from fractions import Fraction as Q
from pathlib import Path
from math import factorial,isqrt
import argparse, hashlib, importlib.util, json

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PRIOR=ROOT/'research/uncertain_transfer_2026_09/noise'

def sqrt_lower(q):
    s=10**60;return Q(isqrt(q.numerator*s*s//q.denominator),s)
def family_factor(record,omega):
    p=record['degree'];rows={r['order']:r for r in record['approximants']}
    if sorted(rows)!=list(range(p+1,33)):raise ValueError('complete polynomial order coverage')
    values=[]
    for start,tail in ((p+1,33),(p+2,34)):
        value=sum((Q(rows[k]['weighted_residual_norm_upper'])*omega**k/factorial(k) for k in range(start,33,2)),Q())
        value+=Q(record['weighted_monomial_norm_upper'][str(tail)])*omega**tail/factorial(tail)
        values.append(value)
    return max(values)
def digest_pairs(rows):
    return hashlib.sha256(json.dumps([[str(Q(a)),str(Q(b))] for a,b in rows],separators=(',',':')).encode()).hexdigest()

def check_budget(saved,prior,approx,clock):
    p=approx['degree'];h=Q(saved['clock_multiplier']);rho=Q(saved['normal_residual_upper'])
    if p!=saved['degree'] or saved['design']!=approx['design'] or saved['design']!=clock['design']:raise ValueError('degree/window binding')
    if h not in (1,60) or rho<0 or rho>Q(1,10**30):raise ValueError('clock/residual contract')
    if Q(saved['clock_slope_radius'])!=h/Q(10**14) or Q(saved['clock_offset_radius'])!=h/Q(10**11):raise ValueError('slope/offset radius')
    f=1-Q(prior['augmented_gram_defect']);sf=sqrt_lower(f);omega=3*(1+h/Q(10**14))
    if Q(saved['effective_frequency_upper'])!=omega or Q(saved['amplitude_upper'])!=4000:raise ValueError('frequency/amplitude contract')
    if [Q(saved[k]) for k in ('sensor_radius','mismatch_radius','digital_correction_radius')]!=[Q(4,10**5),Q(1,10**6),Q(1,10**20)]:raise ValueError('complete fixed uncertainty allowances')
    flag=saved['uses_prior_pointwise_clock_bound']
    if type(flag) is not bool:raise ValueError('comparison flag')
    timing=h*Q(clock['prior_pointwise_clock_coefficient']) if flag else h*Q(clock['linear_clock_coefficient'])+h*h*Q(clock['quadratic_clock_coefficient'])
    family=4000*family_factor(approx,omega)
    delta=Q(4,10**5)+Q(1,10**6)+Q(1,10**20)+family+timing
    if Q(saved['clock_radius'])!=timing or Q(saved['family_radius'])!=family or Q(saved['complete_reading_radius'])!=delta or Q(saved['gram_floor'])!=f:raise ValueError('complete budget identity')
    errors=[];gates=[]
    for n in range(2,51):
        bias=Q(prior['complete_coefficient_bias_upper'][n-1]);m=Q(1,2)-bias-n*n*rho/f
        gates.append(m>0 and n**4*delta**2<m*m*f)
        errors.append(bias+n*n*(delta/sf+rho/f))
    if list(map(Q,saved['complete_coefficient_error_bounds']))!=errors or Q(saved['complete_coefficient_error_maximum'])!=max(errors):raise ValueError('coordinate bounds')
    if saved['passing_gates']!=sum(gates) or saved['all_49_strict_rounding_gates']!=all(gates):raise ValueError('strict gate consequence')
    return all(gates)

def check():
    clock=json.loads((HERE/'clock_bound.json').read_text());verified=json.loads((HERE/'checked_clock.json').read_text())
    if not verified['verified'] or verified['clock_bound_sha256']!=hashlib.sha256((HERE/'clock_bound.json').read_bytes()).hexdigest():raise ValueError('clock replay binding')
    approx=json.loads((PRIOR/'approximation.json').read_text());apcheck=json.loads((PRIOR/'checked_approximation.json').read_text())
    if apcheck['approximation_sha256']!=hashlib.sha256((PRIOR/'approximation.json').read_bytes()).hexdigest() or apcheck['full_vector_polynomial_norm_bounds']!=184 or apcheck['complete_remainder_moment_bounds']!=16:raise ValueError('inherited complete approximation binding')
    spec=importlib.util.spec_from_file_location('_complete_tail_checker',ROOT/'research/transfer_theorem_2026_09/noise/check_certificate.py')
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    tail=json.loads((ROOT/'research/transfer_theorem_2026_09/noise/evidence.json').read_text());checker.check(tail,extended=True)
    demo=json.loads((HERE/'demonstration.json').read_text());replay=json.loads((HERE/'precision_replay.json').read_text())
    if not replay['verified'] or not replay['saved_readings_and_proposals_replayed'] or replay['bits']!=384:raise ValueError('384-bit actual-model replay required')
    rows=demo['baseline_fixed_contract_comparisons']
    if [(r['design'],r['degree']) for r in rows]!=[(d,p) for d in ('multi','outer') for p in (6,8,10,12)]:raise ValueError('fixed comparison coverage')
    def premises(design,p):
        return (next(r for r in tail['designs'][design]['degrees'] if r['degree']==p),
                next(r for r in approx['records'] if (r['design'],r['degree'])==(design,p)),
                next(r for r in clock['records'] if r['design']==design))
    for r in rows:
        pp=premises(r['design'],r['degree'])
        for key in ('future_budget','actual_budget'):
            if Q(r[key]['clock_multiplier'])!=1 or check_budget(r[key],*pp)!=(r['degree']==12):raise ValueError('least tested degree consequence')
        cost=r['cost'];d=50+r['degree']
        if cost['augmented_complex_dimension']!=d or cost['classical_full_gram_complex_multiply_accumulates']!=8900*d*d or cost['forward_matrix_complex_entries']!=8900*d:raise ValueError('cost arithmetic')
        if not r['matrix_reconstruction_wall_seconds']>0 or not r['dual_residual_verification_wall_seconds']>0:raise ValueError('measured cost missing')
    data=json.loads((HERE/'data_sixtyfold.json').read_text())
    if len(data['readings'])!=8900 or digest_pairs(data['readings'])!=data['data_sha256'] or replay['data_sha256']!=data['data_sha256']:raise ValueError('actual reading binding')
    if Q(data['true_clock_slope'])!=1+Q(60,10**14) or Q(data['true_clock_offset'])!=Q(60,10**11):raise ValueError('actual enlarged clock')
    outcomes=[]
    for design in ('multi','outer'):
        result=json.loads((HERE/f'result_{design}_sixtyfold.json').read_text());c=result['certificate']
        pp=premises(design,12)
        if not check_budget(result['uncertainty_budget'],*pp):raise ValueError('new clock positive guarantee')
        old_ok=check_budget(result['prior_pointwise_comparison'],*pp)
        if design=='outer' and old_ok:raise ValueError('prior sufficient-gate adverse control')
        if c['status']!='certified_under_declared_model' or c['data_sha256']!=data['data_sha256'] or c['proposal_sha256']!=digest_pairs(result['proposal']):raise ValueError('actual returned proposal binding')
        if c['answer_a1_through_a50']!=data['truth_a1_through_a50']:raise ValueError('integer fixture consequence')
        if Q(c['normal_residual_upper'])!=Q(result['uncertainty_budget']['normal_residual_upper']):raise ValueError('actual normal residual binding')
        errors=list(map(Q,result['uncertainty_budget']['complete_coefficient_error_bounds']))
        for n,error in zip(range(2,51),errors):
            a,b=map(Q,result['proposal'][n-1]);answer=c['answer_a1_through_a50'][n-1]
            if (n*n*a-answer)**2+(n*n*b)**2>error*error:raise ValueError('returned integer outside complex certificate disk')
        outcomes.append({'design':design,'least_passing_tested_degree':12,'sixtyfold_all_49_integers':True,
                         'prior_pointwise_bound_also_passes':old_ok,
                         'maximum_coefficient_error':result['uncertainty_budget']['complete_coefficient_error_maximum']})
    return {'schema':'structured-clock-independent-consequences-v1','verified':True,
            'fixed_degree_future_and_actual_gate_checks':16*49,'enlarged_and_prior_comparison_gate_checks':4*49,
            'returned_integer_complex_disk_checks':98,'outcomes':outcomes,
            'source_scope':'complete divisor envelope; finite synthetic data verify an instance, not a smaller uniform class'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();r=check()
    if a.write:(HERE/'consequences.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))
