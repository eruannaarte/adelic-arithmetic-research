# Operational Information Geometry VII

## The mollifier phase diagram

- **Research status:** analytic theorem package and computational audit complete;
  not peer reviewed
- **Research, theorem development, computation, and writing:** Codex (OpenAI)
- **Originating direction and research environment:** TGN's human founder
- **Predecessors:** Operational Information Geometry V and VI
- **Scope:** the declared one-way parabolic Markov model; not a physical theory

## Abstract

Stages V and VI isolated two apparently different target preparations. Smooth
densities have finite causal jets and second-order fixed-mode continuum limits,
whereas a cell atom has a first-jet norm of order \(h^{-5/2}\) and an
initial-layer response of order \(h^{-1/2}\). This stage joins them by replacing
the atom with a mollifier of physical width \(\varepsilon\).

Three dimensionless quantities control the limit:

\[
 c=\frac{\varepsilon}{h},\qquad
 q=\frac{t}{\varepsilon^2},\qquad
 \tau=\frac{t}{h^2}=c^2q.
\]

For a resolved interior mollifier and a fixed source port, the full target
\(L^2\)-response has the continuum crossover whenever the declared port is
multiplication-visible, \(F_\phi\not\equiv0\),

\[
 \|\mathcal R_\varepsilon(t)\|_2
 \sim \varepsilon^{-1/2}\mathcal P(q).
\]

The phase function is explicit in terms of the mollifier transform and a
high-frequency source profile. If its first nonzero multiplication moment has
order \(r\), then

\[
 \mathcal P(q)\sim C_{\rm early}q^r
 \quad(q\downarrow0),\qquad
 \mathcal P(q)\sim C_{\rm atom}q^{-1/4}
 \quad(q\to\infty).
\]

Thus the early response remembers the mollifier and the multiplication-moment
order, while the late initial layer forgets the mollifier and approaches the
universal one-dimensional atomic exponent \(t^{-1/4}\).

When \(\varepsilon/h\to c<\infty\), the continuum transform is replaced by the
Fourier transform of a limiting probability profile on the integer lattice:

\[
 \|\mathcal R_h(\tau h^2)\|_2
 \sim h^{-1/2}\Psi_Q(\tau).
\]

The exponent is universal but the crossover constant is not. It records
cell placement, splitting rules, and the finite-width lattice profile.
Consequently there is no placement-free mesoscopic theorem without declaring
a lattice phase or passing to a subsequence.

## 1. Why this is the next theorem

Stage VI proves that fixed low-mode operational geometry survives refinement.
It deliberately does not treat a growing target bandwidth or a target atom at
time zero. Stage V proves that this exclusion is real rather than technical:
an atomic first jet diverges.

The present problem is to determine what happens between those endpoints.
The answer is a two-scale phase surface. Width and time cannot be classified
independently because target diffusion resolves length \(\sqrt t\). The mesh
adds the ultraviolet length \(h\).

The phase diagram answers four different questions:

1. When does the response retain the derivatives of a smooth preparation?
2. When does it retain the finite-cell placement rule?
3. When does diffusion erase both and leave the atomic continuum law?
4. At what shrinking width does a lattice-time response change from vanishing
   to diverging?

## 2. Exact continuum response reduction

Let

\[
 A=-\partial_x^2
\]

be the nonnegative Neumann Laplacian on \(L^2(0,1)\). Let

\[
 V(x)=1+g d(x),\qquad 0<v_-\leq V(x)\leq v_+<\infty,
\]

and consider the formal joint generator

\[
 G=A_x\otimes I+V(x)\otimes A_y.
\]

Fix a smooth source port \(\phi\) with

\[
 \|\phi\|_2=1,\qquad \int_0^1\phi(x)\,dx=0.
\]

For the Neumann target modes

\[
 \varphi_0(y)=1,\qquad
 \varphi_\ell(y)=\sqrt2\cos(\ell\pi y),
\]

write \(\nu_\ell=(\ell\pi)^2\). If the target preparation is the probability
density \(\rho\), define

\[
 \beta_\ell(\rho)=\langle\varphi_\ell,\rho\rangle.
\]

The target marginal response has the exact modal coefficients

\[
 r_\ell(t;\rho)
 =\beta_\ell(\rho)
 \left\langle1,e^{-t(A+\nu_\ell V)}\phi\right\rangle,
 \qquad \ell\geq1.
\]

The stationary coefficient is zero because the source has zero mean. Therefore

\[
 \|\mathcal R_\rho(t)\|_{L^2_y}^2
 =\sum_{\ell\geq1}
 |\beta_\ell(\rho)|^2
 \left|\left\langle1,e^{-t(A+\nu_\ell V)}\phi\right\rangle\right|^2.
\]

This is a full target-density norm for one declared source direction. It is
not a fixed-band response and not the full source-simplex tangent norm from
Stage V.

### 2.1 Discrete density normalization

On a grid, \(q_h\) is a probability-mass vector and
\(\rho_h=q_h/h\) is its density vector. For the density-normalized cosine
samples \(\varphi_{\ell,h}\),

\[
 \beta_{\ell,h}
 =\langle\varphi_{\ell,h},\rho_h\rangle_h
 =\sum_jq_{h,j}\varphi_{\ell,h}(j).
\]

The source density \(\phi_h\) is injected into probability space as
\(h\phi_h\); it has zero total mass and unit \(h\)-weighted density norm.
If \(r_h(t)\) is the target marginal mass response, its declared norm is

\[
 \left\|\frac{r_h(t)}h\right\|_h^2
 =h\sum_j\left|\frac{r_{h,j}(t)}h\right|^2
 =\sum_{\ell=1}^{n-1}|r_{\ell,h}(t)|^2.
\]

This is why an atom has bounded individual modal coefficients but a growing
full-band response. Omitting either the mass-to-density conversion or the
\(h\)-weighted output metric changes the phase exponents artificially.

## 3. Mollifier convention

Let \(y_0\in(0,1)\). Let \(\eta\) be an even, nonnegative, smooth probability
density on the line. For the exact theorem, take
\(\eta\in C_c^\infty(\mathbb R)\), with support contained in
\((-R,R)\). For
\(\varepsilon R<\operatorname{dist}(y_0,\{0,1\})\), put

\[
 \rho_\varepsilon(y)
 =\frac1{\varepsilon}
 \eta\!\left(\frac{y-y_0}{\varepsilon}\right).
\]

Define the Fourier transform by

\[
 \widehat\eta(\xi)
 =\int_{\mathbb R}\eta(z)e^{i\xi z}\,dz.
\]

Evenness gives the exact coefficients

\[
 \beta_\ell(\rho_\varepsilon)
 =\sqrt2\cos(\ell\pi y_0)
 \widehat\eta(\ell\pi\varepsilon).
\]

A rapidly decaying noncompact kernel is also admissible after replacing the
displayed density by

\[
 \rho_\varepsilon(y)
 =\frac{1}{\varepsilon Z_\varepsilon}
 \eta\!\left(\frac{y-y_0}{\varepsilon}\right),
 \qquad
 Z_\varepsilon
 =\int_0^1\frac1\varepsilon
 \eta\!\left(\frac{y-y_0}{\varepsilon}\right)dy.
\]

For a Schwartz kernel and a fixed interior centre,
\(Z_\varepsilon=1+o(\varepsilon^N)\) for every \(N\), so the phase theorem is
unchanged. The simple coefficient formula above is exact in the compactly
supported convention; in the normalized noncompact convention it holds up to
the corresponding superalgebraically small truncation error. The numerical
laboratory uses normalized Gaussian cell masses and therefore conserves
probability exactly.

The restriction \(y_0\in(0,1)\) is material. At a reflecting boundary, the
carrier does not average in the same way and the leading norm constant changes.

## 4. The high-frequency source profile

Define

\[
 F_\phi(s)=\int_0^1 e^{-sV(x)}\phi(x)\,dx,\qquad s\geq0.
\]

This is the source-side profile seen when target frequency tends to infinity
while \(t\nu_\ell\) stays fixed.

### Lemma 4.1 — scaled reduced-semigroup limit

If \(t_j\downarrow0\), \(\nu_j\to\infty\), and
\(t_j\nu_j\to s\in[0,\infty)\), then

\[
 \left\langle1,e^{-t_j(A+\nu_jV)}\phi\right\rangle
 \longrightarrow F_\phi(s).
\]

The convergence is locally uniform in \(s\).

### Proof sketch

The quadratic forms

\[
 t_j\int|u'|^2+t_j\nu_j\int V|u|^2
\]

converge to the bounded multiplication form \(s\int V|u|^2\).
Strong semigroup convergence gives the limit. Uniformity on compact
\(s\)-intervals follows from boundedness of \(V\) and a finite-net argument.
\(\square\)

This is a fixed-physical-port strong limit. It is not convergence in operator
norm: source modes whose frequency grows like the mesh frequency retain
source diffusion. In the lattice chart, a target mode with
\(\ell/n\to\xi\) sees
\(4\sin^2(\pi\xi/2)\), not the continuum surrogate \((\pi\xi)^2\).

### Lemma 4.2 — uniform frequency envelope

There are \(a,C>0\) such that

\[
 \left|
 \left\langle1,e^{-t(A+\nu V)}\phi\right\rangle
 \right|
 \leq C(t\nu)e^{-a t\nu}
\]

for every \(t,\nu\geq0\).

### Proof

Choose a positive constant \(v_0\) and compare \(A+\nu V\) with
\(A+\nu v_0I\) by Duhamel's identity. The constant-potential response is zero
because the Neumann heat semigroup preserves the mean of \(\phi\). The two
positive semigroups contribute a common exponential \(e^{-a\nu t}\), and the
single perturbation contributes \(\nu t\). \(\square\)

This envelope supplies the domination needed for every phase integral below.

## 5. The continuum crossover theorem

Define

\[
 \mathcal P_{\eta,\phi}(q)^2
 =
 \int_0^\infty
 |\widehat\eta(\pi u)|^2
 |F_\phi(\pi^2qu^2)|^2\,du,
 \qquad q>0.
\]

### Theorem 5.1 — resolved mollifier phase law

Suppose \(\varepsilon_j\downarrow0\) and

\[
 \frac{t_j}{\varepsilon_j^2}\longrightarrow q\in(0,\infty).
\]

Then

\[
 \boxed{
 \varepsilon_j
 \|\mathcal R_{\rho_{\varepsilon_j}}(t_j)\|_2^2
 \longrightarrow
 \mathcal P_{\eta,\phi}(q)^2.}
\]

If \(\mathcal P_{\eta,\phi}(q)>0\), equivalently,

\[
 \|\mathcal R_{\rho_\varepsilon}(t)\|_2
 \sim \varepsilon^{-1/2}
 \mathcal P_{\eta,\phi}(t/\varepsilon^2).
\]

### Proof

Set \(u=\ell\varepsilon\). Lemma 4.1 supplies the pointwise reduced-response
limit

\[
 \left\langle1,e^{-t(A+\nu_\ell V)}\phi\right\rangle
 \longrightarrow F_\phi(\pi^2qu^2).
\]

For interior \(y_0\),

\[
 2\cos^2(\ell\pi y_0)
 =1+\cos(2\ell\pi y_0).
\]

Lemma 4.2 first gives an integrable envelope and reduces the argument to a
compact \(u\)-interval. On that interval, the rescaled squared-weight step
functions converge in \(L^1\) to the displayed integrand. Approximation by a
smooth compactly supported weight, followed by the Riemann--Lebesgue lemma,
then removes the carrier term
\(\cos(2\ell\pi y_0)\). The nonoscillatory Riemann sum is exactly the displayed
integral. \(\square\)

The factor \(\varepsilon^{-1/2}\) is the square-root growth in the number of
active target modes. The phase function contains all nontrivial time and
preparation dependence.

## 6. Multiplication-moment order and the two endpoints

Let

\[
 m_j=\int_0^1V(x)^j\phi(x)\,dx.
\]

Since \(m_0=0\), define the multiplication-moment order

\[
 r_*=\min\{j\geq1:m_j\neq0\},
\]

when this set is nonempty. Then

\[
 F_\phi(s)
 =\frac{(-s)^{r_*}}{r_*!}m_{r_*}
 +O(s^{r_*+1}).
\]

### Theorem 6.1 — early and atomic asymptotics

Assume \(\eta\in H^{2r_*}(\mathbb R)\). Then

\[
 \mathcal P_{\eta,\phi}(q)
 \sim
 \frac{|m_{r_*}|}{r_*!}
 \|\eta^{(2r_*)}\|_2 q^{r_*}
 \qquad(q\downarrow0).
\]

Also, always,

\[
 q^{1/4}\mathcal P_{\eta,\phi}(q)
 \longrightarrow C_\phi
 \qquad(q\to\infty),
\]

where

\[
 C_\phi^2
 =\int_0^\infty|F_\phi(\pi^2z^2)|^2\,dz.
\]

If \(C_\phi>0\), equivalently \(F_\phi\not\equiv0\), this limit can be
written as
\(\mathcal P_{\eta,\phi}(q)\sim C_\phi q^{-1/4}\).

### Proof

For \(q\downarrow0\), insert the first nonzero Taylor term of \(F_\phi\).
The identity

\[
 \int_0^\infty
 \pi^{4r}u^{4r}|\widehat\eta(\pi u)|^2\,du
 =\|\eta^{(2r)}\|_2^2
\]

is Parseval's theorem. For \(q\to\infty\), set \(z=\sqrt q\,u\) and use
\(\widehat\eta(0)=1\) with dominated convergence. \(\square\)

Consequently, in the iterated limit in which
\(\varepsilon\downarrow0\) at fixed
\(q=t/\varepsilon^2\) and then \(q\downarrow0\),

\[
 \|\mathcal R_{\rho_\varepsilon}(t)\|_2
 \sim
 \frac{|m_{r_*}|}{r_*!}
 \|\eta^{(2r_*)}\|_2
 t^{r_*}\varepsilon^{-(2r_*+1/2)}.
\]

If \(C_\phi>0\), the opposite joint regime gives

\[
 \|\mathcal R_{\rho_\varepsilon}(t)\|_2
 \sim C_\phi t^{-1/4}
\]

when \(\varepsilon^2\ll t\downarrow0\).

The late display also admits a direct joint proof by scaling modes with
\(\sqrt t\). The early display is a genuine arbitrary joint limit for the
orders and regularity stated in Section 12; for higher order it remains an
iterated profile asymptotic unless the mixed-word remainder is controlled.

The \(t^{-1/4}\) exponent is the one-dimensional \(L^1\)-to-\(L^2\) heat
scaling, but its constant here contains the declared operational source
profile rather than a bare heat kernel.

If every \(m_j\) vanishes, the leading high-frequency multiplication profile
is identically zero. This does not imply all-time invisibility: lower target
powers containing source-diffusion operators can survive. For example, choose
a positive asymmetric smooth \(V\) that has the same value and is flat to all
orders at both endpoints, and put
\(\phi=V'/\|V'\|_2\). Then

\[
 \int_0^1V^r\phi\,dx=0\quad\text{for every }r\geq0,
\]

but, for \(K_\lambda=A+\lambda V\),

\[
 \left\langle1,K_\lambda^3\phi\right\rangle
 =-\frac{\lambda^2}{2\|V'\|_2}\int_0^1(V')^3dx,
\]

which is generically nonzero. Thus \(r_*\) is not the complete causal order.
A true common symmetry can force the stronger all-time zero. Higher continuum
jets also require the appropriate iterated Neumann-domain compatibility;
finite matrix Taylor coefficients need not converge to continuum derivatives
without it.

## 7. Exact ramp specialization

For

\[
 V(x)=1+gx,\qquad
 \phi_k(x)=\sqrt2\cos(k\pi x),
\]

the high-frequency profile has the closed form

\[
 F_k(s)
 =\sqrt2e^{-s}
 \frac{gs\,[1-(-1)^ke^{-gs}]}
 {(gs)^2+(k\pi)^2}.
\]

Therefore

\[
 r_*(k)=
 \begin{cases}
 1,&k\ \text{odd},\\
 2,&k\ \text{even}.
 \end{cases}
\]

The parity zero in Stage V's first jet is thus not silence for the ramp. Even
source modes enter one multiplication order later in the high-frequency
profile.

At \(g=0.8\), the atomic constants computed from the phase integral are

\[
 C_{\phi_1}=0.02962432844,\qquad
 C_{\phi_2}=0.00318183858.
\]

These are continuum quadratures of an explicit positive integrand, not fitted
exponents.

## 8. The lattice-scale phase law

Let \(h=1/n\), let \(A_h=h^{-2}L_n\), and use the density inner product

\[
 \langle u,v\rangle_h=h\sum_i u_iv_i.
\]

For every discrete statement in this section, additionally assume
\(V\in C([0,1])\), set

\[
 x_i=(i+\tfrac12)h,
 \qquad V_h=\operatorname{diag}(V(x_i)),
\]

and use a cell-centred recovery \(\phi_h\) of the fixed smooth source port,
normalized in \(\langle\cdot,\cdot\rangle_h\) and adjusted to have exact
discrete mean zero, such that \(J_h\phi_h\to\phi\) and
\(L_n\phi_h\to0\) strongly. The canonical cosine samples satisfy these
conditions exactly. The reduced block below is
\(K_{\ell,h}=A_h+\mu_{\ell,h}V_h\).

Choose cells \(j_n\) with \(x_{j_n}\to y_0\in(0,1)\). Suppose a target
probability preparation has an asymptotic profile around those cells:

\[
 q_{j_n+m,h}\longrightarrow Q_m,
\qquad
 Q_m\geq0,\qquad
 \sum_{m\in\mathbb Z}Q_m=1,
\]

with uniform tightness of the tails. Define its lattice transform

\[
 B_Q(\theta)=\sum_{m\in\mathbb Z}Q_me^{im\theta}
\]

and the path symbol

\[
 \omega(\xi)=4\sin^2\!\left(\frac{\pi\xi}{2}\right).
\]

Finally, define

\[
 \Psi_{Q,\phi}(\tau)^2
 =
 \int_0^1
 |B_Q(\pi\xi)|^2
 |F_\phi(\tau\omega(\xi))|^2\,d\xi.
\]

### Theorem 8.1 — mesoscopic lattice limit

For each fixed \(\tau>0\),

\[
 \boxed{
 h\|\mathcal R_h(\tau h^2;q_h)\|_{2,h}^2
 \longrightarrow
 \Psi_{Q,\phi}(\tau)^2.}
\]

If \(\Psi_{Q,\phi}(\tau)>0\), this gives

\[
 \|\mathcal R_h(\tau h^2;q_h)\|_{2,h}
 \sim h^{-1/2}\Psi_{Q,\phi}(\tau).
\]

### Proof sketch

In target DCT mode \(\ell\),

\[
 h^2\mu_{\ell,h}
 =\omega(\ell/n).
\]

The scaled source operator is

\[
 h^2K_{\ell,h}
 =L_n+\omega(\ell/n)V_h.
\]

The bounded operators \(L_n\) converge strongly to zero on fixed physical
functions, while \(V_h\) converges to multiplication by \(V\). Hence the
source response tends to \(F_\phi(\tau\omega(\xi))\).

The target coefficient is the real part of a carrier at \(x_{j_n}\) times
\(B_Q(\pi\xi)\). Squaring and summing over \(\ell\) leaves
\(|B_Q|^2\). Uniform \(\ell^1\) convergence of the localized profiles gives
uniform convergence of their lattice transforms; the response weights have an
\(L^1\) limiting step function. The Riemann--Lebesgue lemma removes the second
carrier harmonic because \(y_0\) is interior. The DCT sum becomes the displayed
integral.
\(\square\)

As in Lemma 4.1, this reduction is strong on each fixed physical source port,
not uniform over source modes growing with \(n\).

## 9. Cell averages, lattice phase, and the unresolved limit

Suppose the mollifier centre is

\[
 y_h=x_{j_h}+\theta_hh,\qquad
 \theta_h\to\theta\in[-1/2,1/2],
\]

and \(\varepsilon_h/h\to c\in(0,\infty)\). Cell-average discretization gives

\[
 Q_m^{c,\theta}
 =
 \int_{m-1/2}^{m+1/2}
 \frac1c\eta\!\left(\frac{z-\theta}{c}\right)\,dz.
\]

Theorem 8.1 applies with this \(Q^{c,\theta}\). The dependence on \(\theta\)
is unavoidable.

Cell averages are the canonical positive preparation rule here because they
conserve mass at every width. Normalized point samples, nearest-cell
atomization, and moment-preserving two-cell placement are different models:
point samples of a compactly supported subcell mollifier can miss every cell
centre, while nearest-cell placement discards the width even when it is
resolved. A positive two-cell rule can preserve the first moment at an
interior point, but its ultraviolet constant still varies with the split.

If \(c\downarrow0\) and \(|\theta|<1/2\), then

\[
 Q^{c,\theta}\to\delta_0,\qquad B_Q\to1.
\]

If the centre approaches a cell boundary on the mollifier scale, mass may
split across two cells. For an even mollifier centred exactly on a boundary,

\[
 Q=\tfrac12(\delta_0+\delta_1),
\qquad
 |B_Q(\pi\xi)|^2=\cos^2(\pi\xi/2).
\]

Therefore “\(\varepsilon/h\to0\)” does not by itself select one atomic
crossover function. It selects a family indexed by the limiting placement
rule.

### Proposition 9.1 — first-jet lattice fingerprint

Let \(\Delta_{\mathbb Z}Q\) be the raw lattice Laplacian of \(Q\). If
\(m_1\neq0\), then

\[
 h^{5/2}\|\dot{\mathcal R}_h(0;q_h)\|_{2,h}
 \longrightarrow
 |m_1|\|\Delta_{\mathbb Z}Q\|_{\ell^2}.
\]

For a one-cell atom,

\[
 \|\Delta_{\mathbb Z}\delta_0\|_2=\sqrt6,
\]

whereas an equal two-cell split has constant \(1\). The exponent agrees, but
the ultraviolet coefficient changes by a factor \(\sqrt6\).

This proposition is an interior full-line stencil statement. At a reflecting
boundary the half-line stencil changes the coefficient. For the Stage V full
source tangent and ramp normalization, the corresponding scaled constants
are \(1/\sqrt2\) for an interior atom, \(1/\sqrt6\) for a boundary atom, and
\(1/\sqrt{12}\) for an equal interior split after division by \(g\). A
positive preparation on internal cell centres also cannot preserve the exact
first moment of a point lying inside the boundary half-cell.

## 10. Lattice endpoint asymptotics

If \(r_*\) is finite, then

\[
 \Psi_{Q,\phi}(\tau)
 \sim
 \frac{|m_{r_*}|}{r_*!}\tau^{r_*}
 \left(
 \int_0^1|B_Q(\pi\xi)|^2
 \omega(\xi)^{2r_*}\,d\xi
 \right)^{1/2}
\]

as \(\tau\downarrow0\). For the one-cell atom,

\[
 \int_0^1\omega(\xi)^{2r}\,d\xi
 =\binom{4r}{2r}.
\]

At the other endpoint, every probability profile has \(B_Q(0)=1\), and

\[
 \tau^{1/4}\Psi_{Q,\phi}(\tau)
 \longrightarrow C_\phi
 \qquad(\tau\to\infty).
\]

When \(C_\phi>0\), this is equivalently
\(\Psi_{Q,\phi}(\tau)\sim C_\phi\tau^{-1/4}\).

Thus finite-cell preparation details survive at \(t\asymp h^2\) but disappear
in the iterated lattice-profile limit \(\tau\to\infty\). A single uniform
statement along every joint path \(h^2\ll t\downarrow0\) belongs to the
three-parameter target in Section 18.

## 11. The bridge between the two phase functions

For cell averages of a resolved mollifier, let \(Q^c\) denote the centred
lattice profile of width \(c\). Then, as \(c\to\infty\),

\[
 c^{1/2}\Psi_{Q^c,\phi}(c^2q)
 \longrightarrow
 \mathcal P_{\eta,\phi}(q)
\]

for every \(q>0\).

Indeed, only \(\xi=O(c^{-1})\) contributes. With \(u=c\xi\),

\[
 \omega(u/c)\sim\pi^2u^2/c^2,
\qquad
 B_{Q^c}(\pi u/c)\to\widehat\eta(\pi u).
\]

Since \(\varepsilon=ch\),

\[
 h^{-1/2}\Psi_{Q^c,\phi}(c^2q)
 \sim
 \varepsilon^{-1/2}\mathcal P_{\eta,\phi}(q).
\]

The continuum and lattice theorems are therefore two charts of one phase
surface, not competing approximations.

## 12. Continuum critical shrinking widths

Let

\[
 \varepsilon_h=h^\alpha,\qquad 0<\alpha<1,
\qquad t_h=\tau h^2.
\]

Then \(c_h\to\infty\) and

\[
 \kappa_h=\frac{t_h}{\varepsilon_h^2}
 =\tau h^{2-2\alpha}\longrightarrow0.
\]

For the proved joint statement, specialize the source to a fixed Neumann
cosine port \(\phi_k=\sqrt2\cos(k\pi x)\). The detailed proof memo proves the
genuine joint continuum estimate for \(r_*=1\), and for \(r_*=2\) when
\(V\in W^{1,\infty}\). For \(r_*\geq3\), additionally assume that the joint
source-diffusion remainder is \(o(\kappa_h^{r_*})\) in the weighted modal norm;
this is not automatic because mixed words in \(A\) and \(V\) can dominate
specially chosen joint paths. Under the proved or declared remainder
hypothesis, the continuum response satisfies

\[
 \|\mathcal R_{\varepsilon_h}(t_h)\|_2
 \asymp
 h^{\,2r_*-\alpha(2r_*+1/2)}.
\]

The critical exponent is

\[
 \boxed{\alpha_c(r_*)=\frac{4r_*}{4r_*+1}.}
\]

Hence the response:

- vanishes for \(\alpha<\alpha_c\);
- stays order one for \(\alpha=\alpha_c\); and
- diverges for \(\alpha>\alpha_c\).

For the ramp,

\[
 \alpha_c(\phi_k)=
 \begin{cases}
 4/5,&k\text{ odd},\\
 8/9,&k\text{ even}.
 \end{cases}
\]

This is a direct connection between multiplication-moment selection and the
geometric rate at which a preparation becomes singular. It must not be read as
a general formula for the first nonzero full causal jet.

There is a second, independent boundary. Stage VI's fixed-mode theorem alone
does not transfer this growing-band display to the finite grid. The detailed
memo supplies a narrower direct proof for the canonical midpoint ramp: on the
effective band the lattice dispersion and conservative cell coefficients
converge uniformly; repeated discrete summation by parts controls the tail;
and reflection makes the even-mode discrete first moment exactly zero. Thus
the canonical discrete ramp also has the \(4/5\) and \(8/9\) thresholds. For a
general order-two discretization one needs the quantitative cancellation

\[
 m_{1,h}=o(\kappa_h),\qquad
 \kappa_h=t_h/\varepsilon_h^2,
\]

not merely \(m_{1,h}\to0\). A uniform three-parameter error theorem covering
all ports, preparations, and joint paths remains the next certification
target.

## 13. Fixed positive time forgets the ultraviolet rule

### Theorem 13.1 — fixed-time atomic universality

Assume the Stage VI fixed-mode hypotheses: \(V\in W^{2,\infty}(0,1)\) is
strictly positive and sampled at cell centres, and \(\phi\) is a fixed finite
linear combination of smooth Neumann cosine ports with its corresponding
density-normalized grid recovery. Let \(q_h\) be any target probability
preparations converging weakly to an interior point mass at \(y_0\). For every
\(0<t_0<T<\infty\), the reconstructed full target responses converge in
\(L^2\), uniformly for \(t\in[t_0,T]\), to

\[
 \mathcal R_{\delta_{y_0}}(t,y)
 =
 \sum_{\ell\geq1}
 \varphi_\ell(y_0)
 \left\langle1,e^{-t(A+\nu_\ell V)}\phi\right\rangle
 \varphi_\ell(y).
\]

### Proof sketch

For every fixed target mode, weak convergence gives
\(\beta_{\ell,h}\to\varphi_\ell(y_0)\), and Stage VI gives convergence of the
source-side response. Uniformly in \(h\),

\[
 |\beta_{\ell,h}|\leq\sqrt2,
\qquad
 |F_{\ell,h}(t)|\leq Ct\mu_{\ell,h}e^{-at\mu_{\ell,h}}.
\]

The path bound \(\mu_{\ell,h}\geq4\ell^2\) gives a summable target-mode tail
for \(t\geq t_0\). Low-mode convergence plus the tail bound proves the claim.
\(\square\)

The nearest-cell atom, a split atom, and every vanishing-width mollifier have
the same fixed-positive-time limit. Their difference is an initial-layer
phenomenon.

## 14. Falsification ledger

| Tempting statement | Correct boundary |
|---|---|
| width alone determines the phase | false; \(t/\varepsilon^2\) is equally essential |
| \(\varepsilon/h\to0\) selects one atom | false at cell boundaries or without a limiting lattice phase |
| every source has the \(4/5\) threshold | false; under the joint remainder condition it is \(4r_*/(4r_*+1)\) |
| first-jet silence means all-time silence | false for even ramp modes; their multiplication profile begins quadratically |
| all multiplication moments zero means all-time silence | false; mixed source-diffusion words can survive without an exact symmetry |
| the boundary has the interior constant | false; carrier averaging changes at \(y_0=0,1\) |
| the multiplication limit holds in operator norm | false; mesh-frequency source modes retain source diffusion |
| every smooth-looking kernel has the early Sobolev constant | false; the order-\(r\) law requires \(\eta\in H^{2r}\) |
| a Gaussian on \([0,1]\) is automatically normalized | false; use \(Z_\varepsilon\) or conservative cell masses |
| every continuum critical width automatically transfers to the grid | false; the canonical ramp has a direct proof, but general ports require growing-band and moment-error control |
| \(t^{-1/4}\) holds at arbitrary fixed time | false; it is a small-time atomic asymptotic |
| fixed-time universality controls \(t\asymp h^2\) | false; the finite lattice transform survives there |
| full target \(L^2\) and fixed-band norms are interchangeable | false; only the growing-band norm sees the phase transition |

## 15. Interpretation

This stage gives a precise example of operational geometry as a relation among
preparation, dynamics, resolution, and observation norm.

The preparation is not simply “smooth” or “atomic.” It has a width relative to
both the mesh and the diffusion length. Before diffusion crosses that width,
the response sees derivatives of the preparation. At the mesh scale, it sees
the actual allocation of mass among cells. After diffusion crosses both
lengths, those details disappear and only the atomic continuum law remains.

Nothing here identifies a physical substrate of nature. The result is a
controlled bridge inside a parabolic model. Its value is that the bridge now
has an explicit crossover function, sharp exponents, and declared failure
modes rather than a qualitative appeal to “smoothing.”

## 16. Literature and novelty boundary

The varying-form and strong-semigroup machinery used in the high-frequency
reduction belongs to the generalized Mosco framework developed by Kuwae and
Shioya:

- K. Kuwae and T. Shioya, *Convergence of spectral structures: a functional
  analytic theory and its applications to spectral geometry*, Communications
  in Analysis and Geometry 11 (2003), 599--673,
  <https://www.intlpress.com/site/pub/files/_fulltext/journals/cag/2003/0011/0004/CAG-2003-0011-0004-a001.pdf>.

Heat-kernel smoothing and its short-time scaling are classical; one general
reference is:

- L. Saloff-Coste, *The heat kernel and its estimates*, in *Probabilistic
  Approach to Geometry*, Advanced Studies in Pure Mathematics 57 (2010),
  405--436,
  <https://projecteuclid.org/ebooks/advanced-studies-in-pure-mathematics/Probabilistic-Approach-to-Geometry/chapter/The-heat-kernel-and-its-estimates/10.2969/aspm/05710405.pdf>.

No priority claim is made for these general mechanisms. The contribution of
this stage is their explicit operational assembly in the declared model: the
density normalization, the continuum and lattice phase functions, their
matching law, port-dependent multiplication orders, and the preparation-rule
falsification ledger. That novelty assessment remains provisional until
independent specialist review.

## 17. Reproduction

Install the dedicated dependencies and run both the main and adversarial
laboratories:

    python -m pip install -r oig_vii_mollifier_requirements.txt
    python -m py_compile oig_vii_mollifier_phase.py \
      test_oig_vii_mollifier_phase.py \
      oig_vii_adversarial_controls.py \
      test_oig_vii_adversarial_controls.py
    python -m unittest -v test_oig_vii_mollifier_phase.py
    python oig_vii_mollifier_phase.py --fast
    python oig_vii_mollifier_phase.py
    python oig_vii_adversarial_controls.py
    python -m unittest -v test_oig_vii_adversarial_controls.py
    python -m unittest discover -v

The analytic details are in
[the continuum proof memo](OIG_VII_CONTINUUM_MOLLIFIER_THEOREM.md), the
finite-generator and high-precision evidence is in
[the computational report](oig_vii_mollifier_phase.md), and the independent
counterexamples are in
[the adversarial audit](OIG_VII_ADVERSARIAL_AUDIT.md). The improper scalar
integrals are checked at 60 decimal digits but are not outward-rounded interval
certificates. The complete finite-grid versus modal identity is exact up to
floating roundoff; simultaneous three-parameter convergence remains a theorem
target rather than a computationally inferred claim.

On the reference environment, the two focused suites pass 25 of 25 tests and
the complete repository passes 211 of 211 tests. The full Stage VII numerical
audit uses no external machine and completes in roughly 18 seconds on the
current host.

## 18. Next research order

1. **Prove the uniform three-parameter comparison.** Bound the finite response
   against the continuum or lattice phase as a function of
   \(h,\varepsilon,t\), thereby certifying general all-port discrete
   critical-width laws and every joint atomic tail.
2. **Prove the boundary chart.** Replace the interior carrier average by the
   reflected half-line and boundary-layer laws.
3. **Develop the growing-band theorem.** Classify simultaneous source and
   target bandwidths beyond one fixed source direction.
4. **Return to cyclic visibility.** Compare multiplication-moment order with
   the full noncommutative causal-word hierarchy, then quantify how weak
   symmetry breaking opens formerly invisible singular values.
5. **Develop path-space sensing.** Ask whether jump clocks see a different
   mollifier phase surface than endpoint marginals.
6. **Only afterward open the wave branch.** Replace parabolic smoothing by
   finite-speed propagation and determine which operational phase ideas
   survive.
