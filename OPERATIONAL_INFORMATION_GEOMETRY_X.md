# Operational Information Geometry X

## Certified observable spectra

**Status:** theorem, computer-assisted certificate, and falsification layer;
not peer reviewed

**Model:** the continuum phase-response Gramians of Stages VII--IX for the
declared parabolic path model

**Purpose:** replace qualitative finite-band visibility and high-precision
spectra by coordinate-invariant, outward-rounded information certificates

---

## 1. Outcome

Stage IX identified the quantity that a growing-band theorem must control:
the smallest positive response-Gram eigenvalue on the exact source quotient.
Stage X makes that quantity certifiable.

There are four levels of result.

1. For every fixed quotient dimension on a compact constant-rank parameter
   stratum, the generalized atlas floor is finitely enclosable to arbitrary
   prescribed width, provided validated entry, derivative, and endpoint-tail
   oracles are available.
2. For the affine ramp and the first eight cosine ports, a single validated
   truncated-Laplace Gram supplies rigorous continuous late-chart bounds in
   both the \(L^2\) and continuum \(H^1\) source metrics.
3. For the first two cosine ports, an independent proof covers the complete
   declared continuum atlas, including the calibrated early endpoint and
   every reflecting-boundary coordinate:

   \[
    \boxed{10^{-19}\le \gamma_2\le10^{-6}.}
    \tag{1.1}
   \]

4. In the raw \(L^2\) cosine bands, the truncated-Laplace and fixed one-cell
   lattice exponential maps have rigorous squared-factorial upper ceilings,
   while a separated sampling frame gives an explicit \(e^{-O(K^2)}\) lower
   bound.  The exact fixed-band
   interaction-strength fan is \(g^2,g^4,\ldots,g^{2K}\); the proposed
   factorial ratio constant remains a clearly labeled conjecture.

Here \(\gamma_2\) is a generalized **Gram** eigenvalue.  The corresponding
worst response singular value lies between \(10^{-9.5}\) and \(10^{-3}\).
The broad interval records the conservatism of the proof, not numerical
uncertainty about an ordinary floating-point eigenvalue.

The certificate is continuous in its declared parameters.  It is not an
inference from a grid of sampled eigenvalues.  Exact rational model data,
Arb real-ball quadrature, analytic endpoint reductions, and verified positive
definiteness make every sign decision.

This does not create an infinite-dimensional coercivity theorem.  The phase
maps remain compact, so their observable floors must deteriorate with source
dimension.  Stage X quantifies that deterioration through \(K=8\) and turns
the Stage IX condition ``finite error smaller than the continuum gap'' into
an executable moderate-band test.

---

## 2. The coordinate-invariant object

Let \(E_K\) be a \(K\)-dimensional complement of the exact null

\[
 \mathcal Z_V
 =H_0\cap\{f:\mathbb E[f\mid\sigma(V)]=0\}.
 \tag{2.1}
\]

At chart parameter \(\theta\), let

\[
 G_\theta=R_\theta^*W_\theta R_\theta
 \tag{2.2}
\]

be the response Gram in the declared whitened output metric, and let
\(S_\theta\succ0\) be the source-cost Gram.  Define

\[
 0<\lambda_1(\theta)\le\cdots\le\lambda_K(\theta),
 \qquad
 G_\theta z=\lambda S_\theta z.
 \tag{2.3}
\]

If \(z=P\widetilde z\), then

\[
 (G_\theta,S_\theta)
 \longmapsto
 (P^*G_\theta P,P^*S_\theta P),
 \tag{2.4}
\]

and the generalized eigenvalues do not change.  This is why Stage X
certifies the pair \((G,S)\), never an ordinary eigenvalue after an
unreported whitening or preconditioner.

For a compact constant-rank stratum \(\mathfrak A_a\), put

\[
 \gamma_{K,a}
 =\inf_{\theta\in\mathfrak A_a}\lambda_1(\theta),
 \qquad
 \gamma_K=\min_a\gamma_{K,a}.
 \tag{2.5}
\]

The minimum in (2.5) is meaningful only when the strata share the declared
source interpretation and exact quotient dimension.  If a symmetry opens an
exact null as a parameter changes, the family must be split into separate
strata.  Numerically deleting a tiny eigenvalue is not a substitute for that
algebraic step.

### 2.1 Calibration is part of the experiment

In an \(L^2\)-orthonormal moment-adapted basis with pivot orders
\(r_1,\ldots,r_K\), the calibrated early Gram is

\[
 \widehat G_q
 =D(q)^{-1}\Gamma_q^{\mathrm R}D(q)^{-1},
 \qquad
 D(q)=\operatorname{diag}(q^{r_1},\ldots,q^{r_K}).
 \tag{2.6}
\]

It extends analytically to \(q=0\).  For \(q>0\), the same generalized
spectrum is represented in raw source coordinates by

\[
 \bigl(\Gamma_q^{\mathrm R},D(q)^2\bigr).
 \tag{2.7}
\]

A unit calibrated coordinate in the deepest direction costs
\(q^{-r_K}\) in raw \(L^2\) amplitude.  Thus moment calibration flattens the
causal flag only by changing the declared source cost.  It is an operational
choice, not free information.

---

## 3. Finite certification theorem

Assume on every compact constant-rank stratum that:

1. the entries of \(G_\theta\) and \(S_\theta\) have outward interval
   enclosures on every rational parameter box;
2. the enclosures converge uniformly as the boxes and quadrature panels are
   refined;
3. every noncompact endpoint has a rigorous analytic tail reduction;
4. the exact quotient and source/output metrics are fixed before numerical
   certification; and
5. after exact-null removal, \(G_\theta\succ0\) throughout the stratum.

### Theorem 3.1 — certified generalized atlas floor

For every fixed \(K\) and every requested rational width \(\varepsilon>0\),
there is a finite proof trace producing rational numbers

\[
 0<L_K\le\gamma_K\le U_K,
 \qquad U_K-L_K<\varepsilon.
 \tag{3.1}
\]

#### Proof architecture

Cover every finite parameter region by outward rational boxes.  For a trial
lower bound \(L\), form the interval Hermitian matrix

\[
 [G_\theta]-L[S_\theta].
 \tag{3.2}
\]

Verified positive inertia—by interval \(LDL^*\), a certified pivoted
factorization, or exact-sign leading principal determinants—proves

\[
 G_\theta-LS_\theta\succ0
 \tag{3.3}
\]

throughout the whole box.  Analytic endpoint bounds cover the omitted tails.
Compactness gives a finite cover.  Refinement and uniform convergence make
the accepted lower bounds converge to \(\gamma_K\).

For the upper bound, choose one actual chart point and one exact rational
vector \(v\ne0\).  An outward enclosure of

\[
 \frac{v^*G_\theta v}{v^*S_\theta v}
 \tag{3.4}
\]

is a rigorous atlas upper bound.  Refining around a minimizing parameter and
direction closes the gap.  \(\square\)

The theorem is algorithmic but not vacuous: Sections 4--7 provide analytic
reductions and executable certificates for the declared ramp model.

---

## 4. One common window for three continuous late charts

For \(f\in E_K\), write

\[
 F_f(s)=\int_0^1e^{-sV(x)}f(x)\,dx.
 \tag{4.1}
\]

Define the truncated Laplace Gram

\[
 H_b(f,g)
 =\frac1{2\pi}\int_0^b
 s^{-1/2}F_f(s)\overline{F_g(s)}\,ds.
 \tag{4.2}
\]

Its Hankel kernel is

\[
 K_b(A)=\frac{\operatorname{erf}(\sqrt{Ab})}
 {2\sqrt{\pi A}},
 \qquad A=V(x)+V(y).
 \tag{4.3}
\]

For the standard Gaussian target, the normalized resolved density relative
to (4.2) is

\[
 w_{\mathrm R}(q,s)
 =\sqrt{\frac{1+q}{q}}e^{-s/q}.
 \tag{4.4}
\]

Concavity of
\(\frac12\log(1+1/q)-s/q\) in \(1/q\in[0,1]\) gives, for \(q\ge1\),

\[
 w_{\mathrm R}(q,s)
 \ge c_{\mathrm R}(b)
 :=\min(1,\sqrt2e^{-b}),
 \qquad 0\le s\le b.
 \tag{4.5}
\]

For the one-cell lattice preparation \(Q=\delta_0\), the substitution
\(s=\tau\omega(\theta)\) gives

\[
 w_{\mathrm L}(\tau,s)
 =\frac{2\sqrt{1+\tau}}{\sqrt{4\tau-s}}
 \ge1
 \tag{4.6}
\]

whenever \(\tau\ge1\) and \(0\le s\le b\le4\).  The interior atomic form
contains the same interval.  Therefore

\[
 \boxed{
 \begin{aligned}
  \sqrt{1+q}\,\Gamma_q^{\mathrm R}
    &\succeq c_{\mathrm R}(b)H_b, &&q\ge1,\\
  \sqrt{1+\tau}\,\Gamma_{\tau,\delta_0}^{\mathrm L}
    &\succeq H_b, &&\tau\ge1,\\
  \Gamma_\infty^{\mathrm A}&\succeq H_b.
 \end{aligned}}
 \tag{4.7}
\]

One rigorously validated matrix thus controls two unbounded parameter
families and the interior atomic endpoint simultaneously.

The hypotheses matter.  A general lattice preparation may have zeros in its
characteristic factor \(B_Q\), so (4.6) requires a separately certified
window lower bound.  The reflecting-boundary multiplier contains an
oscillatory cosine term and does not dominate the interior form uniformly.
The boundary family is handled independently in Section 7.

---

## 5. Exact early structure for the affine ramp

Take

\[
 V(x)=1+gx,
 \qquad
 \phi_k(x)=\sqrt2\cos(k\pi x).
 \tag{5.1}
\]

Let

\[
 M_K(g)=\bigl[\langle V^m,\phi_k\rangle\bigr]_{m,k=1}^K.
 \tag{5.2}
\]

Since every cosine port has zero mean,

\[
 M_K(g)=L_K(g)X_K,
 \qquad
 (L_K)_{mr}=\mathbf1_{r\le m}\binom mr g^r,
 \tag{5.3}
\]

where \((X_K)_{rk}=\langle x^r,\phi_k\rangle\).  Hence

\[
 \boxed{
 \det M_K(g)=g^{K(K+1)/2}\det X_K.}
 \tag{5.4}
\]

For the standard Gaussian early endpoint, the calibrated Gram determinant is

\[
 \boxed{
 \det H_K=
 \frac{(\det M_K)^2}{\prod_{i=1}^K(i!)^2}
 \frac1{(2\pi)^K}
 \prod_{j=0}^{K-1}j!\,\Gamma\!\left(j+\frac52\right).}
 \tag{5.5}
\]

Thus

\[
 \det H_K(g)=g^{K(K+1)}C_K(\det X_K)^2
 \tag{5.6}
\]

with an explicit positive constant \(C_K\).  The augmented systems
\(\{1,x,\ldots,x^K\}\) and
\(\{1,\cos(\pi x),\ldots,\cos(K\pi x)\}\), together with the Andréief
determinant argument, make \(\det X_K\ne0\).

Equation (5.6) is a sharp degeneracy law for the determinant as modulation
contrast closes.  It does **not** by itself determine the smallest-eigenvalue
exponent: a determinant is a product of all eigenvalues.

There is nevertheless an exact fixed-band strengthening.  Choose a
moment-adapted orthonormal basis \(e_1,\ldots,e_K\) independently of \(g\),
with

\[
 \langle x^r,e_j\rangle=0\quad(r<j),
 \qquad \langle x^j,e_j\rangle\ne0.
 \tag{5.7}
\]

Then the calibrated endpoint Gram obeys the exact congruence

\[
 H_K^{\mathrm{end}}(g)
 =D_gH_K^{\mathrm{end}}(1)D_g,
 \qquad D_g=\operatorname{diag}(g,g^2,\ldots,g^K).
 \tag{5.8}
\]

If \(\Delta_j\) is the \(j\)-th leading principal determinant of
\(H_K^{\mathrm{end}}(1)\), its descending eigenvalues satisfy, for fixed
\(K\),

\[
 \boxed{
 \lambda_j\bigl(H_K^{\mathrm{end}}(g)\bigr)
 =\frac{\Delta_j}{\Delta_{j-1}}g^{2j}
 \bigl(1+O_K(g^2)\bigr),
 \quad 1\le j\le K.}
 \tag{5.9}
\]

Thus the complete interaction-strength fan is
\(g^2,g^4,\ldots,g^{2K}\) at every fixed band, with leading constants given
by exact Schur pivots.  This fixed-\(K\) statement does not justify
interchanging \(g\downarrow0\) and \(K\to\infty\).

For \(K=2\), the cosine basis is already moment adapted:

\[
 \langle V,\phi_1\rangle\ne0,
 \qquad
 \langle V,\phi_2\rangle=0,
 \qquad
 \langle V^2,\phi_2\rangle\ne0.
 \tag{5.10}
\]

Its pivot orders are exactly \(1,2\), so the early calibration
\(D(q)=\operatorname{diag}(q,q^2)\) is algebraic rather than a numerical rank
decision.

---

## 6. Certified continuous late spectra through eight ports

Set \(g=4/5\).  The checker evaluates (4.2) with Arb validated quadrature,
removing the square-root endpoint by \(s=br^2\).  For a rational proposal
\(L\), it proves

\[
 c_{\mathrm R}(b)H_b-LS\succ0
 \tag{6.1}
\]

directly in the declared metric.  A rational integer Rayleigh vector at an
actual chart point proves the corresponding upper bound.

The following are rounded decimal summaries of exact rational
\(L^2\)-metric certificates.  The exact rationals, rather than these rounded
display values, decide every inequality.  They apply uniformly to every
standard-Gaussian resolved \(q\ge1\), every one-cell lattice \(\tau\ge1\),
and the interior atomic endpoint.

| \(K\) | certified lower | certified upper |
|---:|---:|---:|
| 1 | \(1.31065\times10^{-4}\) | \(5.69203\times10^{-4}\) |
| 2 | \(1.43152\times10^{-7}\) | \(9.94471\times10^{-7}\) |
| 3 | \(1.77650\times10^{-10}\) | \(1.96271\times10^{-9}\) |
| 4 | \(2.23908\times10^{-13}\) | \(3.95391\times10^{-12}\) |
| 5 | \(2.72483\times10^{-16}\) | \(7.96784\times10^{-15}\) |
| 6 | \(2.41218\times10^{-19}\) | \(1.60003\times10^{-17}\) |
| 7 | \(1.53496\times10^{-22}\) | \(3.20199\times10^{-20}\) |
| 8 | \(7.36997\times10^{-26}\) | \(1.82508\times10^{-23}\) |

In the continuum \(H^1\) metric
\(S_{kk}=1+(k\pi)^2\), the certified lower bounds for \(K=1,\ldots,8\)
are

\[
 \begin{aligned}
 &1.20579\times10^{-5},\quad
 3.55231\times10^{-9},\quad
 2.01796\times10^{-12},\quad
 1.48943\times10^{-15},\\
 &1.21070\times10^{-18},\quad
 7.73921\times10^{-22},\quad
 3.74302\times10^{-25},\quad
 1.41495\times10^{-28}.
 \end{aligned}
 \tag{6.2}
\]

All sixteen continuous certificates are generalized-metric statements.
There is no numerical whitening in their proof.

### 6.1 Why binary64 is not evidence of a null

At \(K=8\), the independent high-precision \(H^1\) common-core minimum is
approximately

\[
 3.1443\times10^{-28}.
\]

Ordinary binary64 arithmetic returned the negative value
\(-3.0034\times10^{-28}\) for the same positive-definite Gram.  This sign
failure is not surprising at the attained condition scale.  It demonstrates
why exact symmetry and outward enclosures, rather than a floating rank
threshold, decide nullity.

---

## 7. A complete four-stratum certificate at \(K=2\)

For

\[
 V(x)=1+\frac45x,
 \qquad
 \phi_1=\sqrt2\cos(\pi x),
 \qquad
 \phi_2=\sqrt2\cos(2\pi x),
 \tag{7.1}
\]

declare the strata

\[
\begin{array}{ll}
\text{early resolved:}&
D(q)^{-1}\Gamma_q^{\mathrm R}D(q)^{-1},
\quad 0\le q\le1,\\[1mm]
\text{late resolved:}&
\sqrt{1+q}\,\Gamma_q^{\mathrm R},
\quad 1\le q<\infty,\\[1mm]
\text{one-cell lattice:}&
\sqrt{1+\tau}\,\Gamma_{\tau,\delta_0}^{\mathrm L},
\quad1\le\tau<\infty,\\[1mm]
\text{atomic boundary:}&
\Gamma_\kappa^{\mathrm A},
\quad0\le\kappa\le\infty,
\end{array}
 \tag{7.2}
\]

with \(D(q)=\operatorname{diag}(q,q^2)\).  The early line uses calibrated
moment cost; the other three use raw \(L^2\)-orthonormal cosine cost.

### Theorem 7.1 — certified full-atlas bracket

For the atlas (7.2),

\[
 \boxed{10^{-19}\le\gamma_2\le10^{-6}.}
 \tag{7.3}
\]

#### Lower proof trace

The component lower floors obtained before rational weakening are
approximately

| component | outward lower floor |
|:---|---:|
| calibrated early \(0\le q\le1\) | \(1.40347\times10^{-18}\) |
| late resolved \(q\ge1\) | \(1.33729\times10^{-12}\) |
| one-cell lattice \(\tau\ge1\) | \(4.23793\times10^{-12}\) |
| all reflecting boundaries \(0\le\kappa\le\infty\) | \(3.57225\times10^{-17}\) |

The early inequalities are derived after symbolic cancellation of the powers
of \(q\), so \(q=0\) is included as an analytic endpoint.  The late charts
use the common-window theorem.

The boundary proof checks 1,536 exact dyadic Arb boxes covering
\(0\le\kappa\le3\).  For \(\kappa\ge3\), it uses the analytic interval-mass
bound

\[
 \operatorname{mass}_I(\kappa)
 \ge |I|-\frac1{\pi\kappa}.
 \tag{7.4}
\]

Thus no boundary parameter interval is inferred by interpolation between
sampled points.

#### Upper proof trace

At the actual early chart point \(q=1\), the exact vector

\[
 v=(1,-15)
 \tag{7.5}
\]

has source norm squared \(226\).  A 1,024-box Arb integral plus an analytic
Gaussian tail proves

\[
 \frac{v^*G_1v}{v^*v}
 <7.388788\times10^{-7}<10^{-6}.
 \tag{7.6}
\]

Equations (7.4)--(7.6), exact rational comparisons, and repeated 256-bit
execution independently verify (7.3).

The theorem is for the continuum phase Grams.  It contains no finite-grid
transfer error, finite-sensor frame, target family, general lattice
preparation, or \(K\ge3\) full-atlas claim.

---

## 8. Effective rank and information budgets

For a threshold \(\eta>0\), the number of generalized eigenvalues above
\(\eta\) equals the positive inertia of

\[
 G-\eta S.
 \tag{8.1}
\]

Verified interval inertia therefore certifies effective rank without
diagonalizing an ill-conditioned interval matrix.  The executable audit uses
the exact thresholds

\[
 10^{-4},10^{-8},10^{-12},10^{-16},10^{-20},10^{-24},10^{-28}.
 \tag{8.2}
\]

This turns the abstract phrase ``observable dimension'' into a declared
noise-and-cost-dependent integer.

For a known \(S\)-unit source direction \(u\), amplitude \(a\), independent
whitened Gaussian output noise of standard deviation \(\sigma\), and \(N\)
repetitions, the simple-versus-simple Bayes error is

\[
 \Phi\!\left(
 -\frac{a\sqrt{N\,u^*Gu}}{2\sigma}
 \right).
 \tag{8.3}
\]

If \(z_\alpha=\Phi^{-1}(1-\alpha)\), a certified lower floor \(L\) gives the
sufficient uniform budget

\[
 \boxed{
 N\ge\frac{4\sigma^2z_\alpha^2}{a^2L}.}
 \tag{8.4}
\]

A certified upper witness \(U\) proves that no uniform guarantee is possible
when

\[
 \boxed{
 N<\frac{4\sigma^2z_\alpha^2}{a^2U}.}
 \tag{8.5}
\]

Amplitude, source cost, output whitening, and noise must all use the same
declared metrics.  Equations (8.4)--(8.5) do not cover unknown backgrounds,
unknown support, composite alternatives, or nonlinear recovery.

---

## 9. Asymptotic information loss

The Stage IX phase maps are compact.  For the declared truncated-Laplace and
fixed one-cell lattice exponential maps, Stage X sharpens the generic
analytic upper ceiling to a squared-factorial one and pairs it with a
completely explicit, though nonmatching, truncated-Laplace lower bound.

For the truncated Laplace response

\[
 (T_{b,g}f)(s)=\int_0^1e^{-s(1+gx)}f(x)\,dx,
 \qquad d\nu_b(s)=\frac{ds}{2\pi\sqrt s},
 \tag{9.1}
\]

write
\(H_{b,g}=T_{b,g}^*T_{b,g}\) and let \(\lambda_{K,b}(g)\) be its
smallest eigenvalue on the first \(K\) cosine ports.

### 9.1 Squared-factorial ceilings

A Chebyshev--Bessel approximation on the mean-zero source space proves

\[
 \boxed{
 \lambda_{K,b}(g)
 \le A_{b,g}^2\frac{(gb/4)^{2K}}{(K!)^2},}
 \qquad
 A_{b,g}=\frac{2b^{1/4}}{\sqrt\pi}
 e^{g^2b^2/16+gb/4}.
 \tag{9.2}
\]

At a fixed one-cell lattice time \(\tau>0\), the analogous bound is

\[
 \boxed{
 \lambda_{K,\tau}^{\mathrm L}(g)
 \le A_{\tau,g}^2\frac{(g\tau)^{2K}}{(K!)^2},
 \qquad A_{\tau,g}=2e^{g^2\tau^2+g\tau}.}
 \tag{9.3}
\]

A preparation multiplier with \(|B_Q|\le1\) preserves this upper bound.
Since the full atlas infimum contains any one declared fixed lattice point,
(9.3) is also a squared-factorial upper ceiling for its global floor, up to
the fixed chart normalization.

### 9.2 Explicit lower frame and determinant scale

A separated exponential/cosine sampling frame, continuous Andréief identity,
and approximation-number deflation give a displayed positive number
\(L_{K,b}(g)\) such that

\[
 \boxed{
 e^{-C_{b,g}K^2}
 \le L_{K,b}(g)
 \le\lambda_{K,b}(g).}
 \tag{9.4}
\]

The same proof determines the determinant scale

\[
 \boxed{
 \log\det\bigl(H_{b,g}|_{E_K}\bigr)
 =-K^2\log K+O_{b,g}(K^2).}
 \tag{9.5}
\]

This explains a practical feature of the finite certificates.  The
determinant is not numerically ``failing''; converting its product of
eigenvalues into the final eigenvalue using only a trace bound loses the
correct scale.  Deflating with individual approximation-number bounds
improves the lower theorem to (9.4), but a large gap remains between
\(e^{-O(K^2)}\) and the squared-factorial upper bound.

### 9.3 A falsifiable constant conjecture

High-precision nested-band calculations suggest

\[
 \boxed{
 \lim_{K\to\infty}
 \frac{K\sigma_K(T_{b,g}|_{E_K})}
 {\sigma_{K-1}(T_{b,g}|_{E_{K-1}})}
 =\frac{gb}{6\pi},}
 \tag{9.6}
\]

and, for the one-cell lattice,

\[
 \boxed{
 \lim_{K\to\infty}
 \frac{K\sigma_K(T_{\tau,g}^{\mathrm L}|_{E_K})}
 {\sigma_{K-1}(T_{\tau,g}^{\mathrm L}|_{E_{K-1}})}
 =\frac{2g\tau}{3\pi}.}
 \tag{9.7}
\]

These are **numerical conjectures**, not certified asymptotics.  Calculations
through \(K=40\) support the second constant and separate checks show linear
scaling in \(g\) and \(\tau\), but two proofs are missing: the source
moment-pivot limit \(2/(3\pi)\), and uniform control of off-flag response
terms.  Neither (9.2) nor (9.4) determines the conjectured constant.

---

## 10. Finite-model transfer

Let \(G_h\) be a finite-grid Gram in the same declared source coordinates and
metric as a certified continuum Gram \(G\).  The relevant error is

\[
 \delta_K(h)
 =\left\|S^{-1/2}(G_h-G)S^{-1/2}\right\|.
 \tag{10.1}
\]

Generalized Weyl perturbation gives

\[
 \lambda_{\min}(G_h,S)
 \ge L_K-\delta_K(h).
 \tag{10.2}
\]

Consequently, a continuum certificate transfers only when

\[
 \boxed{\delta_K(h)<L_K.}
 \tag{10.3}
\]

For relative spectral accuracy one needs \(\delta_K=o(\gamma_K)\), precisely
the Stage IX growing-band criterion.  An unweighted entrywise Gram error is
not enough when the source metric is non-Euclidean.

In the early chart, finite transfer must additionally control spatial
resolution, discrete moment leakage, and mixed words in the algebra generated
by diffusion \(A\) and multiplication \(V\).  Pure moment cancellation alone
does not eliminate terms such as \(V^jA\).  Stage X deliberately leaves the
validated finite-\(h\) enclosure of these errors as the next theorem.

---

## 11. Adversarial controls

The independent audit includes exact or executable counterexamples to the
most tempting shortcuts.

| Shortcut | Failure |
|:---|:---|
| certify ordinary eigenvalues after whitening | a coordinate change alters them unless the transformed source metric is retained |
| sample a fine parameter grid | an arbitrarily narrow positive dip can lie between samples |
| use endpoint eigenvalues of an interval matrix | entrywise extrema need not enclose spectral extrema |
| declare a binary64 rank | an exactly positive Hilbert Gram can acquire a false numerical null |
| trust high precision alone | precision does not enclose quadrature tails or uncovered parameters |
| apply the interior common window to every boundary | the boundary cosine multiplier is not positive semidefinite |
| let modulation contrast or sensor rank vanish | the generalized floor collapses exactly |
| use an absolute Gram error for transfer | the correct perturbation is relative to the source metric |

For the boundary-window failure, a two-level modulation and a zero-mean
source give a finite \(\kappa\) at which the reflecting form is smaller than
the proposed interior truncated form.  This is why the complete \(K=2\)
proof certifies the boundary family separately.

All eight adversarial controls pass.

---

## 12. Computational audit

The Stage X evidence is separated into two proof packages.

### 12.1 Moderate-band late core

`oig_x_spectral_certificate.py` proves:

- 16 continuous late-core certificates: \(K=1,\ldots,8\) in two source
  metrics;
- 64 fixed chart/metric/band certificates;
- interval-inertia effective ranks;
- rational Rayleigh upper witnesses;
- analytic tail and ball-radius bounds; and
- Gaussian repetition inequalities.

The default 320-bit run takes about two seconds on the reference machine.
All seven focused tests pass.

### 12.2 Complete two-port atlas

`oig_x_full_atlas_certificate.py` proves:

- exact source orthonormality, moment pivots, and ramp-degeneracy powers;
- analytic coverage of calibrated \(q\in[0,1]\);
- the two unbounded late families through the common window;
- 1,536 boundary boxes and an analytic \(\kappa\ge3\) tail;
- the exact rational lower and upper comparisons in (7.3); and
- repeatability at higher precision.

All eight focused tests pass.  Together with the eight adversarial controls,
the two certificate packages contain 23 passing tests.

### 12.3 Asymptotic conjecture laboratory

`oig_x_spectral_asymptotics.py` independently evaluates the exact cosine
moment recurrence, source-pivot ratios, nested truncated-Laplace singular
ratios, and lattice \(g\)/\(\tau\) scaling controls with mpmath.  Its five
tests reproduce reference values and enforce the theorem/conjecture label.
These calculations are high-precision evidence, not outward certificates.
The complete focused Stage X suite therefore contains 28 passing tests.

The proof scripts use `python-flint` Arb balls.  NumPy and mpmath values in
the reports are descriptive cross-checks and witness-discovery aids; they do
not decide any theorem inequality.

---

## 13. Falsification ledger

| Tempting statement | Correct boundary |
|:---|:---|
| every positive sampled spectrum has a positive continuous infimum | false without a validated cover and endpoint tails |
| whitening improves information | false unless its source and noise costs are retained |
| the late \(K\le8\) table certifies the full atlas | false; full early/boundary coverage is proved only for \(K=2\) here |
| the \(K=2\) theorem certifies a finite grid | false; it concerns continuum phase Grams |
| the common window covers arbitrary lattice preparation | false when \(B_Q\) has a window zero |
| the common window covers all reflecting boundaries | false; the cosine image term can lower a quadratic form |
| positivity through \(K=8\) suggests infinite coercivity | false; compactness forces the floor to zero |
| the determinant contrast power determines \(\lambda_{\min}\) | false; it only fixes the product of eigenvalues |
| the factorial ceiling is a two-sided asymptotic | false; no matching lower constant is proved |
| a tiny numerical eigenvalue is an analytic null | unsupported without exact symmetry or certified arithmetic |
| this spectrum describes fundamental spacetime | unsupported; it belongs to the declared operational model |

---

## 14. Interpretation

Stage IX distinguished algebraic, stable, and sampled visibility.  Stage X
adds a fourth distinction: **certified visibility**.

- Algebraic visibility asks whether a direction survives the exact quotient.
- Stable visibility asks whether its generalized singular value exceeds the
  declared error and noise scales.
- Sampled visibility asks whether a finite sensor frame retains it.
- Certified visibility supplies a finite proof that the relevant inequality
  holds throughout a continuous parameter family.

This is useful because the dangerous scale is not the largest response but
the weakest surviving one.  The same operational model can be exactly
injective, severely ill-conditioned, and practically informative in only a
few directions.  The generalized spectrum and its effective rank state all
three facts without contradiction.

The result also sharpens the bridge between abstract geometry and
measurement.  The quotient says which distinctions exist; the chart says how
scale exposes them; the source and output metrics price the experiment; the
certificate says what finite computation has actually proved.

No claim is made that this construction is a fundamental law of nature.  It
is a mathematically explicit laboratory for how operational distinctions,
scale, cost, and noise interact.

---

## 15. Literature and novelty boundary

Validated numerical linear algebra and interval matrix certification are
established subjects.  Relevant references include:

- S. M. Rump, *Verification methods: rigorous results using floating-point
  arithmetic*, Acta Numerica 19 (2010), 287--449,
  <https://doi.org/10.1017/S096249291000005X>.
- M. Hladík, *Positive semidefiniteness and positive definiteness of a linear
  parametric interval matrix*, arXiv:1704.05782,
  <https://arxiv.org/abs/1704.05782>.
- I. Skalna, *A method for checking the positive definiteness of interval
  matrices*, arXiv:1709.00853,
  <https://arxiv.org/abs/1709.00853>.
- C. Berg and R. Szwarc, *The smallest eigenvalue of Hankel matrices*,
  Constructive Approximation 34 (2011), 107--133,
  <https://arxiv.org/abs/0906.4506>.
- R. R. Lederman and V. Rokhlin, *On the analytical and numerical properties
  of the truncated Laplace transform I*, SIAM Journal on Numerical Analysis
  53 (2015), 1214--1235,
  <https://doi.org/10.1137/140990681>.

No priority claim is made for generalized eigenvalues, interval inertia,
Andréief identities, total positivity, analytic kernel approximation, or
truncated-Laplace ill-posedness.  The provisional contribution is their
assembly for the declared operational atlas: the coordinate-invariant
certification theorem, the common continuous late-window reduction, the exact
ramp contrast law, the moderate-band Arb spectrum, the complete \(K=2\)
four-stratum certificate, and the direct conversion to effective rank and
information budgets.  Literature novelty remains provisional pending
independent specialist review.

---

## 16. Reproduction

Install the repository dependencies and run the Stage X suites:

```text
python -m pip install -r requirements.txt
python -m py_compile \
  oig_x_spectral_certificate.py \
  oig_x_full_atlas_certificate.py \
  oig_x_spectral_asymptotics.py \
  test_oig_x_spectral_certificate.py \
  test_oig_x_full_atlas_certificate.py \
  test_oig_x_spectral_asymptotics.py \
  test_oig_x_adversarial_controls.py
python -m unittest -v test_oig_x_spectral_certificate.py
python -m unittest -v test_oig_x_full_atlas_certificate.py
python -m unittest -v test_oig_x_spectral_asymptotics.py
python -m unittest -v test_oig_x_adversarial_controls.py
python oig_x_spectral_certificate.py --max-band 8 --precision-bits 320
python oig_x_full_atlas_certificate.py --precision-bits 192
python oig_x_spectral_asymptotics.py --maximum-band 12 --digits 100
python -m unittest discover -v
```

For only the Stage X checkers, the narrower dependency surface is recorded in
`oig_x_spectral_certificate_requirements.txt`.  The root requirements are
used above because the final command discovers every earlier repository test.

The optional `--fast` flag on the moderate-band checker changes only
descriptive mpmath work.  It does not weaken Arb quadrature, tail bounds,
generalized shifts, inertia, or Rayleigh checks.

Detailed sources:

- `OIG_X_CERTIFIED_SPECTRUM_THEOREM.md` — analytic certification theorem;
- `OIG_X_SPECTRAL_ASYMPTOTICS.md` — factorial ceilings, explicit lower
  frame, exact interaction fan, and constant conjecture;
- `oig_x_spectral_asymptotics.py` — high-precision recurrence and nested-band
  evidence for the explicitly conjectural constants;
- `oig_x_spectral_certificate.md` — continuous late-core proof trace and
  tables;
- `oig_x_full_atlas_certificate.md` — complete \(K=2\) proof trace; and
- `OIG_X_ADVERSARIAL_AUDIT.md` — independent counterexamples and scope audit.

---

## 17. Next research order

1. **Certify finite-model transfer — begun in Stage XI.**  Stage XI proves the
   metric-normalized transfer theorem, closes the complete one-port
   finite-Neumann crossing at \(n=7\), and isolates the two-port full-model
   enclosure as the next finite certificate.
2. **Optimize certified effective rank.**  Choose multiple times and target
   profiles to maximize the number of eigenvalues above a declared noise
   threshold while fixing source cost and output whitening in advance.
3. **Extend the complete atlas beyond two ports.**  Replace the specialized
   two-port boundary frame by verified matrix-valued Taylor models and
   interval inertia for \(K=3,4,\ldots\).
4. **Resolve the early lattice endpoint.**  Construct its calibrated moment
   filtration and connect it rigorously to the two-frequency transition.
5. **Study the factorial spectrum.**  Prove or falsify the source-pivot limit
   \(2/(3\pi)\), then control the off-flag response matrix uniformly in
   \(K\); keep (9.6)--(9.7) conjectural until both steps close.
6. **Develop finite-frame sensing.**  Certify time/profile sample counts that
   preserve continuum effective rank instead of assuming a complete density
   output.
7. **Build the full causal-word filtration.**  Replace pure multiplication
   moments by the noncommutative algebra generated by \(A\) and \(V\).
8. **Continue to path-space and wave sensing.**  Only after the parabolic
   finite-transfer problem is controlled, test jump-history ports and
   finite-speed analogues.

Stage XI completes the abstract transfer theorem and the first full finite
crossing.  Its immediate continuation is to certify the observed two-port
full-Neumann crossing, then extend the enclosure across lattice time, early
calibration, reflecting boundaries, and finite sensor frames.
