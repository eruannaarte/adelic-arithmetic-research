/*
 * Global Geometry II — bounded pilot atlas.
 *
 * This module composes the exact filled-disk families with finite numerical
 * descriptors. It is a preview instrument, not the confirmatory U2 ensemble:
 * no code path in this file can emit a universality or continuum conclusion.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory(
      require("./global-geometry-core.js"),
      require("./global-geometry-ii-core.js"),
      require("./global-geometry-ii-ensembles.js")
    );
  } else {
    root.GlobalGeometryIIAtlas = factory(
      root.GlobalGeometryCore,
      root.GlobalGeometryII,
      root.GlobalGeometryIIEnsembles
    );
  }
})(typeof self !== "undefined" ? self : this, function (Base, G2, Ensembles) {
  "use strict";

  if (!Base || !G2 || !Ensembles) throw new Error("The pilot atlas requires the base, Global Geometry II, and ensemble cores.");

  var VERSION = "0.2.0-alpha.2";
  var SCHEMA = "gg.atlas.pilot/1";
  var RUN_SCHEMA = "gg.atlas.pilot-run/1";
  var CELL_SCHEMA = "gg.atlas.pilot-cell/1";
  var SPEC_IDENTITY_SCHEMA = "gg.atlas.spec-identity/1";
  var RUN_IDENTITY_SCHEMA = "gg.atlas.run-identity/1";
  var CELL_IDENTITY_SCHEMA = "gg.atlas.cell-identity/1";
  var TRANSPORT_SCHEMA = "gg.transport.dirichlet/1";
  var MAX_LINEAR_SIZE = 8;
  var MAX_RUNS = 128;
  var MAX_CELLS = 128;
  var MAX_TRANSPORT_NODES = 400;
  var MAX_TRANSPORT_EDGES = 5000;
  var LOG_FOUR = Math.log(4);
  var CANONICAL_LOG_FOUR = JSON.parse(G2.stableStringify(LOG_FOUR));
  var GAUSS_BONNET_TOLERANCE = 1e-9;
  var RAYLEIGH_TOLERANCE = 1e-8;
  var TRANSPORT_POLICY = Object.freeze({ tolerance: 1e-10, maxIterations: 10000 });
  var HEAT_TIMES = Object.freeze([0.5, 1, 2, 4, 8, 16, 32]);
  var WITHHELD_CLAIMS = Object.freeze([
    "scaling window", "refinement convergence", "ensemble uncertainty",
    "universality", "continuum limit"
  ]);

  function isPlainObject(value) {
    if (!value || typeof value !== "object" || Array.isArray(value)) return false;
    if (Object.prototype.toString.call(value) !== "[object Object]") return false;
    var prototype = Object.getPrototypeOf(value);
    if (prototype === null) return true;
    if (!Object.prototype.hasOwnProperty.call(prototype, "constructor")) return false;
    return typeof prototype.constructor === "function" &&
      Function.prototype.toString.call(prototype.constructor) === Function.prototype.toString.call(Object);
  }

  function denseArray(value) {
    if (!Array.isArray(value) || Object.keys(value).length !== value.length) return false;
    for (var i = 0; i < value.length; i += 1) {
      if (!Object.prototype.hasOwnProperty.call(value, i)) return false;
    }
    return true;
  }

  function finite(value) { return typeof value === "number" && isFinite(value); }
  function nullableFinite(value) { return value === null || finite(value); }
  function unique(array) { return new Set(array).size === array.length; }
  function hasOwn(object, key) { return Object.prototype.hasOwnProperty.call(object, key); }
  function clone(value) { return JSON.parse(JSON.stringify(value)); }
  function canonicalClone(value) { return JSON.parse(G2.stableStringify(value)); }
  function canonicalNumber(value) { return JSON.parse(G2.stableStringify(value)); }

  function deepFreeze(value) {
    if (!value || typeof value !== "object" || Object.isFrozen(value)) return value;
    Object.keys(value).forEach(function (key) { deepFreeze(value[key]); });
    return Object.freeze(value);
  }

  function unknownKeys(input, allowed) {
    if (!isPlainObject(input)) return [];
    return Object.keys(input).filter(function (key) { return allowed.indexOf(key) < 0; }).sort();
  }

  function canonicalEqual(left, right) {
    return G2.stableStringify(left) === G2.stableStringify(right);
  }

  function validIdentifier(value) {
    return typeof value === "string" && /^[a-z0-9][a-z0-9._:-]{2,127}$/i.test(value);
  }

  function fieldOrDefault(input, field, fallback) {
    return !hasOwn(input, field) || typeof input[field] === "undefined" ? fallback : input[field];
  }

  function validatePilotSpecUnsafe(input) {
    var errors = [];
    var allowed = ["schema", "id", "families", "sizes", "sigmas", "replicates", "seedRoot"];
    if (!isPlainObject(input)) return { valid: false, errors: ["pilot spec must be a plain object"], spec: null };
    unknownKeys(input, allowed).forEach(function (key) { errors.push("unknown pilot field " + key); });

    var schema = fieldOrDefault(input, "schema", SCHEMA);
    var id = fieldOrDefault(input, "id", "ggii.disk-pilot.v1");
    var families = fieldOrDefault(input, "families", Ensembles.FAMILY_IDS.slice());
    var sizes = fieldOrDefault(input, "sizes", [3, 4, 6]);
    var rawSigmas = fieldOrDefault(input, "sigmas", [0, 0.75]);
    var replicates = fieldOrDefault(input, "replicates", 2);
    var seedRoot = fieldOrDefault(input, "seedRoot", "ggii/disk-pilot/v1");

    if (schema !== SCHEMA) errors.push("unsupported pilot schema");
    if (!validIdentifier(id)) errors.push("id must be a stable identifier");
    if (!denseArray(families) || !families.length || families.length > Ensembles.FAMILY_IDS.length ||
        !unique(families) || families.some(function (family) { return Ensembles.FAMILY_IDS.indexOf(family) < 0; })) {
      errors.push("families must be a unique non-empty subset of registered families");
    }
    if (!denseArray(sizes) || !sizes.length || sizes.length > 6 || !unique(sizes) || sizes.some(function (size, index) {
      return !Number.isInteger(size) || size < 3 || size > MAX_LINEAR_SIZE || (index > 0 && size <= sizes[index - 1]);
    })) errors.push("sizes must be unique increasing integers in [3, " + MAX_LINEAR_SIZE + "]");

    var sigmas = null;
    if (!denseArray(rawSigmas) || !rawSigmas.length || rawSigmas.length > 8) {
      errors.push("sigmas must be a non-empty bounded dense array");
    } else {
      var sigmaError = rawSigmas.some(function (sigma) {
        return !finite(sigma) || Object.is(sigma, -0) || sigma < 0 || sigma > CANONICAL_LOG_FOUR;
      });
      if (!sigmaError) {
        try { sigmas = rawSigmas.map(canonicalNumber); }
        catch (error) { sigmaError = true; }
      }
      if (sigmaError || !sigmas || !unique(sigmas) || sigmas.some(function (sigma, index) {
        return sigma < 0 || sigma > CANONICAL_LOG_FOUR || (index > 0 && sigma <= sigmas[index - 1]);
      })) errors.push("sigmas must remain unique increasing canonical finite values in [0, canonical log(4)]");
    }
    if (!Number.isInteger(replicates) || replicates < 1 || replicates > 8) errors.push("replicates must be an integer in [1, 8]");
    if (typeof seedRoot !== "string" || !seedRoot.length || seedRoot.length > 256) errors.push("seedRoot must be a non-empty string of at most 256 characters");
    if (denseArray(families) && denseArray(sizes) && sigmas && Number.isInteger(replicates) &&
        families.length * sizes.length * sigmas.length * replicates > MAX_RUNS) {
      errors.push("pilot matrix must contain at most " + MAX_RUNS + " runs");
    }

    var spec = null;
    if (!errors.length) {
      spec = canonicalClone({
        schema: SCHEMA,
        id: id,
        families: families.slice(),
        sizes: sizes.slice(),
        sigmas: sigmas,
        replicates: replicates,
        seedRoot: seedRoot
      });
    }
    return { valid: errors.length === 0, errors: errors, spec: spec };
  }

  function validatePilotSpec(input) {
    try { return validatePilotSpecUnsafe(input); }
    catch (error) {
      return { valid: false, errors: ["pilot spec rejected malformed input safely: " + error.message], spec: null };
    }
  }

  function requirePilotSpec(input) {
    var candidate = typeof input === "undefined" ? {} : input;
    var report = validatePilotSpec(candidate);
    if (!report.valid) throw new Error("Invalid pilot atlas spec: " + report.errors.join("; "));
    return report.spec;
  }

  function specIdentityPayload(spec) {
    return canonicalClone({
      schema: SPEC_IDENTITY_SCHEMA,
      atlasVersion: VERSION,
      baseCoreVersion: Base.VERSION,
      globalGeometryIICoreVersion: G2.VERSION,
      ensembleVersion: Ensembles.VERSION,
      spec: spec
    });
  }

  function specDigest(spec) { return G2.digestValue(specIdentityPayload(spec)); }

  function runIdentityPayload(specHash, family, familyIndex, size, sizeIndex, sigma, sigmaIndex, replicate) {
    return canonicalClone({
      schema: RUN_IDENTITY_SCHEMA,
      specDigestAlgorithm: G2.DIGEST_ALGORITHM,
      specDigest: specHash,
      familyId: family,
      familyIndex: familyIndex,
      linearSize: size,
      sizeIndex: sizeIndex,
      sigma: sigma,
      sigmaIndex: sigmaIndex,
      replicate: replicate
    });
  }

  function streamTokens(specHash, runHash) {
    var prefix = "ggii-atlas/" + specHash + "/" + runHash + "/";
    return { generator: prefix + "generator", conductance: prefix + "conductance" };
  }

  function buildExpectedMatrix(spec) {
    var hash = specDigest(spec), runs = [], cells = [];
    spec.families.forEach(function (family, familyIndex) {
      spec.sizes.forEach(function (size, sizeIndex) {
        spec.sigmas.forEach(function (sigma, sigmaIndex) {
          var expectedRuns = [];
          for (var replicate = 0; replicate < spec.replicates; replicate += 1) {
            var identity = runIdentityPayload(hash, family, familyIndex, size, sizeIndex, sigma, sigmaIndex, replicate);
            var identityDigest = G2.digestValue(identity);
            expectedRuns.push({
              identity: identity,
              identityDigest: identityDigest,
              runId: spec.id + ".run." + identityDigest,
              streams: streamTokens(hash, identityDigest),
              displayKey: family + " | L=" + size + " | sigma=" + String(sigma) + " | replicate=" + replicate
            });
          }
          var runIds = expectedRuns.map(function (run) { return run.runId; });
          var cellIdentity = canonicalClone({
            schema: CELL_IDENTITY_SCHEMA,
            specDigestAlgorithm: G2.DIGEST_ALGORITHM,
            specDigest: hash,
            familyId: family,
            familyIndex: familyIndex,
            linearSize: size,
            sizeIndex: sizeIndex,
            sigma: sigma,
            sigmaIndex: sigmaIndex,
            runIds: runIds
          });
          var cellDigest = G2.digestValue(cellIdentity);
          var expectedCell = {
            identity: cellIdentity,
            identityDigest: cellDigest,
            cellId: spec.id + ".cell." + cellDigest,
            runs: expectedRuns
          };
          expectedRuns.forEach(function (run) {
            run.cellId = expectedCell.cellId;
            runs.push(run);
          });
          cells.push(expectedCell);
        });
      });
    });
    return { specDigest: hash, runs: runs, cells: cells };
  }

  function validateTransportNetworkUnsafe(complex) {
    var errors = [];
    if (!isPlainObject(complex)) return { valid: false, errors: ["transport network must be a plain object"] };
    if (!denseArray(complex.nodes) || !complex.nodes.length || complex.nodes.length > MAX_TRANSPORT_NODES) {
      errors.push("transport nodes must be a non-empty dense array of at most " + MAX_TRANSPORT_NODES);
    }
    if (!denseArray(complex.edges) || !complex.edges.length || complex.edges.length > MAX_TRANSPORT_EDGES) {
      errors.push("transport edges must be a non-empty dense array of at most " + MAX_TRANSPORT_EDGES);
    }
    if (errors.length) return { valid: false, errors: errors };
    complex.nodes.forEach(function (node, index) {
      if (!isPlainObject(node) || !finite(node.x)) errors.push("transport node " + index + " must be a plain object with finite x");
    });
    var edgeKeys = Object.create(null);
    complex.edges.forEach(function (edge, index) {
      if (!isPlainObject(edge)) { errors.push("transport edge " + index + " must be a plain object"); return; }
      var source = edge.source, target = edge.target;
      if (!Number.isInteger(source) || !Number.isInteger(target) || source < 0 || target < 0 ||
          source >= complex.nodes.length || target >= complex.nodes.length || source === target) {
        errors.push("transport edge " + index + " has invalid exact-integer endpoints");
        return;
      }
      var key = source < target ? source + ":" + target : target + ":" + source;
      if (edgeKeys[key]) errors.push("transport edge " + index + " duplicates edge " + key);
      edgeKeys[key] = true;
      if (!finite(edge.weight) || edge.weight < 1e-12 || edge.weight > 1e12) {
        errors.push("transport edge " + index + " conductance must be finite in [1e-12, 1e12]");
      }
    });
    return { valid: errors.length === 0, errors: errors };
  }

  function validateTransportNetwork(complex) {
    try { return validateTransportNetworkUnsafe(complex); }
    catch (error) { return { valid: false, errors: ["transport network rejected malformed input safely: " + error.message] }; }
  }

  function weightedAdjacency(complex) {
    var adjacency = complex.nodes.map(function () { return []; });
    complex.edges.forEach(function (edge, index) {
      adjacency[edge.source].push({ node: edge.target, weight: edge.weight, edge: index });
      adjacency[edge.target].push({ node: edge.source, weight: edge.weight, edge: index });
    });
    adjacency.forEach(function (row) { row.sort(function (a, b) { return a.node - b.node; }); });
    return adjacency;
  }

  function residualStatistics(adjacency, potential, kind) {
    var absolute = 0, normalized = 0;
    potential.forEach(function (value, vertex) {
      if (kind[vertex] !== "interior") return;
      var denominator = 0;
      var balance = adjacency[vertex].reduce(function (sum, neighbor) {
        denominator += neighbor.weight;
        return sum + neighbor.weight * (value - potential[neighbor.node]);
      }, 0);
      absolute = Math.max(absolute, Math.abs(balance));
      if (denominator > 0) normalized = Math.max(normalized, Math.abs(balance) / denominator);
    });
    return { absolute: absolute, normalized: normalized };
  }

  function dirichletTransport(complex, options) {
    var networkReport = validateTransportNetwork(complex);
    if (!networkReport.valid) throw new Error("Invalid transport network: " + networkReport.errors.join("; "));
    options = typeof options === "undefined" ? {} : options;
    if (!isPlainObject(options)) throw new Error("transport solver policy must be a plain object");
    var optionKeys = unknownKeys(options, ["tolerance", "maxIterations"]);
    if (optionKeys.length) throw new Error("unknown transport solver field " + optionKeys.join(", "));
    var tolerance = fieldOrDefault(options, "tolerance", TRANSPORT_POLICY.tolerance);
    var maxIterations = fieldOrDefault(options, "maxIterations", TRANSPORT_POLICY.maxIterations);
    if (!finite(tolerance) || tolerance <= 0 || tolerance > 1e-3 || !Number.isInteger(maxIterations) ||
        maxIterations < 1 || maxIterations > 100000) throw new Error("invalid transport solver policy");

    var xs = complex.nodes.map(function (node) { return node.x; });
    var minX = Math.min.apply(null, xs), maxX = Math.max.apply(null, xs);
    var scale = Math.max(1, Math.abs(minX), Math.abs(maxX));
    var boundaryTolerance = 1e-10 * scale;
    var left = [], right = [], kind = new Array(complex.nodes.length).fill("interior");
    complex.nodes.forEach(function (node, index) {
      if (Math.abs(node.x - minX) <= boundaryTolerance) { left.push(index); kind[index] = "left"; }
      if (Math.abs(node.x - maxX) <= boundaryTolerance) { right.push(index); kind[index] = "right"; }
    });
    if (!left.length || !right.length || maxX - minX <= boundaryTolerance) {
      return canonicalClone({ schema: TRANSPORT_SCHEMA, available: false, reason: "opposed Dirichlet boundaries are unavailable" });
    }

    var adjacency = weightedAdjacency(complex);
    var potential = complex.nodes.map(function (_, index) {
      return kind[index] === "left" ? 1 : kind[index] === "right" ? 0 : 0.5;
    });
    var iterations = 0, maxChange = Infinity;
    var residual = { absolute: Infinity, normalized: Infinity };
    var converged = false;
    for (var iteration = 0; iteration < maxIterations; iteration += 1) {
      maxChange = 0;
      for (var vertex = 0; vertex < potential.length; vertex += 1) {
        if (kind[vertex] !== "interior") continue;
        var denominator = 0, numerator = 0;
        adjacency[vertex].forEach(function (neighbor) {
          denominator += neighbor.weight;
          numerator += neighbor.weight * potential[neighbor.node];
        });
        if (denominator <= 0) continue;
        var next = numerator / denominator;
        maxChange = Math.max(maxChange, Math.abs(next - potential[vertex]));
        potential[vertex] = next;
      }
      iterations = iteration + 1;
      residual = residualStatistics(adjacency, potential, kind);
      if (maxChange <= tolerance && residual.normalized <= tolerance) {
        converged = true;
        break;
      }
    }

    var leftSet = Object.create(null), rightSet = Object.create(null);
    left.forEach(function (vertex) { leftSet[vertex] = true; });
    right.forEach(function (vertex) { rightSet[vertex] = true; });
    var leftCurrent = 0, rightCurrent = 0;
    complex.edges.forEach(function (edge) {
      if (leftSet[edge.source] && !leftSet[edge.target]) leftCurrent += edge.weight * (potential[edge.source] - potential[edge.target]);
      else if (leftSet[edge.target] && !leftSet[edge.source]) leftCurrent += edge.weight * (potential[edge.target] - potential[edge.source]);
      if (rightSet[edge.source] && !rightSet[edge.target]) rightCurrent += edge.weight * (potential[edge.target] - potential[edge.source]);
      else if (rightSet[edge.target] && !rightSet[edge.source]) rightCurrent += edge.weight * (potential[edge.source] - potential[edge.target]);
    });
    leftCurrent = canonicalNumber(leftCurrent);
    rightCurrent = canonicalNumber(rightCurrent);
    var currentResidual = canonicalNumber(Math.abs(leftCurrent - rightCurrent));
    var currentTolerance = canonicalNumber(3 * complex.nodes.length * tolerance);
    var currentsValid = finite(leftCurrent) && finite(rightCurrent) && leftCurrent >= -tolerance && rightCurrent >= -tolerance;
    converged = converged && currentsValid && currentResidual <= currentTolerance;
    var conductance = leftCurrent;
    return canonicalClone({
      schema: TRANSPORT_SCHEMA,
      available: true,
      method: "deterministic in-place Gauss-Seidel Dirichlet solve",
      boundaryRule: "minimum-x potential 1 and maximum-x potential 0",
      leftBoundaryCount: left.length,
      rightBoundaryCount: right.length,
      conductance: conductance,
      resistance: conductance > 0 ? 1 / conductance : null,
      leftCurrent: leftCurrent,
      rightCurrent: rightCurrent,
      currentConservationResidual: currentResidual,
      currentConservationTolerance: currentTolerance,
      iterations: iterations,
      converged: converged,
      maximumUpdate: maxChange,
      maximumInteriorResidual: residual.absolute,
      maximumNormalizedInteriorResidual: residual.normalized,
      tolerance: tolerance,
      maxIterations: maxIterations,
      potential: potential
    });
  }

  function finiteValues(profile, field) {
    return (profile || []).map(function (point) { return point[field]; }).filter(finite);
  }

  function median(values) {
    if (!values.length) return null;
    var sorted = values.slice().sort(function (a, b) { return a - b; });
    var middle = Math.floor(sorted.length / 2);
    return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
  }

  function perturbFirstConductance(complex, factor) {
    var changed = clone(complex);
    if (changed.edges.length) changed.edges[0].weight *= factor;
    return changed;
  }

  function transportConverged(result) {
    return isPlainObject(result) && result.available === true && result.converged === true &&
      finite(result.conductance) && result.conductance >= 0 &&
      finite(result.maximumUpdate) && result.maximumUpdate <= result.tolerance &&
      finite(result.maximumNormalizedInteriorResidual) && result.maximumNormalizedInteriorResidual <= result.tolerance &&
      finite(result.currentConservationResidual) && finite(result.currentConservationTolerance) &&
      result.currentConservationResidual <= result.currentConservationTolerance;
  }

  function measureRun(complex) {
    var topology = Base.computeBettiNumbers(complex);
    var surface = Base.surfaceValidity(complex, { metric: "embedded" });
    var curvature = Base.angleDefectCurvature(complex, { metric: "embedded" });
    var spectrum = Base.normalizedLaplacianSpectrum(complex, { maxEigenSize: 200, heatTimes: HEAT_TIMES, maxSweeps: 100 });
    var volume = Base.volumeGrowthProfile(complex, { sourceLimit: Math.min(24, complex.nodes.length), maxRadius: 10 });
    var walk = Base.walkDimensionProfile(complex, { walkSourceLimit: Math.min(12, complex.nodes.length), walkSteps: 16 });
    var transport = dirichletTransport(complex, TRANSPORT_POLICY);
    var perturbedTransport = dirichletTransport(perturbFirstConductance(complex, 1.01), TRANSPORT_POLICY);
    var response = null;
    if (transportConverged(transport) && transportConverged(perturbedTransport) && transport.conductance > 1e-14) {
      response = canonicalNumber((perturbedTransport.conductance - transport.conductance) / transport.conductance);
    }
    var rayleighPass = response !== null && response >= -RAYLEIGH_TOLERANCE;
    return canonicalClone({
      exact: {
        betti: topology.betti.array,
        eulerCharacteristic: topology.eulerCharacteristic,
        eulerPoincareResidual: topology.eulerPoincareResidual,
        surfaceValid: surface.valid,
        boundaryComponents: topology.boundary.componentCount,
        gaussBonnetApplicable: curvature.identityApplicable,
        gaussBonnetResidual: curvature.gaussBonnetResidual,
        totalAngleDefect: curvature.total
      },
      dimensions: {
        volumeProfile: volume.profile,
        spectralProfile: spectrum.available ? spectrum.spectralDimensionProfile : [],
        walkProfile: walk.profile,
        unvalidatedDescriptorMedians: {
          volume: median(finiteValues(volume.profile.slice(2, -1), "localDimension")),
          spectral: spectrum.available ? median(finiteValues(spectrum.spectralDimensionProfile.slice(1, -1), "value")) : null,
          walk: median(finiteValues(walk.profile.slice(2, -2), "walkDimension"))
        },
        descriptorWindowPolicy: "fixed finite-preview slices; no plateau or scaling eligibility claim"
      },
      spectrum: {
        available: spectrum.available,
        gap: spectrum.available ? spectrum.spectralGap : null,
        zeroMultiplicity: spectrum.available ? spectrum.zeroMultiplicity : null,
        solver: spectrum.available ? spectrum.solver : null,
        withheldReason: spectrum.available ? null : spectrum.reason
      },
      transport: transport,
      oneEdgeSensitivity: {
        perturbation: "multiply first canonical edge conductance by 1.01",
        edgeIndex: 0,
        factor: 1.01,
        signedRelativeConductanceResponse: response,
        rayleighTolerance: RAYLEIGH_TOLERANCE,
        rayleighMonotonicityPass: rayleighPass,
        baseConverged: transportConverged(transport),
        perturbedConverged: transportConverged(perturbedTransport),
        interpretation: "single declared edge sensitivity, not a stability or robustness estimate",
        perturbedTransport: perturbedTransport
      },
      evidenceCeiling: "finite-numerical-preview",
      withheldClaims: WITHHELD_CLAIMS.slice()
    });
  }

  function mean(values) {
    var items = values.filter(finite);
    return items.length ? items.reduce(function (sum, value) { return sum + value; }, 0) / items.length : null;
  }

  function exactRunPass(run) {
    var exact = run.measurements.exact;
    return exact.surfaceValid === true && exact.gaussBonnetApplicable === true &&
      exact.eulerCharacteristic === 1 && exact.eulerPoincareResidual === 0 && exact.boundaryComponents === 1 &&
      denseArray(exact.betti) && exact.betti.join(",") === "1,0,0" &&
      finite(exact.gaussBonnetResidual) && Math.abs(exact.gaussBonnetResidual) <= GAUSS_BONNET_TOLERANCE;
  }

  function transportRunPass(run) {
    return transportConverged(run.measurements.transport) && run.measurements.transport.conductance > 0;
  }

  function rayleighRunPass(run) {
    var sensitivity = run.measurements.oneEdgeSensitivity;
    return sensitivity.baseConverged === true && sensitivity.perturbedConverged === true &&
      finite(sensitivity.signedRelativeConductanceResponse) && sensitivity.rayleighMonotonicityPass === true &&
      sensitivity.signedRelativeConductanceResponse >= -RAYLEIGH_TOLERANCE;
  }

  function buildRunRecord(expected, complex) {
    return canonicalClone({
      schema: RUN_SCHEMA,
      runId: expected.runId,
      identityDigestAlgorithm: G2.DIGEST_ALGORITHM,
      identityDigest: expected.identityDigest,
      identity: expected.identity,
      cellId: expected.cellId,
      displayKey: expected.displayKey,
      familyId: expected.identity.familyId,
      familyIndex: expected.identity.familyIndex,
      linearSize: expected.identity.linearSize,
      sizeIndex: expected.identity.sizeIndex,
      sigma: expected.identity.sigma,
      sigmaIndex: expected.identity.sigmaIndex,
      replicate: expected.identity.replicate,
      streams: expected.streams,
      structureDigestAlgorithm: complex.metadata.structureDigestAlgorithm,
      structureDigest: complex.metadata.structureDigest,
      complexSummary: { vertices: complex.nodes.length, edges: complex.edges.length, faces: complex.faces.length },
      measurements: measureRun(complex)
    });
  }

  function buildCellRecord(expected, members, requiredReplicates) {
    var exactPass = members.length === requiredReplicates && members.every(exactRunPass);
    var transportPass = members.length === requiredReplicates && members.every(transportRunPass);
    var rayleighPass = members.length === requiredReplicates && members.every(rayleighRunPass);
    var uniqueRealizations = new Set(members.map(function (run) { return run.structureDigest; })).size;
    return canonicalClone({
      schema: CELL_SCHEMA,
      cellId: expected.cellId,
      identityDigestAlgorithm: G2.DIGEST_ALGORITHM,
      identityDigest: expected.identityDigest,
      identity: expected.identity,
      familyId: expected.identity.familyId,
      familyIndex: expected.identity.familyIndex,
      linearSize: expected.identity.linearSize,
      sizeIndex: expected.identity.sizeIndex,
      sigma: expected.identity.sigma,
      sigmaIndex: expected.identity.sigmaIndex,
      runIds: members.map(function (run) { return run.runId; }),
      requiredReplicateCount: requiredReplicates,
      replicateCount: members.length,
      uniqueRealizationCount: uniqueRealizations,
      duplicateRealizationCount: members.length - uniqueRealizations,
      exactGatePass: exactPass,
      transportGatePass: transportPass,
      rayleighGatePass: rayleighPass,
      summaries: {
        spectralGapMean: mean(members.map(function (run) { return run.measurements.spectrum.gap; })),
        conductanceMean: mean(members.map(function (run) { return run.measurements.transport.conductance; })),
        signedOneEdgeSensitivityMean: mean(members.map(function (run) { return run.measurements.oneEdgeSensitivity.signedRelativeConductanceResponse; })),
        unvalidatedDimensionDescriptorMeans: {
          volume: mean(members.map(function (run) { return run.measurements.dimensions.unvalidatedDescriptorMedians.volume; })),
          spectral: mean(members.map(function (run) { return run.measurements.dimensions.unvalidatedDescriptorMedians.spectral; })),
          walk: mean(members.map(function (run) { return run.measurements.dimensions.unvalidatedDescriptorMedians.walk; }))
        }
      },
      phaseLabel: exactPass && transportPass && rayleighPass
        ? "valid-disk-positive-transport-preview"
        : "invalid-or-unresolved-preview",
      evidenceClass: "finite-numerical-preview",
      universalityStatus: "NOT_EVALUATED"
    });
  }

  function buildManifest(spec, hash, resultHash) {
    return G2.createRunManifest({
      experimentId: spec.id,
      families: spec.families,
      refinements: spec.sizes,
      seeds: [spec.seedRoot],
      observables: [
        "exact-topology", "angle-defect-curvature", "finite-dimension-descriptors",
        "dirichlet-transport", "signed-one-percent-canonical-edge-sensitivity"
      ],
      controls: ["Rayleigh monotonicity under a positive conductance increase"],
      parameters: {
        pilotSchema: SCHEMA,
        specDigestAlgorithm: G2.DIGEST_ALGORITHM,
        specDigest: hash,
        atlasVersion: VERSION,
        baseCoreVersion: Base.VERSION,
        globalGeometryIICoreVersion: G2.VERSION,
        ensembleVersion: Ensembles.VERSION,
        sigmas: spec.sigmas,
        effectiveSigmaCap: LOG_FOUR,
        sigmaSerialization: "canonical binary64 values under the Global Geometry II stable JSON contract",
        replicates: spec.replicates,
        heatTimes: HEAT_TIMES,
        transportPolicy: TRANSPORT_POLICY,
        rayleighTolerance: RAYLEIGH_TOLERANCE,
        seedDerivation: "canonical spec identity digest plus canonical run identity digest and stream role",
        maximumSynchronousRuns: MAX_RUNS
      },
      comparisonContract: {
        claimLevel: "preview-only",
        universalityInferenceAllowed: false,
        continuumInferenceAllowed: false,
        scalingWindowRequiredForPromotion: true,
        duplicateRealizationsCountAsIndependent: false
      },
      environment: {
        arithmetic: "ECMAScript binary64",
        execution: "bounded synchronous preview",
        publicArtifactAddress: "SHA-256 supplied by the Node artifact generator"
      },
      resultArtifacts: ["checksum:" + G2.DIGEST_ALGORITHM + ":" + resultHash]
    });
  }

  function familyScopedClaim(spec) {
    var noun = spec.families.length === 1 ? "construction" : "constructions";
    return "The " + spec.families.length + " requested registered bounded disk " + noun + " (" +
      spec.families.join(", ") + ") produced deterministic finite preview cells with recorded exact topology/curvature gates and finite numerical spectrum, transport, and signed one-edge sensitivity descriptors.";
  }

  function buildEvidence(spec, runs, cells, resultHash, manifest) {
    var uniqueRealizations = new Set(runs.map(function (run) { return run.structureDigest; })).size;
    return G2.createEvidenceRecord({
      id: "ggii.result.disk-pilot." + resultHash,
      claim: familyScopedClaim(spec),
      status: "computational",
      basis: "finite-ensemble",
      scope: "The declared small browser-preview matrix only; no scaling-window, confirmatory uncertainty, phase-transition, universality, continuum, or robustness claim is evaluated.",
      method: "Generate every closed-spec cell and exact replicate membership, reuse release-1 disk topology and curvature gates, solve bounded finite spectrum and positive-conductance Dirichlet problems, test Rayleigh monotonicity for one declared edge, and aggregate without fitting a classifier.",
      falsifier: "Invalidate this record if the bound result checksum fails, membership is incomplete, an exact disk or solver gate fails, Rayleigh monotonicity fails beyond tolerance, a required finite estimator is nonfinite without a disclosed reason, or replay changes a run or cell.",
      assumptions: ["preview sizes only", "binary64 finite estimators", "reflecting filled disks", "uniformly elliptic declared conductance range"],
      artifacts: ["manifest:" + manifest.digest, "result:" + G2.DIGEST_ALGORITHM + ":" + resultHash],
      tests: ["canonical identity uniqueness", "deterministic replay", "exact membership and disk gates", "independent transport oracle", "transport residual and Rayleigh control", "total validation", "universality false-positive guard"],
      limitations: ["dimension descriptors use fixed preview slices and are not plateau estimates", "one-edge sensitivity is not a stability estimate", "dense spectrum limits size", "duplicate realizations are reported and are not independent evidence", "replicate counts are not confirmatory"],
      result: {
        runCount: runs.length,
        cellCount: cells.length,
        uniqueRealizationCount: uniqueRealizations,
        resultDigest: resultHash,
        universalityStatus: "NOT_EVALUATED"
      }
    });
  }

  function runPilotAtlas(input) {
    var spec = requirePilotSpec(input);
    var expected = buildExpectedMatrix(spec);
    if (expected.runs.length > MAX_RUNS) throw new Error("pilot execution exceeds the synchronous run budget");
    var expectedRunIds = expected.runs.map(function (run) { return run.runId; });
    var expectedCellIds = expected.cells.map(function (cell) { return cell.cellId; });
    var expectedStreams = [];
    expected.runs.forEach(function (run) { expectedStreams.push(run.streams.generator, run.streams.conductance); });
    if (!unique(expectedRunIds) || !unique(expectedCellIds) || !unique(expectedStreams)) {
      throw new Error("canonical pilot identity collision; change the experiment identifier or specification");
    }
    var runs = expected.runs.map(function (run) {
      var identity = run.identity;
      var complex = Ensembles.generateFamily({
        familyId: identity.familyId,
        linearSize: identity.linearSize,
        level: identity.sizeIndex,
        characteristicSpacing: 1 / identity.linearSize,
        sigma: Math.min(identity.sigma, LOG_FOUR),
        streams: run.streams
      });
      return buildRunRecord(run, complex);
    });
    var runById = Object.create(null);
    runs.forEach(function (run) { runById[run.runId] = run; });
    var cells = expected.cells.map(function (cell) {
      var members = cell.identity.runIds.map(function (runId) { return runById[runId]; }).filter(Boolean);
      return buildCellRecord(cell, members, spec.replicates);
    });
    var resultPayload = {
      schema: SCHEMA,
      version: VERSION,
      spec: spec,
      specDigestAlgorithm: G2.DIGEST_ALGORITHM,
      specDigest: expected.specDigest,
      runs: runs,
      cells: cells
    };
    var resultHash = G2.digestValue(resultPayload);
    var manifest = buildManifest(spec, expected.specDigest, resultHash);
    var evidence = buildEvidence(spec, runs, cells, resultHash, manifest);
    var result = deepFreeze(canonicalClone({
      schema: SCHEMA,
      version: VERSION,
      spec: spec,
      specDigestAlgorithm: G2.DIGEST_ALGORITHM,
      specDigest: expected.specDigest,
      resultDigestAlgorithm: G2.DIGEST_ALGORITHM,
      resultDigest: resultHash,
      manifest: manifest,
      evidence: evidence,
      runs: runs,
      cells: cells,
      universalityStatus: "NOT_EVALUATED"
    }));
    var report = validatePilotResult(result);
    if (!report.valid) throw new Error("Internal pilot result failed validation: " + report.errors.join("; "));
    return result;
  }

  function checkClosedObject(value, allowed, label, errors) {
    if (!isPlainObject(value)) { errors.push(label + " must be a plain object"); return false; }
    unknownKeys(value, allowed).forEach(function (key) { errors.push("unknown " + label + " field " + key); });
    return true;
  }

  function validateProfile(profile, allowed, label, errors) {
    if (!denseArray(profile) || profile.length > 64) { errors.push(label + " must be a bounded dense array"); return; }
    profile.forEach(function (point, index) {
      if (!checkClosedObject(point, allowed, label + "[" + index + "]", errors)) return;
      Object.keys(point).forEach(function (key) {
        if (!nullableFinite(point[key])) errors.push(label + "[" + index + "]." + key + " must be finite or null");
      });
    });
  }

  function validateTransportResult(input, vertexCount, label, errors) {
    if (!checkClosedObject(input, [
      "schema", "available", "reason", "method", "boundaryRule", "leftBoundaryCount", "rightBoundaryCount",
      "conductance", "resistance", "leftCurrent", "rightCurrent", "currentConservationResidual", "currentConservationTolerance", "iterations",
      "converged", "maximumUpdate", "maximumInteriorResidual", "maximumNormalizedInteriorResidual",
      "tolerance", "maxIterations", "potential"
    ], label, errors)) return;
    if (input.schema !== TRANSPORT_SCHEMA || typeof input.available !== "boolean") errors.push(label + " schema/availability is invalid");
    if (!input.available) {
      if (typeof input.reason !== "string" || !input.reason.length) errors.push(label + " unavailable result requires a reason");
      return;
    }
    if (typeof input.method !== "string" || typeof input.boundaryRule !== "string") errors.push(label + " method and boundary rule are required");
    ["leftBoundaryCount", "rightBoundaryCount", "iterations", "maxIterations"].forEach(function (field) {
      if (!Number.isInteger(input[field]) || input[field] < 1) errors.push(label + "." + field + " must be a positive integer");
    });
    ["conductance", "leftCurrent", "rightCurrent", "currentConservationResidual", "currentConservationTolerance", "maximumUpdate", "maximumInteriorResidual", "maximumNormalizedInteriorResidual", "tolerance"].forEach(function (field) {
      if (!finite(input[field]) || input[field] < 0) errors.push(label + "." + field + " must be finite and nonnegative");
    });
    if (input.resistance !== null && (!finite(input.resistance) || input.resistance <= 0)) errors.push(label + ".resistance must be null or finite and positive");
    if (typeof input.converged !== "boolean") errors.push(label + ".converged must be boolean");
    if (!denseArray(input.potential) || input.potential.length !== vertexCount || input.potential.some(function (value) {
      return !finite(value) || value < -1e-8 || value > 1 + 1e-8;
    })) errors.push(label + ".potential must contain one bounded finite value per vertex");
    if (input.converged && (input.maximumUpdate > input.tolerance || input.maximumNormalizedInteriorResidual > input.tolerance)) {
      errors.push(label + " claims convergence outside its update/residual tolerance");
    }
    if (finite(input.leftCurrent) && finite(input.rightCurrent) && input.currentConservationResidual !== canonicalNumber(Math.abs(input.leftCurrent - input.rightCurrent))) errors.push(label + " current-conservation residual does not match boundary currents");
    if (input.converged && input.currentConservationResidual > input.currentConservationTolerance) errors.push(label + " claims convergence outside its current-conservation tolerance");
  }

  function validateMeasurements(measurements, vertexCount, errors) {
    if (!checkClosedObject(measurements, ["exact", "dimensions", "spectrum", "transport", "oneEdgeSensitivity", "evidenceCeiling", "withheldClaims"], "measurements", errors)) return;
    var exact = measurements.exact;
    if (checkClosedObject(exact, ["betti", "eulerCharacteristic", "eulerPoincareResidual", "surfaceValid", "boundaryComponents", "gaussBonnetApplicable", "gaussBonnetResidual", "totalAngleDefect"], "measurements.exact", errors)) {
      if (!denseArray(exact.betti) || exact.betti.length !== 3 || exact.betti.some(function (value) { return !Number.isInteger(value) || value < 0; })) errors.push("measurements.exact.betti is invalid");
      ["eulerCharacteristic", "eulerPoincareResidual", "boundaryComponents"].forEach(function (field) { if (!Number.isInteger(exact[field])) errors.push("measurements.exact." + field + " must be an integer"); });
      if (typeof exact.surfaceValid !== "boolean" || typeof exact.gaussBonnetApplicable !== "boolean") errors.push("measurements.exact applicability flags must be boolean");
      if (!finite(exact.gaussBonnetResidual) || !finite(exact.totalAngleDefect)) errors.push("measurements.exact curvature values must be finite");
    }
    var dimensions = measurements.dimensions;
    if (checkClosedObject(dimensions, ["volumeProfile", "spectralProfile", "walkProfile", "unvalidatedDescriptorMedians", "descriptorWindowPolicy"], "measurements.dimensions", errors)) {
      validateProfile(dimensions.volumeProfile, ["radius", "averageVolume", "minVolume", "maxVolume", "localDimension", "dimension"], "volumeProfile", errors);
      validateProfile(dimensions.spectralProfile, ["scale", "value"], "spectralProfile", errors);
      validateProfile(dimensions.walkProfile, ["step", "scale", "meanSquareDisplacement", "logarithmicSlope", "dimension", "walkDimension"], "walkProfile", errors);
      var medians = dimensions.unvalidatedDescriptorMedians;
      if (checkClosedObject(medians, ["volume", "spectral", "walk"], "unvalidatedDescriptorMedians", errors)) {
        ["volume", "spectral", "walk"].forEach(function (field) { if (!nullableFinite(medians[field])) errors.push("unvalidatedDescriptorMedians." + field + " must be finite or null"); });
      }
      if (typeof dimensions.descriptorWindowPolicy !== "string" || !dimensions.descriptorWindowPolicy.length) errors.push("descriptorWindowPolicy is required");
    }
    var spectrum = measurements.spectrum;
    if (checkClosedObject(spectrum, ["available", "gap", "zeroMultiplicity", "solver", "withheldReason"], "measurements.spectrum", errors)) {
      if (typeof spectrum.available !== "boolean" || !nullableFinite(spectrum.gap) || (spectrum.zeroMultiplicity !== null && !Number.isInteger(spectrum.zeroMultiplicity))) errors.push("measurements.spectrum summary is invalid");
      if (spectrum.available) {
        checkClosedObject(spectrum.solver, ["method", "converged", "sweeps", "maxOffDiagonal", "validatedBounds"], "measurements.spectrum.solver", errors);
      } else if (typeof spectrum.withheldReason !== "string" || !spectrum.withheldReason.length) errors.push("unavailable spectrum requires a reason");
    }
    validateTransportResult(measurements.transport, vertexCount, "measurements.transport", errors);
    var sensitivity = measurements.oneEdgeSensitivity;
    if (checkClosedObject(sensitivity, ["perturbation", "edgeIndex", "factor", "signedRelativeConductanceResponse", "rayleighTolerance", "rayleighMonotonicityPass", "baseConverged", "perturbedConverged", "interpretation", "perturbedTransport"], "measurements.oneEdgeSensitivity", errors)) {
      if (sensitivity.edgeIndex !== 0 || sensitivity.factor !== 1.01 || sensitivity.rayleighTolerance !== RAYLEIGH_TOLERANCE) errors.push("one-edge sensitivity policy mismatch");
      if (!nullableFinite(sensitivity.signedRelativeConductanceResponse) || typeof sensitivity.rayleighMonotonicityPass !== "boolean" || typeof sensitivity.baseConverged !== "boolean" || typeof sensitivity.perturbedConverged !== "boolean") errors.push("one-edge sensitivity result is invalid");
      validateTransportResult(sensitivity.perturbedTransport, vertexCount, "measurements.oneEdgeSensitivity.perturbedTransport", errors);
      var response = null;
      if (transportConverged(measurements.transport) && transportConverged(sensitivity.perturbedTransport) && measurements.transport.conductance > 1e-14) {
        response = canonicalNumber((sensitivity.perturbedTransport.conductance - measurements.transport.conductance) / measurements.transport.conductance);
      }
      if (response !== sensitivity.signedRelativeConductanceResponse) errors.push("one-edge sensitivity response does not match bound transports");
      var rayleigh = response !== null && response >= -RAYLEIGH_TOLERANCE;
      if (sensitivity.rayleighMonotonicityPass !== rayleigh || sensitivity.baseConverged !== transportConverged(measurements.transport) || sensitivity.perturbedConverged !== transportConverged(sensitivity.perturbedTransport)) errors.push("one-edge sensitivity gates are inconsistent");
    }
    if (measurements.evidenceCeiling !== "finite-numerical-preview" || !denseArray(measurements.withheldClaims) || !canonicalEqual(measurements.withheldClaims, WITHHELD_CLAIMS)) errors.push("measurement evidence ceiling/withheld claims mismatch");
  }

  function validateRunRecord(run, expected, errors) {
    if (!checkClosedObject(run, [
      "schema", "runId", "identityDigestAlgorithm", "identityDigest", "identity", "cellId", "displayKey",
      "familyId", "familyIndex", "linearSize", "sizeIndex", "sigma", "sigmaIndex", "replicate", "streams",
      "structureDigestAlgorithm", "structureDigest", "complexSummary", "measurements"
    ], "run", errors)) return;
    if (run.schema !== RUN_SCHEMA || run.runId !== expected.runId || run.cellId !== expected.cellId || run.displayKey !== expected.displayKey) errors.push("run identity labels mismatch");
    if (run.identityDigestAlgorithm !== G2.DIGEST_ALGORITHM || run.identityDigest !== expected.identityDigest || !canonicalEqual(run.identity, expected.identity)) errors.push("run canonical identity mismatch");
    ["familyId", "familyIndex", "linearSize", "sizeIndex", "sigma", "sigmaIndex", "replicate"].forEach(function (field) {
      if (run[field] !== expected.identity[field]) errors.push("run." + field + " does not match its identity");
    });
    if (!canonicalEqual(run.streams, expected.streams)) errors.push("run stream tokens mismatch");
    if (run.structureDigestAlgorithm !== "fnv1a32-canonical-json" || typeof run.structureDigest !== "string" || !/^[0-9a-f]{8}$/.test(run.structureDigest)) errors.push("run structure digest metadata is invalid");
    var summary = run.complexSummary;
    if (checkClosedObject(summary, ["vertices", "edges", "faces"], "run.complexSummary", errors)) {
      ["vertices", "edges", "faces"].forEach(function (field) { if (!Number.isInteger(summary[field]) || summary[field] <= 0) errors.push("run.complexSummary." + field + " must be positive"); });
      if (Number.isInteger(summary.vertices) && Number.isInteger(summary.edges) && Number.isInteger(summary.faces) && summary.vertices - summary.edges + summary.faces !== 1) errors.push("run complex summary violates disk Euler characteristic");
    }
    validateMeasurements(run.measurements, summary && summary.vertices, errors);
    if (!exactRunPass(run)) errors.push("run exact disk gate failed");
    if (!transportRunPass(run)) errors.push("run positive transport gate failed");
    if (!rayleighRunPass(run)) errors.push("run Rayleigh gate failed");
  }

  function validateCellRecord(cell, expected, members, requiredReplicates, errors) {
    if (!checkClosedObject(cell, [
      "schema", "cellId", "identityDigestAlgorithm", "identityDigest", "identity", "familyId", "familyIndex",
      "linearSize", "sizeIndex", "sigma", "sigmaIndex", "runIds", "requiredReplicateCount", "replicateCount",
      "uniqueRealizationCount", "duplicateRealizationCount", "exactGatePass", "transportGatePass", "rayleighGatePass",
      "summaries", "phaseLabel", "evidenceClass", "universalityStatus"
    ], "cell", errors)) return;
    var recomputed = buildCellRecord(expected, members, requiredReplicates);
    if (!canonicalEqual(cell, recomputed)) errors.push("cell does not match its canonical identity, exact membership, summaries, or recomputed gates");
  }

  function validatePilotResultUnsafe(input) {
    var errors = [];
    if (!isPlainObject(input)) return { valid: false, errors: ["pilot result must be a plain object"] };
    var allowed = [
      "schema", "version", "spec", "specDigestAlgorithm", "specDigest", "resultDigestAlgorithm", "resultDigest",
      "manifest", "evidence", "runs", "cells", "universalityStatus"
    ];
    unknownKeys(input, allowed).forEach(function (key) { errors.push("unknown pilot result field " + key); });
    var specReport = validatePilotSpec(input.spec);
    if (!specReport.valid) errors.push("spec: " + specReport.errors.join("; "));
    else if (!canonicalEqual(input.spec, specReport.spec)) errors.push("pilot result spec is not in canonical normalized form");
    if (input.schema !== SCHEMA || input.version !== VERSION) errors.push("pilot result schema/version mismatch");
    if (input.specDigestAlgorithm !== G2.DIGEST_ALGORITHM || typeof input.specDigest !== "string" || !/^[0-9a-f]{8}$/.test(input.specDigest)) errors.push("pilot spec digest metadata is invalid");
    if (input.resultDigestAlgorithm !== G2.DIGEST_ALGORITHM || typeof input.resultDigest !== "string" || !/^[0-9a-f]{8}$/.test(input.resultDigest)) errors.push("pilot result digest metadata is invalid");
    var runsBounded = denseArray(input.runs) && input.runs.length <= MAX_RUNS;
    var cellsBounded = denseArray(input.cells) && input.cells.length <= MAX_CELLS;
    if (!runsBounded) errors.push("pilot runs must be a dense array of at most " + MAX_RUNS);
    if (!cellsBounded) errors.push("pilot cells must be a dense array of at most " + MAX_CELLS);
    if (input.universalityStatus !== "NOT_EVALUATED") errors.push("pilot result cannot claim universality");

    var expected = specReport.valid ? buildExpectedMatrix(specReport.spec) : null;
    if (expected) {
      if (input.specDigest !== expected.specDigest) errors.push("pilot spec digest mismatch");
      if (runsBounded && input.runs.length !== expected.runs.length) errors.push("pilot run cardinality mismatch");
      if (cellsBounded && input.cells.length !== expected.cells.length) errors.push("pilot cell cardinality mismatch");
    }
    var runIds = [], streamTokensSeen = [];
    if (expected && runsBounded) {
      input.runs.forEach(function (run, index) {
        if (index < expected.runs.length) validateRunRecord(run, expected.runs[index], errors);
        if (isPlainObject(run)) {
          runIds.push(run.runId);
          if (isPlainObject(run.streams)) streamTokensSeen.push(run.streams.generator, run.streams.conductance);
        }
      });
      if (!unique(runIds)) errors.push("pilot run IDs must be unique");
      if (!unique(streamTokensSeen)) errors.push("pilot stream tokens must be unique");
    }
    if (expected && cellsBounded && runsBounded) {
      var runById = Object.create(null);
      input.runs.forEach(function (run) { if (isPlainObject(run) && typeof run.runId === "string") runById[run.runId] = run; });
      input.cells.forEach(function (cell, index) {
        if (index >= expected.cells.length) return;
        var expectedCell = expected.cells[index];
        var members = expectedCell.identity.runIds.map(function (runId) { return runById[runId]; }).filter(Boolean);
        validateCellRecord(cell, expectedCell, members, specReport.spec.replicates, errors);
      });
      var cellIds = input.cells.map(function (cell) { return isPlainObject(cell) ? cell.cellId : null; });
      if (!unique(cellIds)) errors.push("pilot cell IDs must be unique");
    }

    if (specReport.valid && runsBounded && cellsBounded) {
      try {
        var recomputed = G2.digestValue({
          schema: SCHEMA,
          version: VERSION,
          spec: input.spec,
          specDigestAlgorithm: G2.DIGEST_ALGORITHM,
          specDigest: input.specDigest,
          runs: input.runs,
          cells: input.cells
        });
        if (recomputed !== input.resultDigest) errors.push("pilot result digest mismatch");
      } catch (error) { errors.push("pilot result payload is not canonicalizable: " + error.message); }
    }

    var manifestReport;
    try { manifestReport = G2.validateRunManifest(input.manifest); }
    catch (error) { manifestReport = { valid: false, errors: ["validator threw safely: " + error.message] }; }
    if (!manifestReport.valid) errors.push("manifest: " + manifestReport.errors.join("; "));
    var evidenceReport;
    try { evidenceReport = G2.validateEvidenceRecord(input.evidence); }
    catch (error) { evidenceReport = { valid: false, errors: ["validator threw safely: " + error.message] }; }
    if (!evidenceReport.valid) errors.push("evidence: " + evidenceReport.errors.join("; "));

    if (expected && typeof input.resultDigest === "string" && /^[0-9a-f]{8}$/.test(input.resultDigest)) {
      var expectedManifest = buildManifest(specReport.spec, expected.specDigest, input.resultDigest);
      if (!canonicalEqual(input.manifest, expectedManifest)) errors.push("manifest does not match the closed pilot contract");
      if (runsBounded && cellsBounded) {
        var expectedEvidence = buildEvidence(specReport.spec, input.runs, input.cells, input.resultDigest, expectedManifest);
        if (!canonicalEqual(input.evidence, expectedEvidence)) errors.push("evidence does not match the family-scoped closed pilot contract");
      }
    }
    return { valid: errors.length === 0, errors: errors };
  }

  function validatePilotResult(input) {
    try { return validatePilotResultUnsafe(input); }
    catch (error) { return { valid: false, errors: ["pilot validation rejected malformed input safely: " + error.message] }; }
  }

  return Object.freeze({
    VERSION: VERSION,
    SCHEMA: SCHEMA,
    RUN_SCHEMA: RUN_SCHEMA,
    CELL_SCHEMA: CELL_SCHEMA,
    TRANSPORT_SCHEMA: TRANSPORT_SCHEMA,
    MAX_RUNS: MAX_RUNS,
    MAX_CELLS: MAX_CELLS,
    HEAT_TIMES: HEAT_TIMES.slice(),
    TRANSPORT_POLICY: canonicalClone(TRANSPORT_POLICY),
    validatePilotSpec: validatePilotSpec,
    validateTransportNetwork: validateTransportNetwork,
    dirichletTransport: dirichletTransport,
    runPilotAtlas: runPilotAtlas,
    validatePilotResult: validatePilotResult
  });
});
