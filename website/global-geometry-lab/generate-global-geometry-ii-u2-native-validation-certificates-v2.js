#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { performance } = require("perf_hooks");
const Strict = require("./global-geometry-ii-u2.js");
const Screen = require("./global-geometry-ii-u2-screening-execution-v3.js");
const Eval = require("./generate-global-geometry-ii-u2-evaluation-index-v2.js");

const ROOT = Eval.ROOT;
const SCRIPT_PATH = "website/global-geometry-lab/generate-global-geometry-ii-u2-native-validation-certificates-v2.js";
function resolve(relative) { return path.join(ROOT, relative); }
function platformLabel() {
  if (process.platform === "darwin") return "macos";
  if (process.platform === "win32") return "windows";
  throw new Error("native validation certificates require darwin or win32");
}
function strictCertificatePath(label) { return "artifacts/global-geometry-ii/u2/strict-partial/" + label + "/u2-strict-partial-" + label + "-validation-certificate-v2.json"; }
function screeningCertificatePath(label) { return "artifacts/global-geometry-ii/u2/screening/screening-v3/" + label + "/screening-v3-" + label + "-validation-certificate-v2.json"; }

function bindFile(relative, semantic) {
  const bytes = fs.readFileSync(resolve(relative)), binding = { path: relative, bytes: bytes.length, sha256: Eval.sha256Bytes(bytes), semanticDigest: null };
  if (semantic) {
    const artifact = JSON.parse(bytes.toString("utf8")), report = Eval.validateContentAddress(artifact);
    if (!report.valid) throw new Error(relative + " invalid semantic content address: " + report.errors.join("; "));
    binding.semanticDigest = artifact.contentAddress.digest;
  }
  return binding;
}

function captureFile(relative, semantic) {
  const loaded = Eval.bindBytes(relative, { json: semantic });
  return { bytes: loaded.bytes, artifact: loaded.artifact, binding: Object.assign({}, loaded.binding, { semanticDigest: loaded.binding.semanticDigest === undefined ? null : loaded.binding.semanticDigest }) };
}

function assertBindingsUnchanged(bindings, label) {
  Object.keys(bindings).forEach(function (key) {
    const binding = bindings[key], observed = bindFile(binding.path, binding.semanticDigest !== null);
    if (Eval.canonicalStringify(observed) !== Eval.canonicalStringify(binding)) throw new Error(label + " changed during native validation: " + key + " (" + binding.path + ")");
  });
}

function assertSnapshotUnchanged(snapshot, label) {
  assertBindingsUnchanged(snapshot.sourceBindings, label + " source");
  const artifactBindings = {};
  Object.keys(snapshot.artifacts).forEach(function (key) { if (snapshot.artifacts[key]) artifactBindings[key] = snapshot.artifacts[key].binding; });
  assertBindingsUnchanged(artifactBindings, label + " artifact");
}

function containsAbsolutePathToken(value) {
  return typeof value === "string" && (value.includes(ROOT) || /(^|=)(\/|[A-Za-z]:[\\/])/.test(value));
}

function sourceBindings() {
  return {
    certificateBuilder: bindFile("website/global-geometry-lab/generate-global-geometry-ii-u2-native-validation-certificates-v2.js", false),
    evaluationBuilder: bindFile("website/global-geometry-lab/generate-global-geometry-ii-u2-evaluation-index-v2.js", false),
    strictValidator: bindFile("website/global-geometry-lab/global-geometry-ii-u2.js", false),
    strictSourceBoundaryValidator: bindFile("website/global-geometry-lab/global-geometry-ii-u2-source-boundary.js", false),
    screeningSemanticBase: bindFile("website/global-geometry-lab/global-geometry-ii-u2-screening-v2.js", false),
    screeningV3Adapter: bindFile("website/global-geometry-lab/global-geometry-ii-u2-screening-execution-v3.js", false),
    screeningV3Runner: bindFile("website/global-geometry-lab/run-global-geometry-ii-u2-screening-execution-v3.js", false),
    screeningSourceBoundary: bindFile("artifacts/global-geometry-ii/u2/screening/screening-v3/source-boundary-v3.json", true)
  };
}

function invocation(mode) {
  const execArgv = process.execArgv.slice();
  if (execArgv.some(containsAbsolutePathToken)) throw new Error("refusing privacy-sensitive absolute path in process.execArgv");
  const command = ["node"].concat(execArgv, [SCRIPT_PATH, mode]).join(" ");
  return { executable: "node", execArgv: execArgv, script: SCRIPT_PATH, mode: mode, argv: [SCRIPT_PATH, mode], command: command };
}

function environment(label, execution) {
  return { environmentClass: "native-" + label + "-" + process.arch + "-node-" + process.versions.node, platformLabel: label, platform: process.platform, arch: process.arch, node: process.version, execArgv: execution.execArgv.slice() };
}

function buildStrictNativeCertificate(label, execution) {
  const input = Eval.INPUTS.strict[label], startedAt = new Date().toISOString(), started = performance.now(), priorCertificatePath = input.certificate && input.certificate !== strictCertificatePath(label) ? input.certificate : null, snapshot = {
    sourceBindings: sourceBindings(),
    artifacts: { normalization: captureFile(input.normalization, true), campaign: captureFile(input.campaign, true), priorHostCertificate: priorCertificatePath ? captureFile(priorCertificatePath, true) : null }
  }, normalization = snapshot.artifacts.normalization.artifact, campaign = snapshot.artifacts.campaign.artifact, normalizationReport = Strict.validateCalibration(normalization), campaignReport = normalizationReport.valid ? Strict.validateCampaign(campaign, normalization) : { valid: false, errors: ["campaign withheld because normalization failed"], semanticReplayCounts: null };
  if (!normalizationReport.valid || !campaignReport.valid) throw new Error(label + " native strict validator failed: " + normalizationReport.errors.concat(campaignReport.errors).join("; "));
  assertSnapshotUnchanged(snapshot, label + " strict snapshot");
  const payload = {
    schema: "gg.u2.evaluation.native-strict-validation-certificate/2",
    semanticRole: "write-once evidence that the frozen strict numerical validators actually replayed on the artifact's native host class",
    command: execution.command,
    invocation: JSON.parse(JSON.stringify(execution)),
    validationPolicy: "invoke Strict.validateCalibration and Strict.validateCampaign on exact native-host artifact bytes; any error prevents certificate creation",
    environment: environment(label, execution),
    sourceBindings: snapshot.sourceBindings,
    artifactSourceBoundary: campaign.sourceBoundary,
    artifacts: { normalization: snapshot.artifacts.normalization.binding, campaign: snapshot.artifacts.campaign.binding, priorHostCertificate: snapshot.artifacts.priorHostCertificate ? snapshot.artifacts.priorHostCertificate.binding : null },
    validation: {
      normalization: { status: "PASS_NATIVE", recordsRemeasured: 384 },
      campaign: { status: "PASS_NATIVE", positiveRecordsRemeasured: campaignReport.semanticReplayCounts.positive, controlRecordsRemeasured: campaignReport.semanticReplayCounts.controls, calibrationRecordsRemeasured: campaignReport.semanticReplayCounts.calibration },
      conclusion: campaign.conclusion.status
    },
    timing: { startedAt: startedAt, completedAt: new Date().toISOString(), elapsedMilliseconds: performance.now() - started },
    outcome: { u2Status: "UNRESOLVED", acceptanceAllowed: false, rejectionClaimed: false, decisionAuthority: "NONE" }
  };
  return Eval.addressed(payload);
}

function buildScreeningNativeCertificate(label, execution) {
  const directory = Eval.INPUTS.screening[label], paths = Eval.screeningPaths(directory), startedAt = new Date().toISOString(), started = performance.now(), snapshot = {
    sourceBindings: sourceBindings(),
    artifacts: { raw: captureFile(paths.raw, false), summary: captureFile(paths.summary, true), runtime: captureFile(paths.runtime, true), checkpoint: captureFile(paths.checkpoint, true), writerCapability: captureFile(paths.writer, true) }
  }, hostProjection = Eval.buildScreenHostProjectionFromLoaded(label, directory, snapshot.artifacts.raw, { nativeCertificateRequired: false, containerLoads: { summary: snapshot.artifacts.summary, runtime: snapshot.artifacts.runtime, checkpoint: snapshot.artifacts.checkpoint, writer: snapshot.artifacts.writerCapability } }), parsed = Screen.Semantic.parseCanonicalJsonl(snapshot.artifacts.raw.bytes, { expectedCount: Screen.EXPECTED_RECORDS }), census = Screen.Semantic.Base.expectedCensus();
  if (!parsed.valid) throw new Error(label + " native screening parse failed: " + parsed.errors.join("; "));
  parsed.records.forEach(function (record, index) {
    const report = Screen.validateRecord(record, census[index], { remeasure: true });
    if (!report.valid) throw new Error(label + " native screening semantic replay failed at record " + index + ": " + report.errors.join("; "));
  });
  assertSnapshotUnchanged(snapshot, label + " screening snapshot");
  const summary = snapshot.artifacts.summary.artifact;
  const payload = {
    schema: "gg.u2.evaluation.native-screening-v3-validation-certificate/2",
    semanticRole: "write-once evidence that every screening-v3 record and all published containers actually replayed on the artifact's native host class",
    command: execution.command,
    invocation: JSON.parse(JSON.stringify(execution)),
    validationPolicy: "validate raw census/order/hash, freshly rebuild every record with Screen.validateRecord remeasure=true, and replay summary/runtime/writer/checkpoint bindings; any error prevents certificate creation",
    environment: environment(label, execution),
    sourceBindings: snapshot.sourceBindings,
    artifactSourceBoundary: summary.sourceBoundary,
    artifacts: {
      raw: snapshot.artifacts.raw.binding,
      summary: snapshot.artifacts.summary.binding,
      runtime: snapshot.artifacts.runtime.binding,
      checkpoint: snapshot.artifacts.checkpoint.binding,
      writerCapability: snapshot.artifacts.writerCapability.binding
    },
    validation: {
      status: "PASS_NATIVE",
      recordsRemeasured: parsed.records.length,
      expectedRecords: Screen.EXPECTED_RECORDS,
      recordHashProjection: hostProjection.recordHashProjection,
      scientificSummaryProjection: hostProjection.scientificSummaryProjection,
      screeningOutcome: hostProjection.screenOutcome.u2Status,
      containerDecisionAuthority: hostProjection.containerOutcome.decisionAuthority
    },
    timing: { startedAt: startedAt, completedAt: new Date().toISOString(), elapsedMilliseconds: performance.now() - started },
    outcome: { u2Status: "UNRESOLVED", acceptanceAllowed: false, rejectionClaimed: false, decisionAuthority: "NONE" }
  };
  return Eval.addressed(payload);
}

function validateCertificate(artifact, expectedSchema, label) {
  const errors = [], address = Eval.validateContentAddress(artifact);
  errors.push.apply(errors, address.errors);
  try {
    if (!artifact || artifact.schema !== expectedSchema || artifact.environment.platformLabel !== label) errors.push("native certificate identity mismatch");
    if (!artifact.invocation || artifact.invocation.executable !== "node" || Object.prototype.hasOwnProperty.call(artifact.invocation, "executablePath") || !Array.isArray(artifact.invocation.execArgv) || artifact.invocation.execArgv.some(containsAbsolutePathToken) || artifact.invocation.script !== SCRIPT_PATH || !["--write-native-all", "--write-native-screening"].includes(artifact.invocation.mode) || Eval.canonicalStringify(artifact.invocation.argv) !== Eval.canonicalStringify([SCRIPT_PATH, artifact.invocation.mode]) || artifact.command !== artifact.invocation.command || Eval.canonicalStringify(artifact.environment.execArgv) !== Eval.canonicalStringify(artifact.invocation.execArgv)) errors.push("native certificate invocation metadata mismatch");
    if (!artifact.validation || (artifact.validation.status && artifact.validation.status !== "PASS_NATIVE") || (artifact.validation.campaign && artifact.validation.campaign.status !== "PASS_NATIVE")) errors.push("native validation did not pass");
    if (!artifact.timing || !(artifact.timing.elapsedMilliseconds >= 0) || Number.isNaN(Date.parse(artifact.timing.startedAt)) || Number.isNaN(Date.parse(artifact.timing.completedAt))) errors.push("native certificate timing invalid");
    if (!artifact.outcome || artifact.outcome.u2Status !== "UNRESOLVED" || artifact.outcome.acceptanceAllowed || artifact.outcome.rejectionClaimed || artifact.outcome.decisionAuthority !== "NONE") errors.push("native certificate is not fail-closed");
    Object.values(artifact.sourceBindings || {}).forEach(function (binding) { const observed = bindFile(binding.path, binding.semanticDigest !== null); if (Eval.canonicalStringify(observed) !== Eval.canonicalStringify(binding)) errors.push("source binding mismatch: " + binding.path); });
    Object.values(artifact.artifacts || {}).filter(Boolean).forEach(function (binding) { const observed = bindFile(binding.path, binding.semanticDigest !== null); if (Eval.canonicalStringify(observed) !== Eval.canonicalStringify(binding)) errors.push("artifact binding mismatch: " + binding.path); });
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

function writeOnce(relative, artifact) {
  const output = resolve(relative), bytes = Eval.serializeArtifact(artifact);
  if (fs.existsSync(output)) throw new Error("refusing to overwrite native validation certificate: " + relative);
  fs.mkdirSync(path.dirname(output), { recursive: true });
  const descriptor = fs.openSync(output, "wx");
  try { fs.writeFileSync(descriptor, bytes); fs.fsyncSync(descriptor); } finally { fs.closeSync(descriptor); }
  if (!fs.readFileSync(output).equals(bytes)) throw new Error("native certificate exact postflight mismatch: " + relative);
  return { path: relative, bytes: bytes.length, sha256: Eval.sha256Bytes(bytes), semanticDigest: artifact.contentAddress.digest };
}

function main(argv) {
  if (argv.length !== 1 || !["--write-native-all", "--write-native-screening"].includes(argv[0])) throw new Error("usage: generate-global-geometry-ii-u2-native-validation-certificates-v2.js --write-native-all|--write-native-screening");
  const label = platformLabel(), execution = invocation(argv[0]), outputs = {};
  let strict = null;
  if (argv[0] === "--write-native-all") {
    strict = buildStrictNativeCertificate(label, execution);
  }
  const screening = buildScreeningNativeCertificate(label, execution), reports = [];
  if (strict) reports.push(validateCertificate(strict, "gg.u2.evaluation.native-strict-validation-certificate/2", label));
  reports.push(validateCertificate(screening, "gg.u2.evaluation.native-screening-v3-validation-certificate/2", label));
  const errors = reports.flatMap(function (report) { return report.errors; }); if (errors.length) throw new Error(errors.join("; "));
  const targets = [];
  if (strict) targets.push(strictCertificatePath(label)); targets.push(screeningCertificatePath(label));
  targets.forEach(function (target) { if (fs.existsSync(resolve(target))) throw new Error("refusing partial write because a native certificate already exists: " + target); });
  if (strict) outputs.strict = writeOnce(strictCertificatePath(label), strict);
  outputs.screening = writeOnce(screeningCertificatePath(label), screening);
  process.stdout.write(JSON.stringify({ status: "WROTE_NATIVE_VALIDATION_CERTIFICATES", platformLabel: label, outputs: outputs, u2Status: "UNRESOLVED", decisionAuthority: "NONE" }) + "\n");
}

if (require.main === module) main(process.argv.slice(2));
module.exports = { ROOT: ROOT, SCRIPT_PATH: SCRIPT_PATH, platformLabel: platformLabel, strictCertificatePath: strictCertificatePath, screeningCertificatePath: screeningCertificatePath, bindFile: bindFile, captureFile: captureFile, assertBindingsUnchanged: assertBindingsUnchanged, assertSnapshotUnchanged: assertSnapshotUnchanged, containsAbsolutePathToken: containsAbsolutePathToken, sourceBindings: sourceBindings, invocation: invocation, environment: environment, buildStrictNativeCertificate: buildStrictNativeCertificate, buildScreeningNativeCertificate: buildScreeningNativeCertificate, validateCertificate: validateCertificate, writeOnce: writeOnce };
