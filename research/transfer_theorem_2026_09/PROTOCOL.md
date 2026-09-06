# Goal: a developed transfer theorem with demonstrated consequences

User authorization, 2026-09-05: pursue the shared transfer theorem using the goal function, with sharper degree-six arithmetic drift bounds and smaller separated spatial sensing banks as the next applications. The active goal has no user-specified token budget.

## Acceptance criteria

1. State a complete experiment contract: source and query, structured nuisance incidence, actual observation-error set and metric, acquisition map, model approximation, and numerical error.
2. Prove exact elimination and restriction conditions, including the correctly transported noise metric, a criterion for when preprocessing can be implemented from retained measurements, and the distinction between exact answer-set preservation and conservative recovery transfer.
3. Give quantitative, implementable sufficient bounds for transferring discrete and continuous query guarantees. Recover prior certificates in at least two distinct models through a common checked interface.
4. Pursue both next applications. Obtain at least one additional rigorously certified improvement or obstruction beyond `unified_query_2026_09`. A failed sufficient inequality is not an impossibility result. Record the outcome and successor for both targets.
5. Independently audit the central theorem and decisive application claims, run appropriate exact or outward model reconstructions and adversarial tests, and publish a concise local synthesis and reproduction guide. Update the current-state index after completion.

## Working boundaries

The earlier research packages and conversations remain historical records. Their initial file identities are recorded in `PREVIOUS_ARTIFACTS_SHA256.json`; identity checks establish preservation, not mathematical validity. The new work is isolated here. Root owns the framework and integration; separate agents develop drift and sensing, with a fourth independent framework reviewer. Completed application work will receive a separate audit.

General linear algebra and optimal-recovery facts receive complete proofs and primary-source context where appropriate. No claim of historical novelty follows from a new local derivation. Infinite arithmetic tails, continuous observation times, arbitrary source directions and shared errors must be handled under their actual quantifiers, not replaced by sampled controls. Numerical examples can check implementations but do not substitute for the uniform theorem.

No physical calibration, deployment, publication, remote-machine use, or edits to other tasks are required by this mathematical goal. Existing calibration status remains unverified unless actual new empirical evidence is obtained.
