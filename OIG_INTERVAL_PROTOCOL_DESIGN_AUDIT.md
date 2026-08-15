# Adversarial audit: interval protocol design

Date: 2026-08-14

Scope: `oig_interval_protocol_design.py` and
`test_oig_interval_protocol_design.py`, with the nominal engine treated as an
imported dependency.  This audit checks the entrywise response enclosure, its
metric-relative form bound, cost-weighted aggregation, the full-rank nominal
restriction, robust noise consequences, and independent report verification.

## Verdict

The mathematical response-box transfer and its cost-weighted aggregation are
sound.  The current independent verifier is not yet sound as a verifier of the
*composed* nominal-plus-interval claim: it does not link a box certificate's
centre or noise precision to the corresponding nominal protocol.  This permits
a report asserting a positive robust floor even when the response family
declared by its boxes has an exact blind direction.

The verifier also ignores every robust-noise field and the local schema/LDL
decision fields of each box certificate.  These are tamper-resistance gaps,
not defects in the generated values.

Publication or use as a proof-producing external verifier should wait for the
linkage defect and robust-noise checks to be fixed.  The construction itself
can continue to be used after in-process generation because the generator
builds the nominal protocol and its box from the same `EnclosedProtocol`.

**Post-audit resolution:** the external verifier now checks the per-box
schema and exact-LDL flag, requires every enclosure centre and noise precision
to equal its nominal protocol declaration, reconstructs both robust-noise
bounds, and validates the realized exposure. The original and adversarial
interval suites now pass all 10 tests, including every mutation described in
this audit.

## 1. Entrywise response-box theorem

Let the enclosed response be `R+D`, with `|D| <= E` entrywise, and let the
exact symmetric positive definite noise precision be `W`.  Then

```text
A_true - A
  = R^T W D + D^T W R + D^T W D,

|A_true-A|
  <= |R|^T |W| E + E^T |W| |R| + E^T |W| E
  = B
```

entrywise.  The implemented `B` is symmetric and nonnegative.  With
`H = diag(B 1)`, for every real `x`,

```text
|x^T(A_true-A)x|
  <= |x|^T B |x|
  <= x^T H x.
```

The final inequality follows termwise from
`2 |x_i x_j| <= x_i^2+x_j^2`; equivalently, `H-B` is the weighted graph
Laplacian of `B` when evaluated on `|x|`.

`_strict_form_upper` accepts `delta` only after exact rational LDL proves
`delta*S-H` positive definite.  Consequently

```text
-delta*S <= A_true-A <= delta*S
```

as quadratic forms.  The floating generalized eigensolver only proposes a
candidate and cannot make the theorem decision.  The exact-zero special case
is also sound.

An exhaustive exact corner check with a correlated precision matrix and a
nondiagonal source metric is included in
`test_oig_interval_protocol_design_adversarial.py` and passes.

Operational limitation: sufficiently extreme rational scalings can make the
floating proposal overflow or require more than the fixed 256 doublings.  That
causes a conservative failure to issue a certificate, not acceptance of a
false certificate.

## 2. General metric and cost aggregation

The nominal engine assigns budget shares `p_i`, positive costs `c_i`, and
physical weights `w_i=p_i/c_i`, so its unit-cost information is

```text
G = sum_i (p_i/c_i) A_i.
```

Applying each box inequality and summing gives

```text
G_true >= G - [sum_i (p_i/c_i) delta_i] S.
```

The wrapper computes exactly this bracket.  Subtracting the aggregate error
from the exact nominal generalized-floor lower bound is therefore correct.
The argument remains valid in the engine's full-rank quotient coordinates:
congruence by the quotient injection transfers both the information inequality
and the source metric.  The wrapper presently rejects every nonzero nominal
blind dimension, so there is no ambiguity about an uncertain activation of a
discarded direction.

The adversarial test suite includes unequal protocol costs and a nondiagonal
metric; the exact aggregate reproduces.

## 3. Required fix: bind every box to its nominal protocol

Severity: **blocking for independent verification**.

`verify_enclosed_design_report` reconstructs a box certificate from

- `bound["response_centre_exact"]`,
- `bound["response_radius_exact"]`, and
- `bound["noise_precision_exact"]`,

but never compares the first and third matrices with the corresponding base
protocol row's `response_exact` and `noise_precision_exact`.

Concrete exploit:

1. Generate a zero-radius report for the two nominal responses `[1,0]` and
   `[0,1]`.  It has a positive nominal and robust floor.
2. Replace the first box certificate by a freshly valid zero-radius box centred
   at `[0,0]`.
3. Keep the nominal report and all aggregate fields unchanged.  Both boxes
   still have `delta=0`.
4. The current verifier returns `passed: true`, although the response family
   declared by the boxes is blind in the first source direction.

Changing only the box precision from `1` to `1/100` similarly passes without
being included in the nominal-to-physical error budget.

Required verifier checks, using exact parsed matrices rather than descriptive
text, are:

```text
box response centre == nominal row response
box noise precision  == nominal row noise precision
```

These checks must occur for each paired protocol before the aggregate floor is
accepted.  They also restore the intended uncertain-blind restriction: a
report cannot retain a full-rank nominal frame while silently declaring a
different, blind collection of interval centres.

## 4. Required fix: verify the local box decision fields

Severity: **high-integrity report gap**.

The verifier recomputes the three numerical box fields, but it accepts a box
whose `schema_version` is unknown or whose `exact_ldl_decision` is false.
Require:

```text
schema_version == "oig-response-box-form-bound-v1"
exact_ldl_decision is True
```

The free-text `meaning` field need not be part of the theorem verifier.

## 5. Required fix: reconstruct robust-noise consequences

Severity: **high-integrity report gap**.

When the robust physical floor is positive, the generator emits two rational
Gaussian-error bounds.  The verifier presently accepts all of the following:

- deletion of the entire robust-noise block;
- changing either error upper bound to `0/1`;
- changing the amplitude without changing either bound;
- changing the integer-realization exposure arbitrarily.

For a positive robust floor `lambda`, the verifier should require the block and
reconstruct

```text
4 / (8 + N * amplitude^2 * lambda)
```

for both exposures.  It should require:

- `amplitude_exact` equals the amplitude in the nominal noise record;
- the continuous exposure equals the nominal requested exposure;
- `integer_realization_exposure` is a strict JSON integer equal to the nominal
  realized budget multiplier;
- both stored rational error bounds equal their reconstructions.

It is also preferable to reject a robust-noise block when the robust floor is
nonpositive.  At minimum, such a block must never be treated as certified.

The nominal verifier currently permits the amplitudes in its approximate and
integer noise rows to differ if both rows are internally recomputed.  The
interval verifier can close that inherited composition gap by requiring its
amplitude to equal both nominal amplitudes; strengthening the nominal verifier
itself would be cleaner.

## 6. Test evidence

Command:

```text
python -m unittest -v \
  test_oig_interval_protocol_design.py \
  test_oig_interval_protocol_design_adversarial.py
```

Before fixes:

- 4 original tests pass;
- 2 new positive mathematical controls pass;
- 8 adversarial subcases fail because the verifier accepts the mutation:
  centre linkage, precision linkage, two local decision fields, and four
  robust-noise mutations.

The failing adversarial assertions are intentional regression controls.  They
should all pass after the verifier is hardened.

## 7. Minimal repair order

1. Link each enclosure centre and precision to its nominal protocol row.
2. Require each box schema and exact-LDL flag.
3. Require and exactly reconstruct the robust-noise block when the robust
   floor is positive; reject it when nonpositive.
4. Run both interval test modules and the full protocol-engine suite.

No change to the response-box inequality, metric-relative LDL comparison,
cost-weighted aggregation, or the conservative full-rank nominal restriction
is required by this audit.
