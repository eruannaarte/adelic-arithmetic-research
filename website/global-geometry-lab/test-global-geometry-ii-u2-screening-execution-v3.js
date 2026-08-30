#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");
const V3 = require("./global-geometry-ii-u2-screening-execution-v3.js");
const Runner = require("./run-global-geometry-ii-u2-screening-execution-v3.js");
const Boundary = require("./generate-global-geometry-ii-u2-screening-source-boundary-v3.js");

let passed = 0;
function test(name, fn) { try { fn(); passed += 1; process.stdout.write("PASS " + name + "\n"); } catch (error) { process.stderr.write("FAIL " + name + "\n" + error.stack + "\n"); process.exitCode = 1; } }

function address(payload) { return { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest: V3.sha256JSON(payload), canonicalBytes: Buffer.byteLength(V3.canonicalStringify(payload), "utf8") }; }
function sourceFixture() {
  const files = Boundary.REQUIRED_FILES.map(function (entry) { const bytes = fs.readFileSync(path.join(V3.ROOT, entry.path)); return { path: entry.path, role: entry.role, bytes: bytes.length, sha256: V3.sha256Bytes(bytes) }; });
  const payload = { schema: "gg.u2.screening.source-boundary/3", boundaryId: "ggii-u2-screening-execution-v3-source-boundary", sourceCommit: "a".repeat(40), sourceTree: "b".repeat(40), semanticBaseCommit: "1c3373267057b8a018ad5039e0f3b2b4e8eb2b1d", semanticBaseBoundaryCommit: "ed624f4ff42b4e5488a1889c3d55ba1195e5a952", activeSupplementDigest: V3.SUPPLEMENT_DIGEST, semanticPayloadVersion: "screening-v3", executionVersion: "screening-v3", verificationModes: { git: "fixture", portable: "fixture" }, files: files };
  const artifact = Object.assign({}, payload, { contentAddress: address(payload) }), bytes = Boundary.serializeArtifact(artifact), pins = { fileSha256: V3.sha256Bytes(bytes), semanticSha256: artifact.contentAddress.digest }, source = V3.sourceBinding(bytes, "portable", pins, null, "fixture/source-boundary-v3.json");
  return { artifact: artifact, bytes: bytes, pins: pins, source: source };
}

test("v3 supplement, v2 base, boundary, and Windows abort bindings replay exactly", function () {
  const prerequisites = V3.loadPrerequisites();
  assert.strictEqual(prerequisites.supplement.contentAddress.digest, V3.SUPPLEMENT_DIGEST);
  assert.strictEqual(prerequisites.semanticKernel.semanticBaseVersion, "screening-v2");
  assert.strictEqual(prerequisites.windowsV2Abort.semanticDigest, "50108bc66bf8807772f9fef21baa35eea3e178e621de1958a9b7ddaef7ad6865");
});

test("small-world no-bulk-root ledger repair is exact across every affected registered record", function () {
  const identities = V3.Semantic.Base.expectedCensus().filter(function (identity) { return identity.kind === "control" && identity.id === "small-world-shortcuts"; }); let affected = 0;
  identities.forEach(function (identity) {
    const base = V3.Semantic.buildRecord(identity), record = V3.buildRecord(identity), noBulk = base.controlDiscriminant.targetShortcutCount === undefined;
    if (noBulk) {
      affected += 1;
      assert.strictEqual(record.controlDiscriminant.targetShortcutCount, record.construction.metadata.targetShortcutCount);
      assert.strictEqual(record.controlDiscriminant.acceptedShortcutCount, record.controlDiscriminant.targetShortcutCount);
      assert.strictEqual(record.failures.some(function (failure) { return failure.channel === "control-shortfall"; }), false);
      assert.strictEqual(record.construction.declaredParametersRealized, true);
    } else {
      assert.strictEqual(record.controlDiscriminant.targetShortcutCount, base.controlDiscriminant.targetShortcutCount);
    }
    assert.strictEqual(V3.validateRecord(record, identity).valid, true);
  });
  assert.strictEqual(affected, 103);
});

test("v3 record construction is deterministic, fail-closed, and independently hashed", function () {
  const identity = V3.Semantic.Base.expectedCensus()[0], first = V3.buildRecord(identity), second = V3.buildRecord(identity), payload = V3.clone(first), hash = payload.recordHash; delete payload.recordHash;
  assert.deepStrictEqual(first, second);
  assert.strictEqual(first.schema, "gg.u2.screening.record/3");
  assert.strictEqual(first.semanticBase.semanticBaseVersion, "screening-v2");
  assert.strictEqual(hash, V3.sha256JSON(payload));
  assert.strictEqual(first.screenInterpretation.u2Status, "UNRESOLVED");
  assert.strictEqual(first.screenInterpretation.decisionAuthority, "NONE");
});

test("v3 chunks contain exact canonical record/3 bytes and deterministic certificate/3 metadata", function () {
  const fixture = sourceFixture(), records = V3.Semantic.Base.expectedCensus().slice(0, 32).map(V3.buildRecord), bytes = V3.Semantic.serializeCanonicalJsonl(records), chunkPath = "fixture/chunk-0000.jsonl", certificate = V3.buildChunkCertificate(0, records, bytes, chunkPath, fixture.source), certificateBytes = V3.serializeJsonArtifact(certificate), report = V3.validateChunk(bytes, certificateBytes, 0, chunkPath, fixture.source, { remeasure: true });
  assert.strictEqual(report.valid, true, report.errors.join("; "));
  assert.strictEqual(certificate.schema, "gg.u2.screening.chunk-certificate/3");
  assert.strictEqual(certificate.semanticPayloadVersion, "screening-v3");
  assert.strictEqual(certificate.chunk.sha256, V3.sha256Bytes(bytes));
});

test("portable writer uses writable handles, exact postflight, and POSIX directory barriers", function () {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-v3-writer-")), output = path.join(directory, "artifact.bin"), bytes = Buffer.from("portable-v3\n"), disposition = Runner.durableWriteNoReplace(output, bytes);
  assert.deepStrictEqual(fs.readFileSync(output), bytes);
  assert.strictEqual(disposition.temporaryHandleMode, "wx+");
  assert.strictEqual(disposition.finalHandleMode, "r+");
  assert.strictEqual(disposition.exactBytePostflight, true);
  assert.strictEqual(disposition.directoryAfterLink.status, process.platform === "win32" ? "DIRECTORY_BARRIER_UNAVAILABLE_WIN32" : "DIRECTORY_FSYNC_COMPLETED");
});

test("win32 writer capability explicitly records the unavailable directory barrier", function () {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-v3-win-writer-")), output = path.join(directory, "artifact.bin"), bytes = Buffer.from("win32-policy\n"), disposition = Runner.durableWriteNoReplace(output, bytes, { platform: "win32" });
  assert.strictEqual(disposition.directoryAfterLink.status, "DIRECTORY_BARRIER_UNAVAILABLE_WIN32");
  assert.strictEqual(disposition.directoryAfterTempUnlink.status, "DIRECTORY_BARRIER_UNAVAILABLE_WIN32");
  assert.deepStrictEqual(fs.readFileSync(output), bytes);
});

test("writer preflight certificate is source-bound, content-addressed, and before record zero", function () {
  const fixture = sourceFixture(), directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-v3-capability-")), paths = { directory: directory, writerCapability: path.join(directory, "writer-capability-v3.json") }, created = Runner.runWriterCapabilityPreflight(paths, "test", fixture.source), report = Runner.validateWriterCapabilityBytes(created.bytes, "test", fixture.source);
  assert.strictEqual(report.valid, true, report.errors.join("; "));
  assert.strictEqual(created.artifact.interpretation.recordZeroStarted, false);
  assert.strictEqual(created.artifact.interpretation.decisionAuthority, "NONE");
  assert.deepStrictEqual(created.artifact.observation.collisionRefusals, { existingTarget: true, temporaryName: true, hardLinkPublication: true, collisionBytesPreserved: true, temporaryWriterResidueAbsent: true });
});

test("CLI requires explicit source mode and both v3 boundary pins", function () {
  assert.throws(function () { Runner.parseArgs([]); }, /source-mode/);
  const options = Runner.parseArgs(["--source-mode", "portable", "--source-boundary-file-sha256", "a".repeat(64), "--source-boundary-semantic-sha256", "b".repeat(64), "--writer-preflight-only"]);
  assert.strictEqual(options.writerPreflightOnly, true);
  assert.strictEqual(options.sourceMode, "portable");
});

test("exclusive v3 run lock is source-bound and ownership-checked", function () {
  const fixture = sourceFixture(), directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-v3-lock-")), paths = { directory: directory }, lock = Runner.acquireRunLock(paths, "test", fixture.source, "fresh");
  assert.strictEqual(Runner.validateRunLockBytes(lock.bytes, "test", fixture.source).valid, true);
  assert.throws(function () { Runner.acquireRunLock(paths, "test", fixture.source, "fresh"); }, /non-resume/);
  assert.strictEqual(Runner.releaseRunLock(lock), "RELEASED_OWNED_RUN_LOCK");
});

if (!process.exitCode) process.stdout.write("Global Geometry II screening-execution-v3: " + passed + "/" + passed + " tests passed.\n");
