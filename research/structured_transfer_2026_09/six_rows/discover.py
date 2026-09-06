"""Floating discovery only: fixed six-row noise/accuracy contract."""
from pathlib import Path
from itertools import combinations
import importlib.util,json,time
import numpy as np
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_six_search_base',HERE.parents[1]/'refined_transfer_2026_09/resolution/discover.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)

SF=(3.2e-8/(19/16)/.001)**2
PF=2*(3.2e-8/(19/16))**2

def score(z): return min(z['source']/SF,z['pair']/PF)

def main():
    started=time.monotonic();rng=np.random.default_rng(2609056)
    ts=np.linspace(1,2,17);v=base.values(ts);seen={}
    def record(bank):
        bank=tuple(sorted(bank))
        if len(set(bank))!=6 or bank[0]<-16 or bank[-1]>16 or min(np.diff(bank))<2:return None
        if bank not in seen: seen[bank]=base.scan(bank,ts,v)
        return score(seen[bank])
    seven=(-10,-8,-4,0,4,8,10)
    for bank in combinations(seven,6):record(bank)
    seeds=[(-10,-6,-2,2,6,10),(-12,-8,-4,0,4,8),(-12,-8,-4,4,8,12),(-10,-8,-4,4,8,10)]
    for bank in seeds:record(bank)
    for _ in range(600):
        bank=np.sort(rng.choice(np.arange(-16,12),6,replace=False))+np.arange(6)
        record(bank)
    for outer in range(5):
        ranked=sorted(seen,key=lambda b:record(b),reverse=True)[:20]
        for bank in ranked:
            for i in range(6):
                for step in (-2,-1,1,2):record(bank[:i]+(bank[i]+step,)+bank[i+1:])
        b=max(seen,key=record)
        print('round',outer,'searched',len(seen),'best',seen[b],'score',record(b),'elapsed',time.monotonic()-started,flush=True)
    top=sorted(seen,key=record,reverse=True)[:50]
    refined=[]
    for bank in top:
        z=base.refine(bank);refined.append(z)
        print('refined',z,'score',score(z),flush=True)
    doc={'schema':'fixed-contract-six-row-floating-discovery-v1','status':'floating numerical screening, no guarantee',
         'contract':{'eta':'3/100000000','rho':'1/1000000000','xi':'1/1000000000','accuracy':'1/1000','gap':2,'range':[-16,16]},
         'seed':2609056,'coarse_time_count':len(ts),'searched':len(seen),'coarse_top':[seen[b] for b in top],
         'refined':sorted(refined,key=score,reverse=True),'deletions':[seen[tuple(b)] for b in combinations(seven,6)],
         'elapsed_seconds':time.monotonic()-started}
    (HERE/'discovery.json').write_text(json.dumps(doc,indent=2)+'\n')
if __name__=='__main__':main()
