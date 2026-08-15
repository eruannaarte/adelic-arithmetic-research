"""Independent adversarial controls for the query-directed certificate lane.

The positive controls below calculate their expected values without importing
private matrix helpers from the implementation.  The serialization controls
encode the intended boundary for a proof-producing report: the embedded
verification result and canonical scope statement are part of the report, and
contradictory theorem-like fields must not survive an ostensibly successful
standalone verification.
"""

from copy import deepcopy
from fractions import Fraction
import unittest

from oig_query_protocol_design import (
    QueryProtocol,
    certify_query_independent_nuisance_mixture,
    certify_query_model,
    verify_query_protocol_report,
)


Q = Fraction


def _matrix(block: object) -> tuple[tuple[Fraction, ...], ...]:
    if not isinstance(block, list):
        raise AssertionError("serialized matrix is not a list")
    return tuple(tuple(Q(value) for value in row) for row in block)


class QueryProtocolDesignAdversarialTests(unittest.TestCase):
    @staticmethod
    def _metric_example() -> dict[str, object]:
        # H=I, nuisance span(1,1), L=(1,-1),
        # W=[[2,1],[1,3]], and T=5.  For h=(1,-1),
        # min_z ||h+z(1,1)||_W^2 = 20/7 while ||Lh||_T^2=20,
        # hence the exact squared amplification is 7.
        return certify_query_model(
            [[1, 0], [0, 1]],
            [[1], [1]],
            [[1, 0], [0, 1]],
            [[2, 1], [1, 3]],
            [[1, -1]],
            [[5]],
        )

    @staticmethod
    def _unidentifiable_report() -> dict[str, object]:
        return certify_query_model(
            [[1, 0], [0, 1]],
            [[1], [1]],
            [[1, 0], [0, 1]],
            [[1, 0], [0, 1]],
            [[1, 0]],
            [[1]],
        )

    @staticmethod
    def _zero_effective_report() -> dict[str, object]:
        return certify_query_model(
            [[1], [1]],
            [[1], [1]],
            [[1]],
            [[2, 0], [0, 1]],
            [[0]],
            [[5]],
        )

    def test_nondiagonal_metric_projector_and_minimax_are_exact(self) -> None:
        report = self._metric_example()
        elimination = report["nuisance_elimination"]
        certificate = report["factorization_and_minimax"]
        self.assertEqual(
            _matrix(elimination["metric_orthogonal_projector_exact"]),
            ((Q(4, 7), Q(-4, 7)), (Q(-3, 7), Q(3, 7))),
        )
        self.assertEqual(
            _matrix(certificate["decoder_exact"]), ((Q(1), Q(-1)),)
        )
        self.assertEqual(
            Q(certificate["minimax_amplification_squared_lower_exact"]), Q(7)
        )
        self.assertGreater(
            Q(certificate["minimax_amplification_squared_upper_exact"]), Q(7)
        )

    def test_output_coordinate_recalibration_preserves_the_certificate(self) -> None:
        original = self._metric_example()
        # y'=M y for M=[[2,1],[1,1]].  Thus H'=M, B'=M B=(3,2),
        # W'=M^-T W M^-1=[[3,-5],[-5,10]], and D'=D M^-1=(2,-3).
        transformed = certify_query_model(
            [[2, 1], [1, 1]],
            [[3], [2]],
            [[1, 0], [0, 1]],
            [[3, -5], [-5, 10]],
            [[1, -1]],
            [[5]],
        )
        original_certificate = original["factorization_and_minimax"]
        transformed_certificate = transformed["factorization_and_minimax"]
        self.assertEqual(
            original_certificate["minimax_amplification_squared_lower_exact"],
            transformed_certificate["minimax_amplification_squared_lower_exact"],
        )
        self.assertEqual(
            _matrix(transformed_certificate["decoder_exact"]),
            ((Q(2), Q(-3)),),
        )

    def test_redundant_nuisance_coordinates_do_not_change_the_quotient(self) -> None:
        original = self._metric_example()
        redundant = certify_query_model(
            [[1, 0], [0, 1]],
            [[1, 2], [1, 2]],
            [[3, 1], [1, 2]],
            [[2, 1], [1, 3]],
            [[1, -1]],
            [[5]],
        )
        self.assertEqual(original["nuisance_rank"], redundant["nuisance_rank"])
        self.assertEqual(
            original["nuisance_elimination"]["metric_orthogonal_projector_exact"],
            redundant["nuisance_elimination"]["metric_orthogonal_projector_exact"],
        )
        self.assertEqual(
            original["factorization_and_minimax"][
                "minimax_amplification_squared_lower_exact"
            ],
            redundant["factorization_and_minimax"][
                "minimax_amplification_squared_lower_exact"
            ],
        )

    def test_zero_query_with_nonzero_effective_response_is_certified_zero(self) -> None:
        report = certify_query_model(
            [[1]], None, [[7]], [[3]], [[0]], [[11]]
        )
        certificate = report["factorization_and_minimax"]
        self.assertEqual(report["effective_response_rank"], 1)
        self.assertEqual(
            certificate["minimax_amplification_squared_lower_exact"], "0/1"
        )
        self.assertEqual(
            certificate["minimax_amplification_squared_upper_exact"], "0/1"
        )
        self.assertTrue(verify_query_protocol_report(report)["passed"])

    def test_huge_rational_scale_uses_exact_fallback_without_overflow(self) -> None:
        huge_integer = 10**400
        huge = str(huge_integer)
        report = certify_query_model(
            [[huge, 0], [0, huge]],
            None,
            [[1, 0], [0, 1]],
            [[1, 0], [0, 1]],
            [[1, 0], [0, 1]],
            [[1, 0], [0, 1]],
        )
        certificate = report["factorization_and_minimax"]
        expected = Q(1, huge_integer * huge_integer)
        self.assertEqual(
            Q(certificate["minimax_amplification_squared_lower_exact"]),
            expected,
        )
        self.assertGreaterEqual(
            Q(certificate["minimax_amplification_squared_upper_exact"]),
            expected,
        )
        self.assertTrue(verify_query_protocol_report(report)["passed"])

    def test_embedded_verification_is_required_and_reproduced(self) -> None:
        original = self._metric_example()
        mutations = []

        deleted = deepcopy(original)
        deleted.pop("independent_exact_verification")
        mutations.append(deleted)

        false_pass = deepcopy(original)
        false_pass["independent_exact_verification"]["passed"] = False
        mutations.append(false_pass)

        false_bound = deepcopy(original)
        false_bound["independent_exact_verification"][
            "amplification_squared_lower_exact"
        ] = "999/1"
        mutations.append(false_bound)

        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                self.assertFalse(verify_query_protocol_report(mutation)["passed"])

    def test_scope_boundary_is_part_of_the_sealed_certificate(self) -> None:
        report = self._metric_example()
        report["proof_boundary"] = (
            "This certificate proves that the external physical model is exact."
        )
        self.assertFalse(verify_query_protocol_report(report)["passed"])

    def test_independent_nuisance_boundary_does_not_call_the_nuisance_shared(self) -> None:
        protocols = (
            QueryProtocol.from_rows("first", [[1]], [[1]], [[1]]),
            QueryProtocol.from_rows("second", [[2]], [[1]], [[1]]),
        )
        report = certify_query_independent_nuisance_mixture(
            protocols, [Q(1, 2), Q(1, 2)], [[1]], [[1]], [[1]]
        )
        self.assertNotIn("shared nuisance", report["proof_boundary"].lower())

    def test_unidentifiable_early_return_rejects_mutated_reason_and_surplus_claims(self) -> None:
        original = self._unidentifiable_report()
        mutations = []

        missing_reason = deepcopy(original)
        missing_reason["factorization_and_minimax"].pop("reason")
        mutations.append(missing_reason)

        false_reason = deepcopy(original)
        false_reason["factorization_and_minimax"]["reason"] = (
            "the query is identifiable with finite error"
        )
        mutations.append(false_reason)

        false_decoder = deepcopy(original)
        false_decoder["factorization_and_minimax"]["decoder_exact"] = [
            ["0/1", "0/1"]
        ]
        mutations.append(false_decoder)

        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                self.assertFalse(verify_query_protocol_report(mutation)["passed"])

    def test_zero_query_early_return_rejects_contradictory_surplus_claims(self) -> None:
        original = self._zero_effective_report()
        mutations = []

        false_raw_factor = deepcopy(original)
        false_raw_factor["factorization_and_minimax"][
            "decoder_times_raw_observation_equals_query_exact"
        ] = False
        mutations.append(false_raw_factor)

        false_minimax = deepcopy(original)
        false_minimax["factorization_and_minimax"]["zero_noise_minimax_error"] = (
            "infinite"
        )
        mutations.append(false_minimax)

        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                self.assertFalse(verify_query_protocol_report(mutation)["passed"])


if __name__ == "__main__":
    unittest.main()
