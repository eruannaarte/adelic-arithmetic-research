# Operational Information Geometry XII

## The two-port finite-Neumann transfer theorem

- **Research status:** analytic theorem, outward-rounded certificate, and
  independent falsification audit; not peer reviewed
- **Research, theorem development, computation, and writing:** Codex (OpenAI)
- **Originating direction and research environment:** TGN's human founder
- **Predecessor:** Operational Information Geometry XI
- **Scope:** the declared one-way parabolic path model; not a physical theory

## Abstract

Stage XI transferred one observable source direction from a continuum
response Gram to the complete finite Neumann dynamics.  Stage XII completes
the same bridge for two source directions at the one-cell lattice point
\(\tau=1\).

The result is metric dependent.  On the exactly centred odd-grid sequence,
the inherited Stage X late-core transfer inequality has the rigorous adjacent
local brackets

\[
 \begin{array}{c|c|c}
 \text{source metric}&\text{predecessor rejected}&\text{finite transfer proved}\\
 \hline
 L^2&n=343&n=345,\\
 \text{declared continuum }H^1&n=647&n=649.
 \end{array}
 \tag{A.1}
\]

At the successful grids, the complete finite Grams inherit the
direction-safe lower floors

\[
 \boxed{
 \lambda_{\min}(G_{345}^{\rm full})
 >9.19093\times10^{-10},}
 \tag{A.2}
\]

and

\[
 \boxed{
 \lambda_{\min}(G_{649}^{\rm full},S_{H^1})
 >5.24653\times10^{-12}.}
 \tag{A.3}
\]

Every noncommuting diffusion--modulation word is retained.  Each finite
matrix exponential is enclosed by a degree-32 centred Taylor action in Arb,
with the exact operator tail

\[
 R_{32}=\frac{(18/5)^{33}}{33!}.
\]

The closed symmetric \(2\times2\) formula supplies the sharp spectral bound
used here; safe row-sum bounds are too coarse at both successful grids.  Fixed
integer Rayleigh vectors prove that the true error norm exceeds the transfer
budget at the two predecessors.

The finite thresholds also admit a sharp analytic explanation.  Along the
exactly centred odd grids,

\[
 \boxed{
 G_n^{\rm full}-G=\frac{E}{n^2}+O(n^{-3}),}
 \tag{A.4}
\]

where \(E\) is an explicit mixed diffusion--modulation integral.  Its
\(L^2\) norm is approximately \(0.0169372548\); its continuum-\(H^1\)
whitened norm is approximately \(0.00149431067\).  Dividing these constants
by the Stage X continuum floors predicts thresholds \(343.97\) and
\(648.58\), matching (A.1).

The predecessor results reject this particular sufficient transfer
inequality; they do not imply that the finite Grams are singular.  The
brackets are local and adjacent, not proofs of the globally smallest
successful odd grids.  Nothing here is uniform in \(\tau\), covers the full
atlas, or changes the declared physical scope of the toy model.

## 1. From a coarse landmark to a sharp bracket

Stage XI sampled the two-port full-model error at

\[
 n=31,63,127,255,383,511.
\]

The first sampled value below the \(L^2\) continuum floor was \(n=383\).
That was useful evidence, not a minimality theorem.  Refinement on the odd
subsequence places the local crossing between \(343\) and \(345\).

The distinction matters because the target cell is exactly centred only
when \(n\) is odd.  On even grids the old single-cell convention places the
target at

\[
 \frac12-\frac1{2n},
\]

which defines a displaced-target experiment with a different carrier phase.
Even and odd values cannot be interleaved without a target-transport theorem.

The Stage XII computation proves:

\[
 \begin{aligned}
 \delta^{L^2}_2(343)
 &>1.43889721110\times10^{-7}
 >L^{L^2}_2,\\
 \delta^{L^2}_2(345)
 &<1.42232872024\times10^{-7}
 <L^{L^2}_2,
 \end{aligned}
 \tag{1.1}
\]

where the exact Stage X floor satisfies

\[
 L^{L^2}_2>1.4315196512138325\times10^{-7}.
 \tag{1.2}
\]

For the separately declared continuum-\(H^1\) cost,

\[
 \begin{aligned}
 \delta^{H^1}_2(647)
 &>3.56901705913\times10^{-9}
 >L^{H^1}_2,\\
 \delta^{H^1}_2(649)
 &<3.54706348693\times10^{-9}
 <L^{H^1}_2,
 \end{aligned}
 \tag{1.3}
\]

with the direction-safe floor

\[
 L^{H^1}_2>3.5523100221039934\times10^{-9}.
 \tag{1.4}
\]

All four decisions use exact rational floors and outward Arb endpoints.  The
printed decimals are explanatory, never the objects compared by the checker.

## 2. The exact finite response

Let \(n\) be odd, \(h=1/n\), and

\[
 x_j=\frac{j+1/2}{n},\qquad0\le j<n.
\]

Let \(L_n\) be the unscaled reflecting path Laplacian and let \(V_n\) be the
diagonal multiplication matrix with

\[
 (V_n)_{jj}=1+\frac45x_j,
 \qquad
 \omega_{n,\ell}=4\sin^2\frac{\pi\ell}{2n}.
 \tag{2.1}
\]

The two Euclidean-orthonormal source ports are

\[
 u_{n,k}(j)=\sqrt{\frac2n}\cos(k\pi x_j),
 \qquad k=1,2.
 \tag{2.2}
\]

For target mode \(\ell\), define

\[
 A_{n,\ell}=L_n+\omega_{n,\ell}V_n,
 \qquad
 a_{n,\ell k}
 =\mathbf1^Te^{-A_{n,\ell}}u_{n,k}.
 \tag{2.3}
\]

The centre cell has \(x_{(n-1)/2}=1/2\).  Its target-DCT coefficient obeys
the exact parity identities

\[
 \beta_{n,\ell}=0\quad(\ell\text{ odd}),
 \qquad
 \beta_{n,\ell}^2=\frac2n
 \quad(\ell\text{ even and nonzero}).
 \tag{2.4}
\]

At \(\ell=0\), \(\beta_{n,0}^2=1/n\), but the response vanishes exactly
because the nonconstant source ports have zero mass and the Neumann semigroup
preserves the constant left vector.

Consequently the complete finite Gram is

\[
 \boxed{
 G_{n,ij}^{\rm full}
 =\frac{2\sqrt2}{n^2}
 \sum_{\substack{2\le\ell<n\\\ell\ \mathrm{even}}}
 a_{n,\ell i}a_{n,\ell j}.}
 \tag{2.5}
\]

Equation (2.5) is not the multiplication-phase surrogate.  The exponential
contains the actual sum \(L_n+\omega V_n\), so it contains every ordered
diffusion--modulation word.

The continuum comparison uses

\[
 F_k(\omega)
 =\int_0^1e^{-\omega(1+4x/5)}\sqrt2\cos(k\pi x)\,dx
 \tag{2.6}
\]

and

\[
 \boxed{
 G=\sqrt2\int_0^1
 F(\omega(\xi))F(\omega(\xi))^T\,d\xi,
 \qquad
 \omega(\xi)=4\sin^2\frac{\pi\xi}{2}.}
 \tag{2.7}
\]

The source costs are

\[
 S_{L^2}=I,
 \qquad
 S_{H^1}=\operatorname{diag}(1+\pi^2,1+4\pi^2).
 \tag{2.8}
\]

The second statement assigns the continuum cost (2.8) to the finite
coefficients as well.  It is not a result for the distinct natural discrete
energy \(1+n^2\omega_{n,k}\).

## 3. The sharp second-order response law

Normalize the modal amplitude by

\[
 b_{n,k}(\omega)=\frac1{\sqrt n}
 \mathbf1^Te^{-(L_n+\omega V_n)}u_{n,k}.
\]

Uniformly for \(0\le\omega\le4\),

\[
 \boxed{
 b_{n,k}(\omega)=F_k(\omega)+h^2D_k(\omega)+O(h^3).}
 \tag{3.1}
\]

Write \(g=4/5\) and

\[
 B_k(\omega)
 =\sqrt2\left[(-1)^ke^{-(1+g)\omega}-e^{-\omega}\right].
\]

Then

\[
 \boxed{
 D_k(\omega)
 =\frac{13}{24}\omega gB_k(\omega)
 +\frac13\omega^2g^2F_k(\omega).}
 \tag{3.2}
\]

The coefficient has two parts.  Composite midpoint Euler--Maclaurin gives

\[
 D_k^{\rm mid}=\frac{\omega g}{24}B_k(\omega).
\]

The first weak Duhamel insertion gives

\[
 D_k^{\rm dyn}
 =-\int_0^1\!\int_0^1
 \partial_x(e^{-(1-s)\omega V})
 \partial_x(e^{-s\omega V}\phi_k)\,dx\,ds
 \tag{3.3}
\]

and therefore

\[
 D_k^{\rm dyn}
 =\frac{\omega g}{2}B_k(\omega)
 +\frac{\omega^2g^2}{3}F_k(\omega).
\]

Adding the two terms yields (3.2).  This is already a mixed
diffusion--modulation coefficient, not a multiplication-moment fit.

The proof does not claim \(\|L_n\|=O(h^2)\); in fact \(\|L_n\|\le4\).
Instead, discrete summation by parts gives, for uniformly smooth midpoint
samples,

\[
 \langle p_h,L_nq_h\rangle_h
 =h^2\int_0^1p'q'\,dx+O(h^3).
 \tag{3.4}
\]

In the norm-convergent Dyson series around \(\omega V_n\), the two outer
Laplacians in every term of order at least two act on smooth endpoints.  Each
has \(h\)-norm \(O(h^{3/2})\); the middle Laplacians have norm at most four,
and the simplex factor \(1/r!\) makes their sum \(O(h^3)\), uniformly in
\(\omega\).  This proves the remainder in (3.1).

## 4. The matrix coefficient and threshold prediction

Put

\[
 \boxed{
 E=\sqrt2\int_0^1
 \left[F(\omega(\xi))D(\omega(\xi))^T
 +D(\omega(\xi))F(\omega(\xi))^T\right]d\xi.}
 \tag{4.1}
\]

The exact-centre target-mode quadrature contributes no \(n^{-2}\) term.
Indeed, its step is \(d=2/n\); it is the midpoint rule on \([d/2,1]\).
For \(H_{ij}=F_iF_j\),

\[
 H'_{ij}(1)=0,
 \qquad H'_{ij}(d/2)=O(d^3),
 \qquad\int_0^{d/2}H_{ij}=O(d^5).
\]

Thus its error is \(O(d^4)\).  Combining this with (3.1) proves (A.4).

High-precision evaluation of the explicit coefficient gives

\[
 E\approx
 \begin{pmatrix}
 -0.01598629511482710915&-0.003908677177631584465\\
 -0.003908677177631584465&-0.000871634196112061576
 \end{pmatrix}.
 \tag{4.2}
\]

Its eigenvalues are approximately

\[
 -0.01693725478632848846,
 \qquad
 0.0000793254753893177344.
\]

Hence

\[
 \|E\|_2\approx0.01693725478632848846,
 \tag{4.3}
\]

while

\[
 \|S_{H^1}^{-1/2}ES_{H^1}^{-1/2}\|_2
 \approx0.001494310669433565307.
 \tag{4.4}
\]

The resulting asymptotic threshold predictions are

\[
 \sqrt{\frac{\|E\|_2}{L_2^{L^2}}}\approx343.9718,
 \qquad
 \sqrt{
 \frac{\|S_{H^1}^{-1/2}ES_{H^1}^{-1/2}\|_2}{L_2^{H^1}}}
 \approx648.5822.
 \tag{4.5}
\]

These values explain the certificate, but do not decide it.  The finite
margin at \(n=345\) is too narrow for a generic asymptotic remainder
constant; the proof needs a direct enclosure of the complete generator.

## 5. The centred-Taylor enclosure

For every target mode,

\[
 0\preceq L_n\preceq4I,
 \qquad
 I\preceq V_n\preceq\frac95I,
 \qquad
 0\le\omega\le4.
\]

Centre the generator at

\[
 c(\omega)=2+\frac75\omega,
 \qquad
 B_{n,\ell}=A_{n,\ell}-c(\omega_{n,\ell})I.
\]

Define

\[
 \rho(\omega)=2+\frac25\omega.
\]

Then

\[
 \|B_{n,\ell}\|_2
 \le\rho(\omega_{n,\ell})
 \le\frac{18}{5}.
 \tag{5.1}
\]

For the current mode, set \(\omega=\omega_{n,\ell}\).  For degree \(m\),
the spectral theorem and Taylor remainder give

\[
 \begin{aligned}
 \left\|e^{-A_{n,\ell}}
 -e^{-c(\omega)}\sum_{r=0}^m\frac{(-B_{n,\ell})^r}{r!}\right\|_2
 &\le e^{-c(\omega)}e^{\rho(\omega)}
 \frac{\rho(\omega)^{m+1}}{(m+1)!}\\
 &=e^{-\omega}\frac{\rho(\omega)^{m+1}}{(m+1)!}\\
 &\le\frac{(18/5)^{m+1}}{(m+1)!}.
 \end{aligned}
 \tag{5.2}
\]

At \(m=32\),

\[
 R_{32}=\frac{(18/5)^{33}}{33!}
 \approx2.62601279829614\times10^{-19}.
 \tag{5.3}
\]

The normalized amplitude error is at most \(R_{32}\).  The induced two-port
Gram tail is below \(1.486\times10^{-18}\), many orders beneath the transfer
margins.  The implementation evaluates every tridiagonal polynomial action
in Arb.  Powers through degree 32 contain every mixed word of those lengths;
(5.2) encloses the complete remaining series.

## 6. Exact metric-relative decisions

For either source metric, form

\[
 \Delta_n=S^{-1/2}(G_n^{\rm full}-G)S^{-1/2}
 =\begin{pmatrix}a&b\\b&d\end{pmatrix}.
\]

The eigenvalues are

\[
 \lambda_\pm
 =\frac{a+d\pm\sqrt{(a-d)^2+4b^2}}2.
 \tag{6.1}
\]

Arb evaluates (6.1) directly and takes outward absolute endpoints.  This is
materially sharper than the maximum absolute row sum.

For the predecessor grids, fixed Rayleigh vectors give rigorous lower
bounds:

\[
 v_{L^2}=(4,1),
 \qquad
 v_{H^1}=(8,1).
 \tag{6.2}
\]

Their directed quotients lie above the respective Stage X floors.  Thus the
predecessor statements concern the true spectral error, not the failure of a
coarse upper bound.

Let \(U_\infty(n)\) be the outward absolute-row-sum upper bound.  At the
successful points,

\[
 \|\Delta_{345}\|_\infty
 \le U_\infty(345)\approx1.67055\times10^{-7},
 \qquad
 \|\Delta_{649}\|_\infty
 \le U_\infty(649)\approx3.93324\times10^{-9}.
\]

Both *upper bounds* exceed their continuum floors, so the row-sum route cannot
close either comparison.  At the rejected predecessors, even the largest
individual matrix entry lies below the floor while the Rayleigh norm lies
above it.  Entrywise maxima can therefore produce a false certificate; row
sums can miss a true one.

## 7. What the theorem does—and does not—say

The successful results prove

\[
 \lambda_{\min}(G_n^{\rm full},S)
 \ge L_2-\delta_2(n)>0
\]

for the declared experiment.  They include:

- the complete noncommuting finite generator;
- the exact finite DCT source ports;
- exact central-target parity and density normalization;
- every finite target mode;
- the validated continuum Gram;
- the declared source metric; and
- rigorous polynomial, summation, and spectral-norm errors.

The rejected predecessors prove only

\[
 \delta_2(n)>L_2.
\]

This means the inherited-floor perturbation criterion cannot certify those
grids.  It does not imply a null direction or a singular finite Gram.

The two adjacent brackets also do not prove global minimality.  Without a
monotonicity/no-recrossing theorem or an exhaustive certificate of every
earlier odd grid, “smallest successful grid” would be unsupported.

The present theorem does not cover:

- even or off-centre target placement;
- a natural discrete \(H^1\) metric;
- a compact or unbounded range of \(\tau\);
- the calibrated early or reflecting-boundary charts;
- a finite-width target or finite sensor frame;
- the complete-atlas floor \(10^{-19}\);
- a growing source band; or
- a physical, wave, radio, or acoustic conclusion.

## 8. Interpretation

Stage XII is the first two-direction finite bridge in the OIG program.  Its
main conceptual lesson is that convergence order alone is insufficient.
The relevant comparison is the exact error geometry relative to the certified
continuum floor.

Three valid estimates of the same matrix can answer three different
questions:

- an entrywise maximum can be dangerously optimistic;
- a row-sum norm is safe but can be too pessimistic; and
- the exact low-dimensional spectral geometry can resolve the true margin.

The sharp coefficient \(E\) makes the grid scale predictable.  The interval
calculation makes it provable.  Together they show how an asymptotic theorem
and a finite certificate can divide labor: the asymptotic identifies the
right scale and mechanism, while the validated finite calculation closes a
margin too small for generic constants.

The later \(H^1\) threshold is not inferior numerical behavior.  It reflects
a different declared source-cost geometry.  Operational information depends
on what perturbations cost and how outputs are measured; a metric change is a
change in the experiment.

No statement is made about fundamental spacetime or physical reality.  This
is a mathematical laboratory for the finite preservation of distinctions in
a noncommuting response system.

## 9. Reproduction

Install the frozen narrow dependency set:

```bash
python -m pip install -r oig_xii_two_port_requirements.txt
```

Run the 256-bit certificate and both focused suites:

```bash
python oig_xii_two_port_certificate.py \
  --precision-bits 256 \
  --taylor-degree 32 \
  --output /tmp/oig_xii_two_port.json
python -m unittest -v test_oig_xii_two_port_certificate.py
python -m unittest -v test_oig_xii_adversarial_controls.py
python -m unittest discover -v
```

The JSON contains exact rational Stage X floors and Taylor tails, directed
dyadic spectral endpoints, interval Grams and eigenvalues, Rayleigh rejection
bounds, transferred finite floors, environment versions, and the scope
boundary.  Binary64 values decide no theorem inequality.

Detailed sources:

- `OIG_XII_TWO_PORT_NEUMANN_THEOREM.md` — analytic \(n^{-2}\) expansion,
  explicit coefficient, and centred polynomial proof;
- `oig_xii_two_port_certificate.md` — outward-rounded proof trace and exact
  decision semantics;
- `OIG_XII_ADVERSARIAL_AUDIT.md` — independent normalization, parity, metric,
  norm, and minimality audit;
- `oig_xii_two_port_certificate.py` — proof-producing Arb checker;
- `oig_xii_two_port_requirements.txt` — frozen narrow dependency surface;
- `test_oig_xii_two_port_certificate.py` — precision repetition, dense-
  exponential overlap, and proof guards; and
- `test_oig_xii_adversarial_controls.py` — dense Kronecker, parity, norm, and
  logical counterexamples.

## 10. Literature and novelty boundary

Dyson expansions, Euler--Maclaurin quadrature, matrix-function Taylor bounds,
Rayleigh quotients, interval arithmetic, and generalized eigenvalue
perturbation are classical.  Stage XII makes no priority claim for those
ingredients.

The provisional contribution is their auditable assembly for the declared
two-port operational experiment: the explicit mixed \(n^{-2}\) coefficient,
its prediction of two metric-dependent resolution scales, and the first
outward-rounded two-direction transfer for the complete noncommuting finite
Neumann dynamics.  Literature novelty remains provisional pending independent
specialist review.

## 11. Next research order

1. **Make the two-port theorem uniform in lattice time.**  Prove a validated
   \(O(n^{-2})\) response bound on a compact interval
   \(\tau\in[\tau_0,\tau_1]\), then cover it with interval Taylor models.
2. **Close the \(\tau\to\infty\) tail.**  Combine the Stage VIII atomic-tail
   theorem with a quantitative finite-generator remainder to extend across
   the complete late lattice sector.
3. **Transfer the natural discrete \(H^1\) metric.**  Certify the generalized
   pair with \(S_{n,k}=1+n^2\omega_{n,k}\) instead of assigning the continuum
   coefficient cost.
4. **Resolve target placement.**  Compare odd central cells, even symmetric
   two-cell deposition, finite-width preparations, and controlled off-centre
   coordinates in one transport theorem.
5. **Certify finite sensor frames.**  Replace the complete modal output with
   finite time/profile measurements while preserving the two transferred
   directions.
6. **Return to the complete atlas.**  Add calibrated early and reflecting-
   boundary finite models, using the global Stage X floor only where its
   declared strata apply.
7. **Resume growing bands.**  Seek uniform mixed-word and spectral constants
   strong enough to let \(K\) grow with \(n\).
8. **Continue to wave, radio, and acoustic sensing.**  After parabolic
   finite-transfer and finite-frame questions are controlled, test
   finite-speed and path-history analogues without importing conclusions from
   the present model.

The immediate target is the first.  The two-port bridge now exists at one
lattice time; the next milestone is to turn an isolated certified point into
a certified late-chart interval.
