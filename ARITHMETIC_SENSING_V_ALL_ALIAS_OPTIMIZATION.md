# Arithmetic Sensing V — All-Alias Optimization

## Cancellation geometry and the degree-thirteen frontier

- **Research lead, theorem, implementation, and manuscript:** Codex (OpenAI)
- **Originating question and research environment:** TGN's human founder
- **Status:** ambitious Stage V milestone complete
- **Date:** 13 August 2026
- **Parent manuscripts:** `ARITHMETIC_SENSING_V.md`,
  `ARITHMETIC_SENSING_V_VERIFIED_MELLIN.md`

## Abstract

The preceding Stage V certificate bounded each shifted Dirichlet kernel
separately and combined their magnitudes by the triangle inequality. That
operation erased the cancellation deliberately created by the cosine window.
This paper derives an exact common-numerator factorization of the centered
midpoint response and turns it into a cancellation-aware interval theorem.
The theorem has an outward-rounded MPFR implementation and is inserted into
the exact-dyadic log-Mellin certificate without changing the arithmetic mass
model.

At `N=50`, `sigma=2`, `T=1000`, `m=5000`, and a million-term finite cutoff,
the unchanged reference window now gives the following hybrid complete
coefficient bounds:

| degree | complete bound | conclusion |
|---:|---:|:---:|
| 9 | `0.00685857145` | certified |
| 12 | `0.127025847` | certified |
| 13 | `0.330597339` | certified |
| 14 | `0.842697201` | not certified |

Thus degree thirteen, not degree eight, is the new frontier of this sufficient
recovery proof at the stated resources. The degree-nine post-million remote
bound at target 50 falls from `4.53398481e-4` to `1.83743168e-6` under formal
MPFR evaluation. This is not a looser numerical heuristic: it follows from an
exact identity that the previous triangle proof discarded.

A second experiment optimizes the actual million-term finite objective plus
every retained Mellin alias bin jointly for targets 49 and 50. Its independently
rechecked candidate improves the degree-nine complete bound from
`0.00685857145` to `0.00659978727`. More importantly, two failed restricted
optimizations expose why an all-target, finite-plus-remote objective is needed:
a remote-only candidate fails completely, while a target-50-only candidate
makes target 49 worse.

The remote artifact is a formal directed-MPFR/dyadic certificate. The finite
million-term response sum and final Gram inverse remain explicitly labelled
binary64 computations, so the end-to-end degree frontier is still a hybrid
certificate rather than a proof-assistant theorem.

---

## 1. The apparent degree-nine obstruction

For the positive midpoint quadrature with cosine density

\[
p(\theta)=1+2\sum_{r=1}^{H}c_r\cos(r\theta),
\]

the former remote theorem bounded the base uniform kernel and all `2H` shifted
kernels independently. It then formed

\[
|D_0|+\sum_{r=1}^{H}|c_r|\bigl(|D_r|+|D_{-r}|\bigr).
\]

This is safe, but it cannot see destructive interference among the shifted
terms. The loss was small in earlier low-degree computations and dominant for
degree nine: the old complete bound was `1.13678878`, although the explicitly
enumerated million-term contribution was tiny. Increasing the observation
time overcame that estimate, but did not explain it.

The right diagnostic question was therefore not “how can the window be made
smaller term by term?” It was “what algebraic relation do all shifted midpoint
kernels share?”

---

## 2. Exact common-numerator identity

Put

\[
u=\frac{T\omega}{2}.
\]

After removing the universal phase, the uniform midpoint response is

\[
D_0(u)=\frac{\sin u}{m\sin(u/m)}.
\]

The `r`th cosine harmonic shifts `u` by `±pi r`. Its numerator satisfies

\[
\sin(u+\pi r)=(-1)^r\sin u.
\]

The midpoint modulation contributes the same factor `(-1)^r`, so the signs
cancel exactly. Define

\[
g_r(u)=\frac{1}{m\sin((u+\pi r)/m)}.
\]

### Theorem A — centered cancellation factorization

Away from the removable sampling aliases, the complete centered response is

\[
R(\omega)=\sin u\left[g_0(u)+
\sum_{r=1}^{H}c_r\bigl(g_r(u)+g_{-r}(u)\bigr)\right].
\]

At an alias, the value is defined by the continuous limit. Because the
quadrature weights are positive and sum to one, `|R(omega)|<=1` globally.

### Proof

Write each modulated cosine as the half-sum of its positive and negative
frequency shifts. Substitute the centered uniform quotient into every shifted
term. The two factors `(-1)^r` described above multiply to one, leaving a
common factor `sin u`. Summing the base term and harmonic pairs gives the
displayed formula. The alias statement follows from the original finite
exponential sum, which has no singularities; positivity gives its unit bound.
QED.

This elementary identity is the central advance. The old proof applied an
absolute value before summing the bracket. The new proof sums first.

---

## 3. A cancellation-aware interval theorem

Let a frequency bin map to an interval `J=[u_-,u_+]`; write its midpoint as
`u_bar` and radius as `rho`. Define the bracket in Theorem A by `G(u)`.
If no shifted denominator meets the alias lattice on `J`, then

\[
|R(\omega)|\le |G(\bar u)|+\rho\sup_{u\in J}|G'(u)|,
\]

because `|sin u|<=1`. Moreover,

\[
|g_r'(u)|
=\frac{|\cos((u+\pi r)/m)|}
{m^2|\sin((u+\pi r)/m)|^2}
\le \frac{1}{m^2\sin^2\delta_r},
\]

where `delta_r` is the distance of the full shifted interval to the nearest
multiple of `pi`. Consequently,

\[
\begin{aligned}
\sup_J |R|
\le \min\Bigg(1,
&\left|g_0(\bar u)+\sum_{r=1}^{H}c_r
 (g_r(\bar u)+g_{-r}(\bar u))\right|\\
&+\rho\left[V_0+\sum_{r=1}^{H}|c_r|(V_r+V_{-r})\right]
\Bigg),
\end{aligned}
\]

with `V_r=1/(m^2 sin^2(delta_r))`. If any denominator interval touches an
alias, the theorem returns the positive-quadrature fallback `1`.

Every operation in the formal realization is outward rounded. Logarithms,
`pi`, interval endpoints, sine evaluations, signed coefficient products,
derivative remainders, and the final dyadic ceiling are evaluated with MPFR
directed modes. Dense sampling tests are useful regressions, but are not the
reason the interval bound is valid.

---

## 4. Formal remote result

The one-factor masses and exact carry-free dyadic convolutions are unchanged
from the verified Mellin milestone. Only the kernel supremum attached to each
product-log bin is replaced by the theorem above.

For degree nine, the formal post-million upper bounds are:

| target | cancellation-aware remote bound |
|---:|---:|
| 1 | `1.852707463901359e-6` |
| 10 | `1.668191471651033e-6` |
| 49 | `1.834139130735533e-6` |
| 50 | `1.837431678271238e-6` |

At target 50, the previous independently shifted theorem gave
`4.533984807992932e-4`. The new bound is about 247 times smaller. The exact
degree-nine remote vector has SHA-256 digest

```text
ddfc4f49c253aa654fe16da92b9cb0e57cc60f7ba0466dcf8495c94dbdf5f094
```

The new compact artifact additionally records degrees 13 and 14, which locate
the pass/fail frontier:

| degree | target 1 | target 10 | target 50 | remote-vector SHA-256 |
|---:|---:|---:|---:|:---|
| 9 | `1.85270746e-6` | `1.66819147e-6` | `1.83743168e-6` | `ddfc4f49…f5f094` |
| 13 | `2.29127550e-4` | `1.32622076e-4` | `1.27491989e-4` | `578b7f3a…e875b` |
| 14 | `7.27729314e-4` | `3.67251555e-4` | `3.29877131e-4` | `93ee352d…b43314` |

The artifact's signed formal projection has SHA-256 digest

```text
a27abd9e849620c74ac851de39430a381b938e73f59d58426ee88c278ca5be50
```

---

## 5. The new fixed-degree frontier

The following scan uses the same reference window and the same resources at
every degree.

| degree | global tail before filtering | worst complete bound | worst target | pass? |
|---:|---:|---:|---:|:---:|
| 2 | — | `0.0000160857` | 49 | yes |
| 3 | — | `0.0000512476` | 49 | yes |
| 4 | — | `0.000128430` | 49 | yes |
| 5 | — | `0.000282671` | 49 | yes |
| 6 | — | `0.000589455` | 49 | yes |
| 7 | — | `0.00124545` | 49 | yes |
| 8 | — | `0.00280806` | 49 | yes |
| 9 | `0.621746` | `0.00685857` | 49 | yes |
| 10 | — | `0.0177363` | 50 | yes |
| 11 | — | `0.0477789` | 50 | yes |
| 12 | — | `0.127026` | 50 | yes |
| 13 | `28.5564` | `0.330597` | 50 | yes |
| 14 | `66.2708` | `0.842697` | 50 | no |
| 15 | `148.450` | `2.11524` | 50 | no |

The global unfiltered remainder already exceeds 28 at degree thirteen, yet the
kernel-aware coefficient error is below one third. That contrast is a useful
quantitative expression of arithmetic sensing: recovery depends on the
geometry of where spectral mass lands, not only on its total amount.

### Corollary — degree-thirteen universal recovery at the tested resources

Subject to the fixed-degree domination `a_K(n)<=d_d(n)` and the Stage V
measurement model, rounding the reconstructed first 50 coefficients is
certified for every number field of degree at most thirteen at
`sigma=2`, `T=1000`, and `m=5000`, under the stated hybrid numerical audit.

Degree fourteen is not disproved. This sufficient certificate merely crosses
its `1/2` threshold there.

---

## 6. Actual all-alias optimization

The new identity also makes the remote objective suitable for direct window
search. For every chosen target, the search precomputes:

1. all affine centered responses for norms `51<=k<=10^6`;
2. all exact-dyadic Mellin masses beyond the cutoff;
3. the affine bracket midpoint and coefficientwise derivative variation for
   every retained product-log interval;
4. the elementary mass after the declared two-alias range.

For coefficients `c`, the objective evaluates the absolute affine finite
responses and every cancellation-aware remote interval. The reported run
minimized the maximum target-scaled envelope for targets 49 and 50. Candidate
generation used Powell's derivative-free method; it is not treated as an
optimality proof.

The recorded candidate is

```text
[-0.6264146955471602,
  0.11592301462359696,
  0.0016545222416823374,
  0.009510801153787815,
 -0.0006316498798685098,
 -0.0001316789270583388,
  0.0003943240799222973,
 -0.0002996383748447402]
```

Its decimal vector has an exact rational Sturm certificate

\[
9.9\times10^{-6}<p(\theta)<2.499999999
\]

on the entire circle. Its 50-by-50 Gram matrix has numerical smallest
eigenvalue `0.981820726`. The exact sum of binary64 representation errors is
also propagated uniformly through the density; it is far smaller than the
displayed strict margins, so the stored floating candidate remains positive
and below `2.5`.

| degree-nine quantity | reference | all-alias candidate |
|:---|---:|---:|
| joint 49/50 search proxy | `0.00683580432100` | `0.00657721945598` |
| independently recomputed complete bound | `0.00685857145` | `0.00659978727` |
| worst target | 49 | 49 |

The candidate gives a modest 3.77% reduction. The theorem, not this numerical
improvement, is responsible for the large frontier jump.

---

## 7. Falsification experiments

Restricted objectives produced useful counterexamples to tempting design
shortcuts.

### Remote-only search

A candidate reduced the target-50 remote proxy to about `1.47e-6`, but moved
spectral energy into the explicitly enumerated near tail. Its complete bound
became `1.2708`, so it failed integer recovery.

### Single-target finite-plus-remote search

Optimizing only target 50 reduced that target's finite term, but target 49
became dominant. The full coefficient bound worsened to about `0.00877`.

### Joint search

Including both adjacent boundary targets balanced their proxies at about
`0.00657722` and survived the independent all-50-target recomputation.

These experiments support a concrete design principle: an arithmetic sensor
must optimize the finite band and every retained alias together, across the
targets likely to exchange dominance. A small remote number in isolation is
not evidence of a good sensor.

---

## 8. Reproduction

Install the declared dependencies, then run:

```bash
python -m unittest
python arithmetic_sensing_v.py --degree-study --maximum-study-degree 15
python verify_mellin_certificate.py \
  --certificate certificates/arithmetic_sensing_v_cancellation_frontier.json \
  --degrees 9,13,14 --skip-hybrid-report
python all_alias_mellin_optimization.py
python all_alias_mellin_optimization.py --objective-audit
python all_alias_mellin_optimization.py --complete-certificate
```

The exact candidate positivity check is fast. The degree scan, complete
candidate audit, and MPFR artifact reconstruction are intentionally expensive.
To rerun candidate generation itself:

```bash
python all_alias_mellin_optimization.py --search
```

That command materializes two million affine finite responses plus the remote
Mellin data and requires substantial transient memory. Search output is only a
candidate; `--complete-certificate` and the exact positivity check remain
mandatory.

---

## 9. What has and has not been established

Established:

- an exact common-numerator factorization for every finite cosine window on
  the midpoint grid;
- a cancellation-aware interval supremum theorem with alias-safe fallback;
- an outward-rounded MPFR implementation of that theorem;
- formal remote dyadic bounds and a compact reconstructible artifact;
- a hybrid universal recovery certificate through degree thirteen at the
  tested resources;
- an actual finite-plus-all-alias window-search implementation and an
  independently checked degree-nine candidate;
- negative evidence against remote-only and single-target optimization.

Not established:

- a fully formal enclosure of the million-term binary64 sum or Gram inverse;
- global optimality of the recorded window;
- failure or impossibility in degree fourteen;
- recovery beyond the first 50 coefficients;
- identification of an entire number field from these coefficients;
- a statement about zeta zeros, altered axioms, quantum fields, or physics.

The most important correction is methodological. The former degree-eight
frontier looked arithmetic, but was actually created by a proof step that
destroyed the window's cancellation. Preserving the exact geometry of the
response changed the theorem by orders of magnitude before optimization had
any serious role.

---

## 10. Next research targets

1. **End-to-end intervalization.** Enclose the million-term affine sums and
   Gram solve so that the degree-thirteen statement becomes formal throughout.
2. **Certified convex search.** Replace candidate-only Powell search by a
   cutting-plane or bundle method with a posteriori lower bounds on the
   finite-plus-alias optimum.
3. **Target exchange.** Add targets adaptively whenever an all-50 audit finds
   a new maximizer, rather than fixing 49 and 50 in advance.
4. **Degree-fourteen resource law.** Determine the smallest change in `T`,
   sampling ratio, harmonic count, or cutoff that certifies degree fourteen.
5. **Sharper numerator use.** The interval theorem currently pays
   `|sin u|<=1`; retaining a correlated interval bound for the common numerator
   may improve bins far from its peaks.
6. **General positive spectral factors.** Express the search directly in a
   Fejer--Riesz or semidefinite parameterization to make continuum positivity
   native rather than a posteriori.

The first target is the natural continuation: the new remote theorem is now
stronger than the numerical model used for the finite and linear-algebra
pieces.
