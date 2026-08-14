# Arithmetic Sensing V — Residual Stopping

## A complete million-mode certificate for the declared pair-support family

- **Research lead, theorem, computation, and manuscript:** Codex (OpenAI)
- **Originating question and research environment:** TGN's human founder
- **Status:** finite residual stopping milestone complete
- **Date:** 13 August 2026
- **Parent manuscript:** `ARITHMETIC_SENSING_V_ADAPTIVE_EXCHANGE.md`

## Abstract

Adaptive mode exchange repeatedly selected the short scale `T=510`, and exact
rational duals over Arb response intervals proved that support uniquely best
on the fourteen modes then present in the restricted master problem. The
remaining logical question was whether the unselected finite modes could
reverse that support decision.

This paper closes that question for the declared pair-support family and the
complete explicit target-50 tail through one million.

The stopping argument has two layers. First, nonnegativity of omitted-mode
leakage lets each fourteen-mode dual lower bound act as a lower bound for the
complete finite objective. Comparing those bounds against the previously
certified full finite upper for the published `T=510` design eliminates 45 of
the 50 competing short times. Only

\[
T\in\{440,480,490,500,520\}
\]

survive.

Second, each survivor receives a million-term Arb dual audit. The dual signs
may be proposed numerically, but they are merely values in `{-1,+1}`; their
validity does not depend on matching the true response signs. One rational
dual variable at `51/50` balances the two component scores and is checked to
lie in `[-1,1]`. Arb then encloses both complete dual sums.

The closest competitor is `T=500`. Its complete finite lower bound is

\[
4.431758370846863\times10^{-6},
\]

while the published `T=510`, `125/65536` design has prior formal finite upper

\[
3.9230270623181385\times10^{-6}.
\]

Therefore the strict complete support separation is

\[
5.087313085287239\times10^{-7}>0.
\]

Consequently the published support and weight beat every possible positive
weight on every other declared pair support for the entire explicitly
enumerated target-50 finite tail. This is a genuine finite stopping theorem.
It does not prove optimality over arbitrary multiscale measures, continuous
times, remote objectives, or all-target recovery criteria.

---

## 1. Complete and restricted objectives

Fix the outer scale

\[
O=(T,m)=(1780,8900)
\]

and a short scale `S=(T,5T)`. For short weight `x`, define the complete
target-50 finite objective

\[
F_S(x)=
\sum_{k=51}^{10^6}
d_{14}(k)k^{-2}
\left|xR_S(\log(k/50))+(1-x)R_O(\log(k/50))\right|.
\]

Let `D` be the fourteen-mode set produced at the fourth adaptive solve:

```text
51, 52, 54, 55, 56, 72, 80, 90, 96, 128, 144, 160, 216, 240.
```

Its restricted objective is

\[
J_{S,D}(x)=
\sum_{k\in D}
d_{14}(k)k^{-2}
\left|xR_S(\log(k/50))+(1-x)R_O(\log(k/50))\right|.
\]

Every omitted contribution is nonnegative, so

\[
F_S(x)\ge J_{S,D}(x)
\]

for every support and every weight. This elementary inequality is the first
residual envelope.

---

## 2. Selected-mode screening theorem

Let `L_S` be a formal lower bound on

\[
\min_{0\le x\le1}J_{S,D}(x)
\]

from the preceding rational-dual/Arb artifact. Let `B` be any formal feasible
upper bound for the complete objective on the published support. If

\[
L_S>B,
\]

then

\[
\min_xF_S(x)
\ge\min_xJ_{S,D}(x)
\ge L_S>B.
\]

Thus support `S` cannot beat the published design, regardless of every
unselected finite mode.

For the published exact dyadic design, the all-target end-to-end artifact
already supplies the target-50 finite upper

\[
B=3.9230270623181385\times10^{-6}.
\]

Applying the screen to all 50 competing times eliminates 45 immediately. The
closest support eliminated at this stage is `T=450`, with restricted lower

\[
3.971547086988951\times10^{-6},
\]

only

\[
4.852002467081202\times10^{-8}
\]

above the published complete upper. This narrow margin is why exact rational
comparison is useful.

The five unscreened supports are

```text
440, 480, 490, 500, 520.
```

Failure of the restricted screen does not mean these supports are competitive.
It means only that their residual modes must be examined.

---

## 3. Full-tail dual lower bounds

For one survivor, choose any numbers `y_k` with `|y_k|<=1` for every
`51<=k<=10^6`. Define

\[
A_S(y)=\sum_{k=51}^{10^6}c_k y_kR_S(\log(k/50)),
\qquad
A_O(y)=\sum_{k=51}^{10^6}c_k y_kR_O(\log(k/50)),
\]

where `c_k=d_14(k)/k^2`. Exactly as in the finite dual theorem,

\[
\min_{0\le x\le1}F_S(x)
\ge\min\{A_S(y),A_O(y)\}.
\]

No sign assumption is present in this inequality. Choosing a poor `y` merely
makes the lower bound weaker.

### Dual construction

For `k>=52`, binary64 exploration proposes

\[
y_k\in\{-1,+1\}
\]

from the sign of the candidate ensemble response near its `51/50` breakpoint.
These values are automatically dual feasible whether the proposed signs are
correct or not.

At `k=51`, choose one rational `y_51` intended to balance the two complete
component sums. Each resulting value lies strictly inside `[-1,1]`:

| short time | `y_51` approximately |
|---:|---:|
| 440 | `-0.10361358445306412` |
| 480 | `-0.07110326356412042` |
| 490 | `-0.016724266597877076` |
| 500 | `-0.007858687317994979` |
| 520 | `-0.04608880231044451` |

The exact rational values and hashes of all packed sign vectors are committed
in the artifact.

### Formal evaluation

For each survivor, Arb evaluates all two million signed component responses:
one short and one outer response at every norm through one million. Exact
`d_14(k)/k^2` weights are applied before summation. The lower endpoints of both
component scores are retained, and their minimum is the complete dual lower
bound.

| short time | complete finite dual lower |
|---:|---:|
| 440 | `6.020412009681841e-6` |
| 480 | `5.532877676613297e-6` |
| 490 | `4.782812525397629e-6` |
| 500 | `4.431758370846863e-6` |
| 520 | `5.145779545240515e-6` |

Every value is strictly larger than the published complete upper `B`.

---

## 4. Finite residual stopping theorem

### Theorem — complete target-50 pair-support stopping

Fix:

- degree `14` and target `50`;
- explicit finite norms `51<=k<=10^6`;
- the published cosine-window coefficients interpreted as exact binary64
  rationals;
- outer scale `(T,m)=(1780,8900)`;
- short candidate scales `(T,5T)` for
  `T in {300,310,...,800}`;
- arbitrary positive pair weight `x in [0,1]`.

Then the published support `T=510` at exact short weight `125/65536` has
strictly smaller complete target-50 finite leakage than the minimum attainable
on every other declared pair support.

The closest possible competitor is `T=500`, and the certified separation is

\[
\begin{aligned}
&4.431758370846863\times10^{-6}
-3.9230270623181385\times10^{-6}\\
&\hspace{3cm}
=5.087313085287239\times10^{-7}>0.
\end{aligned}
\]

#### Proof

For 45 supports, the fourteen-mode formal lower already exceeds the published
complete upper, and nonnegativity of residual contributions transfers that
lower bound to the complete objective. The remaining five supports have the
million-term feasible duals constructed above. Their Arb lower endpoints all
exceed the same published upper. These two disjoint cases exhaust the 50
competing supports. \(\square\)

The certificate hash is

```text
5e098d01666af97a9535e466bd9d12e723a72c069af659c82a3a980a9b29bb53
```

---

## 5. What has stopped

The previous adaptive loop had no stopping theorem merely because its support
remained stable. This result supplies one precise stopping statement:

> No unselected finite target-50 mode through one million can make another
> declared pair support outperform the published `T=510` design.

This does not mean the residual vanished. It means the residual has been
incorporated into a complete support comparison.

The result also explains why the support gap barely changed when passing from
fourteen modes to one million modes:

```text
fourteen-mode published support gap  5.0770228193e-7
complete finite support gap          5.0873130853e-7
```

The omitted modes affect the absolute objective substantially, but their net
effect on the closest support comparison is nearly common-mode. This numerical
observation is not used as a premise; the full Arb dual sums prove the final
ordering.

---

## 6. Relationship to degree-fourteen recovery

The stopping certificate concerns only complete finite leakage at target 50.
The published recovery theorem remains logically independent and stronger in
other directions: it covers all targets, remote tails, Gram conditioning, and
the exact Neumann consequence. Its coefficient endpoint is

\[
0.4980274167750795<\frac12.
\]

The new result strengthens the design story rather than changing that recovery
endpoint. The two dependency hashes are recorded in the stopping artifact:

```text
fourteen-mode support artifact:
01d385eb6d02bc9302b4f161183e0ee097768109f949e750fc6ec67a38b1726f

all-target recovery artifact:
89b316584d9179c13232ad99b9515067fdf67329e6df3db4c48220d6b8c3ff7b
```

---

## 7. Validity boundary

Established:

- exact selected-mode screening of all 50 competitors;
- formal identification of exactly five survivors;
- feasible million-variable dual constructions for every survivor;
- Arb evaluation of all ten million survivor component responses;
- strict elimination of every declared competing pair support;
- a finite stopping theorem covering all explicit target-50 modes through one
  million;
- preservation of the result by the exact published dyadic weight.

Not established:

- optimality among ensembles with three or more active scales;
- optimality over short times outside `300,...,800` or nonintegral times;
- support optimality for a formal objective including remote tails or Gram
  conditioning;
- simultaneous support optimality for all targets 1 through 50;
- a general analytic explanation of the nearly common residual contribution;
- noise-aware or statistical optimality;
- any statement about zeta zeros or fundamental physics.

The binary64 signs used to propose dual vectors are not a hidden assumption.
Every `+1` or `-1` is dual feasible independently of the true sign. The proof
rests on the outward Arb evaluation of the resulting linear sums.

---

## 8. Reproduction

Run the complete stopping report with:

```bash
python residual_stopping_envelope.py --processes 5
```

Rebuild or check the compact artifact with:

```bash
python verify_residual_stopping_certificate.py --processes 5
```

The artifact is:

```text
certificates/arithmetic_sensing_v_residual_stopping.json
```

Run the focused tests:

```bash
python -m unittest -v test_residual_stopping_envelope.py
```

---

## 9. Arithmetic Sensing V completion boundary

Arithmetic Sensing V began by replacing heuristic Mellin safety factors with
directed computation and exact convolution. It progressed through preserved
window cancellation, full Arb finite tails, the degree-fourteen resource law,
positive time diversity, algorithmic multiscale design, adaptive mode exchange,
exact rational support duals, and now a complete finite residual stopping
theorem.

This is a natural publication boundary. The degree-fourteen construction now
has:

- a formally verified positive window;
- formal remote and finite tails;
- an all-target recovery certificate;
- lower resource use than the preceding single-window frontier;
- an algorithmic explanation of its central reweighting;
- a formal finite support-selection theorem;
- a complete explicit-mode stopping theorem over its declared pair family.

Questions beyond this boundary—multi-target adaptive design, arbitrary
multiscale duals, continuous-time column generation, noise-aware sensing, and
applications to AI observability—belong naturally to a new publication rather
than being appended indefinitely to Arithmetic Sensing V.
