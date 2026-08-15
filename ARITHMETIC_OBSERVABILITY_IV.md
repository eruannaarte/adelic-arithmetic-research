# Arithmetic Observability IV

## Local versus global complexity of individual harmonic readings

**Research manuscript — 15 August 2026**

### Status

The algebraic, analytic, and topological statements in Sections 2--6 are
proved.  Their frozen finite inputs are accompanied by an Arb certificate,
a strict machine-readable artifact, and adversarial tests.  Section 7 records
one high-precision numerical collision but does not promote it to a theorem;
that collision is deliberately excluded from the formal certificate.

The model is a finite arithmetic harmonic model.  No assertion about the
Riemann hypothesis, an infinite Euler product, or a physical substrate is
made.

---

## Abstract

Let

\[
 Q_s(z)=1+z+\cdots+z^{s-1},
 \qquad
 f_{C,u}(t)=C\prod_{j=1}^r Q_s(u_jp_j^{-it}),
\]

where the primes `p_j` are distinct and known.  Arithmetic Observability III
showed that two complete complementary marginal blocks recover the positive
free-scale geometric model.  The present paper asks a finer question: how
many *individual complex values* of the global trace are needed when one
uses the nonlinear source model directly?

The generic-local answer is determined exactly.  With complex parameters,
`r+1` complex readings are necessary and sufficient.  With positive real
parameters and a positive free scale, the sharp count is

\[
 \left\lceil\frac{r+1}{2}\right\rceil.
\]

Sufficiency is proved by an explicit Jacobian minor.  At the small-parameter
boundary it becomes an ordinary complex Vandermonde in the prime logarithms;
over the reals, paired quadratures converge after row calibration to the
moment Vandermonde on
`0,log p_1,...,log p_r`.

Local sufficiency does not imply global recovery.  A centered reciprocal
identity converts any collection of `m<=r-1` readings into an odd map from
`S^{r-1}` to `R^m`.  Borsuk--Ulam then produces distinct reciprocal positive
models with identical data on *every* log-parameter sphere.  Thus the
locally sharp two-reading design for three primes is never globally
injective, and it fails locally at the self-reciprocal point `u=(1,...,1)`.

Over the complex numbers the gap is even larger.  At the local threshold
`r+1`, either the homogenized harmonic sections have a basepoint, which gives
an affine zero-data collision, or they define a finite map

\[
 (\mathbb P^1)^r\longrightarrow\mathbb P^r
\]

of degree

\[
 r!(s-1)^r.
\]

Except in the degree-one case `r=1,s=2`, global complex recovery therefore
requires at least `r+2` readings.  For the canonical box
`r=3,s=4,p=(2,3,5)`, four readings are generically locally sufficient but a
basepoint-free four-reading map is generically `162`-to-one over `C`.  The
positive global count lies between three and sixty-four.  Determining
whether a carefully chosen three-reading schedule closes that gap is the
next exact problem.

---

## 1. Model and notions of recovery

Fix integers `r>=1`, `s>=2`, distinct primes
`p_1,...,p_r`, and put

\[
 d=s-1,
 \qquad
 \lambda_j=\log p_j.
 \tag{1.1}
\]

For `u=(u_1,...,u_r)`, define

\[
 A_u(t)=\prod_{j=1}^rQ_s(u_je^{-i\lambda_jt}),
 \qquad
 f_{C,u}(t)=C A_u(t).
 \tag{1.2}
\]

For a schedule `T=(t_1,...,t_m)` of real times, the individual-reading map is

\[
 \mathcal F_T(C,u)
 =\bigl(f_{C,u}(t_1),\ldots,f_{C,u}(t_m)\bigr).
 \tag{1.3}
\]

We use two parameter spaces:

\[
 \Theta_{\mathbb C}=\mathbb C^\times\times\mathbb C^r,
 \qquad
 \Theta_+=\mathbb R_{>0}\times\mathbb R_{>0}^r.
 \tag{1.4}
\]

The following distinctions are essential.

1. **Local injectivity at a point** means injectivity on some neighborhood of
   that point.
2. **Generic-local injectivity** means local injectivity away from a proper
   complex algebraic set in `Theta_C`, or away from a Lebesgue-null real
   analytic set in `Theta_+`.
3. **Global injectivity** means injectivity on the entire declared parameter
   space.
4. **Stable local recovery** additionally asks for a positive smallest
   singular value of a declared real or complex Jacobian.

The coefficient tensor is

\[
 c_\alpha=C\prod_{j=1}^ru_j^{\alpha_j},
 \qquad
 \alpha\in\{0,\ldots,d\}^r.
 \tag{1.5}
\]

Because `c_0=C` and `c_{e_j}=Cu_j`, its finite-parameter representation is
unique whenever `C` is nonzero.  Any collision below is therefore a genuine
coefficient-tensor collision, not a parameterization symmetry.

---

## 2. The sharp complex generic-local threshold

### Theorem 2.1

For the complex parameter space `Theta_C`, the sharp number of individual
complex readings for generic-local recovery is

\[
 \boxed{m_{\mathrm{loc},\mathbb C}=r+1.}
 \tag{2.1}
\]

More explicitly, choose

\[
 t_\ell=\ell\tau,
 \qquad 0\le\ell\le r,
 \tag{2.2}
\]

and suppose that

\[
 1,e^{-i\tau\lambda_1},\ldots,e^{-i\tau\lambda_r}
 \quad\text{are pairwise distinct}.
 \tag{2.3}
\]

Then the complex Jacobian of `F_T` has rank `r+1` on a nonempty Zariski-open
subset of `Theta_C`.

#### Proof

Fewer than `r+1` complex outputs cannot locally embed an open subset of the
complex `(r+1)`-dimensional parameter space into a lower-dimensional complex
space.  Also, every complex Jacobian then has rank at most `m<r+1`.

For sufficiency, evaluate at `C=1,u=0`.  Since

\[
 Q_s(0)=1,
 \qquad Q_s'(0)=1,
\]

the row belonging to time `t_ell` is

\[
 \left(
  \frac{\partial f}{\partial C},
  \frac{\partial f}{\partial u_1},\ldots,
  \frac{\partial f}{\partial u_r}
 \right)
 =\left(1,e^{-it_\ell\lambda_1},\ldots,e^{-it_\ell\lambda_r}\right).
 \tag{2.4}
\]

Put

\[
 \xi_0=1,
 \qquad \xi_j=e^{-i\tau\lambda_j}.
\]

Under (2.2), the matrix in (2.4) is `(xi_j^ell)`, so its determinant is

\[
 \prod_{0\le a<b\le r}(\xi_b-\xi_a),
 \tag{2.5}
\]

which is nonzero by (2.3).  For the fixed schedule, the same Jacobian minor
is a polynomial in `(C,u)` and is not identically zero.  Its nonvanishing set
is therefore Zariski open and dense.  The complex inverse-function theorem
gives local recovery there.  \(\square\)

### Corollary 2.2 — an elementary arithmetic schedule

Condition (2.3) holds for every sufficiently small positive `\tau`.  For
example, it is enough that

\[
 0<\tau\max_j\lambda_j<2\pi,
\]

because then `0,\tau\lambda_1,\ldots,\tau\lambda_r` are distinct and lie in
an interval of length less than `2\pi`.

The proof uses the prime logarithms only through their distinctness.  Their
rational independence becomes relevant to longer full-coefficient
interpolation in Section 6.

---

## 3. The sharp positive-real generic-local threshold

A complex reading supplies two real quadratures.  The constant scale column,
however, must be counted together with all `r` local parameters.

### Theorem 3.1

On `Theta_+`, the sharp generic-local reading count is

\[
 \boxed{
 m_{\mathrm{loc},+}
 =\left\lceil\frac{r+1}{2}\right\rceil.}
 \tag{3.1}
\]

For

\[
 m=\left\lceil\frac{r+1}{2}\right\rceil,
 \qquad
 t_k=k\tau,
 \quad 1\le k\le m,
 \tag{3.2}
\]

the realified Jacobian has full column rank for every sufficiently small
positive `\tau` at some positive parameter point, and hence at almost every
positive parameter point.

#### Proof

The domain has real dimension `n=r+1`, while `m` complex outputs have real
dimension at most `2m`.  An open subset of `R^n` cannot be continuously
embedded in `R^{2m}` when `2m<n`; thus the lower bound in (3.1) is topological,
not merely a regular-Jacobian count.

For sufficiency, first work at the limiting point `C=1,u=0`.  Introduce

\[
 \lambda_0=0.
\]

The real and imaginary derivative rows at time `k tau` are

\[
 E_k=\bigl(\cos(k\tau\lambda_j)\bigr)_{j=0}^r,
 \qquad
 O_k=\bigl(-\sin(k\tau\lambda_j)\bigr)_{j=0}^r.
 \tag{3.3}
\]

Let

\[
 v_q=(\lambda_0^q,\ldots,\lambda_r^q).
\]

Taylor expansion gives

\[
 E_k
 =\sum_{q\ge0}
   \frac{(-1)^q(k\tau)^{2q}}{(2q)!}v_{2q},
 \tag{3.4}
\]

and

\[
 O_k
 =\sum_{q\ge0}
   \frac{(-1)^{q+1}(k\tau)^{2q+1}}{(2q+1)!}v_{2q+1}.
 \tag{3.5}
\]

The two coefficient matrices

\[
 (k^{2q})_{1\le k\le m,\ 0\le q<m},
 \qquad
 (k^{2q+1})_{1\le k\le m,\ 0\le q<m}
 \tag{3.6}
\]

are invertible: the first is a Vandermonde in `1^2,...,m^2`, and the second
is that Vandermonde multiplied by `diag(1,...,m)`.  After invertible row
combinations and the corresponding powers-of-`\tau` rescaling, the rows
therefore converge to

\[
 v_0,v_2,\ldots,v_{2m-2},
 \qquad
 v_1,v_3,\ldots,v_{2m-1}.
 \tag{3.7}
\]

If `n=2m`, these are `v_0,...,v_{n-1}`.  If `n=2m-1`, omit the highest odd
row and again retain `v_0,...,v_{n-1}`.  Their `n` by `n` determinant is

\[
 \prod_{0\le a<b\le r}(\lambda_b-\lambda_a),
 \tag{3.8}
\]

which is nonzero.  Hence the original realified Jacobian has full column
rank for all sufficiently small positive `\tau`.

Although `u=0` is a boundary point of `Theta_+`, continuity preserves the
same nonzero minor at points with all `u_j>0` sufficiently small.  The minor
is real analytic and not identically zero, so its zero set has Lebesgue
measure zero.  Selecting its `n` nonsingular real output coordinates and
applying the inverse-function theorem proves generic-local recovery.
\(\square\)

### Example 3.2 — three primes

For `r=3`, two readings at `\tau` and `2\tau` are enough generically.  With

\[
 \lambda_0=0,
 \quad \lambda_1=\log2,
 \quad \lambda_2=\log3,
 \quad \lambda_3=\log5,
\]

the determinant at `u=0,C=1` has the small-time expansion

\[
 \det J_+(\tau,2\tau)
 =\frac32\tau^6
   \prod_{0\le a<b\le3}(\lambda_b-\lambda_a)
   +O(\tau^8).
 \tag{3.9}
\]

The leading coefficient is positive.  The sixth-order collapse is also a
stability warning: arbitrarily short schedules prove rank but are not good
noise-resistant designs.

---

## 4. Reciprocal symmetry and the positive global obstruction

The local theorem is generic.  A special self-reciprocal point carries an
exact schedule-independent obstruction.

Write

\[
 u_j=e^{x_j},
 \qquad
 S(x)=\sum_{j=1}^rx_j,
 \qquad
 \Lambda=\sum_{j=1}^r\lambda_j.
 \tag{4.1}
\]

Define the centered one-axis factor

\[
 H_s(x,\theta)
 =e^{-d(x-i\theta)/2}Q_s(e^{x-i\theta})
 =\sum_{a=0}^d e^{(a-d/2)(x-i\theta)}.
 \tag{4.2}
\]

Reindexing `a` by `d-a` proves the exact identity

\[
 H_s(-x,\theta)=\overline{H_s(x,\theta)}
 \qquad(x,\theta\in\mathbb R).
 \tag{4.3}
\]

The centered full trace is

\[
 B_x(t)
 =\prod_{j=1}^rH_s(x_j,\lambda_jt)
 =e^{-dS(x)/2}e^{id\Lambda t/2}A_{e^x}(t).
 \tag{4.4}
\]

Consequently,

\[
 B_{-x}(t)=\overline{B_x(t)}.
 \tag{4.5}
\]

### Theorem 4.1 — every-radius reciprocal collision

For every schedule of `m<=r-1` real times, every amplitude `A>0`, and every
radius `\rho>0`, there is an `x\in\mathbb R^r` with `\lVert x\rVert_2=\rho`
such that the two
distinct positive parameter points

\[
 \theta_+(x)
 =\left(Ae^{-dS(x)/2},e^{x_1},\ldots,e^{x_r}\right),
 \tag{4.6}
\]

and

\[
 \theta_-(x)
 =\left(Ae^{dS(x)/2},e^{-x_1},\ldots,e^{-x_r}\right)
 \tag{4.7}
\]

give identical readings at all scheduled times.

#### Proof

On the sphere `S_rho^{r-1}`, define

\[
 G_T(x)
 =\bigl(\Im B_x(t_1),\ldots,\Im B_x(t_m)\bigr)
 \in\mathbb R^m.
 \tag{4.8}
\]

Equations (4.5) imply

\[
 G_T(-x)=-G_T(x),
\]

so `G_T` is continuous and odd.  The Borsuk--Ulam zero theorem says that an
odd map from `S^n` to `R^m` has a zero whenever `m<=n`.  Here `n=r-1`, hence
there is a nonzero `x` on the declared sphere for which every `B_x(t_l)` is
real.  At such an `x`, (4.5) gives

\[
 B_{-x}(t_\ell)=B_x(t_\ell).
\]

Solving (4.4) for `A_{e^x}` and inserting the centered scales (4.6)--(4.7)
shows, exactly,

\[
 Ae^{-dS/2}A_{e^x}(t_\ell)
 =Ae^{dS/2}A_{e^{-x}}(t_\ell)
 =Ae^{-id\Lambda t_\ell/2}B_x(t_\ell).
 \tag{4.9}
\]

Thus all readings agree.  Since `\rho>0`, `x` is nonzero.  Uniqueness of the
coefficient parameterization (1.5) shows that the two source tensors are
distinct.  \(\square\)

### Corollary 4.2 — local failure at the uniform point

For `m<=r-1`, no schedule is locally injective at

\[
 \theta_0=(A,1,\ldots,1).
 \tag{4.10}
\]

Indeed, Theorem 4.1 applies on every sphere `\rho>0`, and both points
`\theta_+(x),\theta_-(x)` converge to `\theta_0` as `\rho` tends to zero.

This does not contradict Theorem 3.1: the full-rank statement there is
generic, whereas (4.10) is the fixed locus of reciprocal symmetry.

### Corollary 4.3 — a tangent kernel and instability

At the uniform point, the realified Jacobian has a nontrivial kernel for
every `m<=r-1` schedule.

To see this, take `\rho_n` decreasing to zero and Borsuk--Ulam zeros
`x_n=rho_n v_n`.  Passing to a subsequence gives `v_n -> v` with `||v||=1`.
Use the logarithmic-coordinate observation map

\[
 \widetilde{\mathcal F}_T(\gamma,x)
 =\mathcal F_T(e^\gamma,e^x).
\]

In coordinates `(gamma,x)=(log C,x)`, the two colliding points equal

\[
 (\log A,0)
 \mathbin{\pm}
 \rho_n
 \left(-\frac d2\sum_j(v_n)_j,\ v_n\right).
 \tag{4.11}
\]

Divide the exact equality of their observations by `2rho_n` and pass to the
limit.  Differentiability gives

\[
 D\widetilde{\mathcal F}_T(\log A,0)
 \left(-\frac d2\sum_jv_j,\ v\right)=0.
 \tag{4.12}
\]

The vector is nonzero.  More strongly, the exact colliding pairs in every
neighborhood rule out any positive local inverse-Lipschitz constant there;
this is not merely a vanishing derivative that could be repaired by a
higher-order injective term.

### Corollary 4.4 — the positive global lower bound

For a positive free scale,

\[
 \boxed{m_{\mathrm{glob},+}\ge r.}
 \tag{4.13}
\]

In particular, for three primes the two-reading generic-local optimum is
never globally sufficient.

### Corollary 4.5 — including time zero costs a global degree of freedom

Since `H_s(x,0)` and hence `B_x(0)` are real for every real `x`, the time-zero
component of (4.8) vanishes identically.  Therefore every schedule of `r`
readings that includes `t=0` still has only `r-1` nontrivial odd equations.
Theorem 4.1 applies unchanged, and such a schedule is not globally injective.

The obstruction uses the freedom to change `C`.  It does not directly apply
when a positive scale is known externally.

---

## 5. Complex global recovery: basepoint or projective degree

The complex obstruction at `r+1` readings is algebraic rather than
order-theoretic.

Let

\[
 X=(\mathbb P^1)^r,
 \qquad
 L=\mathcal O_X(d,\ldots,d).
 \tag{5.1}
\]

For a reading time `t_ell`, put

\[
 z_{j\ell}=e^{-i\lambda_jt_\ell}
\]

and homogenize each local factor as

\[
 q_{j\ell}(X_j,Y_j)
 =\sum_{a=0}^d z_{j\ell}^{a}X_j^aY_j^{d-a}.
 \tag{5.2}
\]

Then

\[
 a_\ell=\prod_{j=1}^rq_{j\ell}
 \tag{5.3}
\]

is a global section of `L`, and on the affine chart `Y_j=1` it equals
`A_u(t_ell)`.

These are highly structured decomposable harmonic sections of `L`, not
generic members of its complete linear system.  No generic-section
assumption is used below: basepoint-freeness is checked from their actual
cyclotomic roots, and the degree computation applies to the morphism they
actually define.

Let

\[
 R_s=\{\zeta\in\mathbb C:\zeta^s=1,\ \zeta\ne1\}
 \tag{5.4}
\]

be the root set of `Q_s`, and define the exact root-ratio set

\[
 \mathcal D_s=R_sR_s^{-1}
 =\{\rho\sigma^{-1}:\rho,\sigma\in R_s\}.
 \tag{5.5}
\]

For `s>=3`, `mathcal D_s=mu_s`: given `eta in mu_s`, choose
`sigma in mu_s` with `sigma!=1,eta^{-1}` and put `rho=eta sigma`; the case
`eta=1` uses any nontrivial `sigma`.  Then `rho,sigma in R_s` and
`rho sigma^{-1}=eta`.  For `s=2`, `mathcal D_2={1}`.  Keeping the exact
root-ratio notation avoids an incorrect claim in the exceptional binary case.

### Lemma 5.1 — the exact basepoint criterion

For `r+1` readings, the sections `(a_0,...,a_r)` have no common projective
zero if and only if

\[
 \frac{z_{j\ell}}{z_{jk}}\notin\mathcal D_s
 \quad
 \text{for every }j\text{ and every }\ell\ne k.
 \tag{5.6}
\]

#### Proof

A zero of `q_{j\ell}` cannot occur at `[X_j:Y_j]=[1:0]`, because

\[
 q_{j\ell}(1,0)=z_{j\ell}^d\ne0.
 \tag{5.7}
\]

At a finite coordinate `u_j=X_j/Y_j`, it occurs exactly when

\[
 u_j=z_{j\ell}^{-1}\rho
 \qquad\text{for some }\rho\in R_s.
 \tag{5.8}
\]

If all `r+1` products (5.3) vanished, choose for each reading one axis whose
factor vanishes.  Pigeonhole forces two readings `ell!=k` to use the same
axis `j`.  Equation (5.8) would then imply

\[
 z_{j\ell}/z_{jk}\in R_sR_s^{-1}=\mathcal D_s,
\]

so (5.6) fails.

Conversely, suppose (5.6) fails on axis `j` for readings `ell!=k`.  By the
definition of `mathcal D_s`, choose `rho,sigma in R_s` so that

\[
 z_{j\ell}/z_{jk}=\rho/\sigma.
\]

Then the single finite coordinate

\[
 u_j=z_{j\ell}^{-1}\rho=z_{jk}^{-1}\sigma
\]

makes both `a_ell` and `a_k` vanish.  There are exactly `r-1` remaining
readings and `r-1` remaining axes.  Assign them bijectively, and on the axis
assigned to reading `h` choose any coordinate
`u_q=z_{qh}^{-1}\zeta` with `zeta in R_s`.  Every section now has a vanishing
factor, giving a common affine-torus zero.  Thus failure of (5.6) is also
necessary.  \(\square\)

Equivalently, the bad real-time differences on axis `j` are

\[
 \lambda_j(t_\ell-t_k)\in
 \begin{cases}
  2\pi\mathbb Z, & s=2,\\[2mm]
  (2\pi/s)\mathbb Z, & s\ge3.
 \end{cases}
 \tag{5.9}
\]

### Lemma 5.2 — every projective basepoint yields an affine-torus collision

If the sections `(a_0,...,a_r)` do have a common zero in `X`, they also have
a common zero in `(\mathbb C^\times)^r`.

#### Proof

By (5.7), an infinite coordinate can never supply a vanishing factor.  At a
projective common zero, retain every finite coordinate used to make one or
more products vanish and replace every infinite coordinate by any nonzero
finite value.  The retained factors still vanish, so every product `a_ell`
still vanishes.  All retained roots in (5.8), and all replacements, are
nonzero.  The resulting common zero lies in the affine torus.  \(\square\)

At that affine parameter, `F_T(C,u)=0` for every nonzero `C`; varying `C`
gives an immediate global collision.

### Theorem 5.3 — exact degree in the basepoint-free case

Suppose `m=r+1` and the sections (5.3) are basepoint-free.  They define a
morphism

\[
 \Phi_T:X\longrightarrow\mathbb P^r,
 \qquad
 x\longmapsto[a_0(x):\cdots:a_r(x)].
 \tag{5.10}
\]

This morphism is finite and surjective, and

\[
 \boxed{\deg\Phi_T=r!d^r=r!(s-1)^r.}
 \tag{5.11}
\]

#### Proof

Basepoint-freeness gives

\[
 \Phi_T^*\mathcal O_{\mathbb P^r}(1)=L.
 \tag{5.12}
\]

The line bundle `L=O(d,...,d)` is ample because `d>0`.  If a fiber of
`\Phi_T` were positive-dimensional, it would contain a projective curve
`Gamma`.  The pullback (5.12) would have degree zero on `Gamma`, while an
ample line bundle has positive degree on every curve, a contradiction.
Thus `\Phi_T` is quasi-finite.  It is projective and hence proper, so it is
finite.  Its image has dimension `r`; being a closed subset of `P^r`, it is
all of `P^r`.

Let `H_j` be the pullback of the hyperplane class from the `j`th `P^1`.
Then

\[
 c_1(L)=d(H_1+\cdots+H_r),
 \qquad H_j^2=0,
\]

and therefore

\[
 \deg\Phi_T
 =\int_Xc_1(L)^r
 =d^rr!\int_XH_1\cdots H_r
 =r!d^r.
 \tag{5.13}
\]

\(\square\)

### Theorem 5.4 — the universal complex global lower bound

Except when `r=1,s=2`, no schedule of `r+1` individual complex readings is
globally injective on `Theta_C`.  Consequently,

\[
 \boxed{m_{\mathrm{glob},\mathbb C}\ge r+2}
 \tag{5.14}
\]

outside that degree-one exception.

#### Proof

There are two exhaustive cases.

1. If the homogeneous sections have a basepoint, Lemma 5.2 turns it into an
   affine-torus zero-data collision for arbitrary nonzero scales.
2. If they are basepoint-free, Theorem 5.3 gives degree
   `D=r!(s-1)^r`.  Over `mathbb C` the finite morphism is generically
   separable, so when `D>1`, a generic projective target away from the branch
   locus has `D` distinct preimages.  The projective boundary
   `X\setminus\mathbb C^r` has dimension `r-1`; because `\Phi_T` is finite,
   its image also has
   dimension at most `r-1`.  A generic target therefore avoids that image,
   so all `D` inverse points are affine.  Each projective inverse determines
   a unique nonzero complex scale matching any chosen nonzero representative
   of the readings.  Hence the original affine free-scale map has multiple
   preimages.

The equality `r!(s-1)^r=1` holds only for `r=1,s=2`; the argument correctly
leaves that case open to a two-reading global inverse.  \(\square\)

### Corollary 5.5 — an explicit basepoint-free arithmetic schedule

Take

\[
 t_\ell=\ell\tau,
 \qquad 0\le\ell\le r,
\]

and suppose

\[
 0<\tau<\frac{2\pi}{sr\max_j\lambda_j}.
 \tag{5.15}
\]

For two distinct reading indices, the nonzero phase difference on any axis
has magnitude strictly below `2\pi/s`; hence its ratio is not in
`\mathcal D_s`.
Lemma 5.1 applies.  The affine Jacobian at `u=0` is also the nonzero
Vandermonde from Theorem 2.1.  Thus this one schedule simultaneously exhibits
generic-local recovery and the exact global projective degree.

---

## 6. A rigorous global upper bound from full interpolation

The preceding lower bounds do not yet determine the optimal global count.
A coarse finite upper bound follows from ordinary exponential interpolation.

For

\[
 \alpha\in\{0,\ldots,d\}^r,
 \qquad
 \omega_\alpha=\sum_{j=1}^r\alpha_j\lambda_j,
 \tag{6.1}
\]

unique factorization implies that all `s^r` frequencies `omega_alpha` are
distinct.  Put

\[
 N=s^r
\]

and choose

\[
 0<\tau<\frac{2\pi}{d\sum_j\lambda_j}.
 \tag{6.2}
\]

Then the nodes

\[
 \eta_\alpha=e^{-i\tau\omega_\alpha}
\]

are pairwise distinct: every nonzero phase difference has absolute value
less than `2\pi`.  The readings at

\[
 t_n=n\tau,
 \qquad 0\le n<N,
 \tag{6.3}
\]

satisfy

\[
 f_{C,u}(n\tau)
 =\sum_\alpha c_\alpha\eta_\alpha^n.
 \tag{6.4}
\]

The square matrix `(eta_alpha^n)` is Vandermonde and invertible.  It recovers
the entire coefficient tensor, after which

\[
 C=c_0,
 \qquad
 u_j=\frac{c_{e_j}}{c_0}.
 \tag{6.5}
\]

Therefore

\[
 m_{\mathrm{glob},+}\le s^r,
 \qquad
 m_{\mathrm{glob},\mathbb C}\le s^r.
 \tag{6.6}
\]

This upper bound deliberately ignores multiplicativity during acquisition.
Its role is to keep the open problem finite and falsifiable, not to claim an
efficient design.

---

## 7. The canonical box `(r,s,p)=(3,4,(2,3,5))`

Here

\[
 d=3,
 \qquad
 \dim_{\mathbb C}\Theta_{\mathbb C}=4,
 \qquad
 \dim_{\mathbb R}\Theta_+=4.
\]

The proved conclusions are:

1. Four complex readings are sharp for generic-local complex recovery.
2. Two complex readings are sharp for generic-local positive-real recovery.
3. Every two-reading schedule has reciprocal positive collisions on every
   sphere about `u=(1,1,1)` in logarithmic coordinates.
4. Every three-reading schedule containing `t=0` also has such a collision.
5. A basepoint-free four-reading complex map has degree

   \[
   3!\,3^3=162.
   \tag{7.1}
   \]

6. Since

   \[
   \frac{2\pi}{4\cdot3\log5}>0.32,
   \]

   the schedule `(0,0.1,0.2,0.3)` is basepoint-free, is generically locally
   nonsingular, and has generic complex fiber size `162`.
7. Sixty-four readings at the Vandermonde schedule (6.3) recover the entire
   coefficient box.

Thus the current rigorous count intervals are

\[
 \boxed{3\le m_{\mathrm{glob},+}\le64,}
 \tag{7.2}
\]

and

\[
 \boxed{5\le m_{\mathrm{glob},\mathbb C}\le64.}
 \tag{7.3}
\]

### 7.1 A numerical three-reading collision

The lower endpoint in (7.2) is not automatically sufficient.  For the
schedule

\[
 T=(1,2,3),
\]

a 70-decimal numerical solve of

\[
 \Im B_x(1)=\Im B_x(2)=\Im B_x(3)=0
 \tag{7.4}
\]

found

\[
 x\approx(
 -2.31164950008188332598,
 -0.49968233927864117650,
  0.28447767590986682963).
 \tag{7.5}
\]

Hence

\[
 e^x\approx(
 0.0990976550803666,
 0.606723361284764,
 1.32906764274293),
 \tag{7.6}
\]

while

\[
 e^{3S(x)}
 \approx0.00051027411800685294.
 \tag{7.7}
\]

An internal solve retained substantially more digits than are displayed in
(7.5).  At that internal precision, the models

\[
 (1,e^x)
 \quad\text{and}\quad
 (e^{3S(x)},e^{-x})
\]

were reported to agree at all three times with residuals below `10^{-69}`;
the rounded coordinates printed here do not reproduce that residual bound.

This is a **high-precision collision candidate for that schedule**, not a
proved collision or a certified falsifier.
It will become formal only after an interval-Newton or exact sign/topological
certificate is supplied.  Exploratory multistart searches did not find
off-diagonal solutions for several other nonzero schedules, including
`(0.17,0.41,0.83)`, but absence in a numerical search is not evidence of
global injectivity.

---

## 8. Validity ledger and scope

### Proved in this paper

1. The sharp complex generic-local count `r+1`.
2. The sharp positive-real generic-local count `ceil((r+1)/2)`.
3. An explicit Vandermonde witness for the complex Jacobian.
4. A paired even--odd moment-Vandermonde witness for the real Jacobian.
5. The centered reciprocal identity (4.3)--(4.5).
6. An exact positive collision on every log-parameter sphere for every
   `m<=r-1` schedule.
7. Failure of local injectivity, a nontrivial tangent kernel, and failure of
   any local inverse-Lipschitz bound at `u=(1,...,1)` under those schedules.
8. Failure of every `r`-reading schedule containing time zero.
9. The projective basepoint criterion using the exact root-ratio set
   `\mathcal D_s`.
10. The basepoint-to-affine-torus reduction.
11. Finiteness and exact degree `r!(s-1)^r` in the basepoint-free complex
    case.
12. The universal complex lower bound `r+2`, except for `r=1,s=2`.
13. The full-interpolation upper bound `s^r`.

### Computed but not yet formally certified

1. The three-reading reciprocal collision in Section 7.1.
2. Negative multistart searches for selected alternative three-reading
   schedules.

### Not proved

1. That any three-reading schedule is globally injective on the positive
   canonical model.
2. That every three-reading schedule fails there.
3. The optimal complex global count between five and sixty-four.
4. A uniform stability constant on the noncompact positive parameter space.
   Saturation as some `u_j` tends to zero or infinity makes such a statement
   unlikely without a compact parameter declaration or a weighted metric.
5. Robustness to unknown primes, time error, off-box coefficients, or model
   mismatch.
6. Any extension from this finite model to an infinite Euler product.

### Novelty boundary

The ingredients are classical: finite exponential interpolation and
Vandermonde matrices, Borsuk--Ulam, Segre--Veronese compactifications,
basepoint-free linear systems, ampleness, and intersection-theoretic degree.
This manuscript does not claim those tools as new.

The contribution is their specific synthesis for individual arithmetic
harmonic readings:

- the exact field-sensitive generic-local counts;
- the centered reciprocal formula and its every-radius Borsuk--Ulam
  obstruction;
- the resulting sharp distinction between generic-local and positive-global
  sensing;
- and the basepoint-or-degree dichotomy giving the exact
  `r!(s-1)^r` complex ambiguity at the local threshold.

These claims should be compared with, rather than substituted for, the
standard theories cited below.

---

## 9. Reproduction

The finite certificate uses exact rational arithmetic and 256-bit Arb
intervals.  It verifies the declared Jacobian, resonance, intersection-number,
and Vandermonde inputs; it does not claim to mechanize Borsuk--Ulam,
ampleness, intersection theory, or the numerical three-reading collision.
Byte-identical reconstruction is pinned to python-flint 0.9.0 with FLINT
3.6.0; these versions are recorded inside the payload because serialized Arb
endpoints are implementation-dependent.

Verify the pinned artifact with:

```bash
python arithmetic_observability_reading_complexity.py \
  --verify arithmetic_observability_reading_complexity_certificate.json
```

Run the adversarial suite with:

```bash
python -m unittest -v \
  test_arithmetic_observability_reading_complexity.py
```

Artifacts:

```text
arithmetic_observability_reading_complexity.py
arithmetic_observability_reading_complexity_certificate.json
test_arithmetic_observability_reading_complexity.py
```

Certificate payload SHA-256:

```text
4b652c09feb7d68c6eb10c143086c390ee5f48e7618aee694e174d513804ef8e
```

Implementation SHA-256:

```text
1fe0b19acae202ec9e196555f5cf73d5079ba7d990fbf678fbcc1e798a66ebb9
```

Certificate-file SHA-256:

```text
be668449767cf299295c5ecfc8445ca725e1f3858ce4b9b1e26a5aa52767153b
```

Adversarial-test SHA-256:

```text
d343a3d915334702171d9d233193f362db3c7690c240b6e4d6253c0c16f7d4c0
```

The verifier independently reconstructs and checks:

1. at the positive point `(1,1/2,1,2)`, the real two-reading schedule
   `(1/4,1/2)` satisfies `J_R^T J_R > 2I`;
2. the complex schedule `(0,1/10,1/5,3/10)` has
   `|det J_C|^2>500000` at that point;
3. every relevant fourth-root resonance distance for that schedule exceeds
   `1/100` of a cycle;
4. the exact intersection-number combinatorics `3! 3^3=162`;
5. all 2,016 pairs of the 64-node `tau=1/10` schedule have squared chord
   distance greater than `1/100000`; and
6. strict JSON rejection of duplicate keys, nonfinite numbers, booleans in
   integer fields, negative zero, undeclared keys, and digest mismatches.

The focused suite contains 24 tests; the combined Arithmetic Observability
I--IV regression contains 108 tests.  The numerical root in (7.5) remains an
explicitly nonformal target for a future interval-Newton certificate.

---

## 10. Next exact question

The immediate target is deliberately narrow:

> Does there exist a three-reading schedule that is globally injective on
> the positive free-scale model for `r=3,s=4,p=(2,3,5)`?

A falsifiable work order is:

1. Express equality after eliminating positive scale as a real secant system
   in logarithmic variables.
2. Search over three nonzero times for schedules maximizing the minimum
   off-diagonal residual and the minimum local singular value on compact
   boxes `[-L,L]^3`.
3. Certify a candidate box by interval branch-and-bound, or extract a
   certified collision.
4. Use the centered formula (4.4) to analyze all faces as
   `x_j -> +infinity` or `x_j -> -infinity`, closing the noncompact part of
   the proof.
5. If every candidate fails, seek a degree or equivariant-topology theorem
   extending the `m<=r-1` Borsuk--Ulam obstruction to `m=r`.

Either outcome is useful.  A certified three-reading inverse would close the
positive count exactly.  A universal obstruction would raise the lower bound
and expose new distinguishability geometry.

---

## References and standard background

1. G. R. de Prony, *Essai experimental et analytique: sur les lois de la
   dilatabilite de fluides elastiques et sur celles de la force expansive de
   la vapeur de l'alcool, a differentes temperatures*, Journal de l'Ecole
   Polytechnique 1 (1795), 24--76; the classical origin of Prony recovery for
   exponential sums.
2. K. Borsuk, *Drei Satze uber die n-dimensionale euklidische Sphare*,
   Fundamenta Mathematicae 20 (1933), 177--190.
3. J. Matousek, *Using the Borsuk--Ulam Theorem*, Springer, 2003.
4. R. Hartshorne, *Algebraic Geometry*, Springer, 1977, especially the
   standard material on projective morphisms, ample line bundles, and
   intersection theory.
5. J. Harris, *Algebraic Geometry: A First Course*, Springer, 1992, for
   projective varieties, Segre--Veronese embeddings, and degree.
6. W. Fulton, *Intersection Theory*, Springer, second edition, 1998.
7. Arithmetic Observability I--III, for the finite prime-box trace, its
   complementary marginals and blind interaction, sharp harmonic completion,
   and multiplicative-source observability.
