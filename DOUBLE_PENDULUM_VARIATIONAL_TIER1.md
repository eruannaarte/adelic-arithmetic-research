# Tier-1 variational layer for the Double-Pendulum Operational Atlas

## Result and scope

The module `double_pendulum_variational.py` integrates the state

\[
z=(\theta_1,\theta_2,\omega_1,\omega_2)
\]

together with the initial-state tangent matrix

\[
\Phi(t)=D_{z_0}\varphi_t(z_0),
\qquad
\dot\Phi=Df(z(t))\Phi,
\qquad
\Phi(t_0)=I_4.
\]

It then constructs the local response and pullback information Gram for a
declared finite observation schedule, linear phase sensor, output precision,
source injection, and source metric. This distinguishes the full four-state
source from the two-angle atlas slice.

This is **Tier-1 numerical evidence**. DOP853 integration, energy auditing,
analytic identities, and finite-difference convergence strongly test the
implementation, but do not provide an outward enclosure of the exact flow or
its derivative. Exact OIG use therefore requires a later validated transfer
that encloses the response matrix.

## Analytic vector-field derivative

Write the acceleration equation as

\[
M(q)a=f(q,\omega).
\]

For any state coordinate \(x_j\), differentiation gives

\[
\frac{\partial a}{\partial x_j}
=M(q)^{-1}
\left(
\frac{\partial f}{\partial x_j}
-\frac{\partial M}{\partial x_j}a
\right).
\]

This form reuses the positive-definite mass matrix and avoids a long expanded
quotient derivative. The implementation evaluates every derivative of
\(M\) and \(f\) analytically, then solves the same two-by-two mass system as
the base dynamics.

## Seam-free observation response

For a source coordinate \(u\) injected into initial state by

\[
J=D_u z_0,
\]

and observation

\[
\chi(z)=
(\sin\theta_1,\cos\theta_1,
  \sin\theta_2,\cos\theta_2,
  \omega_1/s_\omega,\omega_2/s_\omega),
\]

and a declared linear sensor \(C\), the response block at sample time \(t_k\)
is

\[
R_k=C\,D\chi(z(t_k))\,\Phi(t_k)J.
\]

For the atlas slice \(u=q=(\theta_1(0),\theta_2(0))\),

\[
J_q=
\begin{pmatrix}
1&0\\
0&1\\
0&0\\
0&0
\end{pmatrix}.
\]

The default injection is \(I_4\), so full-state recovery remains available,
but source metrics must have the same dimension as the declared injection.

Stacking the selected times gives \(R\). With output precision \(W\succ0\)
and source metric \(S\succ0\), the local operational information is

\[
G=R^TWR.
\]

The reported gains are

\[
\sigma_j=\sqrt{\lambda_j(G,S)}.
\]

The weakest gain measures local identifiability only for the declared finite
protocol; the strongest gain measures its largest local output amplification.
Neither is an infinite-time Lyapunov exponent.

## Independent controls

`test_double_pendulum_variational.py` checks:

1. the analytic vector-field Jacobian against five centred-difference scales
   at three nonlinear states;
2. the phase-observation Jacobian against the atlas observation implementation;
3. the exact small-angle normal frequencies at equilibrium;
4. the integrated tangent against a three-scale centred difference of the
   independently integrated nonlinear flow;
5. \(\Phi(t_0)=I\) and the equilibrium identity
   \(\Phi(t)=\exp(Df(0)t)\);
6. tangent-flow composition across two time segments;
7. agreement of augmented and state-only integration;
8. the analytically known time-zero information Gram;
9. invariance of information under a simultaneous output-coordinate and
   precision transformation; and
10. a scalar-sensor case with genuine blind directions;
11. the exact two-angle slice Gram at launch; and
12. rejection of rank-deficient or dimensionally inconsistent source
    injections.

The focused dynamics, atlas, and variational suites currently pass together.

## Next transfer obligation

The next rigorous layer must outwardly enclose both \(z(t)\) and \(\Phi(t)\),
or directly enclose every response block \(R_k\). Only then can rational
centres and radii be supplied to `EnclosedProtocol` with a proved physical
containment premise. In chaotic regions this enclosure may become too wide;
the required result there is a shorter certified horizon or `unresolved`, not
an optimistic point estimate.
