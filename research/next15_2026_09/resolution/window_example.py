"""Full-model numerical control of the new restricted sensing operator."""
from pathlib import Path
import json
import numpy as np
from simulate import response

if __name__=='__main__':
    n=1001;j=510;u=np.array([.6,.8]);indices=np.arange(451,550)
    F=np.column_stack([response(n,j,[1.,0.]),response(n,j,[0.,1.])]);small=F[indices]
    outside=np.setdiff1d(np.arange(n),indices);lost=F[outside].T@F[outside]
    U,_,_=np.linalg.svd(small,full_matrices=False)
    noise=3e-7*U[:,-1];y=small@u;z=y+noise
    centroid=float(indices@abs(z)**2/(z@z));estimate=np.linalg.lstsq(small,z,rcond=None)[0]
    d={'status':'floating direct-model control, not certificate input','target':j,'source':u.tolist(),'tau':2,
       'channel_count':len(indices),'discarded_information_norm':float(np.linalg.norm(lost,2)),
       'retained_minimum_eigenvalue':float(np.linalg.eigvalsh(small.T@small)[0]),
       'sensor_noise_norm':float(np.linalg.norm(noise)),'centroid':centroid,'rounded_target':round(centroid),
       'source_error':float(np.linalg.norm(estimate-u))}
    assert round(centroid)==j and d['source_error']<.001
    (Path(__file__).resolve().parent/'window_example.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
