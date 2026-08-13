# Arithmetic Sensing V — Verified Mellin Milestone

> **Later milestone:** `ARITHMETIC_SENSING_V_ALL_ALIAS_OPTIMIZATION.md`
> preserves cancellation among shifted kernels and supersedes the numerical
> degree-eight/degree-nine boundary below. This document remains the formal
> foundation for directed bins and exact dyadic convolution.

## Directed MPFR bins, exact dyadic convolution, and a compact checker

- **Research lead and implementation:** Codex (OpenAI)
- **Originating question and research environment:** TGN's human founder
- **Status:** first formal-numerics milestone complete
- **Date:** 13 August 2026
- **Parent manuscript:** `ARITHMETIC_SENSING_V.md`

## Abstract

Arithmetic Sensing V proved an exact log-Mellin bin inequality but realized its
one-factor masses and repeated convolutions in binary64 arithmetic, protected
by a declared `10^-10` multiplicative margin. This milestone removes that
heuristic from the theorem path.

Every exponential bin boundary is evaluated twice with MPFR: once toward
negative infinity and once toward positive infinity. A boundary is accepted
only when both enclosures have the same integer ceiling. Positive one-factor
masses are accumulated toward positive infinity and rounded upward to exact
dyadic rationals with denominator `2^96`. Their degree-`d` convolution is then
computed with exact integer arithmetic, using a carry-free Kronecker encoding.
The periodic sampling-kernel envelope and analytic remote tail are evaluated
toward positive infinity, and each final per-target remainder is stored as an
exact rational with denominator `2^128`.

At the published parameters, the verified post-million remote bounds at target
50 are

| degree | verified remote bound |
|---:|---:|
| 5 | `3.012328757865473e-6` |
| 8 | `1.498499848151033e-4` |
| 9 | `4.533984807992932e-4` |

Replacing the former safety-factor realization changes the hybrid complete
coefficient bounds by less than `7.5e-8`. Degree eight remains certified and
degree nine remains uncertified. Thus the Stage V boundary is stable under the
stronger numerical model.

The committed 11-kilobyte artifact contains all 50 exact dyadic target bounds
for degrees 5, 8, and 9, together with hashes of the one-factor bins and exact
convolutions. The checker reconstructs them from first principles. Its formal
hash deliberately excludes the separately labelled binary64 finite-sum and
Gram-inverse continuation report, allowing independent validation across BLAS
implementations.

---

## 1. Scope of the upgrade

The infinite tail was split in Arithmetic Sensing V at `M=10^6`:

\[
\sum_{k>N}d_d(k)k^{-2}|K(\log(k/n))|
=\sum_{N<k\le M}(\cdots)+\sum_{k>M}(\cdots).
\]

The new formal certificate covers the entire second term, including retained
sampling aliases and the analytic tail after the declared logarithmic range.
It also replaces the default one-factor and convolution backend used by the
ordinary Stage V reproduction.

The first term still uses vectorized binary64 kernel evaluations, and the final
coefficient transformation still uses a binary64 Gram inverse. Consequently:

- the remote Mellin remainder is now an outward-rounded formal numerical
  certificate;
- the displayed complete coefficient bound is still a hybrid computation;
- the mathematical degree-eight margin is reproduced, not promoted to a fully
  formal end-to-end machine proof.

This distinction is encoded in the artifact rather than left to prose.

---

## 2. Certified exponential boundaries

Let the bin width be the exact rational `h=1/100`. For each integer `j`, the
one-factor bin is

\[
B_j=\{n\in\mathbb N:e^{jh}\le n<e^{(j+1)h}\}.
\]

It is enough to know the exact integer ceiling

\[
u_j=\lceil e^{jh}\rceil,
\qquad
B_j=\{u_j,u_j+1,\ldots,u_{j+1}-1\}.
\]

At MPFR precision `p`, compute

\[
L_j\le e^{jh}\le U_j
\]

with directed rounding. The boundary is accepted if

\[
\lceil L_j\rceil=\lceil U_j\rceil.
\]

Otherwise the precision is doubled. All 8,247 boundaries in the published
certificate resolve at the initial 192-bit precision. This procedure does not
assume that a binary approximation lies on the correct side of an integer.

The logarithmic endpoint is selected outward as well. The declared alias range
requires

\[
R\ge \log 50+\left(2+\frac12\right)\frac{2\pi m}{T}.
\]

Directed evaluation gives 8,246 bins, so the checker uses the exact rational

\[
R=8246/100=82.46.
\]

---

## 3. Exact dyadic one-factor masses

For `sigma=2`, define

\[
\beta_j=\sum_{n\in B_j}n^{-2}.
\]

Terms through one million are accumulated with MPFR rounding toward positive
infinity. Above that cutoff, an inclusive interval `[A,B]` uses the exact
rational integral-test bound

\[
\sum_{n=A}^{B}n^{-2}
\le \frac1{A^2}+\int_A^B x^{-2}\,dx
=\frac1{A^2}+\frac1A-\frac1B.
\]

The resulting upper endpoint is rounded upward to

\[
\beta_j\le \frac{b_j}{2^{96}},
\qquad b_j\in\mathbb Z_{\ge0}.
\]

The 8,246 integer numerators have SHA-256 digest

```text
e85cc261efecb4a77c2d044db63f6b01a16d4c82a6ec85ebbe1fce71cc61d8dc
```

Their total upper mass reproduces `zeta(2)` to the displayed precision.
Recomputing the entire artifact at 256-bit MPFR precision produces identical
one-factor, convolution, and remote-target hashes for all three degrees; the
`2^-96` and `2^-128` dyadic endpoints are therefore stable between the two
tested precisions.

---

## 4. Exact convolution without a floating FFT

### Theorem — dyadic convolution domination

If

\[
0\le\beta_j\le b_j2^{-q},
\]

then the degree-`d` ordered-factor bin mass satisfies

\[
C_r^{(d)}\le c_r2^{-qd},
\qquad
c_r=[x^r]\left(\sum_jb_jx^j\right)^d.
\]

### Proof

Expand both `d`-fold convolutions. Each summand is a product of nonnegative
one-factor masses and is bounded termwise by the corresponding product of
dyadic upper endpoints. Summing preserves the inequality. QED.

### Carry-free Kronecker realization

Let

\[
S=\sum_jb_j.
\]

Every coefficient of the polynomial power is at most `S^d`. Choose a power-of-
two base `Q>S^d` and encode

\[
Z=\sum_j b_jQ^j.
\]

Because no coefficient reaches the base, the base-`Q` digits of the exact
integer `Z^d` are precisely the convolution coefficients `c_r`. Python's
arbitrary-precision integer multiplication therefore supplies the full
convolution without FFT roundoff, interval widening, or an empirical margin.

The published convolution hashes are:

| degree | dyadic scale | digit bytes | SHA-256 |
|---:|---:|---:|---|
| 5 | 480 | 61 | `b4e94da0dee4ee24e110e642f208460232a65fa68596973c82a42fd6c081db3f` |
| 8 | 768 | 97 | `04060e38b92b017f985c05a34c83531fd01d8db11b5a23cb2df14efda65c5513` |
| 9 | 864 | 109 | `9a3fab090b54db2747b132a06e3a4f6a96df9c886d5c19121a9dc9c21c593dc5` |

---

## 5. Directed alias and remote bounds

For tuple-bin index `r`, the product logarithm lies in

\[
[rh,(r+d)h].
\]

After subtracting an outward enclosure of `log n`, the checker bounds every
shifted uniform midpoint kernel by

\[
\min\left(1,
\frac{\pi}{T\,\operatorname{dist}(I,\Lambda)}\right),
\]

where `I` is the full frequency interval and `Lambda` is the exact sampling-
alias lattice. Lower bounds for distance are rounded toward negative infinity;
reciprocals, coefficient products, and sums are rounded toward positive
infinity. Positivity of the exactly certified quadrature gives the final global
cap `|K|<=1`.

After `R=82.46`, the remaining `d_d` mass is paid using the elementary tail

\[
2e^{-R}(d-1)!\sum_{j=0}^{d-1}\frac{(1+R)^j}{j!},
\]

again evaluated toward positive infinity. Each completed target bound is then
rounded upward to a rational with denominator `2^128`.

---

## 6. Results and stability of the Stage V boundary

| degree | old complete bound | strengthened hybrid bound | change | conclusion |
|---:|---:|---:|---:|:---:|
| 5 | `0.00775068233457` | `0.00775067643029` | `-5.90e-9` | certified |
| 8 | `0.376281083556` | `0.376281043766` | `-3.98e-8` | certified |
| 9 | `1.13678885660` | `1.13678878251` | `-7.41e-8` | not certified |

The small downward changes arise because exact dyadic convolution needs much
less excess mass than the former `10^-10` multiplier. They are too small to
alter any Stage V conclusion.

The result is scientifically useful in two ways:

1. it validates that the heuristic inflation did not create the degree-eight
   success;
2. it turns the formerly dominant proof concern—the remote fixed-degree
   remainder—into an independently reconstructible object.

---

## 7. Compact artifact and checker

The committed artifact is

```text
certificates/arithmetic_sensing_v_verified_mellin.json
```

Its signed formal projection has SHA-256 digest

```text
e0ec5915b2b9d30d78df024f0fae208dfb14e3c397ee8e3a9f40f0f783115b22
```

The projection includes all formal parameters, binary64 window coefficients as
exact hexadecimal values, one-factor and convolution hashes, and all 50 exact
remote bounds for degrees 5, 8, and 9. It excludes fields explicitly marked
`hybrid`, so a different BLAS implementation cannot invalidate the formal
Mellin check through a last-bit Gram-inverse difference.

Recompute and verify it with:

```sh
python verify_mellin_certificate.py
```

Rebuild and print a fresh artifact with:

```sh
python verify_mellin_certificate.py --emit
```

The checker does not trust stored bin arrays. It reconstructs all exponential
boundaries and masses, repeats the exact integer polynomial powers, recomputes
all target bounds, hashes the formal projection, and compares it with the
artifact.

---

## 8. Validity boundary and next target

This milestone establishes:

- directed transcendental endpoints for the remote Mellin construction;
- exact dyadic domination of every one-factor bin;
- exact repeated convolution;
- directed interval bounds for all retained remote aliases;
- a portable formal payload with tamper detection.

It does not yet establish:

- interval evaluation of all 50 million finite kernel terms;
- a formal interval inverse of the 50-by-50 Gram matrix;
- formal sensor-noise probabilities;
- field identification, a result about zeta zeros, or a physical law.

The next research target from Arithmetic Sensing V remains optimization of the
actual all-alias log-Mellin objective. A tangential formal target is an end-to-
end interval certificate for the finite sum and Gram solve. The former is more
likely to improve the degree-nine boundary; the latter strengthens proof
status without changing the sensing design.

---

## 9. Numerical foundation

GNU MPFR specifies correct rounding as if the exact real result were computed
and then rounded in the requested direction. `gmpy2` exposes MPFR contexts with
rounding toward negative and positive infinity:

- [GNU MPFR](https://www.mpfr.org/)
- [gmpy2 context and rounding documentation](https://gmpy2.readthedocs.io/en/latest/contexts.html)

No novelty is claimed for MPFR, interval arithmetic, dyadic enclosures,
Kronecker substitution, or the classical divisor identity. The contribution is
their auditable composition into the Stage V all-alias arithmetic-sensing
certificate and the measured stability result above.
