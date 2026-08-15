"""Adversarial controls for the proof-oriented protocol-design kernel.

These tests reconstruct the algebra behind the public report instead of
trusting its boolean labels.  They also preserve regression examples for
three proof-boundary errors found during the independent audit.
"""

from __future__ import annotations

from fractions import Fraction
from copy import deepcopy
import math
import unittest

from oig_protocol_design_engine import (
    RationalProtocol,
    _add,
    _ldl_positive_definite,
    _matmul,
    _scale,
    _subtract,
    _trace_product,
    _transpose,
    certify_frame_loss,
    design_protocols,
    exact_observable_quotient,
    exponential_time_response,
    information_matrix,
    rational_matrix,
    verify_design_report,
)
from oig_hidden_network_protocol_demo import (
    hidden_cycle_laplacian,
    tangent_injection,
    tangent_source_metric,
)


Q = Fraction


def _parse_matrix(rows: list[list[str]]):
    return rational_matrix([[Q(value) for value in row] for row in rows])


class ProtocolEngineAdversarialControls(unittest.TestCase):
    def setUp(self) -> None:
        # The third source direction is exactly common-blind.  The metric is
        # deliberately non-diagonal, so Euclidean-complement shortcuts fail.
        self.protocols = (
            RationalProtocol.from_rows(
                "mixed first", [[1, 1, 0]], [[Q(3, 2)]], cost=Q(2, 3)
            ),
            RationalProtocol.from_rows(
                "mixed second", [[2, -1, 0]], [[Q(5, 4)]], cost=Q(7, 5)
            ),
        )
        self.metric = rational_matrix(
            [[4, 1, 1], [1, 3, 1], [1, 1, 2]]
        )

    def test_quotient_injection_reconstructs_responses_and_cost(self) -> None:
        quotient = exact_observable_quotient(self.protocols, self.metric)
        coordinates = quotient.row_coordinates
        injection = quotient.injection
        identity = rational_matrix([[1, 0], [0, 1]])

        self.assertEqual(_matmul(coordinates, injection), identity)
        self.assertEqual(
            _matmul(_transpose(injection), _matmul(self.metric, injection)),
            quotient.source_metric,
        )
        for protocol in self.protocols:
            self.assertEqual(
                _matmul(protocol.response, _matmul(injection, coordinates)),
                protocol.response,
            )

    def test_sensor_reparameterization_with_covariance_change_is_invariant(self) -> None:
        original = RationalProtocol.from_rows(
            "original",
            [[1, 2], [3, -1]],
            [[2, Q(1, 2)], [Q(1, 2), 1]],
        )
        # R' = T R and W' = T^{-T} W T^{-1}, for T=diag(2,1/3).
        transformed = RationalProtocol.from_rows(
            "transformed",
            [[2, 4], [1, Q(-1, 3)]],
            [[Q(1, 2), Q(3, 4)], [Q(3, 4), 9]],
        )
        self.assertEqual(information_matrix(original), information_matrix(transformed))

    def test_reported_dual_bound_is_independently_feasible(self) -> None:
        report = design_protocols(
            self.protocols,
            self.metric,
            weight_denominator=10_000,
            dual_vector_scale=10**6,
        )
        quotient = exact_observable_quotient(self.protocols, self.metric)
        factor = rational_matrix(report["certificate"]["dual_witness_integer_factor"])
        raw_witness = _matmul(factor, _transpose(factor))
        normalization = _trace_product(quotient.source_metric, raw_witness)
        witness = _scale(raw_witness, Q(1) / normalization)
        self.assertEqual(_trace_product(quotient.source_metric, witness), 1)

        sensitivities = tuple(
            _trace_product(information, witness) / protocol.cost
            for information, protocol in zip(
                quotient.protocol_information, self.protocols
            )
        )
        self.assertEqual(
            max(sensitivities),
            Q(report["certificate"]["dual_optimum_upper_exact"]),
        )

        shares = tuple(Q(row["budget_share_exact"]) for row in report["protocols"])
        physical = tuple(Q(row["physical_weight_exact"]) for row in report["protocols"])
        self.assertEqual(sum(shares), 1)
        self.assertEqual(
            sum(protocol.cost * weight for protocol, weight in zip(self.protocols, physical)),
            1,
        )
        for share, weight, protocol in zip(shares, physical, self.protocols):
            self.assertEqual(weight, share / protocol.cost)

        gram = rational_matrix([[0, 0], [0, 0]])
        for information, weight in zip(quotient.protocol_information, physical):
            gram = _add(gram, _scale(information, weight))
        lower = Q(report["certificate"]["primal_generalized_floor_lower_exact"])
        self.assertTrue(
            _ldl_positive_definite(
                _subtract(gram, _scale(quotient.source_metric, lower))
            )
        )

    def test_whitened_noise_is_not_calibrated_twice(self) -> None:
        protocol = RationalProtocol.from_rows("variance four", [[1]], [[Q(1, 4)]])
        report = design_protocols([protocol], [[1]], exposure_multiplier=4)
        noise = report["noise_performance"]["approximate_design_measure"]
        self.assertNotIn("noise_sigma", noise)
        self.assertNotIn("sigma", noise["formula"])
        self.assertTrue(math.isfinite(noise["descriptive_exact_gaussian_error"]))
        self.assertGreater(Q(noise["gaussian_error_rational_upper_exact"]), 0)

    def test_mass_conservation_without_markov_signs_is_rejected(self) -> None:
        # Column sums vanish, but -L has negative off-diagonal transition
        # rates, so this is not a Markov Laplacian under p'=-Lp.
        with self.assertRaisesRegex(ValueError, "nonpositive off-diagonal"):
            exponential_time_response(
                [[-1, 1], [1, -1]], [[1], [-1]], [[1, 0]], 3
            )

    def test_hidden_benchmark_declarations_are_computed_not_trusted(self) -> None:
        laplacian = hidden_cycle_laplacian()
        injection = tangent_injection()
        self.assertNotEqual(laplacian, _transpose(laplacian))
        for column in range(4):
            self.assertEqual(sum(laplacian[row][column] for row in range(4)), 0)
        for row in range(4):
            for column in range(4):
                if row != column:
                    self.assertLessEqual(laplacian[row][column], 0)
        for column in range(3):
            self.assertEqual(sum(injection[row][column] for row in range(4)), 0)
        self.assertEqual(
            _matmul(_transpose(injection), injection), tangent_source_metric()
        )

    def test_nonpositive_frame_transfer_is_not_promoted_to_zero(self) -> None:
        record = certify_frame_loss(
            [[0]],
            [[-1]],
            [[1]],
            inherited_floor=0,
        )
        transferred = Q(record["transferred_form_bound_exact"])
        self.assertLess(transferred, 0)
        self.assertFalse(record["frame_preserves_positive_floor"])
        self.assertNotIn("transferred_floor_lower_exact", record)

    def test_invalid_descriptive_noise_inputs_are_rejected(self) -> None:
        protocol = RationalProtocol.from_rows("one", [[1]], [[1]])
        with self.assertRaises(TypeError):
            design_protocols([protocol], [[1]], amplitude=float("nan"))
        with self.assertRaises(ValueError):
            design_protocols([protocol], [[1]], amplitude="-1")
        with self.assertRaises(ValueError):
            design_protocols([protocol], [[1]], exposure_multiplier=Q(3, 2))

    def test_self_contained_verifier_detects_primal_and_dual_tampering(self) -> None:
        report = design_protocols(
            self.protocols,
            self.metric,
            weight_denominator=10_000,
            dual_vector_scale=10**6,
        )
        self.assertTrue(verify_design_report(report)["passed"])

        primal_tamper = {**report, "certificate": dict(report["certificate"])}
        primal_tamper["certificate"]["primal_generalized_floor_lower_exact"] = "100/1"
        self.assertFalse(verify_design_report(primal_tamper)["passed"])

        dual_tamper = {**report, "certificate": dict(report["certificate"])}
        dual_tamper["certificate"]["dual_optimum_upper_exact"] = "0/1"
        self.assertFalse(verify_design_report(dual_tamper)["passed"])

        instance_tamper = {**report, "protocols": [dict(row) for row in report["protocols"]]}
        instance_tamper["protocols"][0]["response_exact"] = [["999/1", "0/1", "0/1"]]
        self.assertFalse(verify_design_report(instance_tamper)["passed"])

        dimension_tamper = {**report, "source_dimension": 3.5}
        self.assertFalse(verify_design_report(dimension_tamper)["passed"])

        boolean_tamper = {**report, "certificate": dict(report["certificate"])}
        boolean_tamper["certificate"]["dual_metric_trace_exactly_one"] = False
        self.assertFalse(verify_design_report(boolean_tamper)["passed"])

    def test_verifier_rejects_truncated_integer_realization(self) -> None:
        protocols = (
            RationalProtocol.from_rows("first", [[1, 0]], [[1]]),
            RationalProtocol.from_rows("second", [[0, 1]], [[1]]),
        )
        report = design_protocols(
            protocols, [[1, 0], [0, 1]], weight_denominator=3
        )
        tampered = deepcopy(report)
        approximate = tampered["noise_performance"]["approximate_design_measure"]
        realized = tampered["noise_performance"]["integer_realization"]
        for field in (
            "role",
            "amplitude_exact",
            "continuous_budget_exposure_multiplier",
            "certified_squared_separation_lower_exact",
            "gaussian_error_rational_upper_exact",
            "gaussian_error_rational_upper_method",
            "descriptive_exact_gaussian_error",
            "formula",
        ):
            realized[field] = approximate[field]
        realized["realized_budget_multiplier"] = 1
        realized["protocol_counts"] = [0, 0]
        self.assertFalse(verify_design_report(tampered)["passed"])

        oversized = deepcopy(report)
        second = design_protocols(
            protocols, [[1, 0], [0, 1]], weight_denominator=3,
            exposure_multiplier=6,
        )
        oversized["noise_performance"]["integer_realization"] = deepcopy(
            second["noise_performance"]["integer_realization"]
        )
        oversized["noise_performance"]["integer_realization"][
            "requested_multiplier_was_exactly_realizable"
        ] = False
        self.assertFalse(verify_design_report(oversized)["passed"])


if __name__ == "__main__":
    unittest.main()
