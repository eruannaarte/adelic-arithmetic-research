"""Separate review of saved degree-11 answers and exact complex rounding gates.

This script does not import the degree-eleven budget or consequence producer.
The defining physical model is independently replayed in the adjacent logs.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import factorial,isqrt
import hashlib,json
HERE=Path(__file__).resolve().parent;P=HERE.parent/'degree11'

def digest_pairs(rows):
    return hashlib.sha256(json.dumps([[str(Q(a)),str(Q(b))] for a,b in rows],separators=(',',':')).encode()).hexdigest()

def run():
    evidence=json.loads((P/'evidence.json').read_text());summaries=[]
    for design in ('multi','outer'):
        prior=evidence['designs'][design]['degrees'][0]
        if prior['design']!=design or prior['degree']!=11:raise ValueError('tagged actual inverse contract')
        app=next(r for r in evidence['approximations'] if r['design']==design)
        parity={0:Q(),1:Q()};omega=3*(1+Q(1,10**14))
        for row in app['approximants']:
            k=row['order'];poly=list(map(Q,row['rational_polynomial']))
            if len(poly)!=12 or any(v for j,v in enumerate(poly) if (j-k)%2):raise ValueError('degree/parity nesting')
            parity[k%2]+=Q(row['weighted_residual_norm_upper'])*omega**k/factorial(k)
        for k in (33,34):parity[k%2]+=Q(app['weighted_monomial_norm_upper'][str(k)])*omega**k/factorial(k)
        factor=max(parity.values());floor=1-Q(prior['augmented_gram_defect'])
        scale=10**60;root=Q(isqrt(floor.numerator*scale*scale//floor.denominator),scale)
        for B in (4000,500):
            result=json.loads((P/f'result_{design}_B{B}.json').read_text());data=json.loads((P/f'data_B{B}.json').read_text())
            certificate=result['certificate'];budget=result['uncertainty_budget']
            if data['polynomial_degree']!=11 or Q(data['sinusoid_amplitude'])!=B:raise ValueError('actual fixture degree/amplitude')
            if len(data['readings'])!=8900 or len(result['proposal'])!=61:raise ValueError('physical 8900x61 dimensions')
            if certificate['data_sha256']!=digest_pairs(data['readings']) or certificate['proposal_sha256']!=digest_pairs(result['proposal']):raise ValueError('actual inverse/readings binding')
            rho=Q(certificate['normal_residual_upper'])
            if rho>Q(1,10**30) or rho!=Q(budget['normal_residual_upper']):raise ValueError('actual residual contract')
            family=B*factor
            if Q(budget['weighted_family_factor'])!=factor or Q(budget['family_radius'])!=family:raise ValueError('complete parity-family consequence')
            delta=Q(4,10**5)+Q(1,10**6)+Q(1,10**20)+Q(budget['clock_radius'])+family
            if Q(budget['complete_reading_radius'])!=delta:raise ValueError('complete uncertainty sum')
            count=0;errors=[]
            for n in range(2,51):
                tail=Q(prior['complete_coefficient_bias_upper'][n-1]);margin=Q(1,2)-tail-n*n*rho/floor
                count+=int(margin>0 and floor*margin*margin>n**4*delta*delta)
                E=tail+n*n*(delta/root+rho/floor);errors.append(E)
                if B==500:
                    answer=certificate['answer_a1_through_a50'][n-1]
                    re,im=map(Q,result['proposal'][n-1])
                    if answer!=data['truth_a1_through_a50'][n-1] or (n*n*re-answer)**2+(n*n*im)**2>E*E:raise ValueError('accepted integer complex disk')
            if count!=(32 if B==4000 else 49) or budget['passing_gates']!=count:raise ValueError('fixed sufficient-gate result')
            if list(map(Q,budget['complete_coefficient_error_bounds']))!=errors:raise ValueError('reported coordinate enclosures')
            if (certificate['status']=='certified_under_declared_model')!=(B==500):raise ValueError('accepted-certificate interpretation')
            summaries.append({'design':design,'amplitude':B,'passing_gates':count,'maximum_error_upper':str(max(errors))})
    # Every current result must also be present in the separate 384-bit replay.
    replay=json.loads((P/'precision_replay_384.json').read_text())
    if not replay['verified'] or replay['bits']!=384 or not replay['replays_saved_readings_and_proposals']:raise ValueError('model replay contract')
    if {(r['design'],r['amplitude']) for r in replay['results']}!={(d,B) for d in ('multi','outer') for B in (4000,500)}:raise ValueError('replay coverage')
    for r in replay['results']:
        result=json.loads((P/f"result_{r['design']}_B{r['amplitude']}.json").read_text())
        if Q(r['normal_residual_upper'])>Q(result['certificate']['normal_residual_upper']):raise ValueError('higher-precision saved residual bound')
    return {'schema':'separate-degree-eleven-review-v1','verified':True,'exact_strict_gate_checks':196,
      'accepted_integer_complex_disk_checks':98,'four_saved_upper_residuals_replayed_at_384_bits':True,
      'records':summaries,'reviewed_evidence_sha256':hashlib.sha256((P/'evidence.json').read_bytes()).hexdigest()}

if __name__=='__main__':
    out=run();(HERE/'degree11_review.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'verified':True,'exact_strict_gate_checks':out['exact_strict_gate_checks'],
       'records':[{**r,'maximum_error_upper':float(Q(r['maximum_error_upper']))} for r in out['records']]},indent=2))
