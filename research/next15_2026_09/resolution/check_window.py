"""Independent rational retained-information and window-centroid checker."""
from fractions import Fraction as Q
from pathlib import Path
from math import factorial
import json,hashlib
from check_placement import check as check_placement
HERE=Path(__file__).resolve().parent


def check(d):
    path=HERE/'placement_certificate.json';base=json.loads(path.read_text());assert check_placement(base)
    assert d['schema']=='transverse-window-v1' and d['model']==base['model']
    assert d['placement_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
    assert d['nominal_target']==500 and d['target_indices']==[490,510] and d['global_depth']==490
    margin=d['guard_margin'];assert type(margin) is int and 0<=margin<=490
    assert d['window_indices']==[490-margin,510+margin]
    count=2*margin+21;assert d['channel_count']==count
    mu=Q(56,5);nu=Q(d['relative_output_noise']);assert 0<=nu<1
    def remainder(r):
        assert r+1>mu
        return mu**r/factorial(r)/(1-mu/(r+1))
    loss=2*remainder(margin+1)**2
    boundary=8*mu*remainder(490)
    discarded=2*mu*remainder(margin)*remainder(margin+1)
    assert Q(d['information_loss_upper'])==loss
    assert Q(d['boundary_first_moment_upper'])==boundary and Q(d['discarded_first_moment_upper'])==discarded
    kept=Q(base['metrics']['L2']['floor_lower'])-loss
    beta=(boundary+discarded)/kept;gamma=(count-1)*(2*nu+nu**2)/(1-nu)**2
    assert Q(d['centroid_bias_upper'])==beta and Q(d['noise_centroid_shift_upper'])==gamma
    assert Q(d['total_centroid_error_upper'])==beta+gamma<Q(1,2)
    assert set(d['metrics'])==set(base['metrics'])
    for m,v in d['metrics'].items():
        c=Q(base['metrics'][m]['floor_lower'])-loss;eta=Q(v['relative_source_noise'])
        assert Q(v['floor_lower'])==c>Q(99,100)*Q(base['metrics'][m]['central_floor'])
        assert eta>=0 and eta**2<nu**2*c
        assert Q(v['relative_source_error_squared_upper'])==eta**2/c<Q(1,10**6)
    return True


if __name__=='__main__':print('window certificate:',check(json.loads((HERE/'window_certificate.json').read_text())))
