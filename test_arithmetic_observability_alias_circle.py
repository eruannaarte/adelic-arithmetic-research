from __future__ import annotations

import copy
from fractions import Fraction
import json
import os
from pathlib import Path
import tempfile
import unittest

from flint import fmpz_poly
import gmpy2
from verified_mellin_certificate import _distance_to_alias_lower as _legacy_distance_to_alias_lower

from arithmetic_observability_alias_circle import (
    ANCHORS,
    BIN_COUNT,
    BIN_WIDTH,
    DEFAULT_AO8_PATH,
    DEFAULT_ARTIFACT_PATH,
    DEFAULT_SOURCE_PATH,
    DEGREE,
    EXPECTED_ELEMENTARY_TAIL_OUTPUT_NUMERATOR,
    EXPECTED_FINE_CONVOLUTION_SHA256,
    MAX_ARTIFACT_BYTES_AO9,
    MAXIMUM_NORM,
    MPFR_PRECISION_BITS,
    OUTPUT_SCALE_BITS,
    PINNED_PAYLOAD_SHA256,
    SCHEMA,
    TESTS_PATH,
    TRUNCATION,
    VERIFIER_PATH,
    WINDOW_A0,
    WINDOW_COEFFICIENT_HEX,
    WINDOW_S2,
    _canonical_json,
    _certified_target_cells,
    _corrected_derivative_upper,
    _corrected_dirichlet_upper,
    _corrected_distance_to_alias_lower,
    _exact_cross_correlations,
    _first_retained_convolution_index,
    _load_json_strict,
    _log_integer_interval,
    _lower_mpfr,
    _pretty_json,
    _sha256,
    _sha256_file,
    _upper_mpfr,
    load_artifact,
    verify_artifact,
)


class AliasCircleCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.artifact, cls.raw = load_artifact(DEFAULT_ARTIFACT_PATH)
        cls.payload = cls.artifact["payload"]
        cls.remote = cls.payload["formal_remote"]
        cls.consequences = cls.payload["observability_consequences"]

    def test_committed_artifact_is_canonical_and_pinned(self) -> None:
        self.assertEqual(self.raw, _pretty_json(self.artifact))
        self.assertEqual(self.artifact["schema"], SCHEMA)
        self.assertEqual(self.artifact["payload_sha256"], _sha256(self.payload))
        self.assertEqual(self.artifact["payload_sha256"], PINNED_PAYLOAD_SHA256)

    def test_fast_strict_verifier_accepts_artifact(self) -> None:
        result = verify_artifact(self.artifact, DEFAULT_SOURCE_PATH, DEFAULT_AO8_PATH)
        self.assertTrue(result["passed"])
        self.assertFalse(result["full_reconstruction"])

    @unittest.skipUnless(os.environ.get("AO9_FULL_REBUILD") == "1", "expensive opt-in reconstruction")
    def test_full_reconstruction_matches_artifact(self) -> None:
        result = verify_artifact(
            self.artifact,
            DEFAULT_SOURCE_PATH,
            DEFAULT_AO8_PATH,
            recompute=True,
        )
        self.assertTrue(result["passed"])
        self.assertTrue(result["full_reconstruction"])

    def test_reproduction_files_are_pinned(self) -> None:
        reproduction = self.artifact["reproduction_files"]
        self.assertEqual(reproduction["verifier_basename"], VERIFIER_PATH.name)
        self.assertEqual(reproduction["tests_basename"], TESTS_PATH.name)
        self.assertEqual(reproduction["verifier_sha256"], _sha256_file(VERIFIER_PATH))
        self.assertEqual(reproduction["tests_sha256"], _sha256_file(TESTS_PATH))

    def test_fine_mesh_and_exact_convolution_metadata(self) -> None:
        parameters = self.payload["parameters"]
        self.assertEqual(parameters["degree"], DEGREE)
        self.assertEqual(parameters["bin_width"], "1/10000")
        self.assertEqual(Fraction(parameters["bin_width"]), BIN_WIDTH)
        self.assertEqual(parameters["bin_count"], BIN_COUNT)
        self.assertEqual(self.remote["convolution_scale_bits"], 96 * DEGREE)
        self.assertEqual(
            self.remote["convolution_sha256"],
            EXPECTED_FINE_CONVOLUTION_SHA256,
        )
        self.assertEqual(self.remote["combined_kernel_scale_bits"], 144)
        self.assertEqual(self.remote["remote_output_scale_bits"], OUTPUT_SCALE_BITS)

    def test_aligned_cells_and_retained_boundary_recompute(self) -> None:
        cells = _certified_target_cells()
        self.assertEqual(list(cells), self.remote["target_log_cell_indices"])
        self.assertEqual(cells[0], 0)
        self.assertEqual(cells[-1], 39_120)
        self.assertEqual(cells[2], 10_986)
        self.assertEqual(cells[42], 37_612)
        first = _first_retained_convolution_index()
        self.assertEqual(first, 138_142)
        self.assertEqual(first, self.remote["first_retained_convolution_index"])
        self.assertEqual(self.remote["retained_convolution_count"], BIN_COUNT - first)
        cutoff_lower, cutoff_upper = _log_integer_interval(
            TRUNCATION + 1, MPFR_PRECISION_BITS
        )
        previous_endpoint_upper = _upper_mpfr(
            Fraction(first - 1 + DEGREE, 10_000), MPFR_PRECISION_BITS
        )
        first_endpoint_lower = _lower_mpfr(
            Fraction(first + DEGREE, 10_000), MPFR_PRECISION_BITS
        )
        self.assertLessEqual(previous_endpoint_upper, cutoff_lower)
        self.assertLess(cutoff_upper, first_endpoint_lower)
        self.assertEqual(self.remote["aligned_interval_index_minimum"], 99_021)
        self.assertEqual(self.remote["aligned_interval_count"], 725_578)
        self.assertEqual(self.remote["aligned_interval_index_maximum"], 824_598)
        self.assertEqual(
            Fraction(self.remote["aligned_interval_final_endpoint_exact"]),
            Fraction(824_613, 10_000),
        )
        self.assertGreater(
            Fraction(self.remote["aligned_interval_final_endpoint_exact"]),
            Fraction(self.payload["parameters"]["maximum_log"]),
        )

    def test_self_contained_window_and_moments_recompute_exactly(self) -> None:
        parameters = self.payload["parameters"]
        self.assertEqual(
            parameters["window_coefficients_binary64_hex"],
            list(WINDOW_COEFFICIENT_HEX),
        )
        coefficients = [
            Fraction.from_float(float.fromhex(value))
            for value in parameters["window_coefficients_binary64_hex"]
        ]
        a0 = Fraction(1) + 2 * sum(coefficients, Fraction())
        s2 = sum(abs(value) * r**2 for r, value in enumerate(coefficients, 1))
        self.assertEqual(a0, WINDOW_A0)
        self.assertEqual(s2, WINDOW_S2)
        self.assertEqual(Fraction(parameters["window_a0_exact"]), a0)
        self.assertEqual(Fraction(parameters["window_S2_exact"]), s2)

    def test_cross_correlation_reversal_on_impulses_and_signed_offsets(self) -> None:
        mass_values = [0, 2, 0, 3]
        kernel = [5, 7, 11, 13, 17, 19]
        offsets = (-1, 0, 1, 2)
        observed, _ = _exact_cross_correlations(
            fmpz_poly(mass_values), kernel, offsets
        )
        expected = tuple(
            sum(
                mass * kernel[index + offset]
                for index, mass in enumerate(mass_values)
                if 0 <= index + offset < len(kernel)
            )
            for offset in offsets
        )
        self.assertEqual(observed, expected)

    def test_q3_alias_distance_uses_opposite_rounding_for_subtraction(self) -> None:
        precision = 64
        period = (
            _lower_mpfr(Fraction(1, 5), precision),
            _upper_mpfr(Fraction(1, 5), precision),
        )
        exact_frequency = Fraction(600_000_000_000_000_001, 10**18)
        frequency = (
            _lower_mpfr(exact_frequency, precision),
            _upper_mpfr(exact_frequency, precision),
        )
        distance = _corrected_distance_to_alias_lower(
            frequency, period, precision
        )
        legacy = _legacy_distance_to_alias_lower(frequency, period, precision)
        self.assertGreater(distance, 0)
        exact_distance = gmpy2.mpq(1, 10**18)
        self.assertLessEqual(distance, exact_distance)
        self.assertGreater(legacy, exact_distance)
        self.assertLess(distance, legacy)
        downward = gmpy2.context(
            gmpy2.context(), precision=precision, round=gmpy2.RoundDown
        )
        upward = gmpy2.context(
            gmpy2.context(), precision=precision, round=gmpy2.RoundUp
        )
        expected_q3_lower = downward.sub(
            frequency[0], upward.mul(3, period[1])
        )
        self.assertEqual(distance, expected_q3_lower)

    def test_directed_denominator_primitives_are_true_uppers(self) -> None:
        precision = 80
        nearest = gmpy2.context(
            gmpy2.context(), precision=precision, round=gmpy2.RoundToNearest
        )
        upward = gmpy2.context(
            gmpy2.context(), precision=precision, round=gmpy2.RoundUp
        )
        with nearest:
            x = gmpy2.const_pi() / 1_234_567
        x_exact = gmpy2.mpq(x)

        true_dirichlet = gmpy2.mpq(1, 510) / x_exact
        fixed_dirichlet = _corrected_dirichlet_upper(
            gmpy2.mpfr(1), 510, x, precision
        )
        legacy_dirichlet = upward.div(1, upward.mul(510, x))
        self.assertGreaterEqual(fixed_dirichlet, true_dirichlet)
        self.assertLess(legacy_dirichlet, true_dirichlet)

        true_derivative = gmpy2.mpq(1, 2550) / (x_exact * x_exact)
        fixed_derivative = _corrected_derivative_upper(2550, x, precision)
        legacy_derivative = upward.div(
            1, upward.mul(2550, upward.mul(x, x))
        )
        self.assertGreaterEqual(fixed_derivative, true_derivative)
        self.assertLess(legacy_derivative, true_derivative)

    def test_every_formal_hash_is_lowercase_sha256(self) -> None:
        values = [
            self.remote["one_factor_sha256"],
            self.remote["convolution_sha256"],
            self.remote["combined_table_sha256"],
            self.remote["cross_correlation_selected_sha256"],
            *self.remote["component_table_sha256"],
        ]
        for value in values:
            self.assertEqual(len(value), 64)
            self.assertEqual(set(value) - set("0123456789abcdef"), set())

    def test_elementary_tail_is_added_exactly_once_after_mixing(self) -> None:
        self.assertEqual(self.remote["terminal_tail_addition_count"], 1)
        self.assertTrue(self.remote["terminal_tail_added_after_component_mixing"])
        elementary = self.remote["elementary_tail_output_numerator"]
        self.assertEqual(elementary, EXPECTED_ELEMENTARY_TAIL_OUTPUT_NUMERATOR)
        self.assertEqual(self.remote["elementary_tail_output_scale_bits"], 128)
        shift = (
            self.remote["cross_correlation_total_scale_bits"]
            - self.remote["remote_output_scale_bits"]
        )
        denominator = 1 << shift
        raw = [
            int(value)
            for value in self.remote["selected_cross_correlation_numerators"]
        ]
        expected = [
            (value + denominator - 1) // denominator + elementary
            for value in raw
        ]
        self.assertEqual(
            [int(value) for value in self.remote["target_numerators"]],
            expected,
        )
        self.assertIn(
            "deliberate safe overcount",
            self.remote["retained_bin_terminal_tail_overlap"],
        )

    def test_all_fifty_remote_bounds_are_positive_and_improve_ao8(self) -> None:
        numerators = [int(value) for value in self.remote["target_numerators"]]
        self.assertEqual(len(numerators), MAXIMUM_NORM)
        self.assertTrue(all(value > 0 for value in numerators))
        self.assertEqual(numerators[4], 5_409_849_216_438_953_933_448_898_259_612_643)
        self.assertEqual(numerators[49], 1_612_134_240_806_449_149_224_291_781_115_653)
        ao8, _ = _load_json_strict(DEFAULT_AO8_PATH, 500_000)
        old_records = ao8["payload"]["common_box_observability"]["coordinate_records"]
        records = self.consequences["coordinate_records"]
        for n, (new, old) in enumerate(zip(records, old_records), 1):
            new_remote = Fraction(new["fine_remote_correlation_upper_exact"])
            old_remote_principal = Fraction(old["remote_decoder_principal_exact"])
            self.assertLess(new_remote, old_remote_principal / n**2)

    def test_eta_and_radius_consequences_are_exact(self) -> None:
        q = Fraction(self.consequences["global_gram_row_upper_exact"])
        tau = Fraction(self.consequences["fine_complete_tail_maximum_exact"])
        for record in self.consequences["coordinate_records"]:
            n = record["coordinate"]
            finite = Fraction(record["finite_correlation_upper_exact"])
            remote = Fraction(record["fine_remote_correlation_upper_exact"])
            q_n = Fraction(record["gram_row_upper_exact"])
            eta = Fraction(record["fine_pair_specific_eta_exact"])
            self.assertEqual(eta, n**2 * (finite + remote + q_n * tau / (1 - q)))
            schur = (1 - q - q_n**2) / (1 - q)
            self.assertEqual(
                Fraction(record["fine_common_box_radius_squared_exact"]),
                (1 - eta) ** 2 * schur / (4 * n**4),
            )

    def test_four_anchor_and_all_fifty_bottlenecks(self) -> None:
        radii = {
            row["coordinate"]: Fraction(row["fine_common_box_radius_squared_exact"])
            for row in self.consequences["coordinate_records"]
        }
        self.assertEqual(min(ANCHORS, key=radii.__getitem__), 5)
        self.assertEqual(min(radii, key=radii.__getitem__), 50)
        self.assertEqual(self.consequences["unique_four_anchor_bottleneck"], 5)
        self.assertEqual(self.consequences["unique_all_fifty_bottleneck"], 50)

    def test_selected_eta_bounds_strictly_improve_ao8(self) -> None:
        improvements = self.consequences["selected_eta_improvements"]
        self.assertEqual([row["coordinate"] for row in improvements], [5, 50])
        for row in improvements:
            old = Fraction(row["old_eta_exact"])
            fine = Fraction(row["fine_eta_exact"])
            self.assertGreater(old, fine)
            self.assertEqual(Fraction(row["old_to_fine_eta_ratio_exact"]), old / fine)

    def test_prefix_reduction_and_uniform_quotient_bound_are_exact(self) -> None:
        prefix = self.consequences["prefix_reduction"]
        upper = Fraction(prefix["comparison_upper_squared_exact"])
        excluded = prefix["excluded_nonquery_coordinates"]
        unresolved = prefix["unresolved_nonquery_coordinates"]
        self.assertEqual(excluded, [4, *range(6, 25)])
        self.assertEqual(unresolved, list(range(25, 51)))
        self.assertFalse(prefix["global_closest_fibre_search_completed"])
        for row in prefix["excluded_coordinate_records"]:
            self.assertGreater(Fraction(row["unit_projection_lower_squared_exact"]), upper)
            self.assertGreater(Fraction(row["excess_over_alias_upper_exact"]), 0)

        quotient = prefix["uniform_quotient_bound"]
        coordinates = (4, *range(6, 51))
        self.assertEqual(quotient["nonquery_coordinates"], list(coordinates))
        self.assertTrue(quotient["ao8_query_branch_reduction_inherited"])
        self.assertTrue(quotient["realified_real_symmetric_gram"])
        q = Fraction(self.consequences["global_gram_row_upper_exact"])
        rows = self.consequences["coordinate_records"]
        q_5 = Fraction(rows[4]["gram_row_upper_exact"])
        complete = {
            row["coordinate"]: Fraction(row["complete_correlation_upper_exact"])
            for row in rows
        }
        s_5 = 1 - q_5**2 / (1 - q)
        beta_l1 = q_5 / (1 - q)
        tau_w = max(complete[n] for n in coordinates)
        penalty = complete[5] + tau_w * beta_l1
        positive_numerator = s_5 / 25 - penalty
        distance_squared = positive_numerator**2 / s_5
        radius_squared = distance_squared / 4
        self.assertEqual(
            Fraction(quotient["schur_residual_squared_lower_exact"]), s_5
        )
        self.assertEqual(Fraction(quotient["beta_l1_upper_exact"]), beta_l1)
        self.assertEqual(
            Fraction(quotient["nonquery_support_maximum_upper_exact"]), tau_w
        )
        self.assertEqual(
            quotient["nonquery_support_maximizers"],
            [n for n in coordinates if complete[n] == tau_w],
        )
        self.assertEqual(
            Fraction(quotient["quotient_support_penalty_upper_exact"]), penalty
        )
        self.assertGreater(positive_numerator, 0)
        self.assertEqual(
            Fraction(quotient["positive_distance_numerator_exact"]),
            positive_numerator,
        )
        self.assertEqual(
            Fraction(quotient["quotient_distance_squared_lower_exact"]),
            distance_squared,
        )
        self.assertEqual(
            Fraction(quotient["four_anchor_critical_radius_squared_lower_exact"]),
            radius_squared,
        )
        alias_radius_squared = upper / 4
        self.assertEqual(
            Fraction(quotient["integral_alias_radius_squared_upper_exact"]),
            alias_radius_squared,
        )
        self.assertLess(radius_squared, alias_radius_squared)
        radical = quotient["four_anchor_critical_radius_lower_outward"]
        radical_lower = Fraction(radical["lower_exact"])
        radical_upper = Fraction(radical["upper_exact"])
        self.assertLessEqual(radical_lower**2, radius_squared)
        self.assertLessEqual(radius_squared, radical_upper**2)
        self.assertTrue(quotient["global_nonquery_prefix_branch_bounded"])
        self.assertFalse(quotient["exact_minimizer_identified"])

    def test_away_from_pole_partition_is_total(self) -> None:
        section = self.payload["away_from_poles"]
        self.assertEqual(section["product_bin_span_exact"], "7/5000")
        self.assertEqual(section["target_log_cell_span_exact"], "1/10000")
        self.assertEqual(section["aligned_frequency_interval_exact"], "3/2000")
        self.assertTrue(section["all_intervals_covered_by_off_pole_or_cap"])
        counts = self.remote["component_unit_cap_interval_counts"]
        self.assertEqual(counts, [618, 247])
        positivity = section["positive_measure_certificate"]
        self.assertTrue(positivity["certified"])
        self.assertEqual(positivity["strict_density_lower_exact"], "9/1000000")
        self.assertEqual(positivity["strict_density_upper_exact"], "5/2")
        self.assertEqual(positivity["lower_boundary_root_count"], 0)
        self.assertEqual(positivity["upper_boundary_root_count"], 0)
        self.assertEqual(positivity["component_weight_numerators"], [125, 65_411])
        self.assertEqual(positivity["component_weight_numerator_sum"], 1 << 16)
        self.assertTrue(positivity["component_weights_nonnegative"])
        self.assertTrue(positivity["all_sample_counts_exceed_window_degree"])
        self.assertTrue(positivity["component_normalization_exact"])

    def test_scope_does_not_overclaim_closest_fibre_or_quadratic_pilot(self) -> None:
        scope = self.payload["scope"]
        negative = self.payload["negative_results"]
        self.assertEqual(
            scope["closest_fibre_status"],
            "global lower/upper radius bracket certified; exact minimizer not identified",
        )
        self.assertFalse(scope["quadratic_cauchy_pilot_included_as_formal_result"])
        self.assertTrue(negative["global_cauchy_route_rejected"])

    def test_rehashed_remote_tamper_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.artifact)
        tampered["payload"]["formal_remote"]["target_numerators"][4] = str(
            int(tampered["payload"]["formal_remote"]["target_numerators"][4]) + 1
        )
        tampered["payload_sha256"] = _sha256(tampered["payload"])
        with self.assertRaises(ValueError):
            verify_artifact(tampered, DEFAULT_SOURCE_PATH, DEFAULT_AO8_PATH)

    def test_unexpected_top_level_field_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.artifact)
        tampered["extra"] = True
        with self.assertRaises(ValueError):
            verify_artifact(tampered, DEFAULT_SOURCE_PATH, DEFAULT_AO8_PATH)

    def test_producer_tamper_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.artifact)
        tampered["producer"]["flint_threads"] = 2
        with self.assertRaises(ValueError):
            verify_artifact(tampered, DEFAULT_SOURCE_PATH, DEFAULT_AO8_PATH)

    def test_boolean_producer_thread_tamper_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.artifact)
        tampered["producer"]["flint_threads"] = True
        with self.assertRaises(ValueError):
            verify_artifact(tampered, DEFAULT_SOURCE_PATH, DEFAULT_AO8_PATH)

    def test_loader_rejects_adversarial_json_and_oversize(self) -> None:
        cases = (
            b'{"a":1,"a":2}\n', b'{"a":1.5}\n', b'{"a":NaN}\n',
            b'{"a":-0}\n', b'\xef\xbb\xbf{"a":1}\n', b'{"a":1}\r\n',
            b'{"a":1}\n\n', b'{"a":1}',
        )
        for raw in cases:
            with self.subTest(raw=raw), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "bad.json"
                path.write_bytes(raw)
                with self.assertRaises(ValueError):
                    _load_json_strict(path, 100)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large.json"
            path.write_bytes(b"{" + b" " * MAX_ARTIFACT_BYTES_AO9 + b"}\n")
            with self.assertRaisesRegex(ValueError, "byte limit"):
                _load_json_strict(path, MAX_ARTIFACT_BYTES_AO9)

    def test_noncanonical_artifact_whitespace_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spaced.json"
            path.write_bytes((json.dumps(self.artifact) + "\n").encode("utf-8"))
            with self.assertRaisesRegex(ValueError, "canonical deterministic"):
                load_artifact(path)


if __name__ == "__main__":
    unittest.main()
