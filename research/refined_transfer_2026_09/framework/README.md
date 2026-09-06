# One transfer theorem, two new operational consequences

[applications.py](applications.py) imports the unchanged
[transfer library](../../transfer_theorem_2026_09/framework/transfer.py).
It checks the new spatial and arithmetic results through that library's
continuous-cell, pair, inverse, normal-residual and scalar predicates. It does
not introduce a replacement theorem or change either physical model.

## Spatial specialization

For each of the new seven-bank certificate's 3,391 records, the complete
spatial consumer first verifies the physical-model binding, exact translated
polynomial bound, rational preconditioner and separate full-time case cover.
Let \(\gamma\) be the checked lower singular bound at a cell center, \(E\)
the whole-cell perturbation after preconditioning, \(R\) the preconditioner,
and \(f\) the requested unpreconditioned floor. The common predicate verifies

\[
\gamma\ge E+\sqrt{f\|R\|_F^2}.
\]

The spatial consumer's recorded strict inequality makes the resulting floor
strict. The argument is the same continuous-operator transfer theorem:
perturbation below the weakest information direction preserves an inverse.

After the physical normalization, the adapter checks
\(\lambda>2\delta^2\) and \(\delta^2<\mu(0.000998507)^2\), where
\(\delta=10^{-7}+10^{-9}+10^{-9}\). These are respectively the query-pair
and source-inverse consequences. There are **3,391 cell gates and two global
gates**, covering every target, source direction and known time under the
spatial promise. See [the full spatial proof](../resolution/PROOFS.md).

## Arithmetic specialization

The weighted drift result supplies a degree-eight polynomial \(p\) for every
declared slow sinusoid \(g\), with

\[
\|g-p\|_W\le \nu=B K_W(\Omega).
\]

The polynomial joins the already unrestricted polynomial nuisance. Only its
bounded remainder contributes to the joint reading radius
\(r=\eta+\nu+\xi\). This is the theorem's nuisance-and-approximation transfer
under the actual physical norm. It does not create independent readings by
using two windows on the same data.

Write \(f\) for the augmented Gram floor, \(A_n\) for the inherited complete
tail bias, and \(\rho\) for the actual verified normal residual. The unchanged
normal-residual bound supplies solve error \(\rho/f\), so the common scalar
gate for each unknown integer is

\[
A_n+n^2\frac{\rho}{f}
+\frac{n^2}{\sqrt f}(\eta+\nu+\xi)<\frac12.                              \tag{1}
\]

The adapter evaluates (1) without floating square roots, as

\[
\operatorname{strict\_scalar\_gate}
\left(1,\;2\left(A_n+n^2\rho/f\right),\;n^4/f,\;\eta+\nu+\xi\right).
\]

It checks all 49 unknown coordinates for each of two weighting designs:
**98 scalar gates**. The applied family is \(B=20000\), \(\Omega=1\), arbitrary
phase, degree eight, and 8,900 unchanged readings. Its uniform weighted
factors are reconstructed exactly from the independently checked polynomial
residual and remainder norms.

For comparison, 47 gates per design fail when the older pointwise Taylor
radius replaces the new weighted radius. These **94 failed sufficient
inequalities** demonstrate a certificate improvement; they do not prove the
old data or experiment incapable of recovery.
See [the weighted family proof](../noise/PROOFS.md).

## Reproduction and scope

From the project root:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /private/tmp/math-five-paths-venv/bin/python research/refined_transfer_2026_09/framework/applications.py

The command uses the standard library and the unchanged rational transfer
module. It reruns the complete spatial consumer, arithmetic consequence
checker, and normalization component below. Add --write to update this
package's own [applications.json](applications.json). The base results contain
**3,491 successful common transfer gates**; the normalization specialization
adds 18 for a total of **3,509**. All consumed inputs are hashed.

The adapter requires a hash-bound record of the independent weighted-norm
replay. It does not independently reconstruct that physical norm, the spatial
kernel, or the actual numerical normal residual. Those replays are separate
validation jobs documented in the model packages and the root reproduction
guide. A small normal residual certifies the solve under its model; it
cannot validate the declared physical drift family.

## Verified normalization specialization

The adapter independently calls the normalization packet verifier on **72 raw
data packets**: seven, eight and nine rows, all eight declared source/noise
profiles, three times and three source amplitudes. It checks the profile,
exact raw-to-normalized scaling and data hashes for every packet.

The physical gain is \(\|A_j\|\le4/3\), so a raw datum under the sensor promise
satisfies \(\|y\|\le K\|u\|_S\), with \(K=4/3+\eta\) and \(S\succeq I\).
The packet's rational multiplier \(r\) satisfies the exactly verified
fourth-power inequalities

\[
(1-e)^4\le (1+t)r^4\le(1+e)^4.
\]

Therefore, for \(z=ry\), the physical error is

\[
\|\alpha z-y\|\le e\|y\|\le eK\|u\|_S.
\]

Every packet's actual charge \(eK\) is at most \(10^{-9}\). No source
amplitude is an input to this bound. The adapter checks nine new seven-bank
pair gates and nine inverse gates using the **actual** charge in
\(\delta=\eta+\rho+eK\). These are the extra 18 common gates. The raw
observation and known time must remain exact rationals, and the physical
sensor promise still applies.

For the recorded run, the initial 3,491-gate adapter had already completed
before the normalization evidence arrived. Its bound inputs were all rehashed
and found byte-identical; the 72 packets and 18 additional gates were then
checked using --append-normalization. That reuse is explicitly recorded in
the output. A normal invocation now performs the full combined check.
The packet count is kept distinct from the common-theorem gate count.
