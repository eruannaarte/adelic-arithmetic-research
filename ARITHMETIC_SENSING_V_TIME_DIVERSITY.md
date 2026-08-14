# Arithmetic Sensing V — Resonance-Aware Time Diversity

## A nested two-window certificate for degree fourteen

- **Research lead, theorem, computation, and manuscript:** Codex (OpenAI)
- **Originating question and research environment:** TGN's human founder
- **Status:** formal time-diversity milestone complete
- **Date:** 13 August 2026
- **Parent manuscript:** `ARITHMETIC_SENSING_V_DEGREE_14_RESOURCE_LAW.md`

## Abstract

The degree-fourteen resource law showed that proportional increases in sample
count and observation time can initially make deterministic arithmetic recovery
worse. This paper identifies the source of the largest peaks and turns the
diagnosis into a sensing construction.

At target 50 and observation time `T=1100`, the two omitted modes `51/50` and
`52/50` contribute 99.10% of the finite million-term leakage. At `T=1200`, they
contribute 99.37%. The peak is therefore a localized arithmetic resonance, not
a diffuse numerical effect.

We introduce a positive centered time ensemble. Its Fourier kernel is a convex
combination of signed centered window responses, so cancellation can occur
before absolute values are taken. For degree fourteen, choose

\[
\mu=
\frac{7}{4096}\mu_{500,2500}
+\frac{4089}{4096}\mu_{1790,8950}.
\]

Both midpoint grids have exact spacing `1/5`, and the 2,500-point grid is the
contiguous subset with outer indices 3,225 through 5,724. Thus the ensemble is
a positive reweighting of only 8,950 distinct observations over maximum time
1,790; it does not require 11,450 separate readings.

An end-to-end artifact combines:

- exact generalized-divisor coefficients through one million;
- Arb evaluation of every signed two-window finite response;
- two independently reconstructible directed-MPFR remote certificates;
- Arb enclosure of every signed ensemble Gram row;
- an exact-rational Neumann-series consequence.

The outward formal endpoint is

\[
U_{\mathrm{ens}}=0.4972362698851084<\frac12.
\]

Consequently the nested ensemble certifies deterministic integer recovery at
degree fourteen. Relative to the previous fixed-ratio single-window frontier,
it reduces both the distinct reading count, from 9,465 to 8,950, and the
maximum observation time, from 1,893 to 1,790. The construction does not prove
global optimality, and its noise behavior remains a separate question.

---

## 1. The resonance is carried by neighboring integer ratios

For a midpoint cosine window, write its real centered response as

\[
R_{T,m}(\omega)
=e^{-iT\omega/2}K_{T,m}(\omega).
\]

The exact common-numerator formula used by the Arb checker makes
`R_{T,m}` real and even. At target `n=50`, the explicitly enumerated finite
tail is

\[
F_{50}(T,m)=
\sum_{k=51}^{10^6}d_{14}(k)k^{-2}
\left|R_{T,m}(\log(k/50))\right|.
\]

At the two large peaks from the resource-law scan, its leading terms are:

| `T,m` | finite total | `k=51` contribution | `k=52` contribution | combined share |
|:---|---:|---:|---:|---:|
| `1100,5500` | `5.96386001e-4` | `4.272016e-4` | `1.637874e-4` | `99.10%` |
| `1200,6000` | `9.88096396e-4` | `7.014758e-4` | `2.804393e-4` | `99.37%` |

The relevant phase coordinate for the dominant mode is

\[
\theta_{51}(T)=\frac{T\log(51/50)}{2\pi}.
\]

It equals approximately `3.466855` cycles at `T=1100` and `3.782023`
cycles at `T=1200`. Because the cosine taper is not a rectangular window,
the dangerous set is determined by the lobes of the complete response
`R_{T,5T}`, not merely by whether this number is close to an integer.

This gives a falsifiable predictor: a resource peak should be attributable to
specific ratios whose exact log-frequencies simultaneously land in large
response lobes. The million-term decomposition confirms that prediction here.

---

## 2. Positive centered time ensembles

Let `mu_a` be normalized positive sampling measures, all centered at the same
time origin, and let `alpha_a>0` with `sum alpha_a=1`. Define

\[
\mu=\sum_a\alpha_a\mu_a.
\]

This is again a positive probability measure. If every component is symmetric,
its Fourier kernel is real after centering:

\[
R_\mu(\omega)=\sum_a\alpha_aR_a(\omega).
\]

The order of operations is decisive:

\[
\left|\sum_a\alpha_aR_a(\omega)\right|
\quad\text{can be much smaller than}\quad
\sum_a\alpha_a|R_a(\omega)|.
\]

The first expression is used for every explicitly enumerated finite term and
for every Gram entry. The second, conservative expression is used only for the
remote tail, where separate MPFR upper certificates are combined by the
triangle inequality.

### Ensemble recovery theorem

Let

\[
G_{ij}=R_\mu(\log(i/j)),
\qquad
r_i=\sum_{j\ne i}|G_{ij}|,
\qquad
q=\max_i r_i<1.
\]

For complete finite-plus-remote tail bounds `eta_i`, the same inverse-free
argument as in the end-to-end paper gives

\[
|\widehat a_i-a_i|
\le i^2\left[
\eta_i+r_i\frac{\max_j\eta_j}{1-q}
\right].
\]

Hence

\[
\max_i i^2\left[
\eta_i+r_i\frac{\max_j\eta_j}{1-q}
\right]<\frac12
\]

certifies exact integer recovery by rounding.

Nothing in the proof requires a single observation interval. It requires one
positive normalized measure, a certified tail vector, and a certified Gram
row defect. A centered positive ensemble supplies exactly those objects.

### Why centering is structural

For a window written on `[0,T]`, the kernel contains the phase
`exp(i T omega/2)`. Different values of `T` carry different phases, so blindly
averaging uncentered kernels would define a different design. Here every grid
is centered on the common origin. The physical sample times lie symmetrically
in `[-T/2,T/2]`, and the signed real responses combine exactly as stated.

---

## 3. Designing against `51/50`

For the short and long components of the published design,

\[
R_{500,2500}(\log(51/50))\approx 0.2908337078,
\]

while

\[
R_{1790,8950}(\log(51/50))\approx-0.0005004378.
\]

Their signs are opposite. The weight that cancels this one mode exactly is

\[
\alpha_*
=\frac{-R_{1790,8950}}
{R_{500,2500}-R_{1790,8950}}
\approx0.0017177450.
\]

The nearby exact dyadic choice

\[
\alpha=\frac7{4096}\approx0.0017089844
\]

reduces the magnitude of that response to approximately
`2.55228e-6`, a factor of about 196 relative to the long component alone.

This is not a single-mode proof. Once `51/50` is suppressed, `52/50` becomes
the largest explicit target-50 contribution. The formal artifact evaluates
all norms from 51 through one million and all targets from 1 through 50, so no
unexamined-mode assumption enters the theorem.

---

## 4. The short grid costs no additional observations

The centered midpoint grid is

\[
x_{T,m,j}=\frac{T}{m}
\left(j-\frac{m-1}{2}\right),
\qquad 0\le j<m.
\]

For both published components,

\[
\frac{500}{2500}=\frac{1790}{8950}=\frac15.
\]

Moreover

\[
\frac{8950-2500}{2}=3225.
\]

Therefore

\[
x_{500,2500,j}=x_{1790,8950,j+3225}
\]

for every short-grid index `j`. The short grid is exactly the central subset
of the long grid.

Writing `w_L` and `w_S` for their positive cosine-window weights, the ensemble
can be realized on the long grid by

\[
w_k=\frac{4089}{4096}w_{L,k}
+\mathbf 1_{3225\le k\le5724}
\frac7{4096}w_{S,k-3225}.
\]

Every weight is nonnegative and the weights sum to one. Numerically, the
effective sample count `1/sum w_k^2` is approximately `4934.03`, compared with
`4939.70` for the original long cosine window. Thus the deterministic gain is
not purchased by a large concentration of statistical weight, although a
formal noisy-recovery analysis has not yet been performed.

---

## 5. Formal certificate

The published construction has:

| quantity | value |
|:---|---:|
| degree | 14 |
| recovered coefficients | 50 |
| Dirichlet exponent | 2 |
| explicit truncation | `10^6` |
| distinct readings | 8,950 |
| maximum observation time | 1,790 |
| short component | `(T,m,alpha)=(500,2500,7/4096)` |
| long component | `(T,m,alpha)=(1790,8950,4089/4096)` |

The formal computation gives approximately:

| certified quantity | value |
|:---|---:|
| finite target-50 upper | `4.60884955e-6` |
| combined remote target-50 upper | `1.94238434e-4` |
| maximum complete tail | `5.40326569e-4` at target 1 |
| maximum Gram row defect | `7.39146843e-4` |
| target-50 Gram row | `8.73355265e-5` |
| coefficient endpoint | `0.4972362698851084` |

### Theorem — certified degree-fourteen nested time diversity

For every degree-fourteen coefficient sequence dominated by `d_14(n)` under
the declared `N=50`, `sigma=2`, and truncation architecture, the published
nested positive ensemble has formal coefficient endpoint

\[
U_{\mathrm{ens}}=0.4972362698851084<\frac12.
\]

Therefore its deterministic least-squares reconstruction recovers the first
50 integer coefficients exactly by rounding.

The end-to-end certificate hash and dependency hashes are recorded in the
artifact itself and pinned by the test suite.

```text
ensemble end-to-end:
1cc643118a3aad8e31e621c0c913742975723b47263199f1e0aeb598d8d1036e

short remote dependency:
d21502db2d2418c049d64e4d0dbd2ce733293ee834e32fe82c401c8c50d87ec0

long remote dependency:
470cf6021d2320ce175d449875de61037922ab9c884474aa3446212985abcbb7
```

---

## 6. Resource comparison

| certified design | distinct readings | maximum time | formal endpoint |
|:---|---:|---:|---:|
| fixed `T=1000` single window | 14,691 | 1,000 | `0.4999975382` |
| fixed ratio `m/T=5` single window | 9,465 | 1,893 | `0.4992815922` |
| nested time ensemble | **8,950** | **1,790** | `0.4972362699` |

The ensemble does not dominate the fixed-`T=1000` point: it uses a longer
maximum interval in exchange for many fewer readings. It does strictly improve
both coordinates of the previous ratio-five frontier.

The ordinary long component at `T=1790,m=8950`, with no central reweighting,
has formal endpoint `0.5888194725646674` and does not certify. The same 8,950
observations become certifying only after resonance-aware positive reweighting.
This is the sense in which the result is resource architecture, not merely
resource addition. The control artifact has formal hash
`215ca087bc9e29de1b81cbfa8ee6171fb4dfadb2a2e7dbc3b61e6f0b9d57e7f2`.

---

## 7. Formal architecture and reproduction

The remote dependencies are:

```text
certificates/arithmetic_sensing_v_time_ensemble_T500_remote.json
certificates/arithmetic_sensing_v_time_ensemble_T1790_remote.json
```

The composed certificate is:

```text
certificates/arithmetic_sensing_v_time_ensemble_end_to_end.json
```

The same-grid single-window control is:

```text
certificates/arithmetic_sensing_v_time_ensemble_T1790_single_end_to_end.json
```

Run the localized exploratory report with:

```bash
python time_ensemble_design.py
```

Recompute all 50 hybrid targets with:

```bash
python time_ensemble_design.py --all-targets
```

Rebuild the two MPFR dependencies with `verify_mellin_certificate.py`, using
their recorded times, sample counts, cancellation method, and explicit bin
count. Then rebuild or independently check the final artifact with:

```bash
python verify_time_ensemble_certificate.py --processes 8
```

The final command is intentionally expensive: it evaluates approximately one
hundred million component responses with Arb before taking absolute values.

---

## 8. Validity boundary

Established:

- the two nearest omitted ratios explain more than 99% of the two largest
  finite resonance peaks examined;
- a general positive centered-ensemble recovery theorem;
- exact nesting of the short grid inside the long grid;
- full Arb cancellation across both finite kernels and Gram entries;
- conservative MPFR remote composition without assuming remote cancellation;
- formal degree-fourteen recovery with 8,950 distinct samples and maximum time
  1,790.

Not established:

- global optimality of the time pair or mixing weight;
- impossibility for smaller resource pairs;
- a closed formula predicting every resonance peak;
- a noise-robust advantage over optimized single-window weights;
- the same improvement for other degrees, truncations, or target counts;
- any implication for zeta zeros or physical theories.

---

## 9. Next research target

This milestone shows that a tiny positive central reweighting can erase a
specific arithmetic lobe without collecting new data. The next target is a
general resonance-design theorem:

1. construct a finite matrix of dangerous log-ratios and candidate nested
   subwindows;
2. solve a rational positive minimax problem for their signed responses;
3. certify continuum positivity and all remote aliases jointly;
4. determine whether three nested scales can suppress both `51/50` and
   `52/50` while increasing the formal margin;
5. extend the theorem to weighted sensor noise and compare effective sample
   complexity rather than observation count alone.

That would turn the present hand-designed notch into an algorithm for
arithmetic multiscale sensing.
