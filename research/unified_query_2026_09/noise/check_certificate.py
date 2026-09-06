"""Independent standard-library consumer of the numerical enclosures.

This checker imports neither the producer nor Arb. It checks each exact
Schur, full-tail and rounding consequence. The enclosure-to-physical-model
connection is independently replayed by polynomial_drift.py.
"""
from pathlib import Path
from fractions import Fraction as Q
from math import isqrt
import hashlib, json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
XI = Q(1, 10**20)
RADII = {
    'multi': ['97/1000000', '9/100000', '77/1000000', '53/1000000', '16/1000000', None],
    'outer': ['77/1000000', '7/100000', '57/1000000', '33/1000000', None, None],
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def interval(value):
    require(type(value) is list and len(value) == 2, 'bad interval shape')
    lo, hi = map(Q, value)
    require(lo <= hi, 'reversed rational interval')
    return lo, hi


def numbers(value, size):
    require(type(value) is list and len(value) == size, 'wrong vector dimension')
    return list(map(Q, value))


def sqrt_interval(value, digits=18):
    """An exact integer-squared enclosing interval; no floating point."""
    value = Q(value)
    require(value >= 0, 'negative square-root argument')
    scale = 10**digits
    low = isqrt(value.numerator*scale*scale//value.denominator)
    return Q(low, scale), Q(low+1, scale)


def check(document=None):
    if document is None:
        document = json.loads((HERE/'evidence.json').read_text())
    require(document['schema'] == 'polynomial-drift-certificate-v1', 'wrong schema')
    expected = {
        'schema': 'polynomial-drift-input-v1', 'known_a1': 1,
        'measurement_count': 8900,
        'time_formula': '(2*j+1-8900)/10, j=0,...,8899',
        'polynomial_coordinate': 'x=t/890',
        'source': 'integer 0<=a(k)<=d14(k), all k>=1',
        'nuisance': 'arbitrary complex polynomial of degree at most p',
        'maximum_explored_degree': 6, 'correction_radius': str(XI),
        'declared_sensor_radii': RADII,
    }
    require(document['inputs'] == expected, 'source or acquisition contract mismatch')
    require(set(document['designs']) == {'multi', 'outer'}, 'wrong design list')
    files = {
        'research/next15_2026_09/noise/cycle2_evidence.json',
        'research/next15_2026_09/noise/cycle2_correction.json',
        'certificates/arithmetic_sensing_v_multiscale_end_to_end.json',
        'certificates/arithmetic_sensing_v_multiscale_T1780_single_end_to_end.json',
    }
    require(set(document['premise_file_sha256']) == files, 'unexpected premise file')
    for path, digest in document['premise_file_sha256'].items():
        require(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest,
                'inherited premise identity mismatch')
    previous = json.loads((ROOT/'research/next15_2026_09/noise/cycle2_evidence.json').read_text())
    require(document['dependency_binding'] == previous['dependency_binding'], 'tail dependency mismatch')
    require(document['digital_correction_sha256'] == previous['correction_sha256'], 'correction binding mismatch')
    require(Q(previous['correction_error_strict_upper']) == XI, 'uncertified correction error')
    hlow, h0 = interval(document['full_pointwise_centered_tail_interval'])
    require(469 < hlow <= h0 < 470, 'complete envelope outside its recorded contract')
    summaries = {}
    for name, data in document['designs'].items():
        old = previous['designs'][name]
        b = numbers(data['original_complete_bias_upper'], 50)
        qrows = numbers(data['original_gram_rows'], 50)
        require(b == list(map(Q, old['complete_bias_upper'])), 'arithmetic full-tail premise changed')
        require(qrows == list(map(Q, old['gram_rows'])), 'arithmetic Gram premise changed')
        require(min(b+qrows) >= 0 and max(qrows) < 1, 'invalid arithmetic bounds')
        q = max(qrows)
        numeric = data['physical_polynomial_reconstruction']
        require(len(numeric['moments']) == 13, 'missing moments')
        moments = list(map(interval, numeric['moments']))
        require(moments[0] == (1, 1) and all(moments[k] == (0, 0) for k in range(1, 13, 2)),
                'mass or exact parity lost')
        require(len(numeric['polynomial_coefficients']) == 7, 'wrong basis dimension')
        for k, row in enumerate(numeric['polynomial_coefficients']):
            require(len(row) == k+1, 'wrong polynomial degree')
            coefficients = list(map(interval, row))
            require(all(coefficients[j] == (0, 0) for j in range(k+1) if (k-j) % 2),
                    'polynomial parity changed')
            require(coefficients[k][0] > 0, 'basis leading coefficient not positive')
        require(len(numeric['gram_schmidt_residual_norm_squared']) == 6, 'missing positive norms')
        require(all(interval(z)[0] > 0 for z in numeric['gram_schmidt_residual_norm_squared']),
                'polynomial positive norm unavailable')
        require(len(numeric['weighted_absolute_polynomial_norms']) == 6, 'missing L1 channel')
        l1 = [interval(z)[1] for z in numeric['weighted_absolute_polynomial_norms']]
        require(all(0 < a <= 1 for a in l1), 'invalid absolute polynomial norm')
        raw = numeric['cross_channels_real_for_even_imaginary_for_odd']
        require(len(raw) == 50 and all(len(row) == 6 for row in raw), 'wrong cross-channel dimension')
        c = [[max(map(abs, interval(z))) for z in row] for row in raw]
        require(c[0] == [0]*6, 'known constant polynomial alias incorrectly handled')
        require(len(data['degrees']) == 6, 'missing bounded-search degree')
        results = []
        for p, record in enumerate(data['degrees'], 1):
            require(record['degree'] == p, 'degree order mismatch')
            # Re-derive bounds from the numerical inputs, not saved outputs.
            v = [[c[n][k]+qrows[n]*max(row[k] for row in c)/(1-q)
                  for k in range(p)] for n in range(50)]
            defect = [[sum((c[n][i]*v[n][j] for n in range(50)), Q())
                       for j in range(p)] for i in range(p)]
            rows = [sum(row, Q()) for row in defect]
            mu = max(rows)
            qa = max([qrows[n]+sum(c[n][:p], Q()) for n in range(50)] +
                     [sum((row[k] for row in c), Q()) for k in range(p)])
            require(0 <= mu < 1 and 0 <= qa < 1, 'positive Schur or Gram floor missing')
            new_channels = [h0*a for a in l1[:p]]
            residual = [new_channels[k]+sum((c[n][k]*b[n]/(2*(n+1)**2)
                                             for n in range(50)), Q()) for k in range(p)]
            solution = [residual[k]+rows[k]*max(residual)/(1-mu) for k in range(p)]
            extra = [(n+1)**2*sum((v[n][k]*solution[k] for k in range(p)), Q()) for n in range(50)]
            total = [b0/2+e for b0, e in zip(b, extra)]
            matrices = {'inverse_cross_absolute_upper': v,
                        'schur_defect_matrix_absolute_upper': defect}
            vectors = {'complete_centered_nuisance_channels_upper': new_channels,
                       'schur_residual_channels_upper': residual,
                       'schur_solution_absolute_upper': solution,
                       'additional_decoded_bias_upper': extra,
                       'complete_decoded_bias_upper': total}
            for key, wanted in matrices.items():
                require(record[key] == [[str(a) for a in row] for row in wanted], key+' mismatch')
            for key, wanted in vectors.items():
                require(record[key] == list(map(str, wanted)), key+' mismatch')
            require(Q(record['schur_infinity_defect_upper']) == mu, 'Schur consequence mismatch')
            require(Q(record['augmented_gram_defect_upper']) == qa, 'Gram consequence mismatch')
            positive = max(total[1:]) < Q(1, 2)
            require(type(record['positive_rounding_margin']) is bool and
                    record['positive_rounding_margin'] == positive, 'positive-margin flag mismatch')
            eta = RADII[name][p-1]
            radius2 = min((Q(1, 2)-total[n-1])**2*(1-qa)/n**4
                          for n in range(2, 51)) if positive else None
            require(record['sufficient_total_radius_squared'] ==
                    (str(radius2) if radius2 is not None else None), 'strict radius consequence mismatch')
            require(record['declared_sensor_radius'] == (str(Q(eta)) if eta else None),
                    'declared radius mismatch')
            passed = positive and eta is not None and (Q(eta)+XI)**2 < radius2
            require(type(record['rounding_certified']) is bool and record['rounding_certified'] == passed,
                    'strict rounding claim mismatch')
            require(passed == (eta is not None), 'declared guarantee fails')
            require(record['status'] == ('certified' if passed else 'this sufficient complete-tail gate fails'),
                    'failure scope changed')
            # A negative margin is retained as a failure of this sufficient
            # bound, never squared into a false positive certificate.
            require(passed or not positive, 'unexplained omitted positive gate')
            radius_interval = ([str(a-XI) for a in sqrt_interval(radius2)] if positive else None)
            results.append({'degree': p, 'certified': passed,
                            'max_bias_upper': str(max(total[1:])),
                            'sensor_threshold_interval': radius_interval,
                            'declared_eta': eta})
        summaries[name] = results
    return summaries


if __name__ == '__main__':
    output = check()
    print('PASS: independent exact Schur, complete-tail and rounding consequence checker')
    for name, rows in output.items():
        for row in rows:
            print(name, 'degree', row['degree'], 'certified', row['certified'],
                  'threshold', row['sensor_threshold_interval'])
