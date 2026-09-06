"""Independent exact nuisance witnesses and complete signal-derivative audit.

No current producer or consumer is imported. The derivative audit uses ten
 times the producer's summation cutoff and fresh positive integral tails.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import comb, factorial
import hashlib, json
from flint import arb, ctx, fmpq
HERE=Path(__file__).resolve().parent


def ball(x):
    x=Q(x);return arb(fmpq(x.numerator,x.denominator))


def endpoint(x):
    assert x.is_exact() and x.is_finite()
    m,e=map(int,x.man_exp())
    return Q(m*2**e) if e>=0 else Q(m,2**(-e))


def run():
    path=HERE.parent/'noise/approximation.json';doc=json.loads(path.read_text())
    c=doc['clock_and_derivative']
    assert doc['measurement_count']==8900
    assert doc['tested_degrees']==[6,8,10,12]
    witnesses=[]
    h=Q(1,10**12);amplitude=Q(10**20)
    for p in doc['tested_degrees']:
        m=p+2;x=list(map(Q,range(m)))
        functional=[Q((-1)**(p+1-j)*comb(p+1,j)) for j in range(m)]
        moments=[sum((a*t**k for a,t in zip(functional,x)),Q()) for k in range(p+2)]
        assert moments==[Q(0)]*(p+1)+[Q(factorial(p+1))]
        actual=x[:];actual[0]+=h
        leakage=sum((a*amplitude*t for a,t in zip(functional,actual)),Q())
        assert leakage==(-1)**(p+1)*amplitude*h
        # Uniform W has diagonal1/m; dual norm²=m*Σ functional_j².
        dual2=m*sum((a*a for a in functional),Q())
        assert dual2==m*comb(2*p+2,p+1)
        assert 8900>p*p
        witnesses.append({'degree':p,'nominal_times':list(map(str,x)),
                          'annihilator':list(map(str,functional)),
                          'exact_moments_through_degree_p_plus_1':list(map(str,moments)),
                          'one_reading_jitter':str(h),'linear_nuisance_amplitude':str(amplitude),
                          'absolute_quotient_functional_leakage':str(abs(leakage)),
                          'uniform_weight_dual_norm_squared':str(dual2),
                          'quotient_norm_squared_lower_bound':str(leakage*leakage/dual2),
                          'affine_classification_sample_count_condition':8900>p*p})
    n=10000
    with ctx.workprec(384):
        zfinite=sum((ball(Q(1,k*k)) for k in range(1,n+1)),arb(0))
        lfinite=sum((arb(k).log()/k**2 for k in range(2,n+1)),arb(0))
        zlo=zfinite+ball(Q(1,n+1));zhi=zfinite+ball(Q(1,n))
        llo=lfinite+(arb(n+1).log()+1)/(n+1)
        lhi=lfinite+(arb(n).log()+1)/n
        dlo=14*zlo**13*llo;dhi=14*zhi**13*lhi
        reported=Q(c['complete_signal_derivative_upper'])
        assert ball(reported)>dhi
        assert ball(Q(c['zeta2_comparison_upper']))>zhi
        assert ball(Q(c['logarithmic_series_comparison_upper']))>lhi
        epsa=Q(c['clock_slope_radius']);epsb=Q(c['clock_offset_radius'])
        assert epsa==Q(1,10**14) and epsb==Q(1,10**11)
        maxtime=Q(c['maximum_nominal_absolute_time_upper'])
        assert maxtime==890 and Q(8899,10)<maxtime
        asserted=Q(c['complete_clock_distortion_radius'])
        assert asserted==reported*(maxtime*epsa+epsb)
        derivative={'independent_cutoff':n,'working_precision_bits':384,
                    'complete_derivative_interval':[str(endpoint(dlo.lower())),str(endpoint(dhi.upper()))],
                    'reported_derivative_upper_verified':str(reported),
                    'reported_complete_clock_radius_verified':str(asserted),
                    'positive_series_tail_method':'integrals from N+1 and N bound the decreasing positive tails'}
    return {'verified':True,'approximation_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'nuisance_witnesses':witnesses,'complete_derivative':derivative}


if __name__=='__main__':print(json.dumps(run(),indent=2))
