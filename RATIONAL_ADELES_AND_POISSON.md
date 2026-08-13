# Rational Adeles, Self-Duality, and Poisson Summation

## Stage 3 of the adelic-geometry program

**Status:** completed, 2026-08-12. The adelic constructions and Poisson
summation theorem are classical. This note fixes conventions, supplies a
self-contained derivation for a controlled factorable family, distinguishes
the structures that are rigid from those that are additional choices, and
provides reproducible high-precision checks. No claim of mathematical novelty
is made.

## Abstract

Stage 2 retained only the logarithms of local absolute values. Stage 3 lifts to
the actual rational adele ring

`A_Q = R times restricted_product_p Q_p`.

The restricted product preserves local addition, `p`-adic units and residues,
topology, and Haar measure. A standard product character `psi` is trivial on
the diagonal copy of `Q`. With self-dual local Haar measures, `A_Q` is its own
character group and diagonal `Q` is its own annihilator. Moreover, `Q` is a
discrete cocompact subgroup with quotient volume one.

These properties yield adelic Poisson summation:

`sum_(q in Q) f(q) = sum_(q in Q) f_hat(q)`.

For a Gaussian at the real place and the indicator of `M Zhat` at the finite
places, this becomes the exact theta transformation

`theta(t M^2) = 1/(M sqrt(t)) theta(1/(t M^2))`.

The factor `1/M` and the dual lattice `(1/M)Z` arise from finite-place Fourier
duality. Thus the example genuinely uses the adelic structure even though its
final expression is a classical real theta identity.

## 1. The restricted product

For each prime `p`, let `Q_p` be the completion of `Q` in the `p`-adic absolute
value and let

`Z_p={x in Q_p: |x|_p<=1}`

be its compact open ring of integers.

The finite adele ring is

`A_f = restricted_product_p (Q_p,Z_p)`

`= {(x_p)_p : x_p in Z_p for all but finitely many p}`.

The rational adele ring is

`A_Q = R times A_f`.

Addition and multiplication are componentwise. A basic neighborhood restricts
finitely many coordinates to open sets and leaves all remaining finite
coordinates equal to `Z_p`.

The restriction is essential. An unrestricted product of infinitely many
noncompact local fields is not locally compact. The restricted product is a
locally compact topological ring, which makes Haar measure and Fourier analysis
available.

Write

`Zhat=product_p Z_p`.

This is a compact open subring of `A_f`.

### The idele group

The group of invertible adeles is the restricted product

`A_Q^x = R^x times restricted_product_p (Q_p^x,Z_p^x)`.

For an idele `a`, define its module

`|a|_A=|a_infinity| product_p |a_p|_p`.

Only finitely many factors differ from one. Multiplication by `a` scales
additive Haar measure by `|a|_A`.

For a principal idele produced by `q in Q^x`, the product formula gives

`|q|_A=1`.

This is the full multiplicative setting behind the logarithmic conservation
law studied in Stage 2.

## 2. The diagonal rational lattice

Embed `Q` diagonally:

`q -> (q,q,q,...) in A_Q`.

### Proposition 2.1

Diagonal `Q` is a discrete cocompact additive subgroup of `A_Q`. A fundamental
domain, up to its real boundary, is

`F=[0,1) times Zhat`.

### Proof

First consider discreteness. If a rational `q` lies in every `Z_p`, its reduced
denominator has no prime factor, so `q` is an integer. Hence

`((-1/2,1/2) times Zhat) intersect Q = {0}`.

For existence of representatives, let `x in A_Q`. Only finitely many `x_p` are
nonintegral. Choose powers `p^(m_p)` clearing those finitely many local
denominators. The Chinese remainder theorem produces a rational `q` with those
denominators such that

`x_p-q in Z_p`

at every finite place. Subtracting a diagonal integer does not disturb these
conditions and can place the real coordinate of `x-q` in `[0,1)`.

For uniqueness, suppose two points of `F` differ by a diagonal rational `q`.
Their finite components show that `q in Z_p` for every `p`, hence `q in Z`.
Their real components differ by a number in `(-1,1)`, so `q=0`. The compact
closure `[0,1] times Zhat` maps onto the quotient, proving cocompactness. QED.

## 3. A global additive character

At the real place set

`psi_infinity(x)=exp(-2 pi i x)`.

If

`x=sum_(k=m)^infinity a_k p^k in Q_p`,

define its `p`-adic fractional part by

`{x}_p=sum_(k=m)^(-1) a_k p^k`,

with value zero when `m>=0`. Set

`psi_p(x)=exp(2 pi i {x}_p)`.

The kernel of `psi_p` is exactly `Z_p`. Therefore, for an adele `x`, almost all
local factors below equal one and the product

`psi(x)=psi_infinity(x_infinity) product_p psi_p(x_p)`

is well-defined and continuous.

### Proposition 3.1 (additive phase balance)

For every rational `q`,

`psi(q)=1`.

### Proof

Only primes dividing the reduced denominator of `q` have nonzero fractional
part. The elementary rational identity

`q-sum_p {q}_p in Z`

follows from the Chinese remainder theorem, or by combining the prime-power
parts of the denominator. Consequently,

`psi(q)=exp(2 pi i(-q+sum_p {q}_p))=1`. QED.

The script `adelic_poisson.py` computes `-q+sum_p {q}_p` using exact rational
arithmetic. It is an integer for every tested rational; the theorem itself is
exact and does not depend on testing.

## 4. Haar measure and self-duality

Use Lebesgue measure `dx_infinity` on `R`. At every finite place choose the
additive Haar measure `dx_p` normalized by

`measure(Z_p)=1`.

Relative to `psi_p`, this is the self-dual measure. Indeed, the annihilator of
`Z_p` is `Z_p`, and

`Fourier(1_(Z_p))=1_(Z_p)`.

The restricted product measure

`dx=dx_infinity product_p dx_p`

is well-defined on `A_Q` and is self-dual relative to `psi`.

From the fundamental domain in Proposition 2.1,

`volume(A_Q/Q)=1`.

### Theorem F (self-dual rational lattice)

Under the pairing

`<x,y>=psi(xy)`,

the adele ring is its own Pontryagin dual and the annihilator of diagonal `Q`
is diagonal `Q`:

`Q^perp=Q`.

### Proof of the annihilator statement

The local self-duality of `R` and every `Q_p` combines, through the restricted
product, to identify `A_Q` with its character group. Proposition 3.1 already
shows `Q subset Q^perp`.

Conversely, let `y in Q^perp`. By Proposition 2.1, subtract a diagonal rational
so that

`y in R times Zhat`.

This does not change whether `y` annihilates `Q`, because `Q` annihilates
itself. Testing against every integer `n` leaves only the real character and
gives

`exp(-2 pi i n y_infinity)=1`,

so `y_infinity in Z`. Subtract this diagonal integer. We may now assume
`y_infinity=0` and `y_p in Z_p` for all `p`.

Fix a prime `p` and test against `q=p^(-k)`. At every finite place other than
`p`, the argument remains integral. Hence

`psi_p(y_p/p^k)=1`.

Because `psi_p` has kernel `Z_p`, this says `y_p in p^k Z_p`. It holds for
every `k`, forcing `y_p=0`. Repeating for every prime gives `y=0` after the
rational subtractions. Thus the original `y` was diagonal rational. QED.

### Character classification

Every continuous additive character of `A_Q` has the form

`x -> psi(a x)`

for a unique `a in A_Q`. By Theorem F, it is trivial on diagonal `Q` exactly
when `a in Q`. Thus triviality on `Q` does not select one global character by
itself; it leaves a rational frequency. Fixing the real frequency to one
selects the standard `psi` above.

## 5. Schwartz–Bruhat functions and Fourier transform

A factorable Schwartz–Bruhat function on `A_Q` has the form

`f(x)=f_infinity(x_infinity) product_p f_p(x_p)`,

where:

- `f_infinity` is a Schwartz function on `R`;
- every `f_p` is locally constant with compact support;
- `f_p=1_(Z_p)` for all but finitely many primes.

Finite linear combinations of such functions form the Schwartz–Bruhat space
`S(A_Q)`.

Define

`f_hat(y)=integral_(A_Q) f(x) psi(xy) dx`.

For factorable functions and the product measure,

`f_hat(y)=f_hat_infinity(y_infinity) product_p f_hat_p(y_p)`.

Self-duality makes Fourier inversion hold with no additional global constant.

## 6. Adelic Poisson summation

### Theorem G (Poisson summation over `Q`)

For `f in S(A_Q)`, with the standard convergence conditions implicit in this
space,

`sum_(q in Q) f(q)=sum_(q in Q) f_hat(q)`.

### Proof sketch

Periodize `f` over the rational lattice:

`P_f(x)=sum_(q in Q) f(x+q)`.

This is a function on the compact quotient `A_Q/Q`. Its Fourier characters are
indexed by the annihilator lattice `Q^perp`, which equals `Q` by Theorem F. The
Fourier coefficient at `r in Q` is `f_hat(r)`. Fourier inversion on the compact
quotient, evaluated at zero, gives the displayed equality. The quotient volume
is one, so no covolume factor appears. QED.

## 7. A controlled factorable family

Let `M` be a positive integer, `t>0`, and define

`f_(t,M)(x)=exp(-pi t x_infinity^2) 1_(M Zhat)(x_f)`.

Here

`M Zhat=product_p p^(v_p(M)) Z_p`.

At infinity,

`Fourier(exp(-pi t x^2))(y)=t^(-1/2) exp(-pi y^2/t)`.

At a finite place, translation invariance and character orthogonality give,
for every integer `k`,

`Fourier(1_(p^k Z_p))(y)=p^(-k) 1_(p^(-k) Z_p)(y)`.

Multiplying the local formulas gives

`f_hat_(t,M)(y)`

`=1/(M sqrt(t)) exp(-pi y_infinity^2/t) 1_((1/M)Zhat)(y_f)`.

The factor `1/M` is the finite Haar volume of `M Zhat`.

### Theorem H (explicit adelic theta identity)

Let

`theta(a)=sum_(n in Z) exp(-pi a n^2)`.

Then

`theta(t M^2)=1/(M sqrt(t)) theta(1/(t M^2))`.

### Proof

A diagonal rational belongs to `M Zhat` exactly when it belongs to `M Z`.
Therefore

`sum_(q in Q) f_(t,M)(q)=sum_(n in Z) exp(-pi t M^2 n^2)`

`=theta(t M^2)`.

Similarly, a diagonal rational belongs to `(1/M)Zhat` exactly when it belongs
to `(1/M)Z`. Hence

`sum_(q in Q) f_hat_(t,M)(q)`

`=1/(M sqrt(t)) sum_(n in Z) exp(-pi n^2/(t M^2))`.

Theorem G equates the two sums. QED.

### Why this is genuinely adelic

The final equation is the classical theta transformation. But its lattice
conditions and normalization have been distributed across all places:

- `M Zhat` makes the rational diagonal sum run over `M Z`;
- its finite Fourier annihilator is `(1/M)Zhat`;
- finite Haar measure contributes `1/M`;
- the real Gaussian contributes `t^(-1/2)`;
- self-annihilation of diagonal `Q` allows the same rational index set on both
  sides.

This is a simple local–global mechanism, not a numerical coincidence.

## 8. Computational verification

Run:

```sh
python3 adelic_poisson.py --t 0.37 --modulus 6 --digits 60
python3 -m unittest -v test_adelic_poisson.py
```

The verifier uses only the Python standard library. It includes:

- exact `p`-adic fractional parts for rational inputs;
- exact verification that the global character exponent is integral;
- a high-precision decimal implementation of `pi`;
- Gaussian theta summation with an analytic tail bound;
- scaled Poisson tests at several values of `t` and `M`.

For `t=0.37`, `M=6`, and 60 requested digits, the two sides agree with
absolute residual approximately `3.14e-70`; the combined analytic truncation
bound is approximately `4.45e-66`. The symbolic proof, rather than this
calculation, establishes the infinite identity.

## 9. What is rigid, and what is additional structure?

### Rigid after a convention is fixed

- Translation invariance determines each local Haar measure up to scale.
- Self-duality relative to a fixed nontrivial local character fixes that scale.
- The character kernel `Z_p` fixes the standard finite-place conductor.
- The annihilator relation `Q^perp=Q` fixes the dual summation lattice.
- The restricted product is what permits simultaneous local data while
  retaining local compactness.

### Not forced by Stage 1 order rigidity

- An additive character is phase data, not an order-valued observable.
- The standard character still requires a frequency normalization.
- Haar measure and Fourier transform require topology and local compactness.
- The Gaussian is a selected test function, distinguished by real Fourier
  self-duality but not by multiplicative order.
- Poisson summation follows from harmonic analysis, not from factorization and
  order alone.

Thus Stage 3 adds a second rigidity mechanism: **duality normalization**. It is
compatible with logarithmic order rigidity but logically independent of it.

## 10. Two local–global closure laws

The program now contains two complementary classical relations.

### Multiplicative closure

For `q in Q^x`,

`product_v |q|_v=1`.

Principal ideles lie in the kernel of the adelic module. Logarithms turn this
into the balance hyperplane of Stage 2.

### Additive/Fourier closure

For `q,r in Q`,

`psi(qr)=1`.

Diagonal rationals form a self-annihilating lattice. This makes the global
Poisson formula close on the same rational labels.

The first law balances local scales. The second balances local phases. Their
coexistence is the first genuinely adelic structural picture in this program.

## 11. Relation to arithmetic acceleration

Stage 3 did not require quantitative finite order reconstruction. Its input is
the exact local-field and rational-lattice structure, so arithmetic
acceleration remains an adjacent target rather than a dependency.

It will become relevant if we truncate the rational lattice, infer local data
from bounded-height samples, or ask how rapidly a finite Poisson sum reveals
the exact dual lattice. Those questions belong to Stage 5 unless Stage 4
uncovers an earlier need.

## 12. Limitations and next step

- Everything proved here belongs to established adelic harmonic analysis or is
  an elementary specialization of it.
- The numerical experiment verifies one controlled family, not the entire
  Schwartz–Bruhat space.
- Poisson summation is an engine behind zeta functional equations, but this
  note has not derived a zeta integral or any statement about zeros.
- The rational field has only one Archimedean place and no nontrivial unit
  regulator. New geometry appears over number fields.

Stage 4 extends local–global calibration and the adelic constructions to
`Q(i)` and `Q(sqrt(5))`, where complex normalization, prime splitting, units,
ideal classes, and regulators become visible. It is completed in
`NUMBER_FIELD_ADELIC_CALIBRATION.md`.

## 13. Primary source

The constructions used here are classical and follow the local, restricted
product, and global theory in [J. Tate, *Fourier Analysis in Number Fields and
Hecke's Zeta-Functions* (1950)](https://sites.math.rutgers.edu/~alexk/2023S572/Tate1950.pdf).
In particular, Tate develops the local self-dual measures and characters,
restricted direct products, diagonal number field, Poisson formula, ideles,
and product formula used in this note.
