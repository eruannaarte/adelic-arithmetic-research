# Global Inverse Reconstruction and Class-Group Obstructions

## Stage 8 of the order–factorization and adelic-geometry program

**Status:** completed first global inverse layer, 2026-08-12. Exact results
include uniqueness of Dirichlet coefficients from a full response curve,
finite Vandermonde identifiability, an index-two principal-divisor lattice in
`Q(sqrt(-5))`, primitive unit-lattice recovery, and minimum-mass rational
rigidity certificates. Numerical experiments quantify conditioning, noise,
tail mismatch, and missing-comparison failure. No claim about zeta zeros or
physical spacetime is made.

## Abstract

Stage 7 reconstructed arithmetic data from labelled local probes. Stage 8 asks
what remains possible after local contributions are combined into a global
trace.

Three kinds of obstruction appear.

1. **Analytic conditioning:** a finite global Dirichlet trace is invertible in
   principle, but short observation windows make nearby logarithmic frequencies
   almost indistinguishable.
2. **Model tails:** even noiseless data gives wrong finite coefficients if the
   true trace contains unmodelled higher norms.
3. **Integral torsion:** real relation ranks can be full while the integer
   principal-divisor lattice has finite index. In `Q(sqrt(-5))`, this index is
   two and exactly recovers the class-group obstruction.

Two robustness constructions partly compensate:

- minimum-mass dual certificates reduce worst-case order-defect
  amplification;
- alternative certificates improve survival under missing comparisons.

An unlabelled rank-one unit lattice is also recoverable exactly when its sampled
integer multiples are primitive. If their gcd is `d>1`, only the sublattice
spacing `dR` is identifiable.

## 1. What a global trace determines in principle

Let

`F(s)=sum_(n>=1) a_n n^(-s)`

be an absolutely convergent Dirichlet series in some right half-plane.

### Theorem A (uniqueness from a complete real response curve)

Knowledge of `F(s)` for all sufficiently large real `s` uniquely determines
every coefficient `a_n`. Recursively,

`a_1=lim_(s->infinity)F(s)`

and, after `a_1,...,a_(n-1)` are known,

`a_n=lim_(s->infinity) n^s`

`  * (F(s)-sum_(m<n)a_m m^(-s))`.                         (1)

#### Proof

After subtracting the known terms, multiply the remaining series by `n^s`:

`a_n+sum_(m>n)a_m(n/m)^s`.

Choose a real `sigma_0` in the half-plane of absolute convergence. The
absolute value of the tail is bounded by

`(n/(n+1))^(s-sigma_0) n^(sigma_0)`

`  * sum_(m>n)|a_m|m^(-sigma_0)`,

which tends to zero. QED.

This is an identifiability theorem, not a stable numerical algorithm. It uses
an entire asymptotic response curve and limits at arbitrarily large `s`.

### Theorem B (a known finite cutoff is algebraically identifiable)

Suppose

`F_N(s)=sum_(n=1)^N a_n n^(-s)`.

Fix real `sigma` and sample at `s=sigma+j`, `j=0,...,N-1`. Then the resulting
`N` values uniquely determine `a_1,...,a_N`.

#### Proof

The sampling matrix is

`A_(j,n)=n^(-sigma)(1/n)^j`.

It is a Vandermonde matrix in the distinct nodes `1,1/2,...,1/N`, multiplied
by an invertible diagonal matrix. Its determinant is nonzero. QED.

Again, nonzero determinant does not imply good conditioning. The real-moment
Vandermonde system is generally a poor numerical inversion method.

## 2. Complex-time global inversion

For a number field `K`, write

`zeta_K(s)=sum_(n>=1)a_K(n)n^(-s)`,

where `a_K(n)` counts nonzero integral ideals of norm `n`. At a known cutoff
`N`, sample

`F_N(sigma+it_j)=sum_(n<=N)a_K(n)n^(-sigma)e^(-it_j log n)`. (2)

The unknown weighted coefficients are observed through a log-integer Fourier–
Vandermonde matrix. Randomized times avoid the exact aliases possible on a
regular grid.

### Quadratic ideal-count coefficients

If `p^e` is a prime power in a quadratic field, its local coefficient is

| behavior of `p` | `a_K(p^e)` |
|---|---:|
| split | `e+1` |
| ramified | `1` |
| inert | `1` for even `e`, `0` for odd `e` |

Multiplicativity then gives every `a_K(n)`. In particular, `a_K(p)` alone is
`2`, `1`, or `0` for split, ramified, or inert `p`. A recovered coefficient
sequence therefore contains the labelled splitting data studied locally in
Stage 7.

For `Q(sqrt(-5))`, the first twenty coefficients are

`1,1,2,1,1,2,2,1,3,1,0,2,0,2,2,1,0,3,0,1`.

### Finite inversion experiment

Recover all 50 coefficients through norm `50` from 200 randomized samples at
`sigma=2`. The supplied observations initially contain exactly that finite
Dirichlet polynomial. Integer rounding is part of the prior: ideal counts are
known to be nonnegative integers.

With complex Gaussian noise standard deviation `10^-6`:

| time window `T` | mean condition number | complete recoveries |
|---:|---:|---:|
| 20 | `3.71*10^15` | 0/40 |
| 100 | `1.70*10^14` | 0/40 |
| 300 | 3.48 | 40/40 |
| 1,000 | 2.90 | 40/40 |

The smallest adjacent frequency gap near the cutoff is approximately `1/N`,
so a window comparable to `N` is only a crude resolution scale; the realized
condition number gives the more relevant finite diagnostic.

At `T=1000`:

| noise sd | complete recoveries | mean correct coefficients | mean maximum coefficient error |
|---:|---:|---:|---:|
| 0 | 40/40 | 50.0 | `<9*10^-13` |
| `10^-5` | 40/40 | 50.0 | 0.00281 |
| `10^-4` | 40/40 | 50.0 | 0.0313 |
| `10^-3` | 40/40 | 50.0 | 0.296 |
| `3*10^-3` | 5/40 | 47.88 | 0.899 |
| `10^-2` | 0/40 | 35.98 | 3.13 |

### Tail mismatch is not ordinary measurement noise

Keep the fitted model at norms through `50`, use no measurement noise, but let
the true finite trace contain coefficients through a larger cutoff:

| true cutoff | complete recoveries | mean correct coefficients |
|---:|---:|---:|
| 50 | 40/40 | 50.0 |
| 100 | 7/40 | 47.93 |
| 200 | 2/40 | 47.5 |

The fitted matrix remains well-conditioned; failure comes from projecting an
unmodelled tail onto the first 50 modes. A global inverse theorem therefore
needs either a genuine cutoff, an analytic tail bound, or a joint nuisance
model. More computation cannot repair a misspecified observation model.

## 3. A finite class-group obstruction in `Q(sqrt(-5))`

Let

`K=Q(sqrt(-5))`, `O_K=Z[sqrt(-5)]`, `Delta_K=-20`.

The quadratic Minkowski bound is

`2sqrt(20)/pi<3`.

Every ideal class therefore contains an integral ideal of norm `1` or `2`. The
prime `2` ramifies:

`(2)=P_2^2`, `N(P_2)=2`.

The ideal `P_2` is not principal, because the norm equation

`a^2+5b^2=2`

has no integer solution. Hence `P_2` represents a nontrivial class of order
two, and the class number is exactly two.

### Principal-divisor matrix

Select `P_2` and the two primes `P_3,P_3bar` above `3`. In this column order,
the principal divisors of

`2, 3, 1+sqrt(-5), 1-sqrt(-5)`

give the exact integer matrix

```text
[2 0 0]
[0 1 1]
[1 0 1]
[1 1 0]
```

### Theorem C (the class group as an index defect)

The row lattice of this matrix has Smith invariants

`(1,1,2)`.

It is the sublattice of `Z^3` consisting of triples with even coordinate sum,
and

`Z^3/L_principal is isomorphic to Z/2Z`.                 (3)

#### Proof

The three selected primes are nonprincipal: norm equations for `2` and `3`
have no solutions. Since the class group has order two, each represents its
nonzero class. Therefore a divisor supported on them is principal precisely
when its coordinate sum is even.

Every displayed row has even sum. Direct gcds of minors give determinantal
divisors `1,1,2`, hence Smith invariants `(1,1,2)` and row-lattice index two.
The displayed lattice is therefore the full parity kernel. QED.

### Why Stage 4's real theorem did not see the obstruction

Over `R`, multiplication by `2` is invertible and the row span fills `R^3`.
The finite quotient in (3) disappears after tensoring with `R`. Thus:

- real calibration synchronization sees no residual continuous direction;
- integral inverse reconstruction detects a torsion obstruction of order two.

The class group is not an extra Euclidean dimension. It is a finite defect in
the integral relation lattice.

This also quantifies delayed visibility: a principal divisor supported only at
`P_2` must have even exponent. Exponent two is first, supplied by `(2)=P_2^2`.

### What the aggregate Dedekind trace omits

The coefficient `a_K(n)` counts all ideals of norm `n`; it does not label which
of them are principal. Consequently a recovered finite coefficient stream
does not by itself reconstruct the principal-divisor sublattice. Stage 8 needs
both global ideal-count data and principal-relation data to expose (3).

## 4. Minimum-noise and redundant rigidity backbones

For a fixed exact endpoint, minimize

`sum_n y_n`

over all nonnegative dual certificates. By Stage 7, this objective is exactly
the worst-case amplification of a uniform one-sided comparison defect.

At cutoff `100`, the sharp lower bound `11/7` admits the new minimum-mass
identity

`(a_26+a_64+a_80)/7=(11/7)e_2-e_3`.                       (4)

Its mass is `3/7`, versus `5/7` in the first extracted certificate—a 40%
reduction. A second minimum-mass identity is

`(a_24+2a_80)/7=(11/7)e_2-e_3`.                           (5)

Both require comparison `80<81`. An LP feasibility search suggested that no
nonnegative certificate for the exact `11/7` endpoint exists at cutoff `100`
after deleting that comparison. The conclusion is proved independently of the
floating-point solver: the stored integer Farkas witness pairs
nonpositively with every remaining comparison row but pairs to `1` with the
target. A fully disjoint but looser backup is

`a_8/2=(3/2)e_2-e_3`.                                     (6)

For the sharp upper bound `8/5`, the minimum-mass certificate remains

`(a_27+a_63)/5=e_3-(8/5)e_2`,                             (7)

while an edge-disjoint alternative is

`(a_57+a_75+a_87+a_99)/5=e_3-(8/5)e_2`.                  (8)

The “minimum-mass” assertions in (4), (5), and (7) also have exact rational
certificates. Stored dual vectors satisfy `<a_n,z><=1` for every cutoff-100
comparison row and pair with the lower and upper targets to `3/7` and `2/5`,
respectively. Weak duality matches the displayed primal masses, proving global
optimality within the cutoff-100 nonnegative certificate cone.

### Missing-comparison survival

Assume every comparison is independently present with probability `q`. The
probability that the primary minimum-mass lower and upper pair is intact is
`q^5`. Allowing either discovered exact lower and either exact upper backbone
gives:

| `q` | primary pair | redundant alternatives |
|---:|---:|---:|
| 0.80 | 0.3277 | 0.5846 |
| 0.90 | 0.5905 | 0.8252 |
| 0.95 | 0.7738 | 0.9283 |
| 0.99 | 0.9510 | 0.9890 |

This yields two different robustness objectives:

- minimize multiplier mass for amplitude noise;
- diversify support for missing-data resilience.

They need not select the same certificate.

## 5. Recovering an unknown rank-one unit lattice

Stage 7 assumed that the powers `k` in observations of `phi^k` were labelled.
Now suppose exact scalar projections are observed only as

`z_i=k_i R`,

where `R>0` and the positive integers `k_i` are unknown.

### Theorem D (primitive-sample criterion)

The additive subgroup generated by the observations is

`sum_i Z z_i=gcd(k_1,...,k_m) R Z`.                        (9)

Therefore the fundamental spacing `R` is recoverable from the observed lattice
if and only if the sampled multipliers have gcd one. If their gcd is `d>1`,
the data identifies only the sublattice spacing `dR`.

#### Proof

Bézout's identity says the integer combinations of `k_1,...,k_m` are exactly
the multiples of their gcd. Multiply by `R`. QED.

For `Q(sqrt(5))`:

- unknown powers `{6,10,15}` are primitive and identify `R=log phi`;
- unknown powers `{6,10,14}` have gcd two and identify `2R`, not `R`.

The second case is an exact ambiguity, not a numerical failure.

### Noisy bounded-multiplier experiment

Enumerate bounded integer assignments, refit the common spacing by least
squares, and choose the largest spacing compatible with a `3sigma` residual
tolerance. For the primitive sample `{6,10,15}`, 500 trials give:

| scalar noise sd | recovery within 5% | mean relative error |
|---:|---:|---:|
| 0 | 500/500 | 0 |
| 0.0005 | 500/500 | `4.45*10^-5` |
| 0.002 | 500/500 | `1.83*10^-4` |
| 0.01 | 500/500 | `8.33*10^-4` |
| 0.03 | 34/500 | 0.242 |

The abrupt high-noise failure reflects integer-assignment ambiguity. The
algorithm assumes a known multiplier bound; without it, arbitrarily fine
sublattices remain compatible with noisy finite data.

## 6. Integrated identifiability map

| desired structure | sufficient Stage 8 data | obstruction when removed |
|---|---|---|
| ideal-count coefficients | controlled finite global trace with resolved log frequencies | short-window ill-conditioning or unmodelled tail |
| quadratic splitting | recovered labelled coefficient `a_K(p)` | loss of rational-prime labels |
| principal class relation | integer principal-divisor vectors | aggregate ideal counts do not mark principality |
| class torsion | Smith quotient of the principal lattice | tensoring with `R` erases torsion |
| rank-one regulator | primitive Archimedean unit samples | gcd greater than one exposes only a sublattice |
| sharp rigidity interval | exact backbone support | missing critical comparison |
| noise-stable rigidity | minimum multiplier mass | endpoint-only optimization may amplify defects |

The “underlying geometry” emerging from the program is therefore stratified:

- a real logarithmic hyperplane for calibration;
- a discrete valuation lattice for factorization;
- finite torsion in the quotient by principal relations;
- an Archimedean unit lattice;
- Fourier response curves whose inversion has finite resolution limits.

No single scalar metric or trace contains all these layers without additional
labels and priors.

## 7. Exact results, evidence, and limitations

### Proved exactly

- uniqueness of a convergent Dirichlet series from its full large-real response;
- finite Vandermonde identifiability at a known cutoff;
- quadratic ideal-count coefficient formulas;
- class number two and the Smith quotient `Z/2Z` in `Q(sqrt(-5))`;
- cutoff-100 certificate identities and exact alternatives;
- exact dual optimality of the minimum-mass cutoff-100 certificates;
- infeasibility of the sharp lower certificate after deleting comparison 80,
  certified by an integer Farkas separator;
- the primitive-gcd criterion for unknown rank-one unit samples.

### Numerically verified

- finite global trace conditioning, noise thresholds, and tail mismatch;
- missing-comparison availability gains from redundant backbones;
- noisy bounded-integer unit-lattice recovery.

### Not established

- stable inversion of a complete infinite Dedekind trace from finitely many
  noisy samples without tail priors;
- class-group reconstruction from aggregate zeta values alone;
- random-time sample-complexity bounds uniform in the norm cutoff;
- optimal robust certificate families at large cutoffs;
- higher-rank unit-lattice recovery with unknown `GL_r(Z)` basis;
- analogous exact laboratories for larger class groups;
- a Hilbert–Pólya operator, a result about zeta zeros, or a physical law.

## 8. Reproduction

```text
python3 class_group_obstruction.py

python global_trace_inversion.py \
  --maximum-norm 50 --trials 40

python redundant_rigidity_backbones.py

python unknown_unit_lattice.py \
  --trials 500

python -m unittest discover -v
```

The ideal arithmetic, Smith invariants, certificate identities, and exact
lattice statements use integer or rational arithmetic. Trace inversion and
noisy lattice recovery use floating point and seeded Monte Carlo trials.

## 9. Recommended continuation

1. Generalize the Smith-lattice laboratory to class groups of order greater
   than two and noncyclic class groups.
2. Prove random-time conditioning bounds for the log-integer Fourier matrix.
3. Treat the omitted Dirichlet tail analytically or estimate it jointly with
   the target coefficients.
4. Optimize large-cutoff certificate portfolios under combined amplitude and
   missing-edge risk.
5. Recover higher-rank unit lattices up to `GL_r(Z)` using noisy geometry of
   numbers.
6. Compare fields with the same or nearly indistinguishable finite global
   traces to map genuine arithmetic nonidentifiability.

## 10. Sources and novelty boundary

The number-field zeta integral, ideal norms, places, units, and adelic
Fourier/Poisson framework are classical and follow [J. Tate, *Fourier Analysis
in Number Fields and Hecke's Zeta-Functions*
(1950)](https://sites.math.rutgers.edu/~alexk/2023S572/Tate1950.pdf).

The coherence and sparse-recovery viewpoint inherited from Stage 7 follows [J.
Tropp, *Greed is Good: Algorithmic Results for Sparse Approximation*
(2004)](https://authors.library.caltech.edu/records/m0swv-ba672) and [J. Tropp
and A. Gilbert, *Signal Recovery From Random Measurements Via Orthogonal
Matching Pursuit*
(2007)](https://authors.library.caltech.edu/records/hg25b-hf247).

The finite proofs and computations here are elementary constructions tailored
to this program. No literature-priority claim is made.
