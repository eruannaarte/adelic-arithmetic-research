"""Independent exact replay of normalized vectors and all raw decoder decisions.

No decoder, normalization wrapper, timing code or previous consumer is imported.
Whole-time floors and derivative/model bounds are separate proved premises;
this check binds them to the actual raw readings and interval-clock interface.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def digest(data):return hashlib.sha256(json.dumps(list(map(str,data)),separators=(',',':')).encode()).hexdigest()


def solve(g,r):
    a,b=g[0];c,d=g[1];det=a*d-b*c
    assert b==c and a>0 and det>0
    return [(d*r[0]-b*r[1])/det,(a*r[1]-c*r[0])/det]


def run():
    rp=HERE.parent/'framework/raw_results.json';result=json.loads(rp.read_text())
    fp=HERE.parent/'resolution/fixtures.json';fixtures=json.loads(fp.read_text())
    kp=ROOT/'research/transfer_theorem_2026_09/resolution/kernel.json';kernel=json.loads(kp.read_text())
    cp=HERE.parent/'resolution/certificate_7.json';certificate=json.loads(cp.read_text())
    coefficients=[[[sum(map(Q,b))/2 for b in row] for row in d] for d in kernel['coefficient_intervals']]
    rows=certificate['bank_offsets'];assert rows==[-10,-8,-4,0,4,8,10]
    a0=Q(19,16);mu=a0*a0*Q(certificate['unnormalized_source_floor'])
    lam=a0*a0*Q(certificate['unnormalized_pair_floor'])
    assert result['case_count']==len(result['cases'])==len(fixtures['cases'])==12
    cases=[]
    for saved,fixture in zip(result['cases'],fixtures['cases']):
        answer=saved['answer'];packet=answer['normalization'];receipt=packet['scale']
        raw=list(map(Q,fixture['raw_data']));z=list(map(Q,packet['normalized_data']))
        t=Q(answer['nominal_time']);lo,hi=map(Q,answer['actual_time_interval']);true=Q(fixture['true_time'])
        assert t==Q(fixture['nominal_time'])==Q(receipt['time'])
        assert 1<=lo<=t<=hi<=2 and lo<=true<=hi
        eta=Q(receipt['sensor_relative_radius']);assert eta==Q(fixture['sensor_relative_radius'])
        r=Q(receipt['inverse_normalization']);e=Q(receipt['relative_multiplier_error_upper']);xi=Q(receipt['numerical_relative_budget'])
        assert r>0 and 0<=e<1 and 0<=xi<=Q(1,10**9)
        assert (1-e)**4<=(1+t)*r**4<=(1+e)**4
        gain=Q(4,3)+eta;charge=e*gain
        assert gain==Q(receipt['measured_output_gain_upper'])
        assert charge==Q(receipt['charged_physical_relative_radius'])<=xi
        assert z==[r*y for y in raw] and len(z)==7
        assert digest(raw)==packet['raw_data_sha256'] and digest(z)==packet['normalized_data_sha256']
        eps=Q(answer['generator_perturbation_operator_norm_upper'])
        assert Q(fixture['generator_decay_lambda'])<=eps and eps>=0
        h=max(t-lo,hi-t);delta=eta+Q(1,10**9)+charge+Q(37,1000)*h+Q(8,3)*eps
        budget=answer['transfer_budget']
        assert Q(budget['total_radius'])==delta and Q(budget['processing'])==charge
        assert Q(budget['timing'])==Q(37,1000)*h and Q(budget['model_mismatch'])==Q(8,3)*eps
        assert Q(budget['source_floor'])==mu and Q(budget['pair_floor'])==lam
        assert delta*delta<mu/Q(10**6) and 2*delta*delta<lam
        assert Q(budget['source_error_squared_upper'])==delta*delta/mu
        powers=[(t-Q(3,2))**k for k in range(33)]
        accepted=[];estimates={};energy=sum((a*a for a in z),Q())
        assert energy>0
        for label in range(490,511):
            matrix=[[sum((a*b for a,b in zip(coefficients[abs(row-(label-500))][port],powers)),Q())
                     for port in (0,1)] for row in rows]
            gram=[[sum((a[i]*a[j] for a in matrix),Q()) for j in (0,1)] for i in (0,1)]
            rhs=[sum((a[i]*v for a,v in zip(matrix,z)),Q()) for i in (0,1)]
            tube=[[gram[i][j]-int(i==j)*(delta/a0)**2 for j in (0,1)] for i in (0,1)]
            witness=solve(tube,rhs)
            if energy-sum((a*b for a,b in zip(rhs,witness)),Q())<=0:
                accepted.append(label);estimates[label]=solve(gram,rhs)
        assert accepted==answer['feasible_targets']==[fixture['source_label']]
        assert answer['status']=='unique' and answer['guaranteed_relative_source_accuracy']=='1/1000'
        estimate=estimates[accepted[0]];assert list(map(Q,answer['source_estimate']))==estimate
        truth=list(map(Q,fixture['source']));assert saved['source']==fixture['source']
        error2=sum(((a-b)**2 for a,b in zip(estimate,truth)),Q())/sum((a*a for a in truth),Q())
        assert error2==Q(saved['actual_relative_source_error_squared'])<delta*delta/mu<Q(1,10**6)
        assert answer['premise_sha256']=={'kernel':hashlib.sha256(kp.read_bytes()).hexdigest(),
                                           'certificate':hashlib.sha256(cp.read_bytes()).hexdigest()}
        cases.append({'target':accepted[0],'nominal_time':str(t),'actual_time':str(true),
                      'source_norm_for_validation_only':fixture['source_norm'],
                      'all_candidate_feasibility_tests_recomputed':21,
                      'source_error_squared':str(error2),'certified_source_error_squared_upper':str(delta*delta/mu)})
    return {'verified':True,'raw_results_sha256':hashlib.sha256(rp.read_bytes()).hexdigest(),
            'fixtures_sha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'case_count':len(cases),
            'exact_candidate_tests':21*len(cases),'cases':cases,
            'method':'exact quartic normalization; exact physical error budget; independent all-target rational feasibility and ordinary Gram source solve'}


if __name__=='__main__':print(json.dumps(run(),indent=2))
