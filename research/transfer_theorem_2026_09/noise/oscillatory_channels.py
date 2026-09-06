"""Complete nuisance-tail certificates from discrete summation by parts."""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import argparse, hashlib, json, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = ROOT/'research/unified_query_2026_09/noise'
sys.path.insert(0, str(PREVIOUS))
import polynomial_drift as old
from flint import arb, ctx

CUTOFF = 10**12
DENOMINATOR_LOWER = Q(2, 3)
XI = Q(1, 10**20)


def exp_upper(x, n):
    x = Q(x)
    if not 0 <= x < n+2:
        raise ValueError('invalid exponential tail ratio')
    return sum((x**k/factorial(k) for k in range(n+1)), Q()) + x**(n+1)/factorial(n+1)/(1-x/(n+2))


def phase_contract():
    low_exp = exp_upper(Q(39, 10), 80)
    high_exp = sum((Q(28)**k/factorial(k) for k in range(101)), Q())
    sin_low = Q(39, 100)-Q(39, 100)**3/6
    sin_high = sum(((-1)**k*Q(14, 5)**(2*k+1)/factorial(2*k+1) for k in range(8)), Q())
    if not low_exp < 51 or not high_exp > CUTOFF or min(sin_low, sin_high) <= Q(1, 3):
        raise ValueError('uniform finite-frequency separation from sampling aliases failed')
    return {'cutoff': CUTOFF, 'difference_order': 2,
            'frequency_half_step_interval': ['39/100', '14/5'],
            'phase_denominator_strict_lower': str(DENOMINATOR_LOWER),
            'exp_3_9_upper': str(low_exp), 'exp_28_lower': str(high_exp),
            'sin_0_39_lower': str(sin_low), 'sin_2_8_lower': str(sin_high),
            'remote_exponent': '3/2', 'square_root_cutoff': 10**6}


def basis_and_channels(weights, maximum_degree):
    if type(maximum_degree) is not int or not 1 <= maximum_degree <= 12:
        raise ValueError('only the declared bounded polynomial search is supported')
    if len(weights) != 8900 or not all(w > 0 for w in weights):
        raise ValueError('positive physical weights required')
    times = [old.prior.ball(Q(2*j+1, 10)) for j in range(4450)]
    xs = [t/890 for t in times]
    wpos = weights[4450:]
    moments = [arb(1)]+[arb(0)]*(2*maximum_degree)
    for k in range(2, 2*maximum_degree+1, 2):
        moments[k] = 2*sum((w*x**k for w, x in zip(wpos, xs)), arb(0))
    basis = [[arb(1)]]
    norms = []
    for d in range(1, maximum_degree+1):
        monomial = [arb(0)]*d+[arb(1)]
        residual = monomial[:]
        for k, p in enumerate(basis):
            if (d-k) % 2:
                continue
            projection = old.inner_polynomial(monomial, p, moments)
            for j, a in enumerate(p):
                residual[j] -= projection*a
        n2 = old.inner_polynomial(residual, residual, moments)
        if not n2 > 0:
            raise ValueError('positive polynomial residual norm not proved')
        norms.append(n2)
        basis.append([a/n2.sqrt() for a in residual])
    for i, a in enumerate(basis):
        for j, b in enumerate(basis):
            if not old.inner_polynomial(a, b, moments).contains(int(i == j)):
                raise ValueError('orthogonal-polynomial defining identities not enclosed')
    values = [[old.evaluate(p, x) for x in xs] for p in basis[1:]]
    l1, variation = [], []
    for k, positive_values in enumerate(values, 1):
        positive_weighted = [w*p for w, p in zip(wpos, positive_values)]
        full = [((-1)**k)*p for p in reversed(positive_weighted)]+positive_weighted
        l1.append(sum((abs(a) for a in full), arb(0)))
        # Both zero extensions are included. The resulting m+2 terms are
        # exactly the complete second difference of the zero-extended column.
        padded = [arb(0), arb(0)]+full+[arb(0), arb(0)]
        diff2 = [padded[j+2]-2*padded[j+1]+padded[j] for j in range(len(full)+2)]
        variation.append(sum((abs(a) for a in diff2), arb(0)))
    cross = [[arb(0)]*maximum_degree]
    for n in range(2, 51):
        logarithm = arb(n).log()
        sine = [(t*logarithm).sin() for t in times]
        cosine = [(t*logarithm).cos() for t in times]
        cross.append([2*sum((w*p*z for w, p, z in zip(wpos, vals, sine if k % 2 else cosine)), arb(0))
                      for k, vals in enumerate(values, 1)])
    interval = old.endpoint_interval
    return {'moments': [interval(x) for x in moments],
            'polynomial_coefficients': [[interval(x) for x in p] for p in basis],
            'residual_norm_squared': [interval(x) for x in norms],
            'weighted_l1': [interval(x) for x in l1],
            'zero_extended_second_difference_l1': [interval(x) for x in variation],
            'cross_real_even_imaginary_odd': [[interval(x) for x in row] for row in cross]}


def consequences(bias, qrows, cross, channels, degree, eta):
    if len(bias) != 50 or len(qrows) != 50 or len(cross) != 50:
        raise ValueError('wrong arithmetic dimension')
    if type(degree) is not int or not 1 <= degree <= 12:
        raise ValueError('invalid degree')
    if len(channels) < degree or any(len(row) < degree for row in cross):
        raise ValueError('incomplete nuisance channels')
    if min(bias+qrows+channels) < 0 or any(min(row) < 0 for row in cross):
        raise ValueError('negative bound')
    if eta is not None and eta < 0:
        raise ValueError('negative noise radius')
    q = max(qrows)
    if q >= 1:
        raise ValueError('arithmetic Gram floor not positive')
    c = [row[:degree] for row in cross]
    maxima = [max(row[k] for row in c) for k in range(degree)]
    inverse_cross = [[a+qrows[n]*maxima[k]/(1-q) for k, a in enumerate(row)] for n, row in enumerate(c)]
    defect = [[sum((c[n][i]*inverse_cross[n][j] for n in range(50)), Q())
               for j in range(degree)] for i in range(degree)]
    defect_rows = [sum(row, Q()) for row in defect]
    mu = max(defect_rows)
    qa = max(max(qrows[n]+sum(row, Q()) for n, row in enumerate(c)),
             max(sum((row[k] for row in c), Q()) for k in range(degree)))
    if max(mu, qa) >= 1:
        raise ValueError('augmented Schur or Gram positivity failed')
    residual = [channels[k]+sum((c[n][k]*bias[n]/(2*(n+1)**2) for n in range(50)), Q()) for k in range(degree)]
    solved = [r+d*max(residual)/(1-mu) for r, d in zip(residual, defect_rows)]
    total = [b/2+(n+1)**2*sum((v*s for v, s in zip(row, solved)), Q())
             for n, (b, row) in enumerate(zip(bias, inverse_cross))]
    positive = max(total[1:]) < Q(1, 2)
    radius2 = min((Q(1, 2)-total[n-1])**2*(1-qa)/n**4 for n in range(2, 51)) if positive else None
    passed = eta is not None and positive and (eta+XI)**2 < radius2
    if eta is not None and not passed:
        raise ValueError('declared strict integer-recovery guarantee failed')
    return {'degree': degree, 'inverse_cross_upper': [[str(x) for x in row] for row in inverse_cross],
            'schur_defect_upper': [[str(x) for x in row] for row in defect],
            'schur_infinity_defect': str(mu), 'augmented_gram_defect': str(qa),
            'schur_residual_upper': list(map(str, residual)), 'schur_solution_upper': list(map(str, solved)),
            'complete_coefficient_bias_upper': list(map(str, total)),
            'positive_rounding_margin': positive,
            'sufficient_total_noise_radius_squared': str(radius2) if radius2 is not None else None,
            'declared_sensor_radius': str(eta) if eta is not None else None,
            'rounding_certified': passed}


def build(precision=192, extended=False):
    if type(precision) is not int or precision < 128:
        raise ValueError('at least 128 bits required')
    preceding = old.check(precision)
    maximum = 12 if extended else 6
    degrees = [6, 8, 10, 12] if extended else [6]
    radii = ({'multi': ['1/10000', '1/10000', '99/1000000', '99/1000000'],
              'outer': ['8/100000', '8/100000', '8/100000', '79/1000000']} if extended else
             {'multi': ['1/10000'], 'outer': ['8/100000']})
    with ctx.workprec(precision):
        long = old.prior.base.weights(8900)
        short = [arb(0)]*8900
        short[3175:5725] = old.prior.base.weights(2550)
        mix = [old.prior.ball(old.prior.A0)*a+old.prior.ball(1-old.prior.A0)*b for a, b in zip(short, long)]
        zeta_interval = old.endpoint_interval(old.prior.ball(Q(3, 2)).zeta())
        remote = Q(zeta_interval[1])**14/(2*10**6)
        h0 = Q(preceding['full_pointwise_centered_tail_interval'][1])
        designs = {}
        for name, weights in [('multi', mix), ('outer', long)]:
            before = preceding['designs'][name]
            b = list(map(Q, before['original_complete_bias_upper']))
            qr = list(map(Q, before['original_gram_rows']))
            numeric = basis_and_channels(weights, maximum)
            old_numeric = before['physical_polynomial_reconstruction']
            if numeric['polynomial_coefficients'][:7] != old_numeric['polynomial_coefficients']:
                raise ValueError('the first six exact polynomial bases changed')
            if numeric['weighted_l1'][:6] != old_numeric['weighted_absolute_polynomial_norms']:
                raise ValueError('the first six complete weighted norms changed')
            if [row[:6] for row in numeric['cross_real_even_imaginary_odd']] != old_numeric['cross_channels_real_for_even_imaginary_for_odd']:
                raise ValueError('the inherited physical polynomial cross sums changed')
            cross = [[max(abs(Q(lo)), abs(Q(hi))) for lo, hi in row]
                     for row in numeric['cross_real_even_imaginary_odd']]
            l1 = [Q(hi) for lo, hi in numeric['weighted_l1']]
            differences = [Q(hi) for lo, hi in numeric['zero_extended_second_difference_l1']]
            finite = [h0*x/(DENOMINATOR_LOWER**2) for x in differences]
            distant = [remote*x for x in l1]
            channel = [a+b for a, b in zip(finite, distant)]
            coarse = [h0*x for x in l1]
            records = [consequences(b, qr, cross, channel, degree, Q(eta))
                       for degree, eta in zip(degrees, radii[name])]
            control = consequences(b, qr, cross, coarse, 6, None)
            if control['positive_rounding_margin']:
                raise ValueError('the declared old complete degree-six gate no longer fails')
            designs[name] = {'arithmetic_complete_bias_upper': list(map(str, b)),
                             'arithmetic_gram_rows': list(map(str, qr)),
                             'physical_polynomials': numeric,
                             'finite_oscillatory_channel_upper': list(map(str, finite)),
                             'complete_remote_channel_upper': list(map(str, distant)),
                             'complete_nuisance_channel_upper': list(map(str, channel)),
                             'old_pointwise_degree_six_control': control,
                             'degrees': records}
        return {'schema': 'oscillatory-polynomial-tail-v1', 'measurement_count': 8900,
                'known_a1': 1, 'maximum_constructed_degree': maximum,
                'tested_degrees': degrees, 'declared_sensor_radii': radii,
                'source': 'all integer 0<=a(n)<=d14(n); same exact physical times and W designs as predecessor',
                'digital_correction_radius': str(XI), 'phase_contract': phase_contract(),
                'zeta_three_halves_interval': zeta_interval,
                'complete_remote_centered_mass_upper': str(remote),
                'complete_pointwise_centered_mass_upper': str(h0),
                'predecessor_sha256': hashlib.sha256((PREVIOUS/'evidence.json').read_bytes()).hexdigest(),
                'predecessor_dependency_binding': preceding['dependency_binding'],
                'designs': designs}


def check(precision=192, extended=False):
    path = HERE/('evidence.json' if extended else 'core_evidence.json')
    document = json.loads(path.read_text())
    fresh = build(precision, extended)
    if fresh != document:
        raise ValueError('complete physical and oscillatory-channel replay differs')
    return fresh


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--extended', action='store_true')
    parser.add_argument('--precision', type=int, default=192)
    args = parser.parse_args()
    if args.write:
        path = HERE/('evidence.json' if args.extended else 'core_evidence.json')
        path.write_text(json.dumps(build(args.precision, args.extended), indent=2)+'\n')
    document = check(args.precision, args.extended)
    print('PASS: complete oscillatory polynomial nuisance channels')
    for name, design in document['designs'].items():
        for result in design['degrees']:
            print(name, result['degree'], 'eta', result['declared_sensor_radius'],
                  'max bias', float(max(map(Q, result['complete_coefficient_bias_upper'][1:]))))
