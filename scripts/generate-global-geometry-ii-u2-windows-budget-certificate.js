#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const INPUT_DIR = path.join(ROOT, "artifacts", "global-geometry-ii", "u2", "readiness");
const WRAPPER_PATH = path.join(ROOT, "scripts", "run-global-geometry-ii-u2-windows-readiness.ps1");
const REPORT_PATH = path.join(INPUT_DIR, "windows-readiness-wrapper-run-v2.json");
const EXPECTED_BENCHMARK_SHA256 = "68c839dabace59d67274f8c1df48eff59ada23f128f2705042c92b0697dc187a";
const EXPECTED_SOURCE_COMMIT = "e240c1bdc2037ecd597bbfc535e233109194c4f8";

function fail(message) {
  throw new Error(message);
}

function sha256(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function canonicalize(value) {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map(function (key) {
      return [key, canonicalize(value[key])];
    }));
  }
  return value;
}

function canonicalDigest(value) {
  return sha256(Buffer.from(JSON.stringify(canonicalize(value)), "utf8"));
}

function median(values) {
  const sorted = values.slice().sort(function (a, b) { return a - b; });
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

function range(values) {
  return {
    minimum: Math.min.apply(null, values),
    median: median(values),
    maximum: Math.max.apply(null, values)
  };
}

function windowsBasename(value) {
  return value.split("\\").pop();
}

function parseRaw(entry) {
  const artifact = windowsBasename(entry.path);
  const artifactPath = path.join(INPUT_DIR, artifact);
  const bytes = fs.readFileSync(artifactPath);
  const text = bytes.toString("utf8");
  if (Buffer.from(text, "utf8").compare(bytes) !== 0) fail(artifact + ": invalid UTF-8");
  if (bytes.subarray(0, 3).equals(Buffer.from([0xef, 0xbb, 0xbf]))) fail(artifact + ": unexpected BOM");
  if (!/[^\r\n]\r\n$/.test(text)) fail(artifact + ": expected exactly one trailing CRLF");
  if (/(^|[^\r])\n/.test(text) || /\r(?!\n)/.test(text)) fail(artifact + ": non-CRLF line ending");
  const rawSha256 = sha256(bytes);
  if (bytes.length !== entry.bytes) fail(artifact + ": byte count differs from wrapper report");
  if (rawSha256 !== entry.sha256) fail(artifact + ": SHA-256 differs from wrapper report");

  const record = JSON.parse(text);
  if (record.schema !== "ggii.u2.feasibility-benchmark/1") fail(artifact + ": wrong schema");
  if (record.scientificOutcome !== false) fail(artifact + ": scientific boundary violation");
  const withoutDigest = Object.assign({}, record);
  delete withoutDigest.contentDigest;
  const computedContentDigest = sha256(Buffer.from(JSON.stringify(withoutDigest), "utf8"));
  if (computedContentDigest !== record.contentDigest) fail(artifact + ": embedded content digest mismatch");
  if (!(record.conjugateGradient.relativeResidual <= 1e-8)) fail(artifact + ": CG residual exceeded probe tolerance");
  if (!(record.exitBallSolve.relativeResidual <= 1e-8)) fail(artifact + ": exit-solve residual exceeded probe tolerance");

  return {
    artifact: artifact,
    bytes: bytes.length,
    rawSha256: rawSha256,
    contentDigest: record.contentDigest,
    processWallSeconds: entry.processWallSeconds,
    record: record
  };
}

function invariant(records, accessor, label) {
  const values = records.map(accessor);
  if (values.some(function (value) { return value !== values[0]; })) fail(label + " was not invariant");
  return values[0];
}

const reportBytes = fs.readFileSync(REPORT_PATH);
const report = JSON.parse(reportBytes.toString("utf8"));
if (report.schema !== "ggii.u2.windows-readiness-wrapper-run/2") fail("wrong wrapper-report schema");
if (report.scientificOutcome !== false || report.scientificOutcomesRun !== false) fail("scientific boundary violation");
if (report.u2ScientificSourceTransferred !== false) fail("scientific source boundary violation");
if (report.benchmarkSha256 !== EXPECTED_BENCHMARK_SHA256) fail("benchmark SHA-256 mismatch");
if (report.benchmarkSourceCommit !== EXPECTED_SOURCE_COMMIT) fail("benchmark source commit mismatch");
if (!Array.isArray(report.exactBenchmarkArgs) || report.exactBenchmarkArgs.length !== 0) fail("default benchmark must have no CLI arguments");
if (report.repetitions !== 5 || report.sequential.length !== 5) fail("expected five sequential repetitions");
if (report.concurrent.workers !== 4 || report.concurrent.items.length !== 4) fail("expected four concurrent workers");

const wrapperSha256 = sha256(fs.readFileSync(WRAPPER_PATH));
if (wrapperSha256 !== report.wrapperSha256) fail("local wrapper differs from executed wrapper");

const sequential = report.sequential.map(parseRaw);
const concurrent = report.concurrent.items.map(parseRaw);
const allRecords = sequential.concat(concurrent);

invariant(allRecords, function (item) { return item.record.syntheticGraph.vertices; }, "vertex count");
invariant(allRecords, function (item) { return item.record.syntheticGraph.undirectedEdges; }, "edge count");
invariant(allRecords, function (item) { return item.record.sparseApply.checksum; }, "sparse checksum");
invariant(allRecords, function (item) { return item.record.dijkstra.checksum; }, "Dijkstra checksum");
invariant(allRecords, function (item) { return item.record.conjugateGradient.checksum; }, "CG checksum");
invariant(allRecords, function (item) { return item.record.exitBallSolve.checksum; }, "exit-solve checksum");
invariant(allRecords, function (item) { return item.record.conjugateGradient.iterations; }, "CG iterations");
invariant(allRecords, function (item) { return item.record.exitBallSolve.iterationsPerSolve; }, "exit-solve iterations");

const starts = report.concurrent.items.map(function (entry) { return Date.parse(entry.startedAtUtc) / 1000; });
const ends = report.concurrent.items.map(function (entry) { return Date.parse(entry.endedAtUtc) / 1000; });
const allWorkerOverlapSeconds = Math.min.apply(null, ends) - Math.max.apply(null, starts);
if (!(allWorkerOverlapSeconds > 0)) fail("concurrent workers did not have a common overlap interval");

function artifactDescriptor(item, concurrency) {
  const descriptor = {
    artifact: item.artifact,
    bytes: item.bytes,
    rawSha256: item.rawSha256,
    contentDigest: item.contentDigest,
    processWallSeconds: item.processWallSeconds
  };
  if (concurrency) {
    descriptor.startedAtUtc = concurrency.startedAtUtc;
    descriptor.endedAtUtc = concurrency.endedAtUtc;
  }
  return descriptor;
}

function metric(records, accessor) {
  return range(records.map(function (item) { return accessor(item.record); }));
}

const sequentialProcessWall = sequential.map(function (item) { return item.processWallSeconds; });
const concurrentProcessWall = concurrent.map(function (item) { return item.processWallSeconds; });
const sumConcurrentProcessWall = concurrentProcessWall.reduce(function (sum, value) { return sum + value; }, 0);

const certificate = {
  schema: "ggii.u2.windows-budget-certificate/1",
  scientificOutcome: false,
  purpose: "Canonical outcome-blind budget observation for the strict U2 implementation plan",
  evidenceBoundary: {
    benchmarkSourceCommit: EXPECTED_SOURCE_COMMIT,
    benchmarkPath: "scripts/benchmark-global-geometry-ii-u2-full-evaluation.js",
    benchmarkSha256: EXPECTED_BENCHMARK_SHA256,
    exactCliArguments: [],
    resolvedDefaults: {
      rows: 171,
      cols: 171,
      applyRepeats: 256,
      dijkstraRoots: 8,
      cgCap: 960,
      exitSide: 49,
      exitRepeats: 8
    },
    u2ScientificSourceTransferred: false,
    u2ScientificOutcomesRun: false
  },
  executionWrapper: {
    path: "scripts/run-global-geometry-ii-u2-windows-readiness.ps1",
    sha256: wrapperSha256,
    reportArtifact: path.basename(REPORT_PATH),
    reportBytes: reportBytes.length,
    reportRawSha256: sha256(reportBytes),
    reportGeneratedAtUtc: report.generatedAtUtc
  },
  environment: {
    platform: sequential[0].record.environment.platform,
    architecture: sequential[0].record.environment.arch,
    node: sequential[0].record.environment.node,
    cpuModel: sequential[0].record.environment.cpuModel.trim(),
    logicalCpus: sequential[0].record.environment.logicalCpus,
    totalMemoryBytes: sequential[0].record.environment.totalMemoryBytes
  },
  rawEncoding: {
    characterEncoding: "UTF-8",
    byteOrderMark: false,
    lineEnding: "CRLF",
    exactlyOneTrailingCrlf: true,
    rawFilesRewrittenAfterRetrieval: false
  },
  sequentialObservation: {
    repetitions: sequential.length,
    artifacts: sequential.map(function (item) { return artifactDescriptor(item); }),
    processWallSeconds: range(sequentialProcessWall),
    graphBuildSeconds: metric(sequential, function (record) { return record.syntheticGraph.buildSeconds; }),
    sparseApplySeconds: metric(sequential, function (record) { return record.sparseApply.seconds; }),
    sparseApplyUndirectedEdgeApplicationsPerSecond: metric(sequential, function (record) { return record.sparseApply.undirectedEdgeApplicationsPerSecond; }),
    dijkstraSeconds: metric(sequential, function (record) { return record.dijkstra.seconds; }),
    dijkstraRootsPerSecond: metric(sequential, function (record) { return record.dijkstra.rootsPerSecond; }),
    conjugateGradientSeconds: metric(sequential, function (record) { return record.conjugateGradient.seconds; }),
    exitBallSolveSeconds: metric(sequential, function (record) { return record.exitBallSolve.seconds; }),
    exitBallSolvesPerSecond: metric(sequential, function (record) { return record.exitBallSolve.solvesPerSecond; }),
    processRssBytes: metric(sequential, function (record) { return record.processMemory.rssBytes; })
  },
  concurrentObservation: {
    workers: concurrent.length,
    artifacts: concurrent.map(function (item, index) { return artifactDescriptor(item, report.concurrent.items[index]); }),
    groupStartedAtUtc: report.concurrent.groupStartedAtUtc,
    groupEndedAtUtc: report.concurrent.groupEndedAtUtc,
    groupWallSeconds: report.concurrent.groupWallSeconds,
    processWallSeconds: range(concurrentProcessWall),
    sumProcessWallSeconds: sumConcurrentProcessWall,
    processOverlapFactor: sumConcurrentProcessWall / report.concurrent.groupWallSeconds,
    allWorkerOverlapSeconds: allWorkerOverlapSeconds,
    benchmarkCompletionsPerGroupSecond: concurrent.length / report.concurrent.groupWallSeconds,
    sparseApplyUndirectedEdgeApplicationsPerSecond: metric(concurrent, function (record) { return record.sparseApply.undirectedEdgeApplicationsPerSecond; }),
    sumReportedSparseApplyRates: concurrent.reduce(function (sum, item) { return sum + item.record.sparseApply.undirectedEdgeApplicationsPerSecond; }, 0),
    dijkstraRootsPerSecond: metric(concurrent, function (record) { return record.dijkstra.rootsPerSecond; }),
    sumReportedDijkstraRates: concurrent.reduce(function (sum, item) { return sum + item.record.dijkstra.rootsPerSecond; }, 0),
    conjugateGradientSeconds: metric(concurrent, function (record) { return record.conjugateGradient.seconds; }),
    exitBallSolvesPerSecond: metric(concurrent, function (record) { return record.exitBallSolve.solvesPerSecond; }),
    sumReportedExitBallSolveRates: concurrent.reduce(function (sum, item) { return sum + item.record.exitBallSolve.solvesPerSecond; }, 0),
    processRssBytes: metric(concurrent, function (record) { return record.processMemory.rssBytes; }),
    sumReportedProcessRssBytes: concurrent.reduce(function (sum, item) { return sum + item.record.processMemory.rssBytes; }, 0),
    note: "Summed per-process rates and RSS are descriptive aggregates; the timestamp interval proves four-way overlap, but the per-kernel timers were not phase-synchronized."
  },
  deterministicChecks: {
    vertices: sequential[0].record.syntheticGraph.vertices,
    undirectedEdges: sequential[0].record.syntheticGraph.undirectedEdges,
    conjugateGradientIterations: sequential[0].record.conjugateGradient.iterations,
    conjugateGradientRelativeResidual: sequential[0].record.conjugateGradient.relativeResidual,
    exitBallIterationsPerSolve: sequential[0].record.exitBallSolve.iterationsPerSolve,
    exitBallRelativeResidual: sequential[0].record.exitBallSolve.relativeResidual,
    allPrimaryChecksumsInvariant: true,
    allEmbeddedContentDigestsVerified: true,
    allRawHashesAndByteCountsVerified: true,
    allRawEncodingChecksPassed: true,
    allDefaultSolverResidualsAtMost1eMinus8: true
  },
  interpretation: {
    windowsSyntheticBudgetObserved: true,
    decisionGradeRuntimeProjectionMade: false,
    scientificReplicationAuthorizedByThisCertificate: false,
    note: "This times reusable synthetic numerical primitives. It does not estimate the full strict U2 wall time or evaluate any scientific gate."
  }
};

certificate.canonicalDigestAlgorithm = "sha256(sorted-key canonical JSON of the certificate without canonicalDigest)";
certificate.canonicalDigest = canonicalDigest(certificate);
process.stdout.write(JSON.stringify(certificate, null, 2) + "\n");
