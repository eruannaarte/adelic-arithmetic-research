"""Focused tests for the two-protocol structured physical-nuisance lane."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest

from oig_double_pendulum_structured_nuisance import (
    ACTIVE_NAMES,
    PROOF_BOUNDARY,
    SOURCE_RESPONSE_CENTRE,
    build_structured_physical_nuisance_report,
    main,
    verify_structured_physical_nuisance_report,
)
from oig_query_protocol_design import verify_query_protocol_report
from oig_structured_nuisance import verify_structured_nuisance_report
from oig_numerical_replay import numerically_equivalent_json


Q = Fraction


class DoublePendulumStructuredPhysicalNuisanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_structured_physical_nuisance_report()

    def test_two_active_protocols_and_analytic_columns_are_pinned(self) -> None:
        report = self.report
        self.assertEqual(
            tuple(protocol["name"] for protocol in report["protocols"]),
            ACTIVE_NAMES,
        )
        self.assertTrue(report["all_tier1_controls_passed"])
        self.assertEqual(report["proof_boundary"], PROOF_BOUNDARY)
        self.assertFalse(report["outward_ode_nuisance_validation_claimed"])
        for protocol in report["protocols"]:
            fine = protocol["fine"]
            tau = float(Q(protocol["observation_time_tau_exact"]))
            sensor_index = 1 if protocol["sensor"] == "theta_2" else 2
            self.assertEqual(
                fine["clock_log_dilation_column_entry"],
                tau * fine["terminal_rhs_dz_dtau"][sensor_index],
            )
            self.assertEqual(
                fine["common_log_gain_column_entry"],
                fine["sensor_output"],
            )
            self.assertEqual(
                fine["initial_angle_preparation_row"],
                fine["terminal_initial_state_tangent"][sensor_index][:2],
            )
            self.assertTrue(any(fine["initial_angle_preparation_row"]))

    def test_exact_rank_obstruction_and_surviving_one_dimensional_queries(self) -> None:
        exact = self.report["conditional_exact_analysis"]
        conclusions = exact["rank_and_floor_conclusions"]
        self.assertEqual(conclusions["nominal_effective_rank"], 2)
        self.assertEqual(conclusions["shared_clock_effective_rank"], 1)
        self.assertFalse(conclusions["shared_clock_full_two_source_floor_positive"])
        self.assertTrue(conclusions["shared_clock_one_dimensional_query_survives"])
        self.assertEqual(conclusions["shared_common_gain_effective_rank"], 1)
        self.assertEqual(conclusions["clock_and_common_gain_effective_rank"], 0)
        self.assertEqual(conclusions["independent_preparation_effective_rank"], 0)
        self.assertEqual(conclusions["sensor_specific_gain_effective_rank"], 0)

        children = exact["query_engine_children"]
        self.assertTrue(children["nominal_full_source"]["identifiability"]["query_identifiable_exact"])
        self.assertFalse(children["shared_clock_full_source"]["identifiability"]["query_identifiable_exact"])
        self.assertTrue(children["shared_clock_surviving_query"]["identifiability"]["query_identifiable_exact"])
        self.assertFalse(children["shared_clock_and_common_gain_full_source"]["identifiability"]["query_identifiable_exact"])
        self.assertFalse(children["independent_angle_preparation_full_source"]["identifiability"]["query_identifiable_exact"])

    def test_declared_clock_and_gain_are_exactly_confounded_source_combinations(self) -> None:
        exact = self.report["conditional_exact_analysis"]
        columns = exact["declared_columns_exact"]
        confoundings = exact["exact_confoundings"]
        for column_field, source_field in (
            ("shared_clock_log_dilation", "clock_lost_source_direction_H_inverse_b"),
            ("shared_common_log_gain", "gain_lost_source_direction_H_inverse_b"),
        ):
            column = tuple(Q(value) for value in columns[column_field])
            source = tuple(Q(value) for value in confoundings[source_field])
            recovered = tuple(
                sum(SOURCE_RESPONSE_CENTRE[row][coordinate] * source[coordinate] for coordinate in range(2))
                for row in range(2)
            )
            self.assertEqual(recovered, column)

    def test_all_exact_children_verify_and_separation_controls_have_expected_sign(self) -> None:
        exact = self.report["conditional_exact_analysis"]
        for name, child in exact["query_engine_children"].items():
            with self.subTest(kind="query", name=name):
                self.assertTrue(verify_query_protocol_report(child)["passed"])
        structured = exact["structured_nuisance_children"]
        for name, child in structured.items():
            with self.subTest(kind="structured", name=name):
                self.assertTrue(verify_structured_nuisance_report(child)["passed"])
        self.assertGreater(
            Q(structured["shared_clock_survivor"]["exact_calculation"]["distance_squared_lower_exact"]),
            0,
        )
        for name in (
            "shared_clock_exact_confounding",
            "clock_and_gain_span_all_outputs",
            "independent_preparation_span_all_outputs",
        ):
            self.assertEqual(
                structured[name]["exact_calculation"]["distance_squared_upper_exact"],
                "0/1",
            )

    def test_strict_verifier_round_trip_and_tamper_rejection(self) -> None:
        round_trip = json.loads(json.dumps(self.report))
        self.assertTrue(verify_structured_physical_nuisance_report(round_trip)["passed"])

        mutations = []
        outward = deepcopy(round_trip)
        outward["outward_ode_nuisance_validation_claimed"] = True
        mutations.append(outward)

        clock = deepcopy(round_trip)
        clock["protocols"][0]["fine"]["clock_log_dilation_column_entry"] += 0.1
        mutations.append(clock)

        rational = deepcopy(round_trip)
        rational["protocols"][0]["declared_rational_point_columns"][
            "shared_clock_log_dilation_exact"
        ] = "1/1"
        mutations.append(rational)

        child = deepcopy(round_trip)
        child["conditional_exact_analysis"]["query_engine_children"][
            "shared_clock_full_source"
        ]["effective_response_rank"] = 2
        mutations.append(child)

        numeric_bool = deepcopy(round_trip)
        numeric_bool["protocols"][0]["fine"]["terminal_state"][0] = True
        mutations.append(numeric_bool)

        theorem = deepcopy(round_trip)
        theorem["theorem"]["present_two_scalar_protocols_sufficient_for_full_source_with_nuisance"] = True
        mutations.append(theorem)

        extra_root_claim = deepcopy(round_trip)
        extra_root_claim["forged_extra_claim"] = "outwardly validated exact ODE columns"
        mutations.append(extra_root_claim)

        extra_protocol_claim = deepcopy(round_trip)
        extra_protocol_claim["protocols"][0]["forged_extra_claim"] = "exact physical column"
        mutations.append(extra_protocol_claim)

        for index, tampered in enumerate(mutations):
            with self.subTest(index=index):
                self.assertFalse(
                    verify_structured_physical_nuisance_report(tampered)["passed"]
                )

    def test_cli_output_and_no_replay_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nuisance.json"
            self.assertEqual(main(["--output", str(path)]), 0)
            self.assertTrue(path.is_file())
            self.assertEqual(main(["--verify", str(path)]), 0)
            report = json.loads(path.read_text(encoding="utf-8"))
            verification = verify_structured_physical_nuisance_report(report)
            self.assertTrue(verification["passed"])
            self.assertFalse(verification["ode_or_variational_system_replayed"])
            self.assertFalse(verification["outward_ode_nuisance_validation_verified"])

    def test_committed_canonical_artifact_is_fresh_and_strictly_verifies(self) -> None:
        path = (
            Path(__file__).resolve().parent
            / "artifacts"
            / "double_pendulum_structured_physical_nuisance.json"
        )
        committed = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(verify_structured_physical_nuisance_report(committed)["passed"])
        self.assertTrue(numerically_equivalent_json(committed, self.report))


if __name__ == "__main__":
    unittest.main()
