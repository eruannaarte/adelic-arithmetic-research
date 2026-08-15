# Uniform late-lattice transfer: adversarial audit

- **Date:** 14 August 2026
- **Scope:** the proposed extension of the Stage XII two-port theorem from
  \(\tau=1\) to compact and late lattice-time ranges
- **Status:** obstruction analysis and sufficient theorem conditions; not
  peer reviewed
- **Canonical benchmark:** cell-centred Neumann path,
  \(V(x)=1+4x/5\), source ports \(k=1,2\), interior atomic target

## 1. Verdict

A compact-\(\tau\) finite transfer is mathematically coherent.  A positive
finite-grid floor uniform over every \(\tau\ge1\) at one fixed \(n\) is
impossible.

The reason is structural, not numerical.  At fixed \(n\), every responsive
finite target mode has a strictly positive generator gap, so the normalized
finite response Gram tends to zero as \(\tau\to\infty\).  In the continuum
lattice chart the active target frequency simultaneously moves toward zero;
after the declared \(\sqrt{1+\tau}\) normalization its Gram tends instead to
the positive interior-atomic Gram.

Thus the valid late theorem has to be one of the following.

1. A **compact-time theorem:** for each finite \(T\), certify all
   \(1\le\tau\le T\) once \(n\ge N(T)\).
2. A **coupled tail theorem:** certify pairs \((n,\tau)\) satisfying a
   resolution condition such as
   \(h\sqrt\tau\le\varepsilon_*\), equivalently
   \(\tau\le\varepsilon_*^2n^2\), with \(\tau\) allowed to grow as
   \(n\to\infty\).
3. A continuum-only \(\tau\to\infty\) theorem, clearly not presented as a
   finite-network transfer.

Stage VIII contains the qualitative ingredients for the second route, but
does not yet state an explicit, outward-rounded \(K=2\) Gram bound.  The
missing work is a finite-dimensional uniformization with computable
constants, followed by a strict comparison with the Stage X spectral floor.

## 2. The two limits do not commute

For the exactly centred odd-grid experiment, put

\[
 A_{n,\ell}=L_n+\omega_{n,\ell}V_n,
 \qquad
 \omega_{n,\ell}=4\sin^2\frac{\pi\ell}{2n},
\]

and

\[
 a_{n,\ell}(\tau)
 =\left(\mathbf1^Te^{-\tau A_{n,\ell}}u_{n,1},
        \mathbf1^Te^{-\tau A_{n,\ell}}u_{n,2}\right)^T.
\]

The natural extension of the Stage XII Gram is

\[
 \boxed{
 G_n(\tau)=\frac{2\sqrt{1+\tau}}{n^2}
 \sum_{\substack{2\le\ell<n\\\ell\ {\rm even}}}
 a_{n,\ell}(\tau)a_{n,\ell}(\tau)^T.}
 \tag{2.1}
\]

The \(\ell=0\) response is exactly zero because the sources have zero mass.
Since \(V_n\succeq I\),

\[
 A_{n,\ell}\succeq\omega_{n,\ell}I.
\]

Consequently, for fixed \(n\), every term in (2.1) is exponentially small;
in particular

\[
 \|G_n(\tau)\|_2
 \le C_n\sqrt{1+\tau}\,
 e^{-2\tau\omega_{n,2}}
 \longrightarrow0.
 \tag{2.2}
\]

By contrast, the normalized continuum lattice Gram is

\[
 G^{\rm L}(\tau)
 =\sqrt{1+\tau}\,\Gamma^{\rm L}_{\tau,\delta_0},
\]

and Stage X gives

\[
 G^{\rm L}(\tau)\longrightarrow H_\infty,
 \qquad
 H_\infty(f,g)=\frac1{2\pi}\int_0^\infty
 s^{-1/2}F_f(s)F_g(s)\,ds.
 \tag{2.3}
\]

For the affine, injective modulation and the two nonzero cosine ports,
\(H_\infty\) is positive definite.  Indeed, if a linear combination has
zero quadratic form, its Laplace profile vanishes for all \(s>0\).  Laplace
uniqueness after the change of variable \(v=V(x)\) forces that source
combination to vanish.

Equations (2.2)--(2.3) prove

\[
 \lim_{\tau\to\infty}
 \|G_n(\tau)-G^{\rm L}(\tau)\|_2
 =\|H_\infty\|_2>0
\]

for every fixed \(n\).  More decisively,
\(\lambda_{\min}(G_n(\tau),S)\to0\) for either declared positive source
metric.  No positive all-\(\tau\) finite floor can survive at fixed network
size.

The continuum limit first and the time limit first therefore do not commute:

\[
 \lim_{\tau\to\infty}\lim_{n\to\infty}G_n(\tau)=H_\infty,
 \qquad
 \lim_{n\to\infty}\lim_{\tau\to\infty}G_n(\tau)=0.
 \tag{2.4}
\]

This is the principal correction required in any claim to cover the
"complete late lattice sector."

## 3. Normalization audit

Let \(\mathcal N_{n,f}(t)^2\) be the Stage VIII density-response quadratic
form and put \(t=\tau h^2\).  Euclidean DCT coefficients satisfy

\[
 \beta^{E}_{\ell}=n^{-1/2}\beta^h_\ell,
 \qquad
 a^E_{\ell}=n^{1/2}a^h_\ell.
\]

Their product is invariant, so the Euclidean response sum equals
\(\mathcal N_{n,f}(t)^2\).  The protocol Gram is not that raw sum.  It is

\[
 \boxed{
 G_n(\tau)[f,f]
 =\sqrt{1+\tau}\,h\,\mathcal N_{n,f}(\tau h^2)^2.}
 \tag{3.1}
\]

At \(\tau=1\), (3.1) is exactly the \(\sqrt2/n\) factor behind Stage XII.
Dropping \(h\) changes every Gram by a factor \(n\).  Using \(\sqrt t\)
instead of \(h\sqrt{1+\tau}\) changes it by

\[
 \sqrt{\frac{\tau}{1+\tau}},
\]

which tends to one but is not equal to one on a compact lattice chart.

## 4. What Stage VIII does and does not imply for \(K=2\)

The strongest direct finite-to-lattice estimate in Stage VIII has the scalar
form

\[
 \sqrt\tau\,
 \left|h\mathcal N_{n,f}(\tau h^2)^2
       -\Psi_{Q,f}(\tau)^2\right|
 \le C_f\left[
 h\sqrt\tau+h+\|w_h-Q\|_1+\frac{h\sqrt\tau}{d_h}
 \right].
 \tag{4.1}
\]

After multiplication by
\(\sqrt{(1+\tau)/\tau}\), this has exactly the protocol normalization.
For a central one-cell atom, \(w_h=Q=\delta_0\), \(d_h\) is bounded below,
and the error scale is

\[
 O(h\sqrt\tau+h).
 \tag{4.2}
\]

This is the correct mechanism for a coupled tail.  It also displays why
\(h\sqrt\tau\to0\), rather than merely \(h\to0\), is necessary.

However, Stage VIII is stated for a fixed source and permits its constant to
depend on that source.  Applying (4.1) separately to \(\phi_1\) and
\(\phi_2\) controls only the two diagonal Gram entries.  It does not control
the mixed entry: the symmetric matrix

\[
 \begin{pmatrix}0&1\\1&0\end{pmatrix}
\]

vanishes on both coordinate quadratic forms but has operator norm one.

The needed upgrade is explicit.

### Sufficient finite-band uniformization lemma

Let \(C:\mathbb R^2\to X\) synthesize the two source ports, let \(S\succ0\)
be their declared cost, and suppose the proof of (4.1) is sharpened to

\[
 |q_{n,\tau}(Cc)-q_\tau(Cc)|
 \le C_E(c^TSc)R(n,\tau)
 \tag{4.3}
\]

for every coefficient vector \(c\), with one explicit constant \(C_E\).
Then, writing \(\Delta_{n,\tau}\) for the two Gram matrices' difference,

\[
 \boxed{
 \|S^{-1/2}\Delta_{n,\tau}S^{-1/2}\|_2
 \le C_ER(n,\tau).}
 \tag{4.4}
\]

This follows from the variational identity for a symmetric matrix.  It can
also be obtained by polarization, but only after the constants for
\(\phi_i\pm\phi_j\) are made uniform.  Because the source band is finite,
the analytic estimates in Stage VIII appear uniformizable: the relevant
Sobolev, Lipschitz, and recovery norms are bounded on the \(S\)-unit sphere.
That extension is plausible and finite-dimensional, but it is not the
currently stated Stage VIII theorem and it is not yet an outward-rounded
certificate.

Stage VIII's separate atomic estimate similarly gives, after uniformization,

\[
 \|S^{-1/2}(G_n(\tau)-H_\infty)S^{-1/2}\|_2
 \le C_E'\left(h\sqrt\tau+h+\frac1\tau\right)
 \tag{4.5}
\]

for central bounded-cell preparations.  Equation (4.5) is useful for closing
the large-\(\tau\) continuum tail, but it still imposes joint resolution and
contains an as-yet uncertified constant.

## 5. Continuum floor versus finite transfer

Stage X already proves a continuum Loewner floor for every \(\tau\ge1\):

\[
 G^{\rm L}(\tau)\succeq H_b,
 \qquad 0<b\le4.
\]

If

\[
 L=\lambda_{\min}(H_b,S)>0,
\]

then the finite implication is

\[
 \boxed{
 \sup_{\tau\in I}
 \|S^{-1/2}(G_n(\tau)-G^{\rm L}(\tau))S^{-1/2}\|_2
 <L
 \Longrightarrow
 G_n(\tau)\succeq(L-\varepsilon)S
 \quad(\tau\in I).}
 \tag{5.1}
\]

The strict error comparison is indispensable.  Positivity of the finite Gram,
pointwise convergence, or an unspecified \(O(\cdot)\) remainder is not a
proof-producing transfer.  For the small Stage X two-port floors, a hidden
constant is especially consequential.

There are two legitimate ways to use the tail:

- compare \(G_n(\tau)\) directly to \(G^{\rm L}(\tau)\) with the uniformized
  form of (4.1), then invoke the all-\(\tau\) Stage X floor; or
- compare both to \(H_\infty\), combining the finite atomic error (4.5), the
  continuum \(O(1/\tau)\) tail, and \(H_\infty\succeq H_b\).

Neither route removes the condition \(h\sqrt\tau\ll1\).

## 6. Natural discrete \(H^1\)

Stage XII assigns the continuum coefficient cost

\[
 S=\operatorname{diag}(1+\pi^2,1+4\pi^2)
\]

to the finite ports.  The natural discrete energy is instead

\[
 \boxed{
 S_n=\operatorname{diag}
 \left(1+n^2\omega_{n,1},1+n^2\omega_{n,2}\right).}
 \tag{6.1}
\]

These matrices differ by \(O(n^{-2})\).  More usefully,
\(\sin x<x\) gives

\[
 S_n\prec S.
 \tag{6.2}
\]

Therefore a continuum Loewner inequality
\(G^{\rm L}(\tau)\succeq LS\) also implies
\(G^{\rm L}(\tau)\succeq LS_n\).  The old floor \(L\) is a safe comparison
floor for the smaller discrete cost.

But the transfer error must then be evaluated as

\[
 \boxed{
 \|S_n^{-1/2}(G_n(\tau)-G^{\rm L}(\tau))S_n^{-1/2}\|_2.}
 \tag{6.3}
\]

Alternatively, if one compares
\(S_n^{-1/2}G_nS_n^{-1/2}\) directly with
\(S^{-1/2}G^{\rm L}S^{-1/2}\), the \(O(n^{-2})\) metric-change term must be
included.  Reusing Stage XII's continuum-\(H^1\)-whitened error without either
adjustment would silently prove the wrong generalized problem.

## 7. Target parity and placement

On odd grids the central atom lies exactly at \(x=1/2\) and has

\[
 \beta_{n,\ell}=0\quad(\ell\ {\rm odd}),
 \qquad
 \beta_{n,\ell}^2=2/n\quad(\ell\ne0\ {\rm even}).
\]

This identity is responsible for the particularly sharp Stage XII
quadrature and efficient even-mode certificate.

An even grid has no central cell.  There are two distinct choices.

- A single atom is displaced by \(h/2\) from the physical centre.
- A symmetric half/half deposit is physically centred but has local profile
  \(Q=(1/2,1/2)\), hence
  \(|B_Q(\theta)|^2=\cos^2(\theta/2)\), rather than the atomic value one.

The latter changes the finite-\(\tau\) continuum lattice Gram.  It approaches
the same atomic tail only because active \(\theta=O(\tau^{-1/2})\) makes the
profile discrepancy \(O(1/\tau)\).  Odd atoms, even split deposits, and
off-centre atoms therefore cannot be combined into one compact-time
certificate without a target-transport term and a declared reference chart.

## 8. Interval-certificate failure modes

A finite table of successful \(\tau\)-samples is not an interval proof.  The
following must all be controlled.

1. **Hidden interior extrema.** Analytic matrix entries and eigenvalues need
   not be monotone.  Endpoint or mesh values do not bound the interval between
   them.
2. **Dependency inflation.** Substituting the same interval \(\tau\) many
   times into an ordinary interval expression can make a true margin
   undecidable.  Centred Taylor models or derivative-aware subdivision are
   needed.
3. **Matrix norm geometry.** Entrywise maxima are unsafe and row sums may be
   too coarse, as Stage XII already demonstrates.  Each interval box needs a
   valid spectral-norm enclosure, with subdivision when the \(2\times2\)
   radical wraps excessively.
4. **Polynomial remainder scaling.** Stage XII's degree-32 bound is for
   \(\tau=1\).  On \([1,T]\), a naive uniform replacement is
   \((18T/5)^{33}/33!\).  It already exceeds one at \(T=4\), so the old
   truncation cannot simply be relabelled uniform.  Mode-dependent damping,
   a higher degree, scaling-and-squaring, or interval Chebyshev/Taylor models
   are required.
5. **Continuum and finite synchronization.** Both Grams must use the same
   \(\tau\), normalization, source metric, and target profile.  Independently
   wide intervals for the two can destroy cancellation in their difference.
6. **Strict floor margin.** Every box must prove its error upper endpoint is
   strictly below the exact floor.  Floating-point midpoints do not decide
   the inequality.
7. **Parity scope.** A cover for the odd exactly-centred sequence proves
   nothing about even or displaced targets without the placement theorem.

### Sufficient compact-interval certificate

For a fixed odd \(n\), metric \(S_*\), and compact interval
\(I=[\tau_0,T]\), it is sufficient to produce outward enclosures proving

\[
 \varepsilon_{n,I}:=sup_{\tau\in I}
 \|S_*^{-1/2}(G_n(\tau)-G^{\rm L}(\tau))S_*^{-1/2}\|_2<L_I,
 \tag{8.1}
\]

where \(L_I\) is an independently certified continuum lower floor in the
same metric.  Then the uniform finite floor is \(L_I-\varepsilon_{n,I}\).
For the atom and \(\tau\ge1\), the Stage X \(H_b\) floor can serve as
\(L_I\), so the continuum eigenvalue need not be re-minimized on every box.

## 9. Corrected research target

The strongest valid next target is:

> For the two-port Neumann benchmark and each declared source metric, build
> an outward-rounded interval certificate on \(1\le\tau\le T\).  Then prove
> an explicit finite-band Stage VIII bound, uniform on the metric unit sphere,
> which transfers the Stage X floor for all pairs
> \(\tau\ge T\), \(h\sqrt\tau\le\varepsilon_*\).  State explicitly that no
> fixed \(n\) covers \(\tau=\infty\).

A useful output domain is therefore

\[
 \mathcal D=
 \{(n,\tau):1\le\tau\le T,\ n\ge N_T\}
 \cup
 \{(n,\tau):\tau\ge T,\ h\sqrt\tau\le\varepsilon_*\}.
 \tag{9.1}
\]

The first piece is closed by interval computation plus a uniform
\(n^{-2}\) theorem.  The second is closed by explicit Stage VIII constants.
This domain is unbounded in \(\tau\) across growing networks, respects the
noncommuting limits, and is strong enough for a resolution-aware protocol
engine.

## 10. Executable controls

Run

```bash
python -m unittest -v test_oig_uniform_lattice_adversarial_controls.py
```

The controls check:

- fixed-\(n\) late-time collapse against a nonzero atomic constant;
- the exact \(\sqrt{1+\tau}\,h\mathcal N^2\) normalization;
- finite-\(\tau\) separation of an atom and a symmetric split target;
- the natural discrete-\(H^1\) metric change and its Loewner ordering;
- the failure of basis-diagonal checks to control a \(K=2\) Gram;
- hidden extrema between point samples;
- failure of the \(\tau=1\), degree-32 tail on a wider interval; and
- the strict floor-versus-error logic required for transfer.

The numerical controls illustrate obstructions.  The fixed-grid obstruction,
normalization identity, metric ordering, and sufficient transfer conditions
are analytic statements independent of binary64 evidence.
