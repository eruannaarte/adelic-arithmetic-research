"""Adverse contract checks and raw decoder verification for the six-row result."""
from fractions import Fraction as Q
from pathlib import Path
import copy,json,unittest
import certify,comparison,obstruction_check,fixtures
from raw import PhysicalBank
HERE=Path(__file__).resolve().parent

class SixRowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank=PhysicalBank();cls.certificate=json.loads((HERE/'certificate_6.json').read_text())
        cls.fixtures=json.loads((HERE/'fixtures.json').read_text())

    def test_full_time_and_fixed_budget(self):
        s=self.bank.summary;p=s['metrics']['L2']
        self.assertTrue(s['all_case_covers_verified']);self.assertEqual(s['whole_cell_records'],1278)
        self.assertEqual(p['sensor_relative_radius'],'3/100000000')
        self.assertLess(Q(p['source_relative_error_squared_upper']),Q(1,10**6))

    def test_changed_contract_rejected(self):
        d=copy.deepcopy(self.certificate);d['sensor_relative_radius']='29/1000000000'
        with self.assertRaises(ValueError):certify.check(d)
        d=copy.deepcopy(self.certificate);d['bank_offsets'][0]=-14
        with self.assertRaises(ValueError):certify.check(d)

    def test_invalid_minor_or_split_rejected(self):
        d=copy.deepcopy(self.certificate);d['records'][0]['principal_minor_lower_bounds'][0]='1000000000'
        with self.assertRaises(ValueError):certify.check(d)
        d=copy.deepcopy(self.certificate)
        first=next(r for r in d['records'] if len(r['case'])==2);first['source_split_weight']='0'
        with self.assertRaises(ValueError):certify.check(d)

    def test_missing_coverage_rejected(self):
        d=copy.deepcopy(self.certificate);d['records']=d['records'][1:]
        with self.assertRaises(ValueError):certify.check(d)

    def test_raw_contract_and_exact_time(self):
        c=self.fixtures['cases'][0]
        for data,time,xi in ((c['raw_data'],1.0,'1/1000000000'),(c['raw_data'][:-1],'1','1/1000000000'),(c['raw_data'],'1','2/1000000000')):
            with self.assertRaises(ValueError):self.bank.decode(data,time,xi_budget=xi)
        t=Q(36975,28561);P=self.bank.decoder.matrices(t)[500]
        raw=[str(row[0]*Q(16,13)) for row in P]
        answer=self.bank.decode(raw,t,xi_budget='0')
        self.assertEqual(answer['status'],'unique');self.assertEqual(answer['feasible_targets'],[500])

    def test_unknown_amplitude_and_no_false_accuracy(self):
        c=self.fixtures['cases'][7]
        for scale in (Q(1,10**30),Q(10**30)):
            answer=self.bank.decode([str(Q(y)*scale) for y in c['raw_data']],c['time'])
            self.assertEqual(answer['feasible_targets'],[c['source_label']])
        answer=self.bank.decode(['1','0','0','0','0','0'],'1')
        self.assertEqual(answer['status'],'incompatible');self.assertIsNone(answer['guaranteed_relative_source_accuracy'])

    def test_finite_model_fixture_replay_and_tamper(self):
        self.assertTrue(fixtures.replay(self.fixtures)['all_raw_digits_reproduced'])
        d=copy.deepcopy(self.fixtures);d['cases'][0]['raw_data'][0]='0'
        with self.assertRaises(ValueError):fixtures.replay(d)

    def test_gate_obstruction_is_not_recovery_obstruction(self):
        result=comparison.verify(json.loads((HERE/'uniform_comparison.json').read_text()))
        self.assertLess(Q(result['ratio_upper']),1)
        self.assertEqual(obstruction_check.verify()['deletion_layouts'],7)
        self.assertTrue(self.bank.summary['verified'])

if __name__=='__main__':unittest.main(verbosity=2)
