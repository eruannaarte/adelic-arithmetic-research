# Global Geometry: Website Manager Handoff

## Direct publication package

- **Package status:** research contract, interactive laboratory, tests,
  reproducibility manifest, citation metadata, and reuse terms are prepared
- **Dispatch status:** direct Website Manager publication requested and
  authorized by the project owner on 29 August 2026
- **Repository:**
  `https://github.com/eruannaarte/adelic-arithmetic-research`
- **Publishing branch:** `codex/publish-global-geometry-lab`
- **Publishing commit:** supplied in the direct task dispatch; publish only
  that immutable commit or a reviewed descendant
- **Draft pull request:** supplied in the direct task dispatch
- **Suggested public record ID after collision checking:**
  `GG-2026-08-29-001`
- **Suggested slug:** `global-geometry-local-rules`
- **Suggested article route:**
  `/number-geometry/global-geometry-local-rules/`
- **Suggested laboratory route:**
  `/number-geometry/global-geometry-local-rules/lab/`
- **License:** Apache-2.0 for software, with the repository's additional
  CC BY 4.0 grant for original non-software explanatory content

This is the canonical publication brief for the first finite release of the
Global Geometry research programme and its executable laboratory.  The phrase
“Global Geometry” is a programme label for this synthesis; it is not a claim to
have founded the mathematical subjects it draws upon or established literature
priority.

---

## Copy-ready assignment

Publish **Global Geometry · How Local Rules Make Worlds** as a Number Geometry
research article with the **Global Geometry Lab** beside it.  The article and
lab answer one operational question:

> How can purely local rules produce a global shape, dimension, or geometry?

The central answer is:

```text
local data
+ compatible gluing
+ accumulated defects
+ repeated propagation or relaxation
+ observation scale
→ finite global geometry
```

Local edge data and incidence compose into a global path metric.  Local angular
closure failures accumulate into curvature and exact finite topological
identities.  Repeated neighbour diffusion creates global heat, spectral, and
transport structure.  Local curvature-error feedback can attempt to program a
target metric.  Boundary conditions, topology, admissibility obstructions, and
initial state remain globally decisive, so a local law generally determines a
class of possible worlds rather than a unique world.

Required above-the-fold scope labels:

```text
Executable finite research programme
Exact finite identities and numerical estimates are labeled separately
Application presets are analogies, not empirical models
Not peer reviewed
```

Suggested metadata title:

```text
Global Geometry: How Local Rules Make Worlds | The God Network
```

Suggested metadata description:

```text
An interactive discrete-geometry laboratory for generating, programming, and
recognizing global metric, curvature, topology, and scale-dependent dimension
from compatible local rules.
```

## Canonical source order

Read these immutable-repository sources in order:

1. `GLOBAL_GEOMETRY_WEBSITE_MANAGER_HANDOFF.md`
2. `GLOBAL_GEOMETRY_LAB.md`
3. `global_geometry_reproducibility_manifest.json`
4. `website/global-geometry-lab/README.md`
5. `website/global-geometry-lab/index.html`
6. `website/global-geometry-lab/global-geometry-core.js`
7. `website/global-geometry-lab/test-global-geometry-core.js`

The research contract is authoritative for mathematical meaning.  The core is
authoritative for the implemented finite model.  The manifest is authoritative
for source identities and commands.  Condensed website prose must not broaden
claims beyond those sources.

## Required article structure

1. **The question and answer**
   - State the local-data/gluing/defect/propagation/scale mechanism.
   - Explain that local rules do not imply a unique global world.
2. **One state model**
   - Present the finite state
     `G_n = (K_n, ell_n, mu_n, W_n, U_n, Pi_n)`.
   - Distinguish the authoritative intrinsic edge metric from the browser
     projection.
3. **Three directions**
   - Forward: local rule to global geometry.
   - Inverse: target geometry to local feedback, subject to obstructions.
   - Recognition: supplied finite observations to compatible descriptors and
     ambiguity.
4. **Compatibility and obstruction**
   - Explain finite gluing, curvature defects, topology, Gauss--Bonnet, and why
     the target-curvature sum is necessary but not sufficient for arbitrary
     realizability.
5. **Dimension is a profile**
   - Keep volume-growth, spectral, and walk dimension distinct.
   - Preserve their different native clocks and the absence of any claimed
     continuum plateau from one finite run.
6. **The executable laboratory**
   - Embed or link the complete dependency-free lab.
   - Explain deterministic replay, configuration validation, paired-world
     comparison, declared interventions, and JSON export.
7. **Application map**
   - Networks, manifold learning, programmable materials, morphogenesis,
     componentwise swarm consensus, and a relational-graph physics toy.
   - Keep every domain boundary visible.
8. **What is exact, numerical, open, and analogous**
   - Preserve the four-level evidence ladder.
9. **Reproduction, sources, citation, and reuse**
   - Link the immutable commit, manifest, tests, research contract, citation
     file, and licenses.
10. **Open research programme**
    - Continuum limits, inverse realizability, dimension agreement,
      defect stability, universality classes, and recognition lower bounds.

## Canonical static laboratory

Publish these files together:

```text
website/global-geometry-lab/index.html
website/global-geometry-lab/global-geometry-lab.css
website/global-geometry-lab/global-geometry-core.js
website/global-geometry-lab/global-geometry-lab.js
website/global-geometry-lab/README.md
website/global-geometry-lab/test-global-geometry-core.js
```

The production route loads only the HTML, CSS, core, and controller.  The
README and Node suite belong in the public GitHub reproduction package.

The laboratory has no package install, build system, worker, CDN, external
font, analytics, dynamic import, server API, remote request, or user-code
evaluation.  It may run from a file URL, but the published and documented
experience should use HTTP(S).  A strict same-origin Content Security Policy
is compatible; no `unsafe-eval`, inline script permission, or outbound network
permission is required.

When adapting the standalone page to the publication route:

- rewrite `../../GLOBAL_GEOMETRY_LAB.md` to the public article or immutable
  GitHub research-contract URL;
- keep the SVG titles, descriptions, keyboard-operable vertices, status
  regions, focus indicators, and responsive controls;
- preserve the closed JSON configuration vocabulary and bounded generator
  sizes;
- preserve deterministic seeds and the finite-run export record; and
- do not feed L2 analysis results silently into an update labeled L0.

## Required laboratory behavior

1. Nine presets remain available across forward, inverse, and recognition
   lenses.
2. Exact topology is displayed only when integer Betti values pass the
   Euler--Poincare audit.
3. The exact Gauss--Bonnet badge fails closed unless the displayed triangular
   complex passes the manifold and metric validity gates.
4. Missing curvature targets remain missing; ordinary states must not acquire a
   fabricated zero-curvature objective.
5. The inverse target is compiled and obstruction-checked before runtime; the
   radius-one synchronous update remains separately labeled.
6. Volume-growth, spectral, and walk profiles retain actual logarithmic scale
   locations and distinct native clocks.
7. The dimension readout remains a finite point estimate with no unsupported
   refinement plateau claim.
8. The paired-world comparison reports exact topology agreement and finite RMS
   profile/spectral distances; it must not claim isometry or continuum
   universality.
9. Adjacency rewrites, pulses, and jitter remain declared interventions rather
   than ordinary local steps.
10. Configuration import rejects unknown, malformed, nonfinite, and oversized
    inputs without evaluating text as code.
11. Export retains configuration, state, analysis, replay identifier, method
    labels, evidence labels, and any paired-world comparison.
12. The page remains keyboard operable and has no horizontal overflow at 360,
    736, and 1,024 CSS pixels.

## Evidence ladder that must remain visible

- **Exact finite identity:** GF(2) homology, Euler characteristic, and
  Gauss--Bonnet for a valid finite triangulated surface.
- **Finite numerical estimate:** eigenspectrum, heat trace, dimension slopes,
  local-flow trajectories, and two-world signature distances.
- **Research target:** continuum convergence, universality, robustness,
  identifiability, and arbitrary inverse realizability.
- **Application analogy:** every materials, tissue, network, learned-manifold,
  swarm, or spacetime interpretation.

No numerical run may be promoted to a theorem.  No domain-themed preset may be
promoted to empirical adequacy.

## Scientific boundaries that must remain public

- The screen drawing is a projection, not the intrinsic geometry.
- A finite graph or complex is not automatically a smooth manifold.
- A small Gauss--Bonnet residual is a numerical consistency check for an exact
  finite identity, not a new theorem.
- Passing the total-curvature obstruction does not prove that every target is
  realizable or that the local flow converges.
- On a fixed finite graph, spectral dimension returns toward zero at extreme
  heat scales; continuum dimension requires refinement or ensemble evidence.
- Volume, heat, and walk clocks are not silently identified.
- The recognition preset computes descriptors of the complete supplied graph;
  it does not recover a unique latent manifold from bounded observations.
- Two finite seeds with similar signatures do not establish isometry or a
  universality class.
- The morphogenesis preset has no developmental calibration or tissue
  mechanics.
- The sheet preset has no constitutive law, elasticity, collision, or
  fabrication model.
- The swarm preset evolves information on fixed components; it is not a robot
  controller or collision-avoidance system.
- The physics preset is an undirected relational-graph analogy, not Lorentzian
  spacetime, gravity, quantum dynamics, or evidence for our universe.
- The work synthesizes established mathematics, is not peer reviewed, makes no
  literature-priority claim, and introduces no new proved theorem in this
  release.

## Mathematical anchors

The public article should credit the established foundations directly:

- Regge, piecewise-flat curvature and deficit angles:
  `https://cds.cern.ch/record/472394`
- Cheeger--Muller--Schrader, convergence of polyhedral curvature measures:
  `https://www.cs.jhu.edu/~misha/Fall09/Cheeger84.pdf`
- Desbrun--Hirani--Leok--Marsden, discrete exterior calculus:
  `https://arxiv.org/abs/math/0508341`
- Ollivier, coarse Ricci curvature from local transport contraction:
  `https://arxiv.org/abs/math/0701886`
- Belkin--Niyogi, graph-Laplacian approximation of manifold Laplacians:
  `https://papers.nips.cc/paper/2006/hash/5848ad959570f87753a60ce8be1567f3-Abstract.html`
- Chow--Luo, combinatorial Ricci flow:
  `https://sites.math.rutgers.edu/~fluo/mpapers/combinatorial%20Ricci%20flow%20in%20dimension%202.pdf`

The article may explain the synthesis and executable composition as this
release's contribution, but it must not imply that these component theories or
their classical theorems are novel here.

## Reproduction and acceptance gates

From the immutable repository commit:

```bash
node --test website/global-geometry-lab/test-global-geometry-core.js
python -m http.server 8000 --bind 127.0.0.1
```

Then open:

```text
http://127.0.0.1:8000/website/global-geometry-lab/
```

The broader browser-laboratory regression command is:

```bash
node --test website/double-pendulum-oig-wind-tunnel/test-wind-tunnel-core.js website/double-pendulum-oig-wind-tunnel/test-wind-tunnel-ensemble-adversarial.js website/global-geometry-lab/test-global-geometry-core.js
```

Frozen package expectations:

```text
Global Geometry mathematical/adversarial checks: 26/26
combined browser-laboratory regression checks:       58/58
live forward/inverse/recognition interaction QA:      pass
closed-schema rejection QA:                          pass
keyboard vertex and profile controls:                pass
responsive widths 1024 / 736 / 360:                  pass
horizontal overflow:                                 none
browser console errors:                              none
```

Before deployment, the Website Manager should additionally verify the exact
immutable GitHub hashes, adapt links without changing scientific meaning, run
the website's full source-record/privacy/release suite, test the deployed HTTPS
route at desktop and narrow width, confirm all runtime assets return 200,
confirm POST remains rejected by the public origin, and preserve the previous
immutable release as the rollback point.

## Package SHA-256 identities

```text
59154a8c13a8856af7a04810d692efb9198dd3c770c6e2da9128fb87b564378b  GLOBAL_GEOMETRY_LAB.md
ac0027aaca7bfd96e1e8db74c9bd61ea4e3b20cdfc6be203097f2d548d90318c  website/global-geometry-lab/README.md
5a562c2f15e624a09471812986f49f5a2198f4578392e120924bcff6dc0448c3  website/global-geometry-lab/index.html
80d0a3e0294ceea4b284f40f23317fe087eaea60d07b2de88bb15d2ec89d6991  website/global-geometry-lab/global-geometry-lab.css
9c461080b306b4304e4aa0d266d86d55ee31a9c90690a6f01e83022d55f4d77d  website/global-geometry-lab/global-geometry-core.js
a078750217d83e1940b3a96a33d5ba6bcacc59880d15866d1aadce24159618a1  website/global-geometry-lab/global-geometry-lab.js
cabf274a7cacd763107cfed9afe3e2d6f174170195a244ff1c473894b8006fb9  website/global-geometry-lab/test-global-geometry-core.js
8793f33f9ca095db6f14742f2d8fb6cddf87b5e3eab915e1608ec1e58a01da67  CITATION.cff
c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4  LICENSE
c25b0ddbe8ddc9dfad01a4363aa7528840ce1d3a5324e7f809994ef4603a13aa  LICENSE-CONTENT.md
```

The machine-readable copy is
`global_geometry_reproducibility_manifest.json`.  Recompute and compare every
identity from the immutable commit before publishing.

## Attribution

Suggested public attribution:

```text
Research programme, mathematical synthesis, implementation, tests, and
writing: Codex (OpenAI).

Originating question, research direction, collaborative refinement,
publication authorization, and research environment: TGN's human founder.
```

Classical mathematical ingredients and primary sources must retain their own
attribution.  The public page should link `CITATION.cff`, `LICENSE`, and
`LICENSE-CONTENT.md` at the immutable source commit.

## Deployment and rollback rule

Build a new immutable website release from the complete approved public source
set.  Do not mutate an earlier release.  Preserve the previous selected release
until the article, lab, source links, CSP, discovery outputs, read-only HTTP
behavior, Mac origin, and managed Windows mirror all pass.  If any runtime
asset, source identity, evidence label, privacy check, or scientific boundary
fails, keep the new release unpublished or roll back atomically.
