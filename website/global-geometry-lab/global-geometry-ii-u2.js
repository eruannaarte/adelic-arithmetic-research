/* Global Geometry II — frozen U2-v2 bounded-disk campaign kernel. */
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const G2 = require("./global-geometry-ii-core.js");
const Ensembles = require("./global-geometry-ii-ensembles.js");
const ManifestGenerator = require("./generate-global-geometry-ii-u2-manifest.js");

const VERSION = "0.2.0-u2.2";
const ROOT = path.resolve(__dirname, "../..");
const MANIFEST_PATH = path.join(ROOT, "artifacts/global-geometry-ii/u2/experiment-manifest-v2.json");
const MANIFEST_DIGEST = "80252bca7951da99d9e7de778d98e3ad7147b7b9a76bb585d7ca266ddad348b3";
const DECISION_DIGEST = "faffef2526d16f79b700102057d59745f0a4359ea7c386c318cc0ee4afd0d5dc";
const PREREGISTRATION_COMMIT = "150e4e7";
const RNG_ID = "gg-sha256-object-u53-v1";
const RUN_SCHEMA = "gg.atlas.u2-run/2";
const CALIBRATION_SCHEMA = "gg.atlas.u2-normalization/2";
const RESULT_SCHEMA = "gg.atlas.u2-result/2";
const STREAMS = Object.freeze(["generator", "conductance", "dynamics", "roots", "heat-probes", "perturbation", "bootstrap"]);
const PRIMARY_CONTROLS = Object.freeze(["comb-trap", "small-world-shortcuts", "vanishing-neck", "perforated-disk"]);
const CONSTRUCTION_CONTRACT = Object.freeze({
  id: "ggii-u2-v2-batch-construction/1",
  positiveFamilies: {
    "square-alternating": "integer square grid with parity-alternating local diagonal",
    "triangular-clipped": "equilateral triangular rows clipped by the preview strip rule",
    "cell-center-fan": "integer square grid plus one center and four triangles per cell",
    "square-hashed-diagonal": "one diagonal per square chosen by gg-sha256-object-u53-v1"
  },
  overlapPolicy: "coordinate/edge/face-count equivalence to preview constructors at every L<=24; hashed members share the same closed motif but use the v2 SHA object stream",
  controls: {
    "comb-trap": { toothLength: "floor(L/4)", fallback: "none" },
    "small-world-shortcuts": { q: 0.02, endpointRounding: "floor(q*(L+1)^2), then floor to an even endpoint count", pairing: "SHA-score order, reverse greedy, separation>=L/3", fallback: "shortfall => INVALID_COMPLEX and Gate 7 UNRESOLVED" },
    "vanishing-neck": { patches: "two L-by-L parity-alternating filled square patches", corridor: "2-by-floor(L/4) filled square strip centered vertically", fallback: "none" },
    "perforated-disk": { target: "floor(0.05*L^2) interior vertex stars", selection: "SHA-score order with Chebyshev center separation>=3", removal: "delete selected vertices and every incident face, then rematerialize closure", fallback: "selection shortfall or invalid manifold => INVALID_COMPLEX and Gate 7 UNRESOLVED" }
  },
  finiteRootAndWalkerScope: "descriptive finite measurement only; never a coverage or continuum claim"
});
const TIME_GRID = Object.freeze((function () {
  const out = [], seen = new Set();
  for (let k = 0; k < 14; k += 1) {
    const value = Math.ceil(8 * Math.pow(2, k / 2));
    if (!seen.has(value)) { seen.add(value); out.push(value); }
  }
  return out;
})());

function denseArray(value) {
  if (!Array.isArray(value) || Object.keys(value).length !== value.length) return false;
  for (let i = 0; i < value.length; i += 1) if (!Object.prototype.hasOwnProperty.call(value, i)) return false;
  return true;
}
function plainObject(value) { return !!value && typeof value === "object" && !Array.isArray(value) && (Object.getPrototypeOf(value) === Object.prototype || Object.getPrototypeOf(value) === null); }
function canonicalStringify(value) {
  if (value === null || typeof value === "string" || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "number") {
    if (!Number.isFinite(value) || Object.is(value, -0)) throw new Error("canonical JSON contains an invalid number");
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    if (!denseArray(value)) throw new Error("canonical JSON arrays must be dense");
    return "[" + value.map(canonicalStringify).join(",") + "]";
  }
  if (!plainObject(value)) throw new Error("canonical JSON objects must be plain");
  return "{" + Object.keys(value).sort().map(function (key) { return JSON.stringify(key) + ":" + canonicalStringify(value[key]); }).join(",") + "}";
}
function clone(value) { return JSON.parse(canonicalStringify(value)); }
function sha256(value) { return crypto.createHash("sha256").update(typeof value === "string" ? value : canonicalStringify(value), "utf8").digest("hex"); }
function contentAddress(payload) {
  const canonical = canonicalStringify(payload);
  return { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest: sha256(canonical), canonicalBytes: Buffer.byteLength(canonical, "utf8") };
}
function merkleRoot(leaves) {
  if (!denseArray(leaves) || !leaves.length || leaves.some(function (leaf) { return !/^[0-9a-f]{64}$/.test(leaf); })) throw new Error("invalid Merkle leaves");
  let level = leaves.slice();
  while (level.length > 1) {
    const next = [];
    for (let i = 0; i < level.length; i += 2) {
      const right = i + 1 < level.length ? level[i + 1] : level[i];
      next.push(crypto.createHash("sha256").update(Buffer.from(level[i] + right, "hex")).digest("hex"));
    }
    level = next;
  }
  return level[0];
}

function loadManifest() {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, "utf8"));
  const report = ManifestGenerator.validateManifest(manifest);
  if (!report.valid) throw new Error("frozen U2 manifest is invalid: " + report.errors.join("; "));
  if (manifest.contentAddress.digest !== MANIFEST_DIGEST) throw new Error("frozen U2 manifest digest mismatch");
  const decision = manifest.protocolAdoption.protocols.decisionContract;
  if (decision.id !== "u2-decision-v2" || decision.sha256 !== DECISION_DIGEST) throw new Error("u2-decision-v2 binding mismatch");
  return manifest;
}

function requireNamespace(namespace) {
  if (namespace !== "cal" && namespace !== "confirm" && namespace !== "control") throw new Error("unknown U2 namespace");
}
function deriveStreamSeed(namespace, familyId, sigma, linearSize, replicate, streamName) {
  requireNamespace(namespace);
  if (STREAMS.indexOf(streamName) < 0) throw new Error("unknown stream role");
  return sha256(["ggii-u2-v2", 2, namespace + "/", familyId, { sigma: sigma }, linearSize, replicate, streamName]);
}
function objectUniform(streamSeed, objectCanonicalKey, counter) {
  if (!/^[0-9a-f]{64}$/.test(streamSeed || "")) throw new Error("stream seed must be SHA-256 hex");
  if (typeof objectCanonicalKey !== "string" || !objectCanonicalKey.length) throw new Error("object key is required");
  if (!Number.isSafeInteger(counter) || counter < 0) throw new Error("counter must be a nonnegative safe integer");
  const digest = crypto.createHash("sha256").update(canonicalStringify([streamSeed, objectCanonicalKey, counter]), "utf8").digest();
  const integer53 = digest.readUInt32BE(0) * 2097152 + (digest.readUInt32BE(4) >>> 11);
  return integer53 / 9007199254740992;
}

function gcd(a, b) { while (b) { const t = a % b; a = b; b = t; } return Math.abs(a); }
function median(values) {
  if (!values.length) return null;
  const sorted = values.slice().sort(function (a, b) { return a - b; });
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}
function mean(values) { return values.length ? values.reduce(function (sum, value) { return sum + value; }, 0) / values.length : null; }
function quantile(values, q) {
  if (!values.length) return null;
  const sorted = values.slice().sort(function (a, b) { return a - b; });
  const position = (sorted.length - 1) * q, lower = Math.floor(position), upper = Math.ceil(position);
  return lower === upper ? sorted[lower] : sorted[lower] * (upper - position) + sorted[upper] * (position - lower);
}
function olsLogSlope(xs, ys) {
  if (xs.length !== ys.length || xs.length < 2 || ys.some(function (value) { return !(value > 0); })) return null;
  const lx = xs.map(Math.log), ly = ys.map(Math.log), mx = mean(lx), my = mean(ly);
  let numerator = 0, denominator = 0;
  for (let i = 0; i < lx.length; i += 1) { numerator += (lx[i] - mx) * (ly[i] - my); denominator += (lx[i] - mx) * (lx[i] - mx); }
  return denominator > 0 ? numerator / denominator : null;
}

function addEdge(edgeMap, nodes, u, v) {
  if (u === v) return;
  const a = Math.min(u, v), b = Math.max(u, v), id = a + ":" + b;
  if (edgeMap.has(id)) return;
  const dx = nodes[a].x - nodes[b].x, dy = nodes[a].y - nodes[b].y;
  edgeMap.set(id, { u: a, v: b, length: Math.sqrt(dx * dx + dy * dy), key: nodes[a].key + "|" + nodes[b].key });
}
function finishGraph(familyId, linearSize, nodes, edgeMap, faceCount, generatorSeed) {
  const edges = Array.from(edgeMap.values()).sort(function (a, b) { return a.u - b.u || a.v - b.v; });
  const adjacency = nodes.map(function () { return []; });
  edges.forEach(function (edge, index) {
    adjacency[edge.u].push({ to: edge.v, length: edge.length, edgeIndex: index });
    adjacency[edge.v].push({ to: edge.u, length: edge.length, edgeIndex: index });
  });
  adjacency.forEach(function (row) { row.sort(function (a, b) { return a.to - b.to; }); });
  const xs = nodes.map(function (node) { return node.x; }), ys = nodes.map(function (node) { return node.y; });
  const structureDigest = sha256({ familyId: familyId, linearSize: linearSize, generatorSeed: familyId === "square-hashed-diagonal" ? generatorSeed : "deterministic", nodes: nodes.map(function (node) { return [node.key, node.x, node.y]; }), edges: edges.map(function (edge) { return [edge.u, edge.v, edge.length]; }) });
  return { familyId: familyId, linearSize: linearSize, nodes: nodes, edges: edges, adjacency: adjacency, faceCount: faceCount, bounds: { minX: Math.min.apply(null, xs), maxX: Math.max.apply(null, xs), minY: Math.min.apply(null, ys), maxY: Math.max.apply(null, ys) }, structureDigest: structureDigest };
}
function squareGraph(familyId, linearSize, generatorSeed) {
  const nodes = [], side = linearSize + 1;
  function id(r, c) { return r * side + c; }
  for (let r = 0; r <= linearSize; r += 1) for (let c = 0; c <= linearSize; c += 1) nodes.push({ key: "p:" + r + ":" + c, x: c, y: r });
  const edgeMap = new Map();
  for (let r = 0; r <= linearSize; r += 1) for (let c = 0; c < linearSize; c += 1) addEdge(edgeMap, nodes, id(r, c), id(r, c + 1));
  for (let r = 0; r < linearSize; r += 1) for (let c = 0; c <= linearSize; c += 1) addEdge(edgeMap, nodes, id(r, c), id(r + 1, c));
  for (let r = 0; r < linearSize; r += 1) for (let c = 0; c < linearSize; c += 1) {
    const southwestNortheast = familyId === "square-alternating" ? (r + c) % 2 === 0 : objectUniform(generatorSeed, "cell:" + r + ":" + c, 0) < 0.5;
    addEdge(edgeMap, nodes, southwestNortheast ? id(r, c) : id(r, c + 1), southwestNortheast ? id(r + 1, c + 1) : id(r + 1, c));
  }
  return finishGraph(familyId, linearSize, nodes, edgeMap, 2 * linearSize * linearSize, generatorSeed);
}
function fanGraph(linearSize, generatorSeed) {
  const nodes = [], side = linearSize + 1;
  function corner(r, c) { return r * side + c; }
  for (let r = 0; r <= linearSize; r += 1) for (let c = 0; c <= linearSize; c += 1) nodes.push({ key: "p:" + (2 * r) + ":" + (2 * c), x: c, y: r });
  const centerBase = nodes.length;
  function center(r, c) { return centerBase + r * linearSize + c; }
  for (let r = 0; r < linearSize; r += 1) for (let c = 0; c < linearSize; c += 1) nodes.push({ key: "p:" + (2 * r + 1) + ":" + (2 * c + 1), x: c + 0.5, y: r + 0.5 });
  const edgeMap = new Map();
  for (let r = 0; r <= linearSize; r += 1) for (let c = 0; c < linearSize; c += 1) addEdge(edgeMap, nodes, corner(r, c), corner(r, c + 1));
  for (let r = 0; r < linearSize; r += 1) for (let c = 0; c <= linearSize; c += 1) addEdge(edgeMap, nodes, corner(r, c), corner(r + 1, c));
  for (let r = 0; r < linearSize; r += 1) for (let c = 0; c < linearSize; c += 1) {
    const mid = center(r, c); addEdge(edgeMap, nodes, mid, corner(r, c)); addEdge(edgeMap, nodes, mid, corner(r, c + 1)); addEdge(edgeMap, nodes, mid, corner(r + 1, c + 1)); addEdge(edgeMap, nodes, mid, corner(r + 1, c));
  }
  return finishGraph("cell-center-fan", linearSize, nodes, edgeMap, 4 * linearSize * linearSize, generatorSeed);
}
function triangularGraph(linearSize, generatorSeed) {
  const nodes = [], rows = [], height = Math.sqrt(3) / 2, strips = Math.floor(linearSize / height);
  for (let r = 0; r <= strips; r += 1) {
    const count = r % 2 === 0 ? linearSize + 1 : linearSize; rows[r] = [];
    for (let c = 0; c < count; c += 1) { rows[r][c] = nodes.length; nodes.push({ key: "p:" + r + ":" + c, x: c + (r % 2) / 2, y: r * height }); }
  }
  const edgeMap = new Map(); let faces = 0;
  function face(a, b, c) { addEdge(edgeMap, nodes, a, b); addEdge(edgeMap, nodes, b, c); addEdge(edgeMap, nodes, c, a); faces += 1; }
  for (let r = 0; r < strips; r += 1) {
    const lowerEven = r % 2 === 0;
    for (let c = 0; c < linearSize; c += 1) {
      if (lowerEven) face(rows[r][c], rows[r][c + 1], rows[r + 1][c]); else face(rows[r][c], rows[r + 1][c], rows[r + 1][c + 1]);
    }
    for (let c = 0; c < linearSize - 1; c += 1) {
      if (lowerEven) face(rows[r][c + 1], rows[r + 1][c + 1], rows[r + 1][c]); else face(rows[r][c], rows[r][c + 1], rows[r + 1][c + 1]);
    }
  }
  return finishGraph("triangular-clipped", linearSize, nodes, edgeMap, faces, generatorSeed);
}
function generateGraph(familyId, linearSize, generatorSeed) {
  if (familyId === "square-alternating" || familyId === "square-hashed-diagonal") return squareGraph(familyId, linearSize, generatorSeed);
  if (familyId === "cell-center-fan") return fanGraph(linearSize, generatorSeed);
  if (familyId === "triangular-clipped") return triangularGraph(linearSize, generatorSeed);
  throw new Error("unknown positive family");
}

function combGraph(linearSize, generatorSeed) {
  const tooth = Math.floor(linearSize / 4), nodes = [], edgeMap = new Map(), width = linearSize + 1;
  function id(x, y) { return y * width + x; }
  for (let y = 0; y <= tooth; y += 1) for (let x = 0; x <= linearSize; x += 1) nodes.push({ key: "comb:" + x + ":" + y, x: x, y: y });
  for (let x = 0; x < linearSize; x += 1) addEdge(edgeMap, nodes, id(x, 0), id(x + 1, 0));
  for (let x = 0; x <= linearSize; x += 1) for (let y = 0; y < tooth; y += 1) addEdge(edgeMap, nodes, id(x, y), id(x, y + 1));
  return finishGraph("comb-trap", linearSize, nodes, edgeMap, 0, generatorSeed);
}
function smallWorldGraph(linearSize, generatorSeed) {
  const base = squareGraph("square-alternating", linearSize, generatorSeed), edgeMap = new Map();
  base.edges.forEach(function (edge) { edgeMap.set(edge.u + ":" + edge.v, { u: edge.u, v: edge.v, length: edge.length, key: edge.key }); });
  const order = base.nodes.map(function (node, index) { return { index: index, score: objectUniform(generatorSeed, "shortcut-order/" + node.key, 0) }; }).sort(function (a, b) { return a.score - b.score; });
  const used = new Set(), endpointTarget = Math.floor(0.02 * base.nodes.length), targetEdges = Math.floor(endpointTarget / 2);
  let added = 0;
  for (let left = 0; left < order.length && added < targetEdges; left += 1) {
    const u = order[left].index; if (used.has(u)) continue;
    for (let right = order.length - 1; right > left; right -= 1) {
      const v = order[right].index; if (used.has(v)) continue;
      const separation = Math.abs(base.nodes[u].x - base.nodes[v].x) + Math.abs(base.nodes[u].y - base.nodes[v].y);
      if (separation < linearSize / 3) continue;
      const a = Math.min(u, v), b = Math.max(u, v);
      edgeMap.set(a + ":" + b, { u: a, v: b, length: 1, key: base.nodes[a].key + "|" + base.nodes[b].key + "|shortcut" });
      used.add(u); used.add(v); added += 1; break;
    }
  }
  const graph = finishGraph("small-world-shortcuts", linearSize, base.nodes, edgeMap, base.faceCount, generatorSeed);
  graph.controlMetadata = { shortcutDensity: 0.02, requestedEndpointCount: endpointTarget, actualShortcutCount: added, maximumEndpointsPerVertex: 1, minimumIntrinsicEndpointSeparation: linearSize / 3 };
  return graph;
}

function materializeTriangularFaces(familyId, linearSize, rawNodes, rawFaces, generatorSeed) {
  const used = new Set(); rawFaces.forEach(function (face) { face.forEach(function (vertex) { used.add(vertex); }); });
  const kept = Array.from(used).sort(function (a, b) { return a - b; }), remap = new Map(), nodes = [];
  kept.forEach(function (oldIndex, newIndex) { remap.set(oldIndex, newIndex); nodes.push(rawNodes[oldIndex]); });
  const faces = rawFaces.map(function (face) { return face.map(function (vertex) { return remap.get(vertex); }); });
  const edgeMap = new Map(), incidence = new Map();
  faces.forEach(function (face) {
    [[face[0], face[1]], [face[1], face[2]], [face[2], face[0]]].forEach(function (pair) {
      const a = Math.min(pair[0], pair[1]), b = Math.max(pair[0], pair[1]), key = a + ":" + b;
      addEdge(edgeMap, nodes, a, b); incidence.set(key, (incidence.get(key) || 0) + 1);
    });
  });
  const graph = finishGraph(familyId, linearSize, nodes, edgeMap, faces.length, generatorSeed); graph.faces = faces;
  const boundaryAdjacency = new Map();
  incidence.forEach(function (count, key) {
    if (count !== 1) return; const parts = key.split(":").map(Number), a = parts[0], b = parts[1];
    if (!boundaryAdjacency.has(a)) boundaryAdjacency.set(a, []); if (!boundaryAdjacency.has(b)) boundaryAdjacency.set(b, []);
    boundaryAdjacency.get(a).push(b); boundaryAdjacency.get(b).push(a);
  });
  let boundaryComponents = 0; const seenBoundary = new Set();
  boundaryAdjacency.forEach(function (_, start) {
    if (seenBoundary.has(start)) return; boundaryComponents += 1; const stack = [start]; seenBoundary.add(start);
    while (stack.length) { const current = stack.pop(); boundaryAdjacency.get(current).forEach(function (next) { if (!seenBoundary.has(next)) { seenBoundary.add(next); stack.push(next); } }); }
  });
  const seen = new Set([0]), stack = [0]; while (stack.length) { const current = stack.pop(); graph.adjacency[current].forEach(function (edge) { if (!seen.has(edge.to)) { seen.add(edge.to); stack.push(edge.to); } }); }
  const edgeManifold = Array.from(incidence.values()).every(function (count) { return count === 1 || count === 2; });
  const boundaryLinksValid = Array.from(boundaryAdjacency.values()).every(function (neighbors) { return neighbors.length === 2; });
  const chi = nodes.length - graph.edges.length + faces.length, beta1 = seen.size === nodes.length && edgeManifold && boundaryLinksValid ? 1 - chi : null;
  graph.controlTopology = { connected: seen.size === nodes.length, giantComponentFraction: seen.size / Math.max(1, rawNodes.length), edgeManifold: edgeManifold, boundaryLinksValid: boundaryLinksValid, boundaryComponents: boundaryComponents, eulerCharacteristic: chi, betti: beta1 === null ? null : [1, beta1, 0], validDiskWithHoles: beta1 !== null && beta1 === boundaryComponents - 1 };
  graph.structureDigest = sha256({ contract: CONSTRUCTION_CONTRACT.id, familyId: familyId, nodes: nodes.map(function (node) { return [node.key, node.x, node.y]; }), faces: faces });
  return graph;
}
function vanishingNeckGraph(linearSize, generatorSeed) {
  const rawNodes = [], nodeIndex = new Map(), faces = [], length = Math.floor(linearSize / 4), corridorY = Math.floor((linearSize - 2) / 2);
  function node(x, y) { const key = x + ":" + y; if (!nodeIndex.has(key)) { nodeIndex.set(key, rawNodes.length); rawNodes.push({ key: "neck:" + key, x: x, y: y }); } return nodeIndex.get(key); }
  function cell(x, y) {
    const sw = node(x, y), se = node(x + 1, y), ne = node(x + 1, y + 1), nw = node(x, y + 1);
    if ((x + y) % 2 === 0) faces.push([sw, se, ne], [sw, ne, nw]); else faces.push([sw, se, nw], [se, ne, nw]);
  }
  for (let x = 0; x < linearSize; x += 1) for (let y = 0; y < linearSize; y += 1) cell(x, y);
  for (let x = linearSize; x < linearSize + length; x += 1) for (let y = corridorY; y < corridorY + 2; y += 1) cell(x, y);
  for (let x = linearSize + length; x < 2 * linearSize + length; x += 1) for (let y = 0; y < linearSize; y += 1) cell(x, y);
  const graph = materializeTriangularFaces("vanishing-neck", linearSize, rawNodes, faces, generatorSeed);
  graph.controlMetadata = { patchCellSize: linearSize, corridorWidthInH: 2, corridorLengthInH: length, corridorY: corridorY };
  return graph;
}
function perforatedDiskGraph(linearSize, generatorSeed) {
  const rawNodes = [], faces = [], side = linearSize + 1;
  function id(r, c) { return r * side + c; }
  for (let r = 0; r <= linearSize; r += 1) for (let c = 0; c <= linearSize; c += 1) rawNodes.push({ key: "perforated:" + r + ":" + c, x: c, y: r });
  for (let r = 0; r < linearSize; r += 1) for (let c = 0; c < linearSize; c += 1) {
    const sw = id(r, c), se = id(r, c + 1), ne = id(r + 1, c + 1), nw = id(r + 1, c);
    if ((r + c) % 2 === 0) faces.push([sw, se, ne], [sw, ne, nw]); else faces.push([sw, se, nw], [se, ne, nw]);
  }
  const candidates = [];
  for (let r = 2; r <= linearSize - 2; r += 1) for (let c = 2; c <= linearSize - 2; c += 1) candidates.push({ r: r, c: c, vertex: id(r, c), key: r + ":" + c, score: objectUniform(generatorSeed, "hole/" + r + ":" + c, 0) });
  candidates.sort(function (a, b) { return a.score - b.score || a.r - b.r || a.c - b.c; });
  const requested = Math.floor(0.05 * linearSize * linearSize), selected = [];
  for (let i = 0; i < candidates.length && selected.length < requested; i += 1) {
    const candidate = candidates[i];
    if (selected.every(function (other) { return Math.max(Math.abs(other.r - candidate.r), Math.abs(other.c - candidate.c)) >= 3; })) selected.push(candidate);
  }
  const removed = new Set(selected.map(function (entry) { return entry.vertex; }));
  const retainedFaces = faces.filter(function (face) { return face.every(function (vertex) { return !removed.has(vertex); }); });
  const graph = materializeTriangularFaces("perforated-disk", linearSize, rawNodes, retainedFaces, generatorSeed);
  graph.controlMetadata = { holeDensity: 0.05, requestedHoleCount: requested, actualHoleCount: selected.length, minimumChebyshevCenterSeparation: 3, removedVertexKeys: selected.map(function (entry) { return entry.key; }), selectionComplete: selected.length === requested };
  return graph;
}

function weightGraph(graph, sigma, conductanceSeed) {
  const weights = graph.edges.map(function (edge) { return Math.exp(sigma * (2 * objectUniform(conductanceSeed, edge.key, 0) - 1)); });
  const degree = new Float64Array(graph.nodes.length);
  graph.edges.forEach(function (edge, index) { degree[edge.u] += weights[index]; degree[edge.v] += weights[index]; });
  return { weights: weights, degree: degree, minimum: Math.min.apply(null, weights), maximum: Math.max.apply(null, weights), digest: sha256(weights) };
}
function selectRoots(graph, rootsSeed, count) {
  const margin = graph.linearSize / 5;
  const eligible = graph.nodes.map(function (node, index) { return { node: node, index: index }; }).filter(function (entry) {
    const node = entry.node;
    return node.x - graph.bounds.minX >= margin && graph.bounds.maxX - node.x >= margin && node.y - graph.bounds.minY >= margin && graph.bounds.maxY - node.y >= margin;
  }).sort(function (a, b) { return a.node.key < b.node.key ? -1 : a.node.key > b.node.key ? 1 : 0; });
  if (eligible.length < count) throw new Error("insufficient canonical bulk roots: " + eligible.length + " < " + count);
  const offset = Math.floor(objectUniform(rootsSeed, "root-offset", 0) * eligible.length);
  let stride = 1 + Math.floor(objectUniform(rootsSeed, "root-stride", 0) * (eligible.length - 1));
  while (gcd(stride, eligible.length) !== 1) stride = stride === eligible.length - 1 ? 1 : stride + 1;
  const roots = [];
  for (let i = 0; i < count; i += 1) roots.push(eligible[(offset + i * stride) % eligible.length].index);
  return roots;
}
function selectAllCarrierRoots(graph, rootsSeed, count) {
  const eligible = graph.nodes.map(function (node, index) { return { node: node, index: index }; }).sort(function (a, b) { return a.node.key < b.node.key ? -1 : a.node.key > b.node.key ? 1 : 0; });
  if (eligible.length < count) throw new Error("control carrier has fewer than 64 roots");
  const offset = Math.floor(objectUniform(rootsSeed, "root-offset", 0) * eligible.length);
  let stride = 1 + Math.floor(objectUniform(rootsSeed, "root-stride", 0) * (eligible.length - 1));
  while (gcd(stride, eligible.length) !== 1) stride = stride === eligible.length - 1 ? 1 : stride + 1;
  const roots = []; for (let i = 0; i < count; i += 1) roots.push(eligible[(offset + i * stride) % eligible.length].index);
  return roots;
}

class MinHeap {
  constructor() { this.nodes = []; this.values = []; }
  push(node, value) { let i = this.nodes.length; this.nodes.push(node); this.values.push(value); while (i > 0) { const p = (i - 1) >> 1; if (this.values[p] <= value) break; this.nodes[i] = this.nodes[p]; this.values[i] = this.values[p]; i = p; } this.nodes[i] = node; this.values[i] = value; }
  pop() { if (!this.nodes.length) return null; const node = this.nodes[0], value = this.values[0], lastNode = this.nodes.pop(), lastValue = this.values.pop(); if (this.nodes.length) { let i = 0; while (true) { const l = 2 * i + 1, r = l + 1; if (l >= this.nodes.length) break; const c = r < this.nodes.length && this.values[r] < this.values[l] ? r : l; if (this.values[c] >= lastValue) break; this.nodes[i] = this.nodes[c]; this.values[i] = this.values[c]; i = c; } this.nodes[i] = lastNode; this.values[i] = lastValue; } return { node: node, value: value }; }
}
function dijkstraProfile(graph, root, radii, targets, workspace) {
  workspace.epoch += 1; const epoch = workspace.epoch, heap = new MinHeap();
  workspace.mark[root] = epoch; workspace.dist[root] = 0; heap.push(root, 0);
  const ordered = [], maxRadius = radii[radii.length - 1];
  while (heap.nodes.length) {
    const item = heap.pop(); if (workspace.mark[item.node] !== epoch || item.value !== workspace.dist[item.node]) continue;
    if (item.value > maxRadius + 1e-12) break; ordered.push(item.value);
    const row = graph.adjacency[item.node];
    for (let j = 0; j < row.length; j += 1) {
      const edge = row[j], candidate = item.value + edge.length;
      if (candidate > maxRadius + 1e-12) continue;
      if (workspace.mark[edge.to] !== epoch || candidate < workspace.dist[edge.to] - 1e-14) { workspace.mark[edge.to] = epoch; workspace.dist[edge.to] = candidate; heap.push(edge.to, candidate); }
    }
  }
  const counts = radii.map(function (radius) { let lo = 0, hi = ordered.length; while (lo < hi) { const mid = (lo + hi) >> 1; if (ordered[mid] <= radius + 1e-12) lo = mid + 1; else hi = mid; } return lo; });
  const targetDistances = targets.map(function (target) { return workspace.mark[target] === epoch ? workspace.dist[target] : null; });
  return { counts: counts, targetDistances: targetDistances };
}
function primaryWindow(linearSize, radii) {
  const eligible = radii.map(function (radius, index) { return { radius: radius, index: index }; }).filter(function (entry) { return entry.radius >= 4 && entry.radius <= linearSize / 5 + 1e-12; });
  const windows = [];
  for (let start = 0; start < eligible.length; start += 1) for (let end = start + 4; end < eligible.length; end += 1) {
    const subset = eligible.slice(start, end + 1); if (subset[subset.length - 1].radius / subset[0].radius >= 4 - 1e-12) windows.push(subset);
  }
  windows.sort(function (a, b) { const spanA = Math.log(a[a.length - 1].radius / a[0].radius), spanB = Math.log(b[b.length - 1].radius / b[0].radius); return spanB - spanA || a[0].radius - b[0].radius; });
  return windows.length ? windows[0].map(function (entry) { return entry.index; }) : [];
}
function layerTransportUpper(graph, weighted) {
  const xs = Array.from(new Set(graph.nodes.map(function (node) { return node.x; }))).sort(function (a, b) { return a - b; });
  const index = new Map(xs.map(function (x, i) { return [String(x), i]; }));
  const cuts = new Float64Array(Math.max(0, xs.length - 1));
  graph.edges.forEach(function (edge, edgeIndex) {
    const a = index.get(String(graph.nodes[edge.u].x)), b = index.get(String(graph.nodes[edge.v].x));
    if (a === b) return; const lo = Math.min(a, b), hi = Math.max(a, b);
    if (hi === lo + 1) cuts[lo] += weighted.weights[edgeIndex];
  });
  if (!cuts.length || Array.from(cuts).some(function (value) { return !(value > 0); })) return { available: false, reason: "disconnected layer quotient" };
  const resistance = Array.from(cuts).reduce(function (sum, value) { return sum + 1 / value; }, 0);
  return { available: true, method: "Dirichlet restricted-layer quotient", status: "CERTIFIED_UPPER_BOUND_ONLY", conductanceUpperBound: 1 / resistance, layerCount: xs.length, minimumCutConductance: Math.min.apply(null, Array.from(cuts)) };
}
function chooseWeightedNeighbor(graph, weighted, node, uniform) {
  if (uniform < 0.5) return node;
  const row = graph.adjacency[node], target = (uniform - 0.5) * 2 * weighted.degree[node]; let sum = 0;
  for (let i = 0; i < row.length; i += 1) { sum += weighted.weights[row[i].edgeIndex]; if (target <= sum) return row[i].to; }
  return row[row.length - 1].to;
}
function measurePositiveRun(manifest, namespace, familyId, sigma, linearSize, replicate, graphCache) {
  const seeds = {}; STREAMS.forEach(function (stream) { seeds[stream] = deriveStreamSeed(namespace, familyId, sigma, linearSize, replicate, stream); });
  const cacheKey = familyId + ":" + linearSize;
  let graph = familyId === "square-hashed-diagonal" ? null : graphCache.get(cacheKey);
  if (!graph) { graph = generateGraph(familyId, linearSize, seeds.generator); if (familyId !== "square-hashed-diagonal") graphCache.set(cacheKey, graph); }
  const weighted = weightGraph(graph, sigma, seeds.conductance), roots = selectRoots(graph, seeds.roots, 64);
  const rho = manifest.commonGrids.rho, radii = rho.map(function (value) { return value * linearSize; }), windowIndices = primaryWindow(linearSize, radii);
  const workspace = { dist: new Float64Array(graph.nodes.length), mark: new Int32Array(graph.nodes.length), epoch: 0 };
  const maxTime = Math.ceil(linearSize * linearSize / 25), times = TIME_GRID.filter(function (time) { return time <= maxTime; });
  const rootRows = [];
  roots.forEach(function (root) {
    let current = root, timeIndex = 0; const endpoints = [];
    for (let step = 1; step <= maxTime && timeIndex < times.length; step += 1) {
      current = chooseWeightedNeighbor(graph, weighted, current, objectUniform(seeds.dynamics, graph.nodes[root].key + "/trajectory", step));
      if (step === times[timeIndex]) { endpoints.push(current); timeIndex += 1; }
    }
    const profile = dijkstraProfile(graph, root, radii, endpoints, workspace);
    const node = graph.nodes[root], blockX = Math.min(3, Math.floor(4 * (node.x - graph.bounds.minX) / Math.max(1e-12, graph.bounds.maxX - graph.bounds.minX))), blockY = Math.min(1, Math.floor(2 * (node.y - graph.bounds.minY) / Math.max(1e-12, graph.bounds.maxY - graph.bounds.minY)));
    rootRows.push({ rootKey: node.key, spatialBlock: 2 * blockX + blockY, volumeCounts: profile.counts, walkSquaredIntrinsic: profile.targetDistances.map(function (distance) { return distance === null ? null : distance * distance; }) });
  });
  const medianProfile = radii.map(function (_, index) { return median(rootRows.map(function (row) { return row.volumeCounts[index]; })); });
  const meanProfile = radii.map(function (_, index) { return mean(rootRows.map(function (row) { return row.volumeCounts[index]; })); });
  const selectedRadii = windowIndices.map(function (index) { return radii[index]; });
  const dV = windowIndices.length ? olsLogSlope(selectedRadii, windowIndices.map(function (index) { return medianProfile[index]; })) : null;
  const dVAlternate = windowIndices.length ? olsLogSlope(selectedRadii, windowIndices.map(function (index) { return meanProfile[index]; })) : null;
  const msd = times.map(function (_, index) { return mean(rootRows.map(function (row) { return row.walkSquaredIntrinsic[index]; }).filter(function (value) { return value !== null; })); });
  const walkEligible = times.map(function (time, index) { return { time: time, index: index, rms: msd[index] === null ? Infinity : Math.sqrt(msd[index]) }; }).filter(function (entry) { return entry.time >= 8 && entry.rms <= linearSize / 5 && msd[entry.index] > 0; });
  const walkWindow = walkEligible.length >= 5 && walkEligible[walkEligible.length - 1].time / walkEligible[0].time >= 4 ? walkEligible : [];
  const walkSlope = walkWindow.length ? olsLogSlope(walkWindow.map(function (entry) { return entry.time; }), walkWindow.map(function (entry) { return msd[entry.index]; })) : null;
  const runKey = { experimentId: "ggii-u2-v2", namespace: namespace + "/", familyId: familyId, parameterCell: { sigma: sigma }, linearSize: linearSize, replicate: replicate };
  const runId = sha256({ schema: RUN_SCHEMA, runKey: runKey }), transport = layerTransportUpper(graph, weighted);
  return clone({
    schema: RUN_SCHEMA, runId: runId, runKey: runKey, seeds: seeds,
    structure: { digest: graph.structureDigest, vertices: graph.nodes.length, edges: graph.edges.length, faces: graph.faceCount, degreeMaximum: Math.max.apply(null, graph.adjacency.map(function (row) { return row.length; })) },
    sampleCounts: { constructionRealizationCount: 1, measurementBatchCount: 1, uniqueRootCount: new Set(rootRows.map(function (row) { return row.rootKey; })).size, heatProbeCount: 0, coverageClaim: false },
    conductance: { digest: weighted.digest, declaredBounds: [Math.exp(-sigma), Math.exp(sigma)], observedMinimum: weighted.minimum, observedMaximum: weighted.maximum },
    observables: {
      volume: { status: windowIndices.length ? "OK" : "NO_SCALING_WINDOW", rho: rho, radii: radii, medianCounts: medianProfile, meanCounts: meanProfile, selectedWindowIndices: windowIndices, exponent: dV, alternateExponent: dVAlternate, rootRows: rootRows.map(function (row) { return { rootKey: row.rootKey, spatialBlock: row.spatialBlock, counts: row.volumeCounts }; }) },
      walkAlternate: { status: walkWindow.length ? "OK_ALTERNATE_ONLY" : "NO_SCALING_WINDOW", method: "replay-deterministic one-trajectory-per-canonical-root lazy walk; not probability propagation", times: times, intrinsicMsd: msd, admittedIndices: walkWindow.map(function (entry) { return entry.index; }), exponent: walkSlope && walkSlope > 0 ? 2 / walkSlope : null, samplingLimitation: "one trajectory per root; descriptive only, no coverage claim, and cannot satisfy the primary deterministic-propagation atom" },
      spectralPrimary: { status: "RESOURCE_LIMIT", reason: "strict 32/64/128/256-probe certified heat estimator is not implemented in this dependency-free campaign slice" },
      transport: transport
    }, diagnostics: { status: "PARTIAL", failureCodes: ["RESOURCE_LIMIT"], exactReplay: true }
  });
}

function calibrationRecord(manifest, sourceCommit) {
  if (!/^[0-9a-f]{40}$/.test(sourceCommit || "")) throw new Error("calibration requires the final 40-hex source commit");
  const graphCache = new Map(), cells = [];
  manifest.matrix.families.forEach(function (family) {
    manifest.matrix.sigma.forEach(function (sigma) {
      const records = [];
      manifest.matrix.calibrationSizes.forEach(function (size) {
        for (let replicate = 0; replicate < manifest.matrix.calibrationReplicates; replicate += 1) {
          const seeds = {}; STREAMS.forEach(function (stream) { seeds[stream] = deriveStreamSeed("cal", family, sigma, size, replicate, stream); });
          const generatorSeed = seeds.generator, conductanceSeed = seeds.conductance;
          const key = family + ":" + size; let graph = family === "square-hashed-diagonal" ? null : graphCache.get(key);
          if (!graph) { graph = generateGraph(family, size, generatorSeed); if (family !== "square-hashed-diagonal") graphCache.set(key, graph); }
          const weighted = weightGraph(graph, sigma, conductanceSeed), transport = layerTransportUpper(graph, weighted);
          let localSecondMoment = 0, bulkCount = 0;
          graph.nodes.forEach(function (node, index) {
            if (node.x - graph.bounds.minX < size / 5 || graph.bounds.maxX - node.x < size / 5 || node.y - graph.bounds.minY < size / 5 || graph.bounds.maxY - node.y < size / 5) return;
            let stepMoment = 0; graph.adjacency[index].forEach(function (edge) { stepMoment += weighted.weights[edge.edgeIndex] * edge.length * edge.length; });
            localSecondMoment += 0.5 * stepMoment / weighted.degree[index]; bulkCount += 1;
          });
          const runKey = { experimentId: "ggii-u2-v2", namespace: "cal/", familyId: family, parameterCell: { sigma: sigma }, linearSize: size, replicate: replicate };
          records.push({ runId: sha256({ schema: RUN_SCHEMA, runKey: runKey }), runKey: runKey, size: size, replicate: replicate, seeds: seeds, structureDigest: graph.structureDigest, density: graph.nodes.length / ((graph.bounds.maxX - graph.bounds.minX) * (graph.bounds.maxY - graph.bounds.minY)), diffusivity: localSecondMoment / Math.max(1, bulkCount) / 4, conductivityUpperProxy: transport.available ? transport.conductanceUpperBound : null });
        }
      });
      const largest = records.filter(function (record) { return record.size === 36; });
      cells.push({ familyId: family, sigma: sigma, constructionRealizationCount: sigma === 0 && family !== "square-hashed-diagonal" ? 1 : 8, measurementBatchCount: 8, normalization: { bulkDensity: median(largest.map(function (record) { return record.density; })), diffusivity: median(largest.map(function (record) { return record.diffusivity; })), conductivityUpperProxy: median(largest.map(function (record) { return record.conductivityUpperProxy; }).filter(function (value) { return value !== null; })) }, records: records });
    });
  });
  const payload = { schema: CALIBRATION_SCHEMA, experimentId: "ggii-u2-v2", preregistrationCommit: PREREGISTRATION_COMMIT, sourceCommit: sourceCommit, manifestDigest: MANIFEST_DIGEST, decisionDigest: DECISION_DIGEST, namespace: "cal/", confirmatoryInputDigests: [], cells: cells };
  return Object.assign(payload, { contentAddress: contentAddress(payload) });
}

function exactGateOne() {
  const dense = [];
  [4, 6, 8].forEach(function (size) { ["square", "triangular"].forEach(function (family) { dense.push(Object.assign({ family: family, size: size }, G2.compareAnalyticAndDenseSpectrum({ family: family, rows: size, cols: size }))); }); });
  const disks = Ensembles.FAMILY_IDS.map(function (family) {
    const complex = Ensembles.generateFamily({ familyId: family, linearSize: 8, sigma: Math.log(4), streams: { generator: "u2-v2-exact/" + family + "/generator", conductance: "u2-v2-exact/" + family + "/conductance" } });
    const v = complex.metadata.exactValidation;
    return { familyId: family, betti: v.topology.betti, eulerCharacteristic: v.topology.eulerCharacteristic, boundaryComponents: v.topology.boundaryComponents, invalidVertexLinkCount: v.surface.invalidVertexLinkCount, gaussBonnetResidual: v.gaussBonnet.residual, gaussBonnetTolerance: v.gaussBonnet.tolerance, pass: v.valid && JSON.stringify(v.topology.betti) === "[1,0,0]" && v.surface.invalidVertexLinkCount === 0 && Math.abs(v.gaussBonnet.residual) < v.gaussBonnet.tolerance };
  });
  return { densePeriodic: dense, exactSmallDisks: disks, status: dense.every(function (entry) { return entry.available && entry.denseSolverConverged && entry.maxAbsolute <= 1e-10; }) && disks.every(function (entry) { return entry.pass; }) ? "PASS" : "UNRESOLVED" };
}

function bootstrapInterval(values, seed, resamples) {
  if (!values.length) return { lower: null, median: null, upper: null, count: 0 };
  const estimates = new Array(resamples);
  for (let b = 0; b < resamples; b += 1) {
    let sum = 0; for (let i = 0; i < values.length; i += 1) sum += values[Math.floor(objectUniform(seed, "bootstrap/" + b + "/" + i, 0) * values.length)]; estimates[b] = sum / values.length;
  }
  return { lower: quantile(estimates, 0.025), median: quantile(estimates, 0.5), upper: quantile(estimates, 0.975), count: values.length };
}
function aggregatePositive(manifest, runs) {
  const cells = [];
  manifest.matrix.families.forEach(function (family) { manifest.matrix.sigma.forEach(function (sigma) { manifest.matrix.confirmationSizes.forEach(function (size) {
    const members = runs.filter(function (run) { return run.runKey.familyId === family && run.runKey.parameterCell.sigma === sigma && run.runKey.linearSize === size; });
    const exponents = members.map(function (run) { return run.observables.volume.exponent; }).filter(function (value) { return value !== null; });
    const alternates = members.map(function (run) { return run.observables.volume.alternateExponent; }).filter(function (value) { return value !== null; });
    const seed = deriveStreamSeed("confirm", family, sigma, size, 0, "bootstrap");
    const weightedStructures = new Set(members.map(function (run) { return run.structure.digest + ":" + run.conductance.digest; }));
    cells.push({ familyId: family, sigma: sigma, linearSize: size, plannedRuns: 32, measurementBatchCount: 32, successfulVolumeRuns: exponents.length, constructionRealizationCount: sigma === 0 && family !== "square-hashed-diagonal" ? 1 : weightedStructures.size, duplicateWeightedStructureCount: members.length - weightedStructures.size, uniqueRootCount: new Set(members.flatMap(function (run) { return run.observables.volume.rootRows.map(function (row) { return run.structure.digest + ":" + row.rootKey; }); })).size, heatProbeCount: 0, volumeExponentInterval: bootstrapInterval(exponents, seed, 4096), alternateVolumeExponentInterval: bootstrapInterval(alternates, seed, 4096), bootstrapLimitation: "run-exponent bootstrap is descriptive; full construction/root-block/probe reselection remains unimplemented and cannot support Gate 2 PASS", primaryWalkStatus: "UNRESOLVED_NOT_IMPLEMENTED", heatStatus: "UNRESOLVED_RESOURCE_LIMIT", transportStatus: "UNRESOLVED_UPPER_BOUND_ONLY", constituentRunIds: members.map(function (run) { return run.runId; }) });
  }); }); });
  return cells;
}

function measureControlGraphDiagnostic(manifest, controlId, linearSize, replicate, graph) {
  const conductanceSeed = deriveStreamSeed("control", controlId, 0, linearSize, replicate, "conductance"), rootsSeed = deriveStreamSeed("control", controlId, 0, linearSize, replicate, "roots"), dynamicsSeed = deriveStreamSeed("control", controlId, 0, linearSize, replicate, "dynamics");
  const weighted = weightGraph(graph, 0, conductanceSeed), roots = selectAllCarrierRoots(graph, rootsSeed, 64), radii = manifest.commonGrids.rho.map(function (rho) { return rho * linearSize; }), window = primaryWindow(linearSize, radii);
  const workspace = { dist: new Float64Array(graph.nodes.length), mark: new Int32Array(graph.nodes.length), epoch: 0 }, maxTime = Math.ceil(linearSize * linearSize / 25), times = TIME_GRID.filter(function (time) { return time <= maxTime; }), rows = [];
  roots.forEach(function (root) {
    let current = root, timeIndex = 0; const endpoints = [];
    for (let step = 1; step <= maxTime && timeIndex < times.length; step += 1) {
      current = chooseWeightedNeighbor(graph, weighted, current, objectUniform(dynamicsSeed, graph.nodes[root].key + "/trajectory", step));
      if (step === times[timeIndex]) { endpoints.push(current); timeIndex += 1; }
    }
    const profile = dijkstraProfile(graph, root, radii, endpoints, workspace);
    rows.push({ counts: profile.counts, squaredDistances: profile.targetDistances.map(function (distance) { return distance === null ? null : distance * distance; }) });
  });
  const volume = radii.map(function (_, index) { return median(rows.map(function (row) { return row.counts[index]; })); }), msd = times.map(function (_, index) { return mean(rows.map(function (row) { return row.squaredDistances[index]; }).filter(function (value) { return value !== null; })); });
  const walkEligible = times.map(function (time, index) { return { time: time, index: index, rms: msd[index] === null ? Infinity : Math.sqrt(msd[index]) }; }).filter(function (entry) { return entry.time >= 8 && entry.rms <= linearSize / 5 && msd[entry.index] > 0; });
  const walkWindow = walkEligible.length >= 5 && walkEligible[walkEligible.length - 1].time / walkEligible[0].time >= 4 ? walkEligible : [];
  const slope = walkWindow.length ? olsLogSlope(walkWindow.map(function (entry) { return entry.time; }), walkWindow.map(function (entry) { return msd[entry.index]; })) : null;
  return {
    structureDigest: graph.structureDigest,
    vertices: graph.nodes.length,
    edges: graph.edges.length,
    uniqueRootCount: roots.length,
    volume: { radii: radii, medianCounts: volume, selectedWindowIndices: window, exponent: window.length ? olsLogSlope(window.map(function (index) { return radii[index]; }), window.map(function (index) { return volume[index]; })) : null },
    walkAlternate: { times: times, intrinsicMsd: msd, admittedIndices: walkWindow.map(function (entry) { return entry.index; }), exponent: slope && slope > 0 ? 2 / slope : null, status: walkWindow.length ? "OK_ALTERNATE_ONLY" : "NO_SCALING_WINDOW" }
  };
}

function measureControls(manifest) {
  const records = [], deterministicCache = new Map();
  manifest.matrix.confirmationSizes.forEach(function (size) {
    for (let replicate = 0; replicate < 32; replicate += 1) {
      let comb = deterministicCache.get("comb:" + size);
      if (!comb) { comb = combGraph(size, deriveStreamSeed("control", "comb-trap", 0, size, 0, "generator")); deterministicCache.set("comb:" + size, comb); }
      const combDiagnostic = measureControlGraphDiagnostic(manifest, "comb-trap", size, replicate, comb);
      records.push({ controlId: "comb-trap", linearSize: size, replicate: replicate, parameters: { toothLength: Math.floor(size / 4) }, constructed: true, structureWitness: { structureDigest: comb.structureDigest, vertices: comb.nodes.length, edges: comb.edges.length }, measurement: { status: "UNRESOLVED", reason: "walk alternate measured, but the required probability-propagation/exit-time strong-fail pair is incomplete", diagnostic: combDiagnostic }, countsForGate7: false });
      const shortcutSeed = deriveStreamSeed("control", "small-world-shortcuts", 0, size, replicate, "generator"), endpointCount = Math.floor(0.02 * (size + 1) * (size + 1));
      const smallWorld = smallWorldGraph(size, shortcutSeed), smallWorldDiagnostic = measureControlGraphDiagnostic(manifest, "small-world-shortcuts", size, replicate, smallWorld);
      records.push({ controlId: "small-world-shortcuts", linearSize: size, replicate: replicate, parameters: { shortcutDensity: 0.02, maximumEndpointsPerVertex: 1, minimumIntrinsicEndpointSeparation: size / 3 }, constructed: true, structureWitness: { requestedShortcutEndpointCount: endpointCount, actualShortcutCount: smallWorld.controlMetadata.actualShortcutCount, structureDigest: smallWorld.structureDigest, seed: shortcutSeed }, measurement: { status: "UNRESOLVED", reason: "metric-growth and walk alternate measured, but strong-fail hierarchical intervals and heat alternate are incomplete", diagnostic: smallWorldDiagnostic }, countsForGate7: false });
      let neck = deterministicCache.get("neck:" + size);
      if (!neck) { neck = vanishingNeckGraph(size, deriveStreamSeed("control", "vanishing-neck", 0, size, 0, "generator")); deterministicCache.set("neck:" + size, neck); }
      const neckWeighted = weightGraph(neck, 0, deriveStreamSeed("control", "vanishing-neck", 0, size, replicate, "conductance")), neckTransport = layerTransportUpper(neck, neckWeighted);
      records.push({ controlId: "vanishing-neck", linearSize: size, replicate: replicate, parameters: { corridorWidthInH: 2, corridorLengthInH: Math.floor(size / 4) }, constructed: neck.controlTopology.validDiskWithHoles && neck.controlTopology.betti[1] === 0, structureWitness: { structureDigest: neck.structureDigest, vertices: neck.nodes.length, edges: neck.edges.length, faces: neck.faces.length, topology: neck.controlTopology }, measurement: { status: neckTransport.available ? "CERTIFIED_UPPER_BOUND_DIAGNOSTIC" : "UNRESOLVED", transport: neckTransport, limitation: "not counted without calibration-normalized converged Dirichlet solve and resistance alternate" }, countsForGate7: false });
      const holeSeed = deriveStreamSeed("control", "perforated-disk", 0, size, replicate, "generator"), perforated = perforatedDiskGraph(size, holeSeed), topology = perforated.controlTopology, controlValid = perforated.controlMetadata.selectionComplete && topology.validDiskWithHoles && topology.betti[1] === perforated.controlMetadata.actualHoleCount && topology.giantComponentFraction >= 0.9;
      records.push({ controlId: "perforated-disk", linearSize: size, replicate: replicate, parameters: { holeDensity: 0.05, minimumEdgeSeparation: 3 }, constructed: controlValid, structureWitness: { structureDigest: perforated.structureDigest, requestedHoleCount: perforated.controlMetadata.requestedHoleCount, removedInteriorFaceStars: perforated.controlMetadata.removedVertexKeys, exactBetti: topology.betti, boundaryComponents: topology.boundaryComponents, eulerCharacteristic: topology.eulerCharacteristic, giantComponentFraction: topology.giantComponentFraction, surfaceValid: topology.edgeManifold && topology.boundaryLinksValid }, measurement: { status: controlValid ? "STRONG_FAIL_TOPOLOGY" : "INVALID_COMPLEX" }, countsForGate7: controlValid });
    }
  });
  const summaries = PRIMARY_CONTROLS.map(function (id) {
    const members = records.filter(function (record) { return record.controlId === id; }); let counts = false;
    if (id === "perforated-disk") counts = members.every(function (record) { return record.countsForGate7; });
    return { id: id, plannedRuns: 192, actualRuns: members.length, countsForGate7: counts, status: counts ? "FAILS_U2_AS_PREREGISTERED" : "UNRESOLVED" };
  });
  return { records: records, summaries: summaries };
}

function deriveGates(exact, cells, controls, crossPlatformStatus) {
  const volumeDecision = cells.filter(function (cell) { return cell.linearSize === 81 || cell.linearSize === 120; });
  const volumePass = volumeDecision.length === 32 && volumeDecision.every(function (cell) { const ci = cell.volumeExponentInterval; return ci.lower !== null && ci.lower > 1.8 && ci.upper < 2.2; });
  const countControls = controls.summaries.filter(function (control) { return control.countsForGate7; }).length;
  return [
    { gate: 1, status: exact.status, reason: "periodic analytic/dense spectra and four exact-small disk topology/Gauss-Bonnet certificates" },
    { gate: 2, status: "UNRESOLVED", subatoms: { dV: "UNRESOLVED", dVDescriptiveIntervalInsideMargin: volumePass, dS: "UNRESOLVED", dW: "UNRESOLVED" }, reason: "volume was evaluated descriptively, but full hierarchical root-block reselection, strict primary heat, and deterministic-propagation walk atoms are absent" },
    { gate: 3, status: "UNRESOLVED", reason: "joint volume/heat/MSD profile distances cannot be decided without the strict heat primary" },
    { gate: 4, status: "UNRESOLVED", reason: "Einstein diagnostic lacks strict dS and dW intervals" },
    { gate: 5, status: "UNRESOLVED", reason: "positive runs contain certified restricted-potential conductance upper bounds, not converged Dirichlet values and lower bounds" },
    { gate: 6, status: "UNRESOLVED", reason: "the five full paired perturbation ensembles were not executed" },
    { gate: 7, status: countControls >= 3 ? "PASS" : "UNRESOLVED", countedControls: countControls, reason: countControls + " of four primary controls meet their exact preregistered mechanism" },
    { gate: 8, status: crossPlatformStatus === "PASS" ? "PASS" : "UNRESOLVED", reason: crossPlatformStatus === "PASS" ? "full campaign records reproduced" : "independent full macOS/Windows campaign certificates are absent" }
  ];
}
function deriveConclusion(gates) {
  const validScientificFail = gates.some(function (gate) { return gate.status === "FAIL"; }) && gates.find(function (gate) { return gate.gate === 8; }).status === "PASS";
  const accepted = gates.every(function (gate) { return gate.status === "PASS"; });
  return { candidateId: "U2", hypothesisVersion: 2, status: validScientificFail ? "REJECTED" : accepted ? "ACCEPTED" : "UNRESOLVED", acceptanceAllowed: accepted, rejectionClaimed: validScientificFail, determiningAtoms: gates.filter(function (gate) { return gate.status !== "PASS"; }).map(function (gate) { return "Gate " + gate.gate + ": " + gate.reason; }) };
}

function buildCampaign(normalizationArtifact, options) {
  options = options || {};
  if (!/^[0-9a-f]{40}$/.test(options.finalSourceCommit || "")) throw new Error("campaign requires the final 40-hex source commit");
  const manifest = loadManifest(), normalizationReport = validateCalibration(normalizationArtifact);
  if (!normalizationReport.valid) throw new Error("normalization artifact invalid: " + normalizationReport.errors.join("; "));
  if (normalizationArtifact.sourceCommit !== options.finalSourceCommit) throw new Error("normalization and campaign source commits differ");
  const graphCache = new Map(), runs = [];
  manifest.matrix.families.forEach(function (family) { manifest.matrix.confirmationSizes.forEach(function (size) { manifest.matrix.sigma.forEach(function (sigma) {
    for (let replicate = 0; replicate < manifest.matrix.confirmationReplicates; replicate += 1) runs.push(measurePositiveRun(manifest, "confirm", family, sigma, size, replicate, graphCache));
  }); }); });
  const exact = exactGateOne(), cells = aggregatePositive(manifest, runs), controls = measureControls(manifest), gates = deriveGates(exact, cells, controls, "NOT_RUN"), conclusion = deriveConclusion(gates);
  const payload = { schema: RESULT_SCHEMA, engineVersion: VERSION, experimentId: "ggii-u2-v2", preregistrationCommit: PREREGISTRATION_COMMIT, finalSourceCommit: options.finalSourceCommit, manifestBinding: { path: "artifacts/global-geometry-ii/u2/experiment-manifest-v2.json", digest: MANIFEST_DIGEST, decisionId: "u2-decision-v2", decisionDigest: DECISION_DIGEST }, constructionContract: CONSTRUCTION_CONTRACT, constructionContractDigest: sha256(CONSTRUCTION_CONTRACT), normalizationBinding: normalizationArtifact.contentAddress, randomness: { id: RNG_ID, streamCount: runs.length * STREAMS.length, streamSeedCollisionCount: 0 }, counts: { plannedPositiveRuns: 3072, actualPositiveRuns: runs.length, plannedPrimaryControlRuns: 768, actualPrimaryControlRuns: controls.records.length, calibrationRuns: 384, perturbationPairsPlanned: 7680, perturbationPairsExecuted: 0 }, exactGateOne: exact, positiveRuns: runs, cells: cells, primaryControls: controls, gateResults: gates, conclusion: conclusion, evidenceBoundary: { finiteComputationsEstablished: ["exact-small topology/Gauss-Bonnet", "full positive volume profiles", "replay-deterministic lazy-walk alternate", "restricted-potential transport upper bounds", "all four primary control construction attempts and validated witnesses"], withheld: ["strict heat primary", "primary probability-propagation intrinsic MSD", "converged positive Dirichlet transport", "paired perturbation ensembles", "cross-platform full-batch replay", "universality acceptance or rejection", "continuum theorem", "physical validation"] } };
  payload.runManifestMerkleRoot = merkleRoot(runs.map(function (run) { return sha256(run); }));
  return Object.assign(payload, { contentAddress: contentAddress(payload) });
}

function validateCalibration(artifact) {
  const errors = [];
  try {
    if (!artifact || artifact.schema !== CALIBRATION_SCHEMA || artifact.experimentId !== "ggii-u2-v2" || artifact.preregistrationCommit !== PREREGISTRATION_COMMIT || !/^[0-9a-f]{40}$/.test(artifact.sourceCommit || "") || artifact.manifestDigest !== MANIFEST_DIGEST || artifact.decisionDigest !== DECISION_DIGEST) errors.push("calibration identity/binding mismatch");
    if (!artifact || artifact.namespace !== "cal/" || !denseArray(artifact.confirmatoryInputDigests) || artifact.confirmatoryInputDigests.length !== 0) errors.push("calibration/confirmation separation mismatch");
    if (!denseArray(artifact.cells) || artifact.cells.length !== 16 || artifact.cells.some(function (cell) { return !denseArray(cell.records) || cell.records.length !== 24; })) errors.push("calibration must contain 16 cells and 384 records");
    const payload = clone(artifact); const address = payload.contentAddress; delete payload.contentAddress; if (!address || canonicalStringify(address) !== canonicalStringify(contentAddress(payload))) errors.push("calibration content address mismatch");
    if (!errors.length) {
      const expected = calibrationRecord(loadManifest(), artifact.sourceCommit);
      if (canonicalStringify(artifact) !== canonicalStringify(expected)) errors.push("calibration/normalization artifact fails deterministic deep semantic replay");
    }
  } catch (error) { errors.push("calibration validation failed safely: " + error.message); }
  return { valid: errors.length === 0, errors: errors };
}
function expectedRunIdentity(run) {
  const key = run.runKey, seeds = {}; STREAMS.forEach(function (stream) { seeds[stream] = deriveStreamSeed("confirm", key.familyId, key.parameterCell.sigma, key.linearSize, key.replicate, stream); });
  return { runId: sha256({ schema: RUN_SCHEMA, runKey: key }), seeds: seeds };
}
function validateRunIdentityRecord(run) {
  try {
    const expected = expectedRunIdentity(run);
    const errors = [];
    if (run.runId !== expected.runId) errors.push("run ID mismatch");
    if (canonicalStringify(run.seeds) !== canonicalStringify(expected.seeds)) errors.push("run seeds mismatch");
    return { valid: errors.length === 0, errors: errors };
  } catch (error) { return { valid: false, errors: [error.message] }; }
}
function validateDecisionLedger(ledger) {
  try {
    const expectedGates = deriveGates(ledger.exactGateOne, ledger.cells, ledger.primaryControls, ledger.crossPlatformStatus);
    const expectedConclusion = deriveConclusion(expectedGates), errors = [];
    if (canonicalStringify(ledger.gateResults) !== canonicalStringify(expectedGates)) errors.push("gate ledger mismatch");
    if (canonicalStringify(ledger.conclusion) !== canonicalStringify(expectedConclusion)) errors.push("conclusion mismatch");
    return { valid: errors.length === 0, errors: errors };
  } catch (error) { return { valid: false, errors: [error.message] }; }
}
function validateCampaign(artifact) {
  const errors = [];
  try {
    const manifest = loadManifest();
    if (!artifact || artifact.schema !== RESULT_SCHEMA || artifact.experimentId !== manifest.experimentId || artifact.preregistrationCommit !== PREREGISTRATION_COMMIT || !/^[0-9a-f]{40}$/.test(artifact.finalSourceCommit || "") || artifact.manifestBinding.digest !== MANIFEST_DIGEST || artifact.manifestBinding.decisionId !== "u2-decision-v2" || artifact.manifestBinding.decisionDigest !== DECISION_DIGEST) errors.push("campaign manifest/decision binding mismatch");
    if (!artifact || canonicalStringify(artifact.constructionContract) !== canonicalStringify(CONSTRUCTION_CONTRACT) || artifact.constructionContractDigest !== sha256(CONSTRUCTION_CONTRACT)) errors.push("batch construction contract mismatch");
    if (!artifact.randomness || artifact.randomness.id !== RNG_ID || artifact.randomness.streamCount !== 3072 * STREAMS.length || artifact.randomness.streamSeedCollisionCount !== 0) errors.push("batch randomness/collision disclosure mismatch");
    if (!artifact.counts || artifact.counts.plannedPositiveRuns !== 3072 || artifact.counts.actualPositiveRuns !== 3072 || artifact.counts.plannedPrimaryControlRuns !== 768 || artifact.counts.actualPrimaryControlRuns !== 768 || artifact.counts.calibrationRuns !== 384) errors.push("campaign counts mismatch");
    if (!denseArray(artifact.positiveRuns) || artifact.positiveRuns.length !== 3072) errors.push("positive run ledger mismatch");
    else {
      const ids = new Set(), seeds = new Set();
      const expectedRunIds = [];
      manifest.matrix.families.forEach(function (family) { manifest.matrix.confirmationSizes.forEach(function (size) { manifest.matrix.sigma.forEach(function (sigma) { for (let replicate = 0; replicate < 32; replicate += 1) {
        const runKey = { experimentId: "ggii-u2-v2", namespace: "confirm/", familyId: family, parameterCell: { sigma: sigma }, linearSize: size, replicate: replicate };
        expectedRunIds.push(sha256({ schema: RUN_SCHEMA, runKey: runKey }));
      } }); }); });
      if (canonicalStringify(artifact.positiveRuns.map(function (run) { return run.runId; })) !== canonicalStringify(expectedRunIds)) errors.push("positive run enumeration/order mismatch");
      artifact.positiveRuns.forEach(function (run, index) {
        const expected = expectedRunIdentity(run);
        if (run.runId !== expected.runId) errors.push("run " + index + " ID mismatch");
        if (canonicalStringify(run.seeds) !== canonicalStringify(expected.seeds)) errors.push("run " + index + " seed mismatch");
        ids.add(run.runId); Object.values(run.seeds).forEach(function (seed) { seeds.add(seed); });
        const volume = run.observables && run.observables.volume;
        const recomputed = volume && volume.selectedWindowIndices.length ? olsLogSlope(volume.selectedWindowIndices.map(function (i) { return volume.radii[i]; }), volume.selectedWindowIndices.map(function (i) { return volume.medianCounts[i]; })) : null;
        if (!volume || volume.exponent !== recomputed) errors.push("run " + index + " volume exponent mismatch");
      });
      if (ids.size !== 3072) errors.push("duplicate run ID");
      if (seeds.size !== 3072 * STREAMS.length) errors.push("duplicate effective stream seed");
      if (merkleRoot(artifact.positiveRuns.map(function (run) { return sha256(run); })) !== artifact.runManifestMerkleRoot) errors.push("run Merkle root mismatch");
      const expectedCells = aggregatePositive(manifest, artifact.positiveRuns);
      if (canonicalStringify(artifact.cells) !== canonicalStringify(expectedCells)) errors.push("cell summaries do not regenerate from immutable positive runs");

      const replayCache = new Map();
      artifact.positiveRuns.filter(function (run) { return run.runKey.replicate === 0; }).forEach(function (run) {
        const key = run.runKey;
        const replay = measurePositiveRun(manifest, "confirm", key.familyId, key.parameterCell.sigma, key.linearSize, key.replicate, replayCache);
        if (canonicalStringify(run) !== canonicalStringify(replay)) errors.push("semantic replay mismatch for sampled run " + run.runId);
      });
    }
    if (!artifact.primaryControls || !denseArray(artifact.primaryControls.summaries) || canonicalStringify(artifact.primaryControls.summaries.map(function (control) { return control.id; })) !== canonicalStringify(PRIMARY_CONTROLS)) errors.push("primary control set/order mismatch");
    if (!artifact.primaryControls || !denseArray(artifact.primaryControls.records) || artifact.primaryControls.records.length !== 768) errors.push("primary control record count mismatch");
    else artifact.primaryControls.records.forEach(function (record) {
      if (PRIMARY_CONTROLS.indexOf(record.controlId) < 0 || !record.constructed) errors.push("invalid control witness");
      if (record.controlId === "vanishing-neck" && (record.parameters.corridorWidthInH !== 2 || record.parameters.corridorLengthInH !== Math.floor(record.linearSize / 4))) errors.push("vanishing-neck witness mismatch");
      if (record.controlId === "perforated-disk" && (record.parameters.holeDensity !== 0.05 || record.parameters.minimumEdgeSeparation !== 3 || !record.structureWitness || !Array.isArray(record.structureWitness.exactBetti) || record.structureWitness.exactBetti[1] !== record.structureWitness.removedInteriorFaceStars.length || record.countsForGate7 !== (record.constructed && record.measurement.status === "STRONG_FAIL_TOPOLOGY"))) errors.push("perforated-disk witness mismatch");
    });
    const expectedExact = exactGateOne(); if (canonicalStringify(artifact.exactGateOne) !== canonicalStringify(expectedExact)) errors.push("Gate 1 record does not replay independently");
    const expectedSummaries = PRIMARY_CONTROLS.map(function (id) {
      const members = artifact.primaryControls.records.filter(function (record) { return record.controlId === id; });
      const counts = id === "perforated-disk" && members.length === 192 && members.every(function (record) { return record.countsForGate7; });
      return { id: id, plannedRuns: 192, actualRuns: members.length, countsForGate7: counts, status: counts ? "FAILS_U2_AS_PREREGISTERED" : "UNRESOLVED" };
    });
    if (canonicalStringify(artifact.primaryControls.summaries) !== canonicalStringify(expectedSummaries)) errors.push("control summaries do not derive from all control witnesses");
    const replayedControls = measureControls(manifest);
    if (canonicalStringify(artifact.primaryControls) !== canonicalStringify(replayedControls)) errors.push("primary control records fail deterministic deep semantic replay");
    const derivedGates = deriveGates(artifact.exactGateOne, artifact.cells, artifact.primaryControls, "NOT_RUN");
    if (canonicalStringify(artifact.gateResults) !== canonicalStringify(derivedGates)) errors.push("gate ledger is not mechanically derived");
    const derivedConclusion = deriveConclusion(derivedGates); if (canonicalStringify(artifact.conclusion) !== canonicalStringify(derivedConclusion)) errors.push("conclusion is not mechanically derived");
    const payload = clone(artifact); const address = payload.contentAddress; delete payload.contentAddress; if (!address || canonicalStringify(address) !== canonicalStringify(contentAddress(payload))) errors.push("campaign content address mismatch");
  } catch (error) { errors.push("campaign validation failed safely: " + error.message); }
  return { valid: errors.length === 0, errors: errors };
}

module.exports = {
  VERSION: VERSION, RNG_ID: RNG_ID, RUN_SCHEMA: RUN_SCHEMA, CALIBRATION_SCHEMA: CALIBRATION_SCHEMA, RESULT_SCHEMA: RESULT_SCHEMA,
  CONSTRUCTION_CONTRACT: CONSTRUCTION_CONTRACT,
  MANIFEST_PATH: MANIFEST_PATH, MANIFEST_DIGEST: MANIFEST_DIGEST, DECISION_DIGEST: DECISION_DIGEST, PREREGISTRATION_COMMIT: PREREGISTRATION_COMMIT,
  STREAMS: STREAMS, PRIMARY_CONTROLS: PRIMARY_CONTROLS, TIME_GRID: TIME_GRID,
  canonicalStringify: canonicalStringify, sha256: sha256, contentAddress: contentAddress, merkleRoot: merkleRoot,
  loadManifest: loadManifest, deriveStreamSeed: deriveStreamSeed, objectUniform: objectUniform,
  generateGraph: generateGraph, combGraph: combGraph, smallWorldGraph: smallWorldGraph, vanishingNeckGraph: vanishingNeckGraph, perforatedDiskGraph: perforatedDiskGraph,
  weightGraph: weightGraph, selectRoots: selectRoots, primaryWindow: primaryWindow,
  measurePositiveRun: measurePositiveRun, calibrationRecord: calibrationRecord, validateCalibration: validateCalibration,
  exactGateOne: exactGateOne, bootstrapInterval: bootstrapInterval, aggregatePositive: aggregatePositive,
  measureControls: measureControls, deriveGates: deriveGates, deriveConclusion: deriveConclusion,
  buildCampaign: buildCampaign, validateCampaign: validateCampaign
  ,validateRunIdentityRecord: validateRunIdentityRecord, validateDecisionLedger: validateDecisionLedger
};
