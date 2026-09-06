# Six channels with joint clock and potential uncertainty

The contract was fixed in the parent [protocol](../PROTOCOL.md) before this
calculation. The six physical rows are 485, 493, 499, 501, 507 and 515. The
unknown target is any integer from 490 to 510, the source is any nonzero vector
in the same two orthonormal cosine modes, and nominal and true model times
both belong to [1,2]. The sensor error has Euclidean norm at most
`3e-8 ||u||`. The common clock displacement satisfies `|dt| <= 1e-8`; the
common potential parameter satisfies `|g-4/5| <= 1e-8`.

These are model units and a source-relative sensor norm. They are not an
apparatus timing specification or a percentage of the measured signal.

## 1. Complete finite model and its directional approximation

Use the finite reflecting paths with 1001 vertices in each coordinate and

\[
H(g)=I_y\otimes L_x+L_y\otimes\operatorname{diag}(1+g x_i),
\qquad x_i=(i+1/2)/1001,
\]
\[
A_j(t,g)=(1+t)^{1/4}R(I_y\otimes e^T)e^{-tH(g)}(\delta_j\otimes U).
\]

The exact source preparation, spatial average, physical parameter family and
noise promise are premises. No commutation of the spatial potential with
`L_x` is assumed. Let `alpha=(1+t)^(1/4)`, `B_j=alpha P_j`, where `P` is the
preserved rational degree-32 kernel. Let `Q_j` be the independently reconstructed
degree-32 potential derivative kernel. The actual six-row extraction is used
in both constructions; none of the seven-row directional constants is reused.

The full finite-x exponential and its differentiated recurrence, auxiliary
cycle image sum, finite-boundary walk tail and complex-time Cauchy tails are
proved in the preceding [physical derivative proof](../../structured_transfer_2026_09/resolution/PROOFS.md).
They apply here because every displacement is at most 25, within that
kernel's declared maximum 26. The current consumer recomputes all complete
remainders, with **12 matrix entries**, and obtains

\[
\|A_j(t,4/5)-B_j(t)\|<\rho=10^{-9},\quad
\|A_{j,g}-\alpha Q_j\|<10^{-12},\quad
\|A_{j,t}-B'_j\|<10^{-12}.
\]

In particular it checks the entire periodic image series, all omitted finite
walk powers, and the derivative tails `6/3^32` and `67/(2*3^32)`. It does not
differentiate a mere uniform value-error inequality. The recorded fresh
physical replays reconstruct the nominal and derivative coefficients at
320 and 384 bits, respectively, without modifying their saved premises.

Write `h=d=1e-8`. A sequential Taylor expansion at `(t,4/5)` gives

\[
A_j(t+dt,4/5+dg)=B_j+dt B'_j+dg\,\alpha Q_j+E_j,
\qquad \|E_j\|\le\rho+r,
\]
\[
r={h^2\over2}+128hd+{128\over3}d^2+(h+d)10^{-12}
={2567503\over150000000000000000000}
<1.711669\,10^{-14}.
\]

The proof uses `||A_tt||<1`, `||A_tg||<128` and the potential second-order
remainder coefficient `128/3` on the entire parameter rectangle. The exact
consumer checks `||H(g)|| <=56/5+4d<45/4` and positivity of the entire potential
family. The mixed term is charged once, retaining the joint incidence of
clock and potential before taking norms.

## 2. Six-row directional bounds over all times

The physical forward and inverse-direction matrices are

\[
\alpha\{dt(P'_j+\beta P_j)+dg Q_j\},\quad
(P_j^TP_j)^{-1}P_j^T\{dt(P'_j+\beta P_j)+dg Q_j\},
\qquad\beta={1\over4(1+t)}.
\]

For either norm, convexity in `(dt,dg)` reduces the rectangle to its corners;
overall sign symmetry leaves `h T+d G` and `h T-d G`. Forming polynomial
Gram determinants and inverse numerators before interval evaluation retains
the cancellation in weak source directions. For each of the 21 targets,
128 exact rational cells cover all of [1,2]. The producer uses outward
polynomial Horner evaluation. The consumer independently translates each
polynomial to the cell center and bounds its full power series. Every stored
cell bound is checked, not just the displayed global constants.

All 2,688 cases prove the conservative rational limits

\[
F:=\sup\|dt B'_j+dg\,\alpha Q_j\|<4.3\,10^{-10},\qquad
V:=\sup\|B_j^\dagger(dt B'_j+dg\,\alpha Q_j)\|<6.8\,10^{-7}.
\]

The producer's tighter global enclosures are below `4.274161e-10` and
`6.761419e-7`. The certified separate limits are `L_t<.023`, `L_g<.022`,
`C_t<46` and `C_g<23`. The displayed contract uses the rounded joint limits.

## 3. Reprove the enlarged pair separation

Set `delta_*=13/400000000 =3.25e-8`, `alpha_0=19/16`, and
`b_*=delta_*/alpha_0`. Every individual polynomial map satisfies

\[
P_j^TP_j\succ10^{-9}I,
\quad\text{so}\quad
B_j^TB_j\succ\mu I,\qquad\mu={361\over256\,10^9}.
\]

For every distinct pair `(j,k)` and every time cell, a rational `0<a<1`
satisfies

\[
[P_j,-P_k]^T[P_j,-P_k]
\succ\operatorname{diag}\left({b_*^2\over a}I_2,
                               {b_*^2\over1-a}I_2\right).
\]

The new certificate contains 1,280 records covering all 21 single-target and
210 pair cases. Positive leading principal minors prove each inequality by
Sylvester's criterion. The producer expands determinants by permutations;
the independent exact-rational consumer uses fraction-free Bareiss elimination
and interval Horner evaluation after polynomial translation. It checks every
declared lower bound, endpoints, adjacent cells, label pair and split.

This is a new, enlarged tube certificate. Reusing the former `3.2e-8` pair
certificate would leave the joint clock/potential contribution uncovered.
The two candidate explanations may have **different** unknown clock and
potential values. If their nominal tubes intersect, their difference has norm
at most `delta_*(||u||+||v||)`. Weighted Cauchy--Schwarz gives

\[
(\|u\|+\|v\|)^2\le\|u\|^2/a+\|v\|^2/(1-a),
\]

contradicting the strict pair Gram inequality after multiplication by
`alpha^2 >= alpha_0^2`. Thus the tubes for different target answers are
disjoint even with independently chosen admissible uncertainties.

## 4. Full transfer and raw decoder

Charge sensor error `eta=3e-8`, nominal-model error `rho=1e-9`, verified
normalization error `xi<=1e-9`, and the nonlinear remainder `r`. Put
`b=eta+rho+xi+r`. The actual data lie in their correct nominal tube because

\[
b+F={4864502567503\over150000000000000000000}
<3.243001712\,10^{-8}<\delta_*.
\]

After the target is identified, ordinary nominal least squares satisfies

\[
{\|\widehat u-u\|\over\|u\|}
\le {b\over\sqrt\mu}+V
<0.000852831068<0.001.
\]

The square-root inequality and the strict tube gate are verified with exact
rational arithmetic and an outward rational square root. At this particular
small rectangle the coarser source bound `(b+F)/sqrt(mu)` is also below
`0.000863601842`, so structured inversion is **not necessary** to pass the
source gate here. Its sharper bound is useful, but the principal new
consequence is combining six-channel acquisition with a fixed nonzero physical
uncertainty contract. No maximal tolerance or optimal bank is asserted.

The raw decoder accepts six exact rational readings and a nominal time. It
uses the preserved exact quartic normalization receipt. Because the true
generator is positive semidefinite, the raw source-to-output gain is at most
`4/3+eta`, even though the actual time is uncertain. Hence the wrapper still
charges at most `xi` in physical units at the nominal time. It does not assume
that nominal time equals true time.

For each candidate label the decoder tests the scalar relative tube by exact
quadratic completion. Its feasibility minimizer uses `P^T P-b_tube^2 I`;
its reported source estimate uses ordinary `P^T P`. These are intentionally
different solves. Only the unique compatible target receives the source
accuracy guarantee. The synthetic fixtures reconstruct actual finite-model
readings at true times and potential endpoints, not from the nominal Taylor
or derivative matrices. They test the route through the model and decoder;
the all-source/all-time guarantee comes from the proofs above.
