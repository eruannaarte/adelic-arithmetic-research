"""Actual complete-tail integer recovery with a much larger smooth drift.

Synthetic truth is used only to validate the returned answers. The solver sees
only exact readings and declared bounds. Family membership remains an external
model assumption for real data.
"""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import argparse, json, sys
from flint import acb, arb, ctx

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'research/operational_transfer_2026_09/noise'))
from physical import (PhysicalModel, M, ball, upper, quantize, complex_ball,
                      encode, digest_pairs, parse_pairs, evaluate)
from certify import solve, verify, divisor14, consequences
from check_approximation import check_document, drift_radius

ETA=Q(4,100000)
AMPLITUDE=Q(20000)
FREQUENCY=Q(1)
PHASE=Q(1,3)
POLYNOMIAL_AMPLITUDE=Q(10**20)


def fixture(model):
    truth=[1]+[n%7 for n in range(2,51)]
    source=[(n,a) for n,a in enumerate(truth,1)]+[(n,divisor14(n)//2) for n in (51,60,72)]
    if not all(0<=a<=divisor14(n) for n,a in source):raise ValueError('integer source envelope')
    with ctx.workprec(model.bits):
        logs={n:arb(n).log() for n,a in source}
        beta=[complex_ball((POLYNOMIAL_AMPLITUDE/(k+1),POLYNOMIAL_AMPLITUDE/(k+2))) for k in range(9)]
        data=[];quantization=Q(0)
        for t,x in zip(model.times,model.x):
            signal=sum((ball(Q(a,n*n))*acb(0,-t*logs[n]).exp() for n,a in source),acb(0))
            polynomial=acb(0)
            for c in reversed(beta):polynomial=polynomial*x+c
            family=ball(AMPLITUDE)*(ball(FREQUENCY)*x+ball(PHASE)).sin()
            sensor=ball(Q(39,10**6))*acb(0,t/11).exp()
            value=signal+polynomial+family+sensor
            pair=(quantize(value.real,40),quantize(value.imag,40))
            quantization=max(quantization,upper(abs(complex_ball(pair)-value)))
            data.append(pair)
    if not quantization<Q(1,10**35):raise ValueError('unresolved fixture quantization')
    if not Q(39,10**6)+quantization<ETA:raise ValueError('sensor+quantization budget')
    return {'schema':'weighted-drift-physical-fixture-v1','readings':encode(data),
            'data_sha256':digest_pairs(data),'truth_a1_through_a50':truth,
            'finite_source_coefficients':[[n,a] for n,a in source],
            'degree':8,'polynomial_amplitude':str(POLYNOMIAL_AMPLITUDE),
            'polynomial_formula':'sum_(k=0)^8 ((10^20/(k+1))+i*(10^20/(k+2)))*x^k',
            'drift_amplitude':str(AMPLITUDE),'drift_frequency':str(FREQUENCY),'drift_phase':str(PHASE),
            'drift_formula':'20000*sin(x+1/3), x=t/890',
            'sensor_formula':'(39/1000000)*exp(i*t/11)',
            'sensor_radius':str(ETA),'quantization_pointwise_upper':str(quantization),
            'meaning':'Synthetic finite-support integer envelope source; no number-field realizability or measured sensor distribution claimed.'}


def direct_family_check(model,record):
    """Outward check for this fixture, supplementary to the uniform theorem."""
    with ctx.workprec(model.bits):
        s=ball(PHASE).sin();c=ball(PHASE).cos();p=[arb(0)]*9
        def coefficient(k):
            if k%2:return c*((-1)**((k-1)//2))*ball(FREQUENCY**k/Q(factorial(k)))
            return s*((-1)**(k//2))*ball(FREQUENCY**k/Q(factorial(k)))
        for k in range(9):p[k]+=coefficient(k)
        for item in record['approximants']:
            ck=coefficient(item['order'])
            for j,a in enumerate(item['rational_polynomial']):p[j]+=ck*ball(Q(a))
        pp=[ball(AMPLITUDE)*v for v in p]
        residuals=[ball(AMPLITUDE)*(ball(FREQUENCY)*x+ball(PHASE)).sin()-evaluate(pp,x) for x in model.x]
        norm=upper(sum((w*r*r for w,r in zip(model.w,residuals)),arb(0)).sqrt())
    nu=drift_radius(record,AMPLITUDE)
    if norm>nu:raise ValueError('fixture contradicts uniform family certificate')
    return {'weighted_remainder_norm_upper':str(norm),'uniform_family_radius':str(nu),
            'degree_eight_polynomial_absorbed_by_augmented_solve':True}


def run(write=False,bits=256):
    doc=json.loads((HERE/'approximation.json').read_text())
    checked=check_document(doc,max(bits,256))
    model=PhysicalModel('multi',8,bits)
    data=fixture(model)
    if not write:
        saved=json.loads((HERE/'data.json').read_text())
        if data['readings']!=saved['readings']:raise ValueError('physical fixture reconstruction changed digital readings')
    results={}
    for record in doc['designs']:
        design=record['design']
        if design!='multi':model=PhysicalModel(design,8,bits)
        nu=drift_radius(record,AMPLITUDE)
        actual=direct_family_check(model,record)
        result=solve(model,data['readings'],ETA,nu,True)
        cert=result['certificate']
        if cert['status']!='certified_under_declared_model':raise ValueError('failed arithmetic certificate')
        if cert['answer_a1_through_a50']!=data['truth_a1_through_a50']:raise ValueError('wrong recovered fixture truth')
        # Same solver and readings: old pointwise budget is decisively too large.
        theta=parse_pairs(result['proposal'],58)
        old=consequences(model.record,theta,Q(cert['normal_residual_upper']),ETA,AMPLITUDE/Q(factorial(9)))
        if old['status']!='not_certified':raise ValueError('pointwise adverse control unexpectedly passed')
        # The polynomial fit cannot infer the physical family radius.
        oversized=consequences(model.record,theta,Q(cert['normal_residual_upper']),ETA,drift_radius(record,10**6))
        if oversized['status']!='not_certified':raise ValueError('oversized family premise unexpectedly passed')
        result['family_certificate']={'amplitude_bound':str(AMPLITUDE),'frequency_limit':'1','phase':'arbitrary real',
                                      'uniform_weighted_factor':record['uniform_phase_frequency_factor'],
                                      'computed_drift_radius':str(nu),'direct_fixture_check':actual}
        result['adverse_controls']={'same_data_old_pointwise_bound_status':old['status'],
                                    'same_solve_amplitude_bound_1000000_status':oversized['status']}
        result['all_49_unknown_integers_match_fixture']=True
        if write:(HERE/('result_'+design+'.json')).write_text(json.dumps(result,indent=2)+'\n')
        results[design]={'status':cert['status'],'initial_proposal':result['initial_proposal'],
                         'normal_residual_upper':cert['normal_residual_upper'],
                         'uniform_family_radius':str(nu),'direct_fixture_weighted_radius_upper':actual['weighted_remainder_norm_upper'],
                         'admissible_family_amplitude_limit_from_actual_residual':str(Q(cert['strict_sufficient_nonpolynomial_budget_limit'])/Q(record['uniform_phase_frequency_factor'])),
                         'all_49_unknown_integers_match_fixture':True,
                         'old_pointwise_bound_fails':True,'oversized_amplitude_promise_fails':True}
        print(design,'rho',float(Q(cert['normal_residual_upper'])),'nu',float(nu),
              'amplitude limit',float(Q(results[design]['admissible_family_amplitude_limit_from_actual_residual'])),flush=True)
    summary={'schema':'weighted-drift-demonstration-v1','verified':True,'working_precision_bits':bits,
             'measurement_count':M,'degree':8,'fixture_data_sha256':data['data_sha256'],
             'family_amplitude':'20000','frequency_limit':'1','phase_uniformity':True,
             'sensor_radius':str(ETA),'results':results}
    if write:
        (HERE/'data.json').write_text(json.dumps(data,indent=2)+'\n')
        (HERE/'demonstration.json').write_text(json.dumps(summary,indent=2)+'\n')
    else:
        # Replay validates the saved exact proposals afresh at the requested precision.
        for design in ('multi','outer'):
            model=PhysicalModel(design,8,bits)
            saved=json.loads((HERE/('result_'+design+'.json')).read_text())
            record=next(r for r in doc['designs'] if r['design']==design)
            result=verify(model,data['readings'],saved['proposal'],ETA,drift_radius(record,AMPLITUDE),True)
            if result['status']!='certified_under_declared_model' or result['answer_a1_through_a50']!=data['truth_a1_through_a50']:
                raise ValueError('saved exact proposal did not replay')
        summary['saved_exact_proposals_reverified']=True
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--bits',type=int,default=256)
    a=p.parse_args();summary=run(a.write,a.bits)
    print(json.dumps(summary,indent=2))
