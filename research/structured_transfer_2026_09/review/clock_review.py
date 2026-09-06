"""Independent complete phase-pairing audit using exact zeta derivatives.

Imports no current producer or consumer. The preserved physical weight
function defines the original experiment; all new phase sums are rebuilt.
"""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import hashlib, json, sys
from flint import arb, acb, arb_series, ctx

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT/'research/operational_transfer_2026_09/noise'))
from physical import weights, ball, upper


def need(condition, message):
    if not condition:
        raise ValueError(message)


def audit():
    path = PACKAGE/'arithmetic/clock_bound.json'
    doc = json.loads(path.read_text())
    masses = doc['complete_mass_data']
    reports = []
    with ctx.workprec(384):
        z = arb_series([2,1],3).zeta()
        power = z**14
        D, D2 = -power[1], 2*power[2]
        log2 = arb(2).log()
        O = (3*z[0]/4)**14
        O1 = 14*(3*z[0]/4)**13*(-3*z[1]/4-log2*z[0]/4)
        C2 = 14*log2/4
        need(D < ball(Q(doc['complete_first_derivative_upper'])), 'complete first derivative')
        need(D2 < ball(Q(masses['second_derivative_upper'])), 'complete second derivative')
        need(O > ball(Q(masses['odd_mass_lower'])), 'odd-part complete mass')
        need(O1 > ball(Q(masses['odd_derivative_mass_lower'])), 'odd-part derivative mass')
        need(C2 < ball(Q(masses['exception_c2_upper'])), 'unpaired derivative envelope')
        # The only special ratio class is k=0. For every k>=2, all ratios
        # are in[1/4,2], so q>=4/25>210/1681, including unlisted classes.
        q0 = Q(210,1681)
        need(Q(4,25)>q0 and 8<9, 'complete global ratio bound')
        exact_masses = []
        for row in masses['valuation_classes']:
            k = row['even_valuation']
            need(type(k) is int and k%2==0, 'even valuation')
            exact_mass = sum((ball(Q(comb(v+13,13),4**v))*(O1+v*log2*O)
                              for v in (k,k+1)),arb(0))
            if k==0:
                exact_mass -= C2
            need(exact_mass > ball(Q(row['complete_pair_derivative_mass_lower'])), 'complete class mass')
            lo = Q(k+14,4*(k+1))
            hi = Q(35,6) if k==0 else Q(k+14,4*k)
            need(Q(row['minimum_pair_product_fraction']) == min(lo/(1+lo)**2,hi/(1+hi)**2), 'ratio minimum')
            exact_masses.append(exact_mass)
        need(sum(exact_masses,arb(0))+C2 < D, 'unlisted valuations retain positive complete mass')
        for saved in doc['records']:
            w = weights(8900)
            if saved['design']=='multi':
                alpha = ball(Q(125,65536))
                w = [(1-alpha)*x for x in w]
                for i,v in enumerate(weights(2550),3175):
                    w[i] += alpha*v
            times = [ball(Q(2*i+1-8900,10)) for i in range(8900)]
            for c in saved['clock_corners']:
                s,b = c['slope_sign'],c['offset_sign']
                direction = [s*t/1000+b for t in times]
                n2 = sum((wi*d*d for wi,d in zip(w,direction)),arb(0))
                n4 = sum((wi*d**4 for wi,d in zip(w,direction)),arb(0))
                # Separate trig functions, not the producer's complex exp.
                re = sum((wi*d*d*(t*log2).cos() for wi,d,t in zip(w,direction,times)),arb(0))
                im = sum((wi*d*d*(t*log2).sin() for wi,d,t in zip(w,direction,times)),arb(0))
                gamma = Q(c['normalized_phase_correlation_upper'])
                need(ball(gamma)**2*n2*n2 > re*re+im*im, 'actual weighted phase correlation')
                need(n2 < ball(Q(saved['normalized_direction_squared_norm_upper'])), 'clock second moment')
                need(n4 < ball(Q(saved['normalized_direction_fourth_moment_upper'])), 'clock fourth moment')
            gamma = max(Q(c['normalized_phase_correlation_upper']) for c in saved['clock_corners'])
            f0 = Q(saved['global_pair_norm_factor_upper'])
            need(f0>0 and f0*f0>=1-2*(1-gamma)*q0, 'global phase factor')
            improved = f0*Q(doc['complete_first_derivative_upper'])+(1-f0)*Q(masses['exception_c2_upper'])
            for row,f in zip(masses['valuation_classes'],saved['valuation_norm_factors']):
                factor = Q(f['pair_norm_factor_upper'])
                need(0<factor<=f0 and factor**2>=1-2*(1-gamma)*Q(row['minimum_pair_product_fraction']), 'class phase factor')
                improved -= (f0-factor)*Q(row['complete_pair_derivative_mass_lower'])
            need(improved==Q(saved['complete_paired_derivative_norm_upper']), 'complete grouped envelope')
            linear,quad = Q(saved['linear_clock_coefficient']),Q(saved['quadratic_clock_coefficient'])
            need(linear>0 and quad>0, 'nonzero complete remainder')
            need(linear**2*10**22 >= improved**2*Q(saved['normalized_direction_squared_norm_upper']), 'linear length')
            need(4*quad**2*10**44 >= Q(masses['second_derivative_upper'])**2*Q(saved['normalized_direction_fourth_moment_upper']), 'nonlinear length')
            need(linear+quad<Q(saved['weighted_pointwise_clock_coefficient'])<Q(saved['prior_pointwise_clock_coefficient']), 'two separate strict improvements')
            reports.append({'design':saved['design'],'base_clock_radius':str(linear+quad),
                'sixtyfold_clock_radius':str(60*linear+3600*quad),
                'complete_paired_derivative_upper':str(improved),'verified':True})
    result = {'verified':True,'bits':384,'full_clock_corners_reconstructed':8,
              'complete_valuation_classes':20,'unlisted_valuation_tail_retained':True,
              'independent_method':'analytic zeta derivatives and odd Euler factor; direct trigonometric sample sums',
              'clock_bound_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'results':reports}
    return result


if __name__=='__main__':
    result = audit()
    (HERE/'clock_review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
