# Arithmetic Observability III

## Multiplicative structure can remove an ambient blind space

**Research manuscript — 15 August 2026**

### Status

The reconstruction, obstruction, exceptional-locus, stability, and metric
theorems are proved.  The canonical finite model is accompanied by an exact
rational certificate and adversarial tests.  This paper studies a structured
finite arithmetic model; it does not assert that arbitrary number-field data
factor in the manner assumed here.

---

## Abstract

Complementary valuation marginals have a large linear blind space: on an
`r`-axis prime box with `s` exponent states, the full interaction

\[
 W_1\otimes\cdots\otimes W_r
\]

has dimension `(s-1)^r`.  Arithmetic Observability II showed exactly how many
ordinary traces are needed to complete that ambient linear model.  Here we
ask a different question forced by arithmetic multiplicativity: does the
blind space still cause collisions when coefficient arrays are restricted to
rank-one product tensors?

For free-scale geometric tensors

\[
 c_\alpha=C\prod_{j=1}^ru_j^{\alpha_j},
\]

the answer is sharp.  A selected resonant axis `j` is usable exactly when
`Q_s(u_j)=1+u_j+...+u_j^{s-1}` is nonzero.  Two usable axes recover every
local parameter and the scale explicitly; zero or one usable axis leaves an
exact collision fibre.  Positive parameters have no exceptional locus, so
two axes are globally minimal.  Over the complex numbers, roots of `Q_s`
place nonzero Segre tensors directly inside the ambient blind interaction and
give the complete algebraic failure set.

The result is stronger for normalized product distributions.  Any two
complementary marginals recover every factor by ordinary marginalization;
one marginal omits one factor exactly.  The reconstruction is quantitatively
stable in `l1`: from two probability-valued approximate marginals, an explicit
probability-tensor estimate obeys a sharp two-block coupling bound, while a
product-valued plug-in obeys a separately stated factorwise bound.

The induced geometry is also explicit.  At the uniform product, the
calibrated tangent spectrum is

\[
 \boxed{1-w_j\quad\text{with multiplicity }s-1}
\]

in factor direction `j`.  Its sharp floor is `1-max_j w_j`; two uniformly
weighted axes give `1/2`, while all `r` uniform axes give `(r-1)/r`.  Thus the
same protocol whose ambient quotient floor is `1/r` can be much more
informative on the multiplicative manifold.  The linear blind space has not
disappeared; the structured model meets each of its affine fibres at most
once away from an explicit exceptional locus.

---

## 1. Ambient nonobservability need not survive a nonlinear model

Let

\[
 H=(\mathbb F^s)^{\otimes r},
 \qquad \mathbb F\in\{\mathbb R,\mathbb C\},
\]

with `r>=2` and `s>=2`.  For a coefficient tensor `c`, let `M_jc` sum out
axis `j`:

\[
 (M_jc)_{\alpha_{-j}}
 =\sum_{a=0}^{s-1}c_{\operatorname{insert}_j(a,\alpha_{-j})}.
 \tag{1.1}
\]

Arithmetic Observability I proved that prime-resonant harmonic traces recover
these marginals exactly.  It also proved

\[
 \bigcap_{j=1}^r\ker M_j
 =W_1\otimes\cdots\otimes W_r,
 \qquad
 W_j=\{x:\mathbf1^{\mathsf T}x=0\}.
 \tag{1.2}
\]

Therefore the linear observation map is not injective on `H`.  But a
restricted model `S subset H` is identifiable precisely when

\[
 (S-S)\cap(W_1\otimes\cdots\otimes W_r)=\{0\}.
 \tag{1.3}
\]

The relevant object is the secant set `S-S`, not the entire ambient vector
space.  This paper evaluates (1.3) for multiplicative tensors.

---

## 2. Free-scale geometric prime factors

Define

\[
 v_s(z)=(1,z,\ldots,z^{s-1}),
 \qquad
 Q_s(z)=1+z+\cdots+z^{s-1}.
 \tag{2.1}
\]

Consider the Segre family

\[
 c(C,u)
 =C\bigotimes_{j=1}^rv_s(u_j),
 \qquad C\ne0.
 \tag{2.2}
\]

Its coefficient at multi-index `alpha` is

\[
 c_\alpha=C\prod_{j=1}^ru_j^{\alpha_j}.
\]

This is the finite-box form of a multiplicative local model.  Algebraically,
it is an affine chart of the cone over a Segre product of rational normal
curves (a Segre--Veronese variety), rather than the whole rank-one Segre
variety.  The first coordinate of every `v_s(u_j)` is one, so `(C,u)` is a
unique parameterization when `C` is nonzero.

Summing one factor gives the identity

\[
 \boxed{
 M_jc(C,u)
 =C Q_s(u_j)\bigotimes_{k\ne j}v_s(u_k).}
 \tag{2.3}
\]

Thus a resonant axis is visible exactly when `Q_s(u_j)` is nonzero.

For selected axes `J`, put

\[
 N_J(u)=\{j\in J:Q_s(u_j)\ne0\}.
 \tag{2.4}
\]

### Theorem 2.1 — sharp free-scale identifiability

Within the family (2.2), the data `(M_jc)_{j in J}` determine `c(C,u)`
uniquely if and only if

\[
 \boxed{|N_J(u)|\ge2.}
 \tag{2.5}
\]

If `a,b in N_J(u)` are distinct, reconstruction is explicit.  Let

\[
 A_a=(M_ac)_0=CQ_s(u_a).
\]

For `ell!=a`, let `e_ell` denote the marginal coordinate with exponent one
on axis `ell` and zero elsewhere.  Then

\[
 u_\ell=\frac{(M_ac)_{e_\ell}}{A_a},
 \qquad \ell\ne a,
 \tag{2.6}
\]

and the second usable margin supplies

\[
 u_a=\frac{(M_bc)_{e_a}}{(M_bc)_0},
 \qquad
 C=\frac{A_a}{Q_s(u_a)}.
 \tag{2.7}
\]

#### Proof

Equation (2.3) gives all displayed ratios, so two usable axes determine every
parameter.

If `N_J(u)={a}`, the data determine `u_k` for `k!=a` and the product
`A=CQ_s(u_a)`, but every

\[
 u_a=z,
 \qquad
 C=\frac{A}{Q_s(z)},
 \qquad Q_s(z)\ne0,
 \tag{2.8}
\]

gives the same observations.  If `N_J(u)` is empty, every selected marginal
is zero, and the exact zero-data fibre consists of all `C'!=0` and parameters
`u'` for which `Q_s(u'_j)=0` on every selected axis; unselected parameters are
arbitrary.  These fibres prove necessity. \(\square\)

Because each resonant trace block is an invertible Vandermonde transform of
its marginal, Theorem 2.1 applies equally to the corresponding complete raw
resonant blocks.  It is minimality in the number of axis blocks, not yet in
the number of individual time samples used to reconstruct a general
marginal.

---

## 3. The exceptional locus is exactly arithmetic

Over the complex numbers,

\[
 Q_s(z)=0
 \quad\Longleftrightarrow\quad
 z\in\mu_s\setminus\{1\},
 \tag{3.1}
\]

where `mu_s` is the set of `s`-th roots of unity.  For `m=|J|>=2`, define

\[
 \mathcal E_J
 =\{u:\#N_J(u)\le1\}.
 \tag{3.2}
\]

### Proposition 3.1 — algebraic failure set

The nonidentifiable locus is

\[
 \mathcal E_J
 =V\!\left(Q_s(u_j)Q_s(u_k):j<k,\ j,k\in J\right)
 \tag{3.3}
\]

and equivalently

\[
 \mathcal E_J
 =\bigcup_{a\in J}
 \bigcap_{j\in J\setminus\{a\}}
 \{Q_s(u_j)=0\}.
 \tag{3.4}
\]

It has pure complex codimension `m-1` in the parameter space `C^r`.  Hence any
two selected axes are generically sufficient, additional axes raise the
codimension of failure, and no
collection is universally sufficient on the unrestricted complex Segre
cone.

#### Proof

The pairwise products in (3.3) all vanish exactly when no two selected
`Q_s(u_j)` values are simultaneously nonzero.  Equation (3.4) lists the
components: each fixes `m-1` coordinates to finite root sets, hence has
codimension `m-1`. \(\square\)

### 3.1 The ambient kernel is realized, not bypassed

If every `u_j` is a nontrivial `s`-th root of unity, then

\[
 \mathbf1^{\mathsf T}v_s(u_j)=Q_s(u_j)=0,
\]

so

\[
 c(C,u)\in W_1\otimes\cdots\otimes W_r.
 \tag{3.5}
\]

This nonzero rank-one tensor collides with zero under every marginal.  If
exactly one axis `a` is usable, two points of the fibre (2.8) differ by

\[
 \left(
 \frac{v_s(z)}{Q_s(z)}-
 \frac{v_s(z')}{Q_s(z')}
 \right)
 \otimes\bigotimes_{k\ne a}v_s(u_k),
 \tag{3.6}
\]

up to the common scale `A`.  The first factor has coordinate sum zero, as do
the factors on every other selected axis.  Hence the difference lies in
`intersection_{j in J} ker M_j`.  When all `r` axes are selected, it lies in
the full interaction `W_1 tensor ... tensor W_r`; for a proper selected set,
unobserved factors need not have zero sum.  The exceptional set therefore has
a direct geometric meaning rather than being a failure of the proof.

### 3.2 Field-specific consequences

- If `u_j>=0`, then `Q_s(u_j)>0`.  With free scale `C`, any two axes give
  global recovery and one axis is impossible.
- Over signed reals, `Q_s` has no real root when `s` is odd.  When `s` is
  even, its sole real root is `-1`; failure occurs exactly when at most one
  selected parameter differs from `-1`.
- On the complex root-free region, including `|u_j|<1`, any two axes work
  globally.
- If positive `C` is externally known and `u_j>=0`, one margin suffices:
  its baseline determines `Q_s(u_j)`, which is strictly increasing, while its
  ratios determine the other parameters.  The two-axis threshold concerns a
  free scale or probability normalization.
- For `r=1`, the sole free-scale observation is `C Q_s(u_1)`, so recovery is
  impossible without additional information.

---

## 4. Normalized product distributions

Let

\[
 \Delta_{s-1}
 =\{q\in\mathbb R_{\ge0}^s:\mathbf1^{\mathsf T}q=1\}
\]

and consider the full product model

\[
 \mathcal P_{r,s}
 =\left\{p=\bigotimes_{j=1}^rq_j:q_j\in\Delta_{s-1}\right\}.
 \tag{4.1}
\]

This is broader than the one-parameter geometric factors in Section 2.  Since
each factor has unit sum,

\[
 \boxed{M_jp=\bigotimes_{k\ne j}q_k.}
 \tag{4.2}
\]

### Theorem 4.1 — two marginals are globally sharp

For `r>=2`, any two distinct complementary marginals determine every point of
`P_{r,s}`, including boundary points.  One marginal is never injective when
`s>=2`.

#### Reconstruction

Choose distinct axes `a,b`.  For every `k!=a`, marginalize `M_ap` further
onto coordinate `k`; the result is `q_k`.  Marginalizing `M_bp` onto coordinate
`a` gives `q_a`.  Hence all factors and their product are known.

Conversely, `M_ap` is independent of `q_a`, so replacing that factor gives an
exact collision. \(\square\)

Equivalently,

\[
 (\mathcal P_{r,s}-\mathcal P_{r,s})
 \cap\ker(M_a,M_b)=\{0\},
 \tag{4.3}
\]

while the same intersection for one axis contains every difference obtained
by changing its omitted factor.

### Theorem 4.2 — sharp two-margin inverse modulus

For two product sources `p,p'`, put

\[
 d_a=\operatorname{TV}(M_ap,M_ap'),
 \qquad
 d_b=\operatorname{TV}(M_bp,M_bp').
 \tag{4.4}
\]

Then

\[
 \boxed{
 \operatorname{TV}(p,p')
 \le d_a+d_b-d_ad_b.}
 \tag{4.5}
\]

The bound is sharp, already for two binary factors.  Equivalently, if
`D_j=||M_jp-M_jp'||_1`, then

\[
 \boxed{
 \|p-p'\|_1
 \le D_a+D_b-\frac12D_aD_b
 \le D_a+D_b.}
 \tag{4.6}
\]

#### Proof

The factor `q_a` is a marginal of `M_bp`, so total variation contracts to

\[
 \operatorname{TV}(q_a,q_a')\le d_b.
\]

Write `p=q_a tensor M_ap` and similarly for `p'`.  Independently couple the
two factor pairs with maximal couplings.  The probability that at least one
pair disagrees is at most

\[
 1-(1-d_a)(1-d_b),
\]

which proves (4.5).  Equality is attained by comparing a point mass with two
independently contaminated binary factors.  Equation (4.6) follows from
`||mu-nu||_1=2 TV(mu,nu)`. \(\square\)

### Corollary 4.3 — explicit noisy decoder and minimax bracket

Let `0<=epsilon_a,epsilon_b<=1`, and let `Y_a,Y_b` be probability-valued
observations satisfying

\[
 \operatorname{TV}(Y_a,M_ap)\le\varepsilon_a,
 \qquad
 \operatorname{TV}(Y_b,M_bp)\le\varepsilon_b.
 \tag{4.7}
\]

Set

\[
 \widehat q_a=\operatorname{Marg}_a(Y_b),
 \qquad
 \widehat p=\widehat q_a\otimes Y_a.
 \tag{4.8}
\]

Then `p_hat` is a probability tensor and

\[
 \boxed{
 \operatorname{TV}(\widehat p,p)
 \le\varepsilon_a+\varepsilon_b-
 \varepsilon_a\varepsilon_b.}
 \tag{4.9}
\]

It need not itself be fully factorized because `Y_a` may contain correlations.
If a product-valued answer is required, set

\[
 \widehat q_a=\operatorname{Marg}_a(Y_b),
 \qquad
 \widehat q_b=\operatorname{Marg}_b(Y_a),
\]

and for `k` outside `{a,b}` take the `k`-marginal of whichever observation has
the smaller declared radius.  The resulting product estimate obeys

\[
 \operatorname{TV}(\widehat p_{\rm prod},p)
 \le1-(1-\varepsilon_a)(1-\varepsilon_b)
 (1-\min\{\varepsilon_a,\varepsilon_b\})^{r-2}.
 \tag{4.10}
\]

Assume `0<=epsilon_a,epsilon_b<=1`.  Define `R*(epsilon_a,epsilon_b)` as the
infimum over all decoders with probability-tensor output of the worst-case TV
loss, where the supremum ranges over `p in P_{r,s}` and probability-valued
`Y_a,Y_b` satisfying (4.7).  When both radii are at most `1/2`,

\[
 \boxed{
 \varepsilon_a+\varepsilon_b-2\varepsilon_a\varepsilon_b
 \le R^*(\varepsilon_a,\varepsilon_b)
 \le\varepsilon_a+\varepsilon_b-\varepsilon_a\varepsilon_b.}
 \tag{4.11}
\]

The upper bound is (4.9).  The lower bound follows from a binary two-point
common-midpoint construction: compare the all-zero point mass with a product
whose `a` factor moves mass `2 epsilon_b` and whose `b` factor moves mass
`2 epsilon_a` to state one.  Their two marginal distances are exactly twice
the allowed radii, while half their source distance is the lower expression
in (4.11).  Thus the leading additive constant is minimax sharp as the noise
vanishes, although an exact finite-radius minimax identity is not claimed.

The probability-valued assumption is explicit.  Arbitrary signed additive
noise requires a projection or normalization rule and has a different
constant; no stochastic noise model is silently assumed.

---

## 5. Exact nonlinear distinguishability geometry

Use the calibrated marginal operators from Arithmetic Observability I,

\[
 R_j=s^{-1/2}M_j,
 \qquad
 O_wp=(\sqrt{w_j}R_jp)_{j=1}^r,
 \qquad
 w_j\ge0,
 \quad\sum_jw_j=1.
 \tag{5.1}
\]

Unobserved axes have weight zero.  For two product distributions
`p=otimes q_k` and `p'=otimes q'_k`, their exact squared observational
pseudodistance is

\[
 \boxed{
 d_w(p,p')^2
 =\frac1s\sum_{j=1}^rw_j
 \left\|
 \bigotimes_{k\ne j}q_k-
 \bigotimes_{k\ne j}q'_k
 \right\|_2^2.}
 \tag{5.2}
\]

Each summand can be evaluated without constructing an ambient tensor:

\[
 \left\|\bigotimes q_k-\bigotimes q'_k\right\|_2^2
 =\prod_k\|q_k\|_2^2
 +\prod_k\|q'_k\|_2^2
 -2\prod_k\langle q_k,q'_k\rangle,
 \tag{5.3}
\]

with the omitted index removed from every product.  Equations (5.2)--(5.3)
are a global, nonlinear distinguishability pseudogeometry on the model.  It
is a genuine metric on `P_{r,s}` exactly when at least two axes have positive
weight; this is Theorem 4.1 applied to the zero-distance condition.

### 5.1 Pullback metric at the uniform product

Let

\[
 q_0=\frac1s\mathbf1,
 \qquad
 p_0=q_0^{\otimes r}.
\]

A product-manifold tangent is

\[
 \dot p
 =\sum_{j=1}^r
 q_0^{\otimes(j-1)}\otimes h_j
 \otimes q_0^{\otimes(r-j)},
 \qquad
 \mathbf1^{\mathsf T}h_j=0.
 \tag{5.4}
\]

The factor blocks are orthogonal.  Their inherited ambient source metric is

\[
 g_{\rm src}(h,h)
 =s^{-(r-1)}\sum_{j=1}^r\|h_j\|_2^2.
 \tag{5.5}
\]

### Theorem 5.1 — exact tangent spectrum and optimal weights

At `p_0`, the observation pullback metric is

\[
 \boxed{
 g_{\rm obs}(h,h)
 =s^{-(r-1)}
 \sum_{j=1}^r(1-w_j)\|h_j\|_2^2.}
 \tag{5.6}
\]

Relative to (5.5), the generalized spectrum is

\[
 \boxed{1-w_j\quad\text{with multiplicity }s-1}
 \tag{5.7}
\]

for each factor, and the sharp tangent floor is

\[
 \boxed{\gamma_{\rm product}(w)=1-\max_jw_j.}
 \tag{5.8}
\]

If exactly `m` axes have positive weight, the largest possible floor is

\[
 1-\frac1m,
 \tag{5.9}
\]

attained exactly by uniform weights on those axes.  Thus the minimal
two-axis globally injective design has optimal tangent floor `1/2`; all `r`
uniform axes have floor `(r-1)/r`.  A free total-mass direction has
generalized eigenvalue one.

#### Proof

The `j`-th tangent block lies in the one-factor ANOVA space `H_{ {j}}`.
The calibrated Gram from Arithmetic Observability I has eigenvalue

\[
 \sum_{a\ne j}w_a=1-w_j
\]

on that space.  Orthogonality gives (5.6)--(5.7).  The smallest eigenvalue is
`1-max w_j`.  On a support of size `m`, `max w_j>=1/m`, with equality exactly
for uniform weights.  The mass direction is the constant ANOVA component,
whose eigenvalue is `sum w_j=1`. \(\square\)

The one-axis case has `w_a=1`, so factor direction `a` has eigenvalue zero.
This is precisely the infinitesimal form of the global omitted-factor
collision in Theorem 4.1.

### 5.2 Geometric local-factor coordinates

For the normalized geometric factor

\[
 q_\theta(a)=\frac{e^{a\theta}}
 {\sum_{b=0}^{s-1}e^{b\theta}},
\]

one has at `theta=0`

\[
 \left\|\frac{dq_\theta}{d\theta}\right\|_2^2
 =\frac{s^2-1}{12s}.
 \tag{5.10}
\]

Therefore the absolute observation metric in the `r` scalar log-parameters
is

\[
 \boxed{
 g_{\rm obs}
 =\frac{s^2-1}{12s^r}
 \sum_{j=1}^r(1-w_j)d\theta_j^2.}
 \tag{5.11}
\]

If log total mass is included, its orthogonal coefficient is `s^{-r}` at unit
total mass and `A^2s^{-r}` at mass `A`; its relative eigenvalue is one.

---

## 6. Canonical exact model: `r=3`, `s=4`

For `(2,3,5)` with four exponent states, the ambient coefficient space has
dimension 64 and the linear blind interaction has dimension 27.  The
normalized product manifold has dimension nine.

With only two selected axes, the ambient linear common kernel is even larger:

\[
 \dim\ker(M_a,M_b)
 =(s-1)^2s^{r-2}=36.
 \tag{6.1}
\]

Nevertheless, its intersection with the product secant set is zero.  One
axis has ambient kernel dimension 48 and a genuine three-dimensional hidden
factor fibre on the product model.  This contrast makes the result nonlinear
model reduction, not disappearance of the linear kernel.

The exact certificate verifies:

1. two chosen marginals reconstruct a nontrivial rational product tensor;
2. one marginal has an explicit pair of distinct product distributions with
   identical data;
3. the free-scale points

   \[
   (C,u_1,u_2,u_3)=(15,0,-1,-1)
   \quad\text{and}\quad
   (1,2,-1,-1)
   \tag{6.2}
   \]

   have identical all-axis margins, because `Q_4(-1)=0` and
   `15Q_4(0)=Q_4(2)=15`;
4. the exact difference in (6.2) lies in
   `W_1 tensor W_2 tensor W_3`;
5. with weights `(1/3,1/3,1/3)`, the nine-dimensional product tangent has
   generalized eigenvalue `2/3` with multiplicity nine; and
6. with weights `(1/2,1/2,0)`, it has eigenvalue `1/2` with multiplicity six
   and eigenvalue one with multiplicity three.

All calculations use integers and `fractions.Fraction`; no floating point is
needed.

---

## 7. What has and has not been learned

### Proved

1. The ambient marginal kernel need not produce a collision on a nonlinear
   multiplicative source class.
2. Two resonant axes are globally necessary and sufficient for arbitrary
   normalized products and for positive free-scale geometric tensors.
3. The complex failure locus, its exact fibres, and its codimension are
   explicit.
4. The two-margin probability reconstruction has an explicit `l1` stability
   bound.
5. The global observation distance and uniform-product tangent spectrum are
   explicit.
6. Minimal acquisition and E-optimal local stability trade off cleanly: two
   axes suffice with best floor `1/2`, while all axes improve the floor to
   `(r-1)/r`.

### Not proved

1. That natural Dedekind, automorphic, or Euler-product coefficient families
   are exactly rank-one on a finite prime box.
2. Stability of the complex free-scale inverse near `E_J`; it necessarily
   deteriorates as usable contractions approach zero.
3. Minimality in individual harmonic readings.  A parametric decoder may not
   need all `s^(r-1)` samples of a general marginal block.
4. Robustness to off-box tails, model mismatch, phase error, or unknown
   primes.
5. A global Euclidean bi-Lipschitz constant on the full product simplex;
   Theorem 4.2 instead gives a constructive `l1` guarantee.

The negative result is as important as the positive one: multiplicativity
does not erase the linear kernel.  It makes the positive model transverse to
that kernel, while complex root-of-unity factors can enter it exactly.

---

## 8. Reproduction

The exact certificate uses only the Python standard library:

```bash
python arithmetic_observability_multiplicative.py \
  --verify arithmetic_observability_multiplicative_certificate.json
```

Run its adversarial tests with:

```bash
python -m unittest -v \
  test_arithmetic_observability_multiplicative.py
```

The canonical payload SHA-256 is

```text
5805a3f385a6b5a0728d38413c9a0cb76d15b59285f671021ff749a6c4ea6a24
```

The final file SHA-256 values are:

```text
8a6debaf952abd47d25b7e3bb8b43d39b1694bc5e06210cb1a897dff958295f2  arithmetic_observability_multiplicative.py
79d42f1a5d5ddf7f305647824918466700bb178ffd016c6fc50cf399c9bdbf6c  arithmetic_observability_multiplicative_certificate.json
84a59d8c5c96c60e8a5649bbf242be3e208c2a546e88dcd8b0d1fc410297b9fd  test_arithmetic_observability_multiplicative.py
```

The focused suite contains 34 tests.  A combined Arithmetic Observability
I--III regression contains 84 tests.  Independent reconstruction was also
performed on Windows with Python 3.13; the deterministic binary writer makes
the regenerated certificate byte-identical across the tested platforms.

---

## 9. Relation to existing mathematics and novelty boundary

The resonant marginal acquisition, ANOVA kernel, and calibrated spectrum are
inherited from Arithmetic Observability I.  Segre products, tensor
marginalization, coupling bounds for product measures, and pullback metrics
are standard mathematics.

Finite product distributions form the nonnegative part of the Segre, or
complete-independence, model.  Marginal observations and their fibres are
classical objects in algebraic statistics: Vorob'ev studied consistency of
marginal families; Diaconis and Sturmfels developed fixed-margin fibres; and
Kirkup described the decomposition into an independent table plus a common
marginal-kernel term.  More generally, two complementary clique marginals
determine the clique--separator combination in a decomposable graphical
model.  Thus identification of a product law from margins covering every
coordinate is not presented as new; Theorem 4.1 is its sharp specialization
to the complementary-margin protocol used here.

The product-coupling inequality underlying Theorem 4.2 is also standard, as
is the product information geometry of independence models.  At the uniform
law, the Fisher metric is proportional to the calibrated Euclidean metric in
Section 5, so the two geometries have the same generalized eigenvalues.
Uniform weighting is an instance of classical E-optimal design.

The contribution asserted within this programme is the arithmetic,
field-sensitive synthesis: the contraction functional becomes exactly
`Q_s(u_j)`; its cyclotomic zeros give the complete exceptional set and exact
one-/zero-block fibres; and the resulting source geometry can be compared
exactly with the ambient arithmetic blind space.  We make no priority claim
for the classical ingredients or an unsupported claim of uniqueness in the
literature.

### References for Section 9

- V. Vorob'ev, *Consistent Families of Measures and Their Extensions*,
  Theory of Probability and Its Applications 7 (1962),
  [doi:10.1137/1107014](https://doi.org/10.1137/1107014).
- P. Diaconis and B. Sturmfels, *Algebraic Algorithms for Sampling from
  Conditional Distributions*, Annals of Statistics 26 (1998),
  [doi:10.1214/aos/1030563990](https://doi.org/10.1214/aos/1030563990).
- B. Kirkup, *Random Variables with Completely Independent Subcollections*,
  Journal of Algebra 309 (2007),
  [doi:10.1016/j.jalgebra.2006.06.023](https://doi.org/10.1016/j.jalgebra.2006.06.023).
- J. Darroch, S. Lauritzen, and T. Speed, *Markov Fields and Log-Linear
  Interaction Models for Contingency Tables*, Annals of Statistics 8 (1980),
  [doi:10.1214/aos/1176345006](https://doi.org/10.1214/aos/1176345006).
- A. Dawid and S. Lauritzen, *Hyper Markov Laws in the Statistical Analysis
  of Decomposable Graphical Models*, Annals of Statistics 21 (1993),
  [doi:10.1214/aos/1176349260](https://doi.org/10.1214/aos/1176349260).
- J. M. Landsberg, *Tensors: Geometry and Applications*, AMS (2012),
  [doi:10.1090/gsm/128](https://doi.org/10.1090/gsm/128).
- A. Breiding et al., *Algebraic Compressed Sensing*, Applied and
  Computational Harmonic Analysis 65 (2023),
  [doi:10.1016/j.acha.2023.03.006](https://doi.org/10.1016/j.acha.2023.03.006).
- A. Kontorovich, *Obtaining Measure Concentration from Markov Contraction*,
  Markov Processes and Related Fields 18 (2012),
  [arXiv:0711.0987](https://arxiv.org/abs/0711.0987).
- G. Montufar, J. Rauh, and N. Ay, *On the Fisher Metric of Conditional
  Probability Polytopes*, Entropy 16 (2014),
  [doi:10.3390/e16063207](https://doi.org/10.3390/e16063207).
- J. Kiefer, *Optimum Experimental Designs*, Journal of the Royal Statistical
  Society B 21 (1959),
  [doi:10.1111/j.2517-6161.1959.tb00338.x](https://doi.org/10.1111/j.2517-6161.1959.tb00338.x).

---

## 10. Questions forced by the result

1. **Individual-reading complexity.**  Exploit the low parameter dimension
   to replace complete marginal reconstruction by a smaller resonant sample
   set, with a sharp lower bound.
2. **Near-multiplicative models.**  Quantify how observation stability degrades
   with tensor rank, interaction strength, or distance from the Segre variety.
3. **Natural Euler families.**  Replace free factors by local polynomial
   constraints arising from actual arithmetic objects.
4. **Tail-compatible products.**  Add compact divisor-bounded tails and test
   whether multiplicative transversality survives in the observation fibres.
5. **Exceptional-locus sensing.**  Design the cheapest nonresonant trace that
   resolves root-of-unity degeneracies without completing the whole ambient
   space.

The central conclusion is structural: observability belongs to a pair—the
protocol and the admissible source geometry.  A 27-dimensional ambient blind
space can coexist with global two-axis identifiability on a nine-dimensional
multiplicative manifold, and both statements can be exactly true.
