# Uniform lattice-time transfer: a theorem and certificate laboratory

## Status

This note extends the \(K=2\) noncommuting Neumann benchmark from the single
point \(\tau=1\) to variable lattice time. It has three purposes:

1. identify the correct fixed-\(\tau\) coefficient and compact-interval proof
   target;
2. determine the resolution variable in the joint large-\(\tau\), large-\(n\)
   regime; and
3. falsify any proposed theorem that holds \(n\) fixed while sending
   \(\tau\) to infinity.

The accompanying program uses binary64 SciPy quadrature, tridiagonal Krylov
actions, and low-spectrum tridiagonal diagonalization. Its numerical values
are descriptive evidence, not outward-rounded certificates. The formulas
below isolate what a subsequent Arb proof must enclose.

## 1. General-tau objects

Let

\[
 g=\frac45,\qquad V(x)=1+gx,\qquad
 \phi_k(x)=\sqrt2\cos(k\pi x),\quad k=1,2,
\]

and

\[
 \omega(\xi)=4\sin^2\frac{\pi\xi}{2}.
\]

The continuum response has the closed form

\[
 F_k(s)=\sqrt2e^{-s}
 \frac{gs\,[1-(-1)^ke^{-gs}]}{(gs)^2+(k\pi)^2}.
 \tag{1.1}
\]

The normalized continuum Gram at lattice time \(\tau>0\) is

\[
 \boxed{
 G(\tau)=\sqrt{1+\tau}\int_0^1
 F(\tau\omega(\xi))F(\tau\omega(\xi))^T\,d\xi.}
 \tag{1.2}
\]

For an \(n\)-cell midpoint grid, let \(L_n\) be the unscaled reflecting path
Laplacian, \(V_n=\operatorname{diag}(1+gx_j)\), and

\[
 \omega_{n,\ell}=4\sin^2\frac{\pi\ell}{2n},\qquad
 A_{n,\ell}=L_n+\omega_{n,\ell}V_n.
\]

For the DCT source port \(u_{n,k}\), put

\[
 b_{n,k}(\tau,\ell)
 =\frac1{\sqrt n}{\bf1}^T e^{-\tau A_{n,\ell}}u_{n,k}.
\]

If \(\beta_{n,\ell}\) is the DCT coefficient of the target cell, the complete
finite Gram is

\[
 \boxed{
 G_n(\tau)=\sqrt{1+\tau}\sum_{\ell=0}^{n-1}
 \beta_{n,\ell}^2\,b_n(\tau,\ell)b_n(\tau,\ell)^T.}
 \tag{1.3}
\]

Equation (1.3) retains the exponential of the noncommuting sum
\(L_n+\omega V_n\). It is not the multiplication-phase surrogate.

## 2. Exact-centre parity is structural

For odd \(n\), the central cell lies at \(x=1/2\). Its coefficients obey

\[
 \beta_{n,0}^2=\frac1n,
 \qquad \beta_{n,\ell}=0\quad(\ell\text{ odd}),
 \qquad \beta_{n,\ell}^2=\frac2n\quad(\ell\ge2\text{ even}).
 \tag{2.1}
\]

The \(\ell=0\) response is zero because the nonconstant source ports have
zero mass and the Neumann semigroup preserves mass. Thus the first active
target frequency is \(\ell=2\).

The parity reduction in the code is exact algebra. A full numerical sum and
the parity-reduced sum agree to roundoff. An even grid with a one-cell target
has no cell at \(x=1/2\); its odd target coefficients are nonzero and it is a
different experiment. It cannot be silently mixed into an exact-centre
convergence scan.

## 3. Fixed-tau second-order coefficient

Put \(s=\tau\omega\), and define

\[
 B_k(s)=\sqrt2\left[(-1)^ke^{-(1+g)s}-e^{-s}\right].
\]

The direct general-\(\tau\) extension of the Stage XII calculation gives the
candidate coefficient

\[
 \boxed{
 D_{k,\tau}(\omega)
 =\frac{sg}{24}B_k(s)
 +\tau\left[
 \frac{sg}{2}B_k(s)+\frac{s^2g^2}{3}F_k(s)
 \right].}
 \tag{3.1}
\]

The first term is midpoint quadrature. The bracket is the first weak
Duhamel insertion, multiplied by \(\tau\) because the finite semigroup is
\(e^{-\tau(L_n+\omega V_n)}\). At \(\tau=1\), (3.1) is exactly the proved
Stage XII coefficient.

For fixed \(\tau\), the theorem target is

\[
 b_{n,k}(\tau,\ell)
 =F_k(\tau\omega_{n,\ell})
 +\frac1{n^2}D_{k,\tau}(\omega_{n,\ell})
 +O_\tau(n^{-3}).
 \tag{3.2}
\]

Consequently, with

\[
 E(\tau)=\sqrt{1+\tau}\int_0^1
 \left[FD_\tau^T+D_\tau F^T\right](\omega(\xi))\,d\xi,
 \tag{3.3}
\]

one expects

\[
 \boxed{G_n(\tau)-G(\tau)=\frac{E(\tau)}{n^2}+O_\tau(n^{-3}).}
 \tag{3.4}
\]

On every compact interval \(I\Subset(0,\infty)\), the existing Dyson proof
has the right architecture for a uniform version of (3.2): all semigroup
parameters and potential derivatives remain bounded, and the norm-convergent
word series has a uniform factorial majorant. Turning that observation into
an explicit outward bound is unfinished work, so (3.2)--(3.4) are labelled a
theorem target here rather than a proved result.

The implementation of (3.3) at \(\tau=1\) returns

\[
 E(1)=
 \begin{pmatrix}
 -0.0159862951148271&-0.00390867717763158\\
 -0.00390867717763158&-0.000871634196112062
 \end{pmatrix},
\]

recovering the independent Stage XII calculation.

## 4. Compact-interval evidence

The following table compares odd grids \(n=41,81\). The order is
\(-\log(e_{81}/e_{41})/\log(81/41)\), where
\(e_n=\|G_n(\tau)-G(\tau)\|_2\).

| \(\tau\) | \(e_{41}\) | \(e_{81}\) | empirical order |
|---:|---:|---:|---:|
| 1 | \(9.99340\times10^{-6}\) | \(2.57388\times10^{-6}\) | 1.9923 |
| 2 | \(1.50111\times10^{-5}\) | \(3.87848\times10^{-6}\) | 1.9876 |
| 4 | \(2.56453\times10^{-5}\) | \(6.66820\times10^{-6}\) | 1.9783 |
| 8 | \(4.65372\times10^{-5}\) | \(1.22518\times10^{-5}\) | 1.9601 |

Moreover, \(n^2(G_n-G)\) approaches the explicit \(E(\tau)\). At
\(\tau=1\), the spectral residual
\(\|81^2(G_{81}-G)-E(1)\|_2\) is
\(5.81\times10^{-5}\); at \(n=161\) it is \(2.36\times10^{-5}\).
The convergence becomes less pre-asymptotic as \(\tau\) grows, exactly as the
next section predicts.

These are binary64 observations. They do not certify a uniform error.

## 5. The fixed-grid tail obstruction

The large-time continuum change of variables \(y=\sqrt\tau\,\xi\) gives

\[
 \boxed{
 G(\tau)\longrightarrow
 H:=\int_0^\infty
 F(\pi^2y^2)F(\pi^2y^2)^T\,dy.}
 \tag{5.1}
\]

Numerically,

\[
 H\approx
 \begin{pmatrix}
 8.77600835487426\times10^{-4}&7.97893095949038\times10^{-5}\\
 7.97893095949038\times10^{-5}&1.01240967332583\times10^{-5}
 \end{pmatrix},
\]

with eigenvalues approximately
\(2.84624532530\times10^{-6}\) and
\(8.84878686895\times10^{-4}\). Thus the limit is positive definite.
Positivity is not dependent on those decimals: if (a^THa=0), then
(a_1F_1(s)+a_2F_2(s)=0) for almost every (s>0). But (F_1(s)) has a
nonzero linear term at the origin, whereas (F_2(s)) begins quadratically,
so the two analytic functions are linearly independent and (a=0).

For every fixed odd \(n\), however, (2.1) removes \(\ell=0\), and every
active finite generator satisfies

\[
 A_{n,\ell}\succeq\omega_{n,2}I>0.
\]

It follows rigorously that

\[
 G_n(\tau)\longrightarrow0\qquad(\tau\to\infty),
 \tag{5.2}
\]

even after multiplication by \(\sqrt{1+\tau}\). Therefore

\[
 \boxed{
 \lim_{\tau\to\infty}\|G_n(\tau)-G(\tau)\|_2=\|H\|_2>0
 \quad\text{for every fixed }n.}
 \tag{5.3}
\]

This is a theorem-level negative result, not merely a numerical warning:

> A fixed finite grid cannot support continuum-to-finite transfer uniformly
> on the entire interval \([1,\infty)\).

For \(n=31\), the observed errors at \(\tau=64,256,1024\) are respectively
\(8.15113\times10^{-4}\), \(8.87006\times10^{-4}\), and
\(8.85411\times10^{-4}\), converging toward \(\|H\|_2\).

The continuum tail itself behaves cleanly:

| \(\tau\) | \(\|G(\tau)-H\|_2\) | \(\tau\|G(\tau)-H\|_2\) |
|---:|---:|---:|
| 64 | \(8.50295\times10^{-6}\) | \(5.44189\times10^{-4}\) |
| 256 | \(2.12726\times10^{-6}\) | \(5.44578\times10^{-4}\) |
| 1024 | \(5.31912\times10^{-7}\) | \(5.44678\times10^{-4}\) |

This supports an \(O(1/\tau)\) analytic tail expansion for the continuum
Gram, consistent with the previous lattice-phase theorem.

## 6. Correct joint resolution law

The relevant low target frequencies have
\(\xi=O(\tau^{-1/2})\). Their spacing after the tail rescaling is

\[
 \Delta y\asymp\frac{\sqrt\tau}{n}.
\]

At the same time, (3.1) has \(D_{k,\tau}=O(\tau)\) when
\(s=\tau\omega=O(1)\). Therefore the finite response error is governed by

\[
 \boxed{\varepsilon_{n,\tau}=\frac{\tau}{n^2}.}
 \tag{6.1}
\]

The natural joint condition is

\[
 \boxed{
 \frac{n}{\sqrt\tau}\longrightarrow\infty
 \quad\Longleftrightarrow\quad
 \frac{\tau}{n^2}\longrightarrow0.}
 \tag{6.2}
\]

The existing Stage VIII scalar tail theorem gives the safe rate
\(O(\sqrt\tau/n+1/n)\); after a uniformization over the two-dimensional
source sphere, it yields the same condition (6.2). The faster
\(O(\tau/n^2)\) rate below is a special exact-centre, midpoint observation
supported by the explicit coefficient (3.1). It does not replace the
previous safe theorem until its joint remainder is controlled.

For the test path \(n\approx12\tau^{3/4}\):

| \(\tau\) | \(n\) | \(n/\sqrt\tau\) | L2 error | \(n^2e_n/\tau\) |
|---:|---:|---:|---:|---:|
| 4 | 35 | 17.50 | \(3.49491\times10^{-5}\) | 0.01070 |
| 16 | 97 | 24.25 | \(1.63262\times10^{-5}\) | 0.00960 |
| 64 | 273 | 34.13 | \(8.03652\times10^{-6}\) | 0.00936 |
| 256 | 769 | 48.06 | \(4.03275\times10^{-6}\) | 0.00932 |

Also, \(E(\tau)/\tau\) numerically approaches a finite matrix; at
\(\tau=1024\), its spectral norm is \(0.00934131\). These independent
diagnostics agree on the law

\[
 \|G_n(\tau)-G(\tau)\|_2
 \sim C\frac{\tau}{n^2}
\]

in the resolved tail. A proof must still control the remainder uniformly in
the joint limit.

## 7. Source metrics

Three comparisons are implemented:

\[
 S_{L^2}=I,
 \qquad
 S_{H^1}=\operatorname{diag}(1+\pi^2,1+4\pi^2),
\]

and the natural discrete energy

\[
 \boxed{
 S_{n,H^1}=\operatorname{diag}
 \left(1+n^2\omega_{n,1},1+n^2\omega_{n,2}\right).}
 \tag{7.1}
\]

The natural comparison is

\[
 \left\|S_{n,H^1}^{-1/2}G_nS_{n,H^1}^{-1/2}
 -S_{H^1}^{-1/2}GS_{H^1}^{-1/2}\right\|_2.
\]

Since

\[
 n^2\omega_{n,k}
 =(k\pi)^2-\frac{(k\pi)^4}{12n^2}+O(n^{-4}),
\]

the metric mismatch is itself second order and changes the leading transfer
coefficient. The tests verify quadratic convergence rather than assigning
the continuum \(H^1\) cost to the finite coefficients by definition. Along
the joint path above, the natural-\(H^1\) errors decrease from
\(3.05\times10^{-6}\) at \((\tau,n)=(4,35)\) to
\(3.58\times10^{-7}\) at \((256,769)\).

## 8. A proof-producing compact cover

The most direct rigorous compact-interval certificate can reuse the Stage
XII centred operator polynomial. For

\[
 c(\omega)=2+\frac75\omega,
 \qquad B=A-cI,
 \qquad \|B\|\le\rho(\omega)=2+\frac25\omega,
\]

one has, at general \(\tau\),

\[
 \left\|e^{-\tau A}
 -e^{-\tau c}\sum_{r=0}^m\frac{(-\tau B)^r}{r!}\right\|
 \le e^{-\tau\omega}
 \frac{(\tau\rho)^{m+1}}{(m+1)!}.
 \tag{8.1}
\]

For a compact interval \(J=[\tau_c-r,\tau_c+r]\), a sharper cover should:

1. certify the value and several \(\tau\)-derivatives at \(\tau_c\) with Arb;
2. use the commuting identity
   \(e^{-(\tau_c+\delta)A}=e^{-\tau_cA}e^{-\delta A}\);
3. enclose the \(\delta\)-Taylor remainder using
   \(r\|A\|\), with \(\|A\|\le56/5\);
4. enclose the continuum integral and its derivatives on the same interval;
5. apply the exact symmetric \(2\times2\) eigenvalue formula after each
   declared source whitening; and
6. subdivide until the transfer margin is positive throughout every cell.

A contraction-only first-derivative bound is supplied by the code as a
negative control. At \(\tau=1\) it is about \(105.5\), enormously larger
than the \(K=2\) spectral floors. It is rigorous but unusably coarse. A
successful cover therefore needs locally enclosed derivatives or Taylor
models; black-box global Lipschitz constants would create an impractical
number of cells.

For the unbounded tail, (8.1) is the wrong representation because its degree
must grow with \(\tau\). The proof should instead rescale
\(y=\sqrt\tau\,\xi\), control lattice quadrature with mesh
\(\sqrt\tau/n\), prove a uniform response expansion in
\(\varepsilon=\tau/n^2\), and close the continuum tail analytically.

## 9. Consequences for the protocol engine

The calculations change the design requirement in an important way.

- A compact requested time range can receive a genuine interval-cover
  continuum-to-finite certificate.
- An unbounded time range cannot receive such a certificate at fixed \(n\).
- A continuum tail certificate is meaningful only together with a declared
  resolution policy \(n(\tau)\) satisfying \(n/\sqrt\tau\to\infty\).
- For a genuinely fixed finite stochastic network, late-time performance
  must instead be certified directly from its finite spectral gap; its
  nonconstant response floor necessarily collapses at infinite time.

This is useful for protocol optimization: the engine must optimize over a
finite observation-time window or explicitly price increasing resolution.
It must never report a positive uniform late-time continuum floor for one
fixed finite network.

## 10. Reproduction

The laboratory requires NumPy and SciPy, already used elsewhere in the
repository.

    python -m unittest -v test_oig_uniform_lattice_transfer.py
    python oig_uniform_lattice_transfer.py --quick
    python oig_uniform_lattice_transfer.py --output /tmp/oig-uniform.json

The full default run takes roughly one second on the local machine. Its
low-spectrum branch discards components only after binary64 attenuation by
\(e^{-36}\); this is a numerical acceleration, not a certified truncation.

## 11. Immediate proof order

1. Prove (3.2) uniformly on a declared compact
   \([\tau_0,T]\), with an explicit computable remainder.
2. Implement the Arb interval-\(\tau\) Taylor cover suggested in Section 8 and
   transfer the continuum spectral floor for both declared \(H^1\) choices.
3. Prove the rescaled joint-tail bound
   \(\|G_n(\tau)-G(\tau)\|\le C\tau/n^2+o(1)\) in a region
   \(\tau/n^2\le\varepsilon_0\).
4. Prove the continuum expansion \(G(\tau)=H+H_1/\tau+O(\tau^{-2})\)
   with outward constants.
5. Add a finite-network spectral-gap tail certificate for fixed \(n\), so
   the protocol engine handles the regime where continuum transfer is
   mathematically impossible.

The central conclusion is therefore sharper than “make Stage XII uniform in
\(\tau\)”: compact uniformity is feasible, while the infinite tail requires
either joint refinement or a different, finite spectral certificate.
