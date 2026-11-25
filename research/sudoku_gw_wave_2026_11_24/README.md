# Goemans–Williamson "wave" on Sudoku (2026-11-24)

> Scaling follow-up (16×16 and 25×25): see [SCALING.md](SCALING.md).
> Hunt for a failure (bred hard Sudokus, Latin squares): see [HUNT.md](HUNT.md).

**Question.** Lift Sudoku onto a high-dimensional sphere (one unit vector per cell–digit
claim), solve the smooth problem, project back down to digits, and repeat if needed. Does the
answer "pop out" without searching?

**Answer on these 24 puzzles: yes, in one lift, every time.** Simple propagation solves 8 of
them outright. For each of the other 16, including Inkala's 2012 "world's hardest" and Easter
Monster, the first lift's beliefs were already 0/1 and matched the solution. No down-and-up
cycles or guesses were needed. A random-hyperplane GW rounding of the same vectors drew the exact
solution in 3,192 of 3,200 draws.

## Method (`gw_wave.py`)

- **Lift**: Gram matrix of vectors v_0 and v_{i,d}, positive semidefinite and entrywise ≥ 0.
  |v_{i,d}|² = v_0·v_{i,d}. One digit per cell and each digit once per row/column/box (as sums of
  v_0·v_{i,d}). Clashing claims (same cell, or same digit in peer cells) are orthogonal. Solver:
  SCS, tolerance 1e-5. A heavier variant with "lifted" sum rules gave the same answers about 100×
  slower and was dropped.
- **Down**: (a) GW hyperplane rounding on the ±1 vectors u = 2v − v_0. (b) The wave: fix every
  claim the lift is sure of (belief > 0.99), propagate in the ordinary grid, lift again, and
  branch only if nothing pops out.
- **Controls**: propagation alone (naked + hidden singles); the same rules as a plain **LP**
  (beliefs, no vectors) solved to a central point; and backtracking with propagation, which is
  also the source of truth and of the uniqueness check.
- **Forcing audit** (uses the known answer, only for evaluation): the largest total belief each
  relaxation can place on wrong claims. A value of 0 means the relaxation allows nothing but the
  solution, so the answer is forced, not landed on by luck.
- Every lift starts from the grid after cheap propagation.

## Results (16 puzzles that needed a lift)

| Puzzle | Free cells | Backtracking guesses / ms | LP max wrong mass | LP wave lifts / guesses | SDP max wrong mass | SDP lift (s) |
|---|---:|---:|---:|---:|---:|---:|
| generated-30-2 | 29 | 2 / 0.6 | 15.5 | 3 / 3 | ≈0 | 0.2 |
| generated-min-1 | 47 | 6 / 1.4 | 32.7 | 14 / 10 | ≈0 | 4.2 |
| generated-min-4 | 35 | 4 / 1.0 | 21.0 | 6 / 6 | ≈0 | 0.6 |
| norvig-hardest-1 | 48 | 8 / 1.7 | 0 | 1 / 0 | ≈0 | 0.6 |
| norvig-hardest-2 | 56 | 56 / 8.3 | 48.2 | 26 / 20 | ≈0 | 52.0 |
| norvig-hardest-3 | 48 | 12 / 2.3 | 37.0 | 29 / 24 | ≈0 | 6.3 |
| norvig-hardest-4 | 53 | 44 / 6.1 | 0 | 1 / 0 | ≈0 | 1.6 |
| norvig-hardest-6 | 57 | 142 / 16.7 | 51.3 | 81 / 63 | 4e-4 | 58.5 |
| norvig-hardest-7 | 39 | 6 / 1.1 | 24.0 | 3 / 1 | ≈0 | 1.1 |
| norvig-hardest-8 | 35 | 10 / 1.3 | 22.5 | 8 / 8 | ≈0 | 0.7 |
| norvig-hardest-9 | 52 | 4 / 1.0 | 0 | 1 / 0 | ≈0 | 1.6 |
| norvig-hardest-10 | 46 | 8 / 1.3 | 30.0 | 7 / 7 | ≈0 | 2.4 |
| norvig-hardest-11 | 59 | 32 / 5.5 | 36.3 | 17 / 16 | ≈0 | 11.5 |
| inkala-2012 | 60 | 320 / 46.0 | 44.5 | 25 / 19 | ≈0 | 19.5 |
| easter-monster | 60 | 677 / 76.2 | 54.8 | 108 / 72 | 1e-4 | 65.7 |
| norvig-grid2 (17 clues) | 61 | 100 / 10.8 | 0 | 1 / 0 | ≈0 | 5.9 |

"≈0" means below 4e-5. The largest SDP value, 4.3e-4, is within solver precision. The SDP wave
solved all 16 with 1 lift and 0 guesses.

## What this does and does not show

- **It shows** that, on these puzzles, the vector lift captures enough global consistency to
  force the unique solution. The LP over the same rules usually cannot, so the vectors and their
  geometry are doing real work. In the terms of the Oct 27 thread, the lift computes the "global
  compatibility relation" K that the local Hall rules lacked.
- **It is not faster.** Backtracking took 0.6–76 ms; the lift took 0.2–66 s.
- **It says nothing about P vs NP yet.** These are fixed 9×9 puzzles. Sudoku is NP-complete only
  as the grid grows (n²×n²). Any fixed-level relaxation like this must fail on some large
  instances unless P = NP. The real test is how the forcing behaves on 16×16, 25×25, ... grids.
- **It is numerical, not a proof.** "Forced" holds up to solver tolerance. An exact rational
  certificate (a dual witness) would make each one-lift solution a checked proof.
- **The technique itself is known.** Solving Sudoku with a single LP or SDP call appears, for
  example, as a university optimization exercise
  (https://www.math.uni-konstanz.de/~schweigh/12/polopt-prog03.pdf). The forcing audit and the
  side-by-side comparison with the LP are this experiment's contribution.

## Reproduce

```bash
python3 -m venv /Volumes/KINGSTON/Vibecoding/.venvs/sdp
/Volumes/KINGSTON/Vibecoding/.venvs/sdp/bin/pip install cvxpy scipy numpy
/Volumes/KINGSTON/Vibecoding/.venvs/sdp/bin/python gw_wave.py            # about 10 minutes
/Volumes/KINGSTON/Vibecoding/.venvs/sdp/bin/python gw_wave.py inkala-2012   # one puzzle
```

Outputs: `results.json` (every number above) and `run.log`. The generated puzzles use seed 20261124.
