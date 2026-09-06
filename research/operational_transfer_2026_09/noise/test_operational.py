"""Tests of solver failure, nonlinear drift budgets, and refusal contracts."""
from fractions import Fraction as Q
from copy import deepcopy
from math import factorial
import json, unittest
from flint import arb,acb,ctx
import physical, certify
from demo import ETA, NU


class OperationalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=physical.PhysicalModel('multi',8,256)
        cls.data=json.loads((physical.HERE/'data_large.json').read_text())
        cls.saved=json.loads((physical.HERE/'result_multi_large.json').read_text())
        cls.proposal=cls.saved['proposal']

    def test_failed_float_proposal_is_not_accepted(self):
        initial=self.saved['initial_proposal']
        self.assertEqual(initial['status'],'not_certified')
        self.assertGreater(Q(initial['normal_residual_upper']),1)
        result=certify.verify(self.model,self.data['readings'],self.proposal,ETA,NU,True)
        self.assertEqual(result['status'],'certified_under_declared_model')
        self.assertEqual(result['answer_a1_through_a50'],self.data['truth_a1_through_a50'])

    def test_changed_arithmetic_proposal_is_rejected(self):
        proposal=deepcopy(self.proposal)
        proposal[49][0]=str(Q(proposal[49][0])+Q(1,1000))
        result=certify.verify(self.model,self.data['readings'],proposal,ETA,NU)
        self.assertEqual(result['status'],'not_certified')
        self.assertIsNone(result['answer_a1_through_a50'])

    def test_changed_readings_require_a_new_residual(self):
        data=deepcopy(self.data['readings'])
        data[4450][0]=str(Q(data[4450][0])+1000)
        result=certify.verify(self.model,data,self.proposal,ETA,NU)
        self.assertEqual(result['status'],'not_certified')
        self.assertNotEqual(result['data_sha256'],self.saved['certificate']['data_sha256'])

    def test_sensor_and_drift_cannot_each_spend_full_noise_budget(self):
        result=certify.verify(self.model,self.data['readings'],self.proposal,'1/10000','1/10000')
        self.assertEqual(result['status'],'not_certified')
        self.assertFalse(all(c['strict_uniform_rounding_gate'] for c in result['coordinates']))

    def test_sufficient_remainder_limit_is_data_dependent_and_strict(self):
        c=self.saved['certificate'];rho=Q(c['normal_residual_upper'])
        cap=Q(c['strict_sufficient_nonpolynomial_budget_limit'])
        self.assertGreater(cap,NU)
        ok=certify.consequences(self.model.record,self.proposal,rho,ETA,cap-Q(1,10**12))
        bad=certify.consequences(self.model.record,self.proposal,rho,ETA,cap+Q(1,10**12))
        self.assertTrue(all(x['strict_uniform_rounding_gate'] for x in ok['coordinates']))
        self.assertFalse(all(x['strict_uniform_rounding_gate'] for x in bad['coordinates']))
        worse=certify.consequences(self.model.record,self.proposal,rho+Q(1,10**6),ETA,NU)
        self.assertLess(Q(worse['strict_sufficient_nonpolynomial_budget_limit']),cap)

    def test_large_slow_sine_has_small_remainder_after_polynomial_removal(self):
        self.assertLess(Q(10,factorial(9)),NU)
        self.assertGreater(Q(10),ETA+NU)
        self.assertEqual(self.data['nonpolynomial_formula'],'10*sin(t/890)')
        self.assertEqual(Q(self.data['nonpolynomial_remainder_pointwise_upper']),Q(10,factorial(9)))

    def test_normal_residual_does_not_validate_physical_drift(self):
        # Exact alias: increase a(50) by 1, or instead add h=Phi_50/2500.
        # ||Phi_50||_W=1, so the latter drift norm is 1/2500. Both source
        # coefficients 1 and 2 are allowed. No data statistic separates them
        # without an external drift bound excluding this h.
        self.assertLessEqual(2,certify.divisor14(50))
        self.assertGreater(Q(1,2500),ETA+NU)
        with ctx.workprec(128):
            for t in (Q(-8899,10),Q(1,10),Q(8899,10)):
                phi=acb(0,-physical.ball(t)*arb(50).log()).exp()
                self.assertTrue((phi/2500+phi/2500).overlaps(2*phi/2500))
                self.assertTrue(abs(phi).contains(1))

    def test_exact_input_shapes_and_sign_contracts(self):
        for bad in (True,1.0,1e-30):
            with self.assertRaises(ValueError):physical.exact(bad)
        with self.assertRaises(ValueError):physical.parse_pairs([[0,0]],8900)
        for eta,nu,rho in [('-1',NU,'0'),(ETA,'-1','0'),(ETA,NU,'-1')]:
            with self.assertRaises(ValueError):certify.consequences(self.model.record,self.proposal,rho,eta,nu)
        with self.assertRaises(ValueError):physical.PhysicalModel('multi',8,53)
        with self.assertRaises(ValueError):physical.PhysicalModel('unknown',8,256)

    def test_zero_centered_residual_has_a_finite_outward_bound(self):
        rho,_=self.model.residual(physical.correction(),[(0,0)]*58)
        self.assertGreaterEqual(rho,0)
        self.assertLess(rho,Q(1,10**40))


if __name__=='__main__':unittest.main()
