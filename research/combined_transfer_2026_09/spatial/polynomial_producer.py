"""Exact polynomial proposal: principal-minor positivity avoids source-coordinate rotation losses."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations,permutations
import hashlib,json,time
import numpy as np
from flint import fmpq,fmpq_poly
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent
BANK=(-15,-7,-1,1,7,15);TARGETS=tuple(range(-10,11));SOURCE_FLOOR=Q(1,10**9)
LABEL_RADIUS=Q(325,10**10)
BUDGET=LABEL_RADIUS/Q(19,16)
PRIOR=HERE.parents[1]/'transfer_theorem_2026_09/resolution'
K=json.loads((PRIOR/'kernel.json').read_text())
C=np.asarray([[[float((Q(a)+Q(b))/2) for a,b in row] for row in distance] for distance in K['coefficient_intervals']])
C=C.transpose(2,0,1)
base=SimpleNamespace(K=K,C=C,PRIOR=PRIOR)

def fq(q):q=Q(q);return fmpq(q.numerator,q.denominator)
def gram_columns(case):
    kernel=base.K['coefficient_intervals']
    rows=[[fmpq_poly([fq((-1)**side*(Q(a)+Q(b))/2) for a,b in kernel[abs(sensor-j)][port]])
           for side,j in enumerate(case) for port in range(2)] for sensor in BANK]
    n=2*len(case)
    return [[sum((row[i]*row[j] for row in rows),fmpq_poly()) for j in range(n)] for i in range(n)]
def determinant(M):
    n=len(M);answer=fmpq_poly()
    for permutation in permutations(range(n)):
        negative=sum(permutation[i]>permutation[j] for i in range(n) for j in range(i+1,n))%2
        term=fmpq_poly([(-1)**negative])
        for i,j in enumerate(permutation):term*=M[i][j]
        answer+=term
    return answer

def build_case(case):
    G=gram_columns(case);records=[]
    def visit(left,right,depth=0):
        center=(left+right)/2;h=(right-left)/2
        if len(case)==1:split=None;threshold=[SOURCE_FLOOR]*2
        else:
            vv=np.polynomial.polynomial.polyval(float(center)-1.5,base.C)
            M=np.concatenate((vv[np.abs(np.array(BANK)-case[0])],-vv[np.abs(np.array(BANK)-case[1])]),axis=1)
            _,s,Vh=np.linalg.svd(M,full_matrices=False);R=Vh.T/s
            top=np.sum(R[:2]**2);bottom=np.sum(R[2:]**2)
            split=Q(format(np.sqrt(top)/(np.sqrt(top)+np.sqrt(bottom)),'.9f'))
            threshold=[BUDGET**2/split]*2+[BUDGET**2/(1-split)]*2
        H=[[p-fmpq_poly([fq(threshold[i])]) if i==j else p for j,p in enumerate(row)] for i,row in enumerate(G)]
        lower=[]
        for k in range(1,len(H)+1):
            minor=determinant([row[:k] for row in H[:k]])
            shifted=minor(fmpq_poly([fq(center-Q(3,2)),1]))
            coeff=list(shifted);power=fmpq(1);variation=fmpq(0)
            for c in coeff[1:]:power*=fq(h);variation+=abs(c)*power
            lower.append(coeff[0]-variation)
        if min(lower)>0:
            records.append({'case':list(case),'lower':str(left),'upper':str(right),'source_split_weight':None if split is None else str(split),
                            'principal_minor_lower_bounds':[str(v) for v in lower]})
        elif depth<14:
            visit(left,center,depth+1);visit(center,right,depth+1)
        else:raise ValueError(('whole-interval positivity failed',case,str(left),str(right)))
    visit(Q(1),Q(2));return records

def main():
    started=time.monotonic();records=[];cases=[(j,) for j in TARGETS]+list(combinations(TARGETS,2))
    for i,case in enumerate(cases):
        records+=build_case(case)
        if i%10==0:print('case',i+1,'records',len(records),'elapsed',round(time.monotonic()-started,2),flush=True)
    doc={'schema':'polynomial-weighted-pair-combined-six-row-v1','kernel_sha256':hashlib.sha256(base.PRIOR.joinpath('kernel.json').read_bytes()).hexdigest(),
         'bank_offsets':list(BANK),'target_offsets':list(TARGETS),'time_interval':['1','2'],'unnormalized_source_floor':str(SOURCE_FLOOR),
         'sensor_relative_radius':'3/100000000','operator_relative_radius':'1/1000000000','numerical_relative_radius':'1/1000000000',
         'normalization_lower':'19/16','normalization_upper':'4/3','source_relative_accuracy_target':'1/1000','metric':'L2','label_tube_radius':str(LABEL_RADIUS),'clock_radius':'1/100000000','potential_radius':'1/100000000','records':records}
    (HERE/'certificate_6.json').write_text(json.dumps(doc,indent=2)+'\n')
    print('PRODUCED',len(records),'records in',time.monotonic()-started,flush=True)
if __name__=='__main__':main()
