#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");
const zlib = require("zlib");
const B = require("./generate-global-geometry-ii-u2-evaluation-index-v2.js");
const Certificates = require("./generate-global-geometry-ii-u2-native-validation-certificates-v2.js");

let passed = 0;
function test(name, fn) {
  try { fn(); passed += 1; process.stdout.write("PASS " + name + "\n"); }
  catch (error) { process.stderr.write("FAIL " + name + "\n" + error.stack + "\n"); process.exitCode = 1; }
}
function readdress(artifact) { const payload = JSON.parse(JSON.stringify(artifact)); delete payload.contentAddress; return Object.assign({}, payload, { contentAddress: B.contentAddress(payload) }); }
function syntheticScreenCertificateBinding(label) { return { path: B.INPUTS.screeningCertificates[label], bytes: 1, sha256: (label === "macos" ? "a" : "b").repeat(64), semanticDigest: (label === "macos" ? "c" : "d").repeat(64) }; }
function loadStrictFromTrackedArchive(label) {
  const input = B.INPUTS.strict[label], archive = label === "macos" ? B.INPUTS.archives.strictMacos : B.INPUTS.archives.strictWindows;
  return { normalization: B.bindBytes(input.normalization), campaign: B.loadArchivedSource(archive, input.campaign), certificate: label === "windows" ? B.bindBytes(input.certificate) : null };
}
function loadScreenFromTrackedArchive(label) {
  const directory = B.INPUTS.screening[label], rawPath = B.screeningPaths(directory).raw, archive = label === "macos" ? B.INPUTS.archives.screeningMacos : B.INPUTS.archives.screeningWindows;
  return B.buildScreenHostProjectionFromLoaded(label, directory, B.loadArchivedSource(archive, rawPath, { json: false }), { nativeCertificateRequired: false });
}

let macosCompact, windowsCompact, strictComparison, macosScreen, macosStrictLoaded, windowsStrictLoaded;

test("macOS strict-partial compact is mechanically rebuilt from exact source bytes", function () {
  macosStrictLoaded = loadStrictFromTrackedArchive("macos");
  macosCompact = B.buildStrictCompactFromLoaded("macos", B.INPUTS.strict.macos, macosStrictLoaded.normalization, macosStrictLoaded.campaign, null, { nativeCertificateRequired: false });
  assert.strictEqual(macosCompact.schema, "gg.u2.evaluation.strict-partial-compact/2");
  assert.strictEqual(macosCompact.normalization.recordCount, 384);
  assert.strictEqual(macosCompact.campaign.counts.actualPositiveRuns, 3072);
  assert.strictEqual(macosCompact.campaign.counts.actualPrimaryControlRuns, 768);
  assert.strictEqual(macosCompact.campaign.finiteFindings.descriptiveVolume.everyIntervalStrictlyInsidePreregisteredMargin, true);
  assert.strictEqual(macosCompact.campaign.finiteFindings.descriptiveVolume.decisionStatus, "UNRESOLVED");
  assert.strictEqual(macosCompact.interpretation.u2Status, "UNRESOLVED");
  assert.strictEqual(macosCompact.inputs.hostCertificate, null);
});

test("Windows strict-partial compact independently reproduces the closed projection policy", function () {
  windowsStrictLoaded = loadStrictFromTrackedArchive("windows");
  windowsCompact = B.buildStrictCompactFromLoaded("windows", B.INPUTS.strict.windows, windowsStrictLoaded.normalization, windowsStrictLoaded.campaign, windowsStrictLoaded.certificate);
  assert.strictEqual(windowsCompact.inputs.normalization.sha256, macosCompact.inputs.normalization.sha256);
  assert.notStrictEqual(windowsCompact.inputs.campaign.sha256, macosCompact.inputs.campaign.sha256);
  assert.strictEqual(windowsCompact.campaign.diagnosticToleranceProjection.digest, "8f6ba8ff1da1d5acf872fc68bd1dca91a3441390ffac61062d39d6b14fc3289a");
  assert.strictEqual(windowsCompact.campaign.diagnosticToleranceProjection.digest, macosCompact.campaign.diagnosticToleranceProjection.digest);
});

test("strict comparison exposes exact FAIL and diagnostic PASS with no authority", function () {
  strictComparison = B.buildStrictComparison(macosCompact, windowsCompact);
  const report = B.validateStrictComparison(strictComparison, macosCompact, windowsCompact);
  assert.strictEqual(report.valid, true, report.errors.join("; "));
  assert.strictEqual(strictComparison.campaign.exactCrossPlatformReplication, "FAIL");
  assert.strictEqual(strictComparison.campaign.protocolProjectionExact, true);
  assert.strictEqual(strictComparison.campaign.scientificProjectionExact, false);
  assert.strictEqual(strictComparison.diagnosticToleranceProjection.status, "PASS");
  assert.strictEqual(strictComparison.diagnosticToleranceProjection.decisionAuthority, "NONE");
  assert.strictEqual(strictComparison.outcome.u2Status, "UNRESOLVED");
});

test("fresh content addresses cannot bless a changed strict compact", function () {
  const changed = JSON.parse(JSON.stringify(macosCompact));
  changed.campaign.finiteFindings.descriptiveVolume.decisionStatus = "PASS";
  const report = B.validateStrictCompact(readdress(changed), "macos", B.INPUTS.strict.macos, macosStrictLoaded, { nativeCertificateRequired: false });
  assert.strictEqual(report.valid, false);
});

test("Mac strict compact requires and validates its native certificate outside bootstrap", function () {
  const normalization = macosStrictLoaded.normalization, campaign = macosStrictLoaded.campaign;
  assert.throws(function () { B.buildStrictCompactFromLoaded("macos", B.INPUTS.strict.macos, normalization, campaign, null); }, /requires its native validation certificate/);
  const execution = Certificates.invocation("--write-native-all"), certificateBinding = function (loaded) { return Object.assign({}, loaded.binding, { semanticDigest: loaded.binding.semanticDigest === undefined ? null : loaded.binding.semanticDigest }); }, payload = {
    schema: B.STRICT_NATIVE_CERTIFICATE_SCHEMA,
    command: execution.command,
    invocation: execution,
    environment: { platformLabel: "macos", platform: "darwin", execArgv: execution.execArgv },
    sourceBindings: Certificates.sourceBindings(),
    artifactSourceBoundary: campaign.artifact.sourceBoundary,
    artifacts: { normalization: certificateBinding(normalization), campaign: certificateBinding(campaign), priorHostCertificate: null },
    validation: { normalization: { status: "PASS_NATIVE", recordsRemeasured: 384 }, campaign: { status: "PASS_NATIVE", positiveRecordsRemeasured: 3072, controlRecordsRemeasured: 768, calibrationRecordsRemeasured: 384 }, conclusion: campaign.artifact.conclusion.status },
    timing: { startedAt: "2026-08-30T00:00:00.000Z", completedAt: "2026-08-30T01:00:00.000Z", elapsedMilliseconds: 3600000 },
    outcome: { u2Status: "UNRESOLVED", acceptanceAllowed: false, rejectionClaimed: false, decisionAuthority: "NONE" }
  }, certificate = B.addressed(payload), loaded = { artifact: certificate, binding: { path: B.INPUTS.strict.macos.certificate, bytes: B.serializeArtifact(certificate).length, sha256: B.sha256Bytes(B.serializeArtifact(certificate)), semanticDigest: certificate.contentAddress.digest } };
  assert.strictEqual(B.validateStrictHostCertificateLoaded("macos", B.INPUTS.strict.macos, loaded, normalization, campaign).valid, true);
  const changed = JSON.parse(JSON.stringify(certificate)); changed.artifacts.campaign.sha256 = "0".repeat(64); loaded.artifact = readdress(changed);
  assert.strictEqual(B.validateStrictHostCertificateLoaded("macos", B.INPUTS.strict.macos, loaded, normalization, campaign).valid, false);
});

test("diagnostic transform omits only conductance digest and rounds exposed numbers", function () {
  const value = { positiveRuns: [{ conductance: { digest: "opaque", observedMinimum: 0.12345678901234 }, other: -0 }], exactGateOne: { value: 1.0000000000004 } }, transformed = B.diagnosticTransform(value, []);
  assert.strictEqual(Object.prototype.hasOwnProperty.call(transformed.positiveRuns[0].conductance, "digest"), false);
  assert.strictEqual(transformed.positiveRuns[0].conductance.observedMinimum, 0.123456789012);
  assert.strictEqual(Object.is(transformed.positiveRuns[0].other, -0), false);
  assert.strictEqual(transformed.exactGateOne.value, 1);
});

test("macOS screening-v3 finals replay without remeasuring outcome values", function () {
  macosScreen = loadScreenFromTrackedArchive("macos");
  assert.strictEqual(macosScreen.recordCount, 3840);
  assert.strictEqual(macosScreen.rawSha256, "47bbf6da93da1270ea5b8b6120bfa0351be3c0386050d989ef614f2a3802d1d4");
  assert.strictEqual(macosScreen.screenOutcome.u2Status, "UNRESOLVED");
  assert.strictEqual(macosScreen.containerOutcome.decisionAuthority, "NONE");
  assert.strictEqual(macosScreen.inputs.nativeValidationCertificate, null);
  macosScreen.inputs.nativeValidationCertificate = syntheticScreenCertificateBinding("macos");
});

test("screening comparison requires exact raw, record, and scientific projections", function () {
  const syntheticWindows = JSON.parse(JSON.stringify(macosScreen)); syntheticWindows.platformLabel = "windows"; syntheticWindows.inputs.nativeValidationCertificate = syntheticScreenCertificateBinding("windows");
  const comparison = B.buildScreeningComparison(macosScreen, syntheticWindows), report = B.validateScreeningComparison(comparison, macosScreen, syntheticWindows);
  assert.strictEqual(report.valid, true, report.errors.join("; "));
  assert.strictEqual(comparison.raw.status, "PASS");
  assert.strictEqual(comparison.recordHashProjection.status, "PASS");
  assert.strictEqual(comparison.scientificSummaryProjection.status, "PASS");
  assert.strictEqual(comparison.interpretation.decisionAuthority, "NONE");
  syntheticWindows.recordHashProjection = "0".repeat(64);
  assert.strictEqual(B.buildScreeningComparison(macosScreen, syntheticWindows).recordHashProjection.status, "FAIL");
  syntheticWindows.inputs.nativeValidationCertificate = null;
  assert.throws(function () { B.buildScreeningComparison(macosScreen, syntheticWindows); }, /both native validation certificates/);
});

test("screening native certificate binding rejects a freshly readdressed projection mutation", function () {
  const execution = Certificates.invocation("--write-native-all"), certificateBinding = function (binding) { return Object.assign({}, binding, { semanticDigest: binding.semanticDigest === undefined ? null : binding.semanticDigest }); }, payload = {
    schema: "gg.u2.evaluation.native-screening-v3-validation-certificate/2",
    command: execution.command,
    invocation: execution,
    environment: Certificates.environment("macos", execution),
    sourceBindings: Certificates.sourceBindings(),
    artifactSourceBoundary: macosScreen.sourceBoundary,
    artifacts: {
      raw: certificateBinding(macosScreen.inputs.raw),
      summary: certificateBinding(macosScreen.inputs.summary),
      runtime: certificateBinding(macosScreen.inputs.runtime),
      checkpoint: certificateBinding(macosScreen.inputs.checkpoint),
      writerCapability: certificateBinding(macosScreen.inputs.writerCapability)
    },
    validation: { status: "PASS_NATIVE", recordsRemeasured: 3840, expectedRecords: 3840, recordHashProjection: macosScreen.recordHashProjection, scientificSummaryProjection: macosScreen.scientificSummaryProjection, screeningOutcome: "UNRESOLVED", containerDecisionAuthority: "NONE" },
    timing: { startedAt: "2026-08-30T00:00:00.000Z", completedAt: "2026-08-30T00:10:00.000Z", elapsedMilliseconds: 600000 },
    outcome: { u2Status: "UNRESOLVED", acceptanceAllowed: false, rejectionClaimed: false, decisionAuthority: "NONE" }
  }, certificate = B.addressed(payload), loaded = { artifact: certificate, binding: { path: B.INPUTS.screeningCertificates.macos, bytes: B.serializeArtifact(certificate).length, sha256: B.sha256Bytes(B.serializeArtifact(certificate)), semanticDigest: certificate.contentAddress.digest } }, context = {
    raw: { binding: macosScreen.inputs.raw }, summary: { binding: macosScreen.inputs.summary }, runtime: { binding: macosScreen.inputs.runtime }, checkpoint: { binding: macosScreen.inputs.checkpoint }, writer: { binding: macosScreen.inputs.writerCapability }, sourceBoundary: macosScreen.sourceBoundary, recordHashProjection: macosScreen.recordHashProjection, scientificSummaryProjection: macosScreen.scientificSummaryProjection
  };
  assert.strictEqual(B.validateNativeScreeningCertificateLoaded("macos", loaded, context).valid, true);
  const changed = readdress(Object.assign({}, certificate, { validation: Object.assign({}, certificate.validation, { recordHashProjection: "0".repeat(64) }) })); loaded.artifact = changed;
  assert.strictEqual(B.validateNativeScreeningCertificateLoaded("macos", loaded, context).valid, false);
});

test("convenience archive binding proves exact decompressed campaign bytes", function () {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-eval-archive-")), campaignPath = path.join(directory, "campaign.json"), archivePath = path.join(directory, "campaign.json.gz"), payload = { schema: "fixture" }, artifact = Object.assign({}, payload, { contentAddress: B.contentAddress(payload) }), bytes = B.serializeArtifact(artifact);
  fs.writeFileSync(campaignPath, bytes); fs.writeFileSync(archivePath, zlib.gzipSync(bytes, { level: 9, mtime: 0 }));
  const campaignRelative = path.relative(B.ROOT, campaignPath), archiveRelative = path.relative(B.ROOT, archivePath), binding = { path: campaignRelative, bytes: bytes.length, sha256: B.sha256Bytes(bytes), semanticDigest: artifact.contentAddress.digest }, archive = B.bindConvenienceArchive(archiveRelative, binding, "FIXTURE_JSON");
  assert.strictEqual(archive.decompressedSha256, binding.sha256);
  assert.strictEqual(archive.decompressedBytes, binding.bytes);
  assert.strictEqual(archive.scientificAuthority, "NONE");
  fs.writeFileSync(archivePath, zlib.gzipSync(Buffer.from("different\n"), { level: 9, mtime: 0 }));
  assert.throws(function () { B.bindConvenienceArchive(archiveRelative, binding, "FIXTURE_JSON"); }, /decompression differs/);
});

test("evaluation index freezes unperformed stages and overall UNRESOLVED", function () {
  const syntheticWindows = JSON.parse(JSON.stringify(macosScreen)); syntheticWindows.platformLabel = "windows"; syntheticWindows.inputs.nativeValidationCertificate = syntheticScreenCertificateBinding("windows");
  const screenComparison = B.buildScreeningComparison(macosScreen, syntheticWindows), role = "deterministic gzip -n -9 convenience transport; decompressed bytes are the authoritative bound source artifact", archives = [
    { path: B.INPUTS.archives.strictMacos, rawSha256: "1".repeat(64), rawBytes: 1, decompressedSha256: macosCompact.inputs.campaign.sha256, decompressedBytes: macosCompact.inputs.campaign.bytes, correspondingSourcePath: macosCompact.inputs.campaign.path, correspondingSourceSemanticDigest: macosCompact.inputs.campaign.semanticDigest, sourceKind: "STRICT_PARTIAL_CAMPAIGN", scientificAuthority: "NONE", role: role },
    { path: B.INPUTS.archives.strictWindows, rawSha256: "2".repeat(64), rawBytes: 2, decompressedSha256: windowsCompact.inputs.campaign.sha256, decompressedBytes: windowsCompact.inputs.campaign.bytes, correspondingSourcePath: windowsCompact.inputs.campaign.path, correspondingSourceSemanticDigest: windowsCompact.inputs.campaign.semanticDigest, sourceKind: "STRICT_PARTIAL_CAMPAIGN", scientificAuthority: "NONE", role: role },
    { path: B.INPUTS.archives.screeningMacos, rawSha256: "3".repeat(64), rawBytes: 3, decompressedSha256: macosScreen.inputs.raw.sha256, decompressedBytes: macosScreen.inputs.raw.bytes, correspondingSourcePath: macosScreen.inputs.raw.path, correspondingSourceSemanticDigest: null, sourceKind: "SCREENING_V3_RAW_JSONL", scientificAuthority: "NONE", role: role },
    { path: B.INPUTS.archives.screeningWindows, rawSha256: "4".repeat(64), rawBytes: 4, decompressedSha256: syntheticWindows.inputs.raw.sha256, decompressedBytes: syntheticWindows.inputs.raw.bytes, correspondingSourcePath: syntheticWindows.inputs.raw.path, correspondingSourceSemanticDigest: null, sourceKind: "SCREENING_V3_RAW_JSONL", scientificAuthority: "NONE", role: role }
  ], index = B.buildEvaluationIndex(macosCompact, windowsCompact, strictComparison, screenComparison, archives), report = B.validateEvaluationIndex(index, macosCompact, windowsCompact, strictComparison, screenComparison, archives);
  assert.strictEqual(report.valid, true, report.errors.join("; "));
  assert.strictEqual(index.convenienceArchives.length, 4);
  assert.strictEqual(index.stages.preview.status, "NOT_EVALUATED");
  assert.strictEqual(index.stages.fullConfirmatory.status, "NOT_RUN");
  assert.strictEqual(index.stages.physicalValidation.status, "NOT_RUN");
  assert.strictEqual(index.overall.u2Status, "UNRESOLVED");
  assert.strictEqual(index.overall.acceptanceAllowed, false);
  assert.strictEqual(index.overall.rejectionClaimed, false);
  assert.strictEqual(index.artifacts.nativeScreeningMacosCertificate.path, B.INPUTS.screeningCertificates.macos);
  assert.strictEqual(index.artifacts.nativeScreeningWindowsCertificate.path, B.INPUTS.screeningCertificates.windows);
});

test("read-only CLI modes split deep numerical replay without skipping exact output replay", function () {
  const both = B.validationPlan("--validate-only"), strict = B.validationPlan("--validate-strict"), screening = B.validationPlan("--validate-screening");
  assert.deepStrictEqual([both.validateStrict, both.validateScreening, both.sourceMode], [true, true, "archives"]);
  assert.deepStrictEqual([strict.validateStrict, strict.validateScreening, strict.sourceMode], [true, false, "archives"]);
  assert.deepStrictEqual([screening.validateStrict, screening.validateScreening, screening.sourceMode], [false, true, "archives"]);
  assert.throws(function () { B.validationPlan("--validate-unknown"); }, /usage/);
});

test("native certificate schema is private, content-addressed, fail-closed, and write-once", function () {
  const label = process.platform === "darwin" ? "macos" : process.platform === "win32" ? "windows" : "macos", execution = { executable: "node", execArgv: [], script: Certificates.SCRIPT_PATH, mode: "--write-native-screening", argv: [Certificates.SCRIPT_PATH, "--write-native-screening"], command: "node " + Certificates.SCRIPT_PATH + " --write-native-screening" }, payload = {
    schema: "gg.u2.evaluation.native-screening-v3-validation-certificate/2",
    command: execution.command,
    invocation: execution,
    environment: { platformLabel: label, execArgv: [] },
    sourceBindings: { evaluationBuilder: Certificates.bindFile("website/global-geometry-lab/generate-global-geometry-ii-u2-evaluation-index-v2.js", false) },
    artifacts: {},
    validation: { status: "PASS_NATIVE" },
    timing: { startedAt: "2026-08-30T00:00:00.000Z", completedAt: "2026-08-30T00:00:01.000Z", elapsedMilliseconds: 1000 },
    outcome: { u2Status: "UNRESOLVED", acceptanceAllowed: false, rejectionClaimed: false, decisionAuthority: "NONE" }
  }, certificate = B.addressed(payload), report = Certificates.validateCertificate(certificate, payload.schema, label);
  assert.strictEqual(report.valid, true, report.errors.join("; "));
  assert.strictEqual(Object.prototype.hasOwnProperty.call(execution, "executablePath"), false);
  assert.strictEqual(Certificates.containsAbsolutePathToken("--max-old-space-size=4096"), false);
  assert.strictEqual(Certificates.containsAbsolutePathToken("--require=/Users/example/private-loader.js"), true);
  assert.strictEqual(Certificates.containsAbsolutePathToken("--require=C:\\private\\loader.js"), true);
  const changed = JSON.parse(JSON.stringify(certificate)); changed.outcome.acceptanceAllowed = true;
  assert.strictEqual(Certificates.validateCertificate(readdress(changed), payload.schema, label).valid, false);
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-native-cert-")), relative = path.relative(B.ROOT, path.join(directory, "certificate.json"));
  const written = Certificates.writeOnce(relative, certificate); assert.strictEqual(written.semanticDigest, certificate.contentAddress.digest);
  assert.throws(function () { Certificates.writeOnce(relative, certificate); }, /overwrite/);
});

test("native certificate snapshots fail closed when a bound byte changes", function () {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "ggii-native-snapshot-")), target = path.join(directory, "source.js"), relative = path.relative(B.ROOT, target);
  fs.writeFileSync(target, "original\n");
  const binding = Certificates.bindFile(relative, false);
  Certificates.assertBindingsUnchanged({ fixture: binding }, "fixture");
  fs.writeFileSync(target, "changed\n");
  assert.throws(function () { Certificates.assertBindingsUnchanged({ fixture: binding }, "fixture"); }, /changed during native validation/);
});

if (!process.exitCode) process.stdout.write("Global Geometry II U2 evaluation index v2: " + passed + "/" + passed + " tests passed.\n");
