"""Outward construction/replay of noisy raw readings for the full finite model."""
from fractions import Fraction as Q
from pathlib import Path
from math import isqrt
import hashlib,json,argparse
from flint import arb,ctx,fmpq
import certify
from raw import PhysicalBank
HERE=Path(__file__).resolve().parent
ETA=Q(3,10**8);RHO=Q(1,10**9)

def ball(q):q=Q(q);return arb(fmpq(q.numerator,q.denominator))
def dyadic(a):
    if not a.is_exact() or not a.is_finite():raise ValueError('finite exact endpoint required')
    m,e=map(int,a.man_exp());return Q(m*2**e) if e>=0 else Q(m,2**(-e))
def rounded(a):
    q=dyadic(a.mid());scale=10**45;return Q((2*q.numerator*scale+q.denominator)//(2*q.denominator),scale)
def sqrt_upper(q):
    s=10**60;k=isqrt(q.numerator*s*s//q.denominator);return Q(k+int(Q(k,s)**2<q),s)
def value(poly,tau):
    z=Q()
    for c in reversed(poly):z=z*(tau-Q(3,2))+c
    return z

def build(bits=256):
    coeff=certify.interval_coefficients(json.loads((certify.PRIOR/'kernel.json').read_text()))
    rows=certify.CONFIGS['6']['bank'];cases=[]
    with ctx.workprec(bits):
        for t in (Q(1),Q(3,2),Q(2)):
            for label in (490,491,500,509,510):
                for direction in ((Q(1),Q(0)),(Q(0),Q(1)),(Q(3,5),Q(4,5)),(Q(-4,5),Q(3,5))):
                    scale=(Q(1,10**12),Q(1),Q(10**12))[len(cases)%3];source=tuple(scale*v for v in direction)
                    alpha=(1+ball(t)).sqrt().sqrt();data=[];errors=[]
                    for sensor in rows:
                        z=alpha*ball(sum((value(coeff[abs(sensor-(label-500))][port],t)*source[port] for port in (0,1)),Q()))
                        r=rounded(z);data.append(r);errors.append(dyadic(abs(z-ball(r)).upper()))
                    quantization=sqrt_upper(sum((e*e for e in errors),Q()))/scale
                    data[0]+=ETA*scale/4
                    charge=RHO+quantization+ETA/4
                    if not charge<ETA:raise ValueError('sensor promise failed')
                    cases.append({'time':str(t),'source_label':label,'source':list(map(str,source)),'source_norm':str(scale),
                                  'raw_data':list(map(str,data)),'generation_quantization_relative_upper':str(quantization),
                                  'added_sensor_relative_norm':str(ETA/4),'sensor_relative_error_upper':str(charge)})
    return {'schema':'six-row-raw-finite-model-fixtures-v1','kernel_sha256':hashlib.sha256((certify.PRIOR/'kernel.json').read_bytes()).hexdigest(),
            'bank_offsets':list(rows),'sensor_relative_radius':str(ETA),'case_count':len(cases),'precision_bits':bits,
            'status':'synthetic exact rational observations with a full finite-model sensor-promise proof; not empirical data','cases':cases}

def replay(document,bits=320):
    fresh=build(bits)
    for key in ('schema','kernel_sha256','bank_offsets','sensor_relative_radius','case_count','status'):
        if document[key]!=fresh[key]:raise ValueError('fixture metadata changed: '+key)
    if len(document['cases'])!=len(fresh['cases']):raise ValueError('case count')
    for a,b in zip(document['cases'],fresh['cases']):
        for key in ('time','source_label','source','source_norm','raw_data','added_sensor_relative_norm'):
            if a[key]!=b[key]:raise ValueError('fixture reading reconstruction failed')
        quantization=Q(a['generation_quantization_relative_upper'])
        if not 0<=Q(b['generation_quantization_relative_upper'])<=quantization:raise ValueError('quantization enclosure failed')
        if not Q(a['sensor_relative_error_upper'])==RHO+quantization+ETA/4<ETA:raise ValueError('sensor promise failed')
    return {'verified':True,'case_count':len(fresh['cases']),'replay_precision_bits':bits,'all_raw_digits_reproduced':True,'full_finite_model_sensor_promises_reproved':True}

def decode(document):
    bank=PhysicalBank();results=[];maximum=Q()
    for case in document['cases']:
        answer=bank.decode(case['raw_data'],case['time'])
        if answer['status']!='unique' or answer['feasible_targets']!=[case['source_label']]:raise ValueError('incorrect target')
        estimate=tuple(map(Q,answer['source_estimate']));truth=tuple(map(Q,case['source']));norm=Q(case['source_norm'])
        error=sum(((a-b)**2 for a,b in zip(estimate,truth)),Q())/(norm*norm)
        if not error<Q(1,10**6):raise ValueError('source accuracy failed')
        maximum=max(maximum,error)
        results.append({'time':case['time'],'source_label':case['source_label'],'source_relative_error_squared':str(error),'answer':answer})
    return {'verified':True,'case_count':len(results),'unique_correct_targets':len(results),'maximum_source_relative_error_squared':str(maximum),'results':results}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--replay',action='store_true');p.add_argument('--decode',action='store_true');a=p.parse_args()
    if a.replay:
        result=replay(json.loads((HERE/'fixtures.json').read_text()));name='fixtures_replay.json'
    elif a.decode:
        result=decode(json.loads((HERE/'fixtures.json').read_text()));name='decoded.json'
    else:result=build();name='fixtures.json'
    if a.write:(HERE/name).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('cases','results')},indent=2))
