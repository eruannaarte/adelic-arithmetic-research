# Operational Information Geometry IX

## Growing-band Gramians, causal flags, and effective dimension

- **Research status:** analytic theorem package and computational audit;
  not peer reviewed
- **Research, theorem development, computation, and writing:** Codex (OpenAI)
- **Originating direction and research environment:** TGN's human founder
- **Predecessor:** Operational Information Geometry VIII
- **Scope:** the declared one-way parabolic Markov model; not a physical theory

## Abstract

Stage VIII controlled one source direction across the resolved, finite-cell,
and atomic charts.  This stage replaces that direction by a source space and
asks whether its smallest nonzero response singular value remains stable.

The answer has a positive finite-dimensional part and a sharp negative
infinite-dimensional part.  For a zero-mean source \(f\), all three limiting
responses factor through the same Laplace observation

\[
 F_f(s)=\int_0^1 e^{-sV(x)}f(x)\,dx.
\]

Their common invisible space is exactly

\[
 \mathcal Z_V
 =\{f:\mathbb E[f\mid\sigma(V)]=0\}.
\]

After quotienting by this structural null space, every fixed finite source
space has a positive calibrated singular-value floor uniformly across a
compactified three-chart atlas whose uncalibrated lattice sector begins at
\(\tau_0>0\).  The raw \(\tau\downarrow0\) lattice endpoint is excluded; its
limiting phase has an analogous moment flag, while uniform finite-model
transfer there remains open.  In the early resolved chart, the first \(K\)
cosine ports under a strictly monotone modulation carry an exact causal flag:

\[
 \sigma_j(T_q|_{E_K})\asymp_K q^j,
 \qquad j=1,\ldots,K.
\]

Under the physical density normalization this produces the critical fan

\[
 \boxed{\alpha_j=\frac{4j}{4j+1}},
 \qquad \varepsilon=h^{\alpha_j},\quad t=\tau h^2.
\]

However, every chart map is compact.  Even when \(V\) is a strictly monotone
ramp and the analytic null space is zero, no infinite-dimensional
\(L^2\) or fixed Sobolev coercivity floor exists.  The standard chart Grams
have analytic Hankel kernels \(\Phi(V(x)+V(y))\), which impose an exponential
upper ceiling on their tail eigenvalues.  The correct growing-band theorem is
therefore relative:

\[
 \boxed{
 \text{finite band stable}
 \quad\Longleftarrow\quad
 \frac{\delta_K}{\gamma_K}\longrightarrow0,}
\]

where \(\gamma_K\) is the continuum quotient-Gram floor and \(\delta_K\)
is the calibrated finite-model Gram error.  This criterion yields rank,
singular-value, conditioning, and noise-aware detection guarantees.  It also
separates three distinct obstructions: exact symmetry nulls, compact
near-nulls, and finite-sensor rank loss.

## 1. From one response norm to a response operator

Let

\[
 H_0=\left\{f\in L^2(0,1):\int_0^1f(x)\,dx=0\right\},
\]

and assume \(V\in C^2[0,1]\) with \(V\ge v_->0\).  The canonical example is

\[
 V(x)=1+gx,\qquad g>0.
\]

On the cell-centred grid, \(h=1/n\) and \(x_i=(i+1/2)h\).  The reduced
source operator at target mode \(\ell\) is

\[
 K_{\ell,h}=A_h+\mu_{\ell,h}V_h,
\]

where \(A_h\) is the physical Neumann path Laplacian and

\[
 \mu_{\ell,h}=4h^{-2}\sin^2\!\left(\frac{\ell\pi h}{2}\right).
\]

For a declared source injection \(I_hf=f_h\), put

\[
 a_{\ell,h}(t;f)
 =\langle1,e^{-tK_{\ell,h}}f_h\rangle_h.
\]

If \(\beta_{\ell,h}\) is the target-preparation coefficient, the complete
target-density response operator has modal components

\[
 (R_{h,t}f)_\ell=\beta_{\ell,h}a_{\ell,h}(t;f),
 \qquad 1\le\ell<n.
\]

Its bilinear Gram is

\[
 \boxed{
 G_{h,t}(f,g)
 =\sum_{\ell=1}^{n-1}|\beta_{\ell,h}|^2
 a_{\ell,h}(t;f)\overline{a_{\ell,h}(t;g)}.}
 \tag{1.1}
\]

The Stage VIII scalar norm is only the diagonal \(G_{h,t}(f,f)\).  A
smallest singular value depends on every cross term.  Equal column norms do
not determine a Gramian: two identical columns and two opposite columns have
the same norms but different off-diagonal correlations.

The chart-normalized physical operators are, schematically,

\[
 \sqrt\varepsilon\,R_{h,t},\qquad
 \sqrt h\,R_{h,t},\qquad
 t^{1/4}R_{h,t}
\]

in the resolved, finite-cell lattice, and atomic charts.  Their limiting
Grams are defined next.

## 2. A common Laplace observation

Define

\[
 \boxed{
 F_f(s)=\langle1,e^{-sV}f\rangle
 =\int_0^1e^{-sV(x)}f(x)\,dx.}
 \tag{2.1}
\]

Let \(\eta\) be the even smooth probability kernel of the resolved target,
let \(Q=(Q_m)\) be a local lattice probability profile, and set

\[
 B_Q(\theta)=\sum_mQ_me^{im\theta},\qquad
 \omega(\theta)=4\sin^2(\theta/2).
\]

The three phase response maps are

\[
 (T_q^{\mathrm R}f)(u)
 =\widehat\eta(\pi u)F_f(\pi^2qu^2),
 \qquad u>0,
 \tag{2.2}
\]

\[
 (T_{\tau,Q}^{\mathrm L}f)(\theta)
 =B_Q(\theta)F_f(\tau\omega(\theta)),
 \qquad 0<\theta<\pi,
 \tag{2.3}
\]

where the lattice output measure is \(d\theta/\pi\), and

\[
 (T_\kappa^{\mathrm A}f)(r)
 =[1+\cos(2\pi\kappa r)]^{1/2}F_f(\pi^2r^2),
 \qquad r>0.
 \tag{2.4}
\]

Here \(\kappa\in[0,\infty)\) is the distance from a reflecting boundary in
units of \(\sqrt t\).  The notation \(\kappa=\infty\) removes the cosine
term and gives the interior atomic chart.

Their Grams are

\[
 \Gamma_q^{\mathrm R}=(T_q^{\mathrm R})^*T_q^{\mathrm R},\qquad
 \Gamma_{\tau,Q}^{\mathrm L}=(T_{\tau,Q}^{\mathrm L})^*T_{\tau,Q}^{\mathrm L},
 \qquad
 \Gamma_\kappa^{\mathrm A}=(T_\kappa^{\mathrm A})^*T_\kappa^{\mathrm A}.
 \tag{2.5}
\]

This factorization is the first main structural result: all three charts see
the source only through the same one-parameter family \(F_f\).  Their target
preparations and propagation scales change the output weight, not the source
algebra.

## 3. Exact common null space

Here \(q>0\) and \(\tau>0\).  At the raw endpoints \(q=0\) and
\(\tau=0\), every zero-mean source maps to zero; their nontrivial endpoint
limits require the calibrated moment flag of Sections 5--6.

Let \(\mu_V=V_\#(dx)\), and let

\[
 (C_Vf)(v)=\mathbb E[f(X)\mid V(X)=v]
\]

be conditional expectation onto the sigma-algebra generated by \(V\).  By
disintegration,

\[
 F_f(s)=\int e^{-sv}(C_Vf)(v)\,d\mu_V(v).
\]

Because \(\mu_V\) has compact support, uniqueness of the Laplace transform
gives the exact null theorem

\[
 \boxed{
 \ker T_q^{\mathrm R}
 =\ker T_{\tau,Q}^{\mathrm L}
 =\ker T_\kappa^{\mathrm A}
 =\mathcal Z_V,
 \qquad
 \mathcal Z_V=H_0\cap\ker C_V.}
 \tag{3.1}
\]

The assumptions on the target weights are mild: the resolved weight must be
nonzero on an interval; \(B_Q(0)=1\) supplies such an interval in the lattice
chart; and the boundary atomic weight is positive almost everywhere.

Consequences include:

1. if \(V\) is strictly monotone, \(\mathcal Z_V=\{0\}\);
2. if \(V\) is constant, every zero-mean source is invisible; and
3. if \(V(x)=V(1-x)\), every reflection-odd source is exactly invisible.

Thus “nonconstant modulation” is not sufficient for source identifiability.
Every smallest-nonzero-singular-value statement must be made on

\[
 E^\sharp=E/(E\cap\mathcal Z_V),
 \tag{3.2}
\]

not by treating numerical remnants of analytic null vectors as genuine
singular values.

## 4. Exact Hankel Gram kernels

Each phase Gram is an integral operator of the form

\[
 \Gamma(f,g)=\int_0^1\!\int_0^1
 f(x)\overline{g(y)}\,
 \Phi(V(x)+V(y))\,dx\,dy.
 \tag{4.1}
\]

For the standard Gaussian preparation used in the laboratory,

\[
 \boxed{
 \Phi_q^{\mathrm R}(A)
 =\frac{1}{2\sqrt\pi\sqrt{1+qA}}.}
 \tag{4.2}
\]

For an atomic interior target,

\[
 \boxed{
 \Phi^{\mathrm A}(A)=\frac{1}{2\sqrt{\pi A}},}
 \tag{4.3}
\]

and at reflecting-boundary coordinate \(\kappa\),

\[
 \boxed{
 \Phi_\kappa^{\mathrm A}(A)
 =\frac{1+e^{-\kappa^2/A}}{2\sqrt{\pi A}}.}
 \tag{4.4}
\]

For the one-cell lattice atom,

\[
 \boxed{
 \Phi_\tau^{\mathrm L}(A)
 =e^{-2\tau A}I_0(2\tau A),}
 \tag{4.5}
\]

where \(I_0\) is the modified Bessel function.  A general finite profile
replaces (4.5) by

\[
 \Phi_{\tau,Q}^{\mathrm L}(A)
 =\frac1\pi\int_0^\pi
 |B_Q(\theta)|^2e^{-\tau\omega(\theta)A}\,d\theta.
 \tag{4.6}
\]

These are exact kernels of the limiting phase Grams, not formulas for the
unreduced finite-time generator.

The two late charts meet the same atomic Gram:

\[
 \sqrt q\,\Gamma_q^{\mathrm R}\longrightarrow
 \Gamma_\infty^{\mathrm A},\qquad
 \sqrt\tau\,\Gamma_{\tau,Q}^{\mathrm L}\longrightarrow
 \Gamma_\infty^{\mathrm A}.
 \tag{4.7}
\]

For a fixed finite source space, both convergences hold in operator norm.
They follow by rescaling the output variable and dominated convergence.

## 5. Fixed-band atlas theorem

The raw early Gram degenerates as \(q\downarrow0\), so its correct endpoint
uses moment calibration.  Define

\[
 m_r(f)=\int_0^1V(x)^rf(x)\,dx.
\]

For a finite quotient \(E^\sharp\), choose an \(L^2\)-orthonormal,
moment-adapted basis on its orthogonal quotient complement,
\(e_1,\ldots,e_d\), with pivot orders \(r_1<\cdots<r_d\):

\[
 m_j(e_i)=0\quad(j<r_i),\qquad m_{r_i}(e_i)\ne0.
\]

Let

\[
 D_E(q)=\operatorname{diag}(q^{r_1},\ldots,q^{r_d}).
\]

Taylor expansion of \(F_{e_i}\) gives

\[
 \boxed{
 D_E(q)^{-1}\Gamma_q^{\mathrm R}D_E(q)^{-1}
 \longrightarrow H_E^\eta,\qquad q\downarrow0,}
 \tag{5.1}
\]

where

\[
 (H_E^\eta)_{ij}
 =\frac{(-1)^{r_i+r_j}m_{r_i}(e_i)
 \overline{m_{r_j}(e_j)}}{r_i!r_j!}
 \pi^{2(r_i+r_j)}
 \int_0^\infty|\widehat\eta(\pi u)|^2
 u^{2(r_i+r_j)}\,du.
 \tag{5.2}
\]

The distinct monomials \(u^{2r_i}\) make \(H_E^\eta\) positive definite.

Fix \(q_0,\tau_0>0\).  Compactify the early resolved chart
\(0\le q\le q_0\) with (5.1), the resolved-to-atomic chart
\(q_0\le q\le\infty\) and lattice-to-atomic chart
\(\tau_0\le\tau\le\infty\) with (4.7), and the reflecting coordinate
\(0\le\kappa\le\infty\).  Let \(Q\) vary in an \(\ell^1\)-compact
probability family with uniformly bounded first moment.

Explicitly, the chart Grams entering the compact atlas are

\[
 \begin{array}{c|c}
 \text{chart}&\widehat\Gamma_c\\ \hline
 \text{early resolved},\ 0\le q\le q_0
 &D_E(q)^{-1}\Gamma_q^{\mathrm R}D_E(q)^{-1}\\[1mm]
 \text{resolved to atomic},\ q_0\le q\le\infty
 &(1+q)^{1/2}\Gamma_q^{\mathrm R}\\[1mm]
 \text{lattice to atomic},\ \tau_0\le\tau\le\infty
 &(1+\tau)^{1/2}\Gamma_{\tau,Q}^{\mathrm L}\\[1mm]
 \text{atomic/boundary},\ 0\le\kappa\le\infty
 &\Gamma_\kappa^{\mathrm A}.
 \end{array}
 \tag{5.3}
\]

At \(q=0\), the first row means the continuous endpoint value
\(H_E^\eta\), not literal inversion of \(D_E(0)\).

### Theorem 5.1 — finite-source atlas

For every fixed finite \(E^\sharp\), the calibrated Gram family is continuous
and positive definite on the compactified atlas.  Therefore

\[
 \boxed{
 \gamma_E
 =\inf_{c\in\mathfrak A}
 \lambda_{\min}(\widehat\Gamma_c|_{E^\sharp})>0.}
 \tag{5.4}
\]

Equivalently, the normalized response singular floor is at least
\(\sqrt{\gamma_E}\).

This theorem is uniform in chart parameters, not in source dimension.  At
\(q=0\), it is uniform in the declared moment-weighted source metric, not in
raw \(L^2\).

## 6. The causal singular flag

Let

\[
 E_K=\operatorname{span}\{\phi_1,\ldots,\phi_K\},\qquad
 \phi_k(x)=\sqrt2\cos(k\pi x).
\]

If \(V\) is continuous and strictly monotone, the matrix

\[
 M_K=(\langle V^m,\phi_k\rangle)_{m,k=1}^K
\]

is invertible.  One proof augments it with \(m,k=0\) and applies the
Andreief identity.  On the ordered simplex, the determinant of
\((V(x_j)^m)\) and the cosine determinant both have fixed nonzero
Vandermonde signs.  Their product cannot integrate to zero.

Thus the pivot orders on \(E_K\) are exactly

\[
 r_j=j,\qquad 1\le j\le K.
\]

Because the output monomials
\(\widehat\eta(\pi u)u^{2j}\) are linearly independent, exterior powers of
the response operator give the full singular-value theorem—not merely
separate column slopes:

\[
 \boxed{
 \sigma_j(T_q^{\mathrm R}|_{E_K})\asymp_K q^j,
 \qquad j=1,\ldots,K,\quad q\downarrow0.}
 \tag{6.1}
\]

The singular values are ordered from largest to smallest.  Consequently,

\[
 \lambda_j(\Gamma_q^{\mathrm R}|_{E_K})\asymp_Kq^{2j},
 \qquad
 \det(\Gamma_q^{\mathrm R}|_{E_K})\asymp_Kq^{K(K+1)}.
 \tag{6.2}
\]

The same flag argument gives
\(\sigma_j(T_{\tau,Q}^{\mathrm L}|_{E_K})\asymp_K\tau^j\) as
\(\tau\downarrow0\) when the full lattice-phase output is retained and its
weight is nonzero near \(\theta=0\).  A finite target/time sensor array can
truncate that flag by rank and is treated separately in Section 11.

This is a multiplication-moment flag.  It does not assert that all mixed
source-diffusion--multiplication causal words have been cancelled.

## 7. Critical fan and resolution barrier

The continuum multiplication-phase response has the additional density
factor \(\varepsilon^{-1/2}\).  For fixed \(K\),

\[
 \boxed{
 \sigma_j(R_{\varepsilon,t}|_{E_K})
 \asymp_K\varepsilon^{-1/2}q^j,
 \qquad q=t/\varepsilon^2\downarrow0.}
 \tag{7.1}
\]

Here \(R_{\varepsilon,t}\) denotes that continuum phase response.  The same
law transfers to the finite-grid physical response only along paths satisfying
the grid-resolution, moment-leakage, mixed-word, and relative-gap conditions
of Sections 8--9.

Set \(t=\tau h^2\) and \(\varepsilon=h^\alpha\), with fixed \(\tau>0\).
The \(j\)-th exponent is

\[
 e_j(\alpha)=2j(1-\alpha)-\frac\alpha2.
\]

Therefore

\[
 \boxed{\alpha_j=\frac{4j}{4j+1}.}
 \tag{7.2}
\]

The \(j\)-th channel vanishes below this ridge, has finite nonzero amplitude
on it, and diverges above it, always in the declared density normalization.
Away from a ridge, the amplitude-based dimension staircase is

\[
 \boxed{
 d_{\mathrm{crit}}(\alpha)
 =\left\lfloor\frac{\alpha}{4(1-\alpha)}\right\rfloor,}
 \tag{7.3}
\]

truncated by \(K\).  At an integer boundary the last counted channel is
finite rather than divergent.

On the \(K\)-th ridge,

\[
 \frac\varepsilon h=n^{1/(4K+1)}.
\]

Hence genuine continuum resolution requires

\[
 \boxed{K=o(\log n).}
 \tag{7.4}
\]

This is necessary, not sufficient.  It does not control moment-matrix
conditioning, mixed causal words, discrete leakage, or the shrinking
observability floor.

## 8. Exact growing-band stability criterion

Let \(E_K\) be nested finite source spaces after quotienting the analytic
null.  Write \(\widehat\Gamma_{K,c}\) for the calibrated continuum Gram in
chart \(c\), and \(\widehat G_{K,h,c}\) for its finite-grid counterpart.
Define

\[
 \gamma_K
 =\inf_{c\in\mathfrak A}
 \lambda_{\min}(\widehat\Gamma_{K,c}),
 \tag{8.1}
\]

and

\[
 \delta_K
 =\sup_{c\in\mathfrak A(h,\varepsilon,t)}
 \|\widehat G_{K,h,c}-\widehat\Gamma_{K,c}\|_{\mathrm op}.
 \tag{8.2}
\]

### Theorem 8.1 — relative Gram stability

If \(\delta_K<\gamma_K\), then

\[
 \boxed{
 \lambda_{\min}(\widehat G_{K,h,c})
 \ge\gamma_K-\delta_K>0}
 \tag{8.3}
\]

uniformly over the declared chart path.  Moreover,

\[
 |\lambda_j(\widehat G_{K,h,c})
 -\lambda_j(\widehat\Gamma_{K,c})|\le\delta_K
 \tag{8.4}
\]

and

\[
 \left\|
 \widehat\Gamma_{K,c}^{-1/2}
 \widehat G_{K,h,c}
 \widehat\Gamma_{K,c}^{-1/2}-I
 \right\|_{\mathrm op}
 \le\frac{\delta_K}{\gamma_K}.
 \tag{8.5}
\]

Thus

\[
 \boxed{\delta_K/\gamma_K\to0}
 \tag{8.6}
\]

is sufficient for relative eigenvalue, singular-value, rank, and conditioning
stability.  The proof is Weyl's inequality followed by conjugation with the
continuum Gram square root.

Absolute convergence \(\delta_K\to0\) alone is insufficient.  The matrices

\[
 \operatorname{diag}(1,\gamma_K)
 \quad\text{and}\quad
 \operatorname{diag}(1,0)
\]

differ by only \(\gamma_K\), yet have different ranks.

For every fixed \(K\), the Stage VIII estimates imply
\(\delta_K\to0\) on admissible chart paths.  A diagonal argument therefore
produces some possibly very slow \(K(h,\varepsilon,t)\to\infty\) satisfying
(8.6), provided the early path also satisfies the conditions in Section 9.
This proves existence, not a useful explicit bandwidth schedule.

## 9. What finite transfer actually requires

Away from the early endpoint, safe source-band conditions are

\[
 K\varepsilon\to0\quad\text{(balanced resolved)},
\]

\[
 Kh\to0\quad\text{(finite-cell lattice)},
\]

and

\[
 K\sqrt t\to0\quad\text{(atomic)}.
\]

They express that source diffusion remains below the active target
frequency.  For a Neumann cosine band measured in raw \(L^2\), a conservative
Sobolev lift gives

\[
 \delta_{K,0}\le C(1+K^2)^3\mathcal E_{\mathrm{chart}},
 \tag{9.1}
\]

where the chart error is one of

\[
 \mathcal E_{\mathrm R}
 =\varepsilon^2+(h/\varepsilon)^2,
\]

\[
 \mathcal E_{\mathrm L}=h+\|w_h-Q\|_1,
\]

or, for a smooth interior atomic preparation,

\[
 \mathcal E_{\mathrm A}
 =t+\frac{h^2+\varepsilon^2}{t}.
\]

The \(K^6\) factor is safe bookkeeping, not a sharp rate.  In the Neumann
spectral \(H^s\) metric with \(s>5/2\), the corresponding absolute form
bounds are uniform in \(K\), but compactness still destroys a full-band lower
frame bound.

### 9.1 Discrete moment leakage

For a moment-adapted basis, define

\[
 m_{j,h}(e_{i,h})=\langle1,V_h^je_{i,h}\rangle_h
\]

and

\[
 \Delta_{E,h}(q)
 =\max_i\left[
 \sum_{0\le j<r_i}q^{j-r_i}|m_{j,h}(e_{i,h})|
 +|m_{r_i,h}(e_{i,h})-m_{r_i}(e_i)|
 \right].
 \tag{9.2}
\]

Mass cancellation \(m_{0,h}=0\) should be exact.  A spurious lower moment of
size \(h^2\) becomes \(h^2q^{j-r_i}\) after calibration and can dominate the
intended pivot.  Moment-fitted injection can remove these pure-multiplication
defects for each fixed \(K\), but its condition number is not uniform in
\(K\).

### 9.2 Mixed causal words

An early finite-grid path also requires \(Kh\to0\) so that the grid resolves
the source band.  Moment fitting still does not cancel words such as
\(V^jA\), or longer words in which \(A\) is not leftmost.  A leftmost
\(A\) vanishes after pairing with \(1\), but the remaining mixed words do
not.  If
\(r_d\) is the deepest pivot, a safe fixed-band condition is

\[
 \boxed{
 \frac{t\|A\|_{E_K}}{q^{r_d-1}}\longrightarrow0.}
 \tag{9.3}
\]

For a finite \(E_K\subset\operatorname{Dom}(A)\),

\[
 \|A\|_{E_K}
 =\sup\{\|Af\|_2:f\in E_K,\ \|f\|_2=1\}.
\]

For the first \(K\) cosines, \(r_d=K\) and
\(\|A\|_{E_K}\asymp K^2\), so

\[
 \boxed{\frac{tK^2}{q^{K-1}}\longrightarrow0.}
 \tag{9.4}
\]

A safe early error shape is therefore

\[
 \delta_K^{\mathrm{early}}
 \le C_K\left[
 q+(h/\varepsilon)^2+\varepsilon^2
 +\frac{tK^2}{q^{K-1}}+\Delta_{E_K,h}(q)
 \right].
 \tag{9.5}
\]

Every term on the right must be \(o(\gamma_K)\) for a relative growing-band
theorem.  On the fixed-\(K\) critical ridge,

\[
 \frac{tK^2}{q^{K-1}}
 =K^2\tau^{2-K}h^{(6K+4)/(4K+1)}\to0,
\]

so the fixed-\(K\) fan is consistent with the finite model.  No uniform
\(K(n)\) causal-word estimate is proved.

## 10. Compactness and the no-go theorem

Each response map has a square-integrable kernel of the form
\(w(z)e^{-s(z)V(x)}\): the lattice output interval is compact, while
\(V\ge v_->0\) supplies an integrable Gaussian tail in the resolved and
atomic charts.  Hence every phase response \(T\) is Hilbert--Schmidt and
compact.  Equivalently, its Gram \(T^*T\) is trace class.  Boundedness of the
Gram kernel alone would establish compactness of the Gram but would not by
itself prove that \(T\) is Hilbert--Schmidt.

### Theorem 10.1 — no infinite-band coercivity

Let \(E_K\) be nested with dense union in an infinite-dimensional subspace of
\(H_0/\mathcal Z_V\).  At every fixed chart point,

\[
 \boxed{
 \lambda_{\min}(\Gamma|_{E_K^\sharp})\longrightarrow0.}
 \tag{10.1}
\]

The same conclusion holds after any fixed Sobolev weighting whose synthesis
into \(L^2\) is bounded.  Quotienting exact nulls does not remove compact
near-nulls.

There is a stronger spectral ceiling.  If \(\Phi\) is analytic on a complex
neighborhood of \([2v_-,2v_+]\), polynomial approximation gives a rank
\(m+1\) kernel approximant because

\[
 p_m(V(x)+V(y))
 \in\operatorname{span}\{1,V,\ldots,V^m\}\otimes
 \operatorname{span}\{1,V,\ldots,V^m\}.
\]

Courant--Fischer then yields constants \(C<\infty\) and \(\rho>1\) such that
for every \(K\)-dimensional \(L^2\) source space,

\[
 \boxed{
 \lambda_{\min}(\Gamma|_{E_K})\le C\rho^{-K},
 \qquad
 \sigma_{\min}(T|_{E_K})\le\sqrt C\,\rho^{-K/2}.}
 \tag{10.2}
\]

The Gaussian resolved, fixed-\(\tau\) lattice, atomic, and compact boundary
kernels satisfy this hypothesis.  Constants deteriorate if \(v_-\downarrow0\)
or target and calibration weights degenerate.

This is an upper ceiling, not a matching lower estimate.  It shows that an
error budget only polynomially small in the mesh can support at most a
logarithmic-order band, and possibly less.

For the affine ramp, the explicit source profile

\[
 F_k(s)=\sqrt2e^{-s}
 \frac{gs[1-(-1)^ke^{-gs}]}{(gs)^2+(k\pi)^2}
 \tag{10.3}
\]

also gives the elementary bounds

\[
 \Gamma(\phi_k,\phi_k)\le Ck^{-4},\qquad
 \gamma_K\le CK^{-4}.
\]

The analytic ceiling can be much sharper because highly correlated columns
create near-null combinations long before individual column norms vanish.

## 11. Effective dimension and noise

The compactness theorem replaces “how many sources exist?” by “how many
source directions exceed the declared information threshold?”  Define

\[
 \boxed{
 d_\eta(T)=\#\{j:\sigma_j(T)\ge\eta\}.}
 \tag{11.1}
\]

The analytic ceiling implies

\[
 d_\eta(T)=O(\log(1/\eta))
\]

for a fixed analytic chart, up to chart-dependent constants.  In the fixed-
\(K\) early flag, \(\sigma_j\asymp_Kq^j\), so the number above threshold is
controlled by \(\log(1/\eta)/|\log q|\) within the range where the fixed-band
constants remain valid.

Suppose a chart-normalized, whitened observation has independent Gaussian
noise of standard deviation \(\sigma\), an intervention has declared source
amplitude \(a\), and the experiment is repeated \(N\) times.  Amplitude and
unit norm are measured in the same declared calibrated source metric used by
\(\gamma_K-\delta_K\).  For a unit source direction \(u\), the optimal
equal-prior error between zero and \(au\) is

\[
 \Phi\!\left(-\frac{a\sqrt N\,\|Ru\|}{2\sigma}\right).
\]

Here \(\Phi\) denotes the standard normal cumulative distribution function,
not the Hankel kernel of Section 4.

If the certified finite Gram floor is \(\gamma_K-\delta_K\), worst-direction
error is at most \(\alpha<1/2\) whenever

\[
 \boxed{
 N\ge
 \frac{4\sigma^2[\Phi^{-1}(1-\alpha)]^2}
 {a^2(\gamma_K-\delta_K)}.}
 \tag{11.2}
\]

There is no finite background-uniform theorem for distinguishing an exact
zero channel from an arbitrarily weak nonzero channel.  A noise claim must
declare source cost, output whitening, modulation contrast, target
excitation, and a positive threshold.

Finite sensors add a different obstruction.  If only \(M\) scalar target/time
measurements are retained, the response rank is at most \(M\).  Recovering
\(K\) directions requires \(M\ge K\) and a lower frame bound for the sampled
weighted monomials.  The complete-density continuum Gram does not provide
that bound automatically.

## 12. Computational audit

The Stage IX laboratory assembles complete finite response matrices, their
Gramians, the exact limiting Hankel kernels, and independently evaluated
phase integrals.  It uses symmetric tridiagonal reduction for the source
blocks, a small dense Kronecker exponential as an independent control, and
high-precision arithmetic for the smallest continuum singular values.

The audit is ordinary floating point and high-precision quadrature, not an
outward-rounded proof.  Its main controls are:

- constant modulation annihilates every nonconstant source exactly;
- reflection-symmetric modulation annihilates every odd source, while even
  sources remain active;
- the finite modal reduction agrees with the dense joint generator;
- Gram eigenvalues agree with squared response singular values;
- fixed source bands converge in every chart, while source bands at the
  active target frequency retain a nonzero diffusion error;
- the exact Hankel kernels agree with independent one-dimensional phase
  integrals to more than 50 decimal digits; and
- finite sensing exhibits the exact rank ceiling \(\operatorname{rank}\le M\).

For \(K=4\), the last dyadic early-time step gives fitted singular powers

\[
 0.9875,\quad1.9775,\quad2.9675,\quad3.9575,
\]

approaching the predicted \(1,2,3,4\).  The Gram determinant power is
\(19.7802\), approaching the predicted \(K(K+1)=20\).  In the tested ramp,
successive balanced and atomic smallest singular values eventually shrink by
factors about \(0.04461\) and \(0.06068\) per added source direction.  At
\(K=10\), ordinary double precision reports ranks six or seven, depending on
the chart, while the high-precision Gram retains all ten positive directions.
Moment preconditioning reduces one tested response condition number from
about \(1.85\times10^9\) to \(5.20\times10^2\), but only by using source
columns with \(L^2\) norms as large as \(2.37\times10^{13}\).  The apparent
conditioning gain is therefore not free information.

All 23 focused Stage IX laboratory tests and the six adversarial controls
pass.  The clean complete repository run passes 316 tests, and the full
Stage IX laboratory completes in about 5.6 seconds on the reference machine.

## 13. Falsification ledger

| Tempting statement | Correct boundary |
|---|---|
| a nonconstant \(V\) makes every source visible | false; the exact null is \(\mathbb E[f\mid\sigma(V)]=0\) |
| quotienting exact nulls gives an infinite lower frame bound | false; the quotient response remains compact |
| every finite Sobolev weighting fixes compact ill-posedness | false whenever its synthesis into \(L^2\) is bounded |
| nonzero column norms imply source identifiability | false; correlated columns can form near-null combinations |
| fixed-band convergence implies growing-band stability | false unless \(\delta_K=o(\gamma_K)\) |
| \(K=o(\log n)\) proves the diagonal critical theorem | false; it is only the geometric resolution condition |
| moment fitting controls the full causal expansion | false; mixed \(A\)-\(V\) words require (9.3) |
| the continuum flag proves the finite flag on every early path | false without moment, mixed-word, and relative-gap control |
| a full continuum output theorem covers finite sensors | false; \(M\) scalar samples have rank at most \(M\) |
| whitening creates information | false; the norm and noise cost of whitening must be retained |
| a tiny double-precision singular value is an analytic null | unsupported; exact symmetry or certified arithmetic is required |
| these Gramians describe fundamental spacetime | unsupported; they belong to the declared operational model |

## 14. Interpretation

The stage distinguishes three meanings that are easily conflated:

1. **algebraic visibility:** whether a source survives the exact quotient
   \(H_0/\mathcal Z_V\);
2. **stable visibility:** whether its singular value exceeds discretization,
   calibration, and noise; and
3. **sampled visibility:** whether the declared finite sensor frame actually
   retains it.

The causal flag is a genuine geometric hierarchy inside this model.  It says
that different source combinations first appear at different multiplication-
moment orders.  The compactness theorem says, just as importantly, that this
hierarchy becomes progressively harder to invert.  More algebraically visible
directions do not imply an unlimited number of stably recoverable directions.

This is the useful milestone: the three asymptotic charts now share one source
quotient and one stability language.  Geometry determines the exact null;
scale determines the causal amplitude; discretization determines
\(\delta_K\); and the continuum spectrum determines \(\gamma_K\).  None can
be replaced by the others.

## 15. Literature and novelty boundary

Ill-posedness and singular-value analysis for truncated Laplace transforms
are classical.  Relevant primary references include:

- R. R. Lederman and V. Rokhlin, *On the analytical and numerical properties
  of the truncated Laplace transform I*, SIAM Journal on Numerical Analysis
  53 (2015), 1214--1235,
  <https://doi.org/10.1137/140990681>.
- R. R. Lederman and V. Rokhlin, *On the analytical and numerical properties
  of the truncated Laplace transform. Part II*, SIAM Journal on Numerical
  Analysis 54 (2016), 665--687,
  <https://doi.org/10.1137/15M1028583>.
- R. R. Lederman and S. Steinerberger, *Stability estimates for truncated
  Fourier and Laplace transforms* (2016),
  <https://arxiv.org/abs/1605.03866>.
- M. Bertero, P. Boccacci, and E. R. Pike, *On the recovery and resolution of
  exponential relaxation rates from experimental data: a singular-value
  analysis of the Laplace transform inversion in the presence of noise*,
  Proceedings of the Royal Society A 383 (1982), 15--29,
  <https://doi.org/10.1098/rspa.1982.0117>.

No priority claim is made for Laplace uniqueness, compact integral operators,
Hankel kernels, analytic low-rank approximation, singular-value perturbation,
or Gaussian testing.  The provisional contribution here is their operational
assembly for this declared model: the common conditional-expectation quotient,
the exact three-chart Gram kernels, the fixed-band compact atlas, the complete
causal singular flag, the critical fan, the relative diagonal criterion, and
the separation of exact, compact, and finite-sensor nullity.  Literature
novelty remains provisional until independent specialist review.

## 16. Reproduction

Install the dedicated dependencies and run the numerical and adversarial
laboratories:

```text
python -m pip install -r oig_ix_growing_band_requirements.txt
python -m py_compile oig_ix_growing_band.py \
  test_oig_ix_growing_band.py \
  test_oig_ix_adversarial_controls.py
python -m unittest -v test_oig_ix_growing_band.py
python -m unittest -v test_oig_ix_adversarial_controls.py
python oig_ix_growing_band.py --fast
python oig_ix_growing_band.py
python -m unittest discover -v
```

The detailed proof is in `OIG_IX_GROWING_BAND_THEOREM.md`; the computational
report is `oig_ix_growing_band.md`; and the independent proof review and
counterexamples are in `OIG_IX_ADVERSARIAL_AUDIT.md`.

The exact modal reductions, null controls, and finite-sampling rank bounds are
algebraic.  Fitted convergence rates and high-precision quadrature are
verification evidence, not interval certificates.

## 17. Next research order

1. **Certify the observable spectrum — completed in Stage X.** The late
   continuous core is outward-certified through \(K=8\), and the complete
   declared four-stratum atlas is certified at \(K=2\).  Asymptotic lower
   constants and a matching factorial lower law remain open; Stage X proves
   a nonmatching explicit \(e^{-O(K^2)}\) lower bound.
2. **Optimize effective rank.** Choose several times and target profiles to
   maximize the number of singular values above a declared noise threshold,
   with source cost and output whitening fixed in advance.
3. **Resolve the two-frequency transition.** Derive the limiting operator when
   \(K\varepsilon\), \(Kh\), or \(K\sqrt t\) tends to a nonzero constant and
   source diffusion survives; separately close the calibrated
   \(\tau\downarrow0\) lattice moment filtration.
4. **Build the full causal-word filtration.** Replace pure multiplication
   moments by the noncommutative algebra generated by \(A\) and \(V\), and
   quantify how symmetry breaking opens exact null ports.
5. **Develop finite-frame sensing.** Determine time/profile sample counts and
   designs that preserve the continuum effective rank rather than assuming a
   complete density output.
6. **Continue to path-space sensing.** Test whether jump counts and holding
   times factor through the same Laplace quotient or expose additional source
   directions.
7. **Only afterward open the wave branch.** Replace parabolic compactification
   by finite-speed propagation and identify which parts of the Gram atlas
   survive.

Stage X completes the first target with generalized-metric Arb certificates.
Its next handoff is finite-model transfer: enclose the discretization,
mixed-word, target-preparation, boundary, and sensor-frame error in the same
source metric, then prove that it lies below the certified continuum floor.
