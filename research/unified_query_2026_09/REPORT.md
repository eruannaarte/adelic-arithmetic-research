# Certified query recovery under structured uncertainty

The unified line now has a proved common framework and substantive extensions in all five research paths. One exact support-and-noise inequality reproduces **687 scalar certificate gates across three different models**. The applications add a persistent harmonic ambiguity, a calibration-conditioned pendulum guarantee, a joint arithmetic query, recovery under quintic drift, and spatial sensing with approximately half as many channels.

The original discussions and both previous research packages are preserved. [MATH_CURRENT_STATE.md](/Volumes/KINGSTON/Vibecoding/Math/MATH_CURRENT_STATE.md) is the new entry point for continuing work; the [evidence index](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/EVIDENCE_INDEX.md) connects every result below to proofs, witnesses, audits, and reconstruction commands. This package is local research, with no new public release.

## The common result

For each experiment D and observed value y, consider the set of answers consistent with every declared source, nuisance, and error constraint:

\[
\mathcal Q_D(y)=\{q(x):y=F_D(x,u)+e,\ (x,u)\text{ admissible},\ e\text{ allowed}\}.
\]

A discrete answer is determined when this set is a singleton. For continuous answers, the best worst-case error conditional on y is the smallest enclosing radius of this set in the declared query norm; the uniform minimax error is the supremum of these radii over promised observations. These statements distinguish uniqueness from an efficient or numerically certified implementation.

The transfer theorem proves that verified preprocessing and approximation bounds give an **outer answer set containing the true answers**. It composes through nuisance elimination, finite approximation, computation, and observation restriction. Returning the unique answer in an outer set is safe; multiple outer answers mean the certificate abstains, and an empty set flags inconsistency with its contract.

There is a stronger equivalence for unrestricted linear nuisance with bounded noise in a weighted norm. Projecting onto the metric-orthogonal complement of the nuisance space preserves the exact answer set. The proof reconstructs an admissible nuisance and noise vector from every projected explanation. This applies even when the source or query is nonlinear. Bounded, shared, and source-dependent uncertainties retain their actual joint constraints.

The executable common layer reconstructs 243 joint quadratic pair gates, 441 integer-rounding gates for polynomial drift, and three nonlinear preparation diameter gates. Their model-specific proofs establish the inputs; the common checker verifies the same exact transfer inequality in all three. This is a demonstrated connection, not a replacement for their separate arithmetic, ODE, and numerical arguments. [Complete framework](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/framework/PROOFS.md).

## Results at a glance

| Path | New supported result | What remains open |
|---|---|---|
| Harmonic acquisition | Every schedule in an explicit six-dimensional time box has an exact interior collision and a fixed scalar-query ambiguity | A short schedule certified over all source differences, or a larger excluded design region |
| Preparation calibration | A joint calibration record supports source diameter <0.000060053; known offsets and shared systematic errors are treated explicitly | Physical measurements and evidence for apparatus/model adequacy |
| Quadratic arithmetic | An abstaining query uses uncertain a(7) and nonlinear a(25), a(49), a(50); conditional boundary gains reach >0.4% | A sharp actual-sensor limit or a larger gain from improved directional geometry |
| Polynomial drift | The same 8,900 readings recover 49 unknown integers under arbitrary quintic drift at multiscale noise radius 0.000016 | Sharper degree-six bounds and a complete finite-precision implementation |
| Spatial sensing | 50 rows retain >99% of the original central floors; 48 retain >97%, with the previous noise allowances | A much smaller separated-row bank; four real rows are necessary, with sufficiency unresolved |

## Harmonic recovery: an entire design region fails

The previous short schedule separated all product vertices but had one certified interior collision. The extension allows every one of its six observation times to vary independently by **±0.000025**. Every schedule in this complete box still separates all 64 product vertices with factor floor greater than **1.03**, yet has two strictly interior product sources with exactly equal responses. All probabilities exceed 0.07 and the factor separation exceeds 0.79.

The failed question is explicit: the probability of exponent one in the prime-3 factor takes the two values

\[
0.083208071567702588,\qquad 0.63280942665025819.
\]

For every schedule in the box, an observation therefore has scalar-answer diameter at least **0.549601355082555602**. Any deterministic scalar estimate has noiseless worst-case error at least **0.274800677541277801**. The bit asking whether that probability exceeds one half is also impossible to recover uniformly there.

The source pair changes with the schedule. A moving affine center and a uniform contraction prove its existence throughout the parameter box; independent factored and 64-label response calculations reproduce the certificate at 256 and 384 bits. The box is small and conservative. It excludes a nonzero region around this schedule, not every schedule below time 30.

This gives the common framework a concrete negative witness: a large answer ambiguity can persist even when a finite surrogate source set is robustly separated. [Harmonic theorem and certificate](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/harmonic/PROOFS.md).

## Preparation: calibration uncertainty differs from a known offset

Inspection of the existing Atlas and ensemble calibration chamber found reproducible **synthetic** testing. The chamber compares RK4 forecasts with Dormand–Prince outcomes from the same equations and samples disclosed perturbation laws. Its audit explicitly excludes physical calibration. No measured eight-coordinate A+B preparation record was identified in the inspected local material. The available Windows compute host was not needed for these mathematical reconstructions.

The new bridge conditions on a record of measured initial-state centers, separate launch residuals, and one systematic instrument correction shared across both launches:

\[
p_A=m_A+b+v_A,\qquad p_B=m_B+b+v_B.
\]

Known offsets m consume the validated outer-domain allowance. They cancel when comparing two explanations of the same calibration record, so the remaining widths control ambiguity. The shared correction b is projected through the sum of the two launch sensitivity columns before taking absolute values. This retains correlation that independent bounds would discard.

An explicitly synthetic interior specification uses local radii 5×10⁻⁶ except 3×10⁻⁶ for B's first angle, shared systematic radii 10⁻⁶, and known offsets up to 5×10⁻⁶. Its complete support stays inside the previously validated 10⁻⁵ preparation box. At weighted output-noise radius 10⁻⁷ it gives source diameter **below 0.000060053**, with more than **35.79%** slack in the target inequalities. For target diameter 10⁻⁴, the same record has a sufficient noise boundary above **0.0000024787**.

Two controls identify the gain. Enclosing the record by a zero-centered box fails the same sufficient target test. Treating the common systematic correction independently at A and B also worsens the bound. Neither failed control proves physical impossibility.

The delivered protocol, schema, and exact checker specify the coordinate units, clock convention, launch incidence, correction intervals, evidence references, and acceptance criteria. The guarantee concerns the infinity-norm diameter of the logarithmic parameter/shared-clock source and its projection to the two logarithmic physical parameters. Calibration observations and reference characterization add resources beyond the five dynamical outputs. **Physical calibration remains NOT_RUN.** [Calibration protocol](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/CALIBRATION_PROTOCOL.md) · [Complete proof](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/PROOFS.md).

## Arithmetic queries: use uncertain information without guessing it

After certifying a(2),a(3), the new decoder enumerates all nine possibilities for a(5),a(7). Sixteen retained coefficients include nonlinear prime-power information at 25 and 49 and multiplicative information at 35 and 50. Every one of the resulting 81 anchor/template combinations has an independently checked actual quadratic-field witness; discriminants at most **1,365** suffice.

The decoder keeps every template compatible with directional slabs derived from the complete tail and the actual weighted sensor-noise norm. It answers a(5) when all surviving templates agree. It can therefore use a(7) without requiring a separate correct estimate of it. Its decision never selects a budget from the unknown true template.

All 81 conditional sufficient radii are at least those of the previous Q3 query under the same anchors, readings, and norm. The largest relative boundary gain exceeds **0.4%**. The largest absolute declared radius is **0.02332810**, when 2,3,5,7 all split; its boundary improvement over the previous query is over **0.3560%**. These are modest gains, not another order-of-magnitude change.

The worst-case boundary remains exactly unchanged. For inert7 and the pair a(5)=0 versus1, the added coordinates carry no further separation. This equality is a useful limit of the new certificate. Explicit numerical-error bounds can be supplied to the decoder; the canonical radius table assumes the exact sensing inverse. [Joint query proof and implementation](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/quadratic/PROOFS.md).

## Polynomial drift: a controlled complexity/noise tradeoff

The centered degree-14 arithmetic acquisition now handles drift beyond the previous affine baseline. The source normalization a(1)=1 is retained, and the remaining 49 integers through index 50 are recovered from the same **8,900 readings**.

| Maximum polynomial drift degree | Multiscale weighted noise radius | Outer-window weighted noise radius |
|---|---:|---:|
| One | 0.000097 | 0.000077 |
| Two | 0.000090 | 0.000070 |
| Three | 0.000077 | 0.000057 |
| Four | 0.000053 | 0.000033 |
| Five | 0.000016 | Present sufficient gate fails |
| Six | Present sufficient gate fails | Present sufficient gate fails |

Each column uses its own declared positive weighted norm. The drift coefficients may be arbitrary complex numbers in the exact mathematical model. A weighted polynomial basis, complete nuisance-tail channels, and a multi-channel Schur bound prove the table. Using each polynomial's actual weighted absolute norm sharpens the complete tail estimate enough to move the multiscale quintic bias bound from above 0.5541 to below **0.459148827331**, crossing the rounding threshold.

Degree-five or degree-six failures in the table limit this sufficient bound. A separate exact obstruction shows why unrestricted nuisance complexity must eventually fail: a polynomial of degree 8,899 can interpolate every response difference on the 8,900 distinct timestamps. An unknown first coefficient would also alias constant drift exactly.

This is the strongest application extension of the new package. The theorem accounts for the complete infinite arithmetic tail and digital correction error. A deployed solve must additionally bound finite-precision error, and nonpolynomial residual drift needs its own observation-error budget. [Polynomial-drift proofs and scope](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/noise/PROOFS.md).

## Spatial sensing: roughly halve acquisition

With n=1001, a two-dimensional source, known time τ∈[1,2], and unknown target among the 21 integer positions 490 through 510, the former 99-row window can be replaced by **50 asymmetric rows, 476–525**, retaining more than **99%** of every original central information floor. A **48-row** bank, 477–524, retains more than **97%**.

Both preserve the previous source-relative noise allowances: 3×10⁻⁷ times the L² source norm, or 3×10⁻⁸ times the relevant H¹ source norm. The source calibrations remain distinct. Target localization and relative source error below 10⁻³ remain certified. At relative output noise 10⁻³, the centroid errors are below **0.100347** and **0.130178** cells respectively.

The proof bounds transverse propagation directly through weighted state energy, retaining the full noncommuting finite generator. It charges both missing information and missing energy first moment. This is necessary because a positive source information floor alone does not identify an unknown target.

A new necessary benchmark is **at least four real rows** for unrestricted joint recovery of a two-dimensional source and more than one target label. With three rows, two injective two-dimensional source-image spaces must intersect in a nonzero response, causing a noiseless ambiguity. Four-row sufficiency and minimal robust acquisition remain open.

The channel savings apply when these spatial-average readouts can be acquired directly. Each row still averages globally in the other coordinate. Computing the smaller bank from already acquired full modal data is post-processing; it does not reduce the number of measurements already acquired. [Sensing-bank proof](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/resolution/PROOFS.md).

## Conclusions and the next decisions

The unification has produced a useful distinction between three actions. An exact nuisance quotient can preserve the answers; a controlled approximation can give a safe outer set; a restricted experiment can reduce cost while losing information. Each action needs its own mathematical justification. Known deterministic centering is invertible, so the earlier 127× improvement concerns a decoder and its certificate, while intrinsic information in the fixed acquisition remains unchanged.

The next focused work should sharpen the degree-six nuisance channels and certify selected, separated spatial readouts against the four-row benchmark. The harmonic branch suggests adding a measurement that separates its complete collision family. The arithmetic query suggests exact directional Gram bounds or joint bias/noise optimization. The preparation protocol is ready for a measured record once an apparatus and its calibration evidence are available; more synthetic samples cannot supply that evidence.

All six proof tracks have separate audits. The consolidated validation covers **49 focused tests**, complete new harmonic and polynomial numerical reconstructions, exact arithmetic and transfer checks, the preparation ODE replays, and a 192-case full finite-graph diagnostic. The [reproduction guide](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/README.md) identifies inherited complete-tail and central-resolution premises. These are mathematical guarantees under declared models, with explicit remaining trusted components; no historical-priority or empirical apparatus claim is made.
