# Audit of the explicit uniform lattice constants

**Audited artifact:** `OIG_UNIFORM_LATTICE_EXPLICIT_CONSTANTS.md`

**Verdict:** pass, with one minor proof-exposition repair recommended.  I
found no normalization, parity, source-metric, uniformity, or schedule error
that invalidates the theorem.  The constants (23), (23/10), (2/3), and
(1/15), and every integer threshold in Sections 7.1--7.2, are conservative
in the claimed direction.  The proof of the atomic high tail uses a valid
bound but omits the one-line inequality that actually establishes it; that
line should be inserted in the canonical text.

This audit is independent in the sense that all constants below were derived
again from the displayed definitions.  Exact schedule checks are encoded in
`test_oig_uniform_lattice_explicit_constants.py` using integer and rational
arithmetic only.

## 1. Normalization and parity

For midpoint nodes (x_j=(j+1/2)/n), the sampled cosine vectors satisfy

\[
 h\sum_{j=0}^{n-1}\phi_{k,h}(j)\phi_{m,h}(j)=\delta_{km},
 \qquad k,m=1,2,
\]

when odd (n\ge3).  The weighted constant vector also has norm one.  Thus
the contraction estimates in Lemmas 2.1--2.2 introduce no hidden factors of
(n), (h), or (\sqrt2).

At the unique centre cell (j_*=(n-1)/2),

\[
 \phi_{\ell,h}(j_*)=\sqrt2\cos(\ell\pi/2).
\]

Odd target modes vanish, positive even modes have squared coefficient (2),
and the zero mode has zero source response because both source ports have
exact discrete mean zero.  This reproduces exactly

\[
 G_n(\tau)=\frac{2\sqrt{1+\tau}}n
 \sum_{r=1}^{(n-1)/2}b_n(\tau,\omega_{n,2r})
 b_n(\tau,\omega_{n,2r})^T.
\]

Moreover (\xi_r=2r/n) are precisely the midpoints, with panel width (2h),
of the interval ([h,1]).  Since

\[
 \tau\omega(\xi_r)=4\tau\sin^2(\pi r/n)=s_r,
\]

the intermediate phase quadrature has the displayed normalization.  No
even-grid or displaced-target claim is smuggled into the theorem.

## 2. Re-derivation of (23)

The component amplitude constants satisfy

\[
 \sum_{k=1}^2d_k^2
 =10\pi^2+\frac{64}{25e^2}=A^2
\]

and

\[
 \sum_{k=1}^2m_k^2
 =2\left[\left(1+\frac4{5\pi e}\right)^2
 +\left(2+\frac4{5\pi e}\right)^2\right]=B^2.
\]

The outer-product inequality contributes (2\sqrt2g,s_re^{-s_r}).
Using (s_r\ge16tr^2),

\[
 se^{-s}\le\frac2e e^{-s/2},\qquad
 \sum_{r\ge1}e^{-8tr^2}
 \le\frac{\sqrt\pi}{4\sqrt{2t}},
\]

and (2\sqrt{1+\tau}/n\le2\sqrt2\sqrt t) gives

\[
 \frac{2\sqrt{1+\tau}}n\sum_rs_re^{-s_r}
 \le\frac{\sqrt\pi}{e}.
\]

Consequently the modal coefficient is

\[
 K=\frac{8\sqrt{2\pi}}{5e}.
\]

For the target quadrature,

\[
 \int_0^1\|H_\tau'(\xi)\|_2d\xi\le\frac{36}{25},
 \qquad
 \sup_\xi\|H_\tau(\xi)\|_2\le\frac{32}{25e^2}.
\]

Multiplication by (h\sqrt{1+\tau}\le\sqrt2\sqrt t) gives the stated

\[
 Q=\sqrt2\left(\frac{36}{25}+\frac{32}{25e^2}\right).
\]

The direction-safe weakenings re-check as

\[
 A<10,\quad B<\frac{17}{5},\quad K<\frac{37}{25},
 \quad Q<\frac{12}{5}.
\]

Therefore

\[
 C_{\sqrt t}<\frac{86}{5},\qquad
 C_h<\frac{629}{125},
\]

and, because (h\le\sqrt t) for (\tau\ge1),

\[
 C_{\sqrt t}\sqrt t+C_hh
 <\frac{2779}{125}\sqrt t<23\sqrt t.
\]

The energy comparison itself does not require (t\le1): its right side
merely grows like (\sqrt t).  Thus advertising (t_*=1) as an admissible
contract restriction is valid and does not conceal a missing small-time
hypothesis.

## 3. Re-derivation of (23/10) and the discrete metric transfer

For

\[
 S=\operatorname{diag}(1+\pi^2,1+4\pi^2),
\]

the generalized operator norm obeys

\[
 \|M\|_S
 =\|S^{-1/2}MS^{-1/2}\|_2
 \le\frac{\|M\|_2}{1+\pi^2}
 <\frac1{10}\|M\|_2.
\]

This gives (23/10) in the safe direction.  For the natural discrete metric,

\[
 n^2\omega_{n,k}=4n^2\sin^2\frac{k\pi}{2n}
 \le k^2\pi^2,
\]

so (S_n\preceq S).  A floor already proved relative to (S) therefore
also holds relative to (S_n); the direction in Section 7 is correct.

## 4. Re-derivation of (2/(3\tau)) and (1/(15\tau))

The substitution (s=4\tau\sin^2(\pi\xi/2)) gives

\[
 d\xi=\frac{ds}{\pi\sqrt{s(4\tau-s)}}
\]

and hence exactly the factor (1/(2\pi)), not (1/\pi), in the atomic
integral.  On (0\le s\le2\tau), setting

\[
 u=\tau^{-1},\qquad v=\frac{s}{4\tau}\le\frac12
\]

reduces the claimed estimate for (a_\tau-1) to

\[
 \sqrt{\frac{1+u}{1-v}}\le1+u+v.
\]

After squaring, the difference is

\[
 (1+u+v)^2(1-v)-(1+u)
 =-(u+v)\{u(v-1)+v^2+v-1\}\ge0,
\]

because (v\le1/2).  The low-phase coefficient simplifies to

\[
 C_{\rm low}
 =\frac{63\sqrt2}{800\sqrt\pi}<\frac3{40}.
\]

For the finite-lattice high region, the deliberately loose estimates
(s\le4\tau) and (e^{-2s}\le e^{-4\tau}) give

\[
 32g^2\tau^2\sqrt{1+\tau}e^{-4\tau}.
\]

The required multiple of (1/\tau) is maximized at (\tau=1), since
(\tau^3\sqrt{1+\tau}e^{-4\tau}) is decreasing there, and is less than
(27/50).

For the omitted atomic tail, the displayed constant is also valid, but its
proof needs the intermediate estimate

\[
 \begin{aligned}
 \int_{2\tau}^{\infty}s^{3/2}e^{-2s}\,ds
 &=\int_{2\tau}^{\infty}(s^{3/2}e^{-s})e^{-s}\,ds\\
 &\le(2\tau)^{3/2}e^{-2\tau}
       \int_{2\tau}^{\infty}e^{-s}\,ds\\
 &=(2\tau)^{3/2}e^{-4\tau}.
 \end{aligned}
\]

Here (s^{3/2}e^{-s}) is decreasing for (s\ge2\tau\ge2).  Multiplying by
(\tau), the factor (\tau^{5/2}e^{-4(\tau-1)}\) decreases for
(\tau\ge1).  It follows that

\[
 C_{\rm high,A}
 =\frac{g^2}{\pi}2^{3/2}e^{-4}<\frac3{250}.
\]

This intermediate line is absent from Section 6 of the audited manuscript.
The numerical constant is correct, but the canonical proof should add it.
The sum is exactly

\[
 \frac3{40}+\frac{27}{50}+\frac3{250}
 =\frac{627}{1000}<\frac23.
\]

Whitening costs strictly less than (1/10), so the declared (H^1) tail is
strictly less than (1/(15\tau)).

## 5. Exact schedule audit

Write the published rational floors as

\[
 \ell_{L^2}=\frac{14315}{10^{11}},\qquad
 \ell_{H^1}=\frac{35523}{10^{13}}.
\]

The direct schedules require one-half-floor error allocations.  Exact
cross-multiplication confirms

\[
 \frac{23}{322000000}<\frac{\ell_{L^2}}2,
 \qquad
 \frac{23}{10\cdot1300000000}<\frac{\ell_{H^1}}2.
\]

For the joint atomic schedules, the finite-continuum and continuum-atomic
errors each receive one quarter of the floor.  All four strict comparisons
hold:

\[
 \begin{array}{ll}
 \displaystyle\frac{23}{643000000}<\frac{\ell_{L^2}}4,
 &\displaystyle\frac{2}{3\cdot18629000}<\frac{\ell_{L^2}}4,\\[3mm]
 \displaystyle\frac{23}{10\cdot2590000000}<\frac{\ell_{H^1}}4,
 &\displaystyle\frac{1}{15\cdot75069000}<\frac{\ell_{H^1}}4.
 \end{array}
\]

The unrounded lower thresholds are approximately

\[
 \begin{array}{c|r}
 \text{condition}&\text{minimal real coefficient}\
 \hline
 n/\sqrt\tau\ (L^2\text{ atomic})&642682500.8732\\
 \tau\ (L^2\text{ atomic})&18628478.2862\\
 n/\sqrt\tau\ (H^1\text{ atomic})&2589871350.9557\\
 \tau\ (H^1\text{ atomic})&75068734.8103
 \end{array}
\]

so the published integer ceilings are safe.  The smallest slack is in the
(H^1) atomic-time comparison, but it is positive by exact rational
arithmetic.

For a literal proof-producing implementation with rational input (\tau),
it is cleaner to avoid evaluating a floating-point square root: select the
least odd (n) satisfying (n^2\ge C^2\tau).  This is an implementation
clarification, not a correction to the mathematical schedule.

## 6. Required and optional edits

1. **Recommended proof repair:** insert the atomic-tail integral estimate
   displayed in Section 4 above before equation (6.6).  Without it, (6.6) is
   asserted rather than derived, although the assertion is true.
2. **Optional wording repair:** in the finite high-phase paragraph, the
   factor (32) follows most transparently from (s\le4\tau) together with
   (e^{-2s}\le e^{-4\tau}), not from monotonicity of (s^2e^{-2s}).  The
   monotonicity observation would instead give the sharper factor (8).
3. **Optional implementation repair:** expose schedules as squared exact
   comparisons (n^2\ge C^2\tau), followed by odd-integer rounding.

None of these points changes a theorem constant, threshold, metric, or
Loewner conclusion.
