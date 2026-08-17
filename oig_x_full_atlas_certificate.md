# Operational Information Geometry X

## A complete \(K=2\) compact-atlas certificate

**Status:** rigorous computer-assisted theorem for the declared continuum
phase model; not peer reviewed

**Arithmetic:** exact rationals and 192-bit Arb real balls

**Companion checker:** oig_x_full_atlas_certificate.py

---

## 1. Certified result

For

\[
 V(x)=1+\frac45x,\qquad
 \phi_1(x)=\sqrt2\cos(\pi x),\qquad
 \phi_2(x)=\sqrt2\cos(2\pi x),
\tag{1.1}
\]

use the exact source metric \(S=I_2\).  Declare the four chart strata

\[
\begin{array}{ll}
\text{early resolved:}&
\widehat\Gamma_q^{\mathrm R}
=D(q)^{-1}\Gamma_q^{\mathrm R}D(q)^{-1},
\quad D(q)=\operatorname{diag}(q,q^2),\quad0\le q\le1,\\[1mm]
\text{late resolved:}&
\sqrt{1+q}\,\Gamma_q^{\mathrm R},\quad1\le q<\infty,\\[1mm]
\text{one-cell lattice:}&
\sqrt{1+\tau}\,\Gamma_{\tau,\delta_0}^{\mathrm L},
\quad1\le\tau<\infty,\\[1mm]
\text{atomic boundary:}&
\Gamma_\kappa^{\mathrm A},\quad0\le\kappa\le\infty.
\end{array}
\tag{1.2}
\]

At \(q=0\), the first line means the analytic moment-calibrated limit, not a
literal inverse of \(D(0)\).

The metric declaration needs one further sentence.  On the early chart,
\(z\) is a calibrated moment coordinate with cost \(z^*z\); for \(q>0\) it
represents raw physical cosine coefficients \(D(q)^{-1}z\).  Equivalently,
the same generalized spectrum can be written in raw coefficients as the pair

\[
 \bigl(\Gamma_q^{\mathrm R},D(q)^2\bigr).
\tag{1.3}
\]

The late, lattice, and atomic strata use raw cosine coefficients with
\(S=I_2\).  Thus the atlas minimum explicitly compares declared chart costs;
it is not a claim that moment amplification is free in raw \(L^2\).

Let \(\gamma_2\) be the infimum of the smallest generalized Gram eigenvalue
over all four strata in (1.2).  Within each displayed coordinate chart
\(S=I_2\), so the computed generalized eigenvalues equal the ordinary
eigenvalues of the displayed Gram.  The coordinate-to-physical synthesis
above remains part of the theorem.

The checker proves

\[
 \boxed{
 10^{-19}\le\gamma_2\le10^{-6}.}
\tag{1.4}
\]

This is a deliberately conservative bracket.  Its significance is
completeness: there is no sampled gap in \(q\), \(\tau\), or \(\kappa\), and
the infinite endpoints are reduced analytically.

---

## 2. Why the basis is already moment adapted

The source ports in (1.1) are exactly \(L^2(0,1)\)-orthonormal and have zero
mean.  For an affine ramp,

\[
 m_j(f)=\int_0^1V(x)^jf(x)\,dx.
\]

Elementary cosine integration gives

\[
 m_1(\phi_1)=-\frac{8\sqrt2}{5\pi^2}\ne0,
\qquad
 m_1(\phi_2)=0,
\tag{2.1}
\]

and

\[
 m_2(\phi_2)
=\frac{(4/5)^2}{\sqrt2\,\pi^2}\ne0.
\tag{2.2}
\]

Thus the pivot orders are exactly \(1,2\), and no numerical QR or
floating-rank decision is needed.  The analytic null on this source space is
zero because the ramp is strictly monotone.

More generally, since every cosine port has zero mean,

\[
 \det M_K(1+gx)
 =
 g^{1+2+\cdots+K}
 \det\bigl[\langle x^m,\phi_k\rangle\bigr]_{m,k=1}^K.
\tag{2.3}
\]

The early endpoint Gram determinant therefore scales as

\[
 g^{K(K+1)}.
\tag{2.4}
\]

For \(K=2\), the powers are \(g^3\) and \(g^6\).  This is both an exact
normalization check and a warning: no certificate can remain uniform as the
ramp degenerates to \(g=0\).

---

## 3. The explicit two-port Laplace frame

Put \(g=4/5\), \(a=gs\), and

\[
 F_k(s)=\int_0^1e^{-sV(x)}\phi_k(x)\,dx.
\]

Direct integration gives, for \(s>0\),

\[
 F_1(s)
 =
 \sqrt2e^{-s}
 \frac{a(1+e^{-a})}{a^2+\pi^2},
\tag{3.1}
\]

\[
 F_2(s)
 =
 \sqrt2e^{-s}
 \frac{a(1-e^{-a})}{a^2+4\pi^2}.
\tag{3.2}
\]

Both are positive.  Their ratio is

\[
 R(s)=\frac{F_2(s)}{F_1(s)}
=
\tanh\!\left(\frac{gs}{2}\right)
\frac{(gs)^2+\pi^2}{(gs)^2+4\pi^2}.
\tag{3.3}
\]

Both factors in (3.3) are strictly increasing, so \(R\) is strictly
increasing.  A useful explicit derivative bound is

\[
 R'(s)
\ge
\frac g8
\operatorname{sech}^2\!\left(\frac{gs_{\max}}2\right),
\qquad0\le s\le s_{\max}.
\tag{3.4}
\]

This ratio separation is the analytic engine of all three lower-frame
arguments.

### 3.1 The two-dimensional frame inequality

Let

\[
 G_{ij}=\int f_i(z)\overline{f_j(z)}\,d\nu(z).
\]

Andréief's identity at \(K=2\) is

\[
 \det G
 =
 \frac12
 \iint
 |f_1(z_1)f_2(z_2)-f_2(z_1)f_1(z_2)|^2
 \,d\nu(z_1)d\nu(z_2).
\tag{3.5}
\]

If two disjoint intervals have response-determinant lower bound \(d\) and
measure masses at least \(\mu_1,\mu_2\), restricting (3.5) to both ordered
rectangles gives

\[
 \det G\ge d^2\mu_1\mu_2.
\tag{3.6}
\]

For a positive \(2\times2\) Gram,

\[
 \lambda_{\min}(G)
\ge\frac{\det G}{\operatorname{tr}G}.
\tag{3.7}
\]

The checker evaluates the right side of (3.7) outward with Arb.  It never
uses a sampled smallest eigenvalue as a lower certificate.

---

## 4. The complete early interval \(0\le q\le1\)

For \(q>0\), set \(s=\pi^2qu^2\) and define the calibrated response columns

\[
 A_1(q,u)=q^{-1}F_1(s),
\qquad
 A_2(q,u)=q^{-2}F_2(s).
\tag{4.1}
\]

The symbolic formulas cancel the powers of \(q\) before evaluation, so both
columns extend continuously to \(q=0\).  Moreover,

\[
 \frac{A_2(q,u)}{A_1(q,u)}=\frac{R(s)}q.
\tag{4.2}
\]

Choose

\[
 U_1=\left[\frac15,\frac25\right],
\qquad
 U_2=\left[\frac{11}{20},\frac34\right].
\tag{4.3}
\]

For \(u_1\in U_1\), \(u_2\in U_2\), the mean-value theorem and (3.4) give

\[
\frac{R(\pi^2qu_2^2)-R(\pi^2qu_1^2)}q
\ge
\pi^2
\left[
\left(\frac{11}{20}\right)^2
-\left(\frac25\right)^2
\right]
\frac g8
\operatorname{sech}^2\!\left(
\frac{g\pi^2(3/4)^2}{2}
\right).
\tag{4.4}
\]

This bound is independent of \(q\) and remains valid at the endpoint by
continuity.

The standard Gaussian output measure is

\[
 d\nu(u)=e^{-\pi^2u^2}\,du.
\]

On an interval \([a,b]\),

\[
 \nu([a,b])\ge(b-a)e^{-\pi^2b^2}.
\tag{4.5}
\]

The trace is bounded using

\[
 |A_1(q,u)|\le2\sqrt2\,g\,u^2,
\qquad
 |A_2(q,u)|
\le\frac{\sqrt2\,g^2\pi^2}{4}u^4.
\tag{4.6}
\]

Equations (3.6)--(4.6), evaluated with Arb, produce the lower expression

\[
 [1.4034667835842004006\ldots\times10^{-18}
 \ \mathbin{+/-}\ 4.30\times10^{-73}].
\tag{4.7}
\]

In particular, the entire calibrated early stratum has floor above
\(10^{-19}\).  No small positive \(q\) was substituted for the endpoint.

---

## 5. One truncated Gram controls both late interior charts

Define

\[
 H_b(f,g)
=
\frac1{2\pi}\int_0^b
s^{-1/2}F_f(s)\overline{F_g(s)}\,ds
\tag{5.1}
\]

with

\[
 b=\frac32.
\]

The certificate uses the separated intervals

\[
 J_1=\left[\frac14,\frac12\right],
\qquad
 J_2=\left[1,\frac32\right].
\tag{5.2}
\]

Their exact measure masses are

\[
 \mu([a,b])=\frac{\sqrt b-\sqrt a}{\pi}.
\tag{5.3}
\]

The response determinant is bounded using (3.1), the monotonicity of
\(R\), and

\[
 R(1)-R(1/2)>0.
\]

Since each source port has \(L^2\)-norm one,
\(\|\phi_k\|_1\le1\), whence

\[
 |F_k(s)|\le e^{-s}.
\]

Therefore

\[
 \operatorname{tr}H_b
\le
\operatorname{tr}H_\infty
\le\frac1{\sqrt{2\pi}}.
\tag{5.4}
\]

The Arb frame calculation encloses its analytic lower expression by

\[
 [4.2379307829132405\ldots\times10^{-12}
 \ \mathbin{+/-}\ 3.31\times10^{-67}],
\tag{5.5}
\]

which in particular proves
\(\lambda_{\min}(H_b)>4.2\times10^{-12}\).

For every \(q\ge1\),

\[
 \sqrt{1+q}\,\Gamma_q^{\mathrm R}
\succeq
\min\{1,\sqrt2e^{-b}\}H_b
=\sqrt2e^{-3/2}H_b.
\tag{5.6}
\]

For every \(\tau\ge1\), the one-cell lattice substitution
\(s=4\tau\sin^2(\theta/2)\) gives

\[
 \sqrt{1+\tau}\,
\Gamma_{\tau,\delta_0}^{\mathrm L}
\succeq H_b
\qquad(b\le4).
\tag{5.7}
\]

Consequently the certified lower expressions are approximately

\[
\begin{array}{c|c}
\text{stratum}&\text{lower expression}\\ \hline
\text{late resolved}&1.3372947331980443\times10^{-12}\\
\text{one-cell lattice}&4.2379307829132405\times10^{-12}\\
\text{interior atomic}&4.2379307829132405\times10^{-12}.
\end{array}
\tag{5.8}
\]

Equations (5.6)--(5.7) cover the whole infinite parameter tails, not merely a
large finite cutoff.

---

## 6. Every reflecting-boundary coordinate

The boundary Gram is

\[
 \Gamma_\kappa^{\mathrm A}(f,g)
=
\int_0^\infty
[1+\cos(2\pi\kappa r)]
F_f(\pi^2r^2)\overline{F_g(\pi^2r^2)}
\,dr.
\tag{6.1}
\]

A boundary lower bound cannot be obtained by claiming that the cosine
correction is positive semidefinite; it is not.  Instead use the two output
intervals

\[
 I_1=\left[\frac2{25},\frac{11}{50}\right],
\qquad
 I_2=\left[\frac{27}{100},\frac12\right].
\tag{6.2}
\]

For \(I=[a,b]\), its boundary-weight mass is exactly

\[
 \mu_I(\kappa)
=
b-a
+b\,\operatorname{sinc}(2\pi b\kappa)
-a\,\operatorname{sinc}(2\pi a\kappa),
\tag{6.3}
\]

where \(\operatorname{sinc}(x)=\sin(x)/x\).

The checker partitions \(0\le\kappa\le3\) into 768 exact dyadic boxes of
width \(1/256\).  On each of the resulting \(1536\) interval-and-box pairs,
Arb directly proves

\[
 \mu_{I_j}(\kappa)>\frac1{100}.
\tag{6.4}
\]

For \(\kappa\ge3\),

\[
 \mu_I(\kappa)
\ge|I|-\frac1{\pi\kappa}.
\tag{6.5}
\]

The two tail lower bounds are respectively

\[
0.0338967046054\ldots,\qquad
0.1238967046054\ldots,
\]

so (6.4) continues to infinity.

The response-determinant bound follows from (3.1)--(3.3), because the
\(s\)-images of the intervals in (6.2) are strictly separated.  Finally,

\[
1+\cos(2\pi\kappa r)\le2,
\qquad
|F_k(\pi^2r^2)|\le e^{-\pi^2r^2},
\]

give

\[
\operatorname{tr}\Gamma_\kappa^{\mathrm A}
\le\sqrt{\frac2\pi}.
\tag{6.6}
\]

The resulting all-boundary lower expression is

\[
[3.5722497712656042741\ldots\times10^{-17}
\ \mathbin{+/-}\ 2.36\times10^{-72}].
\tag{6.7}
\]

Thus the finite boundary and the \(\kappa=\infty\) endpoint are both covered
without a false Loewner comparison.

---

## 7. A rigorous upper witness at \(q=1\)

An upper bound on an atlas infimum needs only one parameter point and one
source vector.  At \(q=1\), choose the exact coordinate vector

\[
 z=(1,-15),\qquad z^*Sz=226.
\tag{7.1}
\]

The checker evaluates

\[
\frac1{226}\int_0^\infty
e^{-\pi^2u^2}
|F_1(\pi^2u^2)-15F_2(\pi^2u^2)|^2\,du.
\tag{7.2}
\]

On \(0\le u\le1\), 1024 exact dyadic Arb boxes enclose the full positive
integrand.  The checker sums each outward interval upper endpoint times the
exact box width.  For \(u\ge1\),

\[
|F_1-15F_2|\le16e^{-\pi^2u^2}
\]

and

\[
\int_1^\infty e^{-3\pi^2u^2}\,du
\le\frac{e^{-3\pi^2}}{6\pi^2}.
\tag{7.3}
\]

The final outward upper expression is enclosed by

\[
[7.3887873215730786\ldots\times10^{-7}
\ \mathbin{+/-}\ 6.61\times10^{-64}]
<10^{-6}.
\tag{7.4}
\]

This proves the upper half of (1.4).  The displayed value is an outward
upper enclosure, not a floating eigensolver estimate.

---

## 8. What the checker actually verifies

The implementation uses Python-Flint 0.9.0 and:

1. embeds every model constant and decision threshold as an exact rational;
2. constructs the \(\kappa\) and \(u\) boxes with exact dyadic midpoints and
   radii;
3. evaluates \(\pi\), exponentials, hyperbolic functions, trigonometric
   functions, square roots, and all arithmetic as outward Arb balls;
4. proves every sign comparison against an exact rational using the complete
   ball, never its midpoint;
5. covers \(q\in[0,1]\) by a symbolic uniform frame inequality;
6. covers \(q,\tau\in[1,\infty]\) by the common-window reductions;
7. covers \(\kappa\in[0,3]\) by interval boxes and
   \(\kappa\in[3,\infty]\) by (6.5); and
8. repeats successfully at 256-bit precision in the test suite.

To reproduce:

    python oig_x_full_atlas_certificate.py
    python -m unittest -v test_oig_x_full_atlas_certificate.py

The JSON proof trace reports every analytic lower expression, the boundary
box count, its weakest descriptive box, the infinite-tail inequalities, and
the upper-witness enclosure.

---

## 9. Scope and limitations

This is a complete certificate for the declared \(K=2\) **continuum phase
atlas**.  It does not include:

* a finite-grid transfer error;
* finite sensor sampling;
* target families other than the Gaussian resolved preparation and
  \(Q=\delta_0\) lattice preparation;
* raw \(L^2\) early observability without the declared moment cost;
* a \(K=3\) or growing-band lower bound; or
* a claim about physical reality outside the Stage IX parabolic model.

For a finite discretization, a metric-relative transfer estimate

\[
\|S^{-1/2}(G_h-G)S^{-1/2}\|<10^{-19}
\]

would be sufficient to retain a positive bound from this particular
conservative certificate.  That is an extremely demanding threshold; a
sharper lower computation would be preferable before using (1.4) as an
experimental noise budget.

The mathematical milestone is narrower and exact: the qualitative
fixed-band positivity theorem has now been converted, for one nontrivial
two-port model, into a finite reproducible proof spanning the entire
compactified atlas.
