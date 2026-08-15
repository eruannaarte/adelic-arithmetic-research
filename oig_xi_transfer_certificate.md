# OIG Stage XI finite-grid transfer certificate

- **Status:** rigorous at the declared points and dimensions; not peer reviewed
- **Canonical modulation:** \(V(x)=1+\frac45x\)
- **Chart point:** one-cell lattice, \(\tau=1\), normalized by
  \(\sqrt{1+\tau}=\sqrt2\)
- **Bands:** rigorous phase-grid transfer through \(K=8\); rigorous complete
  finite Neumann transfer for \(K=1\)

## 1. Result

Stage X left a precise bridge condition.  If \(G\) is a certified continuum
Gram, \(G_h\) is expressed in the same source coordinates and source metric
\(S\), and

\[
 \delta_K(h)=
 \left\|S^{-1/2}(G_h-G)S^{-1/2}\right\|_2<L_K,
\]

then

\[
 \lambda_{\min}(G_h,S)\ge L_K-\delta_K(h)>0.
\]

This certificate closes that inequality at two deliberately distinct levels.

1. For the cell-centred spectral quadrature of the limiting lattice phase
   Gram, it closes \(\delta_K(n)<L_K\) for every \(1\le K\le8\), in both the
   declared \(L^2\) and continuum \(H^1\) source metrics.
2. For the actual cell-centred finite Neumann dynamics, including the
   noncommuting path Laplacian and ramp multiplication, it closes the complete
   transfer inequality for \(K=1\) at \(n=7\), in both metrics.

The first point is a rigorous quadrature theorem, not a surrogate claim about
the full finite dynamics.  The second is the first complete finite-model
crossing.  Keeping those statements separate is the central audit boundary.

## 2. Continuum and phase-grid Grams

For the cosine port \(\phi_k=\sqrt2\cos(k\pi x)\), define

\[
 F_k(s)=
 \int_0^1 e^{-s(1+4x/5)}\phi_k(x)\,dx.
\]

At the normalized one-cell lattice point \(\tau=1\), the continuum Gram is

\[
 G_{ij}=\sqrt2\int_0^1
 F_i\!\left(4\sin^2\frac{\pi\xi}{2}\right)
 F_j\!\left(4\sin^2\frac{\pi\xi}{2}\right)d\xi.
 \tag{2.1}
\]

The phase grid uses the cell centres
\(\xi_r=(r+\frac12)/n\) and

\[
 \widetilde G_{n,ij}=\frac{\sqrt2}{n}
 \sum_{r=0}^{n-1}
 F_i\!\left(4\sin^2\frac{\pi\xi_r}{2}\right)
 F_j\!\left(4\sin^2\frac{\pi\xi_r}{2}\right).
 \tag{2.2}
\]

Arb encloses every term of (2.2) and every integral in (2.1).  For
\(S=I\) in \(L^2\), or

\[
 S_{kk}=1+(k\pi)^2
\]

in the declared continuum \(H^1\) metric, the checker forms the whitened
interval error \(E=S^{-1/2}(\widetilde G_n-G)S^{-1/2}\) entry by entry.  It
then proves

\[
 \|E\|_2\le\|E\|_\infty
 =\max_i\sum_j|E_{ij}|.
 \tag{2.3}
\]

No numerical eigensolver, sampled sign, or binary64 comparison decides the
certificate.

## 3. Certified phase-grid crossings

The table gives the first \(n\) in the sequential search \(n=K+1,K+2,\ldots\)
for which the rigorous upper bound falls below the exact Stage X lower floor.
Every immediately preceding grid fails the same strict Arb test.

All scientific-notation entries below are nearest decimal summaries.  The
words “upper” and “floor” describe the corresponding exact directed rational
fields in the generated JSON; the displayed rounded decimals themselves are
not substituted into any proof comparison.

| \(K\) | metric | Stage X \(L_K\), decimal approx. | first \(n\) | exact \(\delta_K(n)\) upper, decimal approx. | exact transferred floor, decimal approx. |
|---:|:---:|---:|---:|---:|---:|
| 1 | \(L^2\) | \(1.31065\times10^{-4}\) | 5 | \(2.76537\times10^{-5}\) | \(1.03411\times10^{-4}\) |
| 1 | \(H^1\) | \(1.20579\times10^{-5}\) | 5 | \(2.54413\times10^{-6}\) | \(9.51378\times10^{-6}\) |
| 2 | \(L^2\) | \(1.43152\times10^{-7}\) | 8 | \(1.34060\times10^{-8}\) | \(1.29746\times10^{-7}\) |
| 2 | \(H^1\) | \(3.55231\times10^{-9}\) | 8 | \(1.10477\times10^{-9}\) | \(2.44754\times10^{-9}\) |
| 3 | \(L^2\) | \(1.77650\times10^{-10}\) | 10 | \(1.96122\times10^{-11}\) | \(1.58037\times10^{-10}\) |
| 3 | \(H^1\) | \(2.01796\times10^{-12}\) | 10 | \(1.44594\times10^{-12}\) | \(5.72021\times10^{-13}\) |
| 4 | \(L^2\) | \(2.23908\times10^{-13}\) | 12 | \(1.20802\times10^{-14}\) | \(2.11828\times10^{-13}\) |
| 4 | \(H^1\) | \(1.48943\times10^{-15}\) | 12 | \(8.13182\times10^{-16}\) | \(6.76250\times10^{-16}\) |
| 5 | \(L^2\) | \(2.72483\times10^{-16}\) | 13 | \(2.36482\times10^{-16}\) | \(3.60014\times10^{-17}\) |
| 5 | \(H^1\) | \(1.21070\times10^{-18}\) | 14 | \(2.33862\times10^{-19}\) | \(9.76834\times10^{-19}\) |
| 6 | \(L^2\) | \(2.41218\times10^{-19}\) | 15 | \(5.45528\times10^{-20}\) | \(1.86665\times10^{-19}\) |
| 6 | \(H^1\) | \(7.73921\times10^{-22}\) | 16 | \(3.82898\times10^{-23}\) | \(7.35631\times10^{-22}\) |
| 7 | \(L^2\) | \(1.53496\times10^{-22}\) | 17 | \(7.42541\times10^{-24}\) | \(1.46071\times10^{-22}\) |
| 7 | \(H^1\) | \(3.74302\times10^{-25}\) | 18 | \(3.85162\times10^{-27}\) | \(3.70450\times10^{-25}\) |
| 8 | \(L^2\) | \(7.36997\times10^{-26}\) | 18 | \(7.35882\times10^{-26}\) | \(1.11562\times10^{-28}\) |
| 8 | \(H^1\) | \(1.41495\times10^{-28}\) | 19 | \(3.28780\times10^{-29}\) | \(1.08617\times10^{-28}\) |

The \(K=8\), \(L^2\) margin is intentionally reported without rhetorical
inflation: it is only about \(1.12\times10^{-28}\).  The full run was repeated
at 256 and 320 bits and gave the same crossing, while \(n=17\) was rigorously
rejected.

The surprisingly small grids arise because (2.2) is a midpoint quadrature of
an analytic phase integrand.  They say nothing by themselves about the slower
mixed-word convergence of the actual finite generator.

## 4. Complete finite Neumann certificate for one port

Let \(L_n\) be the unscaled cell-centred Neumann path Laplacian,

\[
 \omega_{n,\ell}=4\sin^2\frac{\pi\ell}{2n},
 \qquad
 V_{n,j}=1+\frac45\frac{j+1/2}{n}.
\]

With \(u_{n,k}\) the exact DCT cosine port, central atomic target cell \(j_*\),
and \(\beta_{n,\ell}=u_{n,\ell}(j_*)\), define

\[
 a_{n,\ell k}
 =\mathbf1^T
 \exp[-(L_n+\omega_{n,\ell}V_n)]u_{n,k},
\]

\[
 G^{\mathrm{full}}_{n,ij}
 =\frac{\sqrt2}{n}\sum_{\ell=1}^{n-1}
 \beta_{n,\ell}^2a_{n,\ell i}a_{n,\ell j}.
 \tag{4.1}
\]

Equation (4.1) retains the noncommutation of \(L_n\) and \(V_n\).  Arb matrix
exponentials enclose it without diagonalizing in binary64.  For \(K=1\), the
complete metric-relative comparison gives:

As in Section 3, the table entries are nearest decimal summaries of the exact
directed rational fields stored in the JSON.

| metric | \(n\) | exact \(\delta_1(n)\) upper, decimal approx. | Stage X \(L_1\), decimal approx. | exact transferred floor, decimal approx. |
|:---:|---:|---:|---:|---:|
| \(L^2\) | 7 | \(1.05892\times10^{-4}\) | \(1.31065\times10^{-4}\) | \(2.51732\times10^{-5}\) |
| \(H^1\) | 7 | \(9.74199\times10^{-6}\) | \(1.20579\times10^{-5}\) | \(2.31593\times10^{-6}\) |

Every declared grid \(3\le n\le6\) is rigorously rejected.  Hence \(n=7\)
is the first crossing in the tested finite-model sequence.

The finite and continuum source coefficients are compared using exactly the
same declared source cost.  DCT orthogonality makes the finite \(L^2\) source
metric exactly \(I\).  The displayed \(H^1\) claim declares the continuum
cost \(1+(k\pi)^2\) on the finite coefficients as well.  If instead one wants
the natural discrete energy \(1+\omega_{n,k}n^2\), then \(S_h\ne S\) and the
generalized pair \((G_h,S_h)\) must be certified directly; this report does
not silently replace it by the continuum metric.

## 5. Descriptive two-port evidence

The same complete finite model was evaluated in binary64 for \(K=2\).  These
numbers diagnose the scale of the next proof but do not certify it.

| \(n\) | descriptive \(\delta_2(n)\) | ratio to Stage X floor |
|---:|---:|---:|
| 31 | \(1.73994\times10^{-5}\) | 121.55 |
| 63 | \(4.24927\times10^{-6}\) | 29.68 |
| 127 | \(1.04843\times10^{-6}\) | 7.32 |
| 255 | \(2.60298\times10^{-7}\) | 1.82 |
| 383 | \(1.15415\times10^{-7}\) | 0.806 |
| 511 | \(6.48439\times10^{-8}\) | 0.453 |

The apparent crossing near \(n=383\) is plausible and consistent with an
\(O(n^{-2})\) error, but it remains a hypothesis until the full finite
operator is outward-enclosed or a quantitative analytic remainder proves the
same inequality.

## 6. Negative controls and exact proof boundary

The executable controls verify that:

- the coarse \(K=2\), \(n=3\) phase grid is rejected;
- a largest entrywise error is not substituted for the operator-norm bound;
- a phase-grid certificate is never promoted to a full finite-model result;
- binary64 full-model diagnostics never decide a certificate; and
- the immediately preceding phase grids fail, preventing an unsupported
  “first grid” claim based only on the successful point.

What has **not** been proved:

- a uniform full-model bound over every \(\tau\ge1\);
- a complete finite-model crossing for \(K\ge2\);
- early-chart transfer, where discrete moment leakage and mixed words
  \(V^jA\) must be controlled;
- the reflecting-boundary family;
- target-preparation or finite-sensor frame errors; or
- transfer with a distinct finite source metric \(S_h\).

The next sharp target is now computationally concrete: prove a quantitative
full-Neumann \(O(n^{-2})\) bound tight enough to validate the observed
\(K=2\) crossing, then make its constant uniform on a compact \(\tau\)-cover
and close the analytic \(\tau\to\infty\) tail.

## 7. Reproduction

Install the narrow dependency set:

```bash
python -m pip install -r oig_xi_transfer_requirements.txt
```

Run the complete certificate and descriptive diagnostics:

```bash
python oig_xi_transfer_certificate.py \
  --max-band 8 \
  --precision-bits 320 \
  --maximum-phase-side-length 24 \
  --output /tmp/oig_xi_transfer.json
```

Run the focused tests:

```bash
python -m unittest -v test_oig_xi_transfer_certificate.py
```

The default proof run completes in under one second on the development
machine; the optional \(K=2\) descriptive sweep brings total runtime to about
eight seconds.  The JSON contains the exact rational Stage X floors, exact
dyadic upper bounds produced from Arb endpoints, transferred positive floors,
environment versions, and the proof boundary.
