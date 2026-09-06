"""Adverse and independent physical-map controls for the new theorem."""
import copy, json, sys, unittest
from pathlib import Path
from fractions import Fraction as Q
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import polynomial_drift as producer
import check_certificate as independent


def physical_arrays():
    t = (2*np.arange(8900)+1-8900)/10
    x = t/890
    coefficients = np.array(producer.prior.base.REFERENCE_COEFFICIENTS)
    def weights(m):
        angle = (2*np.arange(m)+1)*np.pi/m
        return (1+2*np.sum(coefficients[:, None]*
                np.cos(np.arange(1, 9)[:, None]*angle), axis=0))/m
    outer = weights(8900)
    inner = np.zeros(8900)
    inner[3175:5725] = weights(2550)
    multi = float(producer.prior.A0)*inner+(1-float(producer.prior.A0))*outer
    phi = np.exp(-1j*t[:, None]*np.log(np.arange(1, 51)))
    return t, x, phi, {'multi': multi, 'outer': outer}, inner, outer


def numerical_basis(weights, x, degree):
    # Independent direct-vector weighted modified Gram--Schmidt, with no
    # producer moments, polynomial coefficients or enclosure routines.
    basis = [np.ones(len(x))]
    for k in range(1, degree+1):
        residual = x**k
        for previous in basis:
            residual -= np.dot(weights*previous, residual)*previous
        residual /= np.sqrt(np.dot(weights*residual, residual))
        basis.append(residual)
    return np.column_stack(basis[1:])


class PolynomialDriftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = producer.check()

    def test_full_reconstruction_at_256_bits(self):
        self.assertEqual(self.certificate, producer.build(256))

    def test_exact_consumer_and_negative_margin_gates(self):
        result = independent.check(self.certificate)
        self.assertEqual(sum(row['certified'] for rows in result.values() for row in rows), 9)
        self.assertEqual([r['degree'] for r in result['multi'] if not r['certified']], [6])
        self.assertEqual([r['degree'] for r in result['outer'] if not r['certified']], [5, 6])
        for rows in result.values():
            for row in rows:
                if not row['certified']:
                    self.assertIsNone(row['sensor_threshold_interval'])
                    self.assertGreater(Q(row['max_bias_upper']), Q(1, 2))

    def test_independent_full_grid_basis_crosses_and_gram(self):
        _, x, phi, designs, _, _ = physical_arrays()
        for name, weights in designs.items():
            data = self.certificate['designs'][name]
            psi = numerical_basis(weights, x, 6)
            np.testing.assert_allclose(psi.T@(weights[:, None]*psi), np.eye(6), atol=2e-12)
            np.testing.assert_allclose(weights@psi, np.zeros(6), atol=2e-14)
            numerical_cross = phi.conj().T@(weights[:, None]*psi)
            raw = data['physical_polynomial_reconstruction']
            for n in range(50):
                for k in range(6):
                    lo, hi = map(Q, raw['cross_channels_real_for_even_imaginary_for_odd'][n][k])
                    coordinate = numerical_cross[n, k].imag if (k+1) % 2 else numerical_cross[n, k].real
                    other = numerical_cross[n, k].real if (k+1) % 2 else numerical_cross[n, k].imag
                    self.assertLess(abs(coordinate-float((lo+hi)/2)), 3e-13)
                    self.assertLess(abs(other), 3e-13)
            for k, bound in enumerate(raw['weighted_absolute_polynomial_norms']):
                lo, hi = map(Q, bound)
                self.assertLess(abs(np.dot(weights, abs(psi[:, k]))-float((lo+hi)/2)), 3e-12)
            for degree in (2, 4, 6):
                matrix = np.column_stack([phi, psi[:, :degree]])
                gram = matrix.conj().T@(weights[:, None]*matrix)
                floor = 1-float(Q(data['degrees'][degree-1]['augmented_gram_defect_upper']))
                self.assertGreater(np.linalg.eigvalsh(gram)[0], floor-3e-13)

    def test_higher_drift_full_source_example_with_worst_direction_noise(self):
        t, x, phi, designs, _, _ = physical_arrays()
        vector = json.loads((producer.OLD/'cycle2_correction.json').read_text())
        positive = np.array([complex(r/10**20, i/10**20)
                             for r, i in vector['positive_complex_numerators']])
        correction = np.concatenate([positive[::-1].conj(), positive])
        a = np.zeros(50)
        a[0], a[1], a[48], a[49] = 1, 7, 1, 1
        source = phi@(a/np.arange(1, 51)**2)
        # These are actual allowed finite sources, including omitted modes.
        # Their infinite midpoint correction is retained without truncation.
        for k in (51, 60, 72):
            source += (producer.prior.divisor14(k)//2)*np.exp(-1j*t*np.log(k))/k**2
        affine_failures = 0
        for name, degrees in [('multi', (2, 3, 4, 5)), ('outer', (2, 3, 4))]:
            weights = designs[name]
            psi = numerical_basis(weights, x, max(degrees))
            for p in degrees:
                eta = float(Q(self.certificate['designs'][name]['degrees'][p-1]['declared_sensor_radius']))
                matrix = np.column_stack([phi, psi[:, :p]])
                gram = matrix.conj().T@(weights[:, None]*matrix)
                target = np.zeros(50+p, dtype=complex)
                target[49] = 1
                inverse_column = np.linalg.solve(gram, target)
                noise = eta*(matrix@inverse_column)/np.sqrt(inverse_column[49].real)
                self.assertLess(abs(np.dot(weights, abs(noise)**2)-eta**2), 1e-18)
                drift = sum((100000000/(k+1)+30000000j/(k+1))*x**k for k in range(p+1))
                y = source+drift+noise-correction
                solved = np.linalg.solve(gram, matrix.conj().T@(weights*y))
                decoded = solved[:50]*np.arange(1, 51)**2
                np.testing.assert_array_equal(np.rint(decoded[1:].real), a[1:])
                self.assertGreater(abs(decoded[0]-1), 100)
                # The inherited affine-only fit does not silently remove a
                # higher degree nuisance even with the same physical data.
                old_matrix = np.column_stack([phi, psi[:, :1]])
                old_gram = old_matrix.conj().T@(weights[:, None]*old_matrix)
                old = np.linalg.solve(old_gram, old_matrix.conj().T@(weights*y))[:50]*np.arange(1, 51)**2
                affine_failures += bool(np.any(np.rint(old[1:].real) != a[1:]))
        self.assertGreater(affine_failures, 0)

    def test_projection_answer_set_identity_and_reused_covariance(self):
        _, x, phi, designs, inner, outer = physical_arrays()
        weights = designs['multi']
        psi = np.column_stack([np.ones(8900), numerical_basis(weights, x, 5)])
        # Weighted projection is contractive, and the remainder lies exactly
        # in the nuisance subspace. This is the constructive reverse direction
        # of the theorem, checked on a deterministic complex physical vector.
        residual = phi[:, 49]+(2+3j)*x**3+.4j*x**5
        coefficients = psi.conj().T@(weights*residual)
        projected = residual-psi@coefficients
        np.testing.assert_allclose(psi.conj().T@(weights*projected), np.zeros(6), atol=1e-13)
        np.testing.assert_allclose(projected+psi@coefficients, residual, atol=1e-14)
        self.assertLessEqual(np.dot(weights, abs(projected)**2), np.dot(weights, abs(residual)**2)+1e-12)
        matrix = np.column_stack([phi, psi[:, 1:]])
        gram = matrix.conj().T@(weights[:, None]*matrix)
        physical = np.linalg.solve(gram, matrix.conj().T*weights)
        covariance = physical@physical.conj().T
        rhs = matrix.conj().T@((weights**2)[:, None]*matrix)
        formula = np.linalg.solve(gram, np.linalg.solve(gram, rhs).conj().T).conj().T
        np.testing.assert_allclose(covariance, formula, atol=3e-18, rtol=2e-11)
        alpha = float(producer.prior.A0)
        false_weight_square = alpha**2*inner**2+(1-alpha)**2*outer**2
        self.assertGreater(np.sum(weights**2-false_weight_square), 0)

    def test_l1_refinement_is_needed_for_quintic_certificate(self):
        data = self.certificate['designs']['multi']
        numeric = data['physical_polynomial_reconstruction']
        cross = [[max(abs(Q(lo)), abs(Q(hi))) for lo, hi in row]
                 for row in numeric['cross_channels_real_for_even_imaginary_for_odd']]
        bias = list(map(Q, data['original_complete_bias_upper']))
        qr = list(map(Q, data['original_gram_rows']))
        h0 = Q(self.certificate['full_pointwise_centered_tail_interval'][1])
        coarse = producer.rational_consequences(bias, qr, cross, [Q(1)]*6, h0, 5, None)
        self.assertFalse(coarse['positive_rounding_margin'])
        self.assertGreater(max(map(Q, coarse['complete_decoded_bias_upper'][1:])), Q(1, 2))
        self.assertTrue(data['degrees'][4]['rounding_certified'])

    def test_tampering_and_missing_complete_channel_rejected(self):
        mutations = [
            lambda d: d['inputs'].__setitem__('known_a1', 0),
            lambda d: d['inputs'].__setitem__('measurement_count', 8899),
            lambda d: d.__setitem__('digital_correction_sha256', '0'*64),
            lambda d: d['designs']['multi']['degrees'][4].__setitem__('complete_centered_nuisance_channels_upper', ['0']*5),
            lambda d: d['designs']['multi']['degrees'][5].__setitem__('rounding_certified', True),
            lambda d: d['designs']['outer']['physical_polynomial_reconstruction']['weighted_absolute_polynomial_norms'].pop(),
            lambda d: d['designs']['multi']['degrees'][4].__setitem__('declared_sensor_radius', '1/100'),
        ]
        for change in mutations:
            document = copy.deepcopy(self.certificate)
            change(document)
            with self.assertRaises(ValueError):
                independent.check(document)
        changed = copy.deepcopy(producer.INPUTS)
        changed['known_a1'] = 0
        with self.assertRaises(ValueError):
            producer.build(inputs=changed)
        with self.assertRaises(ValueError):
            producer.build(64)

    def test_exact_alias_boundaries(self):
        # Exact a1/constant alias in the declared integer envelope.
        self.assertEqual(Q(0)+Q(1), Q(1)+Q(0))
        # Lagrange interpolation makes an arbitrary m-point nuisance exact
        # by degree m-1. Check the cardinal identities in rational arithmetic;
        # the proof then allows the complex arithmetic response as ordinates.
        nodes = [Q(2*j+1-7, 10) for j in range(7)]
        for i, xi in enumerate(nodes):
            for j, xj in enumerate(nodes):
                value = Q(1)
                for k, xk in enumerate(nodes):
                    if k != i:
                        value *= (xj-xk)/(xi-xk)
                self.assertEqual(value, int(i == j))


if __name__ == '__main__':
    unittest.main(verbosity=2)
