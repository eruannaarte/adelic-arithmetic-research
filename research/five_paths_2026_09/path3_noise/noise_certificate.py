"""Outward finite noise bounds for the actual 8,900-observation AS-V decoder.

Fast rebuilds assume the separately verified complete tail artifacts. Run
rebuild_dependencies.py to reconstruct their mathematical inputs as well.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from flint import arb, ctx, fmpq
from arithmetic_sensing_iv import REFERENCE_COEFFICIENTS
from verified_end_to_end_certificate import VerifiedTimeComponent, verified_ensemble_gram_row_bound
from verify_mellin_certificate import verify_artifact as verify_remote_artifact

HERE = Path(__file__).resolve().parent
SCALE = 1 << 128
COMPONENTS = ((510, 2550, F(125, 65536)), (1780, 8900, F(65411, 65536)))
MULTI = ROOT / 'certificates/arithmetic_sensing_v_multiscale_end_to_end.json'
SINGLE = ROOT / 'certificates/arithmetic_sensing_v_multiscale_T1780_single_end_to_end.json'


def ball(x: F | int) -> arb:
    x = F(x)
    return arb(fmpq(x.numerator, x.denominator))


def endpoint(x: arb) -> F:
    m, e = x.man_exp()
    return F(int(m) * (1 << int(e))) if e >= 0 else F(int(m), 1 << -int(e))


def enclosure(x: arb) -> list[str]:
    if not x.is_finite():
        raise ValueError('nonfinite enclosure')
    return [str(endpoint(x.lower())), str(endpoint(x.upper()))]


def canonical(x: object) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def vector(values: object, scale: object) -> list[F]:
    if not isinstance(values, list) or len(values) != 50 or type(scale) is not int or scale != 128:
        raise ValueError('wrong vector length or frozen dyadic scale')
    nums = [int(x) for x in values]
    if min(nums) < 0:
        raise ValueError('negative upper bound')
    return [F(x, 1 << scale) for x in nums]


def require_parameters(actual: dict, expected: dict) -> None:
    if any(actual.get(k) != v for k, v in expected.items()):
        raise ValueError('source contract mismatch')


def remote_vector(dependency: dict, observation_time: int) -> list[F]:
    name = f'arithmetic_sensing_v_multiscale_T{observation_time}_remote.json'
    if dependency.get('artifact_name') != name:
        raise ValueError('wrong remote dependency name')
    doc = json.loads((ROOT / 'certificates' / name).read_text())
    c = doc['certificate']
    # This validates the formal projection (hybrid observations are not signed),
    # then binds that exact formal payload to the end-to-end source dependency.
    verify_remote_artifact(doc, c)
    if doc['formal_certificate_sha256'] != dependency.get('formal_certificate_sha256'):
        raise ValueError('remote dependency digest mismatch')
    require_parameters(c['parameters'], {
        'maximum_norm': 50, 'sigma': 2, 'truncation': 1_000_000,
        'observation_time': observation_time, 'sample_count': observation_time * 5,
        'kernel_bound_method': 'cancellation', 'bin_width': '1/100',
        'bin_count': 8246, 'remote_output_scale_bits': 128,
        'one_factor_dyadic_scale_bits': 96, 'mpfr_precision_bits': 192,
        'remote_range_strategy': 'explicit_bin_count',
        'window_coefficients_binary64_hex': [float(x).hex() for x in REFERENCE_COEFFICIENTS],
    })
    if [d['degree'] for d in c['degrees']] != [14]:
        raise ValueError('wrong remote degree census')
    d = c['degrees'][0]
    return vector(d['remote_target_numerators'], d['remote_output_scale_bits'])


def source_bias(path: Path) -> tuple[list[F], list[F], str]:
    if path not in (MULTI, SINGLE):
        raise ValueError('unsupported source artifact')
    doc = json.loads(path.read_text())
    c = doc['certificate']
    if hashlib.sha256(canonical(c)).hexdigest() != doc['formal_certificate_sha256']:
        raise ValueError('corrupt source artifact')
    p = c['parameters']
    require_parameters(p, {'maximum_norm': 50, 'sigma': 2, 'truncation': 1_000_000})
    g = c['gram']
    qrows = vector(g['row_numerators'], g['output_scale_bits'])
    q = max(qrows)
    if not 0 <= q < 1:
        raise ValueError('Neumann premise failed')
    if path == MULTI:
        require_parameters(p, {
            'degree': 14, 'components': [dict(observation_time=t, sample_count=m, weight=str(w)) for t,m,w in COMPONENTS],
            'centered_grid_inclusion_offsets': [3175, 0],
            'common_sample_spacing': '1/5', 'distinct_sample_count': 8900,
            'component_sample_count_sum': 11450, 'outer_component_index': 1,
            'maximum_observation_time': 1780,
        })
        deps = c['remote_dependencies']
        if len(deps) != 2:
            raise ValueError('wrong remote dependency census')
        rv = [remote_vector(dep, t) for dep,(t,_,_) in zip(deps, COMPONENTS)]
        f, r = c['finite'], c['combined_remote']
        finite = vector(f['target_numerators'], f['output_scale_bits'])
        remote = vector(r['target_numerators'], r['output_scale_bits'])
        for j, bound in enumerate(remote):
            exact = sum((w * row[j] for row,(_,_,w) in zip(rv, COMPONENTS)), F())
            scaled = exact * (1 << 128)
            rounded = F(-(-scaled.numerator // scaled.denominator), 1 << 128)
            if bound != rounded:
                raise ValueError('combined remote does not match bound components')
    else:
        require_parameters(p, {'observation_time': 1780, 'sample_count': 8900, 'finite_output_scale_bits': 128})
        if [d['degree'] for d in c['degrees']] != [14]:
            raise ValueError('wrong single-window degree census')
        d = c['degrees'][0]
        if d['finite_output_scale_bits'] != p['finite_output_scale_bits']:
            raise ValueError('finite scale mismatch')
        finite = vector(d['finite_target_numerators'], d['finite_output_scale_bits'])
        remote = remote_vector(c['remote_dependency'], 1780)
    tails = [a+b for a,b in zip(finite, remote)]
    top = max(tails)
    biases = [(i+1)**2 * (t + qi*top/(1-q)) for i,(t,qi) in enumerate(zip(tails,qrows))]
    return biases, qrows, doc['formal_certificate_sha256']


def weights(sample_count: int) -> list[arb]:
    """Evaluate the original [0,T] density at its exact midpoint phases."""
    coeff = [ball(F.from_float(float(x))) for x in REFERENCE_COEFFICIENTS]
    out = []
    for j in range(sample_count):
        angle = arb.pi() * (2*j+1)/sample_count
        density = 1 + 2*sum((c*(k*angle).cos() for k,c in enumerate(coeff,1)),arb(0))
        if not density > 0:
            raise ValueError('positive weight not certified')
        out.append(density/sample_count)
    return out


def weight_statistics() -> dict[str, object]:
    long = weights(8900)
    inner = weights(2550)
    short = [arb(0) for _ in range(8900)]
    short[3175:5725] = inner
    x = ball(F(125,65536))
    multi = [x*a+(1-x)*b for a,b in zip(short,long)]
    out = {}
    for name, w in [('multi',multi),('single',long)]:
        mass = sum(w,arb(0))
        if not mass.contains(1):
            raise ValueError('midpoint mass failed')
        s2 = sum((v*v for v in w),arb(0))
        out[name] = {'mass':enclosure(mass),'sum_squared_weights':enclosure(s2),
                     'max_weight_upper':str(max(endpoint(v.upper()) for v in w))}
    single_exact = (1+2*sum((F.from_float(float(c))**2 for c in REFERENCE_COEFFICIENTS),F()))/8900
    if not F(out['single']['sum_squared_weights'][0]) <= single_exact <= F(out['single']['sum_squared_weights'][1]):
        raise ValueError('independent roots-of-unity square identity failed')
    cross = 2*x*(1-x)*sum((a*b for a,b in zip(short,long)),arb(0))
    out['reuse_cross_term'] = enclosure(cross)
    out['single_s2_exact'] = str(single_exact)
    return out


def derive_noise(bias: list[F], qrows: list[F], s2: tuple[F,F]) -> dict[str,object]:
    if len(bias)!=50 or len(qrows)!=50 or min(qrows)<0 or max(qrows)>=1 or not 0<s2[0]<=s2[1]:
        raise ValueError('invalid consequence inputs')
    q = max(qrows)
    variance = []
    for n,qi in enumerate(qrows,1):
        delta = qi/(1-q)
        if delta>=1:
            raise ValueError('lower variance bound unavailable')
        variance.append((n**4*s2[0]*(1-delta)**2, n**4*s2[1]*(1+delta)**2))
    margins = [F(1,2)-b for b in bias]
    eta2 = min(m*m*(1-q)/(n**4) for n,m in enumerate(margins,1)) if min(margins)>0 else F(0)
    sigma = F(1,100000)
    if min(margins)>0:
        failure = sum(((-ball(m*m/(sigma*sigma*v[1]))).exp() for m,v in zip(margins,variance)),arb(0))
        failure_upper = min(F(1),endpoint(failure.upper()))
    else:
        failure_upper = F(1)
    # A round declared radius makes a stable independently checkable claim.
    declared_eta = F(7,10_000_000)
    return {'bias_upper':[str(b) for b in bias], 'qrows':[str(qi) for qi in qrows],
            'variance_intervals':[[str(l),str(u)] for l,u in variance],
            'weighted_noise_radius_squared_sufficient':str(eta2),
            'declared_weighted_noise_radius':str(declared_eta),
            'declared_radius_certified':declared_eta**2<eta2,
            'iid_circular_complex_sigma':str(sigma),
            'gaussian_union_failure_upper':str(failure_upper),
            'bias_certificate_alone_succeeds':min(margins)>0}


def build(precision: int = 192) -> dict[str,object]:
    if precision<128:
        raise ValueError('at least128 bits required')
    ctx.prec=precision
    stats=weight_statistics()
    results={}
    for name,path,components in [('multi',MULTI,COMPONENTS),('single',SINGLE,((1780,8900,F(1)),))]:
        biases,qrows,digest=source_bias(path)
        # Reconstruct all Gram rows with Arb; tail reconstruction is separate.
        fresh=verified_ensemble_gram_row_bound([VerifiedTimeComponent(*c) for c in components],
                                               50,precision=192,output_scale_bits=128)
        # Higher precision can improve the last dyadic bit; it must still fit the committed bound.
        if any(F(v,1<<fresh.scale_bits)>old for v,old in zip(fresh.row_numerators,qrows)):
            raise ValueError('stored Gram row upper fails fresh reconstruction')
        result=derive_noise(biases,qrows,tuple(map(F,stats[name]['sum_squared_weights'])))
        result['source_payload_sha256']=digest
        results[name]=result
    # Independent finite-series bounds establish whether variance really increased.
    vlo=F(results['multi']['variance_intervals'][49][0])
    vhi=F(results['single']['variance_intervals'][49][1])
    payload={'schema':'five-paths-arithmetic-noise-v1','precision_bits':precision,
             'measurement_count':8900,'times':'t_j=(2j+1-8900)/10, j=0,...,8899',
             'weight_statistics':stats,'designs':results,
             'variance50_inflation_ratio_lower':str(vlo/vhi),
             'scope':'new noise consequences; complete deterministic tails require separately rebuilt dependencies'}
    return payload


def main() -> None:
    p=argparse.ArgumentParser();p.add_argument('--write',type=Path,default=HERE/'certificate.json')
    p.add_argument('--precision',type=int,default=192);a=p.parse_args()
    c=build(a.precision)
    a.write.write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')
    print(json.dumps({name:{'bias':float(max(map(F,d['bias_upper']))),
                          'weighted_radius_lower':float(ball(F(d['weighted_noise_radius_squared_sufficient'])).sqrt().lower()),
                          'gaussian_failure_upper':float(F(d['gaussian_union_failure_upper']))}
                      for name,d in c['designs'].items()},indent=2))
    print('variance50 inflation lower:',float(F(c['variance50_inflation_ratio_lower'])))


if __name__=='__main__':main()
