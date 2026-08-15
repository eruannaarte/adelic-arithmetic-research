# Operational Information Geometry XI

## From continuum visibility to a certified finite experiment

- **Research status:** analytic theorem, outward-rounded computation, and
  adversarial audit; not peer reviewed
- **Research, theorem development, computation, and writing:** Codex (OpenAI)
- **Originating direction and research environment:** TGN's human founder
- **Predecessor:** Operational Information Geometry X
- **Scope:** the declared one-way parabolic path model; not a physical theory

## Abstract

Stage X certified positive generalized response-Gram floors for continuum
phase models.  Stage XI asks the harder question: when does a finite grid,
finite target preparation, finite boundary geometry, and finite noisy sensor
system preserve those observable directions?

The answer is metric-relative.  Put the finite and continuum experiments in
the same source and whitened output spaces, including their preparation,
sensor, calibration, and noise maps.  If the normalized responses satisfy

\[
 \|\mathcal A_h-\mathcal A\|\le \eta_K<\sqrt{L_K},
\]

where \(L_K\) is a certified continuum Gram floor, then

\[
 \boxed{
 \lambda_{\min}(\mathcal A_h^*\mathcal A_h)
 \ge (\sqrt{L_K}-\eta_K)^2>0.}
\]

A direct metric-normalized Gram error \(\delta_K<L_K\) instead gives the
finite floor \(L_K-\delta_K\).  An exact telescoping factorization separates
spatial quadrature, target deposition, boundary transport, mixed causal
words, finite sensors, whitening, and source-metric error.  This makes the
theorem a proof contract rather than an informal convergence claim.

The early calibrated chart has a new obstruction.  Midpoint moment leakage is
amplified to \(O(h^2q^{1-K})\), and pure moment fitting still does not control
mixed diffusion--modulation words.  For the affine ramp, the explicit
three-port source

\[
 e_3=\phi_3-\frac19\phi_1
\]

has vanishing first and second multiplication moments, but

\[
 \boxed{\langle V,Ae_3\rangle=-\frac{64\sqrt2}{45}\ne0.}
\]

The finite causal remainder must therefore be enclosed as a complete matrix
exponential response, or by a validated noncommutative word expansion.

The computational part proves two deliberately different results at the
one-cell lattice point \(\tau=1\).  First, Arb midpoint quadrature transfers
the limiting phase Gram through eight cosine ports in both the declared
\(L^2\) and continuum-\(H^1\) metrics.  Second, for the *actual* finite
Neumann generator, retaining the noncommutation of diffusion and modulation,
the first certified finite-model crossing in the tested sequence
\(3\le n\le7\) occurs at one port and \(n=7\).
The resulting direction-safe certified finite floors are

\[
 >2.51731\times10^{-5}\quad(L^2),
 \qquad
 >2.31592\times10^{-6}\quad(H^1).
\]

Two-port full-model calculations suggest an \(O(n^{-2})\) crossing near
\(n=383\), but this remains descriptive evidence.  Stage XI therefore
reaches a real finite experiment without conflating phase quadrature with
finite dynamics, and leaves a sharply specified next theorem: enclose the
full two-port mixed-word error tightly enough to certify that crossing.

## 1. The finite-transfer problem

Let \(C_K:\mathbb C^K\to E_K\) synthesize a complement of the exact source
null and let \(S_K\succ0\) be the declared source-cost Gram.  For a continuum
chart \(c\), let \(R_{K,c}\) be the physical response and let \(\Sigma_c\)
be the output-noise covariance.  After any declared sensor projection
\(P_c\), the normalized response is

\[
 \mathcal A_{K,c}
 =\Sigma_c^{-1/2}P_cR_{K,c}C_KS_K^{-1/2}.
 \tag{1.1}
\]

The finite experiment has its own injection \(I_h\), response \(R_{K,h,c}\),
sensor \(P_{h,c}\), covariance \(\Sigma_{h,c}\), and source metric
\(S_{K,h}\).  A comparison also needs an explicit bridge \(J_{h,c}\) from
the finite output into the continuum comparison space:

\[
 \mathcal A_{K,h,c}
 =J_{h,c}\Sigma_{h,c}^{-1/2}P_{h,c}R_{K,h,c}
 I_hC_KS_{K,h}^{-1/2}.
 \tag{1.2}
\]

Without the bridge and the two metrics, \(R_h-R\) is not a defined
coordinate-invariant object.  Early causal calibration belongs inside
(1.1)--(1.2), as does the transformation of the noise covariance.

The continuum certificate has the form

\[
 \mathcal A_{K,c}^*\mathcal A_{K,c}\succeq L_KI.
 \tag{1.3}
\]

The finite question is not whether a raw matrix entry converges.  It is
whether the entire normalized experiment remains within the singular-value
margin \(\sqrt{L_K}\).

## 2. The transfer theorem

### Theorem 2.1 — normalized-response transfer

Suppose \(\mathcal A\) and \(\mathcal A_h\) have common domain
\(\mathbb C^K\), a common output comparison space, and

\[
 \mathcal A^*\mathcal A\succeq L_KI,
 \qquad
 \|\mathcal A_h-\mathcal A\|\le\eta_K.
 \tag{2.1}
\]

Then

\[
 \boxed{
 \lambda_{\min}(\mathcal A_h^*\mathcal A_h)
 \ge(\sqrt{L_K}-\eta_K)_+^2.}
 \tag{2.2}
\]

Indeed, for every unit source \(z\),

\[
 \|\mathcal A_hz\|
 \ge\|\mathcal Az\|-\|(\mathcal A_h-\mathcal A)z\|
 \ge\sqrt{L_K}-\eta_K.
\]

The threshold for a response error is therefore \(\sqrt{L_K}\), not
\(L_K\).

### Theorem 2.2 — direct Gram and changed-metric transfer

If the same source metric \(S_K\) is used and

\[
 \delta_K=
 \|S_K^{-1/2}(G_{K,h}-G_K)S_K^{-1/2}\|<L_K,
 \tag{2.3}
\]

then

\[
 \boxed{\lambda_{\min}(G_{K,h},S_K)\ge L_K-\delta_K.}
 \tag{2.4}
\]

If, in addition to (2.3),

\[
 \rho_K=
 \|S_K^{-1/2}(S_{K,h}-S_K)S_K^{-1/2}\|<1,
 \tag{2.5}
\]

then

\[
 \boxed{
 \lambda_{\min}(G_{K,h},S_{K,h})
 \ge\frac{L_K-\delta_K}{1+\rho_K}.}
 \tag{2.6}
\]

This is not cosmetic.  The exact counterexample

\[
 G_h=G=I_2,
 \qquad
 S=I_2,
 \qquad
 S_h=\operatorname{diag}(1,h^{-2})
\]

has zero Euclidean Gram error and generalized finite floor \(h^2\to0\).

For midpoint cosine injection, the finite \(L^2\) metric is exactly \(I\)
when \(K<n\).  If the natural discrete \(H^1\) cost
\(1+\mu_{k,h}\) is used instead of the declared continuum cost
\(1+(k\pi)^2\), the difference must be retained in (2.5).

## 3. A proof-producing error decomposition

Insert intermediate normalized response operators by replacing, one at a
time,

1. continuum phase integration by finite spatial/modal quadrature;
2. the ideal target profile by its finite deposition;
3. the ideal boundary coordinate by the finite geometry;
4. frozen multiplication by the full diffusion--modulation generator;
5. the complete output by the declared finite sensor map; and
6. continuum source/output metrics by their finite counterparts.

Writing the consecutive differences as \(E_j\) gives the exact identity

\[
 \mathcal A_h-\mathcal A=\sum_jE_j
\]

and hence

\[
 \boxed{
 \eta_K\le
 \eta_{\rm space}+\eta_{\rm prep}+\eta_{\rm bdry}
 +\eta_{\rm word}+\eta_{\rm sens}+\eta_{\rm metric}.}
 \tag{3.1}
\]

Every term in (3.1) is a norm of two explicit adjacent experiments.  This
prevents two modeling changes from canceling accidentally inside one
numerical residual.

For an \(S_K\)-orthonormal source basis \(u_i\), validated column bounds

\[
 \|E_ju_i\|\le e_{j,i}
\]

give

\[
 \|E_j\|\le\left(\sum_{i=1}^Ke_{j,i}^2\right)^{1/2}.
 \tag{3.2}
\]

A direct interval singular-value enclosure is sharper.  When a computation
works with Grams, verified definiteness of

\[
 G_{K,h}-(L_K-\delta)S_{K,h}
\]

can avoid a pessimistic conversion through separate local norms.

## 4. Chartwise finite-model requirements

For the cell-centred Neumann grid \(h=1/n\),

\[
 A_h=h^{-2}L_n,
 \qquad
 \mu_{k,h}=4h^{-2}\sin^2\frac{k\pi h}{2}.
\]

The first \(K\) midpoint cosine ports are exactly orthonormal for \(K<n\),
and

\[
 0\le(k\pi)^2-\mu_{k,h}
 \le\frac{(k\pi)^4h^2}{12}.
 \tag{4.1}
\]

For fixed \(K\), conservative Stage VIII--IX error scales are:

| chart | safe path | regular error scale |
|:---|:---|:---|
| balanced resolved, fixed positive \(q=t/\varepsilon^2\) | \(\varepsilon=\sqrt h,\ t=qh\) | \(O_K(h)\) |
| fixed finite-cell lattice | exact fixed profile \(Q\), \(t=\tau h^2\) | \(O_K(h)\) |
| smooth interior atomic | \(\varepsilon=O(h),\ t=h\) | \(O_K(h)\) |
| reflecting boundary | actual \(\kappa_h\), \(\sigma_h=O(h)\), \(t=h^{4/3}\) | \(O_K(h^{2/3})\) |
| calibrated early endpoint, \(K\ge2\) | \(\varepsilon=h^{1-1/K},\ q=h^{2/K},\ t=h^2\) | conditional \(O_K(h^{2/K})\) |

These are sufficient asymptotic guides, not transfer certificates.  Their
constants must be enclosed and compared with \(L_K\).

At fixed lattice time, target convergence must preserve the complete local
cell profile:

\[
 \eta_{\rm prep}^{\rm L}\lesssim\|w_h-Q\|_1.
 \tag{4.2}
\]

Weak convergence alone misses growing target frequencies.  In the atomic
chart, a target with physical variance \(\sigma_h^2\) needs
\(\sigma_h^2/t\to0\).  For reflecting boundaries, either compare the finite
model with the continuum chart at its actual \(\kappa_h\), or enclose the
coordinate error explicitly.  A conservative fixed-band boundary budget is

\[
 \sqrt t+h+\frac{h^2+\sigma_h^2}{t}
 +B_K|\kappa_h-\kappa|.
 \tag{4.3}
\]

This gives the table's \(O_K(h^{2/3})\) path when the continuum comparison
uses the actual \(\kappa_h\).  The interior common-window lower bound cannot
be reused blindly because the reflecting cosine image term is not a positive
semidefinite multiplier for every \(\kappa\).

A finite sensor system also needs a frame certificate.  Let
\(\mathcal A_0\) be the pre-sensor normalized response, and let \(P_M\) be
orthogonal in its whitened output space.  Then

\[
 G-G_M=\mathcal A_0^*(I-P_M)\mathcal A_0,
 \qquad
 \delta_{\rm sens}
 =\|G-G_M\|
 =\|(I-P_M)\mathcal A_0\|^2.
 \tag{4.4}
\]

The count \(M\ge K\) is necessary but not sufficient.  A repeated or
misaligned set of \(K\) sensors can still have rank below \(K\).

## 5. Early calibration and the causal-word obstruction

Let \(e_1,\ldots,e_K\) be a moment-adapted source basis with

\[
 \langle V^j,e_i\rangle=0\quad(0\le j<i),
 \qquad
 \langle V^i,e_i\rangle\ne0,
\]

and calibrate by

\[
 D_K(q)=\operatorname{diag}(q,q^2,\ldots,q^K).
\]

Assume the canonical midpoint injection of the nonconstant cosine band with
\(K<n\).  Its discrete zeroth moments vanish exactly.  For
\(0<q\le q_0<1\), composite midpoint quadrature gives \(O(h^2)\) higher-moment
defects.  Put

\[
 H_{j,i}=\frac12\|(V^je_i)''\|_{L^1},
 \qquad
 H_K=\max_{i\le K,\,j\le i}H_{j,i},
\]

with the finite matrix-norm aggregation factors absorbed into \(H_K\).
After early calibration, lower moments in the deepest column are amplified:

\[
 \boxed{
 \Delta_{K,h}(q)
 \le h^2H_K\left(1+\frac{q^{1-K}}{1-q}\right).}
 \tag{5.1}
\]

Thus raw second-order consistency does not imply calibrated consistency.
Exact discrete moment fitting can remove (5.1), but can change the induced
source metric, which must be retained or bounded, and does not remove the next
obstruction.

For \(V(x)=1+4x/5\), \(A\phi_k=(k\pi)^2\phi_k\), and

\[
 e_3=\phi_3-\frac19\phi_1,
\]

direct integration gives

\[
 \langle V,e_3\rangle=\langle V^2,e_3\rangle=0,
 \qquad
 \langle V^3,e_3\rangle
 =-\frac{2048\sqrt2}{3375\pi^4},
 \tag{5.2}
\]

but

\[
 \boxed{\langle V,Ae_3\rangle=-\frac{64\sqrt2}{45}.}
 \tag{5.3}
\]

The second Taylor coefficient of
\(\langle1,e^{-t(A+\mu V)}e_3\rangle\) therefore contains

\[
 \frac{t^2\mu}{2}\langle V,Ae_3\rangle.
\]

After \(q^{-3}\) calibration its relative size is \(t/q^2\).  Cancellation
of the pure moments does not certify the causal flag.

The correct finite object is the complete calibrated remainder

\[
 \eta_{\rm word}
 =\left\|
 J_h\Sigma_h^{-1/2}P_h
 \left(R_h^{A+\mu V}-R_h^{\mu V}\right)
 I_hC_KD_K(q)^{-1}S_K^{-1/2}
 \right\|.
 \tag{5.4}
\]

Because (5.4) is finite dimensional, validated matrix exponentials can
enclose it without truncating the noncommutative series.  If a word expansion
is used, it must cover the \(V\)-generated cyclic space and include a
certified tail; \(\|A\|_{E_K}\) alone is insufficient because multiplication
by \(V\) leaves \(E_K\).

For fixed \(K\ge2\), the path

\[
 \varepsilon=h^{1-1/K},
 \qquad q=h^{2/K},
 \qquad t=h^2
 \tag{5.5}
\]

balances the resolution, moment-leakage, and leading mixed-word powers at
\(h^{2/K}\), provided the complete causal constant is outward-enclosed.
No uniform growing-\(K\) conclusion is inferred from this fixed-band path.

## 6. Rigorous phase-grid transfer through eight ports

At the one-cell lattice point \(\tau=1\), define for
\(\phi_k=\sqrt2\cos(k\pi x)\)

\[
 F_k(s)=\int_0^1e^{-s(1+4x/5)}\phi_k(x)\,dx.
\]

The normalized continuum phase Gram is

\[
 G_{ij}=\sqrt2\int_0^1
 F_i\!\left(4\sin^2\frac{\pi\xi}{2}\right)
 F_j\!\left(4\sin^2\frac{\pi\xi}{2}\right)d\xi,
 \tag{6.1}
\]

and its cell-centred midpoint quadrature is

\[
 \widetilde G_{n,ij}=\frac{\sqrt2}{n}\sum_{r=0}^{n-1}
 F_i\!\left(4\sin^2\frac{\pi(r+1/2)}{2n}\right)
 F_j\!\left(4\sin^2\frac{\pi(r+1/2)}{2n}\right).
 \tag{6.2}
\]

Arb encloses the integral, every summand, and the metric-whitened error.
The first sequential grid sizes proving \(\delta_K(n)<L_K\) are:

| \(K\) | \(L^2\) first \(n\) | continuum-\(H^1\) first \(n\) |
|---:|---:|---:|
| 1 | 5 | 5 |
| 2 | 8 | 8 |
| 3 | 10 | 10 |
| 4 | 12 | 12 |
| 5 | 13 | 14 |
| 6 | 15 | 16 |
| 7 | 17 | 18 |
| 8 | 18 | 19 |

The hardest successful comparison is \(K=8\), \(L^2\), where the
transferred floor is only about \(1.12\times10^{-28}\).  The preceding grid
is rigorously rejected, and the crossing is stable at 256 and 320 bits.

This theorem concerns the limiting phase integrand.  Its rapid convergence
comes from analytic midpoint quadrature.  It is not a certificate for the
full finite generator.

## 7. First complete finite Neumann transfer

For the actual cell-centred model, let \(L_n\) be the unscaled Neumann path
Laplacian, \(V_n\) the sampled ramp, \(u_{n,k}\) the DCT source port, and
\(\omega_{n,\ell}=4\sin^2(\pi\ell/(2n))\).  With central atomic target
coefficient \(\beta_{n,\ell}\), the full response uses

\[
 a_{n,\ell k}
 =\mathbf1^T
 \exp[-(L_n+\omega_{n,\ell}V_n)]u_{n,k},
 \tag{7.1}
\]

and

\[
 G^{\rm full}_{n,ij}
 =\frac{\sqrt2}{n}\sum_{\ell=1}^{n-1}
 \beta_{n,\ell}^2a_{n,\ell i}a_{n,\ell j}.
 \tag{7.2}
\]

Unlike (6.2), (7.1) retains every mixed diffusion--modulation word.  Arb
matrix exponentials enclose the complete finite response.

For \(K=1\), \(n=7\) is the first crossing in the tested sequence
\(3\le n\le7\):

| metric | certified error upper | continuum floor \(L_1\) | certified finite floor |
|:---|---:|---:|---:|
| \(L^2\) | \(<1.05892\times10^{-4}\) | \(>1.31064\times10^{-4}\) | \(>2.51731\times10^{-5}\) |
| continuum \(H^1\) | \(<9.74199\times10^{-6}\) | \(>1.20579\times10^{-5}\) | \(>2.31592\times10^{-6}\) |

The finite and continuum coefficient spaces use the same declared source
cost.  DCT orthogonality makes finite \(L^2\) exactly \(I\).  The displayed
\(H^1\) result deliberately assigns the continuum cost
\(1+(k\pi)^2\) to the finite coefficient as well; a natural discrete energy
would be a different generalized pair requiring (2.5)--(2.6).

This is the first complete finite-model spectral transfer in the OIG line.
It is a theorem at one declared lattice point and one source port, not a
whole-atlas statement.

## 8. The two-port frontier

Binary64 evaluation of the same full finite model gives:

| \(n\) | descriptive \(\delta_2(n)\) | ratio to the Stage X late-core floor |
|---:|---:|---:|
| 31 | \(1.73994\times10^{-5}\) | 121.55 |
| 63 | \(4.24927\times10^{-6}\) | 29.68 |
| 127 | \(1.04843\times10^{-6}\) | 7.32 |
| 255 | \(2.60298\times10^{-7}\) | 1.82 |
| 383 | \(1.15415\times10^{-7}\) | 0.806 |
| 511 | \(6.48439\times10^{-8}\) | 0.453 |

The values are consistent with \(O(n^{-2})\) convergence and an apparent
crossing near \(n=383\).  They do not decide a theorem inequality: binary64
roundoff and an unbounded analytic remainder cannot certify a positive
floor.  The next proof must either outward-enclose (7.2) at that scale or
derive a quantitative full-Neumann \(O(n^{-2})\) bound with a constant below
the available continuum margin.

For the *complete* two-port continuum atlas, Stage X has only the conservative
global floor \(10^{-19}\).  A full-atlas finite transfer therefore needs
either

\[
 \delta_2<10^{-19}
\]

at Gram level or

\[
 \eta_2<3.16227\times10^{-10}<\sqrt{10^{-19}}
\]

at response level.  The much larger late-core floor used in the table above
cannot be substituted for the early and reflecting-boundary strata.

## 9. Growing bands and shrinking margins

Stage X supplies a common late-core lower frame of the form

\[
 L_K\ge e^{-C_0K^2}.
\]

If a validated finite family proves

\[
 \delta_K\le C_1K^ah^p
\]

with constants uniform along a declared late-chart path, then

\[
 C_1K^ah^pe^{C_0K^2}\to0
\]

is sufficient.  Under subexponential hidden constants this allows

\[
 K=o(\sqrt{\log(1/h)}).
\tag{9.1}
\]

The relevant geometric restriction must also hold on the chosen chart:
\(K\varepsilon\to0\), \(Kh\to0\), or \(K\sqrt t\to0\), respectively.

The early balanced path (5.5) is more restrictive.  If the relevant early
continuum floor additionally obeys \(L_K\ge e^{-C_0K^2}\), and the
moment-basis and complete mixed-word constants grow subexponentially on that
scale, it conditionally gives

\[
 K=o((\log(1/h))^{1/3}),
 \tag{9.2}
\]

Neither statement follows from fixed-\(K\) big-\(O\) notation, and (9.2) is
not a proved growing-band full-atlas theorem: no all-\(K\) early/boundary
continuum lower certificate or uniform mixed-word enclosure is presently
available.

The factorial upper ceiling adds a necessary warning.  At fixed lattice
time,

\[
 \gamma_K\le A^2\frac{c^{2K}}{(K!)^2},
\]

so relative transfer demands an error smaller than that shrinking scale.
Geometric resolution \(Kh\to0\) alone cannot guarantee a stable growing
band.

## 10. Falsification ledger

| Tempting statement | Correct boundary |
|:---|:---|
| \(\|G_h-G\|\to0\) transfers the generalized spectrum | only the declared metric-normalized error, or a direct pair certificate, does |
| response error must be below \(L_K\) | the sharp threshold is \(\sqrt{L_K}\); Gram error is compared with \(L_K\) |
| midpoint accuracy makes early calibration safe | canonical exact-mass lower-moment leakage is amplified by \(q^{1-K}\) |
| exact pure-moment fitting proves the causal flag | mixed \(A\)-\(V\) words survive; (5.3) is an exact counterexample |
| weak target convergence selects a lattice profile | the fixed-\(\tau\) chart retains the complete local profile \(Q\) |
| a fixed boundary coordinate is automatic | cell placement can create order-one chart error unless \(\kappa_h\) is controlled |
| \(M\ge K\) sensors preserve rank | a sensor-frame lower bound is also required |
| output whitening creates information | whitening must transform the noise covariance and preserves generalized information |
| the phase-grid \(K\le8\) result is a finite-dynamics theorem | false; full dynamics is certified only for \(K=1,n=7\) here |
| the observed \(K=2,n=383\) crossing is proved | false; it is a numerical target for the next enclosure |
| fixed-band convergence proves growing-band transfer | the error must beat the shrinking continuum floor with uniform constants |

## 11. Interpretation

Stage XI identifies the exact bridge from an ideal observable geometry to a
finite experiment.  The bridge is not “take a finer grid.”  It is the whole
normalized chain

\[
 \text{source cost}
 \longrightarrow\text{source injection}
 \longrightarrow\text{finite dynamics}
 \longrightarrow\text{target/sensors}
 \longrightarrow\text{noise whitening}.
\]

An observable distinction survives only if that complete chain remains
inside the certified singular-value margin.  This is an operational version
of stability: the geometry is defined by what the declared experiment can
distinguish, and every discretization or sensing choice is part of the
geometry rather than an invisible implementation detail.

The result is potentially reusable beyond this toy model.  Whenever an
inverse problem has a continuum observability inequality, a finite solver,
calibrated source coordinates, and colored output noise, the normalized
response theorem gives the correct transfer target.  The OIG-specific work
supplies a nontrivial example where singular scaling, target concentration,
boundary images, and noncommuting generator terms all matter simultaneously.

No claim is made that this model describes fundamental physical reality.
It is a controlled mathematical laboratory for how finite experiments
preserve or destroy distinctions present in an ideal response geometry.

## 12. Reproduction

Install the repository dependencies:

```text
python -m pip install -r requirements.txt
```

Run the Stage XI certificate and focused tests:

```text
python oig_xi_transfer_certificate.py \
  --max-band 8 \
  --precision-bits 320 \
  --maximum-phase-side-length 24 \
  --output /tmp/oig_xi_transfer.json
python -m unittest -v test_oig_xi_transfer_certificate.py
python -m unittest -v test_oig_xi_adversarial_controls.py
python -m unittest discover -v
```

The proof-producing run uses Arb balls through `python-flint`.  Its JSON
records the exact rational Stage X floors, dyadic outward error bounds,
transferred finite floors, rejected predecessor grids, environment versions,
and proof boundary.  NumPy/SciPy values in the two-port sweep are descriptive
only and never decide a certificate.

Detailed sources:

- `OIG_XI_FINITE_TRANSFER_THEOREM.md` — analytic transfer theorem, error
  ledger, causal-word obstruction, and mesh budgets;
- `oig_xi_transfer_certificate.md` — complete Arb proof trace and numerical
  tables;
- `OIG_XI_ADVERSARIAL_AUDIT.md` — independent metric, moment, target,
  boundary, sensor, and growing-band counterexamples;
- `oig_xi_transfer_certificate.py` — phase-grid and full finite-Neumann
  proof-producing checker;
- `test_oig_xi_transfer_certificate.py` — certificate guards and precision
  repetition; and
- `test_oig_xi_adversarial_controls.py` — exact falsification controls.

## 13. Literature and novelty boundary

Singular-value perturbation, generalized eigenvalue comparison, finite
element consistency, validated matrix functions, and sensor-frame theory are
classical subjects.  Stage XI makes no priority claim for those ingredients.
Its provisional contribution is their auditable assembly for this declared
operational atlas, together with the rigorous calibrated moment-leakage
amplification bound, the
explicit mixed-word counterexample, and the first outward-rounded transfer
from an OIG continuum floor to the complete finite Neumann response.

The literature boundary and the finite-element sources used for the
chartwise rates are recorded in the detailed Stage VIII--XI theorem memos.
Novelty remains provisional pending independent specialist review.

## 14. Next research order

1. **Certify the full two-port Neumann crossing.**  Turn the observed
   \(O(n^{-2})\) convergence near \(n=383\) into an Arb enclosure or a sharp
   analytic bound for the complete mixed-word response.
2. **Make the lattice result uniform in \(\tau\).**  Cover a compact
   \(\tau\)-interval with validated response bounds and close the
   \(\tau\to\infty\) tail analytically.
3. **Transfer the complete two-port atlas.**  Add calibrated early and full
   reflecting-boundary finite models, using the global Stage X floor and
   chart-specific error budgets.
4. **Certify finite sensor frames.**  Replace the complete modal output by
   finitely many time/profile measurements while preserving the transferred
   effective rank.
5. **Build the finite causal-word filtration.**  Construct moment-adapted
   coordinates for the noncommutative algebra generated by \(A\) and \(V\),
   not only the multiplication powers of \(V\).
6. **Return to growing bands.**  Prove uniform constants strong enough to
   turn the conditional schedules (9.1)--(9.2) into actual diagonal theorems.
7. **Continue to path-space and wave sensing.**  Once parabolic transfer and
   finite frames are controlled, test jump-history ports and finite-speed
   analogues, including the previously noted radio/acoustic branch.

The immediate target is the first.  The continuum floor is no longer merely
an ideal quantity, and one finite direction has now crossed the bridge.  The
next milestone is to make the two-direction crossing a theorem.
