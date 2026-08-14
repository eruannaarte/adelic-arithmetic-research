# Operational Information Geometry VI

## The fixed-mode continuum theorem

- **Research status:** proved in the declared cell-centred model
- **Research, theorem development, computation, and writing:** Codex (OpenAI)
- **Originating direction and research environment:** TGN's human founder
- **Predecessor:** OPERATIONAL_INFORMATION_GEOMETRY_V.md
- **Scope:** a fixed-domain parabolic Markov model; not a claim about physical
  spacetime, relativistic propagation, or a substrate of reality

## Abstract

Stage V found second-order numerical convergence of density-normalized directed
responses but left the continuum statement as a hypothesis. This stage proves
both the convergence claim and, under smoothness assumptions, the observed
second-order rate, while locating their different time-zero boundaries.

For every fixed target mode, the reduced cell-centred generators converge
compactly in the Mosco sense to a Neumann Schrödinger operator. Their
reconstructed semigroups consequently converge in operator norm, uniformly on
every positive-time interval. For any fixed finite collection of source and
target modes, the response matrices converge uniformly even on time intervals
containing zero, and every finite weighted response Gram converges in operator
norm. If the modulation is \(W^{2,\infty}\), the target density is \(C^2\),
and time is restricted to a fixed positive interval, the complete
density-normalized fixed-mode response and its finite protocol Gram converge
at \(O(n^{-2})\). Thus the discrete operational geometry has a genuine and
quantitatively controlled continuum limit in the declared protocol.

There is also a strict boundary. Full semigroup operator-norm convergence
cannot include time zero because a finite reconstruction is a proper
projection. A target atom is covered only coefficient-by-coefficient at fixed
target bandwidth; it is not an \(L^2\) preparation and does not acquire a
uniform full-band time-zero theorem. Compact Mosco convergence itself proves
no rate; the \(O(n^{-2})\) result requires a separate mass-lumped
finite-element estimate and does not remain uniform as the positive time cutoff
tends to zero. Exact finite-block expansions and a rigorous Galerkin-tail bound
provide independent algebraic and computational checks.

## 1. The result in one sentence

The numerical hypothesis from Stage V becomes a theorem after the continuum
space, reconstruction maps, source metric, output metric, and target bandwidth
are declared explicitly.

The proof has four layers:

1. the graph energies converge compactly to the Neumann energy;
2. compact form convergence transfers to positive-time operator-norm semigroup
   convergence;
3. the exact target-mode reduction transfers that convergence to response
   histories and their Gramians; and
4. a quantitative lumped-mass resolvent estimate, followed by semigroup
   calculus, proves the positive-time \(O(n^{-2})\) response rate.

The mechanism is standard functional analysis. The contribution here is its
operational assembly for the one-way rate-modulated model, including the
normalization, the atom boundary, and falsification controls.

## 2. Discrete and continuum reduced generators

Let \(h=1/n\), \(x_i=(i+1/2)h\), and equip \(H_n=\mathbb R^n\) with

\[
 \langle u,v\rangle_h=h\sum_{i=0}^{n-1}u_iv_i.
\]

Let \(A_n=h^{-2}L_n\), where \(L_n\) is the unweighted path Laplacian.
Its cell-centred Neumann modes and eigenvalues are

\[
 \phi_{0,n}(i)=1,\qquad
 \phi_{k,n}(i)=\sqrt2\cos(k\pi x_i),
\]

\[
 \mu_{k,n}=4h^{-2}\sin^2\!\left(\frac{k\pi h}{2}\right).
\]

Fix a target mode \(\ell\), a coupling \(g\geq0\), and a continuous
modulation \(d:[0,1]\to\mathbb R\) satisfying

\[
 1+g d(x)\geq c>0.
\]

Set \(D_n=\operatorname{diag}(d(x_i))\). The exact target-mode reduction from
Stage V gives

\[
 K_{\ell,n}=A_n+\mu_{\ell,n}(I+gD_n).
\]

The continuum Hilbert space is \(H=L^2(0,1)\). Define

\[
 K_\ell=-\frac{d^2}{dx^2}
 +(\ell\pi)^2(1+g d(x))
\]

with the Neumann realization determined by

\[
 \mathcal E_\ell(u)
 =\int_0^1|u'|^2\,dx
 +(\ell\pi)^2\int_0^1(1+g d)|u|^2\,dx,
 \qquad D(\mathcal E_\ell)=H^1(0,1).
\]

The natural Neumann boundary condition belongs to the operator domain; it is
not imposed on the form domain.

## 3. Comparison maps and an exact compactness identity

For the cells \(C_{i,n}=[ih,(i+1)h)\), define

\[
 (J_nv)(x)=v_i\quad(x\in C_{i,n}),\qquad
 (P_nu)_i=h^{-1}\int_{C_{i,n}}u(x)\,dx.
\]

Then

\[
 \|J_nv\|_{L^2}=\|v\|_h,\qquad
 P_n=J_n^*,\qquad J_nP_nu\to u\quad\hbox{in }L^2.
\]

Midpoint samples are useful recovery sequences for smooth functions, but they
are not the \(L^2\)-adjoint projection. Keeping these roles separate is
essential.

Let \(I_nv\) be linear between adjacent cell centres and constant on the two
boundary half-cells. Then

\[
 \int_0^1 |(I_nv)'|^2\,dx
 =\frac1h\sum_{i=0}^{n-2}|v_{i+1}-v_i|^2
 =\langle v,A_nv\rangle_h,
\]

and

\[
 \|J_nv-I_nv\|_{L^2}^2
 \leq \frac{h^2}{12}\langle v,A_nv\rangle_h.
\]

The second inequality follows by integrating the square of the linear
deviation from each cell value on its two half-cells.

## 4. Compact form convergence

Define

\[
 \mathcal E_{\ell,n}(v)
 =\langle v,A_nv\rangle_h
 +\mu_{\ell,n}h\sum_i(1+gd(x_i))|v_i|^2.
\]

### Theorem 4.1 — compact Mosco convergence

For every fixed target mode \(\ell\),

\[
 \mathcal E_{\ell,n}\longrightarrow\mathcal E_\ell
\]

compactly in the Mosco sense under the comparison maps \(J_n,P_n\).

### Proof

For the lower bound, suppose \(J_nv_n\rightharpoonup u\) in \(L^2\) and

\[
 \sup_n\bigl(\|v_n\|_h^2+\mathcal E_{\ell,n}(v_n)\bigr)<\infty.
\]

The interpolation identity bounds \(I_nv_n\) in \(H^1(0,1)\), while the
interpolation error tends to zero. After taking a subsequence,
\(I_nv_n\rightharpoonup u\) in \(H^1\), and weak lower semicontinuity gives

\[
 \int|u'|^2
 \leq\liminf_n\langle v_n,A_nv_n\rangle_h.
\]

The piecewise-constant functions \(d_n(x)=d(x_i)\) on \(C_{i,n}\) converge
uniformly to \(d\), and \(\mu_{\ell,n}\to(\ell\pi)^2\). Since the potential is
nonnegative, its quadratic form is weakly lower semicontinuous. This proves the
Mosco lower condition.

For recovery, first take \(u\in C^1([0,1])\) and set \(v_{n,i}=u(x_i)\).
The reconstructions converge strongly to \(u\), the difference-quotient energy
is a Riemann sum for \(\int|u'|^2\), and the potential term is a midpoint
Riemann sum. Density of smooth functions in \(H^1(0,1)\), followed by a
diagonal choice, gives a recovery sequence for every \(u\in H^1(0,1)\).

Finally, every sequence with bounded norm and bounded energy has interpolants
bounded in \(H^1(0,1)\). Rellich compactness and the interpolation-error bound
give a strongly convergent subsequence of reconstructions. This is asymptotic
compactness, completing compact Mosco convergence. \(\square\)

## 5. Semigroup convergence and its exact time boundary

Write

\[
 T_{\ell,n}(t)=e^{-tK_{\ell,n}},\qquad
 T_\ell(t)=e^{-tK_\ell}.
\]

### Theorem 5.1 — positive-time operator-norm convergence

For every \(0<t_0<T<\infty\),

\[
 \sup_{t\in[t_0,T]}
 \left\|J_nT_{\ell,n}(t)P_n-T_\ell(t)\right\|_{L^2\to L^2}
 \longrightarrow0.
\]

### Proof

Compact Mosco convergence gives compact convergence of the positive-time
semigroups. Fix \(t>0\). If norm convergence failed, there would be unit
vectors \(f_n\in L^2\) for which the norm difference stayed bounded below.
Pass to a weakly convergent subsequence \(f_n\rightharpoonup f\). Then
\(P_nf_n\) converges generalized-weakly to \(f\), so compact convergence gives

\[
 J_nT_{\ell,n}(t)P_nf_n\longrightarrow T_\ell(t)f
\]

strongly. The continuum positive-time semigroup is compact, so also
\(T_\ell(t)f_n\to T_\ell(t)f\) strongly, a contradiction.

For \(s,t\geq t_0\), spectral calculus gives

\[
 \|e^{-tK}-e^{-sK}\|
 \leq \frac{|t-s|}{e t_0}
\]

for every nonnegative self-adjoint \(K\), discrete or continuous. A finite
time net upgrades pointwise norm convergence to uniform convergence on
\([t_0,T]\). \(\square\)

### Proposition 5.2 — why operator norm cannot include zero

At \(t=0\),

\[
 J_nT_{\ell,n}(0)P_n=J_nP_n=:\Pi_n.
\]

Each \(\Pi_n\) is a proper finite-rank orthogonal projection, hence

\[
 \|\Pi_n-I\|=1.
\]

Full operator-norm convergence therefore cannot hold on an interval containing
zero. This is a structural obstruction, not a weakness of the proof.

## 6. Fixed-mode responses do converge through time zero

Let

\[
 \phi_0(x)=1,\qquad \phi_k(x)=\sqrt2\cos(k\pi x).
\]

Let a normalized target preparation have coefficients
\(\beta_{\ell,n}\to\beta_\ell\) in a fixed collection \(0\leq\ell\leq L\).
For example, if \(\rho\in L^2(0,1)\) is represented by cell averages, then

\[
 \beta_{\ell,n}
 =\langle\phi_{\ell,n},P_n\rho\rangle_h
 \longrightarrow\langle\phi_\ell,\rho\rangle_{L^2}.
\]

For fixed nonconstant source modes \(1\leq k\leq K\), define

\[
 R_n(t)_{\ell k}
 =\beta_{\ell,n}
 \langle\phi_{0,n},T_{\ell,n}(t)\phi_{k,n}\rangle_h
\]

and

\[
 R(t)_{\ell k}
 =\beta_\ell
 \langle\phi_0,T_\ell(t)\phi_k\rangle_{L^2}.
\]

These are precisely the density-normalized modal responses of the one-way
generator.

### Theorem 6.1 — fixed-mode response convergence

For every finite \(K,L\) and every \(T<\infty\),

\[
 \sup_{0\leq t\leq T}\|R_n(t)-R(t)\|_{\mathrm{op}}
 \longrightarrow0.
\]

### Proof

The discrete cosine modes are strongly convergent recovery sequences for the
continuum cosines. On every \([t_0,T]\), Theorem 5.1 gives the conclusion.
Near zero, fixed modes have uniformly bounded generator images:

\[
 \sup_n\|K_{\ell,n}\phi_{k,n}\|_h<\infty
\]

for fixed \(k,\ell\). Hence

\[
 \|(T_{\ell,n}(t)-I)\phi_{k,n}\|_h
 \leq t\|K_{\ell,n}\phi_{k,n}\|_h,
\]

uniformly in \(n\), and the analogous continuum estimate holds. Letting
\(t_0\downarrow0\) closes the interval. There are only finitely many entries,
so entrywise uniform convergence is equivalent to convergence in any matrix
norm. \(\square\)

This improves the original Stage V hypothesis: a positive time cutoff is
unnecessary when both source and observed target bandwidths remain fixed.

### Corollary 6.2 — response-Gram convergence

Let \(W(t)\) be a bounded positive semidefinite output metric and let \(\nu\)
be a finite positive observation measure on \([0,T]\), including finitely many
weighted observation times. Then

\[
 \Gamma_n=\int R_n(t)^*W(t)R_n(t)\,d\nu(t)
 \longrightarrow
 \Gamma=\int R(t)^*W(t)R(t)\,d\nu(t)
\]

in operator norm. Consequently every eigenvalue of the finite operational Gram
converges. A strictly positive limiting smallest eigenvalue persists for all
sufficiently fine grids, although its numerical size may still make recovery
ill-conditioned.

## 7. What the atom statement does and does not say

A target atom is not an \(L^2\) density, so it is not covered as a full
preparation by Theorem 4.1. Nevertheless, if its cell centres
\(x_{j(n)}\to y_0\), then every separately normalized fixed coefficient obeys

\[
 \beta_{\ell,n}=\phi_{\ell,n}(j(n))
 \longrightarrow\phi_\ell(y_0).
\]

Therefore Theorem 6.1 extends coefficient-by-coefficient to a target atom at
fixed target bandwidth. The location approximation is generically only
\(O(h)\), unless the chosen sequence has additional alignment.

This does not prove convergence of the full target-mode vector, whose bandwidth
grows with \(n\). It also does not put the atom in the domain of the continuum
generator at \(t=0\). The divergent \(n^{5/2}\) first jet and the initial-layer
counterexample from Stage V remain valid.

## 8. The positive-time second-order theorem

Compact Mosco convergence supplies convergence but no rate. The sharp rate
uses the special cell-centred scheme and a separate quantitative argument.

Write

\[
 m_n(z,w)=\langle z,w\rangle_h,
 \qquad (S_nf)_i=f(x_i).
\]

Besides the cell-average comparison map \(P_n=J_n^*\), introduce the exact
lumped load map \(Q_n\) by

\[
 m_n(Q_nf,z)=\langle f,I_nz\rangle_{L^2}
 \qquad(z\in H_n).
\]

These maps have different roles: \(P_n\) belongs to the Mosco comparison,
whereas \(Q_n\) removes a load-quadrature remainder in the quantitative
finite-element estimate.

### Lemma 8.1 — cell-centred semigroup error

Let \(v\in W^{2,\infty}(0,1)\), \(v\geq v_->0\), and

\[
 K=-\partial_x^2+\lambda v,
 \qquad K_n=A_n+\lambda\operatorname{diag}(v(x_i)),
\]

with Neumann boundary conditions and fixed \(\lambda\geq0\). If \(f\) belongs
to a fixed finite-dimensional space of smooth functions satisfying
\(f'(0)=f'(1)=0\), then, for \(0<t_0<T<\infty\),

\[
 \sup_{t\in[t_0,T]}
 \|I_ne^{-tK_n}S_nf-e^{-tK}f\|_{L^2}
 \leq C h^2.
\]

### Proof sketch

The interpolation \(I_n\) turns the path stiffness exactly into

\[
 \int|(I_nz)'|^2=\langle z,A_nz\rangle_h.
\]

The remaining mass and reaction forms are their lumped versions. Elementwise
approximation and quadrature estimates, including the two Neumann boundary
half-cells, give a first-order energy estimate for the shifted resolvents with
the exact load \(Q_n\). One-dimensional elliptic regularity and the dual
Aubin--Nitsche argument improve this to

\[
 \|I_n(z+K_n)^{-1}Q_n-(z+K)^{-1}\|_{L^2\to L^2}
 \leq C_\theta h^2
\]

on a fixed sector, with the usual large-\(z\) decay. Dunford's contour formula
then gives \(Ch^2/t\) for the semigroups. Finally,

\[
 \|S_nf-Q_nf\|_h\leq Ch^2\|f\|_{C^2}
\]

for the fixed Neumann-compatible source space, including the endpoint cells.
This proves the displayed estimate. Full details, including the distinction
between \(P_n\) and \(Q_n\), are in the
[detailed proof memo](OIG_VI_FIXED_MODE_RESPONSE_THEOREM.md).
\(\square\)

### Theorem 8.2 — full fixed-response \(O(n^{-2})\) convergence

Assume:

1. \(d\in W^{2,\infty}(0,1)\) and \(1+gd\geq c>0\);
2. the source and observed target mode counts \(K,L\) are fixed;
3. the target density \(\rho\in C^2([0,1])\) is positive and normalized; and
4. its discrete preparation is the normalized midpoint rule,

   \[
   Z_n=h\sum_i\rho(x_i),\qquad
   \beta_{\ell,n}=Z_n^{-1}h\sum_i
   \phi_\ell(x_i)\rho(x_i).
   \]

Then, for every \(0<t_0<T<\infty\),

\[
 \boxed{
 \sup_{t\in[t_0,T]}\|R_n(t)-R(t)\|_{\mathrm{op}}
 \leq C h^2=Cn^{-2}.}
\]

### Proof

Apply Lemma 8.1 to each fixed reduced block with
\(\lambda=(\ell\pi)^2\) and \(v=1+gd\). The actual grid block uses
\(\mu_{\ell,n}\) instead. The exact path estimate

\[
 0\leq(\ell\pi)^2-\mu_{\ell,n}
 \leq\frac{(\ell\pi)^4}{12}h^2
\]

and Duhamel's identity add only \(O(h^2)\), uniformly on \([0,T]\). The
composite midpoint rule gives \(Z_n=1+O(h^2)\) and
\(\beta_{\ell,n}=\beta_\ell+O(h^2)\). Fixed matrix dimension completes the
claim. \(\square\)

Finite stacks, response Grams, and their singular values consequently converge
at \(O(n^{-2})\). This theorem is for fixed ports and \(t\geq t_0>0\); it is
not a full reconstructed-density estimate and its constant is not uniform as
\(t_0\downarrow0\).

### 8.3 Independent algebraic and numerical audit

For the Stage V ramp \(d(x)=x\), exact midpoint cosine sums give, at every
fixed cosine cutoff \(M\),

\[
 K_{n,M}=K_M+n^{-2}E_M+O_M(n^{-4}).
\]

The full finite response was also compared with an independently constructed
continuum cosine operator:

| \(n\) | relative history error | \(n^2\) times error | relative Gram error |
|---:|---:|---:|---:|
| 8 | \(1.09216\times10^{-2}\) | 0.698982 | \(1.18671\times10^{-2}\) |
| 16 | \(2.72552\times10^{-3}\) | 0.697733 | \(2.94648\times10^{-3}\) |
| 32 | \(6.81290\times10^{-4}\) | 0.697641 | \(7.35544\times10^{-4}\) |
| 64 | \(1.70318\times10^{-4}\) | 0.697623 | \(1.83819\times10^{-4}\) |
| 128 | \(4.25793\times10^{-5}\) | 0.697618 | \(4.59507\times10^{-5}\) |

The fitted history order is \(2.00004\). A 70-decimal-digit recomputation
differs from binary64 by at most \(8.35\times10^{-17}\). Separately, a
192-bit Arb audit encloses the declared \(M=5\) generator expansions and
certifies the rational bounds

\[
 \|n^2(K_{n,5}-K_5)\|_F<6000,
 \qquad
 \|n^4(K_{n,5}-K_5-n^{-2}E_5)\|_F<50000
\]

for the nine audited grids \(8\leq n\leq128\). A two-crossing Duhamel bound on
the Galerkin tail independently proves full fixed-mode convergence by first
choosing the cutoff and then refining the grid. These computations audit the
normalization, algebra, rate, and floating arithmetic; they are not substitutes
for Lemma 8.1.

## 9. Falsification ledger

| Overstatement | Control or correction |
|---|---|
| operator norm converges through \(t=0\) | impossible: \(\|J_nP_n-I\|=1\) |
| fixed modes require \(t_0>0\) | false: fixed modal responses converge uniformly on \([0,T]\) |
| an atom is an \(L^2\) preparation | false; only fixed normalized coefficients are covered |
| Mosco convergence proves \(O(h^2)\) | false; it proves convergence without a rate |
| fixed-Galerkin \(O(h^2)\) alone proves the full rate | false; Theorem 8.2 needs the separate lumped-mass resolvent estimate |
| midpoint sampling is the \(L^2\) projection | false; cell averaging is the adjoint projection |
| smoothness is irrelevant to the rate | false; a sampled jump is first order and a half-Hölder cusp is order \(h^{3/2}\) |
| atom placement is harmless | false; nearest-cell coefficients are generically first order, while a moment-preserving split can restore second order |
| the endpoint convention is cosmetic | false; \(h=1/(n-1)\) with this stencil creates an \(O(h)\) boundary shift |
| fixed-mode convergence is a growing-band theorem | false; \(k_n=n/2,\ t_n=n^{-2}\) leaves the gap \(|e^{-2}-e^{-\pi^2/4}|=0.05053\ldots\) |
| nonconstant modulation guarantees visibility | false; reflection-symmetric modulation makes every odd source mode invisible |
| fixed-domain compactness survives infinite volume | not established; Rellich compactness is lost |
| algebraic visibility implies stable recovery | false; the limiting response remains ill-conditioned |

## 10. Interpretation

The theorem establishes a controlled bridge, not a physical ontology. Within
the chosen parabolic model, refining the graph does not erase the declared
low-mode intervention-response geometry. The continuum response is independent
of the arbitrary mesh once preparation and observation ports are normalized as
densities.

This matters for later applications because a protocol optimized on a finite
mesh is meaningful only if its observable geometry survives refinement. The
present result supplies that prerequisite. It does not turn a diffusion model
into a theory of light, radio, sonar, or relativistic causality; those require
wave or Maxwell-type propagators and a new theorem.

## 11. Literature boundary

The equivalence between Mosco convergence, resolvent convergence, and
semigroup convergence on varying Hilbert spaces is part of the theory developed
by Kuwae and Shioya:

- K. Kuwae and T. Shioya, *Convergence of spectral structures: a functional
  analytic theory and its applications to spectral geometry*, Communications
  in Analysis and Geometry 11 (2003), 599–673,
  <https://www.intlpress.com/site/pub/files/_fulltext/journals/cag/2003/0011/0004/CAG-2003-0011-0004-a001.pdf>.

Uniform-on-compact-time semigroup approximation is also a standard
Trotter--Kato theme:

- K. Ito and F. Kappel, *The Trotter--Kato theorem and approximation of
  PDEs*, Mathematics of Computation 67 (1998), 21–44,
  <https://doi.org/10.1090/S0025-5718-98-00915-6>.

Classical optimal \(L^2\) estimates for lumped-mass parabolic methods provide
background for the quantitative argument:

- C. M. Chen and V. Thomée, *The lumped mass finite element method for a
  parabolic problem*, The ANZIAM Journal 26 (1985), 329–354,
  <https://doi.org/10.1017/S0334270000004549>.

That paper treats a two-dimensional Dirichlet setting, not the exact
one-dimensional Neumann half-cell convention used here; the required local
specialization is therefore included in the detailed proof memo. No priority
claim is made for these general mechanisms. The new result in this research
line is their precise application to the declared operational response model,
including its normalization and boundary ledger.

## 12. Reproduction

Install the dedicated high-precision dependencies and run both Stage VI lanes:

    python -m pip install -r oig_vi_fixed_mode_requirements.txt
    python oig_vi_fixed_mode_convergence.py
    python -m unittest -v test_oig_vi_fixed_mode_convergence.py
    python oig_vi_adversarial_controls.py
    python -m unittest -v test_oig_vi_adversarial_controls.py

Then run the complete repository regression suite:

    python -m unittest discover -v

The analytic details are in the [proof memo](OIG_VI_FIXED_MODE_RESPONSE_THEOREM.md),
the independent exact/high-precision audit is in the
[computational report](oig_vi_fixed_mode_convergence.md),
and the falsification results are in the
[adversarial audit](OIG_VI_ADVERSARIAL_AUDIT.md).
Theorems 4.1, 5.1, 6.1, and 8.2 are analytic; the floating and interval
calculations audit their declared specialization.

## 13. Next research order

1. **Map the mollifier phase diagram.** Classify preparation width
   \(\varepsilon_h\) versus mesh width \(h\) in the regimes
   \(\varepsilon_h/h\to\infty,c,0\), together with fixed time versus
   \(t_h/h^2\) fixed.
2. **Resolve the smooth initial layer.** Determine whether the
   Neumann-compatible fixed-response \(O(h^2)\) estimate extends uniformly to
   \(t=0\), and identify the sharp compatibility conditions.
3. **Characterize cyclic visibility.** Turn the modal/Krylov description into
   necessary and sufficient quantitative identifiability conditions.
4. **Develop path-space sensing.** Treat jump counts and holding times with
   tilted generators.
5. **Only then open the wave branch.** Replace the heat semigroup by acoustic
   or electromagnetic propagators and ask which operational statements
   survive.
