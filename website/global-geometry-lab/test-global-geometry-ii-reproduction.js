#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const G2 = require("./global-geometry-ii-core.js");
const Atlas = require("./global-geometry-ii-atlas.js");
const AtlasGenerator = require("./generate-global-geometry-ii-atlas.js");
const Release = require("./generate-global-geometry-ii-release.js");
const Reproduce = require("./reproduce-global-geometry-ii.js");

const tests = [];
function test(name, body) { tests.push({ name, body }); }
function clone(value) { return JSON.parse(JSON.stringify(value)); }

function rebindAtlasDerivedFields(payload) {
  const pilot = payload.pilot;
  pilot.resultDigest = G2.digestValue({
    schema: Atlas.SCHEMA,
    version: Atlas.VERSION,
    spec: pilot.spec,
    specDigestAlgorithm: G2.DIGEST_ALGORITHM,
    specDigest: pilot.specDigest,
    runs: pilot.runs,
    cells: pilot.cells
  });
  const manifest = clone(pilot.manifest);
  delete manifest.digest;
  delete manifest.digestAlgorithm;
  manifest.resultArtifacts = ["checksum:" + G2.DIGEST_ALGORITHM + ":" + pilot.resultDigest];
  pilot.manifest = G2.createRunManifest(manifest);
  const evidence = clone(pilot.evidence);
  delete evidence.digest;
  delete evidence.digestAlgorithm;
  evidence.id = "ggii.result.disk-pilot." + pilot.resultDigest;
  evidence.artifacts = [
    "manifest:" + pilot.manifest.digest,
    "result:" + G2.DIGEST_ALGORITHM + ":" + pilot.resultDigest
  ];
  evidence.result.resultDigest = pilot.resultDigest;
  pilot.evidence = G2.createEvidenceRecord(evidence);
  return payload;
}

test("atlas cross-platform policy freezes exactly eight internally validated derived strings", () => {
  assert.deepStrictEqual(Release.ATLAS_DERIVED_DIGEST_PATHS, [
    "root.pilot.evidence.artifacts[0]",
    "root.pilot.evidence.artifacts[1]",
    "root.pilot.evidence.digest",
    "root.pilot.evidence.id",
    "root.pilot.evidence.result.resultDigest",
    "root.pilot.manifest.digest",
    "root.pilot.manifest.resultArtifacts[0]",
    "root.pilot.resultDigest"
  ]);
  assert.strictEqual(new Set(Release.ATLAS_DERIVED_DIGEST_PATHS).size, 8);
  assert.strictEqual(Release.ATLAS_ABSOLUTE_TOLERANCE, 1e-12);
  assert.strictEqual(Release.ATLAS_RELATIVE_TOLERANCE, 1e-12);
  assert.ok(Release.ATLAS_EXACT_INTEGER_PATH_PATTERNS.includes("root.pilot.runs[*].measurements.transport.iterations"));
  assert.ok(!Release.ATLAS_EXACT_INTEGER_PATH_PATTERNS.includes("root.pilot.runs[*].measurements.exact.gaussBonnetResidual"));
});

test("atlas cross-platform policy accepts an internally valid sub-tolerance replay and reports maxima", () => {
  const committed = AtlasGenerator.buildPayload();
  const replay = clone(committed);
  const location = "root.pilot.runs[0].measurements.transport.maximumUpdate";
  replay.pilot.runs[0].measurements.transport.maximumUpdate += 1e-12;
  rebindAtlasDerivedFields(replay);
  assert.strictEqual(Atlas.validatePilotResult(committed.pilot).valid, true);
  assert.strictEqual(Atlas.validatePilotResult(replay.pilot).valid, true);
  const report = Release.compareAtlasCrossPlatformReplay(committed, replay);
  assert.strictEqual(report.valid, true, report.errors.join("; "));
  assert.strictEqual(report.pilotValidation.committed.valid, true);
  assert.strictEqual(report.pilotValidation.replay.valid, true);
  assert.deepStrictEqual(report.derivedFieldsComparedInternallyOnly, Release.ATLAS_DERIVED_DIGEST_PATHS);
  assert.strictEqual(report.summary.derivedStringsComparedInternallyOnly, 8);
  assert.strictEqual(report.summary.derivedStringDifferences, 8);
  assert.strictEqual(report.summary.continuousDifferences, 1);
  assert.strictEqual(report.summary.toleratedContinuousDifferences, 1);
  assert.strictEqual(report.summary.maxAbsoluteDifference.path, location);
  assert.ok(report.summary.maxAbsoluteDifference.value > 0);
  assert.ok(report.summary.maxToleranceFraction.value <= 1);
});

test("atlas cross-platform policy rejects over-tolerance noninteger drift even when both pilots validate", () => {
  const committed = AtlasGenerator.buildPayload();
  const replay = clone(committed);
  replay.pilot.runs[0].measurements.transport.maximumUpdate += 5e-12;
  rebindAtlasDerivedFields(replay);
  assert.strictEqual(Atlas.validatePilotResult(replay.pilot).valid, true);
  const report = Release.compareAtlasCrossPlatformReplay(committed, replay);
  assert.strictEqual(report.valid, false);
  assert.ok(report.errors.some((error) => /maximumUpdate continuous-number difference .* exceeds tolerance/.test(error)));
  assert.ok(report.summary.maxToleranceFraction.value > 1);
});

test("atlas cross-platform policy requires each pilot to pass its own closed validator", () => {
  const committed = AtlasGenerator.buildPayload();
  const replay = clone(committed);
  replay.pilot.runs[0].measurements.transport.maximumUpdate += 1e-12;
  const report = Release.compareAtlasCrossPlatformReplay(committed, replay);
  assert.strictEqual(report.valid, false);
  assert.strictEqual(report.pilotValidation.committed.valid, true);
  assert.strictEqual(report.pilotValidation.replay.valid, false);
  assert.ok(report.errors.some((error) => /replay pilot failed Atlas\.validatePilotResult/.test(error)));
});

test("atlas cross-platform policy keeps integers, ordinary strings, and unlisted digest strings exact", () => {
  const committed = AtlasGenerator.buildPayload();

  const integerReplay = clone(committed);
  integerReplay.pilot.runs[0].measurements.transport.iterations += 1;
  rebindAtlasDerivedFields(integerReplay);
  assert.strictEqual(Atlas.validatePilotResult(integerReplay.pilot).valid, true);
  const integerReport = Release.compareAtlasCrossPlatformReplay(committed, integerReplay);
  assert.strictEqual(integerReport.valid, false);
  assert.ok(integerReport.errors.some((error) => /iterations exact integer mismatch/.test(error)));

  const nonintegerCountReplay = clone(committed);
  nonintegerCountReplay.pilot.runs[0].measurements.transport.iterations += 1e-13;
  rebindAtlasDerivedFields(nonintegerCountReplay);
  const nonintegerCountReport = Release.compareAtlasCrossPlatformReplay(committed, nonintegerCountReplay);
  assert.strictEqual(nonintegerCountReport.valid, false);
  assert.ok(nonintegerCountReport.errors.some((error) => /iterations is a declared exact-integer field/.test(error)));

  const stringReplay = clone(committed);
  stringReplay.pilot.runs[0].measurements.transport.method += "-different";
  rebindAtlasDerivedFields(stringReplay);
  assert.strictEqual(Atlas.validatePilotResult(stringReplay.pilot).valid, true);
  const stringReport = Release.compareAtlasCrossPlatformReplay(committed, stringReplay);
  assert.strictEqual(stringReport.valid, false);
  assert.ok(stringReport.errors.some((error) => /transport\.method exact string mismatch/.test(error)));

  const digestReplay = clone(committed);
  assert.strictEqual(digestReplay.pilot.runs[0].structureDigest, digestReplay.pilot.runs[1].structureDigest);
  digestReplay.pilot.runs[0].structureDigest = "deadbeef";
  digestReplay.pilot.runs[1].structureDigest = "deadbeef";
  rebindAtlasDerivedFields(digestReplay);
  assert.strictEqual(Atlas.validatePilotResult(digestReplay.pilot).valid, true);
  const digestReport = Release.compareAtlasCrossPlatformReplay(committed, digestReplay);
  assert.strictEqual(digestReport.valid, false);
  assert.ok(digestReport.errors.some((error) => /runs\[0\]\.structureDigest exact string mismatch/.test(error)));
  assert.ok(digestReport.errors.some((error) => /runs\[1\]\.structureDigest exact string mismatch/.test(error)));
});

test("atlas numeric schema treats residual zero as continuous while keeping topological zero exact", () => {
  const committed = AtlasGenerator.buildPayload();
  const replay = clone(committed);
  const runIndex = replay.pilot.runs.findIndex((run) => run.measurements.exact.gaussBonnetResidual === 0);
  assert.ok(runIndex >= 0);
  replay.pilot.runs[runIndex].measurements.exact.gaussBonnetResidual = 1e-14;
  rebindAtlasDerivedFields(replay);
  assert.strictEqual(Atlas.validatePilotResult(replay.pilot).valid, true);
  const report = Release.compareAtlasCrossPlatformReplay(committed, replay);
  assert.strictEqual(report.valid, true, report.errors.join("; "));
  assert.strictEqual(report.summary.continuousDifferences, 1);

  const exactReplay = clone(committed);
  exactReplay.pilot.runs[0].measurements.exact.eulerPoincareResidual = 1e-14;
  rebindAtlasDerivedFields(exactReplay);
  const exactReport = Release.compareAtlasCrossPlatformReplay(committed, exactReplay);
  assert.strictEqual(exactReport.valid, false);
  assert.ok(exactReport.errors.some((error) => /eulerPoincareResidual is a declared exact-integer field/.test(error)));
});

test("atlas cross-platform policy keeps wrapper keys, types, array lengths, and required derived paths closed", () => {
  const committed = AtlasGenerator.buildPayload();

  const keyReplay = clone(committed);
  keyReplay.unexpected = true;
  assert.ok(Release.compareAtlasCrossPlatformReplay(committed, keyReplay).errors.some((error) => /root object key mismatch/.test(error)));

  const typeReplay = clone(committed);
  typeReplay.scientificScope.established = 17;
  assert.ok(Release.compareAtlasCrossPlatformReplay(committed, typeReplay).errors.some((error) => /scientificScope\.established type mismatch/.test(error)));

  const lengthReplay = clone(committed);
  lengthReplay.scientificScope.notEstablished.pop();
  assert.ok(Release.compareAtlasCrossPlatformReplay(committed, lengthReplay).errors.some((error) => /notEstablished array length mismatch/.test(error)));

  const missingDerivedReplay = clone(committed);
  delete missingDerivedReplay.pilot.evidence.digest;
  const missingReport = Release.compareAtlasCrossPlatformReplay(committed, missingDerivedReplay);
  assert.strictEqual(missingReport.valid, false);
  assert.ok(missingReport.errors.some((error) => /root\.pilot\.evidence\.digest required derived atlas string path is missing/.test(error)));
});

test("atlas cross-platform tolerance does not weaken exact replay for other scientific artifacts", () => {
  const calibration = Release.ARTIFACT_DEFINITIONS.find((definition) => definition.id === "calibration-v1");
  const exact = calibration.generator.buildPayload();
  assert.strictEqual(calibration.semanticValidator(exact).valid, true);
  const drifted = clone(exact);
  drifted.spectralCalibration.refinements[0].ringControl.profile[0].normalizedTrace += 1e-13;
  const report = calibration.semanticValidator(drifted);
  assert.strictEqual(report.valid, false);
  assert.deepStrictEqual(report.errors, ["calibration payload does not replay"]);
});

test("local replay observation supports a closed zero-drift fixture in the v2 certificate field", () => {
  assert.strictEqual(Reproduce.CERTIFICATE_SCHEMA, "ggii.local-reproduction-certificate/2");
  assert.strictEqual(Reproduce.VERIFIER_VERSION, "1.0.0-alpha.2");
  assert.strictEqual(Reproduce.LOCAL_REPLAY_OBSERVATIONS_SCHEMA, "ggii.local-replay-observations/1");
  const committed = AtlasGenerator.buildPayload();
  const observation = Reproduce.buildLocalReplayObservations({ committedPayload: committed, replayPayload: clone(committed) });
  assert.strictEqual(Reproduce.validateLocalReplayObservations(observation).valid, true);
  assert.deepStrictEqual(Object.keys(observation).sort(), ["atlas", "schema"]);
  assert.strictEqual(observation.atlas.policyId, "ggii.atlas-cross-platform-replay/1");
  assert.deepStrictEqual(observation.atlas.continuousTolerance, {
    absolute: 1e-12,
    relative: 1e-12,
    formula: "|a-b| <= 1e-12 + 1e-12*max(1,|a|,|b|)"
  });
  assert.deepStrictEqual(observation.atlas.pilotValidation, { committed: "PASS", replay: "PASS" });
  assert.ok(observation.atlas.exactComparisonCounts.objects > 0);
  assert.ok(observation.atlas.exactComparisonCounts.arrays > 0);
  assert.ok(observation.atlas.exactComparisonCounts.exactScalars > 0);
  assert.ok(observation.atlas.exactComparisonCounts.exactIntegerNumbers > 0);
  assert.ok(observation.atlas.continuousComparisonCounts.numbers > 0);
  assert.strictEqual(observation.atlas.continuousComparisonCounts.differences, 0);
  assert.strictEqual(observation.atlas.continuousComparisonCounts.toleratedDifferences, 0);
  assert.strictEqual(observation.atlas.mismatchCount, 0);
  assert.deepStrictEqual(observation.atlas.derivedFieldCounts, { comparedInternallyOnly: 8, differences: 0 });
  ["absoluteDifference", "scaledRelativeDifference", "toleranceFraction"].forEach((key) => {
    assert.deepStrictEqual(observation.atlas.maxima[key], { value: 0, path: null });
  });
});

test("local replay observation default builder captures the current platform rather than assuming zero drift", () => {
  const observation = Reproduce.buildLocalReplayObservations();
  assert.strictEqual(Reproduce.validateLocalReplayObservations(observation).valid, true);
  const atlas = observation.atlas;
  assert.strictEqual(atlas.mismatchCount, 0);
  assert.strictEqual(atlas.continuousComparisonCounts.differences, atlas.continuousComparisonCounts.toleratedDifferences);
  assert.ok(atlas.continuousComparisonCounts.differences >= 0);
  assert.strictEqual(atlas.derivedFieldCounts.comparedInternallyOnly, 8);
  assert.ok(atlas.derivedFieldCounts.differences >= 0 && atlas.derivedFieldCounts.differences <= 8);
  if (atlas.continuousComparisonCounts.differences === 0) {
    assert.deepStrictEqual(atlas.maxima.absoluteDifference, { value: 0, path: null });
    assert.deepStrictEqual(atlas.maxima.scaledRelativeDifference, { value: 0, path: null });
    assert.deepStrictEqual(atlas.maxima.toleranceFraction, { value: 0, path: null });
  } else {
    assert.ok(atlas.maxima.absoluteDifference.value > 0);
    assert.match(atlas.maxima.absoluteDifference.path, /^root\.pilot\./);
    assert.ok(atlas.maxima.toleranceFraction.value > 0 && atlas.maxima.toleranceFraction.value <= 1);
  }
});

test("local replay observation records actual tolerated drift, derived differences, and maximum paths", () => {
  const committed = AtlasGenerator.buildPayload();
  const replay = clone(committed);
  const location = "root.pilot.runs[0].measurements.transport.maximumUpdate";
  replay.pilot.runs[0].measurements.transport.maximumUpdate += 1e-12;
  rebindAtlasDerivedFields(replay);
  const observation = Reproduce.buildLocalReplayObservations({ committedPayload: committed, replayPayload: replay });
  assert.strictEqual(Reproduce.validateLocalReplayObservations(observation).valid, true);
  assert.deepStrictEqual(observation.atlas.pilotValidation, { committed: "PASS", replay: "PASS" });
  assert.deepStrictEqual(observation.atlas.continuousComparisonCounts, {
    numbers: observation.atlas.continuousComparisonCounts.numbers,
    differences: 1,
    toleratedDifferences: 1
  });
  assert.deepStrictEqual(observation.atlas.derivedFieldCounts, { comparedInternallyOnly: 8, differences: 8 });
  assert.strictEqual(observation.atlas.mismatchCount, 0);
  assert.strictEqual(observation.atlas.maxima.absoluteDifference.path, location);
  assert.strictEqual(observation.atlas.maxima.scaledRelativeDifference.path, location);
  assert.strictEqual(observation.atlas.maxima.toleranceFraction.path, location);
  assert.ok(observation.atlas.maxima.absoluteDifference.value > 0);
  assert.ok(observation.atlas.maxima.toleranceFraction.value > 0);
  assert.ok(observation.atlas.maxima.toleranceFraction.value <= 1);
});

test("local replay observation validator rejects open fields and nonpassing summaries", () => {
  const observation = Reproduce.buildLocalReplayObservations();
  const extra = clone(observation);
  extra.atlas.unregistered = true;
  assert.strictEqual(Reproduce.validateLocalReplayObservations(extra).valid, false);
  assert.ok(Reproduce.validateLocalReplayObservations(extra).errors.some((error) => /keys must be exactly/.test(error)));

  const mismatch = clone(observation);
  mismatch.atlas.mismatchCount = 1;
  assert.ok(Reproduce.validateLocalReplayObservations(mismatch).errors.some((error) => /mismatchCount must be zero/.test(error)));

  const failedPilot = clone(observation);
  failedPilot.atlas.pilotValidation.replay = "FAIL";
  assert.ok(Reproduce.validateLocalReplayObservations(failedPilot).errors.some((error) => /pilot validations must be PASS/.test(error)));

  const outOfTolerance = clone(observation);
  outOfTolerance.atlas.maxima.toleranceFraction = { value: 1.01, path: "root.pilot.example" };
  assert.ok(Reproduce.validateLocalReplayObservations(outOfTolerance).errors.some((error) => /may not exceed one/.test(error)));
});

test("reproduction CLI requires one explicit verify mode and parses certificate paths from repo root", () => {
  assert.throws(() => Reproduce.parseArgs([]), /--verify is required/);
  assert.throws(() => Reproduce.parseArgs(["--certificate", "x.json"]), /--verify is required/);
  assert.throws(() => Reproduce.parseArgs(["--verify", "--verify"]), /only once/);
  assert.throws(() => Reproduce.parseArgs(["--verify", "--unknown"]), /unknown/);
  assert.throws(() => Reproduce.parseArgs(["--verify", "--certificate"]), /requires/);
  assert.throws(() => Reproduce.parseArgs(["--verify", "--certificate", "a", "tail"]), /unknown|ambiguous/);
  assert.deepStrictEqual(Reproduce.parseArgs(["--verify"]), { verify: true, certificate: null });
  const parsed = Reproduce.parseArgs(["--certificate", "certificates/windows.json", "--verify"]);
  assert.strictEqual(parsed.certificate, path.join(Release.REPO_ROOT, "certificates/windows.json"));
});

test("release generator arguments are strict and independent of the process working directory", () => {
  const defaults = Release.parseOutputs([]);
  assert.strictEqual(defaults.manifest, path.join(Release.REPO_ROOT, "global_geometry_ii_reproducibility_manifest.json"));
  assert.strictEqual(defaults.index, path.join(Release.REPO_ROOT, "artifacts/global-geometry-ii/release-index-v1.json"));
  const explicit = Release.parseOutputs(["--index", "artifacts/global-geometry-ii/example-index.json", "--manifest", "example-manifest.json"]);
  assert.strictEqual(explicit.manifest, path.join(Release.REPO_ROOT, "example-manifest.json"));
  assert.strictEqual(explicit.index, path.join(Release.REPO_ROOT, "artifacts/global-geometry-ii/example-index.json"));
  assert.throws(() => Release.parseOutputs(["--manifest", "x.json"]), /exactly|together/);
  assert.throws(() => Release.parseOutputs(["--manifest", "x", "--manifest", "y"]), /only once/);
  assert.throws(() => Release.parseOutputs(["--other", "x", "--index", "y"]), /unknown/);
  assert.throws(() => Release.parseOutputs(["--manifest", "same", "--index", "same"]), /different/);
  assert.throws(() => Release.parseOutputs(["--manifest", path.parse(Release.REPO_ROOT).root + "outside-manifest.json", "--index", "inside-index.json"]), /outside the repository/);
  assert.throws(() => Release.generate({
    manifest: path.join(Release.REPO_ROOT, "website/global-geometry-lab/global-geometry-ii-core.js"),
    index: path.join(Release.REPO_ROOT, "unused-release-index.json")
  }), /may not overwrite an input/);
});

test("source manifest selection is closed, sorted, relative, and byte-addressed", () => {
  const paths = Release.collectSourcePaths();
  assert.ok(paths.length >= 20);
  assert.deepStrictEqual(paths, paths.slice().sort());
  assert.strictEqual(new Set(paths).size, paths.length);
  [
    "GLOBAL_GEOMETRY_II_FOUNDATIONS.md",
    ".github/workflows/tests.yml",
    "artifacts/global-geometry-ii/fabrication/fabrication-manifest.json",
    "artifacts/global-geometry-ii/fabrication/validate-fabrication.js",
    "website/global-geometry-lab/global-geometry-core.js",
    "website/global-geometry-lab/reproduce-global-geometry-ii.js",
    "website/global-geometry-lab/reproduce-global-geometry-ii.ps1",
    "website/global-geometry-lab/test-global-geometry-ii-reproduction.js"
  ].forEach((required) => assert.ok(paths.includes(required), "missing source " + required));
  Release.sourceEntries().forEach((entry) => {
    assert.ok(!path.isAbsolute(entry.path));
    assert.match(entry.sha256, /^[0-9a-f]{64}$/);
    assert.strictEqual(entry.bytes, fs.statSync(path.join(Release.REPO_ROOT, entry.path)).size);
  });
});

test("fabrication resources are internally addressed while physical validation stays NOT_RUN", () => {
  const resource = Release.verifyFabricationPackage();
  assert.strictEqual(resource.id, "programmable-sheet-fabrication-package-v1");
  assert.strictEqual(resource.files.length, 10);
  assert.ok(resource.files.some((entry) => entry.path === "artifacts/global-geometry-ii/fabrication/physical-preflight-v1.json"));
  assert.ok(resource.files.some((entry) => entry.path === "website/global-geometry-lab/test-global-geometry-ii-physical-preflight.js"));
  assert.strictEqual(resource.validation, "INTERNAL_HASHES_PASS");
  assert.strictEqual(resource.physicalValidation, "NOT_RUN");
  assert.strictEqual(resource.hardwareAuthorization, false);
  assert.strictEqual(resource.purchaseAuthorization, false);
  assert.match(resource.rawSha256, /^[0-9a-f]{64}$/);
  assert.match(resource.semanticAddress.digest, /^[0-9a-f]{64}$/);
});

test("all four scientific artifacts pass both SHA-256 and semantic replay", () => {
  const entries = Release.scientificArtifactEntries();
  assert.deepStrictEqual(entries.map((entry) => entry.id), [
    "calibration-v1",
    "atlas-pilot-v1",
    "inverse-certificates-v1",
    "sheet-hil-v1"
  ]);
  entries.forEach((entry) => {
    assert.strictEqual(entry.semanticReplay, "PASS");
    assert.match(entry.rawSha256, /^[0-9a-f]{64}$/);
    assert.strictEqual(entry.semanticAddress.algorithm, "sha256");
    assert.match(entry.semanticAddress.digest, /^[0-9a-f]{64}$/);
  });
});

test("metadata delegation: manifest deterministically points to the external comparison record", () => {
  const first = Release.buildManifestPayload();
  const second = Release.buildManifestPayload();
  assert.strictEqual(Release.canonicalStringify(first), Release.canonicalStringify(second));
  assert.strictEqual(first.schema, Release.MANIFEST_SCHEMA);
  assert.strictEqual(first.execution.suites.length, Release.SUITES.length);
  assert.strictEqual(first.sourceManifest.count, first.sourceManifest.entries.length);
  assert.strictEqual(first.certificationPolicy.crossPlatformEqualityClaim, "NOT_MADE");
  assert.strictEqual(first.certificationPolicy.windowsCertificate, "REQUIRED_EXTERNAL_INPUT_NOT_BUNDLED_OR_SIMULATED");
  assert.strictEqual(first.certificationPolicy.externalComparisonRecord, Release.EXTERNAL_COMPARISON_RECORD);
  assert.strictEqual(first.certificationPolicy.externalComparisonRecord, "artifacts/global-geometry-ii/certificates/macos-windows-comparison-v1.json");
  assert.strictEqual(first.certificationPolicy.releaseGate, "STATUS_DELEGATED_TO_EXTERNAL_COMPARISON_RECORD");
  const address = Release.contentAddress(first);
  assert.strictEqual(address.algorithm, "sha256");
  assert.strictEqual(address.canonicalization, Release.ADDRESS_CANONICALIZATION);
  assert.match(address.digest, /^[0-9a-f]{64}$/);
});

test("metadata delegation: release index uses a one-way hash topology and delegates external status", () => {
  const payload = Release.buildManifestPayload();
  const manifest = Release.packageAddressed(payload);
  const index = Release.buildIndexPayload(Release.DEFAULT_MANIFEST, manifest);
  assert.strictEqual(index.schema, Release.INDEX_SCHEMA);
  assert.deepStrictEqual(index.manifest.contentAddress, manifest.contentAddress);
  assert.ok(!Object.prototype.hasOwnProperty.call(payload, "releaseIndex"));
  assert.ok(!Object.prototype.hasOwnProperty.call(index, "contentAddress"));
  assert.match(index.hashTopology, /does not hash the index/);
  assert.strictEqual(index.certificationStatus.crossPlatformEqualityClaim, "NOT_MADE");
  assert.strictEqual(index.certificationStatus.windowsCertificate, "EXTERNAL_NOT_BUNDLED_IN_INDEX");
  assert.strictEqual(index.certificationStatus.externalComparisonRecord, Release.EXTERNAL_COMPARISON_RECORD);
  assert.strictEqual(index.certificationStatus.releaseGate, "STATUS_DELEGATED_TO_EXTERNAL_COMPARISON_RECORD");
});

test("metadata delegation: generator CLI summary delegates status without a time-sensitive absence claim", () => {
  const summary = Release.generatorCliSummary({
    manifest: { path: "/manifest", address: { digest: "a".repeat(64) } },
    index: { path: "/index", address: { digest: "b".repeat(64) } }
  });
  assert.strictEqual(summary.crossPlatformEqualityClaim, "NOT_MADE");
  assert.strictEqual(summary.windowsCertificate, "REQUIRED_EXTERNAL_INPUT_NOT_BUNDLED_OR_SIMULATED");
  assert.strictEqual(summary.externalComparisonRecord, Release.EXTERNAL_COMPARISON_RECORD);
  assert.strictEqual(summary.releaseGate, "STATUS_DELEGATED_TO_EXTERNAL_COMPARISON_RECORD");
  assert.ok(!/ABSENT/.test(Release.canonicalStringify(summary)));
});

test("metadata delegation: source discovery rejects AppleDouble platform metadata by name", () => {
  assert.doesNotThrow(() => Release.assertPortableSourceEntryName("ordinary.js", "/source/ordinary.js"));
  assert.throws(
    () => Release.assertPortableSourceEntryName("._ordinary.js", "/source/._ordinary.js"),
    /AppleDouble\/platform-metadata source entry/
  );
});

test("canonical content addresses detect nested changes and reject non-JSON inputs", () => {
  const original = { z: [1, { a: "x" }], a: true };
  const reordered = { a: true, z: [1, { a: "x" }] };
  const changed = { a: true, z: [1, { a: "y" }] };
  assert.deepStrictEqual(Release.contentAddress(original), Release.contentAddress(reordered));
  assert.notStrictEqual(Release.contentAddress(original).digest, Release.contentAddress(changed).digest);
  assert.throws(() => Release.canonicalStringify({ value: Infinity }), /non-finite/);
  const sparse = [];
  sparse.length = 1;
  assert.throws(() => Release.canonicalStringify(sparse), /dense/);
});

test("metadata delegation: local certificate language remains NOT_MADE and open", () => {
  const darwin = Reproduce.certificationRecord("darwin");
  const windows = Reproduce.certificationRecord("win32");
  const linux = Reproduce.certificationRecord("linux");
  [darwin, windows, linux].forEach((record) => {
    assert.strictEqual(record.crossPlatformEqualityClaim, "NOT_MADE");
    assert.match(record.releaseGate, /^OPEN_/);
  });
  assert.strictEqual(darwin.windowsCertificate, "ABSENT_REQUIRED_INPUT_NOT_SIMULATED");
  assert.match(windows.windowsCertificate, /LOCAL_WINDOWS_CANDIDATE/);
  assert.strictEqual(linux.observedPlatformIsRequiredClass, false);
});

test("repository verifier closes metadata and suite identities with a non-executing test runner", () => {
  const seen = [];
  const result = Reproduce.verifyRepository({
    environment: {
      platform: "darwin",
      architecture: "test",
      operatingSystemRelease: "test",
      endianness: "LE",
      nodeVersion: "test",
      v8Version: "test",
      uvVersion: "test",
      logicalCpuCount: 1,
      cpuModel: "test",
      totalMemoryBytes: 1
    },
    runSuite(suite) {
      seen.push(suite.id);
      return {
        id: suite.id,
        path: suite.path,
        status: "PASS",
        exitCode: 0,
        durationMs: 0,
        stdoutBytes: 0,
        stdoutSha256: Release.sha256Bytes(Buffer.alloc(0)),
        stderrBytes: 0,
        stderrSha256: Release.sha256Bytes(Buffer.alloc(0))
      };
    }
  });
  assert.deepStrictEqual(seen, Release.SUITES.map((suite) => suite.id));
  assert.strictEqual(result.verificationStatus, "PASS");
  assert.strictEqual(result.readOnlyVerification, "PASS_SOURCE_ARTIFACT_AND_RELEASE_SURFACE_UNCHANGED");
  assert.strictEqual(result.suites.length, Release.SUITES.length);
  assert.strictEqual(result.scientificDigests.artifacts.length, 4);
  assert.strictEqual(result.scientificDigests.reproductionResources.length, 1);
  assert.strictEqual(Object.prototype.hasOwnProperty.call(result.scientificDigests, "localReplayObservations"), false);
  assert.strictEqual(Reproduce.validateLocalReplayObservations(result.localReplayObservations).valid, true);
  assert.strictEqual(result.certification.crossPlatformEqualityClaim, "NOT_MADE");
});

test("read-only surface comparison detects a changed digest", () => {
  const before = [{ path: "x", sha256: "a", bytes: 1, mode: 420 }];
  const after = [{ path: "x", sha256: "b", bytes: 1, mode: 420 }];
  assert.doesNotThrow(() => Reproduce.assertUnchanged(before, JSON.parse(JSON.stringify(before))));
  assert.throws(() => Reproduce.assertUnchanged(before, after), /changed during read-only verification/);
});

const requestedFilter = process.env.GGII_REPRO_TEST_FILTER || "";
const selectedTests = requestedFilter
  ? tests.filter((entry) => entry.name.toLowerCase().includes(requestedFilter.toLowerCase()))
  : tests;
if (requestedFilter && selectedTests.length === 0) {
  process.stderr.write("No reproduction tests match GGII_REPRO_TEST_FILTER=" + requestedFilter + "\n");
  process.exitCode = 1;
}

let passed = 0;
for (const entry of selectedTests) {
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
  process.stdout.write("\n1.." + passed + "\nAll selected Global Geometry II reproduction tests passed.\n");
}
