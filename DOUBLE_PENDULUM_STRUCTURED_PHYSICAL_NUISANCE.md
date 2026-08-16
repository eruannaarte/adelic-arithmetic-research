# Structured physical nuisance for the two active double-pendulum protocols

## Result in one sentence

The present two active protocols are sufficient for the transferred nominal
two-parameter response, but they are **not sufficient for a positive
two-source floor after any nonzero unrestricted shared nuisance is introduced**;
independently refitted launch-preparation errors, or separate calibration of
the two different sensors, remove every nonzero query.

This is a dimension obstruction, not an adverse numerical accident. The
existing two observations are scalar. Profiling one shared nuisance leaves at
most one observation dimension; profiling a nonzero local nuisance separately
in each scalar observation leaves none.

Companion executable:

- `oig_double_pendulum_structured_nuisance.py`
- `test_oig_double_pendulum_structured_nuisance.py`
- `artifacts/double_pendulum_structured_physical_nuisance.json`

The executable supplies Tier-1 variational controls, rational point
declarations, exact query-engine children, exact structured-nuisance children,
and a verifier that does not replay or claim to validate the ODE.

## 1. Fixed physical-source response

At the normalized point

\[
  m_1=l_1=g=1,\qquad m_2=e^u,\qquad l_2=e^v,
\]

the source coordinates are

\[
  u=\log(m_2/m_1),\qquad v=\log(l_2/l_1).
\]

The two active scalar protocols are:

1. launch A, sensor \(\theta_2\), terminal time \(\tau=1\);
2. launch B, sensor \(\nu_1=\sqrt{l_1/g}\,\omega_1\), terminal time
   \(\tau=5/4\).

Their declared rational response centre is

\[
H=
\begin{pmatrix}
265/3136 & -4041/8894\\
2357/5025 & 13/3140
\end{pmatrix},
\qquad
\det H={3131448222341\over14669578604800}>0.
\]

The earlier pointwise validated transfer proves that the nonlinear
parameter-response rows lie in declared rational boxes around this centre. In
this note, exact nuisance children use the centre as a fixed rational matrix.
They do not yet combine response-box uncertainty with nuisance-column
uncertainty.

Common multiplication of both masses is still an exact blind direction of the
dimensionless mechanics. It was removed before forming the two-dimensional
source model and is not counted again as experimental nuisance.

## 2. Minimal local nuisance model

For protocol \(i\), let \(z_i(\tau)\) be its nominal trajectory, let
\(h_i\) select its scalar sensor, and let

\[
  \Phi_i(\tau)=D_{z_i(0)}z_i(\tau)
\]

be the initial-state tangent. The local observation model is

\[
 \delta y_i
 =H_i\,\delta x+c_i\epsilon+a_i\kappa
  +p_i\,\delta q_i+\eta_i,
 \qquad \delta x=(\delta u,\delta v)^T.
\]

The nuisance semantics are deliberately explicit.

### 2.1 Shared clock dilation

Define the clock parameter by

\[
  \tau_i^{\rm actual}=e^\epsilon\tau_i.
\]

Dimensionless sensor units are held fixed; only the sampling time moves. The
analytic column is therefore

\[
 c_i=\left.{d\over d\epsilon}
 h_i(z_i(e^\epsilon\tau_i))\right|_{\epsilon=0}
 =\tau_i {d y_i\over d\tau}.
\]

Consequently,

- for the \(\theta_2\) sensor, \(c_A=\tau_A\nu_2(\tau_A)\);
- for the \(\nu_1\) sensor, \(c_B=\tau_B\dot\nu_1(\tau_B)\).

A convention in which the same faulty clock also defines the velocity unit
would produce an additional known term. That is a different nuisance model
and must not be silently substituted for this scheduling-dilation convention.

### 2.2 Multiplicative calibration

For a small log gain,

\[
 y_i^{\rm measured}=e^\kappa y_i,
 \qquad a_i={d y_i^{\rm measured}\over d\kappa}\bigg|_0=y_i.
\]

One common \(\kappa\) across both channels is retained as an optimistic
common-electronics control. The active channels are physically different
(angle and angular velocity), so the more conservative model assigns one gain
to each sensor. Because each sensor occurs in only one present scalar
protocol, sensor-specific calibration is algebraically the same obstruction
as independently refitting one nonzero nuisance in each observation.

### 2.3 Per-launch preparation

The minimal preparation slice allows independent initial-angle errors at each
launch while keeping initial velocities at zero. With

\[
 J_\theta=(e_{\theta_1},e_{\theta_2}),
\]

the preparation row is

\[
 p_i=D_{z_i(0)}y_i\,J_\theta
     =e_{h_i}^{T}\Phi_i(\tau_i)J_\theta.
\]

The two coefficient vectors \(\delta q_A\) and \(\delta q_B\) are refitted
independently. Allowing initial-velocity preparation errors would only enlarge
these local nuisance spaces, so the angle-only model is already the decisive
control.

## 3. Tier-1 evaluation

Joint state/tangent integration with DOP853, an enabled sampled-energy gate,
and coarse/fine refinement gives approximately

| protocol | output / gain column \(a_i\) | clock column \(c_i\) | angle-preparation row \(p_i\) |
|---|---:|---:|---:|
| A: \(\theta_2,\tau=1\) | 0.0960474430 | 1.0515538244 | (-0.2207123358, 0.9617970350) |
| B: \(\nu_1,\tau=5/4\) | 1.1179269426 | 0.5817741920 | (-0.9763354241, 0.2006586479) |

The largest coarse/fine relative discrepancy among state, tangent, and the
assembled nuisance entries is below \(5\times10^{-15}\) in this run. Every
displayed preparation row is nonzero. The two shared columns

\[
 B_{c,a}=\begin{pmatrix}c_A&a_A\\c_B&a_B\end{pmatrix}
\]

are numerically far from dependent (determinant approximately 1.11968).

These are excellent discovery and implementation checks, but they are not
outward enclosures. The executable rationalizes the fine values solely to
exercise exact finite-linear theorem engines. No rationalized value is
promoted to a physical ODE claim.

## 4. Exact rank and confounding theorem

### Theorem 4.1 — one shared scalar nuisance

Let \(H\in\mathbb R^{2\times2}\) be invertible and let a nonzero shared
nuisance column be \(b\in\mathbb R^2\). For any positive output metric, let
\(P_b\) be the corresponding nuisance-removing projector. Then

\[
 \operatorname{rank}(P_bH)=1.
\]

Hence the profiled information Gram

\[
 G_b=H^TP_b^TWP_bH
\]

has a zero smallest generalized eigenvalue. There is no positive full
two-source floor.

The exact lost source direction is

\[
 x_b=H^{-1}b,
\]

because \(Hx_b=b\) is indistinguishable from a nuisance change. If
\(w^Tb=0\), the one-dimensional query

\[
 L_b=w^TH
\]

does survive. Thus one shared nuisance does not make the experiment useless;
it turns a two-source identification experiment into a one-query experiment.

**Proof.** The quotient of a two-dimensional output space by the nonzero line
\(\operatorname{span}(b)\) is one-dimensional. Invertibility of \(H\) makes
the composed map onto that quotient rank one. The identities for \(x_b\) and
\(L_b\) follow by direct multiplication. \(\square\)

This theorem applies separately to the shared clock and optimistic shared-gain
models. The executable's exact query children confirm that the identity query
is unidentifiable while the constructed one-dimensional query factors through
the nuisance quotient with finite amplification.

### Corollary 4.2 — clock plus common gain

If \(c\) and \(a\) are independent, then

\[
 \operatorname{range}(c,a)=\mathbb R^2,
 \qquad P_{(c,a)}=0.
\]

Every nonzero physical query is unidentifiable. The Tier-1 values support the
independence premise, and the rational point declarations satisfy it exactly;
the premise has not yet received outward ODE validation.

### Theorem 4.3 — independent preparation at scalar launches

Suppose each protocol produces one scalar and has a nonzero preparation row
\(p_i\). Its local nuisance map \(p_i:\mathbb R^2\to\mathbb R\) is surjective.
With preparation independently refitted at A and B, the stacked nuisance map
is block local and its range is

\[
 \mathbb R\oplus\mathbb R=\mathbb R^2.
\]

Therefore the profiled response is zero and no nonzero physical query
survives. The same conclusion holds for two nonzero sensor-specific gain
columns.

This conclusion needs only nonvanishing of one preparation derivative per
launch. It does not depend on the numerical conditioning of \(H\), the design
weights, or the sizes of the derivatives.

## 5. What the existing engines do and do not retain

The exact query engine handles unrestricted linear nuisance correctly.

- No nuisance: the two-source identity query is identifiable.
- Shared clock only: the full source is not identifiable, but one exact
  clock-invariant query is.
- Shared common gain only: likewise, one exact gain-invariant query remains.
- Clock plus common gain: no nonzero query remains in the rational point model.
- Independent launch preparation: no nonzero query remains.
- Sensor-specific gain: no nonzero query remains.

The structured-nuisance engine supplies complementary exact controls. It
certifies positive distance for an output displacement orthogonal to the clock
column and zero distance for:

- the exact clock-confounded displacement;
- any displacement when clock and gain span the output space; and
- any displacement after quotienting by the full block-local preparation
  range.

If preparation or calibration coefficients have known finite bounds, they
should be modeled as a correlated zonotope rather than an unrestricted
subspace. A fixed finite-amplitude query may then retain positive separation
when its quotient response exceeds the exact nuisance support. No coefficient
bounds are assumed here, so the manuscript does not invent such a positive
claim. Moreover, a fixed nonzero nuisance radius does not by itself produce a
scale-free local floor as the source amplitude tends to zero.

## 6. Design consequence and next experiment

For \(d\) physical sources, \(r\) independent unrestricted shared nuisance
directions, and \(m\) scalar outputs, a necessary condition for a positive
full-source floor is

\[
 m-r\ge d.
\]

Local preparation nuisance must first be removed within each launch. One
scalar reading at a launch cannot survive even one nonzero local preparation
direction. The next protocol library should therefore collect multiple times
and/or sensors per launch while keeping the same preparation vector shared
within that launch.

Assuming the stated nuisance columns attain their generic independent ranks,
two angle-preparation coordinates at each of two launches consume four output
dimensions. A shared clock consumes one more. One common gain consumes one
more, giving the necessary count \(m\ge8\) for two physical sources; two
sensor-specific gains give \(m\ge9\). These counts can change when declared
nuisance columns are exactly dependent, and meeting either count is **not
sufficient**. The actual response and nuisance columns must still be enclosed
and their smallest profiled singular value certified.

A practical next library is therefore:

1. several terminal times for launch A and launch B;
2. repeated use of each sensor type so its calibration is shared across more
   than one observation;
3. at least three outputs per launch before adding shared clock/calibration
   dimensions, and enough total outputs to meet the quotient count above;
4. an exact grouped-incidence declaration specifying which nuisance
   coefficient is shared by time, sensor, or launch; and
5. outward integration of the selected nuisance columns before any physical
   positive-floor claim.

The present negative result is productive: it tells the protocol engine
exactly what additional experimental diversity must be purchased. More
precision on the same two scalar readings cannot fix a structural nuisance
alias.

## 7. Reproduction

Generate and verify a report:

```bash
python oig_double_pendulum_structured_nuisance.py \
  --output /tmp/double_pendulum_structured_nuisance.json
python oig_double_pendulum_structured_nuisance.py \
  --verify /tmp/double_pendulum_structured_nuisance.json
python oig_double_pendulum_structured_nuisance.py \
  --verify artifacts/double_pendulum_structured_physical_nuisance.json
python -m unittest -v test_oig_double_pendulum_structured_nuisance.py
```

The verifier reconstructs serialized local-column formulas, refinement
discrepancies, rationalization, exact ranks and confoundings, and every exact
child certificate. It explicitly reports that it did not replay the ODE and
did not verify outward ODE nuisance containment.
