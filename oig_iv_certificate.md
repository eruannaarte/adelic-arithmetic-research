# Operational Information Geometry IV: outward-rounded finite-grid certificate

- **Research and implementation:** Codex (OpenAI)
- **Originating direction and research environment:** TGN's human founder
- **Date:** 14 August 2026
- **Status:** computer-assisted adjacent theorem target; not peer reviewed

## Result

The positive multiscale response design in Operational Information Geometry IV
can be upgraded from a floating audit to a rigorous finite-grid bracket.  For
the declared 120 candidate times, use the rational tangent basis

\[
 E=(e_0-e_5,\ldots,e_4-e_5),\qquad
 Q=E^{\mathsf T}E=
 \begin{pmatrix}
 2&1&1&1&1\\1&2&1&1&1\\1&1&2&1&1\\
 1&1&1&2&1\\1&1&1&1&2
 \end{pmatrix}.
\]

The matrix \(Q\) is the Euclidean metric inherited from the probability
simplex.  Let

\[
 A_i=R_E(t_i)^{\mathsf T}R_E(t_i)
\]

and let \(z_*\) be the optimum of

\[
 \max_{w_i\geq0,\,\sum_iw_i=1}
 \lambda_{\min}\!\left(\sum_iw_iA_i,Q\right),
\]

where the last expression is the smallest generalized eigenvalue.  This is
exactly the Stage IV Euclidean E-criterion: changing from \(E\) to an
orthonormal Helmert basis converts \(Q\) to the identity by congruence.

The certificate proves

\[
 \boxed{4.982412\times10^{-9}\ \leq z_*
        \leq 4.982942\times10^{-9}}.
\]

The relative bracket width is \(1.063742\times10^{-4}\), and the certified
primal is at least \(0.999893637\) of the rational dual upper bound.  The same
bracket is certified for both:

1. the exact algebraic grid \(t_i=10^{-3+4i/119}\); and
2. the exact dyadic-rational values of the binary64 array returned by the
   original `numpy.geomspace(0.001, 10.0, 120)` call.

Certifying both versions removes an otherwise easy-to-miss ambiguity between a
mathematically declared geometric grid and its executable floating
representation.

## Exact model and primal witness

The certificate constructs the model independently of the Stage IV floating
implementation.  With \(P_6\) the integer path Laplacian, its exact generator
is

\[
 L_\to=P_6\otimes I+
 \operatorname{diag}\!\left(1,1+\frac4{25},\ldots,1+\frac{20}{25}\right)
 \otimes P_6.
\]

This is exactly the Stage IV choice \(g=4/5\) and
\(D_A=\operatorname{diag}(0,1/5,\ldots,1)\).  The response uses the complete
\(B\)-marginal and the rational difference intervention \(E\) on \(A\), with
the target initially at state zero.  Consequently every generator,
measurement, intervention, and source-metric entry is rational.  Only the
declared times and their matrix exponentials require transcendental enclosure.

The feasible primal weights have denominator 4096:

| zero-based grid index | numerator |
|---:|---:|
| 62 | 963 |
| 76 | 71 |
| 77 | 669 |
| 87 | 1289 |
| 105 | 294 |
| 106 | 810 |

The numerators are positive and sum exactly to 4096.  Arb ball arithmetic
encloses every entry of the resulting Gram matrix \(G\).  For the exact
rational number

\[
 z_L=\frac{1245603}{250000000000000}=4.982412\times10^{-9},
\]

the five leading principal minors of \(G-z_LQ\) are certified to exceed,
respectively,

\[
 10^{-2},\quad7\times10^{-8},\quad10^{-13},\quad
 4\times10^{-25},\quad10^{-40}.
\]

Sylvester's criterion therefore proves \(G-z_LQ\succ0\), giving the primal
lower bound without trusting a floating eigensolver.

## Exact rational dual witness

Let

\[
B=\begin{pmatrix}
-83192408875&105456840882\\
213863105956&-399443523170\\
-118297442349&672776519441\\
-185640175907&-579962301934\\
292803378790&218679629676
\end{pmatrix}
\]

and

\[
 S=\operatorname{tr}(BB^{\mathsf T}Q)
   =1208925819615549701407998,
 \qquad Z=\frac{BB^{\mathsf T}}S.
\]

This representation proves \(Z\succeq0\) and
\(\operatorname{tr}(ZQ)=1\) by exact integer arithmetic.  It avoids the delicate
step of trying to certify rounded floating eigenvectors.  Outward ball
evaluation verifies all 120 inequalities

\[
 \operatorname{tr}(ZA_i)<
 \mu_U=\frac{2491471}{500000000000000}
       =4.982942\times10^{-9}.
\]

Every constraint has certified slack greater than \(8\times10^{-16}\).  The
closest constraint is grid index 62; on the canonical grid its enclosed
sensitivity is approximately \(4.9829411603\times10^{-9}\).

For any feasible design \(w\), set \(G_w=\sum_iw_iA_i\) and
\(\lambda=\lambda_{\min}(G_w,Q)\).  Then
\(G_w-\lambda Q\succeq0\).  Positivity of \(Z\) and its exact metric-trace
normalization give

\[
 \lambda
 =\lambda\operatorname{tr}(ZQ)
 \leq\operatorname{tr}(ZG_w)
 \leq\max_i\operatorname{tr}(ZA_i)<\mu_U.
\]

This proves the dual half of the bracket.

## Outward rounding and error ledger

The checker uses `python-flint`'s Arb real-ball arithmetic at 192-bit working
precision.  Model coefficients are inserted as exact rationals.  Helmert square
roots are avoided entirely: the injection \(E\), metric \(Q\), and dual witness
are rational.  Exact algebraic grid times, matrix exponentials, response
products, principal minors, and dual sensitivities are propagated as enclosing
balls.  Proof decisions use only strict comparisons between those balls and
exact rational thresholds; printed midpoints are never used to decide a claim.
The enclosure method is the midpoint-radius arithmetic described by Fredrik
Johansson, “Arb: Efficient Arbitrary-Precision Midpoint-Radius Interval
Arithmetic,” *IEEE Transactions on Computers* 66 (2017), 1281--1292,
<https://doi.org/10.1109/TC.2017.2690633>.

The executable requires each recorded time, response, information-matrix,
weighted-Gram, determinant, and dual-sensitivity radius to be strictly below
the exact cap \(10^{-54}\).  In the reference run the largest information-entry
radius is about \(5.14\times10^{-57}\), and the closest dual constraint retains
about \(8.40\times10^{-16}\) of slack.  Thus the declared rational margins are
many orders of magnitude wider than the numerical enclosures.

## Reproduction

Install the two dependencies in `oig_iv_certificate_requirements.txt`, then
run:

```sh
python oig_iv_certificate.py
python -m unittest -v test_oig_iv_certificate.py
```

The command emits a JSON proof ledger, including every principal-minor
interval, both grid results, exact rational bounds, exact witness data, radius
audits, and the SHA-256 digest
`1ba037c6f66f515a0cb3513fb5b177e5f74c0eeb8d0f75778511f7f052dec00e`
that freezes the 120 newline-separated binary64 hexadecimal time values.

## Scope and limitations

- This proves optimality bounds only over each declared set of 120 times.  It
  does not upper-bound designs using arbitrary continuum times.
- It certifies the fixed six-weight primal and fixed rational dual witness; it
  does not certify the floating optimizer that originally discovered them.
- Arb provides a rigorous numerical enclosure conditional on the correctness
  of the Arb/FLINT implementation and the checker.  This is a reproducible
  computer-assisted proof, not a derivation checked in a formal proof
  assistant.
- The \(10^{-54}\) cap measures numerical enclosure radii only.  It is not a
  model-error, sampling-error, or physical-uncertainty bound.
- The certificate does not yet provide the proposed noise-aware test separating
  an exact zero response channel from an epsilon-weak one.
- All conceptual limitations of the finite linear Markov toy model and its
  declared tensor partition remain in force.
