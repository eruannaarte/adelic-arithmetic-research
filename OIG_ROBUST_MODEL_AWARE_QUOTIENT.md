# Operational Information Geometry — a robust model-aware quotient layer

## Exact response tubes, secant loss, tangent angles, and uncertain nominal nulls

**Research status:** finite-dimensional theorems proved below; exact-rational
reference implementation and adversarial tests included; not peer reviewed

## Abstract

The existing protocol engine solves an ambient E-optimal design problem after
removing the exact common response kernel.  That is necessary but not
sufficient for a model-aware experiment.  A positive information floor on the
quotient does not show that the declared model or query survives the discarded
directions, and an interval response family can activate a nominal null without
making that activation reliable.

This note supplies the missing finite-dimensional layer.  For an exact
rational response \(H\), source metric \(S\succ0\), and model secant \(v\), it
constructs the \(S\)-minimum representative

\[
 P_Sv=S^{-1}C^T(CS^{-1}C^T)^{-1}Cv,
\]

where \(C\) is a row basis of \(H\).  Its squared norm is the exact rational
quotient distance

\[
 d_Q(v)^2=(Cv)^T(CS^{-1}C^T)^{-1}Cv.
\]

Equal source tubes of radius \(\rho\), together with range-valued data noise
of quotient radius \(\varepsilon_Q\), therefore have exact separation gap

\[
 \boxed{(d_Q(v)-2\rho-2\varepsilon_Q)_+.}
\]

Finite secant families inherit an exact squared separation ratio.  A rational
tangent basis \(T\) has smallest tangent--kernel angle determined by the
generalized form pair

\[
 T^TC^T(CS^{-1}C^T)^{-1}CT,\qquad T^TST.
\]

Exact LDL inequalities certify a lower bound on \(\mu^2\), hence the sharp
linearized source-mismatch amplification \(1/\mu\).  The calculation uses the
declared source metric; it is not silently Euclidean.

For an entrywise response tube \(|H_{\rm true}-H|\le E\), the centre
\(H_{\rm true}=H\) remains admissible.  Consequently no positive uniform
information floor may ever be credited to a nominal blind direction merely
because another member of the box activates it.  Task irrelevance requires
either that the query kills the null or that an exhaustive, provenance-backed
model-secant theorem excludes its collisions.  Full-family null preservation
is a different fact: it makes the quotient structurally stable, but cannot
make a query that depends on the null recoverable.  If preservation fails, the
blind amplitude must be bounded and its leakage treated as additional output
uncertainty.

The implementation exposes a partial model-geometry design certificate.  It
does not invent a scalar combination of ambient information, global secant
separation, local tangent angle, interval information loss, and blind leakage;
those quantities have different meanings and units.  The existing interval
engine's information-form loss remains a separate certificate in this version.

---

## 1. Exact minimum-cost quotient

Let \(X=\mathbb R^d\) carry the source norm

\[
 \|x\|_S^2=x^TSx,
 \qquad S\succ0,
\]

and let \(H:X\to Y\) be a finite response.  Choose any full-row-rank matrix
\(C\) with the same row space as \(H\).  Put

\[
 S_Q=(CS^{-1}C^T)^{-1},
 \qquad J=S^{-1}C^TS_Q,
 \qquad P_S=JC.
 \tag{1.1}
\]

Then \(CJ=I\), \(P_S^2=P_S\), and

\[
 \ker P_S=\ker H=:K.
\]

Moreover \(P_Sx\) is the unique minimum-\(S\)-norm element among all vectors
with the same response as \(x\).  Hence

\[
 \boxed{
 \operatorname{dist}_S(x,K)^2
 =\|P_Sx\|_S^2
 =(Cx)^TS_Q(Cx).}
 \tag{1.2}
\]

All matrices in (1.1)--(1.2) are rational when \(H\) and \(S\) are rational.
The implementation constructs them by exact row reduction and inversion.

### Metric warning

The ordinary Euclidean row-space projector is correct only when \(S=I\).
For example, with

\[
 H=(1\;1),\qquad S=\operatorname{diag}(1,4),\qquad v=(1,0)^T,
\]

the declared quotient distance squared is \(4/5\), while the Euclidean
projection would give \(1/2\).  The test suite fixes this as a regression
counterexample.

---

## 2. Exact response-tube overlap

For a latent centre \(p\), source mismatch radius \(\rho\), and quotient-norm
data radius \(\varepsilon_Q\), define

\[
 \mathcal T_p=Hp+HB_S(\rho)+B_Q(\varepsilon_Q),
 \tag{2.1}
\]

where the last ball lies in \(\operatorname{ran}H\) and uses the quotient norm
induced by \(S\).

### Theorem 2.1 — exact pair gap

For \(v=p-p'\),

\[
 \boxed{
 \operatorname{dist}_Q(\mathcal T_p,\mathcal T_{p'})
 =\bigl(d_Q(v)-2\rho-2\varepsilon_Q\bigr)_+.}
 \tag{2.2}
\]

In particular, the tubes overlap exactly when

\[
 d_Q(v)^2\le4(\rho+\varepsilon_Q)^2.
 \tag{2.3}
\]

#### Proof

The image \(HB_S(r)\) is exactly a radius-\(r\) quotient ball.  The difference
of two symmetric radius-\(r\) balls is the radius-\(2r\) ball.  Distance
between two equal balls in a normed vector space is the positive part of the
centre distance minus the two radii.  Equation (1.2) supplies that centre
distance. \(\square\)

The executable certificate decides (2.3) by comparing exact rational squares;
no square root or binary float decides overlap.  Directed dyadic square-root
bounds are returned only to display a separation-gap interval.

When source mismatch alone causes overlap, the implementation also returns an
exact witness.  If \(u=P_Sv\), choose

\[
 e=-u/2,\qquad e'=u/2.
 \tag{2.4}
\]

Then \(H(p+e)=H(p'+e')\) and each mismatch has squared norm \(d_Q(v)^2/4\).

### Ordinary output noise

If output noise is instead bounded in an independently declared norm
\(\|y\|_W^2=y^TWy\), simultaneous source and output balls do not generally
reduce to one quotient ball.  The implementation therefore distinguishes:

- exact overlap from a source witness;
- exact overlap from output noise alone;
- exact decisions when either noise radius is zero;
- conservative disjointness from

  \[
  \|Hv\|_W>
  2\rho\|H\|_{S\to W}+2\varepsilon;
  \tag{2.5}
  \]

- and an honest undecided result when (2.5) does not close.

The operator gain in (2.5) is bounded by an exact rational form inequality

\[
 H^TWH\prec\delta S.
\]

An undecided result is not reported as overlap.  Exact general resolution
with both radii positive is a convex trust-region calculation and belongs in
a later interval/SOCP layer.

---

## 3. Finite quotient-secant certificates

For a nonzero secant \(v\), define

\[
 \alpha(v)^2=
 \frac{d_Q(v)^2}{\|v\|_S^2}.
 \tag{3.1}
\]

For an explicitly supplied finite family \(\mathcal D\), every value in
(3.1) is rational and so is

\[
 \alpha_{\mathcal D}^2=\min_{v\in\mathcal D}\alpha(v)^2.
 \tag{3.2}
\]

The family is separated precisely when every numerator is positive.  Under
equal source and quotient-noise tubes, each pair loses exactly
\(2\rho+2\varepsilon_Q\) of unnormalized quotient separation, as in (2.2).

This is a global model theorem only when \(\mathcal D\) is an exhaustive
difference set.  Sampling secants from a continuum cannot establish a global
floor.  It remains useful as a proof object for a finite codebook, a finite
lattice window, a rigorously reduced extremal list, or adversarial regression
cases.

### Counterexample to quotient E-optimality alone

Take

\[
 H=(1\;0),\qquad S=I,
 \qquad A=H^TH.
\]

The one-dimensional observable quotient has exact E-optimal floor one.  Yet a
model containing the secant \((0,1)^T\) has an exact collision.  The combined
checker returns the positive information floor and rejects the model target.
This is the smallest example showing why “positive after quotienting” is not
the same theorem as latent-model identifiability.

---

## 4. Tangent--kernel angle in the declared metric

Let the columns of \(T\in\mathbb R^{d\times k}\) form a tangent basis.  From
(1.2), for tangent coordinates \(a\),

\[
 \|P_STa\|_S^2=a^TNa,
 \qquad
 \|Ta\|_S^2=a^TDa,
 \tag{4.1}
\]

where

\[
 N=T^TC^TS_QCT,
 \qquad D=T^TST.
 \tag{4.2}
\]

Therefore

\[
 \boxed{
 \mu^2=\lambda_{\min}(N,D)
 =\inf_{0\ne v\in\operatorname{ran}T}
 \frac{\operatorname{dist}_S(v,K)^2}{\|v\|_S^2}.}
 \tag{4.3}
\]

This is the squared sine of the smallest principal angle in the \(S\)-metric.
If \(CT\) loses column rank, exact row reduction returns tangent coordinates
and an ambient tangent vector in \(K\), proving \(\mu=0\).  Otherwise a
floating generalized eigensolver proposes \(L\), but the theorem field is
accepted only after exact LDL proves

\[
 N-LD\succ0.
 \tag{4.4}
\]

For a one-dimensional tangent the ratio is exact rational.  For larger
tangents the certificate returns an exact rational lower on \(\mu^2\), a
Rayleigh upper, and a directed rational upper on \(1/\mu\).

By AO VI's tangent experiment, the exact linearized adversarial mismatch
radius is

\[
 R^*_{\rm tan}(p,\rho)=\rho/\mu(p).
 \tag{4.5}
\]

The tangent theorem is local.  It neither replaces a global secant theorem
nor controls boundary strata without additional analysis.

---

## 5. Nominally blind directions under response uncertainty

Let

\[
 H_{\rm true}=H+D,
 \qquad |D|\le E
 \tag{5.1}
\]

entrywise, with independent symmetric intervals, and let columns of \(K_0\)
span \(\ker H\).

### Theorem 5.1 — no information from possible activation

The worst-case information floor on the nominal blind subspace is zero.

#### Proof

The centre perturbation \(D=0\) satisfies (5.1).  At that admissible response,
every vector in \(\ker H\) remains exactly blind. \(\square\)

Thus interval uncertainty must never be used as a beneficial regularizer.
Possible activation is not guaranteed observation.

### Theorem 5.2 — exact preservation test

Every member of (5.1) preserves the nominal blind subspace if and only if

\[
 \boxed{E|K_0|=0.}
 \tag{5.2}
\]

#### Proof

The entrywise inequality \(|DK_0|\le E|K_0|\) proves sufficiency.  If an entry
of \(E|K_0|\) is positive, one allowed perturbation entry can be selected with
the sign of the corresponding nonzero basis coefficient, producing a nonzero
entry of \(DK_0\). \(\square\)

### Bounded leakage rule

If (5.2) fails but the nominal blind component is bounded, write it as
\(K_0z\) with

\[
 z^T(K_0^TSK_0)z\le\beta^2.
\]

Set \(M=E|K_0|\).  Then

\[
 \|DK_0z\|_W^2
 \le |z|^TM^T|W|M|z|.
 \tag{5.3}
\]

The nonnegative form on the right is dominated by the diagonal matrix of its
row sums.  Exact LDL supplies \(\delta\) such that this diagonal form is at
most

\[
 \delta K_0^TSK_0.
 \tag{5.4}
\]

Therefore blind leakage has output radius at most

\[
 \boxed{\beta\sqrt\delta.}
 \tag{5.5}
\]

It must be added to the response/noise tube.  If the blind component is
unbounded and (5.2) fails, the nominal quotient is not a uniform predictive
object over the response box.

### Query relevance and family stability are separate obligations

A nominal null is irrelevant to a recovery task only after at least one of
these has been proved exactly:

1. **Query factorization:** \(\ker H\subseteq\ker L\), checked by \(LK_0=0\).
2. **Model restriction:** an exhaustive model difference set has no nonzero
   member in \(\ker H\).

The second route requires an explicit `model_secants_exhaustive=true`
declaration and a nonempty provenance string identifying why the supplied
finite family is exhaustive.  Merely testing a favourable finite sample is
not a theorem about omitted secants.

Family preservation, checked by (5.2), answers a different question: whether
one fixed quotient remains structurally valid throughout the response box.
It does not make a query depending on \(K_0\) recoverable.  If preservation
fails, query insensitivity alone is also insufficient to control uncertain
blind leakage: the blind amplitude must be explicitly bounded and (5.5)
propagated into the output budget.

---

## 6. Optional rational-lattice trichotomy

For a rational lattice basis \(B\) and rational response \(H\), exact row
reduction decides the AO-I trichotomy for \(HB\).

- If \(\operatorname{rank}(HB)<\operatorname{rank}B\), its rational
  nullspace contains a nonzero rational vector.  Clearing denominators gives
  an exact integer collision witness.
- If \(HB\) has full column rank, exact LDL gives \(L>0\) with

  \[
  B^TH^TWHB\succeq LI.
  \]

  Every nonzero integer coordinate vector has norm at least one, so the image
  lattice has separation at least \(\sqrt L\).

The real-rank-deficient but integer-kernel-free middle regime cannot occur for
fully rational inputs: rational rank deficiency already gives an integer
collision.  For an irrational response, the companion logical interface can
return the middle regime only when given a reference to an external exact
integer-kernel-free proof.  A small floating residual is expressly rejected as
a substitute.

---

## 7. The combined design target

For a fixed active protocol support, a model-aware certificate should retain
the vector

\[
 \boxed{
 \left(
 z_{\rm info},
 \alpha_{\rm sec}^2,
 \min_p\mu(p)^2,
 \Delta_{\rm box},
 \delta_{\rm blind}
 \right),}
 \tag{7.1}
\]

where:

- \(z_{\rm info}\) is the E-optimal information floor on the nominal quotient;
- \(\alpha_{\rm sec}\) is a global or declared finite quotient-secant floor;
- \(\mu\) is the tangent--kernel angle;
- \(\Delta_{\rm box}\) is the response-box loss in the information form; and
- \(\delta_{\rm blind}\) is the bounded null-leakage gain.

There is no canonical scalar minimum of (7.1): the entries have different
units and operational meanings.  A design engine should use declared
thresholds, a Pareto order, or a loss function tied to a specific task.  The
full future optimizer should report this vector rather than claiming a
universal scalar optimum.  The present `certify_combined_model_design` is a
partial geometry audit: it reports quotient information, finite secants,
tangent angles, task relevance, and blind-leakage safety.  It explicitly does
**not** compute \(\Delta_{\rm box}\); that field must be imported from and
linked to the interval-response engine in a later integration.

The exact obligations are:

1. positive aggregate information on the nominal quotient;
2. no collision in the declared secant family;
3. transversality of every declared tangent;
4. satisfaction of the nominal-null task-relevance rule; and
5. either full-family quotient preservation or an explicit blind-amplitude
   bound whose leakage is carried as output uncertainty.

---

## 8. Integration audit of the existing engines

The following are concrete failure modes to prevent when this layer is joined
to the E-optimal and interval-response engines.

1. **A quotient floor is not a latent-model theorem.**  The E-optimal engine
   correctly optimizes after removing the common kernel.  A separate
   secant/query check is still mandatory, as the two-dimensional counterexample
   in Section 3 shows.

2. **The kernel depends discontinuously on active support.**  Any protocol
   whose rationalized design weight becomes zero must be removed before the
   common row space is recomputed.  Rows from zero-use protocols cannot be
   retained merely because they appeared in the candidate library.

3. **Possible interval activation is not reliable information.**  A symmetric
   response box contains its nominal centre.  The robust lower floor on a
   nominal blind direction remains zero even if most perturbed matrices see
   it.

4. **A moving quotient is not one common experiment.**  Recomputing
   \(\ker H_{\rm true}\) separately for each interval realization changes the
   equivalence relation being certified.  Use a fixed declared quotient when
   (5.2) holds; otherwise bound the blind amplitude and transfer its leakage
   into the output tube.

5. **The interval information loss and source-tube loss are different.**
   The existing bound on
   \((H+D)^TW(H+D)-H^TWH\) transfers an information floor.  It does not prove
   response-set disjointness under latent source mismatch.  Conversely,
   quotient-tube overlap does not by itself quantify Gaussian Fisher
   information.

6. **Output noise norm and quotient norm must be labelled.**  The exact linear
   erosion law applies to range-valued noise bounded in the induced quotient
   norm.  Ordinary sensor noise in a declared \(W\)-norm uses the raw-tube
   criterion or a separate trust-region certificate.

7. **The source metric controls the projection.**  Tangent angles and secant
   distances must use \(P_S\), not a Euclidean pseudoinverse, unless \(S=I\).

8. **Local and global certificates cannot substitute for one another.**  A
   positive tangent angle is local.  A finite secant list is global only for
   a genuinely finite or exhaustively reduced model.

9. **Aggregate information must respect the nominal kernel.**  Before applying
   the quotient information certificate, the combined checker requires the
   nominal aggregate information to annihilate the declared blind basis.
   This catches mismatched response/design artifacts.

10. **Cost weights affect information but not merely structural rank.**  Every
    strictly positive protocol weight contributes its response kernel to the
    common intersection, while its magnitude and cost scale Fisher
    information.  Structural and metric calculations should not reuse one
    another's weights implicitly.

11. **Exact rank must remain exact.**  Weak nonzero directions may be expensive
    or irrelevant, but a floating singular-value threshold cannot turn them
    into a structural null.  Exact rational row reduction decides the current
    finite artifacts.

12. **The lattice middle regime is Diophantine.**  For irrational maps,
    real-rank deficiency plus a numerical failure to find an integer collision
    is not proof of injectivity.  The external integer-kernel premise must be
    explicit.

---

## 9. Public executable interface

The reference implementation is `oig_robust_model_quotient.py`.  Its public
entry points are:

- `exact_model_quotient` and `quotient_distance_squared`;
- `certify_quotient_tube_pair` for the exact quotient-ball identity;
- `certify_response_tube_pair` for ordinary output-noise overlap/disjointness;
- `certify_finite_quotient_secants`;
- `certify_tangent_kernel_angle`;
- `certify_nominal_null_relevance`;
- `certify_nominal_blind_uncertainty`;
- `certify_combined_model_design`;
- `certify_rational_lattice_trichotomy`; and
- `classify_lattice_trichotomy_from_exact_predicates` for theorem composition
  with an external irrational integer-kernel proof.

Every certificate embeds its applicable original exact matrices, vectors,
radii, and precision; finite model-wide claims also embed their declared
exhaustiveness flag and provenance.  `verify_robust_model_report`
dispatches by schema, reconstructs the complete certificate from those fields,
and performs a strict field- and type-complete comparison.  In particular it
rejects extra fields, booleans substituted for JSON integers, altered
declarations, and theorem-field tampering.

Floating eigensolvers are optional sharpeners rather than range-critical
dependencies.  If a rational form is too large for binary64, the upper-form
certificate starts from
\(\operatorname{tr}(D^{-1}N)+1\), while the positive lower-form certificate
starts from
\(1/(\operatorname{tr}(N^{-1}D)+1)\).  Both candidates are accepted only
after the corresponding exact LDL inequality succeeds.

`verify_combined_model_design_report` is the strict combined-certificate entry
point.  The demo additionally exposes `verify_robust_model_demo_report`, which
verifies all five component schemas and checks that their response, source
metric, output metric, secant, tangent, response-radius, and query declarations
refer to one coherent experiment.

`oig_robust_model_quotient_demo.py` gives one compact pair/tangent/null example
and prints a reconstructible JSON record.  Together, the primary and
independent adversarial suites include:

- a boundary tube collision with an exact witness;
- exact twofold tube erosion;
- a positive quotient information floor hiding a model collision;
- a tangent lying exactly in the observation kernel;
- the non-Euclidean metric counterexample;
- uncertain activation whose worst-case information remains zero;
- all three nominal-null relevance decisions;
- bounded blind leakage;
- rational integer collision and stable-lattice cases; and
- conditional selection of AO-I's unstable-but-injective middle regime.

Reproduce with:

    python oig_robust_model_quotient_demo.py
    python oig_robust_model_quotient_demo.py --output /tmp/robust-demo.json
    python oig_robust_model_quotient_demo.py --verify /tmp/robust-demo.json
    python -m unittest -v test_oig_robust_model_quotient.py
    python -m unittest -v test_oig_robust_model_quotient_adversarial.py

At the time this note was frozen, all 39 primary tests and all 13 independent
adversarial controls passed.  These include JSON round-trip verification,
theorem and declaration tampering, strict-type and extra-field rejection,
embedded-verification tampering, huge-rational overflow, coarse directed-root
bounds, and an individually valid but cross-component-incoherent demo
substitution.

---

## 10. The next integration theorem

The immediate next target is an active-support robust optimizer.  For every
rationalized candidate support it should:

1. recompute the exact common row space;
2. reject query- or model-relevant kernel collisions;
3. certify the nominal/interval E-optimal floor;
4. certify a global analytic or exhaustive finite secant floor;
5. cover the relevant tangent family, including boundary strata; and
6. propagate bounded blind leakage into the same physical output-noise budget.

Only after those steps should candidates be compared by declared thresholds
or a task-specific loss.  This would turn the current proof-producing
protocol engine into a genuinely model-aware robust design engine rather than
an ambient quotient optimizer with robustness appended afterward.
