# Operational Information Geometry — explicit uniform lattice constants

## A conservative machine-checkable joint resolution schedule for two ports

**Status:** analytic constant instantiation; no floating-point inequality is
used in the theorem

**Model:** exactly-centred odd-grid full Neumann benchmark

**Interaction:** \(V(x)=1+gx\), \(g=4/5\)

**Ports:** \(\phi_k(x)=\sqrt2\cos(k\pi x)\), \(k=1,2\)

**Purpose:** instantiate the constants left abstract in
OIG_UNIFORM_LATTICE_TRANSFER_THEOREM.md

---

## 1. Explicit theorem

Let \(n\ge3\) be odd, \(h=1/n\), \(\tau\ge1\), and

\[
 t=\tau h^2=\frac{\tau}{n^2}.
\]

Let \(G_n(\tau)\) be the complete finite Gram formed with

\[
 e^{-\tau(L_n+\omega_{n,\ell}V_n)}
\]

and the exactly-centred one-cell target, and let \(G(\tau)\) be the
normalized continuum one-cell lattice Gram.  Then

\[
 \boxed{
 \|G_n(\tau)-G(\tau)\|_2
 \le C_{\sqrt t}\sqrt t+C_hh,}
 \tag{1.1}
\]

where the explicit elementary constants are

\[
 \begin{aligned}
 A&=\left(10\pi^2+\frac{64}{25e^2}\right)^{1/2},\\
 B&=\left\{
 2\left[\left(1+\frac{4}{5\pi e}\right)^2
       +\left(2+\frac{4}{5\pi e}\right)^2\right]
 \right\}^{1/2},\\
 K&=\frac{8\sqrt{2\pi}}{5e},\\
 Q&=\sqrt2\left(\frac{36}{25}+\frac{32}{25e^2}\right),\\
 C_{\sqrt t}&=KA+Q,\qquad C_h=KB.
 \end{aligned}
 \tag{1.2}
\]

The direction-safe rational weakenings

\[
 C_{\sqrt t}<\frac{86}{5},\qquad
 C_h<\frac{629}{125}
 \tag{1.3}
\]

give the convenient global estimate

\[
 \boxed{
 \|G_n(\tau)-G(\tau)\|_2
 <23\frac{\sqrt\tau}{n}.}
 \tag{1.4}
\]

No small-time assumption is needed for (1.1).  To fit the earlier theorem
contract one may take

\[
 \boxed{t_*=1;}
 \tag{1.5}
\]

all schedules below in fact have \(t\ll1\).

For the declared continuum \(H^1\) metric

\[
 S=\operatorname{diag}(1+\pi^2,1+4\pi^2),
\]

\[
 \boxed{
 \|G_n(\tau)-G(\tau)\|_S
 <\frac{23}{1+\pi^2}\frac{\sqrt\tau}{n}
 <\frac{23}{10}\frac{\sqrt\tau}{n}.}
 \tag{1.6}
\]

The normalized continuum atomic tail

\[
 G_\infty=\frac1{2\pi}\int_0^\infty
 s^{-1/2}F(s)F(s)^T\,ds
\]

satisfies

\[
 \boxed{
 \|G(\tau)-G_\infty\|_2<\frac{2}{3\tau},
 \qquad
 \|G(\tau)-G_\infty\|_S<\frac{1}{15\tau}.}
 \tag{1.7}
\]

Thus an explicit admissible choice of the constants requested by the
uniform theorem is

\[
 \boxed{
 C_{L^2}=23,\quad C_{H^1}=23/10,\quad
 C_{\infty,L^2}=2/3,\quad C_{\infty,H^1}=1/15,\quad t_*=1.}
 \tag{1.8}
\]

These constants are intentionally conservative.  Their purpose is to turn
the joint tail into a proof-producing contract, not to predict practical
grid sizes.

---

## 2. Two elementary response estimates

Write

\[
 W=V-I=gx,\qquad 0\preceq W\preceq gI.
\]

For target phase \(s=\tau\omega_{n,\ell}\), define

\[
 b_{n,k}(t,s)
 =\left\langle\mathbf1,
 e^{-(tA_h+sV_h)}\phi_{k,h}\right\rangle_h,
\]

where \(A_h=h^{-2}L_n\), and

\[
 F_k(s)=\int_0^1e^{-sV(x)}\phi_k(x)\,dx.
\]

Both the discrete and continuum sources have exact mean zero.

### Lemma 2.1 — common exponential envelope

For every \(s\ge0\),

\[
 \boxed{
 |b_{n,k}(t,s)|\le gse^{-s},\qquad
 |F_k(s)|\le gse^{-s}.}
 \tag{2.1}
\]

#### Proof

For the continuum response, compare \(e^{-s(I+W)}\) with \(e^{-s}I\).
The latter has zero pairing with \(\phi_k\); Duhamel and
\(\|W\|_\infty\le g\) give the second inequality.

For the finite response, compare \(tA_h+s(I+W_h)\) with
\(tA_h+sI\).  Since \(A_h\mathbf1=0\), the comparison semigroup also has
zero mass response.  Both sides of the Duhamel integrand contribute their
scalar decay factors, whose product is \(e^{-s}\).  Contractivity then gives
the first inequality. \(\square\)

### Lemma 2.2 — explicit amplitude error

Put

\[
 d_k=\left(2(k\pi)^2+\frac{2g^2}{e^2}\right)^{1/2},
 \qquad
 m_k=\sqrt2\,k+\frac{\sqrt2\,g}{\pi e}.
 \tag{2.2}
\]

Then

\[
 \boxed{
 |b_{n,k}(t,s)-F_k(s)|
 \le d_k\sqrt t+m_kh.}
 \tag{2.3}
\]

#### Proof: diffusion part

Compare

\[
 u(r)=e^{-r(tA_h+sV_h)}\phi_{k,h},
 \qquad
 v(r)=e^{-rsV_h}\phi_{k,h}.
\]

The discrete energy identity and Young's inequality give

\[
 \|u(1)-v(1)\|_h^2
 \le t\int_0^1\|A_h^{1/2}v(r)\|_h^2\,dr.
 \tag{2.4}
\]

For midpoint samples, the discrete Dirichlet energy is bounded by the
continuous energy of the interpolated smooth function:

\[
 \|A_h^{1/2}v(r)\|_h
 \le\left\|\partial_x(e^{-rsV}\phi_k)\right\|_{L^2}
 \le e^{-rs}(k\pi+rsg).
 \tag{2.5}
\]

Since

\[
 (a+b)^2\le2a^2+2b^2,\qquad
 ue^{-u}\le e^{-1},
\]

\[
 \int_0^1e^{-2rs}(k\pi+rsg)^2\,dr
 \le2(k\pi)^2+\frac{2g^2}{e^2}=d_k^2.
 \tag{2.6}
\]

Pairing with the unit-norm constant vector therefore contributes at most
\(d_k\sqrt t\).

#### Proof: spatial midpoint part

For every absolutely continuous scalar function \(f\), the composite
midpoint rule obeys

\[
 \left|h\sum_jf(x_j)-\int_0^1f(x)\,dx\right|
 \le\frac h2\int_0^1|f'(x)|\,dx.
 \tag{2.7}
\]

Here

\[
 \|\phi_k'\|_{L^1}=2\sqrt2\,k,\qquad
 \|\phi_k\|_{L^1}=\frac{2\sqrt2}{\pi}.
\]

Thus, for \(f=e^{-sV}\phi_k\),

\[
 \int_0^1|f'|
 \le e^{-s}\left(2\sqrt2\,k
 +\frac{2\sqrt2\,g}{\pi}s\right)
 \le2m_k.
 \tag{2.8}
\]

Equations (2.4)--(2.8) prove (2.3). \(\square\)

For the two-component response vectors \(b_n=(b_{n,1},b_{n,2})^T\) and
\(F=(F_1,F_2)^T\), Minkowski's inequality gives

\[
 \|b_n-F\|_2\le A\sqrt t+Bh,
 \tag{2.9}
\]

with \(A,B\) exactly as in (1.2).

---

## 3. Accumulating the modal amplitude error

For the centre atom on an odd grid, only target modes \(\ell=2r\) survive.
Put

\[
 s_r=4\tau\sin^2\frac{\pi r}{n},
 \qquad 1\le r\le\frac{n-1}{2}.
\]

By (2.1) and (2.9),

\[
 \|b_nb_n^T-FF^T\|_2
 \le2\sqrt2\,g\,s_re^{-s_r}(A\sqrt t+Bh).
 \tag{3.1}
\]

Concavity of sine on \([0,\pi/2]\) gives

\[
 \sin\frac{\pi r}{n}\ge\frac{2r}{n},
 \qquad
 s_r\ge16tr^2.
 \tag{3.2}
\]

Also

\[
 se^{-s}\le\frac2e e^{-s/2}.
\]

For a decreasing Gaussian,

\[
 \sum_{r=1}^{\infty}e^{-8tr^2}
 \le\int_0^\infty e^{-8tx^2}\,dx
 =\frac{\sqrt\pi}{4\sqrt{2t}}.
\]

Since

\[
 \frac{2\sqrt{1+\tau}}n
 =2\sqrt t\sqrt{\frac{1+\tau}{\tau}}
 \le2\sqrt2\,\sqrt t,
\]

we obtain the explicit accumulation bound

\[
 \boxed{
 \frac{2\sqrt{1+\tau}}n
 \sum_{r=1}^{(n-1)/2}s_re^{-s_r}
 \le\frac{\sqrt\pi}{e}.}
 \tag{3.3}
\]

Multiplying (3.1) by the Gram weights therefore proves

\[
 \left\|G_n(\tau)-\widetilde G_n(\tau)\right\|_2
 \le K(A\sqrt t+Bh),
 \tag{3.4}
\]

where

\[
 \widetilde G_n(\tau)
 =\frac{2\sqrt{1+\tau}}n
 \sum_{r=1}^{(n-1)/2}F(s_r)F(s_r)^T
\]

is only an intermediate phase quadrature and \(K\) is given in (1.2).
All noncommuting finite dynamics remain inside \(G_n\); no phase object has
been substituted into the theorem.

---

## 4. Explicit target quadrature error

Let

\[
 H_\tau(\xi)
 =F(\tau\omega(\xi))F(\tau\omega(\xi))^T,
 \qquad
 \omega(\xi)=4\sin^2\frac{\pi\xi}{2}.
\]

The points \(2r/n\) are exactly the composite midpoints of \([h,1]\) with
panel width \(2h\).  For a matrix-valued absolutely continuous function,

\[
 \left\|
 2h\sum_{r=1}^{(n-1)/2}H_\tau(2r/n)
 -\int_h^1H_\tau(\xi)\,d\xi
 \right\|_2
 \le h\int_h^1\|H_\tau'(\xi)\|_2\,d\xi.
 \tag{4.1}
\]

The response envelope and the simple derivative estimate

\[
 |F_k'(s)|\le\frac95e^{-s}
\]

give

\[
 \begin{aligned}
 \int_0^1\|H_\tau'(\xi)\|_2\,d\xi
 &\le\int_0^\infty
 2\|F(s)\|_2\|F'(s)\|_2\,ds\\
 &\le\int_0^\infty
 4g\frac95\,s e^{-2s}\,ds
 =\frac{36}{25}.
 \end{aligned}
 \tag{4.2}
\]

The omitted interval satisfies

\[
 \|H_\tau(\xi)\|_2
 \le2g^2s^2e^{-2s}
 \le\frac{2g^2}{e^2}
 =\frac{32}{25e^2}.
 \tag{4.3}
\]

Finally,

\[
 h\sqrt{1+\tau}
 =\sqrt t\sqrt{\frac{1+\tau}{\tau}}
 \le\sqrt2\,\sqrt t.
\]

Equations (4.1)--(4.3) yield

\[
 \boxed{
 \|\widetilde G_n(\tau)-G(\tau)\|_2
 \le Q\sqrt t.}
 \tag{4.4}
\]

Adding (3.4) and (4.4) proves (1.1).

---

## 5. Direction-safe weakening

Only elementary rational inequalities are needed:

\[
 3<\pi<\frac{22}{7},\qquad
 \frac{19}{7}<e,\qquad
 \frac75<\sqrt2<\frac{10}{7}.
 \tag{5.1}
\]

They imply

\[
 A<10,\qquad
 \frac{4}{5\pi e}<\frac{1}{10},\qquad
 B<\frac{17}{5}.
\]

Moreover,

\[
 K^2=\frac{128\pi}{25e^2}
 <\frac{19712}{9025}
 <\left(\frac{37}{25}\right)^2,
\]

so \(K<37/25\).  The same inequalities give \(Q<12/5\).  Hence

\[
 C_{\sqrt t}<\frac{37}{25}\,10+\frac{12}{5}
 =\frac{86}{5},
\]

and

\[
 C_h<\frac{37}{25}\frac{17}{5}
 =\frac{629}{125}.
\]

Since \(\tau\ge1\) implies \(h\le\sqrt t\),

\[
 C_{\sqrt t}\sqrt t+C_hh
 <\frac{2779}{125}\sqrt t
 <23\sqrt t,
\]

proving (1.3)--(1.4) without decimal evaluation.

Whitening by \(S\) multiplies an \(L^2\) operator bound by at most

\[
 \|S^{-1/2}\|_2^2=\frac{1}{1+\pi^2}<\frac1{10},
\]

which proves (1.6).

---

## 6. Explicit continuum atomic-tail constant

The exact change of variable \(s=\tau\omega(\xi)\) gives

\[
 G(\tau)
 =\frac1{2\pi}\int_0^{4\tau}
 s^{-1/2}a_\tau(s)F(s)F(s)^T\,ds,
\]

where

\[
 a_\tau(s)
 =\sqrt{\frac{1+\tau^{-1}}{1-s/(4\tau)}}.
 \tag{6.1}
\]

For \(0\le s\le2\tau\), \(a_\tau(s)\ge1\) and

\[
 a_\tau(s)-1
 \le\frac{1+s/4}{\tau}.
 \tag{6.2}
\]

Using

\[
 \|F(s)F(s)^T\|_2
 \le2g^2s^2e^{-2s},
\]

the low-phase difference is at most \(C_{\rm low}/\tau\), where

\[
 C_{\rm low}
 =\frac{g^2}{\pi}\left[
 \frac{\Gamma(5/2)}{2^{5/2}}
 +\frac{\Gamma(7/2)}{4\,2^{7/2}}
 \right].
 \tag{6.3}
\]

The rational inequalities (5.1), together with
\(\Gamma(5/2)=3\sqrt\pi/4\) and
\(\Gamma(7/2)=15\sqrt\pi/8\), give

\[
 C_{\rm low}<\frac3{40}.
 \tag{6.4}
\]

For the finite lattice high-phase region \(s\ge2\tau\), return to the
\(\xi\)-integral.  Since \(s^2e^{-2s}\) decreases for \(s\ge1\),

\[
 \sqrt{1+\tau}\int_{\{s\ge2\tau\}}
 \|F(s)F(s)^T\|_2\,d\xi
 \le32g^2\tau^2\sqrt{1+\tau}\,e^{-4\tau}.
\]

The function \(\tau^3\sqrt{1+\tau}e^{-4\tau}\) decreases for
\(\tau\ge1\), hence this contribution is at most

\[
 \frac{C_{\rm high,L}}{\tau},
 \qquad
 C_{\rm high,L}=32g^2\sqrt2\,e^{-4}
 <\frac{27}{50}.
 \tag{6.5}
\]

The omitted atomic tail obeys

\[
 \frac1{2\pi}\int_{2\tau}^\infty
 s^{-1/2}\|F(s)F(s)^T\|_2\,ds
 \le\frac{C_{\rm high,A}}{\tau},
\]

because, for \(\tau\ge1\), integration by parts (or the monotone-tail
estimate applied successively to the half-integer incomplete gamma function)
gives the deliberately weakened bound

\[
 \int_{2\tau}^{\infty}s^{3/2}e^{-2s}\,ds
 \le (2\tau)^{3/2}e^{-4\tau}.
\]

with

\[
 C_{\rm high,A}
 =\frac{g^2}{\pi}2^{3/2}e^{-4}
 <\frac3{250}.
 \tag{6.6}
\]

Therefore

\[
 C_{\infty,L^2}
 <\frac3{40}+\frac{27}{50}+\frac3{250}
 =\frac{627}{1000}
 <\frac23.
\]

Whitening again contributes less than \(1/10\), proving the second half of
(1.7).

---

## 7. Machine-checkable schedules against the Stage X floors

Use the rational floors

\[
 \ell_{L^2}=1.4315\times10^{-7}
 <L_{L^2},
\qquad
 \ell_{H^1}=3.5523\times10^{-9}
 <L_{H^1}.
 \tag{7.1}
\]

The strict inequalities follow from the Stage X separated-frame
common-late-core certificates

\[
 L_{L^2}>1.4315196512138325\times10^{-7},
\qquad
 L_{H^1}>3.5523100221039934\times10^{-9}.
\]

### 7.1 Direct finite-to-lattice transfer for every \(\tau\ge1\)

For each \(\tau\ge1\), choose any odd \(n\) satisfying

\[
 \boxed{
 n\ge322\,000\,000\sqrt\tau
 \quad(L^2),}
 \tag{7.2}
\]

or

\[
 \boxed{
 n\ge1\,300\,000\,000\sqrt\tau
 \quad(H^1).}
 \tag{7.3}
\]

Then exact rational comparison gives

\[
 \frac{23}{322\,000\,000}<\frac{\ell_{L^2}}2,
\qquad
 \frac{23/10}{1\,300\,000\,000}<\frac{\ell_{H^1}}2.
\]

Consequently,

\[
 \boxed{
 G_n(\tau)\succeq\frac{\ell_{L^2}}2I
 \quad\text{under (7.2)},}
 \tag{7.4}
\]

and

\[
 \boxed{
 G_n(\tau)\succeq\frac{\ell_{H^1}}2S
 \quad\text{under (7.3)}.}
 \tag{7.5}
\]

The certified floors are therefore

\[
 7.1575\times10^{-8}
 \quad\text{and}\quad
 1.77615\times10^{-9},
\]

respectively.  These decimal values are terminating rationals.

The prescription is executable: return the least odd integer no smaller
than the right side.  It covers an unbounded set of lattice times across
growing networks and explicitly does not claim that one fixed \(n\) covers
\(\tau=\infty\).

### 7.2 Joint finite-to-atomic transfer

To reserve one quarter of the floor for each of the two errors in

\[
 \|G_n(\tau)-G_\infty\|_S
 \le\|G_n(\tau)-G(\tau)\|_S
 +\|G(\tau)-G_\infty\|_S,
\]

it is sufficient to impose

\[
 \boxed{
 \begin{aligned}
 \tau&\ge18\,629\,000,&
 n&\ge643\,000\,000\sqrt\tau
 &&(L^2),\\
 \tau&\ge75\,069\,000,&
 n&\ge2\,590\,000\,000\sqrt\tau
 &&(H^1).
 \end{aligned}}
 \tag{7.6}
\]

Indeed, the first row makes each error smaller than
\(\ell_{L^2}/4\), and the second does the same with
\(\ell_{H^1}/4\).  Since the atomic Gram inherits the same common-core
floors, (7.6) proves the finite atomic floors

\[
 G_n(\tau)\succeq\frac{\ell_{L^2}}2I
 \quad\text{or}\quad
 G_n(\tau)\succeq\frac{\ell_{H^1}}2S,
 \tag{7.7}
\]

in the corresponding metric.

For the natural discrete energy

\[
 S_n=\operatorname{diag}
 (1+n^2\omega_{n,1},1+n^2\omega_{n,2}),
\]

\(S_n\preceq S\).  Thus every \(H^1\) Loewner floor in
(7.5) or (7.7) also holds with \(S_n\) on the right.

---

## 8. Audit and limitations

### What is now explicit

- Every source-collapse constant for the two cosine ports.
- The accumulation of all active finite target modes.
- The exactly-centred odd-grid target quadrature error.
- \(C_{L^2}\), \(C_{H^1}\), \(C_{\infty,L^2}\),
  \(C_{\infty,H^1}\), and \(t_*\).
- A strict rational comparison against both sharp Stage X uniform floors.
- A machine-checkable \(n(\tau)\) schedule for the full noncommuting
  finite-to-lattice theorem.
- A separate finite-to-atomic schedule with an explicit continuum-tail
  handoff.

### What these constants do not claim

- They are not close to the true grid threshold.  The descriptive sharp law
  is \(O(\tau/n^2)\), whereas the energy estimate used here is only
  \(O(\sqrt\tau/n)\).
- They do not cover even grids, displaced atoms, split targets, reflecting
  boundary charts, growing source bands, or finite sensor frames.
- They do not replace the compact interval certificate at practical grid
  sizes.  They close the analytic unbounded tail over a resolution-aware
  domain.
- The schedules are mathematical existence certificates, not recommended
  simulations: their intentionally huge constants expose exactly how much
  is lost in the endpoint-robust energy bound.

The missing efficiency theorem is still the sharp two-parameter
\(O(\tau/n^2)\) remainder.  It is no longer a dependency for logical
late-lattice closure: (7.2)--(7.7) already provide an explicit,
direction-safe joint theorem.
