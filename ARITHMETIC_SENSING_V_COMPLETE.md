# Arithmetic Sensing V

## From log-Mellin certificates to a finite multiscale stopping theorem

- **Research lead, theorems, computation, and manuscript:** Codex (OpenAI)
- **Originating question and research environment:** TGN's human founder
- **Status:** complete research publication; not peer reviewed
- **Date:** 13 August 2026
- **Reproducibility:** source, tests, and formal artifacts are included in the
  public repository

## Abstract

Arithmetic Sensing asks a finite inverse question about global arithmetic
traces: when can the first Dirichlet coefficients be recovered exactly from a
finite, noisy, time-limited measurement? Earlier stages separated measurement
noise, finite-window leakage, Gram conditioning, exact aliases, and arithmetic
nonidentifiability. This paper develops the fifth stage from its first analytic
bound to a certified multiscale design and a stopping theorem.

The main analytic step rewrites the universal fixed-degree coefficient
envelope as positive convolution on logarithmic scale. Exact rational Sturm
sequences certify the sensing window over the entire continuum. Directed MPFR
boundaries and exact dyadic convolution then certify the infinite Mellin tail.
An exact common-numerator identity preserves cancellation that a preliminary
triangle inequality had destroyed. Combined with one hundred million Arb
finite-response evaluations and an inverse-free localized Neumann theorem,
this moves the end-to-end formal recovery frontier at the baseline resources
from degree eight to degree thirteen. Degree fourteen is the first failure of
that sufficient certificate, not an impossibility result.

We next treat observation time and sample count as different geometric
resources. At `T=1000`, degree fourteen crosses the formal rounding threshold
between 14,690 and 14,691 readings. Along `m/T=5`, it crosses between
`T=1892` and `T=1893`, but nonmonotonically because the modes lie at
logarithmic frequencies. This resonance structure suggests positive mixtures
of centered time windows. A convex response-signature algorithm produces the
exact nested design

\[
\mu_*=
\frac{125}{65536}\,\mu_{510,2550}
+\frac{65411}{65536}\,\mu_{1780,8900}.
\]

Its short grid is the exact central subset of its long grid, so the measure
uses 8,900 distinct observations, has maximum time 1,780, and gives the formal
all-target degree-fourteen endpoint

\[
0.4980274167750795<\frac12.
\]

Finally, adaptive mode exchange, exact rational LP duals weakened over
192-bit Arb response intervals, and complete million-mode dual audits prove a
finite stopping theorem. On the declared pair family with outer time 1,780 and
short times `300,310,...,800`, the published `T=510` support and dyadic weight
beat every possible positive weight on every other support for the complete
target-50 finite tail through one million. The closest complete support gap is

\[
5.087313085287239\times10^{-7}>0.
\]

The result is a finite, reproducible sensing theorem. It is not a statement
about zeta zeros, arbitrary number-field identification, fundamental physics,
or global optimality over all sensing measures.

---

## 1. The inverse problem

Let

\[
F(s)=\sum_{n\ge1}a_n n^{-s}
\]

be a Dirichlet series observed along the vertical line `s=sigma+it`, with
`sigma>1`. A centered, weighted finite trace attempts to isolate `a_j` by
correlating the measurement against `j^{it}`. In the ideal infinite-time
orthogonal picture, different logarithmic frequencies separate. In a finite
experiment they do not: the response to coefficient `a_k` at target `j`
depends on

\[
\omega_{k,j}=\log(k/j).
\]

For a centered sampling scale `S=(T,m)`, write its response as `R_S(omega)`.
The estimator contains four distinct effects:

1. finite leakage from explicit coefficients;
2. the infinite arithmetic tail;
3. nonorthogonality of the first `N` sensing columns;
4. sensor noise.

They must not be merged into one empirical error number. Arithmetic Sensing V
concentrates on a deterministic coefficient envelope appropriate to number
fields of fixed degree `d`:

\[
|a_n|\le d_d(n),
\]

where `d_d=1^{*d}` is the ordered `d`-fold divisor function. Exact recovery of
an integer coefficient follows whenever the proved coefficientwise error is
strictly below `1/2`.

The baseline parameters are

```text
maximum recovered norm N = 50
vertical line sigma       = 2
observation time T        = 1000
sample count m            = 5000
explicit truncation       = 1,000,000
```

All degree claims in this paper refer to the universal envelope `d_d`, not to
an average number field and not to a probabilistic coefficient model.

---

## 2. Positive geometry on logarithmic scale

The identity

\[
d_d(n)=\#\{(n_1,\ldots,n_d):n_1\cdots n_d=n\}
\]

turns multiplicative factorization into addition after applying the logarithm.
This gives the central analytic reorganization of the project.

Partition the positive log axis into bins. For one factor, bound the mass

\[
\sum_{e^u\le n<e^{u+h}}n^{-\sigma}
\]

from above in each bin. The degree-`d` envelope is then dominated by the
`d`-fold additive convolution of this nonnegative one-factor sequence. Because
the convolution is positive, outward rounding and exact integer convolution
can propagate a proof rather than merely a numerical approximation.

### Log-Mellin convolution theorem

For each tuple of factor bins, take a whole-interval upper bound on the
periodic response kernel over the corresponding sum interval. Multiplying
that kernel supremum by the exact or outward-rounded convolution mass and
summing over all retained bins bounds the complete remote contribution.

The proof uses only:

- ordered factorization;
- positive bin domination;
- additive convolution of log coordinates;
- whole-bin response suprema;
- an analytic terminal integral for the remaining tail.

This is why the method scales with degree more transparently than direct
enumeration of every remote integer.

### Exact continuum positivity

The sensing density is a finite cosine series. Writing `x=cos(theta)` converts
it to a rational polynomial in a Chebyshev basis. Rational Sturm sequences
prove that the chosen window obeys its lower and upper density bounds on the
entire interval, not merely on a sampled mesh. For the reference density the
certificate proves

\[
10^{-5}<p(\theta)<2.499999995
\]

for every real `theta`.

This exact continuum check is essential. A dense plot can suggest positivity
but cannot exclude a narrow negative lobe.

---

## 3. Making the Mellin certificate independently checkable

The first log-Mellin implementation used explicit safety inflation around
floating computations. The verified layer replaces that convention by:

- directed MPFR evaluation of exponential bin boundaries;
- dyadic upper masses at scale `2^-96`;
- exact, carry-free integer convolution;
- hash-pinned compact artifacts;
- a separate checker that reconstructs the mathematical consequence.

The certificate therefore distinguishes discovery from verification. Fast
floating exploration chooses useful parameters. The published theorem is
then recomputed from exact rationals, directed intervals, and deterministic
hash-checked data.

This first formalization preserved the original degree-eight/degree-nine
boundary. It also exposed a deeper problem: the proof was taking absolute
values too early.

---

## 4. Cancellation geometry and the true degree frontier

For a centered cosine window, the shifted sinc responses share a common
trigonometric numerator. Factoring that numerator before interval bounding
retains the cancellation designed into the window. Bounding each shifted term
separately and then adding absolute values discards it.

### Centered common-numerator identity

The response can be reorganized into the form

\[
R(\omega)=\sin(T\omega/2)\,Q(\omega),
\]

with the precise parity and rational denominator structure recorded in the
technical manuscript. The decisive point is that the oscillatory numerator is
shared. Intervalizing the factored expression preserves correlations that the
termwise triangle inequality destroys.

At the unchanged baseline resources, this changes the sufficient fixed-degree
frontier dramatically:

| degree | formal end-to-end endpoint | conclusion |
|---:|---:|:---|
| 13 | `0.3308795520` | exact rounding certified |
| 14 | `0.8438209207` | this certificate does not certify |

Thus degree thirteen is the formal baseline frontier, and degree fourteen is
the first failure. The word *failure* refers to this sufficient proof only. It
does not imply that degree-fourteen recovery is impossible.

The degree-nine remote vector falls by roughly a factor of 247 when the
intended cancellation is retained. That reversal is a useful methodological
lesson: a theorem can be numerically rigorous and still be structurally too
coarse.

---

## 5. End-to-end formal numerics

Formalizing the remote tail alone is not an end-to-end recovery theorem. The
explicit million-term finite band and the inverse Gram consequence also need
controlled arithmetic.

### Exact coefficient construction

Checked unsigned-integer convolution constructs `d_13(n)` and `d_14(n)` for
every `n<=1,000,000`. Fixed-width hashes pin those arrays to the artifacts.

### Arb response enclosures

Arb encloses each finite centered response and every Gram off-diagonal at
192-bit precision. For the degree-13/14 baseline comparison this amounts to
one hundred million finite response evaluations.

### Localized inverse-free Gram theorem

A direct interval matrix inverse is unnecessary and can be wasteful. Write
the Gram matrix as `G=I+E`. A localized Neumann argument bounds each recovered
component using the actual tail vector and row interactions rather than
combining the globally largest tail with the globally worst row. The theorem
controls the inverse consequence without trusting a floating eigensolver or
interval matrix inversion.

Composed with the directed remote artifact, this produces the degree-thirteen
endpoint above. It also rejected a tempting shortcut: starting a single coarse
Mellin certificate immediately after norm 50 destroys adjacent-mode
cancellation so badly that the resulting bound exceeds 12.

---

## 6. The degree-fourteen resource law

Degree fourteen becomes a design problem once the proof is sufficiently
sharp. Observation time and sample count are not interchangeable.

At fixed time `T=1000`, increasing `m` improves discrete quadrature and Gram
conditioning while approaching a nonzero continuous-window leakage floor.
The formal adjacent boundary is:

| `T` | `m` | formal endpoint | result |
|---:|---:|---:|:---|
| 1000 | 14,690 | `0.5000009667019292` | not certified |
| 1000 | 14,691 | `0.49999753821015847` | certified |

Along the proportional path `m=5T`, every integer time from 1000 through 3000
was scanned. The adjacent formal boundary is:

| `T` | `m` | formal endpoint | result |
|---:|---:|---:|:---|
| 1892 | 9460 | `0.5000018477486967` | not certified |
| 1893 | 9465 | `0.4992815921942569` | certified |

The scan is not monotone before the crossing. Large peaks near `T=1100` and
`T=1200` are carried overwhelmingly by the neighboring ratios `51/50` and
`52/50`. Longer observation narrows response lobes, but it can also move an
arithmetic log-frequency onto a side lobe. This is a resonance law, not a
simple data-volume law.

---

## 7. Positive time diversity

The resonance attribution suggests mixing centered windows at different
times. For positive weights `lambda_r` summing to one,

\[
R_{\mathrm{ens}}(\omega)=\sum_r\lambda_rR_r(\omega).
\]

Cancellation occurs inside this signed response before the outer absolute
value. Positivity keeps the construction a genuine sensing measure, while
centering all component grids preserves phase alignment.

A first hand-designed ensemble used exact weights `7/4096` and `4089/4096`
at `(T,m)=(500,2500)` and `(1790,8950)`. Since both grids have spacing `1/5`,
the short grid is the exact central subset of the long one. Only 8,950 distinct
observations are needed. Its formal endpoint is

\[
0.4972362698851084.
\]

This already improves both resource coordinates of the fixed-ratio single
window: fewer readings and a shorter maximum observation time.

---

## 8. Arithmetic multiscale sensing

The hand design can be turned into an algorithm. Each arithmetic mode has a
signed response signature across candidate scales. Choose positive scale
weights to minimize the worst weighted leakage over a declared dangerous-mode
set. Introducing an epigraph variable gives a finite linear program.

### Positive finite minimax theorem

For declared scales `S_r`, modes `omega_k`, positive arithmetic weights `c_k`,
and the probability simplex `lambda_r>=0`, `sum lambda_r=1`, minimizing

\[
\sum_k c_k\left|\sum_r\lambda_rR_{S_r}(\omega_k)\right|
\]

is exactly a linear program after one auxiliary absolute-value variable per
mode. Sparse-support enumeration then reveals whether the optimum actually
needs many scales. Exact dyadic rounding converts the numerical discovery into
a simple implementable measure, and a separate formal checker audits it.

At the first scanned outer-time crossing, a proposed three-scale support
simplifies to two scales:

\[
\boxed{
\mu_*=
\frac{125}{65536}\,\mu_{510,2550}
+\frac{65411}{65536}\,\mu_{1780,8900}}
\]

Both grids use spacing `1/5`. The 2,550-point short grid is centrally nested in
the 8,900-point outer grid, so this is a reweighting of 8,900 samples rather
than an acquisition of 11,450 samples.

The independent all-target Arb/MPFR certificate gives

\[
U_{\mathrm{AMS}}=0.4980274167750795<\frac12.
\]

The corresponding same-grid single-window control fails at
`0.5959293953409309`. The benefit therefore comes from the multiscale weights,
not merely from choosing the outer grid.

### Resource comparison

| design | distinct readings | maximum time | formal endpoint |
|:---|---:|---:|---:|
| fixed `T=1000` single window | 14,691 | 1,000 | `0.4999975382` |
| fixed-ratio single window | 9,465 | 1,893 | `0.4992815922` |
| hand-designed nested ensemble | 8,950 | 1,790 | `0.4972362699` |
| arithmetic multiscale design | **8,900** | **1,780** | `0.4980274168` |

The final design does not have the largest rounding margin in the table. It is
selected for the smaller exact acquisition geometry while remaining formally
below one half.

---

## 9. Adaptive mode exchange and exact support geometry

A design solved on a fixed list of dangerous modes may have missed another
important mode. Adaptive exchange addresses this by alternating:

1. solve the restricted minimax problem;
2. audit all explicit modes through one million;
3. add newly exposed modes;
4. repeat.

Because modes add epigraph constraints, this is mode-row generation. The
scales are columns; calling the procedure scale-column generation would be
incorrect.

Starting from only `51/50` and `52/50`, four audit rounds add twelve exposed
modes. The selected support remains `(510,1780)` in every round. Stability is
evidence, not a proof, so the next layer constructs exact dual witnesses.

For the fourteen-mode restricted problem, every signed response on all 51
candidate short times `300,310,...,800` is enclosed with 192-bit Arb. Rational
primal and dual witnesses are weakened over those intervals. They prove that
`T=510` is uniquely optimal over the declared pair-support family for that
restricted objective.

| support statement | rigorous gap |
|:---|---:|
| optimized `T=510` weight versus runner-up `T=500` | `5.150707611844021e-7` |
| published dyadic `125/65536` weight versus all other supports | `5.077022819265975e-7` |

This is a support-selection theorem, not yet a stopping theorem: an omitted
mode could in principle alter the ordering.

---

## 10. Residual stopping

Let the outer scale be `O=(1780,8900)`, let `S=(T,5T)` be a candidate short
scale, and define the complete target-50 finite objective

\[
F_S(x)=\sum_{k=51}^{10^6}\frac{d_{14}(k)}{k^2}
\left|xR_S(\log(k/50))+(1-x)R_O(\log(k/50))\right|.
\]

The published design has formal feasible upper

\[
B=3.9230270623181385\times10^{-6}.
\]

The stopping proof has two layers.

### Selected-mode screen

The fourteen-mode restricted objective drops only nonnegative terms, so each
restricted dual lower bound is also a lower bound for the complete objective.
This immediately eliminates 45 of the 50 competing short times. The five
survivors are

```text
440, 480, 490, 500, 520.
```

### Complete dual audit

For each survivor choose any dual values `|y_k|<=1`. Binary64 exploration
proposes signs `y_k in {-1,+1}` for `k>=52`; their validity does not depend on
matching the true response sign. A rational `y_51` balances the short and
outer component scores and is checked to lie in `[-1,1]`. Arb then encloses all
two million component terms for that support.

| short time | complete finite dual lower |
|---:|---:|
| 440 | `6.020412009681841e-6` |
| 480 | `5.532877676613297e-6` |
| 490 | `4.782812525397629e-6` |
| 500 | `4.431758370846863e-6` |
| 520 | `5.145779545240515e-6` |

Every lower bound exceeds `B`.

### Finite pair-support stopping theorem

Fix degree 14, target 50, norms `51<=k<=1,000,000`, the exact published
binary64 window coefficients, outer scale `(1780,8900)`, short scales `(T,5T)`
for `T in {300,310,...,800}`, and arbitrary pair weight `x in [0,1]`.

Then the published support `T=510` at exact weight `125/65536` has strictly
smaller complete finite leakage than the minimum attainable on every other
declared pair support.

The closest competitor is `T=500`, with certified separation

\[
4.431758370846863\times10^{-6}
-3.9230270623181385\times10^{-6}
=5.087313085287239\times10^{-7}>0.
\]

For 45 supports the selected-mode lower bound proves the claim. The complete
dual bounds prove it for the remaining five. These cases exhaust the declared
family.

This theorem explains exactly what has stopped: no unselected target-50 finite
mode through one million can make another declared pair support outperform the
published one.

---

## 11. The completed theorem stack

The final design rests on modular results rather than one monolithic numerical
claim:

| layer | role | verification |
|:---|:---|:---|
| continuum density | the window is positive and bounded everywhere | exact rational Sturm sequences |
| remote arithmetic tail | every norm beyond the explicit cutoff is covered | directed MPFR + exact dyadic convolution |
| cancellation | intended window correlations survive the bound | exact common-numerator identity |
| finite tail | every explicit response through one million is enclosed | 192-bit Arb |
| Gram consequence | tail bounds become coefficient bounds | localized inverse-free Neumann theorem |
| recovery | every target 1 through 50 stays below `1/2` | end-to-end artifact |
| design | multiscale weights minimize a declared finite objective | convex LP + exact rationalization |
| restricted support | `T=510` uniquely wins on exchanged modes | rational duals over Arb intervals |
| stopping | all residual target-50 finite modes are accounted for | selected-mode screen + million-mode duals |

Two statements remain intentionally separate. The all-target recovery theorem
includes finite tails, remote tails, and Gram conditioning. The stopping
theorem proves support optimality only for the complete finite target-50
objective on the declared pair family. Neither is silently substituted for the
other.

---

## 12. Reproduction

Create a Python 3.11 or newer environment and install the pinned requirements:

```bash
git clone https://github.com/eruannaarte/adelic-arithmetic-research.git
cd adelic-arithmetic-research
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate with `.venv\\Scripts\\Activate.ps1`.

Run the complete test suite:

```bash
python -m unittest discover -v
```

The principal milestone commands are:

```bash
# Exact positivity and the first log-Mellin studies
python arithmetic_sensing_v.py

# Directed remote-tail artifacts
python verify_mellin_certificate.py

# End-to-end Arb/Neumann artifact
python verify_end_to_end_certificate.py --processes 8

# Degree-fourteen resource law
python degree_fourteen_resource_law.py

# Nested time diversity
python time_ensemble_design.py

# Arithmetic multiscale discovery
python arithmetic_multiscale_sensing.py

# Adaptive support theorem
python adaptive_multiscale_exchange.py
python verify_adaptive_multiscale_certificate.py

# Complete residual stopping theorem
python residual_stopping_envelope.py --processes 5
python verify_residual_stopping_certificate.py --processes 5
```

The three final dependency artifacts have SHA-256 digests:

```text
adaptive restricted-support artifact
01d385eb6d02bc9302b4f161183e0ee097768109f949e750fc6ec67a38b1726f

all-target multiscale recovery artifact
89b316584d9179c13232ad99b9515067fdf67329e6df3db4c48220d6b8c3ff7b

complete residual-stopping artifact
5e098d01666af97a9535e466bd9d12e723a72c069af659c82a3a980a9b29bb53
```

The compact artifact checkers validate schemas, dependencies, exact rational
consequences, interval directions, and pinned projections. Expensive artifact
rebuilding is separate from fast independent checking.

---

## 13. Validity and novelty boundary

### Established in this publication

- exact continuum bounds for the rationalized cosine window;
- a positive log-Mellin convolution theorem for fixed-degree envelopes;
- directed and exact arithmetic for the remote-tail certificate;
- cancellation-aware remote bounds;
- an end-to-end formal degree-thirteen baseline frontier;
- exact degree-fourteen resource crossings at the declared adjacent points;
- an all-target degree-fourteen recovery theorem using 8,900 nested readings;
- unique restricted support selection over 51 declared pair supports;
- a complete explicit target-50 finite stopping theorem for that pair family.

### Not established

- impossibility of degree-fourteen recovery at the baseline resources;
- optimality among ensembles with three or more active scales;
- optimality over continuous or nonintegral observation times;
- all-target support optimality for the complete formal objective;
- a noise-optimal or statistically optimal acquisition design;
- recovery of an arbitrary number field from finitely many zeta coefficients;
- a theorem about zeta zeros or the Riemann hypothesis;
- a new physical law, new axioms of number, or a theory of reality;
- a literature-priority claim without independent specialist review;
- source-level verification in a proof assistant.

The divisor identity, Dirichlet convolution, Sturm's theorem, Chebyshev
polynomials, Fejer--Riesz factorization, linear-program duality, interval
arithmetic, and Neumann-series reasoning are classical ingredients. The
project-level contribution is their particular combination into a modular
arithmetic sensing certificate, the cancellation correction, the exact
resource and resonance studies, the nested multiscale algorithm, and the
finite residual stopping architecture.

Relevant classical context includes:

- A. Fink, “Multifactorisations and divisor functions,” *Utilitas
  Mathematica* 125 (2025), 43--60,
  [article](https://combinatorialpress.com/um-articles/vol-125/multifactorisations-and-divisor-functions/).
- V. Magron et al., “Exact SOHS decompositions of trigonometric univariate
  polynomials with Gaussian coefficients,”
  [arXiv:2202.06544](https://arxiv.org/abs/2202.06544).
- R. Perlis, “On the equation `zeta_K(s)=zeta_K'(s)`,” *Journal of Number
  Theory* 9 (1977), 342--360,
  [doi:10.1016/0022-314X(77)90070-1](https://doi.org/10.1016/0022-314X(77)90070-1).

No novelty claim should be interpreted beyond the explicit constructions and
computational theorems without a broader literature review and peer review.

---

## 14. What comes after Arithmetic Sensing V

This is the natural completion boundary for the fifth publication. The next
line begins with questions that materially enlarge the design class:

1. multi-target adaptive exchange rather than a target-50 design objective;
2. rational and interval duals for arbitrary positive multiscale ensembles;
3. genuine scale-column generation over dense or continuous time families;
4. formal remote-tail and Gram penalties inside the design objective;
5. analytic explanation of the nearly common residual contribution;
6. noise-aware acquisition and information-budget allocation;
7. downstream applications to observability and AI data acquisition, kept
   secondary to the pure theorem development.

Those questions belong to a new publication. Arithmetic Sensing V ends with a
fully reproducible degree-fourteen nested sensor, a certified recovery endpoint,
and a finite stopping theorem that states precisely how far its support
optimality has been proved.
