# Recovery with an uncertain affine clock and separate model mismatch

All norms below are the actual positive, mass-one physical weighted norm on
the 8,900 nominal samples. The two windows and infinite arithmetic tail
certificate are unchanged. Degree means one of 6, 8, 10 or 12. Polynomial
coefficients may be arbitrarily large and complex. A sinusoid has real
amplitude and phase; its sign is immaterial.

## 1. The permitted clock and the nuisance space

Write `x=t/890`, `t'=a*t+b`, `|a-1|<=epsilon_a`, `|b|<=epsilon_b`.
For every degree-p polynomial beta, `beta(a*x+b/890)` is again a
degree-at-most-p polynomial, by the binomial theorem. Thus affine clock
uncertainty preserves the nuisance space exactly. The augmented solve
absorbs the entire polynomial regardless of its coefficient size.

The sinusoid becomes

`A sin(omega*a*x + phi + omega*b/890)`.

Consequently `|omega|<=Omega` gives effective frequency bound
`Omega_e=(1+epsilon_a)*Omega`, and arbitrary phase already includes the
offset. There is no separate bounded-derivative assumption on beta and no
term proportional to its unknown coefficients.

Arbitrary independent jitter cannot receive this guarantee. Take beta(s)=Cs
and a sampled jitter vector delta outside the degree-p polynomial sample
space. If Q is the weighted orthogonal projection onto its complement, the
surviving nuisance is `C Q delta`, whose norm tends to infinity with C.
A one-sample nonzero jitter vector is outside this polynomial space when
the number of distinct samples exceeds p+1: a nonzero polynomial cannot
vanish at all the other samples. The jitter magnitude can be arbitrarily
small. Hence a uniform finite leakage budget requires preservation of the
nuisance space, an amplitude restriction, or an explicit leakage allowance.

## 2. A complete arithmetic timing bound

For an admissible source define

`s(t)=sum_(n>=1) a(n)*n^(-2)*exp(-i*t*log n)`,
`|a(n)|<=d_14(n)`.

The divisor coefficient d_14(n) counts ordered fourteen-tuples of positive
integers with product n. Tonelli's theorem for nonnegative summands gives

`sum d_14(n)*log(n)/n^2 = 14*Z^13*L`,

where `Z=sum k^(-2)` and `L=sum log(k)/k^2`. Both series converge. Uniform
absolute convergence of the differentiated signal series therefore implies

`|s(t')-s(t)| <= D*|t'-t|`, where `D>=14*Z^13*L`.

Equivalently, this inequality follows directly by summing
`|exp(-it'log n)-exp(-itlog n)|<=|t'-t|log n`, without interchanging
differentiation and summation.

For N=1000 the elementary integral comparison gives

`Z <= sum_(k=1)^N k^(-2)+1/N`,
`L <= sum_(k=2)^N log(k)/k^2 + (log N+1)/N`.

The second integrand decreases on `[N,infinity)`. Evaluating these finite
expressions outward yields `D < 8473.355257915`. The certificate uses the
full rational upper bound, not this rounded display. Since `|t_j|<890`,

`||s(t')-s(t)||_W <= D*(890*epsilon_a+epsilon_b) =: tau`.

The declared `epsilon_a=1e-14`, `epsilon_b=1e-11` give
`tau < 1.601465e-7`. This is a uniform complete-source bound. The much
smaller distortion of the finite synthetic example does not replace it.

## 3. A uniform weighted approximation for every tested frequency family

Let p be even and C=32. For each k=p+1,...,C the artifact gives a fixed
rational degree-p polynomial q_k of the same parity as x^k and an outward
bound `d_k>=||x^k-q_k||_W`. It also gives
`m_33>=||x^33||_W` and `m_34>=||x^34||_W`.

The weights and nominal grid are exactly even. Thus every odd sample vector
is W-orthogonal to every even one. Define for any finite nonnegative Omega_e

`R_o = sum_(k=p+1,p+3,...,31) d_k*Omega_e^k/k!
       + m_33*Omega_e^33/33!`,

`R_e = sum_(k=p+2,p+4,...,32) d_k*Omega_e^k/k!
       + m_34*Omega_e^34/34!`,

`K_(W,p)(Omega_e)=max(R_o,R_e)`.

Taylor's theorem applied to sin through degree 32 bounds the full odd
remainder by `|omega*x|^33/33!`. Applied to cos through degree 33 it bounds
the full even remainder by `|omega*x|^34/34!`. All derivatives have modulus
at most one for real arguments, so these bounds hold uniformly for any
finite Omega_e, not only Omega_e<=1.

Replace each Taylor monomial of degree above p by q_k. The triangle
inequality bounds the odd residual by R_o and the even residual by R_e.
For phase phi the residual is their combination with coefficients cos(phi)
and sin(phi). Orthogonality bounds its squared norm by
`cos(phi)^2 R_o^2 + sin(phi)^2 R_e^2 <= max(R_o,R_e)^2`.
Multiplication by `|A|<=B` proves the existence of a degree-p polynomial
with residual at most `B*K_(W,p)(Omega_e)` for the entire continuum family.

The producer proposes q_k through weighted moment projection. The consumer
checks the fixed rational polynomials on all 8,900 physical readings,
independently of the projection or saved Gram matrices. No claim that these
q_k or the resulting uniform family bound are optimal is needed.

For `0<=Omega<=1`, positivity of every term also gives
`K_(W,p)(Omega) <= Omega^(p+1)*K_(W,p)(1)`.

## 4. The complete recovery budget

Subtract the known digital midpoint correction and use the unchanged
nominal arithmetic columns, augmented by all degree-p polynomial columns.
The true clocked polynomial and the approximating sinusoidal polynomial
belong to this exact augmented space. The remaining reading discrepancy is
bounded by

`delta = eta + kappa + tau + B*K_(W,p)(Omega_e) + Xi`,

where `eta=4e-5`, `kappa=1e-6`, and `Xi=1e-20` is the previously certified
digital correction error. Kappa is a separately declared physical mismatch
bound. No independence is assumed; the deterministic bounds add.

For the inherited complete tail bounds A_n, Gram lower bound f, and an
actually reconstructed normal residual rho of the exact returned proposal,

`E_n = A_n + n^2*(delta/sqrt(f) + rho/f)`.

The source integer is uniquely recovered when every E_n is strictly below
one half for n=2,...,50. Exact rational gates instead check positive
`m_n=1/2-A_n-n^2*rho/f` and `n^4*delta^2 < m_n^2*f`.
The answer also satisfies the checked complex error disk and divisor
envelope. The inherited arithmetic-tail A_n includes the entire infinite
source class; a saved finite test source or a tiny rho cannot replace it.

The strict sufficient amplitude capacity is

`B < [min_n {(1/2-A_n-n^2*rho/f)*sqrt(f)/n^2}
      - eta-kappa-tau-Xi] / K_(W,p)(Omega_e)`.

The implementation replaces sqrt(f) by a rational lower bound, so the
displayed capacity remains sufficient. It need not be the true maximal
admissible amplitude. Comparing this expression across p charges both the
improved approximation and its changed Gram/tail cost.

## 5. What the demonstrated data establish

The actual exact rational readings are reconstructed from t' with both
clock parameters at their declared positive endpoints, a degree-six
polynomial of size 10^20, `4000*sin(3*t'/890+1/3)`, separate mismatch
`9e-7*cos(t'/17)`, and sensor perturbation `3.9e-5*exp(i*t'/11)`.
The source has finitely many nonzero integer coefficients and satisfies
the complete divisor envelope. Quantization is outward bounded below
1e-35 and charged to eta. The mismatch has pointwise, hence weighted,
norm at most 9e-7<kappa. The entire degree-six nuisance is admissible for
every tested degree, so all eight comparisons use the same valid readings.

At degree 12 both windows certify all 49 unknown integers. Degrees 6, 8, 10
fail the sufficient gates, which does not establish nonidentifiability.
All eight actual nominal matrices, both forms of the residual, exact
readings and exact proposals replay at 384-bit precision. Other frequency
rows are design capacity calculations, not separate synthetic replays.
The capacity and planning tables use a declared future residual ceiling 1e-30; future
data must independently establish it and their uncertainty-family bounds.

This proves recovery under a specified clock and model-mismatch class.
It supplies no empirical clock calibration, physical noise distribution,
or number-field realization of the synthetic divisor-envelope source.
