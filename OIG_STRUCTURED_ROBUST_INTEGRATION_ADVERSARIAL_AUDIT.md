# Adversarial audit: structured nuisance, robust model quotients, and integration

- **Audit date:** 15 August 2026
- **Audited implementation:** `oig_structured_nuisance.py`,
  `oig_robust_model_quotient.py`, and `oig_atlas_protocol_integration.py`
- **Method:** independent metric derivations, coordinate-covariance controls,
  one-dimensional counterexamples, trust-boundary attacks, strict JSON
  mutation, and extreme rational scaling
- **Edits to audited implementation:** none

## Verdict

The finite structured-nuisance primal/dual inequalities and the
source-metric quotient geometry survived independent rederivation.  In
particular:

- the metric dual denominator is \(u^T\Omega^{-1}u\), while profiling an
  unpenalized additive nuisance requires the covector condition \(B^Tu=0\);
- the exact zonotope support is
  \(\sum_jd_j|u^Tv_j|\), and the reported squared primal/dual gap expands
  exactly into metric residual mismatch plus support slack;
- the minimum-source-cost quotient uses
  \(S^{-1}C^T(CS^{-1}C^T)^{-1}C\), not a Euclidean projector;
- quotient-ball erosion by two equal source radii and two equal quotient-noise
  radii is exact;
- tangent--kernel angles use the declared source metric; and
- the blind-leakage envelope under an entrywise response box is a valid
  conservative bound.

The audit also found several certificate-level false positives and semantic
conflations.  The main implementation was subsequently hardened by its author
while the independent tests remained separate.  Exact fallback proposals now
also prevent binary64 range from limiting multidimensional rational form
certification.

**Publication verdict:** pass for the explicitly declared finite models and
conditional theorem-composition interfaces, subject to the external-premise
and partial-integration boundaries in Section 4.

## 1. Structured additive nuisance

### 1.1 Metric primal and dual checks

For

\[
 d=\inf_{\alpha,z\in\mathcal Z}
 \|q+B\alpha-z\|_\Omega,
\]

every \(u\) satisfying \(B^Tu=0\) obeys

\[
 d^2\ge
 \frac{(u^Tq-h_{\mathcal Z}(u))_+^2}
      {u^T\Omega^{-1}u}.
\]

The implementation uses this metric pairing correctly.  An independent
off-diagonal control with

\[
 \Omega=\begin{pmatrix}2&1\\1&2\end{pmatrix},
 \qquad r=(1,2)^T,
 \qquad u=\Omega r=(4,5)^T
\]

closes the exact squared distance at \(14\).  A diagonal output recalibration
\(y'=Dy\), together with
\(\Omega'=D^{-T}\Omega D^{-1}\) and \(u'=D^{-T}u\), preserves every distance
endpoint and the gap exactly.

### 1.2 Directional-only remote-tail defect — remediated

The first implementation gave the norm remainder a default exact value zero
and always minimized the norm-derived and direction-specific bounds.  A caller
supplying only a directional tail bound therefore received an unintended zero
tail charge.

The one-dimensional counterexample is \(q=1\), finite nuisance
\(\mathcal Z_F=\{0\}\), and an omitted interval with directional support
\(1/2\).  The true distance can be \(1/2\), but the old interface reported the
finite distance \(1\) as exact.

The remediated schema represents an absent premise by JSON `null`.  A
directional-only declaration is charged directly; a norm-only declaration
uses its rational \(\ell^1\) consequence; and only two genuinely present
bounds are minimized.

### 1.3 Scale-invariant dual flags — remediated

With \(q=1\), \(\mathcal Z=\{0\}\), and an overscaled dual \(u=3\), the
scale-invariant norm dual and the primal witness both prove \(d^2=1\), although
the half-squared dual value at that particular scale is negative.  The first
flags incorrectly said that positive separation and the exact optimum were
not certified.

The report now distinguishes squared-dual gap closure from closure of the
strongest final distance bracket.  Positivity follows from the final lower
endpoint, and exact optimality follows when the final lower and upper
endpoints agree.

### 1.4 Trust boundary

The finite verifier proves the algebraic consequences of a declared remote
support or norm bound.  It cannot prove that an omitted infinite generator
family actually satisfies that declaration.  Replacing only the provenance
string and treating it as a new premise therefore still verifies.  This is a
deliberate external-analytic trust boundary, not authenticated evidence.

## 2. Robust model-aware quotient

### 2.1 Coordinate and metric checks

For \(H=(1,1)\), \(S=\operatorname{diag}(1,4)\), and \(v=(1,2)^T\), the exact
quotient distance is \(36/5\).  Under the non-orthogonal source change

\[
 T=\begin{pmatrix}1&1\\0&1\end{pmatrix},
 \quad H'=HT=(1,2),
 \quad S'=T^TST=\begin{pmatrix}1&1\\1&5\end{pmatrix},
 \quad v'=T^{-1}v=(-1,2)^T,
\]

the implementation returns the same \(36/5\).  Directed dyadic square-root
bounds were also checked independently at deliberately low precision.

### 2.2 Finite secant exhaustiveness — false positive remediated

An arbitrary finite sample originally made
`nominal_null_safe_to_ignore=True` whenever its listed secants avoided the
kernel.  For \(H=(1,0)\), a visible sample \((1,0)\) hid the omitted exact
blind collision \((0,1)\).

The interface now separates finite-list separation from a declared exhaustive
model theorem.  The latter requires an explicit Boolean declaration and
nonempty proof provenance.  The verifier checks logical use of that premise;
it does not authenticate the external exhaustiveness proof.

### 2.3 Quotient stability versus task relevance — remediated

Preservation of the nominal kernel by every response in an uncertainty box
proves that one fixed quotient remains structurally valid.  It does not prove
that a query depending on that kernel is recoverable.  The earlier Boolean
combined these claims.

For \(H=(1,0)\), zero response radius, and query \(L=(0,1)\), the corrected
report says:

- the quotient family is stable;
- the query does not kill the kernel; and
- the nominal null is not task-irrelevant.

These are distinct statements and must remain distinct.

### 2.4 Query irrelevance versus uncertain blind leakage — remediated

Even when \(\ker H\subseteq\ker L\), operator uncertainty can turn an
unbounded blind component into unbounded observed nuisance.  With

\[
 H=(1,0),\qquad |D|\le(0,1),\qquad L=(1,0),
\]

the nominal query ignores the second coordinate, but
\(y=x_1+d x_2\) is uncontrolled if \(x_2\) is unbounded.  Query factorization
alone therefore cannot satisfy the response-uncertainty obligation.

The combined checker now requires either full-family null preservation or an
explicit blind-amplitude bound.  Query/model relevance remains a separate
obligation.  The bounded leakage is reported for later addition to the same
physical output-noise budget; that final budget composition is not yet done by
this partial model-geometry audit.

### 2.5 Strict standalone verification — added

The first robust reports did not serialize enough input data to reconstruct
their outputs and exposed no standalone verifier.  Boolean and numerical
fields could consequently be altered without detection.

Every finite robust schema now serializes its exact declarations.  A strict
reconstruction verifier rejects changed theorem Booleans, changed rational
endpoints, integer-for-Boolean substitutions, surplus theorem-like fields,
and nested mutations.  The demo adds cross-component declaration checks so an
individually valid certificate from another problem cannot be substituted.

As in the other integration lanes, reconstruction shares arithmetic helpers
with generation.  It is independent of serialized derived fields, not a
differential second implementation.

### 2.6 Additional remediations

- A zero-real-rank lattice map can no longer be conditionally classified as
  integer-kernel-free.
- Coarse square-root display bounds no longer produce a negative reported
  eroded-gap lower endpoint.
- The combined result is labelled a partial model-geometry audit and states
  that interval information-form loss remains an external certificate.
- Exact trace-based lower and upper form proposals cover inputs outside
  binary64 range.  The adversarial regression exercises both directions with
  a two-dimensional scale of \(10^{400}\), followed by strict standalone
  reconstruction.

## 3. Pinned Atlas-to-OIG integration

### 3.1 Initial follow-through defect — remediated

The first pinned integration script addressed
`positive_separation_certified` and `exact_optimum_certified` as top-level
structured-report fields. They are intentionally nested under
`exact_calculation`, so the integration demonstrator raised `KeyError` before
it could generate or verify a report. The corrected path is exercised by both
the integration tests and the independently reproduced committed artifact.

### 3.2 Cross-layer structured-noise composition — added

The first ledger separately asserted positive structured separation and raw
response-tube disjointness. Those two true statements did not themselves
prove survival when the bounded structured nuisance and the declared data
noise act together.

The revised ledger first seals the calibration needed to make the comparison:
the selected response and source secant induce the structured response
difference, while the candidate, structured, and response-tube output metrics
agree exactly and the candidate/tube source metrics agree exactly. For the
selected gain-two protocol, the structured certificate then gives

\[
 d_{m lower}^2=d_{m upper}^2=\frac94,
 \qquad
 \varepsilon_{m crit}^2=\frac9{16},
\]

while the response-tube declaration uses

\[
 \varepsilon^2=\left(\frac12\right)^2=\frac14<\frac9{16}.
\]

Thus the selected protocol remains disjoint under the declared correlated
nuisance and the declared equal data-noise balls. The adversarial test
recomputes the response-on-secant relation, metric equalities, and strict
radius inequality from the serialized declarations rather than trusting the
ledger Booleans.

### 3.3 Top-level verifier attacks

The integration verifier reconstructs all six child reports, then rebuilds
the pinned report and its cross-layer ledger. It rejected:

- a different structured-nuisance certificate that verifies correctly on its
  own but belongs to another problem;
- a different valid response-tube certificate with response gain three;
- integer-for-Boolean substitution in the final ledger;
- a flipped cross-layer composition result;
- a rewritten proof boundary; and
- a surplus claim of continuous-library optimality.

The committed JSON report is byte-independent but object-identical to a fresh
deterministic build after JSON parsing, and both pass the standalone verifier.
The candidate-library child also seals a common source, query, metric, and
noise-radius comparison contract, so the pinned winner cannot be manufactured
by ranking different scientific tasks against one another.

### 3.4 Integration scope

The pinned report is a finite rational demonstrator, not a theorem that its
toy protocols exhaust a physical design space. Its robust-model component is
a separately declared geometry audit; it is not silently identified with the
selected scalar gain protocol. Remote-tail truth, physical response enclosure,
model-family exhaustiveness, and response-box information transfer remain
explicit external obligations.

## 4. Remaining limitations

1. **External exhaustive-model premise.**  A provenance string labels but does
   not prove that a finite secant list is exhaustive.
2. **External irrational lattice predicate.**  The lattice middle-regime
   composer checks logical consistency but cannot authenticate its cited
   Diophantine proof.
3. **Finite versus global geometry.**  A finite secant list and finitely many
   tangent charts do not cover a continuum model unless a separate reduction
   or covering theorem says they do.
4. **Partial combined target.**  Response-box information loss and bounded
   blind leakage have not yet been propagated into one calibrated physical
   output-noise budget.
5. **Uncertainty model.**  The robust null calculation assumes independent
   symmetric entrywise response intervals.  Correlated operator uncertainty
   needs a different support/enclosure layer.
6. **Reconstruction versus differential verification.**  Standalone report
   verification rebuilds from exact declarations with the same arithmetic
   helpers; it is not a separately implemented formal checker.

## 5. Executable audit

Run:

```text
python -m unittest -v \
  test_oig_structured_nuisance.py \
  test_oig_structured_nuisance_adversarial.py

python -m unittest -v \
  test_oig_robust_model_quotient.py \
  test_oig_robust_model_quotient_adversarial.py

python -m unittest -v \
  test_oig_atlas_protocol_integration.py \
  test_oig_atlas_protocol_integration_adversarial.py \
  test_oig_protocol_artifacts.py
```

After remediation, all suites pass completely, including extreme rational
scaling, semantic counterexamples, coordinate covariance, cross-layer
composition, JSON round trips, valid-but-incoherent child substitution, and
strict mutation rejection.

The query-directed lane has a separate independent audit in
`OIG_QUERY_PROTOCOL_DESIGN_ADVERSARIAL_AUDIT.md`.
