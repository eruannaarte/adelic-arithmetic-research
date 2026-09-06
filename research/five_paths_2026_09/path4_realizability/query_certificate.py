"""Complete d_2-tail and arithmetic constrained-query certificate.

Finite sum 51..10000 is Arb; every larger integer is covered by two analytic
pieces. No discriminant ceiling and no truncated-source assumption are used.
"""
from pathlib import Path
from fractions import Fraction as F
import json
import sys
from itertools import product

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from flint import arb,ctx,fmpq
from arithmetic_sensing_iv import REFERENCE_COEFFICIENTS
from exact_trigonometric_positivity import rational_continuum_certificate
from verified_end_to_end_certificate import VerifiedTimeComponent, verified_ensemble_finite_tail_bounds, verified_ensemble_gram_row_bound

HERE=Path(__file__).resolve().parent
COMPS=(VerifiedTimeComponent(510,2550,F(125,65536)),VerifiedTimeComponent(1780,8900,F(65411,65536)))


def ball(x):
    x=F(x);return arb(fmpq(x.numerator,x.denominator))


def rational(x):
    m,e=x.man_exp(); m=int(m);e=int(e)
    return F(m*(1<<e)) if e>=0 else F(m,1<<(-e))


def upper(x):return rational(x.upper())


def measurement_contract():
    """Prove positivity and the exact normalization/nesting hypotheses."""
    coeff=[F.from_float(float(x)) for x in REFERENCE_COEFFICIENTS]
    if not COMPS or any(type(c.observation_time) is not int or
                       type(c.sample_count) is not int or
                       not isinstance(c.weight,F) or c.weight<=0 or c.observation_time<1 or
                       c.sample_count<=len(coeff) or
                       5*c.observation_time!=c.sample_count for c in COMPS):
        raise ValueError('invalid positive common-spacing measurement ensemble')
    if sum((c.weight for c in COMPS),F())!=1:
        raise ValueError('measurement weights must sum exactly to one')
    largest=max(c.sample_count for c in COMPS)
    if any((largest-c.sample_count)%2 for c in COMPS):
        raise ValueError('centered measurement grids are not nested')
    positivity=rational_continuum_certificate(coeff,F(1,10**9),F(3))
    if not positivity.certified:
        raise ValueError('window positivity was not certified')
    # Exact midpoint orthogonality annihilates all nonconstant harmonics.
    return coeff


def remote_bound(M=10000,K=10**9):
    if type(M) is not int or type(K) is not int or M<50 or K<=M:
        raise ValueError('remote cutoffs must be integers with 50 <= M < K')
    # Integral partial summation: sum_{k>x} d_2(k)/k^2 <= 2(log x+2)/x.
    massM=2*((arb(M)).log()+2)/M
    massK=2*((arb(K)).log()+2)/K
    coeff=measurement_contract()
    C=1+2*sum(map(abs,coeff),F())
    low=(arb(M+1)/50).log()/10
    high=arb(K).log()/10
    terms=[];response=F()
    for comp in COMPS:
        left=low-arb.pi()*len(coeff)/comp.sample_count
        right=high+arb.pi()*len(coeff)/comp.sample_count
        if not (left>0 and right<arb.pi()): raise ValueError('alias-free middle interval not proved')
        # sin is concave on [0,pi], so its minimum is at an endpoint.
        lo=min(rational(left.sin().lower()),rational(right.sin().lower()))
        if lo<=0: raise ValueError('sine denominator not separated')
        bound=F(C,comp.sample_count)/lo
        response+=comp.weight*bound
        terms.append({'sample_count':comp.sample_count,'sine_lower':str(lo),'response_upper':str(bound)})
    # Compose published outward endpoints exactly, so a stdlib checker can
    # reproduce this final consequence without Arb or hidden ball endpoints.
    massM_upper=upper(massM);massK_upper=upper(massK)
    total=response*massM_upper+massK_upper
    return {'M':M,'K':K,'coefficient_triangle_constant':str(C),'middle_response_upper':str(response),
            'mass_above_M_upper':str(massM_upper),'mass_above_K_upper':str(massK_upper),
            'component_bounds':terms,'tail_upper':str(total)}


def derive(tails,qrows,eta=F(2001,100000)):
    if len(tails)!=50 or len(qrows)!=50:
        raise ValueError('exactly 50 tail and Gram row bounds are required')
    tails=[F(x) for x in tails];qrows=[F(x) for x in qrows];eta=F(eta)
    if eta<0 or any(t<0 for t in tails) or any(q<0 or q>=1 for q in qrows):
        raise ValueError('require nonnegative noise/tails and Gram rows in [0,1)')
    q=max(qrows);top=max(tails)
    B=[n*n*(t+qi*top/(1-q)) for n,(t,qi) in enumerate(zip(tails,qrows),1)]
    # Stage1 recovers a2,a3, hence exactly determines c20=a4 and c45=a9.
    anchor=[{'n':n,'margin_squared':str((F(1,2)-B[n-1])**2*(1-q)/n**4),
             'bias_upper':str(B[n-1]),'passes':B[n-1]<F(1,2) and eta**2<(F(1,2)-B[n-1])**2*(1-q)/n**4} for n in (2,3)]
    rows=[]
    for c20,c45 in product((1,3),repeat=2):
        pairs=((5,1),(20,c20),(45,c45))
        J=sum((F(c*c,n**4) for n,c in pairs),F())
        alpha=[F(c,n**4)/J for n,c in pairs]
        bias=sum((a*B[n-1] for a,(n,c) in zip(alpha,pairs)),F())
        eta2=(F(1,2)-bias)**2*(1-q)*J
        rows.append({'a4':c20,'a9':c45,'J':str(J),'alpha':list(map(str,alpha)),'bias_upper':str(bias),
                     'admissible_radius_squared':str(eta2),'passes':bias<F(1,2) and eta**2<eta2})
    return {'q':str(q),'bias_upper':list(map(str,B)),'declared_eta':str(eta),'anchors':anchor,'query_cases':rows,
            'all_pass':all(r['passes'] for r in anchor+rows),'larger_than_envelope_limit':eta>F(1,50)}


def build(precision=192,processes=2):
    if type(precision) is not int or precision<64:
        raise ValueError('precision must be an integer of at least 64 bits')
    ctx.prec=precision
    rem=remote_bound()
    finite=verified_ensemble_finite_tail_bounds(2,COMPS,50,10000,precision=precision,output_scale_bits=128,processes=processes)
    gram=verified_ensemble_gram_row_bound(COMPS,50,precision=precision,output_scale_bits=128)
    fs=[F(x,1<<128) for x in finite.numerators];qs=[F(x,1<<128) for x in gram.row_numerators]
    ts=[f+F(rem['tail_upper']) for f in fs]
    return {'schema':'quadratic-query-v1','source':'all real quadratic fields, without a discriminant ceiling',
            'precision':precision,'maximum_norm':50,'sample_count':8900,'remote':rem,
            'finite_d2_tail_upper':list(map(str,fs)),'complete_tail_upper':list(map(str,ts)),
            'gram_row_upper':list(map(str,qs)),'consequence':derive(ts,qs)}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--precision',type=int,default=192);p.add_argument('--output',type=Path,default=HERE/'certificate.json');a=p.parse_args()
    doc=build(a.precision);a.output.write_text(json.dumps(doc,indent=2)+'\n')
    print('complete quadratic query guarantee:',doc['consequence']['all_pass'])
    print('noise radius:',doc['consequence']['declared_eta'])
    print('remote tail per normalized column:',float(F(doc['remote']['tail_upper'])))
    for row in doc['consequence']['query_cases']:
        print(row['a4'],row['a9'],'bias',float(F(row['bias_upper'])),'radius',float(ball(F(row['admissible_radius_squared'])).sqrt().lower()))
