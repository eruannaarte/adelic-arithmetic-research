# Operational Information Geometry VI

## Fixed-mode response convergence: exact midpoint structure and certified components

- **Research, proof development, computation, and implementation:** Codex (OpenAI)
- **Originating direction and research environment:** TGN's human founder
- **Date:** 14 August 2026
- **Status:** theorem-and-computation layer; not peer reviewed

## Abstract

Stage V observed second-order convergence of a density-normalized directed
response under cell-centred path refinement, but correctly left the full
operator-rate statement as a hypothesis. This report independently audits that
observation and resolves part of the gap.

For an exact declared protocol—source modes \(1,\ldots,5\), target mode one,
\(a=2/5\), \(g=4/5\), and nine rational positive times—we obtain four results.

1. The \(n^2\)-state response and its \(n\)-state target-mode reduction agree to
   \(2.45\times10^{-16}\) absolute error in direct dense controls.
2. A 70-decimal-digit calculation finds full-history and Gram convergence
   orders \(2.00004\) and \(2.00055\). Reference-free Cauchy quotients converge
   to two as well, so the observation is not an artifact of choosing a fine
   reference grid.
3. An exact midpoint-cosine identity proves a genuine expansion

   \[
   K_{n,P}=K_P+\frac{E_P}{n^2}+O_P(n^{-4})
   \]

   for every fixed modal cutoff \(P\). It yields second-order fixed-block
   response convergence and an explicit first correction. At \(P=5\), 192-bit
   Arb arithmetic certifies the declared finite instances with
   \(\|n^2(K_{n,P}-K_P)\|_F<6000\) and fourth-order remainder below \(50000\).
4. A block-Duhamel estimate supplies an explicit high-mode Galerkin tail. It
   proves convergence of the full fixed-mode response by an epsilon argument:
   first choose the modal cutoff, then refine the lattice. These particular
   block-and-tail bounds do **not** combine sharply enough to prove the
   empirically observed uniform \(O(n^{-2})\) rate for the full response. The
   companion analytic proof memo closes that rate by a different
   lumped-mass finite-element argument.

Thus this audit proves the convergence and exposes the exact second-order
mechanism. Together with the companion analytic memo, the declared smooth
fixed-mode positive-time response and Gram now have a proved full
second-order rate.

## 1. Exact declared experiment

Let

\[
x_j=\frac{j+1/2}{n},\qquad A_n=n^2L_n,\qquad
\mu_{k,n}=4n^2\sin^2\!\left(\frac{k\pi}{2n}\right).
\]

The source modes are

\[
\phi_k(x)=\sqrt2\cos(k\pi x),\qquad k=1,\ldots,5,
\]

the target density is

\[
\rho_B(y)=1+\frac25\sqrt2\cos(\pi y),
\]

and the source-dependent target rate is \(1+\frac45x\). The observation times
are the exact rationals

\[
\frac1{1000},\frac1{500},\frac1{200},\frac1{100},\frac1{50},
\frac1{20},\frac1{10},\frac15,\frac12.
\]

Let \(u_{k,n}(j)=\phi_k(x_j)/\sqrt n\). A unit continuum-\(L^2\) source
perturbation is injected as the probability vector \(u_{k,n}/\sqrt n\). The
target marginal is multiplied by \(\sqrt n\) before projection onto
\(u_{1,n}\). The two factors cancel exactly, leaving the response

\[
r_{n,k}(t)=a\,e_0^{\mathsf T}e^{-tK_n}e_k,\qquad a=\frac25,
\]

in discrete cosine coordinates. Here

\[
K_n=\operatorname{diag}(\mu_{p,n})+\mu_{1,n}(I+gX_n),\qquad
(X_n)_{pq}=\frac1n\sum_{j=0}^{n-1}x_j\phi_p(x_j)\phi_q(x_j).
\]

At \(n=32\), the DCT and source-density Gram errors are both
\(2.22\times10^{-16}\); the target mass error is zero, its minimum probability
is \(0.01359\), and its density-normalized first-mode coefficient is \(0.4\).

## 2. Dense versus modal identity

Conjugating the target coordinate by its cosine basis block-diagonalizes the
joint generator. For target mode \(\ell=1\), the relevant block is exactly
\(K_n\). The checker also constructs the complete \(n^2\times n^2\) generator,
the probability-normalized injection, and the density-normalized target port.

| \(n\) | maximum entry error | relative history error |
|---:|---:|---:|
| 6 | \(2.45\times10^{-16}\) | \(2.34\times10^{-14}\) |
| 7 | \(9.28\times10^{-17}\) | \(9.87\times10^{-15}\) |

This is an implementation and normalization audit. The modal reduction itself
is algebraic.

## 3. Exact midpoint multiplication theorem

Define

\[
I_r=\int_0^1x\cos(r\pi x)\,dx,\qquad
I_{r,n}=\frac1n\sum_{j=0}^{n-1}x_j\cos(r\pi x_j).
\]

### Theorem 3.1

For \(0\le r<2n\),

\[
I_0=I_{0,n}=\frac12,\qquad
I_r=\frac{(-1)^r-1}{(r\pi)^2}\quad(r>0),
\]

and

\[
I_{r,n}=\begin{cases}
0,&r>0\text{ even},\\[3pt]
\displaystyle-\frac{\cos(r\pi/(2n))}
 {2n^2\sin^2(r\pi/(2n))},&r\text{ odd}.
\end{cases}
\]

#### Proof

The continuum formula follows by integration. For the discrete formula,
differentiate the finite identity

\[
\sum_{j=0}^{n-1}\sin((j+1/2)\theta)
=\frac{\sin^2(n\theta/2)}{\sin(\theta/2)}
\]

and set \(\theta=r\pi/n\). The derivative is
\(\sum_j(j+1/2)\cos((j+1/2)\theta)\), which gives the displayed cases after
division by \(n^2\). \(\square\)

With \(c_0=1\), \(c_p=\sqrt2\) for \(p>0\), product-to-sum gives

\[
(X_n)_{pq}=\frac{c_pc_q}{2}
\bigl(I_{|p-q|,n}+I_{p+q,n}\bigr).
\]

Two consequences are unusually clean:

- if \(p,q\) have the same parity, \((X_n)_{pq}=X_{pq}\) exactly;
- if they have opposite parity, the Laurent expansion

  \[
  \frac{\cos x}{\sin^2x}
  =\frac1{x^2}-\frac16-\frac{7x^2}{120}+O(x^4)
  \]

  yields

  \[
  (X_n)_{pq}=X_{pq}+\frac{c_pc_q}{12n^2}+O_{p,q}(n^{-4}).
  \]

Thus the parity seen in the first causal jet is also the carrier of the leading
quadrature correction.

## 4. Fixed-block second-order theorem

Let \(\nu_p=(p\pi)^2\), \(\lambda=(\ell\pi)^2\), and let \(K_P\) be the
continuum cosine-Galerkin matrix on modes \(0,\ldots,P\):

\[
(K_P)_{pq}=\delta_{pq}(\nu_p+\lambda)+\lambda gX_{pq}.
\]

The exact eigenvalue expansion is

\[
\mu_{p,n}=\nu_p-\frac{\nu_p^2}{12n^2}+O_p(n^{-4}).
\]

Define

\[
Y_{pq}=\begin{cases}c_pc_q/12,&p+q\text{ odd},\\0,&p+q\text{ even}.
\end{cases}
\]

Combining the two exact expansions gives the following.

### Theorem 4.1 — fixed-modal generator and response expansion

For each fixed \(P\),

\[
K_{n,P}=K_P+\frac{E_P}{n^2}+O_P(n^{-4}),
\]

where

\[
(E_P)_{pq}=
-\delta_{pq}\frac{\nu_p^2}{12}
-\frac{\lambda^2}{12}(\delta_{pq}+gX_{pq})
+\lambda gY_{pq}.
\]

For each fixed \(t\), analyticity of the matrix exponential then gives

\[
R_{n,P}(t)=R_P(t)+\frac1{n^2}
a\,e_0^{\mathsf T}
L_{\exp}(-tK_P,-tE_P)e_{\{1,\ldots,5\}}
+O_P(n^{-4}),
\]

where \(L_{\exp}\) denotes the Fréchet derivative of the exponential.

This is a theorem for every fixed modal block, not merely a fitted rate. At
\(P=5\), the Frobenius norm of the leading nine-time response correction is
\(0.01969573254\). The computations give

| \(n\) | \(n^2\|R_{n,5}-R_5\|_F\) | \(n^4\) scaled remainder |
|---:|---:|---:|
| 8 | 0.01973435 | 0.10157 |
| 16 | 0.01969902 | 0.08258 |
| 32 | 0.01969640 | 0.07881 |
| 64 | 0.01969589 | 0.07791 |
| 128 | 0.01969577 | 0.07769 |

The fourth-order stabilization is a consequence check, not an ingredient in
the analytic expansion.

### Outward-rounded finite audit

An independent 192-bit Arb calculation encloses every entry of \(K_{n,5}\),
\(K_5\), and \(E_5\). For

\[
n\in\{8,12,16,24,32,48,64,96,128\},
\]

it certifies

\[
\|n^2(K_{n,5}-K_5)\|_F<6000,\qquad
\|n^4(K_{n,5}-K_5-n^{-2}E_5)\|_F<50000.
\]

The largest displayed enclosures at \(n=128\) are respectively
\(5537.1044052\) and \(43174.6426657\), with ball radii below
\(7\times10^{-46}\). The rational bounds 6000 and 50000 are deliberately
simple rather than optimized.

## 5. Exact first-jet rate

The midpoint identity also sharpens Stage V's parity theorem.

### Theorem 5.1

For an odd source mode \(k\),

\[
\dot r_{n,k}(0)=2\sqrt2\,ag\frac{\mu_{\ell,n}}{\mu_{k,n}}
\cos\!\left(\frac{k\pi}{2n}\right),
\]

while every even source mode is exactly zero. Relative to the continuum value
\(2\sqrt2\,ag\ell^2/k^2\), put
\(x=k\pi/(2n)\), \(y=\ell\pi/(2n)\). Then

\[
\left|\frac{\dot r_{n,k}(0)}{\dot r_k(0)}-1\right|\le
\max\left\{
(1-x^2/6)^{-2}-1,
1-(1-y^2/3)(1-x^2/2)
\right\}.
\]

#### Proof

Insert Theorem 3.1 into
\(-ag\mu_{\ell,n}(X_n)_{0k}\). For the bound, use
\(\sin z\ge z-z^3/6\), \(\sin z\le z\), and
\(\cos z\ge1-z^2/2\) in the exact ratio

\[
\left(\frac{\sin y}{y}\right)^2
\left(\frac{x}{\sin x}\right)^2\cos x.
\]

\(\square\)

For modes \(1,\ldots,5\), the maximum actual odd-mode relative error falls from
\(0.2354\) at \(n=8\) to \(1.695\times10^{-4}\) at \(n=256\); every even entry
is exactly zero in the closed formula. The proved bounds cover every row.

## 6. A rigorous continuum Galerkin tail

Let

\[
H=-\partial_x^2+\lambda(1+gx)
\]

with Neumann boundary conditions, and let \(P\) project onto cosine modes
\(0,\ldots,P\). Multiplication by \(x-1/2\) has norm at most \(1/2\), so the
off-block coupling obeys

\[
b=\|PH(I-P)\|\le\frac{\lambda g}{2}.
\]

On the high block,

\[
(I-P)H(I-P)\succeq(\nu+\lambda)I,\qquad
\nu=\pi^2(P+1)^2.
\]

Solving the two coupled block evolution equations and applying Duhamel twice
gives

\[
\|Pe^{-tH}P-e^{-tPHP}\|\le
\frac{b^2e^{-\lambda t}}{\nu}
\left[t-\frac{1-e^{-\nu t}}{\nu}\right].
\]

For five response columns, multiply by \(a\sqrt5\). Summing the nine row
bounds in quadrature gives:

| \(P\) | observed difference to \(P=512\) | rigorous history-tail bound |
|---:|---:|---:|
| 16 | \(6.03\times10^{-10}\) | \(2.87\times10^{-4}\) |
| 32 | \(1.87\times10^{-11}\) | \(7.64\times10^{-5}\) |
| 64 | \(5.84\times10^{-13}\) | \(1.97\times10^{-5}\) |
| 128 | \(2.11\times10^{-14}\) | \(5.01\times10^{-6}\) |
| 256 | \(1.14\times10^{-14}\) | \(1.26\times10^{-6}\) |

The observed differences eventually reach binary64 roundoff. Only the third
column is the proof bound.

The finite \(n\) system has the same estimate with
\(\lambda\) and \(\nu\) replaced by \(\mu_{\ell,n}\) and
\(\mu_{P+1,n}\). Since \(\mu_{P+1,n}\) grows quadratically in \(P\) uniformly
away from the Nyquist edge, the following epsilon argument is valid:

1. choose \(P\) so the discrete and continuum high-mode tails are small;
2. use Theorem 4.1 to send \(n\to\infty\) on that fixed block.

This proves full fixed-mode response convergence at the declared positive
times. The displayed tail is too conservative to preserve a sharp
\(n^{-2}\) rate when \(P\) is allowed to grow with \(n\).

## 7. High-precision full-response audit

The complete finite modal matrices were diagonalized with 70-decimal-digit
mpmath arithmetic at \(n=8,16,32,64\), using a 65-mode high-precision
continuum Galerkin calculation. The largest difference between binary64 and
high-precision response entries was \(8.35\times10^{-17}\). The successive
orders were

\[
2.0025791,\qquad2.0001913,\qquad2.0000370.
\]

A wider binary64 sweep against a stabilized \(P=256\) Galerkin reference gives:

| \(n\) | relative history error | \(n^2\) error | relative Gram error | \(n^2\) error |
|---:|---:|---:|---:|---:|
| 8 | \(1.09216\times10^{-2}\) | 0.698982 | \(1.18671\times10^{-2}\) | 0.759496 |
| 16 | \(2.72552\times10^{-3}\) | 0.697733 | \(2.94648\times10^{-3}\) | 0.754300 |
| 32 | \(6.81290\times10^{-4}\) | 0.697641 | \(7.35544\times10^{-4}\) | 0.753197 |
| 64 | \(1.70318\times10^{-4}\) | 0.697623 | \(1.83819\times10^{-4}\) | 0.752924 |
| 128 | \(4.25793\times10^{-5}\) | 0.697618 | \(4.59507\times10^{-5}\) | 0.752856 |
| 256 | \(1.06448\times10^{-5}\) | 0.697617 | \(1.14874\times10^{-5}\) | 0.752839 |

The log-log fitted orders over \(n\ge16\) are \(2.0000448\) for the history and
\(2.0005502\) for its Gram. Reference-free triples
\((n,2n,4n)\) give Cauchy orders from \(2.00465\) down to \(2.000011\).
Richardson extrapolation from \(n=128,256\) reduces the relative history error
to \(2.57\times10^{-9}\), consistent with the fixed-block fourth-order
remainder.

Within this computational lane, these last rates remain empirical because the
finite Galerkin reference is not an interval enclosure of the exact continuum
response. The high-precision and Cauchy controls make floating roundoff and
reference choice implausible explanations. The separate finite-element theorem
in the companion proof memo establishes the full rate analytically.

## 8. Status ledger

### Proved analytically

- the normalization identity;
- the target-mode reduction;
- the exact midpoint-cosine formula and its parity consequences;
- \(K_{n,P}=K_P+n^{-2}E_P+O_P(n^{-4})\) for every fixed \(P\);
- the corresponding fixed-block response expansion;
- the exact finite first-jet formula and explicit \(O(n^{-2})\) bound;
- the continuum and finite discrete Galerkin-tail estimates; and
- convergence of the full fixed-mode response through the cutoff/refinement
  epsilon argument.

### Outward certified on declared finite data

- the \(P=5\) generator expansion at nine side lengths using 192-bit Arb;
- rational upper bounds 6000 and 50000 for the scaled first and second
  remainders.

### Computed independently

- dense-versus-modal agreement;
- 70-digit full-response convergence;
- binary64 sweeps through \(n=256\);
- reference-free Cauchy orders and Richardson cancellation.

### Not proved by the block-and-tail audit alone

- a single uniform semigroup/consistency estimate proving the full response
  error is \(O(n^{-2})\) for \(t\ge t_0>0\), rather than merely proving
  convergence and fixed-block second order. The companion proof memo supplies
  this through an exact-load Strang--Aubin--Nitsche--Dunford route.

## 9. Reproduction

Install the dependencies in oig_vi_fixed_mode_requirements.txt, then run:

    python oig_vi_fixed_mode_convergence.py
    python oig_vi_fixed_mode_convergence.py --fast
    python -m unittest -v test_oig_vi_fixed_mode_convergence.py

The full report takes about five seconds on the reference machine. The tested
environment was Python 3.12.9, NumPy 2.4.6, SciPy 1.15.2, mpmath 1.3.0,
python-flint 0.9.0, and arm64 macOS. The high-precision results do not require
the Windows machine.

## 10. Limitations

- The theorem concerns one smooth target profile, one bounded linear
  modulation, five fixed source modes, and a finite set of positive times.
- The full convergence proof is an iterated cutoff/refinement argument. Its
  explicit tail bound is intentionally general and much larger than the
  observed Galerkin error.
- The sharp full \(O(n^{-2})\) rate is not derived from this report's
  block-tail bounds or interval certified; it is proved separately by the
  analytic finite-element argument.
- Arb certification is conditional on the correctness of Arb/FLINT and the
  checker; it is not a formal-proof-assistant derivation.
- Dense checks are necessarily small because their state dimension is \(n^2\).
- Nothing here changes the finite linear, declared-partition, or nonphysical
  scope of Operational Information Geometry.
