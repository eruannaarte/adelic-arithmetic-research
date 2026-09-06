"""Exact scaling, physical error budgets, interfaces and refusal controls."""
from fractions import Fraction as Q
from copy import deepcopy
import json,unittest
import normalize as n


class NormalizationTests(unittest.TestCase):
    def test_every_dyadic_time_and_three_sensor_profiles(self):
        for k in range(65):
            t=Q(64+k,64)
            for eta in (Q(3,10**7),Q(1,10**7),Q(3,10**8)):
                r=n.make_scale(t,eta)
                self.assertLessEqual(n.verify_scale(r),Q(1,10**9))
                self.assertLess(r['rational_bisection_steps'],40)

    def test_exact_rational_root_and_zero_budget(self):
        t=Q(36975,28561)
        receipt=n.make_scale(t,0,0)
        self.assertEqual((receipt['inverse_normalization'],n.verify_scale(receipt)),('13/16',0))
        for t in (1,Q(3,2),2):
            with self.assertRaisesRegex(ValueError,'zero budget'):n.make_scale(t,0,0)

    def test_scale_equivariance_extreme_and_negative_data(self):
        original=[Q(3),Q(-5),Q(1,100)]
        reference=n.normalize(original,'3/2','1/10000000')
        for c in (Q(1,10**100),Q(-1),Q(10**100)):
            raw=[c*x for x in original];packet=n.normalize(raw,'3/2','1/10000000')
            self.assertEqual(packet['scale'],reference['scale'])
            self.assertEqual(tuple(map(Q,packet['normalized_data'])),tuple(c*Q(x) for x in reference['normalized_data']))
            self.assertEqual(n.verify_packet(raw,packet),n.verify_packet(original,reference))

    def test_omitted_sensor_gain_false_scale_and_false_charge_rejected(self):
        receipt=n.make_scale('3/2','1/10000000')
        for key,value in [('measured_output_gain_upper','4/3'),('inverse_normalization','1'),
                          ('relative_multiplier_error_upper','0'),('charged_physical_relative_radius','0'),
                          ('numerical_relative_budget','0'),('sensor_relative_radius','-1')]:
            bad=deepcopy(receipt);bad[key]=value
            with self.assertRaises(ValueError):n.verify_scale(bad)

    def test_data_binding_and_exact_multiplication_are_checked(self):
        raw=['3','-7','2/5'];packet=n.normalize(raw,'1','1/10000000')
        for change in ('normalized','rawhash','normalizedhash'):
            bad=deepcopy(packet)
            if change=='normalized':bad['normalized_data'][0]='0'
            elif change=='rawhash':bad['raw_data_sha256']='0'*64
            else:bad['normalized_data_sha256']='0'*64
            with self.assertRaises(ValueError):n.verify_packet(raw,bad)
        with self.assertRaises(ValueError):n.verify_packet(['3','-8','2/5'],packet)

    def test_invalid_domains_unresolved_refinement_and_zero_data(self):
        for x in (True,1.0):
            with self.assertRaises(ValueError):n.exact(x)
        for t in ('99/100','201/100'):
            with self.assertRaises(ValueError):n.make_scale(t,0)
        with self.assertRaises(ValueError):n.make_scale(1,0,'-1')
        with self.assertRaisesRegex(ValueError,'refinement'):n.make_scale(1,0,max_refinements=0)
        with self.assertRaises(ValueError):n.normalize([0]*7,1,'1/10000000')
        with self.assertRaises(ValueError):n.normalize([],1,'1/10000000')

    def test_saved_raw_cases_cover_all_banks_profiles_and_scales(self):
        evidence=json.loads((n.HERE/'evidence.json').read_text())
        self.assertEqual(evidence['case_count'],72)
        self.assertEqual({c['bank'] for c in evidence['cases']},{'7','8','9'})
        self.assertEqual(len({(c['bank'],c['profile']) for c in evidence['cases']}),8)
        for c in evidence['cases']:
            charge=n.verify_packet(c['raw_readings'],c['normalization'])
            self.assertLessEqual(charge,Q(1,10**9))
            self.assertEqual(c['unique_recovered_label'],c['source_label'])
            self.assertLess(Q(c['source_relative_error_squared_upper']),Q(c['source_relative_accuracy'])**2)

    def test_physical_wrapper_preserves_profile_and_refuses_excess_budget(self):
        bank=n.PhysicalBank('8')
        for data,t,metric,xi in [([1]*7,1,'L2','1/1000000000'),
                                ([1.0]+[0]*7,1,'L2','1/1000000000'),
                                ([1]*8,1,'unclaimed','1/1000000000'),
                                ([1]*8,1,'L2','2/1000000000'),
                                ([0]*8,1,'L2','1/1000000000')]:
            with self.assertRaises(ValueError):bank.decode(data,t,metric,xi)
        result=bank.decode([1]+[0]*7,1)
        self.assertEqual(result['status'],'incompatible')
        self.assertIsNone(result['source_estimate'])
        self.assertIsNone(result['guaranteed_relative_source_accuracy'])


if __name__=='__main__':unittest.main()
