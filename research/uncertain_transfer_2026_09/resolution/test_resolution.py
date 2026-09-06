"""Focused adverse checks for the new spatial proof and uncertainty contract."""
from fractions import Fraction as Q
from pathlib import Path
import copy,json,unittest
import check,timing,fixtures

HERE=Path(__file__).resolve().parent


class SpatialUncertaintyTests(unittest.TestCase):
    def test_derivative_bounds_cover_targets(self):
        receipt=timing.derivative_bound()
        self.assertEqual(receipt['all_targets'],list(range(-10,11)))
        self.assertEqual(len(receipt['per_target_squared_bounds']),21)
        for z in receipt['per_target_squared_bounds']:
            self.assertLess(Q(z),Q('0.037')**2)

    def test_both_noise_profiles_pass(self):
        profiles=timing.build()['profiles']
        self.assertEqual(Q(profiles['known_clock']['sensor_relative_radius']),Q('1.4e-7'))
        self.assertEqual(Q(profiles['uncertain_clock']['total_relative_radius']),Q(799,6_000_000_000))
        for p in profiles.values():self.assertLess(Q(p['source_relative_error_squared_upper']),Q(1,10**6))

    def test_clock_consumes_budget(self):
        with self.assertRaisesRegex(ValueError,'source accuracy'):
            timing.profile(timing.ETA,Q(1,1_000_000),timing.EPSILON_H,timing.XI)
        with self.assertRaisesRegex(ValueError,'source accuracy'):
            timing.profile(Q('1.5e-7'),0,0,timing.XI)

    def test_negative_or_inexact_budgets_rejected(self):
        for v in (-1,1e-7,True):
            with self.assertRaises(ValueError):timing.profile(v,0,0,0)

    def test_bank_metadata_tamper_rejected(self):
        d=json.loads((HERE/'certificate_7.json').read_text())
        d['bank_offsets'][0]=-11
        with self.assertRaisesRegex(ValueError,'bank rows'):check.check(certificate=d)

    def test_preconditioner_tamper_rejected(self):
        d=json.loads((HERE/'certificate_7.json').read_text())
        r=d['cells'][0]['records'][0]
        r['preconditioner']=[['0' for x in row] for row in r['preconditioner']]
        with self.assertRaisesRegex(ValueError,'point Gram defect'):check.check(certificate=d)

    def test_true_time_fixture_replay(self):
        d=json.loads((HERE/'fixtures.json').read_text())
        self.assertTrue(fixtures.verify(d)['verified'])
        for r in d['cases']:
            self.assertLessEqual(abs(Q(r['true_time'])-Q(r['nominal_time'])),timing.H)
            self.assertNotEqual(Q(r['true_time']),Q(r['nominal_time']))
            self.assertGreater(Q(r['generator_decay_lambda']),0)

    def test_fixture_contract_tamper_rejected(self):
        d=json.loads((HERE/'fixtures.json').read_text())
        d['cases'][0]['generator_perturbation_bound']='0'
        with self.assertRaisesRegex(ValueError,'reconstruction disagrees'):fixtures.verify(d)


if __name__=='__main__':unittest.main(verbosity=2)
