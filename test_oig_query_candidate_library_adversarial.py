"""Adversarial comparability controls for finite query-candidate libraries."""

import unittest

from oig_query_candidate_library import (
    QueryCandidate,
    certify_query_candidate_library,
    verify_query_candidate_library_report,
)


class QueryCandidateLibraryAdversarialTests(unittest.TestCase):
    @staticmethod
    def _candidate(
        name: str,
        *,
        query: list[list[int]],
        query_metric: list[list[int]],
        source_metric: list[list[int]] | None = None,
    ) -> QueryCandidate:
        return QueryCandidate.single_model(
            name,
            [[2]],
            None,
            [[1]] if source_metric is None else source_metric,
            [[1]],
            query,
            query_metric,
        )

    def test_zero_query_cannot_win_a_library_for_a_different_query(self) -> None:
        nonzero = self._candidate("recover x", query=[[1]], query_metric=[[1]])
        zero = self._candidate("recover nothing", query=[[0]], query_metric=[[1]])
        with self.assertRaisesRegex(ValueError, "query|compar"):
            certify_query_candidate_library([nonzero, zero])

    def test_rescaling_query_metric_cannot_manufacture_a_better_design(self) -> None:
        canonical = self._candidate("canonical units", query=[[1]], query_metric=[[1]])
        rescaled = self._candidate(
            "changed loss units", query=[[1]], query_metric=[[100]]
        )
        with self.assertRaisesRegex(ValueError, "query metric|compar"):
            certify_query_candidate_library([canonical, rescaled])

    def test_source_convention_is_part_of_the_comparison_contract(self) -> None:
        first = self._candidate(
            "source convention one",
            query=[[1]],
            query_metric=[[1]],
            source_metric=[[1]],
        )
        second = self._candidate(
            "source convention two",
            query=[[1]],
            query_metric=[[1]],
            source_metric=[[7]],
        )
        with self.assertRaisesRegex(ValueError, "source metric|compar"):
            certify_query_candidate_library([first, second])

    def test_common_contract_is_serialized_and_sealed(self) -> None:
        first = self._candidate("first", query=[[1]], query_metric=[[3]])
        second = QueryCandidate.single_model(
            "second", [[4]], None, [[1]], [[2]], [[1]], [[3]]
        )
        report = certify_query_candidate_library([first, second])
        contract = report["comparison_contract"]
        self.assertEqual(contract["declared_query_exact"], [["1/1"]])
        self.assertEqual(contract["declared_query_metric_exact"], [["3/1"]])
        self.assertEqual(contract["declared_source_metric_exact"], [["1/1"]])
        self.assertTrue(verify_query_candidate_library_report(report)["passed"])


if __name__ == "__main__":
    unittest.main()
