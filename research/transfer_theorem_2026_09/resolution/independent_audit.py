"""Independent analytic and bounded model reconstruction for spatial sensing.

The complete case/cell proof is checked separately by check.py. This module
imports no spatial producer or consumer. It checks all analytic error budgets,
reconstructs 16 selected full-1001-x kernel coefficients by a different positive
uniformization expansion, and exercises separate exact/small dense controls.
"""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import argparse, hashlib, json
import numpy as np
from scipy.linalg import expm
from flint import arb, ctx, fmpq

HERE = Path(__file__).resolve().parent
PRECISION = 256


def ball(q):
    q = Q(q)
    return arb(fmpq(q.numerator, q.denominator))


def exact_endpoint(x):
    assert x.is_exact() and x.is_finite()
    m, e = map(int, x.man_exp())
    return Q(m*2**e) if e >= 0 else Q(m, 2**(-e))


def exp_upper(x, degree=128):
    assert 0 <= x < degree+2
    return sum((x**k/factorial(k) for k in range(degree+1)), Q()) + \
        x**(degree+1)/factorial(degree+1)/(1-x/(degree+2))


def analytic_bounds():
    image = exp_upper(Q(441, 20))*(Q(8)**(-38)+Q(8)**(-90))/(1-Q(8)**(-64))
    assert image < Q(1, 10**24)
    mean = Q(56, 5)
    finite = 2*mean**491/factorial(491)/(1-mean/492)
    assert finite < Q(1, 10**500)
    low, high = Q(19, 16), Q(4, 3)
    assert low**4 < 2 and high**4 > 3
    entry = Q(1, 2**33)+Q(1, 10**24)+Q(1, 10**500)+Q(2, 10**30)
    published_square = high**2*22*entry**2
    assert published_square < Q(1, 10**18)

    # max_{lambda>=0} lambda^33 exp(-s lambda) occurs at lambda=33/s.
    # e>8/3 from its positive series; s>=1 throughout every Taylor segment.
    assert sum((Q(1, factorial(k)) for k in range(5)), Q()) > Q(8, 3)
    stronger_time = Q(99, 16)**33/factorial(33)
    assert stronger_time < Q(1, 2**33)
    stronger_entry = stronger_time+Q(1, 10**24)+Q(1, 10**500)+Q(2, 10**30)
    stronger_square = high**2*22*stronger_entry**2
    assert stronger_square < Q(1, 10**20)
    assert 1+4*Q(22, 7)**2 < 41
    models = {}
    for name, factor, eta in [('L2', 1, Q(3, 10**7)),
                              ('declared_H1', 41, Q(3, 10**8)),
                              ('natural_discrete_H1', 41, Q(3, 10**8))]:
        delta = eta+Q(2, 10**9)  # Retain the published model and numerical budgets.
        single, pair = low**2*Q(7, 10**8)/factor, low**2*Q(1, 10**11)/factor
        assert pair > 2*delta**2
        assert delta**2 < single*Q(1, 10**6)
        # Enlarging the H1 tube to a Euclidean one also keeps pair separation.
        enlarged = factor*(delta/low)**2
        assert Q(1, 10**11) > 2*enlarged
        models[name] = {'total_relative_radius': str(delta),
                        'source_error_squared_bound': str(delta**2/single),
                        'strict_pair_margin': str(pair-2*delta**2)}
    return {'complete_image_bound': str(image), 'finite_boundary_bound': str(finite),
            'published_operator_error_squared_bound': str(published_square),
            'sharper_time_remainder': str(stronger_time),
            'audit_only_operator_error_squared_bound': str(stronger_square),
            'audit_only_operator_radius': '1/10000000000',
            'published_operator_radius_unchanged': '1/1000000000',
            'calibrations': models}


def exact_boundary_control():
    nx, ny, large, offset = 3, 9, 17, 4
    v = [1+Q(4, 5)*Q(2*i+1, 2*nx) for i in range(nx)]
    rate = Q(28, 5)

    def step(state, transverse):
        out = [Q(0)]*len(state)
        for y in range(transverse):
            for x in range(nx):
                index = y*nx+x
                degree = int(x > 0)+int(x+1 < nx)
                degree += v[x]*(int(y > 0)+int(y+1 < transverse))
                out[index] += (1-degree/rate)*state[index]
                for xx in (x-1, x+1):
                    if 0 <= xx < nx:
                        out[y*nx+xx] += state[index]/rate
                for yy in (y-1, y+1):
                    if 0 <= yy < transverse:
                        out[yy*nx+x] += v[x]*state[index]/rate
        assert sum(out, Q()) == sum(state, Q())
        return out

    def embedded(state):
        return [Q(0)]*(offset*nx)+state+[Q(0)]*(offset*nx)

    checks = 0
    for source_x in range(nx):
        small = [Q(0)]*(nx*ny)
        small[4*nx+source_x] = 1
        big = embedded(small)
        for power in range(5):
            assert embedded(small) == big
            checks += 1
            small, big = step(small, ny), step(big, large)
        assert embedded(small) != big  # First change is one step after arrival.
    return {'exact_walk_equalities': checks,
            'boundary_distance': 4, 'first_disagreeing_power': 5,
            'all_three_source_coordinates_checked': True}


def dense_controls():
    nx, period = 7, 8
    lap = np.diag([1]+[2]*(nx-2)+[1])-np.eye(nx, k=1)-np.eye(nx, k=-1)
    cyc = 2*np.eye(period)-np.roll(np.eye(period), 1, axis=0)-np.roll(np.eye(period), -1, axis=0)
    x = (np.arange(nx)+0.5)/nx
    potential = np.diag(1+0.8*x)
    ports = np.sqrt(2/nx)*np.cos(np.pi*x[:, None]*np.array([1, 2]))
    average = np.ones(nx)/np.sqrt(nx)
    assert np.linalg.norm(ports.T@ports-np.eye(2)) < 1e-13
    assert np.linalg.norm(average@ports) < 1e-13
    full = np.kron(np.eye(period), lap)+np.kron(cyc, potential)
    source = np.zeros((period*nx, 2)); source[:nx] = ports
    count = 0
    for time in (1.0, 1.5, 2.0):
        exact_dense = (np.kron(np.eye(period), average[None, :])@expm(-time*full)@source)
        fourier = np.zeros((period, 2), dtype=complex)
        for mode in range(period):
            omega = 4*np.sin(np.pi*mode/period)**2
            response = average@expm(-time*(lap+omega*potential))@ports
            fourier += np.exp(2j*np.pi*mode*np.arange(period)/period)[:, None]*response/period
        assert np.max(np.abs(exact_dense-fourier)) < 1e-12
        assert np.linalg.norm(average@expm(-time*lap)@ports) < 1e-12
        assert abs(average@expm(-time*lap)@average-1) < 1e-12
        count += period*2
    assert np.linalg.norm(lap@potential-potential@lap) > 0.1
    assert np.linalg.norm(expm(-(lap+2*potential))-expm(-lap)@expm(-2*potential)) > 1e-3
    return {'full_cycle_response_entries_checked': count,
            'absolute_comparison_tolerance': '1/1000000000000',
            'zero_mode_and_nonzero_constant_control': True,
            'noncommuting_generator_control': True,
            'role': 'floating diagnostics only; not continuous-time certificates'}


def full_x_selected_coefficients(saved):
    nx, period = 1001, 64
    chosen_orders = (0, 1, 16, 32)
    chosen_distances = (0, 26)
    collected = {(d, p, k): arb(0) for d in chosen_distances for p in range(2) for k in chosen_orders}
    center = ball(Q(3, 2))
    with ctx.workprec(PRECISION):
        x = [ball(Q(2*j+1, 2*nx)) for j in range(nx)]
        ports = [[(arb(2)/nx).sqrt()*(k*arb.pi()*xx).cos() for xx in x] for k in (1, 2)]
        for mode in range(1, 33):
            omega = 4*(arb.pi()*mode/period).sin()**2
            q = 4+ball(Q(9, 5))*omega
            diag = [(1 if j in (0, nx-1) else 2)+omega*(1+ball(Q(4, 5))*xx) for j, xx in enumerate(x)]

            def generator_action(state):
                result = []
                for j, value in enumerate(state):
                    entry = diag[j]*value
                    if j:
                        entry -= state[j-1]
                    if j+1 < nx:
                        entry -= state[j+1]
                    result.append(entry)
                return result

            # e^(-c A)=e^(-c q) sum_h (c q)^h/h! (I-A/q)^h.
            # 0<=I-A/q<=I in the spectral order. No L/V commutation occurs.
            states = [p[:] for p in ports]
            totals = [p[:] for p in ports]
            for h in range(1, 161):
                for port in range(2):
                    applied = generator_action(states[port])
                    states[port] = [(center/h)*(q*v-a) for v, a in zip(states[port], applied)]
                    totals[port] = [a+b for a, b in zip(totals[port], states[port])]
            scalar = (-center*q).exp()
            states = [[scalar*a for a in p] for p in totals]
            tail = scalar*(center*q)**161/factorial(161)/(1-center*q/162)
            assert tail > 0 and center*q < 162
            for k in range(33):
                if k:
                    states = [[-v/k for v in generator_action(p)] for p in states]
                if k not in chosen_orders:
                    continue
                radius = (tail*q**k/factorial(k)).abs_upper()
                response = [sum(p, arb(0))/arb(nx).sqrt()+arb(0, radius) for p in states]
                for d in chosen_distances:
                    multiplier = (ball(Q(2, period))*(2*arb.pi()*mode*d/period).cos()
                                  if mode < 32 else ball(Q((-1)**d, period)))
                    for port in range(2):
                        collected[d, port, k] += multiplier*response[port]
        for (d, port, k), value in collected.items():
            lo, hi = map(Q, saved['coefficient_intervals'][d][port][k])
            assert lo <= exact_endpoint(value.lower())
            assert exact_endpoint(value.upper()) <= hi
    return {'full_x_vertices': nx, 'transverse_fourier_modes': 32,
            'alternative_center_exponential': 'positive uniformization, degree 160',
            'working_precision_bits': PRECISION, 'selected_displacements': list(chosen_distances),
            'selected_orders': list(chosen_orders), 'both_source_columns': True,
            'selected_coefficient_enclosures_verified': len(collected),
            'comparison': 'independent enclosures lie inside saved intervals'}


def audit():
    kernel = json.loads((HERE/'kernel.json').read_text())
    assert kernel['model'] == {'nx': 1001, 'period': 64, 'source_modes': [1, 2], 'g': '4/5',
                               'center': '3/2', 'order': 32, 'exponential_degree': 80,
                               'maximum_distance': 26,
                               'output': 'unnormalized global-x average; multiply by (1+tau)^(1/4)'}
    analytic = analytic_bounds()
    walk = exact_boundary_control()
    dense = dense_controls()
    print('Reconstructing 16 selected full-x coefficients by independent uniformization', flush=True)
    physical = full_x_selected_coefficients(kernel)
    paths = ['kernel.py', 'kernel.json', 'certificate.json', 'PROOFS.md', 'independent_audit.py']
    return {'verified': True, 'analytic_bounds': analytic, 'exact_boundary_control': walk,
            'dense_controls': dense, 'independent_full_x_reconstruction': physical,
            'not_repeated': '895 exact whole-cell records; use the independent check.py consumer',
            'not_claimed': ['physical apparatus validation', 'a deployed computation meets its data-error budget'],
            'sha256': {p: hashlib.sha256((HERE/p).read_bytes()).hexdigest() for p in paths}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    path = HERE/'independent_audit.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2)+'\n')
    else:
        assert json.loads(path.read_text()) == result, 'independent spatial audit evidence changed'
    print('PASS: independent analytic, finite-walk, dense, and full-x coefficient audit')
