# Double-Pendulum Grouped Validated Transfer with a Shared Clock

## Result

The selected five-output grouped experiment now has an outward nonlinear
transfer and an exact nuisance-profiled information theorem. At

\[
u=\log(m_2/m_1)=0,
\qquad
v=\log(l_2/l_1)=0,
\]

one shared local log-clock dilation is profiled after all five observations
are stacked. For every parameter-response and clock-response row in the
outward boxes serialized by the certificate,

\[
\boxed{
\lambda_{\min}(I_{\mathrm{profiled}})
>
\frac{180269}{10000000}
=0.0180269
>
\frac{9}{500}
=0.018.}
\]

The first inequality is decided by exact rational interval arithmetic and a
three-pivot interval \(LDL^T\) proof. No sampled eigenvalue participates in
the decision. The earlier Tier-1 point calculation was approximately
\(0.0180269294533\); the outward theorem retains all but roughly
\(2.95\times10^{-8}\) of that descriptive value.

This is a narrow Tier-3 certificate: Tier 2 supplies outward nonlinear state,
parameter-sensitivity, and nuisance-column enclosures, and Tier 3 composes
them with exact nuisance elimination and an exact positive-floor test. It does
not certify how the fixed mixture was selected.

Here **physical** means only the exact local response of the declared
dimensionless nonlinear equations. It does not mean that those equations,
the diagonal noise metric, launch preparation, calibration, or any apparatus
have been empirically validated.

## Fixed grouped experiment

The dimensionless representative is

\[
m_1=l_1=g=1,
\qquad
m_2=e^u,
\qquad
l_2=e^v,
\qquad
\tau=t\sqrt{g/l_1}.
\]

The fixed budget shares and conservative group costs are

| group | share \(p_g\) | cost \(c_g\) | batch weight \(p_g/c_g\) | outputs |
|---|---:|---:|---:|---:|
| launch A | \(2/3\) | \(7/2\) | \(4/21\) | 3 |
| launch B | \(1/3\) | \(9/4\) | \(4/27\) | 2 |
| launch C | \(0\) | \(5/2\) | \(0\) | 0 |

One repetition of a group acquires its entire output batch. The batch weight
multiplies the full within-group output metric. Every selected canonical
scalar precision is one, so the stacked metric is

\[
W=\operatorname{diag}
\left(\frac4{21},\frac4{21},\frac4{21},
      \frac4{27},\frac4{27}\right).
\]

This diagonal declaration treats the scalar readout noises as independent.
That modeling assumption is explicit; it is not inferred from the mechanics.

The five observations are:

1. launch A, \(\theta_1\) at \(\tau=1\);
2. launch A, \(\theta_2\) at \(\tau=1\);
3. launch A, scaled \(\omega_2\) at \(\tau=3/2\);
4. launch B, \(\theta_1\) at \(\tau=3/4\);
5. launch B, scaled \(\omega_1\) at \(\tau=5/4\).

Launch preparation is exact in this theorem.

## Outward nonlinear and differentiated flow

The validated solver integrates the twelve-dimensional system

\[
Y=(z,\partial_u z,\partial_v z),
\qquad
z=(\theta_1,\theta_2,\omega_1,\omega_2),
\]

using the same defect/Picard--Taylor theorem audited in
`DOUBLE_PENDULUM_VALIDATED_TRANSFER_AUDIT.md`. Parameter derivatives are the
exact forward derivatives of the nonlinear vector field, not finite
differences of nearby trajectories.

For an accepted step with polynomial \(p\), residual bound \(d\), interval
Jacobian magnitude \(A\), and proposed component radius \(\rho\), the solver
proves the componentwise self-mapping inequality

\[
\operatorname{rad}(X_0-p(0))+h d+hA\rho\le\rho.
\]

The default certificate uses:

- 160-bit Arb arithmetic;
- Taylor order 8;
- exact step size \(1/100\);
- tube inflation \(6/5\); and
- at most 12 attempted tube refinements per step.

The realized trajectories used at most two tube iterations for launch A and
six for launch B. The maximum terminal augmented-state radius upper was
\(7.67\times10^{-11}\), and the maximum Picard-tube radius upper was
\(8.96\times10^{-11}\).

## Shared clock column

There is one unrestricted local nuisance parameter \(\epsilon\), shared by
all repetitions, observations, and active groups, with

\[
\tau_i^{\mathrm{actual}}=e^\epsilon\tau_i.
\]

At \(\epsilon=0\), its response is the exact chain-rule column

\[
b_i=
\left.\frac{d}{d\epsilon}
y_i(e^\epsilon\tau_i)\right|_{\epsilon=0}
=\tau_i\frac{dy_i}{d\tau}.
\]

The terminal vector field is evaluated on the outward state box, so the
clock row is enclosed rather than merely computed at a numerical midpoint.
The theorem is local in \(\epsilon\); it is not a finite-amplitude nonlinear
clock-error bound.

## Five joint row boxes

Each row is serialized in augmented coordinate order

\[
(b_i,h_{iu},h_{iv}).
\]

The table gives descriptive midpoint \(\pm\) half-width values for the exact
rational outer intervals. The exact endpoints, not these decimal renderings,
are the proof objects.

| observation | clock \(b_i\) | \(h_{iu}\) | \(h_{iv}\) |
|---|---:|---:|---:|
| A: \(\theta_1,\tau=1\) | \(-1.029104685801041\pm3.35\!\times\!10^{-13}\) | \(-0.104678572583509\pm2.52\!\times\!10^{-13}\) | \(0.031269575651312\pm2.92\!\times\!10^{-13}\) |
| A: \(\theta_2,\tau=1\) | \(1.051553824399967\pm4.70\!\times\!10^{-13}\) | \(0.084502550935089\pm3.38\!\times\!10^{-13}\) | \(-0.454351245129375\pm4.30\!\times\!10^{-13}\) |
| A: scaled \(\omega_2,\tau=3/2\) | \(-2.460379665903024\pm3.11\!\times\!10^{-11}\) | \(-0.255076094363830\pm5.77\!\times\!10^{-11}\) | \(0.234818758248937\pm7.22\!\times\!10^{-11}\) |
| B: \(\theta_1,\tau=3/4\) | \(0.389882294945426\pm3.50\!\times\!10^{-15}\) | \(0.014686299828306\pm3.00\!\times\!10^{-15}\) | \(-0.015556885676874\pm3.50\!\times\!10^{-15}\) |
| B: scaled \(\omega_1,\tau=5/4\) | \(0.581774192015221\pm7.93\!\times\!10^{-12}\) | \(0.469054738019173\pm3.07\!\times\!10^{-11}\) | \(0.004140122028894\pm5.44\!\times\!10^{-11}\) |

The maximum serialized parameter-response half-width is exactly

\[
\frac{144353}{2000000000000000}=7.21765\times10^{-11},
\]

and the maximum clock-response half-width is exactly

\[
\frac{7769}{250000000000000}=3.1076\times10^{-11}.
\]

The proof deliberately discards correlations within a trajectory and treats
the result as a Cartesian box. This only enlarges the family certified by the
subsequent interval theorem.

## Exact interval nuisance profile

For augmented row

\[
q_i=(b_i,h_{iu},h_{iv}),
\]

form the weighted augmented Gram

\[
J=\sum_{i=1}^{5}w_i q_i^Tq_i
=
\begin{pmatrix}
d&c^T\\
c&A
\end{pmatrix},
\]

where

\[
d=b^TWb,
\qquad
c=H^TWb,
\qquad
A=H^TWH.
\]

Exact rational interval multiplication and addition enclose every entry of
\(J\) directly from the five row boxes. In particular,

\[
d\ge
\frac{11056842271774931587166494643791}
     {6750000000000000000000000000000}
\approx1.63805070692962>0.
\]

Thus the profiled two-source information is well-defined:

\[
I_{\mathrm{profiled}}=A-\frac{cc^T}{d}.
\]

Its exact rational interval enclosure has the descriptive decimal form

\[
I_{\mathrm{profiled}}\in
\begin{pmatrix}
[0.0244705633432,0.0244705633794]&
[0.00604984522408,0.00604984526268]\\
[0.00604984522408,0.00604984526268]&
[0.0237070359239,0.0237070359584]
\end{pmatrix}.
\]

## Exact three-pivot proof

For a proposed floor \(L\), the exact Schur theorem gives

\[
I_{\mathrm{profiled}}-LI_2\succ0
\quad\Longleftrightarrow\quad
J-\operatorname{diag}(0,L,L)\succ0,
\]

because \(d>0\). The verifier applies no-pivot interval \(LDL^T\) to the
enclosed three-by-three block. At the sharper value

\[
L=\frac{180269}{10000000},
\]

the exact lower endpoints of all three pivot intervals are positive. Their
decimal descriptions are

\[
1.63805070692962,
\qquad
0.00644366334323,
\qquad
3.97\times10^{-8}.
\]

The final exact pivot margin is small but strictly positive. The artifact
stores the full exact fractions for all three pivots. A second certificate at
\(L=9/500\) has final pivot lower
approximately \(5.06\times10^{-5}\), providing an especially transparent
human-readable control.

This block proof is the executable specialization of
`DOUBLE_PENDULUM_GROUPED_NUISANCE_TRANSFER_THEOREM.md`. It certifies every
fixed pair \((H,b)\) in the outward family after profiling that pair's true
shared clock direction. It does not construct one decoder that annihilates
every possible nuisance column in the box simultaneously; those are distinct
robust-calibration semantics.

## Scope boundary

The certificate proves all of the following:

- outward nonlinear state and exact \(u,v\) sensitivity transfer for the five
  selected observations;
- outward local shared-clock responses from the terminal state boxes;
- exact group-cost and fixed-share weighting;
- exact rational interval enclosure of the augmented Gram; and
- a strictly positive two-source floor after profiling one shared clock.

It does **not** prove:

- preparation-error robustness;
- finite-amplitude clock-dilation robustness;
- parameter-neighbourhood uniformity;
- sensor calibration or sensor-specific gain robustness;
- empirical adequacy of the double-pendulum model or diagonal noise metric;
- hardware performance;
- transfer of the denominator-12 grid ordering;
- exact finite-grid optimality; or
- optimality over launches, sensors, or observation times not in the finite
  library.

In particular, the result transfers the achieved fixed mixture
\((2/3,1/3,0)\). It does not turn the Tier-1 search that discovered that
mixture into an optimality theorem.

## Strict verification and reproduction

The verifier first reconstructs the augmented Gram and both interval
\(LDL^T\) certificates from the serialized rational row boxes. It then reruns
the outward nonlinear integrations, reconstructs the state, response, and
clock hulls, and requires strict JSON equality with the supplied artifact.
Forged floors, row boxes, scope flags, or metadata are rejected. Weak
Picard--Taylor controls raise rather than emit a certificate. A 192-bit,
order-9, step-\(1/200\) control run lies inside every default augmented row
box and proves the same two floors.

```bash
python -m pip install -r requirements.txt
python oig_double_pendulum_grouped_validated_transfer.py \
  --output artifacts/double_pendulum_grouped_physical_clock_floor.json
python oig_double_pendulum_grouped_validated_transfer.py \
  --verify artifacts/double_pendulum_grouped_physical_clock_floor.json
python -m unittest -v \
  test_oig_double_pendulum_grouped_validated_transfer.py
```

Frozen proof objects:

- `oig_double_pendulum_grouped_validated_transfer.py`
- `test_oig_double_pendulum_grouped_validated_transfer.py`
- `artifacts/double_pendulum_grouped_physical_clock_floor.json`
- `DOUBLE_PENDULUM_GROUPED_VALIDATED_TRANSFER_TIER3.md`
