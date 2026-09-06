"""Common gates with explicit timing/mismatch charges in both physical models.

Physical kernel, complete-tail, weighted-moment, and normal-residual replays
are separate premises. This adapter binds those artifacts and checks their
consequences; it does not replace the model reconstruction consumers.
"""
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import argparse, hashlib, json
from uncertainty import spatial_gate, arithmetic_gate, prior

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = HERE.parents[2]
inputs = {}


def read(path):
    inputs[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return json.loads(path.read_text())


def need(condition, message):
    if not condition:
        raise ValueError(message)


def spatial():
    cert = read(PACKAGE/'resolution/certificate_7.json')
    checked = read(PACKAGE/'resolution/checked_7.json')
    timing = read(PACKAGE/'resolution/timing.json')
    gamma = Q(cert['center_singular_lower'])
    count = 0
    for cell in cert['cells']:
        for record in cell['records']:
            source = len(record['case']) == 1
            floor = Q(cert['unnormalized_source_floor' if source else 'unnormalized_pair_floor'])
            r2 = sum((Q(a)**2 for row in record['preconditioner'] for a in row), Q(0))
            e = Q(record['variation_frobenius_upper'])
            need(prior.continuous_cell_gate(gamma**2, e, floor*r2), 'common whole-cell transfer failed')
            count += 1
    need(count == checked['whole_cell_records'] == 3743, 'spatial record count')
    profiles = {}
    for name, p in timing['profiles'].items():
        gate = spatial_gate(p['approximate_source_floor'], p['approximate_pair_floor'],
            p['sensor_relative_radius'], p['operator_approximation_relative_radius'],
            p['normalization_relative_radius'], p['maximum_absolute_clock_error'],
            p['forward_time_lipschitz_upper'], p['generator_perturbation_operator_norm_upper'])
        need(gate['passed'], 'common uncertain spatial transfer failed')
        need(Q(gate['total_radius']) == Q(p['total_relative_radius']), 'spatial total budget')
        need(Q(gate['source_error_squared_upper']) == Q(p['source_relative_error_squared_upper']), 'source bound')
        profiles[name] = gate
    return {'whole_cell_transfer_gates':count, 'global_profile_gates':2*len(profiles),
            'profiles':profiles, 'direct_rows':checked['direct_rows']}


def family_factor(record, frequency):
    # Reconstruct the parity bound from the verified rational approximants.
    p = record['degree']
    residuals = {r['order']:Q(r['weighted_residual_norm_upper']) for r in record['approximants']}
    need(sorted(residuals) == list(range(p+1,33)), 'weighted approximation order coverage')
    moments = {int(k):Q(v) for k,v in record['weighted_monomial_norm_upper'].items()}
    sums = []
    for start, tail in ((p+1,33),(p+2,34)):
        sums.append(sum((residuals[k]*frequency**k/factorial(k)
                         for k in range(start,33,2)), Q(0))
                    +moments[tail]*frequency**tail/factorial(tail))
    return max(sums)


def arithmetic():
    approximation = read(PACKAGE/'noise/approximation.json')
    tail = read(ROOT/'research/transfer_theorem_2026_09/noise/evidence.json')
    fixture = read(PACKAGE/'noise/data.json')
    replay = read(PACKAGE/'noise/precision_replay.json')
    need(replay['verified'] and replay['saved_exact_proposals_reverified'] and replay['bits'] == 384,
         'actual arithmetic replay premise')
    clock = approximation['clock_and_derivative']
    epsa, epsb = Q(clock['clock_slope_radius']), Q(clock['clock_offset_radius'])
    tau = Q(clock['complete_signal_derivative_upper'])*(890*epsa+epsb)
    need(tau == Q(clock['complete_clock_distortion_radius']), 'complete clock budget')
    need(Q(fixture['true_clock_slope'])-1 == epsa and Q(fixture['true_clock_offset']) == epsb,
         'actual affine clock fixture')
    rows = []
    for design in ('multi','outer'):
        for degree in (6,8,10,12):
            result = read(PACKAGE/f'noise/result_{design}_{degree}.json')
            receipt = result['certificate']
            record = next(r for r in approximation['records'] if (r['design'],r['degree']) == (design,degree))
            old = next(r for r in tail['designs'][design]['degrees'] if r['degree'] == degree)
            f = 1-Q(old['augmented_gram_defect'])
            need(Q(receipt['gram_floor']) == f > 0, 'arithmetic Gram floor')
            rho = Q(receipt['normal_residual_upper'])
            need(0 <= rho < Q(1,10**30), 'actual residual must meet future planning ceiling')
            nu = Q(fixture['sinusoid_amplitude'])*family_factor(record,(1+epsa)*Q(fixture['sinusoid_frequency']))
            kappa = Q(approximation['mismatch_radius'])
            eta = Q(approximation['sensor_radius'])
            xi = Q(tail['digital_correction_radius'])
            need(Q(receipt['nonpolynomial_drift_radius']) == nu+tau+kappa, 'arithmetic uncertainty double-count/omission')
            need(Q(receipt['joint_data_error_radius']) == eta+nu+tau+kappa+xi, 'arithmetic total budget')
            gates = []
            for n in range(2,51):
                bias = Q(old['complete_coefficient_bias_upper'][n-1])
                g = arithmetic_gate(n,bias,f,rho,eta,nu,tau,kappa,xi)
                # Independently use the predecessor's directional scalar form.
                support = 2*(bias+n*n*rho/f)
                scalar = prior.strict_scalar_gate(1,support,Q(n**4)/f,eta+nu+tau+kappa+xi)
                need(g['passed'] == scalar, 'general support gate disagrees with integer gate')
                gates.append(g)
            passed = sum(g['passed'] for g in gates)
            need(passed == result['uncertainty_budget']['passing_gates'], 'actual coefficient count')
            need((passed == 49) == (degree == 12), 'actual positive/adverse comparison changed')
            if passed == 49:
                need(receipt['answer_a1_through_a50'] == fixture['truth_a1_through_a50'], 'actual integer recovery')
            rows.append({'design':design,'degree':degree,'evaluated':49,'passed':passed,
                         'clock_radius':str(tau),'mismatch_radius':str(kappa),'family_radius':str(nu),
                         'normal_residual_upper':str(rho)})
    return {'evaluated_integer_gates':sum(r['evaluated'] for r in rows),
            'passing_integer_gates':sum(r['passed'] for r in rows),
            'complete_unknown_integer_recoveries':2,'rows':rows,
            'failed_gates_mean': 'Failure of this sufficient enclosure, not physical impossibility.'}


def raw_packets():
    doc = read(PACKAGE/'framework/raw_results.json')
    fixture = read(PACKAGE/'resolution/fixtures.json')
    need(len(doc['cases']) == len(fixture['cases']) == 12, 'raw case count')
    for c, physical in zip(doc['cases'],fixture['cases']):
        answer = c['answer']
        need(answer['status'] == 'unique' and answer['feasible_targets'] == [physical['source_label']], 'raw answer')
        t = Q(answer['nominal_time'])
        lo,hi = map(Q,answer['actual_time_interval'])
        need(lo <= Q(physical['true_time']) <= hi and 1 <= lo <= t <= hi <= 2, 'actual clock not covered')
        scale = answer['normalization']['scale']
        need(Q(scale['time']) == t, 'normalization nominal time differs')
        r,e = Q(scale['inverse_normalization']),Q(scale['relative_multiplier_error_upper'])
        need(0 <= e < 1 and (1-e)**4 <= (1+t)*r**4 <= (1+e)**4, 'raw quartic certificate')
        eta = Q(scale['sensor_relative_radius'])
        processing = e*(Q(4,3)+eta)
        need(processing == Q(scale['charged_physical_relative_radius']), 'raw source-gain charge')
        budget = answer['transfer_budget']
        check = spatial_gate(budget['source_floor'], budget['pair_floor'], eta,
            budget['approximation'], processing, max(t-lo,hi-t),'37/1000',
            answer['generator_perturbation_operator_norm_upper'])
        need(check == budget and check['passed'], 'raw transfer budget')
        need(Q(c['actual_relative_source_error_squared']) <= Q(check['source_error_squared_upper']), 'raw inverse enclosure')
    return {'actual_raw_packets':12,'actual_inverse_enclosures':12}


def build():
    inputs.clear()
    result = {'verified':True,'spatial':spatial(),'arithmetic':arithmetic(),'raw':raw_packets(),
              'premise': 'Full-time, physical-model, complete-tail and actual residual consumers are documented separately.'}
    result['input_sha256'] = dict(inputs)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--write',action='store_true'); args = parser.parse_args()
    result = build()
    if args.write:
        (HERE/'applications.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'input_sha256'},indent=2))
