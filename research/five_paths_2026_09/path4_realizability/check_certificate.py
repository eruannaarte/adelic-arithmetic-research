"""Independent stdlib check of Path 4's rational and remote-tail consequences.

The finite 51..10000 vector and Gram row vector are trusted outward inputs here;
regenerate them with query_certificate.py for a complete Arb replay. The remote
logarithms, pi, sine bounds, positive measure, and recovery algebra are rebuilt
using exact integers/Fractions only, without importing the producer or numpy.
"""
from fractions import Fraction as Q
from itertools import product
from math import factorial
from pathlib import Path
import ast
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT))
from exact_trigonometric_positivity import rational_continuum_certificate

COMPONENTS=((510,2550,Q(125,65536)),(1780,8900,Q(65411,65536)))


def require(condition,message):
    if not condition: raise ValueError(message)


def coefficients():
    tree=ast.parse((ROOT/'arithmetic_sensing_iv.py').read_text())
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REFERENCE_COEFFICIENTS' for t in node.targets):
            return [Q.from_float(float(x)) for x in ast.literal_eval(node.value.args[0])]
    raise ValueError('reference coefficients missing')


def log_interval(x,terms=350):
    """Rational enclosure from log x = k log 2 + 2 atanh((y-1)/(y+1))."""
    x=Q(x);require(x>0,'log input must be positive')
    k=0
    while x>=2: x/=2;k+=1
    while x<1: x*=2;k-=1
    def unit_log(y):
        z=(y-1)/(y+1);power=z;total=Q()
        for j in range(terms):
            total+=power/(2*j+1);power*=z*z
        remainder=2*power/((2*terms+1)*(1-z*z))
        return 2*total,2*total+remainder
    a,b=unit_log(x);c,d=unit_log(Q(2))
    return (a+k*c,b+k*d) if k>=0 else (a+k*d,b+k*c)


def pi_interval(terms=256):
    # tan(4 atan(1/5))=120/119. Subtracting atan(1/239) gives
    # tangent 1, with angle in (0,pi/2), hence Machin's identity.
    def atan(z):
        value=sum(((-1)**j*z**(2*j+1)/(2*j+1) for j in range(terms)),Q())
        next_term=(-1)**terms*z**(2*terms+1)/(2*terms+1)
        return min(value,value+next_term),max(value,value+next_term)
    a,b=atan(Q(1,5));c,d=atan(Q(1,239))
    return 16*a-4*d,16*b-4*c


def sine_lower(interval,terms=110):
    lo,hi=interval
    # Outward dyadic rounding prevents enormous denominator growth in powers.
    scale=1<<800
    lo=Q((lo.numerator*scale)//lo.denominator,scale)
    hi=Q(-((-hi.numerator*scale)//hi.denominator),scale)
    require(0<lo<=hi<4,'sine interval outside declared positive range')
    x=(lo+hi)/2
    square=x*x;polynomial=Q()
    for j in range(terms-1,-1,-1):
        polynomial=polynomial*square+Q((-1)**j,factorial(2*j+1))
    total=x*polynomial
    # Taylor through the next (zero) even coefficient; every derivative of
    # sin has absolute value <=1. The last subtraction uses |sin'|<=1.
    remainder=x**(2*terms+1)/factorial(2*terms+1)
    return total-remainder-(hi-lo)/2


def check_remote(remote,coeff):
    M=remote['M'];K=remote['K']
    require(type(M) is int and type(K) is int and M==10000 and K==10**9,'wrong finite/remote partition')
    pilo,pihi=pi_interval()
    lowlog=log_interval(Q(M+1,50));highlog=log_interval(K)
    require(len(remote['component_bounds'])==len(COMPONENTS),'wrong component count')
    C=1+2*sum(map(abs,coeff),Q())
    require(Q(remote['coefficient_triangle_constant'])==C,'wrong response triangle constant')
    response=Q()
    for (T,m,weight),row in zip(COMPONENTS,remote['component_bounds']):
        require(row['sample_count']==m and 5*T==m,'wrong component grid')
        left=(lowlog[0]/10-pihi*len(coeff)/m,lowlog[1]/10-pilo*len(coeff)/m)
        right=(highlog[0]/10+pilo*len(coeff)/m,highlog[1]/10+pihi*len(coeff)/m)
        require(left[0]>0 and right[1]<pilo,'middle interval may contain an alias')
        s=Q(row['sine_lower'])
        require(0<s<=min(sine_lower(left),sine_lower(right)),'sine lower bound not independently proved')
        bound=C/(m*s)
        require(Q(row['response_upper'])==bound,'wrong component response bound')
        response+=weight*bound
    require(Q(remote['middle_response_upper'])==response,'wrong mixture response bound')
    massM=Q(remote['mass_above_M_upper']);massK=Q(remote['mass_above_K_upper'])
    require(massM>=2*(log_interval(M)[1]+2)/M,'mass above M is underestimated')
    require(massK>=2*(log_interval(K)[1]+2)/K,'mass above K is underestimated')
    remote_tail=response*massM+massK
    require(Q(remote['tail_upper'])==remote_tail,'remote endpoint composition differs')
    return remote_tail


def check(document):
    require(document['schema']=='quadratic-query-v1','wrong schema')
    require(document['source']=='all real quadratic fields, without a discriminant ceiling','wrong source class')
    require(document['maximum_norm']==50 and document['sample_count']==8900,'wrong model sizes')
    require(type(document['precision']) is int and document['precision']>=64,'invalid precision record')
    coeff=coefficients()
    require(len(coeff)==8,'unexpected harmonic count')
    positivity=rational_continuum_certificate(coeff,Q(1,10**9),Q(3))
    require(positivity.certified,'exact window positivity failed')
    require(sum((w for _,_,w in COMPONENTS),Q())==1,'unnormalized mixture')
    require(all(w>0 and m>len(coeff) and (8900-m)%2==0 for _,m,w in COMPONENTS),'invalid positive nested grids')
    remote=check_remote(document['remote'],coeff)
    finite=[Q(x) for x in document['finite_d2_tail_upper']]
    tails=[Q(x) for x in document['complete_tail_upper']]
    rows=[Q(x) for x in document['gram_row_upper']]
    require(len(finite)==len(tails)==len(rows)==50,'wrong vector lengths')
    require(all(t>=0 for t in finite+tails) and all(0<=q<1 for q in rows),'invalid outward vector domain')
    require(tails==[t+remote for t in finite],'incomplete tail composition')
    q=max(rows);top=max(tails)
    B=[n*n*(tails[n-1]+rows[n-1]*top/(1-q)) for n in range(1,51)]
    c=document['consequence'];eta=Q(c['declared_eta'])
    require(eta==Q(2001,100000),'noise radius differs from declared theorem')
    require(Q(c['q'])==q and [Q(x) for x in c['bias_upper']]==B,'wrong inverse-tail consequence')
    anchors=[]
    for n in (2,3):
        margin=(Q(1,2)-B[n-1])**2*(1-q)/n**4
        passed=B[n-1]<Q(1,2) and eta*eta<margin
        anchors.append({'n':n,'margin_squared':str(margin),'bias_upper':str(B[n-1]),'passes':passed})
    require(c['anchors']==anchors,'wrong anchor recovery consequences')
    cases=[]
    for a4,a9 in product((1,3),repeat=2):
        pairs=((5,1),(20,a4),(45,a9))
        J=sum((Q(v*v,n**4) for n,v in pairs),Q())
        alpha=[Q(v,n**4)/J for n,v in pairs]
        require(sum((a*v for a,(_,v) in zip(alpha,pairs)),Q())==1,'query estimator not normalized')
        bias=sum((a*B[n-1] for a,(n,_) in zip(alpha,pairs)),Q())
        margin=(Q(1,2)-bias)**2*(1-q)*J
        cases.append({'a4':a4,'a9':a9,'J':str(J),'alpha':list(map(str,alpha)),'bias_upper':str(bias),
                      'admissible_radius_squared':str(margin),'passes':bias<Q(1,2) and eta*eta<margin})
    require(c['query_cases']==cases,'wrong constrained-query consequences')
    require(all(x['passes'] for x in anchors+cases) and c['all_pass'] is True,'recovery threshold fails')
    require(eta>Q(1,50) and c['larger_than_envelope_limit'] is True,'no strict envelope improvement')
    return {'verified':True,'noise_radius':str(eta),'positive_window':'1e-9 < density < 3',
            'remote_method':'independent rational log/pi/sine bounds',
            'trusted_inputs':'finite-tail and Gram vectors: replay producer to reconstruct'}


if __name__=='__main__':
    path=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'certificate.json'
    print(json.dumps(check(json.loads(path.read_text())),indent=2))
