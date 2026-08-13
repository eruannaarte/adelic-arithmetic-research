# Arithmetic Acceleration in Finite Order–Factorization Rigidity

## Exact two-prime reduction, sparse rational certificates, and scaling evidence

**Status:** completed first study, 2026-08-12. The finite-dimensional duality
and continued-fraction ingredients are classical. The exact reduction and
certificate formulation below are elementary consequences adapted to this
model. The scaling laws are explicitly labeled conjectural; no new infinite
asymptotic theorem is claimed.

## Abstract

Normalize a completely additive arithmetic coordinate by `E(2)=1` and impose

`E(n) <= E(n+1)` for `1 <= n < N`.

How tightly does this finite order data force `E(3)` toward `log_2(3)`?

There are three distinct quantitative layers.

1. A single denominator gives a universal power squeeze of order roughly
   `1/log N`.
2. Using every comparison among powers of `2` and `3` gives an exact
   continued-fraction model, with stepwise improvements often on the
   `1/(log N)^2` scale.
3. Using all adjacent integers activates auxiliary primes. Exact dual
   certificates show that their cancellation network is dramatically
   stronger: at `N=100000` it narrows the certified interval by a factor of
   about `3108` relative to the two-prime model.

The arithmetic contribution is therefore real and measurable. It is not an
artifact of floating-point optimization: every reported full-model bound is
proved by a nonnegative rational combination of adjacent order inequalities.

## 1. The exact two-prime model

Let

`S_H={2^a 3^b : a,b>=0 and 2^a 3^b<=H}`.

Any multiplicatively additive coordinate on this monoid has the form

`E(2^a 3^b)=a+b*x`,

where `x=E(3)` after the normalization `E(2)=1`.

### Theorem A (all mixed comparisons reduce to pure powers)

Order preservation on `S_H` is equivalent to

`L_H <= x <= U_H`,

where

`L_H=max{m/n : 2^m<3^n, 2^m<=H, 3^n<=H}`

and

`U_H=min{m/n : 3^n<2^m, 2^m<=H, 3^n<=H}`.

In particular,

`L_H < log_2(3) < U_H`.

#### Proof

Consider a comparison

`2^a 3^b < 2^c 3^d`

inside `S_H`. Cancel the common powers of `2` and `3`. If the remaining
exponents occur on the same side, the desired inequality for `E` follows from
`E(2)=1>=0` and `x>=0`. The only nontrivial case has a pure power of `2` on one
side and a pure power of `3` on the other:

`2^m<3^n` or `3^n<2^m`.

The cancelled pure powers are no larger than the original two numbers, so
both remain at most `H`. The first comparison requires `m<n*x`, hence
`x>=m/n`; the second requires `n*x<=m`, hence `x<=m/n`. Taking the strongest
bounds proves necessity. Reversing the cancellation proves sufficiency.

Finally, `2^m<3^n` is equivalent to `m/n<log_2(3)`, and similarly on the
other side. QED.

### Continued-fraction interpretation

The endpoints are best one-sided rational approximations to `log_2(3)` inside
the rectangular exponent window

`0<=m<=floor(log_2 H)`, `1<=n<=floor(log_3 H)`.

The computed endpoints are convergents or intermediate convergents of its
continued fraction. This explains the plateaus: the interval changes only
when the exponent window reaches a better rational approximation. It also
explains why a clean uniform `C/(log H)^2` theorem is not asserted here—the
quality and spacing of successive improvements depend on the partial
quotients of this particular logarithm ratio.

The script `two_prime_rigidity.py` proves the finite reduction computationally
using exact integer comparisons. It never decides a power inequality by
floating-point logarithms.

## 2. Exact certificates for the full arithmetic network

Let `P_N` be the primes at most `N`. For `1<=n<=N`, write

`v(n)=(v_p(n))_(p in P_N)`

for the prime-exponent vector, and put

`a_n=v(n)-v(n+1)`.

For a prime-weight vector `w`, the inequality `E(n)<=E(n+1)` is exactly

`a_n dot w <= 0`.                                            (1)

### Theorem B (rational rigidity certificates)

Suppose nonnegative rational numbers `y_n` satisfy

`sum_n y_n a_n = L e_2-e_3`.                                (2)

Then every `w` obeying (1) satisfies

`E(3)>=L E(2)`.

Similarly, if

`sum_n y_n a_n = e_3-U e_2`,                                (3)

then every such `w` satisfies

`E(3)<=U E(2)`.

Conversely, every homogeneous linear inequality valid on this finite
polyhedral cone has a nonnegative real representation of this kind; when the
data and target are rational, a rational representation exists.

#### Proof

Multiply (1) by `y_n>=0` and sum. Equation (2) gives

`L E(2)-E(3)<=0`,

which is the lower bound. Equation (3) proves the upper bound identically. The
converse is the finite-dimensional Farkas lemma applied to the cone cut out by
the rows `a_n`. Rational polyhedral elimination supplies rational
coefficients. QED.

The auxiliary prime coordinates cancel exactly in (2) and (3). This is the
precise content of a **rigidity backbone**: a small collection of nearby
factorization comparisons transports order information through many primes
and returns with a net relation involving only `2` and `3`.

### A fully visible certificate at `N=100`

The lower certificate is

`(a_62+a_68+a_80+a_84+a_92)/7 = (11/7)e_2-e_3`.

Thus the five true inequalities

`E(62)<=E(63)`, `E(68)<=E(69)`, `E(80)<=E(81)`,

`E(84)<=E(85)`, `E(92)<=E(93)`

prove

`E(3)>=(11/7)E(2)`.

The upper certificate is even shorter:

`(a_27+a_63)/5 = e_3-(8/5)e_2`.

Indeed,

`27=3^3`, `28=2^2*7`, `63=3^2*7`, `64=2^6`,

so the prime `7` cancels and the two inequalities prove

`E(3)<=(8/5)E(2)`.

No optimization software is needed to check either identity.

## 3. Scaling experiment

The table compares the exact two-prime interval with the rationally certified
full interval. “Gain” is the ratio of their widths. `N W_N` is included as a
first test of the candidate scale `W_N=N^(-1+o(1))`.

| `N` | two-prime width | full certified interval | full width | support `(lower,upper)` | gain | `N W_N` |
|---:|---:|---:|---:|---:|---:|---:|
| 30 | `1/2` | `[3/2,5/3]` | `1/6` | `(1,2)` | 3.00 | 5.000 |
| 100 | `1/6` | `[11/7,8/5]` | `1/35` | `(5,2)` | 5.83 | 2.857 |
| 300 | `1/10` | `[49/31,27/17]` | `4/527` | `(6,8)` | 13.2 | 2.277 |
| 1,000 | `1/10` | `[621/392,157/99]` | `65/38808` | `(12,9)` | 59.7 | 1.675 |
| 3,000 | `1/35` | `[1580/997,21239/13398]` | `6443/13357806` | `(20,21)` | 59.2 | 1.447 |
| 10,000 | `1/35` | `[24555/15493,4679/2952]` | `5387/45735336` | `(18,19)` | 243 | 1.178 |
| 30,000 | `1/35` | `[54847/34605,324840/204949]` | `250397/7092260145` | `(26,26)` | 809 | 1.059 |
| 100,000 | `1/35` | `[1724290/1087909,3811017/2404477]` | `24047123/2615852168593` | `(42,38)` | 3,108 | 0.919 |

Every full-model entry in the table has an exactly verified dual certificate.
The floating-point solver is used only to discover a sparse support. The
certificate multipliers are then solved again from the integer exponent
matrix over `Fraction`, and the final vector identity is checked exactly.

These certificates rigorously prove the displayed bounds. The assertion that
each is the exact finite-LP optimum still uses agreement with the numerical
primal optimum; a fully exact optimality proof would additionally record an
exact primal witness. This distinction does not affect the validity of the
certified intervals or the reported upper bounds on their widths.

## 4. What the evidence supports—and what it does not

### Established here

- All finite comparisons in the two-prime monoid reduce exactly to pure-power
  comparisons.
- Every displayed full-model bound follows from an exact nonnegative rational
  identity.
- Auxiliary primes produce a large quantitative improvement over the
  two-prime model at the tested cutoffs.
- Sparse backbones exist: 80 comparisons suffice for both sides together at
  `N=100000`, versus `99999` available adjacent inequalities.

### Sound hypotheses suggested by the data

**H1 — near-reciprocal width.** If `W_N` denotes the optimal full interval
width, then

`W_N=N^(-1+o(1))`.

The eight points are consistent with this, but they are nowhere near an
asymptotic regime proof.

**H2 — sparse certificates.** There are endpoint certificates with support
size `N^o(1)`, perhaps polylogarithmic in `N`.

The observed support grows from single digits to roughly forty. A solver's
basic solution does not prove a general support law.

**H3 — cancellation, not merely smoothness, drives the gain.** The decisive
object is a positive circuit in the adjacent-factorization hypergraph whose
auxiliary prime coordinates cancel. Smooth adjacent pairs may help, but the
certificate as a whole is more informative than any one pair.

### Not established

- no asymptotic formula for `W_N`;
- no proved uniform square-log rate in the two-prime model;
- no connection to the zeros of zeta beyond broad arithmetic motivation;
- no claim that the certificate hypergraph supplies a canonical physical
  metric or literal geometry of spacetime.

## 5. Reproduction

With the SciPy environment used in this workspace:

```text
python arithmetic_acceleration.py \
  --limits 30 100 300 1000 3000 10000 30000 100000

python exact_rigidity_certificates.py \
  --limits 100 1000 10000 30000 100000

python3 two_prime_rigidity.py
```

The `100000` extraction takes materially longer than the smaller runs.

## 6. Next mathematical tests

1. Produce exact primal witnesses as well as dual certificates, making exact
   finite optimality independently checkable.
2. Compute certificate-support statistics: smoothness, largest prime factor,
   graph diameter, repeated primes, and cancellation depth.
3. Replace the generic LP by a column-generation or network algorithm capable
   of reaching much larger `N`.
4. Test other targets `E(p)/E(2)` and look for uniformity in `p`.
5. Seek upper and lower constructions for `W_N` before attempting a precise
   asymptotic conjecture.
6. Relate two-prime plateaus to explicit continued-fraction data, keeping
   unconditional finite statements separate from unproved information about
   partial quotients of `log_2(3)`.
