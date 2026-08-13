# Order–Factorization Geometry

## A rigorous path from “hidden numerical geometry” to a testable physics hypothesis

**Status:** exploratory research note, 2026-08-11. The theorem is classical in
substance, the geometric framing is interpretive, the finite-rate conjecture is
unproved, and the proposed physical sector has not been observed.

## Abstract

There is a mathematically sound version of the intuition that numbers reveal an
underlying geometry. It does not begin by fitting a nonlinear coordinate to a
desired pattern. It begins with independently meaningful symmetries.

Every positive integer has a unique prime-exponent vector

`v(n) = (v_2(n), v_3(n), v_5(n), ...)`.

This turns multiplication into vector addition. Ordinary numerical order is
then recovered by the linear functional

`log n = sum_p v_p(n) log p`.

A classical rigidity result says that this logarithmic functional is unique up
to scale: every monotone, completely additive real-valued function on the
positive integers is `c log n`. Thus the logarithmic geometry is not chosen
because it fits the data; multiplication and order force it.

Finite linear-programming experiments show a strong quantitative version. If
prime weights are initially free, `E(2)=log 2` is fixed, and only the ordering of
the integers through 100,000 is imposed, the allowed value of `E(3)` is already
confined to

`1.0986091226 <= E(3) <= 1.0986154946`,

an interval of relative width `5.80e-6` containing
`log 3 = 1.0986122887`. Independent Mac and Windows runs agree to numerical
precision.

This suggests a precise mathematical conjecture about the rate of finite
rigidity and a falsifiable physical hypothesis: any independently identified
sector of states whose fusion is multiplication, whose energy is extensive,
and whose energy order matches the fusion labels must have logarithmic energy
levels, prime elementary modes, and zeta-function thermodynamics.

## 1. The conceptual correction

Mathematical axioms are not empirical claims in quite the same way that a law of
physics is. An axiom system can be consistent but still be the wrong model for a
physical regime. The productive question is therefore not simply “are numbers
wrong?” It is:

> Which algebraic operations and symmetries does nature realize, and which
> geometry is forced by those operations and symmetries?

This reverses the method in the original “Number Relativity Theory” draft. A
freely selected coordinate `Phi` can manufacture almost any desired pattern.
That makes it weak evidence. A geometry derived from a composition law,
invariance, and order has far less freedom and can make predictions.

## 2. Prime-exponent space

Let `P` be the set of primes. Map each positive integer to the finitely supported
lattice vector

`v(n) = (v_p(n))_(p in P) in N^(P)`.

The fundamental theorem of arithmetic gives

`v(mn) = v(m) + v(n)`.

The integer `1` is the origin. Each prime is a coordinate direction. A composite
number is a multiparticle or multistep state. In this space, multiplication is
literally translation.

The ordinary size of an integer is recovered by

`L(v) = sum_p v_p log p`,

because `L(v(n))=log n`. Therefore

`n < m  iff  L(v(n)) < L(v(m))`.

The vector of prime weights

`(log 2, log 3, log 5, ...)`

is the normal direction that orders the factorization lattice. Ratios such as
`log 3/log 2` are irrational slopes describing how the powers of independent
prime directions interleave:

`2^a < 3^b  iff  a/b < log 3/log 2`.

This is a rigorous sense in which an irrational relationship is geometric: it
is a limiting slope in an integer lattice forced by two compatible structures,
factorization and order.

## 3. Logarithmic rigidity theorem

The integer theorem below is a special case of a more general result for any
monoid carrying a multiplicative size map. A self-contained proof, group
extension, hypothesis audit, and bridge to ideal norms and adelic geometry are
given in `ABSTRACT_ORDERED_MONOID_RIGIDITY.md`.

The subsequent local–global extension on positive rationals, including the
product-formula conservation theorem and finite-prime log-lattice geometry, is
developed in `LOCAL_GLOBAL_ADELIC_CALIBRATION.md`. The maintained sequence of
work is recorded in `RESEARCH_ROADMAP.md`.

The lift from logarithmic valuations to the full rational adele ring, including
the global additive character, self-dual Haar measure, rational self-annihilator
theorem, and a controlled adelic Poisson formula, is given in
`RATIONAL_ADELES_AND_POISSON.md`.

The number-field synchronization theorem and exact laboratories for `Q(i)` and
`Q(sqrt(5))` are developed in `NUMBER_FIELD_ADELIC_CALIBRATION.md`. They show
how unit lattices and ideal classes synchronize local logarithmic scales across
all places.

### Theorem

Let `E:N_+ -> R` satisfy:

1. **Composition extensivity:** `E(mn)=E(m)+E(n)` for all positive integers
   `m,n`.
2. **Order compatibility:** `m<n` implies `E(m)<=E(n)`.

Then there is a constant `c>=0` such that

`E(n)=c log n`

for every positive integer `n`. Strict order compatibility makes `c>0`.

This is a special, elementary form of a theorem of Erdős on monotone additive
arithmetic functions. Erdős proved the stronger result for arithmetic
additivity on coprime arguments; see
[Erdős (1946)](https://combinatorica.hu/~p_erdos/1946-06.pdf).

### Proof for the completely additive case

Fix integers `a,b>1`. For each positive integer `k`, let

`r_k = floor(k log(a)/log(b))`.

Then

`b^(r_k) <= a^k < b^(r_k+1)`.

Monotonicity and complete additivity give

`r_k E(b) <= k E(a) <= (r_k+1) E(b)`.

Divide by `k`. Since

`r_k/k -> log(a)/log(b)`,

the squeeze theorem gives

`E(a)/E(b) = log(a)/log(b)`.

Taking `b=2` proves `E(n)=c log n`, with `c=E(2)/log 2`.

## 4. The metric version

The same idea selects a unique geometry on positive real magnitudes.

### Theorem

Suppose a metric `d` on `R_(>0)` obeys:

1. **Scale invariance:** `d(lambda a,lambda b)=d(a,b)` for all positive
   `lambda,a,b`.
2. **Ordered geodesic additivity:** if `a<=b<=c`, then
   `d(a,c)=d(a,b)+d(b,c)`.

Then, for some constant `k>0`,

`d(a,b)=k |log(b/a)|`.

### Proof sketch

Let `g(t)=d(1,e^t)` for `t>=0`. Scale invariance and ordered additivity give
`g(s+t)=g(s)+g(t)`. Positivity makes `g` monotone. Every monotone solution of
the additive Cauchy equation is linear, so `g(t)=kt`. Scale invariance and metric
symmetry then give the displayed formula.

Thus Euclidean distance is selected by additive translation symmetry, while
logarithmic distance is selected by multiplicative scale symmetry. Geometry is
not absolute here; it is symmetry-selected.

## 5. Finite rigidity experiment

For a cutoff `N`, assign a free real weight `w_p` to every prime `p<=N`, and
extend it completely additively:

`E_w(n)=sum_p v_p(n) w_p`.

Normalize `w_2=log 2` and impose only

`E_w(n)<=E_w(n+1)` for `1<=n<N`.

These are linear inequalities with integer coefficients. They define a
polyhedron `C_N`. Linear programming gives the smallest and largest possible
weight of each fixed prime.

| `N` | relative width allowed for `w_3` | interval still contains `log 3` |
|---:|---:|:---:|
| 30 | 10.5155% | yes |
| 100 | 1.8027% | yes |
| 300 | 0.4789% | yes |
| 1,000 | 0.1057% | yes |
| 3,000 | 0.03043% | yes |
| 10,000 | 0.007431% | yes |
| 30,000 | 0.002228% | yes |
| 100,000 | 0.0005800% | yes |

At `N=100,000`, the bounds are

`1.0986091226 <= w_3 <= 1.0986154946`,

while

`log 3 = 1.0986122887`.

Equivalently, after dividing by `log 2`, the order constraints force

`1.5849579331 <= w_3/w_2 <= 1.5849671259`,

around

`log_2(3)=1.5849625007`.

The same concentration occurs for `3,5,7,11,13`. At `N=3000`, their relative
interval widths lie between `0.0296%` and `0.0346%`.

The calculation was reproduced on:

- macOS, Python 3.9.6, NumPy 2.0.2, SciPy 1.13.1;
- Windows 10, Python 3.13.14, NumPy 2.5.2, SciPy 1.18.0.

The two platforms returned the same bounds up to floating-point rounding. At
`N=100,000`, the minimum reported constraint slack across those two runs was
about `-6.4e-13`, consistent with solver tolerance rather than a material
violation. The implementation uses a sparse prime-exponent matrix so larger
cutoffs do not allocate a dense `N`-by-`pi(N)` array.

The implementation is in `finite_rigidity.py`.

## 6. A sound new hypothesis: finite logarithmic rigidity

For a fixed odd prime `p`, let

`W_p(N) = sup_(w in C_N) w_p - inf_(w in C_N) w_p`.

### Finite Logarithmic Rigidity Conjecture

For every fixed prime `p`,

`W_p(N) = N^(-1+o(1))`.

In words: finite multiplication and order determine each fixed logarithmic
prime weight to essentially inverse-cutoff precision.

This statement is precise and falsifiable. The computation is evidence, not
proof. A quick log-log regression over `N=30,...,100000` gives an apparent
power near `-1.20`, but eight modest cutoffs are not enough to estimate an
asymptotic exponent. The safer observation is that `N W_3(N)` changes slowly
and the data are compatible with an inverse-`N` law modified by logarithms.

There is also an elementary reason the exponent `-1` is a natural boundary.
Start with `w_q=log q` and perturb only `w_p` by `delta`. For adjacent integers
through `N`, the unperturbed order gap is at least `log(1+1/N)`, while a change
in `p`-adic valuation is at most `floor(log_p(N+1))`. Therefore every

`|delta| < log(1+1/N)/floor(log_p(N+1))`

preserves all the finite inequalities. This gives an interval of order
`1/(N log N)` inside `C_N`. Hence the width cannot decay substantially faster
than inverse `N`, apart from subpolynomial factors. The conjecture asks for a
matching upper scale.

A proof would quantify how quickly ordinary order reconstructs logarithmic
geometry from the factorization lattice. It may connect polyhedral geometry,
Diophantine approximation, smooth neighbors, and additive arithmetic
functions. A brief literature search found stability results for additive
arithmetic functions, but not this exact finite-polyhedron rate; that search is
not exhaustive.

## 7. A falsifiable physics hypothesis

### Multiplicative Spectral Sector Hypothesis

There exists a physical or engineered sector with stable states `S_n`, indexed
independently of energy by positive integers, such that:

1. `S_1` is the vacuum or identity state.
2. Fusion satisfies `S_m ⊗ S_n ~= S_(mn)`.
3. Factorization into elementary stable modes is unique; those modes are
   labeled by primes.
4. A conserved energy is extensive under fusion:
   `E(S_m ⊗ S_n)=E(S_m)+E(S_n)`.
5. The independently assigned fusion order agrees with energy order.

If such a sector exists, the rigidity theorem makes parameter-free predictions
after one energy scale is fixed:

`E(S_n)=epsilon log n`,

`E(S_p)=epsilon log p` for prime modes, and

`Z(beta)=sum_(n>=1) exp(-beta epsilon log n)=zeta(beta epsilon)`.

The Euler product means that the prime occupation numbers are independent
geometric random variables in the noninteracting thermal ensemble:

`P(v_p=k)=(1-p^(-beta epsilon)) p^(-k beta epsilon)`.

The partition function diverges at the critical inverse temperature

`beta_c=1/epsilon`.

This is closely related to Julia's established “primon gas” interpretation;
see [Julia's 1989 preprint record](https://cds.cern.ch/record/203834). The new
point here is methodological: logarithmic prime energies need not be guessed.
They are forced if fusion, extensivity, and order are independently observed.

### How it can fail

The proposal is falsifiable only if labels and fusion are fixed before examining
energies. It fails if:

- fusion is not multiplication;
- factorization is nonunique;
- binding/interactions make energy nonadditive;
- measured energy ratios disagree with `log n/log 2` beyond uncertainty;
- prime occupations show unexplained equilibrium correlations;
- the state labels are retrofitted after looking at the spectrum.

Without those safeguards, any spectrum can be relabeled and the claim becomes
numerology.

## 8. Why the broader vision is not unreasonable

There are serious precedents for arithmetic structures behaving like physical
geometries or spectra:

- The [Bost–Connes system](https://cds.cern.ch/record/283504) is a quantum
  statistical-mechanical system built from number theory, with zeta-related
  thermodynamics and a phase transition.
- [Connes' trace-formula program](https://arxiv.org/abs/math/9811068) interprets
  zeta zeros spectrally using the noncommutative geometry of adele classes.
- The [spectral action principle](https://arxiv.org/abs/hep-th/9606001) derives
  gravitational and Standard Model action terms from spectral data of a
  noncommutative geometry.
- Most strikingly for the motivating vision, Hartnoll and Yang's recent
  [“The Conformal Primon Gas at the End of Time”](https://arxiv.org/abs/2502.02661)
  maps semiclassical BKL gravitational dynamics near a spacelike singularity to
  automorphic forms and `L`-functions, and gives a dual gas of prime-labeled
  oscillators.

These are real mathematical bridges. They do not establish that the physical
universe is literally made of integers, that zeta zeros determine observed
black holes, or that familiar constants can be recovered by pattern matching.
They do show that arithmetic, geometry, spectra, thermodynamics, and gravity can
meet in exact constructions.

## 9. A disciplined research program

The following path preserves the original curiosity while avoiding arbitrary
curve fitting:

1. **Derive before fitting.** Choose algebraic composition and symmetry from an
   independently motivated system.
2. **Classify compatible geometries.** Prove what metrics, energies, or
   operators the symmetries allow.
3. **State invariants.** Predictions must survive coordinate changes and unit
   choices.
4. **Predeclare comparisons.** Fix observables, tolerances, and null models
   before examining target data.
5. **Use held-out tests.** A geometry must predict facts not used to construct
   it.
6. **Penalize flexibility.** Kernels, embeddings, graph rules, and boundary
   conditions count as parameters even when called “natural.”
7. **Separate theorem, conjecture, simulation, and metaphor.** All four can be
   valuable, but they are different evidence classes.

Concrete next projects are:

- produce exact rational dual certificates for the finite LP bounds;
- compute `W_p(N)` sparsely at much larger `N` and test the inverse-`N`
  conjecture;
- prove quantitative stability under missing or noisy order constraints;
- generalize from primes to prime ideals, where logarithmic norms lead to
  Dedekind zeta functions;
- build a small classical or quantum simulator with oscillator energies
  `epsilon log p` and test the predicted thermal occupation statistics.

## 10. Possible technology, without overpromising

An engineered prime-mode spectrum could provide a physical simulator for
Euler products, zeta and `L`-function thermodynamics, or multiplicative random
processes. Chemical potentials attached to prime modes can encode Dirichlet or
automorphic coefficients. This resembles directions already present in the
primon-gas and Bost–Connes literature.

It would not automatically factor large integers or solve the Riemann
hypothesis. Encoding a number as prime occupations may require knowing the
factorization, and reading it out may simply move the computational cost into
state preparation or measurement. A technology claim must account for the full
resource cost.

## Conclusion

The most defensible version of “numbers reveal an underlying geometry” found in
this exploration is:

> Algebra supplies a lattice; symmetry and order select a metric or spectral
> direction; constants appear as invariant conversion factors between those
> structures.

For positive integers, factorization gives the lattice and ordinary order
selects the logarithmic direction. The resulting geometry is exact, rigid, and
experimentally approachable in finite form. Whether nature realizes a physical
multiplicative sector is an open empirical question, but it is now a question
with sharp predictions and clear failure conditions rather than an unrestricted
metaphor.
