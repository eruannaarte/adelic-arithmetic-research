"""Bounded floating seven-row search. None of its scores are certificates."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import json, time
import numpy as np
from scipy.optimize import minimize_scalar

HERE=Path(__file__).resolve().parent
PRIOR=HERE.parents[1]/'transfer_theorem_2026_09/resolution'
PAIRS=np.array(list(combinations(range(21),2)))
K=json.loads((PRIOR/'kernel.json').read_text())
C=np.array([[[float((Q(a)+Q(b))/2) for a,b in p] for p in d] for d in K['coefficient_intervals']]).transpose(2,0,1)

def values(ts):return np.array([np.polynomial.polynomial.polyval(t-1.5,C) for t in ts])
def matrices(bank,v):return v[:,np.abs(np.array(bank)[None,:]-np.arange(-10,11)[:,None]),:]
def evaluate(bank,v):
    maps=matrices(bank,v)
    sf=np.linalg.eigvalsh(np.einsum('tjmq,tjmr->tjqr',maps,maps))[...,0]
    blocks=np.concatenate((maps[:,PAIRS[:,0]],-maps[:,PAIRS[:,1]]),axis=3)
    # Singular values avoid squared-condition-number cancellation.
    pf=np.linalg.svd(blocks,compute_uv=False)[...,-1]**2
    return sf,pf
def scan(bank,ts,v):
    sf,pf=evaluate(bank,v)
    ix=np.unravel_index(np.argmin(pf),pf.shape)
    return {'bank':list(map(int,bank)),'source':float(sf.min()),'pair':float(pf.min()),
            'time':float(ts[ix[0]]),'labels':list(map(int,PAIRS[ix[1]]-10))}

def refine(bank):
    ts=np.linspace(1,2,129);v=values(ts);sf,pf=evaluate(bank,v)
    best=scan(bank,ts,v)
    def pair_floor(t,j,k):
        vv=np.polynomial.polynomial.polyval(t-1.5,C)
        B=np.concatenate((vv[np.abs(np.array(bank)-j)],-vv[np.abs(np.array(bank)-k)]),axis=1)
        return np.linalg.svd(B,compute_uv=False)[-1]**2
    count=0
    for p,(j,k) in enumerate(PAIRS-10):
        for i in range(1,len(ts)-1):
            if pf[i,p]<=pf[i-1,p] and pf[i,p]<=pf[i+1,p]:
                r=minimize_scalar(lambda t:pair_floor(t,j,k),bounds=(ts[i-1],ts[i+1]),method='bounded',options={'xatol':1e-13})
                count+=1
                if r.fun<best['pair']:best.update(pair=float(r.fun),time=float(r.x),labels=[int(j),int(k)])
    best['local_time_minimizations']=count
    return best

def main():
    start=time.monotonic();rng=np.random.default_rng(20260905)
    ts=np.linspace(1,2,17);v=values(ts);seen={}
    def record(bank):
        bank=tuple(sorted(bank))
        if len(set(bank))!=7 or bank[0]<-16 or bank[-1]>16 or min(np.diff(bank))<2:return None
        if bank not in seen:seen[bank]=scan(bank,ts,v)
        z=seen[bank]
        return min(z['source']/1e-8,z['pair']/1e-12)
    seeds=[(-15,-10,-5,0,5,10,16),(-14,-10,-6,0,6,10,14),(-14,-10,-6,-2,2,6,10),(-12,-10,-6,-2,2,6,10),(-12,-8,-4,0,4,8,12)]
    for b in seeds:record(b)
    for _ in range(450):
        # Every sample is separated by transforming seven distinct integers.
        b=np.sort(rng.choice(np.arange(-16,11),7,replace=False))+np.arange(7)
        record(b)
    for outer in range(4):
        ranked=sorted(seen,key=lambda b:record(b),reverse=True)[:12]
        for b in ranked:
            for i in range(7):
                for step in (-2,-1,1,2):record(b[:i]+(b[i]+step,)+b[i+1:])
        print('round',outer,'searched',len(seen),'best',seen[max(seen,key=record)],'seconds',round(time.monotonic()-start,1),flush=True)
    top=sorted(seen,key=record,reverse=True)[:30]
    refined=[]
    for b in top:
        z=refine(b);refined.append(z);print('refined',z,flush=True)
    doc={'status':'floating discovery only; not a full-time certificate','fixed_contract':{'rows':7,'minimum_gap':2,'offset_range':[-16,16],'eta':'1e-7','rho':'1e-9','xi':'1e-9','accuracy':'0.001'},'seed':20260905,'coarse_times':list(map(float,ts)), 'candidate_count':len(seen),'best_refined':sorted(refined,key=lambda z:min(z['source']/1e-8,z['pair']/1e-12),reverse=True), 'coarse_top':[seen[b] for b in top]}
    (HERE/'discovery.json').write_text(json.dumps(doc,indent=2)+'\n')
if __name__=='__main__':main()
