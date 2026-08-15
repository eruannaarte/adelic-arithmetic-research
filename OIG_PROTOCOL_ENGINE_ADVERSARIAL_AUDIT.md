# Adversarial audit of the OIG protocol-design engine

## Scope and standard

This is an independent audit of:

- `oig_protocol_design_engine.py`;
- `test_oig_protocol_design_engine.py`;
- `OIG_PROTOCOL_DESIGN_ENGINE.md`; and
- `oig_hidden_network_protocol_demo.py`.

The audit distinguishes an exact certificate for a **declared rational finite
instance** from a theorem transferring a continuum or physical system into
that instance.  Numerical discovery is allowed, but no floating-point result
is treated as proof.

The companion controls are in
`test_oig_protocol_engine_adversarial_controls.py`.  They reconstruct quotient,
budget, primal, and dual identities from the matrices instead of trusting
boolean report fields.

## 1. Algebra that survives audit

### 1.1 Exact observable quotient

Let \(C\) be a row basis of all responses and \(S\succ0\).  The implementation
uses

\[
 J=S^{-1}C^T(CS^{-1}C^T)^{-1},\qquad
 S_q=(CS^{-1}C^T)^{-1}.
\]

Exact rational tests verify

\[
 CJ=I,\qquad J^TSJ=S_q,\qquad R_iJC=R_i.
\]

Thus \(Jy\) is the minimum-\(S\)-cost representative and the information
forms \(J^TR_i^TW_iR_iJ\) live on precisely the common observable quotient.
The audit deliberately uses a non-diagonal \(S\), for which an ordinary
Euclidean-complement shortcut would be wrong.

### 1.2 Noise-coordinate invariance

For an invertible output-coordinate change \(R'=TR\), the information is
unchanged only when

\[
 W'=T^{-T}WT^{-1}.
\]

An exact rational control verifies

\[
 R'^TW'R'=R^TWR.
\]

The engine correctly consumes the supplied precision.  It cannot, however,
infer whether independently supplied response and covariance declarations
are physically calibrated; that remains an input obligation.

### 1.3 Cost normalization

The optimizer works with budget shares \(p_i=c_iw_i\), so

\[
 \sum_i p_i=1,\qquad
 G=\sum_i p_i A_{i,q}/c_i=\sum_iw_iA_{i,q}.
\]

Largest-remainder rationalization preserves the simplex exactly.  The audit
independently parses the returned shares and physical weights and verifies
\(\sum_i c_iw_i=1\) in `Fraction` arithmetic.

### 1.4 Generalized E-optimal primal and dual

For \(B_i=A_{i,q}/c_i\), the primal is

\[
 z_* = \max_{p\in\Delta}\lambda_{\min}
       \left(\sum_i p_iB_i,S_q\right).
\]

Any returned \(L\) satisfying

\[
 G-LS_q\succ0
\]

is a strict lower bound on the achieved design floor.  For every
\(Z\succeq0\) with \(\operatorname{tr}(S_qZ)=1\),

\[
 z_*\le \max_i\operatorname{tr}(B_iZ).
\]

The integer factor \(K\) makes

\[
 Z=KK^T/\operatorname{tr}(S_qKK^T)
\]

exactly dual feasible.  The audit reconstructs \(Z\), all sensitivities, the
design Gram, and the exact positive-definite primal shift.  The derivation and
implementation are sound.  SLSQP and Powell propose candidates only; the
exact result is a certified achieved floor and global-optimum bracket, not a
proof that the returned rational weights are an exact optimizer.

### 1.5 Exponential-time continuous-time Markov response

Under the convention \(p'(t)=-Lp(t)\), a Markov Laplacian must have zero
column sums and nonpositive off-diagonal entries.  For \(\alpha>0\),

\[
 \mathbb E[C e^{-TL}J]
 =C\alpha(\alpha I+L)^{-1}J,
 \qquad T\sim\operatorname{Exp}(\alpha).
\]

Once both the conservation and sign conditions are checked, the rational
resolvent construction is exact.  The benchmark's four-state matrix is
nonsymmetric, conservative, and has the required signs; its tangent
injection has zero column sums and satisfies \(J^TJ=S\).

## 2. Counterexamples found and corrected during audit

### 2.1 Double noise calibration

Originally the finite information already used \(W_i=\Sigma_i^{-1}\), but the
reported Gaussian error divided the resulting Mahalanobis separation by a
second `noise_sigma`.  This counted the same noise scale twice.  The second
scale has been removed: the finite floor is already whitened.

### 2.2 False zero floor after failed frame transfer

Originally, if \(L_{\rm full}-\delta<0\), the report replaced the signed form
bound by zero.  That is invalid unless \(G_{\rm sens}\succeq0\) has separately
been proved.  For example,

\[
 G_{\rm full}=0,\quad G_{\rm sens}=-1,\quad S=1
\]

satisfies a loss inequality with \(\delta>1\), but it does not have a zero
floor.  The engine now returns the signed
`transferred_form_bound_exact` and a separate positivity flag.

### 2.3 Conservation alone is not the Markov property

The matrix

\[
 L=\begin{pmatrix}-1&1\\1&-1\end{pmatrix}
\]

has zero column sums but is not a Markov Laplacian for \(p'=-Lp\).  The helper
originally accepted it.  It now rejects positive off-diagonal entries.

### 2.4 Invalid descriptive-noise parameters

`NaN` amplitude and nonintegral repetitions originally passed validation.
The interface now requires a finite positive amplitude and a positive integer
continuous-budget exposure multiplier.

### 2.5 Optimizer wording

The initial prose said the discovered mixture *maximizes* the floor.  The
exact certificate proves instead

\[
 L\le \lambda_{\min}(G,S_q)\le z_*\le U.
\]

It therefore proves efficiency at least \(L/U\) and suboptimality at most
\(U-L\).  The engine and manuscript now use bracket/near-optimal language.

## 3. Hardening completed following audit

Four originally missing layers were implemented while the audit was live.

### 3.1 Self-contained exact instance and verifier

Every report now embeds the original source metric, protocol responses,
noise precisions, costs, quotient maps, reduced information forms, exact
design Gram, and dual witness. `verify_design_report` reconstructs the
quotient, primal shift, dual sensitivities, cost budget, noise bounds, and
integer realization without rerunning the optimizer. Adversarial tests alter
the instance, primal bound, dual bound, dimension fields, theorem flags, and
integer schedule and require rejection.

### 3.2 Exact-input boundary

Binary floating inputs are rejected. Integers, `Fraction` values, and decimal
strings define the exact rational theorem instance. This makes it explicit
that irrational or interval semigroup data need a separate transfer layer.

### 3.3 Rational outward Gaussian bound

The exact floor proves the squared-separation lower bound. In addition to a
descriptive `ndtr` value, the report now includes the exact rational bound

\[
 \Phi(-d/2)
 \le \tfrac12 e^{-d^2/8}
 \le \frac{4}{8+d^2}
 \le \frac{4}{8+Na^2L}.
\]

The verifier recomputes the squared separation and rational error bound.

### 3.4 Exact integer realization

The report distinguishes a continuous approximate-design exposure from a
realizable integer schedule. It computes the least common multiple of all
physical-weight denominators, rounds the requested budget upward to a
realizable multiple, and returns exact counts. The verifier checks exposure
divisibility, integrality before conversion, each count, total cost, and the
requested-realizability flag. A tampered truncation counterexample is now a
regression test.

## 4. Remaining proof boundary

### 4.1 Finite-instance proof is not model-transfer proof

The hidden-network demo is a valid exact finite CTMC benchmark.  The Neumann
family still needs its uniform continuum-to-finite transfer attached to the
chosen sensor frames and metrics.  Likewise, candidate-library completeness,
model uncertainty, nonlinear dynamics, and adaptive design are outside this
kernel.  The manuscript currently states this boundary honestly.

### 4.2 Frame-loss records are verified in-process, not standalone

`certify_frame_loss` makes its form decision by exact rational elimination,
so the returned inequality is valid for the matrices passed to that call.
Unlike the main design report, however, its small returned record does not
embed the full/sensed Grams and metric and has no independent artifact
verifier. Attaching frame loss to an end-to-end publication certificate will
therefore require either embedding those inputs and adding a verifier or
including the frame decision inside the main self-contained report.

**Post-audit resolution:** `certify_frame_loss` now embeds the full and sensed
information forms and source metric, self-calls
`verify_frame_loss_report`, and rejects altered transfer fields. The separate
Arb response-box and Neumann matched-frame layers also attach a verified
finite-model and two-sensor transfer to the canonical physical candidate
library. Candidate-library completeness and hardware locality remain outside
the theorem.

## 5. Verdict

The quotient geometry, generalized primal/dual bounds, cost normalization,
finite form-loss inequality, and exponential-time CTMC identity are
mathematically valid for the exact rational instance actually supplied.
Adversarial controls independently reproduce those identities.

The kernel is now properly described as a **proof-producing
approximate-design component** with an independent exact verifier and an
integer realization layer. It is not yet a complete physical protocol engine:
the remaining mathematical obligation is to attach the relevant
continuum-to-finite and sensor-frame transfer theorems to each physical
candidate library. The remaining engineering obligation is to make the
standalone frame-loss record independently reconstructible when it is used as
part of such a certificate chain.
