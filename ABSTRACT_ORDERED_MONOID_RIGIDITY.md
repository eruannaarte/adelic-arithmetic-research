# Abstract Ordered-Monoid Rigidity

## Stage 1 of the adelic-geometry program

**Status:** proved, 2026-08-12. The result below is a self-contained
abstraction of the completely additive integer theorem. It is an elementary
Archimedean rigidity statement, and no claim of mathematical novelty is made.

## Abstract

Let a monoid carry two real-valued additive quantities. Call the first one
`ell`, and suppose it is nonnegative and not identically zero. Call the second
one `E`. If every strict comparison made by `ell` is respected by `E`, then
there is no freedom left:

`E = c ell`

for one constant `c >= 0`.

Equivalently, if a monoid has a multiplicative size `S >= 1`, every extensive
real-valued observable that respects size must be a constant multiple of
`log S`. The proof does not require commutativity, cancellation, unique
factorization, countability, continuity, or an order relation intrinsic to the
monoid.

The group version permits sizes both above and below `1`. It applies directly
to positive rationals and to groups of fractional ideals. The proof also shows
that distinct objects with the same size must receive the same scalar energy,
even though this is not assumed.

## 1. Additive formulation

Let `(M, *, 1)` be a monoid. Powers are denoted by `x^n`.

### Theorem A (calibrated monoid rigidity)

Suppose `ell:M -> R_[>=0]` and `E:M -> R` satisfy:

1. `ell(x*y) = ell(x) + ell(y)` for all `x,y in M`;
2. `ell` is not identically zero;
3. `E(x*y) = E(x) + E(y)` for all `x,y in M`;
4. if `ell(x) < ell(y)`, then `E(x) <= E(y)`.

Then there is a unique constant `c >= 0` such that

`E(x) = c ell(x)`

for every `x in M`.

If condition 4 is strengthened to

`ell(x) < ell(y)  implies  E(x) < E(y)`,

then `c > 0`.

### Proof

The identities of the two additive codomains imply

`ell(1)=0` and `E(1)=0`.

Because `ell` is nontrivial and nonnegative, choose `u in M` with
`ell(u)>0`. Comparing `1` with `u` gives

`E(u) >= 0`.                                                   (1)

#### Step 1: strict comparisons force equality on equal-size fibers

Let `x,y in M` satisfy `ell(x)=ell(y)`. For every positive integer `n`,

`ell(x^n) < ell(y^n*u)`

because the right side exceeds the left side by `ell(u)>0`. Order
compatibility and additivity therefore give

`n E(x) <= n E(y) + E(u)`.

Interchanging `x` and `y` gives

`n E(y) <= n E(x) + E(u)`.

Consequently,

`|E(x)-E(y)| <= E(u)/n`.

This holds for every `n`, so the Archimedean property of the real numbers
forces

`E(x)=E(y)`.                                                   (2)

In particular, if `ell(x)=0`, comparison with the identity shows `E(x)=0`.
Equation (2) also upgrades condition 4 to non-strict comparisons:

`ell(x) <= ell(y)  implies  E(x) <= E(y)`.                     (3)

#### Step 2: compare arbitrary powers with powers of one calibrator

Fix `x` with `ell(x)>0`. For each positive integer `n`, define

`r_n = floor(n ell(x)/ell(u))`.

Then

`r_n ell(u) <= n ell(x) < (r_n+1) ell(u)`.

Using (3), the original strict comparison, and additivity yields

`r_n E(u) <= n E(x) <= (r_n+1) E(u)`.                         (4)

Divide (4) by `n`. Since

`r_n/n -> ell(x)/ell(u)`,

both endpoints converge to

`(ell(x)/ell(u)) E(u)`.

The squeeze theorem gives

`E(x) = (E(u)/ell(u)) ell(x)`.

Together with the zero-size case, this proves the conclusion with

`c = E(u)/ell(u) >= 0`.

The constant is unique because `ell(u)>0`. Under strict order compatibility,
the comparison `ell(1)<ell(u)` gives `E(u)>0`, hence `c>0`. QED.

## 2. Multiplicative-size formulation

### Theorem B (abstract logarithmic rigidity)

Let `M` be a monoid and let `S:M -> R_[>=1]` be a nonconstant
multiplicative size map:

`S(x*y)=S(x)S(y)`.

Let `E:M -> R` be extensive:

`E(x*y)=E(x)+E(y)`.

Assume only that

`S(x)<S(y)  implies  E(x)<=E(y)`.

Then a unique `c>=0` satisfies

`E(x)=c log S(x)`

for all `x in M`. Strict size-order compatibility gives `c>0`.

### Proof

Apply Theorem A to `ell=log S`. QED.

### What the theorem does not need

The proof never uses:

- commutativity;
- cancellation;
- inverses;
- unique or atomic factorization;
- finite generation or countability;
- topology, measurability, or continuity;
- an assumption about what happens when `S(x)=S(y)`.

The last point is particularly useful. Global comparison of arbitrarily high
powers forces `E(x)=E(y)` whenever `S(x)=S(y)`.

## 3. Group version

For positive rationals and fractional ideals, a multiplicative size can be
smaller than `1`. Inverses make the extension immediate.

### Theorem C (ordered-group calibration)

Let `G` be a group, let `S:G -> R_(>0)` be a nonconstant multiplicative map,
and let `E:G -> R` be additive. If

`S(x)<S(y)  implies  E(x)<=E(y)`,

then a unique `c>=0` satisfies

`E(x)=c log S(x)`

for every `x in G`.

### Proof

Set `ell=log S` and consider the submonoid

`G_+ = {x in G : ell(x)>=0}`.

It contains an element of positive `ell`: if a nonzero value is negative,
replace that element by its inverse. Theorem A applies to `G_+`, so
`E=c ell` there. If `ell(x)<0`, then `ell(x^(-1))>0`, and

`E(x)=-E(x^(-1))=-c ell(x^(-1))=c ell(x)`.

Thus the formula holds on all of `G`. QED.

## 4. Corollaries

### 4.1 Positive integers

Take `M=N_+` under multiplication and `S(n)=n`. Every completely additive
real function that respects ordinary order is

`E(n)=c log n`.

This recovers the theorem used in `ORDER_FACTORIZATION_GEOMETRY.md`. The
integer theorem is classical in substance. Erdős's 1946 theorem is stronger in
another direction because it assumes arithmetic additivity only on coprime
arguments.

### 4.2 Integral ideals

Let `M` be the multiplicative monoid of nonzero integral ideals of a number
field and let `S(I)=N(I)`, the absolute ideal norm. Since norms multiply and
are positive integers, any extensive real observable satisfying

`N(I)<N(J)  implies  E(I)<=E(J)`

must obey

`E(I)=c log N(I)`.

Distinct ideals can have the same norm. The equal-fiber part of the proof shows
that their scalar energies are nevertheless equal. No extra equality axiom is
needed.

### 4.3 Fractional ideals

Nonzero fractional ideals form a group and their norms are positive rational
numbers. Theorem C gives the same conclusion:

`E(I)=c log N(I)`.

### 4.4 Positive rationals

For the multiplicative group `Q_(>0)`, take `S(q)=q`. Every additive
real-valued observable respecting ordinary rational order is

`E(q)=c log q`.

Prime exponents may now be negative, so the factorization lattice expands from
a positive cone to the direct sum

`direct_sum_p Z`.

### 4.5 Determinant size

Let `M` be any multiplicatively closed collection of matrices for which
`|det A|>=1` and determinant magnitude is nonconstant. Take
`S(A)=|det A|`. An extensive scalar observable ordered only by determinant
magnitude must be

`E(A)=c log |det A|`.

Thus the theorem is not fundamentally about primes. Primes provide coordinates
for the integer monoid, but the rigidity mechanism is the compatibility of two
homomorphisms with an Archimedean order.

## 5. Why the hypotheses matter

### 5.1 If additivity is removed

`E(x)=(log S(x))^2` is monotone for `S>=1`, but it is generally not additive.
Order alone does not select the logarithm.

### 5.2 If order compatibility is removed

On the positive integers, assign arbitrary real weights `w_p` to primes and
set

`E(n)=sum_p v_p(n) w_p`.

This is completely additive. Unless `w_p=c log p`, it eventually contradicts
ordinary order.

### 5.3 If the size map is trivial

If `S(x)=1` for every `x`, there are no strict size comparisons. Any additive
`E` satisfies the order condition vacuously. This is why nontriviality is
required.

### 5.4 If only generators are compared

Ordering the prime generators correctly is insufficient. For example, weights
that increase with `p` need not reproduce the interleaving of prime powers and
composites. The theorem requires compatibility for all monoid elements.

### 5.5 If the codomain is non-Archimedean

The real-valued assumption is structural. Give `R^2` the lexicographic order
and define on positive integers

`E(n)=(log n, Omega(n))`,

where `Omega(n)` counts prime factors with multiplicity. This `E` is additive
and strictly respects ordinary order because its first coordinate does. Yet its
second coordinate is not determined by `log n`.

The proof of Theorem A fails exactly where it sends the bound `E(u)/n` to zero.
Lexicographically ordered `R^2` contains directions infinitesimal relative to
the first coordinate. This supplies a precise warning for higher-dimensional
physics: one scalar order determines one Archimedean scalar energy, not every
possible hidden observable.

### 5.6 If only finitely many comparisons are imposed

The squeeze proof uses arbitrarily high powers. At a finite cutoff there is a
polyhedron of admissible observables rather than a unique ray. This is not a
defect in the theorem; it is the source of the finite-rigidity problem.

## 6. A quantitative fact already contained in the proof

Normalize with a calibrator `u` and suppose `E(u)` is known. For an element `x`
and a positive integer `n`, the power comparisons alone give

`r_n E(u)/n <= E(x) <= (r_n+1) E(u)/n`,

where

`r_n=floor(n ell(x)/ell(u))`.

The interval has exact width

`E(u)/n`.

If a size cutoff permits powers only through approximately `S(x)^n<=N`, then
`n` is only of order `log N`. The abstract proof by itself therefore gives a
finite uncertainty of order `1/log N`, not the much narrower behavior observed
in the full adjacent-integer linear programs. Any proof of the proposed
near-`1/N` finite-rigidity rate must exploit the dense web of comparisons among
different composites, not merely comparisons between two sequences of powers.

This distinguishes two mechanisms:

1. **Archimedean rigidity:** arbitrary powers force exact proportionality in
   the infinite limit.
2. **Arithmetic acceleration:** factorization patterns among many nearby
   integers may force unusually rapid finite convergence.

## 7. Bridge to adelic geometry

For `q in Q_(>0)`, write

`q = product_p p^(v_p(q))`,

where only finitely many integer exponents are nonzero. Then

`log q = sum_p v_p(q) log p`.

With the normalized `p`-adic absolute values

`|q|_p=p^(-v_p(q))`,

this becomes the product-formula relation

`log |q|_infinity + sum_p log |q|_p = 0`.

Theorem C says that imposing the ordinary Archimedean order and asking for one
extensive real scalar collapses this entire valuation vector to a multiple of
`log |q|_infinity`.

That observation identifies the next question precisely. Adelic structure
cannot be recovered from a single scalar ordering alone. To retain genuinely
local information, the theory must introduce additional independently
meaningful observables, local topologies, or symmetry actions. Otherwise the
abstract rigidity theorem deliberately erases all directions transverse to the
logarithmic scalar.

## 8. Next stages opened by the proof

The maintained work order is now in `RESEARCH_ROADMAP.md`. Stage 2 develops the
local–global calibration theorem in `LOCAL_GLOBAL_ADELIC_CALIBRATION.md`.

1. **Two-prime finite theorem.** Determine the exact finite intervals produced
   by the interleaving of `2^a` and `3^b`, and relate their endpoints to
   continued fractions.
2. **Exact LP certificates.** Express finite upper and lower bounds as rational
   primal-dual certificates.
3. **Ideal-norm finite rigidity.** Enumerate ideals in a quadratic field and
   determine what norm ordering fixes before taking an infinite limit.
4. **Adelic observables.** Classify additive vector-valued observables assembled
   from local valuations, then specify which extra order or symmetry conditions
   can select them.
5. **Archimedean versus local information.** Prove a decomposition theorem
   separating the scalar logarithmic direction from the kernel invisible to
   the chosen size order.
6. **Adjacent arithmetic-acceleration target.** Explain why the full network of
   nearby composite comparisons produces much faster finite rigidity than the
   universal power-squeeze proof. Resume this branch when quantitative finite
   adelic reconstruction requires it.

## 9. Literature and novelty boundary

The proof above is elementary and is included so every assumption can be
audited directly. On the integers, logarithmic rigidity is classical; see
[P. Erdős, *On the distribution function of additive functions* (1946)](https://combinatorica.hu/~p_erdos/1946-06.pdf).
The present contribution is a
useful abstraction and research scaffold, not presently a novelty claim. The
potentially original questions begin with finite quantitative rates, exact
certificates, sparse comparison recovery, and adelic extensions with additional
local observables.
