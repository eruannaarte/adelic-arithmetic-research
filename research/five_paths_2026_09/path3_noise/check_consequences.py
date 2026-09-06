"""Standard-library checker of noise consequences from supplied bias/Gram bounds.

This does not validate the tail/Gram inputs; full dependency replay is separate.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse,json


def exp_negative_upper(x):
    if x<0:raise ValueError('negative exponent magnitude')
    # e>2, so x>=512 gives e^-x<2^-512; the remaining finite instance
    # uses an exact lower Taylor sum for exp at a downward dyadic x.
    if x>=512:return Q(1,2**512)
    den=2**256;lo=Q((x*den).numerator//(x*den).denominator,den)
    term=Q(1);total=Q(1)
    for k in range(1,257):term*=lo/k;total+=term
    return 1/total


def check(c):
    assert c['schema']=='five-paths-arithmetic-noise-v1' and c['measurement_count']==8900
    assert c['times']=='t_j=(2j+1-8900)/10, j=0,...,8899'
    ds=c['designs'];stats=c['weight_statistics']
    for name,d in ds.items():
        bias=list(map(Q,d['bias_upper']));qr=list(map(Q,d['qrows']));q=max(qr)
        assert len(bias)==len(qr)==50 and min(bias)>=0 and min(qr)>=0 and q<1
        lo,hi=map(Q,stats[name]['sum_squared_weights']);assert 0<lo<=hi
        var=[]
        for n,qi in enumerate(qr,1):
            delta=qi/(1-q);assert delta<1
            var.append([n**4*lo*(1-delta)**2,n**4*hi*(1+delta)**2])
        assert var==[[Q(a),Q(b)] for a,b in d['variance_intervals']]
        margin=[Q(1,2)-b for b in bias]
        eta2=min(m*m*(1-q)/n**4 for n,m in enumerate(margin,1)) if min(margin)>0 else Q(0)
        assert eta2==Q(d['weighted_noise_radius_squared_sufficient'])
        assert (Q(d['declared_weighted_noise_radius'])**2<eta2)==d['declared_radius_certified']
        if min(margin)>0:
            sigma=Q(d['iid_circular_complex_sigma']);assert sigma>0
            union=sum((exp_negative_upper(m*m/(sigma*sigma*v[1])) for m,v in zip(margin,var)),Q(0))
            assert union<=Q(d['gaussian_union_failure_upper'])<Q(55,10**15)
        else:assert Q(d['gaussian_union_failure_upper'])==1 and not d['bias_certificate_alone_succeeds']
    a=Q(ds['multi']['variance_intervals'][49][0]);b=Q(ds['single']['variance_intervals'][49][1])
    assert a/b==Q(c['variance50_inflation_ratio_lower'])>1
    return True

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('certificate',nargs='?',default=str(Path(__file__).with_name('certificate.json')))
    a=p.parse_args();check(json.loads(Path(a.certificate).read_text()));print('PASS: exact bias-margin, Neumann variance, bounded noise, rational Gaussian tail, and inflation consequences')
