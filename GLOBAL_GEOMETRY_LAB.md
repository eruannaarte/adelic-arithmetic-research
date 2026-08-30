# Global Geometry Lab: research and implementation plan

## Status and purpose

This document turns the proposed Global Geometry programme into an executable
research contract.  The companion browser laboratory is a finite numerical
model.  It is designed to make local-to-global mechanisms inspectable without
confusing a demonstration, a finite computation, and a theorem.

The programme has three directions:

\[
\textbf{Forward:}\quad \text{local rule}\longrightarrow\text{global geometry},
\]

\[
\textbf{Inverse:}\quad \text{target geometry}\longrightarrow\text{local rule},
\]

\[
\textbf{Recognition:}\quad \text{finite observations}\longrightarrow
\text{compatible geometric descriptors and ambiguity}.
\]

The first laboratory release implements all three over one shared finite
metric-measure-cell-complex model.  Application presets are parameterizations
of this model, not independent animations.

### Implementation ledger

| Phase | Research question made executable | Artifact | Release status |
|---|---|---|---|
| 1. Contract | What is state, locality, evidence, and a valid claim? | Sections 1--4 and 8 | complete |
| 2. Forward / inverse / recognition core | Can one engine generate, program, and diagnose finite geometry? | deterministic JavaScript core and closed configuration schema | complete |
| 3. Obstructions and observables | Do topology, manifold validity, Gauss--Bonnet, spectra, and three dimension clocks fail closed? | exact GF(2) topology plus gated numerical analyzers | complete |
| 4. Programmable laboratory | Can a user perturb, replay, compare, inspect, and export an experiment? | accessible browser laboratory with nine presets | complete |
| 5. Application transfer | Can the mathematics be reused without overstating domain validity? | six explicitly bounded application mappings | complete |
| 6. Verification | Are numerical, configuration, interaction, accessibility, and responsive-layout contracts enforced? | 26 automated core checks plus live browser QA | complete |

“Complete” means implemented and verified for this finite first release.  It
does not mean that the continuum, universality, realizability, or empirical
research targets listed later have been proved.

## 1. Mathematical state

At simulation step \(n\), the laboratory state is

\[
\mathfrak G_n=(K_n,\ell_n,\mu_n,W_n,U_n,\Pi_n),
\]

where:

- \(K_n=(V_n,E_n,F_n)\) is a finite graph or two-dimensional simplicial
  complex;
- \(\ell_n:E_n\to\mathbb R_{>0}\) supplies intrinsic local lengths;
- \(\mu_n:V_n\to\mathbb R_{>0}\) supplies vertex measure.  Release 1 uses
  counting measure for metric-ball volume and the explicitly different
  degree-weighted measure associated with random-walk diffusion;
- \(W_n:E_n\to\mathbb R_{>0}\) supplies transport conductance;
- \(U_n\) is one or more scalar fields carried by vertices; and
- source coordinates initialize lengths for embedded presets; \(\Pi_n\) is
  the browser projection of those coordinates.  Once stored, \(\ell_n\) is
  authoritative, and changing only \(\Pi_n\) cannot change an intrinsic
  observable.

The induced global distance is the shortest-path length

\[
d_n(x,y)=\inf_{\gamma:x\leadsto y}\sum_{e\in\gamma}\ell_n(e).
\]

The transport operator is the symmetric normalized graph Laplacian

\[
L_n=I-D_n^{-1/2}W_nD_n^{-1/2}.
\]

This is unitarily equivalent to random-walk diffusion with degree-weighted
measure.  It need not encode the same scale as the counting-measure metric
balls; the lab reports that distinction rather than assuming one continuum
geometry.  Topology is computed from the boundary maps of \(K_n\) over
\(\mathbb F_2\), not inferred from the drawing.

## 2. Locality contract

A dynamics is local with radius \(R\) when the update at a vertex, edge, or
face depends only on its radius-\(R\) combinatorial neighbourhood and declared
global constants.  One laboratory step has the form

\[
\mathfrak G_{n+1}=F_R(\mathfrak G_n;\theta).
\]

The implementation does not evaluate user-supplied code.  A configuration
selects from a closed vocabulary of generators, local laws, target fields, and
measurement schedules.  This makes configurations serializable, replayable,
and testable.

Every operation receives an explicit locality label:

- **L0 -- strictly local:** radius-\(R\) state and fixed constants only;
- **L1 -- local with broadcast:** a local update also receives a disclosed
  global scalar, normalization, boundary value, or precomputed target; and
- **L2 -- globally mediated:** an eigensolve, equilibrium solve, centralized
  optimization, or other whole-state operation participates.

For an L0 synchronous rule on fixed adjacency, a perturbation has an exact
causal cone: after \(t\) steps it cannot influence a cell farther than \(Rt\).
An intervention that rewrites adjacency ends that fixed-graph claim.  An L2
analysis may measure the resulting state, but its output is not silently fed
back into an L0 runtime rule.  In particular, inverse target synthesis is a
disclosed pre-runtime global compilation; the runtime law that attempts to
realize the target remains radius-one and synchronous.

Local laws must also be equivariant under relabeling.  Renaming vertex IDs may
change serialization order but must not change intrinsic observables.

The first release includes three local mechanisms and a separate intervention
channel:

1. **Diffusion:** neighbour differences update a scalar field.
2. **Curvature feedback:** a vertex radius responds to its angle-defect error.
3. **Reaction--diffusion:** two fields react at a vertex and diffuse through
   neighbours.
4. **Declared interventions:** metric pulses, scalar pulses, metric jitter, and
   cell/edge rewrites are labeled rather than counted as ordinary local steps.

Topological events are disclosed interventions rather than silent side effects.

## 3. Exact finite observables

### 3.1 Homology and Euler characteristic

Let \(\partial_1:C_1\to C_0\) and \(\partial_2:C_2\to C_1\) be boundary maps
over \(\mathbb F_2\).  The laboratory computes

\[
\beta_0=|V|-\operatorname{rank}\partial_1,
\]

\[
\beta_1=|E|-\operatorname{rank}\partial_1-
                 \operatorname{rank}\partial_2,
\]

\[
\beta_2=|F|-\operatorname{rank}\partial_2,
\]

and checks

\[
\chi=|V|-|E|+|F|=\beta_0-\beta_1+\beta_2.
\]

These are exact combinatorial results for the displayed finite complex.

### 3.2 Angle-defect curvature and Gauss--Bonnet

For a triangular face, its intrinsic edge lengths determine its three angles
by the cosine law.  For an interior vertex,

\[
K_i=2\pi-\sum_{f\ni i}\alpha_{fi};
\]

for a boundary vertex,

\[
K_i=\pi-\sum_{f\ni i}\alpha_{fi}.
\]

For a triangulated two-manifold with boundary this gives the finite identity

\[
\sum_i K_i=2\pi\chi(K).
\]

The exact badge is enabled only after a fail-closed validity gate checks unique
faces, positive triangle metrics, pure face incidence, edge-manifoldness, and
path/cycle vertex links.  The page then reports the floating residual of the
exact mathematical identity.  A small residual is a numerical consistency
check, not a new theorem.

## 4. Finite-scale dimension profile

The lab deliberately avoids reporting one unqualified dimension.

### 4.1 Volume-growth dimension

For intrinsic balls \(B_{d_\ell}(x,r)\) and the current counting measure, let

\[
V(r)=\frac1{|V|}\sum_x \mu(B_{d_\ell}(x,r)).
\]

Local slopes of \(\log V(r)\) against \(\log r\) produce the finite-scale
volume profile \(d_V(r)\).

### 4.2 Spectral dimension

For eigenvalues \(\lambda_j\) of the normalized Laplacian, define the finite
heat trace

\[
H(t)=\frac1{|V|}\sum_j e^{-t\lambda_j}.
\]

The finite-scale spectral profile is

\[
d_s(t)=-2\frac{d\log H(t)}{d\log t}.
\]

On every fixed finite graph it returns to zero at sufficiently small and large
times.  Only an intermediate plateau, supported by refinement or ensemble
evidence, may be interpreted as an effective dimension.

### 4.3 Walk dimension

When a random walk supplies a stable scaling window,

\[
\mathbb E[d(X_0,X_t)^2]\asymp t^{2/d_w}.
\]

The displayed \(d_w\) is a finite deterministic estimate from weighted
random-walk transitions and hop-distance displacement.  The volume, heat, and
walk clocks are displayed separately and normalized independently for the
shared visual scale.  The identity \(d_s=2d_V/d_w\) is not assumed; it is only
a comparison diagnostic.

## 5. Forward, inverse, and recognition experiments

### Forward

Starting from a declared complex and state, iterate a local law and measure the
global trajectory

\[
n\longmapsto(\chi,\beta_0,\beta_1,\beta_2,K,d_V,d_s,d_w,\lambda_2).
\]

The core questions are convergence, stability under local perturbation,
conserved quantities, and topology-changing events.

### Inverse

Given a target curvature field \(K_i^*\) satisfying

\[
\sum_iK_i^*=2\pi\chi,
\]

the radius variables use the local feedback

\[
u_i=\log r_i,
\qquad
u_i^{n+1}=u_i^n+\eta(K_i^*-K_i^n),
\]

and intrinsic edge lengths are refreshed as \(\ell_{ij}=r_i+r_j\).  There is no
global runtime gauge update.  The target field is compiled once, before the
run, to satisfy the necessary Gauss--Bonnet sum.  The target RMS curvature
error is the objective.  This is a circle-packing-style numerical flow; passing
the sum obstruction is not sufficient for realizability, and the browser does
not claim convergence for arbitrary targets.

### Recognition

Given a complete supplied weighted graph sampled from latent data, compute its
finite-complex topology, diffusion, spectral gap, and dimension profile.  This
is descriptor recognition, not reconstruction from bounded observations.  It
does not certify the existence or uniqueness of an underlying smooth manifold.

## 6. Universality experiment

The first release compares two runs sharing a preset, parameter values, step,
and measurement schedule but differing in seed and seeded microscopic disorder.
For each profile sampled at matched native scales, it reports

\[
\Delta_D=
\sqrt{\frac1M\sum_{j=1}^{M}
\left(D_{\theta_1}(s_j)-D_{\theta_2}(s_j)\right)^2},
\]

together with an RMS distance between the first sixteen normalized-Laplacian
eigenvalues and an exact topology comparison.  Identical seeds are explicitly
labeled as a replay check.  Two-seed agreement is finite observable robustness,
not isometry, an ensemble result, or proof of a continuum universality class.

## 7. Application presets and semantic boundaries

Every preset states which part of the common model is literal and which part is
an analogy.

| Preset | Local mechanism | Global observable | Boundary of interpretation |
|---|---|---|---|
| Programmable sheet | local circle-packing curvature feedback and diffusion | target-curvature error, Gauss--Bonnet, dimension profile | abstract intrinsic sheet, not a calibrated material |
| Morphogenesis | graph reaction--diffusion | scalar pattern, topology, transport scales | qualitative tissue analogy, not a biological fit or mechanics model |
| Resilient network | neighbour diffusion plus a disclosed shortcut intervention | components, graph cycles, spectral gap, transport profile | synthetic routing network |
| Manifold recognition | sampled local similarity graph | finite metric, spectral, and walk profiles | descriptors of the supplied graph, not a manifold-recovery certificate |
| Swarm consensus | neighbour averaging on a disconnected proximity graph | componentwise consensus obstruction, connectivity, spectral nullity | fixed-position information toy, not a robot controller |
| Relational-graph physics toy | local undirected adjacency and diffusion | scale-dependent spectral and volume profiles | no Lorentzian causality, quantum dynamics, or physical-spacetime evidence |

## 8. Evidence ladder

The interface uses four non-interchangeable labels:

- **Exact finite identity:** combinatorial homology, Euler characteristic, and
  the mathematical Gauss--Bonnet identity for a valid finite triangulation.
- **Finite numerical estimate:** eigenvalues, dimension slopes, flow errors,
  finite ensemble spread, and time integration.
- **Research target:** continuum convergence, universality, robustness, and
  identifiability statements that require refinement, uncertainty, or proof
  beyond a single finite run.
- **Application analogy:** a preset's interpretation as material, tissue,
  swarm, learned manifold, network, or spacetime.

No numerical run is promoted to a convergence theorem.  No application preset
is promoted to empirical adequacy.

## 9. Programmability and reproducibility

Every exported run records the core version and analysis-schema version.  The
public configuration schema has:

- a generator and bounded size parameters;
- a deterministic seed;
- a closed set of dynamics and measurement options;
- a target-curvature rule, when applicable; and
- application text and evidence classification supplied by trusted presets.

Configuration import uses allowlisted fields and bounded finite values, and the
page never evaluates configuration text as code.  Exports contain the normalized
configuration, finite state, measurements, optional paired-world comparison,
and method labels.  Equal configurations and seeds must produce equal initial
states and equal deterministic runs.

## 10. Verification gates

The implementation is not complete until all of these pass:

1. deterministic replay for every preset;
2. exact Betti/Euler identities on disk, sphere, graph, and punctured examples;
3. Gauss--Bonnet residual near floating roundoff on valid triangulations;
4. normalized Laplacian spectrum in \([0,2]\) with zero multiplicity
   \(\beta_0\);
5. curvature-flow target error reduction on a declared benchmark;
6. rejection of malformed, oversized, nonfinite, and unknown configurations;
7. finite outputs after every supported local update and intervention;
8. relabeling invariance for topology, curvature, spectrum, and dimensions;
9. a finite influence-cone check for each law labeled L0;
10. display-embedding changes leave intrinsic observables unchanged;
11. keyboard-operable controls and meaningful accessible SVG descriptions;
12. responsive layouts at desktop and narrow mobile widths; and
13. explicit preservation of the evidence ladder in UI copy and exports.

## 11. Research continuation

The executable lab opens rather than closes the programme.  The next theorem
targets are:

1. sufficient compactness and stability hypotheses for families of local
   rules to possess metric-measure scaling limits;
2. rigidity and non-realizability criteria for the inverse problem;
3. conditions under which volume, spectral, and walk dimensions agree;
4. quantitative stability of global topology and curvature under bounded
   local defects;
5. classification of local-rule universality classes; and
6. finite-observation lower bounds for the recognition problem.

The governing research question is:

\[
\boxed{\text{Which global worlds are locally generable, recognizable, and
robustly programmable?}}
\]

## 12. Mathematical anchors and novelty boundary

The programme synthesizes established local-to-global mechanisms rather than
claiming them as new theorems.  Its primary mathematical anchors include:

- Regge's construction of piecewise-flat curvature from local deficit angles
  ([Regge, 1961](https://cds.cern.ch/record/472394));
- convergence of polyhedral curvature measures under nondegenerate refinement
  ([Cheeger--Müller--Schrader, 1984](https://www.cs.jhu.edu/~misha/Fall09/Cheeger84.pdf));
- exact cochain calculus and local incidence operators in discrete exterior
  calculus
  ([Desbrun--Hirani--Leok--Marsden](https://arxiv.org/abs/math/0508341));
- local transport contraction as coarse Ricci curvature
  ([Ollivier](https://arxiv.org/abs/math/0701886));
- graph-Laplacian approximation of manifold Laplacians
  ([Belkin--Niyogi](https://papers.nips.cc/paper/2006/hash/5848ad959570f87753a60ce8be1567f3-Abstract.html));
  and
- combinatorial Ricci flow as local curvature-error relaxation
  ([Chow--Luo](https://sites.math.rutgers.edu/~fluo/mpapers/combinatorial%20Ricci%20flow%20in%20dimension%202.pdf)).

The contribution of this first release is the explicit research contract and
the executable composition of forward, inverse, recognition, obstruction,
dimension-profile, and application-boundary views in one reproducible finite
laboratory.  It makes no literature-priority claim and has not undergone peer
review.
