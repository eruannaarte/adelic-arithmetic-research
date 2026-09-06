"""Consequences and adverse controls for measured joint preparation sets."""
from copy import deepcopy
from fractions import Fraction as Q
import json
import unittest
import calibration_bridge as b


class CalibrationBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads((b.HERE / 'synthetic_calibration.json').read_text())

    def test_complete_rational_replay_and_comfortable_slack(self):
        out = b.verify_saved()
        self.assertTrue(out['mathematical_contract_passes'])
        self.assertLess(Q(out['query_source_diameter_bound']), Q('0.000060053'))
        self.assertGreater(min(map(Q, out['row_slack'])), Q('0.00003579'))
        self.assertGreater(Q(out['maximum_weighted_readout_noise_radius']), Q('0.0000024787'))
        uniform = deepcopy(self.record)
        uniform['design'] = 'uniform_AB'
        uniform_out = b.assess(uniform)
        self.assertTrue(uniform_out['mathematical_contract_passes'])
        self.assertNotEqual(out['weighted_noise_gains'], uniform_out['weighted_noise_gains'])

    def test_known_center_translation_changes_domain_not_ambiguity(self):
        a = b.assess(self.record)
        shifted = deepcopy(self.record)
        for g in ('A', 'B'):
            shifted['launches'][g]['measured_initial_state'] = list(map(str, b.NOMINAL[g]))
        c = b.assess(shifted)
        self.assertNotEqual(a['preparation_centers'], c['preparation_centers'])
        self.assertEqual(a['row_lhs'], c['row_lhs'])
        self.assertEqual(a['query_source_diameter_bound'], c['query_source_diameter_bound'])
        self.assertFalse(a['zero_center_envelope_control_passes'])
        self.assertTrue(c['zero_center_envelope_control_passes'])

    def test_outer_domain_cannot_be_traded_for_small_width(self):
        shifted = deepcopy(self.record)
        shifted['launches']['B']['measured_initial_state'][0] = str(b.NOMINAL['B'][0] + Q('0.000007'))
        with self.assertRaises(ValueError):
            b.assess(shifted)

    def test_shared_projection_independent_direct_sensor_sum(self):
        out = b.assess(self.record)
        raw, _ = b.frozen_sources()
        report, nominal, decoder = b.verified_sources(raw)
        d = b.ch.ingredients(report, nominal, b.ch.DESIGNS['selected_AB'], decoder['designs']['selected_AB']['ingredients']['b'])
        direct = [[b.ch.maxabs(b.ch.sum_intervals([b.ch.scale(d['b'][i][k], b.ch.iv(report['rows'][j]['preparation_jacobian'][a]))
                                                 for k, j in enumerate(d['indices'])])) for a in range(4)] for i in range(3)]
        self.assertEqual(b.encode(direct), out['shared_projected_gains'])
        for a, c in zip(out['row_lhs'], out['independent_systematic_control_row_lhs']):
            self.assertLessEqual(Q(a), Q(c))
        self.assertGreater(Q(out['independent_systematic_control_row_lhs'][0]) - Q(out['row_lhs'][0]), Q('0.00000226'))

    def test_shared_bias_cancellation_toy_and_independent_obstruction(self):
        # y=x+p_A-p_B, p_A=b+v_A, p_B=b+v_B: b cancels exactly.
        for common in (Q(-100), Q(0), Q(100)):
            self.assertEqual(Q(7) + (common + Q(2)) - (common + Q(3)), Q(6))
        # Treating b_A,b_B independently changes the admissible model.
        self.assertEqual(Q(0) + Q(1) - Q(-1), Q(2) + Q(0) - Q(0))

    def test_noise_boundary_and_beyond_are_exactly_distinguished(self):
        out = b.assess(self.record)
        boundary = deepcopy(self.record)
        boundary['readout_noise_radius'] = out['maximum_weighted_readout_noise_radius']
        checked = b.assess(boundary)
        self.assertEqual(min(map(Q, checked['row_slack'])), 0)
        boundary['readout_noise_radius'] = str(Q(boundary['readout_noise_radius']) + Q(1, 10 ** 15))
        with self.assertRaises(ValueError):
            b.assess(boundary)

    def test_synthetic_records_never_supply_physical_validation(self):
        self.assertEqual(b.assess(self.record)['physical_validation'], 'NOT_RUN')
        declared_physical = deepcopy(self.record)
        declared_physical['evidence_kind'] = 'physical_record'
        self.assertEqual(b.assess(declared_physical)['physical_validation'], 'REQUIRES_EXTERNAL_PROVENANCE_AND_MODEL_VALIDATION')
        with self.assertRaises(ValueError):
            b.assess({'evidence_kind': 'browser-ensemble', 'N': 1000})

    def test_reprepared_launch_wrong_clock_units_and_float_rejected(self):
        for change in ('reprepared', 'clock', 'units', 'float', 'extra', 'duplicate_id', 'state_string'):
            altered = deepcopy(self.record)
            if change == 'reprepared':
                altered['launches']['A']['same_preparation_for_all_readings'] = False
            elif change == 'clock':
                altered['source_contract']['clock'] = 'one independent clock per launch'
            elif change == 'units':
                altered['units'][2] = 'radians per nominal clock second'
            elif change == 'float':
                altered['launches']['A']['measured_initial_state'][0] = .8
            elif change == 'extra':
                altered['averaging_gain'] = 1000
            elif change == 'duplicate_id':
                altered['launches']['B']['launch_id'] = altered['launches']['A']['launch_id']
            else:
                altered['launches']['A']['measured_initial_state'] = '0000'
            with self.assertRaises(ValueError):
                b.assess(altered)

    def test_reversed_support_missing_evidence_and_bad_source_box(self):
        for change in ('reversed', 'evidence', 'radius'):
            altered = deepcopy(self.record)
            if change == 'reversed':
                altered['shared_systematic'][0] = ['1', '-1']
            elif change == 'evidence':
                altered['launches']['A']['evidence_reference'] = ''
            else:
                altered['source_radius'] = '1/1000'
            with self.assertRaises(ValueError):
                b.assess(altered)

    def test_mutated_prior_intervals_are_not_trusted_from_cache(self):
        raw, _ = b.frozen_sources()
        b.verified_sources(raw)
        report = json.loads(raw[0])
        report['rows'][0]['preparation_jacobian'][0] = ['0', '0']
        forged = (json.dumps(report).encode(), raw[1], raw[2])
        with self.assertRaises(ValueError):
            b.verified_sources(forged)
        first = b.verified_sources(raw)
        first[0]['rows'][0]['preparation_jacobian'][0] = ['0', '0']
        self.assertNotEqual(first[0], b.verified_sources(raw)[0])


if __name__ == '__main__':
    unittest.main(verbosity=2)
