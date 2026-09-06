"""Independent outward, full-vector reconstruction of the noise extension.

No producer/checker is imported. Rebuilds weights from the original binary64
coefficient literals, performs weighted modified Gram--Schmidt on all 8,900
physical entries, differences twice including the zero extensions, and sums
both phase components. A rational integral-test zeta bound replaces the
producer's special-function tail constant. Inherited arithmetic B/q bounds and
the complete midpoint correction contract remain explicitly inherited.
"""
from pathlib import Path
from fractions import Fraction as Q
from math import isqrt, factorial
import argparse, ast, hashlib, json
from flint import arb, ctx, fmpq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRECISION = 320
ROUND = 10**15


def ball(x):
    x = Q(x)
    return arb(fmpq(x.numerator, x.denominator))


def dyadic(x):
    assert x.is_finite() and x.is_exact()
    m, e = map(int, x.man_exp())
    return Q(m*2**e) if e >= 0 else Q(m, 2**(-e))


def ceilq(x, scale=ROUND):
    x = Q(x)
    return Q(-((-x.numerator*scale)//x.denominator), scale)


def floorq(x, scale=ROUND):
    x = Q(x)
    return Q(x.numerator*scale//x.denominator, scale)


def upper(x):
    return ceilq(dyadic(x.upper()))


def sqrt_upper(x):
    x = Q(x)
    k = isqrt(x.numerator*10**40//x.denominator)
    return Q(k+1, 10**20)


def contains_enclosure(x, saved):
    lo, hi = map(Q, saved)
    assert dyadic(x.lower()) >= lo and dyadic(x.upper()) <= hi


def source_coefficients():
    tree = ast.parse((ROOT/'arithmetic_sensing_iv.py').read_text())
    entries = [node for node in tree.body if isinstance(node, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == 'REFERENCE_COEFFICIENTS'
                       for t in node.targets)]
    assert len(entries) == 1
    values = ast.literal_eval(entries[0].value.args[0])
    assert len(values) == 8 and all(type(x) is float for x in values)
    return [Q.from_float(x) for x in values]


def physical_weights(m, coefficients):
    result = []
    for j in range(m):
        angle = arb.pi()*ball(Q(2*j+1, m))
        value = (1+2*sum((ball(c)*(angle*k).cos()
                         for k, c in enumerate(coefficients, 1)), arb(0)))/m
        assert value > 0
        result.append(value)
    assert sum(result, arb(0)).contains(1)
    return result


def inner(a, b, weights):
    return sum((w*x*y for w, x, y in zip(weights, a, b)), arb(0))


def rational_tail_and_phase():
    # For decreasing t^(-3/2), the tail above 100 is at most integral_100^inf,
    # equal to 1/5. Each retained term is bounded by integer square roots.
    scale = 10**12
    terms = [Q(isqrt(scale*scale//n**3)+1, scale) for n in range(1, 101)]
    for n, a in enumerate(terms, 1):
        assert a*a*n**3 > 1
    zeta_bound = sum(terms, Q())+Q(1, 5)
    assert zeta_bound < Q(2613, 1000)
    remote = Q(2613, 1000)**14/(2*10**6)

    # Independent exponential truncation orders and exact tail sign checks.
    x = Q(39, 10)
    eu = sum((x**k/factorial(k) for k in range(64)), Q())
    eu += x**64/factorial(64)/(1-x/65)
    el = sum((Q(28)**k/factorial(k) for k in range(121)), Q())
    assert eu < 51 and el > 10**12
    sl = Q(39, 100)-Q(39, 100)**3/6
    sh = sum(((-1)**k*Q(14, 5)**(2*k+1)/factorial(2*k+1)
              for k in range(8)), Q())
    assert min(sl, sh) > Q(1, 3)
    # The first omitted sine term has positive sign; successive tail terms
    # decrease because this ratio is <1 and its denominator increases.
    assert Q(14, 5)**2/(18*19) < 1
    assert Q(39, 100)**2/(6*7) < 1
    # A finite exact adverse control: internal-only differences would fail.
    first = [Q(1)]+[Q(0)]*8+[Q(-1)]
    second = [first[0]]+[b-a for a, b in zip(first, first[1:])]+[-first[-1]]
    assert sum(map(abs, second), Q()) == 4
    assert sum(((-1)**j for j in range(9)), 0) == 1
    return remote, {'zeta_three_halves_upper_from_100_terms_and_integral': str(zeta_bound),
                    'simplified_zeta_upper': '2613/1000',
                    'independent_remote_mass_upper': str(remote),
                    'uniform_phase_band_proved': True,
                    'endpoint_omission_control': 'internal variation 0, complete 4, oscillatory sum 1'}


def physical_channels(weights, saved):
    m = len(weights)
    x = [ball(Q(2*j+1-m, 8900)) for j in range(m)]
    times = [ball(Q(2*j+1-m, 10)) for j in range(m)]
    basis = [[arb(1)]*m]
    l1, variation = [], []
    for degree in range(1, 13):
        residual = [t**degree for t in x]
        # Full-vector modified GS, unlike the producer's moment/monomial GS.
        for earlier in basis:
            projection = inner(residual, earlier, weights)
            residual = [a-projection*b for a, b in zip(residual, earlier)]
        norm2 = inner(residual, residual, weights)
        assert norm2 > 0
        norm = norm2.sqrt()
        psi = [a/norm for a in residual]
        assert inner(psi, psi, weights).contains(1)
        for earlier in basis:
            assert inner(psi, earlier, weights).contains(0)
        basis.append(psi)
        weighted = [w*p for w, p in zip(weights, psi)]
        ell = sum(map(abs, weighted), arb(0))
        # Two independent first-difference operations, both zero extended.
        first = [weighted[0]]+[b-a for a, b in zip(weighted, weighted[1:])]+[-weighted[-1]]
        second = [first[0]]+[b-a for a, b in zip(first, first[1:])]+[-first[-1]]
        assert len(second) == m+2
        assert sum(second, arb(0)).contains(0)
        assert sum((a*j for j, a in enumerate(second)), arb(0)).contains(0)
        v2 = sum(map(abs, second), arb(0))
        contains_enclosure(ell, saved['weighted_l1'][degree-1])
        contains_enclosure(v2, saved['zero_extended_second_difference_l1'][degree-1])
        l1.append(upper(ell))
        variation.append(upper(v2))
    # Both full physical phase components; symmetry is not used to sum them.
    cross = [[Q(0)]*12]
    for n in range(2, 51):
        logarithm = arb(n).log()
        cosines = [(t*logarithm).cos() for t in times]
        sines = [(t*logarithm).sin() for t in times]
        row = []
        for degree, psi in enumerate(basis[1:], 1):
            real = inner(psi, cosines, weights)
            imag = inner(psi, sines, weights)
            active, cancelled = (imag, real) if degree % 2 else (real, imag)
            assert cancelled.contains(0)
            assert abs(cancelled) < ball(Q(1, 10**40))
            contains_enclosure(active, saved['cross_real_even_imaginary_odd'][n-1][degree-1])
            row.append(upper(abs(active)))
        cross.append(row)
    return cross, l1, variation


def independent_gates(data, cross, channels):
    b = list(map(Q, data['arithmetic_complete_bias_upper']))
    qr = list(map(Q, data['arithmetic_gram_rows']))
    q = max(qr)
    assert 0 <= q < 1
    rows = []
    for record in data['degrees']:
        p = record['degree']
        columns = [max(row[k] for row in cross) for k in range(p)]
        v = [[cross[n][k]+qr[n]*columns[k]/(1-q) for k in range(p)] for n in range(50)]
        defect_rows = [sum((cross[n][k]*sum(v[n], Q()) for n in range(50)), Q()) for k in range(p)]
        mu = max(defect_rows)
        gram_defect = max([qr[n]+sum(cross[n][:p], Q()) for n in range(50)] +
                          [sum((cross[n][k] for n in range(50)), Q()) for k in range(p)])
        assert 0 <= mu < 1 and 0 <= gram_defect < 1
        residual = [channels[k]+sum((cross[n][k]*b[n]/(2*(n+1)**2)
                                    for n in range(50)), Q()) for k in range(p)]
        solution = [a+d*max(residual)/(1-mu) for a, d in zip(residual, defect_rows)]
        bias = [b[n]/2+(n+1)**2*sum((a*s for a, s in zip(v[n], solution)), Q()) for n in range(50)]
        floor = 1-gram_defect
        eta = Q(record['declared_sensor_radius'])
        rho, xi = Q(1, 10**8), Q(1, 10**20)
        slacks = []
        for n in range(2, 51):
            margin = Q(1, 2)-bias[n-1]-n*n*rho/floor
            assert margin > 0
            assert n**4*(eta+xi)**2 < margin*margin*floor
            slack = margin-n*n*(eta+xi)*sqrt_upper(1/floor)
            assert slack > 0
            slacks.append(slack)
        rows.append({'degree': p, 'sensor_radius': str(eta), 'normal_residual_radius': str(rho),
                     'maximum_bias_upper': str(ceilq(max(bias[1:]))),
                     'gram_floor_lower': str(floorq(floor)),
                     'minimum_rounding_slack_lower': str(floorq(min(slacks))),
                     'passed_coordinate_gates': 49})
    return rows


def audit():
    document = json.loads((HERE/'evidence.json').read_text())
    assert document['tested_degrees'] == [6, 8, 10, 12]
    inherited = json.loads((ROOT/'research/unified_query_2026_09/noise/evidence.json').read_text())
    assert hashlib.sha256((ROOT/'research/unified_query_2026_09/noise/evidence.json').read_bytes()).hexdigest() == document['predecessor_sha256']
    h0 = Q(document['complete_pointwise_centered_mass_upper'])
    assert h0 == Q(inherited['full_pointwise_centered_tail_interval'][1])
    remote, tail_report = rational_tail_and_phase()
    results = {}
    with ctx.workprec(PRECISION):
        coefficients = source_coefficients()
        outer = physical_weights(8900, coefficients)
        inner_window = physical_weights(2550, coefficients)
        inner_embedded = [arb(0)]*3175+inner_window+[arb(0)]*3175
        alpha = ball(Q(125, 65536))
        multi = [alpha*a+(1-alpha)*b for a, b in zip(inner_embedded, outer)]
        for name, weights in [('multi', multi), ('outer', outer)]:
            print('Reconstructing', name, 'full physical vectors at', PRECISION, 'bits', flush=True)
            data = document['designs'][name]
            assert data['arithmetic_complete_bias_upper'] == inherited['designs'][name]['original_complete_bias_upper']
            assert data['arithmetic_gram_rows'] == inherited['designs'][name]['original_gram_rows']
            cross, ell, v2 = physical_channels(weights, data['physical_polynomials'])
            channels = [Q(9, 4)*h0*v+remote*l for v, l in zip(v2, ell)]
            gates = independent_gates(data, cross, channels)
            results[name] = {'weighted_l1_upper': list(map(str, ell)),
                             'complete_second_difference_upper': list(map(str, v2)),
                             'cross_bounds_reconstructed': 49*12,
                             'complete_channel_upper': list(map(str, channels)),
                             'degrees': gates}
    paths = ['evidence.json', 'core_evidence.json', 'oscillatory_channels.py',
             'check_certificate.py', 'PROOFS.md', 'test_oscillatory.py', 'independent_audit.py']
    return {'verified': True, 'precision_bits': PRECISION,
            'physical_samples_per_design': 8900, 'independent_basis_degrees': 12,
            'arithmetic_polynomial_cross_entries_rebuilt': 1176,
            'zero_extended_differences_per_channel': 8902,
            'coordinate_gates_passed': 392, 'remote_and_phase': tail_report,
            'designs': results,
            'inherited_premises': ['unchanged complete arithmetic B_n and q_n bounds',
                                   'complete midpoint digital error Xi=1e-20', 'outward H0'],
            'not_claimed': ['original million-term arithmetic enumeration rerun',
                            'empirical noise validation', 'actual numerical residual certification'],
            'sha256': {p: hashlib.sha256((HERE/p).read_bytes()).hexdigest() for p in paths}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = audit()
    path = HERE/'independent_audit.json'
    if args.write:
        path.write_text(json.dumps(report, indent=2)+'\n')
    else:
        assert json.loads(path.read_text()) == report, 'independent audit evidence changed'
    print('PASS: independent full-vector audit and all 392 rounding gates')
