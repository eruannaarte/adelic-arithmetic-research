"""Independent exact-polynomial consumer: polynomial floors and full transfer."""
from fractions import Fraction as Q
from pathlib import Path
from itertools import combinations
from math import factorial
import argparse,hashlib,json

HERE=Path(__file__).resolve().parent
PRIOR=HERE.parents[1]/'transfer_theorem_2026_09/resolution'
CONFIGS={'6': {'bank':(-15,-7,-1,1,7,15),'source':Q(1,10**9),'eta':Q(3,10**8)}}
TARGETS=tuple(range(-10,11))
A0=Q(19,16);A1=Q(4,3);CENTER_SINGULAR=Q(999999,10**6)


def require(test,message):
    if not test:raise ValueError(message)


def same_json(left,right):
    if type(left) is not type(right):return False
    if type(left) is dict:
        return left.keys()==right.keys() and all(same_json(left[k],right[k]) for k in left)
    if type(left) is list:
        return len(left)==len(right) and all(same_json(a,b) for a,b in zip(left,right))
    return left==right


def rational(value):
    require(type(value) is str,'rational fields must be strings')
    return Q(value)


def interval_coefficients(kernel):
    require(kernel['schema']=='periodic-transverse-taylor-v1','kernel schema')
    require(same_json(kernel['model'],{'nx':1001,'period':64,'source_modes':[1,2],'g':'4/5','center':'3/2',
           'order':32,'exponential_degree':80,'maximum_distance':26,
           'output':'unnormalized global-x average; multiply by (1+tau)^(1/4)'}),'kernel model')
    require(kernel['coefficient_export_grid']=='1/1000000000000000000000000000000','coefficient grid')
    require(kernel['zero_mode']=='exactly zero by cosine-source mean' and kernel['parity']=='kernel(-d)=kernel(d)','symmetry contract')
    data=kernel['coefficient_intervals'];require(type(data) is list and len(data)==27,'kernel extent')
    result=[]
    for d in data:
        require(type(d) is list and len(d)==2,'source dimension');result.append([])
        for row in d:
            require(type(row) is list and len(row)==33,'Taylor dimension');result[-1].append([])
            for box in row:
                require(type(box) is list and len(box)==2,'interval shape')
                low,high=map(rational,box)
                require(low<=high and high-low<=Q(1,10**30),'coefficient width')
                result[-1][-1].append((low+high)/2)
    return result


def translated(coefficients,delta):
    """Independent Horner composition p(delta+h), without binomial sums."""
    out=[coefficients[-1]]
    for c in reversed(coefficients[:-1]):
        new=[delta*out[0]+c]
        new.extend(out[k-1]+delta*out[k] for k in range(1,len(out)))
        new.append(out[-1]);out=new
    return out


def exponential_upper(x):
    require(0<=x<202,'exponential series range')
    return sum((x**k/factorial(k) for k in range(201)),Q())+x**201/factorial(201)/(1-x/202)


def model_error_check(channels):
    require(A0**4<2 and A1**4>3,'normalization bounds')
    # Cauchy/Laurent image bound for all |displacement|<=26.
    a=Q(8);image=exponential_upper(Q(18,5)*(a+1/a-2))*(a**(-38)+a**(-90))/(1-a**(-64))
    require(image<Q(1,10**24),'complete periodic image bound')
    mu=Q(56,5)
    finite=2*mu**491/factorial(491)/(1-mu/492)
    require(finite<Q(1,10**500),'complete finite/infinite boundary bound')
    remainder=Q(1,2**33)
    rounding=Q(2,10**30)
    entry=remainder+Q(1,10**24)+Q(1,10**500)+rounding
    rho=Q(1,10**9)
    require(A1*A1*(2*channels)*entry*entry<rho*rho,'physical operator remainder')
    # Elementary pi<22/7 and sin(x)<=x give both H1 metrics <=41 I.
    require(1+4*Q(22,7)**2<41,'source metric bound')
    return rho


from flint import fmpq,fmpq_poly

def fq(q):
    q=Q(q);return fmpq(q.numerator,q.denominator)

def gram_polynomials(case,coeff):
    rows=[]
    for sensor in CONFIGS['6']['bank']:
        rows.append([fmpq_poly([fq((-1)**side*c) for c in coeff[abs(sensor-label)][port]])
                     for side,label in enumerate(case) for port in (0,1)])
    return [[sum((r[i]*r[j] for r in rows),fmpq_poly()) for j in range(2*len(case))] for i in range(2*len(case))]

def leading_minors_bareiss(matrix):
    """Fraction-free elimination, independent of producer permutation expansion."""
    A=[list(row) for row in matrix];n=len(A);previous=fmpq_poly([1]);out=[A[0][0]]
    for k in range(n-1):
        pivot=A[k][k];require(bool(pivot),'zero polynomial pivot')
        updated={}
        for i in range(k+1,n):
            for j in range(k+1,n):
                quotient,remainder=divmod(pivot*A[i][j]-A[i][k]*A[k][j],previous)
                require(not remainder,'nonexact Bareiss division');updated[i,j]=quotient
        for (i,j),entry in updated.items():A[i][j]=entry
        previous=pivot;out.append(A[k+1][k+1])
    return out

def interval_polynomial_lower(poly,center,radius):
    shifted=poly(fmpq_poly([fq(center-Q(3,2)),1]));r=fq(radius)
    # Interval Horner on [-r,r], with exact rational endpoint multiplication.
    lower=upper=fmpq(0)
    for coefficient in reversed(list(shifted)):
        products=(-r*lower,-r*upper,r*lower,r*upper)
        lower=min(products)+coefficient;upper=max(products)+coefficient
    return lower

def check(certificate=None,kernel=None,bank='6'):
    require(bank=='6','only the fixed six-row configuration is supported')
    path=PRIOR/'kernel.json';original=json.loads(path.read_text())
    kernel=original if kernel is None else kernel
    require(same_json(kernel,original),'unbound kernel premise')
    doc=json.loads((HERE/'certificate_6.json').read_text()) if certificate is None else certificate
    metadata={'schema':'polynomial-weighted-pair-six-row-v1','kernel_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
              'bank_offsets':[-15,-7,-1,1,7,15],'target_offsets':list(TARGETS),'time_interval':['1','2'],
              'unnormalized_source_floor':'1/1000000000','sensor_relative_radius':'3/100000000',
              'operator_relative_radius':'1/1000000000','numerical_relative_radius':'1/1000000000',
              'normalization_lower':'19/16','normalization_upper':'4/3','source_relative_accuracy_target':'1/1000','metric':'L2'}
    for key,value in metadata.items():require(same_json(doc[key],value),'changed certificate contract: '+key)
    coeff=interval_coefficients(kernel);rho=model_error_check(6);eta=Q(3,10**8);xi=Q(1,10**9);delta=eta+rho+xi
    b=delta/A0;sf=Q(1,10**9);mu=A0*A0*sf;accuracy=Q(1,1000)
    require(delta*delta<mu*accuracy*accuracy,'source accuracy gate')
    cases={(j,) for j in TARGETS}|set(combinations(TARGETS,2));covers={case:[] for case in cases};grams={}
    require(type(doc['records']) is list and doc['records'],'empty certificate')
    count=0
    for record in doc['records']:
        raw=record['case'];require(type(raw) is list and all(type(v) is int for v in raw),'case integer labels')
        case=tuple(raw);require(case in cases,'unknown source case')
        left,right=map(rational,(record['lower'],record['upper']));require(1<=left<right<=2,'time cell range')
        n=2*len(case)
        if n==2:
            require(record['source_split_weight'] is None,'individual split must be absent');threshold=[sf]*2
        else:
            split=rational(record['source_split_weight']);require(0<split<1,'source split range')
            threshold=[b*b/split]*2+[b*b/(1-split)]*2
        if case not in grams:grams[case]=gram_polynomials(case,coeff)
        H=[[p-fmpq_poly([fq(threshold[i])]) if i==j else p for j,p in enumerate(row)] for i,row in enumerate(grams[case])]
        declared=record['principal_minor_lower_bounds'];require(type(declared) is list and len(declared)==n,'principal-minor bounds shape')
        for polynomial,claim in zip(leading_minors_bareiss(H),declared):
            lower=interval_polynomial_lower(polynomial,(left+right)/2,(right-left)/2)
            bound=rational(claim);require(0<fq(bound)<=lower,'whole-cell principal minor positivity')
        covers[case].append((left,right));count+=1
    for case,parts in covers.items():
        ordered=sorted(parts)
        require(ordered and ordered[0][0]==1 and ordered[-1][1]==2,'case endpoints missing')
        require(all(a[1]==b[0] for a,b in zip(ordered,ordered[1:])),'case cover gap or overlap')
    metric={'source_relative_accuracy_target':str(accuracy),'sensor_relative_radius':str(eta),'operator_relative_radius':str(rho),
            'conditional_numerical_relative_radius':str(xi),'total_relative_radius':str(delta),
            'individual_approximate_map_floor':str(mu),'source_relative_error_squared_upper':str(delta*delta/mu),
            'pair_certificate':'all weighted two-block Gram inequalities are strictly positive definite on complete time covers'}
    return {'verified':True,'direct_rows':[485,493,499,501,507,515],'channel_count':6,'target_indices':[490,510],
            'known_time_interval':['1','2'],'individual_cases':21,'pair_cases':210,'whole_cell_records':count,
            'all_case_covers_verified':True,'physical_operator_model_error_upper':str(rho),'metrics':{'L2':metric},
            'pair_proof':'Sylvester leading principal minors, polynomial coefficients rational; consumer uses fraction-free elimination.',
            'premise':'full finite-x periodic Taylor enclosures require the preserved kernel.py replay'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=check()
    if args.write:(HERE/'checked_6.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
