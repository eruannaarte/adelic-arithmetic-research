#!/usr/bin/env python3
"""Reconstruct log phases with Arb; derive all global bounds as exact rationals.

This checker accepts only rational acquisition times and integer windings. It
does not trust supplied response matrices or floating-point singular values.
The implication from this finite witness to global inversion is proved in
PROOFS.md; the checker is not a proof assistant.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import json
from math import isqrt
from pathlib import Path
import platform

import flint
from flint import arb, acb, arb_mat, fmpq, ctx

ROOT = Path(__file__).resolve().parent
PRECISION = 384
SCALE = 10**12
A_UPPER = Q(223606797749979, 10**14)  # sqrt(5)
SQRT_TWO_LOWER = Q(1414213562373095, 10**15)
PRIMES = (2, 3, 5)
TARGET_AXES = (0, 0, 1, 1, 2, 2)
TARGET_MULTIPLIERS = (Q(1, 2), Q(1)) * 3


def rat(value: object) -> Q:
    if not isinstance(value, str) or len(value) > 200:
        raise ValueError('expected a short rational string')
    return Q(value)


def aq(value: Q | int) -> arb:
    value = Q(value)
    return arb(fmpq(value.numerator, value.denominator))


def endpoint(value: arb) -> Q:
    if not value.is_exact():
        raise ValueError('endpoint is not exact')
    mantissa, exponent = map(int, value.man_exp())
    return Q(mantissa * 2**exponent) if exponent >= 0 else Q(mantissa, 2**(-exponent))


def ceil_grid(value: Q, scale: int = SCALE) -> Q:
    return Q(-((-value.numerator * scale) // value.denominator), scale)


def upper(value: arb) -> Q:
    return ceil_grid(endpoint(value.upper()))


def sqrt_upper(value: Q) -> Q:
    if value < 0:
        raise ValueError('negative square')
    n = value.numerator * SCALE**2
    d = value.denominator
    u = isqrt(n // d)
    if u*u*d < n:
        u += 1
    return Q(u, SCALE)


def str_matrix(matrix: list[list[Q]]) -> list[list[str]]:
    return [[str(x) for x in row] for row in matrix]


def derive(errors: list[list[Q]]) -> dict:
    """Independent exact arithmetic consequence of certified phase errors."""
    if len(errors) != 6 or any(len(row) != 3 or min(row) < 0 for row in errors):
        raise ValueError('invalid phase error array')
    if not A_UPPER**2 >= 5 or not 0 < SQRT_TWO_LOWER**2 < 2:
        raise ValueError('invalid rational radical bounds')
    b = []
    for row, axis in zip(errors, TARGET_AXES):
        bb = [A_UPPER*x for x in row]
        bb[axis] += 3 * (sum(row) - row[axis])
        b.append(bb)
    gram = [[sum(row[i]*row[j] for row in b) for j in range(3)] for i in range(3)]
    gram_row_sums = [sum(row) for row in gram]
    gamma = max(gram_row_sums)
    err = sqrt_upper(gamma)
    floor = SQRT_TWO_LOWER - err
    # Ensure the square-root rounding itself really is outward.
    if err**2 < gamma:
        raise ValueError('invalid square-root enclosure')
    return {'phase_errors_upper': str_matrix(errors), 'block_majorant_upper': str_matrix(b),
            'gram_row_sums_upper': [str(x) for x in gram_row_sums],
            'operator_error_squared_upper': str(gamma), 'operator_error_upper': str(err),
            'factor_floor_lower': str(floor),
            'tensor_floor_lower': str(floor / sqrt_upper(Q(3)))}


def schedule_bound(spec: dict, clock: Q | None = None, precision: int = PRECISION) -> dict:
    ctx.prec = precision
    times = [rat(x) for x in spec['times']]
    windings = spec['windings']
    if len(times) != 6 or len(set(times)) != 6 or min(times) <= 0:
        raise ValueError('need six distinct positive times')
    if len(windings) != 6 or any(len(x) != 3 or any(type(n) is not int for n in x) for x in windings):
        raise ValueError('need six integer winding triples')
    radius = rat(spec['clock_radius']) if clock is None else clock
    if radius < 0:
        raise ValueError('negative clock radius')
    logarithms = [arb(p).log() for p in PRIMES]
    errors = []
    nominal = []
    for time, winding, axis, multiplier in zip(times, windings, TARGET_AXES, TARGET_MULTIPLIERS):
        row, nominal_row = [], []
        for a in range(3):
            theta = aq(time) * logarithms[a] - 2*arb.pi()*winding[a]
            if a == axis:
                theta -= aq(multiplier)*arb.pi()
            # Triangle inequality covers every independent perturbation of
            # each time in [-radius,radius], and hence one shared offset.
            nominal_row.append(upper(abs(theta)))
            row.append(upper(abs(theta) + aq(radius)*logarithms[a]))
        errors.append(row); nominal.append(nominal_row)
    result = derive(errors)
    result['nominal'] = derive(nominal)
    result['maximum_time'] = str(max(times))
    result['relative_rate_radius_from_box'] = str(radius / max(times))
    omega = 3*arb(30).log()
    drift = upper(arb(6).sqrt()*omega*aq(radius))
    drift_per_time = upper(omega)
    result['unknown_clock_response_radius_upper'] = str(drift)
    result['raw_frequency_max_upper'] = str(drift_per_time)
    epsilon = rat(spec['worked_noise_radius'])
    if epsilon < 0:
        raise ValueError('negative sensor-noise radius')
    c = Q(result['factor_floor_lower'])
    if c > 0:
        result['known_clock_factor_error_upper'] = str(2*epsilon/c)
        result['unknown_clock_factor_error_upper'] = str(2*(epsilon+drift)/c)
    claim = rat(spec['factor_floor_claim'])
    if claim < 0:
        raise ValueError('negative global-separation claim')
    if c <= claim:
        raise ValueError(f'factor floor {float(c)} does not exceed claim {float(claim)}')
    result['factor_floor_claim'] = str(claim)
    return result


def build(inputs: dict, precision: int = PRECISION) -> dict:
    if inputs.get('schema') != 'path2-harmonic-inputs-v1':
        raise ValueError('invalid input schema')
    if inputs.get('model') != {'primes': [2, 3, 5], 'states': 4, 'reading_count': 6}:
        raise ValueError('invalid model')
    results = {name: schedule_bound(spec, precision=precision)
               for name, spec in inputs['schedules'].items()}
    ctx.prec = precision
    baseline = inputs['schedules']['baseline']
    old = arb(2).sqrt() - 9*arb(1202).sqrt()/500
    if not old > aq(Q(7901, 10000)):
        raise ValueError('old AO VI algebraic consequence failed')
    baseline_nominal = results['baseline']['nominal']['phase_errors_upper']
    for row, axis in zip(baseline_nominal, TARGET_AXES):
        for a, text in enumerate(row):
            if not rat(text) < (Q(1, 1000) if a == axis else Q(17, 1000)):
                raise ValueError('old AO VI phase box failed')
    max_old = max(rat(t) for t in baseline['times'])
    ratios = {name: str(max_old / rat(item['maximum_time'])) for name, item in results.items()}
    return {'schema': 'path2-harmonic-certificate-v1',
            'arithmetic': {'phase_interval_precision_bits': precision,
                           'phase_upper_grid': str(SCALE),
                           'sqrt5_upper': str(A_UPPER),
                           'sqrt2_lower': str(SQRT_TWO_LOWER)},
            'baseline_published_floor_reproduced': '7901/10000',
            'five_reading_local_witness': local_witness(precision),
            'schedules': results, 'maximum_time_improvement_ratios': ratios}


def local_witness(precision: int = PRECISION) -> dict:
    """An actual five-reading interior Jacobian minor, not a supplied matrix."""
    ctx.prec = precision
    lams = [arb(p).log() for p in PRIMES]
    q = [aq(Q(97, 100))] + [aq(Q(1, 100))]*3
    rows = []
    for ell in range(1, 6):
        t = aq(Q(ell, 10))
        vectors = [[acb((-a*t*lam).cos(), (-a*t*lam).sin()) for a in range(4)] for lam in lams]
        values = [sum(q[a]*v[a] for a in range(4)) for v in vectors]
        derivative = []
        for j in range(3):
            product = acb(1)
            for k in range(3):
                if k != j:
                    product *= values[k]
            derivative.extend((vectors[j][a]-1)*product for a in range(1, 4))
        rows.append(derivative)
    # Parameters are q_j(1),q_j(2),q_j(3), with q_j(0) their complement.
    matrix = arb_mat([[z.imag for z in row] for row in rows] +
                     [[z.real for z in row] for row in rows[:4]])
    determinant = matrix.det()
    lo, hi = Q(67, 10**36), Q(68, 10**36)
    if not -determinant > aq(lo) or not -determinant < aq(hi):
        raise ValueError('five-reading local witness failed')
    return {'times': [str(Q(k, 10)) for k in range(1, 6)],
            'each_factor': ['97/100', '1/100', '1/100', '1/100'],
            'selected_rows': 'imaginary rows 1-5, then real rows 1-4',
            'determinant_lower': str(-hi), 'determinant_upper': str(-lo),
            'claim': 'nonzero differential minor implies local stability; no useful noise constant asserted'}


def run(input_path: Path, certificate_path: Path, write: bool, precision: int = PRECISION) -> dict:
    inputs = json.loads(input_path.read_text())
    computed = build(inputs, precision)
    if write:
        certificate_path.write_text(json.dumps(computed, indent=2, sort_keys=True) + '\n')
    else:
        stored = json.loads(certificate_path.read_text())
        if stored != computed:
            raise ValueError('certificate differs from complete reconstruction')
    return computed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', type=Path, default=ROOT/'inputs.json')
    parser.add_argument('--certificate', type=Path, default=ROOT/'certificate.json')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--precision', type=int, default=PRECISION)
    args = parser.parse_args()
    result = run(args.inputs, args.certificate, args.write, args.precision)
    print(json.dumps({'verified': True, 'python': platform.python_version(),
                      'python_flint': flint.__version__, 'FLINT': flint.__FLINT_VERSION__,
                      'precision': args.precision,
                      'schedules': {name: {'maximum_time': float(Q(x['maximum_time'])),
                                           'robust_floor': float(Q(x['factor_floor_lower'])),
                                           'nominal_floor': float(Q(x['nominal']['factor_floor_lower'])),
                                           'relative_clock_radius': float(Q(x['relative_rate_radius_from_box'])),
                                           'unknown_clock_error': float(Q(x['unknown_clock_factor_error_upper']))}
                                    for name, x in result['schedules'].items()}}, indent=2))


if __name__ == '__main__':
    main()
