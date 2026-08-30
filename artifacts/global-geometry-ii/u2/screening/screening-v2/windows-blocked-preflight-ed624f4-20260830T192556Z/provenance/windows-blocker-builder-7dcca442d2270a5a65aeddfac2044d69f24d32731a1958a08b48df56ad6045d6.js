#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const RUN_ID = "screening-v2-ed624f4-20260830T192556Z";
const RUN_ROOT = "C:\\Users\\Public\\ggii-u2-replication\\runs\\" + RUN_ID;
const SOURCE_ROOT = path.join(RUN_ROOT, "source");
const OUTPUT_ROOT = path.join(SOURCE_ROOT, "artifacts/global-geometry-ii/u2/screening/screening-v2/windows");
const PROVENANCE_ROOT = path.join(RUN_ROOT, "provenance");
const LOG_ROOT = path.join(RUN_ROOT, "logs");
const PID = 1240;

function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function canonical(value) {
  if (value === null || typeof value === "string" || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "number") {
    if (!Number.isFinite(value) || Object.is(value, -0)) throw new Error("invalid canonical number");
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return "[" + value.map(canonical).join(",") + "]";
  if (!value || typeof value !== "object" || Object.getPrototypeOf(value) !== Object.prototype) throw new Error("canonical input must be plain JSON");
  return "{" + Object.keys(value).sort().map((key) => JSON.stringify(key) + ":" + canonical(value[key])).join(",") + "}";
}
function relativeToRun(file) { return path.relative(RUN_ROOT, file).split(path.sep).join("/"); }
function describe(file) {
  const bytes = fs.readFileSync(file);
  return { path: relativeToRun(file), bytes: bytes.length, sha256: sha256(bytes) };
}
function copyContentAddressed(source, directory, stem, extension) {
  const bytes = fs.readFileSync(source), digest = sha256(bytes), target = path.join(directory, stem + "." + digest + extension);
  if (fs.existsSync(target)) {
    if (!fs.readFileSync(target).equals(bytes)) throw new Error("content-addressed target collision: " + target);
  } else {
    fs.copyFileSync(source, target, fs.constants.COPYFILE_EXCL);
  }
  return describe(target);
}
function listFiles(root) {
  const results = [];
  if (!fs.existsSync(root)) return results;
  const visit = (directory) => {
    fs.readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name)).forEach((entry) => {
      const full = path.join(directory, entry.name);
      if (entry.isDirectory()) visit(full);
      else if (entry.isFile()) results.push({ path: path.relative(root, full).split(path.sep).join("/"), bytes: fs.statSync(full).size, sha256: sha256(fs.readFileSync(full)) });
      else throw new Error("unexpected non-file output entry: " + full);
    });
  };
  visit(root);
  return results;
}

fs.mkdirSync(PROVENANCE_ROOT, { recursive: true });
const blockerPath = path.join(PROVENANCE_ROOT, "windows-screening-v2-blocker.json");
if (fs.existsSync(blockerPath)) throw new Error("refusing to overwrite blocker certificate");

const sourceBoundary = path.join(SOURCE_ROOT, "artifacts/global-geometry-ii/u2/screening/screening-v2/source-boundary-v2.json");
const sourceBoundaryBytes = fs.readFileSync(sourceBoundary);
if (sha256(sourceBoundaryBytes) !== "c60331209247fccee700d10d38b9ae03da3f81e9013f19281a1f5918fb9e6c73") throw new Error("boundary hash changed before blocker certification");
const boundaryArtifact = JSON.parse(sourceBoundaryBytes.toString("utf8"));
if (!boundaryArtifact.contentAddress || boundaryArtifact.contentAddress.digest !== "a1b1b9bb525ba9c172be48af60b9881a13ce58ebed9862a60fec18a25f07fae0") throw new Error("boundary semantic digest changed");

const stderrPath = path.join(LOG_ROOT, "runner.stderr.working.log");
const stdoutPath = path.join(LOG_ROOT, "runner.stdout.working.log");
const dispatchPath = path.join(PROVENANCE_ROOT, "runner-dispatch.json");
const transferPath = path.join(PROVENANCE_ROOT, "transfer-verification.json");
const runLockPath = path.join(OUTPUT_ROOT, ".run-lock.json");
const probePath = "C:\\Users\\Public\\ggii-u2-replication\\fsync-probes\\screening-v2-jG4bUH\\windows-fsync-matrix.json";
const requiredEvidence = [stderrPath, stdoutPath, dispatchPath, transferPath, runLockPath, probePath];
requiredEvidence.forEach((file) => { if (!fs.existsSync(file)) throw new Error("required blocker evidence missing: " + file); });

const stdoutBytes = fs.readFileSync(stdoutPath), stderrBytes = fs.readFileSync(stderrPath);
const stderrText = stderrBytes.toString("utf8");
if (stdoutBytes.length !== 0) throw new Error("runner stdout is nonempty; no-record boundary cannot be certified by this script");
if (sha256(stderrBytes) !== "acd406fe2d51a5f304bf3bd021bbd2827195043c9739b53cb6de224f4959d58a") throw new Error("runner stderr hash changed");
for (const fragment of ["Error: EPERM: operation not permitted, fsync", "durableWriteNoReplace", "run-global-geometry-ii-u2-screening-v2.js:71:14", "code: 'EPERM'", "syscall: 'fsync'", "Node.js v22.22.2"]) {
  if (!stderrText.includes(fragment)) throw new Error("stderr lacks expected failure fragment: " + fragment);
}

const outputCensus = listFiles(OUTPUT_ROOT);
if (outputCensus.length !== 1 || outputCensus[0].path !== ".run-lock.json") throw new Error("scientific output census is not exactly the incomplete run lock");
if (outputCensus[0].bytes !== 800 || outputCensus[0].sha256 !== "8b6a012c91348bf233e837c3cfbf71de191234aa7c1e666db20479d17f0dc26a") throw new Error("run lock evidence changed");
const forbiddenFinals = ["screening-raw-v2.jsonl", "screening-summary-v2.json", "screening-runtime-v2.json", "screening-checkpoint-manifest-v2.json"];
if (forbiddenFinals.some((name) => fs.existsSync(path.join(OUTPUT_ROOT, name)))) throw new Error("a final artifact exists; no-record boundary refused");
const chunksRoot = path.join(OUTPUT_ROOT, "chunks");
const chunkFiles = listFiles(chunksRoot);
if (chunkFiles.length !== 0) throw new Error("chunk records exist; no-record boundary refused");

let pidExited = false;
try { process.kill(PID, 0); }
catch (error) { if (error && error.code === "ESRCH") pidExited = true; else throw error; }
if (!pidExited) throw new Error("dispatched PID is present; blocker certificate refused");

const probe = JSON.parse(fs.readFileSync(probePath, "utf8"));
if (!probe.contentAddress || probe.contentAddress.digest !== "944adfe7c17463bae1e95ac808a2df4032647154dc6dbfbc45a8e77d6dc90b32") throw new Error("fsync probe digest changed");
const preserved = {
  stderr: copyContentAddressed(stderrPath, LOG_ROOT, "runner.stderr", ".log"),
  stdout: copyContentAddressed(stdoutPath, LOG_ROOT, "runner.stdout", ".log"),
  dispatch: copyContentAddressed(dispatchPath, PROVENANCE_ROOT, "runner-dispatch", ".json"),
  incompleteRunLock: copyContentAddressed(runLockPath, PROVENANCE_ROOT, "incomplete-run-lock", ".json"),
  fsyncMatrix: copyContentAddressed(probePath, PROVENANCE_ROOT, "windows-fsync-matrix", ".json")
};

const nodePath = "C:\\Users\\Public\\ggii-u2-replication\\runtime\\node-v22.22.2-win-x64\\node.exe";
const payload = {
  schema: "gg.u2.screening.windows-blocker-certificate/1",
  semanticRole: "sanitized pre-measurement execution blocker; no scientific inference or decision authority",
  runId: RUN_ID,
  status: "BLOCKED_BEFORE_RECORD_0",
  source: {
    implementationCommit: "1c3373267057b8a018ad5039e0f3b2b4e8eb2b1d",
    implementationTree: boundaryArtifact.sourceTree,
    boundaryCommit: "ed624f4ff42b4e5488a1889c3d55ba1195e5a952",
    boundaryFileSha256: sha256(sourceBoundaryBytes),
    boundarySemanticDigest: boundaryArtifact.contentAddress.digest,
    requiredFilesVerified: boundaryArtifact.files.length,
    transferVerification: describe(transferPath)
  },
  commandSemantics: {
    runtime: { distribution: "official portable Node.js v22.22.2 win-x64 already provisioned and checksum-verified by readiness work", version: "v22.22.2", executableSha256: sha256(fs.readFileSync(nodePath)) },
    workingDirectoryRole: "fresh exact extracted source snapshot under the run identifier",
    runner: "website/global-geometry-lab/run-global-geometry-ii-u2-screening-v2.js",
    arguments: ["--source-mode", "portable", "--source-boundary-file-sha256", "c60331209247fccee700d10d38b9ae03da3f81e9013f19281a1f5918fb9e6c73", "--source-boundary-semantic-sha256", "a1b1b9bb525ba9c172be48af60b9881a13ce58ebed9862a60fec18a25f07fae0", "--platform-label", "windows"],
    gitAvailableOnDefaultPath: false,
    macOSRecordTransfer: "NONE"
  },
  process: { pid: PID, pidExitObserved: true, exitCode: "NOT_CAPTURED_BY_DETACHED_DISPATCH", stdout: describe(stdoutPath), stderr: describe(stderrPath) },
  exception: {
    name: "Error",
    code: "EPERM",
    errno: -4048,
    syscall: "fsync",
    message: "EPERM: operation not permitted, fsync",
    firstProjectFrame: "website/global-geometry-lab/run-global-geometry-ii-u2-screening-v2.js:71:14",
    operation: "reopen newly published hard-link path with flag r, then fs.fsyncSync on that read-only descriptor",
    classification: "frozen runner is operationally incompatible with Windows before chunk generation"
  },
  noRecordBoundary: {
    recordCount: 0,
    jsonlChunkCount: 0,
    chunkCertificateCount: 0,
    finalRawPresent: false,
    finalSummaryPresent: false,
    runtimeCertificatePresent: false,
    checkpointManifestPresent: false,
    runnerStdoutBytes: 0,
    artifactCensus: outputCensus
  },
  fsyncMatrix: {
    artifact: { bytes: fs.statSync(probePath).size, sha256: sha256(fs.readFileSync(probePath)), semanticDigest: probe.contentAddress.digest },
    readonlyReopenOperationallyValid: probe.conclusions.readonlyReopenOperationallyValid,
    writableReopenOperationallyValid: probe.conclusions.writableReopenOperationallyValid,
    originalWritableDescriptorAcrossLinkOperationallyValid: probe.conclusions.originalWritableDescriptorAcrossLinkOperationallyValid,
    directoryFsyncAvailableViaNode: probe.conclusions.directoryFsyncAvailableViaNode,
    hardlinkNoReplacePreserved: probe.conclusions.hardlinkNoReplacePreserved,
    narrowRepair: probe.conclusions.narrowRepair,
    durabilityQualification: probe.conclusions.durabilityQualification
  },
  preservedEvidence: preserved,
  action: "do not modify or resume C1/C2; create a versioned implementation repair and a new source boundary before any Windows scientific retry",
  outcome: { u2Status: "UNRESOLVED", decisionAuthority: "NONE" }
};
const canonicalPayload = canonical(payload), semanticDigest = sha256(Buffer.from(canonicalPayload, "utf8"));
const artifact = Object.assign({}, payload, { contentAddress: { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest: semanticDigest, canonicalBytes: Buffer.byteLength(canonicalPayload, "utf8") } });
const bytes = Buffer.from(JSON.stringify(artifact, null, 2) + "\n", "utf8");
fs.writeFileSync(blockerPath, bytes, { flag: "wx" });
const fileSha256 = sha256(bytes), addressedPath = path.join(PROVENANCE_ROOT, "windows-screening-v2-blocker." + fileSha256 + ".json");
fs.copyFileSync(blockerPath, addressedPath, fs.constants.COPYFILE_EXCL);
process.stdout.write(JSON.stringify({ status: artifact.status, runId: RUN_ID, recordCount: 0, artifactCensus: outputCensus, fileSha256, semanticDigest, addressedPath: relativeToRun(addressedPath), fsyncMatrixDigest: probe.contentAddress.digest, u2Status: "UNRESOLVED" }) + "\n");
