# Global Geometry II — U2 full-evaluation feasibility and implementation map

## Status and evidence boundary

This is an outcome-blind engineering and mathematical audit of the frozen
`u2-decision-v2` contract. It is **not** an amendment, an experiment outcome,
or permission to reinterpret a threshold. No production result artifact was
read or used while preparing it.

The audit is bound to:

- `GLOBAL_GEOMETRY_II_U2_ADVERSARIAL_PREREGISTRATION.md`, 23,688 bytes,
  SHA-256 `faffef2526d16f79b700102057d59745f0a4359ea7c386c318cc0ee4afd0d5dc`;
- `artifacts/global-geometry-ii/u2/experiment-manifest-v2.json`, 35,194 bytes,
  raw SHA-256
  `337b22a86b6f7b6b4d842c12d03f3eb580d8097e90746e55f9f1d8456c6cf9c6`
  and declared semantic digest
  `80252bca7951da99d9e7de778d98e3ad7147b7b9a76bb585d7ca266ddad348b3`;
- the estimator and numerical policies in
  `GLOBAL_GEOMETRY_II_UNIVERSALITY_SPEC.md`.

The feasibility benchmark is
`scripts/benchmark-global-geometry-ii-u2-full-evaluation.js`. It constructs a
synthetic bounded-degree grid and measures numerical primitives only. It does
not import an experiment generator, seed, run record, or scientific outcome.

## Verdict

A complete decision-grade U2 evaluation is feasible on the available 16 GiB
macOS and Windows machines, but it is not yet safely runnable from the current
kernel. The dominant constraint is compute time, not memory. The current
frozen documents leave several decision-bearing implementation choices
undefined; silently choosing them in production would make the result
non-preregistered.

The smallest defensible route is therefore:

1. freeze one content-addressed, outcome-blind **implementation supplement**
   that closes the ambiguities listed below without changing any scientific
   margin;
2. implement a compact typed-array measurement kernel, immutable resumable
   records, and a pure aggregation/decision layer;
3. pass mathematical, false-positive, bootstrap, resume, and cross-platform
   smoke tests before measuring confirmation records;
4. run macOS and Windows independently from the same source snapshot;
5. publish either the resulting decision or a fully enumerated, reproducible
   `UNRESOLVED` checkpoint.

The last option is legitimate under section 8 of the decision contract. It is
not permission to publish the existing bounded screen as the U2 evaluation.

## 1. Exact estimator surface required by the frozen contract

The following table separates mandatory decision measurements from descriptive
diagnostics. “Designated alternate” means the exact alternate used to support
a scientific `FAIL`; other exported alternates remain valuable diagnostics.

| Quantity | Primary required by the contract | Mandatory alternate or cross-check | Decision use |
|---|---|---|---|
| bulk density | independent calibration-only fit of vertex measure per physical area for each family/`sigma` | leave-one-family-out diagnostic | normalization of volume profiles |
| diffusivity | independent calibration-only scalar or tensor fit, preserving native and whitened coordinates | covariance/tensor diagnostic and leave-one-family-out fit | `tau=tD/R_L^2` and anisotropy disclosure |
| conductivity | independent calibration-only family/`sigma` fit | effective-resistance/dual check | Gate 5 normalization |
| volume | OLS slope of `log median_x V_x(r)` over every eligible factor-four window; choose the primary window lexicographically | mean-ball slope is the natural designated alternate; median rootwise and pairwise-slope medians must also be exported | `d_V` in Gates 2, 4, and 6; normalized raw profile in Gates 3 and 6 |
| heat | continuous heat trace of the declared symmetric generator; exact eigenvalue trace in the exact tier and Rademacher Hutchinson plus certified Chebyshev approximation in batch | deterministic bulk-root lazy-return profile | `d_s` in Gates 2, 4, and 6; spectral-dimension profile in Gates 3 and 6 |
| walk | deterministic propagation of the probability vector from each registered root, using squared intrinsic distance | mean exit-time slope from finite Dirichlet solves; hop-distance MSD is additionally exported | `d_w` in Gates 2, 4, and 6; intrinsic normalized MSD profile in Gates 3 and 6 |
| topology/curvature | exact `F_2` Betti numbers, links, Euler cross-check, angle defects, and Gauss–Bonnet in applicable filled disks | analytic spectra and exact-small fixtures | Gate 1 and the perforated control |
| transport | converged left-to-right weighted Dirichlet solve, total current, and energy | independently formulated wired-boundary unit-current/effective-resistance solve; capacity max-flow remains diagnostic | Gate 5, robustness, and the vanishing-neck control |
| robustness | paired baseline/perturbed estimates with all unaffected stream IDs preserved | the corresponding designated alternates and diagnostics | Gate 6 |

For every successful run, the raw record must retain native observations,
normalized profiles, all eligible windows, the selected window, root keys,
spatial-block keys, heat-probe keys, solver residuals, and primary/alternate
agreement. A cell summary is not a replacement for those run records.

### 1.1 Required window logic

- Volume uses `4h <= r <= R_L/5`, at least five logarithmically distinct
  samples, and at least a factor-four span for scalar exponents.
- The common spatial grid is
  `[1/32,1/24,1/20,1/16,1/12,1/8,1/6,1/5]` in `rho=r/R_L`.
- Heat and walk are sampled on native
  `t_k=ceil(8*2^(k/2))`, with duplicates removed, through the final
  bulk-admissible step. Interpolation to
  `[1/512,1/384,1/256,1/192,1/128,1/96]` in `tau` is between admissible
  neighbors only and never extrapolates.
- Every bootstrap replicate reconstructs aggregate profiles, enumerates every
  eligible window again, and repeats the lexicographic choice. Holding the
  observed primary window fixed is forbidden.
- Gate 2 and Gate 4 scalar decisions use only `L=81,120`. Gate 3 profiles use
  `L=54,81,120` and require at least four common admissible values per
  observable, even where a scalar factor-four window cannot exist.

## 2. Blocking under-specifications

The frozen thresholds are clear. The items below are not. Each must be bound in
an implementation supplement before new production outcomes are generated.

| Blocking item | Why it matters | Smallest outcome-blind closure |
|---|---|---|
| calibration estimators | “fit density/diffusivity/conductivity” does not specify the statistic, window, weighting, anisotropy rule, or finite-size fit | serialize exact formulas, candidate windows, aggregation unit, and failure semantics; freeze the calibration artifact before confirmation |
| heat generator convention | the specification gives a normalized-Laplacian oracle and also a lazy transition; these differ by a factor of two unless the declared generator is explicit | bind the symmetric lazy generator, its spectral interval, the conversion between continuous heat time and discrete return time, and the role of calibration `D` |
| Chebyshev certificate | probe prefixes are frozen, but coefficient construction, order sequence, truncation bound, and maximum order are absent | bind a deterministic coefficient algorithm, analytic uniform tail bound, order schedule/cap, and the rule combining approximation and 95% probe error into the 2% limit |
| heat derivative | `-2 d log H / d log t` does not define a finite-grid derivative or endpoint rule | bind the local regression/stencil and export its exact support at every common point |
| exact/stochastic overlap | two overlap sizes are required, but the registered calibration sizes exceed the `V<=400` tier for some motifs, especially `cell-center-fan` | add non-confirmatory exact fixtures at two smaller refinements, such as `L=8,12`, for all motifs and weights; do not alter the confirmation matrix |
| spatial root blocks | root-block resampling is mandatory, but block construction and size are not declared | bind a coordinate-invariant normalized-domain partition, for example fixed `4 x 4` spatial bins, its empty-bin rule, and composite block keys across nested measurement batches |
| deterministic-cell bootstrap | deterministic `sigma=0` cells have one construction and 32 nested measurement batches, but the exact resampling of their root blocks/probes is unspecified | keep construction count one; resample tagged spatial blocks and nested probes only, never the 32 batches as geometries |
| bootstrap interval convention | `4096` and `95%` do not determine percentile interpolation, one-sided indices, or tie handling | bind the quantile convention, one-/two-sided endpoints, deterministic seed-key layout, and exact treatment of failed resamples |
| designated alternates | several alternates are listed, but the one whose directional agreement authorizes `FAIL` is not named for every gate | bind one designated alternate per atom; export all others without allowing post-outcome switching |
| alternate “direction” | agreement in direction is required but equality, effect sign, and profile-direction reduction are not defined | bind a signed contrast for scalar atoms and a prespecified scalar direction summary for profile atoms |
| transport alternate | reciprocal resistance computed from the same conductance scalar is not independent | bind a separate unit-current wired-boundary solve (or a rigorously dual flow solve), its residual, and reciprocal-consistency check |
| numerical diagnostics | residual `1e-8` is fixed, but current-conservation, positivity, maximum-principle, symmetry, and energy/current agreement tolerances are not | bind scale-aware tolerances no weaker than `gg-float-compare-v1`; a failed diagnostic yields `SOLVER_NONCONVERGENCE` |
| common-grid aggregation | it is not explicit whether family quantiles are over constructions, batches, root blocks, or probes in deterministic cells | bind the hierarchy: construction at the top, then tagged root blocks or heat probes nested within it; never promote a measurement batch to a construction |
| missing-record sensitivity | no finite adversarial bounds are declared for an unobserved exponent or profile | the smallest safe policy is that any nonzero decision-bearing missingness makes the atom `UNRESOLVED`; this is stricter than, and compatible with, the frozen 5% ceiling |
| perturbation expansion | the manifest names five channels but does not enumerate the eight root streams or four crop offsets | expand every measurement instance and distinguish logical channel comparisons from actual executions/reference links |
| crop baseline | `(0,0)` may be either one member of the four-offset ensemble or distinct from the baseline crop | bind one interpretation; if `(0,0)` equals baseline, retain a content-addressed reference record rather than counting a new computation |
| metric/weight coupling | a metric pulse has a conductance tolerance, but it is not stated whether base conductance changes with intrinsic edge length | bind `w_e^(0)` as a function of geometry or bind conductance invariance and therefore exact `Delta C=0` for that channel |
| control aggregation | “strongly FAILS” identifies mechanisms but not a full atom key/size ledger | bind each control to the exact Gate 2–5 atom(s), largest-size rule, and designated alternate that make it count |

These are implementation closures, not invitations to revise `[1.80,2.20]`,
`[-0.15,0.15]`, `0.25`, `0.20`, any robustness tolerance, any size, or any
replicate count.

### 2.1 Delta from the present bounded kernel

`website/global-geometry-lab/global-geometry-ii-u2.js` is a useful partial
carrier/identity kernel, not a foundation on which the missing gates can be
declared by changing labels. Its present scientific boundary is concrete:

| Present behavior | Full-contract requirement | Consequence |
|---|---|---|
| roots are selected from all vertices | roots must satisfy the intrinsic boundary-distance guard at each admitted radius | present volume/walk roots cannot enter strict Gate 2 or 3 |
| radii and bulk guards use `linearSize` | normalization and guards use serialized realized domain diameter `R_L` | current common-grid profiles are dimensionally incomplete |
| one sampled trajectory per root | deterministic probability-vector propagation, conditional sampling error zero | current walk record is an alternate descriptive trajectory only |
| no certified heat estimator or heat probes | exact/Chebyshev-Hutchinson primary plus deterministic return alternate | Gates 2–4 cannot be evaluated |
| restricted layer quotient gives a conductance upper bound | converged Dirichlet conductance, lower/upper bootstrap bounds, and independent resistance solve | Gate 5 cannot be evaluated and zero/nonzero transport cannot be inferred |
| calibration uses largest calibration size and a transport upper proxy | prespecified multi-size calibration-only fits and a frozen conductivity normalization | current normalization cannot support confirmatory profiles or Gate 5 |
| bootstrap resamples already selected run exponents | construction/root-block/probe hierarchy with window reselection in every draw | current intervals are explicitly descriptive |
| no perturbation records | 23,040 expanded leaf submeasurements/reference links | Gate 6 is absent |
| only the perforated control presently reaches its exact mechanism | all four controls need their registered primary/alternate mechanism | Gate 7 remains below its three-control threshold |
| full records have not been independently generated on two hosts | complete macOS/Windows certificates and float comparison | Gate 8 is absent |

The safe implementation strategy is to reuse canonical construction, hashing,
and validation primitives where their normative tests pass, while adding a new
strict measurement/aggregation path. Mutating the partial fields in place
would make it too easy for a descriptive estimator to acquire decision
authority accidentally.

## 3. Gate aggregation model

The following atomization is the smallest one that preserves every frozen
intersection rather than averaging failures away.

### Gate 2 — 48 exponent atoms

Keys are `(family, sigma, exponent)` for
`4 * 4 * 3 = 48` atoms. Each atom contains size subresults for `L=81,120`.

- `PASS`: both two-sided hierarchical 95% intervals are strictly inside
  `(1.80,2.20)`.
- `FAIL`: both intervals are wholly on the same outside side, the designated
  alternate agrees, and no diagnostic censoring can explain the contrast.
- otherwise `UNRESOLVED`.

Smaller sizes are retained as drift and convergence diagnostics, not additional
Gate 2 vetoes unless their failure destroys another registered fit.

### Gate 3 — 96 profile-distance atoms

At each of four `sigma` values, test all six unordered family pairs for the
three registered profiles and their equal-weight joint distance:
`4 * 6 * 4 = 96` atoms.

Each bootstrap replicate must compute within-family-centered pooled MADs at
each scale. Between-family displacement must never enter that denominator.

- `PASS`: one-sided upper bound `<0.25` at both `L=81,120`, and the upper
  bounds at `L=54,81,120` are nonincreasing.
- `FAIL`: lower bound `>=0.25` at both largest sizes, alternate direction
  agrees, and no censoring can explain the separation.
- otherwise `UNRESOLVED`.

The constrained `D_inf+cL^-omega` result is exported only as a diagnostic.

### Gate 4 — 16 Einstein atoms

Keys are `(family,sigma)`, hence 16 atoms. In every bootstrap draw compute
`d_s-2*d_V/d_w` from the jointly resampled and newly selected estimates.

- `PASS`: both size intervals lie strictly inside `(-0.15,0.15)`.
- `FAIL`: both lie wholly beyond the same side, alternate direction agrees,
  and diagnostics are valid.
- otherwise `UNRESOLVED`.

### Gate 5 — 40 transport atoms

- 16 noncollapse atoms keyed by `(family,sigma)`: `PASS` needs the lower bound
  `>0.25` at both largest sizes; `FAIL` needs the upper bound `<=0.25` at both,
  with converged primary and alternate solves.
- 24 equivalence atoms keyed by `(sigma,familyPair)`: `PASS` needs the
  largest-size upper bound `<0.20`; `FAIL` needs lower bounds `>=0.20` at both
  `L=81,120`, with alternate agreement.

Every failed solve remains in the denominator. It is never encoded as zero
conductance.

### Gate 6 — 80 robustness atoms

Keys are `(family,sigma,channel)`: `4 * 4 * 5 = 80` atoms. Each has size
subresults at `L=54,81,120` and the following registered reductions:

- `max(|Delta d_V|,|Delta d_s|,|Delta d_w|)`;
- maximum of the three registered profile distances;
- relative `|Delta C|` where applicable;
- an exact/floating invariance vector for relabeling.

`PASS` requires every applicable `L=120` upper bound strictly below its channel
tolerance and the registered trend rule. `FAIL` requires the corresponding
lower bound above tolerance at both `L=81,120`, alternate agreement, and valid
diagnostics. Any class/status change fails the channel. Everything between
those cases is `UNRESOLVED`.

### Gate 7, Gate 8, and the global state

Gate 7 has four named control records and one threshold aggregate. A control
counts only when its preregistered mechanism is demonstrated by a valid
primary/alternate atom. At least three must count.

Gate 8 compares two independently generated record sets. Run keys, structure
digests, integer topology, failures, and membership are exact; all finite
scalars use `gg-float-compare-v1`. No copied record and no path-level exclusion
is permitted.

Across Gates 2–6 there are 280 top-level positive decision conjunctions under
this atomization. The 80 Gate 6 conjunctions contain separate exponent-max,
profile-max, conductance, class, and invariance subatoms where applicable; the
supplement must serialize those subatoms and may not replace them with only a
channel label. `ACCEPTED` requires every conjunction and subatom, Gate 1, at
least three controls, Gate 8, and zero unresolved confirmatory cells.
`REJECTED` requires at least one valid prespecified scientific `FAIL`
reproduced on both systems. Every other state is `UNRESOLVED`.

## 4. Exact perturbation census

The robustness base has

```text
4 families * 4 sigma * 3 sizes * 32 replicate/batches = 1,536 base units.
```

Literal measurement expansion is:

| Channel | Measurements per base | Measurement instances |
|---|---:|---:|
| one-cell metric pulse | 1 | 1,536 |
| one-percent weight defects | 1 | 1,536 |
| eight disjoint root-resampling streams | 8 | 12,288 |
| canonical relabel | 1 | 1,536 |
| four predetermined crop offsets | 4 | 6,144 |
| **total** | **15** | **23,040** |

There are only `1,536 * 5 = 7,680` logical channel comparisons. That number is
valid as a channel-summary count but not as a leaf-measurement or compute
census. The supplement may serialize 7,680 top-level channel records with
immutable child keys, or one record per leaf; the frozen text does not choose
between those schemas. In either case, the frozen resource table's `*5`
perturbation model understates the literal execution layer by a factor of
three.

If the supplement declares the baseline crop identical to offset `(0,0)`, the
leaf census remains 23,040 but 1,536 crop leaves may be immutable references to
baseline bytes. This is allowed only after exact structure, metric, weight,
root, and probe semantics have been proved identical. The number of newly
computed perturbed measurements then becomes 21,504. This reuse must be
semantic and content-addressed; it cannot be an omitted leaf.

Safe observable reuse can reduce work further without reducing evidence:

- weight defects reuse baseline metric-volume data;
- root resampling reuses primary global heat trace and transport, but recomputes
  root-dependent volume, return, MSD, and exit-time data for all eight streams;
- a metric pulse may reuse heat/transport only if the supplement explicitly
  makes conductance independent of metric length;
- every crop recomputes the applicable graph-dependent observables;
- relabeling must rerun the numerical path, because schedule invariance is the
  property being tested.

## 5. Smallest defensible implementation architecture

One Node 22 codebase can run on both machines. A native dependency is not
needed for the first decision-grade version; compact typed arrays and worker
threads are sufficient and minimize cross-platform differences.

### 5.1 Six separable layers

1. **Closed supplement and expansion.** A generator validates the original
   manifest/decision digests and emits every calibration, positive, control,
   perturbation, fixture, stream, and expected failure key. Unknown fields fail
   closed.
2. **Graph capsule.** Canonical coordinate keys plus CSR adjacency, intrinsic
   lengths, weights, faces, boundary sets, and exact digests. Measurement code
   never relies on JavaScript object enumeration.
3. **Measurement kernel.** Streaming root groups and probes implement
   Dijkstra, sparse propagation, Chebyshev heat, ball exit solves, topology,
   and paired Dirichlet/resistance solves. It emits diagnostics before any
   estimate is admitted.
4. **Immutable runner.** The coordinator assigns lexicographically ordered
   run keys to workers. Each completed record is written once to a
   content-addressed chunk, then a chunk manifest is atomically committed.
   Resume validates chunks and regenerates only absent keys.
5. **Pure aggregation.** Calibration is built and frozen first. A separate
   process reads raw records, performs all 4,096 hierarchical resamples and
   window reselections, and emits all top-level conjunctions and their complete
   subatom ledger. Measurement workers cannot see gate state.
6. **Certification/comparison.** Each host builds roots for source snapshot,
   expansion, structures, exact fields, raw floats, quantized floats, failed
   runs, cells, and the claim. A comparator has no manual-exclusion option.

The Windows source snapshot should be validated by a committed SHA-256 file
manifest so the portable Node runtime does not require Git. The same snapshot
archive and manifest are copied; experiment records are not.

### 5.2 Memory discipline

- stream probes one at a time or in small fixed blocks;
- stream roots in groups of 4–8 rather than retaining 64 probability matrices;
- retain Dijkstra distances only long enough to produce a root's registered
  profile and exit-ball index;
- cache only by a full structure/metric/weight/root digest;
- keep graph capsules separate from measurement records so repeated nested
  batches reference, rather than duplicate, topology;
- cap each worker before allocation and emit `RESOURCE_LIMIT` instead of
  allowing host swapping or an out-of-memory crash.

Four workers is a conservative starting point on each 16 GiB host. Worker
count is an execution parameter in the environment certificate, never part of
the random key.

## 6. Resource model

### 6.1 Frozen planning counts

Summing the frozen per-family/size upper models gives the following operation
units. These are sparse-edge planning operations, not CPU instructions and not
wall-clock promises.

| Scope | volume/Dijkstra | lazy walk | heat | transport CG | sum |
|---|---:|---:|---:|---:|---:|
| 3,072 positives + 384 calibration | 0.060e12 | 1.330e12 | 0.864e12 | 0.040e12 | 2.294e12 |
| baseline plus targeted reuse-aware perturbations | 0.837e12 | 21.075e12 | 5.526e12 | 0.270e12 | 27.708e12 |

The second line assumes the literal eight root streams and four crop offsets,
while reusing only observables guaranteed unaffected by a channel. It excludes
ball-exit solves, exact-small eigensolves, bootstrap aggregation, validation,
canonical serialization, hashing, and I/O. Those omissions are why dividing
the table by a microbenchmark throughput gives only an optimistic lower bound.

### 6.2 Measured macOS primitive throughput

Hardware at audit time:

```text
Apple M4, 8 logical CPUs, 16 GiB RAM, Node v22.22.2, arm64 Darwin.
```

Five repetitions of the outcome-blind synthetic maximum-size probe used a
29,241-vertex, 87,040-edge triangularized grid. Medians were:

```text
single-worker sparse apply       480.9 million undirected-edge applications/s
single-worker Dijkstra           599.6 maximum-size roots/s
full-grid Dirichlet CG           574 iterations in 0.220 s to 9.6e-9 residual
2,401-vertex exit-ball CG        91 iterations; 301 solves/s to 7.7e-9 residual
synthetic process RSS            about 113 MiB
```

Four concurrent probes sustained about 1.88 billion aggregate undirected-edge
applications/s, about 2,004 aggregate Dijkstra roots/s, and about 1,129
aggregate synthetic exit-ball solves/s, with roughly 120 MiB RSS per process.
The command is:

```sh
node scripts/benchmark-global-geometry-ii-u2-full-evaluation.js \
  --apply-repeats=1024 --dijkstra-roots=32 --cg-cap=960 \
  --exit-side=49 --exit-repeats=64
```

The sparse-operation lower bounds are about 20 minutes for the baseline table
and 4.1 hours for the full reuse-aware table at the observed four-process
aggregate. A conservative eight-radii census has 1,572,864 positive-run
exit-ball solves, up to 393,216 control solves, and 11,796,480 perturbed solves.
At the synthetic four-process rate, the 13,762,560-solve upper census alone has
a 3.4-hour kernel lower bound. Real ball extraction, varying ball sizes,
Chebyshev recurrences, root-block propagation, validation, bootstrap indexing,
hashing, and external-drive writes will be slower. A defensible scheduling
envelope is:

```text
strict baseline + calibration + controls on macOS     4–12 hours
full robustness and final aggregation on macOS        24–72 hours total
```

This is a planning interval, not a promised runtime.

### 6.3 Windows checkpoint

The available Windows inventory reports Windows 10 Pro x64, a Ryzen 5 5600XT
with 6 cores/12 threads, about 16.3 GiB RAM, about 195 GiB free storage, and the
same portable Node `v22.22.2`. Memory and storage are sufficient under the
streaming architecture.

Windows throughput is **not budget-certified** until the same synthetic utility
runs there. A provisional x64 scheduling envelope is 36–120 hours for the full
reuse-aware measurement layer. Production should not begin on Windows until
its measured aggregate sparse rate, Dijkstra rate, CG time, and peak RSS have
been inserted into a content-addressed preflight record. The exact projection
is then:

```text
sparse lower bound = 27.708e12 / measured aggregate edge-applications-per-second
Dijkstra lower bound = expanded root executions / measured aggregate roots-per-second
```

Both hosts can work independently in parallel, so two-platform wall time is
the slower host rather than their sum.

## 7. A preregistration-compatible share-worthy checkpoint

If the full perturbation layer exceeds the predeclared resource cap, the
project can still meet section 8 with an immutable `UNRESOLVED` package. The
minimum honest checkpoint is:

1. the original manifest/decision contract and the frozen implementation
   supplement, all content addressed;
2. all normative mathematical, estimator-overlap, false-positive, bootstrap,
   resume, mutation, and certificate tests;
3. the complete calibration split and frozen normalization artifact;
4. all 3,072 strict positive records with primary and designated alternate
   estimates, profiles, windows, counts, diagnostics, and failures;
5. all 768 control records with enough strict primary/alternate measurements
   to adjudicate each registered mechanism;
6. all 23,040 perturbation leaf keys, nested under 7,680 channel records or
   stored separately, with successful leaf payloads where executed and explicit
   `RESOURCE_LIMIT` payloads elsewhere under a resource cap frozen before
   confirmation outcomes;
7. independently generated macOS and Windows record sets, certificates, and a
   no-exclusion comparison;
8. the mechanically derived top-level and subatom ledger and an immutable
   `status: UNRESOLVED` claim naming every resource-limited Gate 6 leaf and
   conjunction;
9. public UI/prose that exposes negative, failed, and unresolved records and
   makes no continuum or physical-validation claim.

This checkpoint meets section 8 because incompleteness is represented as data,
not hidden or reclassified. It cannot support `ACCEPTED`; a resource failure
also cannot support `REJECTED`. If strict baseline alternates, controls, or the
independent host run are themselves absent, the package does **not** yet meet
the section 8 minimum.

## 8. Pre-production test gate

Production must remain disabled until all of the following pass:

- exact path/cycle/square/series-parallel/topology/spectral vectors;
- exact heat versus certified Chebyshev/Hutchinson on two small refinements of
  every motif;
- deterministic MSD versus enumerated Markov propagation and exit-time solves
  on path, cycle, square, and triangular fixtures;
- Dirichlet conductance versus an independently formulated unit-current solve;
- synthetic hierarchical-bootstrap fixtures that catch construction
  pseudoreplication, individual-root resampling, fixed-window resampling,
  between-family MAD contamination, and deterministic-cell inflation;
- threshold-boundary fixtures proving equality cannot accidentally pass;
- every negative-control mechanism and every wrong-mechanism non-count case;
- stream-isolation, canonical relabel, worker-count, and enumeration-order
  invariance;
- checkpoint interruption/resume byte equality and mutation rejection;
- a small clean macOS/Windows run whose exact and float roots compare without
  exclusions;
- an expansion test proving counts `384`, `3,072`, `768`, `7,680` logical
  channel comparisons, and `23,040` perturbation leaf submeasurements.

Only after this gate should calibration be generated. Only after calibration is
frozen should confirmation start.
