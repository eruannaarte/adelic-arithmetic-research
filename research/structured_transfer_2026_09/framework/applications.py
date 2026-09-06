"""Exact common consequences of the separately reconstructed physical premises."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json
from transfer import directional_gate,pair_budget,integer_gate

HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent
ROOT=HERE.parents[2]
inputs={}


def read(path):
    inputs[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    return json.loads(path.read_text())


def need(test,message):
    if not test:raise ValueError(message)


def spatial():
    d=read(PACKAGE/'resolution/checked.json')
    gate=directional_gate(d['source_floor'],d['label_pair_floor'],
        d['structured_direction_radius'],d['structured_inverse_radius'],d['unstructured_remainder_radius'])
    need(gate['passed'] and not gate['uniform_accuracy'],'directional improvement must be material')
    h,g=Q(d['clock_radius']),Q(d['potential_radius'])
    remainder=h*h/2+128*h*g+Q(128,3)*g*g+(h+g)*Q(1,10**12)
    need(remainder==Q(d['remainders']['total_nonlinear_radius']),'complete mixed nonlinear remainder')
    isotropic=Q(d['sensor_relative_radius'])+Q(2,10**9)+remainder
    need(isotropic==Q(d['unstructured_remainder_radius']),'isotropic error sum')
    need(Q(d['structured_direction_radius'])<h*Q(3,125)+g*Q(3,125),'joint forward gain')
    need(Q(d['structured_inverse_radius'])<18*h+8*g,'joint inverse gain')
    # This comparison optimizes only the preceding scalar formula's allowance,
    # not all possible generic generator arguments.
    old_g_upper=Q(1401,10**12)
    old_delta=Q(d['sensor_relative_radius'])+Q(2,10**9)+Q(37,1000)*h+Q(32,3)*old_g_upper
    need(old_delta**2>=Q(d['source_floor'])/10**6,'preceding scalar formula upper limit')
    need(g/old_g_upper>1784,'fair preceding-formula comparison')
    raw=read(PACKAGE/'resolution/decoded.json')
    need(raw['case_count']==12 and all(c['status']=='unique' for c in raw['cases']),'potential raw recoveries')
    return {'verified':True,'directional_gate':gate,'direction_cells':d['case_cells'],
        'joint_forward_vs_separate_ratio':str(Q(d['structured_direction_radius'])/(h*Q(3,125)+g*Q(3,125))),
        'joint_inverse_vs_separate_ratio':str(Q(d['structured_inverse_radius'])/(18*h+8*g)),
        'potential_radius':str(g),'prior_scalar_formula_potential_upper_limit':str(old_g_upper),
        'improvement_over_this_upper_limit':str(g/old_g_upper),'raw_cases':12}


def six_rows():
    cert=read(PACKAGE/'six_rows/certificate_6.json')
    checked=read(PACKAGE/'six_rows/checked_6.json')
    delta=Q(cert['sensor_relative_radius'])+Q(cert['operator_relative_radius'])+Q(cert['numerical_relative_radius'])
    b=delta/Q(cert['normalization_lower'])
    pairs=0;individual=0
    for record in cert['records']:
        need(all(Q(x)>0 for x in record['principal_minor_lower_bounds']),'positive-minor premise')
        if len(record['case'])==2:
            a=Q(record['source_split_weight'])
            need(0<a<1 and pair_budget(b,b,b*b/a,b*b/(1-a)),'weighted two-source incidence')
            pairs+=1
        else:
            individual+=1
    need(pairs+individual==checked['whole_cell_records']==1278,'complete six-row record count')
    metric=checked['metrics']['L2'];mu=Q(metric['individual_approximate_map_floor'])
    need(delta**2<mu/10**6,'six-row source inverse error')
    comparison=read(PACKAGE/'six_rows/uniform_comparison_checked.json')
    need(Q(comparison['ratio_upper'])<1,'uniform pair-floor failure witness')
    decoded=read(PACKAGE/'six_rows/decoded.json')
    need(decoded['verified'] and decoded['case_count']==decoded['unique_correct_targets']==60,'all raw six-row examples')
    return {'verified':True,'weighted_pair_records':pairs,'individual_records':individual,
        'records':pairs+individual,'source_error_squared_upper':str(delta*delta/mu),
        'uniform_pair_floor_ratio_upper':comparison['ratio_upper'],'raw_cases':60}


def arithmetic():
    clock=read(PACKAGE/'arithmetic/clock_bound.json')
    demo=read(PACKAGE/'arithmetic/demonstration.json')
    tails=read(ROOT/'research/transfer_theorem_2026_09/noise/evidence.json')
    baseline=[];enlarged=[];gates=0
    for row in demo['baseline_fixed_contract_comparisons']:
        for kind in ('actual_budget','future_budget'):
            p=row[kind];n_pass=0
            record=next(r for r in tails['designs'][p['design']]['degrees'] if r['degree']==p['degree'])
            f=1-Q(record['augmented_gram_defect'])
            need(f==Q(p['gram_floor']),'baseline complete-tail Gram premise')
            for n in range(2,51):
                ok=integer_gate(n,record['complete_coefficient_bias_upper'][n-1],f,p['normal_residual_upper'],p['complete_reading_radius'])
                n_pass+=ok;gates+=1
            need(n_pass==p['passing_gates'],'baseline degree gates')
            if kind=='future_budget':
                need(Q(p['normal_residual_upper'])==Q(1,10**30),'future residual scope')
                baseline.append({'design':p['design'],'degree':p['degree'],'passing_gates':n_pass})
    need(all(r['passing_gates']==49 if r['degree']==12 else r['passing_gates']<49 for r in baseline),'least tested degree')
    for design in ('multi','outer'):
        result=read(PACKAGE/f'arithmetic/result_{design}_sixtyfold.json')
        bound=next(r for r in clock['records'] if r['design']==design)
        new_radius=60*Q(bound['linear_clock_coefficient'])+3600*Q(bound['quadratic_clock_coefficient'])
        need(new_radius==Q(result['uncertainty_budget']['clock_radius']),'complete enlarged clock radius')
        outcomes=[]
        record=next(r for r in tails['designs'][design]['degrees'] if r['degree']==12)
        for key in ('uncertainty_budget','prior_pointwise_comparison'):
            p=result[key];n_pass=0
            f=1-Q(record['augmented_gram_defect'])
            for n in range(2,51):
                n_pass+=integer_gate(n,record['complete_coefficient_bias_upper'][n-1],f,p['normal_residual_upper'],p['complete_reading_radius'])
                gates+=1
            need(n_pass==p['passing_gates'],'enlarged/old comparison gates')
            outcomes.append(n_pass)
        need(outcomes[0]==49,'all new integer queries')
        if design=='outer':need(outcomes[1]<49,'old outer bound must fail atsame requirements')
        enlarged.append({'design':design,'new_passing_gates':outcomes[0],'old_passing_gates':outcomes[1],
            'new_clock_radius':str(new_radius),
            'complete_coefficient_error_upper':result['uncertainty_budget']['complete_coefficient_error_maximum']})
    need(gates==980,'integer gate extent')
    return {'verified':True,'total_actual_future_comparison_gates':gates,
        'least_tested_passing_degree':12,'fixed_degree_cases':baseline,'enlarged_clock_results':enlarged}


def check():
    result={'verified':True,'spatial':spatial(),'six_rows':six_rows(),'arithmetic':arithmetic(),
        'premise':'Independent complete-time/physical-series/actual-residual consumers establish the recorded premises; this adapter checks exact transfer consequences.'}
    result['input_sha256']=dict(inputs)
    return result


if __name__=='__main__':
    result=check()
    (HERE/'applications.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='input_sha256'},indent=2))
