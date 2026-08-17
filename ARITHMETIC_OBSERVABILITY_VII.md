# Arithmetic Observability VII

## Discrete queries against bounded continuous tails

### Query-local separation, a near-sharp four-anchor certificate, and the finite-schedule continuous no-go boundary

- **Research lead, theorem synthesis, computation design, and manuscript:** Codex (OpenAI)
- **Originating question and research environment:** TGN's human founder
- **Status:** research manuscript with reproducible finite certificate; not peer reviewed
- **Date:** 15 August 2026
- **Parent manuscripts:** `ARITHMETIC_OBSERVABILITY_I.md` and `ARITHMETIC_SENSING_V_MULTISCALE.md`

## Abstract

Arithmetic Observability I converted a degree-fourteen Arithmetic Sensing V
certificate into a uniform separation theorem for all fifty recovered
coefficients.  That global question is much harder than many natural local
queries.  This paper develops the query-local theory and identifies the
structural boundary responsible for the improvement within a declared model
of independently variable tails whose modes span the finite data space.

Let a finite harmonic experiment have response fibres

\[
 \mathcal F_a=Aa+\mathcal T_a,
\]

and suppose a reconstruction functional `ell_n` reads coordinate `a_n`
exactly before the tail is added.  If its tail bias is at most `B_n` and its
data norm is `kappa_n`, then every pair obeys the anisotropic bound

\[
 \operatorname{dist}(\mathcal F_a,\mathcal F_b)
 \ge
 \max_{n\in I}
 \frac{(|a_n-b_n|-2B_n)_+}{\kappa_n}.
 \tag{A.1}
\]

Only the queried labels need a positive spacing.  The tails and all unqueried
prefix coordinates may be continuous.  In the unit-spaced case,
`B_n<1/2` makes the query exactly identifiable and gives a certified noise
radius `(1/2-B_n)/kappa_n`.  Thus the essential positive mechanism is a
discrete query gap, not tail integrality.

For the pinned Arithmetic Sensing V multiscale experiment, exact rational
finite and remote tail bounds give

\[
 B_n=n^2\left(\tau_n+q_n\frac{\tau}{1-q}\right).
 \tag{A.2}
\]

A classical row-local Schur-complement refinement gives

\[
 \kappa_n^2
 \le \bar\kappa_n^2
 :=n^4\frac{1-q}{1-q-q_n^2}.
 \tag{A.3}
\]

For the four-anchor query `I={1,2,3,5}`, the bottleneck is `n=5` and the
formally certified sufficient noise radius is

\[
 \varepsilon_I
 =0.019717406682172976\ldots .
 \tag{A.4}
\]

Two zero-tail prefixes differing by one at `n=5` give the obstruction
`epsilon_I^*<=1/50=0.02`.  The certified bracket therefore has ratio only
`1.01433...`; it is near-sharp but is not claimed to be the exact minimax
radius.  On multiplicative nonnegative sequences, the same four anchors
recover the normalized two-state product core at primes `2,3,5`.

The opposite side of the boundary is exact.  A finite exponential polynomial
that vanishes on an unbounded sampling set whose mesh tends to zero is
identically zero.  Since `log(n+1)-log n` tends to zero, the integer-indexed tail
phasors above every cutoff span the complete finite complex data space over
the reals.  Consequently, whenever continuously variable tail intervals
contain a spanning subset, their difference set contains a neighbourhood of
zero.  Every genuinely interval-valued continuous query then has exact local
collisions at every positive tail scale.

For the canonical three-reading schedule used in Arithmetic Observability V,
six explicit off-box degree-fourteen modes give a quantitative version.  A
384-bit Arb certificate proves that their realified synthesis matrix has
smallest singular value greater than five.  At full envelope their tail
difference zonotope can cancel every pair of normalized `4 x 4 x 4` product
sources.  This does not contradict the positive four-anchor theorem: a
continuous source has arbitrarily small distinctions, whereas a unit-spaced
query does not.

The general analytic theorems are proved below.  The companion certificate
checks the pinned Arithmetic Sensing V dependency, reconstructs every exact
rational bound, and verifies the six-mode interval inequalities.  It does not
mechanize the analytic proofs or assert realizability of every admissible
coefficient vector by a number field.

---

## 1. The arithmetic boundary

There are two superficially similar but mathematically different questions.

1. Can a finite harmonic experiment distinguish labels drawn from a lattice
   or another separated set despite a bounded tail?
2. Can the same experiment distinguish every point of a continuous model
   after that model is thickened by an arbitrarily small continuous tail?

The first can have a positive answer because distinct query labels have a
fixed gap.  The second has a negative answer in the full-dimensional-tail
model proved below: continuous models contain arbitrarily close distinctions,
while independently variable tail intervals whose modes span the data space
fill a neighbourhood of the data origin.  No such conclusion is asserted for
a lower-dimensional or coupled tail family that fails this spanning premise.

This paper makes that division quantitative.  No assumption of integrality is
placed on the tail.  Indeed, the positive Arithmetic Sensing V estimate was
already derived by domination and triangle inequalities and therefore holds
for every real or complex tail inside the certified envelope.  Likewise,
unqueried prefix coordinates may vary continuously.  What matters is only
that distinct values of each queried coordinate have a declared minimum
spacing.

### 1.1 Response fibres

Let `Y` be a finite-dimensional real or complex Hilbert space, let

\[
 A:X\longrightarrow Y
 \tag{1.1}
\]

be a linear prefix observation, and let `Lambda` be the admissible prefix
class.  A prefix `a` has a possibly prefix-dependent tail-response set
`T_a subset Y` and response fibre

\[
 \mathcal F_a=Aa+\mathcal T_a.
 \tag{1.2}
\]

Fix a finite coordinate set `I`.  Its query is

\[
 Q_I(a)=(a_n)_{n\in I}.
 \tag{1.3}
\]

For every `n in I`, suppose a bounded linear functional
`ell_n:Y->C` satisfies

\[
 \ell_n(Aa)=a_n
 \quad(a\in\Lambda).
 \tag{1.4}
\]

The queried labels may be real, but it is convenient to allow the harmonic
functional to be complex.  Put

\[
 \kappa_n=\|\ell_n\|,
 \qquad
 B_n=\sup_{a\in\Lambda}\sup_{t\in\mathcal T_a}|\ell_n(t)|.
 \tag{1.5}
\]

No common-subspace assumption is made on the tails.

---

## 2. Query-local fibre separation

### Theorem 2.1 — anisotropic query separation

For every two prefixes `a,b in Lambda`,

\[
 \boxed{
 \operatorname{dist}(\mathcal F_a,\mathcal F_b)
 \ge
 D_I(a,b)
 :=\max_{n\in I}
 \frac{(|a_n-b_n|-2B_n)_+}{\kappa_n}.}
 \tag{2.1}
\]

Terms with `kappa_n=0` are interpreted in the natural way: (1.4) then forces
that coordinate to be constant, so it may be deleted from the query.

#### Proof

Choose `y=Aa+t` and `y'=Ab+t'` from the two fibres.  For every queried
coordinate,

\[
 \begin{aligned}
 \kappa_n\|y-y'\|_Y
 &\ge |\ell_n(y-y')|\\
 &=|(a_n-b_n)+\ell_n(t-t')|\\
 &\ge |a_n-b_n|-2B_n.
 \end{aligned}
 \tag{2.2}
\]

Take the positive part, then the maximum over `n`, and finally the infimum
over `y,y'`.  \(\square\)

The gauge `D_I` is more informative than a single worst-case constant.  It
records both the coordinate gap and the anisotropic cost of reading that
coordinate.  Because subtracting `2B_n` need not preserve the triangle
inequality, `D_I` is deliberately called a separation gauge rather than a
metric.  The actual set distance between arbitrary fibres also need not be a
pseudometric, as noted in Arithmetic Observability I.

### Corollary 2.2 — separated-label observability

Suppose the possible values of coordinate `n` have minimum spacing

\[
 \Delta_n
 =\inf\{|u-v|:u\ne v\text{ are admissible values of }a_n\}>2B_n.
 \tag{2.3}
\]

Then `Q_I` is exactly identifiable.  Under adversarial data noise
`||eta||_Y<=epsilon`, coordinatewise nearest-label decoding is correct when

\[
 \varepsilon
 <\varepsilon_I
 :=\min_{n\in I}\frac{\Delta_n/2-B_n}{\kappa_n}.
 \tag{2.4}
\]

For unit-spaced labels this becomes

\[
 \varepsilon_I
 =\min_{n\in I}\frac{1/2-B_n}{\kappa_n}.
 \tag{2.5}
\]

#### Proof

For `z=Aa+t+eta`,

\[
 |\ell_n(z)-a_n|\le B_n+\kappa_n\varepsilon<\Delta_n/2.
 \tag{2.6}
\]

Thus `a_n` is the unique admissible label nearest `ell_n(z)`.  At zero noise,
the same inequality shows that intersecting fibres have identical queried
labels.  \(\square\)

Literal integrality is one important realization of unit spacing, but it is
not required.  Conversely, integrality of unqueried coordinates is irrelevant
to this theorem.

### 2.1 A genuine lower metric on the query lattice

In the unit-spaced case define

\[
 \delta_n=\frac{1-2B_n}{\kappa_n}>0
 \tag{2.7}
\]

and

\[
 \underline d_I(a,b)
 =\max_{\substack{n\in I\\a_n\ne b_n}}\delta_n,
 \qquad
 \underline d_I(a,b)=0\text{ if }Q_I(a)=Q_I(b).
 \tag{2.8}
\]

This descends to a metric on the query labels: it is the maximum of weighted
discrete coordinate metrics.  Theorem 2.1 gives

\[
 \operatorname{dist}(\mathcal F_a,\mathcal F_b)
 \ge\underline d_I(a,b).
 \tag{2.9}
\]

Thus the tail-eroded gauge (2.1) describes larger coordinate gaps, while
(2.8) supplies an honest distinguishability geometry on the query lattice.

---

## 3. The pinned Arithmetic Sensing V experiment

The specialization uses exactly the formal multiscale artifact

```text
certificates/arithmetic_sensing_v_multiscale_end_to_end.json
```

with degree `14`, cutoff `N=50`, vertical exponent `sigma=2`, and 8,900
distinct centered readings.  The grid is symmetric and has no zero node, so
for real coefficient sequences it may equivalently be represented by 4,450
positive-time complex readings and their determined conjugates.  The Hilbert
normalization below retains the original 8,900-point positive measure; this
observation is not a claim that the certified resource count has changed.
Let `mu` be that positive normalized sampling measure and

\[
 Y=L^2(\mu;\mathbb C).
 \tag{3.1}
\]

Put

\[
 c_n(t)=n^{-it},
 \qquad \|c_n\|_Y=1,
 \tag{3.2}
\]

and let `C:C^50->Y` synthesize the first fifty phase columns.  With

\[
 D=\operatorname{diag}(1^2,2^2,\ldots,50^2),
 \qquad G=C^*C,
 \tag{3.3}
\]

the prefix observation on `Re(s)=2` is

\[
 A=CD^{-1}.
 \tag{3.4}
\]

The Gram matrix has exact diagonal one.  Write

\[
 G=I+E,
 \qquad
 q_n\ge\sum_{j\ne n}|E_{nj}|,
 \qquad
 q=\max_nq_n<1.
 \tag{3.5}
\]

The least-squares reconstruction map is

\[
 R=DG^{-1}C^*,
 \qquad RA=I.
 \tag{3.6}
\]

Let `ell_n` be row `n` of `R`.

### 3.1 Exact coordinatewise tail bounds

For every certified tail response `t`, the source artifact encloses its
correlation vector

\[
 e=C^*t,
 \qquad |e_n|\le\tau_n,
 \qquad \tau=\max_n\tau_n.
 \tag{3.7}
\]

All `tau_n`, `q_n`, `tau`, and `q` used here are exact dyadic rationals.  Put
`x=G^{-1}e`.  Since

\[
 x=e-Ex,
 \tag{3.8}
\]

the Neumann estimate gives

\[
 \|x\|_\infty\le\frac{\tau}{1-q}
 \tag{3.9}
\]

and, on returning to row `n`,

\[
 |x_n|
 \le\tau_n+q_n\frac{\tau}{1-q}.
 \tag{3.10}
\]

Therefore

\[
 \boxed{
 B_n
 =n^2\left(\tau_n+q_n\frac{\tau}{1-q}\right)}
 \tag{3.11}
\]

is a certified coordinatewise upper bound on the true tail bias.  The value
on the right is an exact rational formula, not a floating-point inverse of
`G`; equality with the worst attainable bias is not claimed.

Crucially, the argument uses only the magnitude bounds (3.7).  Tail
coefficients may vary continuously inside the declared degree-fourteen
envelope.  The positive theorem below is therefore not a tail-integrality
theorem.

---

## 4. A classical row-local Schur refinement

The global Gershgorin estimate in Arithmetic Observability I used

\[
 \kappa_n^2\le\frac{n^4}{1-q}.
 \tag{4.1}
\]

That is adequate for all fifty coordinates but wastes the exceptionally small
row defects at `n=1,2,3,5`.  The following is a classical block-inverse and
Schur-complement refinement, specialized here to the certified arithmetic
rows; no novelty is claimed for the matrix inequality itself.

### Theorem 4.1 — localized diagonal inverse bound

Suppose `G` is Hermitian, `G_nn=1`, and (3.5) holds.  If

\[
 1-q-q_n^2>0,
 \tag{4.2}
\]

then

\[
 (G^{-1})_{nn}
 \le\frac{1-q}{1-q-q_n^2}.
 \tag{4.3}
\]

Consequently,

\[
 \boxed{
 \kappa_n^2=\|\ell_n\|^2
 =n^4(G^{-1})_{nn}
 \le
 \bar\kappa_n^2
 :=n^4\frac{1-q}{1-q-q_n^2}.}
 \tag{4.4}
\]

#### Proof

Permute coordinate `n` first and write

\[
 G=
 \begin{pmatrix}
 1&g^*\\
 g&H
 \end{pmatrix}.
 \tag{4.5}
\]

Gershgorin gives `lambda_min(G)>=1-q`; the same bound holds for the
principal block `H` by interlacing.  Moreover,

\[
 \|g\|_2\le\|g\|_1\le q_n.
 \tag{4.6}
\]

The block inverse formula and positivity give

\[
 (G^{-1})_{nn}
 =\frac1{1-g^*H^{-1}g},
 \tag{4.7}
\]

while

\[
 0\le g^*H^{-1}g
 \le\frac{q_n^2}{1-q}.
 \tag{4.8}
\]

Equations (4.2), (4.7), and (4.8) prove (4.3).  Finally,

\[
 \begin{aligned}
 \|\ell_n\|^2
 &=n^4e_n^*G^{-1}C^*CG^{-1}e_n\\
 &=n^4(G^{-1})_{nn},
 \end{aligned}
 \tag{4.9}
\]

which proves (4.4).  \(\square\)

The improvement is second order in the local row defect `q_n`, rather than
first order in the global maximum `q`.

### Corollary 4.2 — exact rational sufficient radii

For unit-spaced coordinate `n`, define

\[
 \boxed{
 \varepsilon_{n,\mathrm{Schur}}^2
 =\left(\frac12-B_n\right)^2
 \frac{1-q-q_n^2}{n^4(1-q)}.}
 \tag{4.10}
\]

Then every noise radius below `epsilon_n,Schur` is certified safe for that
coordinate.  For comparison, the reproduced global-Gershgorin control is

\[
 \varepsilon_{n,\mathrm{global}}^2
 =\left(\frac12-B_n\right)^2\frac{1-q}{n^4}.
 \tag{4.11}
\]

Both squares are exact rationals in the companion artifact.  They are
sufficient radii, not asserted exact minimax values.

---

## 5. The four-anchor theorem

Take

\[
 I=\{1,2,3,5\}.
 \tag{5.1}
\]

The pinned source has

\[
 \tau
 =\tau_1
 =\frac{184205979003910569407361247228051779}
 {340282366920938463463374607431768211456}
 =0.0005413327192669644\ldots
 \tag{5.2}
\]

and

\[
 q
 =\frac{257168756981514768514508306559006707}
 {340282366920938463463374607431768211456}
 =0.0007557510525994008\ldots .
 \tag{5.3}
\]

Exact substitution into (3.11), (4.10), and (4.11) gives the following
descriptive decimals.  The machine-readable artifact stores the complete
rational numerators and denominators.

| `n` | certified `B_n` | global control radius | Schur radius | certified unit fibre gap `2 epsilon_n` |
|---:|---:|---:|---:|---:|
| 1 | `0.0005413328049489775` | `0.49926989831600887` | `0.49945866719504477` | `0.99891733439008954` |
| 2 | `0.0015462579530286658` | `0.12456633824408053` | `0.12461343551173978` | `0.24922687102347957` |
| 3 | `0.0030243219258030983` | `0.05519864973703506` | `0.05521951978601992` | `0.11043903957203985` |
| 5 | `0.0070648329456505926` | `0.01970995454849109` | **`0.019717406682172976`** | **`0.03943481336434595`** |

The `B_n` in this table are four anchor-local certified upper bounds, not the
single all-fifty endpoint and not asserted attained suprema.  Likewise, the
last column consists of certified lower bounds on unit-neighbour fibre gaps.

### Theorem 5.1 — certified four-anchor observability

Under the pinned degree-fourteen tail envelope, any unit-spaced query labels
at `I={1,2,3,5}` are exactly identifiable.  Coordinatewise decoding is
uniformly correct whenever

\[
 \boxed{
 \varepsilon<\varepsilon_I
 :=\min_{n\in I}\varepsilon_{n,\mathrm{Schur}}
 =\varepsilon_{5,\mathrm{Schur}}
 =0.019717406682172976\ldots .}
 \tag{5.4}
\]

The corresponding certified distance between query-distinct fibres is

\[
 \delta_I\ge2\varepsilon_I
 =0.03943481336434595\ldots .
 \tag{5.5}
\]

This theorem remains valid if every tail coefficient and every nonquery
prefix coordinate is continuously variable, provided the same certified
domination bounds hold.

### 5.1 A near-matching obstruction

For the bracket only, declare the broad normalized coefficient-envelope
source class

\[
 \Lambda_{14}
 =\{a\in\mathbb Z_{\ge0}^{50}:
 a_1=1,\ 0\le a_n\le d_{14}(n)\ (2\le n\le50)\},
 \tag{5.6}
\]

and the common continuously variable tail-response box

\[
 \mathcal T_{14}
 =\left\{
 \sum_{k>50}b_k k^{-2}c_k:
 0\le b_k\le d_{14}(k)
 \right\}.
 \tag{5.7}
\]

Every prefix fibre in this subsection is
`F_a=Aa+T_14`.  The normalization `a_1=1` is inherited from the
Dirichlet-series setting.  The tail variables in (5.7) are explicitly
continuous and independently variable; their integrality is neither assumed
nor used.

Define the critical query radius for the declared source class by

\[
 \varepsilon_I^*
 =\frac12\inf_{\substack{a,b\in\Lambda_{14}\\Q_I(a)\ne Q_I(b)}}
 \operatorname{dist}(\mathcal F_a,\mathcal F_b).
 \tag{5.8}
\]

The prefix set `Lambda_14` is finite.  Its coefficient box in (5.7) is compact
in the product topology, and the identity
`sum_k d_14(k) k^-2 = zeta(2)^14 < infinity` gives uniform absolute
convergence of the finite observation map.  Thus `T_14` is compact, the relevant
closest-fibre distance is attained, and a closest-pair midpoint gives the
matching decision obstruction at half that distance.

Let `a^(0)` have `a_1=1` and every other prefix coordinate zero, and put
`a^(1)=a^(0)+e_5`.  Both belong to `Lambda_14` because `d_14(5)=14`, and zero
belongs to the common tail box.  Since the normalized column `c_5` has norm
one, these two query-distinct zero-tail prefixes have data distance

\[
 \|Ae_5\|_Y=\frac1{5^2}=\frac1{25}.
 \tag{5.9}
\]

Their midpoint is consistent with noise radius `1/50`.  Hence the exact
critical radius for the declared four-anchor prefix class satisfies

\[
 \boxed{
 0.019717406682172976\ldots
 \le\varepsilon_I^*
 \le0.02.}
 \tag{5.10}
\]

The endpoint ratio is approximately `1.01433217`, a `1.433%` multiplicative
gap.  This is a near-sharp bracket, not an equality theorem.  The upper pair
belongs to the broad dominated-prefix class; it is not claimed to be realized
by number fields or by the multiplicative product-core subclass below.

### 5.2 Comparison with full-prefix recovery

Arithmetic Observability I certified the all-fifty sufficient radius

\[
 7.8873507724418666\times10^{-7}.
 \tag{5.11}
\]

The new four-anchor *certified lower bound* is between 24,998 and 24,999 times
that earlier certified lower bound.  This comparison is between sufficient
bounds, not exact minimax radii.  A stronger comparison follows from the two
published brackets: using the all-fifty upper radius `2e-4`, the true
four-anchor critical radius is more than `98.58` times the true all-fifty
critical radius for the same broad source class.  Query locality is therefore
not merely a cosmetic reduction of output dimension; it changes the robust
geometry by orders of magnitude.

---

## 6. The normalized prime product core

Suppose now that `a(n)` is a nonnegative multiplicative Dirichlet coefficient
sequence normalized by

\[
 a(1)=1.
 \tag{6.1}
\]

On the Boolean prime box

\[
 \mathcal B_{2,3,5}=\{2^{\alpha_1}3^{\alpha_2}5^{\alpha_3}:
 \alpha_j\in\{0,1\}\},
 \tag{6.2}
\]

multiplicativity gives the exact rank-one tensor

\[
 c_\alpha
 =a(2)^{\alpha_1}a(3)^{\alpha_2}a(5)^{\alpha_3}.
 \tag{6.3}
\]

Thus the four anchors determine

\[
 C=a(1)=1,
 \qquad
 v=(a(2),a(3),a(5)).
 \tag{6.4}
\]

After normalization, (6.3) becomes the product probability

\[
 p_\alpha(v)
 =\prod_{j=1}^3
 \frac{v_j^{\alpha_j}}{1+v_j}
 =\bigotimes_{j=1}^3
 \left(\frac1{1+v_j},\frac{v_j}{1+v_j}\right)_{\!\alpha_j}.
 \tag{6.5}
\]

This is exactly the `s=2` normalized Segre core of Arithmetic Observability
VI, and its unnormalized version is the `s=2` positive geometric core of
Arithmetic Observability V.

### Corollary 6.1 — robust recovery of 512 positive shapes

The choice of eight positive levels is an explicit arithmetic anchor, not an
intrinsic cardinality of the Boolean core.  It is the largest integer grid
compatible with the exponent-three geometric continuation used in the prior
`s=4` prime box: for a prime `p`,

\[
 d_{14}(p)=14,\qquad d_{14}(p^2)=105,\qquad d_{14}(p^3)=560,
 \tag{6.6}
\]

so `v<=8` gives `v^a<=d_14(p^a)` for `a=1,2,3`, whereas
`9^3=729>560`.  This continuation only motivates and certifies the grid size;
the exact arithmetic identity (6.3) remains the Boolean, exponent-zero/one
core and does not assume geometric prime-power coefficients.

Restrict `v_j` to `{1,...,8}`.  The resulting `8^3=512` positive labelled
product shapes are all exactly recovered under the hypotheses of Theorem 5.1
and remain separated by the anisotropic gauge

\[
 \underline D(v,w)
 =\max_{n\in\{2,3,5\}}
 \frac{(|v_n-w_n|-2B_n)_+}{\bar\kappa_n}.
 \tag{6.7}
\]

Here `v_2,v_3,v_5` denote the three prime coordinates and
`bar kappa_n` is (4.4).  Unit neighbours along the 2-, 3-, and 5-directions
have the following certified data-gap lower bounds:

\[
 0.2492268710\ldots,
 \quad0.1104390396\ldots,
 \quad0.0394348134\ldots .
 \tag{6.8}
\]

The geometry is strongly anisotropic: the prime-5 anchor is the expensive
direction.  Allowing `v_j=0` gives `9^3=729` nonnegative boundary shapes, with
the convention `v^0=1`; those boundary points are covered by the query theorem
but are not silently included in the positive `8^3` count.

Equation (6.3) uses multiplicativity.  For a general dominated but
nonmultiplicative sequence, `(a_2,a_3,a_5)` still defines a product surrogate,
but it need not equal the actual composite coefficients.  No claim about
number-field realizability of all 512 grid points is made.

---

## 7. Vanishing-mesh uniqueness

The negative theorem begins with an elementary fact about exponential
polynomials.

### Lemma 7.1 — vanishing-mesh uniqueness

Let

\[
 f(x)=\sum_{j=1}^Jd_je^{i\xi_jx},
 \tag{7.1}
\]

where the real frequencies `xi_j` are distinct.  Let
`x_1<x_2<...` be unbounded and satisfy

\[
 x_{k+1}-x_k\longrightarrow0.
 \tag{7.2}
\]

If `f(x_k)=0` for every sufficiently large `k`, then every `d_j=0`.

#### Proof

The derivative of `f` is bounded.  Between consecutive large zeros,

\[
 |f(x)|
 \le\|f'\|_\infty(x_{k+1}-x_k),
 \tag{7.3}
\]

so `f(x)->0` as `x->infinity`.  On the other hand, direct integration gives

\[
 \frac1L\int_0^L|f(x)|^2\,dx
 \longrightarrow\sum_{j=1}^J|d_j|^2,
 \tag{7.4}
\]

because every cross-frequency average tends to zero.  The left side must tend
to zero by (7.3), so all coefficients vanish.  \(\square\)

This is a finite almost-periodic uniqueness argument.  Its arithmetic content
enters only through the next substitution.

### Theorem 7.2 — integer-indexed tail phasors span every finite schedule

Let `0<t_1<...<t_m` be distinct and let `sigma` be real.  For an integer
`n>=1`, put

\[
 v_n=(n^{-\sigma-it_1},\ldots,n^{-\sigma-it_m})\in\mathbb C^m.
 \tag{7.5}
\]

For every cutoff `N`,

\[
 \boxed{
 \operatorname{span}_{\mathbb R}\{v_n:n>N\}=\mathbb C^m.}
 \tag{7.6}
\]

Consequently some `2m` integer modes above `N` form a real basis.

#### Proof

The positive scalar `n^-sigma` does not affect real span.  If (7.6) failed,
there would be a nonzero real functional on `C^m` annihilating every tail
mode.  Every such functional has the form

\[
 L(z)=\operatorname{Re}\sum_{j=1}^m\gamma_jz_j.
 \tag{7.7}
\]

Thus, for all integers `n>N`,

\[
 0=2L((n^{-it_j})_j)
 =\sum_j\gamma_je^{-it_j\log n}
  +\sum_j\overline{\gamma_j}e^{it_j\log n}.
 \tag{7.8}
\]

Because the `t_j` are positive and distinct, the `2m` frequencies
`{-t_j,t_j}` are distinct.  The sampling set `x_n=log n` is unbounded and

\[
 \log(n+1)-\log n\longrightarrow0.
 \tag{7.9}
\]

Lemma 7.1 forces all `gamma_j=0`, a contradiction.  Finite dimensionality
then supplies a basis from finitely many modes.  \(\square\)

For a symmetric schedule, negative times carry the conjugate data of positive
times for real coefficients; the theorem applies to its positive half.  A
zero-time coordinate can be included by adding frequency zero and replacing
`C^m` with the corresponding real-conjugate data space.

---

## 8. Continuous-tail neighbourhoods and exact collisions

### Theorem 8.1 — continuous tail difference has interior

Fix a finite positive schedule and cutoff `N`.  Suppose the coefficient of
each mode in some spanning tail set may independently vary in a real interval
with nonempty interior.  Then the tail difference set

\[
 \mathcal T-\mathcal T
 \tag{8.1}
\]

contains an open neighbourhood of zero in the complete realified data space.

If all interval widths are scaled by `rho>0`, the neighbourhood radius scales
linearly with `rho`.

#### Proof

Choose `2m` basis modes using Theorem 7.2.  The difference of every
nondegenerate coefficient interval contains a symmetric interval about zero.
The synthesis map from the resulting `2m`-dimensional coefficient box to the
realified data space is an invertible real linear map.  It maps a
neighbourhood of the coefficient origin to a neighbourhood of the data
origin.  Scaling the box scales its image.  \(\square\)

### Corollary 8.2 — no local exact observability of a continuous query

Let `M` contain a curve `p(s)` through `p(0)` such that the map
`s -> H(p(s))` is continuous at zero.  Assume there is a sequence `s_k -> 0`,
with `s_k != 0`, for which

\[
 Q(p(s_k))\ne Q(p(0)).
 \tag{8.2}
\]

For each `rho>0`, assume every point of this curve has the same tail-response
box `T_rho`, its spanning coordinates vary independently, and `T_rho` is the
scale-`rho` box of Theorem 8.1.  Then, for every `rho>0`, all sufficiently
large `k` give query-distinct curve points with intersecting response fibres.

#### Proof

Fix `rho>0`.  Theorem 8.1 supplies an open neighbourhood `U_rho` of zero with

\[
 U_\rho\subseteq\mathcal T_\rho-\mathcal T_\rho.
 \tag{8.3}
\]

Continuity of `s -> H(p(s))` at zero gives
`H(p(s_k)-p(0)) -> 0`, so this difference belongs to `U_rho` for all large `k`.
Thus there are `u_k,v_k in T_rho` such that

\[
 H(p(s_k)-p(0))=u_k-v_k,
 \qquad
 H p(s_k)+v_k=H p(0)+u_k.
 \tag{8.4}
\]

The two common-tail fibres intersect, while (8.2) makes their query labels
genuinely different.  \(\square\)

This result is exact, not a condition-number warning.  It also explains why
the queried-label spacing in Corollary 2.2 cannot simply be deleted.  A
genuinely interval-valued coordinate has `Delta_n=0`; arbitrarily small
continuous tail freedom can then cancel arbitrarily small query changes.

There is no contradiction with Theorem 5.1.  Its queried values are separated
even though its tails may already be continuous.

---

## 9. A six-mode quantitative collapse certificate

The general spanning theorem is qualitative.  The following finite witness
measures the size of one tail neighbourhood.

Use the canonical three-reading schedule from Arithmetic Observability V,

\[
 T_*=\left(
 \frac{245943}{1000},
 \frac{281062}{1000},
 \frac{960832}{1000}
 \right),
 \tag{9.1}
\]

The companion AO-VII verifier hardcodes the three rational numbers in (9.1)
and evaluates them directly.  It does not import, trust, or digest-bind an
Arithmetic Observability V certificate; the earlier manuscript is provenance
for the schedule, not a formal dependency of this finite claim.

Take the six off-box modes

\[
 S=\{64,144,168,240,768,2880\}.
 \tag{9.2}
\]

Their exact degree-fourteen vertical-line amplitude envelopes are

| `n` | `d_14(n)/n^2` |
|---:|:---|
| 64 | `6783/1024` |
| 144 | `20825/1728` |
| 168 | `35/9` |
| 240 | `5831/720` |
| 768 | `79135/16384` |
| 2880 | `110789/23040` |

Let `w_n=d_14(n)/n^2`.  Realify the three complex readings and form the
`6 x 6` matrix with column

\[
 W_n=w_n\bigl(
 \cos(t_1\log n),-\sin(t_1\log n),
 \cos(t_2\log n),-\sin(t_2\log n),
 \cos(t_3\log n),-\sin(t_3\log n)
 \bigr)^T.
 \tag{9.3}
\]

### Certified finite statement

The companion 384-bit Arb verifier proves by exact rational lower endpoints
and Sylvester's criterion that

\[
 WW^T-25I\succ0.
 \tag{9.4}
\]

Therefore

\[
 \sigma_{\min}(W)>5.
 \tag{9.5}
\]

The modes in (9.2) all lie outside the prime box

\[
 \{2^a3^b5^c:0\le a,b,c\le3\}.
 \tag{9.6}
\]

### Theorem 9.1 — quantitative continuous-tail blindness

Allow each of the six tail coefficients to vary continuously in
`[0,rho d_14(n)]` and observe it on `Re(s)=2`.  Its difference zonotope
contains the Euclidean data ball of radius `5rho`.

At `rho=1`, every two normalized product distributions on the `4 x 4 x 4`
box have intersecting response fibres under `T_*`.

#### Proof

The coefficient difference cube maps to

\[
 Z_\rho=W[-\rho,\rho]^6.
 \tag{9.7}
\]

The Euclidean coefficient ball `B_2(rho)` lies inside this cube.  By (9.5),
`W B_2(rho)` contains the data ball `B_2(5rho)`, proving the first statement.

Let `p,p'` be normalized product distributions, regarded as spectral masses
on the box.  Each of their three complex readings has modulus at most one, so

\[
 \|H_{T_*}(p-p')\|_2\le2\sqrt3<5.
 \tag{9.8}
\]

Hence some `x` with `||x||_2<1` satisfies

\[
 Wx=-\mathfrak R H_{T_*}(p-p'),
 \tag{9.9}
\]

where `mathfrak R` denotes realification.  In particular `|x_n|<1`.
Split `x=x^+-x^-`; the two nonnegative tails
`d_14(n)x_n^+` and `d_14(n)x_n^-` lie inside their full envelopes and cancel
the core difference exactly.  \(\square\)

This is a declared hybrid spectral-amplitude countermodel.  The normalized
core contributes masses `p_n`, while the off-box amplitude envelope
`d_14(n)n^-2` comes from the degree-fourteen vertical line.  It is not claimed
that the combined source is a Dedekind zeta coefficient sequence.

Unlike the vanishing-radius obstruction in Corollary 8.2, this full-envelope
statement does not require an interval-valued query.  For example,
`delta_1` and `delta_27000` differ by the unit-spaced coordinate `p_1=1`
versus `p_1=0`, yet the six full tail intervals still cancel them.  The two
negative mechanisms must therefore be kept distinct: every positive tail
scale in the common full-dimensional model of Theorem 8.1 defeats continuous
local distinctions, while a discrete distinction
requires a quantitatively large enough tail neighbourhood.  The AS-V
four-anchor neighbourhood is certified too small to cross its unit gap.

As a frozen control, the certificate also reconstructs an exact collision
between the two product vertices `delta_1` and `delta_27000`.  The unique
six-mode correction has certified sign pattern

```text
(-,+,+,+,-,+)
```

and maximum coefficient fraction below `0.260<1/3`.  This finite control is
stronger than needed for Theorem 9.1; the theorem follows already from the
singular-value inequality.

---

## 10. What has and has not been established

### Analytically proved

1. The anisotropic query-fibre lower bound (2.1).
2. Exact and robust recovery for any sufficiently separated queried labels;
   literal integrality is unnecessary.
3. A true weighted discrete metric on unit-spaced query labels.
4. The exact rational componentwise Neumann bias upper bound (3.11).
5. The localized Schur reconstruction bound (4.4).
6. Exact recovery of the normalized Boolean product core for multiplicative
   nonnegative sequences from `a_1,a_2,a_3,a_5`.
7. Vanishing-mesh uniqueness for finite exponential polynomials.
8. Real spanning of every finite positive-time data space by integer-indexed tail
   modes above every cutoff.
9. Interior of continuous tail-difference sets and local failure of every
   genuinely changing continuous query under the common independently
   variable full-dimensional-tail hypotheses of Corollary 8.2.
10. The implication from the certified six-mode singular floor to total
    full-envelope blindness of the declared normalized-product countermodel.

### Finite certificate targets

The companion artifact and verifier:

1. pin the source Arithmetic Sensing V file and its formal payload digest;
2. reconstruct every `tau_n`, `q_n`, `B_n`, global radius, Schur radius, and
   anisotropic unit gap as exact rationals;
3. verify the `n=5` bottleneck and the exact `1/50` upper obstruction;
4. check the two certified-bound comparison brackets;
5. reconstruct the six exact `d_14(n)/n^2` weights;
6. evaluate all logarithmic phases with 384-bit Arb;
7. prove `WW^T-25I` positive definite by interval Sylvester minors; and
8. verify the frozen vertex-collision correction and its coefficient box.

The certificate does not mechanize Sections 2, 4, 6, 7, or 8.

### Not established

1. Equality in the four-anchor critical-radius bracket (5.10).
2. Realizability of every dominated prefix, every `8^3` grid point, or the
   hybrid countermodel by a number field.
3. Object-level identification beyond the selected Dirichlet coefficients.
4. A claim that tail integrality is required for the positive result.
5. Global blindness of the integer four-anchor query under the AS-V
   multiscale schedule; in fact Theorem 5.1 proves the opposite.
6. Any implication for zeta zeros, the Riemann hypothesis, or a physical
   substrate.

---

## 11. Reproduction

The reproduction package is

```text
arithmetic_observability_discrete_queries.py
arithmetic_observability_discrete_queries_certificate.json
test_arithmetic_observability_discrete_queries.py
```

with schema

```text
arithmetic-observability-discrete-queries-v1
```

The source dependency is

```text
certificates/arithmetic_sensing_v_multiscale_end_to_end.json
```

The package is designed so that ordinary verification consumes the frozen
artifact and reconstructs its exact rational payload.  Regeneration of the
six-mode transcendental claims requires `python-flint` for Arb.  The frozen
payload digest is

```text
6dc2aa93d6919bd09928768ff6d5592782fdf2867cba50da039b4698be530996
```

and the package-file SHA-256 digests are

```text
202c46df5fe5b0dddd092886a1437d3cff5d2b80d5050a11b51b5d2754247e6e  arithmetic_observability_discrete_queries.py
786b39e7af8041f8a72be6ee291fd2abe105acd373d12a9c2052667c54ba5e87  arithmetic_observability_discrete_queries_certificate.json
b58147f7c5b741f9b15db353b342a354b68a4f1e6033fae96a4cf134d618d70a  test_arithmetic_observability_discrete_queries.py
ad03df9d6325512074e6940602c1c888c81abd057a5856d6212f93dc8e780517  certificates/arithmetic_sensing_v_multiscale_end_to_end.json
```

Reproduce the focused result with

```bash
python arithmetic_observability_discrete_queries.py \
  --verify arithmetic_observability_discrete_queries_certificate.json
python -m unittest -v test_arithmetic_observability_discrete_queries.py
```

The final local audit passed 32 focused tests, 201 Arithmetic Observability
regressions, and all 665 repository tests.  The formal environment used
`python-flint 0.9.0`, `FLINT 3.6.0`, and 384-bit Arb under CPython 3.12.9.

An independent Windows 10 reconstruction under CPython 3.11.9 with the same
`python-flint`, `FLINT`, and Arb precision passed all 32 focused tests,
recomputed the same payload digest, and regenerated the certificate
byte-for-byte.  The Windows verifier, certificate, tests, and pinned AS-V
dependency hashes all matched the values above.

---

## 12. Relation to established mathematics

The ingredients are classical: diagonal-dominance and inverse estimates,
Schur complements, lattice-separated recovery, finite exponential sums,
almost periodicity, and finite trigonometric moment geometry.  Relevant
points of contact include:

- J. M. Varah, *A lower bound for the smallest singular value of a matrix*,
  Linear Algebra and its Applications 11 (1975), 3--5,
  DOI `10.1016/0024-3795(75)90112-3`;
- H. Bohr, *Zur Theorie der fastperiodischen Funktionen I*, Acta Mathematica
  45 (1925), 29--127, DOI `10.1007/BF02395468`;
- L. Fukshansky, D. Needell, and B. Sudakov, *An algebraic perspective on
  integer sparse recovery*, Applied Mathematics and Computation 340 (2019),
  DOI `10.1016/j.amc.2018.08.007`;
- J.-H. Lange, M. E. Pfetsch, B. M. Seib, and A. M. Tillmann, *Sparse
  Recovery With Integrality Constraints*, Discrete Applied Mathematics 283
  (2020), DOI `10.1016/j.dam.2020.01.021`; and
- J.-P. Gabardo, *Truncated Trigonometric Moment Problems and Determinate
  Measures*, Journal of Mathematical Analysis and Applications 239 (1999),
  349--370, DOI `10.1006/jmaa.1999.6567`.

The claimed contribution is not any one of those ingredients.  It is their
explicit arithmetic-observability synthesis: coordinatewise fibre erosion,
an exact-rational four-anchor certificate, a normalized prime-core geometry,
and a matching continuous-tail no-go theorem in one reproducible model.  No
exhaustive literature search or priority claim is made.

---

## 13. Next questions

1. **Close the 1.433% gap.**  Certify the exact four-anchor closest-fibre
   distance, or find a tail-assisted pair below the zero-tail `n=5` witness.
2. **Optimize the query rather than the prefix.**  Redesign the positive
   sensing measure directly for `{2,3,5}` and compare its Pareto frontier with
   the all-fifty AS-V design.
3. **Natural local Euler data.**  Replace the broad dominated grid by the
   actually realizable splitting types of degree-`d` number fields and compute
   their induced quotient geometry.
4. **Quantitative tail bases.**  Bound the least possible condition number of
   `2m` integer-indexed tail modes as a function of schedule and cutoff.
5. **Mixed discrete-continuous queries.**  Determine which stratified query
   directions retain a gap and which collapse into the continuous tail
   neighbourhood.
6. **Adaptive certificates.**  Choose readings sequentially to maximize the
   minimum remaining query-fibre separation rather than a global coefficient
   norm.

The durable conclusion is precise: incomplete harmonic data need not recover
an entire arithmetic source to recover a useful local arithmetic distinction.
What survives is controlled jointly by the tail bias, the row geometry of the
reconstruction map, and—decisively—the spacing of the query itself.
