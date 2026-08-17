"""Portable comparison helpers for Tier-1 numerical provenance reports.

The Double-Pendulum Tier-1 artifacts contain floating values produced by
adaptive integration and dense linear algebra.  Their scientific gates have
declared tolerances, but byte-for-byte equality of the descriptive floats is
not portable across Python builds, libm implementations, or BLAS backends.

This module keeps the schema and every non-floating declaration exact while
allowing a deliberately much smaller replay tolerance for finite floats.
Adaptive solver work counters are implementation diagnostics rather than
theorem fields; they must remain positive integers but need not be identical.
"""

from __future__ import annotations

import math


REPLAY_RELATIVE_TOLERANCE = 5.0e-9
REPLAY_ABSOLUTE_TOLERANCE = 5.0e-11
REPLAY_DISCREPANCY_ABSOLUTE_TOLERANCE = 5.0e-14

_VOLATILE_POSITIVE_INTEGER_KEYS = frozenset({"accepted_step_count", "nfev"})


def replay_float_equal(left: float, right: float) -> bool:
    """Compare two finite replay floats at the declared portability scale."""

    return (
        math.isfinite(left)
        and math.isfinite(right)
        and math.isclose(
            left,
            right,
            rel_tol=REPLAY_RELATIVE_TOLERANCE,
            abs_tol=REPLAY_ABSOLUTE_TOLERANCE,
        )
    )


def replay_relative_float_equal(left: float, right: float) -> bool:
    """Compare a nonnegative derived discrepancy near the roundoff floor.

    The absolute term is deliberately far below every scientific acceptance
    threshold in the Tier-1 reports. It prevents a few ulps in a nearly equal
    pair of singular values from becoming a large *relative* replay error,
    while remaining small enough to reject material changes to the stored
    discrepancy itself.
    """

    if not math.isfinite(left) or not math.isfinite(right):
        return False
    scale = max(abs(left), abs(right))
    if scale == 0.0:
        return True
    return abs(left - right) <= max(
        REPLAY_DISCREPANCY_ABSOLUTE_TOLERANCE,
        REPLAY_RELATIVE_TOLERANCE * scale,
    )


def numerically_equivalent_json(left: object, right: object) -> bool:
    """Compare JSON-shaped Tier-1 reports without weakening exact fields.

    Dictionary keys, list lengths, booleans, integers, strings, rational text,
    and all other non-float values remain exact.  Only finite built-in floats
    receive the replay tolerance.  The two adaptive work counters may vary
    between implementations, but both sides must be positive built-in ints.
    """

    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        if left.keys() != right.keys():
            return False
        for key in left:
            left_value = left[key]
            right_value = right[key]
            if key in _VOLATILE_POSITIVE_INTEGER_KEYS:
                if (
                    type(left_value) is not int
                    or type(right_value) is not int
                    or left_value < 1
                    or right_value < 1
                ):
                    return False
                continue
            if not numerically_equivalent_json(left_value, right_value):
                return False
        return True
    if isinstance(left, list):
        return len(left) == len(right) and all(
            numerically_equivalent_json(a, b) for a, b in zip(left, right)
        )
    if isinstance(left, float):
        return replay_float_equal(left, right)
    return left == right
