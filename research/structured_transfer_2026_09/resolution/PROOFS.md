# Joint clock and spatial-potential uncertainty

Keep the seven physical rows 490, 492, 496, 500, 504, 508, 510, every target
490 through 510, every nonzero real two-mode source, and both nominal and true
times in [1,2]. The finite reflecting paths each have 1001 vertices. Write

\[
 H(g)=I_y\otimes L_x+L_y\otimes\operatorname{diag}(1+g x_i),\quad
 x_i=(i+1/2)/1001,\quad g_0=4/5,
\]
\[
 A_j(t,g)=(1+t)^{1/4}R(I_y\otimes e^T)e^{-tH(g)}(\delta_j\otimes U).
\]

The spatial averages and orthonormal source columns are unchanged. This is a
specified physical parameter family, not an arbitrary saved-matrix error.
Throughout the certified family H(g) is self-adjoint positive semidefinite.
The derivative D=H_g=L_y tensor diag(x_i) has norm at most 4 and
||H(g0)|| <=56/5. No commutation between L_x and the spatial potential is used.

The prior complete source/pair certificate for the nominal polynomial map
B_j(t)=alpha(t)P_j(t), rechecked by `decoder.py`, gives

\[
 \sigma_{\min}(B_j)^2>\mu=1083/51200000000,\qquad
 \sigma_{\min}([B_j,-B_k])^2>\lambda=361/5120000000000000.
\]

Its full-model remainder rho=10^-9 is retained. All claims below charge raw
sensor radius eta=1.1e-7 and verified normalization radius xi<=1e-9, relative
to the nonzero source Euclidean norm. Define h=5e-7 and d=2.5e-6.

## 1. Reconstruct the actual potential derivative

Fourier reduction on the auxiliary transverse cycle of length 64 leaves the
**entire finite x path**, with modal generator
H_l=L_x+omega_l diag(1+g0 x), omega_l=4 sin²(pi l/64).
The zero Fourier mode is exactly zero because the source cosine modes have
zero mean. Opposite modes combine into exact real cosine weights.

Set c_l=2+(7/5)omega_l, r_l=2+(2/5)omega_l, c=3/2 and
D_l=omega_l diag(x). Then ||H_l-c_l I||<=r_l and ||D_l||<=omega_l.
Differentiating the order-80 shifted exponential power recurrence gives

\[
 S_n={c\over n}[-(H_l-c_lI)S_{n-1}],\quad
 \dot S_n={c\over n}[-(H_l-c_lI)\dot S_{n-1}-D_l S_{n-1}].
\]

The spectral center is held fixed while differentiating. The complete
exponential remainder and its differentiated remainder are bounded by

\[
 E_l=e^{-c\omega_l}{(cr_l)^{81}\over81!},\qquad
 E_{g,l}=c\omega_l e^{-c\omega_l}{(cr_l)^{80}\over80!}.
\]

For the time coefficient of order k, apply the differentiated recurrence
(-H_l)^k/k! to the enclosed center state. Its error is at most

\[
 {N_l^k\over k!}E_{g,l}
 + {\omega_l N_l^{k-1}\over(k-1)!}E_l \quad(k>0),
 \qquad N_l=4+(9/5)\omega_l.
\]

At k=0 only the first term remains. These bounds follow by summing all omitted
powers and all possible derivative positions. `kernel_derivative.py` applies
outward Arb actions and Fourier sums, then exports every coefficient to
rational intervals of width at most 10^-30. Their midpoints define Q_j(t),
a degree-32 approximation to the **unnormalized** potential derivative.

## 2. Complete derivative approximation errors

For any self-adjoint PSD H, exp(-zH) has norm at most one when Re z>=0.
Duhamel's identity along a complex segment gives
||partial_g exp(-zH)|| <= |z| ||D||. On the complex-time circle
|z-3/2|=3/2, this is at most 12. Cauchy's coefficient bound and summing the
entire geometric tail at |t-3/2|<=1/2 prove

\[
 E_{\rm value}\le {1\over2\,3^{32}},\quad
 E_{\rm potential}\le {6\over3^{32}},\quad
 E_{\rm time\ derivative}\le {67\over2\,3^{32}}.
\]

The third bound sums k(1/2)^(k-1)/(3/2)^k for all k>=33; it does **not**
differentiate a uniform value-error bound. Cauchy's formula is valid here
because the finite-matrix exponentials are entire in complex time.

All periodic images and the actual reflecting boundaries also need charging.
For the Laurent generator B(z)=L_x+(2-z-z^-1)V, take a=8 and v*=9/5.
The prior complete image sum is

\[
 I=e^{2v_*(a+a^{-1}-2)}
 {a^{-38}+a^{-90}\over1-a^{-64}}<10^{-24}.
\]

For its g derivative multiply I by 2(2+a+a^-1); for its time derivative
multiply I by 4+v*(2+a+a^-1). These follow from Duhamel and, respectively,
||B(z)|| times the same semigroup bound. Thus every image, not only the
nearest ones, is charged. A rational positive exponential series with a
complete geometric remainder verifies the numerical inequalities.

For actual finite boundaries, uniformize at q=28/5. Finite and infinite walk
powers, and their g derivatives, agree through order 490. The operator
derivative of a kth walk power has norm at most 4k/q. With m=2q, define
T_r=m^r/(r!(1-m/(r+1))). The finite-boundary differences are bounded by
2T_491, 16T_490 and 4q T_490 for value, g derivative and t derivative.
All are below 10^-490. The last two inequalities are obtained by
differentiating the full convergent walk series and summing its entire tail.

Combine these bounds, coefficient rounding, alpha<=4/3 and alpha'<=1/6.
The Frobenius norm over seven rows and two columns proves, uniformly,

\[
 \|A_{j,g}-\alpha Q_j\|<10^{-12},\qquad
 \|A_{j,t}-(\alpha P_j)'\|<10^{-12}.
\]

`check.py:remainders` verifies the exact rational squared inequalities. The
old rho=10^-9 is still charged once for the nominal value approximation.

## 3. Full nonlinear joint remainder

The same dt and dg act in every reading of one experiment. For |dt|<=h and
|dg|<=d, expand at (t,g0):

\[
 A_j(t+dt,g_0+dg)=B_j(t)+dt B'_j(t)+dg\,\alpha(t)Q_j(t)+E_j.
\]

The source operator norm of E_j is at most rho+r, where

\[
 r={h^2\over2}+128hd+{128\over3}d^2+(h+d)10^{-12}
   <4.268\,10^{-10}.
\]

Use a sequential expansion: first expand in g at the true time t+dt;
then expand A(t+dt,g0) in time, and expand A_g(t+dt,g0) about t.
Complex or real Duhamel integrals give ||E_g||<=4t and ||E_gg||<=16t²
along the entire positive potential segment. After alpha normalization the
pure-g second-order remainder is at most (128/3)d². The identity
A_tg=alpha' E_g-alpha(D E+H E_g), evaluated at g0 where
||H(g0)||<=56/5, gives ||A_tg||<128 on [1,2]. Multiplying its
time-difference bound by |dg| charges the cross term 128hd for every
point of the parameter rectangle. No bound ||H(g)||<=56/5 for g>g0
is used. Independently, throughout the rectangle one has
||H(g)||<=56/5+4d<45/4, which gives the uniform bound
(1/6)8+(4/3)(4+(45/4)8)=380/3<128 as well; the consumer checks
these exact inequalities. Finally, alpha''<=1/16 in absolute value, alpha'<=1/6,
||H exp(-tH)||<3/8 and ||H² exp(-tH)||<9/16 give
||A_tt||<15/16<1. Taylor's integral remainder gives h²/2.
The elementary inequality e>8/3 follows already from the first four terms
of its positive series. Approximate derivative replacement costs the final
(h+d)10^-12 term.

## 4. Retain the structured directions through inversion

At nominal time let beta=1/[4(1+t)]. Multiplication by alpha cancels from
nominal inverse influence:

\[
 B_j^\dagger[dt B'_j+dg\,\alpha Q_j]
 =(P_j^TP_j)^{-1}P_j^T
 [dt(P'_j+\beta P_j)+dg Q_j].
\]

For a rectangle of two scalar uncertainties, the norm of this matrix, and
the physical forward-direction matrix, is bounded by its largest corner
norm. This is convexity: every point is a convex combination of the corners.
Global sign symmetry leaves the two signs hT+dG and hT-dG. The shared
incidence is retained **before** taking Frobenius upper bounds on operator
norms. Replacing it by one independent perturbation per reading is unnecessary.

The producer covers every label with 128 equal rational time cells. It forms
polynomial Gram matrices and inverse numerators before interval evaluation;
this retains the small-direction cancellations. An independent consumer
translates each polynomial to the cell center and bounds its full power
series there. It proves all 2,688 label/cell cases, including strictly positive
Gram determinants, with

\[
 J_f:=\sup\|dt B'_j+dg\alpha Q_j\|<6.6\,10^{-8},\qquad
 J_q:=\sup\|B_j^\dagger(dt B'_j+dg\alpha Q_j)\|<2.8\,10^{-5}.
\]

Separately certified constants are L_t,L_g<0.024 for physical forward norms,
and C_t<18,C_g<8 for inverse influence. Their norm sums give 7.2e-8 and
2.9e-5, respectively. The joint-corner bounds reduce these particular
certified allowances by 8.33% and 3.45%. No optimality is asserted.

## 5. Separate label and source gates; actual decoder

Let b=eta+rho+xi+r. Two different admissible explanations may have different
unknown clock/potential values. Each has its own forward tube of radius
b+J_f. We do **not** equate their unknown parameters. Their tubes are disjoint
because

\[
 2(b+J_f)^2<\lambda.
\]

After identifying the target, nominal least squares has relative source error

\[
 {b\over\sqrt\mu}+J_q<0.000801020<0.001.
\]

The same b+J_f, divided entirely by sqrt(mu), exceeds 0.001. Thus the
query-specific inverse bound makes a material difference, not just a change
of vocabulary. `check.py` verifies both strict positive gates and this failed
comparison gate by exact rational arithmetic and an outward rational square
root. The source estimator is ordinary least squares, not the minimizer used
to test each candidate tube.

The decoder normalizes raw exact rational readings at the nominal time using
the earlier verified quartic wrapper. Since the true H(g) is PSD,
||A_j(t_true,g)||<=4/3; normalization error therefore costs at most
its verified scalar error times (4/3+eta), even though actual time is unknown.
The nominal map approximation and derivative remainders already account for
the physical clock discrepancy. No second normalization of the true clock is
silently introduced. Tube feasibility is evaluated with exact rational
quadratic completion; only a unique surviving label receives the source
accuracy guarantee. Calibration and family membership remain physical
premises, not conclusions inferred from a solver residual.
