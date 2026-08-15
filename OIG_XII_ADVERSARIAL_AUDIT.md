# Operational Information Geometry XII: two-port transfer adversarial audit

**Status:** independent theorem-boundary audit; not peer reviewed

**Scope:** the complete finite cell-centred Neumann response at the one-cell
lattice point \(\tau=1\), with source ports \(k=1,2\), the affine ramp
\(V(x)=1+4x/5\), and an atomic target at the exact midpoint

---

## 1. Verdict

The proposed two-port computation can be made rigorous, but the correct
milestone is sharper and more narrowly stated than the Stage XI numerical
target near \(n=383\).

On the exactly centred **odd-grid subsequence**, outward-rounded computation
brackets adjacent local crossings at

\[
 \begin{array}{c|c|c}
 \text{source metric}&\text{failed transfer test}&\text{successful transfer test}\\
 \hline
 L^2&n=343&n=345,\\
 \text{declared continuum }H^1&n=647&n=649.
 \end{array}
\tag{1.1}
\]

The finite formula and its normalization survive the audit.  A centred
Taylor action of the full tridiagonal generator also survives: it retains all
mixed diffusion--multiplication words and has a short exact rational tail.
The closed-form symmetric \(2\times2\) spectral norm is essential to the
sharp brackets.  The absolute-row-sum bound is valid but too coarse at both
successful grids.

Three qualifications are mandatory.

1. The theorem concerns one chart point, \(\tau=1\), not a compact
   \(\tau\)-interval and not the complete OIG atlas.
2. The target is exactly at \(x=1/2\) only for odd \(n\).  Even grids in the
   old default-carrier convention use a different, displaced target.
3. Failure at the immediately preceding odd grid and success at the next one
   prove an adjacent **local bracket**.  They do not prove that the successful
   grid is the smallest successful odd grid without either checking every
   earlier odd grid or proving a no-recrossing/monotonicity theorem.

Thus \(n=383\) was a useful conservative numerical landmark, but it is not
the first exact-centre crossing.  It should not remain in a theorem statement
except as historical exploratory evidence.

---

## 2. Audit of the exact finite formula

Let

\[
 x_j=\frac{j+1/2}{n},\qquad
 u_{n,k}(j)=\sqrt{\frac2n}\cos(k\pi x_j),\qquad k=1,2,
\tag{2.1}
\]

and let \(L_n\) be the unscaled reflecting path Laplacian.  For target mode
\(\ell\), put

\[
 \omega_{n,\ell}=4\sin^2\frac{\ell\pi}{2n},\qquad
 A_{n,\ell}=L_n+\omega_{n,\ell}V_n,
\tag{2.2}
\]

where \(V_n=\operatorname{diag}(1+4x_j/5)\).  The complete reduced response
amplitude is

\[
 a_{n,\ell k}={\bf1}^{T}e^{-A_{n,\ell}}u_{n,k}.
\tag{2.3}
\]

This is not the commuting phase approximation.  Since the exponential in
(2.3) contains the actual sum \(L_n+\omega V_n\), its Taylor polynomial
contains every noncommutative mixed word after like terms are collected.

For a target probability vector \(q\), its target-DCT coefficient is

\[
 \beta_{n,\ell}=u_{n,\ell}^{T}q.
\tag{2.4}
\]

The density-normalized lattice response is

\[
 \frac1{\sqrt n}(\beta_{n,\ell}a_{n,\ell k})_{\ell=0}^{n-1}.
\tag{2.5}
\]

At \(\tau=1\), the Stage X--XI normalization contributes
\(\sqrt{1+\tau}=\sqrt2\) at Gram level.  Therefore

\[
 G_{n,ij}=\frac{\sqrt2}{n}
 \sum_{\ell=1}^{n-1}
 \beta_{n,\ell}^{\,2}a_{n,\ell i}a_{n,\ell j}.
\tag{2.6}
\]

The \(\ell=0\) term is exactly zero: \({\bf1}^{T}u_{n,k}=0\) and the
Neumann semigroup preserves the constant left vector.  Omitting it is an
identity, not a numerical truncation.

The executable audit compares (2.3)--(2.6), on small grids, with the original
\(n^2\)-state Kronecker generator.  It also overlaps the independent Arb
dense-matrix exponential with the centred-Taylor enclosure.  These controls
fix the DCT scale, target scale, density factor \(1/\sqrt n\), and the final
\(\sqrt2\) chart factor simultaneously.

---

## 3. Exact-centre parity is part of the theorem

For odd \(n\), the central carrier cell has centre exactly \(x=1/2\).  With
an atomic target there,

\[
 \beta_{n,\ell}
 =\sqrt{\frac2n}\cos\frac{\ell\pi}{2}
 \quad(\ell\ge1).
\tag{3.1}
\]

Consequently,

\[
 \beta_{n,\ell}=0\quad(\ell\text{ odd}),\qquad
 \beta_{n,\ell}^{\,2}=\frac2n\quad(\ell\text{ even}).
\tag{3.2}
\]

Substitution in (2.6) gives the exact formula used by the proof checker,

\[
 \boxed{
 G_{n,ij}=\frac{2\sqrt2}{n^2}
 \sum_{\substack{2\le\ell<n\\ \ell\ \mathrm{even}}}
 a_{n,\ell i}a_{n,\ell j}.}
\tag{3.3}
\]

Using (3.2) symbolically is preferable to asking interval trigonometry to
rediscover exact zeros.

For even \(n\), the old default carrier is centred at

\[
 \frac12-\frac1{2n},
\tag{3.4}
\]

not at \(1/2\).  Its odd target modes generally do not vanish.  An apparent
even-grid crossing therefore belongs to a displaced-target sequence and
cannot be interleaved with (1.1).  A theorem covering all \(n\) would need a
declared two-cell deposition at the exact midpoint, or a separate target-
transport estimate.

---

## 4. The continuum object being compared

For \(\phi_k(x)=\sqrt2\cos(k\pi x)\), define

\[
 F_k(s)=\int_0^1e^{-s(1+4x/5)}\phi_k(x)\,dx.
\tag{4.1}
\]

The one-cell, atomic, \(\tau=1\) continuum phase Gram is

\[
 G_{ij}^{\infty}=\sqrt2\int_0^1
 F_i\!\left(4\sin^2\frac{\pi\xi}{2}\right)
 F_j\!\left(4\sin^2\frac{\pi\xi}{2}\right)d\xi.
\tag{4.2}
\]

The Stage XII computation encloses (4.2) directly with Arb.  It does not
substitute midpoint phase quadrature for the finite dynamics.  The finite
side remains (3.3), so source diffusion, the reflecting path endpoints, and
all mixed words are included.

The source DCT columns in (2.1) are exactly Euclidean orthonormal.  Thus the
finite and continuum coefficient costs agree exactly for the declared
\(L^2\) result.  For the second result, both sides are deliberately assigned

\[
 S_{H^1}=\operatorname{diag}(1+\pi^2,1+4\pi^2).
\tag{4.3}
\]

This is a valid declared operational cost.  It is not a theorem for the
natural discrete-gradient metric
\(\operatorname{diag}(1+n^2\omega_{n,k})\), which would require a separate
pair-metric transport bound.

---

## 5. Audit of the centred-Taylor enclosure

The direct dense Arb exponential is unnecessary at \(n\approx 10^2\)--
\(10^3\).  The tridiagonal action admits a much cheaper rigorous enclosure.
The exact Loewner bounds are

\[
 0\preceq L_n\preceq4I,
 \qquad I\preceq V_n\preceq\frac95I,
 \qquad0\le\omega\le4.
\tag{5.1}
\]

Set

\[
 c(\omega)=2+\frac75\omega,
 \qquad B_{n,\ell}=A_{n,\ell}-c(\omega_{n,\ell})I.
\tag{5.2}
\]

The spectral interval of \(A_{n,\ell}\) lies in
\([\omega,4+9\omega/5]\).  Hence

\[
 \|B_{n,\ell}\|_2
 \le \rho(\omega)=2+\frac25\omega
 \le\frac{18}{5}.
\tag{5.3}
\]

For the degree-\(m\) Taylor polynomial,

\[
 \left\|
 e^{-A}-e^{-c}\sum_{r=0}^{m}\frac{(-B)^r}{r!}
 \right\|_2
 \le e^{-c}e^{\rho}\frac{\rho^{m+1}}{(m+1)!}
 =e^{-\omega}\frac{\rho^{m+1}}{(m+1)!}
 \le
 \boxed{\frac{(18/5)^{m+1}}{(m+1)!}}.
\tag{5.4}
\]

Because \(\|u_{n,k}\|_2=1\) exactly and
\(\|{\bf1}\|_2=\sqrt n\), the amplitude remainder is at most

\[
 r_{n,m}=\sqrt n\frac{(18/5)^{m+1}}{(m+1)!}.
\tag{5.5}
\]

At degree \(32\), (5.5) is below \(4.9\times10^{-18}\) at \(n=345\)
and below \(6.7\times10^{-18}\) at \(n=649\).  The checker evaluates every
tridiagonal recurrence operation in Arb and adds the symmetric interval
\([-r_{n,m},r_{n,m}]\) to each amplitude.  Subsequent interval products and
sums therefore enclose the full Gram, including correlations that the
calculation elects not to exploit.

The audit found no missing exponential factor in (5.4).  In particular, the
identity \(-c+\rho=-\omega\), rather than the crude norm
\(\|A\|\le56/5\), is what makes the short polynomial effective.

Plain high-precision eigendecomposition is not an equivalent proof.  It
would need explicit residual, orthogonality, eigenvalue-gap, exponential,
and final summation error bounds.  The Arb Taylor action avoids that
validation chain.

---

## 6. Spectral norm, row sums, and unsafe entrywise tests

Let

\[
 E=S^{-1/2}(G_n-G^\infty)S^{-1/2}
 =\begin{pmatrix}a&b\\b&d\end{pmatrix}.
\tag{6.1}
\]

For a real symmetric \(2\times2\) matrix,

\[
 \lambda_\pm=\frac{a+d\pm
 \sqrt{(a-d)^2+4b^2}}{2},
 \qquad
 \|E\|_2=\max(|\lambda_-|,|\lambda_+|).
\tag{6.2}
\]

Applying (6.2) to Arb balls and taking outward absolute upper endpoints is a
rigorous operator-norm bound.  It is sharper here than the safe inequality
\(\|E\|_2\le\|E\|_\infty\).

For \(L^2\), the exact inherited floor is approximately

\[
 L_{2,L^2}=1.4315196512138325\times10^{-7}.
\tag{6.3}
\]

At \(n=345\), degree-32, 192-bit enclosures give

\[
 \|E\|_2<1.4223287202301\times10^{-7}<L_{2,L^2},
\tag{6.4}
\]

while the absolute-row-sum upper bound is about
\(1.67055\times10^{-7}\), which does not close.  The transferred floor from
this conservative comparison is greater than
\(9.19\times10^{-10}\).

At \(n=343\), the fixed rational vector \(v=(4,1)\) gives

\[
 -\frac{v^TEv}{v^Tv}
 >1.4388972111\times10^{-7}>L_{2,L^2}.
\tag{6.5}
\]

Thus the true spectral error is above the transfer budget.  This rejects the
specific perturbative transfer test at \(n=343\); it does **not** say that the
finite response itself is rank deficient.

The actual \(n=343\) error also gives a particularly relevant negative
control: its largest entry magnitude is only about
\(1.35834\times10^{-7}<L_{2,L^2}\), even though (6.5) holds.  An entrywise-
maximum test would therefore produce a false certificate.

For the declared continuum \(H^1\) metric, the corresponding Arb bracket is

\[
 \begin{aligned}
 n=647:&\quad \|E\|_2>L_{2,H^1},\\
 n=649:&\quad \|E\|_2<L_{2,H^1},
 \end{aligned}
 \qquad
 L_{2,H^1}\approx3.5523100221\times10^{-9}.
\tag{6.6}
\]

The successful margin is only about \(5.25\times10^{-12}\).  It must be
reported from exact directed endpoints, not decimal rounding.  The
row-sum bound is again too coarse.

---

## 7. Audit of the explanatory \(n^{-2}\) law

The finite enclosure does not need an asymptotic expansion.  A companion
claim that

\[
 b_{n,k}(\omega)=F_k(\omega)+h^2D_k(\omega)+O(h^3)
\tag{7.1}
\]

uniformly on \(0\le\omega\le4\) is nevertheless supportable, provided its
proof includes the following uniform estimates rather than only a formal
Duhamel calculation.

Put \(M=\omega V_n\), use
\(\langle x,y\rangle_h=h x^Ty\), and expand

\[
 e^{-(M+L)}
 =\sum_{r\ge0}(-1)^r
 \int_{\Delta_r}
 e^{-s_0M}L e^{-s_1M}\cdots L e^{-s_rM}\,ds.
\tag{7.2}
\]

The \(r=0\) term is ordinary composite midpoint quadrature.  The \(r=1\)
term uses the exact Green identity

\[
 \langle p_h,L_nq_h\rangle_h
 =h\sum_{j=0}^{n-2}
 (p_{j+1}-p_j)(q_{j+1}-q_j)
 =h^2\int_0^1p'q'\,dx+O(h^3),
\tag{7.3}
\]

uniformly for the smooth functions generated by
\(e^{-s\omega V}\), \(0\le s\le1\), \(0\le\omega\le4\).

For \(r\ge2\), write a typical scalar term as
\(\langle p,LTLq\rangle_h=\langle Lp,TLq\rangle_h\).
The endpoint samples are uniformly smooth and obey

\[
 \|L_nf_h\|_h=O(h^{3/2}),
\tag{7.4}
\]

because the two boundary entries are \(O(h)\) and the interior entries are
\(O(h^2)\).  The middle product has norm at most \(4^{r-2}\), since
\(\|L_n\|_2\le4\) and every multiplication semigroup is contractive.
The simplex volume \(1/r!\) therefore makes the complete \(r\ge2\) series
uniformly \(O(h^3)\).

The resulting coefficient is

\[
 D_k(\omega)
 =\frac{13}{24}\omega g B_k(\omega)
  +\frac13\omega^2g^2F_k(\omega),
\qquad
 B_k(\omega)=\sqrt2\!
 \left[(-1)^ke^{-(1+g)\omega}-e^{-\omega}\right].
\tag{7.5}
\]

The algebra in (7.5) survives the audit: midpoint quadrature contributes
\(\omega gB_k/24\), and the one-\(L\) Dyson term contributes
\(\omega gB_k/2+\omega^2g^2F_k/3\).

The odd target-mode sum also needs an Euler--Maclaurin statement.  For
\(H_{ij}(\xi)=F_i(\omega(\xi))F_j(\omega(\xi))\),

\[
 Q_hH=2h\sum_{r=1}^{(n-1)/2}H(2rh)
\tag{7.6}
\]

is composite midpoint quadrature on \([h,1]\).  Here
\(H'(1)=0\), while \(F_k(\omega(\xi))=O(\xi^2)\) at the origin, so
\(H(\xi)=O(\xi^4)\) and \(H'(h)=O(h^3)\).  Midpoint
Euler--Maclaurin plus the missing interval \([0,h]\) gives

\[
 Q_hH-\int_0^1H(\xi)\,d\xi=O(h^4),
\tag{7.7}
\]

and in particular no order-\(h^2\) target-quadrature coefficient.  Equations
(7.1)--(7.7) imply

\[
 G_n-G=h^2E+O(h^3)
\tag{7.8}
\]

with the stated cross integral \(E\).

Without the Dyson-series estimate (7.4) and the endpoint quadrature argument
(7.6)--(7.7), the explicit coefficient should be labelled a formal,
numerically validated asymptotic rather than a theorem.  These details do
not affect the independent finite Arb certificates.

---

## 8. What “first” can and cannot mean

The old Stage XI list tested the sparse grids

\[
 31,63,127,255,383,511.
\tag{7.1}
\]

Within that list, \(383\) was the first binary64 value below the \(L^2\)
floor.  It was never the first member of the odd-grid sequence.  The new
enclosure replaces that exploratory statement by the adjacent local bracket
\(343/345\).

Even this bracket does not by itself establish global minimality.  A sequence
can pass at an early index, fail later, and pass again.  The words “smallest
successful odd grid” or “first odd-grid crossing” require one of:

1. rigorous evaluation of every odd \(n<345\) (and analogously below \(649\)
   for \(H^1\));
2. a proved monotonicity/no-recrossing theorem for the metric-relative error;
   or
3. a rigorous global lower estimate that excludes the earlier range.

None is needed for the scientifically useful existence theorem at \(345\)
and \(649\).  “Adjacent certified bracket” is the exact current wording.

---

## 9. Required theorem boundaries

A sound Stage XII theorem may assert:

* the actual finite generator \(L_n+\omega_{n,\ell}V_n\), not the phase-grid
  surrogate, is enclosed;
* at \(\tau=1\), with the exactly centred atomic target and ports \(1,2\),
  the Stage X late-core floor transfers at \(n=345\) in \(L^2\);
* under the separately declared continuum \(H^1\) coefficient cost, it
  transfers at \(n=649\);
* the immediately preceding odd grids \(343\) and \(647\) fail this specific
  sufficient transfer inequality; and
* every inequality is decided by Arb endpoints and exact rational floors.

It may not yet assert:

* smallest successful grid, without the additional work in Section 8;
* an even-grid exact-centre theorem;
* transfer for a natural discrete \(H^1\) metric;
* uniformity for \(\tau\ge1\) or even for a compact \(\tau\)-interval;
* a finite version of the early or reflecting-boundary charts;
* a complete-atlas floor of \(10^{-19}\); or
* a growing-band, finite-sensor, noisy, radio, wave, or physical-universe
  conclusion.

The positive result is already substantial: it is the first rigorous
two-direction bridge in this research line from a continuum spectral floor
to the complete noncommuting finite dynamics at a declared lattice point.

---

## 10. Reproducible adversarial controls

`test_oig_xii_adversarial_controls.py` checks:

1. exact DCT source orthogonality and odd-grid target parity;
2. failure of that parity identity on the displaced even-grid carrier;
3. agreement of the reduced modal formula with the dense Kronecker model;
4. overlap of the centred-Taylor Gram with the independent dense Arb
   exponential on a small grid;
5. the centred spectral-radius and Taylor-tail inequalities;
6. the exact symmetric \(2\times2\) norm against direct eigenvalues;
7. an entrywise-maximum false-certificate counterexample;
8. the fact that a row-sum proof misses the sharp successful bracket;
9. both metric-relative adjacent brackets; and
10. the logical counterexample preventing an unsupported “first” claim.

These tests are controls on the proof boundary.  Passing them does not turn
the result into peer review, nor does it extend the declared chart.
