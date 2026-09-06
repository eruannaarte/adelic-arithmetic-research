"""Physical degree-12 solve under the predeclared 120x shared clock rectangle."""
from fractions import Fraction as Q
from pathlib import Path
import argparse,hashlib,importlib.util,json,platform,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
APPROX=ROOT/'research/uncertain_transfer_2026_09/noise'
OLD=ROOT/'research/structured_transfer_2026_09/arithmetic'
sys.path.insert(0,str(ROOT/'research/operational_transfer_2026_09/noise'))
from physical import PhysicalModel,encode
from certify import verify

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
fixture=load('_orbit_fixture',APPROX/'demonstrate.py')
budget=load('_retained_strict_budget',OLD/'budget.py')

def run(write=False,bits=320):
    approximation=json.loads((APPROX/'approximation.json').read_text())
    new=json.loads((HERE/'orbit_bound.json').read_text());old=json.loads((OLD/'clock_bound.json').read_text())
    fixture.EPS_A=Q(120,10**14);fixture.EPS_B=Q(120,10**11)
    rows=[];dataset=None;dataset_seconds=0
    for design in ('multi','outer'):
        print('actual h=120 model',design,bits,flush=True)
        start=time.perf_counter();model=PhysicalModel(design,12,bits);build_seconds=time.perf_counter()-start
        cr=next(r for r in new['records'] if r['design']==design)
        previous=next(r for r in old['records'] if r['design']==design)
        ar=next(r for r in approximation['records'] if (r['design'],r['degree'])==(design,12))
        if dataset is None:
            start=time.perf_counter();dataset=fixture.fixture(model);dataset_seconds=time.perf_counter()-start
            if write:(HERE/'data_h120.json').write_text(json.dumps(dataset,indent=2)+'\n')
            elif dataset['readings']!=json.loads((HERE/'data_h120.json').read_text())['readings']:raise ValueError('higher precision reading replay failed')
        plan=budget.profile(model.record,ar,cr,120)
        if not plan['all_49_strict_rounding_gates']:raise ValueError('predeclared future contract failed')
        path=HERE/f'result_{design}_h120.json'
        start=time.perf_counter();proposal=model.propose(dataset['readings'],'arb') if write else json.loads(path.read_text())['proposal'];solve_seconds=time.perf_counter()-start
        nu=Q(plan['clock_radius'])+Q(plan['family_radius'])+Q(1,10**6)
        start=time.perf_counter();certificate=verify(model,dataset['readings'],proposal,Q(4,10**5),nu,True);check_seconds=time.perf_counter()-start
        rho=Q(certificate['normal_residual_upper'])
        if not write and rho>Q(json.loads(path.read_text())['certificate']['normal_residual_upper']):raise ValueError('higher-precision residual does not verify the saved upper bound')
        if rho>Q(1,10**30) or certificate['answer_a1_through_a50']!=dataset['truth_a1_through_a50'] or certificate['status']!='certified_under_declared_model':raise ValueError('physical certificate failed')
        actual=budget.profile(model.record,ar,cr,120,rho)
        pair=budget.profile(model.record,ar,previous,120,rho)
        direct=fixture.direct_check(model,ar,Q(plan['clock_radius']))
        result={'proposal':encode(proposal) if write else proposal,'certificate':certificate,
          'future_budget':plan,'uncertainty_budget':actual,'prior_pair_comparison':pair,
          'direct_fixture_diagnostics':direct,'cost':budget.operation_counts(12),
          'matrix_reconstruction_wall_seconds':build_seconds,'proposal_wall_seconds':solve_seconds,
          'dual_residual_verification_wall_seconds':check_seconds,'actual_data_reconstruction_wall_seconds':dataset_seconds}
        if design=='outer' and pair['all_49_strict_rounding_gates']:raise ValueError('prior pair adverse control unexpectedly passes')
        if write:path.write_text(json.dumps(result,indent=2)+'\n')
        rows.append({'design':design,'status':certificate['status'],
          'maximum_coefficient_error':actual['complete_coefficient_error_maximum'],
          'prior_pair_maximum_coefficient_error':pair['complete_coefficient_error_maximum'],
          'prior_pair_passes':pair['all_49_strict_rounding_gates'],'normal_residual_upper':str(rho),
          'actual_timing_distortion':direct['actual_weighted_signal_timing_distortion_upper'],
          'clock_radius':plan['clock_radius'],'result_file':path.name})
        print('certified',design,'Emax',float(Q(actual['complete_coefficient_error_maximum'])),'prior pair',float(Q(pair['complete_coefficient_error_maximum'])),flush=True)
    doc={'schema':'complete-orbit-clock-physical-demonstration-v1','verified':True,'bits':bits,
      'environment':{'python':platform.python_version(),'threads':'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1',
        'timings':'wall seconds for this run, not a machine-independent benchmark'},
      'clock_multiplier':120,'records':rows,'data_sha256':dataset['data_sha256'],
      'orbit_bound_sha256':hashlib.sha256((HERE/'orbit_bound.json').read_bytes()).hexdigest(),
      'saved_readings_and_proposals_replayed':not write}
    (HERE/('demonstration.json' if write else 'precision_replay.json')).write_text(json.dumps(doc,indent=2)+'\n')
    return doc

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bits',type=int,default=320);p.add_argument('--write',action='store_true');a=p.parse_args()
    print(json.dumps(run(a.write,a.bits),indent=2))
