# Operational Information Geometry XI — finite-model transfer theorem

## Metric-normalized response transport, calibrated causal remainders, and certified mesh budgets

**Status:** analytic research memo; not peer reviewed

**Model:** the canonical affine ramp

\[
 V(x)=1+\frac45x
\]

with the first \(K\) Neumann cosine source ports, the cell-centred Neumann
path grid, and the resolved, one-cell lattice, atomic-interior, and
reflecting-boundary response charts of Stages VIII--X.

**Purpose:** turn the Stage X continuum lower certificates into precise
sufficient conditions for a finite path-grid experiment to preserve the
same observable directions.

**Epistemic rule:** the operator perturbation theorems and the exact
three-port mixed-word calculation below are proved.  Chartwise rates are
the rigorous conservative rates established by the Stage VIII--IX estimates
when their stated preparation and regularity hypotheses hold.  Any sharper
rate must be certified for the actual finite model.  No growing-\(K\)
full-atlas theorem is claimed.

---

## 1. Main conclusions

Let \(T_{K,c}\) be a continuum response operator in chart \(c\), after the
declared output whitening and source normalization, and let
\(T_{K,h,c}\) be its finite-grid counterpart transported into the same output
space.  If

\[
 \lambda_{\min}(T_{K,c}^{*}T_{K,c})\ge L_K
\]

and

\[
 \|T_{K,h,c}-T_{K,c}\|\le \eta_K<\sqrt{L_K},
\]

then

\[
 \boxed{
 \lambda_{\min}(T_{K,h,c}^{*}T_{K,h,c})
 \ge (\sqrt{L_K}-\eta_K)^2>0.}
 \tag{1.1}
\]

This response-level theorem is sharper than first converting the response
error to a Gram error.  If a direct interval computation instead proves

\[
 \delta_K
 =\|S^{-1/2}(G_{K,h,c}-G_{K,c})S^{-1/2}\|<L_K,
\]

then the Stage IX--X conclusion remains

\[
 \boxed{
 \lambda_{\min}(G_{K,h,c},S)\ge L_K-\delta_K>0.}
 \tag{1.2}
\]

The error is not one undifferentiated consistency term.  A valid certificate
must account for

\[
 \eta_K\le
 \eta_{\rm space}+\eta_{\rm prep}+\eta_{\rm bdry}
 +\eta_{\rm word}+\eta_{\rm sens}+\eta_{\rm white}
 +\eta_{\rm source\ metric}.
 \tag{1.3}
\]

The terms in (1.3) respectively measure spatial/source discretization,
target deposition, boundary-chart transport, the full mixed
diffusion--multiplication remainder, sensor truncation, output whitening,
and source-metric transport.  Each term has an exact operator definition in
Section 4.  Thus the decomposition is not an informal error taxonomy: it is
a telescoping identity followed by the triangle inequality.

For fixed \(K\), the Stage VIII estimates imply that the physical
discretization, preparation, boundary, and mixed-response terms tend to zero
on every admissible chart path, after exact nulls and early causal
calibration are treated correctly.  A sensor or metric term vanishes only
when the sensor family and metric transport are themselves consistent.
Under those hypotheses, every Stage X positive continuum floor transfers to
a sufficiently fine finite model.

For the complete two-port atlas, Stage X proved the rational bracket

\[
 10^{-19}\le\gamma_2^{\rm full}\le10^{-6}.
\]

Consequently, either a direct Gram certificate

\[
 \delta_2<10^{-19}
 \tag{1.4}
\]

or a matched response certificate

\[
 \eta_2<10^{-9.5}=3.162277660\ldots\times10^{-10}
 \tag{1.5}
\]

proves finite-grid two-port visibility everywhere on the declared atlas.
The tiny tolerance is a mathematical consequence of using the presently
available *global* lower certificate; it is not a claim that the true floor
is close to \(10^{-19}\).

For the three late common-window charts, the \(K\le8\) Stage X floors give
much better chart-restricted budgets.  Section 8 lists them.

The companion Stage XI certificate already closes one nontrivial physical
case: the complete finite Neumann dynamics at the one-cell lattice point
\(\tau=1\), \(K=1\), and \(n=7\), in both declared source metrics.  It also
certifies phase-grid quadrature transfer through \(K=8\).  Those results do
not yet cover the complete \(K=2\) atlas.

---

## 2. The common comparison problem

### 2.1 Continuum source and output metrics

Let \(C_K:\mathbb C^K\to E_K\) synthesize the declared source basis and let
\(S_K\succ0\) be its source-cost Gram.  In the raw \(L^2\) cosine metric,
\(S_K=I\).  In the declared continuum \(H^1\) metric,

\[
 S_K=\operatorname{diag}(1+(k\pi)^2)_{k=1}^K.
 \tag{2.1}
\]

For a chart \(c\), write \(R_{K,c}:E_K\to Y_c\) for the response and
\(W_c\succ0\) for the declared output whitening.  The normalized continuum
operator is

\[
 \mathcal A_{K,c}=W_c^{1/2}R_{K,c}C_KS_K^{-1/2},
 \qquad
 \widetilde G_{K,c}=\mathcal A_{K,c}^{*}\mathcal A_{K,c}.
 \tag{2.2}
\]

Its ordinary eigenvalues are exactly the generalized eigenvalues of
\((G_{K,c},S_K)\), where \(G_{K,c}=C_K^*R_{K,c}^*W_cR_{K,c}C_K\).

### 2.2 Finite model and output bridge

On the cell-centred grid \(x_i=(i+1/2)h\), \(h=1/n\), let

\[
 A_h=h^{-2}L_n,
 \qquad
 K_{\ell,h}=A_h+\mu_{\ell,h}V_h,
 \qquad
 \mu_{\ell,h}=4h^{-2}\sin^2\frac{\ell\pi h}{2}.
 \tag{2.3}
\]

For an injection \(I_h:E_K\to\mathbb C^n\), target coefficient
\(\beta_{\ell,h}\), and physical time \(t\), the modal response is

\[
 (R_{K,h,t}f)_\ell
 =\beta_{\ell,h}
 \langle1,e^{-tK_{\ell,h}}I_hf\rangle_h.
 \tag{2.4}
\]

The finite and limiting outputs need not literally be the same Hilbert
space.  A proof must therefore declare a norm-preserving or contractive
bridge

\[
 J_{h,c}:Y_{h,c}\longrightarrow\mathcal Y_c.
 \tag{2.5}
\]

For modal sums, \(J_{h,c}\) is the chart-normalized piecewise-constant
embedding of the rescaled modal lattice; for a finite sensor array it also
contains the declared reconstruction or sampling operator.  The continuum
operator is embedded into the same \(\mathcal Y_c\).  Without (2.5), the
expression \(R_{h,c}-R_c\) is undefined.

If the finite source cost is \(S_{K,h}\succ0\) and its output whitening is
\(W_{h,c}\), put

\[
 \mathcal A_{K,h,c}
 =J_{h,c}W_{h,c}^{1/2}R_{K,h,c}I_hC_KS_{K,h}^{-1/2}.
 \tag{2.6}
\]

All calibration factors, including the early \(D_K(q)^{-1}\), belong inside
\(R\), \(C\), or \(S^{-1/2}\) *before* the difference between (2.2) and
(2.6) is taken.

---

## 3. Two transfer theorems

### Theorem 3.1 — normalized-response transfer

Assume the continuum and finite normalized response operators in
(2.2) and (2.6) have the same domain \(\mathbb C^K\) and common output
comparison space.  Suppose

\[
 \lambda_{\min}(\mathcal A_{K,c}^*\mathcal A_{K,c})\ge L_K>0,
 \qquad
 \|\mathcal A_{K,h,c}-\mathcal A_{K,c}\|\le\eta_K.
 \tag{3.1}
\]

Then every singular value obeys

\[
 |\sigma_j(\mathcal A_{K,h,c})-\sigma_j(\mathcal A_{K,c})|
 \le\eta_K,
 \tag{3.2}
\]

and in particular

\[
 \boxed{
 \lambda_{\min}(G_{K,h,c},S_{K,h})
 \ge(\sqrt{L_K}-\eta_K)_+^2.}
 \tag{3.3}
\]

#### Proof

For every unit \(z\in\mathbb C^K\),

\[
 \|\mathcal A_{K,h,c}z\|
 \ge\|\mathcal A_{K,c}z\|
 -\|(\mathcal A_{K,h,c}-\mathcal A_{K,c})z\|
 \ge\sqrt{L_K}-\eta_K.
\]

Taking the infimum and squaring proves (3.3).  The full statement (3.2) is
the standard min--max singular-value perturbation inequality.  No
coordinate-dependent whitening argument is used.  \(\square\)

### Theorem 3.2 — fixed-source-metric Gram transfer

Suppose the same source cost \(S_K\) is used to compare the two Grams.  Put

\[
 \mathcal A=\mathcal A_{K,c},
 \qquad
 \mathcal B=J_{h,c}W_{h,c}^{1/2}R_{K,h,c}I_hC_KS_K^{-1/2}.
\]

If

\[
 \|\mathcal B-\mathcal A\|\le\eta,
 \qquad
 \|\mathcal A\|\le M,
 \tag{3.4}
\]

then

\[
 \boxed{
 \|\mathcal B^*\mathcal B-\mathcal A^*\mathcal A\|
 \le 2M\eta+\eta^2.}
 \tag{3.5}
\]

If instead this metric-normalized Gram difference is enclosed directly by
\(\delta\), then

\[
 \boxed{
 \lambda_{\min}(G_{K,h,c},S_K)\ge L_K-\delta.}
 \tag{3.6}
\]

#### Proof

Write \(E=\mathcal B-\mathcal A\).  Then

\[
 \mathcal B^*\mathcal B-\mathcal A^*\mathcal A
 =\mathcal A^*E+E^*\mathcal A+E^*E,
\]

which gives (3.5).  Equation (3.6) is Weyl's inequality.  \(\square\)

### Corollary 3.3 — a changed finite source metric

If a direct fixed-\(S_K\) Gram comparison gives

\[
 \|S_K^{-1/2}(G_{K,h,c}-G_{K,c})S_K^{-1/2}\|\le\delta
\]

and

\[
 \rho=
 \|S_K^{-1/2}(S_{K,h}-S_K)S_K^{-1/2}\|<1,
 \tag{3.7}
\]

then

\[
 \boxed{
 \lambda_{\min}(G_{K,h,c},S_{K,h})
 \ge\frac{L_K-\delta}{1+\rho}.}
 \tag{3.8}
\]

Indeed \(G_{K,h,c}\succeq(L_K-\delta)S_K\) and
\(S_{K,h}\preceq(1+\rho)S_K\).  Thus an ordinary Euclidean difference
\(\|G_h-G\|\) is not a generalized-spectrum certificate unless \(S=I\) is
part of the declaration.

For sampled cosine ports the midpoint injection is exactly an \(L^2\)
isometry whenever \(K<n\).  If one instead declares the discrete \(H^1\)
cost

\[
 S_{K,h}=\operatorname{diag}(1+\mu_{k,h}),
\]

then, for \(K h\le1\),

\[
 \rho\le
 \max_{k\le K}
 \frac{(k\pi)^4h^2}{12(1+(k\pi)^2)}
 \le\frac{(K\pi h)^2}{12}.
 \tag{3.9}
\]

Here \(1-(\sin x/x)^2\le x^2/3\) was used with
\(x=k\pi h/2\).  Alternatively, retaining the continuum matrix (2.1) as
the declared finite source cost makes \(\rho=0\).

---

## 4. Exact error decomposition

Choose intermediate normalized response operators

\[
 \mathcal A^{(0)}=\mathcal A_{K,c},
 \quad \mathcal A^{(1)},\ldots,\mathcal A^{(6)}
 =\mathcal A_{K,h,c},
\]

by making the following replacements one at a time:

1. continuum phase integration by the transported spatial/modal quadrature;
2. ideal target profile by the deposited finite target;
3. ideal boundary coordinate and image factor by the finite geometry;
4. frozen multiplication response by the full
   \(A_h+\mu V_h\) response;
5. complete output by the declared finite sensor map; and
6. continuum source/output metrics by the declared finite metrics.

Define

\[
 \eta_j=\|\mathcal A^{(j)}-\mathcal A^{(j-1)}\|.
 \tag{4.1}
\]

Then the identity

\[
 \mathcal A_{K,h,c}-\mathcal A_{K,c}
 =\sum_{j=1}^6(\mathcal A^{(j)}-\mathcal A^{(j-1)})
\]

gives

\[
 \boxed{
 \eta_K\le
 \eta_{\rm space}+\eta_{\rm prep}+\eta_{\rm bdry}
 +\eta_{\rm word}+\eta_{\rm sens}+\eta_{\rm metric}.}
 \tag{4.2}
\]

Splitting the last term into source and output whitening gives (1.3).
The order of replacements may be changed, but every intermediate operator
must be explicit.  Otherwise two omitted changes can silently cancel in a
numerical residual and defeat reproducibility.

### 4.1 Columnwise enclosure

Let \(u_1,\ldots,u_K\) be an \(S_K\)-orthonormal source basis.  If a validated
calculation gives

\[
 \|(\mathcal A^{(j)}-\mathcal A^{(j-1)})u_i\|\le e_{j,i},
\]

then

\[
 \boxed{
 \eta_j\le\left(\sum_{i=1}^Ke_{j,i}^2\right)^{1/2}.}
 \tag{4.3}
\]

This Hilbert--Schmidt bound is often substantially sharper than multiplying
the largest entry error by \(K\).  A direct interval singular-value bound on
the error matrix is sharper still.

### 4.2 Direct form enclosure

When only squared responses are available, polarization gives the cross
terms.  For a complex source space,

\[
 4\langle u,Gv\rangle
 =\sum_{m=0}^3i^m\,G(u+i^mv,u+i^mv).
 \tag{4.4}
\]

Thus a uniform outward-rounded quadratic-form oracle yields every Gram
entry without assuming that separate scalar norm fits have correlated
errors.  Interval inertia of

\[
 G_{K,h,c}-(L_K-\delta)S_K
\]

can then certify transfer directly, avoiding a pessimistic norm conversion.

---

## 5. Canonical chartwise bounds

The following are sufficient, conservative forms.  Constants depend on a
fixed compact chart region, the declared target regularity and boundary
separation, and the fixed modulation \(V\), but not on \(h,\varepsilon,t\).
For growing \(K\), their \(K\)-dependence must be retained or certified.

### 5.1 Spatial and source-band discretization

For the first \(K\) midpoint-sampled cosines,

\[
 \langle\phi_{j,h},\phi_{k,h}\rangle_h=\delta_{jk},
 \qquad K<n.
 \tag{5.1}
\]

Moreover

\[
 0\le(k\pi)^2-\mu_{k,h}\le\frac{(k\pi)^4h^2}{12}.
 \tag{5.2}
\]

For \(f\in W^{2,1}(0,1)\), composite midpoint quadrature has the safe bound

\[
 \left|h\sum_i f(x_i)-\int_0^1f(x)\,dx\right|
 \le\frac{h^2}{2}\|f''\|_{L^1}.
 \tag{5.3}
\]

Applied to \(f=e^{-sV}u_i\) and integrated against the declared chart
weight, (5.3) gives an explicit finite constant for
\(\eta_{\rm space}\).  The cosine Bernstein estimates

\[
 \|u'\|_2\le K\pi\|u\|_2,
 \qquad
 \|u''\|_2\le(K\pi)^2\|u\|_2
 \tag{5.4}
\]

make the band dependence explicit.  A conservative form-level aggregation
from Stage IX is

\[
 \boxed{
 \delta_{K,{\rm regular}}
 \le C_{c}(1+K^2)^3\mathcal E_c.}
 \tag{5.5}
\]

The factor \((1+K^2)^3\) is safe Sobolev bookkeeping, not a sharp asymptotic
law.  The chart errors are

\[
 \mathcal E_{\rm R}
 =\varepsilon^2+(h/\varepsilon)^2
 \tag{5.6}
\]

on a compact balanced-resolved \(q=t/\varepsilon^2\) interval,

\[
 \mathcal E_{\rm L}=h+\|w_h-Q\|_1
 \tag{5.7}
\]

at fixed finite-cell lattice time, and

\[
 \mathcal E_{\rm A}
 =t+\frac{h^2+\varepsilon^2}{t}
 \tag{5.8}
\]

for the smooth interior atomic preparation.  The corresponding safe
geometric resolution conditions are

\[
 K\varepsilon\to0,
 \qquad Kh\to0,
 \qquad K\sqrt t\to0,
 \tag{5.9}
\]

respectively.  They are necessary bookkeeping conditions for these bounds,
not by themselves transfer theorems.

### 5.2 Target preparation

For exact cell integration of an even smooth resolved kernel, conservation
removes the first-order cell error.  The target multiplier and lattice
symbol contribute the \((h/\varepsilon)^2\) term in (5.6).  A truncated
Schwartz preparation must also include its normalized boundary tail; a
bound that treats the untruncated whole-line Gaussian as the deposited
finite target has changed the experiment.

For a finite-cell target, the robust preparation metric is

\[
 \boxed{\eta_{\rm prep}^{\rm L}\ \text{or}\
 \delta_{\rm prep}^{\rm L}
 \ \lesssim\ \|w_h-Q\|_1,}
 \tag{5.10}
\]

with the response- versus Gram-level constant chosen consistently.
Weak convergence alone is insufficient at fixed microscopic time.

For an atomic target of barycentre \(\bar y_h\) and variance

\[
 \sigma_h^2=\sum_iq_{h,i}(x_i-\bar y_h)^2,
\]

the shape error is controlled by

\[
 \boxed{\sigma_h^2/t.}
 \tag{5.11}
\]

Thus \(t/h^2\to\infty\) does not by itself define the atomic chart; one also
needs \(\sigma_h^2/t\to0\).

### 5.3 Reflecting boundary

Put

\[
 \kappa_h=\frac{d_h}{\sqrt t},
\]

where \(d_h\) is the target barycentre's distance from the nearest reflecting
boundary.  The continuum boundary Gram contains

\[
 1+\cos(2\pi\kappa r).
\]

For fixed \(K\), its derivative in \(\kappa\) is integrably dominated, so

\[
 \delta_{\rm coordinate}
 \le B_K|\kappa_h-\kappa|
 \tag{5.12}
\]

with an explicit integral constant \(B_K\).  Repeating the quantitative
Riemann-sum argument behind the Stage VIII boundary theorem gives the
conservative fixed-\(K\) form-level budget

\[
 \boxed{
 \mathcal E_{\partial}
 =\sqrt t+h+\frac{h^2+\sigma_h^2}{t}
 +B_K'|\kappa_h-\kappa|.}
 \tag{5.13}
\]

The best atlas comparison normally takes the continuum parameter to be the
*actual* \(\kappa_h\).  Since the Stage X full-atlas floor is uniform in
\(\kappa\), this makes the coordinate term in (5.13) exactly zero.  If the
goal is convergence to one preassigned \(\kappa\), cell placement generally
adds \(|\kappa_h-\kappa|=O(h/\sqrt t)\).

The interior common-window inequality must not be substituted for (5.13):
the reflecting cosine multiplier is not positive semidefinite uniformly in
\(\kappa\).

### 5.4 Finite sensors

Let \(\mathcal A_{0,K,c}\) be the pre-sensor normalized response and let
\(P_M\) be an orthogonal projection in its whitened output space.  Then the
lost Gram and its norm are

\[
 \boxed{
 G_{K,c}-G_{K,c}^{(M)}
 =\mathcal A_{0,K,c}^*(I-P_M)\mathcal A_{0,K,c},
 \qquad
 \delta_{\rm sens}
 =\|G_{K,c}-G_{K,c}^{(M)}\|
 =\|(I-P_M)\mathcal A_{0,K,c}\|^2.}
 \tag{5.14}
\]

For a nonorthogonal sensor/reconstruction frame, replace \(P_M\) by the
actual analysis/synthesis operator and certify both frame bounds.  If only
\(M<K\) scalar outputs are retained, the finite Gram has rank at most \(M\).
It follows contrapositively from (1.2) that

\[
 \boxed{M<K\quad\Longrightarrow\quad\delta_{\rm sens}\ge L_K}
 \tag{5.15}
\]

for any \(K\)-dimensional continuum Gram with floor \(L_K\).  No mesh
refinement can cure this rank obstruction.

---

## 6. The early calibrated chart

The early endpoint is the only chart where ordinary consistency estimates
can be magnified by powers of a vanishing chart coordinate.

### 6.1 Pure moment leakage

Let \(e_1,\ldots,e_K\) be an \(L^2\)-orthonormal moment-adapted basis with

\[
 \langle V^j,e_i\rangle=0\quad(0\le j<i),
 \qquad
 p_i=\langle V^i,e_i\rangle\ne0.
 \tag{6.1}
\]

The calibrated source matrix is

\[
 D_K(q)=\operatorname{diag}(q,q^2,\ldots,q^K).
 \tag{6.2}
\]

For midpoint injection define

\[
 m_{j,h}(e_i)=h\sum_rV(x_r)^je_i(x_r).
\]

Every sampled nonconstant cosine has exactly zero discrete mean when
\(K<n\), so \(m_{0,h}(e_i)=0\) exactly.  By (5.3),

\[
 |m_{j,h}(e_i)-m_j(e_i)|
 \le h^2H_{j,i},
 \qquad
 H_{j,i}=\frac12\|(V^je_i)''\|_{L^1}.
 \tag{6.3}
\]

Hence, for \(0<q\le q_0<1\), the calibrated pure-moment defect satisfies

\[
 \boxed{
 \Delta_{K,h}(q)
 \le h^2H_K
 \left(1+\frac{q^{1-K}}{1-q}\right),}
 \tag{6.4}
\]

where \(H_K=\max_{i\le K,j\le i}H_{j,i}\), with harmless finite factors
absorbed into \(H_K\).  The important term is \(h^2q^{1-K}\).  Thus even a
second-order quadrature defect can overwhelm the deepest calibrated port.

A moment-fitted injection can set the lower discrete moments to zero for
fixed \(K\).  That operation is not free: its fitting matrix must be
interval-inverted, its condition number must be bounded, and the transformed
source cost \(S_{K,h}\) must either be retained or controlled by (3.7).

### 6.2 Mixed causal words are genuinely independent

Pure moment fitting does not control the noncommutative words generated by
\(A\) and \(V\).  This is already exact at \(K=3\).

For \(V=1+4x/5\), set

\[
 e_3=\phi_3-\frac19\phi_1.
 \tag{6.5}
\]

Direct integration gives

\[
 \langle V,e_3\rangle=\langle V^2,e_3\rangle=0,
 \qquad
 \langle V^3,e_3\rangle
 =-\frac{2048\sqrt2}{3375\pi^4},
 \tag{6.6}
\]

but, for the positive Neumann Laplacian \(A\phi_k=(k\pi)^2\phi_k\),

\[
 \boxed{
 \langle V,Ae_3\rangle=-\frac{64\sqrt2}{45}\ne0.}
 \tag{6.7}
\]

Indeed the second Taylor coefficient of

\[
 \langle1,e^{-t(A+\mu V)}e_3\rangle
\]

contains

\[
 \frac{t^2\mu}{2}\langle V,Ae_3\rangle,
 \tag{6.8}
\]

whereas the first pure-multiplication term is of order
\((t\mu)^3=q^3s_0^3\).  After \(q^{-3}\) calibration, (6.8) has relative
size \(t/q^2\).  This proves that cancellation of the moments in (6.6)
does not certify the finite causal flag.

Nor is \(\|A\|_{E_K}\) alone a complete all-orders control.  Multiplication
by \(V\) sends \(E_K\) outside \(E_K\), and later occurrences of \(A\) act on
that \(V\)-cyclic closure.  A rigorous certificate must use either

1. a validated enclosure of the *complete calibrated mixed remainder*,
   defined below; or
2. graph/weak-form bounds on every required \(A\)-\(V\) cyclic word,
   including their boundary-domain terms.

Define the exact finite mixed remainder by

\[
 \boxed{
 \eta_{\rm word}
 =\left\|
 J_hW_h^{1/2}
 \left(R_h^{A+\mu V}-R_h^{\mu V}\right)
 I_hC_KD_K(q)^{-1}S_K^{-1/2}
 \right\|.}
 \tag{6.9}
\]

Since every matrix in (6.9) is finite, interval matrix exponentials or
validated exponential actions give a proof without truncating the causal
series.  If a word expansion is used instead, its tail must be enclosed.

The Stage IX safe fixed-band shape can now be stated without concealing this
requirement:

\[
 \boxed{
 \delta_{K}^{\rm early}
 \le C_K\left[
 (h/\varepsilon)^2+\varepsilon^2
 +\frac{t\,\mathfrak C_{K,h}}{q^{K-1}}
 +\Delta_{K,h}(q)
 +\mathcal E_{\rm prep}+\mathcal E_{\rm bdry}
 \right].}
 \tag{6.10}
\]

Here \(\mathfrak C_{K,h}\) is a *certified calibrated weak causal-word
constant*, not merely \(\|A\|_{E_K}\).  For the cosine band its leading
one-\(A\) part is bounded on fixed \(K\) by \(O(K^2)\), but all higher words
and the Taylor tail remain part of the certificate.  Replacing
\(\mathfrak C_{K,h}\) by \(K^2\) without that verification is an unproved
growing-band assertion.

If the finite response is compared with the continuum calibrated Gram at
the *same positive* \(q\), (6.10) contains no intrinsic \(q\) consistency
term.  If it is instead compared directly with the endpoint \(q=0\) Gram,
analytic continuation adds \(C_Kq\).  This distinction removes an avoidable
loss from same-parameter transfer while retaining the correct endpoint
condition.

### 6.3 A sufficient early path

For a transparent fixed-\(K\) path with \(K\ge2\), take

\[
 \boxed{
 \varepsilon=h^{1-1/K},
 \qquad q=h^{2/K},
 \qquad t=q\varepsilon^2=h^2.}
 \tag{6.11}
\]

Then

\[
 (h/\varepsilon)^2=q=h^{2/K},
\]

and

\[
 \frac{tK^2}{q^{K-1}}=K^2h^{2/K},
 \qquad
 h^2q^{1-K}=h^{2/K}.
 \tag{6.12}
\]

Consequently, whenever the full mixed-word certificate satisfies
\(\mathfrak C_{K,h}\le C_K'K^2\) along this path,

\[
 \boxed{
 \delta_K^{\rm early}
 \le\widetilde C_KK^2h^{2/K}.}
 \tag{6.13}
\]

The constants contain the moment-basis conditioning and must not be assumed
uniform in \(K\).  For \(K=2\), (6.11) is
\(\varepsilon=\sqrt h,q=h,t=h^2\), and the safe rate is \(O(h)\).

An exactly moment-fitted injection removes (6.4), but not (6.7)--(6.9).

---

## 7. Fixed-\(K\) transfer theorem

### Theorem 7.1 — complete fixed-band sufficient criterion

Fix one of the constant-rank Stage X strata and its declared source and
output metrics.  Assume:

1. the continuum generalized Gram has a certified floor \(L_K>0\);
2. the finite and continuum outputs are related by an explicit bridge
   \(J_{h,c}\);
3. exact analytic nulls have been quotiented before numerical work;
4. every term in (4.2), including the complete calibrated remainder (6.9),
   has an outward-rounded bound;
5. any metric change satisfies (3.7); and
6. a finite sensor map has a certified frame/tail bound and at least \(K\)
   scalar outputs.

If either

\[
 \sum_j\eta_j<\sqrt{L_K}
 \tag{7.1}
\]

or a direct Gram computation proves

\[
 \sum_j\delta_j<L_K,
 \tag{7.2}
\]

then the finite model has no additional null on the declared \(K\)-port
quotient.  More precisely, (3.3) applies under (7.1), and (3.8) applies
under (7.2).

For every fixed \(K\), the following chart paths make the regular
Stage VIII--IX terms vanish:

| chart | one safe choice | conservative error scale |
|---|---|---|
| balanced resolved, \(q\) in a fixed compact subset of \((0,\infty)\) | \(\varepsilon=\sqrt h,\ t=q h\) | \(O_K(h)\) |
| fixed finite-cell lattice | exact fixed \(Q\), \(t=\tau h^2\) | \(O_K(h)\) |
| smooth atomic interior | \(\varepsilon=O(h),\ t=h\) | \(O_K(h)\) |
| atomic boundary atlas | compare at actual \(\kappa_h\), \(\sigma_h=O(h),\ t=h^{4/3}\) | \(O_K(h^{2/3})\) |
| calibrated early endpoint path | (6.11) | \(O_K(h^{2/K})\) |

The table is a sufficient asymptotic guide, not a numerical certificate:
the constants must be enclosed before comparison with \(L_K\).  The generic
finite-cell bound is only first order even though the canonical midpoint
laboratory often displays second-order residuals.

### Corollary 7.2 — continuum full-atlas transfer budget

For \(K=2\), use the Stage X full-atlas lower certificate \(L_2=10^{-19}\).
If the actual outward-rounded calculation proves

\[
 \delta_2(h)<10^{-19},
\]

then the finite two-port Gram is positive definite over the complete
declared atlas.  If a common-space response calculation is used instead,
it is enough to prove

\[
 \eta_2(h)<3.162277660\times10^{-10}.
\]

On the early path \(\varepsilon=\sqrt h,q=h,t=h^2\), a bound
\(\delta_2(h)\le C_2h\) therefore closes whenever

\[
 \boxed{h<10^{-19}/C_2.}
 \tag{7.3}
\]

This is a rigorous sufficient inequality once \(C_2\) is certified.  It is
not presented as a practical grid recommendation.

---

## 8. Numerical budgets supplied by Stage X

For the standard-Gaussian resolved \(q\ge1\), one-cell lattice
\(\tau\ge1\), and interior atomic common-window charts, Stage X certified
the following rounded lower bounds.  The last two columns are the maximum
response-operator errors allowed by the simple strict test
\(\eta_K<\sqrt{L_K}\).

| \(K\) | \(L_K\), raw \(L^2\) | \(\sqrt{L_K}\) | \(L_K\), continuum \(H^1\) | \(\sqrt{L_K}\) |
|---:|---:|---:|---:|---:|
| 1 | \(1.31065\times10^{-4}\) | \(1.14484\times10^{-2}\) | \(1.20579\times10^{-5}\) | \(3.47245\times10^{-3}\) |
| 2 | \(1.43152\times10^{-7}\) | \(3.78354\times10^{-4}\) | \(3.55231\times10^{-9}\) | \(5.96013\times10^{-5}\) |
| 3 | \(1.77650\times10^{-10}\) | \(1.33285\times10^{-5}\) | \(2.01796\times10^{-12}\) | \(1.42055\times10^{-6}\) |
| 4 | \(2.23908\times10^{-13}\) | \(4.73189\times10^{-7}\) | \(1.48943\times10^{-15}\) | \(3.85931\times10^{-8}\) |
| 5 | \(2.72483\times10^{-16}\) | \(1.65071\times10^{-8}\) | \(1.21070\times10^{-18}\) | \(1.10032\times10^{-9}\) |
| 6 | \(2.41218\times10^{-19}\) | \(4.91139\times10^{-10}\) | \(7.73921\times10^{-22}\) | \(2.78194\times10^{-11}\) |
| 7 | \(1.53496\times10^{-22}\) | \(1.23893\times10^{-11}\) | \(3.74302\times10^{-25}\) | \(6.11802\times10^{-13}\) |
| 8 | \(7.36997\times10^{-26}\) | \(2.71477\times10^{-13}\) | \(1.41495\times10^{-28}\) | \(1.18951\times10^{-14}\) |

These decimals are explanatory summaries.  A proof-producing program must
read the exact rational Stage X lower certificates.

If the conservative direct-Gram estimate (5.5) is used, the natural
dimensionless target is

\[
 \boxed{
 \mathcal E_c<\frac{L_K}{C_c(1+K^2)^3}.}
 \tag{8.1}
\]

For orientation, the factors \(L_K/(1+K^2)^3\), before division by the
unknown certified chart constant \(C_c\), are

| \(K\) | raw \(L^2\) | continuum \(H^1\) |
|---:|---:|---:|
| 1 | \(1.63831\times10^{-5}\) | \(1.50724\times10^{-6}\) |
| 2 | \(1.14522\times10^{-9}\) | \(2.84185\times10^{-11}\) |
| 3 | \(1.77650\times10^{-13}\) | \(2.01796\times10^{-15}\) |
| 4 | \(4.55746\times10^{-17}\) | \(3.03161\times10^{-19}\) |
| 5 | \(1.55031\times10^{-20}\) | \(6.88837\times10^{-23}\) |
| 6 | \(4.76217\times10^{-24}\) | \(1.52789\times10^{-26}\) |
| 7 | \(1.22797\times10^{-27}\) | \(2.99442\times10^{-30}\) |
| 8 | \(2.68365\times10^{-31}\) | \(5.15230\times10^{-34}\) |

This table explains why an asymptotic convergence plot is not yet a transfer
certificate.  At \(K=8\), a perfectly respectable \(10^{-16}\) residual is
still enormously larger than the certified floor.

---

## 9. Growing-band consequences

### 9.1 What is proved for the common late core

The Stage X separated-frame theorem supplies an explicit common-core lower
bound of the form

\[
 L_K^{\rm core}\ge e^{-C_0K^2}
 \tag{9.1}
\]

for fixed modulation and truncation window.  Suppose, in addition, that a
validated family of finite-model estimates proves

\[
 \delta_K\le C_1K^a h^p
 \tag{9.2}
\]

with constants uniform along the declared late-chart path.  Then

\[
 C_1K^ah^pe^{C_0K^2}\longrightarrow0
 \tag{9.3}
\]

is sufficient for relative Gram transfer on that common core.  In
particular,

\[
 \boxed{K=o(\sqrt{\log(1/h)})}
 \tag{9.4}
\]

is sufficient when \(p>0\) is fixed and the omitted constants grow only
subexponentially in \(K^2\).  The geometric restrictions in (5.9) must also
hold.

Equation (9.4) is conditional on the uniform error estimate (9.2); fixed-\(K\)
big-\(O\) notation does not prove it.

### 9.2 The early path is more restrictive

On the early path (6.11), assume the moment and complete mixed-word constants
obey

\[
 \log\widetilde C_K=o(K^2)
\]

and assume a relevant continuum lower bound \(L_K\ge e^{-C_0K^2}\).  Then

\[
 \widetilde C_KK^2h^{2/K}e^{C_0K^2}\to0
\]

whenever

\[
 \boxed{K=o((\log(1/h))^{1/3}).}
 \tag{9.5}
\]

This is a conditional scaling consequence, not a completed full-atlas
theorem.  At present there is no all-\(K\) certified early-plus-boundary atlas
lower bound and no uniform enclosure of the causal constant in (6.9).

### 9.3 A necessary warning from the factorial ceiling

At a fixed one-cell lattice time, Stage X proved

\[
 \gamma_K\le
 A^2\frac{c^{2K}}{(K!)^2}.
 \tag{9.6}
\]

Therefore actual relative transfer \(\delta_K=o(\gamma_K)\) necessarily
requires

\[
 \delta_K=o\!\left(\frac{c^{2K}}{(K!)^2}\right).
 \tag{9.7}
\]

If an actual scheme has a nonvanishing error of algebraic order \(h^p\),
(9.7) forces, at minimum, a scale comparable to

\[
 K\log K=o(\log(1/h)).
 \tag{9.8}
\]

This does not contradict the sufficient lower-bound schedules (9.4)--(9.5):
the proven lower and upper spectral asymptotics do not match.  It does rule
out inferring growing-band stability from \(Kh\to0\) alone.

---

## 10. Calibration, whitening, and noise

The early calibrated Gram

\[
 D_K(q)^{-1}\Gamma_qD_K(q)^{-1}
\]

can equivalently be represented by the raw pair

\[
 (\Gamma_q,D_K(q)^2).
\]

The latter makes the physical cost explicit: a unit deepest calibrated
coordinate costs \(q^{-K}\) in raw source amplitude.  Using
\(D_K(q)^{-1}\) with an identity coordinate metric is valid for the declared
*calibrated* experiment, but it is not the raw fixed-amplitude experiment.
A finite comparison must use the same one of these two interpretations as
the continuum certificate.

Likewise, output whitening \(W=\Sigma^{-1}\) is part of the experiment.  If
the finite noise covariance is \(\Sigma_h\), the correct normalized operator
uses \(\Sigma_h^{-1/2}\), and the whitening change belongs in
\(\eta_{\rm white}\).  A deterministic Gram error computed in an unweighted
Euclidean output does not certify a noise-whitened spectrum.

Once a finite lower floor \(\underline\gamma_{K,h}>0\) is certified, the
Stage X Gaussian repetition bound applies with that floor.  Transfer alone
does not specify amplitude, false-alarm level, unknown background, or sensor
noise covariance.  Conversely, adding repetitions reduces statistical
noise but does not repair a deterministic rank loss from \(M<K\) sensors.

---

## 11. Impossibility boundaries

The following tempting statements are false or presently unproved.

| Tempting statement | Correct boundary |
|---|---|
| \(\|G_h-G\|\to0\) transfers a generalized spectrum | only the declared metric-normalized error, or a direct pair certificate, does |
| a response error below \(L_K\) is required | the sharp response threshold is \(\sqrt{L_K}\); the Gram threshold is \(L_K\) |
| midpoint quadrature is second order, so early calibration is safe | its \(O(h^2)\) lower moments become \(O(h^2q^{1-K})\) |
| exact moment fitting proves the causal flag | the exact counterexample (6.5)--(6.8) has a nonzero mixed word |
| \(\|A\|_{E_K}\asymp K^2\) controls all mixed words | \(V\) leaves \(E_K\); use the full calibrated remainder or the \(V\)-cyclic weak/graph bounds |
| comparing a finite boundary target with one fixed \(\kappa\) is automatic | cell placement contributes \(O(h/\sqrt t)\) unless the continuum comparison uses the actual \(\kappa_h\) |
| weak convergence of target preparations selects the lattice chart | a fixed-\(\tau\) chart retains the complete local profile \(Q\) |
| \(M\ge K\) sensors prove transfer | it is necessary, not sufficient; the sensor frame floor must be certified |
| the \(K\le8\) late table is a complete-atlas certificate | complete early and boundary coverage is currently certified only for \(K=2\) |
| a fixed-\(K\) \(O_K(h^p)\) estimate gives a growing-band theorem | the \(K\)-dependence must beat the shrinking continuum floor |
| mesh refinement compensates for changed source or noise costs | costs and whitening define a different generalized spectrum |

There is also no uniform-in-\(q\downarrow0\) theorem for a naively injected,
pure-moment-calibrated growing band.  Either a lower path cutoff \(q\ge
q_{\min}(h,K)\), an exactly fitted finite causal filtration, or a validated
endpoint finite model must be declared.

---

## 12. Proof-producing certification protocol

A finite transfer certificate should record the following objects.

1. The exact source quotient, basis, calibration, and source metric.
2. The exact finite injection and its metric Gram \(S_{K,h}\).
3. The target deposition rule, including normalization and boundary tail.
4. The finite boundary coordinate \(\kappa_h\) and the continuum parameter
   against which it is compared.
5. The finite output/sensor map, output whitening, and common-space bridge.
6. Outward-rounded bounds for every telescoping term in (4.2).
7. In the early chart, the discrete moment table and the full mixed
   remainder (6.9), including any exponential-series tail.
8. The exact rational Stage X floor \(L_K\), not its printed decimal.
9. Either the response inequality (7.1), the Gram inequality (7.2), or
   direct verified definiteness of \(G_{K,h,c}-\ell S_{K,h}\).
10. The resulting finite floor and any effective-rank/noise statement made
    from it.

The strongest practical route is usually hybrid.  Analytic envelopes remove
infinite modal and boundary tails; interval matrix-exponential actions bound
the finite mixed-word core; direct interval inertia avoids converting every
local error into one pessimistic operator norm.

---

## 13. What is now proved, and what remains

This memo closes the abstract finite-transfer theorem:

1. normalized response error below \(\sqrt{L_K}\) preserves the continuum
   floor with the sharp bound (3.3);
2. metric-relative Gram error below \(L_K\) gives (3.6), and a changed source
   metric is handled by (3.8);
3. the physical errors admit the exact telescoping decomposition (4.2);
4. midpoint moment leakage is explicitly \(O(h^2q^{1-K})\);
5. an exact canonical three-port calculation proves that mixed causal words
   are independent of pure moment fitting;
6. the complete mixed remainder (6.9) is a finite, interval-certifiable
   object;
7. the Stage X floors give explicit finite response and Gram budgets; and
8. conditional late- and early-bandwidth schedules follow from the proven
   continuum lower bounds.

The companion Stage XI computation already gives the first actual finite
path-grid crossing: complete finite Neumann dynamics at the one-cell lattice
point \(\tau=1\), \(K=1\), \(n=7\), in both declared \(L^2\) and continuum
\(H^1\) source metrics.  It separately certifies phase-grid quadrature
transfer through \(K=8\).  The next computational theorem is more ambitious:
extend the complete finite dynamics to \(K=2\), then prove either (1.4) or
(1.5) on a finite cover of the same full atlas used by the Stage X continuum
certificate.  The present memo supplies that proof contract; it does not
claim that the \(K=2\) atlas inequality has already been closed.
