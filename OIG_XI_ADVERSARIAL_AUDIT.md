# Operational Information Geometry XI: finite-transfer adversarial audit

**Status:** independent theorem-boundary audit; not peer reviewed

**Scope:** transfer of a certified continuum source spectrum to a finite
grid, finite target preparation, finite boundary geometry, and finite noisy
sensor system

---

## 1. Verdict

A continuum floor transfers only after the entire finite experiment has been
placed in the same source and output metrics as the continuum certificate.
The clean object is the normalized response

\[
 {\cal A}_\theta
 =
 \Sigma_\theta^{-1/2}
 P_\theta R_\theta J_\theta S_\theta^{-1/2},
\tag{1.1}
\]

where:

* \(J_\theta\) synthesizes the exact quotient source;
* \(S_\theta\) is its declared source-cost metric;
* \(R_\theta\) is the physical response;
* \(P_\theta\) is the retained target/time sensor map; and
* \(\Sigma_\theta\) is the noise covariance on those retained measurements.

The finite experiment has a corresponding \({\cal A}_{h,\theta_h}\), after a
proved identification of its quotient coordinates with the continuum
coordinates.  If

\[
 \sup_{\theta}
 \|{\cal A}_{h,\theta_h}-{\cal A}_\theta\|
 \le\epsilon_K
 <\sqrt{L_K},
\tag{1.2}
\]

and the continuum certificate gives

\[
 \inf_\theta\sigma_{\min}({\cal A}_\theta)^2\ge L_K,
\]

then

\[
 \boxed{
 \inf_\theta
 \lambda_{\min}({\cal A}_{h,\theta_h}^*
 {\cal A}_{h,\theta_h})
 \ge(\sqrt{L_K}-\epsilon_K)^2.}
\tag{1.3}
\]

This response-level theorem is stronger and cleaner than separately
perturbing a raw Gram: it automatically includes cross terms and yields the
right singular-value scale.

An equivalent Gram route is valid if one directly proves

\[
 \sup_\theta
 \|{\cal A}_{h,\theta_h}^*{\cal A}_{h,\theta_h}
  -{\cal A}_\theta^*{\cal A}_\theta\|
 \le\Delta_K<L_K,
\tag{1.4}
\]

which gives the finite floor \(L_K-\Delta_K\).

What does not survive adversarial checking is an unqualified Euclidean
quantity \(\|G_h-G\|\), a moment-only early error, weak target convergence,
or \(M\ge K\) sensor counting.  Each can hold while the finite generalized
floor is zero or tends to zero.

---

## 2. Metric mismatch can invalidate zero Gram error

Suppose continuum and finite calculations are written in the same coefficient
symbols but use source metrics \(S\) and \(S_h\).  Even

\[
 G_h=G
\]

does not transfer a generalized eigenvalue unless the metrics are compared.

### 2.1 Exact counterexample

Let

\[
 G_h=G=I_2,\qquad
 S=I_2,\qquad
 S_h=\operatorname{diag}(1,h^{-2}).
\]

The Euclidean Gram error is exactly zero, while

\[
 \lambda_{\min}(G_h,S_h)=h^2\longrightarrow0.
\tag{2.1}
\]

Thus a finite transfer theorem stated only in terms of
\(\|G_h-G\|\) is coordinate dependent.

### 2.2 Correct pair-form theorem

Work on one exact reference coefficient space and suppose

\[
 (1-\eta_S)S
 \preceq S_h
 \preceq(1+\eta_S)S,
\qquad0\le\eta_S<1,
\tag{2.2}
\]

and

\[
 -\Delta_G S
 \preceq G_h-G
 \preceq\Delta_G S.
\tag{2.3}
\]

If \(G\succeq L S\) and \(\Delta_G<L\), then

\[
 \boxed{
 \lambda_{\min}(G_h,S_h)
 \ge\frac{L-\Delta_G}{1+\eta_S}.}
\tag{2.4}
\]

If a continuum vector has Rayleigh quotient at most \(U\), the same vector
gives

\[
 \lambda_{\min}(G_h,S_h)
 \le\frac{U+\Delta_G}{1-\eta_S}.
\tag{2.5}
\]

The proof is just the two Loewner inequalities.  This is the minimum
acceptable correction when separate source metrics are retained.

### 2.3 Quotient transport is part of the metric

The continuum quotient and finite quotient need the same proved dimension
and a specified injective transport.  Numerical deletion of a small finite
singular direction is not a quotient map.  A valid source transfer records:

1. an exact continuum quotient basis;
2. the finite injection or interpolation of that basis;
3. the finite source Gram \(S_h\);
4. a proof of (2.2); and
5. any moment-fitting change of coordinates and its condition number.

If \(S_h\) becomes singular, the finite experiment has acquired a new exact
source null and no positive \(K\)-direction transfer is possible.

---

## 3. Moment calibration amplifies raw consistency errors

In the early chart, let the continuum response columns have pivot orders
\(r_i\):

\[
 R(q)e_i=q^{r_i}y_i+O(q^{r_i+1}),
\qquad
 D(q)=\operatorname{diag}(q^{r_i}).
\]

The calibrated response is \(R(q)D(q)^{-1}\).  A finite lower-moment defect
\(\ell_{ji,h}q^j\), \(j<r_i\), becomes

\[
 \ell_{ji,h}q^{j-r_i}
\tag{3.1}
\]

after calibration.  Raw convergence \(\ell_{ji,h}\to0\) is not enough.

### 3.1 Exact two-column counterexample

Let

\[
 R(q)=\operatorname{diag}(q,q^2),
\qquad
 E_h=h^2 e_1e_2^*.
\]

Then \(\|E_h\|=h^2\to0\), but

\[
 (R(q)+E_h)D(q)^{-1}
 -R(q)D(q)^{-1}
 =
 h^2q^{-2}e_1e_2^*.
\tag{3.2}
\]

At \(q=h\) the calibrated error is order one; at \(q=h^2\) it diverges like
\(h^{-2}\).  No raw \(O(h^2)\) response theorem can be applied after
calibration without the factor \(q^{-r_i}\).

### 3.2 What a moment certificate must contain

For every calibrated column, certify

\[
 {\cal L}_{i,h}(q)=
 \sum_{j<r_i}
 \|y_{j,h}\|\,|\ell_{ji,h}|q^{j-r_i}
 +
 \|\widetilde y_{r_i,h}-y_{r_i}\|
\tag{3.3}
\]

in the declared output-noise metric.  Scalar moment defects alone are
sufficient only after the associated output coefficient vectors have a
proved uniform norm bound.

Mass cancellation should be exact.  Moment fitting can make selected
\(\ell_{ji,h}\) exactly zero, but the fitting map changes \(S_h\) and may
have a large norm.  Its source-cost inflation must be included in (2.2) or
directly in (1.1).

---

## 4. Pure moments do not control mixed \(A\)-\(V\) words

Expanding a finite generator containing source diffusion \(A\) and
multiplication \(V\) produces noncommutative words.  Pairing with the
conserved vector removes a leftmost \(A\), but it does not remove words such
as

\[
 VAV,\quad V^2AV,\quad VAV^2,\quad\ldots
\]

Moment fitting controls the pure \(V^j\) terms only.

### 4.1 Exact failure of a restricted \(A\)-norm shortcut

In \(\mathbb R^2\), let

\[
 A=
 \begin{pmatrix}1&-1\\-1&1\end{pmatrix},
\qquad
 V=\operatorname{diag}(0,1),
\qquad
 {\bf1}=(1,1)^T,
\qquad
 e=(1,1)^T.
\]

Then

\[
 {\bf1}^TA=0,\qquad Ae=0,
\]

so the norm of \(A\) on \(E=\operatorname{span}\{e\}\) is zero.  Nevertheless

\[
 {\bf1}^T VAVe=1.
\tag{4.1}
\]

Therefore \(\|A\|_{E}\) alone cannot bound all mixed words: \(A\) may act
after multiplication has moved the source outside \(E\).

### 4.2 Correct early mixed-word object

Let \({\cal W}_{n,\ell}(A_h,V_h)\) denote all length-\(n\) words containing
\(\ell\ge1\) occurrences of \(A_h\), after deleting the words killed exactly
by conservation.  A certifiable remainder is

\[
 {\cal M}_{K,h}(q,t)
 =
 \max_i q^{-r_i}
 \left\|
 \sum_{n\ge1}
 \sum_{\ell\ge1}
 c_{n,\ell}(q,t)
 P_h{\cal W}_{n,\ell}(A_h,V_h)J_he_i
 \right\|_{\Sigma_h^{-1}}.
\tag{4.2}
\]

The exact coefficients and a rigorous exponential tail must come from the
Duhamel or power-series representation actually used by the model.

A convenient bound of the form

\[
 C_K\frac{t\|A\|}{q^{r_d-1}}
\tag{4.3}
\]

is valid only after proving a closure estimate on the \(V\)-generated cyclic
space, for example

\[
 \max_{a_0+\cdots+a_\ell\le r_d}
 \|V^{a_0}AV^{a_1}\cdots AV^{a_\ell}J_K\|
 \le C_K\|A\|_{\mathrm{declared}}.
\tag{4.4}
\]

For cosine sources and smooth \(V\), graph or Sobolev norms can supply such a
finite-\(K\) constant.  The constant and the number of words are
\(K\)-dependent and must not disappear from a growing-band statement.

---

## 5. Target preparation needs active-band control

Weak convergence of target probability measures does not control their
Fourier multipliers on a growing output band.

### 5.1 Exact shifted-atom counterexample

Let

\[
 \eta_h=\delta_h,\qquad\eta=\delta_0.
\]

Then \(\eta_h\) converges weakly to \(\eta\), and every fixed-frequency
Fourier multiplier converges.  At the growing frequency

\[
 \xi_h=\frac{\pi}{h},
\]

however,

\[
 |\widehat\eta_h(\xi_h)-\widehat\eta(\xi_h)|
 =|-1-1|=2.
\tag{5.1}
\]

Thus target preparation must be controlled uniformly on the chart's active
frequency set, not only by weak convergence or a few moments.

### 5.2 Chart-specific sufficient data

* **Resolved:** certify a weighted multiplier bound for
  \(\widehat\eta_h-\widehat\eta\) on the full active output region, plus a
  rigorous output tail.
* **Lattice:** an \(\ell^1\) preparation bound is effective because

  \[
  \sup_\theta|B_{Q_h}(\theta)-B_Q(\theta)|
  \le\|Q_h-Q\|_1.
  \]

  For Gram weights, include the corresponding
  \(2\epsilon+\epsilon^2\) bound.
* **Atomic:** control mass normalization, target variance divided by \(t\),
  target centering, and any cell-to-continuum interpolation in the same
  output metric.

Target contrast must be bounded away from zero if a uniform floor is
claimed.  If a centered target response scales by \(\alpha_h\to0\), its Gram
floor scales by \(\alpha_h^2\), regardless of source convergence.

---

## 6. Boundary transfer is a separate stratum

For the continuum reflecting-boundary kernel,

\[
 \Phi_\kappa^{\mathrm A}(A)
 =
 \frac{1+e^{-\kappa^2/A}}{2\sqrt{\pi A}}.
\tag{6.1}
\]

At \(\kappa=0\) the kernel is twice the interior kernel; at
\(\kappa=\infty\) it is the interior kernel.  If the finite boundary
coordinate does not converge to the declared continuum coordinate, the
transfer error can remain order one.

### 6.1 Exact endpoint counterexample

A sequence alternating between \(\kappa_h=0\) and
\(\kappa_h\to\infty\) alternates between the doubled and interior scalar
kernels.  Mesh refinement alone does not select a boundary chart.

### 6.2 Correct boundary inputs

The finite proof must declare

\[
 \kappa_h=\frac{d_h}{\sqrt t}
\]

and certify either:

1. \(|\kappa_h-\kappa|\) together with a uniform derivative bound for
   (6.1); or
2. an outward kernel enclosure over a full \(\kappa\)-box; or
3. an explicit large-\(\kappa\) tail enclosure.

For \(A\ge A_{\min}>0\),

\[
 \sup_{\kappa\ge0}
 \left|\partial_\kappa
 \frac{e^{-\kappa^2/A}}{2\sqrt{\pi A}}\right|
 \le
 \frac1{\sqrt{2e\pi}\,A_{\min}}.
\tag{6.2}
\]

After source synthesis, multiply this kernel bound by the correct
metric-relative synthesis norm.

The interior term \(\sqrt t/d_h\to0\) is incompatible with a finite boundary
coordinate \(d_h/\sqrt t\to\kappa\).  Interior and boundary remainder
budgets must therefore be stated on separate strata.

---

## 7. Finite sensors require a frame, not a count

Let \(T_\theta:E_K^\sharp\to Y_\theta\) be the continuum response and let
\({\cal S}_{h,\theta}:Y_\theta\to\mathbb C^M\) be the whitened finite sensor
map.  A sufficient transfer condition on the response range is

\[
 (1-\eta_{\rm sens})\|y\|_Y^2
 \le
 \|{\cal S}_{h,\theta}y\|_2^2
 \le
 (1+\eta_{\rm sens})\|y\|_Y^2
\tag{7.1}
\]

for every \(y\in T_\theta(E_K^\sharp)\), uniformly on the atlas.

The count \(M\ge K\) is only necessary.

### 7.1 Exact \(M=K\) rank-loss example

Take \(T=I_2\) and

\[
 {\cal S}=
 \begin{pmatrix}1&0\\1&0\end{pmatrix}.
\]

There are two scalar measurements for two source directions, but

\[
 T^*{\cal S}^*{\cal S}T
 =
 \operatorname{diag}(2,0)
\]

has a zero floor.  Repeated, symmetric, or aliased sensors can fail in the
same way.

If sensors are noisy, (7.1) must use the whitened map
\(\Sigma_h^{-1/2}{\cal S}_h\).  Raw sensor amplitudes do not define an
information frame.

---

## 8. Calibration and noise must transform together

Let an output gain \(W\) be applied to response \(R\).  The noise covariance
becomes

\[
 \Sigma'=W\Sigma W^*.
\]

For invertible \(W\),

\[
 (WR)^*(W\Sigma W^*)^{-1}(WR)
 =
 R^*\Sigma^{-1}R.
\tag{8.1}
\]

Ignoring the covariance transformation creates artificial information.

### 8.1 Exact early-noise control

Let

\[
 R(q)=\operatorname{diag}(q,q^2),\qquad
 \Sigma=I,\qquad
 W=D(q)^{-1}.
\]

The displayed calibrated response is \(WR=I\), but its noise covariance is
\(WW^*=D(q)^{-2}\).  The correctly whitened information Gram remains

\[
 R(q)^*R(q)=\operatorname{diag}(q^2,q^4),
\]

not \(I\).  Source calibration answers a different cost question; output
calibration does not improve signal-to-noise ratio.

If \(\Sigma_h\) is estimated, its uncertainty needs a relative positive
definite enclosure.  Inverting an estimated small eigenvalue without such an
enclosure can manufacture an arbitrarily large information direction.

---

## 9. Growing \(K\) requires more than resolution inequalities

Conditions such as

\[
 Kh\to0,\qquad K\varepsilon\to0,\qquad K\sqrt t\to0
\]

control leading dispersion or source-diffusion scales.  They do not by
themselves compare the finite error with the shrinking continuum floor.

### 9.1 Exact dispersion control

For the standard second-difference Neumann or periodic symbol,

\[
 \lambda_{k,h}
 =
 \frac4{h^2}\sin^2\!\left(\frac{k\pi h}{2}\right),
\qquad
 \lambda_k=(k\pi)^2.
\tag{9.1}
\]

If \(kh\to0\), the relative symbol error is

\[
 \frac{\lambda_{k,h}}{\lambda_k}-1
 =
 -\frac{(k\pi h)^2}{12}+O((kh)^4).
\]

If \(kh=1/2\), the ratio is the nonunit constant \(8/\pi^2\).  This confirms
the resolution condition, but a spectral transfer theorem still needs the
resulting operator error to be \(o(\gamma_K)\), or the response error to be
\(o(\sqrt{\gamma_K})\).

### 9.2 Factorial floors make constants decisive

The fixed-\(\tau\) lattice member has a squared-factorial upper ceiling in
\(K\).  Therefore a polynomial-in-\(h\) absolute error bound does not yield a
large growing band merely from \(Kh\to0\).  A useful schedule needs:

1. a quantitative continuum lower certificate \(L_K\);
2. all \(K\)-dependent graph, moment-fit, and calibration constants;
3. a response error \(\epsilon_K<\sqrt{L_K}\), or Gram error
   \(\Delta_K<L_K\); and
4. a finite sensor frame at that same \(K\).

Fixed-\(K\) convergence and a diagonal argument prove existence of some
arbitrarily slow \(K(h)\).  They do not produce an executable bandwidth law.

---

## 10. Strongest valid finite-transfer theorem

### Theorem 10.1: normalized-response transfer

Let the continuum atlas be a finite union of compact constant-quotient-rank
strata.  On every stratum suppose:

1. the continuum and finite quotient coordinates are linked by a certified
   injective transport;
2. the source metrics and noise covariances are positive definite on those
   coordinates;
3. source synthesis, target preparation, boundary geometry, sensor sampling,
   and whitening are all included in the normalized maps (1.1);
4. the continuum certificate gives

   \[
   \sigma_{\min}({\cal A}_\theta)\ge\sqrt{L_K};
   \]

5. a finite outward proof covers every parameter box and endpoint and gives

   \[
   \|{\cal A}_{h,\theta_h}-{\cal A}_\theta\|
   \le\epsilon_K
   \]

   uniformly; and
6. in the early stratum, the error proof includes calibrated lower-moment
   leakage and the complete mixed-word remainder.

If \(\epsilon_K<\sqrt{L_K}\), then (1.3) holds throughout the finite atlas.
For every singular-value index,

\[
 |\sigma_j({\cal A}_{h,\theta_h})
  -\sigma_j({\cal A}_\theta)|
 \le\epsilon_K.
\tag{10.1}
\]

#### Proof

This is the singular-value perturbation inequality applied after all source
and output metrics have been normalized.  Uniform parameter coverage gives
the atlas statement.

### 10.2 A safe auditable decomposition

It is legitimate to prove

\[
 \epsilon_K
 \le
 \epsilon_{\rm source}
 +\epsilon_{\rm dynamics}
 +\epsilon_{\rm moment}
 +\epsilon_{\rm mixed}
 +\epsilon_{\rm target}
 +\epsilon_{\rm boundary}
 +\epsilon_{\rm sensor}
 +\epsilon_{\rm noise}
\tag{10.2}
\]

only when every term is an operator error between consecutive maps in one
telescoping factorization of the **normalized response**.  Raw errors from
different coordinate systems cannot simply be added.

If Gram-form errors are easier to certify, use (2.2)--(2.4) or the normalized
Gram condition (1.4).  Do not mix a response error threshold
\(\sqrt{L_K}\) with a Gram error threshold \(L_K\).

---

## 11. Noise and effective-rank consequences

Under Theorem 10.1, a known unit source direction of amplitude \(a\), observed
with correctly whitened independent Gaussian noise over \(N\) repetitions,
has worst-direction equal-prior testing error at most \(\alpha<1/2\) whenever

\[
 \boxed{
 N\ge
 \frac{
 4[\Phi_{\rm N}^{-1}(1-\alpha)]^2
 }{
 a^2(\sqrt{L_K}-\epsilon_K)^2
 }.}
\tag{11.1}
\]

If whitening leaves a scalar noise variance \(\sigma^2\), multiply the
numerator by \(\sigma^2\).  Amplitude must be measured in the same source
metric used in (1.1).

If a continuum descending singular value has certified lower bound
\(\underline\sigma_r\) and

\[
 \underline\sigma_r-\epsilon_K\ge\eta,
\]

then at least \(r\) finite directions exceed threshold \(\eta\).  If
\(\overline\sigma_{r+1}+\epsilon_K<\eta\), at most \(r\) do.  A finite sensor
system also imposes the exact cap \(r\le M\).

These are simple-known-direction Gaussian consequences.  Unknown support,
composite backgrounds, covariance estimation, and nonlinear recovery need
separate theorems.

---

## 12. Required proof trace

A reproducible Stage XI certificate should contain:

1. exact continuum and finite quotient bases and their transport;
2. \(S,S_h,\Sigma,\Sigma_h\) and positive-definiteness enclosures;
3. the declared continuum atlas bracket \(L_K,U_K\);
4. calibrated moment-leakage bounds column by column;
5. a complete mixed-word or Duhamel remainder with a rigorous tail;
6. active-band target multiplier or preparation bounds;
7. boundary-coordinate boxes and endpoint tails;
8. a whitened finite-sensor frame certificate;
9. an outward normalized-response or normalized-Gram error;
10. all \(K\)-dependent constants and the exact condition
    \(\epsilon_K<\sqrt{L_K}\) or \(\Delta_K<L_K\); and
11. a proof trace identifying the weakest parameter box.

The companion file test_oig_xi_adversarial_controls.py implements exact
small counterexamples for the invalid shortcuts in Sections 2--9.  They are
falsification controls, not a finite-transfer certificate.

---

## 13. Final boundary

The finite-transfer target survives, but in a stricter form than raw
fixed-band convergence:

> A finite noisy sensor experiment inherits a continuum source-spectrum
> certificate only when its complete metric-normalized response is uniformly
> close over the same exact quotient and the entire compactified atlas.

Moment fitting, mesh resolution, target convergence, and sensor count are
ingredients, not substitutes for this operator statement.  In the early
chart, calibration exposes every lower moment and every noncommutative mixed
word.  In a growing band, their constants must beat the shrinking continuum
floor.  This is the correct point at which a continuum theorem becomes an
operational finite theorem.
