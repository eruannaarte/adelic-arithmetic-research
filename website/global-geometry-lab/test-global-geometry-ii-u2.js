#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");
const Ensembles = require("./global-geometry-ii-ensembles.js");
const U2 = require("./global-geometry-ii-u2.js");
const CLI = require("./generate-global-geometry-ii-u2.js");

let passed = 0;
function test(name, fn) {
  try { fn(); passed += 1; process.stdout.write("PASS " + name + "\n"); }
  catch (error) { process.stderr.write("FAIL " + name + "\n" + error.stack + "\n"); process.exitCode = 1; }
}

function edgeSignatureFromProduction(graph) {
  return graph.edges.map(function (edge) {
    const a = graph.nodes[edge.u], b = graph.nodes[edge.v], left = [a.x, a.y], right = [b.x, b.y];
    const ordered = left[0] < right[0] || (left[0] === right[0] && left[1] <= right[1]) ? [left, right] : [right, left];
    return JSON.stringify([ordered[0], ordered[1], edge.length]);
  }).sort();
}
function edgeSignatureFromPreview(complex) {
  return complex.edges.map(function (edge) {
    const a = complex.nodes[edge.source], b = complex.nodes[edge.target], left = [a.x, a.y], right = [b.x, b.y];
    const ordered = left[0] < right[0] || (left[0] === right[0] && left[1] <= right[1]) ? [left, right] : [right, left];
    return JSON.stringify([ordered[0], ordered[1], edge.length]);
  }).sort();
}

test("frozen manifest and preregistration boundary load exactly", function () {
  const manifest = U2.loadManifest();
  assert.strictEqual(manifest.experimentId, "ggii-u2-v2");
  assert.strictEqual(manifest.contentAddress.digest, U2.MANIFEST_DIGEST);
  assert.strictEqual(U2.PREREGISTRATION_COMMIT, "150e4e7");
  assert.strictEqual(manifest.protocolAdoption.protocols.decisionContract.sha256, U2.DECISION_DIGEST);
  assert.deepStrictEqual(manifest.commonGrids.rho, [1 / 32, 1 / 24, 1 / 20, 1 / 16, 1 / 12, 1 / 8, 1 / 6, 1 / 5]);
});

test("SHA object randomness has frozen normative vectors", function () {
  const seed = U2.deriveStreamSeed("confirm", "square-alternating", 0.25, 16, 0, "generator");
  assert.strictEqual(seed, "d6b8db08b030548328f5207491ffd8ac4c7e0d9704cdd07c574c55022cffcdfe");
  assert.deepStrictEqual([0, 1, 2].map(function (counter) { return U2.objectUniform(seed, "family", counter); }), [
    0.07847372247137885, 0.31606970975179616, 0.7322807547556699
  ]);
  assert.throws(function () { U2.objectUniform("bad", "family", 0); }, /SHA-256/);
});

test("all production family-size resource counts match the frozen preview formulas", function () {
  const manifest = U2.loadManifest();
  manifest.matrix.families.forEach(function (family) {
    manifest.matrix.confirmationSizes.forEach(function (size) {
      const seed = U2.deriveStreamSeed("confirm", family, 0, size, 0, "generator"), graph = U2.generateGraph(family, size, seed), expected = Ensembles.estimatePreviewResources(family, size);
      assert.strictEqual(graph.nodes.length, expected.vertices, family + " L=" + size + " vertices");
      assert.strictEqual(graph.edges.length, expected.edges, family + " L=" + size + " edges");
      assert.strictEqual(graph.faceCount, expected.faces, family + " L=" + size + " faces");
      assert.strictEqual(graph.nodes.length - graph.edges.length + graph.faceCount, 1);
    });
  });
});

test("deterministic batch constructors overlap preview geometry at L<=24", function () {
  [2, 4, 8, 16, 24].forEach(function (size) {
    ["square-alternating", "triangular-clipped", "cell-center-fan"].forEach(function (family) {
      const seed = U2.deriveStreamSeed("confirm", family, 0, 16, 0, "generator");
      const production = U2.generateGraph(family, size, seed);
      const preview = Ensembles.generateFamily({ familyId: family, linearSize: size, sigma: 0, streams: { generator: "overlap/" + family + "/generator", conductance: "overlap/" + family + "/conductance" } });
      assert.deepStrictEqual(edgeSignatureFromProduction(production), edgeSignatureFromPreview(preview), family + " L=" + size);
    });
  });
});

test("hashed batch constructor stays inside the one-diagonal-per-cell motif", function () {
  [2, 8, 24].forEach(function (size) {
    const seed = U2.deriveStreamSeed("confirm", "square-hashed-diagonal", 0, 16, 0, "generator"), graph = U2.generateGraph("square-hashed-diagonal", size, seed), expected = Ensembles.estimatePreviewResources("square-hashed-diagonal", size);
    assert.strictEqual(graph.nodes.length, expected.vertices);
    assert.strictEqual(graph.edges.length, expected.edges);
    assert.strictEqual(graph.faceCount, 2 * size * size);
    assert.strictEqual(graph.nodes.length - graph.edges.length + graph.faceCount, 1);
  });
});

test("v2 amended grid opens the two decision-bearing volume windows only", function () {
  const rho = U2.loadManifest().commonGrids.rho;
  const statuses = [16, 24, 36, 54, 81, 120].map(function (size) { return U2.primaryWindow(size, rho.map(function (value) { return value * size; })).length > 0; });
  assert.deepStrictEqual(statuses, [false, false, false, false, true, true]);
});

test("canonical roots are 64 unique keys and stream separated", function () {
  const seed = U2.deriveStreamSeed("confirm", "square-alternating", 0, 81, 0, "generator"), graph = U2.generateGraph("square-alternating", 81, seed), rootSeed = U2.deriveStreamSeed("confirm", "square-alternating", 0, 81, 0, "roots"), roots = U2.selectRoots(graph, rootSeed, 64);
  assert.strictEqual(roots.length, 64); assert.strictEqual(new Set(roots).size, 64);
  const allSeeds = U2.STREAMS.map(function (stream) { return U2.deriveStreamSeed("confirm", "square-alternating", 0, 81, 0, stream); });
  assert.strictEqual(new Set(allSeeds).size, U2.STREAMS.length);
});

test("actual control constructors honor frozen rounding and topology", function () {
  const comb = U2.combGraph(16, U2.deriveStreamSeed("control", "comb-trap", 0, 16, 0, "generator"));
  assert.strictEqual(comb.nodes.length, 17 * 5);
  const small = U2.smallWorldGraph(24, U2.deriveStreamSeed("control", "small-world-shortcuts", 0, 24, 0, "generator"));
  assert.strictEqual(small.controlMetadata.maximumEndpointsPerVertex, 1);
  assert.strictEqual(small.controlMetadata.actualShortcutCount, Math.floor(Math.floor(0.02 * 25 * 25) / 2));
  const neck = U2.vanishingNeckGraph(16, U2.deriveStreamSeed("control", "vanishing-neck", 0, 16, 0, "generator"));
  assert.strictEqual(neck.controlMetadata.corridorWidthInH, 2);
  assert.deepStrictEqual(neck.controlTopology.betti, [1, 0, 0]);
  assert.strictEqual(neck.controlTopology.validDiskWithHoles, true);
  [16, 24, 36].forEach(function (size) {
    const perforated = U2.perforatedDiskGraph(size, U2.deriveStreamSeed("control", "perforated-disk", 0, size, 0, "generator"));
    assert.strictEqual(perforated.controlMetadata.selectionComplete, true);
    assert.strictEqual(perforated.controlTopology.validDiskWithHoles, true);
    assert.strictEqual(perforated.controlTopology.betti[1], perforated.controlMetadata.actualHoleCount);
    assert.ok(perforated.controlTopology.giantComponentFraction >= 0.9);
  });
});

test("exact Gate 1 calibration passes without promoting U2", function () {
  const gate = U2.exactGateOne();
  assert.strictEqual(gate.status, "PASS");
  assert.ok(gate.densePeriodic.every(function (entry) { return entry.available && entry.denseSolverConverged && entry.maxAbsolute <= 1e-10; }));
  assert.ok(gate.exactSmallDisks.every(function (entry) { return entry.pass; }));
});

test("run identity validator rejects a forged seed", function () {
  const key = { experimentId: "ggii-u2-v2", namespace: "confirm/", familyId: "square-alternating", parameterCell: { sigma: 0 }, linearSize: 16, replicate: 0 }, seeds = {};
  U2.STREAMS.forEach(function (stream) { seeds[stream] = U2.deriveStreamSeed("confirm", key.familyId, key.parameterCell.sigma, key.linearSize, key.replicate, stream); });
  const run = { runKey: key, runId: U2.sha256({ schema: U2.RUN_SCHEMA, runKey: key }), seeds: seeds };
  assert.strictEqual(U2.validateRunIdentityRecord(run).valid, true);
  run.seeds.generator = "0".repeat(64);
  assert.strictEqual(U2.validateRunIdentityRecord(run).valid, false);
});

test("semantic replay rejects a changed nonzero replicate", function () {
  const manifest = U2.loadManifest(), cache = new Map();
  const run = U2.measurePositiveRun(manifest, "confirm", "square-alternating", 0, 16, 31, cache);
  assert.strictEqual(U2.replayPositiveRunRecord(manifest, run, new Map()).valid, true);
  run.observables.volume.meanCounts[0] += 1;
  assert.strictEqual(U2.replayPositiveRunRecord(manifest, run, new Map()).valid, false);
});

test("decision ledger is mechanically derived and fail-closed", function () {
  const exact = { status: "PASS" }, cells = [], controls = { summaries: U2.PRIMARY_CONTROLS.map(function (id) { return { id: id, countsForGate7: false }; }) }, gates = U2.deriveGates(exact, cells, controls, "NOT_RUN"), conclusion = U2.deriveConclusion(gates), ledger = { exactGateOne: exact, cells: cells, primaryControls: controls, crossPlatformStatus: "NOT_RUN", gateResults: gates, conclusion: conclusion };
  assert.strictEqual(U2.validateDecisionLedger(ledger).valid, true);
  ledger.gateResults[6].status = "PASS";
  assert.strictEqual(U2.validateDecisionLedger(ledger).valid, false);
  ledger.gateResults = gates; ledger.conclusion.status = "ACCEPTED";
  assert.strictEqual(U2.validateDecisionLedger(ledger).valid, false);
});

test("CLI refuses implicit production and requires normalization for campaign validation", function () {
  assert.throws(function () { CLI.parseArgs([]); }, /select exactly one/);
  assert.throws(function () { CLI.parseArgs(["--campaign", "--output", "x", "--normalization", "n"]); }, /40-hex/);
  assert.throws(function () { CLI.parseArgs(["--validate-campaign", "--input", "x"]); }, /normalization/);
  const parsed = CLI.parseArgs(["--calibration", "--output", "x", "--source-commit", "a".repeat(40)]);
  assert.strictEqual(parsed.mode, "calibration");
});

test("production writer refuses to replace an existing artifact", function () {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-u2-exclusive-"));
  const output = path.join(directory, "artifact.json");
  try {
    CLI.writeArtifact(output, { first: true });
    assert.throws(function () { CLI.requireUnusedOutput(output); }, /overwrite is forbidden/);
    assert.throws(function () { CLI.writeArtifact(output, { second: true }); }, /EEXIST/);
    assert.deepStrictEqual(JSON.parse(fs.readFileSync(output, "utf8")), { first: true });
  } finally {
    fs.rmSync(directory, { recursive: true });
  }
});

if (!process.exitCode) process.stdout.write("Global Geometry II U2 kernel: " + passed + "/" + passed + " tests passed.\n");
