# OIG VIII three-parameter computational and adversarial report

## 1. Scope and verdict

This laboratory tests the proposed finite comparison in the variables

\[
 h=1/n,\qquad c=\varepsilon/h,\qquad
 \tau=t/h^2,\qquad q=t/\varepsilon^2=\tau/c^2.
\]

For the canonical midpoint ramp, conservative Gaussian preparations, and
fixed source ports, the evidence strongly supports a chartwise comparison:

* the fixed-\((c,\tau)\) squared lattice residual is empirically second order
  in \(h\);
* the lattice-to-continuum bridge residual is empirically second order in
  \(c^{-1}=h/\varepsilon\);
* the proposed balanced and atomic-tail error scales contain every tested
  asymptotic path, with small port-dependent constants; and
* the exact Gaussian/ramp endpoint correction explains most of the apparent
  early-law error.

The same computations falsify several stronger statements. There is no
placement-free critical lattice chart, no continuum chart uniform down to
\(c\ll1\), no lattice initial-layer chart uniform at fixed positive physical
time, and no meaningful relative theorem at exact null ports. A major
practical finding is that the critical-width laws are extraordinarily
pre-asymptotic, especially for the even source.

These are floating-point experiments, not proofs or interval certificates.

## 2. Declared finite model and normalization

The source and target grids are the \(n\) cell centres
\(x_j=(j+1/2)/n\). Let \(L_n=h^2A_n\) be the raw Neumann path Laplacian and

\[
 \omega_{\ell,n}=4\sin^2\!\left(\frac{\pi\ell}{2n}\right),
 \qquad V_j=1+\frac45x_j.
\]

After exact target-mode separation, the source coefficient at the lattice
time \(t=\tau h^2\) is

\[
 a_{\ell k}^{(n)}(\tau)
 =\mathbf1^{\mathsf T}
   e^{-\tau(L_n+\omega_{\ell,n}V_n)}u_{k,n}.
\]

For target cell masses \(Q_n\) and target cosine coefficients
\(\beta_{\ell,n}=u_{\ell,n}^{\mathsf T}Q_n\), the complete response is

\[
 N_{n,c,\theta,k}(\tau)^2
 =\sum_{\ell=1}^{n-1}
  |\beta_{\ell,n}a_{\ell k}^{(n)}(\tau)|^2.
\]

The two normalized quantities used below are

\[
 S_n=\frac{N_n}{\sqrt n},
 \qquad
 \sqrt\varepsilon N_n=\sqrt c\,S_n.
\]

Gaussian target masses are integrated over cells, not sampled at cell
centres. The local placement parameter is

\[
 y_n=x_{j_n}+\theta h,\qquad -\tfrac12\leq\theta\leq\tfrac12.
\]

At \(c=0\), \(\theta=0\) declares a one-cell atom and
\(\theta=1/2\) declares the symmetric half/half weak limit at a cell
boundary.

## 3. What is exact and what is numerical

The following statements are algebraic identities of the declared finite
model:

1. the target-mode reduction above;
2. the full norm as the sum of the modal squares;
3. the scaled-clock first jet

   \[
   \partial_\tau(\beta_{\ell,n}a_{\ell k}^{(n)})(0)
   =-g(\mathbf1^{\mathsf T}D_nu_{k,n})
     \omega_{\ell,n}\beta_{\ell,n};
   \]

4. the triangle decomposition

   \[
   |\sqrt cS_n-P(q)|
   \leq
   \sqrt c|S_n-\Psi_{c,\theta}(\tau)|
   +|\sqrt c\Psi_{c,\theta}(\tau)-P(q)|;
   \]

5. constant modulation makes every nonconstant source port null; and
6. reflection-symmetric modulation makes every reflection-odd source port
   null.

A direct \(7^2\)-state matrix exponential and the separated calculation agree
to \(1.6\times10^{-13}\) relatively. This is a roundoff check of the first
identity, not its proof.

The phase integrals, convergence rates, residual magnitudes, and extrema in
the remainder of this report are floating evidence.

## 4. Rectangular stress scan

The main scan contains 720 parameter points:

\[
\begin{aligned}
n&\in\{31,63,127\},\\
c&\in\{0.05,0.25,1,4\},\\
\tau&\in\{0.003,0.03,0.3,3,30\},\\
k&\in\{1,2,3,4\},\\
\theta&\in\{0,0.25,0.5\}.
\end{aligned}
\]

The median absolute finite-to-lattice error decreases as

\[
1.23\times10^{-5},\quad3.18\times10^{-6},\quad7.89\times10^{-7},
\]

for \(n=31,63,127\). The corresponding maxima are

\[
2.07\times10^{-3},\quad4.58\times10^{-4},\quad1.19\times10^{-4}.
\]

The worst point uses \(n=31,c=4,\tau=30,\theta=1/2,k=1\), where neither
the preparation nor the diffusion length is especially local relative to the
finite interval. Across fixed parameter paths, the median fitted norm-error
power is \(n^{-1.993}\). The least mature path fits \(n^{-1.29}\), again at
the edge of this small-grid, large-clock box.

Evaluating the continuum formula everywhere is intentionally adversarial.
Its median relative error is still \(0.078\) at \(n=127\), and its worst
relative error is \(0.99993\). The continuum chart is not a global substitute
for the lattice chart.

## 5. Candidate A: balanced resolved comparison

The squared residual is

\[
 E_A=|\varepsilon N_h^2-P(q)^2|
 =|cS_h^2-P(q)^2|.
\]

It was tested along \(\varepsilon=n^{-\alpha}\),
\(\alpha\in\{0.4,0.6,0.75\}\), with
\(q\in\{0.1,0.5,2\}\), both parities, and
\(\theta\in\{0,0.3\}\). Every terminal residual is contained by

\[
 \varepsilon^2+c^{-2}
\]

with the largest observed quotient \(2.69\times10^{-3}\). This small number
should not be read as a sharp universal constant: the response itself is
small, and individual residuals undergo sign cancellations before settling.
The experiment supports the proposed scale but does not determine its optimal
coefficient.

No \(c^{-1}\) term was detected for the off-centre conservative preparation.
Within this model, using the correct \(\theta\)-dependent phase preserves the
same second-order behavior. A first-order term may remain necessary for less
symmetric discretizations, but it is not forced merely by taking
\(\theta\ne0\).

## 6. Candidate B: fixed lattice comparison

At fixed \((c,\tau,\theta,k)\), the tested residual is

\[
 E_B=|hN_h^2-\Psi_{c,\theta,k}(\tau)^2|
 =|S_h^2-\Psi_{c,\theta,k}(\tau)^2|.
\]

Across
\(c\in\{0.25,1,4\}\),
\(\tau\in\{0.03,0.3,3\}\),
\(k\in\{1,2\}\), and four grids through \(n=255\), the centered median
fitted power is \(h^{1.990}\); the full range is approximately
\(h^{1.80}\) to \(h^{2.00}\). The slower fits arise from the coarsest,
widest preparations. For the representative point
\((c,\tau,k)=(1,0.3,1)\), the fitted powers are

\[
1.99814,\quad1.99814,\quad1.99814
\]

for \(\theta=0,0.3,0.5\), respectively. The quantities \(E_B/h^2\)
converge to approximately \(6.98\times10^{-4}\).

Thus the experiment supports an \(O(h^2)\) canonical theorem and gives no
evidence that a correctly charted conservative off-centre preparation drops
to first order.

## 7. Lattice-to-continuum bridge

For

\[
 E_{\rm bridge}(c)
 =|\sqrt c\,\Psi_{c,\theta,k}(c^2q)-P_k(q)|,
\]

with \(c=2,4,8,16,32\), three values of \(q\), both source parities, and
\(\theta=0,1/2\), the fitted powers in \(c\) range from
\(-2.008\) to \(-1.962\), with median \(-1.999\). This is clean numerical
evidence for the proposed \(O(c^{-2})\) bridge in the conservative Gaussian
model.

## 8. Candidate C: joint atomic tail

The atomic squared residual is

\[
 E_C=|\sqrt t\,N_h^2-C_{\infty,k}^2|.
\]

Paths were chosen as

\[
 \tau=n^\beta,\qquad c=n^\gamma,
 \qquad0<\beta<2,\quad\gamma<\beta/2,
\]

so that \(t\to0\), \(h/\sqrt t\to0\), and
\(\varepsilon/\sqrt t\to0\). Every tested terminal residual is contained by

\[
 \sqrt t+\left(\frac{\varepsilon}{\sqrt t}\right)^2
 +\left(\frac h{\sqrt t}\right)^2,
\]

with largest quotient \(3.10\times10^{-3}\). Both the cell-centred and
cell-boundary preparations converge. This is evidence for the proposed joint
tail scale, while the broad range of fitted single powers confirms that it is
genuinely a sum of competing errors rather than one universal monomial.

## 9. Candidate D and the exact endpoint correction

For a ramp source of multiplication order \(r\), direct expansion of the
Gaussian phase gives the exact first correction

\[
 \frac{P_k(q)}{C_{r,k}q^r}
 =1-\gamma_rq+O(q^2),
 \qquad
 \gamma_r=\frac{(2+g)(4r+1)}4.
\]

At \(g=0.8\),

\[
 \gamma_1=3.5,\qquad\gamma_2=6.3.
\]

At \(q=10^{-4}\), independent quadrature estimates these coefficients as
\(3.498879\) and \(6.297040\). Across six early values of \(q\), the
uncorrected residual fits \(q^{0.986}\) and \(q^{0.980}\), while subtracting
the exact correction gives \(q^{1.986}\) and \(q^{1.980}\). Modes three and
four give the same parity-dependent coefficients and powers.

The new weak-Duhamel estimate sharpens the canonical ramp bound to

\[
\begin{array}{ll}
r=1:&\text{relative error }O(q+c^{-2}+\varepsilon^2),\\
r=2:&\text{relative error }O(q+c^{-2}+\varepsilon^2).
\end{array}
\]

Both continuum parities begin with the explicit \(O(q)\) relative correction,
and the corrected continuum residual is \(O(q^2)\). At \(n=255\), the largest
uncorrected quotient by the displayed canonical candidate scale is \(2.55\)
for odd modes and \(4.39\) for even modes; these are ordinary port constants,
not divergent rates. A general cancelled second-order port may retain a
weaker \(O(\sqrt q)\) form remainder and also requires quantitative control of
its discrete first-moment leakage.

There is a real uniformity caveat. With
\(\varepsilon=n^{-0.4}\), \(q=10^{-3}\), and the even port, the relative
leading-law errors at \(n=63,127,255\) are

\[
14.32,\qquad1.75,\qquad0.00664.
\]

The untruncated Gaussian mass outside \([0,1]\) on those grids is

\[
8.73\times10^{-3},\qquad5.18\times10^{-4},
\qquad4.48\times10^{-6}.
\]

Although exponentially small in \(1/\varepsilon^2\), this boundary tail is
not initially small relative to the \(q^2\) even signal. A relative early-law
theorem therefore needs either a compactly supported interior mollifier or an
explicit tail condition such as ``boundary error is \(o(q^r)\).'' This is a
pre-asymptotic boundary, not a contradiction of the eventual law.

## 10. Critical widths are computationally glacial

At order \(r\), the critical width exponent is

\[
 \alpha_r=\frac{4r}{4r+1},\qquad
 c=n^{1/(4r+1)},\qquad n=c^{4r+1}.
\]

With \(\tau=1\), the direct finite relative errors to the leading critical
constant are:

| \(n\) | odd, \(r=1\), \(\alpha=4/5\) | even, \(r=2\), \(\alpha=8/9\) |
|---:|---:|---:|
| 63  | 0.42744 | 0.82832 |
| 127 | 0.35860 | 0.79442 |
| 255 | 0.29616 | 0.75782 |
| 511 | 0.24098 | 0.71850 |

The finite response already agrees with the lattice phase much more closely:
the odd finite-to-lattice relative error falls from
\(1.35\times10^{-3}\) to \(2.05\times10^{-5}\), and the even error from
\(5.35\times10^{-3}\) to \(8.20\times10^{-5}\). The slow convergence is
therefore in \(c\to\infty\), not a failure of finite-to-lattice convergence.

The lattice phase can extrapolate to inaccessible critical grids:

| order | \(c\) | equivalent \(n=c^{4r+1}\) | error to leading law |
|---:|---:|---:|---:|
| 1 | 4  | 1,024 | 0.1934 |
| 1 | 8  | 32,768 | 0.0563 |
| 1 | 16 | 1,048,576 | 0.0147 |
| 2 | 4  | 262,144 | 0.3322 |
| 2 | 8  | 134,217,728 | 0.1039 |
| 2 | 16 | 68,719,476,736 | 0.0353 |

This is an important practical boundary: the critical exponents can be
correct while direct feasible computations remain far from their final
constants. The exact endpoint correction gives the right extrapolation
variable and explains why \(c\), rather than nominal \(n\), controls the
visible convergence.

## 11. Explicit counterexamples to naive uniformity

### 11.1 Placement blindness

At \(c=0.05\), \(\tau=0.01\), and \(k=1\), the atom and equal-split phase
values are

\[
0.0053604243,\qquad0.0022141320.
\]

Their persistent gap is \(0.0031462923\). At \(n=127\), the correctly
charted boundary error is already below \(7\times10^{-8}\), while its error
to the placement-blind atom remains above \(0.003146\).

### 11.2 Continuum dispersion below mesh resolution

At \(c=0.05\), \(\tau=0.1\), the correct lattice phase is
\(0.0356999636\), while the continuum prediction expressed in lattice units
is \(0.0520819079\). The gap \(0.0163819443\) persists as \(n\to\infty\) at
fixed \((c,\tau)\).

### 11.3 Lattice initial layer at fixed positive time

Along \(\tau=3n^2\), physical time is fixed at \(t=3\). The finite response
is exponentially small, whereas the infinite-lattice phase retains its
algebraic initial-layer tail. The relative error is numerically one on every
tested grid. A lattice-tail theorem must require \(t=\tau h^2\to0\).

### 11.4 Wandering microscopic phase

For the fixed irrational centre \(y_0=\sqrt2/3\), \(c=0.08\), and
\(\tau=0.01\), the phases generated by \(31\leq n\leq600\) range from
\(0.0022142213\) to \(0.0053604243\). Selected finite grids agree with the
corresponding phase values, not with one phase-independent constant. A
subsequence or explicit placement rule is indispensable.

### 11.5 Relative error at null ports

Constant modulation leaves floating residual below \(1.3\times10^{-14}\).
A symmetric modulation with reflection-odd sources leaves residual below
\(1.8\times10^{-14}\), while even controls remain visibly nonzero. These are
numerical shadows of exact null identities. Division by either reference is
mathematically undefined, so a uniform result must use absolute or
envelope-normalized error near null ports.

## 12. Reproduction

Run the focused suite and both audit sizes with

```text
python -m py_compile oig_viii_three_parameter.py \
  test_oig_viii_three_parameter.py
python -m unittest -v test_oig_viii_three_parameter.py
python oig_viii_three_parameter.py --fast
python oig_viii_three_parameter.py
```

The focused suite contains 19 tests. On the reference host the full JSON
audit takes about 13 seconds and requires no external machine.

## 13. Recommended analytic consequences

The evidence suggests that the theorem should be stated chartwise and in
squared norm:

1. prove the fixed-compact \((c,\tau)\) residual as \(O(h^2)\) for the
   canonical midpoint/conservative scheme;
2. prove the Gaussian bridge as \(O(c^{-2})\), uniformly for \(q\) in compact
   subsets of \((0,\infty)\) and uniformly in declared interior phase;
3. combine those estimates with the exact triangle decomposition;
4. state the atomic-tail estimate only when \(t\to0\) and both
   \(h/\sqrt t\) and \(\varepsilon/\sqrt t\) vanish;
5. use the exact \(\gamma_rq\) correction for the canonical ramp, while
   retaining the weaker generic even-port remainder where appropriate;
6. add a quantitative interior-tail hypothesis for relative early laws; and
7. keep placement phase, symmetry nulls, and critical pre-asymptotics in the
   theorem's falsification ledger.

The computations do not prove these estimates. They identify a formulation
that survived the declared tests and record the nearby stronger formulations
that did not.
