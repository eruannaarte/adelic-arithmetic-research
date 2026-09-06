"""Third-agent audit: independent rational consequences and point inverse algebra.

The complete-time enclosure is additionally replayed through its separate
consumer at 384 bits. The 63 point calculations below are cross-checks, not
substitutes for that complete-time replay or for the physical kernel premise.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import isqrt
import importlib.util,json,hashlib,time,argparse
HERE=Path(__file__).resolve().parent
SPATIAL=HERE.parent/'resolution'
spec=importlib.util.spec_from_file_location('_third_potential_consumer',SPATIAL/'check.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

def value(poly,t,derivative=False):
    z=t-Q(3,2)
    if derivative:return sum((k*a*z**(k-1) for k,a in enumerate(poly) if k),Q())
    return sum((a*z**k for k,a in enumerate(poly)),Q())
def alpha_upper(t):
    lo=Q(1);hi=Q(4,3)
    for _ in range(64):
        mid=(lo+hi)/2
        if mid**4>=1+t:hi=mid
        else:lo=mid
    return hi

def inverse_times(P,D):
    a=sum((row[0]**2 for row in P),Q());b=sum((row[0]*row[1] for row in P),Q());d=sum((row[1]**2 for row in P),Q())
    det=a*d-b*b
    if not det>0:raise ValueError('point Gram positivity failed')
    rhs=[[sum((p[i]*v[j] for p,v in zip(P,D)),Q()) for j in (0,1)] for i in (0,1)]
    return [[(d*rhs[0][j]-b*rhs[1][j])/det for j in (0,1)],[(a*rhs[1][j]-b*rhs[0][j])/det for j in (0,1)]]
def norm2(M):return sum((v*v for row in M for v in row),Q())
def sqrt_upper(q):
    s=10**50;k=isqrt(q.numerator*s*s//q.denominator);return Q(k+int(Q(k,s)**2<q),s)

def review():
    reviewed={name:hashlib.sha256((SPATIAL/name).read_bytes()).hexdigest() for name in ('check.py','directions.json','kernel_derivative.json','PROOFS.md')}
    started=time.monotonic();p=c.kernel(c.PRIOR/'kernel.json');g=c.kernel(SPATIAL/'kernel_derivative.json',True)
    worst={k:Q() for k in c.LIMITS};count=0
    for target in range(490,511):
        for t in (Q(1),Q(3,2),Q(2)):
            P=[[value(p[abs(row-target)][k],t) for k in (0,1)] for row in c.BANK]
            T=[[value(p[abs(row-target)][k],t,True)+value(p[abs(row-target)][k],t)/(4*(1+t)) for k in (0,1)] for row in c.BANK]
            G=[[value(g[abs(row-target)][k],t) for k in (0,1)] for row in c.BANK]
            Ti=inverse_times(P,T);Gi=inverse_times(P,G);alpha=alpha_upper(t)
            candidates={'time_forward':alpha*alpha*norm2(T),'potential_forward':alpha*alpha*norm2(G),'time_inverse':norm2(Ti),'potential_inverse':norm2(Gi)}
            for name,X,Y,scale in (('forward',T,G,alpha),('inverse',Ti,Gi,Q(1))):
                candidates['joint_'+name]=scale*scale*max(norm2([[c.H*x+s*c.DG*y for x,y in zip(a,b)] for a,b in zip(X,Y)]) for s in (-1,1))
            for name,norm_squared in candidates.items():
                if not norm_squared<c.LIMITS[name]**2:raise ValueError('independent point bound failed: '+name)
                worst[name]=max(worst[name],norm_squared)
            count+=1
    # Derive the three Cauchy tails directly by geometric series formulas.
    q=Q(1,3);k=33
    value_tail=q**k/(1-q)
    potential_tail=12*value_tail
    time_tail=2*q**k*(k/(1-q)+q/(1-q)**2)
    if (value_tail,potential_tail,time_tail)!=(Q(1,2*3**32),Q(6,3**32),Q(67,2*3**32)):raise ValueError('Cauchy tail identity')
    # Whole potential rectangle, not only the nominal generator.
    Hmax=Q(56,5)+4*c.DG
    if not Hmax<Q(45,4):raise ValueError('generator bound on uncertain family')
    mixed=Q(1,6)*8+Q(4,3)*(4+Q(45,4)*8)
    if not mixed==Q(380,3)<128:raise ValueError('mixed derivative bound')
    second_time=Q(1,16)+2*Q(1,6)*Q(3,8)+Q(4,3)*Q(9,16)
    if not second_time==Q(15,16)<1:raise ValueError('second time derivative bound')
    remainder=c.H**2/2+128*c.H*c.DG+Q(128,3)*c.DG**2+(c.H+c.DG)*Q(1,10**12)
    if remainder!=Q(c.remainders()['total_nonlinear_radius']):raise ValueError('joint remainder mismatch')
    free=c.ETA+c.RHO+c.XI+remainder;total=free+c.LIMITS['joint_forward']
    if not 2*total*total<c.LAM:raise ValueError('independent label gate')
    accuracy=sqrt_upper(free*free/c.MU)+c.LIMITS['joint_inverse']
    if not accuracy<Q(1,1000):raise ValueError('independent query inverse gate')
    if not total*total>c.MU*Q(1,1000)**2:raise ValueError('uniform inverse comparison')
    complete=c.verify(bits=384)
    if reviewed!={name:hashlib.sha256((SPATIAL/name).read_bytes()).hexdigest() for name in reviewed}:raise ValueError('reviewed files changed during audit')
    return {'verified':True,'reviewer_scope':'independent exact-rational inverse algebra and remainder derivation; fresh 384-bit complete-time consumer replay',
            'point_cases':count,'corner_cases':2*count,'exact_point_norm_upper_bounds':{k:str(sqrt_upper(v)) for k,v in worst.items()},
            'cauchy_tail_identities_verified':True,'mixed_derivative_entire_rectangle_upper':str(mixed),'nonlinear_radius':str(remainder),
            'independent_source_error_upper':str(accuracy),'complete_time_cases':complete['case_cells'],'complete_consumer_precision_bits':384,
            'separate_explanations_note':'Two candidate sources may carry different clock and potential values; each complete forward tube is charged independently.',
            'physical_premise':'Potential derivative enclosure replay and old finite-x kernel replay remain separate accepted physical premises.',
            'reviewed_sha256':reviewed,
            'elapsed_seconds':time.monotonic()-started}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=review()
    if args.write:(HERE/'review_potential.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('exact_point_norm_upper_bounds','reviewed_sha256')},indent=2))
