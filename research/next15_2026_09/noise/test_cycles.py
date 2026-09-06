from fractions import Fraction as Q
from pathlib import Path
import json,unittest
import numpy as np
import cycle1 as c1
import cycle2 as c2
import cycle3 as c3

class N1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cert=c1.check()

    def test_complete_new_replay_and_precision(self):
        self.assertEqual(self.cert,c1.build(256))

    def test_exact_affine_exclusion_and_variance(self):
        d=self.cert
        for line in d['minorants']:
            self.assertGreater(Q(line['coefficient50_minorant_at_endpoint'][0]),Q(1,2))
            lo,hi=map(Q,line['normalized_slope'])
            self.assertLess(hi,0) if line['side']=='left' else self.assertGreater(lo,0)
        self.assertGreater(Q(d['coefficient50_variance_inflation_lower']),1)
        self.assertLess(Q(d['reference_complete_bias_upper']),Q(1,2))
        self.assertLess(c1.LEFT,c1.A0);self.assertLess(c1.A0,c1.RIGHT)

    def test_independent_raw_grid_responses_and_covariance(self):
        # Direct8900-row physical decoder; independent of closed kernel formula.
        t=(2*np.arange(8900)+1-8900)/10
        coeff=np.array(c1.base.REFERENCE_COEFFICIENTS)
        def w(m):
            theta=(2*np.arange(m)+1)*np.pi/m
            return (1+2*np.sum(coeff[:,None]*np.cos(np.arange(1,9)[:,None]*theta),axis=0))/m
        long=w(8900);short=np.zeros(8900);short[3175:5725]=w(2550)
        for row in self.cert['selected_mode_intervals']:
            phase=np.cos(t*np.log(row['k']/50))
            for name,weights in (('outer',long),('short',short)):
                value=np.dot(weights,phase);lo,hi=map(lambda z:float(Q(z)),row[name])
                self.assertLess(abs(value-(lo+hi)/2),2e-12)
        phi=np.exp(-1j*t[:,None]*np.log(np.arange(1,51))[None,:])
        def variance(weights):
            gram=phi.conj().T@(weights[:,None]*phi)
            e=np.zeros(50);e[49]=1
            left=np.linalg.solve(gram,e).conj()@phi.conj().T*weights
            return np.vdot(left,left).real
        outer=variance(long)
        for alpha in (float(c1.LEFT),float(c1.A0),float(c1.RIGHT)):
            actual=variance(alpha*short+(1-alpha)*long)/outer
            self.assertGreater(actual,float(Q(self.cert['coefficient50_variance_inflation_lower'])))
        # Deliberately dropping reuse changes the squared-weight noise model.
        a=float(c1.A0);correct=np.sum((a*short+(1-a)*long)**2)
        wrong=a*a*np.sum(short**2)+(1-a)**2*np.sum(long**2)
        self.assertGreater(correct,wrong)

    def test_divisor_counts_and_source_contract_controls(self):
        def convolution(n,d):
            out=[0]*(n+1);out[1]=1
            for _ in range(d):out=[0]+[sum(out[j] for j in range(1,k+1) if k%j==0) for k in range(1,n+1)]
            return out
        values=convolution(240,14)
        for k in c1.MODES:self.assertEqual(c1.divisor14(k),values[k])
        with self.assertRaises(ValueError):c1.divisor14(0)
        with self.assertRaises(ValueError):c1.build(64)
        with self.assertRaises(ValueError):c1.base.require_parameters({'degree':13},{'degree':14})

class N2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cert=c2.check()

    def test_full_vector_at_independent_precision(self):
        evidence,vector=c2.build(256)
        self.assertEqual(self.cert,evidence)
        self.assertEqual(vector,json.loads((c1.HERE/'cycle2_correction.json').read_text()))
        self.assertEqual(len(vector['positive_complex_numerators']),4450)

    def test_independent_mpmath_full_tail_values(self):
        import mpmath as mp
        vector=json.loads((c1.HERE/'cycle2_correction.json').read_text())
        with mp.workdps(75):
            for j in (0,127,4449):
                s=mp.mpc(2,mp.mpf(2*j+1)/10)
                value=(mp.zeta(s)**14-sum(c1.divisor14(n)*mp.exp(-s*mp.log(n)) for n in range(1,51)))/2
                r,i=vector['positive_complex_numerators'][j]
                approx=mp.mpc(mp.mpf(r)/c2.DEN,mp.mpf(i)/c2.DEN)
                self.assertLess(abs(value-approx),mp.mpf(1)/c2.DEN)
                self.assertLess(abs((mp.zeta(s.conjugate())**14-sum(c1.divisor14(n)*mp.exp(-s.conjugate()*mp.log(n)) for n in range(1,51)))/2-approx.conjugate()),mp.mpf(1)/c2.DEN)

    def test_strict_budgets_and_negative_controls(self):
        for name,data in self.cert['designs'].items():
            bias=list(map(Q,data['complete_bias_upper']));qr=list(map(Q,data['gram_rows']))
            eta=Q(data['declared_sensor_radius'])
            self.assertEqual(c2.consequence(bias,qr,eta),data)
            self.assertGreater(Q(data['rounding_margin_after_declared_errors_lower']),0)
            with self.assertRaises(ValueError):c2.consequence(bias,qr,eta*2)
            with self.assertRaises(ValueError):c2.consequence(bias,qr,eta,xi=-1)
            with self.assertRaises(ValueError):c2.consequence(bias,qr,-eta)
            with self.assertRaises(ValueError):c2.consequence([Q(1)]*50,qr,0)
        with self.assertRaises(ValueError):c2.correction(64)
        self.assertGreater(Q(self.cert['reference_noise_radius_gain_interval'][0]),127)

    def test_midpoint_geometry_and_unchanged_noise_response(self):
        # Independent finite source-tail endpoint enumeration, including all
        # signs. Subtracting a known center changes bias but no noise response.
        import itertools
        t=np.array([-.7,-.1,.1,.7]);ks=np.array([51,54,72])
        d=np.array([c1.divisor14(int(k)) for k in ks])
        columns=np.exp(-1j*t[:,None]*np.log(ks))/ks**2
        center=columns@(d/2)
        for bits in itertools.product((0,1),repeat=3):
            a=d*np.array(bits);residual=columns@a-center
            self.assertLessEqual(np.max(abs(residual)),np.sum(d/(2*ks**2))+1e-12)
            np.testing.assert_allclose(columns@(d-a)-center,-residual,rtol=1e-13,atol=1e-13)
        matrix=np.array([[1+2j,2,1j,-1],[1,-2j,3,1]])
        source=columns@d;noise=np.array([1+2j,3-1j,-2j,.2])
        np.testing.assert_allclose(matrix@(source+noise-center)-matrix@(source-center),matrix@noise)

class N3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cert=c3.check()

    def test_full_arb_reconstruction_and_precision(self):
        self.assertEqual(self.cert,c3.build(256))

    def test_independent_augmented_physical_map_and_worked_source(self):
        t=(2*np.arange(8900)+1-8900)/10
        coeff=np.array(c1.base.REFERENCE_COEFFICIENTS)
        def w(m):
            theta=(2*np.arange(m)+1)*np.pi/m
            return (1+2*np.sum(coeff[:,None]*np.cos(np.arange(1,9)[:,None]*theta),axis=0))/m
        long=w(8900);short=np.zeros(8900);short[3175:5725]=w(2550)
        phi=np.exp(-1j*t[:,None]*np.log(np.arange(1,51))[None,:])
        raw=json.loads((c1.HERE/'cycle2_correction.json').read_text())
        positive=np.array([complex(r/c2.DEN,i/c2.DEN) for r,i in raw['positive_complex_numerators']])
        center=np.concatenate([positive[::-1].conj(),positive])
        a=np.zeros(50);a[0]=1;a[1]=7;a[48]=1;a[49]=1
        source=phi@(a/np.arange(1,51)**2)
        drift=(100+37j)+(10000+2000j)*t
        failed_original=False
        for name,weights in [('outer',long),('multi',float(c1.A0)*short+(1-float(c1.A0))*long)]:
            cert=self.cert['designs'][name]
            psi=t/np.sqrt(np.dot(weights,t*t))
            g=phi.conj().T@(weights*psi)
            for actual,(lo,hi) in zip(g,cert['nuisance_cross_imaginary_intervals']):
                self.assertLess(abs(actual.real),2e-13)
                self.assertLess(abs(actual.imag-(float(Q(lo))+float(Q(hi)))/2),2e-13)
            augmented=np.column_stack([phi,psi])
            gram=augmented.conj().T@(weights[:,None]*augmented)
            self.assertGreater(np.linalg.eigvalsh(gram)[0],1-float(Q(cert['augmented_gram_defect_upper']))-2e-13)
            noise=float(Q(cert['sensor_error_radius']))*phi[:,49]
            y=source+drift+noise-center
            recovered=np.linalg.solve(gram,augmented.conj().T@(weights*y))[:50]*np.arange(1,51)**2
            np.testing.assert_array_equal(np.rint(recovered[1:].real),a[1:])
            # Coefficient1 is replaced by its known normalization. Treating
            # the fitted constant as a recovered source coefficient is wrong.
            self.assertGreater(abs(recovered[0]-1),10)
            original=np.linalg.solve(gram[:50,:50],phi.conj().T@(weights*y))*np.arange(1,51)**2
            failed_original |= bool(np.any(np.rint(original[1:].real)!=a[1:]))
        self.assertTrue(failed_original)

    def test_exact_constant_alias_and_contract_controls(self):
        # Distinct legal unknowna1 values have exactly identical data after
        # compensating the arbitrary constant baseline; no algorithm helps.
        self.assertEqual(Q(0)+Q(1),Q(1)+Q(0))
        altered=dict(self.cert['inputs']);altered['known_a1']=0
        with self.assertRaises(ValueError):c3.build(inputs=altered)
        from unittest.mock import patch
        with patch.object(c2,'check',side_effect=ValueError('tampered supplied correction')):
            with self.assertRaises(ValueError):c3.check()
        altered=dict(self.cert['inputs']);altered['measurement_count']=8901
        with self.assertRaises(ValueError):c3.build(inputs=altered)
        for d in self.cert['designs'].values():
            args=[list(map(Q,d['original_complete_bias_upper'])),list(map(Q,d['original_gram_rows'])),list(map(Q,d['nuisance_cross_absolute_upper'])),Q(d['centered_tail_pointwise_upper']),Q(d['sensor_error_radius']),Q(d['digital_correction_radius'])]
            with self.assertRaises(ValueError):c3.derive(*args[:4],args[4]*2,args[5])
            with self.assertRaises(ValueError):c3.derive(args[0],args[1],[Q(1)]*50,*args[3:])
            with self.assertRaises(ValueError):c3.derive(*args[:4],-1,args[5])

if __name__=='__main__':unittest.main(verbosity=2)
