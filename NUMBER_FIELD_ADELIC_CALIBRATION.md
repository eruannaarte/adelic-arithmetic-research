# Number-Field Adelic Calibration, Units, and Prime Splitting

## Stage 4 of the adelic-geometry program

**Status:** completed, 2026-08-12. The number-field facts used below—normalized
places, the product formula, Dirichlet's unit theorem, class-group finiteness,
the different, and adelic self-duality—are classical. The synchronization
theorem is an elementary consequence of those facts and the Stage 1 rigidity
theorem. Exact computations are supplied for `Q(i)` and `Q(sqrt(5))`. No claim
of mathematical novelty is made.

## Abstract

Let `K` be any number field. Attach to every place `v` an additive real
observable `E_v` on `K^x`. Suppose `E_v` respects the ordering of the normalized
local absolute value `|.|_v`, and suppose the local observables obey global
conservation:

`sum_v E_v(x)=0` for every `x in K^x`.

Local order rigidity first gives

`E_v(x)=c_v log |x|_v`.

Dirichlet's unit lattice forces all Archimedean constants `c_v` to agree.
Finiteness of the ideal class group then forces the constant at every finite
prime to equal that common Archimedean constant. Consequently one `c>=0`
satisfies

`E_v(x)=c log |x|_v`

simultaneously at every place.

This result needs neither unique factorization of elements nor class number
one. Units synchronize the infinite places; ideal classes synchronize the
finite places. The regulator measures the first mechanism quantitatively, while
the exponent of an ideal class supplies the second.

The quadratic examples expose new layers absent over `Q`: splitting creates
several local directions above one rational prime, ramification changes their
multiplicity, and real units create an Archimedean lattice invisible to ideal
factorization.

## 1. Normalized places of a number field

Let `K` have degree `n`, with `r_1` real places and `r_2` conjugate pairs of
complex places, so

`n=r_1+2r_2`.

Use one place for each real embedding and one place for each conjugate pair of
complex embeddings. Normalize the Archimedean absolute values by

`|x|_v=|sigma_v(x)|` at a real place

and

`|x|_v=|sigma_v(x)|^2` at a complex place.

For a nonzero prime ideal `P` of the ring of integers `O_K`, use

`|x|_P=N(P)^(-ord_P(x))`.

The exponent two at a complex place absorbs its conjugate embedding. With
these conventions, every `x in K^x` satisfies the product formula

`product_v |x|_v=1`,

or equivalently

`sum_v log |x|_v=0`.                                        (1)

Only finitely many finite-place terms differ from zero.

## 2. General synchronization theorem

### Theorem I (number-field local–global calibration)

For every place `v` of a number field `K`, let

`E_v:K^x -> R`

be a group homomorphism. Suppose:

1. **Local order compatibility:** for all `x,y in K^x`,

   `|x|_v<|y|_v  implies  E_v(x)<=E_v(y)`.

2. **Global conservation:** for every `x in K^x`,

   `sum_v E_v(x)=0`.

Then one constant `c>=0` satisfies

`E_v(x)=c log |x|_v`                                      (2)

for every place `v` and every `x in K^x`.

If local order compatibility is strict at any place, then `c>0`.

### Proof

#### Step 1: calibrate each place separately

For every place `v`, the normalized absolute value

`|.|_v:K^x -> R_(>0)`

is a nonconstant multiplicative map. The ordered-group theorem in
`ABSTRACT_ORDERED_MONOID_RIGIDITY.md` gives a constant `c_v>=0` such that

`E_v(x)=c_v log |x|_v`.                                   (3)

This also makes the global sum automatically finite: at almost every finite
place `|x|_v=1`, and equality of size fibers forces `E_v(x)=E_v(1)=0`.

#### Step 2: synchronize the Archimedean places with units

Let `S_infinity` be the set of Archimedean places and define the logarithmic
unit map

`L(u)=(log |u|_v)_(v in S_infinity)`.

For a unit `u in O_K^x`, every finite-place coordinate is zero. Conservation
and (3) give

`sum_(v in S_infinity) c_v log |u|_v=0`.                  (4)

Dirichlet's unit theorem says that the vectors `L(u)` form a full lattice in
the hyperplane

`H_infinity={z in R^(r_1+r_2): sum_v z_v=0}`.

Equation (4) says that the Archimedean coefficient vector `(c_v)` is orthogonal
to that hyperplane. Its orthogonal complement is the line spanned by the
all-ones vector. Hence there is a number `d>=0` such that

`c_v=d`

at every Archimedean place.

This includes the case `r_1+r_2=1`: then the hyperplane is zero-dimensional
and there is only one Archimedean constant to begin with.

#### Step 3: synchronize each finite place with an ideal-class power

Subtract `d` times the product formula (1) from global conservation. For every
`x in K^x`,

`sum_(P finite) (c_P-d) log |x|_P=0`.                     (5)

Fix a prime ideal `P`. The ideal class group is finite, so the class of `P` has
finite order `h`. Thus

`P^h=(alpha)`

for some `alpha in K^x`. Its finite valuations vanish away from `P`, while

`log |alpha|_P=-h log N(P)`.

Substitution in (5) gives

`(c_P-d)(-h log N(P))=0`,

and hence `c_P=d`. Since `P` was arbitrary, every local constant equals `d`.
Set `c=d` to obtain (2).

Strict order compatibility at one place makes its local constant positive, so
the common constant is positive. QED.

## 3. What the proof reveals

The proof uses two arithmetic structures for two different jobs.

### Units couple infinite places

Units have zero finite valuation. Their logarithmic embeddings therefore move
entirely inside the Archimedean product-formula hyperplane. Dirichlet's theorem
says these movements span every direction in that hyperplane. A globally
conserved calibration can be orthogonal to all of them only if its
Archimedean coefficients are equal.

The **regulator** is the covolume of this unit lattice. It quantifies the
spacing of these otherwise invisible Archimedean motions.

### Ideal classes isolate finite places

A prime ideal need not be generated by one field element. Finiteness of the
class group guarantees that some power is principal. That power supplies a
global element whose finite divisor is supported at the chosen prime alone,
which isolates its calibration constant in equation (5).

Thus failure of unique factorization of elements does not break rigidity. The
ideal class group is precisely the finite obstruction, and its finiteness is
enough to remove that obstruction after a finite power.

## 4. Extension of the additive adelic picture

The adele ring of `K` is

`A_K=restricted_product_v K_v`

with respect to the local integer rings at finite places. The diagonal copy of
`K` is a discrete cocompact additive subgroup.

Starting from the rational global character of Stage 3, define

`psi_K(x)=psi_Q(Tr_(A_K/A_Q)(x))`.

It is trivial on diagonal `K`. With the corresponding self-dual local Haar
measures,

`K^perp=K`

and

`volume(A_K/K)=1`.

Consequently, Schwartz–Bruhat functions on `A_K` satisfy

`sum_(alpha in K) f(alpha)=sum_(alpha in K) f_hat(alpha)`.

These are the number-field counterparts of Theorems F and G in
`RATIONAL_ADELES_AND_POISSON.md`.

### The different and local Fourier normalization

Let `D_K` be the different ideal. At a finite place `P`, the annihilator of
`O_(K,P)` under the trace character is the inverse local different

`D_P^(-1)`.

If `D_P=P^(d_P)`, self-duality fixes

`measure(O_(K,P))=N(P)^(-d_P/2)`.

Multiplying over finite places gives

`measure(product_P O_(K,P))=|Delta_K|^(-1/2)`,             (6)

where `Delta_K` is the field discriminant.

Under ordinary Lebesgue measure, the Minkowski lattice `O_K` has Archimedean
covolume

`2^(-r_2) sqrt(|Delta_K|)`.

The self-dual measure at a complex place is twice planar Lebesgue measure, so
the self-dual Archimedean covolume is

`sqrt(|Delta_K|)`.                                         (7)

Equations (6) and (7) multiply to one. The discriminant distortion at infinity
is exactly cancelled by the finite different. This is the number-field version
of the unit quotient volume in Stage 3.

## 5. Laboratory A: the Gaussian field `Q(i)`

### Basic data

`O_K=Z[i]`, with basis `(1,i)`, signature `(r_1,r_2)=(0,1)`, and

`Delta_K=-4`.

There is one complex place, normalized by

`|a+bi|_infinity=|a+bi|^2=a^2+b^2`.

The units are `+1,-1,+i,-i`. There is no free unit direction, and the regulator
is conventionally `1`.

The quadratic Minkowski bound is

`(4/pi)(2!/2^2)sqrt(4)=4/pi=1.2732395...<2`.

Every ideal class therefore contains an integral ideal of norm one, so the
class number is `1`.

### Prime behavior

- `2` ramifies:

  `(2)=P_2^2`, with `P_2=(2,i-1)` and `N(P_2)=2`.

- A prime `p congruent 1 mod 4` splits into two norm-`p` primes.
  For example,

  `(5)=(5,i-2)(5,i-3)`.

- A prime `p congruent 3 mod 4` remains inert, so `(p)` is prime of norm `p^2`.
  In particular, `N((3))=9`.

### Local–global vectors

For `1+i`, the only nonzero logarithmic coordinates are

`(log 2 at infinity, -log 2 at P_2)`.

For the inert rational integer `3`, they are

`(log 9 at infinity, -log 9 at (3))`.

For the split prime element `2+i`, they are

`(log 5 at infinity, -log 5 at one prime above 5, 0 at the other)`.

Thus splitting separates what was one rational-prime direction into distinct
finite local axes. Conjugate Gaussian factors occupy the two axes.

### Self-dual volume balance

The lattice `Z[i]` has ordinary planar covolume `1`. The complex self-dual
measure is `2 dx dy`, giving Archimedean covolume `2`. The finite integer adeles
have volume

`|Delta_K|^(-1/2)=1/2`.

Their product is `1`.

## 6. Laboratory B: the golden field `Q(sqrt(5))`

Let

`phi=(1+sqrt(5))/2`.

### Basic data

`O_K=Z[phi]`, with

`phi^2-phi-1=0`,

signature `(2,0)`, and discriminant `5`. For `a+b phi`,

`Tr(a+b phi)=2a+b`

and

`N(a+b phi)=a^2+ab-b^2`.

The Minkowski bound is

`sqrt(5)/2=1.1180339...<2`,

so this field also has class number `1`.

### Unit lattice and regulator

The fundamental unit `phi` has norm `-1`. Its two real logarithmic coordinates
are

`(log phi,-log phi)`.

The regulator is

`R_K=log phi=0.48121182505960344749...`.

This unit vector is crucial. It has no finite valuation, so ideal
factorization does not see it at all. Nevertheless, conservation on this one
vector forces the two real calibration constants to agree.

This is the first genuinely new geometric direction relative to `Q`: the
kernel of the map from elements to principal ideals contains a nontrivial
Archimedean lattice.

### Prime behavior

- `5` ramifies:

  `(5)=P_5^2`, with `P_5=(5,phi-3)` and `N(P_5)=5`.

- A prime `p congruent +/-1 mod 5` splits. For example,

  `(11)=(11,phi-4)(11,phi-8)`.

- A prime `p congruent +/-2 mod 5` is inert. Thus `(2)` is prime of norm `4`
  and `(3)` is prime of norm `9`.

### Three synchronization mechanisms in coordinates

1. The unit `phi` gives

   `(log phi,-log phi; 0 at every finite place)`.

   Conservation makes the two real coefficients equal.

2. The inert rational integer `2` gives

   `(log 2,log 2; -log 4 at (2))`.

   Once the real coefficients agree, this fixes the coefficient at `(2)`.

3. The ramified element `sqrt(5)=-1+2phi` gives

   `((1/2)log 5,(1/2)log 5; -log 5 at P_5)`.

   The two conjugate generators `phi-4` and its conjugate separately isolate
   the two primes over `11`.

### Self-dual volume balance

The Minkowski embedding of the basis `(1,phi)` has covolume `sqrt(5)` in
`R^2`. The finite integer adeles have self-dual volume `1/sqrt(5)`. Their
product is again `1`.

## 7. Finite calibration matrices

The exact arithmetic program also forms small numerical product-formula
matrices. Columns are selected places and rows are the local logarithms of
selected global elements.

For `Q(i)`, use the complex place and the primes above `2`, `3`, and `5`, with
elements

`1+i`, `3`, `2+i`, `2-i`.

The resulting `4 x 5` matrix has rank `4` and nullity `1`.

For `Q(sqrt(5))`, use the two real places and primes above `2`, `5`, and `11`,
with elements

`phi`, `2`, `sqrt(5)`, `phi-4`, and its conjugate.

The resulting `5 x 6` matrix has rank `5` and nullity `1`.

In both cases, the all-ones coefficient vector lies in the nullspace because of
the product formula. Nullity one says that these small, deliberately selected
relations already leave only a common calibration scale. This is a finite
linear-algebra illustration, not a replacement for Theorem I.

## 8. Exact computational verification

`quadratic_adelic_geometry.py` implements, without external algebra packages:

- exact arithmetic in `Z[i]` and `Z[phi]`;
- conjugation, trace, and norm;
- rank-two integral ideals in canonical column Hermite form;
- exact ideal multiplication, powers, containment, and norms;
- prime-ideal decomposition through the defining polynomial modulo `p`;
- exact factorization and reconstruction of sampled principal ideals;
- Minkowski class-number bounds;
- the golden unit lattice and regulator;
- discriminant cancellation in self-dual adelic volume;
- the finite calibration matrices described above.

Run:

```sh
python3 quadratic_adelic_geometry.py
python3 -m unittest -v test_quadratic_adelic_geometry.py
```

All ideal arithmetic is integer-exact. Decimal calculations are confined to
displayed logarithms, `pi`, square roots, regulators, and volume checks.

The tests verify, among other examples,

`(1+i)=P_2`,

`(2+i)=(5,i-3)`,

`(7+4i)=(5,i-2)(13,i-8)`,

`(sqrt(5))=P_5`,

and the two conjugate norm-`11` elements in `Z[phi]`.

## 9. What changed from the rational field?

Four structures that were trivial or invisible over `Q` are now separate:

1. **Archimedean multiplicity.** There may be several real and complex local
   sizes.
2. **Unit geometry.** The unit group forms a lattice of rank
   `r_1+r_2-1` inside the Archimedean balance hyperplane.
3. **Prime branching.** One rational prime may split into several prime ideals,
   remain inert, or ramify with multiplicity.
4. **Discriminant coupling.** Archimedean lattice covolume and finite Fourier
   conductor cancel through the discriminant.

The emerging picture is not one universal Euclidean geometry. It is a coupled
system consisting of:

- logarithmic local size coordinates;
- a unit lattice within their Archimedean kernel;
- a prime-ideal divisor lattice at finite places;
- a trace pairing whose different fixes Fourier normalization;
- a product formula and self-dual Poisson structure tying the layers together.

## 10. Relation to arithmetic acceleration

Stage 4 still uses exact infinite structure, so arithmetic acceleration was not
a dependency. It has, however, acquired a natural number-field extension:

> How quickly do bounded-norm element or ideal comparisons reconstruct the
> local weights `log N(P)`, distinguish split primes, and reveal the unit
> regulator?

This belongs naturally to Stage 5. That study has now been carried out at the
first finite layer in `FINITE_LOCAL_GLOBAL_RECONSTRUCTION.md`, with the
rational rate experiment separated into `ARITHMETIC_ACCELERATION.md`.

## 11. Limitations and next step

- Theorem I is a synthesis of classical theorems, not a novelty claim.
- The exact ideal implementation supports the two selected monogenic quadratic
  rings, not arbitrary number fields.
- Class number one in the examples simplifies explicit factorization, although
  the general theorem does not assume it.
- The finite matrices were constructed from informative elements; they do not
  establish sample-complexity bounds.
- No zeta functional equation or claim about zeros is derived here.

Stage 5 subsequently found exact coefficient-height-two relation bases forcing
the common active calibration direction in `Q(i)` and `Q(sqrt(5))`, together
with nullity-one computations through height eight. Uniform height bounds,
invariant-height sampling, and fields with nontrivial class group remain open.

## 12. Primary source and novelty boundary

The normalized local valuations, product formula, local different, self-dual
measures, unit lattice, regulator, ideal classes, adeles, and ideles used here
are developed in [J. Tate, *Fourier Analysis in Number Fields and Hecke's
Zeta-Functions* (1950)](https://sites.math.rutgers.edu/~alexk/2023S572/Tate1950.pdf).

Theorem I and the quadratic laboratories are presented as a fully auditable
bridge between classical number-field structure and the order-rigidity program.
The finite reconstruction rates, minimal relation sets, robustness, and
arithmetic acceleration across split and unit directions are the exploratory
part of the program; no literature-priority claim is made for them.
