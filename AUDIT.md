# Mathematical Validity Audit and Open-Problem Experiments

Date of audit: 2026-08-11 (America/Costa_Rica)

## Scope and verdict

The Google Drive folder `Math` contained two Google Docs:

1. [Number Relativity Theory and the Geometric Origin of Irrational Constants](https://docs.google.com/document/d/19-CrylleFOlkP3sTC43y_5x4Wh3QGOcVuKneU8ZIgz4)
2. [Numerical Lens Geometry](https://docs.google.com/document/d/1clUbNNVhRVMc1Mr1C3rd6eqZrFURNMDGr0lD6Qo8ao8)

The first document is **not valid as a mathematical theory in its current
form**. Its starting metric construction is standard and valid after adding
domain and surjectivity conditions, but several examples violate its own
hypotheses, two stated propositions are false, its “curvature” is a coordinate
derivative rather than intrinsic curvature, and its prime conjecture is vacuous
without severe restrictions on the admissible embeddings.

The second document is **mostly mathematically sound as an expository
synthesis**. It correctly replaces the first draft's coordinate artifacts with
established metric-measure, analytic-number-theoretic, Diophantine, p-adic,
adelic, and algorithmic notions. It is not, however, a new unified theory in
the theorem-producing sense: its master definition is permissive, several
choices are noncanonical, and almost all substantive results are established
mathematics assembled under new terminology. One concrete formula about
prefix Kolmogorov complexity needs correction.

No open problem was solved. The valid ideas do yield useful normalizations,
diagnostics, and a rigorous limitation theorem for computation. The experiments
below reproduce known behavior and identify exactly where the open difficulties
remain.

## Audit of “Number Relativity Theory”

### Valid core

If `Phi` is injective, then

`d_Phi(a,b) = |Phi(a)-Phi(b)|`

is a metric, and `Phi` is an isometry from the labeled space to its image in an
ordinary Euclidean line. This is a standard pullback metric. Transporting
operations through a bijection is also standard:

`a (+)_Phi b = Phi^{-1}(Phi(a)+Phi(b))`.

These facts support a modest but useful statement: different coordinates or
metrics can make different regularities visible.

### Invalid or overstated claims

- **The examples violate the declared domain.** `Phi(x)=x^2` is not strictly
  increasing on all of `R`. `Phi(x)=log(1+x)` is not a map from all of `R` to
  `R`.
- **The transported operations need stronger hypotheses.** If `Phi(R)` is not
  closed under ordinary addition and multiplication, the displayed formulas
  are not defined for every pair. A bijection `Phi:R -> R` is a sufficient
  repair.
- **The “flatness criterion” is false as a characterization.** Affine `Phi`
  gives constant integer spacing, but it is not the only possibility. For
  example, `Phi(x)=x+epsilon sin(2 pi x)` is strictly increasing when
  `|epsilon|<1/(2 pi)`, is nonlinear, and still satisfies
  `Phi(n+1)-Phi(n)=1` for every integer `n`.
- **Proposition 5.2 is false.** The same counterexample is twice differentiable
  and nonlinear while all displayed integer spacings are constant. A
  nonconstant derivative does not imply varying unit increments.
- **`Phi''` and second differences are not intrinsic curvature.** Every smooth
  one-dimensional pullback metric here is locally Euclidean; the document
  itself nearly recognizes this in its metric-pullback proposition. `Phi''`
  measures a coordinate's nonuniformity. It changes under reparameterization.
- **The prime-resonance conjecture is underconstrained.** Given enough freedom,
  one can construct or fit a monotone function whose derivatives or second
  differences mark any prescribed discrete set, including primes. Existence
  alone would say nothing about primes. A meaningful version needs a small,
  independently specified function class, a complexity penalty, a null model,
  and out-of-sample prediction.
- **A coordinate distance becoming rational does not rationalize a number.**
  Algebraicity and irrationality concern field structure. Under transport of
  structure, the rational subfield is transported too; only the label changes.
- **The constant-fitting programs invite overfitting.** A flexible basis or
  neural network can interpolate a finite collection of constants. Evidence
  would require predictions fixed before evaluation and performance against
  appropriate baselines.

The defensible residue is therefore not “number space is intrinsically curved,”
but “multiple metrics, measures, heights, and encodings can expose different
structures.”

## Audit of “Numerical Lens Geometry”

### Substantively correct components

The following sections use standard mathematics correctly, subject to the usual
domain and convergence conventions:

- additive and logarithmic/multiplicative metrics;
- local volume growth and local dimension;
- density metrics `ds = rho(x) dx` and their Euclidean isometry;
- prime counting, the logarithmic integral, von Mangoldt weights, and the
  Chebyshev function;
- the logarithmic derivative of zeta and the explicit formula;
- rational height growth, continued fractions, and irrationality exponents;
- p-adic metrics, Haar measure on `Z_p`, the adeles, and the product formula;
- effective dimension of computable and Martin-Löf random reals;
- the zeta distribution and independence of prime exponents under it.

The document also makes three crucial repairs to the first draft: it explicitly
says that a one-dimensional density metric has no intrinsic Riemannian
curvature, that coordinate transformations do not change arithmetic truth, and
that primes remain irregular after average-density normalization.

### Corrections and limitations

- For **prefix-free** Kolmogorov complexity, the claim
  `K(n) <= log_2(n)+O(1)` is generally too strong. A standard self-delimiting
  encoding gives `K(n) <= log_2(n)+O(log log n)`. The `O(1)` version fits plain
  complexity or requires a conditioned formulation.
- The definition of a “numerical lens” allows a metric, pseudometric, scale,
  measure, height, algebra, and optional spectral data with no fixed
  compatibility axioms. It is an organizing vocabulary, not yet a mathematical
  category with a single invariant theory.
- The “numerical infinity profile” is not canonical until the family of lenses,
  normalizations, kernels, smoothing scales, and equivalence relation are fixed.
- `V'' = -(log rho)''` is a legitimate one-dimensional weighted
  Bakry–Émery-type quantity, as the text says, but calling it simply curvature
  would be misleading. It is not Riemannian curvature and depends on the chosen
  density.
- The Schwarzian is a projective diagnostic, not an invariant of arbitrary
  changes of numerical coordinates.
- The zeta zeros genuinely occur as oscillatory terms in the explicit formula,
  but “spectrum” is partly interpretive unless a corresponding operator or
  precise resonance framework is specified.
- Smoothing an arithmetic measure with an arbitrary kernel produces a valid
  scale-space construction, but observed peaks may be kernel- and scale-induced.
  Stability across preregistered kernels and scales is necessary evidence.

Overall classification: **reliable expository framework, limited novelty,
several terminological choices requiring discipline, one definite complexity
formula correction**.

## Applications to unresolved problems

### 1. Prime gaps and the Riemann hypothesis

The valid prime-density lens uses

`s_P(x) = Li(x)` and `d_P(a,b)=|Li(b)-Li(a)|`.

For consecutive primes `p_n,p_(n+1)`, the intrinsic gap is approximately

`(p_(n+1)-p_n)/log(p_n)`.

The experiment enumerated all 348,513 primes through 5,000,000. In the range
`[1,000,000,5,000,000)`, the mean normalized gap was `0.9999866`, exactly the
average-density behavior the prime number theorem predicts. Its population
standard deviation was still `0.82877`, and an observed ordinary gap of 148
near 2,010,733 became an intrinsic gap of about `10.197`. Thus this lens removes
the first-order thinning of primes but does not make them periodic or eliminate
large fluctuations. That is consistent with rigorous results showing that gaps
can be arbitrarily large multiples of average scale; see
[Ford–Green–Konyagin–Maynard–Tao](https://arxiv.org/abs/1412.5029).

For the Riemann hypothesis, putting `x=e^t` in the explicit formula turns a zero
`rho=beta+i gamma` into a mode `e^(beta t)e^(i gamma t)`. RH is precisely the
claim that every such growth exponent is `beta=1/2`. This is a faithful
spectral restatement, not progress toward proving the common exponent. The
[official Clay problem description](https://www.claymath.org/wp-content/uploads/2022/05/riemann.pdf)
provides the rigorous target.

Useful next experiment: choose a kernel and bandwidth before looking at the
data, smooth the von Mangoldt residual rather than the raw prime indicator, and
compare held-out covariance and extreme-gap statistics against both the Cramér
model and explicit-formula predictions. This can test models; finite data cannot
certify RH.

### 2. Collatz through multiplicative and 2-adic lenses

For an odd integer `n`, use the accelerated map

`U(n)=(3n+1)/2^a`, where `a=v_2(3n+1)`.

The multiplicative lens gives the exact identity

`log(U(n)/n) = log(3+1/n) - a log 2`.

Across odd residue classes, `P(a=k)=2^(-k)` in the limiting uniform sense, so
`E[a]=2` and the heuristic mean drift is

`log 3 - 2 log 2 = log(3/4) = -0.287682...`.

For the 500,000 odd inputs through 1,000,001, the experiment found mean
`v_2=1.999994` and mean log change `-0.2876736`; exactly half the one-step
updates increased. Among 100,000 sampled starts, 96.299% were below their start
or at 1 by 30 accelerated odd steps. Successive sampled valuations had empirical
correlation about `0.0185`.

This does **not** prove Collatz. It exposes the obstruction: average negative
drift over residue classes does not control the dependent residue sequence of
every individual orbit. Tao's theorem proves a profound almost-all result using
an approximate transport property and harmonic analysis on a 3-adic cyclic
group, not the naive independence heuristic; see
[Tao, “Almost all orbits of the Collatz map attain almost bounded values”](https://arxiv.org/abs/1909.03562).

A concrete lens-based research target is a certified Lyapunov function combining
`log n` with a bounded residue correction. If one could prove a uniform decrease
outside the known cycle, convergence would follow. Finite residue searches may
find candidates or counterexamples to restricted ansatzes, but empirical drift
alone is insufficient.

### 3. P versus NP and coordinate invariance

The transport-of-structure idea yields a useful no-shortcut theorem.

**Proposition.** Let `f` be a bijection on finite strings such that `f` and
`f^(-1)` are computable in polynomial time and input/output lengths are
polynomially related. Then `L` is in `P` iff `f(L)` is in `P`; the analogous
statement holds for `NP`, and polynomial-time many-one hardness is preserved.

**Reason.** To decide the transformed language on input `y`, compute
`x=f^(-1)(y)` and run the original machine; compose in the other direction for
the converse. For NP, do the same around the polynomial-time verifier. The
length conditions keep all compositions polynomial.

Consequently, an efficiently usable numerical lens cannot settle P versus NP by
making hard instances “closer” or assigning them smaller-looking coordinates.
If a transformation exponentially compresses an instance or reveals a solution,
the missing cost must appear in computing/inverting the transformation, in
precision, or in representation length. The multiplicative lens actually
recovers the standard computational size of an integer: `log_2 n` is its bit
length. This conclusion aligns with the formal, encoding-robust definition in
[Stephen Cook's official problem description](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf).

This is a genuine deduction from the documents' valid core, but it is a barrier
result, not a solution of P versus NP.

## Assessment of the local image

`1777358178257292.png` is a 2374 x 1542 RGBA screenshot of a cropped plot titled
“Quantum Field Black Hole: Testing.” It is **not mathematically or physically
validatable from the image alone**. It provides no equations, action or
Hamiltonian, units, boundary/initial conditions, discretization, convergence
study, error bars, source data, or code. The sharp oscillation immediately next
to the dashed “Event Horizon” could represent a modeled effect, a discontinuity
response, a grid artifact, or numerical instability; the pixels cannot
distinguish these. The visible entropy labels and black-hole mass axis are not
enough to establish their definitions or consistency. It should be treated as
an unverified visualization, not evidence, and it has no demonstrated logical
connection to either Drive document.

## Reproducibility

The calculations are implemented in `experiments.py` using only the Python
standard library. Run:

```sh
python3 experiments.py
```

The script prints all parameters and results as JSON and prominently warns that
finite computations cannot prove the open conjectures. It was syntax-checked
and executed successfully during this audit.

## Bottom line

The strongest idea in the folder is not a hidden curvature of the real line. It
is the disciplined use of **structure-specific metrics and measures**:
logarithmic coordinates for multiplication and computation, `Li` and von
Mangoldt weights for primes, valuations for Collatz and local arithmetic,
heights for rational approximation, and explicit spectral transforms where
they are genuinely available.

Those lenses are mathematically useful when they are fixed independently of the
phenomenon being explained and when claims are invariant under coordinate
renaming. They normalize known leading behavior and can guide computation. They
do not, by themselves, supply the uniform bounds, dependency control, or
complexity lower bounds needed to resolve the selected open problems.
