"""A parameter-uniform exact harmonic collision, reconstructed from the model."""
from fractions import Fraction as Q
from pathlib import Path
from itertools import product
from math import prod
import argparse
import json
from flint import arb, acb, arb_mat, fmpq, ctx

HERE = Path(__file__).resolve().parent
PRIMES = (2, 3, 5)


def ball(v):
    v = Q(v)
    return arb(fmpq(v.numerator, v.denominator))


def endpoint(v):
    if not v.is_finite() or not v.is_exact():
        raise ValueError('finite exact endpoint required')
    m, e = map(int, v.man_exp())
    return Q(m * 2 ** e) if e >= 0 else Q(m, 2 ** (-e))


def exported(v, upper=True, scale=10 ** 9):
    v = Q(v)
    n = -((-v.numerator * scale) // v.denominator) if upper else v.numerator * scale // v.denominator
    return str(Q(n, scale))


def mat(rows):
    return arb_mat([[ball(v) for v in row] for row in rows])


def norm_inf(A):
    return max(sum((endpoint(A[i, j].abs_upper()) for j in range(A.ncols())), Q()) for i in range(A.nrows()))


def sources(x):
    return [[[1 - sum(x[9 * side + 3 * j:9 * side + 3 * j + 3], arb(0)),
              *x[9 * side + 3 * j:9 * side + 3 * j + 3]]
             for j in range(3)] for side in range(2)]


def model(x, times, active):
    """Twelve real residuals, active-source Jacobian, six-time Jacobian."""
    qs = sources(x)
    values, derivatives, time_derivatives = [], [], []
    for t in times:
        E = [[acb(0, -t * a * arb(p).log()).exp() for a in range(4)] for p in PRIMES]
        Ep = [[acb(0, -a * arb(p).log()) * E[j][a] for a in range(4)] for j, p in enumerate(PRIMES)]
        chars = [[sum((q[j][a] * E[j][a] for a in range(4)), acb(0)) for j in range(3)] for q in qs]
        values.append(prod(chars[0]) - prod(chars[1]))
        cols, dt = [], acb(0)
        for side in range(2):
            sign = 1 if side == 0 else -1
            for j in range(3):
                other = sign * prod(chars[side][h] for h in range(3) if h != j)
                cols.extend(other * (E[j][a] - 1) for a in range(1, 4))
                dt += other * sum((qs[side][j][a] * Ep[j][a] for a in range(4)), acb(0))
        derivatives.append([cols[k] for k in active])
        time_derivatives.append(dt)
    F = arb_mat([[v.real] for v in values] + [[v.imag] for v in values])
    J = arb_mat([[v.real for v in row] for row in derivatives] + [[v.imag for v in row] for row in derivatives])
    # A time affects only its own complex reading.
    K = arb_mat([[(time_derivatives[i % 6].real if i < 6 else time_derivatives[i % 6].imag)
                  if i % 6 == j else arb(0) for j in range(6)] for i in range(12)])
    return F, J, K


def expanded_model(x, times, active):
    """Independent full integer-label expansion and differentiated amplitudes."""
    qs = sources(x)
    values, derivatives, time_derivatives = [], [], []
    for t in times:
        value, dt = acb(0), acb(0)
        cols = [acb(0) for _ in active]
        for a in product(range(4), repeat=3):
            label = prod(p ** n for p, n in zip(PRIMES, a))
            loglabel = arb(label).log()
            phase = acb(0, -t * loglabel).exp()
            amplitude = prod(qs[0][j][a[j]] for j in range(3)) - prod(qs[1][j][a[j]] for j in range(3))
            value += amplitude * phase
            dt += amplitude * acb(0, -loglabel) * phase
            for l, index in enumerate(active):
                side, rem = divmod(index, 9)
                factor, n = divmod(rem, 3)
                differential = int(a[factor] == n + 1) - int(a[factor] == 0)
                if differential:
                    cols[l] += (1 if side == 0 else -1) * differential * prod(qs[side][j][a[j]] for j in range(3) if j != factor) * phase
        values.append(value)
        derivatives.append(cols)
        time_derivatives.append(dt)
    F = arb_mat([[v.real] for v in values] + [[v.imag] for v in values])
    J = arb_mat([[v.real for v in row] for row in derivatives] + [[v.imag for v in row] for row in derivatives])
    K = arb_mat([[(time_derivatives[i % 6].real if i < 6 else time_derivatives[i % 6].imag)
                  if i % 6 == j else arb(0) for j in range(6)] for i in range(12)])
    return F, J, K


def validate_inputs(inputs):
    times = list(map(Q, inputs['times']))
    coords = list(map(Q, inputs['coordinates']))
    active = inputs['active']
    R = [list(map(Q, row)) for row in inputs['preconditioner']]
    P = [list(map(Q, row)) for row in inputs['predictor']]
    epsilon, rho = Q(inputs['time_radius']), Q(inputs['root_radius'])
    if len(times) != 6 or len(set(times)) != 6 or len(coords) != 18:
        raise ValueError('invalid model dimensions')
    if len(active) != 12 or len(set(active)) != 12 or any(type(v) is not int or not 0 <= v < 18 for v in active):
        raise ValueError('invalid active coordinates')
    if len(R) != 12 or any(len(row) != 12 for row in R) or len(P) != 12 or any(len(row) != 6 for row in P):
        raise ValueError('invalid matrix dimensions')
    if epsilon <= 0 or rho <= 0:
        raise ValueError('positive radii required')
    if min(abs(a - b) for i, a in enumerate(times) for b in times[i + 1:]) <= 2 * epsilon:
        raise ValueError('time boxes must remain pairwise disjoint')
    for name in ('probability_claim', 'separation_claim', 'vertex_floor_claim'):
        if Q(inputs[name]) <= 0:
            raise ValueError('positive claims required')
    return times, coords, active, R, P, epsilon, rho


def vertex_floor(times):
    lower = None
    for v in product(range(-3, 4), repeat=3):
        a = prod(p ** max(n, 0) for p, n in zip(PRIMES, v))
        b = prod(p ** max(-n, 0) for p, n in zip(PRIMES, v))
        if a <= b:
            continue
        k = sum(n != 0 for n in v)
        delta = ball(Q(a, b)).log()
        lower_v = endpoint((sum((1 - (t * delta).cos() for t in times), arb(0)) / k).lower())
        lower = lower_v if lower is None else min(lower, lower_v)
    return lower


def query_obstruction(inputs):
    """The second factor's exponent-one probability is fixed on both sides."""
    if 3 in inputs['active'] or 12 in inputs['active']:
        raise ValueError('the declared query must be frozen on both sides')
    a, b = Q(inputs['coordinates'][3]), Q(inputs['coordinates'][12])
    if not a < Q(1, 2) < b:
        raise ValueError('the declared threshold query must have different answers')
    return {'query': 'probability at exponent 1 in the prime-3 factor',
            'first_answer': str(a), 'second_answer': str(b),
            'answer_gap': str(b - a), 'noiseless_absolute_error_lower': str((b - a) / 2),
            'threshold': '1/2', 'threshold_answers': [0, 1]}


def build(inputs, precision=256, independent=False, require=True):
    times, coords, active, Rq, Pq, epsilon, rho = validate_inputs(inputs)
    query = query_obstruction(inputs)
    evaluator = expanded_model if independent else model
    with ctx.workprec(precision):
        R, P = mat(Rq), mat(Pq)
        t0 = list(map(ball, times))
        TB = [arb(t, ball(epsilon)) for t in t0]
        x0 = list(map(ball, coords))
        C, X = x0.copy(), x0.copy()
        widths = [sum(map(abs, row), Q()) * epsilon for row in Pq]
        for l, index in enumerate(active):
            C[index] = arb(x0[index], ball(widths[l]))
            X[index] = arb(x0[index], ball(widths[l] + rho))
        F0, J0, K0 = evaluator(x0, t0, active)
        _, JC, KC = evaluator(C, TB, active)
        _, JX, KX = evaluator(X, TB, active)
        I = arb_mat([[int(i == j) for j in range(12)] for i in range(12)])
        L = norm_inf(I - R * JX)
        e0 = norm_inf(R * F0)
        # Integrate the derivative of f(x0 + P delta, t0 + delta)
        # over the straight parameter chord. C and TB enclose that chord.
        predictor_derivative = norm_inf(R * (JC * P + KC))
        e = e0 + epsilon * predictor_derivative
        branch_derivative = norm_inf(R * (JX * P + KX))
        branch_lipschitz = max(sum(map(abs, row), Q()) for row in Pq) + branch_derivative / (1 - L) if L < 1 else None
        q, r = sources(X)
        plow = min(endpoint(v.lower()) for source in (q, r) for factor in source for v in factor)
        d2 = sum(((a - b) ** 2 for qa, ra in zip(q, r) for a, b in zip(qa, ra)), arb(0))
        dlow = endpoint(d2.lower())
        vlow = vertex_floor(TB)
        gates = (L < 1 and e + L * rho < rho and plow > Q(inputs['probability_claim'])
                 and dlow > Q(inputs['separation_claim']) ** 2 and vlow > Q(inputs['vertex_floor_claim']) ** 2)
        if require and not gates:
            raise ValueError('uniform contraction, source, or vertex gate failed')
        return {'schema': 'uniform-harmonic-collision-v1', 'inputs': inputs,
                'method': 'integer-label expansion' if independent else 'factored product model',
                'contraction_upper': exported(L), 'center_residual_upper': exported(e0, scale=10 ** 24),
                'predictor_derivative_upper': exported(predictor_derivative),
                'moving_center_residual_upper': exported(e),
                'self_map_radius_upper': exported(e + L * rho),
                'self_map_ratio_upper': exported((e + L * rho) / rho),
                'complement_coordinate_branch_lipschitz_upper': exported(branch_lipschitz) if branch_lipschitz is not None else None,
                'minimum_probability_lower': exported(plow, False),
                'factor_distance_squared_lower': exported(dlow, False),
                'vertex_floor_squared_lower': exported(vlow, False),
                'maximum_time_upper': str(max(times) + epsilon),
                'query_obstruction': query,
                'predictor_coordinate_widths': list(map(str, widths)),
                'all_strict_gates_pass': gates}


def check(precision=256, independent=False):
    inputs = json.loads((HERE / 'inputs.json').read_text())
    fresh = build(inputs, precision, independent)
    saved = json.loads((HERE / ('independent_certificate.json' if independent else 'certificate.json')).read_text())
    if fresh != saved:
        raise ValueError('complete model-to-certificate replay mismatch')
    # Rounded public bounds must themselves close the strict proof gates.
    check_consequences(fresh)
    return fresh


def check_consequences(certificate):
    _, _, _, _, _, _, rho = validate_inputs(certificate['inputs'])
    inp = certificate['inputs']
    if not certificate['all_strict_gates_pass']:
        raise ValueError('rejected certificate')
    if certificate['query_obstruction'] != query_obstruction(inp):
        raise ValueError('query consequence mismatch')
    if not (Q(certificate['contraction_upper']) < 1
            and Q(certificate['moving_center_residual_upper']) + Q(certificate['contraction_upper']) * rho < rho
            and Q(certificate['self_map_radius_upper']) < rho
            and Q(certificate['minimum_probability_lower']) > Q(inp['probability_claim'])
            and Q(certificate['factor_distance_squared_lower']) > Q(inp['separation_claim']) ** 2
            and Q(certificate['vertex_floor_squared_lower']) > Q(inp['vertex_floor_claim']) ** 2):
        raise ValueError('exported exact consequence gate failed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--precision', type=int, default=256)
    parser.add_argument('--independent', action='store_true')
    args = parser.parse_args()
    if args.write:
        data = build(json.loads((HERE / 'inputs.json').read_text()), args.precision, args.independent)
        (HERE / ('independent_certificate.json' if args.independent else 'certificate.json')).write_text(json.dumps(data, indent=2) + '\n')
    out = check(args.precision, args.independent)
    print(json.dumps({k: v for k, v in out.items() if k not in ('inputs', 'predictor_coordinate_widths')}, indent=2))
