"""Exact raw-data demonstrations satisfying the full finite-model promise.

The fixture uses the certified approximate maps and explicitly charges their
full possible difference from the physical map to the raw sensor budget. This
is a synthetic existence construction, not measured laboratory data.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse,json,time
from normalize import PhysicalBank,make_scale,verify_packet,GAIN

HERE=Path(__file__).resolve().parent
RHO=Q(1,10**9)


def ceiling(x,digits=30):
    scale=10**digits
    return Q(-(-x.numerator*scale//x.denominator),scale)


def fixture(bank,tau,label,u,metric):
    p=bank.decoder.matrices(tau)[label]
    eta=Q(bank.decoder.profiles[metric]['sensor_relative_radius'])
    exact_alpha=make_scale(tau,0,'1/1000000000000000000000000')
    r=Q(exact_alpha['inverse_normalization']);e=Q(exact_alpha['relative_multiplier_error_upper'])
    # ||P_j|| <= (4/3+rho)/(19/16) < 2 from the true contraction.
    if not GAIN+RHO<2*Q(19,16):raise ValueError('polynomial map upper bound')
    pure=[sum((a*b for a,b in zip(row,u)),Q())/r for row in p]
    norm_square=sum((v*v for v in u),Q())
    # Fixtures use a rational scale times a unit rational direction.
    from math import isqrt
    scale=Q(isqrt(norm_square.numerator),isqrt(norm_square.denominator))
    if scale**2!=norm_square:raise ValueError('fixture needs rational source norm')
    y=pure[:];y[0]+=eta*scale/4
    sensor_charge=RHO+2*e/r+eta/4
    if not sensor_charge<eta:raise ValueError('synthetic raw data do not meet sensor promise')
    return y,{'actual_raw_sensor_relative_error_upper':str(sensor_charge),
              'generation_inverse_normalization':str(r),
              'generation_multiplier_error_upper':str(e),
              'proof':'physical map discrepancy rho, generation normalization at most 2e/r, added sensor norm eta/4; S>=I'}


def run(write=False):
    started=time.monotonic();cases=[]
    for size in ('7','8','9'):
        bank=PhysicalBank(size)
        for metric,profile in bank.decoder.profiles.items():
            for tau in (Q(1),Q(3,2),Q(2)):
                for label,direction,scale in ((490,(Q(3,5),Q(4,5)),Q(1,10**40)),
                                             (500,(Q(-4,5),Q(3,5)),Q(1)),
                                             (510,(Q(0),Q(1)),Q(10**40))):
                    u=tuple(scale*v for v in direction)
                    y,promise=fixture(bank,tau,label,u,metric)
                    result=bank.decode(y,tau,metric)
                    assert (result['status'],result['feasible_targets'])==('unique',[label])
                    charge=verify_packet(y,result['normalization'])
                    assert charge<=Q(1,10**9)
                    estimate=tuple(map(Q,result['source_estimate']))
                    factor=1 if metric.startswith('L2') else 41
                    error_square=factor*sum(((a-b)**2 for a,b in zip(estimate,u)),Q())/scale**2
                    assert error_square<Q(profile['source_relative_accuracy_target'])**2
                    cases.append({'bank':size,'profile':metric,'time':str(tau),'source_label':label,
                                  'source':list(map(str,u)),'source_norm_scale':str(scale),
                                  'raw_readings':list(map(str,y)),'raw_sensor_promise':promise,
                                  'normalization':result['normalization'],
                                  'unique_recovered_label':result['feasible_targets'][0],
                                  'source_relative_error_squared_upper':str(ceiling(error_square)),
                                  'source_relative_accuracy':profile['source_relative_accuracy_target']})
        print('raw bank',size,'completed; cases',len(cases),'elapsed',round(time.monotonic()-started,2),flush=True)
    output={'verified':True,'status':'exact synthetic raw-data promise and exact normalization/decoding checks',
            'case_count':len(cases),'bank_profiles':8,'source_amplitude_scales':['1/10^40','1','10^40'],
            'maximum_source_relative_error_squared_upper':str(max(Q(c['source_relative_error_squared_upper']) for c in cases)),
            'all_normalization_charges_at_most':'1/1000000000','cases':cases}
    if write:(HERE/'evidence.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k!='cases'},indent=2));return output


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');run(p.parse_args().write)
