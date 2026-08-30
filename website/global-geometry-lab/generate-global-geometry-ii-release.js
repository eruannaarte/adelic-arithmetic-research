#!/usr/bin/env node
"use strict";

/*
 * Deterministic release metadata for Global Geometry II.
 *
 * The manifest addresses source and scientific artifacts.  The release index
 * addresses the completed manifest, but the manifest never addresses the
 * index.  This one-way relationship deliberately avoids self-referential or
 * cyclic hashes.
 */

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const assert = require("assert");
const Atlas = require("./global-geometry-ii-atlas.js");
const CalibrationGenerator = require("./generate-global-geometry-ii-calibration.js");
const AtlasGenerator = require("./generate-global-geometry-ii-atlas.js");
const InverseGenerator = require("./generate-global-geometry-ii-inverse.js");
const SheetGenerator = require("./generate-global-geometry-ii-sheet.js");

const REPO_ROOT = path.resolve(__dirname, "../..");
const DEFAULT_MANIFEST = path.join(REPO_ROOT, "global_geometry_ii_reproducibility_manifest.json");
const DEFAULT_INDEX = path.join(REPO_ROOT, "artifacts/global-geometry-ii/release-index-v1.json");
const RELEASE_ID = "global-geometry-ii-alpha-reproduction-v1";
const MANIFEST_SCHEMA = "ggii.reproducibility-manifest/1";
const INDEX_SCHEMA = "ggii.release-index/1";
const ADDRESS_CANONICALIZATION = "ggii-release-json-v1";
const FABRICATION_ROOT = path.join(REPO_ROOT, "artifacts/global-geometry-ii/fabrication");
const FABRICATION_MANIFEST_PATH = "artifacts/global-geometry-ii/fabrication/fabrication-manifest.json";
const EXTERNAL_COMPARISON_RECORD = "artifacts/global-geometry-ii/certificates/macos-windows-comparison-v1.json";
const ATLAS_ABSOLUTE_TOLERANCE = 1e-12;
const ATLAS_RELATIVE_TOLERANCE = 1e-12;
const ATLAS_DERIVED_DIGEST_PATHS = Object.freeze([
  "root.pilot.evidence.artifacts[0]",
  "root.pilot.evidence.artifacts[1]",
  "root.pilot.evidence.digest",
  "root.pilot.evidence.id",
  "root.pilot.evidence.result.resultDigest",
  "root.pilot.manifest.digest",
  "root.pilot.manifest.resultArtifacts[0]",
  "root.pilot.resultDigest"
]);
const ATLAS_EXACT_INTEGER_PATH_PATTERNS = Object.freeze([
  "root.pilot.cells[*].duplicateRealizationCount",
  "root.pilot.cells[*].familyIndex",
  "root.pilot.cells[*].identity.familyIndex",
  "root.pilot.cells[*].identity.linearSize",
  "root.pilot.cells[*].identity.sigmaIndex",
  "root.pilot.cells[*].identity.sizeIndex",
  "root.pilot.cells[*].linearSize",
  "root.pilot.cells[*].replicateCount",
  "root.pilot.cells[*].requiredReplicateCount",
  "root.pilot.cells[*].sigmaIndex",
  "root.pilot.cells[*].sizeIndex",
  "root.pilot.cells[*].uniqueRealizationCount",
  "root.pilot.evidence.result.cellCount",
  "root.pilot.evidence.result.runCount",
  "root.pilot.evidence.result.uniqueRealizationCount",
  "root.pilot.evidence.schemaVersion",
  "root.pilot.manifest.parameters.maximumSynchronousRuns",
  "root.pilot.manifest.parameters.replicates",
  "root.pilot.manifest.parameters.transportPolicy.maxIterations",
  "root.pilot.manifest.refinements[*]",
  "root.pilot.manifest.schemaVersion",
  "root.pilot.runs[*].complexSummary.edges",
  "root.pilot.runs[*].complexSummary.faces",
  "root.pilot.runs[*].complexSummary.vertices",
  "root.pilot.runs[*].familyIndex",
  "root.pilot.runs[*].identity.familyIndex",
  "root.pilot.runs[*].identity.linearSize",
  "root.pilot.runs[*].identity.replicate",
  "root.pilot.runs[*].identity.sigmaIndex",
  "root.pilot.runs[*].identity.sizeIndex",
  "root.pilot.runs[*].linearSize",
  "root.pilot.runs[*].measurements.dimensions.volumeProfile[*].maxVolume",
  "root.pilot.runs[*].measurements.dimensions.volumeProfile[*].minVolume",
  "root.pilot.runs[*].measurements.dimensions.walkProfile[*].scale",
  "root.pilot.runs[*].measurements.dimensions.walkProfile[*].step",
  "root.pilot.runs[*].measurements.exact.betti[*]",
  "root.pilot.runs[*].measurements.exact.boundaryComponents",
  "root.pilot.runs[*].measurements.exact.eulerCharacteristic",
  "root.pilot.runs[*].measurements.exact.eulerPoincareResidual",
  "root.pilot.runs[*].measurements.oneEdgeSensitivity.edgeIndex",
  "root.pilot.runs[*].measurements.oneEdgeSensitivity.perturbedTransport.iterations",
  "root.pilot.runs[*].measurements.oneEdgeSensitivity.perturbedTransport.leftBoundaryCount",
  "root.pilot.runs[*].measurements.oneEdgeSensitivity.perturbedTransport.maxIterations",
  "root.pilot.runs[*].measurements.oneEdgeSensitivity.perturbedTransport.rightBoundaryCount",
  "root.pilot.runs[*].measurements.spectrum.solver.sweeps",
  "root.pilot.runs[*].measurements.spectrum.zeroMultiplicity",
  "root.pilot.runs[*].measurements.transport.iterations",
  "root.pilot.runs[*].measurements.transport.leftBoundaryCount",
  "root.pilot.runs[*].measurements.transport.maxIterations",
  "root.pilot.runs[*].measurements.transport.rightBoundaryCount",
  "root.pilot.runs[*].replicate",
  "root.pilot.runs[*].sigmaIndex",
  "root.pilot.runs[*].sizeIndex",
  "root.pilot.spec.replicates",
  "root.pilot.spec.sizes[*]"
]);

const SUITES = Object.freeze([
  { id: "global-geometry-i-core", path: "website/global-geometry-lab/test-global-geometry-core.js" },
  { id: "global-geometry-ii-core", path: "website/global-geometry-lab/test-global-geometry-ii-core.js" },
  { id: "global-geometry-ii-ensembles", path: "website/global-geometry-lab/test-global-geometry-ii-ensembles.js" },
  { id: "global-geometry-ii-atlas", path: "website/global-geometry-lab/test-global-geometry-ii-atlas.js" },
  { id: "global-geometry-ii-inverse", path: "website/global-geometry-lab/test-global-geometry-ii-inverse.js" },
  { id: "global-geometry-ii-sheet", path: "website/global-geometry-lab/test-global-geometry-ii-sheet.js" },
  { id: "global-geometry-ii-artifacts", path: "website/global-geometry-lab/test-global-geometry-ii-artifacts.js" },
  { id: "global-geometry-ii-fabrication-vectors", path: "artifacts/global-geometry-ii/fabrication/validate-fabrication.js" },
  { id: "global-geometry-ii-reproduction", path: "website/global-geometry-lab/test-global-geometry-ii-reproduction.js" }
]);

const ARTIFACT_DEFINITIONS = Object.freeze([
  {
    id: "calibration-v1",
    path: "artifacts/global-geometry-ii/calibration-v1.json",
    generator: CalibrationGenerator,
    replayPolicy: Object.freeze({ id: "exact-canonical-payload/1" }),
    semanticValidator(payload) {
      return canonicalStringify(payload) === canonicalStringify(CalibrationGenerator.buildPayload())
        ? { valid: true, errors: [] }
        : { valid: false, errors: ["calibration payload does not replay"] };
    }
  },
  {
    id: "atlas-pilot-v1",
    path: "artifacts/global-geometry-ii/atlas-pilot-v1.json",
    generator: AtlasGenerator,
    replayPolicy: Object.freeze({
      id: "ggii.atlas-cross-platform-replay/1",
      continuousTolerance: Object.freeze({
        absolute: ATLAS_ABSOLUTE_TOLERANCE,
        relative: ATLAS_RELATIVE_TOLERANCE,
        formula: "|a-b| <= 1e-12 + 1e-12*max(1,|a|,|b|)"
      }),
      declaredIntegerPaths: ATLAS_EXACT_INTEGER_PATH_PATTERNS,
      continuousNumbers: "frozen tolerance, including integer-valued endpoints and residual zeros",
      structuralAndOtherScalars: "exact",
      derivedFieldsComparedInternallyOnly: ATLAS_DERIVED_DIGEST_PATHS
    }),
    semanticValidator(payload) {
      return compareAtlasCrossPlatformReplay(payload, AtlasGenerator.buildPayload());
    }
  },
  {
    id: "inverse-certificates-v1",
    path: "artifacts/global-geometry-ii/inverse-certificates-v1.json",
    generator: InverseGenerator,
    replayPolicy: Object.freeze({ id: "exact-canonical-payload/1" }),
    semanticValidator(payload) {
      const report = InverseGenerator.validatePayload(payload);
      if (!report.valid) return report;
      return canonicalStringify(payload) === canonicalStringify(InverseGenerator.buildPayload())
        ? { valid: true, errors: [] }
        : { valid: false, errors: ["inverse payload does not replay"] };
    }
  },
  {
    id: "sheet-hil-v1",
    path: "artifacts/global-geometry-ii/sheet-hil-v1.json",
    generator: SheetGenerator,
    replayPolicy: Object.freeze({ id: "exact-canonical-payload/1" }),
    semanticValidator(payload) {
      const report = SheetGenerator.validatePayload(payload);
      if (!report.valid) return report;
      return canonicalStringify(payload) === canonicalStringify(SheetGenerator.buildPayload())
        ? { valid: true, errors: [] }
        : { valid: false, errors: ["sheet payload does not replay"] };
    }
  }
]);

function isPlainJsonObject(value) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

function canonicalStringify(value) {
  const seen = new Set();
  function encode(item, location, depth) {
    if (depth > 128) throw new Error(location + " exceeds canonicalization depth");
    if (item === null || typeof item === "boolean" || typeof item === "string") return JSON.stringify(item);
    if (typeof item === "number") {
      if (!Number.isFinite(item)) throw new Error(location + " contains a non-finite number");
      return JSON.stringify(Object.is(item, -0) ? 0 : item);
    }
    if (typeof item !== "object") throw new Error(location + " is not JSON data");
    if (seen.has(item)) throw new Error(location + " contains a cycle");
    seen.add(item);
    let encoded;
    if (Array.isArray(item)) {
      for (let index = 0; index < item.length; index += 1) {
        if (!Object.prototype.hasOwnProperty.call(item, index)) throw new Error(location + " must be a dense array");
      }
      if (Object.keys(item).length !== item.length) throw new Error(location + " has non-index array properties");
      encoded = "[" + item.map((entry, index) => encode(entry, location + "[" + index + "]", depth + 1)).join(",") + "]";
    } else {
      if (!isPlainJsonObject(item)) throw new Error(location + " must be a plain object");
      const descriptors = Object.getOwnPropertyDescriptors(item);
      const keys = Object.keys(descriptors).sort();
      encoded = "{" + keys.map((key) => {
        const descriptor = descriptors[key];
        if (!("value" in descriptor) || !descriptor.enumerable) throw new Error(location + "." + key + " is not plain JSON data");
        if (key === "__proto__" || key === "prototype" || key === "constructor") throw new Error(location + " contains a forbidden key");
        return JSON.stringify(key) + ":" + encode(descriptor.value, location + "." + key, depth + 1);
      }).join(",") + "}";
    }
    seen.delete(item);
    return encoded;
  }
  return encode(value, "root", 0);
}

function atlasChildPath(parent, key, arrayIndex) {
  if (arrayIndex) return parent + "[" + key + "]";
  return /^[A-Za-z_$][A-Za-z0-9_$]*$/.test(key)
    ? parent + "." + key
    : parent + "[" + JSON.stringify(key) + "]";
}

function atlasNumericPathPattern(location) {
  return location.replace(/\[\d+\]/g, "[*]");
}

function compareAtlasCrossPlatformReplay(committedPayload, replayPayload) {
  const ignored = new Set(ATLAS_DERIVED_DIGEST_PATHS);
  const exactIntegerPatterns = new Set(ATLAS_EXACT_INTEGER_PATH_PATTERNS);
  const ignoredSeen = new Set();
  const errors = [];
  const MAX_REPORTED_ERRORS = 128;
  const summary = {
    nodesCompared: 0,
    objectsCompared: 0,
    arraysCompared: 0,
    exactScalarsCompared: 0,
    exactIntegerNumbersCompared: 0,
    continuousNumbersCompared: 0,
    continuousDifferences: 0,
    toleratedContinuousDifferences: 0,
    derivedStringsComparedInternallyOnly: 0,
    derivedStringDifferences: 0,
    mismatchCount: 0,
    maxAbsoluteDifference: { value: 0, path: null, committed: null, replay: null },
    maxScaledRelativeDifference: { value: 0, path: null },
    maxToleranceFraction: { value: 0, path: null }
  };

  function mismatch(message) {
    summary.mismatchCount += 1;
    if (errors.length < MAX_REPORTED_ERRORS) errors.push(message);
  }

  function validatePilot(payload, label) {
    if (!isPlainJsonObject(payload) || !Object.prototype.hasOwnProperty.call(payload, "pilot")) {
      const message = label + " payload is missing a pilot object";
      mismatch(message);
      return { valid: false, errorCount: 1, errors: [message] };
    }
    let report;
    try { report = Atlas.validatePilotResult(payload.pilot); }
    catch (error) { report = { valid: false, errors: ["validator threw: " + error.message] }; }
    if (!report || report.valid !== true) {
      const pilotErrors = report && Array.isArray(report.errors) ? report.errors : ["validator returned no closed report"];
      mismatch(label + " pilot failed Atlas.validatePilotResult: " + pilotErrors.slice(0, 8).join("; "));
      return { valid: false, errorCount: pilotErrors.length, errors: pilotErrors.slice(0, 16) };
    }
    return { valid: true, errorCount: 0, errors: [] };
  }

  const pilotValidation = {
    committed: validatePilot(committedPayload, "committed"),
    replay: validatePilot(replayPayload, "replay")
  };

  const committedActive = new Set();
  const replayActive = new Set();
  function walk(committed, replay, location, depth) {
    summary.nodesCompared += 1;
    if (summary.nodesCompared > 1000000) {
      mismatch("atlas replay comparison exceeds the one-million-node bound");
      return;
    }
    if (depth > 256) {
      mismatch(location + " exceeds the atlas replay depth bound");
      return;
    }

    if (ignored.has(location)) {
      ignoredSeen.add(location);
      if (typeof committed !== "string" || typeof replay !== "string") {
        mismatch(location + " is a derived atlas field and must exist as a string on both sides");
        return;
      }
      summary.derivedStringsComparedInternallyOnly += 1;
      if (committed !== replay) summary.derivedStringDifferences += 1;
      return;
    }

    const committedIsNull = committed === null;
    const replayIsNull = replay === null;
    if (committedIsNull || replayIsNull) {
      if (!(committedIsNull && replayIsNull)) mismatch(location + " null/type mismatch");
      else summary.exactScalarsCompared += 1;
      return;
    }

    const committedType = typeof committed;
    const replayType = typeof replay;
    if (committedType !== replayType) {
      mismatch(location + " type mismatch: committed " + committedType + ", replay " + replayType);
      return;
    }

    if (committedType === "number") {
      if (!Number.isFinite(committed) || !Number.isFinite(replay)) {
        mismatch(location + " contains a non-finite number");
        return;
      }
      const numericPattern = atlasNumericPathPattern(location);
      if (exactIntegerPatterns.has(numericPattern)) {
        summary.exactIntegerNumbersCompared += 1;
        if (!Number.isSafeInteger(committed) || !Number.isSafeInteger(replay)) {
          mismatch(location + " is a declared exact-integer field and must be a safe integer on both sides");
        } else if (committed !== replay) {
          mismatch(location + " exact integer mismatch: " + committed + " !== " + replay);
        }
        return;
      }
      summary.continuousNumbersCompared += 1;
      const absoluteDifference = Math.abs(committed - replay);
      const scale = Math.max(1, Math.abs(committed), Math.abs(replay));
      const scaledRelativeDifference = absoluteDifference / scale;
      const tolerance = ATLAS_ABSOLUTE_TOLERANCE + ATLAS_RELATIVE_TOLERANCE * scale;
      const toleranceFraction = absoluteDifference / tolerance;
      if (absoluteDifference > summary.maxAbsoluteDifference.value) {
        summary.maxAbsoluteDifference = { value: absoluteDifference, path: location, committed, replay };
      }
      if (scaledRelativeDifference > summary.maxScaledRelativeDifference.value) {
        summary.maxScaledRelativeDifference = { value: scaledRelativeDifference, path: location };
      }
      if (toleranceFraction > summary.maxToleranceFraction.value) {
        summary.maxToleranceFraction = { value: toleranceFraction, path: location };
      }
      if (absoluteDifference > 0) {
        summary.continuousDifferences += 1;
        if (absoluteDifference <= tolerance) summary.toleratedContinuousDifferences += 1;
        else mismatch(location + " continuous-number difference " + absoluteDifference + " exceeds tolerance " + tolerance);
      }
      return;
    }

    if (committedType === "string" || committedType === "boolean") {
      summary.exactScalarsCompared += 1;
      if (committed !== replay) mismatch(location + " exact " + committedType + " mismatch");
      return;
    }

    if (committedType !== "object") {
      mismatch(location + " contains unsupported type " + committedType);
      return;
    }

    const committedArray = Array.isArray(committed);
    const replayArray = Array.isArray(replay);
    if (committedArray !== replayArray) {
      mismatch(location + " array/object kind mismatch");
      return;
    }
    if (committedActive.has(committed) || replayActive.has(replay)) {
      mismatch(location + " contains a cycle");
      return;
    }
    committedActive.add(committed);
    replayActive.add(replay);

    if (committedArray) {
      summary.arraysCompared += 1;
      if (Object.getOwnPropertySymbols(committed).length || Object.getOwnPropertySymbols(replay).length) {
        mismatch(location + " arrays may not contain symbol keys");
      }
      const committedKeys = Object.keys(committed);
      const replayKeys = Object.keys(replay);
      const committedDense = committedKeys.length === committed.length && committedKeys.every((key, index) => key === String(index));
      const replayDense = replayKeys.length === replay.length && replayKeys.every((key, index) => key === String(index));
      if (!committedDense || !replayDense) mismatch(location + " arrays must be dense and index-only");
      if (committed.length !== replay.length) mismatch(location + " array length mismatch: " + committed.length + " !== " + replay.length);
      const commonLength = Math.min(committed.length, replay.length);
      for (let index = 0; index < commonLength; index += 1) {
        walk(committed[index], replay[index], atlasChildPath(location, index, true), depth + 1);
      }
    } else {
      summary.objectsCompared += 1;
      if (!isPlainJsonObject(committed) || !isPlainJsonObject(replay)) {
        mismatch(location + " objects must be plain JSON objects");
      } else {
        if (Object.getOwnPropertySymbols(committed).length || Object.getOwnPropertySymbols(replay).length) {
          mismatch(location + " objects may not contain symbol keys");
        }
        const committedDescriptors = Object.getOwnPropertyDescriptors(committed);
        const replayDescriptors = Object.getOwnPropertyDescriptors(replay);
        const committedKeys = Object.keys(committedDescriptors).sort();
        const replayKeys = Object.keys(replayDescriptors).sort();
        if (canonicalStringify(committedKeys) !== canonicalStringify(replayKeys)) {
          mismatch(location + " object key mismatch: committed [" + committedKeys.join(",") + "], replay [" + replayKeys.join(",") + "]");
        }
        const commonKeys = committedKeys.filter((key) => Object.prototype.hasOwnProperty.call(replayDescriptors, key));
        commonKeys.forEach((key) => {
          const leftDescriptor = committedDescriptors[key];
          const rightDescriptor = replayDescriptors[key];
          if (!("value" in leftDescriptor) || !("value" in rightDescriptor) || !leftDescriptor.enumerable || !rightDescriptor.enumerable) {
            mismatch(atlasChildPath(location, key, false) + " must be enumerable data on both sides");
            return;
          }
          walk(leftDescriptor.value, rightDescriptor.value, atlasChildPath(location, key, false), depth + 1);
        });
      }
    }
    committedActive.delete(committed);
    replayActive.delete(replay);
  }

  walk(committedPayload, replayPayload, "root", 0);
  ATLAS_DERIVED_DIGEST_PATHS.forEach((location) => {
    if (!ignoredSeen.has(location)) mismatch(location + " required derived atlas string path is missing");
  });

  return {
    valid: errors.length === 0 && summary.mismatchCount === 0 && pilotValidation.committed.valid && pilotValidation.replay.valid,
    errors,
    policy: {
      id: "ggii.atlas-cross-platform-replay/1",
      continuousTolerance: {
        absolute: ATLAS_ABSOLUTE_TOLERANCE,
        relative: ATLAS_RELATIVE_TOLERANCE,
        formula: "|a-b| <= 1e-12 + 1e-12*max(1,|a|,|b|)"
      },
      declaredIntegerPaths: ATLAS_EXACT_INTEGER_PATH_PATTERNS.slice(),
      continuousNumbers: "frozen tolerance, including integer-valued endpoints and residual zeros",
      structuralAndOtherScalars: "exact"
    },
    pilotValidation,
    derivedFieldsComparedInternallyOnly: ATLAS_DERIVED_DIGEST_PATHS.slice(),
    summary
  };
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

function repoRelative(absolutePath) {
  const relative = path.relative(REPO_ROOT, absolutePath);
  if (!relative || relative === ".." || relative.startsWith(".." + path.sep) || path.isAbsolute(relative)) {
    throw new Error("path is outside the repository: " + absolutePath);
  }
  return relative.split(path.sep).join("/");
}

function resolveFromRepo(input) {
  if (typeof input !== "string" || !input.trim()) throw new Error("output path must be a non-empty string");
  const resolved = path.isAbsolute(input) ? path.normalize(input) : path.resolve(REPO_ROOT, input);
  repoRelative(resolved);
  return resolved;
}

function parseOutputs(argv) {
  if (!Array.isArray(argv)) throw new Error("argv must be an array");
  if (argv.length === 0) return { manifest: DEFAULT_MANIFEST, index: DEFAULT_INDEX };
  if (argv.length !== 4) throw new Error("use either no arguments or exactly --manifest PATH --index PATH");
  const allowed = new Set(["--manifest", "--index"]);
  const values = {};
  for (let index = 0; index < argv.length; index += 2) {
    const flag = argv[index];
    const value = argv[index + 1];
    if (!allowed.has(flag)) throw new Error("unknown release generator argument " + flag);
    if (Object.prototype.hasOwnProperty.call(values, flag)) throw new Error(flag + " may be supplied only once");
    if (typeof value !== "string" || !value || value.startsWith("--")) throw new Error(flag + " requires an explicit file path");
    values[flag] = resolveFromRepo(value);
  }
  if (!values["--manifest"] || !values["--index"]) throw new Error("--manifest and --index must be supplied together");
  if (values["--manifest"] === values["--index"]) throw new Error("manifest and index outputs must be different files");
  return { manifest: values["--manifest"], index: values["--index"] };
}

function assertPortableSourceEntryName(name, absolutePath) {
  if (typeof name !== "string" || typeof absolutePath !== "string") throw new Error("source entry name/path must be strings");
  if (name.startsWith("._")) {
    throw new Error("refusing AppleDouble/platform-metadata source entry: " + absolutePath);
  }
}

function listFilesRecursively(directory, extensionPattern) {
  extensionPattern = extensionPattern || /\.(?:js|html|css|md|ps1)$/i;
  const entries = [];
  fs.readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0).forEach((entry) => {
    const absolute = path.join(directory, entry.name);
    assertPortableSourceEntryName(entry.name, absolute);
    if (entry.isSymbolicLink()) throw new Error("source selection refuses symbolic link " + repoRelative(absolute));
    if (entry.isDirectory()) entries.push(...listFilesRecursively(absolute, extensionPattern));
    else if (entry.isFile() && extensionPattern.test(entry.name)) entries.push(absolute);
  });
  return entries;
}

function collectSourcePaths() {
  const labFiles = listFilesRecursively(__dirname);
  const fabricationFiles = fs.existsSync(FABRICATION_ROOT)
    ? listFilesRecursively(FABRICATION_ROOT, /\.(?:js|json|svg)$/i)
    : [];
  const rootFiles = fs.readdirSync(REPO_ROOT, { withFileTypes: true })
    .filter((entry) => entry.isFile() && (/^GLOBAL_GEOMETRY_II_.*\.md$/.test(entry.name) || entry.name === "GLOBAL_GEOMETRY_LAB.md"))
    .map((entry) => path.join(REPO_ROOT, entry.name));
  const workflow = path.join(REPO_ROOT, ".github/workflows/tests.yml");
  const explicitFiles = fs.existsSync(workflow) ? [workflow] : [];
  return Array.from(new Set(labFiles.concat(fabricationFiles, rootFiles, explicitFiles).map(repoRelative))).sort();
}

function sourceEntries() {
  return collectSourcePaths().map((relativePath) => {
    const stats = sha256File(path.join(REPO_ROOT, relativePath));
    return { path: relativePath, sha256: stats.sha256, bytes: stats.bytes };
  });
}

function equalAddress(left, right) {
  return canonicalStringify(left) === canonicalStringify(right);
}

function verifyArtifactDefinition(definition) {
  const absolute = path.join(REPO_ROOT, definition.path);
  const raw = fs.readFileSync(absolute);
  const artifact = JSON.parse(raw.toString("utf8"));
  if (!isPlainJsonObject(artifact)) throw new Error(definition.id + " artifact must be a JSON object");
  const suppliedAddress = artifact.contentAddress;
  const payload = Object.assign({}, artifact);
  delete payload.contentAddress;
  const computedAddress = definition.generator.contentAddress(payload);
  if (!suppliedAddress || !equalAddress(suppliedAddress, computedAddress)) {
    throw new Error(definition.id + " content address does not verify");
  }
  const semantic = definition.semanticValidator(payload);
  if (!semantic || semantic.valid !== true) {
    throw new Error(definition.id + " semantic replay failed: " + ((semantic && semantic.errors) || []).join("; "));
  }
  return {
    id: definition.id,
    path: definition.path,
    schema: payload.schema,
    rawSha256: sha256Bytes(raw),
    rawBytes: raw.length,
    semanticAddress: computedAddress,
    semanticReplay: "PASS",
    replayPolicy: definition.replayPolicy
  };
}

function scientificArtifactEntries() {
  return ARTIFACT_DEFINITIONS.map(verifyArtifactDefinition);
}

function verifyFabricationPackage() {
  const absoluteManifest = path.join(REPO_ROOT, FABRICATION_MANIFEST_PATH);
  const raw = fs.readFileSync(absoluteManifest);
  const manifest = JSON.parse(raw.toString("utf8"));
  if (!isPlainJsonObject(manifest) || manifest.schemaVersion !== 1) throw new Error("fabrication manifest schemaVersion must be 1");
  if (manifest.releaseStatus !== "DIGITAL_FABRICATION_PACKAGE_ONLY" || manifest.physicalValidation !== "NOT_RUN") {
    throw new Error("fabrication package must remain digitally scoped and physically unvalidated");
  }
  if (manifest.hardwareAuthorization !== false || manifest.purchaseAuthorization !== false) {
    throw new Error("fabrication package may not grant hardware or purchase authorization");
  }
  if (!Array.isArray(manifest.artifacts) || manifest.artifacts.length !== 5) {
    throw new Error("fabrication package must address exactly its protocol, three SVGs, and validator");
  }
  const expectedPaths = [
    "GLOBAL_GEOMETRY_II_SHEET_EXPERIMENT.md",
    "artifacts/global-geometry-ii/fabrication/q5-star-template.svg",
    "artifacts/global-geometry-ii/fabrication/q6-star-template.svg",
    "artifacts/global-geometry-ii/fabrication/q7-star-template.svg",
    "artifacts/global-geometry-ii/fabrication/validate-fabrication.js"
  ];
  if (canonicalStringify(manifest.artifacts.map((entry) => entry.path)) !== canonicalStringify(expectedPaths)) {
    throw new Error("fabrication manifest artifact order/set is not canonical");
  }
  const files = manifest.artifacts.map((entry) => {
    if (!isPlainJsonObject(entry) || typeof entry.role !== "string" || !entry.role) throw new Error("fabrication manifest entry is malformed");
    if (entry.path === FABRICATION_MANIFEST_PATH) throw new Error("fabrication manifest may not hash itself");
    const digest = sha256File(path.join(REPO_ROOT, entry.path));
    if (entry.sha256 !== digest.sha256) throw new Error("fabrication resource hash mismatch: " + entry.path);
    return { path: entry.path, role: entry.role, sha256: digest.sha256, bytes: digest.bytes };
  });
  if (!Array.isArray(manifest.validationCommands) || !manifest.validationCommands.includes("node artifacts/global-geometry-ii/fabrication/validate-fabrication.js")) {
    throw new Error("fabrication package omits its dependency-free validation command");
  }
  return {
    id: "programmable-sheet-fabrication-package-v1",
    manifestPath: FABRICATION_MANIFEST_PATH,
    schemaVersion: manifest.schemaVersion,
    rawSha256: sha256Bytes(raw),
    rawBytes: raw.length,
    semanticAddress: contentAddress(manifest),
    files,
    validation: "INTERNAL_HASHES_PASS",
    physicalValidation: "NOT_RUN",
    hardwareAuthorization: false,
    purchaseAuthorization: false
  };
}

function reproductionResourceEntries() {
  return [verifyFabricationPackage()];
}

function buildManifestPayload() {
  const sources = sourceEntries();
  const selected = new Set(sources.map((entry) => entry.path));
  SUITES.forEach((suite) => {
    if (!selected.has(suite.path)) throw new Error("suite source is absent from source manifest: " + suite.path);
  });
  return {
    schema: MANIFEST_SCHEMA,
    releaseId: RELEASE_ID,
    purpose: "Clean-room, dependency-free replay metadata for the bounded Global Geometry I/II research release.",
    deterministicMetadata: "No generation timestamp, hostname, checkout path, or git state is included in this addressable payload.",
    execution: {
      entrypoint: "website/global-geometry-lab/reproduce-global-geometry-ii.js",
      command: "node website/global-geometry-lab/reproduce-global-geometry-ii.js --verify",
      powershellWrapper: "website/global-geometry-lab/reproduce-global-geometry-ii.ps1",
      network: "not used",
      packageInstallation: "not used",
      runtimeDependency: "Node.js standard library only",
      runtimePolicy: "Node.js 22.x is the declared alpha baseline; every local certificate records the actual runtime. Exact payload replay is required except for the atlas policy frozen in scientificArtifacts[].replayPolicy.",
      pathPolicy: "All repository inputs are resolved from the verifier location rather than the caller's working directory.",
      suites: SUITES.map((suite) => ({ id: suite.id, path: suite.path }))
    },
    sourceManifest: {
      selection: "All js/html/css/md/ps1 files below website/global-geometry-lab; fabrication js/json/svg resources; .github/workflows/tests.yml; plus GLOBAL_GEOMETRY_LAB.md and GLOBAL_GEOMETRY_II_*.md at repository root.",
      count: sources.length,
      entries: sources
    },
    scientificArtifacts: scientificArtifactEntries(),
    reproductionResources: reproductionResourceEntries(),
    certificationPolicy: {
      localVerificationMeaning: "A PASS certifies only this invocation, environment, source snapshot, artifact replay, and focused test outcomes.",
      crossPlatformEqualityClaim: "NOT_MADE",
      requiredIndependentPlatforms: ["darwin", "win32"],
      requiredIndependentCertificates: 2,
      windowsCertificate: "REQUIRED_EXTERNAL_INPUT_NOT_BUNDLED_OR_SIMULATED",
      externalComparisonRecord: EXTERNAL_COMPARISON_RECORD,
      releaseGate: "STATUS_DELEGATED_TO_EXTERNAL_COMPARISON_RECORD"
    },
    approvalGates: {
      publication: "requires explicit user approval",
      merge: "requires explicit user approval",
      hardwarePurchaseOrFabrication: "requires explicit user approval"
    },
    exclusions: [
      "No certificate is bundled in the deterministic release manifest.",
      "No passing local run proves numerical equality with a different operating system or machine.",
      "No network service, package manager, browser session, camera, actuator, or physical sheet is exercised."
    ]
  };
}

function buildIndexPayload(manifestPath, manifestArtifact) {
  const relativeManifest = repoRelative(manifestPath);
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
    scientificArtifacts: manifestArtifact.scientificArtifacts.map((entry) => ({
      id: entry.id,
      path: entry.path,
      schema: entry.schema,
      rawSha256: entry.rawSha256,
      semanticAddress: entry.semanticAddress
    })),
    reproductionResources: manifestArtifact.reproductionResources.map((entry) => ({
      id: entry.id,
      manifestPath: entry.manifestPath,
      rawSha256: entry.rawSha256,
      semanticAddress: entry.semanticAddress,
      physicalValidation: entry.physicalValidation
    })),
    hashTopology: "Scientific artifacts -> manifest -> release index. No file hashes itself and the manifest does not hash the index.",
    certificationStatus: {
      crossPlatformEqualityClaim: "NOT_MADE",
      windowsCertificate: "EXTERNAL_NOT_BUNDLED_IN_INDEX",
      externalComparisonRecord: EXTERNAL_COMPARISON_RECORD,
      releaseGate: "STATUS_DELEGATED_TO_EXTERNAL_COMPARISON_RECORD"
    }
  };
}

function packageAddressed(payload) {
  return Object.assign({}, payload, { contentAddress: contentAddress(payload) });
}

function writeJson(output, value) {
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, JSON.stringify(value, null, 2) + "\n", "utf8");
}

function verifyAddressedFile(filePath, expectedSchema) {
  const artifact = JSON.parse(fs.readFileSync(filePath, "utf8"));
  if (!artifact || artifact.schema !== expectedSchema) throw new Error("unexpected schema in " + filePath);
  const supplied = artifact.contentAddress;
  const payload = Object.assign({}, artifact);
  delete payload.contentAddress;
  const computed = contentAddress(payload);
  if (!supplied || !equalAddress(supplied, computed)) throw new Error("content address failed for " + filePath);
  return { artifact, payload, address: computed };
}

function generate(outputs) {
  outputs = outputs || { manifest: DEFAULT_MANIFEST, index: DEFAULT_INDEX };
  [outputs.manifest, outputs.index].forEach((output) => repoRelative(path.resolve(output)));
  if (path.resolve(outputs.manifest) === path.resolve(outputs.index)) {
    throw new Error("manifest and index outputs must be different files");
  }
  const protectedInputs = new Set(collectSourcePaths()
    .concat(ARTIFACT_DEFINITIONS.map((definition) => definition.path))
    .map((relative) => path.resolve(REPO_ROOT, relative)));
  [outputs.manifest, outputs.index].forEach((output) => {
    const resolved = path.resolve(output);
    if (protectedInputs.has(resolved)) throw new Error("release output may not overwrite an input: " + repoRelative(resolved));
    const isDefault = resolved === DEFAULT_MANIFEST || resolved === DEFAULT_INDEX;
    if (!isDefault && fs.existsSync(resolved)) throw new Error("explicit release output already exists: " + repoRelative(resolved));
  });
  const manifestPayload = buildManifestPayload();
  const manifestArtifact = packageAddressed(manifestPayload);
  writeJson(outputs.manifest, manifestArtifact);
  const manifestReplay = verifyAddressedFile(outputs.manifest, MANIFEST_SCHEMA);
  assert.strictEqual(canonicalStringify(manifestReplay.payload), canonicalStringify(manifestPayload));

  const indexPayload = buildIndexPayload(outputs.manifest, manifestArtifact);
  const indexArtifact = packageAddressed(indexPayload);
  writeJson(outputs.index, indexArtifact);
  const indexReplay = verifyAddressedFile(outputs.index, INDEX_SCHEMA);
  assert.strictEqual(canonicalStringify(indexReplay.payload), canonicalStringify(indexPayload));
  if (!equalAddress(indexReplay.payload.manifest.contentAddress, manifestReplay.address)) {
    throw new Error("release index does not point to the generated manifest address");
  }
  return {
    manifest: { path: outputs.manifest, address: manifestReplay.address },
    index: { path: outputs.index, address: indexReplay.address }
  };
}

function generatorCliSummary(result) {
  return {
    manifest: { output: result.manifest.path, sha256: result.manifest.address.digest },
    index: { output: result.index.path, sha256: result.index.address.digest },
    crossPlatformEqualityClaim: "NOT_MADE",
    windowsCertificate: "REQUIRED_EXTERNAL_INPUT_NOT_BUNDLED_OR_SIMULATED",
    externalComparisonRecord: EXTERNAL_COMPARISON_RECORD,
    releaseGate: "STATUS_DELEGATED_TO_EXTERNAL_COMPARISON_RECORD"
  };
}

function main() {
  const outputs = parseOutputs(process.argv.slice(2));
  const result = generate(outputs);
  process.stdout.write(JSON.stringify(generatorCliSummary(result)) + "\n");
}

if (require.main === module) main();

module.exports = {
  ADDRESS_CANONICALIZATION,
  ARTIFACT_DEFINITIONS,
  ATLAS_ABSOLUTE_TOLERANCE,
  ATLAS_DERIVED_DIGEST_PATHS,
  ATLAS_EXACT_INTEGER_PATH_PATTERNS,
  ATLAS_RELATIVE_TOLERANCE,
  DEFAULT_INDEX,
  DEFAULT_MANIFEST,
  EXTERNAL_COMPARISON_RECORD,
  INDEX_SCHEMA,
  MANIFEST_SCHEMA,
  RELEASE_ID,
  REPO_ROOT,
  SUITES,
  assertPortableSourceEntryName,
  buildIndexPayload,
  buildManifestPayload,
  canonicalStringify,
  collectSourcePaths,
  compareAtlasCrossPlatformReplay,
  contentAddress,
  generate,
  generatorCliSummary,
  packageAddressed,
  parseOutputs,
  repoRelative,
  reproductionResourceEntries,
  scientificArtifactEntries,
  sha256Bytes,
  sha256File,
  sourceEntries,
  verifyAddressedFile,
  verifyArtifactDefinition,
  verifyFabricationPackage
};
