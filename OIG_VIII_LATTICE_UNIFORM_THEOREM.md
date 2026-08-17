# Operational Information Geometry VIII

## Uniform finite-cell and atomic-tail theorem

- **Research lane:** lattice-scale and singular-preparation analysis
- **Date:** 14 August 2026
- **Status:** proof memo; not peer reviewed
- **Scope:** the declared cell-centred, one-way, rate-modulated Neumann path
  model
- **Predecessor:** `OPERATIONAL_INFORMATION_GEOMETRY_VII.md`

## 1. What this memo proves

Stage VII obtained the finite-cell phase function at each fixed microscopic
time

\[
 \tau=\frac{t}{h^2}
\]

and then took its large-\(\tau\) limit.  It left open whether the finite grid
itself has the same atomic limit along one simultaneous path

\[
 h\downarrow0,\qquad t\downarrow0,\qquad \frac{t}{h^2}\longrightarrow
 \infty.
\]

It does.  The strongest clean version is naturally a squared-norm theorem.
Let \(\mathcal N_h(t)\) be the complete density-normalized target response
norm, let \(\bar y_h\) and \(\sigma_h^2\) be the physical mean and variance of
the target probability preparation, and put

\[
 d_h=\operatorname{dist}(\bar y_h,\{0,1\}).
\]

For an exactly mean-zero smooth source port, a positive Lipschitz modulation,
and \(\tau=t/h^2\to\infty\), the quantitative estimate is

\[
 \boxed{
 \left|\sqrt t\,\mathcal N_h(t)^2-C_F^2\right|
 \leq C\left(
 \sqrt t+h+\frac1\tau+\frac{\sigma_h^2}{t}
 +\frac{\sqrt t}{d_h}
 \right). }
 \tag{1.1}
\]

The last term is only used in the interior version; replacing it by an
explicit boundary-layer profile gives a theorem all the way to a reflecting
endpoint.  Consequently, if

\[
 t\to0,\qquad \tau\to\infty,\qquad
 \frac{\sigma_h^2}{t}\to0,\qquad
 \frac{d_h}{\sqrt t}\to\infty,
 \tag{1.2}
\]

then

\[
 \boxed{\sqrt t\,\mathcal N_h(t)^2\longrightarrow C_F^2.}
 \tag{1.3}
\]

If \(C_F>0\), and only then, this is equivalent to

\[
 \boxed{\mathcal N_h(t)\sim C_Ft^{-1/4}.}
 \tag{1.4}
\]

For a preparation occupying \(O(1)\) lattice cells,
\(\sigma_h^2=O(h^2)\), so its preparation error in (1.1) is

\[
 \frac{\sigma_h^2}{t}=O(\tau^{-1}).
\]

Thus the result includes atoms, split atoms, and every uniformly
second-moment-bounded finite-cell mollifier.  A limiting subcell phase is not
needed in the atomic tail, although it remains essential when \(\tau\) stays
finite.

The memo also proves a uniform comparison with the Stage VII lattice chart.
If the carrier stays in a fixed interior compact set and the local cell
weights converge in \(\ell^1\) to a fixed probability profile \(Q\), then,
uniformly from finite microscopic time into the atomic tail,

\[
 \sqrt\tau\left|
 h\mathcal N_h(\tau h^2)^2-\Psi_Q(\tau)^2
 \right|
 \leq C\left(
 \sqrt t+h+\|w^{(h)}-Q\|_1+\frac{\sqrt t}{d_h}
 \right).
 \tag{1.5}
\]

For \(\tau\) in a fixed compact subset of \((0,\infty)\), the more directly
readable form is

\[
 \boxed{
 \left|h\mathcal N_h(\tau h^2)^2-\Psi_Q(\tau)^2\right|
 \leq C\bigl(h+\|w^{(h)}-Q\|_1\bigr). }
 \tag{1.6}
\]

These estimates make precise which errors come from the source continuum
collapse, lattice dispersion, finite-cell shape, and carrier position.

## 2. Exact finite model and normalization

Let \(h=1/n\), and let

\[
 x_i=(i+\tfrac12)h,\qquad 0\leq i<n.
\]

On grid densities use

\[
 \langle u,v\rangle_h=h\sum_{i=0}^{n-1}u_iv_i.
\]

Let \(L_n\) be the raw path Laplacian, with diagonal
\((1,2,\ldots,2,1)\) and off-diagonal \(-1\), and put

\[
 A_h=h^{-2}L_n.
\]

The target cosine modes and eigenvalues are

\[
 \varphi_{\ell,h}(i)=\sqrt2\cos(\ell\pi x_i),
 \qquad
 \mu_{\ell,h}=4h^{-2}\sin^2\!\left(\frac{\ell\pi h}{2}\right),
 \quad 1\leq\ell<n.
\]

Let

\[
 0<v_-\leq V(x)\leq v_+,
 \qquad V_h=\operatorname{diag}(V(x_i)).
\]

Take a fixed source port \(\phi\) satisfying

\[
 \int_0^1\phi(x)\,dx=0,
 \qquad \|\phi\|_{L^2(0,1)}=1.
\]

Its grid recovery \(\phi_h\) has exact discrete mean zero, converges to this
same normalized source with \(\|\phi_h-\phi\|_h=O(h)\) under the declared
piecewise-constant identification, and has uniformly bounded discrete first
energy.  Midpoint samples of a smooth Neumann cosine have all three
properties (and are already exactly normalized).  No independent
renormalization of \(\phi_h\) is allowed to change the continuum source that
defines \(F\).  The
reduced scalar response is

\[
 a_{\ell,h}(t)
 =\left\langle1,
 e^{-t(A_h+\mu_{\ell,h}V_h)}\phi_h
 \right\rangle_h.
 \tag{2.1}
\]

For a target probability-mass vector \(q_h\), define

\[
 \beta_{\ell,h}=\sum_iq_{h,i}\varphi_{\ell,h}(i).
\]

The full density-normalized response norm is exactly

\[
 \boxed{
 \mathcal N_h(t)^2
 =\sum_{\ell=1}^{n-1}
 |\beta_{\ell,h}|^2|a_{\ell,h}(t)|^2. }
 \tag{2.2}
\]

No target-band cutoff is present in (2.2).

The high-target-frequency source profile is

\[
 F(s)=\int_0^1e^{-sV(x)}\phi(x)\,dx.
 \tag{2.3}
\]

Since the source has zero mean,

\[
 |F(s)|\leq Cs e^{-v_-s}.
 \tag{2.4}
\]

Define

\[
 C_F^2
 =\int_0^\infty|F(\pi^2r^2)|^2\,dr
 =\frac1{2\pi}\int_0^\infty|F(s)|^2s^{-1/2}\,ds.
 \tag{2.5}
\]

The envelope (2.4) makes this integral finite.  It is positive exactly when
\(F\not\equiv0\).

## 3. Exact carrier decomposition

Choose a carrier cell \(j_h\), extend the local weights by zero, and write

\[
 w_m^{(h)}=q_{h,j_h+m},\qquad
 W_h(\theta)=\sum_{m\in\mathbb Z}w_m^{(h)}e^{im\theta}.
\]

With

\[
 \theta_{\ell,h}=\pi\ell h,
 \qquad y_h=x_{j_h},
\]

the target coefficient is exactly

\[
 \beta_{\ell,h}
 =\sqrt2\operatorname{Re}
 \left[e^{i\ell\pi y_h}W_h(\theta_{\ell,h})\right].
\]

Therefore

\[
 \boxed{
 |\beta_{\ell,h}|^2
 =|W_h(\theta_{\ell,h})|^2
 +\operatorname{Re}\left[
 e^{2i\ell\pi y_h}W_h(\theta_{\ell,h})^2
 \right]. }
 \tag{3.1}
\]

The first term produces the lattice profile.  The second is the carrier
harmonic.  At a fixed interior point it averages away; within distance
\(O(\sqrt t)\) of a reflecting endpoint it does not.

There is a more useful coordinate-free form for the joint atomic theorem.
Let

\[
 \bar y_h=\sum_iq_{h,i}x_i,
 \qquad
 \sigma_h^2=\sum_iq_{h,i}(x_i-\bar y_h)^2,
\]

and set

\[
 \chi_h(k)=\sum_iq_{h,i}e^{ik(x_i-\bar y_h)}.
\]

Then

\[
 \beta_{\ell,h}
 =\sqrt2\operatorname{Re}
 \left[e^{i\pi\ell\bar y_h}\chi_h(\pi\ell)\right],
\]

and centering cancels the linear phase:

\[
 \boxed{
 |\chi_h(k)-1|
 \leq\frac{k^2\sigma_h^2}{2}. }
 \tag{3.2}
\]

This follows directly from
\(|e^{iz}-1-iz|\leq z^2/2\).  On the active band
\(\ell=O(t^{-1/2})\), (3.2) is precisely an
\(O(\sigma_h^2/t)\) error.  This is sharper than a first-moment estimate and
explains why physical variance, rather than nominal mollifier width, is the
right preparation variable in the atomic tail.

## 4. Uniform source collapse

Put

\[
 s_{\ell,h}=t\mu_{\ell,h}
 =\tau\,4\sin^2(\theta_{\ell,h}/2).
\]

Then

\[
 t(A_h+\mu_{\ell,h}V_h)=tA_h+s_{\ell,h}V_h.
\]

Two estimates are needed, and both are uniform over every target mode.

### Lemma 4.1 — modal envelope

If \(\phi_h\) has exact discrete mean zero, then

\[
 \boxed{
 |a_{\ell,h}(t)|
 \leq C s_{\ell,h}e^{-v_-s_{\ell,h}}. }
 \tag{4.1}
\]

#### Proof

Compare \(A_h+\mu V_h\) with
\(A_h+\mu v_-I\).  Since \(A_h1=0\) and
\(\langle1,\phi_h\rangle_h=0\), the scalar response of the comparison
operator is zero.  Duhamel's formula and contractivity give

\[
 |a_{\ell,h}(t)|
 \leq t\mu\|V_h-v_-I\|e^{-v_-t\mu}\|\phi_h\|_h.
\]

This is (4.1). \(\square\)

### Lemma 4.2 — quantitative multiplication limit

Assume \(V,\phi\in W^{1,\infty}(0,1)\), and use a stable midpoint recovery
with exact mean correction.  Uniformly for \(s\geq0\),

\[
 \boxed{
 \left|
 \left\langle1,e^{-(tA_h+sV_h)}\phi_h\right\rangle_h-F(s)
 \right|
 \leq C(\sqrt t+h). }
 \tag{4.2}
\]

Together with (2.4) and (4.1), the left side is also bounded by

\[
 C\min\{\sqrt t+h,\;se^{-v_-s}\}.
 \tag{4.3}
\]

#### Proof

On the unit semigroup interval compare

\[
 u(r)=e^{-r(tA_h+sV_h)}\phi_h,
 \qquad
 v(r)=e^{-rsV_h}\phi_h.
\]

For \(z=u-v\), the discrete energy identity gives

\[
 \frac12\frac d{dr}\|z\|_h^2
 +t\|A_h^{1/2}z\|_h^2
 +s\langle V_hz,z\rangle_h
 =-t\langle A_h^{1/2}v,A_h^{1/2}z\rangle_h.
\]

Young's inequality yields

\[
 \|z(1)\|_h^2
 \leq t\int_0^1\|A_h^{1/2}v(r)\|_h^2\,dr.
\]

The last integral is bounded uniformly in \(h\) and \(s\).  Indeed, the
discrete gradient of \(e^{-rsV_h}\phi_h\) is bounded by a constant times

\[
 e^{-rsv_-}\bigl(1+rs\bigr),
\]

and

\[
 \sup_{s\geq0}\int_0^1
 e^{-2rsv_-}(1+r^2s^2)\,dr<\infty.
\]

Thus \(\|u(1)-v(1)\|_h\leq C\sqrt t\).  Pairing with the unit-norm constant
vector preserves this bound.  Finally, the midpoint sum for
\(e^{-sV}\phi\) differs from its integral by \(O(h)\) uniformly in \(s\):
its total variation is uniformly bounded because
\(s e^{-sv_-}\) is bounded.  The stable mean correction has the same order.
This proves (4.2).  The two separate envelopes give (4.3). \(\square\)

The square-root error is intentionally conservative.  It survives endpoint
incompatibility of \(e^{-sV}\phi\) with the Neumann form domain.  Stronger
compatibility can improve it, but is unnecessary for the joint theorem.

### Lemma 4.3 — envelope accumulation

Let \(G\) be any one of the nonnegative bounded-variation envelopes
\(s^a(1+s)^be^{-cs}\) used below, with fixed nonnegative integers \(a,b\)
and \(c>0\), or let \(G(s)=(1+s)^{-1}\).  If \(\tau\geq1\),
\(t=\tau h^2\), and

\[
 s_{\ell,h}=4\tau\sin^2\!\left(\frac{\pi\ell h}{2}\right),
\]

then

\[
 \boxed{
 \sqrt t\sum_{\ell=1}^{n-1}G(s_{\ell,h})\leq C_G. }
 \tag{4.4}
\]

After the change \(r_\ell=\ell\sqrt t\), the corresponding Riemann-sum
error on a bounded \(r\)-interval is \(O(\sqrt t)\); the declared integrable
tail is uniformly summable.

#### Proof

On \(0\leq\ell\leq n\),
\(\sin(\pi\ell/(2n))\geq\ell/n\), so
\(s_{\ell,h}\geq4t\ell^2=4r_\ell^2\); the reverse bound
\(s_{\ell,h}\leq\pi^2r_\ell^2\) follows from \(\sin z\leq z\).  The
exponential factor therefore controls the entire Brillouin zone.  Comparison
with the integral of a polynomial times \(e^{-4cr^2}\) proves (4.4) for the
exponential envelopes.  For \(G(s)=(1+s)^{-1}\), compare instead with
\((1+4r^2)^{-1}\), which is integrable.  Bounded
variation gives the stated Riemann error. \(\square\)

This lemma is the precise reason a per-mode source error is integrated
against the active diffusive band rather than multiplied by the ambient
number \(n\) of modes.

## 5. Quantitative comparison with the finite-cell chart

For a probability profile \(Q=(Q_m)_{m\in\mathbb Z}\), define

\[
 B_Q(\theta)=\sum_mQ_me^{im\theta},
 \qquad
 \omega(\theta)=4\sin^2(\theta/2),
\]

and

\[
 \boxed{
 \Psi_Q(\tau)^2
 =\frac1\pi\int_0^\pi
 |B_Q(\theta)|^2|F(\tau\omega(\theta))|^2\,d\theta. }
 \tag{5.1}
\]

### Theorem 5.1 — fixed microscopic times, with a rate

Assume:

1. the hypotheses of Lemma 4.2;
2. \(y_h=x_{j_h}\in[d,1-d]\) for some fixed \(d>0\);
3. \(w^{(h)}\) and \(Q\) are probability profiles;
4. \(\delta_h=\|w^{(h)}-Q\|_{\ell^1}\); and
5. their first absolute lattice moments are uniformly bounded.

For every compact \(K\Subset(0,\infty)\), uniformly in \(\tau\in K\),

\[
 \boxed{
 \left|h\mathcal N_h(\tau h^2)^2-\Psi_Q(\tau)^2\right|
 \leq C_{K,d}(h+\delta_h). }
 \tag{5.2}
\]

Consequently

\[
 \left|\sqrt h\,\mathcal N_h(\tau h^2)-\Psi_Q(\tau)\right|
 \leq C_{K,d}(h+\delta_h)^{1/2}.
 \tag{5.3}
\]

If \(\inf_{\tau\in K}\Psi_Q(\tau)>0\), division by the sum of the two
nonnegative norms improves (5.3) to \(O(h+\delta_h)\), both absolutely and
relatively.

#### Proof

Insert (3.1) into (2.2).  Lemma 4.2 replaces every source amplitude by
\(F(\tau\omega(\theta_{\ell,h}))\) with an \(O(h)\) error on a fixed
\(\tau\)-compact set.  The inequality

\[
 \|W_h-B_Q\|_{L^\infty(0,\pi)}\leq\delta_h
\]

replaces the local preparation.  The nonoscillatory sum is a Riemann sum for
(5.1).  Its integrand has uniformly bounded variation because the first
lattice moments bound \(B_Q'\).

For the carrier term, the partial geometric sums of
\(e^{2\pi i\ell y_h}\) satisfy

\[
 \sup_M\left|\sum_{\ell=1}^M e^{2\pi i\ell y_h}\right|
 \leq\frac1{|\sin(\pi y_h)|}
 \leq C_d.
\]

Abel summation therefore bounds the carrier term, after multiplication by
\(h\), by \(Ch\) times the bounded variation of its slowly varying weight.
This proves (5.2). \(\square\)

### Theorem 5.2 — one estimate from the lattice chart into its tail

Under the same assumptions, take \(\tau\geq1\), put \(t=\tau h^2\), and
assume \(t\leq t_*\).  Then

\[
 \boxed{
 \sqrt\tau\left|
 h\mathcal N_h(t)^2-\Psi_Q(\tau)^2
 \right|
 \leq C\left(
 \sqrt t+h+\delta_h+\frac{\sqrt t}{d}
 \right). }
 \tag{5.4}
\]

The constant is independent of \(h,t,\tau\) in the displayed range.

#### Why the constant stays uniform

The active angular interval has width \(O(\tau^{-1/2})\).  After
\(r=\sqrt\tau\,\theta/\pi\), the modal envelope is a fixed integrable
function of \(r\).  Thus:

- the source-collapse error contributes \(O(\sqrt t+h)\);
- the profile mismatch contributes \(O(\delta_h)\);
- the shrinking Riemann mesh has size
  \(h\sqrt\tau=\sqrt t\); and
- Abel summation of the carrier harmonic contributes
  \(O(\sqrt t/d)\).

The exponential envelope controls the remainder of the Brillouin zone.
This proves (5.4) by the same decomposition as Theorem 5.1, now in the
rescaled coordinate. \(\square\)

Theorem 5.2 is an absolute squared-profile estimate.  It must not be turned
into a relative norm estimate where \(\Psi_Q\) is zero or very small.

### Corollary 5.3 — the requested norm comparison

Assume additionally that \(F\not\equiv0\), that \(Q\) has finite variance,
and that the right side below tends to zero.  Then, uniformly for
\(\tau\geq1\) with \(t=\tau h^2\to0\),

\[
 \boxed{
 \mathcal N_h(t)
 =h^{-1/2}\Psi_Q(\tau)
 \left[1+O\!\left(
 \sqrt t+h+\delta_h+\frac{\sqrt t}{d}
 \right)\right]. }
 \tag{5.5}
\]

Indeed, \(F\) is analytic, \(B_Q(0)=1\), and \(F\not\equiv0\), so
\(\Psi_Q(\tau)>0\) for every \(\tau>0\).  Moreover,
\(\sqrt\tau\,\Psi_Q(\tau)^2\) is continuous and tends to \(C_F^2>0\) by
Proposition 6.1.  It is therefore bounded away from zero on
\([1,\infty)\).  Divide (5.4) by
\(\sqrt\tau\Psi_Q^2\), and then take the square root.  This is the direct
finite-discrete versus \(h^{-1/2}\Psi_Q(t/h^2)\) comparison; the assumption
\(F\not\equiv0\) is what makes its relative form legitimate.

## 6. Quantitative large-time tail of the lattice phase

Let

\[
 \bar m_Q=\sum_m mQ_m,
 \qquad
 \operatorname{Var}(Q)=\sum_m(m-\bar m_Q)^2Q_m<\infty.
\]

Centering the characteristic function gives

\[
 0\leq1-|B_Q(\theta)|^2
 \leq \operatorname{Var}(Q)\theta^2.
 \tag{6.1}
\]

Indeed, \(|B_Q|^2\) is the characteristic function of the difference of two
independent copies of \(Q\), whose second moment is
\(2\operatorname{Var}(Q)\).

### Proposition 6.1 — quantitative forgetting of lattice phase

If \(Q\) has finite variance, then for \(\tau\geq1\),

\[
 \boxed{
 \left|\sqrt\tau\,\Psi_Q(\tau)^2-C_F^2\right|
 \leq C\frac{1+\operatorname{Var}(Q)}{\tau}. }
 \tag{6.2}
\]

#### Proof

Set \(\theta=\pi r/\sqrt\tau\).  Then

\[
 \sqrt\tau\,\Psi_Q(\tau)^2
 =\int_0^{\sqrt\tau}
 \left|B_Q\!\left(\frac{\pi r}{\sqrt\tau}\right)\right|^2
 \left|F\!\left(
 4\tau\sin^2\frac{\pi r}{2\sqrt\tau}
 \right)\right|^2dr.
 \tag{6.3}
\]

Equation (6.1) contributes
\(O(\operatorname{Var}(Q)/\tau)\) after integration against the Gaussian
envelope.  Taylor's theorem gives

\[
 4\tau\sin^2\frac{\pi r}{2\sqrt\tau}
 =\pi^2r^2+O(r^4/\tau).
\]

The derivative of \(|F|^2\) has an exponential envelope, so lattice
dispersion contributes \(O(\tau^{-1})\).  The omitted tail
\(r>\sqrt\tau\) is exponentially small.  The remaining integral is (2.5).
\(\square\)

The \(\operatorname{Var}(Q)/\tau\) term is the dimensionless form of

\[
 \frac{h^2\operatorname{Var}(Q)}t
 =\frac{\text{physical target variance}}{t}.
\]

This is the precise sense in which diffusion forgets finite-cell placement.

## 7. Direct joint atomic theorem

The fixed profile \(Q\) is useful at \(t\asymp h^2\), but it is unnecessary
once the preparation is much narrower than \(\sqrt t\).

### Theorem 7.1 — interior joint atomic tail

Assume the hypotheses of Lemma 4.2 and exact discrete source mean zero.  Let

\[
 h\downarrow0,\qquad t_h\downarrow0,\qquad
 \tau_h=t_h/h^2\longrightarrow\infty.
\]

For an arbitrary target probability vector \(q_h\), define its physical mean,
variance, and boundary distance by

\[
 \bar y_h=\sum_iq_{h,i}x_i,
 \qquad
 \sigma_h^2=\sum_iq_{h,i}(x_i-\bar y_h)^2,
 \qquad
 d_h=\min\{\bar y_h,1-\bar y_h\}.
\]

If

\[
 \frac{\sigma_h^2}{t_h}\to0,
 \qquad
 \frac{d_h}{\sqrt{t_h}}\to\infty,
 \tag{7.1}
\]

then

\[
 \boxed{
 \sqrt{t_h}\,\mathcal N_h(t_h)^2\longrightarrow C_F^2. }
 \tag{7.2}
\]

More quantitatively, for \(\tau\geq1\), \(0<t\leq t_*\), sufficiently fine
grids, and \(d_h>0\),

\[
 \boxed{
 \left|\sqrt t\,\mathcal N_h(t)^2-C_F^2\right|
 \leq C\left(
 \sqrt t+h+\frac1\tau+\frac{\sigma_h^2}{t}
 +\frac{\sqrt t}{d_h}
 \right). }
 \tag{7.3}
\]

If \(C_F>0\), (7.2) implies

\[
 \mathcal N_h(t_h)\sim C_Ft_h^{-1/4}.
\]

If \(C_F=0\), (7.2) is only the normalized profile limit
\(\sqrt t\mathcal N_h^2\to0\); asymptotic equivalence to
\(C_Ft^{-1/4}\) is meaningless.

#### Proof

Put \(r_\ell=\ell\sqrt t\).  The spacing of this rescaled modal lattice is
\(\sqrt t\), and

\[
 s_{\ell,h}
 =4\tau\sin^2\!\left(\frac{\pi r_\ell}{2\sqrt\tau}\right)
 =\pi^2r_\ell^2+O(r_\ell^4/\tau)
\]

on bounded \(r\)-intervals.  Lemmas 4.1--4.2, with (4.3), replace the
discrete reduced amplitude by \(F(s_{\ell,h})\).  After multiplication by
the modal spacing \(\sqrt t\), the total error is
\(O(\sqrt t+h)\), not the number of modes times that quantity: the envelope
localizes the sum to an integrable function of \(r\).

Using the barycentric carrier decomposition and (3.2), the target shape
contributes \(O(\sigma_h^2/t)\).  Replacing the lattice symbol by
\(\pi^2r^2\) contributes \(O(\tau^{-1})\).  The nonoscillatory Riemann sum
then converges to (2.5), with error \(O(\sqrt t)\).

The remaining pure carrier term is

\[
 \sqrt t\sum_{\ell=1}^{n-1}
 e^{2\pi i\ell\bar y_h}|F(\pi^2r_\ell^2)|^2.
\]

The weight has uniformly bounded total variation.  Abel summation and

\[
 \sup_M\left|\sum_{\ell=1}^Me^{2\pi i\ell\bar y_h}\right|
 \leq\frac1{|\sin(\pi\bar y_h)|}
 \leq\frac C{d_h}
\]

bound this term by \(C\sqrt t/d_h\).  Combining the five errors proves
(7.3) and hence (7.2). \(\square\)

### Corollary 7.2 — finite-cell preparations

Suppose \(q_h\) is localized on lattice offsets whose centered variance is
bounded by \(M\).  Then

\[
 \sigma_h^2\leq Mh^2,
 \qquad
 \frac{\sigma_h^2}{t}\leq\frac M\tau.
\]

Every fixed-width cell-average mollifier, one-cell atom, nearest-cell atom,
and fixed split rule therefore satisfies Theorem 7.1 whenever its barycentre
remains interior.  Its finite-\(\tau\) lattice phase survives in
\(\Psi_Q(\tau)\), but it is quantitatively erased at rate \(O(\tau^{-1})\)
in the squared atomic profile.

## 8. Reflecting-boundary layer

The condition \(d_h/\sqrt t\to\infty\) is sharp for the interior constant.
Suppose instead that

\[
 \frac{d_h}{\sqrt t}\longrightarrow\kappa\in[0,\infty),
 \qquad
 \frac{\sigma_h^2}{t}\longrightarrow0,
\]

and the barycentre approaches either endpoint.  Then the carrier harmonic no
longer averages away.  The same proof, now using an ordinary Riemann sum for
the carrier, gives

\[
 \boxed{
 \sqrt t\,\mathcal N_h(t)^2
 \longrightarrow C_{F,\kappa}^2, }
 \tag{8.1}
\]

where

\[
 \boxed{
 C_{F,\kappa}^2
 =\int_0^\infty
 \bigl[1+\cos(2\pi\kappa r)\bigr]
 |F(\pi^2r^2)|^2\,dr. }
 \tag{8.2}
\]

The convention \(\kappa=\infty\) recovers the interior constant by the
Riemann--Lebesgue lemma.  At the endpoint itself,

\[
 C_{F,0}^2=2C_F^2.
\]

Thus an endpoint atom has a norm constant \(\sqrt2\) times the interior
constant.  This is a reflecting-image effect, not a defect of the lattice
approximation.  If \(d_h/\sqrt t\) has no limit, different subsequences can
have different boundary-layer constants.

## 9. Complete high-frequency cancellation

The condition \(F\not\equiv0\) cannot be omitted from an asymptotic norm
claim.

### Proposition 9.1 — the \(F\equiv0\) control

If

\[
 F(s)=\int_0^1e^{-sV}\phi=0
 \qquad\text{for every }s\geq0,
\]

then \(C_F=0\) and \(\Psi_Q(\tau)=0\) for every \(Q\) and \(\tau\).  Under
the joint hypotheses of Theorem 7.1,

\[
 \sqrt t\,\mathcal N_h(t)^2\longrightarrow0.
\]

The form estimate yields the stronger general upper bound

\[
 \boxed{\sqrt t\,\mathcal N_h(t)^2\leq C(t+h^2)=O(t),}
 \tag{9.1}
\]

because \(h=o(\sqrt t)\).  Equivalently,

\[
 \mathcal N_h(t)=O(t^{1/4}).
\]

To obtain (9.1), retain the decay that was deliberately discarded in the
uniform statement of Lemma 4.2.  Its energy proof actually gives

\[
 \left\|e^{-(tA_h+sV_h)}\phi_h-e^{-sV_h}\phi_h\right\|_h
 \leq C\sqrt{\frac{t}{1+s}},
 \tag{9.2}
\]

because

\[
 \int_0^1e^{-2rsv_-}(1+rs)^2\,dr\leq\frac{C}{1+s}.
\]

When \(F\equiv0\), the midpoint/mean-corrected recovery also satisfies

\[
 \left|\langle1,e^{-sV_h}\phi_h\rangle_h\right|
 \leq Ch(1+s)e^{-v_-s}.
 \tag{9.3}
\]

Squaring (9.2)--(9.3), multiplying the modal sum by \(\sqrt t\), and applying
Lemma 4.3 yields \(C(t+h^2)\).  Thus the displayed rate uses a weighted
form estimate; it would not follow merely by squaring the coarser uniform
\(O(\sqrt t+h)\) bound.

This does not say that the finite response is identically zero.  Mixed words
containing source diffusion and multiplication can survive below the
high-frequency profile retained by \(F\).  Exact zero response follows only
from an additional invariant symmetry that is also preserved by the grid.
There is no universal next coefficient after \(F\equiv0\) without specifying
that mixed causal structure.

## 10. Cell averages and subcell phase

Let a line mollifier \(\eta\) of width \(\varepsilon_h\) be converted to
probability masses by exact cell integration.  Write

\[
 c_h=\frac{\varepsilon_h}{h},
 \qquad
 \alpha_h=\frac{y_h^*}{h}-\left\lfloor\frac{y_h^*}{h}\right\rfloor.
\]

If

\[
 c_h\to c\in(0,\infty),\qquad \alpha_h\to\alpha,
\]

then the local weights converge in \(\ell^1\) to

\[
 Q_m^{c,\alpha}
 =\int_{(m-\alpha)/c}^{(m+1-\alpha)/c}\eta(z)\,dz.
 \tag{10.1}
\]

For a Lipschitz, rapidly decaying mollifier the convergence is quantitative:
away from the physical boundary,

\[
 \|w^{(h)}-Q^{c,\alpha}\|_1
 \leq C\bigl(|c_h-c|+|\alpha_h-\alpha|\bigr)
 +\text{truncation tail}.
 \tag{10.2}
\]

Substitution in Theorem 5.1 gives a complete finite-\(\tau\) error bound.
If \(\alpha_h\) has no limit, there is generally no unique finite-\(\tau\)
profile.  This obstruction is real: an atom in a cell interior and an equal
split at a cell boundary have different \(|B_Q(\theta)|^2\).

For \(\tau\to\infty\), however, every such fixed-\(c\) profile has bounded
lattice variance and therefore satisfies Theorem 7.1.  The subcell phase is
erased because

\[
 \frac{\text{physical variance}}t=O(\tau^{-1}).
\]

The order of statements matters:

\[
 \begin{array}{ccl}
 \tau\to\tau_0\in(0,\infty)
 &:& \text{the limiting lattice phase must be declared},\\[2mm]
 \tau\to\infty
 &:& \text{only mass, barycentre layer, and variance/}t\text{ survive}.
 \end{array}
\]

## 11. Mean leakage and other sharp obstructions

The hypotheses above are not cosmetic.

### 11.1 Exact source centering

The discrete proof uses

\[
 \langle1,\phi_h\rangle_h=0
\]

in the envelope (4.1).  If the leakage is \(\zeta_h\), an atom has roughly
\(t^{-1/2}\) active target modes, each of which can retain an
\(O(\zeta_h)\) component.  The scaled squared response can therefore acquire
an \(O(\zeta_h^2)\) term.  Exact centering is available in the declared
protocol and should be enforced rather than inferred from an asymptotic
quadrature rule.

### 11.2 Mesh diffusion must be resolved

If \(t/h^2\) remains finite, the symbol

\[
 4\sin^2(\theta/2)
\]

does not reduce to \(\theta^2\).  The answer is \(\Psi_Q(\tau)\), not the
continuum atomic constant.

### 11.3 Time must still approach zero

If \(t\) stays positive while \(h\to0\), source diffusion does not collapse
to multiplication.  One obtains the fixed-positive-time continuum atomic
response from Stage VII, not the small-time constant \(C_F\).

### 11.4 Preparation variance must be smaller than diffusion length squared

If \(\sigma_h^2/t\) has a nonzero limit, the preparation remains visible at
the \(\sqrt t\) scale.  Its rescaled characteristic function enters the
limit; calling it an atom loses information.

### 11.5 The carrier must be classified relative to \(\sqrt t\)

Fixed physical interior location gives the carrier average used in (1.3).
Distance \(O(\sqrt t)\) from a reflector gives (8.2).  Location convergence
without this scale comparison is insufficient.

### 11.6 No universal rate follows from tightness alone

Uniform tightness, or bare \(\ell^1\) convergence
\(w^{(h)}\to Q\), proves convergence but supplies no numerical rate: either
can be arbitrarily slow.  The explicit \(O(h+\delta_h)\) estimate retains
\(\delta_h\), while the atomic estimate uses a second moment.  Removing both
quantities would make a rate statement false.

### 11.7 Squared absolute error is the stable object

Neither (5.2) nor (7.3) can be converted uniformly to a relative norm bound
near a zero of the limiting profile.  In particular, when \(F\equiv0\), the
leading lattice chart is identically zero even though diffusion--modulation
commutators can produce a smaller finite response.

## 12. Falsification ledger

| Tempting statement | Status and correction |
|---|---|
| every \(\varepsilon/h=O(1)\) sequence has one finite-\(\tau\) limit | false; the subcell phase can select different \(Q\)'s |
| the phase of a finite-cell preparation survives for all \(\tau\) | false; its squared-profile error is \(O(\operatorname{Var}(Q)/\tau)\) |
| \(t/h^2\to\infty\) alone gives the interior atomic law | false; also require \(t\to0\), width \(o(\sqrt t)\), and interior distance \(\gg\sqrt t\) |
| every atom has the same constant | false near a reflecting endpoint; (8.2) interpolates to twice the squared interior constant |
| \(\sqrt t\mathcal N_h^2\to C_F^2\) always means \(\mathcal N_h\sim C_Ft^{-1/4}\) | false when \(C_F=0\) |
| \(F\equiv0\) forces every finite response to vanish | false without an exact invariant symmetry |
| bare tightness gives an \(O(h)\) rate | false; a moment or explicit \(\ell^1\) modulus is required |
| approximate mean zero is harmless on every joint path | false without a rate; enforce exact discrete centering |

## 13. What is genuinely new at this stage

Within the declared model, this memo upgrades three iterated or qualitative
statements from Stage VII:

1. the fixed-\(\tau\) mesoscopic convergence now has an explicit
   \(O(h+\ell^1\text{-profile error})\) squared-profile bound;
2. one estimate, (5.4), remains valid while \(\tau\) grows from the lattice
   chart into the continuum atomic tail; and
3. the iterated large-\(\tau\) law is promoted to the simultaneous theorem
   (7.2) for every path with
   \(h^2\ll t\ll1\), target variance \(o(t)\), and boundary distance
   \(\gg\sqrt t\).

The boundary profile (8.2) identifies the sharp geometric obstruction to an
unqualified interior theorem.  The cancellation control in Section 9
identifies the sharp source-side obstruction to dividing by the atomic
constant.

## 14. Remaining lattice-side targets

The natural next tasks are narrower than the original three-parameter gap:

1. prove an optimal \(O(t)\), rather than energy-level \(O(\sqrt t)\), source
   collapse under explicit Neumann compatibility conditions;
2. classify the first nonzero mixed diffusion--multiplication profile when
   \(F\equiv0\);
3. allow a nontrivial target shape at the \(\sqrt t\) scale and derive the
   resulting boundary-plus-mollifier transform;
4. extend the variance theorem to nonuniform reversible meshes through their
   local symbols and heat-kernel bounds; and
5. turn (7.3) into a machine-checked interval certificate for representative
   finite grids without confusing numerical enclosure with proof of the
   asymptotic theorem.

The main finite-cell-to-atomic transition itself no longer requires an
iterated limit.
