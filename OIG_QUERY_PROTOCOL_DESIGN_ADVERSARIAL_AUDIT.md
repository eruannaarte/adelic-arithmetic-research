# Adversarial audit: exact query-directed protocol certificates

- **Audit date:** 15 August 2026
- **Audited files:** `oig_query_protocol_design.py`,
  `test_oig_query_protocol_design.py`, and
  `OIG_QUERY_PROTOCOL_DESIGN_THEOREM.md`
- **Method:** independent exact examples, coordinate-covariance controls,
  branch-boundary mutation, and direct standalone-verifier attacks
- **Edits to audited files:** none

## Verdict

No mathematical counterexample was found to the finite linear query theorem,
the metric nuisance projector, the minimax generalized Rayleigh quotient, or
the two declared mixture composition laws.  A non-diagonal metric example has
exact squared amplification `7`; it remains `7` after a non-orthogonal output
coordinate change.  Redundant nuisance coordinates leave the projector and
amplification unchanged.  The zero-query boundary also behaves correctly when
the effective response is nonzero.

The initial audit found a narrower report-envelope defect: cached verification,
the scope boundary, and branch-specific prose or surplus theorem claims could
be altered while `verify_query_protocol_report` still returned `passed=True`.
Those attacks were reported before publication freeze and have now been
remediated.  The standalone verifier seals the exact per-branch report surface,
the nuisance-specific scope statement, and the embedded verification result.

The earlier mandatory-float range failure was also removed.  A new regression
certifies and independently reconstructs a two-dimensional response scaled by
`10**400` using exact fallback proposals.

**Publication verdict:** pass for the explicitly declared finite rational
linear models and nuisance semantics, subject to the scope boundaries in the
theorem note and Section Q5 below.

## Findings

### Q1. Embedded verification sealing — remediated

The original verifier ignored `independent_exact_verification`.  Deleting it,
changing `passed` to `False`, or replacing its exact lower bound by `999/1`
survived verification.  The current verifier requires and reconstructs the
canonical block; all three mutations are rejected.

### Q2. Early-return branch schemas — remediated

The original unidentifiable branch did not reconstruct its `reason` and
accepted a surplus `decoder_exact`.  The zero-effective/zero-query branch
accepted contradictory surplus claims.  Exact allowed key sets and canonical
branch payloads now reject missing reasons, false reasons, false raw
factorizations, infinite-error claims on a zero query, and other surplus
theorem-like fields.

### Q3. Model-specific proof boundary — remediated

The original proof boundary was mutable and described every mixture as an
“unrestricted shared nuisance,” including the independent-refit model.  It is
now selected canonically from `model_kind`, and mutation into a physical-model
claim causes verification failure.

### Q4. Extreme rational scaling — remediated

Floating generalized eigensolvers decide no theorem flag.  They were initially
mandatory proposal generators, so a valid response of scale `10**400`
overflowed before exact LDL could run.  Exact rational upper and Rayleigh
witness fallbacks now cover this case.  The adversarial suite pins the exact
lower amplification (10^{-800}) in a two-dimensional model and verifies the
complete report without binary-float conversion becoming a correctness or
completeness gate.

### Q5. Remaining terminology boundary: reconstruction is not a second implementation

The builder and verifier share `_profile_nuisance`, row-basis, inversion, and
LDL helpers.  The verifier is independent of serialized derived fields, but it
is not a differential implementation capable of detecting a systematic helper
bug.  “Exact reconstruction verifier” is therefore the precise description.
The independently derived metric, covariance, nuisance-basis, and extreme-scale
controls provide additional protection against common-mode mistakes, but they
do not constitute a second formal implementation.

### Q6. Finite-library comparison contract — remediated

The first finite candidate selector verified each child interval but did not
require the children to describe the same scientific query.  It could
therefore certify a zero-query candidate as uniquely better than a nonzero
query, or manufacture a different ranking by rescaling the query metric.  That
is exact arithmetic applied to incomparable losses, not experimental design.

The selector now extracts, serializes, and strictly verifies a common contract
containing the source dimension and metric, query dimension and matrix, query
metric, and unit data-noise-radius convention.  A mixed zero/nonzero query,
changed query metric, or changed source convention is rejected before any
winner is selected.  Candidate-specific output metrics remain allowed because
they are calibrated design/noise declarations under the common unit-radius
convention.

## Executable audit

Run:

```text
python -m unittest -v \
  test_oig_query_protocol_design_adversarial.py \
  test_oig_query_candidate_library_adversarial.py
```

After remediation, all fourteen adversarial methods pass.  They cover four
independently derived mathematical/covariance boundaries, extreme rational
scaling, the formerly successful report-envelope attacks, and exact
finite-library comparability.

## Remaining scope boundaries

1. The exhaustive truth of any external physical or continuum enclosure is
   outside this finite certificate.
2. Shared and independently re-fit nuisance mixtures are different statistical
   models; neither may be substituted for the other after certification.
3. The certified rational mixture is not claimed optimal merely because its
   query amplification is certified.
4. The verifier reconstructs with shared exact helpers; publication should not
   describe it as an independent differential implementation.
5. Finite-library optimality remains limited to the embedded, contract-compatible
   candidates; it does not prove continuous-design or candidate-library
   completeness.
