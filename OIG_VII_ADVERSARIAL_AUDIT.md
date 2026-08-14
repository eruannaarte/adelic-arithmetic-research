# Operational Information Geometry VII — adversarial audit

## Verdict

The two principal phase laws are structurally sound:

\[
 \|\mathcal R_\varepsilon(q\varepsilon^2)\|_2
 \asymp \varepsilon^{-1/2}\mathcal P(q)
\]

for an interior resolved mollifier, and

\[
 \|\mathcal R_h(\tau h^2)\|_{2,h}
 \asymp h^{-1/2}\Psi_{Q,\theta}(\tau)
\]

for a declared lattice profile and phase.  The continuum and lattice
dispersion relations, normalizations, ramp profile, endpoint powers, and
one-cell binomial identity all passed independent checks.

Several boundaries must nevertheless be made explicit:

1. width and time do not determine a critical lattice limit without a
   preparation rule and lattice phase;
2. the multiplication limit is a fixed-port strong limit, not a full
   operator-norm limit;
3. the moment index
   \(r_*=\min\{r:\int V^r\phi\ne0\}\) is the order of the multiplication
   profile \(F_\phi\), not the causal order of the complete parabolic response;
4. the critical exponent \(4r/(4r+1)\) is algebraically correct; the initial
   sequential-limit gap was subsequently closed for continuum orders one and
   two and for the canonical midpoint ramp on the grid, while the arbitrary
   higher-order and all-path statement remains open;
5. boundary centres, nonsymmetric kernels, and nonsmooth kernels require
   separate charts.

## 1. Preparation rules are mathematically different models

Let \(x_j=(j+1/2)h\), let a mollifier be centred at \(y_h\), and write its
lattice phase relative to a chosen centre as

\[
 y_h=x_{j_h}+\theta_hh,\qquad -\tfrac12\le\theta_h\le\tfrac12.
\]

### Cell averages

The finite-volume rule

\[
 q_{j,h}=\int_{jh}^{(j+1)h}\rho_{\varepsilon_h}(y)\,dy
\]

is always a probability and is the robust convention.  When
\(\varepsilon_h/h\to c\in(0,\infty)\), it retains the full profile
\(Q^{c,\theta}\).  When \(\varepsilon_h/h\to0\), it produces:

- a one-cell atom if \(\theta_h\) stays away from a cell boundary on the
  mollifier scale;
- a two-cell split if the centre approaches a boundary on that scale;
- no unique limit if \(\theta_h\) has no limit.

For a fixed irrational physical centre, \(\{ny_0\}\) need not converge.  The
phase theorem is therefore naturally a subsequence theorem unless the centres
are deliberately aligned.

### Point samples

The normalized point rule

\[
 q_{j,h}\propto\rho_{\varepsilon_h}(x_j)
\]

has a sharper pathology.  For a compactly supported kernel, it can be
undefined: if an even tent kernel is centred exactly at a cell boundary and
\(\varepsilon<h/2\), no cell centre intersects its support.  For a Gaussian,
the same subcell limit bifurcates:

- at a cell centre it converges to a one-cell atom;
- at a cell boundary it converges to an equal adjacent split.

Thus rapid decay does not remove phase dependence; it only avoids an empty
sample.

### Nearest-cell atomization

A rule which assigns all mass to the nearest cell discards the physical width.
It gives \(Q=\delta_0\) even when \(\varepsilon/h\) is large and therefore
cannot satisfy the resolved-mollifier bridge theorem.

### Moment-preserving placement

For an interior point, positive weights on the two bracketing centres preserve
mass and first moment.  If the right weight is \(w\), then the raw infinite
lattice Laplacian obeys the exact identity

\[
 \|\Delta_{\mathbb Z}[(1-w)\delta_0+w\delta_1]\|_2^2
 =1+20(w-\tfrac12)^2.
\]

The ultraviolet constant ranges from \(1\) for an equal split to \(\sqrt6\)
for a one-cell atom.  Moment preservation therefore improves low fixed-mode
accuracy but does not produce a placement-independent full-band initial
layer.

At the physical boundary, a positive moment-preserving atom may be impossible:
every cell centre is at least \(h/2\), so no probability on internal centres
can have mean \(y_0<h/2\).  One must choose a reflected ghost convention,
allow signed weights, or abandon exact first-moment preservation.

## 2. Exact first-jet fingerprints

For the ramp and the full source tangent, the Stage V first jet is

\[
 g(A_hq_h)\bigl(\mathbf1^{\mathsf T}D_hH_h\bigr).
\]

The following limits are exact:

\[
\begin{array}{c|c}
\text{preparation} &
\displaystyle\lim_{n\to\infty}n^{-5/2}\|\dot{\mathcal R}_n(0)\|_F/g\\
\hline
\text{interior one-cell atom} & 1/\sqrt2\\
\text{physical-boundary atom} & 1/\sqrt6\\
\text{interior equal adjacent split} & 1/\sqrt{12}.
\end{array}
\]

The boundary stencil has only two nonzero entries, rather than the three of an
interior atom.  “Atomic” is therefore not one ultraviolet constant.

For a cell-averaged Gaussian with \(\varepsilon=0.25h\), an interior cell
boundary and an interior cell centre give respectively

\[
 n^{-5/2}\|\dot{\mathcal R}_n(0)\|_F
 \approx0.28863,\qquad0.65359.
\]

The exponent agrees while the constants differ by more than \(0.36\).

In the resolved regime, a standard Gaussian gives the independent continuum
control

\[
 \varepsilon^{5/2}\|\dot{\mathcal R}_\varepsilon(0)\|_F
 \longrightarrow
 \frac{\|\eta''\|_2}{\sqrt{12}}
 =\frac1{\sqrt{32\sqrt\pi}}
 =0.1327814915\ldots .
\]

The cell-average computation at \(n=1024,\varepsilon=0.04\) gives
\(0.1327566994\).

## 3. Correct time chart

The regimes should be stated as follows.

| Width regime | Time regime | Surviving structure |
|---|---|---|
| \(\varepsilon/h\to\infty\) | \(t/\varepsilon^2\to q\in(0,\infty)\) | continuum phase \(\mathcal P(q)\) |
| \(\varepsilon/h\to\infty\) | \(t/\varepsilon^2\to0\) | smooth early law, subject to a uniform remainder |
| \(\varepsilon/h\to\infty\) | \(t/\varepsilon^2\to\infty,\ t\to0\) | continuum atomic \(t^{-1/4}\) law |
| \(\varepsilon/h\to c\in(0,\infty)\) | \(t/h^2\to\tau\in(0,\infty)\) | lattice phase \(\Psi_{Q,\theta}(\tau)\) |
| \(\varepsilon/h\to0\) | \(t\asymp h^2\) | one-cell or split-atom lattice law |
| \(\varepsilon/h\to0\) | \(t\asymp\varepsilon^2\ll h^2\) | below the lattice clock; essentially an early Taylor regime |
| any vanishing width | fixed \(t>0\) | common smoothed atomic limit |

In the subgrid regime, taking \(t=q\varepsilon^2\) does not recover the
continuum crossover.  The discrete scaled time is

\[
 \tau=t/h^2=q(\varepsilon/h)^2\to0.
\]

For a first-order visible port and an atomic lattice profile, the leading norm
is \(t h^{-5/2}\), not the resolved
\(t\varepsilon^{-5/2}\).  The mesh has saturated the target bandwidth.

## 4. High-frequency multiplication: valid scope and counterexample

The modewise statement is valid:

\[
 t_h\mu_{\ell_h,h}\to\sigma,\qquad
 t_hA_h\to0\text{ strongly on fixed physical inputs}
\]

implies

\[
 \left\langle1,e^{-t_h(A_h+\mu_{\ell_h,h}V_h)}\phi_h\right\rangle_h
 \longrightarrow
 \int_0^1e^{-\sigma V(x)}\phi(x)\,dx.
\]

At critical lattice frequency \(\ell_h/n\to\xi\) and
\(t_h=\tau h^2\), the correct parameter is

\[
 \sigma=4\tau\sin^2(\pi\xi/2),
\]

not \(\tau(\pi\xi)^2\).  For \(\xi=1/2,\tau=0.7,g=0.8,\phi=\phi_1\),
the \(n=256\) response is

\[
 0.0465658814.
\]

The lattice multiplication limit is \(0.0465687678\), whereas replacing the
lattice symbol by continuum dispersion gives \(0.0369013062\), an error of
approximately \(9.66\times10^{-3}\).

This is not a full operator-norm limit.  The operators \(h^2A_h=L_n\) converge
strongly to zero under the fixed-domain embeddings, but their norms approach
four.  With \(g=0\), source mode \(k_h=n/2\), and the same diffusive time,
source diffusion contributes \(e^{-2\tau}\), which multiplication alone omits.
For \(\xi=1/2,\tau=0.7\), the resulting operator gap is

\[
 e^{-1.4}(1-e^{-1.4})=0.1857869013\ldots .
\]

The reduction therefore requires fixed physical source ports, a fixed regular
modulation profile, and strong rather than operator-norm topology.

Two exact null controls must accompany every computation:

- if \(g=0\), every nonconstant source has zero target-marginal response;
- if \(V\) is reflection symmetric, every reflection-odd source is invisible
  at every time.

## 5. The proposed general causal order is not the actual causal order

Let \(K_\lambda=A+\lambda V\).  The complete Taylor coefficient is

\[
 \langle1,K_\lambda^m\phi\rangle,
\]

which contains noncommuting words in \(A\) and \(V\).  The coefficient of the
highest target power \(\lambda^m\) is the pure moment
\(\int V^m\phi\), but lower target powers contain terms such as

\[
 \int V A(V\phi).
\]

Consequently,

\[
 r_*=\min\{r\ge1:\int V^r\phi\ne0\}
\]

is the multiplication-moment order governing the expansion of
\(F_\phi(s)=\int e^{-sV}\phi\).  It is not, without additional hypotheses, the
first nonzero time derivative of the full response.

### An all-pure-moments counterexample

Choose a positive asymmetric \(C^\infty\) profile \(V\) which is equal and flat
to all orders at both endpoints and, temporarily suppressing the harmless
source normalization, put \(\phi=V'\). Then

\[
 \int_0^1V^r\phi\,dx
 =\left[\frac{V^{r+1}}{r+1}\right]_0^1=0
\]

for every \(r\ge0\).  Nevertheless, integration by parts gives

\[
 \boxed{
 \langle1,K_\lambda^3\phi\rangle
 =-\frac{\lambda^2}{2}\int_0^1(V')^3dx,}
\]

which is generically nonzero for an asymmetric profile.  The explicit flat
bump in the adversarial control file has

\[
 -\frac12\int(V')^3=0.0115039768422\ldots .
\]

This is not a source-normalization artifact.  The same source has
\(\|V'\|_2=0.517628923226115\ldots\), so after unit-\(L^2\) normalization the
mixed coefficient is \(0.0222243702507\ldots\).

Thus all pure moment cancellations kill the leading multiplication limit but
do not imply exact dynamical invisibility.  Exact silence requires a genuine
common invariant symmetry or an equivalent cyclic-subspace obstruction.

There is a second regularity boundary: a continuum derivative of order \(m\)
requires the source to lie in the appropriate domain of \(K^m\).  A generic
nonconstant potential can destroy iterated Neumann compatibility.  Finite
matrices always have Taylor series, but their higher jets need not converge to
continuum derivatives.  A general causal-jet theorem must assume flat boundary
compatibility, use periodic geometry, or formulate the result through
semigroup asymptotics rather than formal derivatives.

## 6. What remains correct about the critical exponent

The pure multiplication contribution at order \(r\) is

\[
 \frac{t^r}{r!}
 \left(\int V^r\phi\right)A_y^r\rho_\varepsilon.
\]

For an interior kernel \(\eta\in H^{2r}(\mathbb R)\),

\[
 \|A_y^r\rho_\varepsilon\|_2
 =\varepsilon^{-(2r+1/2)}\|\eta^{(2r)}\|_2.
\]

At \(t=\tau h^2\) and \(\varepsilon=h^\alpha\), this term scales as

\[
 h^{2r-\alpha(2r+1/2)}.
\]

Hence

\[
 \alpha_c(r)=\frac{4r}{4r+1}
\]

is algebraically correct for the first nonzero multiplication moment.
Mixed terms contain fewer target powers than time powers.  They do not move
this threshold near its critical chart, although they may be the actual first
time derivative or dominate a different joint path.

The initial draft proved a crossover for fixed
\(q=t/\varepsilon^2>0\), then derived the endpoint \(q\downarrow0\). Applying
those two sequential statements alone to

\[
 q_h=\tau h^{2-2\alpha}\to0
\]

requires a direct joint expansion. The final analytic memo supplies that
expansion for \(r=1\), and for \(r=2\) under
\(V\in W^{1,\infty}\): its form estimate gives a scalar remainder
\(O(s^{5/2})\), which is lower order by \(O(\sqrt q)\) after modal summation.
For the actual midpoint ramp grid, reflection makes the even-mode discrete
first moment vanish exactly, and repeated discrete summation by parts controls
the growing-band tail. Thus the \(4/5\) and \(8/9\) ramp thresholds are
closed. A general proof must still control:

- higher pure terms by powers of \(t/\varepsilon^2\);
- mixed \(A,V\) words;
- the target spectral tail uniformly in \(q_h\);
- discrete-to-continuum error when \(h/\varepsilon\to0\);
- the source's iterated generator domains; and
- for order two on a general grid, the quantitative cancellation
  \(m_{1,h}=o(q_h)\), not merely \(m_{1,h}\to0\).

The remaining open statement is the uniform three-parameter comparison across
all ports, preparations, orders, and joint paths, not the canonical ramp
thresholds.

## 7. Carrier averaging, nonsymmetry, and boundaries

For a general real, not necessarily even kernel,

\[
 \beta_\ell
 =\sqrt2\,\Re\!\left(
 e^{i\ell\pi y_0}\widehat\eta(\ell\pi\varepsilon)
 \right)
\]

up to the chosen Fourier-sign convention.  At a fixed interior centre, the
rapid carrier still averages the squared coefficient to
\(|\widehat\eta|^2\), so evenness is unnecessary for the full resolved norm.
It is essential for the simpler exact coefficient formula and for parity
claims.

Preserving the kernel mean does not restore reflection parity.  A
mean-preserving asymmetric Gaussian mixture centred at \(1/2\) has a nonzero
third odd cosine coefficient, approximately
\(-5.63\times10^{-4}\) at width \(0.04\), while the symmetric Gaussian
coefficient is zero to roundoff.

Carrier averaging can fail or change form in four situations:

1. \(y_0\) lies at a reflecting boundary;
2. \(y_0/\varepsilon\) remains finite in a boundary layer;
3. only a sparse or fixed selection of target modes is observed;
4. the critical lattice profile is retained instead of taking
   \(\varepsilon/h\to\infty\).

At \(y_0=0\), the carrier does not oscillate.  A normalized half-mollifier has
a different derivative norm and the reflected heat kernel has a different
atomic constant.  One cannot reuse the interior \(1/2\)-carrier average.

The manuscript's summation-by-parts sentence also needs a regularity
justification.  Bounded carrier partial sums alone do not control arbitrary
weights.  A clean proof is to show that the rescaled squared-weight step
functions converge in \(L^1\), then apply the Riemann–Lebesgue lemma.  The
semigroup envelope supplies domination, but this \(L^1\) convergence should be
stated.

## 8. Kernel regularity

The early formula

\[
 \|\eta^{(2r)}\|_2
\]

requires \(\eta\in H^{2r}\).  It is not valid for an arbitrary object called a
mollifier.  A box kernel has distributional second derivatives and no
continuum \(L^2\) first jet.  Even when its width is resolved, the discrete jet
is controlled by the two grid-scale edges and remains mesh dependent.

For rapidly decaying kernels on the finite interval, the manuscript currently
calls

\[
 \varepsilon^{-1}\eta((y-y_0)/\varepsilon)
\]

a probability and gives an exact coefficient formula.  This is exact for
compact support contained in the interval, but not for a Gaussian: a small
tail lies outside \([0,1]\).  Either restrict the exact theorem to compact
support or introduce the normalization

\[
 Z_\varepsilon^{-1}
 \varepsilon^{-1}\eta((y-y_0)/\varepsilon).
\]

For a fixed interior centre, \(Z_\varepsilon=1+o(\varepsilon^N)\) for rapidly
decaying kernels, so the asymptotic phase law is unchanged.

## 9. Resolved corrections and theorem boundaries

The final canonical synthesis addresses the following audit items; they are
retained here as the falsification trail:

1. Rename \(r_*\) the multiplication-moment order, or explicitly distinguish
   it from the complete causal order.
2. Supply a direct joint expansion before asserting critical shrinking-width
   laws; the final memo now does so for orders one and two and for the
   canonical midpoint ramp, while higher orders remain conditional.
3. State that the multiplication reduction is for fixed source ports in
   strong topology; it is false in full operator norm.
4. Add the lattice symbol
   \(4\sin^2(\pi\xi/2)\) whenever \(\ell/n\) is not small.
5. Declare cell averages as the canonical positive discretization and treat
   point sampling, nearest-cell atomization, and moment preservation as
   different charts.
6. Add the boundary atom constant and the impossibility of positive
   first-moment placement inside the boundary half-cell.
7. Extend the resolved theorem to nonsymmetric kernels using the real-part
   coefficient, or retain evenness explicitly.
8. Replace the unsupported carrier summation-by-parts step with an
   \(L^1\)-convergence/Riemann–Lebesgue argument.
9. Normalize rapidly decaying noncompact kernels on \([0,1]\).
10. In the falsification ledger, remove the duplicated table header.
11. In the large-\(q\) endpoint, say “provided \(C_\phi>0\)”; asymptotic
    equivalence to zero is undefined when the multiplication profile vanishes.

## 10. Reproduction

The independent laboratory is in oig_vii_adversarial_controls.py and the
regressions are in test_oig_vii_adversarial_controls.py.

Run:

    python oig_vii_adversarial_controls.py
    python -m unittest -v test_oig_vii_adversarial_controls.py

The eleven tests cover:

- interior, boundary, and split-atom constants;
- continuous two-cell phase dependence;
- critical cell-average phase;
- point-sampling bifurcation and empty compact support;
- the resolved Gaussian constant;
- a mean-preserving asymmetric-kernel parity failure;
- lattice versus continuum high-frequency dispersion;
- failure of full operator-norm multiplication reduction;
- exact zero-coupling and reflection-null controls;
- the all-pure-moments mixed-jet counterexample; and
- the algebraic critical exponent.
