"""Exact consequences of target-block locality, without matrix simulation."""
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]/'five_paths_2026_09/path5_resolution/certificate.json'


def placement_bound(depth,tmax=Q(2),rate=Q(56,5),ports=2,normalization_upper=Q(2)):
    if type(depth) is not int or depth<0 or tmax<0 or rate<=0 or ports<1 or normalization_upper**2<1+tmax:
        raise ValueError('invalid locality hypotheses')
    mu=rate*tmax;order=2*depth+1
    if order+1<=mu: raise ValueError('geometric tail ratio not below one')
    tail=mu**order/factorial(order)/(1-mu/(order+1))
    return 2*ports*normalization_upper*tail


def build():
    source=json.loads(BASE.read_text());floors={m:Q(v['floor_lower']) for m,v in source['uniform_bounds'].items()}
    for d in range(501):
        try:error=placement_bound(d)
        except ValueError:continue
        if all(error<f/100 for f in floors.values()):break
    else:raise ValueError('no nonempty certified placement interval')
    return {'schema':'resolution-placement-v1','baseline_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),
            'model':{'n':1001,'K':2,'g':'4/5','tau':['1','2'],'output_normalization':'sqrt(1+tau)'},
            'uniformization_rate':'56/5','depth':d,'target_indices':[d,1000-d],
            'target_coordinate_endpoints':[str(Q(2*d+1,2002)),str(Q(2001-2*d,2002))],
            'matrix_error_upper':str(error),'retained_fraction':'99/100',
            'metrics':{m:{'central_floor':str(f),'floor_lower':str(f-error),
                          'full_continuum_error_upper':str(Q(source['uniform_bounds'][m]['error_upper'])+error)} for m,f in floors.items()}}


if __name__=='__main__':
    p=HERE/'placement_certificate.json';d=build();p.write_text(json.dumps(d,indent=2)+'\n')
    print('depth',d['depth'],'targets',d['target_indices'],'placement error',float(Q(d['matrix_error_upper'])))
    for m,v in d['metrics'].items():print(m,'floor',float(Q(v['floor_lower'])))
