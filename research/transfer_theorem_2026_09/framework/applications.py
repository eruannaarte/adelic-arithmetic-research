"""Bind the common transfer gates to separately verified model certificates."""
from pathlib import Path
from fractions import Fraction as F
import importlib.util
import json
import sys
from transfer import (scalar_boundary_squared, strict_scalar_gate,
                      normal_residual_error_bound, pair_gate, inverse_gate)

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parents[1]
PREVIOUS = ROOT/'research/unified_query_2026_09'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def need(condition, message):
    if not condition:
        raise ValueError(message)


def recover_previous():
    counts = {'quadratic_pairs': 0, 'polynomial_coordinates': 0, 'preparation_rows': 0}
    joint = load('_transfer_previous_joint', PREVIOUS/'quadratic/joint_query.py')
    qc = json.loads((PREVIOUS/'quadratic/certificate.json').read_text())
    joint.check(qc)
    q = F(qc['gram_q'])
    for anchor in qc['strata']:
        for pair in anchor['pairs']:
            s, h = F(pair['squared_distance']), F(pair['tail_support'])
            bound = scalar_boundary_squared(s, 2*h, s/(1-q))['boundary_squared']
            need(bound == F(pair['radius_squared_sufficient']), 'quadratic transfer differs')
            counts['quadratic_pairs'] += 1

    polynomial = load('_transfer_previous_polynomial', PREVIOUS/'noise/check_certificate.py')
    nc = json.loads((PREVIOUS/'noise/evidence.json').read_text())
    polynomial.check(nc)
    xi = F(nc['inputs']['correction_radius'])
    for design in nc['designs'].values():
        for entry in design['degrees']:
            if not entry['rounding_certified']:
                continue
            eta = F(entry['declared_sensor_radius'])
            q = F(entry['augmented_gram_defect_upper'])
            bounds = []
            for n in range(2, 51):
                h = F(entry['complete_decoded_bias_upper'][n-1])
                gain2 = F(n**4)/(1-q)
                need(strict_scalar_gate(1, 2*h, gain2, eta+xi), 'polynomial total-error gate fails')
                bounds.append(scalar_boundary_squared(1, 2*h, gain2)['boundary_squared'])
                counts['polynomial_coordinates'] += 1
            need(min(bounds) == F(entry['sufficient_total_radius_squared']), 'polynomial boundary differs')

    calibration = load('_transfer_previous_calibration', PREVIOUS/'preparation/calibration_bridge.py')
    pc = calibration.verify_saved()
    target = F(pc['record']['target_diameter'])
    eta = F(pc['record']['readout_noise_radius'])
    local = list(map(F, pc['local_uncertainty_radii']))
    shared = list(map(F, pc['shared_systematic_radii']))
    thresholds = []
    for row in range(3):
        k = F(pc['row_contraction'][row])
        gain = F(pc['weighted_noise_gains'][row])
        h = sum((F(g)*r for g, r in zip(pc['local_projected_gains'][row], local)), F())
        h += sum((F(g)*r for g, r in zip(pc['shared_projected_gains'][row], shared)), F())
        need(0 <= k < 1, 'nonlinear variational premise fails')
        boundary = scalar_boundary_squared(target*(1-k), 2*h, gain*gain)['boundary_squared']
        # Diameter uses a non-strict endpoint; this recorded fixture is interior.
        need(eta*eta < boundary, 'calibration interior gate fails')
        limit = (target*(1-k)/2-h)/gain
        need(limit*limit == boundary, 'calibration transfer differs')
        thresholds.append(limit)
        counts['preparation_rows'] += 1
    need(min(thresholds) == F(pc['maximum_weighted_readout_noise_radius']), 'calibration boundary differs')
    need(counts == {'quadratic_pairs': 243, 'polynomial_coordinates': 441, 'preparation_rows': 3},
         'previous-model coverage incomplete')
    return {'passed': True, 'models': 3, 'scalar_gates': sum(counts.values()), **counts}


def check_new_noise(extended=False):
    folder = PACKAGE/'noise'
    consumer = load('_transfer_new_oscillatory', folder/'check_certificate.py')
    doc = json.loads((folder/('evidence.json' if extended else 'core_evidence.json')).read_text())
    checked = consumer.check(doc, extended=extended)
    xi = F(doc['digital_correction_radius'])
    rho = F(checked['conditional_exact_normal_residual_radius'])
    gates, residual_gates, cases = 0, 0, []
    for design, records in doc['designs'].items():
        for entry in records['degrees']:
            need(entry['rounding_certified'], 'new declared design is not certified')
            eta = F(entry['declared_sensor_radius'])
            q = F(entry['augmented_gram_defect'])
            bounds = []
            for n in range(2, 51):
                h = F(entry['complete_coefficient_bias_upper'][n-1])
                gain2 = F(n**4)/(1-q)
                need(strict_scalar_gate(1, 2*h, gain2, eta+xi), 'new full-tail scalar transfer fails')
                bounds.append(scalar_boundary_squared(1, 2*h, gain2)['boundary_squared'])
                gates += 1
                solve_error = n*n*normal_residual_error_bound(1-q, rho)
                need(strict_scalar_gate(1, 2*(h+solve_error), gain2, eta+xi),
                     'new jointly budgeted normal-residual transfer fails')
                residual_gates += 1
            need(min(bounds) == F(entry['sufficient_total_noise_radius_squared']),
                 'new noise boundary differs')
            cases.append({'design': design, 'degree': entry['degree'], 'sensor_radius': str(eta)})
    return {'passed': True, 'scalar_gates': gates, 'design_degrees': cases,
            'additional_conditional_normal_residual_gates': residual_gates,
            'conditional_normal_residual_radius': str(rho),
            'complete_tail_consequences_checked': True,
            'solve_contract': 'exact solve, or a verified exact-model normal residual within the declared radius'}


def check_new_resolution():
    folder = PACKAGE/'resolution'
    consumer = load('_transfer_new_resolution', folder/'check.py')
    doc = json.loads((folder/'certificate.json').read_text())
    checked = consumer.check(doc)
    need(checked['all_case_covers_verified'] and checked['individual_cases'] == 21
         and checked['pair_cases'] == 210, 'spatial full-source/time coverage incomplete')
    alpha = F(doc['normalization_lower'])
    individual = alpha*alpha*F(doc['unnormalized_source_floor'])
    pair = alpha*alpha*F(doc['unnormalized_pair_floor'])
    rho = F(doc['operator_model_error_upper'])
    numerical = F(1, 10**9)
    contracts = []
    for name in doc['source_metrics']:
        factor = F(1) if name == 'L2' else F(doc['H1_metric_upper'])
        sensor = F(3, 10**7) if name == 'L2' else F(3, 10**8)
        total = sensor+rho+numerical
        need(pair_gate(pair/factor, total, total), 'spatial label transfer fails')
        need(inverse_gate(individual/factor, total, F(962, 10**6)),
             'spatial source transfer fails at the sharpened reporting bound')
        old = checked['metrics'][name]
        need(F(old['total_relative_radius']) == total
             and F(old['pair_approximate_map_floor']) == pair/factor
             and F(old['individual_approximate_map_floor']) == individual/factor,
             'spatial normalization/metric interface differs')
        contracts.append({'source_metric': name, 'sensor_relative_radius': str(sensor),
                          'model_relative_radius': str(rho),
                          'conditional_computed_data_relative_radius': str(numerical),
                          'total_relative_radius': str(total),
                          'pair_floor': str(pair/factor), 'individual_floor': str(individual/factor),
                          'strict_source_error_upper': '481/500000',
                          'label_gate_passed': True, 'source_gate_passed': True})
    return {'passed': True, 'direct_rows': checked['direct_rows'],
            'individual_cases': 21, 'pair_cases': 210,
            'whole_cell_records': checked['whole_cell_records'],
            'metric_contracts': contracts,
            'scope': 'common pair and inverse theorem after the complete spatial consumer; exact inverse or additional certified solve error required'}


def check(include_new_noise=False, extended_noise=False, include_resolution=False):
    result = {'previous': recover_previous()}
    if include_new_noise:
        result['new_noise'] = check_new_noise(extended_noise)
    if include_resolution:
        result['new_resolution'] = check_new_resolution()
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--new-noise', action='store_true')
    parser.add_argument('--extended-noise', action='store_true')
    parser.add_argument('--resolution', action='store_true')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = check(args.new_noise or args.extended_noise or args.all,
                   args.extended_noise or args.all, args.resolution or args.all)
    if args.write:
        (HERE/'applications.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
