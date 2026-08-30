# Global Geometry II — computational universality and phase-atlas specification

## Status, scope, and governing claim

This is an alpha research specification.  It is not peer reviewed and makes
no literature-priority or publication claim.

This document is the implementation contract for the computational-universality
workstream of **Global Geometry II: The Universality and Inverse-Design Atlas**.
It is additive to `GLOBAL_GEOMETRY_LAB.md` and the version 0.1 browser core. It
does not change either artifact yet.

The workstream asks a falsifiable question:

\[
\boxed{
  \text{When do microscopically different finite-radius rules become}
  \text{ geometrically indistinguishable after rescaling?}
}
\]

For a local-rule family \(f\), parameters \(\theta\), linear size \(L\), and
replicate \(\omega\), let

\[
  G_{f,\theta,L,\omega}\sim\mathcal E_{f,\theta,L},\qquad
  \Phi(G;r,t)=
  (d_V,d_s,d_w,K,\beta,\mathsf T,\mathsf S).
\]

Here \(\mathsf T\) denotes transport observables and \(\mathsf S\) denotes
stability under declared perturbations. Two rule families are an **empirical
universality candidate** only when a preregistered normalization makes their
joint observable laws approach one another across increasing sizes, while
adversarial controls remain distinguishable. Agreement at one size, between
two seeds, or in a single exponent is not universality.

The engine MUST preserve this evidence ladder:

1. **Exact finite result:** integer homology, Euler–Poincaré, analytic test
   spectra, or a validated finite identity.
2. **Verified numerical result:** a finite estimate with solver residual,
   estimator metadata, and calibration test.
3. **Finite-size empirical finding:** an ensemble statement with uncertainty
   and all declared sizes.
4. **Universality candidate:** a preregistered hypothesis that survived the
   stated controls; never worded as a theorem.
5. **Rejected or unresolved candidate:** retained in the atlas, including the
   failed gate and sufficient raw evidence to reproduce it.

No finite computation in this plan proves a continuum limit. The mathematical
literature motivates hypotheses and estimators; it does not license transferring
a theorem whose hypotheses were not checked.

## 1. Audit of the existing laboratory

### 1.1 Capabilities to preserve

`website/global-geometry-lab/global-geometry-core.js` already supplies:

- a dependency-free UMD core with a closed, bounded configuration schema;
- deterministic FNV-1a/Mulberry32 seeded generation;
- graph, point-cloud, triangulated-disk, and icosphere generators;
- exact \(\mathbb F_2\) Betti numbers and Euler–Poincaré checks;
- fail-closed surface validation and intrinsic angle-defect curvature;
- normalized-Laplacian spectra and heat traces for small graphs;
- finite volume-growth, spectral-dimension, and walk-dimension profiles;
- synchronous L0 diffusion, reaction–diffusion, and incident-star curvature
  feedback, with L1/L2 operations disclosed;
- deterministic state replay, declared interventions, and JSON-safe exports;
- 26 passing core tests as of this specification.

The ensemble engine MUST call these exact finite routines where their validity
and complexity gates permit. It MUST NOT fork a second definition of Betti
number, angle defect, configuration locality, or evidence class.

### 1.2 Limitations that define the new work

The current paired-world comparison changes only a seed inside one preset. It
is a replay/robustness diagnostic, not a family-level universality experiment.
In addition:

- the dense cyclic-Jacobi eigensolver is cubic and normally capped at 120
  vertices (hard validation cap 400);
- heat time is not yet rescaled by mesh spacing or effective diffusivity;
- volume radii are linearly spaced over an estimated diameter and dimensions
  use adjacent-point slopes, making them boundary-sensitive and noisy;
- walk dimension uses deterministic probability propagation, but measures hop
  displacement, samples roots by array index, and uses consecutive-time slopes;
- source-by-index sampling can change under a vertex relabeling even when the
  underlying geometry does not;
- graph curvature, persistent topology, Dirichlet transport, uncertainty,
  refinement fits, perturbation response, and phase classification are absent;
- the 32-bit seed is replayable but does not provide named independent random
  streams or a cross-language rerun certificate;
- a floating result currently has no solver residual, tolerance policy, or
  independent-machine comparison attached to its digest.

Global Geometry II therefore adds an ensemble layer rather than inflating a
single-run state. Small exact analysis remains the calibration oracle; scalable
sparse/probe estimators handle the atlas.

## 2. Operational definition of a universality class

### 2.1 Rule-family contract

A family declaration MUST specify independently:

- `constructionLocality`: how adjacency, faces, metric, measure, and weights
  are constructed;
- `runtimeLocality`: the radius, synchronous/asynchronous schedule, fields
  read, and fields written by the evolution rule;
- `analysisLocality: "L2"`: all global measurements and fitted normalizations;
- `refinement`: how \(L\), characteristic spacing \(h\), and nested/non-nested
  levels relate;
- `boundaryCondition`: periodic, reflecting, absorbing, or Dirichlet;
- `nonUniversalScales`: density, metric factor, diffusion tensor, and time
  scale allowed to differ before comparing families;
- `forbiddenNormalization`: any fitted transform that would erase the target
  observable itself.

A construction based on a global Delaunay solve or k-nearest-neighbor search
may appear in recognition experiments, but cannot be labeled an L0 generative
rule. Local cell templates, local edge hashes, and finite-radius updates are the
primary universality families.

### 2.2 Scaling maps

Every run records both native and dimensionless coordinates. `linearSize` is
the integer number of microscopic cells across the specimen,
`characteristicSpacing` is their native intrinsic spacing \(h\), and
`domainDiameter` is the measured physical span \(R_L\) (normally proportional
to \(Lh\)). For a bounded two-dimensional specimen,

\[
  \rho=r/R_L,\qquad
  \tau=tD_{f,\theta}/R_L^2,\qquad
  \widehat V(\rho)=\frac{V(r)}{\widehat\varrho_{f,\theta}R_L^2},
\]

where \(\widehat\varrho\) is the bulk vertex density and \(D\) is a declared
effective scalar diffusivity. If the measured covariance is anisotropic, the
engine stores the tensor \(\Sigma\), compares both native results and the
whitened coordinate \(x\mapsto\Sigma^{-1/2}x\), and labels the latter
`anisotropyNormalized`. It MUST NOT silently replace anisotropic geometry with a
scalar fit.

For nested refinements, the shared refinement fields are:

```text
level, characteristicSpacing, linearSize, domainDiameter, vertexCount,
parentLevel, restrictionMapDigest, prolongationMapDigest
```

Given errors \(E_{h_c}\) and \(E_{h_f}\), the observed order is

\[
  p_{c,f}=\frac{\log(E_{h_c}/E_{h_f})}{\log(h_c/h_f)}.
\]

At least four sizes are required for a universality extrapolation; three levels
are sufficient only for a compiler/refinement diagnostic.

### 2.3 Family distance

Profiles are evaluated on one preregistered common grid inside the admissible
bulk window. Let \(z_{f,L}^{(q)}(s_j)\) be family \(f\)'s ensemble quantile
\(q\in\{0.1,0.5,0.9\}\). For observable \(O\), define

\[
 D^O_{fg}(L)=
 \left[\frac1{3m}\sum_{q,j}
 \left(
 \frac{z^{(q)}_{f,L}(s_j)-z^{(q)}_{g,L}(s_j)}
      {a_O+\operatorname{MAD}_{\rm pooled}(s_j)}
 \right)^2\right]^{1/2}.
\]

The fixed floor \(a_O\) is declared before runs and prevents a nearly
deterministic observable from creating an unbounded standardized distance. The
joint distance is a weighted Euclidean norm of the registered observable
distances. Weights are fixed in the hypothesis document, never learned from
the same outcomes.

Families pass an **equivalence gate** at tolerance \(\epsilon_O\) only when a
deterministic hierarchical bootstrap gives a 95% upper bound below
\(\epsilon_O\). They pass a **convergence gate** only when the prespecified fit

\[
  D^O_{fg}(L)=D_\infty+cL^{-\omega}
\]

is identifiable, or the simpler conservative alternative—nonincrease over the
three largest sizes and equivalence at the largest two—passes. Both results are
reported; a failed nonlinear fit cannot be replaced post hoc by the easier
rule.

### 2.4 Plateau selection without visual cherry-picking

Each exponent estimator receives a declared candidate window:

- metric radius: \(4h\le r\le L/5\);
- diffusion time: at least eight lazy-walk steps and bulk RMS displacement at
  most \(L/5\);
- heat scale: exclude times where the finite zero mode exceeds 10% of the heat
  trace or where fewer than 95% of probe mass remains within the bulk guard;
- a window contains at least five logarithmically distinct samples spanning at
  least a factor of four.

All contiguous subwindows meeting these rules are fit. The primary window is
chosen lexicographically by: widest log span, smallest leave-one-scale-out
instability, then smallest start scale. The engine exports every eligible fit,
not only the winner. `NO_SCALING_WINDOW` is a valid result and MUST NOT be
converted into a point dimension.

## 3. First falsifiable candidate: U2 flat diffusive geometry

### 3.1 Candidate statement

**U2 — uniformly elliptic planar-disk diffusion.** Distinct bounded-valence,
finite-range, locally constructed planar triangulations of a disk, with
stationary bounded conductances

\[
  0<c_-\le w_e\le c_+<\infty,
\]

are predicted—after density and diffusivity/tensor normalization—to share a
two-dimensional bulk metric-diffusion signature:

\[
  d_V\to2,\qquad d_s\to2,\qquad d_w\to2,
  \qquad d_s-2d_V/d_w\to0.
\]

Their filled complexes remain disks, their valid intrinsic angle defects obey
\(\sum K=2\pi\), and their normalized transverse conductance remains finite and
nonzero. This is a finite-size research candidate, motivated by invariance
principles for random conductance media—including domains with boundaries—not
an assertion that those theorems automatically cover every generator here.

The candidate is deliberately falsifiable. It fails if any registered family
has persistent anomalous diffusion, a nonvanishing cross-family profile
distance, unresolved refinement drift, unstable topology, or transport that
collapses despite matching dimension exponents.

### 3.2 Positive families

Every family is constructed from integer cell coordinates. IDs are assigned by
lexicographic canonical coordinates after construction, never by random draw
order.

| ID | Microscopic local construction | Distinguishing structure |
|---|---|---|
| `square-alternating` | Square cells; each cell is divided by a parity-alternating diagonal using only cell coordinates. | Two vertex valences and a fixed two-cell motif. |
| `triangular-clipped` | Equilateral triangular lattice clipped to the same declared disk/polygon and filled by elementary triangles. | Sixfold bulk adjacency; no square-cell ancestry. |
| `cell-center-fan` | Each square cell creates a center vertex and four incident triangles; neighboring cells share only their boundary edge. | Mixed degree-4 centers and higher-degree corner vertices. |
| `square-hashed-diagonal` | Each square cell chooses one diagonal from a named seed stream and its own coordinate hash. | Quenched local combinatorial disorder with the same macroscopic domain. |

Each family has a periodic-torus counterpart used only for analytic spectral
calibration and boundary-free exponent tests. The disk counterparts are used
for curvature, topology, transport, and programmable-sheet integration.

Two unfilled periodic adjacency carriers are normative spectral oracles. For
the \(L\times L\) four-neighbor square torus,

\[
 \lambda^{\square}_{pq}
 =1-\frac12\left[
 \cos\left(\frac{2\pi p}{L}\right)+
 \cos\left(\frac{2\pi q}{L}\right)\right],
 \qquad 0\le p,q<L.
\]

For the six-neighbor triangular torus with directions
\(\pm e_1,\pm e_2,\pm(e_1-e_2)\),

\[
 \lambda^{\triangle}_{pq}
 =1-\frac13\left[
 \cos\left(\frac{2\pi p}{L}\right)+
 \cos\left(\frac{2\pi q}{L}\right)+
 \cos\left(\frac{2\pi(p-q)}{L}\right)\right].
\]

Sorting these \(L^2\) values with multiplicity must match the numerical
normalized-Laplacian spectrum. These graph carriers calibrate diffusion only;
they are not substituted for the filled disk complexes in curvature or
topology gates. The filled periodic motifs may use block-Fourier or numerical
spectra, but are checked against the two analytic carriers on their common
long-wavelength \(L^{-2}\) scaling.

Edge lengths are embedded Euclidean lengths at initialization and remain the
authoritative intrinsic metric. U2 production runs use native lattice spacing
\(h=1\), so \(R_L\asymp L\); a unit-domain rendering may rescale coordinates
only after analysis. Inverse-design refinements may instead use \(h\asymp
1/L\) and \(R_L\asymp1\), which is why the schema stores all three quantities.
Diffusion uses the lazy reversible rule

\[
 P=\tfrac12 I+\tfrac12D_W^{-1}W,
\]

which removes bipartite parity oscillations. Optional quenched disorder is

\[
  w_e=w_e^{(0)}\exp(\sigma(2u_e-1)),\quad
  0\le\sigma\le\log4,
\]

where \(u_e\) is drawn from the edge's dedicated deterministic stream. The
bound is stored explicitly as `[exp(-sigma), exp(sigma)]`. A zero or unbounded
weight moves the run outside U2 and into an adversarial family.

### 3.3 Preregistered U2 matrix

The confirmatory matrix is frozen before production runs:

```text
families: [square-alternating, triangular-clipped,
           cell-center-fan, square-hashed-diagonal]
linear sizes: [16, 24, 36, 54, 81, 120]
sigma: [0, 0.25, 0.75, log(4)]
replicates: 32 for seeded families/disorder; 1 construction × 32 root/probe
            streams for deterministic families
boundary modes: [periodic-calibration, reflecting-disk]
lazy probability: 0.5
common rho grid: [1/32, 1/24, 1/16, 1/12, 1/8, 1/6, 1/5]
```

The 120 level may be reduced only by a recorded resource amendment made before
looking at its outcomes. Browser previews use `[8, 12, 18, 24]`; they do not
count toward confirmation.

### 3.4 Confirmatory gates

The candidate survives this release only if all gates pass:

1. **Calibration:** exact periodic square and triangular spectra match analytic
   eigenvalues within the solver policy; all four disk families have
   \((\beta_0,\beta_1,\beta_2)=(1,0,0)\), \(\chi=1\), valid vertex links, and
   Gauss–Bonnet residual \(<10^{-9}\max(1,|2\pi\chi|)\) in the small exact tier.
2. **Exponent equivalence:** at each of the two largest sizes, every family's
   bootstrap 95% interval lies inside `[1.80, 2.20]` for each of
   \(d_V,d_s,d_w\). The interval, not just its center, must fit.
3. **Profile collapse:** the 95% upper bound of each pairwise normalized
   profile distance is `< 0.25` at the largest size and nonincreasing over the
   three largest sizes.
4. **Einstein diagnostic:** the 95% interval for
   \(d_s-2d_V/d_w\) lies inside `[-0.15, 0.15]` at both largest sizes. This is
   a comparison diagnostic, not an identity assumed by the estimators.
5. **Transport:** normalized transverse conductance is bounded away from zero,
   and the largest-size between-family equivalence bound is `< 0.20` after the
   declared conductivity normalization.
6. **Robustness:** one-cell metric pulses, 1% bounded edge-weight defects, root
   resampling, relabeling, and boundary crop shifts do not change class status;
   their registered response norms shrink or stay within the fixed tolerance.
7. **Specificity:** at least three of the four primary negative controls below
   fail a gate for the predicted reason. If controls are admitted as U2, the
   classifier is not informative and the candidate is unresolved.
8. **Independent rerun:** macOS and Windows certificates match structurally,
   all exact outputs match bit-for-bit, and numerical outputs pass the declared
   tolerance comparison without manual exclusions.

These tolerances are first-release engineering criteria, not universal
constants. Any revision creates a new hypothesis version; it never overwrites
the old outcome.

The existing bounded software comparison at
`artifacts/global-geometry-ii/certificates/macos-windows-comparison-v1.json`
does **not** satisfy gate 8 for U2.  It compares the declared alpha
manifest/release-index/source/artifact/resource digests and canonical nine
focused PASS suite identities/paths from
`artifacts/global-geometry-ii/certificates/macos-local-v2.json` and
`artifacts/global-geometry-ii/certificates/windows-local-v1.json`; it does not
contain the frozen confirmatory U2 batch,
its Merkle roots, ensemble cells, numerical tolerance audit, or controls.
Accordingly the present U2 result remains `NOT_EVALUATED` and unresolved.

### 3.5 Strong adversarial controls

| ID | Controlled assumption violation | Expected discriminant |
|---|---|---|
| `comb-trap` | Attach a tooth of length proportional to local scale at each backbone site. Local degree remains bounded but traps create anomalous walk behavior. | \(d_w\), return probability, exit time, and directional transport disagree even if volume looks roughly two-dimensional. |
| `small-world-shortcuts` | Add coordinate-hashed edges of macroscopic length at rate \(q>0\). Runtime remains neighbor-local but construction is no longer finite-range. | Ball growth crosses over, distance collapses, and spectral/transport profiles leave U2. |
| `critical-bond-control` | Delete square-lattice bonds near the registered percolation sweep and retain the largest component; do not fill broken faces. | Components, topology, anomalous heat/walk profiles, and sample variance expose the transition. |
| `vanishing-neck` | Join two U2 disks by a corridor whose width is fixed while \(L\) grows. | Local exponents can look U2, but conductance, Cheeger ratio, mixing, and stability fail. |
| `perforated-disk` | Remove a positive density of well-separated face stars. | Bulk diffusion can look U2 while persistent/exact \(\beta_1\) and transport reveal a different global world. |
| `heavy-tail-conductance` | Permit weights below the U2 ellipticity floor with a registered heavy-tail exponent. | Exit time, resistance, and walk estimates separate trapping from mere geometric dimension. |
| `degree-preserving-rewire` | Apply canonical double-edge swaps while approximately preserving degree and the first spectral moments. | Planarity, metric growth, curvature applicability, and topology detect a counterfeit that a short eigenvalue vector may miss. |

The `critical-bond-control` sweep includes \(p=1/2\) for square-lattice bond
retention because Kesten proved that exact infinite-lattice threshold. Finite
graphs are still labeled finite samples, not critical infinite clusters.

An anisotropic, uniformly elliptic lattice is a **positive stress test**, not a
negative control: native profiles may differ, but tensor-whitened profiles are
predicted to rejoin U2. Both views remain visible.

## 4. Phase-diagram programme

### 4.1 Axes

The exploratory atlas sweeps one or two axes at a time while keeping a full
factorial confirmatory slice:

| Axis | Registered range | Meaning |
|---|---:|---|
| `conductanceLogRange sigma` | `0 … 4` | bounded disorder through a deliberately non-elliptic trap regime |
| `bondRetention p` | `0.35 … 1` | fragmentation/percolation |
| `shortcutDensity q` | `0 … 0.05` | finite-range to small-world crossover |
| `anisotropyRatio a` | `1 … 32` | scalar to tensor diffusion |
| `neckWidthRatio w/L` | `1/64 … 1` | transport bottleneck |
| `holeDensity eta` | `0 … 0.2` | topology/transport coupling |
| `curvatureTargetAmplitude A` | within target admissibility | flat to programmed-curvature sheet bridge |
| `localDefectRate delta` | `0 … 0.1` | stability to bounded sparse defects |

Refined samples concentrate near a detected crossover only after the coarse
grid is frozen and exported. Adaptive samples are tagged `exploratory`; they
cannot retroactively join a confirmatory test.

### 4.2 Rule-based geometric phases

The primary phase label is deterministic and multi-label:

- `flat-diffusive`: U2 exponent, profile, topology, and transport gates pass;
- `anisotropic-diffusive`: tensor-normalized gates pass, native isotropy fails;
- `anomalous-diffusive`: a stable scaling window exists but \(d_w\) or \(d_s\)
  is outside U2;
- `small-world-crossover`: polynomial ball-growth windows fail and shortcut
  scale is resolved;
- `transport-bottlenecked`: local dimension gates pass but conductance or
  mixing fails;
- `topologically-perforated`: persistent or exact \(\beta_1\) density remains
  nonzero;
- `fragmented`: \(\beta_0>1\) or giant-component fraction is below threshold;
- `curved-surface`: angle-defect measure is valid and non-flat after declared
  refinement;
- `unresolved`: solver, scaling-window, finite-size, or uncertainty gate fails.

Unsupervised embeddings and clustering may be shown as exploratory overlays,
but may not define the scientific phase labels in release 1.

### 4.3 Cell summary

Every phase cell shows distributions, not a single color:

```text
sample count and failed-run count
median and [10%, 90%] for each exponent/profile
95% hierarchical-bootstrap intervals
exact topology frequency table
solver residual and censoring frequencies
cross-family and cross-size distances
phase-label probabilities and reasons
links to all run IDs and both-machine certificates
```

A low-opacity or hatched cell denotes inadequate information. Missing values
are never imputed for phase classification.

## 5. Observable and estimator contract

### 5.1 Scale-dependent volume dimension

For each canonical bulk root \(x\), use intrinsic shortest-path balls and
report the full distribution of

\[
 V_x(r)=\mu(B(x,r)),\qquad
 d_V(r)=\frac{d\log\operatorname{median}_x V_x(r)}{d\log r}.
\]

Primary estimator: OLS slope on the preregistered log window, with a
root-cluster bootstrap. Alternatives:

1. slope of mean ball volume;
2. median of rootwise slopes;
3. robust pairwise-slope median;
4. dyadic box-counting on embedded positive controls only.

Report boundary distance for every root and 10/50/90% ball-volume quantiles.
The current adjacent-slope profile remains as `legacyAdjacentSlope` for visual
continuity but is not confirmatory.

### 5.2 Spectral dimension and heat return

Use the normalized or declared generator Laplacian \(L\) and

\[
 H(t)=\frac1{|V|}\operatorname{Tr}(e^{-tL}),\qquad
 d_s(t)=-2\frac{d\log H(t)}{d\log t}.
\]

Primary small tier: exact eigenvalue heat trace. Primary large tier: fixed
Rademacher Hutchinson probes with a fixed-order Chebyshev approximation to
\(e^{-tL}\); probe count and polynomial order are increased until both the
analytic truncation bound and repeated-probe standard error meet the declared
tolerance. Alternative: deterministic bulk-root return probabilities under
the lazy transition. Exact and stochastic methods MUST overlap for at least
two sizes and agree within their combined error bounds.

The zero mode is retained in raw heat trace and explicitly excluded only by the
registered bulk-window gate. Solver nonconvergence, an out-of-range normalized
spectrum, or a trace error bound above 2% censors the exponent.

### 5.3 Walk dimension

Primary:

\[
 M_x(t)=\mathbb E_x[d(X_0,X_t)^2],\qquad
 d_w=2\left(\frac{d\log M}{d\log t}\right)^{-1}.
\]

The probability vector is propagated deterministically, so `samplingError=0`
conditional on the chosen roots. Root variation is still uncertain. Use the
same intrinsic metric as volume; hop distance is exported as an alternate.

Independent alternate: mean exit time

\[
 \mathbb E_x\tau_{B(x,r)}\asymp r^{d_w}.
\]

Solve the finite Dirichlet system on each ball with residual and maximum-
principle checks. MSD and exit-time estimates must agree within `0.15` on the
U2 confirmation window or the run is `ESTIMATOR_DISAGREEMENT`.

### 5.4 Curvature

For valid triangular 2-manifolds, the primary curvature is the existing angle
defect and boundary defect. Store it as a signed measure, not only as a vertex
average:

\[
 \nu_K(A)=\sum_{v\in A}K_v.
\]

Across refinement, compare integrated curvature on registered spatial bins and
report `curvatureMeasureDiscrepancy`, total variation, bulk/boundary split, and
Gauss–Bonnet residual. This follows the piecewise-flat deficit-angle tradition
originating with Regge; convergence of curvature measures requires mesh
conditions and is not inferred from the identity alone.

For graph-only controls, compute Ollivier coarse Ricci curvature on edges at
idleness \(1/2\), using shortest-path ground distance and an exact local
transport solve. Optional Forman curvature is a cheap, explicitly different
cell-complex diagnostic. These are not substitutes for angle defect and MUST
appear in separate fields.

### 5.5 Topology

Primary: existing exact \(\mathbb F_2\) Betti numbers of the declared complex,
with Euler–Poincaré cross-check. Add:

- component-size distribution and giant-component fraction;
- Betti density \(\beta_k/|V|\);
- boundary component count and link-validity histogram;
- a metric Vietoris–Rips/clique filtration through dimension two for capped
  point/graph controls;
- bottleneck distance between persistence diagrams under perturbation.

Persistent results are numerical/combinatorial and separately versioned. If a
filtration is truncated by simplex caps, intervals touching the cap are marked
right-censored. Stability of persistence diagrams motivates the perturbation
metric but does not make a noisy reconstruction identical to a latent space.

### 5.6 Diffusion and mixing

Record:

- heat trace and bulk return probabilities;
- spectral gap and zero multiplicity;
- total-variation mixing curve for small/medium tiers;
- diffusion covariance tensor and non-Gaussian parameter;
- first-passage and exit-time quantiles;
- mass conservation, positivity, and maximum-principle residuals.

All dynamics state whether time is discrete/continuous, lazy/non-lazy, and
constant-speed/variable-speed. Results from different conventions cannot share
a phase cell without an explicit conversion.

### 5.7 Transport

For declared source boundary \(A\) and sink boundary \(B\), solve

\[
  (L_Wu)_i=0\ (i\notin A\cup B),\quad u|_A=1,\ u|_B=0,
\]

and compute total current/Dirichlet energy

\[
  C_{\rm eff}(A,B)=\frac12\sum_{(i,j)\text{ ordered adjacent}}
  w_{ij}(u_i-u_j)^2.
\]

Store effective conductance/resistance, solver residual, current conservation,
directional conductivity tensor, Cheeger sweep bound, and max-flow as a
capacity-only alternate. Effective resistance also provides an independent
link to commute-time diagnostics; the engine does not assume that relation for
nonreversible dynamics.

### 5.8 Stability

For perturbation \(P_{\delta,s}\) of magnitude \(\delta\) and stream \(s\),
define the finite response

\[
 R_O(\delta,L)=
 \operatorname{median}_s
 \frac{d_O(O(G),O(P_{\delta,s}G))}{\max(\delta,\delta_0)}.
\]

Perturbation channels are orthogonal and named:

1. metric-length noise;
2. conductance noise;
3. local edge deletion/addition;
4. vertex/face removal;
5. scalar-state pulse;
6. boundary crop/extension;
7. coordinate-only display jitter;
8. relabeling;
9. update-schedule change.

Channels 7 and 8 MUST leave intrinsic observables unchanged within exact or
floating policy. Other channels report a response curve, a recovery time when
there is dynamics, and whether topology changed. Stability is never inferred
from only one perturbation site.

## 6. Deterministic ensemble engine

### 6.1 Proposed additive modules and integration points

No existing file is changed by this specification. A later implementation
should add:

```text
website/global-geometry-lab/global-geometry-ensemble.js
website/global-geometry-lab/global-geometry-estimators.js
website/global-geometry-lab/global-geometry-worker.js
website/global-geometry-lab/test-global-geometry-ensemble.js
scripts/run-global-geometry-atlas.mjs
```

The ensemble module consumes and emits plain JSON and uses the current core as
an injected dependency. Its public surface is:

```javascript
validateExperiment(spec)
expandExperiment(spec)
deriveStreamSeed(runKey, streamName)
generateFamily(familySpec, runKey)
applyPerturbation(complex, perturbationSpec, streamSeed)
measureRun(complex, measurementSpec)
aggregatePhaseCell(runRecords, inferenceSpec)
testUniversality(cellRecords, hypothesisSpec)
createRerunCertificate(experiment, records, environment)
```

`global-geometry-lab.js` later receives only summarized, validated phase cells;
it must not run a production ensemble on the UI thread. Browser work uses a Web
Worker and cancelable chunks. The Node runner owns large sparse computations,
resume/checkpoint, and macOS/Windows replication.

### 6.2 Canonical construction order

1. Validate the closed experiment schema and all enumerations/ranges.
2. Expand parameter cells in lexicographic JCS order.
3. Expand sizes ascending, replicates ascending, then named streams.
4. Derive independent seeds from the complete run key.
5. Generate cells/vertices using coordinate keys; canonicalize vertices,
   undirected edges, and oriented faces.
6. Validate positivity, closure, face uniqueness, links, boundary mode, degree
   bounds, and locality declaration.
7. Apply construction disorder, then interventions, in declared order.
8. Compute a structure digest before dynamics.
9. Evolve with a fixed update order or synchronous buffers.
10. Measure native observables, alternates, solver diagnostics, and scale maps.
11. Write one immutable run record atomically; aggregation reads records only.

Changing loop order MUST NOT change random values because each cell, edge,
root, probe, bootstrap resample, and perturbation has its own derived stream.

### 6.3 Seed and stream contract

The current PRNG is retained for browser compatibility but versioned as
`gg-fnv1a32-mulberry32-v1`. A stream seed is

```text
hex(SHA-256(JCS([
  experimentId, hypothesisVersion, familyId, parameterCell,
  linearSize, replicate, streamName, objectCanonicalKey
])))
```

and that hex string is passed to `seededRandom`. Required stream names are
`generator`, `conductance`, `dynamics`, `roots`, `heat-probes`, `perturbation`,
and `bootstrap`. No stream may be reused for another role.

Normative vectors:

```text
JCS input:
["ggii-u2-v1",1,"square-alternating",{"sigma":0.25},32,7,"generator","family"]
SHA-256:
824641970497f26429c2da4462bb532f1cbe80700162b88c1e7f77b0ce20db19

seededRandom("global-geometry") first five uint32:
[1490147701,3915623240,834937229,1938599049,2182202516]

seededRandom("ggii/u2/test") first five uint32:
[4179899659,141968999,3798011444,2966400562,2780702181]
```

SHA-256 follows FIPS 180-4; JSON uses RFC 8785 JCS with verified errata applied.
NaN, infinities, `-0`, duplicate semantic keys, and locale-dependent strings are
rejected before hashing.

### 6.4 Canonical root and probe selection

Root selection is independent of node array order:

1. form the eligible bulk set from intrinsic boundary distance;
2. sort by canonical coordinate/structural key;
3. choose a seeded cyclic offset and coprime stride;
4. take the first `rootCount` distinct keys;
5. export every chosen key.

Rademacher probes are keyed by `(probeIndex, canonicalNodeKey)`. A relabeling
therefore changes neither roots nor probe signs. Root-count convergence is
tested at `[8, 16, 32, 64]`; the production count is the smallest for which
registered estimates differ by less than 2% from the next level.

### 6.5 Failure semantics

Every stage returns one of:

```text
OK
INVALID_CONFIG
INVALID_COMPLEX
LOCALITY_CONTRACT_VIOLATION
NO_SCALING_WINDOW
SOLVER_NONCONVERGENCE
ESTIMATOR_DISAGREEMENT
RESOURCE_LIMIT
NUMERICAL_DOMAIN_ERROR
CERTIFICATE_MISMATCH
```

Failures are data. Aggregation reports their frequency by family/size and MUST
not silently drop them. If more than 5% of planned runs in any confirmatory
cell fail for a non-scientific reason, that cell and its universality gate are
`unresolved`.

## 7. Data schemas

All schemas are closed, versioned, JSON-safe, and separately migrated. The
snippets below show required topology, not every enumerated constraint.

### 7.1 Experiment specification — `gg.atlas.experiment/2`

```json
{
  "schema": "gg.atlas.experiment/2",
  "experimentId": "ggii-u2-v1",
  "hypothesis": {
    "id": "U2",
    "version": 1,
    "frozenAt": "ISO-8601",
    "claimClass": "universality-candidate"
  },
  "engine": {
    "coreVersion": "0.1.0",
    "ensembleVersion": "planned-0.2.0",
    "prng": "gg-fnv1a32-mulberry32-v1",
    "canonicalization": "RFC8785+errata",
    "hash": "SHA-256"
  },
  "families": [
    {
      "id": "square-alternating",
      "generator": {"type": "square-alternating"},
      "constructionLocality": {"class": "L0", "radius": 1},
      "runtimeLocality": {"class": "L0", "radius": 1, "synchronous": true},
      "boundaryCondition": "reflecting-disk",
      "refinement": {"kind": "linear-size", "sizes": [16,24,36,54,81,120]}
    }
  ],
  "parameterGrid": {"sigma": [0,0.25,0.75,1.3862943611198906]},
  "replicates": 32,
  "measurements": {
    "observables": ["volume","heat","walk","curvature","topology","transport","stability"],
    "scaleWindowPolicy": "u2-bulk-v1",
    "alternateEstimators": true
  },
  "perturbations": [],
  "inference": {
    "bootstrapReplicates": 4096,
    "confidence": 0.95,
    "familyDistanceVersion": "joint-mad-v1",
    "gates": "u2-confirmatory-v1"
  },
  "resourcePolicy": {"tier": "batch", "checkpointEveryRuns": 8}
}
```

### 7.2 Immutable run record — `gg.atlas.run/2`

```json
{
  "schema": "gg.atlas.run/2",
  "runId": "SHA256-of-run-key",
  "runKey": {
    "experimentId": "ggii-u2-v1",
    "familyId": "square-alternating",
    "parameterCellId": "SHA256",
    "level": 3,
    "linearSize": 54,
    "characteristicSpacing": 1,
    "domainDiameter": 54,
    "replicate": 7
  },
  "seeds": {"generator": "hex", "roots": "hex", "heat-probes": "hex"},
  "provenance": {
    "sourceCommit": "40-hex",
    "sourceDirty": false,
    "experimentDigest": "hex",
    "structureDigest": "hex",
    "startedAt": "ISO-8601",
    "durationMs": 0
  },
  "complexSummary": {
    "vertices": 0, "edges": 0, "faces": 0,
    "degreeMin": 0, "degreeMax": 0,
    "boundaryCondition": "reflecting-disk"
  },
  "normalization": {
    "linearSize": 54,
    "bulkDensity": 0,
    "diffusivity": 0,
    "diffusionTensor": [[0,0],[0,0]],
    "fittedFrom": "calibration-split"
  },
  "observables": {
    "volume": {}, "spectral": {}, "walk": {}, "curvature": {},
    "topology": {}, "transport": {}, "stability": {}
  },
  "diagnostics": {
    "status": "OK",
    "solverResiduals": {},
    "censoring": [],
    "warnings": []
  }
}
```

Normalization is fit only on a designated calibration split and then frozen
for confirmatory replicates. A run cannot fit its own transform to its own
profile-collapse error.

### 7.3 Phase-cell summary — `gg.atlas.cell/2`

Required fields:

```text
cellId, experimentDigest, familyIds, parameterCell, sizes,
plannedRuns, successfulRuns, failuresByCode, exactTopologyTable,
profileQuantiles, exponentFits, alternateEstimatorAgreement,
finiteSizeFits, pairwiseFamilyDistances, bootstrapIntervals,
phaseLabels, gateResults, evidenceClass, constituentRunIds
```

### 7.4 Rerun certificate — `gg.atlas.certificate/2`

```json
{
  "schema": "gg.atlas.certificate/2",
  "certificateId": "SHA256",
  "experimentDigest": "hex",
  "runManifestMerkleRoot": "hex",
  "structureMerkleRoot": "hex",
  "exactResultMerkleRoot": "hex",
  "rawFloatResultMerkleRoot": "hex",
  "quantizedFloatResultMerkleRoot": "hex",
  "tolerancePolicy": "gg-float-compare-v1",
  "environment": {
    "os": "windows|macos",
    "architecture": "string",
    "runtime": "node",
    "runtimeVersion": "string",
    "cpu": "string",
    "timezone": "UTC",
    "locale": "C"
  },
  "source": {"commit": "40-hex", "dirty": false},
  "counts": {"planned": 0, "ok": 0, "failed": 0},
  "comparison": {"referenceCertificateId": null, "status": "standalone"}
}
```

The raw floating digest may differ across conforming math libraries. Exact
structures/integers must match. Cross-machine numerical comparison uses per-
observable absolute/relative tolerances and solver error bounds; the quantized
digest is a fast diagnostic, not a proof of equivalence.

This `gg.atlas.certificate/2` contract is a future confirmatory-atlas record.
It is not replaced by the current bounded release-replay comparison, whose
scope is only the declared digest and focused-test surface.

## 8. Algorithms and performance bounds

### 8.1 Tiers

| Tier | Vertex target | Methods | Purpose |
|---|---:|---|---|
| `exact-small` | \(V\le400\) | existing dense spectrum; exact homology; all-root distances | analytic calibration and browser teaching |
| `browser-preview` | \(V\le10^4\), \(E=O(V)\) | sparse/probe heat, capped roots, worker chunks | interactive phase previews, never confirmation |
| `batch` | \(V\le10^5\), bounded degree | sparse matrices, checkpoints, deterministic probes | macOS/Windows production ensembles |

Actual caps are lowered when simplex growth, degree, or memory estimates exceed
policy. User interface tasks yield at least every 100 ms and are cancelable.

### 8.2 Complexity contract

Let \(n=|V|\), \(m=|E|\), \(s\) roots, \(T\) walk steps, \(q\) heat probes,
and \(k\) Chebyshev order.

- canonical generation/validation: expected \(O(n+m)\), memory \(O(n+m)\);
- exact \(\mathbb F_2\) reduction: worst-case cubic in chain size; use sparse
  columns and reject above the declared fill estimate;
- Dijkstra volume roots: \(O(s(m+n)\log n)\), memory \(O(n+m)\);
- unweighted BFS alternate: \(O(s(n+m))\);
- deterministic walk propagation: \(O(Tm+sTn)\) when sources are batched;
- dense Jacobi spectrum: \(O(n^3)\), `exact-small` only;
- stochastic heat trace: \(O(qkm)\) per polynomial schedule, memory
  \(O(qn+m)\), with shared recurrences across registered times;
- Dirichlet/exit-time conjugate gradient: iteration count, residual, and
  preconditioner recorded; abort at the fixed iteration cap rather than return
  an unconverged value;
- local Ollivier curvature: bounded-support transport per edge; disabled when
  degree/support caps are exceeded;
- persistence through dimension two: worst-case simplex count is checked
  before allocation; resource censoring is explicit.

Production acceptance is based on complexity and solver diagnostics, not one
machine's wall-clock benchmark. The Windows node may run the largest cells in
parallel, but a parallel schedule cannot affect run keys or outputs.

### 8.3 Numeric policy — `gg-float-compare-v1`

- input geometry and weights: finite binary64, positive where required;
- exact identities: integers exact; Gauss–Bonnet uses its stated residual gate;
- linear solve: relative residual \(\le10^{-10}\) small tier,
  \(\le10^{-8}\) batch tier;
- eigen calibration: absolute error \(\le10^{-10}\) small tier;
- stochastic heat trace: certified approximation plus 95% probe error
  \(\le2\%\);
- cross-machine scalar comparison:
  \(|a-b|\le10^{-11}+10^{-9}\max(|a|,|b|)\), unless the estimator's own error
  interval is wider, in which case both values must lie in the union of the
  two certified intervals;
- signed zero is normalized; NaN and infinity fail the run.

Tolerance changes version the experiment and comparison policy.

## 9. Normative tests

### 9.1 Exact mathematical vectors

1. **Path \(P_5\):** normalized-Laplacian eigenvalues
   `[0, 0.2928932188134524, 1, 1.7071067811865475, 2]`; endpoint effective
   resistance `4`; \((\beta_0,\beta_1)=(1,0)\).
2. **Cycle \(C_8\):** spectrum
   `[0, 0.2928932188134524, 0.2928932188134524, 1, 1,
   1.7071067811865475, 1.7071067811865475, 2]` and \(\beta_1=1\).
3. **One square, one diagonal, two faces:**
   \((V,E,F)=(4,5,2)\), \((\beta_0,\beta_1,\beta_2)=(1,0,0)\), each boundary
   defect \(\pi/2\), total \(2\pi\).
4. **Infinite-window square-lattice ball:** before boundary contact,
   \(V(r)=1+2r(r+1)\) at integer hop radius.
5. **Infinite-window triangular-lattice ball:** before boundary contact,
   \(V(r)=1+3r(r+1)\).
6. **Two resistors in series / parallel:** Dirichlet solver returns `2` and
   `1/2` resistance respectively, with conserved current.
7. **Disconnected pair of edges:** zero-eigenvalue multiplicity and
   \(\beta_0\) both equal `2`.
8. **Torus refinements:** square and triangular analytic Fourier spectra match
   numerical spectra for all exact-small sizes.

### 9.2 Determinism and invariance tests

- normative PRNG/SHA vectors in section 6.3;
- same run twice is deep-equal before environment timestamps;
- shuffled parameter enumeration yields the same run manifest/Merkle root;
- vertex/edge/face relabeling preserves root keys, topology, profiles, and
  phase result;
- rigid display rotation/reflection/translation preserves intrinsic results;
- coordinate-only jitter changes no intrinsic digest;
- changing one stream changes only its declared descendants;
- worker, Node single-thread, and Node parallel schedules give equivalent
  certificates;
- checkpoint/resume equals uninterrupted execution;
- for confirmatory U2, macOS and Windows pass the atlas certificate and
  numerical-comparison policy; the bounded alpha replay record is not a
  substitute.

### 9.3 Estimator cross-checks

- exact heat trace versus Hutchinson/Chebyshev at every exact-small size;
- MSD versus exit-time \(d_w\) on path, cycle pre-saturation, square torus, and
  triangular torus;
- mean-ball, median-ball, and rootwise slopes on analytic lattice windows;
- Dirichlet conductance versus commute-time/effective-resistance relation on
  reversible unit-weight graphs;
- angle-defect measure versus exact Gauss–Bonnet on disk, sphere, punctured
  disk, and invalid nonmanifold counterexample;
- persistent \(\beta_0\) at filtration zero versus exact components;
- graph Ollivier transport solve against hand-computed path/complete-graph
  cases; Forman results remain a separate field.

### 9.4 Scientific false-positive tests

- a one-size-only synthetic collapse MUST be rejected for missing refinement;
- identical seeds MUST be labeled replay, not ensemble evidence;
- two families with matching \(d_V\) but different \(d_w\) MUST not cluster as
  universal;
- vanishing-neck disks MUST fail transport even if all three dimensions pass;
- perforated disks MUST fail topology even if diffusion profiles pass;
- degree-preserving rewires MUST not pass on a short spectral prefix alone;
- a deliberately biased root set MUST disagree with canonical bulk sampling
  and raise `ROOT_SELECTION_BIAS`;
- adjusting a tolerance after reading outcomes creates a new hypothesis
  version and leaves the original rejection intact.

## 10. Reproduction protocol

This protocol applies to a frozen confirmatory U2 experiment.  The current
content-addressed Darwin/Windows comparison closes only its bounded
release-digest and focused-test surface and supplies no confirmatory U2 run
records.

1. Check out the exact clean commit named by the experiment.
2. Verify source, experiment, and dependency-lock digests.
3. Run normative exact tests before any ensemble cell.
4. Execute the frozen confirmatory manifest; adaptive/exploratory cells use a
   separate manifest.
5. Resume only through content-addressed immutable run records.
6. Build the local certificate and compare it to the reference with
   `gg-float-compare-v1`.
7. On Windows, run from clean instructions rather than copying macOS results;
   return its certificate and failed-run records.
8. Aggregate only after both manifests are complete or explicitly unresolved.
9. If publication is explicitly approved, release the experiment spec, raw run
   records (or a content-addressed archive), summaries, both certificates,
   environment manifests, tests, and claim ledger together.

The public atlas links every claim to a cell and every cell to runs. A visitor
can download a single small run, a phase-cell bundle, or the complete manifest.

## 11. Integration sequence and release gates

### Phase U0 — calibration kernel

- implement the four family generators and periodic counterparts;
- add canonical IDs, named streams, sparse adjacency, and analytic spectra;
- pass all existing 26 tests plus the normative vectors above.

**Gate:** no regression in version 0.1; exact lattice calibrations pass.

### Phase U1 — scalable observables

- heat probes, robust volume windows, intrinsic MSD and exit times;
- Dirichlet transport, perturbation response, solver diagnostics;
- exact/alternate overlap across at least two refinements.

**Gate:** all estimator disagreement and resource-censoring tests pass.

### Phase U2 — ensemble and certificates

- closed experiment/run/cell/certificate schemas;
- checkpointed deterministic runner and hierarchical bootstrap;
- independent macOS/Windows replay.

**Gate:** exact Merkle roots and tolerant numerical comparison pass from a
clean checkout on both machines.

The bounded `macos-windows-comparison-v1.json` record predates and excludes
this phase.  Phase U2 still requires new platform-local atlas certificates and
a comparison over the frozen batch surface.

### Phase U3 — U2 hypothesis

- freeze and execute the confirmatory matrix;
- run all primary controls without retuning thresholds;
- produce accepted, rejected, or unresolved claim record.

**Gate:** a candidate is promoted only by section 3.4; otherwise retain the
negative or unresolved result in the claim record.  Any publication remains a
separate approval-gated action.

### Phase U4 — interactive atlas

- phase-map navigation, family/profile comparison, uncertainty, failure views;
- raw/native versus normalized toggle;
- evidence labels and downloadable rerun manifests;
- bridge disk cells to inverse-design and programmable-sheet examples.

**Gate:** UI cannot hide failed runs, alternate estimators, boundaries, or
normalization; accessibility and responsive checks extend the version 0.1 bar.

## 12. Known blockers and decisions required

1. **Sparse numerical backend:** the dependency-free core cannot reach the
   production sizes with dense eigensolves. Select a deterministic sparse
   implementation for Node and a compatible browser subset; record its exact
   version and solver order.
2. **General cell complexes:** the core stores triangular faces only. U2 is
   intentionally triangulated; later quadrilateral/polyhedral universality
   requires a versioned chain-complex schema rather than encoding every face as
   an arbitrary diagonal without disclosure.
3. **Persistent homology cost:** clique filtrations can explode. Release 1
   requires strict simplex caps and right-censoring; a specialized library is a
   later dependency decision.
4. **Curvature comparability:** angle defect, Ollivier curvature, and Forman
   curvature answer different questions. The atlas must resist combining them
   into one scalar “curvature score.”
5. **Finite-size power:** 32 replicates and six sizes are a starting design.
   Pilot variance may justify a preregistered sample-size increase, never a
   decrease made after favorable results.
6. **Windows confirmatory-batch access:** a bounded Windows local replay and
   external comparison now exist for the alpha digest/test snapshot.  No clean
   Windows U2 batch manifest, rerun certificate, or larger ensemble has been
   produced.  The confirmatory cross-platform U2 gate therefore remains
   unresolved rather than waived.
7. **Theorem boundary:** U2 is plausible and connected to established
   invariance-principle results, but the implemented families' exact continuum
   hypotheses must be proved separately before any theorem claim.

None of these blocks the exact calibration kernel or small pilot. They do block
promotion of a full universality claim.

## 13. Primary mathematical and reproducibility anchors

These sources define or motivate nontrivial pieces of the contract. They are
anchors, not a literature-priority claim.

- T. Regge, “General relativity without coordinates” (1961), introduces
  simplicial piecewise-flat curvature concentrated in deficit angles:
  [DOI](https://doi.org/10.1007/BF02733251),
  [CERN record](https://cds.cern.ch/record/472394).
- J. Cheeger, W. Müller, and R. Schrader, “On the curvature of piecewise flat
  spaces” (1984), gives curvature-measure convergence under controlled
  polyhedral approximation:
  [paper](https://www.cs.jhu.edu/~misha/Fall09/Cheeger84.pdf).
- Y. Ollivier, “Ricci curvature of Markov chains on metric spaces,” defines
  coarse Ricci curvature by Wasserstein contraction of local transition
  measures: [arXiv](https://arxiv.org/abs/math/0701886).
- R. Forman, “Bochner's Method for Cell Complexes and Combinatorial Ricci
  Curvature” (2003), defines the distinct cell-complex curvature used only as
  an alternate diagnostic: [DOI](https://doi.org/10.1007/s00454-002-0743-x).
- S. Alexander and R. Orbach, “Density of states on fractals: ‘fractons’”
  (1982), is an early primary source for the spectral/fractal diffusion scaling
  relation: [DOI](https://doi.org/10.1051/jphyslet:019820043017062500),
  [HAL record](https://hal.science/jpa-00232103).
- M. Belkin and P. Niyogi, “Towards a Theoretical Foundation for
  Laplacian-Based Manifold Methods,” proves graph-Laplacian approximation under
  stated sampling/scaling assumptions:
  [author PDF](https://misha.belkin-wang.org/papers/TT_JCSS_08.pdf).
- Z.-Q. Chen, D. Croydon, and T. Kumagai, “Quenched invariance principles for
  random walks and elliptic diffusions in random media with boundary” (2015),
  motivates the bounded-conductance, bounded-domain U2 candidate:
  [DOI](https://doi.org/10.1214/14-AOP914).
- A. Chandra, P. Raghavan, W. Ruzzo, R. Smolensky, and P. Tiwari, “The
  electrical resistance of a graph captures its commute and cover times,”
  grounds the resistance/commute cross-check:
  [paper](https://homes.cs.washington.edu/~ruzzo/papers/resist.pdf),
  [DOI](https://doi.org/10.1007/BF01270385).
- D. Cohen-Steiner, H. Edelsbrunner, and J. Harer, “Stability of persistence
  diagrams” (2005), grounds the bottleneck stability diagnostic:
  [DOI](https://doi.org/10.1145/1064092.1064133),
  [paper](https://math.uchicago.edu/~shmuel/AAT-readings/Data%20Analysis/Edelsbrunner%2C%20Harer%2C%20Stability.pdf).
- M. F. Hutchinson, “A stochastic estimator of the trace of the influence
  matrix for Laplacian smoothing splines” (1989), supplies the named trace
  estimator: [DOI](https://doi.org/10.1080/03610918908812806).
- M. E. Fisher and M. N. Barber, “Scaling Theory for Finite-Size Effects in the
  Critical Region” (1972), is the primary finite-size-scaling anchor:
  [DOI](https://doi.org/10.1103/PhysRevLett.28.1516).
- H. Kesten, “The critical probability of bond percolation on the square
  lattice equals 1/2” (1980), fixes the exact square-lattice control point:
  [DOI](https://doi.org/10.1007/BF01197577).
- M. Newman and D. Watts, “Scaling and percolation in the small-world network
  model” (1999), motivates the finite-to-small-world crossover control:
  [arXiv](https://arxiv.org/abs/cond-mat/9904419),
  [DOI](https://doi.org/10.1103/PhysRevE.60.7332).
- RFC 8785 specifies JSON Canonicalization Scheme:
  [RFC](https://www.rfc-editor.org/rfc/rfc8785.html), with
  [verified errata](https://www.rfc-editor.org/errata/rfc8785).
- NIST FIPS 180-4 specifies SHA-256:
  [standard](https://doi.org/10.6028/NIST.FIPS.180-4).

## 14. Definition of done for this workstream

The computational-universality workstream is complete for Global Geometry II
when:

- at least four genuinely distinct positive local construction families and
  the stated controls are implemented under one closed schema;
- exact periodic square/triangular benchmarks and all normative vectors pass;
- every primary observable has a scalable estimator, alternate estimator, and
  calibration overlap;
- finite-size, perturbation, and family-level uncertainty are visible and
  machine-readable;
- U2 has an immutable accepted, rejected, or unresolved record produced without
  post-outcome threshold changes;
- macOS and Windows independently reproduce the manifest under valid
  confirmatory-atlas certificates; the bounded alpha comparison does not
  discharge this condition;
- the interactive phase atlas exposes normalization, native profiles,
  uncertainty, failures, and raw provenance;
- all published prose continues to distinguish exact identities, finite
  estimates, empirical candidates, and theorems.

The most valuable outcome need not be confirmation. A clean rejection that
identifies the local assumption responsible for a new geometric phase is a
successful Global Geometry result.
