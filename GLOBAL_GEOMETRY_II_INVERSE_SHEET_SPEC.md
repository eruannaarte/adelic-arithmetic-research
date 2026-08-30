# Global Geometry II: obstruction-aware inverse design and programmable-sheet specification

## Status, outcome, and scope

**Document status:** proposed research and implementation contract, 2026-08-30;
not peer reviewed and no literature-priority claim.  No hardware has been
purchased, fabricated, connected, or experimentally validated. Nothing in
this document is a publication claim.

This workstream answers a deliberately bounded form of the Global Geometry II
question:

\[
\boxed{
\text{target intrinsic geometry}
\longrightarrow
\text{compatibility certificate}
\longrightarrow
\text{candidate local variables and rules}
\longrightarrow
\text{refined digital prediction}
\longrightarrow
\text{small physical test}
}
\]

It extends the existing Global Geometry Lab without changing its scientific
contract. The current lab already supplies finite complexes, angle-defect
curvature, exact topology, a necessary Gauss--Bonnet target check, and the
radius-one feedback

\[
u_i^{n+1}=u_i^n+\eta\bigl(K_i^*-K_i(u^n)\bigr),
\qquad u_i=\log r_i,
\qquad \ell_{ij}=r_i+r_j.
\]

The first new compiler slice must remain dependency-free and usable without
hardware. Its central addition is not another optimizer; it is a fail-closed
answer to **why** a requested target is or is not compatible with a declared
local metric model. Extrinsic embedding, elasticity, cameras, and actuation are
separate downstream stages and may never be used to upgrade an intrinsic
compatibility result.

### Required separation of claims

The compiler must keep the following questions distinct:

1. **Intrinsic compatibility:** do local edge lengths or circle variables
   define a valid piecewise-flat metric with the requested curvature and
   topology?
2. **Model realizability:** is that metric realizable inside the selected
   family, such as tangency circle packings or an integer-valence tile kit?
3. **Extrinsic embeddability:** can the metric be placed in \(\mathbb R^3\)
   without unacceptable strain or self-intersection?
4. **Mechanical selection:** will the actual hinges, stiffness, gravity, and
   boundary conditions select the desired embedding among possible ones?
5. **Instrument observability:** can the camera arrangement distinguish and
   measure the resulting configuration?

A pass at level 1 or 2 does not imply a pass at levels 3--5. A failed numerical
embedding search means `NO_SOLUTION_FOUND`, not “mathematically impossible.”

## 1. Evidence and status contract

The public `evidenceClass` field reuses the four labels of the first lab. The
new `basis` field adds precision without inventing a competing evidence ladder.

| `evidenceClass` | Allowed `basis` values here | What may be claimed |
|---|---|---|
| `exact-finite-identity` | `combinatorial-identity`, `theorem-instance`, `exhaustive-finite-check` | An exact statement for the supplied finite complex and the explicitly declared model/hypotheses |
| `finite-numerical-estimate` | `optimization`, `simulation`, `refinement-study`, `uncertainty-ensemble`, `camera-estimate` | A reproducible finite estimate with tolerances, seeds, residuals, and failure modes |
| `research-target` | `continuum-limit`, `general-inverse-design`, `universality`, `physical-validation` | An objective not established by the present artifacts |
| `application-analogy` | `programmable-sheet`, `growth-metric`, `actuated-shell` | A mapping from the mathematical model to an application; not empirical adequacy |

Every gate also has one of these statuses:

- `PASS` -- the declared check succeeded;
- `FAIL` -- a witness violates a necessary condition or a declared hard bound;
- `MARGINAL` -- the nominal result passes but its certified or estimated margin
  is below the requested guard band;
- `INCONCLUSIVE` -- the chosen procedure cannot decide;
- `NOT_APPLICABLE` -- the gate is outside the selected model; or
- `NOT_RUN` -- no result exists.

Only a `FAIL` with `basis: theorem-instance`, `combinatorial-identity`, or
`exhaustive-finite-check` may use `impossibleInDeclaredModel: true`. Physical
language must instead say `infeasibleUnderDeclaredBounds` or
`notYetExperimentallyValidated`.

## 2. Mathematical models

### 2.1 Shared surface state

The intrinsic compiler receives a finite triangular complex

\[
T=(V,E,F),
\]

with a declared compact surface topology, boundary set \(\partial V\), and one
of the metric families below. Its finite curvature is

\[
K_i(\ell)=
\begin{cases}
2\pi-\displaystyle\sum_{f\ni i}\alpha_{fi}(\ell), & i\notin\partial V,\\[6pt]
\pi-\displaystyle\sum_{f\ni i}\alpha_{fi}(\ell), & i\in\partial V.
\end{cases}
\]

The topology and angle conventions must match the current lab. In particular,
the drawing is never authoritative for intrinsic length or topology.

### 2.2 Model CP: Euclidean weighted circle-packing metrics

Assign \(r_i>0\) and edge intersection angles
\(\Phi_{ij}\in[0,\pi/2]\). The local length law is

\[
\ell_{ij}
=
\sqrt{r_i^2+r_j^2+2r_ir_j\cos\Phi_{ij}}.
\]

Tangency is the present lab's special case \(\Phi_{ij}=0\), hence
\(\ell_{ij}=r_i+r_j\). The Euclidean scale gauge is fixed by

\[
\sum_{i\in V}u_i=0,\qquad u_i=\log r_i,
\]

or an equivalent declared normalization. Changing the gauge cannot change
angle defects.

This is the first certified compiler model. It does not represent arbitrary
edge metrics, elasticity, or a physical actuator.

### 2.3 Model EM: arbitrary positive edge metrics

Assign \(\ell_e>0\) directly, subject to strict triangle inequalities on each
face. This model can express more metrics than Model CP, but the first release
has only exact surface, topology, triangle, and Gauss--Bonnet gates. Target
realizability and embedding are numerical. Therefore a successful solve is a
finite numerical estimate, while a solver failure is inconclusive.

### 2.4 Model QV: equilateral integer-valence modules

For equilateral triangular faces, every corner angle is \(\pi/3\). If \(q_i\)
triangles meet at an interior vertex and \(q_i^\partial\) triangles meet at a
boundary vertex, then

\[
K_i^{\rm QV}=\frac{(6-q_i)\pi}{3},
\qquad
K_i^{\partial,{\rm QV}}=\frac{(3-q_i^\partial)\pi}{3}.
\]

This finite model is the basis of the passive programmable-sheet demonstrator.
It gives exact intrinsic defects for a correctly assembled complex. It does not
fix the extrinsic fold angles.

### 2.5 Model ES: elastic-shell embedding

Given a compiled rest metric \(\ell^*\), rest dihedrals \(\theta_e^0\), and a
candidate embedding \(x:V\to\mathbb R^3\), a proposed simulation objective is

\[
\begin{aligned}
E_{\rm shell}(x)
={}&
\frac{k_s}{2}\sum_{e=(i,j)}w_e^s
\left(\frac{\lVert x_i-x_j\rVert-\ell_e^*}{\ell_e^*}\right)^2\\
&+\frac{k_b}{2}\sum_{e\in E_{\rm int}}w_e^b
\bigl(\theta_e(x)-\theta_e^0\bigr)^2
+E_{\rm collision}(x)+E_{\rm gravity}(x)+E_{\rm boundary}(x).
\end{aligned}
\]

This is an engineering model. Its minimizer can be nonunique and
initialization-dependent. It may predict a physical experiment only after
calibration and validation.

## 3. Exact intrinsic feasibility gates

The compiler evaluates gates in order and never runs a costly optimizer after
an exact rejection unless the user explicitly requests a diagnostic repair.

### G0 -- schema, units, and finite bounds

Reject unknown fields, nonfinite values, inconsistent units, duplicate IDs,
oversized inputs, and unsupported target/model combinations. Configuration
text is data and is never evaluated as code. Normalize units internally to
SI, while retaining the original unit declarations in the report.

**Certificate codes:** `SCHEMA_INVALID`, `NONFINITE_VALUE`,
`UNSUPPORTED_TARGET_CLASS`, `RESOURCE_BOUND_EXCEEDED`.

### G1 -- complex and surface validity

Reuse the current fail-closed surface gate and add explicit checks for:

- face uniqueness and orientation consistency;
- positive, nonrepeated vertices in every triangle;
- edge-manifold incidence: one incident face on the boundary, two in the
  interior;
- path/cycle vertex links;
- declared orientability and boundary-component count;
- computed \((\beta_0,\beta_1,\beta_2,\chi)\) versus the target topology; and
- connectedness when required by a theorem-backed model.

**Certificate codes:** `SURFACE_INVALID`, `TOPOLOGY_MISMATCH`,
`DISCONNECTED_DOMAIN`.

### G2 -- local curvature bounds

Every nondegenerate Euclidean cone has positive total angle. Therefore

\[
K_i^*<2\pi\quad(i\notin\partial V),
\qquad
K_i^*<\pi\quad(i\in\partial V).
\]

These are necessary, not sufficient. A violation returns the vertex as a
minimal local witness.

**Certificate code:** `CURVATURE_LOCAL_UPPER_BOUND`.

### G3 -- Gauss--Bonnet total

For the declared compact triangulated surface with boundary-angle convention,

\[
\sum_{i\in V}K_i^*=2\pi\chi(T).
\]

Use the scale-aware floating comparison

\[
\tau_{\rm GB}
=64\,\epsilon_{\rm mach}
\max\!\left(1,\sum_i|K_i^*|,|2\pi\chi|\right)
\]

for values entered as binary floating point. The report always includes the
unrounded residual. Exact rational multiples of \(\pi\), when supplied through
the symbolic target vocabulary, are compared symbolically.

The compiler must not silently repair an explicit incompatible target. It may
offer the disclosed projection

\[
\widehat K_i=K_i^*-
\frac{w_i}{\sum_jw_j}
\left(\sum_jK_j^*-2\pi\chi\right)
\]

as a new candidate request, preserving both the original and projected target.

**Certificate code:** `GAUSS_BONNET_TOTAL`.

### G4 -- Chow--Luo curvature-polytope obstruction for Model CP

This gate is exact only under all of these declared hypotheses:

- \(T\) is a connected triangulation of a closed surface;
- \(T\) satisfies the simplicial/generalized-triangulation hypotheses used by
  Chow--Luo (in particular no loops or double edges, no degree-one or
  degree-two vertices, no null-homotopic loops of at most two edges, and at
  most one face on a given vertex triple);
- the background triangles are Euclidean;
- \(\Phi:E\to[0,\pi/2]\); and
- the metric is the weighted circle-packing metric of Model CP.

For every nonempty proper subset \(I\subset V\), let \(F_I\) be the full
subcomplex whose cells have all vertices in \(I\). Let
\(\operatorname{Lk}(I)\) be the set of pairs \((e,v)\) for which
\(v\in I\), neither endpoint of \(e\) is in \(I\), and \(e\) with \(v\)
forms a triangle. Define the **Chow--Luo slack**

\[
\Delta_{\rm CL}(I;K^*,\Phi)
=
\sum_{i\in I}K_i^*
+\sum_{(e,v)\in\operatorname{Lk}(I)}
\bigl(\pi-\Phi(e)\bigr)
-2\pi\chi(F_I).
\]

The target is in the open curvature polytope precisely when

\[
\sum_iK_i^*=2\pi\chi(T)
\quad\text{and}\quad
\Delta_{\rm CL}(I;K^*,\Phi)>0
\quad\text{for every proper nonempty }I.
\]

Under the hypotheses above, this gives a necessary-and-sufficient
realizability certificate for normalized Model CP. It is stronger than the
Gauss--Bonnet gate and supplies an informative obstruction witness:

- the violating subset \(I\);
- \(\chi(F_I)\);
- the members and angle weights of \(\operatorname{Lk}(I)\);
- target curvature mass \(\sum_{i\in I}K_i^*\);
- required lower bound;
- signed slack \(\Delta_{\rm CL}\); and
- a suggested minimum curvature redistribution.

Strict inequalities require a numerical guard. With requested guard
\(\rho_{\rm CL}>0\):

- `PASS` if every exhaustively evaluated slack is at least
  \(\rho_{\rm CL}\);
- `MARGINAL` if every slack is positive but the minimum is below the guard;
- `FAIL` if a slack is nonpositive beyond roundoff; and
- `INCONCLUSIVE` if the search was not exhaustive and found no violation.

The reference implementation should exhaust all subsets for small complexes
(browser default \(|V|\le18\), worker/Node target \(|V|\le24\)). A validated
branch-and-bound or integer formulation may extend the exact range. Heuristic
subset search may find a valid obstruction, but failure to find one cannot
produce an exact pass.

**Certificate codes:** `CHOW_LUO_SUBSET`, `CHOW_LUO_MARGIN`,
`CHOW_LUO_SEARCH_INCOMPLETE`.

### G5 -- certified disk mode by symmetric doubling

The first release must not apply the closed-surface theorem directly to a
surface with boundary. A disk target receives an exact Model CP result only by
a declared symmetric double:

1. duplicate all interior vertices and faces;
2. identify corresponding boundary vertices and edges;
3. verify that the result is a valid closed connected triangulation;
4. give each interior copy the original target curvature; and
5. map each boundary defect to
   \(\widetilde K_i^*=2K_i^{\partial,*}\).

The doubled total is twice the original disk total. Run G2--G4 on the double.
Because the doubled target and triangulation possess the reflection symmetry
and normalized Model CP is rigid under the theorem's hypotheses, the compiled
radii must respect that symmetry. Restrict them back to one disk copy.

If any doubling hypothesis fails, the disk result is `INCONCLUSIVE` for Model
CP; it must not be mislabeled impossible.

**Certificate codes:** `DOUBLE_INVALID`, `DOUBLE_TARGET_ASYMMETRIC`,
`DOUBLE_CHOW_LUO_SUBSET`.

### G6 -- metric positivity and triangle margin

For every candidate radius or edge vector, require positive finite lengths and
for each face \((i,j,k)\)

\[
m_{ijk}=\min\{
\ell_{ij}+\ell_{jk}-\ell_{ki},
\ell_{jk}+\ell_{ki}-\ell_{ij},
\ell_{ki}+\ell_{ij}-\ell_{jk}
\}>0.
\]

Report the relative margin
\(m_{ijk}/\max(\ell_{ij},\ell_{jk},\ell_{ki})\). A candidate below the
fabrication or numerical guard is marginal even if mathematically positive.

**Certificate codes:** `NONPOSITIVE_LENGTH`, `TRIANGLE_INEQUALITY`,
`TRIANGLE_MARGIN_LOW`.

## 4. Compiler architecture and interfaces

### 4.1 Implementable slices

**Slice I -- certified digital curvature compiler, no hardware**

- closed JSON schema and deterministic normalization;
- G0--G6;
- exact subset witnesses in the bounded regime;
- Model CP radius solve with gauge fixing and residual history;
- the three small star targets and a closed tetrahedral obstruction target;
- deterministic export and focused tests.

This is the first integration target. It can be implemented in the current
dependency-free JavaScript core and exercised in Node and the browser.

**Slice II -- numerical edge metric and embedding**

- Model EM optimization;
- Model ES quasi-static embedding with collision diagnostics;
- nested refinement reports;
- uncertainty ensembles and target repair proposals.

**Slice III -- fabrication and measurement package**

- deterministic SVG/PDF/DXF template generation;
- passive modular sheet assembly;
- prerecorded camera fixtures and reconstruction;
- human-in-the-loop closed-loop trials.

**Slice IV -- optional active hardware**

- hardware-in-the-loop transport emulator first;
- bounded actuator protocol, watchdog, and emergency stop;
- calibration on approved hardware; and
- future Windows camera/device instrumentation with a separately scoped
  comparison.

Slice IV requires separate approval before purchase, fabrication, or physical
connection.

### 4.2 Request interface

The following TypeScript-like contract is normative; an implementation may be
plain JavaScript.

```ts
type EvidenceClass =
  | "exact-finite-identity"
  | "finite-numerical-estimate"
  | "research-target"
  | "application-analogy";

interface InverseDesignRequest {
  schemaVersion: 2;
  id: string;
  seed: string;
  target: {
    kind:
      | "intrinsic-curvature"
      | "intrinsic-edge-metric"
      | "extrinsic-embedding"
      | "dimension-profile";
    topology: {
      surface: "disk" | "sphere" | "annulus" | "torus" | "custom";
      orientable: boolean;
      boundaryComponents: number;
      expectedBetti?: [number, number, number];
    };
    discretization: {
      generator?: Record<string, unknown>;
      complex?: FiniteTriangleComplex;
    };
    curvature?: {
      basis: "vertex" | "procedural" | "symbolic-pi";
      values?: number[];
      piCoefficients?: Array<{ numerator: number; denominator: number }>;
      procedural?: "uniform" | "boundary-wave" | "cone" | "saddle" | "dipole";
      parameters?: Record<string, number>;
    };
    edgeLengths?: number[];
    embedding?: { vertices: Array<[number, number, number]> };
    dimensionProfile?: Array<{ scale: number; dimension: number }>;
  };
  models: Array<
    | "circle-packing-tangency"
    | "circle-packing-weighted"
    | "edge-metric"
    | "equilateral-valence"
    | "elastic-shell"
  >;
  constraints: {
    phiByEdge?: number[];
    radiusBounds?: [number, number];
    edgeLengthBounds?: [number, number];
    allowedInteriorValences?: number[];
    allowedBoundaryValences?: number[];
    maxStrain?: number;
    allowTopologyChange: boolean;
  };
  verification: {
    gbTolerance?: number;
    chowLuoGuard: number;
    exactSubsetLimit: number;
    optimizerTolerance: number;
    maxIterations: number;
    refinementLevels: number;
    uncertaintySamples: number;
    uncertaintyModel?: UncertaintyModel;
  };
  fabrication?: FabricationConstraints;
}
```

`dimension-profile` is an accepted target vocabulary so the atlas and compiler
share one envelope, but Slice I must return `UNSUPPORTED_TARGET_CLASS` rather
than pretending that a two-dimensional sheet compiler can synthesize an
arbitrary scale-dependent dimension. A later graph/cell-complex compiler may
own that target class.

### 4.3 Report interface

```ts
interface CompileReport {
  schemaVersion: 2;
  compilerVersion: string;
  requestId: string;
  requestDigest: string;
  normalizedRequest: InverseDesignRequest;
  status: "PASS" | "FAIL" | "MARGINAL" | "INCONCLUSIVE";
  gates: GateReport[];
  candidates: CandidateLocalProgram[];
  selectedCandidateId: string | null;
  obstructionCertificates: ObstructionCertificate[];
  repairProposals: RepairProposal[];
  refinement: RefinementReport | null;
  robustness: RobustnessReport | null;
  fabricationPackage: FabricationPackageManifest | null;
  replay: {
    deterministic: boolean;
    seed: string;
    platformIndependentInputsDigest: string;
    methods: string[];
  };
  claims: {
    demonstrated: string[];
    notDemonstrated: string[];
  };
}

interface ObstructionCertificate {
  code: string;
  status: "FAIL" | "MARGINAL" | "INCONCLUSIVE";
  stage: "intrinsic" | "model" | "embedding" | "fabrication" | "sensing" | "hardware";
  evidenceClass: EvidenceClass;
  basis: string;
  impossibleInDeclaredModel: boolean;
  statement: string;
  hypotheses: string[];
  witness: Record<string, unknown>;
  observed: number | null;
  required: string;
  signedMargin: number | null;
  tolerance: number | null;
  repairHints: string[];
}
```

The report contains no executable callbacks. Arrays are deterministically
ordered by stable IDs. Replaying the same normalized request and seed must
produce the same intrinsic candidates, gate order, witnesses, and numerical
history within a declared platform tolerance.

### 4.4 Candidate local program

Each candidate must identify which work is global compilation and which rule
is local runtime:

```ts
interface CandidateLocalProgram {
  id: string;
  model: string;
  targetUsed: "original" | "repair-proposal";
  preRuntimeCompilation: {
    localityClass: "L2";
    operations: string[];
  };
  runtimeRule: {
    localityClass: "L0" | "L1";
    radius: number;
    synchronous: boolean;
    stateVariables: string[];
    immutableLocalTargets: string[];
    updateEquation: string;
  };
  topology: FiniteTriangleComplex;
  variables: {
    radii?: number[];
    edgeLengths?: number[];
    valences?: number[];
    hingeRestAngles?: number[];
  };
  objectiveHistory: number[];
  residuals: Record<string, number>;
  hardBoundsSatisfied: boolean;
  evidenceClass: EvidenceClass;
  caveats: string[];
}
```

For Model CP, the baseline exported runtime rule is exactly the lab-compatible
radius-one curvature-error update. A line search, Newton step, eigensolve, or
global gauge solve used by the compiler is disclosed as L2 and never described
as local dynamics.

## 5. Synthesis algorithms

### 5.1 Model CP solve

After exact admission, solve

\[
\min_{u:\,\sum_i u_i=0}
J_K(u)=\frac12
\bigl(K(u)-K^*\bigr)^T W_K\bigl(K(u)-K^*\bigr),
\]

with bounded \(u\), deterministic initialization, and a backtracking step that
must decrease \(J_K\). Slice I should first reuse the explicit local flow for
parity with the existing lab. A later compiler-only Gauss--Newton direction is

\[
\left(J_K'(u)^T W_KJ_K'(u)+\lambda P\right)\delta u
=-J_K'(u)^TW_K\bigl(K(u)-K^*\bigr),
\]

where \(P\) removes the scale-null direction. The report includes the gauge,
Jacobian method, damping, accepted steps, radius extrema, curvature residual,
and stop reason.

An exact feasibility pass plus a failed finite-iteration optimizer remains
`INCONCLUSIVE` computationally; it does not invalidate the theorem-backed
existence result.

### 5.2 Model EM solve

Use log lengths \(s_e=\log\ell_e\), triangle barriers, and

\[
J_{\rm EM}(s)
=w_K\lVert K(e^s)-K^*\rVert_{W_K}^2
+w_g\lVert s-s^0\rVert_{W_g}^2
+\mu\sum_{f}\psi\bigl(m_f(e^s)\bigr).
\]

The barrier \(\psi\) diverges as a triangle margin approaches zero. Report
whether bounds or barriers, rather than curvature, dominate the solution. No
general existence or uniqueness claim is made.

### 5.3 Model QV compilation

Quantize target curvature to an allowed module library:

\[
\min_{q_i\in Q_i}
\sum_iw_i\left(K_i^{\rm QV}(q_i)-K_i^*\right)^2
+\lambda_{\rm edit}N_{\rm local\ edits},
\]

subject to a valid triangulation and the exact Euler/defect budget. Candidate
edits include `ADD_SECTOR`, `REMOVE_SECTOR`, `EDGE_FLIP`, `INSERT_VERTEX`, and
`REMOVE_VERTEX`; each must carry its affected radius-one neighborhood and a
before/after surface-validity proof. Topology-changing edits require
`allowTopologyChange: true` and are interventions, not ordinary runtime steps.

If the requested curvature is outside the allowed quantized library, return
`CURVATURE_QUANTIZATION` as infeasible under that library, not impossible for
all sheets.

### 5.4 Extrinsic target as a soft, nonunique objective

If a target supplies positions \(x_i^*\), first extract or verify its intrinsic
edge metric. After intrinsic compilation, compare embeddings only after rigid
Procrustes alignment:

\[
J_X(x)=\min_{R\in SO(3),\,t\in\mathbb R^3}
\sum_iw_i\lVert Rx_i+t-x_i^*\rVert^2.
\]

Run the shell solve from a declared ensemble of initial folds. Report distinct
local minima, self-intersections, strain, and target error. A metric alone does
not generally select one embedding; hinge rest angles or boundary conditions
are a separate local program.

### 5.5 Repair proposals

Repairs are never silently substituted. The report may propose:

- Gauss--Bonnet projection while preserving selected pinned vertices;
- nearest guarded point in the Chow--Luo polytope,
  \(\min\lVert K-K^*\rVert_W^2\) subject to total curvature and
  \(\Delta_{\rm CL}(I)\ge\rho\);
- redistribution of curvature away from a violating witness subset;
- triangulation refinement or a legal edge-flip sequence;
- wider but explicitly bounded radius/edge/module ranges;
- a different topology or boundary-curvature budget; or
- demotion of an extrinsic hard target to a soft selection objective.

The “nearest feasible” claim is exact only if all relevant constraints were
enumerated and the convex projection was solved to a certified tolerance.

## 6. Representative targets and expected results

| ID | Domain and request | Model | Expected result | Evidence boundary |
|---|---|---|---|---|
| `star-flat-q6` | Disk fan, six equilateral faces, \(K_c^*=0\), six boundary defects \(\pi/3\) | QV | exact pass; planar rest state is available | Exact intrinsic defects; flat physical state still depends on assembly |
| `star-cone-q5` | Disk fan, five faces, \(K_c^*=+\pi/3\), five boundary defects \(\pi/3\) | QV | exact pass; positive discrete cone | Cone-like embedding is a finite experiment, not forced uniquely by the metric |
| `star-saddle-q7` | Disk fan, seven faces, \(K_c^*=-\pi/3\), seven boundary defects \(\pi/3\) | QV | exact pass; negative discrete cone | Extrinsic saddle/fold is nonunique |
| `disk-dipole` | Disk with one \(+\pi/3\) and one \(-\pi/3\) interior target plus total boundary \(2\pi\) | CP and QV | compile after doubled subset checks; compare radius and valence realizations | Equality of macroscopic shapes is a research target |
| `sphere-uniform` | Icosphere target \(K_i^*=4\pi/|V|\) | CP | exact polytope admission plus numerical radius solve | Continuum round-sphere convergence requires refinement |
| `torus-flat` | Closed torus, \(K_i^*=0\) | CP | exact admission only if every subset inequality passes | An embedding in \(\mathbb R^3\) cannot be inferred from intrinsic admission |
| `cylinder-zero-interior` | Annular mesh, zero interior curvature with compatible boundary turning | EM | exact total/triangle checks; numerical solve | Boundary Model CP theorem is not implemented by disk doubling |
| `tetra-subset-reject` | Tetrahedral sphere target \((-6\pi/5,26\pi/15,26\pi/15,26\pi/15)\) | tangency CP | total is \(4\pi\), but singleton \(I=\{0\}\) violates the strict lower bound \(K_0>-\pi\) | Exact failure in the declared CP model |
| `sphere-zero-reject` | Sphere with all target defects zero | any finite Euclidean cone metric | Gauss--Bonnet rejection: required \(4\pi\) | Exact finite obstruction |
| `branching-sheet` | A Y-branch with a nonmanifold seam | surface compiler | fail G1 or route to a future stratified-complex model | Not proof that branching structures are impossible in other models |
| `scale-varying-dimension` | Requested \(d(r)\) profile | sheet Slice I | unsupported target class; route to atlas/graph compiler | Explicit research target |

For the tetrahedral example, the three positive values sum with
\(-6\pi/5\) to \(4\pi\) and each remains below \(2\pi\). Thus it is a
deliberate example that passes the obvious total and local upper gates but
fails a genuine subcomplex inequality.

## 7. Robustness and sensitivity

### 7.1 Exact robust margins where available

If target components have independent deterministic bounds
\(|\delta K_i|\le\varepsilon_i\), a sufficient robust Chow--Luo margin is

\[
\Delta_{\rm CL}(I;K^*,\Phi)-
\sum_{i\in I}\varepsilon_i-
\sum_{(e,v)\in\operatorname{Lk}(I)}\varepsilon_{\Phi,e}>0.
\]

The report stores both nominal and worst-case slacks and the first subset to
lose its guard. A similar interval audit applies to triangle inequalities and
fabrication length ranges.

### 7.2 Finite uncertainty ensemble

The engineering ensemble samples only declared uncertainties, for example:

- cut-length error and print scaling;
- hinge gap, stiffness, and rest-angle error;
- radius or edge actuator calibration;
- shell stiffness and friction ranges;
- camera intrinsics and pixel noise;
- marker dropout and occlusion; and
- initial-fold perturbations.

For sample \(s\), define success by all declared hard bounds and a target loss
below \(\tau_J\). Report sample count, seeds, failure taxonomy, empirical
success \(\widehat p\), and a two-sided Wilson interval. The lower 95% bound is

\[
p_L=
\frac{
\widehat p+z^2/(2N)-z\sqrt{\widehat p(1-\widehat p)/N+z^2/(4N^2)}
}{1+z^2/N},
\qquad z=1.96.
\]

Also report median error, 95th percentile error, worst observed error, and
CVaR over the worst 5%. These are finite numerical estimates, not distribution-
free reliability guarantees.

### 7.3 Conditioning

At a compiled point, estimate the gauge-reduced curvature Jacobian and actuator
Jacobian. Report smallest nonzero singular value, condition number, and the
least observable/controllable modes. A target near the polytope boundary or a
nearly singular Jacobian is `MARGINAL` even if its residual is small.

## 8. Refinement validation

Each refinement record uses the shared atlas fields:

```ts
interface RefinementLevel {
  level: number;
  characteristicSpacing: number;
  linearSize: number;
  vertexCount: number;
  parentMap?: number[];
  childMap?: number[][];
  intrinsicMetricDistortion: number;
  curvatureMeasureDiscrepancy: number;
  targetResidual: number;
  minimumTriangleMargin: number;
  minimumChowLuoSlack: number | null;
  embeddingShapeError: number | null;
}
```

For nested triangulations, prolong the target as a curvature measure and
restrict compiled measures back to a common coarse complex. Preserve total
curvature exactly during transfer. Compare:

- `intrinsicMetricDistortion`: relative distortion on declared landmark pairs
  or all pairs in the bounded regime;
- `curvatureMeasureDiscrepancy`: total-variation or Wasserstein discrepancy on
  the common support, with the chosen method named;
- optimizer target residual;
- topology and obstruction margins; and
- aligned extrinsic shape error, only when embedding is requested.

For an error \(E\) at consecutive characteristic spacings, report

\[
\operatorname{observedOrder}
=
\frac{\log(E_{\rm coarse}/E_{\rm fine})}
{\log(h_{\rm coarse}/h_{\rm fine})}.
\]

Three levels are the minimum compiler diagnostic. Four or more are required
before the result can participate in an atlas curve fit. No run is called
convergent merely because its finest error is small; the report needs a stable
window, nondegenerate triangles, fixed comparison semantics, and uncertainty
separated from discretization error.

## 9. Focused verification matrix

| Test | Construction | Required assertion |
|---|---|---|
| `INV-SCHEMA-01` | unknown key, `NaN`, oversized subset limit | fail closed with stable error paths |
| `INV-SURFACE-01` | duplicate face and nonmanifold edge | G1 rejects before curvature solve |
| `INV-GB-01` | zero-curvature sphere | exact `GAUSS_BONNET_TOTAL` witness |
| `INV-GB-02` | symbolic multiples of \(\pi\) on each q-star | exact total \(2\pi\) |
| `INV-CL-01` | tetrahedral uniform target | exhaustive positive Chow--Luo slack |
| `INV-CL-02` | `tetra-subset-reject` | singleton witness, slack \(-\pi/5\) |
| `INV-CL-03` | relabel the same tetrahedron | identical sorted witness under inverse relabeling |
| `INV-CL-04` | target at strict-polytope guard | `MARGINAL`, never rounded to exact pass |
| `INV-DOUBLE-01` | valid disk fan and symmetric target | doubled sphere passes topology and target mapping |
| `INV-DOUBLE-02` | asymmetric doubled boundary target | `DOUBLE_TARGET_ASYMMETRIC` |
| `INV-TRI-01` | one equality triangle | exact triangle rejection with face witness |
| `INV-CP-01` | supported sphere target | radius bounds, gauge, decreasing accepted objective, finite residual |
| `INV-CP-02` | same request and seed twice | byte-stable normalized intrinsic report, apart from declared timestamps |
| `INV-QV-01` | q=5, 6, 7 stars | center defects \(+\pi/3,0,-\pi/3\); every boundary defect \(\pi/3\) |
| `INV-QV-02` | unavailable q target | library-specific quantization certificate, not universal impossibility |
| `INV-EM-01` | admissible target with optimizer budget zero | `INCONCLUSIVE`, not exact failure |
| `INV-REF-01` | three nested disk meshes | exact target-mass preservation and named comparison fields |
| `INV-ROB-01` | fixed uncertainty seeds | stable ensemble summary and Wilson interval |
| `INV-EMBED-01` | two initial folds of q=7 | preserve both minima or disclose merge criterion; no uniqueness claim |
| `INV-SENSE-01` | prerecorded flat fiducial board | reconstruction passes calibrated error gates |
| `INV-SENSE-02` | core-face marker missing | closed-loop command inhibited and observability certificate emitted |
| `INV-HIL-01` | timeout, stale sequence, saturation, unplug faults | safe hold/disable and deterministic fault transcript |
| `INV-WIN-01` | clean bounded Windows software replay | content-addressed comparison of the declared release digest and focused PASS test surface only; no camera/device/hardware implication |

The current 26 Global Geometry tests remain a nonregression gate. New tests
must not weaken their locality, evidence, or configuration-schema assertions.

## 10. Passive programmable-sheet experiment

### 10.1 Experimental question

> Can changing one local sector count in an otherwise identical hinged
> triangular patch reliably change the sign and magnitude of its exact
> intrinsic angle defect, and does the global three-dimensional response agree
> with a calibrated discrete-shell model within declared uncertainty?

The primary result is the exact finite defect; the global 3-D response is the
experiment. The apparatus deliberately avoids gels, heat, lasers, and reactive
chemicals.

### 10.2 Geometry of the q-star

Build a topological disk from \(q\) separate equilateral triangles of side
\(s=60\,\mathrm{mm}\), all sharing a center vertex and hinged cyclically along
their radial edges. The disk has

\[
|V|=q+1,\qquad |E|=2q,\qquad |F|=q,\qquad \chi=1.
\]

At the center,

\[
K_c=2\pi-q\pi/3=(6-q)\pi/3.
\]

Every outer boundary vertex has two incident 60-degree corners, hence

\[
K_b=\pi-2\pi/3=\pi/3.
\]

Therefore

\[
K_c+\sum_{b=1}^{q}K_b
=\frac{(6-q)\pi}{3}+q\frac{\pi}{3}=2\pi,
\]

for all three configurations:

- \(q=5\): positive center defect \(+\pi/3\), cone-like response;
- \(q=6\): zero center defect, flat configuration available; and
- \(q=7\): negative center defect \(-\pi/3\), nonplanar saddle/fold response.

These equalities are exact for the ideal finite design: equilateral planar
faces with the stated incidence. A fabricated cardstock object is an
approximation. Its inferred defects use its calibrated side lengths/corner
angles and carry measurement uncertainty; they retain the
`finite-numerical-estimate` label even when their nominal values agree with the
exact template.

Seven reusable faces are enough. Adding or removing a face at the labeled seam
programs the center curvature while preserving disk topology. The final seam
for \(q=7\) must be closed after the patch is lifted out of the plane; forcing
it flat would require overlap or strain.

### 10.3 Proposed bill of materials -- no purchase authorization

Quantities and cost bands are planning estimates, not vendor quotes. Existing
equipment is preferred.

**Option A -- paper demonstrator, target incremental cost under US$20**

| Item | Proposed quantity/specification | Purpose |
|---|---|---|
| Printed face sheets | 2 A4 or Letter sheets, 250--300 gsm cardstock | seven rigid-enough equilateral faces plus spares |
| Hinge tape | low-tack paper, drafting, or thin cloth tape, about 2 m | reversible radial hinges |
| Cutting tools | scissors, metal ruler, cutting mat | template preparation |
| Temporary closure | small binder clips or removable tabs | close final radial seam; no loose magnets |
| Fiducials | printed directly on each face | per-face camera pose |
| Camera | existing 720p-or-better webcam or phone in local-camera mode | sensing |
| Support | books/cardboard stand or existing tripod | fixed camera view |

**Option B -- more durable passive kit, planning band under US$60 excluding
cameras**

| Item | Proposed specification | Note |
|---|---|---|
| Faces | 0.4--0.8 mm polypropylene/PET or 1 mm chipboard | cut edges must be deburred; scissors-compatible stock preferred |
| Hinges | textile/Tyvek strips with removable adhesive | lower hinge fatigue and bidirectional folding |
| Closures | hook-and-loop dots, paper fasteners, or lacing | avoid small high-strength magnets |
| Camera support | one or two existing webcams and fixed stands | second view reduces occlusion |

**Option C -- optional active research extension, not part of the first
physical milestone**

- one USB-powered microcontroller with explicit hardware enable;
- a current-limited 5 V supply;
- four to eight low-voltage microservos;
- compliant thread/tendon spools and guards;
- optional PWM driver;
- physical power disconnect/emergency stop; and
- a second camera.

Servos would control selected **extrinsic hinge preferences or seam closures**.
They do not change the intrinsic Gauss--Bonnet budget unless the mechanism
actually changes face angles, edge lengths, or combinatorics. That distinction
must appear in the interface and every result.

### 10.4 Fabrication-ready output contract

Slice III generates, but this specification does not yet create, the following
deterministic package:

```text
fabrication/<design-id>/
  faces.svg
  faces.pdf
  optional-faces.dxf
  assembly-q5.svg
  assembly-q6.svg
  assembly-q7.svg
  fiducial-map.json
  camera-calibration-board.pdf
  measurement-gauges.pdf
  fabrication-manifest.json
```

Template requirements:

- physical SVG/DXF units are millimetres;
- every triangle has vertices
  \((0,0),(60,0),(30,30\sqrt3)\,\mathrm{mm}\);
- cut lines, hinge lines, no-cut zones, labels, and fiducials use both semantic
  layer names and visibly different dash patterns, not color alone;
- each face has a unique ID, central-corner mark, left/right radial-edge label,
  boundary-edge label, and orientation arrow;
- the square fiducial outer size is 20 mm and remains inside a no-hinge region;
- nominal hinge gap is 1.0 mm and is recorded, never absorbed into face size;
- the page includes 10 mm and 100 mm scale bars;
- output has no printer “fit to page” dependency;
- the manifest records generator version, request digest, material assumptions,
  dimensions, tolerances, assembly graph, fiducial dictionary, page size, and
  SHA-256 digest of every file; and
- PDF and SVG geometry are cross-checked numerically before release.

Reject a print when the measured 100 mm bar differs by more than 0.5 mm unless
the measured scale is explicitly recalibrated into the reconstruction.

### 10.5 Assembly protocol

1. Print at 100% scale and verify both scale bars.
2. Cut seven faces and record measured side lengths at all three edges.
3. Reject or relabel any face whose maximum edge error exceeds the declared
   fabrication tolerance (provisional target: 0.5 mm).
4. Arrange \(q\) faces by face ID with central corners coincident.
5. Leave a 1.0 mm radial gap and bridge each adjacent radial pair with one
   flexible tape hinge. Do not tape the final seam yet.
6. For \(q=5\), lift and close the final seam without creasing the faces.
7. For \(q=6\), close the seam on a flat reference plane without forcing it.
8. For \(q=7\), lift into a low-strain nonplanar fold before closing the seam.
9. Photograph both sides, record material and hinge lot, and run the intrinsic
   assembly audit from the face/edge IDs.
10. Only after the intrinsic audit passes, acquire the calibrated 3-D trial.

The experiment should use at least five independent disassembly/reassembly
trials of each \(q\), randomizing assembly order with recorded seeds. This tests
repeatability of the selected embedding, not the already exact angle sum.

## 11. Sensing and reconstruction

### 11.1 Camera model and fiducials

Calibrate each camera from multiple views of a planar board, including radial
distortion. Detect one square ArUco-family fiducial per rigid face. The marker
dictionary and marker-to-face transform are fixed in `fiducial-map.json`.

For face \(f\), pose estimation yields \((R_f,t_f)\) and covariance or a
bootstrap approximation. Transform the known local triangle corners into
camera coordinates. A shared mesh vertex is fused from all incident face
estimates:

\[
\widehat x_v=
\left(\sum_{f\ni v}W_{vf}\right)^{-1}
\sum_{f\ni v}W_{vf}x_{vf},
\]

where \(W_{vf}\) is derived from reprojection and calibration uncertainty.
Report the unfused spread; do not hide inconsistent face poses by averaging.

Intrinsic angle defects are calculated from measured/calibrated face edge
lengths, the cosine law, and assembly incidence; the ideal symbolic template
result is retained separately. Camera positions measure the extrinsic realization:
dihedral angles, height range, RMS distance from the best-fit plane, face-normal
distribution, and aligned point-cloud distance to simulation.

### 11.2 Calibration sequence

1. Verify print scale and physical face side lengths.
2. Calibrate camera intrinsics from at least ten usable board views spanning
   image position and tilt; retain all residuals and rejected views.
3. Verify marker-to-face coordinates from the template manifest.
4. Measure a flat q=6 sheet on a reference plane.
5. Measure rigid reference wedges at nominal 0, 30, and 60 degree dihedrals.
6. If active hardware is later approved, sweep each channel independently at
   low rate to identify its bounded hinge-response column in the actuation
   Jacobian.
7. Freeze a versioned calibration record before target trials.

Provisional measurement validity gates, to be revised from pilot data:

- camera reprojection RMS \(\le1.0\) pixel;
- at least 80% of expected markers detected and every target-critical face
  directly observed;
- fused shared-edge endpoint discrepancy \(\le1.5\) mm or 2% of face side,
  whichever is larger;
- flat q=6 plane RMS \(\le2.0\) mm; and
- rigid-wedge dihedral error \(\le3\) degrees.

These are engineering acceptance targets, not achieved results. A trial failing
them is invalid, not unfavorable data to be discarded.

### 11.3 Observability failures

Return `SENSOR_UNOBSERVABLE` when target-critical faces are hidden, pose
ambiguity is unresolved, the calibration is stale, or uncertainty is larger
than the target distinction. One camera may be enough for shallow q-stars; a
second calibrated view is the preferred repair for occlusion. Inference through
hinge constraints may fill a display, but it is not a direct measurement and
must carry increased uncertainty.

## 12. Closed-loop control

### 12.1 Human-in-the-loop passive controller

For the first physical milestone, the controller recommends one local assembly
action and waits for a fresh valid measurement:

1. estimate current intrinsic program from face incidence;
2. compute target error and compatible action set;
3. score each legal `ADD_SECTOR`, `REMOVE_SECTOR`, or seam action by predicted
   target-loss decrease minus edit cost;
4. present the best action, its affected neighborhood, and expected defect
   change;
5. require the operator to confirm completion;
6. re-audit topology and remeasure; and
7. stop on target, no improving legal action, invalid sensing, or safety hold.

At no point should the controller infer assembly success merely because it
issued an instruction.

### 12.2 Optional bounded actuator controller

If actuation is later approved, identify a local linear response

\[
e_{t+1}\approx e_t+B\,\Delta a_t
\]

inside a calibrated neighborhood. A proposed bounded update is

\[
\Delta a_t=
\operatorname*{argmin}_{\Delta a}
\lVert e_t+B\Delta a\rVert_W^2+lambda\lVert\Delta a\rVert^2
\]

subject to position, velocity, current, and neighborhood limits. Only one
bounded step is applied before remeasurement. Commands are inhibited on stale
telemetry, invalid camera state, out-of-order sequence, high residual, or
watchdog timeout.

Servo hinge control selects an extrinsic embedding; it must not be scored as
success on intrinsic curvature unless the hardware really changes the metric or
combinatorics and the intrinsic audit confirms it.

## 13. Hardware-in-the-loop emulator

The HIL emulator is mandatory before any physical actuator connection. It uses
the same transport and state machine as hardware but defaults to a virtual
quasi-static plant.

### 13.1 Transport protocol

Each newline-delimited message has:

```json
{
  "protocol": "ggii-hil/1",
  "type": "COMMAND",
  "seq": 42,
  "monotonicTimeMs": 12034,
  "deadlineMs": 12534,
  "payload": {
    "channels": [
      {"id": "hinge-03", "positionDeg": 18.0, "maxRateDegPerSec": 10.0}
    ]
  },
  "checksum": "crc32-hex"
}
```

Required message types are `HELLO`, `CAPABILITIES`, `ARM`, `COMMAND`,
`TELEMETRY`, `HOLD`, `DISARM`, `ESTOP`, and `FAULT`. Hardware starts disarmed,
does not move on `HELLO`, rejects unknown channels and stale sequences, and
enters hold on missed heartbeat.

### 13.2 Virtual plant and fault injection

The emulator supports:

- discrete sector-add/remove events for the passive logical model;
- continuous hinge-rest-angle channels for the active extension;
- saturation, rate limit, backlash, delay, quantization, and observation noise;
- stuck channel, stale telemetry, corrupt checksum, timeout, disconnect,
  over-current flag, sensor dropout, and emergency-stop injection; and
- deterministic recording and replay of every command, telemetry frame, plant
  state, and safety transition.

The default run has no serial-port access. A future physical adapter requires
an explicit `--hardware` flag and explicit port identifier; environment
autodiscovery alone may not arm motion.

### 13.3 Bounded Windows replay and future instrumentation role

The bounded software snapshot has a content-addressed Windows local record at
`artifacts/global-geometry-ii/certificates/windows-local-v1.json`, paired with
`artifacts/global-geometry-ii/certificates/macos-local-v2.json`.
Cross-platform status is delegated to
`artifacts/global-geometry-ii/certificates/macos-windows-comparison-v1.json`,
which reports
`PASS_FOR_DECLARED_DIGEST_AND_TEST_SURFACE` only for the declared manifest,
release-index, source, scientific-artifact, reproduction-resource, and
canonical nine focused PASS suite identity/path surface.  Each local record by
itself remains a single-run record.

That comparison includes bounded compiler, HIL, and artifact test execution;
it does not establish suite-output or performance equality, new uncertainty
ensembles, prerecorded-image reconstruction, camera enumeration or
calibration, device discovery, actuator behavior, hardware safety, or physical
validation.  Those future instrumentation tasks require separately frozen
inputs, new platform records, and a new content-addressed comparison after the
relevant equipment and work are explicitly approved.

Windows-specific adapter paths should remain limited to device discovery and
port names. Mathematical, report, image-fixture, and protocol code should stay
shared, but shared source alone is not instrumentation evidence.

## 14. Safety and privacy

### Passive kit

- Prefer scissors-compatible cardstock and low-tack tape; use a cutting mat and
  cut away from hands.
- If a craft knife, punch, or rigid plastic is used, require adult supervision,
  eye protection as appropriate, and deburring of sharp edges.
- Do not use loose high-strength magnets; they are unnecessary and present an
  ingestion/pinch hazard.
- Do not force q=7 flat or push a buckled patch toward the face or eyes.
- Store small clips and fasteners away from children and pets.

### Optional active tier

- Use only low-voltage, current-limited 5 V power; no mains wiring and no loose
  lithium-polymer battery.
- Guard servo horns, spools, tendons, and pinch points; tie back hair and loose
  clothing.
- Enforce mechanical travel stops, software limits, rate limits, current/fault
  monitoring, watchdog hold, and a reachable physical power disconnect.
- Test one unloaded channel at a time before attaching the sheet.
- Never leave energized hardware unattended.

### Cameras and data

- Process video locally by default and frame the apparatus only.
- Do not record people, audio, or unrelated spaces.
- Release derived fiducial poses and deliberately selected apparatus images,
  not raw ambient video, unless separately reviewed.
- Record calibration and trial consent/provenance in the experiment manifest.

## 15. Reproducibility package and data schema

Each digital or physical trial exports:

```text
run/<run-id>/
  request.json
  compile-report.json
  candidate-local-program.json
  refinement-report.json
  robustness-report.json
  fabrication-manifest.json
  calibration.json
  trial-protocol.json
  observations.jsonl
  hil-transcript.jsonl
  environment.json
  claims.json
  checksums.sha256
```

Absent stages use explicit `null` results and `NOT_RUN`; files are not invented
to make the package look complete. `environment.json` records OS, architecture,
runtime versions, camera identifiers without personal device names, compiler
version, git commit, and test commands. Exact results serialize symbolic
\(\pi\)-coefficients when available in addition to floats.

## 16. Implementation milestones and acceptance gates

### M1 -- theorem-backed digital admission

- implement interfaces, G0--G6, and stable certificates;
- verify exact q-star and tetrahedral examples;
- preserve the current evidence ladder and locality disclosures; and
- pass existing and new focused tests.

**Exit:** a target that passes Gauss--Bonnet but violates a Chow--Luo subset is
rejected with a reproducible minimal witness, while an admitted target can be
handed to the existing radius flow.

### M2 -- candidate synthesis and repairs

- stable Model CP solve and bounds;
- QV action compiler;
- guarded target projection as an explicit proposal;
- deterministic report/export/import; and
- at least three successful and three rejected representative targets.

**Exit:** every candidate states its L2 compilation and local runtime parts;
no optimizer failure is mislabeled a theorem.

### M3 -- refinement and robustness

- at least three nested compiler levels;
- atlas-compatible field names and four-level optional suite;
- uncertainty ensemble and conditioning;
- independent deterministic replay fixtures.

**Exit:** refinement and robustness reports reproduce from seeds and retain
finite-estimate labels.

### M4 -- fabrication package and passive experiment

- render and dimension-check all templates;
- perform scale, assembly, and intrinsic audits;
- validate camera calibration on references;
- collect randomized q=5/6/7 trials; and
- compare reconstructed embeddings to Model ES without uniqueness claims.

**Exit:** another operator can reproduce the passive kit from the package and
obtain the exact intrinsic defects; empirical 3-D outcomes include uncertainty
and all invalid trials.

### M5 -- HIL, bounded platform replay, and future instrumentation

- pass every injected fault in simulation;
- retain the bounded Darwin/Windows digest-and-focused-test comparison;
- issue new local records and a new comparison for any future vision fixture,
  larger ensemble, device, camera, or hardware surface;
- only then request approval for an active BOM; and
- if approved, calibrate one actuator channel before expanding.

**Exit:** no uncontrolled motion on startup, timeout, stale command, lost
camera state, or emergency stop; a content-addressed comparison records only
the parity surface it explicitly names.

## 17. Primary mathematical and experimental anchors

These sources establish the ingredients, not the novelty or completion of this
research program.

1. T. Regge, “General Relativity Without Coordinates,” *Il Nuovo Cimento* 19
   (1961), 558--571. Deficit-angle foundation for piecewise-flat curvature.
   [DOI](https://doi.org/10.1007/BF02733251) and
   [CERN record](https://cds.cern.ch/record/472394).
2. B. Chow and F. Luo, “Combinatorial Ricci Flows on Surfaces,” *Journal of
   Differential Geometry* 63 (2003), 97--129. Weighted circle-packing length
   law, curvature map, strict subset inequalities, rigidity, and flow results
   under their stated hypotheses.
   [Primary paper](https://sites.math.rutgers.edu/~fluo/mpapers/combinatorial%20Ricci%20flow%20in%20dimension%202.pdf).
3. A. I. Bobenko and B. A. Springborn, “Variational Principles for Circle
   Patterns and Koebe's Theorem,” *Transactions of the AMS* 356 (2004),
   659--689. Existence/uniqueness and variational construction for circle
   patterns, including surfaces with boundary under their own hypotheses.
   [arXiv](https://arxiv.org/abs/math/0203250).
4. J. Cheeger, W. Müller, and R. Schrader, “On the Curvature of Piecewise Flat
   Spaces,” *Communications in Mathematical Physics* 92 (1984), 405--454.
   Curvature-measure convergence under suitable nondegenerate approximation;
   this motivates, but does not replace, the refinement gates.
   [DOI](https://doi.org/10.1007/BF01210729) and
   [paper](https://www.cs.jhu.edu/~misha/Fall09/Cheeger84.pdf).
5. E. Grinspun, A. N. Hirani, M. Desbrun, and P. Schröder, “Discrete Shells,”
   SCA 2003, 62--67. A primary discrete-shell modeling anchor for the proposed
   extrinsic simulator.
   [DOI](https://doi.org/10.2312/SCA03/062-067) and
   [paper](https://www.geometry.caltech.edu/pubs/GHDS03.pdf).
6. Y. Klein, E. Efrati, and E. Sharon, “Shaping of Elastic Sheets by
   Prescription of Non-Euclidean Metrics,” *Science* 315 (2007), 1116--1120.
   Experimental evidence that prescribed local metric changes can drive
   global sheet shapes, while allowing multiple buckling/wrinkling responses.
   [DOI](https://doi.org/10.1126/science.1135994).
7. E. Efrati, E. Sharon, and R. Kupferman, “Elastic Theory of Unconstrained
   Non-Euclidean Plates,” *Journal of the Mechanics and Physics of Solids* 57
   (2009), 762--775. Continuum mechanics anchor for separating target metric,
   stretching, bending, and selected configuration.
   [DOI](https://doi.org/10.1016/j.jmps.2008.12.004) and
   [arXiv](https://arxiv.org/abs/0810.2411).
8. Z. Zhang, “A Flexible New Technique for Camera Calibration,” *IEEE TPAMI*
   22 (2000), 1330--1334. Planar-pattern camera calibration.
   [DOI](https://doi.org/10.1109/34.888718).
9. S. Garrido-Jurado, R. Muñoz-Salinas, F. J. Madrid-Cuevas, and M. J.
   Marín-Jiménez, “Automatic Generation and Detection of Highly Reliable
   Fiducial Markers under Occlusion,” *Pattern Recognition* 47 (2014),
   2280--2292. Fiducial detection and pose-estimation anchor.
   [DOI](https://doi.org/10.1016/j.patcog.2014.01.005).

## 18. Novelty boundary, blockers, and open questions

### What this workstream can contribute

- one typed, evidence-aware path from target to local program;
- exact obstruction witnesses beyond a total-curvature check for a carefully
  delimited circle-packing model;
- transparent separation of intrinsic, extrinsic, mechanical, and sensing
  feasibility;
- a passive q-star whose local program and global curvature budget are exact
  enough to audit by hand; and
- one report format spanning theorem instances, computation, fabrication,
  sensing, and HIL without mixing their evidentiary strength.

### What it must not claim

- that the Chow--Luo certificate applies to arbitrary edge metrics, arbitrary
  intersection angles, boundaries without the declared doubling argument, or
  elastic sheets;
- that a compatible metric has a unique embedding in \(\mathbb R^3\);
- that the proposed shell energy is a calibrated constitutive law;
- that cardstock trials validate hydrogel, biological growth, or metamaterial
  behavior;
- that three or four mesh levels prove a continuum limit;
- that absence of a numerical solution proves nonexistence; or
- that Windows camera/device instrumentation, physical robustness, or hardware
  results exist before their content-addressed artifacts and scoped comparison
  are produced.

### Known blockers and research decisions

1. **General boundary prescription:** symmetric doubling certifies a useful
   disk subclass, not every surface-with-boundary target. A broader exact
   boundary compiler should implement and test an appropriate boundary circle-
   pattern theorem rather than extrapolate the closed result.
2. **Subset scalability:** exhaustive Chow--Luo certification is exponential.
   Larger meshes require a verified separation oracle, branch-and-bound, or
   proof-producing optimization formulation. Until then, no found violation is
   informative, but no violation found is inconclusive.
3. **Combinatorial inverse design:** finding a triangulation with prescribed
   integer valences and fabrication constraints is a constrained topology
   problem. The q-star is solved; general multi-defect sheets remain research.
4. **Extrinsic nonuniqueness:** especially for negative curvature, hinge and
   boundary programming may be needed to select a repeatable global shape.
5. **Material calibration:** no stiffness, friction, fatigue, or actuator
   parameters have been measured. Model ES is therefore predictive only after
   calibration.
6. **Single-camera occlusion:** severe folds may require a second view. The
   first experiment should keep the geometry small and all target-critical
   markers visible.
7. **Dimension targets:** a two-dimensional sheet compiler is not a general
   dimension compiler. The universality atlas must own graph/fractal/diffusion
   targets until a common certified inverse theory exists.

The decisive success condition is modest but meaningful: the compiler must be
able to say **yes**, **no in this precisely declared model**, or **not yet
known**, give a checkable reason, and carry that distinction intact from a
mathematical target to a physical bench protocol.
