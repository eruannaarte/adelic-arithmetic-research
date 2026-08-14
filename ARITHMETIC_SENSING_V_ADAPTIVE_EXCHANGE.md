# Arithmetic Sensing V — Adaptive Mode Exchange and Dual Geometry

## Exact support selection on an Arb-enclosed response polytope

- **Research lead, theorem, computation, and manuscript:** Codex (OpenAI)
- **Originating question and research environment:** TGN's human founder
- **Status:** finite support-optimality milestone complete
- **Date:** 13 August 2026
- **Parent manuscript:** `ARITHMETIC_SENSING_V_MULTISCALE.md`

## Abstract

Arithmetic multiscale sensing selected a small central reweighting that turns
8,900 fixed observations from a failing degree-fourteen sensor into a formally
certifying one. Its search began from a finite list of dangerous arithmetic
modes. This paper asks two narrower questions:

1. Does the selected scale survive when the design itself exposes previously
   omitted modes?
2. Can the scale choice be proved optimal over its declared finite search
   family without trusting a floating-point optimizer?

We introduce adaptive mode exchange. Beginning only with `51/50` and `52/50`,
the algorithm alternates between positive two-scale design and a complete
million-term target-50 audit. Each iteration adds the four omitted modes with
largest realized contribution. Over four solves the selected short scale and
weight remain unchanged:

\[
T_S=510,
\qquad
\alpha_S\approx0.0019069987957300665.
\]

The exposed finite set grows from two modes to fourteen. The next batch is
reported rather than silently discarded.

For the final fourteen-mode problem, we derive an exact rational dual for each
two-scale support. Every signed response is independently enclosed by a
192-bit Arb interval. Weakening the rational dual across those intervals gives
a rigorous lower bound for the actual transcendental response problem. The
candidate family consists of all 51 short times from 300 through 800 in steps
of 10, each paired with the fixed outer scale `T=1780`.

The result is a strict support certificate:

| quantity | rigorous value |
|:---|---:|
| winning short time | `510` |
| winner selected-mode upper | `1.8370133525992209e-6` |
| runner-up short time | `500` |
| runner-up selected-mode lower | `2.352084113783623e-6` |
| optimized support separation | `5.150707611844021e-7` |
| published `125/65536` upper | `1.8443818318570255e-6` |
| published-weight separation | `5.077022819265975e-7` |

Thus even the simple published dyadic weight at `T=510` has smaller selected
finite leakage than the best possible weight on every competing declared pair
support. This is not a global optimality theorem, a stopping certificate for
the adaptive exchange, or a replacement for the prior all-target recovery
artifact. It formally explains one design decision inside that independently
certified construction.

---

## 1. A terminology correction

The initial research plan described adding newly dangerous `(n,k)` modes as
“adaptive column generation.” In standard linear-programming terminology,
that operation adds constraints or objective epigraph terms: it is **row
generation**, also called constraint or cutting-plane generation. Candidate
scales are the columns. The parent manuscript has been corrected accordingly.

This paper therefore uses **adaptive mode exchange** for the implemented loop:

\[
\text{restricted mode set}
\longrightarrow
\text{positive design}
\longrightarrow
\text{complete audit}
\longrightarrow
\text{new mode rows}.
\]

True scale-column generation remains a later problem. It would require a
reduced-cost oracle over a large or continuous family of observation times.

---

## 2. The finite pair-support problem

Fix a target `n`, a finite mode set `D`, an outer centered window `O`, and one
short candidate `S`. Write

\[
r_{a,k}=R_a(\log(k/n)),
\qquad
c_k=d_{14}(k)k^{-2}.
\]

For short weight `x` define

\[
J_S(x)=
\sum_{k\in D}c_k
\left|x r_{S,k}+(1-x)r_{O,k}\right|,
\qquad 0\le x\le1.
\]

This section deliberately excludes remote tails, Gram terms, other targets,
and unselected finite modes. It asks only which declared short support best
suppresses the selected target-50 modes when paired with the fixed outer grid.

Because `J_S` is convex and piecewise linear, an optimum occurs at an endpoint
or at a zero of one affine response:

\[
x=-\frac{r_{O,k}}{r_{S,k}-r_{O,k}}.
\]

When all response data are rational, enumerating these breakpoints solves the
primal problem exactly.

---

## 3. Exact rational dual certificate

Use the elementary identity

\[
|q|=\max_{|y|\le1}yq.
\]

For any vector `y=(y_k)` with `|y_k|<=1`,

\[
\begin{aligned}
J_S(x)
&\ge
\sum_{k\in D}c_k y_k
\left[xr_{S,k}+(1-x)r_{O,k}\right]\\
&=x A_S(y)+(1-x)A_O(y),
\end{aligned}
\]

where

\[
A_a(y)=\sum_{k\in D}c_k y_k r_{a,k}.
\]

Taking the minimum over `x` gives the dual lower bound

\[
\min_{0\le x\le1}J_S(x)
\ge
\min\{A_S(y),A_O(y)\}.
\]

### Theorem — exact pair-support duality

Let `x_*` minimize the rational piecewise-linear objective. For every nonzero
realized response choose

\[
y_k=\operatorname{sgn}
\left(x_*r_{S,k}+(1-x_*)r_{O,k}\right).
\]

At zero responses choose `y_k` in `[-1,1]` so that zero belongs to the
subgradient of `J_S` at `x_*`, with the corresponding one-sided condition at
an endpoint. Then

\[
J_S(x_*)=\min\{A_S(y),A_O(y)\}.
\]

Consequently `x_*` and `y` are matching exact rational primal and dual
certificates of optimality.

#### Proof

For nonzero responses, the chosen sign makes `y_k q_k=|q_k|`. At a zero
response equality holds for every admissible `y_k`. Therefore the dual affine
minorant equals the primal objective at `x_*`. The subgradient choice makes
the affine minorant constant for an interior optimum, nondecreasing from a
left-endpoint optimum, or nonincreasing toward a right-endpoint optimum. Its
minimum on `[0,1]` is therefore attained at `x_*` and equals the primal value.
Weak duality supplies the opposite inequality. \(\square\)

The checker constructs the free zero-response dual variables using exact
fractions and verifies feasibility, equality, and every stored objective from
scratch.

---

## 4. From rational midpoints to rigorous transcendental responses

The true response values contain logarithms and trigonometric functions, so
they are not rational. For every candidate scale and selected mode, Arb gives
exact dyadic endpoints

\[
r_{a,k}\in[\ell_{a,k},u_{a,k}].
\]

The window coefficients are interpreted as the exact binary64 rationals used
by the end-to-end formal checker. No binary64 transcendental evaluation enters
this interval layer.

For a rational dual variable `y_k`, define

\[
L_a(y)=\sum_{k\in D}c_k
\min\{y_k\ell_{a,k},y_k u_{a,k}\}.
\]

For every realization inside the Arb intervals and every `x in [0,1]`,

\[
J_S(x)
\ge xL_S(y)+(1-x)L_O(y)
\ge\min\{L_S(y),L_O(y)\}.
\]

This is a rigorous lower bound for the best possible weight on that pair
support.

Conversely, at any exact rational `x`, positive interval combination gives

\[
q_k(x)\in
\left[
x\ell_{S,k}+(1-x)\ell_{O,k},
xu_{S,k}+(1-x)u_{O,k}
\right].
\]

Taking the larger endpoint magnitude gives a rigorous primal upper bound. If
one support's feasible upper bound is smaller than every other support's dual
lower bound, that support is uniquely optimal over the declared family even
though its response values are transcendental.

---

## 5. Adaptive mode-exchange experiment

The discovery layer fixes:

```text
degree                     14
target                     50
explicit audit             k=51,...,1,000,000
outer scale                (T,m)=(1780,8900)
short candidates           T=300,310,...,800 with m=5T
initial modes              51/50 and 52/50
modes added per iteration  4
```

Each restricted solve includes the binary64 cancellation-aware remote proxy.
The complete audit column below includes all one million finite terms plus the
same remote proxy. It is a discovery diagnostic, not the formal recovery
endpoint.

| iteration | modes in solve | added after audit | selected short time | short weight | restricted objective | complete target-50 tail |
|---:|---:|:---|---:|---:|---:|---:|
| 0 | 2 | `54,72,96,144` | 510 | `0.0019069987957300665` | `1.9537692578e-4` | `1.9916053071e-4` |
| 1 | 6 | `56,240,216,80` | 510 | `0.0019069987957300665` | `1.9659443351e-4` | `1.9916053071e-4` |
| 2 | 10 | `55,128,160,90` | 510 | `0.0019069987957300665` | `1.9687293895e-4` | `1.9916053071e-4` |
| 3 | 14 | `192,384,576,108` | 510 | `0.0019069987957300665` | `1.9708191898e-4` | `1.9916053071e-4` |

The fourteen modes present in the final solve are

```text
51, 52, 54, 55, 56, 72, 80, 90, 96, 128, 144, 160, 216, 240.
```

The newly exposed fourth batch is not included retroactively in the
fourteen-mode support theorem. It is published as the next exchange input.
Support stability across four iterations is strong evidence that the nearest
mode `51/50` fixes the optimal notch location, but it is not a termination
proof.

---

## 6. Formal support frontier

For each of the 51 declared short times, the checker:

1. computes every selected response as a 192-bit Arb interval;
2. uses exact `d_14(k)/k^2` arithmetic weights;
3. solves the interval-midpoint problem by exact rational breakpoint
   enumeration;
4. constructs a matching exact rational dual vector;
5. weakens that vector to a valid lower bound over the complete Arb box;
6. computes a feasible interval upper bound for the pair;
7. compares the winning upper bound against all 50 competing lower bounds.

The midpoint optimizer for `T=510` is the exact rational number

\[
\frac{
422204939324553957083884186939767230386777664510693232917
}{
221397590952824935224211945906309855141371488519057291865173
}
\approx0.0019069987957299713.
\]

Its robust lower-to-upper interval has width approximately
`5.85201e-57`. The runner-up is `T=500`, whose rigorous lower bound is
`2.352084113783623e-6`. The optimized `T=510` feasible upper is
`1.8370133525992209e-6`, leaving separation

\[
5.150707611844021\times10^{-7}>0.
\]

More importantly, the simple weight actually used in the recovery theorem,

\[
\alpha_S=\frac{125}{65536},
\]

has selected-mode upper bound `1.8443818318570255e-6`. It remains below the
best possible lower bound for every competing declared support by

\[
5.077022819265975\times10^{-7}>0.
\]

### Theorem — unique declared pair-support selection

For target 50, the stated fourteen-mode set, the fixed outer window
`(T,m)=(1780,8900)`, the 51 short windows `(T,5T)` with
`T in {300,310,...,800}`, and the published exact window coefficients,
the support with short time `T=510` is the unique minimizer of selected finite
leakage. Moreover, the published dyadic weight `125/65536` on that support
already has lower leakage than the optimally weighted response on every other
declared pair support.

This theorem is certified by the Arb interval boxes and exact rational duals
stored under hash

```text
01d385eb6d02bc9302b4f161183e0ee097768109f949e750fc6ec67a38b1726f
```

---

## 7. Relationship to the recovery theorem

The present certificate explains why `T=510` was selected. It does not prove
degree-fourteen recovery. That logically independent theorem is the preceding
all-target artifact:

```text
arithmetic_sensing_v_multiscale_end_to_end.json
89b316584d9179c13232ad99b9515067fdf67329e6df3db4c48220d6b8c3ff7b
```

That artifact includes all targets 1 through 50, every finite norm through one
million, both remote dependencies, all ensemble Gram rows, and the exact
Neumann consequence. Its endpoint remains

\[
0.4980274167750795<\frac12.
\]

The logical chain is therefore:

\[
\begin{array}{c}
\text{adaptive exchange}\quad\text{discovers a finite mode set},\\
\text{rational duals + Arb}\quad\text{prove the declared support choice},\\
\text{full Arb/MPFR artifact}\quad\text{proves coefficient recovery}.
\end{array}
\]

No layer is used outside its stated scope.

---

## 8. Validity boundary

Established:

- a correctly identified mode-row generation procedure;
- repeated support and weight stability under twelve adaptively added modes;
- an exact rational primal/dual theorem for each finite pair problem;
- a rigorous method for weakening those duals over Arb response intervals;
- exact checking of all 51 declared pair supports;
- unique formal selection of `T=510` for the fourteen-mode objective;
- preservation of that selection by the published dyadic weight;
- explicit separation between design optimality and recovery validity.

Not established:

- termination of adaptive mode exchange;
- a bound proving that all unselected modes cannot change the support;
- optimality among three-or-more-scale measures;
- optimality for a continuous interval of short times;
- optimality when remote tails, Gram conditioning, or all targets enter the
  formal design objective;
- a two-sided formal remote objective for all 51 candidate scales;
- a noise-aware advantage;
- any consequence for zeta zeros, the Riemann hypothesis, or physics.

The constant complete-audit value in the exchange table occurs because the
same support and numerical weight are selected each time. It is not evidence
that the unselected residual vanished. Indeed, the restricted objective still
increases as modes are added.

---

## 9. Reproduction

Run the adaptive discovery and formal support report:

```bash
python adaptive_multiscale_exchange.py
```

Rebuild or independently check the exact artifact:

```bash
python verify_adaptive_multiscale_certificate.py
```

The committed artifact is:

```text
certificates/arithmetic_sensing_v_adaptive_multiscale.json
```

Run the focused executable checks:

```bash
python -m unittest -v test_adaptive_multiscale_exchange.py
```

---

## 10. Next research targets

1. **Residual stopping envelope.** Bound the total contribution of every
   unselected finite mode uniformly over the candidate weight simplex. This
   would turn support stability into a finite stopping theorem.
2. **Multi-target exchange.** Let targets 1 through 50 propose mode rows and
   solve the true worst-target restricted master problem.
3. **Robust multi-scale duals.** Extend the Arb-interval rational certificate
   from pair supports to arbitrary positive ensembles by a general Farkas or
   interval-LP certificate.
4. **True scale-column generation.** Use dual reduced costs to search a dense
   or continuous time family, with a certified global oracle in `T`.
5. **Formal design penalties.** Construct two-sided or robust remote and Gram
   contributions for every candidate scale rather than using them only in the
   independent recovery audit.

The most immediate target is the residual stopping envelope. It attacks the
largest remaining logical gap: not whether the selected finite LP is solved,
but when the adaptive finite LP has seen enough of the million-term geometry.
