"""Finite witness checks plus direct-model controls, not analytic proof tests."""
from copy import deepcopy
from fractions import Fraction as Q
import itertools
import json
import unittest

import numpy as np

import certificate_checker as cc


INPUTS = json.loads((cc.ROOT/'inputs.json').read_text())
CERTIFICATE = json.loads((cc.ROOT/'certificate.json').read_text())
LAM = np.log([2., 3., 5.])
A = np.arange(4)
Z = A - 1.5
# An orthonormal basis of the real zero-sum space, columns indexed by state.
HELMERT = np.array([[1., -1., 0., 0.], [1., 1., -2., 0.], [1., 1., 1., -3.]])
HELMERT /= np.sqrt(np.array([2., 6., 12.]))[:, None]


def raw_readings(q, times):
    return np.array([np.prod(np.sum(q*np.exp(-1j*t*LAM[:, None]*A), axis=1)) for t in times])


def centered_jacobian(q, times, windings):
    result = np.zeros((6, 9), dtype=complex)
    for row, (time, winding) in enumerate(zip(times, windings)):
        theta = time*LAM - 2*np.pi*np.array(winding)
        vectors = np.exp(-1j*theta[:, None]*Z)
        values = np.sum(q*vectors, axis=1)
        for j in range(3):
            result[row, 3*j:3*j+3] = (HELMERT @ vectors[j]) * np.prod(np.delete(values, j))
    return result


def ideal_jacobian():
    result = np.zeros((6, 9), dtype=complex)
    for row, (axis, multiplier) in enumerate(zip(cc.TARGET_AXES, cc.TARGET_MULTIPLIERS)):
        result[row, 3*axis:3*axis+3] = HELMERT @ np.exp(-1j*np.pi*float(multiplier)*Z)
    return result


def realify(matrix):
    return np.vstack([matrix.real, matrix.imag])


class CertificateTests(unittest.TestCase):
    def test_complete_reconstruction(self):
        self.assertEqual(cc.build(INPUTS), CERTIFICATE)

    def test_higher_precision_reconstruction(self):
        refined = cc.build(INPUTS, 512)
        self.assertEqual(refined['schedules'], CERTIFICATE['schedules'])
        self.assertEqual(refined['five_reading_local_witness'], CERTIFICATE['five_reading_local_witness'])

    def test_six_distinct_resonant_readings_are_blind(self):
        times = 2*np.pi*np.arange(1, 7)/np.log(2.)
        q = np.eye(4)[[0, 0, 0]]
        other = np.eye(4)[[1, 0, 0]]
        self.assertLess(np.linalg.norm(raw_readings(q, times)-raw_readings(other, times)), 1e-12)

    def test_exact_gram_consequences(self):
        for record in CERTIFICATE['schedules'].values():
            errors = [[Q(x) for x in row] for row in record['phase_errors_upper']]
            actual = cc.derive(errors)
            for key, value in actual.items():
                self.assertEqual(value, record[key])

    def test_inflated_claim_rejected(self):
        spec = deepcopy(INPUTS['schedules']['balanced'])
        spec['factor_floor_claim'] = '1'
        with self.assertRaises(ValueError):
            cc.schedule_bound(spec)

    def test_wrong_winding_rejected(self):
        spec = deepcopy(INPUTS['schedules']['balanced'])
        spec['windings'][0][0] += 1
        with self.assertRaises(ValueError):
            cc.schedule_bound(spec)

    def test_duplicate_and_zero_time_rejected(self):
        for value in ('0', INPUTS['schedules']['balanced']['times'][1]):
            spec = deepcopy(INPUTS['schedules']['balanced'])
            spec['times'][0] = value
            with self.assertRaises(ValueError):
                cc.schedule_bound(spec)

    def test_bad_schedule_rejected(self):
        spec = deepcopy(INPUTS['schedules']['balanced'])
        spec['times'] = [str(i) for i in range(1, 7)]
        with self.assertRaises(ValueError):
            cc.schedule_bound(spec)

    def test_excess_clock_rejected(self):
        spec = deepcopy(INPUTS['schedules']['balanced'])
        spec['clock_radius'] = '1'
        with self.assertRaises(ValueError):
            cc.schedule_bound(spec)

    def test_negative_noise_or_floor_rejected(self):
        for field in ('worked_noise_radius', 'factor_floor_claim'):
            spec = deepcopy(INPUTS['schedules']['balanced'])
            spec[field] = '-1'
            with self.assertRaises(ValueError):
                cc.schedule_bound(spec)

    def test_centering_matches_raw_model(self):
        rng = np.random.default_rng(260905)
        spec = INPUTS['schedules']['balanced']
        times = np.array([float(Q(x)) for x in spec['times']])
        for _ in range(30):
            q = rng.dirichlet(np.ones(4), 3)
            raw = raw_readings(q, times)
            for row, (t, winding) in enumerate(zip(times, spec['windings'])):
                theta = t*LAM - 2*np.pi*np.array(winding)
                centered = np.prod(np.sum(q*np.exp(-1j*theta[:, None]*Z), axis=1))
                multiplier = (-1)**(3*sum(winding))*np.exp(1.5j*t*sum(LAM))
                self.assertLess(abs(centered-multiplier*raw[row]), 3e-11)

    def test_all_vertex_derivatives_and_clock_corners(self):
        # Multi-affinity makes vertex coverage a strong direct-model control;
        # this float test is still not the interval certificate's proof.
        ideal = ideal_jacobian()
        q_vertices = [np.eye(4)[list(indices)] for indices in itertools.product(range(4), repeat=3)]
        for name in ('short', 'balanced', 'high_floor'):
            spec = INPUTS['schedules'][name]
            times = np.array([float(Q(x)) for x in spec['times']])
            err = float(Q(CERTIFICATE['schedules'][name]['operator_error_upper']))
            for dt in (-.001, 0., .001):
                for q in q_vertices:
                    difference = centered_jacobian(q, times+dt, spec['windings']) - ideal
                    self.assertLess(np.linalg.norm(realify(difference), 2), err+1e-10)

    def test_secants_include_simplex_boundaries(self):
        rng = np.random.default_rng(260905)
        spec = INPUTS['schedules']['balanced']
        times = np.array([float(Q(x)) for x in spec['times']])
        floor = float(Q(CERTIFICATE['schedules']['balanced']['factor_floor_lower']))
        candidates = [rng.dirichlet(np.ones(4), 3) for _ in range(80)]
        candidates += [np.eye(4)[list(idx)] for idx in itertools.product(range(4), repeat=3)]
        for q, other in zip(candidates, candidates[1:] + candidates[:1]):
            for dt in (-.001, 0., .001):
                diff = raw_readings(q, times+dt) - raw_readings(other, times+dt)
                self.assertGreaterEqual(np.linalg.norm(diff)+1e-10, floor*np.linalg.norm(q-other))

    def test_unknown_clock_displacement_direct_model(self):
        spec = INPUTS['schedules']['balanced']
        times = np.array([float(Q(x)) for x in spec['times']])
        radius = float(Q(CERTIFICATE['schedules']['balanced']['unknown_clock_response_radius_upper']))
        for indices in itertools.product(range(4), repeat=3):
            q = np.eye(4)[list(indices)]
            for dt in (-.001, .001):
                drift = np.linalg.norm(raw_readings(q, times+dt)-raw_readings(q, times))
                self.assertLessEqual(drift, radius+1e-10)

    def test_half_dft_even_odd_and_small_cases(self):
        rng = np.random.default_rng(260905)
        for s in range(2, 10):
            for _ in range(20):
                h = rng.normal(size=s); h -= h.mean()
                values = np.fft.fft(h)
                energy = np.linalg.norm(values[1:s//2+1])**2
                self.assertGreaterEqual(energy+1e-10, s/2*np.linalg.norm(h)**2)
                if s%2:
                    self.assertAlmostEqual(energy, s/2*np.linalg.norm(h)**2, places=9)


if __name__ == '__main__':
    unittest.main()
