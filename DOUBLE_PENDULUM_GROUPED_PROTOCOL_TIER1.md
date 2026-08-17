# Double-Pendulum Grouped Protocols under a Shared Clock

## Result

The structured-nuisance rank obstruction is constructive, not terminal. The
seven already declared scalar double-pendulum candidates become sufficient for
the full two-coordinate query once observations are grouped and a single clock
dilation is shared across the active experiment.

The finite library batches candidates by exact launch:

| Group | Readouts | Outputs | Conservative cost |
|---|---|---:|---:|
| launch A | theta1 at tau=1; theta2 at tau=1; scaled omega2 at tau=3/2 | 3 | 7/2 |
| launch B | theta1 at tau=3/4; scaled omega1 at tau=5/4 | 2 | 9/4 |
| launch C | theta2 at tau=1; scaled omega2 at tau=3/2 | 2 | 5/2 |

Launch A alone is a minimum-output witness. Its three outputs retain exact
rank two after profiling one shared clock column. The exact query-engine child
certifies a strictly positive floor for the declared rational point model,
although the floor is small:

\[
  \lambda_{\min}^{\mathrm{profiled}}
  > 9.7891241646\times 10^{-6}.
\]

A complete denominator-12 search over all 91 rational three-group budget
shares selects

\[
  (p_A,p_B,p_C)=\left(\frac23,\frac13,0\right).
\]

With the declared conservative group costs, the physical repetition weights
are \(p_A/c_A=4/21\) and \(p_B/c_B=4/27\). Five scalar outputs are stacked,
the one shared clock direction is profiled only after stacking, and the exact
finite-linear certificate gives

\[
  \lambda_{\min}^{\mathrm{profiled}}
  > 0.018026929453263358.
\]

This is the first positive two-query floor in the double-pendulum lane after
admitting the declared shared nuisance in a conditional rational point model.
It also resolves why the earlier two-scalar design failed: two
outputs minus one unrestricted nuisance leave at most one effective output,
whereas three outputs can retain two independent query directions.

## Model and grouping semantics

The source coordinates are

\[
  u=\log(m_2/m_1),\qquad v=\log(l_2/l_1),
\]

in dimensionless time \(\tau=t\sqrt{g/l_1}\), with
\(\nu_i=d\theta_i/d\tau\). For a fixed exact launch, the analytic parameter
sensitivity satisfies

\[
  S'=D_zF\,S+D_{(u,v)}F,\qquad S(0)=0.
\]

Every state, tangent, parameter, clock, and gain row in this milestone is a
local linearization at
\((u,v,\epsilon,\kappa)=(0,0,0,0)\), with \(\kappa\) present only in the
secondary common-gain model.

For a scalar sensor output \(y_i\) observed at \(\tau_i\), one shared log clock
dilation \(\epsilon\) acts as

\[
  \tau_i^{\rm actual}=e^\epsilon\tau_i,
  \qquad
  \left.\frac{\partial y_i}{\partial\epsilon}\right|_{\epsilon=0}
  =\tau_i\frac{dy_i}{d\tau}.
\]

Each group is an inseparable batch: a repetition collects every member output
and receives one budget weight. If its budget share is \(p_g\) and its group
cost is \(c_g\), the complete within-group output metric is scaled by
\(p_g/c_g\). The group cost is the conservative sum of the legacy scalar
candidate costs; no shared-run discount is assumed. The clock parameter is
global across every repetition and every active group type, so its column is
profiled after the active groups are stacked. Profiling separately inside each
group or repetition would be a different model. The within-group output metric
is diagonal, with the legacy scalar noise precisions on its diagonal; this
declares independent scalar readout noise before the common batch factor
\(p_g/c_g\) is applied.

Preparation is exact in this milestone. The rational initial states are fixed
declarations. Initial-angle or initial-velocity errors are not profiled, and
no preparation-error bound is claimed.

## Rank condition

Write the stacked source response as \(H\in\mathbb R^{m\times 2}\) and the
shared nuisance response as \(B\in\mathbb R^{m\times r}\). The profiled query
has full rank exactly when

\[
  \operatorname{rank}[B\ H]-\operatorname{rank}B=2.
\]

Consequently \(m-r\ge 2\) is necessary. For one nonzero shared clock column,
\(m\ge3\). Launch A attains that lower output count and passes the exact rank
test. The selected A+B design improves conditioning while remaining inside
the original seven-candidate library.

## Secondary common-gain control

As an additional conditional test, the report adds one optimistic common log
gain \(\kappa\) with derivative \(\partial_\kappa y_i=y_i\). The same gain is
shared even across angle and scaled-velocity channels; this is not a model of
independent sensor calibrations.

With clock plus common gain, \(r=2\), hence at least four outputs are necessary.
The denominator-12 search selects

\[
  (p_A,p_B,p_C)=\left(\frac5{12},\frac14,\frac13\right),
\]

uses all seven outputs, retains exact effective rank two, and certifies the
conditional point-model floor

\[
  \lambda_{\min}^{\mathrm{profiled}}
  > 0.0021840122221773164.
\]

This extension is useful as a dimensional stress test, but the clock-only,
exact-preparation design is the primary milestone.

## What is exact and what is not

For every scalar observation, the artifact stores coarse and refined terminal
states, full \(4\times2\) analytic parameter sensitivities, terminal vector
fields, all four clock-response entries, and the selected sensor rows. All
refinement and energy controls pass. Fine scalar rows are rounded to the
nearest multiple of \(10^{-6}\) and serialized as rational point declarations.

The exact query engine then proves, for those rational declarations:

- shared-nuisance projection and rank;
- an exact decoder for the full identity query;
- exact annihilation of the declared nuisance columns; and
- a positive rational lower bound on the profiled information floor.

The denominator-12 search ordering is reproducible binary64 discovery. It is
not claimed as an exact optimality theorem. The selected designs receive
separate exact certificates, so positivity does not depend on the numerical
ordering.

Nothing in this Tier-1 result outwardly encloses the nonlinear trajectory,
parameter sensitivity, or clock response. Rounding a numerical value to a
rational point is not an enclosure. The exact certificates are therefore
conditional finite-linear theorems, not yet ODE transfer theorems.

## Reproduction

Generate the canonical artifact:

    python oig_double_pendulum_grouped_protocol.py \
      --output artifacts/double_pendulum_grouped_protocol_tier1.json

Strictly recompute all Tier-1 numerics, the complete rational-share grid, and
the exact query children:

    python oig_double_pendulum_grouped_protocol.py \
      --verify artifacts/double_pendulum_grouped_protocol_tier1.json

Run the focused tests:

    python -m unittest -v test_oig_double_pendulum_grouped_protocol.py

## Next proof targets

The shortest route from this conditional milestone to a physical guarantee is:

1. outwardly enclose the state, both parameter-response rows, and the clock row
   for the five active A+B observations;
2. transfer those boxes through a robust nuisance-profiled query certificate;
3. add a separately bounded preparation layer, or measure preparation well
   enough to eliminate it before profiling; and
4. treat sensor-specific gains only after adding enough observations to meet
   the enlarged output-count condition.

Free scalar weighting or a larger time/sensor grid may improve the floor, but
that is a distinct design space. The present result deliberately proves that
the existing finite library already contains a constructive grouped solution.
