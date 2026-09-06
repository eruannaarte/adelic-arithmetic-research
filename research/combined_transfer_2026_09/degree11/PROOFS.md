# Verified degree eleven and its cost–amplitude consequence

The missing odd degree can be certified using the existing complete physical
channels, but it needs its own inverse and its own parity-correct approximation.
The fixed B=4000, Omega=3 test fails this sufficient certificate. Degree eleven
nevertheless certifies B=500 in both specified norms with the same readings,
clock, sensor and mismatch allowances.

## 1. Exact experiment and the complete inverse

Use the source, positive even mass-one W, times, known a(1)=1 and complete
digital midpoint of the [complete-tail theorem](../../transfer_theorem_2026_09/noise/PROOFS.md).
There are 8,900 complex readings, at t_j=(2j+1−8900)/10. Every unknown integer
coefficient obeys 0≤a(n)≤d_14(n), including every n>50. No multiplicativity of
the actual coefficients or number-field realization is assumed. The nuisance
space is all complex polynomials in x=t/890 of degree at most eleven.
The constant nuisance is represented by the first arithmetic column and its
fitted value is discarded; known a(1) is returned separately.

Let Phi be the fifty arithmetic columns and Psi the eleven positive-degree
W-orthonormal polynomial columns. The degree-twelve polynomial construction
already encloses these exact first eleven columns: positive-leading weighted
orthogonal polynomials are unique and the construction is nested. Its complete
channel premises apply separately to every column. The degree-twelve **decoded
coefficient bias** does not follow to a smaller inverse and is not reused.

Here is the complete rational derivation used anew for p=11. Let q_n bound
the off-diagonal row sums of G=Phi*W Phi, q=max q_n<1, and let B_n be the
inherited complete uncentered arithmetic coefficient bias. Let c_nk bound
|(Phi*W Psi)_nk| and let C_k bound the entire centered tail channel
|(Psi*W h)_k|. For k,l=1,...,11 define

v_nk = c_nk + q_n max_m c_mk/(1−q),
M_kl = sum_n c_nk v_nl, m_k=sum_l M_kl, mu=max_k m_k,
Q_aug = max{max_n(q_n+sum_k c_nk), max_k sum_n c_nk}, f=1−Q_aug.

The Neumann series bounds G^−1 C componentwise by v. It bounds the inverse
of the exact nuisance Schur complement I−C*G^−1 C when mu<1. Put

R_k=C_k+sum_n c_nk B_n/(2n²),
s_k=R_k+m_k max_l R_l/(1−mu),
A_n=B_n/2+n² sum_k v_nk s_k.

This bounds every coefficient's complete centered tail after the actual
degree-eleven augmented inverse. Gershgorin gives X*W X ≥ f I for
X=[Phi,Psi]. Both mu<1 and f>0 are checked exactly. Every sum and Schur
coefficient here is recomputed for eleven columns, rather than truncating the
degree-twelve answer vector or retaining its inverse gain.

The inherited C_k include the full zero-extended second differences, the
uniform oscillatory finite-frequency bound for 51≤n≤10^12, and the entire
remote bound zeta(3/2)^14/(2·10^6) times the weighted L1 norm. Thus the
existing all-integer tail remains complete. The new full-vector replay
independently reconstructs all eleven physical columns, their 550 cross
entries per design, and their L1 and zero-extended second-difference bounds.
The unchanged arithmetic-channel enumeration through 10^6 is an explicitly
hash-bound inherited premise with its earlier replay route.

## 2. The odd-degree approximation

Assume an additional drift B sin(omega x+phi), with |B|≤B_max, |omega|≤Omega,
and arbitrary real phi. Its allowed family is a separate physical-model
premise. An even W gives orthogonality between odd and even functions.

For every omitted monomial x^k, 12≤k≤32, choose a rational polynomial q_k:

* for even k use the saved degree-ten approximant (degree at most ten);
* for odd k use the saved degree-twelve approximant, whose exact odd parity
  makes its x^12 coefficient zero (degree at most eleven).

This produces an actual polynomial of degree at most eleven in every case.
Write d_k≥||x^k−q_k||_W. The old exact rational approximants and their
complete 8,900-point norm bounds are bound by hash, degree and parity checks;
the present independent replay recomputes every norm directly. No claim that
the rational approximants are exactly optimal is needed.

A sine Taylor expansion through order 31 has complete remainder at most
|omega x|^33/33!, and a cosine expansion through order 32 has complete
remainder at most |omega x|^34/34!. This follows from Taylor's theorem,
using the zero even/odd coefficients at the intervening orders and the
unit bound on every derivative. Let m_r≥||x^r||_W, r=33,34, and put

K_odd(Omega) = sum_(k=13,15,...,31) d_k Omega^k/k!
              +m_33 Omega^33/33!,
K_even(Omega) = sum_(k=12,14,...,32) d_k Omega^k/k!
               +m_34 Omega^34/34!,
K_W,11(Omega)=max(K_odd,K_even).

The remainder after the constructed polynomial has odd and even pieces of
norm at most |B cos(phi)|K_odd and |B sin(phi)|K_even. Orthogonality makes
the squared norm no larger than B² K_W,11². The bound holds at every phase
and every frequency within the declared interval. For an odd degree the
first omitted even order is twelve and the first omitted odd order is
thirteen; an even-degree implementation's alternating loops cannot simply
be retained with p set to eleven.

## 3. Joint clock, mismatch, noise and computed residual

Allow the same shared affine clock at all readings, with
|delta_a|≤10^−14 and |delta_b|≤10^−11. Affine composition preserves the
entire degree-eleven polynomial space. The sinusoid's effective frequency
is at most Omega_eff=3(1+10^−14); the clock offset is absorbed into its
already arbitrary phase. The source clock distortion is charged by the
complete weighted pairing certificate, or by the separately proved complete
[orbit certificate](../blocks/PROOFS.md). The latter's use is separately
recorded in orbit_comparison.json.

For eta=4·10^−5, mismatch kappa=10^−6, digital centering Xi=10^−20, and a
certified normal residual rho, set

delta = eta+kappa+Xi+tau_W+B_max K_W,11(Omega_eff),
E_n = A_n+n²(delta/sqrt(f)+rho/f).

The normal residual is ||X*W X theta_tilde−X*W(y−u_tilde)||_2 for the exact
physical model, evaluated from all raw readings. The least-squares inverse
gain is at most 1/sqrt(f); the residual-to-solution gain is at most 1/f.
These give the displayed coefficient bound for every admissible source.
The exact strict rounding test checks m_n=1/2−A_n−n² rho/f>0 before testing
n^4 delta² < m_n² f. A smaller outward rational lower bound for sqrt(f)
is used only to display E_n and amplitude thresholds. The strict gate itself
uses f and exact rational squares.

All uncertainties are charged jointly. Their physical membership cannot be
inferred from a small normal residual. No independence, empirical apparatus
calibration, or random-noise law is asserted.

## 4. What the comparison establishes

With the complete orbit clock, B_max=4000 gives displayed upward bounds
1.092523325 (multiscale) and 1.142117571 (outer). Only 32 of the 49 scalar
gates pass in either case. Therefore this degree-eleven sufficient certificate
is inconclusive for the fixed all-coefficient requirement. This neither
exhibits ambiguity nor proves an optimal degree lower bound.

At B_max=500, the same construction gives upward bounds 0.445865330 and
0.494913819, and all 49 scalar gates pass. The actual computed inverses are
also certified: both raw synthetic data sets have a nonzero degree-eleven
polynomial with coefficients of scale 10^20, nonzero shared clock distortion,
nonpolynomial drift, separate mismatch and sensor terms. Their independently
evaluated normal and reading-space residual identities agree. The 384-bit
replay verifies every saved 320-bit residual upper bound and the exact
rational readings, rather than only comparing displayed answers.

The preceding degree-twelve construction passes the fixed B=4000 contract.
Consequently twelve remains the least passing degree among the explicitly
tested 6,8,10,11,12 under these constructions. Degrees not in that set, and
sharper approximation families at an already tested degree, have not been
excluded. The degree-eleven result supplies a real cost–amplitude option:
61 augmented columns instead of 62, with the same 8,900 physical readings.
