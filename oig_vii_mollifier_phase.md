# Operational Information Geometry VII computational report

## Smooth-to-atomic mollifier phase diagram

- **Research and computation:** Codex (OpenAI)
- **Originating direction and research environment:** TGN's human founder
- **Date:** 14 August 2026
- **Status:** analytic phase laws plus reproducible numerical evidence; not peer reviewed
- **Laboratory:** `oig_vii_mollifier_phase.py`
- **Tests:** `test_oig_vii_mollifier_phase.py`

## 1. Outcome

The smooth preparation and the target atom are not separate phenomena.  In the
declared path model they are the two ends of a two-parameter phase diagram.
For a Gaussian target of width \(\varepsilon\), mesh width \(h=1/n\), and a
fixed odd source cosine, there are two natural charts:

\[
 \boxed{\ \|R_{h,\varepsilon}(t)\|
   \sim \varepsilon^{-1/2}P(t/\varepsilon^2)\ }
 \qquad (\varepsilon/h\to\infty),
\]

and

\[
 \boxed{\ \|R_{h,ch}(\tau h^2)\|
   \sim h^{-1/2}\Psi_c(\tau)\ }
 \qquad (\varepsilon/h\to c<\infty).
\]

The resolved phase has the two ends

\[
 P(q)\sim C_0q\quad(q\downarrow0),\qquad
 P(q)\sim C_\infty q^{-1/4}\quad(q\to\infty).
\]

Consequently

\[
 \|R(t)\|\sim C_0t\varepsilon^{-5/2}
 \quad(t\ll\varepsilon^2),
\]

and

\[
 \|R(t)\|\sim C_\infty t^{-1/4}
 \quad(\varepsilon^2\ll t\ll1).
\]

At finite \(c\), the complete response is instead \(h^{-1/2}\) at
\(t=\tau h^2\).  The atomic chart is \(c=0\).  The charts agree in their
overlap:

\[
 \sqrt c\,\Psi_c(c^2q)\longrightarrow P(q).
\]

This supplies the phase diagram requested at the end of Stage VI and explains
the Stage V \(n^{5/2}\) first jet and \(n^{1/2}\) initial-layer response as
different sections of one scaling surface.

## 2. Exact declared experiment and normalization

Let

\[
 x_j=(j+1/2)/n,\qquad A_n=n^2L_n,\qquad D_n=\operatorname{diag}(x_j),
\]

and

\[
 G_n=A_n\otimes I+(I+gD_n)\otimes A_n,
 \qquad g=4/5.
\]

All refinement experiments use odd \(n\), so the preparation centre
\(y_0=1/2\) is exactly a cell centre.  The target probability vector consists
of exact cell integrals of the Gaussian

\[
 \rho_\varepsilon(y)
 =\frac{1}{\sqrt{2\pi}\varepsilon}
   e^{-(y-1/2)^2/(2\varepsilon^2)},
\]

renormalized by its mass on \([0,1]\).  The cell masses are differences of
normal CDF values, not midpoint samples.  At \(\varepsilon=0\), the definition
is the central-cell atom.

The source port is the continuum-unit mode

\[
 \phi_k(x)=\sqrt2\cos(k\pi x),
\]

represented by the probability perturbation \(u_{k,n}/\sqrt n\).  The target
probability marginal is multiplied by \(\sqrt n\) before its Euclidean norm is
taken.  These factors cancel in the modal response, but the dense control in
the code applies both explicitly.  Thus the reported quantity is the complete
density-normalized target \(L^2\) response norm, not an unnormalized probability
norm and not a fixed target-band projection.

The direct \(n^2\)-state computation and the target-mode reduction agree to a
maximum absolute entry error below

\[
 4\times10^{-16}
\]

at \(n=7\), three source modes, and four times.  The source density Gram error
is \(4.14\times10^{-16}\), target mass and reflection errors are zero, and the
time-zero response is exactly zero in the modal calculation.

## 3. Exact finite modal identity

Let \(u_{\ell,n}\) be the orthonormal DCT modes,

\[
 \mu_{\ell,n}=4n^2\sin^2\!\frac{\ell\pi}{2n},
 \qquad \beta_{\ell,n}=u_{\ell,n}^{\mathsf T}q_{n,\varepsilon}.
\]

For source mode \(k\), the \(\ell\)-th target coefficient is exactly

\[
 r_{\ell,n}(t)=\beta_{\ell,n}\,
 \mathbf1^{\mathsf T}e^{-tK_{\ell,n}}u_{k,n},
\]

where

\[
 K_{\ell,n}=A_n+\mu_{\ell,n}(I+gD_n).
\]

Therefore

\[
 \|R_{n,\varepsilon,k}(t)\|^2
 =\sum_{\ell=1}^{n-1}|r_{\ell,n}(t)|^2.
\]

No target truncation occurs.  The implementation diagonalizes the symmetric
tridiagonal \(K_{\ell,n}\) and uses `expm1` in the zero-sum scalar product to
avoid cancellation when \(t=O(n^{-2})\).

Differentiating at zero gives another exact finite identity:

\[
 \boxed{
 \|R'_{n,\varepsilon,k}(0)\|
 =g\,|\mathbf1^{\mathsf T}D_nu_{k,n}|\,
   \|A_nq_{n,\varepsilon}\|_2 .}
\]

This equality is tested independently in physical and target-modal
coordinates.

## 4. Resolved first jet

For the standard normal \(\eta\),

\[
 \widehat\eta(\xi)=e^{-\xi^2/2},\qquad
 \|\eta''\|_{L^2(\mathbb R)}
 =\sqrt{\frac{3}{8\sqrt\pi}}.
\]

For odd \(k\),

\[
 m_k:=\int_0^1x\phi_k(x)\,dx
 =-\frac{2\sqrt2}{(k\pi)^2}.
\]

Cell averaging and the cell-centred Laplacian give, when
\(h/\varepsilon\to0\) and \(\varepsilon\to0\),

\[
 \varepsilon^{5/2}\|R'_{n,\varepsilon,k}(0)\|
 \longrightarrow C_{0,k}
 :=g|m_k|\|\eta''\|_2.
\]

For \(g=4/5,k=1\),

\[
 C_{0,1}=0.105454083305103465691404219277\ldots.
\]

The whole-line Gaussian is used in this limiting constant.  The finite code
uses its exactly normalized restriction to \([0,1]\); because the centre is
interior, the difference is exponentially small in \(1/\varepsilon^2\).

For the path \(\varepsilon=n^{-0.6}\):

| \(n\) | \(\varepsilon/h\) | \(\varepsilon^{5/2}\|R'_n(0)\|\) | relative error |
|---:|---:|---:|---:|
| 127 | 6.9426 | 0.104771264 | \(6.48\times10^{-3}\) |
| 255 | 9.1752 | 0.105063134 | \(3.71\times10^{-3}\) |
| 511 | 12.1163 | 0.105229823 | \(2.13\times10^{-3}\) |
| 1023 | 15.9937 | 0.105325340 | \(1.22\times10^{-3}\) |
| 2047 | 21.1080 | 0.105380151 | \(7.01\times10^{-4}\) |

## 5. Continuum phase function

For a high target mode with \(s=t(\ell\pi)^2\), source diffusion disappears
to leading order on the fixed smooth port, while the rate modulation remains.
The limiting source scalar has the closed form

\[
 F_k(s)=\int_0^1e^{-s(1+gx)}\phi_k(x)\,dx
 =\frac{\sqrt2e^{-s}(gs)
 [1-(-1)^ke^{-gs}]}{(gs)^2+(k\pi)^2}.
\]

For the centered Gaussian, the resolved phase is

\[
 \boxed{
 P_k(q)^2=\int_0^\infty
 e^{-(\pi z)^2}\,F_k(q\pi^2z^2)^2\,dz .}
\]

The factor from the vanishing odd target modes and the doubled even-mode
coefficient cancels exactly in the Riemann-sum limit.

The two ends follow by dominated convergence and Parseval.  As \(q\downarrow0\),

\[
 F_k(s)=-sgm_k+O(s^2),\qquad P_k(q)\sim C_{0,k}q.
\]

As \(q\to\infty\), substitute \(z=u/\sqrt q\):

\[
 P_k(q)\sim C_{\infty,k}q^{-1/4},\qquad
 C_{\infty,k}^2=\int_0^\infty F_k(\pi^2u^2)^2\,du.
\]

At \(g=4/5,k=1\), 60-digit quadrature gives

\[
 C_{\infty,1}
 =0.0296243284394334623461787404606825975\ldots.
\]

Binary64 quadrature differs by \(3.47\times10^{-18}\).  This is a
high-precision cross-check, not an outward-rounded interval certificate.

| \(q=t/\varepsilon^2\) | \(P(q)\) | \(P/(C_0q)\) | \(P/(C_\infty q^{-1/4})\) |
|---:|---:|---:|---:|
| 0.001 | 0.0001050862 | 0.996511 | 0.000631 |
| 0.01 | 0.0010187731 | 0.966082 | 0.010875 |
| 0.1 | 0.0077518050 | 0.735088 | 0.147148 |
| 1 | 0.0200620904 | 0.190245 | 0.677217 |
| 10 | 0.0159248643 | 0.015101 | 0.955932 |
| 100 | 0.0093252023 | 0.000884 | 0.995428 |

The phase peaks at

\[
 q_*=1.4607992112,\qquad P(q_*)=0.02037281848.
\]

Direct full finite responses on \(\varepsilon=n^{-0.6}\), at
\(q=(0.03,0.1,0.3,1,3)\), collapse after multiplication by
\(\sqrt\varepsilon\).  Their maximum relative errors against \(P\) are:

| \(n\) | \(\varepsilon/h\) | maximum error |
|---:|---:|---:|
| 127 | 6.9426 | 0.03456 |
| 255 | 9.1752 | 0.01923 |
| 511 | 12.1163 | 0.00842 |

The analytic formula above is a continuum high-band asymptotic.  The displayed
joint finite-grid convergence is computational evidence; this report does not
supply a single uniform remainder bound over every path
\((h,\varepsilon,t)\to0\).

## 6. Finite-width lattice phase

Let \(c=\varepsilon/h\) stay finite.  The limiting Gaussian cell masses are

\[
 Q_c(r)=\Phi((r+1/2)/c)-\Phi((r-1/2)/c),\qquad r\in\mathbb Z,
\]

with \(Q_0=\delta_0\), and define

\[
 B_c(\pi\xi)=\sum_{r\in\mathbb Z}Q_c(r)\cos(\pi\xi r).
\]

The lattice phase is

\[
 \boxed{
 \Psi_{c,k}(\tau)^2
 =\int_0^1|B_c(\pi\xi)|^2
 \left|F_k\!\left(4\tau\sin^2\frac{\pi\xi}{2}\right)\right|^2d\xi .}
\]

For fixed \(c,\tau\), the target DCT sum is a Riemann sum in
\(\xi=\ell/n\).  On a fixed smooth source port,
\(h^2A_n=L_n\) disappears strongly while
\(t\mu_{\ell,n}=4\tau\sin^2(\pi\xi/2)\) remains.  This yields

\[
 n^{-1/2}\|R_{n,ch}(\tau h^2)\|\to\Psi_c(\tau).
\]

This is fixed-port strong asymptotics, not convergence of the complete
semigroup in operator norm.

For the atom, \(B_0=1\).  At small \(\tau\),

\[
 \Psi_0(\tau)\sim g|m_k|\sqrt6\,\tau,
\]

because \(\int_0^1(4\sin^2(\pi\xi/2))^2d\xi=6\).  For \(k=1\), its exact
coefficient is

\[
 0.56157900144494610279489106785\ldots.
\]

At large \(\tau\), every fixed \(c\) has

\[
 \Psi_c(\tau)\sim C_\infty\tau^{-1/4},
\]

because the active wavelengths exceed the fixed preparation width in cells.
For the atom, the ratios to these two asymptotes are 0.995345 at
\(\tau=0.001\) and 1.000575 at \(\tau=100\), respectively.

Across \(c=0,0.5,1,2,4\) and six times from \(\tau=0.03\) to 10, the maximum
finite-grid errors against \(\Psi_c\) are:

| \(n\) | worst relative error over all \(c,\tau\) |
|---:|---:|
| 63 | 0.01272 |
| 127 | 0.00316 |
| 255 | 0.000785 |
| 511 | 0.000196 |

This approximately fourfold reduction is consistent with the cell-centred
second-order error, but no uniform second-order theorem in \(c,\tau\) is
claimed here.

For a genuinely vanishing ratio \(c_n=n^{-1/4}\), the maximum response error
against the central-cell atom at \(\tau=(0.1,1,10)\) falls as follows:

| \(n\) | \(c_n\) | central-cell mass | maximum response error |
|---:|---:|---:|---:|
| 63 | 0.35495 | 0.84106 | 0.24754 |
| 127 | 0.29789 | 0.90675 | 0.14612 |
| 255 | 0.25024 | 0.95429 | 0.07188 |
| 511 | 0.21033 | 0.98256 | 0.02748 |

Thus \(\varepsilon/h\to0\) really does select the atomic phase; it is not
merely a label assigned to a narrow but resolved density.

## 7. The overlap and maximum-response ridge

As \(c\to\infty\), put \(\xi=z/c\).  Cell averaging gives

\[
 B_c(\pi z/c)\to e^{-(\pi z)^2/2},
\]

and

\[
 4c^2q\sin^2(\pi z/(2c))\to q\pi^2z^2.
\]

Therefore

\[
 c\Psi_c(c^2q)^2\to P(q)^2.
\]

For \(q=(0.1,1,10)\), the maximum relative bridge error is

| \(c\) | maximum bridge error |
|---:|---:|
| 2 | 0.04491 |
| 4 | 0.01136 |
| 8 | 0.002848 |
| 16 | 0.0007125 |
| 32 | 0.0001782 |

The same bridge predicts a ridge in the phase diagram:

\[
 \tau_{*,c}/c^2\to q_*,\qquad
 \sqrt c\,\Psi_c(\tau_{*,c})\to P(q_*).
\]

At \(c=8\), these quantities are 1.462521 and 0.02037147, within
\(1.18\times10^{-3}\) and \(6.62\times10^{-5}\) of the continuum peak.

## 8. A parity boundary

The \(t\varepsilon^{-5/2}\) law requires \(m_k\ne0\), hence an odd source
mode in this centered linear-modulation experiment.  The closed formula for
\(F_k\) shows

\[
 F_k(s)=O(s)\quad(k\text{ odd}),\qquad
 F_k(s)=O(s^2)\quad(k\text{ even}).
\]

Numerical local orders over \(s=10^{-4}\) to \(10^{-3}\) are 0.999 and
1.999.  For even modes the leading resolved small-time law is instead
\(t^2\varepsilon^{-9/2}\).  This is a useful falsification boundary: the
phase exponents are properties of the preparation, dynamics, **and port**, not
of the atom alone.

## 9. Epistemic ledger

### Exact finite identities

1. density normalization and target-mode reduction;
2. Gaussian cell probabilities as CDF differences;
3. the finite first-jet norm;
4. DCT spectrum and complete modal norm; and
5. agreement with the direct joint generator to floating roundoff.

### Analytically derived phase structure

1. the closed source profile \(F_k\);
2. the continuum phase integral \(P_k\);
3. its \(q\) and \(q^{-1/4}\) ends;
4. the finite-width lattice integral \(\Psi_{c,k}\);
5. its atomic small-time and universal fixed-\(c\) large-time ends; and
6. the bridge \(\sqrt c\Psi_c(c^2q)\to P(q)\).

### Computational evidence

1. simultaneous finite-grid convergence to \(P\);
2. finite-grid convergence to \(\Psi_c\) throughout the declared table;
3. convergence of \(\varepsilon/h\to0\) to the atom;
4. the maximum-response ridge; and
5. 60-digit scalar quadrature against binary64.

### Not certified or claimed

1. The improper integrals are not outward-rounded interval enclosures.
2. No error estimate is uniform over every path in the full
   \((h,\varepsilon,t)\) corner.
3. The centered calculation fixes the carrier phase at \(y_0=1/2\); other
   lattice placements can introduce a phase parameter at finite \(c\).
4. The \(t^{-1/4}\) statement is the short-positive-time window
   \(\varepsilon^2\ll t\ll1\), not a long-time law on the bounded interval.
5. The limit is for fixed smooth source ports, not full operator norm.
6. Nothing here identifies physical spacetime or a fundamental substrate.

## 10. Reproduction

Reference environment:

- Python 3.12.9
- NumPy 2.4.6
- SciPy 1.15.2
- mpmath 1.3.0
- macOS arm64

Commands:

```bash
python -m pip install -r oig_vii_mollifier_requirements.txt
python -m py_compile oig_vii_mollifier_phase.py test_oig_vii_mollifier_phase.py
python -m unittest -v test_oig_vii_mollifier_phase.py
python oig_vii_mollifier_phase.py --fast
python oig_vii_mollifier_phase.py
python -m unittest discover -q
```

The default full audit uses \(n\le511\); the first-jet-only calculation reaches
\(n=2047\).  No external machine is required.
