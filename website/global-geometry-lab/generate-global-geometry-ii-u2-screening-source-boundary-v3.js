#!/usr/bin/env node
"use strict";

const childProcess = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "../..");
const ACTIVE_SUPPLEMENT_DIGEST = "1524f69ef343a1048e3cfd05c9b4f6d93f9c6783233611094a345b3d4863885d";
const REQUIRED_FILES = Object.freeze([
  { path: "GLOBAL_GEOMETRY_II_EVALUATION_REPAIR_AUDIT.md", role: "governing-repair-audit" },
  { path: "GLOBAL_GEOMETRY_II_U2_ADVERSARIAL_PREREGISTRATION.md", role: "decision-contract" },
  { path: "GLOBAL_GEOMETRY_II_UNIVERSALITY_SPEC.md", role: "governing-specification" },
  { path: "artifacts/global-geometry-ii/u2/experiment-manifest-v2.json", role: "parent-experiment" },
  { path: "artifacts/global-geometry-ii/u2/screening/screening-manifest-v1.json", role: "base-screening-preregistration" },
  { path: "artifacts/global-geometry-ii/u2/screening/screening-implementation-supplement-v2.json", role: "semantic-base-prior-supplement" },
  { path: "artifacts/global-geometry-ii/u2/screening/screening-implementation-supplement-v3.json", role: "semantic-base-supplement" },
  { path: "artifacts/global-geometry-ii/u2/screening/screening-pilot-abort-macos-v1.json", role: "semantic-base-aborted-pilot-metadata" },
  { path: "artifacts/global-geometry-ii/u2/screening/screening-v2/source-boundary-v2.json", role: "semantic-base-source-boundary" },
  { path: "artifacts/global-geometry-ii/u2/screening/screening-windows-preflight-abort-v2.json", role: "v2-windows-abort-metadata" },
  { path: "artifacts/global-geometry-ii/u2/screening/screening-execution-v3-supplement-v1.json", role: "active-v3-supplement" },
  { path: "website/global-geometry-lab/global-geometry-ii-u2-screening.js", role: "semantic-base-kernel-v1" },
  { path: "website/global-geometry-lab/global-geometry-ii-u2-screening-v2.js", role: "semantic-base-kernel-v2" },
  { path: "website/global-geometry-lab/generate-global-geometry-ii-u2-screening-supplement-v3.js", role: "semantic-base-supplement-builder" },
  { path: "website/global-geometry-lab/generate-global-geometry-ii-u2-screening-source-boundary-v2.js", role: "semantic-base-boundary-verifier" },
  { path: "website/global-geometry-lab/generate-global-geometry-ii-u2-screening-execution-v3-supplement.js", role: "v3-supplement-builder" },
  { path: "website/global-geometry-lab/global-geometry-ii-u2-screening-execution-v3.js", role: "v3-semantic-adapter-and-container" },
  { path: "website/global-geometry-lab/run-global-geometry-ii-u2-screening-execution-v3.js", role: "v3-production-runner" },
  { path: "website/global-geometry-lab/test-global-geometry-ii-u2-screening-execution-v3.js", role: "v3-implementation-tests" },
  { path: "website/global-geometry-lab/test-global-geometry-ii-u2-screening-execution-v3-adversarial.js", role: "v3-adversarial-tests" },
  { path: "website/global-geometry-lab/generate-global-geometry-ii-u2-screening-source-boundary-v3.js", role: "v3-source-boundary-generator" }
]);

function sha256Bytes(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
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

function git(args, encoding) { return childProcess.execFileSync("git", args, { cwd: ROOT, encoding: encoding || "utf8", stdio: ["ignore", "pipe", "pipe"] }); }

function buildBoundary(commit) {
  if (typeof commit !== "string" || !/^[0-9a-f]{40}$/.test(commit)) throw new Error("an explicit full lowercase 40-hex Git commit is required");
  const fullCommit = git(["rev-parse", commit + "^{commit}"]).trim(), tree = git(["rev-parse", fullCommit + "^{tree}"]).trim();
  const files = REQUIRED_FILES.map(function (entry) {
    const local = fs.readFileSync(path.join(ROOT, entry.path)), committed = git(["show", fullCommit + ":" + entry.path], "buffer");
    if (!local.equals(committed)) throw new Error(entry.path + " local bytes differ from source commit " + fullCommit);
    return { path: entry.path, role: entry.role, bytes: local.length, sha256: sha256Bytes(local) };
  });
  const payload = {
    schema: "gg.u2.screening.source-boundary/3",
    boundaryId: "ggii-u2-screening-execution-v3-source-boundary",
    sourceCommit: fullCommit,
    sourceTree: tree,
    semanticBaseCommit: "1c3373267057b8a018ad5039e0f3b2b4e8eb2b1d",
    semanticBaseBoundaryCommit: "ed624f4ff42b4e5488a1889c3d55ba1195e5a952",
    activeSupplementDigest: ACTIVE_SUPPLEMENT_DIGEST,
    semanticPayloadVersion: "screening-v3",
    executionVersion: "screening-v3",
    verificationModes: {
      git: "verify commit object, tree, commit:path bytes, local bytes, and every listed digest; any Git error is fatal",
      portable: "without invoking Git, verify exact required path set, local bytes/sizes/digests, boundary content address, commit/tree syntax, and active supplement digest"
    },
    files: files
  };
  const canonical = canonicalStringify(payload);
  return Object.assign({}, payload, { contentAddress: { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest: sha256Bytes(Buffer.from(canonical, "utf8")), canonicalBytes: Buffer.byteLength(canonical, "utf8") } });
}

function validateBoundaryStructure(artifact) {
  const errors = [];
  try {
    if (!artifact || artifact.schema !== "gg.u2.screening.source-boundary/3" || artifact.boundaryId !== "ggii-u2-screening-execution-v3-source-boundary") errors.push("v3 source boundary identity mismatch");
    if (!/^[0-9a-f]{40}$/.test(artifact.sourceCommit || "") || !/^[0-9a-f]{40}$/.test(artifact.sourceTree || "")) errors.push("source commit/tree must be full lowercase Git object IDs");
    if (artifact.semanticBaseCommit !== "1c3373267057b8a018ad5039e0f3b2b4e8eb2b1d" || artifact.semanticBaseBoundaryCommit !== "ed624f4ff42b4e5488a1889c3d55ba1195e5a952") errors.push("semantic-base commit binding mismatch");
    if (artifact.activeSupplementDigest !== ACTIVE_SUPPLEMENT_DIGEST || artifact.semanticPayloadVersion !== "screening-v3" || artifact.executionVersion !== "screening-v3") errors.push("v3 version/supplement binding mismatch");
    const expected = REQUIRED_FILES.map(function (entry) { return entry.path + "\0" + entry.role; }), observed = Array.isArray(artifact.files) ? artifact.files.map(function (entry) { return entry.path + "\0" + entry.role; }) : [];
    if (canonicalStringify(observed) !== canonicalStringify(expected)) errors.push("v3 source boundary required path/role set mismatch");
    if (!artifact.contentAddress) errors.push("v3 source boundary contentAddress missing");
    else {
      const payload = JSON.parse(JSON.stringify(artifact)); delete payload.contentAddress;
      const canonical = canonicalStringify(payload);
      if (artifact.contentAddress.digest !== sha256Bytes(Buffer.from(canonical, "utf8")) || artifact.contentAddress.canonicalBytes !== Buffer.byteLength(canonical, "utf8")) errors.push("v3 source boundary contentAddress mismatch");
    }
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

function verifyBoundary(artifact, mode, adapters) {
  const errors = validateBoundaryStructure(artifact).errors.slice(); adapters = adapters || {};
  try {
    if (mode !== "git" && mode !== "portable") errors.push("source verification mode must be explicitly git or portable");
    artifact.files.forEach(function (entry) {
      const local = (adapters.readFile || fs.readFileSync)(path.join(ROOT, entry.path));
      if (local.length !== entry.bytes || sha256Bytes(local) !== entry.sha256) errors.push("local source mismatch: " + entry.path);
    });
    if (mode === "git") {
      const runGit = adapters.git || git, fullCommit = runGit(["rev-parse", artifact.sourceCommit + "^{commit}"], "utf8").trim(), tree = runGit(["rev-parse", fullCommit + "^{tree}"], "utf8").trim();
      if (fullCommit !== artifact.sourceCommit || tree !== artifact.sourceTree) errors.push("Git commit/tree binding mismatch");
      artifact.files.forEach(function (entry) {
        const committed = runGit(["show", fullCommit + ":" + entry.path], "buffer");
        if (committed.length !== entry.bytes || sha256Bytes(committed) !== entry.sha256) errors.push("commit source mismatch: " + entry.path);
      });
    }
  } catch (error) { errors.push((mode === "git" ? "Git verification failed without portable fallback: " : "portable verification failed: ") + error.message); }
  return { valid: errors.length === 0, errors: errors, mode: mode };
}

function serializeArtifact(artifact) { return Buffer.from(JSON.stringify(artifact, null, 2) + "\n", "utf8"); }

function verifyBoundaryBytes(bytes, mode, pins, adapters) {
  const errors = []; let artifact = null;
  try {
    if (!Buffer.isBuffer(bytes)) errors.push("source boundary bytes must be a Buffer");
    if (!pins || !/^[0-9a-f]{64}$/.test(pins.fileSha256 || "") || !/^[0-9a-f]{64}$/.test(pins.semanticSha256 || "")) errors.push("external source-boundary file and semantic SHA-256 pins are required");
    if (!errors.length && sha256Bytes(bytes) !== pins.fileSha256) errors.push("source boundary file pin mismatch");
    artifact = JSON.parse(bytes.toString("utf8"));
    if (!artifact.contentAddress || artifact.contentAddress.digest !== pins.semanticSha256) errors.push("source boundary semantic pin mismatch");
    if (!serializeArtifact(artifact).equals(bytes)) errors.push("source boundary bytes are not exact pretty-JSON-plus-one-LF serialization");
    errors.push.apply(errors, verifyBoundary(artifact, mode, adapters).errors);
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors, mode: mode, artifact: artifact, pins: pins || null };
}

function writeOnce(output, bytes) {
  if (fs.existsSync(output)) throw new Error("refusing to overwrite v3 source boundary: " + output);
  fs.mkdirSync(path.dirname(output), { recursive: true }); fs.writeFileSync(output, bytes, { flag: "wx" });
}

function main(argv) {
  let commit = null, output = null;
  for (let index = 0; index < argv.length; index += 1) {
    if (argv[index] === "--commit" && argv[index + 1]) commit = argv[++index];
    else if (argv[index] === "--output" && argv[index + 1]) output = path.resolve(argv[++index]);
    else throw new Error("usage: generate-global-geometry-ii-u2-screening-source-boundary-v3.js --commit HASH [--output path]");
  }
  const artifact = buildBoundary(commit), report = verifyBoundary(artifact, "git");
  if (!report.valid) throw new Error(report.errors.join("; "));
  if (output) writeOnce(output, serializeArtifact(artifact)); else process.stdout.write(serializeArtifact(artifact));
}

if (require.main === module) main(process.argv.slice(2));
module.exports = { ROOT: ROOT, ACTIVE_SUPPLEMENT_DIGEST: ACTIVE_SUPPLEMENT_DIGEST, REQUIRED_FILES: REQUIRED_FILES, buildBoundary: buildBoundary, validateBoundaryStructure: validateBoundaryStructure, verifyBoundary: verifyBoundary, verifyBoundaryBytes: verifyBoundaryBytes, serializeArtifact: serializeArtifact, canonicalStringify: canonicalStringify, sha256Bytes: sha256Bytes };
