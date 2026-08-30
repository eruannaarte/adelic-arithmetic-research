#!/usr/bin/env node
"use strict";

const childProcess = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "../..");
const SCHEMA = "gg.atlas.u2-source-boundary/1";
const REQUIRED_FILES = Object.freeze([
  "GLOBAL_GEOMETRY_II_EVALUATION_REPAIR_AUDIT.md",
  "GLOBAL_GEOMETRY_II_U2_ADVERSARIAL_PREREGISTRATION.md",
  "GLOBAL_GEOMETRY_II_UNIVERSALITY_SPEC.md",
  "artifacts/global-geometry-ii/u2/experiment-manifest-v2.json",
  "website/global-geometry-lab/generate-global-geometry-ii-u2-manifest.js",
  "website/global-geometry-lab/global-geometry-core.js",
  "website/global-geometry-lab/global-geometry-ii-core.js",
  "website/global-geometry-lab/global-geometry-ii-ensembles.js",
  "website/global-geometry-lab/global-geometry-ii-u2-source-boundary.js",
  "website/global-geometry-lab/global-geometry-ii-u2.js",
  "website/global-geometry-lab/generate-global-geometry-ii-u2.js",
  "website/global-geometry-lab/test-global-geometry-ii-u2.js",
  "website/global-geometry-lab/test-global-geometry-ii-u2-adversarial.js"
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
function contentAddress(payload) {
  const canonical = canonicalStringify(payload);
  return { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest: sha256Bytes(Buffer.from(canonical, "utf8")), canonicalBytes: Buffer.byteLength(canonical, "utf8") };
}
function git(args, encoding) {
  return childProcess.execFileSync("git", args, { cwd: ROOT, encoding: encoding || "utf8", stdio: ["ignore", "pipe", "pipe"] });
}

function buildSourceBoundary(commit, adapters) {
  if (typeof commit !== "string" || !/^[0-9a-f]{40}$/.test(commit)) throw new Error("strict U2 production requires a full lowercase 40-hex Git commit");
  adapters = adapters || {};
  const runGit = adapters.git || git, readFile = adapters.readFile || fs.readFileSync;
  const resolved = runGit(["rev-parse", commit + "^{commit}"], "utf8").trim();
  if (resolved !== commit) throw new Error("source commit did not resolve exactly");
  const tree = runGit(["rev-parse", resolved + "^{tree}"], "utf8").trim();
  const files = REQUIRED_FILES.map(function (relativePath) {
    const local = readFile(path.join(ROOT, relativePath));
    const committed = runGit(["show", resolved + ":" + relativePath], "buffer");
    if (!Buffer.isBuffer(local) || !Buffer.isBuffer(committed) || !local.equals(committed)) throw new Error(relativePath + " local bytes differ from the bound source commit");
    return { path: relativePath, bytes: local.length, sha256: sha256Bytes(local) };
  });
  const payload = { schema: SCHEMA, sourceCommit: resolved, sourceTree: tree, verification: "actual Git commit/tree plus exact local=commit:path bytes", files: files };
  return Object.assign({}, payload, { contentAddress: contentAddress(payload) });
}

function validateSourceBoundary(artifact, options) {
  const errors = [];
  options = options || {};
  try {
    if (!artifact || artifact.schema !== SCHEMA) errors.push("source boundary schema mismatch");
    if (!artifact || !/^[0-9a-f]{40}$/.test(artifact.sourceCommit || "") || !/^[0-9a-f]{40}$/.test(artifact.sourceTree || "")) errors.push("source commit/tree identity mismatch");
    const observedPaths = artifact && Array.isArray(artifact.files) ? artifact.files.map(function (entry) { return entry.path; }) : [];
    if (canonicalStringify(observedPaths) !== canonicalStringify(REQUIRED_FILES)) errors.push("source boundary required path/order mismatch");
    const payload = JSON.parse(JSON.stringify(artifact));
    const address = payload.contentAddress;
    delete payload.contentAddress;
    if (!address || canonicalStringify(address) !== canonicalStringify(contentAddress(payload))) errors.push("source boundary content address mismatch");
    if (!errors.length && options.verifyGit !== false) {
      const expected = buildSourceBoundary(artifact.sourceCommit, options.adapters);
      if (canonicalStringify(artifact) !== canonicalStringify(expected)) errors.push("source boundary fails Git/blob semantic replay");
    }
  } catch (error) { errors.push("source boundary validation failed safely: " + error.message); }
  return { valid: errors.length === 0, errors: errors };
}

module.exports = {
  ROOT: ROOT,
  SCHEMA: SCHEMA,
  REQUIRED_FILES: REQUIRED_FILES,
  buildSourceBoundary: buildSourceBoundary,
  validateSourceBoundary: validateSourceBoundary,
  canonicalStringify: canonicalStringify,
  contentAddress: contentAddress,
  sha256Bytes: sha256Bytes
};
