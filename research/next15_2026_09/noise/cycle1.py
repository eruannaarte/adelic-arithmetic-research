"""A complete-family bias-certificate/actual-variance tradeoff obstruction."""
from pathlib import Path
from fractions import Fraction as Q
from math import comb
import argparse,importlib.util,json,sys
from flint import arb,ctx,fmpq

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('baseline_noise',ROOT/'research/five_paths_2026_09/path3_noise/noise_certificate.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
from verified_end_to_end_certificate import VerifiedTimeComponent,verified_ensemble_gram_row_bound,verified_centered_response_interval

A0=Q(125,65536);LEFT=Q(17613,10**7);RIGHT=Q(5107,2500000)
MODES=(51,52,54,55,56,72,80,90,96,128,144,160,216,240)

def ball(x):
    x=Q(x);return arb(fmpq(x.numerator,x.denominator))

def endpoint(x):
    if not x.is_exact() or not x.is_finite():raise ValueError('finite exact endpoint required')
    m,e=map(int,x.man_exp());return Q(m*2**e) if e>=0 else Q(m,2**(-e))

def iv(x,scale=10**18):
    if not x.is_finite():raise ValueError('nonfinite arithmetic')
    lo=endpoint(x.lower());hi=endpoint(x.upper())
    return [str(Q(lo.numerator*scale//lo.denominator,scale)),str(Q(-((-hi.numerator*scale)//hi.denominator),scale))]

def divisor14(n):
    if type(n) is not int or n<1:raise ValueError('positive integer required')
    out=1;p=2
    while p*p<=n:
        e=0
        while n%p==0:n//=p;e+=1
        if e:out*=comb(e+13,13)
        p+=1
    if n>1:out*=14
    return out

def dependencies():
    biases,qref,refhash=base.source_bias(base.MULTI)
    _,qouter,outerhash=base.source_bias(base.SINGLE)
    doc=json.loads(base.MULTI.read_text())['certificate']
    remotes=[base.remote_vector(dep,t) for dep,t in zip(doc['remote_dependencies'],(510,1780))]
    return biases,qref,qouter,remotes,{'reference':refhash,'outer':outerhash,
           'remote_digests':[x['formal_certificate_sha256'] for x in doc['remote_dependencies']],
           'premise_status':'complete remote and finite baselines reconstructed in five_paths_2026_09; inherited explicitly'}

def response_interval(n,k,t,m,bits):
    lo,hi=verified_centered_response_interval(n,k,t,m,precision=bits)
    return arb(ball((lo+hi)/2),ball((hi-lo)/2))

def build(precision=192):
    if precision<128:raise ValueError('precision below128')
    with ctx.workprec(precision):
        bias,qref,qouter,remote,digests=dependencies()
        samples=[]
        for k in MODES:
            a=response_interval(50,k,510,2550,precision);b=response_interval(50,k,1780,8900,precision)
            samples.append((k,Q(divisor14(k),k*k),a,b))
        # Two globally valid affine minorants of the full absolute-tail
        # certificate; fixed signs are chosen at their respective endpoints.
        lines=[]
        for name,alpha in (('left',LEFT),('right',RIGHT)):
            const=ball(remote[1][49]);slope=ball(remote[0][49]-remote[1][49]);signs=[]
            for k,w,a,b in samples:
                z=b+ball(alpha)*(a-b)
                if z>0:sign=1
                elif z<0:sign=-1
                else:raise ValueError('minorant sign not separated')
                signs.append(sign);const+=ball(sign*w)*b;slope+=ball(sign*w)*(a-b)
            value=2500*(const+ball(alpha)*slope)
            if not value>ball(Q(1,2)):raise ValueError('endpoint exclusion failed')
            if name=='left' and not slope<0:raise ValueError('left exclusion direction')
            if name=='right' and not slope>0:raise ValueError('right exclusion direction')
            lines.append({'side':name,'alpha':str(alpha),'signs':signs,'coefficient50_minorant_at_endpoint':iv(value),
                          'normalized_intercept':iv(const),'normalized_slope':iv(slope)})
        fresh=[]
        for t,m in ((510,2550),(1780,8900)):
            g=verified_ensemble_gram_row_bound([VerifiedTimeComponent(t,m,Q(1))],50,precision=precision,output_scale_bits=128)
            fresh.append([Q(v,1<<128) for v in g.row_numerators])
        if any(new>old for new,old in zip(fresh[1],qouter)):raise ValueError('outer Gram premise does not reproduce')
        # The reference Gram is also rebuilt, preserving its cancellation.
        g=verified_ensemble_gram_row_bound([VerifiedTimeComponent(510,2550,A0),VerifiedTimeComponent(1780,8900,1-A0)],50,precision=precision,output_scale_bits=128)
        if any(Q(v,1<<128)>old for v,old in zip(g.row_numerators,qref)):raise ValueError('reference Gram mismatch')
        displacement=max(A0-LEFT,RIGHT-A0)
        qbox=[a+displacement*(b+c) for a,b,c in zip(qref,fresh[0],fresh[1])]
        q=max(qbox)
        if q>=1:raise ValueError('uniform Gram floor fails')
        short=base.weights(2550);long=base.weights(8900)
        cross=sum((a*b for a,b in zip(short,long[3175:5725])),arb(0))
        normconst=1+2*sum((Q.from_float(float(c))**2 for c in base.REFERENCE_COEFFICIENTS),Q())
        AS=normconst/2550;BL=normconst/8900
        curvature=ball(AS+BL)-2*cross
        if not cross>ball(BL) or not curvature>0:raise ValueError('variance mass monotonicity fails')
        s2=ball(LEFT**2*AS+(1-LEFT)**2*BL)+2*ball(LEFT*(1-LEFT))*cross
        slo=endpoint(s2.lower())
        delta=qbox[49]/(1-q)
        outerdelta=qouter[49]/(1-max(qouter))
        if delta>=1:raise ValueError('variance lower unavailable')
        ratio=slo*(1-delta)**2/(BL*(1+outerdelta)**2)
        if not ratio>1:raise ValueError('uniform actual variance inflation not proved')
        return {'schema':'noise-cycle1-v1','family':'alpha in[0,1], same8900 observations and positive nested windows',
                'necessary_alpha_interval':[str(LEFT),str(RIGHT)],'scope':'necessary for the original complete absolute-tail Neumann certificate, not actual recovery impossibility',
                'minorants':lines,'selected_mode_intervals':[{'k':k,'d14_over_k_squared':str(w),'short':iv(a),'outer':iv(b)} for k,w,a,b in samples],
                'remote50_bounds':[str(row[49]) for row in remote],
                'uniform_gram_rows':list(map(str,qbox)),'uniform_gram_defect':str(q),
                'weight_statistics':{'short_s2_exact':str(AS),'outer_s2_exact':str(BL),'reuse_inner_product':iv(cross),'curvature':iv(curvature),'minimum_s2_in_interval':iv(s2)},
                'coefficient50_variance_inflation_lower':iv(ball(ratio))[0],
                'reference_complete_bias_upper':str(max(bias)),'reference_alpha':str(A0),'dependency_binding':digests,
                'proved':'every rounding-capable original mixture certificate pays strictly greater target50 iid variance than the outer window'}

def check():
    saved=json.loads((HERE/'cycle1_evidence.json').read_text());fresh=build()
    if saved!=fresh:raise ValueError('full N1 reconstruction mismatch')
    return fresh

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    if a.write:(HERE/'cycle1_evidence.json').write_text(json.dumps(build(),indent=2)+'\n')
    d=check();print('N1 PASS: complete-family certificate/actual-variance Pareto obstruction')
    print('alpha interval',d['necessary_alpha_interval']);print('uniform variance inflation lower',d['coefficient50_variance_inflation_lower'])
