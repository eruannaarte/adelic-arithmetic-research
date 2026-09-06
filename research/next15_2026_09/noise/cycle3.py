"""Certified arithmetic recovery in arbitrary affine measurement drift."""
from fractions import Fraction as Q
import argparse,json
from flint import arb,ctx
import cycle1 as c1
import cycle2 as c2

HERE=c1.HERE

def validate_inputs(inputs):
    expected={'schema':'noise-affine-nuisance-input-v1','known_a1':1,
              'nuisance':'arbitrary complex beta0+beta1*t','measurement_count':8900,
              'declared_sensor_radii':{'multi':'9/100000','outer':'7/100000'},
              'correction_radius':str(c2.XI)}
    if inputs!=expected:raise ValueError('frozen normalized affine-nuisance contract mismatch')

def nuisance_gram(weights,precision):
    # Symmetry is exact. Constant and t columns are exactly orthogonal;
    # every other cross term is pure imaginary.
    pos=weights[4450:];ts=[c1.ball(Q(2*j+1,10)) for j in range(4450)]
    variance=2*sum((w*t*t for w,t in zip(pos,ts)),arb(0))
    if not variance>0:raise ValueError('linear nuisance has zero norm')
    norm=variance.sqrt();wt=[w*t for w,t in zip(pos,ts)]
    imaginary=[arb(0)]
    for n in range(2,51):
        logn=arb(n).log()
        imaginary.append(2*sum((a*(t*logn).sin() for a,t in zip(wt,ts)),arb(0))/norm)
    return variance,imaginary

def derive(bias,qrows,gabs,h0,eta,xi):
    if len(bias)!=50 or len(qrows)!=50 or len(gabs)!=50:raise ValueError('wrong retained dimension')
    if min(bias)<0 or min(qrows)<0 or min(gabs)<0 or h0<0 or eta<0 or xi<0:raise ValueError('negative bound')
    q=max(qrows)
    if q>=1:raise ValueError('original Gram invertibility not proved')
    v=[g+qr*max(gabs)/(1-q) for g,qr in zip(gabs,qrows)]
    gamma=1-sum((g*r for g,r in zip(gabs,v)),Q())
    if gamma<=0:raise ValueError('Schur complement positivity not proved')
    augmented_q=max(max(a+b for a,b in zip(qrows,gabs)),sum(gabs))
    if augmented_q>=1:raise ValueError('augmented singular-value floor not proved')
    channel=h0+sum((g*b/(2*n*n) for n,(g,b) in enumerate(zip(gabs,bias),1)),Q())
    extra=[n*n*r*channel/gamma for n,r in enumerate(v,1)]
    augmented_bias=[b/2+e for b,e in zip(bias,extra)]
    margins=[Q(1,2)-b for b in augmented_bias]
    # Coefficient1 is supplied by normalization, not inferred from a column
    # which exactly aliases the arbitrary constant baseline.
    if min(margins[1:])<=0:raise ValueError('positive rounding margin unavailable')
    radius2=min(m*m*(1-augmented_q)/n**4 for n,m in enumerate(margins,1) if n>=2)
    if not (eta+xi)**2<radius2:raise ValueError('augmented strict noise certificate fails')
    with ctx.workprec(192):
        remaining=min(c1.ball(m)-n*n*c1.ball(eta+xi)/c1.ball(1-augmented_q).sqrt() for n,m in enumerate(margins,1) if n>=2)
        radius=c1.iv(c1.ball(radius2).sqrt()-c1.ball(xi))
    return {'original_complete_bias_upper':list(map(str,bias)),
            'original_gram_rows':list(map(str,qrows)),'nuisance_cross_absolute_upper':list(map(str,gabs)),
            'inverse_cross_absolute_upper':list(map(str,v)),
            'schur_complement_lower':str(gamma),'augmented_gram_defect_upper':str(augmented_q),
            'centered_tail_pointwise_upper':str(h0),'complete_nuisance_channel_upper':str(channel),
            'additional_decoded_bias_upper':list(map(str,extra)),
            'augmented_complete_bias_upper':list(map(str,augmented_bias)),
            'sensor_error_radius':str(eta),'digital_correction_radius':str(xi),
            'sufficient_total_radius_squared':str(radius2),'sensor_radius_threshold_interval':radius,
            'remaining_rounding_margin_lower':c1.iv(remaining)[0]}

def build(precision=192,inputs=None):
    if precision<128:raise ValueError('precision below128')
    if inputs is None:inputs=json.loads((HERE/'cycle3_inputs.json').read_text())
    validate_inputs(inputs)
    # Standalone N3 checking includes the actual supplied preprocessing vector,
    # rather than assuming an unrelated earlier package check validated it.
    centering=c2.check()
    if Q(centering['correction_error_strict_upper'])>Q(inputs['correction_radius']):
        raise ValueError('centering error exceeds the nuisance theorem budget')
    with ctx.workprec(precision):
        bias,qr,qo,_,digests=c1.dependencies()
        outer,_,_=c1.base.source_bias(c1.base.SINGLE)
        # Complete unwindowed tail at Re(s)=2, including every index>50.
        h0=(arb(2).zeta()**14-sum((c1.ball(Q(c1.divisor14(n),n*n)) for n in range(1,51)),arb(0)))/2
        hupper=Q(c1.iv(h0)[1])
        long=c1.base.weights(8900);inner=c1.base.weights(2550)
        short=[arb(0)]*8900;short[3175:5725]=inner
        mix=[c1.ball(c1.A0)*a+c1.ball(1-c1.A0)*b for a,b in zip(short,long)]
        designs={}
        for name,w,b,q in [('multi',mix,bias,qr),('outer',long,outer,qo)]:
            variance,g=nuisance_gram(w,precision)
            # Published rational upper endpoints are the exact premises used
            # by all subsequent inequalities, so replay is stable across bits.
            givs=[c1.iv(x) for x in g]
            gabs=[max(abs(Q(lo)),abs(Q(hi))) for lo,hi in givs]
            eta=Q(inputs['declared_sensor_radii'][name]);xi=Q(inputs['correction_radius'])
            d=derive(b,q,gabs,hupper,eta,xi)
            d['time_second_moment_interval']=c1.iv(variance)
            d['nuisance_cross_imaginary_intervals']=givs
            designs[name]=d
        return {'schema':'noise-cycle3-v1','inputs':inputs,
                'certified_correction_sha256':centering['correction_sha256'],
                'full_unwindowed_centered_tail_interval':c1.iv(h0),
                'designs':designs,'dependency_binding':digests,
                'scope':'known a1=1, allother retained integers, arbitrary complex affine baseline, exact augmented fit',
                'exact_obstruction':'without known a1, adding1 toa1 and subtracting1 frombeta0 gives identical observations'}

def check():
    fresh=build();saved=json.loads((HERE/'cycle3_evidence.json').read_text())
    if fresh!=saved:raise ValueError('N3 full nuisance certificate mismatch')
    return fresh

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    if args.write:(HERE/'cycle3_evidence.json').write_text(json.dumps(build(),indent=2)+'\n')
    d=check();print('N3 PASS: arbitrary affine baseline, knowna1, same8900 observations')
    for name,v in d['designs'].items():
        print(name,'noise radius',v['sensor_error_radius'],'maxbias',float(max(map(Q,v['augmented_complete_bias_upper']))),'remainingmargin',float(Q(v['remaining_rounding_margin_lower'])))
