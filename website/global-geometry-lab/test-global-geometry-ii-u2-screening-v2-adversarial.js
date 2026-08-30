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

function readdress(artifact) {
  const payload = JSON.parse(JSON.stringify(artifact)); delete payload.contentAddress;
  return Object.assign({}, payload, { contentAddress: address(payload) });
}

function sourceFixture() {
  const payload = {
    schema: "gg.u2.screening.source-boundary/2", boundaryId: "ggii-u2-screening-v2-source-boundary",
    sourceCommit: "a".repeat(40), sourceTree: "b".repeat(40), activeSupplementDigest: Screening.SUPPLEMENT_DIGEST,
    verificationModes: { git: "test", portable: "test" },
    files: Boundary.REQUIRED_FILES.map(function (entry) { const bytes = fs.readFileSync(path.join(Screening.ROOT, entry.path)); return { path: entry.path, role: entry.role, bytes: bytes.length, sha256: Screening.sha256Bytes(bytes) }; })
  };
  const artifact = Object.assign({}, payload, { contentAddress: address(payload) }), bytes = Boundary.serializeArtifact(artifact), pins = { fileSha256: Screening.sha256Bytes(bytes), semanticSha256: artifact.contentAddress.digest };
  const source = Screening.sourceBinding(bytes, "portable", pins, null, "fixture/source-boundary-v2.json");
  return { payload: payload, artifact: artifact, bytes: bytes, pins: pins, source: source };
}

function chunkFixture(index, source, chunkPath) {
  const start = index * 32, records = Screening.Base.expectedCensus().slice(start, start + 32).map(Screening.buildRecord), chunkBytes = Screening.serializeCanonicalJsonl(records), certificate = Screening.buildChunkCertificate(index, records, chunkBytes, chunkPath, source), certificateBytes = Screening.serializeJsonArtifact(certificate);
  return { records: records, chunkBytes: chunkBytes, certificate: certificate, certificateBytes: certificateBytes };
}

function summaryFixtureRecords() {
  return Screening.Base.expectedCensus().filter(function (identity) {
    return identity.size === 16 && (
      (identity.kind === "positive" && identity.id === "square-alternating" && (identity.sigmaIndex === 0 || identity.sigmaIndex === 1)) ||
      (identity.kind === "positive" && identity.id === "square-hashed-diagonal" && identity.sigmaIndex === 0) ||
      (identity.kind === "control" && identity.id === "vanishing-neck")
    );
  }).map(Screening.buildRecord);
}

test("fresh-hash supplement mutations cannot redirect repair audit or repeat accounting", function () {
  const auditRedirect = Supplement.buildSupplement(); auditRedirect.bindings.governingRepairAudit.sha256 = "0".repeat(64);
  assert.strictEqual(Supplement.validateSupplement(readdress(auditRedirect)).valid, false);
  const repeatInflation = Supplement.buildSupplement(); repeatInflation.independenceAccounting.controls["vanishing-neck"].repeatedDeterministicEvaluationCount = 32;
  assert.strictEqual(Supplement.validateSupplement(readdress(repeatInflation)).valid, false);
});

test("freshly rehashed carrier/conductance conflation fails full record replay", function () {
  const identity = Screening.Base.expectedCensus()[0], record = Screening.buildRecord(identity), tampered = JSON.parse(JSON.stringify(record));
  tampered.independenceAccounting.conductanceRealizationCount = 32;
  const payload = JSON.parse(JSON.stringify(tampered)); delete payload.recordHash; tampered.recordHash = Screening.sha256JSON(payload);
  assert.strictEqual(Screening.validateRecord(tampered, identity).valid, false);
  assert.strictEqual(Screening.replayRecord(tampered).valid, false);
});

test("vanishing-neck is one unique evaluation plus 31 repeats, never 32 randomized nested batches", function () {
  const identity = Screening.Base.expectedCensus().find(function (row) { return row.kind === "control" && row.id === "vanishing-neck"; }), record = Screening.buildRecord(identity);
  assert.deepStrictEqual([record.independenceAccounting.carrierConstructionRealizationCount, record.independenceAccounting.randomizedNestedMeasurementBatchCount, record.independenceAccounting.repeatedDeterministicEvaluationCount, record.independenceAccounting.measurementBatchCount], [1, 0, 31, 32]);
});

test("declaredParametersRealized cannot contradict a control-shortfall ledger", function () {
  const identity = Screening.Base.expectedCensus().find(function (row) { return row.kind === "control" && row.id === "small-world-shortcuts"; }), record = Screening.buildRecord(identity), tampered = JSON.parse(JSON.stringify(record));
  tampered.construction.declaredParametersRealized = !tampered.construction.declaredParametersRealized;
  const payload = JSON.parse(JSON.stringify(tampered)); delete payload.recordHash; tampered.recordHash = Screening.sha256JSON(payload);
  assert.strictEqual(Screening.validateRecord(tampered, identity, { remeasure: false }).valid, false);
});

test("noncanonical, CRLF, missing-LF, and extra-LF JSONL are all rejected", function () {
  const record = Screening.buildRecord(Screening.Base.expectedCensus()[0]), canonical = Screening.serializeCanonicalJsonl([record]);
  assert.strictEqual(Screening.parseCanonicalJsonl(canonical).valid, true);
  assert.strictEqual(Screening.parseCanonicalJsonl(Buffer.from(JSON.stringify(record, null, 2) + "\n")).valid, false);
  assert.strictEqual(Screening.parseCanonicalJsonl(canonical.subarray(0, canonical.length - 1)).valid, false);
  assert.strictEqual(Screening.parseCanonicalJsonl(Buffer.concat([canonical, Buffer.from("\n")])).valid, false);
  assert.strictEqual(Screening.parseCanonicalJsonl(Buffer.from(canonical.toString("utf8").replace("\n", "\r\n"))).valid, false);
});

test("fresh-hash chunk-certificate mutation is exposed by deterministic rebuild", function () {
  const fixture = sourceFixture(), chunk = chunkFixture(0, fixture.source, "fixture/chunk-0000.jsonl"), mutated = JSON.parse(JSON.stringify(chunk.certificate));
  mutated.recordCount = 31;
  const bytes = Screening.serializeJsonArtifact(readdress(mutated));
  assert.strictEqual(Screening.validateChunk(chunk.chunkBytes, bytes, 0, "fixture/chunk-0000.jsonl", fixture.source).valid, false);
});

test("resume discovery refuses orphan chunks, gaps, unknown files, and byte mutation", function () {
  const fixture = sourceFixture();
  function pathsIn(directory) { return { directory: directory, chunks: path.join(directory, "chunks") }; }
  const orphanDir = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-orphan-")), orphanPaths = pathsIn(orphanDir); fs.mkdirSync(orphanPaths.chunks);
  const orphan = chunkFixture(0, fixture.source, path.relative(Screening.ROOT, path.join(orphanPaths.chunks, "chunk-0000.jsonl")).split(path.sep).join("/"));
  fs.writeFileSync(path.join(orphanPaths.chunks, "chunk-0000.jsonl"), orphan.chunkBytes);
  assert.throws(function () { Runner.discoverChunks(orphanPaths, fixture.source, { remeasure: false }); }, /orphan/);

  const gapDir = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-gap-")), gapPaths = pathsIn(gapDir); fs.mkdirSync(gapPaths.chunks);
  const gapChunkPath = path.relative(Screening.ROOT, path.join(gapPaths.chunks, "chunk-0001.jsonl")).split(path.sep).join("/"), gap = chunkFixture(1, fixture.source, gapChunkPath);
  fs.writeFileSync(path.join(gapPaths.chunks, "chunk-0001.jsonl"), gap.chunkBytes); fs.writeFileSync(path.join(gapPaths.chunks, "chunk-0001.certificate.json"), gap.certificateBytes);
  assert.throws(function () { Runner.discoverChunks(gapPaths, fixture.source, { remeasure: false }); }, /gap/);

  const unknownDir = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-unknown-")), unknownPaths = pathsIn(unknownDir); fs.mkdirSync(unknownPaths.chunks); fs.writeFileSync(path.join(unknownPaths.chunks, "surprise.tmp"), "x");
  assert.throws(function () { Runner.discoverChunks(unknownPaths, fixture.source, { remeasure: false }); }, /unknown/);

  const mutationDir = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-mutation-")), mutationPaths = pathsIn(mutationDir); fs.mkdirSync(mutationPaths.chunks);
  const mutationChunkPath = path.relative(Screening.ROOT, path.join(mutationPaths.chunks, "chunk-0000.jsonl")).split(path.sep).join("/"), mutation = chunkFixture(0, fixture.source, mutationChunkPath), changed = Buffer.from(mutation.chunkBytes); changed[10] ^= 1;
  fs.writeFileSync(path.join(mutationPaths.chunks, "chunk-0000.jsonl"), changed); fs.writeFileSync(path.join(mutationPaths.chunks, "chunk-0000.certificate.json"), mutation.certificateBytes);
  assert.throws(function () { Runner.discoverChunks(mutationPaths, fixture.source, { remeasure: false }); }, /validation failed/);
});

test("a hard-crash stale lock with one validated chunk archives audibly and resumes byte-identically", function () {
  const fixture = sourceFixture(), directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-resume-byte-equality-")), paths = { directory: directory, chunks: path.join(directory, "chunks") };
  try {
    const stale = Runner.acquireRunLock(paths, "test", fixture.source, "fresh", { pid: 987654321, startedAt: "2026-08-30T00:00:00.000Z" });
    const first = Runner.createChunk(paths, 0, fixture.source);
    const resumedLock = Runner.acquireRunLock(paths, "test", fixture.source, "resume", {
      pid: process.pid,
      startedAt: "2026-08-30T00:01:00.000Z",
      pidProbe: function (pid) { assert.strictEqual(pid, 987654321); return { state: "dead", mechanism: "test process table", errorCode: "ESRCH" }; }
    });
    assert.strictEqual(resumedLock.recovery.staleLockSha256, Screening.sha256Bytes(stale.bytes));
    const archivedBytes = fs.readFileSync(path.resolve(Screening.ROOT, resumedLock.recovery.archivePath));
    assert.deepStrictEqual(archivedBytes, stale.bytes);
    const recoveryBytes = fs.readFileSync(path.resolve(Screening.ROOT, resumedLock.recovery.certificatePath)), recovery = Screening.validateJsonArtifactBytes(recoveryBytes);
    assert.strictEqual(recovery.valid, true, recovery.errors.join("; "));
    assert.strictEqual(recovery.artifact.schema, "gg.u2.screening.stale-lock-recovery/2");
    assert.strictEqual(recovery.artifact.deathProof.state, "dead");
    assert.strictEqual(recovery.artifact.staleLock.sha256, Screening.sha256Bytes(stale.bytes));
    const recovered = Runner.discoverChunks(paths, fixture.source, { remeasure: true });
    assert.deepStrictEqual([recovered.entries.length, recovered.records.length], [1, 32]);
    const second = Runner.createChunk(paths, 1, fixture.source), resumedBytes = Buffer.concat([recovered.entries[0].chunkBytes, second.chunkBytes]);
    const uninterrupted = Screening.serializeCanonicalJsonl(Screening.Base.expectedCensus().slice(0, 64).map(Screening.buildRecord));
    assert.deepStrictEqual(resumedBytes, uninterrupted);
    assert.deepStrictEqual(first.chunkBytes, recovered.entries[0].chunkBytes);
    assert.throws(function () { Runner.durableWriteNoReplace(path.resolve(Screening.ROOT, resumedLock.recovery.archivePath), stale.bytes); }, /overwrite/);
    assert.strictEqual(Runner.releaseRunLock(resumedLock), "RELEASED_OWNED_LOCK");
  } finally {
    fs.rmSync(directory, { recursive: true });
  }
});

test("stale-lock recovery refuses live, unknown, platform-mismatched, source-mismatched, and non-resume claims", function () {
  const fixture = sourceFixture();
  function makeCase() {
    const directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-stale-refusal-")), paths = { directory: directory };
    Runner.acquireRunLock(paths, "test", fixture.source, "fresh", { pid: 987654320, startedAt: "2026-08-30T00:00:00.000Z" });
    return { directory: directory, paths: paths };
  }
  ["alive", "unknown"].forEach(function (state) {
    const item = makeCase();
    try {
      assert.throws(function () { Runner.acquireRunLock(item.paths, "test", fixture.source, "resume", { pidProbe: function () { return { state: state, mechanism: "test probe", errorCode: state === "unknown" ? "EPERM" : null }; } }); }, /definitive dead-PID proof/);
      assert.strictEqual(fs.existsSync(path.join(item.directory, ".run-lock.json")), true);
      assert.strictEqual(fs.existsSync(path.join(item.directory, ".stale-run-locks")), false);
    } finally { fs.rmSync(item.directory, { recursive: true }); }
  });
  const platform = makeCase();
  try { assert.throws(function () { Runner.acquireRunLock(platform.paths, "other", fixture.source, "resume", { pidProbe: function () { return { state: "dead", mechanism: "test", errorCode: "ESRCH" }; } }); }, /platform mismatch/); }
  finally { fs.rmSync(platform.directory, { recursive: true }); }
  const source = makeCase(), changedSource = JSON.parse(JSON.stringify(fixture.source)); changedSource.semanticDigest = "f".repeat(64);
  try { assert.throws(function () { Runner.acquireRunLock(source.paths, "test", changedSource, "resume", { pidProbe: function () { return { state: "dead", mechanism: "test", errorCode: "ESRCH" }; } }); }, /source-boundary mismatch/); }
  finally { fs.rmSync(source.directory, { recursive: true }); }
  const fresh = makeCase();
  try { assert.throws(function () { Runner.acquireRunLock(fresh.paths, "test", fixture.source, "fresh", { pidProbe: function () { return { state: "dead", mechanism: "test", errorCode: "ESRCH" }; } }); }, /non-resume/); }
  finally { fs.rmSync(fresh.directory, { recursive: true }); }
  const remote = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-stale-remote-host-")), remotePaths = { directory: remote }, remoteHost = { hostname: "remote-host", platform: "remote-platform", arch: "remote-arch" };
  try {
    Runner.acquireRunLock(remotePaths, "test", fixture.source, "fresh", { pid: 987654319, startedAt: "2026-08-30T00:00:00.000Z", hostIdentity: remoteHost });
    let probed = false;
    assert.throws(function () { Runner.acquireRunLock(remotePaths, "test", fixture.source, "resume", { pidProbe: function () { probed = true; return { state: "dead", mechanism: "test", errorCode: "ESRCH" }; } }); }, /creator host does not match/);
    assert.strictEqual(probed, false);
  } finally { fs.rmSync(remote, { recursive: true }); }
});

test("exclusive recovery claim serializes competing resumptions and leaked claims fail closed", function () {
  const fixture = sourceFixture(), directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-recovery-claim-")), paths = { directory: directory };
  try {
    Runner.acquireRunLock(paths, "test", fixture.source, "fresh", { pid: 987654318, startedAt: "2026-08-30T00:00:00.000Z" });
    const claim = Runner.acquireRecoveryClaim(paths, "test", fixture.source, "resume", { pid: process.pid, startedAt: "2026-08-30T00:01:00.000Z" });
    assert.strictEqual(fs.existsSync(claim.path), true);
    assert.throws(function () { Runner.acquireRunLock(paths, "test", fixture.source, "resume", { pidProbe: function () { return { state: "dead", mechanism: "test", errorCode: "ESRCH" }; } }); }, /existing stale-lock recovery claim/);
    assert.strictEqual(fs.existsSync(path.join(directory, ".run-lock.json")), true);
    assert.strictEqual(Runner.releaseRecoveryClaim(claim), "RELEASED_OWNED_RECOVERY_CLAIM");
  } finally { fs.rmSync(directory, { recursive: true }); }
  const failedReplacementDirectory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-recovery-replacement-failure-")), failedPaths = { directory: failedReplacementDirectory };
  try {
    Runner.acquireRunLock(failedPaths, "test", fixture.source, "fresh", { pid: 987654316, startedAt: "2026-08-30T00:00:00.000Z" });
    fs.writeFileSync(path.join(failedReplacementDirectory, ".run-lock.json.exclusive-temp"), "forced replacement collision\n");
    assert.throws(function () { Runner.acquireRunLock(failedPaths, "test", fixture.source, "resume", { pidProbe: function () { return { state: "dead", mechanism: "test", errorCode: "ESRCH" }; } }); }, /temporary-file collision/);
    assert.strictEqual(fs.existsSync(path.join(failedReplacementDirectory, ".run-lock.json")), false);
    assert.strictEqual(fs.existsSync(Runner.recoveryClaimPath(failedPaths)), true);
    assert.throws(function () { Runner.acquireRunLock(failedPaths, "test", fixture.source, "resume", { pidProbe: function () { return { state: "dead", mechanism: "test", errorCode: "ESRCH" }; } }); }, /pending manual audit/);
  } finally { fs.rmSync(failedReplacementDirectory, { recursive: true }); }
});

test("stale-lock recovery refuses archive/certificate collisions and a lock changed during PID probing", function () {
  const fixture = sourceFixture(), dead = function () { return { state: "dead", mechanism: "test", errorCode: "ESRCH" }; };
  function staleCase(prefix) {
    const directory = fs.mkdtempSync(path.join(os.tmpdir(), prefix)), paths = { directory: directory }, stale = Runner.acquireRunLock(paths, "test", fixture.source, "fresh", { pid: 987654317, startedAt: "2026-08-30T00:00:00.000Z" });
    return { directory: directory, paths: paths, stale: stale, locations: Runner.staleLockPaths(paths, stale.bytes) };
  }
  const archiveCollision = staleCase("ggii-stale-archive-collision-");
  try {
    fs.mkdirSync(archiveCollision.locations.directory); fs.writeFileSync(archiveCollision.locations.archive, "wrong archive bytes\n");
    assert.throws(function () { Runner.acquireRunLock(archiveCollision.paths, "test", fixture.source, "resume", { pidProbe: dead }); }, /archive collision/);
    assert.deepStrictEqual(fs.readFileSync(path.join(archiveCollision.directory, ".run-lock.json")), archiveCollision.stale.bytes);
  } finally { fs.rmSync(archiveCollision.directory, { recursive: true }); }
  const certificateCollision = staleCase("ggii-stale-certificate-collision-");
  try {
    fs.mkdirSync(certificateCollision.locations.directory); fs.writeFileSync(certificateCollision.locations.archive, certificateCollision.stale.bytes); fs.writeFileSync(certificateCollision.locations.certificate, "wrong certificate bytes\n");
    assert.throws(function () { Runner.acquireRunLock(certificateCollision.paths, "test", fixture.source, "resume", { pidProbe: dead }); }, /archive collision/);
    assert.deepStrictEqual(fs.readFileSync(path.join(certificateCollision.directory, ".run-lock.json")), certificateCollision.stale.bytes);
  } finally { fs.rmSync(certificateCollision.directory, { recursive: true }); }
  const changed = staleCase("ggii-stale-changed-probe-");
  try {
    const replacement = Runner.buildRunLock("test", fixture.source, "resume", { pid: process.pid, startedAt: "2026-08-30T00:02:00.000Z" });
    assert.throws(function () {
      Runner.acquireRunLock(changed.paths, "test", fixture.source, "resume", { pidProbe: function () { fs.writeFileSync(path.join(changed.directory, ".run-lock.json"), replacement.bytes); return dead(); } });
    }, /changed during recovery/);
    assert.deepStrictEqual(fs.readFileSync(path.join(changed.directory, ".run-lock.json")), replacement.bytes);
    assert.strictEqual(fs.existsSync(changed.locations.archive), true);
    assert.strictEqual(fs.existsSync(Runner.recoveryClaimPath(changed.paths)), true);
  } finally { fs.rmSync(changed.directory, { recursive: true }); }
});

test("summary count semantics and aggregates replay independently of legacy labels", function () {
  const fixture = sourceFixture(), records = summaryFixtureRecords(), raw = Screening.serializeCanonicalJsonl(records), rawBinding = { path: "fixture/raw.jsonl", bytes: raw.length, sha256: Screening.sha256Bytes(raw) };
  const provenance = { sourceBoundary: fixture.source, checkpointManifest: { path: "fixture/checkpoint.json", bytes: 1, sha256: "1".repeat(64), semanticDigest: "2".repeat(64) } };
  const first = Screening.buildSummary(records, rawBinding, provenance), second = Screening.buildSummary(records, rawBinding, provenance);
  assert.deepStrictEqual(first, second);

  const deterministic = first.positiveCells.find(function (cell) { return cell.family === "square-alternating" && cell.size === 16 && cell.sigmaIndex === 0; });
  assert.deepStrictEqual([
    deterministic.independence.carrierConstructionRealizationCount,
    deterministic.independence.conductanceRealizationCount,
    deterministic.independence.jointWeightedRealizationCount,
    deterministic.independence.randomizedNestedMeasurementBatchCount,
    deterministic.uniqueStructureDigestCount,
    deterministic.uniqueWeightDigestCount,
    deterministic.uniqueJointDigestCount
  ], [1, 1, 1, 32, 1, 1, 1]);

  const weighted = first.positiveCells.find(function (cell) { return cell.family === "square-alternating" && cell.size === 16 && cell.sigmaIndex === 1; });
  assert.deepStrictEqual([weighted.independence.carrierConstructionRealizationCount, weighted.independence.conductanceRealizationCount, weighted.independence.jointWeightedRealizationCount], [1, 32, 32]);
  assert.deepStrictEqual([weighted.uniqueStructureDigestCount, weighted.uniqueWeightDigestCount, weighted.uniqueJointDigestCount], [1, 32, 32]);

  const hashed = first.positiveCells.find(function (cell) { return cell.family === "square-hashed-diagonal" && cell.size === 16 && cell.sigmaIndex === 0; });
  assert.deepStrictEqual([hashed.independence.carrierConstructionRealizationCount, hashed.independence.conductanceRealizationCount, hashed.independence.jointWeightedRealizationCount], [32, 1, 32]);
  assert.ok(hashed.uniqueStructureDigestCount > 1);
  assert.deepStrictEqual([hashed.uniqueWeightDigestCount, hashed.uniqueJointDigestCount], [32, 32]);
  assert.match(hashed.independence.label, /one deterministic unit-conductance law/);

  const neck = first.controlCells.find(function (cell) { return cell.control === "vanishing-neck" && cell.size === 16; });
  assert.deepStrictEqual([neck.independence.carrierConstructionRealizationCount, neck.independence.randomizedNestedMeasurementBatchCount, neck.independence.repeatedDeterministicEvaluationCount], [1, 0, 31]);
  const volumeValues = records.filter(function (record) { return record.identity.kind === "positive" && record.identity.id === "square-alternating" && record.identity.sigmaIndex === 0; }).map(function (record) { return record.volumeGrowthScreen.logLogSlopeDescriptor; });
  assert.deepStrictEqual(deterministic.volumeSlopeDescriptor, { count: 32, mean: volumeValues.reduce(function (sum, value) { return sum + value; }, 0) / 32, minimum: Math.min.apply(null, volumeValues), maximum: Math.max.apply(null, volumeValues) });
});

test("runtime fresh-hash redirects of raw, summary, checkpoint, or source are rejected", function () {
  const fixture = sourceFixture(), rawBytes = Buffer.from("{}\n"), summary = { contentAddress: { digest: "1".repeat(64) } }, summaryBytes = Buffer.from("summary\n"), checkpoint = { contentAddress: { digest: "2".repeat(64) } }, checkpointBytes = Buffer.from("checkpoint\n");
  const context = { platformLabel: "test", source: fixture.source, rawPath: "raw", rawBytes: rawBytes, summaryPath: "summary", summaryBytes: summaryBytes, summary: summary, checkpointPath: "checkpoint", checkpointBytes: checkpointBytes, checkpoint: checkpoint };
  const runtime = Runner.buildRuntimeCertificate(context, { elapsedMilliseconds: 1 });
  [
    function (item) { item.artifacts.raw.path = "redirected"; },
    function (item) { item.artifacts.summary.sha256 = "0".repeat(64); },
    function (item) { item.artifacts.checkpointManifest.semanticDigest = "0".repeat(64); },
    function (item) { item.sourceBoundary.sourceCommit = "f".repeat(40); }
  ].forEach(function (mutate) {
    const changed = JSON.parse(JSON.stringify(runtime)); mutate(changed);
    assert.strictEqual(Runner.validateRuntimeBytes(Screening.serializeJsonArtifact(readdress(changed)), context).valid, false);
  });
});

test("runtime and checkpoint artifacts require exact pretty serialization bytes", function () {
  const fixture = sourceFixture(), rawBytes = Buffer.from("{}\n"), summary = { contentAddress: { digest: "1".repeat(64) } }, summaryBytes = Buffer.from("summary\n"), checkpoint = { contentAddress: { digest: "2".repeat(64) } }, checkpointBytes = Buffer.from("checkpoint\n"), context = { platformLabel: "test", source: fixture.source, rawPath: "raw", rawBytes: rawBytes, summaryPath: "summary", summaryBytes: summaryBytes, summary: summary, checkpointPath: "checkpoint", checkpointBytes: checkpointBytes, checkpoint: checkpoint };
  const runtime = Runner.buildRuntimeCertificate(context, { elapsedMilliseconds: 1 }), canonical = Screening.serializeJsonArtifact(runtime), noncanonical = Buffer.from(JSON.stringify(runtime) + "\n");
  assert.strictEqual(Runner.validateRuntimeBytes(canonical, context).valid, true);
  assert.strictEqual(Runner.validateRuntimeBytes(noncanonical, context).valid, false);

  const entries = Array.from({ length: 120 }, function (_, index) {
    const chunkBytes = Buffer.from("chunk-" + index + "\n"), certificatePayload = { index: index }, certificate = Object.assign({}, certificatePayload, { contentAddress: address(certificatePayload) }), certificateBytes = Screening.serializeJsonArtifact(certificate);
    return { index: index, chunkPath: "chunks/chunk-" + String(index).padStart(4, "0") + ".jsonl", certificatePath: "chunks/chunk-" + String(index).padStart(4, "0") + ".certificate.json", chunkBytes: chunkBytes, certificateBytes: certificateBytes, certificate: certificate };
  }), assembled = Buffer.concat(entries.map(function (entry) { return entry.chunkBytes; })), manifest = Runner.buildCheckpointManifest(entries, assembled, "raw", fixture.source, "test"), manifestBytes = Screening.serializeJsonArtifact(manifest);
  assert.strictEqual(Runner.validateCheckpointManifestBytes(manifestBytes, entries, assembled, "raw", fixture.source, "test").valid, true);
  assert.strictEqual(Runner.validateCheckpointManifestBytes(Buffer.from(JSON.stringify(manifest) + "\n"), entries, assembled, "raw", fixture.source, "test").valid, false);
});

test("portable boundary rejects self-readdressing, local mutation, and missing external pins", function () {
  const fixture = sourceFixture(), changed = JSON.parse(JSON.stringify(fixture.artifact)); changed.files[0].sha256 = "0".repeat(64); const changedArtifact = readdress(changed), changedBytes = Boundary.serializeArtifact(changedArtifact), changedPins = { fileSha256: Screening.sha256Bytes(changedBytes), semanticSha256: changedArtifact.contentAddress.digest };
  assert.strictEqual(Boundary.verifyBoundaryBytes(changedBytes, "portable", fixture.pins).valid, false);
  assert.strictEqual(Boundary.verifyBoundaryBytes(changedBytes, "portable", changedPins).valid, false);
  assert.strictEqual(Boundary.verifyBoundaryBytes(fixture.bytes, "portable", null).valid, false);
  const mutatedRead = function (filePath) { const bytes = fs.readFileSync(filePath); if (filePath.endsWith(fixture.artifact.files[0].path)) { const copy = Buffer.from(bytes); copy[0] ^= 1; return copy; } return bytes; };
  assert.strictEqual(Boundary.verifyBoundaryBytes(fixture.bytes, "portable", fixture.pins, { readFile: mutatedRead }).valid, false);
});

test("Git verification failure never falls back to portable mode", function () {
  const fixture = sourceFixture(), report = Boundary.verifyBoundaryBytes(fixture.bytes, "git", fixture.pins, { git: function () { throw new Error("simulated git failure"); } });
  assert.strictEqual(report.valid, false);
  assert.ok(report.errors.some(function (error) { return /without portable fallback/.test(error); }));
});

test("runner refuses portable mode whenever Git is available", function () {
  assert.throws(function () { Runner.assertSourceModePolicy("portable", function () { return true; }); }, /refused because Git is available/);
  assert.strictEqual(Runner.assertSourceModePolicy("portable", function () { return false; }).selectedMode, "portable");
});

test("run lock cannot be stolen, silently broken, or released after mutation", function () {
  const fixture = sourceFixture(), directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-lock-adversarial-")), paths = { directory: directory }, lock = Runner.acquireRunLock(paths, "test", fixture.source, "fresh");
  assert.throws(function () { Runner.acquireRunLock(paths, "test", fixture.source, "resume"); }, /definitive dead-PID proof/);
  const changed = Buffer.from(lock.bytes); changed[changed.length - 2] = changed[changed.length - 2] === 32 ? 33 : 32; fs.writeFileSync(lock.path, changed);
  assert.throws(function () { Runner.releaseRunLock(lock); }, /ownership bytes changed/);
  assert.strictEqual(fs.existsSync(lock.path), true);
});

test("durable and final writers refuse every overwrite or collision", function () {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-overwrite-")), output = path.join(directory, "final.bin"), bytes = Buffer.from("one\n");
  Runner.durableWriteNoReplace(output, bytes);
  assert.throws(function () { Runner.durableWriteNoReplace(output, bytes); }, /overwrite/);
  assert.throws(function () { Runner.ensureFinal(output, bytes, false); }, /existing final/);
  assert.strictEqual(Runner.ensureFinal(output, bytes, true), "EXISTING_IDENTICAL_VALIDATED");
  assert.throws(function () { Runner.ensureFinal(output, Buffer.from("two\n"), true); }, /collision/);
  const temporary = path.join(directory, "temp-target"); fs.writeFileSync(temporary + ".exclusive-temp", "stale");
  assert.throws(function () { Runner.durableWriteNoReplace(temporary, bytes); }, /temporary-file collision/);
});

if (!process.exitCode) process.stdout.write("Global Geometry II U2 screening v2 adversarial: " + passed + "/" + passed + " tests passed.\n");
