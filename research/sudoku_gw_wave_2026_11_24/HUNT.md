# Hunting for a puzzle where one lift fails (2026-11-24)

**Goal.** Find a uniquely solvable puzzle where one vector lift (the SDP of `gw_wave.py` /
`gw_scale.py`) does **not** force the answer. Theory says such puzzles must exist at large sizes
unless P = NP.

**Result: none found.** Across every hunt, 102 more uniquely solvable puzzles needed a lift, and
one lift forced every one of them. A "genuine failure" would have needed all of the following:
- the lift's solver converged (status optimal),
- its matrix passed the feasibility checks (PSD, constraints met, entries ≥ 0),
- the forcing audit showed real room for wrong beliefs (> 0.01),
- and all of that held again when re-solved at 100× tighter tolerance.

No puzzle reached even the first suspicion threshold. The largest audit value in the whole hunt
was 1.5e-4.

## The hunts

| Hunt | How puzzles were made | Needed a lift | Forced | Hardest for search |
|---|---|---:|---:|---:|
| Bred 9×9 Sudoku (`hunt.py`, `evaluate.py`) | 6 hill-climbers × 30 min mutating clue sets; 3 maximized backtracking guesses, 3 maximized the LP's forcing gap; 2 started from Easter Monster / Inkala | 34 | 34 | 677 guesses (Easter Monster itself; best bred relative 405) |
| Random Latin squares 8–11 (`latin.py`) | random Latin square, clues removed while unique (minimal) | 32 of 60 | 32 | 28 guesses |
| Bred Latin squares 9, 10 (`hunt.py … latinN`, `eval_latin.py`) | 4 hill-climbers × 25 min | 36 | 36 | 240 guesses |

Some bred puzzles differ in their clues but reduce to the same grid after propagation. Those
are counted separately above; distinct lifted problems: 28 bred Sudoku, 32 random Latin,
30 bred Latin. Together with the earlier runs (38 at 9×9, 5 at 16×16, 3 at 25×25), **148
puzzles needed a lift, and one lift forced all 148.**

## What the hunt taught us

1. **Hard for search ≠ hard for the lift.** The bred Latin squares that cost backtracking 240
   guesses were forced not only by the lift but even by the plain LP (wrong mass 0), in about
   2 s and only 275 solver steps. Our climbers optimized the wrong kind of hardness. Search
   difficulty (how badly guessing goes) and relaxation difficulty (whether fractional "ghost"
   solutions exist) are different properties.
2. **The LP-gap climbers did find relaxation-hard puzzles, but only for the LP.** Puzzles bred
   to maximize the LP's room for wrong beliefs (up to 55 cells' worth) were still forced by the
   vector lift. The extra vector geometry (positive semidefiniteness plus orthogonality of
   clashing claims) closes those gaps every time we have seen.
3. **Where solver effort concentrates.** Across Sudoku, the solver steps a lift needed tracked
   search difficulty: Easter Monster took 10,900 steps, its 405-guess relative 18,850, and easy
   puzzles a few hundred. The lift pays for hardness in convergence time, not in correctness.

## Why we still believe failures exist, and where to look next

- Each lift runs in polynomial time. If one lift forced every uniquely solvable N×N Sudoku or
  Latin square, unique-solution Latin-square completion would be in polynomial time, which is
  not believed possible. (The precise statement involves "promise" versions of NP; the
  intuition is that P ≠ NP rules it out.) So failures should exist. They are just not found by
  random generation or by climbing on search difficulty at the sizes a laptop can lift.
- **Climbing directly on the lift's own forcing gap** is the honest next hunt. It is about 100×
  more expensive per step, but it optimizes the right hardness.
- **Theory-backed adversaries.** For constraint problems built from parity (random 3-XOR) or
  Tseitin formulas on expander graphs, it is *proven* that low-degree sum-of-squares relaxations
  (the family this lift belongs to) cannot refute them, while Gaussian elimination solves them
  instantly. Testing the lift's CSP version on random 3-XOR would show the wall directly: a lift
  that fails, next to a simple algorithm that succeeds.

## Reproduce

```bash
P=/Volumes/KINGSTON/Vibecoding/.venvs/sdp/bin/python
$P hunt.py guesses 21 1800 hunt/g_easter.json easter          # one Sudoku climber
$P evaluate.py 0 1 8 hunt/eval.json hunt/g_easter.json        # lift + audit on its best 8
$P latin.py 10 15 101 latin/latin10.json                      # random 10x10 Latin squares
$P hunt.py guesses 32 1500 latin/g10.json latin10              # Latin climber
$P eval_latin.py 10 0 1 10 latin/eval10.json latin/g10.json   # lift + audit on bred Latin
```

Data: `hunt/` (Sudoku climbers and evaluations) and `latin/` (Latin squares), each with logs.
