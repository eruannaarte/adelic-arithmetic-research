# Double-Pendulum Ensemble Calibration: Adversarial Audit

## Verdict

The ensemble and background-laboratory lane has an independent hostile test
suite. It exercises deterministic generation, the six structured perturbation
laws, numerical summary reconstruction, statistical-language boundaries,
worker cancellation and stale-result rejection, laboratory grids, evidence
commitments, local-only assets, responsive markup, and research-scale execution.

Passing these tests establishes reproducible browser numerics and internally
consistent finite-sample bookkeeping. It does **not** certify a physical
probability law, hardware adequacy, exact-flow truth, outward enclosures, or
state-space stability.

## Scientific semantics guarded by the audit

- **Bounded mode** is a deterministic finite design. Every sampled component
  is checked against its declared support. No probability interval is shown.
- **Sampled-distribution mode** is a seeded numerical sample from a disclosed
  law. Its Wilson-style 95% interval is descriptive, not a certified
  probability guarantee, and is withheld unless at least one nonzero iid
  component is actually sampled.
- The Wilson event is exactly **whole-horizon member survival**: a success is a
  resolved member with no sampled output-tube exit. The interval records its
  success and trial counts; it is not attached to pointwise or member-time
  coverage.
- **Persistent exit** starts at the first run of the declared number of
  consecutive outside-tube samples. Later re-entry does not erase that exit.
- **Projected output reconvergence** means a selected-sensor output left its
  member-specific tube and later re-entered it. It is not evidence of
  state-space convergence, synchronization, or stability. The paired
  wrapped-angle/scaled-velocity state-distance statistic makes that distinction
  numerically inspectable without declaring an attraction threshold.
- **Refined** requires the adaptive/fixed centre comparison, the selected-sensor
  response and both information gains at finite-difference scales `h` and
  `h/2`, and the energy gate. The energetic `T=30` negative control remains
  Live/unresolved even when its empirical tube coverage looks favorable.
- Every stochastic component serializes its exact seeded sampling law and
  support. The audit rejects altered disk, interval, normal, transformed-clock,
  or zero-support declarations even when their checksum is recomputed.
- Percentiles use Hyndman--Fan Type 7 interpolation. Covariances use the
  population denominator over resolved members. The audit reconstructs these
  quantities independently from member records.

## Reproduction and scheduling invariance

Seeds are derived independently from a master seed and explicit coordinates.
Member draws are bit-for-bit identical when generated in one batch, split into
chunks, restarted, or visited in a different order. Laboratory repeat seeds
include `N`, horizon, law, amplitude, and repeat index, so scheduling order
cannot change a cell result. `N = 1` preserves the legacy deterministic launch
to floating-point solver tolerance while leaving the frozen forecast unchanged.

The worker protocol carries both a channel and a unique run token. Missing or
mismatched channels, cancelled tokens, and stale results cannot update the UI.
Worker cancellation terminates the dedicated worker; the no-worker fallback
uses event-loop-yielding asynchronous core functions. Both ensemble and
laboratory cancellation discard partial results.

The performance lane explicitly executes `N = 50, T = 30` and `N = 1000`
fixtures without retaining full trajectories. A compact laboratory projection
removes repeated grids, noise arrays, inside masks, and trajectories while
retaining individual seeds, draw summaries, terminal outcomes, coverage/exits,
amplification, endpoint/full-state diagnostics, and gate decisions. Strict
verification replays what was omitted. The 1,000-member, 30-second,
1,201-sample regression is about 3.08 MB as compact JSON and 6.14 MB as the
indented browser export (down from 67.0 MB before projection). A conservative
pretty-export preflight rejects estimates above 512 MiB. Runtime ceilings are
regression gates, not cross-machine benchmark claims.

## Exact reproduction commands

Run from the repository root:

```sh
node --test website/double-pendulum-oig-wind-tunnel/test-wind-tunnel-core.js
node --test website/double-pendulum-oig-wind-tunnel/test-wind-tunnel-ensemble-adversarial.js
python -m unittest -v test_double_pendulum_wind_tunnel.py
```

The browser bundle is repository-local: HTML, CSS, application script,
generated evidence, dedicated ensemble worker, and core engine require no
network dependency. The only worker import is the local
`./wind-tunnel-core.js` asset.

## Fail-closed provenance

The declaration commitment covers the canonical declaration and hidden-draw
commitments. The runner revalidates the frozen source point, structured law
formula, member coordinates, seeds, offsets, sampling laws, supports, gates,
and draw commitments rather than treating a self-recomputed checksum as
scientific authorization. Strict result and laboratory verifiers replay the
frozen forecast, comparison baseline, seeded outcomes, audits, and summaries;
self-recommitted alterations of retained or compact scientific fields fail.
This is same-code deterministic replay, not a signature, external provenance,
outward enclosure, or physical validation. Numerical failures remain
unresolved; they are not silently promoted to empirical support.
