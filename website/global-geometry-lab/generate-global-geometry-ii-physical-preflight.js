#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const Sheet = require("./global-geometry-ii-sheet.js");

const REPO_ROOT = path.resolve(__dirname, "../..");
const FABRICATION_ROOT = path.join(REPO_ROOT, "artifacts/global-geometry-ii/fabrication");
const PROFILE_PATH = path.join(FABRICATION_ROOT, "physical-preflight-profile-v1.json");
const WORKSHEET_PATH = path.join(FABRICATION_ROOT, "physical-trial-worksheet-v1.json");
const DEFAULT_OUTPUT = path.join(FABRICATION_ROOT, "physical-preflight-v1.json");
const TEMPLATE_PATHS = [5, 6, 7].map((q) => `artifacts/global-geometry-ii/fabrication/q${q}-star-template.svg`);
const MM_PER_POINT = 25.4 / 72;

function canonicalStringify(value) {
  return Sheet.stableStringify(value);
}

function sha256Bytes(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function fileRecord(relativePath) {
  const bytes = fs.readFileSync(path.join(REPO_ROOT, relativePath));
  return { path: relativePath, sha256: sha256Bytes(bytes), bytes: bytes.length };
}

function round(value) {
  return Math.round(value * 1e12) / 1e12;
}

function parseArguments(argv) {
  if (!argv.length) return { mode: "generate", output: DEFAULT_OUTPUT };
  if (argv.length === 1 && argv[0] === "--validate-only") {
    return { mode: "validate", input: DEFAULT_OUTPUT };
  }
  if (argv.length === 2 && argv[0] === "--validate-only" && argv[1] && !argv[1].startsWith("--")) {
    return { mode: "validate", input: path.resolve(argv[1]) };
  }
  if (argv.length === 2 && argv[0] === "--output" && argv[1] && !argv[1].startsWith("--")) {
    return { mode: "generate", output: path.resolve(argv[1]) };
  }
  throw new Error("expected no arguments, --validate-only [path], or --output <path>");
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function validateProfile(profile) {
  const errors = [];
  if (!profile || profile.schema !== "ggii.physical-printer-profile/1") errors.push("wrong printer-profile schema");
  if (!profile || profile.hostVolatileIdentifiersRetained !== false) errors.push("host identifiers must be excluded");
  if (!profile || !profile.page || profile.page.name !== "A4" || profile.page.widthMm !== 210 || profile.page.heightMm !== 297) errors.push("profile page must be A4");
  const box = profile && profile.imagingBoxPt;
  if (!box || ![box.left, box.top, box.right, box.bottom].every(Number.isFinite) || box.left >= box.right || box.top >= box.bottom) errors.push("invalid imaging box");
  if (!profile || canonicalStringify(profile.supportedResolutionDpi) !== canonicalStringify([300, 600])) errors.push("expected frozen 300/600 dpi capability");
  if (!profile || !Array.isArray(profile.dryRasterObservations) || profile.dryRasterObservations.length !== 2) errors.push("two dry-raster observations are required");
  else profile.dryRasterObservations.forEach((entry) => {
    if (![300, 600].includes(entry.dpi) || entry.fitToPage !== false || entry.drawingMode !== "unscaled" || entry.jobSubmitted !== false) errors.push("invalid dry-raster observation");
  });
  if (!profile || profile.connectivity !== "NOT_EVALUATED" || profile.physicalOutput !== "NOT_RUN") errors.push("profile must not claim connectivity or physical output");
  return { valid: errors.length === 0, errors };
}

function validateWorksheetTemplate(worksheet) {
  const errors = [];
  if (!worksheet || worksheet.schema !== "ggii.physical-trial-worksheet/1") errors.push("wrong worksheet schema");
  if (!worksheet || worksheet.templateStatus !== "BLANK_NOT_RUN" || worksheet.copyBeforeUse !== true) errors.push("worksheet is not a blank copy-before-use template");
  if (!worksheet || !worksheet.authorization || Object.values(worksheet.authorization).some((value) => value !== false)) errors.push("blank worksheet must contain no authorization");
  if (!worksheet || !worksheet.gates || Object.values(worksheet.gates).some((value) => value !== "NOT_RUN")) errors.push("every blank worksheet gate must be NOT_RUN");
  if (!worksheet || worksheet.finalDecision !== "NOT_RUN") errors.push("blank worksheet decision must be NOT_RUN");
  if (!worksheet || !worksheet.printAudit || worksheet.printAudit.accepted !== null || worksheet.printAudit.rawEvidenceFiles.length !== 0) errors.push("blank print audit contains observations");
  if (!worksheet || !worksheet.cameraCalibration || worksheet.cameraCalibration.accepted !== null || worksheet.cameraCalibration.rawEvidenceFiles.length !== 0) errors.push("blank camera audit contains observations");
  if (!worksheet || !worksheet.trialMeasurements || worksheet.trialMeasurements.centerDefectRad !== null || worksheet.trialMeasurements.rawEvidenceFiles.length !== 0) errors.push("blank trial contains measurements");
  const t = worksheet && worksheet.frozenThresholds;
  if (!t || t.absolute100MmScaleErrorMaxMm !== 0.5 || t.faceEdgeErrorMaxMm !== 0.5 || t.cameraReprojectionRmsMaxPx !== 1 || t.independentAssembliesPerQMin !== 5) errors.push("worksheet thresholds changed");
  return { valid: errors.length === 0, errors };
}

function parseTemplate(relativePath) {
  const source = fs.readFileSync(path.join(REPO_ROOT, relativePath), "utf8");
  const qMatch = source.match(/data-q="(\d+)"/);
  const boxMatch = source.match(/data-layout-revision="printer-safe-v2"\s+data-required-printable-box-mm="([^"]+)"/);
  if (!qMatch || !boxMatch) throw new Error(`${relativePath}: missing printer-safe metadata`);
  const requiredPrintableBoxMm = boxMatch[1].trim().split(/\s+/).map(Number);
  if (requiredPrintableBoxMm.length !== 4 || requiredPrintableBoxMm.some((value) => !Number.isFinite(value))) {
    throw new Error(`${relativePath}: invalid required printable box`);
  }
  return {
    ...fileRecord(relativePath),
    q: Number(qMatch[1]),
    layoutRevision: "printer-safe-v2",
    requiredPrintableBoxMm
  };
}

function imagingBoxMm(profile) {
  const box = profile.imagingBoxPt;
  return [box.left, box.top, box.right, box.bottom].map((value) => round(value * MM_PER_POINT));
}

function clearanceMm(required, available) {
  return {
    left: round(required[0] - available[0]),
    top: round(required[1] - available[1]),
    right: round(available[2] - required[2]),
    bottom: round(available[3] - required[3])
  };
}

function rendererClearance(profile) {
  const observation = profile.rendererObservation300Dpi;
  const foreground = observation.foregroundBounds;
  const [px, py] = observation.printableOriginPx;
  const [pw, ph] = observation.printableSizePx;
  const values = {
    left: foreground.x - px,
    top: foreground.y - py,
    right: px + pw - (foreground.x + foreground.width),
    bottom: py + ph - (foreground.y + foreground.height)
  };
  return { ...values, minimum: Math.min(...Object.values(values)) };
}

function buildPayload(options) {
  const supplied = options || {};
  const profile = supplied.profile || readJson(PROFILE_PATH);
  const worksheet = supplied.worksheet || readJson(WORKSHEET_PATH);
  const profileValidation = validateProfile(profile);
  const worksheetValidation = validateWorksheetTemplate(worksheet);
  if (!profileValidation.valid) throw new Error(`invalid printer profile: ${profileValidation.errors.join("; ")}`);
  if (!worksheetValidation.valid) throw new Error(`invalid worksheet: ${worksheetValidation.errors.join("; ")}`);

  const availableBoxMm = imagingBoxMm(profile);
  const templates = TEMPLATE_PATHS.map(parseTemplate).map((template) => {
    const clearance = clearanceMm(template.requiredPrintableBoxMm, availableBoxMm);
    const minimumClearanceMm = Math.min(clearance.left, clearance.top, clearance.right, clearance.bottom);
    if (!(minimumClearanceMm > 0)) throw new Error(`${template.path}: declared foreground does not fit the printer profile`);
    return { ...template, availablePrintableBoxMm: availableBoxMm, clearanceMm: clearance, minimumClearanceMm };
  });

  const pixelClearance = rendererClearance(profile);
  if (!(pixelClearance.minimum > 0)) throw new Error("renderer foreground does not fit the observed printable raster");

  return {
    schema: "ggii.physical-preflight-evidence/1",
    evidenceStatus: "PASS_DRIVER_PROFILE_DRY_PREFLIGHT_ONLY",
    physicalValidation: "NOT_RUN",
    cameraValidation: "NOT_RUN",
    printJobSubmitted: false,
    scope: {
      established: [
        "the q=5,6,7 vector foreground envelopes fit the frozen sanitized A4 imaging box with positive analytic clearance",
        "the frozen 300/600 dpi dry-filter observations used 100 percent unscaled placement",
        "the renderer-specific 300 dpi foreground envelope remains inside the dry printable raster"
      ],
      notEstablished: [
        "printer connectivity, paper feed, ink output, or physical print scale",
        "cut dimensions, hinge gaps, incidence, assembly, or material response",
        "camera line of sight, permission, calibration, fiducial decoding, or 3-D reconstruction",
        "intrinsic or extrinsic physical measurements and repeatability"
      ]
    },
    normalizedPrinterProfile: { ...profile, source: fileRecord(path.relative(REPO_ROOT, PROFILE_PATH)) },
    templates,
    rendererClearance300DpiPx: pixelClearance,
    operatorWorksheet: {
      ...fileRecord(path.relative(REPO_ROOT, WORKSHEET_PATH)),
      schema: worksheet.schema,
      templateStatus: worksheet.templateStatus
    },
    reproductionCommands: {
      vectorAudit: "node artifacts/global-geometry-ii/fabrication/validate-fabrication.js",
      xmlAudit: "xmllint --noout artifacts/global-geometry-ii/fabrication/q5-star-template.svg artifacts/global-geometry-ii/fabrication/q6-star-template.svg artifacts/global-geometry-ii/fabrication/q7-star-template.svg",
      pdfRender: "rsvg-convert --format=pdf --output=<tmp>/q<q>.pdf artifacts/global-geometry-ii/fabrication/q<q>-star-template.svg",
      foregroundRender: "pdftoppm -png -r 300 -singlefile <tmp>/q<q>.pdf <tmp>/q<q>-full",
      foregroundBounds: "magick identify -format 'page=%wx%h foreground=%@\\n' <tmp>/q<q>-full.png",
      dryRaster300: "cupsfilter -p <ppd> -i application/pdf -m application/vnd.cups-raster -o PageSize=A4 -o Resolution=300dpi -o scaling=100 <tmp>/q<q>.pdf > <tmp>/q<q>-a4-300.raster",
      dryRaster600: "cupsfilter -p <ppd> -i application/pdf -m application/vnd.cups-raster -o PageSize=A4 -o Resolution=600dpi -o scaling=100 <tmp>/q<q>.pdf > <tmp>/q<q>-a4-600.raster"
    },
    handoffRequired: [
      "operator powers and loads an approved printer and explicitly selects actual size",
      "operator measures both scale directions and every face edge before cutting",
      "operator cuts, hinges, audits incidence, and assembles each q-star",
      "operator installs a frozen decodable marker dictionary and records tag-to-face transforms",
      "operator positions an apparatus-only camera, grants capture permission, and completes calibration/reference gates",
      "operator performs at least five independently seeded assemblies per q and retains every valid trial"
    ]
  };
}

function contentAddress(payload) {
  const canonical = canonicalStringify(payload);
  return {
    algorithm: "sha256",
    canonicalization: "ggii-physical-preflight-jcs-subset-v1",
    digest: sha256Bytes(Buffer.from(canonical, "utf8")),
    canonicalBytes: Buffer.byteLength(canonical, "utf8")
  };
}

function validatePayload(payload) {
  const errors = [];
  if (!payload || payload.schema !== "ggii.physical-preflight-evidence/1") errors.push("wrong evidence schema");
  if (!payload || payload.evidenceStatus !== "PASS_DRIVER_PROFILE_DRY_PREFLIGHT_ONLY") errors.push("wrong evidence status");
  if (!payload || payload.physicalValidation !== "NOT_RUN" || payload.cameraValidation !== "NOT_RUN" || payload.printJobSubmitted !== false) errors.push("physical evidence boundary violated");
  if (!payload || !Array.isArray(payload.templates) || payload.templates.length !== 3 || payload.templates.some((entry) => !(entry.minimumClearanceMm > 0))) errors.push("template clearance suite invalid");
  if (!payload || !payload.rendererClearance300DpiPx || !(payload.rendererClearance300DpiPx.minimum > 0)) errors.push("renderer clearance invalid");
  if (!payload || !payload.normalizedPrinterProfile || payload.normalizedPrinterProfile.hostVolatileIdentifiersRetained !== false) errors.push("printer profile is not sanitized");
  if (!payload || !payload.operatorWorksheet || payload.operatorWorksheet.templateStatus !== "BLANK_NOT_RUN") errors.push("blank operator worksheet not bound");
  try {
    if (canonicalStringify(payload) !== canonicalStringify(buildPayload())) errors.push("payload does not replay from the frozen profile, templates, and worksheet");
  } catch (error) {
    errors.push(`semantic replay failed: ${error.message}`);
  }
  return { valid: errors.length === 0, errors };
}

function validateArtifact(artifact) {
  const errors = [];
  if (!artifact || typeof artifact !== "object" || Array.isArray(artifact)) return { valid: false, errors: ["artifact must be an object"] };
  const payload = JSON.parse(JSON.stringify(artifact));
  const suppliedAddress = payload.contentAddress;
  delete payload.contentAddress;
  if (!suppliedAddress || canonicalStringify(suppliedAddress) !== canonicalStringify(contentAddress(payload))) errors.push("content address mismatch");
  const semantic = validatePayload(payload);
  if (!semantic.valid) errors.push(...semantic.errors);
  return { valid: errors.length === 0, errors };
}

function serializeArtifact(artifact) {
  return `${JSON.stringify(artifact, null, 2)}\n`;
}

function validateArtifactFile(input) {
  const raw = fs.readFileSync(input, "utf8");
  let artifact;
  try {
    artifact = JSON.parse(raw);
  } catch (error) {
    return { valid: false, errors: [`artifact JSON parse failed: ${error.message}`] };
  }
  const validation = validateArtifact(artifact);
  const errors = validation.errors.slice();
  if (raw !== serializeArtifact(artifact)) errors.push("artifact bytes are not in the frozen pretty-JSON encoding");
  return { valid: errors.length === 0, errors, artifact };
}

function writeExclusive(output, bytes) {
  fs.mkdirSync(path.dirname(output), { recursive: true });
  const descriptor = fs.openSync(output, "wx", 0o644);
  try {
    fs.writeFileSync(descriptor, bytes, "utf8");
    fs.fsyncSync(descriptor);
  } finally {
    fs.closeSync(descriptor);
  }
}

function main() {
  const args = parseArguments(process.argv.slice(2));
  if (args.mode === "validate") {
    const report = validateArtifactFile(args.input);
    if (!report.valid) throw new Error(`preflight artifact invalid: ${report.errors.join("; ")}`);
    process.stdout.write(`${JSON.stringify({ input: args.input, valid: true, sha256: report.artifact.contentAddress.digest, status: report.artifact.evidenceStatus, physicalValidation: report.artifact.physicalValidation })}\n`);
    return;
  }
  const output = args.output;
  const payload = buildPayload();
  const validation = validatePayload(payload);
  if (!validation.valid) throw new Error(`preflight payload invalid: ${validation.errors.join("; ")}`);
  const artifact = { ...payload, contentAddress: contentAddress(payload) };
  writeExclusive(output, serializeArtifact(artifact));
  const replayValidation = validateArtifactFile(output);
  if (!replayValidation.valid) throw new Error(`post-write artifact validation failed: ${replayValidation.errors.join("; ")}`);
  const replay = replayValidation.artifact;
  process.stdout.write(`${JSON.stringify({ output, sha256: replay.contentAddress.digest, status: replay.evidenceStatus, physicalValidation: replay.physicalValidation, minimumClearanceMm: Math.min(...replay.templates.map((entry) => entry.minimumClearanceMm)) })}\n`);
}

if (require.main === module) main();

module.exports = {
  buildPayload,
  canonicalStringify,
  clearanceMm,
  contentAddress,
  imagingBoxMm,
  parseArguments,
  rendererClearance,
  serializeArtifact,
  validateArtifactFile,
  validatePayload,
  validateArtifact,
  validateProfile,
  validateWorksheetTemplate,
  writeExclusive
};
