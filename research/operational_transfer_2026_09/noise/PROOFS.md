# A verified augmented solve with bounded residual drift

## 1. Exact experiment and inherited premise

There are 8,900 complex readings at

\[
t_j=(2j+1-8900)/10,\qquad x_j=t_j/890,\qquad 0\le j<8900.
\]

The source satisfies $a(1)=1$ and $a(n)\in\mathbb Z$, $0\le a(n)\le d_{14}(n)$.
The query is $(a(2),\ldots,a(50))$. The class is an integer coefficient envelope;
realization of every such sequence by a number field is not assumed.

The observation model is

\[
y_j=\sum_{n\ge1}a(n)n^{-2-it_j}+b(x_j)+h_j+e_j,\qquad
b\in\mathcal P_p(\mathbb C),\quad
\|h\|_W\le\nu,\quad\|e\|_W\le\eta.                         \tag{1}
\]

The coefficients of $b$ are unrestricted. The remainder $h$ is bounded; it is
not silently treated as an additional unrestricted nuisance. The same physical
readings are used for either of two positive diagonal matrices $W$, with
$\sum_jw_j=1$: the previous outer cosine window, or its mixture with the
centered 2,550-reading window at mixture coefficient $125/65536$. Their exact
binary64 coefficient literals define rational constants in the model. Their
values, times, embedding and metric have not been optimized or changed here.

Let $\Phi_{jn}=\exp(-it_j\log n)$, $1\le n\le50$. Let $\psi_1,\ldots,\psi_p$
be the positive-leading, $W$-orthonormal polynomials orthogonal to the constant.
Set $X=[\Phi,\Psi]$, $H=X^*WX$. The first source column is the constant, so its
fitted coefficient combines $a(1)$ and the constant nuisance. It is discarded;
the known value $a(1)=1$ is supplied to the final answer, not estimated.

The previous [complete-tail proof](../../transfer_theorem_2026_09/noise/PROOFS.md)
and [rational consumer](../../transfer_theorem_2026_09/noise/check_certificate.py)
establish the following premise for degrees 6, 8, 10 and 12. The demonstration
in this phase uses degree 8.

* $H\succeq fI$ for the positive rational
  $f=1-\texttt{augmented\_gram\_defect}$ in the bound record.
* After the exact midpoint tail correction, the full infinite arithmetic tail
  contributes at most $A_n$ to decoded coefficient $n$. The rational $A_n$ is
  `complete_coefficient_bias_upper[n-1]` in that record.
* The fixed digital correction $\widetilde u$ satisfies
  $\|u-\widetilde u\|_W\le\Xi=10^{-20}$.

The correction is

\[
u_j=\tfrac12\left[\zeta(2+it_j)^{14}
                 -\sum_{n\le50}d_{14}(n)n^{-2-it_j}\right].
\]

These are complete tail bounds, not a truncation at the largest coefficient
used in the synthetic examples. The inherited proof includes the arithmetic
tail channels, the polynomial cross channels, and every coefficient beyond
$10^{12}$. This phase checks the predecessor's rational consequences and file
bindings. Its unchanged expensive arithmetic-tail and correction reconstructions
remain documented in the predecessor's reproduction guide.

## 2. Operational transfer theorem

Take any proposed augmented coefficient vector $\widehat\theta\in\mathbb C^{50+p}$.
Suppose the actual normal residual has been enclosed:

\[
r=H\widehat\theta-X^*W(y-\widetilde u),\qquad \|r\|_2\le\rho.              \tag{2}
\]

Then, under (1), for every $2\le n\le50$,

\[
\left|n^2\widehat\theta_n-a(n)\right|
\le E_n:=A_n+n^2\left\{\frac{\eta+\nu+\Xi}{\sqrt f}
                              +\frac\rho f\right\}.                     \tag{3}
\]

In particular, $E_n<1/2$ for all 49 coordinates certifies integer recovery by
nearest-real-integer rounding. An implementation may also check that the
resulting integer lies in $[0,d_{14}(n)]$ and in the complex error disk (3).
Failure of these sufficient checks produces no certified answer.

**Proof.** Let $\theta_*=H^{-1}X^*W(y-\widetilde u)$ be the exact augmented
least-squares solution. Equation (2) gives
$\widehat\theta-\theta_*=H^{-1}r$, hence
$\|\widehat\theta-\theta_*\|_2\le\rho/f$.

Let $K=H^{-1}X^*W^{1/2}$. Direct multiplication gives $KK^*=H^{-1}$, so
$\|K\|_2\le1/\sqrt f$. The combined data perturbation
$e+h+(u-\widetilde u)$ has $W$ norm at most $\eta+\nu+\Xi$ by the triangle
inequality. Its fitted coefficient vector therefore changes by at most
$(\eta+\nu+\Xi)/\sqrt f$. Add the inherited complete tail bound $A_n$ and
multiply the two vector-error contributions by the coefficient scaling $n^2$.
This proves (3). The polynomial lies exactly in the augmented column space;
its size never enters this argument. An integer at complex distance less than
$1/2$ is uniquely determined by rounding the real part. ∎

This is the earlier transfer theorem's normal-residual and query-separation
corollary. In particular, the solve residual costs $\rho/f$, whereas a physical
data error costs its norm divided by $\sqrt f$. These factors are not
interchangeable. No independence of the separate errors, windows or readings
is required or claimed.

## 3. Exact gates and a sufficient remainder allowance

Define $m_n=1/2-A_n-n^2\rho/f$. The implemented gate avoids approximate square
roots:

\[
m_n>0,\qquad n^4(\eta+\nu+\Xi)^2<m_n^2f.                                 \tag{4}
\]

Let $s$ be a positive rational lower bound on $\sqrt f$. When all $m_n>0$,
the computable quantity

\[
L(\rho,\eta)=\min_{2\le n\le50}\frac{m_ns}{n^2}-\eta-\Xi                 \tag{5}
\]

is a **sufficient budget limit**: $0\le\nu<L$ implies every gate (4).
`strict_sufficient_nonpolynomial_budget_limit` records this conservative value.
The square-root bound uses an integer square root on a $10^{-60}$ rational
grid. It is not an estimate of the true physical remainder or an optimal
robust threshold. If a margin is nonpositive, no positive allowance is asserted.

For sensor radius $\eta=0.00004$, the large-drift degree-eight examples give
limits exceeding $0.00006009$ for the multiscale window and $0.00004050$ for
the outer window. Both accept the declared $\nu=0.00003$ jointly with that
sensor radius. These allowances depend on the verified residual of the actual
proposal; they are not obtained by assigning both errors the old full sensor
allowance separately.

## 4. What the residual verifier actually evaluates

[physical.py](physical.py) reconstructs all 8,900 positive weights, all complex
phase columns, and the polynomial basis with outward Arb arithmetic. Moments
of odd degree are exactly zero by symmetry. The constant moment is exactly one
by the finite trigonometric sum defining each window. The remaining moments
are summed over every reading. Gram–Schmidt with positive leading coefficients
defines the same unique orthonormal polynomials used by the tail proof; their
computed coefficient intervals must lie inside the saved tail enclosures.

The verifier forms $X^*W$ with complex conjugation and reconstructs the full
augmented $H$. Its computed absolute row-sum defect must establish at least
the inherited floor $f$. It never substitutes a saved floating Gram matrix.

The inputs are exact rational real/imaginary pairs. Ordinary floating solves
are proposals only. Every proposed coefficient is frozen as an exact rational.
The verifier evaluates both

\[
H\widehat\theta-X^*Wz
\quad\text{and}\quad
X^*W(X\widehat\theta-z),\qquad z=y-\widetilde u.                          \tag{6}
\]

The demonstration checks componentwise overlap of their outward enclosures and
uses the larger resulting norm bound. To bound a residual norm, each complex
modulus is first bounded above by a rational; the sum of their squares and a
rational square-root upper bound then produce $\rho$. This remains valid for
an interval centered at zero, where directly taking the square root of an
interval square may produce an indeterminate result.

If a binary64 proposal fails, [certify.py](certify.py) proposes an Arb augmented
solve and separately re-evaluates (2). Its JSON result binds both the readings
and proposal by content hashes. The solver receives neither the target integer
answer nor the synthetic source coefficients. A saved result is a receipt;
[replay.py](replay.py) reconstructs the model and reevaluates the residual to
validate it.

Inadequate working precision can cause refusal. A positive residual certificate
does not certify that a user-supplied $\eta$ or $\nu$ describes the apparatus.
The CLI accepts exact rational inputs; digitization uncertainty must be included
in the physical data budget. Known exact times and the declared model remain
assumptions.

## 5. A large nonpolynomial drift can have a small charged remainder

Only the part of a drift outside its polynomial approximation needs the bounded
remainder budget. For example, on $|x|\le1$, Taylor's theorem gives

\[
\left|10\sin x-10\left(x-\frac{x^3}{6}+\frac{x^5}{120}
                                      -\frac{x^7}{5040}\right)\right|
\le\frac{10}{9!}=\frac1{36288}<0.00003.                                  \tag{7}
\]

The ninth derivative of sine has modulus at most one; this proves the complete
remainder bound. Since the weights sum to one, the same number bounds its
$W$ norm. The displayed polynomial is absorbed into the unrestricted
degree-eight nuisance. Thus the guarantee applies to the full drift
$10\sin(t/890)$ although its amplitude is many orders larger than $\nu$.

More generally, for a real drift with ninth derivative bounded by $D$ on
$[-1,1]$, the degree-eight Taylor remainder has $W$ norm at most $D/9!$.
For $B\sin(\omega x)$ one may use $D=|B||\omega|^9$. This bound is sufficient;
it does not establish the best weighted polynomial approximation.

## 6. Demonstrated consequences and a necessary limitation

Two full complex datasets use $a(n)=n\bmod7$ for $2\le n\le50$, known $a(1)=1$,
and nonzero omitted coefficients at 51, 60 and 72 equal to
$\lfloor d_{14}(n)/2\rfloor$. All other coefficients vanish. They therefore
lie in the declared envelope and exercise the omitted-tail channels.

Both contain degree-eight polynomial nuisance
$\beta_k=A/(k+1)+iA/(k+2)$ in powers of $x$. The moderate case uses $A=10^6$
and drift $0.00003\sin(t/7)$. The large case uses $A=10^{20}$ and (7).
Both add deterministic sensor perturbation $0.000039e^{it/11}$ and are rounded
to an exact rational grid of size $10^{-40}$ in each component. Outward
reconstruction proves the complete digitization error below $10^{-35}$, so
the declared sensor radius $0.00004$ includes it.

All 49 unknown integers are certified and correct for both windows on both
datasets. In the large case, the binary64 proposals have normal residuals above
$10^5$ and fail; the refined proposals have verified residuals below
$3.21\cdot10^{-39}$ at 256 bits. At 320 bits, all four exact saved proposals,
all data digits, both identities (6), and all answer gates replay successfully.
The large example tests computational cancellation using inputs that retain
the small signal; it is not a hardware dynamic-range or empirical noise result.

Finally, a small normal residual cannot validate a physical drift promise.
Increasing $a(50)$ by one produces exactly the same data as leaving it fixed
and adding $h_j=\Phi_{j,50}/2500$. Both integer values 1 and 2 are permitted;
$\|h\|_W=1/2500$ because $|\Phi_{j,50}|=1$. If such a remainder is allowed,
the two sources are observationally identical. The exact least-squares normal
residual can still vanish. This is why (1)'s remainder bound must come from a
valid model or calibration, not from the stopping residual of a solver.
