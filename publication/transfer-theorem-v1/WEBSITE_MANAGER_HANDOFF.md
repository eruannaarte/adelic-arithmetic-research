# Transfer Theorem v1 — finished publication package

For **Website Manager**, Autonomous Radio Explorer. The user requested this
research continuation, a shareable presentation, publication of reproducibility
elements to the research GitHub repository, and delivery of the finished package
to this task. Integrate it using the website's normal review/release workflow.

## Public identity and source

- Visible research line: **Certified query recovery under structured uncertainty**.
- Public article title: **Certified answers from imperfect experiments**.
- Lab title: **The Transfer Theorem Lab**.
- Repository: [Adelic Arithmetic Research](https://github.com/eruannaarte/adelic-arithmetic-research).
- Immutable version identifier: `transfer-theorem-v1-2026-09-05`.
- [Release and downloads](https://github.com/eruannaarte/adelic-arithmetic-research/releases/tag/transfer-theorem-v1-2026-09-05).
- [Public guide source](../../TRANSFER_THEOREM_PUBLIC_COMPANION.md).
- [Current research report](../../research/combined_transfer_2026_09/REPORT.md).
- [Reproduction guide](PORTABLE_GUIDE.md), [citation](CITATION.cff), [browser QA](BROWSER_QA.json).

The delivery message supplies the verified commit and asset checksums. Confirm
those against the release before copying assets. The published research branch
preserves the existing programme history; this delivery does not require merging
unrelated pending programme branches into the repository's default branch.

## Suggested integration

1. Publish the public guide at `/number-geometry/certified-query-recovery/`.
2. Serve the standalone lab at `/number-geometry/certified-query-recovery/lab/`.
3. Link the lab with **Explore the Transfer Theorem Lab**.
4. Add the research line to the Number Geometry ledger with the three precise
   results below and links to the proof/report/reproduction release. Preserve the
   original programme pages and historical records.
5. Add the article and lab to existing navigation, sitemap, public discovery and
   lab manifests. `lab-manifest.json` provides a bounded static metadata source.
6. Keep existing owner approval, immutable release, content-hash, CSP, rollback,
   and Mac/Windows origin procedures. Package delivery is not evidence of a live
   production deployment.

All serving assets are in `website/transfer-theorem-lab/`:

| File | Purpose |
|---|---|
| `index.html` | Complete accessible guide and interactive shell |
| `transfer.css` | Responsive presentation and print styles |
| `core.js` | Exact toy membership and saved-contract inheritance |
| `app.js` | SVG views, controls, share/import/export UI |
| `evidence.js` | Embedded public evidence; direct-file loading needs no fetch |
| `evidence.json` | Equivalent portable evidence index |
| `lab-manifest.json` | Asset hashes, declared routes, scope and provenance |

Serve these files together. There is no build, external script, external font,
analytics, storage, API call, active WebMCP registration or backend compute.
User-provided scenario JSON contains only a small closed set of control values.
The page makes no background network requests; following an evidence link opens
the pinned GitHub record. Dynamic chart styles use element style properties, as
in the existing labs; verify compatibility with the site's actual CSP.

## The three new results

- **Combined six-channel spatial contract:** rows 485/493/499/501/507/515,
  sensor radius 3e-8, shared clock and potential radii 1e-8, all 21 targets,
  all nonzero two-mode sources and all admitted nominal/actual times in [1,2].
  Relative source error <0.000852831068. The coarse inverse also passes this
  small box; the achievement is the combined acquisition/uncertainty contract.
- **Complete arithmetic clock blocks:** base bound <2.987008e-8, over 53.45%
  smaller than the previous pairing bound. Degree12 recovers all 49 unknown
  integers at 120 times the base clock radii, with complete errors <0.447153367
  and <0.496198708. The prior outer-window pair formula exceeds 0.506493579 at
  this identical contract. This is a sufficient-certificate comparison.
- **Degree 11 verified:** at amplitude 4000/frequency 3/base clock its sufficient
  bound misses the target (32/49 gates). At amplitude 500 it certifies all 49,
  errors <0.445865330 /0.494913819 with the new clock bound. Twelve is least
  passing among tested 6/8/10/11/12; this is not a universal degree lower bound.

## Presentation and evidence boundaries to preserve

The lab begins with possible answers, gives the compact transfer theorem, then
the spatial and arithmetic experiments, the original five paths and nine-package
history. The toy is exact for its displayed observation and explicitly selected
source class. The research plots are rounded estimates; badges inherit saved
contracts. Do not replace an out-of-certificate message by an impossibility claim.
Continuous source percentages round upward. Arithmetic errors are complex
moduli; integer rounding uses the real part.

Keep source norms, complete infinite tails, the known first coefficient, shared
affine-clock incidence, separate mismatch, actual residual requirements and model
family limits. Model membership cannot come from a solver residual. Pendulum
apparatus calibration remains unperformed; these results have internal independent
reviews, not external peer review or a claimed historical priority.

## Validation and release files

There are 33 focused research tests and 19 lab tests. Independent reviewers also
checked 606 toy cases, 4020 arithmetic scenarios and 192 spatial boundary cases,
the 10 display profiles and 7 source-evidence hashes. The scientific package has
complete-time consumers, complete orbit tails, fresh actual-matrix solves and
320/384/448-bit internal replays. All 660 original local artifacts are unchanged. The public source includes 657
of them plus the original hashes and citations of three omitted third-party
reference scans; those scans are not numerical inputs. See the public archive
note in the current research package.

Browser QA covers desktop,390px mobile,360px narrow mobile and 768px tablet,
control boundaries, shared URL state and scenario import. Export exposes a
manual JSON fallback. Local `file://` navigation was blocked by the browser tool's
URL policy; the direct-file design has a static dependency audit, not an observed
file-URL browser run. The browser tool also did not deliver a Blob download event;
the export handler and visible JSON fallback were checked separately. Preserve
these QA limits if summarizing validation.

The release includes:

- `Transfer-Theorem-Lab-v1.zip` — self-contained interactive guide.
- `Transfer-Theorem-Publication-v1.zip` — exact website assets, public guide,
  citation, validation, source builders and this handoff.
- `Transfer-Theorem-Reproducibility-v1.zip` — complete repository source at
  the release commit, including all scientific dependency packages.
- `SHA256SUMS` — hashes of these three assets.

The standalone lab is shareable immediately through its public download. The
final website URL becomes the preferred link once your release is live.
