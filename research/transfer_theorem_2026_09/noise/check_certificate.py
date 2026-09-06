"""Strict standard-library checker for complete oscillatory-tail consequences.

It imports no producer or interval library. Numerical enclosures are verified
against the physical model by the separate full reconstruction commands.
"""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial, isqrt
import argparse, hashlib, importlib.util, json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = ROOT/'research/unified_query_2026_09/noise'
XI = Q(1, 10**20)
NORMAL_RESIDUAL_RADIUS = Q(1, 10**8)


def require(value, message):
    if not value:
        raise ValueError(message)


def interval(value):
    require(type(value) is list and len(value) == 2, 'wrong interval shape')
    lo, hi = map(Q, value)
    require(lo <= hi, 'reversed interval')
    return lo, hi


def sqrt_interval(value):
    value = Q(value)
    require(value >= 0, 'negative square root')
    scale = 10**18
    k = isqrt(value.numerator*scale*scale//value.denominator)
    return Q(k, scale), Q(k+1, scale)


def phase_check(p):
    require(p['cutoff'] == 10**12 and p['difference_order'] == 2,
            'changed finite range or summation order')
    require(p['frequency_half_step_interval'] == ['39/100', '14/5'], 'frequency band changed')
    require(p['phase_denominator_strict_lower'] == '2/3', 'phase denominator changed')
    require(p['remote_exponent'] == '3/2' and p['square_root_cutoff'] == 10**6,
            'complete remote tail exponent changed')
    x = Q(39, 10)
    upper = sum((x**k/factorial(k) for k in range(101)), Q()) + x**101/factorial(101)/(1-x/102)
    lower = sum((Q(28)**k/factorial(k) for k in range(141)), Q())
    require(upper <= Q(p['exp_3_9_upper']) < 51, 'lower logarithm endpoint unproved')
    require(10**12 < Q(p['exp_28_lower']) <= lower, 'upper logarithm endpoint unproved')
    first = Q(39, 100)-Q(39, 100)**3/6
    second = sum(((-1)**k*Q(14, 5)**(2*k+1)/factorial(2*k+1) for k in range(8)), Q())
    require(Q(p['sin_0_39_lower']) == first > Q(1, 3), 'first sine bound false')
    require(Q(p['sin_2_8_lower']) == second > Q(1, 3), 'second sine bound false')


def normal_residual_budget(record, rho=NORMAL_RESIDUAL_RADIUS):
    """Conditional allowance for a *verified exact-model* normal residual.

    This is not a floating residual computation. The deployed residual must
    include all errors in evaluating the exact physical normal equations.
    """
    rho = Q(rho)
    require(rho >= 0, 'negative normal residual allowance')
    floor = 1-Q(record['augmented_gram_defect'])
    require(floor > 0, 'normal residual needs a positive exact Gram floor')
    eta = Q(record['declared_sensor_radius'])
    biases = list(map(Q, record['complete_coefficient_bias_upper']))
    require(len(biases) == 50, 'normal residual source dimension wrong')
    for n in range(2, 51):
        margin = Q(1, 2)-biases[n-1]-n*n*rho/floor
        require(margin > 0, 'normal residual consumes rounding margin')
        require(n**4*(eta+XI)**2 < margin*margin*floor,
                'joint sensor and normal residual gate fails')
    return {'verified': True, 'coordinate_gates': 49,
            'conditional_exact_normal_residual_radius': str(rho)}


def derive_and_check(record, b, qr, c, channels, p, eta):
    q = max(qr)
    require(0 <= q < 1, 'arithmetic Gram floor missing')
    C = [row[:p] for row in c]
    v = [[C[n][k]+qr[n]*max(row[k] for row in C)/(1-q)
          for k in range(p)] for n in range(50)]
    m = [[sum((C[n][i]*v[n][j] for n in range(50)), Q()) for j in range(p)] for i in range(p)]
    rows = [sum(row, Q()) for row in m]
    mu = max(rows)
    qa = max([qr[n]+sum(C[n], Q()) for n in range(50)] +
             [sum((row[k] for row in C), Q()) for k in range(p)])
    require(0 <= mu < 1 and 0 <= qa < 1, 'Schur or augmented Gram floor missing')
    r = [channels[k]+sum((C[n][k]*b[n]/(2*(n+1)**2) for n in range(50)), Q()) for k in range(p)]
    s = [r[k]+rows[k]*max(r)/(1-mu) for k in range(p)]
    total = [b[n]/2+(n+1)**2*sum((v[n][k]*s[k] for k in range(p)), Q()) for n in range(50)]
    require(record['degree'] == p, 'degree record mismatch')
    for key, matrix in [('inverse_cross_upper', v), ('schur_defect_upper', m)]:
        require(record[key] == [[str(x) for x in row] for row in matrix], key+' mismatch')
    for key, vector in [('schur_residual_upper', r), ('schur_solution_upper', s),
                        ('complete_coefficient_bias_upper', total)]:
        require(record[key] == list(map(str, vector)), key+' mismatch')
    require(Q(record['schur_infinity_defect']) == mu, 'Schur norm mismatch')
    require(Q(record['augmented_gram_defect']) == qa, 'Gram norm mismatch')
    positive = max(total[1:]) < Q(1, 2)
    require(type(record['positive_rounding_margin']) is bool and record['positive_rounding_margin'] == positive,
            'positive margin flag mismatch')
    r2 = min((Q(1, 2)-total[n-1])**2*(1-qa)/n**4 for n in range(2, 51)) if positive else None
    require(record['sufficient_total_noise_radius_squared'] == (str(r2) if r2 is not None else None),
            'noise radius consequence mismatch')
    passed = positive and eta is not None and (eta+XI)**2 < r2
    require(record['declared_sensor_radius'] == (str(eta) if eta is not None else None), 'noise budget changed')
    require(type(record['rounding_certified']) is bool and record['rounding_certified'] == passed,
            'rounding flag mismatch')
    require(eta is None or passed, 'declared recovery guarantee fails')
    return {'degree': p, 'certified': passed, 'maximum_bias_upper': str(max(total[1:])),
            'sensor_radius': str(eta) if eta is not None else None,
            'sensor_threshold_interval': [str(x-XI) for x in sqrt_interval(r2)] if positive else None}


def check(document=None, extended=False):
    if document is None:
        document = json.loads((HERE/('evidence.json' if extended else 'core_evidence.json')).read_text())
    require(document['schema'] == 'oscillatory-polynomial-tail-v1', 'schema mismatch')
    require(type(document['measurement_count']) is int and document['measurement_count'] == 8900,
            'acquisition changed')
    require(type(document['known_a1']) is int and document['known_a1'] == 1, 'normalization changed')
    require(document['source'] == 'all integer 0<=a(n)<=d14(n); same exact physical times and W designs as predecessor',
            'source class or metric changed')
    require(document['digital_correction_radius'] == str(XI), 'digital correction unbudgeted')
    maximum = 12 if extended else 6
    degrees = [6, 8, 10, 12] if extended else [6]
    radii = ({'multi': ['1/10000', '1/10000', '99/1000000', '99/1000000'],
              'outer': ['8/100000', '8/100000', '8/100000', '79/1000000']} if extended else
             {'multi': ['1/10000'], 'outer': ['8/100000']})
    require(document['maximum_constructed_degree'] == maximum and document['tested_degrees'] == degrees,
            'bounded exploration changed')
    require(document['declared_sensor_radii'] == radii, 'declared radius table changed')
    phase_check(document['phase_contract'])
    prior_bytes = (PRIOR/'evidence.json').read_bytes()
    require(hashlib.sha256(prior_bytes).hexdigest() == document['predecessor_sha256'], 'predecessor identity mismatch')
    before = json.loads(prior_bytes)
    spec = importlib.util.spec_from_file_location('_oscillatory_predecessor_consumer', PRIOR/'check_certificate.py')
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    verifier.check(before)
    require(document['predecessor_dependency_binding'] == before['dependency_binding'], 'tail binding changed')
    h0 = Q(document['complete_pointwise_centered_mass_upper'])
    require(h0 == Q(before['full_pointwise_centered_tail_interval'][1]), 'full centered mass changed')
    zlo, zhi = interval(document['zeta_three_halves_interval'])
    require(Q(26, 10) < zlo <= zhi < Q(27, 10), 'zeta enclosure contract invalid')
    remote = zhi**14/(2*10**6)
    require(Q(document['complete_remote_centered_mass_upper']) == remote, 'infinite remote mass consequence wrong')
    require(set(document['designs']) == {'multi', 'outer'}, 'design coverage wrong')
    summaries = {}
    for name, data in document['designs'].items():
        old_data = before['designs'][name]
        b = list(map(Q, data['arithmetic_complete_bias_upper']))
        qr = list(map(Q, data['arithmetic_gram_rows']))
        require(len(b) == len(qr) == 50 and min(b+qr) >= 0, 'invalid arithmetic vectors')
        require(b == list(map(Q, old_data['original_complete_bias_upper'])), 'complete arithmetic tail changed')
        require(qr == list(map(Q, old_data['original_gram_rows'])), 'arithmetic Gram changed')
        numeric = data['physical_polynomials']
        require(len(numeric['moments']) == 2*maximum+1, 'moment dimension wrong')
        require(numeric['moments'][0] == ['1', '1'], 'weight mass changed')
        require(all(numeric['moments'][k] == ['0', '0'] for k in range(1, 2*maximum+1, 2)), 'moment parity wrong')
        require(len(numeric['polynomial_coefficients']) == maximum+1, 'basis dimension wrong')
        for k, coefficients in enumerate(numeric['polynomial_coefficients']):
            require(len(coefficients) == k+1, 'polynomial degree wrong')
            values = list(map(interval, coefficients))
            require(values[k][0] > 0, 'positive leading coefficient missing')
            require(all(values[j] == (0, 0) for j in range(k+1) if (k-j) % 2), 'basis parity wrong')
        require(len(numeric['residual_norm_squared']) == maximum and
                all(interval(x)[0] > 0 for x in numeric['residual_norm_squared']), 'positive polynomial norms missing')
        require(len(numeric['weighted_l1']) == len(numeric['zero_extended_second_difference_l1']) == maximum,
                'incomplete oscillatory channels')
        ell = [interval(x)[1] for x in numeric['weighted_l1']]
        variation = [interval(x)[1] for x in numeric['zero_extended_second_difference_l1']]
        require(all(0 < x <= 1 for x in ell) and min(variation) >= 0, 'invalid polynomial norm bounds')
        raw = numeric['cross_real_even_imaginary_odd']
        require(len(raw) == 50 and all(len(row) == maximum for row in raw), 'cross-channel dimensions wrong')
        c = [[max(map(abs, interval(x))) for x in row] for row in raw]
        require(c[0] == [0]*maximum, 'constant alias incorrectly handled')
        old_numeric = old_data['physical_polynomial_reconstruction']
        require(numeric['polynomial_coefficients'][:7] == old_numeric['polynomial_coefficients'], 'inherited bases changed')
        require(numeric['weighted_l1'][:6] == old_numeric['weighted_absolute_polynomial_norms'], 'inherited L1 norms changed')
        require([row[:6] for row in raw] == old_numeric['cross_channels_real_for_even_imaginary_for_odd'],
                'inherited physical cross terms changed')
        finite = [Q(9, 4)*h0*x for x in variation]
        distant = [remote*x for x in ell]
        channel = [a+b for a, b in zip(finite, distant)]
        for key, vector in [('finite_oscillatory_channel_upper', finite),
                            ('complete_remote_channel_upper', distant),
                            ('complete_nuisance_channel_upper', channel)]:
            require(data[key] == list(map(str, vector)), key+' mismatch')
        control = derive_and_check(data['old_pointwise_degree_six_control'], b, qr, c, [h0*x for x in ell], 6, None)
        require(not control['certified'] and Q(control['maximum_bias_upper']) >= Q(1, 2),
                'old sufficient obstruction not reproduced')
        require(data['old_pointwise_degree_six_control']['complete_coefficient_bias_upper'] ==
                old_data['degrees'][5]['complete_decoded_bias_upper'], 'old degree-six comparison changed')
        require(len(data['degrees']) == len(degrees), 'missing final degree cases')
        summaries[name] = [derive_and_check(row, b, qr, c, channel, p, Q(eta))
                           for row, p, eta in zip(data['degrees'], degrees, radii[name])]
        for row in data['degrees']:
            normal_residual_budget(row)
    return {'verified': True, 'physical_readings': 8900, 'designs': summaries,
            'conditional_exact_normal_residual_radius': str(NORMAL_RESIDUAL_RADIUS),
            'complete_tail_contract': 'finite uniform oscillatory bound plus all coefficients above 10^12'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--extended', action='store_true')
    args = parser.parse_args()
    result = check(extended=args.extended)
    print('PASS: complete oscillatory-tail and exact Schur/rounding consequences')
    for name, rows in result['designs'].items():
        for row in rows:
            print(name, 'degree', row['degree'], 'eta', row['sensor_radius'],
                  'maximum bias upper (display)', float(Q(row['maximum_bias_upper'])),
                  'threshold interval (display)', [float(Q(x)) for x in row['sensor_threshold_interval']])
