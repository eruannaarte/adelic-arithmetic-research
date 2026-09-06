"""Adverse contract and consequence tests; physical reconstruction has its own replay."""
from fractions import Fraction as Q
from pathlib import Path
import copy,json,unittest
import check,decoder,fixtures
HERE=Path(__file__).resolve().parent

class StructuredTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank=decoder.StructuredBank()
        cls.document=json.loads((HERE/'directions.json').read_text())
        cls.fixture=json.loads((HERE/'fixtures.json').read_text())['cases'][0]
    def test_complete_remainders_and_material_inverse_improvement(self):
        result=check.consequence();r=result['remainders']
        self.assertLess(Q(r['total_nonlinear_radius']),Q(4268,10**13))
        self.assertGreater(Q(r['clock_potential_cross_radius']),0)
        self.assertTrue(result['old_global_inverse_gate_fails_at_same_rectangle'])
        self.assertLess(Q(result['source_relative_error_upper']),Q(802,10**6))
    def test_must_not_substitute_unproved_smaller_bounds(self):
        bad=dict(check.LIMITS);bad['joint_inverse']/=2
        with self.assertRaises(ValueError):check.consequence(bad)
        with self.assertRaises(ValueError):check.consequence(h=5e-7)
        with self.assertRaises(ValueError):check.consequence(dg=check.DG*2)
    def test_changed_rows_rejected(self):
        bad=copy.deepcopy(self.document);bad['bank_rows'][0]-=1
        with self.assertRaises(ValueError):check.verify(bad)
    def test_missing_target_time_coverage_rejected(self):
        bad=copy.deepcopy(self.document);bad['records'].pop()
        with self.assertRaises(ValueError):check.verify(bad)
    def test_relabelled_time_cell_rejected(self):
        bad=copy.deepcopy(self.document);bad['records'][0]['time_cell']=['1','3/2']
        with self.assertRaises(ValueError):check.verify(bad)
    def test_falsely_reduced_saved_direction_bound_rejected(self):
        bad=copy.deepcopy(self.document)
        bad['records'][0]['bounds']['joint_inverse']=str(Q(bad['records'][0]['bounds']['joint_inverse'])/2)
        with self.assertRaises(ValueError):check.verify(bad)
    def test_changed_derivative_premise_rejected(self):
        bad=copy.deepcopy(self.document)
        key=next(k for k in bad['premise_sha256'] if 'kernel_derivative' in k)
        bad['premise_sha256'][key]='0'*64
        with self.assertRaises(ValueError):check.verify(bad)
    def test_actual_potential_fixture_and_raw_wrapper(self):
        case=self.fixture;nominal=Q(case['nominal_time'])
        result=self.bank.decode(case['raw_data'],nominal,[nominal,nominal+check.H],[Q(4,5)-check.DG,Q(4,5)+check.DG])
        self.assertEqual(result['feasible_targets'],[case['source_label']])
        error=sum((Q(a)-Q(b))**2 for a,b in zip(result['source_estimate'],case['source']))/Q(case['source_norm'])**2
        self.assertLess(error,Q(1,1000)**2)
        self.assertLess(fixtures.complete_physical_radius(),check.ETA)
    def test_excess_clock_or_potential_rejected(self):
        data=self.fixture['raw_data']
        with self.assertRaises(ValueError):self.bank.decode(data,1,[1,1+2*check.H],[Q(4,5)-check.DG,Q(4,5)+check.DG])
        with self.assertRaises(ValueError):self.bank.decode(data,1,[1,1+check.H],[Q(4,5)-check.DG,Q(4,5)+2*check.DG])
        with self.assertRaises(ValueError):self.bank.decode(data,1.0,[1,1+check.H],[Q(4,5)-check.DG,Q(4,5)+check.DG])
    def test_zero_raw_data_cannot_receive_guarantee(self):
        with self.assertRaises(ValueError):self.bank.decode([Q(0)]*7,1,[1,1+check.H],[Q(4,5)-check.DG,Q(4,5)+check.DG])

if __name__=='__main__':unittest.main()
