"""Coverage corruption, calibrated decoding, and the specific seven-row alias."""
from fractions import Fraction as Q
from copy import deepcopy
import json, unittest
import check, decoder, obstruction


class SpatialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.banks={b:decoder.CertifiedBank(b) for b in ('8','9')}
        cls.certs={b:json.loads((check.HERE/('certificate_'+b+'.json')).read_text()) for b in cls.banks}

    def test_complete_time_covers_and_calibrations(self):
        for size,bank in self.banks.items():
            s=bank.summary
            self.assertEqual((s['individual_cases'],s['pair_cases'],s['channel_count']),(21,210,int(size)))
            self.assertTrue(s['all_case_covers_verified'])
            for profile in s['metrics'].values():
                self.assertLess(Q(profile['source_relative_error_squared_upper']),Q(profile['source_relative_accuracy_target'])**2)
                self.assertGreater(Q(profile['pair_approximate_map_floor']),2*Q(profile['total_relative_radius'])**2)

    def test_deleting_one_pair_cell_invalidates_cover(self):
        c=deepcopy(self.certs['8'])
        cell=next(v for v in c['cells'] if any(len(r['case'])==2 for r in v['records']))
        cell['records'].pop(next(i for i,r in enumerate(cell['records']) if len(r['case'])==2))
        with self.assertRaisesRegex(ValueError,'case (does not cover endpoints|cover gap or overlap)'):
            check.check(certificate=c,bank='8')

    def test_wrong_rows_floors_and_kernel_rejected(self):
        for key,value in [('bank_offsets',list(range(8))),('operator_model_error_upper','0'),
                          ('unnormalized_source_floor','1/1000000'),('kernel_sha256','0'*64),('case_count',True)]:
            c=deepcopy(self.certs['8']);c[key]=value
            with self.assertRaises(ValueError):check.check(certificate=c,bank='8')
        with self.assertRaises(ValueError):check.check(certificate=self.certs['8'],bank='9')

    def test_wrong_preconditioner_and_omitted_variation_rejected(self):
        for kind in ('preconditioner','variation'):
            c=deepcopy(self.certs['9']);r=c['cells'][0]['records'][0]
            if kind=='preconditioner':r['preconditioner'][0][0]='0'
            else:r['variation_frobenius_upper']='0'
            with self.assertRaises(ValueError):check.check(certificate=c,bank='9')

    def test_unknown_label_all_targets_and_time_endpoints(self):
        sources=((Q(1),Q(0)),(Q(0),Q(1)),(Q(3,5),Q(4,5)),(Q(-4,5),Q(3,5)))
        for bank in self.banks.values():
            for t in (Q(1),Q(3,2),Q(2)):
                for label,P in bank.matrices(t).items():
                    u=sources[(label-490)%4]
                    data=[sum((a*b for a,b in zip(row,u)),Q()) for row in P]
                    got=bank.decode(data,t)
                    self.assertEqual((got.status,got.feasible_targets,got.estimate),('unique',(label,),u))

    def test_noise_and_both_H1_norms_and_original_noise_profile(self):
        u=(Q(3,5),Q(4,5))
        for bank in self.banks.values():
            for t,label in ((Q(1),490),(Q(285,256),507),(Q(2),510)):
                P=bank.matrices(t)[label]
                pure=[sum((a*b for a,b in zip(row,u)),Q()) for row in P]
                for metric,profile in bank.profiles.items():
                    z=pure[:];z[3]+=Q(profile['sensor_relative_radius'])/check.A1
                    got=bank.decode(z,t,metric,'1/1000000000')
                    self.assertEqual((got.status,got.feasible_targets),('unique',(label,)))
                    factor=1 if metric.startswith('L2') else 41
                    self.assertLess(factor*sum(((a-b)**2 for a,b in zip(got.estimate,u)),Q()),Q(profile['source_relative_accuracy_target'])**2)

    def test_invalid_time_data_normalization_budget_and_incompatibility(self):
        bank=self.banks['8']
        for time in (True,1.5,'99/100','201/100'):
            with self.assertRaises(ValueError):bank.decode([1]*8,time)
        for data in ([1]*7,[1.0]+[0]*7,[True]+[0]*7,[0]*8):
            with self.assertRaises(ValueError):bank.decode(data,1)
        for xi in ('-1/1000000000','2/1000000000',1e-9):
            with self.assertRaises(ValueError):bank.decode([1]*8,1,numerical_relative_radius=xi)
        self.assertEqual(bank.decode([1]+[0]*7,1).status,'incompatible')
        with self.assertRaises(ValueError):self.banks['9'].decode([1]*9,1,'L2_original_noise')

    def test_seven_row_physical_alias_is_specific_and_strict(self):
        doc=json.loads((check.HERE/'obstruction_7.json').read_text())
        out=obstruction.verify(doc)
        self.assertLess(Q(out['sufficient_collision_radius_upper']),Q(out['sensor_relative_radius']))
        for key,new in [('source_pair',['1','0','1','0']),('sensor_relative_radius','1/1000000000'),('target_offsets',[6,8])]:
            bad=deepcopy(doc);bad[key]=new
            with self.assertRaises(ValueError):obstruction.verify(bad)


if __name__=='__main__':unittest.main()
