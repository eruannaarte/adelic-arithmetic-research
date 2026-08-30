# Global Geometry II: local rules, observable-relative universality, and obstruction-aware inverse design

**Research manuscript draft — 2026-08-30**
**Status:** alpha research manuscript; not peer reviewed; no publication,
physical-validation, or literature-priority claim

## Abstract

How can a finite-radius rule, which sees only a bounded neighborhood, produce
a global shape, dimension, or geometry?  We develop a discrete framework in
which the answer has three parts.  First, local incidence and metric data glue
into a global piecewise geometry only when local compatibility and global
integral constraints agree.  Second, equivariant local dynamics propagate
state through finite causal cones while preserving or modifying only the
structures they are authorized to change.  Third, a refinement and scaling
program can erase some microscopic distinctions while retaining others.  The
resulting notion of universality is therefore relative to a declared metric,
operator, observable family, and convergence topology.

The formal package contains sixteen proved-here finite or elementary
propositions.  Two results isolate the central phenomenon.  Unit-edge square
and triangular lattice graphs converge, in their graph-length metrics, to
nonisometric normed planes with four- and six-vertex unit balls,
respectively.  Yet uniform random walks on the corresponding orthogonal and
equilateral step sets have the same covariance-normalized Gaussian
finite-dimensional limit.  Thus a pair of local constructions can be
universal as diffusion laws and nonuniversal as metric spaces.  A third result
proves a robust cylinder-law basin for fixed-dimensional, centered,
bounded-range iid increments with uniformly nondegenerate covariance, after
exact law-specific covariance whitening.

We accompany the theory with deterministic finite artifacts: analytic
spectral calibration on periodic lattices; a 5-by-5 anisotropy/sample-size
resolution map inside the proved diffusion basin; four bounded filled-disk
construction families; a deliberately nonconfirmatory preview atlas; and an
inverse compiler that orders surface, curvature, circle-packing, and metric
compatibility gates before synthesis.  Representative certificates include
admitted intrinsic targets on a tetrahedral sphere, triangular disk, annulus,
and periodic torus; a target that passes Gauss--Bonnet but fails a Chow--Luo
subset inequality by exactly \(-\pi/5\); a zero-curvature sphere rejected by
Gauss--Bonnet; and a degenerate triangle rejected by an exact
binary64-dyadic sign test.  A programmable q-star sheet and
hardware-in-the-loop emulator translate the intrinsic theory into a digital
engineering instrument, without claiming physical validation.  All finite
numerical findings remain distinct from continuum theorems.  Bounded digital
Darwin/Windows replay status is delegated to the content-addressed
[comparison record](artifacts/global-geometry-ii/certificates/macos-windows-comparison-v1.json),
whose inputs are
[the macOS local record](artifacts/global-geometry-ii/certificates/macos-local-v2.json)
and
[the Windows local record](artifacts/global-geometry-ii/certificates/windows-local-v1.json).
That comparison closes only its declared digest-and-focused-test surface.  The
preregistered confirmatory U2 atlas and every physical, camera, device, or
hardware experiment remain open and unvalidated.

## 1. The local-to-global question

The phrase “local rules produce global geometry” can hide several different
claims.  A local formula may create one finite trajectory, a sequence of
larger finite objects, a convergent refinement family, or a robust limiting
law.  These statements are not interchangeable.  Global Geometry II keeps the
chain explicit:

\[
\text{local rule}
\longrightarrow
\text{finite trajectory}
\longrightarrow
\text{refinement family}
\longrightarrow
\text{declared macroscopic limit}.
\]

The programme has forward, inverse, and recognition forms:

\[
\begin{array}{rcl}
\text{forward} &:& \text{local programme}\to\text{global geometry},\\
\text{inverse} &:& \text{target geometry}\to\text{candidate local programme},\\
\text{recognition} &:& \text{local observations}\to\text{admissible global worlds}.
\end{array}
\]

The constructive answer developed here is:

\[
\boxed{
\begin{aligned}
\text{global geometry}
={}&\text{locally compatible cells and measurements}\\
&+\text{global obstruction and conservation laws}\\
&+\text{dynamical selection from initial and boundary data}\\
&+\text{a declared refinement and observation scale}.
\end{aligned}}
\]

Locality is sufficient to build global organization because neighboring
patches share data, updates propagate, and repeated composition reaches the
whole carrier.  Locality is not sufficient to guarantee an arbitrary global
world: topology, total curvature, conservation, and model-specific
inequalities can obstruct it.  Nor does a visually stable large object by
itself establish a continuum limit.  The observation and scaling contract is
part of the geometry being claimed.

## 2. Evidence discipline

Every scientific statement in the project has one primary label:

| Label | Meaning in this work |
|---|---|
| `proved` | A complete proof is given here, or a cited theorem is used after its hypotheses are checked. |
| `computational` | A deterministic or statistical finite calculation with a versioned method and falsifier. |
| `conjectural` | A quantified mathematical statement for which the required proof is not present. |
| `engineering` | A model, emulator, calibration target, or design approximation with a declared envelope. |
| `speculative` | An interpretation that has no evidentiary force. |

A proved record additionally declares `proved-here` or `proved-external`.
Tests can verify that software implements a formula; test success alone never
turns a numerical statement into a theorem.  “Exact” is reserved for symbolic
or combinatorial statements on the declared finite object.  A binary64
evaluation of an exact identity remains a finite numerical audit unless an
exact representation or justified enclosure is supplied.

The implementation uses closed, versioned records.  Each claim names its
scope, method, assumptions, falsifier, dependencies, artifacts, tests, and
limitations.  Internal 32-bit canonical checksums bind replay records and
detect accidental mutations; they are not security boundaries.  Generated
artifact containers add canonical SHA-256 content addresses.

## 3. Mathematical setting

### 3.1 Carrier, metric, measure, and operator

A finite carrier is a typed incidence structure

\[
K=(C_0,C_1,\ldots,C_D,\prec),
\]

with finite cell sets and codimension-one incidence.  A simplicial or cellular
carrier supplies boundary maps over \(\mathbb F_2\) satisfying
\(\partial_{q-1}\partial_q=0\).  The principal implemented surface class is a
finite triangular complex \(K=(V,E,F)\).

At time \(n\), the declared discrete world is

\[
\mathfrak G_n=(K_n,\ell_n,\mu_n,W_n,U_n,A_n,B_n,\Pi_n).
\]

Here \(\ell\) assigns positive intrinsic edge lengths, \(\mu\) is a declared
cell measure, \(W\) assigns transport conductances, \(U\) is local state,
\(A\) is actuator state, and \(B\) records boundary data.  The display or
measured embedding \(\Pi\) is not authoritative intrinsic geometry unless a
configuration explicitly compiles lengths from it.

For a connected one-skeleton,

\[
d_\ell(x,y)=\min_{\gamma:x\leadsto y}\sum_{e\in\gamma}\ell_e.
\]

For a valid triangulated surface, the project can instead use the
piecewise-Euclidean length metric, which permits paths through face interiors.
Those metrics need not share a limit.  Likewise, the transport operator is
declared rather than inferred from the metric.  One implemented family is the
symmetric normalized Laplacian

\[
L=I-D^{-1/2}WD^{-1/2}.
\]

Graph, finite-element, cotangent, and random-walk operators are different
objects and receive different identifiers.

### 3.2 Finite-radius rules

For a cell \(c\), let \(\mathcal N_R(c;\mathfrak G)\) be its rooted,
typed, decorated radius-\(R\) neighborhood in the declared adjacency.  A
synchronous deterministic local rule applies the same isomorphism-invariant
kernel to every such neighborhood and commits all writes at once:

\[
\mathfrak G_{n+1}=F_R(\mathfrak G_n;\theta,b_n).
\]

The locality classes are:

- **L0:** a bounded neighborhood and fixed constants;
- **L1:** L0 plus a disclosed boundary value, precompiled target, broadcast,
  or global scalar; and
- **L2:** a global eigensolve, optimization, equilibrium solve, matching, or
  any computation that can depend on the whole state.

An L2 compiler may create immutable target data used by an L1 runtime.  This
does not make the compiler local.  Structural rewrites are also separate from
state updates: a rule that never changes \(K\) cannot change the carrier's
homology.

### 3.3 Generability and recognition

The framework distinguishes four strengths of generability:

1. exact finite generability;
2. approximate finite generability in a declared target distance;
3. asymptotic generability in a declared convergence topology; and
4. robust generability under a declared perturbation class.

“Programmable” means that an inverse compiler returns a rule programme and the
strongest certificate supported at one of these levels.  “Recognizable” means
that the estimator is identifiable and stable under a declared observation
model; merely calculating a descriptor is not recognition.

### 3.4 Refinement and observable profiles

A refinement programme is a family

\[
\mathscr P=
\left\{(\mathfrak G_h,a_h,b_h,\tau_h,\iota_h,\mathbb P_h)\right\}_{h\downarrow0},
\]

where distance, measure, and time are rescaled by \(a_h,b_h,\tau_h\),
\(\iota_h\) is a comparison or coupling map, and \(\mathbb P_h\) is the law
of any seeded disorder.  A refinement must identify its resolution, boundary
model, mesh-quality gates, and convergence topology.

The observable profile is not one dimension number.  It contains distinct
clocks:

\[
\Phi_h=
\left(d_V(r),d_s(t),d_w(m),\kappa_h,\beta_k(r),
\lambda_2,\operatorname{transport},\operatorname{stability}\right).
\]

Metric radius \(r\), heat time \(t\), walk time \(m\), and filtration scale
are not silently identified.  Agreement of a few components is profile
equivalence, not isometry.

### 3.5 Universality is relative to retained structure

Two families can agree at several distinct levels: replay, finite
isomorphism, finite intrinsic isometry, finite profile equivalence,
finite-dimensional or cylinder-law equivalence, common limit object, or
path-space/object-law universality.  Robustness modifies any one of these
levels when its conclusion holds uniformly over a predeclared microscopic
basin; it is not a stronger topology.  For random
rescaled objects \(\mathcal Z_h^A,\mathcal Z_h^B\) in a declared state space
and topology \(\mathcal T\), object-level universality means

\[
\mathcal Z_h^A\Rightarrow\mathbb Q_\infty,
\qquad
\mathcal Z_h^B\Rightarrow\mathbb Q_\infty
\]

for one limit law.  The topology determines what is retained: metric-measure
shape, rooted neighborhoods, Dirichlet form, curvature measure, topology,
marks, or a combination.  Universality in one projection does not imply
universality in another.

## 4. Proved-here proposition package

The machine-readable ledger contains sixteen proposition records.  Their
proofs are elementary or finite, and their scopes are deliberately narrow.

| ID | Exact statement in its declared scope | Local-to-global role |
|---|---|---|
| P3.1 | A synchronous radius-\(R\) rule on fixed adjacency has a radius-\(RT\) causal cone after \(T\) steps. | Bounds propagation. |
| P3.2 | Neighborhood-isomorphism kernels with equivariant commit commute with relabeling. | Prevents identifier-dependent geometry. |
| P3.3 | State-only updates on a fixed carrier preserve homology and Euler characteristic. | Separates geometric evolution from topology rewrite. |
| P3.4 | A deterministic radius-\(R\), \(T\)-round observer cannot distinguish roots with matching radius-\(RT\) decorated neighborhoods. | Gives a recognition obstruction. |
| P4.1 | Positive shared edge lengths satisfying every strict face inequality glue to a piecewise-Euclidean complex; valid links make it a surface. | Turns compatible local cells into global intrinsic geometry. |
| P4.2 | Positive tangency radii with \(\ell_{ij}=r_i+r_j\) satisfy all face inequalities. | Supplies an automatically compatible local metric family. |
| P4.3 | With interior target angle \(2\pi\) and boundary target angle \(\pi\), finite angle defects sum to \(2\pi\chi(K)\). | Gives a global curvature obstruction. |
| P4.4 | The normalized-Laplacian zero multiplicity equals the number of connected components. | Couples global topology to diffusion. |
| P4.5 | Symmetric edge flux conserves the measure-weighted total. | Produces a global invariant from local cancellation. |
| P5.1 | Solvable circle-radius edge sums are unique on a connected nonbipartite graph and retain a one-dimensional alternating gauge on a bipartite graph. | States inverse identifiability exactly. |
| P5.2 | If every edge of a fixed connected \(N\)-vertex graph changes by at most \(\varepsilon\), every shortest-path distance changes by at most \((N-1)\varepsilon\). | Quantifies finite metric stability. |
| P5.3 | Closed deterministic generation, seeds, broadcasts, and synchronous updates determine one finite trajectory. | Grounds replay. |
| P6.1 | Straight inherited subdivision is isometric in the piecewise-Euclidean metric. | Supplies a null refinement control. |
| P8.1 | Unit-edge square and triangular graph metrics have nonisometric normed-plane limits. | Proves metric nonuniversality. |
| P8.2 | Square and equilateral-triangular simple walks have the same Gaussian finite-dimensional diffusion limit after common covariance scaling. | Proves a scoped universality relation. |
| P8.3 | Centered bounded-range iid laws with a uniform covariance gap have one standard Gaussian finite-dimensional limit after exact law-specific whitening, uniformly over the declared basin. | Proves robust level-5/cylinder-law universality. |

The most important structural consequences are already visible in P3.1,
P4.3, and P6.1.  A bounded rule reaches a global world only by repeated
composition; total curvature can reject globally inconsistent local targets;
and increasing cell count can be geometrically null when it merely subdivides
an unchanged intrinsic surface.

### 4.1 P8.1: exact graph-metric nonuniversality

Let the square coordinate graph have generators
\(\{\pm e_1,\pm e_2\}\), and let the triangular coordinate graph have
generators \(\{\pm e_1,\pm e_2,\pm(e_2-e_1)\}\).  Give every edge length
\(h\).  The exact word distances from the origin are

\[
d_\square(0,(m,n))=|m|+|n|,
\]

and

\[
d_\triangle(0,(m,n))=\max\{|m|,|n|,|m+n|\}.
\]

Each formula follows from a matching lower bound on the coordinate changes
of one allowed step and an explicit path attaining it.  Multiplying by \(h\)
and rounding continuum points to nearby lattice points changes distances by
\(O(h)\).  On bounded pointed sets the two graph-length spaces therefore
converge to polyhedral normed planes.  The square unit ball has four extreme
points; the triangular unit ball has six.  By affine rigidity of surjective
isometries of real normed spaces, an isometry would preserve the number of
extreme points.  Hence the limiting graph metrics are not isometric.

This is a negative control, not a failure of the programme.  It demonstrates
that a common dimension exponent or heat profile cannot identify the entire
geometry.

### 4.2 P8.2: a common finite-dimensional diffusion limit

Embed the square step set as

\[
S_\square=\{\pm(1,0),\pm(0,1)\},
\]

and the triangular step set as

\[
S_\triangle=\{\pm u,\pm v,\pm(u-v)\},
\quad
u=(1,0),\quad v=(1/2,\sqrt3/2).
\]

Choose every step independently and uniformly.  Symmetry gives mean zero.  A
direct calculation gives the same one-step covariance for both laws:

\[
\frac1{|S_A|}\sum_{z\in S_A}zz^{\mathsf T}=\frac12I_2,
\qquad A\in\{\square,\triangle\}.
\]

Their characteristic functions consequently have the common expansion

\[
\varphi_A(\xi)=1-\frac14\lVert\xi\rVert^2
+O(\lVert\xi\rVert^4).
\]

For \(Z_n^A(t)=n^{-1/2}X^A_{\lfloor nt\rfloor}\),

\[
\varphi_A(\xi/\sqrt n)^{\lfloor nt\rfloor}
\longrightarrow
\exp(-t\lVert\xi\rVert^2/4).
\]

For finitely many times, every linear combination of positions decomposes
into disjoint increment blocks.  Independence makes their characteristic
functions multiply, proving convergence to one centered Gaussian process in
finite-dimensional distribution, with

\[
\mathbb E[B_sB_t^{\mathsf T}]=\frac12\min(s,t)I_2.
\]

At spatial edge scale \(h\), accelerating time to \(2h^{-2}\) steps per unit
physical time gives the standard planar Brownian finite-dimensional laws.

The fourth moments of the two microscopic step laws differ, and P8.1 proves
that their graph metrics differ.  P8.2 therefore identifies a genuine but
strictly scoped universality relation.  It does not establish path-space
tightness, filled-disk boundary behavior, a common graph metric, or robustness
to disordered conductance.

### 4.3 P8.3: a robust whitened cylinder-law basin

Fix dimension \(d<\infty\), support bound \(M<\infty\), and
\(0<\kappa\le1\).  Let \(\mathcal P_{M,\kappa}\) be a family of laws on
\(\mathbb R^d\) such that, for \(X\sim P\),

\[
\mathbb E_PX=0,
\qquad
\lVert X\rVert\le M\ \text{almost surely},
\qquad
\kappa I\preceq\Sigma_P\preceq\kappa^{-1}I.
\]

For iid increments define

\[
W_n^P(t)=n^{-1/2}\Sigma_P^{-1/2}
\sum_{j=1}^{\lfloor nt\rfloor}X_j,
\]

where \(\Sigma_P^{-1/2}\) is the exact symmetric covariance whitening for
that law.  For every fixed schedule
\(0=t_0<t_1<\cdots<t_m\) and fixed Cramér--Wold coefficients, the joint
characteristic functions of \(W_n^P\)
converge to those of standard \(d\)-dimensional Brownian motion uniformly in
\(P\in\mathcal P_{M,\kappa}\).

Indeed, \(Y_P=\Sigma_P^{-1/2}X\) has mean zero, identity covariance, and
\(\lVert Y_P\rVert\le M/\sqrt\kappa\).  Taylor's theorem gives the uniform
one-step bound

\[
\mathbb E_Pe^{i\langle c,Y_P\rangle/\sqrt n}
=1-\frac{\lVert c\rVert^2}{2n}+R_{P,n}(c),
\qquad
|R_{P,n}(c)|
\le
\frac{M^3\lVert c\rVert^3}
{6\kappa^{3/2}n^{3/2}}.
\]

Taking powers over each increment block and multiplying the finitely many
uniformly convergent block characteristic functions proves the joint result.
Equivalently, every sequence \(P_n\) in the basin has the same limit; the
multivariate Lévy continuity theorem and Cramér--Wold convert this sequential
statement into uniform finite-dimensional weak convergence.  This is robust
level-5, or cylinder-law, universality only.  It does not cover
estimated whitening, path tightness, semigroup or operator convergence,
boundaries, correlated or state-dependent increments, unbounded or
degenerating laws, metric/object universality, or materials.

The code includes four deliberately different finite step laws in the shared
audit basin \(M=\sqrt2,\kappa=0.3\), plus an unwhitened anisotropic negative
control.  Independent numerical moment and repeated-squaring oracles support
their finite-\(n\) calculations.  These are regression fixtures for the
theorem implementation, not an independently reproduced basin experiment and
not the proof of P8.3.

## 5. Computational methods and finite artifacts

### 5.1 Exact periodic calibration

For an \(m\times n\) square torus with the normalized Laplacian,

\[
\lambda_{p,q}^{\square}
=1-\frac12\left(
\cos\frac{2\pi p}{m}+\cos\frac{2\pi q}{n}
\right).
\]

For the six-neighbor triangular torus,

\[
\lambda_{p,q}^{\triangle}
=1-\frac13\bigl(\cos a+\cos b+\cos(a-b)\bigr),
\quad
a=\frac{2\pi p}{m},\quad b=\frac{2\pi q}{n}.
\]

The implementation sorts these closed-form eigenvalues with multiplicity and
checks small instances against the independent dense symmetric eigensolver in
the Global Geometry I core.  It then evaluates

\[
H(t)=\frac1N\sum_j e^{-t\lambda_j},
\qquad
d_s(t)=2t\frac{\sum_j\lambda_j e^{-t\lambda_j}}
{\sum_j e^{-t\lambda_j}}
\]

on a frozen time grid.  The calibration protocol uses six registered sizes
\([16,24,36,54,81,120]\), requires a nontrivial intermediate window, and
includes an equal-size cycle as a one-dimensional negative control.  The
generated finite result is labeled a calibrated profile candidate.  It is not
a common metric-object, operator-limit, or continuum theorem.

### 5.2 Deterministic bounded disk ensembles

Four filled-disk constructions implement distinct local motifs:

| Family | Microscopic construction |
|---|---|
| `square-alternating` | Square cells triangulated by a parity-alternating diagonal. |
| `triangular-clipped` | An equilateral triangular lattice clipped to a declared bounded domain. |
| `cell-center-fan` | A center vertex and four triangular fans inside every square cell. |
| `square-hashed-diagonal` | A coordinate-hashed diagonal choice giving quenched local combinatorial disorder. |

Every family specification declares characteristic spacing, domain, boundary,
metric, conductance law, generator seed, and resource policy.  Construction
uses canonical coordinates; generated carriers are deeply immutable.  The
engine binds both a combinatorial digest and a realization digest, so changes
to connectivity and changes to lengths or conductances cannot be conflated.
Raw validation is fail closed: sparse arrays, repeated identities, invalid
faces, nonpositive or nonfinite metric data, closure mismatches, and rebound
digests are rejected rather than repaired.

For accepted exact-small disks, the base core recomputes \(\mathbb F_2\)
Betti numbers, Euler characteristic, boundary components, surface links, and
angle-defect Gauss--Bonnet.  Metric and curvature evaluations are identified
as binary64 audits of proved finite identities; topology remains an exact
finite combinatorial result.

### 5.3 The preview atlas is not universality evidence

The generated preview specification uses the four families, sizes
\([3,4,6]\), conductance-disorder parameters \(\sigma\in\{0,0.75\}\), and
two replicates.  The artifact contains 48 runs grouped into 24 exact-member
cells.  It reports 39 unique realized structures; duplicates are disclosed
rather than counted as independent evidence.

Each run records exact finite disk gates, finite dense-spectrum diagnostics,
Dirichlet transport, and one signed conductance response obtained by
multiplying the first canonical edge conductance by 1.01.  The transport
solver requires a finite positive network, reports residual and update
stopping diagnostics, and is checked against independent finite fixtures.
Rayleigh monotonicity is a control on that single perturbation, not a
robustness theorem.

The displayed dimension values are explicitly named unvalidated finite
descriptors.  No plateau is selected, no ensemble interval is inferred, no
negative-control matrix is run, and no continuum fit is attempted.  Every
cell carries

```text
universalityStatus: NOT_EVALUATED
```

and the artifact withholds scaling-window, refinement-convergence,
universality, continuum, and material claims.  Its scientific purpose is to
validate deterministic construction, measurement, provenance, and failure
semantics before confirmatory computation.

### 5.4 A finite-resolution map inside the proved diffusion basin

To turn the robust P8.3 statement into a parameter experiment, define the
centered square step law

\[
\mathbb P(X=\pm e_1)=\frac p2,
\qquad
\mathbb P(X=\pm e_2)=\frac{1-p}{2}.
\]

Its covariance is \(\operatorname{diag}(p,1-p)\).  The frozen audit uses
\(p\in\{0.3,0.4,0.5,0.6,0.7\}\), so every row remains in the declared
nondegenerate basin, and sample sizes
\(n\in\{200,632,2000,6325,20000\}\).  After exact law-specific whitening,
each cell reports the maximum characteristic-function error over the three
predeclared Fourier directions used by the four-law control.

The display classifies a cell as `within-resolution-guard` when this finite
error is at most \(5\times10^{-5}\).  At \(n=2000\), the \(p=0.3\) and
\(p=0.4\) rows remain just above the guard, while the other three rows lie
below it; by \(n=6325\), all five lie below.  Every row decreases strictly
across the registered sample sizes.  This is a deterministic finite-size
resolution map supporting the audit of P8.3.  The threshold is a disclosed
visualization and diagnostic rule, not a singularity, thermodynamic phase
boundary, or additional convergence theorem.

## 6. Obstruction-aware inverse design

### 6.1 Why the compiler is staged

Inverse design is not represented as one optimizer.  A failed optimization
does not prove nonexistence, and a passed necessary condition does not prove a
target is realizable.  The compiler therefore orders finite gates:

| Gate | Question |
|---|---|
| G0 | Is the request closed, finite, bounded, and supported? |
| G1 | Is the supplied complex a valid declared triangular surface with the requested topology? |
| G2 | Does every target defect satisfy the strict local cone upper bound? |
| G3 | Does the target satisfy the exact or interval-separated Gauss--Bonnet total? |
| G4 | For a verified closed weighted circle-packing model, does every proper nonempty subset satisfy the Chow--Luo inequality? |
| G5 | If a supported disk theorem is requested, does a separately verified symmetric double justify using the closed theorem? |
| G6 | Are all candidate lengths positive and all face inequalities strictly satisfied? |

Results are `PASS`, `FAIL`, `MARGINAL`, or `INCONCLUSIVE`; individual gates
can also be `NOT_APPLICABLE` or `NOT_RUN`.  Only a theorem instance,
combinatorial identity, or exhaustive finite check may set
`impossibleInDeclaredModel: true`.  Floating Gauss--Bonnet proximity does not
unlock the exact Chow--Luo theorem.  A bounded search that finds no violating
subset is inconclusive unless exhaustive coverage is certified.

The first implemented models are:

- **CP:** a Euclidean weighted circle-packing metric, with tangency law
  \(\ell_{ij}=r_i+r_j\) in the representative cases;
- **EM:** explicitly supplied positive edge lengths with strict face
  inequalities; and
- **QV:** equilateral integer-valence modules used by the q-star sheet.

Extrinsic shell equilibrium, fabrication, sensing, and actuation are separate
engineering layers.  Intrinsic feasibility never implies a unique or
stress-free embedding in \(\mathbb R^3\).

### 6.2 Representative pass certificates

The `tetra-uniform-pass` request is a tetrahedral sphere with target defect
\(K_i=\pi\) at every vertex.  The compiler verifies the finite sphere
topology, the symbolic total \(4\pi\), all 14 nonempty proper subsets, and a
strict positive minimum Chow--Luo slack of \(\pi\).  The equal-radius
reference metric has positive triangle margin.  Within the verified closed
tangency circle-packing model, this is a theorem-backed finite admission and a
realized symmetric reference case.

It is not evidence for a general geometry compiler, continuum sphere
convergence, extrinsic embedding uniqueness, material feasibility, or
fabrication readiness.

Three direct edge-metric cases exercise different topology classes without
invoking the closed circle-packing theorem:

| Request | \((V,E,F)\) | \((\beta_0,\beta_1,\beta_2)\) | Boundary components |
|---|---:|---:|---:|
| `triangle-valid-pass` | \((3,3,1)\) | \((1,0,0)\) | 1 |
| `annulus-valid-pass` | \((10,20,10)\) | \((1,1,0)\) | 2 |
| `torus-valid-pass` | \((9,27,18)\) | \((1,2,1)\) | 0 |

All three use unit intrinsic edge lengths.  The compiler checks the declared
surface, topology, and every face’s exact binary64-dyadic strict-triangle
sign, then returns an immutable radius-zero local programme that preserves
the supplied edge metric.  These are successful intrinsic finite candidates,
not embeddings, optimized actuators, continuum refinements, or proofs that an
arbitrary target geometry is compilable.

### 6.3 Representative obstruction certificates

The `tetra-subset-reject` target is

\[
\left(-\frac{6\pi}{5},
\frac{26\pi}{15},
\frac{26\pi}{15},
\frac{26\pi}{15}\right).
\]

It passes every local upper bound and its symbolic total is \(4\pi\), so a
Gauss--Bonnet-only compiler would admit it.  Exhaustive subset evaluation
instead finds the singleton \(I=\{0\}\) with

\[
\Delta_{\mathrm{CL}}(I)=-\frac\pi5.
\]

The report binds the subset, its full-subcomplex Euler characteristic, its
link terms, target curvature mass, signed slack, exact subset-ledger digest,
and repair direction.  It is impossible in that declared tangency
circle-packing class, not impossible for every metric or sheet model.

Two simpler failures anchor the gate order.  A tetrahedral sphere with zero
target defect at all vertices is rejected at G3 because \(0\ne4\pi\).  A
single face with edge vector \((1,1,2)\) is rejected at G6: the exact sign of
the supplied binary64 dyadic margin is zero.  Later model and optimization
gates are not presented as having run.

### 6.4 Certificate integrity

The normalized request and report use exact binary64-preserving canonical
serialization.  Accessors, class instances, sparse arrays, symbols used to
spoof object identity, unsafe numeric magnitudes, and derived-edge resource
overruns fail before mathematical gates.  Exhaustive subset searches can
stream the complete ledger digest while bounding displayed witness rows.
Report validation recompiles the normalized request and compares the entire
deterministic report; merely changing a result and rebinding its public digest
does not create a valid certificate.

## 7. Programmable q-star sheet and digital HIL instrument

### 7.1 Exact intrinsic programme

Join \(q\) equilateral triangular faces cyclically around one center.  The
result is a disk with

\[
|V|=q+1,\qquad |E|=2q,\qquad |F|=q,\qquad\chi=1.
\]

Each triangle contributes a center angle \(\pi/3\).  Hence

\[
K_c=2\pi-q\pi/3=\frac{(6-q)\pi}{3}.
\]

Every outer boundary vertex receives two \(\pi/3\) corners, so
\(K_b=\pi/3\).  The global budget is exact:

\[
K_c+\sum_{b=1}^qK_b=2\pi.
\]

The three programmed states are therefore

| State | Exact center defect | Intrinsic statement only |
|---|---:|---|
| \(q=5\) | \(+\pi/3\) | positive discrete cone defect |
| \(q=6\) | \(0\) | a flat intrinsic configuration is available |
| \(q=7\) | \(-\pi/3\) | negative discrete cone defect |

Adding or removing one local sector changes the center defect by exactly
\(\mp\pi/3\) while preserving disk topology.  The metric does not uniquely
choose an extrinsic fold, especially at \(q=7\).

### 7.2 Virtual plant, sensing, and controller contract

The alpha sheet module exposes a bounded virtual plant rather than hardware.
Its intrinsic reference, schematic nonunique embedding branch, actuator
bounds, pending commands, and state revision are explicit.  A synthetic
measurement is bound to a particular plant identity, state revision, state
digest, and snapshot digest.  It separately reports ideal symbolic intrinsic
geometry, synthetic camera-like extrinsic estimates, calibration, noise, and
observability.  Missing target-critical faces or stale calibration produces
`SENSOR_UNOBSERVABLE`.  This synthetic observability predicate is not camera
calibration, camera observability, or physical validation.

The human-in-the-loop planner can recommend one `ADD_SECTOR` or
`REMOVE_SECTOR` action only when the predicted reduction exceeds its edit
cost.  Issuing a recommendation does not update the asserted assembly state;
a fresh measurement is required.

### 7.3 Hardware-in-the-loop is engineering evidence only

The in-memory `ggii-hil/2` emulator uses the same bounded message vocabulary
intended for a future adapter, but declares

```text
virtualOnly: true
hardwareAccess: false
transport: in-memory-only
```

Its contract includes session-bound arm epochs, monotone sequence numbers,
observation-bound commands, position and rate limits, watchdog hold, stale or
corrupt message rejection, a latched emergency stop, and deterministic fault
injection.  Accepted commands consume their authorizing observation.  State
snapshots and measurements have content digests; full request/response/state
events form a bounded transcript hash chain.

These mechanisms are safety and replay properties of a digital model.  No
serial, USB, camera, network, filesystem, timer, or device-discovery interface
is opened; no actuator is connected; and no physical sheet response has been
observed.  CRC32 is frame-corruption detection, not authentication.  The
SHA-256/JCS bindings establish reproducible content and state linkage, not
transport authentication.  The shell branch, camera noise, and actuator
response are engineering assumptions rather than calibrated constitutive or
sensor laws.

### 7.4 Fabrication-ready passive package

The digital release includes a separate
[programmable-sheet experiment manual](GLOBAL_GEOMETRY_II_SHEET_EXPERIMENT.md)
and three standalone A4 SVG templates for (q=5,6,7).  Each drawing contains
detached nominal 60 mm equilateral faces, cyclic seam instructions, cut and
fold-hinge conventions, non-decodable fiducial locations, horizontal and
vertical scale checks, and explicit `NO ACTUATORS`, `NOT A CONTROL DRAWING`,
and `NOT RUN` warnings.  A read-only validator checks the vector contract and
the SHA-256 fabrication manifest.

This makes the package fabrication-ready in the narrow sense that a reviewed
passive protocol, drawings, dimension checks, reconstruction plan,
uncertainty budget, safety boundary, and acceptance/falsification rules are
specified.  It does not mean that printing, cutting, assembly, camera
calibration, actuation, or physical validation occurred.  Those states remain
`NOT_RUN`, and no material purchase or bench action is authorized by this
manuscript.

## 8. Evidence summary

| Result | Primary label | Reproducible support | Established | Explicitly withheld |
|---|---|---|---|---|
| P3.1--P6.1 | proved / proved-here | foundations, machine-readable claim ledger, focused fixtures | Finite causal, compatibility, invariant, rigidity, replay, and null-refinement statements in their hypotheses | Compactness, arbitrary topology rewrite, continuum limits |
| P8.1 | proved / proved-here | exact word-distance and unit-ball fixtures; calibration artifact | Nonisometric graph-metric limits for the declared square/triangular generators | No obstruction to a shared diffusion law or common PE metric |
| P8.2 | proved / proved-here | moment and characteristic-function calculation; finite convergence audit | Common covariance-normalized Gaussian finite-dimensional limit | Path-space tightness, boundaries, disorder, metric equivalence |
| P8.3 | proved / proved-here | uniform Taylor remainder and increment-block argument; four-law fixture; 5-by-5 anisotropy/size resolution map | Robust standard-Gaussian cylinder-law basin after exact law-specific whitening; finite crossover audit within that basin | Estimated whitening, paths, operators, boundaries, correlated/state-dependent/unbounded laws, metric or material universality |
| Periodic spectral calibration | computational | closed Fourier spectra, dense small-instance oracle, frozen six-size protocol, cycle control | A finite profile-equivalence candidate under the frozen estimator and thresholds | Common operator limit, full geometry, bounded-disk U2 |
| Four filled-disk generators | exact finite topology plus binary64 metric/curvature audits | deterministic immutable generator records and strict validator | Reproducible distinct finite construction families in the preview bounds | Limit existence or universality |
| Preview atlas | computational | SHA-256-addressed artifact; 48 runs, 24 cells, 39 unique realizations | Deterministic small finite topology, spectrum, transport, and one-edge response records | Scaling windows, uncertainty, phase classification, robustness, universality |
| Tetrahedral CP admission | exact finite theorem instance and exhaustive check | inverse certificate artifact | Admission inside the checked closed tangency CP class | General compiler completeness, extrinsic or material feasibility |
| Disk, annulus, and torus edge metrics | exact finite identity and exhaustive face check | inverse certificate artifact | Three topology-distinct positive intrinsic metric candidates | Embedding, optimization, refinement convergence, or physical response |
| CP, Gauss--Bonnet, and triangle obstructions | exact finite theorem instance or exhaustive check | witnesses \(-\pi/5\), \(-4\pi\), and zero triangle margin | Impossibility in each precisely declared finite model | Impossibility in unrelated metric/material classes |
| q-star intrinsic budgets | exact finite identity | symbolic q-star constructor and focused fixtures | \(+\pi/3,0,-\pi/3\) center defects and total \(2\pi\) | A unique 3-D shape or a fabricated response |
| Virtual sheet/HIL | engineering | bounded plant, synthetic measurement, protocol, safety-state, and transcript contracts | Deterministic digital model behavior in the implemented envelope | Physical hardware, material response, and camera/device instrumentation, including Windows instrumentation |
| Bounded Darwin/Windows digital replay | computational | content-addressed `macos-local-v2.json`, `windows-local-v1.json`, and external comparison record | Equality of the declared manifest, release-index, source, scientific-artifact, reproduction-resource, and canonical nine PASS suite identity/path surface | Suite-output or performance equality; confirmatory U2; vision/device/hardware instrumentation; physical validation; authentication or publication approval |

## 9. Reproducibility

### 9.1 Source and artifact map

The mathematical and implementation contracts are:

- [formal foundations](GLOBAL_GEOMETRY_II_FOUNDATIONS.md);
- [universality specification](GLOBAL_GEOMETRY_II_UNIVERSALITY_SPEC.md);
- [inverse-design and sheet specification](GLOBAL_GEOMETRY_II_INVERSE_SHEET_SPEC.md);
- [programmable-sheet experiment manual](GLOBAL_GEOMETRY_II_SHEET_EXPERIMENT.md);
- [implementation and evidence plan](GLOBAL_GEOMETRY_II_IMPLEMENTATION_PLAN.md);
- [Global Geometry I baseline](GLOBAL_GEOMETRY_LAB.md).

The dependency-free browser/Node modules are:

- [`global-geometry-ii-core.js`](website/global-geometry-lab/global-geometry-ii-core.js), version `0.2.0-alpha.5`, schema 2;
- [`global-geometry-ii-ensembles.js`](website/global-geometry-lab/global-geometry-ii-ensembles.js), version `0.2.0-alpha.3`, family schema `gg.atlas.family-preview/1`;
- [`global-geometry-ii-atlas.js`](website/global-geometry-lab/global-geometry-ii-atlas.js), version `0.2.0-alpha.2`, pilot schema `gg.atlas.pilot/1`;
- [`global-geometry-ii-inverse.js`](website/global-geometry-lab/global-geometry-ii-inverse.js), version `0.1.0-alpha.2`, schema 2; and
- [`global-geometry-ii-sheet.js`](website/global-geometry-lab/global-geometry-ii-sheet.js), version `0.2.0-alpha.1`, schema 2, HIL protocol `ggii-hil/2`.

Current generated artifacts are:

- [calibration artifact](artifacts/global-geometry-ii/calibration-v1.json);
- [atlas preview artifact](artifacts/global-geometry-ii/atlas-pilot-v1.json);
- [inverse certificates](artifacts/global-geometry-ii/inverse-certificates-v1.json); and
- [virtual sheet/HIL artifact](artifacts/global-geometry-ii/sheet-hil-v1.json).

The passive fabrication resources are the
[fabrication manifest](artifacts/global-geometry-ii/fabrication/fabrication-manifest.json),
its three q-star SVGs, and the read-only vector validator in the same
directory.  The release manifest and generated evidence index bind these
resources into the clean-room package.

The bounded platform records are
[macos-local-v2.json](artifacts/global-geometry-ii/certificates/macos-local-v2.json),
[windows-local-v1.json](artifacts/global-geometry-ii/certificates/windows-local-v1.json),
and their
[content-addressed comparison](artifacts/global-geometry-ii/certificates/macos-windows-comparison-v1.json).
The sheet artifact and those replay records are digital evidence, not physical
measurements.  No camera calibration, physical response, device discovery, or
hardware instrumentation has been performed.

### 9.2 Focused verification

From the repository root, the focused suites are invoked with:

```bash
node website/global-geometry-lab/test-global-geometry-core.js
node website/global-geometry-lab/test-global-geometry-ii-core.js
node website/global-geometry-lab/test-global-geometry-ii-ensembles.js
node website/global-geometry-lab/test-global-geometry-ii-atlas.js
node website/global-geometry-lab/test-global-geometry-ii-inverse.js
node website/global-geometry-lab/test-global-geometry-ii-sheet.js
node website/global-geometry-lab/test-global-geometry-ii-artifacts.js
node artifacts/global-geometry-ii/fabrication/validate-fabrication.js
node website/global-geometry-lab/test-global-geometry-ii-reproduction.js
```

Their contract includes exact finite fixtures, deterministic replay,
relabeling invariance, immutable digest binding, hostile-data validation,
independent transport or spectrum oracles, scientific false-positive tests,
inverse certificate replay, and HIL safety transitions.  A release candidate
requires all suites to pass together from a clean checkout.  This manuscript
does not treat a test count as scientific evidence.

The four scientific JSON artifacts are regenerated with:

```bash
node website/global-geometry-lab/generate-global-geometry-ii-calibration.js
node website/global-geometry-lab/generate-global-geometry-ii-atlas.js
node website/global-geometry-lab/generate-global-geometry-ii-inverse.js
node website/global-geometry-lab/generate-global-geometry-ii-sheet.js
```

The generators recompute payloads before applying canonical SHA-256 content
addresses.  If publication is separately approved, its bundle must record the
source commit, clean/dirty state, Node version, operating system, exact
artifact hashes, and the declared floating comparison policy.  Exact
combinatorial records should reproduce
byte-for-byte; floating results use schema-aware tolerances unless an exact or
outward-rounded certificate is supplied.

### 9.3 Scoped cross-platform replication boundary

Each local input remains a single-run record: neither
`macos-local-v2.json` nor `windows-local-v1.json` makes a cross-platform
claim.  Cross-platform status is delegated exclusively to
`macos-windows-comparison-v1.json`.  That content-addressed comparison reports
`PASS_FOR_DECLARED_DIGEST_AND_TEST_SURFACE` because the two inputs agree on the
declared manifest, release-index, source, scientific-artifact,
reproduction-resource, and canonical nine focused PASS suite identities and
paths.

This closes only the bounded alpha software-replay surface named by that
record.  It does not compare suite stdout, stderr, timing, or performance; it
does not establish floating-point equality outside the addressed artifacts;
and it does not certify confirmatory U2 batches, camera or device behavior,
hardware, a physical sheet, authentication, machine independence, scientific
completeness, peer review, priority, or publication approval.  Any enlarged
surface requires new local certificates and a new comparison record.

## 10. Preregistered next experiments

### 10.1 Confirmatory U2 atlas

The preregistered U2 candidate concerns bounded-valence, finite-range planar
disk triangulations with uniformly elliptic conductances.  The confirmatory
matrix fixes four construction families, sizes
\([16,24,36,54,81,120]\), disorder parameters
\([0,0.25,0.75,\log4]\), and 32 declared replicate or root/probe streams.
It measures matched volume, heat, walk, topology, curvature, transport, and
perturbation profiles.

Before outcomes are inspected, the release must retain the registered
equivalence margins, finite-size rule, alternate estimators, and strong
controls: comb traps, small-world shortcuts, critical or nonelliptic bonds,
vanishing necks, perforations, and degree-preserving rewires.  The result will
be classified as accepted, rejected, or unresolved in its preregistered record.
Any publication remains separately approval-gated.  The current preview is not
part of this confirmation.

### 10.2 Strengthen the diffusion theorem

P8.2 and the robust cylinder-law basin P8.3 should be extended, without
changing their present scopes, by proving or properly citing and
hypothesis-checking a functional invariance principle in path space.  Separate
programmes should then examine estimated covariance calibration, reflecting
boundaries, uniformly elliptic disorder, and convergence of Dirichlet forms.
None of those extensions may infer a common graph metric contradicted by
P8.1.

### 10.3 Common-metric positive control

Construct two genuinely different triangulations of the same facewise
piecewise-Euclidean flat domain and use consistently scaled finite-element or
cotangent energies.  This tests a stronger common metric-measure-operator
claim while retaining the original graph metrics as a nonuniversality
control.

### 10.4 Inverse compiler expansion

Implement and verify symmetric doubling for a bounded disk subclass, add
three-level curvature-measure refinement, and preserve `INCONCLUSIVE` whenever
subset search or optimization is incomplete.  A proof-producing separation
method is needed before large circle-packing targets can receive exhaustive
certificates.  Extrinsic shell synthesis remains a separate engineering
problem.

### 10.5 Passive programmable-sheet experiment

Begin from the generated, vector-validated q-star templates, then verify
physical print scale and edge lengths before assembly.  After explicit
approval, assemble at least five randomized trials for each \(q=5,6,7\), and
measure face poses only after camera calibration is frozen.  The exact
intrinsic defect is the control; observed height, dihedral, and shape are the
experiment.  Invalid or occluded trials remain in the record.  No purchase,
printing, cutting, assembly, or camera work is authorized by this manuscript.

### 10.6 Scoped cross-platform replication and future instrumentation

The bounded alpha source/artifact/test snapshot has the scoped comparison
described in section 9.3.  That result must not be reused as a certificate for
the confirmatory U2 batch, prerecorded-vision reconstruction, device
discovery, camera calibration, or hardware-in-the-loop instrumentation.  Each
such extension needs a new frozen surface, new Darwin and Windows local
records, and a new content-addressed comparison.  Device, camera, and hardware
work additionally requires explicit approval.  None of these records confers
publication, merge, or hardware authorization.

## 11. Application boundary

The framework is potentially useful for networks, learned data geometry,
programmable materials, morphogenesis, distributed robotics, and relational
models of spacetime.  What transfers is the discipline of declaring the
carrier, metric, measure, operator, locality, obstruction, and observation
scale.  Domain adequacy does not transfer automatically.  A network curvature
descriptor does not by itself predict resilience; a pattern does not identify
a biological mechanism; a synchronous simulation is not a robot controller;
and a graph with a selected spectral dimension is not physical spacetime.

The programmable sheet is the nearest application because its discrete
curvature budget is directly auditable.  Even there, intrinsic compatibility,
extrinsic embeddability, mechanical selection, observability, and fabrication
are five different questions.

## 12. Ethics, safety, and non-claims

No human-subject, biological, or clinical inference is made.  The proposed
camera protocol frames the apparatus only, processes locally by default, and
does not call for ambient audio or unrelated video.  Derived fiducial poses
are preferred over raw room footage.

The first physical option, if separately approved, uses cardstock, scissors,
low-tack hinges, and no chemicals, lasers, or magnets.  Sharp tools require a
cutting mat and appropriate supervision.  A q=7 patch must not be forced flat
or pushed toward the face.  Any later active tier requires low-voltage,
current-limited power, guarded pinch points, mechanical and software travel
limits, watchdog hold, a latched emergency stop, and a physical power
disconnect.  The present software has no hardware access.

This work does **not** claim:

- a proved bounded-disk U2 universality class;
- a common square/triangular graph metric or full geometry;
- path-space, operator, or material convergence from P8.2;
- a complete inverse compiler for arbitrary curvature, topology, dimension,
  or transport targets;
- that Gauss--Bonnet alone is sufficient for realizability;
- that failure to find a numerical candidate proves nonexistence;
- a unique embedding of any compatible intrinsic metric in \(\mathbb R^3\);
- calibrated shell, camera, actuator, or material parameters;
- fabricated q-star results or physical validation;
- cross-platform equality outside the comparison record's declared
  digest-and-focused-test surface;
- literature priority for the component mathematics; or
- publication, peer review, or protected-branch release.

## 13. Discussion

The main theoretical lesson is that “global geometry” is a bundle of
structures rather than one picture.  The same microscopic pair can converge
together after one projection and remain separated after another.  P8.1 and
P8.2 make this exact: covariance matching removes the difference relevant to
finite-dimensional diffusion, while shortest-path geometry retains the
direction set as a polyhedral norm ball.

This resolves an apparent tension in emergence.  Large-scale order need not
mean that every microscopic fact is forgotten.  A scaling limit is a
structure-selective compression.  Symmetry, conservation, locality,
covariance, boundaries, and obstruction classes decide what survives.  A
responsible universality statement must therefore say not just “these rules
look the same,” but “these rescaled marked objects converge in this topology,”
or, at finite resolution, “these preregistered observable laws agree while
these controls remain separated.”

The inverse perspective supplies the complementary lesson.  Local programmes
cannot be designed solely by minimizing a global picture error.  Exact
compatibility comes first.  A curvature target can obey every pointwise bound
and the total Gauss--Bonnet budget yet violate a subset obstruction.  When that
happens, failure is explanatory: the certificate names the smallest local
region whose requested curvature mass cannot be glued into the declared
global model.

The q-star then makes the logic tangible.  One local sector changes one
discrete defect, the boundary defects compensate so that Gauss--Bonnet remains
global, and the sheet must choose an extrinsic response.  The intrinsic law is
exact; the visible shape is a mechanical experiment.  Keeping those statements
separate is not a limitation of Global Geometry II but its organizing method.

## 14. Conclusion

Purely local rules can produce global geometry because local patches share
incidence and metric data, repeated bounded updates propagate influence, and
refinement selects stable macroscopic structures.  The resulting world is not
arbitrary.  Compatibility glues it; topology, curvature, spectrum, and
conservation constrain it; boundaries and dynamics select among admissible
states; and the declared observation topology decides which microscopic
features disappear.

Global Geometry II turns that answer into a research instrument with three
outputs: forward families and observable profiles, inverse candidates and
obstruction witnesses, and recognition limits from local indistinguishability.
Its strongest current conclusion is deliberately nuanced: the square and
triangular examples share one proved cylinder-law diffusion limit while
retaining different proved graph-metric limits, and P8.3 robustifies the
finite-dimensional statement only after exact covariance whitening over a
bounded iid basin.  The confirmatory atlas, physical sheet, and replication
beyond the bounded comparison record's declared surface will test how far
that structure-relative view of emergence can be extended.

## Bibliography

Only primary mathematical, computational, and experimental sources already
cited in the project specifications are listed.  They anchor ingredients of
the framework and do not establish a literature-priority claim for their
assembly.

1. T. Regge, “General Relativity Without Coordinates,” *Il Nuovo Cimento* 19
   (1961), 558--571. [DOI](https://doi.org/10.1007/BF02733251).
2. J. Cheeger, W. Müller, and R. Schrader, “On the Curvature of Piecewise Flat
   Spaces,” *Communications in Mathematical Physics* 92 (1984), 405--454.
   [DOI](https://doi.org/10.1007/BF01210729).
3. M. Desbrun, A. N. Hirani, M. Leok, and J. E. Marsden, “Discrete Exterior
   Calculus” (2005). [arXiv](https://arxiv.org/abs/math/0508341).
4. I. Benjamini and O. Schramm, “Recurrence of Distributional Limits of
   Finite Planar Graphs,” *Electronic Journal of Probability* 6 (2001).
   [DOI](https://doi.org/10.1214/EJP.v6-96).
5. K.-T. Sturm, “On the Geometry of Metric Measure Spaces,” *Acta
   Mathematica* 196 (2006). [DOI](https://doi.org/10.1007/s11511-006-0002-8).
6. K. Kuwae and T. Shioya, “Convergence of Spectral Structures: A Functional
   Analytic Theory and Its Applications to Spectral Geometry,” *Communications
   in Analysis and Geometry* 11 (2003).
   [DOI](https://doi.org/10.4310/CAG.2003.v11.n4.a1).
7. B. Chow and F. Luo, “Combinatorial Ricci Flows on Surfaces,” *Journal of
   Differential Geometry* 63 (2003), 97--129.
   [Primary paper](https://sites.math.rutgers.edu/~fluo/mpapers/combinatorial%20Ricci%20flow%20in%20dimension%202.pdf).
8. X. D. Gu, F. Luo, J. Sun, and T. Wu, “A Discrete Uniformization Theorem for
   Polyhedral Surfaces,” *Journal of Differential Geometry* 109 (2018).
   [DOI](https://doi.org/10.4310/jdg/1527040872).
9. D. Cohen-Steiner, H. Edelsbrunner, and J. Harer, “Stability of Persistence
   Diagrams,” *Discrete & Computational Geometry* 37 (2007).
   [DOI](https://doi.org/10.1007/s00454-006-1276-5).
10. Z.-Q. Chen, D. Croydon, and T. Kumagai, “Quenched Invariance Principles for
    Random Walks and Elliptic Diffusions in Random Media with Boundary,”
    *Annals of Probability* 43 (2015).
    [DOI](https://doi.org/10.1214/14-AOP914).
11. S. Mazur and S. Ulam, “Sur les transformations isométriques d'espaces
    vectoriels normés,” *C. R. Acad. Sci. Paris* 194 (1932), 946--948.
12. E. Grinspun, A. N. Hirani, M. Desbrun, and P. Schröder, “Discrete Shells,”
    SCA 2003, 62--67. [DOI](https://doi.org/10.2312/SCA03/062-067).
13. Y. Klein, E. Efrati, and E. Sharon, “Shaping of Elastic Sheets by
    Prescription of Non-Euclidean Metrics,” *Science* 315 (2007), 1116--1120.
    [DOI](https://doi.org/10.1126/science.1135994).
14. E. Efrati, E. Sharon, and R. Kupferman, “Elastic Theory of Unconstrained
    Non-Euclidean Plates,” *Journal of the Mechanics and Physics of Solids* 57
    (2009), 762--775.
    [DOI](https://doi.org/10.1016/j.jmps.2008.12.004).
15. Z. Zhang, “A Flexible New Technique for Camera Calibration,” *IEEE
    Transactions on Pattern Analysis and Machine Intelligence* 22 (2000),
    1330--1334. [DOI](https://doi.org/10.1109/34.888718).
16. S. Garrido-Jurado, R. Muñoz-Salinas, F. J. Madrid-Cuevas, and M. J.
    Marín-Jiménez, “Automatic Generation and Detection of Highly Reliable
    Fiducial Markers under Occlusion,” *Pattern Recognition* 47 (2014),
    2280--2292. [DOI](https://doi.org/10.1016/j.patcog.2014.01.005).
