# Double-Pendulum Variational Angle-Slice Atlas — Tier 1

This lane maps each cell-centred initial-angle launch

\[
z_0=(\theta_1,\theta_2,0,0)
\]

to the weakest and strongest local gains of the finite-time operational
feature.  It uses the two-column `source_injection` for the initial-angle
slice, so the reported gains measure perturbations of the two launch angles
rather than arbitrary four-state perturbations.

The output metric exactly matches the existing atlas feature.  For normalized
sample weights \(w_k\), the feature stacks \(\sqrt{w_k}\,h(z(t_k))\).  The
variational implementation equivalently stacks the unweighted response blocks
and declares output precision

\[
W=\operatorname{diag}(w_k)\otimes I_6.
\]

Thus its \(2\times2\) pullback Gram is the Jacobian Gram of the RMS trajectory
feature, not a differently normalized sensitivity statistic.

Every cell is integrated twice with a declared coarse/fine ladder and an
enabled sampled energy gate. State, tangent, weighted-response, Gram, weakest-
gain, and strongest-gain discrepancies must all pass their gates. The report
serializes the physical parameters, software environment, and exact Frobenius-
relative formulas used by those decisions. Direct gain gates matter because a
small relative Gram error need not protect the weakest eigenvalue of a highly
conditioned Gram.

Four declared cells in the canonical run also compare the full variational
feature response and Gram against centered finite differences of independently
integrated trajectories. The spot ledger serializes both response matrices,
reconstructs their Grams, and separately gates the weakest and strongest gains;
this prevents a Frobenius-small Gram discrepancy from concealing a poorly
controlled weakest direction. These are spot checks only; cells elsewhere do
not inherit a finite-difference claim. A failed or unavailable gate marks the
cell unresolved, and its selected weakest and strongest gains are serialized
as `null` rather than silently promoted.

The implementation and reproducer are
`oig_double_pendulum_variational_atlas.py` and
`test_oig_double_pendulum_variational_atlas.py`.
The same module provides a strict report verifier and the command
`--verify REPORT.json`. It reconstructs the serialized masks, gates, gain/Gram
relations, finite-difference response and gain discrepancies, spot decisions,
counts, and quantiles without replaying an ODE.

The coarse/fine state, tangent, and weighted-response discrepancy fields are
serialized Tier-1 numerical inputs. The verifier cross-links their gates to
the unresolved mask and reconstructs every relation available from the stored
responses and Grams, but it does not store the full trajectory/tangent arrays,
authenticate provenance, or recompute those three discrepancies from an ODE.

## Atlas-matched finding

For the \(13\times13\), \(T=4\) run, 167 of 169 cells pass every declared
coarse/fine gate. The two seam-adjacent cells \((0,12)\) and \((12,0)\) are
unresolved: tangent, weighted-response, Gram, strongest-gain, and selected
finite-difference checks fail there. Their selected gain fields are `null`.
Only four cells receive finite-difference checks; two pass and the two
unresolved seam cells fail, so this is not 167-cell finite-difference evidence.

The weakest-gain quantiles over resolved cells are approximately
\(0.9712,2.3363,5.1923\), while the strongest-gain quantiles are approximately
\(2.6155,19.2260,406.576\). These describe finite-time local amplification
under the declared protocol, not Lyapunov exponents or stability classes.

## Reproduction

```bash
python oig_double_pendulum_variational_atlas.py \
  --side 13 --duration 4 \
  --output artifacts/double_pendulum_variational_atlas_13x13_t4_tier1.json
python oig_double_pendulum_variational_atlas.py \
  --verify artifacts/double_pendulum_variational_atlas_13x13_t4_tier1.json
python -m unittest -v test_oig_double_pendulum_variational_atlas.py
```

## Claim boundary

This is Tier-1 numerical evidence.  Adaptive-solver refinement and centered
finite-difference agreement are valuable falsification checks, but they are
not outward enclosures of the exact flow or tangent map.  The atlas therefore
does not supply physical response boxes to the exact OIG engine, prove local
or Lyapunov stability, or make an infinite-time claim.
