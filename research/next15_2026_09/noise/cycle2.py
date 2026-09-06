"""Full infinite-tail envelope centering with certified digital correction."""
from fractions import Fraction as Q
import argparse,hashlib,json
from flint import acb,arb,ctx
import cycle1 as c1

HERE=c1.HERE;DEN=10**20;XI=Q(1,DEN)

def correction(precision=192):
    if precision<128:raise ValueError('precision below128')
    rows=[]
    with ctx.workprec(precision):
        logs=[arb(n).log() for n in range(1,51)]
        coefficients=[c1.ball(Q(c1.divisor14(n),n*n)) for n in range(1,51)]
        for j in range(4450):
            t=c1.ball(Q(2*j+1,10))
            head=sum((b*acb(0,-t*l).exp() for b,l in zip(coefficients,logs)),acb(0))
            z=(acb(2,t).zeta()**14-head)/2
            if not z.is_finite():raise ValueError('nonfinite full-tail correction')
            r=round(c1.endpoint(z.real.mid())*DEN)
            i=round(c1.endpoint(z.imag.mid())*DEN)
            # A squared-modulus enclosure includes all special-function,
            # finite-head, and rational-rounding errors, not just rounding.
            er=z.real-c1.ball(Q(r,DEN));ei=z.imag-c1.ball(Q(i,DEN))
            if not er*er+ei*ei<c1.ball(XI*XI):raise ValueError('correction error budget fails')
            rows.append([r,i])
    return {'schema':'noise-midpoint-vector-v1','positive_time_formula':'(2*j+1)/10,j=0,...,4449',
            'denominator':DEN,'positive_complex_numerators':rows,
            'negative_times':'conjugates in reversed positive-time order',
            'maximum_complex_error_strict_upper':str(XI),
            'formula':'(zeta(2+it)^14-sum(n<=50,d14(n)*n^(-2-it)))/2'}

def vector_digest(vector):
    return hashlib.sha256(json.dumps(vector,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def consequence(bias,qrows,eta,xi=XI):
    with ctx.workprec(192):
        return _consequence(bias,qrows,eta,xi)

def _consequence(bias,qrows,eta,xi):
    if len(bias)!=50 or len(qrows)!=50 or min(bias)<0 or min(qrows)<0 or max(qrows)>=1:
        raise ValueError('invalid full bias/Gram premise')
    eta,xi=Q(eta),Q(xi)
    if eta<0 or xi<0:raise ValueError('nonnegative error budgets required')
    q=max(qrows);margins=[Q(1,2)-b/2 for b in bias]
    if min(margins)<=0:raise ValueError('centered bias does not leave a strict rounding margin')
    radius2=min(m*m*(1-q)/n**4 for n,m in enumerate(margins,1))
    if not (eta+xi)**2<radius2:raise ValueError('strict all-coefficient rounding test fails')
    return {'complete_bias_upper':list(map(str,bias)),
            'centered_complete_bias_upper':[str(b/2) for b in bias],
            'gram_rows':list(map(str,qrows)),
            'declared_sensor_radius':str(eta),'digital_correction_radius':str(xi),
            'total_error_radius':str(eta+xi),
            'sufficient_total_radius_squared':str(radius2),
            'sensor_radius_threshold_interval':c1.iv(c1.ball(radius2).sqrt()-c1.ball(xi)),
            'rounding_margin_after_declared_errors_lower':c1.iv(min((c1.ball(m)-n*n*c1.ball(eta+xi)/c1.ball(1-q).sqrt() for n,m in enumerate(margins,1))))[0]}

def build(precision=192):
    with ctx.workprec(precision):
        vector=correction(precision)
        bias,qr,qo,remote,digests=c1.dependencies()
        outer,_,_=c1.base.source_bias(c1.base.SINGLE)
        multi=consequence(bias,qr,Q(1,10000))
        single=consequence(outer,qo,Q(8,100000))
        if max(bias)>=Q(1,2):raise ValueError('uncentered reference has no positive rounding margin for gain comparison')
        old_radius2=min((Q(1,2)-b)**2*(1-max(qr))/n**4 for n,b in enumerate(bias,1))
        gain=(c1.ball(Q(multi['sufficient_total_radius_squared'])).sqrt()-c1.ball(XI))/c1.ball(old_radius2).sqrt()
        evidence={'schema':'noise-cycle2-v1','measurement_count':8900,
                  'model':'all integer0<=a(k)<=d14(k); identical original observations',
                  'correction_sha256':vector_digest(vector),'correction_error_strict_upper':str(XI),
                  'designs':{'multi':multi,'outer':single},
                  'reference_noise_radius_gain_interval':c1.iv(gain),
                  'covariance':'exactly unchanged by deterministic centering; original reused-reading cross term retained',
                  'dependency_binding':digests,
                  'evaluation_trust':'Arb complex zeta/exponential enclosures plus exact rational final inequalities'}
        return evidence,vector

def check():
    evidence,vector=build()
    if evidence!=json.loads((HERE/'cycle2_evidence.json').read_text()):raise ValueError('N2 evidence mismatch')
    if vector!=json.loads((HERE/'cycle2_correction.json').read_text()):raise ValueError('complete correction vector mismatch')
    return evidence

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    if args.write:
        evidence,vector=build()
        (HERE/'cycle2_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
        (HERE/'cycle2_correction.json').write_text(json.dumps(vector,indent=2)+'\n')
    d=check()
    print('N2 PASS: full-tail midpoint correction, all8900 readings, strict bounded-noise rounding')
    for k,v in d['designs'].items():print(k,'sensor radius',v['declared_sensor_radius'],'threshold',v['sensor_radius_threshold_interval'])
    print('radius gain interval',d['reference_noise_radius_gain_interval'])
