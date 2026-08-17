from copy import deepcopy
from fractions import Fraction
import json
import unittest

from oig_structured_nuisance import (
    certify_structured_nuisance_separation,
    demo_certificates,
    entrywise_box_support_upper,
    finite_zonotope_support,
    verify_structured_nuisance_demo_report,
    verify_structured_nuisance_report,
)


Q = Fraction


class StructuredNuisanceTests(unittest.TestCase):
    def test_finite_zonotope_support_and_attainment_are_exact(self) -> None:
        support = finite_zonotope_support(
            [[1, 2, -1], [2, -1, 3]],
            [2, "1/3", "5/2"],
            [3, -2],
        )
        pairings = [Q(value) for value in support["direction_generator_pairings_exact"]]
        radii = (Q(2), Q(1, 3), Q(5, 2))
        expected = sum(
            (radius * abs(pairing) for radius, pairing in zip(radii, pairings)),
            Q(0),
        )
        self.assertEqual(Q(support["finite_support_exact"]), expected)
        exposed = [Q(value) for value in support["exposed_point_exact"]]
        self.assertEqual(3 * exposed[0] - 2 * exposed[1], expected)
        self.assertIs(support["attainment_verified_exactly"], True)

    def test_weighted_point_primal_dual_gap_closes_exactly(self) -> None:
        report = certify_structured_nuisance_separation(
            name="weighted exact projection",
            query_response=[3, 1],
            generators=[[1, 0], [0, 1]],
            coefficient_radii=[1, "1/2"],
            primal_coefficients=[1, "1/2"],
            dual_direction=[4, "3/2"],
            observation_precision=[[2, 0], [0, 3]],
        )
        calculation = report["exact_calculation"]
        self.assertEqual(calculation["distance_squared_lower_exact"], "35/4")
        self.assertEqual(calculation["distance_squared_upper_exact"], "35/4")
        self.assertEqual(calculation["primal_dual_gap_upper_exact"], "0/1")
        self.assertIs(calculation["exact_optimum_certified"], True)
        self.assertTrue(verify_structured_nuisance_report(report)["passed"])

    def test_query_response_profiles_additive_subspace(self) -> None:
        report = demo_certificates()["query_response_certificate"]
        calculation = report["exact_calculation"]
        self.assertEqual(report["certificate_kind"], "query-response quotient")
        self.assertEqual(calculation["dual_nuisance_orthogonality_exact"], ["0/1"])
        self.assertEqual(calculation["distance_squared_lower_exact"], "1/1")
        self.assertEqual(calculation["distance_squared_upper_exact"], "1/1")
        self.assertTrue(verify_structured_nuisance_report(report)["passed"])

    def test_countable_tail_interface_charges_directional_remainder(self) -> None:
        report = demo_certificates()["countable_tail_interface_certificate"]
        tail = report["tail_remainder"]
        calculation = report["exact_calculation"]
        self.assertEqual(tail["l1_derived_directional_support_upper_exact"], "1/10")
        self.assertEqual(tail["effective_directional_support_upper_exact"], "1/20")
        self.assertIs(tail["external_analytic_assumption"], True)
        self.assertEqual(calculation["dual_linear_separation_numerator_exact"], "39/20")
        self.assertLess(
            Q(calculation["distance_squared_lower_exact"]),
            Q(calculation["distance_squared_upper_exact"]),
        )
        self.assertTrue(verify_structured_nuisance_report(report)["passed"])

    def test_norm_remainder_alone_produces_rational_l1_support_bound(self) -> None:
        report = certify_structured_nuisance_separation(
            name="coarse countable tail",
            query_response=[3, 2],
            generators=[[1], [0]],
            coefficient_radii=[1],
            primal_coefficients=[1],
            dual_direction=["1/2", "-3/2"],
            tail_norm_remainder_upper="1/7",
            tail_provenance="proved absolute norm sum for omitted generators",
        )
        tail = report["tail_remainder"]
        self.assertEqual(tail["l1_derived_directional_support_upper_exact"], "2/7")
        self.assertEqual(tail["effective_directional_support_upper_exact"], "2/7")
        self.assertTrue(verify_structured_nuisance_report(report)["passed"])

    def test_directional_tail_premise_does_not_inherit_a_fake_zero_norm_bound(self) -> None:
        report = certify_structured_nuisance_separation(
            name="directional-only countable tail",
            query_response=[1],
            generators=[[0]],
            coefficient_radii=[0],
            primal_coefficients=[0],
            dual_direction=[1],
            tail_directional_support_upper="1/2",
            tail_provenance="proved support bound in the serialized direction",
        )
        tail = report["tail_remainder"]
        calculation = report["exact_calculation"]
        self.assertIsNone(tail["declared_norm_remainder_upper_exact"])
        self.assertIsNone(tail["l1_derived_directional_support_upper_exact"])
        self.assertEqual(tail["effective_directional_support_upper_exact"], "1/2")
        self.assertEqual(calculation["distance_squared_lower_exact"], "1/4")
        self.assertTrue(verify_structured_nuisance_report(report)["passed"])

    def test_scale_invariant_norm_dual_can_close_when_squared_dual_does_not(self) -> None:
        report = certify_structured_nuisance_separation(
            name="overscaled norm-dual witness",
            query_response=[1],
            generators=[[0]],
            coefficient_radii=[0],
            primal_coefficients=[0],
            dual_direction=[3],
        )
        calculation = report["exact_calculation"]
        self.assertEqual(calculation["distance_squared_lower_exact"], "1/1")
        self.assertEqual(calculation["distance_squared_upper_exact"], "1/1")
        self.assertIs(calculation["positive_separation_certified"], True)
        self.assertIs(calculation["exact_optimum_certified"], True)
        self.assertIs(calculation["squared_dual_gap_closes_exactly"], False)
        self.assertTrue(verify_structured_nuisance_report(report)["passed"])

    def test_shared_generator_correlation_can_be_lost_by_entrywise_box(self) -> None:
        control = entrywise_box_support_upper([[1], [1]], [1], [1, -1])
        self.assertEqual(control["finite_zonotope_support_exact"], "0/1")
        self.assertEqual(control["entrywise_box_support_upper_exact"], "2/1")
        self.assertEqual(control["correlation_loss_exact"], "2/1")

    def test_tampering_is_rejected(self) -> None:
        original = demo_certificates()["point_certificate"]
        mutations = []
        changed_floor = deepcopy(original)
        changed_floor["exact_calculation"]["distance_squared_lower_exact"] = "99/1"
        mutations.append(changed_floor)
        changed_support = deepcopy(original)
        changed_support["finite_zonotope_support_certificate"][
            "finite_support_exact"
        ] = "0/1"
        mutations.append(changed_support)
        changed_precision = deepcopy(original)
        changed_precision["problem"]["observation_noise_precision_exact"][0][0] = "2/1"
        mutations.append(changed_precision)
        changed_flag = deepcopy(original)
        changed_flag["exact_calculation"]["exact_optimum_certified"] = False
        mutations.append(changed_flag)
        integer_flag = deepcopy(original)
        integer_flag["exact_calculation"]["exact_optimum_certified"] = 1
        mutations.append(integer_flag)
        changed_verification = deepcopy(original)
        changed_verification["independent_verification"]["passed"] = False
        mutations.append(changed_verification)
        noncanonical = deepcopy(original)
        noncanonical["problem"]["query_response_exact"][0] = "6/2"
        mutations.append(noncanonical)
        for mutation in mutations:
            self.assertFalse(verify_structured_nuisance_report(mutation)["passed"])

    def test_json_round_trip_remains_independently_verifiable(self) -> None:
        demo = demo_certificates()
        round_trip = json.loads(json.dumps(demo))
        self.assertTrue(verify_structured_nuisance_demo_report(round_trip)["passed"])
        self.assertTrue(
            verify_structured_nuisance_report(round_trip["point_certificate"])[
                "passed"
            ]
        )
        tampered = deepcopy(round_trip)
        tampered["correlation_control"]["correlation_loss_exact"] = "0/1"
        self.assertFalse(verify_structured_nuisance_demo_report(tampered)["passed"])

    def test_infeasible_inputs_are_rejected(self) -> None:
        base = dict(
            name="invalid",
            query_response=[2, 1],
            generators=[[1], [0]],
            coefficient_radii=[1],
            primal_coefficients=[1],
            dual_direction=[0, 1],
        )
        with self.assertRaisesRegex(ValueError, "not exactly orthogonal"):
            certify_structured_nuisance_separation(
                **base,
                nuisance_basis=[[0], [1]],
                primal_nuisance_coefficients=[0],
            )
        outside = dict(base)
        outside["primal_coefficients"] = [2]
        with self.assertRaisesRegex(ValueError, "violate"):
            certify_structured_nuisance_separation(**outside)
        with self.assertRaisesRegex(ValueError, "positive definite"):
            certify_structured_nuisance_separation(
                **base, observation_precision=[[1, 0], [0, 0]]
            )
        with self.assertRaisesRegex(ValueError, "linearly independent"):
            certify_structured_nuisance_separation(
                **base,
                nuisance_basis=[[1, 2], [0, 0]],
                primal_nuisance_coefficients=[0, 0],
            )
        binary = dict(base)
        binary["query_response"] = [2.0, 1]
        with self.assertRaisesRegex(TypeError, "binary floating"):
            certify_structured_nuisance_separation(**binary)
        boolean = dict(base)
        boolean["query_response"] = [True, 1]
        with self.assertRaisesRegex(TypeError, "Boolean"):
            certify_structured_nuisance_separation(**boolean)

    def test_scope_excludes_response_operator_uncertainty(self) -> None:
        report = demo_certificates()["point_certificate"]
        scope = report["scope_boundary"]
        self.assertIn("fixed exactly", scope)
        self.assertIn("does not cover uncertainty in any response matrix", scope)
        self.assertNotIn("R^T W R is robust", scope)


if __name__ == "__main__":
    unittest.main()
