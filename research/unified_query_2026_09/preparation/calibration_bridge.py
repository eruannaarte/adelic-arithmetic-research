"""Exact bridge from joint launch-calibration intervals to query guarantees."""
from fractions import Fraction as Q
from pathlib import Path
from functools import lru_cache
import argparse
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parents[1] / 'next15_2026_09' / 'preparation'
# The preserved verifier is read-only. Its own helper imports must resolve to
# its directory; this standalone entry point runs in an isolated process.
sys.path.insert(0, str(PRIOR))
import checker as ch
import synthesize as old_synthesis

COORDINATES = ['theta1', 'theta2', 'scaled_omega1', 'scaled_omega2']
UNITS = ['radian', 'radian', 'dimensionless physical-time angular velocity', 'dimensionless physical-time angular velocity']
NOMINAL = {'A': [Q(4, 5), Q(-7, 20), Q(0), Q(0)], 'B': [Q(-3, 5), Q(9, 10), Q(0), Q(0)]}
CONTRACT = {'source_coordinates': ['log(m2/m1)', 'log(l2/l1)', 'epsilon'],
            'clock': 'one epsilon shared globally; actual dimensionless time exp(epsilon)*tau',
            'velocity': 'sqrt(l1/g)*dtheta/dt_physical; not dtheta/dtau_nominal',
            'angles': 'unwrapped around the literal nominal launches',
            'correction_equation': 'true initial state = measured initial state + shared systematic + launch residual',
            'scope': 'one A launch and one B launch; every reading in a group uses that same preparation'}


def exact(v):
    if type(v) is not str:
        raise ValueError('exact rational strings required; floats are not accepted')
    return Q(v)


def interval(v):
    if not isinstance(v, list) or len(v) != 2:
        raise ValueError('two exact endpoints required')
    lo, hi = map(exact, v)
    if lo > hi:
        raise ValueError('reversed support interval')
    return lo, hi


def keys(obj, expected):
    if not isinstance(obj, dict) or set(obj) != set(expected):
        raise ValueError('strict object schema mismatch')


def encode(obj):
    return ch.encode(obj)


def frozen_sources():
    names = ['cycle2_region.json', 'nominal.json', 'cycle2_certificate.json']
    raw = tuple((PRIOR / name).read_bytes() for name in names)
    return raw, {name: hashlib.sha256(data).hexdigest() for name, data in zip(names, raw)}


@lru_cache(maxsize=4)
def _validate_source_bytes(raw):
    report, nominal, decoders = [json.loads(data) for data in raw]
    old_synthesis.verify(report, nominal, decoders)
    if Q(report['parameter_box_radius']) != Q(1, 10000) or Q(report['preparation_box_radius']) != Q(1, 100000):
        raise ValueError('frozen outer source or preparation model changed')
    return True


def verified_sources(raw):
    _validate_source_bytes(raw)
    # Never expose cached mutable scientific data to a caller.
    return tuple(json.loads(data) for data in raw)


def ingredients(design):
    raw, hashes = frozen_sources()
    report, nominal, decoders = verified_sources(raw)
    if design not in ('selected_AB', 'uniform_AB'):
        raise ValueError('this bridge requires the frozen A+B experiment')
    d = ch.ingredients(report, nominal, ch.DESIGNS[design], decoders['designs'][design]['ingredients']['b'])
    # Keep signs through both the within-launch projection and the common
    # calibration instrument's cross-launch column sum.
    signed = [[ch.sum_intervals([ch.scale(d['b'][i][k], ch.iv(report['rows'][j]['preparation_jacobian'][a]))
                                for k, j in enumerate(d['indices']) if ch.GROUPS[j] == g])
               for g in (0, 1) for a in range(4)] for i in range(3)]
    local = [[ch.maxabs(v) for v in row] for row in signed]
    shared = [[ch.maxabs(ch.add(row[a], row[a + 4])) for a in range(4)] for row in signed]
    if local != [row[:8] for row in d['H']]:
        raise ValueError('preparation-column reconstruction mismatch')
    return d, local, shared, hashes


def validate_record(record):
    keys(record, ['schema', 'evidence_kind', 'experiment_id', 'design', 'source_radius', 'target_diameter',
                  'readout_noise_radius', 'source_contract', 'coordinates', 'units', 'shared_systematic',
                  'shared_systematic_evidence', 'operating_assumptions_evidence', 'launches'])
    if record['schema'] != 'joint-launch-calibration-v1' or record['evidence_kind'] not in ('synthetic_fixture', 'physical_record'):
        raise ValueError('unrecognized schema or evidence kind')
    if type(record['experiment_id']) is not str or not record['experiment_id'].strip():
        raise ValueError('nonempty experiment identifier required')
    if record['source_contract'] != CONTRACT or record['coordinates'] != COORDINATES or record['units'] != UNITS:
        raise ValueError('coordinate, clock, unit, or correlation contract mismatch')
    if exact(record['source_radius']) != Q(1, 10000):
        raise ValueError('source must remain in the inherited validated box')
    delta, eta = exact(record['target_diameter']), exact(record['readout_noise_radius'])
    if delta <= 0 or eta < 0:
        raise ValueError('invalid target or readout-noise radius')
    if type(record['shared_systematic_evidence']) is not str or not record['shared_systematic_evidence'].strip():
        raise ValueError('systematic-support evidence reference required')
    keys(record['operating_assumptions_evidence'], ['source_box', 'readout_noise', 'model', 'time_and_velocity_reference'])
    if any(type(v) is not str or not v.strip() for v in record['operating_assumptions_evidence'].values()):
        raise ValueError('operating-assumption evidence references required')
    if not isinstance(record['shared_systematic'], list) or len(record['shared_systematic']) != 4:
        raise ValueError('four shared systematic correction intervals required')
    shared = [interval(v) for v in record['shared_systematic']]
    keys(record['launches'], ['A', 'B'])
    centers, local_radii, absolute_extents, measurements, ids = [], [], [], [], []
    sigma = [(hi - lo) / 2 for lo, hi in shared]
    shared_mid = [(lo + hi) / 2 for lo, hi in shared]
    for g in ('A', 'B'):
        launch = record['launches'][g]
        keys(launch, ['launch_id', 'measured_initial_state', 'local_residual_intervals',
                      'same_preparation_for_all_readings', 'evidence_reference'])
        if launch['same_preparation_for_all_readings'] is not True:
            raise ValueError('re-preparation between readings changes the certified model')
        if any(type(launch[k]) is not str or not launch[k].strip() for k in ('launch_id', 'evidence_reference')):
            raise ValueError('launch identifier and evidence reference required')
        ids.append(launch['launch_id'])
        if (not isinstance(launch['measured_initial_state'], list)
                or not isinstance(launch['local_residual_intervals'], list)
                or len(launch['measured_initial_state']) != 4 or len(launch['local_residual_intervals']) != 4):
            raise ValueError('four measured states and local intervals required')
        obs = list(map(exact, launch['measured_initial_state']))
        residual = [interval(v) for v in launch['local_residual_intervals']]
        for j, (z, (lo, hi)) in enumerate(zip(obs, residual)):
            center = z - NOMINAL[g][j] + shared_mid[j] + (lo + hi) / 2
            radius = (hi - lo) / 2
            centers.append(center)
            local_radii.append(radius)
            absolute_extents.append(abs(center) + radius + sigma[j])
        measurements.append(obs)
    if len(set(ids)) != 2:
        raise ValueError('the A and B launches need distinct identifiers')
    return delta, eta, centers, local_radii, sigma, absolute_extents


def assess(record, require=True):
    delta, eta, centers, radii, sigma, extents = validate_record(record)
    d, H, C, hashes = ingredients(record['design'])
    cap = Q(1, 100000)
    if max(extents) > cap:
        raise ValueError('calibrated support leaves the validated outer preparation box')
    k = [sum(row, Q()) for row in d['R']]
    if max(k) >= 1:
        raise ValueError('source decoder is not contractive')
    h = [sum((a * b for a, b in zip(row, radii)), Q()) + sum((a * b for a, b in zip(common, sigma)), Q()) for row, common in zip(H, C)]
    local_plus_independent = [radii[j] + sigma[j % 4] for j in range(8)]
    h_independent = [sum((a * b for a, b in zip(row, local_plus_independent)), Q()) for row in H]
    h_zero_center = [sum((a * b for a, b in zip(row, extents)), Q()) for row in H]
    lhs = [delta * a + 2 * b + 2 * eta * c for a, b, c in zip(k, h, d['noise'])]
    slack = [delta - v for v in lhs]
    passes = min(slack) >= 0
    if require and not passes:
        raise ValueError('joint preparation/readout-noise certificate exceeds target')
    diam = max(2 * (b + eta * c) / (1 - a) for a, b, c in zip(k, h, d['noise']))
    noise_limit = min((delta * (1 - a) / 2 - b) / c for a, b, c in zip(k, h, d['noise']))
    independent_lhs = [delta * a + 2 * b + 2 * eta * c for a, b, c in zip(k, h_independent, d['noise'])]
    zero_lhs = [delta * a + 2 * b + 2 * eta * c for a, b, c in zip(k, h_zero_center, d['noise'])]
    return encode({'schema': 'joint-launch-calibration-result-v1', 'record': record, 'prior_artifact_hashes': hashes,
                   'mathematical_contract_passes': passes,
                   'physical_validation': 'NOT_RUN' if record['evidence_kind'] == 'synthetic_fixture' else 'REQUIRES_EXTERNAL_PROVENANCE_AND_MODEL_VALIDATION',
                   'preparation_centers': centers, 'local_uncertainty_radii': radii,
                   'shared_systematic_radii': sigma, 'absolute_outer_extents': extents,
                   'row_contraction': k, 'local_projected_gains': H, 'shared_projected_gains': C,
                   'weighted_noise_gains': d['noise'], 'row_lhs': lhs, 'row_slack': slack,
                   'query_source_diameter_bound': diam, 'maximum_weighted_readout_noise_radius': noise_limit,
                   'independent_systematic_control_row_lhs': independent_lhs,
                   'zero_center_envelope_control_row_lhs': zero_lhs,
                   'zero_center_envelope_control_passes': all(v <= delta for v in zero_lhs)})


def verify_saved():
    record = json.loads((HERE / 'synthetic_calibration.json').read_text())
    fresh = assess(record)
    if fresh != json.loads((HERE / 'certificate.json').read_text()):
        raise ValueError('complete calibration consequence replay mismatch')
    return fresh


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', type=Path)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.write:
        record = json.loads((HERE / 'synthetic_calibration.json').read_text())
        (HERE / 'certificate.json').write_text(json.dumps(assess(record), indent=2) + '\n')
    out = assess(json.loads(args.record.read_text())) if args.record else verify_saved()
    print(json.dumps({k: out[k] for k in ('mathematical_contract_passes', 'physical_validation',
                                         'query_source_diameter_bound', 'maximum_weighted_readout_noise_radius',
                                         'zero_center_envelope_control_passes')}, indent=2))
