/*
 * Global Geometry II — universality and inverse-design research core.
 *
 * This extension depends only on the release-1 Global Geometry core.  Its
 * first slice provides deterministic evidence records, replay manifests, and
 * a closed-form periodic-lattice spectral calibration evaluated in binary64.
 * It deliberately labels that calibration as profile evidence, not full
 * geometric universality.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory(require("./global-geometry-core.js"));
  } else {
    root.GlobalGeometryII = factory(root.GlobalGeometryCore);
  }
})(typeof self !== "undefined" ? self : this, function (Base) {
  "use strict";

  if (!Base) throw new Error("Global Geometry II requires GlobalGeometryCore.");

  var VERSION = "0.2.0-alpha.5";
  var SCHEMA_VERSION = 2;
  var EPS = 1e-12;
  var TAU = 2 * Math.PI;
  var EVIDENCE_STATUSES = ["proved", "computational", "conjectural", "engineering", "speculative"];
  var EVIDENCE_BASES_BY_STATUS = {
    proved: ["proved-here", "proved-external"],
    computational: ["finite-computation", "finite-ensemble"],
    conjectural: ["falsifiable-hypothesis"],
    engineering: ["model", "calibration", "physical-measurement"],
    speculative: ["interpretation"]
  };
  var DIGEST_ALGORITHM = "fnv1a32-canonical-json";
  var CALIBRATION_PROTOCOL = {
    id: "ggii.spectral-profile.calibration.v1",
    hypothesisId: "ggii.hypothesis.spectral-profile.calibration.v1",
    sizes: [16, 24, 36, 54, 81, 120],
    times: [4, 5.656854249, 8, 11.313708499, 16, 22.627416998, 32, 45.254833996, 64, 90.509667992, 128, 181.019335984],
    minMacroTime: 8,
    finiteSizeDivisor: 8,
    maxZeroModeFraction: 0.1,
    minWindowSamples: 5,
    minWindowSpan: 4,
    minEligibleRefinements: 4,
    rmsThreshold: 0.025,
    targetDimension: 2,
    targetTolerance: 0.2,
    controlTargetDimension: 1,
    controlTolerance: 0.2,
    negativeControlSeparation: 0.6,
    estimatorId: "heat-trace-analytic-log-derivative-v1"
  };

  function isPlainObject(value) {
    if (!value || typeof value !== "object" || Array.isArray(value)) return false;
    if (Object.prototype.toString.call(value) !== "[object Object]") return false;
    var prototype = Object.getPrototypeOf(value);
    if (prototype === null) return true;
    if (!Object.prototype.hasOwnProperty.call(prototype, "constructor")) return false;
    var constructor = prototype.constructor;
    return typeof constructor === "function" &&
      Function.prototype.toString.call(constructor) === Function.prototype.toString.call(Object);
  }

  function finiteNumber(value) {
    return typeof value === "number" && isFinite(value);
  }

  function assertInteger(value, name, lo, hi) {
    if (!Number.isInteger(value) || value < lo || value > hi) {
      throw new Error(name + " must be an integer in [" + lo + ", " + hi + "].");
    }
    return value;
  }

  function deepFreeze(value) {
    if (!value || typeof value !== "object" || Object.isFrozen(value)) return value;
    Object.keys(value).forEach(function (key) { deepFreeze(value[key]); });
    return Object.freeze(value);
  }

  function denseArray(value) {
    if (!Array.isArray(value)) return false;
    var keys = Object.keys(value);
    if (keys.length !== value.length) return false;
    for (var i = 0; i < value.length; i += 1) {
      if (!Object.prototype.hasOwnProperty.call(value, i) || keys.indexOf(String(i)) < 0) return false;
    }
    return true;
  }

  function canonicalValue(value, path, depth) {
    path = path || "root";
    depth = depth || 0;
    if (depth > 64) throw new Error(path + " exceeds the maximum serialization depth.");
    if (value === null || typeof value === "boolean") return value;
    if (typeof value === "string") {
      if (value.length > 1000000) throw new Error(path + " exceeds the maximum string length.");
      return value;
    }
    if (typeof value === "number") {
      if (!isFinite(value)) throw new Error(path + " contains a non-finite number.");
      if (Math.abs(value) < 1e-15) return 0;
      return Number(value.toPrecision(14));
    }
    if (Array.isArray(value)) {
      if (!denseArray(value)) throw new Error(path + " must be a dense index-only array.");
      if (value.length > 262144) throw new Error(path + " exceeds the maximum array length.");
      return value.map(function (item, index) { return canonicalValue(item, path + "[" + index + "]", depth + 1); });
    }
    if (isPlainObject(value)) {
      var result = {};
      var keys = Object.keys(value).sort();
      if (keys.length > 10000) throw new Error(path + " exceeds the maximum object field count.");
      keys.forEach(function (key) {
        if (key === "__proto__" || key === "prototype" || key === "constructor") {
          throw new Error(path + " contains a forbidden object key.");
        }
        if (typeof value[key] === "undefined" || typeof value[key] === "function") {
          throw new Error(path + "." + key + " is not serializable.");
        }
        result[key] = canonicalValue(value[key], path + "." + key, depth + 1);
      });
      return result;
    }
    throw new Error(path + " contains an unsupported value.");
  }

  function stableStringify(value) {
    return JSON.stringify(canonicalValue(value));
  }

  function fnv1a32(text) {
    var hash = 2166136261 >>> 0;
    for (var i = 0; i < text.length; i += 1) {
      hash ^= text.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return ("00000000" + (hash >>> 0).toString(16)).slice(-8);
  }

  function digestValue(value) {
    return fnv1a32(stableStringify(value));
  }

  function unknownKeys(input, allowed) {
    if (!isPlainObject(input)) return [];
    return Object.keys(input).filter(function (key) { return allowed.indexOf(key) < 0; }).sort();
  }

  function validIdentifier(value) {
    return typeof value === "string" && /^[a-z0-9][a-z0-9._:-]{2,127}$/i.test(value);
  }

  function validString(value, maxLength) {
    return typeof value === "string" && value.trim().length > 0 && value.length <= maxLength;
  }

  function validStringArray(value, maxItems) {
    return denseArray(value) && value.length <= maxItems && value.every(function (item) {
      return typeof item === "string" && item.length > 0 && item.length <= 1000;
    });
  }

  function evidencePayload(input) {
    return canonicalValue({
      schemaVersion: SCHEMA_VERSION,
      id: input.id,
      claim: input.claim,
      status: input.status,
      basis: input.basis,
      scope: input.scope,
      method: input.method,
      falsifier: input.falsifier,
      proofAnchor: input.proofAnchor || null,
      sourceUrls: input.sourceUrls || [],
      assumptions: input.assumptions || [],
      artifacts: input.artifacts || [],
      tests: input.tests || [],
      limitations: input.limitations || [],
      dependencies: input.dependencies || [],
      result: input.result == null ? null : input.result
    });
  }

  function validateEvidenceRecord(input, options) {
    options = options || {};
    var allowDraft = options.allowDraft === true;
    var errors = [];
    var allowed = [
      "schemaVersion", "id", "claim", "status", "basis", "scope", "method",
      "falsifier", "proofAnchor", "sourceUrls",
      "assumptions", "artifacts", "tests", "limitations", "dependencies",
      "result", "digestAlgorithm", "digest"
    ];
    if (!isPlainObject(input)) return { valid: false, errors: ["evidence record must be an object"] };
    unknownKeys(input, allowed).forEach(function (key) { errors.push("unknown evidence field " + key); });
    if (allowDraft) {
      if (input.schemaVersion != null && input.schemaVersion !== SCHEMA_VERSION) errors.push("unsupported evidence schemaVersion");
    } else if (input.schemaVersion !== SCHEMA_VERSION) errors.push("finalized evidence requires the current schemaVersion");
    if (!validIdentifier(input.id)) errors.push("id must be a stable identifier");
    if (!validString(input.claim, 4000)) errors.push("claim must be a non-empty string of at most 4000 characters");
    if (EVIDENCE_STATUSES.indexOf(input.status) < 0) errors.push("unknown evidence status");
    if (!EVIDENCE_BASES_BY_STATUS[input.status] || EVIDENCE_BASES_BY_STATUS[input.status].indexOf(input.basis) < 0) errors.push("evidence basis does not match status");
    if (!validString(input.scope, 4000)) errors.push("scope must be explicit");
    if (!validString(input.method, 4000)) errors.push("method must be explicit");
    if (!validString(input.falsifier, 4000)) errors.push("falsifier must be explicit");
    if (input.proofAnchor != null && !validString(input.proofAnchor, 2000)) errors.push("proofAnchor must be a non-empty bounded string when supplied");
    if (input.status === "proved" && !validString(input.proofAnchor, 2000)) errors.push("proved evidence requires a proofAnchor");
    ["sourceUrls", "assumptions", "artifacts", "tests", "limitations", "dependencies"].forEach(function (field) {
      if (input[field] != null && !validStringArray(input[field], 128)) errors.push(field + " must be a bounded string array");
    });
    if (input.basis === "proved-external" && (!Array.isArray(input.sourceUrls) || input.sourceUrls.length === 0)) errors.push("proved-external evidence requires sourceUrls");
    try { canonicalValue(input.result == null ? null : input.result, "result"); }
    catch (error) { errors.push(error.message); }
    if (allowDraft) {
      if (input.digestAlgorithm != null && input.digestAlgorithm !== DIGEST_ALGORITHM) errors.push("unsupported digestAlgorithm");
      if (input.digest != null && !/^[0-9a-f]{8}$/.test(input.digest)) errors.push("digest must be an eight-character lowercase hexadecimal checksum");
    } else {
      if (input.digestAlgorithm !== DIGEST_ALGORITHM) errors.push("finalized evidence requires the declared digestAlgorithm");
      if (!/^[0-9a-f]{8}$/.test(input.digest || "")) errors.push("finalized evidence requires an eight-character lowercase hexadecimal digest");
    }
    var payload = null;
    if (!errors.length) {
      payload = evidencePayload(input);
      if (input.digest != null && digestValue(payload) !== input.digest) errors.push("evidence digest mismatch");
    }
    return { valid: errors.length === 0, errors: errors, payload: payload };
  }

  function createEvidenceRecord(input) {
    var report = validateEvidenceRecord(input, { allowDraft: true });
    if (!report.valid) throw new Error("Invalid evidence record: " + report.errors.join("; "));
    var digest = digestValue(report.payload);
    var record = canonicalValue(report.payload);
    record.digestAlgorithm = DIGEST_ALGORITHM;
    record.digest = digest;
    return deepFreeze(canonicalValue(record));
  }

  function manifestPayload(input) {
    return canonicalValue({
      schemaVersion: SCHEMA_VERSION,
      coreVersion: VERSION,
      experimentId: input.experimentId,
      families: input.families,
      refinements: input.refinements,
      seeds: input.seeds,
      observables: input.observables,
      controls: input.controls || [],
      parameters: input.parameters || {},
      comparisonContract: input.comparisonContract,
      environment: input.environment || {},
      resultArtifacts: input.resultArtifacts || []
    });
  }

  function validateRunManifest(input, options) {
    options = options || {};
    var allowDraft = options.allowDraft === true;
    var errors = [];
    var allowed = [
      "schemaVersion", "coreVersion", "experimentId", "families",
      "refinements", "seeds", "observables", "controls", "parameters",
      "comparisonContract", "environment", "resultArtifacts",
      "digestAlgorithm", "digest"
    ];
    if (!isPlainObject(input)) return { valid: false, errors: ["run manifest must be an object"] };
    unknownKeys(input, allowed).forEach(function (key) { errors.push("unknown manifest field " + key); });
    if (allowDraft) {
      if (input.schemaVersion != null && input.schemaVersion !== SCHEMA_VERSION) errors.push("unsupported manifest schemaVersion");
      if (input.coreVersion != null && input.coreVersion !== VERSION) errors.push("manifest coreVersion does not match this core");
    } else {
      if (input.schemaVersion !== SCHEMA_VERSION) errors.push("finalized manifest requires the current schemaVersion");
      if (input.coreVersion !== VERSION) errors.push("finalized manifest requires this coreVersion");
    }
    if (!validIdentifier(input.experimentId)) errors.push("experimentId must be a stable identifier");
    if (!validStringArray(input.families, 32) || input.families.length === 0) errors.push("families must be a non-empty bounded string array");
    if (!Array.isArray(input.refinements) || input.refinements.length === 0 || input.refinements.length > 32 || input.refinements.some(function (n) { return !Number.isInteger(n) || n < 3 || n > 512; })) errors.push("refinements must contain integers in [3, 512]");
    if (!validStringArray(input.seeds, 128) || input.seeds.length === 0) errors.push("seeds must be a non-empty bounded string array");
    if (!validStringArray(input.observables, 64) || input.observables.length === 0) errors.push("observables must be a non-empty bounded string array");
    if (input.controls != null && !validStringArray(input.controls, 64)) errors.push("controls must be a bounded string array");
    if (!isPlainObject(input.parameters || {})) errors.push("parameters must be an object");
    if (!isPlainObject(input.comparisonContract)) errors.push("comparisonContract must be an object");
    if (!isPlainObject(input.environment || {})) errors.push("environment must be an object");
    if (input.resultArtifacts != null && !validStringArray(input.resultArtifacts, 128)) errors.push("resultArtifacts must be a bounded string array");
    try {
      canonicalValue(input.parameters || {}, "parameters");
      canonicalValue(input.comparisonContract || {}, "comparisonContract");
      canonicalValue(input.environment || {}, "environment");
    } catch (error) { errors.push(error.message); }
    if (allowDraft) {
      if (input.digestAlgorithm != null && input.digestAlgorithm !== DIGEST_ALGORITHM) errors.push("unsupported digestAlgorithm");
      if (input.digest != null && !/^[0-9a-f]{8}$/.test(input.digest)) errors.push("digest must be an eight-character lowercase hexadecimal checksum");
    } else {
      if (input.digestAlgorithm !== DIGEST_ALGORITHM) errors.push("finalized manifest requires the declared digestAlgorithm");
      if (!/^[0-9a-f]{8}$/.test(input.digest || "")) errors.push("finalized manifest requires an eight-character lowercase hexadecimal digest");
    }
    var payload = null;
    if (!errors.length) {
      payload = manifestPayload(input);
      if (input.digest != null && digestValue(payload) !== input.digest) errors.push("manifest digest mismatch");
    }
    return { valid: errors.length === 0, errors: errors, payload: payload };
  }

  function createRunManifest(input) {
    var report = validateRunManifest(input, { allowDraft: true });
    if (!report.valid) throw new Error("Invalid run manifest: " + report.errors.join("; "));
    var digest = digestValue(report.payload);
    var manifest = canonicalValue(report.payload);
    manifest.digestAlgorithm = DIGEST_ALGORITHM;
    manifest.digest = digest;
    return deepFreeze(canonicalValue(manifest));
  }

  function edgeKey(a, b) {
    return a < b ? a + ":" + b : b + ":" + a;
  }

  function periodicLatticeGraph(options) {
    options = options || {};
    var family = options.family || "square";
    if (family !== "square" && family !== "triangular") throw new Error("family must be square or triangular");
    var rows = assertInteger(options.rows == null ? 8 : options.rows, "rows", 3, 128);
    var cols = assertInteger(options.cols == null ? rows : options.cols, "cols", 3, 128);
    var nodes = [], edges = [], edgeMap = Object.create(null);
    var majorRadius = 2, minorRadius = 0.65;
    function index(row, col) {
      return ((row % rows) + rows) % rows * cols + ((col % cols) + cols) % cols;
    }
    for (var row = 0; row < rows; row += 1) {
      for (var col = 0; col < cols; col += 1) {
        var theta = TAU * col / cols, phi = TAU * row / rows;
        nodes.push({
          id: nodes.length,
          label: row + "," + col,
          x: (majorRadius + minorRadius * Math.cos(phi)) * Math.cos(theta),
          y: (majorRadius + minorRadius * Math.cos(phi)) * Math.sin(theta),
          z: minorRadius * Math.sin(phi),
          radius: 1,
          value: Math.cos(theta),
          u: 1,
          v: 0
        });
      }
    }
    function addEdge(a, b) {
      if (a === b) return;
      var key = edgeKey(a, b);
      if (edgeMap[key]) return;
      edgeMap[key] = true;
      edges.push({ source: Math.min(a, b), target: Math.max(a, b), weight: 1, length: 1 });
    }
    var offsets = family === "square" ? [[0, 1], [1, 0]] : [[0, 1], [1, 0], [1, -1]];
    for (var r = 0; r < rows; r += 1) {
      for (var c = 0; c < cols; c += 1) {
        offsets.forEach(function (offset) { addEdge(index(r, c), index(r + offset[0], c + offset[1])); });
      }
    }
    edges.sort(function (a, b) { return a.source - b.source || a.target - b.target; });
    return {
      nodes: nodes,
      edges: edges,
      faces: [],
      metadata: {
        generator: "periodic-lattice",
        family: family,
        rows: rows,
        cols: cols,
        intrinsicEdgeLength: 1,
        displayEmbedding: "torus projection only",
        geometryScope: "graph metric and normalized-Laplacian diffusion; no 2-cell topology is asserted"
      }
    };
  }

  function degreeSequence(graph) {
    var degree = new Array(graph.nodes.length).fill(0);
    graph.edges.forEach(function (edge) { degree[edge.source] += 1; degree[edge.target] += 1; });
    return degree;
  }

  function periodicLatticeSpectrum(options) {
    options = options || {};
    var family = options.family || "square";
    if (family !== "square" && family !== "triangular") throw new Error("family must be square or triangular");
    var rows = assertInteger(options.rows == null ? 8 : options.rows, "rows", 3, 512);
    var cols = assertInteger(options.cols == null ? rows : options.cols, "cols", 3, 512);
    var eigenvalues = [];
    for (var p = 0; p < rows; p += 1) {
      for (var q = 0; q < cols; q += 1) {
        var a = TAU * p / rows, b = TAU * q / cols;
        var lambda = family === "square"
          ? 1 - (Math.cos(a) + Math.cos(b)) / 2
          : 1 - (Math.cos(a) + Math.cos(b) + Math.cos(a - b)) / 3;
        if (Math.abs(lambda) < EPS) lambda = 0;
        if (lambda < 0 && lambda > -1e-12) lambda = 0;
        if (lambda > 2 && lambda < 2 + 1e-12) lambda = 2;
        eigenvalues.push(lambda);
      }
    }
    eigenvalues.sort(function (x, y) { return x - y; });
    var positive = eigenvalues.filter(function (value) { return value > 1e-10; });
    return canonicalValue({
      family: family,
      rows: rows,
      cols: cols,
      nodeCount: rows * cols,
      operator: "symmetric normalized graph Laplacian",
      formula: family === "square"
        ? "1-(cos(2πp/rows)+cos(2πq/cols))/2"
        : "1-(cos(a)+cos(b)+cos(a-b))/3",
      eigenvalues: eigenvalues,
      zeroMultiplicity: eigenvalues.filter(function (value) { return value <= 1e-10; }).length,
      spectralGap: positive.length ? positive[0] : 0,
      bounds: { min: eigenvalues[0], max: eigenvalues[eigenvalues.length - 1] }
    });
  }

  function cycleSpectrum(count) {
    count = assertInteger(count, "count", 4, 262144);
    var eigenvalues = [];
    for (var k = 0; k < count; k += 1) {
      var lambda = 1 - Math.cos(TAU * k / count);
      eigenvalues.push(Math.abs(lambda) < EPS ? 0 : lambda);
    }
    return eigenvalues.sort(function (a, b) { return a - b; });
  }

  function squareWordDistance(m, n) {
    if (!Number.isSafeInteger(m) || !Number.isSafeInteger(n)) throw new Error("square coordinates must be safe integers");
    var distance = Math.abs(m) + Math.abs(n);
    if (!Number.isSafeInteger(distance)) throw new Error("square word distance exceeds the safe-integer range");
    return distance;
  }

  function triangularWordDistance(m, n) {
    if (!Number.isSafeInteger(m) || !Number.isSafeInteger(n)) throw new Error("triangular coordinates must be safe integers");
    var sum = m + n;
    if (!Number.isSafeInteger(sum)) throw new Error("triangular coordinate sum exceeds the safe-integer range");
    var distance = Math.max(Math.abs(m), Math.abs(n), Math.abs(sum));
    if (!Number.isSafeInteger(distance)) throw new Error("triangular word distance exceeds the safe-integer range");
    return distance;
  }

  function latticeStepVectors(family) {
    if (family === "square") return [[1, 0], [-1, 0], [0, 1], [0, -1]];
    if (family === "triangular") {
      var half = 0.5, height = Math.sqrt(3) / 2;
      return [[1, 0], [-1, 0], [half, height], [-half, -height], [half, -height], [-half, height]];
    }
    throw new Error("family must be square or triangular");
  }

  function latticeStepMoments(family) {
    var steps = latticeStepVectors(family), count = steps.length;
    var mean = [0, 0], covariance = [[0, 0], [0, 0]], fourth = { x: 0, y: 0, radial: 0 };
    steps.forEach(function (step) {
      mean[0] += step[0] / count;
      mean[1] += step[1] / count;
      covariance[0][0] += step[0] * step[0] / count;
      covariance[0][1] += step[0] * step[1] / count;
      covariance[1][0] += step[1] * step[0] / count;
      covariance[1][1] += step[1] * step[1] / count;
      fourth.x += Math.pow(step[0], 4) / count;
      fourth.y += Math.pow(step[1], 4) / count;
      fourth.radial += Math.pow(step[0] * step[0] + step[1] * step[1], 2) / count;
    });
    return canonicalValue({
      family: family,
      embedding: family === "square" ? "orthonormal unit generators" : "equilateral unit generators at angle pi/3",
      steps: steps,
      mean: mean,
      covariance: covariance,
      fourthMoments: fourth
    });
  }

  function latticeStepCharacteristic(family, xi) {
    if (!denseArray(xi) || xi.length !== 2 || !xi.every(finiteNumber)) throw new Error("xi must be a dense pair of finite numbers");
    var steps = latticeStepVectors(family);
    var sum = steps.reduce(function (running, step) {
      var dot = xi[0] * step[0] + xi[1] * step[1];
      if (!finiteNumber(dot)) throw new Error("xi produces a non-finite characteristic-function phase");
      var term = Math.cos(dot);
      if (!finiteNumber(term)) throw new Error("xi is outside the finite numerical characteristic-function domain");
      return running + term;
    }, 0);
    var result = sum / steps.length;
    if (!finiteNumber(result)) throw new Error("characteristic-function evaluation was non-finite");
    return result;
  }

  function diffusionFiniteDimensionalUniversalityControl() {
    var square = latticeStepMoments("square"), triangular = latticeStepMoments("triangular");
    var evidence = createEvidenceRecord({
      id: "ggii.theorem.p8.2.square-triangular-gaussian-fdd",
      claim: "Uniform simple random walks on the orthogonal square and equilateral triangular step sets have the same covariance-normalized Gaussian finite-dimensional diffusion limit.",
      status: "proved",
      basis: "proved-here",
      scope: "Independent-increment walks using exactly the declared physical step vectors; convergence of finite-dimensional distributions under n^{-1/2} spatial scaling.",
      method: "Prove the symbolic zero mean and covariance I/2 identities, expand each finite-support symmetric characteristic function at the origin, and apply Cramer--Wold after factoring joint characteristic functions over disjoint time increments.",
      falsifier: "A declared step moment differs from I/2, or a fixed finite collection of rescaled-time characteristic functions has a non-Gaussian or family-dependent limit.",
      proofAnchor: "GLOBAL_GEOMETRY_II_FOUNDATIONS.md Proposition 8.2",
      assumptions: ["uniform independent increments", "declared Euclidean embeddings", "fixed finite observation times", "diffusive n^{-1/2} spatial scaling"],
      artifacts: ["formula:lattice-step-moments", "formula:lattice-step-characteristic"],
      tests: ["symbolic covariance identity with binary64 residual audit", "multi-time finite-n characteristic convergence audit", "distinct fourth-moment microscopic control", "derived-phase overflow rejection"],
      limitations: ["does not prove path-space tightness", "does not identify graph metrics", "does not cover boundaries or disordered conductance"],
      dependencies: [],
      result: {
        symbolicMean: "0",
        symbolicCovariance: "I/2",
        squareCovariance: square.covariance,
        triangularCovariance: triangular.covariance,
        limitingCharacteristicFunction: "exp(-t*|xi|^2/4)",
        covarianceAtTimeT: "t*I/2",
        standardBrownianTimeAccelerationAtEdgeScaleH: "2/h^2"
      }
    });
    return deepFreeze(canonicalValue({ square: square, triangular: triangular, evidence: evidence }));
  }

  function diffusionPerturbationLaws() {
    return [
      {
        id: "square-uniform",
        steps: [[1, 0], [-1, 0], [0, 1], [0, -1]],
        probabilities: [0.25, 0.25, 0.25, 0.25]
      },
      {
        id: "square-anisotropic-p70",
        steps: [[1, 0], [-1, 0], [0, 1], [0, -1]],
        probabilities: [0.35, 0.35, 0.15, 0.15]
      },
      {
        id: "triangular-pair-biased",
        steps: [[1, 0], [-1, 0], [0.5, Math.sqrt(3) / 2], [-0.5, -Math.sqrt(3) / 2], [0.5, -Math.sqrt(3) / 2], [-0.5, Math.sqrt(3) / 2]],
        probabilities: [0.25, 0.25, 0.15, 0.15, 0.10, 0.10]
      },
      {
        id: "centered-three-step-skew",
        steps: [[1, 0], [0, 1], [-1, -1]],
        probabilities: [1 / 3, 1 / 3, 1 / 3]
      }
    ];
  }

  function analyzeStepLaw(law) {
    var mean = [0, 0], covariance = [[0, 0], [0, 0]], probabilityTotal = 0;
    law.steps.forEach(function (step, index) {
      var probability = law.probabilities[index];
      probabilityTotal += probability;
      mean[0] += probability * step[0];
      mean[1] += probability * step[1];
    });
    law.steps.forEach(function (step, index) {
      var probability = law.probabilities[index];
      var x = step[0] - mean[0], y = step[1] - mean[1];
      covariance[0][0] += probability * x * x;
      covariance[0][1] += probability * x * y;
      covariance[1][0] += probability * y * x;
      covariance[1][1] += probability * y * y;
    });
    var a = covariance[0][0], b = covariance[0][1], c = covariance[1][1];
    var determinant = a * c - b * b;
    if (!(determinant > 0)) throw new Error("diffusion perturbation law must have positive-definite covariance");
    var determinantRoot = Math.sqrt(determinant);
    var normalization = Math.sqrt(a + c + 2 * determinantRoot);
    var shiftedDeterminant = (a + determinantRoot) * (c + determinantRoot) - b * b;
    var inverseSquareRoot = [
      [normalization * (c + determinantRoot) / shiftedDeterminant, -normalization * b / shiftedDeterminant],
      [-normalization * b / shiftedDeterminant, normalization * (a + determinantRoot) / shiftedDeterminant]
    ];
    var whitenedSteps = law.steps.map(function (step) {
      var x = step[0] - mean[0], y = step[1] - mean[1];
      return [
        inverseSquareRoot[0][0] * x + inverseSquareRoot[0][1] * y,
        inverseSquareRoot[1][0] * x + inverseSquareRoot[1][1] * y
      ];
    });
    var whitenedMean = [0, 0], whitenedCovariance = [[0, 0], [0, 0]];
    whitenedSteps.forEach(function (step, index) {
      var probability = law.probabilities[index];
      whitenedMean[0] += probability * step[0];
      whitenedMean[1] += probability * step[1];
      whitenedCovariance[0][0] += probability * step[0] * step[0];
      whitenedCovariance[0][1] += probability * step[0] * step[1];
      whitenedCovariance[1][0] += probability * step[1] * step[0];
      whitenedCovariance[1][1] += probability * step[1] * step[1];
    });
    var discriminant = Math.sqrt((a - c) * (a - c) + 4 * b * b);
    return {
      id: law.id,
      steps: law.steps,
      probabilities: law.probabilities,
      probabilityTotal: probabilityTotal,
      mean: mean,
      covariance: covariance,
      covarianceEigenvalueBounds: [(a + c - discriminant) / 2, (a + c + discriminant) / 2],
      inverseSquareRoot: inverseSquareRoot,
      whitenedSteps: whitenedSteps,
      whitenedMean: whitenedMean,
      whitenedCovariance: whitenedCovariance
    };
  }

  function complexPower(real, imaginary, exponent) {
    var radius = Math.sqrt(real * real + imaginary * imaginary);
    var angle = Math.atan2(imaginary, real);
    var poweredRadius = Math.pow(radius, exponent);
    return { real: poweredRadius * Math.cos(exponent * angle), imaginary: poweredRadius * Math.sin(exponent * angle) };
  }

  function analyzedLawCharacteristic(analysis, xi, whitened) {
    var steps = whitened ? analysis.whitenedSteps : analysis.steps;
    var real = 0, imaginary = 0;
    steps.forEach(function (step, index) {
      var phase = xi[0] * step[0] + xi[1] * step[1];
      real += analysis.probabilities[index] * Math.cos(phase);
      imaginary += analysis.probabilities[index] * Math.sin(phase);
    });
    return { real: real, imaginary: imaginary };
  }

  function diffusionAnisotropyPhaseDiagram() {
    var anisotropyParameters = [0.3, 0.4, 0.5, 0.6, 0.7];
    var sampleSizes = [200, 632, 2000, 6325, 20000];
    var directions = [[0.7, -1.1], [1.2, 0.3], [-0.4, 0.9]];
    var resolutionGuard = 5e-5;
    var rows = anisotropyParameters.map(function (p) {
      var analysis = analyzeStepLaw({
        id: "square-anisotropy-p" + String(Math.round(100 * p)),
        steps: [[1, 0], [-1, 0], [0, 1], [0, -1]],
        probabilities: [p / 2, p / 2, (1 - p) / 2, (1 - p) / 2]
      });
      var cells = sampleSizes.map(function (sampleSize) {
        var maximumError = directions.reduce(function (maximum, direction) {
          var argument = direction.map(function (value) { return value / Math.sqrt(sampleSize); });
          var oneStep = analyzedLawCharacteristic(analysis, argument, true);
          var finite = complexPower(oneStep.real, oneStep.imaginary, sampleSize);
          var limit = Math.exp(-(direction[0] * direction[0] + direction[1] * direction[1]) / 2);
          var error = Math.sqrt(Math.pow(finite.real - limit, 2) + finite.imaginary * finite.imaginary);
          return Math.max(maximum, error);
        }, 0);
        return {
          sampleSize: sampleSize,
          maximumCharacteristicError: maximumError,
          classification: maximumError <= resolutionGuard ? "within-resolution-guard" : "finite-size-above-guard"
        };
      });
      var firstResolved = cells.filter(function (cell) { return cell.classification === "within-resolution-guard"; })[0];
      return {
        horizontalStepProbability: p,
        covarianceEigenvalues: analysis.covarianceEigenvalueBounds,
        covarianceConditionNumber: analysis.covarianceEigenvalueBounds[1] / analysis.covarianceEigenvalueBounds[0],
        cells: cells,
        firstResolvedSampleSize: firstResolved ? firstResolved.sampleSize : null
      };
    });
    return deepFreeze(canonicalValue({
      schema: "ggii.diffusion-anisotropy-finite-size-map/1",
      status: "finite-computational-map",
      axes: {
        horizontalStepProbability: anisotropyParameters,
        sampleSize: sampleSizes
      },
      fixedProtocol: {
        stepLaw: "P(±e1)=p/2 and P(±e2)=(1-p)/2",
        normalization: "exact covariance whitening followed by n^{-1/2} scaling",
        statistic: "maximum characteristic-function error over three predeclared Fourier directions",
        directions: directions,
        resolutionGuard: resolutionGuard,
        basin: "support norm <= 1 and covariance eigenvalues in [0.3,0.7]"
      },
      rows: rows,
      interpretation: "This is a finite-size resolution map inside the proved P8.3 basin. The color boundary is a disclosed numerical guard, not a thermodynamic phase transition.",
      limitations: ["exact-law whitening only", "five anisotropy values", "five finite sample sizes", "fixed three-direction diagnostic", "no path-space, boundary, disorder, or material claim"]
    }));
  }

  function robustWhitenedDiffusionUniversalityControl() {
    var sampleSizes = [200, 2000, 20000];
    var directions = [[0.7, -1.1], [1.2, 0.3], [-0.4, 0.9]];
    var basin = { dimension: 2, supportBoundM: Math.sqrt(2), covarianceLowerKappa: 0.3, covarianceUpper: 1 / 0.3, whitening: "exact-law symmetric-SPD inverse square root" };
    var analyses = diffusionPerturbationLaws().map(analyzeStepLaw);
    var rows = analyses.map(function (analysis) {
      var maxErrors = sampleSizes.map(function (sampleSize) {
        return directions.reduce(function (maximum, direction) {
          var argument = direction.map(function (value) { return value / Math.sqrt(sampleSize); });
          var oneStep = analyzedLawCharacteristic(analysis, argument, true);
          var finite = complexPower(oneStep.real, oneStep.imaginary, sampleSize);
          var limit = Math.exp(-(direction[0] * direction[0] + direction[1] * direction[1]) / 2);
          return Math.max(maximum, Math.sqrt(Math.pow(finite.real - limit, 2) + finite.imaginary * finite.imaginary));
        }, 0);
      });
      return { law: analysis, sampleSizes: sampleSizes, maxCharacteristicErrors: maxErrors };
    });
    var anisotropic = analyses.filter(function (analysis) { return analysis.id === "square-anisotropic-p70"; })[0];
    var controlDirection = [1, 0], controlN = 20000;
    var rawOneStep = analyzedLawCharacteristic(anisotropic, controlDirection.map(function (value) { return value / Math.sqrt(controlN); }), false);
    var rawFinite = complexPower(rawOneStep.real, rawOneStep.imaginary, controlN);
    var rawAnalyticLimit = Math.exp(-0.35), standardLimit = Math.exp(-0.5);
    var rawStandardError = Math.abs(rawFinite.real - standardLimit);
    var rawAnalyticError = Math.sqrt(Math.pow(rawFinite.real - rawAnalyticLimit, 2) + Math.pow(rawFinite.imaginary, 2));
    var negativeControl = {
      n: controlN,
      direction: controlDirection,
      rawCovariance: [[0.7, 0], [0, 0.3]],
      finiteNCharacteristic: rawFinite,
      analyticDifferentLimit: rawAnalyticLimit,
      standardGaussianLimit: standardLimit,
      finiteNErrorFromAnalyticLimit: rawAnalyticError,
      finiteNErrorFromStandardGaussian: rawStandardError,
      asymptoticGapFromStandardGaussian: Math.abs(rawAnalyticLimit - standardLimit)
    };
    var phaseDiagram = diffusionAnisotropyPhaseDiagram();
    var theoremEvidence = createEvidenceRecord({
      id: "ggii.theorem.p8.3.robust-whitened-gaussian-fdd",
      claim: "Centered iid bounded-range step laws with uniformly nondegenerate covariance converge uniformly over the declared bounded basin, after covariance whitening, to common standard-Brownian finite-dimensional laws.",
      status: "proved",
      basis: "proved-here",
      scope: "Families of centered iid laws on R^d with support norm at most M and covariance eigenvalues in [kappa,1/kappa], for fixed finite observation times and Cramer--Wold coefficients after exact covariance whitening.",
      method: "Whitening gives identity covariance and a uniform support bound M/sqrt(kappa); a third-order characteristic-function remainder is O(n^-3/2) uniformly, and independent increment blocks give uniform finite-dimensional convergence.",
      falsifier: "A law inside the declared bounded centered nondegenerate basin has a whitened fixed-time characteristic function that does not converge uniformly to exp(-|xi|^2/2), or the uniform Taylor remainder bound fails.",
      proofAnchor: "GLOBAL_GEOMETRY_II_FOUNDATIONS.md Proposition 8.3",
      assumptions: ["iid increments", "zero mean", "uniformly bounded support", "uniformly positive-definite covariance", "covariance whitening", "fixed finite observation schedule"],
      artifacts: ["formula:uniform-whitened-characteristic-expansion", "artifact:calibration-v1.json"],
      tests: ["four-law perturbation basin", "anisotropic unwhitened negative control", "whitened covariance residual audit", "three-direction finite-n convergence audit"],
      limitations: ["finite-dimensional laws only", "does not prove path-space tightness in this package", "does not cover estimated whitening", "does not cover state-dependent, correlated, boundary, or degenerate increments"],
      dependencies: [],
      result: { convergence: "uniform finite-dimensional after covariance whitening", limitingCovarianceAtTimeT: "t*I", robustnessParameters: "fixed finite M and kappa>0" }
    });
    var auditEvidence = createEvidenceRecord({
      id: "ggii.audit.p8.3.four-law-perturbation-basin",
      claim: "Four predeclared centered microscopic laws, including anisotropic and nonsymmetric controls, numerically approach the common whitened Gaussian characteristic function while the unwhitened anisotropic control stays separated; a predeclared 5-by-5 anisotropy/size map resolves the finite-size crossover under a disclosed guard.",
      status: "computational",
      basis: "finite-computation",
      scope: "The four embedded laws inside the declared M=sqrt(2), kappa=0.3 basin, three Fourier directions, sample sizes 200, 2000, and 20000, plus the returned five-anisotropy by five-size finite-resolution map.",
      method: "Compute each covariance and analytic 2x2 inverse square root, evaluate the exact finite-support characteristic function, take integer powers, compare with the standard Gaussian target, and classify the frozen anisotropy/size grid against the disclosed 5e-5 diagnostic guard.",
      falsifier: "A whitened covariance residual exceeds tolerance, characteristic error fails to decrease, or the anisotropic raw control is not separated from the standard target.",
      assumptions: ["binary64 trigonometric evaluation", "predeclared finite laws and directions"],
      artifacts: ["artifact:calibration-v1.json"],
      tests: ["independent raw-moment and A*Sigma*A^T oracle", "independent repeated-squaring characteristic oracle", "strict three-size error decrease", "analytic different-limit negative control", "multi-time Cramer--Wold fixture"],
      limitations: ["finite audit supports but does not prove P8.3", "not an ensemble uncertainty study", "not a boundary or material experiment"],
      dependencies: ["ggii.theorem.p8.3.robust-whitened-gaussian-fdd"],
      result: { basin: basin, sampleSizes: sampleSizes, directions: directions, rows: rows, unwhitenedAnisotropicControl: negativeControl, anisotropyFiniteSizeMap: phaseDiagram }
    });
    return deepFreeze(canonicalValue({ theoremEvidence: theoremEvidence, auditEvidence: auditEvidence, basin: basin, sampleSizes: sampleSizes, directions: directions, analyses: analyses, rows: rows, phaseDiagram: phaseDiagram }));
  }

  function graphMetricNonuniversalityControl() {
    var evidence = createEvidenceRecord({
      id: "ggii.graph-metric.square-triangular.p8.1",
      claim: "Unit-edge square and triangular one-skeleton refinements have different normed-plane metric limits: the square unit ball has four extreme points and the triangular unit ball has six.",
      status: "proved",
      basis: "proved-here",
      scope: "Infinite square and triangular coordinate graphs with their word metrics, rescaled by lattice spacing on bounded pointed sets.",
      method: "Use the exact word-distance formula |m|+|n| for square generators and max(|m|,|n|,|m+n|) for triangular generators, then count the extreme points of their polyhedral unit balls.",
      falsifier: "An integer coordinate contradicting either word-distance formula, or a surjective normed-space isometry preserving neither extreme-point count, would refute the stated proof fixture.",
      proofAnchor: "GLOBAL_GEOMETRY_II_FOUNDATIONS.md Proposition 8.1",
      assumptions: ["uniform positive edge length", "declared square and triangular generator sets", "one-skeleton shortest-path metric"],
      artifacts: ["formula:square-word-distance", "formula:triangular-word-distance"],
      tests: ["bounded integer-coordinate breadth-first fixtures", "unit-ball extreme-point fixture"],
      limitations: ["does not obstruct a shared covariance-normalized diffusion limit", "does not apply when both meshes are given a common facewise piecewise-Euclidean metric"],
      result: { squareExtremePoints: 4, triangularExtremePoints: 6, isometricLimits: false }
    });
    return deepFreeze(canonicalValue({
      status: "proved-nonuniversal-in-graph-metric",
      square: {
        generators: [[1, 0], [-1, 0], [0, 1], [0, -1]],
        distanceFormula: "|m|+|n|",
        unitBallExtremePoints: [[1, 0], [0, 1], [-1, 0], [0, -1]]
      },
      triangular: {
        generators: [[1, 0], [-1, 0], [0, 1], [0, -1], [1, -1], [-1, 1]],
        distanceFormula: "max(|m|,|n|,|m+n|)",
        unitBallExtremePoints: [[1, 0], [1, -1], [0, -1], [-1, 0], [-1, 1], [0, 1]]
      },
      evidence: evidence
    }));
  }

  function heatProfileFromSpectrum(spectrumOrEigenvalues, options) {
    options = options || {};
    var eigenvalues = Array.isArray(spectrumOrEigenvalues)
      ? spectrumOrEigenvalues.slice()
      : spectrumOrEigenvalues && Array.isArray(spectrumOrEigenvalues.eigenvalues)
        ? spectrumOrEigenvalues.eigenvalues.slice()
        : null;
    if (!eigenvalues || !eigenvalues.length || eigenvalues.some(function (value) { return !finiteNumber(value) || value < -1e-10 || value > 2 + 1e-10; })) {
      throw new Error("A bounded normalized-Laplacian spectrum is required.");
    }
    var times = options.times || [1, 2, 4, 8, 16, 32, 64];
    if (!Array.isArray(times) || !times.length || times.length > 128 || times.some(function (time) { return !finiteNumber(time) || time <= 0; })) {
      throw new Error("times must be a bounded array of positive finite values.");
    }
    var operatorScale = options.operatorScale == null ? 1 : Number(options.operatorScale);
    if (!finiteNumber(operatorScale) || operatorScale <= 0) throw new Error("operatorScale must be positive and finite.");
    var zeroModeCount = eigenvalues.filter(function (value) { return Math.abs(value) <= 1e-10; }).length;
    return canonicalValue(times.map(function (time) {
      var trace = 0, firstMoment = 0;
      eigenvalues.forEach(function (rawLambda) {
        var lambda = Math.max(0, rawLambda) * operatorScale;
        var heat = Math.exp(-time * lambda);
        trace += heat;
        firstMoment += lambda * heat;
      });
      return {
        time: time,
        trace: trace,
        normalizedTrace: trace / eigenvalues.length,
        spectralDimension: trace > EPS ? 2 * time * firstMoment / trace : null,
        zeroModeFraction: trace > EPS ? zeroModeCount / trace : null
      };
    }));
  }

  function profileDistance(profileA, profileB, field, predicate) {
    field = field || "spectralDimension";
    var byTime = Object.create(null), differences = [];
    profileA.forEach(function (point) { byTime[String(point.time)] = point; });
    profileB.forEach(function (point) {
      var other = byTime[String(point.time)];
      if (!other || (predicate && !predicate(point.time))) return;
      if (!finiteNumber(other[field]) || !finiteNumber(point[field])) return;
      differences.push({ time: point.time, difference: other[field] - point[field] });
    });
    if (!differences.length) return { available: false, reason: "no matched finite profile points" };
    var squareSum = differences.reduce(function (sum, point) { return sum + point.difference * point.difference; }, 0);
    return canonicalValue({
      available: true,
      field: field,
      count: differences.length,
      rms: Math.sqrt(squareSum / differences.length),
      maxAbsolute: Math.max.apply(null, differences.map(function (point) { return Math.abs(point.difference); })),
      differences: differences
    });
  }

  function meanField(profile, field, predicate) {
    var values = profile.filter(function (point) {
      return (!predicate || predicate(point.time)) && finiteNumber(point[field]);
    }).map(function (point) { return point[field]; });
    return values.length ? values.reduce(function (sum, value) { return sum + value; }, 0) / values.length : null;
  }

  function runSpectralCalibration(options) {
    options = options || {};
    if (!isPlainObject(options)) throw new Error("calibration options must be a plain object");
    var allowedOptions = ["sizes", "times", "minMacroTime", "finiteSizeDivisor", "maxZeroModeFraction", "minWindowSamples", "minWindowSpan", "minEligibleRefinements"];
    var optionUnknowns = unknownKeys(options, allowedOptions);
    if (optionUnknowns.length) throw new Error("unknown calibration option " + optionUnknowns[0]);
    var sizes = options.sizes || CALIBRATION_PROTOCOL.sizes.slice();
    var times = options.times || CALIBRATION_PROTOCOL.times.slice();
    if (!Array.isArray(sizes) || !sizes.length || sizes.length > 16) throw new Error("sizes must be a non-empty bounded array");
    sizes.forEach(function (size) { assertInteger(size, "size", 4, 256); });
    if (new Set(sizes).size !== sizes.length || sizes.some(function (size, index) { return index > 0 && size <= sizes[index - 1]; })) {
      throw new Error("sizes must be unique and strictly increasing");
    }
    if (!Array.isArray(times) || !times.length || times.length > 128 || times.some(function (time) { return !finiteNumber(time) || time <= 0; })) {
      throw new Error("times must be a bounded array of positive finite values");
    }
    if (new Set(times).size !== times.length || times.some(function (time, index) { return index > 0 && time <= times[index - 1]; })) {
      throw new Error("times must be unique and strictly increasing");
    }
    var minMacroTime = options.minMacroTime == null ? CALIBRATION_PROTOCOL.minMacroTime : Number(options.minMacroTime);
    var finiteSizeDivisor = options.finiteSizeDivisor == null ? CALIBRATION_PROTOCOL.finiteSizeDivisor : Number(options.finiteSizeDivisor);
    var maxZeroModeFraction = options.maxZeroModeFraction == null ? CALIBRATION_PROTOCOL.maxZeroModeFraction : Number(options.maxZeroModeFraction);
    var minWindowSamples = options.minWindowSamples == null ? CALIBRATION_PROTOCOL.minWindowSamples : options.minWindowSamples;
    var minWindowSpan = options.minWindowSpan == null ? CALIBRATION_PROTOCOL.minWindowSpan : Number(options.minWindowSpan);
    var minEligibleRefinements = options.minEligibleRefinements == null ? CALIBRATION_PROTOCOL.minEligibleRefinements : options.minEligibleRefinements;
    if (!finiteNumber(minMacroTime) || minMacroTime <= 0 || !finiteNumber(finiteSizeDivisor) || finiteSizeDivisor <= 0 ||
        !finiteNumber(maxZeroModeFraction) || maxZeroModeFraction <= 0 || maxZeroModeFraction > 0.5 ||
        !Number.isInteger(minWindowSamples) || minWindowSamples < 5 || minWindowSamples > 128 ||
        !finiteNumber(minWindowSpan) || minWindowSpan < 4 ||
        !Number.isInteger(minEligibleRefinements) || minEligibleRefinements < 4 || minEligibleRefinements > sizes.length) {
      throw new Error("invalid calibration window or refinement gate");
    }
    var selectedProtocol = canonicalValue({
      sizes: sizes,
      times: times,
      minMacroTime: minMacroTime,
      finiteSizeDivisor: finiteSizeDivisor,
      maxZeroModeFraction: maxZeroModeFraction,
      minWindowSamples: minWindowSamples,
      minWindowSpan: minWindowSpan,
      minEligibleRefinements: minEligibleRefinements,
      rmsThreshold: CALIBRATION_PROTOCOL.rmsThreshold,
      targetDimension: CALIBRATION_PROTOCOL.targetDimension,
      targetTolerance: CALIBRATION_PROTOCOL.targetTolerance,
      controlTargetDimension: CALIBRATION_PROTOCOL.controlTargetDimension,
      controlTolerance: CALIBRATION_PROTOCOL.controlTolerance,
      negativeControlSeparation: CALIBRATION_PROTOCOL.negativeControlSeparation,
      estimatorId: CALIBRATION_PROTOCOL.estimatorId
    });
    var frozenProtocolComparable = canonicalValue({
      sizes: CALIBRATION_PROTOCOL.sizes,
      times: CALIBRATION_PROTOCOL.times,
      minMacroTime: CALIBRATION_PROTOCOL.minMacroTime,
      finiteSizeDivisor: CALIBRATION_PROTOCOL.finiteSizeDivisor,
      maxZeroModeFraction: CALIBRATION_PROTOCOL.maxZeroModeFraction,
      minWindowSamples: CALIBRATION_PROTOCOL.minWindowSamples,
      minWindowSpan: CALIBRATION_PROTOCOL.minWindowSpan,
      minEligibleRefinements: CALIBRATION_PROTOCOL.minEligibleRefinements,
      rmsThreshold: CALIBRATION_PROTOCOL.rmsThreshold,
      targetDimension: CALIBRATION_PROTOCOL.targetDimension,
      targetTolerance: CALIBRATION_PROTOCOL.targetTolerance,
      controlTargetDimension: CALIBRATION_PROTOCOL.controlTargetDimension,
      controlTolerance: CALIBRATION_PROTOCOL.controlTolerance,
      negativeControlSeparation: CALIBRATION_PROTOCOL.negativeControlSeparation,
      estimatorId: CALIBRATION_PROTOCOL.estimatorId
    });
    var conformsToFrozenProtocol = stableStringify(selectedProtocol) === stableStringify(frozenProtocolComparable);
    var refinements = sizes.map(function (size) {
      var squareSpectrum = periodicLatticeSpectrum({ family: "square", rows: size, cols: size });
      var triangularSpectrum = periodicLatticeSpectrum({ family: "triangular", rows: size, cols: size });
      var squareProfile = heatProfileFromSpectrum(squareSpectrum, { times: times });
      var triangularProfile = heatProfileFromSpectrum(triangularSpectrum, { times: times });
      var ringProfile = heatProfileFromSpectrum(cycleSpectrum(size * size), { times: times });
      var maxMacroTime = size * size / finiteSizeDivisor;
      var squareByTime = Object.create(null), triangularByTime = Object.create(null), ringByTime = Object.create(null);
      squareProfile.forEach(function (point) { squareByTime[String(point.time)] = point; });
      triangularProfile.forEach(function (point) { triangularByTime[String(point.time)] = point; });
      ringProfile.forEach(function (point) { ringByTime[String(point.time)] = point; });
      function inWindow(time) {
        var squarePoint = squareByTime[String(time)], triangularPoint = triangularByTime[String(time)], ringPoint = ringByTime[String(time)];
        return time >= minMacroTime && time <= maxMacroTime && squarePoint && triangularPoint && ringPoint &&
          squarePoint.zeroModeFraction <= maxZeroModeFraction && triangularPoint.zeroModeFraction <= maxZeroModeFraction &&
          ringPoint.zeroModeFraction <= maxZeroModeFraction;
      }
      var windowTimes = times.filter(inWindow);
      var windowSpan = windowTimes.length > 1 ? windowTimes[windowTimes.length - 1] / windowTimes[0] : 0;
      var windowValid = windowTimes.length >= minWindowSamples && windowSpan >= minWindowSpan;
      var comparison = profileDistance(squareProfile, triangularProfile, "spectralDimension", inWindow);
      var squareMean = meanField(squareProfile, "spectralDimension", inWindow);
      var triangularMean = meanField(triangularProfile, "spectralDimension", inWindow);
      var ringMean = meanField(ringProfile, "spectralDimension", inWindow);
      var passes = windowValid && comparison.available && comparison.rms <= CALIBRATION_PROTOCOL.rmsThreshold &&
        Math.abs(squareMean - CALIBRATION_PROTOCOL.targetDimension) <= CALIBRATION_PROTOCOL.targetTolerance &&
        Math.abs(triangularMean - CALIBRATION_PROTOCOL.targetDimension) <= CALIBRATION_PROTOCOL.targetTolerance &&
        Math.abs(ringMean - CALIBRATION_PROTOCOL.controlTargetDimension) <= CALIBRATION_PROTOCOL.controlTolerance &&
        Math.abs(ringMean - CALIBRATION_PROTOCOL.targetDimension) >= CALIBRATION_PROTOCOL.negativeControlSeparation;
      return canonicalValue({
        size: size,
        window: {
          requestedMin: minMacroTime,
          requestedMax: maxMacroTime,
          zeroModeFractionMax: maxZeroModeFraction,
          acceptedTimes: windowTimes,
          acceptedSampleCount: windowTimes.length,
          acceptedSpan: windowSpan,
          requiredSampleCount: minWindowSamples,
          requiredSpan: minWindowSpan,
          valid: windowValid,
          status: windowValid ? "OK" : "NO_SCALING_WINDOW"
        },
        square: { spectrum: squareSpectrum, profile: squareProfile, windowMeanDimension: squareMean },
        triangular: { spectrum: triangularSpectrum, profile: triangularProfile, windowMeanDimension: triangularMean },
        ringControl: { nodeCount: size * size, profile: ringProfile, windowMeanDimension: ringMean },
        comparison: comparison,
        passesCalibrationGate: passes
      });
    });
    var eligible = refinements.filter(function (entry) { return entry.window.valid && entry.comparison.available; });
    var pass = eligible.length >= minEligibleRefinements && eligible.every(function (entry) { return entry.passesCalibrationGate; });
    var candidateStatus = pass
      ? (conformsToFrozenProtocol ? "calibrated-profile-candidate" : "exploratory-calibration-pass")
      : "rejected-calibration";
    var resultPayload = canonicalValue({
      schemaVersion: SCHEMA_VERSION,
      experiment: "spectral-profile-calibration",
      candidateStatus: candidateStatus,
      conformsToFrozenProtocol: conformsToFrozenProtocol,
      protocol: selectedProtocol,
      refinements: refinements
    });
    var resultDigest = digestValue(resultPayload);
    var hypothesis = createEvidenceRecord({
      id: CALIBRATION_PROTOCOL.hypothesisId,
      claim: "Under the frozen finite calibration protocol, periodic square and triangular normalized-Laplacian heat profiles will agree within the declared spectral-dimension tolerances on admissible intermediate windows, while an equal-size cycle will remain near spectral dimension one.",
      status: "conjectural",
      basis: "falsifiable-hypothesis",
      scope: "The finite periodic families, refinements, time grid, analytic-log-derivative estimator, zero-mode mask, and thresholds encoded by calibration protocol v1; not a continuum or full-object universality statement.",
      method: "Freeze all levels, scales, masks, estimator identity, equivalence bounds, and negative-control bounds in the source protocol before producing the result artifact.",
      falsifier: "Reject the calibration hypothesis if fewer than four unique levels expose five accepted samples over a 4x window, either 2D profile leaves 2±0.2, pairwise RMS exceeds 0.025, the cycle leaves 1±0.2, or control separation from 2 is below 0.6.",
      assumptions: ["periodic unweighted regular lattices", "continuous-time normalized-Laplacian heat semigroup", "binary64 evaluation of closed-form Fourier eigenvalue formulae"],
      artifacts: ["source:global-geometry-ii-core.js#CALIBRATION_PROTOCOL"],
      tests: ["protocol override cannot receive the confirmatory candidate label", "one-point and duplicate-level false-positive controls"],
      limitations: ["thresholds are first-release protocol choices", "bounded disks, disorder, and full U2 evidence are separate"],
      result: frozenProtocolComparable
    });
    var experimentId = conformsToFrozenProtocol
      ? CALIBRATION_PROTOCOL.id
      : CALIBRATION_PROTOCOL.id + ".exploratory." + digestValue(selectedProtocol);
    var manifest = createRunManifest({
      experimentId: experimentId,
      families: ["periodic-square", "periodic-triangular"],
      refinements: sizes,
      seeds: ["exact-deterministic"],
      observables: ["normalized-laplacian-spectrum-binary64", CALIBRATION_PROTOCOL.estimatorId],
      controls: ["cycle-graph-one-dimensional"],
      parameters: selectedProtocol,
      comparisonContract: {
        field: "spectralDimension",
        estimatorId: CALIBRATION_PROTOCOL.estimatorId,
        matchedNativeTimes: true,
        rmsThreshold: CALIBRATION_PROTOCOL.rmsThreshold,
        targetDimension: CALIBRATION_PROTOCOL.targetDimension,
        targetTolerance: CALIBRATION_PROTOCOL.targetTolerance,
        controlTargetDimension: CALIBRATION_PROTOCOL.controlTargetDimension,
        controlTolerance: CALIBRATION_PROTOCOL.controlTolerance,
        negativeControlSeparation: CALIBRATION_PROTOCOL.negativeControlSeparation,
        maxZeroModeFraction: maxZeroModeFraction,
        minWindowSamples: minWindowSamples,
        minWindowSpan: minWindowSpan,
        minEligibleRefinements: minEligibleRefinements,
        fittedAfterObservation: false,
        conformsToFrozenProtocol: conformsToFrozenProtocol
      },
      resultArtifacts: ["checksum:" + DIGEST_ALGORITHM + ":" + resultDigest]
    });
    var evidence = createEvidenceRecord({
      id: "ggii.result.spectral-profile.calibration." + resultDigest,
      claim: pass
        ? "Closed-form square and triangular spectra evaluated in binary64 agree within the frozen finite spectral-dimension profile tolerances on every eligible intermediate window, and the cycle control remains within its registered one-dimensional tolerance."
        : "The evaluated finite spectral calibration did not satisfy every declared scaling-window, profile, and control gate.",
      status: "computational",
      basis: "finite-computation",
      scope: "Binary64 evaluations of closed-form finite normalized-Laplacian spectra and the heat-trace analytic-log-derivative estimator only; this does not assert graph isometry, a common metric limit, full marked metric-measure-operator equivalence, or a continuum theorem.",
      method: "Evaluate Fourier eigenvalue formulae in binary64, compute d_s(t)=2t·Σλe^{-tλ}/Σe^{-tλ}, mask scales by finite-size and zero-mode rules, compare matched windows, and apply the frozen target and cycle-control bounds.",
      falsifier: "Invalidate this result if its bound result checksum does not reproduce, a finalized evidence or manifest digest fails, or recomputation changes any gate under the same protocol and runtime contract.",
      assumptions: ["periodic unweighted regular lattices", "continuous-time heat semigroup of the normalized graph Laplacian", "predeclared finite-size window"],
      artifacts: ["manifest:" + manifest.digest, "result:" + DIGEST_ALGORITHM + ":" + resultDigest],
      tests: ["analytic spectra versus release-1 dense eigensolver on small lattices", "deterministic replay", "one-dimensional cycle rejection control"],
      limitations: ["profile agreement is weaker than full geometry", "bounded planar and disordered ensembles are required before a universality claim", "finite-size thresholds are research protocol choices"],
      dependencies: [hypothesis.id],
      result: { candidateStatus: candidateStatus, eligibleRefinements: eligible.length, resultDigest: resultDigest, conformsToFrozenProtocol: conformsToFrozenProtocol }
    });
    return deepFreeze(canonicalValue({
      schemaVersion: SCHEMA_VERSION,
      experiment: "spectral-profile-calibration",
      candidateStatus: candidateStatus,
      conformsToFrozenProtocol: conformsToFrozenProtocol,
      protocol: selectedProtocol,
      hypothesis: hypothesis,
      resultDigestAlgorithm: DIGEST_ALGORITHM,
      resultDigest: resultDigest,
      manifest: manifest,
      evidence: evidence,
      refinements: refinements
    }));
  }

  function validateSpectralCalibrationResult(input) {
    var errors = [];
    var allowed = [
      "schemaVersion", "experiment", "candidateStatus", "conformsToFrozenProtocol",
      "protocol", "hypothesis", "resultDigestAlgorithm", "resultDigest",
      "manifest", "evidence", "refinements"
    ];
    if (!isPlainObject(input)) return { valid: false, errors: ["calibration result must be a plain object"] };
    unknownKeys(input, allowed).forEach(function (key) { errors.push("unknown calibration result field " + key); });
    if (input.schemaVersion !== SCHEMA_VERSION) errors.push("calibration result schemaVersion mismatch");
    if (input.experiment !== "spectral-profile-calibration") errors.push("calibration experiment identifier mismatch");
    if (["calibrated-profile-candidate", "exploratory-calibration-pass", "rejected-calibration"].indexOf(input.candidateStatus) < 0) errors.push("unknown calibration candidateStatus");
    if (typeof input.conformsToFrozenProtocol !== "boolean") errors.push("calibration protocol conformance flag is required");
    if (!isPlainObject(input.protocol)) errors.push("calibration protocol must be an object");
    if (!Array.isArray(input.refinements)) errors.push("calibration refinements must be an array");
    if (input.resultDigestAlgorithm !== DIGEST_ALGORITHM) errors.push("calibration result digestAlgorithm mismatch");
    if (!/^[0-9a-f]{8}$/.test(input.resultDigest || "")) errors.push("calibration result digest is missing or malformed");
    var manifestReport = validateRunManifest(input.manifest);
    if (!manifestReport.valid) errors.push("manifest: " + manifestReport.errors.join("; "));
    var evidenceReport = validateEvidenceRecord(input.evidence);
    if (!evidenceReport.valid) errors.push("evidence: " + evidenceReport.errors.join("; "));
    var hypothesisReport = validateEvidenceRecord(input.hypothesis);
    if (!hypothesisReport.valid) errors.push("hypothesis: " + hypothesisReport.errors.join("; "));
    var recomputed = null;
    if (isPlainObject(input.protocol) && Array.isArray(input.refinements)) {
      try {
        recomputed = digestValue({
          schemaVersion: SCHEMA_VERSION,
          experiment: "spectral-profile-calibration",
          candidateStatus: input.candidateStatus,
          conformsToFrozenProtocol: input.conformsToFrozenProtocol,
          protocol: input.protocol,
          refinements: input.refinements
        });
        if (recomputed !== input.resultDigest) errors.push("calibration result digest mismatch");
      } catch (error) { errors.push(error.message); }
    }
    var binding = "result:" + DIGEST_ALGORITHM + ":" + input.resultDigest;
    var manifestBinding = "checksum:" + DIGEST_ALGORITHM + ":" + input.resultDigest;
    if (!input.manifest || !Array.isArray(input.manifest.resultArtifacts) || input.manifest.resultArtifacts.indexOf(manifestBinding) < 0) errors.push("manifest does not bind the calibration result digest");
    if (!input.evidence || !Array.isArray(input.evidence.artifacts) || input.evidence.artifacts.indexOf(binding) < 0) errors.push("evidence does not bind the calibration result digest");
    if (input.evidence && input.evidence.result && input.evidence.result.candidateStatus !== input.candidateStatus) errors.push("evidence candidateStatus mismatch");
    if (input.evidence && input.evidence.result && input.evidence.result.resultDigest !== input.resultDigest) errors.push("evidence resultDigest mismatch");
    if (input.candidateStatus === "calibrated-profile-candidate" && input.conformsToFrozenProtocol !== true) errors.push("confirmatory candidate requires frozen-protocol conformance");
    return { valid: errors.length === 0, errors: errors, recomputedDigest: recomputed };
  }

  function compareAnalyticAndDenseSpectrum(options) {
    options = options || {};
    var graph = periodicLatticeGraph(options);
    var analytic = periodicLatticeSpectrum(options);
    var dense = Base.normalizedLaplacianSpectrum(graph, { maxEigenSize: 400, maxSweeps: 100, tolerance: 1e-12 });
    if (!dense.available) return { available: false, reason: dense.reason };
    var maxAbsolute = 0, squareSum = 0;
    analytic.eigenvalues.forEach(function (value, index) {
      var difference = value - dense.eigenvalues[index];
      maxAbsolute = Math.max(maxAbsolute, Math.abs(difference));
      squareSum += difference * difference;
    });
    return canonicalValue({
      available: true,
      family: analytic.family,
      nodeCount: analytic.nodeCount,
      maxAbsolute: maxAbsolute,
      rms: Math.sqrt(squareSum / analytic.eigenvalues.length),
      analyticZeroMultiplicity: analytic.zeroMultiplicity,
      denseZeroMultiplicity: dense.zeroMultiplicity,
      denseSolverConverged: dense.solver.converged
    });
  }

  return {
    VERSION: VERSION,
    SCHEMA_VERSION: SCHEMA_VERSION,
    EVIDENCE_STATUSES: EVIDENCE_STATUSES.slice(),
    EVIDENCE_BASES_BY_STATUS: canonicalValue(EVIDENCE_BASES_BY_STATUS),
    DIGEST_ALGORITHM: DIGEST_ALGORITHM,
    CALIBRATION_PROTOCOL: deepFreeze(canonicalValue(CALIBRATION_PROTOCOL)),
    stableStringify: stableStringify,
    digestValue: digestValue,
    validateEvidenceRecord: validateEvidenceRecord,
    createEvidenceRecord: createEvidenceRecord,
    validateRunManifest: validateRunManifest,
    createRunManifest: createRunManifest,
    periodicLatticeGraph: periodicLatticeGraph,
    degreeSequence: degreeSequence,
    periodicLatticeSpectrum: periodicLatticeSpectrum,
    cycleSpectrum: cycleSpectrum,
    squareWordDistance: squareWordDistance,
    triangularWordDistance: triangularWordDistance,
    latticeStepMoments: latticeStepMoments,
    latticeStepCharacteristic: latticeStepCharacteristic,
    diffusionFiniteDimensionalUniversalityControl: diffusionFiniteDimensionalUniversalityControl,
    diffusionAnisotropyPhaseDiagram: diffusionAnisotropyPhaseDiagram,
    robustWhitenedDiffusionUniversalityControl: robustWhitenedDiffusionUniversalityControl,
    graphMetricNonuniversalityControl: graphMetricNonuniversalityControl,
    heatProfileFromSpectrum: heatProfileFromSpectrum,
    profileDistance: profileDistance,
    runSpectralCalibration: runSpectralCalibration,
    validateSpectralCalibrationResult: validateSpectralCalibrationResult,
    compareAnalyticAndDenseSpectrum: compareAnalyticAndDenseSpectrum
  };
});
