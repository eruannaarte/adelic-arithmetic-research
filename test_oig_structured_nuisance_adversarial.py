"""Independent adversarial controls for the structured-nuisance lane.

This file was written independently of ``test_oig_structured_nuisance.py``.
It targets certificate semantics and covariance properties which are easy to
miss when the builder and verifier share one reconstruction routine.
"""

from copy import deepcopy
from fractions import Fraction
import unittest

from oig_structured_nuisance import (
    certify_structured_nuisance_separation,
    demo_certificates,
    verify_structured_nuisance_report,
)


Q = Fraction


def _fraction(value: object) -> Fraction:
    if not isinstance(value, str):
        raise AssertionError("certificate endpoint is not an exact string")
    return Q(value)


class StructuredNuisanceAdversarialTests(unittest.TestCase):
    def test_directional_only_tail_is_not_silently_overridden_by_zero(self) -> None:
        """The advertised either/or tail interface must really support either.

        The full one-dimensional nuisance tail may be ``[-1/2,1/2]``.  Its
        distance from q=1 is 1/2, not 1.  Omitting a norm remainder therefore
        must not manufacture the stronger premise R=0 before taking a minimum.
        """
        report = certify_structured_nuisance_separation(
            name="directional-only remote support",
            query_response=[1],
            generators=[[0]],
            coefficient_radii=[0],
            primal_coefficients=[0],
            dual_direction=[1],
            tail_directional_support_upper="1/2",
            tail_provenance="declared exact support of the omitted interval",
        )
        tail = report["tail_remainder"]
        calculation = report["exact_calculation"]
        self.assertIsNone(tail["declared_norm_remainder_upper_exact"])
        self.assertEqual(
            tail["effective_directional_support_upper_exact"], "1/2"
        )
        self.assertEqual(calculation["distance_squared_lower_exact"], "1/4")
        self.assertEqual(calculation["distance_squared_upper_exact"], "1/1")
        self.assertIs(calculation["exact_optimum_certified"], False)
        self.assertTrue(verify_structured_nuisance_report(report)["passed"])

    def test_overscaled_dual_still_closes_the_scale_invariant_bracket(self) -> None:
        """Endpoint flags must follow the strongest serialized lower bound.

        For q=1 and Z={0}, u=3 is not normalized for the half-squared dual,
        but weighted Cauchy--Schwarz is sharp and proves d^2=1 exactly.
        """
        report = certify_structured_nuisance_separation(
            name="overscaled but sharp norm-dual witness",
            query_response=[1],
            generators=[[0]],
            coefficient_radii=[0],
            primal_coefficients=[0],
            dual_direction=[3],
        )
        calculation = report["exact_calculation"]
        self.assertEqual(calculation["distance_squared_lower_exact"], "1/1")
        self.assertEqual(calculation["distance_squared_upper_exact"], "1/1")
        self.assertLess(
            _fraction(calculation["dual_half_squared_lower_raw_exact"]), Q(0)
        )
        self.assertIs(calculation["positive_separation_certified"], True)
        self.assertIs(calculation["exact_optimum_certified"], True)

    def test_off_diagonal_metric_gap_identity_is_exact(self) -> None:
        # Omega=[[2,1],[1,2]], residual=(1,2), and u=Omega residual=(4,5).
        # The selected box corner is exposed by u, so both KKT terms vanish.
        report = certify_structured_nuisance_separation(
            name="off-diagonal metric KKT control",
            query_response=[0, 4],
            generators=[[1, 1], [0, -1]],
            coefficient_radii=[1, 2],
            primal_coefficients=[1, -2],
            dual_direction=[4, 5],
            observation_precision=[[2, 1], [1, 2]],
        )
        calculation = report["exact_calculation"]
        self.assertEqual(calculation["distance_squared_lower_exact"], "14/1")
        self.assertEqual(calculation["distance_squared_upper_exact"], "14/1")
        self.assertEqual(calculation["primal_dual_gap_upper_exact"], "0/1")
        self.assertEqual(
            calculation["residual_dual_mismatch_half_squared_exact"], "0/1"
        )
        self.assertEqual(calculation["finite_support_slack_exact"], "0/1")

    def test_coordinate_recalibration_preserves_metric_certificate(self) -> None:
        """Check y'=S y, Omega'=S^-T Omega S^-1, u'=S^-T u."""
        original = certify_structured_nuisance_separation(
            name="original calibrated quotient",
            query_response=[-10, 12],
            generators=[[1, 1], [0, -1]],
            coefficient_radii=[1, 2],
            primal_coefficients=[1, -2],
            dual_direction=[4, 5],
            nuisance_basis=[[5], [-4]],
            primal_nuisance_coefficients=[2],
            observation_precision=[[2, 1], [1, 2]],
        )
        # S=diag(2,3).  All transformed data are written explicitly so this
        # audit does not rely on any matrix helper from the implementation.
        transformed = certify_structured_nuisance_separation(
            name="recalibrated quotient",
            query_response=[-20, 36],
            generators=[[2, 2], [0, -3]],
            coefficient_radii=[1, 2],
            primal_coefficients=[1, -2],
            dual_direction=[2, "5/3"],
            nuisance_basis=[[10], [-12]],
            primal_nuisance_coefficients=[2],
            observation_precision=[["1/2", "1/6"], ["1/6", "2/9"]],
        )
        for field in (
            "distance_squared_lower_exact",
            "distance_squared_upper_exact",
            "critical_equal_noise_radius_squared_lower_exact",
            "primal_dual_gap_upper_exact",
        ):
            self.assertEqual(
                original["exact_calculation"][field],
                transformed["exact_calculation"][field],
            )
        self.assertEqual(
            transformed["exact_calculation"]["dual_nuisance_orthogonality_exact"],
            ["0/1"],
        )

    def test_serialized_tail_consequences_cannot_be_tampered(self) -> None:
        original = demo_certificates()["countable_tail_interface_certificate"]
        paths_and_values = (
            (("tail_remainder", "effective_directional_support_upper_exact"), "0/1"),
            (("tail_remainder", "l1_derived_directional_support_upper_exact"), "0/1"),
            (("tail_remainder", "external_analytic_assumption"), False),
            (("exact_calculation", "critical_equal_noise_radius_squared_lower_exact"), "999/1"),
            (("scope_boundary",), "all uncertainty is certified"),
        )
        for path, value in paths_and_values:
            mutation = deepcopy(original)
            cursor = mutation
            for key in path[:-1]:
                cursor = cursor[key]
            cursor[path[-1]] = value
            with self.subTest(path=path):
                self.assertFalse(verify_structured_nuisance_report(mutation)["passed"])

    def test_provenance_is_declarative_and_not_authenticated(self) -> None:
        """Changing only prose changes a premise, not checked mathematics.

        This passing control documents the verifier's deliberate trust
        boundary: it reconstructs use of a tail bound but cannot authenticate
        the cited proof or establish that the bound is true.
        """
        report = demo_certificates()["countable_tail_interface_certificate"]
        mutation = deepcopy(report)
        mutation["tail_remainder"]["provenance"] = (
            "unauthenticated replacement provenance; mathematical truth unchecked"
        )
        self.assertTrue(verify_structured_nuisance_report(mutation)["passed"])

    def test_zero_dual_cannot_create_a_positive_certificate(self) -> None:
        report = certify_structured_nuisance_separation(
            name="zero dual negative control",
            query_response=[7, -4],
            generators=[[0], [0]],
            coefficient_radii=[0],
            primal_coefficients=[0],
            dual_direction=[0, 0],
            observation_precision=[[3, 1], [1, 2]],
        )
        calculation = report["exact_calculation"]
        self.assertEqual(calculation["distance_squared_lower_exact"], "0/1")
        self.assertIs(calculation["positive_separation_certified"], False)
        self.assertIs(calculation["exact_optimum_certified"], False)


if __name__ == "__main__":
    unittest.main()
