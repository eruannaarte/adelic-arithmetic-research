"""Exact independent consumer for all seven one-row deletions of the previous seven-row bank.

No numerical search or singular-value routine is imported. Every rejection is
proved using a rational source pair and the complete physical operator error.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
from math import factorial,isqrt
import hashlib,json,argparse
HERE=Path(__file__).resolve().parent
KERNEL=HERE.parents[1]/'transfer_theorem_2026_09/resolution/kernel.json'
ETA=Q(3,10**8);RHO=Q(1,10**9);A1=Q(4,3)
SEVEN=(-10,-8,-4,0,4,8,10)

def require(test,message):
    if not test:raise ValueError(message)
def rational(value):
    require(type(value) is str,'rational fields must be strings');return Q(value)
def deletion_layouts():return set(combinations(SEVEN,6))
def layouts():return deletion_layouts()
def sqrt_bounds(x):
    require(x>=0,'negative radicand');scale=10**40;k=isqrt(x.numerator*scale*scale//x.denominator)
    return Q(k,scale),Q(k+1,scale)
def alpha_upper(tau):
    lo=Q(1);hi=Q(4,3)
    for _ in range(48):
        mid=(lo+hi)/2
        if mid**4>=1+tau:hi=mid
        else:lo=mid
    return hi

def exp_upper(x):
    require(0<=x<202,'exponential series range')
    return sum((x**k/factorial(k) for k in range(201)),Q())+x**201/factorial(201)/(1-x/202)
def physical_error():
    require(A1**4>3,'normalization upper')
    a=Q(8);image=exp_upper(Q(18,5)*(a+1/a-2))*(a**(-38)+a**(-90))/(1-a**(-64))
    require(image<Q(1,10**24),'complete periodic image bound')
    mu=Q(56,5);finite=2*mu**491/factorial(491)/(1-mu/492)
    require(finite<Q(1,10**500),'complete finite-boundary bound')
    entry=Q(1,2**33)+Q(1,10**24)+Q(1,10**500)+Q(2,10**30)
    require(A1*A1*12*entry*entry<RHO*RHO,'six-row physical operator error')
    return RHO

def coefficients():
    kernel=json.loads(KERNEL.read_text())
    require(kernel['schema']=='periodic-transverse-taylor-v1','kernel schema')
    require(kernel['model']=={'nx':1001,'period':64,'source_modes':[1,2],'g':'4/5','center':'3/2','order':32,'exponential_degree':80,'maximum_distance':26,'output':'unnormalized global-x average; multiply by (1+tau)^(1/4)'},'kernel model')
    require(kernel['coefficient_export_grid']=='1/1000000000000000000000000000000','coefficient grid')
    require(kernel['zero_mode']=='exactly zero by cosine-source mean' and kernel['parity']=='kernel(-d)=kernel(d)','kernel symmetry')
    data=kernel['coefficient_intervals'];require(type(data) is list and len(data)==27,'kernel extent')
    out=[]
    for d in data:
        require(type(d) is list and len(d)==2,'source dimension');out.append([])
        for row in d:
            require(type(row) is list and len(row)==33,'Taylor dimension');out[-1].append([])
            for box in row:
                require(type(box) is list and len(box)==2,'coefficient interval shape')
                lo,hi=map(rational,box);require(lo<=hi and hi-lo<=Q(1,10**30),'coefficient interval width')
                out[-1][-1].append((lo+hi)/2)
    return out

def value(c,t):
    z=Q(0)
    for a in reversed(c):z=z*(t-Q(3,2))+a
    return z

def verify_record(record,coeff):
    raw=record['bank_offsets']
    require(type(raw) is list and all(type(v) is int for v in raw),'bank integer labels')
    bank=tuple(raw);require(bank in layouts(),'bank outside declared classes')
    tau=rational(record['time']);require(1<=tau<=2,'time outside acquisition interval')
    labels=record['target_offsets'];require(type(labels) is list and len(labels)==2 and all(type(v) is int and -10<=v<=10 for v in labels) and labels[0]<labels[1],'target pair')
    v=list(map(rational,record['source_pair']));require(len(v)==4,'source dimension')
    ulo,uhi=sqrt_bounds(sum((x*x for x in v[:2]),Q()));vlo,vhi=sqrt_bounds(sum((x*x for x in v[2:]),Q()))
    require(ulo>0 and vlo>0,'nonzero source pair')
    responses=[]
    for row in bank:
        responses.append(sum(((-1)**side*value(coeff[abs(row-j)][port],tau)*v[2*side+port] for side,j in enumerate(labels) for port in (0,1)),Q()))
    _,approx=sqrt_bounds(sum((r*r for r in responses),Q()))
    upper=alpha_upper(tau)*approx+RHO*(uhi+vhi)
    lower=ulo+vlo
    require(upper<ETA*lower,'physical noise balls not proved to overlap')
    radius=upper/lower
    return {'bank_offsets':list(bank),'time':str(tau),'target_offsets':labels,'collision_radius_upper':str(radius)}

def verify(document=None):
    doc=json.loads((HERE/'obstructions.json').read_text()) if document is None else document
    require(doc['schema']=='seven-deletion-six-row-obstructions-v1','obstruction schema')
    require(doc['kernel_sha256']==hashlib.sha256(KERNEL.read_bytes()).hexdigest(),'kernel identity')
    require(doc['sensor_relative_radius']==str(ETA),'fixed noise radius')
    require(doc['scope']=={'deletion_parent':list(SEVEN),'time_interval':['1','2'],'target_offsets':[-10,10],'metric':'L2'},'scope changed')
    records=doc['witnesses'];require(type(records) is list,'witness list')
    seen=set();results=[];coeff=coefficients();physical_error()
    for rec in records:
        result=verify_record(rec,coeff);bank=tuple(result['bank_offsets'])
        require(bank not in seen,'duplicate bank witness');seen.add(bank);results.append(result)
    require(seen==layouts(),'incomplete or excessive layout coverage')
    maximum=max(results,key=lambda r:Q(r['collision_radius_upper']))
    return {'verified':True,'deletion_layouts':len(deletion_layouts()),'distinct_layouts':len(seen),
            'maximum_collision_radius_upper':maximum['collision_radius_upper'],'maximum_case':maximum,
            'sensor_relative_radius':str(ETA),'all_deletion_layouts_physically_ambiguous':True,
            'consequence':'No decoder identifies every target for every nonzero source at eta=3e-8 on any of the seven one-row deletions.',
            'scope_limitation':'Other six-row layouts are not covered; the separate redesigned bank has a positive certificate.',
            'kernel_premise':'Rerun the preserved 256-bit finite-x kernel reconstruction to discharge its coefficient enclosures.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    result=verify()
    if args.write:(HERE/'checked.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
