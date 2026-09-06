"""Exact unknown-target centroid certificate from first-moment locality."""
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent


def tail(mu,r):
    if r<0 or mu<0 or r+1<=mu:raise ValueError('invalid exponential-tail bound')
    return mu**r/factorial(r)/(1-mu/(r+1))


def build():
    path=HERE/'placement_certificate.json';base=json.loads(path.read_text())
    floor=Q(base['metrics']['L2']['floor_lower']);mu=Q(56,5);nu=Q(1,10000)
    perturbation=1000*(2*nu+nu*nu)/(1-nu)**2
    for depth in range(base['depth'],501):
        bias=8*mu*tail(mu,depth)/floor
        if bias+perturbation<Q(1,2):break
    else:raise ValueError('localization does not close')
    result={'schema':'unknown-target-centroid-v1','placement_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'model':base['model'],'single_graph_rate':'28/5','relative_output_noise':str(nu),
            'depth':depth,'target_indices':[depth,1000-depth],'centroid_bias_upper':str(bias),
            'noise_centroid_shift_upper':str(perturbation),'total_centroid_error_upper':str(bias+perturbation),
            'source_nonzero':True,'metrics':{}}
    for m,record in base['metrics'].items():
        c=Q(record['floor_lower']);eta=Q(3,10**8 if m=='L2' else 10**9)
        if not eta**2<nu**2*c:raise ValueError('source-relative noise does not imply output-relative noise')
        result['metrics'][m]={'floor_lower':str(c),'relative_source_noise':str(eta),'relative_source_error_squared_upper':str(eta**2/c)}
    return result


if __name__=='__main__':
    d=build();(HERE/'localization_certificate.json').write_text(json.dumps(d,indent=2)+'\n')
    print('targets',d['target_indices'],'centroid total',float(Q(d['total_centroid_error_upper'])))
