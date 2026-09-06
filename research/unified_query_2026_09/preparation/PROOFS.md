# Conditioning a preparation certificate on joint calibration records

## Model and inherited premises

The source is \(s=(u,v,e)\in[-10^{-4},10^{-4}]^3\), with \(u=\log(m_2/m_1)\), \(v=\log(l_2/l_1)\), and one unknown clock \(e\) shared by every reading. The dimensionless model has \(m_1=l_1=g=1\), and nominal-time dynamics are \(z'=\exp(e)F(z;u,v)\). The measured state coordinates are unwrapped angles and physical angular velocities multiplied by \(\sqrt{l_1/g}\). They are not angular derivatives with respect to the uncertain nominal clock.

The fixed launches and outputs are:

| Launch | Nominal initial state | Readings |
|---|---|---|
| A | \((4/5,-7/20,0,0)\) | \(\theta_1(1),\theta_2(1),\widetilde\omega_2(3/2)\) |
| B | \((-3/5,9/10,0,0)\) | \(\theta_1(3/4),\widetilde\omega_1(5/4)\) |

The selected design allocates budget shares \((2/3,1/3)\), with group costs \((7/2,9/4)\). Its row weights are \(4/21\) for the three A readings and \(4/27\) for the two B readings. Noise satisfies \(\|W^{1/2}n\|_2\le\eta\). Each launch supplies all of its readings without re-preparation.

The five readings are the dynamical outputs. Observing the initial states and establishing the common instrument-correction support add calibration acquisitions and reference-characterization resources. Their cost is not included in these original group costs and cannot be specified until an apparatus and metrology protocol are chosen.

The prior outward ODE enclosure covers the whole source box and every initial preparation offset \(p\in[-10^{-5},10^{-5}]^8\). It contains the source Jacobian \(J=D_sf\) and preparation Jacobian \(D_pf\). The fixed rational decoder \(B\) satisfies \(BA=I_3\) for the rational nominal source matrix \(A\). The inherited exact checker reconstructs these quantities and verifies this equality. Its complete finite-flow proof is preserved in [the prior preparation proof](/Volumes/KINGSTON/Vibecoding/Math/research/next15_2026_09/preparation/PROOFS.md).

The new checker reads the source artifacts afresh, caches validation by immutable file contents, reconstructs the exact decoder consequences, and records file hashes. The nonlinear enclosures are inherited mathematical premises. Their nominal and two finite preparation-box ODE reconstructions were also rerun successfully during this extension. No browser trajectory or nominal sensitivity is substituted for them.

## Joint calibration theorem

Fix one record of initial-state measurements. Let its consistent preparation set have the form

\[
p_A=m_A+b+v_A,\qquad p_B=m_B+b+v_B,
\]

where \(m_A,m_B\in\mathbb R^4\) are known, \(|b_j|\le\sigma_j\), and \(|v_{g,j}|\le r_{g,j}\). Asymmetric correction intervals are included by moving their midpoints into \(m_g\). The same \(b\) applies to both launches; the \(v_g\) are separate bounded residuals. No distribution, independence, or averaging law is assumed. The residuals may be adversarially correlated with the source and with one another.

Assume the whole joint set lies in the inherited outer preparation box. The executable sufficient containment test is

\[
|m_{g,j}|+\sigma_j+r_{g,j}\le10^{-5}\quad\text{for all eight coordinates}.\tag{P1}
\]

Let interval projection be performed before absolute values, and define

\[
R_{ik}\ge\sup |[B(J-A)]_{ik}|,
\quad k_i=\sum_kR_{ik}<1,
\]

\[
H_{i,g,j}\ge\sup |[B D_{p_g}f]_{ij}|,
\qquad
C_{ij}\ge\sup |[B(D_{p_A}f+D_{p_B}f)]_{ij}|,
\]

\[
c_i\ge\left(\sum_l B_{il}^2/w_l\right)^{1/2},
\qquad h_i=\sum_{g,j}H_{i,g,j}r_{g,j}+\sum_jC_{ij}\sigma_j.
\]

All suprema cover the complete inherited source/preparation box. For every pair of sources consistent with the *same* output observation and the *same* calibration record,

\[
\|s-s'\|_\infty\le
\max_i\frac{2(h_i+\eta c_i)}{1-k_i}.\tag{P2}
\]

In particular, source and physical-query diameter are at most \(\Delta\) if

\[
\Delta k_i+2h_i+2\eta c_i\le\Delta\quad\text{for every row }i.\tag{P3}
\]

Here the physical query is \(q(s)=(u,v)\), the two log parameters, measured in the infinity norm. Deleting the clock coordinate cannot increase that norm. The reported conclusion is the diameter of the consistent query set; a particular point estimator and its error need a separately justified inverse or enclosing center. No half-diameter estimation error is asserted by this bridge.

The fixed-certificate readout-noise boundary for that calibration record is exactly

\[
\eta_*=
\min_i\frac{\Delta(1-k_i)/2-h_i}{c_i},\tag{P4}
\]

provided every numerator is nonnegative and \(c_i>0\), as in this instance. Equality is admitted by this sufficient criterion. This is not a sharp minimax noise boundary for the nonlinear experiment.

**Proof.** Take two consistent worlds \((s,p,n)\), \((s',p',n')\). Subtract their equal observations. At fixed \(p\), integrate the source derivative along the segment from \(s'\) to \(s\); after applying \(B\), its value is \((s-s')+E(s-s')\) with \(|E|\le R\). At fixed \(s'\), integrate the preparation derivative along the joint affine segment from \((b',v_A',v_B')\) to \((b,v_A,v_B)\). The segment remains inside the joint set and outer box by convexity. Its common-bias derivative is precisely \(B(D_{p_A}f+D_{p_B}f)\). The known centers cancel on subtraction. The unknown differences obey \(|b-b'|\le2\sigma\), \(|v_g-v_g'|\le2r_g\), so the decoded preparation difference in row \(i\) is at most \(2h_i\). Weighted Cauchy–Schwarz bounds each decoded noise by \(\eta c_i\).

Thus \(x=|s-s'|\) obeys \(x\le Rx+v\), where \(v_i=2(h_i+\eta c_i)\). Let \(M=\max_i x_i\), and choose an index \(i\) attaining that maximum. Its inequality yields \(M\le k_iM+v_i\), so \(M\le v_i/(1-k_i)\), and hence (P2). Condition (P3) bounds each such quotient by \(\Delta\). Solving its three affine inequalities for \(\eta\) gives (P4). QED.

This proof identifies two useful rules. A known measured center consumes outer-domain allowance through (P1), but is not an ambiguity radius in (P2). A shared systematic offset must remain a shared variable until after projecting and summing its columns. Triangle inequality gives \(C_{ij}\le H_{i,A,j}+H_{i,B,j}\); replacing it by the latter is valid but can be weaker.

The source box already includes the unknown clock. If a velocity calibration depends on that same clock, its correction intervals must enclose the velocity in the declared physical-time state coordinates over the entire allowed clock range. The theorem tolerates source-dependent corrections inside the stated support. It does not justify entering nominal-clock derivatives as though they were calibrated physical velocities.

## A concrete interior specification

The worked record is explicitly synthetic. It makes the following preparation-offset center choices, in coordinate order \((\theta_1,\theta_2,\widetilde\omega_1,\widetilde\omega_2)\):

| Quantity | A | B |
|---|---|---|
| Known center offset | \((1,-1,1,-1)\times10^{-6}\) | \((5,1,-1,1)\times10^{-6}\) |
| Separate residual radii | \((5,5,5,5)\times10^{-6}\) | \((3,5,5,5)\times10^{-6}\) |
| Common systematic radii | \((1,1,1,1)\times10^{-6}\) | Same four unknown values as A |

The absolute outer extents are \(7\times10^{-6}\) in seven coordinates and \(9\times10^{-6}\) in B's first angle. All are strictly inside the validated cap. With \(\eta=10^{-7}\), \(\Delta=10^{-4}\), the normalized row loads from (P3) are approximately

\[
(0.6420269184,\ 0.6051979067,\ 0.2874388387).
\]

Each exact row has slack greater than \(3.5797\times10^{-5}\), or more than 35.79% of the target. This specification deliberately leaves a substantial mathematical margin instead of using the previous volume-maximizing box, which lay almost on a constraint face.

The source-diameter bound is

\[
D<0.000060053.
\]

The exact fixed-certificate boundary satisfies

\[
\eta_*>0.0000024787.
\]

Thus the same declared calibration supports a weighted readout-noise radius over 24.787 times the fixture's baseline \(10^{-7}\) if only the \(10^{-4}\) target is required. This is a budget tradeoff in the prescribed noise norm, not an empirical sensor-noise or optimality claim.

Two controls isolate the reason for the improvement. If the identical total support is replaced by a zero-centered box with radii equal to the absolute outer extents, the first normalized row load is approximately **1.0675849674**, so that sufficient target test fails. Conditioning on the measured centers restores it without tightening the actual support. If the common instrument offsets are replaced by independent A/B offsets with the same coordinate radii, the first load increases from **0.6420269184** to **0.6647068597**. The former comparison tests center information; the latter tests retained correlation. A failed sufficient control is not a nonrecoverability theorem.

## Measurement meaning and a calibration-time transport bound

The support statement belongs to the two actual launches whose outputs enter the certificate. A finite history of successful calibration trials does not itself bound a future launch: the deterministic sequence of zero errors for the observed trials and an out-of-range next error is a counterexample. A certified operating envelope, or a calibration observation on each actual launch, supplies the additional premise. No sample-size averaging factor appears in this package.

If the initial-state measurement occurs up to \(h\) dimensionless physical-time units before the model's launch origin, a bounded release evolution can be included in the local residual. For example, if the measurement-time physical scaled velocity has absolute bound \(V_j\) and the intervening scaled acceleration has bound \(A_j\), then integrating \(\dot\omega_j\) gives a velocity change at most \(A_jh\), and integrating that bound gives an angle change at most \(V_jh+A_jh^2/2\). Add these deterministic intervals, plus the instrument's nonshared uncertainty, to the relevant local residual intervals. The acceleration bounds and delay bound require their own evidence; the algebra does not manufacture them from a successful simulation.

## Validation and scope

The new ordinary checker is standard-library-only. It verifies the strict record shape, rational interval endpoints, state/clock/launch incidence, support containment, exact inherited source and decoder consequences, signed common-offset projection, all row inequalities, and the exact noise boundary. Ten tests include center translation, full-domain escape, direct sensor-column reconstruction, the shared-offset cancellation identity, the equality noise boundary, malformed records, and altered inherited intervals. A physical-record label still returns an explicit external-provenance/model-validation requirement; it cannot turn asserted bounds into empirical evidence.

The inspected browser chamber uses RK4 forecasts and adaptive Dormand–Prince 5(4) outcomes from the same declared equations. Its ensemble supports, internal replay, and statistical bookkeeping are useful synthetic diagnostics. The atlas laboratory explicitly reports finite-time numerical discovery on an initial-angle slice and does not validate a physical flow enclosure. Neither source supplies measured eight-coordinate A+B calibration intervals. Their certified strip concerns the older exact-preparation experiment. The present extension adds a separate read-only record bridge; it does not alter that interface or relabel its runs.
