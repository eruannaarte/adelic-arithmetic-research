# Independent audit: clocks and unbounded polynomial nuisance

This note supplies complete elementary proofs. The obstruction concerns a
uniform additive error budget after the declared nominal nuisance elimination;
it is not an impossibility theorem for every joint clock/source decoder.

## General acquisition criterion

Let N be the nominal nuisance subspace in the actual retained, weighted
measurement space, and let L be its exact quotient map (so ker L=N). Under
acquisition parameter tau, let B_tau map an unrestricted nuisance coefficient
vector beta to measurements. For a fixed source, a finite bound uniform in
beta for the post-quotient nuisance error exists **if and only if**

    ran B_tau ⊆ N for every admissible tau.

Indeed this inclusion makes the quotient identically zero. If it fails, choose
beta0 with L B_tau beta0 !=0; scaling beta=c beta0 makes its norm unbounded.
Subtracting a nominal nuisance term does not alter the conclusion because L
annihilates that term. The same argument holds for any positive definite
physical weighting, or after restriction using its correctly transported norm.

A bounded source norm, tiny clock error, or tiny solver normal residual cannot
supply the missing nuisance-amplitude bound. In particular, a normal residual
measures numerical error in solving the nominal least-squares equations; it
does not identify whether an unmodeled reading perturbation lies in the
nominal source or nuisance span.

## Exact characterization on an interval

Write P_p for real or complex polynomials of degree at most p, p>=1, on a
nondegenerate interval I. A clock map gamma:I→R preserves this nuisance family,
meaning f∘gamma lies in P_p for every f in P_p, **if and only if gamma is affine**
(including constant affine maps mathematically).

Proof: choosing f(s)=s gives gamma=r on I for a polynomial r with degree≤p.
Choosing f(s)=s^p gives r^p=q on I for a polynomial q with degree≤p. Equality on
an interval is polynomial equality. If r is nonconstant of degree d then
pd≤p, so d≤1. The converse follows by polynomial composition. A physical clock
may further require positive affine slope; this is an extra acquisition
assumption, not needed for the algebraic statement. When p=0 any clock works.

## Exact characterization on the actual finite grid

Let x_1,...,x_m be distinct nominal times and let s_1,...,s_m be their actual
sample times. Define

    V_p(x) = {(f(x_j))_j : f∈P_p}.

If m>p² and p>=1, then V_p(s)⊆V_p(x) **if and only if** there are constants
a,b such that s_j=a x_j+b at every sample.

Proof: inclusion applied to f(s)=s gives a polynomial r∈P_p satisfying
r(x_j)=s_j. Inclusion applied to f(s)=s^p gives q∈P_p satisfying
q(x_j)=s_j^p. Hence r^p−q has m distinct roots and degree at most p². Since
m>p² it is zero. As above, r has degree at most one. Conversely, substituting
s_j=a x_j+b into any degree-p polynomial gives a degree-p polynomial in x_j.

The actual experiment has m=8,900 and p∈{6,8,10,12}; in each case m>p². Thus
there is no finite-grid exception to the affine characterization for these
complete polynomial families. For sparse grids this size hypothesis matters:
when m≤p+1, V_p(x) is the entire measurement space, so every sampled clock map
is absorbed, at the expense of retaining no query information after quotient.
For larger but m≤p² grids the preceding proof makes no classification claim.

## Arbitrarily small per-reading jitter gives unbounded leakage

Suppose m>=p+2. Choose one index j0, set s_j=x_j for j!=j0 and
s_j0=x_j0+h for any nonzero arbitrarily small h. The linear nuisance
f(s)=c s changes the measurement vector by c h e_j0. The unit vector e_j0 is
not in V_p(x): a representing polynomial would vanish at m−1>p distinct
points and hence be zero, contradicting its value at j0. Therefore its exact
quotient is nonzero, and the quotient norm of this perturbation tends to
infinity with |c|.

It follows that a class allowing such independent jitter cannot have a finite
uniform post-quotient timing allowance while polynomial coefficients remain
unbounded. One must restrict the clock family (affine is sufficient here),
bound the nuisance amplitudes/derivatives, enlarge the exactly eliminated
space, or prove a different joint inference theorem.

## The positive affine-clock alternative

For actual time s=a t+b, every unrestricted polynomial beta(s/890) of degree
p is another unrestricted degree-p polynomial in nominal x=t/890. It is
therefore absorbed exactly without charging its coefficients.

A sinusoidal family A sin(omega s/890+phi) with |A|≤B, |omega|≤Omega and
arbitrary phase is contained in the nominal family with frequency bound
|a| Omega: the new phase is phi+omega b/890. This exact absorption of phase
is justified only because the declared phase set is unrestricted. A restricted
phase set must be propagated rather than silently enlarged as an equality.
The arithmetic source signal is not invariant under the affine clock and
must still receive a complete timing-error budget.

If 0≤a(n)≤d_14(n), its absolutely convergent Dirichlet series at real part 2
has uniform time derivative bound

    D = Σ_{n>=1} d_14(n) log(n)/n²
      = 14 ζ(2)^13 Σ_{n>=1} log(n)/n².

The identity follows from the positive 14-fold divisor convolution and
log(n_1...n_14)=Σ log n_i; Tonelli justifies rearrangement. Finiteness follows
from convergence of ζ(2) and Σ log n/n², and also justifies termwise
differentiation uniformly in time by the Weierstrass test. Thus, for fixed
positive weights of mass one, a complete timing allowance is

    ||F(a t+b)−F(t)||_W
       ≤ D sqrt(Σ_j w_j (|(a−1)t_j+b|)²).

For a clock box |a−1|≤epsilon_a, |b|≤epsilon_b, the envelope
D sqrt(Σ w_j (epsilon_a |t_j|+epsilon_b)²) is valid. It is deterministic:
there is no independence assumption between clock, source, drift or mismatch.
A separate model-mismatch radius is added in this same weighted norm unless
a proved joint uncertainty set yields a sharper support bound.

## A reproducible rational witness

Take nominal times x_j=j, j=0,...,p+1, and the functional

    ell_j=(-1)^(p+1-j) binomial(p+1,j).

The (p+1)-st forward difference annihilates every degree-p polynomial;
explicitly Σ_j ell_j j^k=0 for 0≤k≤p and equals (p+1)! for k=p+1.
Change only the first actual time to h=10^(-12) and use the linear nuisance
f(s)=10^20 s. The functional applied to the changed readings has absolute
value exactly 10^8. Under uniform weights W=I/(p+2), its dual norm squared is
(p+2) binomial(2p+2,p+1), by the coefficient identity
Σ_j binomial(p+1,j)^2=binomial(2p+2,p+1). Therefore the squared quotient norm
is at least 10^16 divided by this explicit positive integer. Arbitrarily
large linear nuisance amplitudes give arbitrarily large quotient errors.
The standalone `clock_review.py` checks every rational moment, leakage and
dual norm for p=6,8,10,12. The interval and finite-grid general statements
above do not depend on these examples.
