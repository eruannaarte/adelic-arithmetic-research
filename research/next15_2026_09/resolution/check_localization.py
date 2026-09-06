"""Separate exact verifier for centroid and recovered-source consequences."""
from fractions import Fraction as Q
from pathlib import Path
from math import factorial
import json,hashlib
from check_placement import check as check_placement
HERE=Path(__file__).resolve().parent


def check(d):
    path=HERE/'placement_certificate.json';base=json.loads(path.read_text());assert check_placement(base)
    assert d['schema']=='unknown-target-centroid-v1' and d['source_nonzero'] is True
    assert d['placement_sha256']==hashlib.sha256(path.read_bytes()).hexdigest() and d['model']==base['model']
    assert d['single_graph_rate']=='28/5'
    depth=d['depth'];assert type(depth) is int and base['depth']<=depth<=500
    assert d['target_indices']==[depth,1000-depth]
    mu=Q(56,5);nu=Q(d['relative_output_noise']);assert 0<=nu<1
    assert depth+1>mu
    beta=8*mu**(depth+1)/factorial(depth)/(1-mu/(depth+1))/Q(base['metrics']['L2']['floor_lower'])
    gamma=1000*(2*nu+nu**2)/(1-nu)**2
    assert Q(d['centroid_bias_upper'])==beta and Q(d['noise_centroid_shift_upper'])==gamma
    assert Q(d['total_centroid_error_upper'])==beta+gamma<Q(1,2)
    assert set(d['metrics'])==set(base['metrics'])
    for m,v in d['metrics'].items():
        floor=Q(base['metrics'][m]['floor_lower']);eta=Q(v['relative_source_noise'])
        assert Q(v['floor_lower'])==floor and eta>=0 and eta**2<nu**2*floor
        assert Q(v['relative_source_error_squared_upper'])==eta**2/floor<Q(1,10**8)
    return True


if __name__=='__main__':print('unknown-target certificate:',check(json.loads((HERE/'localization_certificate.json').read_text())))
