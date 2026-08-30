# Global Geometry II: formal foundations

## The Universality and Inverse-Design Atlas

- **Research status:** foundations contract, elementary theorem package, and
  implementation specification; not peer reviewed; no publication or
  literature-priority claim
- **Predecessor:** [Global Geometry Lab](GLOBAL_GEOMETRY_LAB.md)
- **Scope:** finite graphs and finite cell or simplicial complexes, their
  refinements, local dynamics, metric-measure limits, and inverse-design
  certificates
- **Central question:**

\[
\boxed{\text{Which global geometries are locally generable, recognizable,
and robustly programmable?}}
\]

This document supplies the mathematical contract for Global Geometry II.
P8.2 proves a precisely scoped Gaussian finite-dimensional diffusion limit for
the declared square/triangular iid walks, and P8.3 proves its uniform
covariance-whitened extension over a bounded centered nondegenerate iid basin.
Neither result proves bounded-disk U2, object-level or metric universality,
operator/semigroup convergence, path-space tightness, boundary or disorder
stability, or material/physical universality.  The finite browser laboratory
does not supply those missing claims.  Instead, this contract states what they
would mean, which propositions are established, and which experiments can
raise or falsify the remaining claims.

The extension has four non-interchangeable levels:

\[
\text{local rule}
\longrightarrow
\text{finite trajectory}
\longrightarrow
\text{refinement family}
\longrightarrow
\text{declared macroscopic limit}.
\]

Skipping a level is prohibited.  In particular, agreement between two finite
runs is not convergence, and agreement between selected observables is not
isometry.

## 1. Evidence grammar

Every theorem, claim, chart, compiler result, and application statement must
carry exactly one primary evidence label.

| Label | Meaning | Minimum support |
|---|---|---|
| **proved** | A mathematical statement established either here or by an applicable published theorem | complete proof, or a primary source plus a check of every invoked hypothesis |
| **computational** | A deterministic or statistical result for declared finite instances | executable artifact, configuration identity, numerical method, uncertainty, and falsification gate |
| **conjectural** | A precise research statement not yet proved | quantified claim, topology of convergence, hypotheses, and intended falsifier |
| **engineering** | A design approximation, emulator result, calibration, or hardware claim | tolerances, calibration procedure, failure envelope, and versioned artifact |
| **speculative** | An interpretation not licensed by the mathematical or empirical evidence | explicit non-claim and no use as an input to a theorem |

The label vocabulary is exactly the shared core vocabulary:
“proved,” “computational,” “conjectural,” “engineering,” and “speculative.”
A proved record additionally requires
“basis: proved-here” or “basis: proved-external.”  The basis is
metadata, not a sixth evidence label.  Every proposition proved in this
document has basis “proved-here.”  Every literature result invoked below is
identified as basis “proved-external.”

Definitions, schemas, and protocol requirements are not evidence claims.
Whenever they are instantiated, the resulting assertion must receive a label.
The word “exact” is reserved for symbolic or combinatorial identities on the
declared finite object.  Floating residuals are **computational**, even when
they audit an exact identity.

### 1.1 Claim record

Every exported scientific claim must have this logical record:

~~~typescript
interface ClaimRecord {
  schemaVersion: 2;
  id: string;
  claim: string;
  status:
    | "proved"
    | "computational"
    | "conjectural"
    | "engineering"
    | "speculative";
  basis:
    | "proved-here"
    | "proved-external"
    | "finite-computation"
    | "finite-ensemble"
    | "falsifiable-hypothesis"
    | "model"
    | "calibration"
    | "physical-measurement"
    | "interpretation";
  scope: string;
  method: string;
  falsifier: string;
  proofAnchor?: string;
  sourceUrls: string[];
  assumptions: string[];
  artifacts: string[];
  tests: string[];
  limitations: string[];
  dependencies: string[];
  result: unknown;
  digestAlgorithm: "fnv1a32-canonical-json";
  digest: string;
}
~~~

A test suite may support a **computational** claim and may verify that code
implements a **proved** formula.  Passing tests alone never promotes a
scientific statement to **proved**.

## 2. The declared discrete world

### 2.1 Carrier

A finite carrier is a typed incidence structure

\[
K=(C_0,C_1,\ldots,C_D,\prec),
\]

where \(C_q\) is the finite set of \(q\)-cells and \(\prec\) records incidence.
The release-one object \(K=(V,E,F)\) is the special case \(D\leq2\) with
vertices, undirected edges, and triangular faces.  A simplicial carrier must be
closed under taking faces.  A more general cell carrier must supply boundary
operators

\[
\partial_q:C_q(K;\mathbb F_2)\longrightarrow C_{q-1}(K;\mathbb F_2),
\qquad
\partial_{q-1}\partial_q=0.
\]

The incidence graph \(\mathcal I(K)\) has one typed node for every cell and an
edge for every codimension-one incidence.  Locality for mixed-dimensional
rules is measured in this graph.  Vertex-only rules may instead declare the
one-skeleton metric.  The choice is part of the rule, because the two radii are
not interchangeable.

### 2.2 State

At discrete time \(n\), a state is

\[
\mathfrak G_n=
(K_n,\ell_n,\mu_n,W_n,U_n,A_n,B_n,\Pi_n).
\]

Here:

- \(\ell_n:E_n\to(0,\infty)\) is the intrinsic edge length;
- \(\mu_n\) is a positive measure on declared cells, normally vertices or
  faces;
- \(W_n:E_n\to(0,\infty)\) is symmetric transport conductance;
- \(U_n\) contains scalar, vector, or categorical marks attached to cells;
- \(A_n\) contains actuator or control state;
- \(B_n\) records boundary type and imposed boundary data; and
- \(\Pi_n\) is a visualization or measured embedding, never an intrinsic
  datum unless the configuration explicitly compiles \(\ell_n\) from it.

For a connected one-skeleton, the graph-length metric is

\[
d_{\ell_n}(x,y)
=
\min_{\gamma:x\leadsto y}\sum_{e\in\gamma}\ell_n(e).
\]

For a valid triangulated surface, Global Geometry II may additionally use the
piecewise-Euclidean length metric \(d_{\mathrm{PE}}\), which permits paths
through face interiors.  These two metrics can have different scaling limits.
Every observable must name which one it uses.

The transport operator is not inferred from the metric.  One admissible
choice is the weighted normalized Laplacian

\[
L=I-D^{-1/2}WD^{-1/2},
\]

with the isolated-vertex convention declared separately.  Finite-element,
cotangent, combinatorial, and random-walk Laplacians are distinct operator
families and must have distinct identifiers.

### 2.3 Four meanings of “generable”

Let \(\mathcal R\) be a declared rule family and \(Y\) a target.

1. **Exact finite generability:** some finite carrier, seed, parameter, and
   time produce an output isomorphic to \(Y\).
2. **Approximate finite generability:** a declared target distance is at most
   a declared tolerance.
3. **Asymptotic generability:** a refinement program produces rescaled outputs
   converging to \(Y\) in a declared topology.
4. **Robust generability:** a specified perturbation class has the same
   macroscopic limit, or remains inside a specified target neighborhood with
   stated probability.

“Programmable” means that an inverse compiler returns a rule program together
with the strongest certificate supported by one of these four levels.
“Recognizable” means that an estimator is identifiable and stable under a
declared observation model; descriptor calculation alone is not recognition.

## 3. Finite-radius local rules

### 3.1 Rooted decorated neighborhoods

For a cell \(c\), let

\[
\mathcal N_R(c;\mathfrak G)
\]

denote the rooted, typed, decorated radius-\(R\) ball in the rule's declared
adjacency graph.  It contains only the state fields listed in the rule's
read-set.  Absolute cell identifiers and serialization order are excluded.
Boundary tags may be read if declared.  A geometric rule may read intrinsic
lengths and incidence; it may not silently read display coordinates.

A deterministic synchronous radius-\(R\) rule is a family of maps

\[
f_q:
\{\text{rooted decorated radius-\(R\) neighborhoods of \(q\)-cells}\}
\times\Theta\times\mathcal B
\longrightarrow S_q,
\]

where \(\Theta\) contains fixed parameters and \(\mathcal B\) contains
explicitly disclosed broadcasts.  Applying every \(f_q\) to the same old
state and then committing all writes gives

\[
\mathfrak G_{n+1}=F_R(\mathfrak G_n;\theta,b_n).
\]

The rule must be invariant under rooted decorated neighborhood isomorphism.
This is the mathematical form of relabeling equivariance.

The locality classes remain:

- **L0:** bounded neighborhood plus fixed constants;
- **L1:** L0 plus a disclosed broadcast, boundary value, target field, or
  global scalar; and
- **L2:** eigensolve, global optimization, equilibrium solve, centralized
  matching, or any operation that can depend on the whole state.

An L2 analyzer may measure an L0 trajectory.  Its output cannot be fed back
while continuing to call the runtime L0.

### 3.2 Structural rewrites

A cell rewrite is local only when its proposal is determined by a bounded
decorated patch and every conflict is resolved by an equivariant bounded-radius
rule.  “Choose the smallest vertex identifier” is not equivariant.  “Choose a
maximal independent set” is not automatically bounded-radius unless the
specific distributed schedule and random labels are declared.

The first Global Geometry release treats topology changes as interventions.
Global Geometry II retains that safe default.  A future topology-changing
runtime must declare:

\[
(R_{\rm proposal},R_{\rm conflict},T_{\rm commit})
\]

and supply a causal proof for the combined radius.

### Proposition 3.1 — finite causal cone

**Evidence status: proved; proof basis: proved-here.**  Let \(F_R\) be a deterministic synchronous L0
rule on a fixed adjacency structure.  If two initial states agree on
\(\mathcal N_{RT}(c)\), then the state at \(c\) agrees for the first \(T\)
updates.  A perturbation supported on \(S\) cannot affect a cell whose
combinatorial distance from \(S\) exceeds \(RT\).

**Proof.**  At one step the new state of a cell reads only its radius-\(R\)
neighborhood.  Inductively, the state in a radius-\(R(T-k)\) neighborhood
after \(k\) steps depends only on the original radius-\(RT\) neighborhood.
Set \(k=T\).  The support statement is the contrapositive. \(\square\)

The same proof applies to L1 rules only when the two runs receive the same
broadcast sequence.  It does not apply after an undeclared adjacency rewrite.
For a dynamically changing metric-ball neighborhood, the rule must also
provide a fixed underlying combinatorial-radius bound; otherwise \(RT\) is not
a valid cone in the original adjacency.

### Proposition 3.2 — global relabeling equivariance

**Evidence status: proved; proof basis: proved-here.**  If each local update depends only on the isomorphism
class of its rooted decorated neighborhood and synchronous conflict resolution
is equivariant, then for every carrier isomorphism \(\varphi\),

\[
F_R(\varphi_\ast\mathfrak G)=\varphi_\ast F_R(\mathfrak G).
\]

Consequently, every intrinsic isomorphism-invariant observable is unchanged by
relabeling.

**Proof.**  The map \(\varphi\) sends the rooted neighborhood at \(c\)
isomorphically to the rooted neighborhood at \(\varphi(c)\).  The two local
maps therefore return corresponding writes.  Synchronous equivariant commit
preserves the correspondence. \(\square\)

### Proposition 3.3 — topology cannot emerge from state-only updates

**Evidence status: proved; proof basis: proved-here.**  If \(K_n=K_0\) for every \(n\), then every
combinatorial invariant of the carrier, including homology and Euler
characteristic, is constant in time.

**Proof.**  The chain groups and boundary matrices are unchanged.  Hence their
ranks, kernels, images, homology groups, and alternating cell count are
unchanged. \(\square\)

Metric shape, diffusion, curvature, and effective dimension may still change
on a fixed carrier.  A topology change, however, requires a carrier rewrite or
a scale-dependent observation rule; it cannot be attributed to a scalar-field
update alone.

### Proposition 3.4 — local indistinguishability bound

**Evidence status: proved; proof basis: proved-here.**  Suppose two rooted decorated worlds have
isomorphic radius-\(RT\) neighborhoods and receive identical broadcasts.  No
deterministic equivariant radius-\(R\) observer running for at most \(T\)
rounds can distinguish their roots.

**Proof.**  Couple the two runs through the rooted neighborhood isomorphism.
Propositions 3.1 and 3.2 give identical root histories through time \(T\).
Any output determined by those histories is identical. \(\square\)

This is the first recognition obstruction.  Global topology, diameter, and
remote defects cannot in general be certified by a fixed-radius, fixed-time
observer.  Recognition needs a growing observation radius, multiple sampled
roots, a trusted global channel, or an explicit prior restricting possible
worlds.

## 4. Compatibility of local data

Compatibility is a hierarchy.  Passing one level never silently implies the
next.

1. **Syntactic compatibility:** finite values, valid endpoints, closure under
   faces, declared types.
2. **Local metric compatibility:** positive edge lengths and a realizable
   metric on every cell.
3. **Incidence compatibility:** manifold link or chosen singular-complex
   conditions.
4. **Global integral compatibility:** homology, Euler, total curvature,
   boundary, conservation, and source balance.
5. **Model-class compatibility:** circle-packing, material, actuator, or
   controller constraints.
6. **Limit compatibility:** compactness, mesh quality, consistent scaling, and
   a declared convergence topology.

### Proposition 4.1 — gluing compatible Euclidean triangles

**Evidence status: proved; proof basis: proved-here.**  Let \(K\) be a finite triangular complex and let
\(\ell:E\to(0,\infty)\).  If the three lengths of every face satisfy the
strict triangle inequalities, then each face has a Euclidean realization
unique up to rigid motion.  Gluing equal copies of each common edge produces a
piecewise-Euclidean length space unique up to a facewise isometry commuting
with the cell identifications.  If every interior vertex link is a cycle and
every boundary vertex link is a path, the result is a piecewise-Euclidean
surface with boundary.

**Proof.**  The side-side-side theorem gives existence and uniqueness of each
Euclidean triangle.  A shared abstract edge has one declared length, so its
two copies are identified by an edge isometry.  Taking the quotient of the
disjoint faces and its induced path metric gives the claimed length space.
The link criterion is precisely the local topological criterion for a
triangular two-manifold with boundary. \(\square\)

This determines intrinsic, not extrinsic, geometry.  Folding a valid sheet in
\(\mathbb R^3\) can change its embedding without changing this metric.

### Proposition 4.2 — circle-packing lengths are face-compatible

**Evidence status: proved; proof basis: proved-here.**  If every vertex radius is positive and

\[
\ell_{ij}=r_i+r_j,
\]

then every triangular face satisfies the strict triangle inequalities.

**Proof.**  For a face \(i,j,k\),

\[
\ell_{ij}+\ell_{jk}-\ell_{ki}=2r_j>0,
\]

and cyclic permutations give the other two inequalities. \(\square\)

This does not prove that a prescribed curvature vector is realized by some
positive radius vector.

### Proposition 4.3 — discrete Gauss–Bonnet with the lab boundary convention

**Evidence status: proved; proof basis: proved-here.**  Let \(K\) be a finite triangulation of a compact
two-manifold with boundary and nondegenerate Euclidean faces.  Define

\[
K_v=
\begin{cases}
2\pi-\sum_{f\ni v}\alpha_{fv},&v\text{ interior},\\[2mm]
\pi-\sum_{f\ni v}\alpha_{fv},&v\text{ on the boundary}.
\end{cases}
\]

Then

\[
\sum_vK_v=2\pi\chi(K).
\]

**Proof.**  Every triangular face contributes total angle \(\pi\), so the sum
of all incident angles is \(\pi F\).  Let \(V_i,V_b\) be the interior and
boundary vertex counts.  Thus

\[
\sum_vK_v=2\pi V_i+\pi V_b-\pi F.
\]

For a triangulated surface,
\(3F=2E_i+E_b\), and the boundary is a disjoint union of polygonal cycles, so
\(E_b=V_b\).  Substitution gives
\[
2\pi V_i+\pi V_b-\pi F
=2\pi(V-E+F)=2\pi\chi(K).
\]
\(\square\)

Hence a target \(K^\ast\) failing

\[
\sum_vK_v^\ast=2\pi\chi(K)
\]

is impossible in this target class.  Passing this equation is only a
necessary gate.  For the closed-surface circle-packing class, Global Geometry
II will use the stronger Chow–Luo curvature-polytope inequalities, with the
subset slack denoted \(\Delta_{\mathrm{CL}}(I)\) to distinguish it from the
Laplacian \(L\).  A disk receives that exact certificate only through a
declared symmetric-doubling construction.  The general release-one disk
compiler remains a numerical candidate generator.

### Proposition 4.4 — normalized-Laplacian nullity

**Evidence status: proved; proof basis: proved-here.**  For a finite undirected graph with positive edge
weights, the multiplicity of \(0\) in the symmetric normalized Laplacian,
using a zero block for isolated vertices, equals the number of connected
components.

**Proof.**  On nonisolated vertices,

\[
x^\top Lx
=
\sum_{\{i,j\}\in E}w_{ij}
\left(\frac{x_i}{\sqrt{d_i}}-\frac{x_j}{\sqrt{d_j}}\right)^2.
\]

The quadratic form vanishes exactly when \(x_i/\sqrt{d_i}\) is constant on
each nontrivial connected component.  Every isolated vertex contributes one
independent zero coordinate. \(\square\)

A target requesting one global consensus mode on a disconnected carrier
therefore has an exact spectral-topological obstruction.

### Proposition 4.5 — conservation by antisymmetric local flux

**Evidence status: proved; proof basis: proved-here.**  Let \(q_{ij}=q_{ji}\geq0\), and update

\[
u_i^{n+1}
=u_i^n+\frac{\Delta t}{\mu_i}
\sum_jq_{ij}(u_j^n-u_i^n).
\]

Then the weighted total \(\sum_i\mu_i u_i^n\) is conserved, independently of
the time-step size.

**Proof.**  Multiply by \(\mu_i\) and sum.  Every undirected edge contributes
\(q_{ij}(u_j-u_i)+q_{ji}(u_i-u_j)=0\). \(\square\)

Stability and positivity of the explicit update require additional step-size
conditions; conservation alone does not provide them.

## 5. Rigidity and ambiguity

Inverse design must state what is expected to be unique.

| Rigidity level | Meaning |
|---|---|
| **R0 finite state** | one labeled state is determined |
| **R1 gauge rigidity** | unique after quotienting scale, rigid motion, relabeling, or another declared gauge |
| **R2 intrinsic rigidity** | one metric-measure object up to isometry |
| **R3 macroscopic rigidity** | every admitted refinement subsequence has the same limit |
| **R4 dynamic selection** | a local flow converges to that limit from a declared basin |

R4 is strictly stronger than R3, and R3 is stronger than agreement of a
finite descriptor vector.

### Proposition 5.1 — identifiability of circle-packing radii from edge sums

**Evidence status: proved; proof basis: proved-here.**  Let \(G\) be a connected graph and assume the
equations

\[
r_i+r_j=\ell_{ij}\qquad(\{i,j\}\in E)
\]

have a real solution.

- If \(G\) contains an odd cycle, the solution is unique.
- If \(G\) is bipartite, the full solution set is an affine line
  \(r+t\sigma\), where \(\sigma=+1\) on one color class and \(-1\) on the
  other.  If one strictly positive solution exists, positivity restricts
  \(t\) to a nonempty open interval and therefore does not restore
  uniqueness.

**Proof.**  The difference \(x\) of two solutions obeys \(x_i+x_j=0\) on
every edge.  Along a path, signs alternate from one chosen root.  An odd cycle
forces the root value to be its own negative and hence zero, proving
uniqueness.  On a connected bipartite graph, the alternating sign vector
\(\sigma\) spans all homogeneous solutions. \(\square\)

Thus even perfect knowledge of every circle-packing edge length does not
identify vertex actuators on a bipartite carrier without a gauge or additional
measurement.

### Proposition 5.2 — stability of graph distances on a fixed carrier

**Evidence status: proved; proof basis: proved-here.**  Let \(G\) be a connected graph on \(N\) vertices
with two positive edge-length assignments \(\ell,\ell'\), and put

\[
\varepsilon=\max_{e\in E}|\ell_e-\ell'_e|.
\]

Then

\[
\max_{x,y\in V}|d_\ell(x,y)-d_{\ell'}(x,y)|
\leq (N-1)\varepsilon.
\]

**Proof.**  A positive-length shortest path can be chosen simple and hence
has at most \(N-1\) edges.  Evaluate an \(\ell\)-shortest path with the
\(\ell'\) lengths to obtain
\(d_{\ell'}\leq d_\ell+(N-1)\varepsilon\).  Exchange \(\ell\) and \(\ell'\).
\(\square\)

For a refinement family this bound is useful only if the rescaled quantity
\(a_h(N_h-1)\varepsilon_h\) tends to zero.  “Small per-edge error” alone is not
a uniform continuum stability statement.

### Proposition 5.3 — deterministic replay

**Evidence status: proved; proof basis: proved-here.**  A deterministic generator, canonical
serialization, deterministic synchronous rule, fixed parameter record, fixed
broadcast sequence, and fixed seed determine one finite trajectory.

**Proof.**  The initial state is a deterministic function of the record.
Induction through the deterministic update gives every later state. \(\square\)

Cross-platform floating-point equality is a separate engineering issue.
Intrinsic combinatorial outputs can be byte-identical; eigensolver and
optimization outputs should use schema-aware tolerances unless an
outward-rounded certificate is supplied.

## 6. Refinement and scaling

### 6.1 Refinement program

A refinement program is not a list of increasingly large screenshots.  It is
a tuple

\[
\mathscr P=
\bigl\{
(\mathfrak G_h,a_h,b_h,\tau_h,\iota_h,\mathbb P_h)
\bigr\}_{h\downarrow0},
\]

where:

- \(h\) is the declared resolution parameter;
- \(a_h>0\) rescales intrinsic distance;
- \(b_h>0\) normalizes measure;
- \(\tau_h>0\) rescales the generator or physical time;
- \(\iota_h\) is an optional coupling, interpolation, or coarse-graining map;
  and
- \(\mathbb P_h\) is the law of seeded disorder, if the family is random.

The rescaled marked object is

\[
\mathcal Z_h=
\left(
X_h,\,
a_hd_h,\,
b_h\mu_h,\,
\tau_hL_h,\,
M_h
\right),
\]

where \(M_h\) contains fields, boundary marks, and curvature measures that are
part of the claim.

The program must declare whether \(h\) means maximum cell diameter, mean edge
length, inverse vertex count, or another quantity.  It must also declare mesh
quality: minimum angle, aspect ratio, degree bounds, conductance ellipticity,
or the relevant substitute.

### 6.2 Four distinct refinement operations

1. **Combinatorial subdivision:** replace cells by more cells.
2. **Geometric refinement:** approximate the same metric space more finely.
3. **Statistical enlargement:** sample a larger random world.
4. **Renormalization:** coarse-grain and rescale a microscopic rule.

They answer different questions.

### Proposition 6.1 — metric-preserving subdivision does not create geometry

**Evidence status: proved; proof basis: proved-here.**  Subdivide each Euclidean face of a
piecewise-Euclidean complex by adding points and straight segments inside the
same face, with consistent subdivisions on shared edges.  If every new edge
inherits its Euclidean length, the geometric realization with its
piecewise-Euclidean length metric is isometric to the original realization.

**Proof.**  Each old face is partitioned into subsets carrying the restriction
of the same Euclidean metric.  The identity on every old face is length
preserving before and after subdivision, and the quotient identifications on
old shared edges are unchanged.  Hence every rectifiable path has the same
length in both realizations. \(\square\)

This is a crucial null control.  A refinement chart that merely subdivides an
already fixed surface should show exact metric agreement; any change exposes
an implementation or measurement artifact.

### 6.3 Declared convergence topologies

No convergence claim is valid without naming a topology.

#### Global metric-measure shape

For compact objects, the default is a marked
Gromov–Hausdorff–Prokhorov-type topology:

- Hausdorff comparison controls the supports after isometric embedding in a
  common space;
- Prokhorov comparison controls normalized measures; and
- marks are compared by a declared joint-measure, correspondence, or
  interpolation rule.

For unmarked compact probability spaces the base distance is

\[
d_{\mathrm{GHP}}(X,Y)
=
\inf_{Z,\varphi,\psi}
\max\left\{
d_H^Z(\varphi X,\psi Y),
d_P^Z(\varphi_\ast\mu_X,\psi_\ast\mu_Y)
\right\},
\]

where the infimum runs over common metric spaces \(Z\) and isometric
embeddings \(\varphi,\psi\).  The mark-comparison rule adds one declared term
to this maximum; it may not be changed between refinement levels.

This is appropriate for diameter, global shape, mass distribution, and
curvature-measure limits.  It is not implied by local neighborhood
convergence.

#### Local weak geometry

For bounded-degree random rooted graphs, local weak convergence means that for
every fixed radius \(R\), the law of the rooted decorated \(R\)-ball converges.
For a finite graph the canonical root is uniform unless another root law is
declared.  This is the Benjamini–Schramm framework
([Benjamini–Schramm, 2001](https://doi.org/10.1214/EJP.v6-96)).

Local weak convergence can forget diameter, global topology, and total volume.
It is therefore suited to local phases, not by itself to “global shape.”

#### Diffusion and spectrum

Operator convergence uses generalized Mosco convergence of the rescaled
Dirichlet forms on varying \(L^2\) spaces:

\[
\begin{aligned}
u_h\rightharpoonup u
&\Longrightarrow
\liminf_h\mathcal E_h(u_h)\geq\mathcal E(u),\\
\forall u\;\exists u_h\to u
&\Longrightarrow
\limsup_h\mathcal E_h(u_h)\leq\mathcal E(u).
\end{aligned}
\]

The strong/weak comparison maps belong to the refinement program.  Under the
full hypotheses of the generalized framework, Mosco convergence controls
resolvents and semigroups; see
[Kuwae–Shioya, 2003](https://doi.org/10.4310/CAG.2003.v11.n4.a1).
This has status **proved** and proof basis **proved-external**; it is not an
automatic consequence of a visually convergent mesh.

#### Topology from uncertain samples

Exact homology of a supplied complex has status **proved** and proof basis
**proved-here** by finite linear algebra.  When the complex itself comes from
a noisy scale filtration,
persistent homology is the appropriate profile.  Stability of persistence
diagrams under the hypotheses of
[Cohen-Steiner–Edelsbrunner–Harer,
2007](https://doi.org/10.1007/s00454-006-1276-5)
has status **proved** and proof basis **proved-external**; it does not
identify which filtration represents the unknown physical object.

### 6.4 Compactness gates

Before fitting a limit, a program must report:

- a uniform diameter bound or a pointed basepoint convention;
- uniform covering-number bounds at every fixed physical radius;
- tight normalized measures;
- nondegenerate cell-shape or an explicitly singular chart;
- uniform conductance/energy control for operator claims; and
- boundary conditions that remain stable under refinement.

Uniform total boundedness gives subsequential compactness in the compact
Gromov–Hausdorff setting; this standard compactness principle is
**proved**.  The atlas initially treats the numerical covering audit
as **computational** and the conclusion “the family has a unique limit” as
**conjectural** until a proof supplies both compactness and uniqueness.

The metric-measure viewpoint follows the framework developed, among other
places, by [Sturm,
2006](https://doi.org/10.1007/s11511-006-0002-8).  Random metric-measure laws
can be compared in Gromov-weak form as in
[Greven–Pfaffelhuber–Winter,
2009](https://doi.org/10.1007/s00440-008-0169-3).  These references motivate
the declared topology; they do not certify a particular experiment.

## 7. Observable profiles

The atlas treats dimension, curvature, and transport as profiles over their
native clocks.

Normalize \(\mu_h(X_h)=1\) for the formulas below.  If physical mass must not
be normalized, record both measures.

### 7.1 Metric volume profile

\[
\bar d_h=a_hd_h,
\qquad
V_h(r)
=
\int_{X_h}\mu_h(B_{\bar d_h}(x,r))\,d\mu_h(x).
\]

For a multiplicative window factor \(q>1\), define the centered slope

\[
d_{V,h}(r;q)
=
\frac{\log V_h(qr)-\log V_h(r/q)}{2\log q}.
\]

The result is a finite-scale slope.  Boundary saturation and the one-point
regime are automatically masked.

### 7.2 Spectral profile

For a finite operator with eigenvalues \(\lambda_{j,h}\), define

\[
H_h(t)=\frac{1}{N_h}\sum_{j=1}^{N_h}
e^{-t\tau_h\lambda_{j,h}},
\qquad
d_{s,h}(t;q)
=
-2\frac{\log H_h(qt)-\log H_h(t/q)}{2\log q}.
\]

The normalizing factor and the physical time scale \(\tau_h\) are part of the
claim.  Every fixed finite connected graph has \(d_s\to0\) in the extreme
large-time regime, so only a refinement-supported intermediate window can
suggest a nonzero macroscopic spectral dimension.

### 7.3 Walk profile

Let \(X_0\) follow the declared root measure and \(X_m\) follow the declared
Markov chain.  With physical metric \(\bar d_h=a_hd_h\),

\[
M_h(m)=
\mathbb E\bigl[\bar d_h(X_0,X_m)^2\bigr],
\]

and, where the denominator is positive,

\[
d_{w,h}(m;q)
=
\frac{4\log q}
{\log M_h(qm)-\log M_h(m/q)}.
\]

This convention returns \(d_w=2\) when mean-square displacement is linear in
time.  Integer-time interpolation must be declared.

### 7.4 Curvature and topology profiles

For a valid triangulated surface, compare the curvature measure

\[
\kappa_h=\sum_{v\in V_h}K_{v,h}\,\delta_v,
\]

not only the list of point defects.  Weak convergence of \(\kappa_h\) is the
natural continuum claim.  Regge's local deficit construction is classical
([Regge, 1961](https://doi.org/10.1007/BF02733251)).  Convergence of
polyhedral curvature measures under appropriate nondegenerate approximation
hypotheses has status **proved** and proof basis **proved-external** in
[Cheeger–Müller–Schrader,
1984](https://doi.org/10.1007/BF01210729).  Arbitrary refined meshes do not
inherit that conclusion.

For a filtered complex \(K_h(r)\), record

\[
r\longmapsto
\bigl(\beta_{0,h}(r),\beta_{1,h}(r),\ldots\bigr)
\]

or its persistence diagram.  Betti numbers at one arbitrarily chosen sampling
radius are not a robust topology reconstruction claim.

### 7.5 Combined profile and scale registry

The core atlas profile is

\[
\Phi_h=
\left(
d_V(r),d_s(t),d_w(m),
\kappa_h,\beta_k(r),
\lambda_2(t),
\text{transport},
\text{stability}
\right).
\]

The arguments \(r,t,m\) remain distinct.  A scale registry may relate them
only through declared conversions:

~~~typescript
interface ScaleRegistry {
  metricScale: { native: number; physical: number; unit: string };
  heatTime: { native: number; physical: number; unit: string };
  walkTime: { steps: number; physical: number; interpolation: string };
  curvatureScale?: { dualAreaRule: string; smoothingRadius?: number };
  topologyScale?: { filtrationId: string; parameter: number };
}
~~~

The relation \(d_s=2d_V/d_w\) is a diagnostic unless heat-kernel scaling
hypotheses have been proved.  Divergence of the three clocks is data, not a
software error.

### 7.6 Reliability record

Every profile point must include:

- native and physical scale;
- estimator and window factor;
- number of centers, paths, eigenpairs, or ensemble members;
- finite-size and boundary masks;
- numerical residual or sampling interval;
- refinement level and seed;
- evidence label; and
- reasons for unavailability.

A plateau detector is an **engineering** classifier until a theorem connects
its tolerances to a limiting exponent.

## 8. Macroscopic equivalence and universality

### 8.1 A hierarchy of equivalence

Two runs can be equivalent in increasingly strong senses:

1. **Replay equivalence:** identical normalized configuration and seed.
2. **Finite isomorphism:** a state-preserving carrier isomorphism exists.
3. **Finite intrinsic isometry:** the metric-measure marked objects agree up
   to isometry.
4. **Profile equivalence:** selected observables agree on a declared scale
   window and tolerance.
5. **Finite-dimensional law equivalence:** every declared finite collection
   of process observations converges to the same joint law.  This is also
   called cylinder-law equivalence.
6. **Limit-object equivalence:** both refinement families converge to the same
   deterministic marked object.
7. **Path-space or object-law universality:** both random refinement families
   converge in law in one declared topology to the same random marked object.

**Robustness is a modifier, not a stronger topology:** any limit level receives
the label *robust* only when that same result persists uniformly over a
predeclared basin of microscopic perturbations.  Thus a robust level-5 result
does not silently become a path-space result.

An atlas badge must display the highest established level and every weaker
level it actually implies.  Profile equivalence does not imply finite
isometry, and local weak equivalence does not imply global
metric-measure equivalence.

Level 5 is intentionally separate.  Convergence of all fixed finite-time
vectors does not by itself give tightness in a path topology, hence does not
establish level 7.  Proposition 8.2 reaches level 5 for two iid walk laws;
Proposition 8.3 adds a uniform robustness basin at that same level.

### 8.2 Object-level definition

Let \(\mathscr P^A\) and \(\mathscr P^B\) be refinement programs whose rescaled
outputs are random elements of the same declared state space
\((\mathcal S,\mathcal T)\).  They are **universal in topology
\(\mathcal T\)** when there is one probability law \(\mathbb Q_\infty\) such
that

\[
\mathcal Z_h^A\Rightarrow\mathbb Q_\infty,
\qquad
\mathcal Z_h^B\Rightarrow\mathbb Q_\infty.
\]

For deterministic programs the law is a point mass.  The topology must say
which structures survive: metric-measure shape, rooted neighborhoods,
Dirichlet form, marks, topology, or some combination.

This definition makes universality an equivalence of limits, not a small
finite RMS score.

### 8.3 Profile-level definition

For scale window \(W\), observable components \(k\), weights \(w_k\), and
declared standardizations \(\sigma_k(s)>0\), define

\[
d_{\Phi,W}(A,B)^2
=
\sum_k w_k
\int_W
\frac{|\Phi_k^A(s)-\Phi_k^B(s)|^2}
{\sigma_k(s)^2}\,d\nu_k(s).
\]

Finite \(d_{\Phi,W}\) below a registered tolerance is a
**computational profile-equivalence** result.  The standardization cannot be
chosen after observing the comparison.  The comparison must report components
separately so cancellation inside the aggregate cannot hide a failed
observable.

A **conjectural profile universality** claim is

\[
d_{\Phi,W_h}(A_h,B_h)\longrightarrow0
\]

on matched physical windows, with nontrivial window overlap surviving
refinement.  This remains weaker than object-level universality.

### 8.4 Required universality evidence

A credible universality package requires:

1. within-family refinement convergence for \(A\);
2. within-family refinement convergence for \(B\);
3. a common scaling and comparison topology;
4. cross-family agreement after parameters are calibrated independently of
   held-out levels;
5. perturbation-basin tests;
6. a negative control known to have a different limit;
7. uncertainty and finite-size analysis; and
8. an explicit statement of which structures are not compared.

No finite number of levels proves a limit.  A convergent fit is
**computational** evidence for a **conjectural** limit unless accompanied by a
proof.

### 8.5 First benchmark: square versus triangular diffusion

Periodic square- and triangular-lattice diffusion is an excellent first
falsifiable benchmark only after the claim is narrowed correctly.

- For the two declared iid step laws, Proposition 8.2 proves convergence of
  every finite collection of rescaled walk positions to the same planar
  Gaussian process.  This is a finite-dimensional diffusion universality
  theorem.  Convergence of the lab's finite heat profiles toward
  \(d_s=d_w=2\), path-space tightness, semigroup convergence, boundary
  effects, and disordered conductances retain their separate computational or
  conjectural status.
- With the current one-skeleton shortest-path metric and uniform edge
  lengths, the square and triangular families do **not** automatically
  approach the same metric object.  Their finite direction sets lead to
  different anisotropic norm balls (diamond versus hexagonal).  Matching
  spectral dimensions would therefore establish profile universality, not
  full Global Geometry universality.
- A clean full-object benchmark should instead give two microscopic
  triangulation families the same facewise piecewise-Euclidean flat torus
  metric and use consistently scaled finite-element or cotangent Dirichlet
  forms.  Alternatively, retain the graph metrics and explicitly test the
  predicted nonuniversality as the negative control.

This distinction is scientifically valuable: two local rules may share a
diffusion fixed point while retaining different macroscopic metric geometry.

### Proposition 8.1 — the standard graph metrics retain different norm balls

**Evidence status: proved; proof basis: proved-here.**  Let the square graph have vertices
\(h\mathbb Z^2\) and generators
\(\{\pm e_1,\pm e_2\}\).  Let the triangular graph have coordinate generators
\(\{\pm e_1,\pm e_2,\pm(e_2-e_1)\}\), embedded using two unit vectors meeting
at angle \(\pi/3\).  Give every edge length \(h\).  As \(h\downarrow0\), their
pointed graph-length spaces converge on bounded sets to normed planes whose
unit balls are respectively a quadrilateral and a hexagon.  The two limits
are not isometric normed spaces.

**Proof.**  On the square graph the exact word distance from \(0\) to
\((m,n)\) is \(|m|+|n|\).  On the triangular coordinate graph it is

\[
\max\{|m|,|n|,|m+n|\}.
\]

The lower bound follows because each allowed generator changes all three
quantities by at most one.  If \(m,n\) have the same sign, the coordinate
generators give a path of length \(|m+n|\).  If they have opposite signs,
use \(\min\{|m|,|n|\}\) diagonal generators and finish along the remaining
coordinate; the length is \(\max\{|m|,|n|\}\).  These are exactly the two
cases of the displayed maximum.
After multiplication by \(h\), these formulas are the restrictions of two
polyhedral norms.  Rounding continuum coordinates to the nearest lattice
point changes either distance by \(O(h)\), proving bounded-set pointed
convergence.  Their unit balls have four and six extreme points.  The
Mazur–Ulam theorem states that a surjective isometry of real normed spaces is
affine; after translating the origin it is linear, and a linear isometry
preserves extreme points.  Hence the two normed planes are not isometric.
\(\square\)

Thus P8.1 is an exact negative control for full graph-metric universality.  It
does not obstruct a common diffusion limit after covariance calibration.

### Proposition 8.2 — square and equilateral-triangular walks share a Gaussian finite-dimensional limit

**Evidence status: proved; proof basis: proved-here.**  Embed the square step
set as

\[
S_\square=\{\pm(1,0),\pm(0,1)\}
\]

and the triangular step set as

\[
S_\triangle=\{\pm u,\pm v,\pm(u-v)\},\qquad
u=(1,0),\quad v=(1/2,\sqrt3/2).
\]

Let each infinite-plane walk choose uniformly from its step set,
independently at every time.  If

\[
Z_n^A(t)=n^{-1/2}X^A_{\lfloor nt\rfloor},
\qquad A\in\{\square,\triangle\},
\]

then the finite-dimensional distributions of both \(Z_n^A\) converge to the
same centered Gaussian process with independent
increments and covariance

\[
\mathbb E[B_sB_t^{\mathsf T}]=\tfrac12\min(s,t)I_2.
\]

Equivalently, at spatial edge scale \(h\), the physical-time process

\[
Y_h(t)=hX_{\lfloor 2t/h^2\rfloor}
\]

has the standard planar Brownian finite-dimensional limit.

**Proof.**  Symmetry gives zero mean.  For the square walk,

\[
\frac14\sum_{z\in S_\square}zz^{\mathsf T}=\tfrac12I_2.
\]

For the triangular walk, pairing opposite steps gives

\[
\frac13\bigl(uu^{\mathsf T}+vv^{\mathsf T}
 +(u-v)(u-v)^{\mathsf T}\bigr)=\tfrac12I_2.
\]

Because both step laws are finite and symmetric, their characteristic
functions have a common quadratic term and family-dependent fourth-order
remainders:

\[
\varphi_A(\xi)=1-\tfrac14\lVert\xi\rVert^2+O(\lVert\xi\rVert^4)
\quad(\xi\to0).
\]

Consequently, for each fixed \(t\ge0\),

\[
\varphi_A(\xi/\sqrt n)^{\lfloor nt\rfloor}
\longrightarrow \exp(-t\lVert\xi\rVert^2/4),
\]

the characteristic function of a centered Gaussian with covariance
\(tI_2/2\).  For \(0=t_0<t_1<\cdots<t_m\), the Cramér--Wold transform of any
linear combination of the positions can be rewritten using coefficients
\(c_r\) on disjoint increment blocks.  Independence gives

\[
\prod_{r=1}^{m}
\varphi_A(c_r/\sqrt n)^{\lfloor nt_r\rfloor-\lfloor nt_{r-1}\rfloor}
\longrightarrow
\exp\!\left[-\frac14\sum_{r=1}^{m}
(t_r-t_{r-1})\lVert c_r\rVert^2\right].
\]

Cramér--Wold therefore gives the claimed joint Gaussian laws and their
independent-increment covariance.  \(\square\)

P8.2 is a genuine local-rule universality result, but only for the declared
finite-dimensional diffusion laws.  It does **not** identify the graph
metrics (P8.1 proves that they differ), prove path-space tightness, compare
filled-disk boundaries, or cover disordered conductances.  Those stronger
claims retain their separate proof and computational gates.

### Proposition 8.3 — a robust covariance-whitened finite-dimensional basin

**Evidence status: proved; proof basis: proved-here.**  Fix the dimension
\(d\), \(M<\infty\), and \(0<\kappa\le1\).  Let
\(\mathcal P_{M,\kappa}\) be any family
of probability laws on \(\mathbb R^d\) such that, for
\(X\sim P\in\mathcal P_{M,\kappa}\),

\[
\mathbb E_PX=0,
\qquad \lVert X\rVert\le M\ \text{almost surely},
\qquad
\kappa I\preceq\Sigma_P:=\mathbb E_P[XX^{\mathsf T}]
\preceq\kappa^{-1}I.
\]

For iid increments with law \(P\), write
\(S_m^P=X_1+\cdots+X_m\) and

\[
W_n^P(t)=n^{-1/2}\Sigma_P^{-1/2}S^P_{\lfloor nt\rfloor},
\]

where \(\Sigma_P^{-1/2}\) is the symmetric positive-definite inverse square
root.  For every fixed schedule \(0=t_0<t_1<\cdots<t_m\) and every fixed
Cramér--Wold coefficient vector, the joint characteristic functions of
\(W_n^P\) converge
to those of standard \(d\)-dimensional Brownian motion **uniformly in**
\(P\in\mathcal P_{M,\kappa}\).  Hence this is a robust level-5
finite-dimensional universality class after the declared covariance
calibration.

**Proof.**  Put \(Y_P=\Sigma_P^{-1/2}X\).  Then
\(\mathbb E Y_P=0\), \(\mathbb E[Y_PY_P^{\mathsf T}]=I\), and the spectral
lower bound gives \(\lVert Y_P\rVert\le M/\sqrt\kappa\).  Taylor's theorem
for \(e^{iu}\) yields, uniformly over the family and for every fixed
\(c\in\mathbb R^d\),

\[
\mathbb E_P e^{i\langle c,Y_P\rangle/\sqrt n}
=1-\frac{\lVert c\rVert^2}{2n}+R_{P,n}(c),
\qquad
|R_{P,n}(c)|
\le \frac{M^3\lVert c\rVert^3}{6\kappa^{3/2}n^{3/2}}.
\]

The linear term vanishes and the quadratic term is common because the
whitened covariance is exactly \(I\).  The uniform remainder and
\(\log(1+z)=z+O(z^2)\) show that a block of \(\lfloor nt\rfloor\) increments
has characteristic function converging uniformly to
\(\exp(-t\lVert c\rVert^2/2)\).  For finitely many observation times,
rewrite a Cramér--Wold linear combination as finitely many independent
increment blocks.  Multiplying their uniformly convergent characteristic
functions proves the joint statement.  Equivalently, every sequence
\(P_n\in\mathcal P_{M,\kappa}\) has the same characteristic-function limit;
the multivariate Lévy continuity theorem and Cramér--Wold convert this
sequential uniform statement into uniform finite-dimensional weak
convergence.  \(\square\)

The committed audit instantiates four deliberately different members of the
shared basin \(M=\sqrt2\), \(\kappa=0.3\): the uniform square law, an
anisotropic square law, a pair-biased
triangular law, and a nonsymmetric centered three-step law.  It checks their
whitened moment residuals and three-direction characteristic errors at
\(n=200,2000,20000\).  The finite audit is **computational** support and a
regression oracle, not the proof.  An unwhitened anisotropic law is retained as
a negative control: covariance calibration is essential.

P8.3 assumes exact law-specific covariance whitening; estimated covariance is
outside its current statement.  It does not prove tightness in a path topology, a semigroup limit, a
boundary invariance principle, or a result for correlated, state-dependent,
unbounded, or degenerating increments.

## 9. Obstruction certificates

An obstruction certificate is not a solver failure message.  It is a
machine-verifiable witness that a necessary condition fails inside a declared
target and rule class.

### 9.1 Logical statuses

| Status | Meaning |
|---|---|
| **CERTIFIED_FEASIBLE_FINITE** | an explicit finite witness passes all exact gates and the declared target predicate |
| **CERTIFIED_INFEASIBLE** | a verified necessary condition fails in the declared class |
| **CANDIDATE** | an optimizer returned a witness within numerical tolerance, without a sufficiency or convergence theorem |
| **UNRESOLVED** | search failed, compactness is unproved, or numerical enclosures overlap zero |
| **OUT_OF_SCOPE** | the target or rule is outside the implemented theorem class |

“No candidate found” is **UNRESOLVED**, never **CERTIFIED_INFEASIBLE**.
Passing necessary conditions is not a feasibility certificate.

### 9.2 Certificate classes

| Code | Witness | Consequence |
|---|---|---|
| **OB-CELL-METRIC** | nonpositive edge or a face violating a triangle inequality | no piecewise-Euclidean realization with those cell lengths |
| **OB-LINK** | edge incidence above two or a vertex link not one path/cycle | not a triangular two-manifold in the declared class |
| **OB-GB** | exact or interval-separated residual in \(\sum K^\ast-2\pi\chi\) | curvature target impossible under the declared defect convention |
| **OB-CL-SUBSET** | a subset \(I\) with nonpositive \(\Delta_{\mathrm{CL}}(I)\) | closed-surface circle-packing target outside the Chow–Luo curvature polytope |
| **OB-RADIUS-GAUGE** | bipartite carrier and no extra gauge measurement | actuator radii not identifiable from edge sums alone |
| **OB-SPECTRAL-COMPONENT** | requested nullity differs from \(\beta_0\) | impossible normalized-Laplacian target on that carrier |
| **OB-CONSERVATION** | requested total change with no source/boundary flux | impossible under the declared conservative local update |
| **OB-FIXED-TOPOLOGY** | requested Betti change with a state-only runtime | impossible without a carrier rewrite or observation-scale change |
| **OB-LOCAL-VIEW** | paired worlds agree through radius \(RT\) but target labels differ | no radius-\(R\), \(T\)-round recognizer can solve the declared pair |
| **OB-LIMIT-GATE** | scaling mismatch, degenerating cells, or absent tightness evidence | continuum claim withheld; this is unresolved, not target impossibility |

The closed-surface Chow–Luo entry has status **proved** and proof basis
**proved-external** only within the exact circle-packing hypotheses of
[Chow–Luo, 2003](https://doi.org/10.4310/jdg/1080835659).
The atlas must not attach that certificate to an arbitrary curvature flow.
Stronger discrete conformal existence and uniqueness results also exist in
specific polyhedral categories; see
[Gu–Luo–Sun–Wu,
2018](https://doi.org/10.4310/jdg/1527040872).  Their hypotheses and surgery
operations must be implemented before their conclusions are used.

### 9.3 Certificate payload

~~~typescript
interface ObstructionCertificate {
  certificateId: string;
  code: string;
  status:
    | "CERTIFIED_FEASIBLE_FINITE"
    | "CERTIFIED_INFEASIBLE"
    | "CANDIDATE"
    | "UNRESOLVED"
    | "OUT_OF_SCOPE";
  evidenceStatus: ClaimRecord["status"];
  targetClassId: string;
  ruleClassId: string;
  hypothesesChecked: Array<{
    id: string;
    passed: boolean;
    method: "exact" | "interval" | "floating" | "not_checked";
    witness?: unknown;
    residual?: number;
    enclosure?: [number, number];
  }>;
  violatedCondition?: string;
  verifierId: string;
  verifierVersion: string;
  humanExplanation: string;
  nonClaims: string[];
}
~~~

A floating residual can certify a sign only when a justified error enclosure
excludes zero.  Otherwise its evidence is **computational** and its logical
status is **CANDIDATE** or **UNRESOLVED**.

## 10. Implementation-facing contracts

The new interfaces extend the release-one closed vocabulary.  Configurations
remain data; they never contain evaluated user code.

### 10.1 Rule family

~~~typescript
interface LocalRuleFamilySpec {
  schemaVersion: 2;
  ruleFamilyId: string;
  carrierClassId: string;
  stateSchemaId: string;
  locality: {
    class: "L0" | "L1" | "L2";
    adjacency: "one_skeleton" | "incidence_graph" | "metric_ball";
    radius: number;
    synchronous: boolean;
    readFields: string[];
    writeFields: string[];
    broadcasts: Array<{
      id: string;
      source: "fixed" | "boundary" | "precompiled_target" | "global_runtime";
      producerClass: "L0" | "L1" | "L2";
      refresh: "never" | "per_step";
      evidenceBoundary: string;
    }>;
  };
  updateKernelId: string;
  parameterSchemaId: string;
  structuralRewrite?: {
    enabled: boolean;
    proposalRadius: number;
    conflictRadius: number;
    commitRounds: number;
    kernelId: string;
  };
  equivarianceTests: string[];
  conservationLaws: string[];
  allowedTargetClasses: string[];
}
~~~

Validation rejects a per-step L2 producer on a rule labeled L0 or L1.  L0
rejects every changing global broadcast.  A target compiled globally before
time zero may have an L2 producer and refresh “never”; it is L1 runtime data,
not evidence that the compiler itself is local.

### 10.2 Refinement program

~~~typescript
interface RefinementProgramSpec {
  schemaVersion: 2;
  programId: string;
  ruleFamilyId: string;
  levels: Array<{
    levelId: string;
    resolution: number;
    resolutionMeaning: string;
    generatorConfig: unknown;
    distanceScale: number;
    measureScale: number;
    timeScale: number;
    seeds: string[];
  }>;
  metricModel: "graph_length" | "piecewise_euclidean" | "effective_resistance";
  measureModel: string;
  operatorModel: string;
  boundaryModel: string;
  coupling: {
    type: "nested" | "shared_randomness" | "independent" | "explicit_map";
    mapId?: string;
  };
  meshQualityGates: Array<{
    observableId: string;
    relation: "<=" | ">=";
    threshold: number;
  }>;
  convergenceTopologies: Array<
    | "marked_GHP"
    | "local_weak"
    | "generalized_Mosco"
    | "curvature_measure_weak"
    | "persistence_bottleneck"
    | "profile_only"
  >;
  physicalWindows: ObservationWindowSpec[];
  perturbationFamilies: string[];
  negativeControlProgramIds: string[];
}
~~~

### 10.3 Observables

~~~typescript
interface ObservationWindowSpec {
  windowId: string;
  clock: "metric_radius" | "heat_time" | "walk_time" | "filtration";
  physicalMin: number;
  physicalMax: number;
  sampling: "log" | "linear" | "explicit";
  values?: number[];
  precommitted: boolean;
}

interface ObservableSpec {
  observableId: string;
  family:
    | "topology"
    | "curvature"
    | "metric"
    | "volume_dimension"
    | "spectral_dimension"
    | "walk_dimension"
    | "transport"
    | "stability";
  metricModel?: string;
  measureModel?: string;
  operatorModel?: string;
  estimatorId: string;
  windowId?: string;
  exactGateId?: string;
  uncertaintyMethodId?: string;
  availabilityGateIds: string[];
}

interface ObservableResult {
  observableId: string;
  levelId: string;
  seed: string;
  nativeScale?: number;
  physicalScale?: number;
  value: number | number[] | null;
  evidenceStatus: "proved" | "computational" | "engineering";
  proofBasis?: "proved-here";
  uncertainty?: { lower: number; upper: number; method: string };
  residual?: number;
  available: boolean;
  withheldReasons: string[];
  methodVersion: string;
}
~~~

### 10.4 Universality comparison

~~~typescript
interface UniversalityComparisonSpec {
  comparisonId: string;
  leftProgramId: string;
  rightProgramId: string;
  claimLevel:
    | "profile_equivalence"
    | "local_weak_limit"
    | "metric_measure_limit"
    | "operator_limit"
    | "joint_marked_limit";
  topology: string;
  matchedScalingFields: string[];
  observableIds: string[];
  physicalWindowIds: string[];
  weights: Record<string, number>;
  standardizationId: string;
  fitLevels: string[];
  heldOutLevels: string[];
  equivalenceMargins: Record<string, number>;
  perturbationFamilyIds: string[];
  negativeControlProgramIds: string[];
}
~~~

The engine reports componentwise equivalence tests before any aggregate
distance.  Calibration on held-out levels is forbidden.  A comparison cannot
request “joint marked limit” unless both programs declare compatible metric,
measure, operator, mark, and topology mappings.

### 10.5 Compiler target

~~~typescript
interface GeometryTargetSpec {
  targetId: string;
  targetClass:
    | "finite_metric"
    | "piecewise_euclidean_surface"
    | "circle_packing_curvature"
    | "topology"
    | "dimension_profile"
    | "transport_profile"
    | "joint";
  carrierPolicy: "fixed" | "refinable" | "compiler_selected";
  metricTarget?: unknown;
  curvatureTarget?: unknown;
  topologyTarget?: unknown;
  profileTargets?: unknown;
  tolerances: Record<string, number>;
  allowedRuleFamilyIds: string[];
  allowedLocalityClasses: Array<"L0" | "L1" | "L2">;
  materialOrActuatorConstraints?: unknown;
  requiredCertificateLevel:
    | "finite_candidate"
    | "finite_exact"
    | "asymptotic"
    | "robust";
}
~~~

Compiler output contains:

1. normalized target;
2. all applicable compatibility gates;
3. zero or more obstruction certificates;
4. candidate local-rule programs;
5. forward verification on held-out refinements;
6. sensitivity and actuator-gauge analysis;
7. convergence status; and
8. explicit non-claims.

### 10.6 Pure-core function boundary

The computational workstream can implement these pure functions without
changing the browser shell:

~~~typescript
validateRuleFamily(spec) -> ValidationReport
validateRefinementProgram(spec) -> ValidationReport
generateRefinementLevel(program, levelId, seed) -> FiniteState
verifyLocality(rule, pairedStates, rounds) -> CausalConeReport
measureObservables(state, observableSpecs) -> ObservableResult[]
compareRefinementLevels(program, results) -> ConvergenceAudit
compareUniversality(spec, leftResults, rightResults) -> ComparisonReport
verifyCompatibility(target, carrier, ruleClass) -> ObstructionCertificate[]
compileGeometry(target) -> CompilerReport
verifyCompilerCandidate(candidate, heldOutLevels) -> CompilerVerification
~~~

All return values are finite JSON.  Dense eigensolver size limits, unavailable
profiles, invalid surface gates, and failed numerical convergence must fail
closed.

## 11. Elementary theorem suite

The following finite theorem package is available before any new simulation.

| ID | Statement | Evidence | Main hypotheses | Implementation test |
|---|---|---|---|---|
| **P3.1** | finite causal cone | proved | synchronous radius-\(R\), fixed adjacency, matched broadcasts | paired perturbations inside/outside \(RT\) |
| **P3.2** | relabeling equivariance | proved | neighborhood-isomorphism kernels and equivariant commit | random permutations preserve intrinsic outputs |
| **P3.3** | fixed carrier preserves topology | proved | no cell rewrite | boundary matrices remain identical |
| **P3.4** | bounded observers cannot distinguish equal local views | proved | deterministic equivariant observer | adversarial paired worlds |
| **P4.1** | compatible triangles glue to a PE space | proved | positive lengths and strict face inequalities | metric gate and link gate |
| **P4.2** | positive circle radii satisfy face inequalities | proved | \(r_i>0\) | generated-face property test |
| **P4.3** | finite Gauss–Bonnet | proved | valid triangular surface and stated boundary defects | exact topology plus floating residual |
| **P4.4** | Laplacian nullity equals component count | proved | undirected positive weights | spectral multiplicity audit |
| **P4.5** | symmetric flux conserves weighted mass | proved | symmetric conductance | exact or tolerance mass audit |
| **P5.1** | radius inverse is unique iff connected graph is nonbipartite | proved | a solution exists | odd-cycle/bipartite fixtures |
| **P5.2** | fixed-graph distance stability | proved | positive lengths, fixed connected graph | adversarial edge perturbation |
| **P5.3** | deterministic replay | proved | fully deterministic closed record | cross-run equality |
| **P6.1** | PE subdivision is metric-null | proved | straight inherited subdivision | exact point/path controls |
| **P8.1** | standard square/triangular graph metrics have different normed limits | proved | declared generators and uniform edge lengths | norm-ball and distance-formula fixtures |
| **P8.2** | square/triangular iid walks share Gaussian finite-dimensional limits | proved | declared Euclidean steps, uniform iid increments, diffusive scaling | symbolic moments and characteristic-function fixtures |
| **P8.3** | bounded centered nondegenerate iid laws share uniform whitened Gaussian finite-dimensional limits | proved | bounded support, covariance basin, whitening, fixed finite observations | four-law perturbation and anisotropic negative-control fixtures |

These propositions are deliberately modest.  P8.2 proves one precisely scoped
finite-dimensional limit-law universality statement and P8.3 proves its
uniform bounded-basin extension after covariance whitening.  None proves compactness,
path-space or operator convergence, circle-packing convergence for the lab's
explicit Euler step, or object-level universality.

## 12. Theorem and experiment dependency map

### 12.1 Definitions

| ID | Contract |
|---|---|
| **D1** | typed finite carrier and decorated state |
| **D2** | finite-radius equivariant rule and locality class |
| **D3** | refinement and scaling program |
| **D4** | declared convergence topology |
| **D5** | observable and native-scale registry |
| **D6** | profile/object/limit-law universality hierarchy |
| **D7** | obstruction-certificate logic |
| **D8** | inverse target and compiler result |

### 12.2 Dependency graph

\[
\begin{array}{c}
D1\longrightarrow
\{P4.1,P4.2,P4.3,P4.4,P4.5,P5.1,P5.2,P6.1\}\\
D1+D2\longrightarrow\{P3.1,P3.2,P3.3,P3.4,P5.3\}\\
D1+D3+D4+D5\longrightarrow
\text{refinement and limit experiments}\\
D3+D4+D5+D6+P8.1+P8.2+P8.3\longrightarrow
\text{universality atlas}\\
P4.1+P4.2+P4.3+P5.1+D7+D8
\longrightarrow
\text{obstruction-aware sheet compiler}\\
P3.1+P3.4+D5+D7
\longrightarrow
\text{recognition lower bounds}.
\end{array}
\]

### 12.3 Experiment map

| Experiment | Dependencies | Output | Evidence ceiling without a new theorem |
|---|---|---|---|
| **X1 Locality audit** | D1, D2, P3.1, P3.2 | measured causal cone and relabeling audit | computational audit of a proved bound |
| **X2 Null refinement** | D1, D3, P6.1 | metric agreement under inherited PE subdivision | computational implementation validation |
| **X3 Dimension-flow atlas** | D3, D5 | \(d_V,d_s,d_w\) across physical windows | computational |
| **X4 Square/triangular diffusion** | D3–D6, P8.1–P8.3 | finite-profile comparison, proved robust whitened finite-dimensional diffusion limit, and metric negative control | bounded-basin iid finite-dimensional diffusion universality and graph-metric nonuniversality proved; heat-profile/operator/path-space claims remain computational or conjectural |
| **X5 Curvature compiler** | P4.1–P4.3, P5.1, D7, D8 | candidates, GB/CL obstruction, gauge report | finite exact where symbolic; otherwise computational candidate |
| **X6 Recognition adversary** | P3.4, D5, D7 | indistinguishable local pairs with different global labels | proved impossibility for the pair plus computational fixture |
| **X7 Programmable sheet emulator** | X5 plus material model | target shape, actuator settings, sensitivity | engineering |
| **X8 Physical sheet** | X7 plus calibration and measurements | reconstructed geometry and repeatability | engineering |
| **X9 Cross-platform replication** | P5.3 and all schemas | current bounded digest/focused-test comparison; new records for any expanded U2 or instrumentation surface | computational for the declared software surface; engineering only after calibrated instrumentation |

### 12.4 First theorem targets

1. **T1 compactness.**  **conjectural:** a declared bounded-degree,
   uniformly doubling, noncollapsing metric-measure rule class with controlled
   cell quality has a subsequential marked metric-measure limit.
2. **T2 operator convergence.**  **conjectural:** the selected local diffusion
   forms Mosco-converge after the declared scaling on the benchmark
   refinements.
3. **T3 operator universality.**  **conjectural:** extending the proved iid
   finite-dimensional result P8.2, two microscopically distinct,
   covariance-matched diffusion families share a common semigroup/operator
   limit while the graph-length metric negative control remains distinct.
4. **T4 inverse rigidity.**  **conjectural outside the exact Chow–Luo class:**
   the obstruction-aware compiler identifies all realizable curvature targets
   in a specified actuator family up to declared gauges.
5. **T5 recognition lower bound.**  The finite pairwise bound P3.4 is proved;
   a minimax lower bound under noisy multi-root sampling is
   **conjectural**.
6. **T6 defect stability.**  **conjectural:** bounded, sparse local metric
   defects induce a quantitatively controlled marked GHP and
   curvature-measure deviation under a nondegenerate refinement regime.

Each target must be replaced by a fully quantified theorem statement before
proof work begins; the prose above is a research direction, not a manuscript
claim.

## 13. Research implementation order

### Phase A — schema and exact gates

Implement D1–D8, all elementary proposition fixtures, and three-valued
certificate logic.  Preserve the 26 release-one core tests.  Add property
tests for relabeling, causal cones, bipartite radius gauge, metric stability,
and metric-null subdivision.

**Exit:** every result carries an evidence label; impossible, candidate, and
unresolved are distinct serialized states.

### Phase B — two refinement baselines

Build:

1. a metric-null piecewise-Euclidean subdivision family; and
2. a graph diffusion family with explicit distance, measure, and time scaling.

The first is the geometry null control.  The second exposes finite-size and
clock effects.

**Exit:** matched physical-scale profiles, mesh-quality tables, and
cross-platform deterministic records.

### Phase C — universality and nonuniversality pair

Run square and triangular periodic diffusion with precommitted covariance
calibration.  Report:

- spectral and walk profile convergence;
- local weak rooted-ball differences;
- graph-metric ball anisotropy;
- facewise-metric alternative, if implemented;
- perturbation ensembles; and
- one deliberately anisotropic diffusion negative control.

The desired first finding is nuanced: shared diffusion profiles alongside a
detectably different graph-metric limit.  That is more informative than
forcing one yes/no universality badge.

### Phase D — obstruction-aware inverse design

Add compatibility in increasing strength:

1. face metric and link gates;
2. exact Gauss–Bonnet;
3. exact closed-surface Chow–Luo subset slacks;
4. disk certification only through symmetric doubling;
5. circle-radius gauge analysis;
6. numerical curvature-flow candidates;
7. held-out refinement validation; and
8. actuator/material constraints.

**Exit:** sphere, torus, and saddle-like targets; at least one certified
infeasible target; at least one unresolved target; no conflation between the
two.

### Phase E — programmable sheet

Map intrinsic targets to an emulator whose local variables are hinge angle,
edge rest length, or differential strain.  The continuum material model,
fabrication tolerance, camera reconstruction, and controller are separate
engineering layers.  A valid intrinsic curvature target need not have a
stress-free embedding in \(\mathbb R^3\).

**Exit:** fabrication-ready files and hardware-in-the-loop replay.  Physical
success becomes **engineering**, not a proof of the continuum theory.

### Phase F — scoped cross-platform replay and expanded replication

The bounded alpha software surface has local content-addressed inputs
`artifacts/global-geometry-ii/certificates/macos-local-v2.json` and
`artifacts/global-geometry-ii/certificates/windows-local-v1.json`.  Their
external
`artifacts/global-geometry-ii/certificates/macos-windows-comparison-v1.json`
record closes only the declared manifest,
release-index, source, scientific-artifact, reproduction-resource, and
canonical nine focused PASS suite identity/path surface.  Neither local record
alone makes a cross-platform claim, and the comparison does not authenticate
machine independence or compare suite output, timing, or performance.

Confirmatory U2 ensembles, numerical tolerance audits beyond addressed
artifacts, vision fixtures, camera/device behavior, and hardware
instrumentation are expanded surfaces.  Each must freeze new inputs, emit new
Darwin and Windows local records, and produce a new content-addressed
comparison.  Byte equality is required where the new contract declares
canonical exact JSON; floating eigensystems and optimizers need registered
tolerances or justified enclosures.  Physical, camera, and hardware validation
remain `NOT_RUN` until separately approved and performed.

## 14. Application transfer boundaries

| Application | Mathematical core that may transfer | Additional evidence required | Forbidden inference |
|---|---|---|---|
| Programmable material | PE compatibility, curvature target, actuator gauge, local feedback | calibrated constitutive model, embedding mechanics, fabrication tolerance | intrinsic feasibility implies stress-free physical shape |
| Morphogenesis | local reaction–diffusion and metric growth profiles | biological parameter fit, mechanics, interventions, held-out tissue data | a similar pattern identifies the biological mechanism |
| Network design | components, weighted diffusion, curvature/transport profiles | domain-specific traffic and failure model | one discrete curvature scalar predicts resilience |
| Manifold learning | graph operator, scale profiles, persistent topology | sampling/noise model and statistical consistency | a finite descriptor proves a unique latent manifold |
| Swarm control | causal cones, conservative consensus, topology obstruction | collision avoidance, asynchronous delays, sensing and actuator model | synchronous graph simulation is a robot controller |
| Emergent spacetime | relational metric/operator limit as a mathematical toy | Lorentzian causality, dynamics, quantum and empirical structure | a graph with \(d_s\approx4\) is physical spacetime |

The last column is **speculative** territory and may not feed back into theorem
or compiler labels.

## 15. Falsification ledger

| Tempting statement | Correct boundary |
|---|---|
| a finite-radius rule is local because its formula mentions neighbors | false if neighbor selection, normalization, conflict resolution, or feedback uses undeclared global data |
| two seeds agree, therefore the rule is universal | false; this is finite robustness at most |
| two dimension slopes agree, therefore the spaces are the same | false; profiles are incomplete invariants |
| more vertices mean a refinement | false without a resolution map, scaling, and mesh-quality contract |
| subdivision demonstrates emergence | false when P6.1 makes it a metric-null operation |
| Gauss–Bonnet passes, therefore a curvature target is realizable | false; it is only the first global necessary condition |
| an optimizer failed, therefore the target is impossible | false; status is unresolved without a verified obstruction |
| the curvature flow converged once, therefore it always converges | false outside a proved basin and theorem class |
| local weak convergence gives global shape | false; diameter and topology can escape every fixed rooted ball |
| spectral convergence follows from metric convergence | false without operator/energy hypotheses |
| square and triangular graph lattices have the same \(d_s\), therefore the same geometry | false for their one-skeleton metrics; this may be diffusion-profile universality only |
| \(d_s=2d_V/d_w\) must hold | false without the required heat-kernel scaling hypotheses |
| a valid intrinsic sheet target has a realizable embedding | false; extrinsic mechanics adds compatibility and stress constraints |
| a Windows numerical mismatch refutes a theorem | false until exact outputs, floating tolerances, and dependency identities are separated |

## 16. Literature anchors and novelty boundary

The foundations deliberately synthesize established theories.

- Piecewise-flat deficit curvature begins with
  [Regge, 1961](https://doi.org/10.1007/BF02733251).
- Curvature-measure convergence for suitable nondegenerate polyhedral
  approximations is developed by
  [Cheeger, Müller, and Schrader,
  1984](https://doi.org/10.1007/BF01210729).
- Incidence-based differential operators and discrete exterior calculus are
  developed by
  [Desbrun, Hirani, Leok, and Marsden,
  2005](https://arxiv.org/abs/math/0508341).
- Local weak limits of finite rooted graphs are anchored by
  [Benjamini and Schramm,
  2001](https://doi.org/10.1214/EJP.v6-96).
- Metric-measure convergence and curvature frameworks are developed by
  [Sturm, 2006](https://doi.org/10.1007/s11511-006-0002-8).
- Varying-space spectral and Dirichlet-form convergence is developed by
  [Kuwae and Shioya,
  2003](https://doi.org/10.4310/CAG.2003.v11.n4.a1).
- Circle-packing curvature flow and its convergence in its declared surface
  class are developed by
  [Chow and Luo,
  2003](https://doi.org/10.4310/jdg/1080835659).
- Discrete conformal existence and uniqueness in a broader polyhedral setting
  are developed by
  [Gu, Luo, Sun, and Wu,
  2018](https://doi.org/10.4310/jdg/1527040872).
- Persistence stability is established by
  [Cohen-Steiner, Edelsbrunner, and Harer,
  2007](https://doi.org/10.1007/s00454-006-1276-5).
- The affine rigidity of isometries between real normed spaces used in P8.1
  is the theorem of S. Mazur and S. Ulam, *Sur les transformations
  isométriques d'espaces vectoriels normés*, C. R. Acad. Sci. Paris 194
  (1932), 946–948.

The **proved** contributions of this document are elementary contract
theorems: causal propagation, equivariance, fixed-carrier topology,
local-observer indistinguishability, triangle gluing, circle-length
compatibility, finite Gauss–Bonnet, spectral nullity, flux conservation,
circle-radius gauge rigidity, fixed-graph metric stability, deterministic
replay, and metric-null subdivision.

The provisional research contribution is their assembly into one
obstruction-aware universality contract with implementation schemas and
falsification gates.  No literature-priority claim is made.  Beyond the
precisely scoped finite-dimensional iid diffusion limits P8.2 and P8.3,
bounded-disk, object, metric, operator, path-space, and material universality;
continuum generability; arbitrary inverse realizability; material adequacy;
and physical interpretation remain explicitly unproved until separately
discharged.

## 17. Foundations completion gate

This foundations workstream is complete when:

1. D1–D8 are implemented as closed versioned schemas;
2. every P3.1–P6.1 fixture passes under relabeling and adversarial inputs;
3. graph-length and piecewise-Euclidean metrics cannot be confused in an
   export;
4. every refinement family declares distance, measure, and time scaling;
5. every universality comparison declares its topology and claim level;
6. obstruction reports distinguish impossible, candidate, unresolved, and
   out-of-scope;
7. the square/triangular benchmark is labeled profile-only unless a common
   metric-object contract is supplied;
8. the inverse compiler includes Gauss–Bonnet, Chow–Luo subset, and
   circle-radius gauge gates in their exact scopes;
9. the bounded alpha replay status remains delegated to its content-addressed
   comparison, while every expanded U2, numerical, vision, device, or hardware
   surface receives new platform-local records and a new scoped comparison;
   and
10. every public-facing application statement preserves the evidence grammar.

At that point Global Geometry II can ask its central question without hiding
the quantifiers:

\[
\boxed{
\begin{gathered}
\text{For which declared local-rule classes, perturbation families,}\\
\text{scalings, and convergence topologies does a prescribed}\\
\text{global metric-measure-operator world exist uniquely and robustly?}
\end{gathered}}
\]
