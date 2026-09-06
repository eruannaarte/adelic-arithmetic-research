"""Degree-eleven raw data, actual inverse, and two residual identities."""
from fractions import Fraction as Q
from pathlib import Path
import argparse,importlib.util,json,platform,time
from flint import acb,arb,ctx
from physical import PhysicalModel,ball,upper,quantize,complex_ball,encode,digest_pairs
from budget import profile,operation_counts
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('_degree11_actual_verifier',ROOT/'research/operational_transfer_2026_09/noise/certify.py')
verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)

def fixture(model,amplitude):
    truth=[1]+[n%7 for n in range(2,51)]
    source=[(n,a) for n,a in enumerate(truth,1)]+[(n,verifier.divisor14(n)//2) for n in (51,60,72)]
    if not all(0<=a<=verifier.divisor14(n) for n,a in source):raise ValueError('integer source envelope')
    with ctx.workprec(model.bits):
        logs={n:arb(n).log() for n,a in source}
        beta=[complex_ball((Q(10**20,k+1),Q(10**20,k+2))) for k in range(12)]
        data=[];qbound=Q()
        for t in model.times:
            actual=(1+ball(Q(1,10**14)))*t+ball(Q(1,10**11));x=actual/890
            signal=sum((ball(Q(a,n*n))*acb(0,-actual*logs[n]).exp() for n,a in source),acb(0))
            polynomial=acb(0)
            for c in reversed(beta):polynomial=polynomial*x+c
            family=ball(amplitude)*(3*x+ball(Q(1,3))).sin()
            mismatch=ball(Q(9,10**7))*(actual/17).cos()
            sensor=ball(Q(39,10**6))*acb(0,actual/11).exp()
            value=signal+polynomial+family+mismatch+sensor
            pair=(quantize(value.real,40),quantize(value.imag,40))
            qbound=max(qbound,upper(abs(complex_ball(pair)-value)));data.append(pair)
    if qbound>=Q(1,10**35) or Q(39,10**6)+qbound>=Q(4,10**5):raise ValueError('sensor digitization exceeds allowance')
    return {'schema':'degree-eleven-raw-fixture-v1','readings':encode(data),'data_sha256':digest_pairs(data),
        'truth_a1_through_a50':truth,'finite_source_coefficients':source,
        'true_clock_slope':'100000000000001/100000000000000','true_clock_offset':'1/100000000000',
        'polynomial_degree':11,'polynomial_formula':'sum k=0..11 (10^20/(k+1)+i*10^20/(k+2))*(t_actual/890)^k',
        'sinusoid_amplitude':str(amplitude),'sinusoid_frequency':'3','sinusoid_phase':'1/3',
        'mismatch_formula':'(9/10000000)*cos(t_actual/17)','sensor_formula':'(39/1000000)*exp(i*t_actual/11)',
        'digitization_pointwise_upper':str(qbound),
        'meaning':'Synthetic divisor-envelope source. These data are a model illustration, not number-field realization or apparatus calibration.'}

def run(write=False,bits=320,record_replay=False):
    doc=json.loads((HERE/'evidence.json').read_text())
    clock=json.loads((ROOT/'research/structured_transfer_2026_09/arithmetic/clock_bound.json').read_text())
    datasets={};out=[]
    for name in ('multi','outer'):
        start=time.perf_counter();model=PhysicalModel(name,11,bits);built=time.perf_counter()-start
        app=next(a for a in doc['approximations'] if a['design']==name)
        cr=next(c for c in clock['records'] if c['design']==name)
        print('actual model built',name,bits,flush=True)
        for amp in (4000,500):
            if amp not in datasets:
                start=time.perf_counter();data=fixture(model,amp);data_seconds=time.perf_counter()-start
                path=HERE/f'data_B{amp}.json'
                if write:path.write_text(json.dumps(data,indent=2)+'\n')
                else:
                    old=json.loads(path.read_text())
                    if data['readings']!=old['readings'] or data['data_sha256']!=old['data_sha256']:raise ValueError('raw data did not replay exactly')
                datasets[amp]=data
            data=datasets[amp];path=HERE/f'result_{name}_B{amp}.json';plan=profile(model.record,app,cr,amplitude=amp)
            start=time.perf_counter()
            proposal=model.propose(data['readings'],'arb') if write else json.loads(path.read_text())['proposal']
            solve_seconds=time.perf_counter()-start
            nu=Q(plan['family_radius'])+Q(plan['clock_radius'])+Q(1,10**6)
            start=time.perf_counter();cert=verifier.verify(model,data['readings'],proposal,Q(4,10**5),nu,True);verify_seconds=time.perf_counter()-start
            rho=Q(cert['normal_residual_upper'])
            if not write and rho>Q(json.loads(path.read_text())['certificate']['normal_residual_upper']):raise ValueError('higher-precision residual does not verify saved upper bound')
            if rho>Q(1,10**30):raise ValueError('actual normal residual exceeds planned ceiling')
            actual=profile(model.record,app,cr,rho,amp)
            expected=amp==500
            if actual['all_49_strict_rounding_gates']!=expected or (cert['status']=='certified_under_declared_model')!=expected:raise ValueError('fixed and smaller-amplitude expected gate results differ')
            if expected and cert['answer_a1_through_a50']!=data['truth_a1_through_a50']:raise ValueError('accepted answer differs from fixture')
            result={'proposal':encode(proposal) if write else proposal,'certificate':cert,
                'uncertainty_budget':actual,'cost':operation_counts(),
                'matrix_reconstruction_seconds':built,'proposal_seconds':solve_seconds,
                'dual_residual_verification_seconds':verify_seconds,'fixture_reconstruction_seconds':data_seconds}
            if write:path.write_text(json.dumps(result,indent=2)+'\n')
            out.append({'design':name,'amplitude':amp,'status':cert['status'],'normal_residual_upper':str(rho),
                'complete_coefficient_error_maximum':actual['complete_coefficient_error_maximum'],
                'passing_gates':actual['passing_gates'],'actual_gram_defect_upper':str(model.actual_gram_defect_upper),
                'data_sha256':data['data_sha256'],'result_file':path.name,'dual_residual_seconds':verify_seconds})
            print(name,amp,cert['status'],'rho',float(rho),'E',float(Q(actual['complete_coefficient_error_maximum'])),flush=True)
    result={'schema':'degree-eleven-actual-demonstration-v1','bits':bits,'verified':True,
        'replays_saved_readings_and_proposals':not write,'polynomial_degree_actually_present':11,
        'results':out,'environment':{'python':platform.python_version(),'platform':platform.platform(),
            'threads':'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1','timings':'One-run wall seconds; not a benchmark across machines.'}}
    if write or record_replay:(HERE/('demonstration.json' if write else f'precision_replay_{bits}.json')).write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--bits',type=int,default=320);p.add_argument('--record-replay',action='store_true');a=p.parse_args()
    print(json.dumps(run(a.write,a.bits,a.record_replay),indent=2))
