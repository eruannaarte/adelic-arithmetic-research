import copy,json,unittest
from fractions import Fraction as Q
from pathlib import Path
import checker as ch
import anisotropic as a
HERE=Path(__file__).resolve().parent
load=lambda f:json.loads((HERE/f).read_text())

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=load('cycle2_region.json');cls.n=load('nominal.json');cls.d=load('cycle2_certificate.json');cls.c=load('cycle3_certificate.json')
    def test_exact_primal_dual_and_targets(self):
        self.assertTrue(a.verify(self.r,self.n,self.d,self.c))
        for v in self.c['designs'].values():
            c=v['certificate'];self.assertTrue(c['geometric_mean_at_least_8e6']);self.assertTrue(c['volume_within_one_per_mille_of_optimal'])
            self.assertGreater(Q(c['volume_gain_over_isotropic']),5)
            self.assertGreater(Q(c['volume_ratio_lower_bound']),Q(9999999994,10**10))
    def test_isotropic_boundary_matches_previous_cycle(self):
        prev=load('cycle2_calibration.json')
        for name,v in self.c['designs'].items():
            c=v['certificate'];self.assertEqual(Q(v['outer_preparation_radius'])*Q(c['isotropic_normalized_radius']),Q(prev['designs'][name]['synthesized']['maximum_preparation_radius']))
    def test_face_and_cap_violations(self):
        for v in self.c['designs'].values():
            G=[[Q(x) for x in r] for r in v['constraints_G']];cap=Q(v['outer_preparation_radius']);c=v['certificate'];x=list(map(Q,c['normalized_radii']))
            x[4]+=Q(1,10**7)
            with self.assertRaisesRegex(ValueError,'half-plane'):a.exact_certificate(G,cap,x,c['dual_lambda'],c['dual_mu'])
            x=list(map(Q,c['normalized_radii']));x[0]=Q(10000001,10000000)
            with self.assertRaisesRegex(ValueError,'cap'):a.exact_certificate(G,cap,x,c['dual_lambda'],c['dual_mu'])
    def test_dual_and_binding_tamper(self):
        bad=copy.deepcopy(self.c);bad['designs']['selected_AB']['certificate']['dual_lambda'][0]='-1'
        with self.assertRaises(ValueError):a.verify(self.r,self.n,self.d,bad)
        bad=copy.deepcopy(self.c);bad['coordinates'][4]='B.omega1'
        with self.assertRaises(ValueError):a.verify(self.r,self.n,self.d,bad)
        bad=copy.deepcopy(self.c);bad['designs']['selected_AB']['certificate']['normalized_volume_upper_bound']='1/100'
        with self.assertRaises(ValueError):a.verify(self.r,self.n,self.d,bad)
    def test_amgm_sharp_unit_cube(self):
        c=a.exact_certificate([[Q(0)]*8]*3,Q(1),[Q(1)]*8,[Q(0)]*3,[Q(1)]*8)
        self.assertEqual(c['normalized_volume'],1);self.assertEqual(c['normalized_volume_upper_bound'],1)
        with self.assertRaisesRegex(ValueError,'positive'):a.exact_certificate([[Q(0)]*8]*3,Q(1),[Q(1)]*8,[Q(0)]*3,[Q(0)]*8)

if __name__=='__main__':unittest.main(verbosity=2)
