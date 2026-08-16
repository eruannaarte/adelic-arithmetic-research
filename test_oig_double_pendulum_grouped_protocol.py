"""Focused tests for the grouped double-pendulum protocol milestone."""

from __future__ import annotations

from contextlib import redirect_stdout
from copy import deepcopy
from fractions import Fraction
import io
import json
from pathlib import Path
import tempfile
import unittest

from oig_double_pendulum_grouped_protocol import (
    GROUP_DEFINITIONS,
    PROOF_BOUNDARY,
    build_grouped_protocol_report,
    main,
    verify_grouped_protocol_report,
)
from oig_query_protocol_design import verify_query_protocol_report


Q = Fraction


class DoublePendulumGroupedProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_grouped_protocol_report()

    def test_existing_seven_candidates_are_grouped_by_exact_launch(self) -> None:
        report = self.report
        self.assertEqual(len(report["scalar_observation_library"]), 7)
        groups = report["grouped_protocol_library"]
        self.assertEqual(len(groups), 3)
        self.assertEqual(
            tuple((group["name"], tuple(group["member_names"])) for group in groups),
            GROUP_DEFINITIONS,
        )
        self.assertEqual([group["output_count"] for group in groups], [3, 2, 2])
        self.assertTrue(all(group["is_multi_sensor"] for group in groups))
        self.assertTrue(all(group["is_multi_time"] for group in groups))
        self.assertEqual(
            [group["group_cost_exact"] for group in groups],
            ["7/2", "9/4", "5/2"],
        )
        self.assertTrue(report["all_tier1_controls_passed"])

    def test_serialized_state_parameter_and_clock_rows_reconstruct(self) -> None:
        for observation in self.report["scalar_observation_library"]:
            fine = observation["fine"]
            index = observation["sensor_state_index"]
            tau = float(Q(observation["observation_time_tau_exact"]))
            self.assertEqual(
                fine["selected_sensor_output"],
                fine["terminal_state"][index],
            )
            self.assertEqual(
                fine["selected_parameter_response_row"],
                fine["terminal_parameter_sensitivity_D_state_D_uv"][index],
            )
            self.assertEqual(
                fine["selected_clock_response"],
                fine["clock_log_dilation_state_response_tau_times_rhs"][index],
            )
            self.assertEqual(
                fine["clock_log_dilation_state_response_tau_times_rhs"][index],
                tau * fine["terminal_rhs_D_state_D_tau"][index],
            )
            self.assertEqual(
                fine["selected_common_gain_response"],
                fine["selected_sensor_output"],
            )
            self.assertTrue(observation["tier1_controls_passed"])

    def test_output_count_obstruction_is_constructively_overcome(self) -> None:
        theorem = self.report["rank_theorem"]
        self.assertEqual(theorem["minimum_three_output_launch_A_effective_rank_exact"], 2)
        self.assertTrue(theorem["minimum_output_condition_is_constructively_attained"])
        self.assertEqual(theorem["selected_clock_output_count"], 5)
        self.assertEqual(theorem["selected_clock_effective_rank_exact"], 2)
        self.assertEqual(theorem["secondary_gain_selected_output_count"], 7)
        self.assertEqual(theorem["secondary_gain_effective_rank_exact"], 2)

    def test_rational_cost_weighted_search_and_positive_exact_floors(self) -> None:
        searches = self.report["rational_grid_search"]
        clock = searches["clock_only"]
        gain = searches["clock_and_optimistic_common_gain"]
        self.assertEqual(clock["evaluated_share_count"], 91)
        self.assertEqual(gain["evaluated_share_count"], 91)
        self.assertEqual(
            clock["selected"]["budget_shares_exact"],
            ["2/3", "1/3", "0/1"],
        )
        self.assertEqual(
            gain["selected"]["budget_shares_exact"],
            ["5/12", "1/4", "1/3"],
        )
        selected = self.report["selected_designs"]
        for name, design in selected.items():
            with self.subTest(name=name):
                floor = design["positive_floor"]
                self.assertTrue(floor["strictly_positive_exact"])
                self.assertGreater(Q(floor["profiled_floor_lower_exact"]), 0)
        self.assertGreater(
            Q(selected["cost_weighted_clock_only"]["positive_floor"]["profiled_floor_lower_exact"]),
            Q(selected["minimum_clock_only"]["positive_floor"]["profiled_floor_lower_exact"]),
        )

    def test_all_exact_query_children_verify_and_annihilate_nuisance(self) -> None:
        children = self.report["exact_query_engine_children"]
        self.assertEqual(len(children), 3)
        for name, child in children.items():
            with self.subTest(name=name):
                self.assertTrue(verify_query_protocol_report(child)["passed"])
                self.assertTrue(child["identifiability"]["query_identifiable_exact"])
                self.assertEqual(child["effective_response_rank"], 2)
                factorization = child["factorization_and_minimax"]
                self.assertTrue(factorization["decoder_annihilates_nuisance_exact"])
                self.assertTrue(factorization["factorization_exists"])

    def test_exact_preparation_and_tier1_boundary_are_explicit(self) -> None:
        report = self.report
        self.assertEqual(report["proof_boundary"], PROOF_BOUNDARY)
        self.assertIn("exact declarations", report["experimental_semantics"]["preparation"])
        self.assertFalse(report["finite_library_scope"]["continuous_launch_time_sensor_optimization_claimed"])
        self.assertTrue(
            all(value is False for value in report["outward_validation"].values())
        )

    def test_strict_recomputing_verifier_rejects_tampering(self) -> None:
        round_trip = json.loads(json.dumps(self.report))
        verification = verify_grouped_protocol_report(round_trip)
        self.assertTrue(verification["passed"])
        self.assertTrue(verification["tier1_numerics_recomputed"])
        self.assertFalse(verification["outward_ode_validation_verified"])

        bad_schema = deepcopy(round_trip)
        bad_schema["schema_version"] = "unknown"
        early_rejection = verify_grouped_protocol_report(bad_schema)
        self.assertFalse(early_rejection["passed"])
        self.assertFalse(early_rejection["tier1_numerics_recomputed"])
        self.assertFalse(early_rejection["finite_rational_grid_recomputed"])

        mutations = []
        outward = deepcopy(round_trip)
        outward["outward_validation"]["clock_response_enclosed"] = True
        mutations.append(outward)

        row = deepcopy(round_trip)
        row["scalar_observation_library"][0]["fine"][
            "selected_parameter_response_row"
        ][0] += 0.01
        mutations.append(row)

        share = deepcopy(round_trip)
        share["selected_designs"]["cost_weighted_clock_only"][
            "budget_shares_exact"
        ] = ["1/1", "0/1", "0/1"]
        mutations.append(share)

        child = deepcopy(round_trip)
        child["exact_query_engine_children"]["selected_cost_weighted_clock_only"][
            "effective_response_rank"
        ] = 1
        mutations.append(child)

        numeric_bool = deepcopy(round_trip)
        numeric_bool["scalar_observation_library"][0]["fine"]["terminal_state"][0] = True
        mutations.append(numeric_bool)

        for index, tampered in enumerate(mutations):
            with self.subTest(index=index):
                self.assertFalse(verify_grouped_protocol_report(tampered)["passed"])

    def test_cli_and_committed_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "grouped.json"
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["--output", str(path)]), 0)
            self.assertTrue(path.is_file())
            with redirect_stdout(output):
                self.assertEqual(main(["--verify", str(path)]), 0)

        artifact = (
            Path(__file__).resolve().parent
            / "artifacts"
            / "double_pendulum_grouped_protocol_tier1.json"
        )
        committed = json.loads(artifact.read_text(encoding="utf-8"))
        self.assertEqual(committed, self.report)
        self.assertTrue(verify_grouped_protocol_report(committed)["passed"])


if __name__ == "__main__":
    unittest.main()
