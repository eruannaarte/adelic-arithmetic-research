#!/usr/bin/env node
"use strict";

/*
 * Deterministic release metadata for the Global Geometry II evaluation
 * checkpoint.  Version 2 is intentionally independent of the historical v1
 * release files: it reads an explicit compact-input registry and never scans
 * U2 result directories for files to publish.
 *
 * Hash topology:
 *
 *   registered compact artifacts -> input registry -> manifest -> index
 *
 * No file hashes itself.  Uncompressed raw/chunk/checkpoint-working files are
 * not eligible registry inputs.  The only raw-derived inputs are four
 * explicitly non-authoritative gzip transports cross-bound by the evaluation
 * index.
 */

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { TextDecoder } = require("util");
const V1 = require("./generate-global-geometry-ii-release.js");

const REPO_ROOT = path.resolve(__dirname, "../..");
const DEFAULT_REGISTRY = path.join(REPO_ROOT, "artifacts/global-geometry-ii/release-input-registry-v2.json");
const DEFAULT_MANIFEST = path.join(REPO_ROOT, "global_geometry_ii_reproducibility_manifest_v2.json");
const DEFAULT_INDEX = path.join(REPO_ROOT, "artifacts/global-geometry-ii/release-index-v2.json");
const RELEASE_ID = "global-geometry-ii-evaluation-checkpoint-v2";
const REGISTRY_SCHEMA = "ggii.release-input-registry/2";
const MANIFEST_SCHEMA = "ggii.reproducibility-manifest/2";
const INDEX_SCHEMA = "ggii.release-index/2";
const ADDRESS_CANONICALIZATION = "ggii-release-json-v2";
const HISTORICAL_V1_CLASSIFICATION = "HISTORICAL_PRIOR_RELEASE_ONLY_DOES_NOT_CERTIFY_V2";
const HISTORICAL_V1_INDEX = "artifacts/global-geometry-ii/release-index-v1.json";
const HISTORICAL_V1_COMPARISON = "artifacts/global-geometry-ii/certificates/macos-windows-comparison-v1.json";
const EXTERNAL_COMPARISON_RECORD = "artifacts/global-geometry-ii/certificates/macos-windows-comparison-v2.json";
const EVALUATION_INDEX_SCHEMA = "gg.u2.evaluation.index/2";
const EVALUATION_VALIDATOR_PATH = "website/global-geometry-lab/generate-global-geometry-ii-u2-evaluation-index-v2.js";
const REQUIRED_DEEP_VALIDATION_SURFACES = Object.freeze({
  "screening-v3": Object.freeze({ id: "screening-v3-artifact-validation", path: EVALUATION_VALIDATOR_PATH, args: Object.freeze(["--validate-screening"]) }),
  "strict-partial": Object.freeze({ id: "strict-partial-artifact-validation", path: EVALUATION_VALIDATOR_PATH, args: Object.freeze(["--validate-strict"]) })
});
const ARCHIVE_ROLE = "deterministic gzip -n -9 convenience transport; decompressed bytes are the authoritative bound source artifact";
const MAX_REGISTERED_BYTES = 16 * 1024 * 1024;
const MAX_REGISTRY_BYTES = 2 * 1024 * 1024;

const PRINCIPAL_ARTIFACTS = Object.freeze([
  Object.freeze({ id: "calibration-v1", path: "artifacts/global-geometry-ii/calibration-v1.json", schema: "ggii.calibration-artifact/1" }),
  Object.freeze({ id: "atlas-pilot-v1", path: "artifacts/global-geometry-ii/atlas-pilot-v1.json", schema: "ggii.atlas-pilot-artifact/1" }),
  Object.freeze({ id: "inverse-certificates-v1", path: "artifacts/global-geometry-ii/inverse-certificates-v1.json", schema: "ggii.inverse-certificates-artifact/1" }),
  Object.freeze({ id: "sheet-hil-v1", path: "artifacts/global-geometry-ii/sheet-hil-v1.json", schema: "ggii.sheet-hil-artifact/1" })
]);

const PHYSICAL_PREFLIGHT_ARTIFACT = Object.freeze({
  id: "physical-preflight-v1",
  path: "artifacts/global-geometry-ii/fabrication/physical-preflight-v1.json",
  schema: "ggii.physical-preflight-evidence/1"
});

const SAFE_DEEP_VALIDATION_FLAGS = Object.freeze([
  "--validate-only",
  "--validate-strict",
  "--validate-screening",
  "--validate-calibration",
  "--validate-campaign"
]);

const ARCHIVE_ROLES = Object.freeze([
  "strict-campaign-archive",
  "screening-raw-archive"
]);

const ENTRY_ROLES = Object.freeze([
  "principal-artifact",
  "evaluation-index",
  "evaluation-report",
  "screening-summary",
  "screening-runtime",
  "screening-writer-capability",
  "screening-checkpoint",
  "screening-certificate",
  "screening-source-boundary",
  "screening-comparison",
  "strict-normalization",
  "strict-partial-summary",
  "strict-partial-certificate",
  "strict-partial-comparison",
  "physical-preflight",
  "strict-campaign-archive",
  "screening-raw-archive",
  "historical-v1-metadata"
]);

const ADDRESSING_POLICIES = Object.freeze([
  "canonical-json",
  "content-addressed-json",
  "utf8-text",
  "raw-bytes-only"
]);

const REQUIRED_ROLE_COUNTS = Object.freeze({
  "principal-artifact": 4,
  "evaluation-index": 1,
  "evaluation-report": 1,
  "screening-summary": 2,
  "screening-runtime": 2,
  "screening-writer-capability": 2,
  "screening-checkpoint": 2,
  "screening-certificate": 2,
  "screening-source-boundary": 1,
  "screening-comparison": 1,
  "strict-normalization": 2,
  "strict-partial-summary": 2,
  "strict-partial-certificate": 2,
  "strict-partial-comparison": 1,
  "physical-preflight": 1,
  "strict-campaign-archive": 2,
  "screening-raw-archive": 2,
  "historical-v1-metadata": 2
});

const REQUIRED_PAIRED_ROLES = Object.freeze([
  "screening-summary",
  "screening-runtime",
  "screening-writer-capability",
  "screening-checkpoint",
  "screening-certificate",
  "strict-normalization",
  "strict-partial-summary",
  "strict-partial-certificate",
  "strict-campaign-archive",
  "screening-raw-archive"
]);

const QUICK_SUITES = Object.freeze([
  { id: "global-geometry-i-core", path: "website/global-geometry-lab/test-global-geometry-core.js", args: [] },
  { id: "global-geometry-ii-core", path: "website/global-geometry-lab/test-global-geometry-ii-core.js", args: [] },
  { id: "global-geometry-ii-ensembles", path: "website/global-geometry-lab/test-global-geometry-ii-ensembles.js", args: [] },
  { id: "global-geometry-ii-atlas", path: "website/global-geometry-lab/test-global-geometry-ii-atlas.js", args: [] },
  { id: "global-geometry-ii-inverse", path: "website/global-geometry-lab/test-global-geometry-ii-inverse.js", args: [] },
  { id: "global-geometry-ii-sheet", path: "website/global-geometry-lab/test-global-geometry-ii-sheet.js", args: [] },
  { id: "global-geometry-ii-artifacts", path: "website/global-geometry-lab/test-global-geometry-ii-artifacts.js", args: [] },
  { id: "global-geometry-ii-fabrication-vectors", path: "artifacts/global-geometry-ii/fabrication/validate-fabrication.js", args: [] },
  { id: "global-geometry-ii-physical-preflight", path: "website/global-geometry-lab/test-global-geometry-ii-physical-preflight.js", args: [] },
  { id: "global-geometry-ii-u2-kernel", path: "website/global-geometry-lab/test-global-geometry-ii-u2.js", args: [] },
  { id: "global-geometry-ii-u2-kernel-adversarial", path: "website/global-geometry-lab/test-global-geometry-ii-u2-adversarial.js", args: [] },
  { id: "global-geometry-ii-u2-screening", path: "website/global-geometry-lab/test-global-geometry-ii-u2-screening.js", args: [] },
  { id: "global-geometry-ii-u2-screening-adversarial", path: "website/global-geometry-lab/test-global-geometry-ii-u2-screening-adversarial.js", args: [] },
  // Screening-v2 is a frozen, nonportable historical execution surface. Its
  // exact source boundary and Windows abort record remain release inputs, while
  // the portable v3 implementation owns the active writer/replay gate.
  { id: "global-geometry-ii-u2-screening-v3", path: "website/global-geometry-lab/test-global-geometry-ii-u2-screening-execution-v3.js", args: [] },
  { id: "global-geometry-ii-u2-screening-v3-adversarial", path: "website/global-geometry-lab/test-global-geometry-ii-u2-screening-execution-v3-adversarial.js", args: [] },
  { id: "global-geometry-ii-u2-evaluation-v2", path: "website/global-geometry-lab/test-global-geometry-ii-u2-evaluation-index-v2.js", args: [] },
  { id: "global-geometry-ii-static-publication-v2", path: "website/global-geometry-lab/test-global-geometry-ii-static-publication-v2.js", args: [] },
  { id: "global-geometry-ii-release-v2", path: "website/global-geometry-lab/test-global-geometry-ii-release-v2.js", args: [] }
]);

const REGISTRY_TOP_LEVEL_KEYS = Object.freeze([
  "schema",
  "releaseId",
  "evaluationBoundary",
  "historicalV1",
  "entries",
  "deepSuites"
]);

const ENTRY_KEYS = Object.freeze([
  "id",
  "path",
  "role",
  "platform",
  "mediaType",
  "addressing",
  "expectedSchema",
  "required",
  "maximumBytes"
]);

const DEEP_SUITE_KEYS = Object.freeze([
  "id",
  "path",
  "args",
  "timeoutMs",
  "readOnly",
  "coverage"
]);

function isPlainObject(value) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

function sameJson(left, right) {
  return canonicalStringify(left) === canonicalStringify(right);
}

function canonicalStringify(value) {
  return V1.canonicalStringify(value);
}

function sha256Bytes(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function sha256File(filePath) {
  const bytes = fs.readFileSync(filePath);
  return { sha256: sha256Bytes(bytes), bytes: bytes.length };
}

function contentAddress(payload) {
  const canonical = canonicalStringify(payload);
  return {
    algorithm: "sha256",
    canonicalization: ADDRESS_CANONICALIZATION,
    digest: sha256Bytes(Buffer.from(canonical, "utf8")),
    canonicalBytes: Buffer.byteLength(canonical, "utf8")
  };
}

function assertClosedObject(value, expectedKeys, location) {
  if (!isPlainObject(value)) throw new Error(location + " must be a plain JSON object");
  const actual = Object.keys(value).sort();
  const expected = expectedKeys.slice().sort();
  if (!sameJson(actual, expected)) {
    throw new Error(location + " has a noncanonical schema; expected exactly " + expected.join(", "));
  }
}

function assertDenseArray(value, location) {
  if (!Array.isArray(value)) throw new Error(location + " must be an array");
  for (let index = 0; index < value.length; index += 1) {
    if (!Object.prototype.hasOwnProperty.call(value, index)) throw new Error(location + " must be dense");
  }
  if (Object.keys(value).length !== value.length) throw new Error(location + " has non-index properties");
}

function assertBoundedString(value, location, maximumLength) {
  if (typeof value !== "string" || !value || value.length > (maximumLength || 4096) || /\u0000/.test(value)) {
    throw new Error(location + " must be a non-empty bounded NUL-free string");
  }
}

function repoRelative(absolutePath, repoRoot) {
  repoRoot = path.resolve(repoRoot || REPO_ROOT);
  const relative = path.relative(repoRoot, path.resolve(absolutePath));
  if (!relative || relative === ".." || relative.startsWith(".." + path.sep) || path.isAbsolute(relative)) {
    throw new Error("path is outside the repository: " + absolutePath);
  }
  return relative.split(path.sep).join("/");
}

function resolveFromRepo(input, repoRoot) {
  assertBoundedString(input, "path", 8192);
  const root = path.resolve(repoRoot || REPO_ROOT);
  const resolved = path.isAbsolute(input) ? path.normalize(input) : path.resolve(root, input);
  repoRelative(resolved, root);
  return resolved;
}

function assertPortableRelativePath(relativePath, location) {
  assertBoundedString(relativePath, location, 4096);
  if (relativePath !== relativePath.replace(/\\/g, "/") || path.posix.isAbsolute(relativePath)) {
    throw new Error(location + " must be a portable repository-relative POSIX path");
  }
  const normalized = path.posix.normalize(relativePath);
  if (normalized !== relativePath || normalized === "." || normalized === ".." || normalized.startsWith("../")) {
    throw new Error(location + " must be a normalized in-repository path");
  }
  relativePath.split("/").forEach((part) => {
    if (!part || part.startsWith("._")) throw new Error(location + " contains a forbidden platform-metadata or empty component");
  });
}

function assertCompactEntryPath(entry, location) {
  const lower = entry.path.toLowerCase();
  const forbidden = [
    /(^|\/)chunks?\//,
    /(^|\/)\.stale-run-locks\//,
    /(^|\/)\.run-lock/,
    /run-lock\.json$/,
    /\.partial(?:-|\.|$)/,
    /\.jsonl$/,
    /checkpoint-working/,
    /transfer-helper/,
    /(?:^|\/)logs?\//
  ];
  if (forbidden.some((pattern) => pattern.test(lower))) {
    throw new Error(location + ".path is not a compact publishable artifact: " + entry.path);
  }
  if (/(^|[-_.])raw(?:[-_.]|$)/.test(lower) && entry.role !== "screening-raw-archive") {
    throw new Error(location + ".path may contain a raw marker only for a registered screening-raw-archive");
  }
  if (entry.mediaType === "application/json" && !lower.endsWith(".json")) {
    throw new Error(location + ".path must end in .json for application/json");
  }
  if (entry.role === "evaluation-report" && !lower.endsWith(".md")) {
    throw new Error(location + ".path must be a Markdown report");
  }
  if (entry.role !== "evaluation-report" && entry.mediaType === "text/markdown") {
    throw new Error(location + " may use text/markdown only for the evaluation report");
  }
  if (entry.role === "strict-campaign-archive" && !lower.endsWith(".json.gz")) {
    throw new Error(location + ".path must end in .json.gz for a strict campaign convenience archive");
  }
  if (entry.role === "screening-raw-archive" && !lower.endsWith(".jsonl.gz")) {
    throw new Error(location + ".path must end in .jsonl.gz for a screening raw convenience archive");
  }
}

function validateEvaluationBoundary(boundary) {
  assertClosedObject(boundary, [
    "checkpointStatus",
    "u2Decision",
    "universalityClaim",
    "fullConfirmatoryEvaluation",
    "physicalValidation",
    "publicationMeaning"
  ], "registry.evaluationBoundary");
  const statusAllowed = new Set(["UNRESOLVED", "NOT_EVALUATED", "NOT_RUN"]);
  if (!statusAllowed.has(boundary.checkpointStatus)) {
    throw new Error("registry.evaluationBoundary.checkpointStatus must remain unresolved or not run");
  }
  if (boundary.u2Decision !== "NO_ACCEPTANCE_OR_REJECTION_CLAIM") {
    throw new Error("registry.evaluationBoundary must not make a U2 acceptance or rejection claim");
  }
  if (boundary.universalityClaim !== "NONE") {
    throw new Error("registry.evaluationBoundary.universalityClaim must be NONE");
  }
  if (!statusAllowed.has(boundary.fullConfirmatoryEvaluation)) {
    throw new Error("registry.evaluationBoundary.fullConfirmatoryEvaluation must remain unresolved or not run");
  }
  if (boundary.physicalValidation !== "NOT_RUN") {
    throw new Error("registry.evaluationBoundary.physicalValidation must remain NOT_RUN");
  }
  if (boundary.publicationMeaning !== "SHAREABLE_EVIDENCE_CHECKPOINT_NOT_A_CONFIRMATORY_DECISION") {
    throw new Error("registry.evaluationBoundary.publicationMeaning exceeds the checkpoint claim boundary");
  }
  return boundary;
}

function validateHistoricalV1(historical) {
  assertClosedObject(historical, ["classification", "releaseIndexPath", "comparisonPath"], "registry.historicalV1");
  if (historical.classification !== HISTORICAL_V1_CLASSIFICATION ||
      historical.releaseIndexPath !== HISTORICAL_V1_INDEX ||
      historical.comparisonPath !== HISTORICAL_V1_COMPARISON) {
    throw new Error("registry.historicalV1 must identify v1 as historical and non-certifying for v2");
  }
  return historical;
}

function validateRegistryEntry(entry, index) {
  const location = "registry.entries[" + index + "]";
  assertClosedObject(entry, ENTRY_KEYS, location);
  assertBoundedString(entry.id, location + ".id", 128);
  if (!/^[a-z0-9][a-z0-9._-]*$/.test(entry.id)) throw new Error(location + ".id is not portable");
  assertPortableRelativePath(entry.path, location + ".path");
  if (!ENTRY_ROLES.includes(entry.role)) throw new Error(location + ".role is not registered");
  if (!["shared", "darwin", "win32"].includes(entry.platform)) throw new Error(location + ".platform is not registered");
  if (!["application/json", "text/markdown", "text/plain", "application/gzip"].includes(entry.mediaType)) {
    throw new Error(location + ".mediaType is not registered");
  }
  if (!ADDRESSING_POLICIES.includes(entry.addressing)) throw new Error(location + ".addressing is not registered");
  if (entry.addressing === "utf8-text" && !entry.mediaType.startsWith("text/")) {
    throw new Error(location + " utf8-text addressing requires a text media type");
  }
  if (entry.addressing === "raw-bytes-only" && (entry.mediaType !== "application/gzip" || !ARCHIVE_ROLES.includes(entry.role))) {
    throw new Error(location + " raw-bytes-only addressing is reserved for application/gzip convenience archives");
  }
  if (entry.addressing !== "utf8-text" && entry.addressing !== "raw-bytes-only" && entry.mediaType !== "application/json") {
    throw new Error(location + " JSON addressing requires application/json");
  }
  if (ARCHIVE_ROLES.includes(entry.role) && entry.addressing !== "raw-bytes-only") {
    throw new Error(location + " convenience archives must use raw-bytes-only addressing");
  }
  if (!ARCHIVE_ROLES.includes(entry.role) && entry.addressing === "raw-bytes-only") {
    throw new Error(location + " raw-bytes-only addressing may not be used for scientific evidence");
  }
  if (!(entry.expectedSchema === null || (typeof entry.expectedSchema === "string" && entry.expectedSchema.length > 0 && entry.expectedSchema.length <= 256))) {
    throw new Error(location + ".expectedSchema must be null or a bounded string");
  }
  if (entry.addressing === "raw-bytes-only" && entry.expectedSchema !== null) {
    throw new Error(location + ".expectedSchema must be null for a gzip convenience archive");
  }
  if (entry.required !== true) throw new Error(location + ".required must be true for a release-v2 input");
  if (!Number.isSafeInteger(entry.maximumBytes) || entry.maximumBytes < 1 || entry.maximumBytes > MAX_REGISTERED_BYTES) {
    throw new Error(location + ".maximumBytes exceeds the compact-input policy");
  }
  if (REQUIRED_PAIRED_ROLES.includes(entry.role) && entry.platform === "shared") {
    throw new Error(location + " must be platform-specific");
  }
  if (!REQUIRED_PAIRED_ROLES.includes(entry.role) && entry.platform !== "shared") {
    throw new Error(location + " must use platform shared");
  }
  assertCompactEntryPath(entry, location);
  return entry;
}

function validateDeepSuite(suite, index) {
  const location = "registry.deepSuites[" + index + "]";
  assertClosedObject(suite, DEEP_SUITE_KEYS, location);
  assertBoundedString(suite.id, location + ".id", 128);
  if (!/^[a-z0-9][a-z0-9._-]*$/.test(suite.id)) throw new Error(location + ".id is not portable");
  assertPortableRelativePath(suite.path, location + ".path");
  if (!/^website\/global-geometry-lab\/(?:test|generate|run)-.*\.js$/.test(suite.path) &&
      !/^artifacts\/global-geometry-ii\/fabrication\/validate-.*\.js$/.test(suite.path)) {
    throw new Error(location + ".path is outside the registered Node validation-script surface");
  }
  assertDenseArray(suite.args, location + ".args");
  suite.args.forEach((arg, argIndex) => {
    assertBoundedString(arg, location + ".args[" + argIndex + "]", 4096);
    if (["--output", "--certificate", "--fresh", "--resume"].includes(arg)) {
      throw new Error(location + ".args contains a write-capable flag " + arg);
    }
  });
  if (!suite.args.some((arg) => SAFE_DEEP_VALIDATION_FLAGS.includes(arg))) {
    throw new Error(location + " must explicitly select a registered read-only validation mode");
  }
  if (!Number.isSafeInteger(suite.timeoutMs) || suite.timeoutMs < 1000 || suite.timeoutMs > 3600000) {
    throw new Error(location + ".timeoutMs must be between one second and one hour");
  }
  if (suite.readOnly !== true) throw new Error(location + ".readOnly must be true");
  if (!["screening-v3", "strict-partial", "evaluation-index"].includes(suite.coverage)) {
    throw new Error(location + ".coverage is not registered");
  }
  return suite;
}

function validateRegistry(registry) {
  assertClosedObject(registry, REGISTRY_TOP_LEVEL_KEYS, "registry");
  if (registry.schema !== REGISTRY_SCHEMA || registry.releaseId !== RELEASE_ID) {
    throw new Error("registry schema/releaseId mismatch");
  }
  validateEvaluationBoundary(registry.evaluationBoundary);
  validateHistoricalV1(registry.historicalV1);
  assertDenseArray(registry.entries, "registry.entries");
  if (registry.entries.length < Object.values(REQUIRED_ROLE_COUNTS).reduce((sum, value) => sum + value, 0)) {
    throw new Error("registry.entries is missing one or more required compact release roles");
  }
  const ids = new Set();
  const paths = new Set();
  const roleCounts = Object.fromEntries(ENTRY_ROLES.map((role) => [role, 0]));
  const pairedPlatforms = Object.fromEntries(REQUIRED_PAIRED_ROLES.map((role) => [role, new Set()]));
  registry.entries.forEach((entry, index) => {
    validateRegistryEntry(entry, index);
    if (ids.has(entry.id)) throw new Error("registry entry id is duplicated: " + entry.id);
    if (paths.has(entry.path)) throw new Error("registry entry path is duplicated: " + entry.path);
    ids.add(entry.id);
    paths.add(entry.path);
    roleCounts[entry.role] += 1;
    if (pairedPlatforms[entry.role]) pairedPlatforms[entry.role].add(entry.platform);
  });
  Object.entries(REQUIRED_ROLE_COUNTS).forEach(([role, count]) => {
    if (roleCounts[role] !== count) throw new Error("registry requires exactly " + count + " entry/entries for role " + role);
  });
  REQUIRED_PAIRED_ROLES.forEach((role) => {
    if (roleCounts[role] !== 2 || !sameJson(Array.from(pairedPlatforms[role]).sort(), ["darwin", "win32"])) {
      throw new Error("registry role " + role + " must contain exactly one darwin and one win32 entry");
    }
  });
  const principalIdentity = registry.entries
    .filter((entry) => entry.role === "principal-artifact")
    .map((entry) => ({ id: entry.id, path: entry.path, schema: entry.expectedSchema, platform: entry.platform, addressing: entry.addressing }))
    .sort((left, right) => left.id.localeCompare(right.id, "en"));
  const expectedPrincipalIdentity = PRINCIPAL_ARTIFACTS
    .map((entry) => ({ id: entry.id, path: entry.path, schema: entry.schema, platform: "shared", addressing: "content-addressed-json" }))
    .sort((left, right) => left.id.localeCompare(right.id, "en"));
  if (!sameJson(principalIdentity, expectedPrincipalIdentity)) {
    throw new Error("principal-artifact entries must be exactly the four existing content-addressed principal artifacts");
  }
  const physicalIdentity = registry.entries
    .filter((entry) => entry.role === "physical-preflight")
    .map((entry) => ({ id: entry.id, path: entry.path, schema: entry.expectedSchema, platform: entry.platform, addressing: entry.addressing }));
  if (!sameJson(physicalIdentity, [{
    id: PHYSICAL_PREFLIGHT_ARTIFACT.id,
    path: PHYSICAL_PREFLIGHT_ARTIFACT.path,
    schema: PHYSICAL_PREFLIGHT_ARTIFACT.schema,
    platform: "shared",
    addressing: "content-addressed-json"
  }])) {
    throw new Error("physical-preflight entry must be the existing content-addressed digital preflight artifact");
  }
  const evaluationIndexes = registry.entries.filter((entry) => entry.role === "evaluation-index");
  if (evaluationIndexes.length !== 1 || evaluationIndexes[0].expectedSchema !== EVALUATION_INDEX_SCHEMA ||
      evaluationIndexes[0].addressing !== "content-addressed-json" || evaluationIndexes[0].mediaType !== "application/json" ||
      evaluationIndexes[0].platform !== "shared") {
    throw new Error("registry must contain exactly one shared content-addressed evaluation index using " + EVALUATION_INDEX_SCHEMA);
  }
  const evaluationReports = registry.entries.filter((entry) => entry.role === "evaluation-report");
  if (evaluationReports.length !== 1 || evaluationReports[0].addressing !== "utf8-text" || evaluationReports[0].mediaType !== "text/markdown" ||
      evaluationReports[0].platform !== "shared") {
    throw new Error("registry must contain exactly one shared UTF-8 Markdown U2 evaluation report");
  }
  const historicalPaths = registry.entries
    .filter((entry) => entry.role === "historical-v1-metadata")
    .map((entry) => entry.path)
    .sort();
  if (!sameJson(historicalPaths, [HISTORICAL_V1_COMPARISON, HISTORICAL_V1_INDEX].sort())) {
    throw new Error("historical-v1-metadata entries must be exactly the historical v1 index and comparison");
  }
  assertDenseArray(registry.deepSuites, "registry.deepSuites");
  const deepIds = new Set();
  const deepCoverage = new Set();
  registry.deepSuites.forEach((suite, index) => {
    validateDeepSuite(suite, index);
    if (deepIds.has(suite.id)) throw new Error("registry deep-suite id is duplicated: " + suite.id);
    deepIds.add(suite.id);
    deepCoverage.add(suite.coverage);
  });
  if (registry.deepSuites.length !== Object.keys(REQUIRED_DEEP_VALIDATION_SURFACES).length) {
    throw new Error("registry.deepSuites must contain exactly the strict and screening evaluation-index validators");
  }
  Object.entries(REQUIRED_DEEP_VALIDATION_SURFACES).forEach(([coverage, expected]) => {
    const candidates = registry.deepSuites.filter((suite) => suite.coverage === coverage);
    if (candidates.length !== 1 || candidates[0].id !== expected.id || candidates[0].path !== expected.path || !sameJson(candidates[0].args, expected.args)) {
      throw new Error("registry.deepSuites must bind the evaluation-index validator for " + coverage);
    }
  });
  return registry;
}

function readRegistry(registryPath, options) {
  options = options || {};
  const repoRoot = path.resolve(options.repoRoot || REPO_ROOT);
  const resolved = resolveFromRepo(registryPath || DEFAULT_REGISTRY, repoRoot);
  const stat = fs.lstatSync(resolved);
  if (!stat.isFile() || stat.isSymbolicLink()) throw new Error("release input registry must be a regular non-symlink file");
  if (stat.size < 1 || stat.size > MAX_REGISTRY_BYTES) throw new Error("release input registry exceeds the bounded size policy");
  const raw = fs.readFileSync(resolved);
  if (raw.length >= 3 && raw[0] === 0xef && raw[1] === 0xbb && raw[2] === 0xbf) {
    throw new Error("release input registry must not contain a byte-order mark");
  }
  let registry;
  try { registry = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(raw)); }
  catch (error) { throw new Error("release input registry is not valid JSON: " + error.message); }
  validateRegistry(registry);
  return {
    path: resolved,
    relativePath: repoRelative(resolved, repoRoot),
    raw,
    registry,
    rawSha256: sha256Bytes(raw),
    rawBytes: raw.length,
    semanticAddress: contentAddress(registry)
  };
}

function verifySuppliedContentAddress(document, location) {
  if (!isPlainObject(document) || !isPlainObject(document.contentAddress)) {
    throw new Error(location + " must contain a top-level contentAddress");
  }
  const address = document.contentAddress;
  assertClosedObject(address, ["algorithm", "canonicalization", "digest", "canonicalBytes"], location + ".contentAddress");
  if (address.algorithm !== "sha256" || typeof address.canonicalization !== "string" || !address.canonicalization) {
    throw new Error(location + ".contentAddress algorithm/canonicalization is invalid");
  }
  if (!/^[0-9a-f]{64}$/.test(address.digest) || !Number.isSafeInteger(address.canonicalBytes) || address.canonicalBytes < 1) {
    throw new Error(location + ".contentAddress digest/length is invalid");
  }
  const payload = Object.assign({}, document);
  delete payload.contentAddress;
  const canonical = canonicalStringify(payload);
  const computed = {
    algorithm: "sha256",
    canonicalization: address.canonicalization,
    digest: sha256Bytes(Buffer.from(canonical, "utf8")),
    canonicalBytes: Buffer.byteLength(canonical, "utf8")
  };
  if (!sameJson(address, computed)) throw new Error(location + " contentAddress does not verify");
  return { payload, semanticAddress: computed };
}

function schemaValue(document) {
  if (!isPlainObject(document)) return undefined;
  if (Object.prototype.hasOwnProperty.call(document, "schema")) return document.schema;
  if (Object.prototype.hasOwnProperty.call(document, "schemaVersion")) return String(document.schemaVersion);
  return undefined;
}

function inspectRegisteredEntry(entry, options) {
  options = options || {};
  const repoRoot = path.resolve(options.repoRoot || REPO_ROOT);
  const absolute = path.join(repoRoot, entry.path.split("/").join(path.sep));
  repoRelative(absolute, repoRoot);
  if (!fs.existsSync(absolute)) throw new Error("required release input is absent: " + entry.path);
  const stat = fs.lstatSync(absolute);
  if (!stat.isFile() || stat.isSymbolicLink()) throw new Error("release input must be a regular non-symlink file: " + entry.path);
  if (stat.size < 1 || stat.size > entry.maximumBytes || stat.size > MAX_REGISTERED_BYTES) {
    throw new Error("release input violates its compact size bound: " + entry.path);
  }
  const raw = fs.readFileSync(absolute);
  let semanticAddress;
  let semanticReplay;
  let observedSchema = null;
  if (entry.addressing === "raw-bytes-only") {
    if (raw.length < 2 || raw[0] !== 0x1f || raw[1] !== 0x8b) {
      throw new Error("convenience archive does not have the gzip magic bytes: " + entry.path);
    }
    semanticAddress = null;
    semanticReplay = "NOT_APPLICABLE_GZIP_CONVENIENCE_COPY_DECOMPRESSED_ADDRESS_RECORDED_BY_EVALUATION_INDEX";
  } else if (entry.addressing === "utf8-text") {
    let text;
    try { text = new TextDecoder("utf-8", { fatal: true }).decode(raw); }
    catch (error) { throw new Error("release text input is not valid UTF-8: " + entry.path); }
    if (/\u0000/.test(text)) throw new Error("release text input contains NUL: " + entry.path);
    semanticAddress = contentAddress({ mediaType: entry.mediaType, utf8Text: text });
    semanticReplay = "UTF8_TEXT_ADDRESS_COMPUTED";
  } else {
    if (raw.length >= 3 && raw[0] === 0xef && raw[1] === 0xbb && raw[2] === 0xbf) {
      throw new Error("release JSON input must not contain a byte-order mark: " + entry.path);
    }
    let document;
    try { document = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(raw)); }
    catch (error) { throw new Error("release JSON input is invalid: " + entry.path + ": " + error.message); }
    canonicalStringify(document);
    observedSchema = schemaValue(document) == null ? null : schemaValue(document);
    if (entry.expectedSchema !== null && observedSchema !== entry.expectedSchema) {
      throw new Error("release input schema mismatch for " + entry.path);
    }
    if (entry.addressing === "content-addressed-json") {
      semanticAddress = verifySuppliedContentAddress(document, entry.path).semanticAddress;
      semanticReplay = "VERIFIED_SUPPLIED_CONTENT_ADDRESS";
    } else {
      semanticAddress = contentAddress(document);
      semanticReplay = "CANONICAL_JSON_ADDRESS_COMPUTED";
    }
  }
  return {
    id: entry.id,
    path: entry.path,
    role: entry.role,
    platform: entry.platform,
    mediaType: entry.mediaType,
    addressing: entry.addressing,
    expectedSchema: entry.expectedSchema,
    observedSchema,
    rawSha256: sha256Bytes(raw),
    rawBytes: raw.length,
    semanticAddress,
    semanticReplay
  };
}

function readStrictJsonFile(filePath, location) {
  const raw = fs.readFileSync(filePath);
  if (raw.length >= 3 && raw[0] === 0xef && raw[1] === 0xbb && raw[2] === 0xbf) {
    throw new Error(location + " must not contain a byte-order mark");
  }
  try { return JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(raw)); }
  catch (error) { throw new Error(location + " is not valid UTF-8 JSON: " + error.message); }
}

function verifyArchiveIndexBindings(registry, registeredArtifacts, options) {
  options = options || {};
  const repoRoot = path.resolve(options.repoRoot || REPO_ROOT);
  const indexEntries = registry.entries.filter((entry) => entry.role === "evaluation-index");
  if (indexEntries.length !== 1) throw new Error("registry must contain exactly one evaluation-index entry");
  const indexEntry = indexEntries[0];
  if (indexEntry.expectedSchema !== EVALUATION_INDEX_SCHEMA || indexEntry.addressing !== "content-addressed-json") {
    throw new Error("evaluation-index entry must use the frozen v2 schema and verified content-addressed JSON");
  }
  const absolute = path.join(repoRoot, indexEntry.path.split("/").join(path.sep));
  const document = readStrictJsonFile(absolute, "evaluation index");
  if (!isPlainObject(document) || document.schema !== EVALUATION_INDEX_SCHEMA) throw new Error("evaluation index schema mismatch");
  assertDenseArray(document.convenienceArchives, "evaluation index.convenienceArchives");
  if (document.convenienceArchives.length !== 4) throw new Error("evaluation index must bind exactly four raw-only gzip transport archives");
  const archiveArtifacts = registeredArtifacts.filter((entry) => ARCHIVE_ROLES.includes(entry.role));
  if (archiveArtifacts.length !== 4) throw new Error("release registry must address exactly four raw-only gzip transport archives");
  const artifactByPath = new Map(archiveArtifacts.map((entry) => [entry.path, entry]));
  const seen = new Set();
  const bindings = document.convenienceArchives.map((record, index) => {
    const location = "evaluation index.convenienceArchives[" + index + "]";
    assertClosedObject(record, [
      "path",
      "rawSha256",
      "rawBytes",
      "decompressedSha256",
      "decompressedBytes",
      "correspondingSourcePath",
      "correspondingSourceSemanticDigest",
      "sourceKind",
      "scientificAuthority",
      "role"
    ], location);
    ["path", "correspondingSourcePath"].forEach((field) => assertPortableRelativePath(record[field], location + "." + field));
    ["rawSha256", "decompressedSha256"].forEach((field) => {
      if (typeof record[field] !== "string" || !/^[0-9a-f]{64}$/.test(record[field])) {
        throw new Error(location + "." + field + " must be a lowercase SHA-256 digest");
      }
    });
    ["rawBytes", "decompressedBytes"].forEach((field) => {
      if (!Number.isSafeInteger(record[field]) || record[field] < 1) throw new Error(location + "." + field + " must be a positive safe integer");
    });
    if (record.scientificAuthority !== "NONE" || record.role !== ARCHIVE_ROLE) {
      throw new Error(location + " promotes a convenience archive beyond its frozen non-authoritative role");
    }
    const artifact = artifactByPath.get(record.path);
    if (!artifact) throw new Error(location + ".path is not a registered convenience archive");
    if (seen.has(record.path)) throw new Error("evaluation index contains a duplicate convenience archive path");
    seen.add(record.path);
    if (record.rawSha256 !== artifact.rawSha256 || record.rawBytes !== artifact.rawBytes) {
      throw new Error(location + " raw archive address does not match the registered gzip bytes");
    }
    const expectedSourceKind = artifact.role === "strict-campaign-archive"
      ? "STRICT_PARTIAL_CAMPAIGN"
      : "SCREENING_V3_RAW_JSONL";
    if (record.sourceKind !== expectedSourceKind) throw new Error(location + ".sourceKind does not match the registered archive role");
    if (expectedSourceKind === "STRICT_PARTIAL_CAMPAIGN") {
      if (typeof record.correspondingSourceSemanticDigest !== "string" || !/^[0-9a-f]{64}$/.test(record.correspondingSourceSemanticDigest)) {
        throw new Error(location + ".correspondingSourceSemanticDigest must bind the strict campaign semantic digest");
      }
    } else if (record.correspondingSourceSemanticDigest !== null) {
      throw new Error(location + ".correspondingSourceSemanticDigest must be null for raw screening JSONL");
    }
    if (artifact.semanticAddress !== null || artifact.semanticReplay !== "NOT_APPLICABLE_GZIP_CONVENIENCE_COPY_DECOMPRESSED_ADDRESS_RECORDED_BY_EVALUATION_INDEX") {
      throw new Error(location + " is incorrectly treated as semantic evidence");
    }
    return {
      path: record.path,
      rawSha256: record.rawSha256,
      rawBytes: record.rawBytes,
      decompressedSha256: record.decompressedSha256,
      decompressedBytes: record.decompressedBytes,
      correspondingSourcePath: record.correspondingSourcePath,
      correspondingSourceSemanticDigest: record.correspondingSourceSemanticDigest,
      sourceKind: record.sourceKind,
      scientificAuthority: record.scientificAuthority,
      role: record.role
    };
  });
  if (seen.size !== artifactByPath.size) throw new Error("evaluation index does not bind every registered convenience archive");
  return {
    evaluationIndexId: indexEntry.id,
    evaluationIndexPath: indexEntry.path,
    policy: "RAW_GZIP_BYTES_ADDRESSED_ONLY; DECOMPRESSED_BYTE_ADDRESS_IMPORTED_FROM_CONTENT_ADDRESSED_EVALUATION_INDEX; NO_GZIP_SEMANTIC_REPLAY",
    bindings
  };
}

function assertPortableSourceEntryName(name, absolutePath) {
  if (name.startsWith("._")) throw new Error("refusing AppleDouble/platform-metadata source entry: " + absolutePath);
}

function listFilesRecursively(directory, extensionPattern, repoRoot) {
  if (!fs.existsSync(directory)) return [];
  const files = [];
  fs.readdirSync(directory, { withFileTypes: true })
    .sort((left, right) => left.name.localeCompare(right.name, "en"))
    .forEach((entry) => {
      const absolute = path.join(directory, entry.name);
      assertPortableSourceEntryName(entry.name, absolute);
      if (entry.isSymbolicLink()) throw new Error("source selection refuses symbolic link " + repoRelative(absolute, repoRoot));
      if (entry.isDirectory()) files.push(...listFilesRecursively(absolute, extensionPattern, repoRoot));
      else if (entry.isFile() && extensionPattern.test(entry.name)) files.push(absolute);
    });
  return files;
}

function collectSourcePaths(options) {
  options = options || {};
  const repoRoot = path.resolve(options.repoRoot || REPO_ROOT);
  const labRoot = path.resolve(options.labRoot || path.join(repoRoot, "website/global-geometry-lab"));
  const labFiles = listFilesRecursively(labRoot, /\.(?:js|html|css|md|ps1)$/i, repoRoot);
  const fabricationSourceRoot = path.join(repoRoot, "artifacts/global-geometry-ii/fabrication");
  const fabricationSources = listFilesRecursively(fabricationSourceRoot, /\.js$/i, repoRoot);
  const rootFiles = fs.readdirSync(repoRoot, { withFileTypes: true })
    .filter((entry) => entry.isFile() && (/^GLOBAL_GEOMETRY_II_.*\.md$/.test(entry.name) || entry.name === "GLOBAL_GEOMETRY_LAB.md" || entry.name === "README.md"))
    .map((entry) => path.join(repoRoot, entry.name));
  const workflow = path.join(repoRoot, ".github/workflows/tests.yml");
  const explicit = fs.existsSync(workflow) ? [workflow] : [];
  return Array.from(new Set(labFiles.concat(fabricationSources, rootFiles, explicit).map((absolute) => repoRelative(absolute, repoRoot)))).sort();
}

function sourceEntries(options) {
  options = options || {};
  const repoRoot = path.resolve(options.repoRoot || REPO_ROOT);
  return collectSourcePaths(options).map((relativePath) => {
    const absolute = path.join(repoRoot, relativePath.split("/").join(path.sep));
    const stat = fs.lstatSync(absolute);
    if (!stat.isFile() || stat.isSymbolicLink()) throw new Error("source manifest requires a regular non-symlink file: " + relativePath);
    const digest = sha256File(absolute);
    return { path: relativePath, sha256: digest.sha256, bytes: digest.bytes };
  });
}

function buildManifestPayload(options) {
  options = options || {};
  const repoRoot = path.resolve(options.repoRoot || REPO_ROOT);
  const registryRecord = options.registryRecord || readRegistry(options.registryPath || DEFAULT_REGISTRY, { repoRoot });
  validateRegistry(registryRecord.registry);
  const sources = sourceEntries({ repoRoot, labRoot: options.labRoot });
  const selectedSources = new Set(sources.map((entry) => entry.path));
  QUICK_SUITES.forEach((suite) => {
    if (!selectedSources.has(suite.path)) throw new Error("quick suite is absent from the source manifest: " + suite.path);
  });
  registryRecord.registry.deepSuites.forEach((suite) => {
    if (!selectedSources.has(suite.path)) throw new Error("deep suite is absent from the source manifest: " + suite.path);
  });
  const registeredArtifacts = registryRecord.registry.entries.map((entry) => inspectRegisteredEntry(entry, { repoRoot }));
  const archiveIndexBindings = verifyArchiveIndexBindings(registryRecord.registry, registeredArtifacts, { repoRoot });
  return {
    schema: MANIFEST_SCHEMA,
    releaseId: RELEASE_ID,
    purpose: "Reproducible, compact evidence checkpoint for Global Geometry II and its bounded U2 evaluation.",
    deterministicMetadata: "No generation timestamp, hostname, checkout path, git state, or machine-specific outcome is included in this addressable payload.",
    claimBoundary: Object.assign({}, registryRecord.registry.evaluationBoundary, {
      interpretation: "This release packages an evidence checkpoint. It makes no U2 acceptance or rejection decision, no universality claim, and no physical-validation claim."
    }),
    historicalV1: {
      classification: HISTORICAL_V1_CLASSIFICATION,
      releaseIndexPath: HISTORICAL_V1_INDEX,
      comparisonPath: HISTORICAL_V1_COMPARISON,
      interpretation: "The v1 index and comparison are retained as historical prior-release records only; neither certifies the v2 source, artifact, evaluation, or suite surface."
    },
    execution: {
      entrypoint: "website/global-geometry-lab/reproduce-global-geometry-ii-v2.js",
      quickCommand: "node website/global-geometry-lab/reproduce-global-geometry-ii-v2.js --verify --mode quick",
      deepCommand: "node website/global-geometry-lab/reproduce-global-geometry-ii-v2.js --verify --mode deep",
      comparator: "website/global-geometry-lab/compare-global-geometry-ii-certificates-v2.js",
      network: "not used",
      packageInstallation: "not used",
      runtimeDependency: "Node.js standard library only",
      quickMeaning: "Closed source/artifact hashes plus focused deterministic unit and adversarial suites; no expensive current-artifact revalidation.",
      deepMeaning: "The complete quick surface plus the registry-frozen read-only current-artifact validators.",
      quickSuites: QUICK_SUITES.map((suite) => ({ id: suite.id, path: suite.path, args: suite.args.slice() })),
      deepSuites: registryRecord.registry.deepSuites.map((suite) => ({
        id: suite.id,
        path: suite.path,
        args: suite.args.slice(),
        timeoutMs: suite.timeoutMs,
        readOnly: suite.readOnly,
        coverage: suite.coverage
      }))
    },
    sourceManifest: {
      selection: "Portable js/html/css/md/ps1 sources below website/global-geometry-lab, fabrication validation JavaScript, the test workflow, root README, and Global Geometry II root documentation. Outcome directories are excluded.",
      count: sources.length,
      entries: sources
    },
    inputRegistry: {
      path: registryRecord.relativePath,
      rawSha256: registryRecord.rawSha256,
      rawBytes: registryRecord.rawBytes,
      semanticAddress: registryRecord.semanticAddress
    },
    registeredArtifacts,
    archiveIndexBindings,
    compactnessPolicy: {
      maximumRegisteredBytes: MAX_REGISTERED_BYTES,
      gzipTransportPolicy: "Exactly two strict-campaign and two screening-raw gzip transports are raw-addressed; decompressed byte addresses come from the content-addressed evaluation index and the gzip files receive no semantic authority.",
      excludedClasses: [
        "raw JSONL observations",
        "chunk payloads and chunk certificates",
        "partial files and active or stale locks",
        "working checkpoints, transfer helpers, and execution logs",
        "any unregistered file discovered by directory scan"
      ]
    },
    certificationPolicy: {
      localVerificationMeaning: "A PASS certifies only the selected mode, this invocation/environment, the exact v2 source and compact-artifact snapshot, and the recorded suite outcomes.",
      requiredIndependentPlatforms: ["darwin", "win32"],
      requiredIndependentCertificates: 2,
      crossPlatformEqualityClaim: "NOT_MADE_BY_LOCAL_CERTIFICATE",
      externalComparisonRecord: EXTERNAL_COMPARISON_RECORD,
      comparisonScope: "DECLARED_V2_DIGEST_AND_SELECTED_TEST_SURFACE_ONLY"
    },
    approvalGates: {
      publication: "requires explicit user approval",
      merge: "requires explicit user approval",
      hardwarePurchaseOrFabrication: "requires explicit user approval"
    }
  };
}

function packageAddressed(payload) {
  return Object.assign({}, payload, { contentAddress: contentAddress(payload) });
}

function buildIndexPayload(manifestPath, manifestArtifact, options) {
  options = options || {};
  const repoRoot = path.resolve(options.repoRoot || REPO_ROOT);
  const relativeManifest = repoRelative(manifestPath, repoRoot);
  const raw = Buffer.from(JSON.stringify(manifestArtifact, null, 2) + "\n", "utf8");
  return {
    schema: INDEX_SCHEMA,
    releaseId: RELEASE_ID,
    manifest: {
      path: relativeManifest,
      rawSha256: sha256Bytes(raw),
      rawBytes: raw.length,
      contentAddress: manifestArtifact.contentAddress
    },
    inputRegistry: Object.assign({}, manifestArtifact.inputRegistry),
    claimBoundary: Object.assign({}, manifestArtifact.claimBoundary),
    historicalV1: Object.assign({}, manifestArtifact.historicalV1),
    registeredArtifacts: manifestArtifact.registeredArtifacts.map((entry) => ({
      id: entry.id,
      path: entry.path,
      role: entry.role,
      platform: entry.platform,
      rawSha256: entry.rawSha256,
      rawBytes: entry.rawBytes,
      semanticAddress: entry.semanticAddress,
      semanticReplay: entry.semanticReplay
    })),
    archiveIndexBindings: Object.assign({}, manifestArtifact.archiveIndexBindings, {
      bindings: manifestArtifact.archiveIndexBindings.bindings.map((entry) => Object.assign({}, entry))
    }),
    executionSurface: {
      quickSuiteCount: manifestArtifact.execution.quickSuites.length,
      deepSuiteCount: manifestArtifact.execution.deepSuites.length,
      deepRevalidationSeparatedFromQuick: true
    },
    hashTopology: "Registered compact artifacts -> input registry -> manifest -> release index. No file hashes itself; v1 is historical and does not certify v2.",
    certificationStatus: {
      crossPlatformEqualityClaim: "NOT_MADE_BY_INDEX",
      externalComparisonRecord: EXTERNAL_COMPARISON_RECORD,
      releaseGate: "STATUS_DELEGATED_TO_V2_EXTERNAL_COMPARISON_WITH_BOUNDED_SCOPE"
    }
  };
}

function verifyAddressedFile(filePath, expectedSchema) {
  const raw = fs.readFileSync(filePath);
  if (raw.length >= 3 && raw[0] === 0xef && raw[1] === 0xbb && raw[2] === 0xbf) throw new Error("addressed JSON must not contain a byte-order mark: " + filePath);
  let artifact;
  try { artifact = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(raw)); }
  catch (error) { throw new Error("addressed JSON is not valid UTF-8 JSON: " + filePath + ": " + error.message); }
  if (!isPlainObject(artifact) || artifact.schema !== expectedSchema) throw new Error("unexpected schema in " + filePath);
  const supplied = artifact.contentAddress;
  const payload = Object.assign({}, artifact);
  delete payload.contentAddress;
  const computed = contentAddress(payload);
  if (!supplied || !sameJson(supplied, computed)) throw new Error("content address failed for " + filePath);
  return { raw, artifact, payload, address: computed };
}

function writeJsonExclusive(output, value) {
  fs.mkdirSync(path.dirname(output), { recursive: true });
  const descriptor = fs.openSync(output, "wx", 0o644);
  try {
    fs.writeFileSync(descriptor, JSON.stringify(value, null, 2) + "\n", "utf8");
    fs.fsyncSync(descriptor);
  }
  finally { fs.closeSync(descriptor); }
}

function generate(outputs, options) {
  options = options || {};
  const repoRoot = path.resolve(options.repoRoot || REPO_ROOT);
  outputs = outputs || { manifest: DEFAULT_MANIFEST, index: DEFAULT_INDEX, registry: DEFAULT_REGISTRY };
  const manifestPath = resolveFromRepo(outputs.manifest, repoRoot);
  const indexPath = resolveFromRepo(outputs.index, repoRoot);
  const registryPath = resolveFromRepo(outputs.registry || options.registryPath || DEFAULT_REGISTRY, repoRoot);
  if (new Set([manifestPath, indexPath, registryPath]).size !== 3) throw new Error("registry, manifest, and index paths must be distinct");
  [manifestPath, indexPath].forEach((output) => {
    if (fs.existsSync(output)) throw new Error("release-v2 output already exists; generation is write-once: " + repoRelative(output, repoRoot));
  });
  const registryRecord = readRegistry(registryPath, { repoRoot });
  const protectedInputs = new Set(collectSourcePaths({ repoRoot, labRoot: options.labRoot })
    .concat(registryRecord.registry.entries.map((entry) => entry.path))
    .concat([registryRecord.relativePath])
    .map((relative) => path.resolve(repoRoot, relative.split("/").join(path.sep))));
  [manifestPath, indexPath].forEach((output) => {
    if (protectedInputs.has(output)) throw new Error("release-v2 output may not overwrite an input: " + repoRelative(output, repoRoot));
  });
  const manifestPayload = buildManifestPayload({ repoRoot, labRoot: options.labRoot, registryRecord });
  const manifestArtifact = packageAddressed(manifestPayload);
  let manifestCreated = false;
  let indexCreated = false;
  try {
    writeJsonExclusive(manifestPath, manifestArtifact);
    manifestCreated = true;
    const manifestReplay = verifyAddressedFile(manifestPath, MANIFEST_SCHEMA);
    assert.strictEqual(canonicalStringify(manifestReplay.payload), canonicalStringify(manifestPayload));
    const indexPayload = buildIndexPayload(manifestPath, manifestArtifact, { repoRoot });
    const indexArtifact = packageAddressed(indexPayload);
    writeJsonExclusive(indexPath, indexArtifact);
    indexCreated = true;
    const indexReplay = verifyAddressedFile(indexPath, INDEX_SCHEMA);
    assert.strictEqual(canonicalStringify(indexReplay.payload), canonicalStringify(indexPayload));
    if (!sameJson(indexReplay.payload.manifest.contentAddress, manifestReplay.address)) {
      throw new Error("release-v2 index does not point to the generated manifest address");
    }
    return {
      manifest: { path: manifestPath, address: manifestReplay.address },
      index: { path: indexPath, address: indexReplay.address }
    };
  } catch (error) {
    // A failed first-time generation must not leave an apparently valid pair.
    // Only exact files created by this invocation are removed.
    if (indexCreated && fs.existsSync(indexPath)) fs.unlinkSync(indexPath);
    if (manifestCreated && fs.existsSync(manifestPath)) fs.unlinkSync(manifestPath);
    throw error;
  }
}

function parseOutputs(argv) {
  if (!Array.isArray(argv)) throw new Error("argv must be an array");
  if (argv.length === 0) return { manifest: DEFAULT_MANIFEST, index: DEFAULT_INDEX, registry: DEFAULT_REGISTRY };
  if (argv.length !== 6) throw new Error("use no arguments or exactly --registry PATH --manifest PATH --index PATH");
  const allowed = new Set(["--registry", "--manifest", "--index"]);
  const values = {};
  for (let index = 0; index < argv.length; index += 2) {
    const flag = argv[index];
    const value = argv[index + 1];
    if (!allowed.has(flag)) throw new Error("unknown release-v2 generator argument " + flag);
    if (Object.prototype.hasOwnProperty.call(values, flag)) throw new Error(flag + " may be supplied only once");
    if (typeof value !== "string" || !value || value.startsWith("--")) throw new Error(flag + " requires an explicit path");
    values[flag] = resolveFromRepo(value, REPO_ROOT);
  }
  allowed.forEach((flag) => {
    if (!Object.prototype.hasOwnProperty.call(values, flag)) throw new Error(flag + " is required with explicit outputs");
  });
  if (new Set(Object.values(values)).size !== 3) throw new Error("registry, manifest, and index paths must be distinct");
  return { registry: values["--registry"], manifest: values["--manifest"], index: values["--index"] };
}

function generatorCliSummary(result) {
  return {
    manifest: { output: result.manifest.path, sha256: result.manifest.address.digest },
    index: { output: result.index.path, sha256: result.index.address.digest },
    checkpointMeaning: "SHAREABLE_EVIDENCE_CHECKPOINT_NOT_A_CONFIRMATORY_DECISION",
    u2Decision: "NO_ACCEPTANCE_OR_REJECTION_CLAIM",
    physicalValidation: "NOT_RUN",
    historicalV1: HISTORICAL_V1_CLASSIFICATION,
    externalComparisonRecord: EXTERNAL_COMPARISON_RECORD
  };
}

function main() {
  try {
    const outputs = parseOutputs(process.argv.slice(2));
    const result = generate(outputs);
    process.stdout.write(JSON.stringify(generatorCliSummary(result)) + "\n");
  } catch (error) {
    process.stderr.write("Global Geometry II release-v2 generation failed: " + (error && error.message ? error.message : String(error)) + "\n");
    process.exitCode = 1;
  }
}

if (require.main === module) main();

module.exports = {
  ADDRESSING_POLICIES,
  ADDRESS_CANONICALIZATION,
  ARCHIVE_ROLES,
  DEFAULT_INDEX,
  DEFAULT_MANIFEST,
  DEFAULT_REGISTRY,
  ENTRY_ROLES,
  EXTERNAL_COMPARISON_RECORD,
  EVALUATION_INDEX_SCHEMA,
  ARCHIVE_ROLE,
  HISTORICAL_V1_CLASSIFICATION,
  HISTORICAL_V1_COMPARISON,
  HISTORICAL_V1_INDEX,
  INDEX_SCHEMA,
  MANIFEST_SCHEMA,
  MAX_REGISTERED_BYTES,
  PHYSICAL_PREFLIGHT_ARTIFACT,
  PRINCIPAL_ARTIFACTS,
  QUICK_SUITES,
  REGISTRY_SCHEMA,
  RELEASE_ID,
  REPO_ROOT,
  REQUIRED_PAIRED_ROLES,
  REQUIRED_DEEP_VALIDATION_SURFACES,
  REQUIRED_ROLE_COUNTS,
  SAFE_DEEP_VALIDATION_FLAGS,
  assertCompactEntryPath,
  buildIndexPayload,
  buildManifestPayload,
  canonicalStringify,
  collectSourcePaths,
  contentAddress,
  generate,
  generatorCliSummary,
  inspectRegisteredEntry,
  packageAddressed,
  parseOutputs,
  readRegistry,
  repoRelative,
  sha256Bytes,
  sha256File,
  sourceEntries,
  validateRegistry,
  verifyArchiveIndexBindings,
  verifyAddressedFile,
  verifySuppliedContentAddress
};
