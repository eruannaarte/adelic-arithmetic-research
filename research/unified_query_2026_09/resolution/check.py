"""Independent standard-library checker for source-bound bank certificates."""
from fractions import Fraction as Q
from pathlib import Path
from math import factorial
import hashlib, importlib.util, json, sys
sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]/'next15_2026_09'/'resolution'

def checked_base():
    sys.path.insert(0,str(BASE))
    spec=importlib.util.spec_from_file_location('prior_bank_placement_checker',BASE/'check_placement.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    path=BASE/'placement_certificate.json';base=json.loads(path.read_text())
    assert module.check(base)
    return path,base

def check(d):
    path,base=checked_base()
    assert d['schema']=='asymmetric-bank-v1' and d['model']==base['model']
    assert d['placement_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
    assert d['target_indices']==[490,510]
    assert d['source_metric_lower']=={'L2':'1','declared_H1':'9','natural_discrete_H1':'9'}
    assert d['joint_exact_recovery_necessary_channels']==4
    # pi>3, sin(x)>=x-x^3/6, and monotonicity on [0,pi/2].
    n=1001
    assert 1+9*(1-Q(3,8*n*n))**2>9
    mu=Q(56,5)
    boundary=8*mu*mu**490/factorial(490)/(1-mu/491)
    assert boundary<=Q(d['boundary_moment_upper'])<=Q(1,10**300)
    assert len(d['banks'])==2
    for b,(lo,hi,retained) in zip(d['banks'],[(476,525,Q(99,100)),(477,524,Q(97,100))]):
        assert b['indices']==list(range(lo,hi+1)) and b['channel_count']==hi-lo+1
        assert lo+hi!=1000  # deliberately asymmetric about the prior centre
        a=Q(b['weight_ratio']);assert a>1
        x=Q(36,5)*(a+1/a-2);assert Q(b['exponent'])==x
        # Independent upper series at degree 180, different from the producer.
        terms=[x**k/factorial(k) for k in range(181)]
        assert x<182
        upper=sum(terms)+x**181/factorial(181)/(1-x/182)
        E=Q(b['exponential_upper']);assert E>=upper and E-upper<Q(1,10**30)
        bounds=[];moments=[]
        for j in range(490,511):
            r=(j-lo+1,hi-j+1)
            assert all(v>=1 and a*a>=Q(v+1,v) for v in r)
            bounds.append(2*E*sum(a**(-2*v) for v in r))
            moments.append(2*E*sum(v*a**(-2*v) for v in r))
        loss=Q(b['energy_loss_L2_upper']);moment=Q(b['discarded_moment_L2_upper'])
        assert max(bounds)<=loss<max(bounds)+Q(1,10**30)
        assert max(moments)<=moment<max(moments)+Q(1,10**30)
        assert Q(b['retained_central_fraction'])==retained
        nu=Q(b['relative_output_noise']);assert nu==Q(1,1000)
        kept=Q(base['metrics']['L2']['floor_lower'])-loss
        beta=Q(b['centroid_bias_upper'])
        assert (Q(d['boundary_moment_upper'])+moment)/kept<=beta
        gamma=(hi-lo)*(2*nu+nu**2)/(1-nu)**2
        assert Q(b['noise_centroid_shift_upper'])==gamma
        assert beta+gamma<=Q(b['total_centroid_error_upper'])<Q(1,2)
        assert set(b['metrics'])==set(base['metrics'])
        for m,v in b['metrics'].items():
            c=Q(base['metrics'][m]['floor_lower'])-loss/Q(d['source_metric_lower'][m])
            assert Q(v['floor_lower'])==c>retained*Q(base['metrics'][m]['central_floor'])
            eta=Q(v['relative_source_noise']);assert eta==Q(3,10**7 if m=='L2' else 10**8)
            assert eta**2<nu**2*c
            assert eta**2/c<=Q(v['relative_source_error_squared_upper'])<Q(1,10**6)
    return True

if __name__=='__main__':
    assert check(json.loads((HERE/'evidence.json').read_text()))
    print('Smaller asymmetric banks: exact certificate passed.')
