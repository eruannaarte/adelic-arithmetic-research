"""Adversarial tests for the model-aware robust quotient certificates."""

from __future__ import annotations

from fractions import Fraction
from copy import deepcopy
import json
import unittest

from oig_robust_model_quotient import (
    classify_lattice_trichotomy_from_exact_predicates,
    certify_combined_model_design,
    certify_finite_quotient_secants,
    certify_nominal_blind_uncertainty,
    certify_nominal_null_relevance,
    certify_quotient_tube_pair,
    certify_rational_lattice_trichotomy,
    certify_response_tube_pair,
    certify_tangent_kernel_angle,
    exact_model_quotient,
    quotient_distance_squared,
    verify_combined_model_design_report,
    verify_robust_model_report,
)
from oig_robust_model_quotient_demo import (
    run_demo,
    verify_robust_model_demo_report,
)


Q = Fraction
IDENTITY_2 = [[1, 0], [0, 1]]


class ExactQuotientTests(unittest.TestCase):
    def test_minimum_cost_distance_uses_declared_metric(self) -> None:
        quotient = exact_model_quotient([[1, 1]], [[1, 0], [0, 4]])
        self.assertEqual(quotient_distance_squared(quotient, [1, 0]), Q(4, 5))
        self.assertEqual(len(quotient.row_coordinates), 1)
        self.assertEqual(len(quotient.blind_basis[0]), 1)

    def test_binary_float_declarations_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            exact_model_quotient([[1.0, 0]], IDENTITY_2)
        with self.assertRaises(TypeError):
            certify_quotient_tube_pair(
                [[1, 0]], IDENTITY_2, [1, 0], source_radius=0.1
            )


class TubeCertificateTests(unittest.TestCase):
    def test_exact_quotient_gap(self) -> None:
        report = certify_quotient_tube_pair(
            [[1, 0]], IDENTITY_2, [3, 4], source_radius=1
        )
        self.assertFalse(report["response_tubes_overlap_exactly"])
        self.assertEqual(report["quotient_distance_squared_exact"], "9/1")
        self.assertEqual(report["quotient_gap_lower_exact"], "1/1")
        self.assertEqual(report["quotient_gap_upper_exact"], "1/1")

    def test_boundary_overlap_has_exact_source_witness(self) -> None:
        report = certify_quotient_tube_pair(
            [[1, 0]], IDENTITY_2, [3, 4], source_radius=Q(3, 2)
        )
        self.assertTrue(report["response_tubes_overlap_exactly"])
        witness = report["source_only_overlap_witness"]
        self.assertIsNotNone(witness)
        self.assertEqual(witness["left_source_error_exact"], ["-3/2", "0/1"])
        self.assertEqual(witness["right_source_error_exact"], ["3/2", "0/1"])

    def test_quotient_noise_erodes_twice_its_radius(self) -> None:
        report = certify_quotient_tube_pair(
            [[1, 0]],
            IDENTITY_2,
            [3, 4],
            source_radius=1,
            quotient_noise_radius=Q(1, 2),
        )
        self.assertEqual(report["erosion_exact"], "3/1")
        self.assertTrue(report["response_tubes_overlap_exactly"])

    def test_raw_tube_disjointness_is_sound_but_explicitly_conservative(self) -> None:
        report = certify_response_tube_pair(
            [[1, 0]],
            IDENTITY_2,
            [[1]],
            [5, 0],
            source_radius=1,
            data_noise_radius=1,
        )
        self.assertEqual(report["status"], "certified_disjoint")
        self.assertTrue(report["certified_disjoint"])
        self.assertFalse(report["certified_overlap"])

    def test_source_overlap_remains_overlap_with_ordinary_noise(self) -> None:
        report = certify_response_tube_pair(
            [[1, 0]],
            IDENTITY_2,
            [[1]],
            [1, 99],
            source_radius=Q(1, 2),
            data_noise_radius=0,
        )
        self.assertEqual(report["status"], "certified_overlap")
        self.assertTrue(report["source_only_overlap_exact"])

    def test_zero_data_noise_uses_exact_quotient_decision_not_gain_bound(self) -> None:
        report = certify_response_tube_pair(
            [[100, 0], [0, 1]],
            IDENTITY_2,
            IDENTITY_2,
            [0, 3],
            source_radius=1,
            data_noise_radius=0,
        )
        self.assertTrue(report["decision_is_exact"])
        self.assertEqual(report["status"], "certified_disjoint")


class SecantAndTangentTests(unittest.TestCase):
    def test_finite_secant_floor_and_loss(self) -> None:
        report = certify_finite_quotient_secants(
            [[1, 0]], IDENTITY_2, [[1, 1], [2, 0]], source_radius=Q(1, 4)
        )
        self.assertTrue(report["finite_family_is_quotient_separated"])
        self.assertEqual(report["minimum_quotient_ratio_squared_exact"], "1/2")
        self.assertEqual(report["minimum_eroded_gap_lower_exact"], "1/2")

    def test_coarse_sqrt_bound_never_makes_eroded_gap_negative(self) -> None:
        report = certify_finite_quotient_secants(
            [[1, 0]],
            IDENTITY_2,
            [[1, 1]],
            source_radius=Q(5, 8),
            sqrt_bits=1,
        )
        self.assertEqual(report["minimum_eroded_gap_lower_exact"], "0/1")

    def test_finite_secant_collision_is_not_hidden_by_quotient_floor(self) -> None:
        report = certify_finite_quotient_secants(
            [[1, 0]], IDENTITY_2, [[0, 1]]
        )
        self.assertFalse(report["finite_family_is_quotient_separated"])
        self.assertEqual(report["minimum_quotient_ratio_squared_exact"], "0/1")

    def test_one_dimensional_tangent_angle_is_exact(self) -> None:
        report = certify_tangent_kernel_angle(
            [[1, 0]], IDENTITY_2, [[3], [4]]
        )
        self.assertTrue(report["tangent_is_transverse_to_kernel"])
        self.assertEqual(report["mu_squared_lower_exact"], "9/25")
        self.assertEqual(report["mu_squared_upper_exact"], "9/25")
        self.assertGreaterEqual(Q(report["mismatch_amplification_upper_exact"]), Q(5, 3))

    def test_tangent_metric_is_not_silently_euclidean(self) -> None:
        report = certify_tangent_kernel_angle(
            [[1, 1]], [[1, 0], [0, 4]], [[1], [0]]
        )
        self.assertEqual(report["mu_squared_lower_exact"], "4/5")
        self.assertEqual(report["mu_squared_upper_exact"], "4/5")

    def test_tangent_kernel_intersection_has_exact_witness(self) -> None:
        report = certify_tangent_kernel_angle(
            [[1, 0]], IDENTITY_2, [[0], [1]]
        )
        self.assertFalse(report["tangent_is_transverse_to_kernel"])
        self.assertEqual(report["mu_squared_lower_exact"], "0/1")
        self.assertEqual(
            report["kernel_witness"]["ambient_tangent_kernel_vector_exact"],
            ["0/1", "1/1"],
        )


class BlindUncertaintyTests(unittest.TestCase):
    def test_zero_radius_columns_preserve_nominal_null(self) -> None:
        report = certify_nominal_blind_uncertainty(
            [[1, 0]], [[0, 0]], IDENTITY_2, [[1]]
        )
        self.assertTrue(report["box_preserves_nominal_blind_subspace"])
        self.assertTrue(report["quotient_family_stable"])
        self.assertFalse(report["nominal_null_task_irrelevant"])
        self.assertFalse(report["nominal_null_safe_to_ignore"])
        self.assertEqual(report["blind_leakage_gain_squared_upper_exact"], "0/1")

    def test_possible_activation_never_becomes_guaranteed_information(self) -> None:
        report = certify_nominal_blind_uncertainty(
            [[1, 0]], [[0, "1/10"]], IDENTITY_2, [[1]]
        )
        self.assertFalse(report["box_preserves_nominal_blind_subspace"])
        self.assertEqual(report["worst_case_blind_information_floor_exact"], "0/1")
        self.assertEqual(report["blind_leakage_gain_squared_upper_exact"], "1/100")
        self.assertFalse(report["nominal_null_safe_to_ignore"])

    def test_query_kernel_inclusion_makes_nominal_null_irrelevant(self) -> None:
        report = certify_nominal_null_relevance(
            [[1, 0]], IDENTITY_2, query_matrix=[[1, 0]]
        )
        self.assertTrue(report["kernel_is_subset_of_query_kernel"])
        self.assertTrue(report["nominal_null_safe_to_ignore"])

    def test_query_that_uses_blind_coordinate_fails_relevance_rule(self) -> None:
        report = certify_nominal_null_relevance(
            [[1, 0]],
            IDENTITY_2,
            query_matrix=[[0, 1]],
            model_secants=[[0, 1]],
            response_radius=[[0, "1/10"]],
        )
        self.assertFalse(report["kernel_is_subset_of_query_kernel"])
        self.assertFalse(report["declared_model_secants_exclude_kernel_collisions"])
        self.assertFalse(report["entire_response_box_preserves_nominal_null"])
        self.assertFalse(report["nominal_null_safe_to_ignore"])

    def test_nonexhaustive_visible_secant_cannot_hide_omitted_blind_collision(self) -> None:
        report = certify_nominal_null_relevance(
            [[1, 0]],
            IDENTITY_2,
            query_matrix=[[0, 1]],
            model_secants=[[1, 0]],
        )
        self.assertTrue(report["declared_model_secants_exclude_kernel_collisions"])
        self.assertFalse(report["model_secants_exhaustive"])
        self.assertFalse(report["exhaustive_model_secants_prove_task_irrelevance"])
        self.assertFalse(report["nominal_null_task_irrelevant"])

    def test_family_preservation_does_not_make_blind_query_recoverable(self) -> None:
        report = certify_nominal_null_relevance(
            [[1, 0]],
            IDENTITY_2,
            query_matrix=[[0, 1]],
            response_radius=[[0, 0]],
        )
        self.assertTrue(report["quotient_family_stable"])
        self.assertFalse(report["kernel_is_subset_of_query_kernel"])
        self.assertFalse(report["nominal_null_task_irrelevant"])

    def test_exhaustive_secants_require_provenance(self) -> None:
        with self.assertRaises(ValueError):
            certify_nominal_null_relevance(
                [[1, 0]],
                IDENTITY_2,
                model_secants=[[1, 0]],
                model_secants_exhaustive=True,
            )

    def test_bounded_blind_amplitude_becomes_output_uncertainty(self) -> None:
        report = certify_nominal_blind_uncertainty(
            [[1, 0]],
            [[0, "1/10"]],
            IDENTITY_2,
            [[1]],
            blind_source_radius=2,
        )
        self.assertIsNotNone(report["bounded_blind_leakage_radius_upper_exact"])
        self.assertGreaterEqual(
            Q(report["bounded_blind_leakage_radius_upper_exact"]), Q(1, 5)
        )


class CombinedTargetAndLatticeTests(unittest.TestCase):
    def test_positive_e_optimal_quotient_floor_can_hide_model_collision(self) -> None:
        report = certify_combined_model_design(
            [[1, 0]],
            IDENTITY_2,
            [[1, 0], [0, 0]],
            [[0, 1]],
            [[[1], [0]]],
        )
        self.assertEqual(report["quotient_information_floor_lower_exact"], "1/1")
        self.assertFalse(report["combined_target_passed"])
        self.assertFalse(report["obligations"]["declared_finite_secants_avoid_kernel"])

    def test_combined_target_passes_declared_finite_model(self) -> None:
        report = certify_combined_model_design(
            [[1, 0]],
            IDENTITY_2,
            [[1, 0], [0, 0]],
            [[1, 1]],
            [[[1], [1]]],
            model_secants_exhaustive=True,
            model_secants_provenance="declared two-point test model",
        )
        self.assertTrue(report["combined_target_passed"])

    def test_query_insensitivity_does_not_control_unbounded_uncertain_blind_leakage(self) -> None:
        report = certify_combined_model_design(
            [[1, 0]],
            IDENTITY_2,
            [[1, 0], [0, 0]],
            [[1, 0]],
            [[[1], [0]]],
            response_radius=[[0, "1/10"]],
            output_metric=[[1]],
            query_matrix=[[1, 0]],
        )
        self.assertTrue(report["obligations"]["nominal_null_relevance_rule_satisfied"])
        self.assertFalse(report["obligations"]["uncertain_blind_direction_rule_satisfied"])
        self.assertFalse(report["combined_target_passed"])

    def test_rational_rank_deficiency_produces_integer_collision(self) -> None:
        report = certify_rational_lattice_trichotomy(
            [[1, 0]], IDENTITY_2, [[1]]
        )
        self.assertEqual(report["regime"], "exact_integer_collision")
        witness = report["integer_kernel_witness"]
        self.assertNotEqual(witness, [0, 0])
        self.assertEqual(witness[0], 0)

    def test_full_rank_rational_lattice_has_positive_separation(self) -> None:
        report = certify_rational_lattice_trichotomy(
            IDENTITY_2, [[1, 0], [0, 2]], IDENTITY_2
        )
        self.assertEqual(report["regime"], "stable_lattice_observability")
        self.assertGreater(Q(report["uniform_separation_lower_exact"]), 0)

    def test_external_exact_predicate_can_select_middle_lattice_regime(self) -> None:
        report = classify_lattice_trichotomy_from_exact_predicates(
            lattice_rank=2,
            real_image_rank=1,
            integer_kernel_status="kernel_free_proved",
            proof_reference="declared irrational-independence lemma",
        )
        self.assertEqual(
            report["regime"], "exact_injective_but_zero_uniform_separation"
        )

    def test_zero_real_rank_cannot_be_declared_integer_kernel_free(self) -> None:
        with self.assertRaises(ValueError):
            classify_lattice_trichotomy_from_exact_predicates(
                lattice_rank=2,
                real_image_rank=0,
                integer_kernel_status="kernel_free_proved",
                proof_reference="impossible premise",
            )


class SerializedVerifierTests(unittest.TestCase):
    def test_huge_positive_information_uses_exact_lower_form_fallback(self) -> None:
        huge = str(10**400)
        report = certify_combined_model_design(
            IDENTITY_2,
            IDENTITY_2,
            [[huge, 0], [0, huge]],
            [[1, 0]],
            [IDENTITY_2],
        )
        self.assertGreater(Q(report["quotient_information_floor_lower_exact"]), 0)
        self.assertTrue(report["combined_target_passed"])
        self.assertTrue(verify_combined_model_design_report(report)["passed"])

    def test_every_standalone_schema_reconstructs(self) -> None:
        reports = [
            certify_response_tube_pair(
                [[1, 0]], IDENTITY_2, [[1]], [3, 4], source_radius=1, data_noise_radius=1
            ),
            certify_nominal_blind_uncertainty(
                [[1, 0]], [[0, "1/10"]], IDENTITY_2, [[1]], blind_source_radius=2
            ),
            certify_nominal_null_relevance(
                [[1, 0]], IDENTITY_2, query_matrix=[[1, 0]]
            ),
            certify_rational_lattice_trichotomy(
                IDENTITY_2, IDENTITY_2, IDENTITY_2
            ),
            classify_lattice_trichotomy_from_exact_predicates(
                lattice_rank=2,
                real_image_rank=1,
                integer_kernel_status="kernel_free_proved",
                proof_reference="exact schema-dispatch test premise",
            ),
        ]
        for report in reports:
            with self.subTest(schema=report["schema_version"]):
                self.assertTrue(verify_robust_model_report(report)["passed"])

    def test_pair_report_survives_json_round_trip_and_verifies(self) -> None:
        report = certify_quotient_tube_pair(
            [[1, 0]], IDENTITY_2, [3, 4], source_radius=1
        )
        serialized = json.loads(json.dumps(report))
        self.assertTrue(verify_robust_model_report(serialized)["passed"])

    def test_pair_theorem_tampering_is_rejected(self) -> None:
        report = certify_quotient_tube_pair(
            [[1, 0]], IDENTITY_2, [3, 4], source_radius=1
        )
        report["quotient_gap_lower_exact"] = "0/1"
        self.assertFalse(verify_robust_model_report(report)["passed"])

    def test_declaration_tampering_without_recomputed_fields_is_rejected(self) -> None:
        report = certify_tangent_kernel_angle(
            [[1, 0]], IDENTITY_2, [[3], [4]]
        )
        report["tangent_basis_exact"][0][0] = "4/1"
        self.assertFalse(verify_robust_model_report(report)["passed"])

    def test_schema_extra_field_and_bool_as_integer_are_rejected(self) -> None:
        report = certify_finite_quotient_secants(
            [[1, 0]], IDENTITY_2, [[1, 1]]
        )
        extra = deepcopy(report)
        extra["unverified"] = True
        self.assertFalse(verify_robust_model_report(extra)["passed"])
        wrong_type = deepcopy(report)
        wrong_type["sqrt_bits"] = True
        self.assertFalse(verify_robust_model_report(wrong_type)["passed"])

    def test_combined_report_has_strict_standalone_verifier(self) -> None:
        report = certify_combined_model_design(
            [[1, 0]],
            IDENTITY_2,
            [[1, 0], [0, 0]],
            [[1, 1]],
            [[[1], [1]]],
            model_secants_exhaustive=True,
            model_secants_provenance="declared two-point verifier model",
        )
        self.assertTrue(verify_combined_model_design_report(report)["passed"])
        report["obligations"]["declared_tangents_avoid_kernel"] = False
        self.assertFalse(verify_combined_model_design_report(report)["passed"])

    def test_demo_self_verifies_after_json_round_trip(self) -> None:
        report = json.loads(json.dumps(run_demo()))
        self.assertTrue(verify_robust_model_demo_report(report)["passed"])

    def test_demo_rejects_embedded_verification_tampering(self) -> None:
        report = run_demo()
        report["independent_verification"]["passed"] = False
        self.assertFalse(verify_robust_model_demo_report(report)["passed"])

    def test_demo_rejects_individually_valid_but_incoherent_component(self) -> None:
        report = run_demo()
        report["pair_quotient_tube"] = certify_quotient_tube_pair(
            [[1, 0, 0], [0, 0, 1]],
            [[1, 0, 0], [0, 4, 0], [0, 0, 9]],
            [3, 4, 5],
            source_radius=1,
            quotient_noise_radius="1/2",
        )
        self.assertTrue(
            verify_robust_model_report(report["pair_quotient_tube"])["passed"]
        )
        self.assertFalse(verify_robust_model_demo_report(report)["passed"])


if __name__ == "__main__":
    unittest.main()
