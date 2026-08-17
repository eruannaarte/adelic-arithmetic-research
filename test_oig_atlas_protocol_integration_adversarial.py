"""Independent hostile controls for the pinned Atlas-to-OIG proof chain."""

from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import unittest

from oig_atlas_protocol_integration import (
    run_integration_demo,
    verify_atlas_protocol_integration_report,
)
from oig_robust_model_quotient import certify_response_tube_pair
from oig_structured_nuisance import demo_certificates


class AtlasProtocolIntegrationAdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(json.dumps(run_integration_demo()))

    def test_cross_layer_followthrough_is_rederived_not_trusted(self) -> None:
        report = self.report
        selection = report["query_gain_library"]["selection"]
        selected = report["query_gain_library"]["candidates"][
            selection["selected_candidate_index"]
        ]["query_certificate"]
        structured = report["selected_protocol_structured_separation"]
        tube = report["selected_protocol_response_tube"]

        self.assertEqual(selection["selected_candidate_name"], "double gain")
        response = [
            [Fraction(entry) for entry in row]
            for row in tube["response_exact"]
        ]
        secant = [Fraction(entry) for entry in tube["secant_exact"]]
        response_on_secant = [
            sum(row[j] * secant[j] for j in range(len(secant)))
            for row in response
        ]
        self.assertEqual(
            response_on_secant,
            [
                Fraction(entry)
                for entry in structured["problem"]["query_response_exact"]
            ],
        )
        self.assertEqual(
            selected["declared_observation_exact"], tube["response_exact"]
        )
        self.assertEqual(
            selected["declared_output_metric_exact"],
            structured["problem"]["observation_noise_precision_exact"],
        )
        self.assertEqual(
            selected["declared_output_metric_exact"], tube["output_metric_exact"]
        )
        self.assertEqual(
            selected["declared_source_metric_exact"], tube["source_metric_exact"]
        )

        exact = structured["exact_calculation"]
        self.assertEqual(
            Fraction(exact["distance_squared_lower_exact"]),
            Fraction(exact["distance_squared_upper_exact"]),
        )
        self.assertLess(
            Fraction(tube["data_noise_radius_exact"]) ** 2,
            Fraction(exact["critical_equal_noise_radius_squared_lower_exact"]),
        )
        self.assertTrue(tube["certified_disjoint"])
        self.assertTrue(
            report["integration_ledger"][
                "selected_protocol_remains_disjoint_under_structured_nuisance_and_declared_noise"
            ]
        )

    def test_individually_valid_but_incoherent_children_are_rejected(self) -> None:
        substitutions = []

        different_structured = deepcopy(self.report)
        different_structured["selected_protocol_structured_separation"] = (
            demo_certificates()["point_certificate"]
        )
        substitutions.append(different_structured)

        different_tube = deepcopy(self.report)
        different_tube["selected_protocol_response_tube"] = (
            certify_response_tube_pair(
                [[3]],
                [[1]],
                [[1]],
                [1],
                source_radius=0,
                data_noise_radius="1/2",
            )
        )
        substitutions.append(different_tube)

        for substitution in substitutions:
            with self.subTest():
                self.assertFalse(
                    verify_atlas_protocol_integration_report(substitution)[
                        "passed"
                    ]
                )

    def test_type_scope_and_cross_layer_ledger_tampering_are_rejected(self) -> None:
        mutations = []

        boolean_as_integer = deepcopy(self.report)
        boolean_as_integer["integration_ledger"][
            "all_pinned_integration_obligations_pass"
        ] = 1
        mutations.append(boolean_as_integer)

        false_cross_layer_claim = deepcopy(self.report)
        false_cross_layer_claim["integration_ledger"][
            "selected_protocol_remains_disjoint_under_structured_nuisance_and_declared_noise"
        ] = False
        mutations.append(false_cross_layer_claim)

        narrowed_boundary = deepcopy(self.report)
        narrowed_boundary["proof_boundary"] = "unrestricted robust-design theorem"
        mutations.append(narrowed_boundary)

        surplus = deepcopy(self.report)
        surplus["continuous_library_optimum_certified"] = True
        mutations.append(surplus)

        for mutation in mutations:
            with self.subTest():
                self.assertFalse(
                    verify_atlas_protocol_integration_report(mutation)["passed"]
                )

    def test_committed_artifact_reproduces_the_pinned_report_exactly(self) -> None:
        artifact = json.loads(
            Path(__file__)
            .with_name("certificates")
            .joinpath("oig_atlas_protocol_integration.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(artifact, self.report)
        self.assertTrue(verify_atlas_protocol_integration_report(artifact)["passed"])


if __name__ == "__main__":
    unittest.main()
