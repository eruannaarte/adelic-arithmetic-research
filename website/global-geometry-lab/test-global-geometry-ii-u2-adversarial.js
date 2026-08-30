#!/usr/bin/env node
"use strict";

/* Independent outcome-review mutations. This file never runs the production matrix. */
const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const Manifest = require("./generate-global-geometry-ii-u2-manifest.js");
const U2 = require("./global-geometry-ii-u2.js");

let passed = 0;
function test(name, fn) {
  try { fn(); passed += 1; process.stdout.write("PASS " + name + "\n"); }
  catch (error) { process.stderr.write("FAIL " + name + "\n" + error.stack + "\n"); process.exitCode = 1; }
}
function clone(value) { return JSON.parse(JSON.stringify(value)); }
function readdressManifest(artifact) {
  const payload = clone(artifact); delete payload.contentAddress;
  const canonical = Manifest.canonicalStringify(payload);
  payload.contentAddress = { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest: crypto.createHash("sha256").update(canonical, "utf8").digest("hex"), canonicalBytes: Buffer.byteLength(canonical, "utf8") };
  return payload;
}
function assertRehashedMutationRejected(mutator) {
  const artifact = Manifest.buildManifest(); mutator(artifact); assert.strictEqual(Manifest.validateManifest(readdressManifest(artifact)).valid, false);
}

test("the committed manifest is exact semantic regeneration of u2-decision-v2", function () {
  const committed = JSON.parse(fs.readFileSync(U2.MANIFEST_PATH, "utf8")), expected = Manifest.buildManifest();
  assert.strictEqual(Manifest.validateManifest(committed).valid, true);
  assert.strictEqual(Manifest.canonicalStringify(committed), Manifest.canonicalStringify(expected));
  assert.strictEqual(committed.contentAddress.digest, U2.MANIFEST_DIGEST);
  assert.strictEqual(committed.protocolAdoption.protocols.decisionContract.id, "u2-decision-v2");
});

test("fresh content address cannot bless amended rho", function () { assertRehashedMutationRejected(function (artifact) { artifact.commonGrids.rho[2] = 0.051; }); });
test("fresh content address cannot bless a smaller resource row", function () { assertRehashedMutationRejected(function (artifact) { artifact.resourcePolicy.rows[23].predictedVertices -= 1; }); });
test("fresh content address cannot bless a substituted primary control", function () { assertRehashedMutationRejected(function (artifact) { artifact.matrix.primaryControls[0].id = "heavy-tail-conductance"; }); });
test("fresh content address cannot bless a downgraded RNG", function () { assertRehashedMutationRejected(function (artifact) { artifact.sourcePolicy.batchRandomness.id = "gg-fnv1a32-mulberry32-v1"; }); });
test("fresh content address cannot bless an altered protocol digest", function () { assertRehashedMutationRejected(function (artifact) { artifact.protocolAdoption.protocols.decisionContract.sha256 = "0".repeat(64); }); });
test("fresh content address cannot bless an unknown semantic field", function () { assertRehashedMutationRejected(function (artifact) { artifact.gates.postHocEscape = true; }); });

test("run identity seed mutation is rejected independently of content addressing", function () {
  const key = { experimentId: "ggii-u2-v2", namespace: "confirm/", familyId: "triangular-clipped", parameterCell: { sigma: 0.75 }, linearSize: 81, replicate: 7 }, seeds = {};
  U2.STREAMS.forEach(function (stream) { seeds[stream] = U2.deriveStreamSeed("confirm", key.familyId, key.parameterCell.sigma, key.linearSize, key.replicate, stream); });
  const record = { runKey: key, runId: U2.sha256({ schema: U2.RUN_SCHEMA, runKey: key }), seeds: seeds };
  assert.strictEqual(U2.validateRunIdentityRecord(record).valid, true);
  record.seeds.roots = record.seeds.generator;
  assert.strictEqual(U2.validateRunIdentityRecord(record).valid, false);
});

test("Gate 7 cannot be promoted from incomplete controls", function () {
  const exact = { status: "PASS" }, controls = { summaries: U2.PRIMARY_CONTROLS.map(function (id) { return { id: id, countsForGate7: false }; }) }, cells = [], gates = U2.deriveGates(exact, cells, controls, "NOT_RUN"), conclusion = U2.deriveConclusion(gates);
  assert.strictEqual(gates.find(function (gate) { return gate.gate === 7; }).status, "UNRESOLVED");
  const ledger = { exactGateOne: exact, cells: cells, primaryControls: controls, crossPlatformStatus: "NOT_RUN", gateResults: clone(gates), conclusion: clone(conclusion) };
  ledger.gateResults.find(function (gate) { return gate.gate === 7; }).status = "PASS";
  assert.strictEqual(U2.validateDecisionLedger(ledger).valid, false);
});

test("global status and conclusion cannot be promoted independently", function () {
  const exact = { status: "PASS" }, controls = { summaries: U2.PRIMARY_CONTROLS.map(function (id) { return { id: id, countsForGate7: false }; }) }, cells = [], gates = U2.deriveGates(exact, cells, controls, "NOT_RUN"), conclusion = U2.deriveConclusion(gates), ledger = { exactGateOne: exact, cells: cells, primaryControls: controls, crossPlatformStatus: "NOT_RUN", gateResults: gates, conclusion: conclusion };
  assert.strictEqual(U2.validateDecisionLedger(ledger).valid, true);
  ledger.conclusion = clone(conclusion); ledger.conclusion.status = "REJECTED"; ledger.conclusion.rejectionClaimed = true;
  assert.strictEqual(U2.validateDecisionLedger(ledger).valid, false);
});

test("construction contract serializes every control rounding and fallback", function () {
  assert.strictEqual(U2.CONSTRUCTION_CONTRACT.id, "ggii-u2-v2-batch-construction/1");
  assert.match(U2.CONSTRUCTION_CONTRACT.controls["small-world-shortcuts"].fallback, /INVALID_COMPLEX/);
  assert.match(U2.CONSTRUCTION_CONTRACT.controls["perforated-disk"].fallback, /INVALID_COMPLEX/);
  assert.match(U2.CONSTRUCTION_CONTRACT.finiteRootAndWalkerScope, /never a coverage/);
});

if (!process.exitCode) process.stdout.write("Global Geometry II U2 adversarial: " + passed + "/" + passed + " tests passed.\n");
