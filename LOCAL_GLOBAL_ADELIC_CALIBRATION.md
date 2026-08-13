# Local–Global Adelic Calibration on the Positive Rationals

## Stage 2 of the adelic-geometry program

**Status:** proved for finite sets of rational places, 2026-08-12. The local
absolute values, product formula, adeles, and ideles are established
mathematics. The calibration theorem below is a direct application of Stage 1.
The finite-prime Euclidean calculations are elementary consequences of a
specified metric choice. No claim of mathematical novelty is made.

## Abstract

Every positive rational number has simultaneous Archimedean and `p`-adic
sizes. Their logarithms form a vector whose coordinates sum to zero. Stage 1
showed that a single size ordering determines a single additive scalar up to
scale. Stage 2 applies that theorem at every place.

For a finite set of primes `T`, suppose an additive scalar `E_v` is attached to
each place `v in {infinity} union T`. If `E_v` respects the local absolute-value
ordering at its own place, then

`E_v(q)=c_v log |q|_v`.

If the local scalars also obey one global conservation law,

`sum_v E_v(q)=0`,

then all `c_v` are equal. Thus local order plus global balance reconstructs the
entire logarithmic valuation vector up to one common scale.

The product formula has a second consequence: no two distinct rational points
can be larger in every local coordinate at once. The adelic geometry is a
geometry of compensating expansions and contractions, not one global size
hierarchy.

## 1. Validity boundary: this is not yet the full adele ring

The object studied first is the **logarithmic valuation skeleton** of the
multiplicative group of positive rationals. It records the real numbers

`log |q|_v`

at all places `v`.

The full rational adele ring is instead the restricted product

`A_Q = R times restricted_product_p Q_p`,

with `x_p in Z_p` for all but finitely many primes. It retains additive,
topological, residue-class, and unit information that absolute values discard.
The idele group is the analogous restricted multiplicative product, with
`p`-adic unit components at almost all primes.

The logarithmic skeleton is obtained only after applying absolute values and
logarithms to multiplicative data. It is a useful bridge to adelic theory, but
calling it the adele ring would be incorrect.

## 2. Local logarithmic coordinates

Let `T` be a finite nonempty set of rational primes, and let

`Gamma_T = {product_(p in T) p^(n_p) : n_p in Z}`.

This is the group of positive rational `T`-units. Unique factorization gives

`Gamma_T ~= Z^T`.

Use the normalized absolute values

`|q|_infinity = q`

and

`|q|_p = p^(-v_p(q))`.

Define

`lambda_v(q)=log |q|_v`.

For `q=product p^(n_p)`, the coordinates are

`lambda_infinity(q)=sum_(p in T) n_p log p`

and

`lambda_p(q)=-n_p log p`.

Every `lambda_v` is an additive homomorphism from the multiplicative group
`Gamma_T` to the additive reals.

### Proposition 2.1 (finite product formula)

For every `q in Gamma_T`,

`lambda_infinity(q) + sum_(p in T) lambda_p(q)=0`.

### Proof

Substituting the displayed formulas cancels each term `n_p log p`. QED.

Define the product-formula hyperplane

`H_T = {x in R^({infinity} union T) : sum_v x_v=0}`

and the logarithmic embedding

`Lambda_T(q)=(lambda_v(q))_v`.

### Proposition 2.2 (faithful log embedding)

`Lambda_T:Gamma_T -> H_T` is an injective group homomorphism.

### Proof

Additivity of each coordinate makes it a homomorphism. If `Lambda_T(q)=0`,
then `lambda_p(q)=0` at each `p in T`, so every exponent `v_p(q)` is zero.
Thus `q=1`. QED.

## 3. Local–global rigidity

### Theorem D (local–global calibration)

For every place `v in {infinity} union T`, let

`E_v:Gamma_T -> R`

be additive. Assume:

1. **Local order compatibility:** for every `x,y in Gamma_T`,

   `|x|_v < |y|_v  implies  E_v(x)<=E_v(y)`.

2. **Global conservation:** for every `q in Gamma_T`,

   `E_infinity(q)+sum_(p in T) E_p(q)=0`.

Then one constant `c>=0` satisfies

`E_v(q)=c log |q|_v`

for every active place `v` and every `q in Gamma_T`.

If local order compatibility is strict at any one active place, then `c>0`.

### Proof

For every active place `v`, the map `q -> |q|_v` is a nonconstant
multiplicative size on the group `Gamma_T`. The ordered-group theorem proved in
`ABSTRACT_ORDERED_MONOID_RIGIDITY.md` therefore gives a constant `c_v>=0` with

`E_v(q)=c_v log |q|_v`.                                      (1)

Fix `p in T` and apply global conservation to the generator `q=p`. Its only
nonzero local logarithms are

`log |p|_infinity=log p`

and

`log |p|_p=-log p`.

Equation (1) and conservation give

`(c_infinity-c_p) log p=0`.

Hence `c_p=c_infinity`. This holds for every `p in T`, so all local scales are
one common constant `c`. Strict compatibility at one place makes its local
constant positive and therefore makes the common constant positive. QED.

### Interpretation

Local order does not merely suggest the standard local logarithms. It forces
each one up to a local scale. The conservation law couples those initially
independent calibrations and leaves only one global choice of units.

The logical inputs are therefore:

`local multiplicativity + local order + global balance`

and the output is

`the product-formula logarithmic vector, up to common scale`.

## 4. There is no nontrivial “larger everywhere” order

### Proposition 4.1 (product-order obstruction)

Let `x,y in Gamma_T`. If

`lambda_v(x)<=lambda_v(y)`

at every active place `v`, then `x=y`.

### Proof

Every difference

`lambda_v(y)-lambda_v(x)`

is nonnegative. The product formula says their sum is zero. Therefore every
difference is zero. Injectivity of `Lambda_T` then gives `x=y`. QED.

### Meaning

Increasing a rational magnitude at one place must be balanced by contraction
somewhere else. Coordinatewise comparison across every place collapses to
equality. There is therefore no nontrivial global Pareto order on principal
log-valuation vectors.

This prevents a tempting but invalid extension of Stage 1: the full local
geometry cannot be selected by declaring one rational to be globally larger
than another at every place. Multiple local calibrations and a balance law are
the appropriate structure.

## 5. Finite-prime Euclidean log geometry

The product formula supplies a vector space but not a preferred Euclidean
metric. For exploration, equip `R^({infinity} union T)` with the standard
equal-coordinate inner product and restrict it to `H_T`. This is an explicit
additional choice.

For every `p in T`, let `g_p=Lambda_T(p)`. With `e_v` denoting a coordinate
unit vector,

`g_p=(log p)(e_infinity-e_p)`.

The vectors `g_p` form a basis of the real hyperplane `H_T`, and their integer
span is exactly `Lambda_T(Gamma_T)`.

### Theorem E (equiangular prime directions)

In the chosen Euclidean model:

1. `||g_p||=sqrt(2) log p`;
2. for distinct primes `p,q`,

   `<g_p,g_q>=(log p)(log q)`;

3. every pair of normalized prime directions meets at `60` degrees;
4. if `r=|T|`, the squared covolume of the log lattice is

   `(r+1) product_(p in T) (log p)^2`.

Hence its fundamental `r`-dimensional volume is

`sqrt(r+1) product_(p in T) log p`.

### Proof

Each `g_p` has only two nonzero coordinates: `log p` at infinity and
`-log p` at `p`. This gives the norm formula. Distinct vectors overlap only in
their infinity coordinate, giving the inner product formula. Their cosine is

`(log p log q)/(sqrt(2)log p sqrt(2)log q)=1/2`,

so their angle is `60` degrees.

Let `l` be the column vector with entries `log p`, and let

`D=diag((log p)^2)`.

The Gram matrix is

`G=D+l l^T`.

The matrix determinant lemma gives

`det G = det D (1+l^T D^(-1) l)`

`= product_p (log p)^2 (1+r)`.

The square root of a Gram determinant is the volume of the fundamental
parallelotope. QED.

### Important qualification

The product-formula hyperplane and its lattice are canonical after the usual
normalization of absolute values. The `60`-degree statement additionally uses
equal Euclidean weights for the place coordinates. Rescaling local axes changes
the angles. It is a valid and symmetric model geometry, not yet an intrinsic
adelic metric selected by a theorem.

## 6. The two-prime plane

For `T={2,3}`, the logarithmic image lies in

`x_infinity+x_2+x_3=0`.

Its basis is

`g_2=(log 2,-log 2,0)`

and

`g_3=(log 3,0,-log 3)`.

These vectors meet at `60` degrees and their fundamental parallelogram has area

`sqrt(3) log 2 log 3 = 1.3189567080...`.

Ordinary rational order observes only the projection

`lambda_infinity(2^a 3^b)=a log 2+b log 3`.

Lattice points close to the plane `lambda_infinity=0` correspond to unusually
close rational approximations between powers of `2` and `3`. Continued
fractions describe the best such near-cancellations. This places the proposed
two-prime finite theorem inside a local–global plane rather than treating it as
an isolated numerical trick.

## 7. Connection to finite rigidity and arithmetic acceleration

The ordinary integer ordering sees the Archimedean projection but not the
individual finite-place coordinates. Factorization supplies those coordinates;
order data reconstruct the projection weights `log p`.

There are now two different finite questions:

1. **Projection reconstruction:** how quickly do finite integer comparisons
   determine the Archimedean functional on the prime-exponent lattice?
2. **Local reconstruction:** which finite local comparisons and conservation
   constraints determine the whole valuation vector?

The first question is where arithmetic acceleration lives. Pure power
comparisons provide only logarithmic-in-cutoff resolution, while the complete
network of nearby composite comparisons empirically gives much sharper bounds.
The adjacent arithmetic-acceleration branch will study why.

It is not currently a prerequisite for the exact local–global theorem. It
becomes a dependency if we seek quantitative finite adelic reconstruction,
need rates for the two-prime projection, or need exact finite certificates for
publication.

## 8. Computational verification

`adelic_log_geometry.py` checks finite samples of the formulas above. It:

- constructs rational numbers exactly from exponent vectors;
- verifies injectivity over the sampled box;
- checks the product-formula residual;
- computes all pairwise prime-direction angles;
- verifies the Gram determinant and covolume formulas;
- reports the sampled nonidentity rational closest to `1` in Archimedean log
  projection.

For example:

```sh
python3 adelic_log_geometry.py --primes 2 3 5 7 --bound 2
python3 -m unittest -v test_adelic_log_geometry.py
```

The program uses floating-point logarithms only as a reproducibility check.
The proofs are symbolic and do not depend on numerical tolerance.

For `T={2,3,5,7}` and exponent bound `2`, all `625` rational samples were
distinct, the largest product-formula residual was approximately `1.33e-15`,
all six pairwise angles were `60` degrees to displayed precision, and the two
Gram-determinant calculations agreed to machine precision.

## 9. Passage to the actual adeles

The diagonal embedding sends a rational `q` to the principal adele or idele
whose component at every place is the same field element `q`. Applying local
absolute values and logarithms to a principal idele produces `Lambda(q)`.

This map forgets:

- the sign at the real place;
- every `p`-adic unit component;
- residue information;
- additive distances and cancellation inside `Q_p`;
- the restricted-product topology and Haar measure.

The product formula says that principal ideles land in the norm-one subgroup.
It does not say that every norm-one idele is principal.

Stage 3 lifts the analysis from the logarithmic skeleton to the
restricted product itself. The natural structures to examine next are local
additive characters, the diagonal embedding of `Q`, self-duality, Haar measure,
and Poisson summation. Those are the mechanisms through which adelic analysis
reaches zeta and `L`-functions. This construction is completed in
`RATIONAL_ADELES_AND_POISSON.md`.

## 10. Limitations

- The local–global theorem is infinite and exact; it assumes every required
  comparison and exact additivity.
- Global conservation is an independent axiom. It is motivated by the product
  formula but is not derived from local order alone.
- The Euclidean inner product is selected for exploration, not forced by the
  adele topology.
- The finite experiment illustrates proved identities; it is not evidence for
  new physics.
- Nothing here proves a new result about zeta zeros or the Riemann hypothesis.

## 11. Literature boundary

The adelic foundations used here belong to classical number theory. Tate's
thesis develops local normalized valuations, restricted direct products,
adeles, ideles, the product formula, and their role in Fourier analysis and
zeta functions: [J. Tate, *Fourier Analysis in Number Fields and Hecke's
Zeta-Functions* (1950)](https://sites.math.rutgers.edu/~alexk/2023S572/Tate1950.pdf).

Theorems D and E are included with complete proofs so their exact assumptions
can be audited. They should presently be viewed as a clean synthesis and a
platform for the finite and higher-number-field questions in
`RESEARCH_ROADMAP.md`, not as novelty claims.
