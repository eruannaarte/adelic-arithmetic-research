# Arithmetic Observability public companion package

This directory is a dependency-free, standalone version of the AO Lab for
publication beside the formal Arithmetic Observability Atlas.

## Files

- `index.html` — accessible standalone companion page and laboratory shell.
- `ao-lab.css` — responsive light/dark presentation styles.
- `ao-lab.js` — deterministic synthetic-model computation and SVG charts.
- `../../ARITHMETIC_OBSERVABILITY_PUBLIC_COMPANION.md` — the canonical public
  science-communication text.

The page uses no network requests, external fonts, analytics, or third-party
JavaScript.  The JavaScript is ordinary browser code and needs no build step.

## Publication contract

- Suggested route:
  `/number-geometry/arithmetic-observability-atlas/lab/`
- Suggested visible label: `Explore the AO Lab`
- Keep the existing formal Atlas page and add this as a companion, not a
  replacement.
- Display `Interactive illustration — synthetic declared model` above the
  controls.
- Preserve the distinction between proved statements, sampled diagnostics,
  and controlled physical analogy.
- Keep the control label `Pair cutoff (2ε)`: the displayed value is the
  distance between two noiseless readings, corresponding to two independent
  adversarial error balls of radius `ε`.
- Do not call the sampled separation envelope an energy spectrum or a formal
  certificate.

## Model provenance

The lab uses normalized four-level geometric factors on primes 2, 3, and 5 and
the explicit AO V schedule

```text
T = (245943/1000, 140531/500, 120104/125).
```

For each prime `p`, the compact coordinate `y_p` gives

```text
u_p = y_p/(1-y_p),
q_p(a) = u_p^a/(1+u_p+u_p^2+u_p^3),  a=0,1,2,3.
```

The laboratory evaluates

```text
H_y(t) = ∏_p ∑_{a=0}^3 q_p(a) exp(-i a t log p).
```

The heatmap minimizes reading distance over the hidden candidate `y_5` grid.
The envelope is the lower observed reading distance in bins of compact
`L∞` shape distance.  Both plots are finite-grid diagnostics.

## Local validation

From this directory:

```bash
python -m http.server 8765
```

Then open `http://127.0.0.1:8765/`.  Validate at desktop and narrow mobile
widths, change every slider, switch between one and three readings, and confirm
that the heatmap, envelope, statistics, tooltip, and explanatory status line
update without horizontal overflow.
