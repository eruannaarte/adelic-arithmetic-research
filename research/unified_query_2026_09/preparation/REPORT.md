# Preparation: a joint calibration record now implies an explicit query bound

**Known initial-state offsets need not be charged as unknown preparation error.** Conditioning on measured launch intervals improves the preparation certificate while preserving the full nonlinear source and preparation enclosure. A shared systematic instrument offset can also retain cancellation across launches.

The new theorem handles a record of the form

\[
p_A=m_A+b+v_A,\qquad p_B=m_B+b+v_B.
\]

Here the measured centers m_A,m_B are known, b is one bounded instrument correction shared across A and B, and v_A,v_B are separate bounded launch residuals. All of them must fit inside the already validated preparation box. The source-ambiguity bound depends on the unknown interval widths. The measured centers affect domain containment but cancel when comparing worlds consistent with the same record. No distribution or independence assumption is needed.

A concrete synthetic specification demonstrates the consequence. Seven local residual radii are 0.000005; B.theta1 has radius 0.000003. Four common instrument correction radii are 0.000001. With modest nonzero measured center offsets, the entire support remains inside the old outer box: seven absolute extents are 0.000007 and B.theta1 reaches 0.000009.

For the fixed selected A+B experiment at weighted readout-noise radius 0.0000001, this record certifies source diameter **below 0.000060053**, including the two physical log-parameter queries and shared clock coordinate. The target is 0.0001, and every row retains **more than 35.79%** of that target as slack. The exact same preparation record supports weighted readout-noise radius **above 0.0000024787** if only the 0.0001 diameter target is required. This is a mathematical budget tradeoff, not a measured noise capability.

The diameter uses the infinity norm; projecting to the two log parameters preserves the bound. It is not an asserted half-diameter error for a supplied point estimator. The five dynamical readings also do not account for the extra initial-state metrology and common-reference characterization needed to justify a calibration record. Total acquisition cost remains to be determined for a chosen apparatus.

The controls make the contribution visible. Enclosing the same calibrated support in a box centered at the original nominal launch gives a first-row target load **1.06758**, which fails the sufficient test. Retaining the measured center gives load **0.64203**. Keeping the same interval radii but treating the instrument offsets independently across A and B raises that load to **0.66471**. The two gains therefore come from specific known-center information and cross-launch correlation. None is an assertion of global decoder optimality or an impossibility result for the failed control.

The package provides a complete proof, a concrete per-experiment calibration protocol, a strict machine-readable input schema, and a standard-library exact checker. The checker requires the precise velocity, clock, launch, and source conventions. It rejects re-preparation between grouped readings, unconverted velocity units, unsupported source-box changes, malformed intervals, domain escape, and excessive noise. Ten tests pass; the three inherited outward ODE reconstructions also pass.

Inspection of the existing chamber, its adversarial audit, and the atlas laboratory confirms their stated role: they are reproducible synthetic experiments. Their RK4/DP54 comparison and finite ensemble bookkeeping do not constitute measured eight-coordinate launch calibration. The older displayed certified strip also has exact preparation. The new bridge leaves those existing artifacts intact and gives future measured records a separate, explicit route to a conditional query guarantee.

**Physical calibration remains NOT_RUN.** The supplied record is labelled synthetic. Even a record labelled physical is not automatically promoted to empirical validation: its support evidence and model adequacy must be established externally. A finite batch of successful launch trials alone cannot guarantee a bounded future launch.

The next objective is to apply this protocol to actual A/B initial-state metrology, or to integrate the strict record interface into the chamber with a clearly labelled synthetic mode. The exact acceptance inequalities already determine which tolerance or noise bound would need improvement if a measured record fails.

[Complete theorem and proof](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/PROOFS.md) · [Calibration protocol](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/CALIBRATION_PROTOCOL.md) · [Reproduction guide](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/README.md)
