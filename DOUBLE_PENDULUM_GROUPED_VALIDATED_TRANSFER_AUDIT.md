# Hostile Audit of the Grouped Validated Shared-Clock Transfer

## Audit conclusion

No theorem-fatal defect was found.

The production certificate genuinely composes:

1. outward Picard--Taylor enclosures of five nonlinear terminal states and
   their two exact parameter-sensitivity columns;
2. outward endpoint chain-rule enclosures of one clock-dilation column;
3. exact group-share and cost scaling;
4. exact rational interval construction of the augmented Gram; and
5. a uniform positive-definiteness proof after nuisance profiling.

For the declared local model, exact preparation, fixed grouped shares
\((2/3,1/3,0)\), and one clock nuisance shared globally across repetitions and
groups, the audit independently confirms

\[
  \lambda_{\min}(I_{\mathrm{profiled}})
  >
  \frac{180269}{10000000}
  =0.0180269.
\]

The statement is uniform over the Cartesian outward boxes for the five
parameter-response rows and five clock entries. It is a local derivative
theorem at \((u,v,\epsilon)=(0,0,0)\), not a finite-amplitude, preparation,
calibration, hardware, candidate-selection, or optimality theorem.

## 1. Independent exact interval reconstruction

The audit suite implements its own exact closed-interval type. It does not
call the production Gram or profile builders when reconstructing the proof.
From the serialized row boxes

\[
  q_i=(b_i,h_{iu},h_{iv})
\]

and exact scalar weights

\[
  (w_1,\ldots,w_5)
  =
  \left(
  \frac4{21},\frac4{21},\frac4{21},
  \frac4{27},\frac4{27}
  \right),
\]

it independently forms

\[
  J=\sum_i w_iq_i^Tq_i
   =\begin{pmatrix}d&c^T\\c&A\end{pmatrix}.
\]

Every exact endpoint agrees with the serialized production Gram. In
particular, the shared-clock denominator obeys

\[
  d\ge
  \frac{11056842271774931587166494643791}
       {6750000000000000000000000000000}
  \approx1.6380507069296244.
\]

This is comfortably separated from zero before any interval division is
performed.

The independently reconstructed interval Schur complement is

\[
  A-\frac{cc^T}{d}\in
  \begin{pmatrix}
  [0.0244705633432,0.0244705633794]&
  [0.00604984522408,0.00604984526268]\\
  [0.00604984522408,0.00604984526268]&
  [0.0237070359239,0.0237070359584]
  \end{pmatrix}.
\]

These endpoints also agree exactly with the artifact.

## 2. A second floor proof

Production proves the floor through a sequential interval \(LDL^T\) test on
the three-by-three augmented block. The audit uses a distinct route.

For a symmetric interval matrix

\[
  S=
  \begin{pmatrix}a&c\\c&d\end{pmatrix},
\]

let \(a_-\) and \(d_-\) be the diagonal lower endpoints and let

\[
  c_+=\max(|c_-|,|c_+^{\rm endpoint}|).
\]

Every enclosed matrix satisfies \(S-LI\succ0\) whenever

\[
  a_- - L>0,\qquad
  d_- - L>0,\qquad
  (a_- - L)(d_- - L)>c_+^2.
\]

Exact rational arithmetic verifies all three inequalities at

\[
  L=\frac{180269}{10000000}.
\]

This independently certifies the same uniform floor without reusing the
production pivot recursion.

The audit also includes a nearby negative control. The slightly larger value

\[
  L_{\rm false}=\frac{18027}{1000000}=0.018027
\]

already makes the shifted determinant negative at the Cartesian row-box
midpoint. It therefore cannot be a uniform floor, and both the independent
interval test and the midpoint witness reject it. The accepted value is not
merely an arbitrary positive number that happened to pass a weak test.

## 3. Alternate outward time partition

An independent validated run uses:

- 192-bit Arb arithmetic;
- Taylor order 9; and
- exact nominal step \(1/125\).

This partition is deliberately incommensurate with several endpoints and
therefore exercises exact final remainder steps. The five observation step
counts are

\[
  (125,125,188,94,157).
\]

For every observation, all three alternate outward balls

\[
  (b_i,h_{iu},h_{iv})
\]

overlap the default production rational boxes. The audit recomputes the clock
entry at the alternate terminal enclosure as

\[
  b_i=\tau_iF_{\mathrm{sensor}}(z(\tau_i)).
\]

For angle sensors this is \(\tau_i\nu_i\); for scaled-velocity sensors it is
\(\tau_i\alpha_i\). This guards against the common indexing error of using a
terminal velocity where a terminal acceleration is required.

## 4. Failure-mode matrix

### 4.1 Uncertain response and nuisance columns

Profiling only the center clock column and then placing intervals around the
result would not be uniform in \(b\). The projector moves with the true clock
direction. Production instead encloses the complete augmented Gram built
from uncertain \(H\) and uncertain \(b\), then proves block positivity.

Cartesian interval multiplication discards correlations between state,
parameter, and clock rows. That loss is conservative: it enlarges the family.
No favorable trajectory correlation is used to obtain the floor.

### 4.2 Shared versus refitted nuisance

The certified model has one global clock column. Independent midpoint
calculations give the following descriptive floors under the same row and
weight declarations:

| nuisance incidence | descriptive floor |
|---|---:|
| one clock shared globally | \(0.01802692111\) |
| one clock refitted independently for A and B | \(0.00898593\) |
| one independent clock nuisance per scalar output | \(0\) |

These are different models. The production certificate correctly stacks the
five rows and profiles one column only after assembly. It does not silently
sum separately profiled group forms.

The uncertainty-box theorem profiles each enclosed model's own true clock
direction. It does not construct one fixed decoder that annihilates every
possible clock vector in the entire box simultaneously. The production memo
states this distinction explicitly.

### 4.3 Cost and precision scaling

For a group share \(p_g\) and group cost \(c_g\), the correct batch precision
factor is \(p_g/c_g\), applied once to the complete within-group metric. The
five exact weights are \(4/21\) for launch A and \(4/27\) for launch B.

Using budget shares directly, scaling response rows by \(p_g/c_g\) instead of
scaling the information metric, or applying cost twice produces a different
floor. The audit reconstructs the serialized Gram from the correct weights
and confirms that the incorrectly unscaled result differs materially.

Launch C has zero share and is omitted from the five-row output space. Keeping
zero-weight C rows would make the enlarged output metric semidefinite and
would obscure the actual theorem incidence.

### 4.4 Denominator safety

The Schur expression is meaningful only after proving \(d=b^TWb>0\). The
artifact proves a strong exact lower bound before division.

The audit replaces every clock interval by \([-1,1]\). The resulting
Cartesian family contains the zero clock vector, its denominator interval is
not bounded away from zero, the independent profile refuses division, and the
strict production verifier rejects the forged artifact. This is a fail-closed
control against division through an interval containing zero.

### 4.5 Endpoint and grouping incidence

The active rows are exactly the first five canonical candidates:

1. A theta1 at \(\tau=1\);
2. A theta2 at \(\tau=1\);
3. A scaled omega2 at \(\tau=3/2\);
4. B theta1 at \(\tau=3/4\); and
5. B scaled omega1 at \(\tau=5/4\).

The two A observations at \(\tau=1\) share one launch/time trajectory. All
launch coordinates and terminal times remain exact rationals. Exact remainder
segments prevent endpoint rounding or overshoot in partitions that do not
divide a terminal time.

### 4.6 Scope promotion

The strict verifier preserves false flags for:

- preparation-error robustness;
- finite clock-amplitude robustness;
- parameter-neighbourhood uniformity;
- candidate-selection transfer;
- finite-grid optimality;
- empirical model adequacy; and
- hardware calibration.

The diagonal unit-precision output metric and exact launch preparation are
model declarations, not consequences of the mechanics.

## 5. Verifier audit

The production verifier:

1. rejects unknown schema, method, tier, scope, and promoted flags before
   accepting a proof;
2. reconstructs the interval Gram, profile, and both floor children from the
   serialized exact row boxes;
3. rebuilds all outward ODE, sensitivity, output, and clock enclosures from
   the recorded validated-solver configuration; and
4. requires strict type-sensitive JSON equality.

The audit additionally checks forged floors, widened clock boxes, incorrect
weights, a denominator family containing zero, a nearby false floor, and all
three nuisance-incidence patterns.

## 6. Residual trust boundary

The proof relies on python-flint/Arb outward elementary functions and the
already audited Picard--Taylor step theorem. The alternate partition is an
independent validated run, but it uses the same underlying Arb and augmented
vector-field implementation.

The exact rational interval and two-by-two floor audit is separately
implemented. It still assumes correct Python arbitrary-precision integer and
rational arithmetic.

Byte-identical artifact regeneration can depend on the pinned numerical
runtime. The mathematical proof object is the exact collection of outward
rational boxes and exact inequalities, not the decimal displays.

The production memo informally compares the final information-pivot margin
with a response-row half-width. Those quantities have different units, so
that ratio should be read only as a rough numerical scale comparison. The
exact interval \(LDL^T\) inequalities, not that comparison, establish the
robustness margin.

## Reproduction

Run production and hostile audit suites together:

    python -m unittest -v \
      test_oig_double_pendulum_grouped_validated_transfer.py \
      test_oig_double_pendulum_grouped_validated_transfer_audit.py

Strictly verify the canonical artifact:

    python oig_double_pendulum_grouped_validated_transfer.py \
      --verify artifacts/double_pendulum_grouped_physical_clock_floor.json

The hostile audit adds only:

- test_oig_double_pendulum_grouped_validated_transfer_audit.py
- DOUBLE_PENDULUM_GROUPED_VALIDATED_TRANSFER_AUDIT.md

It does not edit production implementation, tests, manuscript, or artifact.
