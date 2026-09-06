"""Reproducible physical-model fixtures and verified augmented recovery.

No proposed integer answer is supplied to the solver. Fixture truth is used
only afterward for validation. These are synthetic envelope sources, not a
claim of realization by number fields or a measured noise distribution.
"""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import argparse, json
from flint import acb, arb, ctx
from physical import (PhysicalModel, M, ball, upper, quantize, complex_ball,
                      encode, digest_pairs, parse_pairs)
from certify import solve, verify, divisor14

HERE=Path(__file__).resolve().parent
ETA=Q(4,10**5);NU=Q(3,10**5)


def fixture(model,amplitude,slow=False):
    amplitude=Q(amplitude)
    truth=[1]+[n%7 for n in range(2,51)]
    source=[(n,a) for n,a in enumerate(truth,1)]+[(n,divisor14(n)//2) for n in (51,60,72)]
    assert all(0<=a<=divisor14(n) for n,a in source)
    with ctx.workprec(model.bits):
        logs={n:arb(n).log() for n,a in source}
        beta=[complex_ball((amplitude/(k+1),amplitude/(k+2))) for k in range(model.degree+1)]
        data=[];quantization=Q(0)
        for t,x in zip(model.times,model.x):
            signal=sum((ball(Q(a,n*n))*acb(0,-t*logs[n]).exp() for n,a in source),acb(0))
            polynomial=acb(0)
            for c in reversed(beta):polynomial=polynomial*x+c
            nonpolynomial=10*x.sin() if slow else ball(NU)*(t/7).sin()
            sensor=ball(Q(39,10**6))*acb(0,t/11).exp()
            value=signal+polynomial+nonpolynomial+sensor
            pair=(quantize(value.real,40),quantize(value.imag,40))
            quantization=max(quantization,upper(abs(complex_ball(pair)-value)))
            data.append(pair)
    assert quantization<Q(1,10**35)
    assert Q(39,10**6)+quantization<ETA
    return {'schema':'operational-arithmetic-fixture-v1','readings':encode(data),
            'data_sha256':digest_pairs(data),'truth_a1_through_a50':truth,
            'finite_source_coefficients':[[n,a] for n,a in source],
            'degree':model.degree,'polynomial_amplitude':str(amplitude),
            'polynomial_formula':'beta_k=(amplitude/(k+1))+i*(amplitude/(k+2)), k=0,...,degree, in x=t/890',
            'nonpolynomial_formula':'10*sin(t/890)' if slow else '(3/100000)*sin(t/7)',
            'absorbed_nonpolynomial_taylor_part':'10*(x-x^3/6+x^5/120-x^7/5040)' if slow else '0',
            'nonpolynomial_remainder_pointwise_upper':str(Q(10,factorial(9)) if slow else NU),
            'sensor_formula':'(39/1000000)*exp(i*t/11)',
            'quantization_norm_upper':str(quantization),
            'declared_sensor_radius':str(ETA),'declared_nonpolynomial_radius':str(NU),
            'fixture_promise_verified_by':'finite integer envelope; degree-eight Taylor remainder when slow; pointwise sine and phase modulus bounds; outward data quantization; sum W=1'}


def run(write=False):
    model=PhysicalModel('multi',8,256)
    assert Q(10,factorial(9))<NU
    fixtures={name:fixture(model,amp,slow) for name,amp,slow in [('moderate',10**6,False),('large',10**20,True)]}
    results={}
    for design in ('multi','outer'):
        if design!='multi':model=PhysicalModel(design,8,256)
        for name,data in fixtures.items():
            result=solve(model,data['readings'],ETA,NU,True)
            cert=result['certificate']
            assert cert['status']=='certified_under_declared_model'
            assert cert['answer_a1_through_a50']==data['truth_a1_through_a50']
            key=design+'_'+name;results[key]=result
            print(key,'initial',result['initial_proposal'],'final rho',float(Q(cert['normal_residual_upper'])),
                  'nu limit',float(Q(cert['strict_sufficient_nonpolynomial_budget_limit'])),flush=True)
            if write:(HERE/('result_'+key+'.json')).write_text(json.dumps(result,indent=2)+'\n')
    if write:
        for name,data in fixtures.items():(HERE/('data_'+name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    summary={'verified':True,'measurement_count':M,'degree':8,
             'fixture_data_sha256':{k:v['data_sha256'] for k,v in fixtures.items()},
             'results':{k:{'status':v['certificate']['status'],
                           'initial_proposal':v['initial_proposal'],
                           'normal_residual_upper':v['certificate']['normal_residual_upper'],
                           'strict_sufficient_nonpolynomial_budget_limit':v['certificate']['strict_sufficient_nonpolynomial_budget_limit'],
                           'all_49_unknown_integers_match_fixture':True} for k,v in results.items()}}
    if write:(HERE/'demonstration.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    print(json.dumps(run(args.write),indent=2))
