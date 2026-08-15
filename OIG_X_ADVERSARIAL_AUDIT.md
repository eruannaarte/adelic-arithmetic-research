# Operational Information Geometry X: adversarial certification audit

**Status:** independent theorem-boundary audit; not peer reviewed

**Scope:** fixed-band lower and upper certificates for the Stage IX response
Gramians.  This note deliberately separates statements that are
coordinate-invariant and machine-certifiable from statements that are only
qualitative or numerical evidence.

---

## 1. Verdict

For a fixed finite source quotient, a rigorous two-sided atlas certificate is
possible.  The object that can be certified is not an ordinary matrix
eigenvalue.  It is the generalized Rayleigh floor

\[
 \gamma_K
 =
 \inf_{\theta\in\Theta}
 \inf_{z\ne0}
 \frac{z^*G_\theta z}{z^*S_\theta z},
 \tag{1.1}
\]

where

* the exact structural null space has already been quotiented out;
* \(S_\theta\succ0\) is the declared source-cost metric;
* \(G_\theta\) is the information Gram in the declared output-noise metric;
* the quotient dimension is constant on each parameter stratum; and
* every finite parameter box and every compactified endpoint is covered by
  outward-rounded matrix and tail enclosures.

Under those hypotheses, interval positivity of

\[
 [G]_B-L[S]_B
 \tag{1.2}
\]

on every box \(B\) proves \(\gamma_K\ge L\).  One certified Rayleigh quotient
at one parameter point proves \(\gamma_K\le U\).  Refinement gives an
arbitrarily tight finite-\(K\) bracket if the matrix and endpoint oracles are
effective and convergent.

The qualifications are essential.  The following implications are false:

1. a positive smallest ordinary eigenvalue after source calibration implies
   physical observability;
2. positive eigenvalues at finitely many parameter samples imply a positive
   atlas floor;
3. positive pointwise quotient spectra imply a positive uniform floor without
   compactness, continuity, a uniform source metric, and constant quotient
   rank;
4. entrywise interval endpoints bound the eigenvalues of every matrix in the
   interval;
5. a floating-point Cholesky factorization, many decimal digits, or one call
   to math.nextafter is an interval proof;
6. a continuum-output Gram floor transfers automatically to finitely many
   sensors; or
7. fixed-\(K\) certificates imply a growing-\(K\) lower law.

The strongest valid result is therefore finite, metric-aware, quotient-aware,
and atlas-complete.  It supports rigorous noise and effective-rank
consequences, but not a dimension-uniform coercivity claim.

---

## 2. The invariant pair, including noise

Let \(J_\theta:\mathbb C^K\to E^\sharp\) synthesize a physical source from
coordinates, \(R_\theta\) be the response map, and \(\Sigma_\theta\succ0\)
be the output noise covariance.  The natural pair is

\[
 S_\theta=J_\theta^*J_\theta,
 \qquad
 G_\theta
 =J_\theta^*R_\theta^*\Sigma_\theta^{-1}R_\theta J_\theta.
 \tag{2.1}
\]

Other source costs may replace \(J^*J\), but they must be declared.  Other
output metrics may replace \(\Sigma^{-1}\), but then the result is not
automatically a statistical information statement.

Under an invertible source-coordinate change \(z=C\widetilde z\),

\[
 (G,S)\longmapsto(C^*GC,C^*SC).
 \tag{2.2}
\]

The generalized spectrum is invariant under this congruence.  The ordinary
spectrum of \(G\) is not.

### 2.1 Exact calibration counterexample

Let

\[
 G_\epsilon=
 \begin{pmatrix}1&0\\0&\epsilon^2\end{pmatrix},
 \qquad S=I,
 \qquad
 C_\epsilon=
 \begin{pmatrix}1&0\\0&\epsilon^{-1}\end{pmatrix}.
\]

Then

\[
 C_\epsilon^*G_\epsilon C_\epsilon=I,
 \qquad
 C_\epsilon^*SC_\epsilon
 =\operatorname{diag}(1,\epsilon^{-2}).
\]

Calibration has made the ordinary Gram perfectly conditioned, but the
generalized eigenvalues remain \(1,\epsilon^2\).  This is exactly the issue
with a causal-moment scaling such as \(D(q)^{-1}\): it is a valid coordinate
or cost transformation only when \(D(q)^{-2}\), equivalently the transformed
source metric, remains in the information budget.  It does not turn a raw
\(L^2\) singular value of order \(q^j\) into free information.

### 2.2 Output whitening is also a pair transformation

If \(R'=WR\), the noise covariance becomes

\[
 \Sigma'=W\Sigma W^*.
\]

For invertible \(W\),

\[
 R'^*(\Sigma')^{-1}R'=R^*\Sigma^{-1}R.
\]

Multiplying the response by a large gain while leaving the noise covariance
unchanged on paper is not whitening; it is a false information gain.

### 2.3 A needed correction to analytic spectral ceilings

Suppose an analytic kernel is approximated by a rank-\(m\) kernel with
physical \(L^2\)-operator error \(\delta_m\).  To convert this into a
generalized-eigenvalue bound in arbitrary source coordinates, one needs

\[
 \|J_KS_K^{-1/2}\|\le C_0
 \tag{2.3}
\]

uniformly in \(K\).  Merely assuming \(S_K\succeq s_*I\) is enough only when
the synthesis \(J_K\) is already uniformly bounded, for example in an
\(L^2\)-orthonormal coordinate basis.  Otherwise rescaling the physical
basis can make the kernel-approximation error arbitrarily large in
coefficient coordinates.

With (2.3), a rank-\(m\) approximation gives the descending spectral bound

\[
 \mu_{m+1}\le C_0^2\delta_m,
 \tag{2.4}
\]

where \(\mu_1\ge\mu_2\ge\cdots\) are generalized Gram eigenvalues in
descending order.  If a finite \(K\)-dimensional spectrum is written in
ascending order

\[
 0<\lambda_1\le\cdots\le\lambda_K,
\]

then the corresponding statement is

\[
 \lambda_i\le C\rho^{-(K-i+1)}
 \tag{2.5}
\]

up to harmless index shifts, not \(\lambda_i\le C\rho^{-i}\).

---

## 3. Exact quotient before numerical rank

For the Stage IX phase responses,

\[
 F_f(s)=\int_0^1e^{-sV(x)}f(x)\,dx
\]

and the common structural null is

\[
 \mathcal Z_V
 =
 \{f:\mathbb E[f\mid\sigma(V)]=0\}
\]

inside the declared zero-mean source space.  Certification must occur on

\[
 E^\sharp=E/(E\cap\mathcal Z_V),
 \tag{3.1}
\]

or on a proved complement with the induced source metric.

If a true null is left in the coordinates, the full-space coercivity
constant is exactly zero.  If a small but nonzero singular vector is deleted
by a floating SVD tolerance, the reported quotient floor can be arbitrarily
too large.  Numerical rank is not a substitute for an analytic null theorem.

### 3.1 Full-space, quotient, and Sobolev statements differ

The following are distinct:

* **Full-space coercivity:** \(G\succeq cI\) on an infinite-dimensional
  source space.  This is impossible for an injective compact response
  operator.
* **Finite-quotient coercivity:** \(G\succeq c_KS\) on a fixed
  \(K\)-dimensional exact quotient.  This is possible and is the Stage X
  certification target.
* **Sobolev-weighted stability:** \(G\succeq cS_s\), where \(S_s\) assigns a
  declared frequency cost.  This changes the operational source class; it
  does not remove compactness for free.
* **Fixed-band convergence:** for each fixed \(K\), finite-model Gramians
  converge to continuum Gramians.  Constants may depend badly on \(K\).
* **Growing-band stability:** a lower bound along \(K=K(n)\).  This needs
  explicit uniform control of all \(K\)-dependent constants and cannot be
  inferred from fixed-\(K\) convergence.

### 3.2 Constant dimension is necessary but not always sufficient

If the modulation itself varies, constant null dimension does not by itself
provide a usable common coordinate system.  One also needs a verified
continuous quotient frame, or finitely many bundle charts with certified
transition congruences.  In the Stage IX atlas \(V\) is normally fixed, so
the quotient is fixed.  If \(V\) is added to the design parameters, this
extra condition becomes active.

### 3.3 Exact degeneracies

* If \(V\) is constant, every zero-mean source lies in the null.
* If \(V(x)=V(1-x)\), every reflection-odd source is in the null.
* If \(M<K\) scalar sensor values are retained, the sensed Gram has rank at
  most \(M\), even if the continuum-output Gram has rank \(K\).
* If two effective sensor functionals coincide, rank can be lost even when
  \(M\ge K\).
* If a target contrast is \(\rho_\alpha=1+\alpha\psi\), a centered response
  typically scales as \(\alpha\), so its Gram scales as \(\alpha^2\).
  Allowing \(\alpha\downarrow0\) destroys every uniform floor.

The last example also shows why a family with \(g>0\) or
\(\alpha>0\) at every sampled point may still have zero infimum as the
parameter approaches a degenerate stratum.

---

## 4. When pointwise positivity becomes uniform

The correct qualitative compactness statement is short.

### Proposition 4.1

Let \(\Theta\) be compact.  Suppose \(G_\theta\) and \(S_\theta\) are
continuous Hermitian \(K\times K\) matrices, \(S_\theta\succ0\), and
\(G_\theta\succ0\) on one fixed exact quotient for every
\(\theta\in\Theta\).  Then

\[
 \inf_{\theta\in\Theta}
 \lambda_{\min}(G_\theta,S_\theta)>0.
 \tag{4.1}
\]

Indeed, compactness and continuity give a uniform lower bound for \(S\), and
\(S^{-1/2}GS^{-1/2}\) is a continuous positive-definite matrix family.

Every word in the hypotheses matters.

### 4.1 Open-family counterexample

For the scalar family

\[
 G_\theta=\theta,\qquad S_\theta=1,\qquad0<\theta\le1,
\]

every pointwise floor is positive, but the infimum is zero.

### 4.2 Compact but discontinuous counterexample

On \([0,1]\), set

\[
 G_0=1,\qquad G_\theta=\theta\quad(\theta>0).
\]

Every matrix is positive, but the uniform infimum is zero.

### 4.3 Rank-changing compactification

Let a modulation slope \(g\downarrow0\).  For every \(g>0\), a monotone
modulation may give a trivial analytic null on a fixed finite band.  At
\(g=0\), every zero-mean port becomes null.  The family cannot be certified
as one fixed positive-definite quotient stratum.  Either impose
\(g\ge g_0>0\), or separate the degenerate endpoint and declare what quotient
and source cost are being compared.

### 4.4 Finite samples miss an arbitrarily narrow dip

Given any finite parameter grid, choose an unsampled midpoint
\(\theta_*\) and

\[
 G_\delta(\theta)=\delta+(\theta-\theta_*)^2.
\]

All sampled values can be visibly separated from zero while the true minimum
is the arbitrarily small number \(\delta\).  Dense-looking plots therefore
provide upper witnesses, not a global lower certificate.

---

## 5. Compactifying the Stage IX atlas

A finite proof must cover every finite parameter box and every infinite
endpoint.  Qualitative dominated convergence is not a numerical tail bound.

### 5.1 Early resolved endpoint

At \(q=0\), the raw response loses rank.  The calibrated matrix

\[
 D(q)^{-1}\Gamma_q^{\mathrm R}D(q)^{-1}
\]

can have a regular endpoint, but \(D(0)^{-1}\) does not exist.  A certificate
must either:

1. define the endpoint by its exact moment-limit matrix and prove an outward
   remainder

   \[
   \|D(q)^{-1}\Gamma_q^{\mathrm R}D(q)^{-1}-H\|
   \le E_0(q),
   \tag{5.1}
   \]

   or
2. use the raw pair \((\Gamma_q^{\mathrm R},D(q)^2)\) for \(q>0\) and a
   separate endpoint coordinate chart.

Evaluating at a tiny floating value of \(q\) is especially unsafe: different
moment columns underflow at different orders and create false numerical
rank.

### 5.2 Resolved and lattice infinite tails

The substitutions used in Stage IX show convergence of
\(\sqrt q\,\Gamma_q^{\mathrm R}\) and
\(\sqrt\tau\,\Gamma_{\tau,Q}^{\mathrm L}\) to the interior atomic Gram.
Certification additionally needs a computable uniform tail modulus after
the declared source metric has been inserted.

For a family of lattice preparations, saying that \(Q\) belongs to a compact
set is not yet an executable description.  A valid finite reduction uses,
for example:

* a finite-support probability polytope;
* a finite \(\ell^1\) net and
  \(|B_Q-B_{\widetilde Q}|\le\|Q-\widetilde Q\|_1\); or
* a uniform moment and tail envelope with a proved truncation error.

The constants must be uniform in \(Q\), \(K\), and the declared metric to the
extent claimed.

### 5.3 Reflecting-boundary endpoint

The coordinate \(\kappa=\infty\) is not certified by sampling a large
finite \(\kappa\).  Nor does the reciprocal coordinate
\(x=(1+\kappa)^{-1}\) automatically make ordinary interval Taylor bounds
effective: the cosine representation becomes increasingly oscillatory near
\(x=0\).

Use the exact kernel

\[
 \Phi_\kappa^{\mathrm A}(A)
 =
 \frac{1+e^{-\kappa^2/A}}{2\sqrt{\pi A}}
\]

with \(A\in[2v_-,2v_+]\), a proved Fourier tail, or verified integration by
parts.  The result must be converted to an operator or metric-relative form
bound.

### 5.4 Audit of the common-window lower lemma

Define

\[
 H_b(f,f)
 =
 \frac1{2\pi}\int_0^b
 s^{-1/2}|F_f(s)|^2\,ds.
\]

For the standard Gaussian resolved chart, the substitution
\(s=\pi^2qu^2\) gives, for \(q\ge1\),

\[
 \sqrt{1+q}\,\Gamma_q^{\mathrm R}
 \succeq
 \min\{1,\sqrt2e^{-b}\}\,H_b.
\tag{5.2}
\]

This is correct: with \(x=1/q\), the logarithm of the window multiplier is
\(\frac12\log(1+x)-sx\), a concave function whose minimum occurs at an
endpoint.

For the one-cell lattice atom, the substitution
\(s=4\tau\sin^2(\theta/2)\) gives

\[
 \sqrt{1+\tau}\,\Gamma_{\tau,\delta_0}^{\mathrm L}
 \succeq H_b,
 \qquad \tau\ge1,\quad b\le4.
\tag{5.3}
\]

For general \(Q\), (5.3) needs a proved uniform lower bound on
\(|B_Q(\theta)|\) over the transformed window.

For the interior atomic chart,

\[
 \Gamma_\infty^{\mathrm A}=H_\infty\succeq H_b.
\tag{5.4}
\]

The analogous statement for every reflecting-boundary coordinate is false.
The cosine term is not a positive-semidefinite quadratic form.

An exact two-level counterexample takes a zero-mean source whose Laplace
profile is proportional to

\[
 F(s)=e^{-s}-e^{-2s}.
\]

This is realized by a modulation taking values \(1\) and \(2\) on two
equal-measure cells and a source with opposite signs on those cells.  Direct
Gaussian integration gives

\[
\begin{aligned}
 \Gamma_\infty^{\mathrm A}
 &=I(2)-2I(3)+I(4),\\
 \Gamma_\kappa^{\mathrm A}
 &=\Gamma_\infty^{\mathrm A}
   +I(2)e^{-\kappa^2/2}
   -2I(3)e^{-\kappa^2/3}
   +I(4)e^{-\kappa^2/4},
\end{aligned}
\tag{5.5}
\]

where \(I(c)=1/(2\sqrt{\pi c})\).  At
\(\kappa\approx1.607\),

\[
 \Gamma_\kappa^{\mathrm A}/\Gamma_\infty^{\mathrm A}
 \approx0.3961,
\]

whereas

\[
 H_1/\Gamma_\infty^{\mathrm A}\approx0.6567.
\]

Thus \(\Gamma_\kappa^{\mathrm A}\not\succeq H_1\).  The boundary family needs
its own compact-parameter certificate or a different proved form bound.

---

## 6. What interval arithmetic must prove

Let \(B\) be one box in a finite cover.  A correct oracle supplies Hermitian
interval matrices \([G]_B\) and \([S]_B\) containing the exact matrices for
every parameter in \(B\), including:

* basis and metric uncertainty;
* directed rounding in every elementary and special function;
* quadrature or series remainder;
* truncation of infinite source, target, or output domains;
* compactified endpoint tails; and
* parameter dependence across the entire box.

First certify \([S]_B\succ0\).  To prove a candidate lower value \(L\),
certify

\[
 [G]_B-L[S]_B\succ0
\tag{6.1}
\]

for every matrix represented by the interval enclosure.  Valid routes
include:

1. interval Cholesky;
2. symmetric interval \(LDL^*\) with a fixed verified pivot pattern,
   including \(2\times2\) pivots when needed;
3. a midpoint smallest-eigenvalue lower bound minus a rigorous operator-norm
   radius; or
4. a verified generalized-eigenvalue enclosure.

Failure of an interval factorization is inconclusive.  Dependency
overestimation may make an actually positive family impossible to certify
until the box is split or a sharper representation is used.

### 6.1 Entrywise endpoint eigenvalues are unsound

Entrywise inequalities do not imply Loewner inequalities.  Consider the
interval whose diagonal is fixed at \(2\), and whose off-diagonal lower and
upper endpoint matrices are

\[
 L=
\begin{pmatrix}
2&0.25548882&-0.08607100\\
0.25548882&2&-1.40896198\\
-0.08607100&-1.40896198&2
\end{pmatrix},
\]

\[
 U=
\begin{pmatrix}
2&1.17513321&0.81983103\\
1.17513321&2&0.62089529\\
0.81983103&0.62089529&2
\end{pmatrix}.
\]

Both endpoint matrices are positive definite, with smallest eigenvalues
approximately \(0.58\) and \(0.80\).  Yet the allowed mixed-corner matrix

\[
 M=
\begin{pmatrix}
2&1.17513321&0.81983103\\
1.17513321&2&-1.40896198\\
0.81983103&-1.40896198&2
\end{pmatrix}
\]

has smallest eigenvalue approximately \(-0.286\).  Computing eigenvalues of
two entrywise endpoint matrices does not enclose the interval family.

### 6.2 Floating factorization is evidence, not a proof

A floating Cholesky or \(LDL^*\) calculation may:

* round a negative pivot upward;
* suffer cancellation in a Schur complement;
* use an unverified pivot permutation;
* evaluate a special function with an unknown error; or
* omit quadrature and endpoint tails.

Applying math.nextafter only to the final eigenvalue cannot repair inward
rounding in all prior operations.  A residual bound for one approximate
eigenpair also does not by itself prove that it is the smallest eigenvalue.

### 6.3 Underflow and false numerical rank

The positive number \(e^{-800}\) underflows to zero in ordinary binary64.
Early moment columns can therefore appear exactly null even when the
analytic response is nonzero.

The \(13\times13\) Hilbert matrix

\[
 H_{ij}=\frac1{i+j+1},\qquad0\le i,j<13,
\]

is exactly positive definite: exact rational \(LDL^*\) has strictly positive
pivots.  Standard binary64 rank and eigensolvers commonly report rank loss
and may even return a negative smallest eigenvalue.  This is a useful
reproducible control for every proposed rank-certification pipeline.

High precision helps, but without directed rounding and remainder bounds it
is still not a certificate.

---

## 7. Strongest valid finite-cover theorem

### Theorem 7.1: certified atlas bracket

Let the declared atlas be a finite union
\(\Theta=\bigcup_{a=1}^A\Theta_a\).  On each stratum assume:

1. \(\Theta_a\) is effectively compact;
2. the analytic null has been quotiented exactly and its dimension is a
   constant \(K_a\);
3. a continuous quotient frame or finitely many certified frame charts are
   supplied;
4. \(G_\theta\) and \(S_\theta\) are continuous Hermitian matrices in those
   frames, with \(S_\theta\succ0\);
5. a convergent outward oracle encloses \(G\) and \(S\) on every rational
   parameter box;
6. the oracle includes all rounding, quadrature, preparation, and infinite
   tail errors; and
7. finite covers and endpoint regions are effectively enumerable.

If a finite cover \(\mathcal B_a\) and \(L>0\) satisfy

\[
 [G]_B-L[S]_B\succ0
\qquad
\text{for every }a\text{ and }B\in\mathcal B_a,
\tag{7.1}
\]

then

\[
 \gamma=\min_a\inf_{\theta\in\Theta_a}
 \lambda_{\min}(G_\theta,S_\theta)\ge L.
\tag{7.2}
\]

If, at one certified parameter point \(\theta_*\), a nonzero vector \(z_*\)
has outward numerator upper bound \(\overline n\) and positive denominator
lower bound \(\underline d\), then

\[
 \gamma\le
 \frac{\overline n}{\underline d}
 =U.
\tag{7.3}
\]

If each stratum is pointwise positive definite and the interval oracle
converges uniformly under refinement, finite refinement eventually produces
\(L>0\).  With an effective modulus or the stated convergent box oracle,
lower and upper brackets can be refined to any prescribed tolerance.

#### Proof

For every exact \(\theta\in B\), (7.1) gives

\[
 z^*G_\theta z\ge Lz^*S_\theta z
\]

for every \(z\).  The finite cover gives (7.2).  The Rayleigh principle gives
(7.3).  Compactness, continuity, and positive definiteness give a strictly
positive exact margin on each stratum.  Uniformly shrinking interval radii
eventually fit inside that margin.

### 7.2 Upper bounds are easier than lower bounds

One parameter point and one source direction are enough for a rigorous
upper bound on an infimum.  A lower bound must cover every point and every
source direction.  This asymmetry is useful operationally: a cheap upper
witness can quickly disprove an overoptimistic proposed lower certificate.

---

## 8. Transfer, noise, and effective rank

Every transfer error must be stated in the source metric.  A sufficient form
is

\[
 \left|
 z^*(G_{h,\theta}-G_\theta)z
 \right|
 \le
 \Delta_K\,z^*S_\theta z
\tag{8.1}
\]

uniformly on the atlas.  Equivalently, for a fixed metric,

\[
 \|S_\theta^{-1/2}
 (G_{h,\theta}-G_\theta)
 S_\theta^{-1/2}\|\le\Delta_K.
\]

An unqualified Euclidean matrix norm does not justify a generalized Weyl
shift when \(S\ne I\).

If the continuum certificate is \(\gamma_K\ge L_K\) and
\(\Delta_K<L_K\), then

\[
 \gamma_{K,h}\ge L_K-\Delta_K.
\tag{8.2}
\]

### 8.1 Gaussian testing consequence

Suppose the output is correctly whitened, each repetition has independent
noise \(N(0,\sigma^2I)\), the source direction is known and has unit
\(S\)-norm, and the source amplitude is \(a\).  Equal-prior testing of zero
against that intervention has error at most \(\alpha<1/2\) in every declared
direction whenever

\[
 N\ge
 \frac{
 4\sigma^2[\Phi_{\mathrm N}^{-1}(1-\alpha)]^2
 }{
 a^2(L_K-\Delta_K)
 }.
\tag{8.3}
\]

Here \(\Phi_{\mathrm N}\) is the standard normal distribution function.  The
formula does not cover unknown support, composite backgrounds, correlated
repetitions, or nonlinear reconstruction.

One certified upper witness \(U_K\), combined with a transfer upper error,
also gives the converse worst-direction obstruction with
\(U_K+\Delta_K\) in the denominator.

### 8.2 Certified effective rank

Let the generalized Gram eigenvalues be ordered increasingly.  A verified
lower enclosure satisfying

\[
 \inf_\theta\lambda_r(\theta)\ge L_r
\]

and \(L_r-\Delta_K\ge\eta^2\) certifies at least
\(K-r+1\) directions above singular-value threshold \(\eta\).  Equivalently,
using descending eigenvalues \(\mu_1\ge\cdots\ge\mu_K\), a lower bound on
\(\mu_r\) certifies at least \(r\) visible directions.

An upper enclosure satisfying

\[
 \sup_\theta\mu_{r+1}(\theta)+\Delta_K<\eta^2
\]

certifies at most \(r\) visible directions.  Intervals crossing
\(\eta^2\) are unresolved, not invisible.  With \(M\) scalar sensors the
effective rank is always at most \(M\).

Analytic low-rank approximation may yield
\(\mu_j\le C\rho^{-j}\) in descending order, giving an
\(O(\log(1/\eta))\) upper information count.  It does not give a matching
lower count.

---

## 9. Required controls for a Stage X implementation

A proof trace should fail loudly on at least these cases:

1. source-coordinate whitening leaves the generalized spectrum unchanged;
2. a finite parameter grid misses a narrow positive dip;
3. positive entrywise endpoint matrices hide an indefinite mixed corner;
4. exact rational \(LDL^*\) proves a Hilbert matrix positive while binary64
   reports false rank loss;
5. a positive exponential underflows to binary64 zero;
6. target contrast tending to zero collapses a Gram quadratically;
7. fewer sensors than source dimensions create an exact sampled null; and
8. a midpoint-minus-radius box proof succeeds on a simple continuous matrix
   family and lies below the true dense-grid minimum.

The companion file test_oig_x_adversarial_controls.py implements these
controls.  They are not a Stage X certificate; they are regression tests
against several invalid certification shortcuts.

---

## 10. Final theorem boundary

The Stage X goal survives in the following precise form:

> For each declared finite source quotient and each effectively compact
> constant-rank atlas stratum, a metric-correct, outward-rounded matrix oracle
> with rigorous finite-box and endpoint-tail coverage can certify arbitrarily
> sharp lower and upper bounds on the generalized observability floor.

What does not survive is any implication from this finite theorem to
full-space coercivity, an unweighted growing-band floor, or a physical
information gain obtained by calibration.  Compactness still forces raw
high-mode singular values toward zero, finite sensors impose their own rank
cap, and all useful noise claims must spend the same source and output metrics
that were used in the spectral certificate.
