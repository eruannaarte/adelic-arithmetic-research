"""One integrated contract test with adverse cross-model scope controls."""
from copy import deepcopy
from pathlib import Path
import importlib.util,unittest
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_combined_integrity',HERE.parent/'integrity.py')
integrity=importlib.util.module_from_spec(spec);spec.loader.exec_module(integrity)

class SharedTransferTest(unittest.TestCase):
    def test_two_norms_complete_tails_and_conditional_degree_choice(self):
        bundle=integrity.headline_bundle()
        result=integrity.check_headlines(bundle)
        self.assertTrue(result['six_rows_full_clock_potential_contract'])
        self.assertTrue(result['failing_sufficient_gate_is_not_impossibility'])
        self.assertEqual([r['h120_degree12_gates'] for r in result['arithmetic']],[49,49])
        # A certificate for one joint physical box cannot silently certify a
        # larger clock box, even when its previous successful flags survive.
        larger=deepcopy(bundle);larger['spatial']['clock_radius']='1/10000000'
        with self.subTest('uncharged spatial clock'),self.assertRaises(ValueError):integrity.check_headlines(larger)
        # Retaining 32 valuations computationally never permits deletion of
        # the infinite source class's omitted-valution charge.
        truncated=deepcopy(bundle);truncated['orbit']['complete_valuation_tail']['omitted_envelope_mass_upper']='0'
        with self.subTest('deleted arithmetic tail'),self.assertRaises(ValueError):integrity.check_headlines(truncated)
        # A lower-degree failed sufficient gate cannot become a proved query
        # by relabelling the saved success flag.
        false=deepcopy(bundle);false['degree11_orbit']['results'][0]['all_49_strict_rounding_gates']=True
        with self.subTest('false degree11 recovery'),self.assertRaises(ValueError):integrity.check_headlines(false)
        # Public archives may omit exactly the named third-party reference
        # copies; neither additional files nor different reference hashes.
        previous=integrity.read(HERE.parent/'PREVIOUS_ARTIFACTS_SHA256.json')
        archival=set(integrity.ARCHIVAL_REFERENCES)
        self.assertEqual(len(integrity.predecessor_selection(previous,archival)),657)
        with self.subTest('omitted authored proof'),self.assertRaises(ValueError):
            integrity.predecessor_selection(previous,archival|{'five_paths_2026_09/REPORT.md'})
        changed=deepcopy(previous);changed['files'][sorted(archival)[0]]='0'*64
        with self.subTest('different archival reference'),self.assertRaises(ValueError):
            integrity.predecessor_selection(changed,archival)

if __name__=='__main__':unittest.main(verbosity=2)
