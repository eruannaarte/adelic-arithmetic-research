"""Uncertified direct finite graph regression; never a proof input."""
from pathlib import Path
import json
import numpy as np


def response(n,target,source,tau=2.,terms=90):
    x=(np.arange(n)+.5)/n
    v=1+.8*x;degree=np.full(n,2.);degree[[0,-1]]=1.
    rate=5.6;mu=rate*tau
    diagonal=1-(degree[None,:]+degree[:,None]*v[None,:])/rate
    state=np.zeros((n,n));state[target]=sum(c*np.sqrt(2/n)*np.cos((k+1)*np.pi*x) for k,c in enumerate(source))
    coefficient=np.exp(-mu);total=coefficient*state
    for k in range(1,terms+1):
        out=diagonal*state
        out[:,1:]+=state[:,:-1]/rate;out[:,:-1]+=state[:,1:]/rate
        out[1:]+=state[:-1]*v/rate;out[:-1]+=state[1:]*v/rate
        state=out;coefficient*=mu/k;total+=coefficient*state
    return (1+tau)**.25*total.sum(axis=1)/np.sqrt(n)


if __name__=='__main__':
    n=1001;target=47;source=np.array([.6,.8])
    F=np.column_stack([response(n,target,[1.,0.]),response(n,target,[0.,1.])])
    y=F@source;noise=np.zeros(n);noise[-1]=3e-8;z=y+noise
    centroid=float(np.arange(n)@abs(z)**2/(z@z));estimate=np.linalg.lstsq(F,z,rcond=None)[0]
    d={'status':'floating direct-model regression, not certified data','n':n,'target':target,'source':source.tolist(),'tau':2,
       'output_energy':float(y@y),'source_noise_norm':float(np.linalg.norm(noise)),
       'centroid':centroid,'rounded_target':round(centroid),'source_error':float(np.linalg.norm(estimate-source)),
       'matrix_minimum_eigenvalue':float(np.linalg.eigvalsh(F.T@F)[0])}
    assert d['rounded_target']==target and d['source_error']<1e-4
    (Path(__file__).resolve().parent/'localization_example.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
