# Adversarial Audit of the Double-Pendulum Validated Transfer

## Audit conclusion

No theorem-fatal defect was found in the outward transfer for the two active
protocols. The implementation genuinely validates the joint state and
first-parameter-sensitivity ODE, proves a componentwise Picard tube on every
time segment, propagates outward endpoint balls, and composes strict response
box membership with the existing exact rational OIG theorem.

The resulting claim is narrow but real:

\[
\lambda_{\min}(G_{\mathrm{physical}})\ge
\frac{195932905640268820789}{2500000000000000000000}>0
\]

for the stated fixed two-protocol mixture, the declared dimensionless model,
and the single nominal parameter point \((u,v)=(0,0)\). The audit does not
promote that statement to the seven-candidate selection problem, a parameter
neighbourhood, empirical model adequacy, or calibrated hardware.

## 1. Equation and convention audit

The augmented coordinate order is

\[
Y=(z,\partial_u z,\partial_v z),\qquad
z=(\theta_1,\theta_2,\nu_1,\nu_2),
\]

where \(\tau=t\sqrt{g/l_1}\), \(\nu=d\theta/d\tau\),
\(u=\log(m_2/m_1)\), and \(v=\log(l_2/l_1)\). Direct comparison away from
the launch points confirms that the implemented derivative blocks equal

\[
(F,\ D_zF\,\partial_u z+\partial_uF,\
     D_zF\,\partial_v z+\partial_vF).
\]

The observation indices are `(5, 9)` for the two source derivatives of
\(\theta_2\), and `(6, 10)` for those of scaled \(\omega_1=\nu_1\). Launches
are parameter independent, so all eight initial sensitivity entries correctly
vanish.

At the nominal representative, the mass determinant is

\[
\det M=2-\cos^2(\theta_1-\theta_2)
      =1+\sin^2(\theta_1-\theta_2)\ge 1.
\]

More generally it is
\(m_2l_2^2(1+m_2\sin^2(\theta_1-\theta_2))>0\) for positive ratios.
Thus the vector field is smooth on the relevant tubes, and the standard
parameter-differentiability theorem links the validated augmented solution to
the derivative of the nonlinear flow.

## 2. Taylor-defect audit

For a degree-\(q\) polynomial \(p\), the code forms the exact mathematical
defect \(r=p'-F(p)\) in outward Arb series arithmetic. It retains the
coefficients of degrees zero through \(q-1\) at zero. It then substitutes an
interval center \(s\in[0,h]\) and encloses the coefficient of \(\xi^q\) in
\(r(s+\xi)\). That coefficient is \(r^{(q)}(s)/q!\), so

\[
|r(t)|\le \sum_{k=0}^{q-1}|r_k|h^k
 +\sup_{s\in[0,h]}|r^{(q)}(s)/q!|h^q
\]

is a direct Taylor remainder bound. Truncating the formal series at degree
\(q\) is sufficient: a quotient coefficient of degree \(q\) depends only on
input coefficients through degree \(q\), provided its constant denominator
excludes zero, which every accepted interval evaluation does.

The separate audit suite densely samples this defect at 400-bit precision on
a later, already-wrapped step. Sampling is not used as proof; it is a hostile
indexing and truncation regression. Every sample lies inside the analytic
bound.

## 3. Picard tube and endpoint audit

The production gate is, componentwise,

\[
e_0+h d+hA\rho<\rho.
\]

The interval box used for \(A\) contains the natural interval range of
\(p([0,h])\), enlarged by \(\rho\). Hence it contains both \(p(t)\) and every
candidate curve in the tube. The integral mean-value bound makes the Picard
operator a self-map. Equivalently, a first-exit time would satisfy an error
strictly below the boundary radius and is impossible. Finite interval
Jacobian bounds supply local Lipschitz continuity and uniqueness.

The audit independently reconstructs this gate after sixty propagated steps,
checks the production acceptance iteration, and verifies that each propagated
endpoint ball contains \(p(h)\) enlarged by the proved endpoint error. A
quarter-sized hostile tube fails, guarding against omission of the initial or
defect term and against a reversed comparison.

## 4. Segmentation and wrapping controls

Three independent exact partitions all prove the response boxes:

- order 8, step \(1/100\), 160 bits;
- order 8, step \(1/125\), 192 bits;
- order 9, step \(1/80\), 192 bits.

Their step counts are respectively `(100, 125)`, `(125, 157)`, and
`(80, 100)` for the two terminal times. The \(1/125\) run exercises a final
remainder segment at \(5/4\). All four response intervals have nonempty common
intersections across the three proofs. This is a strong control on time
partitioning, endpoint wrapping, and terminal extraction; each run remains an
independent outward proof rather than a comparison of floating trajectories.

## 5. Rational membership and OIG composition

Every serialized rational outer hull lies strictly inside its declared
center-radius interval. Exact boundary tests confirm that touching a declared
boundary is rejected. No decimal value participates in membership.

The two exact shares sum to one:

\[
w_A=4589/10000,\qquad w_B=5411/10000,
\]

and each physical weight equals budget share divided by cost. Independent
two-by-two rational arithmetic reconstructs the nominal information matrix
and verifies a strictly positive LDL margin above the child's nominal floor.
The robust floor is exactly

\[
\text{nominal floor}-\text{aggregate box error}
=\frac{195932905640268820789}{2500000000000000000000}>0.
\]

The strict composed verifier rejects mutations to a response enclosure, a
declared radius, the exact child, the final floor, or any false scope flag.

## 6. Residual trust boundary

This audit assumes the correctness of Arb/python-flint outward elementary
functions and integer/rational arithmetic, just as the exact child assumes
correct host integer arithmetic. The executable artifact records its proof
precision, order, rational step, and tube iteration limit, and its verifier
recomputes rather than trusting embedded pass fields.

The lane is therefore suitable as a proof-producing, model-conditional
transfer for the fixed active experiment. Extending it to a parameter box or
certifying the original seven-candidate selection remains separate work.

## Reproduction

```bash
python -m unittest -v \
  test_oig_double_pendulum_validated_transfer.py \
  test_oig_double_pendulum_validated_transfer_audit.py
python oig_double_pendulum_validated_transfer.py \
  --verify-physical artifacts/double_pendulum_physical_positive_floor.json
```
