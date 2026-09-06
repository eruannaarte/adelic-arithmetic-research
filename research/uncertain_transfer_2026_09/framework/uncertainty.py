"""Exact consequence gates for the proved uncertain-acquisition transfer.

Callers must establish the supplied physical bounds; passing these numerical
gates does not establish model membership or calibration.
"""
from fractions import Fraction as Q
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('_uncertain_prior_transfer',
        HERE.parents[1] / 'transfer_theorem_2026_09/framework/transfer.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)


def exact(value):
    if type(value) not in (str, int, Q):
        raise ValueError('use exact rational strings, integers or Fractions')
    return Q(value)


def nonnegative(value):
    value = exact(value)
    if value < 0:
        raise ValueError('negative error bound')
    return value


def spatial_gate(source_floor, pair_floor, sensor, approximation, processing,
                 clock_radius, forward_lipschitz, generator_error,
                 accuracy='1/1000'):
    mu, lam, eta, rho, xi, h, lip, eps, target = map(nonnegative, (
        source_floor, pair_floor, sensor, approximation, processing,
        clock_radius, forward_lipschitz, generator_error, accuracy))
    timing = lip*h
    mismatch = Q(8, 3)*eps
    delta = eta+rho+xi+timing+mismatch
    pair = prior.pair_gate(lam, delta, delta)
    source = prior.inverse_gate(mu, delta, target)
    return {'sensor': str(eta), 'approximation': str(rho),
            'processing': str(xi), 'timing': str(timing),
            'model_mismatch': str(mismatch), 'total_radius': str(delta),
            'source_floor': str(mu), 'pair_floor': str(lam),
            'target_relative_accuracy': str(target),
            'source_error_squared_upper': None if mu == 0 else str(delta*delta/mu),
            'pair_gate': pair, 'source_gate': source, 'passed': pair and source}


def arithmetic_gate(n, bias, gram_floor, normal_residual, sensor, approximation,
                    timing, mismatch, centering):
    if type(n) is not int or n < 2:
        raise ValueError('unknown integer coefficient index required')
    bias, f, residual, eta, nu, tau, kappa, xi = map(nonnegative, (
        bias, gram_floor, normal_residual, sensor, approximation,
        timing, mismatch, centering))
    if f == 0:
        raise ValueError('positive Gram floor required')
    radius = eta+nu+tau+kappa+xi
    margin = Q(1, 2)-bias-n*n*residual/f
    left, right = n**4*radius**2, margin**2*f
    return {'coefficient': n, 'combined_reading_radius': str(radius),
            'remaining_coefficient_margin': str(margin),
            'gate_left': str(left), 'gate_right': str(right),
            'passed': margin > 0 and left < right}
