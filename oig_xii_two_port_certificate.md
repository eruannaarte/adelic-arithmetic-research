# OIG Stage XII two-port finite-Neumann certificate

- **Status:** rigorous at the declared chart point and grids; not peer reviewed
- **Canonical modulation:** \(V(x)=1+\frac45x\)
- **Chart point:** one-cell lattice, \(\tau=1\), normalized by
  \(\sqrt{1+\tau}=\sqrt2\)
- **Source band:** \(K=2\), ports \(\sqrt2\cos(\pi x)\) and
  \(\sqrt2\cos(2\pi x)\)
- **Target:** central atomic cell, exactly \(x=1/2\) on the odd grids used
- **Metrics:** the declared \(L^2\) coefficient cost and continuum \(H^1\)
  coefficient cost

## 1. Result

Stage XI found a descriptive two-port crossing near \(n=383\).  The
proof-producing calculation here sharpens and validates that observation.
For the actual finite cell-centred Neumann dynamics, including the
noncommuting path Laplacian and ramp multiplication, it proves the adjacent
odd-grid brackets

\[
 \begin{array}{c|c|c}
 \text{metric}&\text{rigorously rejected}&\text{rigorously transferred}\\
 \hline
 L^2&n=343&n=345\\
 H^1&n=647&n=649.
 \end{array}
\]

“Rejected” is not merely failure of an upper-bound routine.  At each
predecessor a fixed integer Rayleigh vector gives a directed lower bound for
the true error norm that lies strictly above the exact Stage X continuum
floor.  At each successful grid, a closed-form interval enclosure of the
two-by-two spectral norm lies strictly below that floor.

The theorem is local.  It concerns one lattice point \(\tau=1\), one exactly
centred atomic target, two source ports, and the two declared coefficient
metrics.  It is not a uniform late-chart result and is not a full-atlas
finite-grid theorem.

## 2. The full finite object

Let \(L_n\) be the unscaled cell-centred Neumann path Laplacian and put

\[
 \omega_{n,\ell}=4\sin^2\frac{\pi\ell}{2n},\qquad
 V_{n,j}=1+\frac45\frac{j+1/2}{n}.
\]

For the exact DCT port \(u_{n,k}\), define

\[
 A_{n,\ell}=L_n+\omega_{n,\ell}V_n,
 \qquad
 a_{n,\ell k}=\mathbf1^T e^{-A_{n,\ell}}u_{n,k}.
 \tag{2.1}
\]

The checker evaluates (2.1) with \(A_{n,\ell}\) intact.  In particular, it
does not replace \(e^{-(L_n+\omega V_n)}\) by commuting factors and does not
discard any mixed diffusion--modulation words.

For odd \(n\), the selected target cell is exactly \(x=1/2\).  Its target
coefficient obeys the symbolic identities

\[
 \beta_{n,\ell}=0\quad(\ell\text{ odd}),\qquad
 \beta_{n,\ell}^2=\frac2n\quad(\ell\text{ even}).
\]

Consequently the full normalized finite Gram is

\[
 G^{\mathrm{full}}_{n,ij}
 =\frac{2\sqrt2}{n^2}
 \sum_{\substack{1\le\ell<n\\ \ell\ \mathrm{even}}}
 a_{n,\ell i}a_{n,\ell j}.
 \tag{2.2}
\]

These exact parity identities halve the validated work.  They do not alter
the finite model.

## 3. Validated exponential actions

A dense \(649\times649\) interval matrix exponential for every target mode
would be needlessly expensive.  The certificate instead uses a centred
Taylor action with an explicit uniform tail.

The elementary form bounds are

\[
 0\preceq L_n\preceq4I,
 \qquad I\preceq V_n\preceq\frac95I,
 \qquad 0\le\omega_{n,\ell}\le4.
\]

Set

\[
 c_\ell=2+\frac75\omega_{n,\ell},\qquad
 B_{n,\ell}=A_{n,\ell}-c_\ell I.
\]

Then

\[
 \|B_{n,\ell}\|_2
 \le \rho_\ell=2+\frac25\omega_{n,\ell}
 \le\frac{18}{5}.
\]

For Taylor degree \(m\),

\[
 \left\|e^{-A_{n,\ell}}
 -e^{-c_\ell}\sum_{r=0}^{m}\frac{(-B_{n,\ell})^r}{r!}
 \right\|_2
 \le
 e^{-c_\ell}e^{\rho_\ell}
 \frac{\rho_\ell^{m+1}}{(m+1)!}
 \le
 \frac{(18/5)^{m+1}}{(m+1)!}.
 \tag{3.1}
\]

The last quantity is an exact rational.  The production run uses \(m=32\),
for which it is approximately

\[
 2.62601279829614\times10^{-19}.
\]

Both DCT source vectors have exact Euclidean norm one.  Since
\(\|\mathbf1\|_2=\sqrt n\), the checker adds the symmetric amplitude error
\(\sqrt n\) times (3.1) to every Taylor response before assembling (2.2).
All tridiagonal recurrences, exponentials of \(-c_\ell\), trigonometric
quantities, finite sums, and error inflations use Arb ball arithmetic.

As an implementation control, the focused tests compare this sparse Taylor
construction against Arb's direct dense matrix exponential on \(n=5\); all
four Gram entries overlap.

## 4. Metric-relative spectral enclosure

Let \(G\) be the Arb-enclosed continuum phase Gram from Stage XI and let

\[
 E_n=S^{-1/2}(G_n^{\mathrm{full}}-G)S^{-1/2}.
 \tag{4.1}
\]

The two source costs are

\[
 S_{L^2}=I,
 \qquad
 S_{H^1}=\operatorname{diag}\bigl(1+\pi^2,1+4\pi^2\bigr).
\]

The \(H^1\) statement deliberately assigns this continuum coefficient cost
to the finite ports as well.  It does not claim transfer for the distinct
natural discrete energy metric.

For the symmetric interval matrix

\[
 E_n=\begin{pmatrix}a&b\\b&d\end{pmatrix},
\]

the checker encloses

\[
 \lambda_\pm=
 \frac{a+d\pm\sqrt{(a-d)^2+4b^2}}2,
 \qquad
 \delta_n=\|E_n\|_2=\max(|\lambda_-|,|\lambda_+|).
 \tag{4.2}
\]

No floating-point eigensolver or binary64 sign decision enters (4.2).  The
closed form is essential here: the absolute-row-sum bound remains above the
Stage X floor at both successful grids.

## 5. Certified brackets

The following decimals summarize exact rational or outward-rounded fields in
the generated JSON.  The decimals themselves never decide an inequality.

| metric | grid | role | rigorous deciding bound | Stage X floor | transferred finite floor |
|:---:|---:|:---|---:|---:|---:|
| \(L^2\) | 343 | Rayleigh lower rejects | \(1.43889721110\times10^{-7}\) | \(1.43151965121\times10^{-7}\) | -- |
| \(L^2\) | 345 | spectral upper passes | \(1.42232872023\times10^{-7}\) | \(1.43151965121\times10^{-7}\) | \(9.19093098375\times10^{-10}\) |
| \(H^1\) | 647 | Rayleigh lower rejects | \(3.56901705914\times10^{-9}\) | \(3.55231002210\times10^{-9}\) | -- |
| \(H^1\) | 649 | spectral upper passes | \(3.54706348692\times10^{-9}\) | \(3.55231002210\times10^{-9}\) | \(5.24653518039\times10^{-12}\) |

The rejecting Rayleigh vectors in the whitened coordinates are \((4,1)\)
for \(L^2\) and \((8,1)\) for \(H^1\).  Their quotient intervals are
strictly above the exact respective floors.  Thus the two predecessor
statements concern the true operator norm, not merely a conservative bound.

At the same predecessors, the rigorous largest-entry upper bounds are only
about \(1.35834\times10^{-7}\) in \(L^2\) and
\(3.51278\times10^{-9}\) in \(H^1\), both below their floors.  An
entrywise-maximum test would therefore falsely certify transfer even though
the Rayleigh lower bounds reject it.

For comparison, the successful-grid absolute-row-sum upper bounds are about
\(1.67055\times10^{-7}\) in \(L^2\) and
\(3.93324\times10^{-9}\) in \(H^1\), both too large to close the theorem.

## 6. What the certificate establishes

At each successful grid, Stage X gives the exact continuum generalized-frame
floor \(L_2\), while this checker proves \(\delta_n<L_2\).  Therefore

\[
 \lambda_{\min}(G_n^{\mathrm{full}},S)
 \ge L_2-\delta_n>0.
\]

This is a complete transfer for the declared finite dynamics at the single
chart point.  It includes:

- the full noncommuting generator \(L_n+\omega V_n\);
- exact finite DCT ports and central-target parity;
- the finite target-mode sum and density normalization;
- the validated continuum Gram;
- metric whitening; and
- rigorous exponential-action and spectral-norm remainders.

It does **not** establish:

- uniformity over \(\tau\ge1\) or even a compact \(\tau\)-interval;
- a complete finite late-chart theorem;
- early or reflecting-boundary finite transfer;
- target preparation away from the exactly centred atom;
- finite sensor-frame perturbations;
- a natural discrete \(H^1\) source metric; or
- any full-atlas claim.

The next analytic target is to replace these isolated brackets by a
quantitative \(O(n^{-2})\) full-Neumann bound, first uniformly on a compact
late-chart \(\tau\)-cover and then with a controlled \(\tau\to\infty\) tail.

## 7. Reproduction

Install the narrow dependency set:

```bash
python -m pip install -r oig_xii_two_port_requirements.txt
```

Run the 256-bit certificate:

```bash
python oig_xii_two_port_certificate.py \
  --precision-bits 256 \
  --taylor-degree 32 \
  --output /tmp/oig_xii_two_port.json
```

Run the focused tests, including 192/256-bit repetition and the independent
small-grid dense-exponential comparison:

```bash
python -m unittest -v test_oig_xii_two_port_certificate.py
```

On the development machine, one two-metric certificate run takes about
19 seconds and the ten focused tests take about 38 seconds.  The JSON stores
the exact Stage X rational floors, exact rational Taylor tail, directed
dyadic endpoints, interval Grams and eigenvalues, predecessor Rayleigh lower
bounds, transferred positive floors, environment versions, and the explicit
scope boundary.
