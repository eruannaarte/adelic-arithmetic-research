#!/usr/bin/env node
"use strict";

const childProcess = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "../..");
const REQUIRED_FILES = Object.freeze([
  { path: "GLOBAL_GEOMETRY_II_EVALUATION_REPAIR_AUDIT.md", role: "governing-repair-audit" },
  { path: "GLOBAL_GEOMETRY_II_U2_ADVERSARIAL_PREREGISTRATION.md", role: "decision-contract" },
  { path: "GLOBAL_GEOMETRY_II_UNIVERSALITY_SPEC.md", role: "governing-specification" },
  { path: "artifacts/global-geometry-ii/u2/experiment-manifest-v2.json", role: "parent-experiment" },
  { path: "artifacts/global-geometry-ii/u2/screening/screening-manifest-v1.json", role: "base-screening-preregistration" },
  { path: "artifacts/global-geometry-ii/u2/screening/screening-implementation-supplement-v2.json", role: "prior-implementation-preregistration" },
  { path: "artifacts/global-geometry-ii/u2/screening/screening-implementation-supplement-v3.json", role: "active-implementation-preregistration" },
  { path: "artifacts/global-geometry-ii/u2/screening/screening-pilot-abort-macos-v1.json", role: "aborted-pilot-metadata" },
  { path: "website/global-geometry-lab/global-geometry-ii-u2-screening.js", role: "measurement-kernel-v1-base" },
  { path: "website/global-geometry-lab/global-geometry-ii-u2-screening-v2.js", role: "measurement-kernel-v2" },
  { path: "website/global-geometry-lab/run-global-geometry-ii-u2-screening-v2.js", role: "production-runner-v2" },
  { path: "website/global-geometry-lab/generate-global-geometry-ii-u2-screening-supplement-v3.js", role: "active-supplement-builder" },
  { path: "website/global-geometry-lab/test-global-geometry-ii-u2-screening-v2.js", role: "implementation-tests-v2" },
  { path: "website/global-geometry-lab/test-global-geometry-ii-u2-screening-v2-adversarial.js", role: "adversarial-tests-v2" },
  { path: "website/global-geometry-lab/generate-global-geometry-ii-u2-screening-source-boundary-v2.js", role: "source-boundary-generator" }
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

function git(args, encoding) {
  return childProcess.execFileSync("git", args, { cwd: ROOT, encoding: encoding || "utf8", stdio: ["ignore", "pipe", "pipe"] });
}

function buildBoundary(commit) {
  if (typeof commit !== "string" || !/^[0-9a-f]{40}$/.test(commit)) throw new Error("an explicit full lowercase 40-hex Git commit is required");
  const fullCommit = git(["rev-parse", commit + "^{commit}"]).trim(), tree = git(["rev-parse", fullCommit + "^{tree}"]).trim();
  const files = REQUIRED_FILES.map(function (entry) {
    const local = fs.readFileSync(path.join(ROOT, entry.path));
    const committed = git(["show", fullCommit + ":" + entry.path], "buffer");
    if (!local.equals(committed)) throw new Error(entry.path + " local bytes differ from source commit " + fullCommit);
    return { path: entry.path, role: entry.role, bytes: local.length, sha256: sha256Bytes(local) };
  });
  const payload = {
    schema: "gg.u2.screening.source-boundary/2",
    boundaryId: "ggii-u2-screening-v2-source-boundary",
    sourceCommit: fullCommit,
    sourceTree: tree,
    activeSupplementDigest: "21d69b11b12277e228e2934e033fd8f366b3c8d5d89f1b8833aa781a36118888",
    verificationModes: {
      git: "verify commit object, commit:path bytes, local bytes, and every listed digest; any Git error is fatal",
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
    if (!artifact || artifact.schema !== "gg.u2.screening.source-boundary/2" || artifact.boundaryId !== "ggii-u2-screening-v2-source-boundary") errors.push("source boundary identity mismatch");
    if (!/^[0-9a-f]{40}$/.test(artifact.sourceCommit || "") || !/^[0-9a-f]{40}$/.test(artifact.sourceTree || "")) errors.push("source commit/tree must be full lowercase Git object IDs");
    if (artifact.activeSupplementDigest !== "21d69b11b12277e228e2934e033fd8f366b3c8d5d89f1b8833aa781a36118888") errors.push("active supplement digest mismatch");
    const expectedPaths = REQUIRED_FILES.map(function (entry) { return entry.path + "\0" + entry.role; });
    const observedPaths = Array.isArray(artifact.files) ? artifact.files.map(function (entry) { return entry.path + "\0" + entry.role; }) : [];
    if (canonicalStringify(observedPaths) !== canonicalStringify(expectedPaths)) errors.push("source boundary required path/role set mismatch");
    if (!artifact.contentAddress) errors.push("source boundary contentAddress missing");
    else {
      const payload = JSON.parse(JSON.stringify(artifact)); delete payload.contentAddress;
      const canonical = canonicalStringify(payload);
      if (artifact.contentAddress.digest !== sha256Bytes(Buffer.from(canonical, "utf8")) || artifact.contentAddress.canonicalBytes !== Buffer.byteLength(canonical, "utf8")) errors.push("source boundary contentAddress mismatch");
    }
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

function verifyBoundary(artifact, mode, adapters) {
  const errors = validateBoundaryStructure(artifact).errors.slice();
  adapters = adapters || {};
  try {
    if (mode !== "git" && mode !== "portable") errors.push("source verification mode must be explicitly git or portable");
    artifact.files.forEach(function (entry) {
      const local = (adapters.readFile || fs.readFileSync)(path.join(ROOT, entry.path));
      if (local.length !== entry.bytes || sha256Bytes(local) !== entry.sha256) errors.push("local source mismatch: " + entry.path);
    });
    if (mode === "git") {
      const runGit = adapters.git || git;
      const fullCommit = runGit(["rev-parse", artifact.sourceCommit + "^{commit}"], "utf8").trim();
      const tree = runGit(["rev-parse", fullCommit + "^{tree}"], "utf8").trim();
      if (fullCommit !== artifact.sourceCommit || tree !== artifact.sourceTree) errors.push("Git commit/tree binding mismatch");
      artifact.files.forEach(function (entry) {
        const committed = runGit(["show", fullCommit + ":" + entry.path], "buffer");
        if (committed.length !== entry.bytes || sha256Bytes(committed) !== entry.sha256) errors.push("commit source mismatch: " + entry.path);
      });
    }
  } catch (error) {
    errors.push((mode === "git" ? "Git verification failed without portable fallback: " : "portable verification failed: ") + error.message);
  }
  return { valid: errors.length === 0, errors: errors, mode: mode };
}

function serializeArtifact(artifact) {
  return Buffer.from(JSON.stringify(artifact, null, 2) + "\n", "utf8");
}

function verifyBoundaryBytes(bytes, mode, pins, adapters) {
  const errors = [];
  let artifact = null;
  try {
    if (!Buffer.isBuffer(bytes)) errors.push("source boundary bytes must be a Buffer");
    if (!pins || !/^[0-9a-f]{64}$/.test(pins.fileSha256 || "") || !/^[0-9a-f]{64}$/.test(pins.semanticSha256 || "")) errors.push("external source-boundary file and semantic SHA-256 pins are required");
    if (!errors.length && sha256Bytes(bytes) !== pins.fileSha256) errors.push("source boundary file pin mismatch");
    artifact = JSON.parse(bytes.toString("utf8"));
    if (!artifact.contentAddress || artifact.contentAddress.digest !== pins.semanticSha256) errors.push("source boundary semantic pin mismatch");
    if (!serializeArtifact(artifact).equals(bytes)) errors.push("source boundary bytes are not the exact pretty-JSON-plus-one-LF serialization");
    const report = verifyBoundary(artifact, mode, adapters);
    errors.push.apply(errors, report.errors);
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors, mode: mode, artifact: artifact, pins: pins || null };
}

function writeOnce(output, bytes) {
  if (fs.existsSync(output)) throw new Error("refusing to overwrite source boundary: " + output);
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, bytes, { flag: "wx" });
}

function main(argv) {
  let commit = null, output = null;
  for (let index = 0; index < argv.length; index += 1) {
    if (argv[index] === "--commit" && argv[index + 1]) commit = argv[++index];
    else if (argv[index] === "--output" && argv[index + 1]) output = path.resolve(argv[++index]);
    else throw new Error("usage: generate-global-geometry-ii-u2-screening-source-boundary-v2.js --commit HASH [--output path]");
  }
  const artifact = buildBoundary(commit), report = verifyBoundary(artifact, "git");
  if (!report.valid) throw new Error(report.errors.join("; "));
  if (output) writeOnce(output, Buffer.from(JSON.stringify(artifact, null, 2) + "\n", "utf8"));
  else process.stdout.write(serializeArtifact(artifact));
}

if (require.main === module) main(process.argv.slice(2));
module.exports = { ROOT: ROOT, REQUIRED_FILES: REQUIRED_FILES, buildBoundary: buildBoundary, validateBoundaryStructure: validateBoundaryStructure, verifyBoundary: verifyBoundary, verifyBoundaryBytes: verifyBoundaryBytes, serializeArtifact: serializeArtifact, canonicalStringify: canonicalStringify, sha256Bytes: sha256Bytes };
