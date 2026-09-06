"""Exact raw spatial decoding under an interval clock and PSD generator error.

The physical interval and generator/sensor bounds are declared premises. They
are never inferred from a small solver residual or from the returned label.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse, hashlib, importlib.util, json, sys
from uncertainty import exact, nonnegative, spatial_gate

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


normalization = load('_clock_prior_normalization',
    PACKAGE.parent / 'refined_transfer_2026_09/normalization/normalize.py')
consumer = load('_clock_spatial_consumer', PACKAGE / 'resolution/check.py')
old_check = sys.modules.get('check')
sys.modules['check'] = consumer
try:
    timing = load('_clock_spatial_timing', PACKAGE / 'resolution/timing.py')
finally:
    if old_check is None:
        sys.modules.pop('check', None)
    else:
        sys.modules['check'] = old_check


def solve2(matrix, rhs):
    a, b = matrix[0]
    c, d = matrix[1]
    det = a*d-b*c
    if b != c or a <= 0 or det <= 0:
        raise ValueError('positive symmetric two-dimensional Gram required')
    return ((d*rhs[0]-b*rhs[1])/det, (a*rhs[1]-c*rhs[0])/det)


def polynomial(coefficients, time):
    z = time-Q(3, 2)
    out = Q(0)
    for c in reversed(coefficients):
        out = out*z+c
    return out


class RawClockBank:
    """Validate the whole-time spatial premise once, then accept exact readings."""
    def __init__(self):
        kernel_path = consumer.PRIOR / 'kernel.json'
        kernel = json.loads(kernel_path.read_text())
        self.summary = consumer.check(kernel=kernel, bank='7')
        self.derivative = timing.derivative_bound()
        self.lipschitz = Q(self.derivative['polynomial_forward_lipschitz_upper'])
        self.rows = tuple(self.summary['direct_rows'])
        self.coefficients = tuple(tuple(tuple(row) for row in distance)
                                  for distance in consumer.interval_coefficients(kernel))
        profile = self.summary['metrics']['L2']
        self.source_floor = Q(profile['individual_approximate_map_floor'])
        self.pair_floor = Q(profile['pair_approximate_map_floor'])
        self.rho = Q(self.summary['physical_operator_model_error_upper'])
        self.premise_sha256 = {
            'kernel': hashlib.sha256(kernel_path.read_bytes()).hexdigest(),
            'certificate': hashlib.sha256((PACKAGE/'resolution/certificate_7.json').read_bytes()).hexdigest()}

    def matrices(self, nominal_time):
        t = exact(nominal_time)
        if not 1 <= t <= 2:
            raise ValueError('nominal time outside [1,2]')
        return {label: tuple(tuple(polynomial(self.coefficients[abs(row-label)][port], t)
                                  for port in (0, 1)) for row in self.rows)
                for label in range(490, 511)}

    def decode(self, raw_data, nominal_time, actual_time_interval,
               sensor_radius='11/100000000', generator_error='1/1000000000',
               normalization_budget='1/1000000000'):
        t = exact(nominal_time)
        if type(actual_time_interval) not in (list, tuple) or len(actual_time_interval) != 2:
            raise ValueError('two exact endpoints for actual time required')
        lo, hi = map(exact, actual_time_interval)
        if not 1 <= lo <= t <= hi <= 2:
            raise ValueError('interval must contain nominal time and lie in [1,2]')
        eta, eps, xi = map(nonnegative, (sensor_radius, generator_error, normalization_budget))
        if xi > Q(1, 10**9):
            raise ValueError('normalization budget exceeds declared interface maximum')
        h = max(t-lo, hi-t)
        raw = normalization.vector(raw_data)
        if len(raw) != len(self.rows):
            raise ValueError('wrong number of spatial channels')
        packet = normalization.normalize(raw, t, eta, xi)
        processing = normalization.verify_packet(raw, packet)
        budget = spatial_gate(self.source_floor, self.pair_floor, eta, self.rho,
                              processing, h, self.lipschitz, eps)
        if not budget['passed']:
            raise ValueError('clock/model/sensor budget fails a strict recovery gate')
        z = tuple(map(Q, packet['normalized_data']))
        radius2 = (Q(budget['total_radius'])/consumer.A0)**2
        energy = sum((a*a for a in z), Q(0))
        accepted = []
        estimates = {}
        for label, P in self.matrices(t).items():
            G = tuple(tuple(sum((row[i]*row[j] for row in P), Q(0))
                            for j in (0, 1)) for i in (0, 1))
            rhs = tuple(sum((row[i]*y for row, y in zip(P, z)), Q(0)) for i in (0, 1))
            H = tuple(tuple(G[i][j]-radius2*int(i == j) for j in (0, 1)) for i in (0, 1))
            witness = solve2(H, rhs)
            if energy-sum((a*b for a, b in zip(rhs, witness)), Q(0)) <= 0:
                accepted.append(label)
                estimates[label] = solve2(G, rhs)
        status = 'unique' if len(accepted) == 1 else ('abstain' if accepted else 'incompatible')
        return {'schema': 'uncertain-clock-raw-spatial-answer-v1',
                'status': status, 'feasible_targets': accepted,
                'source_estimate': list(map(str, estimates[accepted[0]])) if status == 'unique' else None,
                'guaranteed_relative_source_accuracy': '1/1000' if status == 'unique' else None,
                'nominal_time': str(t), 'actual_time_interval': [str(lo), str(hi)],
                'generator_perturbation_operator_norm_upper': str(eps),
                'normalization': packet, 'transfer_budget': budget,
                'premise_sha256': self.premise_sha256,
                'physical_premise': 'Actual time in supplied interval; fixed preparation/readout/alpha; '
                'both generators self-adjoint PSD and their difference norm bounded as supplied; '
                'raw sensor error bounded by supplied radius times nonzero source L2 norm. '
                'These acquisition assumptions are not inferred from data.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data', type=Path, help='JSON exact real raw reading vector')
    parser.add_argument('--nominal-time', required=True)
    parser.add_argument('--time-lower', required=True)
    parser.add_argument('--time-upper', required=True)
    parser.add_argument('--sensor-radius', default='11/100000000')
    parser.add_argument('--generator-error', default='1/1000000000')
    args = parser.parse_args()
    result = RawClockBank().decode(json.loads(args.data.read_text()), args.nominal_time,
        [args.time_lower, args.time_upper], args.sensor_radius, args.generator_error)
    print(json.dumps(result, indent=2))
