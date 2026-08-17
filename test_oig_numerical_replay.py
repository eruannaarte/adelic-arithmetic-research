import unittest

from oig_numerical_replay import (
    numerically_equivalent_json,
    replay_float_equal,
    replay_relative_float_equal,
)


class NumericalReplayComparisonTests(unittest.TestCase):
    def test_roundoff_scale_float_drift_is_portable(self) -> None:
        self.assertTrue(replay_float_equal(1.0, 1.0 + 1.0e-10))
        self.assertTrue(
            numerically_equivalent_json(
                {"response": [0.0, 2.0]},
                {"response": [2.0e-11, 2.0 + 2.0e-10]},
            )
        )

    def test_material_numeric_tampering_is_rejected(self) -> None:
        self.assertFalse(replay_float_equal(1.0, 1.0 + 1.0e-5))
        self.assertFalse(
            numerically_equivalent_json(
                {"response": [0.0, 2.0]},
                {"response": [0.0, 2.0 + 1.0e-4]},
            )
        )
        self.assertFalse(replay_relative_float_equal(1.0e-13, 2.0e-13))

    def test_tiny_discrepancy_has_a_narrow_roundoff_floor(self) -> None:
        self.assertTrue(replay_relative_float_equal(2.50e-12, 2.52e-12))

    def test_schema_and_exact_types_remain_strict(self) -> None:
        self.assertFalse(numerically_equivalent_json({"rank": 1}, {"rank": True}))
        self.assertFalse(numerically_equivalent_json({"rank": 1}, {"rank": 1.0}))
        self.assertFalse(numerically_equivalent_json({"a": 1}, {"b": 1}))

    def test_only_positive_adaptive_work_counters_may_vary(self) -> None:
        self.assertTrue(
            numerically_equivalent_json(
                {"nfev": 100, "accepted_step_count": 20},
                {"nfev": 112, "accepted_step_count": 21},
            )
        )
        self.assertFalse(
            numerically_equivalent_json({"nfev": 100}, {"nfev": 0})
        )
        self.assertFalse(
            numerically_equivalent_json({"other_count": 100}, {"other_count": 101})
        )


if __name__ == "__main__":
    unittest.main()
