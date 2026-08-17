# Tier-1 persistence laboratory for the Double-Pendulum Operational Atlas

## Purpose

The first atlas image samples a finite-time operational field on one grid.
Small connected components in that image need not represent spatially stable
regions: they can move, split, or disappear when the grid origin, resolution,
threshold, cadence, or observation horizon changes.

`oig_double_pendulum_persistence.py` makes those dependencies explicit without
promoting them to a theorem about the exact nonlinear flow.

## Common evaluation contract

Run \(r\) produces a scalar grid-edge log-stretch field \(g_r\) on its own
cell-centred torus grid. The laboratory periodically bilinear-interpolates
every field to one declared common grid:

\[
 \widetilde g_r=I_r g_r.
\]

All RMS errors, correlations, and threshold overlaps are calculated between
the \(\widetilde g_r\) on that common grid. This avoids comparing cell indices
that denote different initial angles after a shift or resolution change.

The interpolation is a declared numerical comparison map. It is not an
outward enclosure, does not transfer connected-component identities, and may
smooth sub-cell structure.

These common-grid persistence ledgers concern the scalar log-stretch field
only. Each run also records the exact serialized Boolean source-grid mask whose
entries label cells with no full-turn excursion at the sampled times, its
reconstructed fraction, and the source-grid count satisfying both the
reference stretch threshold and that sampled no-turn condition. “Exact” here
means that the serialized mask is reproduced without categorical interpolation,
not that it is an exact statement about the continuous dynamics. The mask is
neither interpolated nor combined with the common-grid filtration. A sampled
no-turn label also does not exclude an unobserved turn between sample times.

## Threshold filtration

For each declared threshold \(\tau\), the sublevel set is

\[
 A_r(\tau)=\{q:\widetilde g_r(q)\le \tau\}.
\]

The report stores its active fraction and torus-connected component sizes.
It also compares two runs by

\[
 J_{r,s}(\tau)=
 \frac{|A_r(\tau)\cap A_s(\tau)|}
 {|A_r(\tau)\cup A_s(\tau)|},
\]

with \(J=1\) when both sets are empty. Sweeping thresholds exposes whether an
apparent region exists only because one display cutoff was chosen.

This is a discrete threshold filtration, not a persistent-homology theorem or
a proof of cellwise coherence.

## Four ledgers

1. **Resolution:** each source grid is transported to the common grid and
   compared with the highest declared resolution.
2. **Shift:** half-cell and unshifted grids at equal resolution are compared
   without assuming matching component identities.
3. **Cadence:** equal-RMS finite observation schedules are compared with the
   densest declared schedule. They remain different protocols, not exact
   quadrature enclosures.
4. **Horizon continuation:** horizons are ordered and adjacent fields are
   compared. A different horizon defines a different operational geometry, so
   this ledger deliberately contains no numerical pass/fail flag.

## Energy association

The baseline field is compared descriptively with the zero-velocity initial
energy using Pearson and rank correlation and quantile-bin summaries. This can
reveal that a pattern follows energy stratification, but neither correlation
nor bin conditioning identifies a causal dynamical mechanism.

## Evidence boundary

Every report is Tier 1. The internal verifier validates the serialized source
field schemas and reconstructs:

- the shifted-grid declarations;
- source-to-common periodic interpolation;
- scalar comparisons and threshold overlaps;
- toroidal filtration summaries;
- the fraction and reference-threshold marked count derived from the supplied
  source-grid sampled no-turn mask; and
- energy correlations and bins.

The strict schema requires actual JSON-style numeric and integer values;
booleans and numeric strings are rejected rather than coerced.

It does not reconstruct the source log-stretch or no-turn mask from the ODE,
rerun the ODE, authenticate provenance, enclose the exact flow, or certify
variational responses. Fields that persist under these diagnostics are
better targets for later validated integration; nonpersistence is evidence
against spending rigorous-enclosure effort on the current discretization, not
evidence that no exact dynamical structure exists.

## Reproduction

Generate the bounded-runtime canonical report:

```bash
python oig_double_pendulum_persistence.py \
  --output /tmp/double-pendulum-persistence.json
```

Reconstruct its serialized comparison ledger without an ODE replay:

```bash
python oig_double_pendulum_persistence.py \
  --verify /tmp/double-pendulum-persistence.json
```

Run the focused controls:

```bash
python -m unittest -v test_oig_double_pendulum_persistence.py
```

The atlas-matched research preset is opt-in:

```bash
python oig_double_pendulum_persistence.py --research \
  --output artifacts/double_pendulum_persistence_13x13_t4_tier1.json
python oig_double_pendulum_persistence.py \
  --verify artifacts/double_pendulum_persistence_13x13_t4_tier1.json
```

## Atlas-matched findings

The opt-in preset surrounds the \(N=13,T=4\) portrait by resolutions
\(N=9,13,17\), three half-cell shifts, 5/9/17/41/81 equal-RMS phase samples,
threshold filtration, five initial-energy strata, and horizons \(T=2,4,6\).
It contains 12 deduplicated field runs and its internal verifier passes.

At the source-grid reference predicate (log-stretch at most \(0.5\) and no
sampled full-turn excursion), the resolution counts are 3/7/11 out of
81/169/289 cells, so the marked area fraction remains near four percent while
the discrete marked set remains resolution-sensitive. The three shifted
\(N=13\) grids contain 4, 4, and 8 marked cells, versus 7 on the unshifted
grid.

After periodic bilinear transport of the *scalar log-stretch field* to the
declared 51-by-51 comparison grid, threshold-\(0.5\) Jaccard overlap with the
unshifted field is only \(0.298\), \(0.233\), and \(0.170\) for the three
half-cell shifts. These are not overlaps of the categorical no-turn masks.

The source marked count remains seven for every tested cadence. Against the
81-sample reference, the transported threshold-\(0.5\) Jaccard values are
\(0.714,0.806,0.886,1\) for 5, 9, 17, and 41 samples. This is a declared-grid
trend, not an exact quadrature enclosure. Horizon continuation is not a
convergence test: the transported threshold-\(0.5\) active fraction decreases
from about \(0.0438\) at \(T=2\), to \(0.0127\) at \(T=4\), to \(0.00154\)
at \(T=6\).

Finally, baseline log-stretch has Pearson correlation \(0.8314\) and Spearman
rank correlation \(0.8948\) with the zero-velocity initial energy. Only the two
lowest energy quintiles contain source cells below the reference threshold.
This supports reporting energy stratification alongside the portrait, but
correlation does not identify the dynamical mechanism.
