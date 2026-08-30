# Global Geometry Lab

This directory contains a dependency-free browser laboratory for the research
programme described in [`../../GLOBAL_GEOMETRY_LAB.md`](../../GLOBAL_GEOMETRY_LAB.md).

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

No package installation, build system, remote request, analytics, dynamic
import, or user-code evaluation is required.

## Evidence contract

The page distinguishes:

1. **Exact finite identities** — Betti numbers, Euler characteristic, and
   Gauss--Bonnet for a valid finite triangulation;
2. **finite numerical estimates** — eigenspectra, heat traces, dimension
   slopes, and local-flow trajectories;
3. **research targets** — continuum limits, universality, robustness, and
   recognition claims that the finite page can probe but cannot prove; and
4. **application analogies** — materials, tissue, networks, learned
   manifolds, swarms, and a relational-graph physics toy.

Finite agreement is not labeled continuum convergence or universality.  A
preset is not labeled an empirically adequate model of its application domain.

## Run locally

From the repository root:

```bash
python -m http.server 8000 --bind 127.0.0.1
```

Open:

```text
http://127.0.0.1:8000/website/global-geometry-lab/
```

## Run tests

```bash
node --test website/global-geometry-lab/test-global-geometry-core.js
```

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
