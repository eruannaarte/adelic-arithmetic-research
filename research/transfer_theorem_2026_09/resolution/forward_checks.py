"""Direct million-state finite-grid diagnostics; never a proof input."""
from fractions import Fraction as Q
from pathlib import Path
import argparse,json,math
import numpy as np
from decoder import CertifiedBank


def actual_response(target,source,tau,n=1001,terms=100):
    # Both directions are finite reflecting paths; no periodic surrogate here.
    x=(np.arange(n)+.5)/n;v=1+.8*x
    degree=np.full(n,2.);degree[[0,-1]]=1.
    diagonal=1-(degree[None,:]+degree[:,None]*v[None,:])/5.6
    state=np.zeros((n,n))
    state[target]=sum(c*np.sqrt(2/n)*np.cos((k+1)*np.pi*x) for k,c in enumerate(source))
    coefficient=np.exp(-5.6*tau);total=coefficient*state
    for k in range(1,terms+1):
        out=diagonal*state
        out[:,1:]+=state[:,:-1]/5.6;out[:,:-1]+=state[:,1:]/5.6
        out[1:]+=state[:-1]*v/5.6;out[:-1]+=state[1:]*v/5.6
        state=out;coefficient*=5.6*tau/k;total+=coefficient*state
    return (1+tau)**.25*total.sum(axis=1)/np.sqrt(n)


def run(write=False):
    bank=CertifiedBank();rows=bank.summary['direct_rows'];records=[]
    for tau in (Q(1),Q(3,2),Q(2)):
        matrices=bank.matrices(tau)
        for target in (490,500,510):
            u=(Q(3,5),Q(4,5)) if target!=500 else (Q(-4,5),Q(3,5))
            actual=actual_response(target,list(map(float,u)),float(tau))[rows]
            alpha=(1+float(tau))**.25
            P=matrices[target]
            predicted=alpha*np.array([float(sum((a*b for a,b in zip(row,u)),Q())) for row in P])
            discrepancy=float(np.linalg.norm(actual-predicted))
            assert discrepancy<1e-9
            for metric in ('L2','declared_H1','natural_discrete_H1'):
                eta=3e-7 if metric=='L2' else 3e-8
                observed=actual.copy();observed[4]+=eta
                z=[format(v/alpha,'.17g') for v in observed]
                r=bank.decode(z,tau,metric,numerical_relative_radius='1/1000000000')
                assert r.status=='unique' and r.feasible_targets==(target,)
                err=np.array([float(a-b) for a,b in zip(r.estimate,u)])
                if metric=='L2':S=np.ones(2)
                elif metric=='declared_H1':S=1+(np.pi*np.array([1,2]))**2
                else:S=1+4*1001**2*np.sin(np.pi*np.array([1,2])/(2*1001))**2
                relative_error=float(np.sqrt(np.sum(S*err*err)/np.sum(S*np.array(list(map(float,u)))**2)))
                assert relative_error<1e-3
                records.append({'tau':str(tau),'target':target,'metric':metric,
                     'source':[str(v) for v in u],'physical_model_discrepancy':discrepancy,
                     'added_physical_noise_norm':eta,'recovered_target':r.feasible_targets[0],
                     'relative_source_error':relative_error})
    result={'status':'floating full finite-grid regression, not proof evidence or a certified rounding budget',
            'state_dimension':1002001,'cases':records,'count':len(records),
            'maximum_physical_model_discrepancy':max(r['physical_model_discrepancy'] for r in records),
            'maximum_relative_source_error':max(r['relative_source_error'] for r in records)}
    if write:
        (Path(__file__).resolve().parent/'forward_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    run(write=parser.parse_args().write)
