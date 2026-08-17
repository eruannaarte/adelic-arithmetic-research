# Double-Pendulum OIG Wind Tunnel: Website Manager Handoff

## Direct publishing package

- **Package status:** frozen, independently audited, and ready for public static
  deployment
- **Dispatch status:** direct Website Manager dispatch authorized by the user
- **Prepared:** 16 August 2026
- **Repository:**
  `https://github.com/eruannaarte/adelic-arithmetic-research`
- **Publishing branch:** `codex/oig-finite-transfer`
- **Publishing commit:** supplied in the direct task dispatch; deploy only that
  immutable commit or a reviewed descendant
- **Suggested route:**
  `/number-geometry/operational-information-geometry/double-pendulum-wind-tunnel/`
- **Reuse boundary:** the repository currently has no `LICENSE`; the user's
  publication authorization permits TGN to display this package but does not
  silently grant a third-party reuse license

This is the canonical Website Manager brief for publishing the complete
Double-Pendulum Operational Atlas research package and its proof-aware Ensemble
Calibration Chamber. Instructions added by the user in the Website Manager task
remain authoritative.

---

## Copy-ready assignment

Publish the **Double-Pendulum OIG Wind Tunnel · Ensemble Calibration Chamber**
as the public nonlinear benchmark for Operational Information Geometry. The
page should let a visitor freeze an OIG forecast, reveal independently
integrated numerical outcomes, and compare prediction with observation across
one launch, a finite ensemble, or a queued background laboratory.

The interface is not a decorative chaos animation. Its central public lesson
is that more trajectories can stabilize finite-sample descriptions, while a
longer time horizon can destroy the validity of a local response forecast. A
failed refinement gate must remain visibly unresolved.

Suggested navigation:

```text
OIG protocol engine | Double-Pendulum Operational Atlas | Explore the Wind Tunnel
```

Required above-the-fold scope labels:

```text
Interactive nonlinear benchmark · declared numerical model
Live and Refined evidence are not proofs
Not peer reviewed
```

## Canonical source order

Read these sources in order:

1. `DOUBLE_PENDULUM_WEBSITE_MANAGER_HANDOFF.md`
2. `DOUBLE_PENDULUM_OPERATIONAL_ATLAS.md`
3. `website/double-pendulum-oig-wind-tunnel/README.md`
4. `DOUBLE_PENDULUM_WIND_TUNNEL_AUDIT.md`
5. `DOUBLE_PENDULUM_ENSEMBLE_CALIBRATION_AUDIT.md`
6. `README.md`, section **Nonlinear OIG benchmark — Double-Pendulum
   Operational Atlas**

The theorem and Tier memos are authoritative whenever condensed public copy
would otherwise broaden a claim.

## Canonical static application

Publish these nine files together on one HTTPS origin:

```text
website/double-pendulum-oig-wind-tunnel/index.html
website/double-pendulum-oig-wind-tunnel/wind-tunnel.css
website/double-pendulum-oig-wind-tunnel/wind-tunnel-data.js
website/double-pendulum-oig-wind-tunnel/wind-tunnel-core.js
website/double-pendulum-oig-wind-tunnel/wind-tunnel.js
website/double-pendulum-oig-wind-tunnel/ensemble-worker.js
website/double-pendulum-oig-wind-tunnel/README.md
website/double-pendulum-oig-wind-tunnel/test-wind-tunnel-core.js
website/double-pendulum-oig-wind-tunnel/test-wind-tunnel-ensemble-adversarial.js
```

The production page loads only the first six. The README and two Node suites
belong in the public source/reproduction package.

The app has no package build, CDN, font, analytics, dynamic import, server API,
or remote request. All simulation happens in the visitor's browser. Serve it
over HTTP(S), not `file://`, because the cancellable background computation uses
the same-origin `ensemble-worker.js`. A Content Security Policy may remain
strict; it needs same-origin scripts and `worker-src 'self'`. No `unsafe-eval`
or network permission is required.

The application-relative CSS, JavaScript, and worker paths can be preserved at
any route. The existing links that leave the app directory (`../../...`) must
either resolve within TGN's publication tree or be rewritten to the matching
public paper/artifact or immutable GitHub URLs.

## Required public behavior

Preserve all of the following:

1. **Forecast before outcome.** The forecast identifier, numerical response,
   ensemble declaration, law, seed, and evidence scope freeze before hidden
   member draws are revealed.
2. **Legacy single trial.** `N=1` remains the detailed deterministic held-out
   preparation-boundary experiment. Ensemble-only noise/law controls remain
   visibly inactive.
3. **Interactive ensembles.** `N=1...50`, `T=1...30 s`, responsive
   representative/cloud rendering, per-member diagnostics, P05/P50/P95 spread,
   member-time coverage, whole-horizon survival, persistent exits, declared
   outliers, amplification, output-tube re-entry, and its full-state
   countermetric.
4. **Declared microscopic variation.** The realism dial visibly runs from
   `0 — mathematically ideal` to `100 — naturally noisy`. Exact synthetic
   sampling laws and supports for angle, velocity, log-parameter, clock, and
   sensor components remain disclosed. They are not physical population laws.
5. **Structured laws.** Preserve `off`, `linear`, `quadratic`, `sinusoidal`,
   `radial`, and `geometric` launch-angle laws with their frozen formula,
   amplitude, and direction. Do not add arbitrary expression evaluation.
6. **Background Laboratory.** Preserve `N=50...1000`, `T=1...30 s`, Cartesian
   N-by-T/law/amplitude/repeat studies, nested progress, authoritative
   cancellation, stale-result rejection, compact machine-readable export,
   research-preset confirmation, and the conservative 512 MiB export
   preflight. The interface must continue to say that computation uses the
   visitor's CPU.
7. **Fail-closed evidence.** Live, Refined, and Certified remain distinct.
   Any solver, energy, centre-trajectory, response, weakest-gain, or
   strongest-gain gate failure is unresolved rather than agreement.
8. **Accessible responsive layout.** Retain keyboard labels, semantic status
   text, desktop density, and zero horizontal overflow at narrow-phone width.

## Certified strip

The page's Certified status belongs only to the fixed artifact-backed protocol,
not to arbitrary slider trials.

Display exactly:

```text
Fixed A+B five-output mixture
physical parameters: log(m2/m1), log(l2/l1)
one shared local clock nuisance
exact launch preparation
information floor > 0.0180269
exact rational floor 180269/10000000
```

The separate fixed two-row/no-nuisance result may be shown only as
`> 0.0783731`; nearest rounding to `> 0.0783732` would overstate the strict
lower bound.

Certified promotion requires the exact six-source provenance set embedded in
`wind-tunnel-data.js`, with every source verifier passing. A missing, altered,
or partial set must keep the panel unverified.

## Scientific boundaries that must remain public

- The browser's “actual” side is an independently integrated outcome from the
  same declared equations, not an independent physical measurement.
- The live band is a first-order selected-sensor numerical forecast, not an
  outward enclosure.
- Coverage, survival, Wilson intervals, spread, and outlier counts are
  descriptive finite-ensemble statistics, not certified probabilities or
  calibrated physical-population claims.
- Selected-sensor re-entry is not attraction, state synchronization, or
  full-state convergence; the full-state distance is reported precisely to
  expose that distinction.
- Local information gains are not Lyapunov exponents.
- The committed atlas's small marked regions are not established persistent
  islands; resolution and half-cell shifts remain materially sensitive.
- The Tier-3 theorem does not prove arbitrary launch/sensor/time selection,
  finite preparation error, finite clock amplitude, hardware calibration,
  model adequacy, or robust optimality over all response boxes.
- The work is not peer reviewed.

## Large-laboratory public safety

The laboratory is intentionally client-side and bounded:

- large presets require confirmation;
- work runs in a dedicated cancellable worker;
- stale or partial jobs cannot promote results;
- progress exposes long work rather than freezing the page;
- compact export omits repeated arrays but strict replay reconstructs them;
- a conservative 512 MiB estimate rejects oversized designs; and
- the copy warns that the visitor's own CPU performs the calculation.

Frozen benchmark records:

```text
N=50, T=30:    0.570 s generation, 0.543 s strict replay,
               1,144,092-byte pretty export
N=1000, T=30: 10.494 s generation, 10.527 s strict replay,
               5,559,706-byte pretty export
N=1000, T=30 at 40 Hz: 6.14 MB pretty export, below the 8 MiB test gate
```

These are reference-machine measurements, not universal performance promises.

## Reproduction and acceptance gates

From the repository root:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -v
node --test website/double-pendulum-oig-wind-tunnel/test-wind-tunnel-core.js
node --test website/double-pendulum-oig-wind-tunnel/test-wind-tunnel-ensemble-adversarial.js
python -m unittest -v test_double_pendulum_wind_tunnel.py
python build_double_pendulum_wind_tunnel_data.py --verify-sources --check
```

The frozen focused release gates were:

```text
core Node suite:                 25/25 passed
adversarial/frontend Node suite: 32/32 passed
Python provenance suite:         12/12 passed
broader double-pendulum suite:    53/53 passed
desktop/mobile browser audit:     PASS
independent release audit:        PASS — no blockers
```

Before deployment, the Website Manager should additionally verify:

- the site serves all six runtime assets with successful HTTP status;
- the worker starts under the production Content Security Policy;
- `N=1`, a small `N>1` ensemble, cancellation, and export operate on the
  deployed origin;
- the exact six provenance records promote Certified and a deliberately
  removed record fails closed;
- mobile width has no horizontal overflow;
- all formal-paper/artifact links resolve to public immutable targets; and
- rollback can restore the prior route without deleting the research source.

## Package SHA-256 identities

```text
63a25d37b37a6b1f1e5107f99f04a56a982fee5d4e9359f4cc803c5380abaec6  README.md
d59a8d6dfea872a6a333de07d78805bdd548eb52cab79a88b3c715d6ad5abc75  index.html
6d70d5071f9b7ae13c30ea85a2a36a9317d64a7401204902f28709b7a26e13b6  wind-tunnel.css
a9754f20d58395acdac6074089ba9ea95b4076372a76f4f2b4f15849c2d9368a  wind-tunnel-data.js
85ef5bdadbcd7e69f0924e9e6b2e45759a17c2e57f0c4497054ade9b6ecd25ed  wind-tunnel-core.js
01da9e09d3213c26557f53819fc3df08d636c3d1e01977c70cbce71f51290413  wind-tunnel.js
672d9130c21fcf23799a4dd70cca6d46f24ad7355e1d72ea7f37021e93210ad6  ensemble-worker.js
11b60b6b58f5fd3e07c73a3ef0ee9682c421eec8dc025e01177abd2a64849f94  test-wind-tunnel-core.js
167778dc797d1f7ef6305c0eeee45e18514e469460911601c892e8caf4c93cb1  test-wind-tunnel-ensemble-adversarial.js
```

The certified artifact hashes embedded in `wind-tunnel-data.js` are
authoritative for the six-source provenance panel. At dispatch they include:

```text
4f7ea64c85525449144415201faa7f2a11fa7b00d6548709f6e052852ba30b7c  grouped clock floor
5ea11882549d4b407ad1e94a8f42fa84a18806a06329b191e57f186ba7468ea7  grouped library
acfaeecc614ce5c7d8b912fabf97f5739789ea2ff58b34ce34791cdada8e2134  persistence
a874f664ac5565336b9d945181ac2ab3836ba530d8c3937647721c87f1849aed  state atlas
176b836ed003ef48959e73e74f57d8ec615d48dd4f0983e92e5b118f85884611  two-row floor
629c27a70b6686864cd03a0658893b21f6f5be6fb91297ae6b374bfe77b7ab8d  variational atlas
```

## Deployment and rollback rule

Deploy only after the Website Manager's ordinary preview, immutable-release,
link, CSP, desktop/mobile, and rollback gates pass. Preserve the previous route
until the new page completes production validation. If any runtime asset,
worker, provenance record, or scientific-scope label fails, keep the new route
unpublished or revert atomically to the prior site release.
