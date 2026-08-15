# Certified protocol design for hidden stochastic networks

## Exact quotients, calibrated finite sensors, and rational E-optimal certificates

## 1. Purpose

The Operational Information Geometry programme has proved continuum response
limits, source-visibility quotients, spectral floors, and several
continuum-to-finite transfer certificates. This module assembles the first
general engine kernel that consumes a finite collection of observation
protocols and returns a proof-producing design.

The engine addresses a deliberately finite question:

> Given exact response maps, source cost, output noise, and protocol costs,
> find a strong mixture for the weakest observable source direction, certify
> its exact floor, and bound how far it can be from the global E-optimum.

The implementation is oig_protocol_design_engine.py. It does not assume that
the candidate protocols came from the Neumann benchmark. They may be finite
response maps extracted from any linearized partially observed stochastic
network, provided their declared matrices have exact rational entries.

This is an engine component, not yet the complete end-to-end application.
Continuum-to-finite transfer and completeness of a physical candidate library
remain separate proof obligations.

---

## 2. Declared experiment

Let the source parameter be \(u\in\mathbb R^d\), with positive-definite source
cost

\[
 \lVert u\rVert_S^2=u^TSu.
 \tag{2.1}
\]

Protocol \(i\) has response matrix \(R_i\), positive-definite output-noise
precision \(W_i=\Sigma_i^{-1}\), and positive cost \(c_i\). Its exact
information form is

\[
 A_i=R_i^TW_iR_i.
 \tag{2.2}
\]

Whitening is part of the declared protocol. The engine takes \(R_i,W_i\)
literally and cannot infer whether a user forgot to transform covariance
after changing sensor coordinates. A genuine coordinate rescaling must
transform both response and covariance; the exact declarations are therefore
embedded in every report for independent inspection.

If \(w_i\ge0\) denotes physical replication weight, the cost budget and
aggregate Gram are

\[
 \sum_i c_iw_i=1,
 \qquad
 G(w)=\sum_iw_iA_i.
 \tag{2.3}
\]

---

## 3. Exact removal of blind directions

Stack every row of every \(R_i\), and let \(C\) be any full-row-rank rational
basis of that row space. The common blind space is

\[
 \mathcal N=\ker C=\bigcap_i\ker R_i.
 \tag{3.1}
\]

The engine uses quotient coordinates

\[
 y=Cu.
 \tag{3.2}
\]

The cost of a quotient class must not depend on an arbitrary complement. It
is the minimum source cost among all representatives:

\[
 \lVert y\rVert_{\rm q}^2
 =\min_{Cu=y}u^TSu.
 \tag{3.3}
\]

Define

\[
 M=CS^{-1}C^T,
 \qquad
 J=S^{-1}C^TM^{-1}.
 \tag{3.4}
\]

Then \(CJ=I\), \(Jy\) is the unique minimum-cost representative, and

\[
 S_{\rm q}=J^TSJ=M^{-1}.
 \tag{3.5}
\]

Every response factors through the quotient because
\(\ker C\subseteq\ker R_i\):

\[
 R_iu=R_iJ(Cu).
 \tag{3.6}
\]

Consequently the reduced information matrices are exactly

\[
 A_{i,{\rm q}}=J^TA_iJ.
 \tag{3.7}
\]

All matrices in (3.1)--(3.7) are computed with rational row reduction and
rational inversion. No numerical rank threshold defines the theorem
quotient.

### Proposition 3.1 — quotient invariance

The generalized eigenvalues of

\[
 \left(\sum_iw_iA_{i,{\rm q}},S_{\rm q}\right)
 \tag{3.8}
\]

are invariant under a rational basis change \(C\mapsto TC\) with \(T\)
invertible. They depend only on the response equivalence relation, source
cost, noise metrics, protocol costs, and weights.

#### Proof

Changing \(C\) replaces \(y\) by \(Ty\). Both reduced information and the
quotient metric transform by the same congruence. Generalized eigenvalues are
invariant under simultaneous congruence. \(\square\)

---

## 4. The design problem

Put \(p_i=c_iw_i\), so \(p_i\ge0\) and \(\sum_ip_i=1\). The E-optimal problem
on the exact observable quotient is

\[
 z_\star=\max_{p\in\Delta}
 \lambda_{\min}\!\left(
 \sum_i p_i\frac{A_{i,{\rm q}}}{c_i},S_{\rm q}
 \right).
 \tag{4.1}
\]

Equivalently, its primal semidefinite form is

\[
 \begin{array}{ll}
 \text{maximize}&z\\
 \text{subject to}&
 \displaystyle\sum_i p_i\frac{A_{i,{\rm q}}}{c_i}-zS_{\rm q}\succeq0,\\
 &p_i\ge0,\quad\sum_ip_i=1.
 \end{array}
 \tag{4.2}
\]

The code uses floating-point optimization only to discover a candidate \(p\).
It does not assume that the local numerical search is globally correct. It
rounds \(p\) to exact rational simplex weights by an integer largest-remainder
rule, and the reported design has an exactly satisfied budget. The independent
dual bound below brackets the global optimum.

---

## 5. Exact primal and dual bounds

For the rationalized design, let

\[
 G=\sum_i p_i\frac{A_{i,{\rm q}}}{c_i}.
 \tag{5.1}
\]

### Primal lower certificate

A rational number \(L>0\) is a valid floor whenever

\[
 G-LS_{\rm q}\succ0.
 \tag{5.2}
\]

The engine verifies (5.2) by exact rational \(LDL^T\) elimination. Thus

\[
 L<\lambda_{\min}(G,S_{\rm q})\le z_\star.
 \tag{5.3}
\]

### Dual upper certificate

Let \(Z\succeq0\) satisfy

\[
 \operatorname{tr}(S_{\rm q}Z)=1.
 \tag{5.4}
\]

Then

\[
 z_\star
 \le
 U(Z):=\max_i
 \frac{\operatorname{tr}(A_{i,{\rm q}}Z)}{c_i}.
 \tag{5.5}
\]

The engine numerically discovers a lower-triangular factor and rationalizes it
to a nonzero integer matrix \(K\). It then takes

\[
 Z=\frac{KK^T}{\operatorname{tr}(S_{\rm q}KK^T)}.
 \tag{5.6}
\]

This witness is exactly positive semidefinite and satisfies (5.4) in rational
arithmetic. Therefore

\[
 \boxed{L\le z_\star\le U.}
 \tag{5.7}
\]

The numerical factor search is not trusted. Only the rationalized
factorization, exact trace normalization, and exact candidate sensitivities
decide the upper bound. The bracket can remain loose if discovery finds a
poor dual factor; validity is unaffected.

The ratio \(L/U\) is a certified lower bound on the efficiency of the returned
design relative to the unknown global optimum. Thus the engine never promotes
a local optimizer status to a theorem about exact optimal weights.

---

## 6. Certified finite-sensor loss

Suppose \(G_{\rm full}\) is a complete-output Gram and \(G_{\rm sens}\) is the
Gram retained by a finite sensor frame. The engine searches for a rational
\(\delta>0\) and proves

\[
 \delta S-(G_{\rm full}-G_{\rm sens})\succ0.
 \tag{6.1}
\]

Hence

\[
 G_{\rm sens}\succeq G_{\rm full}-\delta S.
 \tag{6.2}
\]

If an independent theorem gives

\[
 G_{\rm full}\succeq L_{\rm full}S,
 \tag{6.3}
\]

then

\[
 \boxed{
 G_{\rm sens}\succeq(L_{\rm full}-\delta)S.
 }
 \tag{6.4}
\]

This is the finite-frame transfer needed by the larger application. Merely
using at least as many scalar sensors as quotient dimensions does not prove
(6.1); the actual frame loss is certified.

---

## 7. Noise consequence

In a whitened unit-covariance Gaussian observation model, a declared quotient
displacement of exact rational amplitude \(a\), under continuous design-budget
multiplier \(N\), has squared separation at least

\[
 Na^2L.
 \tag{7.1}
\]

For equal prior probabilities, the simple-versus-simple error is bounded by

\[
 P_{\rm err}
 \le
 \Phi\!\left(-\frac{a\sqrt{NL}}{2}\right).
 \tag{7.2}
\]

The engine retains a descriptive numerical evaluation of (7.2), but also
returns the exact rational outward bound

\[
 P_{\rm err}
 \le \frac12e^{-Na^2L/8}
 \le \frac{4}{8+Na^2L}.
 \tag{7.3}
\]

The second inequality uses \(e^x\ge1+x\). Noise precision has already been
included in every \(A_i=R_i^TW_iR_i\), so introducing a second noise scale
would double-calibrate the experiment.

Approximate design weights need not be integer observation counts. The engine
therefore computes the least common multiple of the physical-weight
denominators, gives exact protocol counts for the least realizable budget not
smaller than the requested multiplier, and evaluates (7.3) again for that
integer realization. It is not a uniform
zero-versus-arbitrarily-small-channel theorem; source amplitude and the
whitened noise model are declared inputs.

---

## 8. Exact continuous-time hidden-network responses

For a finite chain with column probabilities

\[
 p(t)=e^{-tL}p(0),
 \tag{8.1}
\]

let \(T\) be independent and exponentially distributed with rate
\(\alpha>0\). Then

\[
 \mathbb E[e^{-TL}]
 =\int_0^\infty\alpha e^{-\alpha t}e^{-tL}\,dt
 =\alpha(\alpha I+L)^{-1}.
 \tag{8.2}
\]

For rational \(L\), intervention \(J\), sensor \(C\), and rate \(\alpha\),
the response

\[
 R=C\alpha(\alpha I+L)^{-1}J
 \tag{8.3}
\]

is rational. The helper exponential_time_response constructs (8.3) exactly
after verifying mass conservation and the nonpositive off-diagonal Markov
sign convention for \(p'=-Lp\). This supplies a genuine continuous-time
stochastic-network benchmark without a floating matrix exponential.

The companion oig_hidden_network_protocol_demo.py applies the engine to a
non-symmetric four-state chain, five heterogeneous sensor/time protocols,
nonuniform costs, and declared noise precisions.

---

## 9. Reproduction

```bash
python -m unittest -v \
  test_oig_protocol_design_engine.py \
  test_oig_protocol_engine_adversarial_controls.py
python oig_hidden_network_protocol_demo.py
```

The tests cover:

- exact use of output-noise precision;
- removal of a common blind direction;
- the minimum-cost quotient metric and injection;
- cost-aware E-optimal balancing;
- exact primal and dual bounds;
- certified finite-frame loss;
- exact exponential-time CTMC response; and
- rejection of all-blind and non-positive noise declarations.

Every JSON report embeds the declared \(S,R_i,W_i,c_i\), quotient maps,
reduced information matrices, rationalized design Gram, and dual witness.
The public verify_design_report routine reconstructs all exact theorem fields
without rerunning numerical optimization and rejects tampering.
Finite-frame records likewise embed both information forms and their source
metric; verify_frame_loss_report independently reconstructs the exact
metric-relative loss inequality and rejects altered transfer fields.

---

## 10. What is proved and what remains

### Proved by this engine kernel

1. Exact common-null removal for rational finite response maps.
2. Exact descent of a positive rational source cost to the quotient.
3. Exact incorporation of rational output-noise precision.
4. Exact budget feasibility of the returned rational design.
5. An exact generalized-information primal lower certificate.
6. An exact feasible-dual upper certificate.
7. An exact metric-relative finite-sensor loss certificate.
8. Exact exponential-time responses for rational finite CTMCs.
9. An independently reconstructible report and exact rational Gaussian-error
   upper bound.

### Not yet proved by this kernel

1. That a supplied finite response accurately represents a continuum or
   infinite-resolution model.
2. That the candidate protocols exhaust a physical experiment class.
3. A general interval-input API for irrational semigroup responses and
   natural discrete \(H^1\) costs.
4. A tight dual bracket for every candidate library.
5. Nonlinear, model-uncertain, or adaptive sequential protocol design.

The companion resolution-aware theorem now addresses item 1 for the canonical
two-port benchmark. The response-box layer and matched-frame application
attach that transfer to finite sensors: at \(n=345\), two rational matched
linear statistics compress 172 active modal outputs with an independently
verified positive physical floor. Local or hardware-constrained sensor
synthesis remains open.

Binary floating matrix declarations are rejected in proof mode. Decimal
strings denote exact decimal rationals; irrational or interval-valued physical
responses require the future Arb input layer rather than silent
rationalization.
