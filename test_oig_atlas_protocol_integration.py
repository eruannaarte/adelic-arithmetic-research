"""Integration and tamper tests for the Arithmetic-Atlas protocol demo."""

from copy import deepcopy
import json
import unittest

from oig_atlas_protocol_integration import (
    run_integration_demo,
    verify_atlas_protocol_integration_report,
)


class AtlasProtocolIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run_integration_demo()

    def test_pinned_report_self_verifies_after_json_round_trip(self) -> None:
        submitted = json.loads(json.dumps(self.report))
        self.assertTrue(
            verify_atlas_protocol_integration_report(submitted)["passed"]
        )

    def test_gain_library_selects_the_stronger_measurement(self) -> None:
        selection = self.report["query_gain_library"]["selection"]
        self.assertEqual(selection["selected_candidate_name"], "double gain")
        self.assertTrue(selection["unique_winner_certified"])

    def test_shared_and_independent_nuisance_are_not_conflated(self) -> None:
        library = self.report["shared_vs_independent_nuisance_library"]
        self.assertEqual(library["identifiable_candidate_count"], 1)
        self.assertEqual(
            library["selection"]["selected_candidate_name"],
            "one nuisance shared across protocols",
        )

    def test_all_integration_obligations_are_explicit(self) -> None:
        ledger = self.report["integration_ledger"]
        self.assertTrue(ledger["all_pinned_integration_obligations_pass"])
        self.assertTrue(
            ledger["response_box_information_composition_remains_external"]
        )
        self.assertTrue(
            ledger[
                "selected_protocol_remains_disjoint_under_structured_nuisance_and_declared_noise"
            ]
        )
        self.assertTrue(
            ledger["selected_protocol_metrics_are_shared_across_followthrough"]
        )

    def test_nested_and_top_level_tampering_are_rejected(self) -> None:
        mutations = []

        nested = deepcopy(self.report)
        nested["query_gain_library"]["selection"][
            "selected_candidate_name"
        ] = "unit gain"
        mutations.append(nested)

        ledger = deepcopy(self.report)
        ledger["integration_ledger"][
            "response_box_information_composition_remains_external"
        ] = False
        mutations.append(ledger)

        boundary = deepcopy(self.report)
        boundary["proof_boundary"] = "unrestricted physical theorem"
        mutations.append(boundary)

        verification = deepcopy(self.report)
        verification["independent_verification"]["passed"] = False
        mutations.append(verification)

        missing_verification = deepcopy(self.report)
        del missing_verification["independent_verification"]
        mutations.append(missing_verification)

        surplus = deepcopy(self.report)
        surplus["unverified_claim"] = True
        mutations.append(surplus)

        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.assertFalse(
                    verify_atlas_protocol_integration_report(mutation)["passed"]
                )


if __name__ == "__main__":
    unittest.main()
