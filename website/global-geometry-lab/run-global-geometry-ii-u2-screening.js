#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const childProcess = require("child_process");
const { performance } = require("perf_hooks");
const Screening = require("./global-geometry-ii-u2-screening.js");

function parseArgs(argv) {
  const options = { platformLabel: process.platform === "darwin" ? "macos" : process.platform, sourceCommit: null, validateOnly: false };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--platform-label" && argv[index + 1]) options.platformLabel = argv[++index];
    else if (arg === "--source-commit" && argv[index + 1]) options.sourceCommit = argv[++index];
    else if (arg === "--validate-only") options.validateOnly = true;
    else throw new Error("usage: run-global-geometry-ii-u2-screening.js --source-commit HASH [--platform-label label] [--validate-only]");
  }
  if (!options.sourceCommit) throw new Error("--source-commit is required so the production run binds a committed implementation boundary");
  if (!/^[a-z0-9_-]{1,32}$/.test(options.platformLabel)) throw new Error("platform label must match [a-z0-9_-]{1,32}");
  return options;
}

function git(args) {
  return childProcess.execFileSync("git", args, { cwd: Screening.ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
}

function assertSourceBoundary(sourceCommit) {
  const full = git(["rev-parse", sourceCommit + "^{commit}"]);
  const supplementRelative = "artifacts/global-geometry-ii/u2/screening/screening-implementation-supplement-v2.json";
  const moduleRelative = "website/global-geometry-lab/global-geometry-ii-u2-screening.js";
  const runnerRelative = "website/global-geometry-lab/run-global-geometry-ii-u2-screening.js";
  const supplementAtCommit = childProcess.execFileSync("git", ["show", full + ":" + supplementRelative], { cwd: Screening.ROOT });
  if (Screening.sha256Bytes(supplementAtCommit) !== "5380552dc7c6ee91d6e632b7bfec6a6031d49ab0b98a2aa6f95b71b4c73ab8d6") throw new Error("source commit does not contain the frozen screening supplement");
  [moduleRelative, runnerRelative].forEach(function (relative) {
    const committed = childProcess.execFileSync("git", ["show", full + ":" + relative], { cwd: Screening.ROOT });
    const working = fs.readFileSync(path.join(Screening.ROOT, relative));
    if (!committed.equals(working)) throw new Error(relative + " working bytes differ from the bound source commit");
  });
  return full;
}

function pathsFor(label) {
  const directory = path.join(Screening.ROOT, "artifacts/global-geometry-ii/u2/screening");
  return {
    directory: directory,
    raw: path.join(directory, "screening-raw-" + label + "-v1.jsonl"),
    summary: path.join(directory, "screening-summary-" + label + "-v1.json"),
    runtime: path.join(directory, "screening-runtime-" + label + "-v1.json")
  };
}

function percentile(values, probability) {
  if (!values.length) return null;
  const sorted = values.slice().sort(function (a, b) { return a - b; }), position = (sorted.length - 1) * probability, lower = Math.floor(position), upper = Math.ceil(position), alpha = position - lower;
  return sorted[lower] * (1 - alpha) + sorted[upper] * alpha;
}

function writeOnce(output, bytes) {
  if (fs.existsSync(output)) {
    const existing = fs.readFileSync(output);
    if (!existing.equals(bytes)) throw new Error("write-once artifact already exists with different bytes: " + output);
    return "EXISTING_IDENTICAL";
  }
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, bytes, { flag: "wx" });
  return "CREATED";
}

function parseRaw(bytes) {
  const text = bytes.toString("utf8"), lines = text.endsWith("\n") ? text.slice(0, -1).split("\n") : text.split("\n");
  return lines.filter(Boolean).map(function (line) { return JSON.parse(line); });
}

function validateExisting(paths) {
  const rawBytes = fs.readFileSync(paths.raw), records = parseRaw(rawBytes), summary = JSON.parse(fs.readFileSync(paths.summary, "utf8"));
  const started = performance.now(), report = Screening.validateSummary(summary, records, rawBytes);
  return { report: report, records: records, summary: summary, rawBytes: rawBytes, validationMilliseconds: performance.now() - started };
}

function runtimeCertificate(label, sourceCommit, rawBytes, summaryBytes, metrics) {
  const payload = {
    schema: "gg.u2.screening.runtime-certificate/1",
    semanticRole: "non-semantic execution telemetry; excluded from record hashes, record Merkle root, and scientific summary content address",
    platformLabel: label,
    sourceCommit: sourceCommit,
    manifestDigest: Screening.EXPECTED_MANIFEST_SEMANTIC_SHA256,
    supplementDigest: Screening.EXPECTED_SUPPLEMENT_SEMANTIC_SHA256,
    environment: { platform: process.platform, arch: process.arch, node: process.version, cpuCount: require("os").cpus().length },
    artifacts: {
      raw: { bytes: rawBytes.length, sha256: Screening.sha256Bytes(rawBytes) },
      summary: { bytes: summaryBytes.length, sha256: Screening.sha256Bytes(summaryBytes) }
    },
    runtime: metrics,
    u2Status: "UNRESOLVED"
  };
  return Object.assign({}, payload, { contentAddress: { algorithm: "sha256", digest: Screening.sha256JSON(payload), canonicalBytes: Buffer.byteLength(Screening.canonicalStringify(payload), "utf8") } });
}

function run(options) {
  Screening.loadManifest();
  const sourceCommit = assertSourceBoundary(options.sourceCommit), paths = pathsFor(options.platformLabel);
  if (options.validateOnly) {
    const existing = validateExisting(paths);
    if (!existing.report.valid) throw new Error("existing screening validation failed: " + existing.report.errors.slice(0, 20).join("; "));
    process.stdout.write(JSON.stringify({ mode: "validate-only", records: existing.records.length, validationMilliseconds: existing.validationMilliseconds, summaryDigest: existing.summary.contentAddress.digest, u2Status: existing.summary.outcome.u2Status }) + "\n");
    return;
  }
  [paths.raw, paths.summary, paths.runtime].forEach(function (output) { if (fs.existsSync(output)) throw new Error("refusing to begin production because write-once output already exists: " + output); });
  const census = Screening.expectedCensus();
  if (census.length !== 3840) throw new Error("unexpected production census");
  const records = [], times = [], startWall = new Date().toISOString(), started = performance.now(); let peakRss = process.memoryUsage().rss;
  const partialRaw = paths.raw + ".partial-" + process.pid, rawDescriptor = fs.openSync(partialRaw, "wx");
  census.forEach(function (identity, index) {
    const recordStarted = performance.now(), record = Screening.buildRecord(identity), elapsed = performance.now() - recordStarted;
    const report = Screening.validateRecord(record, identity, { remeasure: false });
    if (!report.valid) throw new Error("fresh record validation failed for " + identity.runId + ": " + report.errors.join("; "));
    records.push(record); times.push(elapsed); fs.writeSync(rawDescriptor, Buffer.from(Screening.canonicalStringify(record) + "\n", "utf8"));
    peakRss = Math.max(peakRss, process.memoryUsage().rss);
    if ((index + 1) % 32 === 0) { fs.fsyncSync(rawDescriptor); process.stderr.write(JSON.stringify({ progress: index + 1, total: census.length, elapsedSeconds: (performance.now() - started) / 1000, lastRunId: identity.runId, peakRssBytes: peakRss, checkpoint: path.basename(partialRaw) }) + "\n"); }
  });
  fs.fsyncSync(rawDescriptor); fs.closeSync(rawDescriptor);
  const generationMilliseconds = performance.now() - started, rawBytes = fs.readFileSync(partialRaw), rawRelative = path.relative(Screening.ROOT, paths.raw).split(path.sep).join("/");
  const rawBinding = { path: rawRelative, bytes: rawBytes.length, sha256: Screening.sha256Bytes(rawBytes) };
  const summary = Screening.summarizeRecords(records, rawBinding), summaryBytes = Buffer.from(JSON.stringify(summary, null, 2) + "\n", "utf8");
  const validationStarted = performance.now(), validation = Screening.validateSummary(summary, records, rawBytes), validationMilliseconds = performance.now() - validationStarted;
  if (!validation.valid) throw new Error("full semantic screening replay failed: " + validation.errors.slice(0, 20).join("; "));
  const metrics = {
    planningEstimateStatus: "UNVALIDATED_PLANNING_ESTIMATE_BEFORE_RUN",
    startWallTime: startWall,
    endWallTime: new Date().toISOString(),
    generationMilliseconds: generationMilliseconds,
    fullSemanticReplayMilliseconds: validationMilliseconds,
    totalWallMilliseconds: performance.now() - started,
    recordElapsedMilliseconds: { count: times.length, minimum: Math.min.apply(null, times), median: percentile(times, 0.5), p95: percentile(times, 0.95), maximum: Math.max.apply(null, times), mean: times.reduce(function (sum, value) { return sum + value; }, 0) / times.length },
    peakRssBytes: peakRss,
    failureRecordCount: records.filter(function (record) { return record.failures.length; }).length,
    failureEntryCount: records.reduce(function (sum, record) { return sum + record.failures.length; }, 0)
  };
  const runtime = runtimeCertificate(options.platformLabel, sourceCommit, rawBytes, summaryBytes, metrics), runtimeBytes = Buffer.from(JSON.stringify(runtime, null, 2) + "\n", "utf8");
  if (fs.existsSync(paths.raw)) throw new Error("write-once raw artifact appeared during production");
  fs.renameSync(partialRaw, paths.raw);
  const dispositions = { raw: "CREATED_FROM_CHECKPOINT", summary: writeOnce(paths.summary, summaryBytes), runtime: writeOnce(paths.runtime, runtimeBytes) };
  const post = validateExisting(paths);
  if (!post.report.valid) throw new Error("post-write semantic replay failed: " + post.report.errors.slice(0, 20).join("; "));
  process.stdout.write(JSON.stringify({ paths: paths, dispositions: dispositions, records: records.length, failures: summary.failureLedger.count, rawSha256: rawBinding.sha256, recordMerkleRoot: summary.integrity.recordMerkleRoot, summaryDigest: summary.contentAddress.digest, runtimeDigest: runtime.contentAddress.digest, generationMilliseconds: generationMilliseconds, semanticReplayMilliseconds: validationMilliseconds, postWriteReplayMilliseconds: post.validationMilliseconds, peakRssBytes: peakRss, u2Status: summary.outcome.u2Status }) + "\n");
}

if (require.main === module) run(parseArgs(process.argv.slice(2)));
module.exports = { parseArgs: parseArgs, assertSourceBoundary: assertSourceBoundary, pathsFor: pathsFor, parseRaw: parseRaw, validateExisting: validateExisting, runtimeCertificate: runtimeCertificate, run: run };
