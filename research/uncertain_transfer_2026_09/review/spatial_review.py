"""Independent spatial derivative, gate, model-error and raw-fixture audit.

No current spatial implementation is imported. Direct polynomial powers and
outward LDL point checks supplement, rather than replace, the exact whole-time
cell consumer. All derivative coefficient bounds and transfer gates are exact.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
from math import factorial
import hashlib,json
from flint import arb,ctx,fmpq
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def ball(x):
    x=Q(x);return arb(fmpq(x.numerator,x.denominator))


def endpoint(x):
    assert x.is_exact() and x.is_finite();m,e=map(int,x.man_exp())
    return Q(m*2**e) if e>=0 else Q(m,2**(-e))


def positive_pivots(a):
    a=[row[:] for row in a];pivots=[]
    for k in range(len(a)):
        pivot=a[k][k];assert pivot>0;pivots.append(endpoint(pivot.lower()))
        for i in range(k+1,len(a)):
            for j in range(i,len(a)):
                a[j][i]=a[i][j]=a[i][j]-a[i][k]*a[k][j]/pivot
    return pivots


def exp_upper(x):
    return sum((x**k/factorial(k) for k in range(201)),Q())+x**201/factorial(201)/(1-x/202)


def run():
    kp=ROOT/'research/transfer_theorem_2026_09/resolution/kernel.json'
    kernel=json.loads(kp.read_text());certpath=HERE.parent/'resolution/certificate_7.json'
    cert=json.loads(certpath.read_text());tp=HERE.parent/'resolution/timing.json'
    timing=json.loads(tp.read_text());fp=HERE.parent/'resolution/fixtures.json'
    fixtures=json.loads(fp.read_text());bank=cert['bank_offsets']
    assert bank==[-10,-8,-4,0,4,8,10]
    assert cert['target_offsets']==list(range(-10,11)) and cert['time_interval']==['1','2']
    assert cert['kernel_sha256']==hashlib.sha256(kp.read_bytes()).hexdigest()
    coeff=[[[sum(map(Q,b))/2 for b in row] for row in d] for d in kernel['coefficient_intervals']]
    assert len(coeff)==27 and all(len(d)==2 and all(len(r)==33 for r in d) for d in coeff)
    derivative=[]
    for label in range(-10,11):
        bound=Q()
        for sensor in bank:
            for port in (0,1):
                c=coeff[abs(sensor-label)][port]
                v=sum((abs(a)/2**k for k,a in enumerate(c)),Q())
                dv=sum((k*abs(c[k])/2**(k-1) for k in range(1,33)),Q())
                bound+=(v/6+Q(4,3)*dv)**2
        derivative.append(bound)
    d=timing['derivative'];L=Q(d['polynomial_forward_lipschitz_upper'])
    assert list(map(Q,d['per_target_squared_bounds']))==derivative
    assert Q(d['maximum_derivative_frobenius_squared_upper'])==max(derivative)<L*L
    assert L==Q(37,1000) and Q(4,3)**4>3 and Q(3,2)**4<8
    # Complete inherited model-error comparison, including all remote images
    # and all finite-boundary walks, rather than a saved error boolean.
    a=Q(8);image=exp_upper(Q(18,5)*(a+1/a-2))*(a**-38+a**-90)/(1-a**-64)
    walks=2*Q(56,5)**491/factorial(491)/(1-Q(56,5)/492)
    assert image<Q(1,10**24) and walks<Q(1,10**500)
    entry=Q(1,2**33)+Q(1,10**24)+Q(1,10**500)+Q(2,10**30)
    rho=Q(1,10**9);assert Q(4,3)**2*14*entry**2<rho**2
    a0=Q(19,16);sf=Q(cert['unnormalized_source_floor']);pf=Q(cert['unnormalized_pair_floor'])
    assert sf==Q(15,10**9) and pf==Q(5,10**14)
    mu=a0*a0*sf;lam=a0*a0*pf;profiles=[]
    for name,p in timing['profiles'].items():
        eta=Q(p['sensor_relative_radius']);h=Q(p['maximum_absolute_clock_error'])
        mismatch=Q(p['generator_perturbation_operator_norm_upper']);xi=Q(p['normalization_relative_radius'])
        assert min(eta,h,mismatch,xi)>=0
        delta=eta+rho+L*h+Q(8,3)*mismatch+xi
        assert Q(p['timing_relative_radius'])==L*h and Q(p['model_mismatch_relative_radius'])==Q(8,3)*mismatch
        assert Q(p['total_relative_radius'])==delta
        assert Q(p['approximate_source_floor'])==mu and Q(p['approximate_pair_floor'])==lam
        assert Q(p['source_relative_error_squared_upper'])==delta*delta/mu
        assert 2*delta*delta<lam and delta*delta<mu*Q(1,1000)**2
        profiles.append({'profile':name,'verified_total_relative_radius':str(delta),
                         'fraction_of_source_error_squared_target':str(delta*delta/(mu*Q(1,1000)**2)),
                         'fraction_of_pair_floor':str(2*delta*delta/lam)})
    pointreports=[];rawreports=[]
    with ctx.workprec(384):
        cases=[(j,) for j in range(-10,11)]+list(combinations(range(-10,11),2))
        for t in (Q(1),Q(3,2),Q(2)):
            z=ball(t-Q(3,2));powers=[z**k for k in range(33)]
            def value(distance,port):
                return sum((ball(c)*power for c,power in zip(coeff[distance][port],powers)),arb(0))
            minpivot=None
            for labels in cases:
                n=2*len(labels)
                matrix=[[(-1)**side*value(abs(row-label),port) for side,label in enumerate(labels)
                         for port in (0,1)] for row in bank]
                floor=mu if n==2 else lam;alpha2=ball(1+t).sqrt()
                gram=[[alpha2*sum((row[i]*row[j] for row in matrix),arb(0))-int(i==j)*ball(floor)
                       for j in range(n)] for i in range(n)]
                pivots=positive_pivots(gram)
                minpivot=min(pivots) if minpivot is None else min(minpivot,min(pivots))
            pointreports.append({'nominal_time':str(t),'gram_floors_checked':len(cases),
                                 'minimum_positive_LDL_pivot':str(minpivot)})
        p=timing['profiles']['uncertain_clock'];assert fixtures['case_count']==12==len(fixtures['cases'])
        assert fixtures['bank_offsets']==bank
        for row in fixtures['cases']:
            t0=Q(row['nominal_time']);t1=Q(row['true_time']);decay=Q(row['generator_decay_lambda'])
            assert 1<=t0<=2 and 1<=t1<=2
            assert abs(t1-t0)<=Q(p['maximum_absolute_clock_error'])
            assert 0<=decay<=Q(p['generator_perturbation_operator_norm_upper'])
            label=row['source_label']-500;assert label in range(-10,11)
            u=list(map(Q,row['source']));s=Q(row['source_norm']);assert len(u)==2 and sum(a*a for a in u)==s*s and s>0
            raw=list(map(Q,row['raw_data']));assert len(raw)==len(bank)
            powers=[ball(t1-Q(3,2))**k for k in range(33)]
            scale=ball(1+t1).sqrt().sqrt()*(-ball(decay*t1)).exp()
            errors=[]
            for sensor,y in zip(bank,raw):
                output=scale*sum((ball(u[port])*sum((ball(c)*power for c,power in
                                  zip(coeff[abs(sensor-label)][port],powers)),arb(0)) for port in (0,1)),arb(0))
                errors.append(endpoint(abs(ball(y)-output).upper())/s)
            measured2=sum((e*e for e in errors),Q());eta=Q(p['sensor_relative_radius'])
            assert measured2<(eta-rho)**2
            rawreports.append({'nominal_time':str(t0),'actual_time':str(t1),'target':label+500,
                               'source_norm':str(s),'raw_polynomial_residual_relative_squared_upper':str(measured2),
                               'remaining_physical_sensor_radius_after_model_approximation':str(eta-rho)})
    return {'verified':True,'working_precision_bits':384,'kernel_sha256':hashlib.sha256(kp.read_bytes()).hexdigest(),
            'certificate_sha256':hashlib.sha256(certpath.read_bytes()).hexdigest(),
            'timing_sha256':hashlib.sha256(tp.read_bytes()).hexdigest(),
            'fixtures_sha256':hashlib.sha256(fp.read_bytes()).hexdigest(),
            'derivative_target_count':21,'uniform_polynomial_forward_lipschitz_verified':str(L),
            'complete_physical_operator_error_verified':str(rho),'profiles':profiles,
            'independent_point_floors':pointreports,'physical_raw_fixture_checks':rawreports,
            'scope':'693 point floors supplement the separate exact whole-time consumer; derivative and model-error bounds hold on the entire interval'}


if __name__=='__main__':print(json.dumps(run(),indent=2))
