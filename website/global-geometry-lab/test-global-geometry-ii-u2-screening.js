#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const Preview = require("./global-geometry-ii-ensembles.js");
const Screening = require("./global-geometry-ii-u2-screening.js");
const BaseManifest = require("./generate-global-geometry-ii-u2-screening-manifest.js");
const Supplement = require("./generate-global-geometry-ii-u2-screening-supplement.js");

let passed = 0;
function test(name, fn) {
  try { fn(); passed += 1; process.stdout.write("PASS " + name + "\n"); }
  catch (error) { process.stderr.write("FAIL " + name + "\n" + error.stack + "\n"); process.exitCode = 1; }
}

function readdress(artifact, canonicalStringify, sha256Bytes) {
  const copy = JSON.parse(JSON.stringify(artifact)); delete copy.contentAddress;
  const canonical = canonicalStringify(copy);
  copy.contentAddress = { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest: sha256Bytes(Buffer.from(canonical, "utf8")), canonicalBytes: Buffer.byteLength(canonical, "utf8") };
  return copy;
}

function coordinateKey(node) { return node.x.toPrecision(15) + "," + node.y.toPrecision(15); }
function signature(graph, preview) {
  const nodes = preview ? graph.nodes : graph.vertices;
  const vertices = nodes.map(coordinateKey).sort();
  const edges = graph.edges.map(function (edge) {
    const a = preview ? edge.source : edge.u, b = preview ? edge.target : edge.v;
    return [coordinateKey(nodes[a]), coordinateKey(nodes[b])].sort().join("|");
  }).sort();
  const faces = graph.faces.map(function (face) { return face.map(function (index) { return coordinateKey(nodes[index]); }).sort().join("|"); }).sort();
  return { vertices: vertices, edges: edges, faces: faces };
}

function oracleSquareSignature(size, oracle) {
  const vertices = [];
  function at(x, y) { return y * (size + 1) + x; }
  for (let y = 0; y <= size; y += 1) for (let x = 0; x <= size; x += 1) vertices.push({ x: x, y: y });
  const faceRows = [];
  for (let y = 0; y < size; y += 1) for (let x = 0; x < size; x += 1) {
    const sw = at(x, y), se = at(x + 1, y), ne = at(x + 1, y + 1), nw = at(x, y + 1);
    if (oracle(x, y)) faceRows.push([sw, se, ne], [sw, ne, nw]);
    else faceRows.push([sw, se, nw], [se, ne, nw]);
  }
  const edgeMap = new Map();
  faceRows.forEach(function (face) { [[face[0], face[1]], [face[1], face[2]], [face[2], face[0]]].forEach(function (pair) { const a = Math.min(pair[0], pair[1]), b = Math.max(pair[0], pair[1]); edgeMap.set(a + ":" + b, { u: a, v: b }); }); });
  return signature({ vertices: vertices, edges: Array.from(edgeMap.values()), faces: faceRows }, false);
}

test("base manifest and v2 supplement replay their deterministic builders", function () {
  const base = JSON.parse(fs.readFileSync(path.resolve(__dirname, "../../artifacts/global-geometry-ii/u2/screening/screening-manifest-v1.json"), "utf8"));
  const supplement = JSON.parse(fs.readFileSync(path.resolve(__dirname, "../../artifacts/global-geometry-ii/u2/screening/screening-implementation-supplement-v2.json"), "utf8"));
  assert.deepStrictEqual(base, BaseManifest.buildManifest());
  assert.deepStrictEqual(supplement, Supplement.buildSupplement());
  assert.strictEqual(BaseManifest.validateManifest(base).valid, true);
  assert.strictEqual(Supplement.validateSupplement(supplement).valid, true);
  assert.strictEqual(Screening.loadManifest().supplement.contentAddress.digest, Screening.EXPECTED_SUPPLEMENT_SEMANTIC_SHA256);
});

test("fresh content addresses cannot bless supplement mutations", function () {
  const supplement = Supplement.buildSupplement();
  supplement.estimatorLanguageCorrections.randomWalk.counts.walkersPerRoot = 80;
  assert.strictEqual(Supplement.validateSupplement(readdress(supplement, Supplement.canonicalStringify, Supplement.sha256Bytes)).valid, false);
  const controlMutation = Supplement.buildSupplement();
  controlMutation.exactControlAlgorithms["comb-trap"].rounding = "toothLength=ceil(L/4)";
  assert.strictEqual(Supplement.validateSupplement(readdress(controlMutation, Supplement.canonicalStringify, Supplement.sha256Bytes)).valid, false);
});

test("SHA-256 u53 and stream derivation match frozen vectors", function () {
  assert.strictEqual(Screening.u53("0".repeat(64), "edge:a|b", 0), 0.5485663401125992);
  assert.strictEqual(Screening.deriveSeed("positive", "square-alternating", 16, 1, 7, "conductance"), "4508e37e25bfbd8c758fa0dbd2aec16bf6defc6cda8a1b17f60fae33b5eb9ae5");
});

test("census contains 3072 positive and 768 control records with unique identities and seeds", function () {
  const census = Screening.expectedCensus();
  assert.strictEqual(census.length, 3840);
  assert.strictEqual(census.filter(function (row) { return row.kind === "positive"; }).length, 3072);
  assert.strictEqual(census.filter(function (row) { return row.kind === "control"; }).length, 768);
  assert.strictEqual(new Set(census.map(function (row) { return row.runId; })).size, 3840);
  const seeds = [];
  census.forEach(function (row) { Object.values(Screening.streamsFor(row)).forEach(function (seed) { seeds.push(seed); }); });
  assert.strictEqual(new Set(seeds).size, seeds.length);
});

test("three deterministic scalable constructors exactly overlap preview through L=24", function () {
  ["square-alternating", "triangular-clipped", "cell-center-fan"].forEach(function (family) {
    [2, 4, 8, 16, 24].forEach(function (size) {
      const scalable = Screening.buildPositive(family, size, "0".repeat(64));
      const preview = Preview.generateFamily({ familyId: family, linearSize: size, sigma: 0, streams: { generator: "overlap/generator", conductance: "overlap/conductance" } });
      assert.deepStrictEqual(signature(scalable, false), signature(preview, true), family + " L=" + size);
    });
  });
});

test("hashed constructor overlaps an independent reference under a common diagonal oracle", function () {
  [2, 4, 8, 16, 24].forEach(function (size) {
    const oracle = function (x, y) { return Screening.u53("oracle".padEnd(64, "0"), "cell:" + y + ":" + x, 0) < 0.5; };
    const scalable = Screening.buildPositive("square-hashed-diagonal", size, "native".padEnd(64, "0"), { diagonalOracle: oracle });
    assert.deepStrictEqual(signature(scalable, false), oracleSquareSignature(size, oracle));
    assert.deepStrictEqual(scalable.metadata.constructionRandomAudit, { draws: 0, duplicates: 0 });
  });
});

test("native hashed constructor is deterministic, local, and has exact disk counts", function () {
  const first = Screening.buildPositive("square-hashed-diagonal", 24, "a".repeat(64));
  const second = Screening.buildPositive("square-hashed-diagonal", 24, "a".repeat(64));
  const different = Screening.buildPositive("square-hashed-diagonal", 24, "b".repeat(64));
  assert.strictEqual(Screening.analyzeGraph(first).public.structureDigest, Screening.analyzeGraph(second).public.structureDigest);
  assert.notStrictEqual(Screening.analyzeGraph(first).public.structureDigest, Screening.analyzeGraph(different).public.structureDigest);
  assert.deepStrictEqual(Screening.analyzeGraph(first).public.counts, { vertices: 625, edges: 1776, faces: 1152 });
  assert.strictEqual(first.metadata.constructionRandomAudit.draws, 576);
  assert.strictEqual(Screening.analyzeGraph(first).public.surfaceWitness.exactBetti.beta1, 0);
});

test("every positive constructor validates exact disk topology and edge incidence", function () {
  Screening.FAMILIES.forEach(function (family) {
    const audit = Screening.analyzeGraph(Screening.buildPositive(family, 24, "c".repeat(64))).public;
    assert.strictEqual(audit.connectedComponents, 1);
    assert.strictEqual(audit.surfaceWitness.valid, true);
    assert.deepStrictEqual([audit.surfaceWitness.exactBetti.beta0, audit.surfaceWitness.exactBetti.beta1, audit.surfaceWitness.exactBetti.beta2], [1, 0, 0]);
    assert.strictEqual(audit.boundary.componentCount, 1);
  });
});

test("conductance and volume screens evaluate every edge and eight roots", function () {
  const identity = Screening.expectedCensus().find(function (row) { return row.kind === "positive" && row.id === "square-hashed-diagonal" && row.size === 24 && row.sigmaIndex === 3 && row.replicate === 7; });
  const record = Screening.buildRecord(identity), report = Screening.validateRecord(record, identity);
  assert.strictEqual(report.valid, true, report.errors.join("; "));
  assert.strictEqual(record.conductanceAudit.randomAudit.drawCount, record.graphAudit.counts.edges);
  assert.strictEqual(record.conductanceAudit.boundResidual, 0);
  assert.strictEqual(record.volumeGrowthScreen.rootCount, 8);
  assert.match(record.volumeGrowthScreen.samplingNote, /smoke descriptor only/i);
});

test("decision-size walk output is descriptive, noncoverage, deterministic, and transport is nondecisional", function () {
  const identity = Screening.expectedCensus().find(function (row) { return row.kind === "positive" && row.id === "cell-center-fan" && row.size === 81 && row.sigmaIndex === 2 && row.replicate === 3; });
  const record = Screening.buildRecord(identity), serialized = JSON.stringify(record);
  assert.strictEqual(record.randomWalkScreen.rootCount, 4);
  assert.strictEqual(record.randomWalkScreen.walkersPerRoot, 8);
  assert.strictEqual(record.randomWalkScreen.totalWalkers, 32);
  assert.match(record.randomWalkScreen.rootBlockDescriptiveTWidth.label, /descriptive/i);
  assert.match(record.randomWalkScreen.rootBlockDescriptiveTWidth.label, /not a confidence interval/i);
  assert.doesNotMatch(serialized, /lower95|upper95|Interval95/);
  assert.match(record.transportScreen.decisionNote, /cannot establish transport noncollapse/i);
  assert.strictEqual(Screening.replayRecord(record).valid, true);
});

test("all four controls construct and expose their actual discriminants", function () {
  const offsets = { "comb-trap": 3072, "small-world-shortcuts": 3264, "vanishing-neck": 3456, "perforated-disk": 3648 };
  Object.keys(offsets).forEach(function (control) {
    const identity = Screening.expectedCensus()[offsets[control]], record = Screening.buildRecord(identity);
    assert.strictEqual(record.identity.id, control);
    assert.deepStrictEqual(record.failures, []);
    assert.strictEqual(Screening.validateRecord(record, identity).valid, true);
    assert.ok(record.controlDiscriminant.discriminant);
  });
});

test("L=120 perforated construction avoids argument overflow and validates 661 actual holes", function () {
  const graph = Screening.buildControl("perforated-disk", 120, "2".repeat(64)), audit = Screening.analyzeGraph(graph).public;
  assert.strictEqual(graph.metadata.targetHoleCount, 661);
  assert.strictEqual(graph.metadata.removedFaceStarCount, 661);
  assert.strictEqual(graph.metadata.minimumCenterSeparationObserved, 3);
  assert.strictEqual(audit.surfaceWitness.valid, true);
  assert.strictEqual(audit.surfaceWitness.exactBetti.beta1, 661);
  assert.strictEqual(audit.boundary.componentCount, 662);
  assert.ok(audit.largestComponentFraction >= 0.9);
});

test("freshly rehashed record measurement tampering fails semantic replay", function () {
  const identity = Screening.expectedCensus()[0], record = Screening.buildRecord(identity), tampered = JSON.parse(JSON.stringify(record));
  tampered.volumeGrowthScreen.logLogSlopeDescriptor += 0.25;
  const payload = JSON.parse(JSON.stringify(tampered)); delete payload.recordHash;
  tampered.recordHash = Screening.sha256JSON(payload);
  const report = Screening.validateRecord(tampered, identity);
  assert.strictEqual(report.valid, false);
  assert.ok(report.errors.some(function (error) { return /semantic remeasurement/.test(error); }));
});

test("record hashes exclude wall-clock telemetry and replay bit-for-bit", function () {
  const identity = Screening.expectedCensus()[1], first = Screening.buildRecord(identity), second = Screening.buildRecord(identity);
  assert.strictEqual(first.recordHash, second.recordHash);
  assert.deepStrictEqual(first, second);
  assert.strictEqual(Object.prototype.hasOwnProperty.call(first, "telemetry"), false);
});

if (!process.exitCode) process.stdout.write("Global Geometry II U2 screening: " + passed + "/" + passed + " tests passed.\n");
