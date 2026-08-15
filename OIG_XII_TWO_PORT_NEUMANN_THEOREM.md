# Operational Information Geometry XII — the two-port Neumann transfer theorem

## A sharp asymptotic law and two rigorous finite crossings

**Status:** analytic Stage XII memo

**Chart:** one-cell lattice, \(\tau=1\)

**Interaction:** \(V(x)=1+\frac45x\)

**Ports:** \(\sqrt2\cos(\pi x)\) and \(\sqrt2\cos(2\pi x)\)
**Target:** one atomic cell centred exactly at \(x=1/2\) on an odd grid

---

## 1. Result

Stage XI left a very narrow numerical target.  For the complete
cell-centred Neumann dynamics, the two-port \(L^2\)-relative Gram error
appeared to cross the inherited continuum floor near \(n=383\).  Refining
the odd, exactly-centred grid sequence moves the transition to the adjacent
pair

\[
 n=343,\qquad n=345.
\]

The crossing can be proved without commuting diffusion and modulation and
without forming a floating-point matrix exponential.  A centred Taylor
action applied to the *full* tridiagonal generator gives

\[
 \begin{aligned}
 \delta^{L^2}_2(343)&>1.4388972111\times10^{-7}
                    >L^{L^2}_2,\\
 \delta^{L^2}_2(345)&<1.4223287203\times10^{-7}
                    <L^{L^2}_2,
 \end{aligned}
\]

where

\[
 L^{L^2}_2
 >1.4315196512138325\times10^{-7}
\]

is the exact Stage X late-core lower certificate.  Consequently the
complete finite Gram at \(n=345\) has the direction-safe inherited floor

\[
 \boxed{
 \lambda_{\min}(G^{\rm full}_{345})
 >9.1909309837\times10^{-10}.}
\]

The declared continuum-\(H^1\) coefficient metric has a later transition:

\[
 n=647\quad\hbox{fails the transfer inequality},\qquad
 n=649\quad\hbox{passes it}.
\]

More precisely, with

\[
 S_{H^1}=\operatorname{diag}(1+\pi^2,1+4\pi^2)
\]

and the Stage X floor

\[
 L^{H^1}_2>3.5523100221039934\times10^{-9},
\]

the same full-generator enclosure gives

\[
 \begin{aligned}
 \delta^{H^1}_2(647)&>3.5690170591\times10^{-9}
                     >L^{H^1}_2,\\
 \delta^{H^1}_2(649)&<3.5470634870\times10^{-9}
                     <L^{H^1}_2,
 \end{aligned}
\]

and hence

\[
 \boxed{
 \lambda_{\min}(G^{\rm full}_{649},S_{H^1})
 >5.2465351803\times10^{-12}.}
\]

These are local theorems at \(\tau=1\), not finite-grid theorems for the
whole Stage X atlas.  Rejection of \(n=343\) or \(647\) means that the
particular perturbative transfer inequality fails there; it does **not** say
that the finite Gram is singular.

There is also a sharp analytic explanation for both grid scales.  If
\(G_n\) denotes the complete two-port finite Gram and \(G\) its continuum
lattice-phase limit, then along the exactly-centred odd grids

\[
 \boxed{
 G_n-G=\frac{E}{n^2}+O(n^{-3}),}
\]

with an explicit matrix \(E\).  Its \(L^2\) norm is approximately
\(0.0169372547863\), while its declared-\(H^1\) whitened norm is approximately
\(0.00149431066943\).  Dividing these constants by the two Stage X floors
predicts transition scales \(343.97\) and \(648.58\), respectively.  The
rigorous finite certificates occur at the first odd grid above each of those
asymptotic predictions.

---

## 2. The exact finite object

Let \(n\) be odd, \(h=1/n\), and

\[
 x_j=\frac{j+1/2}{n},\qquad 0\le j<n.
\]

Let \(L_n\) be the unscaled Neumann path Laplacian,

\[
 L_n=
 \begin{pmatrix}
 1&-1\\
 -1&2&-1\\
 &\ddots&\ddots&\ddots\\
 &&-1&2&-1\\
 &&&-1&1
 \end{pmatrix},
\]

and put

\[
 V_{n,j}=1+\frac45x_j,
 \qquad
 \omega_{n,\ell}=4\sin^2\!\left(\frac{\pi\ell}{2n}\right).
\]

The two Euclidean-orthonormal source ports are

\[
 u_{n,k}(j)=\sqrt{\frac2n}\cos(k\pi x_j),
 \qquad k=1,2.
\]

For target mode \(\ell\), define the complete amplitude

\[
 a_{n,\ell k}
 =\mathbf1^T
 \exp[-(L_n+\omega_{n,\ell}V_n)]u_{n,k},
\]

and its continuum-scaled version

\[
 b_{n,k}(\omega_{n,\ell})=\frac{a_{n,\ell k}}{\sqrt n}.
\]

Equivalently, if \(\phi_{k,h}(j)=\sqrt2\cos(k\pi x_j)\), then

\[
 b_{n,k}(\omega)
 =\langle\mathbf1,e^{-(L_n+\omega V_n)}\phi_{k,h}\rangle_h,
 \qquad
 \langle p,q\rangle_h=h\sum_jp_jq_j.
\]

The centre cell is \(j_*=(n-1)/2\), so \(x_{j_*}=1/2\).  Exact DCT parity
then gives

\[
 \beta_{n,\ell}^2=
 \begin{cases}
 2/n,&\ell\ \text{even and nonzero},\\
 0,&\ell\ \text{odd}.
 \end{cases}
\]

Thus the full two-port Gram can be written as

\[
 \boxed{
 G_n^{\rm full}
 =\frac{2\sqrt2}{n}
 \sum_{r=1}^{(n-1)/2}
 b_n(\omega_{n,2r})b_n(\omega_{n,2r})^T,}
 \tag{2.1}
\]

where \(b_n=(b_{n,1},b_{n,2})^T\).  Formula (2.1) is the actual finite
dynamics.  No multiplication-only response and no phase-grid surrogate has
been substituted for it.

The continuum phase vector is

\[
 F(\omega)=\bigl(F_1(\omega),F_2(\omega)\bigr)^T,
\]

where, for \(g=4/5\),

\[
 F_k(\omega)
 =\sqrt2e^{-\omega}
 \frac{g\omega[1-(-1)^ke^{-g\omega}]}
 {(g\omega)^2+(k\pi)^2}.
\]

The comparison Gram is

\[
 \boxed{
 G=\sqrt2\int_0^1
 F(\omega(\xi))F(\omega(\xi))^T\,d\xi,
 \qquad
 \omega(\xi)=4\sin^2\!\frac{\pi\xi}{2}.}
 \tag{2.2}
\]

---

## 3. The second-order response law

The main analytic observation is that the full response has an explicit
weak second-order correction even though \(\lVert L_n\rVert\) does not tend
to zero.

### Theorem 3.1 — full-amplitude expansion

For \(k\in\{1,2\}\), uniformly for \(0\le\omega\le4\),

\[
 \boxed{
 b_{n,k}(\omega)
 =F_k(\omega)+h^2D_k(\omega)+O(h^3).}
 \tag{3.1}
\]

Put

\[
 B_k(\omega)
 =\sqrt2\left[(-1)^ke^{-(1+g)\omega}-e^{-\omega}\right].
\]

Then the coefficient in (3.1) is

\[
 \boxed{
 D_k(\omega)
 =\frac{13}{24}\,\omega g B_k(\omega)
 +\frac13\,\omega^2g^2F_k(\omega).}
 \tag{3.2}
\]

This coefficient has two sources.  Composite midpoint quadrature gives

\[
 D_k^{\rm mid}
 =-\frac{f'_{k,\omega}(1)-f'_{k,\omega}(0)}{24}
 =\frac{\omega g}{24}B_k(\omega),
\]

where \(f_{k,\omega}=e^{-\omega V}\phi_k\).  The weak Duhamel correction is

\[
 \begin{aligned}
 D_k^{\rm dyn}
 &=-\int_0^1\!\int_0^1
 \partial_x(e^{-(1-s)\omega V})
 \partial_x(e^{-s\omega V}\phi_k)\,dx\,ds\\
 &=\frac{\omega g}{2}
 \int_0^1e^{-\omega V}\phi_k'\,dx
 -\frac{\omega^2g^2}{6}F_k(\omega)\\
 &=\frac{\omega g}{2}B_k(\omega)
 +\frac{\omega^2g^2}{3}F_k(\omega).
 \end{aligned}
\]

Adding these terms proves (3.2).

### Lemma 3.2 — the uniform weak Dyson remainder

There is a constant \(C_0\), independent of \(n\),
\(0\le\omega\le4\), and \(0\le t\le1\), such that every sampled endpoint
function

\[
 f_h=e^{-t\omega V_h}\mathbf1
 \quad\hbox{or}\quad
 f_h=e^{-t\omega V_h}\phi_{k,h},\qquad k=1,2,
\]

satisfies

\[
 \lVert L_nf_h\rVert_h\le C_0h^{3/2}.
 \tag{3.3}
\]

Moreover, the sum of all Dyson terms containing at least two occurrences of
\(L_n\), paired between \(\mathbf1\) and \(\phi_{k,h}\), is bounded in
absolute value by

\[
 C_0^2h^3\sum_{r\ge2}\frac{4^{r-2}}{r!}.
 \tag{3.4}
\]

#### Proof

At an endpoint, \((L_nf_h)_j=O(h)\); at every interior cell it is
\(O(h^2)\).  The derivative bounds are uniform over the compact family just
displayed.  Therefore

\[
 \lVert L_nf_h\rVert_h^2
 \le h\left(2C^2h^2+(n-2)C^2h^4\right)
 \le C_0^2h^3,
\]

which proves (3.3).

For completeness, expand the bounded finite-dimensional semigroup in the
norm-convergent Dyson series around \(M_n=\omega V_n\):

\[
 e^{-(M_n+L_n)}
 =e^{-M_n}+
 \sum_{r\ge1}(-1)^r
 \int_{\Delta_r}
 e^{-t_0M_n}L_ne^{-t_1M_n}\cdots
 L_ne^{-t_rM_n}\,dt,
 \tag{3.5}
\]

where \(t_j\ge0\) and \(\sum_{j=0}^rt_j=1\).  In a term with \(r\ge2\),
move the leftmost Laplacian onto the smooth left endpoint by symmetry.  The
rightmost Laplacian already acts on the smooth right endpoint.  The
diagonal factors have norm at most one and \(\lVert L_n\rVert_2\le4\), so
the integrand is bounded by \(C_0^2h^3 4^{r-2}\).  Since
\(\operatorname{vol}(\Delta_r)=1/r!\), summing proves (3.4).  \(\square\)

### Completion of Theorem 3.1

For smooth midpoint samples \(p_h,q_h\), discrete summation by parts gives

\[
 \langle p_h,L_nq_h\rangle_h
 =h\sum_{j=0}^{n-2}
 (p_{j+1}-p_j)(q_{j+1}-q_j)
 =h^2\int_0^1p'q'\,dx+O(h^3).
 \tag{3.6}
\]

The first Duhamel insertion therefore contributes at order \(h^2\), even
though \(L_n\) has an order-one spectral norm.  Lemma 3.2 controls every
higher insertion.  The \(r=1\) term is (3.6), and composite
midpoint Euler--Maclaurin has an \(O(h^4)\) remainder for this uniformly
smooth family.  This proves (3.1) without the false claim
\(\lVert L_n\rVert=O(h^2)\).

The integral in \(D_k^{\rm dyn}\) sums all placements of one diffusion
factor among arbitrarily many modulation factors.  It is therefore already
a mixed diffusion--modulation correction, not a pure moment approximation.
The rigorous finite certificate below retains the terms with two or more
diffusion factors exactly as well.

---

## 4. The sharp Gram coefficient

Define

\[
 \boxed{
 E=\sqrt2\int_0^1
 \left[F(\omega(\xi))D(\omega(\xi))^T
 +D(\omega(\xi))F(\omega(\xi))^T\right]d\xi.}
 \tag{4.1}
\]

For the exactly-centred odd sequence, (3.1) and (2.1) give

\[
 \boxed{
 G_n^{\rm full}-G=\frac{E}{n^2}+O(n^{-3}).}
 \tag{4.2}
\]

### Lemma 4.1 — exact-centre quadrature cancellation

With

\[
 H_{ij}(\xi)=F_i(\omega(\xi))F_j(\omega(\xi)),
\]

every \(i,j\in\{1,2\}\) satisfies

\[
 \frac2n\sum_{r=1}^{(n-1)/2}H_{ij}(2r/n)
 -\int_0^1H_{ij}(\xi)\,d\xi=O(n^{-4}).
 \tag{4.3}
\]

#### Proof

First, \(H'_{ij}(1)=0\) because \(\omega'(1)=0\).  At the other endpoint,
\(F_1(\omega(\xi))=O(\xi^2)\) and
\(F_2(\omega(\xi))=O(\xi^4)\), so every \(H_{ij}=O(\xi^4)\).

More explicitly, put \(d=2/n\) and \(m=(n-1)/2\).  The target-mode
quadrature is

\[
 Q_nH=d\sum_{r=1}^mH(rd).
\]

It is exactly the composite midpoint rule for \([d/2,1]\).  Hence

\[
 Q_nH-\int_{d/2}^1H
 =-\frac{d^2}{24}\bigl(H'(1)-H'(d/2)\bigr)+O(d^4).
\]

Here \(H'(1)=0\), \(H'(d/2)=O(d^3)\), and
\(\int_0^{d/2}H=O(d^5)\).  Therefore

\[
 Q_nH-\int_0^1H=O(d^4)=O(n^{-4}).
\]

There is consequently no order-\(n^{-2}\) or order-\(n^{-3}\) target-mode
quadrature contribution, proving the lemma.  Applying the same rule to the
smooth cross term in (4.1), and using the uniform \(O(h^3)\) response
remainder from (3.1), gives (4.2).  \(\square\)

High-precision evaluation of the explicit integral (4.1) gives

\[
 E\approx
 \begin{pmatrix}
 -0.01598629511482710915&-0.003908677177631584465\\
 -0.003908677177631584465&-0.000871634196112061576
 \end{pmatrix}.
\]

Its eigenvalues are approximately

\[
 -0.01693725478632848846,
 \qquad
 0.0000793254753893177344,
\]

so

\[
 \boxed{\lVert E\rVert_2\approx0.01693725478632848846.}
 \tag{4.4}
\]

For the declared continuum-\(H^1\) metric,

\[
 \boxed{
 \left\lVert S_{H^1}^{-1/2}ES_{H^1}^{-1/2}\right\rVert_2
 \approx0.001494310669433565307.}
 \tag{4.5}
\]

Equations (4.4)--(4.5) explain the two finite thresholds:

\[
 \sqrt{\frac{\lVert E\rVert_2}{L_2^{L^2}}}
 \approx343.9718,
 \qquad
 \sqrt{\frac{\lVert S_{H^1}^{-1/2}ES_{H^1}^{-1/2}\rVert_2}
 {L_2^{H^1}}}
 \approx648.5822.
\]

The asymptotic law is explanatory, not by itself a finite certificate.  At
\(n=345\), an analytic remainder bound appended to the leading constant
would have a coefficient budget of only about

\[
 L_2^{L^2}345^2-\lVert E\rVert_2
 \approx1.0141\times10^{-4}.
\]

Generic heat-semigroup or weak Duhamel constants are much too coarse for
that margin.  This is why the direct full-generator enclosure is the right
non-asymptotic proof.

---

## 5. A complete mixed-word enclosure

For each target mode write

\[
 A_{n,\ell}=L_n+\omega_{n,\ell}V_n.
\]

The Loewner bounds

\[
 0\preceq L_n\preceq4I,
 \qquad
 I\preceq V_n\preceq\frac95I,
 \qquad
 0\le\omega_{n,\ell}\le4
\]

imply

\[
 \sigma(A_{n,\ell})
 \subseteq\left[\omega_{n,\ell},
 4+\frac95\omega_{n,\ell}\right].
\]

Centre this interval at

\[
 c_\ell=2+\frac75\omega_{n,\ell},
 \qquad
 B_{n,\ell}=A_{n,\ell}-c_\ell I.
\]

Then

\[
 \lVert B_{n,\ell}\rVert_2
 \le\rho_\ell=2+\frac25\omega_{n,\ell}
 \le\frac{18}{5}.
\]

For the degree-\(m\) polynomial

\[
 P_{m,\ell}
 =e^{-c_\ell}\sum_{r=0}^m\frac{(-B_{n,\ell})^r}{r!},
\]

scalar Taylor remainder and the spectral theorem give the exact operator
bound

\[
 \begin{aligned}
 \left\lVert e^{-A_{n,\ell}}-P_{m,\ell}\right\rVert_2
 &\le e^{-c_\ell}e^{\rho_\ell}
 \frac{\rho_\ell^{m+1}}{(m+1)!}\\
 &=e^{-\omega_{n,\ell}}
 \frac{\rho_\ell^{m+1}}{(m+1)!}\\
 &\le
 \boxed{R_m:=\frac{(18/5)^{m+1}}{(m+1)!}.}
 \end{aligned}
 \tag{5.1}
\]

At degree \(m=32\),

\[
 R_{32}=\frac{(18/5)^{33}}{33!}
 \approx2.62601279829614\times10^{-19}.
\]

The normalized amplitude error is at most \(R_{32}\).  Since each of the
two normalized exact amplitudes has absolute value at most one, the induced
two-port Gram error is bounded by

\[
 \left\lVert G_n(e^{-A})-G_n(P_{32})\right\rVert_2
 \le\sqrt2(4R_{32}+2R_{32}^2)
 <1.486\times10^{-18}.
 \tag{5.2}
\]

This is more than eight orders of magnitude below the \(n=345\) transfer
margin.  A global degree-60 expansion around zero also works, but the
spectral centring in (5.1) makes degree 32 sufficient.

Most importantly, every power

\[
 (L_n+\omega V_n-c_\ell I)^r
\]

is evaluated as the complete tridiagonal action.  It contains every
noncommuting \(L_n\)-\(V_n\) word of length at most \(r\); (5.1) encloses all
longer words.  No commutation, moment truncation, or multiplication-only
replacement enters the proof.

---

## 6. Interval proof at the two transitions

The finite proof uses four outward-rounded components:

1. Arb enclosures of the DCT source values and lattice symbols;
2. tridiagonal degree-32 actions with the exact tail (5.1);
3. the Stage XI Arb enclosure of the continuum integral (2.2); and
4. the closed symmetric \(2\times2\) eigenvalue formula.

For a symmetric error matrix

\[
 \Delta=\begin{pmatrix}a&b\\b&d\end{pmatrix},
\]

the two eigenvalues are enclosed directly as

\[
 \lambda_\pm
 =\frac{a+d\pm\sqrt{(a-d)^2+4b^2}}2.
\]

This last step is essential.  At \(n=345\), the absolute row-sum upper bound
is approximately

\[
 1.6705493006\times10^{-7},
\]

which is larger than the Stage X floor and therefore cannot prove transfer.
The exact symmetric spectral bound is approximately

\[
 1.4223287203\times10^{-7},
\]

which does prove it.

### 6.1 Declared \(L^2\) metric

At \(n=343\), the fixed integer vector \((4,1)\) gives the directed
Rayleigh lower bound

\[
 \frac{|v^T(G_{343}-G)v|}{v^Tv}
 >1.4388972111\times10^{-7}>L_2^{L^2}.
\]

At \(n=345\), the interval spectral calculation gives

\[
 \lVert G_{345}-G\rVert_2
 <1.4223287203\times10^{-7}<L_2^{L^2}.
\]

The latter is a complete finite-model transfer theorem.  The former is a
rigorous rejection of the same sufficient transfer test on the immediately
preceding odd grid.

### 6.2 Declared continuum-\(H^1\) metric

Whiten the same finite and continuum Grams by

\[
 S_{H^1}^{-1/2}.
\]

At \(n=647\), the integer vector \((8,1)\) gives

\[
 \frac{|v^TS_{H^1}^{-1/2}(G_{647}-G)S_{H^1}^{-1/2}v|}{v^Tv}
 >3.5690170591\times10^{-9}>L_2^{H^1}.
\]

At \(n=649\), direct interval diagonalization gives

\[
 \left\lVert
 S_{H^1}^{-1/2}(G_{649}-G)S_{H^1}^{-1/2}
 \right\rVert_2
 <3.5470634870\times10^{-9}<L_2^{H^1}.
\]

This result deliberately assigns the continuum coefficient cost
\(1+(k\pi)^2\) to the finite coefficients, exactly as Stage XI did.  It is
not a result for the natural discrete energy

\[
 1+n^2\omega_{n,k}.
\]

That alternative requires a generalized-pair certificate with a changed
finite source metric.

---

## 7. Exact theorem boundary

The following statements are now proved.

- The complete two-port cell-centred Neumann dynamics transfer at
  \(\tau=1\), \(n=345\), for the declared \(L^2\) coefficient metric.
- The same dynamics transfer at \(\tau=1\), \(n=649\), for the declared
  continuum-\(H^1\) coefficient metric.
- Every mixed diffusion--modulation word is either evaluated in the
  degree-32 full-generator polynomial or enclosed by its spectral tail.
- The immediately preceding odd grids \(343\) and \(647\) rigorously fail
  the respective inherited-floor transfer tests.
- The exact-centred odd-grid error has a sharp \(n^{-2}\) leading law with
  coefficient (4.1).

The following statements are **not** proved.

- No monotonicity theorem for \(\delta_2(n)\) has been established.  Thus
  “adjacent-grid transition” is the safe statement; rejection of one
  predecessor alone is not a proof that no much smaller, nonmonotone grid
  could pass.
- The theorem is not uniform over \(\tau\ge1\).
- It does not transfer the early calibrated chart or either reflecting
  boundary chart.
- It does not use the complete-atlas \(10^{-19}\) floor.
- It does not cover even grids, off-centre atomic placement, a finite-width
  target, or a finite sensor frame.
- It does not certify the natural discrete \(H^1\) metric.
- The \(n^{-2}\) asymptotic formula does not supply a sufficiently sharp
  standalone non-asymptotic remainder at \(n=345\); the Taylor-action
  enclosure supplies that missing finite proof.

These boundaries matter.  The result is a complete bridge at one declared
lattice point, not evidence obtained by silently changing the experiment.

---

## 8. Consequences and next order

The two-port crossing reveals a useful division of labour.

- The weak expansion explains *why* convergence is second order and predicts
  the correct grid scale.
- Spectral centring turns the full matrix exponential into a short,
  rigorously bounded tridiagonal recurrence.
- Exact \(2\times2\) spectral geometry recovers a margin that a row-sum norm
  loses.
- Metric whitening changes the practical resolution scale from \(345\) to
  \(649\), even though the underlying finite response is identical.

The natural next theorem is a compact-\(\tau\) transfer.  The efficient route
is now clear:

1. retain the centred Taylor action, but make \(c_\ell\), \(\rho_\ell\), and
   the continuum Gram interval-valued functions of \(\tau\);
2. cover a finite interval \(1\le\tau\le T\) by outward rational boxes and
   prove the two-port perturbation inequality on every box;
3. use the explicit exponential phase envelope to close \(\tau\ge T\);
4. only then transport the argument to target-placement and reflecting
   boundary families; and
5. certify the changed generalized pair if the natural discrete energy is
   adopted.

Stage XI proved that a finite experiment must be compared in the right
metric.  Stage XII adds the next piece: at two ports, the complete
noncommuting Neumann experiment actually crosses that metric-relative bridge,
and its grid scale is quantitatively explained by a sharp mixed-response
coefficient.
