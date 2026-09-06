"""Independent exact controls for the physical normalization transfer lemma.

This does not import the implementation under review. Its rational-alpha
examples test the actual error rather than another formula for the same gate.
"""
from fractions import Fraction as Q
import json


def quartic_gate(t, r, eps):
    if not (Q(1) <= t <= Q(2) and r > 0 and 0 <= eps < 1):
        return False
    return (1-eps)**4 <= (1+t)*r**4 <= (1+eps)**4


def run():
    checks = {}
    alpha = Q(5, 4)
    t = alpha**4 - 1
    xi = Q(1, 10**9)
    eta = Q(3, 10**7)
    bound = Q(4, 3)
    eps = xi/(bound+eta)
    # A known rational root supplies genuine equality and adjacent failure.
    for side in (-1, 1):
        r = (1 + side*eps)/alpha
        assert quartic_gate(t, r, eps)
        assert abs(alpha*r - 1) == eps
        assert not quartic_gate(t, (1+side*(eps+eps/100))/alpha, eps)
    checks['both_closed_endpoints_and_adjacent_failures'] = True
    assert not quartic_gate(t, -1/alpha, eps)
    assert (1+t)*(-1/alpha)**4 == 1
    checks['negative_root_requires_an_explicit_sign_check'] = True
    assert quartic_gate(t, 1/alpha, Q(0))
    assert not quartic_gate(t, (1+eps)/alpha, Q(0))
    checks['zero_radius_requires_exact_normalization'] = True

    # A physical contraction A=alpha*I is a legitimate instance of the
    # abstract transfer lemma. It is not claimed to be a diffusion-bank map.
    # Merely bounding normalized coordinate error by xi is insufficient.
    u = Q(1)
    y = alpha*u
    r_bad = 1/alpha + xi/bound
    z_bad = r_bad*y
    normalized_error = abs(z_bad-y/alpha)
    physical_error = abs(alpha*z_bad-y)
    assert normalized_error <= xi and physical_error > xi
    checks['normalized_error_is_not_the_physical_budget'] = {
        'normalized_error_over_xi': str(normalized_error/xi),
        'physical_error_over_xi': str(physical_error/xi),
    }

    # Dropping eta from ||y|| <= (C+eta)||u|| can similarly overspend.
    local_bound = alpha
    large_eta = Q(1, 4)
    noisy_y = alpha*u + large_eta*u
    r_bad = (1+xi/local_bound)/alpha
    error_bad = abs(alpha*r_bad*noisy_y-noisy_y)
    r_good = (1+xi/(local_bound+large_eta))/alpha
    error_good = abs(alpha*r_good*noisy_y-noisy_y)
    assert error_bad > xi and error_good == xi
    checks['measured_noise_must_enter_the_gain'] = {
        'omitted_eta_error_over_xi': str(error_bad/xi),
        'correct_error_over_xi': str(error_good/xi),
    }

    # Rational bisection is tested on a mesh containing both physical endpoints.
    cases = 0
    steps_max = 0
    for k in range(65):
        tau = 1+Q(k, 64)
        for radius in (Q(1, 10**9), Q(1, 10**20)):
            eps_k = radius/(bound+eta)
            lo, hi = Q(3, 4), Q(16, 19)
            assert (1+tau)*lo**4 < 1 < (1+tau)*hi**4
            steps = 0
            while True:
                r = (lo+hi)/2
                if quartic_gate(tau, r, eps_k):
                    break
                if (1+tau)*r**4 < 1:
                    lo = r
                else:
                    hi = r
                steps += 1
                assert steps < 100
            # Independent inverse-root interval confirms the physical error
            # without using the quartic tolerance comparisons.
            if r/hi < 1-eps_k or r/lo > 1+eps_k:
                # Tighten the enclosure while keeping the accepted r fixed.
                for _ in range(4):
                    middle = (lo+hi)/2
                    if (1+tau)*middle**4 < 1:
                        lo = middle
                    else:
                        hi = middle
                    if 1-eps_k <= r/hi and r/lo <= 1+eps_k:
                        break
                else:
                    # Near a budget endpoint an arbitrarily tighter interval
                    # is sometimes required; use the guaranteed terminating
                    # search only when exact equality is absent (irrational
                    # roots in this mesh except the explicit test above).
                    for _ in range(100):
                        middle = (lo+hi)/2
                        if (1+tau)*middle**4 < 1:
                            lo = middle
                        else:
                            hi = middle
                        if 1-eps_k <= r/hi and r/lo <= 1+eps_k:
                            break
                    else:
                        raise AssertionError('inverse-root control unresolved')
            assert 1-eps_k <= r/hi <= r/lo <= 1+eps_k
            cases += 1
            steps_max = max(steps_max, steps)
    checks['independent_inverse_root_enclosure_cases'] = cases
    checks['maximum_proposal_bisections'] = steps_max

    # All inherited calibrations rule out zero data for nonzero sources.
    a0 = Q(19, 16)
    rho = xi
    calibrations = [(Q(65, 10**9), 1, Q(3, 10**7)),
                    (Q(65, 10**9), 41, Q(3, 10**8)),
                    (Q(4, 10**8), 1, Q(23, 10**8)),
                    (Q(4, 10**8), 1, Q(3, 10**7)),
                    (Q(4, 10**8), 41, Q(3, 10**8))]
    for floor, factor, sensor in calibrations:
        assert a0*a0*floor/factor > (rho+sensor)**2
    checks['inherited_zero_data_exclusion_calibrations'] = len(calibrations)
    return {'verified': True, 'method': 'independent exact rational controls',
            'checks': checks}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
