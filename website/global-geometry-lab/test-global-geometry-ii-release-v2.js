#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const Release = require("./generate-global-geometry-ii-release-v2.js");
const Reproduce = require("./reproduce-global-geometry-ii-v2.js");
const Compare = require("./compare-global-geometry-ii-certificates-v2.js");

const tests = [];
function test(name, body) { tests.push({ name, body }); }
function clone(value) { return JSON.parse(JSON.stringify(value)); }
function isArchiveRole(role) { return Release.ARCHIVE_ROLES.includes(role); }

function writeJson(filePath, value) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(value, null, 2) + "\n", "utf8");
}

function reseal(value) {
  delete value.contentAddress;
  value.contentAddress = Release.contentAddress(value);
  return value;
}

function relativeToRepo(absolute) {
  return Release.repoRelative(absolute, Release.REPO_ROOT);
}

function fixtureEntry(directory, descriptor, index) {
  const extension = descriptor.role === "evaluation-report"
    ? ".md"
    : descriptor.role === "screening-raw-archive" ? ".jsonl.gz"
      : descriptor.role === "strict-campaign-archive" ? ".json.gz" : ".json";
  const filename = String(index).padStart(2, "0") + "-" + descriptor.role + "-" + descriptor.platform + extension;
  const absolute = path.join(directory, filename);
  let addressing = "canonical-json";
  let mediaType = "application/json";
  let expectedSchema = descriptor.role === "evaluation-index"
    ? Release.EVALUATION_INDEX_SCHEMA
    : "ggii.release-v2-test-fixture/1";
  if (descriptor.role === "evaluation-report") {
    fs.writeFileSync(absolute, "# Synthetic evaluation checkpoint\n\nNo acceptance or rejection claim.\n", "utf8");
    addressing = "utf8-text";
    mediaType = "text/markdown";
    expectedSchema = null;
  } else if (isArchiveRole(descriptor.role)) {
    fs.writeFileSync(absolute, zlib.gzipSync(Buffer.from(JSON.stringify({ fixtureId: descriptor.id }) + "\n", "utf8")));
    addressing = "raw-bytes-only";
    mediaType = "application/gzip";
    expectedSchema = null;
  } else {
    let document = {
      schema: expectedSchema,
      fixtureId: descriptor.id,
      platform: descriptor.platform,
      boundary: "NO_ACCEPTANCE_OR_REJECTION_CLAIM"
    };
    if (descriptor.id === "evaluation-index") {
      document = reseal(document);
      addressing = "content-addressed-json";
    }
    writeJson(absolute, document);
  }
  return {
    id: descriptor.id,
    path: relativeToRepo(absolute),
    role: descriptor.role,
    platform: descriptor.platform,
    mediaType,
    addressing,
    expectedSchema,
    required: true,
    maximumBytes: 1024 * 1024
  };
}

function makeRegistry(directory) {
  const descriptors = [
    { id: "evaluation-index", role: "evaluation-index", platform: "shared" },
    { id: "evaluation-report", role: "evaluation-report", platform: "shared" },
    { id: "screening-summary-darwin", role: "screening-summary", platform: "darwin" },
    { id: "screening-summary-win32", role: "screening-summary", platform: "win32" },
    { id: "screening-runtime-darwin", role: "screening-runtime", platform: "darwin" },
    { id: "screening-runtime-win32", role: "screening-runtime", platform: "win32" },
    { id: "screening-writer-darwin", role: "screening-writer-capability", platform: "darwin" },
    { id: "screening-writer-win32", role: "screening-writer-capability", platform: "win32" },
    { id: "screening-checkpoint-darwin", role: "screening-checkpoint", platform: "darwin" },
    { id: "screening-checkpoint-win32", role: "screening-checkpoint", platform: "win32" },
    { id: "screening-certificate-darwin", role: "screening-certificate", platform: "darwin" },
    { id: "screening-certificate-win32", role: "screening-certificate", platform: "win32" },
    { id: "screening-source-boundary", role: "screening-source-boundary", platform: "shared" },
    { id: "screening-comparison", role: "screening-comparison", platform: "shared" },
    { id: "strict-normalization-darwin", role: "strict-normalization", platform: "darwin" },
    { id: "strict-normalization-win32", role: "strict-normalization", platform: "win32" },
    { id: "strict-summary-darwin", role: "strict-partial-summary", platform: "darwin" },
    { id: "strict-summary-win32", role: "strict-partial-summary", platform: "win32" },
    { id: "strict-certificate-darwin", role: "strict-partial-certificate", platform: "darwin" },
    { id: "strict-certificate-win32", role: "strict-partial-certificate", platform: "win32" },
    { id: "strict-comparison", role: "strict-partial-comparison", platform: "shared" },
    { id: "strict-archive-darwin", role: "strict-campaign-archive", platform: "darwin" },
    { id: "strict-archive-win32", role: "strict-campaign-archive", platform: "win32" },
    { id: "screening-archive-darwin", role: "screening-raw-archive", platform: "darwin" },
    { id: "screening-archive-win32", role: "screening-raw-archive", platform: "win32" }
  ];
  const entries = Release.PRINCIPAL_ARTIFACTS.map((artifact) => ({
    id: artifact.id,
    path: artifact.path,
    role: "principal-artifact",
    platform: "shared",
    mediaType: "application/json",
    addressing: "content-addressed-json",
    expectedSchema: artifact.schema,
    required: true,
    maximumBytes: Release.MAX_REGISTERED_BYTES
  })).concat(descriptors.map((descriptor, index) => fixtureEntry(directory, descriptor, index)));
  const archiveEntries = entries.filter((entry) => isArchiveRole(entry.role));
  const evaluationIndexEntry = entries.find((entry) => entry.role === "evaluation-index");
  const archiveRecords = archiveEntries.map((entry) => {
    const absolute = path.join(Release.REPO_ROOT, entry.path);
    const raw = fs.readFileSync(absolute);
    const decompressed = zlib.gunzipSync(raw);
    const strict = entry.role === "strict-campaign-archive";
    return {
      path: entry.path,
      rawSha256: Release.sha256Bytes(raw),
      rawBytes: raw.length,
      decompressedSha256: Release.sha256Bytes(decompressed),
      decompressedBytes: decompressed.length,
      correspondingSourcePath: relativeToRepo(path.join(directory, entry.platform + (strict ? "-campaign.json" : "-screening.jsonl"))),
      correspondingSourceSemanticDigest: strict ? Release.sha256Bytes(decompressed) : null,
      sourceKind: strict ? "STRICT_PARTIAL_CAMPAIGN" : "SCREENING_V3_RAW_JSONL",
      scientificAuthority: "NONE",
      role: Release.ARCHIVE_ROLE
    };
  });
  writeJson(path.join(Release.REPO_ROOT, evaluationIndexEntry.path), reseal({
    schema: Release.EVALUATION_INDEX_SCHEMA,
    fixtureId: "evaluation-index",
    convenienceArchives: archiveRecords
  }));
  entries.push({
    id: Release.PHYSICAL_PREFLIGHT_ARTIFACT.id,
    path: Release.PHYSICAL_PREFLIGHT_ARTIFACT.path,
    role: "physical-preflight",
    platform: "shared",
    mediaType: "application/json",
    addressing: "content-addressed-json",
    expectedSchema: Release.PHYSICAL_PREFLIGHT_ARTIFACT.schema,
    required: true,
    maximumBytes: Release.MAX_REGISTERED_BYTES
  });
  entries.push({
    id: "historical-v1-index",
    path: Release.HISTORICAL_V1_INDEX,
    role: "historical-v1-metadata",
    platform: "shared",
    mediaType: "application/json",
    addressing: "canonical-json",
    expectedSchema: null,
    required: true,
    maximumBytes: Release.MAX_REGISTERED_BYTES
  });
  entries.push({
    id: "historical-v1-comparison",
    path: Release.HISTORICAL_V1_COMPARISON,
    role: "historical-v1-metadata",
    platform: "shared",
    mediaType: "application/json",
    addressing: "canonical-json",
    expectedSchema: null,
    required: true,
    maximumBytes: Release.MAX_REGISTERED_BYTES
  });
  return {
    schema: Release.REGISTRY_SCHEMA,
    releaseId: Release.RELEASE_ID,
    evaluationBoundary: {
      checkpointStatus: "UNRESOLVED",
      u2Decision: "NO_ACCEPTANCE_OR_REJECTION_CLAIM",
      universalityClaim: "NONE",
      fullConfirmatoryEvaluation: "NOT_RUN",
      physicalValidation: "NOT_RUN",
      publicationMeaning: "SHAREABLE_EVIDENCE_CHECKPOINT_NOT_A_CONFIRMATORY_DECISION"
    },
    historicalV1: {
      classification: Release.HISTORICAL_V1_CLASSIFICATION,
      releaseIndexPath: Release.HISTORICAL_V1_INDEX,
      comparisonPath: Release.HISTORICAL_V1_COMPARISON
    },
    entries,
    deepSuites: [
      {
        id: "screening-v3-artifact-validation",
        path: "website/global-geometry-lab/generate-global-geometry-ii-u2-evaluation-index-v2.js",
        args: ["--validate-screening"],
        timeoutMs: 600000,
        readOnly: true,
        coverage: "screening-v3"
      },
      {
        id: "strict-partial-artifact-validation",
        path: "website/global-geometry-lab/generate-global-geometry-ii-u2-evaluation-index-v2.js",
        args: ["--validate-strict"],
        timeoutMs: 600000,
        readOnly: true,
        coverage: "strict-partial"
      }
    ]
  };
}

function withFixture(body) {
  const parent = path.join(Release.REPO_ROOT, "artifacts/global-geometry-ii");
  const directory = fs.mkdtempSync(path.join(parent, ".release-v2-test-"));
  try {
    const registry = makeRegistry(directory);
    const registryPath = path.join(directory, "registry.json");
    writeJson(registryPath, registry);
    return body({ directory, registry, registryPath });
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
}

function fixtureEnvironment(platform) {
  return {
    platform,
    architecture: platform === "darwin" ? "arm64" : "x64",
    endianness: "LE",
    nodeVersion: "v22.0.0-fixture",
    v8Version: "fixture-v8",
    uvVersion: "fixture-uv"
  };
}

function syntheticSuiteResult(suite) {
  const empty = Release.sha256Bytes(Buffer.alloc(0));
  return {
    id: suite.id,
    path: suite.path,
    args: suite.args.slice(),
    tier: suite.tier,
    coverage: suite.coverage,
    status: "PASS",
    exitCode: 0,
    durationMs: 0,
    stdoutBytes: 0,
    stdoutSha256: empty,
    stderrBytes: 0,
    stderrSha256: empty
  };
}

function generateFixtureRelease(fixture) {
  const manifest = path.join(fixture.directory, "manifest-v2.json");
  const index = path.join(fixture.directory, "index-v2.json");
  const result = Release.generate({ manifest, index, registry: fixture.registryPath });
  return { manifest, index, result };
}

function deepCertificate(fixture, platform) {
  const release = generateFixtureRelease(fixture);
  const payload = Reproduce.verifyRepository({
    mode: "deep",
    manifest: release.manifest,
    index: release.index,
    environment: fixtureEnvironment(platform),
    runSuite: syntheticSuiteResult
  });
  return { release, artifact: reseal(payload) };
}

test("release-v2 paths, schemas, and CLI contracts are versioned independently from v1", () => {
  assert.notStrictEqual(Release.DEFAULT_MANIFEST, path.join(Release.REPO_ROOT, "global_geometry_ii_reproducibility_manifest.json"));
  assert.notStrictEqual(Release.DEFAULT_INDEX, path.join(Release.REPO_ROOT, "artifacts/global-geometry-ii/release-index-v1.json"));
  assert.strictEqual(Release.MANIFEST_SCHEMA, "ggii.reproducibility-manifest/2");
  assert.strictEqual(Release.INDEX_SCHEMA, "ggii.release-index/2");
  assert.strictEqual(Reproduce.CERTIFICATE_SCHEMA, "ggii.local-reproduction-certificate/3");
  assert.strictEqual(Compare.COMPARISON_SCHEMA, "ggii.cross-platform-reproduction-comparison/3");
  assert.throws(() => Release.parseOutputs(["--manifest", "x"]), /exactly/);
  assert.throws(() => Reproduce.parseArgs(["--verify"]), /mode/);
  assert.throws(() => Reproduce.parseArgs(["--verify", "--mode", "other"]), /quick or deep/);
  assert.deepStrictEqual(Reproduce.parseArgs(["--verify", "--mode", "quick"]), {
    verify: true,
    mode: "quick",
    certificate: null,
    manifest: Release.DEFAULT_MANIFEST,
    index: Release.DEFAULT_INDEX
  });
});

test("public release certificates minimize host fingerprinting", () => {
  const environment = Reproduce.environmentRecord();
  assert.deepStrictEqual(Object.keys(environment).sort(), [
    "architecture", "endianness", "nodeVersion", "platform", "uvVersion", "v8Version"
  ]);
  ["hostname", "operatingSystemRelease", "logicalCpuCount", "cpuModel", "totalMemoryBytes", "execPath"].forEach((field) => {
    assert.strictEqual(Object.prototype.hasOwnProperty.call(environment, field), false);
  });
});

test("registry closes every required compact role and labels v1 historical only", () => withFixture((fixture) => {
  assert.doesNotThrow(() => Release.validateRegistry(fixture.registry));
  assert.strictEqual(fixture.registry.entries.length, 32);
  assert.strictEqual(fixture.registry.historicalV1.classification, Release.HISTORICAL_V1_CLASSIFICATION);
  const history = fixture.registry.entries.filter((entry) => entry.role === "historical-v1-metadata");
  assert.deepStrictEqual(history.map((entry) => entry.path).sort(), [Release.HISTORICAL_V1_COMPARISON, Release.HISTORICAL_V1_INDEX].sort());
  Release.REQUIRED_PAIRED_ROLES.forEach((role) => {
    assert.deepStrictEqual(fixture.registry.entries.filter((entry) => entry.role === role).map((entry) => entry.platform).sort(), ["darwin", "win32"]);
  });
  const extra = clone(fixture.registry.entries.find((entry) => entry.role === "screening-comparison"));
  extra.id += "-duplicate";
  extra.path = "artifacts/global-geometry-ii/extra-screening-comparison.json";
  const duplicateRole = clone(fixture.registry);
  duplicateRole.entries.push(extra);
  assert.throws(() => Release.validateRegistry(duplicateRole), /exactly 1 entry\/entries for role screening-comparison/);
}));

test("registry rejects scope promotion, missing platform pairs, and write-capable deep commands", () => withFixture((fixture) => {
  const promoted = clone(fixture.registry);
  promoted.evaluationBoundary.u2Decision = "ACCEPT";
  assert.throws(() => Release.validateRegistry(promoted), /must not make/);

  const missingPair = clone(fixture.registry);
  missingPair.entries = missingPair.entries.filter((entry) => entry.id !== "screening-summary-win32");
  assert.throws(() => Release.validateRegistry(missingPair), /required compact release roles|screening-summary/);

  const writeCapable = clone(fixture.registry);
  writeCapable.deepSuites[0].args = ["--validate-only", "--output", "forbidden.json"];
  assert.throws(() => Release.validateRegistry(writeCapable), /write-capable flag/);
}));

test("targeted strict and screening deep-validation flags are read-only registered modes", () => withFixture((fixture) => {
  assert.doesNotThrow(() => Release.validateRegistry(fixture.registry));
  const impostor = clone(fixture.registry);
  impostor.deepSuites[0].path = "website/global-geometry-lab/run-global-geometry-ii-u2-screening-execution-v3.js";
  assert.throws(() => Release.validateRegistry(impostor), /must bind the evaluation-index validator/);
}));

test("compact policy rejects chunks, raw JSONL, partials, locks, and oversized bounds", () => withFixture((fixture) => {
  const forbiddenPaths = [
    "artifacts/global-geometry-ii/u2/chunks/chunk-0001.json",
    "artifacts/global-geometry-ii/u2/screening-raw-v3.jsonl",
    "artifacts/global-geometry-ii/u2/result.json.partial",
    "artifacts/global-geometry-ii/u2/.run-lock-v3.json"
  ];
  forbiddenPaths.forEach((forbidden) => {
    const changed = clone(fixture.registry);
    changed.entries[0].path = forbidden;
    assert.throws(() => Release.validateRegistry(changed), /not a compact publishable artifact|raw marker/);
  });
  const oversized = clone(fixture.registry);
  oversized.entries[0].maximumBytes = Release.MAX_REGISTERED_BYTES + 1;
  assert.throws(() => Release.validateRegistry(oversized), /compact-input policy/);
}));

test("registered JSON and Markdown inputs receive deterministic raw and semantic addresses", () => withFixture((fixture) => {
  const record = Release.readRegistry(fixture.registryPath);
  const first = fixture.registry.entries.map((entry) => Release.inspectRegisteredEntry(entry));
  const second = record.registry.entries.map((entry) => Release.inspectRegisteredEntry(entry));
  assert.strictEqual(Release.canonicalStringify(first), Release.canonicalStringify(second));
  first.forEach((entry) => {
    assert.match(entry.rawSha256, /^[0-9a-f]{64}$/);
    assert.ok(entry.rawBytes > 0 && entry.rawBytes <= Release.MAX_REGISTERED_BYTES);
    if (entry.semanticAddress !== null) assert.match(entry.semanticAddress.digest, /^[0-9a-f]{64}$/);
  });
  const report = first.find((entry) => entry.role === "evaluation-report");
  assert.strictEqual(report.observedSchema, null);
  assert.strictEqual(report.semanticAddress.canonicalization, Release.ADDRESS_CANONICALIZATION);
  const archives = first.filter((entry) => isArchiveRole(entry.role));
  assert.strictEqual(archives.length, 4);
  archives.forEach((entry) => {
    assert.strictEqual(entry.semanticAddress, null);
    assert.match(entry.semanticReplay, /^NOT_APPLICABLE_GZIP_CONVENIENCE_COPY/);
  });
}));

test("raw-only gzip transports are cross-bound to the content-addressed evaluation index", () => withFixture((fixture) => {
  const payload = Release.buildManifestPayload({ registryPath: fixture.registryPath });
  assert.strictEqual(payload.archiveIndexBindings.bindings.length, 4);
  payload.archiveIndexBindings.bindings.forEach((binding) => {
    assert.match(binding.rawSha256, /^[0-9a-f]{64}$/);
    assert.match(binding.decompressedSha256, /^[0-9a-f]{64}$/);
    assert.strictEqual(binding.scientificAuthority, "NONE");
    assert.strictEqual(binding.role, Release.ARCHIVE_ROLE);
  });
  const indexEntry = fixture.registry.entries.find((entry) => entry.role === "evaluation-index");
  const indexPath = path.join(Release.REPO_ROOT, indexEntry.path);
  const original = JSON.parse(fs.readFileSync(indexPath, "utf8"));
  const rawMismatch = clone(original);
  delete rawMismatch.contentAddress;
  rawMismatch.convenienceArchives[0].rawSha256 = "0".repeat(64);
  writeJson(indexPath, reseal(rawMismatch));
  assert.throws(() => Release.buildManifestPayload({ registryPath: fixture.registryPath }), /raw archive address/);

  const wrongKind = clone(original);
  delete wrongKind.contentAddress;
  wrongKind.convenienceArchives[0].sourceKind = wrongKind.convenienceArchives[0].sourceKind === "STRICT_PARTIAL_CAMPAIGN"
    ? "SCREENING_V3_RAW_JSONL"
    : "STRICT_PARTIAL_CAMPAIGN";
  writeJson(indexPath, reseal(wrongKind));
  assert.throws(() => Release.buildManifestPayload({ registryPath: fixture.registryPath }), /sourceKind/);

  const archiveEntry = fixture.registry.entries.find((entry) => isArchiveRole(entry.role));
  fs.writeFileSync(path.join(Release.REPO_ROOT, archiveEntry.path), Buffer.from("not gzip", "utf8"));
  assert.throws(() => Release.inspectRegisteredEntry(archiveEntry), /gzip magic/);
}));

test("content-addressed inputs fail closed under nested tampering or schema mismatch", () => withFixture((fixture) => {
  const entry = fixture.registry.entries.find((candidate) => candidate.id === "evaluation-index");
  const absolute = path.join(Release.REPO_ROOT, entry.path);
  const original = JSON.parse(fs.readFileSync(absolute, "utf8"));
  original.platform = "tampered";
  writeJson(absolute, original);
  assert.throws(() => Release.inspectRegisteredEntry(entry), /contentAddress does not verify/);

  const other = fixture.registry.entries.find((candidate) => candidate.id === "screening-summary-darwin");
  const mismatched = clone(other);
  mismatched.expectedSchema = "another/schema";
  assert.throws(() => Release.inspectRegisteredEntry(mismatched), /schema mismatch/);
}));

test("generator produces a one-way, content-addressed v2 manifest/index without modifying v1", () => withFixture((fixture) => {
  const v1IndexBefore = Release.sha256File(path.join(Release.REPO_ROOT, Release.HISTORICAL_V1_INDEX));
  const v1ComparisonBefore = Release.sha256File(path.join(Release.REPO_ROOT, Release.HISTORICAL_V1_COMPARISON));
  const release = generateFixtureRelease(fixture);
  const manifest = Release.verifyAddressedFile(release.manifest, Release.MANIFEST_SCHEMA);
  const index = Release.verifyAddressedFile(release.index, Release.INDEX_SCHEMA);
  assert.deepStrictEqual(index.payload.manifest.contentAddress, manifest.address);
  assert.strictEqual(manifest.payload.registeredArtifacts.length, 32);
  assert.strictEqual(manifest.payload.claimBoundary.u2Decision, "NO_ACCEPTANCE_OR_REJECTION_CLAIM");
  assert.strictEqual(manifest.payload.claimBoundary.physicalValidation, "NOT_RUN");
  assert.strictEqual(manifest.payload.historicalV1.classification, Release.HISTORICAL_V1_CLASSIFICATION);
  assert.strictEqual(index.payload.historicalV1.classification, Release.HISTORICAL_V1_CLASSIFICATION);
  assert.strictEqual(index.payload.executionSurface.deepRevalidationSeparatedFromQuick, true);
  assert.match(index.payload.hashTopology, /v1 is historical and does not certify v2/);
  assert.deepStrictEqual(Release.sha256File(path.join(Release.REPO_ROOT, Release.HISTORICAL_V1_INDEX)), v1IndexBefore);
  assert.deepStrictEqual(Release.sha256File(path.join(Release.REPO_ROOT, Release.HISTORICAL_V1_COMPARISON)), v1ComparisonBefore);
  assert.throws(() => Release.generate({ manifest: release.manifest, index: release.index, registry: fixture.registryPath }), /write-once/);
}));

test("generator fails closed when any configured artifact is absent", () => withFixture((fixture) => {
  const missing = clone(fixture.registry);
  const target = missing.entries.find((entry) => entry.role === "evaluation-index");
  target.path = relativeToRepo(path.join(fixture.directory, "absent-evaluation-index.json"));
  const registryPath = path.join(fixture.directory, "missing-registry.json");
  writeJson(registryPath, missing);
  assert.throws(() => Release.buildManifestPayload({ registryPath }), /required release input is absent/);
}));

test("quick and deep verification surfaces are explicitly separate and read-only", () => withFixture((fixture) => {
  const release = generateFixtureRelease(fixture);
  const quickSeen = [];
  const quick = Reproduce.verifyRepository({
    mode: "quick",
    manifest: release.manifest,
    index: release.index,
    environment: fixtureEnvironment("darwin"),
    runSuite(suite) { quickSeen.push(suite); return syntheticSuiteResult(suite); }
  });
  assert.strictEqual(quick.suites.quick.length, Release.QUICK_SUITES.length);
  assert.strictEqual(quick.suites.deep.length, 0);
  assert.ok(quickSeen.every((suite) => suite.tier === "quick"));
  assert.match(quick.certification.releaseGate, /QUICK_MODE/);

  const deepSeen = [];
  const deep = Reproduce.verifyRepository({
    mode: "deep",
    manifest: release.manifest,
    index: release.index,
    environment: fixtureEnvironment("darwin"),
    runSuite(suite) { deepSeen.push(suite); return syntheticSuiteResult(suite); }
  });
  assert.strictEqual(deep.suites.quick.length, Release.QUICK_SUITES.length);
  assert.strictEqual(deep.suites.deep.length, 2);
  assert.ok(deepSeen.some((suite) => suite.tier === "deep"));
  assert.strictEqual(deep.certification.u2Decision, "NO_ACCEPTANCE_OR_REJECTION_CLAIM");
  assert.strictEqual(deep.certification.physicalValidation, "NOT_RUN");
}));

test("verifier rejects a compact artifact changed after manifest generation", () => withFixture((fixture) => {
  const release = generateFixtureRelease(fixture);
  const entry = fixture.registry.entries.find((candidate) => candidate.role === "evaluation-index");
  const absolute = path.join(Release.REPO_ROOT, entry.path);
  const document = JSON.parse(fs.readFileSync(absolute, "utf8"));
  document.changedAfterFreeze = true;
  writeJson(absolute, document);
  assert.throws(() => Reproduce.loadReleaseMetadata({ manifest: release.manifest, index: release.index }), /does not match the current|contentAddress does not verify/);
}));

test("deep certificates are write-once, content-addressed, and no-decision scoped", () => withFixture((fixture) => {
  const release = generateFixtureRelease(fixture);
  const payload = Reproduce.verifyRepository({
    mode: "deep",
    manifest: release.manifest,
    index: release.index,
    environment: fixtureEnvironment("darwin"),
    runSuite: syntheticSuiteResult
  });
  const output = path.join(fixture.directory, "darwin-deep-certificate.json");
  const written = Reproduce.writeCertificate(output, payload, { manifest: release.manifest, index: release.index });
  assert.match(written.address.digest, /^[0-9a-f]{64}$/);
  const artifact = JSON.parse(fs.readFileSync(output, "utf8"));
  assert.strictEqual(Compare.validateLocalCertificate(artifact, "fixture").platform, "darwin");
  assert.strictEqual(artifact.certification.u2Decision, "NO_ACCEPTANCE_OR_REJECTION_CLAIM");
  assert.strictEqual(artifact.certification.historicalV1, Release.HISTORICAL_V1_CLASSIFICATION);
  assert.throws(() => Reproduce.writeCertificate(output, payload, { manifest: release.manifest, index: release.index }), /EEXIST|exist/i);
  assert.throws(() => Reproduce.writeCertificate(release.manifest, payload, { manifest: release.manifest, index: release.index }), /overwrite/);
  const widened = clone(payload);
  widened.unregisteredClaim = "PASS";
  assert.throws(
    () => Reproduce.writeCertificate(path.join(fixture.directory, "widened.json"), widened, { manifest: release.manifest, index: release.index }),
    /noncanonical schema/
  );
  const digestDrift = clone(payload);
  digestDrift.releaseDigests.registeredArtifacts[0].rawSha256 = "0".repeat(64);
  assert.throws(
    () => Reproduce.writeCertificate(path.join(fixture.directory, "digest-drift.json"), digestDrift, { manifest: release.manifest, index: release.index }),
    /release digests/
  );
}));

test("matching Darwin and Windows deep certificates close only the declared v2 surface", () => withFixture((fixture) => {
  const darwinRecord = deepCertificate(fixture, "darwin");
  const darwin = darwinRecord.artifact;
  const windows = clone(darwin);
  windows.generatedAtUtc = "2026-08-30T20:00:00.000Z";
  windows.environment = fixtureEnvironment("win32");
  windows.certification.observedPlatform = "win32";
  windows.suites.quick.forEach((suite, index) => { suite.durationMs = 100 + index; });
  windows.suites.deep.forEach((suite, index) => { suite.durationMs = 200 + index; });
  reseal(windows);
  const verifiedDarwin = Compare.validateLocalCertificate(darwin, "darwin fixture");
  const verifiedWindows = Compare.validateLocalCertificate(windows, "windows fixture");
  const payload = Compare.buildComparisonPayload(verifiedDarwin, verifiedWindows);
  assert.strictEqual(payload.comparisonStatus, Compare.COMPARISON_STATUS);
  assert.strictEqual(payload.scope.allOtherClaims, "OPEN_OR_UNCHANGED");
  assert.deepStrictEqual(payload.scope.claimsNotClosed, Compare.CLAIMS_NOT_CLOSED);
  assert.strictEqual(payload.claimBoundary.u2Decision, "NO_ACCEPTANCE_OR_REJECTION_CLAIM");
  assert.strictEqual(payload.historicalV1.classification, Release.HISTORICAL_V1_CLASSIFICATION);
  assert.doesNotThrow(() => Compare.validateComparisonArtifact(Compare.packageComparison(payload)));
}));

test("comparison rejects quick certificates, digest drift, suite drift, and coordinated claim promotion", () => withFixture((fixture) => {
  const darwinRecord = deepCertificate(fixture, "darwin");
  const darwin = darwinRecord.artifact;
  const windows = clone(darwin);
  windows.generatedAtUtc = "2026-08-30T20:00:00.000Z";
  windows.environment = fixtureEnvironment("win32");
  windows.certification.observedPlatform = "win32";
  reseal(windows);
  const verifiedDarwin = Compare.validateLocalCertificate(darwin, "darwin fixture");

  const quick = clone(windows);
  quick.verificationMode = "quick";
  quick.certification.verificationMode = "quick";
  quick.suites.deep = [];
  reseal(quick);
  assert.throws(() => Compare.validateLocalCertificate(quick, "quick fixture"), /deep/);

  const drifted = clone(windows);
  drifted.releaseDigests.registeredArtifacts[0].rawSha256 = "0".repeat(64);
  reseal(drifted);
  const verifiedDrift = Compare.validateLocalCertificate(drifted, "drift fixture");
  assert.throws(() => Compare.buildComparisonPayload(verifiedDarwin, verifiedDrift), /digest surface mismatch/);

  const suiteDrift = clone(windows);
  suiteDrift.suites.deep[0].args.push("--different-input");
  reseal(suiteDrift);
  assert.throws(() => Compare.validateLocalCertificate(suiteDrift, "suite drift fixture"), /exact registry-frozen evaluation-index validator/);

  const coordinatedExtraSuiteDarwin = clone(darwin);
  const extraSuite = clone(coordinatedExtraSuiteDarwin.suites.deep[0]);
  extraSuite.id = "coordinated-extra-evaluation-validator";
  extraSuite.coverage = "evaluation-index";
  coordinatedExtraSuiteDarwin.suites.deep.push(extraSuite);
  reseal(coordinatedExtraSuiteDarwin);
  assert.throws(() => Compare.validateLocalCertificate(coordinatedExtraSuiteDarwin, "extra suite fixture"), /dense array of length 2/);

  const coordinatedExtraArtifactDarwin = clone(darwin);
  const extraArtifact = clone(coordinatedExtraArtifactDarwin.releaseDigests.registeredArtifacts.find((entry) => entry.role === "screening-comparison"));
  extraArtifact.id = "coordinated-extra-screening-comparison";
  extraArtifact.path = "artifacts/global-geometry-ii/coordinated-extra-screening-comparison.json";
  coordinatedExtraArtifactDarwin.releaseDigests.registeredArtifacts.push(extraArtifact);
  reseal(coordinatedExtraArtifactDarwin);
  assert.throws(() => Compare.validateLocalCertificate(coordinatedExtraArtifactDarwin, "extra artifact fixture"), /exactly 1 for role screening-comparison/);

  const promoted = clone(windows);
  promoted.claimBoundary.u2Decision = "ACCEPT";
  promoted.certification.u2Decision = "ACCEPT";
  reseal(promoted);
  assert.throws(() => Compare.validateLocalCertificate(promoted, "promoted fixture"), /no-decision|boundary/);
}));

test("comparison artifact cannot be redigested to promote v1 or close scientific/physical claims", () => withFixture((fixture) => {
  const darwinRecord = deepCertificate(fixture, "darwin");
  const windows = clone(darwinRecord.artifact);
  windows.generatedAtUtc = "2026-08-30T20:00:00.000Z";
  windows.environment = fixtureEnvironment("win32");
  windows.certification.observedPlatform = "win32";
  reseal(windows);
  const payload = Compare.buildComparisonPayload(
    Compare.validateLocalCertificate(darwinRecord.artifact, "darwin"),
    Compare.validateLocalCertificate(windows, "windows")
  );
  const promoted = Compare.packageComparison(payload);
  delete promoted.contentAddress;
  promoted.historicalV1.classification = "CURRENT_RELEASE";
  promoted.scope.allOtherClaims = "CLOSED";
  promoted.contentAddress = Release.contentAddress(promoted);
  assert.throws(() => Compare.validateComparisonArtifact(promoted), /scope exceeds|historical/);
}));

const filter = process.env.GGII_RELEASE_V2_TEST_FILTER || "";
const selected = filter ? tests.filter((entry) => entry.name.toLowerCase().includes(filter.toLowerCase())) : tests;
if (filter && selected.length === 0) {
  process.stderr.write("No release-v2 tests match GGII_RELEASE_V2_TEST_FILTER=" + filter + "\n");
  process.exitCode = 1;
}

let passed = 0;
for (const entry of selected) {
  try {
    entry.body();
    passed += 1;
    process.stdout.write("ok " + passed + " - " + entry.name + "\n");
  } catch (error) {
    process.stderr.write("not ok - " + entry.name + "\n" + (error.stack || error.message) + "\n");
    process.exitCode = 1;
    break;
  }
}

if (!process.exitCode) {
  process.stdout.write("\n1.." + passed + "\nAll Global Geometry II release-v2 tests passed.\n");
}
