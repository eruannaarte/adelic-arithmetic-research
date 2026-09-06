"""Independent physical diagnostics and adverse controls; no sampled proof."""
from pathlib import Path
from fractions import Fraction as Q
import copy, json, math, sys, unittest
import numpy as np
import mpmath as mp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_certificate as consumer
import oscillatory_channels as producer


def physical_arrays():
    t = (2*np.arange(8900)+1-8900)/10
    x = t/890
    coefficients = np.array(producer.old.prior.base.REFERENCE_COEFFICIENTS)
    def weights(m):
        angle = (2*np.arange(m)+1)*np.pi/m
        return (1+2*np.sum(coefficients[:, None]*np.cos(
            np.arange(1, 9)[:, None]*angle), axis=0))/m
    outer = weights(8900)
    inner = np.zeros(8900)
    inner[3175:5725] = weights(2550)
    alpha = float(producer.old.prior.A0)
    phi = np.exp(-1j*t[:, None]*np.log(np.arange(1, 51)))
    return t, x, phi, {'multi': alpha*inner+(1-alpha)*outer, 'outer': outer}, inner, outer


def numerical_basis(weights, x, degree):
    # Independent weighted vector modified Gram--Schmidt, reorthogonalized;
    # no producer polynomial coefficients, moments or interval operations.
    basis = [np.ones(len(x))]
    for k in range(1, degree+1):
        v = x**k
        for _ in range(2):
            for b in basis:
                v -= np.dot(weights*b, v)*b
        v /= np.sqrt(np.dot(weights*v, v))
        basis.append(v)
    return np.column_stack(basis[1:])


class OscillatoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((HERE/'evidence.json').read_text())
        cls.core = json.loads((HERE/'core_evidence.json').read_text())
        cls.physical = physical_arrays()

    def test_exact_consumers_and_frozen_core(self):
        self.assertTrue(consumer.check(self.core)['verified'])
        result = consumer.check(self.data, extended=True)
        self.assertEqual(sum(row['certified'] for rows in result['designs'].values() for row in rows), 8)
        for name, data in self.data['designs'].items():
            self.assertEqual(data['degrees'][0], self.core['designs'][name]['degrees'][0])
            old = data['old_pointwise_degree_six_control']
            self.assertFalse(old['positive_rounding_margin'])
            self.assertIsNone(old['sufficient_total_noise_radius_squared'])

    def test_summation_by_parts_identity_and_essential_endpoints(self):
        for r in ([Q(1)]*9, [Q(2), Q(-3), Q(1, 2), Q(7)], [Q(0), Q(1), Q(0)]):
            def at(k):
                return r[k] if 0 <= k < len(r) else Q(0)
            delta = [at(j)-2*at(j-1)+at(j-2) for j in range(len(r)+2)]
            for z in (Q(-1), Q(1, 2), Q(-2, 3)):
                left = (1-z)**2*sum((a*z**j for j, a in enumerate(r)), Q())
                right = sum((a*z**j for j, a in enumerate(delta)), Q())
                self.assertEqual(left, right)
        r = [Q(1)]*9
        internal = sum(abs(r[j]-2*r[j-1]+r[j-2]) for j in range(2, len(r)))
        self.assertEqual(internal, 0)
        self.assertEqual(sum(a*(-1)**j for j, a in enumerate(r)), 1)
        self.assertEqual(sum(abs(a) for a in [1, -1]+[0]*7+[-1, 1]), 4)

    def test_finite_phase_bound_and_remote_alias_control(self):
        consumer.phase_check(self.data['phase_contract'])
        for n in (51, 53, 1000, 1048576, 10**9, 10**12):
            self.assertGreater(abs(1-np.exp(-1j*np.log(n)/5)), 2/3)
        # The first nonzero sampling alias lies above the certified finite
        # band. A nearby integer refutes extending that denominator to infinity.
        n = round(math.exp(10*math.pi))
        self.assertGreater(n, 10**12)
        self.assertLess(abs(1-np.exp(-1j*math.log(n)/5)), 1e-10)

    def test_independent_zeta_and_divisor_convolution(self):
        with mp.workdps(75):
            lo, hi = map(Q, self.data['zeta_three_halves_interval'])
            value = mp.zeta(mp.mpf(3)/2)
            self.assertLess(mp.mpf(lo.numerator)/lo.denominator, value)
            self.assertLess(value, mp.mpf(hi.numerator)/hi.denominator)
        d = [0]*257
        d[1] = 1
        for _ in range(14):
            nxt = [0]*257
            for a in range(1, 257):
                for n in range(a, 257, a):
                    nxt[n] += d[a]
            d = nxt
        self.assertEqual(d[1:], [producer.old.prior.divisor14(n) for n in range(1, 257)])

    def test_independent_actual_basis_variations_crosses_and_gram(self):
        _, x, phi, designs, _, _ = self.physical
        for name, weights in designs.items():
            psi = numerical_basis(weights, x, 12)
            np.testing.assert_allclose(psi.T@(weights[:, None]*psi), np.eye(12), atol=2e-12)
            np.testing.assert_allclose(weights@psi, np.zeros(12), atol=2e-14)
            data = self.data['designs'][name]
            physical = data['physical_polynomials']
            cross = phi.conj().T@(weights[:, None]*psi)
            for k in range(12):
                r = weights*psi[:, k]
                l1 = np.abs(r).sum()
                variation = np.abs(np.diff(np.pad(r, (2, 2)), n=2)).sum()
                for value, pair in ((l1, physical['weighted_l1'][k]),
                                    (variation, physical['zero_extended_second_difference_l1'][k])):
                    midpoint = float(sum(map(Q, pair))/2)
                    self.assertLess(abs(value-midpoint), 2e-11)
                for n in range(50):
                    pair = physical['cross_real_even_imaginary_odd'][n][k]
                    midpoint = float(sum(map(Q, pair))/2)
                    actual = cross[n, k].imag if (k+1) % 2 else cross[n, k].real
                    self.assertLess(abs(actual-midpoint), 2e-11)
            for record in data['degrees']:
                p = record['degree']
                X = np.column_stack([phi, psi[:, :p]])
                H = X.conj().T@(weights[:, None]*X)
                self.assertGreater(np.linalg.eigvalsh(H)[0],
                                   1-float(Q(record['augmented_gram_defect']))-2e-12)

    def test_physical_oscillatory_responses_obey_complete_variation_bound(self):
        t, x, _, designs, _, _ = self.physical
        for name, weights in designs.items():
            psi = numerical_basis(weights, x, 12)
            variations = [float(Q(pair[1])) for pair in self.data['designs'][name]
                          ['physical_polynomials']['zero_extended_second_difference_l1']]
            for n in (51, 53, 1000, 1048576, 10**6, 10**12):
                response = abs(psi.T@(weights*np.exp(-1j*t*np.log(n))))
                denominator = abs(1-np.exp(-1j*np.log(n)/5))**2
                self.assertTrue(np.all(response <= np.array(variations)/denominator+2e-12))

    def test_actual_source_drift_and_worst_coefficient_noise(self):
        t, x, phi, designs, _, _ = self.physical
        vector = json.loads((producer.old.OLD/'cycle2_correction.json').read_text())
        positive = np.array([complex(r/10**20, i/10**20)
                             for r, i in vector['positive_complex_numerators']])
        correction = np.concatenate([positive[::-1].conj(), positive])
        a = np.zeros(50)
        a[0], a[1], a[48], a[49] = 1, 7, 1, 1
        source = phi@(a/np.arange(1, 51)**2)
        for n in (51, 60, 72):
            source += (producer.old.prior.divisor14(n)//2)*np.exp(-1j*t*np.log(n))/n**2
        for name, weights in designs.items():
            psi = numerical_basis(weights, x, 12)
            for record in self.data['designs'][name]['degrees']:
                p = record['degree']
                eta = float(Q(record['declared_sensor_radius']))
                X = np.column_stack([phi, psi[:, :p]])
                H = X.conj().T@(weights[:, None]*X)
                target = np.zeros(50+p, complex)
                target[49] = 1
                inverse = np.linalg.solve(H, target)
                noise = eta*(X@inverse)/np.sqrt(inverse[49].real)
                self.assertLess(abs(np.dot(weights, abs(noise)**2)-eta**2), 1e-18)
                drift = sum((1000000+300000j)/(k+1)*x**k for k in range(p+1))
                y = source+drift+noise-correction
                fitted = np.linalg.solve(H, X.conj().T@(weights*y))
                decoded = fitted[:50]*np.arange(1, 51)**2
                np.testing.assert_array_equal(np.rint(decoded[1:].real), a[1:])
                self.assertGreater(abs(decoded[0]-1), 100)

    def test_conditional_exact_normal_residual_contract(self):
        gates = 0
        for data in self.data['designs'].values():
            for record in data['degrees']:
                gates += consumer.normal_residual_budget(record)['coordinate_gates']
                with self.assertRaises(ValueError):
                    consumer.normal_residual_budget(record, Q(1, 100))
                with self.assertRaises(ValueError):
                    consumer.normal_residual_budget(record, Q(-1))
        self.assertEqual(gates, 392)
        # Exact normal residual and observation noise have different gains.
        H = np.diag([1/4, 1.0])
        residual = np.array([1e-8, 0.0])
        solve_error = np.linalg.solve(H, residual)
        self.assertAlmostEqual(np.linalg.norm(solve_error), 4e-8)
        self.assertGreater(np.linalg.norm(solve_error), 1e-8/np.sqrt(1/4))

    def test_reused_covariance_and_unbounded_projection_leakage(self):
        _, x, phi, designs, inner, outer = self.physical
        w = designs['multi']
        X = np.column_stack([phi, numerical_basis(w, x, 12)])
        H = X.conj().T@(w[:, None]*X)
        L = np.linalg.solve(H, X.conj().T*w)
        rhs = X.conj().T@((w*w)[:, None]*X)
        formula = np.linalg.solve(H, np.linalg.solve(H, rhs).conj().T).conj().T
        np.testing.assert_allclose(L@L.conj().T, formula, atol=3e-18, rtol=3e-11)
        alpha = float(producer.old.prior.A0)
        self.assertGreater(np.sum(w*w-alpha*alpha*inner*inner-(1-alpha)**2*outer*outer), 0)
        epsilon = Q(1, 10**12)
        self.assertEqual(epsilon*10**20, 10**8)

    def test_missing_remote_and_false_guarantees_rejected(self):
        mutations = [
            lambda d: d.__setitem__('known_a1', 0),
            lambda d: d.__setitem__('measurement_count', 8899),
            lambda d: d.__setitem__('predecessor_sha256', '0'*64),
            lambda d: d['phase_contract'].__setitem__('cutoff', 10**14),
            lambda d: d['phase_contract'].__setitem__('phase_denominator_strict_lower', '1'),
            lambda d: d.__setitem__('complete_remote_centered_mass_upper', '0'),
            lambda d: d['designs']['multi']['complete_remote_channel_upper'].__setitem__(0, '0'),
            lambda d: d['designs']['outer']['physical_polynomials']['weighted_l1'].pop(),
            lambda d: d['designs']['multi']['degrees'][0].__setitem__('declared_sensor_radius', '1/100'),
            lambda d: d['designs']['outer']['old_pointwise_degree_six_control'].__setitem__('rounding_certified', True),
        ]
        for mutation in mutations:
            changed = copy.deepcopy(self.data)
            mutation(changed)
            with self.assertRaises(ValueError):
                consumer.check(changed, extended=True)
        with self.assertRaises(ValueError):
            producer.basis_and_channels([], 13)


if __name__ == '__main__':
    unittest.main(verbosity=2)
