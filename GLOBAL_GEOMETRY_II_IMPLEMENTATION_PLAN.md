# Global Geometry II: implementation and evidence plan

## Programme status

This is an alpha implementation plan.  It is not peer reviewed and makes no
literature-priority or publication claim.

Global Geometry II is an active extension of the published Global Geometry
Lab.  The release-1 core remains the reference implementation for exact finite
topology, gated angle-defect Gauss--Bonnet, deterministic local dynamics,
finite-scale dimension profiles, and closed configuration replay.  Its focused
baseline currently passes 26/26 tests.

This programme asks a stronger question:

\[
\boxed{\text{Which global geometries are locally generable, recognizable,
and robustly programmable?}}
\]

No refinement experiment, numerical collapse, or successful inverse solve is
silently promoted to a theorem.  Every public claim must link to a
machine-readable evidence record with one of these statuses:

- `proved`: a complete finite proof or a cited theorem whose hypotheses are
  checked in the stated scope;
- `computational`: a reproducible finite calculation with declared estimators,
  uncertainty, controls, and failure conditions;
- `conjectural`: a falsifiable mathematical statement not yet proved;
- `engineering`: a calibrated model or design approximation with stated
  tolerances and domain;
- `speculative`: a motivating interpretation with no evidentiary force.

Every `proved` record additionally declares `proved-here` or
`proved-external` as its basis.  External theorems require a primary source and
a machine- or human-auditable hypothesis check; a passing numerical test is
not itself a proof.

## Shared mathematical contract

A microscopic world is a tuple

\[
\mathcal W=(K,\ell,\mu,W,U,F_R,\theta),
\]

where `K` is a finite graph or cell complex, `ell` is an intrinsic metric,
`mu` is a measure, `W` is a transport law, `U` is local state, and `F_R` is a
radius-`R` equivariant update with parameters `theta`.  A refinement family is
not merely a list of larger graphs; it must declare comparison maps, physical
scale, boundary convention, operator normalization, and the observables that
are intended to converge.

For a declared observable family `Phi`, two rule/refinement families are a
*candidate macroscopic equivalence* only relative to:

1. the chosen observables and scale window;
2. an explicit scale-alignment rule fixed before comparison;
3. finite-size and perturbation tests;
4. negative controls capable of rejecting the comparison; and
5. a tolerance or convergence model that is not fitted to the final pair.

This is deliberately weaker than isometry, equality in law, or a proved
continuum limit.

## Architecture

The extension remains dependency-free in the browser-facing path:

- `global-geometry-core.js`: unchanged release-1 mathematical substrate;
- `global-geometry-ii-core.js`: exact spectra, typed evidence, metric and
  diffusion controls, and the anisotropy/size resolution map;
- `global-geometry-ii-ensembles.js` and `global-geometry-ii-atlas.js`:
  bounded filled-disk families, measurements, aggregation, and semantic
  replay validation;
- `global-geometry-ii-inverse.js`: closed-schema ordered theorem gates,
  finite candidates, and obstruction certificates;
- `global-geometry-ii-sheet.js`: exact q-star budgets, bounded virtual plant,
  synthetic observation, safety protocol, and transcript validation;
- `global-geometry-ii-lab.js`: the forward, universality, recognition,
  inverse, sheet, and evidence views; and
- focused test and generator scripts for the four generated JSON evidence
  layers and platform replication certificates.

Large or optional reference calculations may use audited offline scripts, but
the published finite demonstrations must replay from their exported JSON and
must state when a browser result is an approximation to an offline result.

## Milestone A: exact calibration and evidence ledger

Implement an immutable evidence-record schema and a deterministic run
manifest before adding scientific claims.  The first exact calibration pair is
diffusion on periodic square and triangular lattice graphs.

For an `m` by `n` square torus with normalized Laplacian,

\[
\lambda_{p,q}^{\square}
=1-\tfrac12\left(\cos\tfrac{2\pi p}{m}
+\cos\tfrac{2\pi q}{n}\right).
\]

For the six-neighbour triangular torus used by the implementation,

\[
\lambda_{p,q}^{\triangle}
=1-\tfrac13\left(\cos a+\cos b+\cos(a-b)\right),
\quad a=\tfrac{2\pi p}{m},\ b=\tfrac{2\pi q}{n}.
\]

These formulae provide independent, large-refinement checks against the dense
finite eigensolver.  The calibration claim is limited to the declared
diffusive/spectral observables after a family-specific normalization; it does
not identify the two finite graphs or their complete geometry.  In fact, with
unit one-skeleton edge lengths, their scaling metric balls are respectively
quadrilateral and hexagonal.  The foundations prove this graph-metric
nonuniversality as an exact negative control.  A future full-object comparison
must instead declare a common facewise piecewise-Euclidean metric and a
consistent finite-element/cotangent operator.

Required gates include exact node/degree counts, spectral range and zero-mode
multiplicity, analytic-versus-numerical agreement on small instances,
relabeling invariance, deterministic serialization, and fail-closed manifests.

The alpha browser core retains a named non-cryptographic canonical JSON
checksum for some internal accidental-mutation checks; it must never be
described as a security boundary.  Release artifacts and platform records use
canonical SHA-256 content addresses.  Those addresses make mutation evident
but are not signatures, endpoint authentication, or publication provenance by
themselves.

## Milestone B: falsifiable universality atlas

The principal experiment adds bounded planar disk refinements, a third local
triangulation family, and seeded uniformly elliptic edge disorder.  It measures

\[
\Phi(s)=\bigl(d_V(s),d_s(s),d_w(s),K(s),\beta_k,
H(s),\lambda_2,\text{transport}(s),\text{stability}(s)\bigr).
\]

Scale alignment and diffusivity normalization are fixed by calibration rather
than selected to minimize the final discrepancy.  The atlas reports raw and
aligned profiles, estimator windows, residuals, ensemble intervals, and
finite-size trends.

Mandatory negative controls are comb, shortcut/small-world, bottleneck,
perforated, anisotropic, and non-elliptic families.  A universality badge is
disabled unless the candidate passes replay, refinement, perturbation,
alternate-estimator, leave-one-size-out, and control-separation gates.

## Milestone C: obstruction-aware inverse compiler

The compiler is a staged decision procedure rather than one optimizer:

1. parse and normalize the requested target and constraints;
2. check exact combinatorial and Gauss--Bonnet compatibility;
3. apply stronger declared curvature-polytope or subset inequalities when
   their hypotheses are met;
4. attempt a deterministic intrinsic circle-packing or metric solve;
5. validate residual, robustness, and refinement behaviour;
6. separately assess extrinsic embedding, material, sensing, and actuation
   feasibility.

Every result is one of `certified-compatible`, `certified-obstructed`,
`candidate-found`, `numerically-unresolved`, or `out-of-model`.  Passing a
necessary condition is never represented as sufficient.  An obstruction
report includes the violated invariant or inequality and a minimal witness
whenever the finite model permits one.

## Milestone D: programmable-sheet instrument

The first release is fully testable without physical hardware.  It contains an
intrinsic triangular-sheet model, deterministic actuator emulator, synthetic
sensor noise, reconstruction, and closed-loop target tracking.  Physical
layers are separate:

- fabricable passive templates and safe low-cost actuator options;
- calibration targets and fiducial/camera reconstruction;
- content-addressed cross-platform software replay, with Windows
  camera/device instrumentation kept as a separate future layer;
- uncertainty comparison between commanded, inferred, and predicted geometry.

Intrinsic curvature realization, extrinsic shell equilibrium, and material
response receive separate evidence records.  Hardware purchase, fabrication,
or public deployment requires user approval.

## Milestone E: scoped platform replay and publication candidate

The bounded alpha software snapshot has two content-addressed local inputs,
`artifacts/global-geometry-ii/certificates/macos-local-v2.json` and
`artifacts/global-geometry-ii/certificates/windows-local-v1.json`.  Their
external comparison record,
`artifacts/global-geometry-ii/certificates/macos-windows-comparison-v1.json`,
reports `PASS_FOR_DECLARED_DIGEST_AND_TEST_SURFACE`.  It closes only equality
of the declared manifest, release-index, source, scientific-artifact,
reproduction-resource, and canonical nine focused PASS suite identity/path
surface.  Each local input remains a single-run record.

This bounded comparison does not attest suite-output or performance equality,
the confirmatory U2 batch, vision/device behavior, camera calibration,
hardware, physical validation, scientific completeness, authentication,
priority, peer review, publication, or merge readiness.  Enlarging the replay
surface requires new local records and a new comparison.  Publication and
protected-branch merge remain explicit approval gates outside the attestation.

## Integration execution order

1. Reconcile the formal, universality, and inverse/sheet specifications.
2. Freeze schema version 2 for manifests and evidence records.
3. Implement the exact metric and diffusion controls and their tests.
4. Add bounded ensembles, perturbation sweeps, and negative controls.
5. Implement staged inverse certificates and the digital sheet loop.
6. Integrate the interactive atlas, fabrication package, and manuscript.
7. Generate the bounded macOS and Windows local records and compare their
   declared canonical digest-and-focused-test surface.
8. For confirmatory U2, vision fixtures, or instrumentation, freeze a new
   surface and issue new platform records rather than extending the bounded
   comparison by prose.

## Current verified implementation state

As of the integrated alpha candidate:

- the unchanged release-1 core passes 26/26 focused tests;
- the Global Geometry II core passes 16/16 tests, with sixteen
  machine-readable PROVED-HERE records;
- P8.1 proves graph-metric nonuniversality, P8.2 proves the common
  square/triangular Gaussian finite-dimensional limit, and P8.3 proves a
  uniform covariance-whitened finite-dimensional limit for the declared
  bounded centered nondegenerate iid basin;
- the P8.3 audit contains four unrelated microscopic laws, an anisotropic raw
  negative control, and a frozen 5-by-5 anisotropy/sample-size resolution map.
  Its color boundary is a numerical guard, not a phase-transition claim;
- the filled-disk generator and atlas suites pass 14/14 and 13/13 tests.  The
  generated pilot contains 48 runs in 24 cells and deliberately reports
  `NOT_EVALUATED` for bounded-disk universality;
- the inverse compiler passes 29/29 tests and emits seven replayable reports:
  successful intrinsic witnesses for a tetrahedral sphere, triangular disk,
  annulus, and periodic torus, plus exact Chow--Luo, Gauss--Bonnet, and strict
  triangle-inequality obstructions;
- the virtual-sheet suite passes 32/32 tests for q=5,6,7 intrinsic phases,
  observation-bound commands, watchdog/ESTOP behavior, transcript binding,
  and fail-closed replay;
- the artifact suite passes 5/5 tests over SHA-256-addressed calibration,
  atlas, inverse, and virtual-sheet layers;
- the bounded platform comparison delegates cross-platform status to
  `macos-windows-comparison-v1.json`, whose local inputs are
  `macos-local-v2.json` and `windows-local-v1.json`; it covers only the
  declared digest and canonical nine focused PASS suite identity/path surface;
  and
- the interactive lab exposes real forward, universality, recognition,
  inverse, programmable-sheet, and evidence modes with an explicit evidence
  ceiling in every panel.

The full programme is not yet complete.  The bounded-disk U2 conjecture and
its larger negative-control campaign remain withheld; the sheet is digitally
validated and fabrication-ready rather than physically validated; and the
bounded platform comparison is not a certificate for confirmatory U2,
camera/device instrumentation, or hardware.  Every physical stage remains
`NOT_RUN`.  Public publication and protected-branch merge remain outside the
attestation and approval-gated.
