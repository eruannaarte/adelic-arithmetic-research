# A weighted approximation transfer for slow sinusoidal drift

All statements concern the same 8,900 complex readings and positive physical
weights as the completed arithmetic experiment. This is a sufficient guarantee
within a declared model, not a claim that a fitted residual identifies the
physical drift family or that the approximation is optimal.

## 1. Physical norm and the family

Let

\[
t_j=(2j+1-8900)/10,\quad x_j=t_j/890=(2j+1-8900)/8900,
\qquad 0\leq j<8900.
\]

For either the outer or multiscale design, use its unchanged physical weights
\(w_j>0\), with \(\sum_jw_j=1\), and write
\(\|v\|_W^2=\sum_jw_j|v_j|^2\).
The window formula is

\[
w_j^{(m)}=\frac{1+2\sum_{k=1}^8c_k
 \cos(k(2j+1)\pi/m)}{m}.
\]

The \(c_k\) are the exact binary rational coefficients in the original
`arithmetic_sensing_iv.py`. The outer window has \(m=8900\). The multiscale
window adds the \(m=2550\) window at indices 3175 through 5724, with coefficient
\(125/65536\), and multiplies the outer window by its complementary coefficient.
No extra readings are introduced. The two windows act on shared readings.

Discrete Fourier summation gives mass one, since \(1\leq k\leq8<m\).
Also \(w_j=w_{8899-j}\) exactly: reflection changes each cosine argument from
\(k\theta\) to \(2\pi k-k\theta\), and the inner window is centered exactly.
The consumer checks positivity at every node by outward arithmetic. Thus any
odd vector sampled from an odd function is W-orthogonal to any even vector.

Assume the nonpolynomial drift has the form

\[
g(x)=A\sin(\omega x+\phi),\qquad |A|\leq B,
\quad |\omega|\leq\Omega\leq1,\quad \phi\in\mathbb R.
\]

An arbitrary polynomial of degree at most eight is allowed in addition.
Here \(\omega\) is frequency in the normalized coordinate \(x=t/890\):
\(\Omega=1\) permits at most approximately two radians of phase change across
the full observation window. This is a slow drift family. The bounds below are
uniform over its whole frequency interval and every phase, not a frequency grid.

## 2. Rational approximation certificate

For each \(k=9,\ldots,20\), the certificate supplies a fixed rational polynomial
\(q_k\) of degree at most eight and of the same parity as \(k\). It supplies
positive rational numbers \(d_k,m_9,m_{21},m_{22}\) satisfying

\[
\|x^k-q_k(x)\|_W\leq d_k,
\qquad \|x^r\|_W\leq m_r\quad(r=9,21,22).
\]

These are finite, directly verifiable inequalities for the actual physical
weights. The producer proposes \(q_k\) by weighted projection and rounds its
coefficients to forty decimal places, enforcing parity exactly. The proof does
not require the proposed polynomials to be exact projections or optimal.

For verification, evaluate every residual at all 8,900 nodes and sum its
weighted square using Arb intervals. The consumer uses direct powers instead
of the producer's Horner evaluation and reconstructs the original weights from
their defining source coefficients. It proves an upper endpoint of the squared
norm is at most the square of the declared rational upper bound. It never
subtracts a fitted norm from a nearly equal original norm. An independent review
also verifies the norms with 320-bit interval moment quadratic forms; outward
arithmetic controls the cancellation in that separate method.

## 3. Uniform phase and frequency theorem

Define the rational functions

\[
\begin{aligned}
R_o(\Omega)&=\sum_{k=9,11,\ldots,19}
 \frac{d_k\Omega^k}{k!}+\frac{m_{21}\Omega^{21}}{21!},\\
R_e(\Omega)&=\sum_{k=10,12,\ldots,20}
 \frac{d_k\Omega^k}{k!}+\frac{m_{22}\Omega^{22}}{22!},\\
K_W(\Omega)&=\max\{R_o(\Omega),R_e(\Omega)\}.
\end{aligned}
\]

**Theorem.** Every drift in the declared family admits a polynomial \(p\) of
degree at most eight such that

\[
\|g-p\|_W\leq B K_W(\Omega).
\]

**Proof.** Expand \(\sin(\omega x)\) through degree twenty, whose last nonzero
term has degree nineteen. Replace each power \(x^k\) of degree greater than
eight by \(q_k(x)\). Taylor's theorem, applied through degree twenty, bounds the
remaining sine error pointwise by
\(|\omega x|^{21}/21!\). The triangle inequality in W gives an odd residual
\(r_o\) with \(\|r_o\|_W\leq R_o(\Omega)\). Likewise, expand cosine through
degree twenty-one, whose last nonzero term has degree twenty, and replace the
higher powers by \(q_k\). Its complete remainder is bounded by
\(|\omega x|^{22}/22!\), giving an even residual
\(\|r_e\|_W\leq R_e(\Omega)\). These are full Taylor remainders, not truncated
infinite sums left without a bound.

Use
\(\sin(\omega x+\phi)=\cos\phi\sin(\omega x)+\sin\phi\cos(\omega x)\).
The corresponding polynomial is a linear combination of the two degree-eight
polynomials just constructed. Exact parity and exact even weighting give

\[
\|\cos\phi\,r_o+\sin\phi\,r_e\|_W^2
 =\cos^2\phi\|r_o\|_W^2+\sin^2\phi\|r_e\|_W^2
 \leq K_W(\Omega)^2.
\]

Multiplication by \(|A|\leq B\) proves the result. □

The proof's orthogonality step is essential for the maximum rather than the
sum. An asymmetric physical weighting would require a new cross-term bound or
a more conservative triangle bound. The certificate does not silently cover
such a change.

For comparison, direct degree-eight Taylor approximation at zero gives the
pointwise bound \(B\Omega^9/9!\), and weighting that same remainder gives
\(B\Omega^9m_9/9!\). Both are valid for arbitrary phase. The new theorem improves
the polynomial itself as well as measuring its error in the physical norm.
For \(0\leq\Omega\leq1\), all powers in \(R_o\) are at least nine and all
powers in \(R_e\) at least ten, so
\(K_W(\Omega)\leq\Omega^9K_W(1)\). This states an explicit amplitude-frequency
tradeoff without identifying frequency from the observations.

## 4. Transfer into the complete arithmetic inverse

The defining observation model is

\[
y_j=\sum_{n\geq1}a(n)n^{-2-it_j}+\beta(x_j)+g(x_j)+e_j,
\]

where \(a(1)=1\), \(a(n)\) are integers in \([0,d_{14}(n)]\),
\(\deg\beta\leq8\) with arbitrary complex coefficients, and
\(\|e\|_W\leq\eta\). The target is \(a(2),\ldots,a(50)\).
The complete tail still uses the unchanged midpoint correction and its complete
infinite-tail coefficient bounds \(A_n\). The digital correction allowance is
\(\Xi=10^{-20}\). No arithmetic tail is replaced by the synthetic fixture's
finite support in the recovery verifier.

By the theorem, \(g=p+r\) with \(\|r\|_W\leq\nu:=BK_W(\Omega)\).
The existing augmented polynomial columns absorb \(p\) exactly at the
mathematical level, since \(\beta+p\) is still degree at most eight. No explicit
subtraction of \(p\), no new measurements, and no bound on its coefficients
are needed. This is the bounded-approximation clause of the unchanged transfer
theorem; it does not turn approximate nuisance annihilation into an exact claim.

Let \(X\) be the actual 58-column augmented matrix, \(H=X^*WX\), and let the
unchanged complete certificate give \(H\succeq fI\), \(f>0\). For an exact
rational numerical proposal \(\widehat\theta\), the operational verifier
reconstructs the physical matrix and all readings and establishes

\[
\|H\widehat\theta-X^*W(y-\widetilde u)\|_2\leq\rho.
\]

Thus its error relative to the exact least-squares solution is at most
\(\rho/f\). Weighted sensor and remainder errors have augmented inverse gain
at most \(1/\sqrt f\); the complete tail has its separately certified bound.
Therefore each unknown integer satisfies

\[
|n^2\widehat\theta_n-a(n)|
 \leq A_n+n^2\left(\frac{\eta+BK_W(\Omega)+\Xi}{\sqrt f}
                         +\frac{\rho}{f}\right).
\]

Strictly less than \(1/2\) implies unique integer rounding. The exact rational
consumer tests the equivalent sufficient gate

\[
M_n:=\tfrac12-A_n-n^2\rho/f>0,
\qquad n^4(\eta+BK_W(\Omega)+\Xi)^2<M_n^2f.
\]

The noise terms share the same readings and are added before applying the gain;
no independence assumption is used. A tiny normal residual proves only that the
augmented numerical solve was accurate. It cannot establish the family bound,
sensor radius, or arithmetic source promise. The actual data demonstration
checks its synthetic family membership and noise construction independently.

## 5. Demonstrated consequence and limits

The provided exact digital fixture has the valid finite integer-envelope source
specified in `data.json`, includes nonzero omitted coefficients at 51, 60 and 72,
an unrestricted degree-eight complex polynomial with scale \(10^{20}\),
\(g(x)=20000\sin(x+1/3)\), and sensor perturbation
\((39/10^6)e^{it/11}\). Arb verifies digitization error below \(10^{-35}\),
which together with the sensor perturbation is below \(\eta=4\cdot10^{-5}\)
in either physical norm. The inverse sees all 8,900 exact readings but no target
answer. Both designs recover all 49 unknown integers, using the original
complete infinite-tail guarantees and separately verified normal residuals.

These are model-derived certificates, not experimental calibration, statistical
superiority, number-field realizability, optimal polynomial approximation, or a
sharp maximal drift amplitude. Family membership and the amplitude-frequency
bound remain inputs that a physical application must justify.
