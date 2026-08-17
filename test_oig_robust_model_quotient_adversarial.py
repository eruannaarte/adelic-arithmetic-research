"""Independent adversarial controls for robust model-aware quotients.

The positive controls use hand-derived coordinate transformations and simple
one-dimensional counterexamples.  The tests intentionally distinguish a
stable response quotient from task irrelevance and from bounded leakage under
operator uncertainty.
"""

from copy import deepcopy
from fractions import Fraction
import json
import unittest

from oig_robust_model_quotient import (
    _sqrt_bounds,
    certify_combined_model_design,
    certify_finite_quotient_secants,
    certify_nominal_blind_uncertainty,
    certify_nominal_null_relevance,
    certify_quotient_tube_pair,
    certify_response_tube_pair,
    classify_lattice_trichotomy_from_exact_predicates,
    exact_model_quotient,
    quotient_distance_squared,
    verify_robust_model_report,
)


Q = Fraction
I2 = [[1, 0], [0, 1]]


class RobustModelQuotientAdversarialTests(unittest.TestCase):
    def test_source_coordinate_change_preserves_quotient_distance(self) -> None:
        # x=T x' for T=[[1,1],[0,1]].  Hence H'=HT, S'=T^TST,
        # and v'=T^-1 v.  Both declarations represent the same geometry.
        original = exact_model_quotient([[1, 1]], [[1, 0], [0, 4]])
        transformed = exact_model_quotient([[1, 2]], [[1, 1], [1, 5]])
        self.assertEqual(quotient_distance_squared(original, [1, 2]), Q(36, 5))
        self.assertEqual(
            quotient_distance_squared(original, [1, 2]),
            quotient_distance_squared(transformed, [-1, 2]),
        )

    def test_directed_sqrt_bounds_are_outward_even_at_low_precision(self) -> None:
        lower, upper = _sqrt_bounds(Q(2), bits=2)
        self.assertLessEqual(lower * lower, Q(2))
        self.assertGreaterEqual(upper * upper, Q(2))
        self.assertLess(lower, upper)
        exact_lower, exact_upper = _sqrt_bounds(Q(9, 4), bits=2)
        self.assertEqual(exact_lower, Q(3, 2))
        self.assertEqual(exact_upper, Q(3, 2))

    def test_huge_rational_scale_does_not_make_exact_certification_overflow(self) -> None:
        huge = str(10**400)
        upper_report = certify_response_tube_pair(
            [[huge, 0], [0, huge]],
            I2,
            I2,
            [1, 0],
            source_radius=0,
            data_noise_radius=1,
        )
        self.assertEqual(upper_report["status"], "certified_disjoint")
        self.assertTrue(verify_robust_model_report(upper_report)["passed"])

        lower_report = certify_combined_model_design(
            I2,
            I2,
            [[huge, 0], [0, huge]],
            [[1, 0]],
            [I2],
            query_matrix=I2,
        )
        self.assertGreater(
            Q(lower_report["quotient_information_floor_lower_exact"]), Q(0)
        )
        self.assertTrue(verify_robust_model_report(lower_report)["passed"])

    def test_finite_secant_gap_floor_is_never_reported_negative(self) -> None:
        # sqrt(2)>5/4, so the true eroded gap is positive.  At one dyadic bit
        # the directed distance lower is only 1; the certified gap should be
        # clamped to the universal lower bound zero, not serialized as -1/4.
        report = certify_finite_quotient_secants(
            I2,
            I2,
            [[1, 1]],
            source_radius="5/8",
            sqrt_bits=1,
        )
        self.assertFalse(report["secants"][0]["tube_overlap_exact"])
        self.assertEqual(report["minimum_eroded_gap_lower_exact"], "0/1")
        self.assertEqual(report["secants"][0]["eroded_gap_lower_exact"], "0/1")

    def test_unlabelled_finite_sample_cannot_prove_task_irrelevance(self) -> None:
        report = certify_nominal_null_relevance(
            [[1, 0]],
            I2,
            query_matrix=[[0, 1]],
            model_secants=[[1, 0]],
            response_radius=[[0, 1]],
        )
        self.assertTrue(report["declared_model_secants_exclude_kernel_collisions"])
        self.assertFalse(report["model_secants_exhaustive"])
        self.assertFalse(report["exhaustive_model_secants_prove_task_irrelevance"])
        self.assertFalse(report["nominal_null_task_irrelevant"])
        self.assertFalse(report["nominal_null_safe_to_ignore"])

    def test_family_preservation_is_stability_not_query_relevance(self) -> None:
        report = certify_nominal_null_relevance(
            [[1, 0]],
            I2,
            query_matrix=[[0, 1]],
            model_secants=[[0, 1]],
            response_radius=[[0, 0]],
        )
        self.assertTrue(report["entire_response_box_preserves_nominal_null"])
        self.assertTrue(report["quotient_family_stable"])
        self.assertFalse(report["kernel_is_subset_of_query_kernel"])
        self.assertFalse(report["nominal_null_task_irrelevant"])

    def test_exhaustive_secant_claim_requires_explicit_provenance(self) -> None:
        with self.assertRaisesRegex(ValueError, "provenance"):
            certify_nominal_null_relevance(
                [[1, 0]],
                I2,
                model_secants=[[1, 1]],
                model_secants_exhaustive=True,
            )
        report = certify_nominal_null_relevance(
            [[1, 0]],
            I2,
            model_secants=[[1, 1]],
            model_secants_exhaustive=True,
            model_secants_provenance="finite two-codeword difference set",
        )
        self.assertTrue(report["exhaustive_model_secants_prove_task_irrelevance"])
        self.assertTrue(report["nominal_null_task_irrelevant"])

    def test_query_insensitivity_does_not_control_unbounded_operator_leakage(self) -> None:
        report = certify_combined_model_design(
            [[1, 0]],
            I2,
            [[1, 0], [0, 0]],
            [[1, 0]],
            [[[1], [0]]],
            response_radius=[[0, 1]],
            output_metric=[[1]],
            query_matrix=[[1, 0]],
        )
        self.assertTrue(
            report["nominal_null_relevance_certificate"][
                "kernel_is_subset_of_query_kernel"
            ]
        )
        self.assertIsNone(
            report["blind_uncertainty_certificate"]["blind_source_radius_exact"]
        )
        self.assertFalse(
            report["obligations"]["uncertain_blind_direction_rule_satisfied"]
        )
        self.assertFalse(report["combined_target_passed"])

    def test_bounded_operator_leakage_satisfies_only_the_leakage_obligation(self) -> None:
        report = certify_combined_model_design(
            [[1, 0]],
            I2,
            [[1, 0], [0, 0]],
            [[1, 0]],
            [[[1], [0]]],
            response_radius=[[0, "1/10"]],
            output_metric=[[1]],
            blind_source_radius=2,
            query_matrix=[[1, 0]],
        )
        blind = report["blind_uncertainty_certificate"]
        # sqrt(1/100)=1/10 is not dyadic, so the serialized directed upper is
        # slightly larger than the exact value and remains a valid enclosure.
        self.assertGreaterEqual(
            Q(blind["bounded_blind_leakage_radius_upper_exact"]), Q(1, 5)
        )
        self.assertTrue(
            report["obligations"]["uncertain_blind_direction_rule_satisfied"]
        )
        self.assertTrue(report["obligations"]["nominal_null_relevance_rule_satisfied"])
        self.assertTrue(report["combined_target_passed"])
        self.assertIn("partial", report["design_target"])
        self.assertIn("external", report["warning"])

    def test_zero_real_rank_cannot_be_integer_kernel_free(self) -> None:
        with self.assertRaisesRegex(ValueError, "integer collision"):
            classify_lattice_trichotomy_from_exact_predicates(
                lattice_rank=2,
                real_image_rank=0,
                integer_kernel_status="kernel_free_proved",
                proof_reference="contradictory premise",
            )

    def test_standalone_verifier_rejects_boolean_numeric_and_surplus_tampering(self) -> None:
        original = certify_quotient_tube_pair(
            [[1, 0]], I2, [3, 4], source_radius=1
        )
        self.assertTrue(verify_robust_model_report(original)["passed"])
        mutations = []

        changed_boolean = deepcopy(original)
        changed_boolean["response_tubes_overlap_exactly"] = True
        mutations.append(changed_boolean)

        changed_floor = deepcopy(original)
        changed_floor["quotient_distance_squared_exact"] = "0/1"
        mutations.append(changed_floor)

        integer_boolean = deepcopy(original)
        integer_boolean["response_tubes_overlap_exactly"] = 0
        mutations.append(integer_boolean)

        surplus_claim = deepcopy(original)
        surplus_claim["physical_model_validated"] = True
        mutations.append(surplus_claim)

        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                self.assertFalse(verify_robust_model_report(mutation)["passed"])

    def test_combined_report_survives_json_and_nested_tamper_is_rejected(self) -> None:
        original = certify_combined_model_design(
            [[1, 0]],
            I2,
            [[1, 0], [0, 0]],
            [[1, 1]],
            [[[1], [1]]],
            query_matrix=[[1, 0]],
        )
        round_trip = json.loads(json.dumps(original))
        self.assertTrue(verify_robust_model_report(round_trip)["passed"])
        tampered = deepcopy(round_trip)
        tampered["finite_secant_certificate"]["finite_family_is_quotient_separated"] = False
        self.assertFalse(verify_robust_model_report(tampered)["passed"])

    def test_external_proof_reference_is_a_declarative_trust_boundary(self) -> None:
        report = classify_lattice_trichotomy_from_exact_predicates(
            lattice_rank=2,
            real_image_rank=1,
            integer_kernel_status="kernel_free_proved",
            proof_reference="external irrational-independence lemma",
        )
        self.assertTrue(verify_robust_model_report(report)["passed"])
        replacement = deepcopy(report)
        replacement["external_exact_proof_reference"] = (
            "replacement assertion not authenticated by this finite verifier"
        )
        # Reconstruction checks logical use of the premise, not the truth or
        # authenticity of the externally cited Diophantine proof.
        self.assertTrue(verify_robust_model_report(replacement)["passed"])


if __name__ == "__main__":
    unittest.main()
