"""Exact independent arithmetic consequences of physically checked residuals.

This check binds the fixture, proposal and prior tail bounds; it does not replace
Arb reconstruction of the physical residual performed by demonstrate.py.
"""
from pathlib import Path
from fractions import Fraction as Q
from math import isqrt, factorial
import hashlib, json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def digest(rows):
    canon=[[str(Q(a)),str(Q(b))] for a,b in rows]
    return hashlib.sha256(json.dumps(canon,separators=(',',':')).encode()).hexdigest()


def check():
    approximation=json.loads((HERE/'approximation.json').read_text())
    evidence=json.loads((ROOT/'research/transfer_theorem_2026_09/noise/evidence.json').read_text())
    data=json.loads((HERE/'data.json').read_text())
    outputs=[];checked=0
    for r in approximation['designs']:
        design=r['design'];result=json.loads((HERE/('result_'+design+'.json')).read_text())
        cert=result['certificate'];theta=[tuple(map(Q,p)) for p in result['proposal']]
        if cert['data_sha256']!=digest(data['readings']) or cert['proposal_sha256']!=digest(result['proposal']):
            raise ValueError('data or proposal binding')
        record=next(v for v in evidence['designs'][design]['degrees'] if v['degree']==8)
        f=1-Q(record['augmented_gram_defect']);bias=list(map(Q,record['complete_coefficient_bias_upper']))
        rho=Q(cert['normal_residual_upper']);eta=Q(4,100000);nu=20000*Q(r['uniform_phase_frequency_factor']);xi=Q(1,10**20)
        if f<=0 or min(rho,eta,nu,xi)<0:raise ValueError('invalid Gram or error bound')
        if cert['nonpolynomial_drift_radius']!=str(nu) or Q(cert['sensor_radius'])!=eta:raise ValueError('family budget binding')
        scale=10**60;sqrt_lower=Q(isqrt(f.numerator*scale*scale//f.denominator),scale)
        max_error=Q(0);old_fail=0
        for n in range(2,51):
            margin=Q(1,2)-bias[n-1]-n*n*rho/f
            if not margin>0 or not n**4*(eta+nu+xi)**2<margin**2*f:raise ValueError('integer gate')
            err=bias[n-1]+n*n*((eta+nu+xi)/sqrt_lower+rho/f)
            if not err<Q(1,2):raise ValueError('explicit error enclosure')
            re,im=(n*n*c for c in theta[n-1])
            answer=(2*re.numerator+re.denominator)//(2*re.denominator)
            if answer!=data['truth_a1_through_a50'][n-1]:raise ValueError('integer consequence disagrees with synthetic truth')
            if (re-answer)**2+im**2>err**2:raise ValueError('complex error-disk consequence')
            max_error=max(max_error,err);checked+=1
            old=Q(20000,factorial(9))
            old_fail+=not (margin>0 and n**4*(eta+old+xi)**2<margin**2*f)
        if old_fail==0:raise ValueError('old pointwise comparison failed')
        outputs.append({'design':design,'integer_gates':49,'maximum_coefficient_error_upper':str(max_error),
                        'old_pointwise_failed_gates':old_fail,'normal_residual_upper':str(rho),
                        'joint_reading_radius':str(eta+nu+xi),'complete_tail_premise_unchanged':True})
    return {'schema':'weighted-drift-exact-consequences-v1','verified':True,'integer_gates_checked':checked,'designs':outputs}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();result=check()
    if a.write:(HERE/'consequences.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
