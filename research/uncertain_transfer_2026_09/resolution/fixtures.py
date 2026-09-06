"""Outward synthetic raw readings for true time and a perturbed finite generator.

For Htrue=H+lambda I, the exact finite response is exp(-lambda t) times
its old finite response. Polynomial kernel approximation and rounding are
charged to the raw sensor budget, independently of decoder approximation.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import isqrt
import argparse, hashlib, json
from flint import arb,ctx,fmpq
import check, timing

HERE=Path(__file__).resolve().parent


def ball(q):
    q=Q(q);return arb(fmpq(q.numerator,q.denominator))


def dyadic(a):
    if not a.is_exact() or not a.is_finite():raise ValueError('exact finite endpoint required')
    m,e=map(int,a.man_exp());return Q(m*2**e) if e>=0 else Q(m,2**(-e))


def rounded(a,digits=50):
    q=dyadic(a.mid());scale=10**digits
    return Q((2*q.numerator*scale+q.denominator)//(2*q.denominator),scale)


def sqrt_upper(q,digits=50):
    s=10**digits;k=isqrt(q.numerator*s*s//q.denominator)
    return Q(k if Q(k,s)**2==q else k+1,s)


def evaluate(poly,t):
    v=Q()
    for c in reversed(poly):v=v*(t-Q(3,2))+c
    return v


def build(bits=256):
    coeff=check.interval_coefficients(json.loads((check.PRIOR/'kernel.json').read_text()))
    rows=check.CONFIGS['7']['bank'];cases=[]
    time_pairs=[(Q(1),Q(1)+timing.H),(Q(3,2),Q(3,2)-timing.H),
                (Q(3,2),Q(3,2)+timing.H),(Q(2),Q(2)-timing.H)]
    sources=[(490,(Q(3,5),Q(4,5)),Q(1,10**8)),
             (500,(Q(-4,5),Q(3,5)),Q(1)),(510,(Q(0),Q(1)),Q(10**8))]
    with ctx.workprec(bits):
        for t0,t1 in time_pairs:
            for label,direction,scale in sources:
                u=tuple(scale*v for v in direction);lam=timing.EPSILON_H
                assert sum(v*v for v in u)==scale*scale
                alpha=(1+ball(t1)).sqrt().sqrt();decay=(-ball(lam*t1)).exp()
                raw=[];round_errors=[];clock_difference=[]
                for sensor in rows:
                    p=sum((evaluate(coeff[abs(sensor-(label-500))][port],t1)*u[port] for port in (0,1)),Q())
                    exact_approx=decay*alpha*ball(p)
                    z=rounded(exact_approx)
                    raw.append(z);round_errors.append(dyadic(abs(exact_approx-ball(z)).upper()))
                    p0=sum((evaluate(coeff[abs(sensor-(label-500))][port],t0)*u[port] for port in (0,1)),Q())
                    clock_difference.append(exact_approx-(1+ball(t0)).sqrt().sqrt()*ball(p0))
                quantization=sqrt_upper(sum(q*q for q in round_errors))/scale
                raw[0]+=timing.ETA*scale/4
                charge=timing.RHO+quantization+timing.ETA/4
                assert charge<timing.ETA
                diff=sum((z*z for z in clock_difference),arb(0)).sqrt()/ball(scale)
                cases.append({'nominal_time':str(t0),'true_time':str(t1),
                              'maximum_absolute_clock_error':str(timing.H),
                              'generator_decay_lambda':str(lam),'generator_perturbation_bound':str(timing.EPSILON_H),
                              'source_label':label,'source':list(map(str,u)),
                              'source_norm':str(scale),'raw_data':list(map(str,raw)),
                              'sensor_relative_radius':str(timing.ETA),
                              'generation_quantization_relative_error_upper':str(quantization),
                              'added_sensor_relative_norm':str(timing.ETA/4),
                              'actual_raw_sensor_relative_error_upper':str(charge),
                              'perturbed_versus_nominal_polynomial_output_relative_norm':str(dyadic(diff.upper()))})
    return {'schema':'spatial-uncertain-time-raw-fixtures-v1',
            'physical_model':'The declared finite generator Htrue=H+lambda I; all true times in [1,2].',
            'status':'synthetic exact-rational observations with outward sensor-promise proof, not empirical measurements',
            'kernel_sha256':hashlib.sha256((check.PRIOR/'kernel.json').read_bytes()).hexdigest(),
            'bank_offsets':list(rows),'case_count':len(cases),'working_precision_bits':bits,
            'generation_proof':'Raw discrepancy from the full perturbed finite model is <= exp(-lambda*t)rho||u|| plus outward generation rounding plus the explicit sensor vector; exp(-lambda*t)<=1.',
            'cases':cases}


def verify(document,bits=320):
    expected=build(bits)
    for key in ('schema','physical_model','status','kernel_sha256','bank_offsets','case_count','generation_proof'):
        if document[key]!=expected[key]:raise ValueError('fixture contract disagrees: '+key)
    # The fixed decimal data must reproduce; outward error radii may tighten.
    for a,b in zip(document['cases'],expected['cases']):
        for key in ('nominal_time','true_time','maximum_absolute_clock_error',
                    'generator_decay_lambda','generator_perturbation_bound',
                    'source_label','source','source_norm','raw_data',
                    'sensor_relative_radius','added_sensor_relative_norm'):
            if a[key]!=b[key]:raise ValueError('raw reconstruction disagrees: '+key)
        quantization=Q(a['generation_quantization_relative_error_upper'])
        if quantization<0 or Q(b['generation_quantization_relative_error_upper'])>quantization:
            raise ValueError('generation rounding promise not proved')
        if not Q(a['actual_raw_sensor_relative_error_upper'])==timing.RHO+quantization+timing.ETA/4<timing.ETA:
            raise ValueError('stored sensor charge is inconsistent or excessive')
        if Q(b['actual_raw_sensor_relative_error_upper'])>Q(a['actual_raw_sensor_relative_error_upper']):
            raise ValueError('replay does not imply stored sensor promise')
    if len(document['cases'])!=len(expected['cases']):raise ValueError('case count')
    return {'verified':True,'case_count':len(expected['cases']),'reconstruction_precision_bits':bits,
            'raw_readings_reconstructed':True,'all_sensor_promises_reproved':True}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--replay',action='store_true');a=p.parse_args()
    if a.replay:
        result=verify(json.loads((HERE/'fixtures.json').read_text()))
        if a.write:(HERE/'fixtures_replay.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        result=build()
        if a.write:(HERE/'fixtures.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
