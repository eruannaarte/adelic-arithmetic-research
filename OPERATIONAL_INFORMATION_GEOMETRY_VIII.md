# Operational Information Geometry VIII

## The uniform three-parameter atlas

- **Research status:** analytic theorem package and computational audit
  complete; not peer reviewed
- **Research, theorem development, computation, and writing:** Codex (OpenAI)
- **Originating direction and research environment:** TGN's human founder
- **Predecessor:** Operational Information Geometry VII
- **Scope:** the declared one-way parabolic Markov model; not a physical theory

## Abstract

Stage VII found continuum and lattice phase functions for a target preparation
of width \(\varepsilon\) on a mesh of spacing \(h\), observed at time \(t\).
Its missing step was uniformity: the earlier results fixed one ratio before
taking another limit.  This stage replaces that iterated picture by a
three-chart quantitative atlas in

\[
 c=\frac{\varepsilon}{h},\qquad
 q=\frac{t}{\varepsilon^2},\qquad
 \tau=\frac{t}{h^2}=c^2q.
\]

For the canonical cell-centred Neumann path, a ramp modulation, a fixed cosine
source, an interior conservative smooth preparation, and the complete
density-normalized target norm, the resolved chart satisfies

\[
 \left|
 \frac{\sqrt\varepsilon\,\mathcal N_h(t)}{\mathcal P(q)}-1
 \right|
 \leq C\left[\varepsilon^2+(h/\varepsilon)^2\right]
\]

when \(q\) remains in a compact subset of \((0,\infty)\).  At early times the
canonical odd and even ramp ports obey

\[
 \left|
 \frac{\sqrt\varepsilon\,\mathcal N_h(t)}{\mathcal P(q)}-1
 \right|
 \leq C\left[q+(h/\varepsilon)^2+\varepsilon^2\right].
\]

At finite lattice width, a declared local probability profile \(Q\) has its
own phase \(\Psi_Q(\tau)\).  The fixed-microscopic-time comparison is

\[
 |h\mathcal N_h(\tau h^2)^2-\Psi_Q(\tau)^2|
 \leq C(h+\|w_h-Q\|_1),
\]

and a single estimate remains valid while \(\tau\) grows into the atomic
tail.  Most importantly, if

\[
 t\to0,\qquad t/h^2\to\infty,\qquad
 \sigma_h^2/t\to0,\qquad d_h/\sqrt t\to\infty,
\]

then the full finite response satisfies the simultaneous limit

\[
 \boxed{\sqrt t\,\mathcal N_h(t)^2\longrightarrow C_F^2.}
\]

Here \(\sigma_h^2\) is the physical preparation variance and \(d_h\) its
barycentre's distance from the reflecting boundary.  No fixed lattice phase
is needed in this tail.  At distance \(d_h/\sqrt t\to\kappa\), a reflected
boundary profile replaces the interior constant and doubles the squared
constant at an endpoint.

The canonical critical-width laws are now quantitative: odd ports at
\(\varepsilon=h^{4/5}\) have relative error \(O(h^{2/5})\), while even ports
at \(\varepsilon=h^{8/9}\) have relative error \(O(h^{2/9})\).  Exact first
corrections explain why those theorems can be computationally glacial.  The
stage also gives explicit counterexamples to placement-free lattice limits,
unresolved continuum limits, relative theorems at null ports, and cancelled
ports without discrete moment preservation.

## 1. Why the answer is an atlas

A single relative error formula over the whole \((h,\varepsilon,t)\) cube is
false.  There are three distinct mechanisms:

1. when \(\varepsilon\gg h\), conservative Fourier consistency resolves the
   smooth preparation;
2. when \(\varepsilon=O(h)\) and \(t=O(h^2)\), the actual allocation of mass
   among cells survives through a lattice characteristic function; and
3. when \(h,\varepsilon\ll\sqrt t\ll1\), diffusion erases both ultraviolet
   rules and leaves a continuum atomic constant.

Zeros force an additional distinction.  Absolute squared-profile estimates
remain meaningful when a limiting channel vanishes; relative estimates do
not.  A valid uniform result is therefore a compatible collection of charts,
with overlap theorems and declared null sets, rather than one formula obtained
by dividing everywhere by a phase function.

## 2. Declared finite model and normalization

Let \(h=1/n\), \(x_i=(i+1/2)h\), and

\[
 \langle u,v\rangle_h=h\sum_{i=0}^{n-1}u_iv_i.
\]

Let \(A_h=h^{-2}L_n\), where \(L_n\) is the unweighted path Laplacian.  Its
nonconstant Neumann modes and eigenvalues are

\[
 \phi_{\ell,h}(i)=\sqrt2\cos(\ell\pi x_i),\qquad
 \mu_{\ell,h}=4h^{-2}\sin^2\!\left(\frac{\ell\pi h}{2}\right).
\]

Fix the modulation

\[
 V(x)=1+gx,\qquad g>0,
\]

and a fixed source port

\[
 \phi_k(x)=\sqrt2\cos(k\pi x).
\]

At target mode \(\ell\), the reduced source operator is

\[
 K_{\ell,h}=A_h+\mu_{\ell,h}V_h.
\]

For a target probability-mass vector \(q_h\), define

\[
 \beta_{\ell,h}=\sum_iq_{h,i}\phi_{\ell,h}(i),\qquad
 a_{\ell k,h}(t)=
 \langle1,e^{-tK_{\ell,h}}\phi_{k,h}\rangle_h.
\]

The complete declared response is

\[
 \boxed{
 \mathcal N_{h,k}(t)^2
 =\sum_{\ell=1}^{n-1}|\beta_{\ell,h}|^2
 |a_{\ell k,h}(t)|^2.}
\]

This is the \(L^2\) norm of the target *density* response.  The source density
has unit \(L^2\) norm and is injected as a mass perturbation.  These reciprocal
normalizations cancel in the modal formula; omitting either changes every
singular exponent.

## 3. The two phase functions

The high-target-frequency source profile is

\[
 F_k(s)=\int_0^1e^{-sV(x)}\phi_k(x)\,dx
 =\sqrt2e^{-s}
 \frac{gs[1-(-1)^ke^{-gs}]}{(gs)^2+(k\pi)^2}.
\]

For an even smooth probability kernel \(\eta\), the resolved phase is

\[
 \boxed{
 \mathcal P_k(q)^2
 =\int_0^\infty
 |\widehat\eta(\pi u)|^2
 |F_k(\pi^2qu^2)|^2\,du.}
\]

For a local lattice probability profile \(Q=(Q_m)_{m\in\mathbb Z}\), put

\[
 B_Q(\theta)=\sum_mQ_me^{im\theta},\qquad
 \omega(\theta)=4\sin^2(\theta/2),
\]

and define

\[
 \boxed{
 \Psi_{Q,k}(\tau)^2
 =\frac1\pi\int_0^\pi
 |B_Q(\theta)|^2|F_k(\tau\omega(\theta))|^2\,d\theta.}
\]

Finally,

\[
 \boxed{
 C_{F,k}^2
 =\int_0^\infty|F_k(\pi^2r^2)|^2\,dr.}
\]

For the ramp and every nonconstant cosine source, \(C_{F,k}>0\).  The general
theorems retain the explicit condition \(F\not\equiv0\) before turning a
squared-profile limit into a norm equivalence.

## 4. Resolved comparison theorem

Let the target preparation be deposited by exact cell integration from an
even \(C_c^\infty\) kernel of width \(\varepsilon\), centred a fixed positive
distance from the endpoints.  An even Schwartz kernel is also admissible
after exact normalization on \([0,1]\), provided its boundary tail is included
in every relative error budget.

### Theorem 4.1 — balanced chart

For every compact \(K\Subset(0,\infty)\), there are constants \(C_K,h_0>0\)
such that, for \(q=t/\varepsilon^2\in K\),
\(h/\varepsilon<h_0\), and sufficiently small \(h,\varepsilon\),

\[
 \boxed{
 \left|
 \frac{\sqrt\varepsilon\,\mathcal N_{h,k}(t)}{\mathcal P_k(q)}-1
 \right|
 \leq C_K\left[
 \varepsilon^2+\left(\frac h\varepsilon\right)^2
 \right].}
\]

The \(\varepsilon^2\) term is source diffusion.  The
\((h/\varepsilon)^2\) term combines target dispersion, cell integration, and
source quadrature.  A first-order \(h/\varepsilon\) term is absent because the
preparation is conservative.

### Theorem 4.2 — early chart

Let

\[
 r(k)=\begin{cases}1,&k\text{ odd},\\2,&k\text{ even}.
 \end{cases}
\]

For \(0<q\leq q_0\), \(h/\varepsilon<h_0\), and sufficiently small
\(h,\varepsilon\), the canonical ramp/cosine model satisfies

\[
 \boxed{
 \left|
 \frac{\sqrt\varepsilon\,\mathcal N_{h,k}(t)}{\mathcal P_k(q)}-1
 \right|
 \leq C\left[
 q+\left(\frac h\varepsilon\right)^2+\varepsilon^2
 \right].}
\]

The proof is uniform even when \(q\) is smaller than every fixed power used in
the Fourier argument.  In that ultra-early subchart, set
\(\tau=t/h^2\) and \(s=t\mu_{\ell,h}\).  A Dyson expansion gives

\[
 \left|a_{\ell k,h}(t)-\frac{(-s)^r}{r!}m_{r,k,h}\right|
 \leq Cs^r\tau,
\]

while the conservative target jet satisfies

\[
 \varepsilon^{4r+1}
 \sum_\ell|\beta_{\ell,h}|^2\mu_{\ell,h}^{2r}
 =\|\eta^{(2r)}\|_2^2
 [1+O((h/\varepsilon)^2)].
\]

For even \(k\), reflection makes the discrete first moment exactly zero at
every mesh size.  This exact cancellation is material.

### General cancelled ports

If a general smooth modulation has continuum first moment \(m_1=0\) but
second moment \(m_2\ne0\), its discrete comparison contains

\[
 \frac{|m_{1,h}|}{q}.
\]

Thus \(h/\varepsilon\to0\) is not sufficient: one also needs
\(m_{1,h}=o(q)\).  A smooth explicit modulation in the proof memo has
\(m_1=0\) but \(m_{1,h}\asymp h^2\), and a path with \(q\ll h^2\) makes the
spurious discrete first jet dominate.  This falsifies an all-port theorem
based on geometric resolution alone.

## 5. Finite-cell lattice theorem

Choose a carrier cell and let \(w_h\) be the local target weights around it.
Suppose \(w_h\to Q\) in \(\ell^1\), with uniformly bounded first lattice
moment, and keep the physical carrier a fixed distance \(d>0\) from the
endpoints.

### Theorem 5.1 — fixed microscopic time

For every compact \(K\Subset(0,\infty)\), uniformly in \(\tau\in K\),

\[
 \boxed{
 |h\mathcal N_h(\tau h^2)^2-\Psi_Q(\tau)^2|
 \leq C_{K,d}[h+\|w_h-Q\|_1].}
\]

The general proof deliberately states a first-order safe bound.  In the
canonical midpoint/conservative laboratory, the residual is empirically
second order for centred and off-centre preparations alike.

### Theorem 5.2 — one bound into the tail

For \(\tau\geq1\), \(t=\tau h^2\leq t_*\),

\[
 \boxed{
 \sqrt\tau\,
 |h\mathcal N_h(t)^2-\Psi_Q(\tau)^2|
 \leq C\left[
 \sqrt t+h+\|w_h-Q\|_1+\frac{\sqrt t}{d}
 \right].}
\]

If \(F\not\equiv0\) and the displayed error tends to zero, division by the
positive lattice profile gives

\[
 \mathcal N_h(t)=h^{-1/2}\Psi_Q(\tau)[1+o(1)].
\]

The lattice phase itself forgets every fixed finite-cell profile at the
quantitative rate

\[
 \boxed{
 |\sqrt\tau\,\Psi_Q(\tau)^2-C_F^2|
 \leq C\frac{1+\operatorname{Var}(Q)}{\tau}.}
\]

This is the overlap between the finite-cell and continuum atomic charts.

## 6. Simultaneous atomic and boundary theorems

For an arbitrary target probability vector, let

\[
 \bar y_h=\sum_iq_{h,i}x_i,\qquad
 \sigma_h^2=\sum_iq_{h,i}(x_i-\bar y_h)^2,
\]

and

\[
 d_h=\min\{\bar y_h,1-\bar y_h\}.
\]

### Theorem 6.1 — joint interior atomic tail

For \(\tau=t/h^2\geq1\), \(0<t\leq t_*\), and sufficiently fine grids,

\[
 \boxed{
 |\sqrt t\,\mathcal N_h(t)^2-C_F^2|
 \leq C\left[
 \sqrt t+h+\frac1\tau+\frac{\sigma_h^2}{t}
 +\frac{\sqrt t}{d_h}
 \right].}
\]

Consequently,

\[
 t\to0,\quad t/h^2\to\infty,\quad
 \sigma_h^2/t\to0,\quad d_h/\sqrt t\to\infty
\]

imply

\[
 \boxed{\sqrt t\,\mathcal N_h(t)^2\to C_F^2.}
\]

If \(C_F>0\), and only then,

\[
 \mathcal N_h(t)\sim C_Ft^{-1/4}.
\]

For a preparation supported on a uniformly bounded number of cells,
\(\sigma_h^2=O(h^2)\), so its shape error is \(O(1/\tau)\).  One-cell atoms,
half/half split atoms, and fixed finite-cell mollifiers therefore share the
same joint atomic tail even though they have different finite-\(\tau\)
phases.

For the smoother canonical mollifier, the refined resolved proof gives the
sharper endpoint estimate

\[
 |\sqrt t\,\mathcal N_h(t)^2-C_F^2|
 \leq C\left[t+\frac{h^2+\varepsilon^2}{t}\right].
\]

### Theorem 6.2 — reflecting boundary layer

Assume still that \(t\to0\), \(t/h^2\to\infty\), and
\(\sigma_h^2/t\to0\).  If instead of the interior condition one has

\[
 \frac{d_h}{\sqrt t}\to\kappa\in[0,\infty),
\]

then

\[
 \boxed{
 \sqrt t\,\mathcal N_h(t)^2\to C_{F,\kappa}^2,}
\]

where

\[
 \boxed{
 C_{F,\kappa}^2
 =\int_0^\infty
 [1+\cos(2\pi\kappa r)]
 |F(\pi^2r^2)|^2\,dr.}
\]

The interior convention \(\kappa=\infty\) recovers \(C_F^2\).  At the
reflecting endpoint,

\[
 C_{F,0}^2=2C_F^2.
\]

The factor two applies to the squared norm; the endpoint norm constant is
\(\sqrt2\) times the interior constant.

## 7. Critical widths and the resolution barrier

At microscopic time \(t=\tau h^2\), let \(\varepsilon=h^\alpha\).  If the
first nonzero multiplication moment has order \(r\), the critical exponent is

\[
 \alpha_c(r)=\frac{4r}{4r+1}.
\]

Theorems 4.1--4.2 certify, for the ramp,

\[
 \boxed{
 \begin{aligned}
 k\text{ odd},\quad\varepsilon=h^{4/5}:\quad
 \mathcal N_{h,k}(\tau h^2)
 &=\frac{2\sqrt2g}{(k\pi)^2}\|\eta''\|_2\tau
 [1+O(h^{2/5})],\\
 k\text{ even},\quad\varepsilon=h^{8/9}:\quad
 \mathcal N_{h,k}(\tau h^2)
 &=\frac{\sqrt2g^2}{(k\pi)^2}\|\eta^{(4)}\|_2\tau^2
 [1+O(h^{2/9})].
 \end{aligned}}
\]

For the standard Gaussian, if

\[
 \mathcal P_k(q)=C_{r,k}q^r[1+O(q)],
\]

then the first correction is exactly

\[
 \boxed{
 \frac{\mathcal P_k(q)}{C_{r,k}q^r}
 =1-\gamma_rq+O(q^2),\qquad
 \gamma_r=\frac{(2+g)(4r+1)}4.}
\]

At \(g=0.8\),

\[
 \gamma_1=3.5,\qquad\gamma_2=6.3.
\]

On a critical path, \(c=\varepsilon/h=n^{1/(4r+1)}\) and \(q\asymp c^{-2}\).
Thus the physical endpoint correction and lattice dispersion improve only as
\(c^{-2}\), while

\[
 n=c^{4r+1}.
\]

This creates a severe accessibility barrier.  At \(\tau=1\), the direct
finite errors to the leading critical constant are

| \(n\) | odd \(r=1\) | even \(r=2\) |
|---:|---:|---:|
| 63 | 0.42744 | 0.82832 |
| 127 | 0.35860 | 0.79442 |
| 255 | 0.29616 | 0.75782 |
| 511 | 0.24098 | 0.71850 |

Yet the finite response already agrees with its lattice phase to between
roughly \(10^{-3}\) and \(10^{-5}\).  The slow step is \(c\to\infty\), not
finite-grid convergence.  Lattice extrapolation gives:

| order | \(c\) | equivalent \(n=c^{4r+1}\) | leading-law error |
|---:|---:|---:|---:|
| 1 | 8 | 32,768 | 0.0563 |
| 2 | 8 | 134,217,728 | 0.1039 |

An asymptotically correct exponent can therefore be practically invisible on
ordinary grids.  This is a theorem-resolution issue, not evidence against the
limit.

## 8. Proof architecture

Four ingredients make the uniform bounds work.

### 8.1 Weak Duhamel estimate

With \(s=t\mu_{\ell,h}\), a discrete gradient maximum principle gives

\[
 \boxed{
 |a_{\ell k,h}(t)-F_{k,h}(s)|
 \leq Ct\,s(1+s)e^{-cs}.}
\]

The extra factor \(s\) comes from moving the source Laplacian onto the left
semigroup and observing that the constant vector develops a gradient only
through the modulation.  This matrix-element bound removes the earlier
\(O(\sqrt t)\) loss without making a false operator-norm claim.

### 8.2 Conservative Fourier multiplier

Exact cell integration gives

\[
 \beta_{\ell,h}
 =\sqrt2\operatorname{Re}\left[
 e^{i\ell\pi y_0}\widehat\eta(\varepsilon\ell\pi)
 \operatorname{sinc}(\ell\pi h/2)
 \right]+R_{\ell,h},
\]

with \(|R_{\ell,h}|\leq C_M(h/\varepsilon)^M\).  The sinc and lattice-symbol
errors are second order on the active band.

### 8.3 Envelope accumulation

The response envelope \(s^a(1+s)^be^{-cs}\) is summable on the rescaled modal
lattice.  For \(\tau\geq1\),

\[
 \sqrt t\sum_{\ell=1}^{n-1}
 G\!\left(4\tau\sin^2\frac{\pi\ell}{2n}\right)\leq C_G.
\]

Errors are therefore integrated over a band of physical width
\(O(t^{-1/2})\); they are not multiplied by the ambient dimension \(n\).

### 8.4 Barycentric characteristic function

If \(\chi_h(k)\) is the characteristic function of the preparation centred
at its physical barycentre, then

\[
 |\chi_h(k)-1|\leq\frac{k^2\sigma_h^2}{2}.
\]

On the active band \(k=O(t^{-1/2})\), this becomes exactly
\(O(\sigma_h^2/t)\).  That is why physical variance, rather than a nominal
width label, is the correct atomic-tail variable.

## 9. Computational audit

The Stage VIII laboratory uses exact target-mode separation followed by
symmetric tridiagonal source eigendecomposition.  A small dense
\(n^2\)-state exponential independently checks the reduction.  The tests use
ordinary floating point and adaptive quadrature; they are regression and
falsification evidence, not interval certificates.

The main findings are:

- the fixed-\((c,\tau)\) squared residual has median empirical order
  \(h^{1.990}\);
- the lattice-to-continuum bridge has median order \(c^{-1.999}\);
- the balanced residual divided by
  \(\varepsilon^2+c^{-2}\) is at most \(2.69\times10^{-3}\) at the terminal
  tested grids;
- the joint atomic residual divided by
  \(\sqrt t+(\varepsilon/\sqrt t)^2+(h/\sqrt t)^2\) is at most
  \(3.10\times10^{-3}\) at the terminal tested grids;
- independent quadrature recovers \(\gamma_1\) and \(\gamma_2\) as
  \(3.498879\) and \(6.297040\) at \(q=10^{-4}\), and subtracting the exact
  correction changes the residual order from approximately \(q\) to
  \(q^2\); and
- the endpoint/interior squared atomic ratios converge numerically to
  \(2\) and \(1\), respectively.

The focused Stage VIII suites contain 20 tests, and the clean complete
repository run passes 231 tests after this stage's independent boundary
control is added.

## 10. Falsification ledger

| Tempting statement | Correct boundary |
|---|---|
| one relative formula is uniform over all \((h,\varepsilon,t)\) | false near phase zeros; use absolute squared-profile bounds and a chart atlas |
| \(\varepsilon/h=O(1)\) selects one lattice phase | false without a limiting placement/deposition rule |
| an atom and a half/half split are equivalent at finite \(\tau\) | false; their phase gap is about \(0.00314629\) in the declared control |
| the continuum phase remains valid below mesh resolution | false; a tested unresolved gap tends to \(0.01638194\) |
| \(t/h^2\to\infty\) alone gives the atomic law | false; also require \(t\to0\), variance \(o(t)\), and the correct boundary chart |
| every atom has the interior constant | false within \(O(\sqrt t)\) of a reflector |
| \(F\equiv0\) implies \(\mathcal N\sim C_Ft^{-1/4}\) | false; division by zero is meaningless and mixed words may survive |
| a continuum-cancelled first moment is enough on every mesh | false; require \(m_{1,h}=o(q)\) unless symmetry makes it exactly zero |
| a noncompact Gaussian tail is harmless in every relative early law | false until its omitted mass is small compared with \(q^r\) |
| the multiplication profile is a complete causal hierarchy | false; mixed diffusion--multiplication words may appear later |
| a slow finite critical plot refutes the exponent | false; \(n=c^{4r+1}\) makes convergence exceptionally pre-asymptotic |
| these limits describe fundamental spacetime | unsupported; every theorem is internal to the declared parabolic model |

## 11. Interpretation

The result sharpens the operational meaning of “the same preparation.”  A
probability distribution is not classified only by weak convergence.  What
the observer sees depends on its width relative to both the mesh and the
diffusion length:

\[
 \text{cell rule}\quad\longrightarrow\quad
 \text{smooth profile}\quad\longrightarrow\quad
 \text{atomic universality}.
\]

The arrows are scale-dependent and reversible only in the sense of changing
the experimental chart.  At finite microscopic time, cell placement is real
operational information.  After the diffusion length dominates the target
variance, that information is erased from this endpoint-marginal protocol.
Near a reflector, geometry leaves one last image term.

This is a mathematical bridge among preparation, dynamics, and observation.
It is not evidence that nature itself is a lattice, a diffusion, or an
information substrate.  Its broader value is methodological: singular limits
should carry preparation metrics, resolution scales, null controls, and
overlap theorems rather than being inferred from one asymptotic route.

## 12. Literature and novelty boundary

The varying-space semigroup background remains the generalized Mosco
framework of Kuwae and Shioya:

- K. Kuwae and T. Shioya, *Convergence of spectral structures: a functional
  analytic theory and its applications to spectral geometry*, Communications
  in Analysis and Geometry 11 (2003), 599--673,
  <https://doi.org/10.4310/CAG.2003.v11.n4.a1>.

Optimal-order lumped-mass parabolic approximation has a classical finite
element literature.  One background reference is:

- C. M. Chen and V. Thomée, *The lumped mass finite element method for a
  parabolic problem*, The ANZIAM Journal 26 (1985), 329--354,
  <https://doi.org/10.1017/S0334270000004549>.

That paper treats a different two-dimensional Dirichlet setting and is not a
direct citation for the present Neumann half-cell proof.  The conservative
Fourier and local variational estimates here are carried out for the declared
path.

Discrete interval heat kernels and their Neumann image structure are also
classical; see:

- J. S. Dowker, *Heat-kernels on the discrete circle and interval* (2012),
  <https://arxiv.org/abs/1207.2096>.

No priority claim is made for Mosco convergence, mass lumping, Poisson
summation, heat-kernel scaling, or characteristic-function bounds.  The
provisional contribution of this stage is their explicit operational assembly:
the chartwise finite error bounds, the direct simultaneous atomic theorem,
the boundary crossover, the discrete-moment obstruction, and the quantitative
critical-resolution barrier.  Literature novelty remains provisional until
independent specialist review.

## 13. Reproduction

Install the dedicated dependencies and run the analytic laboratories and
adversarial controls:

```text
python -m pip install -r oig_viii_three_parameter_requirements.txt
python -m py_compile oig_viii_three_parameter.py \
  test_oig_viii_three_parameter.py \
  test_oig_viii_adversarial_controls.py
python -m unittest -v test_oig_viii_three_parameter.py
python -m unittest -v test_oig_viii_adversarial_controls.py
python oig_viii_three_parameter.py --fast
python oig_viii_three_parameter.py
python -m unittest discover -v
```

The detailed resolved proof is in
`OIG_VIII_RESOLVED_UNIFORM_THEOREM.md`; the finite-cell, simultaneous atomic,
and boundary proofs are in `OIG_VIII_LATTICE_UNIFORM_THEOREM.md`; the numerical
report is `oig_viii_three_parameter.md`; and the independent proof review is
`OIG_VIII_ADVERSARIAL_AUDIT.md`.

The exact finite modal reduction is algebraic.  Numerical phase integrals and
convergence fits are not outward-rounded certificates.  On the reference
environment, 20 of 20 focused Stage VIII tests and 231 of 231 repository tests
pass; the full Stage VIII laboratory completes in about 13 seconds.

## 14. Next research order

1. **Develop the growing-band theorem.** Replace the fixed source port by a
   finite or Sobolev-bounded family, assemble response Gramians, and control
   the smallest nonzero singular value uniformly across the three charts.
2. **Classify diffusion-scale target shapes.** Treat
   \(\sigma_h^2/t\to\lambda\in(0,\infty)\) and combine their characteristic
   functions with the reflecting boundary profile.
3. **Return to cyclic visibility.** Relate multiplication moments to the full
   noncommutative causal-word algebra, then quantify how symmetry breaking
   opens an invisible port.
4. **Develop path-space sensing.** Replace endpoint marginals by jump counts
   and holding-time observables; determine whether their mollifier atlas has
   different null ports.
5. **Extend beyond uniform paths.** Identify which local symbols, reversible
   measures, and heat-kernel bounds preserve the atlas on nonuniform meshes
   and graphs.
6. **Only afterward open the wave branch.** Replace parabolic smoothing by
   finite-speed propagation and determine which preparation and boundary
   phases survive.

The most immediate target is the growing-band response Gramian.  Stage VIII
has controlled one declared source direction across resolution; the next
question is whether a whole operational source space remains stably visible,
not merely pointwise convergent.
