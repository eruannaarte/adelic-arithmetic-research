# Double-Pendulum OIG Ensemble Calibration Chamber

This dependency-free browser laboratory puts a declared double-pendulum world
beside forecasts made by Operational Information Geometry (OIG). It is a
falsifiable numerical experiment, not a decorative animation and not a claim
of physical truth.

The original single-launch Wind Tunnel remains intact at `N = 1`: it uses one
deterministic held-out direction on the declared preparation-radius boundary,
the top-level readout-noise allowance, no structured law, and no ensemble
realism components. The realism, sampled-distribution, seed, and structured-law
controls visibly remain inactive until `N > 1`. Increasing `N` activates a
reproducible finite ensemble; the Background Laboratory runs larger,
unanimated `N`-by-`T` studies.

## What happens when Run is pressed

The interface performs the operations in this order:

1. construct the centre trajectory and its two initial-angle response field,
   then repeat the selected-sensor response at half the finite-difference scale;
2. freeze the forecast, ensemble declaration, seed, structured law, and a
   visible forecast identifier;
3. reveal no member-specific random draw until after that freeze;
4. evolve every declared member with an adaptive outcome integrator;
5. compare those outcomes with the frozen first-order prediction;
6. report finite-sample coverage, exits, spread, amplification, numerical
   gates, and unresolved members.

The forecast uses fixed-step RK4. Outcomes use adaptive Dormand--Prince 5(4).
Those are independent integration paths, but both use the same declared
double-pendulum equations. The “actual” side is therefore a held-out numerical
model outcome, not an independent physical measurement.

## Ensemble declaration

Every member is generated from the frozen decomposition

\[
q_i=q_0+\sigma\xi_i+\alpha f(s_i)v.
\]

The terms are kept separate:

- `q0` is the selected centre launch on the two-initial-angle source slice.
- `sigma xi_i` is the seeded microscopic preparation component.
- `alpha f(s_i) v` is a disclosed structured perturbation with an independently
  selected amplitude and direction.
- velocity, log-parameter, clock-dilation, and selected-sensor components form
  additional disclosed realism stressors.

The realism dial visibly ranges from **0 — mathematically ideal** to **100 —
naturally noisy**. Opening **Disclose the actual uncertainty components** shows
each numerical scale and unit together with the exact `samplingLaw` and
`support` serialized by the core declaration. In bounded mode the support is a
declared bounded set such as a disk or interval; in sampled-distribution mode
the law names the seeded distribution and the support says when it is
unbounded or transformed. A zero scale serializes an off/point-mass-at-zero
law and produces exact zero draws; floating-point roundoff is never used as an
experimental perturbation. These laws describe the synthetic numerical
ensemble, not a calibrated physical population.

Supported safe structured laws are `off`, `linear`, `quadratic`, `sinusoidal`,
`radial`, and `geometric`. Their direction can be OIG's weakest local direction,
its strongest local direction, or a bounded custom angle. No expression is
evaluated as code. The structured layer remains active even when stochastic
realism is zero.

Member and component seeds are derived from the master seed and member index.
The same declaration is invariant to chunk boundaries, resumption, and worker
scheduling order. Exports contain the declaration, revealed draws, member
audits, aggregate summaries, and integrity identifiers. These identifiers
detect accidental or tested structural tampering; they are not signatures and
do not authenticate provenance against a malicious author.

## What the ensemble statistics mean

The page distinguishes these quantities:

- **member-time coverage** is the fraction of all resolved member/time samples
  inside the frozen selected-sensor tube;
- **whole-horizon survival** is the fraction of resolved members with no
  sampled tube exit;
- **persistent exit** begins at the first run of at least three consecutive
  outside samples, even if the member later returns;
- **projected reconvergence** means a selected-sensor tube exit followed by a
  later return; the chamber reports the declared wrapped-angle/scaled-velocity
  full-state distance at that return precisely to show why this is not
  full-state convergence, attraction, or synchronization;
- **P05/P50/P95 bands** are descriptive finite-ensemble percentiles;
- **terminal outliers** use the frozen Tukey 1.5-IQR rule and retain the member
  identifiers used for representative traces;
- **amplification** compares observed selected-sensor separation with the
  frozen initial-angle linearization;
- **unresolved** means a declared energy, refinement, or solver gate failed.

Bounded mode is a finite deterministic design. Seeded-distribution mode is a
reproducible numerical sample from its disclosed distribution. A Wilson-style
95% interval is shown only when the declaration contains a nonzero eligible
iid probabilistic component with no structured law. It belongs specifically
to the Bernoulli event “whole-horizon member survival.” It remains an empirical
descriptive interval, not a certified probability or a statement about a
physical population.

The first-order live band propagates initial-angle response and selected-sensor
allowance. Velocity, parameter, and clock stressors alter outcomes but are
explicitly not propagated by that band. Their failures are informative stress
tests, not violations of a theorem that never covered them.

## Visualization policy

- `N = 1` retains the detailed perspective pendulum and held-out path.
- small ensembles show translucent members and individual traces;
- medium ensembles emphasize representatives and the cloud;
- large interactive ensembles show a representative subset, percentile
  ribbons, outliers, survival, and spread rather than fifty detailed windows.

The numerical result is authoritative; the animation is a human-readable view
of that record.

## Horizon versus ensemble size

Time horizon `T` is a protocol variable, not an accuracy setting. A longer run
can reveal stronger nonlinear amplification and make a local first-order
forecast worse. The chamber compares the selected-sensor response computed at
finite-difference scales `h` and `h/2`; if that response, its weakest gain, or
its strongest gain moves by more than the declared tolerance, the result stays
Live/unresolved instead of being promoted to Refined. Increasing `N` at fixed
`T` can stabilize a finite-sample estimate; increasing `T` does not necessarily
improve any forecast.

Use the Background Laboratory to keep those questions separate:

- compare `N` at fixed `T` to study finite-sample stabilization;
- compare `T` at fixed `N` to study horizon-dependent forecast survival;
- cross declared laws, amplitudes, and independently derived repeat seeds.

The laboratory accepts `N = 50…1000` and `T = 1…30 s`, reports progress, can
be cancelled without promoting partial work, and exports a machine-readable
study. Its workers yield between chunks; stale or superseded results cannot
update the active interface. The research-scale preset asks for confirmation
before beginning a large study. Laboratory members use a compact projection:
individual seeds, draw summaries, terminal outcomes, coverage/exit metrics,
and gate decisions remain, while repeated time grids, noise arrays, inside
masks, and trajectories are regenerated only during strict replay. A
conservative preflight rejects designs whose compact export is estimated above
512 MiB; the executable `N=1000`, `T=30`, 1,201-sample regression is about
3.08 MB as compact JSON and 6.14 MB as the indented browser export.

## Evidence ladder

- **Live** is an immediate first-order numerical forecast.
- **Refined** means independent adaptive integration, centre-trajectory
  agreement, response/gain refinement, energy, and solver gates all passed.
- **Certified** refers only to committed theorem artifacts whose source
  verifiers and hashes passed.

The certified strip concerns a fixed five-output A+B experiment in the
physical-parameter coordinates `log(m2/m1)` and `log(l2/l1)`, with one shared
local clock nuisance and exact launch preparation. Its information floor is
strictly greater than `180269/10000000`.

That theorem does **not** certify arbitrary slider settings, ensemble laws,
preparation error, long horizons, the browser tube, active recommendations,
hardware, or empirical model adequacy. The certificate panel starts neutral
and is promoted only when all six committed provenance records verify.

## Run locally

From the repository root:

```bash
python -m http.server 8000 --bind 127.0.0.1
```

Open:

```text
http://127.0.0.1:8000/website/double-pendulum-oig-wind-tunnel/
```

The page uses no package installation, build tool, CDN, WebGL library, remote
request, or dynamic import. The worker imports only the committed local core.

## Rebuild the certified-artifact bridge

```bash
python build_double_pendulum_wind_tunnel_data.py --verify-sources
python build_double_pendulum_wind_tunnel_data.py --verify-sources --check
```

The first command replays every source-artifact verifier, hashes the six
committed inputs, and writes `wind-tunnel-data.js`. The second fails when the
browser bundle is stale.

## Tests

```bash
node website/double-pendulum-oig-wind-tunnel/test-wind-tunnel-core.js
node website/double-pendulum-oig-wind-tunnel/test-wind-tunnel-ensemble-adversarial.js
python -m unittest -v test_double_pendulum_wind_tunnel.py
```

The suites cover mechanics, two independent integrators, OIG response and gain
half-step refinement,
all structured laws, deterministic seeds and chunk invariance, bounded versus
sampled semantics, first and persistent exits, survival, percentiles,
covariance, projected-output re-entry versus full-state separation, declared
outlier identities, N=1 compatibility, worker
cancellation, stale-message rejection, local-only dependencies, exported
record integrity, and certified-scope boundaries.

## Scientific boundary

The toroidal atlas remains a finite-time, finite-grid diagnostic on the
zero-velocity initial-angle slice. Its small marked regions are not established
persistent islands: the committed persistence study shows material sensitivity
to grid resolution and half-cell shifts. Local gains are not Lyapunov
exponents, connected threshold regions are not indistinguishability classes,
and a projected sensor return is not state synchronization.
