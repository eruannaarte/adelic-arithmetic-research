**Math research review — strongest findings and next priorities**

Reviewed September 4, 2026, America/Costa_Rica. Repository snapshot: `3d71fade83f57c6fcdb4b044145c44084af589ab`.

The strongest outcome of this project is a connected theory and software framework for deciding which distinctions finite measurements preserve, certifying their robustness, and designing better experiments. Its most promising mathematical results concern restricted harmonic reconstruction, arithmetic tails, nuisance uncertainty, and the resolution needed for stable observation. The initial geometric motivation has led to concrete inverse problems with explicit success and failure criteria.

This assessment draws on the [public research ledger](https://thegodnet.work/number-geometry/), the four available Math research tasks—“Assess Math files and ideas,” “Operational Information Geometry.”, “Double-pendulum Operational Atlas,” and “Explore an interesting math subject”—and their central manuscripts, later corrections, audits, and selected artifacts. Task histories were paginated selectively. Some public Atlas links were unavailable through the web reader; the corresponding local manuscripts were reviewed. This is research triage with selected proof inspection and fresh checks, not an exhaustive independent verification of every manuscript.

The ordering below weighs explicit mathematical content, strength of evidence, usefulness beyond the example, and the availability of a decisive next step. Publication priority has not been established. “Theorem” refers to a statement with a proof in the manuscript, not external peer review or proof-assistant verification.

| Priority | Finding | Strongest reason to pursue it | Present boundary |
|---|---|---|---|
| 1 | Query-directed, nuisance-aware certified experiment design | A reusable tool with exact witnesses and a nonlinear application | Guarantees depend on a declared model and calibrated uncertainty |
| 2 | Sharp harmonic reading complexity | A compact theorem with matching constructive and impossibility arguments | Restricted product models; reading count excludes acquisition time |
| 3 | Certified multiscale arithmetic sensing | Complete infinite-tail control changes a failed recovery certificate into a successful one | The headline degree-14 recovery is noiseless |
| 4 | Discrete queries, common uncertainty, and arithmetic convexification | Explains why apparently similar recovery problems have different answers | Independent coefficient envelopes are broader than genuine number-field data |
| 5 | Resolution-aware transfer and spectral limits | Connects continuum mathematics to finite measurements quantitatively | Strong results for specific models; some bounds remain very conservative |
| 6 | Finite order–factorization acceleration | A simple, well-defined open number-theory direction with exact finite evidence | The asymptotic rate and sparse-support laws remain conjectural |
| Exploratory | Global Geometry and inverse design | Useful obstruction certificates and observable-dependent notions of universality | The broader U2 evaluation remains unresolved |

**1. Certified experimental design is the strongest application direction.**

The engine can ask for a particular quantity rather than requiring recovery of an entire hidden state. For data `y = Hx + Bz + noise`, it removes the allowed nuisance directions and tests whether every remaining invisible source change also leaves the requested quantity unchanged. A successful certificate supplies a decoder and an error bound; failure supplies an explicit indistinguishable pair or direction. This is useful because full-state blindness need not prevent a valuable partial answer. [Exact query theorem](/Volumes/KINGSTON/Vibecoding/Math/OIG_QUERY_PROTOCOL_DESIGN_THEOREM.md:32).

The design layer brackets an achieved information level against an upper bound on the optimum. Its four-state Markov example certifies at least **97.253% efficiency** within the declared design problem. During this review, an independent implementation using exact rational arithmetic reconstructed its quotient, five information forms, budget, and primal/dual witnesses. [Design engine](/Volumes/KINGSTON/Vibecoding/Math/OIG_PROTOCOL_DESIGN_ENGINE.md:149).

The most convincing application is the double pendulum. Two scalar readings can identify two local parameters when no nuisance is present, but one nonzero unrestricted clock or gain direction reduces the effective rank to one. Grouping five readings across two launches and eliminating one clock direction shared across the experiment restores a certified information floor **greater than 0.0180269**. This demonstrates a complete reasoning cycle: detect confounding, redesign observations, and certify the repaired experiment. The result applies at the stated nominal parameters, with exact launch preparation and the declared noise metric; it is not uniform over finite clock shifts or a physical parameter neighborhood. [Rank obstruction](/Volumes/KINGSTON/Vibecoding/Math/DOUBLE_PENDULUM_STRUCTURED_PHYSICAL_NUISANCE.md:176); [grouped transfer theorem](/Volumes/KINGSTON/Vibecoding/Math/DOUBLE_PENDULUM_GROUPED_VALIDATED_TRANSFER_TIER3.md:3).

Another striking certificate compresses 172 modal outputs into two global linear statistics with information loss below `1.95e-37`. Its practical meaning requires care: these statistics combine the full field, and the tiny loss concerns tightly enclosed numerical response error. It does not establish equivalence to two local hardware detectors. [Matched-frame audit](/Volumes/KINGSTON/Vibecoding/Math/OIG_NEUMANN_MATCHED_FRAME_AUDIT.md:15).

**Next priority:** add a realistic preparation-error bound and realizable sensor constraints to one application. Compare its certified query error with uniform sampling and an established optimal-design method under identical noise and cost assumptions. The new value to establish is a usable guarantee or acquisition advantage. Estimability, nuisance projection, and optimal design have substantial existing literature; [Rosa and Harman’s nuisance-resistant design paper](https://arxiv.org/abs/1504.06079) is one relevant comparison.

**2. The sharp harmonic reading count is the clearest focused theorem candidate.**

For a labelled product of `r` probability distributions, each supported on the known prime-exponent alphabet `0,...,s-1`, Arithmetic Observability VI gives the exact global harmonic reading count

`m = r floor(s/2)`.

A constructive schedule achieves global identification with a stability bound. Every smaller schedule admits exact collisions; for even `s`, a reflection/topological argument is stronger than ordinary dimension counting. For three factors with four states each, six complex readings are necessary and sufficient in this access model. Inspection of the upper and lower proofs found no obvious gap under their stated assumptions. [Constructive theorem](/Volumes/KINGSTON/Vibecoding/Math/ARITHMETIC_OBSERVABILITY_VI.md:295); [matching lower bound and exact count](/Volumes/KINGSTON/Vibecoding/Math/ARITHMETIC_OBSERVABILITY_VI.md:538).

This deserves attention because a sharp count with a matching obstruction is more informative than a successful numerical reconstruction. However, it assumes known labels and exact product structure. The canonical six-reading schedule extends to approximately 220,023 in the declared time coordinate: minimizing the number of readings does not minimize time, precision, or clock sensitivity. [Canonical schedule](/Volumes/KINGSTON/Vibecoding/Math/ARITHMETIC_OBSERVABILITY_VI.md:615).

**Next priority:** derive the count-versus-time-versus-noise tradeoff, including small departures from product structure. This would turn a strong identification theorem into an acquisition theorem. A focused manuscript and specialist literature comparison would be more useful than adding another broad synthesis layer.

**3. Arithmetic Sensing V provides the strongest complete computational recovery result.**

At `N=50` and `sigma=2`, the positive nested measure

`(125/65536) mu_(510,2550) + (65411/65536) mu_(1780,8900)`

uses **8,900 distinct readings**, because the short grid is contained in the long one. For integer coefficients under the degree-14 divisor envelope, its full coefficient-bias endpoint is **0.4980274167750795**, below the `1/2` rounding threshold. The same-grid single-window control has endpoint **0.5959293953409309**. The changed weights therefore improve the sufficient certificate on the same acquisition grid. [Canonical synthesis](/Volumes/KINGSTON/Vibecoding/Math/ARITHMETIC_SENSING_V_COMPLETE.md:335); [public article](https://thegodnet.work/number-geometry/arithmetic-sensing-v-multiscale-stopping/).

The substantial achievement is control of the complete omitted tail: exact continuum positivity, directed rounding, positive logarithmic convolution, cancellation-preserving bounds, and finite Gram correction work together. A finite truncation is not silently treated as the full Dirichlet series.

The headline theorem is explicitly **deterministic noiseless recovery**. Its remaining uncentered coefficientwise rounding margin is only about **0.00197258**; extra sensor error must be propagated through the decoder and fit the remaining budget. A noise advantage has not been proved. [Precise recovery statement](/Volumes/KINGSTON/Vibecoding/Math/ARITHMETIC_SENSING_V_MULTISCALE.md:332).

A separate stopping theorem shows that the chosen short-scale support beats every competing support in the declared two-scale family for finite target-50 leakage through one million. Its positive separation is approximately `5.0873e-7`. This does not establish optimality for arbitrary sensing measures, all-target recovery, or even exact weight optimality on the chosen support. [Stopping theorem](/Volumes/KINGSTON/Vibecoding/Math/ARITHMETIC_SENSING_V_RESIDUAL_STOPPING.md:239).

**Next priority:** optimize the full noise-aware recovery objective at a fixed acquisition budget, and compare against established stable reconstruction methods. [Adcock, Hansen, and Poon’s generalized-sampling analysis](https://arxiv.org/abs/1301.2831) provides a relevant stability/optimality baseline; it does not by itself settle the novelty of this arithmetic specialization.

**4. Discrete queries and uncertainty structure produce a valuable theory of information limits.**

Arithmetic Observability VII proves an instructive distinction. Independently variable continuous tail coefficients can span a neighborhood of every finite measurement vector. They can conceal arbitrarily small continuous source changes, causing exact local ambiguity. A separated query alphabet—such as integer labels—can nevertheless remain identifiable if its gap exceeds the allowed tail variation. The result explains why recovering a few arithmetic labels can be feasible when exact continuous reconstruction is impossible. [Tail-spanning and no-go proofs](/Volumes/KINGSTON/Vibecoding/Math/ARITHMETIC_OBSERVABILITY_VII.md:852).

The later papers improve robust separation by preserving the actual common uncertainty set and removing irrelevant prefix directions before bounding the tail. For the four queried coefficients `{1,2,3,5}` in the pinned model, the critical adversarial noise radius lies between approximately **0.0199913430 and 0.0200000000**, a relative gap of about **0.0433%** in the declared weighted measurement norm. This is a substantially sharper information-limit statement than a successful reconstruction trial. [Quotient lower bound](/Volumes/KINGSTON/Vibecoding/Math/ARITHMETIC_OBSERVABILITY_IX.md:1365); [latest integral upper witness](/Volumes/KINGSTON/Vibecoding/Math/ARITHMETIC_OBSERVABILITY_X.md:1594).

Arithmetic Observability X also identifies when replacing integral uncertainty by its convex hull changes the true answer. Equality requires the closest convex response to be integrally realizable; this remains unresolved in the pinned example. Its more distinctive structural result is that positive-distance optimal tails cannot have finite support: finite witnesses approximate the optimum but remain improvable. That changes how an optimizer should be sought. [Convexification gap](/Volumes/KINGSTON/Vibecoding/Math/ARITHMETIC_OBSERVABILITY_X.md:823); [infinite-support theorem](/Volumes/KINGSTON/Vibecoding/Math/ARITHMETIC_OBSERVABILITY_X.md:1361).

The main limitation is arithmetic realizability. Independent divisor-bounded coefficient boxes include sequences that no number field produces. A recovery guarantee for the larger box transfers to a realizable subclass; an impossibility witness in the larger box need not. The near-matching envelope bounds therefore do not automatically identify the information limit for actual number fields.

**Next priority:** solve a smaller nontrivial case of integral-versus-continuous equality, or characterize a genuinely realizable arithmetic subclass and repeat the separation analysis there. This is a stronger conceptual advance than another minute improvement to the existing numerical upper endpoint.

**5. OIG’s finite-resolution and spectral results are a serious analysis direction.**

The work identifies precisely why an apparently informative continuum model can be misleading on a fixed finite grid. In the declared two-port Neumann problem, no fixed grid covers every late lattice time. A valid coupled estimate instead gives a finite-to-continuum error bounded by `23 sqrt(tau)/n` in the specified L2 source metric, with a different constant for H1. A practical interval certificate covers `n=1001` on `1 <= tau <= 6/5`. [Explicit transfer theorem](/Volumes/KINGSTON/Vibecoding/Math/OIG_UNIFORM_LATTICE_EXPLICIT_CONSTANTS.md:19).

The spectral continuation distinguishes exact visibility from stable recovery. It identifies the conditional-expectation blind space and proves that increasing bandwidth destroys any uniform positive information floor. For the affine-ramp cosine model, the manuscript derives squared-factorial upper ceilings, explicit `exp(-C K^2)` lower bounds, and determinant asymptotics. Specific spectral-ratio constants remain conjectural. [Growing-band theorem](/Volumes/KINGSTON/Vibecoding/Math/OIG_IX_GROWING_BAND_THEOREM.md:15); [spectral asymptotics](/Volumes/KINGSTON/Vibecoding/Math/OIG_X_SPECTRAL_ASYMPTOTICS.md:13).

These are promising specialized analysis results, but the global explicit transfer bound is conservative and the practical interval cover is narrow. The operational question is whether approximation error is small relative to the weakest informative direction, which may already be extremely small.

**Next priority:** prove a useful uniform second-order transfer bound and test target-placement perturbations, or isolate and prove/disprove the proposed spectral-ratio limit. Both are precise mathematical targets with clear success criteria.

**6. Finite arithmetic acceleration remains an attractive open number-theory project.**

Finite adjacent-order comparisons constrain a normalized additive prime weight. Using auxiliary primes and exact cancellation gives much tighter bounds than comparisons involving powers of two and three alone. At cutoff 100,000, the displayed certified interval for the weight of three is about **3,108 times narrower**, supported by 80 comparisons in total. The interval bounds are exact certificates; exact optimality at every large cutoff is not independently established. [Finite acceleration study](/Volumes/KINGSTON/Vibecoding/Math/ARITHMETIC_ACCELERATION.md:170).

At cutoff 100, the minimum-mass lower certificate improves from `5/7` to `3/7`, reducing its worst-case comparison-defect amplification by 40%. This review directly rechecked the exact minimum-mass primal/dual identities and the Farkas witness proving that comparison `80 < 81` is indispensable for the stated sharp lower endpoint. [Exact robustness results](/Volumes/KINGSTON/Vibecoding/Math/GLOBAL_INVERSE_RECONSTRUCTION.md:262).

The proposed width law `W_p(N) = N^(-1+o(1))` is a conjecture, with eight modest cutoffs providing evidence. It should explicitly exclude the normalization prime `p=2`, whose width is identically zero. The underlying infinite logarithmic rigidity is classical; the interesting open target is its finite quantitative rate, not the fact that an ordered additive coordinate becomes logarithmic. [Rate conjecture and elementary lower scale](/Volumes/KINGSTON/Vibecoding/Math/ORDER_FACTORIZATION_GEOMETRY.md:249); [classical context in Erdős–Ryavec](https://www.renyi.hu/~p_erdos/1972-01.pdf).

**Next priority:** find a structural upper-bound argument or a counterexample sequence, with exact finite witnesses for additional odd primes. A wider numerical scan is useful for falsification and conjecture refinement but cannot replace the missing asymptotic proof.

**Global Geometry is promising exploratory work, with a narrower current conclusion.**

Its clearest structural lesson is that square and triangular grids can share a covariance-normalized diffusion limit while retaining different limiting graph metrics. Universality depends on which structure is measured. Its most actionable tool is inverse design that returns a mathematical obstruction: one curvature target passes the total Gauss–Bonnet check but fails a circle-packing subset inequality by `-pi/5`. This rules out that target within the declared circle-packing class. [Metric/diffusion distinction](/Volumes/KINGSTON/Vibecoding/Math/GLOBAL_GEOMETRY_II_MANUSCRIPT.md:299); [subset obstruction](/Volumes/KINGSTON/Vibecoding/Math/GLOBAL_GEOMETRY_II_MANUSCRIPT.md:634).

The August 30 U2 report supersedes any broader impression of scientific completion from task summaries. Screening completed on both hosts, but only Gate 1 passes in the strict partial evaluation; Gates 2–8 are unresolved, and the full confirmatory campaign and physical validation have not run. Exact cross-platform record replication failed, while a rounded diagnostic agrees; neither fact settles U2. [Authoritative evaluation status](/Volumes/KINGSTON/Vibecoding/Math/GLOBAL_GEOMETRY_II_U2_EVALUATION_REPORT.md:10).

Further work should first complete decision-grade estimators, normalization use, and uncertainty aggregation. More preview runs alone cannot answer the registered universality question. The pendulum’s proposed optimal information horizon and persistent stability islands also remain hypotheses: current finite refinement and energy controls do not establish them as general effects.

**Verification and interpretation of this review.**

Fresh checks passed: 17 foundational arithmetic tests, six exact OIG constant tests, and 51 Arithmetic Observability corpus/integrity tests. The corpus payload verified. Independent exact-rational calculations reconstructed the Markov design certificate and the grouped pendulum’s Gram/Schur intervals and positive floor. The cutoff-100 rigidity optimality and indispensability witnesses also passed direct exact checks.

These 74 targeted tests have different purposes; the 51 corpus tests check integrity and scope handling, not analytic theorem truth. The complete repository suite was not rerun. Heavy Arb/MPFR tail, spectrum, and nonlinear ODE computations were inspected through their manuscripts and artifacts rather than regenerated, because the available runtime lacks their specialized dependencies. Historical test counts in other tasks were treated as historical evidence.

Most general ingredients are established mathematics. The strongest candidates for a distinct contribution are the precise arithmetic theorems, explicit transfer estimates, and composed certificate workflows. A focused external review should compare these specific results with prior work rather than assess novelty from the programme names. The early [validity audit](/Volumes/KINGSTON/Vibecoding/Math/AUDIT.md:5) remains important: the original coordinate constructions did not establish the proposed broader theory, while the later restricted problems have produced concrete mathematical results.

My recommended research sequence is: pursue the nuisance-aware OIG application with preparation uncertainty; prepare the sharp harmonic-count theorem for specialist review; develop the noise-aware arithmetic sensing comparison; then choose one focused analytic or finite-rigidity conjecture. Keep the broader universality programme exploratory until its existing evaluation requirements are met.
