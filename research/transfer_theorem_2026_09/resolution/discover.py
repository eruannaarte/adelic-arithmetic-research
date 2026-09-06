"""Floating proposals only: periodic actual-x graph; no certification claims."""
import numpy as np
from itertools import combinations
from pathlib import Path
import json


def responses(t,n=1001,N=64,terms=100):
    x=(np.arange(n)+.5)/n;v=1+.8*x
    deg=np.full(n,2.);deg[[0,-1]]=1.
    diagonal=1-(deg[None,:]+2*v[None,:])/5.6
    state=np.zeros((N,n,2))
    state[0,:,0]=np.sqrt(2/n)*np.cos(np.pi*x)
    state[0,:,1]=np.sqrt(2/n)*np.cos(2*np.pi*x)
    coefficient=np.exp(-5.6*t);total=coefficient*state
    for k in range(1,terms+1):
        out=diagonal[:,:,None]*state
        out[:,1:]+=state[:,:-1]/5.6;out[:,:-1]+=state[:,1:]/5.6
        out+=(np.roll(state,1,axis=0)+np.roll(state,-1,axis=0))*v[None,:,None]/5.6
        state=out;coefficient*=5.6*t/k;total+=coefficient*state
    return (1+t)**.25*total.sum(axis=1)/np.sqrt(n)


def score(bank,kernels):
    low=1.;pairlow=1.;arg=None
    for t,K in kernels:
        maps={j:K[(np.array(bank)-j)%64] for j in range(-10,11)}
        low=min(low,min(np.linalg.eigvalsh(A.T@A)[0] for A in maps.values()))
        for j,k in combinations(maps,2):
            M=np.column_stack([maps[j],-maps[k]])
            v=np.linalg.eigvalsh(M.T@M)[0]
            if v<pairlow:pairlow=v;arg=(t,j,k)
    return {'rows':bank,'count':len(bank),'individual_floor':low,'pair_floor':pairlow,'limiting_pair':arg}


if __name__=='__main__':
    kernels=[(t,responses(t)) for t in np.linspace(1,2,5)]
    banks=[list(range(-15,16,2)),list(range(-14,15,2)),list(range(-15,16,3)),list(range(-16,17,4)),
           [-15,-12,-9,-6,-3,0,3,6,9,12,16],[-16,-12,-8,-4,0,4,8,12,17]]
    out={'status':'floating discovery; periodic approximation not yet charged',
         'proposals':[score(b,kernels) for b in banks]}
    (Path(__file__).resolve().parent/'discovery.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
