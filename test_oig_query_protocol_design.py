"""Positive and adversarial tests for exact query-directed certificates."""

from copy import deepcopy
from fractions import Fraction
import json
import unittest

from oig_query_protocol_design import (
    QueryProtocol,
    certify_query_independent_nuisance_mixture,
    certify_query_model,
    certify_query_protocol_mixture,
    verify_query_protocol_report,
)


class QueryProtocolDesignTests(unittest.TestCase):
    @staticmethod
    def _partial_query_report() -> dict[str, object]:
        # The nuisance destroys the common mode (1,1,0), so the full
        # three-coordinate state is not identifiable.  Difference and third
        # coordinate remain an exactly identifiable two-dimensional query.
        return certify_query_model(
            [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            [[1], [1], [0]],
            [[2, Fraction(1, 3), 0], [Fraction(1, 3), 1, 0], [0, 0, 3]],
            [[2, Fraction(1, 3), 0], [Fraction(1, 3), 1, 0], [0, 0, 4]],
            [[1, -1, 0], [0, 0, 1]],
            [[1, Fraction(1, 4)], [Fraction(1, 4), 2]],
        )

    @staticmethod
    def _two_protocols() -> tuple[QueryProtocol, QueryProtocol]:
        return (
            QueryProtocol.from_rows("first", [[1]], [[1]], [[1]]),
            QueryProtocol.from_rows("second", [[2]], [[1]], [[1]]),
        )

    def test_nontrivial_query_is_identifiable_when_full_state_is_not(self) -> None:
        report = self._partial_query_report()
        self.assertEqual(report["source_dimension"], 3)
        self.assertEqual(report["effective_response_rank"], 2)
        self.assertTrue(report["identifiability"]["query_identifiable_exact"])
        certificate = report["factorization_and_minimax"]
        self.assertTrue(certificate["factorization_exists"])
        self.assertLessEqual(
            Fraction(certificate["minimax_amplification_squared_lower_exact"]),
            Fraction(certificate["minimax_amplification_squared_upper_exact"]),
        )
        self.assertTrue(verify_query_protocol_report(report)["passed"])
        round_tripped = json.loads(json.dumps(report))
        self.assertTrue(verify_query_protocol_report(round_tripped)["passed"])

    def test_strict_gain_demonstrator_has_exact_squared_amplification_two(self) -> None:
        report = certify_query_model(
            [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            [[1], [1], [0]],
            [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            [[1, -1, 0], [0, 0, 1]],
            [[1, 0], [0, 1]],
        )
        self.assertEqual(report["effective_response_rank"], 2)
        self.assertEqual(
            report["factorization_and_minimax"][
                "minimax_amplification_squared_lower_exact"
            ],
            "2/1",
        )

    def test_unidentifiable_query_carries_exact_kernel_counterexample(self) -> None:
        report = certify_query_model(
            [[1, 0], [0, 1]],
            [[1], [1]],
            [[1, 0], [0, 1]],
            [[2, Fraction(1, 2)], [Fraction(1, 2), 1]],
            [[1, 0]],
            [[1]],
        )
        self.assertFalse(report["identifiability"]["query_identifiable_exact"])
        witness = tuple(
            Fraction(value)
            for value in report["identifiability"]["kernel_counterexample_exact"]
        )
        self.assertNotEqual(witness[0], 0)
        self.assertEqual(report["factorization_and_minimax"]["zero_noise_minimax_error"], "infinite")
        self.assertTrue(verify_query_protocol_report(report)["passed"])

    def test_zero_query_is_identifiable_through_zero_effective_response(self) -> None:
        report = certify_query_model(
            [[1], [1]],
            [[1], [1]],
            [[3]],
            [[2, 0], [0, 1]],
            [[0]],
            [[5]],
        )
        self.assertEqual(report["effective_response_rank"], 0)
        certificate = report["factorization_and_minimax"]
        self.assertEqual(certificate["kind"], "identifiable-zero-query")
        self.assertEqual(certificate["minimax_amplification_squared_upper_exact"], "0/1")

    def test_shared_nuisance_mixture_identifies_a_difference_across_protocols(self) -> None:
        # Each protocol alone observes h_i*x+z and is completely blind after
        # profiling z.  Sharing one z across both makes their difference an
        # informative measurement of x.
        report = certify_query_protocol_mixture(
            self._two_protocols(),
            [Fraction(1, 2), Fraction(1, 2)],
            [[1]],
            [[1]],
            [[1]],
        )
        self.assertTrue(report["identifiability"]["query_identifiable_exact"])
        self.assertEqual(
            report["factorization_and_minimax"][
                "minimax_amplification_squared_lower_exact"
            ],
            "4/1",
        )
        self.assertTrue(verify_query_protocol_report(report)["passed"])

    def test_independent_nuisance_refits_restore_linear_information_sum(self) -> None:
        report = certify_query_independent_nuisance_mixture(
            self._two_protocols(),
            [Fraction(1, 2), Fraction(1, 2)],
            [[1]],
            [[1]],
            [[1]],
        )
        self.assertFalse(report["identifiability"]["query_identifiable_exact"])
        mixture = report["protocol_mixture"]
        self.assertTrue(mixture["profiled_information_adds_linearly_exact"])
        self.assertEqual(
            mixture["individually_profiled_information_sum_exact"], [["0/1"]]
        )
        self.assertEqual(
            report["nuisance_elimination"]["profiled_information_exact"], [["0/1"]]
        )
        self.assertTrue(verify_query_protocol_report(report)["passed"])

    def test_unequal_cost_and_zero_share_are_assembled_exactly(self) -> None:
        protocols = (
            QueryProtocol.from_rows("x", [[1, 0]], None, [[2]], cost=2),
            QueryProtocol.from_rows("inactive", [[100, 100]], None, [[1]], cost=7),
            QueryProtocol.from_rows("y", [[0, 1]], None, [[3]], cost=3),
        )
        report = certify_query_independent_nuisance_mixture(
            protocols,
            [Fraction(1, 2), 0, Fraction(1, 2)],
            [[1, 0], [0, 1]],
            [[1, 1]],
            [[1]],
        )
        mixture = report["protocol_mixture"]
        self.assertEqual(mixture["active_protocol_indices"], [0, 2])
        self.assertEqual(
            [row["physical_weight_exact"] for row in mixture["protocols"]],
            ["1/4", "0/1", "1/6"],
        )
        self.assertTrue(verify_query_protocol_report(report)["passed"])

    def test_binary_float_declarations_are_rejected(self) -> None:
        with self.assertRaisesRegex(TypeError, "binary floating"):
            certify_query_model(
                [[1.0]], None, [[1]], [[1]], [[1]], [[1]]
            )

    def test_invalid_metrics_and_mixture_budgets_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "output metric"):
            certify_query_model([[1]], None, [[1]], [[0]], [[1]], [[1]])
        with self.assertRaisesRegex(ValueError, "sum exactly"):
            certify_query_protocol_mixture(
                self._two_protocols(), [Fraction(1, 3), Fraction(1, 3)], [[1]], [[1]], [[1]]
            )

    def test_verifier_rejects_structural_and_minimax_tampering(self) -> None:
        report = self._partial_query_report()
        mutations = []

        changed_projector = deepcopy(report)
        changed_projector["nuisance_elimination"]["metric_orthogonal_projector_exact"][0][0] = "0/1"
        mutations.append(changed_projector)

        changed_rank = deepcopy(report)
        changed_rank["effective_response_rank"] = 3
        mutations.append(changed_rank)

        changed_flag = deepcopy(report)
        changed_flag["identifiability"]["kernel_condition_exact"] = False
        mutations.append(changed_flag)

        changed_decoder = deepcopy(report)
        changed_decoder["factorization_and_minimax"]["decoder_exact"][0][0] = "0/1"
        mutations.append(changed_decoder)

        changed_upper = deepcopy(report)
        changed_upper["factorization_and_minimax"][
            "minimax_amplification_squared_upper_exact"
        ] = "0/1"
        mutations.append(changed_upper)

        changed_lower = deepcopy(report)
        changed_lower["factorization_and_minimax"][
            "minimax_amplification_squared_lower_exact"
        ] = "0/1"
        mutations.append(changed_lower)

        changed_query_metric = deepcopy(report)
        changed_query_metric["declared_query_metric_exact"][0][0] = "100/1"
        mutations.append(changed_query_metric)

        for index, tampered in enumerate(mutations):
            with self.subTest(mutation=index):
                self.assertFalse(verify_query_protocol_report(tampered)["passed"])

    def test_verifier_rejects_unidentifiable_witness_tampering(self) -> None:
        report = certify_query_model(
            [[1, 0], [0, 1]], [[1], [1]], [[1, 0], [0, 1]], [[1, 0], [0, 1]], [[1, 0]], [[1]]
        )
        tampered = deepcopy(report)
        tampered["identifiability"]["kernel_counterexample_exact"] = ["0/1", "0/1"]
        self.assertFalse(verify_query_protocol_report(tampered)["passed"])

    def test_verifier_rejects_shared_mixture_semantics_and_weights_tampering(self) -> None:
        report = certify_query_protocol_mixture(
            self._two_protocols(), [Fraction(1, 2), Fraction(1, 2)], [[1]], [[1]], [[1]]
        )
        mutations = []
        semantics = deepcopy(report)
        semantics["protocol_mixture"]["nuisance_semantics"] = "independent"
        mutations.append(semantics)

        physical = deepcopy(report)
        physical["protocol_mixture"]["protocols"][0]["physical_weight_exact"] = "3/4"
        mutations.append(physical)

        active = deepcopy(report)
        active["protocol_mixture"]["active_protocol_indices"] = [1]
        mutations.append(active)

        for index, tampered in enumerate(mutations):
            with self.subTest(mutation=index):
                self.assertFalse(verify_query_protocol_report(tampered)["passed"])

    def test_verifier_rejects_independent_linear_sum_tampering(self) -> None:
        report = certify_query_independent_nuisance_mixture(
            self._two_protocols(), [Fraction(1, 2), Fraction(1, 2)], [[1]], [[1]], [[1]]
        )
        tampered = deepcopy(report)
        tampered["protocol_mixture"]["profiled_information_adds_linearly_exact"] = False
        self.assertFalse(verify_query_protocol_report(tampered)["passed"])


if __name__ == "__main__":
    unittest.main()
