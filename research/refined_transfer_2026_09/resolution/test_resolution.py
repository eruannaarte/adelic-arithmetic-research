"""Exact cover corruption, calibrated seven-row decoding, and time alias."""
from fractions import Fraction as Q
from copy import deepcopy
import json, unittest
import check, decoder, obstruction


class SpatialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank=decoder.CertifiedBank('7')
        cls.cert=json.loads((check.HERE/'certificate_7.json').read_text())

    def test_fixed_contract_and_full_case_covers(self):
        s=self.bank.summary;p=s['metrics']['L2']
        self.assertEqual((s['individual_cases'],s['pair_cases'],s['channel_count']),(21,210,7))
        self.assertTrue(s['all_case_covers_verified'])
        self.assertEqual(self.bank.bank,(-12,-10,-3,0,4,8,10))
        self.assertGreaterEqual(min(b-a for a,b in zip(self.bank.bank,self.bank.bank[1:])),2)
        self.assertEqual(Q(p['sensor_relative_radius']),Q(1,10**7))
        self.assertLess(Q(p['source_relative_error_squared_upper']),Q(998507,10**9)**2)
        self.assertGreater(Q(p['pair_approximate_map_floor']),2*Q(p['total_relative_radius'])**2)

    def test_missing_pair_cell_is_not_full_time(self):
        c=deepcopy(self.cert)
        cell=next(v for v in c['cells'] if any(len(r['case'])==2 for r in v['records']))
        cell['records'].pop(next(i for i,r in enumerate(cell['records']) if len(r['case'])==2))
        with self.assertRaisesRegex(ValueError,'case (does not cover endpoints|cover gap or overlap)'):
            check.check(certificate=c)

    def test_changed_contract_or_model_premise_rejected(self):
        for key,val in [('bank_offsets',[-11,-8,-4,0,4,8,11]),('operator_model_error_upper','0'),
                        ('unnormalized_source_floor','1/1000000'),('kernel_sha256','0'*64),('case_count',True),
                        ('source_metrics',['L2','declared_H1'])]:
            c=deepcopy(self.cert);c[key]=val
            with self.assertRaises(ValueError):check.check(certificate=c)

    def test_proposal_and_whole_cell_error_are_not_trusted(self):
        for kind in ('preconditioner','variation'):
            c=deepcopy(self.cert);r=c['cells'][0]['records'][0]
            if kind=='preconditioner':r['preconditioner'][0][0]='0'
            else:r['variation_frobenius_upper']='0'
            with self.assertRaises(ValueError):check.check(certificate=c)

    def test_all_unknown_targets_at_endpoints_and_interior(self):
        directions=((Q(1),Q(0)),(Q(0),Q(1)),(Q(3,5),Q(4,5)),(Q(-4,5),Q(3,5)))
        for t in (Q(1),Q(3,2),Q(2)):
            for label,P in self.bank.matrices(t).items():
                u=directions[(label-490)%4]
                z=[sum((a*b for a,b in zip(row,u)),Q()) for row in P]
                r=self.bank.decode(z,t)
                self.assertEqual((r.status,r.feasible_targets,r.estimate),('unique',(label,),u))

    def test_sensor_noise_full_numerical_budget_and_source_amplitude(self):
        for amplitude in (Q(1,10**20),Q(1),Q(10**20)):
            u=(amplitude*Q(3,5),amplitude*Q(4,5))
            for t,label in ((Q(1),496),(Q(1221707459,10**9),493),(Q(2),510)):
                P=self.bank.matrices(t)[label]
                z=[sum((a*b for a,b in zip(row,u)),Q()) for row in P]
                z[3]+=amplitude*Q(1,10**7)/check.A1
                got=self.bank.decode(z,t,numerical_relative_radius='1/1000000000')
                self.assertEqual((got.status,got.feasible_targets),('unique',(label,)))
                self.assertLess(sum(((a-b)**2 for a,b in zip(got.estimate,u)),Q()),amplitude**2/10**6)

    def test_invalid_time_data_and_uncharged_error_are_rejected(self):
        for t in (True,1.5,'99/100','201/100'):
            with self.assertRaises(ValueError):self.bank.decode([1]*7,t)
        for z in ([1]*6,[1.0]+[0]*6,[True]+[0]*6,[0]*7):
            with self.assertRaises(ValueError):self.bank.decode(z,1)
        for xi in ('-1/1000000000','2/1000000000',1e-9):
            with self.assertRaises(ValueError):self.bank.decode([1]*7,1,numerical_relative_radius=xi)
        self.assertEqual(self.bank.decode([1]+[0]*6,1).status,'incompatible')

    def test_coarse_grid_winner_has_a_real_interior_alias(self):
        doc=json.loads((check.HERE/'coarse_grid_obstruction.json').read_text())
        out=obstruction.verify(doc)
        self.assertLess(Q(out['sufficient_collision_radius_upper']),Q(1463,10**12))
        self.assertEqual(Q(out['sensor_relative_radius']),Q(1,10**7))
        for key,val in [('source_pair',['1','0','1','0']),('time','1'),('sensor_relative_radius','1/1000000000')]:
            bad=deepcopy(doc);bad[key]=val
            with self.assertRaises(ValueError):obstruction.verify(bad)

if __name__=='__main__':unittest.main()
