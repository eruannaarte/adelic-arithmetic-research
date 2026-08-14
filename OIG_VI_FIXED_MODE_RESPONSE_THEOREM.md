# Operational Information Geometry VI

## A fixed-mode discrete-to-continuum response theorem

- **Research lane:** analytic closure of Stage V Hypothesis 6.1
- **Date:** 14 August 2026
- **Status:** proof memo plus an independent continuum-reference computation;
  not peer reviewed
- **Laboratory:** oig_vi_fixed_mode_convergence.py
- **Tests:** test_oig_vi_fixed_mode_convergence.py

## 1. Result in one paragraph

For the cell-centred Neumann path, the finite one-way response has a genuine
continuum limit once source and output channels are fixed in physical modes and
probability masses are converted to density units. For every fixed number of
source cosine modes, every fixed number of target cosine sensors, and every
compact time interval

\[
 0<t_0\le t\le T<\infty,
\]

the density-normalized response matrix converges uniformly to the response of

\[
 K_\ell=-\partial_x^2+(\ell\pi)^2(1+g d(x))
\]

with Neumann boundary conditions. Continuous bounded modulation is enough for
plain convergence by generalized Mosco convergence. If
\(d\in W^{2,\infty}(0,1)\), the target density is \(C^2\), and
\(1+gd\) stays strictly positive, the finite response matrix and every fixed
protocol Gram converge at rate \(O(n^{-2})\). The linear ramp \(d(x)=x\) used
in Stage V satisfies these hypotheses. Thus the specific fixed-five-source,
single-target-mode Stage V convergence claim is promoted from a numerical
hypothesis to a theorem.

The theorem is deliberately about fixed physical modes. It does not give an
\(O(n^{-2})\) approximation of the entire output density under a
piecewise-constant embedding, nor is it uniform as \(t_0\downarrow0\), in a
growing number of modes, or for atomic target preparations.

## 2. Density Hilbert spaces and the two reconstructions

Put \(h=1/n\), let

\[
 C_j=[jh,(j+1)h),\qquad x_j=(j+1/2)h,
 \qquad 0\le j<n,
\]

and equip

\[
 H_h=\mathbb R^n
\]

with the density inner product

\[
 \langle v,w\rangle_h
 =h\sum_{j=0}^{n-1}v_jw_j.
\]

This is the correct physical metric for density samples. A density \(f\)
corresponds to cell probability masses \(h f(x_j)\).

Two reconstructions have different jobs.

### 2.1 Piecewise-constant isometry

Define

\[
 (J_hv)(x)=v_j,\qquad x\in C_j.
\]

Then

\[
 \|J_hv\|_{L^2}=\|v\|_h.
\]

Its adjoint is cell averaging:

\[
 (P_hf)_j=\frac1h\int_{C_j}f(x)\,dx.
\]

Thus \(P_hJ_h=I_{H_h}\), while \(J_hP_h\) is the orthogonal projection onto
cellwise constants.

This is the right pair for generalized strong and weak convergence of the
Hilbert spaces.

### 2.2 Piecewise-linear energy reconstruction

Let \(I_hv\) be linear between consecutive cell centres and constant on the two
boundary half-cells:

\[
 I_hv=v_0\ \hbox{on }[0,h/2],\qquad
 I_hv=v_{n-1}\ \hbox{on }[1-h/2,1].
\]

Direct integration gives

\[
 \int_0^1 I_hv\,dx=h\sum_jv_j
\]

and

\[
 \int_0^1 |(I_hv)'|^2dx
 =\frac1h\sum_{j=0}^{n-2}(v_{j+1}-v_j)^2.
\]

Moreover,

\[
 \|I_hv-J_hv\|_{L^2}^2
 \le C h^2
 \frac1h\sum_{j=0}^{n-2}(v_{j+1}-v_j)^2.
\]

The first reconstruction preserves the discrete density norm exactly; the
second represents the discrete Dirichlet energy exactly. Their difference
vanishes whenever the energies stay bounded.

## 3. Neumann modes and physical ports

Let

\[
 \phi_0(x)=1,\qquad
 \phi_k(x)=\sqrt2\cos(k\pi x),\quad k\ge1.
\]

Their cell-centre samples

\[
 \phi_{k,h}(j)=\phi_k(x_j)
\]

satisfy the exact discrete orthogonality law

\[
 \langle\phi_{k,h},\phi_{m,h}\rangle_h=\delta_{km},
 \qquad 0\le k,m<n.
\]

For the cell-centred path operator \(A_h=h^{-2}L_n\),

\[
 A_h\phi_{k,h}=\mu_{k,h}\phi_{k,h},
\qquad
 \mu_{k,h}=4h^{-2}\sin^2(k\pi h/2).
\]

For each fixed \(k\),

\[
 0\le(k\pi)^2-\mu_{k,h}
 \le\frac{(k\pi)^4}{12}h^2.
\]

Fix source modes \(1\le k\le K\). A unit continuum density perturbation
\(\phi_k\) is injected in the finite probability simplex as

\[
 h\phi_{k,h}.
\]

This mass vector has zero total mass; after division by \(h\), its associated
density sample \(\phi_{k,h}\) has \(\|\phi_{k,h}\|_h=1\). Fix target modes
\(1\le\ell\le L\). The target output is the coefficient in the orthonormal
density mode \(\phi_\ell\); its Euclidean coefficient metric is therefore
already the whitened \(L^2\) output metric.

## 4. Continuum and discrete reduced generators

Let \(d:[0,1]\to\mathbb R\), \(g\ge0\), and put

\[
 v(x)=1+g d(x).
\]

Assume throughout that

\[
 0<v_-\le v(x)\le v_+<\infty.
\]

Let \(A=-\partial_x^2\) be the nonnegative Neumann Laplacian. For target mode
\(\ell\), define

\[
 \nu_\ell=(\ell\pi)^2,\qquad
 K_\ell=A+\nu_\ell M_v.
\]

Its closed quadratic form on \(H^1(0,1)\) is

\[
 \mathcal E_\ell(u)
 =\int_0^1|u'|^2dx
  +\nu_\ell\int_0^1v|u|^2dx.
\]

On the grid, sample \(v_{h,j}=v(x_j)\) and define

\[
 K_{\ell,h}
 =A_h+\mu_{\ell,h}\operatorname{diag}(v_{h,0},\ldots,v_{h,n-1}).
\]

Its form is

\[
 \mathcal E_{\ell,h}(z)
 =\frac1h\sum_{j=0}^{n-2}(z_{j+1}-z_j)^2
  +\mu_{\ell,h}h\sum_{j=0}^{n-1}v(x_j)|z_j|^2.
\]

These are exactly the target-mode blocks obtained from the joint generator

\[
 G_h=A_h\otimes I+(I+gD_h)\otimes A_h.
\]

No approximation is used in this reduction.

## 5. Background normalization and the response matrices

Let \(\rho\) be a positive target density with

\[
 \int_0^1\rho(y)\,dy=1.
\]

Write

\[
 \beta_\ell=\langle\phi_\ell,\rho\rangle_{L^2}.
\]

For a sampled probability preparation, define

\[
 Z_h=h\sum_j\rho(x_j),\qquad
 \rho_{h,j}=\frac{\rho(x_j)}{Z_h},\qquad
 q_{h,j}=h\rho_{h,j}.
\]

Then \(\sum_jq_{h,j}=1\). Its discrete target coefficient is

\[
 \beta_{\ell,h}
 =\langle\phi_{\ell,h},\rho_h\rangle_h.
\]

The continuum fixed-mode response matrix is

\[
 R_{\ell k}(t)
 =\beta_\ell
 \left\langle 1,e^{-tK_\ell}\phi_k\right\rangle_{L^2},
 \qquad
 1\le\ell\le L,\quad1\le k\le K.
\]

The density-normalized discrete response is

\[
 R_{\ell k}^{(h)}(t)
 =\beta_{\ell,h}
 \left\langle 1,e^{-tK_{\ell,h}}\phi_{k,h}\right\rangle_h.
\]

To verify the normalization, start with joint probability perturbation

\[
 (h\phi_{k,h})\otimes(h\rho_h).
\]

After evolution, sum over the source coordinate, divide the target marginal
mass by \(h\), and pair with \(\phi_{\ell,h}\) in the \(h\)-weighted metric.
The displayed formula is exactly what remains. It is also the normalization
implemented in Operational Information Geometry V.

The stationary target row is absent: for \(\ell=0\),

\[
 \langle1,e^{-tA}\phi_k\rangle
 =\langle1,\phi_k\rangle=0,
\]

and the same identity holds exactly on every grid.

## 6. Plain convergence by Mosco convergence

### Theorem 6.1 — reduced forms and semigroups converge

Assume only that \(v\) is continuous and satisfies
\(0<v_-\le v\le v_+\). For each fixed target mode \(\ell\),
\(\mathcal E_{\ell,h}\) Mosco-converges to \(\mathcal E_\ell\) under the
varying-space identification \(J_h,P_h\). Consequently, for every
\(f\in L^2(0,1)\),

\[
 J_he^{-tK_{\ell,h}}P_hf
 \longrightarrow e^{-tK_\ell}f
\]

strongly in \(L^2\), uniformly for \(t\) in every compact interval in
\([0,\infty)\).

#### Proof

**Liminf.** Suppose \(J_hz_h\rightharpoonup u\) weakly in \(L^2\) and

\[
 \sup_h\left(\|z_h\|_h^2+\mathcal E_{\ell,h}(z_h)\right)<\infty.
\]

The energy identity makes \(I_hz_h\) bounded in \(H^1(0,1)\). The estimate
between \(I_h\) and \(J_h\) shows that they have the same weak limit. After a
subsequence,

\[
 I_hz_h\rightharpoonup u\quad\hbox{in }H^1,
\qquad
 I_hz_h\to u\quad\hbox{in }L^2.
\]

Weak lower semicontinuity gives

\[
 \int|u'|^2
 \le\liminf_h\frac1h\sum_j(z_{h,j+1}-z_{h,j})^2.
\]

Because \(v_h=J_h(v(x_0),\ldots,v(x_{n-1}))\) converges uniformly to \(v\),
because \(\mu_{\ell,h}\to\nu_\ell\), and because
\(J_hz_h\to u\) strongly in \(L^2\), the potential terms converge:

\[
 \mu_{\ell,h}h\sum_jv(x_j)|z_{h,j}|^2
 \longrightarrow
 \nu_\ell\int v|u|^2.
\]

This proves the Mosco liminf inequality.

**Recovery.** First take \(u\in C^\infty[0,1]\) and set \(z_{h,j}=u(x_j)\).
Midpoint Riemann sums and difference quotients give

\[
 \|J_hz_h-u\|_{L^2}\to0,
\qquad
 \mathcal E_{\ell,h}(z_h)\to\mathcal E_\ell(u).
\]

Smooth functions are dense in \(H^1(0,1)\). A diagonal approximation supplies
a recovery sequence for every \(u\in H^1\).

The equivalence between generalized Mosco convergence and strong convergence
of the associated resolvents and symmetric contraction semigroups now applies.
Strong semigroup convergence is locally uniform in time by the contraction
property and the Trotter--Kato argument. This proves the theorem.
\(\square\)

The varying-Hilbert-space equivalence used in the last step is the framework
of Kuwae and Shioya, “Convergence of spectral structures: a functional
analytic theory and its applications to spectral geometry,”
Communications in Analysis and Geometry 11 (2003), 599--673,
https://doi.org/10.4310/cag.2003.v11.n4.a1.

### Corollary 6.2 — fixed-mode response convergence

Let \(K,L\) be fixed, let \(\rho\) be continuous and positive, and let
\(R^{(h)},R\) be the matrices above. Then, for every \(T<\infty\),

\[
 \sup_{0\le t\le T}
 \|R^{(h)}(t)-R(t)\|_{\mathbb R^K\to\mathbb R^L}
 \longrightarrow0.
\]

#### Proof

The sampled source \(\phi_{k,h}\) and the cell average \(P_h\phi_k\) have the
same strong limit \(\phi_k\). Theorem 6.1 therefore gives convergence of each
semigroup matrix element. Midpoint Riemann sums give
\(\beta_{\ell,h}\to\beta_\ell\). There are only \(KL\) entries, so entrywise
uniform convergence is equivalent to matrix operator-norm convergence.
\(\square\)

This theorem includes \(t=0\). Both response matrices are exactly zero there.
It is a convergence theorem, not yet a rate theorem.

## 7. The quantitative cell-centred lemma

The second-order rate rests on the following one-dimensional mass-lumped
finite-element estimate.

### Lemma 7.1 — fixed-reaction semigroup error

Let \(v\in W^{2,\infty}(0,1)\) with \(v\ge v_->0\), fix
\(\lambda\ge0\), and let

\[
 K=A+\lambda M_v.
\]

Let \(K_h=A_h+\lambda\operatorname{diag}(v(x_j))\). If
\(f\) belongs to a fixed finite-dimensional subspace of smooth Neumann
functions, then for every \(0<t_0<T<\infty\),

\[
 \sup_{t_0\le t\le T}
 \left\|
 I_he^{-tK_h}S_hf-e^{-tK}f
 \right\|_{L^2}
 \le C h^2.
\]

Here \(S_hf=(f(x_0),\ldots,f(x_{n-1}))\), and \(C\) may depend on
\(t_0,T,\lambda,v\), and the fixed source space, but not on \(h\).

#### Proof

The discrete scheme is the lumped-mass piecewise-linear method on the
cell-centred mesh, with constant reconstruction on the boundary half-cells.
Indeed its stiffness form is exactly

\[
 \int (I_hz)'(I_hw)'
 =\frac1h\sum_j(z_{j+1}-z_j)(w_{j+1}-w_j),
\]

and its lumped mass and reaction forms are

\[
 m_h(z,w)=h\sum_jz_jw_j,
\qquad
 b_h(z,w)=h\sum_jv(x_j)z_jw_j.
\]

For the quantitative argument, introduce the lumped load projection

\[
 Q_h:L^2(0,1)\longrightarrow H_h,
 \qquad
 m_h(Q_hf,z)=\langle f,I_hz\rangle_{L^2}
 \quad(z\in H_h).
\]

This is not the cell-average map \(P_h=J_h^*\). The latter is the natural
comparison map in the Mosco theorem; \(Q_h\) is the load map for which the
finite-element variational equation has the exact continuum right-hand side.
Conflating the two maps would leave an unjustified step in the quantitative
estimate.

On this shape-regular one-dimensional mesh, direct elementwise Taylor
expansion gives, for \(u\in H^2(0,1)\) satisfying the Neumann endpoint
conditions, the approximation estimate

\[
 \inf_z
 \left(
 \|u-I_hz\|_{L^2}
 +h\|u-I_hz\|_{H^1}
 \right)
 \le C h^2\|u\|_{H^2},
\]

and, for arbitrary discrete \(z,w\), the quadrature estimates

\[
 \left|
 m_h(z,w)-\langle I_hz,I_hw\rangle
 \right|
 \le C h^2\|I_hz\|_{H^1}\|I_hw\|_{H^1},
\]

and

\[
 \left|
 b_h(z,w)-\langle vI_hz,I_hw\rangle
 \right|
 \le C h^2\|v\|_{W^{2,\infty}}
 \|I_hz\|_{H^1}\|I_hw\|_{H^1}.
\]

For the approximation estimate, the boundary half-cells obey the same bound
because the Neumann solution has zero first derivative at the endpoints. The
boundary contributions to both quadrature formulas satisfy the displayed
global (h^2\|I_hz\|_{H^1}\|I_hw\|_{H^1}) estimate through the
one-dimensional trace inequality. They need not themselves be (O(h^2)) for
arbitrary discrete vectors: the (H^1) norm of a boundary hat grows as the
mesh is refined.

Apply Strang's lemma to the shifted elliptic resolvents

\[
 (z+K)^{-1},\qquad (z+K_h)^{-1}
\]

on a fixed sector avoiding the negative real axis. One-dimensional Neumann
elliptic regularity gives \(H^2\) control of the continuum resolvent. The three
displayed estimates give first-order energy error. In particular, if
\(u_h=(z+K_h)^{-1}Q_hf\), then its discrete equation is exactly

\[
 z\,m_h(u_h,w)+
 \int (I_hu_h)'(I_hw)'
 +\lambda b_h(u_h,w)
 =\langle f,I_hw\rangle
 \qquad(w\in H_h).
\]

Thus there is no load-quadrature remainder. Applying the same estimate to the
dual resolvent problem gives, by the Aubin--Nitsche identity,

\[
 \left\|
 I_h(z+K_h)^{-1}Q_h-(z+K)^{-1}
 \right\|_{L^2\to L^2}
 \le C_\theta h^2
\]

with the standard sectorial decay for large \(|z|\). Insert this estimate into
the Dunford contour representation of the analytic semigroups. The contour
integral yields

\[
 \left\|
 I_he^{-tK_h}Q_hf-e^{-tK}f
 \right\|_{L^2}
 \le C h^2t^{-1}\|f\|_{L^2}.
\]

For a fixed finite-dimensional space of smooth functions satisfying the
Neumann endpoint conditions, an elementwise Taylor expansion gives

\[
 \|S_hf-Q_hf\|_h\le Ch^2\|f\|_{C^2}.
\]

For interior basis functions this is the symmetric hat-function quadrature
estimate. At the two boundary basis functions the first moment is \(O(h)\)
after division by the lumped mass, but \(f'(h/2)=O(h)\) and
\(f'(1-h/2)=O(h)\) because \(f'(0)=f'(1)=0\); hence those entries are also
\(O(h^2)\). The reconstruction is uniformly stable,
\(\|I_hz\|_{L^2}\le C\|z\|_h\), while \(e^{-tK_h}\) is an \(m_h\)-contraction.
Therefore

\[
 \left\|I_he^{-tK_h}(S_h-Q_h)f\right\|_{L^2}
 \le Ch^2\|f\|_{C^2}.
\]

This replaces \(Q_hf\) by \(S_hf\) in the semigroup estimate.
Since \(t\ge t_0\), the factor \(t^{-1}\) is harmless. This proves the lemma.
\(\square\)

The optimal \(L^2\) estimate belongs to the classical theory of lumped-mass
parabolic methods. For background, see C. M. Chen and V. Thomée, “The lumped
mass finite element method for a parabolic problem,” *The ANZIAM Journal* 26
(1985), 329--354, https://doi.org/10.1017/S0334270000004549. That paper treats
a two-dimensional Dirichlet setting; it is not a direct citation for the
present boundary convention. The local argument above records the required
one-dimensional Neumann half-cell specialization explicitly.

### Remark 7.2 — why \(t_0>0\) is declared

For general \(L^2\) initial data, the analytic-semigroup estimate contains
\(h^2/t\). Fixed smooth modes often admit an estimate uniform down to zero
under additional compatibility, and the response itself is exactly zero at
zero. None of that is needed for the Stage V protocol, whose earliest time is
\(0.001\). The quantitative theorem therefore keeps the honest,
standard assumption \(t\ge t_0>0\).

## 8. The second-order response theorem

### Theorem 8.1 — uniform \(O(n^{-2})\) fixed-mode response convergence

Assume:

1. \(d\in W^{2,\infty}(0,1)\);
2. \(v=1+gd\) satisfies \(0<v_-\le v\le v_+\);
3. \(\rho\in C^2[0,1]\), \(\rho>0\), and \(\int\rho=1\);
4. the source count \(K\) and target count \(L\) are fixed; and
5. \(0<t_0<T<\infty\).

Then there are \(C<\infty\) and \(h_0>0\) such that

\[
 \boxed{
 \sup_{t_0\le t\le T}
 \|R^{(h)}(t)-R(t)\|_2
 \le C h^2,\qquad 0<h<h_0.}
\]

#### Proof

Fix \(\ell\le L\). Lemma 7.1 first compares the continuum generator

\[
 A+\nu_\ell M_v
\]

with the grid generator using the same reaction coefficient
\(\nu_\ell\). The actual grid uses \(\mu_{\ell,h}\). The exact path estimate
gives

\[
 |\mu_{\ell,h}-\nu_\ell|
 \le\frac{(\ell\pi)^4}{12}h^2.
\]

Duhamel's identity and contraction of the positive semigroups give, uniformly
for \(0\le t\le T\),

\[
 \left\|
 e^{-t(A_h+\mu_{\ell,h}V_h)}
 -e^{-t(A_h+\nu_\ell V_h)}
 \right\|_{h\to h}
 \le
 T\|v\|_\infty|\mu_{\ell,h}-\nu_\ell|
 \le C_\ell h^2.
\]

Hence, for every \(k\le K\),

\[
 \sup_{t_0\le t\le T}
 \left|
 \langle1,e^{-tK_{\ell,h}}\phi_{k,h}\rangle_h
 -\langle1,e^{-tK_\ell}\phi_k\rangle
 \right|
 \le Ch^2.
\]

Here we used

\[
 \langle1,z\rangle_h=\int_0^1I_hz\,dx,
\]

so the scalar output inherits the \(L^2\) estimate of Lemma 7.1 without an
additional reconstruction error.

The composite midpoint rule gives

\[
 Z_h=1+O(h^2)
\]

and, for each fixed \(\ell\),

\[
 \beta_{\ell,h}=\beta_\ell+O(h^2).
\]

Multiplying the two factors in the response entry preserves the \(O(h^2)\)
error because both semigroups are contractions and \(K,L\) are fixed. Taking
the norm of the resulting finite matrix proves the claim.
\(\square\)

### Corollary 8.2 — histories, Grams, and singular values

Let \(t_1,\ldots,t_m\in[t_0,T]\), let \(w_i\ge0\) be fixed, and form

\[
 \mathcal R_h=
 \begin{bmatrix}
 \sqrt{w_1}R^{(h)}(t_1)\\
 \vdots\\
 \sqrt{w_m}R^{(h)}(t_m)
 \end{bmatrix},
\qquad
 \mathcal R=
 \begin{bmatrix}
 \sqrt{w_1}R(t_1)\\
 \vdots\\
 \sqrt{w_m}R(t_m)
 \end{bmatrix}.
\]

Then

\[
 \|\mathcal R_h-\mathcal R\|_2=O(h^2),
\]

\[
 \|\mathcal R_h^{\mathsf T}\mathcal R_h
      -\mathcal R^{\mathsf T}\mathcal R\|_2
 =O(h^2),
\]

and every singular value of \(\mathcal R_h\) differs from the corresponding
singular value of \(\mathcal R\) by \(O(h^2)\).

#### Proof

The history estimate is a finite stacking of Theorem 8.1. The Gram identity

\[
 X^{\mathsf T}X-Y^{\mathsf T}Y
 =X^{\mathsf T}(X-Y)+(X-Y)^{\mathsf T}Y
\]

and uniform boundedness give the second estimate. Weyl's singular-value
inequality gives the last.
\(\square\)

If the limiting smallest singular value is positive, fixed-mode rank and
condition number are therefore stable for all sufficiently fine grids. This is
a statement about a fixed quotient. It does not stabilize the rank of a
tangent space whose dimension grows with \(n\).

## 9. Exact specialization to the Stage V protocol

Stage V uses

\[
 d(x)=x,\qquad
 g=0.8,\qquad
 \rho(y)=1+0.4\sqrt2\cos(\pi y),
\]

five source modes, the first target mode, and 30 times in
\([0.001,0.5]\). All assumptions of Theorem 8.1 hold:

\[
 d\in W^{2,\infty},\qquad
 1\le1+0.8x\le1.8,
\]

and the target density is smooth and strictly positive.

For this ramp, multiplication by \(x\) has an exact continuum cosine matrix.
If

\[
 I_0=\frac12,\qquad
 I_m=\int_0^1x\cos(m\pi x)\,dx
 =\frac{(-1)^m-1}{(m\pi)^2}\quad(m\ge1),
\]

then

\[
 \langle\phi_0,x\phi_q\rangle=\sqrt2 I_q
\]

and, for \(p,q\ge1\),

\[
 \langle\phi_p,x\phi_q\rangle
 =I_{|p-q|}+I_{p+q}.
\]

The new laboratory diagonalizes the resulting continuum reduced operator
directly. A 128-mode cutoff and a 64-mode cutoff differ by less than
\(2\times10^{-12}\) over the declared response history. This is a truncation
stability audit, not an interval certificate.

The direct continuum comparison is:

| \(n\) | history error | \(n^2\) history error | relative Gram error | \(n^2\) relative Gram error | observed order |
|---:|---:|---:|---:|---:|---:|
| 8 | \(5.92862\times10^{-4}\) | 0.0379432 | \(1.30561\times10^{-2}\) | 0.835593 | -- |
| 16 | \(1.47932\times10^{-4}\) | 0.0378707 | \(3.24597\times10^{-3}\) | 0.830968 | 2.00093 |
| 32 | \(3.69760\times10^{-5}\) | 0.0378635 | \(8.10533\times10^{-4}\) | 0.829986 | 2.00016 |
| 64 | \(9.24363\times10^{-6}\) | 0.0378619 | \(2.02574\times10^{-4}\) | 0.829743 | 2.00004 |
| 128 | \(2.31088\times10^{-6}\) | 0.0378615 | \(5.06398\times10^{-5}\) | 0.829682 | 2.00001 |

The \(n^2\)-scaled errors approach nonzero constants, which is stronger
evidence than comparison with another finite grid: it identifies the leading
second-order discretization term against an independently constructed
continuum operator.

The laboratory also checks a smooth recovery sequence for the quadratic form.
For

\[
 f=1+0.3\phi_1-0.2\phi_2,
\]

the value \(n^2|\mathcal E_{\ell,h}(f_h)-\mathcal E_\ell(f)|\) approaches
\(5.525\), again showing a nonzero second-order leading term.

## 10. What has and has not been proved

### Now proved

1. The reduced forms Mosco-converge for every fixed target mode under a
   continuous positive modulation.
2. The corresponding reduced semigroups and all fixed-mode response matrices
   converge.
3. With \(W^{2,\infty}\) modulation, a \(C^2\) positive target density, fixed
   ports, and \(t\in[t_0,T]\), the response histories, Grams, and singular
   values converge at \(O(n^{-2})\).
4. The theorem applies to the exact linear-ramp, five-source, one-target-mode
   Stage V protocol.

### Not proved here

1. **Full-output \(O(n^{-2})\) convergence.** A piecewise-constant density
   reconstruction has an unavoidable \(O(h)\) approximation error for a
   generic smooth function. Fixed modal coefficients can superconverge at
   \(O(h^2)\); the entire reconstructed density is a different normed claim.
2. **Uniform second-order convergence at \(t=0\).** The quantitative estimate
   is declared only for \(t\ge t_0>0\). Plain convergence includes zero.
3. **A growing-mode theorem.** Constants depend on \(K\) and \(L\). No claim is
   made when either grows with \(n\).
4. **Atomic target preparations.** They fall outside the smooth-background
   rate theorem. Stage V already proves that their first full-tangent jet
   diverges.
5. **An interval-certified continuum reference.** The cosine multiplication
   matrix is analytic, but the reported continuum exponential is evaluated in
   floating arithmetic with a truncation-stability check.
6. **The joint continuum/infinite-volume limit.** The theorem is fixed-domain.
7. **Nonlinear or path-space sensors.** The theorem concerns endpoint target
   density modes of the fixed linear generator.

## 11. Reproduction

Run:

    python oig_vi_fixed_mode_convergence.py
    python -m unittest -v test_oig_vi_fixed_mode_convergence.py

The tests independently verify:

- exact \(h\)-orthonormal density modes and the path spectrum;
- the analytic cosine matrix for multiplication by \(x\);
- stability of the continuum cosine cutoff;
- exact zero response at \(t=0\);
- second-order response-history and Gram convergence;
- second-order quadratic-form recovery; and
- positive definiteness of the limiting fixed-mode response Gram.

## 12. Recommended next theorem

The cleanest continuation is the mollifier phase diagram. Let a target
background have physical width \(\varepsilon_h\). The present theorem covers
fixed positive width. Stage V's atom is the opposite endpoint. The next task
should classify:

\[
 \varepsilon_h/h\to\infty,\qquad
 \varepsilon_h/h\to c\in(0,\infty),\qquad
 \varepsilon_h/h\to0,
\]

together with fixed \(t>0\) versus \(t_h/h^2\) fixed. That will determine
precisely where the smooth \(O(h^2)\) response theorem gives way to the
singular atomic initial layer.
