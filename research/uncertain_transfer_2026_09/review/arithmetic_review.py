"""Independent clocked-data reconstruction and complete rational budget audit.

No current or previous arithmetic producer is imported. The complete-tail
bounds and outward normal residuals are explicit inherited/replayed premises;
this audit reconstructs all raw digits directly and independently propagates
those premises through every claimed actual and planning consequence.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import comb,factorial,isqrt
import hashlib,json
from flint import acb,arb,ctx,fmpq
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def ball(x):
    x=Q(x);return arb(fmpq(x.numerator,x.denominator))


def endpoint(x):
    assert x.is_exact() and x.is_finite();m,e=map(int,x.man_exp())
    return Q(m*2**e) if e>=0 else Q(m,2**(-e))


def digest_pairs(data):
    canonical=[[str(Q(a)),str(Q(b))] for a,b in data]
    return hashlib.sha256(json.dumps(canonical,separators=(',',':')).encode()).hexdigest()


def divisor(n):
    result=1;p=2
    while p*p<=n:
        exponent=0
        while n%p==0:n//=p;exponent+=1
        result*=comb(exponent+13,13);p+=1
    return result*14 if n>1 else result


def factor(record,o):
    p=record['degree'];r={v['order']:Q(v['weighted_residual_norm_upper']) for v in record['approximants']}
    tail={int(k):Q(v) for k,v in record['weighted_monomial_norm_upper'].items()}
    return max(sum((r[k]*o**k/factorial(k) for k in range(p+1,33,2)),Q())+tail[33]*o**33/factorial(33),
               sum((r[k]*o**k/factorial(k) for k in range(p+2,33,2)),Q())+tail[34]*o**34/factorial(34))


def check_budget(row,old,approx,clock):
    n2=Q(10**60);f=1-Q(old['augmented_gram_defect'])
    floor=Q(isqrt(f.numerator*int(n2)**2//f.denominator),int(n2));assert 0<floor and floor*floor<=f
    rho=Q(row['normal_residual_upper']);assert rho>=0
    biases=list(map(Q,old['complete_coefficient_bias_upper']));assert len(biases)==50
    omega=Q(row['frequency_upper']);effective=omega*(1+Q(1,10**14))
    k=factor(approx,effective);amplitude=Q(row['amplitude_upper']);family=k*amplitude
    assert Q(row['effective_frequency_upper'])==effective and Q(row['weighted_family_factor'])==k
    assert Q(row['family_radius'])==family and Q(row['gram_floor'])==f
    eta=Q(1,25000);mismatch=Q(1,10**6);centering=Q(1,10**20)
    assert Q(row['sensor_radius'])==eta and Q(row['mismatch_radius'])==mismatch and Q(row['clock_radius'])==clock
    total=eta+mismatch+centering+clock+family
    errors=[];gates=[];reserves=[]
    for n in range(2,51):
        margin=Q(1,2)-biases[n-1]-n*n*rho/f
        gates.append(margin>0 and n**4*total*total<margin*margin*f)
        errors.append(biases[n-1]+n*n*(total/floor+rho/f))
        reserves.append(margin*floor/n**2-eta-mismatch-clock-centering)
    reserve=min(reserves)
    assert Q(row['sufficient_family_radius_limit'])==reserve
    assert Q(row['strict_sufficient_amplitude_limit'])==reserve/k
    assert Q(row['complete_coefficient_error_maximum'])==max(errors)
    assert row['passing_gates']==sum(gates) and row['all_49_strict_rounding_gates']==all(gates)
    assert Q(row['complete_bias_maximum'])==max(biases[1:])
    return errors,gates


def run():
    folder=HERE.parent/'noise';ap=folder/'approximation.json';approx=json.loads(ap.read_text())
    dp=folder/'data.json';data=json.loads(dp.read_text());cp=folder/'consequences.json';consequence=json.loads(cp.read_text())
    prior=json.loads((ROOT/'research/transfer_theorem_2026_09/noise/evidence.json').read_text())
    assert len(data['readings'])==8900 and digest_pairs(data['readings'])==data['data_sha256']==consequence['data_sha256']
    ea=Q(1,10**14);eb=Q(1,10**11);clock=Q(approx['clock_and_derivative']['complete_clock_distortion_radius'])
    assert Q(data['true_clock_slope'])==1+ea and Q(data['true_clock_offset'])==eb
    assert data['polynomial_degree']==6 and Q(data['sinusoid_amplitude'])==4000
    assert Q(data['sinusoid_frequency'])==3 and Q(data['sinusoid_phase'])==Q(1,3)
    assert Q(data['mismatch_pointwise_radius'])==Q(9,10**7)<Q(1,10**6)
    truth=[1]+[n%7 for n in range(2,51)];assert truth==data['truth_a1_through_a50']
    source=[(n,a) for n,a in enumerate(truth,1)]+[(n,divisor(n)//2) for n in (51,60,72)]
    assert [list(v) for v in source]==data['finite_source_coefficients']
    assert all(0<=a<=divisor(n) for n,a in source)
    digitization=Q(data['digitization_pointwise_upper']);assert digitization<Q(1,10**35)
    assert Q(39,10**6)+digitization<Q(data['sensor_radius'])==Q(1,25000)
    maxerror=Q()
    with ctx.workprec(384):
        logs={n:arb(n).log() for n,a in source if a}
        for j,saved in enumerate(data['readings']):
            t=Q(2*j+1-8900,10);actual=ball((1+ea)*t+eb);x=actual/890
            signal=acb(0)
            for n,a in source:
                if not a:continue
                angle=actual*logs[n]
                signal+=ball(Q(a,n*n))*acb(angle.cos(),-angle.sin())
            # Direct powers differ from the producer's Horner implementation.
            polynomial=sum((acb(ball(Q(10**20,k+1)),ball(Q(10**20,k+2)))*x**k for k in range(7)),acb(0))
            drift=4000*(3*x+ball(Q(1,3))).sin()
            mismatch=ball(Q(9,10**7))*(actual/17).cos()
            sensor=ball(Q(39,10**6))*acb((actual/11).cos(),(actual/11).sin())
            ideal=signal+polynomial+drift+mismatch+sensor
            recorded=acb(ball(Q(saved[0])),ball(Q(saved[1])))
            err=endpoint(abs(recorded-ideal).upper());assert err<=digitization
            maxerror=max(maxerror,err)
    actualrows=[]
    for design in ('multi','outer'):
        for p in (6,8,10,12):
            name=f'result_{design}_{p}.json';path=folder/name;result=json.loads(path.read_text());cert=result['certificate']
            assert consequence['result_bindings'][name]==hashlib.sha256(path.read_bytes()).hexdigest()
            assert cert['data_sha256']==data['data_sha256'] and cert['proposal_sha256']==digest_pairs(result['proposal'])
            assert len(result['proposal'])==50+p and cert['degree']==p and cert['design']==design
            row=result['uncertainty_budget'];old=next(r for r in prior['designs'][design]['degrees'] if r['degree']==p)
            ar=next(r for r in approx['records'] if (r['design'],r['degree'])==(design,p))
            errors,gates=check_budget(row,old,ar,clock)
            assert Q(cert['normal_residual_upper'])==Q(row['normal_residual_upper'])<Q(1,10**30)
            assert Q(cert['nonpolynomial_drift_radius'])==Q(row['family_radius'])+clock+Q(1,10**6)
            assert Q(cert['joint_data_error_radius'])==Q(1,25000)+Q(cert['nonpolynomial_drift_radius'])+Q(1,10**20)
            assert cert['status']==('certified_under_declared_model' if all(gates) else 'not_certified')
            coordinates=cert['coordinates'];assert len(coordinates)==49
            for n,(entry,error,gate) in enumerate(zip(coordinates,errors,gates),2):
                assert entry['n']==n and entry['strict_uniform_rounding_gate']==gate
                assert Q(entry['coordinate_error_upper'])==error
                a,b=map(Q,result['proposal'][n-1]);re=n*n*a
                candidate=(2*re.numerator+re.denominator)//(2*re.denominator)
                disk=0<=candidate<=divisor(n) and (re-candidate)**2+(n*n*b)**2<=error*error
                assert entry['candidate_within_complex_error_disk']==disk
                assert entry['integer']==(candidate if gate and disk else None)
            if p==12:
                assert all(gates) and cert['answer_a1_through_a50']==truth
            else:assert not all(gates)
            actualrows.append({'design':design,'degree':p,'passing_gates':sum(gates),
                               'coefficient_error_upper_display':float(max(errors)),
                               'normal_residual_upper':cert['normal_residual_upper']})
    tables=[('actual_fixture_budgets',8),('frequency_degree_capacities',32),('planning_error_budgets',40)]
    for table,count in tables:
        assert len(consequence[table])==count
        for row in consequence[table]:
            design=row['design'];p=row['degree']
            old=next(r for r in prior['designs'][design]['degrees'] if r['degree']==p)
            ar=next(r for r in approx['records'] if (r['design'],r['degree'])==(design,p))
            check_budget(row,old,ar,clock)
            if table!='actual_fixture_budgets':assert Q(row['normal_residual_upper'])==Q(1,10**30)
    for w in consequence['best_tested_capacity_degrees']:
        candidates=[r for r in consequence['frequency_degree_capacities'] if r['design']==w['design'] and r['frequency_upper']==w['frequency_upper']]
        winner=max(candidates,key=lambda r:Q(r['strict_sufficient_amplitude_limit']))
        assert winner['degree']==w['best_tested_degree'] and winner['strict_sufficient_amplitude_limit']==w['strict_sufficient_amplitude_limit']
    for w in consequence['planning_minimum_error_degrees']:
        candidates=[r for r in consequence['planning_error_budgets'] if r['design']==w['design'] and r['amplitude_upper']==w['amplitude_upper']]
        winner=min(candidates,key=lambda r:Q(r['complete_coefficient_error_maximum']))
        assert winner['degree']==w['minimum_error_tested_degree'] and winner['complete_coefficient_error_maximum']==w['complete_coefficient_error_maximum']
    return {'verified':True,'working_precision_bits':384,'reconstructed_actual_readings':8900,
            'maximum_independent_digitization_error_upper':str(maxerror),
            'data_sha256':data['data_sha256'],'data_file_sha256':hashlib.sha256(dp.read_bytes()).hexdigest(),
            'approximation_sha256':hashlib.sha256(ap.read_bytes()).hexdigest(),
            'consequences_sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),
            'actual_results':actualrows,'actual_coordinate_gates_recomputed':392,
            'reported_actual_and_planning_budgets_recomputed':80,'future_residual_ceiling':'1/1000000000000000000000000000000',
            'scope':'Complete-tail and outward normal-residual bounds are separately reconstructed premises; this consumer independently reconstructs raw data and rederives all subsequent arithmetic consequences.'}


if __name__=='__main__':print(json.dumps(run(),indent=2))
