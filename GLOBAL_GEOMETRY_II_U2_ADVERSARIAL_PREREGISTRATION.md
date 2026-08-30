# Global Geometry II — U2 adversarial preregistration proposal

## Status

Decision-contract ID: `u2-decision-v2`.

This is an outcome-blind review proposal written against
`GLOBAL_GEOMETRY_II_UNIVERSALITY_SPEC.md` before inspecting any new U2 batch
result. It is not itself a U2 result and does not authorize promotion of the
candidate. This exact file becomes normative only when a closed experiment
manifest created before production outcomes are read binds its relative path,
byte length, and SHA-256 digest as decision contract `u2-decision-v2`.

Its purpose is to supersede ambiguous decision fields in version 1 with the
versioned `u2-decision-v2` contract
without weakening the existing gates. Where this proposal is stricter than the
specification, the stricter rule applies.

## 1. Experimental unit and independence

The top-level independent unit is a **weighted construction realization**,
identified by the pair `(generatorStream, conductanceStream)` and its structure
digest. A root set, heat-probe set, bootstrap draw, relabeling, or repeated
measurement of the same weighted complex is not a new construction
realization.

- `square-hashed-diagonal` has 32 independent construction realizations at
  every registered `sigma`.
- At `sigma > 0`, each other positive family has 32 independent conductance
  realizations.
- At `sigma = 0`, `square-alternating`, `triangular-clipped`, and
  `cell-center-fan` each have one deterministic construction and 32 nested
  root/probe batches. Their construction-law variance is exactly zero by the
  declared deterministic model; the 32 batches quantify only numerical and
  spatial-integration uncertainty. They MUST NOT be reported as `n=32`
  independent geometries.
- Roots are spatially dependent. Root uncertainty is estimated by resampling
  registered spatial blocks, not individual roots. Heat probes are nested
  Monte Carlo measurements. Both are resampled strictly inside a construction
  realization in the hierarchical bootstrap.
- The bootstrap hierarchy is construction realization, spatial root block,
  then heat probe. A level that is deterministic is retained as a singleton;
  it is never inflated by duplicating it.
- Production uses 64 canonical bulk roots per measurement batch. Heat probes
  use nested prefixes of `[32,64,128,256]` probes and the smallest prefix whose
  certified approximation plus 95% probe error is at most 2%; failure at 256
  is `SOLVER_NONCONVERGENCE`, not a license to relax the error bar.

Every interval reports all three counts:
`constructionRealizationCount`, `uniqueRootCount`, and `heatProbeCount`.
Duplicate structure digests are disclosed and contribute once at the
construction level.

### Calibration split

Normalization is fit from an additional calibration split, not from any of
the 32 confirmatory replicate IDs. Calibration IDs use the prefix `cal/` and
confirmation IDs use `confirm/`; the namespaces are disjoint.

- Calibration sizes: `[16, 24, 36]`.
- Calibration realizations: 8 per stochastic family/`sigma` cell; 8 nested
  measurement batches for a deterministic `sigma=0` cell.
- Confirmation sizes: `[16, 24, 36, 54, 81, 120]` with the 32 units specified
  above.
- Bulk density, scalar/tensor diffusivity, and conductivity normalization are
  fit on calibration records, serialized, hashed, and frozen before a
  confirmatory record is measured.
- No confirmatory profile, class label, pairwise distance, or failed gate may
  enter a normalization fit. A leave-one-family-out diagnostic is reported but
  cannot replace the frozen transform.

## 2. Gate 3: exact profile-collapse contract

The three confirmatory profile observables are:

1. `logNormalizedVolumeProfile`:
   `log(V(r)/(bulkDensity*R_L^2))`;
2. `spectralDimensionProfile`: the primary heat-trace log-derivative estimate;
3. `logNormalizedMsdProfile`: `log(M(t)/R_L^2)` using intrinsic distance.

Transport is excluded here because Gate 5 tests it separately. Curvature and
topology are excluded from the numerical joint norm because Gate 1 tests their
exact/applicability conditions separately. Legacy adjacent slopes and alternate
estimators never enter Gate 3.

The version-1 matrix's spatial grid cannot satisfy its own `r>=4h`, five-point,
factor-four exponent window at `L=81`: the smallest eligible registered point
would be `rho=1/16`, giving a span of only `3.2` through `rho=1/5`. Before any
outcome is read, the adopted experiment therefore MUST version the hypothesis
and add `rho=1/20`. The amended common spatial grid is
`[1/32, 1/24, 1/20, 1/16, 1/12, 1/8, 1/6, 1/5]`. This is a correction to an
internally infeasible design, not a post-outcome threshold change.

For this guard, the physical upper radius is frozen as `R_L/5`, where `R_L` is
the serialized realized domain diameter, rather than `linearSize/5` with
unstated units. Each selected root must additionally have intrinsic boundary
distance at least `r`. This makes the `rho` grid and the scaling definition
dimensionally consistent. The added `1/20` point remains required because
family-dependent realized diameters and crop guards must share one common
cross-family window.

The common dimensionless heat/walk grid is
`[1/512, 1/384, 1/256, 1/192, 1/128, 1/96]` in
`tau = t D / R_L^2`. A value is admitted only if it also passes every bulk,
zero-mode, solver, and minimum-step guard in the governing specification.
Primary time estimators are measured on the fixed native schedule
`t_k=ceil(8*2^(k/2))`, with duplicates removed, through the last bulk-admissible
step; interpolation to the common `tau` grid is performed only between two
admissible native samples and never extrapolates.

Gate 3 compares raw/local profiles rather than scalar plateau fits. At each of
`L=54,81,120`, at least four common admissible values per profile are required.
The factor-four rule continues to govern scalar exponent estimates, but does
not invalidate an otherwise defined raw-profile distance. This distinction is
necessary because `r>=4h` and `r<=L/5` make a factor-four volume window
mathematically impossible at `L=54`.

For the distance in section 2.3 of the governing specification:

```text
observable                         a_O     joint weight
logNormalizedVolumeProfile        0.05    1/sqrt(3)
spectralDimensionProfile          0.05    1/sqrt(3)
logNormalizedMsdProfile           0.05    1/sqrt(3)
```

`MAD_pooled(s_j)` means the pooled **within-family** median absolute deviation:
each observation is centered on its own family median before pooling. It MUST
NOT include the between-family displacement being tested, because doing so
would enlarge the denominator when families separate. The floor and MAD are
computed separately for each observable and scale. No cell may tune either
quantity.

At each `sigma`, all six unordered pairs of the four positive families are
tested separately for all three observables and for the equal-weight joint
distance. For each distance:

- PASS requires its one-sided hierarchical-bootstrap 95% upper bound to be
  strictly below `0.25` at both `L=81` and `L=120`, and the upper bounds at
  `L=54,81,120` to be nonincreasing in that order.
- FAIL requires its 95% lower bound to be at least `0.25` at both `L=81` and
  `L=120`, alternate estimators to agree on the direction of separation, and
  no solver or window censoring capable of explaining the difference.
- Any other result is UNRESOLVED.

The constrained fit `D(L)=D_inf+c L^(-omega)`, with
`D_inf>=0`, `c>=0`, and `omega in [0.25,4]`, is always exported as a diagnostic.
It is not the decision rule and cannot rescue a failure of the preregistered
three-largest-size rule. This selects the conservative alternative allowed by
section 2.3 before outcomes and prevents post-outcome switching.

All comparisons are strict: equality with an acceptance threshold does not
pass.

### Decision-bearing sizes and Gate 2

Scalar exponent decisions are made only at `L=81` and `L=120`. Sizes
`16,24,36,54` remain mandatory calibration, drift, and profile-convergence
records, but `NO_SCALING_WINDOW` for a scalar exponent at one of those smaller
sizes does not independently block ACCEPTED unless it prevents the expressly
required Gate 3 profile comparison or another registered fit.

For each positive family and `sigma`, separately for `d_V,d_s,d_w`:

- PASS requires the two-sided hierarchical-bootstrap 95% interval to be wholly
  inside `[1.80,2.20]` at both `L=81` and `L=120`.
- FAIL requires the interval to be wholly below `1.80` at both sizes or wholly
  above `2.20` at both sizes, with the alternate estimator agreeing in
  direction and no diagnostic censoring.
- Any boundary crossing, opposite-direction result, absent factor-four window,
  or estimator disagreement is UNRESOLVED.

For Gate 4, apply the same three-way logic to
`d_s-2*d_V/d_w` and `[-0.15,0.15]` at both decision-bearing sizes. The entire
bootstrap recomputes root/probe aggregation, eligible-window enumeration, and
lexicographic primary-window selection. Holding a data-selected window fixed
inside bootstrap resamples is forbidden because it omits selection uncertainty.

## 3. Gate 5: transport floor

The normalized transverse conductance is raw left-to-right Dirichlet
conductance divided by the conductivity predicted by the independent
calibration split for the same family and `sigma`. It may not be divided by a
largest-size confirmatory value.

- Noncollapse PASS: for every positive family and `sigma`, the one-sided 95%
  lower bound is strictly greater than `0.25` at both `L=81` and `L=120`.
- Noncollapse FAIL: the one-sided 95% upper bound is at most `0.25` at both
  largest sizes, with converged linear solves and the same direction under the
  effective-resistance alternate.
- Otherwise: UNRESOLVED.
- Cross-family equivalence PASS: every largest-size pairwise 95% upper bound
  for absolute normalized-conductance difference is strictly below `0.20`.
- Cross-family equivalence FAIL: the corresponding 95% lower bound is at least
  `0.20` at both `L=81` and `L=120`, with alternate agreement.
- Otherwise: UNRESOLVED.

Every linear solve must meet the batch residual limit `1e-8`, current
conservation, positivity, and maximum-principle checks. A failed solve never
becomes zero conductance.

## 4. Gate 6: perturbations and tolerances

Robustness uses the four positive families, all four `sigma` values, the three
largest sizes, and the same independent-unit hierarchy as confirmation. The
baseline and perturbation are paired by construction realization and all
unaffected stream IDs.

1. `one-cell-metric-pulse-v1`: select one canonical bulk face-star from the
   perturbation stream and multiply its incident intrinsic lengths by `1.05`.
   The perturbed triangle inequalities and surface validity must pass.
2. `one-percent-weight-defects-v1`: select exactly
   `ceil(0.01 * edgeCount)` canonical edges without replacement. Replace each
   selected log-weight by
   `0.9*log(w)+0.1*s`, where `s` is independently and uniformly drawn from
   `[-log(4),log(4)]`. This preserves the U2 ellipticity interval.
3. `root-resampling-v1`: use eight new, disjoint named root streams with the
   production root count and no change to construction or probes.
4. `canonical-relabel-v1`: apply reverse canonical input enumeration, then
   recanonicalize before measurement.
5. `half-cell-crop-v1`: use the four predetermined domain-origin offsets
   `(0,0)`, `(h/2,0)`, `(0,h/2)`, and `(h/2,h/2)`; compare their ensemble to
   the baseline crop while preserving the declared target domain.

Every channel must leave the U2 class status unchanged. The following are
one-sided 95% upper-bound acceptance tolerances at `L=120`:

```text
channel                       max |Delta exponent|   profile D   relative |Delta C|
one-cell-metric-pulse-v1             0.05               0.10          0.05
one-percent-weight-defects-v1        0.05               0.10          0.10
root-resampling-v1                   0.10               0.10          n/a
half-cell-crop-v1                    0.10               0.15          0.15
```

Here `max |Delta exponent|` ranges over `d_V,d_s,d_w` and `profile D` ranges
over the three Gate 3 observables. PASS also requires the upper-bound response
at `L=54,81,120` to be nonincreasing, unless all three upper bounds are already
below half the stated `L=120` tolerance. For relabeling, exact combinatorial
outputs and keys must match bit-for-bit and floating outputs must satisfy
`gg-float-compare-v1`; any class/status change is FAIL.

A numerical upper bound over tolerance is not automatically a scientific
rejection: FAIL requires the corresponding 95% lower bound to exceed the
tolerance at both `L=81` and `L=120`, agreement of the alternate estimator,
and valid diagnostics. An interval crossing the tolerance is UNRESOLVED.

## 5. Gate 7: four primary controls

The four controls counted for specificity are frozen as follows. The other
three controls in section 3.5 remain valuable exploratory tests but do not enter
the release specificity decision.

1. `comb-trap`: tooth length `floor(L/4)` at every backbone site. It counts
   only if walk/exit-time evidence strongly FAILS Gate 2 or Gate 4 in the
   predicted anomalous direction.
2. `small-world-shortcuts`: shortcut density `q=0.02`, maximum one shortcut
   endpoint per vertex, and intrinsic endpoint separation at least `L/3`. It
   counts only if metric growth or heat/walk profile evidence strongly FAILS
   Gate 2 or Gate 3 in the predicted crossover direction.
3. `vanishing-neck`: two comparable disk patches joined by a corridor of width
   `2h` and length `floor(L/4)h`. It counts only if the transport lower bound
   strongly FAILS Gate 5 in the predicted collapsing direction.
4. `perforated-disk`: remove coordinate-hashed, mutually three-edge-separated
   interior face stars at target density `eta=0.05`. It counts only if exact
   topology gives `beta_1>0` while the giant component remains at least `0.9`.

Controls use all six sizes and 32 independent construction realizations when
random; deterministic controls use the nested measurement treatment in section
1. A control with invalid construction, unresolved diagnostics, or the wrong
failure mechanism does not count. At least three must count. Fewer than three
makes Gate 7 and the candidate UNRESOLVED; it does not confirm or reject U2.

## 6. Three-way outcome and failure semantics

Each atomic gate result is `PASS`, `FAIL`, or `UNRESOLVED`.

- **ACCEPTED universality candidate:** every positive-family atomic test in
  Gates 1--6 is PASS, at least three primary controls count in Gate 7, Gate 8
  passes on the full confirmatory records, and no confirmatory cell is
  unresolved. This remains a finite-size empirical candidate, not a theorem.
- **REJECTED universality candidate:** at least one prespecified positive-family
  scientific contrast is FAIL at both largest sizes under the rules above,
  its alternate estimator and diagnostics agree, and the falsifying records
  reproduce under Gate 8. One valid counterexample is logically sufficient to
  reject the universal candidate. Mere failure to establish equivalence is not
  rejection.
- **UNRESOLVED:** neither condition above holds, including intervals that cross
  a margin, insufficient scaling windows, estimator disagreement, incomplete
  controls, missing cross-platform evidence, or resource/solver limitations.

Outcome precedence is `REJECTED` over `UNRESOLVED` only for a fully valid,
cross-platform-reproduced scientific FAIL. Infrastructure failures cannot
produce REJECTED.

Failure codes are classified as follows:

```text
INVALID_CONFIG                    infrastructure -> UNRESOLVED
INVALID_COMPLEX                   infrastructure unless a separately validated
                                  in-scope mathematical counterexample exists
LOCALITY_CONTRACT_VIOLATION       out of candidate scope -> UNRESOLVED
NO_SCALING_WINDOW                 UNRESOLVED at a decision-bearing size or when
                                  it breaks Gate 3; diagnostic-only otherwise
SOLVER_NONCONVERGENCE             infrastructure -> UNRESOLVED
ESTIMATOR_DISAGREEMENT            measurement ambiguity -> UNRESOLVED
RESOURCE_LIMIT                    infrastructure -> UNRESOLVED
NUMERICAL_DOMAIN_ERROR            infrastructure -> UNRESOLVED
CERTIFICATE_MISMATCH              reproduction failure -> UNRESOLVED
```

No failed record is dropped. If non-scientific failures exceed 5% in any cell,
that cell is UNRESOLVED. At or below 5%, aggregation is allowed only when a
worst-case missing-record sensitivity analysis cannot change the cell's
three-way status; otherwise it is also UNRESOLVED. Scientific censoring is
never treated as missing at random.

The 4096 deterministic hierarchical-bootstrap resamples and 95% intervals in
the governing specification remain frozen. They are marginal intervals and are
not advertised as simultaneous confidence bands. The global ACCEPT rule is an
intersection of all equivalence gates; descriptive claims about individual
cells must not imply familywise 95% coverage.

## 7. Independent rerun minimum

Gate 8 requires separate macOS and Windows executions from the same clean
commit and closed manifest. Both must independently generate every run record;
copying records between hosts is not a rerun.

- Exact run keys, structure digests, integer topology, failure codes, and
  constituent membership match bit-for-bit.
- Every finite scalar is compared by `gg-float-compare-v1`; there are no
  path-level manual exclusions.
- Platform-local `gg.atlas.certificate/2` records bind the experiment digest,
  run-manifest root, structure root, exact-result root, raw/quantized float
  roots, counts, clean source commit, runtime, and environment.
- A separate comparison record lists every tolerance-bounded difference and
  the maximum tolerance fraction by observable.
- A falsifying cell must reproduce its `FAIL` status on both platforms for the
  global result to be REJECTED. Every cell must reproduce for ACCEPTED.

## 8. Minimum share-worthy evidence

The result is share-worthy when the following package exists even if the
outcome is UNRESOLVED:

1. the frozen manifest and this adopted decision contract, each content
   addressed;
2. normative mathematical and false-positive tests;
3. immutable raw run records, calibration records, normalization artifact,
   cell summaries, and an explicit failed-run ledger;
4. construction-, root-, and probe-level sample counts with no
   pseudoreplication;
5. primary and alternate estimates, all eligible windows, bootstrap intervals,
   native and normalized profiles, and sensitivity analyses;
6. all four primary controls;
7. independent macOS/Windows atlas certificates and their comparison;
8. an immutable `ACCEPTED`, `REJECTED`, or `UNRESOLVED` claim record that states
   exactly which atomic gate determined the result;
9. UI and prose that call ACCEPTED only a finite-size universality candidate,
   preserve negative/unresolved cells, and do not imply physical validation.

## 9. Feasible matrix and resource checkpoint

The positive reflecting-disk matrix contains
`4 families * 4 sigma * 6 sizes * 32 = 3072` confirmatory measurement units,
but only the construction counts described in section 1 are statistically
independent. The four primary controls add at most
`4 * 6 * 32 = 768` units. The additional calibration split adds
`4 * 4 * 3 * 8 = 384` units. Paired perturbations are a separate layer and
must be enumerated explicitly; they are not silently folded into the baseline
count.

`periodic-calibration` is not interpreted as a second full factorial boundary
mode. It consists of the two analytic square/triangular spectral carriers and
the explicitly capped filled-periodic overlap tests. This interpretation must
be serialized in the manifest; otherwise the boundary-mode matrix is ambiguous.

Before outcomes, the implementation must publish a dry-run resource report for
every family/size: predicted vertices, edges, operations, peak bytes, run count,
and checkpoint layout. Reducing `L=120`, a replicate count, an observable, or a
control after inspecting any scientific output creates a new experiment
version. An honestly incomplete `u2-decision-v2` run is UNRESOLVED.

## 10. Outcome-review checklist

An independent reviewer evaluates generated outcomes in this order:

- [ ] The manifest predates outcome inspection and binds this exact file as
      `u2-decision-v2` by path, byte length, and SHA-256.
- [ ] The manifest closes every family, `sigma`, size, boundary/calibration
      carrier, replicate, seed role, estimator, tolerance, perturbation, and
      primary-control enumeration; unknown fields fail closed.
- [ ] A dry-run resource report accounts for all 3072 positive units, 768
      primary-control units, 384 calibration units, and every separately
      enumerated perturbation pair, or a pre-outcome versioned amendment is
      present.
- [ ] Calibration and confirmation seed namespaces and record IDs are disjoint;
      frozen normalization artifacts contain no confirmatory input digest.
- [ ] Construction realizations, root blocks, and probes are counted separately;
      deterministic `sigma=0` carriers are not reported as 32 geometries.
- [ ] Duplicate effective PRNG seeds and duplicate structure digests are listed;
      neither is silently counted as independent evidence.
- [ ] Every bootstrap resamples the declared hierarchy and reruns scale-window
      selection; no selected window or normalization is held data-adaptively
      fixed without disclosure.
- [ ] Gate 2 and Gate 4 use only `L=81,120`; smaller exponent windows are labeled
      diagnostic. Gate 3 still uses raw/local profiles at `L=54,81,120`.
- [ ] Gate 3 uses exactly the three registered profiles, within-family pooled
      MADs, floors `0.05`, equal weights, all six family pairs, and strict
      acceptance inequalities.
- [ ] Gate 5 uses only calibration-frozen conductivity normalization, the
      `0.25` noncollapse floor, and the `0.20` cross-family margin.
- [ ] Gate 6 perturbations are paired, preserve unaffected streams, and use the
      registered magnitudes, tolerances, trend rule, and validity checks.
- [ ] Gate 7 counts only comb-trap, small-world-shortcuts, vanishing-neck, and
      perforated-disk, and only for their preregistered failure mechanisms.
- [ ] Failed and censored records remain in the cell denominator. Any <=5%
      missingness passes the registered worst-case sensitivity analysis.
- [ ] Primary and alternate estimators, all eligible windows, solver residuals,
      bootstrap intervals, and native plus normalized profiles are present.
- [ ] An atomic PASS/FAIL/UNRESOLVED ledger mechanically derives the global
      result. A confidence interval merely crossing a margin is UNRESOLVED.
- [ ] Any REJECTED result identifies a valid positive-family contrast that
      fails at both largest sizes, agrees with its alternate, and reproduces on
      both operating systems. Infrastructure cannot generate rejection.
- [ ] Any ACCEPTED result has no unresolved confirmatory gate, counts at least
      three specificity controls, and passes the complete two-platform batch.
- [ ] macOS and Windows certificates independently bind every run, exact root,
      float root, environment, source commit, and failure count; no copied runs
      or path-level comparison exclusions exist.
- [ ] Public prose says `finite-size empirical universality candidate`,
      `REJECTED`, or `UNRESOLVED` exactly as the immutable claim record says; it
      makes neither a continuum theorem nor a physical-validation claim.
