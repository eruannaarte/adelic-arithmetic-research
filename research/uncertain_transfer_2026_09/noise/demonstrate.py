"""Actual clocked and mismatched data, all degrees, complete-tail residual checks."""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import argparse, json, sys
from flint import acb, arb, ctx

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'research/operational_transfer_2026_09/noise'))
from physical import PhysicalModel,M,ball,upper,quantize,complex_ball,encode,digest_pairs,parse_pairs,evaluate
from certify import solve,verify,divisor14
sys.path.insert(0,str(HERE))
from budget import profile, factor

ETA=Q(4,10**5);MISMATCH=Q(1,10**6)
EPS_A=Q(1,10**14);EPS_B=Q(1,10**11)
AMPLITUDE=Q(4000);OMEGA=Q(3);PHASE=Q(1,3)
POLY_AMPLITUDE=Q(10**20)


def fixture(model):
    truth=[1]+[n%7 for n in range(2,51)]
    source=[(n,a) for n,a in enumerate(truth,1)]+[(n,divisor14(n)//2) for n in (51,60,72)]
    if not all(0<=a<=divisor14(n) for n,a in source):raise ValueError('integer envelope')
    with ctx.workprec(model.bits):
        logs={n:arb(n).log() for n,a in source}
        beta=[complex_ball((POLY_AMPLITUDE/(k+1),POLY_AMPLITUDE/(k+2))) for k in range(7)]
        data=[];qbound=Q()
        for t in model.times:
            actual=(1+ball(EPS_A))*t+ball(EPS_B);x=actual/890
            signal=sum((ball(Q(a,n*n))*acb(0,-actual*logs[n]).exp() for n,a in source),acb(0))
            polynomial=acb(0)
            for c in reversed(beta):polynomial=polynomial*x+c
            family=ball(AMPLITUDE)*(ball(OMEGA)*x+ball(PHASE)).sin()
            mismatch=ball(Q(9,10**7))*(actual/17).cos()
            sensor=ball(Q(39,10**6))*acb(0,actual/11).exp()
            value=signal+polynomial+family+mismatch+sensor
            pair=(quantize(value.real,40),quantize(value.imag,40))
            qbound=max(qbound,upper(abs(complex_ball(pair)-value)))
            data.append(pair)
    if not qbound<Q(1,10**35) or not Q(39,10**6)+qbound<ETA:raise ValueError('sensor and digitization budget')
    return {'schema':'uncertain-clock-arithmetic-fixture-v1','readings':encode(data),
            'data_sha256':digest_pairs(data),'truth_a1_through_a50':truth,
            'finite_source_coefficients':[[n,a] for n,a in source],
            'true_clock_slope':str(1+EPS_A),'true_clock_offset':str(EPS_B),
            'polynomial_degree':6,'polynomial_formula':'sum k=0..6 (10^20/(k+1)+i*10^20/(k+2))*(t_actual/890)^k',
            'sinusoid_amplitude':str(AMPLITUDE),'sinusoid_frequency':str(OMEGA),'sinusoid_phase':str(PHASE),
            'mismatch_formula':'(9/10000000)*cos(t_actual/17)','mismatch_pointwise_radius':'9/10000000',
            'sensor_formula':'(39/1000000)*exp(i*t_actual/11)','sensor_radius':str(ETA),
            'digitization_pointwise_upper':str(qbound),
            'meaning':'Synthetic integer divisor-envelope source. Family and clock bounds are declared model assumptions, not apparatus calibration or number-field realization.'}


def direct_check(model,record,clock_radius):
    with ctx.workprec(model.bits):
        omega=OMEGA*(1+EPS_A);phase=PHASE+OMEGA*EPS_B/890
        s=ball(phase).sin();c=ball(phase).cos();degree=record['degree'];p=[arb(0)]*(degree+1)
        def ck(k):
            if k%2:return c*((-1)**((k-1)//2))*ball(omega**k/Q(factorial(k)))
            return s*((-1)**(k//2))*ball(omega**k/Q(factorial(k)))
        for k in range(degree+1):p[k]+=ck(k)
        for entry in record['approximants']:
            v=ck(entry['order'])
            for j,a in enumerate(entry['rational_polynomial']):p[j]+=v*ball(Q(a))
        pp=[ball(AMPLITUDE)*v for v in p]
        residuals=[ball(AMPLITUDE)*(ball(omega)*x+ball(phase)).sin()-evaluate(pp,x) for x in model.x]
        norm=upper(sum((w*r*r for w,r in zip(model.w,residuals)),arb(0)).sqrt())
        family=AMPLITUDE*factor(record,omega)
        if norm>family:raise ValueError('uniform family theorem failed direct check')
        # Source fixture is finite, but the timing certificate uses the complete
        # infinite divisor-envelope derivative, not this diagnostic norm.
        source=[(1,1)]+[(n,n%7) for n in range(2,51)]+[(n,divisor14(n)//2) for n in (51,60,72)]
        logs={n:arb(n).log() for n,a in source};dist=[]
        for t in model.times:
            actual=(1+ball(EPS_A))*t+ball(EPS_B)
            delta=sum((ball(Q(a,n*n))*(acb(0,-actual*logs[n]).exp()-acb(0,-t*logs[n]).exp()) for n,a in source),acb(0))
            dist.append(abs(delta))
        timing=upper(sum((w*r*r for w,r in zip(model.w,dist)),arb(0)).sqrt())
        if timing>clock_radius:raise ValueError('uniform timing theorem failed direct check')
    return {'actual_weighted_family_remainder_upper':str(norm),'uniform_family_radius':str(family),
            'actual_weighted_signal_timing_distortion_upper':str(timing),'uniform_complete_timing_radius':str(clock_radius)}


def run(write=False,bits=320):
    doc=json.loads((HERE/'approximation.json').read_text())
    clock=Q(doc['clock_and_derivative']['complete_clock_distortion_radius'])
    results=[];dataset=None
    for design in ('multi','outer'):
        for degree in (6,8,10,12):
            print('reconstruct',design,degree,'bits',bits,flush=True)
            model=PhysicalModel(design,degree,bits)
            if dataset is None:
                dataset=fixture(model)
                if write:(HERE/'data.json').write_text(json.dumps(dataset,indent=2)+'\n')
                else:
                    saved=json.loads((HERE/'data.json').read_text())
                    if dataset['readings']!=saved['readings']:raise ValueError('readings reconstruction mismatch')
            record=next(r for r in doc['records'] if (r['design'],r['degree'])==(design,degree))
            nu=AMPLITUDE*factor(record,OMEGA*(1+EPS_A))+clock+MISMATCH
            path=HERE/('result_'+design+'_'+str(degree)+'.json')
            if write:
                # Always use the high precision proposal so that adverse family
                # bounds do not cause repeated trial solves.
                proposal=model.propose(dataset['readings'],'arb')
                certificate=verify(model,dataset['readings'],proposal,ETA,nu,True)
                result={'proposal':encode(proposal),'certificate':certificate}
            else:
                saved=json.loads(path.read_text())
                certificate=verify(model,dataset['readings'],saved['proposal'],ETA,nu,True)
                result=saved
            rho=Q(certificate['normal_residual_upper'])
            budget=profile(model.record,record,rho,OMEGA,AMPLITUDE,clock)
            if budget['all_49_strict_rounding_gates']!=(certificate['status']=='certified_under_declared_model'):raise ValueError('independent gate disagreement')
            if degree==12:
                if certificate['answer_a1_through_a50']!=dataset['truth_a1_through_a50']:raise ValueError('promised positive fixture failed')
                direct=direct_check(model,record,clock)
                result['direct_fixture_diagnostics']=direct
            elif certificate['status']!='not_certified':raise ValueError('adverse degree control unexpectedly passed')
            result['uncertainty_budget']=budget
            result['answer_matches_fixture_if_certified']=certificate['answer_a1_through_a50']==dataset['truth_a1_through_a50'] if degree==12 else None
            if write:path.write_text(json.dumps(result,indent=2)+'\n')
            results.append({'design':design,'degree':degree,'status':certificate['status'],
                            'normal_residual_upper':str(rho),'max_coefficient_error':budget['complete_coefficient_error_maximum'],
                            'passing_gates':budget['passing_gates'],'result_file':path.name})
            print('verified',design,degree,certificate['status'],'rho',float(rho),'Emax',float(Q(budget['complete_coefficient_error_maximum'])),flush=True)
    summary={'schema':'uncertain-clock-arithmetic-demonstration-v1','verified':True,'bits':bits,
             'data_sha256':dataset['data_sha256'],'actual_nonzero_clock_and_mismatch':True,
             'results':results,'saved_exact_proposals_reverified':not write}
    path=HERE/('demonstration.json' if write else 'precision_replay.json')
    path.write_text(json.dumps(summary,indent=2)+'\n')
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bits',type=int,default=320);p.add_argument('--write',action='store_true')
    a=p.parse_args();print(json.dumps(run(a.write,a.bits),indent=2))
