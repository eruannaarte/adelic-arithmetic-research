"""Exact polynomial time bound and strict uncertainty budgets; no float arithmetic."""
from fractions import Fraction as Q
from math import isqrt
from pathlib import Path
import argparse, hashlib, json
import check

HERE=Path(__file__).resolve().parent
L=Q(37,1000)
ETA=Q(11,10**8)
H=Q(1,2_000_000)
EPSILON_H=Q(1,10**9)
RHO=XI=Q(1,10**9)


def sqrt_lower(x,digits=30):
    if x<0:raise ValueError('negative radicand')
    scale=10**digits
    return Q(isqrt(x.numerator*scale**2//x.denominator),scale)


def derivative_bound():
    path=check.PRIOR/'kernel.json'
    coeff=check.interval_coefficients(json.loads(path.read_text()))
    rows=check.CONFIGS['7']['bank'];bounds=[]
    for j in check.TARGETS:
        square=Q()
        for sensor in rows:
            for port in (0,1):
                c=coeff[abs(sensor-j)][port]
                value=sum((abs(a)*Q(1,2)**k for k,a in enumerate(c)),Q())
                derivative=sum((k*abs(a)*Q(1,2)**(k-1) for k,a in enumerate(c) if k),Q())
                # alpha <= 4/3 and alpha' <= 1/6 throughout [1,2].
                square+=(value/6+Q(4,3)*derivative)**2
        bounds.append(square)
    assert Q(4,3)**4>3 and Q(3,2)**4<8
    assert max(bounds)<L*L
    return {'norm':'Euclidean operator norm, bounded by Frobenius norm',
            'time_interval':['1','2'],'all_targets':list(check.TARGETS),
            'kernel_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'bank_offsets':list(rows),'polynomial_forward_lipschitz_upper':str(L),
            'maximum_derivative_frobenius_squared_upper':str(max(bounds)),
            'per_target_squared_bounds':list(map(str,bounds))}


def profile(eta,h,epsilon_h,xi):
    values=(eta,h,epsilon_h,xi)
    if any(type(v) not in (int,str,Q) for v in values):
        raise ValueError('exact rational budgets required')
    eta,h,epsilon_h,xi=map(Q,values)
    if min(eta,h,epsilon_h,xi)<0:raise ValueError('negative budget')
    config=check.CONFIGS['7'];mu=check.A0**2*config['source'];lam=check.A0**2*config['pair']
    timing=L*h;model=Q(8,3)*epsilon_h
    delta=eta+RHO+xi+timing+model
    if not delta*delta<mu*Q(1,1000)**2:raise ValueError('source accuracy gate fails')
    if not 2*delta*delta<lam:raise ValueError('label separation gate fails')
    return {'sensor_relative_radius':str(eta),'maximum_absolute_clock_error':str(h),
            'generator_perturbation_operator_norm_upper':str(epsilon_h),
            'forward_time_lipschitz_upper':str(L),
            'timing_relative_radius':str(timing),'model_mismatch_relative_radius':str(model),
            'operator_approximation_relative_radius':str(RHO),
            'normalization_relative_radius':str(xi),'total_relative_radius':str(delta),
            'approximate_source_floor':str(mu),'approximate_pair_floor':str(lam),
            'source_relative_error_squared_upper':str(delta*delta/mu),
            'source_relative_error_target':'1/1000','label_separation_verified':True,
            'source_accuracy_verified':True}


def build():
    d=derivative_bound()
    return {'schema':'spatial-clock-model-budget-v1','derivative':d,
            'physical_model_approximation_verified':str(check.model_error_check(7)),
            'uncertain_time_domain':'Both nominal and true times lie in [1,2]',
            'model_family':'H and Htrue are self-adjoint positive semidefinite; ||Htrue-H||_2 <= epsilon_H; source, sensing rows and alpha(t) unchanged',
            'profiles':{'uncertain_clock':profile(ETA,H,EPSILON_H,XI),
                        'known_clock':profile(Q(14,10**8),Q(0),Q(0),XI)},
            'sufficient_tradeoff':'eta + rho + xi + L h + (8/3) epsilon_H < min(0.001 sqrt(mu), sqrt(lambda/2))',
            'derivative_note':'One inherited model approximation radius is charged at the true time, then the polynomial map is transported to nominal time.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    result=build()
    if args.write:(HERE/'timing.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='derivative'},indent=2))
