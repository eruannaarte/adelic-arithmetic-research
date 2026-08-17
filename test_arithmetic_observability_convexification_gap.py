from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from arithmetic_observability_convexification_gap import (
    AO8_ARTIFACT_PATH,
    AO9_ARTIFACT_PATH,
    DEFAULT_ARTIFACT_PATH,
    EFFECTIVE_TRIGONOMETRIC_DEGREE,
    ELEVEN_MODE_FACTORIZATIONS,
    EXPECTED_AO8_ARTIFACT_SHA256,
    EXPECTED_AO9_ARTIFACT_SHA256,
    EXPECTED_PREFIX_BOUND,
    EXPECTED_RANK_ELEVEN_AMPLITUDE,
    EXPECTED_RANK_ELEVEN_D14,
    FORMAL_PRECISION_BITS,
    MAX_ARTIFACT_BYTES,
    MAX_CONTAINER_ITEMS,
    MAX_JSON_DEPTH,
    PINNED_PAYLOAD_SHA256,
    RANK_ELEVEN_MODE,
    SCHEMA,
    TEN_MODE_FACTORIZATIONS,
    TESTS_PATH,
    VERIFIER_PATH,
    _canonical_json,
    _d14_from_factors,
    _factorization_product,
    _load_json_strict,
    _mode_record,
    _parse_fraction_limited,
    _pretty_json,
    _sha256,
    _sha256_file,
    artifact_document,
    build_payload,
    load_artifact,
    verify_artifact,
)


def _interval(record: dict[str, object]) -> tuple[Fraction, Fraction]:
    return Fraction(record["lower_exact"]), Fraction(record["upper_exact"])


class ConvexificationGapCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.artifact, cls.raw = load_artifact(DEFAULT_ARTIFACT_PATH)
        cls.payload = cls.artifact["payload"]

    def test_committed_artifact_is_canonical_pinned_and_reconstructed(self) -> None:
        self.assertEqual(self.raw, _pretty_json(self.artifact))
        self.assertEqual(self.artifact["schema"], SCHEMA)
        self.assertEqual(self.artifact["payload_sha256"], _sha256(self.payload))
        self.assertEqual(self.artifact["payload_sha256"], PINNED_PAYLOAD_SHA256)
        result = verify_artifact(self.artifact)
        self.assertTrue(result["passed"])
        self.assertTrue(result["full_reconstruction"])

    def test_reproduction_files_are_hash_pinned(self) -> None:
        reproduction = self.artifact["reproduction_files"]
        self.assertEqual(reproduction["verifier_basename"], VERIFIER_PATH.name)
        self.assertEqual(reproduction["tests_basename"], TESTS_PATH.name)
        self.assertEqual(reproduction["verifier_sha256"], _sha256_file(VERIFIER_PATH))
        self.assertEqual(reproduction["tests_sha256"], _sha256_file(TESTS_PATH))

    def test_dependency_artifacts_and_transitive_reproduction_are_pinned(self) -> None:
        dependencies = self.payload["dependencies"]
        self.assertEqual(
            dependencies["ao8_artifact_sha256"], EXPECTED_AO8_ARTIFACT_SHA256
        )
        self.assertEqual(
            dependencies["ao9_artifact_sha256"], EXPECTED_AO9_ARTIFACT_SHA256
        )
        self.assertEqual(_sha256_file(AO8_ARTIFACT_PATH), EXPECTED_AO8_ARTIFACT_SHA256)
        self.assertEqual(_sha256_file(AO9_ARTIFACT_PATH), EXPECTED_AO9_ARTIFACT_SHA256)
        for value in dependencies.values():
            self.assertEqual(len(value), 64)
            self.assertFalse(set(value) - set("0123456789abcdef"))

    def test_exact_prefix_localization_constant_recomputes(self) -> None:
        section = self.payload["fixed_tail_prefix_projection"]
        q = Fraction(section["gram_row_defect_q_G_upper_exact"])
        q5 = Fraction(section["row_5_off_diagonal_l1_upper_exact"])
        tau_w = Fraction(section["nonquery_support_maximum_upper_exact"])
        self.assertEqual(
            q,
            Fraction(
                257168756981514768514508306559006707,
                2**128,
            ),
        )
        self.assertEqual(
            q5,
            Fraction(108343607646993126701039729904793, 2**128),
        )
        self.assertEqual(
            tau_w,
            Fraction(6670899940450463606943553795810303, 2**128),
        )
        scaled = (tau_w + q5 / 25) / (1 - q)
        prefix = 2500 * scaled
        self.assertEqual(
            Fraction(section["normalized_nuisance_coefficient_linf_upper_exact"]),
            scaled,
        )
        self.assertEqual(
            Fraction(section["original_prefix_coefficient_linf_upper_exact"]),
            prefix,
        )
        self.assertEqual(prefix, EXPECTED_PREFIX_BOUND)
        self.assertLess(prefix, 1)
        self.assertTrue(section["original_prefix_bound_strictly_below_one"])
        self.assertEqual(section["nonquery_support_maximizers"], [4])

    def test_time_lattice_degree_antiperiod_and_zero_counts_are_exact(self) -> None:
        section = self.payload["symbolic_zero_geometry"]
        self.assertEqual(
            section["effective_time_lattice"],
            "{r/10: r odd, -8899<=r<=8899}",
        )
        self.assertEqual(section["trigonometric_degree_upper"], 8899)
        self.assertEqual(
            section["nonzero_response_zero_phases_modulo_20pi_upper"], 17798
        )
        self.assertEqual(
            section["nonzero_response_zero_phase_classes_modulo_10pi_upper"],
            8899,
        )
        self.assertEqual(section["exceptional_arithmetic_indices_upper"], 8899)
        self.assertEqual(section["exact_antiperiod_rule"], "F(x+10*pi)=-F(x)")
        components = section["time_components"]
        self.assertEqual([row["sample_count"] for row in components], [2550, 8900])
        self.assertEqual(
            [row["minimum_time_numerator_over_ten"] for row in components],
            [-2549, -EFFECTIVE_TRIGONOMETRIC_DEGREE],
        )
        self.assertEqual(
            [row["maximum_time_numerator_over_ten"] for row in components],
            [2549, EFFECTIVE_TRIGONOMETRIC_DEGREE],
        )
        self.assertTrue(all(row["all_time_numerators_odd"] for row in components))

    def test_arithmetic_zero_count_keeps_its_hypotheses_and_effectivity_caveat(self) -> None:
        section = self.payload["symbolic_zero_geometry"]
        self.assertIn("Gelfond-Schneider", section["arithmetic_phase_injectivity"])
        self.assertIn("not identically zero", section["zero_bound_hypothesis"])
        self.assertTrue(section["identically_zero_case_excluded_from_finite_zero_bound"])
        self.assertFalse(section["exceptional_indices_effectively_bounded"])
        self.assertFalse(section["numeric_root_search_used"])

    def test_ten_mode_factorizations_and_primal_endpoints_recompute(self) -> None:
        witness = self.payload["ten_mode_witness"]
        self.assertEqual(witness["mode_count"], 10)
        self.assertEqual(
            [record["mode"] for record in witness["mode_records"]],
            [mode for mode, _ in TEN_MODE_FACTORIZATIONS],
        )
        for expected, record in zip(TEN_MODE_FACTORIZATIONS, witness["mode_records"]):
            mode, frozen_factors = expected
            factors = tuple(tuple(pair) for pair in record["factorization"])
            self.assertEqual(factors, frozen_factors)
            self.assertEqual(_factorization_product(factors), mode)
            self.assertEqual(_d14_from_factors(factors), record["d14"])
            self.assertEqual(record["tail_coefficient"], record["d14"])
            self.assertEqual(
                Fraction(record["normalized_amplitude_exact"]),
                Fraction(record["d14"], mode**2),
            )
            self.assertTrue(record["target_kernel_strictly_negative"])
            phase_lower, phase_upper = _interval(
                record["first_alias_phase_offset_outward"]
            )
            self.assertGreater(phase_lower, -Fraction(1, 10**8))
            self.assertLess(phase_upper, Fraction(1, 10**8))
        self.assertTrue(witness["all_tail_coefficients_integral_and_legal"])
        self.assertFalse(witness["continuous_convexity_used"])

    def test_rank_eleven_factorization_d14_and_reduced_amplitude_recompute(self) -> None:
        record = self.payload["eleven_mode_witness"]["mode_records"][-1]
        mode, frozen_factors = RANK_ELEVEN_MODE
        factors = tuple(tuple(pair) for pair in record["factorization"])
        self.assertEqual(record["mode"], mode)
        self.assertEqual(factors, frozen_factors)
        self.assertEqual(_factorization_product(factors), mode)
        self.assertEqual(_d14_from_factors(factors), EXPECTED_RANK_ELEVEN_D14)
        self.assertEqual(record["d14"], EXPECTED_RANK_ELEVEN_D14)
        self.assertEqual(
            Fraction(record["normalized_amplitude_exact"]),
            EXPECTED_RANK_ELEVEN_AMPLITUDE,
        )
        self.assertEqual(
            Fraction(record["normalized_amplitude_exact"]),
            Fraction(EXPECTED_RANK_ELEVEN_D14, mode**2),
        )
        self.assertEqual(record["nonformal_discovery_rank"], 11)
        kernel_lower, kernel_upper = _interval(record["target_kernel_outward"])
        self.assertLess(kernel_upper, 0)
        self.assertLess(kernel_lower, kernel_upper)

    def test_all_eleven_modes_are_unique_integral_legal_endpoints(self) -> None:
        witness = self.payload["eleven_mode_witness"]
        records = witness["mode_records"]
        self.assertEqual(witness["mode_count"], 11)
        self.assertEqual(len(set(record["mode"] for record in records)), 11)
        self.assertEqual(
            [record["mode"] for record in records],
            [mode for mode, _ in ELEVEN_MODE_FACTORIZATIONS],
        )
        self.assertTrue(witness["all_modes_outside_prefix"])
        self.assertTrue(witness["all_tail_coefficients_integral_and_legal"])
        self.assertTrue(
            all(record["tail_coefficient_is_integral"] for record in records)
        )
        self.assertTrue(
            all(record["tail_coefficient_saturates_legal_endpoint"] for record in records)
        )

    def test_rank_eleven_squared_distance_and_radius_improvements_are_disjoint(self) -> None:
        old = self.payload["ten_mode_witness"]
        new = self.payload["eleven_mode_witness"]
        improvement = self.payload["rank_eleven_improvement"]
        old_squared_lower, _ = _interval(old["response_squared_outward"])
        _, new_squared_upper = _interval(new["response_squared_outward"])
        old_radius_lower, _ = _interval(old["critical_radius_outward"])
        _, new_radius_upper = _interval(new["critical_radius_outward"])
        self.assertGreater(old_squared_lower, new_squared_upper)
        self.assertGreater(old_radius_lower, new_radius_upper)
        self.assertEqual(
            Fraction(improvement["squared_distance_gap_lower_exact"]),
            old_squared_lower - new_squared_upper,
        )
        self.assertEqual(
            Fraction(improvement["critical_radius_gap_lower_exact"]),
            old_radius_lower - new_radius_upper,
        )
        self.assertTrue(improvement["comparison_uses_disjoint_512_bit_arb_intervals"])

    def test_rank_eleven_direct_one_coordinate_update_is_strictly_negative(self) -> None:
        section = self.payload["rank_eleven_improvement"]
        inner_lower, inner_upper = _interval(
            section["old_residual_inner_product_with_rank_eleven_column_outward"]
        )
        linear_lower, linear_upper = _interval(
            section["linear_squared_increment_outward"]
        )
        increment_lower, increment_upper = _interval(
            section["signed_squared_increment_outward"]
        )
        decrement_lower, decrement_upper = _interval(
            section["direct_squared_decrement_outward"]
        )
        amplitude = Fraction(section["rank_eleven_normalized_amplitude_exact"])
        self.assertEqual(amplitude, EXPECTED_RANK_ELEVEN_AMPLITUDE)
        self.assertEqual(len(section["ten_mode_cross_kernel_records"]), 10)
        self.assertEqual(
            [row["ten_mode_column"] for row in section["ten_mode_cross_kernel_records"]],
            [mode for mode, _ in TEN_MODE_FACTORIZATIONS],
        )
        target_kernel_lower, target_kernel_upper = _interval(
            section["target_5_kernel_with_rank_eleven_outward"]
        )
        self.assertLess(target_kernel_upper, 0)
        self.assertLess(target_kernel_lower, target_kernel_upper)
        aggregate_lower = target_kernel_lower / 25
        aggregate_upper = target_kernel_upper / 25
        for (_, factors), row in zip(
            TEN_MODE_FACTORIZATIONS, section["ten_mode_cross_kernel_records"]
        ):
            mode = row["ten_mode_column"]
            coefficient = _d14_from_factors(factors)
            weight = Fraction(coefficient, mode**2)
            kernel_lower, kernel_upper = _interval(
                row["kernel_with_rank_eleven_outward"]
            )
            aggregate_lower += weight * kernel_lower
            aggregate_upper += weight * kernel_upper
        # The independently rounded aggregate and direct Arb sum need not
        # contain one another, but rigorous evaluations of the same exact
        # expression must overlap.
        self.assertLessEqual(aggregate_lower, inner_upper)
        self.assertLessEqual(inner_lower, aggregate_upper)
        self.assertLess(inner_upper, 0)
        self.assertLess(linear_upper, 0)
        self.assertLess(increment_upper, 0)
        self.assertGreater(decrement_lower, 0)
        self.assertEqual(decrement_lower, -increment_upper)
        self.assertEqual(decrement_upper, -increment_lower)
        self.assertEqual(
            Fraction(section["quadratic_squared_increment_exact"]),
            amplitude**2,
        )
        self.assertTrue(
            section[
                "direct_update_overlaps_independent_full_eleven_mode_evaluation"
            ]
        )

    def test_rank_eleven_radius_has_the_declared_scale(self) -> None:
        lower, upper = _interval(
            self.payload["eleven_mode_witness"]["critical_radius_outward"]
        )
        self.assertGreater(lower, Fraction("0.019999999997766001249970807963"))
        self.assertLess(upper, Fraction("0.019999999997766001249970807965"))
        self.assertEqual(
            self.payload["parameters"]["formal_precision_bits"],
            FORMAL_PRECISION_BITS,
        )

    def test_c7_profile_proves_nonstationarity_but_not_an_integer_improvement(self) -> None:
        section = self.payload["continuous_c7_profile"]
        inner_lower, inner_upper = _interval(
            section["residual_pairing_h7_outward"]
        )
        drop_lower, drop_upper = _interval(section["critical_radius_drop_outward"])
        h7_lower, h7_upper = _interval(
            section["corresponding_original_prefix_p7_outward"]
        )
        self.assertLess(inner_upper, 0)
        self.assertGreater(inner_lower, Fraction("-9.163e-10"))
        self.assertGreater(drop_lower, Fraction("5.2467e-18"))
        self.assertLess(drop_upper, Fraction("5.2468e-18"))
        self.assertGreater(h7_lower, 0)
        self.assertLess(h7_upper, 1)
        self.assertTrue(section["old_ten_mode_point_not_quotient_stationary"])
        self.assertFalse(section["legal_integer_prefix_improvement_claimed"])
        self.assertFalse(section["exact_quotient_optimizer_claimed"])

    def test_c7_profiled_square_and_radius_are_strictly_smaller(self) -> None:
        old = self.payload["ten_mode_witness"]
        profile = self.payload["continuous_c7_profile"]
        old_squared_lower, _ = _interval(old["response_squared_outward"])
        _, profiled_squared_upper = _interval(
            profile["profiled_response_squared_outward"]
        )
        old_radius_lower, _ = _interval(old["critical_radius_outward"])
        _, profiled_radius_upper = _interval(
            profile["profiled_critical_radius_outward"]
        )
        self.assertGreater(old_squared_lower, profiled_squared_upper)
        self.assertGreater(old_radius_lower, profiled_radius_upper)
        self.assertGreater(Fraction(profile["squared_distance_drop_lower_exact"]), 0)
        self.assertGreater(Fraction(profile["critical_radius_drop_lower_exact"]), 0)

    def test_updated_radius_bracket_composes_exactly(self) -> None:
        section = self.payload["updated_bracket_and_arithmetic_defect_geometry"]
        distance_lower = Fraction(section["quotient_distance_squared_lower_exact"])
        distance_upper = Fraction(
            section["integral_witness_distance_squared_upper_exact"]
        )
        radius_lower = Fraction(section["critical_radius_squared_lower_exact"])
        radius_upper = Fraction(section["critical_radius_squared_upper_exact"])
        old_upper = Fraction(
            section["old_ao9_integral_witness_distance_squared_upper_exact"]
        )
        self.assertEqual(distance_lower, 4 * radius_lower)
        self.assertEqual(distance_upper, 4 * radius_upper)
        self.assertLess(distance_lower, distance_upper)
        self.assertLess(distance_upper, old_upper)
        self.assertTrue(section["new_integral_upper_strictly_improves_ao9"])
        self.assertTrue(section["applies_as_bracket_to_continuous_box_radius"])
        self.assertTrue(section["applies_as_bracket_to_integral_envelope_radius"])
        self.assertFalse(section["continuous_and_integral_values_claimed_equal"])

    def test_convex_projection_localization_is_the_exact_squared_gap(self) -> None:
        section = self.payload["updated_bracket_and_arithmetic_defect_geometry"]
        projection = section["current_convex_projection_localization"]
        lower = Fraction(section["quotient_distance_squared_lower_exact"])
        upper = Fraction(section["integral_witness_distance_squared_upper_exact"])
        gap = Fraction(
            projection["convex_projection_to_alias_distance_squared_upper_exact"]
        )
        self.assertEqual(gap, upper - lower)
        radical_lower, radical_upper = _interval(
            projection["convex_projection_to_alias_distance_upper_outward"]
        )
        self.assertLessEqual(radical_lower**2, gap)
        self.assertLessEqual(gap, radical_upper**2)
        self.assertFalse(projection["coefficientwise_optimizer_identified"])
        self.assertFalse(projection["integral_optimizer_identified"])

    def test_arithmetic_defect_geometry_keeps_exact_equivalence_separate(self) -> None:
        section = self.payload["updated_bracket_and_arithmetic_defect_geometry"]
        geometry = section["arithmetic_defect_geometry"]
        self.assertIn("independent integral", geometry["model_scope"])
        self.assertEqual(
            geometry["two_sided_inequality"],
            "sqrt(d^2+eta_arith^2)<=dist(q,S_Z)<=d+eta_arith",
        )
        self.assertEqual(geometry["integral_equals_convex_distance_iff"], "eta_arith=0")
        self.assertFalse(geometry["arithmetic_defect_exact_value_computed"])
        consequences = self.payload["formal_consequences"]
        self.assertTrue(
            consequences[
                "unbounded_quotient_equals_bounded_continuous_prefix_distance"
            ]
        )
        self.assertTrue(
            consequences[
                "unbounded_quotient_equals_distance_to_convex_hull_of_independent_integral_envelope_responses"
            ]
        )
        self.assertTrue(
            consequences[
                "integral_attainment_at_quotient_forces_zero_nonquery_prefix"
            ]
        )

    def test_formal_scope_does_not_overclaim(self) -> None:
        scope = self.payload["scope"]
        consequences = self.payload["formal_consequences"]
        self.assertIn("compact integer-selection image", scope["formal_tail_model"])
        self.assertFalse(scope["exact_optimizer_identified"])
        self.assertFalse(scope["continuous_integral_equality_claimed"])
        self.assertFalse(scope["number_field_realization_claimed"])
        self.assertFalse(scope["coarse_numerical_optimizer_included"])
        self.assertFalse(scope["symbolic_zero_theorem_numerically_inferred"])
        self.assertFalse(consequences["exact_closest_fibre_value_determined"])

    def test_build_payload_is_byte_deterministic(self) -> None:
        first = build_payload()
        second = build_payload()
        self.assertEqual(_canonical_json(first), _canonical_json(second))
        self.assertEqual(_sha256(first), PINNED_PAYLOAD_SHA256)

    def test_artifact_document_reconstructs_committed_bytes(self) -> None:
        rebuilt = artifact_document(build_payload())
        self.assertEqual(_pretty_json(rebuilt), self.raw)

    def test_rehashed_payload_mutation_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.artifact)
        tampered["payload"]["fixed_tail_prefix_projection"][
            "original_prefix_coefficient_linf_upper_exact"
        ] = "1/1"
        tampered["payload_sha256"] = _sha256(tampered["payload"])
        with self.assertRaises(ValueError):
            verify_artifact(tampered)

    def test_bool_for_integer_alias_mutation_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.artifact)
        tampered["payload"]["parameters"]["formal_precision_bits"] = True
        tampered["payload_sha256"] = _sha256(tampered["payload"])
        with self.assertRaises(ValueError):
            verify_artifact(tampered)

    def test_reproduction_hash_mutation_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.artifact)
        tampered["reproduction_files"]["tests_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            verify_artifact(tampered)

    def test_dependency_file_mutation_is_rejected_even_with_untouched_payload(self) -> None:
        original = _sha256_file

        def hostile(path: Path) -> str:
            if path == AO9_ARTIFACT_PATH:
                return "0" * 64
            return original(path)

        with patch(
            "arithmetic_observability_convexification_gap._sha256_file",
            side_effect=hostile,
        ):
            with self.assertRaises(ValueError):
                verify_artifact(self.artifact)

    def test_factorization_hostile_mutations_are_rejected(self) -> None:
        mode, factors = RANK_ELEVEN_MODE
        with self.assertRaises(ValueError):
            _factorization_product(((2, 12), (4, 1)))
        with self.assertRaises(ValueError):
            _factorization_product(((3, 3), (2, 12)))
        with self.assertRaises(ValueError):
            _factorization_product(((2, 0),))
        with self.assertRaises(ValueError):
            _mode_record(mode + 1, factors, discovery_rank=11)

    def test_fraction_parser_rejects_noncanonical_and_oversized_inputs(self) -> None:
        self.assertEqual(_parse_fraction_limited("1/2"), Fraction(1, 2))
        for value in ("2/4", "1", "01/2", "1/-2", True, 1):
            with self.assertRaises(ValueError):
                _parse_fraction_limited(value)
        with self.assertRaises(ValueError):
            _parse_fraction_limited(f"{1 << 9000}/1")

    def test_strict_json_parser_rejects_duplicates_floats_constants_and_line_endings(self) -> None:
        hostile = {
            "duplicate.json": b'{"x":1,"x":2}\n',
            "float.json": b'{"x":1.25}\n',
            "constant.json": b'{"x":NaN}\n',
            "crlf.json": b'{"x":1}\r\n',
            "bom.json": b'\xef\xbb\xbf{"x":1}\n',
            "missing-newline.json": b'{"x":1}',
            "double-newline.json": b'{"x":1}\n\n',
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, raw in hostile.items():
                path = root / name
                path.write_bytes(raw)
                with self.subTest(name=name), self.assertRaises(ValueError):
                    _load_json_strict(path, MAX_ARTIFACT_BYTES)

    def test_noncanonical_json_and_oversized_artifact_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            noncanonical = root / "noncanonical.json"
            noncanonical.write_bytes(b'{"x": 1}\n')
            with self.assertRaises(ValueError):
                load_artifact(noncanonical)
            oversized = root / "oversized.json"
            oversized.write_bytes(b"{" + b" " * MAX_ARTIFACT_BYTES + b"}\n")
            with self.assertRaises(ValueError):
                _load_json_strict(oversized, MAX_ARTIFACT_BYTES)

    def test_strict_json_parser_enforces_integer_container_and_depth_bounds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            oversized_integer = root / "integer.json"
            oversized_integer.write_bytes(
                b'{"x":' + str(1 << 9000).encode("ascii") + b"}\n"
            )
            oversized_container = root / "container.json"
            oversized_container.write_bytes(
                ("{\"x\":[" + ",".join("0" for _ in range(MAX_CONTAINER_ITEMS + 1)) + "]}\n").encode("ascii")
            )
            excessive_depth = root / "depth.json"
            excessive_depth.write_bytes(
                ("{\"x\":" + "[" * (MAX_JSON_DEPTH + 2) + "0" + "]" * (MAX_JSON_DEPTH + 2) + "}\n").encode("ascii")
            )
            for path in (oversized_integer, oversized_container, excessive_depth):
                with self.subTest(path=path.name), self.assertRaises(ValueError):
                    _load_json_strict(path, MAX_ARTIFACT_BYTES)


if __name__ == "__main__":
    unittest.main()
