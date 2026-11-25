# A hybrid "wave": geometry and finite-field algebra taking turns (2026-11-24)

**Question.** Geometric lifts (like the vector lift that solved every Sudoku in
`../sudoku_gw_wave_2026_11_24`) and algebra over finite fields (Gaussian elimination and its
higher-degree versions) are each strong where the other is weak. If they take turns, passing what
each has derived to the other, can the pair solve problems neither can solve alone? And where does
the pair still fail?

**Answer.**
- **Yes, when the problem has separate parts with a narrow link between them.** On a problem
  whose parity half switches on a counting half through one variable, the wave won in one round
  at degree 1, for every size tried. Neither engine could solve it alone at that cost.
- **No on random 3-SAT.** Neither engine could derive even one fact, so there was nothing to pass
  back and forth. The wave stalled immediately.

## The two engines (`engines.py`)

Both work on the same 0/1 problems (clauses, parity equations, "exactly one" and "at most one"
rules).

- **Algebra:** degree-d *Polynomial Calculus* over the two-element field F₂ (where 1 + 1 = 0).
  Each rule becomes polynomial equations. The engine takes all their sums, and multiplies them by
  variables, as long as the degree stays ≤ d. That is Gaussian elimination on a matrix whose
  columns are all monomials of degree ≤ d. It **refutes** the problem if it derives 1 = 0. It
  **forces** a variable if it derives x = 0 or x = 1. Degree 1 is ordinary Gaussian elimination.
- **Geometry:** the vector lift. It uses a positive semidefinite moment matrix over (1, x₁, …, xₙ),
  with x² = x, pairwise bounds, and the linear rules multiplied by each variable. Every small rule
  also gets a local probability distribution that must agree with the matrix. It **refutes** the
  problem if this is infeasible, and **forces** a variable if fixing it the other way is
  infeasible. Solver: Clarabel (interior point).
- **The wave:** run the algebra, hand its new facts (x = a, x = y, x = 1 − y) to the geometry, run
  the geometry, hand its new facts back, and repeat. Stop on a refutation or when no new facts
  appear.

## Results (`run_all.py`; data in `results_*.json`, logs in `run_*.log`)

**1. Pigeons: n+1 pigeons, n holes, one pigeon per hole (impossible). Counting wins.**

| Pigeons → holes | 3→2 | 4→3 | 5→4 | 6→5 | 7→6 | 8→7 |
|---|---:|---:|---:|---:|---:|---:|
| Algebra: lowest degree that refutes | 2 | 3 | 3 | 4 | 4 | > 3 (degree 4 too big) |
| Geometry: refutes? (time) | yes, 0.01 s | yes, 0.02 s | yes, 0.04 s | yes, 0.1 s | yes, 0.4 s | yes, 1 s |

The geometry argument is a single inequality. Vectors for pigeons sharing a hole are orthogonal,
so the beliefs in each hole sum to at most 1. That makes the total at most n, but n+1 pigeons need
n+1. The algebra has no notion of "at most", and the degree it needs keeps rising, as
Razborov (1998) proved it must (roughly n/2).

**2. Parity: random 3-variable XOR equations with no solution. Algebra wins.**

| Variables / equations | 10/15 | 10/30 | 20/30 | 20/60 | 40/60 | 40/120 | 60/90 | 60/180 | 80/120 | 80/240 |
|---|---|---|---|---|---|---|---|---|---|---|
| Algebra (degree 1) | refutes | refutes | refutes | refutes | refutes | refutes | refutes | refutes | refutes | refutes |
| Geometry | fails | fails | fails | fails | fails | fails | fails | fails | fails | fails |

The algebra refutes every case instantly. The geometry finds a feasible point in every case: all
beliefs at ½, with every local distribution uniform. Parity is invisible to it. This matches the
known lower bounds (Grigoriev 2001; Schoenebeck 2008).

**3. Coupled: a parity part (11 variables) that forces a switch z = 1, and pigeon rules that apply
only when z = 1. Impossible. Each engine has half the answer.**

| Pigeons → holes (variables) | 4→3 (23) | 5→4 (31) | 6→5 (41) | 7→6 (53) | 8→7 (67) | 9→8 (83) |
|---|---|---|---|---|---|---|
| Algebra alone: lowest degree | 3 | 3 | 4 | > 3 | > 3 | > 3 |
| Geometry alone | refutes* | fails | fails | fails | fails | fails |
| **Wave at degree 1** | **refutes, 1 round** | **1 round** | **1 round** | **1 round** | **1 round** | **1 round** |

In every case the wave ran the same way. Degree-1 algebra solved the parity part (11 facts,
including z = 1), and the geometry then refuted the pigeons immediately. *At the smallest size the
geometry also succeeded alone. From 5→4 on, it left z fractional (0.42 in a trial run) and failed. "> 3" means degree
3 did not refute and degree 4 was too large for this solver (over 150,000 monomials).

**4. The 16 hard Sudokus from the earlier study: geometry wins.**

| Engine | Solved completely | Notes |
|---|---:|---|
| Geometry (earlier study) | 16 / 16 | one lift each |
| Algebra degree 1 | 0 / 16 | forced at most 8 cells |
| Algebra degree 2 | 7 / 16 | 0 cells on Inkala and Easter Monster; 1–51 cells on the other 7 |
| Algebra degree 3 | not run | 1–2 million monomials, too big |

The 7 that degree 2 solved are not simply the easy ones. It solved Norvig #1 and #4 but not #9,
and the earlier LP control had forced all three.

**5. Random 3-SAT (5 clauses per variable, every instance checked unsatisfiable): the wall.**

| Variables | 12 | 16 | 20 | 25 | 30 | 40 | 50 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Algebra: lowest degree | 3 | 3 | 4 | 4 | 4 | 4 | > 3 (degree 4 too big) |
| Geometry | fails | fails | fails | fails | fails | fails | fails |
| Wave at degree 3 | — | — | stuck | stuck | stuck | stuck | stuck |

"Stuck" means neither engine derived a single fact, so the wave never started. Degree 3 or 4
works here only because the instances are small. The proven lower bounds say both engines need
degree growing in proportion to n on random 3-SAT: Ben-Sasson–Impagliazzo and
Alekhnovich–Razborov for the algebra, Grigoriev and Schoenebeck for the geometry.

## What this shows

1. **The two kinds of reasoning really are complementary.** Geometry handles counting (pigeons,
   Sudoku); algebra over F₂ handles parity. This matches what proof complexity predicts.
2. **A wave beats both when the problem decomposes.** If the parts talk through a few simple facts,
   each engine solves its part and hands over the result, and the total cost stays at the cheapest
   level of each engine. That gap would grow without bound with problem size (the coupled family's
   algebra-alone degree is tied to the pigeon bound).
3. **The bottleneck is the shared language.** The wave only passes single-variable facts and
   equalities. On random 3-SAT the information is spread out: no single variable is forced by
   anything cheap. Nothing crosses between the engines, and both fail.
4. **Translating between the worlds costs degree.** A parity fact on k variables (x₁ + … + xₖ = 1
   mod 2) is a real polynomial of degree k. A level-1 lift cannot use one longer than 2. So richer
   communication has to be paid for in degree, and that is exactly where the proven lower bounds
   apply. A hybrid that only exchanges short facts cannot get past them.

**Not new, in context.** Combining linear algebra with other reasoning is an active area. Known
proof systems that mix parity with resolution or cutting planes include Res(⊕) and its relatives.
SAT solvers such as CryptoMiniSat run Gaussian elimination alongside search. The coupled family is
constructed to show the mechanism. It is not a natural problem.

## Follow-up 1: a richer shared language (`engines2.py`, `run_rich.py`)

**Idea.** Let the engines exchange the constraint language itself, not just single-variable facts:
- **clauses of up to 3 literals.** A clause means the same thing in both worlds, because it is the
  polynomial ∏(1 − literal) = 0, valid over F₂ and over the reals.
- **parity equations of up to 3 variables** (the algebra's degree).

The algebra scans its derived span for every such short fact. The level-1 lift reports every
event (one variable, a pair, or a clause's local assignment) whose probability sits at 0, and
confirms each with a probe. A stronger **level-2 lift** (degree-4 sum of squares: a PSD matrix over
all monomials of degree ≤ 2) was also tried.

**Results on random 3-SAT** (5 clauses per variable, unsatisfiable, 3 seeds; the seed-4 instances
are the same ones as in section 5):

| Variables | 12 | 16 | 20 | 25 | 30 | 40 |
|---|---|---|---|---|---|---|
| Algebra alone: lowest degree | 3 | 3 | 4 (all 3 seeds) | 4 (all 3) | 4 (all 3) | 4 (all 3) |
| Level-1 lift alone | fails | fails | fails | fails | fails | fails |
| **Richer wave, algebra at degree 3** | (degree 3 alone suffices) | (same) | **stuck, 3 of 3** | **stuck, 3 of 3** | **stuck, 3 of 3** | **stuck, 3 of 3** |
| Level-2 lift alone | refutes (2.6 s) | refutes (40 s, about 5 GB) | not run: about 25 GB | — | — | — |

- **The exchange did start this time.** On 12 instances the algebra passed 0–12 derived clauses
  per round. In 3 of them the geometry found new clauses as well (5, 6 and 3), and in two of those
  the algebra then derived more from them (8 and 12). That is a real back-and-forth.
- **It always fizzled out.** After at most 3 rounds and 24 facts, neither engine had anything new,
  and neither had refuted the instance. Degree-4 algebra, one level higher, refutes all of them on
  its own. The richer exchange at degree 3 never closed that one-level gap.
- **No parity equation was ever derived.** Random 3-SAT has no short parity structure to find, so
  that half of the new language went unused.
- **The level-2 lift is strong but expensive.** It refuted the 12- and 16-variable instances alone,
  where the level-1 lift could not. But its cost explodes. At 20 variables each run needed about
  25 GB, and three in parallel exhausted this 16 GB Mac's memory and swap, so they were stopped.
  (The first attempt's logs are kept as `rich_s*_first_attempt.log`.)

**Reading.** A richer language lets the engines talk, but on random 3-SAT they have very little to
say. The facts that would help are long ones, and long facts cost degree. This is the same wall as
before, seen from closer up.

## Follow-up 2: the problem as a wave (`fourier.py`)

**Idea.** On n bits the natural Fourier transform is the Walsh–Hadamard transform. Its waves are
the parities χ_S(x) = (−1)^(sum of x_i over S), one for each subset S of the variables. Write the
solution set as an indicator f = f₁·f₂·…·f_m, with one factor per constraint. Then multiplying the
constraints together *convolves* their spectra. Each 3-variable constraint has a tiny spectrum, at
most 8 frequencies. The script tracks how many frequencies are on as the constraints are
multiplied in (18 variables, all 262,144 frequencies computed exactly).

| After k constraints | 3-SAT (planted): solutions | 3-SAT: frequencies on | 3-XOR (planted): solutions | 3-XOR: frequencies on |
|---|---:|---:|---:|---:|
| 1 | 229,376 | 8 | 131,072 | 2 |
| 9 | — | — | 512 | 512 |
| 10 | 70,000 | 16,384 (6%) | — | — |
| 19 | 24,766 | 131,072 (50%) | 4 (k=19) | 65,536 (25%) |
| 37 | 3,027 | 262,144 (100%) | — | — |
| 72 (end) | 39 | 262,144 (100%) | 2 (k=22) | 131,072 (50%) |

1. **The spectrum fills up.** For 3-SAT, after 37 of 72 clauses every frequency is on, and 92% of
   the final spectral weight sits at degree 5 or higher.
2. **Parity stays crystalline.** For XOR the switched-on frequencies always form a subspace, the
   span of the equations. At every step, *solutions × frequencies = 2¹⁸ exactly*. That is the
   Fourier **uncertainty principle** (|support of f| · |support of f̂| ≥ 2ⁿ), with equality exactly
   for subspaces. A subspace is described by a basis of at most n vectors, which is why Gaussian
   elimination handles parity in polynomial time even though the spectrum itself is huge. For
   3-SAT the product is at least 7× the bound, and no basis describes it.
3. **The uncertainty principle answers the "wave" question directly.** A problem with few solutions
   *must* have a spread-out spectrum: a unique solution switches on every frequency. The answer
   can't be hidden in a few waves. Its lowest frequencies do determine it: the degree-1 coefficient
   for x_i is proportional to (#solutions with x_i = 0) − (#solutions with x_i = 1). But computing
   them from the formula is a sum over all 2ⁿ assignments, the same wall as the moments in the
   partSAT paper.
4. **Waves of a different kind: quantum.** A quantum computer manipulates exactly this kind of
   spectrum through interference, which powers Shor's factoring algorithm. For unstructured search
   the BBBV / Grover bound limits interference to a quadratic speedup: √(2ⁿ) instead of 2ⁿ, still
   exponential.

## Next ideas

- **Sparse elimination.** The dense solver stops at about 150,000 monomials. A sparse F₂
  elimination, like those in Gröbner-basis software, would reach degree 3 on Sudoku and degree 5
  on pigeons.
- **Natural hybrids.** Look for real problem families with a parity part and a counting part, for
  example Sudoku variants with parity cages, or cryptographic puzzles with a combinatorial wrapper.

## Reproduce

```bash
P=/Volumes/KINGSTON/Vibecoding/.venvs/sdp/bin/python
$P run_all.py pigeons parity coupled   # minutes -> results_pigeons_parity_coupled.json
$P run_all.py sudoku                   # minutes -> results_sudoku.json
$P run_all.py sat                      # minutes -> results_sat.json
$P run_rich.py rich_s4.json 4 12 16 20 25 30 40   # richer wave; run seeds one at a time (memory)
$P run_rich.py rich_s5.json 5 20 25 30 40
$P run_rich.py rich_s6.json 6 20 25 30 40
$P fourier.py 18 1                     # seconds -> fourier_n18_s1.json
```

Files: `engines.py` (both engines and the wave), `engines2.py` (richer language, level-2 lift),
`families.py` (test problems), `run_all.py`, `run_rich.py`, `fourier.py`.
Needs cvxpy (with Clarabel), numpy and python-sat.
