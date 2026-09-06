"""Adverse contract, coverage and exact unknown-label decoding tests."""
from fractions import Fraction as Q
from copy import deepcopy
import json,unittest
import check,decoder,exact


class SpatialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank=decoder.CertifiedBank()
        cls.certificate=json.loads((check.HERE/'certificate.json').read_text())
        cls.kernel=json.loads((check.HERE/'kernel.json').read_text())

    def test_complete_case_cover_and_three_calibrations(self):
        s=self.bank.summary
        self.assertEqual((s['individual_cases'],s['pair_cases'],s['whole_cell_records']),(21,210,895))
        self.assertTrue(s['all_case_covers_verified'])
        for m in s['metrics'].values():
            self.assertLess(Q(m['source_relative_error_squared_upper']),Q(1,10**6))
            self.assertGreater(Q(m['pair_approximate_map_floor']),2*Q(m['total_relative_radius'])**2)

    def test_individual_pair_case_gap_not_hidden_by_union(self):
        c=deepcopy(self.certificate)
        # Delete one valid pair record but leave the entire collection of cells.
        cell=next(v for v in c['cells'] if len(v['records'])>1)
        index=next(i for i,r in enumerate(cell['records']) if len(r['case'])==2)
        cell['records'].pop(index)
        with self.assertRaisesRegex(ValueError,'case (does not cover endpoints|cover gap or overlap)'):
            check.check(certificate=c)

    def test_changed_rows_noise_premise_or_kernel_rejected(self):
        for field,new in [('bank_offsets',list(range(11))),('operator_model_error_upper','0'),
                          ('kernel_sha256','0'*64),('case_count',True)]:
            c=deepcopy(self.certificate);c[field]=new
            with self.assertRaises(ValueError):check.check(certificate=c)
        k=deepcopy(self.kernel);k['model']['source_modes'][0]=True
        with self.assertRaisesRegex(ValueError,'unbound kernel'):check.check(kernel=k)

    def test_rational_polynomial_translation_independent_identity(self):
        coeff=check.interval_coefficients(self.kernel)
        for center in (Q(9,8),Q(3,2),Q(31,16)):
            producer=exact.shift_kernel(coeff,center)
            for d in (0,7,26):
                for port in (0,1):
                    independent=check.translated(coeff[d][port],center-Q(3,2))
                    self.assertEqual(independent,producer[d][port])
                    h=Q(1,100)
                    self.assertEqual(decoder.value(coeff[d][port],center+h),
                                     sum((c*h**k for k,c in enumerate(independent)),Q()))

    def test_unknown_label_every_target_and_time_endpoints(self):
        sources=((Q(1),Q(0)),(Q(0),Q(1)),(Q(3,5),Q(4,5)),(Q(-4,5),Q(3,5)))
        for t in (Q(1),Q(3,2),Q(2)):
            matrices=self.bank.matrices(t)
            for label,P in matrices.items():
                u=sources[(label-490)%4]
                z=tuple(sum((a*b for a,b in zip(row,u)),Q()) for row in P)
                r=self.bank.decode(z,t)
                self.assertEqual((r.status,r.feasible_targets),('unique',(label,)))
                self.assertEqual(r.estimate,u)

    def test_same_observation_sensor_noise_and_H1_envelopes(self):
        u=(Q(3,5),Q(4,5))
        for t,label in ((Q(1),490),(Q(5,4),501),(Q(2),510)):
            P=self.bank.matrices(t)[label]
            pure=[sum((a*b for a,b in zip(row,u)),Q()) for row in P]
            for metric in ('L2','declared_H1','natural_discrete_H1'):
                eta=Q(3,10**7 if metric=='L2' else 10**8)
                data=pure[:];data[4]+=eta/check.A1
                r=self.bank.decode(data,t,metric,numerical_relative_radius='1/1000000000')
                self.assertEqual((r.status,r.feasible_targets),('unique',(label,)))
                factor=1 if metric=='L2' else 41
                self.assertLess(factor*sum(((a-b)**2 for a,b in zip(r.estimate,u)),Q()),Q(1,10**6))

    def test_incompatible_data_returns_empty_answer_set(self):
        r=self.bank.decode([1]+[0]*10,'3/2')
        self.assertEqual((r.status,r.feasible_targets,r.estimate),('incompatible',(),None))

    def test_zero_time_and_numerical_contract_rejections(self):
        with self.assertRaisesRegex(ValueError,'zero data'):self.bank.decode([0]*11,1)
        for t in ('99/100','201/100',1.5,True):
            with self.assertRaises(ValueError):self.bank.decode([1]*11,t)
        for xi in ('-1/1000000000','2/1000000000',1e-9):
            with self.assertRaises(ValueError):self.bank.decode([1]*11,1,numerical_relative_radius=xi)
        for data in ([1]*10,[True]+[0]*10,[1.0]+[0]*10):
            with self.assertRaises(ValueError):self.bank.decode(data,1)
        with self.assertRaises(ValueError):self.bank.decode([1]*11,1,'unclaimed_norm')

    def test_model_tail_and_normalization_strict(self):
        self.assertEqual(check.model_error_check(),Q(1,10**9))
        self.assertTrue(check.A0**4<2 and check.A1**4>3)
        self.assertFalse(check.same_json({'integer':True},{'integer':1}))


if __name__=='__main__':unittest.main()
