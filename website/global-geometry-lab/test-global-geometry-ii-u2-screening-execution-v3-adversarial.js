#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");
const V3 = require("./global-geometry-ii-u2-screening-execution-v3.js");
const Runner = require("./run-global-geometry-ii-u2-screening-execution-v3.js");
const Boundary = require("./generate-global-geometry-ii-u2-screening-source-boundary-v3.js");

let passed = 0;
function test(name, fn) { try { fn(); passed += 1; process.stdout.write("PASS " + name + "\n"); } catch (error) { process.stderr.write("FAIL " + name + "\n" + error.stack + "\n"); process.exitCode = 1; } }
function readdress(artifact) { const payload = V3.clone(artifact); delete payload.contentAddress; return Object.assign({}, payload, { contentAddress: V3.contentAddress(payload) }); }
function sourceFixture() {
  const files = Boundary.REQUIRED_FILES.map(function (entry) { const bytes = fs.readFileSync(path.join(V3.ROOT, entry.path)); return { path: entry.path, role: entry.role, bytes: bytes.length, sha256: V3.sha256Bytes(bytes) }; });
  const payload = { schema: "gg.u2.screening.source-boundary/3", boundaryId: "ggii-u2-screening-execution-v3-source-boundary", sourceCommit: "a".repeat(40), sourceTree: "b".repeat(40), semanticBaseCommit: "1c3373267057b8a018ad5039e0f3b2b4e8eb2b1d", semanticBaseBoundaryCommit: "ed624f4ff42b4e5488a1889c3d55ba1195e5a952", activeSupplementDigest: V3.SUPPLEMENT_DIGEST, semanticPayloadVersion: "screening-v3", executionVersion: "screening-v3", verificationModes: { git: "fixture", portable: "fixture" }, files: files };
  const artifact = Object.assign({}, payload, { contentAddress: V3.contentAddress(payload) }), bytes = Boundary.serializeArtifact(artifact), pins = { fileSha256: V3.sha256Bytes(bytes), semanticSha256: artifact.contentAddress.digest }, source = V3.sourceBinding(bytes, "portable", pins, null, "fixture/source-boundary-v3.json");
  return { artifact: artifact, bytes: bytes, pins: pins, source: source };
}
function pathsIn(directory) { return { directory: directory, chunks: path.join(directory, "chunks"), raw: path.join(directory, "screening-raw-v3.jsonl"), summary: path.join(directory, "screening-summary-envelope-v3.json"), runtime: path.join(directory, "screening-runtime-v3.json"), checkpointManifest: path.join(directory, "screening-checkpoint-manifest-v3.json"), writerCapability: path.join(directory, "writer-capability-v3.json") }; }

test("freshly rehashed semantic-adapter mutation still fails fresh v3 rebuild", function () {
  const identity = V3.Semantic.Base.expectedCensus().find(function (row) { return row.kind === "control" && row.id === "small-world-shortcuts" && row.size === 54; }), record = V3.buildRecord(identity), changed = V3.clone(record);
  changed.controlDiscriminant.targetShortcutCount += 1; delete changed.recordHash; changed.recordHash = V3.sha256JSON(changed);
  assert.strictEqual(V3.validateRecord(changed, identity, { remeasure: true }).valid, false);
});

test("adapter never erases a genuine small-world shortfall", function () {
  const identity = V3.Semantic.Base.expectedCensus().find(function (row) { return row.kind === "control" && row.id === "small-world-shortcuts" && row.size === 54; }), base = V3.clone(V3.Semantic.buildRecord(identity));
  delete base.recordHash; base.controlDiscriminant.acceptedShortcutCount = base.construction.metadata.targetShortcutCount - 1;
  V3.adaptSmallWorldLedger(base);
  assert.strictEqual(base.controlDiscriminant.targetShortcutCount, base.construction.metadata.targetShortcutCount);
  assert.strictEqual(base.failures.some(function (failure) { return failure.channel === "control-shortfall"; }), true);
  assert.strictEqual(base.construction.declaredParametersRealized, false);
});

test("writer refuses target overwrite, temporary collision, and hard-link collision", function () {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-v3-collisions-")), output = path.join(directory, "artifact.bin"), bytes = Buffer.from("one\n");
  Runner.durableWriteNoReplace(output, bytes);
  assert.throws(function () { Runner.durableWriteNoReplace(output, bytes); }, /overwrite/);
  const other = path.join(directory, "other.bin"); fs.writeFileSync(other + ".v3-exclusive-temp", "occupied");
  assert.throws(function () { Runner.durableWriteNoReplace(other, bytes); }, /temporary-file collision/);
  const raced = path.join(directory, "raced.bin"), sentinel = Buffer.from("collision-winner\n");
  assert.throws(function () {
    Runner.durableWriteNoReplace(raced, bytes, { linkSync: function (source, target) { fs.writeFileSync(target, sentinel, { flag: "wx" }); fs.linkSync(source, target); } });
  }, function (error) { return error && error.code === "EEXIST"; });
  assert.deepStrictEqual(fs.readFileSync(raced), sentinel);
  assert.strictEqual(fs.existsSync(raced + ".v3-exclusive-temp"), false);
  assert.deepStrictEqual(fs.readFileSync(output), bytes);
});

test("writer actually opens both temporary and final files with writable modes", function () {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-v3-open-modes-")), output = path.join(directory, "artifact.bin"), modes = [], open = fs.openSync;
  Runner.durableWriteNoReplace(output, Buffer.from("modes\n"), { openSync: function (target, mode) { modes.push([target, mode]); return open(target, mode); } });
  assert.ok(modes.some(function (row) { return row[1] === "wx+"; }));
  assert.ok(modes.some(function (row) { return row[0] === output && row[1] === "r+"; }));
});

test("writer detects exact postflight mutation and leaves fail-closed evidence", function () {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-v3-postflight-")), output = path.join(directory, "artifact.bin"), bytes = Buffer.from("expected\n"), read = fs.readFileSync;
  assert.throws(function () { Runner.durableWriteNoReplace(output, bytes, { readFileSync: function (target) { const observed = read(target); return target === output ? Buffer.concat([observed, Buffer.from("x")]) : observed; } }); }, /postflight mismatch/);
  assert.strictEqual(fs.existsSync(output), true);
  assert.deepStrictEqual(fs.readFileSync(output), bytes);
  assert.throws(function () { Runner.durableWriteNoReplace(output, bytes); }, /overwrite/);
});

test("resume discovery refuses orphan, gap, unknown, and mutated v3 checkpoints", function () {
  const fixture = sourceFixture();
  const orphan = pathsIn(fs.mkdtempSync(path.join(os.tmpdir(), "ggii-v3-orphan-"))); fs.mkdirSync(orphan.chunks); fs.writeFileSync(path.join(orphan.chunks, "chunk-0000.jsonl"), "x\n");
  assert.throws(function () { Runner.discoverChunks(orphan, fixture.source, { remeasure: false }); }, /orphan/);
  const gap = pathsIn(fs.mkdtempSync(path.join(os.tmpdir(), "ggii-v3-gap-"))); fs.mkdirSync(gap.chunks); const gapEntry = Runner.createChunk(gap, 1, fixture.source);
  assert.throws(function () { Runner.discoverChunks(gap, fixture.source, { remeasure: false }); }, /gap/);
  const unknown = pathsIn(fs.mkdtempSync(path.join(os.tmpdir(), "ggii-v3-unknown-"))); fs.mkdirSync(unknown.chunks); fs.writeFileSync(path.join(unknown.chunks, "surprise.tmp"), "x");
  assert.throws(function () { Runner.discoverChunks(unknown, fixture.source, { remeasure: false }); }, /unknown/);
  assert.strictEqual(gapEntry.index, 1);
});

test("validated-prefix resume bytes equal uninterrupted v3 construction", function () {
  const fixture = sourceFixture(), paths = pathsIn(fs.mkdtempSync(path.join(os.tmpdir(), "ggii-v3-resume-"))), first = Runner.createChunk(paths, 0, fixture.source), recovered = Runner.discoverChunks(paths, fixture.source, { remeasure: true }), second = Runner.createChunk(paths, 1, fixture.source), resumed = Buffer.concat([recovered.entries[0].chunkBytes, second.chunkBytes]), uninterrupted = V3.Semantic.serializeCanonicalJsonl(V3.Semantic.Base.expectedCensus().slice(0, 64).map(V3.buildRecord));
  assert.strictEqual(recovered.records.length, 32);
  assert.deepStrictEqual(first.chunkBytes, recovered.entries[0].chunkBytes);
  assert.deepStrictEqual(resumed, uninterrupted);
});

test("stale-lock recovery is host-bound, claim-serialized, and archives exact bytes", function () {
  const fixture = sourceFixture(), paths = pathsIn(fs.mkdtempSync(path.join(os.tmpdir(), "ggii-v3-stale-"))), stale = Runner.acquireRunLock(paths, "test", fixture.source, "fresh", { pid: 987654311, startedAt: "2026-08-30T00:00:00.000Z" });
  const resumed = Runner.acquireRunLock(paths, "test", fixture.source, "resume", { pidProbe: function () { return { state: "dead", mechanism: "test", errorCode: "ESRCH" }; } });
  assert.strictEqual(resumed.recovery.staleLockSha256, V3.sha256Bytes(stale.bytes));
  assert.deepStrictEqual(fs.readFileSync(path.resolve(V3.ROOT, resumed.recovery.archivePath)), stale.bytes);
  assert.strictEqual(Runner.releaseRunLock(resumed), "RELEASED_OWNED_RUN_LOCK");
  const remotePaths = pathsIn(fs.mkdtempSync(path.join(os.tmpdir(), "ggii-v3-remote-"))), remote = { hostname: "remote", platform: "win32", arch: "x64" };
  Runner.acquireRunLock(remotePaths, "test", fixture.source, "fresh", { pid: 987654312, hostIdentity: remote });
  assert.throws(function () { Runner.acquireRunLock(remotePaths, "test", fixture.source, "resume", { pidProbe: function () { return { state: "dead", mechanism: "test", errorCode: "ESRCH" }; } }); }, /creator host/);
});

test("writer capability mutation cannot be blessed by a fresh content address", function () {
  const fixture = sourceFixture(), directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-v3-capability-mutation-")), paths = pathsIn(directory), created = Runner.runWriterCapabilityPreflight(paths, "test", fixture.source, { platform: "win32" }), changed = V3.clone(created.artifact);
  changed.observation.collisionRefusals.hardLinkPublication = false;
  const report = Runner.validateWriterCapabilityBytes(V3.serializeJsonArtifact(readdress(changed)), "test", fixture.source);
  assert.strictEqual(report.valid, false);
});

test("portable v3 boundary rejects local mutation and external-pin substitution", function () {
  const fixture = sourceFixture(), changed = V3.clone(fixture.artifact); changed.files[0].sha256 = "0".repeat(64); const changedArtifact = readdress(changed), changedBytes = Boundary.serializeArtifact(changedArtifact), changedPins = { fileSha256: V3.sha256Bytes(changedBytes), semanticSha256: changedArtifact.contentAddress.digest };
  assert.strictEqual(Boundary.verifyBoundaryBytes(changedBytes, "portable", fixture.pins).valid, false);
  assert.strictEqual(Boundary.verifyBoundaryBytes(changedBytes, "portable", changedPins).valid, false);
  assert.strictEqual(Boundary.verifyBoundaryBytes(fixture.bytes, "portable", null).valid, false);
});

test("Git verification failure never falls back to portable v3 verification", function () {
  const fixture = sourceFixture(), report = Boundary.verifyBoundaryBytes(fixture.bytes, "git", fixture.pins, { git: function () { throw new Error("simulated git failure"); } });
  assert.strictEqual(report.valid, false);
  assert.ok(report.errors.some(function (error) { return /without portable fallback/.test(error); }));
});

test("v3 summary envelope rejects a freshly readdressed semantic mutation", function () {
  const fixture = sourceFixture(), records = V3.Semantic.Base.expectedCensus().slice(0, 32).map(V3.buildRecord), raw = V3.Semantic.serializeCanonicalJsonl(records), checkpoint = { path: "fixture/checkpoint-v3.json", bytes: 10, sha256: "1".repeat(64), semanticDigest: "2".repeat(64) }, summary = V3.buildSummaryEnvelope(records, { path: "fixture/raw-v3.jsonl", bytes: raw.length, sha256: V3.sha256Bytes(raw) }, checkpoint, fixture.source), changed = V3.clone(summary);
  changed.semanticSummary.aggregateFailureCounts = {}; const bytes = V3.serializeJsonArtifact(readdress(changed));
  assert.strictEqual(V3.validateSummaryEnvelopeBytes(bytes, records, raw, "fixture/raw-v3.jsonl", checkpoint, fixture.source, { remeasure: false, allowIncompleteCensusForTest: true }).valid, false);
});

if (!process.exitCode) process.stdout.write("Global Geometry II screening-execution-v3 adversarial: " + passed + "/" + passed + " tests passed.\n");
