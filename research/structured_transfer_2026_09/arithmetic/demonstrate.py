"""Reconstruct degree costs, then recover actual data under a 60x clock rectangle."""
from fractions import Fraction as Q
from pathlib import Path
import argparse, importlib.util, json, platform, sys, time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PRIOR=ROOT/'research/uncertain_transfer_2026_09/noise'
sys.path.insert(0,str(ROOT/'research/operational_transfer_2026_09/noise'))
from physical import PhysicalModel,encode
from certify import verify
spec=importlib.util.spec_from_file_location('_previous_fixture',PRIOR/'demonstrate.py')
fixture_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture_module)
# Loading the historical demonstration inserts its own directory into sys.path.
# Bind our budget explicitly so no old hard-coded clock profile is selected.
spec=importlib.util.spec_from_file_location('_new_complete_budget',HERE/'budget.py')
budget=importlib.util.module_from_spec(spec);spec.loader.exec_module(budget)

def run(write=False,bits=320,benchmark=False):
    approximation=json.loads((PRIOR/'approximation.json').read_text())
    clock=json.loads((HERE/'clock_bound.json').read_text())
    old_data=json.loads((PRIOR/'data.json').read_text())
    baseline=[];enlarged=[];dataset=None
    if benchmark:
        for design in ('multi','outer'):
            cr=next(r for r in clock['records'] if r['design']==design)
            for p in (6,8,10,12):
                print('cost and fixed-contract verification',design,p,bits,flush=True)
                start=time.perf_counter();model=PhysicalModel(design,p,bits);build=time.perf_counter()-start
                ar=next(r for r in approximation['records'] if (r['design'],r['degree'])==(design,p))
                saved=json.loads((PRIOR/f'result_{design}_{p}.json').read_text())
                planning=budget.profile(model.record,ar,cr)
                nu=Q(planning['clock_radius'])+Q(planning['family_radius'])+Q(1,10**6)
                start=time.perf_counter();certificate=verify(model,old_data['readings'],saved['proposal'],Q(4,10**5),nu,True);verification=time.perf_counter()-start
                rho=Q(certificate['normal_residual_upper'])
                if rho>Q(1,10**30):raise ValueError('fixed residual ceiling not met')
                actual=budget.profile(model.record,ar,cr,rho=rho)
                if actual['all_49_strict_rounding_gates']!=(certificate['status']=='certified_under_declared_model'):raise ValueError('degree comparison disagrees with decoder')
                if p==12 and certificate['answer_a1_through_a50']!=old_data['truth_a1_through_a50']:raise ValueError('baseline truth mismatch')
                baseline.append({'design':design,'degree':p,'future_budget':planning,'actual_budget':actual,
                                 'matrix_reconstruction_wall_seconds':build,'dual_residual_verification_wall_seconds':verification,
                                 'cost':budget.operation_counts(p),'historical_data_sha256':old_data['data_sha256']})
    fixture_module.EPS_A=Q(60,10**14);fixture_module.EPS_B=Q(60,10**11)
    for design in ('multi','outer'):
        print('enlarged clock, actual model',design,12,bits,flush=True)
        start=time.perf_counter();model=PhysicalModel(design,12,bits);build=time.perf_counter()-start
        cr=next(r for r in clock['records'] if r['design']==design)
        ar=next(r for r in approximation['records'] if (r['design'],r['degree'])==(design,12))
        if dataset is None:
            start=time.perf_counter();dataset=fixture_module.fixture(model);data_seconds=time.perf_counter()-start
            if write:(HERE/'data_sixtyfold.json').write_text(json.dumps(dataset,indent=2)+'\n')
            else:
                frozen=json.loads((HERE/'data_sixtyfold.json').read_text())
                if dataset['readings']!=frozen['readings']:raise ValueError('actual enlarged-clock reading replay differs')
        plan=budget.profile(model.record,ar,cr,60)
        if not plan['all_49_strict_rounding_gates']:raise ValueError('enlarged clock fails fixed recovery contract')
        path=HERE/f'result_{design}_sixtyfold.json'
        start=time.perf_counter()
        proposal=model.propose(dataset['readings'],'arb') if write else json.loads(path.read_text())['proposal']
        proposal_seconds=time.perf_counter()-start
        nu=Q(plan['clock_radius'])+Q(plan['family_radius'])+Q(1,10**6)
        start=time.perf_counter();certificate=verify(model,dataset['readings'],proposal,Q(4,10**5),nu,True);verification=time.perf_counter()-start
        rho=Q(certificate['normal_residual_upper'])
        if rho>Q(1,10**30) or certificate['answer_a1_through_a50']!=dataset['truth_a1_through_a50'] or certificate['status']!='certified_under_declared_model':raise ValueError('enlarged clock actual certificate failed')
        actual=budget.profile(model.record,ar,cr,60,rho)
        previous=budget.profile(model.record,ar,cr,60,rho,old_clock=True)
        direct=fixture_module.direct_check(model,ar,Q(plan['clock_radius']))
        result={'proposal':encode(proposal) if write else proposal,'certificate':certificate,
                'uncertainty_budget':actual,'prior_pointwise_comparison':previous,
                'direct_fixture_diagnostics':direct,'cost':budget.operation_counts(12),
                'matrix_reconstruction_wall_seconds':build,'proposal_wall_seconds':proposal_seconds,
                'dual_residual_verification_wall_seconds':verification,'actual_data_reconstruction_wall_seconds':data_seconds}
        if design=='outer' and previous['all_49_strict_rounding_gates']:raise ValueError('expected strict improvement control did not fail')
        if write:path.write_text(json.dumps(result,indent=2)+'\n')
        enlarged.append({'design':design,'status':certificate['status'],'max_coefficient_error':actual['complete_coefficient_error_maximum'],
                         'old_bound_max_coefficient_error':previous['complete_coefficient_error_maximum'],
                         'normal_residual_upper':str(rho),'actual_timing_distortion':direct['actual_weighted_signal_timing_distortion_upper'],
                         'clock_radius':plan['clock_radius'],'result_file':path.name})
        print('certified',design,'new Emax',float(Q(actual['complete_coefficient_error_maximum'])),'old Emax',float(Q(previous['complete_coefficient_error_maximum'])),flush=True)
    result={'schema':'structured-clock-arithmetic-demonstration-v1','verified':True,'bits':bits,
            'environment':{'python':platform.python_version(),'platform':platform.platform(),'processor':platform.processor(),
                           'threads':'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1','timings':'wall seconds, one run per matrix; not a performance benchmark across machines'},
            'baseline_fixed_contract_comparisons':baseline,'enlarged_clock_multiplier':60,
            'enlarged_clock_results':enlarged,'data_sha256':dataset['data_sha256'],
            'saved_readings_and_proposals_replayed':not write}
    path=HERE/('demonstration.json' if write else 'precision_replay.json')
    path.write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bits',type=int,default=320);p.add_argument('--write',action='store_true');p.add_argument('--benchmark',action='store_true')
    a=p.parse_args();print(json.dumps(run(a.write,a.bits,a.benchmark),indent=2))
