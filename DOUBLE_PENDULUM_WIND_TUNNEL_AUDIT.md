# Double-Pendulum OIG Wind Tunnel: numerical and claim audit

## Verdict

The browser core implements the declared point-mass, massless-rod double
pendulum consistently with `double_pendulum_dynamics.py`.  The hanging
equilibrium, rigid-rod geometry, energy identity, RK4/adaptive-solver agreement,
finite-difference response convergence, response-Gram calculation, and active
recommendation search are covered by executable Node tests.

The live and refined paths are useful numerical evidence.  They are not an
outward enclosure or a certificate.  The certified status in the interface may
only be attached to the separate, fixed A+B five-output artifact after its
committed verifiers pass.

## Exact interpretation of the three paths

### Live forecast

`forecastExperiment` freezes a centre trajectory computed with fixed-step RK4.
It differentiates all six displayed sensors with respect to the two initial
angle coordinates by centred finite differences.  Its response Gram is

\[
  G = \frac{1}{N}\sum_{k=0}^{N-1} r_k r_k^\mathsf{T},
\]

for the currently selected scalar sensor.  The displayed weakest and strongest
gains are the square roots of the two eigenvalues of this Gram.

The selected-sensor response is recomputed with centred perturbations at
finite-difference scales `h` and `h/2`.  The Refined gate uses the maximum of
the response-field relative RMS discrepancy and the relative shifts in the
weakest and strongest gains.  The default tolerance is five percent.  This is
a convergence diagnostic, not an outward derivative enclosure.  In
particular, the energetic launch `[1.95,-1.15,0.35,-0.2]` at `T=30` fails this
gate by a wide margin and is retained as a negative regression.

The uncertainty-band radius

\[
  \rho\,\lVert r_k\rVert_2 + \eta
\]

is a first-order local prediction for an Euclidean preparation disk in
`(theta1, theta2)`, plus a declared scalar readout allowance.  It does not bound
initial angular-velocity error, parameter error, nonlinear Taylor remainder,
model discrepancy, or hardware error.  It is therefore a **linearized live
tube**, never a certified enclosure.

### Refined comparison

`runIndependentOutcome` chooses a held-out direction on the boundary of that
two-angle disk and evolves it with an adaptive Dormand--Prince 5(4) integrator.
It also adaptively reintegrates the unperturbed centre.  This is independent
integration logic, but it deliberately shares the same JavaScript right-hand
side and declared mechanical model.  The result is an independently integrated
simulation outcome, not independent model truth and not a physical
measurement.

No random measurement noise is injected into the outcome.  `noiseRadius` is a
comparison allowance.  Tube coverage is the observed fraction for one held-out
direction and must not be described as a coverage probability or a universal
guarantee.  The `confusable`/`separated` classification concerns only the final
sensor sample and uses a two-radius worst-case separation convention; it is not
a whole-trajectory classification.

The reported energy drift uses `max(1, abs(initialEnergy))` as its scale.  The
single-outcome Refined status requires this finite drift to be no larger than
the serialized `energyDriftTolerance` (default `1e-7`), in addition to both
baseline and response-refinement gates.  This remains a browser numerical
diagnostic and is not interchangeable with the separately declared energy
gates in the research artifacts.

### Certified comparison

The live two-coordinate initial-state Gram is distinct from the certified
physical-parameter OIG theorem.  The latter concerns the source coordinates
`u = log(m2/m1)` and `v = log(l2/l1)`, the fixed grouped A+B five-output
mixture, exact launch preparation, a local unrestricted shared clock column,
and the declared dimensionless model at `u = v = 0`.  Its outward/exact floor
is `180269/10000000`.  It does not certify arbitrary slider settings, the live
tube, the active recommendation, hardware, model adequacy, preparation error,
finite clock amplitude, a parameter neighbourhood, selection optimality, or
efficiency.

## Active-design semantics

The recommender enumerates a sampled sensor/time lattice and adds one rank-one
row, weighted by `1/N`, to the current live Gram.  It maximizes the resulting
smallest Gram eigenvalue.  The core exposes both quantities explicitly:

- `informationFloor` is the smallest eigenvalue;
- `weakestGain` is its square root.

This is an exploratory, local initial-angle recommendation.  It has no cost,
nuisance, uncertainty, or robust-minimax profiling and must not be presented as
the certified protocol engine selecting the globally optimal next physical
experiment.

## Claim guardrails for the interface

Safe labels include “frozen numerical forecast,” “linearized uncertainty
tube,” “held-out adaptive simulation,” “empirical tube coverage,” “endpoint
confusability,” “local initial-angle response,” and “certified fixed A+B
artifact.”

Unsafe labels include “exact prediction” for the live forecast, “proved tube,”
“independent physical truth,” “coverage probability,” “Lyapunov exponent,”
“stability island,” “synchronization,” or any suggestion that the certified
`0.0180269` floor applies to the interactive initial conditions.

## Reproduction check

Run:

```sh
node --test website/double-pendulum-oig-wind-tunnel/test-wind-tunnel-core.js
```

The suite checks:

1. equilibrium and rod geometry;
2. the energy directional identity;
3. fixed/adaptive solver agreement and energy drift;
4. Gram eigenvalues, gains, and orthogonal directions;
5. finite-difference response and weakest/strongest-gain refinement at `h`
   versus `h/2`, including a long-horizon negative control;
6. declared perturbation radius, local amplification agreement, empirical tube
   coverage, and non-certificate method labels;
7. exhaustive agreement with the active recommendation objective; and
8. rejection of invalid time grids, steps, tolerances, finite-difference
   scales, energy gates, and uncertainty radii.

## Deterministic ensemble extension

The ensemble API implements

\[
q_i=q_0+r\,\xi_i+\alpha f(s_i)v
\]

in the two-initial-angle subspace. Here r and alpha are resolved in radians,
s_i is -1+2i/(N-1) for N>1 and zero for N=1, and v is a serialized unit
direction. The safe bounded laws are:

- off: f(s)=0;
- linear: f(s)=s;
- quadratic: f(s)=2s^2-1;
- sinusoidal: f(s)=sin(pi s);
- radial: f(s)=2|s|-1;
- geometric: f(s)=sign(s) expm1(k|s|)/expm1(k).

Every member, component, sensor sample, and laboratory repeat has an
independently derived seed. Results therefore do not depend on worker batch
size, cancellation/restart, rendering selection, or scheduling. The frozen
declaration publishes known structured offsets and commitments; the outcome
reveals exact angle, angular-velocity, log-parameter, fractional-clock, and
sensor draws.

Bounded angle draws lie in a hard Euclidean disk. Probabilistic angle draws
have independent normal coordinates. Angular-velocity draws are in radians per
second. Positive m1, m2, l1, l2, and g heterogeneity is applied through their
five log coordinates. Fractional clock draws map nominal time to
(1+clockFraction)t; probabilistic clock fractions use a safe tanh transform.
Sensor draws use the normalized units of the selected sensor.

The declaration serializes the exact sampling law and support for every one of
these components.  Bounded angle and velocity vectors are uniform by area on
their two-dimensional disks.  Bounded log-parameter, clock, and sensor draws
are componentwise uniform on their stated intervals.  Probabilistic angle,
velocity, log-parameter, and sensor coordinates are independent centred
normals at their stated scales; the probabilistic clock is explicitly
`tanh(scale*z)` for a standard-normal `z`.  Zero-scale components are declared
as deterministic singleton supports.  These law/support strings are canonical
declaration fields and are rejected if altered even with a recomputed checksum.
The compatibility `N=1` path is separately and truthfully declared as a
deterministic held-out boundary direction, not as a uniform-disk draw; the
declaration distinguishes the requested distribution from this authoritative
actual distribution.

The predicted centre uses only the known structured offset. Hidden angle
uncertainty and additive sensor noise enter the linearized prediction band.
For bounded draws the radius is

\[
r\|g(t)\|+\eta.
\]

For independent normal draws it is

\[
z\sqrt{r^2\|g(t)\|^2+\eta^2}.
\]

Velocity, parameter, and clock draws alter every generated outcome but remain
explicitly unpropagated stressors. Their coverage loss is evidence against the
narrow prediction, not something hidden by widening the tube after observing
the result.

Persistent exit means the first run of a declared number of consecutive
outside samples (three by default); later re-entry does not erase the event.
The survival curve uses first exit. Projected reconvergence requires an exit
from and later re-entry into that member's declared scalar output tube; it is
never state synchronization. Percentiles use Type-7 interpolation, and
covariance uses population denominator N over resolved members. A Wilson
interval appears only for a nonzero iid probabilistic declaration and targets
whole-horizon no-exit member survival.

For every member, the export reports a selected-sensor endpoint distance from
the frozen member-specific structured centre.  Bounded declarations use an
explicit equal-noise two-radius confusable/separated cutoff; probabilistic
sensor declarations remain unclassified.  Terminal representatives use a
serialized Tukey 1.5-IQR scalar-output rule.  At every output-tube re-entry the
core also reports a descriptive full-state distance from the independently
integrated baseline, using principal wrapped angle differences and angular
velocities scaled by `sqrt(l1/g)`.  No threshold for state attraction is
declared.  Large studies omit four-component trajectories but retain terminal
state, terminal sensor, sample count, extrema, RMS, and series digests for each
individual outcome.  Their laboratory-specific projection also removes
repeated nominal/member time arrays, per-sample sensor-noise values, and inside
masks.  It retains seeds, commitments, exact non-time draw coordinates,
sensor-noise summary/digest, coverage counts, exit indices/times,
amplification, endpoint class, full-state re-entry/terminal scalars, and gate
status.  Strict verification regenerates every omitted deterministic sequence
and trajectory before accepting the projection.

Each declaration commits the frozen forecast configuration, times, baseline
sensor series, initial-angle gradients, tube, information matrix, and active
recommendation. Runtime validation binds those values, the source coordinates,
law formulas, units, q0, and canonical members together. Result and laboratory
IDs cover their complete public scientific payloads. The strict exported
verifiers do not trust a self-recomputed checksum: they deterministically
replay the frozen forecast, adaptive comparison baseline, every member outcome,
audit, compact record, and aggregate summary. This same-code replay rejects
self-recommitted alterations of retained series, compact statistics, exit
events, survival, covariance, or comparison baselines. It is still not an
outward enclosure, an externally anchored signature, a physical provenance
proof, or independent model validation.

The worker accepts run-ensemble, run-laboratory, and cancel, echoes both
channel and run ID, yields between member batches, and suppresses stale
results. Laboratory studies natively cross ensemble sizes, horizons, laws,
amplitudes, and repeat seeds while retaining the base observation cadence.  A
single large job emits nested member-level progress rather than remaining at
zero until completion.  A conservative preflight estimates compact-export
bytes from run, member, and shared time-sample counts and rejects designs above
512 MiB.

### Performance record

Measured on the local Node 22.22.2 Darwin/arm64 runtime.  `Run` is study
generation; `Replay verify` repeats the forecast, baseline, and member solves
and validates all cross-fields:

| Case | Declaration | Result | Pretty JSON | Run | Replay verify |
| --- | --- | --- | ---: | ---: | ---: |
| Foreground long horizon | N=50, T=30, 601 samples, bounded angle scale 0.001 rad, linear structured alpha 0.002 rad, no extra realism | coverage 0.9955074875, 50 resolved, study `d3468d6e`, compact result `83604cb7` | 1,144,092 B | 0.570 s | 0.543 s |
| Research lab | N=1000, T=30, 601 samples, normal angle scale 0.001 rad, sinusoidal alpha 0.002 rad; velocity 0.001 rad/s, parameter-log 0.0001, clock 0.0001, sensor 0.0002 | coverage 0.8558801997, 1000 resolved, study `83ef2637`, compact result `71ed0f54` | 5,559,706 B | 10.494 s | 10.527 s |

The dedicated 40 Hz size regression uses N=1000, T=30, and 1,201 nominal
samples.  Its compact encoding is about 3.08 MB and its indented export is
6,140,966 bytes, below the executable 8 MiB pretty-export gate and far below
the pre-compaction 67,027,436-byte hostile-audit result.

These are reproducibility measurements, not universal performance guarantees.
