/* Global Geometry II — machine-readable elementary theorem ledger. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory(require("./global-geometry-ii-core.js"));
  } else {
    root.GlobalGeometryIIClaims = factory(root.GlobalGeometryII);
  }
})(typeof self !== "undefined" ? self : this, function (G2) {
  "use strict";

  if (!G2) throw new Error("Global Geometry II claim ledger requires GlobalGeometryII.");

  function provedHere(spec) {
    return G2.createEvidenceRecord({
      id: spec.id,
      claim: spec.claim,
      status: "proved",
      basis: "proved-here",
      scope: spec.scope,
      method: spec.method,
      falsifier: spec.falsifier,
      proofAnchor: "GLOBAL_GEOMETRY_II_FOUNDATIONS.md " + spec.anchor,
      assumptions: spec.assumptions || [],
      artifacts: spec.artifacts || ["GLOBAL_GEOMETRY_II_FOUNDATIONS.md"],
      tests: spec.tests || [],
      limitations: spec.limitations || [],
      dependencies: spec.dependencies || [],
      result: { theoremId: spec.anchor.split(" ")[1], conclusion: spec.conclusion || "proved in declared finite scope" }
    });
  }

  var claims = [
    provedHere({
      id: "ggii.theorem.p3.1.causal-cone",
      anchor: "Proposition 3.1",
      claim: "A synchronous radius-R local rule on fixed adjacency has an exact radius-RT causal cone after T steps.",
      scope: "Deterministic synchronous L0 rules on a fixed declared adjacency, with identical broadcasts when L1 data are present.",
      method: "Induct on the number of synchronous updates and the nested neighborhoods each update can read.",
      falsifier: "Two matched initial states agreeing on the radius-RT neighborhood produce different root states within T updates without an adjacency rewrite or differing broadcast.",
      assumptions: ["fixed adjacency", "synchronous writes", "bounded read radius", "equivariant local kernel"],
      tests: ["release-1 L0 causal-cone fixture"],
      limitations: ["not valid across undeclared structural rewrites", "requires a fixed combinatorial bound for metric-defined neighborhoods"]
    }),
    provedHere({
      id: "ggii.theorem.p3.2.relabeling",
      anchor: "Proposition 3.2",
      claim: "Neighborhood-isomorphism local kernels with equivariant synchronous commit commute with every carrier relabeling.",
      scope: "Finite decorated carriers and rules that exclude absolute IDs and serialization order from their read semantics.",
      method: "Transport every rooted decorated neighborhood and corresponding write through the carrier isomorphism.",
      falsifier: "A carrier permutation changes an intrinsic output while all neighborhood data and conflict resolution are transported equivariantly.",
      assumptions: ["rooted-neighborhood isomorphism invariance", "equivariant commit"],
      tests: ["release-1 relabeling invariance fixtures"]
    }),
    provedHere({
      id: "ggii.theorem.p3.3.fixed-topology",
      anchor: "Proposition 3.3",
      claim: "State-only updates on a fixed finite carrier preserve its homology and Euler characteristic.",
      scope: "Any trajectory whose cell sets and boundary operators remain unchanged.",
      method: "The chain groups and boundary matrices are identical at every time, so their ranks, kernels, images, and alternating cell count are identical.",
      falsifier: "A combinatorial invariant changes while every cell and boundary matrix remains byte-identical.",
      assumptions: ["no carrier rewrite"],
      tests: ["topology remains constant under release-1 diffusion and curvature steps"],
      limitations: ["scale-dependent inferred topology may change even when exact carrier topology does not"]
    }),
    provedHere({
      id: "ggii.theorem.p3.4.local-indistinguishability",
      anchor: "Proposition 3.4",
      claim: "No deterministic equivariant radius-R observer running for T rounds distinguishes roots with isomorphic radius-RT decorated neighborhoods and matched broadcasts.",
      scope: "Bounded-round deterministic distributed recognition on declared rooted decorated carriers.",
      method: "Couple the two executions through the rooted isomorphism and apply the causal-cone and equivariance propositions.",
      falsifier: "A bounded observer returns different root histories for two coupled radius-RT-identical inputs.",
      assumptions: ["deterministic observer", "equivariant local rule", "matched broadcasts"],
      dependencies: ["ggii.theorem.p3.1.causal-cone", "ggii.theorem.p3.2.relabeling"],
      limitations: ["does not restrict observers with growing radius or trusted global data"]
    }),
    provedHere({
      id: "ggii.theorem.p4.1.triangle-gluing",
      anchor: "Proposition 4.1",
      claim: "Positive shared edge lengths satisfying strict triangle inequalities define a piecewise-Euclidean triangular length space; valid vertex links make it a surface with boundary.",
      scope: "Finite triangular complexes with one authoritative length per abstract edge.",
      method: "Apply side-side-side realization facewise, glue equal edge copies isometrically, and use the path/cycle link criterion.",
      falsifier: "A face satisfying all strict inequalities lacks a Euclidean SSS realization, or equal shared edges cannot be glued isometrically.",
      assumptions: ["strict face inequalities", "shared-edge length consistency", "valid links for the surface conclusion"],
      tests: ["release-1 surface-validity and intrinsic-curvature fixtures"],
      limitations: ["intrinsic construction does not prove an embedding in three-space"]
    }),
    provedHere({
      id: "ggii.theorem.p4.2.circle-face-compatibility",
      anchor: "Proposition 4.2",
      claim: "Positive tangency-circle radii with edge lengths l_ij=r_i+r_j satisfy every strict triangular face inequality.",
      scope: "Triangular faces in the positive tangency circle-packing metric.",
      method: "Each triangle slack reduces exactly to twice the radius at the intervening vertex.",
      falsifier: "Positive radii yield a nonpositive triangle slack under l_ij=r_i+r_j.",
      assumptions: ["strictly positive radii", "tangency length law"],
      tests: ["circle-packing length property fixtures"],
      limitations: ["does not establish prescribed-curvature realizability"]
    }),
    provedHere({
      id: "ggii.theorem.p4.3.gauss-bonnet",
      anchor: "Proposition 4.3",
      claim: "Angle defects on a finite nondegenerate triangulated surface, using interior target angle 2pi and boundary target angle pi, sum to 2pi times Euler characteristic.",
      scope: "Compact finite triangular two-manifolds with boundary and nondegenerate Euclidean faces.",
      method: "Sum face angles, use 3F=2E_i+E_b and E_b=V_b, then identify the Euler alternating count.",
      falsifier: "An exact valid triangulation violates the symbolic angle-count identity under the stated boundary convention.",
      assumptions: ["valid surface links", "nondegenerate Euclidean triangles", "declared boundary convention"],
      tests: ["release-1 disk, sphere, puncture, and invalid-surface fixtures"],
      limitations: ["floating residuals are computational audits", "the total condition is not sufficient for a target metric"]
    }),
    provedHere({
      id: "ggii.theorem.p4.4.laplacian-nullity",
      anchor: "Proposition 4.4",
      claim: "The zero-eigenvalue multiplicity of the symmetric normalized Laplacian equals the number of connected components.",
      scope: "Finite undirected graphs with positive edge weights and the declared zero-block isolated-vertex convention.",
      method: "Characterize the kernel from the nonnegative Dirichlet quadratic form component by component.",
      falsifier: "An eligible graph has normalized-Laplacian nullity different from its component count.",
      assumptions: ["undirected graph", "positive edge weights", "declared isolated-vertex convention"],
      tests: ["release-1 connected and disconnected spectral fixtures"]
    }),
    provedHere({
      id: "ggii.theorem.p4.5.flux-conservation",
      anchor: "Proposition 4.5",
      claim: "A symmetric edge-flux update conserves the declared measure-weighted total exactly in algebra.",
      scope: "Finite graphs with symmetric nonnegative conductance and the stated antisymmetric neighbor-difference update.",
      method: "Pair and cancel the two oriented contributions of every undirected edge.",
      falsifier: "The symbolic weighted sum changes under a finite symmetric flux update.",
      assumptions: ["symmetric conductance", "same edge flux used at both endpoints"],
      limitations: ["conservation alone does not ensure positivity or time-step stability"]
    }),
    provedHere({
      id: "ggii.theorem.p5.1.radius-identifiability",
      anchor: "Proposition 5.1",
      claim: "When circle-radius edge-sum equations are solvable on a connected graph, radii are unique exactly when the graph is nonbipartite; a bipartite graph retains a one-dimensional alternating gauge.",
      scope: "Connected finite graphs and real solutions of r_i+r_j=l_ij on every edge.",
      method: "Differences of two solutions alternate sign along paths; an odd cycle forces the root difference to zero.",
      falsifier: "A solvable connected nonbipartite instance has two radius solutions, or a connected bipartite instance has a homogeneous solution outside the alternating line.",
      assumptions: ["connected carrier", "edge-sum system is solvable"],
      limitations: ["positivity bounds restrict but do not generally remove the bipartite gauge"]
    }),
    provedHere({
      id: "ggii.theorem.p5.2.metric-stability",
      anchor: "Proposition 5.2",
      claim: "Changing every edge length of a fixed connected N-vertex graph by at most epsilon changes every shortest-path distance by at most (N-1)epsilon.",
      scope: "Fixed finite connected graphs with positive edge lengths.",
      method: "Evaluate each old shortest simple path in the perturbed metric and reverse the argument.",
      falsifier: "A pairwise distance changes by more than (N-1) times the maximum edge perturbation.",
      assumptions: ["fixed graph", "positive lengths", "connectedness"],
      limitations: ["a useful refinement bound additionally requires the rescaled factor to vanish"]
    }),
    provedHere({
      id: "ggii.theorem.p5.3.deterministic-replay",
      anchor: "Proposition 5.3",
      claim: "A closed deterministic generator, seed, parameter record, broadcast sequence, and synchronous update determine one finite trajectory.",
      scope: "Finite computations without undeclared nondeterministic inputs.",
      method: "The initial state is fixed by the closed record; induction fixes each subsequent deterministic update.",
      falsifier: "Two executions with the identical closed record produce different exact finite states before environment-only metadata.",
      assumptions: ["deterministic generator", "canonical serialization", "fixed seed", "deterministic updates"],
      tests: ["release-1 replay fixtures", "Global Geometry II checksum and manifest fixtures"],
      limitations: ["floating libraries may require schema-aware tolerance rather than byte equality"]
    }),
    provedHere({
      id: "ggii.theorem.p6.1.metric-null-subdivision",
      anchor: "Proposition 6.1",
      claim: "Straight inherited subdivision of a piecewise-Euclidean complex is isometric to the original piecewise-Euclidean realization.",
      scope: "Facewise straight subdivisions with consistent shared-edge subdivisions and inherited Euclidean lengths.",
      method: "The identity on every old face preserves every rectifiable path length before and after partition.",
      falsifier: "A path changes intrinsic piecewise-Euclidean length under a purely inherited straight subdivision.",
      assumptions: ["same face metrics", "consistent edge subdivisions", "piecewise-Euclidean path metric"],
      limitations: ["a changed graph one-skeleton distance is not the same metric"]
    }),
    G2.graphMetricNonuniversalityControl().evidence,
    G2.diffusionFiniteDimensionalUniversalityControl().evidence,
    G2.robustWhitenedDiffusionUniversalityControl().theoremEvidence
  ];

  function validateLedger(records) {
    var errors = [], ids = Object.create(null);
    if (!Array.isArray(records)) return { valid: false, errors: ["claim ledger must be an array"] };
    records.forEach(function (record, index) {
      var report = G2.validateEvidenceRecord(record);
      if (!report.valid) errors.push("record " + index + ": " + report.errors.join("; "));
      if (record && ids[record.id]) errors.push("duplicate claim id " + record.id);
      if (record) ids[record.id] = true;
    });
    records.forEach(function (record) {
      (record && record.dependencies || []).forEach(function (dependency) {
        if (!ids[dependency]) errors.push("missing dependency " + dependency + " for " + record.id);
      });
    });
    return { valid: errors.length === 0, errors: errors, count: records.length };
  }

  var validation = validateLedger(claims);
  if (!validation.valid) throw new Error("Invalid Global Geometry II claim ledger: " + validation.errors.join("; "));
  Object.freeze(claims);

  function listClaims() { return claims.slice(); }
  function getClaim(id) { return claims.find(function (record) { return record.id === id; }) || null; }

  return {
    VERSION: "0.2.0-alpha.4",
    CLAIMS: claims,
    listClaims: listClaims,
    getClaim: getClaim,
    validateLedger: validateLedger
  };
});
