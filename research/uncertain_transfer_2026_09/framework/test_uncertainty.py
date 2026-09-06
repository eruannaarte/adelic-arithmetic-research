"""Meaningful strict-boundary, malformed-contract and physical fixture checks."""
import json, unittest
from fractions import Fraction as Q
from pathlib import Path
from uncertainty import spatial_gate, arithmetic_gate
from raw_clock import RawClockBank

HERE = Path(__file__).resolve().parent


class TransferTests(unittest.TestCase):
    def test_strict_spatial_boundary(self):
        self.assertFalse(spatial_gate(1, 100, 1, 0, 0, 0, 0, 0, 1)['passed'])
        self.assertFalse(spatial_gate(100, 2, 1, 0, 0, 0, 0, 0, 1)['passed'])
        self.assertTrue(spatial_gate(100, 3, 1, 0, 0, 0, 0, 0, 1)['passed'])

    def test_correlated_errors_are_added(self):
        result = spatial_gate(100, 100, 1, 1, 1, 1, 1, '3/8', 1)
        self.assertEqual(result['total_radius'], '5')
        self.assertFalse(spatial_gate(1, 1, 0, 0, 0, 1, 1, 0, 1)['passed'])

    def test_integer_half_boundary_and_negative_margin(self):
        self.assertFalse(arithmetic_gate(2, 0, 1, 0, '1/8', 0, 0, 0, 0)['passed'])
        self.assertTrue(arithmetic_gate(2, 0, 1, 0, '1/9', 0, 0, 0, 0)['passed'])
        self.assertFalse(arithmetic_gate(2, 1, 1, 0, 0, 0, 0, 0, 0)['passed'])
        with self.assertRaises(ValueError):
            arithmetic_gate(2, 0, 0, 0, 0, 0, 0, 0, 0)


class RawTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = RawClockBank()
        cls.fixtures = json.loads((HERE.parent/'resolution/fixtures.json').read_text())
        cls.results = []

    def decode_case(self, c, **kwargs):
        t, h = Q(c['nominal_time']), Q(c['maximum_absolute_clock_error'])
        interval = [max(Q(1), t-h), min(Q(2), t+h)]
        return self.bank.decode(c['raw_data'], t, interval, **kwargs)

    def test_all_raw_fixtures(self):
        for c in self.fixtures['cases']:
            result = self.decode_case(c)
            self.assertEqual(result['status'], 'unique')
            self.assertEqual(result['feasible_targets'], [c['source_label']])
            truth = list(map(Q, c['source']))
            estimate = list(map(Q, result['source_estimate']))
            relative2 = sum((a-b)**2 for a,b in zip(estimate,truth))/sum(a*a for a in truth)
            self.assertLessEqual(relative2, Q(result['transfer_budget']['source_error_squared_upper']))
            self.assertLess(relative2, Q(1, 10**6))
            self.assertGreater(Q(result['transfer_budget']['timing']), 0)
            self.assertGreater(Q(result['transfer_budget']['model_mismatch']), 0)
            self.results.append({'source_label':c['source_label'], 'source':c['source'],
                'actual_relative_source_error_squared':str(relative2), 'answer':result})

    def test_uncertainty_over_budget_rejected(self):
        c = self.fixtures['cases'][0]
        with self.assertRaises(ValueError):
            self.bank.decode(c['raw_data'], '3/2', ['1','2'])
        with self.assertRaises(ValueError):
            self.decode_case(c, generator_error='1/1000000')
        with self.assertRaises(ValueError):
            self.decode_case(c, sensor_radius='1/1000000')

    def test_invalid_contracts_rejected(self):
        c = self.fixtures['cases'][0]
        for t, interval in [(1.0,['1','2']), ('1',['0','2']), ('1',['2','1']),
                            ('3/2',['1','5/4']), ('1',[True,'2'])]:
            with self.assertRaises(ValueError):
                self.bank.decode(c['raw_data'], t, interval)
        for values in ({'generator_error':'-1'}, {'sensor_radius':'-1'},
                       {'normalization_budget':'1/1000'}):
            with self.assertRaises(ValueError):
                self.decode_case(c, **values)

    def test_incompatible_data_has_no_accuracy_claim(self):
        result = self.bank.decode(['1']*7, '3/2', ['3/2','3/2'])
        self.assertEqual(result['status'], 'incompatible')
        self.assertIsNone(result['source_estimate'])
        self.assertIsNone(result['guaranteed_relative_source_accuracy'])

    def test_source_amplitude_not_required(self):
        c = self.fixtures['cases'][1]
        reference = self.decode_case(c)
        for multiplier in (Q(10)**-100, Q(10)**100):
            scaled = dict(c,raw_data=[str(Q(x)*multiplier) for x in c['raw_data']])
            result = self.decode_case(scaled)
            self.assertEqual(result['feasible_targets'], reference['feasible_targets'])
            self.assertEqual(list(map(Q,result['source_estimate'])),
                [Q(x)*multiplier for x in reference['source_estimate']])

    @classmethod
    def tearDownClass(cls):
        if len(cls.results) == cls.fixtures['case_count']:
            result = {'verified': True, 'cases':cls.results, 'case_count':len(cls.results),
                      'full_time_certificate_checked':True,
                      'physical_fixture_assumptions': 'Reconstructed separately by resolution/fixtures.py'}
            (HERE/'raw_results.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
