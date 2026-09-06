"""Independent standard-library consumer: polynomial floors and full transfer."""
from fractions import Fraction as Q
from pathlib import Path
from itertools import combinations
from math import factorial
import argparse,hashlib,json

HERE=Path(__file__).resolve().parent
PRIOR=HERE.parents[1]/'transfer_theorem_2026_09/resolution'
CONFIGS={
 '9': {'bank':(-15,-12,-8,-4,0,4,8,12,16),'source':Q(65,10**9),'pair':Q(1,10**11),'eta':Q(3,10**7)},
 '8': {'bank':(-12,-10,-6,-2,2,6,10,14),'source':Q(4,10**8),'pair':Q(1,10**12),'eta':Q(23,10**8)},
}
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


def check(certificate=None,kernel=None,bank='9'):
    require(bank in CONFIGS,'unknown bank configuration')
    config=CONFIGS[bank];BANK=config['bank'];sf=config['source'];pf=config['pair']
    path=PRIOR/'kernel.json'
    kernel=json.loads(path.read_text()) if kernel is None else kernel
    certificate=json.loads((HERE/('certificate_'+bank+'.json')).read_text()) if certificate is None else certificate
    require(certificate['schema']=='operational-separated-bank-v1','certificate schema')
    require(certificate['kernel_sha256']==hashlib.sha256(path.read_bytes()).hexdigest(),'physical kernel identity')
    # The public consumer accepts only the exact on-disk kernel premise.
    require(same_json(kernel,json.loads(path.read_text())),'unbound kernel premise')
    require(type(certificate['bank_offsets']) is list and
            all(type(v) is int for v in certificate['bank_offsets']) and tuple(certificate['bank_offsets'])==BANK,'bank rows')
    require(type(certificate['target_offsets']) is list and
            all(type(v) is int for v in certificate['target_offsets']) and tuple(certificate['target_offsets'])==TARGETS,'targets')
    require(certificate['time_interval']==['1','2'],'time interval')
    require(certificate['unnormalized_source_floor']==str(sf) and
            certificate['unnormalized_pair_floor']==str(pf),'source or pair floor')
    require(certificate['center_singular_lower']=='999999/1000000','point contraction contract')
    require(certificate['operator_model_error_upper']=='1/1000000000','model error contract')
    require(certificate['normalization_lower']=='19/16' and certificate['normalization_upper']=='4/3','normalization')
    require(certificate['source_metrics']==['L2','declared_H1','natural_discrete_H1'] and
            certificate['H1_metric_upper']=='41','source metric contract')
    require(type(certificate['case_count']) is int and certificate['case_count']==231,'case count')
    coeff=interval_coefficients(kernel)
    cases={(j,) for j in TARGETS}|set(combinations(TARGETS,2))
    covers={case:[] for case in cases}
    require(type(certificate['cells']) is list and certificate['cells'],'empty cover')
    records=0;seen_cells=set()
    for cell in certificate['cells']:
        left,right=map(rational,(cell['lower'],cell['upper']))
        require(Q(1)<=left<right<=Q(2),'time cell range')
        require((left,right) not in seen_cells,'duplicate time cell');seen_cells.add((left,right))
        center=(left+right)/2;radius=(right-left)/2
        shifted=[[translated(row,center-Q(3,2)) for row in d] for d in coeff]
        powers=[radius**k for k in range(1,33)]
        require(type(cell['records']) is list and cell['records'],'empty cell record')
        local=set()
        for record in cell['records']:
            raw=record['case']
            require(type(raw) is list and all(type(v) is int for v in raw),'case must use integer labels')
            case=tuple(raw);require(case in cases and case not in local,'unknown or duplicate case');local.add(case)
            dimension=2*len(case);Rraw=record['preconditioner']
            require(type(Rraw) is list and len(Rraw)==dimension and all(type(row) is list and len(row)==dimension for row in Rraw),'preconditioner shape')
            R=[list(map(rational,row)) for row in Rraw]
            point=[];variation_squared=Q(0)
            for sensor in BANK:
                polys=[]
                for side,label in enumerate(case):
                    for port in (0,1):
                        polys.append([(-1)**side*v for v in shifted[abs(sensor-label)][port]])
                transformed=[[sum((polys[l][k]*R[l][column] for l in range(dimension)),Q())
                              for k in range(33)] for column in range(dimension)]
                point.append([p[0] for p in transformed])
                variation_squared+=sum((sum((abs(v)*h for v,h in zip(p[1:],powers)),Q())**2 for p in transformed),Q())
            gram=[[sum((p[i]*p[j] for p in point),Q()) for j in range(dimension)] for i in range(dimension)]
            defect=max(sum((abs(gram[i][j]-int(i==j)) for j in range(dimension)),Q()) for i in range(dimension))
            declared_defect=rational(record['point_defect_upper'])
            require(0<=defect<=declared_defect<1-CENTER_SINGULAR**2,'point Gram defect')
            e=rational(record['variation_frobenius_upper']);need=rational(record['required_transformed_norm_upper'])
            rnorm=sum((v*v for row in R for v in row),Q())
            floor=sf if dimension==2 else pf
            require(e>=0 and e*e>=variation_squared,'whole-cell variation')
            require(need>0 and need*need>=floor*rnorm,'unpreconditioned floor conversion')
            require(e+need<CENTER_SINGULAR,'strict singular floor')
            covers[case].append((left,right));records+=1
    for case,parts in covers.items():
        ordered=sorted(parts)
        require(ordered and ordered[0][0]==1 and ordered[-1][1]==2,'case does not cover endpoints')
        require(all(a[1]==b[0] for a,b in zip(ordered,ordered[1:])),'case cover gap or overlap')
    rho=model_error_check(len(BANK))
    mu=A0*A0*sf;pair=A0*A0*pf
    metrics={}
    for name in certificate['source_metrics']+(['L2_original_noise'] if bank=='8' else []):
        factor=1 if name.startswith('L2') else 41
        eta=(Q(3,10**7) if name=='L2_original_noise' else config['eta']) if factor==1 else Q(3,10**8)
        xi=Q(1,10**9) # Conditional additional computed-data error budget.
        delta=eta+rho+xi
        require(pair/factor>2*delta*delta,'pair tubes may intersect')
        accuracy=Q(13,10**4) if name=='L2_original_noise' else Q(1,1000)
        require(delta*delta<mu/factor*accuracy**2,'source error target')
        metrics[name]={'source_relative_accuracy_target':str(accuracy),'sensor_relative_radius':str(eta),'operator_relative_radius':str(rho),
                       'conditional_numerical_relative_radius':str(xi),'total_relative_radius':str(delta),
                       'individual_approximate_map_floor':str(mu/factor),'pair_approximate_map_floor':str(pair/factor),
                       'source_relative_error_squared_upper':str(delta*delta/(mu/factor))}
    return {'verified':True,'direct_rows':[v+500 for v in BANK],'channel_count':len(BANK),'target_indices':[490,510],
            'known_time_interval':['1','2'],'individual_cases':21,'pair_cases':210,
            'nonempty_time_cells':len(seen_cells),'whole_cell_records':records,'all_case_covers_verified':True,
            'physical_operator_model_error_upper':str(rho),'metrics':metrics,
            'premise':'full finite-x periodic Taylor enclosures require separate kernel.py replay'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--bank',choices=['8','9'],default='9');args=parser.parse_args()
    print(json.dumps(check(bank=args.bank),indent=2))
