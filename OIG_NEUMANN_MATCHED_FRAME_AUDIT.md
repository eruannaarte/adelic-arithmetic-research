# Independent audit: finite Neumann matched sensor frame

**Audited artifacts:** `oig_neumann_matched_frame.py` and
`test_oig_neumann_matched_frame.py`

**Audit method:** exact-rational reconstruction, independent Arb comparison,
hostile-sign quadratic-form control, report-integrity review, and a fresh
default certificate run

**Verdict:** the mathematical certificate generated in memory is sound for
its stated model.  One publication-hardening fix is required: the top-level
matched-frame report needs its own independent verifier.  A wording repair
should also make the absolute-value step in the frame-loss proof explicit.

**Post-audit resolution:** both items were implemented. The generator now
self-calls `verify_neumann_matched_frame_report`, which reconstructs the
sensor rows, covariance, response boxes, complete and compressed floors, and
outer pass fields. The proof text and implementation now distinguish the
actual signed error from its nonnegative radius and explicitly apply the
diagonal row-sum form bound. All nine original and adversarial matched-frame
tests pass without a skip.

## 1. Fresh default run

The command

```bash
python oig_neumann_matched_frame.py \
  --output /private/tmp/oig_neumann_matched_frame_audit_default.json
```

completed successfully at (n=345), 192-bit Arb precision, and Taylor degree
32.  It retained 172 active even target modes and returned
`overall_passed=true`.

The following decimals are only readable summaries of exact rational fields.

| source metric | nominal complete floor | complete-box error | frame loss | inherited two-channel floor | direct enclosed floor |
|---|---:|---:|---:|---:|---:|
| (L^2) | (5.74300087146833\times10^{-6}) | (2.88349586081380\times10^{-20}) | (1.94675860513591\times10^{-37}) | (5.74300087146830\times10^{-6}) | (5.74300087146798\times10^{-6}) |
| rational (H^1) majorant | (1.41073748093610\times10^{-7}) | (2.62135987346709\times10^{-21}) | (1.76978055012355\times10^{-38}) | (1.41073748093607\times10^{-7}) | (1.41073748093579\times10^{-7}) |

All deciding fields are rational.  Floating generalized eigensolvers propose
candidate lower or upper bounds, but exact rational LDL tests accept them.

## 2. Arb extraction and normalization

For an Arb value with exact directed endpoints (a\le b), `_arb_box`
returns

\[
 c=\frac{a+b}{2},\qquad r=\frac{b-a}{2}.
\]

Thus ([c-r,c+r]=[a,b]) exactly as rational intervals.  No conversion through
binary floating point occurs.

The response-row multiplier is

\[
 \frac{\sqrt{2\sqrt2}}{n}.
\]

Consequently the sum of row outer products has coefficient

\[
 \left(\frac{\sqrt{2\sqrt2}}{n}\right)^2
 =\frac{2\sqrt2}{n^2},
\]

which is exactly the complete finite Gram normalization in the Stage-XII
checker.  The adversarial tests independently assemble a small (n=5) row
box and compare it with a fresh Arb evaluation of
`finite_neumann_two_port_gram`; the two outward enclosures overlap in every
entry.  This also checks even-mode selection and the central-target parity
normalization.

The Taylor remainder is propagated correctly.  The operator-norm remainder
is multiplied by (\sqrt n), using

\[
 |\mathbf 1^T E u_k|
 \le \lVert\mathbf1\rVert_2\lVert E\rVert_2\lVert u_k\rVert_2
 =\sqrt n\lVert E\rVert_2,
\]

then by the same response-row scale inside Arb before directed endpoints are
extracted.

## 3. Matched sensor and noise law

Let the rational centre response be (C\in\mathbb Q^{m\times2}) and choose
the two sensor rows

\[
 P=C^T.

\]

For a whitened (m)-channel modal observation, the induced two-channel noise
covariance and precision are

\[
 \Sigma=PP^T=C^TC,
 \qquad W=\Sigma^{-1}.

\]

The nominal matched response is (PC=C^TC), so exact rational arithmetic
gives

\[
 (PC)^T(PP^T)^{-1}(PC)=C^TC.

\]

The certificate therefore retains the entire nominal two-dimensional
information form.  The audit reconstructs all three identities directly
from the serialized rational matrices.  The inverse exists because the
centre response has rank two; singularity would be rejected by the exact
Gauss--Jordan inverse.

For a true response (R=C+E), entrywise radii propagate through the fixed
sensor exactly as an enclosure:

\[
 |P R-P C|=|PE|\le |P|\,\mathcal E.

\]

The direct two-channel certificate correctly uses this radius and the
induced precision (W); it does not whiten the noise a second time.

## 4. Projector identity and second-order loss

Define

\[
 \Pi=P^T(PP^T)^{-1}P
 =C(C^TC)^{-1}C^T.

\]

This is the Euclidean orthogonal projector onto
\(\operatorname{range}(C)\).  Hence

\[
 C^T(I-\Pi)=0,
\]

and the loss between the complete and matched true information forms is

\[
 R^TR-R^T\Pi R
 =R^T(I-\Pi)R
 =E^T(I-\Pi)E
 \preceq E^TE.
\]

This proves that the frame loss is genuinely second order in the response
enclosure radius.

There is an important absolute-value step after this identity.  If
\(|E|\le\mathcal E), it is **not** generally true that

\[
 E^TE\preceq\mathcal E^T\mathcal E.

\]

For example, (\mathcal E=(1,1)) and (E=(1,-1)) make the difference of
those two matrices indefinite.  What is true for every real vector (x) is

\[
 x^TE^TEx=\lVert Ex\rVert_2^2
 \le \lVert\mathcal E|x|\rVert_2^2
 =|x|^T\mathcal E^T\mathcal E|x|.

\]

Since (B=\mathcal E^T\mathcal E) is entrywise nonnegative and symmetric,

\[
 |x|^TB|x|
 \le \sum_i\left(\sum_j B_{ij}\right)x_i^2.

\]

The implementation does construct precisely this diagonal row-sum matrix
before comparing it to the source metric by exact LDL.  Therefore the
computed bound is valid.  However, the code comment and serialized
`identity` field jump directly from (E^TE) to the radius construction and
can invite the false Loewner interpretation above.  They should state the
two absolute-value inequalities explicitly.

## 5. Complete and inherited floors

The complete response box first certifies

\[
 -\delta_{\rm box}S
 \preceq R^TR-C^TC
 \preceq \delta_{\rm box}S.

\]

An exact rational LDL test also certifies

\[
 C^TC-L_0S\succ0.

\]

Thus the true complete response has floor at least

\[
 L_{\rm full}=L_0-\delta_{\rm box}.

\]

The projector loss certificate gives

\[
 R^T(I-\Pi)R\preceq\delta_{\rm frame}S,

\]

so the inherited matched-frame floor

\[
 L_{\rm matched}=L_0-\delta_{\rm box}-\delta_{\rm frame}

\]

is valid.  Subtracting the two errors is conservative but sound, even though
they arise from the same response uncertainty.  The independently generated
direct enclosed-design floor supplies a useful second route and agrees at
the displayed scale.

## 6. Rational (H^1) majorant

For source modes (k=1,2), the natural finite energy weights are

\[
 s_{n,k}=1+4n^2\sin^2\!\frac{k\pi}{2n}.

\]

Using (\sin x\le x),

\[
 s_{n,k}\le 1+(k\pi)^2.

\]

The elementary bound (\pi^2<10) then gives

\[
 1+\pi^2<11,
 \qquad
 1+4\pi^2<41.

\]

Therefore

\[
 S_{n,H^1}\preceq S_{H^1,\mathrm{cont}}
 \preceq\operatorname{diag}(11,41).

\]

A certified floor against the larger rational metric is also a floor of the
same size against either smaller metric.  The direction in the report is
correct.  The adversarial test repeats both strict comparisons with outward
Arb intervals rather than `math.sin` binary64 values.

## 7. Report-integrity gap

The nested `direct_two_channel_enclosed_design` reports are self-verifying:
`verify_enclosed_design_report` reconstructs their exact response boxes,
nominal certificate, robust floor, and noise fields.

There is no corresponding verifier for the top-level
`oig-neumann-matched-frame-v1` report.  In particular, after serialization a
consumer can alter any of the following without detection by the embedded
verifier:

- the full modal centre or radius;
- the matched sensor rows, covariance, response centre, or radius;
- the nominal complete floor;
- the complete-box error;
- the second-order frame loss;
- the inherited two-channel floor;
- the per-metric `passed` flags; or
- `overall_passed`.

Running the constructor itself still produces consistent values, so this is
not a counterexample to the mathematical theorem.  It is a proof-artifact
integrity gap and should be fixed before treating a saved JSON file as a
self-contained certificate.

### Required fix

Add `verify_neumann_matched_frame_report(report)` and call it before returning
the report.  At minimum it should:

1. validate the schema, shapes, nonnegative radii, declared model parameters,
   and exact rational encodings;
2. reconstruct (P=C^T), (\Sigma=PP^T), (PC), and
   (|P|\mathcal E);
3. reconstruct each complete response-box bound;
4. verify each claimed nominal floor directly by exact LDL;
5. reconstruct the diagonal second-order radius bound and its metric-relative
   comparison;
6. reproduce the robust complete and inherited matched floors;
7. run `verify_enclosed_design_report` on each nested direct certificate;
8. check each `passed` flag and `overall_passed`; and
9. preferably rerun `finite_modal_response_box` from the declared model
   parameters and compare its exact directed rational boxes to the serialized
   ones.  If this expensive step is optional, the report must distinguish
   algebraic self-verification from physical-model enclosure reproduction.

The new adversarial test automatically exercises tamper rejection when that
verifier becomes available; until then it is reported as skipped.

## 8. Scope verdict

The stated boundary is accurate.  The certificate concerns exactly:

- two source coordinates;
- the τ=1 finite Neumann model;
- an odd, exactly centred (n=345) grid;
- the declared response and Taylor-tail boxes; and
- two dense global linear sensors acting on a whitened modal-output field.

It does not prove that these global rows are local or directly realizable in
hardware, does not transfer dynamics outside the boxes, and does not cover a
τ interval, displaced target, even grid, larger source band, or full OIG
atlas.  No language in the current scope boundary improperly promotes this
finite declared experiment to a statement about physical reality.

## 9. Final verdict and test status

The normalization, Arb enclosure, matched covariance/precision, exact
information identity, projector reduction, second-order frame-loss bound,
exact rational floor comparisons, and rational-(H^1) direction all survive
the audit.  The theorem itself is valid within the stated scope.

The new adversarial suite is
`test_oig_neumann_matched_frame_adversarial.py`.  Its substantive controls
pass; the top-level tamper test is intentionally skipped until the required
verifier exists.  The original focused suite also passes.

Publication verdict: **mathematically sound, but add the top-level verifier
and clarify the absolute-value step before calling the serialized JSON a
self-verifying proof artifact.**
