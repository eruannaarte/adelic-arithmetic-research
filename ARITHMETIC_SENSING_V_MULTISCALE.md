# Arithmetic Sensing V — Arithmetic Multiscale Sensing

## A convex response-signature algorithm and a smaller degree-fourteen sensor

- **Research lead, theorem, computation, and manuscript:** Codex (OpenAI)
- **Originating question and research environment:** TGN's human founder
- **Status:** algorithm implemented; formal certificate complete
- **Date:** 13 August 2026
- **Parent manuscript:** `ARITHMETIC_SENSING_V_TIME_DIVERSITY.md`

## Abstract

The preceding time-diversity result constructed one positive nested sensing
measure by hand. This paper turns that construction into an algorithm.

For a finite collection of omitted arithmetic ratios and candidate centered
subwindows, each window determines a signed response vector. Positive
multiscale design is therefore convex geometry: choose a point in the convex
hull of those response vectors that minimizes the worst weighted target
leakage. Absolute values are represented by epigraph variables, so the
declared finite design problem is a linear program. Small-support enumeration
and exact dyadic rounding then turn its numerical output into a simple
rational measure. The optimization is only a discovery layer; an independent
Arb/MPFR computation remains the proof.

Applied to the degree-fourteen boundary, the procedure first found a
three-scale cancellation design at maximum time 1,780. Optimizing the complete
localized consequence then drove the middle weight to zero, revealing the
sparser exact candidate

\[
\mu_{\mathrm{AMS}}
=\frac{125}{65536}\mu_{510,2550}
+\frac{65411}{65536}\mu_{1780,8900}.
\]

Both grids have spacing `1/5`; the short grid is an exact central subset of
the long one. The measure therefore uses 8,900 distinct readings, not 11,450.
The final end-to-end certificate evaluates all 50 targets, all finite omitted
norms through one million, both directed-MPFR remote dependencies, and every
signed ensemble Gram row. Its formal coefficient endpoint is

\[
U_{\mathrm{AMS}}=0.4980274167750795<\frac12.
\]

This is below `1/2`, so exact integer recovery is certified. It reduces the
previous nested construction by 50 readings and 10 time units. No global
optimality or noisy-recovery advantage is claimed.

---

## 1. Response signatures of arithmetic modes

For a normalized positive centered window `mu_a`, let

\[
R_a(\omega)=\int e^{i\omega t}\,d\mu_a(t).
\]

The cosine midpoint windows used here are symmetric, so `R_a` is real and
even. For target coefficient `n` and omitted norm `k>N`, the relevant
frequency is

\[
\omega_{n,k}=\log(k/n).
\]

Choose candidate scales `a=1,...,A` and a finite dangerous set
`D` of pairs `(n,k)`. The response signature of candidate `a` is the vector

\[
v_a=\bigl(R_a(\omega_{n,k})\bigr)_{(n,k)\in D}.
\]

A positive ensemble with weights `alpha_a>=0` and `sum alpha_a=1` has
signature

\[
v_\alpha=\sum_a\alpha_a v_a.
\]

Thus every realizable signature lies in `conv{v_1,...,v_A}`. Arithmetic
multiscale sensing asks whether this convex hull approaches the origin in the
directions that carry the largest divisor-weighted leakage.

The arithmetic weight of a degree-`d` tail norm at exponent `sigma` is

\[
c_k=d_d(k)k^{-\sigma}.
\]

For the selected modes belonging to target `n`, define

\[
L_n(\alpha)=
\sum_{(n,k)\in D}c_k
\left|\sum_a\alpha_aR_a(\omega_{n,k})\right|
+\sum_a\alpha_a u_{n,a},
\]

where `u_{n,a}` is an optional nonnegative remote-tail upper bound for that
component. The remote term is deliberately combined linearly: no unproved
remote cancellation is assumed.

---

## 2. The positive finite minimax theorem

Introduce one variable `z_(n,k)` per dangerous mode and a common target bound
`rho`. Solve

\[
\begin{aligned}
\text{minimize}\quad &\rho,\\
\text{subject to}\quad
&-z_{n,k}\le \sum_a\alpha_aR_a(\omega_{n,k})\le z_{n,k},\\
&\sum_{(n,k)\in D}c_kz_{n,k}
 +\sum_a\alpha_a u_{n,a}\le\rho &&\text{for every selected }n,\\
&\alpha_a\ge0,\quad z_{n,k}\ge0,\quad \sum_a\alpha_a=1.
\end{aligned}
\]

### Theorem — exact solution of the declared finite design problem

If the response values, arithmetic weights, and remote bounds in the displayed
program are treated as fixed real data, every feasible point defines a
positive normalized sensing ensemble and its objective bounds every selected
`L_n`. Conversely, every positive ensemble on the candidate set extends to a
feasible point with `z_(n,k)` equal to the absolute signed responses and
`rho=max_n L_n`. Therefore the linear program's optimum equals

\[
\min_{\alpha\in\Delta_A}\max_n L_n(\alpha).
\]

#### Proof

The two epigraph inequalities imply

\[
z_{n,k}\ge
\left|\sum_a\alpha_aR_a(\omega_{n,k})\right|.
\]

Substitution into the target constraint gives `L_n(alpha)<=rho`. In the other
direction, assign every `z_(n,k)` its realized absolute response and assign
`rho=max_n L_n(alpha)`. All constraints then hold with equality where
appropriate. Minimizing over the simplex proves the identity. Positivity and
normalization follow directly from the simplex constraints. \(\square\)

This theorem proves optimality only for the explicitly declared candidate
scales, dangerous modes, and numerical response data. It is not the recovery
theorem and not a continuum or infinite-tail proof.

---

## 3. Exact nesting theorem

The centered midpoint grid at time `T` and sample count `m` is

\[
x_{T,m,j}=\frac{T}{m}\left(j-\frac{m-1}{2}\right).
\]

Suppose all candidate grids have common spacing `h=T_a/m_a`, and let an outer
grid have sample count `m_*`. If every difference `m_*-m_a` is nonnegative
and even, then

\[
x_{T_a,m_a,j}
=x_{T_*,m_*,j+(m_*-m_a)/2}.
\]

Hence every component is a contiguous central subset of the outer grid. A
positive ensemble can be implemented by adding its component weights at those
outer indices. It uses exactly `m_*` distinct observation times, regardless of
the sum of component sample counts.

For the promoted design,

\[
\frac{510}{2550}=\frac{1780}{8900}=\frac15,
\qquad
\frac{8900-2550}{2}=3175.
\]

The exact dyadic mixing weights are nonnegative and sum to one. Since each
cosine window is itself positive and normalized, the realized 8,900-point
measure is positive and normalized.

---

## 4. Algorithm

The executable pipeline in `arithmetic_multiscale_sensing.py` is:

1. **Detect.** For a baseline outer scale, rank explicitly enumerated terms by
   `d_d(k) k^-sigma |R(log(k/n))|` for each selected target.
2. **Embed.** Evaluate every candidate nested scale on the detected
   log-frequency set to form its signed response signature.
3. **Optimize.** Solve the positive target-minimax epigraph LP. Optional
   componentwise remote upper bounds enter linearly.
4. **Sparsify.** Enumerate small supports, optionally requiring the outer grid,
   and solve the restricted LP on each support. This exposes simple designs
   that a dense numerical optimum can obscure.
5. **Rationalize.** Round the probability vector to a common dyadic
   denominator by a largest-remainder rule, preserving positivity and exact
   normalization.
6. **Audit.** Recompute the complete binary64 discovery consequence, including
   all million finite terms and all Gram rows.
7. **Certify.** Discard the numerical guarantee and independently rebuild the
   signed finite and Gram calculations in Arb, the remote tails in directed
   MPFR plus exact dyadic arithmetic, and the final consequence in exact
   rational arithmetic.

The separation between steps 3 and 7 matters. A floating-point optimizer is a
candidate generator. It never becomes a premise of the formal recovery
claim.

### Rationalization stability

Every normalized positive component satisfies `|R_a(omega)|<=1`. If numerical
weights `alpha` are replaced by rational weights `beta`, then at every
frequency

\[
\left|R_\alpha(\omega)-R_\beta(\omega)\right|
\le\|\alpha-\beta\|_1.
\]

This supplies a quick design-stage perturbation bound. The published result
does not rely on it: the rational weights themselves are the inputs to the
formal checker.

---

## 5. Degree-fourteen search

The declared experiment fixed

```text
degree d             14
recovered norms N    50
Dirichlet exponent   2
explicit truncation  1,000,000
grid spacing         1/5
```

On the ordinary `T=1780,m=8900` baseline, `51/50` contributes 95.66% of
the total contribution of the eight automatically selected target-50 modes.
The next detected ratios were `54/50`, `52/50`, `72/50`, `96/50`, `144/50`,
`56/50`, and `240/50`. Their ordering reflects both the window response and
the degree-fourteen divisor weight; it is not simply an ordering by distance
from one.

Requiring the outer scale and searching every two-scale support with short
times from 300 through 800 in steps of 10 selected `T=510`. The finite-mode
plus remote discovery objective was `1.9675677030755654e-4`, at numerical
weights

\[
(0.0019069987957300665,\ 0.9980930012042699).
\]

The next-ranked short times were 500, 490, 520, and 480. Thus the reported
short scale is the output of the declared sparse minimax search, not an
after-the-fact choice.

The search inspected short times on a ten-unit grid and long times through
1,790. An initial sparse experiment forced exact numerical cancellation of
the two nearest target-50 modes `51/50` and `52/50`. The table records the best
localized complete binary64 consequence found up to selected outer-time
budgets; it is a finite computational scan, not an impossibility theorem.

| outer-time budget | representative support | localized consequence |
|---:|:---|---:|
| 1,700 | `(480,1690,1700)` | `0.52032044` |
| 1,720 | `(490,1450,1720)` | `0.51300979` |
| 1,740 | `(450,1410,1740)` | `0.50916245` |
| 1,750 | `(500,1730,1750)` | `0.50567100` |
| 1,760 | `(500,1710,1760)` | `0.50397222` |
| 1,770 | `(510,1400,1770)` | `0.50274923` |
| 1,780 | `(510,1400,1780)` | `0.49822043` |
| 1,790 | `(510,1780,1790)` | `0.49364049` |

At the first observed crossing, optimization of the complete localized
consequence reduced the middle weight to numerical zero. Dyadic rounding at
16 bits produced

\[
(\alpha_{510},\alpha_{1780})
=\frac1{65536}(125,65411).
\]

The independent binary64 audit of this exact rational candidate gave
approximately `0.49802742`. That margin was sufficient to justify the costly
all-target formal run, but it is not the published endpoint.

An interesting negative result accompanies the simplification: asking for
three scales does not imply that three scales are useful. The convex optimum
may lie on a lower-dimensional face. Here the proposed middle scale vanished,
leaving a two-component measure discovered by a multiscale algorithm.

---

## 6. Formal certificate

The formal computation uses:

- exact unsigned generalized-divisor coefficients through one million;
- Arb enclosure of the signed rational-weight ensemble response before every
  finite absolute value;
- separate directed-MPFR/dyadic remote certificates at `T=510` and `T=1780`;
- conservative positive combination of those remote upper bounds;
- Arb enclosure of every signed ensemble Gram entry;
- exact-rational Neumann and coefficient consequences.

| certified quantity | value |
|:---|---:|
| distinct readings | 8,900 |
| maximum observation time | 1,780 |
| short component | `(510,2550,125/65536)` |
| long component | `(1780,8900,65411/65536)` |
| finite target-50 upper | `3.92302707e-6` |
| combined remote target-50 upper | `1.95245029e-4` |
| maximum complete tail | `5.41332720e-4` at target 1 |
| maximum Gram row defect | `7.55751053e-4` |
| target-50 Gram row | `7.92092183e-5` |
| formal coefficient endpoint | `0.4980274167750795` |

### Theorem — certified arithmetic multiscale recovery

For every degree-fourteen coefficient sequence dominated by `d_14(n)` under
the declared `N=50`, `sigma=2`, and truncation architecture, the exact nested
measure `mu_AMS` has formal coefficient endpoint

\[
U_{\mathrm{AMS}}=0.4980274167750795,
\]

which is strictly below `1/2`. Therefore the first 50 integer coefficients are
recovered exactly by rounding under the deterministic noiseless model.

Artifact hashes:

```text
ensemble end-to-end:
89b316584d9179c13232ad99b9515067fdf67329e6df3db4c48220d6b8c3ff7b

T=510 remote dependency:
c7f86fc51a19355ac882f3ede53d3870ed298eb5e09dc713259b5b5736d46409

T=1780 remote dependency:
d515a57c8484649a7618912b9be08ebf49318cbe240df8cff2ff81e38194a4d7
```

---

## 7. Resource comparison and control

| formally certified design | distinct readings | maximum time | endpoint |
|:---|---:|---:|---:|
| fixed `T=1000` single window | 14,691 | 1,000 | `0.4999975382` |
| fixed-ratio single window | 9,465 | 1,893 | `0.4992815922` |
| hand-designed nested ensemble | 8,950 | 1,790 | `0.4972362699` |
| arithmetic multiscale design | **8,900** | **1,780** | `0.4980274168` |

The new point strictly improves both resource coordinates of the previous
nested measure. It does not dominate the fixed-`T=1000` point, which trades
many more readings for a shorter interval.

The unreweighted single window on the identical `T=1780,m=8900` outer grid has
formal endpoint `0.5959293953409309` and does not certify. Its artifact hash is
`723d3069d31e927dadd5e1eddd28decd9d2a05b2ac3f1bd5d77706c4cc7222aa`.
Thus the new certificate comes from a positive redistribution of existing
readings, not merely from selecting an already-certifying outer window.

---

## 8. What the geometry says

The construction gives a precise, limited realization of the motivating idea
that numerical relationships can expose geometry. Here the geometry is not a
new physical spacetime and not a claim about the foundations of number. It is
the convex geometry of log-frequency response signatures:

\[
\text{nested positive measures}
\longrightarrow
\text{points in a response convex hull}
\longrightarrow
\text{suppressed arithmetic resonances}.
\]

The ratios `k/n` become locations `log(k/n)` in the character group of the
positive reals. Observation windows become Fourier response vectors on those
locations. Positivity restricts design to a convex hull, while exact nesting
turns abstract mixing into a realizable reweighting of one sensor grid. This
is genuine information geometry in a concrete sense: algebraic coefficient
growth, harmonic response, and finite measurement resources meet in one
optimization problem.

---

## 9. Validity boundary

Established:

- a general response-signature formulation for finite dangerous-mode sets;
- an LP theorem exactly solving the declared positive finite minimax problem;
- a sparse-support search and exact dyadic rationalization procedure;
- exact realization of every accepted design on one nested outer grid;
- an automatically inspired degree-fourteen candidate using 8,900 readings;
- a full all-target Arb/MPFR certificate for that rational candidate;
- a same-grid single-window formal control.

Not established:

- global optimality over all times, grids, windows, or positive measures;
- impossibility below 8,900 readings or time 1,780;
- that a fixed finite dangerous set controls the infinite tail without the
  independent full audit;
- a formal advantage under sensor noise;
- transfer of the resource improvement to other degrees or target counts;
- any consequence for zeta zeros, the Riemann hypothesis, or fundamental
  physics;
- literature priority without independent specialist review.

---

## 10. Reproduction

Run the discovery algorithm:

```bash
python arithmetic_multiscale_sensing.py
```

Rebuild the two remote dependencies with their recorded parameters, then
rebuild or check the all-target certificate:

```bash
python verify_multiscale_certificate.py --processes 8
```

The formal artifacts are:

```text
certificates/arithmetic_sensing_v_multiscale_T510_remote.json
certificates/arithmetic_sensing_v_multiscale_T1780_remote.json
certificates/arithmetic_sensing_v_multiscale_end_to_end.json
certificates/arithmetic_sensing_v_multiscale_T1780_single_end_to_end.json
```

Run the focused tests with:

```bash
python -m unittest -v test_arithmetic_multiscale_sensing.py
```

---

## 11. Next research targets

1. **Dual lower bounds.** Rationalize the finite LP dual to certify that no
   declared candidate support beats a stated dangerous-mode objective.
2. **Adaptive column generation.** Alternate between designing a measure and
   adding the worst newly exposed `(n,k)` mode, rather than fixing the
   dangerous set once.
3. **Robust LP coefficients.** Replace binary64 response entries by intervals
   and solve a robust rational program whose finite optimality statement is
   itself formal.
4. **Noise-aware design.** Add variance or effective-sample constraints and
   prove a rounding-failure comparison under a declared sensor-noise model.
5. **Degree and target phase diagram.** Test whether the selected scale ratios
   persist as `d`, `N`, and `sigma` vary.
6. **Continuum design limit.** Study the convex hull generated by all central
   subwindow lengths and derive analytic lower or approximation bounds.

The most natural next step is adaptive mode-row generation with a rational
dual certificate. It would close the remaining gap between a useful mode
detector and a finite design theorem that certifies its own search domain.

That continuation is carried out in
`ARITHMETIC_SENSING_V_ADAPTIVE_EXCHANGE.md`.
