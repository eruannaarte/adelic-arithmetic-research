# Verified normalization of raw spatial readings

## 1. A target-independent physical upper bound

Retain the exact finite diffusion model and source metrics of the spatial
certificates. For selected rows $I$, its physical source map is

\[
A_j(t)=\alpha(t)P_I(I_y\otimes e^T)e^{-tH}(\delta_j\otimes U),
\qquad\alpha(t)=(1+t)^{1/4},\quad t\in[1,2].
\]

The generator is symmetric positive semidefinite, so the spectral theorem gives
$\|e^{-tH}\|_2\le1$. Restriction, projection onto the unit constant vector, and
the orthonormal source embedding are contractions. Therefore $\|A_j(t)\|_2
\le\alpha(t)<4/3$ for every target and every selected bank. For any of the
declared source norms $S\succeq I$, the same bound holds from source norm $S$
to physical output norm.

Suppose the unnormalized observation is
$y=A_j(t)u+\epsilon$, with $\|\epsilon\|_2\le\eta\|u\|_S$. Then

\[
\|y\|_2\le K\|u\|_S,\qquad K=4/3+\eta.                                  \tag{1}
\]

This bound uses the noisy observation and is independent of the unknown target,
direction and amplitude. Omitting the sensor contribution from $K$ is not
valid. The guarantee below assumes the exact rational input $y$ already
includes any acquisition or digitization error charged to $\eta$.

## 2. Exact scalar certificate and transfer

Take a positive rational $r$ and rational $0\le e<1$ such that

\[
(1-e)^4\le(1+t)r^4\le(1+e)^4.                                            \tag{2}
\]

The positive fourth root is strictly increasing, so (2) is equivalent to
$|\alpha(t)r-1|\le e$. Form the normalized rational data **exactly** as $z=ry$.
Its difference in physical coordinates satisfies

\[
\|\alpha(t)z-y\|_2
\le e\|y\|_2\le eK\|u\|_S.                                               \tag{3}
\]

Thus $eK\le\xi$ certifies the former conditional computed-data allowance
$\xi\|u\|_S$. The existing decoder receives the actual rational charge $eK$,
the same $\eta$, and $z$. Its approximate-map tube has total radius
$\eta+\rho+eK$, with the established model error $\rho=10^{-9}$.

The seven-row, eight-row and nine-row theorems allow $\xi\le10^{-9}$, so
monotonicity of the common pair-separation and inverse gates preserves their
guarantees. The final inverse and its output are exact rational arithmetic;
there is no uncharged floating solve in this interface. A displayed or exported
rounded source estimate would need to account for that additional rounding.

The physical error in (3), rather than just $\|z-y/\alpha\|$, is what the
spatial certificate requires. Charging the latter directly would miss a factor
of $\alpha$. The [independent review](../review/NORMALIZATION_REVIEW.md) gives
explicit counterexamples to this mistake and to dropping $\eta$ from (1).

## 3. Construction without a numerical fourth root

The inverse normalization $c=(1+t)^{-1/4}$ lies in $[3/4,16/19]$. Exact
rational bisection maintains

\[
(1+t)\ell^4\le1\le(1+t)h^4.
\]

With $r=(\ell+h)/2$,

\[
|r/c-1|\le\frac{h-\ell}{2\ell}=:e.                                       \tag{4}
\]

The width tends to zero while $\ell\ge3/4$, so a positive budget is eventually
met. A final independent rational quartic check (2) verifies the receipt;
no floating approximation or saved iteration count establishes it.

A zero budget requires exact rational normalization. In lowest terms,
$1+t=a/b$ has a rational fourth root exactly when both $a$ and $b$ are perfect
fourth powers. This follows from prime exponents in a reduced rational fourth
power. The implementation checks this using integer square roots twice and
exact fourth-power equality. For example, $t=36975/28561$ gives $r=13/16$
exactly and costs zero. An irrational normalization with a zero budget is
rejected. Exhausting a user-selected bisection limit is also a refusal.

No source-amplitude lower bound is needed. Multiplying $y$ by any nonzero
exact rational scalar preserves the same receipt and scales $z$ accordingly.
Zero observations are rejected: the existing individual lower floors imply
$\|y\|_2\ge(\sqrt{\mu_S}-\rho-\eta)\|u\|_S>0$ for every promised nonzero
source. The selected sensor profiles satisfy this strict inequality.

## 4. Interface and proof boundaries

[normalize.py](normalize.py) implements the scalar certificate, exact data
scaling and content-hash bindings. `PhysicalBank('7')`, `PhysicalBank('8')` and
`PhysicalBank('9')` validate their spatial certificates and derive their sensor
and numerical budgets from the selected certified profile. A caller cannot
replace those budgets through an altered normalization receipt.

The wrapper returns `unique`, `incompatible` or `abstain` according to the
existing feasibility decoder. A source-accuracy result is emitted only with
a unique decision. Unsupported profiles, too many or too few readings,
unbudgeted numerical error, zero data, float inputs and invalid times are
rejected. The lower-level standalone receipt checker verifies the time and
sensor contract stated in its receipt; an external user must match those to
the actual acquisition. The wrapper constructs them from its explicit input
and validated profile.

The theorem establishes normalization under **known exact rational time** and
exact rational raw input. It does not establish the accuracy of an approximate
clock, infer a sensor error distribution, or calibrate a physical device. The
sensor/model assumptions persist. What is discharged is the previously
conditional arithmetic normalization error, now bounded by an actual exact
calculation on the input.

## 5. Demonstrations that satisfy the full physical promise

[demo.py](demo.py) constructs 72 exact raw cases: seven, eight and nine rows;
all eight certified profiles; three times; and source norm scales
$10^{-40}$, $1$ and $10^{40}$. For a certified polynomial map $P_j$ and source
$u$, it forms rational readings close to $\alpha P_ju$, then adds a rational
sensor perturbation of norm $\eta\|u\|_2/4$.

The raw fixture is certified against the actual finite graph. The full possible
difference $\rho\|u\|_2$ between the physical and polynomial map is charged to
its sensor budget. If $r_g$ and $e_g$ are the much more precise generation
scale and multiplier error, $\|P_j\|<2$ gives the additional generation charge
$2e_g/r_g$. The exact test is

\[
\rho+2e_g/r_g+\eta/4<\eta.
\]

Therefore these synthetic raw observations satisfy the full physical sensor
promise; they are not merely samples of an uncharged surrogate. The wrapper
is given only the raw data, time, bank and profile. True source labels are used
afterward to check its answers.

Every case returns its correct target and meets its source-error guarantee;
every normalization charge is at most $10^{-9}$. Eight focused tests include
the exact-root case, 195 additional scalar budget checks, amplitude and sign
invariance, corrupt receipts, altered readings, refused input contracts and
incompatible observations. Independent review supplies separate endpoint and
failure controls. These are exact synthetic verification results, not new
physical measurements.
