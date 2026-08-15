import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import unittest

from arithmetic_observability_prime_box import (
    build_artifact,
    build_payload,
    marginal_projector,
    pooled_gram,
    predicted_spectrum,
    pure_distance_squared,
    validate_parameters,
    verify_artifact,
)


def matmul(a, b):
    return [
        [
            sum((a[i][k] * b[k][j] for k in range(len(b))), Fraction(0))
            for j in range(len(b[0]))
        ]
        for i in range(len(a))
    ]


class PrimeBoxObservabilityTests(unittest.TestCase):
    def test_pinned_artifact_matches_exact_builder(self):
        path = Path("arithmetic_observability_prime_box_certificate.json")
        stored = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(stored, build_artifact())
        result = verify_artifact(stored)
        self.assertEqual(
            result["payload_sha256"],
            "3fe7461250815719b4e80c9ad73dc04325f7fb13e8fa0dd83f0906c9505dcc56",
        )

    def test_projectors_are_exactly_idempotent(self):
        for axis in range(3):
            projector = marginal_projector(3, 3, axis)
            self.assertEqual(matmul(projector, projector), projector)

    def test_projectors_commute(self):
        p0 = marginal_projector(3, 2, 0)
        p1 = marginal_projector(3, 2, 1)
        self.assertEqual(matmul(p0, p1), matmul(p1, p0))

    def test_uniform_three_axis_geometry(self):
        payload = build_payload()
        geometry = payload["exact_geometry"]
        self.assertEqual(geometry["ambient_dimension"], 64)
        self.assertEqual(geometry["observable_rank"], 37)
        self.assertEqual(geometry["common_kernel_dimension"], 27)
        self.assertEqual(geometry["simplex_tangent_quotient_dimension"], 36)
        self.assertEqual(geometry["positive_spectral_floor"], "1/3")
        self.assertEqual(geometry["minimax_noise_amplification_squared"], "3/1")

    def test_spectrum_multiplicities_sum_to_dimension(self):
        entries = predicted_spectrum((Fraction(1, 3),) * 3, 4)
        self.assertEqual(sum(entry["multiplicity"] for entry in entries), 64)
        zero_multiplicity = sum(
            entry["multiplicity"]
            for entry in entries
            if entry["eigenvalue"] == "0/1"
        )
        self.assertEqual(zero_multiplicity, 27)

    def test_nonuniform_floor_is_smallest_weight(self):
        weights = (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
        payload = build_payload((2, 3, 5), 3, weights)
        self.assertEqual(payload["exact_geometry"]["positive_spectral_floor"], "1/6")

    def test_pure_distance_rule(self):
        weights = (Fraction(1, 3),) * 3
        self.assertEqual(
            pure_distance_squared((0, 0, 0), (1, 0, 0), 4, weights),
            Fraction(1, 3),
        )
        self.assertEqual(
            pure_distance_squared((0, 0, 0), (1, 1, 0), 4, weights),
            Fraction(1, 2),
        )
        self.assertEqual(
            pure_distance_squared((0, 0, 0), (1, 1, 1), 4, weights),
            Fraction(1, 2),
        )

    def test_collision_is_exact(self):
        artifact = build_artifact()
        collision = artifact["payload"]["exact_probability_collision"]
        self.assertEqual(collision["pooled_distance_squared"], "0/1")
        self.assertEqual(collision["difference_l2_squared"], "1/512")
        self.assertEqual(collision["difference_total_variation"], "1/16")

    def test_gram_is_symmetric(self):
        gram = pooled_gram((2, 3), 3, (Fraction(2, 5), Fraction(3, 5)))
        self.assertEqual(gram, [list(row) for row in zip(*gram)])

    def test_artifact_round_trip(self):
        result = verify_artifact(build_artifact())
        self.assertTrue(result["verified"])
        self.assertEqual(result["observable_rank"], 37)

    def test_tampered_payload_is_rejected_even_with_stale_hash(self):
        artifact = build_artifact()
        artifact["payload"]["exact_geometry"]["observable_rank"] = 38
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            verify_artifact(artifact)

    def test_tampered_payload_is_rejected_with_recomputed_hash(self):
        artifact = build_artifact()
        tampered = copy.deepcopy(artifact)
        tampered["payload"]["exact_geometry"]["observable_rank"] = 38
        canonical = json.dumps(
            tampered["payload"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
        tampered["payload_sha256"] = hashlib.sha256(canonical).hexdigest()
        with self.assertRaisesRegex(ValueError, "exact reconstruction"):
            verify_artifact(tampered)

    def test_numeric_alias_tampering_is_rejected(self):
        artifact = build_artifact()
        artifact["payload"]["parameters"]["primes"][0] = 2.0
        canonical = json.dumps(
            artifact["payload"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
        artifact["payload_sha256"] = hashlib.sha256(canonical).hexdigest()
        with self.assertRaisesRegex(ValueError, "canonical JSON types"):
            verify_artifact(artifact)

    def test_unknown_top_level_field_is_rejected(self):
        artifact = build_artifact()
        artifact["comment"] = "not part of the proof schema"
        with self.assertRaisesRegex(ValueError, "unexpected"):
            verify_artifact(artifact)

    def test_invalid_prime_axes_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "distinct primes"):
            validate_parameters((2, 2), 3, (Fraction(1, 2), Fraction(1, 2)))
        with self.assertRaisesRegex(ValueError, "distinct primes"):
            validate_parameters((2, 9), 3, (Fraction(1, 2), Fraction(1, 2)))

    def test_invalid_weights_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "positive"):
            validate_parameters((2, 3), 3, (Fraction(1), Fraction(0)))
        with self.assertRaisesRegex(ValueError, "sum"):
            validate_parameters((2, 3), 3, (Fraction(1, 3), Fraction(1, 3)))

    def test_invalid_box_size_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least two"):
            validate_parameters((2, 3), 1, (Fraction(1, 2), Fraction(1, 2)))

    def test_oversized_formal_models_are_rejected_before_reconstruction(self):
        with self.assertRaisesRegex(ValueError, "dimension limit"):
            validate_parameters(
                (2, 3, 5, 7, 11),
                4,
                (Fraction(1, 5),) * 5,
            )
        with self.assertRaisesRegex(ValueError, "integer limit"):
            validate_parameters(
                (2, 1_000_003),
                2,
                (Fraction(1, 2), Fraction(1, 2)),
            )


if __name__ == "__main__":
    unittest.main()
