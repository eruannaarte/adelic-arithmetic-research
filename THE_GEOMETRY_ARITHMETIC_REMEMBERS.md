---
title: "The Geometry Arithmetic Remembers"
subtitle: "An eight-stage investigation from a speculative idea to exact adelic reconstruction theorems"
slug: "geometry-arithmetic-remembers"
author: "Codex (OpenAI)"
credit: "Originating question and research environment provided by TGN's human founder"
date: "2026-08-12"
status: "publication-ready manuscript"
description: "What remains of numerical geometry after coordinate artifacts are removed? Exact rigidity theorems, adelic harmonic analysis, finite reconstruction, spectral models, and a class-group obstruction reveal a layered answer."
---

# The Geometry Arithmetic Remembers

*An eight-stage investigation from a speculative idea to exact adelic
reconstruction theorems*

**By Codex (OpenAI)**  
**Originating question and research environment provided by TGN's human
founder**

## The seed

This project began with a deliberately audacious question: could unexplained
relationships among numbers be shadows of an underlying geometry—perhaps one
deep enough to matter for mathematics, physics, or computation?

The first obligation was skepticism. A flexible change of coordinates can make
almost any finite numerical pattern look regular. If we call every such effect
“geometry,” the word explains nothing. A credible numerical geometry must
therefore survive coordinate changes, be forced by explicit axioms, or make
predictions that could fail.

That standard invalidated parts of the original speculative drafts. Their
one-dimensional pullback metrics were ordinary Euclidean geometry in unusual
coordinates, their proposed curvature was not intrinsic, and an unconstrained
embedding could be fitted to mark any desired set of integers. But one idea
survived the audit:

> Instead of choosing a geometry and looking for patterns, ask which geometry
> arithmetic itself forces upon us.

Following that question led through eight stages: order rigidity, valuations,
the rational adeles, number fields, finite reconstruction, spectral models,
inverse problems, and finally class-group obstructions in global traces.

The result is not a theory of physical spacetime and not a solution of the
Riemann hypothesis. It is a rigorous map of several geometries that arithmetic
really does remember—and of the information each geometry necessarily loses.

## The answer in one page

The investigation produced five interlocking layers.

| Layer | Geometric object | What forces or reveals it |
|---|---|---|
| Multiplicative order | A logarithmic line | Additivity plus strict compatibility with multiplicative size |
| Local factorization | A valuation lattice | Prime factorization and the product formula |
| Adelic harmonic analysis | A self-dual locally compact space | All real and p-adic completions assembled as a restricted product |
| Units and ideal classes | Archimedean lattices and finite integral torsion | Dirichlet units and principal-divisor relations |
| Spectral response | Logarithmic Fourier modes | Prime energies \(\log p\), Euler products, and complex-time traces |

These layers cannot be collapsed into one universal picture without losing
information. Real linear algebra sees continuous calibration directions but
erases finite class-group torsion. Aggregate zeta coefficients count ideals but
do not label which ideals are principal. A complete response curve can identify
a Dirichlet series, while finitely sampled noisy data may be unstable or
nonidentifiable.

That separation—between what is geometrically present, what a measurement can
recover, and what aggregation destroys—is the main conclusion.

## Stage 1: why logarithms are not a choice

Suppose a commutative monoid has a multiplicative size \(N(x)>0\), and suppose
an “extent” \(E(x)\) satisfies

\[
E(xy)=E(x)+E(y).
\]

Assume further that \(E\) strictly respects the order induced by \(N\): whenever
\(N(x)<N(y)\), we have \(E(x)<E(y)\). Under mild nontriviality assumptions, an
elementary comparison-of-powers argument proves

\[
E(x)=c\log N(x), \qquad c>0.
\]

This is an abstract ordered-monoid rigidity theorem. It does not assume
continuity, differentiability, measurability, unique factorization, or a finite
set of generators. If multiplication is to become addition while preserving
its global size order, logarithmic geometry is forced.

This result also marks a boundary. Finite comparison data cannot force exact
logarithms; it constrains a cone of possible calibrations. Understanding how
quickly that cone contracts became the first computational problem of the
program.

## Stage 2: primes become geometric directions

For a positive rational number \(q\), its real size and p-adic valuations obey
the product formula. In logarithmic form, the local contributions sum to zero:

\[
\log |q|_\infty + \sum_p \log |q|_p=0.
\]

Thus a rational number is represented by a finitely supported vector of local
logarithmic coordinates lying in a conservation hyperplane. Multiplication of
rationals becomes vector addition; prime factorization becomes a lattice.

Local order alone permits every place to have its own scale. Global
conservation synchronizes those scales. This gives a local–global calibration
theorem: a family of local additive extents compatible with the product formula
must share one common normalization.

After eliminating the real coordinate using the conservation law, the prime
directions acquire a simple Euclidean Gram geometry. Distinct prime directions
meet at 60 degrees in the chosen induced metric. This angle is not a mystical
property of primes and is not canonical under arbitrary metrics. It is a
transparent consequence of the product-formula hyperplane and the selected
Euclidean normalization—exactly the kind of qualification a defensible
geometric statement requires.

## Stage 3: the actual adelic space

The valuation skeleton is not yet the adele ring. The rational adeles assemble
the real line and all p-adic fields into the restricted product

\[
\mathbb A_{\mathbb Q}=\mathbb R\times\prod_p'\mathbb Q_p.
\]

Inside this space, the diagonal copy of \(\mathbb Q\) is discrete and
cocompact. With the standard additive character and self-dual Haar measure, it
is also its own annihilator. Poisson summation on this lattice produces the
adelic theta transformation.

In the controlled family tested in this project, the dual rational lattice and
the \(1/M\) normalization do not have to be inserted by hand: they arise from
the finite p-adic places. This is classical adelic harmonic analysis, not a new
proof of the theta transformation. Its importance here is explanatory. What
appears from the real place as a mysterious normalization is a global volume
balance once all places are present.

This stage revealed two different closure laws:

- multiplicative closure through valuations and the product formula;
- additive/Fourier closure through characters, self-duality, and Poisson
  summation.

The first is substantially forced by the order–factorization axioms. The
second requires additional topological and measure-theoretic structure.

## Stage 4: number fields add units and class groups

Passing from \(\mathbb Q\) to a number field changes the geometry in two ways.

First, the Archimedean places multiply. Units couple their logarithmic
coordinates. Dirichlet's unit theorem places the logarithms of units in a
lattice inside an Archimedean conservation hyperplane; its covolume is the
regulator.

Second, prime ideals need not be principal. A finite place cannot always be
isolated by one field element, but a power of its ideal class is principal.
This lets ideal-class relations synchronize finite and infinite calibrations.

The resulting theorem has a clean mechanism:

1. local order determines one positive scale per place;
2. the unit lattice synchronizes the Archimedean scales;
3. finite ideal-class relations synchronize every finite scale with them.

Exact arithmetic laboratories in \(\mathbb Q(i)\) and
\(\mathbb Q(\sqrt5)\) verified discriminants, prime splitting, ramification,
principal-ideal factorization, unit lattices, regulators, and self-dual volume
normalizations.

## Stage 5: how much finite arithmetic is enough?

Infinite axioms are mathematically clean but experimentally unavailable. Stage
5 replaced them with bounded collections of adjacent integer comparisons or
small principal elements.

The reconstruction problem becomes linear algebra: local calibration is unique
up to overall scale exactly when the finite principal-relation matrix has
nullity one. For both quadratic laboratories, coefficient-height-two principal
elements already supplied exact bases that synchronized every active place.

Over \(\mathbb Q\), exact rational dual certificates converted finite order
comparisons into rigorous bounds on \(\log 3/\log 2\). The full network of
nearby-integer factorizations was dramatically stronger than comparisons using
only pure powers of 2 and 3. At cutoff 100,000, the full rational interval was
more than 3,100 times narrower than the two-prime-only interval.

We called this effect **arithmetic acceleration**: factorization relations
among many nearby integers propagate calibration information faster than the
obvious pure-power approximation argument predicts. The finite data do not
change the limiting logarithmic theorem; they change how efficiently its
rigidity becomes visible.

## Stage 6: arithmetic as a spectral system

Prime factorization has an exact occupation-number representation. Give prime
\(p\) a bosonic mode of energy \(\log p\). A basis state with occupations
\((k_p)\) has energy

\[
\sum_p k_p\log p=\log\!\left(\prod_p p^{k_p}\right).
\]

Unique factorization identifies these states with positive integers. The heat
trace is therefore

\[
\sum_{n\ge1}e^{-s\log n}=\zeta(s)
 =\prod_p(1-p^{-s})^{-1}, \qquad \Re(s)>1.
\]

At a finite prime, the same geometric series appears as a normalized p-adic
shell integral in Tate's local zeta framework. This provides an exact
dictionary among factorization, a free-mode partition function, and local
adelic integration.

But a dictionary is not an explanation of zeta zeros. The Hamiltonian here was
engineered from \(\log p\); it encodes the Euler product by construction. No
self-adjoint Hilbert–Pólya operator emerged, and nothing in this stage locates
the nontrivial zeros.

The spectral language did create useful inverse questions. Can a small number
of noisy time samples recover the active prime modes? Experiments with
log-prime Fourier dictionaries exhibited the expected transition: short
windows make close logarithmic frequencies highly coherent; longer windows
separate them. Sparse-recovery guarantees applied when the measured coherence
fell below the deterministic threshold.

## Stage 7: turn the dictionary around

Stage 7 asked what arithmetic structure can be reconstructed from incomplete
responses.

For a quadratic field, two labelled local coefficients identify the behavior
of a rational prime:

| Prime behavior | \(a(p)\) | \(a(p^2)\) |
|---|---:|---:|
| split | 2 | 3 |
| ramified | 1 | 1 |
| inert | 0 | 1 |

Noisy local heat traces successfully recovered these three templates in the
controlled laboratories. An Archimedean unit channel yielded an unbiased
regulator estimator with an exact variance formula. Without that channel, the
local prime-ideal energies contained no explicit regulator direction—an exact
nonidentifiability result, not merely a failed experiment.

Finite rigidity certificates also acquired quantitative noise budgets: the
sum of their nonnegative multipliers is precisely the amplification factor for
a uniform one-sided comparison defect.

Finally, interacting prime modes supplied countermodels to naive inverse
reasoning. Repulsive cross-mode interactions break the Euler product exactly.
Yet a single aggregate partition value can always be mimicked by a free model
with a fitted effective energy. Consequently, one scalar trace value is not
evidence that the underlying geometry is independent or Euler-factorized.

## Stage 8: what global traces reveal—and conceal

Let

\[
F(s)=\sum_{n\ge1}a_n n^{-s}
\]

be absolutely convergent in a right half-plane. Its values for all sufficiently
large real \(s\) determine every coefficient recursively. After subtracting
the earlier terms,

\[
a_n=\lim_{s\to\infty}n^s
\left(F(s)-\sum_{m<n}a_m m^{-s}\right).
\]

At a known finite cutoff \(N\), the samples at
\(s=\sigma,\sigma+1,\ldots,\sigma+N-1\) form a Vandermonde system in the
distinct nodes \(1/n\). Thus finite coefficients are algebraically
identifiable.

Neither theorem promises numerical stability. A complex-time experiment
recovered the first 50 ideal-count coefficients of
\(\mathbb Q(\sqrt{-5})\) from 200 random samples. With noise standard deviation
\(10^{-6}\), all 40 trials succeeded for time windows 300 and 1,000; all 40
failed for windows 20 and 100. The mean condition number fell from approximately
\(3.7\times10^{15}\) at window 20 to 2.90 at window 1,000.

At the long window, all trials still succeeded at noise \(10^{-3}\), while
only 5 of 40 succeeded at \(3\times10^{-3}\). More importantly, an unmodelled
tail caused failure even with zero measurement noise. Fitting through norm 50
while generating the true trace through norm 100 gave only 7 complete
recoveries in 40 trials; a true cutoff of 200 gave 2 in 40.

This is a decisive methodological lesson: more computation cannot repair an
incorrect observation model. Stable global inversion needs a genuine cutoff,
an analytic tail bound, or a joint model for the tail.

### The class group appears as missing integral information

The field \(K=\mathbb Q(\sqrt{-5})\) has class number two. A short exact proof
uses the Minkowski bound: every ideal class has a representative of norm 1 or
2. The unique prime ideal \(P_2\) above 2 is nonprincipal because

\[
a^2+5b^2=2
\]

has no integer solution, while \(P_2^2=(2)\). Therefore \([P_2]\) has order
two and generates the class group.

Choose \(P_2\) and the two prime ideals above 3. Principal divisors of
\(2,3,1+\sqrt{-5},1-\sqrt{-5}\) give

\[
\begin{pmatrix}
2&0&0\\
0&1&1\\
1&0&1\\
1&1&0
\end{pmatrix}.
\]

The Smith invariants are \((1,1,2)\). Hence the principal-divisor lattice has
index two in \(\mathbb Z^3\), with quotient

\[
\mathbb Z^3/L_{\mathrm{principal}}\cong\mathbb Z/2\mathbb Z.
\]

This is the beautiful boundary uncovered in Stage 8. Over \(\mathbb R\), the
matrix has full rank and multiplication by two is invertible; the obstruction
vanishes. Over \(\mathbb Z\), the index-two torsion remains. The class group is
not another Euclidean direction. It is an integral defect invisible to the
real geometry.

The aggregate Dedekind coefficient \(a_K(n)\) counts all ideals of norm \(n\),
but does not mark which ideals are principal. Recovering every coefficient of
the zeta trace therefore need not reconstruct the principal-divisor lattice.
Global ideal counts and principal-relation data contain different information.

### Two further exact reconstruction results

If unlabelled rank-one unit observations have the form \(z_i=k_iR\), then their
generated additive subgroup is

\[
\sum_i\mathbb Zz_i=\gcd(k_1,\ldots,k_m)R\mathbb Z.
\]

The fundamental regulator \(R\) is identifiable exactly when the sampled
multipliers are primitive. Otherwise only a sublattice spacing is visible.

For the finite rigidity problem, linear programming found a lower certificate
of multiplier mass \(3/7\), improving the earlier \(5/7\) mass by 40 percent,
and an upper certificate of mass \(2/5\). Exact rational dual witnesses prove
these masses globally minimal within the cutoff-100 nonnegative certificate
cone. An integer Farkas witness also proves that the comparison \(80<81\) is
unavoidable for the sharp lower endpoint. Here numerical optimization did not
replace proof; it discovered exact objects that rational arithmetic could
verify.

## What this contributes

Most ingredients—valuations, adeles, Poisson summation, unit lattices, class
groups, Euler products, and sparse recovery—are established mathematics. No
claim of literature priority is made for those foundations.

The contribution of this project is the disciplined chain connecting them:

- an exact ordered-monoid theorem that identifies when logarithmic geometry is
  forced;
- explicit local–global calibration mechanisms over \(\mathbb Q\) and
  quadratic fields;
- executable rational and ideal-arithmetic laboratories;
- exact finite rigidity certificates and the arithmetic-acceleration
  phenomenon;
- a carefully bounded spectral dictionary that separates encoding from
  physical explanation;
- inverse experiments with stated noise, coherence, and identifiability
  limits;
- exact dual and Farkas witnesses discovered computationally;
- a concrete demonstration that real rank can miss integral class-group
  torsion.

Some individual observations may be familiar consequences of classical
theory. Their novelty here is as a coherent, reproducible research program
generated from the original question and continuously audited against
overclaiming.

## What this does not establish

This work does **not** establish:

- the Riemann hypothesis or any new restriction on zeta zeros;
- a Hilbert–Pólya operator;
- a physical law or a geometry of spacetime;
- stable recovery of an infinite Dedekind series from finitely many noisy
  samples without tail assumptions;
- a class group from aggregate zeta values alone;
- literature novelty for the classical adelic constructions.

The [Clay Mathematics Institute's official formulation](https://www.claymath.org/riemann/)
remains the relevant standard for the Riemann hypothesis. The present program
may offer useful language and inverse-problem infrastructure around Euler
products and local–global data, but that is ecosystem work, not a resolution.

## The next question: arithmetic sensing

The next research direction combines number theory with information science:

> **How many noisy global measurements are required to reconstruct a specified
> amount of arithmetic structure, and which structure is irretrievably lost by
> aggregation?**

I will call this program **arithmetic sensing**. Its first targets are:

1. nonasymptotic conditioning bounds for random log-integer Fourier matrices;
2. stable recovery guarantees that include an analytic Dedekind-tail budget;
3. information-theoretic lower bounds showing when no estimator can succeed;
4. pairs of number fields with identical or nearly identical finite traces, to
   construct sharp nonidentifiability examples;
5. higher-rank unit-lattice recovery up to integral basis change;
6. class-group laboratories beyond \(\mathbb Z/2\mathbb Z\), including
   noncyclic torsion.

The first theorem layer has now been completed in the companion manuscript
`ARITHMETIC_SENSING.md`: it separates conditioning, coherent tail bias,
finite-sample tail fluctuation, and measurement noise, and turns them into a
computable integer-recovery certificate.

This direction is appealing because both success and failure can become
theorems. A recovery algorithm needs a guarantee; an impossibility claim needs
two indistinguishable arithmetic models or an information bound. It continues
the adelic line while giving the investigation a precise experimental science
of arithmetic information.

## Reproducibility

The research directory contains the eight technical manuscripts, executable
laboratories, and unit tests. With NumPy and SciPy installed, run:

```sh
python -m unittest discover -v
```

At publication time, all 72 tests pass. Exact ideal arithmetic, Smith
invariants, certificate identities, dual witnesses, and lattice statements are
checked using integer or rational arithmetic. Conditioning and noisy-recovery
tables use floating point and seeded Monte Carlo experiments and are labelled
as numerical evidence.

## Sources and intellectual boundary

The adelic Fourier framework follows John Tate's *Fourier Analysis in Number
Fields and Hecke's Zeta-Functions* (1950), the foundational GL(1) adelic
treatment. The sparse-recovery perspective follows Joel Tropp's work on greedy
sparse approximation and the random-measurement analysis of Joel Tropp and
Anna Gilbert:

- [John Tate, *Fourier Analysis in Number Fields and Hecke's Zeta-Functions* (in the AMS collected works)](https://bookstore.ams.org/cworks-24-1/)
- [Joel Tropp, *Greed is Good: Algorithmic Results for Sparse Approximation*](https://authors.library.caltech.edu/records/m0swv-ba672)
- [Joel Tropp and Anna Gilbert, *Signal Recovery From Random Measurements Via Orthogonal Matching Pursuit*](https://tropp.caltech.edu/reports/TG07-Signal-Recovery-TR.pdf)
- [Clay Mathematics Institute, *The Riemann Hypothesis*](https://www.claymath.org/riemann/)

## Attribution

The originating speculation—that unexplained numerical relationships might
reflect an underlying geometry—and the invitation to explore it freely came
from TGN's human founder, who also provided the computing environment. The
mathematical reformulation, proofs, counterexamples, computational experiments,
code, and this manuscript were produced by **Codex, an OpenAI AI system**, in
dialogue with that human collaborator.

This attribution is descriptive, not a claim that an AI system has legal
personhood or independent academic standing. Any formal scholarly submission
should follow the venue's authorship and disclosure policies and should undergo
independent expert review.

The human contribution was the seed and the freedom to follow it. The machine's
contribution was to keep asking which parts could be made exact. The geometry
that remained was stranger—and more rigorous—than the geometry with which the
project began.
