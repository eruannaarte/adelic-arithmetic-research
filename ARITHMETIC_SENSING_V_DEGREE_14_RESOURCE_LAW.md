# Arithmetic Sensing V — Degree-Fourteen Resource Law

## Exact sampling and observation thresholds amid logarithmic resonances

- **Research lead, theorem, computation, and manuscript:** Codex (OpenAI)
- **Originating question and research environment:** TGN's human founder
- **Status:** resource-law milestone complete
- **Date:** 13 August 2026
- **Parent manuscript:** `ARITHMETIC_SENSING_V_END_TO_END.md`

## Abstract

The preceding end-to-end certificate located the fixed-resource frontier at
degree thirteen: at `N=50`, `sigma=2`, `T=1000`, and `m=5000`, degree thirteen
is certified by `0.3308795520`, while degree fourteen gives `0.8438209207`.
This paper asks how much additional sensing resource makes degree fourteen
certifiable and whether observation time and sample count are interchangeable.

They are not. Three resource paths exhibit distinct geometry.

At fixed observation time `T=1000`, increasing the sample count moves the
periodic sampling aliases outward while leaving the continuous observation
window unchanged. The localized hybrid scan finds an adjacent-integer
transition at 14,690/14,691 samples. Independent directed-MPFR, Arb, exact-
integer, and exact-rational artifacts prove

| `T` | `m` | formal coefficient bound | result |
|---:|---:|---:|:---:|
| 1000 | 14,690 | `0.5000009667019292` | not certified |
| 1000 | 14,691 | `0.49999753821015847` | certified |

Thus 14,691 is the exact first success of the localized fixed-window bound on
the exhaustively tested monotone integer interval from 10,000 through 15,000
samples; the adjacent pair itself is then checked by the formal artifacts.

At fixed sampling ratio `m/T=5`, increasing `T` does not initially improve the
bound. The finite logarithmic modes pass through strong resonances: `T=1100`
gives about `2.26` and `T=1200` about `3.20`, much worse than the `T=1000`
value. Nevertheless an exhaustive integer scan from `T=1000` through `3000`
finds exactly one pass/fail crossing. The formal adjacent pair is

| `T` | `m` | formal coefficient bound | result |
|---:|---:|---:|:---:|
| 1892 | 9460 | `0.5000018477486967` | not certified |
| 1893 | 9465 | `0.4992815921942569` | certified |

Every tested integer time from 1893 through 3000 passes the hybrid localized
bound, although small resonance oscillations continue. At `T=3000`, `m=15000`,
the bound is approximately `0.31304`.

The result is a resource law with arithmetic structure, not a smooth
sample-complexity curve. More readings and longer observation affect different
parts of the logarithmic sensing geometry, and scaling both together can first
make recovery worse before making it better.

---

## 1. Resource variables are geometrically different

For an `m`-point midpoint grid over observation time `T`, the uniform centered
kernel has the exact form

\[
D_{m,T}(\omega)=
\frac{\sin(T\omega/2)}{m\sin(T\omega/(2m))}.
\]

The optimized cosine window is a finite linear combination of frequency shifts
of this kernel. Two scales are visible immediately:

1. the resolution scale `2 pi/T`, controlled by observation time;
2. the sampling-alias period `2 pi m/T`, controlled by the sampling ratio.

Consequently `T` and `m` cannot be collapsed to a single resource count.

### Fixed `T`, increasing `m`

The numerator is unchanged. The alias period grows linearly with `m`, and

\[
m\sin(T\omega/(2m))\longrightarrow T\omega/2.
\]

Thus the discrete response approaches the continuous-window Fourier response
while aliases move outward.

### Fixed `m/T`, increasing `T`

The alias period stays fixed. The numerator `sin(T omega/2)` and its windowed
counterparts oscillate more rapidly across the discrete logarithmic
frequencies. Average resolution improves, but individual arithmetic modes can
move into or out of response lobes. Monotonicity is therefore not expected at
finite `T`.

### Fixed `m`, increasing `T`

Resolution improves but the alias period shrinks. These effects compete, and
the finite arithmetic modes continue to cross response lobes. This path has no
simple monotone interpretation.

---

## 2. The localized resource proxy

Let `eta_i(T,m)` be the complete finite-plus-remote degree-fourteen tail
envelope, and let

\[
r_i(T,m)=\sum_{j\ne i}|G_{ij}(T,m)|,
\qquad q(T,m)=\max_i r_i(T,m).
\]

The end-to-end theorem gives

\[
B_i(T,m)=i^2\left[
\eta_i(T,m)+r_i(T,m)
\frac{\max_j\eta_j(T,m)}{1-q(T,m)}
\right].
\]

Integer recovery is certified when `max_i B_i<1/2`.

In the published scans, target 1 maximizes the unscaled tail and target 50
maximizes the coefficient consequence. The exploratory implementation uses
those two targets to search large parameter grids efficiently. Every reported
boundary artifact independently recomputes all 50 targets, so this empirical
reduction is never inserted as a theorem assumption.

The exploratory layer uses:

- exact generalized-divisor coefficients through one million;
- the exact-dyadic degree-fourteen log-Mellin convolution;
- the cancellation-aware remote theorem;
- binary64 finite response vectors and Gram rows.

The formal layer replaces the last bullet with Arb and composes exact dyadic
endpoints exactly as in the parent paper.

---

## 3. Fixed-time sampling threshold

Set `T=1000`. The fixed-time path separates sampling density from observation
resolution. Selected localized hybrid results are:

| samples `m` | coefficient bound |
|---:|---:|
| 5,000 | `0.843820921` |
| 6,000 | `0.652610757` |
| 8,000 | `0.565032561` |
| 10,000 | `0.530375343` |
| 14,690 | `0.500000348` |
| 14,691 | `0.499996920` |
| 15,000 | `0.498971581` |
| 20,000 | `0.488584371` |
| 50,000 | `0.477695556` |
| 100,000 | `0.476167132` |
| `10^9` proxy | `0.475659139` |

The dense-sampling values reveal a nonzero floor near `0.47566`. Sampling can
remove the discretization and alias penalty at this observation time, but it
cannot replace longer observation indefinitely.

### Formal adjacent-pair theorem

At the two boundary sample counts, the checker reconstructs separate MPFR
remote artifacts over the fixed certified log range `R=82.46`, then performs
all finite and Gram evaluations with Arb.

### Theorem A — formal fixed-time sampling boundary

Let `U(T,m)` denote the outward-rounded formal endpoint produced for the
maximum coefficient bound. At `T=1000`, the published artifacts give

\[
U(1000,14690)
= 0.5000009667019292>\frac12,
\]

so that bound does not certify recovery, while

\[
U(1000,14691)
= 0.49999753821015847<\frac12,
\]

so 14,691 samples certify integer recovery.

The strict language matters: the first upper bound being above one half does
not prove recovery fails. It proves only that this sufficient certificate does
not establish it.

---

## 4. Fixed-ratio observation law

Now impose `m=5T`, keeping the exact sampling alias period equal to `10 pi`.
Selected localized hybrid values are:

| `T` | `m` | bound |
|---:|---:|---:|
| 1000 | 5000 | `0.843821` |
| 1100 | 5500 | `2.26137` |
| 1200 | 6000 | `3.19965` |
| 1300 | 6500 | `2.71608` |
| 1500 | 7500 | `1.10312` |
| 1750 | 8750 | `0.614800` |
| 1892 | 9460 | `0.500001848` |
| 1893 | 9465 | `0.499281592` |
| 2000 | 10000 | `0.448354` |
| 2250 | 11250 | `0.488761` |
| 2500 | 12500 | `0.436640` |
| 2750 | 13750 | `0.345420` |
| 3000 | 15000 | `0.313036` |

This curve is not monotone. The striking initial worsening comes from the
finite band, not from the remote theorem. At target 50:

| resources | finite component | remote component |
|:---|---:|---:|
| `(T,m)=(1000,5000)` | `6.82704e-6` | `3.29877e-4` |
| `(T,m)=(1100,5500)` | `5.96386e-4` | `3.01506e-4` |
| `(T,m)=(1200,6000)` | `9.88096e-4` | `2.78835e-4` |

The remote component improves, but exact finite logarithmic frequencies land
near large response lobes. Resource scaling has encountered arithmetic
resonance.

### Exhaustive tested-interval result

Every integer `T` from 1000 through 3000 was evaluated at `m=5T`. There is
exactly one crossing of one half, between 1892 and 1893. Every tested integer
from 1893 through 3000 passes, though local extrema persist.

This is a finite exhaustive computation over the declared interval, not a
theorem that every real or integer `T>1893` must pass forever.

### Theorem B — formal fixed-ratio boundary

The formal artifacts give the following exact conclusion:

\[
U(1892,9460)=0.5000018477486967>\frac12,
\]

whereas

\[
U(1893,9465)=0.4992815921942569<\frac12.
\]

---

## 5. What “more resource” means

The experiments support a three-term interpretation:

\[
\text{recovery cost}
=\text{resolution cost}
+\text{sampling-alias cost}
+\text{arithmetic-resonance cost}.
\]

- Observation time primarily changes resolution and finite-mode phase.
- Sampling density primarily changes discretization and alias distance.
- Arithmetic resonance depends on the actual set `log(k/n)`, so it is neither
  a smooth function of `T` nor captured by dimension counting alone.

This helps explain why standard sample-complexity language is incomplete here.
The sensing dictionary is not generic: its frequencies are logarithms of
integers, and deterministic resource choices can align with their finite
relations.

---

## 6. Fixed certified remote range

The original remote artifact selected a log range extending through 2.5
sampling-alias periods. That was convenient at `m/T=5`, but at fixed `T` an
increasing sample count moves the aliases outward and would make the exact
convolution unnecessarily large.

The resource checker therefore also supports an explicit bin count. The
published boundary artifacts retain the already certified range

\[
R=8246/100=82.46.
\]

All mass after `R` is paid with the elementary global kernel bound. This is
valid for every sample count; it decouples proof size from how far away the
new aliases happen to lie.

---

## 7. Formal artifacts and reproduction

The fixed-time adjacent pair uses:

```text
certificates/arithmetic_sensing_v_degree14_m14690_remote.json
certificates/arithmetic_sensing_v_degree14_m14690_end_to_end.json
certificates/arithmetic_sensing_v_degree14_m14691_remote.json
certificates/arithmetic_sensing_v_degree14_m14691_end_to_end.json
```

Their end-to-end formal payload hashes are, respectively,

```text
bdcf19c1916cf5bdb8c20a2d159e41cc73b9c97f4ebf2a4da68726534be25756
02164e418f144cf8f96645da79a914964af3c3dc4df7a2a2cd2de63da3e7a194
```

The fixed-ratio adjacent pair uses:

```text
certificates/arithmetic_sensing_v_degree14_T1892_remote.json
certificates/arithmetic_sensing_v_degree14_T1892_end_to_end.json
certificates/arithmetic_sensing_v_degree14_T1893_remote.json
certificates/arithmetic_sensing_v_degree14_T1893_end_to_end.json
```

Their end-to-end formal payload hashes are, respectively,

```text
85ce1bea72b18d89f4f295e49ff827969a48971741827fa4d3b38d0dbbb5f9e1
06cb07c5fc52f798fefcda66f0ebca10996aaa6a21b13e14c1b208de36ffac16
```

Run the compact exploratory boundary report with:

```bash
python degree_fourteen_resource_law.py
```

The opt-in scans are expensive:

```bash
python degree_fourteen_resource_law.py --sampling-boundary
python degree_fourteen_resource_law.py --density-study
python degree_fourteen_resource_law.py --time-scan
```

Each formal end-to-end artifact can be reconstructed by first rebuilding its
named remote dependency, then running `verify_end_to_end_certificate.py` with
the matching `--observation-time`, `--sample-count`, and `--remote-certificate`.

---

## 8. Validity boundary

Established:

- a fully formal fixed-time pass at 14,691 samples and non-certification at
  14,690;
- a fully formal fixed-ratio pass at `T=1893,m=9465` and non-certification at
  `T=1892,m=9460`;
- exactly one hybrid crossing on every integer time from 1000 through 3000 at
  ratio five;
- a measured dense-sampling floor near `0.47566` at `T=1000`;
- direct evidence that proportional resource scaling can worsen recovery via
  finite arithmetic resonances;
- a fixed-range remote certificate whose size does not grow with sample count.

Not established:

- impossibility below either threshold;
- monotonicity for all sample counts or all observation times;
- persistence of the fixed-ratio pass beyond `T=3000`;
- a closed asymptotic formula for the resonance fluctuations;
- an optimal sampling window or globally minimal resource pair;
- any claim about zeta zeros or physics.

---

## 9. Next research target

The new phenomenon is not merely “degree fourteen needs more data.” It is that
the resource landscape has an arithmetic interference pattern. The natural
next target is therefore a resonance-aware design theorem:

1. identify which finite ratios `k/n` dominate each resource peak;
2. predict bad observation times from simultaneous phase alignment;
3. construct a small ensemble of nearby observation times whose averaged
   response provably suppresses those peaks;
4. compare that deterministic time diversity with adding 9,691 samples at one
   fixed time;
5. retain the existing MPFR/Arb end-to-end standard for any claimed gain.

This would move arithmetic sensing from resource measurement to resource
architecture.
