# Double-Pendulum Grouped Nuisance Transfer Theorem

## Outward response boxes, a shared clock column, and a certified profiled floor

**Status:** analytic finite-dimensional theorem and exact-rational certificate
recipe; not peer reviewed

**Scope:** one unrestricted scalar nuisance shared by all active outputs.  The
double-pendulum application is the selected five-output launch-A plus launch-B
design at the local linearization

\[
 (u,v,\epsilon)=(0,0,0),
 \qquad
 u=\log(m_2/m_1),\quad v=\log(l_2/l_1),
\]

with exact launch preparation.

---

## 1. Result

Let the local grouped observation model be

\[
 y-y_0=Hx+b\epsilon+\eta,
 \qquad x\in\mathbb R^q,
 \tag{1.1}
\]

where \(W\succ0\) is the output precision, \(S\succ0\) is the source
metric, and the scalar \(\epsilon\) is one clock-dilation nuisance shared by
every active output.  Define

\[
 \begin{aligned}
 A&=H^TWH,\\
 c&=H^TWb,\\
 d&=b^TWb,\\
 K(H,b)&=A-\frac{cc^T}{d}.
 \end{aligned}
 \tag{1.2}
\]

The information floor in this note is the generalized floor

\[
 \lambda_*(H,b;W,S)
 =\lambda_{\min}(K(H,b),S)
 =\inf_{x\ne0}\frac{x^TK(H,b)x}{x^TSx}.
 \tag{1.3}
\]

Suppose \((H,b)\) lies in a rigorously enclosed box about \((H_0,b_0)\),
and let \(L_0>0\).  Put

\[
 \begin{aligned}
 L_0&\le \lambda_*(H_0,b_0;W,S),\\
 M_0&\ge \|W^{1/2}H_0S^{-1/2}\|_2,\\
 r_0&=\|b_0\|_W,\\
 \eta_H&\ge
 \|W^{1/2}(H-H_0)S^{-1/2}\|_2,\\
 \eta_b&\ge\|b-b_0\|_W.
 \end{aligned}
 \tag{1.4}
\]

The first robust transfer theorem is

\[
 \boxed{
 \lambda_*(H,b;W,S)
 \ge
 \left(
 \sqrt{L_0}-\eta_H-\frac{\eta_b}{r_0}M_0
 \right)_+^2 }
 \tag{1.5}
\]

whenever \(\eta_b<r_0\).  The same premise gives the uniform denominator
bound

\[
 \boxed{b^TWb\ge(r_0-\eta_b)^2>0.}
 \tag{1.6}
\]

Thus uncertainty in the query response and uncertainty in the nuisance
direction enter differently.  Query-response error is paid directly in
normalized response norm.  Nuisance-column error first rotates the
nuisance-removing projector, with rotation at most \(\eta_b/r_0\), and is
then multiplied by the nominal response norm.

There is also a division-free exact certificate.  Let

\[
 Z=[\,b\ H\,],\qquad J=Z^TWZ.
\]

On the domain \(d=b^TWb>0\), for any proposed rational \(L\ge0\),

\[
 \boxed{
 K(H,b)-LS\succ0
 \quad\Longleftrightarrow\quad
 \begin{pmatrix}
 b^TWb & b^TWH\\
 H^TWb & H^TWH-LS
 \end{pmatrix}\succ0.}
 \tag{1.7}
\]

An outward interval enclosure of the small block in (1.7), followed by an
exact rational \(LDL^T\) positivity check, therefore proves both denominator
positivity and the robust profiled floor without interval division.  For the
two-source double pendulum the block is only \(3\times3\).

---

## 2. Normalized-response proof

Choose the symmetric positive square roots of the two metrics and set

\[
 \mathcal H=W^{1/2}HS^{-1/2},
 \qquad
 \beta=W^{1/2}b,
 \qquad
 \Pi_\beta=I-\frac{\beta\beta^T}{\beta^T\beta}.
 \tag{2.1}
\]

Then

\[
 S^{-1/2}K(H,b)S^{-1/2}
 =\mathcal H^T\Pi_\beta\mathcal H
 =(\Pi_\beta\mathcal H)^T(\Pi_\beta\mathcal H).
 \tag{2.2}
\]

Consequently

\[
 \sqrt{\lambda_*(H,b;W,S)}
 =\sigma_{\min}(\Pi_\beta\mathcal H).
 \tag{2.3}
\]

Let \(\beta_0=W^{1/2}b_0\).  If
\(\|\beta-\beta_0\|_2\le\eta_b<\|\beta_0\|_2=r_0\), then \(\beta\ne0\).
The operator norm between the two rank-one orthogonal-complement projectors
is the sine of the acute angle between their spans.  The Euclidean ball of
radius \(\eta_b\) about \(\beta_0\) cannot meet a ray making angle \(\theta\)
with \(\beta_0\) unless \(r_0\sin\theta\le\eta_b\).  Hence

\[
 \|\Pi_\beta-\Pi_{\beta_0}\|_2
 \le\frac{\eta_b}{r_0}.
 \tag{2.4}
\]

Writing \(\mathcal H_0=W^{1/2}H_0S^{-1/2}\),

\[
 \begin{aligned}
 \|\Pi_\beta\mathcal H-\Pi_{\beta_0}\mathcal H_0\|_2
 &\le
 \|\Pi_\beta(\mathcal H-\mathcal H_0)\|_2
 +\|(\Pi_\beta-\Pi_{\beta_0})\mathcal H_0\|_2\\
 &\le \eta_H+\frac{\eta_b}{r_0}M_0.
 \end{aligned}
 \tag{2.5}
\]

The minimum-singular-value perturbation inequality applied to (2.5) proves
(1.5).  The reverse triangle inequality gives
\(\|b\|_W\ge r_0-\eta_b\), proving (1.6).  No entrywise interval reciprocal
appears in the proof. \(\square\)

### 2.1 What this theorem is uniform over

Equation (1.5) takes the infimum over all fixed pairs \((H,b)\) in the
declared enclosure.  It proves that every enclosed local linear model remains
full-query identifiable after its own true shared nuisance direction is
profiled.  If the interval width is only proof uncertainty around a uniquely
specified physical derivative, this is the relevant transfer statement.

It does **not** automatically construct one decoder that annihilates every
possible \(b\) in the box.  If \(b\) itself is epistemically unknown when the
decoder is deployed, a common decoder must annihilate the span of the entire
nuisance family, or nuisance-column error must be charged as separately
bounded model error.  Uniform per-model conditioning and one-decoder robust
calibration are distinct claims.

---

## 3. Turning entrywise boxes into exact norm bounds

Assume exact rational declarations

\[
 |H-H_0|\le E_H,
 \qquad
 |b-b_0|\le e_b
 \tag{3.1}
\]

entrywise, with nonnegative rational radii.  All absolute values below are
entrywise.  Define

\[
 C_H=E_H^T|W|E_H,
 \qquad
 D_H=\operatorname{diag}(C_H\mathbf1).
 \tag{3.2}
\]

For every source vector \(x\) and every \(D=H-H_0\) in the box,

\[
 \begin{aligned}
 \|Dx\|_W^2
 &\le |x|^TE_H^T|W|E_H|x|\\
 &\le x^TD_Hx.
 \end{aligned}
 \tag{3.3}
\]

The second inequality follows from
\(2|x_ix_j|\le x_i^2+x_j^2\).  Therefore any exact rational \(a_H\) for
which

\[
 a_HS-D_H\succeq0
 \tag{3.4}
\]

gives \(\eta_H\le\sqrt{a_H}\).  Positive semidefiniteness in (3.4) may be
certified by exact rational \(LDL^T\), with a directed rational upper square
root used only at the final display layer.

For the nuisance column,

\[
 \eta_b^2\le e_b^T|W|e_b.
 \tag{3.5}
\]

The remaining nominal quantities are also exact form comparisons:

\[
 \begin{aligned}
 K(H_0,b_0)-L_0S&\succeq0,\\
 M_0^2S-H_0^TWH_0&\succeq0,\\
 r_0^2&=b_0^TWb_0.
 \end{aligned}
 \tag{3.6}
\]

A fully rational checker may choose numbers
\(s_0,h_+,m_+,r_-\in\mathbb Q_{>0}\) satisfying

\[
 s_0^2\le L_0,
 \quad h_+^2\ge a_H,
 \quad m_+^2\ge M_0^2,
 \quad r_-^2\le b_0^TWb_0,
 \tag{3.7}
\]

and \(b_+^2\ge e_b^T|W|e_b\).  It then reports the exact outward bound

\[
 \boxed{
 \lambda_*(H,b;W,S)
 \ge
 \left(s_0-h_+-\frac{b_+m_+}{r_-}\right)_+^2,}
 \tag{3.8}
\]

accepted only when \(b_+<r_-\).  Here \(h_+\) is the complete response-box
operator error, not a per-entry radius.

Entrywise boxes discard correlations.  A Taylor model, affine arithmetic
form, or zonotope can give smaller \(\eta_H\) and \(\eta_b\), but the transfer
theorem itself is unchanged.

---

## 4. A division-free outward Schur certificate

The response-level theorem is transparent and usually sharp.  A second route
is useful when all enclosures are rational intervals and one wants a tiny
proof object with no square roots or reciprocal intervals.

Set

\[
 Z_0=[\,b_0\ H_0\,],
 \qquad
 E_Z=[\,e_b\ E_H\,],
 \qquad
 J_0=Z_0^TWZ_0.
 \tag{4.1}
\]

Every enclosed augmented Gram \(J=Z^TWZ\) obeys the entrywise bound

\[
 |J-J_0|\le R_J,
 \tag{4.2}
\]

where

\[
 R_J=
 |Z_0|^T|W|E_Z
 +E_Z^T|W||Z_0|
 +E_Z^T|W|E_Z.
 \tag{4.3}
\]

The matrix \(R_J\) is symmetric and entrywise nonnegative.  Put

\[
 D_J=\operatorname{diag}(R_J\mathbf1),
 \qquad
 Q_L=\begin{pmatrix}0&0\\0&LS\end{pmatrix}.
 \tag{4.4}
\]

For every vector \(z\),

\[
 |z^T(J-J_0)z|
 \le |z|^TR_J|z|
 \le z^TD_Jz,
 \tag{4.5}
\]

so \(J\succeq J_0-D_J\).

### Theorem 4.1 — exact block-Gram transfer

If exact rational \(LDL^T\) proves

\[
 \boxed{J_0-D_J-Q_L\succ0,}
 \tag{4.6}
\]

then every \((H,b)\) in (3.1) satisfies

\[
 b^TWb>0,
 \qquad
 K(H,b)-LS\succ0,
 \qquad
 \lambda_*(H,b;W,S)>L.
 \tag{4.7}
\]

#### Proof

Equations (4.5)--(4.6) imply \(J-Q_L\succ0\) for every enclosed pair.  Its
first diagonal principal block is \(d=b^TWb>0\).  Taking the Schur complement
of that scalar block gives

\[
 H^TWH-LS-H^TWb\,(b^TWb)^{-1}b^TWH
 =K(H,b)-LS\succ0.
\]

Conversely, \(d>0\) and positivity of this Schur complement imply positivity
of the block, proving (1.7). \(\square\)

The lower bound \(d\ge (J_0-D_J)_{11}>0\) is available directly from the
same certificate.  The block route can be less conservative than bounding a
projector rotation, because it preserves the algebraic coupling among
\(A,c,d\).  It is still conservative in replacing the true correlated Gram
family by the entrywise radius (4.3).

---

## 5. Instantiation for the selected five-output design

The selected denominator-12 grouped design uses budget shares

\[
 (p_A,p_B,p_C)=\left(\frac23,\frac13,0\right)
\]

and conservative group costs \(c_A=7/2\), \(c_B=9/4\).  The physical
per-unit-budget repetition weights are therefore

\[
 \alpha_A=\frac{p_A}{c_A}=\frac4{21},
 \qquad
 \alpha_B=\frac{p_B}{c_B}=\frac4{27}.
 \tag{5.1}
\]

The inactive launch-C rows are omitted.  With the declared unit scalar
precisions inside each group,

\[
 W=\operatorname{diag}\left(
 \frac4{21},\frac4{21},\frac4{21},
 \frac4{27},\frac4{27}
 \right),
 \qquad S=I_2.
 \tag{5.2}
\]

The Tier-1 rational point declarations are

| output | \(H_{i,u}\) | \(H_{i,v}\) | shared clock \(b_i\) |
|---|---:|---:|---:|
| A: \(\theta_1,\tau=1\) | \(-104679/10^6\) | \(3127/10^5\) | \(-205821/200000\) |
| A: \(\theta_2,\tau=1\) | \(84503/10^6\) | \(-454351/10^6\) | \(525777/500000\) |
| A: scaled \(\omega_2,\tau=3/2\) | \(-63769/250000\) | \(234819/10^6\) | \(-123019/50000\) |
| B: \(\theta_1,\tau=3/4\) | \(7343/500000\) | \(-15557/10^6\) | \(194941/500000\) |
| B: scaled \(\omega_1,\tau=5/4\) | \(93811/200000\) | \(207/50000\) | \(290887/500000\) |

For these exact declarations,

\[
 d_0=b_0^TWb_0
 =\frac{77397916670069}{47250000000000}
 \approx1.63805114645649,
 \tag{5.3}
\]

and

\[
 K_0\approx
 \begin{pmatrix}
 0.0244705918682351 & 0.00604981941545038\\
 0.00604981941545038 & 0.0237069779416075
 \end{pmatrix}.
 \tag{5.4}
\]

Its two eigenvalues are approximately

\[
 0.0180269294532634,
 \qquad
 0.0301506403565793.
 \tag{5.5}
\]

The decimals in (5.4)--(5.5) are descriptive only.  The following simpler
rational inequalities are enough for a robust transfer and are decided by
exact two-by-two \(LDL^T\):

\[
 \begin{aligned}
 K_0-\frac9{500}I_2&\succ0,\\
 \left(\frac{263}{1000}\right)^2I_2-H_0^TWH_0&\succ0,\\
 d_0&>\left(\frac{1279}{1000}\right)^2.
 \end{aligned}
 \tag{5.6}
\]

For auditability, the two exact positive \(LDL^T\) pivots in the first test
are

\[
 \frac{591582202576731129747553}
 {91426289066519006250000000},
 \qquad
 \frac{418818474684195169659995106645389}
 {8282150836074235816465742000000000000},
 \tag{5.7}
\]

and those in the second test are

\[
 \frac{978177406219}{47250000000000},
 \qquad
 \frac{8747450032976304100079}
 {5777360305480968750000000}.
 \tag{5.8}
\]

### Corollary 5.1 — a simple uniform-entry tolerance

Suppose an outward enclosure is expressed about the tabulated Tier-1 centres
\((H_0,b_0)\), every entry of the five-by-two response has total radius at
most \(\rho_H\) about that centre, and every entry of the five-row clock
column has total radius at most \(\rho_b\).  Since

\[
 \sum_iW_{ii}=\frac{164}{189},
\]

the declared metric gives

\[
 \begin{aligned}
 \eta_H
 &\le\sqrt{\frac{328}{189}}\,\rho_H
 <\frac{659}{500}\rho_H,\\
 \eta_b
 &\le\sqrt{\frac{164}{189}}\,\rho_b
 <\frac{233}{250}\rho_b.
 \end{aligned}
 \tag{5.9}
\]

Moreover \(\sqrt{9/500}>67/500\).  Substitution in (1.5) gives the entirely
rational outward bound

\[
 \boxed{
 \lambda_*(H,b;W,I_2)
 \ge
 \left(
 \frac{67}{500}
 -\frac{659}{500}\rho_H
 -\frac{61279}{319750}\rho_b
 \right)_+^2.}
 \tag{5.10}
\]

It is accepted with the separate denominator gate

\[
 \rho_b<\frac{1279}{932}.
 \tag{5.11}
\]

In particular, the right side is strictly positive whenever

\[
 \frac{659}{500}\rho_H
 +\frac{61279}{319750}\rho_b
 <\frac{67}{500}.
 \tag{5.12}
\]

Nonuniform per-entry radii should be inserted into (3.2)--(3.8) or
(4.1)--(4.6); doing so will usually improve substantially on the uniform
maximum-radius corollary.

### 5.2 Achieved outward instance

The companion certificate
`oig_double_pendulum_grouped_validated_transfer.py`, documented in
`DOUBLE_PENDULUM_GROUPED_VALIDATED_TRANSFER_TIER3.md` and serialized as
`artifacts/double_pendulum_grouped_physical_clock_floor.json`, now performs
the required outward ODE transfer for all five selected rows.  Its default
validation uses 160-bit Arb arithmetic, Taylor order eight, rational step
\(1/100\), tube inflation \(6/5\), at most twelve tube iterations, and
rational outer hull denominator \(10^{15}\).

The serialized largest outward-box half-widths are

\[
 \rho_H^{\rm half}
 =\frac{144353}{2000000000000000}
 =7.21765\times10^{-11},
 \qquad
 \rho_b^{\rm half}
 =\frac{7769}{250000000000000}
 =3.1076\times10^{-11}.
 \tag{5.13}
\]

These are half-widths about the individual outward interval midpoints.  They
are not silently substituted for the total radii about the rounded Tier-1
centres required by (5.10).  Instead, the companion applies exact rational
interval arithmetic directly to the complete \(3\times3\) augmented Gram and
performs outward interval Schur/\(LDL^T\) pivot divisions.  This uses the
block-Gram equivalence (1.7), but it is not the centre-radius majorant of
Theorem 4.1.  Its first augmented-Gram pivot gives the exact
clock-denominator lower bound

\[
 b^TWb\ge
 \frac{11056842271774931587166494643791}
 {6750000000000000000000000000000}
 \approx1.6380507069296195>0,
 \tag{5.14}
\]

and exact rational interval \(LDL^T\) proves

\[
 \boxed{
 \lambda_*(H,b;W,I_2)
 >\frac{180269}{10000000}
 =0.0180269
 >\frac9{500}}
 \tag{5.15}
\]

for every response-and-clock row in the five outward boxes.  No sampled
eigenvalue decides (5.15).  The strict recomputation verifier rebuilds the
ODE boxes, augmented Gram, and all three interval pivots.

This achieved result has exactly the local-linear scope of Sections 1 and 8:
the point \(u=v=0\), one shared derivative column at \(\epsilon=0\), the
fixed A+B shares, and exact launch preparation.  It does not certify a finite
clock-dilation amplitude, a parameter neighbourhood, preparation error,
candidate-grid optimality, empirical model adequacy, or hardware calibration.

---

## 6. Cost, grouping, and coordinate audit

### 6.1 Cost and share scaling

For group \(g\), one batch repetition acquires every output in that group.
If \(W_g\) is its within-batch precision, \(p_g\) its budget share, and
\(c_g\) its batch cost, the per-unit-total-budget precision block is

\[
 \frac{p_g}{c_g}W_g.
 \tag{6.1}
\]

The shared-clock design must first stack \(H_g\) and \(b_g\), set

\[
 W=\operatorname{blockdiag}_g\left(\frac{p_g}{c_g}W_g\right),
 \tag{6.2}
\]

and only then profile the one global nuisance column.  In general,

\[
 K\!\left(\operatorname{stack}_g(H_g,b_g)\right)
 \ne\sum_g\frac{p_g}{c_g}K(H_g,b_g),
\]

because the Schur complement couples all groups through one shared
denominator.  Profiling separately would model independently refitted clocks.

A zero-share group is removed before applying the theorem; retaining its
zero-weight rows would make \(W\) semidefinite on an artificial output space.
Multiplying the total experimental budget by \(N\) changes \(W\) to \(NW\)
and changes the profiled Gram and its floor by the same factor \(N\).

### 6.2 Coordinate invariance

The physical quantity (1.3) is invariant under the following consistent
changes.

- If \(x=T\xi\), then \(H\mapsto HT\) and \(S\mapsto T^TST\); the profiled
  Gram changes by congruence and its generalized eigenvalues are unchanged.
- If \(y\mapsto Cy\), then
  \(H\mapsto CH\), \(b\mapsto Cb\), and
  \(W\mapsto C^{-T}WC^{-1}\); all terms in (1.2) are unchanged.
- Rescaling the nuisance coordinate rescales \(b\) but not its span, so the
  projector and profiled Gram are unchanged.  The ratio \(\eta_b/r_0\) in
  (1.5) is likewise invariant under a common rescaling of the nominal column
  and its error set.

The norm statement (1.5) shares these invariances when the uncertainty sets
are transported exactly.  Entrywise boxes and the row-sum majorants in
Sections 3--4 are coordinate-dependent outer approximations.  They remain
sound after a change of coordinates, but may become looser because a box hull
forgets transformed correlations.  This is a property of the enclosure, not
of the profiled information geometry.

The theorem assumes the precision \(W\), source metric \(S\), costs, and
shares are exact.  Whitening, calibration, cost, or scheduling uncertainty
requires its own enclosure and cannot be silently absorbed into \(E_H\)
unless the resulting response box is proved to contain its complete effect.

---

## 7. Response error is not Gram error

Two valid transfer routes must not be conflated.

1. **Response-level route.**  Enclose the metric-normalized response and
   nuisance column, then use (1.5).  A response error \(\eta\) erodes a
   singular value, so an information floor \(L\) transfers as a square of
   \(\sqrt L-\eta\).
2. **Gram-level route.**  Enclose the augmented Gram with (4.2)--(4.5), then
   prove (4.6).  Here the erosion is a quadratic-form error.  Formula (4.3)
   contains both first-order cross terms with the centre response and the
   quadratic error term.

An entrywise response radius is neither a singular-value error nor an
information-form error.  Subtracting it directly from a floor is
dimensionally and mathematically unjustified.  Likewise, applying the usual
unprofiled estimate

\[
 \|H^TWH-H_0^TWH_0\|
 \le2\|W^{1/2}H_0\|\,\eta_H+\eta_H^2
\]

does not by itself control the moving nuisance projector.  One must either
pay the projector-rotation term in (1.5) or enclose the full augmented block
in (4.6).

---

## 8. Exact preparation and nonlinear scope

This theorem closes a finite-dimensional transfer step only after rigorous
boxes for the required derivative rows have been supplied.  Its current
double-pendulum scope is deliberately narrower than a hardware or
finite-amplitude theorem.

- The five rows of \(H\) are derivatives with respect to \((u,v)\) at the
  fixed rational launch declarations and at \((u,v)=(0,0)\).
- The clock column is the local derivative
  \(b_i=\tau_i\,dy_i/d\tau\) at \(\epsilon=0\), for
  \(\tau_i^{\rm actual}=e^\epsilon\tau_i\).
- An interval box for \((H,b)\) gives uniformity over enclosed **local
  derivative values**.  It does not bound the nonlinear remainder for a
  finite clock error, a finite source displacement, or their mixed terms.
- Launch coordinates are exact.  Preparation error is not profiled.  If a
  bounded preparation set is propagated all the way into rigorous boxes for
  \(H\), \(b\), and the finite-amplitude output remainder, that bounded model
  can be handled explicitly.  If preparation coordinates are unrestricted
  fitted nuisances, their response columns must be appended to \(b\); the
  one-column theorem no longer applies.
- Sensor-specific gains, output correlations not represented by (5.2), and
  apparatus calibration are outside the present claim.

Thus a future outward ODE certificate should report separately:

1. state containment at every active observation time;
2. containment of both query-sensitivity rows;
3. containment of the shared clock derivative;
4. the exact preparation declaration or a separate preparation model;
5. any finite-amplitude Taylor remainder needed by the intended inference
   radius; and
6. either the response-level certificate (3.8) or the division-free block
   certificate (4.6).

Only items 1--3 plus exact preparation are needed to turn the current
conditional **local-linear** grouped floor into a uniform local-linear ODE
floor.  They are not enough by themselves for a finite-amplitude nonlinear
clock or hardware claim.

---

## 9. Minimal verifier contract

A proof-producing implementation of this theorem should serialize and
independently verify:

1. exact \(H_0,b_0,W,S\), group shares, costs, and active-row incidence;
2. nonnegative rational radii \(E_H,e_b\) and their stated provenance;
3. exact positive definiteness of \(W\) and \(S\);
4. one jointly stacked shared-nuisance model, with zero-share groups omitted;
5. either all exact form bounds in (3.2)--(3.8), including the strict
   denominator gate, or the block quantities (4.1)--(4.6);
6. an exact rational \(LDL^T\) decision for every theorem inequality;
7. strict rejection of altered centres, radii, weights, costs, shares,
   nuisance incidence, or proof-scope fields; and
8. explicit false flags for finite-amplitude clock robustness, preparation
   robustness, sensor calibration, and hardware adequacy unless independent
   evidence supplies those premises.

The division-free block certificate is the shortest exact child for the
selected design: a rational enclosure of one \(3\times3\) augmented Gram and
one exact \(LDL^T\) positivity proof.  The normalized-response certificate is
the more interpretable child and exposes separate budgets for query-response
and clock-column uncertainty.  Producing both gives the strongest audit:
agreement is a cross-check, while either valid child is already sufficient.
