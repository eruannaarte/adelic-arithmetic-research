#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const U2 = require("./global-geometry-ii-u2.js");

function valueAfter(argv, flag) {
  const index = argv.indexOf(flag); if (index < 0) return null;
  if (!argv[index + 1] || argv[index + 1].startsWith("--")) throw new Error(flag + " requires an explicit value");
  if (argv.filter(function (item) { return item === flag; }).length !== 1) throw new Error(flag + " may be supplied once");
  return argv[index + 1];
}
function parseArgs(argv) {
  const modes = ["--calibration", "--campaign", "--validate-calibration", "--validate-campaign"].filter(function (flag) { return argv.indexOf(flag) >= 0; });
  if (modes.length !== 1) throw new Error("select exactly one mode: --calibration, --campaign, --validate-calibration, or --validate-campaign");
  const mode = modes[0], allowed = [mode, "--output", "--source-commit", "--normalization", "--input"];
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i].startsWith("--") && allowed.indexOf(argv[i]) < 0) throw new Error("unknown argument " + argv[i]);
    if (!argv[i].startsWith("--") && i > 0 && !argv[i - 1].startsWith("--")) throw new Error("unexpected positional argument " + argv[i]);
  }
  const parsed = { mode: mode.slice(2), output: valueAfter(argv, "--output"), sourceCommit: valueAfter(argv, "--source-commit"), normalization: valueAfter(argv, "--normalization"), input: valueAfter(argv, "--input") };
  if ((mode === "--calibration" || mode === "--campaign") && (!parsed.output || !/^[0-9a-f]{40}$/.test(parsed.sourceCommit || ""))) throw new Error("production modes require --output and a 40-hex --source-commit");
  if (mode === "--campaign" && !parsed.normalization) throw new Error("--campaign requires --normalization");
  if ((mode === "--validate-calibration" || mode === "--validate-campaign") && !parsed.input) throw new Error("validation modes require --input");
  if (mode === "--validate-campaign" && !parsed.normalization) throw new Error("--validate-campaign requires --normalization");
  return parsed;
}
function writeArtifact(output, artifact) {
  const resolved = path.resolve(output), bytes = JSON.stringify(artifact, null, 2) + "\n";
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  const descriptor = fs.openSync(resolved, "wx", 0o644);
  try { fs.writeFileSync(descriptor, bytes, "utf8"); fs.fsyncSync(descriptor); }
  finally { fs.closeSync(descriptor); }
  return resolved;
}
function requireUnusedOutput(output) { if (fs.existsSync(path.resolve(output))) throw new Error("production output already exists; overwrite is forbidden"); }
function readJSON(input) { return JSON.parse(fs.readFileSync(path.resolve(input), "utf8")); }
function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.mode === "calibration") {
    requireUnusedOutput(args.output);
    const artifact = U2.calibrationRecord(U2.loadManifest(), args.sourceCommit), report = U2.validateCalibration(artifact);
    if (!report.valid) throw new Error("calibration failed validation: " + report.errors.join("; "));
    const output = writeArtifact(args.output, artifact);
    process.stdout.write(JSON.stringify({ mode: args.mode, output: output, digest: artifact.contentAddress.digest, cells: artifact.cells.length, records: artifact.cells.reduce(function (sum, cell) { return sum + cell.records.length; }, 0) }) + "\n");
    return;
  }
  if (args.mode === "campaign") {
    requireUnusedOutput(args.output);
    const normalization = readJSON(args.normalization), artifact = U2.buildCampaign(normalization, { finalSourceCommit: args.sourceCommit }), report = U2.validateCampaign(artifact, normalization);
    if (!report.valid) throw new Error("campaign failed validation: " + report.errors.join("; "));
    const output = writeArtifact(args.output, artifact);
    process.stdout.write(JSON.stringify({ mode: args.mode, output: output, digest: artifact.contentAddress.digest, positiveRuns: artifact.counts.actualPositiveRuns, controlRuns: artifact.counts.actualPrimaryControlRuns, conclusion: artifact.conclusion.status }) + "\n");
    return;
  }
  const artifact = readJSON(args.input), normalization = args.mode === "validate-campaign" ? readJSON(args.normalization) : null;
  const report = args.mode === "validate-calibration" ? U2.validateCalibration(artifact) : U2.validateCampaign(artifact, normalization);
  if (!report.valid) throw new Error(args.mode + " failed: " + report.errors.join("; "));
  process.stdout.write(JSON.stringify({ mode: args.mode, input: path.resolve(args.input), valid: true }) + "\n");
}

if (require.main === module) main();
module.exports = { parseArgs: parseArgs, writeArtifact: writeArtifact, requireUnusedOutput: requireUnusedOutput, readJSON: readJSON };
