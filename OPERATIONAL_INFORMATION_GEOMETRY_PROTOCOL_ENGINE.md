# Operational Information Geometry — from response limits to certified experiments

## A resolution-aware transfer theorem and a proof-producing protocol-design engine

**Research status:** proved within the declared finite and continuum models;
not peer reviewed

**Author:** Codex (OpenAI), developed from the originating research question
and computational environment provided by TGN's founder

---

## Abstract

Earlier Operational Information Geometry results constructed response
quotients, proved fixed-mode continuum convergence, resolved the
smooth-to-atomic initial layer, identified compact growing-band Gramians, and
certified positive continuum information floors. This paper closes the next
operational loop: it turns those response theorems into finite experimental
designs with reconstructible certificates.

The first result is a necessary correction to the naive uniform-transfer
target. No fixed finite Neumann grid can approximate the normalized one-cell
lattice response for all lattice times \(\tau\ge1\): the finite response
eventually decays exponentially, while the continuum normalization approaches
a positive atomic Gram. The correct theorem is resolution aware. For the first
two cosine ports and every odd \(n\ge3\),

\[
 \|G_n(\tau)-G(\tau)\|_{L^2}
 <23\frac{\sqrt\tau}{n},
 \qquad
 \|G_n(\tau)-G(\tau)\|_{H^1}
 <\frac{23}{10}\frac{\sqrt\tau}{n}.
\]

The continuum-to-atomic error is bounded by \(2/(3\tau)\) and
\(1/(15\tau)\), respectively. These estimates give explicit joint
\(n(\tau)\) schedules on the whole late half-line. A complementary Arb
certificate gives a much sharper practical cover at \(n=1001\), uniformly
for \(1\le\tau\le6/5\), in \(L^2\), declared continuum \(H^1\), and natural
discrete \(H^1\).

The second result is a proof-producing finite protocol engine. It removes
exact common blind directions, descends the declared source cost to the
minimum-cost quotient, includes output-noise precision and protocol cost,
finds an E-optimal candidate design, and returns exact rational primal and
dual bounds. An interval-response layer transfers that certificate to every
response inside declared rational boxes. A finite-frame theorem then
compresses the complete \(n=345\) Neumann modal field from 172 active outputs
to two matched linear sensors. The information loss is second order in the
Arb response radii and is certified below \(1.95\times10^{-37}\) in \(L^2\).
The resulting two-channel physical floor exceeds
\(5.74300087146830\times10^{-6}\). A separate nonreversible four-state hidden
Markov benchmark yields an exact design bracket with certified efficiency
above 97.25 percent.

These are experiment-design theorems for declared stochastic models. They do
not establish that nature uses those models, that matched global sensors are
hardware-local, or that a candidate protocol library is physically complete.

---

## 1. The operational question

Let \(u\in\mathbb R^d\) denote an intervention coordinate and let
\(S\succ0\) be its declared cost metric. Protocol \(i\) produces a linearized
response

\[
 y_i=R_i u+\xi_i,
 \qquad
 \operatorname{Cov}(\xi_i)=\Sigma_i,
\]

with information form

\[
 A_i=R_i^T\Sigma_i^{-1}R_i.
 \tag{1.1}
\]

If the protocol has cost \(c_i>0\) and physical use weight \(w_i\ge0\), the
budget and aggregate information are

\[
 \sum_i c_iw_i=1,
 \qquad
 G(w)=\sum_iw_iA_i.
 \tag{1.2}
\]

The operational design objective is the weakest observable direction,

\[
 \max_w\lambda_{\min}(G(w),S).
 \tag{1.3}
\]

Three proof obligations precede any physical interpretation:

1. the finite response must approximate the declared limiting model on the
   parameter domain actually used;
2. source and output calibrations must be carried through the comparison; and
3. the numerical design must be replaced by an outward or exact certificate.

The present work supplies all three obligations for the models stated below.

---

## 2. Why a fixed-grid uniform theorem is impossible

For the exactly-centred odd-grid target, the constant target mode is removed
and the smallest retained target mode is \(\ell=2\). At fixed finite \(n\),
every retained finite generator has a strictly positive eigenvalue. Therefore

\[
 G_n(\tau)\longrightarrow0
 \qquad(\tau\to\infty)
 \tag{2.1}
\]

exponentially, even after multiplication by the continuum normalization
\(\sqrt{1+\tau}\).

The normalized continuum one-cell lattice Gram instead satisfies

\[
 G(\tau)\longrightarrow G_\infty\succ0.
 \tag{2.2}
\]

Hence, for every fixed \(n\),

\[
 \sup_{\tau\ge1}\|G_n(\tau)-G(\tau)\|
 \not\longrightarrow0.
 \tag{2.3}
\]

This is not a numerical pathology. It is a noncommutation of limits: the late
lattice limit requires increasing spatial resolution. The correct small
parameter is

\[
 \frac{\sqrt\tau}{n}=\sqrt{t},
 \qquad t=\frac{\tau}{n^2}.
 \tag{2.4}
\]

---

## 3. Explicit coupled-resolution theorem

Consider the cell-centred Neumann path, interaction
\(V(x)=1+4x/5\), source ports
\(\phi_k(x)=\sqrt2\cos(k\pi x)\), \(k=1,2\), and the exactly-centred one-cell
target on odd grids.

### Theorem 3.1 — global finite-to-lattice bound

For every odd \(n\ge3\) and every \(\tau\ge1\),

\[
 \boxed{
 \|G_n(\tau)-G(\tau)\|_2
 <23\frac{\sqrt\tau}{n}.}
 \tag{3.1}
\]

For the declared continuum energy metric

\[
 S=\operatorname{diag}(1+\pi^2,1+4\pi^2),
\]

\[
 \boxed{
 \|S^{-1/2}(G_n(\tau)-G(\tau))S^{-1/2}\|_2
 <\frac{23}{10}\frac{\sqrt\tau}{n}.}
 \tag{3.2}
\]

#### Proof structure

The proof keeps the full noncommuting finite generator. It separates only the
error analysis:

- an energy/Duhamel estimate gives the response-amplitude error
  \(A\sqrt t+Bh\);
- the mean-zero response envelope \(|b_{n,k}|,|F_k|\le(4/5)se^{-s}\)
  makes that error summable over all active target modes;
- exact odd-grid parity turns the modal target sum into midpoint quadrature;
  and
- explicit Gaussian accumulation and midpoint-variation bounds yield the
  constants.

Every weakening to 23 and \(23/10\) uses rational inequalities for
\(\pi,e,\sqrt2\). No numerical approximation decides (3.1) or (3.2).

### Theorem 3.2 — continuum atomic tail

For every \(\tau\ge1\),

\[
 \boxed{
 \|G(\tau)-G_\infty\|_2<\frac{2}{3\tau},
 \qquad
 \|G(\tau)-G_\infty\|_S<\frac{1}{15\tau}.}
 \tag{3.3}
\]

Equations (3.1)--(3.3) give a complete compact-plus-tail theorem. They also
produce executable, though intentionally conservative, schedules. For
example, half of the sharp Stage X one-cell floor is inherited whenever

\[
 n\ge322{,}000{,}000\sqrt\tau
 \quad(L^2),
 \qquad
 n\ge1{,}300{,}000{,}000\sqrt\tau
 \quad(H^1).
 \tag{3.4}
\]

The enormous constants measure proof inefficiency, not a predicted physical
resolution requirement. The observed sharp error is \(O(\tau/n^2)\).

### Practical compact certificate

A separate 256-bit Arb Taylor cover retains the complete noncommuting finite
dynamics and proves, at \(n=1001\), uniform transfer on

\[
 1\le\tau\le\frac65.
 \tag{3.5}
\]

The directed finite-to-continuum error uppers and transferred floors are:

| Metric | error upper | transferred floor lower |
|---|---:|---:|
| \(L^2\) | \(1.86417779915\times10^{-8}\) | \(1.24510187129\times10^{-7}\) |
| continuum \(H^1\) | \(1.64080518010\times10^{-9}\) | \(1.91150484201\times10^{-9}\) |
| natural discrete \(H^1\) | \(1.54750212864\times10^{-9}\) | \(2.00480789346\times10^{-9}\) |

The exact directed rational fields, rather than these displayed decimal
approximations, are the certificate.

---

## 4. Exact observable quotient

Stack every response row and let \(C\) be a rational row basis. Then

\[
 \mathcal N=\ker C=\bigcap_i\ker R_i
 \tag{4.1}
\]

is the exact common blind space. For quotient coordinates \(y=Cu\), the
minimum-cost representative and quotient metric are

\[
 J=S^{-1}C^T(CS^{-1}C^T)^{-1},
 \qquad
 S_q=(CS^{-1}C^T)^{-1}.
 \tag{4.2}
\]

Every response descends exactly:

\[
 R_i u=R_iJ(Cu),
 \qquad
 A_{i,q}=J^TA_iJ.
 \tag{4.3}
\]

The construction is invariant under a rational change of quotient
coordinates. Unlike a numerical rank threshold, it cannot turn a weak but
nonzero direction into an exact null.

---

## 5. Proof-producing E-optimal design

Put \(p_i=c_iw_i\), so \(p\) lies in the simplex. The quotient design problem
is

\[
 z_\star=\max_{p\in\Delta}
 \lambda_{\min}\!\left(
 \sum_i p_i\frac{A_{i,q}}{c_i},S_q
 \right).
 \tag{5.1}
\]

Floating point is used only to discover a candidate. The candidate weights
are rationalized with an exact unit budget.

### Primal certificate

For the rational candidate Gram \(G\), exact \(LDL^T\) proves

\[
 G-LS_q\succ0,
 \tag{5.2}
\]

so \(L<z_\star\).

### Dual certificate

For an exact rational factor \(K\), put

\[
 Z=\frac{KK^T}{\operatorname{tr}(S_qKK^T)}.
 \tag{5.3}
\]

Then \(Z\succeq0\), \(\operatorname{tr}(S_qZ)=1\), and

\[
 z_\star\le
 U=\max_i\frac{\operatorname{tr}(A_{i,q}Z)}{c_i}.
 \tag{5.4}
\]

Thus every design report contains the reconstructible bracket

\[
 \boxed{L\le z_\star\le U.}
 \tag{5.5}
\]

The engine also gives the least integer exposure that realizes all rational
physical weights and an exact Gaussian testing bound under the declared
whitened model.

---

## 6. Outward transfer from response boxes

Irrational semigroup responses cannot be silently converted to decimal
rationals. Let \(R\) be a rational centre, let \(E\ge0\) be a rational
entrywise radius, and assume

\[
 |R_{\rm true}-R|\le E.
 \tag{6.1}
\]

With \(W=\Sigma^{-1}\), define the nonnegative matrix

\[
 B=|R|^T|W|E+E^T|W||R|+E^T|W|E.
 \tag{6.2}
\]

If \(Q_B\) is diagonal with the row sums of \(B\), then for every source
vector \(x\),

\[
 \left|x^T(A_{\rm true}-A)x\right|
 \le |x|^TB|x|
 \le x^TQ_Bx.
 \tag{6.3}
\]

An exact rational \(LDL^T\) decision proves

\[
 Q_B\prec\delta S.
 \tag{6.4}
\]

For rational design shares \(p_i\), the total physical response uncertainty is

\[
 \delta_{\rm design}
 =\sum_i\frac{p_i}{c_i}\delta_i.
 \tag{6.5}
\]

Therefore the nominal design certificate transfers as

\[
 \boxed{
 G_{\rm true}\succeq(L-\delta_{\rm design})S.}
 \tag{6.6}
\]

The verifier reconstructs every response box, checks that its centre and
precision match the nominal design declarations, rebuilds (6.2)--(6.5), and
rejects altered noise or theorem fields.

---

## 7. Two matched sensors replace 172 modal outputs

Let the complete whitened finite response be

\[
 R_{\rm true}=R_0+E_R\in\mathbb R^{m\times d},
 \qquad d=2,quad m=172.
 \tag{7.1}
\]

The rational centre \(R_0\) is obtained from 192-bit Arb balls for the full
\(n=345\), \(\tau=1\), exactly-centred Neumann model. Define two matched
sensor rows

\[
 P=R_0^T.
 \tag{7.2}
\]

If the original 172 modal noises are white, the compressed noise covariance is

\[
 \Sigma_P=PP^T=R_0^TR_0.
 \tag{7.3}
\]

After whitening, the two-channel information is

\[
 G_P
 =R_{\rm true}^T
 R_0(R_0^TR_0)^{-1}R_0^T
 R_{\rm true}
 =R_{\rm true}^T\Pi R_{\rm true},
 \tag{7.4}
\]

where \(\Pi\) is the orthogonal projector onto \(\operatorname{range}(R_0)\).
Because \((I-\Pi)R_0=0\),

\[
 \boxed{
 G_{\rm full}-G_P
 =E_R^T(I-\Pi)E_R
 \preceq E_R^TE_R.}
 \tag{7.5}
\]

Thus the compression loss is second order in the response enclosure, rather
than first order. To turn the entrywise radius \(D\) into a form bound, the
checker uses

\[
 |E_Rx|\le D|x|,
 \qquad
 \|E_Rx\|_2^2\le |x|^TD^TD|x|.
 \tag{7.6}
\]

It then replaces \(D^TD\) by the diagonal matrix of its row sums. This last
diagonal dominates the scalar quadratic form by
\(2|x_ix_j|\le x_i^2+x_j^2\). The code does **not** assert the generally false
Loewner comparison \(E_R^TE_R\preceq D^TD\).

### Certified values

The complete finite response has 172 active even target modes. The rational
two-channel frame gives:

| Declared source cost | complete robust floor lower | matched-frame loss upper | inherited two-channel floor lower |
|---|---:|---:|---:|
| \(L^2\) | \(5.74300087146830\times10^{-6}\) | \(1.94675860514\times10^{-37}\) | \(5.74300087146830\times10^{-6}\) |
| rational \(H^1\) majorant \(\operatorname{diag}(11,41)\) | \(1.41073748093607\times10^{-7}\) | \(1.76978055013\times10^{-38}\) | \(1.41073748093607\times10^{-7}\) |

The second metric dominates both the declared continuum two-mode energy cost
and the natural finite-grid two-mode energy cost, since

\[
 4n^2\sin^2\frac{k\pi}{2n}\le(k\pi)^2,
 \qquad k=1,2.
 \tag{7.7}
\]

The result is mathematically finite sensing: 172 whitened modal channels are
compressed to two linear statistics without a meaningful loss at the proved
precision. It is not yet a locality theorem. Implementing those matched rows
with spatially local or radio/acoustic hardware would require a separate
sensor-synthesis constraint.

---

## 8. Broader hidden stochastic-network benchmark

The engine is also tested on a rational four-state, irreducible,
nonreversible continuous-time Markov chain. If observation time is
exponentially distributed with rate \(\alpha\), then

\[
 \mathbb E[C e^{-TL}J]
 =C\alpha(\alpha I+L)^{-1}J,
 \tag{8.1}
\]

so every candidate response is rational without replacing the dynamics by a
discrete-time surrogate.

Five protocols vary sensor, observation-time rate, output precision, and
cost. On the three-dimensional mass-preserving source tangent, the engine
returns

\[
 L=0.0271729952538361\ldots,
 \qquad
 U=0.0279404490621997\ldots,
 \tag{8.2}
\]

and therefore a certified design efficiency

\[
 \frac LU>0.9725325170.
 \tag{8.3}
\]

There are no exact blind directions. Four of the five protocols receive
positive rational weight, and the least exact integer realization uses budget
multiplier 600,000. Every matrix, quotient map, weight, primal shift, dual
witness, noise bound, and count is embedded in the generated JSON and checked
by an independent exact verifier.

---

## 9. What has been achieved

The research path that began with fixed-mode convergence has now reached a
working certified-design application:

1. fixed-mode response convergence is proved;
2. the smooth/atomic and lattice/continuum charts are identified;
3. fixed-grid uniform late transfer is disproved and replaced by the correct
   coupled-resolution theorem;
4. a practical compact Arb cover and a global analytic tail schedule are
   available;
5. exact null removal, cost calibration, noise whitening, and E-optimal design
   are implemented;
6. irrational response enclosures transfer into exact physical floors;
7. finite sensor loss is certified; and
8. both the canonical noncommuting Neumann model and a broader hidden CTMC are
   validated.

This is the first point in the programme where the mathematics answers an
experimenter's question rather than only describing a response limit:

> Which declared measurements should be taken, how should budget be divided,
> and what information floor survives model and sensor approximation?

---

## 10. Boundaries and next research order

The following are not claimed:

- one fixed finite grid does not cover all \(\tau\ge1\);
- the explicit global \(O(\sqrt\tau/n)\) schedule is valid but extremely
  conservative;
- the compact Arb cover currently stops at \(\tau=6/5\);
- matched Neumann sensors are global linear combinations, not local hardware
  designs;
- entrywise response boxes are conservative when correlations between errors
  are known;
- the engine optimizes a declared finite candidate library, not every
  physically possible experiment; and
- no conclusion about fundamental physics follows from the model.

The strongest next targets are:

1. prove the observed sharp uniform \(O(\tau/n^2)\) remainder, replacing the
   huge analytic schedule by practical resolution laws;
2. extend the Arb cover adaptively across larger compact \(\tau\) intervals;
3. add structured locality, sparsity, and bandwidth constraints to the matched
   sensor synthesis;
4. admit correlated interval or affine-arithmetic response uncertainty rather
   than entrywise boxes;
5. extend the exact quotient engine to robustly nominally blind directions;
6. add sequential and adaptive protocol design; and
7. instantiate a radio/acoustic branch in which candidate responses come from
   measured or simulated Green functions and the source/output metrics are
   physically calibrated.

The radio/acoustic branch is now a plausible application rather than an
analogy: the engine needs response maps, noise covariance, costs, and a source
metric, all of which can be declared for array sensing or channel sounding.
What remains is model-specific calibration and hardware-constrained sensor
synthesis.

---

## 11. Reproduction

Install the repository dependencies, then run:

```bash
python -m unittest -v \
  test_oig_uniform_lattice_transfer.py \
  test_oig_uniform_lattice_adversarial_controls.py \
  test_oig_uniform_lattice_explicit_constants.py

python -m unittest -v test_oig_uniform_lattice_arb_cover.py

python -m unittest -v \
  test_oig_protocol_design_engine.py \
  test_oig_protocol_engine_adversarial_controls.py \
  test_oig_interval_protocol_design.py \
  test_oig_interval_protocol_design_adversarial.py \
  test_oig_neumann_matched_frame.py

python oig_hidden_network_protocol_demo.py \
  --output /tmp/oig-hidden-protocol-design.json

python oig_neumann_matched_frame.py \
  --output /tmp/oig-neumann-matched-frame.json

python -m unittest -v test_oig_protocol_artifacts.py
```

The compact Arb cover is intentionally the slowest focused test. Exact
rational fields in the generated JSON are authoritative; displayed decimal
summaries are for readability.

The repository commits independently verifiable reference artifacts at:

- `certificates/oig_uniform_lattice_arb_cover.json`;
- `certificates/oig_hidden_protocol_design.json`; and
- `certificates/oig_neumann_matched_frame.json`.

Detailed sources:

- `OIG_UNIFORM_LATTICE_TRANSFER_THEOREM.md`
- `OIG_UNIFORM_LATTICE_EXPLICIT_CONSTANTS.md`
- `oig_uniform_lattice_arb_cover.md`
- `OIG_PROTOCOL_DESIGN_ENGINE.md`
- `OIG_INTERVAL_PROTOCOL_DESIGN_AUDIT.md`
- `OIG_PROTOCOL_ENGINE_ADVERSARIAL_AUDIT.md`
- `OIG_UNIFORM_LATTICE_ADVERSARIAL_AUDIT.md`

---

## 12. Credit and interpretation

This work was developed by **Codex (OpenAI)** from the originating curiosity,
research direction, and computational environment provided by **TGN's human
founder**. The result should be read as a transparent, executable contribution
to stochastic inverse problems, information geometry, and experimental
design—not as a claim about the ultimate substrate of reality.

Its conceptual lesson is narrower and useful: information becomes operational
geometry only after interventions, observations, costs, noise, approximation,
and exact null directions have all been declared. Once those declarations are
made, the geometry can select experiments and can state, with a certificate,
what remains distinguishable.
