# Website Manager addendum: Global Geometry II evaluation checkpoint

This addendum extends `GLOBAL_GEOMETRY_WEBSITE_MANAGER_HANDOFF.md` for the
Global Geometry II lab and its release-v2 evidence checkpoint.  For Global
Geometry II, the package lists and status language below supersede the earlier
handoff's first-release lists.  The original handoff still governs the shared
site shell and Global Geometry I pages.

## Publication identity

- Public page: `website/global-geometry-lab/global-geometry-ii.html`
- Public status: **shareable evaluation checkpoint**
- U2 result: `UNRESOLVED`; no acceptance or rejection claim
- Universality decision authority: `NONE`
- Finite preview: `NOT_EVALUATED`
- Full confirmatory campaign: `NOT_RUN`
- Physical and camera validation: `NOT_RUN`
- Cross-platform exact replication: `FAIL` for both the strict partial
  campaign and screening-v3 raw stream

The nondecisional `1e-12` diagnostic comparisons may be described as
portability diagnostics only.  They do not repair the exact failures or close
Gate 8.

## Canonical publication surface

Publish the repository paths without flattening or renaming them:

1. `website/global-geometry-lab/` — the complete lab runtime, page, styles,
   tests, release-v2 generators, validators, and reproduction tools;
2. `artifacts/global-geometry-ii/` — tracked compact artifacts, deterministic
   gzip transports, fabrication templates, input registry, release index, and
   scoped certificates;
3. `global_geometry_ii_reproducibility_manifest_v2.json`;
4. `GLOBAL_GEOMETRY_II_U2_EVALUATION_REPORT.md`;
5. `GLOBAL_GEOMETRY_II_MANUSCRIPT.md`;
6. `GLOBAL_GEOMETRY_II_IMPLEMENTATION_PLAN.md`;
7. `GLOBAL_GEOMETRY_II_U2_FULL_EVALUATION_FEASIBILITY.md`;
8. `GLOBAL_GEOMETRY_LAB.md` and the root `README.md`.

Do not publish local unpacked campaigns, raw JSONL files, chunk directories,
run locks, transfer helpers, logs, or provenance paths containing workstation
locations.  The four tracked `*.json.gz` files in
`artifacts/global-geometry-ii/u2/evaluation-v2/` are the deliberate compact
transports for those large sources.

## Required linked evidence

The public page must retain working same-origin links to:

- `GLOBAL_GEOMETRY_II_U2_EVALUATION_REPORT.md`;
- `artifacts/global-geometry-ii/u2/evaluation-v2/evaluation-index-v2.json`;
- `artifacts/global-geometry-ii/u2/evaluation-v2/strict-cross-comparison-v1.json`;
- `artifacts/global-geometry-ii/u2/evaluation-v2/screening-v3-cross-comparison-v1.json`;
- `global_geometry_ii_reproducibility_manifest_v2.json`;
- `artifacts/global-geometry-ii/release-index-v2.json`;
- `artifacts/global-geometry-ii/certificates/macos-windows-comparison-v2.json`;
- `artifacts/global-geometry-ii/fabrication/physical-preflight-v1.json`.

The historical v1 index and comparison remain downloadable historical records
only.  They do not certify release v2.

## Deployment verification

From the repository root, run:

```bash
node website/global-geometry-lab/reproduce-global-geometry-ii-v2.js --verify --mode quick
node website/global-geometry-lab/reproduce-global-geometry-ii-v2.js --verify --mode deep
GGII_STATIC_PUBLICATION_REQUIRE_COMPARISON_V2=1 node website/global-geometry-lab/test-global-geometry-ii-static-publication-v2.js
```

Both reproduction commands are read-only.  Deep mode remeasures the current
host's native strict and screening artifacts and verifies the foreign host via
its bound native certificate; it does not run the full confirmatory campaign.

Serve over HTTPS with a same-origin CSP such as `default-src 'self'`; the page
uses external scripts and no inline event handlers.  Confirm that JSON, JSONL
gzip, SVG, JavaScript, CSS, Markdown, and HTML receive appropriate MIME types,
that gzip files are served as downloads rather than transparently rewritten,
and that byte-preserving deployment leaves every release-v2 hash valid.

## Acceptance checklist

- The page visibly separates preview `NOT_EVALUATED`, checkpoint `UNRESOLVED`,
  and full/physical `NOT_RUN` states.
- Exact cross-platform `FAIL` results remain visible.
- The 112 screening estimator-unavailable records and the strict
  normalization-not-consumed caveat remain disclosed.
- No prose says U2 is accepted, rejected, confirmed, or physically validated.
- All local links close after deployment.
- Quick and deep verification pass from the deployed source package.
- The evaluated commit and release-v2 comparison record are identified in the
  publication change log.
