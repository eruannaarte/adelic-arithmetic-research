#!/usr/bin/env node
"use strict";

/*
 * Deterministic, dependency-free audit for the Global Geometry II q-star SVGs.
 * This checks vector semantics and the protocol-v2 exact identities. An XML
 * parser remains a separate release gate (`xmllint --noout q*-template.svg`).
 */

const fs = require("fs");
const path = require("path");
const Sheet = require(path.join(__dirname, "../../../website/global-geometry-lab/global-geometry-ii-sheet.js"));

const EXPECTED_DISPLAY = Object.freeze({ 5: "+π/3", 6: "0", 7: "−π/3" });
const SERIALIZATION_TOLERANCE_MM = 5e-10;
const REQUIRED_PRINTABLE_BOX_MM = Object.freeze([7.75, 13.75, 202.25, 283.25]);

function fail(file, message) {
  throw new Error(path.basename(file) + ": " + message);
}

function distance(a, b) {
  return Math.hypot(a[0] - b[0], a[1] - b[1]);
}

function audit(q) {
  const file = path.join(__dirname, "q" + q + "-star-template.svg");
  const source = fs.readFileSync(file, "utf8");

  if (!/width="210mm" height="297mm" viewBox="0 0 210 297"/.test(source)) {
    fail(file, "page must be A4 with a matching millimetre viewBox");
  }
  if (!new RegExp("data-q=\\\"" + q + "\\\"").test(source)) {
    fail(file, "root q metadata is absent or wrong");
  }
  const printableBox = source.match(/data-layout-revision="printer-safe-v2"\s+data-required-printable-box-mm="([^"]+)"/);
  if (
    !printableBox ||
    printableBox[1].trim().split(/\s+/).map(Number).some((value, index) => value !== REQUIRED_PRINTABLE_BOX_MM[index])
  ) {
    fail(file, "printer-safe foreground box metadata is absent or wrong");
  }
  if (/<script|<foreignObject|(?:href|src)="(?!#)/i.test(source) || /url\(https?:/i.test(source)) {
    fail(file, "executable or external content is forbidden");
  }

  const ids = Array.from(source.matchAll(/\sid="([^"]+)"/g), match => match[1]);
  if (new Set(ids).size !== ids.length) fail(file, "XML IDs are not unique");

  const faces = Array.from(
    source.matchAll(/<g id="face-(\d{2})"[^>]*data-face-id="face-\1"[^>]*data-marker-location-id="F\1"[^>]*data-nominal-side-mm="60"/g),
    match => Number(match[1])
  );
  if (faces.length !== q || faces.some((value, index) => value !== index)) {
    fail(file, "face groups must be the dense canonical sequence face-00 through face-" + String(q - 1).padStart(2, "0"));
  }
  if ((source.match(/<use href="#nominal-face"\/>/g) || []).length !== q) {
    fail(file, "every face group must expand the local nominal-face definition exactly once");
  }
  const faceTranslations = Array.from(
    source.matchAll(/<g id="face-\d{2}" transform="translate\(([\d.]+) ([\d.]+)\)"/g),
    match => [Number(match[1]), Number(match[2])]
  );
  if (
    faceTranslations.length !== q ||
    faceTranslations.some(([x, y]) => x < 10 || x + 60 > 200 || y < 28 || y + 30 * Math.sqrt(3) > 200)
  ) {
    fail(file, "face placement leaves the declared printer-safe layout envelope");
  }

  const pointMatch = source.match(/data-role="cut-perimeter"[^>]*points="([^"]+)"/);
  if (!pointMatch) fail(file, "nominal cut polygon is missing");
  const points = pointMatch[1].trim().split(/\s+/).map(pair => pair.split(",").map(Number));
  if (points.length !== 3 || points.some(point => point.length !== 2 || point.some(value => !Number.isFinite(value)))) {
    fail(file, "nominal cut polygon is malformed");
  }
  [distance(points[0], points[1]), distance(points[1], points[2]), distance(points[2], points[0])].forEach(length => {
    if (Math.abs(length - 60) > SERIALIZATION_TOLERANCE_MM) fail(file, "face edge is not 60 mm: " + length);
  });

  if (!/data-role="fiducial-location"\s+x="20" y="9" width="20" height="20"/.test(source)) {
    fail(file, "20 mm fiducial location is missing");
  }
  if (!/data-role="fiducial-clearance"\s+x="19" y="8" width="22" height="22"/.test(source)) {
    fail(file, "fiducial no-cut/no-hinge clearance is missing");
  }
  if ((source.match(/data-role="(?:left|right)-hinge-guide"/g) || []).length !== 2) {
    fail(file, "the local face must declare both radial hinge guides");
  }

  if (!/data-role="horizontal-10mm-scale" data-length-mm="10"\s+x="8"[^>]*width="10"/.test(source)) {
    fail(file, "horizontal 10 mm scale is missing or malformed");
  }
  const horizontal = source.match(/id="horizontal-scale-bars" data-role="horizontal-100mm-scale"\s+data-length-mm="100" data-start-x-mm="([^"]+)" data-end-x-mm="([^"]+)"/);
  if (!horizontal || Number(horizontal[2]) - Number(horizontal[1]) !== 100) {
    fail(file, "horizontal 100 mm scale is missing or malformed");
  }
  const vertical = source.match(/data-role="vertical-100mm-scale" data-length-mm="100"[^>]*x1="([^"]+)" y1="([^"]+)" x2="([^"]+)" y2="([^"]+)"/);
  if (!vertical || Math.hypot(Number(vertical[3]) - Number(vertical[1]), Number(vertical[4]) - Number(vertical[2])) !== 100) {
    fail(file, "vertical 100 mm scale is missing or malformed");
  }
  if (
    Number(vertical[1]) !== 201 ||
    Number(vertical[3]) !== 201 ||
    Math.max(...faceTranslations.map(([x]) => x + 60)) >= Number(vertical[1]) ||
    !source.includes('translate(202 151) rotate(-90)')
  ) {
    fail(file, "vertical scale is outside the printer-safe layout position");
  }
  if (!/data-role="print-safe-header" x="8" y="14" width="194" height="13"/.test(source)) {
    fail(file, "printer-safe header placement is absent or malformed");
  }
  if (!/data-role="print-safe-legend" x="8" y="204" width="194" height="51"/.test(source)) {
    fail(file, "printer-safe legend placement is absent or malformed");
  }
  if (!/class="warning" x="105" y="279"/.test(source) || !/class="tiny" x="105" y="282\.5"/.test(source)) {
    fail(file, "printer-safe footer placement is absent or malformed");
  }

  ["NO ACTUATORS", "NOT A CONTROL DRAWING", "PHYSICAL VALIDATION NOT PERFORMED"].forEach(label => {
    if (!source.includes(label)) fail(file, "required safety/evidence label is absent: " + label);
  });
  if (!source.includes(EXPECTED_DISPLAY[q])) fail(file, "displayed q-specific center defect is absent");

  const star = Sheet.createQStar(q);
  const center = star.intrinsic.center.defectPiCoefficient;
  const expectedDenominator = q === 6 ? 1 : 3;
  if (
    star.schemaVersion !== 2 ||
    star.counts.eulerCharacteristic !== 1 ||
    center.numerator !== 6 - q ||
    center.denominator !== expectedDenominator ||
    star.intrinsic.boundary.length !== q ||
    star.intrinsic.boundary.some(entry => entry.defectPiCoefficient.numerator !== 1 || entry.defectPiCoefficient.denominator !== 3) ||
    star.intrinsic.totalDefectPiCoefficient.numerator !== 2 ||
    star.intrinsic.totalDefectPiCoefficient.denominator !== 1 ||
    star.intrinsic.exactGaussBonnetIdentity !== true
  ) {
    fail(file, "SVG program disagrees with the protocol-v2 q-star identity");
  }

  return {
    q,
    faces: faces.length,
    sideMm: 60,
    requiredPrintableBoxMm: REQUIRED_PRINTABLE_BOX_MM,
    centerDefectPiCoefficient: center,
    boundaryDefectPiCoefficient: { numerator: 1, denominator: 3 },
    totalDefectPiCoefficient: { numerator: 2, denominator: 1 }
  };
}

const reports = [5, 6, 7].map(audit);
reports.forEach(report => {
  process.stdout.write(
    "PASS q=" + report.q +
    " faces=" + report.faces +
    " side=" + report.sideMm + "mm" +
    " exact Kc=" + report.centerDefectPiCoefficient.numerator + "π/" + report.centerDefectPiCoefficient.denominator +
    "\n"
  );
});
process.stdout.write("All Global Geometry II fabrication-vector audits passed.\n");
