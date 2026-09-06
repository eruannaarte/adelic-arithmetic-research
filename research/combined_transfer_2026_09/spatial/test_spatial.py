"""Adverse tests for the fixed combined six-row contract."""
from fractions import Fraction as Q
from pathlib import Path
import copy,json,unittest
import check,certify,decoder,fixtures
HERE=Path(__file__).resolve().parent

class CombinedSpatialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank=decoder.StructuredBank()
        cls.document=json.loads((HERE/'directions.json').read_text())
        cls.pairs=json.loads((HERE/'certificate_6.json').read_text())
        cls.fixture=json.loads((HERE/'fixtures.json').read_text())['cases'][0]
    def test_joint_contract_and_honest_comparison(self):
        result=check.consequence()
        self.assertLess(Q(result['label_total_relative_radius']),Q(result['certified_label_tube_radius']))
        self.assertLess(Q(result['source_relative_error_upper']),Q(852832,10**9))
        self.assertTrue(result['global_inverse_gate_also_passes'])
        self.assertGreater(Q(result['global_inverse_source_error_upper']),Q(result['source_relative_error_upper']))
        self.assertGreater(Q(result['remainders']['clock_potential_cross_radius']),0)
    def test_must_not_substitute_unproved_smaller_bounds(self):
        bad=dict(check.LIMITS);bad['joint_inverse']/=2
        with self.assertRaises(ValueError):check.consequence(bad)
        with self.assertRaises(ValueError):check.consequence(h=1e-8)
        with self.assertRaises(ValueError):check.consequence(dg=check.DG*2)
    def test_changed_rows_rejected(self):
        bad=copy.deepcopy(self.document);bad['bank_rows'][0]-=1
        with self.assertRaises(ValueError):check.verify(bad)
    def test_missing_direction_coverage_rejected(self):
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
    def test_old_pair_budget_cannot_replace_new_budget(self):
        bad=copy.deepcopy(self.pairs);bad['label_tube_radius']='1/31250000'
        with self.assertRaises(ValueError):certify.check(bad)
    def test_false_principal_minor_rejected(self):
        bad=copy.deepcopy(self.pairs);bad['records'][0]['principal_minor_lower_bounds'][0]='1'
        with self.assertRaises(ValueError):certify.check(bad)
    def test_nonpositive_split_rejected(self):
        bad=copy.deepcopy(self.pairs)
        record=next(r for r in bad['records'] if len(r['case'])==2)
        record['source_split_weight']='0'
        with self.assertRaises(ValueError):certify.check(bad)
    def test_actual_parameter_fixture_and_raw_wrapper(self):
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
        with self.assertRaises(ValueError):self.bank.decode([Q(0)]*6,1,[1,1+check.H],[Q(4,5)-check.DG,Q(4,5)+check.DG])

if __name__=='__main__':unittest.main()
