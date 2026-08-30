#!/usr/bin/env node
"use strict";

var assert = require("assert");
var fs = require("fs");
var path = require("path");
var vm = require("vm");
var Base = require("./global-geometry-core.js");
var Inverse = require("./global-geometry-ii-inverse.js");

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
function gate(report, id) { return report.gates.filter(function (entry) { return entry.id === id; })[0]; }

test("exports a bounded dependency-free Slice I API", function () {
  assert.strictEqual(Inverse.SCHEMA_VERSION, 2);
  assert.strictEqual(typeof Inverse.compileInverseDesign, "function");
  assert.strictEqual(Inverse.LIMITS.maxExactSubsetLimit, 18);
  assert.deepStrictEqual(Inverse.listRepresentativeRequests(), ["tetra-uniform-pass", "triangle-valid-pass", "annulus-valid-pass", "torus-valid-pass", "tetra-subset-reject", "sphere-zero-reject", "triangle-equality-reject"]);
});

test("UMD loads in a browser-like global without the optional Global Geometry II core", function () {
  var source = fs.readFileSync(path.join(__dirname, "global-geometry-ii-inverse.js"), "utf8");
  var context = { self: { GlobalGeometryCore: Base }, Math: Math, JSON: JSON, Object: Object, Number: Number, String: String, Error: Error, RegExp: RegExp, Set: Set, ArrayBuffer: ArrayBuffer, BigInt: BigInt, isFinite: isFinite };
  vm.createContext(context);
  vm.runInContext(source, context);
  assert.strictEqual(typeof context.self.GlobalGeometryIIInverse.compileInverseDesign, "function");
  var report = context.self.GlobalGeometryIIInverse.compileInverseDesign(context.self.GlobalGeometryIIInverse.representativeRequest("tetra-uniform-pass"));
  assert.strictEqual(report.status, "PASS");
});

test("uniform tetrahedral sphere receives an exhaustive exact Model CP admission", function () {
  var report = Inverse.compileInverseDesign(Inverse.representativeRequest("tetra-uniform-pass"));
  assert.strictEqual(report.status, "PASS");
  assert.deepStrictEqual(report.gates.map(function (entry) { return entry.id; }), ["G0", "G1", "G2", "G3", "G4", "G5", "G6"]);
  assert.strictEqual(gate(report, "G3").witness.comparison, "exact-rational-multiple-of-pi");
  assert.strictEqual(gate(report, "G4").status, "PASS");
  assert.strictEqual(gate(report, "G4").basis, "exhaustive-finite-check");
  assert.strictEqual(gate(report, "G4").evidenceClass, "exact-finite-identity");
  assert.strictEqual(gate(report, "G4").witness.exhaustive, true);
  assert.strictEqual(gate(report, "G4").witness.evaluatedSubsetCount, 14);
  assert.strictEqual(gate(report, "G4").witness.subsetSlacks.length, 14);
  assert.ok(gate(report, "G4").witness.minimum.slack > 0);
  assert.match(gate(report, "G4").statement, /intrinsic statement does not establish an embedding/i);
});

test("direct metrics compile successful disk, annulus, and torus witnesses", function () {
  [
    { id: "triangle-valid-pass", betti: [1, 0, 0], boundary: 1, counts: { vertices: 3, edges: 3, faces: 1 } },
    { id: "annulus-valid-pass", betti: [1, 1, 0], boundary: 2, counts: { vertices: 10, edges: 20, faces: 10 } },
    { id: "torus-valid-pass", betti: [1, 2, 1], boundary: 0, counts: { vertices: 9, edges: 27, faces: 18 } }
  ].forEach(function (expected) {
    var report = Inverse.compileInverseDesign(Inverse.representativeRequest(expected.id));
    assert.strictEqual(report.status, "PASS", expected.id);
    assert.strictEqual(gate(report, "G1").status, "PASS");
    assert.deepStrictEqual(gate(report, "G1").witness.bettiGF2, expected.betti);
    assert.strictEqual(gate(report, "G1").witness.boundaryComponents, expected.boundary);
    assert.deepStrictEqual(gate(report, "G1").witness.simplexCounts, expected.counts);
    assert.strictEqual(gate(report, "G6").status, "PASS");
    assert.strictEqual(gate(report, "G6").evidenceClass, "exact-finite-identity");
    assert.strictEqual(gate(report, "G6").witness.checkedFaceCount, expected.counts.faces);
    assert.strictEqual(gate(report, "G6").witness.minimumTriangle.exactDyadicSign, 1);
    assert.ok(report.selectedCandidateId);
    assert.strictEqual(report.candidates.length, 1);
    assert.strictEqual(Inverse.validateCompilerReport(report).valid, true);
  });
});

test("tetrahedral obstruction passes local and total gates then returns the singleton -pi/5 witness", function () {
  var report = Inverse.compileInverseDesign(Inverse.representativeRequest("tetra-subset-reject"));
  assert.strictEqual(report.status, "FAIL");
  assert.strictEqual(gate(report, "G2").status, "PASS");
  assert.strictEqual(gate(report, "G3").status, "PASS");
  var chow = gate(report, "G4");
  assert.strictEqual(chow.status, "FAIL");
  assert.strictEqual(chow.code, "CHOW_LUO_SUBSET");
  assert.deepStrictEqual(chow.witness.minimum.subset, [0]);
  assert.deepStrictEqual(chow.witness.minimum.symbolicSlackPiCoefficient, { denominator: 5, numerator: -1 });
  assert.strictEqual(chow.witness.minimum.eulerCharacteristicFullSubcomplex, 1);
  assert.strictEqual(chow.witness.minimum.linkCount, 3);
  assert.strictEqual(chow.impossibleInDeclaredModel, true);
  assert.match(chow.statement, /declared Model CP/);
  assert.match(chow.statement, /nothing universal about arbitrary edge metrics/i);
});

test("zero-curvature sphere is rejected exactly by Gauss-Bonnet before subset search", function () {
  var report = Inverse.compileInverseDesign(Inverse.representativeRequest("sphere-zero-reject"));
  assert.strictEqual(gate(report, "G3").code, "GAUSS_BONNET_TOTAL");
  assert.strictEqual(gate(report, "G3").status, "FAIL");
  assert.deepStrictEqual(gate(report, "G3").witness.observedPiCoefficient, { denominator: 1, numerator: 0 });
  assert.deepStrictEqual(gate(report, "G3").witness.requiredPiCoefficient, { denominator: 1, numerator: 4 });
  assert.strictEqual(gate(report, "G4").status, "NOT_RUN");
  assert.strictEqual(report.repairProposals[0].preservesOriginalTarget, true);
});

test("local cone upper bound is strict and stops later exact gates", function () {
  var request = Inverse.representativeRequest("tetra-uniform-pass");
  request.id = "tetra-local-bound-reject";
  request.target.curvature.piCoefficients = [
    { numerator: 2, denominator: 1 },
    { numerator: 2, denominator: 1 },
    { numerator: 0, denominator: 1 },
    { numerator: 0, denominator: 1 }
  ];
  var report = Inverse.compileInverseDesign(request);
  assert.strictEqual(gate(report, "G2").status, "FAIL");
  assert.strictEqual(gate(report, "G2").code, "CURVATURE_LOCAL_UPPER_BOUND");
  assert.strictEqual(gate(report, "G2").witness.vertex, 0);
  assert.strictEqual(gate(report, "G3").status, "NOT_RUN");
});

test("direct edge metric equality triangle is rejected at G6 with its face witness", function () {
  var report = Inverse.compileInverseDesign(Inverse.representativeRequest("triangle-equality-reject"));
  assert.strictEqual(gate(report, "G1").status, "PASS");
  assert.strictEqual(gate(report, "G6").status, "FAIL");
  assert.strictEqual(gate(report, "G6").code, "TRIANGLE_INEQUALITY");
  assert.strictEqual(gate(report, "G6").witness.minimumTriangle.faceIndex, 0);
  assert.strictEqual(gate(report, "G6").witness.minimumTriangle.margin, 0);
  assert.strictEqual(gate(report, "G6").impossibleInDeclaredModel, true);
});

test("weighted declared Phi model runs exhaustive subset and triangle gates", function () {
  var request = Inverse.representativeRequest("tetra-uniform-pass");
  request.id = "tetra-weighted-pass";
  request.models = ["circle-packing-weighted"];
  request.constraints.phiByEdge = [0.1, 0.2, 0.3, 0.1, 0.2, 0.3];
  var report = Inverse.compileInverseDesign(request);
  assert.strictEqual(report.status, "PASS");
  assert.strictEqual(gate(report, "G4").status, "PASS");
  assert.strictEqual(gate(report, "G4").witness.exactSymbolicTangencyArithmetic, false);
  assert.strictEqual(gate(report, "G6").status, "PASS");
  assert.strictEqual(gate(report, "G6").witness.referenceOnly, true);
  assert.strictEqual(report.selectedCandidateId, null, "reference radii must not be mislabeled as a solved target");
});

test("incomplete subset search is INCONCLUSIVE and never PASS", function () {
  var request = Inverse.representativeRequest("tetra-uniform-pass");
  request.id = "tetra-incomplete-search";
  request.verification.exactSubsetLimit = 3;
  var report = Inverse.compileInverseDesign(request);
  assert.strictEqual(report.status, "INCONCLUSIVE");
  assert.strictEqual(gate(report, "G4").status, "INCONCLUSIVE");
  assert.strictEqual(gate(report, "G4").code, "CHOW_LUO_SEARCH_INCOMPLETE");
  assert.strictEqual(gate(report, "G4").witness.exhaustive, false);
  assert.ok(gate(report, "G4").witness.evaluatedSubsetCount < gate(report, "G4").witness.totalProperNonemptySubsetCount);
  assert.match(gate(report, "G4").statement, /not an admission certificate/i);
});

test("strictly positive exact slack below the declared guard is MARGINAL, never rounded to PASS", function () {
  var request = Inverse.representativeRequest("tetra-uniform-pass");
  request.id = "tetra-exact-open-boundary-margin";
  request.verification.chowLuoGuard = 1e-4;
  request.target.curvature.piCoefficients = [
    { numerator: -99999, denominator: 100000 },
    { numerator: 499999, denominator: 300000 },
    { numerator: 499999, denominator: 300000 },
    { numerator: 499999, denominator: 300000 }
  ];
  var report = Inverse.compileInverseDesign(request);
  assert.strictEqual(report.status, "MARGINAL");
  assert.strictEqual(gate(report, "G4").status, "MARGINAL");
  assert.strictEqual(gate(report, "G4").code, "CHOW_LUO_MARGIN");
  assert.deepStrictEqual(gate(report, "G4").witness.minimum.symbolicSlackPiCoefficient, { denominator: 100000, numerator: 1 });
  assert.ok(gate(report, "G4").signedMargin > 0);
  assert.ok(gate(report, "G4").signedMargin < request.verification.chowLuoGuard);
  assert.match(gate(report, "G4").statement, /open-polytope boundary/i);
});

test("surface-with-boundary never receives the closed theorem and disk doubling is explicitly NOT_RUN", function () {
  var request = Inverse.representativeRequest("triangle-equality-reject");
  request.id = "disk-cp-boundary-contract";
  request.target.kind = "intrinsic-curvature";
  delete request.target.edgeLengths;
  request.models = ["circle-packing-tangency"];
  request.target.curvature = {
    basis: "symbolic-pi",
    piCoefficients: [0, 1, 2].map(function () { return { numerator: 2, denominator: 3 }; })
  };
  var report = Inverse.compileInverseDesign(request);
  assert.strictEqual(report.status, "INCONCLUSIVE");
  assert.strictEqual(gate(report, "G4").status, "NOT_APPLICABLE");
  assert.match(gate(report, "G4").statement, /closed-surface Chow–Luo theorem was not applied/i);
  assert.match(gate(report, "G4").statement, /no CP realizability or impossibility conclusion/i);
  assert.strictEqual(gate(report, "G5").status, "NOT_RUN");
  assert.strictEqual(gate(report, "G5").impossibleInDeclaredModel, false);
});

test("unknown fields and nonfinite values fail closed with stable paths", function () {
  var unknown = Inverse.representativeRequest("tetra-uniform-pass");
  unknown.extraExecutableLookingText = "return process.exit()";
  var unknownReport = Inverse.compileInverseDesign(unknown);
  assert.strictEqual(gate(unknownReport, "G0").status, "FAIL");
  assert.deepStrictEqual(gate(unknownReport, "G0").witness.errors[0], { code: "SCHEMA_INVALID", message: "unknown field", path: "root.extraExecutableLookingText" });
  assert.strictEqual(gate(unknownReport, "G1").status, "NOT_RUN");

  var nonfinite = Inverse.representativeRequest("tetra-uniform-pass");
  nonfinite.target.discretization.complex.nodes[0].x = NaN;
  var nonfiniteReport = Inverse.compileInverseDesign(nonfinite);
  assert.ok(gate(nonfiniteReport, "G0").witness.errors.some(function (entry) { return entry.code === "NONFINITE_VALUE" && /nodes\[0\]\.x$/.test(entry.path); }));
  assert.strictEqual(nonfiniteReport.requestDigest, null);
});

test("oversized exhaustive limit returns the resource-bound certificate before mathematics", function () {
  var request = Inverse.representativeRequest("tetra-uniform-pass");
  request.verification.exactSubsetLimit = Inverse.LIMITS.maxExactSubsetLimit + 1;
  var report = Inverse.compileInverseDesign(request);
  assert.strictEqual(report.status, "FAIL");
  assert.strictEqual(gate(report, "G0").code, "RESOURCE_BOUND_EXCEEDED");
  assert.strictEqual(gate(report, "G1").status, "NOT_RUN");
});

test("topology mismatch rejects before a Chow-Luo theorem instance", function () {
  var request = Inverse.representativeRequest("tetra-uniform-pass");
  request.id = "tetra-declared-torus";
  request.target.topology.surface = "torus";
  var report = Inverse.compileInverseDesign(request);
  assert.strictEqual(gate(report, "G1").status, "FAIL");
  assert.strictEqual(gate(report, "G1").code, "TOPOLOGY_MISMATCH");
  assert.strictEqual(gate(report, "G4").status, "NOT_RUN");
});

test("duplicate face is a G1 surface witness rather than sanitized away", function () {
  var request = Inverse.representativeRequest("tetra-uniform-pass");
  request.id = "tetra-duplicate-face";
  request.target.discretization.complex.faces.push([2, 1, 0]);
  var report = Inverse.compileInverseDesign(request);
  assert.strictEqual(gate(report, "G0").status, "PASS");
  assert.strictEqual(gate(report, "G1").status, "FAIL");
  assert.ok(gate(report, "G1").witness.errors.some(function (entry) { return entry.kind === "duplicate-face"; }));
});

test("floating Gauss--Bonnet proximity never unlocks exact Chow--Luo admission", function () {
  var request = Inverse.representativeRequest("tetra-uniform-pass");
  request.id = "tetra-floating-total-near";
  request.target.curvature = { basis: "vertex", values: [Math.PI + 5e-7, Math.PI, Math.PI, Math.PI] };
  request.verification.gbTolerance = 1e-6;
  var report = Inverse.compileInverseDesign(request);
  assert.strictEqual(gate(report, "G2").status, "PASS");
  assert.strictEqual(gate(report, "G3").status, "INCONCLUSIVE");
  assert.strictEqual(gate(report, "G3").code, "GAUSS_BONNET_NUMERIC_ONLY");
  assert.strictEqual(gate(report, "G3").evidenceClass, "finite-numerical-estimate");
  assert.strictEqual(gate(report, "G4").status, "NOT_RUN");
  assert.strictEqual(report.status, "INCONCLUSIVE");
  assert.ok(!report.claims.demonstrated.some(function (claim) { return /Chow.Luo/i.test(claim); }));
});

test("an analytically feasible CP reference scale is found instead of falsely rejected", function () {
  var request = Inverse.representativeRequest("tetra-uniform-pass");
  request.id = "tetra-reference-scale";
  request.constraints.radiusBounds = [0.5, 2];
  request.constraints.edgeLengthBounds = [3, 4];
  var report = Inverse.compileInverseDesign(request);
  var triangle = gate(report, "G6");
  assert.strictEqual(triangle.status, "PASS");
  assert.strictEqual(triangle.witness.referenceScale.feasible, true);
  assert.ok(triangle.witness.referenceScale.interval[0] <= triangle.witness.referenceScale.selected);
  assert.ok(triangle.witness.referenceScale.selected <= triangle.witness.referenceScale.interval[1]);
  assert.ok(report.candidates[0].variables.radii.every(function (radius) { return radius >= 0.5 && radius <= 2; }));
  assert.ok(report.candidates[0].variables.edgeLengths.every(function (length) { return length >= 3 && length <= 4; }));
  assert.ok(report.selectedCandidateId);
});

test("canonicalization preserves every accepted binary64 value and distinguishes nearby requests", function () {
  var first = Inverse.representativeRequest("tetra-uniform-pass");
  first.id = "canonical-nearby-a";
  first.verification.chowLuoGuard = 1e-16;
  first.constraints.radiusBounds = [0.1234567890123456, 0.1234567890123457];
  var firstNormalization = Inverse.normalizeRequest(first);
  assert.strictEqual(firstNormalization.valid, true);
  assert.strictEqual(firstNormalization.normalized.verification.chowLuoGuard, 1e-16);
  assert.deepStrictEqual(firstNormalization.normalized.constraints.radiusBounds, first.constraints.radiusBounds);

  var second = clone(first);
  second.id = "canonical-nearby-b";
  second.constraints.radiusBounds[0] = 0.12345678901234561;
  var secondNormalization = Inverse.normalizeRequest(second);
  assert.strictEqual(secondNormalization.valid, true);
  assert.notStrictEqual(Inverse.digestValue(firstNormalization.normalized), Inverse.digestValue(secondNormalization.normalized));
});

test("exact dyadic triangle signs avoid catastrophic-cancellation false rejection", function () {
  var request = Inverse.representativeRequest("triangle-equality-reject");
  request.id = "large-strict-dyadic-triangle";
  request.target.edgeLengths = [1e16, 1e16, 1];
  request.constraints.edgeLengthBounds = [1e-100, 1e100];
  var report = Inverse.compileInverseDesign(request);
  var triangle = gate(report, "G6");
  assert.notStrictEqual(triangle.status, "FAIL");
  assert.strictEqual(triangle.status, "MARGINAL");
  assert.strictEqual(triangle.witness.minimumTriangle.exactDyadicSign, 1);
  assert.strictEqual(triangle.impossibleInDeclaredModel, false);
});

test("arithmetic-unsafe finite extremes fail at G0 instead of throwing", function () {
  var edgeRequest = Inverse.representativeRequest("triangle-equality-reject");
  edgeRequest.target.edgeLengths = [1e308, 1e308, 1e308];
  var edgeReport = Inverse.compileInverseDesign(edgeRequest);
  assert.strictEqual(gate(edgeReport, "G0").status, "FAIL");
  assert.ok(gate(edgeReport, "G0").witness.errors.some(function (error) { return error.code === "ARITHMETIC_UNSAFE"; }));
  assert.strictEqual(edgeReport.requestDigest, null);

  var cpRequest = Inverse.representativeRequest("tetra-uniform-pass");
  cpRequest.constraints.radiusBounds = [1e200, 1e300];
  var cpReport = Inverse.compileInverseDesign(cpRequest);
  assert.strictEqual(gate(cpReport, "G0").status, "FAIL");
  assert.ok(gate(cpReport, "G0").witness.errors.some(function (error) { return error.code === "ARITHMETIC_UNSAFE"; }));
});

test("a named topology cannot be overridden by contradictory expected Betti numbers", function () {
  var request = Inverse.representativeRequest("tetra-uniform-pass");
  request.target.topology.surface = "torus";
  request.target.topology.expectedBetti = [1, 0, 1];
  var report = Inverse.compileInverseDesign(request);
  assert.strictEqual(gate(report, "G0").status, "FAIL");
  assert.ok(gate(report, "G0").witness.errors.some(function (error) { return error.code === "TOPOLOGY_MISMATCH" && /expectedBetti$/.test(error.path); }));
  assert.strictEqual(gate(report, "G1").status, "NOT_RUN");
});

test("sparse arrays and class instances fail the data preflight without compiler exceptions", function () {
  var sparse = Inverse.representativeRequest("tetra-uniform-pass");
  delete sparse.target.curvature.piCoefficients[1];
  var sparseReport = Inverse.compileInverseDesign(sparse);
  assert.strictEqual(gate(sparseReport, "G0").status, "FAIL");
  assert.ok(gate(sparseReport, "G0").witness.errors.some(function (error) { return /dense index-only array/.test(error.message); }));
  assert.strictEqual(sparseReport.requestDigest, null);

  var custom = Inverse.representativeRequest("tetra-uniform-pass");
  class CurvaturePayload {}
  custom.target.curvature = Object.assign(new CurvaturePayload(), custom.target.curvature);
  var customReport = Inverse.compileInverseDesign(custom);
  assert.strictEqual(gate(customReport, "G0").status, "FAIL");
  assert.ok(gate(customReport, "G0").witness.errors.some(function (error) { return /plain data objects/.test(error.message); }));

  var spoofed = Inverse.representativeRequest("tetra-uniform-pass");
  var inheritedCurvature = {
    constructor: Object,
    basis: "symbolic-pi",
    piCoefficients: clone(spoofed.target.curvature.piCoefficients)
  };
  spoofed.target.curvature = Object.create(inheritedCurvature);
  var spoofedReport = Inverse.compileInverseDesign(spoofed);
  assert.strictEqual(gate(spoofedReport, "G0").status, "FAIL");
  assert.ok(gate(spoofedReport, "G0").witness.errors.some(function (error) { return /plain data objects/.test(error.message); }));

  var nullPrototypeSpoof = Inverse.representativeRequest("tetra-uniform-pass");
  var forgedPrototype = Object.create(null);
  Object.defineProperty(forgedPrototype, "constructor", { value: Object, enumerable: false });
  forgedPrototype.basis = "symbolic-pi";
  forgedPrototype.piCoefficients = clone(nullPrototypeSpoof.target.curvature.piCoefficients);
  nullPrototypeSpoof.target.curvature = Object.create(forgedPrototype);
  var nullPrototypeReport = Inverse.compileInverseDesign(nullPrototypeSpoof);
  assert.strictEqual(gate(nullPrototypeReport, "G0").status, "FAIL");
  assert.ok(gate(nullPrototypeReport, "G0").witness.errors.some(function (error) { return /plain data objects/.test(error.message); }));
});

test("rejected accessors are never invoked while constructing the malformed report", function () {
  ["id", "seed"].forEach(function (field) {
    var request = Inverse.representativeRequest("tetra-uniform-pass");
    Object.defineProperty(request, field, {
      enumerable: true,
      get: function () { throw new Error("forbidden getter executed"); }
    });
    var report = Inverse.compileInverseDesign(request);
    assert.strictEqual(gate(report, "G0").status, "FAIL");
    assert.strictEqual(report.requestDigest, null);
    assert.strictEqual(report.requestId, field === "id" ? null : "tetra-uniform-pass");
    assert.strictEqual(report.replay.seed, field === "seed" ? null : "exact-deterministic");
  });

  var tagged = Inverse.representativeRequest("tetra-uniform-pass");
  Object.defineProperty(tagged.target.curvature, Symbol.toStringTag, {
    enumerable: false,
    get: function () { throw new Error("tag-fired"); }
  });
  var taggedReport = Inverse.compileInverseDesign(tagged);
  assert.strictEqual(gate(taggedReport, "G0").status, "FAIL");
  assert.ok(gate(taggedReport, "G0").witness.errors.some(function (error) { return /symbol-keyed fields/.test(error.message); }));
});

test("every gate uses the normative evidence-class and basis vocabulary", function () {
  var evidenceBases = {
    "exact-finite-identity": ["combinatorial-identity", "theorem-instance", "exhaustive-finite-check"],
    "finite-numerical-estimate": ["optimization", "simulation", "refinement-study", "uncertainty-ensemble", "camera-estimate"],
    "research-target": ["continuum-limit", "general-inverse-design", "universality", "physical-validation"],
    "application-analogy": ["programmable-sheet", "growth-metric", "actuated-shell"]
  };
  Inverse.listRepresentativeRequests().forEach(function (id) {
    Inverse.compileInverseDesign(Inverse.representativeRequest(id)).gates.forEach(function (entry) {
      assert.ok(evidenceBases[entry.evidenceClass], entry.id + " " + entry.evidenceClass);
      assert.ok(evidenceBases[entry.evidenceClass].includes(entry.basis), entry.id + " " + entry.evidenceClass + "/" + entry.basis);
    });
  });
});

test("derived edges are capped before a rejected complex reaches mathematical gates", function () {
  var request = Inverse.representativeRequest("tetra-uniform-pass");
  request.id = "derived-edge-resource-cap";
  request.target.curvature = { basis: "procedural", procedural: "uniform", parameters: {} };
  request.target.discretization.complex.nodes = Array.from({ length: 256 }, function (_, id) { return { id: id }; });
  delete request.target.discretization.complex.edges;
  var faces = [], seen = new Set(), state = 123456789;
  function next() { state = (Math.imul(state, 1664525) + 1013904223) >>> 0; return (state >>> 16) % 256; }
  while (faces.length < 500) {
    var face = [next(), next(), next()].sort(function (a, b) { return a - b; });
    var key = face.join(":");
    if (new Set(face).size === 3 && !seen.has(key)) { seen.add(key); faces.push(face); }
  }
  request.target.discretization.complex.faces = faces;
  var report = Inverse.compileInverseDesign(request);
  assert.strictEqual(gate(report, "G0").status, "FAIL");
  assert.ok(gate(report, "G0").witness.errors.some(function (error) { return error.code === "RESOURCE_BOUND_EXCEEDED" && /derived edge count/.test(error.message); }));
  assert.strictEqual(gate(report, "G1").status, "NOT_RUN");
});

test("a valid 16-vertex exhaustive theorem run exports a bounded ledger instead of crashing", function () {
  var request = Inverse.representativeRequest("tetra-uniform-pass");
  request.id = "bipyramid-16-exhaustive";
  var equatorCount = 14;
  request.target.discretization.complex.nodes = Array.from({ length: equatorCount + 2 }, function (_, id) { return { id: id, label: "v" + id }; });
  request.target.discretization.complex.faces = [];
  for (var index = 0; index < equatorCount; index += 1) {
    var current = 2 + index, next = 2 + (index + 1) % equatorCount;
    request.target.discretization.complex.faces.push([0, current, next], [1, next, current]);
  }
  delete request.target.discretization.complex.edges;
  request.target.curvature = { basis: "procedural", procedural: "uniform", parameters: {} };
  request.verification.exactSubsetLimit = 16;
  var report = Inverse.compileInverseDesign(request);
  var chow = gate(report, "G4");
  assert.strictEqual(chow.witness.exhaustive, true);
  assert.strictEqual(chow.witness.evaluatedSubsetCount, 65534);
  assert.strictEqual(chow.witness.subsetSlacksComplete, false);
  assert.strictEqual(chow.witness.exportedSubsetRowCount, Inverse.LIMITS.maxExportedSubsetRows);
  assert.strictEqual(chow.witness.subsetSlacks.length, Inverse.LIMITS.maxExportedSubsetRows);
  assert.match(chow.witness.subsetLedgerDigest, /^[0-9a-f]{8}$/);
  assert.strictEqual(Inverse.validateCompilerReport(report).valid, true);
});

test("the exact Chow--Luo obstruction witness is invariant under vertex relabeling", function () {
  var originalRequest = Inverse.representativeRequest("tetra-subset-reject");
  var original = Inverse.compileInverseDesign(originalRequest);
  var order = [2, 0, 3, 1];
  var oldToNew = new Array(order.length);
  order.forEach(function (oldIndex, newIndex) { oldToNew[oldIndex] = newIndex; });
  var relabeled = clone(originalRequest);
  relabeled.id = "tetra-subset-reject-relabeled";
  relabeled.target.discretization.complex.nodes = order.map(function (oldIndex, newIndex) { return { id: newIndex, label: "v" + oldIndex }; });
  relabeled.target.discretization.complex.edges = originalRequest.target.discretization.complex.edges.map(function (edge) {
    return { source: oldToNew[edge.source], target: oldToNew[edge.target], length: edge.length, weight: edge.weight };
  });
  relabeled.target.discretization.complex.faces = originalRequest.target.discretization.complex.faces.map(function (face) { return face.map(function (vertex) { return oldToNew[vertex]; }); });
  relabeled.target.curvature.piCoefficients = order.map(function (oldIndex) { return clone(originalRequest.target.curvature.piCoefficients[oldIndex]); });
  var replay = Inverse.compileInverseDesign(relabeled);
  var originalMinimum = gate(original, "G4").witness.minimum;
  var replayMinimum = gate(replay, "G4").witness.minimum;
  assert.deepStrictEqual(replayMinimum.subset.map(function (vertex) { return order[vertex]; }).sort(), originalMinimum.subset);
  assert.deepStrictEqual(replayMinimum.symbolicSlackPiCoefficient, originalMinimum.symbolicSlackPiCoefficient);
  assert.strictEqual(replayMinimum.eulerCharacteristicFullSubcomplex, originalMinimum.eulerCharacteristicFullSubcomplex);
  assert.strictEqual(replayMinimum.linkCount, originalMinimum.linkCount);
});

test("normalized request, witnesses, report digest, and bytes replay deterministically", function () {
  var request = Inverse.representativeRequest("tetra-subset-reject");
  var first = Inverse.compileInverseDesign(clone(request));
  var second = Inverse.compileInverseDesign(clone(request));
  assert.strictEqual(first.requestDigest, second.requestDigest);
  assert.strictEqual(first.reportDigest, second.reportDigest);
  assert.strictEqual(Inverse.stableStringify(first), Inverse.stableStringify(second));
  assert.ok(/^[0-9a-f]{8}$/.test(first.requestDigest));
  assert.ok(/^[0-9a-f]{8}$/.test(first.reportDigest));
  assert.strictEqual(Object.isFrozen(first), true);
  assert.strictEqual(first.digestAlgorithm, Inverse.DIGEST_ALGORITHM);
  assert.strictEqual(Inverse.validateCompilerReport(first).valid, true);

  var changed = clone(first);
  changed.gates[4].status = "PASS";
  assert.strictEqual(Inverse.validateCompilerReport(changed).valid, false);
  assert.ok(Inverse.validateCompilerReport(changed).errors.some(function (error) { return /status|digest/.test(error); }));

  var unknown = clone(first);
  unknown.universallyRealizable = true;
  assert.ok(Inverse.validateCompilerReport(unknown).errors.some(function (error) { return /unknown report field/.test(error); }));

  var coordinated = clone(first);
  coordinated.gates[4].evidenceClass = "speculative-magic";
  coordinated.gates[4].basis = "because-I-said-so";
  coordinated.gates[4].unexpectedNestedField = true;
  delete coordinated.reportDigest;
  coordinated.reportDigest = Inverse.digestValue(coordinated);
  var coordinatedValidation = Inverse.validateCompilerReport(coordinated);
  assert.strictEqual(coordinatedValidation.valid, false);
  assert.ok(coordinatedValidation.errors.some(function (error) { return /unknown field|evidenceClass\/basis|does not replay/.test(error); }));
});

if (process.exitCode) {
  process.stderr.write("\nGlobal Geometry II inverse tests failed.\n");
} else {
  process.stdout.write("\n1.." + passed + "\nAll Global Geometry II inverse tests passed.\n");
}
