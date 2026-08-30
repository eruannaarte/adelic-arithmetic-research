/*
 * Global Geometry II — preregistered U2 screening evaluator.
 *
 * This dependency-free Node module is intentionally separate from the U2
 * decision implementation.  Its lower-cost measurements are outcome-bearing
 * screens, never decision-gate substitutes.  See screening-manifest-v1.json.
 */
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "../..");
const MANIFEST_PATH = path.join(ROOT, "artifacts/global-geometry-ii/u2/screening/screening-manifest-v1.json");
const EXPECTED_MANIFEST_FILE_SHA256 = "2b60f5ca51bfa37c7de068b92928c17664b36f81ff931a8851316b47f135cc25";
const EXPECTED_MANIFEST_SEMANTIC_SHA256 = "25fea0bad6f4b60ae27a75fd13c13be117c28a288a5f6b3bd9e25859c4b1d309";
const SUPPLEMENT_PATH = path.join(ROOT, "artifacts/global-geometry-ii/u2/screening/screening-implementation-supplement-v2.json");
const EXPECTED_SUPPLEMENT_FILE_SHA256 = "5380552dc7c6ee91d6e632b7bfec6a6031d49ab0b98a2aa6f95b71b4c73ab8d6";
const EXPECTED_SUPPLEMENT_SEMANTIC_SHA256 = "7d948db5996eb025c949d1bdfe73ce8cf29b10a77904ca2558b1a6d601301b8c";
const PREREGISTRATION_COMMIT = "150e4e7";
const FAMILIES = Object.freeze(["square-alternating", "triangular-clipped", "cell-center-fan", "square-hashed-diagonal"]);
const SIZES = Object.freeze([16, 24, 36, 54, 81, 120]);
const SIGMAS = Object.freeze([0, 0.25, 0.75, Math.log(4)]);
const CONTROLS = Object.freeze(["comb-trap", "small-world-shortcuts", "vanishing-neck", "perforated-disk"]);
const RHOS = Object.freeze([1 / 32, 1 / 24, 1 / 20, 1 / 16, 1 / 12, 1 / 8, 1 / 6, 1 / 5]);
const WALK_TIMES = Object.freeze([8, 16, 32, 64, 128, 256]);

function canonicalStringify(value) {
  if (value === null || typeof value === "string" || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "number") {
    if (!Number.isFinite(value) || Object.is(value, -0)) throw new Error("invalid canonical number");
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return "[" + value.map(canonicalStringify).join(",") + "]";
  if (!value || typeof value !== "object" || Object.getPrototypeOf(value) !== Object.prototype) throw new Error("canonical values must be plain JSON");
  return "{" + Object.keys(value).sort().map(function (key) {
    return JSON.stringify(key) + ":" + canonicalStringify(value[key]);
  }).join(",") + "}";
}

function sha256Bytes(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function sha256JSON(value) { return sha256Bytes(Buffer.from(canonicalStringify(value), "utf8")); }

function loadManifest() {
  const bytes = fs.readFileSync(MANIFEST_PATH);
  if (sha256Bytes(bytes) !== EXPECTED_MANIFEST_FILE_SHA256) throw new Error("frozen screening manifest file digest mismatch");
  const manifest = JSON.parse(bytes.toString("utf8"));
  if (!manifest.contentAddress || manifest.contentAddress.digest !== EXPECTED_MANIFEST_SEMANTIC_SHA256) throw new Error("frozen screening manifest semantic digest mismatch");
  if (!manifest.freezeStatus || manifest.freezeStatus.forcedU2Status !== "UNRESOLVED") throw new Error("screening manifest is not fail-closed");
  const supplementBytes = fs.readFileSync(SUPPLEMENT_PATH);
  if (sha256Bytes(supplementBytes) !== EXPECTED_SUPPLEMENT_FILE_SHA256) throw new Error("frozen screening supplement file digest mismatch");
  const supplement = JSON.parse(supplementBytes.toString("utf8"));
  if (!supplement.contentAddress || supplement.contentAddress.digest !== EXPECTED_SUPPLEMENT_SEMANTIC_SHA256 || !supplement.status || supplement.status.forcedU2Status !== "UNRESOLVED") throw new Error("frozen screening supplement semantic digest mismatch");
  return { manifest: manifest, supplement: supplement };
}

function deriveSeed(namespace, id, size, sigmaIndex, replicate, role) {
  return sha256JSON(["ggii-u2-v2-screening-v1", namespace, id, size, sigmaIndex, replicate, role]);
}

function u53(streamSeed, objectCanonicalKey, counter) {
  const digest = crypto.createHash("sha256").update(canonicalStringify([streamSeed, objectCanonicalKey, counter])).digest();
  const high32 = digest.readUInt32BE(0);
  const next21 = digest.readUInt32BE(4) >>> 11;
  return (high32 * 2097152 + next21) / 9007199254740992;
}

function clean(value) {
  if (typeof value !== "number") return value;
  if (!Number.isFinite(value)) return null;
  if (Object.is(value, -0) || Math.abs(value) < 1e-15) return 0;
  return value;
}

function mean(values) {
  return values.length ? values.reduce(function (sum, value) { return sum + value; }, 0) / values.length : null;
}

function median(values) {
  if (!values.length) return null;
  const sorted = values.slice().sort(function (a, b) { return a - b; });
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

function descriptiveTWidth(values, critical) {
  if (values.length < 2) return { count: values.length, mean: values.length ? clean(values[0]) : null, descriptiveLower: null, descriptiveUpper: null, descriptiveHalfWidth: null, standardError: null, criticalMultiplier: critical, label: "descriptive finite-sample t-width only; not a confidence interval and not a coverage guarantee" };
  const center = mean(values);
  const variance = values.reduce(function (sum, value) { const delta = value - center; return sum + delta * delta; }, 0) / (values.length - 1);
  const standardError = Math.sqrt(variance / values.length);
  return { count: values.length, mean: clean(center), descriptiveLower: clean(center - critical * standardError), descriptiveUpper: clean(center + critical * standardError), descriptiveHalfWidth: clean(critical * standardError), standardError: clean(standardError), criticalMultiplier: critical, label: "descriptive finite-sample t-width only; not a confidence interval and not a coverage guarantee" };
}

function olsSlope(xs, ys) {
  if (xs.length !== ys.length || xs.length < 2) return null;
  const mx = mean(xs), my = mean(ys);
  let numerator = 0, denominator = 0;
  for (let index = 0; index < xs.length; index += 1) {
    numerator += (xs[index] - mx) * (ys[index] - my);
    denominator += (xs[index] - mx) * (xs[index] - mx);
  }
  return denominator > 0 ? clean(numerator / denominator) : null;
}

class DSU {
  constructor(size) {
    this.parent = new Int32Array(size);
    this.rank = new Uint8Array(size);
    for (let index = 0; index < size; index += 1) this.parent[index] = index;
  }
  find(value) {
    let root = value;
    while (this.parent[root] !== root) root = this.parent[root];
    while (this.parent[value] !== value) { const next = this.parent[value]; this.parent[value] = root; value = next; }
    return root;
  }
  union(a, b) {
    a = this.find(a); b = this.find(b);
    if (a === b) return;
    if (this.rank[a] < this.rank[b]) { const swap = a; a = b; b = swap; }
    this.parent[b] = a;
    if (this.rank[a] === this.rank[b]) this.rank[a] += 1;
  }
}

function vertex(key, x, y) { return { key: key, x: x, y: y }; }
function signedArea(a, b, c) { return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x); }

function orientFaces(vertices, faces) {
  return faces.map(function (face) {
    const area = signedArea(vertices[face[0]], vertices[face[1]], vertices[face[2]]);
    if (area === 0) throw new Error("degenerate face in constructed carrier");
    return area > 0 ? face : [face[0], face[2], face[1]];
  });
}

function finalizeGraph(id, size, vertices, faces, standaloneEdges, metadata) {
  faces = orientFaces(vertices, faces || []);
  const edgeMap = new Map();
  function ensureEdge(a, b) {
    const u = Math.min(a, b), v = Math.max(a, b), key = u + ":" + v;
    if (!edgeMap.has(key)) edgeMap.set(key, { u: u, v: v, key: vertices[u].key + "|" + vertices[v].key, incidents: [], signs: [] });
    return edgeMap.get(key);
  }
  faces.forEach(function (face, faceIndex) {
    [[face[0], face[1]], [face[1], face[2]], [face[2], face[0]]].forEach(function (directed) {
      const edge = ensureEdge(directed[0], directed[1]);
      edge.incidents.push(faceIndex);
      edge.signs.push(directed[0] < directed[1] ? 1 : -1);
    });
  });
  (standaloneEdges || []).forEach(function (edge) { ensureEdge(edge[0], edge[1]); });
  const edges = Array.from(edgeMap.values()).sort(function (a, b) { return a.u - b.u || a.v - b.v; });
  const adjacency = Array.from({ length: vertices.length }, function () { return []; });
  edges.forEach(function (edge, index) {
    adjacency[edge.u].push({ to: edge.v, edge: index });
    adjacency[edge.v].push({ to: edge.u, edge: index });
  });
  adjacency.forEach(function (row) { row.sort(function (a, b) { return a.to - b.to; }); });
  return { id: id, size: size, vertices: vertices, edges: edges, faces: faces, adjacency: adjacency, metadata: metadata || {} };
}

function buildSquareCarrier(id, size, structureSeed, diagonalOracle) {
  const vertices = [];
  function at(x, y) { return y * (size + 1) + x; }
  for (let y = 0; y <= size; y += 1) for (let x = 0; x <= size; x += 1) vertices.push(vertex("p:" + y + ":" + x, x, y));
  const faces = [], randomValues = new Set(), randomCollisions = { draws: 0, duplicates: 0 };
  for (let y = 0; y < size; y += 1) {
    for (let x = 0; x < size; x += 1) {
      const sw = at(x, y), se = at(x + 1, y), ne = at(x + 1, y + 1), nw = at(x, y + 1);
      let forward = (x + y) % 2 === 0;
      if (id === "square-hashed-diagonal") {
        if (typeof diagonalOracle === "function") {
          forward = diagonalOracle(x, y) === true;
        } else {
          const draw = u53(structureSeed, "cell:" + y + ":" + x, 0);
          randomCollisions.draws += 1;
          if (randomValues.has(draw)) randomCollisions.duplicates += 1;
          randomValues.add(draw);
          forward = draw < 0.5;
        }
      }
      if (forward) faces.push([sw, se, ne], [sw, ne, nw]);
      else faces.push([sw, se, nw], [se, ne, nw]);
    }
  }
  return finalizeGraph(id, size, vertices, faces, [], { constructionRandomAudit: randomCollisions });
}

function buildCellCenterCarrier(size) {
  const vertices = [];
  function corner(x, y) { return y * (size + 1) + x; }
  for (let y = 0; y <= size; y += 1) for (let x = 0; x <= size; x += 1) vertices.push(vertex("p:" + (2 * y) + ":" + (2 * x), x, y));
  const firstCenter = vertices.length;
  function center(x, y) { return firstCenter + y * size + x; }
  for (let y = 0; y < size; y += 1) for (let x = 0; x < size; x += 1) vertices.push(vertex("c:" + y + ":" + x, x + 0.5, y + 0.5));
  const faces = [];
  for (let y = 0; y < size; y += 1) {
    for (let x = 0; x < size; x += 1) {
      const sw = corner(x, y), se = corner(x + 1, y), ne = corner(x + 1, y + 1), nw = corner(x, y + 1), c = center(x, y);
      faces.push([sw, se, c], [se, ne, c], [ne, nw, c], [nw, sw, c]);
    }
  }
  return finalizeGraph("cell-center-fan", size, vertices, faces, [], { constructionRandomAudit: { draws: 0, duplicates: 0 } });
}

function buildTriangularCarrier(size) {
  const vertices = [], rowIds = [];
  const height = Math.sqrt(3) / 2;
  const strips = Math.floor(size / height);
  for (let row = 0; row <= strips; row += 1) {
    rowIds[row] = [];
    const columns = row % 2 === 0 ? size + 1 : size;
    for (let column = 0; column < columns; column += 1) {
      rowIds[row][column] = vertices.length;
      vertices.push(vertex("p:" + row + ":" + column, column + (row % 2) / 2, row * height));
    }
  }
  const faces = [];
  for (let strip = 0; strip < strips; strip += 1) {
    const lowerEven = strip % 2 === 0;
    for (let index = 0; index < size; index += 1) {
      if (lowerEven) faces.push([rowIds[strip][index], rowIds[strip][index + 1], rowIds[strip + 1][index]]);
      else faces.push([rowIds[strip][index], rowIds[strip + 1][index], rowIds[strip + 1][index + 1]]);
    }
    for (let bridge = 0; bridge < size - 1; bridge += 1) {
      if (lowerEven) faces.push([rowIds[strip][bridge + 1], rowIds[strip + 1][bridge + 1], rowIds[strip + 1][bridge]]);
      else faces.push([rowIds[strip][bridge], rowIds[strip][bridge + 1], rowIds[strip + 1][bridge + 1]]);
    }
  }
  return finalizeGraph("triangular-clipped", size, vertices, faces, [], { strips: strips, constructionRandomAudit: { draws: 0, duplicates: 0 } });
}

function buildPositive(family, size, structureSeed, options) {
  options = options || {};
  if (family === "square-alternating" || family === "square-hashed-diagonal") return buildSquareCarrier(family, size, structureSeed, options.diagonalOracle);
  if (family === "cell-center-fan") return buildCellCenterCarrier(size);
  if (family === "triangular-clipped") return buildTriangularCarrier(size);
  throw new Error("unknown positive family " + family);
}

function boundsOf(graph) {
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  graph.vertices.forEach(function (item) { minX = Math.min(minX, item.x); maxX = Math.max(maxX, item.x); minY = Math.min(minY, item.y); maxY = Math.max(maxY, item.y); });
  return { minX: minX, maxX: maxX, minY: minY, maxY: maxY, diameter: Math.hypot(maxX - minX, maxY - minY) };
}

function graphStructureDigest(graph) {
  const hash = crypto.createHash("sha256");
  hash.update("gg-u2-screen-graph-v1\n" + graph.id + "\n" + graph.size + "\n");
  graph.vertices.forEach(function (item) { hash.update("v\t" + item.key + "\t" + item.x + "\t" + item.y + "\n"); });
  graph.edges.forEach(function (edge) { hash.update("e\t" + graph.vertices[edge.u].key + "\t" + graph.vertices[edge.v].key + "\n"); });
  graph.faces.forEach(function (face) { hash.update("f\t" + face.map(function (index) { return graph.vertices[index].key; }).join("\t") + "\n"); });
  return hash.digest("hex");
}

function componentData(graph) {
  const dsu = new DSU(graph.vertices.length);
  graph.edges.forEach(function (edge) { dsu.union(edge.u, edge.v); });
  const counts = new Map();
  for (let index = 0; index < graph.vertices.length; index += 1) {
    const root = dsu.find(index); counts.set(root, (counts.get(root) || 0) + 1);
  }
  return { count: counts.size, largest: Math.max.apply(null, Array.from(counts.values())), dsu: dsu };
}

function analyzeGraph(graph) {
  const component = componentData(graph);
  const degrees = graph.adjacency.map(function (row) { return row.length; });
  const boundaryEdges = graph.edges.filter(function (edge) { return edge.incidents.length === 1; });
  const invalidIncidences = graph.edges.filter(function (edge) { return graph.faces.length && (edge.incidents.length < 1 || edge.incidents.length > 2); }).length;
  const orientationMismatchCount = graph.edges.filter(function (edge) { return edge.incidents.length === 2 && edge.signs[0] + edge.signs[1] !== 0; }).length;
  let boundaryComponents = 0, boundaryDegreeValid = true;
  const boundaryVertices = new Set();
  if (boundaryEdges.length) {
    const boundaryAdj = new Map();
    boundaryEdges.forEach(function (edge) {
      boundaryVertices.add(edge.u); boundaryVertices.add(edge.v);
      if (!boundaryAdj.has(edge.u)) boundaryAdj.set(edge.u, []);
      if (!boundaryAdj.has(edge.v)) boundaryAdj.set(edge.v, []);
      boundaryAdj.get(edge.u).push(edge.v); boundaryAdj.get(edge.v).push(edge.u);
    });
    boundaryDegreeValid = Array.from(boundaryAdj.values()).every(function (row) { return row.length === 2; });
    const seen = new Set();
    boundaryAdj.forEach(function (_, start) {
      if (seen.has(start)) return;
      boundaryComponents += 1;
      const stack = [start]; seen.add(start);
      while (stack.length) boundaryAdj.get(stack.pop()).forEach(function (next) { if (!seen.has(next)) { seen.add(next); stack.push(next); } });
    });
  }

  let faceComponentCount = graph.faces.length ? graph.faces.length : 0;
  if (graph.faces.length) {
    const faceDsu = new DSU(graph.faces.length);
    graph.edges.forEach(function (edge) { if (edge.incidents.length === 2) faceDsu.union(edge.incidents[0], edge.incidents[1]); });
    const roots = new Set(); for (let index = 0; index < graph.faces.length; index += 1) roots.add(faceDsu.find(index));
    faceComponentCount = roots.size;
  }

  let invalidVertexLinks = 0;
  if (graph.faces.length) {
    const linkEdges = Array.from({ length: graph.vertices.length }, function () { return []; });
    graph.faces.forEach(function (face) {
      linkEdges[face[0]].push([face[1], face[2]]);
      linkEdges[face[1]].push([face[2], face[0]]);
      linkEdges[face[2]].push([face[0], face[1]]);
    });
    linkEdges.forEach(function (pairs, vertexIndex) {
      if (!pairs.length) { invalidVertexLinks += 1; return; }
      const adjacency = new Map();
      pairs.forEach(function (pair) {
        if (!adjacency.has(pair[0])) adjacency.set(pair[0], []);
        if (!adjacency.has(pair[1])) adjacency.set(pair[1], []);
        adjacency.get(pair[0]).push(pair[1]); adjacency.get(pair[1]).push(pair[0]);
      });
      const keys = Array.from(adjacency.keys()), seen = new Set([keys[0]]), stack = [keys[0]];
      while (stack.length) adjacency.get(stack.pop()).forEach(function (next) { if (!seen.has(next)) { seen.add(next); stack.push(next); } });
      const counts = Array.from(adjacency.values()).map(function (row) { return row.length; });
      const expected = boundaryVertices.has(vertexIndex)
        ? counts.filter(function (degree) { return degree === 1; }).length === 2 && counts.every(function (degree) { return degree === 1 || degree === 2; })
        : counts.every(function (degree) { return degree === 2; });
      if (seen.size !== keys.length || !expected) invalidVertexLinks += 1;
    });
  }

  const eulerCharacteristic = graph.vertices.length - graph.edges.length + graph.faces.length;
  const surfaceWitnessValid = graph.faces.length > 0 && component.count === 1 && invalidIncidences === 0 && boundaryEdges.length > 0 && boundaryDegreeValid && faceComponentCount === 1 && invalidVertexLinks === 0 && orientationMismatchCount === 0;
  const exactBetti = surfaceWitnessValid
    ? { beta0: 1, beta1: 1 - eulerCharacteristic, beta2: 0, derivation: "validated connected orientable triangulated surface with nonempty manifold boundary plus Euler-Poincare" }
    : null;
  return {
    public: {
      counts: { vertices: graph.vertices.length, edges: graph.edges.length, faces: graph.faces.length },
      connectedComponents: component.count,
      largestComponentFraction: clean(component.largest / graph.vertices.length),
      degree: { minimum: Math.min.apply(null, degrees), maximum: Math.max.apply(null, degrees), mean: clean(mean(degrees)) },
      eulerCharacteristic: eulerCharacteristic,
      graphCycleRank: graph.edges.length - graph.vertices.length + component.count,
      boundary: { edgeCount: boundaryEdges.length, componentCount: boundaryComponents, allBoundaryDegreesTwo: boundaryDegreeValid },
      surfaceWitness: {
        applicable: graph.faces.length > 0,
        valid: surfaceWitnessValid,
        invalidEdgeIncidenceCount: invalidIncidences,
        faceComponentCount: faceComponentCount,
        invalidVertexLinkCount: invalidVertexLinks,
        orientationMismatchCount: orientationMismatchCount,
        exactBetti: exactBetti
      },
      structureDigest: graphStructureDigest(graph),
      bounds: boundsOf(graph)
    },
    boundaryVertices: Array.from(boundaryVertices)
  };
}

function bfsDistances(graph, sources) {
  const distances = new Int32Array(graph.vertices.length); distances.fill(-1);
  const queue = new Int32Array(graph.vertices.length); let head = 0, tail = 0;
  sources.forEach(function (source) { if (distances[source] < 0) { distances[source] = 0; queue[tail++] = source; } });
  while (head < tail) {
    const current = queue[head++], nextDistance = distances[current] + 1;
    graph.adjacency[current].forEach(function (neighbor) { if (distances[neighbor.to] < 0) { distances[neighbor.to] = nextDistance; queue[tail++] = neighbor.to; } });
  }
  return distances;
}

function coordinateBoundaryVertices(graph, bounds) {
  const epsilon = 1e-12;
  const out = [];
  graph.vertices.forEach(function (item, index) {
    if (Math.abs(item.x - bounds.minX) < epsilon || Math.abs(item.x - bounds.maxX) < epsilon || Math.abs(item.y - bounds.minY) < epsilon || Math.abs(item.y - bounds.maxY) < epsilon) out.push(index);
  });
  return out;
}

function volumeMeasurement(graph, analysis, rootSeed) {
  const bounds = analysis.public.bounds;
  const radii = Array.from(new Set(RHOS.map(function (rho) { return Math.max(1, Math.floor(rho * bounds.diameter)); }))).sort(function (a, b) { return a - b; });
  const maxRadius = radii[radii.length - 1];
  const boundarySources = analysis.boundaryVertices.length ? analysis.boundaryVertices : coordinateBoundaryVertices(graph, bounds);
  const boundaryDistance = bfsDistances(graph, boundarySources);
  const ranked = [];
  graph.vertices.forEach(function (item, index) {
    if (boundaryDistance[index] >= maxRadius) ranked.push({ index: index, key: item.key, rank: u53(rootSeed, item.key, 0) });
  });
  ranked.sort(function (a, b) { return a.rank - b.rank || (a.key < b.key ? -1 : 1); });
  const roots = ranked.slice(0, 8);
  if (roots.length < 8) return { public: { status: "INSUFFICIENT_BULK_ROOTS", eligibleRootCount: ranked.length, requiredRootCount: 8, radii: radii }, rootIds: [], rootDistances: [] };
  const profiles = [], exponents = [], rootDistances = [];
  roots.forEach(function (root) {
    const distances = bfsDistances(graph, [root.index]); rootDistances.push(distances);
    const counts = radii.map(function (radius) {
      let count = 0; for (let index = 0; index < distances.length; index += 1) if (distances[index] >= 0 && distances[index] <= radius) count += 1;
      return count;
    });
    const slope = olsSlope(radii.map(Math.log), counts.map(Math.log));
    if (slope != null) exponents.push(slope);
    profiles.push({ rootKey: root.key, boundaryDistance: boundaryDistance[root.index], counts: counts, exponent: slope });
  });
  const meanCounts = radii.map(function (_, index) { return clean(mean(profiles.map(function (profile) { return profile.counts[index]; }))); });
  return {
    public: {
      status: radii.length >= 3 ? "MEASURED_SCREENING_ONLY" : "INSUFFICIENT_VOLUME_WINDOW",
      metric: "unweighted-graph-hop",
      rootCount: roots.length,
      eligibleRootCount: ranked.length,
      radii: radii,
      meanBallCounts: meanCounts,
      rootProfiles: profiles,
      logLogSlopeDescriptor: clean(olsSlope(radii.map(Math.log), meanCounts.map(Math.log))),
      rootBlockSlopeDescriptiveTWidth: descriptiveTWidth(exponents, 2.365),
      samplingNote: "Eight-root graph-hop ball-growth smoke descriptor only; not a dimension estimate or exponent confidence interval."
    },
    rootIds: roots.map(function (root) { return root.index; }),
    rootDistances: rootDistances
  };
}

function conductanceMeasurement(graph, conductanceSeed, sigma) {
  const weights = new Float64Array(graph.edges.length), values = new Set();
  let minimum = Infinity, maximum = -Infinity, sum = 0, sumLog = 0, duplicateU53Count = 0, drawCount = 0;
  const lower = Math.exp(-sigma), upper = Math.exp(sigma), hash = crypto.createHash("sha256");
  graph.edges.forEach(function (edge, index) {
    let draw = null, weight = 1;
    if (sigma > 0) {
      draw = u53(conductanceSeed, edge.key, 0); drawCount += 1;
      if (values.has(draw)) duplicateU53Count += 1; values.add(draw);
      weight = Math.exp(sigma * (2 * draw - 1));
    }
    weights[index] = weight; minimum = Math.min(minimum, weight); maximum = Math.max(maximum, weight); sum += weight; sumLog += Math.log(weight);
    hash.update(edge.key + "\t" + weight.toString() + "\n");
  });
  const boundResidual = Math.max(0, lower - minimum, maximum - upper);
  return {
    weights: weights,
    public: {
      law: "quenched-log-uniform-conductance",
      sigma: sigma,
      declaredBounds: [clean(lower), clean(upper)],
      observedMinimum: clean(minimum),
      observedMaximum: clean(maximum),
      arithmeticMean: clean(sum / graph.edges.length),
      geometricMean: clean(Math.exp(sumLog / graph.edges.length)),
      strictlyPositive: minimum > 0,
      boundResidual: clean(boundResidual),
      everyEdgeEvaluated: true,
      weightDigest: hash.digest("hex"),
      randomAudit: { algorithm: "gg-sha256-object-u53-v1", drawCount: drawCount, duplicateU53Count: duplicateU53Count, deterministicIrrelevantDrawCount: sigma === 0 ? graph.edges.length : 0 }
    }
  };
}

function weightedWalkMeasurement(graph, weights, rootIds, rootDistances, walkSeed) {
  if (rootIds.length < 4) return { status: "INSUFFICIENT_BULK_ROOTS", rootCount: rootIds.length, walkersPerRoot: 8 };
  const roots = rootIds.slice(0, 4), perRoot = [], draws = new Set(); let duplicateU53Count = 0, drawCount = 0;
  roots.forEach(function (root, rootIndex) {
    const sums = new Float64Array(WALK_TIMES.length);
    for (let walker = 0; walker < 8; walker += 1) {
      let current = root, timeIndex = 0;
      for (let step = 1; step <= WALK_TIMES[WALK_TIMES.length - 1]; step += 1) {
        const draw = u53(walkSeed, "root:" + rootIndex + "/walker:" + walker + "/step:" + step, 0); drawCount += 1;
        if (draws.has(draw)) duplicateU53Count += 1; draws.add(draw);
        if (draw >= 0.5) {
          const neighbors = graph.adjacency[current]; let total = 0;
          neighbors.forEach(function (neighbor) { total += weights[neighbor.edge]; });
          let target = ((draw - 0.5) * 2) * total, chosen = neighbors[neighbors.length - 1].to;
          for (let index = 0; index < neighbors.length; index += 1) { target -= weights[neighbors[index].edge]; if (target <= 0) { chosen = neighbors[index].to; break; } }
          current = chosen;
        }
        if (step === WALK_TIMES[timeIndex]) {
          const distance = rootDistances[rootIndex][current]; sums[timeIndex] += distance * distance; timeIndex += 1;
        }
      }
    }
    const msd = Array.from(sums, function (value) { return clean(value / 8); });
    const valid = WALK_TIMES.map(function (time, index) { return { time: time, value: msd[index] }; }).filter(function (entry) { return entry.value > 0; });
    const slope = olsSlope(valid.map(function (entry) { return Math.log(entry.time); }), valid.map(function (entry) { return Math.log(entry.value); }));
    perRoot.push({ rootKey: graph.vertices[root].key, walkerCount: 8, msd: msd, slope: slope, walkDimension: slope > 0 ? clean(2 / slope) : null });
  });
  const dimensions = perRoot.map(function (row) { return row.walkDimension; }).filter(function (value) { return value != null; });
  return {
    status: dimensions.length === 4 ? "MEASURED_SCREENING_ONLY" : "ESTIMATOR_UNDEFINED",
    process: "lazy-weighted-nearest-neighbor",
    lazyProbability: 0.5,
    rootCount: 4,
    walkersPerRoot: 8,
    totalWalkers: 32,
    nativeTimes: WALK_TIMES.slice(),
    perRoot: perRoot,
    rootBlockDescriptiveTWidth: descriptiveTWidth(dimensions, 3.182),
    randomAudit: { algorithm: "gg-sha256-object-u53-v1", drawCount: drawCount, duplicateU53Count: duplicateU53Count },
    samplingNote: "Nonzero Monte Carlo error. The reported four-root t-width is descriptive only, not a confidence interval or coverage guarantee; no hierarchical construction/probe resampling."
  };
}

function transportMeasurement(graph, weights) {
  const bounds = boundsOf(graph), span = bounds.maxX - bounds.minX;
  let linearEnergy = 0;
  graph.edges.forEach(function (edge, index) {
    const dx = graph.vertices[edge.v].x - graph.vertices[edge.u].x;
    linearEnergy += weights[index] * (dx / span) * (dx / span);
  });
  const firstInteger = Math.ceil(bounds.minX), cutCount = Math.max(0, Math.ceil(bounds.maxX) - firstInteger), cutCapacities = new Float64Array(cutCount);
  graph.edges.forEach(function (edge, index) {
    const a = graph.vertices[edge.u].x, b = graph.vertices[edge.v].x, low = Math.min(a, b), high = Math.max(a, b);
    let first = Math.ceil(low - 0.5 + Number.EPSILON), last = Math.floor(high - 0.5 + Number.EPSILON);
    first = Math.max(first, firstInteger); last = Math.min(last, firstInteger + cutCount - 1);
    for (let integer = first; integer <= last; integer += 1) cutCapacities[integer - firstInteger] += weights[index];
  });
  const cuts = [];
  for (let offset = 0; offset < cutCapacities.length; offset += 1) if (cutCapacities[offset] > 0) cuts.push({ x: firstInteger + offset + 0.5, capacity: clean(cutCapacities[offset]) });
  const capacities = cuts.map(function (cut) { return cut.capacity; });
  const layered = capacities.length ? 1 / capacities.reduce(function (sum, capacity) { return sum + 1 / capacity; }, 0) : null;
  const minCapacity = capacities.length ? Math.min.apply(null, capacities) : null, medianCapacity = median(capacities);
  return {
    status: capacities.length ? "MEASURED_SCREENING_ONLY" : "ESTIMATOR_UNDEFINED",
    linearTrialDirichletEnergy: clean(linearEnergy),
    layeredSeriesProxy: clean(layered),
    minimumCutCapacity: clean(minCapacity),
    medianCutCapacity: clean(medianCapacity),
    minimumCutRatio: medianCapacity > 0 ? clean(minCapacity / medianCapacity) : null,
    cutCount: cuts.length,
    cutProfile: cuts,
    decisionNote: "Linear energy is an upper bound and the other quantities are proxies. They cannot establish transport noncollapse, Gate 5 PASS, normalized conductivity equivalence, or a Dirichlet-solver result."
  };
}

function buildComb(size) {
  const toothLength = Math.floor(size / 4), vertices = [], edges = [];
  function at(x, y) { return x * (toothLength + 1) + y; }
  for (let x = 0; x <= size; x += 1) for (let y = 0; y <= toothLength; y += 1) vertices.push(vertex("comb:" + x + ":" + y, x, y));
  for (let x = 0; x <= size; x += 1) for (let y = 0; y < toothLength; y += 1) edges.push([at(x, y), at(x, y + 1)]);
  for (let x = 0; x < size; x += 1) edges.push([at(x, 0), at(x + 1, 0)]);
  return finalizeGraph("comb-trap", size, vertices, [], edges, { toothLength: toothLength });
}

function combDiscriminant(graph, walkSeed) {
  const times = [16, 32, 64, 128, 256, 512, 1024].filter(function (time) { return time <= Math.max(256, Math.floor(graph.size * graph.size / 8)); });
  const roots = [0.4, 0.47, 0.53, 0.6].map(function (fraction) { return Math.round(fraction * graph.size) * (graph.metadata.toothLength + 1); });
  const perRoot = [], draws = new Set(); let drawCount = 0, duplicates = 0, occupiedTeeth = 0;
  roots.forEach(function (root, rootIndex) {
    const sums = new Float64Array(times.length);
    for (let walker = 0; walker < 8; walker += 1) {
      let current = root, timeIndex = 0;
      for (let step = 1; step <= times[times.length - 1]; step += 1) {
        const draw = u53(walkSeed, "comb/root:" + rootIndex + "/walker:" + walker + "/step:" + step, 0); drawCount += 1;
        if (draws.has(draw)) duplicates += 1; draws.add(draw);
        if (draw >= 0.5) {
          const row = graph.adjacency[current]; current = row[Math.min(row.length - 1, Math.floor(((draw - 0.5) * 2) * row.length))].to;
        }
        if (step === times[timeIndex]) {
          const dx = graph.vertices[current].x - graph.vertices[root].x; sums[timeIndex] += dx * dx; timeIndex += 1;
        }
      }
      if (graph.vertices[current].y > 0) occupiedTeeth += 1;
    }
    const msd = Array.from(sums, function (value) { return clean(value / 8); });
    const valid = times.map(function (time, index) { return { time: time, value: msd[index] }; }).filter(function (entry) { return entry.value > 0; });
    const slope = olsSlope(valid.map(function (entry) { return Math.log(entry.time); }), valid.map(function (entry) { return Math.log(entry.value); }));
    perRoot.push({ msd: msd, slope: slope, axialWalkDimension: slope > 0 ? clean(2 / slope) : null });
  });
  const dimensions = perRoot.map(function (row) { return row.axialWalkDimension; }).filter(function (value) { return value != null; });
  return {
    discriminant: "axial-lazy-walk",
    toothLength: graph.metadata.toothLength,
    rootCount: 4,
    walkersPerRoot: 8,
    times: times,
    perRoot: perRoot,
    axialWalkDimensionDescriptiveTWidth: descriptiveTWidth(dimensions, 3.182),
    finalToothOccupationFraction: clean(occupiedTeeth / 32),
    randomAudit: { drawCount: drawCount, duplicateU53Count: duplicates },
    interpretation: "actual screening discriminant; not a Gate 2/4 alternate-estimator decision"
  };
}

function buildSmallWorld(size, seed, withShortcuts) {
  const vertices = [], edges = [];
  function at(x, y) { return y * (size + 1) + x; }
  for (let y = 0; y <= size; y += 1) for (let x = 0; x <= size; x += 1) vertices.push(vertex("grid:" + y + ":" + x, x, y));
  for (let y = 0; y <= size; y += 1) for (let x = 0; x < size; x += 1) edges.push([at(x, y), at(x + 1, y)]);
  for (let y = 0; y < size; y += 1) for (let x = 0; x <= size; x += 1) edges.push([at(x, y), at(x, y + 1)]);
  const accepted = [], used = new Set(), target = Math.ceil(0.02 * vertices.length), minimumSeparation = size / 3;
  if (withShortcuts) {
    const starts = vertices.map(function (item, index) { return { index: index, rank: u53(seed, "start:" + item.key, 0) }; }).sort(function (a, b) { return a.rank - b.rank; });
    for (let si = 0; si < starts.length && accepted.length < target; si += 1) {
      const a = starts[si].index; if (used.has(a)) continue;
      let choice = null;
      for (let attempt = 0; attempt < 32; attempt += 1) {
        const candidate = Math.floor(u53(seed, "endpoint:" + vertices[a].key, attempt) * vertices.length);
        if (candidate === a || used.has(candidate)) continue;
        const distance = Math.abs(vertices[a].x - vertices[candidate].x) + Math.abs(vertices[a].y - vertices[candidate].y);
        if (distance < minimumSeparation) continue;
        choice = candidate; break;
      }
      if (choice != null) { used.add(a); used.add(choice); edges.push([a, choice]); accepted.push({ a: vertices[a].key, b: vertices[choice].key, intrinsicBaseSeparation: Math.abs(vertices[a].x - vertices[choice].x) + Math.abs(vertices[a].y - vertices[choice].y) }); }
    }
  }
  return finalizeGraph("small-world-shortcuts", size, vertices, [], edges, { targetShortcutCount: target, acceptedShortcuts: accepted, minimumSeparation: minimumSeparation });
}

function smallWorldDiscriminant(graph, baseGraph, rootSeed) {
  const analysis = analyzeGraph(graph), measured = volumeMeasurement(graph, analysis, rootSeed);
  if (!measured.rootIds.length) return { discriminant: "root-ball-inflation", status: measured.public.status, acceptedShortcutCount: graph.metadata.acceptedShortcuts.length };
  const radius = Math.max(2, Math.floor(graph.size / 5)), ratios = [];
  measured.rootIds.forEach(function (root) {
    const augmented = bfsDistances(graph, [root]), base = bfsDistances(baseGraph, [root]); let aCount = 0, bCount = 0;
    for (let index = 0; index < augmented.length; index += 1) { if (augmented[index] >= 0 && augmented[index] <= radius) aCount += 1; if (base[index] >= 0 && base[index] <= radius) bCount += 1; }
    ratios.push(aCount / bCount);
  });
  return {
    discriminant: "root-ball-inflation",
    status: "MEASURED_SCREENING_ONLY",
    shortcutDensityParameter: 0.02,
    targetShortcutCount: graph.metadata.targetShortcutCount,
    acceptedShortcutCount: graph.metadata.acceptedShortcuts.length,
    maximumEndpointsPerVertexObserved: 1,
    minimumIntrinsicEndpointSeparationRequired: graph.metadata.minimumSeparation,
    minimumIntrinsicEndpointSeparationObserved: graph.metadata.acceptedShortcuts.length ? Math.min.apply(null, graph.metadata.acceptedShortcuts.map(function (row) { return row.intrinsicBaseSeparation; })) : null,
    radius: radius,
    rootCount: ratios.length,
    inflationRatios: ratios.map(clean),
    meanBallInflation: clean(mean(ratios)),
    interpretation: "actual construction and metric crossover screen; not Gate 2/3 decision evidence"
  };
}

function buildVanishingNeck(size) {
  const corridorLength = Math.floor(size / 4), corridorWidth = 2, center = Math.floor((size - corridorWidth) / 2), cellKeys = new Set();
  function addPatch(startX) { for (let y = 0; y < size; y += 1) for (let x = startX; x < startX + size; x += 1) cellKeys.add(x + ":" + y); }
  addPatch(0); addPatch(size + corridorLength);
  for (let x = size; x < size + corridorLength; x += 1) for (let y = center; y < center + corridorWidth; y += 1) cellKeys.add(x + ":" + y);
  const pointMap = new Map(), vertices = [], faces = [];
  function point(x, y) { const key = x + ":" + y; if (!pointMap.has(key)) { pointMap.set(key, vertices.length); vertices.push(vertex("neck:" + key, x, y)); } return pointMap.get(key); }
  Array.from(cellKeys).sort(function (a, b) { const aa = a.split(":").map(Number), bb = b.split(":").map(Number); return aa[0] - bb[0] || aa[1] - bb[1]; }).forEach(function (key) {
    const parts = key.split(":").map(Number), x = parts[0], y = parts[1], sw = point(x, y), se = point(x + 1, y), ne = point(x + 1, y + 1), nw = point(x, y + 1);
    if ((x + y) % 2 === 0) faces.push([sw, se, ne], [sw, ne, nw]); else faces.push([sw, se, nw], [se, ne, nw]);
  });
  return finalizeGraph("vanishing-neck", size, vertices, faces, [], { corridorLength: corridorLength, corridorWidth: corridorWidth, corridorCellCount: corridorLength * corridorWidth });
}

function filterFacesAndVertices(baseGraph, keptFaces) {
  const used = new Set(); keptFaces.forEach(function (face) { face.forEach(function (index) { used.add(index); }); });
  const oldIds = Array.from(used).sort(function (a, b) { return a - b; }), map = new Map(), vertices = oldIds.map(function (old, index) { map.set(old, index); return baseGraph.vertices[old]; });
  const faces = keptFaces.map(function (face) { return face.map(function (old) { return map.get(old); }); });
  return { vertices: vertices, faces: faces, retainedOriginalVertexCount: oldIds.length };
}

function buildPerforated(size, seed) {
  const base = buildSquareCarrier("square-alternating", size, seed), candidates = [];
  base.vertices.forEach(function (item, index) {
    if (item.x >= 3 && item.x <= size - 3 && item.y >= 3 && item.y <= size - 3) candidates.push({ index: index, x: item.x, y: item.y, rank: u53(seed, "hole-center:" + item.key, 0) });
  });
  candidates.sort(function (a, b) { return a.rank - b.rank; });
  const target = Math.floor(0.05 * candidates.length), selected = [];
  candidates.forEach(function (candidate) {
    if (selected.length >= target) return;
    if (selected.every(function (other) { return Math.max(Math.abs(candidate.x - other.x), Math.abs(candidate.y - other.y)) >= 3; })) selected.push(candidate);
  });
  const removedCenters = new Set(selected.map(function (item) { return item.index; }));
  const keptFaces = base.faces.filter(function (face) { return !face.some(function (index) { return removedCenters.has(index); }); });
  const filtered = filterFacesAndVertices(base, keptFaces);
  let minimumCenterSeparationObserved = null;
  for (let first = 0; first < selected.length; first += 1) {
    for (let second = first + 1; second < selected.length; second += 1) {
      const separation = Math.max(Math.abs(selected[first].x - selected[second].x), Math.abs(selected[first].y - selected[second].y));
      if (minimumCenterSeparationObserved == null || separation < minimumCenterSeparationObserved) minimumCenterSeparationObserved = separation;
    }
  }
  const graph = finalizeGraph("perforated-disk", size, filtered.vertices, filtered.faces, [], {
    densityParameter: 0.05,
    candidateCenterCount: candidates.length,
    targetHoleCount: target,
    removedFaceStarCount: selected.length,
    minimumCenterSeparationObserved: minimumCenterSeparationObserved,
    originalVertexCount: base.vertices.length,
    retainedOriginalVertexCount: filtered.retainedOriginalVertexCount,
    removedFaceCount: base.faces.length - keptFaces.length
  });
  return graph;
}

function buildControl(control, size, seed) {
  if (control === "comb-trap") return buildComb(size);
  if (control === "small-world-shortcuts") return buildSmallWorld(size, seed, true);
  if (control === "vanishing-neck") return buildVanishingNeck(size);
  if (control === "perforated-disk") return buildPerforated(size, seed);
  throw new Error("unknown control " + control);
}

function positiveIdentity(family, size, sigmaIndex, replicate, ordinal) {
  return { ordinal: ordinal, kind: "positive", id: family, size: size, sigmaIndex: sigmaIndex, sigma: SIGMAS[sigmaIndex], replicate: replicate, runId: "positive/" + family + "/L" + size + "/s" + sigmaIndex + "/r" + String(replicate).padStart(2, "0") };
}

function controlIdentity(control, size, replicate, ordinal) {
  return { ordinal: ordinal, kind: "control", id: control, size: size, sigmaIndex: -1, sigma: 0, replicate: replicate, runId: "control/" + control + "/L" + size + "/r" + String(replicate).padStart(2, "0") };
}

function expectedCensus() {
  const out = []; let ordinal = 0;
  FAMILIES.forEach(function (family) { SIZES.forEach(function (size) { SIGMAS.forEach(function (_, sigmaIndex) { for (let replicate = 0; replicate < 32; replicate += 1) out.push(positiveIdentity(family, size, sigmaIndex, replicate, ordinal++)); }); }); });
  CONTROLS.forEach(function (control) { SIZES.forEach(function (size) { for (let replicate = 0; replicate < 32; replicate += 1) out.push(controlIdentity(control, size, replicate, ordinal++)); }); });
  return out;
}

function streamsFor(identity) {
  const namespace = identity.kind;
  return {
    construction: deriveSeed(namespace, identity.id, identity.size, identity.sigmaIndex, identity.replicate, "construction"),
    conductance: deriveSeed(namespace, identity.id, identity.size, identity.sigmaIndex, identity.replicate, "conductance"),
    volumeRoots: deriveSeed(namespace, identity.id, identity.size, identity.sigmaIndex, identity.replicate, "volume-roots"),
    walk: deriveSeed(namespace, identity.id, identity.size, identity.sigmaIndex, identity.replicate, "walk"),
    control: deriveSeed(namespace, identity.id, identity.size, identity.sigmaIndex, identity.replicate, "control")
  };
}

function buildPositiveRecord(identity) {
  const streams = streamsFor(identity), failures = [];
  const graph = buildPositive(identity.id, identity.size, streams.construction), analysis = analyzeGraph(graph), conductance = conductanceMeasurement(graph, streams.conductance, identity.sigma);
  if (!analysis.public.surfaceWitness.valid || !analysis.public.surfaceWitness.exactBetti || analysis.public.surfaceWitness.exactBetti.beta1 !== 0) failures.push({ code: "INVALID_COMPLEX", channel: "surface-topology", detail: "positive carrier did not validate as an exact combinatorial disk witness" });
  if (!conductance.public.strictlyPositive || conductance.public.boundResidual !== 0) failures.push({ code: "INVALID_COMPLEX", channel: "conductance", detail: "uniform ellipticity witness failed" });
  const volume = volumeMeasurement(graph, analysis, streams.volumeRoots);
  if (volume.public.status !== "MEASURED_SCREENING_ONLY") failures.push({ code: volume.public.status, channel: "volume", detail: "screening volume profile unavailable" });
  let randomWalk = null, transport = null;
  if (identity.size === 81 || identity.size === 120) {
    randomWalk = weightedWalkMeasurement(graph, conductance.weights, volume.rootIds, volume.rootDistances, streams.walk);
    transport = transportMeasurement(graph, conductance.weights);
    if (randomWalk.status !== "MEASURED_SCREENING_ONLY") failures.push({ code: randomWalk.status, channel: "random-walk", detail: "screening walk estimate unavailable" });
    if (transport.status !== "MEASURED_SCREENING_ONLY") failures.push({ code: transport.status, channel: "transport", detail: "screening transport estimate unavailable" });
  }
  const payload = {
    schema: "gg.u2.screening.record/1",
    manifestDigest: EXPECTED_MANIFEST_SEMANTIC_SHA256,
    supplementDigest: EXPECTED_SUPPLEMENT_SEMANTIC_SHA256,
    preregistrationCommit: PREREGISTRATION_COMMIT,
    identity: identity,
    streams: streams,
    construction: { family: identity.id, localityRadius: 1, randomAudit: graph.metadata.constructionRandomAudit || { draws: 0, duplicates: 0 }, deterministicConstruction: identity.id !== "square-hashed-diagonal" },
    graphAudit: analysis.public,
    conductanceAudit: conductance.public,
    volumeGrowthScreen: volume.public,
    randomWalkScreen: randomWalk,
    transportScreen: transport,
    failures: failures,
    screenInterpretation: { u2Status: "UNRESOLVED", decisionAuthority: "NONE", reason: "Preregistered lower-cost screen cannot satisfy decision Gates 2-8." }
  };
  return Object.assign({}, payload, { recordHash: sha256JSON(payload) });
}

function buildControlRecord(identity) {
  const streams = streamsFor(identity), failures = [], graph = buildControl(identity.id, identity.size, streams.control), analysis = analyzeGraph(graph);
  let discriminant;
  if (identity.id === "comb-trap") discriminant = combDiscriminant(graph, streams.walk);
  else if (identity.id === "small-world-shortcuts") discriminant = smallWorldDiscriminant(graph, buildSmallWorld(identity.size, streams.control, false), streams.volumeRoots);
  else if (identity.id === "vanishing-neck") {
    const weights = new Float64Array(graph.edges.length); weights.fill(1);
    discriminant = Object.assign({ discriminant: "two-cell-corridor-transport", corridorLength: graph.metadata.corridorLength, corridorWidth: graph.metadata.corridorWidth, corridorCellCount: graph.metadata.corridorCellCount }, transportMeasurement(graph, weights));
  } else {
    discriminant = {
      discriminant: "separated-removed-face-stars",
      densityParameter: graph.metadata.densityParameter,
      candidateCenterCount: graph.metadata.candidateCenterCount,
      targetHoleCount: graph.metadata.targetHoleCount,
      removedFaceStarCount: graph.metadata.removedFaceStarCount,
      minimumCenterSeparationObserved: graph.metadata.minimumCenterSeparationObserved,
      removedFaceCount: graph.metadata.removedFaceCount,
      giantComponentFraction: analysis.public.largestComponentFraction,
      exactBetti: analysis.public.surfaceWitness.exactBetti,
      interpretation: "actual topology discriminant; counts toward no Gate 7 decision without full confirmatory inference and reproduction"
    };
  }
  if (identity.id === "vanishing-neck" || identity.id === "perforated-disk") {
    if (!analysis.public.surfaceWitness.valid) failures.push({ code: "INVALID_COMPLEX", channel: "control-surface", detail: "control triangulation did not satisfy its surface witness" });
  }
  if (identity.id === "comb-trap" && (!discriminant.axialWalkDimensionDescriptiveTWidth || discriminant.axialWalkDimensionDescriptiveTWidth.count !== 4)) {
    failures.push({ code: "ESTIMATOR_UNDEFINED", channel: "comb-discriminant", detail: "four root-block axial walk descriptors were not all defined" });
  }
  if (identity.id === "small-world-shortcuts" && discriminant.acceptedShortcutCount !== discriminant.targetShortcutCount) {
    failures.push({ code: "INVALID_COMPLEX", channel: "control-shortfall", detail: "small-world accepted " + discriminant.acceptedShortcutCount + " of " + discriminant.targetShortcutCount + " preregistered shortcuts" });
  }
  if (identity.id === "small-world-shortcuts" && (discriminant.status !== "MEASURED_SCREENING_ONLY" || discriminant.meanBallInflation == null)) {
    failures.push({ code: "ESTIMATOR_UNDEFINED", channel: "small-world-discriminant", detail: "root-ball inflation discriminant was unavailable" });
  }
  if (identity.id === "vanishing-neck" && (discriminant.status !== "MEASURED_SCREENING_ONLY" || discriminant.minimumCutRatio == null)) {
    failures.push({ code: "ESTIMATOR_UNDEFINED", channel: "neck-discriminant", detail: "registered transport proxy was unavailable" });
  }
  if (identity.id === "perforated-disk" && discriminant.removedFaceStarCount !== discriminant.targetHoleCount) {
    failures.push({ code: "INVALID_COMPLEX", channel: "control-shortfall", detail: "perforated constructor realized " + discriminant.removedFaceStarCount + " of " + discriminant.targetHoleCount + " preregistered face stars" });
  }
  if (identity.id === "perforated-disk" && (!discriminant.exactBetti || discriminant.exactBetti.beta1 <= 0 || discriminant.giantComponentFraction < 0.9)) {
    failures.push({ code: "ESTIMATOR_UNDEFINED", channel: "perforated-discriminant", detail: "validated beta_1>0 and giant-component fraction>=0.9 were not both observed" });
  }
  const payload = {
    schema: "gg.u2.screening.record/1",
    manifestDigest: EXPECTED_MANIFEST_SEMANTIC_SHA256,
    supplementDigest: EXPECTED_SUPPLEMENT_SEMANTIC_SHA256,
    preregistrationCommit: PREREGISTRATION_COMMIT,
    identity: identity,
    streams: streams,
    construction: { control: identity.id, declaredParametersRealized: true, metadata: graph.metadata },
    graphAudit: analysis.public,
    controlDiscriminant: discriminant,
    failures: failures,
    screenInterpretation: { u2Status: "UNRESOLVED", decisionAuthority: "NONE", reason: "Control screen is not a Gate 7 decision." }
  };
  return Object.assign({}, payload, { recordHash: sha256JSON(payload) });
}

function buildRecord(identity) { return identity.kind === "positive" ? buildPositiveRecord(identity) : buildControlRecord(identity); }

function validateRecord(record, expectedIdentity, options) {
  const errors = [];
  options = options || {};
  try {
    if (!record || record.schema !== "gg.u2.screening.record/1") errors.push("record schema mismatch");
    if (record.manifestDigest !== EXPECTED_MANIFEST_SEMANTIC_SHA256 || record.supplementDigest !== EXPECTED_SUPPLEMENT_SEMANTIC_SHA256 || record.preregistrationCommit !== PREREGISTRATION_COMMIT) errors.push("record binding mismatch");
    if (expectedIdentity && canonicalStringify(record.identity) !== canonicalStringify(expectedIdentity)) errors.push("record identity mismatch");
    const expectedStreams = streamsFor(record.identity);
    if (canonicalStringify(record.streams) !== canonicalStringify(expectedStreams)) errors.push("stream derivation mismatch");
    if (!record.screenInterpretation || record.screenInterpretation.u2Status !== "UNRESOLVED" || record.screenInterpretation.decisionAuthority !== "NONE") errors.push("record is not fail-closed");
    const payload = JSON.parse(JSON.stringify(record)); delete payload.recordHash;
    if (record.recordHash !== sha256JSON(payload)) errors.push("record hash mismatch");
    if (record.identity.kind === "positive") {
      if (!record.conductanceAudit || record.conductanceAudit.everyEdgeEvaluated !== true) errors.push("positive conductance census incomplete");
      if (!record.volumeGrowthScreen || record.volumeGrowthScreen.rootCount !== 8) errors.push("positive volume root census incomplete");
      if ((record.identity.size === 81 || record.identity.size === 120) && (!record.randomWalkScreen || record.randomWalkScreen.totalWalkers !== 32 || !record.transportScreen)) errors.push("decision-size screening diagnostics incomplete");
    }
    if (options.remeasure !== false && errors.length === 0) {
      const rebuilt = buildRecord(record.identity);
      if (canonicalStringify(record) !== canonicalStringify(rebuilt)) errors.push("record differs from deterministic semantic remeasurement");
    }
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

function merkleRoot(hashes) {
  if (!hashes.length) return sha256Bytes(Buffer.alloc(0));
  let level = hashes.slice();
  while (level.length > 1) {
    const next = [];
    for (let index = 0; index < level.length; index += 2) next.push(sha256Bytes(Buffer.from(level[index] + (level[index + 1] || level[index]), "hex")));
    level = next;
  }
  return level[0];
}

function aggregateNumbers(records, accessor) {
  const values = records.map(accessor).filter(function (value) { return typeof value === "number" && Number.isFinite(value); });
  return { count: values.length, mean: clean(mean(values)), minimum: values.length ? clean(Math.min.apply(null, values)) : null, maximum: values.length ? clean(Math.max.apply(null, values)) : null };
}

function summarizeRecords(records, rawBinding, telemetry) {
  const positives = records.filter(function (record) { return record.identity.kind === "positive"; });
  const controls = records.filter(function (record) { return record.identity.kind === "control"; });
  const positiveCells = [];
  FAMILIES.forEach(function (family) { SIZES.forEach(function (size) { SIGMAS.forEach(function (_, sigmaIndex) {
    const cell = positives.filter(function (record) { return record.identity.id === family && record.identity.size === size && record.identity.sigmaIndex === sigmaIndex; });
    positiveCells.push({
      family: family, size: size, sigmaIndex: sigmaIndex, sigma: SIGMAS[sigmaIndex], recordCount: cell.length,
      failureRecordCount: cell.filter(function (record) { return record.failures.length; }).length,
      volumeSlopeDescriptor: aggregateNumbers(cell, function (record) { return record.volumeGrowthScreen.logLogSlopeDescriptor; }),
      walkDimensionDescriptor: aggregateNumbers(cell, function (record) { return record.randomWalkScreen && record.randomWalkScreen.rootBlockDescriptiveTWidth.mean; }),
      minimumCutRatio: aggregateNumbers(cell, function (record) { return record.transportScreen && record.transportScreen.minimumCutRatio; }),
      maximumConductanceBoundResidual: cell.length ? Math.max.apply(null, cell.map(function (record) { return record.conductanceAudit.boundResidual; })) : null,
      uniqueStructureDigests: new Set(cell.map(function (record) { return record.graphAudit.structureDigest; })).size,
      uniqueWeightedRealizationCount: new Set(cell.map(function (record) { return record.graphAudit.structureDigest + ":" + record.conductanceAudit.weightDigest; })).size,
      independence: (sigmaIndex === 0 && family !== "square-hashed-diagonal")
        ? { constructionRealizationCount: 1, nestedMeasurementBatchCount: 32, measurementBatchCount: 32, measurementBatchesPerConstruction: 32, label: "one deterministic geometry with 32 nested measurement batches; not n=32 independent geometries" }
        : { constructionRealizationCount: 32, nestedMeasurementBatchCount: 0, measurementBatchCount: 32, measurementBatchesPerConstruction: 1, label: "32 weighted construction realizations, one measurement batch each" }
    });
  }); }); });
  const controlCells = [];
  CONTROLS.forEach(function (control) { SIZES.forEach(function (size) {
    const cell = controls.filter(function (record) { return record.identity.id === control && record.identity.size === size; });
    const deterministic = control === "comb-trap" || control === "vanishing-neck";
    const row = {
      control: control,
      size: size,
      recordCount: cell.length,
      failureRecordCount: cell.filter(function (record) { return record.failures.length; }).length,
      uniqueStructureDigests: new Set(cell.map(function (record) { return record.graphAudit.structureDigest; })).size,
      uniqueWeightedRealizationCount: new Set(cell.map(function (record) { return record.graphAudit.structureDigest; })).size,
      independence: deterministic
        ? { constructionRealizationCount: 1, nestedMeasurementBatchCount: 32, measurementBatchCount: 32, measurementBatchesPerConstruction: 32, label: "one deterministic control construction with 32 nested measurement batches; not n=32 independent geometries" }
        : { constructionRealizationCount: 32, nestedMeasurementBatchCount: 0, measurementBatchCount: 32, measurementBatchesPerConstruction: 1, label: "32 independently streamed control constructions" }
    };
    if (control === "comb-trap") row.axialWalkDimensionDescriptor = aggregateNumbers(cell, function (record) { return record.controlDiscriminant.axialWalkDimensionDescriptiveTWidth.mean; });
    if (control === "small-world-shortcuts") { row.acceptedShortcutCount = aggregateNumbers(cell, function (record) { return record.controlDiscriminant.acceptedShortcutCount; }); row.meanBallInflation = aggregateNumbers(cell, function (record) { return record.controlDiscriminant.meanBallInflation; }); }
    if (control === "vanishing-neck") row.minimumCutRatio = aggregateNumbers(cell, function (record) { return record.controlDiscriminant.minimumCutRatio; });
    if (control === "perforated-disk") { row.beta1 = aggregateNumbers(cell, function (record) { const betti = record.controlDiscriminant.exactBetti; return betti && betti.beta1; }); row.giantComponentFraction = aggregateNumbers(cell, function (record) { return record.controlDiscriminant.giantComponentFraction; }); row.removedFaceStarCount = aggregateNumbers(cell, function (record) { return record.controlDiscriminant.removedFaceStarCount; }); }
    controlCells.push(row);
  }); });
  const failures = [];
  records.forEach(function (record) { record.failures.forEach(function (failure) { failures.push({ runId: record.identity.runId, code: failure.code, channel: failure.channel, detail: failure.detail }); }); });
  const allSeeds = [], seedOwners = new Map(), collisions = [];
  records.forEach(function (record) { Object.keys(record.streams).forEach(function (role) { const seed = record.streams[role], owner = record.identity.runId + "/" + role; if (seedOwners.has(seed)) collisions.push({ seed: seed, first: seedOwners.get(seed), second: owner }); else seedOwners.set(seed, owner); allSeeds.push(seed); }); });
  const payload = {
    schema: "gg.u2.screening.summary/1",
    screeningId: "ggii-u2-v2-screening-v1",
    manifestDigest: EXPECTED_MANIFEST_SEMANTIC_SHA256,
    supplementDigest: EXPECTED_SUPPLEMENT_SEMANTIC_SHA256,
    preregistrationCommit: PREREGISTRATION_COMMIT,
    outcome: { u2Status: "UNRESOLVED", acceptanceAllowed: false, rejectionAllowed: false, evidenceClass: "outcome-bearing-screening", reason: "This screen lacks decision-grade estimators, hierarchical inference, robustness channels, and independent Gate 8 reproduction." },
    census: { expectedRecords: 3840, observedRecords: records.length, positiveExpected: 3072, positiveObserved: positives.length, controlExpected: 768, controlObserved: controls.length, uniqueRunIds: new Set(records.map(function (record) { return record.identity.runId; })).size },
    gates: [1, 2, 3, 4, 5, 6, 7, 8].map(function (gate) { return { gate: gate, status: "NOT_EVALUATED_BY_SCREEN", decisionAuthority: "NONE" }; }),
    positiveCells: positiveCells,
    controlCells: controlCells,
    failureLedger: { count: failures.length, records: failures },
    randomnessAudit: { algorithm: "gg-sha256-object-u53-v1", effectiveStreamSeedCount: allSeeds.length, uniqueEffectiveStreamSeedCount: seedOwners.size, seedCollisionCount: collisions.length, seedCollisions: collisions, perRecordDrawCollisionCount: records.reduce(function (sum, record) { let count = 0; if (record.conductanceAudit) count += record.conductanceAudit.randomAudit.duplicateU53Count; if (record.randomWalkScreen) count += record.randomWalkScreen.randomAudit.duplicateU53Count; if (record.controlDiscriminant && record.controlDiscriminant.randomAudit) count += record.controlDiscriminant.randomAudit.duplicateU53Count; return sum + count; }, 0) },
    integrity: { recordMerkleRoot: merkleRoot(records.map(function (record) { return record.recordHash; })), raw: rawBinding },
    telemetryBinding: "runtime telemetry is emitted in a separate non-semantic certificate and is not part of this scientific content address"
  };
  return Object.assign({}, payload, { contentAddress: { algorithm: "sha256", canonicalization: "RFC8785-compatible closed JSON subset", digest: sha256JSON(payload), canonicalBytes: Buffer.byteLength(canonicalStringify(payload), "utf8") } });
}

function validateSummary(summary, records, rawBytes) {
  const errors = [];
  try {
    if (!summary || summary.schema !== "gg.u2.screening.summary/1" || !summary.outcome || summary.outcome.u2Status !== "UNRESOLVED" || summary.outcome.acceptanceAllowed || summary.outcome.rejectionAllowed) errors.push("summary outcome is not fail-closed");
    const census = expectedCensus();
    if (records.length !== census.length || records.length !== 3840) errors.push("record census length mismatch");
    records.forEach(function (record, index) { const report = validateRecord(record, census[index]); if (!report.valid) errors.push("record " + index + ": " + report.errors.join(", ")); });
    if (summary.census.observedRecords !== records.length || summary.census.uniqueRunIds !== new Set(records.map(function (record) { return record.identity.runId; })).size) errors.push("summary census mismatch");
    if (summary.integrity.recordMerkleRoot !== merkleRoot(records.map(function (record) { return record.recordHash; }))) errors.push("record Merkle root mismatch");
    if (rawBytes && (summary.integrity.raw.bytes !== rawBytes.length || summary.integrity.raw.sha256 !== sha256Bytes(rawBytes))) errors.push("raw-file binding mismatch");
    const payload = JSON.parse(JSON.stringify(summary)); const address = payload.contentAddress; delete payload.contentAddress;
    if (!address || address.digest !== sha256JSON(payload) || address.canonicalBytes !== Buffer.byteLength(canonicalStringify(payload), "utf8")) errors.push("summary contentAddress mismatch");
    if (!summary.gates.every(function (gate) { return gate.status === "NOT_EVALUATED_BY_SCREEN" && gate.decisionAuthority === "NONE"; })) errors.push("screen improperly claims a decision gate");
    if (rawBytes) {
      const expected = summarizeRecords(records, { path: summary.integrity.raw.path, bytes: rawBytes.length, sha256: sha256Bytes(rawBytes) });
      if (canonicalStringify(summary) !== canonicalStringify(expected)) errors.push("summary differs from deterministic full-payload rebuild");
    }
  } catch (error) { errors.push(error.message); }
  return { valid: errors.length === 0, errors: errors };
}

function replayRecord(record) {
  const rebuilt = buildRecord(record.identity);
  return { valid: rebuilt.recordHash === record.recordHash, expectedHash: rebuilt.recordHash, observedHash: record.recordHash, rebuilt: rebuilt };
}

module.exports = {
  ROOT: ROOT,
  MANIFEST_PATH: MANIFEST_PATH,
  EXPECTED_MANIFEST_SEMANTIC_SHA256: EXPECTED_MANIFEST_SEMANTIC_SHA256,
  SUPPLEMENT_PATH: SUPPLEMENT_PATH,
  EXPECTED_SUPPLEMENT_SEMANTIC_SHA256: EXPECTED_SUPPLEMENT_SEMANTIC_SHA256,
  PREREGISTRATION_COMMIT: PREREGISTRATION_COMMIT,
  FAMILIES: FAMILIES,
  SIZES: SIZES,
  SIGMAS: SIGMAS,
  CONTROLS: CONTROLS,
  canonicalStringify: canonicalStringify,
  sha256Bytes: sha256Bytes,
  sha256JSON: sha256JSON,
  loadManifest: loadManifest,
  deriveSeed: deriveSeed,
  u53: u53,
  buildPositive: buildPositive,
  buildControl: buildControl,
  analyzeGraph: analyzeGraph,
  conductanceMeasurement: conductanceMeasurement,
  volumeMeasurement: volumeMeasurement,
  transportMeasurement: transportMeasurement,
  expectedCensus: expectedCensus,
  streamsFor: streamsFor,
  buildRecord: buildRecord,
  validateRecord: validateRecord,
  summarizeRecords: summarizeRecords,
  validateSummary: validateSummary,
  replayRecord: replayRecord,
  merkleRoot: merkleRoot
};
