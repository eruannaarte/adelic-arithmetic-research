# Double-Pendulum Operational Atlas

## A nonlinear benchmark for Operational Information Geometry

## 1. Research question

Animations of a large grid of double pendulums often use the grid coordinates
to specify two initial angles. Each cell then evolves an independent dynamical
system. Bands and islands of similar colour can be visually striking, but the
image alone does not say what has become similar, whether that similarity is
stable, or whether the cells are physically synchronized.

This project turns that picture into a declared experimental object:

> Which finite observations distinguish initial conditions, parameters, or
> model hypotheses in a double pendulum; which distinctions survive
> preparation error, calibration nuisance, numerical uncertainty, and output
> noise; and which launches, sensors, and observation times should be selected
> under a finite experimental budget?

The atlas is intended as a nonlinear benchmark for the proof-producing OIG
protocol engine. It is not evidence for a fundamental physical geometry, an
infinite-time classification of the double pendulum, or synchronization
between uncoupled simulations.

---

## 2. Three claim tiers

The work is divided by what its evidence actually proves.

1. **Reproducible numerical atlas.** A declared ODE, finite horizon, grid,
   integrator, tolerance ladder, observation map, and thresholds produce a
   finite numerical portrait with energy and refinement diagnostics.
2. **Validated nonlinear enclosure.** Interval or otherwise outward-validated
   integration encloses trajectories, event times, and variational responses
   over declared point or cell inputs.
3. **End-to-end exact operational certificate.** Outward response, secant,
   tangent, and nuisance enclosures are passed to the existing exact OIG
   engines. Exact rational elimination and \(LDL^T\) tests then certify a
   finite-library design or robust separation claim for the physical model.

An exact algebraic certificate over *assumed* rational response boxes is useful
before Tier 2, but remains conditional. It becomes a Tier-3 pendulum result only
after a validated transfer proves that the nonlinear model lies in those boxes.

That composition is now complete at two sharply bounded targets at \(u=v=0\):
the two active scalar parameter protocols without nuisance, and the selected
five-output A+B mixture after profiling one shared local clock column. It
remains incomplete for preparation error, the other grouped/nuisance models,
parameter neighbourhoods, empirical model adequacy, and hardware calibration.

A Tier 1 result may discover a candidate for Tier 2 or Tier 3. It is not itself
an interval or physical theorem.

---

## 3. Declared mechanical model

The first model consists of two point masses on massless rigid rods in a
uniform gravitational field. Both angles are absolute and measured from the
downward vertical. The state convention is frozen as

\[
 z=(\theta_1,\theta_2,\omega_1,\omega_2).
 \tag{3.1}
\]

For positive masses and lengths, the angular mass matrix is

\[
 M(\theta)=
 \begin{pmatrix}
 (m_1+m_2)\ell_1^2 & m_2\ell_1\ell_2\cos(\theta_1-\theta_2)\\
 m_2\ell_1\ell_2\cos(\theta_1-\theta_2) & m_2\ell_2^2
 \end{pmatrix}.
 \tag{3.2}
\]

Its determinant is

\[
 \det M=m_2\ell_1^2\ell_2^2
 \left(m_1+m_2\sin^2(\theta_1-\theta_2)\right)>0,
 \tag{3.3}
\]

so solving the two-by-two mass system is nonsingular for every configuration.
The initial numerical benchmark is conservative and unforced. Damping,
forcing, coupling between different pendulums, and flexibility are different
model families and will never be introduced silently.

The initial atlas uses the two-dimensional slice

\[
 q=(\theta_1(0),\theta_2(0))\in\mathbb T^2,
 \qquad
 z_0(q)=(\theta_1(0),\theta_2(0),0,0).
 \tag{3.4}
\]

This is a slice of the four-dimensional phase space, not the whole state
space. Its cells are independent launches unless a later model explicitly
introduces coupling.

---

## 4. Topology and observations

The angle domain is a torus. The numerical grid is cell-centred and half-open,
so the equivalent endpoints \(-\pi\) and \(\pi\) are not duplicated. Opposite
grid edges are adjacent.

The default phase observation is seam-free:

\[
 \chi(z)=
 \left(
 \sin\theta_1,\cos\theta_1,
 \sin\theta_2,\cos\theta_2,
 \omega_1/s_\omega,\omega_2/s_\omega
 \right),
 \tag{4.1}
\]

where \(s_\omega>0\) is a declared output calibration. For protocol

\[
 P=(h,\{t_k\}_{k=1}^m,W,c),
 \tag{4.2}
\]

the observation map is

\[
 Y_P(q,p,\nu)
 =\operatorname{stack}_{k=1}^m
 h_k\!\left(\varphi_{t_k}^{p}(z_0(q,\nu))\right),
 \tag{4.3}
\]

with output-noise precision \(W\succ0\), cost \(c>0\), physical/model
parameters \(p\), and declared preparation or calibration nuisance \(\nu\).
Cartesian bob positions and velocities are alternative sensor maps. Every
atlas must name its map, horizon, cadence, metric, and nuisance semantics.

---

## 5. Four different geometries

Several attractive but incorrect identifications are avoided by keeping four
notions separate.

### 5.1 Finite-time dynamical regularity

Examples include a tangent-flow gain, finite-time Lyapunov exponent,
recurrence, or winding statistic. A sampled net excursion of \(2\pi\) is only
a descriptive event unless dense-output or interval event tracking proves
that no crossing was missed.

### 5.2 Operational coherence

A cell \(C\) is operationally coherent at radius \(\eta\) only when a uniform
bound proves

\[
 \operatorname{diam}_{W}Y_P(C)\le\eta.
 \tag{5.1}
\]

A grid-edge finite difference is a useful Tier 1 diagnostic, but it is not a
bound over the whole cell and not the largest tangent singular value.

### 5.3 Local observability

Where differentiable, the pullback information field is

\[
 G_P(q)=D_qY_P(q)^T W D_qY_P(q).
 \tag{5.2}
\]

Relative to a declared source metric \(S\succ0\),

\[
 \sqrt{\lambda_{\min}(G_P,S)}
 \quad\text{measures weakest local identifiability,}
 \qquad
 \sqrt{\lambda_{\max}(G_P,S)}
 \quad\text{measures strongest local output amplification.}
 \tag{5.3}
\]

Low amplification may indicate regular motion or merely a blind sensor. It is
not automatically desirable experimental information.

### 5.4 Synchronization

Synchronization is reserved for a declared phase-lock or frequency-lock
predicate, or for a model with actual coupling/shared forcing. Similar colours
from independent conservative trajectories mean only finite-resolution output
coherence under the chosen display.

---

## 6. Fibres, confusability, and islands

Exact observational fibres are level sets of \(Y_P\). Let \(\mathcal T_P(C)\)
denote the allowed output/nuisance tube *before* measurement noise is added.
Robust separation at equal measurement-noise radius \(\varepsilon\) requires

\[
 \operatorname{dist}_{W}
 \left(\mathcal T_P(C),\mathcal T_P(C')\right)>2\varepsilon.
 \tag{6.1}
\]

Failure to prove (6.1) is **undecided**, not proof of physical confusability.
Even actual pairwise confusability need not be transitive: \(A\) can be
confusable with \(B\), and \(B\) with \(C\), while \(A\) and \(C\) remain
separable. Consequently, connected components of thresholded cells are
display regions, not quotient classes or mutual-indistinguishability classes.

The current atlas primitives therefore use the deliberately limited phrase
**connected low-stretch, no-sampled-full-turn region** for a connected
component whose cells have low grid-edge feature stretch and no sampled
full-turn excursion. This does not prove libration: a trajectory can rotate
less than one turn within the horizon, or cross and return between samples.

---

## 7. Query-directed experimental design

An initial condition that the experimenter deliberately selects cannot also
be treated as the unknown source in the same design statement. Two OIG modes
are therefore separated.

### 7.1 Local state-recovery atlas

At a fixed launch, the unknown source is a small perturbation of the initial
state. Protocols choose sensors and observation times. The atlas maps local
response singular values and robust tangent bounds over the angle grid.

### 7.2 Parameter/model identification

The candidate protocol selects a launch, sensor set, and observation schedule.
The unknown source is an identifiable dimensionless parameter or finite model
hypothesis. A useful first parameter source is

\[
 u=\left(\delta\log(m_2/m_1),\delta\log(\ell_2/\ell_1)\right).
 \tag{7.1}
\]

Common mass scaling is exactly blind in the ideal unforced angle dynamics and
is retained as a falsification control. Gravity, length, and clock scaling can
also be confounded without external calibration.

For a candidate protocol \(i\), the local response and nuisance matrices are

\[
 H_i=\frac{\partial Y_i}{\partial u},
 \qquad
 B_i=\frac{\partial Y_i}{\partial\nu}.
 \tag{7.2}
\]

Validated entrywise enclosures for \(H_i\) can be consumed directly by
`EnclosedProtocol` and `design_enclosed_protocols`. The exact OIG engine then
chooses a cost-weighted finite mixture and proves a robust information floor
for every response inside the declared rational boxes. The outward
Picard--Taylor transfer now supplies this premise for the two active responses
at the nominal parameter point. Responses for the other five candidates and
all parameter-neighbourhood claims remain Tier-1 or conditional.

---

## 8. Nuisance semantics

The first design contract distinguishes:

- physical parameters or camera calibration shared across every launch;
- preparation error shared within one launch but independently re-fitted
  between launches;
- sensor gain or offset shared across all times from that sensor;
- temporally correlated measurement noise represented by the full precision
  matrix rather than counted as independent samples;
- numerical/model remainder carried as an outer response or output tube.

Correlation is part of the physics. Replacing a common coefficient by
independent coordinate boxes can destroy or invent apparent distinguishability.
The existing structured-nuisance zonotope interface preserves finite shared
coefficients, while the query engine already distinguishes globally shared
from independently refitted nuisance. A general group-incidence assembler is
a later engine target.

The present response-box design certificate and the structured/query nuisance
certificates are separate ledgers. They may be composed only after a fixed
nuisance projection or a new joint theorem has been validated for the same
uncertain response family; running both modules does not by itself certify
uncertain \(H\) and grouped nuisance simultaneously.

---

## 9. Numerical acceptance ledger

The Tier 1 simulator is accepted only with all declarations serialized and the
following controls exercised:

1. the downward equilibrium remains fixed;
2. the two small-angle normal frequencies match the analytic linearization;
3. energy drift is reported and bounded at accepted steps, midpoints, and
   observation times;
4. a tolerance and maximum-step refinement compares trajectories on the same
   output grid;
5. angle differences used for diagnostics respect the torus seam;
6. a deliberately loose solver fails the same materially meaningful accuracy
   gate that the production configuration passes;
7. grid side, half-cell shift, and cadence refinements are compared;
8. horizon is continued as a physical protocol coordinate, not required to
   preserve a finite-time classification;
9. initial energy is published so zero-velocity energy contours cannot be
   mistaken for an independent stability mechanism;
10. raw scalar fields and masks, not a colour palette, remain authoritative;
11. points whose convergence or enclosure gate fails are `unresolved`, never
    assigned zero uncertainty.

Energy conservation is necessary but insufficient: chaotic trajectory error
can grow while energy remains accurate. Refinement agreement is also empirical,
not an outward error proof.

---

## 10. Current executable foundation

The implementation now contains:

- `double_pendulum_dynamics.py`: declared mechanics, adaptive DOP853
  integration, energy audit, and same-grid state refinement;
- `oig_double_pendulum_atlas.py`: seam-free trajectory features, sampled turn
  excursions, grid-edge operational stretch, and toroidal regions;
- `oig_double_pendulum_lab.py`: an all-cell Tier-1 runner and strict
  internal-consistency verifier;
- `oig_double_pendulum_render.py`: an SVG rendering derived from the verified
  raw report;
- `double_pendulum_variational.py`: the analytic vector-field Jacobian, joint
  state/tangent integration, general source injection, and local OIG Grams;
- `oig_double_pendulum_variational_atlas.py`: a two-angle, RMS-matched
  weakest/strongest-gain atlas with coarse/fine tangent, response, Gram, and
  direct gain gates;
- `oig_double_pendulum_persistence.py`: resolution, half-cell-shift,
  threshold, cadence, horizon, and energy ledgers on a declared common torus
  comparison grid;
- `oig_double_pendulum_parameter_sensitivity.py`: analytic inhomogeneous
  sensitivities for the two active dimensionless parameter protocols, with
  multiscale finite-difference and physical-similarity audits;
- `oig_double_pendulum_protocol.py`: numerical parameter-response discovery,
  explicit rational box declaration, and a sealed exact conditional design;
- `oig_double_pendulum_validated_transfer.py`: outward Arb Picard--Taylor
  integration of the twelve-dimensional state/sensitivity system, strict
  active-box inclusion, and composition with the exact rational OIG child;
- `oig_double_pendulum_structured_nuisance.py`: clock, calibration, and
  per-launch preparation columns plus exact rank/confounding controls;
- `oig_double_pendulum_grouped_protocol.py`: launch-batched multi-output
  protocols, a complete denominator-12 budget-share search, and exact
  shared-nuisance query children for the selected rational point models;
- `DOUBLE_PENDULUM_GROUPED_NUISANCE_TRANSFER_THEOREM.md`: invariant response-
  level and augmented-Gram transfer theorems for uncertain query and clock
  derivatives;
- `oig_double_pendulum_grouped_validated_transfer.py`: outward validation of
  all five selected parameter/clock rows and exact rational interval
  certification of the clock-profiled floor;
- `DOUBLE_PENDULUM_GROUPED_VALIDATED_TRANSFER_AUDIT.md`: independent interval,
  alternate-partition, wrong-weight, nuisance-incidence, and false-floor
  attacks on the grouped Tier-3 certificate;
- focused mechanics, topology, variational, verifier, protocol, renderer, and
  committed-artifact tests.

The committed provisional Tier-1 portrait is
`artifacts/double_pendulum_operational_atlas_stage1.json`, with its derived SVG
beside it. The exact conditional protocol artifact is
`artifacts/double_pendulum_protocol_design_conditional.json`. The matched
persistence and variational reports are
`artifacts/double_pendulum_persistence_13x13_t4_tier1.json` and
`artifacts/double_pendulum_variational_atlas_13x13_t4_tier1.json`. The active
analytic response report is
`artifacts/double_pendulum_parameter_sensitivity_tier1.json`. The composed
validated-model certificate is
`artifacts/double_pendulum_physical_positive_floor.json`. The strict
nuisance-obstruction report is
`artifacts/double_pendulum_structured_physical_nuisance.json`. The constructive
grouped report is
`artifacts/double_pendulum_grouped_protocol_tier1.json`. Its composed Tier-3
physical certificate is
`artifacts/double_pendulum_grouped_physical_clock_floor.json`.

The atlas verifier reconstructs the serialized numerical contract, gates, raw
summaries, and masks, but deliberately reports that provenance, ODE-to-array
linkage, and physical flow enclosure are unverified. The protocol verifier
reconstructs the seven-candidate rational child without rerunning floating
numerics and deliberately reports that ODE membership for the full library is
unproved. Separately, the validated-transfer verifier recomputes the outward
ODE proof for the two active rows and the exact fixed-mixture child. The
structured-nuisance verifier reconstructs its local-column relations and exact
finite-linear children but explicitly does not replay or outwardly validate
the nuisance ODE derivatives. The grouped verifier reruns its Tier-1
state/sensitivity/clock calculations, share-grid search, and exact query
children, while keeping ODE enclosure and preparation-error flags false. The
grouped validated-transfer verifier then reruns all five outward ODE rows,
reconstructs the exact interval augmented Gram, and rechecks both rational
\(LDL^T\) floor certificates; its preparation and hardware/model flags remain
false.
The persistence verifier accepts the source numerical fields as Tier-1 input
and reconstructs their periodic comparison ledger; the variational verifier
reconstructs the serialized refinement, response/Gram, direct-gain,
finite-difference spot, unresolved-mask, and summary relations. Neither
verifier replays or outwardly encloses the ODE.

---

## 11. Current results

For the canonical equal-unit pendulum, the current portrait uses a
cell-centred \(13\times13\) angle grid, horizon \(T=4\), 81 observation times,
and nine equal-RMS phase samples. All 169 state-refinement comparisons pass.
The maximum scaled state discrepancy is
\(6.08645\times10^{-8}\) against a \(2\times10^{-7}\) gate, and the maximum
sampled scaled energy drift is \(5.99996\times10^{-10}\) against a
\(2\times10^{-9}\) gate.

At the diagnostic threshold \(\log s\le0.5\), seven cells are marked in five
toroidal components of sizes \((2,2,1,1,1)\). The joint-angle reflection audit
passes. This is a finite-resolution observation, not yet a spatially persistent
island theorem, and state refinement does not validate tangent matrices.

The atlas-matched persistence family surrounds this portrait by resolutions
\(N=9,13,17\), three half-cell shifts, 5/9/17/41/81 equal-RMS feature
schedules, thresholds, five initial-energy strata, and horizons \(T=2,4,6\).
The source-grid marked counts at the reference predicate are \(3/7/11\) over
the three resolutions, while the shifted \(N=13\) grids contain \(4,4,8\)
marked cells. Thus the marked area remains near four percent, but the
low-threshold scalar pattern is not yet shift-stable. Against the 81-sample
reference, the
threshold-\(0.5\) cadence Jaccard values are \(0.714,0.806,0.886,1\) for
5, 9, 17, and 41 samples; this is a declared-grid trend, not a quadrature
enclosure.
Horizon continuation changes the operational geometry and is reported without
a convergence pass/fail flag.

Initial energy is a major covariate: baseline log stretch has Pearson
correlation \(0.8314\) and Spearman correlation \(0.8948\) with the
zero-velocity initial energy. This supports reporting energy stratification
alongside the portrait; it does not identify a causal mechanism.

The two-angle variational atlas replaces grid-edge differences by the analytic
tangent response of exactly the same RMS feature. On the \(13\times13\),
\(T=4\) grid, 167 of 169 cells pass the declared state, tangent, weighted
response, Gram, weakest-gain, and strongest-gain refinement gates. The two
seam-adjacent cells \((0,12)\) and \((12,0)\) are explicitly unresolved and
their selected gains are `null`. Only four declared cells receive independent
centred finite-difference spot checks; this is not a claim that all 167
resolved cells were finite-difference validated.

For the two active design protocols, analytic inhomogeneous parameter
sensitivities now replace finite differences in the selected response
calculation:

\[
\begin{aligned}
R_{\mathrm{A},\theta_2,\tau=1}
  &=(0.0845025509351,-0.454351245129),\\
R_{\mathrm{B},\nu_1,\tau=5/4}
  &=(0.469054738020,0.00414012202747).
\end{aligned}
\]

The standard/refined analytic discrepancies are below
\(2.4\times10^{-15}\), and the smallest-step comparisons to independently
integrated centred differences are below \(7.4\times10^{-9}\). Physical
representatives related by the declared time and velocity scaling agree to
\(1.33\times10^{-15}\). These Tier-1 controls settle the parameter convention
and derivative formula; the separate validated-transfer lane supplies the
outward membership proof.

The first parameter-design library contains seven launch/sensor/time
candidates. The nominal-centre E-design assigns nonzero budget to two:

1. launch A \([4/5,-7/20,0,0]\), sensor \(\theta_2\), \(\tau=1\), budget
   share \(4589/10000\);
2. launch B \([-3/5,9/10,0,0]\), sensor
   \(\sqrt{\ell_1/g}\,\omega_1\), \(\tau=5/4\), budget share
   \(5411/10000\).

Within the seven declared rational centres, the certified nominal E-optimal
efficiency exceeds \(0.9989907\). For the chosen mixture, outward Arb
Picard--Taylor enclosures of both active response rows compose with the exact
response-box theorem to prove the declared-model floor

\[
\frac{195932905640268820789}{2500000000000000000000}
\approx 0.0783732.
\]

The default ODE enclosures have radii between \(3.36\times10^{-13}\) and
\(5.45\times10^{-11}\), and every entry retains more than \(0.00100998\) of
exact rational inclusion slack. That unused slack is an available budget for a
separately proved discrepancy bound; it is not itself proof of model or
calibration error. The result does not prove robust optimality over the boxes,
physical selection or efficiency for all seven candidates, a parameter-
neighbourhood theorem, empirical model adequacy, or hardware calibration.

The next structured-nuisance audit gives a sharp negative boundary. With only
the two active scalar observations, any nonzero unrestricted shared clock or
common-gain coefficient reduces the profiled source rank from two to one.
Exactly one nuisance-invariant query survives. A shared clock together with a
common gain generically spans both outputs, while independently refitted
initial-angle preparation errors or sensor-specific gains already span each
scalar output separately; in those cases no nonzero query survives. The exact
query and structured-nuisance engines certify these finite rational rank and
confounding statements. The nuisance columns themselves remain Tier-1
variational evaluations, not outward ODE enclosures.

The obstruction is nevertheless constructive rather than terminal. Batching
the original seven observations by exact launch creates three grouped
protocols with \(3\), \(2\), and \(2\) scalar outputs. Launch A alone is the
minimum \(m=3\) witness: after profiling one shared clock column, the declared
rational point model still has effective query rank two and an exact floor
lower bound \(9.78912\times10^{-6}\). A complete denominator-12 search over
the three group budget shares selects

\[
  (p_A,p_B,p_C)=\left(\frac23,\frac13,0\right),
\]

with conservative additive group costs \(7/2,9/4,5/2\). Its five stacked
outputs are profiled against one global clock only after assembly, and the
exact query child proves

\[
  \lambda_{\min}^{\mathrm{profiled}}>0.018026929453263358.
\]

As an optimistic dimensional stress test, one shared clock plus one shared
common gain across all channel types retains rank two using all seven outputs,
with a conditional point-model floor above \(0.00218401\). The share-grid
ordering is deterministic binary64 discovery, not an exact optimality theorem.
All three design statements assume exact preparation, and the search ordering
remains Tier 1. For the fixed primary A+B shares, however, outward Arb
Picard--Taylor integration now encloses every one of the five parameter rows
and its shared-clock derivative. The largest parameter-response half-width is
\(7.21765\times10^{-11}\), and the largest clock half-width is
\(3.1076\times10^{-11}\). Exact rational interval arithmetic gives

\[
  b^TWb>1.6380507069296194
\]

and a three-pivot interval \(LDL^T\) proof certifies uniformly over the five
Cartesian row boxes that

\[
  \lambda_{\min}^{\mathrm{profiled}}
  >\frac{180269}{10000000}=0.0180269.
\]

This is a Tier-3 theorem for the fixed local nonlinear model and one shared
clock derivative. It does not transfer the search optimality, bound launch
preparation error, cover finite clock-dilation amplitudes, or validate the
model and noise metric against hardware.

---

## 12. Research hypotheses

The central empirical hypothesis is not that chaotic regions are automatically
the best experiments. Instead:

> Raw response sensitivity may rise near chaotic or interface regions, while
> robust query information peaks at an intermediate finite-time stretching
> scale because the same dynamics amplifies preparation and model uncertainty.

This will be tested by displaying side by side:

1. weakest and strongest local response gains;
2. finite-time dynamical amplification;
3. nuisance-profiled or response-box-robust information floors;
4. the protocols selected by the exact finite-library design engine.

A null result is informative: it would demonstrate that visual regularity,
dynamical sensitivity, local observability, and robust experiment quality are
genuinely different geometries.

---

## 13. Reproduction

Install the repository dependencies, then run the focused suite:

```bash
python -m pip install -r requirements.txt
python -m unittest -v \
  test_double_pendulum_dynamics.py \
  test_double_pendulum_variational.py \
  test_oig_double_pendulum_atlas.py \
  test_oig_double_pendulum_lab.py \
  test_oig_double_pendulum_protocol.py \
  test_oig_double_pendulum_protocol_artifact.py \
  test_oig_double_pendulum_persistence.py \
  test_oig_double_pendulum_variational_atlas.py \
  test_oig_double_pendulum_parameter_sensitivity.py \
  test_oig_double_pendulum_validated_transfer.py \
  test_oig_double_pendulum_validated_transfer_audit.py \
  test_oig_double_pendulum_structured_nuisance.py \
  test_oig_double_pendulum_grouped_protocol.py \
  test_oig_double_pendulum_grouped_validated_transfer.py \
  test_oig_double_pendulum_grouped_validated_transfer_audit.py \
  test_oig_double_pendulum_render.py \
  test_double_pendulum_artifacts.py
```

Regenerate and verify the Tier-1 portrait:

```bash
python oig_double_pendulum_lab.py \
  --side 13 --duration 4 --observations 81 --feature-samples 9 \
  --log-stretch-threshold 0.5 \
  --output artifacts/double_pendulum_operational_atlas_stage1.json
python oig_double_pendulum_lab.py \
  --verify artifacts/double_pendulum_operational_atlas_stage1.json
python oig_double_pendulum_render.py \
  artifacts/double_pendulum_operational_atlas_stage1.json \
  artifacts/double_pendulum_operational_atlas_stage1.svg
```

Regenerate and verify the conditional protocol certificate:

```bash
python oig_double_pendulum_protocol.py \
  --output artifacts/double_pendulum_protocol_design_conditional.json
python oig_double_pendulum_protocol.py \
  --verify artifacts/double_pendulum_protocol_design_conditional.json
```

Regenerate the bounded smoke report and the atlas-matched persistence study:

```bash
python oig_double_pendulum_persistence.py \
  --output artifacts/double_pendulum_persistence_tier1.json
python oig_double_pendulum_persistence.py --research \
  --output artifacts/double_pendulum_persistence_13x13_t4_tier1.json
python oig_double_pendulum_persistence.py \
  --verify artifacts/double_pendulum_persistence_tier1.json
python oig_double_pendulum_persistence.py \
  --verify artifacts/double_pendulum_persistence_13x13_t4_tier1.json
```

Regenerate and verify the two-angle variational atlases:

```bash
python oig_double_pendulum_variational_atlas.py \
  --side 7 --duration 2 \
  --output artifacts/double_pendulum_variational_atlas_tier1.json
python oig_double_pendulum_variational_atlas.py \
  --side 13 --duration 4 \
  --output artifacts/double_pendulum_variational_atlas_13x13_t4_tier1.json
python oig_double_pendulum_variational_atlas.py \
  --verify artifacts/double_pendulum_variational_atlas_tier1.json
python oig_double_pendulum_variational_atlas.py \
  --verify artifacts/double_pendulum_variational_atlas_13x13_t4_tier1.json
```

Regenerate and recompute the active analytic parameter responses:

```bash
python oig_double_pendulum_parameter_sensitivity.py \
  --output artifacts/double_pendulum_parameter_sensitivity_tier1.json
python oig_double_pendulum_parameter_sensitivity.py \
  --verify artifacts/double_pendulum_parameter_sensitivity_tier1.json
```

Regenerate and strictly verify the composed validated-model certificate:

```bash
python oig_double_pendulum_validated_transfer.py \
  --physical-output artifacts/double_pendulum_physical_positive_floor.json
python oig_double_pendulum_validated_transfer.py \
  --verify-physical artifacts/double_pendulum_physical_positive_floor.json
```

Regenerate and verify the structured-nuisance obstruction report:

```bash
python oig_double_pendulum_structured_nuisance.py \
  --output artifacts/double_pendulum_structured_physical_nuisance.json
python oig_double_pendulum_structured_nuisance.py \
  --verify artifacts/double_pendulum_structured_physical_nuisance.json
```

Regenerate and strictly recompute the constructive grouped protocol report:

```bash
python oig_double_pendulum_grouped_protocol.py \
  --output artifacts/double_pendulum_grouped_protocol_tier1.json
python oig_double_pendulum_grouped_protocol.py \
  --verify artifacts/double_pendulum_grouped_protocol_tier1.json
```

Regenerate and strictly verify the grouped Tier-3 shared-clock certificate:

```bash
python oig_double_pendulum_grouped_validated_transfer.py \
  --output artifacts/double_pendulum_grouped_physical_clock_floor.json
python oig_double_pendulum_grouped_validated_transfer.py \
  --verify artifacts/double_pendulum_grouped_physical_clock_floor.json
```

---

## 14. Next research order

1. Add a separately bounded preparation layer or measured preparation
   channel. Unrestricted independent preparation refits erase scalar-output
   information, so this requires additional outputs or an external bound.
2. Extend outward validation to all seven scalar candidates and the remaining
   grouped rows before claiming physical finite-library selection or nominal-
   efficiency transfer.
3. Extend the persistence study from a thresholded scalar field to uncertainty-
   aware variational cells, while retaining horizon as a protocol coordinate.
4. Certify cell coherence and pairwise separation with the three honest
   outcomes `distinct`, `confusable by witness`, and `undecided`.
5. Build a sealed bundle whose verifier reconstructs contracts, metrics, raw
   hashes, nuisance incidence, response boxes, and exact OIG children.

The first end-to-end validated OIG-selected nonlinear model experiment is now
closed for the two active nominal responses. A constructive multi-output
design now preserves a positive floor after one shared clock nuisance, and its
fixed A+B mixture has an outward nonlinear Tier-3 transfer. The immediate proof
target is a scientifically declared preparation bound, followed by the larger
candidate-library transfer.
