"""Tests for finite-library query-directed experimental design certificates."""

from copy import deepcopy
from fractions import Fraction
import json
import unittest

from oig_query_candidate_library import (
    QueryCandidate,
    certify_query_candidate_library,
    verify_query_candidate_library_report,
)
from oig_query_protocol_design import QueryProtocol, certify_query_model


class QueryCandidateLibraryTests(unittest.TestCase):
    @staticmethod
    def _gain(name: str, gain: int) -> QueryCandidate:
        return QueryCandidate.single_model(
            name, [[gain]], None, [[1]], [[1]], [[1]], [[1]]
        )

    @staticmethod
    def _blind(name: str) -> QueryCandidate:
        return QueryCandidate.single_model(
            name, [[0]], None, [[1]], [[1]], [[1]], [[1]]
        )

    @staticmethod
    def _zero_query(name: str) -> QueryCandidate:
        return QueryCandidate.single_model(
            name, [[1]], None, [[1]], [[1]], [[0]], [[1]]
        )

    def test_selects_smallest_upper_and_certifies_library_bracket(self) -> None:
        report = certify_query_candidate_library(
            [self._gain("gain one", 1), self._gain("gain two", 2), self._blind("blind")]
        )
        selection = report["selection"]
        self.assertEqual(selection["selected_candidate_index"], 1)
        self.assertEqual(selection["selected_candidate_name"], "gain two")
        self.assertEqual(
            selection["library_optimum_kappa_squared_lower_exact"], "1/4"
        )
        self.assertGreater(
            Fraction(selection["library_optimum_kappa_squared_upper_exact"]),
            Fraction(1, 4),
        )
        self.assertLess(
            Fraction(selection["library_optimum_kappa_squared_upper_exact"]),
            Fraction(1, 1),
        )
        self.assertTrue(selection["unique_winner_certified"])
        self.assertEqual(report["identifiable_candidate_count"], 2)
        self.assertTrue(
            report["comparison_contract"]["common_contract_verified_exact"]
        )
        self.assertIn(
            "same numerical epsilon",
            report["comparison_contract"]["data_noise_radius_convention"],
        )
        self.assertEqual(
            report["candidates"][2]["classification"],
            "unidentifiable-infinite-loss",
        )
        self.assertIsNone(report["candidates"][2]["kappa_squared_upper_exact"])
        self.assertTrue(verify_query_candidate_library_report(report)["passed"])

    def test_tied_upper_uses_declaration_order_but_does_not_claim_uniqueness(self) -> None:
        report = certify_query_candidate_library(
            [self._gain("first", 2), self._gain("second", 2)]
        )
        selection = report["selection"]
        self.assertEqual(selection["selected_candidate_index"], 0)
        self.assertEqual(selection["selected_candidate_name"], "first")
        self.assertFalse(selection["unique_winner_certified"])
        self.assertFalse(
            selection["competitor_checks"][0][
                "selected_upper_strictly_below_competitor_lower"
            ]
        )

    def test_zero_query_library_is_exact_but_tied_zero_designs_are_not_unique(self) -> None:
        single = certify_query_candidate_library([self._zero_query("zero")])
        selection = single["selection"]
        self.assertEqual(selection["selected_candidate_name"], "zero")
        self.assertEqual(selection["library_optimum_kappa_squared_lower_exact"], "0/1")
        self.assertEqual(selection["library_optimum_kappa_squared_upper_exact"], "0/1")
        self.assertTrue(selection["unique_winner_certified"])
        self.assertEqual(
            single["candidates"][0]["classification"],
            "identifiable-zero-query",
        )

        tied = certify_query_candidate_library(
            [self._zero_query("zero first"), self._zero_query("zero second")]
        )
        self.assertEqual(tied["selection"]["selected_candidate_index"], 0)
        self.assertFalse(tied["selection"]["unique_winner_certified"])

    def test_zero_and_nonzero_queries_cannot_be_compared(self) -> None:
        with self.assertRaisesRegex(ValueError, "common comparison contract"):
            certify_query_candidate_library(
                [self._gain("nonzero query", 1), self._zero_query("zero query")]
            )

    def test_dimension_metric_and_query_contract_mismatches_are_rejected(self) -> None:
        source_dimension_two = QueryCandidate.single_model(
            "two source coordinates",
            [[1, 0]],
            None,
            [[1, 0], [0, 1]],
            [[1]],
            [[1, 0]],
            [[1]],
        )
        query_dimension_two = QueryCandidate.single_model(
            "two query coordinates",
            [[1]],
            None,
            [[1]],
            [[1]],
            [[1], [1]],
            [[1, 0], [0, 1]],
        )
        different_source_metric = QueryCandidate.single_model(
            "different source metric",
            [[1]],
            None,
            [[2]],
            [[1]],
            [[1]],
            [[1]],
        )
        different_query_metric = QueryCandidate.single_model(
            "different query metric",
            [[1]],
            None,
            [[1]],
            [[1]],
            [[1]],
            [[2]],
        )
        baseline = self._gain("baseline", 1)
        for hostile in (
            source_dimension_two,
            query_dimension_two,
            different_source_metric,
            different_query_metric,
        ):
            with self.subTest(hostile=hostile.name):
                with self.assertRaisesRegex(ValueError, "common comparison contract"):
                    certify_query_candidate_library([baseline, hostile])

    def test_only_identifiable_candidate_is_vacuously_unique(self) -> None:
        report = certify_query_candidate_library(
            [self._blind("blind"), self._gain("finite", 1)]
        )
        selection = report["selection"]
        self.assertTrue(selection["unique_winner_certified"])
        self.assertEqual(
            selection["unique_winner_basis"],
            "only identifiable candidate in the declared library",
        )
        self.assertEqual(selection["competitor_checks"], [])

    def test_all_unidentifiable_library_has_no_finite_selection(self) -> None:
        report = certify_query_candidate_library(
            [self._blind("blind one"), self._blind("blind two")]
        )
        selection = report["selection"]
        self.assertEqual(selection["outcome"], "no-identifiable-candidate")
        self.assertIsNone(selection["selected_candidate_index"])
        self.assertIsNone(selection["library_optimum_kappa_squared_lower_exact"])
        self.assertIsNone(selection["library_optimum_kappa_squared_upper_exact"])
        self.assertFalse(selection["unique_winner_certified"])
        self.assertTrue(verify_query_candidate_library_report(report)["passed"])

    def test_shared_and_independent_nuisance_semantics_compose_without_conflation(self) -> None:
        protocols = (
            QueryProtocol.from_rows("first", [[1]], [[1]], [[1]]),
            QueryProtocol.from_rows("second", [[2]], [[1]], [[1]]),
        )
        shared = QueryCandidate.shared_mixture(
            "shared nuisance",
            protocols,
            [Fraction(1, 2), Fraction(1, 2)],
            [[1]],
            [[1]],
            [[1]],
        )
        independent = QueryCandidate.independent_mixture(
            "independent refits",
            protocols,
            [Fraction(1, 2), Fraction(1, 2)],
            [[1]],
            [[1]],
            [[1]],
        )
        report = certify_query_candidate_library([shared, independent])
        self.assertEqual(report["selection"]["selected_candidate_name"], "shared nuisance")
        self.assertTrue(report["selection"]["unique_winner_certified"])
        self.assertEqual(
            report["candidates"][0]["query_certificate"]["model_kind"],
            "shared_nuisance_protocol_mixture",
        )
        self.assertEqual(
            report["candidates"][1]["query_certificate"]["model_kind"],
            "independent_nuisance_protocol_mixture",
        )
        self.assertEqual(
            report["candidates"][1]["classification"],
            "unidentifiable-infinite-loss",
        )

    def test_existing_reports_and_json_round_trip_are_self_contained(self) -> None:
        child = certify_query_model(
            [[3]], None, [[1]], [[1]], [[1]], [[1]]
        )
        report = certify_query_candidate_library([("existing report", child)])
        round_tripped = json.loads(json.dumps(report))
        result = verify_query_candidate_library_report(round_tripped)
        self.assertTrue(result["passed"])
        self.assertEqual(result["candidate_certificates_verified"], 1)

    def test_huge_exact_rationals_do_not_require_a_float_path(self) -> None:
        huge = 10**400
        candidate = QueryCandidate.single_model(
            "huge exact gain", [[huge]], None, [[1]], [[1]], [[1]], [[1]]
        )
        report = certify_query_candidate_library([candidate])
        row = report["candidates"][0]
        self.assertEqual(
            row["kappa_squared_lower_exact"], f"1/{huge * huge}"
        )
        self.assertTrue(verify_query_candidate_library_report(report)["passed"])

    def test_invalid_library_declarations_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "nonempty"):
            certify_query_candidate_library([])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            certify_query_candidate_library(
                [self._gain("same", 1), self._gain("same", 2)]
            )
        with self.assertRaisesRegex(ValueError, "trimmed"):
            certify_query_candidate_library(
                [QueryCandidate(" padded ", self._gain("unused", 1).query_certificate)]
            )
        with self.assertRaisesRegex(TypeError, "QueryCandidate"):
            certify_query_candidate_library([{"name": "not accepted"}])  # type: ignore[list-item]

    def test_invalid_child_report_is_rejected_at_composition_boundary(self) -> None:
        child = self._gain("valid", 1).query_certificate
        tampered = deepcopy(child)
        del tampered["independent_exact_verification"]
        with self.assertRaisesRegex(ValueError, "failed verification"):
            certify_query_candidate_library([("invalid child", tampered)])

    def test_verifier_rejects_summary_child_and_embedded_tampering(self) -> None:
        report = certify_query_candidate_library(
            [self._gain("one", 1), self._gain("two", 2), self._blind("blind")]
        )
        mutations = []

        changed_selection = deepcopy(report)
        changed_selection["selection"]["selected_candidate_index"] = 0
        mutations.append(changed_selection)

        changed_lower = deepcopy(report)
        changed_lower["candidates"][1]["kappa_squared_lower_exact"] = "0/1"
        mutations.append(changed_lower)

        changed_child = deepcopy(report)
        changed_child["candidates"][0]["query_certificate"][
            "declared_observation_exact"
        ][0][0] = "100/1"
        mutations.append(changed_child)

        changed_child_verification = deepcopy(report)
        changed_child_verification["candidates"][0]["child_exact_verification"][
            "query_identifiable"
        ] = False
        mutations.append(changed_child_verification)

        changed_uniqueness = deepcopy(report)
        changed_uniqueness["selection"]["unique_winner_certified"] = False
        mutations.append(changed_uniqueness)

        changed_contract = deepcopy(report)
        changed_contract["comparison_contract"]["declared_query_exact"] = [["0/1"]]
        mutations.append(changed_contract)

        changed_embedded = deepcopy(report)
        changed_embedded["independent_exact_verification"][
            "candidate_certificates_verified"
        ] = 99
        mutations.append(changed_embedded)

        extra_field = deepcopy(report)
        extra_field["unsupported_claim"] = True
        mutations.append(extra_field)

        for index, tampered in enumerate(mutations):
            with self.subTest(mutation=index):
                self.assertFalse(
                    verify_query_candidate_library_report(tampered)["passed"]
                )

    def test_verifier_is_type_strict_and_requires_embedded_verification(self) -> None:
        report = certify_query_candidate_library([self._gain("one", 1)])
        bool_index = deepcopy(report)
        bool_index["candidates"][0]["index"] = False
        self.assertFalse(verify_query_candidate_library_report(bool_index)["passed"])

        unsealed = deepcopy(report)
        del unsealed["independent_exact_verification"]
        result = verify_query_candidate_library_report(unsealed)
        self.assertFalse(result["passed"])
        self.assertIn("verification block is missing", result["reason"])

    def test_proof_boundary_forbids_continuous_optimality_claim(self) -> None:
        report = certify_query_candidate_library([self._gain("one", 1)])
        self.assertFalse(report["continuous_design_optimality_claimed"])
        self.assertIn("finite library", report["proof_boundary"])
        tampered = deepcopy(report)
        tampered["continuous_design_optimality_claimed"] = True
        self.assertFalse(verify_query_candidate_library_report(tampered)["passed"])


if __name__ == "__main__":
    unittest.main()
