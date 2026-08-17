# Operational Information Geometry VIII

## A uniform resolved-regime comparison theorem

- **Research lane:** three-parameter continuum/lattice error analysis
- **Date:** 14 August 2026
- **Status:** proof memo; not peer reviewed
- **Scope:** the cell-centred Neumann path with a conservative target
  preparation; no claim about physical spacetime
- **Predecessor:** OPERATIONAL_INFORMATION_GEOMETRY_VII.md

## 1. Result in one paragraph

Stage VII identified the continuum phase function

\[
 \mathcal P_k(q)^2=\int_0^\infty
 |\widehat\eta(\pi u)|^2|F_k(\pi^2qu^2)|^2\,du,
 \qquad q={t\over\varepsilon^2}.
\]

This memo supplies the missing finite-grid comparison in the resolved
regime. Put

\[
 \delta_\varepsilon={h\over\varepsilon},\qquad
 \delta_t={h\over\sqrt t}.
\]

For the canonical ramp \(V(x)=1+gx\), a fixed cosine source, a fixed interior
carrier, and conservative cell masses, the following estimates hold. In the
balanced chart, uniformly for \(q\) in a compact subset of \((0,\infty)\),

\[
 \boxed{
 \left|
 {\sqrt\varepsilon\,\mathcal N_{h,k}(t)\over\mathcal P_k(q)}-1
 \right|
 \le C\left(\varepsilon^2+\delta_\varepsilon^2\right). }
\]

In the early chart \(0<q\le q_0\), if \(r=1\) for odd \(k\) and \(r=2\) for
even \(k\),

\[
 \boxed{
 \left|
 {\sqrt\varepsilon\,\mathcal N_{h,k}(t)\over\mathcal P_k(q)}-1
 \right|
 \le C\left[
 q+\delta_\varepsilon^2+{t\over q^{r-1}}+\varepsilon^2
 \right]. }
\]

For the ramp the last two terms reduce to \(t\) when \(k\) is odd and to
\(\varepsilon^2=t/q\) when \(k\) is even, so they are harmless. At the two
critical paths \(t=\tau h^2\), \(\varepsilon=h^{4/5}\) and
\(\varepsilon=h^{8/9}\), the relative errors are respectively
\(O(h^{2/5})\) and \(O(h^{2/9})\).

In the heat-resolved chart \(q\to\infty\), \(t\downarrow0\),
\(\delta_t\to0\),

\[
 \boxed{
 \left|\sqrt t\,\mathcal N_{h,k}(t)^2-C_{F,k}^2\right|
 \le C\left[t+{h^2+\varepsilon^2\over t}\right]. }
\]

Across these two declared initial-layer charts, the mesh condition can be
summarized as

\[
 {h\over\max\{\varepsilon,\sqrt t\}}\longrightarrow0
\]

but it is not by itself a complete convergence hypothesis.  One must also
declare the early/balanced or heat-resolved time chart, keep the carrier
interior, and preserve every cancelled lower source moment. Cell-average
Fourier consistency controls early and balanced times; heat smoothing and a
two-copy characteristic-function estimate control late times. The theorem is
exact for the declared canonical path. A general smooth modulation needs an
additional discrete moment condition in a cancelled early chart; this is a
genuine obstruction, not a proof artifact.

## 2. Exact finite model

Let \(h=1/n\), \(x_i=(i+1/2)h\), and

\[
 \langle u,v\rangle_h=h\sum_{i=0}^{n-1}u_iv_i.
\]

The nonnegative cell-centred Neumann Laplacian is

\[
 A_h=h^{-2}L_n,
\]

where \(L_n\) is the unweighted path Laplacian. Its orthonormal modes and
eigenvalues are

\[
 \phi_{\ell,h}(i)=\sqrt2\cos(\ell\pi x_i),\qquad
 \mu_{\ell,h}=4h^{-2}\sin^2\!\left({\ell\pi h\over2}\right),
 \quad1\le\ell<n.
\]

Fix \(g>0\), \(V(x)=1+gx\), and a source mode
\(\phi_k(x)=\sqrt2\cos(k\pi x)\), with \(k\) fixed while \(n\to\infty\).
Write \(V_h=\operatorname{diag}(V(x_i))\). The reduced source block at target
mode \(\ell\) is

\[
 K_{\ell,h}=A_h+\mu_{\ell,h}V_h.
\]

Let \(y_0\in[d_0,1-d_0]\) for a fixed \(d_0>0\). Take an even nonnegative
\(\eta\in C_c^\infty(-R,R)\) with integral one and, for
\(R\varepsilon<d_0\), set

\[
 \rho_\varepsilon(y)=\varepsilon^{-1}
 \eta\!\left({y-y_0\over\varepsilon}\right),\qquad
 q_{h,j}=\int_{jh}^{(j+1)h}\rho_\varepsilon(y)\,dy.
\]

An even Schwartz probability kernel is also allowed after normalizing its
restriction to \([0,1]\).  All displayed bounds then acquire its
superalgebraically small boundary-tail term; relative early statements
require that term to be bounded by the displayed error times \(q^{r(k)}\).
This is the convention used when Section 8 specializes to the Gaussian.

The word *conservative* refers to this exact cell integral. Define

\[
 \beta_{\ell,h}=\sum_jq_{h,j}\phi_{\ell,h}(j),
\]

\[
 a_{\ell k,h}(t)=
 \left\langle1,e^{-tK_{\ell,h}}\phi_{k,h}\right\rangle_h,
\]

and the full density-normalized response norm

\[
 \boxed{
 \mathcal N_{h,k}(t)^2
 =\sum_{\ell=1}^{n-1}|\beta_{\ell,h}|^2
 |a_{\ell k,h}(t)|^2. }
\]

The continuum high-frequency profile is

\[
 F_k(s)=\int_0^1e^{-sV(x)}\phi_k(x)\,dx
 =\sqrt2e^{-s}
 {gs[1-(-1)^ke^{-gs}]\over(gs)^2+(k\pi)^2}.
\]

It has multiplication order

\[
 r(k)=\begin{cases}1,&k\text{ odd},\\2,&k\text{ even}.
 \end{cases}
\]

Finally,

\[
 C_{F,k}^2=\int_0^\infty|F_k(\pi^2z^2)|^2\,dz>0.
\]

All constants below may depend on \(g,k,\eta,d_0\), and on the displayed
compact \(q\)-range, but not on \(h,\varepsilon,t\).

## 3. The scalar estimate that removes the old square-root loss

The key new ingredient is a weak, rather than operator-norm, comparison of
source semigroups.

### Lemma 3.1 — uniform discrete Lipschitz estimate

Let \(D_hu(i)=(u_{i+1}-u_i)/h\). If \(V_h\ge v_->0\) and
\(\|D_hV_h\|_\infty\le L\), then for every \(d\ge0\), \(r\ge0\),

\[
 \|D_he^{-r(dA_h+V_h)}f\|_\infty
 \le C e^{-v_-r}
 \bigl(\|D_hf\|_\infty+rL\|f\|_\infty\bigr).
\]

The same estimate holds for the continuum Neumann semigroup with the weak
derivative in place of \(D_h\).

#### Proof

On the path graph, \(D_hA_h=A_h^{D}D_h\), where \(A_h^{D}\) is the
nonnegative Dirichlet edge Laplacian. If
\(u(r)=e^{-r(dA_h+V_h)}f\), the edge vector \(w=D_hu\) satisfies a
sub-Markov parabolic equation with killing at least \(v_-\) and forcing

\[
 -(D_hV_h)\,\overline u.
\]

Here bars denote adjacent-cell averages; the exact discrete product identity
is

\[
 D_h(V_hu)=\overline V_hD_hu+(D_hV_h)\overline u.
\]

The maximum principle and
\(\|u(r)\|_\infty\le e^{-v_-r}\|f\|_\infty\) give the result by variation of
constants. In the continuum, differentiate the parabolic equation. The
derivative solves the analogous Dirichlet problem and the same maximum
principle applies. Approximation removes any initial boundary-compatibility
issue. \(\square\)

### Lemma 3.2 — reduced response versus multiplication

Put

\[
 s_{\ell,h}=t\mu_{\ell,h},\qquad
 F_{k,h}(s)=\langle1,e^{-sV_h}\phi_{k,h}\rangle_h.
\]

Then

\[
 \boxed{
 |a_{\ell k,h}(t)-F_{k,h}(s_{\ell,h})|
 \le Ct\,s_{\ell,h}(1+s_{\ell,h})e^{-c s_{\ell,h}}. }
\]

The continuum analogue, with \(\mu>0\), obeys the same bound.

#### Proof

Set \(s=t\mu\), \(d=1/\mu\), and \(B=dA_h+V_h\). Form Duhamel gives

\[
 \begin{aligned}
 &\langle1,e^{-sB}\phi_{k,h}\rangle_h
 -\langle1,e^{-sV_h}\phi_{k,h}\rangle_h\\
 &\quad=-d\int_0^s
 \left\langle
 D_he^{-(s-r)B}1,
 D_h(e^{-rV_h}\phi_{k,h})
 \right\rangle_{h,\mathrm{edge}}\,dr.
 \end{aligned}
\]

Lemma 3.1 bounds the first gradient by
\(C(s-r)e^{-v_-(s-r)}\) and direct differencing bounds the second by
\(C(1+r)e^{-v_-r}\). The edge interval has total length below one. Hence

\[
 |\cdots|\le Cd e^{-v_-s}\int_0^s(s-r)(1+r)\,dr
 \le Cd s^2(1+s)e^{-c s}.
\]

Since \(ds=t\), this is the claim. \(\square\)

This \(O(ts)\) scalar estimate is the reason the balanced error is
\(O(\varepsilon^2)\), rather than the \(O(\varepsilon)\) supplied by an
absolute Brownian-displacement bound. It uses one spatial derivative of the
modulation and of the source. It is a matrix-element estimate; an operator
norm estimate of this strength is false at the singular endpoint.

### Lemma 3.3 — midpoint source quadrature

For the ramp and cosine source,

\[
 |F_{k,h}(s)-F_k(s)|
 \le Ch^2s^{r(k)}(1+s)^3e^{-cs}.
\]

#### Proof

Composite midpoint quadrature is second order. The constant cosine has
exactly zero midpoint sum. If \(k\) is even, reflection of the midpoint grid
also gives

\[
 h\sum_iV(x_i)\phi_k(x_i)
 =\int_0^1V(x)\phi_k(x)\,dx=0.
\]

Subtract the first \(r(k)\) terms of \(e^{-sV}\) before applying the midpoint
remainder for \(s\le1\); for \(s\ge1\), apply it directly and weaken the
exponential from \(v_-\) to \(c<v_-\). \(\square\)

For a general \(C^2\) modulation with \(m_1=0\), Lemma 3.3 instead contains

\[
 |m_{1,h}|s,
 \qquad m_{1,h}=h\sum_iV(x_i)\phi_k(x_i),
\]

unless the discretization preserves the cancellation.

## 4. Target preparation, dispersion, and carrier averaging

Let \(\xi_\ell=\pi\ell\), \(\theta_\ell=h\xi_\ell\), and
\(\operatorname{sinc}z=\sin z/z\).

### Lemma 4.1 — conservative cell-average transform

For every integer \(M\ge1\), uniformly for \(0\le\theta_\ell\le\pi\),

\[
 \begin{aligned}
 \beta_{\ell,h}
 &=\sqrt2\,\operatorname{Re}\left[
 e^{i\xi_\ell y_0}\widehat\eta(\varepsilon\xi_\ell)
 \operatorname{sinc}(\theta_\ell/2)
 \right]+R_{\ell,h},\\
 |R_{\ell,h}|&\le C_M(h/\varepsilon)^M.
 \end{aligned}
\]

#### Proof

The masses divided by \(h\) are midpoint samples of the convolution of
\(\rho_\varepsilon\) with a box of width \(h\). Poisson summation on the
infinite midpoint lattice gives the displayed zero alias. Every nonzero
alias has physical frequency at least \(\pi/h\); rapid decay of
\(\widehat\eta\) gives the remainder. Compact support inside \((0,1)\) makes
the infinite-lattice extension exact. \(\square\)

On the band \(\ell\lesssim1/\varepsilon\),

\[
 \operatorname{sinc}(\theta_\ell/2)=1+O(\delta_\varepsilon^2),
\]

and

\[
 \mu_{\ell,h}=\xi_\ell^2
 \left[1+O(\delta_\varepsilon^2)\right].
\]

The Schwartz tail absorbs the complementary band to arbitrary algebraic
order. This is where smoothness of the mollifier is used.

### Lemma 4.2 — phase quadrature

For \(q\) in a fixed compact subset of \((0,\infty)\),

\[
 \begin{aligned}
 &\varepsilon\sum_{\ell\ge1}
 2\cos^2(\ell\pi y_0)
 |\widehat\eta(\ell\pi\varepsilon)|^2
 |F_k(t(\ell\pi)^2)|^2\\
 &\hspace{35mm}=\mathcal P_k(q)^2+O(\varepsilon^M)
 \end{aligned}
\]

for every fixed \(M\). Uniformly for \(0<q\le q_0\), the error after division
by \(q^{2r(k)}\) has the same estimate.

#### Proof

Write \(2\cos^2=1+\cos(2\ell\pi y_0)\). The nonoscillatory summand extends to
an even Schwartz function of \(u=\varepsilon\ell\). It vanishes at \(u=0\)
to order \(4r(k)\). Poisson summation therefore gives arbitrary algebraic
accuracy. The carrier term is the Fourier transform of the same Schwartz
function evaluated at frequency \(2y_0/\varepsilon\); the fixed interior
distance makes it superalgebraically small. For small \(q\), divide by
\(q^{2r(k)}\) and use the smooth bounded quotient
\(F_k(s)/s^{r(k)}\). \(\square\)

The apparently natural \(O(\varepsilon)\) Riemann-sum error is therefore not
sharp. Evenness, stationary cancellation, and an interior carrier improve it
beyond every algebraic order. We retain only \(O(\varepsilon^2)\) in the
theorems.

### Lemma 4.3 — ultra-early jet closure

Put \(\tau=t/h^2\), \(s=t\mu_{\ell,h}\), and suppose \(\tau\leq\tau_0\).
For the ramp/cosine pair, with \(r=r(k)\in\{1,2\}\),

\[
 \boxed{
 \left|a_{\ell k,h}(t)-{(-s)^r\over r!}m_{r,k,h}\right|
 \leq Cs^r\tau,
 \qquad
 m_{r,k,h}=\langle1,V_h^r\phi_{k,h}\rangle_h. }
 \tag{4.4}
\]

Moreover the conservative target preparation satisfies

\[
 \boxed{
 \varepsilon^{4r+1}
 \sum_{\ell=1}^{n-1}|\beta_{\ell,h}|^2\mu_{\ell,h}^{2r}
 =\|\eta^{(2r)}\|_2^2
 \left[1+O(\!\left((h/\varepsilon)^2\right))\right]. }
 \tag{4.5}
\]

#### Proof

Write \(T=tA_h\) and

\[
 f_\ell(z)=\langle1,e^{-(T+zV_h)}\phi_{k,h}\rangle_h.
\]

The path spectrum gives \(\|T\|\leq4\tau\) and \(0\leq s\leq4\tau\).
Dyson's expansion in \(z\) is therefore uniform in \(h\) on the displayed
range.  Since \(1\) is the stationary left vector and \(\phi_{k,h}\) is an
exact eigenvector of \(A_h\),

\[
 f_\ell'(0)
 =-m_{1,k,h}\int_0^1e^{-ut\lambda_{k,h}}\,du.
\]

For odd \(k\), this equals \(-m_{1,k,h}[1+O(t)]\).  For even \(k\),
reflection gives \(m_{1,k,h}=0\) exactly, so the entire first derivative
vanishes.  A second Dyson differentiation then gives

\[
 \tfrac12f_\ell''(0)=\tfrac12m_{2,k,h}+O(\tau),
\]

because replacing any of the intervening factors \(e^{-uT}\) by the identity
costs at most \(C\|T\|\).  The next Taylor term is \(O(s^{r+1})\), which is
\(O(s^r\tau)\).  This proves (4.4).

For (4.5), insert the conservative transform of Lemma 4.1 and the symbol
expansion

\[
 \mu_{\ell,h}^{r}=(\pi\ell)^{2r}
 \left[1+O((\ell h)^2)\right]
\]

on \(\ell\varepsilon=O(1)\).  Poisson summation and Plancherel turn the
zero-alias sum into \(\|\eta^{(2r)}\|_2^2\); the sinc, symbol, and alias
remainders are \(O((h/\varepsilon)^2)\) after the Schwartz tail is summed.
\(\square\)

## 5. Main finite-parameter theorem

### Theorem 5.1 — early and balanced resolved comparison

There are \(q_0>0\), \(h_0>0\), and \(C<\infty\) such that the following
holds for the canonical ramp and cosine source.

#### Balanced chart

For any fixed \(0<q_-<q_+<\infty\), whenever

\[
 q_-\le {t\over\varepsilon^2}\le q_+,
 \qquad0<h<h_0,\qquad {h\over\varepsilon}<h_0,
\]

one has

\[
 \boxed{
 \left|
 {\sqrt\varepsilon\,\mathcal N_{h,k}(t)\over\mathcal P_k(q)}-1
 \right|
 \le C_{q_-,q_+}
 \left[\varepsilon^2+\left({h\over\varepsilon}\right)^2\right]. }
\]

Equivalently, for squared norms,

\[
 \left|\varepsilon\mathcal N_{h,k}(t)^2-\mathcal P_k(q)^2\right|
 \le C_{q_-,q_+}\mathcal P_k(q)^2
 \left[\varepsilon^2+\left({h\over\varepsilon}\right)^2\right].
\]

#### Early chart

Let \(r=r(k)\). Uniformly for \(0<q\le q_0\),

\[
 \boxed{
 \left|
 {\sqrt\varepsilon\,\mathcal N_{h,k}(t)\over\mathcal P_k(q)}-1
 \right|
 \le C\left[
 q+\left({h\over\varepsilon}\right)^2
 +{t\over q^{r-1}}+\varepsilon^2
 \right]. }
\]

For odd \(k\), \(t/q^{r-1}=t\). For even \(k\), it is
\(t/q=\varepsilon^2\). Hence a simpler canonical bound is

\[
 \left|
 {\sqrt\varepsilon\,\mathcal N_{h,k}(t)\over\mathcal P_k(q)}-1
 \right|
 \le C\left[q+\delta_\varepsilon^2+\varepsilon^2\right].
\]

#### Proof

Insert Lemmas 3.2 and 3.3 mode by mode. On the effective band
\(\ell\varepsilon=O(1)\), Lemma 4.1 and

\[
 t\mu_{\ell,h}=\pi^2q(\ell\varepsilon)^2
 [1+O(\delta_\varepsilon^2)]
\]

give a relative \(O(\delta_\varepsilon^2)\) error. Lemma 3.2 contributes
\(O(t)\) relative to a first-order profile and \(O(t/q)\) relative to a
second-order profile. Lemma 3.3 contributes \(O(h^2)\), which is absorbed by
\(\delta_\varepsilon^2\). Lemma 4.2 supplies the remaining phase sum.

For completeness, very early times require one extra bookkeeping step. If
\(q\ge\delta_\varepsilon^4\), take sufficiently many integrations by parts in
Lemma 4.1; the alias tail is \(O(\delta_\varepsilon^2q^r)\) in the response
norm. If \(q<\delta_\varepsilon^4\), then

\[
 {t\over h^2}={q\over\delta_\varepsilon^2}<\delta_\varepsilon^2.
\]

Lemma 4.3 gives the full response jet with relative error
\(O(\tau+\delta_\varepsilon^2)=O(\delta_\varepsilon^2)\). Comparing the phase
function to its endpoint adds \(O(q)\). This proves the bound in the
ultra-early subchart and closes the gap between the Taylor and Fourier
arguments. \(\square\)

The split in the last paragraph is not an additional hypothesis. It shows
why no hidden relation between \(q\) and \(h/\varepsilon\) is needed for the
canonical ramp.

### 5.2 General modulation correction

Suppose \(V\in C^2\), \(V\ge v_->0\), and its first continuum moment vanishes,
\(m_1=\int V\phi=0\), while \(m_2\ne0\). Then the early bound acquires

\[
 \boxed{{|m_{1,h}|\over q},\qquad
 m_{1,h}=h\sum_iV(x_i)\phi(x_i).}
\]

Consequently a general second-order port requires

\[
 m_{1,h}=o(q).
\]

An \(O(h^2)\) midpoint estimate is enough only along paths with \(h^2=o(q)\).
The canonical ramp with even cosine source is stronger:
\(m_{1,h}=0\) exactly for every \(h\), by reflection pairing.

## 6. The heat-resolved theorem

The late chart allows \(\varepsilon/h\) to tend to zero, a finite constant, or
infinity. Only the diffusive wavelength must be resolved.

### Lemma 6.1 — two-copy cell quantization

Let \(Y,Y'\) be independent with density \(\rho_\varepsilon\), and let
\(Q_h(Y)\) be the centre of the cell containing \(Y\). Then, for every
\(\xi\),

\[
 \left|
 \left|\mathbb Ee^{i\xi Q_h(Y)}\right|^2
 -\left|\mathbb Ee^{i\xi Y}\right|^2
 \right|
 \le C\xi^2(h^2+h\varepsilon).
\]

#### Proof

Both squared moduli are real characteristic functions of differences of two
independent copies.  Couple

\[
 A=Q_h(Y)-Q_h(Y'),\qquad B=Y-Y'.
\]

The elementary identity

\[
 |\cos(\xi A)-\cos(\xi B)|
 \leq\frac{\xi^2}{2}|A^2-B^2|
\]

follows by integrating the derivative of \(\cos(\xi\sqrt u)\) with respect
to \(u\).  Now \(|A-B|\leq h\), while
\(\mathbb E|B|^2=O(\varepsilon^2)\) and
\(\mathbb E|A+B|\leq C(\varepsilon+h)\).  Hence

\[
 \mathbb E|A^2-B^2|
 \leq Ch(h+\varepsilon),
\]

which is the claimed \(C\xi^2(h^2+h\varepsilon)\) bound.  Comparing the two
cosines under this coupling is essential: separate second-order Taylor
bounds would leave an unnecessary \(O(\xi^2\varepsilon^2)\) term. \(\square\)

This quadratic estimate is sharper than comparing the two characteristic
functions separately, which loses a factor \(h/\sqrt t\). Squared response
norms naturally see the two-copy quantity.

### Theorem 6.2 — late phase comparison and atomic endpoint

There are \(Q,t_0,C>0\) such that, whenever

\[
 q={t\over\varepsilon^2}\ge Q,\qquad
 0<t<t_0,\qquad {h\over\sqrt t}<t_0,
\]

the phase comparison obeys

\[
 \left|
 {\sqrt\varepsilon\,\mathcal N_{h,k}(t)\over\mathcal P_k(q)}-1
 \right|
 \le C\left[t+{h^2+h\varepsilon\over t}\right].
\]

Moreover,

\[
 \boxed{
 \left|\sqrt t\,\mathcal N_{h,k}(t)^2-C_{F,k}^2\right|
 \le C\left[t+{h^2+\varepsilon^2\over t}\right]. }
\]

#### Proof

Use \(z=\sqrt t\,\ell\). The response envelope
\(Cs e^{-cs}\) restricts the sum to \(\ell=O(t^{-1/2})\). On this band,

\[
 t\mu_{\ell,h}=\pi^2z^2[1+O(h^2/t)].
\]

Lemma 3.2 contributes \(O(t)\), source midpoint quadrature is smaller, and
the finite target cutoff is exponentially small in \(t/h^2\). Lemma 6.1
contributes \(O((h^2+h\varepsilon)/t)\). After writing
\(2\cos^2=1+\cos(2\ell\pi y_0)\), Poisson summation in the \(z\)-variable
makes both the sum error and the interior carrier term \(O(t)\). This proves
the phase comparison.

Finally,

\[
 \sqrt q\,\mathcal P_k(q)^2
 =\int_0^\infty
 \left|\widehat\eta\!\left({\pi z\over\sqrt q}\right)\right|^2
 |F_k(\pi^2z^2)|^2\,dz.
\]

Evenness and a finite second moment give

\[
 \left|\sqrt q\,\mathcal P_k(q)^2-C_{F,k}^2\right|
 \le Cq^{-1}=C\varepsilon^2/t.
\]

The inequality \(2h\varepsilon\le h^2+\varepsilon^2\) completes the endpoint
bound. \(\square\)

The theorem explicitly permits a subcell mollifier \(\varepsilon\ll h\) once
\(h\ll\sqrt t\). Heat has then erased the preparation before the response is
read.

## 7. Canonical critical paths

Let \(t=\tau h^2\), with \(\tau>0\) fixed, and
\(\varepsilon=h^\alpha\), \(0<\alpha<1\). Then

\[
 q=\tau h^{2-2\alpha},\qquad
 \delta_\varepsilon^2=h^{2-2\alpha}.
\]

At the critical exponent

\[
 \alpha_c(r)={4r\over4r+1},
\]

the main power of \(h\) cancels. Theorem 5.1 gives the quantitative limits

\[
 \mathcal N_{h,k}(\tau h^2)
 ={ |m_{r,k}|\over r!}\|\eta^{(2r)}\|_2\tau^r
 \left[1+O\!\left(h^{2/(4r+1)}\right)\right].
\]

Thus, for the ramp,

\[
 \boxed{
 \begin{aligned}
 k\text{ odd},\quad\varepsilon=h^{4/5}:\quad
 \mathcal N_{h,k}(\tau h^2)
 &= {2\sqrt2g\over(k\pi)^2}\|\eta''\|_2\tau
 [1+O(h^{2/5})],\\
 k\text{ even},\quad\varepsilon=h^{8/9}:\quad
 \mathcal N_{h,k}(\tau h^2)
 &= {\sqrt2g^2\over(k\pi)^2}\|\eta^{(4)}\|_2\tau^2
 [1+O(h^{2/9})].
 \end{aligned}}
\]

These estimates turn the Stage VII critical exponents into finite-resolution
certificates. They also show a resolution barrier: at microscopic time,

\[
 q=\tau(h/\varepsilon)^2.
\]

The physical endpoint correction and the grid dispersion correction therefore
enter at the same order \(c^{-2}\), where \(c=\varepsilon/h\). Increasing the
number of cells across the preparation improves both errors simultaneously.

## 8. First pre-asymptotic correction

Suppose

\[
 F(s)=a_rs^r+a_{r+1}s^{r+1}+O(s^{r+2}),\qquad a_r\ne0.
\]

Put

\[
 J_j=\|\eta^{(j)}\|_2^2.
\]

Expansion under the phase integral gives

\[
 \boxed{
 {\mathcal P(q)\over |a_r|\sqrt{J_{2r}}q^r}
 =1+{a_{r+1}\over a_r}{J_{2r+1}\over J_{2r}}q+O(q^2). }
\]

Indeed, the cross term in \(|F|^2\) is
\(2a_ra_{r+1}s^{2r+1}\), and Parseval identifies its integral with
\(J_{2r+1}\).

For the standard Gaussian
\(\eta(x)=(2\pi)^{-1/2}e^{-x^2/2}\),

\[
 {J_{2r+1}\over J_{2r}}=2r+{1\over2}={4r+1\over2}.
\]

For the canonical ramp, direct expansion of the closed form for \(F_k\)
gives, for both parities,

\[
 {a_{r+1}\over a_r}=-{2+g\over2}.
\]

Therefore

\[
 \boxed{
 {\mathcal P_k(q)\over C_{r,k}q^r}
 =1-{(2+g)(4r+1)\over4}q+O(q^2). }
\]

At \(g=0.8\), the correction is \(-3.5q\) for odd modes and \(-6.3q\) for
even modes. This explains the pre-asymptotic slopes observed in the Stage VII
laboratory; they are not numerical bias.

## 9. Adversarial boundaries and counterexamples

### 9.1 Resolved length alone does not preserve a cancelled moment

For a general modulation, continuum cancellation need not be inherited by the
midpoint grid. Here is an explicit example. Take \(k=2\) and

\[
 p(x)=x^4-\left(2-{3\over\pi^2}\right)x^2,
 \qquad V(x)=1+\gamma p(x)
\]

with \(|\gamma|\) small enough to keep \(V>0\). Integration by parts gives

\[
 \int_0^1p(x)\cos(2\pi x)\,dx=0,
\]

while the intended next moment is nonzero:

\[
 \int_0^1p(x)^2\cos(2\pi x)\,dx
 ={3(-69+28\pi^2)\over2\pi^8}>0.
\]

but composite midpoint Euler--Maclaurin gives

\[
 h\sum_ip(x_i)\cos(2\pi x_i)
 =-{h^2\over4\pi^2}+O(h^4).
\]

Choose, for example, \(\varepsilon=h^{1/2}\) and \(q=h^3\). Then
\(h/\varepsilon\to0\), yet \(|m_{1,h}|/q\to\infty\): the spurious discrete
first jet dominates the intended second-order continuum signal. Exact
moment preservation, or the scale condition \(m_{1,h}=o(q)\), is necessary.

### 9.2 Other sharp boundaries

1. **Null port.** If \(g=0\), then \(F_k\equiv0\) and relative estimates with
   denominator \(\mathcal P_k(q)\) are meaningless; the response itself is
   exactly zero.

2. **Carrier approaching a boundary.** If
   \(\operatorname{dist}(y_0,\{0,1\})/\max\{\varepsilon,\sqrt t\}\) stays
   bounded, the oscillatory carrier no longer averages away. The
   reflecting-boundary constant replaces the interior constant.

3. **Nonconservative preparation.** Point sampling followed by an informal
   normalization changes the Fourier multiplier and may inject an
   \(O(h/\varepsilon)\) error. Lemma 4.1 is specific to exact cell masses.

4. **Rough mollifier.** A box profile has only algebraic Fourier decay and a
   derivative jump. The \(O((h/\varepsilon)^2)\) full-band claim can fail or
   acquire logarithms. \(C_c^\infty\) is stronger than necessary, but some
   weighted Fourier regularity through order \(2r+2\) is material.

5. **Unresolved balanced chart.** If \(h/\varepsilon\to c>0\) while \(q\)
   stays finite, the limit is the lattice phase function from Stage VII, not
   \(\mathcal P_k\).

6. **Unresolved late chart.** If \(t/h^2\) stays finite, the continuum
   dispersion \(\pi^2z^2\) is replaced by \(4\sin^2(\theta/2)\); the atomic
   continuum constant need not be correct.

7. **An atom at time zero.** The bound is a small-positive-time theorem. It
   does not extend to \(t=0\), where the full density response has no uniform
   continuum norm.

## 10. Exact statements versus extensions

### Proved in this memo

1. the discrete Lipschitz and weak Duhamel estimate of Lemmas 3.1--3.2;
2. second-order conservative coefficient and dispersion control in the
   early/balanced resolved charts;
3. the canonical ramp comparison bounds in Theorem 5.1, including arbitrarily
   early joint paths via the Fourier/Taylor split;
4. the late phase and atomic endpoint estimates of Theorem 6.2;
5. the \(O(h^{2/5})\) and \(O(h^{2/9})\) critical-path certificates;
6. the general first pre-asymptotic phase correction; and
7. the explicit discrete-moment counterexample.

### Not claimed

1. a uniform relative theorem when the limiting phase vanishes;
2. the same rates for arbitrary rough \(V\), rough preparations, nonuniform
   grids, or nonconservative deposition rules;
3. a placement-free theorem at \(\varepsilon/h=O(1)\) or
   \(t/h^2=O(1)\);
4. an arbitrary multiplication order \(r\ge3\) without bounds on mixed
   diffusion--multiplication words and all lower discrete moments; or
5. any conclusion about a fundamental geometry of physical reality.

The natural next theorem is a port-uniform version: replace the fixed cosine
by a finite or Sobolev-bounded source family, track the smallest nonzero phase
singular value, and determine precisely when the scalar error bounds survive
Gram assembly.
