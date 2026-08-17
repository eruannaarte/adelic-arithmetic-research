# Operational Information Geometry — uniform lattice transfer theorem

## Compact lattice time, the fixed-grid obstruction, and the joint atomic tail

**Status:** analytic theorem memo; the compact and tail constants have not yet
been converted into an outward-rounded numerical certificate

**Model:** the exactly-centred odd-grid, two-port, full Neumann benchmark

**Interaction:** \(V(x)=1+gx\), \(g=4/5\)

**Ports:** \(\phi_k(x)=\sqrt2\cos(k\pi x)\), \(k=1,2\)

**Continuum normalization:** \(\sqrt{1+\tau}\)

---

## 1. Result and its necessary qualification

The Stage XII theorem at \(\tau=1\) has two different extensions.

1. On every compact interval \(1\leq\tau\leq T<\infty\), the sharp
   exactly-centred expansion persists uniformly:

   \[
   \boxed{
   G_n(\tau)-G(\tau)
   =\frac{E(\tau)}{n^2}+O_T(n^{-3}).}
   \tag{1.1}
   \]

   The coefficient \(E(\tau)\) is explicit.  In particular, the full
   noncommuting finite Neumann Grams converge uniformly on every compact
   lattice-time interval.

2. No fixed finite grid can extend this conclusion uniformly over
   \(1\leq\tau<\infty\).  For fixed \(n\), every nonzero finite target mode
   is exponentially damped and

   \[
   G_n(\tau)\longrightarrow0,
   \qquad
   G(\tau)\longrightarrow G_\infty\succ0.
   \tag{1.2}
   \]

   Thus a claimed fixed-\(n\) certificate on the whole half-line would be
   false.

The correct tail theorem is joint.  Put \(h=1/n\) and physical time

\[
 t=\tau h^2=\frac{\tau}{n^2}.
\]

There are finite constants \(C_S,C_{\infty,S}\), depending only on the
declared two-dimensional source space and source metric \(S\), such that,
for \(\tau\geq1\), \(t\leq t_*\), and sufficiently fine exactly-centred
odd grids,

\[
 \boxed{
 \|G_n(\tau)-G(\tau)\|_S
 \leq C_S\left(\frac{\sqrt\tau}{n}+\frac1n\right),}
 \tag{1.3}
\]

and

\[
 \boxed{
 \|G_n(\tau)-G_\infty\|_S
 \leq C_S\left(\frac{\sqrt\tau}{n}+\frac1n\right)
      +\frac{C_{\infty,S}}{\tau}.}
 \tag{1.4}
\]

Here

\[
 \|A\|_S=\|S^{-1/2}AS^{-1/2}\|_2.
\]

Consequently,

\[
 \tau\to\infty,\qquad \frac{n}{\sqrt\tau}\to\infty,qquad n\ \text{ odd}
 \tag{1.5}
\]

imply \(G_n(\tau)\to G_\infty\) in the declared metric.  More generally, a
fixed but sufficiently large ratio \(n/\sqrt\tau\) already suffices to beat
a fixed positive transfer floor; divergence of the ratio is required only
when the transfer error itself must tend to zero.

Equations (1.1)--(1.5) are the strongest theorem currently justified by the
existing Stage VIII and XII arguments.  They close the logical error in the
informal instruction “take \(\tau\to\infty\) at fixed \(n\)”: that limit is
the wrong experiment.

---

## 2. Exact finite and continuum families

Let \(n\geq3\) be odd, \(h=1/n\), and

\[
 x_j=\frac{j+1/2}{n},\qquad 0\leq j<n.
\]

Let \(L_n\) be the unscaled Neumann path Laplacian, let
\(V_n=\operatorname{diag}(1+gx_j)\), and put

\[
 \omega_{n,\ell}=4\sin^2\!\left(\frac{\pi\ell}{2n}\right).
\]

For \(0\leq\omega\leq4\), \(s=\tau\omega\), define the normalized full
response

\[
 b_{n,k}(\tau,\omega)
 =\left\langle\mathbf1,
 e^{-(\tau L_n+sV_n)}\phi_{k,h}\right\rangle_h,
 \qquad
 \phi_{k,h}(j)=\sqrt2\cos(k\pi x_j).
 \tag{2.1}
\]

This is exactly the physical exponent

\[
 t(A_h+\mu_{\ell,h}V_h)
 =\tau L_n+\tau\omega_{n,\ell}V_n.
\]

For the centre cell \(j_*=(n-1)/2\), exact DCT parity leaves only the
positive even target modes.  The normalized finite Gram is therefore

\[
 \boxed{
 G_n(\tau)
 =\frac{2\sqrt{1+\tau}}{n}
 \sum_{r=1}^{(n-1)/2}
 b_n(\tau,\omega_{n,2r})
 b_n(\tau,\omega_{n,2r})^T.}
 \tag{2.2}
\]

No phase surrogate is used in (2.2).

The multiplication-limit responses are

\[
 F_k(s)=\int_0^1e^{-sV(x)}\phi_k(x)\,dx
 =\sqrt2e^{-s}
 \frac{gs[1-(-1)^ke^{-gs}]}{(gs)^2+(k\pi)^2}.
 \tag{2.3}
\]

Writing \(F=(F_1,F_2)^T\) and

\[
 \omega(\xi)=4\sin^2\frac{\pi\xi}{2},
\]

the normalized continuum lattice Gram is

\[
 \boxed{
 G(\tau)=\sqrt{1+\tau}\int_0^1
 F(\tau\omega(\xi))F(\tau\omega(\xi))^T\,d\xi.}
 \tag{2.4}
\]

For a coefficient vector \(z\), (2.2)--(2.4) are precisely

\[
 z^TG_n(\tau)z
 =\sqrt{1+\tau}\,h\mathcal N_{h,z}(\tau h^2)^2,
 \qquad
 z^TG(\tau)z
 =\sqrt{1+\tau}\,\Psi_z(\tau)^2.
 \tag{2.5}
\]

Identity (2.5) is the bridge to the Stage VIII uniform squared-response
theorem.

---

## 3. Uniform sharp expansion on a compact \(\tau\)-interval

Define

\[
 B_k(s)=\sqrt2\left[(-1)^ke^{-(1+g)s}-e^{-s}\right].
 \tag{3.1}
\]

### Theorem 3.1 — compact-\(\tau\) response expansion

For every finite \(T\geq1\), uniformly for

\[
 1\leq\tau\leq T,qquad 0\leq\omega\leq4,qquad k=1,2,
\]

one has

\[
 \boxed{
 b_{n,k}(\tau,\omega)
 =F_k(s)+h^2D_k(\tau,\omega)+O_T(h^3),
 \qquad s=\tau\omega,}
 \tag{3.2}
\]

where

\[
 \boxed{
 \begin{aligned}
 D_k(\tau,\omega)
 &=\frac{sg}{24}B_k(s)
   +\tau\left[
      \frac{sg}{2}B_k(s)
      +\frac{s^2g^2}{3}F_k(s)
   \right]\\
 &=sg\left(\frac1{24}+\frac\tau2\right)B_k(s)
   +\frac{\tau s^2g^2}{3}F_k(s).
 \end{aligned}}
 \tag{3.3}
\]

At \(\tau=1\), (3.3) is exactly the Stage XII coefficient

\[
 \frac{13}{24}\omega gB_k(\omega)
 +\frac13\omega^2g^2F_k(\omega).
\]

#### Proof

Composite midpoint Euler--Maclaurin applied to
\(e^{-sV}\phi_k\) contributes

\[
 D_k^{\rm mid}=\frac{sg}{24}B_k(s).
\]

Expand the finite semigroup around \(sV_n\).  The first occurrence of
\(L_n\) carries the coefficient \(\tau\), and discrete summation by parts
gives

\[
 \langle p_h,L_nq_h\rangle_h
 =h^2\int_0^1p'q'\,dx+O_T(h^3).
\]

The resulting weak Duhamel coefficient is

\[
 D_k^{\rm dyn}
 =\tau\left[
 \frac{sg}{2}B_k(s)+\frac{s^2g^2}{3}F_k(s)
 \right].
\]

For terms containing at least two \(L_n\)'s, the two exterior Laplacians
act on uniformly smooth endpoint families with \(0\leq s\leq4T\).  Each
has \(\ell_h^2\)-norm \(O_T(h^{3/2})\); every interior Laplacian has norm at
most four.  The \(r\)-th Dyson term is thus bounded by

\[
 C_T h^3\frac{(4T)^{r-2}T^2}{r!},
 \]

and the series is summable uniformly on the compact rectangle.  This is
the Stage XII weak-Dyson argument with its \(\tau\)-factors retained, and
proves (3.2).  \(\square\)

### Theorem 3.2 — compact-\(\tau\) Gram expansion

Put \(D=(D_1,D_2)^T\) and

\[
 \boxed{
 E(\tau)=\sqrt{1+\tau}\int_0^1
 \left[
 F(\tau\omega(\xi))D(\tau,\omega(\xi))^T
 +D(\tau,\omega(\xi))F(\tau\omega(\xi))^T
 \right]d\xi.}
 \tag{3.4}
\]

Then (1.1) holds uniformly on \([1,T]\).

#### Proof

For

\[
 H_{ij,\tau}(\xi)
 =F_i(\tau\omega(\xi))F_j(\tau\omega(\xi)),
\]

one has \(H'_{ij,\tau}(1)=0\).  At the origin,
\(F_1(\tau\omega(\xi))=O_T(\xi^2)\) and
\(F_2(\tau\omega(\xi))=O_T(\xi^4)\).  The exactly-centred target-mode sum
is the composite midpoint rule on \([1/n,1]\), and hence

\[
 \frac2n\sum_{r=1}^{(n-1)/2}H_{ij,\tau}(2r/n)
 -\int_0^1H_{ij,\tau}(\xi)\,d\xi
 =O_T(n^{-4}).
 \tag{3.5}
\]

Insert (3.2) into (2.2), use (3.5) for the leading product, and apply the
same midpoint estimate to the smooth cross term.  The uniform response
remainder contributes \(O_T(n^{-3})\).  This proves (1.1). \(\square\)

### Corollary 3.3 — compact-interval transfer

Let \(S\succ0\) be a fixed declared source metric and suppose

\[
 \lambda_{\min}(G(\tau),S)\geq L_S>0,
 \qquad 1\leq\tau\leq T.
 \tag{3.6}
\]

Then there is an odd \(N(T,S,L_S)\) such that every odd \(n\geq N\)
satisfies

\[
 G_n(\tau)\succeq\frac{L_S}{2}S
 \qquad(1\leq\tau\leq T).
 \tag{3.7}
\]

For the benchmark, the Stage X separated-frame common-late-core certificate
supplies (3.6) on the larger one-cell lattice half-line \(\tau\geq1\), with
the direction-safe floors

\[
 L_{L^2}>1.4315196512138325\times10^{-7},
\]

and

\[
 L_{H^1}>3.5523100221039934\times10^{-9},
 \qquad
 S_{H^1}=\operatorname{diag}(1+\pi^2,1+4\pi^2).
 \tag{3.8}
\]

These are the sharp \(b=7/4\) common-late-core bounds, not values inferred
from the isolated Stage XII point \(\tau=1\).  The independent
\(b=3/2\) full-atlas construction gives the much coarser but still uniform
lattice fallback \(4.2379307829\times10^{-12}\) in raw \(L^2\).  The two
valid certificates answer the same late-lattice lower-bound question with
different sharpness; they must not be confused.

Corollary 3.3 is an existence theorem until an outward bound for
\(\sup_{[1,T]}\|E(\tau)\|_S\) and the \(O_T(n^{-3})\) constant is supplied.
Section 7 records a more efficient direct interval route.

---

## 4. Why fixed \(n\) cannot cover \(\tau\to\infty\)

### Proposition 4.1 — fixed-grid extinction

For every fixed odd \(n\),

\[
 \boxed{\lim_{\tau\to\infty}G_n(\tau)=0.}
 \tag{4.1}
\]

#### Proof

For every active target mode \(\ell=2r\geq2\),

\[
 L_n+\omega_{n,\ell}V_n\succeq\omega_{n,\ell}I.
\]

Thus each normalized two-port response vector satisfies

\[
 \|b_n(\tau,\omega_{n,\ell})\|_2^2
 \leq2e^{-2\tau\omega_{n,\ell}}.
\]

Since \(\omega_{n,2r}\geq\omega_{n,2}>0\), (2.2) gives the explicit bound

\[
 \|G_n(\tau)\|_2
 \leq2\sqrt{1+\tau}\,e^{-2\tau\omega_{n,2}},
 \tag{4.2}
\]

which tends to zero. \(\square\)

The normalized continuum family has the different limit

\[
 \boxed{
 G_\infty
 =\frac1{2\pi}\int_0^\infty
 s^{-1/2}F(s)F(s)^T\,ds.}
 \tag{4.3}
\]

Indeed, putting \(s=\tau\omega(\xi)\), or using the Stage VIII atomic-tail
theorem, gives

\[
 \|G(\tau)-G_\infty\|_S\leq\frac{C_{\infty,S}}{\tau}.
 \tag{4.4}
\]

The affine modulation separates the two cosine ports, so
\(G_\infty\succ0\); the Stage X common-core certificate gives a rigorous
positive lower floor.  Equations (4.1) and (4.4) prove the fixed-grid
impossibility (1.2).

This is not a defect in the finite model.  At large \(\tau\), the active
target band has angular width \(O(\tau^{-1/2})\).  A fixed grid eventually
contains no modes in that shrinking window.

---

## 5. The rigorous joint tail

For the source-uniform step, let \(R_h\phi\) denote the linear midpoint
recovery used in Stage VIII, let \(I_hR_h\phi\) be its piecewise-constant
identification, and define the homogeneous control norm

\[
 \begin{aligned}
 \|\phi\|_{\mathcal X}
 := {}&\|\phi\|_{L^2}+\|\phi\|_{W^{1,\infty}}\\
 &+\sup_{0<h\leq h_0}\left[
 \|R_h\phi\|_h
 +\|A_h^{1/2}R_h\phi\|_h
 +h^{-1}\|I_hR_h\phi-\phi\|_{L^2}
 \right].
 \end{aligned}
 \tag{5.1}
\]

On \(E_2\), exact discrete mean zero is imposed by the DCT recovery.  Every
term in (5.1) is finite for the two cosine ports.

### Lemma 5.1 — homogeneous Stage VIII constant

There is a model constant \(C_{\rm model}\), depending on \(V\), the centre
distance \(d=1/2\), and the fixed upper physical time \(t_*\), but not on
\(\phi\in E_2\), \(h\), or \(\tau\), such that

\[
 \sqrt\tau\left|
 h\mathcal N_{h,\phi}(t)^2-\Psi_\phi(\tau)^2
 \right|
 \leq C_{\rm model}\|\phi\|_{\mathcal X}^2(\sqrt t+h)
 \tag{5.2}
\]

whenever \(\tau\geq1\), \(t=\tau h^2\leq t_*\), and the grid is
sufficiently fine.

#### Proof

This is not an appeal to pointwise constants plus compactness.  Track the
source dependence in the proof of Stage VIII, Theorem 5.2:

- the modal envelope is linear in \(\|R_h\phi\|_h\);
- the multiplication-limit energy estimate is linear in
  \(\|R_h\phi\|_h+\|A_h^{1/2}R_h\phi\|_h\);
- midpoint recovery and total-variation bounds are linear in
  \(\|\phi\|_{W^{1,\infty}}
    +h^{-1}\|I_hR_h\phi-\phi\|_{L^2}\); and
- passing from amplitude errors to squared responses multiplies two such
  linear bounds.

The target Riemann and Abel-summation terms are likewise quadratic in the
same response envelope.  Taking the maximum of the finitely many
model-dependent coefficients gives (5.2).  No division by a source response
or pointwise positivity is used. \(\square\)

### Theorem 5.2 — full-Gram joint transfer

Let \(E_2=\operatorname{span}\{\phi_1,\phi_2\}\), and let \(S\succ0\) be
any fixed metric on its coefficient space.  There are constants
\(C_S<\infty\), \(t_*>0\), and \(n_0\) such that every exactly-centred odd
grid with \(n\geq n_0\), \(\tau\geq1\), and \(t=\tau/n^2\leq t_*\)
satisfies (1.3).

#### Proof

Let \(Cz=z_1\phi_1+z_2\phi_2\).  Because \(C:\mathbb R^2\to\mathcal X\)
is linear and finite dimensional,

\[
 M_{E_2,S}:=\sup_{z^TSz=1}\|Cz\|_{\mathcal X}^2<\infty.
 \tag{5.3}
\]

Apply Lemma 5.1 to \(Cz\), the one-cell profile \(Q=\delta_0\), and the
centre carrier.  There is no profile mismatch.  Multiply (5.2) by
\(\sqrt{(1+\tau)/\tau}\leq\sqrt2\) and use (2.5).  This yields

\[
 \sup_{z^TSz=1}|z^T(G_n-G)z|
 \leq \sqrt2\,C_{\rm model}M_{E_2,S}(\sqrt t+h).
 \tag{5.4}
\]

For a real symmetric matrix the left side is exactly
\(\|G_n-G\|_S\).  Taking
\(C_S=\sqrt2C_{\rm model}M_{E_2,S}\) proves (1.3). \(\square\)

Combining Theorem 5.2 with (4.4) proves (1.4).

### Corollary 5.3 — an honest resolution schedule

Assume the continuum uniform floor

\[
 G(\tau)\succeq L_SS,\qquad\tau\geq1.
 \tag{5.5}
\]

For any \(0<\varepsilon<L_S\), it is sufficient to choose an odd grid with

\[
 \frac{\tau}{n^2}\leq t_*,
 \qquad
 C_S\left(\frac{\sqrt\tau}{n}+\frac1n\right)\leq\varepsilon.
 \tag{5.6}
\]

Then

\[
 \boxed{G_n(\tau)\succeq(L_S-\varepsilon)S.}
 \tag{5.7}
\]

A simple, deliberately nonoptimal sufficient rule for \(\tau\geq1\) is

\[
 n\geq\max\left\{
 \sqrt{\frac{\tau}{t_*}},
 \frac{2C_S\sqrt\tau}{\varepsilon}
 \right\},
 \qquad n\ \text{ odd}.
 \tag{5.8}
\]

Thus the theorem does not require an impossible uniform fixed grid.  It
requires resolution proportional to the width of the active diffusive
band.  To get convergence rather than a fixed error budget, take
\(n/\sqrt\tau\to\infty\).

For an atomic-limit comparison, it is additionally sufficient that

\[
 \frac{C_{\infty,S}}{\tau}\leq\varepsilon_\infty.
\]

Then (1.4) gives the finite atomic floor

\[
 G_n(\tau)\succeq
 (L_{\infty,S}-\varepsilon-\varepsilon_\infty)S.
 \tag{5.9}
\]

---

## 6. Declared continuum and natural discrete \(H^1\) costs

The compact and joint theorems apply directly with the declared continuum
metric

\[
 S=\operatorname{diag}(1+\pi^2,1+4\pi^2).
\]

There is also a useful one-sided transport to the natural discrete energy

\[
 S_n=\operatorname{diag}
 \left(1+n^2\omega_{n,1},1+n^2\omega_{n,2}\right).
 \tag{6.1}
\]

Since \(\sin x\leq x\),

\[
 \boxed{S_n\preceq S.}
 \tag{6.2}
\]

More quantitatively, \(\sin^2x\geq x^2-x^4/3\) gives

\[
 0\preceq S-S_n
 \preceq \frac1{12n^2}
 \operatorname{diag}(\pi^4,(2\pi)^4).
 \tag{6.3}
\]

Therefore any certificate

\[
 G_n\succeq\gamma S
\]

automatically implies

\[
 \boxed{G_n\succeq\gamma S_n,
 \qquad
 \lambda_{\min}(G_n,S_n)\geq\gamma.}
 \tag{6.4}
\]

This is a lower-floor result for the natural discrete energy.  It does not
say that the two cost conventions are identical, and (6.3) must be retained
if a two-sided comparison or a cost-sensitive optimizer switches between
them.

---

## 7. What can already be made proof-producing

On \(1\leq\tau\leq T\), put

\[
 A_{n,\ell}(\tau)=\tau(L_n+\omega_{n,\ell}V_n).
\]

The Stage XII spectral centring becomes

\[
 c_{\ell,\tau}=\tau\left(2+\frac75\omega_{n,\ell}\right),
 \qquad
 \rho_{\ell,\tau}=\tau\left(2+\frac25\omega_{n,\ell}\right)
 \leq\frac{18T}{5}.
\]

For the degree-\(m\) centred Taylor action,

\[
 \left\|e^{-A_{n,\ell}(\tau)}-P_{m,\ell}(\tau)\right\|_2
 \leq
 e^{-\tau\omega_{n,\ell}}
 \frac{\rho_{\ell,\tau}^{m+1}}{(m+1)!}
 \leq
 \frac{(18T/5)^{m+1}}{(m+1)!}.
 \tag{7.1}
\]

Thus every finite compact interval has a terminating outward-rounded
certificate:

1. subdivide \([1,T]\) into rational \(\tau\)-boxes;
2. evaluate the complete tridiagonal Taylor actions with interval
   coefficients;
3. enclose the continuum Gram on the same boxes;
4. diagonalize each symmetric \(2\times2\) error enclosure; and
5. increase \(m\), grid resolution, or box resolution until every box
   closes.

Equation (7.1) is not a tail method: its degree grows with \(T\), and at
fixed \(n\) the desired theorem is false anyway.  The compact Taylor cover
must hand off to Theorem 5.2 with a declared joint grid schedule.

---

## 8. The sharp tail coefficient and the remaining analytic gap

The compact coefficient itself has a clean atomic limit.  Define

\[
 J_k(s)=\frac{sg}{2}B_k(s)+\frac{s^2g^2}{3}F_k(s).
 \tag{8.1}
\]

Dominated convergence in (3.4), after the substitution
\(s=\tau\omega(\xi)\), proves

\[
 \boxed{
 \frac{E(\tau)}{\tau}\longrightarrow
 E_\infty^{(1)}
 :=\frac1{2\pi}\int_0^\infty s^{-1/2}
 \left[F(s)J(s)^T+J(s)F(s)^T\right]ds.}
 \tag{8.2}
\]

This predicts a leading joint discretization error

\[
 h^2E(\tau)\sim tE_\infty^{(1)}.
 \tag{8.3}
\]

A 70-digit, non-rigorous quadrature gives

\[
 E_\infty^{(1)}\approx
 \begin{pmatrix}
 -0.00888442225255&-0.00200532267217\\
 -0.00200532267217&-0.000406971336015
 \end{pmatrix},
\]

with descriptive norms

\[
 \|E_\infty^{(1)}\|_2\approx0.00933484517433,
 \qquad
 \|E_\infty^{(1)}\|_{H^1}\approx0.000828530604875.
 \tag{8.4}
\]

The values in (8.4) are evidence, not theorem inequalities.

The missing sharp theorem is a two-parameter remainder of the schematic
strength

\[
 \|G_n(\tau)-G(\tau)-tE_\infty^{(1)}\|_S
 \leq C_S\left(t^{3/2}+\frac{t}{\tau}
 +\text{controlled lattice-quadrature remainder}\right)
 \tag{8.5}
\]

or another explicit bound of comparable strength.  The current Stage VIII
energy argument proves the safe \(O(\sqrt t)\) estimate (1.3), not (8.5).
Endpoint incompatibility with the Neumann form domain is exactly where a
naive uniform Dyson remainder loses sharpness.  Equation (8.5) must not be
claimed until that boundary contribution has been resolved.

This distinction matters numerically.  The safe theorem asks for a ratio
\(n/\sqrt\tau\) proportional to \(L_S^{-1}\) to beat a floor \(L_S\),
whereas a certified sharp \(O(t)\) theorem would ask only for a ratio
proportional to \(L_S^{-1/2}\).

---

## 9. Exact theorem boundary and next work

### Proved here from the Stage VIII and XII machinery

- the explicit compact-\(\tau\) response coefficient (3.3);
- the uniform compact Gram expansion (1.1);
- uniform finite transfer on every compact \([1,T]\) for all sufficiently
  fine exactly-centred odd grids;
- fixed-grid extinction and therefore the impossibility of an all-\(\tau\)
  certificate at fixed \(n\);
- the full noncommuting joint tail bounds (1.3)--(1.4);
- the sufficient resolution law (5.6)--(5.8);
- direct transport of any continuum-\(H^1\) lower certificate to the
  smaller natural discrete energy through (6.2); and
- the exact atomic limit (8.2) of the sharp compact coefficient.

### Not yet numerically certified

- an outward value of \(C_S\) in (1.3) and
  \(C_{\infty,S}\) in (1.4);
- a finite rational \(\tau\)-box cover joining the existing \(\tau=1\)
  certificate to a chosen handoff time \(T\);
- a machine-verifiable schedule \(n(\tau)\) using those outward constants;
  and
- the sharp two-parameter remainder (8.5).

The immediate proof-producing route is therefore precise: instantiate the
Stage VIII constants for the two cosine ports, build the compact interval
Taylor cover, and let its last box overlap the analytic joint-tail bound.
Only that overlap—not a fixed-grid \(\tau\to\infty\) extrapolation—closes
the complete late-lattice sector.
