# OIG VIII adversarial audit

- **Date:** 14 August 2026
- **Scope:** independent audit of the Stage VIII uniform comparison memos
- **Status:** proof audit; not peer reviewed

## 1. Verdict

The lattice-side result has a sound core.  In the declared cell-centred
model, the exact normalization, carrier decomposition, fixed-microscopic-time
chart, lattice-tail constant, boundary image factor, and simultaneous
interior atomic limit all survive adversarial checking.  In particular, the
stable joint statement is the squared-norm limit

\[
  \sqrt t\,\mathcal N_h(t)^2\longrightarrow C_F^2
\]

when \(t\to0\), \(t/h^2\to\infty\), target variance is \(o(t)\), and the
target barycentre is at distance \(\gg\sqrt t\) from both reflectors.

The first proof-memo versions needed one hypothesis repair, one missing
quantitative argument, and several smaller domain and wording repairs.  The
canonical synthesis now incorporates those repairs; none changed the
principal atomic theorem.

The resolved-side theorem is valid in its early, balanced, and heat-resolved
charts.  The initially compressed all-\(q\) step is now closed by an explicit
uniform Dyson jet and conservative spectral-jet identity, audited in Section
7.2.

## 2. Checks that passed

### 2.1 Finite normalization

For \(h=1/n\), the cell-centred modes

\[
 \varphi_{\ell,h}(i)=\sqrt2\cos(\ell\pi(i+1/2)h)
\]

are orthonormal in \(h\sum_i\), with path eigenvalue
\(4h^{-2}\sin^2(\ell\pi h/2)\).  A probability-mass target therefore has
coefficient \(\beta_{\ell,h}=\sum_iq_i\varphi_{\ell,h}(i)\), and

\[
 \mathcal N_h^2=\sum_{\ell=1}^{n-1}|\beta_{\ell,h}|^2|a_{\ell,h}|^2
\]

contains no missing factor of \(h\), \(n\), or \(2\).  The Euclidean
normalization used by `oig_viii_three_parameter.py` cancels the reciprocal
\(\sqrt n\) factors between its source amplitude and target coefficient, so
its reported full norm is the same \(\mathcal N_h\).

### 2.2 Carrier identity and reflecting boundary factor

Writing \(\beta=\sqrt2\operatorname{Re}(e^{i\ell\pi y}W)\) gives exactly

\[
 |\beta|^2=|W|^2+\operatorname{Re}(e^{2i\ell\pi y}W^2).
\]

Thus the interior carrier averages to zero, whereas an endpoint carrier
contributes a second copy of the nonoscillatory term.  The boundary-layer
profile

\[
 C_{F,\kappa}^2=\int_0^\infty
 [1+\cos(2\pi\kappa r)]|F(\pi^2r^2)|^2\,dr
\]

has the correct normalization: \(C_{F,0}^2=2C_F^2\).  A direct finite-grid
control along \((n,\tau)=(63,4),(127,8),(255,16)\), for which the first-cell
barycentre has \(d/\sqrt t=1/(2\sqrt\tau)\to0\), gave boundary/interior
ratios tending respectively to \(2\) and \(1\) after division by \(C_F^2\):
the boundary ratios were \(1.9213,1.9610,1.9806\), while the interior ratios
were \(1.0200,1.0097,1.0048\).  These are floating-point controls, not proof.

### 2.3 Variance is the correct preparation variable

For the barycentrically centred characteristic function,

\[
 |\chi_h(k)-1|\leq \tfrac12 k^2\sigma_h^2
\]

is exact.  On \(k=O(t^{-1/2})\), it gives the dimensionless error
\(\sigma_h^2/t\).  It also controls both the nonoscillatory factor
\(|\chi|^2\) and the carrier factor \(\chi^2\), after using the trivial
bound when \(k^2\sigma_h^2>1\).  Fixed-cell preparations have
\(\sigma_h^2=O(h^2)\), hence error \(O(1/\tau)\).

### 2.4 Lattice dispersion and Riemann spacing

With \(r_\ell=\ell\sqrt t\), the rescaled modal spacing is \(\sqrt t\), and

\[
 4\tau\sin^2\!\left(\frac{\pi r}{2\sqrt\tau}\right)
 =\pi^2r^2+O(r^4/\tau).
\]

The exponential modal envelope makes the accumulated dispersion error
\(O(1/\tau)\), not an error multiplied by the raw number of target modes.
The corresponding quadrature error is \(O(\sqrt t)\).  The formula

\[
 \sqrt\tau\,\Psi_Q(\tau)^2
 =\int_0^{\sqrt\tau}|B_Q(\pi r/\sqrt\tau)|^2
 |F(4\tau\sin^2(\pi r/(2\sqrt\tau)))|^2\,dr
\]

and the constant

\[
 C_F^2=\int_0^\infty|F(\pi^2r^2)|^2\,dr
 =\frac1{2\pi}\int_0^\infty|F(s)|^2s^{-1/2}\,ds
\]

are normalized correctly.

### 2.5 Carrier rate

Abel summation gives

\[
 \sup_M\left|\sum_{\ell=1}^Me^{2\pi i\ell y}\right|
 \leq |\sin(\pi y)|^{-1}\lesssim d^{-1}.
\]

After the \(\sqrt t\)-spaced rescaling, this is precisely the
\(O(\sqrt t/d)\) carrier error.  Consequently the condition
\(d/\sqrt t\to\infty\) is sharp for the interior constant; at
\(d/\sqrt t\to\kappa<\infty\) the displayed boundary profile replaces it.

## 3. Corrections identified in the lattice memo

### R1. Normalize the continuum source, or redefine its recovery

Section 2 assumes only \(\int\phi=0\), then independently normalizes
\(\phi_h\), while \(F\) is defined from the unqualified continuum \(\phi\).
As written this permits, for example, replacing \(\phi\) by \(2\phi\) while
leaving its normalized grid recovery unchanged; the claimed limit then has
the wrong constant.  Require

\[
 \|\phi\|_{L^2}=1,
 \qquad \|\phi_h-\phi\|_h=O(h)
\]

for the declared midpoint/mean-corrected recovery (or omit discrete
renormalization and state the actual convergent normalization).  The
constants \(F\), \(C_F\), and all asymptotic equivalences must use that same
limit source.

**Disposition:** repaired in the canonical memo.

### R2. Supply the missing proof of the \(F\equiv0\) rate

Lemma 4.2 as stated gives only

\[
 |a-F|\lesssim\min\{\sqrt t+h,se^{-v_-s}\}.
\]

Squaring and integrating this displayed bound does **not** by itself yield
Section 9's uniform \(O(t+h^2)\) estimate; a slowly growing crossover factor
is left if one uses only the uniform \(\sqrt t+h\) bound.  The claimed rate
is recoverable, but the proof must retain the decay discarded in Lemma 4.2.
The same energy calculation gives

\[
 \|e^{-(tA_h+sV_h)}\phi_h-e^{-sV_h}\phi_h\|_h
 \lesssim \sqrt{\frac{t}{1+s}},
\]

because

\[
 \int_0^1 e^{-2rsv_-}(1+rs)^2\,dr\lesssim(1+s)^{-1}.
\]

When \(F\equiv0\), midpoint quadrature gives

\[
 |\langle1,e^{-sV_h}\phi_h\rangle_h|
 \lesssim h(1+s)e^{-v_-s}.
\]

Summing these squared bounds on the \(\sqrt t\)-spaced modal lattice proves
\(\sqrt t\mathcal N_h^2\lesssim t+h^2\).  Section 9 should include this
argument or weaken its rate to the convergence already established by
Theorem 7.1.

**Disposition:** repaired.  The weighted estimate was added and the
accumulation lemma explicitly includes \(G(s)=(1+s)^{-1}\); the comparison
\(s_{\ell,h}\ge4(\ell\sqrt t)^2\) proves the required bound.

### R3. State the domain of every quantitative estimate

The asymptotic theorem is correct, but (7.3) is phrased as though it held for
all \(t,\tau,d_h>0\).  State explicitly, as in Theorem 5.2, that the uniform
bound is for \(\tau\geq1\), \(0<t\leq t_*\), and sufficiently fine grids,
with constants depending on the fixed source/modulation regularity.  If
\(d_h\) is allowed to vary, use the explicit \(\sqrt t/d_h\) term and do not
also hide dependence on a fixed interior distance in the constant.

**Disposition:** repaired in the canonical memo.

### R4. Make the accumulation lemma explicit

The sentence “the total error is \(O(\sqrt t+h)\), not the number of modes
times that quantity” is right but currently compresses a substantive
argument.  Record a uniform sum lemma of the form

\[
 \sqrt t\sum_{\ell=1}^{n-1}
 G\!\left(4\tau\sin^2\frac{\pi\ell}{2n}\right)\leq C_G
\]

for the finite collection of exponentially decaying envelopes used in the
proof, together with the bounded-variation Riemann error.  This closes the
only place where a reader might incorrectly multiply a per-mode estimate by
\(n\).

**Disposition:** repaired.  The envelope-accumulation lemma, including its
\((1+s)^{-1}\) case, now covers every use in the memo.

### R5. Qualify finite-grid evidence and relative statements

The norm comparison (5.5) is legitimate only after its displayed error tends
to zero and because \(F\not\equiv0\) supplies a uniform lower bound for
\(\sqrt\tau\Psi_Q^2\) on \([1,\infty)\).  Keep that condition adjacent to
the formula.  The fixed-\(K\) norm improvement likewise applies for small
enough \(h+\delta_h\), after the finite norm is known to inherit the lower
bound.  No relative statement is valid at \(F\equiv0\).

**Disposition:** repaired in the canonical synthesis.

## 4. Counterexamples that the final synthesis must retain

1. **Normalization mismatch:** continuum scaling of \(\phi\) with an
   independently normalized \(\phi_h\) changes \(C_F\) but not the finite
   response.
2. **Unresolved mesh diffusion:** \(t/h^2\to\tau_0<\infty\) retains
   \(4\sin^2(\theta/2)\) and the subcell profile; it does not give the
   continuum atomic constant.
3. **Boundary approach:** \(d_h=O(\sqrt t)\) retains the carrier harmonic;
   an endpoint atom has twice the interior squared constant.
4. **Macroscopic preparation at the diffusion scale:** if
   \(\sigma_h^2/t\not\to0\), the limiting characteristic function survives.
5. **Null high-frequency profile:** \(F\equiv0\) forbids division by
   \(C_F\), even though mixed diffusion--multiplication terms need not vanish.
6. **Placement-blind finite-cell chart:** an atom and a half/half split have
   different \(|B_Q|^2\) at finite \(\tau\); bare \(\varepsilon/h=O(1)\)
   does not select a unique phase.

## 5. Executable controls

The following existing Stage VIII tests materially audit the proof rather
than merely reproduce plots:

- dense Kronecker evolution versus the separated modal formula;
- full-norm normalization under Euclidean versus density conventions;
- atom/split placement counterexample;
- finite lattice phase versus the invalid unresolved continuum phase;
- inverse-\(\tau\) lattice-to-continuum tail rate;
- exact null and reflection-symmetry controls; and
- balanced and joint-atomic squared-error residuals.

The boundary-factor spot check in Section 2.2 is implemented in
`test_oig_viii_adversarial_controls.py`.  It tests monotone approach along a
joint path and deliberately labels its tolerances as regression evidence,
not proof of the theorem.

## 6. Provisional publication boundary

After the recorded repairs, it is defensible to state that Stage VIII promotes the iterated
finite-cell/large-\(\tau\) argument to a simultaneous atomic theorem in the
declared model.  It is not defensible to advertise a relative theorem at a
null port, a phase-free theorem at finite \(\tau\), or a universal physical
claim beyond this reversible path system.

## 7. Resolved-regime audit

### 7.1 Checks that passed

#### Weak Duhamel normalization

In Lemma 3.2, setting \(s=t\mu\), \(d=1/\mu\), and
\(B=dA_h+V_h\) gives \(sB=t(A_h+\mu V_h)\) exactly.  Form Duhamel and
discrete integration by parts produce

\[
 -d\int_0^s
 \langle D_he^{-(s-r)B}1,D_h(e^{-rV_h}\phi_{k,h})\rangle_{h,e}\,dr.
\]

The first gradient is
\(O((s-r)e^{-v_-(s-r)})\), the second is
\(O((1+r)e^{-v_-r})\), and the edge measure is below one.  Therefore

\[
 |a_{\ell k,h}-F_{k,h}(s)|
 \lesssim d s^2(1+s)e^{-cs}
 =t s(1+s)e^{-cs}.
\]

There is no missing \(h\), \(\mu\), or \(s\) factor.  This scalar weak
estimate legitimately improves the canonical balanced source error to
\(O(\varepsilon^2)\).

#### Conservative cell transform

The exact cell masses are midpoint samples of the box convolution
\(\rho_\varepsilon*h^{-1}\mathbf1_{[-h/2,h/2]}\).  Its zero Poisson alias is

\[
 e^{i\xi y_0}\widehat\eta(\varepsilon\xi)
 \operatorname{sinc}(h\xi/2),
\]

so Lemma 4.1 has the correct phase and box multiplier.  On
\(0\le h\xi\le\pi\), every nonzero alias samples \(\widehat\eta\) at
frequency of magnitude at least \(\pi\varepsilon/h\); Schwartz decay gives
\(O((h/\varepsilon)^M)\).  Compact support away from the physical endpoints
justifies the infinite-lattice extension.

#### Balanced chart

For \(q\) bounded above and away from zero, the four relative error sources
have the stated scales:

\[
 \text{weak source}=O(t)=O(\varepsilon^2),\quad
 \text{source quadrature}=O(h^2),\quad
 \text{box/dispersion}=O((h/\varepsilon)^2),
\]

with a superalgebraic phase-sum and interior-carrier error.  Since
\(\varepsilon<1\) in the declared compactly supported preparation,
\(h^2\) is safely absorbed by \((h/\varepsilon)^2\).  Positivity of the
canonical \(\mathcal P_k\) makes the relative norm form legitimate.

#### Late quantization and atomic endpoint

Lemma 6.1's rate is correct.  Put

\[
 A=Q_h(Y)-Q_h(Y'),\qquad B=Y-Y'.
\]

Then \(|A-B|\le h\),
\(\mathbb E|A+B|\lesssim\varepsilon+h\), and

\[
 |\cos(\xi A)-\cos(\xi B)|
 \leq\tfrac12\xi^2|A^2-B^2|.
\]

Taking expectations gives
\(C\xi^2(h^2+h\varepsilon)\).  On the active heat band
\(\xi=O(t^{-1/2})\), this is
\(O((h^2+h\varepsilon)/t)\).  Dispersion contributes \(h^2/t\), the weak
source comparison contributes \(t\), and the continuum mollifier tail
contributes \(\varepsilon^2/t\).  Thus

\[
 |\sqrt t\,\mathcal N_{h,k}^2-C_{F,k}^2|
 \lesssim t+(h^2+\varepsilon^2)/t
\]

has the correct normalization and error scales.

#### Critical constants and first correction

The critical balance

\[
 2r(1-\alpha)-\alpha/2=0
\]

gives \(\alpha=4r/(4r+1)\).  The displayed ramp constants agree with
\(m_{1,k}=-2\sqrt2g/(k\pi)^2\) for odd \(k\) and
\(m_{2,k}=2\sqrt2g^2/(k\pi)^2\) for even \(k\), including the factor
\(1/r!\).  Parseval also confirms

\[
 \frac{\mathcal P(q)}{|a_r|\sqrt{J_{2r}}q^r}
 =1+\frac{a_{r+1}}{a_r}\frac{J_{2r+1}}{J_{2r}}q+O(q^2).
\]

For a standard Gaussian,
\(J_{2r+1}/J_{2r}=2r+1/2\), yielding the stated coefficients \(-3.5\)
and \(-6.3\) when \(g=0.8\).  The executable endpoint-correction tests
recover first- and second-order residual slopes as claimed.

### 7.2 Ultra-early repair: audited and validated

The original last paragraph of Theorem 5.1 left a proof gap when
\(q<(h/\varepsilon)^4\).  The revised memo now inserts the needed uniform
lemma.  With \(T=tA_h\), \(s=t\mu_{\ell,h}\), and
\(f(z)=\langle1,e^{-(T+zV_h)}\phi_{k,h}\rangle_h\), one has
\(\|T\|\le4\tau\) and \(0\le s\le4\tau\).  Dyson differentiation gives
the following bound:

\[
 \left|
 a_{\ell k,h}(t)-\frac{(-t\mu_{\ell,h})^r}{r!}m_{r,k,h}
 \right|
 \leq Cs^r\tau,
 \tag{7.1}
\]

uniformly in \(1\le\ell<n\).  Specifically, odd modes have
\(f'(0)=-m_{1,k,h}\int_0^1e^{-ut\lambda_{k,h}}du
=-m_{1,k,h}[1+O(t)]\); midpoint reflection makes \(f'(0)=0\) exactly for
even modes; and \(f''(0)/2=m_{2,k,h}/2+O(\tau)\).  The next Taylor term is
\(O(s^{r+1})=O(s^r\tau)\).  The revised proof also establishes the
conservative spectral identity

\[
 \varepsilon^{4r+1}
 \sum_{\ell=1}^{n-1}|\beta_{\ell,h}|^2\mu_{\ell,h}^{2r}
 =J_{2r}\,[1+O((h/\varepsilon)^2)]
 \tag{7.2}
\]

by the zero Poisson alias, symbol expansion, carrier averaging, and
Plancherel.  Since
\(\tau=q/(h/\varepsilon)^2<(h/\varepsilon)^2\), (7.1)--(7.2) give the
claimed relative \(O((h/\varepsilon)^2)\) ultra-early error.  The powers of
\(s,\tau,\varepsilon\), and the factor \(1/r!\) all check.  This closes the
all-\(q\) theorem; no additional lower relation between \(q\) and
\(h/\varepsilon\) is needed for the ramp/cosine pair.

### 7.3 Two-copy coupling repair

The original sentence “apply the second-order Taylor bound to” the two
variables separately only gives the weaker sum of their second moments,
which contains an unwanted \(O(\varepsilon^2)\) term.  The sharper
\(h^2+h\varepsilon\) rate follows from the coupled
\(|A^2-B^2|\) argument above.  The revised memo now contains that coupled
argument, so the theorem need not be weakened.

### 7.4 Smaller repairs

1. The theorem class is \(\eta\in C_c^\infty\), whereas Section 8 uses the
   standard Gaussian.  State the correction as a Schwartz-class extension,
   or broaden the preparation hypothesis and separately control its
   exponentially small physical-boundary tail.  **Repaired:** the revised
   memo states the normalized Schwartz extension and its boundary-tail term.
2. The “single resolution condition”
   \(h/\max\{\varepsilon,\sqrt t\}\to0\) is only the mesh-resolution part of
   the theorem.  By itself it does not force an initial-layer limit: the
   small-scale, fixed-interior, conservative-preparation, and (for cancelled
   general ports) discrete-moment hypotheses remain necessary.  **Repaired:**
   the revised summary makes this qualification explicit.
3. In the boundary warning, use
   \(\operatorname{dist}(y_0,\{0,1\})\), not only \(y_0\), to cover the right
   reflector.  **Repaired** in the revised memo.
4. The phrase “discrete \(2r\)-th target difference of conservative
   mollifier masses” should specify the density \(q_h/h\) and its weighted
   discrete norm; otherwise a reader can insert an erroneous power of \(h\)
   into (7.2).  **Repaired:** the revised proof replaces that phrase with the
   explicitly normalized spectral identity (7.2).

### 7.5 Counterexample verification

The general-modulation obstruction in Section 9.1 is correct.  For

\[
 p(x)=x^4-(2-3/\pi^2)x^2
\]

one has \(\int_0^1p(x)\cos(2\pi x)\,dx=0\), while midpoint
Euler--Maclaurin gives

\[
 h\sum_i p(x_i)\cos(2\pi x_i)
 =-h^2/(4\pi^2)+O(h^4).
\]

Along \(\varepsilon=h^{1/2}\), \(q=h^3\), the grid is spatially resolved
but \(|m_{1,h}|/q\asymp h^{-1}\).  This decisively rules out extending the
canonical even-port early theorem to a general modulation without exact
moment preservation or a quantitative condition on \(m_{1,h}\).
