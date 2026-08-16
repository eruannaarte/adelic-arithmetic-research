# Double-Pendulum Validated Transfer: Two Active Protocols

## Result

The conditional response-box theorem used by the double-pendulum protocol
engine now has an outward physical transfer at the nominal parameter point.
For

\[
u=\log(m_2/m_1)=0,\qquad v=\log(l_2/l_1)=0,
\]

the exact parameter-response rows of the two protocols carrying nonzero design
weight are rigorously contained in their already-declared rational boxes.
Composing this ODE containment result with the exact rational box theorem gives

\[
\lambda_{\min}(G_{\rm physical})\ge
\frac{195932905640268820789}{2500000000000000000000}
\approx 0.0783731622561>0.
\]

Here and in the executable schema, **physical** means the exact response of the
declared nonlinear dimensionless double-pendulum equations. It does not mean
that those equations adequately model nature or a particular apparatus. The
result certifies neither measured calibration nor hardware. Subject to that
definition, this is a physical positive-floor certificate for the stated
two-protocol model experiment at the nominal point. It is not a claim about a
parameter neighbourhood, the other five candidate protocols, or
seven-candidate optimality.

## ODE and differentiated flow

The dimensionless representative is

\[
m_1=l_1=g=1,\qquad m_2=e^u,\qquad l_2=e^v.
\]

The four state variables are

\[
z=(\theta_1,\theta_2,\omega_1,\omega_2).
\]

Rather than finite-differencing two numerical trajectories, the validated
solver integrates the twelve-dimensional autonomous system

\[
Y=(z,\partial_u z,\partial_v z),
\]

obtained by exact forward automatic differentiation of the Euler--Lagrange
vector field. Nested automatic differentiation then evaluates the full
Jacobian of this augmented field over interval boxes. All scalar operations,
including trigonometric functions, exponentials, and division by the mass
determinant, are outward Arb ball operations.

## Accepted-step theorem

Let \(X_0\) contain the exact augmented initial value on a step \([0,h]\), and
let \(p(t)\) be the fixed dyadic-coefficient Taylor polynomial constructed by
the implementation. Define the defect

\[
r(t)=p'(t)-F(p(t)).
\]

For a proposed componentwise radius \(\rho\), form the tube

\[
B=p([0,h])+[-\rho,\rho].
\]

Outward interval automatic differentiation supplies

\[
A_{ij}\ge \sup_{y\in B}|\partial_jF_i(y)|,
\]

and an outward interval Taylor remainder calculation supplies

\[
d_i\ge\sup_{0\le t\le h}|r_i(t)|.
\]

The implementation accepts the step only when it proves, component by
component,

\[
\operatorname{rad}(X_0-p(0))+h d+hA\rho<\rho. \tag{1}
\]

As long as the exact solution remains in the tube, the mean-value theorem and
the integral equation bound its error by the left side of (1). A first-exit
argument, together with ordinary local existence and continuation on the
compact smooth tube, rules out departure during the step. The same left side
is an endpoint error radius about \(p(h)\). Thus every enclosure passed to the
next step is outward.

This proof architecture is a validated defect/Picard--Taylor method. It does
not interval-evaluate an ordinary Runge--Kutta trajectory and call the result
an enclosure.

## Taylor defect obligation

If the Taylor polynomial has degree \(q\), its construction cancels the defect
coefficients through degree \(q-1\), up to outward arithmetic balls. For every
component, the implementation computes the low coefficients at zero and the
degree-\(q\) coefficient over every possible Taylor center \(s\in[0,h]\):

\[
|r(t)|\le
\sum_{k=0}^{q-1}|[t^k]r_0|h^k
+ \sup_{s\in[0,h]}|[\xi^q]r(s+\xi)|h^q.
\]

The second coefficient is \(r^{(q)}(s)/q!\), so this is Taylor's theorem with
an outward interval remainder, not a sampled residual heuristic.

## Certified enclosures

The default proof uses 160-bit Arb arithmetic, Taylor order 8, and exact step
size \(1/100\). Launch A required at most two tube iterations per step and
launch B at most six.

For launch A, sensor \(\theta_2\), \(\tau=1\), the response enclosures have
midpoints and radius uppers

\[
(0.08450255093508893\;\pm 3.36\times10^{-13},
-0.4543512451293749\;\pm 4.28\times10^{-13}).
\]

For launch B, sensor \(\sqrt{l_1/g}\,\omega_1\), \(\tau=5/4\), they are

\[
(0.46905473801917236\;\pm 3.08\times10^{-11},
0.00414012202889391\;\pm 5.45\times10^{-11}).
\]

Each is strictly inside its exact declared interval with radius
\(101/100000=0.00101\). Rational outward endpoints are serialized in the
report; decimal values above are descriptive only and never decide
membership.

The verifier also reconstructs the exact conservative per-entry slack between
each rational outer enclosure and the nearest declared-box face. In response
order `(mass ratio, length ratio)`, the decimal descriptions are

- launch A: `(0.00100999991434, 0.00100999709657)`;
- launch B: `(0.00100998831826, 0.00100999458591)`.

The exact fractions, not these decimal renderings, appear under
`declared_box_inclusion_slack_exact`. This unused margin is an auditable budget
that could later be combined with a *separately proved* model or calibration
discrepancy. It is not itself evidence for, or a certificate of, any such
physical uncertainty.

## Exact engine interface

`validated_active_enclosed_protocols()` exports two `EnclosedProtocol` objects
only after recomputing and proving physical membership. Their centers, radii,
noise precisions, and costs are exactly the declarations already used by the
conditional engine:

- launch A / theta 2 / tau 1, cost \(1\);
- launch B / scaled omega 1 / tau \(5/4\), cost \(5/4\).

The exact design then recovers budget shares \(4589/10000\) and \(5411/10000\)
and the positive floor displayed above. This transfers the achieved fixed
mixture. It deliberately does not claim that the two ODE enclosures prove the
quality or completeness of the original seven-candidate library.

The report therefore carries explicit false scope flags for seven-candidate
selection, seven-candidate efficiency, parameter-neighbourhood uniformity,
empirical model adequacy, and hardware calibration.

## Failure and unresolved semantics

A failed tube inclusion, a nonfinite interval evaluation, a response enclosure
that is not strictly inside its rational box, or a failed exact child theorem
produces `status: unresolved` and
`physical_positive_floor_certified: false`. No fallback numerical trajectory,
finite-difference estimate, embedded pass flag, or decimal comparison can
promote that status. Export to `EnclosedProtocol` raises rather than crossing
an unresolved physical-membership boundary.

The strict verifier recomputes both the outward ODE proof and the exact
rational child. Adversarial tests alter enclosures, tube metadata, membership
fields, the exact child, and the composed floor; all such mutations are
rejected.

## Reproduction

```bash
python -m pip install -r requirements.txt
python -m unittest -v \
  test_oig_double_pendulum_validated_transfer.py \
  test_oig_double_pendulum_validated_transfer_audit.py
python oig_double_pendulum_validated_transfer.py \
  --physical-output artifacts/double_pendulum_physical_positive_floor.json
python oig_double_pendulum_validated_transfer.py \
  --verify-physical artifacts/double_pendulum_physical_positive_floor.json
```

The implementation and tests are:

- `oig_double_pendulum_validated_transfer.py`
- `test_oig_double_pendulum_validated_transfer.py`
- `test_oig_double_pendulum_validated_transfer_audit.py`
- `DOUBLE_PENDULUM_VALIDATED_TRANSFER_AUDIT.md`
