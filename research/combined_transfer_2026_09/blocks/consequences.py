"""Exact independent budget, maximal integer multiplier and returned-query checks."""
from fractions import Fraction as Q
from pathlib import Path
from math import factorial,isqrt
import argparse,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
APPROX=ROOT/'research/uncertain_transfer_2026_09/noise'
OLD=ROOT/'research/structured_transfer_2026_09/arithmetic'

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def digest_pairs(rows):
    return hashlib.sha256(json.dumps([[str(Q(a)),str(Q(b))] for a,b in rows],separators=(',',':')).encode()).hexdigest()

def sqrt_lower(v):
    s=10**60;return Q(isqrt(v.numerator*s*s//v.denominator),s)

def family_factor(approx,omega):
    p=approx['degree'];rr={r['order']:r for r in approx['approximants']}
    if sorted(rr)!=list(range(p+1,33)):raise ValueError('complete approximation coverage')
    values=[]
    for start,tail in [(p+1,33),(p+2,34)]:
        v=sum((Q(rr[k]['weighted_residual_norm_upper'])*omega**k/factorial(k) for k in range(start,33,2)),Q())
        v+=Q(approx['weighted_monomial_norm_upper'][str(tail)])*omega**tail/factorial(tail)
        values.append(v)
    return max(values)

def exact_budget(prior,approx,clock,h=1,rho=Q(1,10**30)):
    h=Q(h);rho=Q(rho);f=1-Q(prior['augmented_gram_defect'])
    if h<0 or rho<0 or rho>Q(1,10**30) or f<=0:raise ValueError('uncertainty/Gram contract')
    omega=3*(1+h/Q(10**14));family=4000*family_factor(approx,omega)
    timing=h*Q(clock['linear_clock_coefficient'])+h*h*Q(clock['quadratic_clock_coefficient'])
    total=Q(4,10**5)+Q(1,10**6)+Q(1,10**20)+timing+family
    sf=sqrt_lower(f);errors=[];gates=[]
    for n in range(2,51):
        A=Q(prior['complete_coefficient_bias_upper'][n-1]);margin=Q(1,2)-A-n*n*rho/f
        gates.append(margin>0 and n**4*total**2<margin*margin*f)
        errors.append(A+n*n*(total/sf+rho/f))
    return {'clock_radius':str(timing),'family_radius':str(family),'complete_reading_radius':str(total),
      'gram_floor':str(f),'complete_coefficient_error_bounds':list(map(str,errors)),
      'complete_coefficient_error_maximum':str(max(errors)),
      'passing_gates':sum(gates),'all_49_strict_rounding_gates':all(gates)}

def check_saved_budget(saved,prior,approx,clock):
    if saved['design']!=approx['design'] or saved['design']!=clock['design'] or saved['degree']!=approx['degree'] or saved['degree']!=prior['degree']:raise ValueError('model/window/degree binding')
    h=Q(saved['clock_multiplier']);rho=Q(saved['normal_residual_upper'])
    if [Q(saved[k]) for k in ('amplitude_upper','sensor_radius','mismatch_radius','digital_correction_radius')]!=[Q(4000),Q(4,10**5),Q(1,10**6),Q(1,10**20)]:raise ValueError('fixed full contract')
    if [Q(saved[k]) for k in ('clock_slope_radius','clock_offset_radius','effective_frequency_upper')]!=[h/Q(10**14),h/Q(10**11),3*(1+h/Q(10**14))]:raise ValueError('clock/frequency binding')
    if saved['uses_prior_pointwise_clock_bound'] is not False:raise ValueError('clock formula selection')
    expected=exact_budget(prior,approx,clock,h,rho)
    for k,v in expected.items():
        if saved[k]!=v:raise ValueError('false complete recovery consequence: '+k)
    return expected['all_49_strict_rounding_gates']

def premises():
    tail=json.loads((ROOT/'research/transfer_theorem_2026_09/noise/evidence.json').read_text())
    checker=load('_inherited_complete_tail_consumer',ROOT/'research/transfer_theorem_2026_09/noise/check_certificate.py')
    checker.check(tail,extended=True)
    approximation=json.loads((APPROX/'approximation.json').read_text())
    replay=json.loads((APPROX/'checked_approximation.json').read_text())
    if replay['approximation_sha256']!=hashlib.sha256((APPROX/'approximation.json').read_bytes()).hexdigest() or replay['full_vector_polynomial_norm_bounds']!=184 or replay['complete_remainder_moment_bounds']!=16:raise ValueError('complete inherited approximation binding')
    orbit=json.loads((HERE/'orbit_bound.json').read_text());checked=json.loads((HERE/'checked_orbit.json').read_text())
    if checked['verified'] is not True or checked['bits']<384 or checked['actual_corner_lag_checks']!=248 or checked['orbit_bound_sha256']!=hashlib.sha256((HERE/'orbit_bound.json').read_bytes()).hexdigest():raise ValueError('complete actual-grid orbit replay binding')
    pair=json.loads((OLD/'clock_bound.json').read_text())
    def lookup(d,p,method='orbit'):
        return (next(r for r in tail['designs'][d]['degrees'] if r['degree']==p),
          next(r for r in approximation['records'] if (r['design'],r['degree'])==(d,p)),
          next(r for r in (orbit if method=='orbit' else pair)['records'] if r['design']==d))
    return lookup

def greatest_integer(lookup,d,method):
    pp=lookup(d,12,method);lo=0;hi=1
    if not exact_budget(*pp,lo)['all_49_strict_rounding_gates']:raise ValueError('zero clock must pass this comparison')
    while exact_budget(*pp,hi)['all_49_strict_rounding_gates']:lo,hi=hi,2*hi
    while hi-lo>1:
        m=(lo+hi)//2
        if exact_budget(*pp,m)['all_49_strict_rounding_gates']:lo=m
        else:hi=m
    return {'design':d,'method':method,'degree':12,'normal_residual_upper':'1/1000000000000000000000000000000',
      'largest_passing_integer_multiplier':lo,'passing_boundary':exact_budget(*pp,lo),
      'next_integer_boundary':exact_budget(*pp,lo+1),
      'scope':'threshold of this monotone sufficient formula; not an optimal experimental tolerance'}

def check_actual(lookup):
    data=json.loads((HERE/'data_h120.json').read_text());replay=json.loads((HERE/'precision_replay.json').read_text())
    if len(data['readings'])!=8900 or digest_pairs(data['readings'])!=data['data_sha256']:raise ValueError('complete physical reading digest')
    if Q(data['true_clock_slope'])!=1+Q(120,10**14) or Q(data['true_clock_offset'])!=Q(120,10**11):raise ValueError('actual enlarged clock')
    if replay['verified'] is not True or replay['bits']<384 or replay['saved_readings_and_proposals_replayed'] is not True or replay['data_sha256']!=data['data_sha256']:raise ValueError('384-bit full physical-model replay binding')
    rows=[]
    for d in ('multi','outer'):
        r=json.loads((HERE/f'result_{d}_h120.json').read_text());c=r['certificate'];b=r['uncertainty_budget'];old=r['prior_pair_comparison']
        if Q(b['clock_multiplier'])!=120 or not check_saved_budget(b,*lookup(d,12)):raise ValueError('new complete actual budget')
        if Q(old['clock_multiplier'])!=120:raise ValueError('same-clock comparison')
        prior_pass=check_saved_budget(old,*lookup(d,12,'pair'))
        if d=='outer' and prior_pass:raise ValueError('prior pair sufficient-gate control')
        if c['status']!='certified_under_declared_model' or c['data_sha256']!=data['data_sha256'] or c['proposal_sha256']!=digest_pairs(r['proposal']):raise ValueError('actual inverse/data binding')
        if c['answer_a1_through_a50']!=data['truth_a1_through_a50'] or Q(c['normal_residual_upper'])!=Q(b['normal_residual_upper']):raise ValueError('actual returned answer and residual')
        for n,E in zip(range(2,51),map(Q,b['complete_coefficient_error_bounds'])):
            re,im=map(Q,r['proposal'][n-1]);answer=c['answer_a1_through_a50'][n-1]
            if (n*n*re-answer)**2+(n*n*im)**2>E*E:raise ValueError('returned integer lies outside certified complex disk')
        rows.append({'design':d,'all_49_integers_recovered':True,'prior_pair_bound_passes':prior_pass,
          'coefficient_error_maximum':b['complete_coefficient_error_maximum'],
          'prior_pair_error_maximum':old['complete_coefficient_error_maximum']})
    return rows

def publication_budget(lookup):
    def ceiling(v):
        scale=10**12
        return Q(-(-v.numerator*scale//v.denominator),scale)
    records=[]
    for design in ('multi','outer'):
        tail,approx,clock=lookup(design,12)
        result=exact_budget(tail,approx,clock,120)
        floor=Q(result['gram_floor']);root=sqrt_lower(floor)
        values={'tail':max(map(Q,tail['complete_coefficient_bias_upper'][1:])),
          'sensor':2500*Q(4,10**5)/root,'mismatch':2500*Q(1,10**6)/root,
          'drift':2500*Q(result['family_radius'])/root,
          'clock':2500*Q(result['clock_radius'])/root,
          'correction':2500*Q(1,10**20)/root,'residual':2500*Q(1,10**30)/floor}
        components={k:ceiling(v) for k,v in values.items()}
        total=sum(components.values(),Q())
        if total>=Q(1,2):raise ValueError('public component display loses its strict margin')
        records.append({'design':design,'degree':12,'clock_multiplier':120,
          'component_upper_bounds':{k:str(v) for k,v in components.items()},
          'decimal_component_upper_bounds':{k:format(float(v),'.12f') for k,v in components.items()},
          'sum_component_upper_bounds':str(total),'sum_decimal':format(float(total),'.12f'),
          'exact_coordinate_maximum':result['complete_coefficient_error_maximum'],
          'interpretation':'Each component bounds its contribution uniformly over n=2..50 and is rounded upward to 12 decimal places. Their sum is an upper bound; component maxima need not occur at the same n. This display uses the future normal-residual premise rho<=1e-30, not a claim for arbitrary computed proposals.'})
    return {'schema':'orbit-clock-publication-budget-v1',
      'fixed_contract':{'amplitude':'4000','frequency':'3','sensor_radius':'1/25000',
        'mismatch_radius':'1/1000000','clock_slope_radius':'3/2500000000000',
        'clock_offset_radius':'3/2500000000','correction_radius':'1/100000000000000000000',
        'normal_residual_upper':'1/1000000000000000000000000000000'},'records':records}

def run(write=False):
    lookup=premises();prior_budget=load('_independent_budget_producer',OLD/'budget.py')
    comparisons=[]
    for d in ('multi','outer'):
        for p in (6,8,10,12):
            for h in (1,60,120):
                for method in ('orbit','pair'):
                    pp=lookup(d,p,method);r=prior_budget.profile(*pp,h)
                    check_saved_budget(r,*pp)
                    comparisons.append({'method':method,'budget':r})
    boundaries=[greatest_integer(lookup,d,m) for d in ('multi','outer') for m in ('orbit','pair')]
    actual=check_actual(lookup)
    public=publication_budget(lookup)
    if write:(HERE/'publication_budget.json').write_text(json.dumps(public,indent=2)+'\n')
    elif json.loads((HERE/'publication_budget.json').read_text())!=public:raise ValueError('public component budget mismatch')
    doc={'schema':'complete-orbit-clock-consequences-v1','verified':True,
      'fixed_amplitude':'4000','fixed_frequency':'3','fixed_sensor_radius':'1/25000',
      'fixed_mismatch_radius':'1/1000000','strict_rounding_threshold':'1/2',
      'compared_degrees':[6,8,10,12],'degree_eleven_scope':'verified separately by the degree11 package',
      'comparisons':comparisons,'integer_multiplier_boundaries':boundaries,'actual_h120_results':actual,
      'complete_budget_gate_checks':len(comparisons)*49,'boundary_gate_checks':len(boundaries)*2*49,
      'actual_complex_disk_checks':98,'orbit_bound_sha256':hashlib.sha256((HERE/'orbit_bound.json').read_bytes()).hexdigest()}
    if write:(HERE/'consequences.json').write_text(json.dumps(doc,indent=2)+'\n')
    else:
        saved=json.loads((HERE/'consequences.json').read_text())
        if saved!=doc:raise ValueError('saved consequences mismatch independent replay')
    return {'verified':True,'complete_budget_gate_checks':len(comparisons)*49,
      'integer_multiplier_boundaries':[{k:r[k] for k in ('design','method','largest_passing_integer_multiplier')} for r in boundaries],
      'actual_h120_results':[{**r,'coefficient_error_maximum':float(Q(r['coefficient_error_maximum'])),'prior_pair_error_maximum':float(Q(r['prior_pair_error_maximum']))} for r in actual]}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();print(json.dumps(run(a.write),indent=2))
