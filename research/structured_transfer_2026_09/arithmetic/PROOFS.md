# Complete weighted affine-clock distortion

The model retains the 8,900 nominal times `t_j=(2j+1-8900)/10`, the two
positive, mass-one, exactly even physical weight vectors W, and every source
`s(t)=sum_(n>=1) a(n)n^(-2) exp(-it log n)`, where `a(1)=1` and
`0<=a(n)<=d_14(n)` are integers. No assertion of number-field realization is
made. The clock rectangle with multiplier h is

`t'=t+delta_a*t+delta_b`, `|delta_a|<=h/10^14`, `|delta_b|<=h/10^11`.

The multiplier is nonnegative. The base comparison fixes h=1; the additional
example uses h=60. Sensor, mismatch and correction radii remain respectively
`4e-5`, `1e-6`, and `1e-20` in the absolute physical weighted norm.

## 1. Complete first and second derivative envelopes

Put `Z=sum n^-2`, `L1=sum log(n)n^-2`, and `L2=sum log(n)^2 n^-2`.
Counting ordered fourteen-tuples and summing nonnegative terms gives

`D1=sum d_14(n)log(n)n^-2=14 Z^13 L1`,

`D2=sum d_14(n)log(n)^2 n^-2=14 Z^13 L2+182 Z^12 L1^2`.

For N=1000, the tail of each decreasing summand lies between its integrals
from N+1 and from N. The upper integrals for Z,L1,L2 are respectively
`1/N`, `(log N+1)/N`, and `(log(N)^2+2 log N+2)/N`.
Lower integrals use N+1. These finite calculations give outward intervals
for all three complete series. D1 uses the unchanged historical rational
upper bound, below 8473.355258; the new D2 bound is below 80762.59. Thus the
improvement below is not credited to a changed D1 approximation.

For real v, integration twice proves `|exp(-iv)-1+iv|<=v^2/2`. Absolute
convergence therefore gives the exact decomposition

`s(t_j+delta_j)-s(t_j)=V_j(delta_a,delta_b)+R_j`,

`V_j=-i delta_j sum a(n)log(n)n^-2 exp(-it_j log n)`,

`|R_j|<=D2 delta_j^2/2`.

The series and nonlinear remainder include every n, with no finite cutoff
in the source class. N=1000 is only an elementary integral comparison for
three one-dimensional positive generating series.

## 2. The shared clock is retained across the physical readings

For a fixed source, V is linear in its two shared clock errors. Its W-norm
is convex, so its maximum on the clock rectangle is bounded by the maximum
at the four corners. At a corner write

`delta_j=(h/10^11)d_j`, `d_j=epsilon_b+epsilon_a*t_j/1000`,

with epsilon_a and epsilon_b independently in {-1,1}. Exact evenness of W
and of the nominal grid makes

`S2=sum W_j d_j^2=1+E_W[t^2]/10^6`,

`S4=sum W_j d_j^4=1+6 E_W[t^2]/10^6+E_W[t^4]/10^12`

the same at all four corners. The quartic moment is convex in the clock
parameters, so it also bounds the nonlinear remainder throughout the
rectangle. The producer sums actual physical samples; the consumer verifies
all four corners independently. Hence

`||R||_W <= h^2 D2 sqrt(S4)/(2*10^22)`.

The pointwise D1 bound already improves to `h D1 sqrt(S2)/10^11`. However,
the next step gains additional information from the actual arithmetic phases.

## 3. A complete pairing of the infinite oscillatory source

Every positive integer is in exactly one pair (n,2n) with v2(n) even. In
every such pair the phase gap is log 2, independently of n. Put

`gamma=max_corners |sum W_j d_j^2 exp(it_j log 2)|/S2`.

This is one weighted phase correlation, checked at every clock corner. It
is below 2.959e-8 for both windows. With `c_n=d_14(n)log(n)/n^2`, any actual
pair satisfies

`||d*(a(n)log(n)n^-2 phi_n + a(2n)log(2n)(2n)^-2 phi_(2n))||_W`

`<=sqrt(S2)*sqrt(c_n^2+c_(2n)^2+2 gamma c_n c_(2n))`.

Here the envelope is used only after bounding the cross term by its
absolute value. The resulting expression is monotone in each nonnegative
coefficient magnitude. No ratio condition is imposed on actual a(n), which
may vanish independently. The ratio conditions below concern only c_n.

If k=v2(n), multiplicativity and stars-and-bars counting give
`d_14(2n)/d_14(n)=(k+14)/(k+1)`. For even k>=2 this implies

`r=c_(2n)/c_n in [(k+14)/(4(k+1)), (k+14)/(4k)]`.

For k=0 and odd n>=3 the interval is `[7/2,35/6]`, because
`log 2/log 3<2/3` follows from 8<9. Pair (1,2) has c_1=0 and is charged
separately by c_2=14 log(2)/4. Every other pair has `1/4<=r<=35/6`.

For an interval [l,u], set
`q=min(l/(1+l)^2,u/(1+u)^2)`. Differentiation of r/(1+r)^2, whose maximum
is at r=1, shows that this is its minimum on that interval. Then

`sqrt(c_n^2+c_(2n)^2+2 gamma c_n c_(2n))`

`<=(c_n+c_(2n))*sqrt(1-2(1-gamma)q)`.

The universal interval gives q0=210/1681. Each even valuation class has a
stronger q_k. The executable certificate uses rational upper bounds F0 and
F_k for these square roots and checks `0<F_k<=F0<1` exactly.

## 4. Summing complete valuation classes without truncating the source

Write `Zodd=(3/4)Z`, `Lodd=(3/4)L1-(log 2)Z/4`,
`Godd=Zodd^14`, and `Dodd=14 Zodd^13 Lodd`.
These follow by separating the even integers in the two positive series.
The total derivative mass for exact valuation k is

`M_k=binom(k+13,13)4^(-k) [Dodd+k(log 2)Godd]`.

Thus the full mass of pairs with even first valuation k is M_k+M_(k+1).
For k=0 subtract c_2 to remove the exceptional pair. The producer gives
positive lower bounds m_k for these complete masses, for k=0,2,...,38,
using the elementary series enclosures above. The consumer independently
checks them, and also checks D1,D2,Godd,Dodd by an outward zeta power series.

All other valuation classes continue to receive the universal factor F0.
Starting from that complete bound and subtracting only verified savings gives

`Bpair = F0 D1_upper + (1-F0)c2_upper
         - sum_(k=0,2,...,38) (F0-F_k)m_k`.

Consequently the triangle inequality over all integer pairs proves

`||s(t')-s(t)||_W <= h Bpair sqrt(S2)/10^11
                         + h^2 D2_upper sqrt(S4)/(2*10^22)`.

This is the certificate's exact linear-plus-quadratic radius. The infinite
remaining valuation classes are included by F0, not discarded. Cross-pair
phase cancellation is deliberately unused; no optimality is claimed.

## 5. Nuisance removal and complete query recovery

For any degree-p polynomial beta, `beta((1+delta_a)x+delta_b/890)` is still
degree at most p. The unbounded polynomial nuisance is therefore absorbed
exactly by the same augmented nominal solve. A sinusoid of amplitude at most
4000 and frequency at most 3 has effective frequency at most
`3(1+h/10^14)`; arbitrary phase already includes the offset. The unchanged
verified weighted approximations supply the entire sinusoidal remainder.

An orthogonal W-nuisance projection is contractive, so the same complete
clock bound remains valid after the correct nuisance operation. This result
does not claim a smaller projected bound: its new improvement comes from
retaining the shared clock direction and arithmetic phase correlation before
that contraction. The source/clock incidence is preserved in each pair and
corner. It is not replaced by independently variable errors at 8,900 samples.

For each inherited complete tail A_n, Gram lower bound f, and freshly verified
normal residual rho, use

`delta=4e-5+1e-6+clock_radius+4000*K_(W,p)(3(1+h/10^14))+1e-20`,

`E_n=A_n+n^2[delta/sqrt(f)+rho/f]`.

The unchanged strict rational gates `m_n>0`,
`n^4 delta^2 < m_n^2 f`, where `m_n=1/2-A_n-n^2 rho/f`, certify unique
rounding of every n=2,...,50. All error sources are charged jointly without
an independence assumption. The family bound, complete arithmetic tail,
clock distortion, model mismatch, correction and solve residual are separate
premises. In particular, the actual residual cannot establish clock or
mismatch calibration.

The degree comparison fixes h=1 and rho<=1e-30 before evaluating p=6,8,10,12.
The result identifies the least passing degree in this tested set, not among
all integer degrees or all possible approximations. The h=60 example is a
separate, explicitly declared consequence using the same amplitude,
frequency, sensor, mismatch and accuracy requirements.
