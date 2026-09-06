"""Data-dependent integer recovery, conditional on the declared physical bounds.

A normal residual verifies a solve, not the physical noise or drift promise.
No residual is accepted as input: verify() evaluates it from all readings.
"""
from fractions import Fraction as Q
from math import isqrt
import argparse, json
from pathlib import Path
from physical import (PhysicalModel, M, parse_pairs, exact, encode, digest_pairs)

XI=Q(1,10**20)


def sqrt_bracket(x,digits=60):
    x=Q(x)
    if x<0:raise ValueError('negative square root')
    scale=10**digits;k=isqrt(x.numerator*scale*scale//x.denominator)
    return Q(k,scale),Q(k+1,scale)


def divisor14(n):
    from math import comb
    ans=1;p=2
    while p*p<=n:
        a=0
        while n%p==0:n//=p;a+=1
        ans*=comb(a+13,13);p+=1
    return ans*14 if n>1 else ans


def consequences(record,proposal,rho,eta,nu):
    """Exact rational consequence layer; the physical verifier supplies rho."""
    rho,eta,nu=map(exact,(rho,eta,nu))
    if min(rho,eta,nu)<0:raise ValueError('negative error allowance')
    theta=parse_pairs(proposal,50+record['degree'])
    f=1-Q(record['augmented_gram_defect'])
    if f<=0:raise ValueError('nonpositive augmented Gram floor')
    sqlo,sqhi=sqrt_bracket(f)
    biases=list(map(Q,record['complete_coefficient_bias_upper']))
    if len(biases)!=50 or min(biases)<0:raise ValueError('complete bias dimensions/sign')
    nuisance_cap=min((Q(1,2)-biases[n-1]-n*n*rho/f)*sqlo/n**2 for n in range(2,51))-eta-XI
    total=eta+nu+XI
    coordinates=[];answer=[1];all_gates=True
    for n in range(2,51):
        margin=Q(1,2)-biases[n-1]-n*n*rho/f
        gate=margin>0 and n**4*total**2<margin**2*f
        error=biases[n-1]+n*n*(total/sqlo+rho/f)
        re,im=(n*n*x for x in theta[n-1])
        candidate=(2*re.numerator+re.denominator)//(2*re.denominator)
        # Under the model, a successful <1/2 gate must contain this one integer.
        compatible=(0<=candidate<=divisor14(n) and (re-candidate)**2+im**2<=error**2)
        success=gate and compatible
        coordinates.append({'n':n,'strict_uniform_rounding_gate':gate,
                            'coordinate_error_upper':str(error),'integer':candidate if success else None,
                            'candidate_within_complex_error_disk':compatible})
        all_gates &= success;answer.append(candidate if success else None)
    return {'status':'certified_under_declared_model' if all_gates else 'not_certified',
            'gram_floor':str(f),'normal_residual_upper':str(rho),
            'sensor_radius':str(eta),'nonpolynomial_drift_radius':str(nu),
            'digital_correction_radius':str(XI),'joint_data_error_radius':str(total),
            'strict_sufficient_nonpolynomial_budget_limit':str(nuisance_cap),
            'answer_a1_through_a50':answer if all_gates else None,'coordinates':coordinates}


def verify(model,data,proposal,eta,nu,dual_evaluation=False):
    pairs=parse_pairs(data,M);theta=parse_pairs(proposal,50+model.degree)
    rho,normal=model.residual(pairs,theta,'normal')
    audit=None
    if dual_evaluation:
        other,readings=model.residual(pairs,theta,'readings')
        for j in range(50+model.degree):
            if not normal[j,0].overlaps(readings[j,0]):raise ValueError('residual identities disagree')
        audit={'reading_space_residual_upper':str(other),'componentwise_enclosures_overlap':True}
        rho=max(rho,other)
    result=consequences(model.record,theta,rho,eta,nu)
    result.update({'schema':'operational-arithmetic-answer-v1','design':model.design,
                   'degree':model.degree,'working_precision_bits':model.bits,
                   'data_sha256':digest_pairs(pairs),'proposal_sha256':digest_pairs(theta),
                   'actual_reconstructed_gram_defect_upper':str(model.actual_gram_defect_upper),
                   'residual_identity_audit':audit,
                   'premise':'known a(1)=1; all integer 0<=a(n)<=d14(n); stated W-norm sensor and remainder bounds; unrestricted degree-p polynomial'})
    return result


def solve(model,data,eta,nu,dual_evaluation=False):
    proposal=model.propose(data,'float')
    result=verify(model,data,proposal,eta,nu,dual_evaluation)
    initial={'status':result['status'],'normal_residual_upper':result['normal_residual_upper']}
    if result['status']=='certified_under_declared_model':method='binary64 proposal verified by Arb'
    else:
        proposal=model.propose(data,'arb')
        result=verify(model,data,proposal,eta,nu,dual_evaluation)
        method='Arb augmented solve proposed and separately residual checked'
    return {'initial_proposal':initial,'accepted_proposal_method':method,
            'proposal':encode(proposal),'certificate':result}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('data',type=Path,help='JSON with readings as 8,900 [real rational, imaginary rational] pairs')
    p.add_argument('--design',choices=['multi','outer'],default='multi')
    p.add_argument('--degree',type=int,choices=[6,8,10,12],default=8)
    p.add_argument('--bits',type=int,default=256)
    p.add_argument('--eta',required=True);p.add_argument('--nu',required=True)
    p.add_argument('--proposal',type=Path,help='optional exact augmented proposal pairs; no solver invoked')
    args=p.parse_args();data=json.loads(args.data.read_text())['readings']
    model=PhysicalModel(args.design,args.degree,args.bits)
    if args.proposal:
        result=verify(model,data,json.loads(args.proposal.read_text()),args.eta,args.nu,True)
    else:result=solve(model,data,args.eta,args.nu,True)
    print(json.dumps(result,indent=2))
