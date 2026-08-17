#!/usr/bin/env python3
"""Adversarial tests for the exact multiplicative-observability artifact."""

from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from arithmetic_observability_multiplicative import (
    AMBIENT_DIMENSION,
    AXIS_COUNT,
    CANONICAL_FACTORS,
    COLLISION_FACTOR_MINUS,
    COLLISION_FACTOR_PLUS,
    EXPONENTS_PER_AXIS,
    FREE_SCALE_LEFT,
    FREE_SCALE_RIGHT,
    MAX_ARTIFACT_BYTES,
    SCHEMA,
    SELECTED_AXES,
    TV_EPSILON_A,
    TV_EPSILON_B,
    UNIFORM_FACTOR,
    _canonical_json,
    _determinant,
    _dot,
    _read_artifact,
    build_artifact,
    calibrated_projector_apply,
    complementary_marginal,
    exponent_states,
    free_scale_geometric_tensor,
    reconstruct_product_from_two_marginals,
    tangent_pullback_gram,
    tangent_source_metric,
    tensor_product,
    total_variation,
    uniform_tangent_columns,
    verify_artifact,
)


ARTIFACT_PATH = Path("arithmetic_observability_multiplicative_certificate.json")
PINNED_PAYLOAD_SHA256 = "5805a3f385a6b5a0728d38413c9a0cb76d15b59285f671021ff749a6c4ea6a24"


def _rehash(artifact: dict[str, object]) -> None:
    artifact["payload_sha256"] = hashlib.sha256(
        _canonical_json(artifact["payload"])
    ).hexdigest()


class MultiplicativeObservabilityCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.built = build_artifact()

    def test_pinned_artifact_matches_exact_reconstruction(self) -> None:
        stored = _read_artifact(ARTIFACT_PATH)
        self.assertEqual(stored, self.built)
        self.assertEqual(stored["payload_sha256"], PINNED_PAYLOAD_SHA256)
        verification = verify_artifact(stored)
        self.assertTrue(verification["verified"])
        self.assertTrue(verification["overall_passed"])

    def test_complementary_marginal_identity_is_exact(self) -> None:
        factors = [list(factor) for factor in CANONICAL_FACTORS]
        tensor = tensor_product(factors)
        self.assertEqual(len(tensor), AMBIENT_DIMENSION)
        for axis in range(AXIS_COUNT):
            self.assertEqual(
                complementary_marginal(
                    tensor, AXIS_COUNT, EXPONENTS_PER_AXIS, axis
                ),
                tensor_product(factors[:axis] + factors[axis + 1 :]),
            )

    def test_scalar_marginal_helper_scope_is_explicit(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least two axes"):
            complementary_marginal(
                [Fraction(1), Fraction(0)], 1, 2, 0
            )

    def test_dot_rejects_silent_dimension_truncation(self) -> None:
        with self.assertRaisesRegex(ValueError, "different dimensions"):
            _dot([Fraction(1)], [Fraction(1), Fraction(2)])

    def test_vertex_products_exhaustively_check_axis_indexing(self) -> None:
        s = EXPONENTS_PER_AXIS
        for alpha in exponent_states(AXIS_COUNT, s):
            factors = []
            for state in alpha:
                factor = [Fraction(0) for _ in range(s)]
                factor[state] = Fraction(1)
                factors.append(factor)
            tensor = tensor_product(factors)
            for axis in range(AXIS_COUNT):
                expected = tensor_product(factors[:axis] + factors[axis + 1 :])
                self.assertEqual(
                    complementary_marginal(tensor, AXIS_COUNT, s, axis),
                    expected,
                )

    def test_every_two_axis_pair_reconstructs_all_factors(self) -> None:
        factors = [list(factor) for factor in CANONICAL_FACTORS]
        tensor = tensor_product(factors)
        marginals = {
            axis: complementary_marginal(
                tensor, AXIS_COUNT, EXPONENTS_PER_AXIS, axis
            )
            for axis in range(AXIS_COUNT)
        }
        for left in range(AXIS_COUNT):
            for right in range(left + 1, AXIS_COUNT):
                recovered, reconstructed = reconstruct_product_from_two_marginals(
                    {left: marginals[left], right: marginals[right]},
                    AXIS_COUNT,
                    EXPONENTS_PER_AXIS,
                )
                self.assertEqual(recovered, factors)
                self.assertEqual(reconstructed, tensor)

    def test_two_axis_reconstruction_includes_boundary_points(self) -> None:
        point = [Fraction(1), Fraction(0), Fraction(0), Fraction(0)]
        factors = [point, list(CANONICAL_FACTORS[1]), point]
        tensor = tensor_product(factors)
        marginals = {
            axis: complementary_marginal(
                tensor, AXIS_COUNT, EXPONENTS_PER_AXIS, axis
            )
            for axis in SELECTED_AXES
        }
        recovered, reconstructed = reconstruct_product_from_two_marginals(
            marginals, AXIS_COUNT, EXPONENTS_PER_AXIS
        )
        self.assertEqual(recovered, factors)
        self.assertEqual(reconstructed, tensor)

    def test_one_marginal_is_rejected_as_insufficient_for_reconstruction(self) -> None:
        tensor = tensor_product(CANONICAL_FACTORS)
        marginal = complementary_marginal(
            tensor, AXIS_COUNT, EXPONENTS_PER_AXIS, 0
        )
        with self.assertRaisesRegex(ValueError, "exactly two"):
            reconstruct_product_from_two_marginals(
                {0: marginal}, AXIS_COUNT, EXPONENTS_PER_AXIS
            )

    def test_probability_collision_is_exact_and_nontrivial(self) -> None:
        plus = tensor_product(
            [COLLISION_FACTOR_PLUS, UNIFORM_FACTOR, UNIFORM_FACTOR]
        )
        minus = tensor_product(
            [COLLISION_FACTOR_MINUS, UNIFORM_FACTOR, UNIFORM_FACTOR]
        )
        self.assertNotEqual(plus, minus)
        self.assertEqual(
            complementary_marginal(plus, 3, 4, 0),
            complementary_marginal(minus, 3, 4, 0),
        )
        self.assertNotEqual(
            complementary_marginal(plus, 3, 4, 1),
            complementary_marginal(minus, 3, 4, 1),
        )
        self.assertEqual(total_variation(plus, minus), Fraction(1, 4))
        delta = [left - right for left, right in zip(plus, minus)]
        self.assertEqual(sum(value * value for value in delta), Fraction(1, 128))

    def test_free_scale_exceptional_collision_and_k_membership(self) -> None:
        left = free_scale_geometric_tensor(*FREE_SCALE_LEFT)
        right = free_scale_geometric_tensor(*FREE_SCALE_RIGHT)
        self.assertNotEqual(left, right)
        difference = [a - b for a, b in zip(left, right)]
        for axis in range(AXIS_COUNT):
            self.assertEqual(
                complementary_marginal(left, 3, 4, axis),
                complementary_marginal(right, 3, 4, axis),
            )
            self.assertEqual(
                complementary_marginal(difference, 3, 4, axis),
                [Fraction(0)] * 16,
            )
        self.assertEqual(sum(value * value for value in difference), 4480)

    def test_free_scale_collision_records_root_of_unity_factorization(self) -> None:
        section = self.built["payload"]["free_scale_exceptional_collision"]
        self.assertEqual(section["geometric_sums_left"], [1, 0, 0])
        self.assertEqual(section["geometric_sums_right"], [15, 0, 0])
        self.assertEqual(section["scaled_geometric_sums_left"], [15, 0, 0])
        self.assertEqual(section["scaled_geometric_sums_right"], [15, 0, 0])
        self.assertEqual(section["difference_factor_sums"], [0, 0, 0])
        self.assertTrue(section["difference_in_full_mean_zero_interaction"])

    def test_sharp_total_variation_modulus_witness(self) -> None:
        section = self.built["payload"]["sharp_tv_witness"]
        d_a = Fraction(section["margin_tv_d_a"])
        d_b = Fraction(section["margin_tv_d_b"])
        source = Fraction(section["source_total_variation"])
        self.assertEqual(d_a, Fraction(1, 4))
        self.assertEqual(d_b, Fraction(1, 3))
        self.assertEqual(source, d_a + d_b - d_a * d_b)
        self.assertEqual(source, Fraction(1, 2))
        self.assertTrue(section["sharp_modulus_equality_verified"])

    def test_common_midpoint_minimax_lower_witness(self) -> None:
        section = self.built["payload"]["sharp_tv_witness"]
        distances = [Fraction(value) for value in section["common_midpoint_endpoint_distances"]]
        self.assertEqual(
            distances,
            [TV_EPSILON_A, TV_EPSILON_A, TV_EPSILON_B, TV_EPSILON_B],
        )
        formula = TV_EPSILON_A + TV_EPSILON_B - 2 * TV_EPSILON_A * TV_EPSILON_B
        self.assertEqual(Fraction(section["half_source_total_variation"]), formula)
        self.assertEqual(formula, Fraction(1, 4))
        self.assertTrue(section["common_midpoint_lower_witness_verified"])

    def test_uniform_tangent_source_metric_is_positive_and_exact(self) -> None:
        metric = tangent_source_metric(3, 4)
        self.assertEqual(len(metric), 9)
        self.assertEqual(_determinant(metric), Fraction(1, 2**30))
        section = self.built["payload"]["uniform_product_tangent_geometry"]
        self.assertEqual(section["source_metric_determinant"], "1/1073741824")
        self.assertEqual(section["factor_tangent_dimension"], 9)

    def test_calibrated_projectors_have_exact_factor_block_action(self) -> None:
        columns = uniform_tangent_columns(3, 4)
        for observed_axis in range(3):
            for factor_axis in range(3):
                block = columns[factor_axis * 3 : (factor_axis + 1) * 3]
                images = [
                    calibrated_projector_apply(column, 3, 4, observed_axis)
                    for column in block
                ]
                if observed_axis == factor_axis:
                    self.assertEqual(images, [[Fraction(0)] * 64 for _ in range(3)])
                else:
                    self.assertEqual(images, block)

    def test_all_three_uniform_tangent_spectrum(self) -> None:
        design = self.built["payload"]["uniform_product_tangent_geometry"]["designs"]["all_three_uniform"]
        self.assertEqual(design["factor_block_generalized_eigenvalues"], ["2/3"] * 3)
        self.assertEqual(
            design["generalized_spectrum"],
            [{"eigenvalue": "2/3", "multiplicity": 9}],
        )
        self.assertEqual(design["generalized_floor"], "2/3")
        self.assertEqual(design["tangent_rank"], 9)

    def test_two_axis_half_tangent_spectrum(self) -> None:
        design = self.built["payload"]["uniform_product_tangent_geometry"]["designs"]["two_axis_half"]
        self.assertEqual(design["factor_block_generalized_eigenvalues"], ["1/2", "1/2", "1/1"])
        self.assertEqual(
            design["generalized_spectrum"],
            [
                {"eigenvalue": "1/2", "multiplicity": 6},
                {"eigenvalue": "1/1", "multiplicity": 3},
            ],
        )
        self.assertEqual(design["generalized_floor"], "1/2")
        self.assertEqual(design["tangent_rank"], 9)

    def test_one_axis_tangent_kernel_matches_hidden_factor(self) -> None:
        design = self.built["payload"]["uniform_product_tangent_geometry"]["designs"]["one_axis"]
        self.assertEqual(design["factor_block_generalized_eigenvalues"], ["0/1", "1/1", "1/1"])
        self.assertEqual(design["generalized_floor"], "0/1")
        self.assertEqual(design["tangent_rank"], 6)
        self.assertEqual(
            design["generalized_spectrum"],
            [
                {"eigenvalue": "0/1", "multiplicity": 3},
                {"eigenvalue": "1/1", "multiplicity": 6},
            ],
        )

    def test_invalid_tangent_weights_are_rejected_exactly(self) -> None:
        with self.assertRaisesRegex(ValueError, "sum exactly"):
            tangent_pullback_gram(
                [Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)], 3, 4
            )
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            tangent_pullback_gram(
                [Fraction(1), Fraction(1), Fraction(-1)], 3, 4
            )

    def test_stale_digest_tampering_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["sharp_tv_witness"]["source_total_variation"] = "1/3"
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            verify_artifact(tampered)

    def test_rehashed_semantic_tampering_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["uniform_product_tangent_geometry"]["designs"]["two_axis_half"]["generalized_floor"] = "1/3"
        _rehash(tampered)
        with self.assertRaisesRegex(ValueError, "independent exact reconstruction"):
            verify_artifact(tampered)

    def test_numeric_alias_tampering_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["parameters"]["prime_axes"][0] = 2.0
        _rehash(tampered)
        with self.assertRaisesRegex(ValueError, "floating-point"):
            verify_artifact(tampered)

    def test_noncanonical_fraction_tampering_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["normalized_product_reconstruction"]["canonical_factors"][0][0] = "2/20"
        _rehash(tampered)
        with self.assertRaisesRegex(ValueError, "reduced and canonical"):
            verify_artifact(tampered)

    def test_metric_shape_resource_cap_is_enforced(self) -> None:
        tampered = copy.deepcopy(self.built)
        tampered["payload"]["uniform_product_tangent_geometry"]["source_metric_coordinate_matrix"].append(["0/1"] * 9)
        _rehash(tampered)
        with self.assertRaisesRegex(ValueError, "dimension cap"):
            verify_artifact(tampered)

    def test_unknown_top_level_and_payload_fields_are_rejected(self) -> None:
        top = copy.deepcopy(self.built)
        top["comment"] = "not covered by the digest"
        with self.assertRaisesRegex(ValueError, "unexpected top-level"):
            verify_artifact(top)
        nested = copy.deepcopy(self.built)
        nested["payload"]["comment"] = "not covered by the schema"
        _rehash(nested)
        with self.assertRaisesRegex(ValueError, "payload has unexpected"):
            verify_artifact(nested)

    def test_duplicate_json_keys_are_rejected_at_file_boundary(self) -> None:
        text = (
            '{"schema":"attacker","schema":"'
            + SCHEMA
            + '","payload":{},"payload_sha256":"'
            + "0" * 64
            + '"}'
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON object key"):
                _read_artifact(path)

    def test_nonfinite_json_numbers_are_rejected_at_file_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nonfinite.json"
            path.write_text('{"value":NaN}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-finite JSON constant"):
                _read_artifact(path)

    def test_negative_zero_is_rejected_at_file_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "negative-zero.json"
            path.write_text('{"value":-0}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "negative-zero"):
                _read_artifact(path)

    def test_json_floats_are_rejected_at_file_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "float.json"
            path.write_text('{"value":2.0}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "floating-point"):
                _read_artifact(path)

    def test_oversized_file_is_rejected_before_json_parsing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "oversized.json"
            path.write_text(" " * (MAX_ARTIFACT_BYTES + 1), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "serialized resource cap"):
                _read_artifact(path)

    def test_oversized_integer_literal_is_rejected_lexically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "huge-integer.json"
            path.write_text('{"value":' + "1" * 81 + "}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "integer literal"):
                _read_artifact(path)

    def test_invalid_utf8_is_rejected_canonically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid-utf8.json"
            path.write_bytes(b'{"value":"\xff"}')
            with self.assertRaisesRegex(ValueError, "canonical UTF-8"):
                _read_artifact(path)

    def test_cli_write_is_byte_deterministic(self) -> None:
        root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rebuilt.json"
            subprocess.run(
                [
                    sys.executable,
                    str(root / "arithmetic_observability_multiplicative.py"),
                    "--write",
                    str(path),
                ],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(path.read_bytes(), ARTIFACT_PATH.read_bytes())
            self.assertNotIn(b"\r\n", path.read_bytes())

    def test_schema_and_digest_are_exactly_pinned(self) -> None:
        self.assertEqual(self.built["schema"], SCHEMA)
        self.assertEqual(self.built["payload_sha256"], PINNED_PAYLOAD_SHA256)
        tampered = copy.deepcopy(self.built)
        tampered["schema"] = f"{SCHEMA}-future"
        with self.assertRaisesRegex(ValueError, "unsupported"):
            verify_artifact(tampered)


if __name__ == "__main__":
    unittest.main()
