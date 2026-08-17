# Operational Information Geometry VII

## The continuum mollifier phase diagram

- **Research lane:** analytic singular-preparation limit
- **Date:** 14 August 2026
- **Status:** self-contained proof memo; not peer reviewed
- **Scope:** the fixed-domain one-way rate-modulated Neumann path model
- **Predecessors:** OPERATIONAL_INFORMATION_GEOMETRY_V.md and
  OPERATIONAL_INFORMATION_GEOMETRY_VI.md

## 1. Result in one paragraph

Let a smooth target preparation of width \(\varepsilon\) concentrate at a
fixed interior point, and let \(t\downarrow0\). The full target-mode norm of
the response to a fixed source cosine has the crossover law whenever
\(\mathcal P_k(q)>0\):

\[
 \mathcal N_{\varepsilon,k}(q\varepsilon^2)
 \sim \varepsilon^{-1/2}\mathcal P_k(q).
\]

The profile is not phenomenological. If

\[
 V(x)=1+g d(x),\qquad
 F_k(s)=\int_0^1e^{-sV(x)}\phi_k(x)\,dx,
\]

then

\[
 \mathcal P_k(q)^2
 =\int_0^\infty
   |\widehat\eta(\pi u)|^2
   |F_k(\pi^2q u^2)|^2\,du.
\]

This formula keeps the full finite coupling \(g\); no weak-coupling
linearization is used. If

\[
 r_*=\min\left\{r\geq1:
 \int_0^1V(x)^r\phi_k(x)\,dx\neq0\right\},
\]

then

\[
 \mathcal P_k(q)\sim
 \frac{\left|\int V^{r_*}\phi_k\right|}{r_*!}
 \|\eta^{(2r_*)}\|_2 q^{r_*}
 \quad(q\downarrow0),
\]

whereas, whenever \(F_k\not\equiv0\),

\[
 \mathcal P_k(q)\sim C_{F,k}q^{-1/4}
 \quad(q\to\infty).
\]

Thus the generic early response is
\(t\varepsilon^{-5/2}\), while after heat has resolved the preparation width
it is \(t^{-1/4}\) and independent of the mollifier shape to leading order.
For the canonical ramp \(V=1+gx\), odd source modes have \(r_*=1\), but even
source modes have \(r_*=2\). At microscopic time \(t=\tau h^2\) and resolved
width \(\varepsilon=h^\alpha\), their critical exponents are respectively
\(\alpha=4/5\) and \(\alpha=8/9\).

At \(\varepsilon/h=O(1)\), the continuum profile is replaced by an explicit
lattice profile depending on the cell-mass rule and, along subsequences, the
subcell phase of the carrier. When \(\varepsilon/h\to0\), a conservative
preparation becomes an atom and the microscopic response is
\(h^{-1/2}\mathcal P^{\rm lat}(\tau)\). The lattice profile has the same
\(\tau^{-1/4}\) large-time tail, so the continuum and atomic regimes match
once \(t/h^2\to\infty\).

## 2. Continuum model and exact response norm

Let

\[
 A=-\frac{d^2}{dx^2}
\]

be the nonnegative Neumann Laplacian on \(L^2(0,1)\). Assume

\[
 V\in L^\infty(0,1),\qquad
 0<a\leq V(x)\leq b<\infty.
\]

In the OIG model \(V=1+gd\). Fix a nonconstant source cosine

\[
 \phi_k(x)=\sqrt2\cos(k\pi x),\qquad k\geq1.
\]

For target mode \(\ell\geq1\), put

\[
 \nu_\ell=(\ell\pi)^2,\qquad
 K_\ell=A+\nu_\ell M_V,
\]

and define the reduced scalar response

\[
 a_{\ell k}(t)
 =\left\langle1,e^{-tK_\ell}\phi_k\right\rangle_{L^2}.
\]

Choose a nonnegative even mollifier

\[
 \eta\in C_c^\infty(-R,R),\qquad
 \int_{\mathbb R}\eta(z)\,dz=1.
\]

Fix \(y_0\in(0,1)\). For
\(\varepsilon<\operatorname{dist}(y_0,\{0,1\})/R\), set

\[
 \rho_\varepsilon(y)
 =\varepsilon^{-1}
  \eta\!\left(\frac{y-y_0}{\varepsilon}\right).
\]

With the Fourier convention

\[
 \widehat\eta(\xi)
 =\int_{\mathbb R}\eta(z)e^{-i\xi z}\,dz,
\]

evenness gives the exact coefficient formula

\[
 \beta_\ell(\varepsilon)
 =\langle\phi_\ell,\rho_\varepsilon\rangle
 =\sqrt2\cos(\ell\pi y_0)
   \widehat\eta(\ell\pi\varepsilon).
\]

The full density-normalized target response norm is

\[
 \boxed{
 \mathcal N_{\varepsilon,k}(t)^2
 =\sum_{\ell=1}^{\infty}
  |\beta_\ell(\varepsilon)|^2
  |a_{\ell k}(t)|^2.}
\]

This is the \(L^2\) norm of the nonstationary target marginal response,
expressed in its orthonormal Neumann cosine basis. It is a growing-band
quantity. No fixed-band theorem can see its singular scaling.

## 3. Two estimates that control every mode

### Lemma 3.1 — a uniform response envelope

For every \(\ell\geq1\) and \(t\geq0\),

\[
 |a_{\ell k}(t)|
 \leq
 \nu_\ell t\,\|V-a\|_\infty e^{-a\nu_\ell t}.
\]

#### Proof

Let

\[
 H_\ell=A+\nu_\ell V,\qquad
 H_{\ell,0}=A+\nu_\ell a.
\]

Because \(A1=0\) and \(\langle1,\phi_k\rangle=0\),

\[
 \langle1,e^{-tH_{\ell,0}}\phi_k\rangle=0.
\]

Duhamel's formula gives

\[
 e^{-tH_\ell}-e^{-tH_{\ell,0}}
 =-\nu_\ell\int_0^t
 e^{-(t-r)H_\ell}(V-a)e^{-rH_{\ell,0}}\,dr.
\]

The two semigroups have norms at most
\(e^{-a\nu_\ell(t-r)}\) and \(e^{-a\nu_\ell r}\), respectively.
Taking the matrix element between \(1\) and \(\phi_k\), both of norm one,
proves the estimate. \(\square\)

The envelope has the crucial form

\[
 C\,s e^{-as},\qquad s=t\nu_\ell.
\]

It both removes the stationary cancellation at \(s=0\) and supplies a
Gaussian summable tail in \(\ell\).

### Lemma 3.2 — full-coupling high-frequency rescaling

If \(\ell_j\to\infty\) and \(t_j\nu_{\ell_j}\to s\in[0,\infty)\), then

\[
 a_{\ell_j k}(t_j)\longrightarrow F_k(s),
\]

where

\[
 \boxed{
 F_k(s)=\int_0^1e^{-sV(x)}\phi_k(x)\,dx.}
\]

The convergence is uniform when \(s\) ranges over a fixed compact interval.

#### Proof

Write

\[
 \delta_\ell=\nu_\ell^{-1},\qquad
 tK_\ell=s(\delta_\ell A+V).
\]

The closed forms

\[
 \mathfrak b_\delta(u)
 =\delta\int_0^1|u'|^2dx+\int_0^1V|u|^2dx,
\qquad D(\mathfrak b_\delta)=H^1(0,1),
\]

Mosco-converge as \(\delta\downarrow0\) to the bounded multiplication form

\[
 \mathfrak b_0(u)=\int_0^1V|u|^2dx,
\qquad D(\mathfrak b_0)=L^2(0,1).
\]

The liminf follows by dropping the nonnegative derivative term. For recovery,
approximate an arbitrary \(L^2\) function by a smooth function and choose the
approximation diagonally so that
\(\delta\|u_\delta'\|_2^2\to0\). Hence

\[
 e^{-s(\delta A+V)}f\longrightarrow e^{-sV}f
\]

strongly, locally uniformly in \(s\geq0\). Taking the matrix element between
\(1\) and \(\phi_k\) proves the claim. \(\square\)

This is the step that validates \(F_k\) at full finite \(g\). Replacing
\(F_k\) by its first term in \(g\) is neither necessary nor generally
accurate.

## 4. The balanced mollifier theorem

### Theorem 4.1 — the \(t/\varepsilon^2\) crossover

For every fixed \(q\in(0,\infty)\),

\[
 \boxed{
 \lim_{\varepsilon\downarrow0}
 \varepsilon\,
 \mathcal N_{\varepsilon,k}(q\varepsilon^2)^2
 =\mathcal P_k(q)^2,}
\]

where

\[
 \boxed{
 \mathcal P_k(q)^2
 =\int_0^\infty
 |\widehat\eta(\pi u)|^2
 |F_k(\pi^2q u^2)|^2\,du.}
\]

Equivalently, if \(\mathcal P_k(q)>0\),

\[
 \mathcal N_{\varepsilon,k}(q\varepsilon^2)
 \sim\varepsilon^{-1/2}\mathcal P_k(q).
\]

#### Proof

Put \(u_\ell=\varepsilon\ell\). The exact coefficient formula gives

\[
 \begin{aligned}
 \varepsilon\mathcal N_{\varepsilon,k}(q\varepsilon^2)^2
 ={}&\varepsilon\sum_{\ell\geq1}
 2\cos^2(\ell\pi y_0)
 |\widehat\eta(\pi u_\ell)|^2\\
 &\hspace{32mm}\cdot
 |a_{\ell k}(q\varepsilon^2)|^2.
 \end{aligned}
\]

For every fixed \(u>0\), a sequence with
\(\varepsilon\ell\to u\) satisfies

\[
 q\varepsilon^2\nu_\ell
 \longrightarrow\pi^2q u^2,
\]

so Lemma 3.2 gives

\[
 a_{\ell k}(q\varepsilon^2)
 \longrightarrow F_k(\pi^2q u^2).
\]

Lemma 3.1 bounds the squared summand by

\[
 C_q u^4e^{-2a\pi^2q u^2}.
\]

This is integrable, and \(\widehat\eta\) is bounded. A compact-plus-tail
Riemann-sum argument therefore replaces the response amplitude by its limit.

Finally,

\[
 2\cos^2(\ell\pi y_0)
 =1+\cos(2\ell\pi y_0).
\]

The compact-plus-tail argument can be expressed by rescaled squared-weight
step functions. They converge in \(L^1(0,\infty)\) to the displayed limiting
integrand: pointwise convergence holds on compact sets by Lemma 3.2, while
Lemma 3.1 gives a common integrable tail. Approximate that limit in \(L^1\) by
a smooth compactly supported function. Bounded geometric partial sums, or
equivalently the Riemann--Lebesgue lemma for the approximation, then show that
the second carrier harmonic tends to zero. The nonoscillatory term gives the
displayed integral. This proves the theorem.
\(\square\)

The phase averaging is a statement about the complete modal sum. It does not
say that \(\cos^2(\ell\pi y_0)\) converges to \(1/2\) mode by mode.

### Boundary-carrier warning

The interior assumption is material, and the mollifier declared in Section 2
is not admissible unchanged at \(y_0=0\) or \(1\). Restricting an even kernel
to the interval without renormalization leaves mass \(1/2\) and produces one
half of the interior squared profile. Renormalizing the half-kernel by two, or
using its Neumann-reflected convention, produces twice the interior squared
profile. More generally, when
\(y_0=y_0(\varepsilon)\) and
\(y_0/\varepsilon\to\gamma\), the limiting weight contains the normalized
one-sided truncated Fourier transform as well as the carrier phase. It is not
obtained by inserting only \(2\cos^2(\pi\gamma u)\) into the interior formula.
Theorem 4.1 deliberately excludes this boundary layer.

## 5. Exact asymptotics of the crossover profile

Put

\[
 m_{r,k}=\int_0^1V(x)^r\phi_k(x)\,dx,\qquad r\geq0.
\]

Since \(m_{0,k}=0\), define

\[
 r_*=\min\{r\geq1:m_{r,k}\neq0\},
\]

when this set is nonempty.

### Theorem 5.1 — early side of the crossover

If \(r_*<\infty\), then

\[
 \boxed{
 \mathcal P_k(q)
 \sim
 \frac{|m_{r_*,k}|}{r_*!}
 \|\eta^{(2r_*)}\|_{L^2(\mathbb R)}
 q^{r_*}
 \qquad(q\downarrow0).}
\]

#### Proof

Because \(V\) is bounded,

\[
 F_k(s)
 =\sum_{r=1}^{\infty}
 \frac{(-s)^r}{r!}m_{r,k}.
\]

Thus

\[
 F_k(s)
 =\frac{(-s)^{r_*}}{r_*!}m_{r_*,k}
 +O(s^{r_*+1}).
\]

The same Taylor remainder, together with boundedness for \(s\geq1\), gives a
global bound \(|F_k(s)|\leq C s^{r_*}\). Dominated convergence in the
definition of \(\mathcal P_k\) yields

\[
 \lim_{q\downarrow0}
 \frac{\mathcal P_k(q)^2}{q^{2r_*}}
 =
 \frac{|m_{r_*,k}|^2}{(r_*!)^2}
 \pi^{4r_*}
 \int_0^\infty
 u^{4r_*}|\widehat\eta(\pi u)|^2\,du.
\]

With the declared Fourier convention, Plancherel gives

\[
 \pi^{4r_*}
 \int_0^\infty
 u^{4r_*}|\widehat\eta(\pi u)|^2\,du
 =\|\eta^{(2r_*)}\|_2^2.
\]

Taking square roots proves the claim. \(\square\)

The often-anticipated linear law

\[
 \mathcal P_k(q)\sim Cq
\]

is therefore generic, but not universal: it requires \(m_{1,k}\neq0\).

### Theorem 5.2 — late side of the crossover

If \(F_k\not\equiv0\), then

\[
 \boxed{
 \mathcal P_k(q)\sim C_{F,k}q^{-1/4}
 \qquad(q\to\infty),}
\]

where

\[
 C_{F,k}^2
 =\int_0^\infty|F_k(\pi^2r^2)|^2\,dr
 =\frac1{2\pi}\int_0^\infty
 |F_k(s)|^2s^{-1/2}\,ds.
\]

The constant is finite and strictly positive.

#### Proof

After \(r=\sqrt q\,u\),

\[
 q^{1/2}\mathcal P_k(q)^2
 =\int_0^\infty
 \left|\widehat\eta\!\left(\frac{\pi r}{\sqrt q}\right)\right|^2
 |F_k(\pi^2r^2)|^2\,dr.
\]

Since \(\widehat\eta(0)=1\), the integrand converges pointwise to
\(|F_k(\pi^2r^2)|^2\). Lemma 3.1 in its multiplication limit gives

\[
 |F_k(s)|\leq Cse^{-as},
\]

which is square-integrable after \(s=\pi^2r^2\).
Dominated convergence proves the first identity and the asymptotic.
\(\square\)

The large-\(q\) coefficient is independent of the mollifier shape. At these
times the relevant target wavelengths are of order \(\sqrt t\), much larger
than \(\varepsilon\), so the preparation is seen only through its unit mass.

### Complete cancellation

If \(m_{r,k}=0\) for every \(r\geq1\), then the entire function \(F_k\)
vanishes identically and \(\mathcal P_k\equiv0\). This can happen through an
exact symmetry. It does not, by itself, prove that every finite-\(\ell\)
response vanishes: diffusion-potential commutators can live below the
high-frequency scaling retained here. If both \(V\) and the Neumann problem
have a reflection symmetry and \(\phi_k\) lies in the odd sector, then the
full response is indeed identically zero.

## 6. The three continuum time-width regimes

Theorems 4.1 and 5.1--5.2 give the following phase diagram.

### 6.1 Early preparation-resolved layer: \(t/\varepsilon^2\to0\)

As an iterated consequence of the profile theorem, and as a joint statement
under the conditions separated below, when the first nonzero multiplication
moment has order \(r_*\),

\[
 \mathcal N_{\varepsilon,k}(t)
 \asymp
 t^{r_*}\varepsilon^{-(2r_*+1/2)}.
\]

For the generic case \(r_*=1\),

\[
 \boxed{
 \mathcal N_{\varepsilon,k}(t)
 \sim
 |m_{1,k}|\|\eta''\|_2\,
 t\varepsilon^{-5/2}.}
\]

This is exactly the \(L^2\) size of the first response jet. The power
\(\varepsilon^{-5/2}\) consists of two target derivatives
\(\varepsilon^{-2}\) and the \(L^2\) concentration factor
\(\varepsilon^{-1/2}\).

For \(r_*=1\), the displayed asymptotic is valid as a genuine joint limit,
not merely as an iterated reading of Theorem 4.1. Indeed, with

\[
 B_\delta=\delta A+V,\qquad s=t\nu_\ell,
\]

the scalar function

\[
 f_\delta(s)=\langle1,e^{-sB_\delta}\phi_k\rangle
\]

satisfies

\[
 f_\delta'(0)=-m_{1,k}
\]

and

\[
 |f_\delta''(s)|
 =
 |\langle B_\delta1,e^{-sB_\delta}B_\delta\phi_k\rangle|
 \leq C
\]

uniformly for \(0<\delta\leq\pi^{-2}\). Hence

\[
 |a_{\ell k}(t)+m_{1,k}t\nu_\ell|
 \leq C(t\nu_\ell)^2.
\]

The Schwartz decay of \(\widehat\eta\) then makes the response-vector
remainder \(O(t^2\varepsilon^{-9/2})\), smaller than the leading norm by the
factor \(t/\varepsilon^2\).

For \(r_*=2\), assume in addition that \(V\in W^{1,\infty}(0,1)\). The same
genuine joint conclusion then holds. The first two scalar derivatives are

\[
 f_\delta'(0)=-m_{1,k},
\qquad
 f_\delta''(0)=m_{2,k}+\delta(k\pi)^2m_{1,k}.
\]

Thus \(m_{1,k}=0\) leaves the second derivative exactly \(m_{2,k}\);
to quantify the remainder, put

\[
 u_\delta=B_\delta\phi_k
 =\delta(k\pi)^2\phi_k+V\phi_k.
\]

The assumption \(V\in W^{1,\infty}\) gives a uniform bound on
\(\|B_\delta^{1/2}u_\delta\|_2\). When \(m_{1,k}=0\),

\[
 f_\delta''(s)-m_{2,k}
 =\left\langle V,
 (e^{-sB_\delta}-I)u_\delta\right\rangle.
\]

Spectral calculus gives
\(\|(e^{-sB_\delta}-I)u_\delta\|_2\leq C\sqrt s\), uniformly in
\(\delta\). Integrating twice yields

\[
 f_\delta(s)=\frac{m_{2,k}}2s^2+O(s^{5/2}).
\]

After the modal sum, the remainder is
\(O(t^{5/2}\varepsilon^{-11/2})\), smaller than the leading norm by
\(O(\sqrt t/\varepsilon)=O(\sqrt q)\). Consequently

\[
 \mathcal N_{\varepsilon,k}(t)
 \sim
 \frac{|m_{2,k}|}{2}\|\eta^{(4)}\|_2
 t^2\varepsilon^{-9/2}.
\]

For \(r_*\geq3\), the profile asymptotic of Theorem 5.1 is rigorous, but its
promotion to every arbitrary joint path \((\varepsilon,t)\to(0,0)\) is not
claimed. Words containing both \(A\) and \(V\) may be smaller than the pure
multiplication term in the iterated limit yet dominate a specially chosen
path on which \(q=t/\varepsilon^2\) vanishes too quickly. A sufficient
scale-separation target is

\[
 t=o(q^{r_*-1}),
\]

together with enough regularity and endpoint compatibility to control the
mixed-word expansion. This condition is deliberately recorded as
sufficient-looking rather than sharp; a full arbitrary-\(r_*\) commutator
theorem is open in this memo.

### 6.2 Balanced layer: \(t/\varepsilon^2\to q\in(0,\infty)\)

If \(\mathcal P_k(q)>0\), then

\[
 \boxed{
 \mathcal N_{\varepsilon,k}(t)
 \sim\varepsilon^{-1/2}\mathcal P_k(q).}
\]

Both the mollifier transform and the full finite-\(g\) profile \(F_k\) remain
visible. This is the genuine crossover, not a pure power law.

### 6.3 Heat-resolved singular layer:
\(\varepsilon^2/t\to0\), \(t\to0\)

Assume \(F_k\not\equiv0\), equivalently \(C_{F,k}>0\). Then

\[
 \boxed{
 \mathcal N_{\varepsilon,k}(t)
 \sim C_{F,k}t^{-1/4}.}
\]

A direct joint proof repeats Theorem 4.1 with \(u=\sqrt t\,\ell\).
The factor
\(\widehat\eta(\pi\varepsilon\ell)\) tends to one on the relevant modes
\(\ell=O(t^{-1/2})\), and the interior carrier again averages.

The same formula holds for a target atom:

\[
 \mathcal N_{\delta_{y_0},k}(t)^2
 =\sum_{\ell\geq1}
 2\cos^2(\ell\pi y_0)|a_{\ell k}(t)|^2,
\]

\[
 \lim_{t\downarrow0}
 t^{1/2}\mathcal N_{\delta_{y_0},k}(t)^2
 =C_{F,k}^2.
\]

Every fixed modal coefficient tends to zero as \(t\downarrow0\), but under
this nonnull-port assumption the full atomic response norm diverges like
\(t^{-1/4}\). This is a precise
noncommutation of the fixed-band and full-band limits.

For fixed \(t>0\), on the other hand,

\[
 \mathcal N_{\varepsilon,k}(t)
 \longrightarrow
 \mathcal N_{\delta_{y_0},k}(t)
\]

by dominated convergence. Positive time smooths the atom, exactly as
suggested in Stage V.

## 7. Exact full-coupling profile for the canonical ramp

Take

\[
 V(x)=1+gx,\qquad g>0.
\]

For \(b=k\pi\) and \(a_s=gs\),

\[
 \begin{aligned}
 F_k(s)
 &=\sqrt2e^{-s}\int_0^1e^{-a_sx}\cos(bx)\,dx\\
 &=\boxed{
 \sqrt2e^{-s}
 \frac{gs\,[1-(-1)^ke^{-gs}]}
      {(gs)^2+(k\pi)^2}.}
 \end{aligned}
\]

This formula is exact for every finite \(g\).

For odd \(k\),

\[
 F_k(s)
 =\frac{2\sqrt2g}{(k\pi)^2}s+O(s^2),
\]

so

\[
 r_*=1,\qquad
 m_{1,k}=-\frac{2\sqrt2g}{(k\pi)^2}.
\]

For even \(k\),

\[
 F_k(s)
 =\frac{\sqrt2g^2}{(k\pi)^2}s^2+O(s^3),
\]

so

\[
 r_*=2,\qquad
 m_{1,k}=0,\qquad
 m_{2,k}=\frac{2\sqrt2g^2}{(k\pi)^2}.
\]

Thus the early constants are

\[
 \mathcal N_{\varepsilon,k}(t)
 \sim
 \frac{2\sqrt2g}{(k\pi)^2}\|\eta''\|_2
 t\varepsilon^{-5/2}
 \quad(k\ {\rm odd}),
\]

and

\[
 \mathcal N_{\varepsilon,k}(t)
 \sim
 \frac{\sqrt2g^2}{(k\pi)^2}\|\eta^{(4)}\|_2
 t^2\varepsilon^{-9/2}
 \quad(k\ {\rm even}).
\]

The parity distinction is a cancellation in the full nonlinear profile, not
an artifact of first-order perturbation theory.

If \(g=0\), then \(V\) is constant and \(F_k\equiv0\). There is no directed
endpoint response at any scale.

## 8. The \(t=\tau h^2\), \(\varepsilon=h^\alpha\) critical widths

First suppose

\[
 0<\alpha<1,\qquad
 \varepsilon=h^\alpha,\qquad
 t=\tau h^2.
\]

Then \(\varepsilon/h\to\infty\), so the mollifier is resolved by many cells,
and

\[
 q=\frac{t}{\varepsilon^2}
 =\tau h^{2-2\alpha}\longrightarrow0.
\]

Whenever the joint early asymptotic is valid,

\[
 \mathcal N_{\varepsilon,k}(\tau h^2)
 \sim
 \frac{|m_{r_*,k}|}{r_*!}
 \|\eta^{(2r_*)}\|_2
 \tau^{r_*}
 h^{\,2r_*-\alpha(2r_*+1/2)}.
\]

The critical exponent is therefore

\[
 \boxed{
 \alpha_c(r_*)=\frac{4r_*}{4r_*+1}.}
\]

Specifically:

| width exponent | response behavior at \(t=\tau h^2\) |
|---|---|
| \(\alpha<\alpha_c(r_*)\) | tends to zero |
| \(\alpha=\alpha_c(r_*)\) | tends to a finite nonzero scale |
| \(\alpha_c(r_*)<\alpha<1\) | diverges |
| \(\alpha=1\) | enters the lattice crossover; continuum constants are no longer universal |

For the ramp:

\[
 \alpha_c=\frac45\quad(k\ {\rm odd}),\qquad
 \alpha_c=\frac89\quad(k\ {\rm even}).
\]

The odd-mode value \(4/5\) is the sharp balance between the microscopic
\(h^2\) time and the \(\varepsilon^{-5/2}\) first-jet norm. The even-mode
\(8/9\) threshold is a genuine second-jet effect.

For the canonical midpoint ramp with conservative cell masses, these two
thresholds also hold for the actual discrete path, not only for the continuum
expression evaluated at \(t=\tau h^2\). On every effective band
\(\ell\varepsilon\leq M\), the assumptions \(\alpha<1\) and
\(h/\varepsilon\to0\) give

\[
 \frac{\mu_{\ell,n}}{(\ell\pi)^2}\longrightarrow1
\]

uniformly. The cell-mass cosine coefficients converge to the mollifier
coefficients uniformly on that band. Repeated discrete summation by parts for
the conservative masses gives, for every fixed \(N\),

\[
 |\beta_{\ell,h}|
 \leq C_N(1+\ell\varepsilon)^{-N},
\]

which controls the complement uniformly. The discrete first two scalar
derivatives have the same moment formulas as in Section 6. The odd ramp has no
first-moment cancellation to preserve. For an even ramp mode, cell reflection
symmetry makes the discrete first moment \(m_{1,k}^{(h)}\) vanish exactly, so
the uniform scalar Taylor bound transfers the \(r_*=2\) power and constant.

For a general discretization, mere convergence
\(m_{1,k}^{(h)}\to0\) is insufficient: the first jet is negligible relative
to the second only if

\[
 m_{1,k}^{(h)}=o(\kappa_h),
 \qquad \kappa_h=t_h/\varepsilon_h^2.
\]

At the \(8/9\) critical width this means
\(m_{1,k}^{(h)}=o(h^{2/9})\). An \(O(h)\) midpoint error is sufficient, and
the canonical reflection cancellation is stronger. This direct small-\(q\)
argument is narrower than a uniform three-parameter crossover theorem, but it
is enough for the canonical \(4/5\) and \(8/9\) claims.

For general \(r_*\geq3\), the exponent is the multiplication-profile
prediction. It becomes a theorem along paths for which the mixed
diffusion-potential terms are proved negligible; the sufficient
scale-separation condition recorded in Section 6 is satisfied at the formal
critical power, but a complete arbitrary-\(r_*\) endpoint-domain proof is not
included here.

## 9. The finite-cell and atomic lattice theorem

The continuum calculation does not apply unchanged when
\(\varepsilon/h=O(1)\). The correct replacement can nevertheless be written
explicitly.

For this section additionally assume \(V\in C([0,1])\). Let \(h=1/n\), let
\(L_n\) be the unscaled path Laplacian, set

\[
 A_n=h^{-2}L_n,\qquad
 V_h=\operatorname{diag}(V((j+1/2)h)),
\]

and write

\[
 \omega(\theta)=4\sin^2(\theta/2).
\]

The exact target eigenvalues obey

\[
 h^2\mu_{\ell,n}
 =\omega(\theta_{\ell,n}),\qquad
 \theta_{\ell,n}=\pi\ell h.
\]

The reduced grid block is

\[
 K_{\ell,n}=A_n+\mu_{\ell,n}V_h,
\]

and \(\phi_{k,n}(j)=\sqrt2\cos(k\pi(j+1/2)h)\).

Let \(q_h\) be a target probability localized around a carrier cell \(j_h\),
where

\[
 h(j_h+1/2)\longrightarrow y_0\in(0,1).
\]

Write its local weights as

\[
 w_m^{(h)}=q_h(j_h+m)
\]

and assume, after extension by zero,

\[
 w^{(h)}\longrightarrow w
 \quad\hbox{in }\ell^1(\mathbb Z).
\]

No finite-support hypothesis is imposed. The \(\ell^1\) convergence is the
uniform-tightness condition that also covers cell-averaged Gaussians of fixed
lattice width.

Let

\[
 W(\theta)=\sum_{m\in\mathbb Z}w_me^{im\theta}.
\]

The weights are nonnegative and sum to one, so \(W(0)=1\).

If

\[
 \beta_{\ell,h}
 =\sum_jq_h(j)\phi_{\ell,h}(j),
\]

define

\[
 \mathcal N_{h,k}^{\rm disc}(t)^2
 =\sum_{\ell=1}^{n-1}
 |\beta_{\ell,h}|^2
 \left|
 \left\langle1,
 e^{-tK_{\ell,n}}\phi_{k,n}
 \right\rangle_h
 \right|^2.
\]

### Theorem 9.1 — microscopic lattice profile

For every fixed \(\tau>0\), the complete discrete target-mode response norm
satisfies

\[
 \boxed{
 \lim_{h\downarrow0}
 h\,\mathcal N_{h,k}^{\rm disc}(\tau h^2)^2
 =
 \mathcal P_{w,k}^{\rm lat}(\tau)^2,}
\]

where

\[
 \boxed{
 \mathcal P_{w,k}^{\rm lat}(\tau)^2
 =\frac1\pi\int_0^\pi
 |W(\theta)|^2
 |F_k(\tau\omega(\theta))|^2\,d\theta.}
\]

#### Proof

For a target mode with
\(\theta_{\ell,n}\to\theta\in(0,\pi)\),

\[
 \tau h^2K_{\ell,n}
 =\tau\left(
 L_n+\omega(\theta_{\ell,n})V_h
 \right).
\]

Under the density embedding, the uniformly bounded operators satisfy
\(J_nL_nP_n\to0\) strongly and
\(J_nV_hP_n\to M_V\) strongly. Duhamel's formula makes the convergence uniform
for the coefficient \(\omega\in[0,4]\). Therefore the reduced scalar amplitude
converges uniformly in \(\theta\) to

\[
 F_k(\tau\omega(\theta)).
\]

The discrete version of Lemma 3.1 gives the uniform envelope

\[
 C\tau\omega(\theta)e^{-a\tau\omega(\theta)}.
\]

The target coefficient is

\[
 \beta_{\ell,h}
 =\sqrt2\,
 \operatorname{Re}\left[
 e^{i\theta_{\ell,n}(j_h+1/2)}
 W_h(\theta_{\ell,n})\right],
\]

where \(W_h\to W\) uniformly by the \(\ell^1\) assumption. The uniform scalar
limit and envelope imply convergence of the full squared-weight step functions
in \(L^1(0,\pi)\). Squaring gives a nonoscillatory term \(|W_h|^2\) and an
oscillatory term with phase \(2\theta_{\ell,n}(j_h+1/2)\). Since the carrier
tends to a fixed interior point, Abel summation with bounded geometric partial
sums removes the latter. Finally

\[
 h\sum_{\ell=1}^{n-1}f(\pi\ell h)
 \longrightarrow\frac1\pi\int_0^\pi f(\theta)\,d\theta.
\]

This proves the formula. \(\square\)

### Lattice small- and large-time limits

If \(r_*<\infty\), then

\[
 \mathcal P_{w,k}^{\rm lat}(\tau)
 \sim
 \frac{|m_{r_*,k}|}{r_*!}\tau^{r_*}
 \left[
 \frac1\pi\int_0^\pi
 |W(\theta)|^2\omega(\theta)^{2r_*}\,d\theta
 \right]^{1/2}
\]

as \(\tau\downarrow0\).

For a one-cell atom \(W\equiv1\) and \(r_*=1\),

\[
 \frac1\pi\int_0^\pi\omega(\theta)^2\,d\theta=6,
\]

so

\[
 \mathcal P_{\rm atom,k}^{\rm lat}(\tau)
 \sim\sqrt6\,|m_{1,k}|\tau.
\]

If \(F_k\not\equiv0\), then as \(\tau\to\infty\), every probability
preparation with \(W(0)=1\) obeys

\[
 \boxed{
 \mathcal P_{w,k}^{\rm lat}(\tau)
 \sim C_{F,k}\tau^{-1/4}.}
\]

Indeed only \(\theta=O(\tau^{-1/2})\) contributes,
\(\omega(\theta)\sim\theta^2\), and \(W(\theta)\to1\). Thus the microscopic
lattice profile forgets cell placement after many lattice diffusion times and
matches the continuum atomic constant.

## 10. The three \(\varepsilon/h\) regimes

Use conservative cell masses

\[
 q_{h,j}=\int_{jh}^{(j+1)h}\rho_\varepsilon(y)\,dy.
\]

This choice remains meaningful even when the mollifier is narrower than one
cell.

### 10.1 Resolved mollifier: \(\varepsilon/h\to\infty\)

The cell masses approximate the continuum preparation. In the iterated
resolved limit, when \(t/\varepsilon^2\to q\in(0,\infty)\), the continuum
profile in Theorem 4.1 is recovered. When \(t/\varepsilon^2\to0\) or
infinity, the early and late laws of Section 6 are the matching profiles.

The effective target wavelength is

\[
 r_{\rm eff}\asymp\max\{\varepsilon,\sqrt t\}.
\]

The low-dispersion continuum approximation requires

\[
 \frac{h}{r_{\rm eff}}\longrightarrow0.
\]

For a genuinely resolved preparation this is automatic in the early and
balanced layers. In the late layer it reduces to \(h/\sqrt t\to0\).
A quantitative estimate uniform over every such joint path is not proved in
this memo; Section 8 proves directly the small-\(q\), \(r_*=1,2\) power-law
subfamily needed for the canonical critical exponents.

### 10.2 Finite-cell mollifier:
\(\varepsilon/h\to c\in(0,\infty)\)

Let

\[
 \alpha_h=\frac{y_0}{h}-\left\lfloor\frac{y_0}{h}\right\rfloor.
\]

Along a subsequence on which \(\alpha_h\to\alpha\in[0,1]\), the limiting local
cell weights are

\[
 w_m^{c,\alpha}
 =\int_{(m-\alpha)/c}^{(m+1-\alpha)/c}
 \eta(z)\,dz.
\]

Theorem 9.1 applies with their discrete Fourier transform

\[
 W_{c,\alpha}(\theta)
 =\sum_mw_m^{c,\alpha}e^{im\theta}.
\]

At \(t=\tau h^2\), if
\(\mathcal P_{w^{c,\alpha},k}^{\rm lat}(\tau)>0\),

\[
 \mathcal N_{h,k}^{\rm disc}(t)
 \sim h^{-1/2}
 \mathcal P_{w^{c,\alpha},k}^{\rm lat}(\tau).
\]

There is no universal continuum profile at finite \(c\). Both lattice
dispersion and the subcell phase \(\alpha\) survive. If the sequence
\(\alpha_h\) has no limit, different subsequences can have different
microscopic constants.

In the iterated overlap \(c\to\infty\) with \(\tau=qc^2\), provided
\(\mathcal P_k(q)>0\),

\[
 \mathcal P_{w^{c,\alpha},k}^{\rm lat}(qc^2)
 \sim c^{-1/2}\mathcal P_k(q),
\]

which recovers
\(\varepsilon^{-1/2}\mathcal P_k(q)\) after
\(\varepsilon=ch\).

### 10.3 Subcell mollifier: \(\varepsilon/h\to0\)

If the support stays inside one carrier cell, conservative cell integration
gives a one-cell atom in the limit. If the carrier approaches a cell boundary
on the \(\varepsilon\) scale, a nontrivial two-cell split can remain. These
possibilities are all covered by Theorem 9.1 through the limiting weights
\(w\).

For a generic one-cell limit with
\(\mathcal P_{\rm atom,k}^{\rm lat}(\tau)>0\),

\[
 \mathcal N_{h,k}^{\rm disc}(\tau h^2)
 \sim h^{-1/2}\mathcal P_{\rm atom,k}^{\rm lat}(\tau).
\]

Consequently,

\[
 \mathcal N_{h,k}^{\rm disc}(t)
 \asymp t h^{-5/2}
\quad(t/h^2\to0,\ r_*=1),
\]

while, provided \(F_k\not\equiv0\),

\[
 \mathcal N_{h,k}^{\rm disc}(t)
 \sim C_{F,k}t^{-1/4}
 \quad(t/h^2\to\infty,\ t\to0).
\]

The last display is proved here as the iterated large-\(\tau\) limit of the
lattice profile. Promoting it to every joint path
\(h\to0,\ t/h^2\to\infty,\ t\to0\) requires the uniform three-parameter
estimate proposed in Section 13.

The grid has saturated the effective preparation width at \(h\). Substituting
the physical \(\varepsilon\ll h\) into the continuum
\(t\varepsilon^{-5/2}\) law would therefore be false.

Midpoint sampling is particularly unsafe here: a compactly supported
mollifier can miss every cell centre and produce zero mass, or jump
discontinuously when a centre enters its support. Cell integration or another
declared mass-conservative placement rule is necessary.

## 11. Falsification and scope ledger

| Tempting statement | Correct boundary |
|---|---|
| the response is always \(\varepsilon^{-1/2}\) | the multiplier is the nontrivial crossover \(\mathcal P_k(t/\varepsilon^2)\) |
| \(\mathcal P_k(q)\sim Cq\) for every source | only if \(\int V\phi_k\neq0\); the ramp's even modes begin at \(q^2\) |
| first-order perturbation in \(g\) determines the crossover | false; \(F_k(s)=\int e^{-sV}\phi_k\) keeps all orders in \(g\) |
| the carrier factor is pointwise \(1/2\) | false; only its complete interior modal sum averages |
| the same constant holds at a reflecting boundary | false; truncation and renormalization select different half-kernel constants |
| \(\varepsilon/h\to c\) has a unique continuum limit | false; lattice dispersion, sampling rule, and subcell phase remain |
| a midpoint sample represents every narrow density | false when \(\varepsilon\lesssim h\); use conservative cell masses |
| an atom has a continuous full-band response at \(t=0\) | false; it is zero coefficientwise at zero but its positive-time norm grows as \(t^{-1/4}\) |
| fixed-mode convergence controls the singular norm | false; the norm is carried by modes of order \(1/\max(\varepsilon,\sqrt t)\) |
| the general \(r_*\) profile automatically gives every joint limit | false for \(r_*\geq3\) without mixed \(A/V\) control |
| every null multiplication profile has a \(t^{-1/4}\) law | false; asymptotic equivalence requires \(F_k\not\equiv0\) |
| \(g=0\) is a nontrivial control | false; constant \(V\) makes every directed endpoint response vanish |

## 12. What is proved and what remains open

### Proved in this memo

1. the exact full-response norm formula for an interior smooth mollifier;
2. the uniform high-mode envelope;
3. the full-finite-\(g\) rescaling
   \(a_{\ell k}(s/\nu_\ell)\to F_k(s)\);
4. the balanced continuum limit
   \(\varepsilon\mathcal N^2\to\mathcal P^2\);
5. the exact small- and large-\(q\) asymptotics of \(\mathcal P\);
6. the joint early law for the generic \(r_*=1\) case and, with
   \(W^{1,\infty}\) modulation, the multiplication-dominated \(r_*=2\) case;
7. the joint late law for \(F_k\not\equiv0\), including the
   \(t^{-1/4}\) atomic singularity;
8. the exact ramp profile and its odd/even selection rule;
9. the \(4/5\) and \(8/9\) critical exponents for the continuum and the
   canonical midpoint ramp grid;
10. the finite-cell lattice profile for localized conservative preparations;
    and
11. matching of the lattice and continuum atomic tails in the declared
    profile limits.

### Not closed here

1. a sharp arbitrary-joint-path theorem for \(r_*\geq3\);
2. carriers approaching a reflecting boundary jointly with
   \(\varepsilon,t\);
3. nonsymmetric or sign-changing mollifiers beyond the straightforward
   Fourier-phase modification;
4. a quantitative error rate in Theorem 4.1 uniform over all
   \(q\in(0,\infty)\);
5. a joint continuum/infinite-volume limit;
6. nonlinear generators, time-dependent modulation, or path-space sensors;
   and
7. a physical-wave interpretation. Every result here remains parabolic.

## 13. Recommended next analytic target

The most useful next theorem is a uniform three-parameter estimate comparing
the discrete norm with the appropriate continuum or lattice profile:

\[
 \mathcal N_{h,\varepsilon,k}(t)
 \quad\hbox{versus}\quad
 \begin{cases}
 \varepsilon^{-1/2}\mathcal P_k(t/\varepsilon^2),
   & h/\max(\varepsilon,\sqrt t)\ll1,\\[1mm]
 h^{-1/2}\mathcal P_{w,k}^{\rm lat}(t/h^2),
   & \varepsilon/h=O(1).
 \end{cases}
\]

Such an estimate would turn the present subsequential phase diagram into a
single finite-\((h,\varepsilon,t)\) error theorem and would identify the exact
transition surface on which mesh dispersion, mollifier shape, and heat
smoothing are equally visible.
