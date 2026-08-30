#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const REPO_ROOT = path.resolve(__dirname, "../..");
const PAGE_PATH = path.join(__dirname, "global-geometry-ii.html");
const REQUIRED_V2_LINKS = Object.freeze([
  "../../GLOBAL_GEOMETRY_II_U2_EVALUATION_REPORT.md",
  "../../artifacts/global-geometry-ii/u2/evaluation-v2/evaluation-index-v2.json",
  "../../global_geometry_ii_reproducibility_manifest_v2.json",
  "../../artifacts/global-geometry-ii/release-index-v2.json",
  "../../artifacts/global-geometry-ii/certificates/macos-windows-comparison-v2.json"
]);
const REQUIRED_DEEP_COMMAND = "node website/global-geometry-lab/reproduce-global-geometry-ii-v2.js --verify --mode deep";

function decodeHtmlAttribute(value) {
  return value
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, "\"")
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">");
}

function extractReferences(html) {
  if (typeof html !== "string") throw new Error("HTML source must be a string");
  const references = [];
  const tagPattern = /<(a|link|script|img|source)\b[^>]*?\b(href|src)\s*=\s*(?:"([^"]*)"|'([^']*)')[^>]*>/gi;
  let match;
  while ((match = tagPattern.exec(html)) !== null) {
    references.push({
      tag: match[1].toLowerCase(),
      attribute: match[2].toLowerCase(),
      value: decodeHtmlAttribute(match[3] === undefined ? match[4] : match[3])
    });
  }
  return references;
}

function isExternalOrFragment(reference) {
  return reference === "" || reference.startsWith("#") ||
    /^(?:https?:|mailto:|tel:|data:|javascript:|blob:|about:)/i.test(reference) || reference.startsWith("//");
}

function localReferencePath(pagePath, reference, repoRoot) {
  repoRoot = path.resolve(repoRoot || REPO_ROOT);
  if (isExternalOrFragment(reference)) return null;
  const withoutSuffix = reference.split("#", 1)[0].split("?", 1)[0];
  let decoded;
  try { decoded = decodeURIComponent(withoutSuffix); }
  catch (error) { throw new Error("local reference has invalid percent encoding: " + reference); }
  if (/\u0000/.test(decoded)) throw new Error("local reference contains NUL: " + reference);
  const resolved = path.resolve(path.dirname(pagePath), decoded);
  const relative = path.relative(repoRoot, resolved);
  if (!relative || relative === ".." || relative.startsWith(".." + path.sep) || path.isAbsolute(relative)) {
    throw new Error("local reference escapes the repository: " + reference);
  }
  return resolved;
}

function assertLocalTargets(html, pagePath, options) {
  options = options || {};
  const repoRoot = path.resolve(options.repoRoot || REPO_ROOT);
  const exists = options.exists || ((target) => {
    const stat = fs.lstatSync(target);
    return stat.isFile() && !stat.isSymbolicLink();
  });
  const allowedPending = new Set(options.allowedPendingReferences || []);
  const checked = [];
  const pending = [];
  extractReferences(html).forEach((reference) => {
    const target = localReferencePath(pagePath, reference.value, repoRoot);
    if (target === null) return;
    let valid = false;
    try { valid = exists(target); }
    catch (error) { valid = false; }
    if (!valid && allowedPending.has(reference.value)) {
      pending.push(reference.value);
      return;
    }
    if (!valid) throw new Error("local " + reference.attribute + " target is absent or not a regular file: " + reference.value);
    checked.push({ reference: reference.value, target });
  });
  return { checked, pending };
}

function textContent(html) {
  return html
    .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, " ")
    .replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/\s+/g, " ")
    .trim();
}

function evidenceBlocks(html) {
  const blocks = [];
  const pattern = /<(article|p|li)\b[^>]*>([\s\S]*?)<\/\1>/gi;
  let match;
  while ((match = pattern.exec(html)) !== null) blocks.push(textContent(match[2]));
  return blocks;
}

function assertEvidenceLanguage(html) {
  const text = textContent(html);
  const blocks = evidenceBlocks(html);
  const previewBlocks = blocks.map((block, index) => /\b(?:finite\s+)?preview\b.{0,500}\bNOT_EVALUATED\b/i.test(block) ? index : -1).filter((index) => index >= 0);
  const evaluationBlocks = blocks.map((block, index) => /\bevaluation(?:\s+checkpoint|\s+status)?\b.{0,500}\bUNRESOLVED\b/i.test(block) ? index : -1).filter((index) => index >= 0);
  if (previewBlocks.length === 0) {
    throw new Error("publication must retain a separately labeled preview status of NOT_EVALUATED");
  }
  if (evaluationBlocks.length === 0 || !previewBlocks.some((preview) => evaluationBlocks.some((evaluation) => evaluation !== preview))) {
    throw new Error("publication must separately label the current evaluation checkpoint UNRESOLVED");
  }
  if (!/\bphysical(?:\s+validation)?\b.{0,300}\bNOT_RUN\b/i.test(text)) {
    throw new Error("publication must state physical validation NOT_RUN");
  }
  const forbidden = [
    /\bU2\b.{0,100}\bACCEPTED\b/i,
    /\bU2\b.{0,100}\bREJECTED\b/i,
    /\bACCEPTED\b.{0,100}\bU2\b/i,
    /\bREJECTED\b.{0,100}\bU2\b/i,
    /\bphysical(?:\s+validation)?\b.{0,100}\bPASS(?:ED)?\b/i,
    /\bPASS(?:ED)?\b.{0,100}\bphysical(?:\s+validation)?\b/i
  ];
  forbidden.forEach((pattern) => {
    if (pattern.test(text)) throw new Error("publication contains a forbidden U2 or physical-validation promotion: " + pattern);
  });
  return text;
}

function assertV2Resources(html) {
  const references = new Set(extractReferences(html).map((entry) => entry.value));
  REQUIRED_V2_LINKS.forEach((required) => {
    if (!references.has(required)) throw new Error("publication omits required release-v2 link " + required);
  });
  const text = textContent(html);
  if (!text.includes(REQUIRED_DEEP_COMMAND)) throw new Error("publication omits the exact release-v2 deep reproduction command");
  return { references, text };
}

function assertCspCompatibleMarkup(html) {
  if (/\son[a-z]+\s*=/i.test(html)) throw new Error("publication contains an inline event handler incompatible with strict same-origin CSP");
  if (/\b(?:href|src)\s*=\s*["']\s*javascript:/i.test(html)) throw new Error("publication contains a javascript: URL incompatible with strict CSP");
  return true;
}

function validatePublication(html, pagePath, options) {
  const targets = assertLocalTargets(html, pagePath, options);
  const resources = assertV2Resources(html);
  assertEvidenceLanguage(html);
  assertCspCompatibleMarkup(html);
  return { localTargetCount: targets.checked.length, pendingTargets: targets.pending.slice(), referenceCount: resources.references.size };
}

const tests = [];
function test(name, body) { tests.push({ name, body }); }

test("reference parser separates local files from fragments and external URLs", () => {
  const fixture = [
    '<a href="local&amp;name.json">local</a>',
    '<script src="scripts/app.js"></script>',
    '<a href="#section">section</a>',
    '<a href="https://example.test/example">external</a>'
  ].join("\n");
  const references = extractReferences(fixture);
  const fixtureRoot = path.join(path.parse(path.resolve(".")).root, "ggii-static-publication-fixture");
  const fixturePage = path.join(fixtureRoot, "page.html");
  assert.deepStrictEqual(references.map((entry) => entry.value), ["local&name.json", "scripts/app.js", "#section", "https://example.test/example"]);
  assert.strictEqual(localReferencePath(fixturePage, "#section", fixtureRoot), null);
  assert.strictEqual(localReferencePath(fixturePage, "https://example.test", fixtureRoot), null);
  assert.strictEqual(localReferencePath(fixturePage, "scripts/app.js", fixtureRoot), path.join(fixtureRoot, "scripts/app.js"));
  assert.throws(() => localReferencePath(fixturePage, "../outside", fixtureRoot), /escapes/);
  assert.throws(
    () => assertLocalTargets('<a href="pending.json">pending</a>', fixturePage, { repoRoot: fixtureRoot, exists: () => false }),
    /absent/
  );
  const pending = assertLocalTargets('<a href="pending.json">pending</a>', fixturePage, {
    repoRoot: fixtureRoot,
    exists: () => false,
    allowedPendingReferences: ["pending.json"]
  });
  assert.deepStrictEqual(pending.pending, ["pending.json"]);
  const materialized = assertLocalTargets('<a href="pending.json">pending</a>', fixturePage, {
    repoRoot: fixtureRoot,
    exists: () => true,
    allowedPendingReferences: ["pending.json"]
  });
  assert.deepStrictEqual(materialized.pending, []);
  assert.strictEqual(materialized.checked.length, 1);
});

test("evidence-language helper keeps preview/evaluation/physical states distinct and rejects promotion", () => {
  const bounded = "<p>Finite preview status NOT_EVALUATED.</p><p>Evaluation checkpoint status UNRESOLVED.</p><p>Physical validation status NOT_RUN.</p>";
  assert.doesNotThrow(() => assertEvidenceLanguage(bounded));
  assert.throws(() => assertEvidenceLanguage(bounded + " U2 is ACCEPTED."), /forbidden/);
  assert.throws(() => assertEvidenceLanguage(bounded + " Physical validation PASS."), /forbidden/);
  assert.throws(() => assertEvidenceLanguage("Evaluation UNRESOLVED. Physical NOT_RUN."), /preview/);
});

test("strict-CSP markup rejects inline event handlers", () => {
  assert.doesNotThrow(() => assertCspCompatibleMarkup('<form class="controls"></form>'));
  assert.throws(() => assertCspCompatibleMarkup('<form onsubmit="return false"></form>'), /inline event handler/);
  assert.throws(() => assertCspCompatibleMarkup('<a href="javascript:void(0)">x</a>'), /javascript:/);
});

test("published Global Geometry II page has closed local links and the release-v2 evidence boundary", () => {
  const html = fs.readFileSync(PAGE_PATH, "utf8");
  const externalComparison = "../../artifacts/global-geometry-ii/certificates/macos-windows-comparison-v2.json";
  const requireComparison = process.env.GGII_STATIC_PUBLICATION_REQUIRE_COMPARISON_V2 === "1";
  const report = validatePublication(html, PAGE_PATH, {
    // The general v2 comparison is generated from the two local certificates,
    // while this test is itself in each local certificate's quick suite.  Its
    // exact link is mandatory, but existence becomes mandatory only in the
    // post-comparison publication audit to avoid a certification cycle.
    allowedPendingReferences: requireComparison ? [] : [externalComparison]
  });
  assert.ok(report.localTargetCount >= REQUIRED_V2_LINKS.length);
  assert.ok(report.referenceCount >= REQUIRED_V2_LINKS.length);
  if (requireComparison) assert.deepStrictEqual(report.pendingTargets, []);
  else {
    assert.ok(
      report.pendingTargets.length === 0 ||
      (report.pendingTargets.length >= 1 && report.pendingTargets.every((entry) => entry === externalComparison))
    );
  }
});

const filter = process.env.GGII_STATIC_PUBLICATION_V2_TEST_FILTER || "";
const selected = filter ? tests.filter((entry) => entry.name.toLowerCase().includes(filter.toLowerCase())) : tests;
if (filter && selected.length === 0) {
  process.stderr.write("No static-publication-v2 tests match GGII_STATIC_PUBLICATION_V2_TEST_FILTER=" + filter + "\n");
  process.exitCode = 1;
}

let passed = 0;
for (const entry of selected) {
  try {
    entry.body();
    passed += 1;
    process.stdout.write("ok " + passed + " - " + entry.name + "\n");
  } catch (error) {
    process.stderr.write("not ok - " + entry.name + "\n" + (error.stack || error.message) + "\n");
    process.exitCode = 1;
    break;
  }
}

if (!process.exitCode) {
  process.stdout.write("\n1.." + passed + "\nAll Global Geometry II static-publication-v2 tests passed.\n");
}

module.exports = {
  PAGE_PATH,
  REPO_ROOT,
  REQUIRED_DEEP_COMMAND,
  REQUIRED_V2_LINKS,
  assertCspCompatibleMarkup,
  assertEvidenceLanguage,
  assertLocalTargets,
  assertV2Resources,
  extractReferences,
  evidenceBlocks,
  isExternalOrFragment,
  localReferencePath,
  textContent,
  validatePublication
};
