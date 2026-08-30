#!/usr/bin/env node
"use strict";

/* Independent outcome-review mutations. This file never runs the production matrix. */
const assert = require("assert");
const childProcess = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");
const Manifest = require("./generate-global-geometry-ii-u2-manifest.js");
const U2 = require("./global-geometry-ii-u2.js");
const CLI = require("./generate-global-geometry-ii-u2.js");
const SourceBoundary = require("./global-geometry-ii-u2-source-boundary.js");

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
function currentCommit() {
  return childProcess.execFileSync("git", ["rev-parse", "HEAD^{commit}"], { cwd: SourceBoundary.ROOT, encoding: "utf8" }).trim();
}
function readdressBoundary(artifact) {
  const payload = clone(artifact); delete payload.contentAddress;
  return Object.assign({}, payload, { contentAddress: SourceBoundary.contentAddress(payload) });
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

test("source boundary binds the actual commit tree and all thirteen committed source blobs", function () {
  const commit = currentCommit(), boundary = SourceBoundary.buildSourceBoundary(commit);
  assert.strictEqual(boundary.sourceCommit, commit);
  assert.strictEqual(boundary.files.length, 13);
  assert.strictEqual(new Set(boundary.files.map(function (entry) { return entry.path; })).size, 13);
  assert.strictEqual(SourceBoundary.validateSourceBoundary(boundary).valid, true);
});

test("dirty relevant local bytes cannot enter a source boundary", function () {
  const target = path.join(SourceBoundary.ROOT, "website/global-geometry-lab/global-geometry-ii-u2.js");
  assert.throws(function () {
    SourceBoundary.buildSourceBoundary(currentCommit(), {
      readFile: function (candidate) {
        const bytes = fs.readFileSync(candidate);
        return candidate === target ? Buffer.concat([bytes, Buffer.from("\n// adversarial dirty byte\n", "utf8")]) : bytes;
      }
    });
  }, /local bytes differ/);
});

test("tree, file, path, and content-address mutations fail source-boundary replay", function () {
  const boundary = SourceBoundary.buildSourceBoundary(currentCommit());

  const treeMutation = clone(boundary);
  treeMutation.sourceTree = "0".repeat(40);
  assert.strictEqual(SourceBoundary.validateSourceBoundary(readdressBoundary(treeMutation)).valid, false);

  const fileMutation = clone(boundary);
  fileMutation.files[0].sha256 = "0".repeat(64);
  assert.strictEqual(SourceBoundary.validateSourceBoundary(readdressBoundary(fileMutation)).valid, false);

  const pathMutation = clone(boundary);
  pathMutation.files[0].path = "GLOBAL_GEOMETRY_II_EVALUATION_REPAIR_AUDIT-copy.md";
  assert.strictEqual(SourceBoundary.validateSourceBoundary(readdressBoundary(pathMutation)).valid, false);

  const addressMutation = clone(boundary);
  addressMutation.contentAddress.digest = "0".repeat(64);
  assert.strictEqual(SourceBoundary.validateSourceBoundary(addressMutation).valid, false);
});

test("a substituted source boundary or calibration payload is rejected after fresh readdressing", function () {
  const commit = currentCommit(), boundary = SourceBoundary.buildSourceBoundary(commit);
  const calibration = U2.calibrationRecord(U2.loadManifest(), commit, boundary);
  assert.strictEqual(U2.validateCalibration(calibration).valid, true);

  const boundarySubstitution = clone(calibration);
  boundarySubstitution.sourceBoundary.sourceTree = "f".repeat(40);
  boundarySubstitution.sourceBoundary = readdressBoundary(boundarySubstitution.sourceBoundary);
  delete boundarySubstitution.contentAddress;
  boundarySubstitution.contentAddress = U2.contentAddress(boundarySubstitution);
  assert.strictEqual(U2.validateCalibration(boundarySubstitution).valid, false);

  const calibrationSubstitution = clone(calibration);
  calibrationSubstitution.cells[0].normalization.bulkDensity += 0.125;
  delete calibrationSubstitution.contentAddress;
  calibrationSubstitution.contentAddress = U2.contentAddress(calibrationSubstitution);
  assert.strictEqual(U2.validateCalibration(calibrationSubstitution).valid, false);
});

test("independent overwrite mutation leaves the first artifact bytes unchanged", function () {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-u2-adversarial-overwrite-"));
  const output = path.join(directory, "artifact.json");
  try {
    CLI.writeArtifact(output, { immutable: "first" });
    const before = fs.readFileSync(output);
    assert.throws(function () { CLI.writeArtifact(output, { immutable: "second" }); }, /EEXIST/);
    assert.throws(function () { CLI.requireUnusedOutput(output); }, /overwrite is forbidden/);
    assert.deepStrictEqual(fs.readFileSync(output), before);
  } finally {
    fs.rmSync(directory, { recursive: true });
  }
});

if (!process.exitCode) process.stdout.write("Global Geometry II U2 adversarial: " + passed + "/" + passed + " tests passed.\n");
