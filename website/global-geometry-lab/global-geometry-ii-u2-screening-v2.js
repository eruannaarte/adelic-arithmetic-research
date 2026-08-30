/* Global Geometry II — repaired, versioned U2 screening artifact kernel. */
"use strict";

const fs = require("fs");
const path = require("path");
const Base = require("./global-geometry-ii-u2-screening.js");
const Supplement = require("./generate-global-geometry-ii-u2-screening-supplement-v3.js");
const SourceBoundary = require("./generate-global-geometry-ii-u2-screening-source-boundary-v2.js");

const ROOT = Base.ROOT;
const VERSION = "2.0.0-screening";
const SUPPLEMENT_PATH = path.join(ROOT, "artifacts/global-geometry-ii/u2/screening/screening-implementation-supplement-v3.json");
const SUPPLEMENT_FILE_SHA256 = "3bd284f7b19a5c4caa790c3e25a177a603e81e74e265a526cc99407a691b18da";
const SUPPLEMENT_DIGEST = "21d69b11b12277e228e2934e033fd8f366b3c8d5d89f1b8833aa781a36118888";
const REPAIR_AUDIT_PATH = path.join(ROOT, "GLOBAL_GEOMETRY_II_EVALUATION_REPAIR_AUDIT.md");
const REPAIR_AUDIT_SHA256 = "3810154ff591ca42a0e85d4ceb90900c09f85e79a6e3ff403525003bac6e0313";
const REPAIR_AUDIT_COMMIT = "c2bc19072c29c3e8f76b190dd598307d70f843a3";
const PILOT_ABORT_PATH = path.join(ROOT, "artifacts/global-geometry-ii/u2/screening/screening-pilot-abort-macos-v1.json");
const PILOT_ABORT_FILE_SHA256 = "ce1f7100730a68775fcc80f8fa6155f8b97b48dd9c6aa5e64d14461c0dd25228";
const PILOT_ABORT_DIGEST = "8db910463c3fbf0fa0e4610ffdba6e6c4c7b70bf04e99ae91bce2f811e2d9166";
const CHUNK_SIZE = 32;
const EXPECTED_RECORDS = 3840;
const EXPECTED_CHUNKS = 120;

function clone(value) { return JSON.parse(JSON.stringify(value)); }
function canonicalStringify(value) { return Base.canonicalStringify(value); }
function sha256Bytes(value) { return Base.sha256Bytes(value); }
function sha256JSON(value) { return Base.sha256JSON(value); }

function serializeJsonArtifact(artifact) {
  return Buffer.from(JSON.stringify(artifact, null, 2) + "\n", "utf8");
}

function validateJsonArtifactBytes(bytes, semanticValidator) {
  const errors = [];
  let artifact = null;
  try {
    if (!Buffer.isBuffer(bytes)) errors.push("artifact bytes must be a Buffer");
    artifact = JSON.parse(bytes.toString("utf8"));
    if (!serializeJsonArtifact(artifact).equals(bytes)) errors.push("artifact bytes are not exact pretty JSON followed by exactly one LF");
    if (semanticValidator) {
      const report = semanticValidator(artifact);
      if (!report.valid) errors.push.apply(errors, report.errors);
    }
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors, artifact: artifact };
}

function loadPrerequisites() {
  Base.loadManifest();
  const supplementBytes = fs.readFileSync(SUPPLEMENT_PATH), supplement = JSON.parse(supplementBytes.toString("utf8"));
  if (sha256Bytes(supplementBytes) !== SUPPLEMENT_FILE_SHA256 || !supplement.contentAddress || supplement.contentAddress.digest !== SUPPLEMENT_DIGEST) throw new Error("active screening-v2 supplement binding mismatch");
  const supplementReport = Supplement.validateSupplement(supplement);
  if (!supplementReport.valid) throw new Error("active supplement validation failed: " + supplementReport.errors.join("; "));
  const auditBytes = fs.readFileSync(REPAIR_AUDIT_PATH);
  if (auditBytes.length !== 9042 || sha256Bytes(auditBytes) !== REPAIR_AUDIT_SHA256) throw new Error("governing repair audit binding mismatch");
  const pilotBytes = fs.readFileSync(PILOT_ABORT_PATH), pilot = JSON.parse(pilotBytes.toString("utf8"));
  if (sha256Bytes(pilotBytes) !== PILOT_ABORT_FILE_SHA256 || !pilot.contentAddress || pilot.contentAddress.digest !== PILOT_ABORT_DIGEST || pilot.audit.inferentialUse !== "PROHIBITED") throw new Error("aborted-pilot metadata binding mismatch");
  return { supplement: supplement, repairAudit: { path: "GLOBAL_GEOMETRY_II_EVALUATION_REPAIR_AUDIT.md", bytes: auditBytes.length, sha256: REPAIR_AUDIT_SHA256, commit: REPAIR_AUDIT_COMMIT }, pilotAbort: pilot };
}

function independenceForPositive(family, sigmaIndex) {
  const hashed = family === "square-hashed-diagonal", sigmaZero = sigmaIndex === 0;
  return {
    carrierConstructionRealizationCount: hashed ? 32 : 1,
    conductanceRealizationCount: sigmaZero ? 1 : 32,
    jointWeightedRealizationCount: hashed || !sigmaZero ? 32 : 1,
    randomizedNestedMeasurementBatchCount: !hashed && sigmaZero ? 32 : 0,
    repeatedDeterministicEvaluationCount: 0,
    measurementBatchCount: 32,
    label: !hashed && sigmaZero
      ? "one deterministic carrier and one deterministic conductance field with 32 randomized nested measurement batches; not 32 independent geometries"
      : (hashed && sigmaZero
        ? "32 construction realizations sharing one deterministic unit-conductance law"
        : (!hashed
          ? "one deterministic carrier with 32 conductance/joint weighted realizations"
          : "32 construction and joint weighted realizations"))
  };
}

function independenceForControl(control) {
  if (control === "comb-trap") return { carrierConstructionRealizationCount: 1, conductanceRealizationCount: 0, jointWeightedRealizationCount: 1, randomizedNestedMeasurementBatchCount: 32, repeatedDeterministicEvaluationCount: 0, measurementBatchCount: 32, label: "one deterministic carrier with 32 randomized walk batches" };
  if (control === "vanishing-neck") return { carrierConstructionRealizationCount: 1, conductanceRealizationCount: 0, jointWeightedRealizationCount: 1, randomizedNestedMeasurementBatchCount: 0, repeatedDeterministicEvaluationCount: 31, measurementBatchCount: 32, label: "one unique deterministic evaluation plus 31 exact repeated evaluations; not randomized nested batches" };
  return { carrierConstructionRealizationCount: 32, conductanceRealizationCount: 0, jointWeightedRealizationCount: 32, randomizedNestedMeasurementBatchCount: 0, repeatedDeterministicEvaluationCount: 0, measurementBatchCount: 32, label: "32 independently streamed control constructions" };
}

function buildRecord(identity) {
  const baseRecord = Base.buildRecord(identity), payload = clone(baseRecord);
  delete payload.recordHash;
  payload.schema = "gg.u2.screening.record/2";
  payload.supplementDigest = SUPPLEMENT_DIGEST;
  payload.implementation = { version: VERSION, repairAuditSha256: REPAIR_AUDIT_SHA256, repairAuditCommit: REPAIR_AUDIT_COMMIT };
  payload.independenceAccounting = identity.kind === "positive" ? independenceForPositive(identity.id, identity.sigmaIndex) : independenceForControl(identity.id);
  if (identity.kind === "control") {
    const hasShortfall = payload.failures.some(function (failure) { return failure.channel === "control-shortfall"; });
    payload.construction.declaredParametersRealized = !hasShortfall;
  }
  return Object.assign({}, payload, { recordHash: sha256JSON(payload) });
}

function validateRecord(record, expectedIdentity, options) {
  const errors = [];
  options = options || {};
  try {
    if (!record || record.schema !== "gg.u2.screening.record/2" || record.supplementDigest !== SUPPLEMENT_DIGEST) errors.push("record v2 identity/binding mismatch");
    if (expectedIdentity && canonicalStringify(record.identity) !== canonicalStringify(expectedIdentity)) errors.push("record census identity mismatch");
    const payload = clone(record); delete payload.recordHash;
    if (record.recordHash !== sha256JSON(payload)) errors.push("recordHash mismatch");
    if (!record.screenInterpretation || record.screenInterpretation.u2Status !== "UNRESOLVED" || record.screenInterpretation.decisionAuthority !== "NONE") errors.push("record is not fail-closed");
    const expectedIndependence = record.identity.kind === "positive" ? independenceForPositive(record.identity.id, record.identity.sigmaIndex) : independenceForControl(record.identity.id);
    if (canonicalStringify(record.independenceAccounting) !== canonicalStringify(expectedIndependence)) errors.push("record independence accounting mismatch");
    if (record.identity.kind === "control") {
      const hasShortfall = record.failures.some(function (failure) { return failure.channel === "control-shortfall"; });
      if (!record.construction || record.construction.declaredParametersRealized !== !hasShortfall) errors.push("declaredParametersRealized must equal absence of control-shortfall");
    }
    if (options.remeasure !== false && errors.length === 0) {
      const rebuilt = buildRecord(record.identity);
      if (record.recordHash !== rebuilt.recordHash) errors.push("rebuilt recordHash mismatch");
      if (canonicalStringify(record) !== canonicalStringify(rebuilt)) errors.push("full rebuilt canonical record mismatch");
    }
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

function replayRecord(record) {
  const errors = [];
  let rebuilt = null;
  try {
    rebuilt = buildRecord(record.identity);
    if (record.recordHash !== rebuilt.recordHash) errors.push("record hash differs from rebuilt hash");
    if (canonicalStringify(record) !== canonicalStringify(rebuilt)) errors.push("supplied record differs from full canonical rebuild");
    const suppliedPayload = clone(record); delete suppliedPayload.recordHash;
    if (record.recordHash !== sha256JSON(suppliedPayload)) errors.push("supplied recordHash does not bind supplied payload");
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors, observedHash: record && record.recordHash, expectedHash: rebuilt && rebuilt.recordHash, rebuilt: rebuilt };
}

function serializeCanonicalJsonl(records) {
  if (!Array.isArray(records) || !records.length) throw new Error("canonical JSONL requires at least one record");
  return Buffer.from(records.map(canonicalStringify).join("\n") + "\n", "utf8");
}

function parseCanonicalJsonl(bytes, options) {
  const errors = [], records = [];
  options = options || {};
  try {
    if (!Buffer.isBuffer(bytes) || !bytes.length) throw new Error("JSONL bytes must be a nonempty Buffer");
    if (bytes[bytes.length - 1] !== 10) errors.push("JSONL must end with exactly one LF");
    if (bytes.length > 1 && bytes[bytes.length - 2] === 10) errors.push("JSONL has more than one terminal LF");
    if (bytes.includes(13)) errors.push("JSONL must not contain CR bytes");
    const body = bytes.subarray(0, bytes.length - 1).toString("utf8"), lines = body.split("\n");
    if (lines.some(function (line) { return !line.length; })) errors.push("JSONL contains an empty record line");
    lines.forEach(function (line, index) {
      try {
        const record = JSON.parse(line);
        if (canonicalStringify(record) !== line) errors.push("line " + index + " is not exact canonical JSON");
        records.push(record);
      } catch (error) { errors.push("line " + index + ": " + error.message); }
    });
    if (options.expectedCount != null && records.length !== options.expectedCount) errors.push("JSONL record count mismatch");
    if (!errors.length && !serializeCanonicalJsonl(records).equals(bytes)) errors.push("JSONL byte replay mismatch");
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors, records: records };
}

function sourceBinding(boundaryBytes, mode, pins, adapters, boundaryPath) {
  const report = SourceBoundary.verifyBoundaryBytes(boundaryBytes, mode, pins, adapters);
  if (!report.valid) throw new Error("source boundary verification failed: " + report.errors.join("; "));
  return {
    path: boundaryPath || "artifacts/global-geometry-ii/u2/screening/screening-v2/source-boundary-v2.json",
    fileSha256: pins.fileSha256,
    semanticDigest: pins.semanticSha256,
    sourceCommit: report.artifact.sourceCommit,
    sourceTree: report.artifact.sourceTree,
    verificationMode: mode
  };
}

function buildChunkCertificate(chunkIndex, records, chunkBytes, chunkPath, source) {
  if (!Number.isInteger(chunkIndex) || chunkIndex < 0 || chunkIndex >= EXPECTED_CHUNKS || records.length !== CHUNK_SIZE) throw new Error("invalid chunk certificate input");
  const payload = {
    schema: "gg.u2.screening.chunk-certificate/2",
    screeningVersion: "screening-v2",
    supplementDigest: SUPPLEMENT_DIGEST,
    chunkIndex: chunkIndex,
    ordinalRange: [chunkIndex * CHUNK_SIZE, chunkIndex * CHUNK_SIZE + CHUNK_SIZE - 1],
    recordCount: records.length,
    firstRunId: records[0].identity.runId,
    lastRunId: records[records.length - 1].identity.runId,
    chunk: { path: chunkPath, bytes: chunkBytes.length, sha256: sha256Bytes(chunkBytes), recordMerkleRoot: Base.merkleRoot(records.map(function (record) { return record.recordHash; })) },
    sourceBoundary: clone(source),
    outcome: { u2Status: "UNRESOLVED", decisionAuthority: "NONE" }
  };
  return Object.assign({}, payload, { contentAddress: { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest: sha256JSON(payload), canonicalBytes: Buffer.byteLength(canonicalStringify(payload), "utf8") } });
}

function validateChunk(chunkBytes, certificateBytes, chunkIndex, chunkPath, source, options) {
  const errors = [], parsed = parseCanonicalJsonl(chunkBytes, { expectedCount: CHUNK_SIZE });
  options = options || {};
  errors.push.apply(errors, parsed.errors);
  const census = Base.expectedCensus(), start = chunkIndex * CHUNK_SIZE;
  if (!errors.length) parsed.records.forEach(function (record, offset) {
    const report = validateRecord(record, census[start + offset], { remeasure: options.remeasure !== false });
    if (!report.valid) errors.push("record " + (start + offset) + ": " + report.errors.join(", "));
  });
  const certificateReport = validateJsonArtifactBytes(certificateBytes), certificate = certificateReport.artifact;
  errors.push.apply(errors, certificateReport.errors);
  if (!errors.length) {
    const expected = buildChunkCertificate(chunkIndex, parsed.records, chunkBytes, chunkPath, source);
    if (canonicalStringify(certificate) !== canonicalStringify(expected)) errors.push("chunk certificate differs from deterministic full rebuild");
  }
  return { valid: errors.length === 0, errors: errors, records: parsed.records, certificate: certificate };
}

function uniqueCounts(cell, kind) {
  const structures = new Set(cell.map(function (record) { return record.graphAudit.structureDigest; }));
  if (kind === "positive") {
    const weights = new Set(cell.map(function (record) { return record.conductanceAudit.weightDigest; }));
    const joint = new Set(cell.map(function (record) { return record.graphAudit.structureDigest + ":" + record.conductanceAudit.weightDigest; }));
    return { uniqueStructureDigestCount: structures.size, uniqueWeightDigestCount: weights.size, uniqueJointDigestCount: joint.size };
  }
  return { uniqueStructureDigestCount: structures.size, uniqueWeightDigestCount: 0, uniqueJointDigestCount: structures.size };
}

function buildSummary(records, rawBinding, provenance) {
  const base = Base.summarizeRecords(records, rawBinding), payload = clone(base);
  delete payload.contentAddress;
  payload.schema = "gg.u2.screening.summary/2";
  payload.screeningId = "ggii-u2-v2-screening-v2";
  payload.screeningVersion = "screening-v2";
  payload.supplementDigest = SUPPLEMENT_DIGEST;
  payload.implementation = { version: VERSION, repairAuditSha256: REPAIR_AUDIT_SHA256, repairAuditCommit: REPAIR_AUDIT_COMMIT };
  payload.sourceBoundary = clone(provenance.sourceBoundary);
  payload.checkpointManifest = clone(provenance.checkpointManifest);
  payload.positiveCells.forEach(function (row) {
    const cell = records.filter(function (record) { return record.identity.kind === "positive" && record.identity.id === row.family && record.identity.size === row.size && record.identity.sigmaIndex === row.sigmaIndex; });
    row.independence = independenceForPositive(row.family, row.sigmaIndex);
    Object.assign(row, uniqueCounts(cell, "positive"));
    delete row.uniqueStructureDigests;
    delete row.uniqueWeightedRealizationCount;
  });
  payload.controlCells.forEach(function (row) {
    const cell = records.filter(function (record) { return record.identity.kind === "control" && record.identity.id === row.control && record.identity.size === row.size; });
    row.independence = independenceForControl(row.control);
    Object.assign(row, uniqueCounts(cell, "control"));
    delete row.uniqueStructureDigests;
    delete row.uniqueWeightedRealizationCount;
  });
  payload.telemetryBinding = "runtime telemetry is a separately validated non-semantic artifact";
  return Object.assign({}, payload, { contentAddress: { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest: sha256JSON(payload), canonicalBytes: Buffer.byteLength(canonicalStringify(payload), "utf8") } });
}

function validateSummaryBytes(summaryBytes, records, rawBytes, rawPath, provenance, options) {
  const errors = [], byteReport = validateJsonArtifactBytes(summaryBytes), summary = byteReport.artifact;
  options = options || {};
  errors.push.apply(errors, byteReport.errors);
  const parsedRaw = parseCanonicalJsonl(rawBytes, { expectedCount: EXPECTED_RECORDS });
  errors.push.apply(errors, parsedRaw.errors);
  if (!errors.length && canonicalStringify(parsedRaw.records) !== canonicalStringify(records)) errors.push("summary records differ from validated raw records");
  if (!errors.length && options.remeasure !== false) records.forEach(function (record, index) {
    const report = validateRecord(record, Base.expectedCensus()[index]);
    if (!report.valid) errors.push("record " + index + ": " + report.errors.join(", "));
  });
  if (!errors.length) {
    const rawBinding = { path: rawPath, bytes: rawBytes.length, sha256: sha256Bytes(rawBytes) };
    const expected = buildSummary(records, rawBinding, provenance);
    if (canonicalStringify(summary) !== canonicalStringify(expected)) errors.push("summary differs from deterministic full-payload rebuild");
  }
  return { valid: errors.length === 0, errors: errors, summary: summary };
}

module.exports = {
  ROOT: ROOT,
  VERSION: VERSION,
  SUPPLEMENT_DIGEST: SUPPLEMENT_DIGEST,
  SUPPLEMENT_FILE_SHA256: SUPPLEMENT_FILE_SHA256,
  REPAIR_AUDIT_SHA256: REPAIR_AUDIT_SHA256,
  REPAIR_AUDIT_COMMIT: REPAIR_AUDIT_COMMIT,
  CHUNK_SIZE: CHUNK_SIZE,
  EXPECTED_RECORDS: EXPECTED_RECORDS,
  EXPECTED_CHUNKS: EXPECTED_CHUNKS,
  Base: Base,
  SourceBoundary: SourceBoundary,
  canonicalStringify: canonicalStringify,
  sha256Bytes: sha256Bytes,
  sha256JSON: sha256JSON,
  serializeJsonArtifact: serializeJsonArtifact,
  validateJsonArtifactBytes: validateJsonArtifactBytes,
  loadPrerequisites: loadPrerequisites,
  independenceForPositive: independenceForPositive,
  independenceForControl: independenceForControl,
  buildRecord: buildRecord,
  validateRecord: validateRecord,
  replayRecord: replayRecord,
  serializeCanonicalJsonl: serializeCanonicalJsonl,
  parseCanonicalJsonl: parseCanonicalJsonl,
  sourceBinding: sourceBinding,
  buildChunkCertificate: buildChunkCertificate,
  validateChunk: validateChunk,
  buildSummary: buildSummary,
  validateSummaryBytes: validateSummaryBytes
};
