#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");

const PROBE_PARENT = "C:\\Users\\Public\\ggii-u2-replication\\fsync-probes";
fs.mkdirSync(PROBE_PARENT, { recursive: true });
const root = fs.mkdtempSync(path.join(PROBE_PARENT, "screening-v2-"));
const probeId = path.basename(root);

function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function canonical(value) {
  if (value === null || typeof value === "string" || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "number") {
    if (!Number.isFinite(value) || Object.is(value, -0)) throw new Error("invalid canonical number");
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return "[" + value.map(canonical).join(",") + "]";
  return "{" + Object.keys(value).sort().map((key) => JSON.stringify(key) + ":" + canonical(value[key])).join(",") + "}";
}

function observe(id, operation) {
  try {
    const detail = operation();
    return { id, completed: true, error: null, detail: detail || null };
  } catch (error) {
    return { id, completed: false, error: { name: error.name || null, code: error.code || null, errno: error.errno === undefined ? null : error.errno, syscall: error.syscall || null, message: error.message || String(error) }, detail: null };
  }
}

const bytes = Buffer.from("ggii-windows-fsync-probe-v1\n", "utf8");
const cases = [];

cases.push(observe("original-wx-fsync-before-link", () => {
  const temporary = path.join(root, "case1.temp");
  const descriptor = fs.openSync(temporary, "wx");
  try { fs.writeFileSync(descriptor, bytes); fs.fsyncSync(descriptor); }
  finally { fs.closeSync(descriptor); }
  return { contentSha256: sha256(fs.readFileSync(temporary)) };
}));

cases.push(observe("reopen-hardlink-readonly-r-fsync", () => {
  const temporary = path.join(root, "case2.temp"), output = path.join(root, "case2.final");
  fs.writeFileSync(temporary, bytes, { flag: "wx" });
  fs.linkSync(temporary, output);
  const descriptor = fs.openSync(output, "r");
  try { fs.fsyncSync(descriptor); }
  finally { fs.closeSync(descriptor); }
  return { contentSha256: sha256(fs.readFileSync(output)) };
}));

cases.push(observe("reopen-hardlink-writable-r-plus-fsync", () => {
  const temporary = path.join(root, "case3.temp"), output = path.join(root, "case3.final");
  fs.writeFileSync(temporary, bytes, { flag: "wx" });
  fs.linkSync(temporary, output);
  const descriptor = fs.openSync(output, "r+");
  try { fs.fsyncSync(descriptor); }
  finally { fs.closeSync(descriptor); }
  return { contentSha256: sha256(fs.readFileSync(output)) };
}));

cases.push(observe("original-writable-fd-across-hardlink-and-refsync", () => {
  const temporary = path.join(root, "case4.temp"), output = path.join(root, "case4.final");
  const descriptor = fs.openSync(temporary, "wx+");
  try {
    fs.writeFileSync(descriptor, bytes);
    fs.fsyncSync(descriptor);
    fs.linkSync(temporary, output);
    fs.fsyncSync(descriptor);
  } finally { fs.closeSync(descriptor); }
  return { contentSha256: sha256(fs.readFileSync(output)), sameContent: fs.readFileSync(output).equals(bytes) };
}));

cases.push(observe("directory-open-r-fsync", () => {
  const descriptor = fs.openSync(root, "r");
  try { fs.fsyncSync(descriptor); }
  finally { fs.closeSync(descriptor); }
  return { directoryFsyncReturned: true };
}));

cases.push(observe("hardlink-no-replace-eexist", () => {
  const temporary = path.join(root, "case6.temp"), output = path.join(root, "case6.final");
  fs.writeFileSync(temporary, bytes, { flag: "wx" });
  fs.writeFileSync(output, Buffer.from("preexisting\n", "utf8"), { flag: "wx" });
  let collision = null;
  try { fs.linkSync(temporary, output); }
  catch (error) { collision = { code: error.code || null, syscall: error.syscall || null }; }
  if (!collision) throw new Error("hard link unexpectedly replaced existing output");
  return { collision, outputSha256: sha256(fs.readFileSync(output)), outputPreserved: fs.readFileSync(output).toString("utf8") === "preexisting\n" };
}));

const byId = Object.fromEntries(cases.map((entry) => [entry.id, entry]));
const payload = {
  schema: "gg.u2.screening.windows-fsync-matrix/1",
  semanticRole: "outcome-blind Windows filesystem capability probe; no scientific source or decision authority",
  probeId,
  environment: { platform: process.platform, arch: process.arch, node: process.version, osRelease: os.release(), filesystemApi: "node:fs synchronous operations" },
  cases,
  conclusions: {
    readonlyReopenOperationallyValid: byId["reopen-hardlink-readonly-r-fsync"].completed,
    writableReopenOperationallyValid: byId["reopen-hardlink-writable-r-plus-fsync"].completed,
    originalWritableDescriptorAcrossLinkOperationallyValid: byId["original-writable-fd-across-hardlink-and-refsync"].completed,
    directoryFsyncAvailableViaNode: byId["directory-open-r-fsync"].completed,
    hardlinkNoReplacePreserved: byId["hardlink-no-replace-eexist"].completed && byId["hardlink-no-replace-eexist"].detail.outputPreserved === true,
    narrowRepair: "keep the original writable descriptor open through the exclusive hard-link publication and fsync it after linking; on win32 do not call directory fsync, and report the unavailable directory barrier explicitly",
    durabilityQualification: "functional file flush and no-replace publication are demonstrated; power-loss persistence of the directory entry is not established because Node win32 directory fsync is unavailable"
  },
  outcome: { u2Status: "UNRESOLVED", decisionAuthority: "NONE" }
};
const digest = sha256(Buffer.from(canonical(payload), "utf8"));
const artifact = Object.assign({}, payload, { contentAddress: { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest, canonicalBytes: Buffer.byteLength(canonical(payload), "utf8") } });
const output = path.join(root, "windows-fsync-matrix.json");
fs.writeFileSync(output, Buffer.from(JSON.stringify(artifact, null, 2) + "\n", "utf8"), { flag: "wx" });
process.stdout.write(JSON.stringify({ probeId, output, fileSha256: sha256(fs.readFileSync(output)), semanticDigest: digest, conclusions: artifact.conclusions }) + "\n");
