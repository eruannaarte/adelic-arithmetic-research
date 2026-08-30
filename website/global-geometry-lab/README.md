# Global Geometry Lab

This directory contains two dependency-free browser laboratories.  Global
Geometry I implements the finite local-to-global engine described in
[`../../GLOBAL_GEOMETRY_LAB.md`](../../GLOBAL_GEOMETRY_LAB.md).  The separate
[`global-geometry-ii.html`](global-geometry-ii.html) interface develops the
observable-relative universality, recognition, inverse-design, and virtual
programmable-sheet programme documented in
[`../../GLOBAL_GEOMETRY_II_MANUSCRIPT.md`](../../GLOBAL_GEOMETRY_II_MANUSCRIPT.md).

The lab asks a single operational question across several declared application
analogies:

> How do finite-radius rules, compatibility conditions, interventions, and
> observation scale combine to produce global metric, curvature, topology, and
> dimension measurements?

## Files

- `index.html` — accessible page and laboratory shell.
- `global-geometry-lab.css` — responsive light/dark presentation.
- `global-geometry-core.js` — deterministic generators, local dynamics,
  topology, curvature, Laplacian, and dimension diagnostics for browser and
  Node.
- `global-geometry-lab.js` — controls, rendering, configuration import/export,
  and application adapters.
- `test-global-geometry-core.js` — executable mathematical and adversarial
  checks.
- `../../global_geometry_reproducibility_manifest.json` — machine-readable
  source identities, commands, scope labels, and expected verification gates.

Global Geometry II adds:

- `global-geometry-ii.html`, `global-geometry-ii-lab.css`, and
  `global-geometry-ii-lab.js` — six evidence-bounded interactive modes;
- `global-geometry-ii-core.js`, `global-geometry-ii-ensembles.js`, and
  `global-geometry-ii-atlas.js` — the exact metric/diffusion controls,
  anisotropy map, bounded disk families, and nonconfirmatory preview atlas;
- `global-geometry-ii-inverse.js` — exact finite admissions and obstruction
  reports for sphere, disk, annulus, and torus examples;
- `global-geometry-ii-sheet.js` — the q-star intrinsic model and
  observation-bound virtual HIL protocol;
- focused test/generator/reproduction scripts; and
- `../../global_geometry_ii_reproducibility_manifest.json` plus the
  fabrication-ready protocol and SVGs under
  `../../artifacts/global-geometry-ii/fabrication/`.

The later U2 evaluation publication adds the
[`../../GLOBAL_GEOMETRY_II_U2_EVALUATION_REPORT.md`](../../GLOBAL_GEOMETRY_II_U2_EVALUATION_REPORT.md),
[`evaluation-v2` index](../../artifacts/global-geometry-ii/u2/evaluation-v2/evaluation-index-v2.json),
[`release-v2` manifest](../../global_geometry_ii_reproducibility_manifest_v2.json),
and
[`release-v2` evidence index](../../artifacts/global-geometry-ii/release-index-v2.json).

No package installation, build system, remote request, analytics, dynamic
import, or user-code evaluation is required.

## Evidence contract

The page distinguishes:

1. **Exact finite identities** — Betti numbers, Euler characteristic, and
   Gauss--Bonnet for a valid finite triangulation;
2. **finite numerical estimates** — eigenspectra, heat traces, dimension
   slopes, and local-flow trajectories;
3. **scoped proved limits** — P8.1 graph-metric nonuniversality and the
   covariance-whitened finite-dimensional diffusion limits of P8.2 and P8.3,
   only under their declared hypotheses;
4. **research targets** — bounded-disk or object-level universality,
   path/operator limits, robustness beyond the proved P8.3 basin, and
   recognition-identifiability claims that the finite page can probe but does
   not prove; and
5. **application analogies** — materials, tissue, networks, learned
   manifolds, swarms, and a relational-graph physics toy.

Finite agreement is not labeled continuum convergence or universality.  A
preset is not labeled an empirically adequate model of its application domain.

### U2 evaluation checkpoint

The finite preview remains `NOT_EVALUATED`.  A distinct cross-platform
screening and strict-partial checkpoint is `UNRESOLVED`: screening v3 completed
3,840/3,840 records on each host, while exact raw cross-host comparison is
`FAIL`; strict Gate 1 is `PASS`, Gates 2--8 are `UNRESOLVED`, and exact strict
cross-host replication is `FAIL`.  The strict \(10^{-12}\)-rounded diagnostic
projection is `PASS` with decision authority `NONE`.  The full confirmatory
campaign, physical validation, and camera validation are all `NOT_RUN`.

The authoritative comparisons are the
[strict-partial comparison](../../artifacts/global-geometry-ii/u2/evaluation-v2/strict-cross-comparison-v1.json)
and
[screening-v3 comparison](../../artifacts/global-geometry-ii/u2/evaluation-v2/screening-v3-cross-comparison-v1.json).
Compressed macOS/Windows strict campaigns and screening streams are indexed as
non-authoritative convenience transports by the evaluation-v2 index.

## Run locally

From the repository root:

```bash
python -m http.server 8000 --bind 127.0.0.1
```

Open:

```text
http://127.0.0.1:8000/website/global-geometry-lab/
```

Global Geometry II is at:

```text
http://127.0.0.1:8000/website/global-geometry-lab/global-geometry-ii.html
```

## Run tests

```bash
node --test website/global-geometry-lab/test-global-geometry-core.js
node website/global-geometry-lab/reproduce-global-geometry-ii.js --verify
node website/global-geometry-lab/reproduce-global-geometry-ii-v2.js --verify --mode deep
```

The last command is the current release-v2 deep verifier.  It checks the
registered compact release surface and runs the platform-native evaluation
validators; it does not execute full confirmation or any physical experiment.

For the historical v1 surface, Windows verification is wrapped by
`reproduce-global-geometry-ii.ps1`.  The platform-local
[macOS v2](../../artifacts/global-geometry-ii/certificates/macos-local-v2.json)
and [Windows v1](../../artifacts/global-geometry-ii/certificates/windows-local-v1.json)
certificates remain single-run records and never claim cross-platform parity.
Only the separately addressed
[macOS / Windows comparison](../../artifacts/global-geometry-ii/certificates/macos-windows-comparison-v1.json)
may close that historical declared digest-and-test-surface gate.  It does not
certify release v2 and does not validate
bounded-disk universality, camera or hardware behavior, a physical sheet,
peer review, publication, or merge status.  The earlier `macos-local-v1.json`
is a historical development record and is not the designated comparison input.

The current enlarged surface uses the separately addressed
[release-v2 macOS / Windows comparison](../../artifacts/global-geometry-ii/certificates/macos-windows-comparison-v2.json).
That record compares only the v2 release and declared deep-test surface; it has
no U2 decision or physical-validation authority.

When transferring a tar archive from macOS, create it with
`COPYFILE_DISABLE=1` and reject any `._*` AppleDouble entry before Windows
extraction.

## Programmability

The browser exposes the pure core as `window.GlobalGeometryCore`; Node receives
the same API through `require("./global-geometry-core.js")`.

The advanced panel shows the normalized JSON configuration for the current
run.  Import accepts the core's closed schema and rejects unknown generators,
dynamics, nonfinite values, oversized states, and unknown fields; configuration
text is never evaluated as code.  Export records the normalized configuration,
deterministic replay identifier, finite state, current analysis, optional
paired-world comparison, and method/evidence labels.

Runtime rules are classified by locality:

- `L0`: radius-bounded state and fixed constants only;
- `L1`: local state plus a declared broadcast scalar, normalization, or target;
- `L2`: globally mediated optimization or eigensolve.

The implemented synchronous runtime rules are L0 on fixed adjacency.  The
inverse target field is globally normalized and obstruction-checked before the
run, and the eigensolve used to *measure* a run is L2 analysis.  Neither global
result is silently fed back into the L0 curvature-feedback update.

Volume, spectral, and walk dimension are separate finite-scale profiles.  The
chart aligns each on its own normalized logarithmic scale and reports the
native radius, heat time, or walk step at the selected position; those three
clocks are not silently identified.

## Manual validation

At desktop and narrow widths:

1. load every preset and confirm the evidence boundary changes with it;
2. run, pause, step, reset, and apply the disclosed intervention;
3. select vertices and confirm local data update without changing intrinsic
   observables;
4. move the observation scale and toggle all dimension series;
5. compare two seeds and confirm the result is labeled finite observable
   agreement rather than isometry or continuum universality;
6. import the displayed configuration and reject an unknown generator or a
   nonfinite parameter;
7. export a run and verify it includes configuration, state, analysis, replay
   identifier, and evidence labels;
8. navigate all controls with a keyboard at widths of 360, 736, and 1,024
   pixels; and
9. confirm there is no horizontal page overflow in light or dark appearance.

## Citation and reuse

The repository's [`CITATION.cff`](../../CITATION.cff) supplies citation
metadata. Software in this package is covered by the repository's Apache-2.0
license; original explanatory documentation is additionally available under
the terms in [`LICENSE-CONTENT.md`](../../LICENSE-CONTENT.md). Preserve the
evidence labels and scientific non-claims when adapting the laboratory.
