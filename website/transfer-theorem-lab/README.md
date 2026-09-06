# Transfer Theorem Lab

A standalone, responsive public companion to **Certified query recovery under
structured uncertainty**. Open `index.html` directly or serve this directory:

```sh
python -m http.server 8765 --directory website/transfer-theorem-lab
```

The lab uses ordinary JavaScript, CSS and SVG, with no build, external runtime,
fonts, analytics, storage or background network requests. Proof and release
links intentionally navigate to public evidence when followed.

The guide has three interactive views: an exact elementary answer set; spatial
containment in published uncertainty boxes; and a complete arithmetic error
budget with verified preset inheritance. It connects all five original paths
and nine research packages. `evidence.json` is the portable evidence index;
`evidence.js` embeds the same data so direct-file use needs no fetch request.

## Reuse and share

Use **Copy scenario link** to encode control state in the URL fragment. For
offline sharing, send the lab ZIP and the downloaded scenario JSON. Import
validates a closed versioned schema; it does not load code, data URLs or external
resources. File URL links point to the sender's folder location, so the
scenario file is the portable offline form. The clipboard has a visible manual
copy fallback when browser permission or context prevents writing. Scenario
export also exposes the exact JSON as a manual copy fallback.

Suggested website routes:

- Article: `/number-geometry/certified-query-recovery/`
- Lab: `/number-geometry/certified-query-recovery/lab/`
- Link label: **Explore the Transfer Theorem Lab**

Copy all seven serving files together: `index.html`, `transfer.css`, `core.js`,
`app.js`, `evidence.js`, `evidence.json`, and `lab-manifest.json`. The remaining
files are documentation and tests. The website's own discovery manifest may
reference `lab-manifest.json`. No active WebMCP or server computation is added.

## Mathematical display contract

The toy assumes either integer x∈{0,1,2,3,4} or real x∈[0,4], with unrestricted
offsets and bounded sensor errors. Membership uses exact integer hundredths.
It is an answer set for the displayed observation, not a uniform minimax noise
threshold. The compact transfer statement includes positive Gram comparison
constants and distinct unknown parameters in competing explanations.

Research status comes from saved, separately checked contracts. The browser
does not run interval matrices or prove new arbitrary slider settings. Spatial
percentage bounds round upward. Arithmetic plots use rounded estimates and
are labelled accordingly. Future data require their own actual-matrix residual
check and justified model membership. Source norms, complex-modulus coefficient
error, shared affine clocks, complete tails and separate mismatch are explicit.

## Verification

```sh
node --test website/transfer-theorem-lab/test-core.js
node research/combined_transfer_2026_09/review/presentation_review.js
python publication/transfer-theorem-v1/build_evidence.py
```

The first command has 19 tests, including exact toy boundaries, scenario parser
controls, all degree/window/amplitude settings over clock multipliers 0–200,
saved-contract containment, evidence identities and standalone runtime checks.
The independent mathematical review separately tests 606 toy, 4,020 arithmetic
and 192 spatial cases. Browser validation is recorded in the publication package.

Software is Apache-2.0; original explanatory content is additionally CC BY 4.0.
See the repository licenses and publication citation.
