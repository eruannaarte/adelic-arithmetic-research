# Harmonic acquisition: nonidentifiability persists under time perturbations

**A whole open neighborhood of the earlier short schedule fails to identify the full source, while continuing to separate every product vertex.** The new result rules out a design region, and identifies a specific scalar and bit query that remain impossible there.

For the six times

\[
(15.790052,25.962780,28.039208,28.695603,29.332467,29.966619),
\]

allow each reading time to vary independently by at most **0.000025**. Every schedule in this entire six-dimensional box has both of these properties:

- Its factor-distance separation floor on all 64 product vertices exceeds **1.03**.
- Two strictly interior product distributions have exactly equal six complex responses, every factor probability exceeds **0.07**, and their factor distance exceeds **0.79**.

The maximum time remains below 30. The collision pair varies with the schedule. This does not assert that one fixed pair remains indistinguishable at all perturbed times, or that every schedule below 30 fails.

The failed query can be made explicit. Let \(Q(q)=q_{2,1}\), the probability of exponent one in the prime-3 factor. At the same observation, the two certified sources give

\[
Q(q)=0.083208071567702588,
\qquad Q(r)=0.63280942665025819.
\]

These coordinates were deliberately kept fixed while the remaining source coordinates adapt to the times. Thus the query answer set has diameter at least **0.549601355082555602**. Any deterministic estimate has worst-case absolute error at least **0.274800677541277801**, even without sensor noise. The bit “is this probability greater than one half?” also cannot be recovered uniformly.

This advances the previous isolated collision in two ways. It proves that failure survives arbitrary small independent changes to all six readings, and it turns full-source nonidentifiability into an explicit obstruction for a specified low-dimensional question. A robust positive vertex certificate therefore supplies no positive guarantee for that question over the full product-distribution source class.

The proof uses a source center that moves affinely with the times, followed by a uniform interval contraction in twelve active source coordinates. The affine predictor cancels the first-order timing response sufficiently to bound the residual over the entire parameter box. The complete derivative and phase calculation is reconstructed from the prime-labelled model. The factored calculation has contraction bound **0.218567913** and maps its root box into **31.56%** of its radius. A separate expansion into all 64 integer-labelled terms also proves the root gate, mapping into **78.72%** of the radius. Both calculations pass at 256 and 384 bits, with identical exported rational certificates. The resulting collision branch is also Lipschitz in the times, with bound **3.567017552** in the combined pair's complement-coordinate infinity norm.

The useful conclusion for unified query recovery is precise: a design region can have a certified positive separation bound on a finite surrogate source set and still have a large noiseless answer-set diameter for actual admissible sources. The full answer-set condition must be checked on all relevant source differences, including interior pairs. The parameterized contraction supplies a reusable way to certify persistent collisions in other smooth finite-dimensional models.

The radius **0.000025** is conservative and small; its importance is the proved nonzero neighborhood, not a claim of a large or maximal forbidden region. The six-time schedule remains only one local design region. Larger boxes rejected by this particular contraction do not establish the behavior of the true inverse problem outside it.

The next concrete objective is to add a seventh measurement that separates the entire certified collision branch, and then check whether the augmented design also controls other full-source differences. As an alternative, a validated continuation of this branch could expand the forbidden design region. A seventh reading that merely separates the recorded center pair would be insufficient: the full parameterized branch must be covered.

[Complete theorem and proofs](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/harmonic/PROOFS.md) · [Reproduction guide](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/harmonic/README.md) · [Objective and successor record](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/harmonic/OBJECTIVE.md)
