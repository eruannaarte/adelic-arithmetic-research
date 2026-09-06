"""Complete recovery budget and degree comparison using reconstructed residuals."""
from pathlib import Path
from fractions import Fraction as Q
import argparse, hashlib, json, sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'research/operational_transfer_2026_09/noise'))
from physical import load_prior,parse_pairs,digest_pairs
sys.path.insert(0,str(HERE))
from budget import profile


def build():
    approximation=json.loads((HERE/'approximation.json').read_text())
    prior=load_prior();fixture=json.loads((HERE/'data.json').read_text())
    data=parse_pairs(fixture['readings'],8900);dh=digest_pairs(data)
    if dh!=fixture['data_sha256']:raise ValueError('data hash')
    clock=Q(approximation['clock_and_derivative']['complete_clock_distortion_radius'])
    rows=[];observed=[];planning=[];bindings={}
    for design in ('multi','outer'):
        for degree in (6,8,10,12):
            path=HERE/('result_'+design+'_'+str(degree)+'.json');result=json.loads(path.read_text());cert=result['certificate']
            if cert['design']!=design or cert['degree']!=degree:raise ValueError('certificate domain')
            if cert['data_sha256']!=dh or cert['proposal_sha256']!=digest_pairs(parse_pairs(result['proposal'],50+degree)):raise ValueError('data/proposal binding')
            rho=Q(cert['normal_residual_upper'])
            if not 0<=rho<Q(1,10**30):raise ValueError('verified planning residual ceiling')
            old=next(r for r in prior['designs'][design]['degrees'] if r['degree']==degree)
            approx=next(r for r in approximation['records'] if (r['design'],r['degree'])==(design,degree))
            actual=profile(old,approx,rho,3,4000,clock)
            if actual!=result['uncertainty_budget']:raise ValueError('changed exact budget consequence')
            if Q(cert['nonpolynomial_drift_radius'])!=Q(actual['family_radius'])+clock+Q(1,10**6):raise ValueError('joint physical charge')
            if actual['all_49_strict_rounding_gates']!=(cert['status']=='certified_under_declared_model'):raise ValueError('gate status mismatch')
            if degree==12 and cert['answer_a1_through_a50']!=fixture['truth_a1_through_a50']:raise ValueError('actual recovered integers')
            observed.append(actual)
            for omega in (Q(1,2),Q(1),Q(2),Q(3)):
                rows.append(profile(old,approx,Q(1,10**30),omega,4000,clock))
            # This separate planning table assumes a freshly verified future
            # residual <=1e-30. Its smaller families need not contain this
            # actual Omega=3, B=4000 fixture.
            for amplitude in (Q(0),Q(1,10),Q(1),Q(100),Q(4000)):
                planning.append(profile(old,approx,Q(1,10**30),1,amplitude,clock))
            bindings[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
    winners=[]
    for design in ('multi','outer'):
        for omega in ('1/2','1','2','3'):
            candidates=[r for r in rows if r['design']==design and r['frequency_upper']==omega]
            winner=max(candidates,key=lambda r:Q(r['strict_sufficient_amplitude_limit']))
            winners.append({'design':design,'frequency_upper':omega,'best_tested_degree':winner['degree'],
                            'strict_sufficient_amplitude_limit':winner['strict_sufficient_amplitude_limit']})
    planning_choices=[]
    for design in ('multi','outer'):
        for amplitude in ('0','1/10','1','100','4000'):
            candidates=[r for r in planning if r['design']==design and r['amplitude_upper']==amplitude]
            winner=min(candidates,key=lambda r:Q(r['complete_coefficient_error_maximum']))
            planning_choices.append({'design':design,'frequency_upper':'1','amplitude_upper':amplitude,
                                     'minimum_error_tested_degree':winner['degree'],
                                     'complete_coefficient_error_maximum':winner['complete_coefficient_error_maximum']})
    return {'schema':'uncertain-clock-complete-budget-v1','verified':True,
            'data_sha256':dh,'result_bindings':bindings,
            'interpretation':'Strict sufficient capacities conditional on family membership and a freshly verified normal residual <=1e-30. All capacity rows use this common residual ceiling; actual fixture rows retain their measured residuals. Only Omega=3 and B=4000 are the actual fixture. Other frequencies describe design bounds, not replayed physical families.',
            'actual_fixture_budgets':observed,'frequency_degree_capacities':rows,'best_tested_capacity_degrees':winners,
            'planning_residual_ceiling':'1/1000000000000000000000000000000',
            'planning_interpretation':'Future data must independently verify the residual ceiling and declared family. Minimum error among four tested degrees, without claiming globally optimal approximation.',
            'planning_error_budgets':planning,'planning_minimum_error_degrees':planning_choices}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();doc=build()
    if a.write:(HERE/'consequences.json').write_text(json.dumps(doc,indent=2)+'\n')
    print('verified',len(doc['frequency_degree_capacities']),'frequency/degree capacities;',len(doc['planning_error_budgets']),'planning budgets')
    for r in doc['best_tested_capacity_degrees']:print(r['design'],r['frequency_upper'],'best degree',r['best_tested_degree'],'B <',float(Q(r['strict_sufficient_amplitude_limit'])))
    for r in doc['planning_minimum_error_degrees']:print('planning',r['design'],'B',r['amplitude_upper'],'degree',r['minimum_error_tested_degree'],'Emax',float(Q(r['complete_coefficient_error_maximum'])))
