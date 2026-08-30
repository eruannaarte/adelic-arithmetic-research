#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");
const Screening = require("./global-geometry-ii-u2-screening-v2.js");
const Runner = require("./run-global-geometry-ii-u2-screening-v2.js");
const Supplement = require("./generate-global-geometry-ii-u2-screening-supplement-v3.js");
const Boundary = require("./generate-global-geometry-ii-u2-screening-source-boundary-v2.js");

let passed = 0;
function test(name, fn) {
  try { fn(); passed += 1; process.stdout.write("PASS " + name + "\n"); }
  catch (error) { process.stderr.write("FAIL " + name + "\n" + error.stack + "\n"); process.exitCode = 1; }
}

function address(payload) {
  return { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest: Screening.sha256JSON(payload), canonicalBytes: Buffer.byteLength(Screening.canonicalStringify(payload), "utf8") };
}

function sourceFixture() {
  const payload = {
    schema: "gg.u2.screening.source-boundary/2",
    boundaryId: "ggii-u2-screening-v2-source-boundary",
    sourceCommit: "a".repeat(40),
    sourceTree: "b".repeat(40),
    activeSupplementDigest: Screening.SUPPLEMENT_DIGEST,
    verificationModes: { git: "test", portable: "test" },
    files: Boundary.REQUIRED_FILES.map(function (entry) {
      const bytes = fs.readFileSync(path.join(Screening.ROOT, entry.path));
      return { path: entry.path, role: entry.role, bytes: bytes.length, sha256: Screening.sha256Bytes(bytes) };
    })
  };
  const artifact = Object.assign({}, payload, { contentAddress: address(payload) }), bytes = Boundary.serializeArtifact(artifact);
  return { artifact: artifact, bytes: bytes, pins: { fileSha256: Screening.sha256Bytes(bytes), semanticSha256: artifact.contentAddress.digest } };
}

function sourceBindingFixture() {
  const fixture = sourceFixture();
  return Screening.sourceBinding(fixture.bytes, "portable", fixture.pins, null, "fixture/source-boundary-v2.json");
}

test("v3 supplement, repair audit, and aborted-pilot metadata are exactly bound", function () {
  const loaded = Screening.loadPrerequisites(), artifact = JSON.parse(fs.readFileSync(path.join(Screening.ROOT, "artifacts/global-geometry-ii/u2/screening/screening-implementation-supplement-v3.json"), "utf8"));
  assert.deepStrictEqual(artifact, Supplement.buildSupplement());
  assert.strictEqual(Supplement.validateSupplement(artifact).valid, true);
  assert.strictEqual(loaded.supplement.contentAddress.digest, Screening.SUPPLEMENT_DIGEST);
  assert.strictEqual(loaded.repairAudit.sha256, Screening.REPAIR_AUDIT_SHA256);
  assert.strictEqual(loaded.repairAudit.commit, Screening.REPAIR_AUDIT_COMMIT);
  assert.strictEqual(loaded.pilotAbort.partialArtifact.recordLineCount, 3589);
  assert.strictEqual(loaded.pilotAbort.audit.inferentialUse, "PROHIBITED");
});

test("independence accounting separates carriers, conductances, nested batches, and repeats", function () {
  assert.deepStrictEqual(Screening.independenceForPositive("square-alternating", 0), {
    carrierConstructionRealizationCount: 1, conductanceRealizationCount: 1, jointWeightedRealizationCount: 1,
    randomizedNestedMeasurementBatchCount: 32, repeatedDeterministicEvaluationCount: 0, measurementBatchCount: 32,
    label: "one deterministic carrier and one deterministic conductance field with 32 randomized nested measurement batches; not 32 independent geometries"
  });
  const positive = Screening.independenceForPositive("cell-center-fan", 2);
  assert.strictEqual(positive.carrierConstructionRealizationCount, 1);
  assert.strictEqual(positive.conductanceRealizationCount, 32);
  assert.strictEqual(positive.jointWeightedRealizationCount, 32);
  const hashed = Screening.independenceForPositive("square-hashed-diagonal", 0);
  assert.deepStrictEqual([hashed.carrierConstructionRealizationCount, hashed.conductanceRealizationCount, hashed.jointWeightedRealizationCount], [32, 1, 32]);
  const neck = Screening.independenceForControl("vanishing-neck");
  assert.deepStrictEqual([neck.randomizedNestedMeasurementBatchCount, neck.repeatedDeterministicEvaluationCount, neck.measurementBatchCount], [0, 31, 32]);
});

test("record v2 is deterministic and replay compares the full supplied canonical record", function () {
  const identity = Screening.Base.expectedCensus()[0], first = Screening.buildRecord(identity), second = Screening.buildRecord(identity);
  assert.deepStrictEqual(first, second);
  assert.strictEqual(Screening.validateRecord(first, identity).valid, true);
  assert.strictEqual(Screening.replayRecord(first).valid, true);
  const tampered = JSON.parse(JSON.stringify(first)); tampered.volumeGrowthScreen.logLogSlopeDescriptor += 0.125;
  const payload = JSON.parse(JSON.stringify(tampered)); delete payload.recordHash; tampered.recordHash = Screening.sha256JSON(payload);
  assert.strictEqual(Screening.replayRecord(tampered).valid, false);
  assert.strictEqual(Screening.validateRecord(tampered, identity).valid, false);
});

test("canonical JSONL has exact line bytes and exactly one terminal LF", function () {
  const records = Screening.Base.expectedCensus().slice(0, 2).map(Screening.buildRecord), bytes = Screening.serializeCanonicalJsonl(records), report = Screening.parseCanonicalJsonl(bytes, { expectedCount: 2 });
  assert.strictEqual(report.valid, true, report.errors.join("; "));
  assert.strictEqual(bytes[bytes.length - 1], 10);
  assert.notStrictEqual(bytes[bytes.length - 2], 10);
  assert.strictEqual(Screening.parseCanonicalJsonl(bytes.subarray(0, bytes.length - 1)).valid, false);
  assert.strictEqual(Screening.parseCanonicalJsonl(Buffer.concat([bytes, Buffer.from("\n")])).valid, false);
  assert.strictEqual(Screening.parseCanonicalJsonl(Buffer.from(bytes.toString("utf8").replace("\n", "\r\n"))).valid, false);
});

test("chunk certificate binds exact canonical bytes, census, Merkle root, and source", function () {
  const source = sourceBindingFixture(), records = Screening.Base.expectedCensus().slice(0, 32).map(Screening.buildRecord), bytes = Screening.serializeCanonicalJsonl(records), chunkPath = "fixture/chunk-0000.jsonl";
  const certificate = Screening.buildChunkCertificate(0, records, bytes, chunkPath, source), certificateBytes = Screening.serializeJsonArtifact(certificate), report = Screening.validateChunk(bytes, certificateBytes, 0, chunkPath, source, { remeasure: true });
  assert.strictEqual(report.valid, true, report.errors.join("; "));
  assert.strictEqual(certificate.recordCount, 32);
  assert.strictEqual(certificate.chunk.sha256, Screening.sha256Bytes(bytes));
  assert.strictEqual(Screening.validateChunk(Buffer.concat([bytes.subarray(0, bytes.length - 2), Buffer.from(" \n")]), certificateBytes, 0, chunkPath, source).valid, false);
});

test("portable source boundary is externally pinned and validates without Git", function () {
  const fixture = sourceFixture(), report = Boundary.verifyBoundaryBytes(fixture.bytes, "portable", fixture.pins);
  assert.strictEqual(report.valid, true, report.errors.join("; "));
  assert.strictEqual(report.artifact.sourceCommit, "a".repeat(40));
  assert.strictEqual(Boundary.verifyBoundaryBytes(fixture.bytes, "portable", { fileSha256: "0".repeat(64), semanticSha256: fixture.pins.semanticSha256 }).valid, false);
  assert.throws(function () { Boundary.buildBoundary("abc1234"); }, /full lowercase 40-hex/);
});

test("durable writer creates one fsynced hard-link result and never overwrites", function () {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-screen-v2-write-")), output = path.join(directory, "artifact.bin"), bytes = Buffer.from("immutable\n");
  assert.strictEqual(Runner.durableWriteNoReplace(output, bytes), "CREATED_EXCLUSIVE_FSYNC");
  assert.deepStrictEqual(fs.readFileSync(output), bytes);
  assert.throws(function () { Runner.durableWriteNoReplace(output, bytes); }, /overwrite/);
});

test("exclusive run lock is owned, collision-refusing, and explicitly released", function () {
  const fixture = sourceBindingFixture(), directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-screen-v2-lock-")), paths = { directory: directory };
  const lock = Runner.acquireRunLock(paths, "test", fixture, "resume");
  assert.strictEqual(fs.existsSync(lock.path), true);
  assert.throws(function () { Runner.acquireRunLock(paths, "test", fixture, "resume"); }, /definitive dead-PID proof/);
  assert.strictEqual(Runner.releaseRunLock(lock), "RELEASED_OWNED_LOCK");
  assert.strictEqual(fs.existsSync(lock.path), false);
});

test("portable mode is allowed only when the Git executable is unavailable", function () {
  assert.throws(function () { Runner.assertSourceModePolicy("portable", function () { return true; }); }, /Git is available/);
  assert.deepStrictEqual(Runner.assertSourceModePolicy("portable", function () { return false; }), { gitExecutableAvailable: false, selectedMode: "portable" });
  assert.deepStrictEqual(Runner.assertSourceModePolicy("git", function () { return true; }), { gitExecutableAvailable: true, selectedMode: "git" });
});

test("control declaredParametersRealized exactly follows absence of control-shortfall", function () {
  const identity = Screening.Base.expectedCensus().find(function (row) { return row.kind === "control" && row.id === "small-world-shortcuts"; }), record = Screening.buildRecord(identity);
  const hasShortfall = record.failures.some(function (failure) { return failure.channel === "control-shortfall"; });
  assert.strictEqual(record.construction.declaredParametersRealized, !hasShortfall);
  assert.strictEqual(Screening.validateRecord(record, identity).valid, true);
});

test("runtime certificate validates exact source, raw, summary, and checkpoint bindings", function () {
  const source = sourceBindingFixture(), rawBytes = Buffer.from("{}\n"), summary = { contentAddress: { digest: "1".repeat(64) } }, summaryBytes = Buffer.from("summary\n"), checkpoint = { contentAddress: { digest: "2".repeat(64) } }, checkpointBytes = Buffer.from("checkpoint\n");
  const context = { platformLabel: "test", source: source, rawPath: "raw", rawBytes: rawBytes, summaryPath: "summary", summaryBytes: summaryBytes, summary: summary, checkpointPath: "checkpoint", checkpointBytes: checkpointBytes, checkpoint: checkpoint };
  const runtime = Runner.buildRuntimeCertificate(context, { elapsedMilliseconds: 1 }), bytes = Screening.serializeJsonArtifact(runtime), report = Runner.validateRuntimeBytes(bytes, context);
  assert.strictEqual(report.valid, true, report.errors.join("; "));
  assert.strictEqual(runtime.artifacts.raw.sha256, Screening.sha256Bytes(rawBytes));
});

test("JSON summary artifacts require their exact frozen pretty serialization bytes", function () {
  const summaryLike = { schema: "gg.u2.screening.summary/2", outcome: { u2Status: "UNRESOLVED" } }, exact = Screening.serializeJsonArtifact(summaryLike), compact = Buffer.from(JSON.stringify(summaryLike) + "\n");
  assert.strictEqual(Screening.validateJsonArtifactBytes(exact).valid, true);
  assert.strictEqual(Screening.validateJsonArtifactBytes(compact).valid, false);
  assert.strictEqual(Screening.validateJsonArtifactBytes(Buffer.concat([exact, Buffer.from("\n")])).valid, false);
});

test("CLI requires explicit source mode and both immutable boundary pins", function () {
  assert.throws(function () { Runner.parseArgs([]); }, /source-mode/);
  const options = Runner.parseArgs(["--source-mode", "portable", "--source-boundary-file-sha256", "a".repeat(64), "--source-boundary-semantic-sha256", "b".repeat(64)]);
  assert.strictEqual(options.sourceMode, "portable");
  assert.strictEqual(options.sourceBoundaryFileSha256, "a".repeat(64));
});

if (!process.exitCode) process.stdout.write("Global Geometry II U2 screening v2: " + passed + "/" + passed + " tests passed.\n");
