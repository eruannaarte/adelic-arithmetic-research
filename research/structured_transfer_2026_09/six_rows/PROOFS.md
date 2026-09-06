# Six spatial channels with a fixed noise contract

Let `Lx,Ly` be the reflecting path Laplacians on 1,001 vertices, let
`V=diag(1+(4/5)(i+1/2)/1001)`, and let
`H=I⊗Lx+Ly⊗V`. The two source columns are the orthonormal first and second
midpoint cosine modes in x. An input is a target `j∈{490,…,510}` and a nonzero
real coefficient vector `u∈R²`. Each output row averages globally in x at one
y coordinate, after applying `exp(-tH)` and multiplying by
`α(t)=(1+t)^(1/4)`. Time is known exactly and lies in `[1,2]`.

Use the six y coordinates

\[
R=(485,493,499,501,507,515).
\]

The physical model and the independently reconstructed finite-x Taylor kernel
are those of `transfer_theorem_2026_09/resolution`. The present consumer checks
the exact model metadata, kernel digest, coefficient enclosure widths, and the
complete transfer remainders. With `P_j(t)` the resulting degree-32 rational
polynomial matrix,

\[
\|A_j(t)-\alpha(t)P_j(t)\|_{2\to2}\le\rho=10^{-9},
\qquad a_0=19/16<\alpha(t)<4/3.
\]

The complete model bound includes the Taylor remainder `2^-33`, all periodic
images below `10^-24`, finite boundary effects below `10^-500`, and coefficient
rounding below `2·10^-30` per entry. The sum, multiplied by `(4/3)√12`, is below
`10^-9`. No finite tail truncation substitutes for these bounds.

## Weighted separation lemma

Suppose an approximate normalized reading `z` from source `(j,u)` obeys
`||z-P_j u||≤b||u||`. For a second explanation `(k,v)`, where `j≠k`, suppose
the same inequality holds. The triangle inequality would imply

\[
\|P_j u-P_k v\|\le b(\|u\|+\|v\|).
\]

For any fixed `a∈(0,1)`, weighted Cauchy gives

\[
(\|u\|+\|v\|)^2
\le\frac{\|u\|^2}{a}+\frac{\|v\|^2}{1-a}.
\]

Consequently, with `M=[P_j,-P_k]`, the strict matrix inequality

\[
M^TM\succ b^2\operatorname{diag}
 (a^{-1},a^{-1},(1-a)^{-1},(1-a)^{-1}) \tag{1}
\]

excludes two explanations. The scalar `a` is fixed before considering `u,v`;
(1) holds for *every* source pair. It can depend on the target pair and the
known time cell. This retains the two source blocks in their joint difference
map. The choice `a=1/2` gives the older uniform sufficient floor `2b²`.

## Exact complete-time certificate

Fix, without reducing the acquisition contract,

\[
\eta=3\cdot10^{-8},\quad \rho=\xi=10^{-9},\quad
\delta=\eta+\rho+\xi=3.2\cdot10^{-8},\quad b=\delta/a_0.
\]

For each of the 21 targets the certificate proves

\[
P_j(t)^TP_j(t)\succ 10^{-9}I_2. \tag{2}
\]

For each of the 210 target pairs it proves (1). Its 1,278 records cover the
entire closed time interval separately for every target and pair, without gaps
or overlapping interiors. A record fixes rational endpoints and, for a pair,
a rational weight `a`.

All entries of each matrix in (1) or (2), after subtracting its right-hand
side, are rational polynomials of degree at most 64. Every leading principal
minor is a rational polynomial of degree at most 256. Translate such a
polynomial to the center of its cell:

\[
p(c+h)=\sum_{k=0}^{d}p_kh^k,\qquad |h|\le r.
\]

Every stored bound is recomputed and verified to satisfy

\[
0<\ell\le p_0-\sum_{k=1}^{d}|p_k|r^k.
\]

Thus all leading principal minors are positive at every time in that cell.
Sylvester's criterion gives positive definiteness. It can also be seen from
symmetric Gaussian elimination: the successive pivots are ratios of these
positive minors, producing an `LDLᵀ` factorization with positive diagonal.
The producer uses determinant permutation expansions; the consumer reconstructs
the matrices and uses exact fraction-free elimination with checked polynomial
division. Neither a sampled singular value nor a floating preconditioner is a
certificate premise. Numerical values only propose the rational weights.

## Decoder, normalization and source accuracy

For raw rational readings `y`, the preserved normalization procedure constructs
rational `r` and verifies the quartic inequalities bounding `|αr-1|`. Since
`H` is positive semidefinite, `||A_j||≤4/3`; therefore
`||y||≤(4/3+η)||u||`. The wrapper charges
`||α(ry)-y||≤ξ||u||`. It needs no source amplitude or target input. Consequently
`z=ry` belongs to the true source tube with radius `b||u||`.

For every candidate target, the exact decoder minimizes
`||z-P_jv||²-b_actual²||v||²` over `v∈R²`, using the actual normalization
charge, which is no larger than `ξ`. The positive source floor makes this a
strictly convex quadratic. At least one candidate is feasible and (1) makes
it unique. The returned source estimate is ordinary least squares at that
unique target, not the feasibility minimizer.

From (2), its relative error satisfies

\[
\frac{\|\widehat u-u\|^2}{\|u\|^2}
\le\frac{\delta^2}{a_0^2\,10^{-9}}
=\frac{512}{705078125}<10^{-6}.
\]

In particular the error is below `0.000852151`, beating the fixed `0.001`
requirement. No timing or potential uncertainty is claimed in this six-row
profile; that is the separate seven-row structured-uncertainty objective.

## Why retaining the two source blocks matters

At `t=1`, for targets 509 and 510, a stored rational four-vector gives an
exact Rayleigh upper bound below `1.416749·10^-15` for the smallest eigenvalue
of `MᵀM`. This is below the old required uniform floor `2b²`; their ratio is
below `0.975507`. Therefore no honest common lower eigenvalue bound can pass
that old sufficient gate on this bank. The weighted certificate nevertheless
proves recovery with exactly the same sensor, model and arithmetic budgets.
This is a certified gain from preserving source-block geometry, not a noise
reduction or a claim that a failed sufficient bound establishes impossibility.

## Why one cannot merely drop an old row

For each of the seven one-row deletions of the earlier bank
`(490,492,496,500,504,508,510)`, a rational time and two nonzero rational sources
at distinct targets give a physical output difference satisfying

\[
\|A_j u-A_k v\|<\eta(\|u\|+\|v\|).
\]

The consumer derives this from an exact polynomial response, an outward
rational fourth-root bound, and the complete model error `ρ(||u||+||v||)`.
The largest sufficient collision radius among the seven witnesses is below
`1.080·10^-9`, already much smaller than `η=3·10^-8`. The corresponding closed
physical noise balls intersect. A shared observation cannot determine both
distinct target labels, so every deletion layout fails the fixed contract.
This covers precisely those seven layouts. The redesigned six-row bank above
shows why it must not be presented as a six-channel impossibility theorem.
