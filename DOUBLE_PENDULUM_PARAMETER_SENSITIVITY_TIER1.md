# Analytic parameter sensitivities for the active double-pendulum protocols

## Result and evidence boundary

The module `oig_double_pendulum_parameter_sensitivity.py` replaces the
finite-difference discovery derivative for the two active protocols by an
analytic inhomogeneous sensitivity equation in the source coordinates

\[
u=\log(m_2/m_1),\qquad v=\log(l_2/l_1).
\]

At the normalized base point \((u,v)=(0,0)\), the refined Tier-1 responses
are

| active protocol | \(\partial_u y\) | \(\partial_v y\) |
|---|---:|---:|
| launch A, \(y=\theta_2\), \(\tau=1\) | 0.0845025509351 | -0.454351245129 |
| launch B, \(y=\nu_1\), \(\tau=5/4\) | 0.469054738020 | 0.00414012202747 |

Here \(\nu_1=\sqrt{l_1/g}\,\omega_1\), so the second row is exactly the
declared `scaled_omega_1` sensor in the protocol engine. These values agree
with the earlier finite-difference discovery record while removing finite
differencing from the selected response calculation.

This remains **Tier-1 numerical evidence**. The parameter derivative of the
vector field is analytic, but the state and sensitivity trajectories are
ordinary floating-point DOP853 integrations. Neither trajectory is an outward
enclosure, and this result does not prove that an exact nonlinear response lies
in any rational response box.

## Dimensionless quotient and fixed-time convention

Use the clock and velocity coordinates

\[
\tau=t\sqrt{g/l_1},\qquad
\nu_i=\frac{d\theta_i}{d\tau}
     =\omega_i\sqrt{l_1/g}.
\]

Writing \(r=e^u=m_2/m_1\), \(\rho=e^v=l_2/l_1\), and
\(\delta=\theta_1-\theta_2\), division by the common mechanical scale gives

\[
M=
\begin{pmatrix}
1+r&r\rho\cos\delta\\
r\rho\cos\delta&r\rho^2
\end{pmatrix},
\]

\[
b=
\begin{pmatrix}
-r\rho\sin\delta\,\nu_2^2-(1+r)\sin\theta_1\\
r\rho\sin\delta\,\nu_1^2-r\rho\sin\theta_2
\end{pmatrix},
\qquad Ma=b.
\]

Thus the dimensionless state

\[
z=(\theta_1,\theta_2,\nu_1,\nu_2)
\]

obeys \(z'=F(z;u,v)=(\nu_1,\nu_2,a_1,a_2)\). The canonical representative
used by the implementation is

\[
m_1=l_1=g=1,\qquad m_2=e^u,\qquad l_2=e^v.
\]

Every protocol endpoint is fixed in \(\tau\), not in unscaled laboratory
time. Consequently there is no moving-endpoint term in \(D_{(u,v)}y\). The
physical implementation of the same protocol uses

\[
t=\tau\sqrt{l_1/g}
\]

and converts angular velocity back with
\(\nu=\omega\sqrt{l_1/g}\). A protocol that instead fixes an unscaled
laboratory time would be a different experiment and would require an endpoint
derivative.

## Analytic parameter forcing

For either source coordinate \(p\in\{u,v\}\), differentiating \(Ma=b\)
gives

\[
\partial_p a
=M^{-1}\left(\partial_p b-(\partial_p M)a\right).
\]

The required matrices are

\[
M_u=
\begin{pmatrix}
r&r\rho\cos\delta\\
r\rho\cos\delta&r\rho^2
\end{pmatrix},
\qquad
M_v=
\begin{pmatrix}
0&r\rho\cos\delta\\
r\rho\cos\delta&2r\rho^2
\end{pmatrix},
\]

and

\[
b_u=
\begin{pmatrix}
-r\rho\sin\delta\,\nu_2^2-r\sin\theta_1\\
r\rho\sin\delta\,\nu_1^2-r\rho\sin\theta_2
\end{pmatrix},
\]

\[
b_v=
\begin{pmatrix}
-r\rho\sin\delta\,\nu_2^2\\
r\rho\sin\delta\,\nu_1^2-r\rho\sin\theta_2
\end{pmatrix}.
\]

For the fixed launches used here,

\[
S(\tau)=D_{(u,v)}z(\tau)
\]

therefore solves

\[
S'=D_zF\,S+D_{(u,v)}F,
\qquad S(0)=0_{4\times2}.
\]

The scalar response is the appropriate row of \(S\): row two for the
`theta_2` protocol and row three for the dimensionless `scaled_omega_1`
protocol.

## Common-mass blindness

Under a common mass rescaling

\[
(m_1,m_2)\mapsto(c m_1,c m_2),\qquad c>0,
\]

both the physical mass matrix and forcing vector are multiplied by \(c\).
Hence

\[
(cM)^{-1}(cb)=M^{-1}b
\]

and the response in the \(\log c\) direction is structurally zero. This is an
exact algebraic identity, not a numerical observation. The two-dimensional
source space is therefore the quotient by this blind common-mass direction.

As an implementation control, the report also integrates physical
representatives with common mass scales 0.2 and 5, multiple choices of
\((l_1,g)\), and a simultaneous change of all three scales. After the declared
time and velocity conversions, all final \(\tau\)-states agree to a maximum
absolute discrepancy of

\[
1.33\times10^{-15}.
\]

This physical-similarity audit checks the code convention; it is not needed
to establish the common-mass algebraic identity.

## Independent numerical checks

The focused test suite performs the following checks.

1. It compares the analytic \(D_{(u,v)}F\) with centered differences of the
   independently evaluated vector field at three nonlinear states and five
   decreasing steps. The discrepancies decrease at the expected second-order
   rate and reach below \(3\times10^{-9}\).
2. It integrates the analytic inhomogeneous sensitivity for the two active
   protocols and compares it with independently integrated centered flow
   differences at steps \(8,4,2,1\times10^{-4}\).
3. It compares the analytic response under the standard and refined solver
   settings. The maximum discrepancies are \(2.22\times10^{-16}\) for launch
   A and \(2.30\times10^{-15}\) for launch B.
4. At the smallest finite-difference step, the maximum response discrepancies
   are \(5.04\times10^{-10}\) and \(7.34\times10^{-9}\), respectively.
5. It checks the common-mass vector-field identity directly and checks the
   physical-to-dimensionless similarity transform for both active protocols.
6. It strictly recomputes the JSON report and rejects a modified analytic
   response. That verifier explicitly returns false for outward validation and
   exact response-box membership.

The largest sampled scaled energy drift across the canonical report is
\(8.89\times10^{-16}\).

## Reproduction

Generate the canonical report:

```bash
python oig_double_pendulum_parameter_sensitivity.py \
  --output artifacts/double_pendulum_parameter_sensitivity_tier1.json
```

Recompute and strictly verify it:

```bash
python oig_double_pendulum_parameter_sensitivity.py \
  --verify artifacts/double_pendulum_parameter_sensitivity_tier1.json
```

Run the focused tests:

```bash
python -m unittest -v test_oig_double_pendulum_parameter_sensitivity.py
```

The artifact is
`artifacts/double_pendulum_parameter_sensitivity_tier1.json`.

## Transfer obligation and its discharge

This Tier-1 artifact deliberately retains false outward-validation and
box-membership flags. Its next proof obligation was an outward integration of
\(z(\tau)\) and \(S(\tau)\) at \(\tau=1\) and \(\tau=5/4\). That separate
obligation is now discharged by
[DOUBLE_PENDULUM_VALIDATED_TRANSFER_TIER2.md](DOUBLE_PENDULUM_VALIDATED_TRANSFER_TIER2.md),
which uses Arb Picard--Taylor tubes and composes the two active enclosures with
the exact OIG box theorem. The separation is intentional: this report remains
a numerical derivation audit, while the companion carries the outward proof.
