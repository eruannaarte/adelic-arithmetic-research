"""Floating full n=1001 graph replay and blind-label decoder control.

Every model response is reconstructed from the finite graph stencil. These
regressions are diagnostics, not certificate premises or sampled-time proofs.
"""
from pathlib import Path
from functools import lru_cache
from fractions import Fraction as Q
import argparse, importlib.util, json
import numpy as np
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]/'next15_2026_09'/'resolution'
spec=importlib.util.spec_from_file_location('inherited_full_graph_stencil',BASE/'simulate.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

@lru_cache(maxsize=4)
def forward(target,tau):
    return np.column_stack([mod.response(1001,target,[1.,0.],tau),mod.response(1001,target,[0.,1.],tau)])

def decode(z,indices,tau):
    """No true-target argument: identify its label before selecting the inverse."""
    centroid=float(indices@(z*z)/(z@z));label=round(centroid)
    if label not in range(490,511):raise ValueError('decoded label outside prior')
    estimate=np.linalg.lstsq(forward(label,tau)[indices],z,rcond=None)[0]
    return label,centroid,estimate

def run():
    cert=json.loads((HERE/'evidence.json').read_text());examples=[]
    for target in [490,510]:
        for tau in [1.,2.]:
            F=forward(target,tau)
            for bank in cert['banks']:
                indices=np.array(bank['indices']);A=F[indices];left,_,_=np.linalg.svd(A,full_matrices=False)
                worst=left[:,-1];errmax=0.;centmax=0.
                for angle in np.linspace(0,2*np.pi,9)[:-1]:
                    u=np.array([np.cos(angle),np.sin(angle)]);y=A@u
                    for kind in ['least-information','left-edge','right-edge']:
                        noise=3e-7*worst
                        if kind!='least-information':
                            noise=np.zeros(len(indices));noise[0 if kind=='left-edge' else -1]=3e-7
                        label,c,estimate=decode(y+noise,indices,tau)
                        assert label==target
                        err=float(np.linalg.norm(estimate-u));shift=abs(c-target)
                        assert err**2<=float(Q(bank['metrics']['L2']['relative_source_error_squared_upper']))
                        assert shift<float(Q(bank['total_centroid_error_upper']))
                        errmax=max(errmax,err);centmax=max(centmax,shift)
                missing=np.setdiff1d(np.arange(1001),indices)
                examples.append({'target':target,'tau':tau,'channel_count':len(indices),
                    'cases':24,'source_error_max':errmax,'centroid_error_max':centmax,
                    'actual_Gram_loss_norm':float(np.linalg.norm(F[missing].T@F[missing],2)),
                    'actual_retained_floor_L2':float(np.linalg.eigvalsh(A.T@A)[0])})
    return {'status':'floating full-model diagnostic; not an interval certificate',
            'model_n':1001,'model_state_dimension':1002001,'full_stencil_terms':90,
            'cases':sum(v['cases'] for v in examples),'examples':examples}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    data=run()
    if args.write:(HERE/'example.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))
