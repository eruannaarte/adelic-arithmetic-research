# Structured additive nuisance certificates

## Exact finite-zonotope support, metric separation, and countable-tail transfer

**Status:** theorem note with an exact-rational self-verifying implementation

**Companion artifacts:** `oig_structured_nuisance.py` and
`test_oig_structured_nuisance.py`

**Mathematical sources:** the common-box zonoid, quotient, and remote-aware
primal-dual identities developed in Arithmetic Observability VIII--X

## 1. Purpose

Partially observed systems often contain a nuisance that is not arbitrary
entrywise noise.  A small collection of shared hidden coefficients can move
many observed coordinates together.  Preserving those correlations produces
the finite zonotope

\[
 \mathcal Z_F
 =\{Vx:|x_j|\le d_j,\ 1\le j\le m\},
 \tag{1.1}
\]

where the columns \(v_j\) of \(V\) are fixed response directions.  The
module certifies the distance between this structured additive nuisance and
a fixed query-response difference, optionally after profiling a further
linear nuisance span.

The certificate is designed to compose with the exact-rational protocol
engine.  Its observation norm is induced by an exact positive-definite noise
precision matrix \(\Omega\):

\[
 \|y\|_\Omega^2=y^T\Omega y.
 \tag{1.2}
\]

All reported theorem endpoints are rational.  Floating-point optimization is
neither required nor trusted.  An external optimizer may propose witnesses,
but the checker reconstructs their feasibility, support values, primal and
dual bounds, and gap exactly.

## 2. Exact support of a finite zonotope

### Theorem 2.1 -- finite support and an attaining point

For every covector \(u\in\mathbb R^r\),

\[
 \boxed{
 h_{\mathcal Z_F}(u)
 =\max_{z\in\mathcal Z_F}u^Tz
 =\sum_{j=1}^m d_j|u^Tv_j|.}
 \tag{2.1}
\]

The maximum is attained by

\[
 x_j^*
 =d_j\operatorname{sign}(u^Tv_j)
 \tag{2.2}
\]

at every nonzero pairing, with any admissible coefficient when the pairing
vanishes.

#### Proof

Every feasible coefficient obeys

\[
 u^TVx=\sum_jx_j(u^Tv_j)
 \le\sum_jd_j|u^Tv_j|.
\]

The signs in (2.2) attain all summands simultaneously.  □

The implementation stores the exact pairings, maximizing coefficients,
exposed point, and support.  It verifies \(u^TVx^*=h_{\mathcal Z_F}(u)\)
using `Fraction` arithmetic.

## 3. Point and query-response separation

Let \(B\in\mathbb Q^{r\times p}\) describe an additive nuisance subspace and
let \(q\in\mathbb Q^r\) be the fixed query-response difference.  Define

\[
 d
 =\inf_{\alpha\in\mathbb R^p,\ z\in\mathcal Z_F}
 \|q+B\alpha-z\|_\Omega.
 \tag{3.1}
\]

When \(p=0\), this is ordinary point-to-zonotope distance.  When \(p>0\), it
is the quotient or query-response separation after every additive direction
in \(\operatorname{range}(B)\) has been profiled out.

### Theorem 3.1 -- exact rational primal and norm-dual bracket

Choose any rational primal coefficients \(x\) with

\[
 |x_j|\le d_j
\]

and any rational \(\alpha\).  Put

\[
 r=q+B\alpha-Vx.
 \tag{3.2}
\]

Then

\[
 d^2\le r^T\Omega r.
 \tag{3.3}
\]

Choose any nonzero rational dual covector \(u\) satisfying

\[
 B^Tu=0.
 \tag{3.4}

\]

Then

\[
 \boxed{
 d^2\ge
 \frac{\bigl(u^Tq-h_{\mathcal Z_F}(u)\bigr)_+^2}
      {u^T\Omega^{-1}u}.}
 \tag{3.5}

\]

For \(u=0\), the lower bound is defined to be zero.

#### Proof

For every feasible \((\alpha,z)\), orthogonality gives

\[
 u^T(q+B\alpha-z)
 =u^Tq-u^Tz
 \ge u^Tq-h_{\mathcal Z_F}(u).
\]

Weighted Cauchy--Schwarz gives

\[
 u^Ty
 \le\sqrt{u^T\Omega^{-1}u}\sqrt{y^T\Omega y}.
\]

Take the positive part, take the infimum over \((\alpha,z)\), and square.  The primal
bound follows by evaluating one feasible pair.  □

Equation (3.5) is scale invariant in the dual direction and contains no
square root in its serialized form.  This is the principal positive-
separation certificate used by the module.

If two response fibres receive independent adversarial errors of
\(\Omega\)-norm at most \(\varepsilon\), they remain disjoint whenever

\[
 \varepsilon^2<\frac{d_{\rm lower}^2}{4}.
 \tag{3.6}

\]

The JSON reports this rational critical-radius square.  Strict inequality is
essential at the boundary.

## 4. Generalized squared dual and exact gap identity

For \(z=Vx\), define

\[
 \begin{aligned}
 P(\alpha,z)
 &=\frac12\|q+B\alpha-z\|_\Omega^2,\\
 D(u)
 &=u^Tq-h_{\mathcal Z_F}(u)
   -\frac12u^T\Omega^{-1}u,
 \qquad B^Tu=0.
 \end{aligned}
 \tag{4.1}

\]

### Theorem 4.1 -- metric primal-dual gap

Every primal-feasible \((\alpha,z)\) and dual-feasible \(u\) satisfy

\[
 \boxed{
 P(\alpha,z)-D(u)
 =\frac12
 \|r-\Omega^{-1}u\|_\Omega^2
 +h_{\mathcal Z_F}(u)-u^Tz
 \ge0.}
 \tag{4.2}

\]

#### Proof

Use \(q=r-B\alpha+z\) and \(u^TB=0\), then expand

\[
 \frac12(r-\Omega^{-1}u)^T
 \Omega(r-\Omega^{-1}u).
\]

The remaining term is nonnegative by the definition of the support
function.  □

Zero gap certifies that the serialized primal witness and the *squared-dual*
witness attain the same optimum.  The scale-invariant norm dual can also close
the distance bracket with a differently scaled direction; the implementation
therefore records squared-dual gap closure separately from exact equality of
the final distance lower and upper bounds.  A positive squared-dual gap is not
an optimizer claim.

## 5. Countably generated zonoid tails

Let the full nuisance body be

\[
 \mathcal Z
 =\mathcal Z_F+
 \left\{
   \sum_{k>M}x_kv_k:|x_k|\le d_k
 \right\},
 \qquad
 \sum_{k>M}d_k\|v_k\|_2<\infty.
 \tag{5.1}

\]

The omitted response is a compact countably generated zonoid.  Suppose an
external analytic argument proves the directional support bound

\[
 U_{\rm tail}(u)
 \ge\sum_{k>M}d_k|u^Tv_k|.
 \tag{5.2}

\]

Then Theorem 3.1 becomes

\[
 \boxed{
 d_{\rm full}^2\ge
 \frac{\bigl(u^Tq-h_{\mathcal Z_F}(u)-U_{\rm tail}(u)\bigr)_+^2}
      {u^T\Omega^{-1}u}.}
 \tag{5.3}

\]

The squared-dual value becomes

\[
 D_U(u)=u^Tq-h_{\mathcal Z_F}(u)-U_{\rm tail}(u)
 -\frac12u^T\Omega^{-1}u.
 \tag{5.4}

\]

For the finite primal witness with all remote coefficients set to zero, the
exact conservative gap is

\[
 \boxed{
 P-D_U
 =\frac12\|r-\Omega^{-1}u\|_\Omega^2
 +h_{\mathcal Z_F}(u)-u^TVx
 +U_{\rm tail}(u).}
 \tag{5.5}

\]

The interface accepts either of two exact rational premises.  An omitted
premise is represented by JSON `null`; it is never interpreted as a proved
zero remainder.

1. A direction-specific value \(U_{\rm dir}(u)\) proved by an external
   analytic certificate.
2. A norm remainder

   \[
   \sum_{k>M}d_k\|v_k\|_2\le R_M.
   \tag{5.6}
   \]

   This implies the fully rational coarse bound

   \[
   U_{\rm tail}(u)
   \le R_M\|u\|_2
   \le R_M\|u\|_1.
   \tag{5.7}
   \]

When both premises are declared, the implementation uses their minimum.  When
only one is declared, it uses that bound directly.

The finite verifier checks all algebra downstream of the declared remainder,
including the minimum, dual value, gap, and separation endpoints.  It cannot
prove the analytic premise (5.2) or (5.6) from a JSON file that does not
contain the omitted infinite generator sequence.  The report labels that
boundary explicitly and requires a provenance string for every declared tail
premise, including a claimed exact-zero remainder.

## 6. Why an entrywise response box can be much weaker

The coordinatewise outer box of (1.1) has radii

\[
 e_i=\sum_jd_j|V_{ij}|.
 \tag{6.1}

\]

Its support is

\[
 h_{\rm box}(u)=\sum_i e_i|u_i|
 \ge h_{\mathcal Z_F}(u).
 \tag{6.2}

\]

The inequality can be strict because the box forgets that the same
coefficient \(x_j\) moves several observed coordinates together.  For the
single generator

\[
 v_1=(1,1)^T,
 \qquad d_1=1,
 \qquad u=(1,-1)^T,
\]

the exact structured support is zero, while the entrywise-box support is two:

\[
 h_{\mathcal Z_F}(u)=|u^Tv_1|=0,
 \qquad h_{\rm box}(u)=2.
 \tag{6.3}

\]

The executable includes this as a pinned control, and the tests verify the
strict rational gap.  It is the simplest demonstration of why structured
additive nuisance should not be replaced automatically by independent entry
uncertainty.

## 7. Exact report verification

The schema is

```text
oig-structured-additive-nuisance-v1
```

Each certificate serializes:

- the exact query response, finite generator matrix, coefficient radii,
  nuisance basis, and observation precision;
- rational primal zonotope and nuisance coefficients;
- a rational dual direction;
- every generator pairing, support-maximizing sign, and exposed point;
- the declared norm and directional tail remainders with provenance;
- primal residual, subspace orthogonality, support slack, metric dual
  representer, squared-dual value, norm-dual lower square, primal upper
  square, and gap decomposition; and
- exact Boolean conclusions and a narrow scope boundary.

`verify_structured_nuisance_report` parses canonical rational strings,
rejects binary floats and malformed dimensions, reconstructs the complete
payload independently, compares JSON types strictly, and checks an embedded
verification block when present.  Reports emitted by the certificate builder
include that block.  Mutations of a floor, support, precision entry,
canonical fraction, theorem flag, or verification flag are rejected by the
adversarial tests.

## 8. Pinned demonstrations

Run

```bash
python oig_structured_nuisance.py \
  --output /tmp/oig_structured_nuisance_demo.json
python oig_structured_nuisance.py \
  --verify /tmp/oig_structured_nuisance_demo.json
python -m unittest -v test_oig_structured_nuisance.py
python -m unittest -v test_oig_structured_nuisance_adversarial.py
```

The output contains four small controls.

1. An exact point-to-rectangle projection with
   \(d^2=17/4\).
2. An exact query-response quotient after profiling one additive direction,
   with \(d^2=1\).
3. A finite prefix plus declared countable-tail directional remainder, with
   the rigorous bracket

   \[
   \frac{1521}{400}\le d^2\le5.
   \]

4. The correlation example (6.3), where the structured and entrywise-box
   supports are respectively zero and two.

A separate weighted test uses
\(\Omega=\operatorname{diag}(2,3)\) and closes both primal-dual routes at

\[
 d^2=\frac{35}{4}.
\]

## 9. Scope boundary

This theorem covers **additive structured nuisance with fixed response
directions**.  It preserves the dependence created by shared nuisance
coefficients and can profile an exact additive nuisance subspace.

It does not cover an uncertain response operator.  In particular, if a
protocol information form is

\[
 R^T\Omega R
\]

and \(R\) itself varies, that is a multiplicative or operator-uncertainty
problem.  It changes the information matrix and generally creates cross and
quadratic perturbation terms.  Such uncertainty must be enclosed by a
response-box or operator perturbation theorem before, or separately from,
this additive-zonotope certificate.  Reinterpreting uncertain entries of
\(R\) as independent additive generators would usually destroy both the
correct dependence and the correct quantifiers.

The current implementation also does not:

- discover optimal witnesses;
- prove externally declared infinite-tail remainder premises;
- identify a continuous coefficient box with an integral or arithmetically
  realizable nuisance set;
- cover uncertain noise precision or source calibration;
- establish locality or hardware realizability of the generators; or
- replace interval arithmetic when the declared response directions are
  irrational.

For an integral nuisance subset, the continuous-zonotope dual lower bound
remains valid because the integral set is smaller.  Equality and fractional
primal witnesses, however, belong only to the declared continuous model
unless integral realizability is proved separately.

## 10. Integration role

The module supplies a clean bridge between the OIG protocol engine and the
AO VIII--X nuisance theory:

1. the protocol engine fixes a response coordinate system and noise
   precision;
2. known shared additive nuisance directions are assembled as columns of
   \(V\);
3. unpenalized additive response directions, if any, are placed in \(B\);
4. an optimizer proposes rational primal and dual witnesses;
5. analytic tail work supplies \(U_{\rm tail}(u)\) or \(R_M\); and
6. the exact checker returns a falsifiable separation bracket and critical
   noise-radius square.

This does not solve response uncertainty, but it prevents structured
additive uncertainty from being collapsed into a much weaker entrywise box.
