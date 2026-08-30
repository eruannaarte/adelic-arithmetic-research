#!/usr/bin/env node
"use strict";

/*
 * Global Geometry II U2 evaluation index v2.
 *
 * This is a read-only, outcome-bearing projection builder. It never upgrades
 * the frozen screening to decision evidence and never converts the strict
 * partial checkpoint into a complete confirmatory campaign. Every compact
 * claim below is rebuilt from exact, content-addressed source artifacts.
 */

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const Strict = require("./global-geometry-ii-u2.js");
const Screen = require("./global-geometry-ii-u2-screening-execution-v3.js");
const ScreenRunner = require("./run-global-geometry-ii-u2-screening-execution-v3.js");

const ROOT = path.resolve(__dirname, "../..");
const OUTPUT_DIRECTORY = "artifacts/global-geometry-ii/u2/evaluation-v2";
const OUTPUTS = Object.freeze({
  macStrictCompact: OUTPUT_DIRECTORY + "/strict-partial-macos-compact-v1.json",
  windowsStrictCompact: OUTPUT_DIRECTORY + "/strict-partial-windows-compact-v1.json",
  strictComparison: OUTPUT_DIRECTORY + "/strict-cross-comparison-v1.json",
  screeningComparison: OUTPUT_DIRECTORY + "/screening-v3-cross-comparison-v1.json",
  evaluationIndex: OUTPUT_DIRECTORY + "/evaluation-index-v2.json"
});
const INPUTS = Object.freeze({
  strict: {
    macos: {
      normalization: "artifacts/global-geometry-ii/u2/strict-partial/macos/u2-normalization-v2.json",
      campaign: "artifacts/global-geometry-ii/u2/strict-partial/macos/u2-campaign-partial-v2.json",
      certificate: "artifacts/global-geometry-ii/u2/strict-partial/macos/u2-strict-partial-macos-validation-certificate-v2.json"
    },
    windows: {
      normalization: "artifacts/global-geometry-ii/u2/strict-partial/windows/u2-normalization-v2.json",
      campaign: "artifacts/global-geometry-ii/u2/strict-partial/windows/u2-campaign-partial-v2.json",
      certificate: "artifacts/global-geometry-ii/u2/strict-partial/windows/u2-strict-partial-windows-certificate-v1.json"
    }
  },
  screening: {
    macos: "artifacts/global-geometry-ii/u2/screening/screening-v3/macos",
    windows: "artifacts/global-geometry-ii/u2/screening/screening-v3/windows"
  },
  screeningCertificates: {
    macos: "artifacts/global-geometry-ii/u2/screening/screening-v3/macos/screening-v3-macos-validation-certificate-v2.json",
    windows: "artifacts/global-geometry-ii/u2/screening/screening-v3/windows/screening-v3-windows-validation-certificate-v2.json"
  },
  archives: {
    strictMacos: OUTPUT_DIRECTORY + "/strict-partial-macos-campaign-v2.json.gz",
    strictWindows: OUTPUT_DIRECTORY + "/strict-partial-windows-campaign-v2.json.gz",
    screeningMacos: OUTPUT_DIRECTORY + "/screening-v3-macos-raw.jsonl.gz",
    screeningWindows: OUTPUT_DIRECTORY + "/screening-v3-windows-raw.jsonl.gz"
  }
});

const STRICT_PROTOCOL_KEYS = Object.freeze(["schema", "engineVersion", "experimentId", "preregistrationCommit", "finalSourceCommit", "sourceBoundary", "manifestBinding", "constructionContract", "constructionContractDigest", "normalizationBinding", "randomness"]);
const STRICT_SCIENTIFIC_KEYS = Object.freeze(["exactGateOne", "positiveRuns", "cells", "primaryControls", "gateResults", "counts", "conclusion", "evidenceBoundary"]);
const STRICT_CRITICAL_KEYS = Object.freeze(["sourceBoundary", "normalizationBinding", "counts", "cells", "gateResults", "conclusion", "evidenceBoundary"]);
const SCREEN_SCIENTIFIC_KEYS = Object.freeze(["schema", "screeningId", "manifestDigest", "preregistrationCommit", "outcome", "census", "gates", "positiveCells", "controlCells", "failureLedger", "randomnessAudit", "telemetryBinding", "screeningVersion", "implementation", "semanticBaseSupplementDigest", "semanticBaseImplementation", "semanticBase", "executionSupplementDigest", "semanticAmendment"]);
const STRICT_NATIVE_CERTIFICATE_SCHEMA = "gg.u2.evaluation.native-strict-validation-certificate/2";
const SCREEN_NATIVE_CERTIFICATE_SCHEMA = "gg.u2.evaluation.native-screening-v3-validation-certificate/2";
const SCREEN_NATIVE_CERTIFICATE_SOURCE_BINDINGS = Object.freeze({
  certificateBuilder: { path: "website/global-geometry-lab/generate-global-geometry-ii-u2-native-validation-certificates-v2.js", semantic: false },
  evaluationBuilder: { path: "website/global-geometry-lab/generate-global-geometry-ii-u2-evaluation-index-v2.js", semantic: false },
  strictValidator: { path: "website/global-geometry-lab/global-geometry-ii-u2.js", semantic: false },
  strictSourceBoundaryValidator: { path: "website/global-geometry-lab/global-geometry-ii-u2-source-boundary.js", semantic: false },
  screeningSemanticBase: { path: "website/global-geometry-lab/global-geometry-ii-u2-screening-v2.js", semantic: false },
  screeningV3Adapter: { path: "website/global-geometry-lab/global-geometry-ii-u2-screening-execution-v3.js", semantic: false },
  screeningV3Runner: { path: "website/global-geometry-lab/run-global-geometry-ii-u2-screening-execution-v3.js", semantic: false },
  screeningSourceBoundary: { path: "artifacts/global-geometry-ii/u2/screening/screening-v3/source-boundary-v3.json", semantic: true }
});

function clone(value) { return JSON.parse(JSON.stringify(value)); }
function canonicalStringify(value) {
  if (value === null || typeof value === "string" || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "number") {
    if (!Number.isFinite(value) || Object.is(value, -0)) throw new Error("invalid canonical number");
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return "[" + value.map(canonicalStringify).join(",") + "]";
  if (!value || typeof value !== "object" || Object.getPrototypeOf(value) !== Object.prototype) throw new Error("canonical values must be plain JSON");
  return "{" + Object.keys(value).sort().map(function (key) { return JSON.stringify(key) + ":" + canonicalStringify(value[key]); }).join(",") + "}";
}
function sha256Bytes(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function sha256JSON(value) { return sha256Bytes(Buffer.from(canonicalStringify(value), "utf8")); }
function contentAddress(payload) { const canonical = canonicalStringify(payload); return { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest: sha256Bytes(Buffer.from(canonical, "utf8")), canonicalBytes: Buffer.byteLength(canonical, "utf8") }; }
function addressed(payload) { return Object.assign({}, payload, { contentAddress: contentAddress(payload) }); }
function serializeArtifact(artifact) { return Buffer.from(JSON.stringify(artifact, null, 2) + "\n", "utf8"); }
function resolve(relative) { return path.join(ROOT, relative); }

function validateContentAddress(artifact) {
  if (!artifact || !artifact.contentAddress) return { valid: false, errors: ["contentAddress missing"] };
  const payload = clone(artifact), supplied = payload.contentAddress; delete payload.contentAddress;
  const expected = contentAddress(payload), valid = canonicalStringify(supplied) === canonicalStringify(expected);
  return { valid: valid, errors: valid ? [] : ["contentAddress mismatch"] };
}

function bindBytes(relativePath, options) {
  options = options || {};
  const bytes = fs.readFileSync(resolve(relativePath)), binding = { path: relativePath, bytes: bytes.length, sha256: sha256Bytes(bytes) };
  let artifact = null;
  if (options.json !== false) {
    artifact = JSON.parse(bytes.toString("utf8"));
    const report = validateContentAddress(artifact);
    if (options.requireContentAddress !== false && !report.valid) throw new Error(relativePath + " invalid content address: " + report.errors.join("; "));
    binding.semanticDigest = artifact.contentAddress ? artifact.contentAddress.digest : null;
  }
  return { bytes: bytes, artifact: artifact, binding: binding };
}

function certificateStyleBinding(loaded) {
  return Object.assign({}, loaded.binding, { semanticDigest: loaded.binding.semanticDigest === undefined ? null : loaded.binding.semanticDigest });
}

function validateCertificateSourceBindings(certificate) {
  const errors = [], sourceKeys = Object.keys(SCREEN_NATIVE_CERTIFICATE_SOURCE_BINDINGS).sort();
  try {
    if (!certificate.sourceBindings || canonicalStringify(Object.keys(certificate.sourceBindings).sort()) !== canonicalStringify(sourceKeys)) errors.push("native certificate source-binding census mismatch");
    sourceKeys.forEach(function (key) {
      const spec = SCREEN_NATIVE_CERTIFICATE_SOURCE_BINDINGS[key], observed = certificateStyleBinding(bindBytes(spec.path, { json: spec.semantic }));
      if (!certificate.sourceBindings || canonicalStringify(certificate.sourceBindings[key]) !== canonicalStringify(observed)) errors.push("native certificate source binding mismatch: " + key);
    });
  } catch (error) { errors.push(error.message); }
  return errors;
}

function loadArchivedSource(archivePath, logicalSourcePath, options) {
  options = options || {};
  const archiveBytes = fs.readFileSync(resolve(archivePath)), bytes = zlib.gunzipSync(archiveBytes), binding = { path: logicalSourcePath, bytes: bytes.length, sha256: sha256Bytes(bytes) };
  let artifact = null;
  if (options.json !== false) {
    artifact = JSON.parse(bytes.toString("utf8"));
    const report = validateContentAddress(artifact);
    if (!report.valid) throw new Error(archivePath + " decompressed JSON invalid: " + report.errors.join("; "));
    binding.semanticDigest = artifact.contentAddress.digest;
  }
  return { archivePath: archivePath, archiveBytes: archiveBytes, bytes: bytes, artifact: artifact, binding: binding };
}

function select(object, keys) { const projection = {}; keys.forEach(function (key) { projection[key] = object[key]; }); return projection; }
function projection(keys, object) { return { keys: keys.slice(), digest: sha256JSON(select(object, keys)) }; }
function histogram(values) { const counts = {}; values.forEach(function (value) { const key = String(value); counts[key] = (counts[key] || 0) + 1; }); return Object.fromEntries(Object.keys(counts).sort().map(function (key) { return [key, counts[key]]; })); }
function sum(values) { return values.reduce(function (total, value) { return total + value; }, 0); }

function diagnosticTransform(value, pathParts) {
  pathParts = pathParts || [];
  if (typeof value === "number") {
    if (!Number.isFinite(value)) throw new Error("diagnostic projection contains a nonfinite number");
    const rounded = Math.round(value * 1e12) / 1e12;
    return Object.is(rounded, -0) ? 0 : rounded;
  }
  if (Array.isArray(value)) return value.map(function (item, index) { return diagnosticTransform(item, pathParts.concat(index)); });
  if (value && typeof value === "object") {
    const output = {};
    Object.keys(value).forEach(function (key) {
      if (key === "digest" && pathParts.length === 3 && pathParts[0] === "positiveRuns" && Number.isInteger(pathParts[1]) && pathParts[2] === "conductance") return;
      output[key] = diagnosticTransform(value[key], pathParts.concat(key));
    });
    return output;
  }
  return value;
}

function strictDiagnosticProjection(campaign) {
  const scientific = select(campaign, STRICT_SCIENTIFIC_KEYS), transformed = diagnosticTransform(scientific, []);
  return {
    scientificKeys: STRICT_SCIENTIFIC_KEYS.slice(),
    tolerance: 1e-12,
    policy: "omit only positiveRuns[].conductance.digest; round every finite exposed number to nearest 1e-12; normalize -0 to 0",
    digest: sha256JSON(transformed),
    decisionAuthority: "NONE"
  };
}

function strictControlCensus(campaign) {
  return campaign.primaryControls.summaries.map(function (summary) {
    const records = campaign.primaryControls.records.filter(function (record) { return record.controlId === summary.id; });
    return {
      id: summary.id,
      recordCount: records.length,
      constructedCount: records.filter(function (record) { return record.constructed; }).length,
      countsForGate7Count: records.filter(function (record) { return record.countsForGate7; }).length,
      measurementStatuses: histogram(records.map(function (record) { return record.measurement && record.measurement.status; })),
      summaryCountsForGate7: summary.countsForGate7,
      summaryStatus: summary.status
    };
  });
}

function strictFiniteFindings(campaign) {
  const decisionCells = campaign.cells.filter(function (cell) { return cell.linearSize === 81 || cell.linearSize === 120; }), intervals = decisionCells.map(function (cell) { return cell.volumeExponentInterval; }), exact = campaign.exactGateOne;
  const lower = intervals.map(function (interval) { return interval.lower; }).filter(function (value) { return value !== null; }), upper = intervals.map(function (interval) { return interval.upper; }).filter(function (value) { return value !== null; });
  return {
    gateOne: {
      status: exact.status,
      periodicCertificateCount: exact.densePeriodic.length,
      exactSmallDiskCertificateCount: exact.exactSmallDisks.length,
      maximumSpectralAbsoluteDiscrepancy: Math.max.apply(null, exact.densePeriodic.map(function (row) { return Math.abs(row.maxAbsolute); })),
      maximumAbsoluteGaussBonnetResidual: Math.max.apply(null, exact.exactSmallDisks.map(function (row) { return Math.abs(row.gaussBonnetResidual); }))
    },
    descriptiveVolume: {
      decisionCellCount: decisionCells.length,
      successfulRunCount: sum(decisionCells.map(function (cell) { return cell.successfulVolumeRuns; })),
      everyIntervalStrictlyInsidePreregisteredMargin: decisionCells.length === 32 && intervals.every(function (interval) { return interval.count === 32 && interval.lower > 1.8 && interval.upper < 2.2; }),
      intervalEnvelope: { lower: Math.min.apply(null, lower), upper: Math.max.apply(null, upper) },
      decisionStatus: "UNRESOLVED",
      reason: "descriptive intervals lack the preregistered hierarchical construction/root-block/probe reselection"
    }
  };
}

function strictFailureCensus(campaign) {
  return {
    positiveDiagnosticStatus: histogram(campaign.positiveRuns.map(function (run) { return run.diagnostics.status; })),
    positiveFailureCodes: histogram(campaign.positiveRuns.flatMap(function (run) { return run.diagnostics.failureCodes; })),
    spectralPrimaryStatus: histogram(campaign.positiveRuns.map(function (run) { return run.observables.spectralPrimary.status; })),
    volumeStatus: histogram(campaign.positiveRuns.map(function (run) { return run.observables.volume.status; })),
    alternateWalkStatus: histogram(campaign.positiveRuns.map(function (run) { return run.observables.walkAlternate.status; })),
    transportStatus: histogram(campaign.positiveRuns.map(function (run) { return run.observables.transport.status; }))
  };
}

function validateStrictHostCertificateLoaded(platformLabel, input, certificateLoaded, normalizationLoaded, campaignLoaded) {
  const errors = [], certificate = certificateLoaded && certificateLoaded.artifact, normalization = normalizationLoaded && normalizationLoaded.artifact, campaign = campaignLoaded && campaignLoaded.artifact;
  try {
    if (!certificateLoaded || !certificate) throw new Error(platformLabel + " strict native certificate missing");
    errors.push.apply(errors, validateContentAddress(certificate).errors);
    if (certificateLoaded.binding.path !== input.certificate) errors.push("strict native certificate path mismatch");
    if (platformLabel === "macos") {
      if (certificate.schema !== STRICT_NATIVE_CERTIFICATE_SCHEMA || !certificate.environment || certificate.environment.platformLabel !== "macos" || certificate.environment.platform !== "darwin") errors.push("Mac strict native certificate identity mismatch");
      if (!certificate.invocation || certificate.invocation.executable !== "node" || Object.prototype.hasOwnProperty.call(certificate.invocation, "executablePath") || !Array.isArray(certificate.invocation.execArgv) || certificate.invocation.script !== "website/global-geometry-lab/generate-global-geometry-ii-u2-native-validation-certificates-v2.js" || certificate.invocation.mode !== "--write-native-all" || canonicalStringify(certificate.invocation.argv) !== canonicalStringify([certificate.invocation.script, certificate.invocation.mode]) || certificate.command !== certificate.invocation.command || canonicalStringify(certificate.environment.execArgv) !== canonicalStringify(certificate.invocation.execArgv)) errors.push("Mac strict native certificate invocation metadata mismatch");
      if (canonicalStringify(certificate.artifactSourceBoundary) !== canonicalStringify(campaign.sourceBoundary)) errors.push("Mac strict native certificate source-boundary mismatch");
      const expectedArtifacts = { normalization: certificateStyleBinding(normalizationLoaded), campaign: certificateStyleBinding(campaignLoaded), priorHostCertificate: null };
      if (canonicalStringify(certificate.artifacts) !== canonicalStringify(expectedArtifacts)) errors.push("Mac strict native certificate artifact bindings mismatch");
      errors.push.apply(errors, validateCertificateSourceBindings(certificate));
      if (!certificate.validation || !certificate.validation.normalization || certificate.validation.normalization.status !== "PASS_NATIVE" || certificate.validation.normalization.recordsRemeasured !== 384 || !certificate.validation.campaign || certificate.validation.campaign.status !== "PASS_NATIVE" || certificate.validation.campaign.positiveRecordsRemeasured !== 3072 || certificate.validation.campaign.controlRecordsRemeasured !== 768 || certificate.validation.campaign.calibrationRecordsRemeasured !== 384 || certificate.validation.conclusion !== campaign.conclusion.status) errors.push("Mac strict native certificate full-census validation mismatch");
      if (!certificate.outcome || certificate.outcome.u2Status !== "UNRESOLVED" || certificate.outcome.acceptanceAllowed || certificate.outcome.rejectionClaimed || certificate.outcome.decisionAuthority !== "NONE") errors.push("Mac strict native certificate is not fail-closed");
      if (!certificate.timing || !(certificate.timing.elapsedMilliseconds >= 0) || Number.isNaN(Date.parse(certificate.timing.startedAt)) || Number.isNaN(Date.parse(certificate.timing.completedAt))) errors.push("Mac strict native certificate timing invalid");
    } else if (platformLabel === "windows") {
      if (certificate.schema !== "gg.u2.strict-partial.windows-run-certificate/1") errors.push("Windows strict native certificate schema mismatch");
      if (!certificate.result || certificate.result.normalizationValid !== true || certificate.result.campaignValid !== true || certificate.result.u2Status !== "UNRESOLVED" || certificate.result.decisionAuthority !== "STRICT_PARTIAL_ONLY") errors.push("Windows strict native certificate result mismatch");
      if (!certificate.stages || !certificate.stages.calibration || !certificate.stages.campaign || certificate.stages.calibration.artifact.bytes !== normalizationLoaded.binding.bytes || certificate.stages.calibration.artifact.sha256 !== normalizationLoaded.binding.sha256 || certificate.stages.calibration.artifact.semanticDigest !== normalization.contentAddress.digest || certificate.stages.campaign.artifact.bytes !== campaignLoaded.binding.bytes || certificate.stages.campaign.artifact.sha256 !== campaignLoaded.binding.sha256 || certificate.stages.campaign.artifact.semanticDigest !== campaign.contentAddress.digest) errors.push("Windows strict native certificate artifact bindings mismatch");
    } else errors.push("unsupported strict native certificate platform");
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

function buildStrictCompactFromLoaded(platformLabel, input, normalizationLoaded, campaignLoaded, certificateLoaded, options) {
  options = options || {};
  if (!input || !input.normalization || !input.campaign || !normalizationLoaded || !campaignLoaded) throw new Error("strict compact requires normalization and campaign inputs");
  const normalization = normalizationLoaded.artifact, campaign = campaignLoaded.artifact;
  if (normalization.schema !== Strict.CALIBRATION_SCHEMA || campaign.schema !== Strict.RESULT_SCHEMA) throw new Error(platformLabel + " strict schema mismatch");
  if (canonicalStringify(campaign.normalizationBinding) !== canonicalStringify(normalization.contentAddress)) throw new Error(platformLabel + " campaign normalization binding mismatch");
  if (canonicalStringify(campaign.sourceBoundary) !== canonicalStringify(normalization.sourceBoundary)) throw new Error(platformLabel + " strict source-boundary mismatch");
  if (!Array.isArray(normalization.cells) || normalization.cells.length !== 16 || sum(normalization.cells.map(function (cell) { return cell.records.length; })) !== 384) throw new Error(platformLabel + " normalization census mismatch");
  if (!Array.isArray(campaign.positiveRuns) || campaign.positiveRuns.length !== 3072 || !campaign.primaryControls || campaign.primaryControls.records.length !== 768 || campaign.cells.length !== 96) throw new Error(platformLabel + " campaign census mismatch");
  const derivedGates = Strict.deriveGates(campaign.exactGateOne, campaign.cells, campaign.primaryControls, "NOT_RUN"), derivedConclusion = Strict.deriveConclusion(derivedGates);
  if (canonicalStringify(campaign.gateResults) !== canonicalStringify(derivedGates) || canonicalStringify(campaign.conclusion) !== canonicalStringify(derivedConclusion)) throw new Error(platformLabel + " gate/conclusion ledger does not replay");
  const calibrationReport = Strict.validateCalibration(normalization);
  if (!calibrationReport.valid) throw new Error(platformLabel + " normalization replay failed: " + calibrationReport.errors.join("; "));
  if (input.certificate && options.nativeCertificateRequired !== false && !certificateLoaded) throw new Error(platformLabel + " strict compact requires its native validation certificate");
  if (certificateLoaded) {
    const certificateReport = validateStrictHostCertificateLoaded(platformLabel, input, certificateLoaded, normalizationLoaded, campaignLoaded);
    if (!certificateReport.valid) throw new Error(platformLabel + " strict native certificate invalid: " + certificateReport.errors.join("; "));
  }
  const certificate = certificateLoaded || null;
  const critical = {}; STRICT_CRITICAL_KEYS.forEach(function (key) { critical[key] = sha256JSON(campaign[key]); });
  const payload = {
    schema: "gg.u2.evaluation.strict-partial-compact/2",
    semanticRole: "mechanically derived compact projection of one content-addressed strict-partial host result",
    platformLabel: platformLabel,
    inputs: {
      normalization: normalizationLoaded.binding,
      campaign: campaignLoaded.binding,
      hostCertificate: certificate ? certificate.binding : null
    },
    sourceBoundary: {
      sourceCommit: campaign.sourceBoundary.sourceCommit,
      sourceTree: campaign.sourceBoundary.sourceTree,
      semanticDigest: campaign.sourceBoundary.contentAddress.digest
    },
    normalization: {
      semanticReplay: "PASS",
      cellCount: normalization.cells.length,
      recordCount: sum(normalization.cells.map(function (cell) { return cell.records.length; })),
      confirmatoryInputDigestCount: normalization.confirmatoryInputDigests.length,
      constructionRealizationCounts: histogram(normalization.cells.map(function (cell) { return cell.constructionRealizationCount; })),
      measurementBatchCounts: histogram(normalization.cells.map(function (cell) { return cell.measurementBatchCount; }))
    },
    campaign: {
      counts: clone(campaign.counts),
      protocolProjection: projection(STRICT_PROTOCOL_KEYS, campaign),
      scientificProjection: projection(STRICT_SCIENTIFIC_KEYS, campaign),
      diagnosticToleranceProjection: strictDiagnosticProjection(campaign),
      criticalProjectionDigests: critical,
      runManifestMerkleRoot: campaign.runManifestMerkleRoot,
      gates: clone(derivedGates),
      conclusion: clone(derivedConclusion),
      finiteFindings: strictFiniteFindings(campaign),
      failureCensus: strictFailureCensus(campaign),
      controls: strictControlCensus(campaign),
      evidenceBoundary: clone(campaign.evidenceBoundary)
    },
    interpretation: {
      evaluationClass: "STRICT_PARTIAL",
      completeConfirmatoryU2: false,
      u2Status: "UNRESOLVED",
      acceptanceAllowed: false,
      rejectionClaimed: false,
      decisionAuthority: "PARTIAL_EVIDENCE_ONLY"
    }
  };
  return addressed(payload);
}

function buildStrictCompact(platformLabel, input, options) {
  if (!input || !input.normalization || !input.campaign) throw new Error("strict compact requires normalization and campaign paths");
  options = options || {};
  return buildStrictCompactFromLoaded(platformLabel, input, bindBytes(input.normalization), bindBytes(input.campaign), input.certificate && options.nativeCertificateRequired !== false ? bindBytes(input.certificate) : null, options);
}

function validateStrictCompact(artifact, platformLabel, input, loaded, options) {
  const errors = [];
  try {
    const expected = loaded ? buildStrictCompactFromLoaded(platformLabel, input, loaded.normalization, loaded.campaign, loaded.certificate || null, options) : buildStrictCompact(platformLabel, input, options);
    if (canonicalStringify(artifact) !== canonicalStringify(expected)) errors.push("strict compact differs from deterministic full rebuild");
    errors.push.apply(errors, validateContentAddress(artifact).errors);
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

function artifactBinding(relativePath, artifact) {
  const bytes = serializeArtifact(artifact);
  return { path: relativePath, bytes: bytes.length, sha256: sha256Bytes(bytes), semanticDigest: artifact.contentAddress.digest };
}

function buildStrictComparison(macosCompact, windowsCompact) {
  const exactRaw = macosCompact.inputs.campaign.sha256 === windowsCompact.inputs.campaign.sha256 && macosCompact.inputs.campaign.bytes === windowsCompact.inputs.campaign.bytes;
  const critical = {}; STRICT_CRITICAL_KEYS.forEach(function (key) { critical[key] = macosCompact.campaign.criticalProjectionDigests[key] === windowsCompact.campaign.criticalProjectionDigests[key]; });
  const diagnosticEqual = macosCompact.campaign.diagnosticToleranceProjection.digest === windowsCompact.campaign.diagnosticToleranceProjection.digest;
  const payload = {
    schema: "gg.u2.evaluation.strict-cross-comparison/2",
    semanticRole: "strict exact and explicitly nondecisional 1e-12 diagnostic comparison of independent host projections",
    inputs: {
      macos: artifactBinding(OUTPUTS.macStrictCompact, macosCompact),
      windows: artifactBinding(OUTPUTS.windowsStrictCompact, windowsCompact)
    },
    normalization: {
      rawExact: macosCompact.inputs.normalization.sha256 === windowsCompact.inputs.normalization.sha256 && macosCompact.inputs.normalization.bytes === windowsCompact.inputs.normalization.bytes,
      semanticExact: macosCompact.inputs.normalization.semanticDigest === windowsCompact.inputs.normalization.semanticDigest
    },
    campaign: {
      rawExact: exactRaw,
      semanticExact: macosCompact.inputs.campaign.semanticDigest === windowsCompact.inputs.campaign.semanticDigest,
      protocolProjectionExact: macosCompact.campaign.protocolProjection.digest === windowsCompact.campaign.protocolProjection.digest,
      scientificProjectionExact: macosCompact.campaign.scientificProjection.digest === windowsCompact.campaign.scientificProjection.digest,
      criticalProjectionExact: critical,
      exactCrossPlatformReplication: exactRaw ? "PASS" : "FAIL"
    },
    diagnosticToleranceProjection: {
      tolerance: 1e-12,
      policy: macosCompact.campaign.diagnosticToleranceProjection.policy,
      macosDigest: macosCompact.campaign.diagnosticToleranceProjection.digest,
      windowsDigest: windowsCompact.campaign.diagnosticToleranceProjection.digest,
      equal: diagnosticEqual,
      status: diagnosticEqual ? "PASS" : "FAIL",
      decisionAuthority: "NONE"
    },
    gateEight: {
      status: "NOT_SATISFIED",
      reason: "the strict partial campaign is not byte/scientific-projection exact across hosts; a rounded diagnostic cannot satisfy Gate 8"
    },
    outcome: { u2Status: "UNRESOLVED", acceptanceAllowed: false, rejectionClaimed: false, decisionAuthority: "NONE" }
  };
  return addressed(payload);
}

function validateStrictComparison(artifact, macosCompact, windowsCompact) {
  const errors = [];
  try {
    const expected = buildStrictComparison(macosCompact, windowsCompact);
    if (canonicalStringify(artifact) !== canonicalStringify(expected)) errors.push("strict comparison differs from deterministic full rebuild");
    errors.push.apply(errors, validateContentAddress(artifact).errors);
    if (artifact.campaign.exactCrossPlatformReplication !== "FAIL") errors.push("strict exact comparison must expose the observed FAIL");
    if (artifact.diagnosticToleranceProjection.status !== "PASS" || artifact.diagnosticToleranceProjection.decisionAuthority !== "NONE") errors.push("strict 1e-12 diagnostic must be PASS/NONE");
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

function screeningPaths(directory) {
  return {
    raw: directory + "/screening-raw-v3.jsonl",
    summary: directory + "/screening-summary-envelope-v3.json",
    runtime: directory + "/screening-runtime-v3.json",
    checkpoint: directory + "/screening-checkpoint-manifest-v3.json",
    writer: directory + "/writer-capability-v3.json"
  };
}

function validateNativeScreeningCertificateLoaded(platformLabel, certificateLoaded, context) {
  const errors = [], certificate = certificateLoaded && certificateLoaded.artifact;
  try {
    if (!certificateLoaded || !certificate) throw new Error(platformLabel + " native screening certificate missing");
    errors.push.apply(errors, validateContentAddress(certificate).errors);
    if (certificateLoaded.binding.path !== INPUTS.screeningCertificates[platformLabel]) errors.push("native screening certificate path mismatch");
    if (certificate.schema !== SCREEN_NATIVE_CERTIFICATE_SCHEMA || !certificate.environment || certificate.environment.platformLabel !== platformLabel) errors.push("native screening certificate identity mismatch");
    if (!certificate.invocation || certificate.invocation.executable !== "node" || Object.prototype.hasOwnProperty.call(certificate.invocation, "executablePath") || !Array.isArray(certificate.invocation.execArgv) || certificate.invocation.script !== "website/global-geometry-lab/generate-global-geometry-ii-u2-native-validation-certificates-v2.js" || !["--write-native-screening", "--write-native-all"].includes(certificate.invocation.mode) || canonicalStringify(certificate.invocation.argv) !== canonicalStringify([certificate.invocation.script, certificate.invocation.mode]) || certificate.command !== certificate.invocation.command || canonicalStringify(certificate.environment.execArgv) !== canonicalStringify(certificate.invocation.execArgv)) errors.push("native screening certificate invocation metadata mismatch");
    if (!certificate.timing || !(certificate.timing.elapsedMilliseconds >= 0) || Number.isNaN(Date.parse(certificate.timing.startedAt)) || Number.isNaN(Date.parse(certificate.timing.completedAt))) errors.push("native screening certificate timing invalid");
    if (canonicalStringify(certificate.artifactSourceBoundary) !== canonicalStringify(context.sourceBoundary)) errors.push("native screening certificate source-boundary mismatch");
    const expectedArtifacts = {
      raw: certificateStyleBinding(context.raw),
      summary: certificateStyleBinding(context.summary),
      runtime: certificateStyleBinding(context.runtime),
      checkpoint: certificateStyleBinding(context.checkpoint),
      writerCapability: certificateStyleBinding(context.writer)
    };
    if (canonicalStringify(certificate.artifacts) !== canonicalStringify(expectedArtifacts)) errors.push("native screening certificate artifact bindings mismatch");
    errors.push.apply(errors, validateCertificateSourceBindings(certificate));
    if (!certificate.validation || certificate.validation.status !== "PASS_NATIVE" || certificate.validation.recordsRemeasured !== Screen.EXPECTED_RECORDS || certificate.validation.expectedRecords !== Screen.EXPECTED_RECORDS) errors.push("native screening certificate does not attest the full native census");
    if (certificate.validation && certificate.validation.recordHashProjection !== context.recordHashProjection) errors.push("native screening certificate record-hash projection mismatch");
    if (certificate.validation && canonicalStringify(certificate.validation.scientificSummaryProjection) !== canonicalStringify(context.scientificSummaryProjection)) errors.push("native screening certificate scientific projection mismatch");
    if (certificate.validation && (certificate.validation.screeningOutcome !== "UNRESOLVED" || certificate.validation.containerDecisionAuthority !== "NONE")) errors.push("native screening certificate outcome projection mismatch");
    if (!certificate.outcome || certificate.outcome.u2Status !== "UNRESOLVED" || certificate.outcome.acceptanceAllowed || certificate.outcome.rejectionClaimed || certificate.outcome.decisionAuthority !== "NONE") errors.push("native screening certificate is not fail-closed");
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

function buildScreenHostProjectionFromLoaded(platformLabel, directory, rawLoaded, options) {
  options = options || {};
  const supplied = options.containerLoads || {}, paths = screeningPaths(directory), raw = rawLoaded, summary = supplied.summary || bindBytes(paths.summary), runtime = supplied.runtime || bindBytes(paths.runtime), checkpoint = supplied.checkpoint || bindBytes(paths.checkpoint), writer = supplied.writer || bindBytes(paths.writer), source = summary.artifact.sourceBoundary;
  if (!raw || raw.binding.path !== paths.raw) throw new Error(platformLabel + " screening logical raw path mismatch");
  if (summary.binding.path !== paths.summary || runtime.binding.path !== paths.runtime || checkpoint.binding.path !== paths.checkpoint || writer.binding.path !== paths.writer) throw new Error(platformLabel + " screening container logical path mismatch");
  const parsed = Screen.Semantic.parseCanonicalJsonl(raw.bytes, { expectedCount: Screen.EXPECTED_RECORDS });
  if (!parsed.valid) throw new Error(platformLabel + " screening raw invalid: " + parsed.errors.join("; "));
  const census = Screen.Semantic.Base.expectedCensus();
  parsed.records.forEach(function (record, index) {
    const report = Screen.validateRecord(record, census[index], { remeasure: options.remeasure === true });
    if (!report.valid) throw new Error(platformLabel + " screening record " + index + " invalid: " + report.errors.join("; "));
  });
  if (summary.artifact.raw.path !== paths.raw || summary.artifact.raw.bytes !== raw.bytes.length || summary.artifact.raw.sha256 !== raw.binding.sha256) throw new Error(platformLabel + " summary raw binding mismatch");
  const summaryReport = Screen.validateSummaryEnvelopeBytes(summary.bytes, parsed.records, raw.bytes, paths.raw, summary.artifact.checkpointManifest, source, { remeasure: false });
  if (!summaryReport.valid) throw new Error(platformLabel + " screening summary replay failed: " + summaryReport.errors.join("; "));
  const checkpointAddress = validateContentAddress(checkpoint.artifact); if (!checkpointAddress.valid) throw new Error(platformLabel + " checkpoint invalid");
  if (checkpoint.artifact.finalAssembly.path !== paths.raw || checkpoint.artifact.finalAssembly.bytes !== raw.bytes.length || checkpoint.artifact.finalAssembly.sha256 !== raw.binding.sha256) throw new Error(platformLabel + " checkpoint raw assembly mismatch");
  if (checkpoint.artifact.platformLabel !== platformLabel) throw new Error(platformLabel + " checkpoint platform mismatch");
  const writerReport = ScreenRunner.validateWriterCapabilityBytes(writer.bytes, platformLabel, source); if (!writerReport.valid) throw new Error(platformLabel + " writer capability invalid: " + writerReport.errors.join("; "));
  const capabilityBinding = { path: paths.writer, bytes: writer.bytes.length, sha256: writer.binding.sha256, semanticDigest: writer.artifact.contentAddress.digest };
  if (canonicalStringify(checkpoint.artifact.writerCapability) !== canonicalStringify(capabilityBinding)) throw new Error(platformLabel + " checkpoint writer binding mismatch");
  const runtimeContext = { platformLabel: platformLabel, source: source, capabilityBinding: capabilityBinding, rawPath: paths.raw, rawBytes: raw.bytes, summaryPath: paths.summary, summaryBytes: summary.bytes, summary: summary.artifact, checkpointPath: paths.checkpoint, checkpointBytes: checkpoint.bytes, checkpoint: checkpoint.artifact };
  const runtimeReport = ScreenRunner.validateRuntimeBytes(runtime.bytes, runtimeContext); if (!runtimeReport.valid) throw new Error(platformLabel + " runtime invalid: " + runtimeReport.errors.join("; "));
  const hostProjection = {
    platformLabel: platformLabel,
    inputs: { raw: raw.binding, summary: summary.binding, runtime: runtime.binding, checkpoint: checkpoint.binding, writerCapability: writer.binding, nativeValidationCertificate: null },
    sourceBoundary: clone(source),
    recordCount: parsed.records.length,
    rawSha256: raw.binding.sha256,
    recordHashProjection: sha256JSON(parsed.records.map(function (record) { return { identity: record.identity, recordHash: record.recordHash }; })),
    scientificSummaryProjection: projection(SCREEN_SCIENTIFIC_KEYS, summary.artifact.semanticSummary),
    census: clone(summary.artifact.semanticSummary.census),
    screenOutcome: clone(summary.artifact.semanticSummary.outcome),
    containerOutcome: clone(summary.artifact.outcome)
  };
  if (options.nativeCertificateRequired !== false) {
    const certificate = bindBytes(INPUTS.screeningCertificates[platformLabel]), report = validateNativeScreeningCertificateLoaded(platformLabel, certificate, {
      raw: raw, summary: summary, runtime: runtime, checkpoint: checkpoint, writer: writer, sourceBoundary: source,
      recordHashProjection: hostProjection.recordHashProjection, scientificSummaryProjection: hostProjection.scientificSummaryProjection
    });
    if (!report.valid) throw new Error(platformLabel + " native screening certificate invalid: " + report.errors.join("; "));
    hostProjection.inputs.nativeValidationCertificate = certificate.binding;
  }
  return hostProjection;
}

function buildScreenHostProjection(platformLabel, directory, options) {
  const paths = screeningPaths(directory);
  return buildScreenHostProjectionFromLoaded(platformLabel, directory, bindBytes(paths.raw, { json: false }), options);
}

function buildScreeningComparison(macosProjection, windowsProjection) {
  if (!macosProjection.inputs.nativeValidationCertificate || !windowsProjection.inputs.nativeValidationCertificate) throw new Error("screening comparison requires both native validation certificates");
  if (macosProjection.inputs.nativeValidationCertificate.path !== INPUTS.screeningCertificates.macos || windowsProjection.inputs.nativeValidationCertificate.path !== INPUTS.screeningCertificates.windows) throw new Error("screening comparison native certificate path mismatch");
  const rawExact = macosProjection.inputs.raw.bytes === windowsProjection.inputs.raw.bytes && macosProjection.rawSha256 === windowsProjection.rawSha256;
  const recordProjectionExact = macosProjection.recordHashProjection === windowsProjection.recordHashProjection;
  const scientificProjectionExact = macosProjection.scientificSummaryProjection.digest === windowsProjection.scientificSummaryProjection.digest;
  const payload = {
    schema: "gg.u2.evaluation.screening-v3-cross-comparison/2",
    semanticRole: "exact cross-host comparison of independently validated screening-v3 raw records and scientific summary projections",
    hosts: { macos: clone(macosProjection), windows: clone(windowsProjection) },
    sourceBoundaryExact: canonicalStringify(macosProjection.sourceBoundary) === canonicalStringify(windowsProjection.sourceBoundary),
    raw: { bytesExact: rawExact, macosSha256: macosProjection.rawSha256, windowsSha256: windowsProjection.rawSha256, status: rawExact ? "PASS" : "FAIL" },
    recordHashProjection: { exact: recordProjectionExact, status: recordProjectionExact ? "PASS" : "FAIL" },
    scientificSummaryProjection: { exact: scientificProjectionExact, status: scientificProjectionExact ? "PASS" : "FAIL", keys: SCREEN_SCIENTIFIC_KEYS.slice() },
    interpretation: {
      screeningReplication: rawExact && recordProjectionExact && scientificProjectionExact ? "PASS" : "FAIL",
      decisionAuthority: "NONE",
      gateEightSatisfied: false,
      reason: rawExact && recordProjectionExact && scientificProjectionExact
        ? "screening-v3 reproduced exactly, but still lacks the preregistered decision-grade estimators, robustness ensembles, and full confirmatory authority"
        : "screening-v3 was evaluated independently across hosts but did not reproduce exactly; it also lacks decision-grade estimators, robustness ensembles, and full confirmatory authority"
    },
    outcome: { u2Status: "UNRESOLVED", acceptanceAllowed: false, rejectionClaimed: false, decisionAuthority: "NONE" }
  };
  return addressed(payload);
}

function validateScreeningComparison(artifact, macosProjection, windowsProjection) {
  const errors = [];
  try {
    const expected = buildScreeningComparison(macosProjection, windowsProjection);
    if (canonicalStringify(artifact) !== canonicalStringify(expected)) errors.push("screening comparison differs from deterministic full rebuild");
    errors.push.apply(errors, validateContentAddress(artifact).errors);
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

function bindConvenienceArchive(archivePath, sourceBinding, sourceKind, expectedBytes) {
  const archive = fs.readFileSync(resolve(archivePath)), decompressed = zlib.gunzipSync(archive), sourcePath = resolve(sourceBinding.path), source = expectedBytes || (fs.existsSync(sourcePath) ? fs.readFileSync(sourcePath) : decompressed);
  if (!decompressed.equals(source)) throw new Error(archivePath + " decompression differs from " + sourceBinding.path);
  if (decompressed.length !== sourceBinding.bytes || sha256Bytes(decompressed) !== sourceBinding.sha256) throw new Error(archivePath + " decompressed raw binding mismatch");
  if (sourceBinding.semanticDigest !== undefined && sourceBinding.semanticDigest !== null) {
    const decompressedArtifact = JSON.parse(decompressed.toString("utf8")), addressReport = validateContentAddress(decompressedArtifact);
    if (!addressReport.valid || decompressedArtifact.contentAddress.digest !== sourceBinding.semanticDigest) throw new Error(archivePath + " decompressed semantic binding mismatch");
  }
  return {
    path: archivePath,
    rawSha256: sha256Bytes(archive),
    rawBytes: archive.length,
    decompressedSha256: sha256Bytes(decompressed),
    decompressedBytes: decompressed.length,
    correspondingSourcePath: sourceBinding.path,
    correspondingSourceSemanticDigest: sourceBinding.semanticDigest === undefined ? null : sourceBinding.semanticDigest,
    sourceKind: sourceKind,
    scientificAuthority: "NONE",
    role: "deterministic gzip -n -9 convenience transport; decompressed bytes are the authoritative bound source artifact"
  };
}

function buildEvaluationIndex(macosCompact, windowsCompact, strictComparison, screeningComparison, suppliedArchives) {
  if (!screeningComparison.hosts.macos.inputs.nativeValidationCertificate || !screeningComparison.hosts.windows.inputs.nativeValidationCertificate) throw new Error("evaluation index requires both native screening certificates");
  const archives = suppliedArchives ? clone(suppliedArchives) : [
    bindConvenienceArchive(INPUTS.archives.strictMacos, macosCompact.inputs.campaign, "STRICT_PARTIAL_CAMPAIGN"),
    bindConvenienceArchive(INPUTS.archives.strictWindows, windowsCompact.inputs.campaign, "STRICT_PARTIAL_CAMPAIGN"),
    bindConvenienceArchive(INPUTS.archives.screeningMacos, screeningComparison.hosts.macos.inputs.raw, "SCREENING_V3_RAW_JSONL"),
    bindConvenienceArchive(INPUTS.archives.screeningWindows, screeningComparison.hosts.windows.inputs.raw, "SCREENING_V3_RAW_JSONL")
  ];
  if (!Array.isArray(archives) || archives.length !== 4) throw new Error("evaluation index requires exactly four convenience archive bindings");
  const payload = {
    schema: "gg.u2.evaluation.index/2",
    evaluationId: "global-geometry-ii-u2-evaluation-v2",
    semanticRole: "closed, content-addressed index of completed partial/screening evaluations and explicitly unperformed work",
    artifacts: {
      strictPartialMacos: artifactBinding(OUTPUTS.macStrictCompact, macosCompact),
      strictPartialWindows: artifactBinding(OUTPUTS.windowsStrictCompact, windowsCompact),
      strictCrossComparison: artifactBinding(OUTPUTS.strictComparison, strictComparison),
      screeningV3CrossComparison: artifactBinding(OUTPUTS.screeningComparison, screeningComparison),
      nativeScreeningMacosCertificate: clone(screeningComparison.hosts.macos.inputs.nativeValidationCertificate),
      nativeScreeningWindowsCertificate: clone(screeningComparison.hosts.windows.inputs.nativeValidationCertificate)
    },
    convenienceArchives: archives,
    stages: {
      strictPartial: { status: "COMPLETED_PARTIAL", exactCrossPlatformReplication: strictComparison.campaign.exactCrossPlatformReplication, diagnosticToleranceProjection: strictComparison.diagnosticToleranceProjection.status, diagnosticDecisionAuthority: "NONE", u2Status: "UNRESOLVED" },
      screeningV3: { status: "COMPLETED_SCREENING", exactRawReplication: screeningComparison.raw.status, exactScientificProjection: screeningComparison.scientificSummaryProjection.status, decisionAuthority: "NONE", u2Status: "UNRESOLVED" },
      preview: { status: "NOT_EVALUATED", decisionAuthority: "NONE" },
      fullConfirmatory: { status: "NOT_RUN", decisionAuthority: "NONE" },
      physicalValidation: { status: "NOT_RUN", decisionAuthority: "NONE" }
    },
    overall: {
      u2Status: "UNRESOLVED",
      acceptanceAllowed: false,
      rejectionClaimed: false,
      decisionAuthority: "NONE",
      shareableAs: "content-addressed strict-partial and cross-platform-evaluated screening checkpoint",
      prohibitedClaim: "this index is not a completed confirmatory U2 evaluation and contains no physical validation"
    },
    cleanCloneReplay: {
      command: "node website/global-geometry-lab/generate-global-geometry-ii-u2-evaluation-index-v2.js --validate-only",
      targetedCommands: {
        strict: "node website/global-geometry-lab/generate-global-geometry-ii-u2-evaluation-index-v2.js --validate-strict",
        screening: "node website/global-geometry-lab/generate-global-geometry-ii-u2-evaluation-index-v2.js --validate-screening"
      },
      sourceMode: "FOUR_TRACKED_GZIP_TRANSPORTS",
      uncompressedStrictCampaignsRequired: false,
      uncompressedScreeningRawRequired: false,
      screeningChunksRequired: false,
      validates: ["gzip decompression-to-source byte equality", "raw and semantic bindings", "platform-native frozen strict campaign semantic replay plus foreign-host certificate/content/ledger verification", "all 3840 native screening records by fresh semantic remeasurement; foreign records require their native certificate when raw bytes differ", "screening summaries/runtime/writer/checkpoint", "compact summaries", "both comparisons", "evaluation index"]
    }
  };
  return addressed(payload);
}

function validateEvaluationIndex(artifact, macosCompact, windowsCompact, strictComparison, screeningComparison, suppliedArchives) {
  const errors = [];
  try {
    const expected = buildEvaluationIndex(macosCompact, windowsCompact, strictComparison, screeningComparison, suppliedArchives);
    if (canonicalStringify(artifact) !== canonicalStringify(expected)) errors.push("evaluation index differs from deterministic full rebuild");
    errors.push.apply(errors, validateContentAddress(artifact).errors);
    if (artifact.stages.preview.status !== "NOT_EVALUATED" || artifact.stages.fullConfirmatory.status !== "NOT_RUN" || artifact.stages.physicalValidation.status !== "NOT_RUN") errors.push("unperformed-stage semantics mismatch");
    if (artifact.overall.u2Status !== "UNRESOLVED" || artifact.overall.acceptanceAllowed || artifact.overall.rejectionClaimed) errors.push("evaluation index is not fail-closed");
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

function writeAllOnce(artifacts) {
  const entries = Object.entries(artifacts).map(function (entry) { return { path: resolve(entry[0]), bytes: serializeArtifact(entry[1]) }; });
  entries.forEach(function (entry) { if (fs.existsSync(entry.path)) throw new Error("refusing to overwrite evaluation-v2 artifact: " + entry.path); });
  fs.mkdirSync(resolve(OUTPUT_DIRECTORY), { recursive: true });
  entries.forEach(function (entry) { fs.writeFileSync(entry.path, entry.bytes, { flag: "wx" }); });
}

function buildAll(options) {
  options = options || {}; const archiveMode = options.sourceMode === "archives";
  let macosCompact, windowsCompact, macosScreen, windowsScreen, archiveStrictReports = null;
  if (archiveMode) {
    archiveStrictReports = [];
    {
      const normalization = bindBytes(INPUTS.strict.macos.normalization), campaign = loadArchivedSource(INPUTS.archives.strictMacos, INPUTS.strict.macos.campaign), certificate = bindBytes(INPUTS.strict.macos.certificate), loaded = { normalization: normalization, campaign: campaign, certificate: certificate };
      macosCompact = buildStrictCompactFromLoaded("macos", INPUTS.strict.macos, normalization, campaign, certificate);
      archiveStrictReports.push(validateStrictCompact(macosCompact, "macos", INPUTS.strict.macos, loaded));
    }
    {
      const normalization = bindBytes(INPUTS.strict.windows.normalization), campaign = loadArchivedSource(INPUTS.archives.strictWindows, INPUTS.strict.windows.campaign), certificate = INPUTS.strict.windows.certificate ? bindBytes(INPUTS.strict.windows.certificate) : null, loaded = { normalization: normalization, campaign: campaign, certificate: certificate };
      windowsCompact = buildStrictCompactFromLoaded("windows", INPUTS.strict.windows, normalization, campaign, certificate);
      archiveStrictReports.push(validateStrictCompact(windowsCompact, "windows", INPUTS.strict.windows, loaded));
    }
    {
      const rawPath = screeningPaths(INPUTS.screening.macos).raw, raw = loadArchivedSource(INPUTS.archives.screeningMacos, rawPath, { json: false });
      macosScreen = buildScreenHostProjectionFromLoaded("macos", INPUTS.screening.macos, raw, { nativeCertificateRequired: options.nativeCertificateRequired !== false });
    }
    {
      const rawPath = screeningPaths(INPUTS.screening.windows).raw, raw = loadArchivedSource(INPUTS.archives.screeningWindows, rawPath, { json: false });
      windowsScreen = buildScreenHostProjectionFromLoaded("windows", INPUTS.screening.windows, raw, { nativeCertificateRequired: options.nativeCertificateRequired !== false });
    }
  } else {
    macosCompact = buildStrictCompact("macos", INPUTS.strict.macos); windowsCompact = buildStrictCompact("windows", INPUTS.strict.windows);
    macosScreen = buildScreenHostProjection("macos", INPUTS.screening.macos, { nativeCertificateRequired: options.nativeCertificateRequired !== false }); windowsScreen = buildScreenHostProjection("windows", INPUTS.screening.windows, { nativeCertificateRequired: options.nativeCertificateRequired !== false });
  }
  const strictComparison = buildStrictComparison(macosCompact, windowsCompact), screeningComparison = buildScreeningComparison(macosScreen, windowsScreen), evaluationIndex = buildEvaluationIndex(macosCompact, windowsCompact, strictComparison, screeningComparison);
  const reports = (archiveStrictReports || [validateStrictCompact(macosCompact, "macos", INPUTS.strict.macos), validateStrictCompact(windowsCompact, "windows", INPUTS.strict.windows)]).concat([validateStrictComparison(strictComparison, macosCompact, windowsCompact), validateScreeningComparison(screeningComparison, macosScreen, windowsScreen), validateEvaluationIndex(evaluationIndex, macosCompact, windowsCompact, strictComparison, screeningComparison)]);
  const errors = reports.flatMap(function (report) { return report.errors; }); if (errors.length) throw new Error(errors.join("; "));
  return { macosCompact: macosCompact, windowsCompact: windowsCompact, strictComparison: strictComparison, screeningComparison: screeningComparison, evaluationIndex: evaluationIndex };
}

function deepValidateStrictSources() {
  const reports = {}, nativeLabel = process.platform === "darwin" ? "macos" : process.platform === "win32" ? "windows" : null;
  if (!nativeLabel) throw new Error("deep strict numerical replay requires a native darwin or win32 host");
  ["macos", "windows"].forEach(function (platformLabel) {
    const input = INPUTS.strict[platformLabel], archivePath = platformLabel === "macos" ? INPUTS.archives.strictMacos : INPUTS.archives.strictWindows, normalizationLoaded = bindBytes(input.normalization), campaignLoaded = loadArchivedSource(archivePath, input.campaign), normalization = normalizationLoaded.artifact, campaign = campaignLoaded.artifact;
    const normalizationReport = Strict.validateCalibration(normalization);
    if (!normalizationReport.valid) throw new Error(platformLabel + " frozen normalization validator failed: " + normalizationReport.errors.join("; "));
    const derivedGates = Strict.deriveGates(campaign.exactGateOne, campaign.cells, campaign.primaryControls, "NOT_RUN"), derivedConclusion = Strict.deriveConclusion(derivedGates), addressReport = validateContentAddress(campaign);
    if (!addressReport.valid || canonicalStringify(campaign.normalizationBinding) !== canonicalStringify(normalization.contentAddress) || canonicalStringify(campaign.gateResults) !== canonicalStringify(derivedGates) || canonicalStringify(campaign.conclusion) !== canonicalStringify(derivedConclusion)) throw new Error(platformLabel + " foreign-safe campaign structural/ledger validation failed");
    if (!input.certificate) throw new Error(platformLabel + " strict native certificate path is missing");
    const certificateLoaded = bindBytes(input.certificate), certificateReport = validateStrictHostCertificateLoaded(platformLabel, input, certificateLoaded, normalizationLoaded, campaignLoaded);
    if (!certificateReport.valid) throw new Error(platformLabel + " strict native certificate invalid: " + certificateReport.errors.join("; "));
    if (platformLabel === nativeLabel) {
      const campaignReport = Strict.validateCampaign(campaign, normalization);
      if (!campaignReport.valid) throw new Error(platformLabel + " native frozen campaign validator failed: " + campaignReport.errors.join("; "));
      reports[platformLabel] = { normalization: "PASS", contentAddressAndLedger: "PASS", numericalSemanticReplay: "PASS_NATIVE", semanticReplayCounts: campaignReport.semanticReplayCounts, independentHostCertificate: "PASS_BOUND_NATIVE_CERTIFICATE" };
    } else {
      reports[platformLabel] = { normalization: "PASS", contentAddressAndLedger: "PASS", numericalSemanticReplay: "NOT_REEXECUTED_CROSS_PLATFORM", semanticReplayCounts: null, independentHostCertificate: "PASS_BOUND_INDEPENDENT_NATIVE_CERTIFICATE" };
    }
  });
  return { validatorPlatform: process.platform, nativeCampaign: nativeLabel, exactCrossPlatformStrictReplayExpected: false, hosts: reports };
}

function deepValidateScreeningSources() {
  const macPaths = screeningPaths(INPUTS.screening.macos), winPaths = screeningPaths(INPUTS.screening.windows), macRaw = loadArchivedSource(INPUTS.archives.screeningMacos, macPaths.raw, { json: false }), winRaw = loadArchivedSource(INPUTS.archives.screeningWindows, winPaths.raw, { json: false }), exact = macRaw.bytes.equals(winRaw.bytes), census = Screen.Semantic.Base.expectedCensus();
  const projections = {
    macos: buildScreenHostProjectionFromLoaded("macos", INPUTS.screening.macos, macRaw),
    windows: buildScreenHostProjectionFromLoaded("windows", INPUTS.screening.windows, winRaw)
  };
  function remeasure(label, loaded) {
    const parsed = Screen.Semantic.parseCanonicalJsonl(loaded.bytes, { expectedCount: Screen.EXPECTED_RECORDS });
    if (!parsed.valid) throw new Error(label + " deep screening parse failed: " + parsed.errors.join("; "));
    parsed.records.forEach(function (record, index) {
      const report = Screen.validateRecord(record, census[index], { remeasure: true });
      if (!report.valid) throw new Error(label + " deep screening semantic replay failed at record " + index + ": " + report.errors.join("; "));
    });
    return parsed.records.length;
  }
  const nativeLabel = process.platform === "darwin" ? "macos" : process.platform === "win32" ? "windows" : null, nativeRaw = nativeLabel === "macos" ? macRaw : nativeLabel === "windows" ? winRaw : null, nativeCount = nativeRaw ? remeasure(nativeLabel, nativeRaw) : 0;
  if (!nativeLabel) throw new Error("deep screening numerical replay requires a native darwin or win32 host");
  return {
    validatorPlatform: process.platform,
    nativeHost: nativeLabel,
    rawByteExact: exact,
    exactReplicationStatus: exact ? "PASS" : "FAIL",
    nativeRemeasuredRecords: nativeCount,
    foreignNumericalSemanticReplay: exact ? "COVERED_BY_EXACT_RAW_EQUALITY" : "NOT_REEXECUTED_CROSS_PLATFORM",
    foreignContainerBindings: "PASS",
    nativeCertificateBindings: {
      macos: { status: "PASS_BOUND_NATIVE_CERTIFICATE", semanticDigest: projections.macos.inputs.nativeValidationCertificate.semanticDigest },
      windows: { status: "PASS_BOUND_NATIVE_CERTIFICATE", semanticDigest: projections.windows.inputs.nativeValidationCertificate.semanticDigest }
    },
    totalFreshRemeasurements: nativeCount
  };
}

function validateFinalOutputBytes(built) {
  const expected = {
    [OUTPUTS.macStrictCompact]: built.macosCompact,
    [OUTPUTS.windowsStrictCompact]: built.windowsCompact,
    [OUTPUTS.strictComparison]: built.strictComparison,
    [OUTPUTS.screeningComparison]: built.screeningComparison,
    [OUTPUTS.evaluationIndex]: built.evaluationIndex
  };
  Object.keys(expected).forEach(function (relativePath) {
    const observed = fs.readFileSync(resolve(relativePath)), exact = serializeArtifact(expected[relativePath]);
    if (!observed.equals(exact)) throw new Error(relativePath + " differs from deterministic final rebuild");
    const parsed = JSON.parse(observed.toString("utf8")), report = validateContentAddress(parsed);
    if (!report.valid) throw new Error(relativePath + " invalid final content address");
  });
  return { status: "EXACT_FINAL_OUTPUT_REPLAY_PASS", outputCount: Object.keys(expected).length };
}

function validationPlan(mode) {
  if (!["--write-final", "--validate-only", "--validate-strict", "--validate-screening"].includes(mode)) throw new Error("usage: generate-global-geometry-ii-u2-evaluation-index-v2.js --write-final|--validate-only|--validate-strict|--validate-screening");
  return {
    mode: mode,
    sourceMode: mode === "--write-final" ? "local-raw" : "archives",
    writeFinal: mode === "--write-final",
    validateStrict: mode === "--validate-only" || mode === "--validate-strict",
    validateScreening: mode === "--validate-only" || mode === "--validate-screening"
  };
}

function main(argv) {
  if (argv.length !== 1) throw new Error("usage: generate-global-geometry-ii-u2-evaluation-index-v2.js --write-final|--validate-only|--validate-strict|--validate-screening");
  const plan = validationPlan(argv[0]), built = buildAll({ sourceMode: plan.sourceMode });
  if (plan.writeFinal) {
    writeAllOnce({ [OUTPUTS.macStrictCompact]: built.macosCompact, [OUTPUTS.windowsStrictCompact]: built.windowsCompact, [OUTPUTS.strictComparison]: built.strictComparison, [OUTPUTS.screeningComparison]: built.screeningComparison, [OUTPUTS.evaluationIndex]: built.evaluationIndex });
    process.stdout.write(JSON.stringify({ status: "WROTE_FINAL_EVALUATION_V2", outputs: OUTPUTS, overall: built.evaluationIndex.overall }) + "\n");
    return;
  }
  const outputReplay = validateFinalOutputBytes(built), strictReplay = plan.validateStrict ? deepValidateStrictSources() : { status: "NOT_REQUESTED", mode: plan.mode }, screeningReplay = plan.validateScreening ? deepValidateScreeningSources() : { status: "NOT_REQUESTED", mode: plan.mode };
  process.stdout.write(JSON.stringify({ status: "VALIDATED_FINAL_EVALUATION_V2_READ_ONLY", mode: plan.mode, outputReplay: outputReplay, strictReplay: strictReplay, screeningReplay: screeningReplay, overall: built.evaluationIndex.overall }) + "\n");
}

if (require.main === module) main(process.argv.slice(2));
module.exports = {
  ROOT: ROOT, OUTPUT_DIRECTORY: OUTPUT_DIRECTORY, OUTPUTS: OUTPUTS, INPUTS: INPUTS,
  STRICT_PROTOCOL_KEYS: STRICT_PROTOCOL_KEYS, STRICT_SCIENTIFIC_KEYS: STRICT_SCIENTIFIC_KEYS, STRICT_CRITICAL_KEYS: STRICT_CRITICAL_KEYS, SCREEN_SCIENTIFIC_KEYS: SCREEN_SCIENTIFIC_KEYS, STRICT_NATIVE_CERTIFICATE_SCHEMA: STRICT_NATIVE_CERTIFICATE_SCHEMA, SCREEN_NATIVE_CERTIFICATE_SCHEMA: SCREEN_NATIVE_CERTIFICATE_SCHEMA,
  canonicalStringify: canonicalStringify, sha256Bytes: sha256Bytes, sha256JSON: sha256JSON, contentAddress: contentAddress, addressed: addressed, serializeArtifact: serializeArtifact, validateContentAddress: validateContentAddress,
  bindBytes: bindBytes, loadArchivedSource: loadArchivedSource, projection: projection, diagnosticTransform: diagnosticTransform, strictDiagnosticProjection: strictDiagnosticProjection,
  validateCertificateSourceBindings: validateCertificateSourceBindings, validateStrictHostCertificateLoaded: validateStrictHostCertificateLoaded, buildStrictCompactFromLoaded: buildStrictCompactFromLoaded, buildStrictCompact: buildStrictCompact, validateStrictCompact: validateStrictCompact, buildStrictComparison: buildStrictComparison, validateStrictComparison: validateStrictComparison,
  screeningPaths: screeningPaths, certificateStyleBinding: certificateStyleBinding, validateNativeScreeningCertificateLoaded: validateNativeScreeningCertificateLoaded, buildScreenHostProjectionFromLoaded: buildScreenHostProjectionFromLoaded, buildScreenHostProjection: buildScreenHostProjection, buildScreeningComparison: buildScreeningComparison, validateScreeningComparison: validateScreeningComparison,
  bindConvenienceArchive: bindConvenienceArchive, buildEvaluationIndex: buildEvaluationIndex, validateEvaluationIndex: validateEvaluationIndex, buildAll: buildAll, writeAllOnce: writeAllOnce,
  deepValidateStrictSources: deepValidateStrictSources, deepValidateScreeningSources: deepValidateScreeningSources, validateFinalOutputBytes: validateFinalOutputBytes, validationPlan: validationPlan
};
