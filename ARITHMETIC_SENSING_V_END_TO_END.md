# Arithmetic Sensing V — End-to-End Certificate

> **Later milestone:** `ARITHMETIC_SENSING_V_DEGREE_14_RESOURCE_LAW.md`
> proves that degree fourteen becomes certifiable at 14,691 samples with
> `T=1000`, or at `T=1893,m=9465` along the fixed-ratio path.

## Arb finite tails, inverse-free Gram control, and a formal degree-thirteen frontier

- **Research lead, theorem, implementation, and manuscript:** Codex (OpenAI)
- **Originating question and research environment:** TGN's human founder
- **Status:** end-to-end formal-numerics milestone complete
- **Date:** 13 August 2026
- **Parent manuscript:** `ARITHMETIC_SENSING_V_ALL_ALIAS_OPTIMIZATION.md`

## Abstract

The cancellation-aware Arithmetic Sensing V theorem formally enclosed the
post-million log-Mellin tail, but its degree-thirteen recovery statement still
used binary64 for the first million terms and for inversion of a 50-by-50 Gram
matrix. This paper removes both qualifications.

Generalized divisor coefficients are computed by checked unsigned-integer
Dirichlet convolution. Every finite response from norm 51 through one million
is then evaluated with Arb real-ball arithmetic using the exact
common-numerator identity. All 50 positive sums are rounded upward to exact
dyadic rationals. No binary64 logarithm, sine, response, or dot product appears
in the certificate.

The Gram matrix is not interval-inverted. Writing `G=I+E`, a formal
ball-arithmetic audit gives

\[
q=\max_i\sum_{j\ne i}|E_{ij}|
\le 0.020000000000000642.
\]

The Neumann theorem first gives `||G^-1||_infinity <= 1/(1-q)`. A localized
component inequality then prevents the largest unscaled tail, which occurs at
target 1, from being incorrectly multiplied by `50^2`:

\[
|(G^{-1}e)_i|
\le \eta_i+r_i\frac{\|\eta\|_\infty}{1-q},
\qquad
r_i=\sum_{j\ne i}|E_{ij}|.
\]

Composed with the existing directed-MPFR remote artifact, the exact rational
consequence is

| degree | formal coefficient bound | result |
|---:|---:|:---:|
| 13 | `0.3308795520013974` | certified |
| 14 | `0.8438209207138999` | not certified |

Thus degree thirteen is now the end-to-end formal-numerics frontier at
`N=50`, `sigma=2`, `T=1000`, `m=5000`, and the stated window. Degree fourteen
remains only a failure of this sufficient bound. The result is not a theorem
about zeta zeros or identification of number fields.

---

## 1. The two remaining hybrid steps

The preceding milestone split each omitted correlation at `M=10^6`:

\[
\eta_n=
\sum_{50<k\le M}d_d(k)k^{-2}|K(\log(k/n))|
+\sum_{k>M}d_d(k)k^{-2}|K(\log(k/n))|.
\]

The second sum had a directed-MPFR and exact-dyadic certificate. The first was
computed by vectorized binary64 arithmetic. The final coefficient estimate
then used a binary64 inverse of the Gram matrix. Both calculations had wide
empirical margins, but neither was an outward-rounded formal numerical proof.

The new target was deliberately narrow:

1. enclose every finite term rather than estimate floating-point roundoff
   statistically;
2. certify the effect of the Gram operator without trusting a numerical
   inverse;
3. determine whether the degree-thirteen margin survives;
4. preserve degree fourteen as a negative control.

---

## 2. A rejected shortcut: one Mellin certificate after 50

Before evaluating fifty million finite responses, we tested whether the exact
log-Mellin bins could simply begin at `M=50`. This would have been elegant but
false as a useful estimate.

For degree `d`, a tuple-bin with one-factor width `h` locates the product log
only inside an interval of width `d h`. With `d=13` and `h=0.01`, that width is
`0.13`. Near target 50, the response oscillates on scale approximately
`2 pi/T = 0.00628`. The product interval therefore spans many oscillations and
often has supremum one, even when the exact integer frequency has a tiny
response.

The resulting degree-thirteen tail bound was `12.6864` at target 50. This is
not evidence of a large true tail. It is a rigorous falsification of the
coarse-bin shortcut. The near band must retain substantially finer arithmetic
location than the remote tuple convolution provides.

---

## 3. Exact generalized-divisor coefficients

For fixed degree,

\[
d_1(n)=1,
\qquad
d_{r+1}(n)=\sum_{a\mid n}d_r(n/a).
\]

The implementation performs this recurrence in `uint64`. Before every vector
addition it checks whether unsigned wraparound would occur. Consequently the
stored values are exact integers whenever the routine returns normally.

At one million the observed maxima are:

| degree | maximum `d_d(n)` for `n<=10^6` |
|---:|---:|
| 13 | `49,723,844,170` |
| 14 | `125,572,684,160` |

Both are far below `2^64`. The complete coefficient arrays, including their
zero index, are hashed as fixed-width unsigned integers. Their SHA-256 digests
are stored in the artifact so the analytic balls cannot silently be paired
with a different arithmetic envelope.

---

## 4. Arb enclosure of the finite band

Let the binary64 window coefficients be interpreted as their exact dyadic
rational values. For positive frequency put `u=T omega/2` and

\[
B(u)=\frac{1}{m\sin(u/m)}+
\sum_{r=1}^{8}c_r\left[
\frac{1}{m\sin((u+\pi r)/m)}+
\frac{1}{m\sin((u-\pi r)/m)}
\right].
\]

The exact centered response identity is

\[
|K(\omega)|=|\sin(u)B(u)|.
\]

For each target `1<=n<=50` and every `51<=k<=10^6`, the checker constructs
the exact rational input `k/n`, encloses its logarithm, evaluates the displayed
formula, takes the ball absolute value, multiplies by the exact integer
`d_d(k)` and the enclosed rational `1/k^2`, and adds the nonnegative result to
an Arb ball.

The precision is 128 bits. Each completed upper endpoint is rounded upward to
a rational with denominator `2^128`. Precision failure near a removable alias
causes an exception; it cannot silently return a finite-looking result. No such
failure occurs in the published run.

Selected finite upper bounds are:

| degree | target 1 | target 10 | target 50 |
|---:|---:|---:|---:|
| 13 | `1.21937253e-6` | `1.80654115e-6` | `4.59966047860e-6` |
| 14 | `1.98722021e-6` | `2.88890533e-6` | `6.82704001e-6` |

The full vectors, not only these selected values, are committed as exact
dyadic numerators.

---

## 5. Invertibility without interval matrix inversion

The normalized quadrature has exact diagonal Gram entries equal to one. Write

\[
G=I+E.
\]

Every off-diagonal magnitude is enclosed with the same Arb response formula,
now at frequency `|log(i/j)|`. Summing within each row and rounding upward
gives exact dyadic bounds `r_i`. Their maximum is

\[
q=\max_i r_i
\le
\frac{
3402823669209493910661946651439818601
}{
170141183460469231731687303715884105728
}
=0.020000000000000642\ldots.
\]

Since `q<1`, the Neumann series converges and

\[
\|G^{-1}\|_\infty\le\frac{1}{1-q}
=1.0204081632653068\ldots.
\]

This proves invertibility and controls the inverse without computing one.

### Why the global norm alone initially failed

Let `eta_i` be the complete finite-plus-remote tail upper bound. The first
attempt used

\[
\max_i i^2 |(G^{-1}e)_i|
\le 50^2\frac{\max_i\eta_i}{1-q}.
\]

The largest `eta_i` occurs at target 1. Multiplying it by `50^2` gave
`0.587620`, above the rounding threshold. This mixed the scale of one target
with the tail of another.

---

## 6. The localized Neumann theorem

### Theorem A — componentwise inverse-free recovery bound

Suppose `G=I+E`, let

\[
r_i=\sum_{j\ne i}|E_{ij}|,
\qquad q=\max_i r_i<1,
\]

and suppose the tail-correlation vector `e` obeys `|e_i|<=eta_i`. Then

\[
|(G^{-1}e)_i|
\le \eta_i+r_i\frac{\|\eta\|_\infty}{1-q}.
\]

Consequently, for Dirichlet coefficient scaling at `sigma=2`,

\[
|\widehat a_i-a_i|
\le i^2\left(
\eta_i+r_i\frac{\|\eta\|_\infty}{1-q}
\right).
\]

### Proof

Let `x=G^{-1}e`. From `(I+E)x=e`,

\[
x=e-Ex.
\]

Taking the infinity norm gives

\[
\|x\|_\infty
\le\|\eta\|_\infty+q\|x\|_\infty,
\]

so `||x||_infinity <= ||eta||_infinity/(1-q)`. Returning to coordinate `i`,

\[
|x_i|\le\eta_i+r_i\|x\|_\infty,
\]

which gives the stated result. Multiplication by `i^2` is the exact
coefficient rescaling. QED.

This theorem retains almost all of the sharp numerical inverse result while
using only nonnegative exact rational arithmetic after the Arb row sums have
been produced.

---

## 7. End-to-end results

The complete target envelope is the exact sum of:

1. the Arb/dyadic finite numerator for `51<=k<=10^6`;
2. the directed-MPFR/dyadic remote numerator for `k>10^6`.

The largest unscaled complete tails occur at target 1:

| degree | maximum complete tail | target |
|---:|---:|---:|
| 13 | `0.0002303469227617945` | 1 |
| 14 | `0.0007297165341828428` | 1 |

After applying Theorem A target by target, the largest coefficient errors occur
at target 50:

| degree | previous hybrid bound | end-to-end bound | worst target | result |
|---:|---:|---:|---:|:---:|
| 13 | `0.3305973392` | `0.3308795520` | 50 | certified |
| 14 | `0.8426972009` | `0.8438209207` | 50 | not certified |

The formalization penalty in degree thirteen is about `2.82e-4`, less than one
tenth of one percent of the bound. It is far too small to change the frontier.

### Corollary — end-to-end formal degree-thirteen recovery

Under the Arithmetic Sensing V measurement model and the universal domination
`a_K(n)<=d_d(n)`, the first 50 Dirichlet coefficients are certified recoverable
by integer rounding for every number field of degree at most thirteen at
`sigma=2`, `T=1000`, and `m=5000`, using the published positive window.
Indeed `d_r(n)<=d_13(n)` for every `r<=13`, so the degree-thirteen envelope is
itself a common certificate for all smaller degrees.

The corollary is a formal numerical certificate in Arb, MPFR, exact integers,
and exact rationals. It is not a proof-assistant formalization of the source
code or of the surrounding classical number-field facts.

---

## 8. Compact artifact and modular verification

The new artifact is

```text
certificates/arithmetic_sensing_v_end_to_end.json
```

Its signed formal payload has SHA-256 digest

```text
d1881f9448d8a405b0bffa9ef540bc53f0dcb320c41688afb2e4685c9ceb6987
```

It contains:

- all 50 finite dyadic upper numerators for degrees 13 and 14;
- hashes of both exact generalized-divisor arrays;
- all 50 Gram row numerators and their maximum;
- the exact rational localized coefficient consequence;
- the formal hash of the required cancellation-aware remote artifact.

Run the remote reconstruction first:

```bash
python verify_mellin_certificate.py \
  --certificate certificates/arithmetic_sensing_v_cancellation_frontier.json \
  --degrees 9,13,14 --skip-hybrid-report
```

Then reconstruct every finite ball and verify the end-to-end artifact:

```bash
python verify_end_to_end_certificate.py --processes 8
```

The second command takes several minutes because it deliberately evaluates one
hundred million finite response terms for the degree-13/14 frontier pair. A
fresh artifact can be written with:

```bash
python verify_end_to_end_certificate.py \
  --processes 8 \
  --write certificates/arithmetic_sensing_v_end_to_end.json
```

---

## 9. Numerical foundation and validity boundary

Arb represents real quantities by midpoint-radius balls and propagates proven
enclosures through arithmetic and transcendental functions. Python-FLINT
exposes those balls to the checker:

- [Python-FLINT real ball documentation](https://python-flint.readthedocs.io/en/latest/arb.html)
- [Arb documentation](https://arblib.org/)

The certificate establishes:

- exact fixed-degree divisor coefficients through one million;
- outward finite response sums for every target;
- outward Gram row sums;
- an exact inverse-free conditioning theorem;
- exact composition with the separately reconstructible remote artifact;
- a formal numerical pass in degree 13 and failure of this bound in degree 14.

It does not establish:

- impossibility of degree-fourteen recovery;
- global optimality of the window;
- complete identification of a number field from 50 coefficients;
- a theorem about zeta zeros, new axioms, or physical law;
- source-code verification in a proof assistant.

---

## 10. Next research target

The proof bottleneck has now moved. Numerical validity is no longer the reason
degree fourteen fails. The most informative next target is a certified
degree-fourteen resource law:

1. vary observation time and sample count while retaining the formal response
   and Gram theorems;
2. locate the first rigorously certified resource point;
3. separate improvement due to longer observation from improvement due to
   denser sampling;
4. only then test a certified cutting-plane window optimizer at the boundary.

This order keeps theorem improvement distinct from numerical window search and
will show whether degree fourteen is limited primarily by resolution, alias
placement, or the universal `d_14` envelope.
