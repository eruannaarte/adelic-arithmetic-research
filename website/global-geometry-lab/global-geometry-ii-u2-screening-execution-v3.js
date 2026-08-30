/* Global Geometry II — screening-v3 execution container over the frozen v2 semantic kernel. */
"use strict";

const fs = require("fs");
const path = require("path");
const Semantic = require("./global-geometry-ii-u2-screening-v2.js");
const Supplement = require("./generate-global-geometry-ii-u2-screening-execution-v3-supplement.js");
const SourceBoundary = require("./generate-global-geometry-ii-u2-screening-source-boundary-v3.js");

const ROOT = Semantic.ROOT;
const SEMANTIC_BASE_VERSION = "screening-v2";
const SEMANTIC_PAYLOAD_VERSION = "screening-v3";
const EXECUTION_VERSION = "screening-v3";
const SUPPLEMENT_PATH = path.join(ROOT, "artifacts/global-geometry-ii/u2/screening/screening-execution-v3-supplement-v1.json");
const SUPPLEMENT_FILE_SHA256 = "7b796ba54d0e07a0deeb3877eb1834e9114e1c150e44d337d9aa44ca626ab500";
const SUPPLEMENT_DIGEST = "1524f69ef343a1048e3cfd05c9b4f6d93f9c6783233611094a345b3d4863885d";
const SEMANTIC_KERNEL_SHA256 = "3976809ec412580975852540166147d870c354672d055e243861ea7046e19873";
const SEMANTIC_SOURCE_BOUNDARY_FILE_SHA256 = "c60331209247fccee700d10d38b9ae03da3f81e9013f19281a1f5918fb9e6c73";
const SEMANTIC_SOURCE_BOUNDARY_DIGEST = "a1b1b9bb525ba9c172be48af60b9881a13ce58ebed9862a60fec18a25f07fae0";
const WINDOWS_V2_ABORT_FILE_SHA256 = "7550c5fec0aff5744a51e59e5958c45e363e5e6e0a49946c98307c4c6f1d7528";
const WINDOWS_V2_ABORT_DIGEST = "50108bc66bf8807772f9fef21baa35eea3e178e621de1958a9b7ddaef7ad6865";
const CHUNK_SIZE = Semantic.CHUNK_SIZE;
const EXPECTED_RECORDS = Semantic.EXPECTED_RECORDS;
const EXPECTED_CHUNKS = Semantic.EXPECTED_CHUNKS;

function clone(value) { return JSON.parse(JSON.stringify(value)); }
function canonicalStringify(value) { return Semantic.canonicalStringify(value); }
function sha256Bytes(value) { return Semantic.sha256Bytes(value); }
function sha256JSON(value) { return Semantic.sha256JSON(value); }
function serializeJsonArtifact(artifact) { return Buffer.from(JSON.stringify(artifact, null, 2) + "\n", "utf8"); }

function contentAddress(payload) {
  return { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest: sha256JSON(payload), canonicalBytes: Buffer.byteLength(canonicalStringify(payload), "utf8") };
}

function validateContentAddress(artifact) {
  if (!artifact || !artifact.contentAddress) return ["contentAddress missing"];
  const payload = clone(artifact), supplied = payload.contentAddress; delete payload.contentAddress;
  return canonicalStringify(supplied) === canonicalStringify(contentAddress(payload)) ? [] : ["contentAddress mismatch"];
}

function validateJsonArtifactBytes(bytes) {
  const errors = []; let artifact = null;
  try {
    if (!Buffer.isBuffer(bytes)) errors.push("artifact bytes must be a Buffer");
    artifact = JSON.parse(bytes.toString("utf8"));
    if (!serializeJsonArtifact(artifact).equals(bytes)) errors.push("artifact bytes are not exact pretty JSON followed by exactly one LF");
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors, artifact: artifact };
}

function semanticKernelBinding() {
  return {
    semanticBaseVersion: SEMANTIC_BASE_VERSION,
    semanticPayloadVersion: SEMANTIC_PAYLOAD_VERSION,
    recordSchema: "gg.u2.screening.record/3",
    implementationCommit: "1c3373267057b8a018ad5039e0f3b2b4e8eb2b1d",
    kernelPath: "website/global-geometry-lab/global-geometry-ii-u2-screening-v2.js",
    kernelSha256: SEMANTIC_KERNEL_SHA256,
    semanticSupplementDigest: Semantic.SUPPLEMENT_DIGEST,
    sourceBoundary: {
      path: "artifacts/global-geometry-ii/u2/screening/screening-v2/source-boundary-v2.json",
      fileSha256: SEMANTIC_SOURCE_BOUNDARY_FILE_SHA256,
      semanticDigest: SEMANTIC_SOURCE_BOUNDARY_DIGEST,
      commit: "ed624f4ff42b4e5488a1889c3d55ba1195e5a952"
    }
  };
}

function loadPrerequisites() {
  Semantic.loadPrerequisites();
  const supplementBytes = fs.readFileSync(SUPPLEMENT_PATH), supplement = JSON.parse(supplementBytes.toString("utf8"));
  if (sha256Bytes(supplementBytes) !== SUPPLEMENT_FILE_SHA256 || !supplement.contentAddress || supplement.contentAddress.digest !== SUPPLEMENT_DIGEST) throw new Error("screening-v3 execution supplement binding mismatch");
  const report = Supplement.validateSupplement(supplement);
  if (!report.valid) throw new Error("screening-v3 execution supplement validation failed: " + report.errors.join("; "));
  const kernelBytes = fs.readFileSync(path.join(ROOT, semanticKernelBinding().kernelPath));
  if (sha256Bytes(kernelBytes) !== SEMANTIC_KERNEL_SHA256) throw new Error("frozen screening-v2 semantic kernel mismatch");
  const boundaryBytes = fs.readFileSync(path.join(ROOT, semanticKernelBinding().sourceBoundary.path));
  if (sha256Bytes(boundaryBytes) !== SEMANTIC_SOURCE_BOUNDARY_FILE_SHA256 || JSON.parse(boundaryBytes).contentAddress.digest !== SEMANTIC_SOURCE_BOUNDARY_DIGEST) throw new Error("semantic source-boundary mismatch");
  const abortPath = path.join(ROOT, "artifacts/global-geometry-ii/u2/screening/screening-windows-preflight-abort-v2.json"), abortBytes = fs.readFileSync(abortPath), abort = JSON.parse(abortBytes.toString("utf8"));
  if (sha256Bytes(abortBytes) !== WINDOWS_V2_ABORT_FILE_SHA256 || !abort.contentAddress || abort.contentAddress.digest !== WINDOWS_V2_ABORT_DIGEST) throw new Error("Windows v2 abort binding mismatch");
  if (abort.schema !== "gg.u2.screening.windows-blocker-certificate/1" || abort.outcome.u2Status !== "UNRESOLVED" || abort.outcome.decisionAuthority !== "NONE") throw new Error("Windows v2 abort metadata is not fail-closed");
  return { supplement: supplement, semanticKernel: semanticKernelBinding(), windowsV2Abort: { path: path.relative(ROOT, abortPath).split(path.sep).join("/"), sha256: WINDOWS_V2_ABORT_FILE_SHA256, semanticDigest: WINDOWS_V2_ABORT_DIGEST } };
}

function sourceBinding(boundaryBytes, mode, pins, adapters, boundaryPath) {
  const report = SourceBoundary.verifyBoundaryBytes(boundaryBytes, mode, pins, adapters);
  if (!report.valid) throw new Error("screening-v3 source boundary verification failed: " + report.errors.join("; "));
  return {
    path: boundaryPath || "artifacts/global-geometry-ii/u2/screening/screening-v3/source-boundary-v3.json",
    fileSha256: pins.fileSha256,
    semanticDigest: pins.semanticSha256,
    sourceCommit: report.artifact.sourceCommit,
    sourceTree: report.artifact.sourceTree,
    verificationMode: mode
  };
}

function adaptSmallWorldLedger(payload) {
  if (!payload || !payload.identity || payload.identity.kind !== "control" || payload.identity.id !== "small-world-shortcuts") return payload;
  if (!payload.controlDiscriminant || payload.controlDiscriminant.targetShortcutCount !== undefined) return payload;
  const metadata = payload.construction && payload.construction.metadata;
  if (!metadata || !Number.isSafeInteger(metadata.targetShortcutCount) || metadata.targetShortcutCount < 0) throw new Error("small-world v3 adapter requires construction.metadata.targetShortcutCount");
  const omittedTargetFailure = "small-world accepted " + payload.controlDiscriminant.acceptedShortcutCount + " of undefined preregistered shortcuts";
  payload.controlDiscriminant.targetShortcutCount = metadata.targetShortcutCount;
  payload.failures = payload.failures.filter(function (failure) {
    return !(failure.code === "INVALID_COMPLEX" && failure.channel === "control-shortfall" && failure.detail === omittedTargetFailure);
  });
  if (payload.controlDiscriminant.acceptedShortcutCount !== metadata.targetShortcutCount) {
    payload.failures.push({ code: "INVALID_COMPLEX", channel: "control-shortfall", detail: "small-world accepted " + payload.controlDiscriminant.acceptedShortcutCount + " of " + metadata.targetShortcutCount + " preregistered shortcuts" });
  }
  payload.construction.declaredParametersRealized = !payload.failures.some(function (failure) { return failure.channel === "control-shortfall"; });
  return payload;
}

function buildRecord(identity) {
  const payload = clone(Semantic.buildRecord(identity));
  delete payload.recordHash;
  adaptSmallWorldLedger(payload);
  payload.schema = "gg.u2.screening.record/3";
  payload.semanticBaseSupplementDigest = payload.supplementDigest;
  delete payload.supplementDigest;
  payload.semanticBaseImplementation = payload.implementation;
  payload.implementation = { version: "3.0.0-screening", semanticBaseVersion: SEMANTIC_BASE_VERSION, amendment: "small-world-no-bulk-root-target-ledger-v1" };
  payload.semanticBase = semanticKernelBinding();
  payload.semanticPayloadVersion = SEMANTIC_PAYLOAD_VERSION;
  payload.executionSupplementDigest = SUPPLEMENT_DIGEST;
  payload.semanticAmendment = {
    id: "small-world-no-bulk-root-target-ledger-v1",
    scope: "restore omitted targetShortcutCount from construction metadata and re-evaluate only the shortcut-count shortfall against it",
    numericalEstimatorChange: "NONE"
  };
  return Object.assign({}, payload, { recordHash: sha256JSON(payload) });
}

function validateRecord(record, identity, options) {
  const errors = []; options = options || {};
  try {
    if (!record || record.schema !== "gg.u2.screening.record/3" || record.semanticPayloadVersion !== SEMANTIC_PAYLOAD_VERSION || record.executionSupplementDigest !== SUPPLEMENT_DIGEST) errors.push("v3 record identity/binding mismatch");
    if (identity && canonicalStringify(record.identity) !== canonicalStringify(identity)) errors.push("v3 record census identity mismatch");
    const supplied = clone(record), suppliedHash = supplied.recordHash; delete supplied.recordHash;
    if (suppliedHash !== sha256JSON(supplied)) errors.push("v3 recordHash mismatch");
    if (!record.screenInterpretation || record.screenInterpretation.u2Status !== "UNRESOLVED" || record.screenInterpretation.decisionAuthority !== "NONE") errors.push("v3 record is not fail-closed");
    if (record.identity && record.identity.kind === "control") {
      const shortfall = record.failures.some(function (failure) { return failure.channel === "control-shortfall"; });
      if (!record.construction || record.construction.declaredParametersRealized !== !shortfall) errors.push("declaredParametersRealized must equal absence of control-shortfall");
    }
    if (options.remeasure !== false && !errors.length) {
      const rebuilt = buildRecord(record.identity);
      if (canonicalStringify(record) !== canonicalStringify(rebuilt)) errors.push("v3 record differs from fresh v2-base plus closed adapter rebuild");
    }
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

function buildChunkCertificate(index, records, chunkBytes, chunkPath, source) {
  if (!Number.isInteger(index) || index < 0 || index >= EXPECTED_CHUNKS || records.length !== CHUNK_SIZE) throw new Error("invalid v3 chunk certificate input");
  const payload = {
    schema: "gg.u2.screening.chunk-certificate/3",
    executionVersion: EXECUTION_VERSION,
    semanticPayloadVersion: SEMANTIC_PAYLOAD_VERSION,
    semanticKernel: semanticKernelBinding(),
    executionSupplementDigest: SUPPLEMENT_DIGEST,
    chunkIndex: index,
    ordinalRange: [index * CHUNK_SIZE, index * CHUNK_SIZE + CHUNK_SIZE - 1],
    recordCount: records.length,
    firstRunId: records[0].identity.runId,
    lastRunId: records[records.length - 1].identity.runId,
    chunk: { path: chunkPath, bytes: chunkBytes.length, sha256: sha256Bytes(chunkBytes), recordMerkleRoot: Semantic.Base.merkleRoot(records.map(function (record) { return record.recordHash; })) },
    sourceBoundary: clone(source),
    outcome: { u2Status: "UNRESOLVED", decisionAuthority: "NONE" }
  };
  return Object.assign({}, payload, { contentAddress: contentAddress(payload) });
}

function validateChunk(chunkBytes, certificateBytes, index, chunkPath, source, options) {
  const errors = [], parsed = Semantic.parseCanonicalJsonl(chunkBytes, { expectedCount: CHUNK_SIZE }), certificateReport = validateJsonArtifactBytes(certificateBytes), certificate = certificateReport.artifact;
  options = options || {};
  errors.push.apply(errors, parsed.errors); errors.push.apply(errors, certificateReport.errors);
  const census = Semantic.Base.expectedCensus(), start = index * CHUNK_SIZE;
  if (!parsed.errors.length) parsed.records.forEach(function (record, offset) {
    const report = validateRecord(record, census[start + offset], { remeasure: options.remeasure !== false });
    if (!report.valid) errors.push("record " + (start + offset) + ": " + report.errors.join(", "));
  });
  if (!errors.length) {
    const expected = buildChunkCertificate(index, parsed.records, chunkBytes, chunkPath, source);
    if (canonicalStringify(certificate) !== canonicalStringify(expected)) errors.push("v3 chunk certificate differs from deterministic full rebuild");
  }
  return { valid: errors.length === 0, errors: errors, records: parsed.records, certificate: certificate };
}

function buildSummaryEnvelope(records, rawBinding, checkpointBinding, source) {
  const semanticProvenance = { sourceBoundary: semanticKernelBinding().sourceBoundary, checkpointManifest: clone(checkpointBinding) };
  const semanticSummary = clone(Semantic.buildSummary(records, rawBinding, semanticProvenance));
  delete semanticSummary.contentAddress;
  semanticSummary.schema = "gg.u2.screening.semantic-summary/3";
  semanticSummary.screeningId = "ggii-u2-screening-v3";
  semanticSummary.screeningVersion = SEMANTIC_PAYLOAD_VERSION;
  semanticSummary.semanticBaseSupplementDigest = semanticSummary.supplementDigest;
  delete semanticSummary.supplementDigest;
  semanticSummary.semanticBaseImplementation = semanticSummary.implementation;
  semanticSummary.implementation = { version: "3.0.0-screening", semanticBaseVersion: SEMANTIC_BASE_VERSION, amendment: "small-world-no-bulk-root-target-ledger-v1" };
  semanticSummary.semanticBase = semanticKernelBinding();
  semanticSummary.executionSupplementDigest = SUPPLEMENT_DIGEST;
  semanticSummary.semanticAmendment = "small-world-no-bulk-root-target-ledger-v1";
  semanticSummary.contentAddress = contentAddress(semanticSummary);
  const payload = {
    schema: "gg.u2.screening.summary-envelope/3",
    executionVersion: EXECUTION_VERSION,
    semanticPayloadVersion: SEMANTIC_PAYLOAD_VERSION,
    semanticKernel: semanticKernelBinding(),
    executionSupplementDigest: SUPPLEMENT_DIGEST,
    sourceBoundary: clone(source),
    raw: clone(rawBinding),
    checkpointManifest: clone(checkpointBinding),
    semanticSummary: semanticSummary,
    outcome: { u2Status: "UNRESOLVED", decisionAuthority: "NONE" }
  };
  return Object.assign({}, payload, { contentAddress: contentAddress(payload) });
}

function validateSummaryEnvelopeBytes(bytes, records, rawBytes, rawPath, checkpointBinding, source, options) {
  const report = validateJsonArtifactBytes(bytes), errors = report.errors.slice(), artifact = report.artifact;
  options = options || {};
  if (!Array.isArray(records) || (!options.allowIncompleteCensusForTest && records.length !== EXPECTED_RECORDS)) errors.push("v3 summary validation requires the complete registered census");
  if (!errors.length) {
    errors.push.apply(errors, validateContentAddress(artifact));
    const rawBinding = { path: rawPath, bytes: rawBytes.length, sha256: sha256Bytes(rawBytes) };
    const expected = buildSummaryEnvelope(records, rawBinding, checkpointBinding, source);
    if (canonicalStringify(artifact) !== canonicalStringify(expected)) errors.push("v3 summary envelope differs from deterministic full rebuild");
    if (options.remeasure !== false) records.forEach(function (record, index) {
      const recordReport = validateRecord(record, Semantic.Base.expectedCensus()[index], { remeasure: true });
      if (!recordReport.valid) errors.push("record " + index + ": " + recordReport.errors.join(", "));
    });
  }
  return { valid: errors.length === 0, errors: errors, summary: artifact };
}

module.exports = {
  ROOT: ROOT,
  Semantic: Semantic,
  Supplement: Supplement,
  SourceBoundary: SourceBoundary,
  SEMANTIC_BASE_VERSION: SEMANTIC_BASE_VERSION,
  SEMANTIC_PAYLOAD_VERSION: SEMANTIC_PAYLOAD_VERSION,
  EXECUTION_VERSION: EXECUTION_VERSION,
  SUPPLEMENT_PATH: SUPPLEMENT_PATH,
  SUPPLEMENT_FILE_SHA256: SUPPLEMENT_FILE_SHA256,
  SUPPLEMENT_DIGEST: SUPPLEMENT_DIGEST,
  CHUNK_SIZE: CHUNK_SIZE,
  EXPECTED_RECORDS: EXPECTED_RECORDS,
  EXPECTED_CHUNKS: EXPECTED_CHUNKS,
  clone: clone,
  canonicalStringify: canonicalStringify,
  sha256Bytes: sha256Bytes,
  sha256JSON: sha256JSON,
  serializeJsonArtifact: serializeJsonArtifact,
  contentAddress: contentAddress,
  validateContentAddress: validateContentAddress,
  validateJsonArtifactBytes: validateJsonArtifactBytes,
  semanticKernelBinding: semanticKernelBinding,
  loadPrerequisites: loadPrerequisites,
  sourceBinding: sourceBinding,
  buildRecord: buildRecord,
  adaptSmallWorldLedger: adaptSmallWorldLedger,
  validateRecord: validateRecord,
  buildChunkCertificate: buildChunkCertificate,
  validateChunk: validateChunk,
  buildSummaryEnvelope: buildSummaryEnvelope,
  validateSummaryEnvelopeBytes: validateSummaryEnvelopeBytes
};
