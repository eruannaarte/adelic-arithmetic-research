"""Independent exact consequence check; central certificate is a stated premise."""
import hashlib,json,importlib.util
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]/'five_paths_2026_09/path5_resolution/certificate.json'


def check(d):
    source=json.loads(BASE.read_text())
    spec=importlib.util.spec_from_file_location('_resolution_baseline_check',BASE.with_name('check_certificate.py'))
    verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
    verifier.check(source)
    assert list(map(Q,source['covered_interval']))==[Q(1),Q(2)]
    assert d['schema']=='resolution-placement-v1'
    assert d['baseline_sha256']==hashlib.sha256(BASE.read_bytes()).hexdigest()
    assert source['model']=={'n':1001,'K':2,'g':'4/5','target':'exact central cell','normalization':'sqrt(1+tau)','output_metric':'Euclidean modal energy'}
    assert d['model']=={'n':1001,'K':2,'g':'4/5','tau':['1','2'],'output_normalization':'sqrt(1+tau)'}
    assert d['uniformization_rate']=='56/5' and type(d['depth']) is int
    depth=d['depth'];assert 0<=depth<=500
    r=2*depth+1;mu=Q(112,5);assert r+1>mu
    error=Q(d['matrix_error_upper'])
    assert error==8*mu**r/factorial(r)/(1-mu/(r+1))
    assert d['target_indices']==[depth,1000-depth]
    assert list(map(Q,d['target_coordinate_endpoints']))==[Q(2*depth+1,2002),Q(2001-2*depth,2002)]
    assert d['retained_fraction']=='99/100' and set(d['metrics'])==set(source['uniform_bounds'])
    for name,record in d['metrics'].items():
        old=source['uniform_bounds'][name];floor=Q(old['floor_lower'])
        assert Q(record['central_floor'])==floor
        assert Q(record['floor_lower'])==floor-error>Q(99,100)*floor
        assert Q(record['full_continuum_error_upper'])==Q(old['error_upper'])+error
    return True


if __name__=='__main__':
    print('placement certificate:',check(json.loads((HERE/'placement_certificate.json').read_text())))
