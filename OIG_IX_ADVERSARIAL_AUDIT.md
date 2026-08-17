# Operational Information Geometry IX

## Adversarial audit of the growing-band response Gramian

- **Date:** 14 August 2026
- **Research lane:** source-band visibility and inverse stability
- **Status:** theorem-boundary audit; not peer reviewed
- **Scope:** the declared one-way parabolic model and its Stage VIII phase
  limits; no claim about physical spacetime

## 1. Verdict

The proposed growing-band milestone is mathematically worthwhile, but its
strongest tempting formulation is false.  There is no parameter-independent
constant \(c>0\) such that every nonnull source direction in an arbitrarily
growing \(L^2\) band satisfies

\[
 \|\mathcal R f\|\ge c\,\operatorname{dist}(f,\ker\mathcal R).
\]

The obstruction is not merely a bad discretization or a parity accident.
Across the resolved, finite-lattice, and atomic charts, the limiting source
response factors through the same transform

\[
 \boxed{
 (\mathcal L_V f)(s)=\int_0^1 e^{-sV(x)}f(x)\,dx . }
 \tag{1.1}
\]

Every chart only changes the set of sampled \(s\)'s and its nonnegative
weight.  These phase maps are compact.  For a monotone ramp they are
injective, but an injective compact operator on an infinite-dimensional
space is not bounded below.  Quotienting exact nulls therefore does not cure
growing-band ill-conditioning.

The sound Stage IX target is consequently two-tiered.

1. **Fixed-band quotient theorem.**  For a declared finite source space,
   identify the exact common null space, prove positivity of the smallest
   quotient singular value on compact nondegenerate chart sets, and transfer
   it to the grid when the assembled operator error is smaller than that
   gap.
2. **Diagonal effective-rank theorem.**  Permit a cutoff \(K=K(h,t)\) to
   grow only while the discretization, preparation, boundary, and calibration
   errors are \(o(\sigma_{*,K})\).  Equivalently, at noise level \(\delta\),
   certify only singular directions above a threshold
   \(\eta\gg\delta\).  The stable dimension is then an effective rank, not
   the raw band dimension.

This is still a substantial milestone.  It would unite the three charts at
the operator level, distinguish structural invisibility from compact
ill-conditioning, and state exactly how much operational source space can be
resolved at a declared resolution and noise floor.

## 2. The common phase operator

Let

\[
 H_0=\left\{f\in L^2(0,1):\int_0^1f=0\right\},
 \qquad 0<v_-\le V(x)\le v_+<\infty.
\]

For the Stage VIII ramp, \(V(x)=1+gx\), but this section does not require
monotonicity.  Put

\[
 L_f(s)=(\mathcal L_Vf)(s).
\]

The three limiting source maps are the following weighted copies of \(L_f\).

### 2.1 Resolved chart

For \(q=t/\varepsilon^2>0\),

\[
 (T_{\mathrm{res},q}f)(u)
 =\widehat\eta(\pi u)L_f(\pi^2qu^2),
 \qquad u>0.
 \tag{2.1}
\]

Its squared norm is the source-family version of the Stage VII--VIII phase
integral.  The assumption \(\int\eta=1\) gives
\(\widehat\eta(0)=1\).

### 2.2 Finite-lattice chart

For a local probability profile \(Q\),

\[
 B_Q(\theta)=\sum_mQ_me^{im\theta},
 \qquad \omega(\theta)=4\sin^2(\theta/2),
\]

and

\[
 (T_{\mathrm{lat},\tau,Q}f)(\theta)
 =B_Q(\theta)L_f(\tau\omega(\theta)),
 \qquad 0<\theta<\pi.
 \tag{2.2}
\]

Here \(B_Q(0)=1\).  The target deposition rule changes the observation
weight, not the underlying source transform.

### 2.3 Interior and boundary atomic charts

The interior map is

\[
 (T_{\mathrm{at}}f)(r)=L_f(\pi^2r^2),
 \qquad r>0.
 \tag{2.3}
\]

At boundary distance \(d/\sqrt t\to\kappa\), its squared norm acquires

\[
 w_\kappa(r)=1+\cos(2\pi\kappa r)
 =2\cos^2(\pi\kappa r).
 \tag{2.4}
\]

Thus \(T_{\mathrm{at},\kappa}=w_\kappa^{1/2}T_{\mathrm{at}}\).
The endpoint \(\kappa=0\) doubles the Gram; it does not create a new source
direction.

For a finite source family \(e_1,\ldots,e_K\), each phase Gram is simply

\[
 G_{ij}=\langle Te_i,Te_j\rangle.
 \tag{2.5}
\]

This operator formulation is preferable to assembling scalar norm estimates
afterward: singular-value perturbation is controlled by
\(\|T_h-T\|\), not by the largest scalar error alone.

### 2.4 Exact Hankel kernels and a basis-independent spectral ceiling

Every phase Gram has an exact integral kernel of the form

\[
 \boxed{G(x,y)=\Phi(V(x)+V(y)).}
 \tag{2.6}
\]

Specifically,

\[
 \begin{aligned}
 \Phi_{\mathrm{res},q}(z)
 &=\int_0^\infty |\widehat\eta(\pi u)|^2
   e^{-\pi^2qu^2z}\,du,\\
 \Phi_{\mathrm{lat},\tau,Q}(z)
 &={1\over\pi}\int_0^\pi |B_Q(\theta)|^2
   e^{-\tau\omega(\theta)z}\,d\theta,\\
 \Phi_{\mathrm{at}}(z)
 &={1\over2\sqrt\pi}\,z^{-1/2},\\
 \Phi_{\mathrm{at},\kappa}(z)
 &={1\over2\sqrt\pi}\,z^{-1/2}
   \left(1+e^{-\kappa^2/z}\right).
 \end{aligned}
 \tag{2.7}
\]

The last line follows by evaluating the Gaussian cosine transform in the
boundary carrier term.

Because \(z\in[2v_-,2v_+]\) and \(v_->0\), every function in (2.7) is
holomorphic on a complex neighbourhood of that interval.  Hence there are
constants \(C<\infty\) and \(\rho>1\), for each declared compact chart
family, and degree-\(m\) polynomials \(P_m\) such that

\[
 \sup_{2v_-\le z\le2v_+}|\Phi(z)-P_m(z)|
 \le C\rho^{-m}.
 \tag{2.8}
\]

But \(P_m(V(x)+V(y))\) has range contained in

\[
 \operatorname{span}\{1,V,\ldots,V^m\},
\]

so its rank is at most \(m+1\), independently of the chosen source basis.
The approximation-number bound therefore gives

\[
 \lambda_{m+2}(G)\le C\rho^{-m},
 \qquad
 \sigma_{m+2}(T)\le \sqrt C\,\rho^{-m/2}.
 \tag{2.9}
\]

This is a stronger basis-independent compactness certificate than the
single-column estimate in Section 5.2.  It also explains why no fixed finite
Sobolev loss can regularize the full inverse.

The hypotheses matter.  If \(v_-\downarrow0\), the atomic singularity at
\(z=0\) destroys a uniform analytic neighbourhood.  If chart weights,
calibration gains, or preparation families degenerate, the constants in
(2.8) need not be uniform.  Finally, (2.6) is exact for the limiting phase
Grams; before the Stage VIII source-diffusion collapse, the finite-time
physical Gram also contains \(A\) and is not generally a Hankel kernel in
\(V(x)+V(y)\).

## 3. Exact kernel theorem

For \(f\in H_0\), define the finite signed pushforward measure

\[
 \nu_f(E)=\int_{V^{-1}(E)}f(x)\,dx,
 \qquad E\subset[v_-,v_+].
\]

Then

\[
 L_f(s)=\int e^{-sv}\,d\nu_f(v).
\]

### Theorem 3.1 — common structural null space

Assume \(q,\tau>0\), \(\eta\in L^1\) has integral one, and \(Q\) is a
probability profile.  For every one of (2.1)--(2.4),

\[
 \boxed{
 \ker T=\{f\in H_0:\nu_f=0\}
 =\{f\in H_0:\mathbb E[f\mid\sigma(V)]=0\}. }
 \tag{3.1}
\]

#### Proof

The weights in (2.1) and (2.2) are nonzero on a neighbourhood of the
origin because \(\widehat\eta(0)=B_Q(0)=1\).  The maps
\(u\mapsto\pi^2qu^2\) and \(\theta\mapsto\tau\omega(\theta)\) therefore
cover a nonempty \(s\)-interval.  The atomic weight is positive almost
everywhere; its boundary factor has only isolated zeros.  Hence \(Tf=0\)
implies \(L_f=0\) on a set with an accumulation point.

Because \(\nu_f\) has compact support, its Laplace transform is entire.
Analytic uniqueness gives \(L_f(s)=0\) for every complex \(s\), so all
moments of \(\nu_f\) vanish.  Polynomial density on
\([v_-,v_+]\) gives \(\nu_f=0\).  The reverse implication is immediate.
The conditional-expectation identity is the standard characterization of a
zero pushforward density. \(\square\)

### Corollary 3.2 — exact symmetry nulls

If \(V(1-x)=V(x)\), every reflection-odd \(f\) belongs to the kernel.  In
particular, for Neumann cosine ports

\[
 \phi_k(x)=\sqrt2\cos(k\pi x),
 \qquad \phi_k(1-x)=(-1)^k\phi_k(x),
\]

all odd \(k\) are invisible in every chart and at every time.  The same null
is exact on a reflection-symmetric cell-centred grid.

If \(V(x)=1+gx\) with \(g\ne0\), \(V\) is one-to-one and a change of
variables in \(\nu_f\) shows that the common continuum kernel is zero.
This removes structural nulls, but not ill-conditioning.

### Warning 3.3 — nonconstant is not enough

A nonconstant \(V\) can still have nontrivial level-set fibres.  The response
sees the conditional average of \(f\) along those fibres and nothing else.
The correct visibility condition is therefore injectivity of the conditional
expectation on the declared source quotient, not merely
"\(V\) is nonconstant."

## 4. Compactness no-go

### Theorem 4.1 — no infinite-dimensional quotient coercivity

Each map in Section 2 is compact from \(H_0\) to its declared output
space.  If

\[
 H_0/\ker T
\]

is infinite-dimensional, there is no \(c>0\) satisfying

\[
 \|Tf\|\ge c\,\operatorname{dist}_{L^2}(f,\ker T)
 \qquad(f\in H_0).
 \tag{4.1}
\]

#### Proof

For the atomic map, the integral kernel

\[
 K(r,x)=e^{-\pi^2r^2V(x)}
\]

is square-integrable because \(V\ge v_->0\).  The boundary multiplier is
bounded.  The lattice kernel lives on a finite rectangle.  In the resolved
chart, the Stage VIII kernels have \(\widehat\eta\in L^2\), so the same
Hilbert--Schmidt argument applies.  Thus all four maps are compact.

If (4.1) held, the induced injective map on the quotient would have a bounded
inverse on its range.  Composing that inverse with the compact map would make
the identity on an infinite-dimensional quotient compact, a contradiction.
\(\square\)

For the monotone ramp, the kernel is zero and the quotient is all of \(H_0\).
Thus even the most favourable declared modulation cannot possess a uniform
full-band \(L^2\) lower bound.

### Corollary 4.2 — fixed bands are sound, growing bands deteriorate

Let \(E_K\subset H_0\) be finite-dimensional and define

\[
 \sigma_{*,K}(T)=
 \inf_{\substack{f\in E_K\cap(\ker T)^\perp\\\|f\|_2=1}}
 \|Tf\|.
 \tag{4.2}
\]

Then \(\sigma_{*,K}(T)>0\) whenever the displayed quotient is nonzero.
For nested spaces whose quotient union is dense and infinite-dimensional,

\[
 \sigma_{*,K}(T)\longrightarrow0.
 \tag{4.3}
\]

Calling (4.2) the "smallest nonzero singular value" is safe only if the
nullity is reported beside it.  A matrix can have a comfortable smallest
*nonzero* singular value while most of the proposed source band lies in an
exact kernel.

## 5. Sharp ramp constructions

For \(V(x)=1+gx\) and the cosine port \(\phi_k\), Stage VIII found

\[
 F_k(s)=L_{\phi_k}(s)
 =\sqrt2e^{-s}
 \frac{gs[1-(-1)^ke^{-gs}]}{(gs)^2+(k\pi)^2}.
 \tag{5.1}
\]

This single formula exposes four separate obstructions.

### 5.1 Weak calibration and parity order

As \(g\to0\), uniformly on compact \(s\)-sets,

\[
 F_k(s)=
 \begin{cases}
 \displaystyle
 {2\sqrt2\,gse^{-s}\over(k\pi)^2}+O(g^2),&k\text{ odd},\\[3mm]
 \displaystyle
 {\sqrt2\,g^2s^2e^{-s}\over(k\pi)^2}+O(g^3),&k\text{ even}.
 \end{cases}
 \tag{5.2}
\]

At \(g=0\), every mean-zero source is exactly invisible.  A family containing
even ports therefore has a singular value no larger than \(O(g^2)\), before
any band-growth effect.  Uniform calibration claims require a declared
lower bound on the symmetry-breaking modulation and must retain the different
odd/even opening orders.

At early resolved time \(q\downarrow0\), the same cancellation appears as

\[
 \|T_{\mathrm{res},q}\phi_k\|
 =O(q)\quad(k\text{ odd}),
 \qquad
 \|T_{\mathrm{res},q}\phi_k\|=O(q^2)\quad(k\text{ even}).
 \tag{5.3}
\]

No common first-order normalization can keep both parity blocks coercive.

### 5.2 High-frequency column decay

For fixed parity,

\[
 k^2F_k(s)\longrightarrow
 H_{\pm}(s)
 ={\sqrt2\over\pi^2}e^{-s}gs
 [1\mp e^{-gs}],
 \tag{5.4}
\]

where the sign records even or odd \(k\).  Dominated convergence applies in
all three phase norms on compact nondegenerate chart sets.  Consequently

\[
 \|T\phi_k\|\asymp k^{-2}
 \tag{5.5}
\]

for each parity, and for the consecutive cosine band
\(E_K=\operatorname{span}\{\phi_1,\ldots,\phi_K\}\),

\[
 \boxed{\sigma_{*,K}(T)\le C K^{-2}.}
 \tag{5.6}
\]

The bound is only a column test; correlations make the true smallest
singular value substantially smaller.

### 5.3 A concrete Sobolev-weighted counterexample

It might seem that measuring source size in \(H^{-2}\) should exactly absorb
the \(k^{-2}\) decay.  It does not.  For same-parity neighbours set

\[
 f_k=(k\pi)^2\phi_k-((k+2)\pi)^2\phi_{k+2}.
 \tag{5.7}
\]

Then \(\|f_k\|_{H^{-2}}\to\sqrt2\), whereas (5.1) gives

\[
 \|Tf_k\|=O(k^{-3})\longrightarrow0.
 \tag{5.8}
\]

The leading scaled columns in (5.4) cancel.  More generally, for any fixed
\(s\ge0\), take a sufficiently high finite difference of the same-parity
sequence

\[
 (k\pi)^sF_k.
\]

Its \(H^{-s}\) source norm stays bounded away from zero while its phase norm
tends to zero.  Hence no inequality

\[
 \|Tf\|\ge c_s\|f\|_{H^{-s}}
 \tag{5.9}
\]

holds on the full cosine span for any fixed finite derivative loss \(s\).
The inverse problem is more severe than a single two-derivative smoothing
law: high same-parity columns become coherent as well as small.

A positive Sobolev prior \(\|f\|_{H^s}\le M\) remains useful for
regularization and cutoff-error bounds.  It is a compactness prior, not a
uniform observability inequality.

### 5.4 Early-chart moment collapse

The Taylor expansion

\[
 L_f(s)=\sum_{m=0}^\infty{(-s)^m\over m!}
 \int_0^1V(x)^mf(x)\,dx
 \tag{5.10}
\]

gives an exact dimension obstruction.  If \(E\subset H_0\) has dimension
\(K\), then for every \(p<K\) there is a nonzero \(f\in E\) satisfying

\[
 \int V^mf=0,
 \qquad 0\le m\le p-1.
 \tag{5.11}
\]

For \(p=K\), the \(K-1\) nontrivial constraints \(m=1,\ldots,K-1\)
still leave at least one direction, and that direction obeys

\[
 |L_f(s)|\le C_f s^K.
 \tag{5.12}
\]

If \(\widehat\eta\) has all polynomial moments, as in Stage VIII, this yields

\[
 \sigma_{*,K}(T_{\mathrm{res},q})\le C_Kq^K
 \qquad(q\downarrow0).
 \tag{5.13}
\]

Similarly,

\[
 \sigma_{*,K}(T_{\mathrm{lat},\tau,Q})\le C_{K,Q}\tau^K
 \qquad(\tau\downarrow0).
 \tag{5.14}
\]

The constants are not asserted uniform in \(K\).  The conclusion does not
need them to be: every fixed multidimensional band becomes arbitrarily ill
conditioned when the observation interval collapses to \(s=0\).  A genuine
early-chart theorem must either keep \(q\) (or \(\tau\)) away from zero,
use port-dependent causal-jet renormalizations, or accept a vanishing
singular-value scale.

### 5.5 The fixed-\(K\) causal flag is a singular-value theorem

For the first \(K\) cosine ports, the upper bound in Section 5.4 is sharp
under a precise geometric hypothesis.

### Theorem 5.1 — strict monotonicity gives a complete moment flag

Let \(V\) be continuous and strictly monotone.  On

\[
 E_K=\operatorname{span}\{\phi_1,\ldots,\phi_K\},
\]

the \(K\) functionals

\[
 \ell_m(f)=\int_0^1V(x)^mf(x)\,dx,
 \qquad 1\le m\le K,
 \tag{5.15}
\]

are linearly independent.

#### Proof

Put \(\phi_0=1\) and consider the augmented cross-moment matrix

\[
 A_{mk}=\int_0^1V(x)^m\phi_k(x)\,dx,
 \qquad 0\le m,k\le K.
\]

Andréief's identity writes its determinant as an integral of

\[
 \det[V(x_j)^m]_{m,j=0}^K
 \det[\phi_k(x_j)]_{k,j=0}^K.
\]

On the ordered simplex \(x_0<\cdots<x_K\), the first determinant is a
nonzero fixed-sign Vandermonde because \(V\) is strictly monotone.  The
second is also a fixed-sign Vandermonde: each
\(\cos(k\pi x)=T_k(\cos\pi x)\), where \(T_k\) is a degree-\(k\)
Chebyshev polynomial and \(\cos\pi x\) is strictly monotone.  Their product
therefore has fixed nonzero sign almost everywhere, so \(\det A\ne0\).
Since the first row is \((1,0,\ldots,0)\), the lower-right moment matrix in
(5.15) is invertible. \(\square\)

The resolved operator has the analytic expansion

\[
 T_{\mathrm{res},q}
 =\sum_{m\ge1}q^m y_m\otimes\ell_m,
 \qquad
 y_m(u)={(-\pi^2u^2)^m\over m!}\widehat\eta(\pi u).
 \tag{5.16}
\]

The vectors \(y_1,\ldots,y_K\) are linearly independent because
\(\widehat\eta\) is nonzero near zero.  Domain and range bases adapted to
the two complete flags reduce (5.16), by bounded triangular operations, to
\(\operatorname{diag}(q,q^2,\ldots,q^K)\) plus higher-order entries.
Consequently, for each **fixed** \(K\), the ordered singular values satisfy

\[
 \boxed{
 c_{j,K}q^j\le
 \sigma_j(T_{\mathrm{res},q}|_{E_K})
 \le C_{j,K}q^j,
 \qquad1\le j\le K, }
 \tag{5.17}
\]

for all sufficiently small \(q\), with \(0<c_{j,K}\le C_{j,K}<\infty\).
Thus \(q,q^2,\ldots,q^K\) are genuine singular-value exponents, not merely
slopes of specially selected columns.  The analogous statement holds for
\(\tau\downarrow0\) in the full lattice phase.

Strict monotonicity is sufficient, not cosmetic.  For symmetric or other
noninjective \(V\), the flag can lose ranks and Theorem 3.1 supplies exact
nulls.  Even among strictly monotone modulations, the constants in (5.17)
are not uniform: a ramp approaching a constant, or a monotone profile
approaching a plateau, makes the moment determinant arbitrarily small.

### 5.6 When target weights preserve or destroy the flag

The output half of (5.17) needs \(K\) independent weighted monomials.  Every
declared continuum Stage VIII weight supplies an interval of effective
\(s\)-values:

* \(\widehat\eta(0)=1\) in the resolved chart;
* \(B_Q(0)=1\) in the lattice chart; and
* the full boundary carrier is positive almost everywhere.

Zeros away from the origin therefore do not collapse the continuum causal
flag.  A diffusion-scale probability characteristic function likewise equals
one at the origin and preserves the flag if the full continuum output is
retained.

Finite sensing is different.  With \(M\) effective samples, the weighted
monomials have rank at most \(M\).  To retain the first \(K\) flag increments
one needs at least \(K\) distinct nonzero effective \(s\)-values with
nonvanishing target and carrier weights.  Boundary carrier zeros, repeated
times, missing target coefficients, or \(M<K\) truncate the staircase.

### 5.7 Critical fan and its nonuniform boundary

The physical resolved response has the extra target-preparation factor
\(\varepsilon^{-1/2}\).  Equation (5.17) therefore gives, for fixed \(K\),

\[
 \sigma_j^{\mathrm{phys}}
 \asymp \varepsilon^{-1/2}q^j.
\tag{5.18}
\]

For the actual diffusion--multiplication response rather than the limiting
phase map, (5.18) additionally requires every mixed-word remainder to be
small on the \(j\)-th scale.  A coarse condition for the deepest direction
is (6.3) below.  This condition is automatic at the level of powers on each
fixed-\(K\) critical path, but not on an arbitrary joint early path and not
uniformly in growing \(K\).

On

\[
 t=\tau h^2,
 \qquad \varepsilon=h^\alpha,
 \qquad q=\tau h^{2-2\alpha},
\]

the \(j\)-th singular value has power

\[
 \sigma_j^{\mathrm{phys}}
 \asymp
 h^{\,2j-\alpha(2j+1/2)}.
 \tag{5.19}
\]

Its critical ridge is

\[
 \boxed{\alpha_j={4j\over4j+1}.}
 \tag{5.20}
\]

This produces a fixed-\(K\) dimension staircase.  At
\(\alpha=\alpha_j\), the \(j\)-th direction is order one, the earlier
directions diverge in the unrenormalized density metric, and the later
directions vanish.  Between consecutive ridges the number of directions
above a fixed absolute scale is constant.

On the weakest \(K\)-th ridge,

\[
 \alpha_K={4K\over4K+1},
 \qquad
 c={\varepsilon\over h}=n^{1/(4K+1)},
 \qquad q=\tau c^{-2}.
 \tag{5.21}
\]

If \(K=K(n)\) grows, remaining in the resolved early chart requires

\[
 c\to\infty\quad\Longleftrightarrow\quad
 {\log n\over4K+1}\to\infty,
\]

or

\[
 \boxed{K=o(\log n).}
 \tag{5.22}
\]

This condition is **necessary for the geometry of the growing critical
ridge, not sufficient for a diagonal singular-value theorem**.  The proof of
(5.17) fixes \(K\).  A valid \(K(n)\) extension must additionally control,
uniformly in \(K\),

1. the inverse moment determinant from Theorem 5.1;
2. the conditioning of the weighted output monomials;
3. analytic Taylor remainders and high Sobolev norms of the preparation;
4. leakage of every lower discrete multiplication moment;
5. mixed diffusion--multiplication words;
6. source resolution and source diffusion; and
7. target, boundary, calibration, and finite-sampling frame errors relative
   to the \(K\)-th gap.

For the affine ramp the moment determinant already carries high powers of
the slope \(g\), while the \(1/m!\) in (5.16) and the derivative moments of
\(\widehat\eta\) introduce further \(K\)-dependent constants.  None is
controlled by (5.22).  Calling \(K=o(\log n)\) sufficient would therefore
interchange a fixed-\(K\) asymptotic with a nonuniform diagonal limit.

## 6. Source bandwidth, mesh, and time

The fixed-port Stage VIII reduction replaces

\[
 e^{-(tA+sV)}f
\]

by \(e^{-sV}f\).  On the cosine band \(k\le K\), the omitted source-diffusion
scale is

\[
 t\|A\|_{E_K}\asymp tK^2.
\]

Thus a uniform use of the *same* phase operator requires at least

\[
 \boxed{tK^2\longrightarrow0.}
 \tag{6.1}
\]

If \(tK^2\to\lambda>0\), the problem enters a new joint
source-diffusion phase.  If \(tK^2\to\infty\), parabolic smoothing suppresses
the top of the source band.  Neither regime is covered by the fixed-port
atomic profile.

The grid must also resolve the source oscillations:

\[
 \boxed{Kh\longrightarrow0.}
 \tag{6.2}
\]

Indeed,

\[
 (k\pi)^2-\mu_{k,h}
 ={(k\pi)^4h^2\over12}+O(k^6h^4),
\]

so the semigroup phase error contains \(th^2K^4\).  Conditions (6.1)--(6.2)
make it small.  Without them, the exact Stage VI counterexample

\[
 k={n\over2},\qquad t=n^{-2},\qquad
 |e^{-t\mu_{k,h}}-e^{-t(k\pi)^2}|
 =|e^{-2}-e^{-\pi^2/4}|
\]

stays separated from zero.

These are regime conditions, not a proof of a growing-band lower bound.
Even when both hold, compactness forces \(\sigma_{*,K}\to0\); the conditions
only make the declared continuum phase the correct ill-conditioned limit.

There is a stronger early-chart warning.  Suppose a moment-adapted direction
satisfies

\[
 \ell_j(f)=\int_0^1V(x)^jf(x)\,dx=0,
 \qquad1\le j<K,
\]

so its pure multiplication profile starts at \(s^K\).  The expansion of
\(e^{-(tA+sV)}\) also contains mixed words.  The first generic one is

\[
 {ts\over2}\langle1,VAf\rangle.
\]

It is not cancelled by the conditions \(\ell_j(f)=0\).  On the cosine band,
\(\|Af\|\lesssim K^2\|f\|\), so comparison with \(s^K\), for effective
\(s\asymp q\), requires the coarse fixed-band condition

\[
 \boxed{C_K\,{tK^2\over q^{K-1}}\longrightarrow0,}
 \tag{6.3}
\]

unless the relevant mixed causal words are separately cancelled.  The
constant \(C_K\) includes the norm of the moment-adapted basis.  Higher mixed
words require corresponding bounds, though (6.3) controls their powers for
fixed \(K\) once their combinatorial constants are tracked.

This obstruction distinguishes absolute source collapse from preservation of
the weakest calibrated singular direction.  For example, with fixed
\(K=3\), \(q=\varepsilon^4\), and \(t=q\varepsilon^2\), both
\(K\varepsilon\to0\) and \(tK^2\to0\), but

\[
 {t\over q^{K-1}}=\varepsilon^{-2}\to\infty.
\]

The mixed profile can dominate the proposed \(q^3\) channel.  Therefore an
early physical Gram theorem cannot replace the Stage VIII joint remainder
condition by a bare \(K\varepsilon\to0\) hypothesis.

At fixed positive time the full parabolic response is still more smoothing.
For smooth \(V\), its source representers are smooth, and high cosine
coefficients decay superalgebraically.  A fixed-\(t_0\) Stage VI theorem and
a shrinking-time Stage IX theorem therefore have different admissible
bandwidth laws.

## 7. Target preparation is part of observability

Let \(\beta_\ell\) denote the nonconstant target coefficients.  The full
response map has the schematic form

\[
 f\longmapsto
 \bigl(\beta_\ell a_\ell(f,t)\bigr)_\ell.
 \tag{7.1}
\]

No source theorem can be uniform over unrestricted preparations.

### 7.1 Exact contrast counterexample

Take a bounded mean-zero density perturbation \(\psi\) and

\[
 \rho_\alpha=1+\alpha\psi,
\]

with \(|\alpha|\) small enough for positivity.  Every nonconstant
\(\beta_\ell\), and hence every response singular value, is multiplied by
\(|\alpha|\).  As \(\alpha\to0\), the preparation approaches the uniform
target and the response Gram vanishes.  A lower theorem must normalize target
contrast or impose a quantitative spectral-frame condition.

### 7.2 Variance control is not a Gram gap

The Stage VIII condition \(\sigma_h^2/t\to0\) proves that an atomic
preparation multiplier approaches one on the active target scale.  For a
growing source band, that \(o(1)\) error must be compared with the shrinking
source gap.  If \(\Delta_{\mathrm{prep},K}\) is the induced operator error,
the required statement is

\[
 \Delta_{\mathrm{prep},K}=o(\sigma_{*,K}),
 \tag{7.2}
\]

not merely \(\Delta_{\mathrm{prep},K}=o(1)\).

At finite lattice scale, two preparations with the same coarse width can
have different \(B_Q\)'s.  Although \(B_Q(0)=1\) preserves injectivity for
each declared \(Q\) and \(\tau>0\), no placement-free quantitative lower
bound follows.  A family with unbounded local variance can make the useful
window around \(\theta=0\) arbitrarily narrow.

### 7.3 Finite target sensing

If only target modes in a finite set \(S\) are retained, one can choose a
nonuniform positive preparation with

\[
 \beta_\ell=0\qquad(\ell\in S).
\]

For example, \(\rho=1+\alpha\phi_m\) with \(m\notin S\) has this property.
Thus a theorem based on finitely many target sensors needs an explicit lower
frame bound for the declared preparation; nonuniformity alone is
insufficient.

## 8. Boundary effects: what changes and what does not

The continuum boundary factor in (2.4) is nonnegative and positive almost
everywhere.  Consequently it does not enlarge the exact kernel.

For a fixed finite source quotient on which the interior atomic Gram is
positive definite, the boundary Gram is positive definite for every
\(\kappa\ge0\).  Its entries depend continuously on \(\kappa\), and the
Riemann--Lebesgue lemma gives

\[
 G_\kappa\longrightarrow G_{\mathrm{int}}
 \qquad(\kappa\to\infty).
\]

Compactness in bounded \(\kappa\)-intervals therefore yields

\[
 \inf_{\kappa\ge0}\sigma_{*,K}(G_\kappa)>0
\]

for each fixed \(K\), after exact source nulls are removed.  This is a useful
positive result: the full continuum boundary crossover changes conditioning
but introduces no new fixed-band structural source null.

Two cautions remain.

1. Replacing \(G_\kappa\) by the interior Gram when \(\kappa=O(1)\) creates
   an order-one model error.
2. Finite modal sampling can land on carrier zeros.  For one rescaled sensor
   \(r_0\), choosing \(\kappa=(2m+1)/(2r_0)\) gives
   \(w_\kappa(r_0)=0\).  At an interior midpoint target,
   \(\cos(\ell\pi/2)=0\) deletes every odd target sensor.  Continuous
   full-output positivity does not automatically survive a finite sampling
   design.

## 9. Finite sampling, rank, and calibration

### 9.1 Row-count obstruction

Suppose \(M\) scalar target-time observations are retained.  Their response
matrix on a \(K\)-dimensional source band has rank at most \(M\).  If \(K>M\),
there are at least \(K-M\) exact discrete null directions, regardless of the
continuum transform's injectivity.

In a pure phase approximation with effective samples \(s_1,\ldots,s_M\),
the matrix is

\[
 R_{mk}=L_{e_k}(s_m).
\]

This makes the rank bound exact.  Clustered \(s_m\)'s additionally reproduce
the moment collapse of Section 5.4 and can make the nonzero singular values
arbitrarily small.  A sampling theorem therefore needs both

\[
 M\ge\dim(E_K/\ker T)
\]

and a quantitative frame/design condition.  Counting samples alone is not
enough.

### 9.2 Scalar bounds do not assemble dimension-free

If each of \(K\) normalized response columns has error at most \(e_K\), then
only

\[
 \|R_h-R\|_2\le\|R_h-R\|_F\le\sqrt K\,e_K
 \tag{9.1}
\]

follows without additional orthogonality.  Thus a scalar Stage VIII estimate
does not automatically give a growing-band Gram theorem.  One needs an
operator estimate or the condition

\[
 \sqrt K\,e_K=o(\sigma_{*,K}).
 \tag{9.2}
\]

The Gram identity gives

\[
 \|R_h^*R_h-R^*R\|
 \le(2\|R\|+\Delta_K)\Delta_K,
 \qquad \Delta_K=\|R_h-R\|.
 \tag{9.3}
\]

Direct relative control of the smallest Gram eigenvalue is therefore more
demanding than absolute response convergence.  Working with singular values
and Weyl's inequality is cleaner:

\[
 |\sigma_j(R_h)-\sigma_j(R)|\le\Delta_K.
 \tag{9.4}
\]

### 9.3 Calibration and noise floor

Let \(C_K\) be the calibrated source-port matrix and \(W\) the output
whitening.  Replacing \(R\) by \(WRC_K\) changes its lower singular value by
the smallest gains of both metrics.  Uniform stability requires those gains
to be bounded away from zero.  Nearly dependent physical ports can destroy a
Gram even when the mathematical cosine basis is well conditioned.

For an additive modelling or calibration error \(E\), Weyl gives

\[
 \sigma_{*,K}(R+E)\ge\sigma_{*,K}(R)-\|E\|.
\]

Consequently no fixed absolute tolerance certifies a band with
\(K\to\infty\).  The necessary scale is

\[
 \boxed{\|E\|=o(\sigma_{*,K}).}
 \tag{9.5}
\]

At finite precision or observational noise \(\delta\), singular directions
below a threshold comparable with \(\delta\) are not operationally
distinguishable.  Reporting raw algebraic rank in that regime overstates the
information actually recovered.

## 10. The strongest theorem shape that survives

### Proposition 10.1 — fixed-band compact-chart stability

Let \(E_K\subset H_0\) be fixed.  Quotient its common structural kernel from
Theorem 3.1.  Let \(\Theta\) be a compact family of declared chart
parameters such that

1. resolved \(q\) and lattice \(\tau\) are bounded away from zero whenever
   ordinary, unrenormalized response Grams are used;
2. target weights obey a uniform finite-band frame condition;
3. source and output calibration metrics are uniformly positive; and
4. the appropriate interior or boundary chart is used.

Then continuity of the finite-dimensional Grams gives

\[
 \gamma_K:=\inf_{\theta\in\Theta}\sigma_{*,K}(T_\theta)>0.
 \tag{10.1}
\]

If discrete response maps satisfy

\[
 \sup_{\theta\in\Theta}\|T_{h,\theta}-T_\theta\|
 =\Delta_{h,K}\longrightarrow0,
 \tag{10.2}
\]

then every quotient singular value converges uniformly, and for
\(\Delta_{h,K}<\gamma_K/2\),

\[
 \sigma_{*,K}(T_{h,\theta})\ge\gamma_K/2.
 \tag{10.3}
\]

This proposition is elementary but important: positivity comes from a
declared continuum Gram gap, not from discretization convergence alone.

### Proposition 10.2 — diagonally growing certification

Let \(K=K(h,t)\to\infty\).  A valid diagonal extension of Proposition 10.1
requires

\[
 Kh\to0,\qquad tK^2\to0,\qquad
 {\Delta_{h,t,K}\over\gamma_K}\to0,
 \tag{10.4}
\]

together with the Stage VIII chart conditions and preparation/boundary errors
included inside \(\Delta_{h,t,K}\).  Then the quotient singular values above
the gap are transferred correctly.  Since \(\gamma_K\to0\), (10.4) is a
diagonal convergence theorem, not uniform growing-band coercivity.

### Proposition 10.3 — noise-thresholded effective rank

For threshold \(\eta>0\), define

\[
 r_\eta(T)=\#\{j:\sigma_j(T)\ge\eta\}.
\]

Compactness makes \(r_\eta(T)<\infty\) for every \(\eta>0\).  If
\(\|T_h-T\|<\delta\) and no singular value of \(T\) lies in
\([\eta-\delta,\eta+\delta]\), Weyl's inequality preserves
\(r_\eta\).  More generally, it brackets the discrete effective rank between
the continuum counts at thresholds \(\eta\pm\delta\).

This is the natural operational statement for a noisy growing source family.
It says exactly how many quotient directions are resolvable without claiming
that an infinitely refined source space remains uniformly visible.

## 11. Chart-by-chart requirements

| Chart | Exact obstruction | Necessary theorem boundary |
|---|---|---|
| resolved, \(q\downarrow0\) | moment/causal-jet rank collapse; odd/even orders differ | keep \(q\ge q_0>0\), or renormalize declared jets and accept a \(K\)-dependent gap |
| resolved, \(q\asymp1\) | compact Laplace map; preparation multiplier | finite-band quotient gap, \(Kh\to0\), \(tK^2\to0\), operator error \(o(\gamma_K)\) |
| finite lattice, \(\tau\asymp1\) | placement-dependent \(B_Q\); finite number of effective samples | declare \(Q\), impose a weighted frame bound, and require \(Kh\to0\) for the continuum source profile |
| atomic, \(\tau\to\infty\) | compact Laplace map and \(k^{-2}\) ramp columns | \(tK^2\to0\), target variance/preparation error \(o(\gamma_K)\), correct boundary Gram |
| fixed physical time | parabolic source smoothing | fixed band or spectral regularization; no finite-Sobolev full-band coercivity |
| finite sensor/time array | row-count nulls and sample clustering | rows at least quotient dimension plus a quantitative sampling-frame certificate |

## 12. Falsification ledger

| Tempting statement | Status and correction |
|---|---|
| a monotone ramp makes the entire source space stably visible | false; it removes exact nulls but the response remains compact |
| quotienting parity nulls gives a uniform lower singular value | false on an infinite-dimensional quotient |
| the ramp loses exactly two derivatives, so \(H^{-2}\) coercivity holds | false; adjacent same-parity scaled columns become coherent |
| a Sobolev-bounded source family is uniformly invertible | false; it is a regularization prior, not a lower observability bound |
| fixed-port scalar errors can be stacked with the same constant | false; absent structure, column errors acquire at least a \(\sqrt K\) assembly factor |
| \(Kh\to0\) is the only source-band condition | false for the Stage VIII phase; also require \(tK^2\to0\), or develop a new joint source-diffusion chart |
| target variance \(o(t)\) is enough for a growing Gram | false; the induced error must be small relative to the shrinking source gap |
| a nonuniform target preparation excites the sensors | false; it can be orthogonal to every retained target mode |
| the boundary creates new continuum source nulls | false for the full atomic phase; its weight is positive almost everywhere |
| the same is true for any finite boundary sampling | false; discrete samples can land on carrier zeros |
| smallest nonzero singular value summarizes visibility | incomplete; exact nullity and noise-thresholded effective rank must also be reported |

## 13. Work order supplied to the Stage IX synthesis

This was the audit's pre-synthesis work order.  Items 1--5 are now implemented
in the canonical manuscript and analytic memo; item 6 is proved only as a
rank/noise boundary, and item 7 remains open.

1. **Prove Theorem 3.1 and the Hilbert--Schmidt no-go in the canonical
   manuscript.**  This supplies the invariant source quotient shared by all
   three charts.
2. **Build the finite-\(K\) phase Grams.**  For the ramp cosine family,
   compute resolved, lattice, interior atomic, and boundary atomic Grams from
   (2.1)--(2.4), recording nullity, \(\sigma_{*,K}\), and effective rank.
3. **Prove the fixed-band compact-chart theorem.**  Keep early \(q\) away
   from zero in the ordinary Gram, and treat the causal-jet limit as a
   separately rescaled chart.
4. **Upgrade scalar Stage VIII errors to operator errors.**  Track their
   \(K\)-dependence and verify the two source scales \(Kh\) and
   \(K\sqrt t\).
5. **State the diagonal theorem.**  Choose only those \(K(h,t)\) for which
   every error is \(o(\gamma_K)\); do not promise a universal power law before
   the singular-value decay is measured or proved.
6. **Add calibrated finite sampling.**  Optimize target modes and times for
   a thresholded E-design, then certify the quotient dimension and noise
   floor.
7. **Only then study a new source-diffusion atlas.**  The regime
   \(tK^2\to\lambda\in(0,\infty)\) is a legitimate adjacent target, but it is
   not the fixed-port Stage VIII phase.

The result would be stronger for acknowledging compactness rather than trying
to evade it: Stage IX can turn "all ports are visible" into the operationally
meaningful statement "these quotient directions are resolvable at this
resolution, schedule, preparation, boundary position, and noise level."

## 14. Executable controls

`test_oig_ix_adversarial_controls.py` checks the following independent
constructions:

1. exact reflection-odd phase nulls on a symmetric cell-centred grid;
2. the finite-sampling rank cap;
3. \(k^{-2}\) ramp column decay and collapse of the \(H^{-2}\)-normalized
   same-parity difference;
4. an early-time source direction with four cancelled multiplication
   moments; and
5. an exact carrier zero for a finite boundary sample.

The controls illustrate theorem boundaries; floating-point singular values
are not proofs of asymptotic coercivity or noncoercivity.
