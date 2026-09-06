"""Full physical-grid certificates for polynomial instrument drift.

Every new polynomial, moment, cross channel and complete nuisance-tail bound
is reconstructed with outward Arb arithmetic. The older arithmetic tail
premises are validated and explicitly inherited, never silently truncated.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse, hashlib, json, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / 'research/next15_2026_09/noise'
sys.path.insert(0, str(OLD))
import cycle1 as prior
import cycle2 as centering
from flint import arb, ctx

SCALE = 10**18
INPUTS = {
    'schema': 'polynomial-drift-input-v1',
    'known_a1': 1,
    'measurement_count': 8900,
    'time_formula': '(2*j+1-8900)/10, j=0,...,8899',
    'polynomial_coordinate': 'x=t/890',
    'source': 'integer 0<=a(k)<=d14(k), all k>=1',
    'nuisance': 'arbitrary complex polynomial of degree at most p',
    'maximum_explored_degree': 6,
    'correction_radius': str(centering.XI),
    'declared_sensor_radii': {
        'multi': ['97/1000000', '9/100000', '77/1000000', '53/1000000', '16/1000000', None],
        'outer': ['77/1000000', '7/100000', '57/1000000', '33/1000000', None, None],
    },
}


def validate_inputs(inputs):
    if inputs != INPUTS:
        raise ValueError('fixed source, normalization, acquisition or nuisance contract changed')


def endpoint_interval(x):
    return prior.iv(x, SCALE)


def upper(x):
    return Q(endpoint_interval(x)[1])


def inner_polynomial(a, b, moments):
    return sum((x*y*moments[i+j] for i, x in enumerate(a)
                for j, y in enumerate(b)), arb(0))


def evaluate(coefficients, x):
    out = arb(0)
    for a in reversed(coefficients):
        out = out*x+a
    return out


def nuisance_basis(weights, max_degree):
    """Enclose the exactly defined W-orthonormal polynomial basis.

    The exact basis is Gram--Schmidt applied to 1,x,...,x**p in the actual
    positive weighted inner product. Symmetry makes all odd moments zero.
    """
    if len(weights) != 8900 or max_degree != 6:
        raise ValueError('only the declared physical grid and bounded search are supported')
    if not all(w > 0 for w in weights):
        raise ValueError('strictly positive physical weights required')
    positive = weights[4450:]
    times = [prior.ball(Q(2*j+1, 10)) for j in range(4450)]
    xs = [t/890 for t in times]
    moments = [arb(1)] + [arb(0)]*(2*max_degree)
    for k in range(2, 2*max_degree+1, 2):
        moments[k] = 2*sum((w*x**k for w, x in zip(positive, xs)), arb(0))
    basis = [[arb(1)]]
    residual_norms = []
    for d in range(1, max_degree+1):
        monomial = [arb(0)]*d + [arb(1)]
        residual = monomial[:]
        for k, previous in enumerate(basis):
            if (d-k) % 2:
                continue  # Exact symmetry, not a numerical zero test.
            projection = inner_polynomial(monomial, previous, moments)
            for j, a in enumerate(previous):
                residual[j] -= projection*a
        norm2 = inner_polynomial(residual, residual, moments)
        if not norm2 > 0:
            raise ValueError('positive polynomial residual norm not proved')
        residual_norms.append(norm2)
        basis.append([a/norm2.sqrt() for a in residual])
    # This is an additional consistency check; exact orthogonality follows
    # from the defining Gram--Schmidt identity proved in PROOFS.md.
    for i, a in enumerate(basis):
        for j, b in enumerate(basis):
            if not inner_polynomial(a, b, moments).contains(int(i == j)):
                raise ValueError('orthonormal defining identity lost by enclosure')
    values = [[evaluate(p, x) for x in xs] for p in basis[1:]]
    l1 = [2*sum((w*abs(p) for w, p in zip(positive, vals)), arb(0)) for vals in values]
    # C[n,k] = <arithmetic column n, polynomial k>_W. Parity makes each
    # entry purely real or purely imaginary, and its constant entry zero.
    crosses = [[arb(0)]*max_degree]
    for n in range(2, 51):
        logn = arb(n).log()
        sines = [(t*logn).sin() for t in times]
        cosines = [(t*logn).cos() for t in times]
        crosses.append([
            2*sum((w*p*z for w, p, z in zip(positive, vals,
                       sines if k % 2 else cosines)), arb(0))
            for k, vals in enumerate(values, 1)
        ])
    return {
        'moments': [endpoint_interval(a) for a in moments],
        'polynomial_coefficients': [[endpoint_interval(a) for a in p] for p in basis],
        'gram_schmidt_residual_norm_squared': [endpoint_interval(a) for a in residual_norms],
        'weighted_absolute_polynomial_norms': [endpoint_interval(a) for a in l1],
        'cross_channels_real_for_even_imaginary_for_odd': [
            [endpoint_interval(a) for a in row] for row in crosses
        ],
    }


def rational_consequences(bias, qrows, cross, l1, h0, degree, eta):
    """Derive componentwise Schur and complete-tail bounds exactly."""
    if len(bias) != 50 or len(qrows) != 50 or len(cross) != 50:
        raise ValueError('wrong retained dimension')
    if type(degree) is not int or not 1 <= degree <= 6:
        raise ValueError('degree outside bounded exploration')
    if len(l1) < degree or any(len(row) < degree for row in cross):
        raise ValueError('missing complete nuisance channels')
    if min(bias + qrows + l1 + [h0]) < 0 or any(min(row) < 0 for row in cross):
        raise ValueError('negative bound')
    if eta is not None and eta < 0:
        raise ValueError('negative sensor radius')
    q = max(qrows)
    if q >= 1:
        raise ValueError('arithmetic Gram floor unavailable')
    c = [row[:degree] for row in cross]
    maxc = [max(row[k] for row in c) for k in range(degree)]
    v = [[a + qrows[n]*maxc[k]/(1-q) for k, a in enumerate(row)]
         for n, row in enumerate(c)]
    m = [[sum((c[n][i]*v[n][j] for n in range(50)), Q())
          for j in range(degree)] for i in range(degree)]
    mrows = [sum(row, Q()) for row in m]
    schur_defect = max(mrows)
    qaug = max(max(qrows[n] + sum(row, Q()) for n, row in enumerate(c)),
               max(sum((row[k] for row in c), Q()) for k in range(degree)))
    if schur_defect >= 1 or qaug >= 1:
        raise ValueError('positive augmented Gram or Schur floor unavailable')
    centered_z = [b/(2*n*n) for n, b in enumerate(bias, 1)]
    channel = [h0*l1[k] + sum((c[n][k]*centered_z[n] for n in range(50)), Q())
               for k in range(degree)]
    # |S^-1 r| <= |r| + |I-S| max|r|/(1-||I-S||_infinity).
    schur_solution = [r + row*max(channel)/(1-schur_defect)
                      for r, row in zip(channel, mrows)]
    additional = [n*n*sum((a*r for a, r in zip(row, schur_solution)), Q())
                  for n, row in enumerate(v, 1)]
    total_bias = [b/2+e for b, e in zip(bias, additional)]
    margins = [Q(1, 2)-b for b in total_bias]
    positive = min(margins[1:]) > 0
    radius2 = (min(m*m*(1-qaug)/n**4 for n, m in enumerate(margins, 1) if n >= 2)
               if positive else None)
    certified = positive and eta is not None and (eta+centering.XI)**2 < radius2
    if eta is not None and not certified:
        raise ValueError('declared strict all-coefficient certificate failed')
    return {
        'degree': degree,
        'inverse_cross_absolute_upper': [[str(a) for a in row] for row in v],
        'schur_defect_matrix_absolute_upper': [[str(a) for a in row] for row in m],
        'schur_infinity_defect_upper': str(schur_defect),
        'augmented_gram_defect_upper': str(qaug),
        'complete_centered_nuisance_channels_upper': [str(h0*a) for a in l1[:degree]],
        'schur_residual_channels_upper': list(map(str, channel)),
        'schur_solution_absolute_upper': list(map(str, schur_solution)),
        'additional_decoded_bias_upper': list(map(str, additional)),
        'complete_decoded_bias_upper': list(map(str, total_bias)),
        'positive_rounding_margin': positive,
        'declared_sensor_radius': str(eta) if eta is not None else None,
        'sufficient_total_radius_squared': str(radius2) if radius2 is not None else None,
        'rounding_certified': certified,
        'status': 'certified' if certified else 'this sufficient complete-tail gate fails',
    }


def file_bindings():
    paths = [OLD/'cycle2_evidence.json', OLD/'cycle2_correction.json',
             prior.base.MULTI, prior.base.SINGLE]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths}


def build(precision=192, inputs=None):
    if type(precision) is not int or precision < 128:
        raise ValueError('at least 128 bits required')
    inputs = INPUTS if inputs is None else inputs
    validate_inputs(inputs)
    correction_evidence, vector = centering.build(precision)
    if correction_evidence != json.loads((OLD/'cycle2_evidence.json').read_text()):
        raise ValueError('inherited centering consequence does not replay')
    if vector != json.loads((OLD/'cycle2_correction.json').read_text()):
        raise ValueError('full 8,900-reading correction does not replay')
    with ctx.workprec(precision):
        bias, qr, qo, _, dependencies = prior.dependencies()
        outer_bias, _, _ = prior.base.source_bias(prior.base.SINGLE)
        long = prior.base.weights(8900)
        short = [arb(0)]*8900
        short[3175:5725] = prior.base.weights(2550)
        mix = [prior.ball(prior.A0)*a+prior.ball(1-prior.A0)*b for a, b in zip(short, long)]
        h0 = (arb(2).zeta()**14 - sum((prior.ball(Q(prior.divisor14(n), n*n))
                                     for n in range(1, 51)), arb(0)))/2
        designs = {}
        for name, weights, b, q in [('multi', mix, bias, qr), ('outer', long, outer_bias, qo)]:
            components = ([prior.VerifiedTimeComponent(510, 2550, prior.A0),
                           prior.VerifiedTimeComponent(1780, 8900, 1-prior.A0)]
                          if name == 'multi' else [prior.VerifiedTimeComponent(1780, 8900, Q(1))])
            fresh_gram = prior.verified_ensemble_gram_row_bound(
                components, 50, precision=precision, output_scale_bits=128)
            if any(Q(a, 1 << 128) > bound for a, bound in zip(fresh_gram.row_numerators, q)):
                raise ValueError('physical arithmetic Gram premise does not replay')
            numeric = nuisance_basis(weights, inputs['maximum_explored_degree'])
            cross = [[max(abs(Q(lo)), abs(Q(hi))) for lo, hi in row]
                     for row in numeric['cross_channels_real_for_even_imaginary_for_odd']]
            l1 = [Q(hi) for lo, hi in numeric['weighted_absolute_polynomial_norms']]
            records = [rational_consequences(b, q, cross, l1, upper(h0), p,
                       Q(eta) if eta is not None else None)
                       for p, eta in enumerate(inputs['declared_sensor_radii'][name], 1)]
            designs[name] = {
                'original_complete_bias_upper': list(map(str, b)),
                'original_gram_rows': list(map(str, q)),
                'physical_polynomial_reconstruction': numeric,
                'degrees': records,
            }
        return {
            'schema': 'polynomial-drift-certificate-v1',
            'inputs': inputs,
            'full_pointwise_centered_tail_interval': endpoint_interval(h0),
            'digital_correction_sha256': correction_evidence['correction_sha256'],
            'dependency_binding': dependencies,
            'premise_file_sha256': file_bindings(),
            'designs': designs,
            'scope': 'known a1; exact polynomial drift fit; all 49 unknown retained integers; actual respective W norm',
        }


def check(precision=192):
    fresh = build(precision)
    saved = json.loads((HERE/'evidence.json').read_text())
    if fresh != saved:
        raise ValueError('fresh physical-grid and complete-channel replay differs from evidence')
    return fresh


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--precision', type=int, default=192)
    args = parser.parse_args()
    if args.write:
        (HERE/'evidence.json').write_text(json.dumps(build(args.precision), indent=2)+'\n')
    result = check(args.precision)
    print('PASS: complete polynomial-drift physical reconstruction')
    for name, d in result['designs'].items():
        for r in d['degrees']:
            print(name, 'degree', r['degree'], 'eta', r['declared_sensor_radius'],
                  'max bias', float(max(map(Q, r['complete_decoded_bias_upper'][1:]))), r['status'])
