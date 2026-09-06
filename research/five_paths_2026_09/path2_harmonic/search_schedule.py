#!/usr/bin/env python3
"""Nonformal candidate search; certificate_checker.py supplies the proof."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np

LAM = np.log([2.0, 3.0, 5.0])
TARGETS = [(j, om) for j in range(3) for om in (np.pi / 2, np.pi)]
BASELINE = [90540.692, 220023.423, 27819.627, 94581.299, 18084.130, 75110.287]
CLOCK = 0.001


def majorant(time: float, winding: np.ndarray, axis: int, omega: float,
             clock: float = CLOCK) -> np.ndarray:
    ideal = 2 * np.pi * winding.astype(float)
    ideal[axis] += omega
    error = abs(time * LAM - ideal) + clock * LAM
    result = np.sqrt(5) * error
    result[axis] += 3 * (sum(error) - error[axis])
    return result


def row_optimum(roots: np.ndarray, winding: np.ndarray, axis: int,
                omega: float) -> tuple[float, np.ndarray]:
    # The squared majorant norm is convex and piecewise quadratic. Its
    # minimizer lies between the smallest and largest zero-phase roots.
    breaks = np.unique(roots)
    candidates = list(breaks)
    for lo, hi in zip(breaks[:-1], breaks[1:]):
        sign = np.sign((lo + hi) / 2 - roots)
        slope_e = sign * LAM
        offset_e = -slope_e * roots + CLOCK * LAM
        slope_b, offset_b = np.sqrt(5) * slope_e, np.sqrt(5) * offset_e
        slope_b[axis] += 3 * (sum(slope_e) - slope_e[axis])
        offset_b[axis] += 3 * (sum(offset_e) - offset_e[axis])
        optimum = -np.dot(slope_b, offset_b) / np.dot(slope_b, slope_b)
        candidates.append(float(np.clip(optimum, lo, hi)))
    scored = [(np.linalg.norm(majorant(t, winding, axis, omega)), t)
              for t in candidates]
    _, best = min(scored)
    return best, majorant(best, winding, axis, omega)


def candidate_rows(cap: float, retain: int = 100) -> list[list[dict]]:
    rows = []
    for axis, omega in TARGETS:
        count = int(np.floor((cap * LAM[axis] - omega) / (2 * np.pi))) + 2
        options = []
        for n in range(max(0, count)):
            seed = (omega + 2 * np.pi * n) / LAM[axis]
            ideal_target = np.zeros(3); ideal_target[axis] = omega
            winding = np.rint((seed * LAM - ideal_target) / (2 * np.pi)).astype(int)
            roots = (2 * np.pi * winding + ideal_target) / LAM
            t, b = row_optimum(roots, winding, axis, omega)
            # Only the rounded, realizable time is considered for selection.
            t = round(t, 6)
            if 0 < t <= cap:
                b = majorant(t, winding, axis, omega)
                options.append({'time': t, 'winding': winding.tolist(),
                                'b': b.tolist(), 'row_score': float(np.dot(b, b))})
        rows.append(sorted(options, key=lambda x: x['row_score'])[:retain])
    return rows


def score(schedule: list[dict]) -> float:
    b = np.array([x['b'] for x in schedule])
    return float(np.max(np.sum(b.T @ b, axis=1)))


def solve(cap: float) -> dict:
    options = candidate_rows(cap)
    current = [x[0] for x in options]
    for _ in range(10):
        improved = False
        for row in range(6):
            old_score = score(current)
            best = min(options[row], key=lambda x: score(current[:row] + [x] + current[row + 1:]))
            proposal = current[:row] + [best] + current[row + 1:]
            if score(proposal) + 1e-15 < old_score:
                current = proposal
                improved = True
        if not improved:
            break
    b = np.array([x['b'] for x in current])
    return {'cap': cap, 'clock_radius': CLOCK, 'schedule': current,
            'maximum_time': max(x['time'] for x in current),
            'row_sum_error': float(np.sqrt(score(current))),
            'factor_floor_proxy': float(np.sqrt(2) - np.sqrt(score(current))),
            'spectral_error_diagnostic': float(np.linalg.norm(b, 2))}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--caps', default='1000,2000,3000,4000,5000,7500,10000')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    results = [solve(float(cap)) for cap in args.caps.split(',')]
    report = {'status': 'nonformal discovery; not an optimality claim', 'results': results}
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
