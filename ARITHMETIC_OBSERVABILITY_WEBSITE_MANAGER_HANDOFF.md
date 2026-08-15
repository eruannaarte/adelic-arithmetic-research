# Arithmetic Observability Atlas: Website Manager Handoff

## User-mediated publishing package

- **Package status:** ready for the user to augment and hand to the Website
  Manager
- **Dispatch status:** not sent to the Website Manager
- **Prepared:** 15 August 2026
- **Repository:**
  `https://github.com/eruannaarte/adelic-arithmetic-research`
- **Publishing branch:** `codex/oig-finite-transfer`
- **Canonical Atlas commit:** `ff2eac1` (`Publish arithmetic observability atlas`)
- **Corpus schema:** `arithmetic-observability-corpus-v1`
- **Corpus payload SHA-256:**
  `a64f515f770d316a3d6ecad4b70494af1a5cc90342b4076c7fd783fce0f1c0d6`

This is the handoff artifact.  It is intentionally self-contained so the user
can append design, audience, deployment, or editorial instructions before
prompting the Website Manager.  Instructions added by the user at handoff
time are authoritative.

---

## Copy-ready Website Manager brief

### Assignment

Prepare a public web presentation for the **Arithmetic Observability Atlas**
from the canonical sources on the GitHub branch named above.  The Atlas is a
rigorous synthesis of ten manuscripts and eleven formal certificate packages.
It asks:

> Which local arithmetic distinctions are identifiable and stably
> recoverable from incomplete global harmonic information?

Build the presentation around exact reconstruction criteria, matching
impossibility results, quantitative stability, and the geometry induced by
distinguishability.  Preserve the boundary between proved mathematics,
finite certified computations, and open problems.

Do not deploy, notify collaborators, or broaden the scientific scope unless
the user's accompanying instructions explicitly authorize it.  By default,
return a preview and change summary for approval.

### Canonical source order

Read these sources in order:

1. `ARITHMETIC_OBSERVABILITY_WEBSITE_MANAGER_HANDOFF.md`
2. `ARITHMETIC_OBSERVABILITY_ATLAS.md`
3. `arithmetic_observability_corpus_manifest.json`
4. `README.md`, section **Reproduce Arithmetic Observability**
5. the numbered manuscripts I--X only when the Atlas cites a theorem that
   needs expanded hypotheses or proof context

The numbered manuscript is authoritative whenever a compressed Atlas
statement and the full theorem differ.  The corpus manifest is authoritative
for file identity, schemas, dependency edges, and certificate scope.

### Required publication outcome

Create one clear Atlas landing page, or an equivalent top-level Atlas section
within the existing research site, with these sections:

1. **Hero and status**
   - Title: `Arithmetic Observability Atlas`
   - Suggested subtitle: `Reconstruction, obstruction, and geometry from
     incomplete arithmetic measurements`
   - Display `Synthesis of Arithmetic Observability I--X` and
     `Not peer reviewed` above the fold.
2. **The common question**
   - Explain model, feature, protocol, nuisance, query, and response fibre.
   - Separate representation, acquisition, and nuisance obstructions.
3. **Two-branch model map**
   - Finite prime-box/no-tail branch: AO I--VI.
   - Degree-fourteen tail branch: AO I and AO VII--X.
   - Preserve the Atlas's Mermaid graph or render an accessible equivalent.
4. **Reconstruction versus obstruction**
   - Present positive and negative theorems as matched pairs.
   - Make the hypotheses visible; do not show theorem conclusions as
     context-free slogans.
5. **Distinguishability geometries**
   - Cover quotient, ANOVA, multiplicative pullback, compact phase,
     tangent--kernel, separated-query, zonoid, and arithmetic-defect
     geometries.
6. **Evidence and reproduction**
   - Link the Atlas, all ten manuscripts, the corpus manifest, and verifier.
   - Give the ordinary verification commands verbatim.
   - Mark the AO-IX full rebuild as an opt-in multi-gigabyte computation.
7. **Scope and open boundary**
   - Reproduce a concise version of the established/non-established ledger.
   - Link readers to the full Atlas scope section.

### Required theorem cards

At minimum, expose these four results with source links:

1. **Linear query criterion and exact minimax stability**

   `ker A subset ker L` is the exact identifiability criterion in the common
   linear nuisance model, and the recoverable case factors as `L=RA` with
   exact adversarial minimax radius `||R|| epsilon`.

   Source: AO I, Theorem 2.3.

2. **Sharp positive geometric reading count**

   The positive free-scale geometric model has exact global complexity `r`:
   a phase-separated `r`-reading schedule is globally injective, while every
   smaller schedule has reciprocal Borsuk--Ulam collisions.

   Sources: AO V, Theorems 3.2, 4.1, and 4.2; AO IV, Theorem 4.1.

3. **Sharp labelled product-simplex reading count**

   The labelled product-simplex model has exact global complexity
   `r floor(s/2)`, with a constructive DFT-isolating upper theorem and exact
   reflection/Borsuk--Ulam collisions for every smaller schedule.

   Source: AO VI, Theorems 3.2, 4.1, and 4.2.

4. **Near-matching degree-fourteen four-anchor radius**

   The certified common-nuisance lower radius is
   `0.019991343027394314...`; a legal eleven-mode independent-integral
   response gives upper radius `0.019999999997766001...`.

   Sources: AO IX, Corollary 2.4 and Equation 9.5; AO X, Section 8.1.

   Label this a near-matching bracket, not an exact radius or equality
   theorem.

### Editorial and scientific constraints

- Use **observational equivalence** only for equality under a deterministic
  effective observation or equality of whole response fibres.
- Use **confusability** for intersecting set-valued response fibres; do not
  call it an equivalence relation because it need not be transitive.
- Keep distance and adversarial critical radius distinct: in the AS-V branch,
  the critical radius is half the corresponding fibre distance.
- Do not merge the calibrated marginal norm, raw RMS norm, torus
  `l_infinity` norm, raw reading norm, quotient source norm, and weighted
  AS-V `L2` norm.
- Distinguish continuous coefficient boxes, independent integral envelopes,
  and arithmetically realizable coefficient sequences.
- Use `arithmetically realizable` only as a nonclaim boundary.  The corpus
  does not characterize that class.
- Say `formally certified computation` only when the associated package's
  declared finite scope supports it.  The corpus manifest does not mechanize
  analytic manuscript proofs.
- Do not claim peer review, historical priority, universal number-field
  recovery, infinite-Euler-product recovery, or an exact closest integral
  fibre.
- Do not turn the separate Operational Information Geometry protocol-engine
  integration into the Atlas's primary narrative unless the user requests
  that expansion.

### Suggested presentation language

**One-sentence summary**

> A ten-manuscript theory of when incomplete global harmonic measurements
> determine local arithmetic structure, when they cannot, how stable recovery
> can be, and what geometry the measurements impose.

**Suggested metadata title**

> Arithmetic Observability Atlas | Adelic Arithmetic Research

**Suggested metadata description**

> Exact recovery criteria, sharp reading counts, matching obstructions,
> induced geometries, and reproducible certificates for arithmetic harmonic
> models.

### Navigation and linking

Use repository-relative source links when the site build understands the
GitHub checkout.  Otherwise use branch-pinned GitHub links rooted at:

```text
https://github.com/eruannaarte/adelic-arithmetic-research/blob/codex/oig-finite-transfer/
```

The primary source links are:

```text
ARITHMETIC_OBSERVABILITY_ATLAS.md
ARITHMETIC_OBSERVABILITY_I.md
ARITHMETIC_OBSERVABILITY_II.md
ARITHMETIC_OBSERVABILITY_III.md
ARITHMETIC_OBSERVABILITY_IV.md
ARITHMETIC_OBSERVABILITY_V.md
ARITHMETIC_OBSERVABILITY_VI.md
ARITHMETIC_OBSERVABILITY_VII.md
ARITHMETIC_OBSERVABILITY_VIII.md
ARITHMETIC_OBSERVABILITY_IX.md
ARITHMETIC_OBSERVABILITY_X.md
arithmetic_observability_corpus.py
arithmetic_observability_corpus_manifest.json
test_arithmetic_observability_corpus.py
```

Do not maintain a second manual list of certificate dependencies.  Read the
manifest payload's `formal_packages` and external-dependency records.  That
machine-readable inventory binds 10 manuscripts, 11 formal packages, their
33 verifier/certificate/test files, and the external proof objects used by
the tail branch.

### Reproduction block

Show the ordinary verification commands exactly:

```bash
python arithmetic_observability_corpus.py \
  arithmetic_observability_corpus_manifest.json
python -m unittest -q test_arithmetic_observability_corpus.py
python -m unittest discover -s . \
  -p 'test_arithmetic_observability*.py' -q
```

The verified package state at handoff has:

- 51 focused corpus hostile tests passing;
- 333 Arithmetic Observability tests, with 332 passing and one intentional
  opt-in AO-IX rebuild skip;
- 797 whole-repository tests, with 796 passing and the same skip; and
- a separately successful AO-IX full reconstruction from unchanged AO-IX
  producer bytes.

The full AO-IX rebuild is deliberately not a default website-build step.  Its
producer environment and Windows/LF caveats are recorded in Atlas Section 9.

### Accessibility and quality bar

- Preserve mathematical notation with accessible text alternatives.
- Supply a readable fallback for the model-map diagram.
- Keep theorem tables usable on narrow screens.
- Ensure color is not the only distinction between proved, computed, and
  open material.
- Use descriptive link text rather than raw filenames in the visible UI.
- Verify every manuscript and reproduction link against the publishing
  branch.
- Surface the `Not peer reviewed` status and the open-boundary ledger without
  requiring interaction.

### Acceptance checklist

- [ ] The page identifies the source branch or immutable publication commit.
- [ ] All ten manuscripts are reachable.
- [ ] The two model branches are visually distinct.
- [ ] The four required theorem cards retain their hypotheses and sources.
- [ ] Confusability is not mislabeled as a general equivalence relation.
- [ ] Distance is not mislabeled as critical radius.
- [ ] The continuous/integral/arithmetic source classes remain distinct.
- [ ] The numerical four-anchor result is labeled a bracket.
- [ ] The corpus verifier and ordinary test commands are visible.
- [ ] The AO-IX rebuild is marked opt-in and resource-intensive.
- [ ] Proved, formally computed, descriptive, and open claims have distinct
      presentation treatments.
- [ ] No deployment occurs before the user's requested review gate.

---

## User additions before Website Manager dispatch

Add any desired visual direction, audience emphasis, site location, release
timing, deployment authority, analytics requirements, or additional calls to
action below this line.  These additions override the defaults above when
they are explicit.

```text
[USER ADDITIONAL INSTRUCTIONS GO HERE]
```

---

## Package integrity notes

The handoff deliberately points to the corpus manifest instead of duplicating
its 47-file integrity inventory.  The following identities are the compact
root of trust for the website content:

```text
Atlas SHA-256:
b381d3f9424de5ed5e6cfe35c27093ee2ce38b08d742299bfe7a1ee7a55db10f

Corpus verifier SHA-256:
01c75a062128db70a43b402241eca0fad96cc40bfbda04a867ed82951c1495f8

Corpus manifest SHA-256:
ee13e874b6a4da6455ed24bdbc74197fbd1fe39efbd87d8d15d1d813c8499ea6

Corpus tests SHA-256:
523801d9144272a1dfbf2a5284ce98a050afab48686b038a10159b078d0c1a66

Corpus payload SHA-256:
a64f515f770d316a3d6ecad4b70494af1a5cc90342b4076c7fd783fce0f1c0d6
```

This handoff itself is a publication brief, not a new mathematical source and
not part of the corpus payload.  Its language must not be used to enlarge the
hypotheses or conclusions of the numbered manuscripts.
