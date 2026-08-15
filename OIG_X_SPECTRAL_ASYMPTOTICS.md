# Operational Information Geometry X — spectral asymptotics

## Factorial ceilings, explicit lower frames, and the unresolved cosine constant

**Status:** analytic extension memo; not peer reviewed

**Scope:** canonical affine ramp, raw \(L^2\) cosine source metric

**Epistemic rule:** statements called theorems are proved below.  The constant
\(2/(3\pi)\) is a numerical conjecture, not a theorem.

---

## 1. Results

Let

\[
 V_g(x)=1+gx,\qquad g>0,\qquad
 E_K=\operatorname{span}\{\sqrt2\cos(k\pi x):1\le k\le K\}.
\]

For the truncated Laplace response

\[
 (T_{b,g}f)(s)=\int_0^1e^{-s(1+gx)}f(x)\,dx,\qquad
 d\nu_b(s)=\frac{ds}{2\pi\sqrt s},\quad 0<s<b,
\]

write \(H_{b,g}=T_{b,g}^*T_{b,g}\) and
\(\lambda_{K,b}(g)=\lambda_{\min}(H_{b,g}|_{E_K})\).
This memo proves:

1. A rank-\((K-1)\) Chebyshev approximation gives

   \[
   \boxed{\lambda_{K,b}(g)
   \le A_{b,g}^2\frac{(gb/4)^{2K}}{(K!)^2}.}
   \tag{1.1}
   \]

   The fixed-\(\tau\) one-cell lattice has the analogous ceiling
   \(A_{\tau,g}^2(g\tau)^{2K}/(K!)^2\).  A single such atlas point makes the
   global atlas floor at most squared-factorial, sharper than a generic
   geometric analytic-kernel ceiling.

2. A separated sampling frame, followed by approximation-number deflation,
   gives a fully explicit \(L_{K,b}(g)>0\) with

   \[
   \boxed{L_{K,b}(g)\le\lambda_{K,b}(g),\qquad
   \log L_{K,b}(g)\ge-C_{b,g}K^2.}
   \tag{1.2}
   \]

3. The determinant itself has the sharp logarithmic scale

   \[
   \boxed{\log\det(H_{b,g}|_{E_K})
   =-K^2\log K+O_{b,g}(K^2).}
   \tag{1.3}
   \]

   Thus determinant certification is not numerically failing.  The large
   loss occurs when its product of eigenvalues is converted to the last
   eigenvalue with only a trace bound.

4. At the calibrated early endpoint, affine-ramp dependence is an exact
   diagonal congruence.  Its descending fixed-\(K\) eigenvalues have powers
   \(g^2,g^4,\ldots,g^{2K}\), with leading Schur-pivot constants.

5. High-precision calculations suggest, but do not prove,

   \[
   \frac{K\sigma_K}{\sigma_{K-1}}\to\frac{gb}{6\pi}
   \quad(H_b),\qquad
   \frac{K\sigma_K}{\sigma_{K-1}}\to\frac{2g\tau}{3\pi}
   \quad(\text{one-cell lattice}).
   \tag{1.4}
   \]

---

## 2. Factorial approximation numbers

Put

\[
 W_b=\frac{\sqrt b}{\pi},\qquad C=gb,\qquad R=\frac{gb}{4},
\]

\[
 \boxed{A_{b,g}=
 \frac{2b^{1/4}}{\sqrt\pi}
 \exp\!\left(\frac{g^2b^2}{16}+\frac{gb}{4}\right).}
 \tag{2.1}
\]

Eigenvalues and singular values are ordered descending in this memo.

### Lemma 2.1 — uniform Chebyshev remainder

For \(0\le c\le C\) and integer \(n\ge0\), a polynomial \(p_{n-1,c}\) of
degree at most \(n-1\) satisfies

\[
 \boxed{\sup_{0\le x\le1}|e^{-cx}-p_{n-1,c}(x)|
 \le2e^{C^2/16+C/4}\frac{(C/4)^n}{n!}.}
 \tag{2.2}
\]

#### Proof

Use

\[
 e^{-cx}=e^{-c/2}\left[
 I_0(c/2)+2\sum_{m\ge1}(-1)^mI_m(c/2)T_m(2x-1)\right].
\]

The power series of \(I_m\) gives

\[
 I_m(c/2)\le\frac{(c/4)^m}{m!}e^{c^2/16},
\]

and

\[
 \sum_{m\ge n}\frac{(C/4)^m}{m!}
 \le\frac{(C/4)^n}{n!}e^{C/4}.
\]

Truncate before degree \(n\), use \(|T_m|\le1\), and drop
\(e^{-c/2}\le1\).  The right side also covers \(n=0\).  \(\square\)

### Theorem 2.2 — mean-zero factorial ceiling

On the mean-zero subspace of \(L^2(0,1)\),

\[
 \boxed{\sigma_j(T_{b,g})\le A_{b,g}\frac{R^j}{j!},\qquad j\ge1.}
 \tag{2.3}
\]

Consequently,

\[
 \boxed{\lambda_{K,b}(g)
 \le A_{b,g}^2\frac{R^{2K}}{(K!)^2}.}
 \tag{2.4}
\]

#### Proof

Apply Lemma 2.1 with \(c=gs\) and multiply by \(e^{-s}\).  A degree
\((j-1)\) polynomial normally has response rank at most \(j\).  Its constant
coefficient vanishes on mean-zero sources, so the restricted rank is at most
\(j-1\).  The Hilbert--Schmidt error is at most \(\sqrt{W_b}\) times (2.2),
namely \(A_{b,g}R^j/j!\).  The approximation-number variational principle
proves (2.3), and restriction to \(E_K\) proves (2.4).  \(\square\)

### Corollary 2.3 — factorial lattice and atlas ceiling

For

\[
 (T_{\tau,g}^{\rm L}f)(\theta)
 =\int_0^1e^{-\tau\omega(\theta)(1+gx)}f(x)\,dx,\qquad
 \omega(\theta)=4\sin^2(\theta/2),
\]

in \(L^2([0,\pi],d\theta/\pi)\), define

\[
 A_{\tau,g}=2e^{g^2\tau^2+g\tau}.
\]

Then

\[
 \boxed{\lambda_{\min}
 ((T_{\tau,g}^{\rm L})^*T_{\tau,g}^{\rm L}|_{E_K})
 \le A_{\tau,g}^2\frac{(g\tau)^{2K}}{(K!)^2}.}
 \tag{2.5}
\]

Indeed \(0\le g\tau\omega\le4g\tau\), so Lemma 2.1 has
\(C=4g\tau\) and \(C/4=g\tau\).  A preparation multiplier
\(|B_Q|\le1\) preserves this upper bound.  If a fixed \(\tau_0\) belongs to
the atlas, its global Gram floor is no larger than (2.5), multiplied only by
the declared fixed chart normalization.

The atomic output variable is unbounded, so this factorial proof does not
extend to it.  The atomic kernel has a finite complex singularity and gives a
geometric analytic-kernel ceiling instead.  The global atlas floor
nevertheless has a squared-factorial upper ceiling because the atlas contains
the bounded-phase lattice member.

---

## 3. Explicit sampling determinant

Let

\[
 \phi_0=1,\qquad\phi_k=\sqrt2\cos(k\pi x),\qquad
 \widetilde E_N=\operatorname{span}\{\phi_0,\ldots,\phi_{N-1}\},
\]

and set \(N=K+1\),

\[
 P_N=\frac{N(N-1)}2,\qquad
 \mathcal V_N=\prod_{j=1}^{N-1}j!.
 \tag{3.1}
\]

### Lemma 3.1 — separated exponential/cosine determinant

For \(a,j=0,\ldots,N-1\), choose

\[
 I_a=\left[\frac b4+\frac{ab}{2N},
 \frac b4+\frac{ab}{2N}+\frac b{4N}\right],
\quad
 J_j=\left[\frac14+\frac{j}{2N},
 \frac14+\frac{j}{2N}+\frac1{4N}\right].
\]

If \(s_a\in I_a\), then

\[
 \left|\det\left[
 \int_0^1e^{-s_a(1+gx)}\phi_k(x)\,dx
 \right]_{a,k=0}^{N-1}\right|\ge d_N,
 \tag{3.2}
\]

where

\[
 \boxed{d_N=
 e^{-3(1+g)bN/4}g^{P_N}b^{P_N}
 2^{(N-1)(3N-2)/4}
 \frac{\mathcal V_N^2}{(4N)^{3P_N+N}}.}
 \tag{3.3}
\]

#### Proof

Continuous Cauchy--Binet expresses (3.2) as an integral on
\(0<x_0<\cdots<x_{N-1}<1\) of an exponential determinant times a cosine
determinant.  Both have fixed sign.  Factoring

\[
 e^{-s(1+gx)}=e^{-(1+g)s}e^{gs(1-x)}
\]

and retaining the first generalized-Vandermonde term in the positive
power-series Cauchy--Binet expansion gives

\[
 |\det[e^{-s_a(1+gx_j)}]|
 \ge e^{-(1+g)\sum_as_a}
 \frac{g^{P_N}\Delta(s)\Delta(x)}{\mathcal V_N}.
 \tag{3.4}
\]

The normalized cosine determinant is

\[
 |\det[\phi_k(x_j)]|
 =2^{(N-1)^2/2}
 \prod_{i<j}|\cos(\pi x_i)-\cos(\pi x_j)|.
\]

On the selected boxes,

\[
 x_j-x_i\ge\frac{j-i}{4N},\quad
 s_j-s_i\ge\frac{b(j-i)}{4N},\quad
 |\cos(\pi x_i)-\cos(\pi x_j)|\ge\sqrt2(x_j-x_i).
\]

Use \(s_a\le3b/4\), input volume \((4N)^{-N}\), and
\(\prod_{i<j}(j-i)=\mathcal V_N\).  Collecting factors gives (3.3).
\(\square\)

### Corollary 3.2 — cosine determinant lower

Each \(I_a\) has \(\nu_b\)-mass at least

\[
 \boxed{\mu_N=\frac{\sqrt b}{4\pi\sqrt3\,N}.}
 \tag{3.5}
\]

The separated-output Andréief bound gives

\[
 \det(H_{b,g}|_{\widetilde E_N})\ge d_N^2\mu_N^N.
 \tag{3.6}
\]

The augmented constant-source diagonal is at most
\(W_b=\sqrt b/\pi\).  A Schur complement therefore yields

\[
 \boxed{\det(H_{b,g}|_{E_K})
 \ge D_{K,b}(g):=\frac{\pi}{\sqrt b}\,
 d_{K+1}^2\mu_{K+1}^{K+1}.}
 \tag{3.7}
\]

---

## 4. A deflated lower bound and the determinant obstruction

### Theorem 4.1 — explicit \(e^{-O(K^2)}\) lower bound

For every \(K\ge1\),

\[
 \boxed{\lambda_{K,b}(g)\ge L_{K,b}(g):=
 D_{K,b}(g)
 \frac{\displaystyle\prod_{j=1}^{K-1}(j!)^2}
 {A_{b,g}^{\,2(K-1)}R^{K(K-1)}}.}
 \tag{4.1}
\]

For fixed \(b,g>0\), there is a finite \(C_{b,g}\) such that

\[
 \boxed{\lambda_{K,b}(g)\ge e^{-C_{b,g}K^2}.}
 \tag{4.2}
\]

#### Proof

Let \(\lambda_1\ge\cdots\ge\lambda_K\) be the eigenvalues on \(E_K\).
Theorem 2.2 gives

\[
 \lambda_j\le A_{b,g}^2\frac{R^{2j}}{(j!)^2},
 \qquad1\le j<K.
\]

Divide (3.7) by the product of these \(K-1\) upper bounds.  This proves
(4.1).  Stirling's formula and

\[
 \log\mathcal V_N
 =\frac12N^2\log N-\frac34N^2+O(N\log N)
\]

show that all \(K^2\log K\) terms cancel in (4.1), proving (4.2).
\(\square\)

The exact powers also recover the correct interaction-collapse factor
\(g^{2K}\): the determinant contributes \(g^{K(K+1)}\), while deflation of
the first \(K-1\) channels contributes \(g^{K(K-1)}\).

### Corollary 4.2 — three late-chart lower bounds

For the standard Gaussian resolved chart,

\[
 \sqrt q\,\Gamma_q^{\rm R}\succeq e^{-b/q_0}H_b,\qquad q\ge q_0>0.
\]

For the normalized one-cell lattice and interior atomic charts,

\[
 \sqrt\tau\,\Gamma_\tau^{\rm L}\succeq H_b
 \quad(b\le4\tau),\qquad
 \Gamma_\infty^{\rm A}\succeq H_b.
\]

Thus (4.1) supplies explicit \(e^{-O(K^2)}\) lower bounds for all three raw
\(L^2\) cosine compressions, with the displayed constants.  A general
lattice preparation additionally needs \(|B_Q|\ge\beta>0\) on the comparison
window, multiplying the Gram lower by \(\beta^2\).

No such positive-form comparison is asserted for finite boundary coordinate
\(\kappa\): its cosine correction is not positive semidefinite.

### Theorem 4.3 — sharp determinant logarithmic scale

For fixed \(b,g>0\),

\[
 \boxed{\log\det(H_{b,g}|_{E_K})
 =-K^2\log K+O_{b,g}(K^2).}
 \tag{4.3}
\]

#### Proof

The lower half is (3.7).  For the upper half, multiply the \(K\) ceilings
from Theorem 2.2:

\[
 \det(H_{b,g}|_{E_K})
 \le A_{b,g}^{2K}
 \frac{R^{K(K+1)}}{\prod_{j=1}^K(j!)^2}.
\]

Now
\(\sum_{j\le K}\log(j!)=\tfrac12K^2\log K+O(K^2)\).
\(\square\)

### Proposition 4.4 — why determinant--trace is too conservative

If a response has the factorial hierarchy

\[
 \sigma_j=\exp(o(j))\frac{c^j}{j!},
\]

then its true last Gram eigenvalue obeys

\[
 \log\lambda_K=-2K\log K+O(K),
\]

whereas the determinant--trace lower bound has logarithm

\[
 -K^2\log K+O(K^2).
\]

This is an algebraic implication, not an assumption that the canonical Gram
has already been proved to possess that hierarchy.  It shows that even a
sharp determinant such as (4.3) loses a factor of order \(K\) in the leading
logarithmic exponent when all earlier eigenvalues are bounded only by the
trace.  The individual approximation-number deflation in Theorem 4.1
improves the result to \(e^{-O(K^2)}\), but does not yet give a factorial
lower law.

---

## 5. Exact affine-ramp dependence at fixed \(K\)

### Theorem 5.1 — exact endpoint congruence and eigenvalue fan

For \(g\ne0\), the filtration generated by \((1+gx)^m\) equals that generated
by \(x^m\).  Hence a moment-adapted orthonormal basis
\(e_1,\ldots,e_K\) can be chosen independently of \(g\), with

\[
 \langle x^r,e_j\rangle=0\quad(r<j),\qquad
 \xi_j:=\langle x^j,e_j\rangle\ne0.
\]

If \(H_K^{\rm end}(g)\) is the Gaussian calibrated early-endpoint Gram, then

\[
 \boxed{H_K^{\rm end}(g)=D_gH_K^{\rm end}(1)D_g,\qquad
 D_g=\operatorname{diag}(g,g^2,\ldots,g^K).}
 \tag{5.1}
\]

Let \(\Delta_j\) be the \(j\)-th leading principal determinant of
\(H_K^{\rm end}(1)\), with \(\Delta_0=1\).  As \(g\downarrow0\), the
descending eigenvalues satisfy

\[
 \boxed{\lambda_j(H_K^{\rm end}(g))
 =\frac{\Delta_j}{\Delta_{j-1}}g^{2j}
 (1+O_K(g^2)),\qquad1\le j\le K.}
 \tag{5.2}
\]

For all \(0<g\le1\),

\[
 g^{2K}\lambda_{\min}(H_K^{\rm end}(1))
 \le\lambda_{\min}(H_K^{\rm end}(g))
 \le g^{2K}(H_K^{\rm end}(1))_{KK}.
 \tag{5.3}
\]

#### Proof

The binomial change from \(x^r\) to \((1+gx)^m\) is lower triangular with
diagonal \(g^m\).  Lower moments vanish on \(e_j\), so
\(\langle(1+gx)^j,e_j\rangle=g^j\xi_j\).  At the calibrated endpoint the
Gram entries have the form

\[
 (H_K^{\rm end})_{ij}
 =C_{ij}\,
 \frac{\langle V^i,e_i\rangle}{i!}
 \frac{\langle V^j,e_j\rangle}{j!},
\]

with \(C_{ij}\) independent of \(g\), proving (5.1).
Successive symmetric elimination, equivalently the Newton polygon of the
principal-minor expansion, proves (5.2); its constants are the successive
\(LDL^*\) pivots \(\Delta_j/\Delta_{j-1}\).  The minimum diagonal entry of
\(D_g\) and the last-coordinate Rayleigh quotient give (5.3).
\(\square\)

This is stronger than the determinant identity
\(\det H_K^{\rm end}(g)=g^{K(K+1)}\det H_K^{\rm end}(1)\): it resolves every
fixed-\(K\) interaction exponent and leading constant.

### Theorem 5.2 — fixed-\(K\) response flag

Let \(Y\) be a chart output Hilbert space for which

\[
 T_gf=\sum_{r\ge1}\frac{(-g)^r}{r!}
 y_r\langle x^r,f\rangle
 \tag{5.4}
\]

converges in operator norm near \(g=0\), and suppose
\(y_1,\ldots,y_K\) are independent.  Define

\[
 \zeta_j=\operatorname{dist}
 (y_j,\operatorname{span}\{y_1,\ldots,y_{j-1}\}).
\]

Then, for fixed \(K\),

\[
 \boxed{\sigma_j(T_g|_{E_K})
 =\frac{|\xi_j|\zeta_j}{j!}|g|^j
 (1+O_K(|g|)),\qquad1\le j\le K.}
 \tag{5.5}
\]

Indeed the unique lowest-order term of the \(j\)-th exterior power uses
moment orders \(1,\ldots,j\).  Its input and output Gram--Schmidt volumes are
\(\prod_{r\le j}|\xi_r|\) and \(\prod_{r\le j}\zeta_r\).  Ratios of
successive exterior-power norms give (5.5).

This is a fixed-\(K\) theorem.  It gives no bound on the \(O_K\) constant and
therefore cannot justify an exchange of \(g\downarrow0\) with
\(K\to\infty\).

---

## 6. The \(2/(3\pi)\) numerical conjecture

### 6.1 Exact audit recurrence

Let

\[
 I_{m,k}=\int_0^1x^m\cos(k\pi x)\,dx.
\]

Integration by parts gives

\[
 I_{0,k}=0,\qquad
 I_{1,k}=\frac{(-1)^k-1}{(k\pi)^2},
\]

\[
 \boxed{I_{m,k}=\frac{m(-1)^k}{(k\pi)^2}
 -\frac{m(m-1)}{(k\pi)^2}I_{m-2,k},\qquad m\ge2.}
 \tag{6.1}
\]

For \(X_K=(\sqrt2I_{m,k})_{m,k=1}^K\), the last row-QR pivot is

\[
 \xi_K=
 \frac{|\det X_K|}
 {\sqrt{\det(X_K^{<K}(X_K^{<K})^*)}},
 \tag{6.2}
\]

where \(X_K^{<K}\) contains the first \(K-1\) rows.  High-precision
arithmetic gives:

| \(K\) | \(\xi_K/\xi_{K-1}\) |
|---:|---:|
| 10 | 0.217383837671205 |
| 20 | 0.213836030193609 |
| 30 | 0.212818500136561 |
| 40 | 0.212332936581949 |

The apparent limit is

\[
 \frac2{3\pi}=0.212206590789194\ldots.
\]

These values are high-precision evaluations, not outward-rounded interval
certificates.

### 6.2 Response-ratio evidence

For \(g=0.8\), direct high-precision quadrature gives:

| \(b\) | \(K=8\) | \(K=10\) | \(K=12\) | \(gb/(6\pi)\) |
|---:|---:|---:|---:|---:|
| 1 | 0.0436584 | 0.0433158 | 0.0431065 | 0.0424413 |
| 4 | 0.1752970 | 0.1736806 | 0.1727122 | 0.1697653 |

Each entry is \(K\sigma_K/\sigma_{K-1}\).  For the one-cell lattice at
\(\tau=1\), calculations through \(K=40\) tend to
\(0.169765\ldots=2g/(3\pi)\).  At \(K=24\), scaling checks are

\[
\begin{array}{c|ccc}
g&0.4&0.8&1.6\\ \hline
K\sigma_K/\sigma_{K-1}&0.0852706&0.1705815&0.341431
\end{array}
\]

and

\[
\begin{array}{c|cccc}
\tau&0.5&1&2&4\\ \hline
K\sigma_K/\sigma_{K-1}&0.0852662&0.1705815&0.341357&0.681977.
\end{array}
\]

### Conjecture 6.1 — cosine factorial constants

For fixed \(b,g>0\),

\[
 \boxed{\lim_{K\to\infty}
 \frac{K\sigma_K(T_{b,g}|_{E_K})}
 {\sigma_{K-1}(T_{b,g}|_{E_{K-1}})}
 =\frac{gb}{6\pi}.}
 \tag{6.3}
\]

For the one-cell lattice,

\[
 \boxed{\lim_{K\to\infty}
 \frac{K\sigma_K(T_{\tau,g}^{\rm L}|_{E_K})}
 {\sigma_{K-1}(T_{\tau,g}^{\rm L}|_{E_{K-1}})}
 =\frac{2g\tau}{3\pi}.}
 \tag{6.4}
\]

The candidate mechanism is coherent but incomplete.  The source flag appears
to have \(\xi_K/\xi_{K-1}\to2/(3\pi)\).  On a finite output interval, the
ratio of norms of consecutive monic orthogonal polynomials tends to the
logarithmic capacity \(b/4\); for \(\omega\in[0,4]\), that capacity is \(1\).
Multiplication by \(g\), or \(g\tau\), predicts (6.3)--(6.4).

Two missing arguments prevent promotion to a theorem:

1. a proof of the source pivot limit; and
2. uniform-in-\(K\) control of the off-flag terms in (5.4).

The fixed-\(K\) theorem does not permit exchanging \(g\downarrow0\) with
\(K\to\infty\) at fixed \(g\).

---

## 7. Theorem/hypothesis boundary

| Statement | Status |
|---|---|
| \(H_b\) squared-factorial upper (2.4) | proved |
| fixed-\(\tau\) lattice upper (2.5) | proved |
| global atlas factorial ceiling from one lattice point | proved for the declared raw metric and normalization |
| explicit \(H_b\) lower (4.1), hence \(e^{-O(K^2)}\) | proved |
| late resolved, lattice atom, and interior atomic inherit that lower | proved under the displayed restrictions |
| \(\log\det H_K=-K^2\log K+O(K^2)\) | proved |
| determinant--trace obstruction | proved as an algebraic implication |
| exact endpoint congruence and fixed-\(K\) \(g^{2j}\) fan | proved |
| fixed-\(K\) response flag (5.5) | proved under its hypotheses |
| \(\xi_K/\xi_{K-1}\to2/(3\pi)\) | numerical conjecture |
| constants \(gb/(6\pi)\) and \(2g\tau/(3\pi)\) | numerical conjecture |
| matched factorial lower | open |
| general-\(K\) or asymptotic finite-boundary lower | open |

The proof ingredients—Chebyshev--Bessel expansions, continuous
Cauchy--Binet/Andréief identities, generalized Vandermonde positivity,
Schur complements, and approximation numbers—are classical.  This memo
makes no literature-priority claim for their combination.  The cosine pivot
limit and Conjecture 6.1 have not been identified here with a published
theorem; that is not an exhaustive literature claim.

The next proof target is precise: prove the source-pivot limit from (6.1),
then show that the response matrix in source-flag and output
orthogonal-polynomial coordinates is uniformly invertible after factorial
scaling.  Until then the strongest honest bracket is

\[
 \boxed{e^{-C_{b,g}K^2}
 \le\lambda_{K,b}(g)
 \le A_{b,g}^2\frac{(gb/4)^{2K}}{(K!)^2},}
\]

with an exact fixed-\(K\) interaction fan and a falsifiable constant
conjecture.

---

## 8. Reproduction

The theorem proofs above are analytic.  Representative entries and scaling
controls from the explicitly conjectural tables can be regenerated
independently with

```text
python oig_x_spectral_asymptotics.py --maximum-band 12 --digits 100
python -m unittest -v test_oig_x_spectral_asymptotics.py
```

The \(K=20,30,40\) rows in Section 6 require correspondingly larger band,
precision, and quadrature settings than this compact default audit.  The
script uses mpmath rather than outward interval arithmetic, labels its output
as numerical evidence, and never promotes a computed ratio to a theorem.
