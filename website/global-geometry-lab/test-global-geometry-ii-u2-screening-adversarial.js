#!/usr/bin/env node
"use strict";

/* Outcome-blind independent audit of the bounded U2 screening manifest. */
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const Screening = require("./generate-global-geometry-ii-u2-screening-manifest.js");
const Supplement = require("./generate-global-geometry-ii-u2-screening-supplement.js");
const Evaluator = require("./global-geometry-ii-u2-screening.js");

let passed = 0;
function test(name, fn) {
  try {
    fn();
    passed += 1;
    process.stdout.write("PASS " + name + "\n");
  } catch (error) {
    process.stderr.write("FAIL " + name + "\n" + error.stack + "\n");
    process.exitCode = 1;
  }
}

function readdress(manifest) {
  const payload = JSON.parse(JSON.stringify(manifest));
  delete payload.contentAddress;
  const canonical = Screening.canonicalStringify(payload);
  payload.contentAddress = {
    algorithm: "sha256",
    canonicalization: "RFC8785-compatible closed JSON subset",
    digest: Screening.sha256Bytes(Buffer.from(canonical, "utf8")),
    canonicalBytes: Buffer.byteLength(canonical, "utf8")
  };
  return payload;
}

test("committed screening manifest exactly replays its outcome-blind builder", function () {
  const expected = Screening.buildManifest();
  const committed = JSON.parse(fs.readFileSync(path.resolve(
    __dirname, "../../artifacts/global-geometry-ii/u2/screening/screening-manifest-v1.json"
  ), "utf8"));
  assert.deepStrictEqual(committed, expected);
  assert.strictEqual(Screening.validateManifest(committed).valid, true);
});

test("screening has no U2 decision authority", function () {
  const manifest = Screening.buildManifest();
  assert.strictEqual(manifest.freezeStatus.decisionAuthority, "NONE");
  assert.strictEqual(manifest.freezeStatus.forcedU2Status, "UNRESOLVED");
  assert.strictEqual(manifest.failureSemantics.scientificRejectionAllowed, false);
  assert.match(manifest.scope.claimLimit, /cannot (?:PASS|FAIL).*Gates 2-8/i);
});

test("screening census includes all positive records and four frozen controls", function () {
  const manifest = Screening.buildManifest();
  assert.strictEqual(manifest.scope.positiveMatrix.recordCount, 3072);
  assert.strictEqual(manifest.scope.controls.recordCount, 768);
  assert.deepStrictEqual(manifest.scope.controls.ids, [
    "comb-trap", "small-world-shortcuts", "vanishing-neck", "perforated-disk"
  ]);
  assert.strictEqual(manifest.artifactContract.expectedRawRecords, 3840);
});

test("a fresh hash cannot bless altered screening estimator semantics", function () {
  const manifest = Screening.buildManifest();
  manifest.estimators.randomWalkScreen.walkersPerRoot = 80;
  assert.strictEqual(Screening.validateManifest(readdress(manifest)).valid, false);
});

test("a fresh hash cannot bless a substituted screening control", function () {
  const manifest = Screening.buildManifest();
  manifest.scope.controls.ids[3] = "critical-bond-control";
  assert.strictEqual(Screening.validateManifest(readdress(manifest)).valid, false);
});

test("a fresh hash cannot redirect the bound decision contract", function () {
  const manifest = Screening.buildManifest();
  const governing = manifest.bindings.governingSpecification;
  manifest.bindings.decisionContract = JSON.parse(JSON.stringify(governing));
  assert.strictEqual(Screening.validateManifest(readdress(manifest)).valid, false);
});

test("immutable v1 discloses its non-hierarchical interval and has no decision authority", function () {
  const manifest = Screening.buildManifest();
  assert.match(manifest.estimators.randomWalkScreen.interval, /non-hierarchical/i);
  assert.strictEqual(manifest.freezeStatus.decisionAuthority, "NONE");
  assert.strictEqual(manifest.failureSemantics.scientificRejectionAllowed, false);
});

test("implementation supplement exactly replays and rejects fresh-hash mutation", function () {
  const expected = Supplement.buildSupplement();
  const committed = JSON.parse(fs.readFileSync(path.resolve(
    __dirname, "../../artifacts/global-geometry-ii/u2/screening/screening-implementation-supplement-v2.json"
  ), "utf8"));
  assert.deepStrictEqual(committed, expected);
  assert.strictEqual(committed.schema, "gg.u2.screening.implementation-supplement/2");
  assert.strictEqual(committed.supplementId, "ggii-u2-v2-screening-implementation-v2");
  assert.strictEqual(Supplement.validateSupplement(committed).valid, true);
  const mutated = JSON.parse(JSON.stringify(committed));
  mutated.estimatorLanguageCorrections.randomWalk.counts.walkersPerRoot = 80;
  delete mutated.contentAddress;
  const canonical = Supplement.canonicalStringify(mutated);
  mutated.contentAddress = {
    algorithm: "sha256",
    canonicalization: "RFC8785-compatible closed JSON subset",
    digest: Supplement.sha256Bytes(Buffer.from(canonical, "utf8")),
    canonicalBytes: Buffer.byteLength(canonical, "utf8")
  };
  assert.strictEqual(Supplement.validateSupplement(mutated).valid, false);
});

test("supplement freezes non-inferential estimator language", function () {
  const supplement = Supplement.buildSupplement();
  assert.match(supplement.estimatorLanguageCorrections.randomWalk.label, /descriptive/i);
  assert.match(supplement.estimatorLanguageCorrections.randomWalk.label, /not a confidence interval/i);
  assert.match(supplement.estimatorLanguageCorrections.volumeGrowth.label, /not a dimension estimate/i);
  assert.match(supplement.estimatorLanguageCorrections.transport.prohibitedConclusion, /No screening transport observable can establish transport noncollapse/i);
});

test("screening record replay excludes nondeterministic telemetry from scientific identity", function () {
  const identity = Evaluator.expectedCensus()[0];
  const first = Evaluator.buildRecord(identity);
  const second = Evaluator.buildRecord(identity);
  assert.strictEqual(first.recordHash, second.recordHash);
  assert.strictEqual(Evaluator.replayRecord(first).valid, true);
});

test("screening record fields obey supplement estimator names", function () {
  const record = Evaluator.buildRecord(Evaluator.expectedCensus()[0]);
  assert.ok(Object.prototype.hasOwnProperty.call(record.volumeGrowthScreen, "logLogSlopeDescriptor"));
  assert.ok(!Object.prototype.hasOwnProperty.call(record.volumeGrowthScreen, "meanProfileExponent"));
});

test("largest perforated control is constructible without argument explosion", function () {
  const seed = Evaluator.deriveSeed("control", "perforated-disk", 120, -1, 0, "control");
  const graph = Evaluator.buildControl("perforated-disk", 120, seed);
  assert.strictEqual(graph.metadata.removedFaceStarCount, graph.metadata.targetHoleCount);
  assert.ok(graph.metadata.minimumCenterSeparationObserved >= 3);
  assert.strictEqual(Evaluator.analyzeGraph(graph).public.surfaceWitness.valid, true);
});

let aggregateFixture = null;
function buildAggregateFixture() {
  if (aggregateFixture) return aggregateFixture;
  const selected = Evaluator.expectedCensus().filter(function (identity) {
    if (identity.size !== 16) return false;
    if (identity.kind === "positive") {
      return (identity.id === "square-alternating" && (identity.sigmaIndex === 0 || identity.sigmaIndex === 1)) ||
        (identity.id === "square-hashed-diagonal" && identity.sigmaIndex === 0);
    }
    return identity.id === "comb-trap";
  });
  const records = selected.map(Evaluator.buildRecord);
  const rawBytes = Buffer.from(records.map(function (record) {
    return Evaluator.canonicalStringify(record) + "\n";
  }).join(""), "utf8");
  const rawBinding = { path: "audit-fixture.jsonl", bytes: rawBytes.length, sha256: Evaluator.sha256Bytes(rawBytes) };
  aggregateFixture = {
    records: records,
    rawBytes: rawBytes,
    rawBinding: rawBinding,
    summary: Evaluator.summarizeRecords(records, rawBinding)
  };
  return aggregateFixture;
}

function positiveCell(summary, family, sigmaIndex) {
  return summary.positiveCells.find(function (cell) {
    return cell.family === family && cell.size === 16 && cell.sigmaIndex === sigmaIndex;
  });
}

test("independence reporting uses construction realizations rather than nested batches", function () {
  const summary = buildAggregateFixture().summary;
  const deterministic = positiveCell(summary, "square-alternating", 0);
  assert.strictEqual(deterministic.recordCount, 32);
  assert.strictEqual(deterministic.uniqueStructureDigests, 1);
  assert.strictEqual(deterministic.uniqueWeightedRealizationCount, 1);
  assert.deepStrictEqual(deterministic.independence, {
    constructionRealizationCount: 1,
    nestedMeasurementBatchCount: 32,
    measurementBatchCount: 32,
    measurementBatchesPerConstruction: 32,
    label: "one deterministic geometry with 32 nested measurement batches; not n=32 independent geometries"
  });

  const hashed = positiveCell(summary, "square-hashed-diagonal", 0);
  assert.strictEqual(hashed.recordCount, 32);
  assert.ok(hashed.uniqueStructureDigests > 1);
  assert.deepStrictEqual(hashed.independence, {
    constructionRealizationCount: 32,
    nestedMeasurementBatchCount: 0,
    measurementBatchCount: 32,
    measurementBatchesPerConstruction: 1,
    label: "32 weighted construction realizations, one measurement batch each"
  });

  const weighted = positiveCell(summary, "square-alternating", 1);
  assert.strictEqual(weighted.uniqueStructureDigests, 1);
  assert.strictEqual(weighted.uniqueWeightedRealizationCount, 32);
  assert.strictEqual(weighted.independence.constructionRealizationCount, 32);
  assert.strictEqual(weighted.independence.nestedMeasurementBatchCount, 0);

  const comb = summary.controlCells.find(function (cell) {
    return cell.control === "comb-trap" && cell.size === 16;
  });
  assert.strictEqual(comb.recordCount, 32);
  assert.strictEqual(comb.uniqueStructureDigests, 1);
  assert.strictEqual(comb.independence.constructionRealizationCount, 1);
  assert.strictEqual(comb.independence.nestedMeasurementBatchCount, 32);
});

test("cell aggregates independently replay and fresh-hash aggregate tampering is exposed", function () {
  const fixture = buildAggregateFixture();
  const records = fixture.records.filter(function (record) {
    return record.identity.kind === "positive" && record.identity.id === "square-alternating" &&
      record.identity.size === 16 && record.identity.sigmaIndex === 0;
  });
  const values = records.map(function (record) { return record.volumeGrowthScreen.logLogSlopeDescriptor; });
  const expected = {
    count: values.length,
    mean: values.reduce(function (sum, value) { return sum + value; }, 0) / values.length,
    minimum: Math.min.apply(null, values),
    maximum: Math.max.apply(null, values)
  };
  assert.deepStrictEqual(positiveCell(fixture.summary, "square-alternating", 0).volumeSlopeDescriptor, expected);
  assert.deepStrictEqual(
    fixture.summary,
    Evaluator.summarizeRecords(fixture.records, fixture.rawBinding),
    "summary aggregation must replay deterministically"
  );

  const tampered = JSON.parse(JSON.stringify(fixture.summary));
  tampered.positiveCells.find(function (cell) {
    return cell.family === "square-alternating" && cell.size === 16 && cell.sigmaIndex === 0;
  }).volumeSlopeDescriptor.mean += 0.125;
  delete tampered.contentAddress;
  const canonical = Evaluator.canonicalStringify(tampered);
  tampered.contentAddress = {
    algorithm: "sha256",
    canonicalization: "RFC8785-compatible closed JSON subset",
    digest: Evaluator.sha256Bytes(Buffer.from(canonical, "utf8")),
    canonicalBytes: Buffer.byteLength(canonical, "utf8")
  };
  const report = Evaluator.validateSummary(tampered, fixture.records, fixture.rawBytes);
  assert.strictEqual(report.valid, false);
  assert.ok(report.errors.some(function (error) { return /full-payload rebuild/.test(error); }));
});

if (!process.exitCode) {
  process.stdout.write("Global Geometry II U2 screening adversarial: " + passed + "/" + passed + " tests passed.\n");
}
