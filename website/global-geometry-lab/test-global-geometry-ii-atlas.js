#!/usr/bin/env node
"use strict";

var assert = require("assert");
var fs = require("fs");
var path = require("path");
var vm = require("vm");
var Base = require("./global-geometry-core.js");
var G2 = require("./global-geometry-ii-core.js");
var Ensembles = require("./global-geometry-ii-ensembles.js");
var Atlas = require("./global-geometry-ii-atlas.js");
var Generator = require("./generate-global-geometry-ii-atlas.js");

var passed = 0;
function test(name, body) {
  try {
    body();
    passed += 1;
    process.stdout.write("ok " + passed + " - " + name + "\n");
  } catch (error) {
    process.stderr.write("not ok - " + name + "\n" + (error.stack || error.message) + "\n");
    process.exitCode = 1;
  }
}

function clone(value) { return JSON.parse(JSON.stringify(value)); }
function approx(actual, expected, tolerance) {
  assert.ok(Math.abs(actual - expected) <= tolerance, actual + " is not within " + tolerance + " of " + expected);
}

function smallSpec(patch) {
  return Object.assign({
    id: "ggii.disk-pilot.test",
    families: ["square-alternating"],
    sizes: [3],
    sigmas: [0],
    replicates: 1,
    seedRoot: "ggii/test/disk-pilot"
  }, patch || {});
}

function independentConductance(complex) {
  var xs = complex.nodes.map(function (node) { return node.x; });
  var minX = Math.min.apply(null, xs), maxX = Math.max.apply(null, xs);
  var scale = Math.max(1, Math.abs(minX), Math.abs(maxX));
  var tolerance = 1e-10 * scale;
  var left = Object.create(null), right = Object.create(null), interior = [];
  complex.nodes.forEach(function (node, index) {
    if (Math.abs(node.x - minX) <= tolerance) left[index] = true;
    else if (Math.abs(node.x - maxX) <= tolerance) right[index] = true;
    else interior.push(index);
  });
  var position = Object.create(null);
  interior.forEach(function (vertex, index) { position[vertex] = index; });
  var matrix = interior.map(function () { return new Array(interior.length).fill(0); });
  var rhs = new Array(interior.length).fill(0);
  var adjacency = complex.nodes.map(function () { return []; });
  complex.edges.forEach(function (edge) {
    adjacency[edge.source].push([edge.target, edge.weight]);
    adjacency[edge.target].push([edge.source, edge.weight]);
  });
  interior.forEach(function (vertex, row) {
    adjacency[vertex].forEach(function (neighbor) {
      var target = neighbor[0], weight = neighbor[1];
      matrix[row][row] += weight;
      if (hasOwn(position, target)) matrix[row][position[target]] -= weight;
      else if (left[target]) rhs[row] += weight;
    });
  });
  for (var column = 0; column < interior.length; column += 1) {
    var pivot = column;
    for (var row = column + 1; row < interior.length; row += 1) {
      if (Math.abs(matrix[row][column]) > Math.abs(matrix[pivot][column])) pivot = row;
    }
    assert.ok(Math.abs(matrix[pivot][column]) > 1e-14, "independent Dirichlet matrix is singular");
    var matrixSwap = matrix[column]; matrix[column] = matrix[pivot]; matrix[pivot] = matrixSwap;
    var rhsSwap = rhs[column]; rhs[column] = rhs[pivot]; rhs[pivot] = rhsSwap;
    var divisor = matrix[column][column];
    for (var normalize = column; normalize < interior.length; normalize += 1) matrix[column][normalize] /= divisor;
    rhs[column] /= divisor;
    for (var eliminate = 0; eliminate < interior.length; eliminate += 1) {
      if (eliminate === column) continue;
      var factor = matrix[eliminate][column];
      if (factor === 0) continue;
      for (var entry = column; entry < interior.length; entry += 1) matrix[eliminate][entry] -= factor * matrix[column][entry];
      rhs[eliminate] -= factor * rhs[column];
    }
  }
  var potential = complex.nodes.map(function (_, index) { return left[index] ? 1 : 0; });
  interior.forEach(function (vertex, index) { potential[vertex] = rhs[index]; });
  var current = 0;
  complex.edges.forEach(function (edge) {
    if (left[edge.source] && !left[edge.target]) current += edge.weight * (1 - potential[edge.target]);
    else if (left[edge.target] && !left[edge.source]) current += edge.weight * (1 - potential[edge.source]);
  });
  return { conductance: current, potential: potential };
}

function hasOwn(object, key) { return Object.prototype.hasOwnProperty.call(object, key); }

function rebindChecksums(result) {
  result.resultDigest = G2.digestValue({
    schema: Atlas.SCHEMA,
    version: Atlas.VERSION,
    spec: result.spec,
    specDigestAlgorithm: G2.DIGEST_ALGORITHM,
    specDigest: result.specDigest,
    runs: result.runs,
    cells: result.cells
  });
  var manifest = clone(result.manifest);
  delete manifest.digest;
  delete manifest.digestAlgorithm;
  manifest.resultArtifacts = ["checksum:" + G2.DIGEST_ALGORITHM + ":" + result.resultDigest];
  result.manifest = G2.createRunManifest(manifest);
  var evidence = clone(result.evidence);
  delete evidence.digest;
  delete evidence.digestAlgorithm;
  evidence.id = "ggii.result.disk-pilot." + result.resultDigest;
  evidence.artifacts = ["manifest:" + result.manifest.digest, "result:" + G2.DIGEST_ALGORITHM + ":" + result.resultDigest];
  evidence.result.resultDigest = result.resultDigest;
  result.evidence = G2.createEvidenceRecord(evidence);
  return result;
}

test("exports the repaired bounded API and full browser UMD execution matches CommonJS", function () {
  assert.strictEqual(Atlas.SCHEMA, "gg.atlas.pilot/1");
  assert.strictEqual(Atlas.MAX_RUNS, 128);
  assert.strictEqual(typeof Atlas.validateTransportNetwork, "function");
  var source = fs.readFileSync(path.join(__dirname, "global-geometry-ii-atlas.js"), "utf8");
  var context = {
    self: { GlobalGeometryCore: Base, GlobalGeometryII: G2, GlobalGeometryIIEnsembles: Ensembles },
    Math: Math, JSON: JSON, Object: Object, Array: Array, Number: Number,
    String: String, Error: Error, RegExp: RegExp, Set: Set, isFinite: isFinite,
    Infinity: Infinity
  };
  vm.createContext(context);
  vm.runInContext(source, context);
  var common = Atlas.runPilotAtlas(smallSpec({ seedRoot: "ggii/umd" }));
  var browser = context.self.GlobalGeometryIIAtlas.runPilotAtlas(smallSpec({ seedRoot: "ggii/umd" }));
  assert.strictEqual(G2.stableStringify(browser), G2.stableStringify(common));
  assert.strictEqual(context.self.GlobalGeometryIIAtlas.validatePilotResult(browser).valid, true);
});

test("spec normalization is closed under replay and rejects raw canonical collisions", function () {
  var defaults = Atlas.validatePilotSpec({});
  assert.strictEqual(defaults.valid, true);
  assert.deepStrictEqual(defaults.spec.families, Ensembles.FAMILY_IDS);
  assert.deepStrictEqual(defaults.spec.sizes, [3, 4, 6]);
  [null, false, "", [], { execute: "process.exit()" }, { families: null }, { sizes: [2] },
    { sizes: [4, 3] }, { sigmas: [-0] }, { sigmas: [0, 1e-16] }, { sigmas: [0.5, 0.5] },
    { replicates: 0 }, { seedRoot: "" }].forEach(function (spec) {
    assert.strictEqual(Atlas.validatePilotSpec(spec).valid, false, String(spec));
  });
  [null, false, ""].forEach(function (spec) {
    assert.throws(function () { Atlas.runPilotAtlas(spec); }, /Invalid pilot atlas spec/);
  });
  var hostile = {};
  Object.defineProperty(hostile, "sigmas", { enumerable: true, get: function () { throw new Error("hostile getter"); } });
  var hostileReport;
  assert.doesNotThrow(function () { hostileReport = Atlas.validatePilotSpec(hostile); });
  assert.strictEqual(hostileReport.valid, false);
  var logFour = Atlas.runPilotAtlas(smallSpec({ sigmas: [Math.log(4)] }));
  assert.strictEqual(Atlas.validatePilotResult(logFour).valid, true);
  assert.strictEqual(Atlas.validatePilotSpec(logFour.spec).valid, true);
  var awkward = Atlas.runPilotAtlas(smallSpec({ sigmas: [0.1234567890123456] }));
  assert.strictEqual(awkward.cells[0].replicateCount, 1);
  assert.strictEqual(awkward.cells[0].runIds.length, 1);
  assert.strictEqual(awkward.cells[0].exactGatePass, true);
});

test("maximum matrix and long seed roots remain bounded and executable", function () {
  assert.strictEqual(Atlas.validatePilotSpec({
    sizes: [3, 4, 5, 6, 7, 8],
    sigmas: [0, 0.1, 0.2, 0.3, 0.4, 0.5],
    replicates: 2
  }).valid, false);
  var longRoot = Atlas.runPilotAtlas(smallSpec({ seedRoot: "s".repeat(256) }));
  longRoot.runs.forEach(function (run) {
    assert.ok(run.streams.generator.length < 256);
    assert.ok(run.streams.conductance.length < 256);
  });
  assert.strictEqual(Atlas.validatePilotResult(longRoot).valid, true);
});

test("Dirichlet transport matches exact series, parallel, direct, and disconnected fixtures", function () {
  function network(xs, edges) {
    return { nodes: xs.map(function (x) { return { x: x }; }), edges: edges.map(function (edge) {
      return { source: edge[0], target: edge[1], weight: edge[2] };
    }), faces: [] };
  }
  var series = Atlas.dirichletTransport(network([0, 1, 2], [[0, 1, 2], [1, 2, 3]]));
  approx(series.conductance, 6 / 5, 1e-12);
  approx(series.potential[1], 2 / 5, 1e-12);
  assert.strictEqual(series.converged, true);
  assert.ok(series.maximumUpdate <= series.tolerance);
  assert.ok(series.maximumNormalizedInteriorResidual <= series.tolerance);
  assert.ok(series.currentConservationResidual <= series.currentConservationTolerance);
  var parallel = Atlas.dirichletTransport(network([0, 1, 1, 2], [[0, 1, 1], [1, 3, 1], [0, 2, 2], [2, 3, 2]]));
  approx(parallel.conductance, 1.5, 1e-12);
  var direct = Atlas.dirichletTransport(network([0, 1], [[0, 1, 7]]));
  approx(direct.conductance, 7, 1e-12);
  var disconnected = Atlas.dirichletTransport(network([0, 1, 2, 3], [[0, 1, 1], [2, 3, 1]]));
  assert.strictEqual(disconnected.conductance, 0);
  assert.strictEqual(disconnected.resistance, null);
  assert.strictEqual(disconnected.converged, true);
});

test("transport has a strict positive-network and solver-policy preflight", function () {
  var bad = [
    { nodes: [{ x: 0 }, { x: 1 }], edges: [{ source: 0, target: 1, weight: -1 }] },
    { nodes: [{ x: 0 }, { x: 1 }], edges: [{ source: 0, target: 7, weight: 1 }] },
    { nodes: [{ x: 0 }, { x: NaN }], edges: [{ source: 0, target: 1, weight: 1 }] },
    { nodes: [{ x: 0 }, { x: 1 }], edges: [{ source: 0, target: 1, weight: 1 }, { source: 1, target: 0, weight: 1 }] }
  ];
  bad.forEach(function (network) {
    assert.strictEqual(Atlas.validateTransportNetwork(network).valid, false);
    assert.throws(function () { Atlas.dirichletTransport(network); }, /Invalid transport network/);
  });
  var hostileNetwork = { edges: [] };
  Object.defineProperty(hostileNetwork, "nodes", { enumerable: true, get: function () { throw new Error("hostile getter"); } });
  var hostileNetworkReport;
  assert.doesNotThrow(function () { hostileNetworkReport = Atlas.validateTransportNetwork(hostileNetwork); });
  assert.strictEqual(hostileNetworkReport.valid, false);
  var good = { nodes: [{ x: 0 }, { x: 1 }], edges: [{ source: 0, target: 1, weight: 1 }] };
  assert.throws(function () { Atlas.dirichletTransport(good, null); }, /plain object/);
  assert.throws(function () { Atlas.dirichletTransport(good, { tolerance: 0 }); }, /invalid transport solver policy/);
  assert.throws(function () { Atlas.dirichletTransport(good, { execute: true }); }, /unknown transport solver field/);
});

test("an independent dense linear solve verifies transport for all four families", function () {
  Ensembles.FAMILY_IDS.forEach(function (family) {
    var complex = Ensembles.generateFamily({
      familyId: family,
      linearSize: 4,
      level: 0,
      characteristicSpacing: 0.25,
      sigma: 1.1,
      streams: { generator: "atlas-oracle/" + family + "/generator", conductance: "atlas-oracle/" + family + "/conductance" }
    });
    var independent = independentConductance(complex);
    var actual = Atlas.dirichletTransport(complex);
    assert.strictEqual(actual.converged, true, family);
    approx(actual.conductance, independent.conductance, 2e-8);
    actual.potential.forEach(function (value, index) { approx(value, independent.potential[index], 3e-9); });
  });
});

test("every family has exact membership, disk gates, positive transport, and signed Rayleigh control", function () {
  var result = Atlas.runPilotAtlas({
    id: "ggii.disk-pilot.all-families",
    families: Ensembles.FAMILY_IDS,
    sizes: [3],
    sigmas: [0, 0.75],
    replicates: 1,
    seedRoot: "ggii/test/all-families"
  });
  assert.strictEqual(result.runs.length, 8);
  assert.strictEqual(result.cells.length, 8);
  assert.strictEqual(Atlas.validatePilotResult(result).valid, true);
  result.runs.forEach(function (run) {
    assert.deepStrictEqual(run.measurements.exact.betti, [1, 0, 0]);
    assert.strictEqual(run.measurements.exact.gaussBonnetApplicable, true);
    assert.strictEqual(run.measurements.transport.converged, true);
    assert.ok(run.measurements.transport.conductance > 0);
    assert.strictEqual(run.measurements.oneEdgeSensitivity.baseConverged, true);
    assert.strictEqual(run.measurements.oneEdgeSensitivity.perturbedConverged, true);
    assert.strictEqual(run.measurements.oneEdgeSensitivity.rayleighMonotonicityPass, true);
    assert.ok(run.measurements.oneEdgeSensitivity.signedRelativeConductanceResponse >= -1e-8);
  });
  result.cells.forEach(function (cell) {
    assert.strictEqual(cell.replicateCount, 1);
    assert.strictEqual(cell.requiredReplicateCount, 1);
    assert.strictEqual(cell.runIds.length, 1);
    assert.strictEqual(cell.exactGatePass, true);
    assert.strictEqual(cell.transportGatePass, true);
    assert.strictEqual(cell.rayleighGatePass, true);
    assert.strictEqual(cell.phaseLabel, "valid-disk-positive-transport-preview");
  });
});

test("canonical object identities distinguish close sigmas, seed roots, and cells", function () {
  var close = Atlas.runPilotAtlas(smallSpec({ sigmas: [0.750000001, 0.750000002] }));
  assert.strictEqual(new Set(close.runs.map(function (run) { return run.runId; })).size, 2);
  assert.strictEqual(new Set(close.runs.map(function (run) { return run.streams.conductance; })).size, 2);
  assert.strictEqual(new Set(close.cells.map(function (cell) { return cell.cellId; })).size, 2);
  close.cells.forEach(function (cell) { assert.strictEqual(cell.replicateCount, 1); });
  var first = Atlas.runPilotAtlas(smallSpec({ sigmas: [0.75], seedRoot: "identity/root-a" }));
  var second = Atlas.runPilotAtlas(smallSpec({ sigmas: [0.75], seedRoot: "identity/root-b" }));
  assert.notStrictEqual(first.specDigest, second.specDigest);
  assert.notStrictEqual(first.runs[0].runId, second.runs[0].runId);
  assert.notStrictEqual(first.cells[0].cellId, second.cells[0].cellId);
  assert.notStrictEqual(first.runs[0].streams.conductance, second.runs[0].streams.conductance);
  assert.notStrictEqual(first.runs[0].structureDigest, second.runs[0].structureDigest);
});

test("duplicate realizations are reported rather than counted as independent evidence", function () {
  var result = Atlas.runPilotAtlas(smallSpec({ sigmas: [0], replicates: 2 }));
  assert.strictEqual(result.cells[0].replicateCount, 2);
  assert.strictEqual(result.cells[0].uniqueRealizationCount, 1);
  assert.strictEqual(result.cells[0].duplicateRealizationCount, 1);
  assert.strictEqual(result.manifest.comparisonContract.duplicateRealizationsCountAsIndependent, false);
});

test("pilot labels and evidence remain preview-only and family scoped", function () {
  var result = Atlas.runPilotAtlas(smallSpec());
  assert.strictEqual(result.universalityStatus, "NOT_EVALUATED");
  assert.strictEqual(result.cells[0].universalityStatus, "NOT_EVALUATED");
  assert.ok(!/universal/i.test(result.cells[0].phaseLabel));
  assert.match(result.evidence.claim, /The 1 requested registered bounded disk construction \(square-alternating\)/);
  assert.doesNotMatch(result.evidence.claim, /four/i);
  assert.match(result.evidence.scope, /no scaling-window.*universality.*robustness claim/i);
  assert.strictEqual(result.manifest.parameters.atlasVersion, Atlas.VERSION);
  assert.strictEqual(result.manifest.parameters.baseCoreVersion, Base.VERSION);
  assert.strictEqual(result.manifest.parameters.ensembleVersion, Ensembles.VERSION);
  assert.deepStrictEqual(result.manifest.parameters.transportPolicy, Atlas.TRANSPORT_POLICY);
  assert.strictEqual(result.manifest.comparisonContract.universalityInferenceAllowed, false);
});

test("closed validation rejects coordinated scientific forgery after public checksums are rebound", function () {
  var forged = clone(Atlas.runPilotAtlas(smallSpec()));
  forged.runs[0].measurements.exact.betti = [9, 9, 9];
  forged.runs[0].measurements.transport.conductance = -123;
  rebindChecksums(forged);
  var report = Atlas.validatePilotResult(forged);
  assert.strictEqual(report.valid, false);
  assert.ok(report.errors.some(function (error) { return /run exact disk gate failed|conductance.*nonnegative|cell does not match/.test(error); }), report.errors.join("\n"));

  var missing = clone(Atlas.runPilotAtlas(smallSpec()));
  missing.runs = [];
  missing.cells[0].runIds = [];
  missing.cells[0].replicateCount = 0;
  missing.cells[0].exactGatePass = true;
  missing.cells[0].transportGatePass = true;
  rebindChecksums(missing);
  var missingReport = Atlas.validatePilotResult(missing);
  assert.strictEqual(missingReport.valid, false);
  assert.ok(missingReport.errors.some(function (error) { return /cardinality|membership/.test(error); }), missingReport.errors.join("\n"));
});

test("result validation is total for hostile nested values and detects closed-field tampering", function () {
  var original = Atlas.runPilotAtlas(smallSpec());
  var mutations = [
    function (value) { value.resultDigest = Symbol("x"); },
    function (value) { value.runs = [new Date()]; },
    function (value) { value.cells = [function () {}]; },
    function (value) { value.runs[0].measurements.transport.conductance = NaN; },
    function (value) { value.runs[0].execute = "code"; }
  ];
  mutations.forEach(function (mutate) {
    var changed = clone(original);
    mutate(changed);
    var report;
    assert.doesNotThrow(function () { report = Atlas.validatePilotResult(changed); });
    assert.strictEqual(report.valid, false);
  });
  var oversized = clone(original);
  oversized.runs = new Array(Atlas.MAX_RUNS + 1).fill(null);
  var oversizedReport;
  assert.doesNotThrow(function () { oversizedReport = Atlas.validatePilotResult(oversized); });
  assert.strictEqual(oversizedReport.valid, false);
  assert.ok(oversizedReport.errors.some(function (error) { return /at most/.test(error); }));
  assert.strictEqual(Object.isFrozen(original), true);
  assert.strictEqual(Object.isFrozen(original.runs[0].measurements), true);
});

test("the generator builds a deterministic validated SHA-256-addressed payload in memory", function () {
  var payloadA = Generator.buildPayload(smallSpec({ seedRoot: "generator/test" }));
  var payloadB = Generator.buildPayload(smallSpec({ seedRoot: "generator/test" }));
  assert.strictEqual(G2.stableStringify(payloadA), G2.stableStringify(payloadB));
  assert.strictEqual(Atlas.validatePilotResult(payloadA.pilot).valid, true);
  assert.strictEqual(payloadA.pilot.universalityStatus, "NOT_EVALUATED");
  var addressA = Generator.contentAddress(payloadA);
  var addressB = Generator.contentAddress(payloadB);
  assert.strictEqual(addressA.algorithm, "sha256");
  assert.match(addressA.digest, /^[0-9a-f]{64}$/);
  assert.deepStrictEqual(addressA, addressB);
  assert.match(Generator.parseOutput([]), /atlas-pilot-v1\.json$/);
  assert.throws(function () { Generator.parseOutput(["--output"]); }, /requires/);
  assert.throws(function () { Generator.parseOutput(["--unknown"]); }, /unknown/);
  assert.throws(function () { Generator.parseOutput(["--output", "a", "--output", "b"]); }, /only once/);
});

if (process.exitCode) {
  process.stderr.write("\nGlobal Geometry II atlas tests failed.\n");
} else {
  process.stdout.write("\n1.." + passed + "\nAll Global Geometry II atlas tests passed.\n");
}
