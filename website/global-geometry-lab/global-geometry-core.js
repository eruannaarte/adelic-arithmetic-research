/*
 * Global Geometry Lab — dependency-free mathematical core.
 *
 * This module intentionally keeps the numerical models small and inspectable.
 * It is a teaching/research-prototyping laboratory, not a substitute for a
 * certified geometry-processing or sparse eigensolver package.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.GlobalGeometryCore = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var VERSION = "0.1.0";
  var PI = Math.PI;
  var TAU = 2 * PI;
  var EPS = 1e-12;

  function clamp(x, lo, hi) {
    return Math.max(lo, Math.min(hi, x));
  }

  function finiteNumber(x, fallback) {
    return typeof x === "number" && isFinite(x) ? x : fallback;
  }

  function integer(x, fallback, lo, hi) {
    var value = Number.isInteger(x) ? x : fallback;
    return Math.max(lo, Math.min(hi, value));
  }

  function roundNumber(x) {
    if (!isFinite(x)) return null;
    if (Math.abs(x) < 1e-15) return 0;
    return Number(x.toPrecision(14));
  }

  function jsonSafe(value) {
    if (value === null || typeof value === "string" || typeof value === "boolean") return value;
    if (typeof value === "number") return roundNumber(value);
    if (Array.isArray(value) || ArrayBuffer.isView(value)) {
      return Array.prototype.map.call(value, jsonSafe);
    }
    if (typeof value === "object" && value) {
      var out = {};
      Object.keys(value).forEach(function (key) {
        if (typeof value[key] !== "undefined" && typeof value[key] !== "function") {
          out[key] = jsonSafe(value[key]);
        }
      });
      return out;
    }
    return null;
  }

  function cloneJSON(value) {
    return JSON.parse(JSON.stringify(jsonSafe(value)));
  }

  function deepFreeze(object) {
    if (!object || typeof object !== "object" || Object.isFrozen(object)) return object;
    Object.keys(object).forEach(function (key) { deepFreeze(object[key]); });
    return Object.freeze(object);
  }

  function mergeDeep(base, patch) {
    var result = cloneJSON(base || {});
    if (!patch || typeof patch !== "object") return result;
    Object.keys(patch).forEach(function (key) {
      var value = patch[key];
      if (value && typeof value === "object" && !Array.isArray(value)) {
        result[key] = mergeDeep(result[key] || {}, value);
      } else {
        result[key] = cloneJSON(value);
      }
    });
    return result;
  }

  function hashSeed(seed) {
    var text = String(seed == null ? "global-geometry" : seed);
    var h = 2166136261 >>> 0;
    for (var i = 0; i < text.length; i += 1) {
      h ^= text.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  function seededRandom(seed) {
    var a = hashSeed(seed);
    return function () {
      a |= 0;
      a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function edgeKey(a, b) {
    return a < b ? a + ":" + b : b + ":" + a;
  }

  function distance(a, b) {
    var dx = finiteNumber(a.x, 0) - finiteNumber(b.x, 0);
    var dy = finiteNumber(a.y, 0) - finiteNumber(b.y, 0);
    var dz = finiteNumber(a.z, 0) - finiteNumber(b.z, 0);
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }

  function triangleArea(a, b, c) {
    var ux = b.x - a.x, uy = b.y - a.y, uz = b.z - a.z;
    var vx = c.x - a.x, vy = c.y - a.y, vz = c.z - a.z;
    var cx = uy * vz - uz * vy;
    var cy = uz * vx - ux * vz;
    var cz = ux * vy - uy * vx;
    return 0.5 * Math.sqrt(cx * cx + cy * cy + cz * cz);
  }

  function angleFromSides(adjacentA, adjacentB, opposite) {
    var denominator = 2 * adjacentA * adjacentB;
    if (denominator <= EPS) return null;
    var cosine = clamp(
      (adjacentA * adjacentA + adjacentB * adjacentB - opposite * opposite) / denominator,
      -1,
      1
    );
    return Math.acos(cosine);
  }

  function canonicalizeComplex(input) {
    if (!input || typeof input !== "object") throw new Error("A complex/state object is required.");
    var rawNodes = input.nodes || input.vertices;
    if (!Array.isArray(rawNodes) || rawNodes.length === 0) {
      throw new Error("A complex must contain a non-empty nodes or vertices array.");
    }
    var nodes = rawNodes.map(function (node, index) {
      var n = node || {};
      return {
        id: index,
        label: n.label == null ? String(index) : String(n.label),
        x: finiteNumber(Number(n.x), 0),
        y: finiteNumber(Number(n.y), 0),
        z: finiteNumber(Number(n.z), 0),
        radius: clamp(finiteNumber(Number(n.radius), 1), 0.01, 100),
        value: finiteNumber(Number(n.value), 0),
        u: finiteNumber(Number(n.u), 1),
        v: finiteNumber(Number(n.v), 0)
      };
    });
    var faces = Array.isArray(input.faces) ? input.faces.map(function (face) {
      return [Number(face[0]), Number(face[1]), Number(face[2])];
    }) : [];
    var edgeMap = Object.create(null);
    var rawEdges = Array.isArray(input.edges) ? input.edges : [];
    rawEdges.forEach(function (edge) {
      var a = Array.isArray(edge) ? Number(edge[0]) : Number(edge.source);
      var b = Array.isArray(edge) ? Number(edge[1]) : Number(edge.target);
      if (!Number.isInteger(a) || !Number.isInteger(b) || a === b || a < 0 || b < 0 || a >= nodes.length || b >= nodes.length) return;
      var key = edgeKey(a, b);
      edgeMap[key] = {
        source: Math.min(a, b),
        target: Math.max(a, b),
        weight: clamp(finiteNumber(Number(Array.isArray(edge) ? edge[2] : edge.weight), 1), EPS, 1e12),
        length: clamp(finiteNumber(Number(Array.isArray(edge) ? null : edge.length), distance(nodes[a], nodes[b])), EPS, 1e12)
      };
    });
    faces.forEach(function (face) {
      [[face[0], face[1]], [face[1], face[2]], [face[2], face[0]]].forEach(function (pair) {
        var key = edgeKey(pair[0], pair[1]);
        if (!edgeMap[key]) {
          edgeMap[key] = {
            source: Math.min(pair[0], pair[1]),
            target: Math.max(pair[0], pair[1]),
            weight: 1,
            length: Math.max(EPS, distance(nodes[pair[0]], nodes[pair[1]]))
          };
        }
      });
    });
    var edges = Object.keys(edgeMap).sort(function (ka, kb) {
      var a = edgeMap[ka], b = edgeMap[kb];
      return a.source - b.source || a.target - b.target;
    }).map(function (key) { return edgeMap[key]; });
    var complex = {
      nodes: nodes,
      edges: edges,
      faces: faces,
      metadata: cloneJSON(input.metadata || {})
    };
    var report = validateComplex(complex);
    if (!report.valid) throw new Error("Invalid complex: " + report.errors.join("; "));
    return complex;
  }

  function validateComplex(input) {
    var errors = [], warnings = [];
    var nodes = input && (input.nodes || input.vertices);
    var edges = input && input.edges;
    var faces = input && input.faces;
    if (!Array.isArray(nodes) || nodes.length === 0) {
      errors.push("nodes must be a non-empty array");
      return { valid: false, errors: errors, warnings: warnings };
    }
    (Array.isArray(edges) ? edges : []).forEach(function (edge, i) {
      var a = Array.isArray(edge) ? Number(edge[0]) : Number(edge.source);
      var b = Array.isArray(edge) ? Number(edge[1]) : Number(edge.target);
      if (!Number.isInteger(a) || !Number.isInteger(b) || a < 0 || b < 0 || a >= nodes.length || b >= nodes.length || a === b) {
        errors.push("edge " + i + " has invalid endpoints");
      }
    });
    var faceKeys = Object.create(null);
    (Array.isArray(faces) ? faces : []).forEach(function (face, i) {
      if (!Array.isArray(face) || face.length !== 3 || face.some(function (v) { return !Number.isInteger(Number(v)) || Number(v) < 0 || Number(v) >= nodes.length; })) {
        errors.push("face " + i + " must contain three valid node indices");
      } else if (new Set(face.map(Number)).size !== 3) {
        errors.push("face " + i + " is degenerate");
      } else {
        var key = face.map(Number).sort(function (a, b) { return a - b; }).join(":");
        if (faceKeys[key]) warnings.push("duplicate triangular face " + i);
        faceKeys[key] = true;
      }
    });
    return { valid: errors.length === 0, errors: errors, warnings: warnings };
  }

  function generateTriangulatedDisk(options) {
    options = options || {};
    var rings = integer(options.rings, 3, 1, 12);
    var sectors = integer(options.sectors, 12, 3, 64);
    var outerRadius = clamp(finiteNumber(Number(options.radius), 1), 0.05, 100);
    var nodes = [{ id: 0, label: "center", x: 0, y: 0, z: 0, radius: 1, value: 1, u: 1, v: 0.2 }];
    for (var r = 1; r <= rings; r += 1) {
      for (var s = 0; s < sectors; s += 1) {
        var angle = TAU * s / sectors;
        var rho = outerRadius * r / rings;
        nodes.push({
          id: nodes.length,
          label: "r" + r + "s" + s,
          x: rho * Math.cos(angle),
          y: rho * Math.sin(angle),
          z: 0,
          radius: 1,
          value: Math.exp(-4 * rho * rho / (outerRadius * outerRadius)),
          u: 1,
          v: r === 1 && s % Math.max(1, Math.floor(sectors / 4)) === 0 ? 0.25 : 0
        });
      }
    }
    function index(ring, sector) {
      return 1 + (ring - 1) * sectors + ((sector % sectors) + sectors) % sectors;
    }
    var faces = [];
    for (var a = 0; a < sectors; a += 1) faces.push([0, index(1, a), index(1, a + 1)]);
    for (var ring = 2; ring <= rings; ring += 1) {
      for (var sector = 0; sector < sectors; sector += 1) {
        var p0 = index(ring - 1, sector), p1 = index(ring - 1, sector + 1);
        var q0 = index(ring, sector), q1 = index(ring, sector + 1);
        faces.push([p0, q0, q1], [p0, q1, p1]);
      }
    }
    return canonicalizeComplex({
      nodes: nodes,
      faces: faces,
      metadata: { generator: "triangulated-disk", rings: rings, sectors: sectors, topologyHint: "disk" }
    });
  }

  function generateIcosphere(options) {
    options = options || {};
    var subdivisions = integer(options.subdivisions, 0, 0, 3);
    var scale = clamp(finiteNumber(Number(options.radius), 1), 0.05, 100);
    var phi = (1 + Math.sqrt(5)) / 2;
    var raw = [
      [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0],
      [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi],
      [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1]
    ];
    var nodes = raw.map(function (p, i) {
      var norm = Math.sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2]);
      return { id: i, label: String(i), x: scale * p[0] / norm, y: scale * p[1] / norm, z: scale * p[2] / norm, radius: 1, value: p[2] / norm, u: 1, v: p[2] > 0 ? 0.08 : 0 };
    });
    var faces = [
      [0,11,5],[0,5,1],[0,1,7],[0,7,10],[0,10,11],
      [1,5,9],[5,11,4],[11,10,2],[10,7,6],[7,1,8],
      [3,9,4],[3,4,2],[3,2,6],[3,6,8],[3,8,9],
      [4,9,5],[2,4,11],[6,2,10],[8,6,7],[9,8,1]
    ];
    for (var level = 0; level < subdivisions; level += 1) {
      var midpointCache = Object.create(null);
      function midpoint(a, b) {
        var key = edgeKey(a, b);
        if (midpointCache[key] != null) return midpointCache[key];
        var pa = nodes[a], pb = nodes[b];
        var x = (pa.x + pb.x) / 2, y = (pa.y + pb.y) / 2, z = (pa.z + pb.z) / 2;
        var norm = Math.sqrt(x * x + y * y + z * z);
        var id = nodes.length;
        nodes.push({ id: id, label: String(id), x: scale * x / norm, y: scale * y / norm, z: scale * z / norm, radius: 1, value: z / norm, u: 1, v: z > 0.7 * scale ? 0.08 : 0 });
        midpointCache[key] = id;
        return id;
      }
      var refined = [];
      faces.forEach(function (f) {
        var ab = midpoint(f[0], f[1]), bc = midpoint(f[1], f[2]), ca = midpoint(f[2], f[0]);
        refined.push([f[0], ab, ca], [f[1], bc, ab], [f[2], ca, bc], [ab, bc, ca]);
      });
      faces = refined;
    }
    return canonicalizeComplex({
      nodes: nodes,
      faces: faces,
      metadata: { generator: "icosphere", subdivisions: subdivisions, topologyHint: "sphere" }
    });
  }

  function generateGraph(options) {
    options = options || {};
    var graphType = options.graphType || options.shape || "grid";
    var nodes = [], edges = [];
    if (graphType === "ring") {
      var count = integer(options.count, 24, 4, 300);
      for (var i = 0; i < count; i += 1) {
        var theta = TAU * i / count;
        nodes.push({ id: i, label: String(i), x: Math.cos(theta), y: Math.sin(theta), z: 0, radius: 1, value: Math.cos(theta), u: 1, v: i < 3 ? 0.2 : 0 });
        edges.push({ source: i, target: (i + 1) % count, weight: 1 });
      }
      var chord = integer(options.chord, 0, 0, Math.floor(count / 2));
      if (chord > 1) {
        for (var c = 0; c < count; c += 1) edges.push({ source: c, target: (c + chord) % count, weight: 0.7 });
      }
    } else {
      var rows = integer(options.rows, 7, 2, 40);
      var cols = integer(options.cols, 9, 2, 40);
      function gridIndex(row, col) { return row * cols + col; }
      for (var r = 0; r < rows; r += 1) {
        for (var col = 0; col < cols; col += 1) {
          nodes.push({ id: nodes.length, label: r + "," + col, x: col / Math.max(1, cols - 1) * 2 - 1, y: r / Math.max(1, rows - 1) * 2 - 1, z: 0, radius: 1, value: col === 0 ? 1 : 0, u: 1, v: Math.abs(r - rows / 2) < 1 && Math.abs(col - cols / 2) < 1 ? 0.2 : 0 });
          if (col > 0) edges.push({ source: gridIndex(r, col - 1), target: gridIndex(r, col), weight: 1 });
          if (r > 0) edges.push({ source: gridIndex(r - 1, col), target: gridIndex(r, col), weight: 1 });
        }
      }
    }
    return canonicalizeComplex({ nodes: nodes, edges: edges, faces: [], metadata: { generator: "graph", graphType: graphType, topologyHint: "one-dimensional complex" } });
  }

  function generatePointCloud(options) {
    options = options || {};
    var count = integer(options.count, 54, 8, 240);
    var k = integer(options.k, 5, 1, Math.min(20, count - 1));
    var shape = options.shape || "swiss-roll";
    var random = seededRandom(options.seed == null ? "point-cloud" : options.seed);
    var nodes = [];
    for (var i = 0; i < count; i += 1) {
      var x, y, z;
      if (shape === "circle") {
        var theta = TAU * i / count + (random() - 0.5) * 0.025;
        x = Math.cos(theta); y = Math.sin(theta); z = (random() - 0.5) * 0.025;
      } else if (shape === "clusters") {
        var cluster = i % 3;
        var centerAngle = TAU * cluster / 3;
        x = 0.68 * Math.cos(centerAngle) + (random() - 0.5) * 0.34;
        y = 0.68 * Math.sin(centerAngle) + (random() - 0.5) * 0.34;
        z = (random() - 0.5) * 0.2;
      } else {
        var t = 1.5 * PI + (3 * PI * i / Math.max(1, count - 1));
        x = t * Math.cos(t) / (4.5 * PI);
        z = t * Math.sin(t) / (4.5 * PI);
        y = random() * 2 - 1;
      }
      nodes.push({ id: i, label: String(i), x: x, y: y, z: z, radius: 1, value: i / Math.max(1, count - 1), u: 1, v: i % 17 === 0 ? 0.15 : 0 });
    }
    var candidateDistances = [];
    for (var a = 0; a < count; a += 1) {
      var row = [];
      for (var b = 0; b < count; b += 1) if (a !== b) row.push({ index: b, distance: distance(nodes[a], nodes[b]) });
      row.sort(function (p, q) { return p.distance - q.distance || p.index - q.index; });
      candidateDistances.push(row.slice(0, k));
    }
    var scaleSamples = [];
    candidateDistances.forEach(function (row) { row.forEach(function (item) { scaleSamples.push(item.distance); }); });
    scaleSamples.sort(function (a, b) { return a - b; });
    var sigma = finiteNumber(Number(options.sigma), scaleSamples[Math.floor(scaleSamples.length / 2)] || 1);
    sigma = Math.max(EPS, sigma);
    var edgeMap = Object.create(null);
    candidateDistances.forEach(function (row, source) {
      row.forEach(function (item) {
        var key = edgeKey(source, item.index);
        edgeMap[key] = {
          source: Math.min(source, item.index),
          target: Math.max(source, item.index),
          length: item.distance,
          weight: Math.exp(-(item.distance * item.distance) / (2 * sigma * sigma))
        };
      });
    });
    return canonicalizeComplex({
      nodes: nodes,
      edges: Object.keys(edgeMap).map(function (key) { return edgeMap[key]; }),
      faces: [],
      metadata: { generator: "point-cloud", shape: shape, k: k, sigma: sigma, seed: String(options.seed == null ? "point-cloud" : options.seed), topologyHint: "k-nearest-neighbor graph; not a surface reconstruction" }
    });
  }

  function generateComplex(generatorConfig) {
    generatorConfig = generatorConfig || {};
    var type = generatorConfig.type || "triangulated-disk";
    if (type === "triangulated-disk") return generateTriangulatedDisk(generatorConfig);
    if (type === "icosphere" || type === "triangulated-sphere") return generateIcosphere(generatorConfig);
    if (type === "graph") return generateGraph(generatorConfig);
    if (type === "point-cloud") return generatePointCloud(generatorConfig);
    throw new Error("Unknown generator type: " + type);
  }

  function adjacencyData(input) {
    var complex = canonicalizeComplex(input);
    var adjacency = complex.nodes.map(function () { return []; });
    complex.edges.forEach(function (edge, index) {
      adjacency[edge.source].push({ node: edge.target, weight: edge.weight, edge: index });
      adjacency[edge.target].push({ node: edge.source, weight: edge.weight, edge: index });
    });
    adjacency.forEach(function (row) { row.sort(function (a, b) { return a.node - b.node; }); });
    return { complex: complex, adjacency: adjacency };
  }

  function connectedComponents(input) {
    var data = adjacencyData(input), adjacency = data.adjacency;
    var seen = new Array(adjacency.length).fill(false), components = [];
    for (var start = 0; start < adjacency.length; start += 1) {
      if (seen[start]) continue;
      var queue = [start], component = [], cursor = 0;
      seen[start] = true;
      while (cursor < queue.length) {
        var node = queue[cursor++]; component.push(node);
        adjacency[node].forEach(function (neighbor) {
          if (!seen[neighbor.node]) { seen[neighbor.node] = true; queue.push(neighbor.node); }
        });
      }
      components.push(component.sort(function (a, b) { return a - b; }));
    }
    return components;
  }

  function rankGF2(columns, rowCount) {
    var basis = new Array(rowCount), rank = 0;
    columns.forEach(function (indices) {
      var vector = new Uint8Array(rowCount);
      indices.forEach(function (index) { vector[index] ^= 1; });
      for (var pivot = rowCount - 1; pivot >= 0; pivot -= 1) {
        if (!vector[pivot]) continue;
        if (basis[pivot]) {
          for (var j = 0; j < rowCount; j += 1) vector[j] ^= basis[pivot][j];
        } else {
          basis[pivot] = vector;
          rank += 1;
          break;
        }
      }
    });
    return rank;
  }

  function boundaryStructure(complex) {
    var counts = Object.create(null);
    complex.edges.forEach(function (edge) { counts[edgeKey(edge.source, edge.target)] = 0; });
    complex.faces.forEach(function (f) {
      [[f[0],f[1]],[f[1],f[2]],[f[2],f[0]]].forEach(function (pair) {
        var key = edgeKey(pair[0], pair[1]); counts[key] = (counts[key] || 0) + 1;
      });
    });
    var boundaryEdges = complex.edges.filter(function (edge) { return counts[edgeKey(edge.source, edge.target)] === 1; });
    var nonManifoldEdges = complex.edges.filter(function (edge) { return counts[edgeKey(edge.source, edge.target)] > 2; });
    var boundaryVerticesSet = Object.create(null);
    boundaryEdges.forEach(function (edge) { boundaryVerticesSet[edge.source] = true; boundaryVerticesSet[edge.target] = true; });
    var boundaryVertices = Object.keys(boundaryVerticesSet).map(Number).sort(function (a, b) { return a - b; });
    var boundaryAdjacency = Object.create(null);
    boundaryVertices.forEach(function (v) { boundaryAdjacency[v] = []; });
    boundaryEdges.forEach(function (edge) { boundaryAdjacency[edge.source].push(edge.target); boundaryAdjacency[edge.target].push(edge.source); });
    var seen = Object.create(null), boundaryComponents = 0;
    boundaryVertices.forEach(function (start) {
      if (seen[start]) return;
      boundaryComponents += 1;
      var queue = [start]; seen[start] = true;
      while (queue.length) {
        var current = queue.pop();
        (boundaryAdjacency[current] || []).forEach(function (next) { if (!seen[next]) { seen[next] = true; queue.push(next); } });
      }
    });
    return {
      edgeFaceCounts: counts,
      boundaryEdges: boundaryEdges,
      boundaryVertices: boundaryVertices,
      boundaryComponents: boundaryComponents,
      nonManifoldEdges: nonManifoldEdges
    };
  }

  function computeBettiNumbers(input) {
    var complex = canonicalizeComplex(input);
    var edgeIndex = Object.create(null);
    complex.edges.forEach(function (edge, index) { edgeIndex[edgeKey(edge.source, edge.target)] = index; });
    var boundaryOneColumns = complex.edges.map(function (edge) { return [edge.source, edge.target]; });
    var boundaryTwoColumns = complex.faces.map(function (face) {
      return [edgeIndex[edgeKey(face[0], face[1])], edgeIndex[edgeKey(face[1], face[2])], edgeIndex[edgeKey(face[2], face[0])]];
    });
    var rankBoundaryOne = rankGF2(boundaryOneColumns, complex.nodes.length);
    var rankBoundaryTwo = rankGF2(boundaryTwoColumns, complex.edges.length);
    var b0 = complex.nodes.length - rankBoundaryOne;
    var b1 = complex.edges.length - rankBoundaryOne - rankBoundaryTwo;
    var b2 = complex.faces.length - rankBoundaryTwo;
    var boundary = boundaryStructure(complex);
    var chi = complex.nodes.length - complex.edges.length + complex.faces.length;
    return jsonSafe({
      coefficients: "GF(2)",
      simplexCounts: { vertices: complex.nodes.length, edges: complex.edges.length, faces: complex.faces.length },
      boundaryRanks: { d1: rankBoundaryOne, d2: rankBoundaryTwo },
      betti: { b0: b0, b1: b1, b2: b2, array: [b0, b1, b2] },
      eulerCharacteristic: chi,
      eulerPoincareResidual: chi - (b0 - b1 + b2),
      connectedComponents: b0,
      boundary: {
        vertices: boundary.boundaryVertices,
        edgeCount: boundary.boundaryEdges.length,
        componentCount: boundary.boundaryComponents
      },
      manifoldCheck: {
        nonManifoldEdgeCount: boundary.nonManifoldEdges.length,
        isEdgeManifold: boundary.nonManifoldEdges.length === 0
      },
      interpretation: complex.faces.length ? "Homology of the finite triangular simplicial complex." : "Homology of the graph as a one-dimensional simplicial complex; graph cycles are not filled faces.",
      caveat: "Betti numbers use the supplied finite complex over GF(2); they do not by themselves infer the topology of an unknown continuum."
    });
  }

  function faceAngles(complex, face, metric, edgeLengths) {
    var a = face[0], b = face[1], c = face[2];
    var ab, bc, ca, area;
    if (metric === "circle-packing") {
      ab = complex.nodes[a].radius + complex.nodes[b].radius;
      bc = complex.nodes[b].radius + complex.nodes[c].radius;
      ca = complex.nodes[c].radius + complex.nodes[a].radius;
      var semiperimeter = (ab + bc + ca) / 2;
      area = Math.sqrt(Math.max(0, semiperimeter * (semiperimeter - ab) * (semiperimeter - bc) * (semiperimeter - ca)));
    } else {
      edgeLengths = edgeLengths || {};
      ab = finiteNumber(edgeLengths[edgeKey(a, b)], distance(complex.nodes[a], complex.nodes[b]));
      bc = finiteNumber(edgeLengths[edgeKey(b, c)], distance(complex.nodes[b], complex.nodes[c]));
      ca = finiteNumber(edgeLengths[edgeKey(c, a)], distance(complex.nodes[c], complex.nodes[a]));
      var semiperimeterEmbedded = (ab + bc + ca) / 2;
      area = Math.sqrt(Math.max(0, semiperimeterEmbedded * (semiperimeterEmbedded - ab) * (semiperimeterEmbedded - bc) * (semiperimeterEmbedded - ca)));
    }
    return {
      angles: [angleFromSides(ab, ca, bc), angleFromSides(ab, bc, ca), angleFromSides(bc, ca, ab)],
      area: area,
      sideLengths: [ab, bc, ca]
    };
  }

  function surfaceValidity(input, options) {
    options = options || {};
    var complex = canonicalizeComplex(input);
    var metric = options.metric === "circle-packing" ? "circle-packing" : "embedded";
    var boundary = boundaryStructure(complex);
    var edgeLengths = Object.create(null);
    complex.edges.forEach(function (edge) { edgeLengths[edgeKey(edge.source, edge.target)] = edge.length; });
    var faceKeys = Object.create(null), duplicateFaces = [], degenerateFaces = [];
    complex.faces.forEach(function (face, faceIndex) {
      var key = face.slice().sort(function (a, b) { return a - b; }).join(":");
      if (faceKeys[key] != null) duplicateFaces.push(faceIndex);
      else faceKeys[key] = faceIndex;
      var geometry = faceAngles(complex, face, metric, edgeLengths);
      var sides = geometry.sideLengths.slice().sort(function (a, b) { return a - b; });
      if (geometry.area <= EPS || sides[0] + sides[1] <= sides[2] + EPS || geometry.angles.some(function (angle) { return angle == null || !isFinite(angle); })) degenerateFaces.push(faceIndex);
    });
    var danglingEdges = complex.faces.length ? complex.edges.filter(function (edge) { return boundary.edgeFaceCounts[edgeKey(edge.source, edge.target)] === 0; }) : [];
    var boundarySet = Object.create(null);
    boundary.boundaryVertices.forEach(function (vertex) { boundarySet[vertex] = true; });
    var incidentFaces = complex.nodes.map(function () { return []; });
    complex.faces.forEach(function (face, faceIndex) { face.forEach(function (vertex) { incidentFaces[vertex].push(faceIndex); }); });
    var invalidVertexLinks = [];
    incidentFaces.forEach(function (facesAtVertex, vertex) {
      if (!facesAtVertex.length) {
        if (complex.faces.length) invalidVertexLinks.push({ vertex: vertex, reason: "surface-isolated vertex" });
        return;
      }
      var link = Object.create(null);
      function addLinkNode(v) { if (!link[v]) link[v] = []; }
      facesAtVertex.forEach(function (faceIndex) {
        var opposite = complex.faces[faceIndex].filter(function (v) { return v !== vertex; });
        addLinkNode(opposite[0]); addLinkNode(opposite[1]);
        link[opposite[0]].push(opposite[1]); link[opposite[1]].push(opposite[0]);
      });
      var linkNodes = Object.keys(link).map(Number);
      var seen = Object.create(null), queue = linkNodes.length ? [linkNodes[0]] : [];
      if (queue.length) seen[queue[0]] = true;
      while (queue.length) {
        var current = queue.pop();
        link[current].forEach(function (next) { if (!seen[next]) { seen[next] = true; queue.push(next); } });
      }
      var connected = Object.keys(seen).length === linkNodes.length;
      var degrees = linkNodes.map(function (v) { return link[v].length; });
      var degreeOne = degrees.filter(function (d) { return d === 1; }).length;
      var expectedDegrees = boundarySet[vertex] ? degreeOne === 2 && degrees.every(function (d) { return d === 1 || d === 2; }) : degrees.length >= 3 && degrees.every(function (d) { return d === 2; });
      if (!connected || !expectedDegrees) invalidVertexLinks.push({ vertex: vertex, reason: boundarySet[vertex] ? "boundary link is not one path" : "interior link is not one cycle" });
    });
    var errors = [];
    if (!complex.faces.length) errors.push("no triangular 2-cells");
    if (duplicateFaces.length) errors.push("duplicate faces");
    if (degenerateFaces.length) errors.push("degenerate or triangle-inequality-violating faces");
    if (boundary.nonManifoldEdges.length) errors.push("edges with more than two incident faces");
    if (danglingEdges.length) errors.push("edges not incident to any face in a surface complex");
    if (invalidVertexLinks.length) errors.push("non-manifold vertex links");
    return jsonSafe({
      valid: errors.length === 0,
      identityApplicable: errors.length === 0,
      metric: metric,
      errors: errors,
      duplicateFaces: duplicateFaces,
      degenerateFaces: degenerateFaces,
      nonManifoldEdges: boundary.nonManifoldEdges.map(function (edge) { return [edge.source, edge.target]; }),
      danglingEdges: danglingEdges.map(function (edge) { return [edge.source, edge.target]; }),
      invalidVertexLinks: invalidVertexLinks,
      boundaryComponents: boundary.boundaryComponents,
      caveat: "This gate checks a finite pure triangular 2-manifold with nondegenerate intrinsic triangles and path/cycle vertex links; it does not certify orientability or continuum convergence."
    });
  }

  function angleDefectCurvature(input, options) {
    options = options || {};
    var complex = canonicalizeComplex(input);
    var metric = options.metric === "circle-packing" ? "circle-packing" : "embedded";
    if (complex.faces.length === 0) {
      return {
        available: false,
        identityApplicable: false,
        metric: metric,
        vertices: [],
        total: null,
        targetTotal: null,
        gaussBonnetResidual: null,
        caveat: "Angle-defect curvature requires triangular 2-cells; this object is currently only a graph."
      };
    }
    var validity = surfaceValidity(complex, { metric: metric });
    if (!validity.valid) {
      return {
        available: false,
        identityApplicable: false,
        metric: metric,
        vertices: [],
        total: null,
        targetTotal: null,
        gaussBonnetResidual: null,
        surfaceValidity: validity,
        caveat: "Angle-defect and Gauss–Bonnet claims are withheld because the supplied cells do not pass the triangular 2-manifold validity gate."
      };
    }
    var boundary = boundaryStructure(complex);
    var boundarySet = Object.create(null);
    boundary.boundaryVertices.forEach(function (v) { boundarySet[v] = true; });
    var angleSums = new Array(complex.nodes.length).fill(0);
    var dualAreas = new Array(complex.nodes.length).fill(0);
    var incident = new Array(complex.nodes.length).fill(0);
    var degenerateFaces = [];
    var edgeLengths = Object.create(null);
    complex.edges.forEach(function (edge) { edgeLengths[edgeKey(edge.source, edge.target)] = edge.length; });
    complex.faces.forEach(function (face, faceIndex) {
      var geometry = faceAngles(complex, face, metric, edgeLengths);
      if (geometry.area <= EPS || geometry.angles.some(function (angle) { return angle == null || !isFinite(angle); })) {
        degenerateFaces.push(faceIndex);
        return;
      }
      face.forEach(function (vertex, local) {
        angleSums[vertex] += geometry.angles[local];
        dualAreas[vertex] += geometry.area / 3;
        incident[vertex] += 1;
      });
    });
    var vertices = [], total = 0;
    complex.nodes.forEach(function (node, index) {
      if (!incident[index]) return;
      var target = boundarySet[index] ? PI : TAU;
      var defect = target - angleSums[index];
      total += defect;
      vertices.push({
        id: index,
        boundary: !!boundarySet[index],
        incidentFaces: incident[index],
        angleSum: angleSums[index],
        defect: defect,
        dualArea: dualAreas[index],
        density: dualAreas[index] > EPS ? defect / dualAreas[index] : null
      });
    });
    var chi = complex.nodes.length - complex.edges.length + complex.faces.length;
    var targetTotal = TAU * chi;
    return jsonSafe({
      available: true,
      identityApplicable: true,
      metric: metric,
      surfaceValidity: validity,
      boundaryConvention: "Interior target angle 2π; boundary target angle π, so boundary turning is included at boundary vertices.",
      vertices: vertices,
      total: total,
      targetTotal: targetTotal,
      gaussBonnetResidual: total - targetTotal,
      relativeResidual: Math.abs(targetTotal) > EPS ? (total - targetTotal) / Math.abs(targetTotal) : total - targetTotal,
      minDefect: Math.min.apply(null, vertices.map(function (v) { return v.defect; })),
      maxDefect: Math.max.apply(null, vertices.map(function (v) { return v.defect; })),
      degenerateFaceCount: degenerateFaces.length,
      nonManifoldEdgeCount: boundary.nonManifoldEdges.length,
      formula: "Σ K_v = 2πχ for the stated piecewise-Euclidean boundary convention.",
      caveat: metric === "embedded" ? "Curvature is intrinsic to the supplied triangular edge lengths, even though display coordinates are used to obtain those lengths." : "Circle-packing lengths ℓ_ij=r_i+r_j define an abstract intrinsic metric; display positions need not be an isometric embedding."
    });
  }

  function normalizedLaplacian(input) {
    var data = adjacencyData(input), complex = data.complex;
    var n = complex.nodes.length;
    var matrix = new Array(n);
    var degree = new Array(n).fill(0);
    for (var i = 0; i < n; i += 1) matrix[i] = new Array(n).fill(0);
    complex.edges.forEach(function (edge) { degree[edge.source] += edge.weight; degree[edge.target] += edge.weight; });
    for (var d = 0; d < n; d += 1) if (degree[d] > EPS) matrix[d][d] = 1;
    complex.edges.forEach(function (edge) {
      var value = -edge.weight / Math.sqrt(degree[edge.source] * degree[edge.target]);
      matrix[edge.source][edge.target] += value;
      matrix[edge.target][edge.source] += value;
    });
    return { matrix: matrix, degree: degree, complex: complex };
  }

  function jacobiEigenvalues(symmetricMatrix, options) {
    options = options || {};
    var n = symmetricMatrix.length;
    var a = symmetricMatrix.map(function (row) { return row.slice(); });
    var tolerance = finiteNumber(Number(options.tolerance), 1e-11);
    var maxSweeps = integer(options.maxSweeps, 35, 1, 100);
    var sweeps = 0, converged = false, maxOffDiagonal = 0;
    for (var sweep = 0; sweep < maxSweeps; sweep += 1) {
      maxOffDiagonal = 0;
      for (var p = 0; p < n - 1; p += 1) {
        for (var q = p + 1; q < n; q += 1) {
          var apq = a[p][q];
          maxOffDiagonal = Math.max(maxOffDiagonal, Math.abs(apq));
          if (Math.abs(apq) <= tolerance) continue;
          var phi = 0.5 * Math.atan2(2 * apq, a[q][q] - a[p][p]);
          var c = Math.cos(phi), s = Math.sin(phi);
          var app = a[p][p], aqq = a[q][q];
          for (var k = 0; k < n; k += 1) {
            if (k === p || k === q) continue;
            var akp = a[k][p], akq = a[k][q];
            a[k][p] = a[p][k] = c * akp - s * akq;
            a[k][q] = a[q][k] = s * akp + c * akq;
          }
          a[p][p] = c * c * app - 2 * s * c * apq + s * s * aqq;
          a[q][q] = s * s * app + 2 * s * c * apq + c * c * aqq;
          a[p][q] = a[q][p] = 0;
        }
      }
      sweeps = sweep + 1;
      if (maxOffDiagonal <= tolerance) { converged = true; break; }
    }
    var values = a.map(function (row, i) { return Math.abs(row[i]) < 1e-10 ? 0 : row[i]; });
    values.sort(function (x, y) { return x - y; });
    return { eigenvalues: values, converged: converged, sweeps: sweeps, maxOffDiagonal: maxOffDiagonal };
  }

  function defaultHeatTimes() {
    return [0.05, 0.1, 0.2, 0.4, 0.8, 1.5, 3, 6, 12, 24, 48];
  }

  function normalizedLaplacianSpectrum(input, options) {
    options = options || {};
    var complex = canonicalizeComplex(input);
    var maxSize = integer(options.maxEigenSize, 120, 4, 400);
    if (complex.nodes.length > maxSize) {
      return {
        available: false,
        reason: "dense eigensolver safety limit",
        nodeCount: complex.nodes.length,
        maxEigenSize: maxSize,
        eigenvalues: [],
        heatTrace: [],
        caveat: "Increase maxEigenSize knowingly or use a sparse eigensolver outside this dependency-free demo."
      };
    }
    var laplacian = normalizedLaplacian(complex);
    var eig = jacobiEigenvalues(laplacian.matrix, options);
    var rawEigenvalues = eig.eigenvalues.slice();
    var boundTolerance = 1e-8;
    var eigenvalues = rawEigenvalues.map(function (v) {
      if (v < 0 && v >= -boundTolerance) return 0;
      if (v > 2 && v <= 2 + boundTolerance) return 2;
      return v;
    });
    var boundViolations = rawEigenvalues.filter(function (v) { return v < -boundTolerance || v > 2 + boundTolerance; });
    var times = Array.isArray(options.heatTimes) && options.heatTimes.length ? options.heatTimes.map(Number).filter(function (t) { return isFinite(t) && t > 0; }) : defaultHeatTimes();
    var heatTrace = times.map(function (time) {
      var z = 0, firstMoment = 0;
      eigenvalues.forEach(function (lambda) {
        var heat = Math.exp(-time * lambda);
        z += heat;
        firstMoment += lambda * heat;
      });
      return { time: time, trace: z, normalizedTrace: z / eigenvalues.length, spectralDimension: z > EPS ? 2 * time * firstMoment / z : null };
    });
    var zeroMultiplicity = eigenvalues.filter(function (v) { return v < 1e-8; }).length;
    var firstPositive = eigenvalues.filter(function (v) { return v >= 1e-8; })[0];
    return jsonSafe({
      available: true,
      operator: "symmetric normalized graph Laplacian L=I-D^{-1/2}AD^{-1/2}",
      nodeCount: complex.nodes.length,
      eigenvalues: eigenvalues,
      rawEigenvalueBounds: { min: rawEigenvalues[0], max: rawEigenvalues[rawEigenvalues.length - 1], valid: boundViolations.length === 0, violations: boundViolations },
      zeroMultiplicity: zeroMultiplicity,
      spectralGap: firstPositive == null ? 0 : firstPositive,
      gap: firstPositive == null ? 0 : firstPositive,
      heatTrace: heatTrace,
      spectralDimensionProfile: heatTrace.map(function (point) { return { scale: point.time, value: point.spectralDimension }; }),
      solver: { method: "cyclic Jacobi dense symmetric eigensolver", converged: eig.converged, sweeps: eig.sweeps, maxOffDiagonal: eig.maxOffDiagonal, validatedBounds: boundViolations.length === 0 },
      measure: "Degree-weighted measure in the random-walk representation; the symmetric normalized operator is unitarily equivalent.",
      interpretation: "d_s(t)=-2 d log Tr(exp(-tL))/d log t, evaluated analytically from the finite spectrum.",
      caveat: "On a finite graph, spectral dimension tends toward zero at extreme scales. A plateau over a justified intermediate window is descriptive evidence, not proof of a continuum dimension."
    });
  }

  function volumeGrowthProfile(input, options) {
    options = options || {};
    var data = adjacencyData(input), complex = data.complex, adjacency = data.adjacency, n = adjacency.length;
    var sourceLimit = integer(options.sourceLimit, n, 1, n);
    var sources = [];
    if (sourceLimit === n) {
      for (var i = 0; i < n; i += 1) sources.push(i);
    } else {
      for (var s = 0; s < sourceLimit; s += 1) sources.push(Math.floor(s * n / sourceLimit));
    }
    var distanceRows = [], diameter = 0;
    function shortestIntrinsicDistances(source) {
      var distances = new Array(n).fill(Infinity), heap = [];
      function push(item) {
        heap.push(item);
        var child = heap.length - 1;
        while (child > 0) {
          var parent = Math.floor((child - 1) / 2);
          if (heap[parent][0] <= heap[child][0]) break;
          var swap = heap[parent]; heap[parent] = heap[child]; heap[child] = swap; child = parent;
        }
      }
      function pop() {
        var root = heap[0], tail = heap.pop();
        if (heap.length) {
          heap[0] = tail;
          var parent = 0;
          while (true) {
            var left = 2 * parent + 1, right = left + 1, smallest = parent;
            if (left < heap.length && heap[left][0] < heap[smallest][0]) smallest = left;
            if (right < heap.length && heap[right][0] < heap[smallest][0]) smallest = right;
            if (smallest === parent) break;
            var swap = heap[parent]; heap[parent] = heap[smallest]; heap[smallest] = swap; parent = smallest;
          }
        }
        return root;
      }
      distances[source] = 0; push([0, source]);
      while (heap.length) {
        var item = pop(), currentDistance = item[0], current = item[1];
        if (currentDistance > distances[current] + EPS) continue;
        adjacency[current].forEach(function (neighbor) {
          var edgeLength = options.volumeMetric === "hop" ? 1 : complex.edges[neighbor.edge].length;
          var candidate = currentDistance + edgeLength;
          if (candidate + EPS < distances[neighbor.node]) {
            distances[neighbor.node] = candidate;
            push([candidate, neighbor.node]);
          }
        });
      }
      return distances;
    }
    sources.forEach(function (source) {
      var distances = shortestIntrinsicDistances(source);
      distances.forEach(function (d) { if (isFinite(d) && d > diameter) diameter = d; });
      distanceRows.push(distances);
    });
    var scaleSamples = integer(options.maxRadius, 8, 2, 40);
    var profile = [];
    for (var sample = 0; sample <= scaleSamples; sample += 1) {
      var radius = diameter > EPS ? diameter * sample / scaleSamples : sample;
      var volumes = distanceRows.map(function (row) { return row.filter(function (d) { return isFinite(d) && d <= radius + EPS; }).length; });
      var average = volumes.reduce(function (sum, value) { return sum + value; }, 0) / volumes.length;
      profile.push({ radius: radius, averageVolume: average, minVolume: Math.min.apply(null, volumes), maxVolume: Math.max.apply(null, volumes), localDimension: null, dimension: null });
    }
    for (var p = 2; p < profile.length; p += 1) {
      if (profile[p - 1].averageVolume > 0 && profile[p].averageVolume > 0) {
        profile[p].localDimension = Math.log(profile[p].averageVolume / profile[p - 1].averageVolume) / Math.log(profile[p].radius / profile[p - 1].radius);
        profile[p].dimension = profile[p].localDimension;
      }
    }
    return jsonSafe({
      metric: options.volumeMetric === "hop" ? "unweighted shortest-path hop distance" : "intrinsic shortest-path distance from stored positive edge.length values",
      sourcesUsed: sources.length,
      reachableDiameterEstimate: diameter,
      scaleSamples: scaleSamples,
      profile: profile,
      measure: "Counting measure on vertices: μ(B)=the number of sampled vertices in the graph ball.",
      interpretation: "The local slope estimates d_V(r)=d log μ(B(r)) / d log r from successive declared intrinsic radii.",
      caveat: "Finite size, boundaries, disconnected components, and the chosen graph construction can dominate this scale-dependent descriptor."
    });
  }

  function walkDimensionProfile(input, options) {
    options = options || {};
    var data = adjacencyData(input), complex = data.complex, adjacency = data.adjacency, n = complex.nodes.length;
    var sourceLimit = integer(options.walkSourceLimit, Math.min(12, n), 1, n);
    var maxSteps = integer(options.walkSteps, Math.min(14, Math.max(4, n)), 2, 60);
    var sources = [];
    for (var s = 0; s < sourceLimit; s += 1) sources.push(Math.floor(s * n / sourceLimit));
    sources = sources.filter(function (value, i, array) { return array.indexOf(value) === i; });
    var msdSums = new Array(maxSteps + 1).fill(0);
    sources.forEach(function (source) {
      var distances = new Array(n).fill(-1), queue = [source], cursor = 0;
      distances[source] = 0;
      while (cursor < queue.length) {
        var current = queue[cursor++];
        adjacency[current].forEach(function (neighbor) {
          if (distances[neighbor.node] < 0) { distances[neighbor.node] = distances[current] + 1; queue.push(neighbor.node); }
        });
      }
      var probability = new Array(n).fill(0); probability[source] = 1;
      for (var step = 1; step <= maxSteps; step += 1) {
        var next = new Array(n).fill(0);
        for (var i = 0; i < n; i += 1) {
          if (probability[i] === 0) continue;
          var degree = adjacency[i].reduce(function (sum, edge) { return sum + edge.weight; }, 0);
          if (degree <= EPS) next[i] += probability[i];
          else adjacency[i].forEach(function (edge) { next[edge.node] += probability[i] * edge.weight / degree; });
        }
        probability = next;
        msdSums[step] += probability.reduce(function (sum, mass, node) {
          return sum + mass * (distances[node] < 0 ? 0 : distances[node] * distances[node]);
        }, 0);
      }
    });
    var profile = [];
    for (var t = 1; t <= maxSteps; t += 1) {
      var msd = msdSums[t] / Math.max(1, sources.length);
      var slope = null, dimension = null;
      if (t >= 2) {
        var previous = msdSums[t - 1] / Math.max(1, sources.length);
        if (msd > EPS && previous > EPS) {
          slope = Math.log(msd / previous) / Math.log(t / (t - 1));
          if (slope > 1e-6) dimension = 2 / slope;
        }
      }
      profile.push({ step: t, scale: t, meanSquareDisplacement: msd, logarithmicSlope: slope, dimension: dimension, walkDimension: dimension });
    }
    return jsonSafe({
      metric: "unweighted shortest-path displacement with weighted random-walk transitions",
      measure: "Probability measure evolved from deterministic delta sources; source results are averaged uniformly.",
      sourcesUsed: sources.length,
      profile: profile,
      interpretation: "Where ⟨r²(t)⟩ scales approximately as t^(2/d_w), the local logarithmic slope gives d_w(t)=2/slope.",
      caveat: "Parity, boundaries, bottlenecks, and finite-size saturation can destroy a scaling window; null values are reported instead of forcing a dimension."
    });
  }

  function causalCone(input, sources, steps) {
    var data = adjacencyData(input), adjacency = data.adjacency;
    var sourceList = Array.isArray(sources) ? sources.slice() : [sources == null ? 0 : sources];
    sourceList = sourceList.map(Number).filter(function (v, i, array) {
      return Number.isInteger(v) && v >= 0 && v < adjacency.length && array.indexOf(v) === i;
    }).sort(function (a, b) { return a - b; });
    var depth = integer(steps, 1, 0, Math.max(0, adjacency.length));
    var distances = new Array(adjacency.length).fill(-1), queue = sourceList.slice(), cursor = 0;
    sourceList.forEach(function (source) { distances[source] = 0; });
    while (cursor < queue.length) {
      var current = queue[cursor++];
      if (distances[current] >= depth) continue;
      adjacency[current].forEach(function (neighbor) {
        if (distances[neighbor.node] < 0) {
          distances[neighbor.node] = distances[current] + 1;
          queue.push(neighbor.node);
        }
      });
    }
    var shells = [];
    for (var d = 0; d <= depth; d += 1) {
      shells.push({ distance: d, nodes: distances.map(function (value, index) { return value === d ? index : null; }).filter(function (v) { return v != null; }) });
    }
    return jsonSafe({
      sources: sourceList,
      steps: depth,
      reachable: distances.map(function (value, index) { return value >= 0 && value <= depth ? index : null; }).filter(function (v) { return v != null; }),
      shells: shells,
      rule: "A radius-one synchronous local rule can influence only nodes within k graph hops after k steps.",
      caveat: "This is a support bound (an L0 causal cone), not a bound on signal magnitude or a relativistic causal structure."
    });
  }

  function validateCurvatureTarget(input, targetSpec, tolerance) {
    var complex = canonicalizeComplex(input);
    var chi = complex.nodes.length - complex.edges.length + complex.faces.length;
    var expectedTotal = TAU * chi;
    var supplied = null, source = "procedural target normalized to Gauss–Bonnet total", errors = [];
    targetSpec = targetSpec || {};
    if (Array.isArray(targetSpec)) {
      supplied = targetSpec;
      source = "explicit target-curvature array";
    } else if (Array.isArray(targetSpec.targetCurvatures)) {
      supplied = targetSpec.targetCurvatures;
      source = "simulation.targetCurvatures";
    }
    var suppliedTotal;
    if (supplied) {
      if (supplied.length !== complex.nodes.length) errors.push("targetCurvatures length must equal the node count");
      if (supplied.some(function (value) { return typeof value !== "number" || !isFinite(value); })) errors.push("targetCurvatures must contain only finite numbers");
      suppliedTotal = supplied.reduce(function (sum, value) { return sum + finiteNumber(Number(value), 0); }, 0);
    } else if (targetSpec && targetSpec.targetTotal != null) {
      suppliedTotal = Number(targetSpec.targetTotal);
      source = "simulation.targetTotal";
      if (!isFinite(suppliedTotal)) errors.push("targetTotal must be finite");
    } else suppliedTotal = expectedTotal;
    var tol = Math.max(EPS, finiteNumber(Number(tolerance), 1e-8 * (1 + Math.abs(expectedTotal))));
    var residual = suppliedTotal - expectedTotal;
    if (isFinite(residual) && Math.abs(residual) > tol) {
      errors.push("Gauss–Bonnet obstruction: target curvature sums to " + suppliedTotal + " but 2πχ=" + expectedTotal);
    }
    return jsonSafe({
      admissible: errors.length === 0,
      necessaryConditionOnly: true,
      source: source,
      eulerCharacteristic: chi,
      suppliedTotal: suppliedTotal,
      requiredTotal: expectedTotal,
      residual: residual,
      tolerance: tol,
      errors: errors,
      caveat: "Matching ΣK=2πχ removes the global Gauss–Bonnet obstruction but is not sufficient for circle-packing realizability; additional local/subcomplex inequalities may apply."
    });
  }

  function curvatureTargets(complex, curvature, simulation) {
    simulation = simulation || {};
    var targetMode = simulation.targetMode || "uniform";
    var active = curvature.vertices;
    var total = curvature.targetTotal;
    var raw = new Array(complex.nodes.length).fill(0);
    if (Array.isArray(simulation.targetCurvatures) && simulation.targetCurvatures.length === complex.nodes.length) {
      return simulation.targetCurvatures.slice();
    }
    if (targetMode === "flat-interior" || targetMode === "boundary-wave") {
      var boundaryVertices = active.filter(function (v) { return v.boundary; });
      if (boundaryVertices.length) {
        boundaryVertices.forEach(function (entry) {
          var node = complex.nodes[entry.id];
          var angle = Math.atan2(node.y, node.x);
          raw[entry.id] = targetMode === "boundary-wave" ? Math.max(0.05, 1 + finiteNumber(Number(simulation.targetAmplitude), 0.55) * Math.cos(integer(simulation.targetFrequency, 3, 1, 12) * angle)) : 1;
        });
      } else active.forEach(function (entry) { raw[entry.id] = 1; });
    } else if (targetMode === "cap-gradient") {
      active.forEach(function (entry) { raw[entry.id] = Math.exp(finiteNumber(Number(simulation.targetStrength), 1.1) * complex.nodes[entry.id].z); });
    } else {
      active.forEach(function (entry) { raw[entry.id] = 1; });
    }
    var rawSum = raw.reduce(function (sum, value) { return sum + value; }, 0);
    if (Math.abs(rawSum) <= EPS) active.forEach(function (entry) { raw[entry.id] = 1; });
    rawSum = raw.reduce(function (sum, value) { return sum + value; }, 0);
    return raw.map(function (value) { return total * value / rawSum; });
  }

  function curvatureFlowStep(input, options) {
    options = options || {};
    var complex = canonicalizeComplex(input);
    if (!complex.faces.length) return { complex: complex, energyBefore: null, energyAfter: null, skipped: true, reason: "no triangular faces" };
    var admissibility = validateCurvatureTarget(complex, options);
    if (!admissibility.admissible) {
      return {
        complex: complex,
        energyBefore: null,
        energyAfter: null,
        skipped: true,
        rejected: true,
        reason: admissibility.errors.join("; "),
        targetAdmissibility: admissibility
      };
    }
    var rate = clamp(finiteNumber(Number(options.rate), 0.06), 0, 0.5);
    var before = angleDefectCurvature(complex, { metric: "circle-packing" });
    if (!before.available) {
      return { complex: complex, energyBefore: null, energyAfter: null, skipped: true, rejected: true, reason: before.caveat, surfaceValidity: before.surfaceValidity };
    }
    var targets = curvatureTargets(complex, before, options);
    var errors = [];
    before.vertices.forEach(function (entry) {
      var error = entry.defect - targets[entry.id];
      errors.push(error);
      var exponent = clamp(-rate * error, -0.3, 0.3);
      complex.nodes[entry.id].radius = clamp(complex.nodes[entry.id].radius * Math.exp(exponent), 0.03, 30);
    });
    complex.edges.forEach(function (edge) {
      edge.length = complex.nodes[edge.source].radius + complex.nodes[edge.target].radius;
    });
    complex.metadata.metric = "circle-packing";
    complex.metadata.intrinsicLengthRule = "edge.length = radius(source) + radius(target)";
    var after = angleDefectCurvature(complex, { metric: "circle-packing" });
    var afterTargets = curvatureTargets(complex, after, options);
    var afterErrors = after.vertices.map(function (entry) { return entry.defect - afterTargets[entry.id]; });
    function rms(values) { return Math.sqrt(values.reduce(function (sum, x) { return sum + x * x; }, 0) / Math.max(1, values.length)); }
    return jsonSafe({
      complex: complex,
      energyBefore: rms(errors),
      energyAfter: rms(afterErrors),
      targetMode: options.targetMode || "uniform",
      targetAdmissibility: admissibility,
      skipped: false,
      localityNote: "Each radius update uses only the node's incident triangular star. The state API compiles the target field before runtime; direct low-level calls may compile it once inside this call. No global gauge update is performed.",
      caveat: "This explicit circle-packing-style step is a demonstrator. Convergence depends on topology, admissible target curvature, triangulation, and step size."
    });
  }

  function randomWalkLaplacianValues(complex, field) {
    var data = adjacencyData(complex), next = new Array(complex.nodes.length).fill(0);
    data.adjacency.forEach(function (neighbors, i) {
      var degree = neighbors.reduce(function (sum, item) { return sum + item.weight; }, 0);
      if (degree <= EPS) { next[i] = 0; return; }
      next[i] = neighbors.reduce(function (sum, item) { return sum + item.weight * (field[item.node] - field[i]); }, 0) / degree;
    });
    return next;
  }

  function diffusionStep(input, options) {
    options = options || {};
    var complex = canonicalizeComplex(input);
    var dt = clamp(finiteNumber(Number(options.dt), 0.2), 0, 1);
    var diffusivity = clamp(finiteNumber(Number(options.diffusivity), 0.75), 0, 1);
    var values = complex.nodes.map(function (node) { return node.value; });
    var laplacian = randomWalkLaplacianValues(complex, values);
    complex.nodes.forEach(function (node, i) { node.value = values[i] + dt * diffusivity * laplacian[i]; });
    return { complex: complex, dt: dt, diffusivity: diffusivity, caveat: "The update is an explicit local random-walk diffusion step; dt·diffusivity≤1 enforces a convex neighbor averaging step." };
  }

  function reactionDiffusionStep(input, options) {
    options = options || {};
    var complex = canonicalizeComplex(input);
    var dt = clamp(finiteNumber(Number(options.dt), 0.5), 0, 1);
    var du = clamp(finiteNumber(Number(options.diffusionU), 0.18), 0, 1);
    var dv = clamp(finiteNumber(Number(options.diffusionV), 0.08), 0, 1);
    var feed = clamp(finiteNumber(Number(options.feed), 0.035), 0, 0.2);
    var kill = clamp(finiteNumber(Number(options.kill), 0.062), 0, 0.2);
    var u = complex.nodes.map(function (node) { return node.u; });
    var v = complex.nodes.map(function (node) { return node.v; });
    var lapU = randomWalkLaplacianValues(complex, u), lapV = randomWalkLaplacianValues(complex, v);
    complex.nodes.forEach(function (node, i) {
      var reaction = u[i] * v[i] * v[i];
      node.u = clamp(u[i] + dt * (du * lapU[i] - reaction + feed * (1 - u[i])), 0, 1.5);
      node.v = clamp(v[i] + dt * (dv * lapV[i] + reaction - (feed + kill) * v[i]), 0, 1.5);
      node.value = node.v;
    });
    return { complex: complex, dt: dt, model: "Gray–Scott-type reaction–diffusion on graph neighborhoods", caveat: "Pattern formation is qualitative and graph/discretization dependent; it is not a calibrated biological morphogenesis model." };
  }

  var BASE_CONFIG = {
    id: "custom",
    title: "Custom Global Geometry experiment",
    lens: "forward",
    application: "theory",
    question: "Which global observables arise from these local relations?",
    generator: { type: "triangulated-disk", rings: 3, sectors: 12, seed: "global-geometry", signal: "hotspot", disorder: 0 },
    analysis: { curvatureMetric: "embedded", volumeMetric: "intrinsic", maxEigenSize: 120, maxRadius: 8, sourceLimit: 120, walkSteps: 14, walkSourceLimit: 12 },
    simulation: { model: "diffusion", dt: 0.2, diffusivity: 0.75, rate: 0.06, targetMode: "uniform" },
    event: { type: "radius-pulse", index: 0, factor: 1.8 },
    locality: "L0 synchronous radius-one runtime; L1 target compilation and L2 analysis are disclosed separately",
    runtimeLocality: {
      updateClass: "L0",
      radius: 1,
      synchronous: true,
      reads: ["current node", "adjacent nodes", "incident triangular faces"],
      writes: ["current node state"],
      preRuntimeGlobal: ["target-curvature normalization/admissibility"],
      analysisClass: "L2",
      globalAnalysis: ["GF(2) homology", "Gauss–Bonnet audit", "eigenspectrum", "multiscale profiles"]
    },
    claims: {
      demonstrates: "A finite, reproducible relationship between local rules and selected global observables.",
      doesNotDemonstrate: "Uniqueness of a continuum limit or a physical mechanism without additional analysis."
    },
    caveats: []
  };

  var PRESET_SOURCE = {
    "forward-sphere-curvature": {
      id: "forward-sphere-curvature", title: "Forward lens · local defects make a sphere", lens: "forward", application: "theory",
      question: "How do incident-triangle angle sums encode a global Euler characteristic?",
      generator: { type: "icosphere", subdivisions: 1, radius: 1, seed: "sphere" },
      analysis: { curvatureMetric: "circle-packing", maxEigenSize: 120, maxRadius: 6 },
      simulation: { model: "curvature-flow", rate: 0.055, targetMode: "cap-gradient", targetStrength: 0.9 },
      event: { type: "radius-pulse", index: 0, factor: 2.1 },
      claims: { demonstrates: "Angle defects obey discrete Gauss–Bonnet and a neighbor-star feedback rule redistributes intrinsic curvature.", doesNotDemonstrate: "That every prescribed curvature is admissible or that the explicit flow always converges." },
      caveats: ["Display coordinates need not follow the evolving circle-packing metric."]
    },
    "forward-disk-boundary": {
      id: "forward-disk-boundary", title: "Forward lens · boundary turns close the disk", lens: "forward", application: "theory",
      question: "Where does the disk's 2π total curvature live when its interior is flat?",
      generator: { type: "triangulated-disk", rings: 4, sectors: 16, radius: 1 },
      analysis: { curvatureMetric: "embedded", maxEigenSize: 120, maxRadius: 7 },
      simulation: { model: "diffusion", dt: 0.25, diffusivity: 0.8 },
      event: { type: "jitter", magnitude: 0.025, seed: "disk-jitter" },
      claims: { demonstrates: "Boundary angle defects complete the Gauss–Bonnet balance for a piecewise-flat disk.", doesNotDemonstrate: "Extrinsic bending energy or a unique three-dimensional embedding." },
      caveats: ["The displayed disk is a fixed triangulation with polygonal boundary."]
    },
    "inverse-curvature-programming": {
      id: "inverse-curvature-programming", title: "Inverse lens · program a curvature profile", lens: "inverse", application: "programmable-materials",
      question: "Can local radius updates approximate a globally prescribed boundary-curvature pattern?",
      generator: { type: "triangulated-disk", rings: 4, sectors: 18, radius: 1 },
      analysis: { curvatureMetric: "circle-packing", maxEigenSize: 120, maxRadius: 7 },
      simulation: { model: "curvature-flow", rate: 0.045, targetMode: "boundary-wave", targetAmplitude: 0.6, targetFrequency: 3 },
      event: { type: "radius-pulse", index: 10, factor: 1.9 },
      claims: { demonstrates: "An inverse target can be translated into local curvature-error feedback while preserving the Gauss–Bonnet total.", doesNotDemonstrate: "Mechanical realizability, material stability, or convergence for arbitrary target fields." },
      caveats: ["Circle radii are abstract metric variables, not literal actuator dimensions."]
    },
    "recognition-swiss-roll": {
      id: "recognition-swiss-roll", title: "Recognition lens · infer geometry from samples", lens: "recognition", application: "machine-learning",
      question: "What do diffusion and ball growth reveal when only local sample similarities are given?",
      generator: { type: "point-cloud", shape: "swiss-roll", count: 58, k: 5, seed: "recognition" },
      analysis: { curvatureMetric: "embedded", maxEigenSize: 120, maxRadius: 9 },
      simulation: { model: "diffusion", dt: 0.3, diffusivity: 0.8 },
      event: { type: "add-cycle-edge" },
      claims: { demonstrates: "A local similarity graph supports reproducible spectral and volume-growth descriptors.", doesNotDemonstrate: "Recovery of the ground-truth manifold without a sampling and bandwidth theorem." },
      caveats: ["The k-nearest-neighbor graph is an estimator whose geometry changes with k and sampling density."]
    },
    "network-resilience": {
      id: "network-resilience", title: "Application · network resilience", lens: "forward", application: "networks",
      question: "How does one disclosed shortcut intervention alter cycle rank, spectral gap, and diffusion?",
      generator: { type: "graph", graphType: "grid", rows: 7, cols: 9 },
      simulation: { model: "diffusion", dt: 0.35, diffusivity: 0.9 },
      event: { type: "add-cycle-edge" },
      claims: { demonstrates: "A controlled edge edit has coupled topological and transport signatures.", doesNotDemonstrate: "Operational resilience under a domain-specific failure model." },
      caveats: ["Graph cycle rank treats every unfilled loop as a first-homology class."]
    },
    "metamaterial-sheet": {
      id: "metamaterial-sheet", title: "Application · programmable sheet", lens: "inverse", application: "metamaterials",
      question: "How can local metric variables redistribute a target curvature budget?",
      generator: { type: "triangulated-disk", rings: 3, sectors: 15 },
      analysis: { curvatureMetric: "circle-packing" },
      simulation: { model: "hybrid", rate: 0.04, targetMode: "boundary-wave", targetAmplitude: 0.5, targetFrequency: 5, dt: 0.2, diffusivity: 0.65 },
      event: { type: "radius-pulse", index: 4, factor: 1.7 },
      claims: { demonstrates: "Local metric feedback and transport can be coupled in a controllable abstract sheet.", doesNotDemonstrate: "A constitutive law or fabrication-ready metamaterial." },
      caveats: ["No elasticity, collision, or embedding solver is included."]
    },
    "morphogenesis-pattern": {
      id: "morphogenesis-pattern", title: "Application · morphogenesis pattern", lens: "forward", application: "morphogenesis",
      question: "How can local reaction and neighbor diffusion make an organized global field?",
      generator: { type: "triangulated-disk", rings: 5, sectors: 18 },
      simulation: { model: "reaction-diffusion", dt: 0.55, diffusionU: 0.18, diffusionV: 0.08, feed: 0.035, kill: 0.062 },
      event: { type: "value-pulse", index: 0, magnitude: 0.3 },
      claims: { demonstrates: "Local nonlinear reaction plus graph diffusion can amplify spatial organization.", doesNotDemonstrate: "A fitted developmental pathway or biological causal explanation." },
      caveats: ["This is a qualitative Gray–Scott-type graph model."]
    },
    "swarm-consensus": {
      id: "swarm-consensus", title: "Application · componentwise swarm consensus", lens: "forward", application: "distributed-robotics",
      question: "Why can neighbor averaging reach componentwise consensus but not one global value when β₀>1?",
      generator: { type: "point-cloud", shape: "clusters", count: 48, k: 4, seed: "swarm" },
      simulation: { model: "diffusion", dt: 0.4, diffusivity: 0.9 },
      event: { type: "add-cycle-edge" },
      claims: { demonstrates: "Disconnected components are a topological obstruction to global consensus; each zero Laplacian mode supports an independent component value.", doesNotDemonstrate: "Collision avoidance, communication delay robustness, or physical robot control." },
      caveats: ["Positions are fixed; this demo evolves information, not vehicle dynamics."]
    },
    "emergent-spacetime-toy": {
      id: "emergent-spacetime-toy", title: "Application · emergent-spacetime toy", lens: "recognition", application: "physics",
      question: "Can multiscale spectral and volume profiles make a graph look geometric?",
      generator: { type: "graph", graphType: "ring", count: 48, chord: 7 },
      simulation: { model: "diffusion", dt: 0.28, diffusivity: 0.8 },
      event: { type: "add-cycle-edge" },
      claims: { demonstrates: "A finite relational system has measurable scale-dependent transport and growth geometry.", doesNotDemonstrate: "Lorentzian spacetime, gravity, quantum dynamics, or emergence of our physical universe." },
      caveats: ["This is explicitly a graph-geometry analogy, not evidence for a theory of quantum gravity."]
    }
  };

  var PRESETS = {};
  var APPLICATION_KEYS = {
    theory: "theory",
    "programmable-materials": "materials",
    metamaterials: "materials",
    "machine-learning": "learning",
    networks: "networks",
    morphogenesis: "morphogenesis",
    "distributed-robotics": "swarms",
    physics: "physics"
  };
  Object.keys(PRESET_SOURCE).forEach(function (id) {
    var preset = mergeDeep(BASE_CONFIG, PRESET_SOURCE[id]);
    preset.mode = preset.lens.charAt(0).toUpperCase() + preset.lens.slice(1);
    preset.meta = mergeDeep(preset.meta || {}, {
      title: preset.title,
      mode: preset.mode,
      applicationKey: APPLICATION_KEYS[preset.application] || preset.application,
      question: preset.question,
      boundary: preset.claims.doesNotDemonstrate,
      locality: preset.locality,
      eventLabel: "Declared intervention"
    });
    PRESETS[id] = preset;
  });
  deepFreeze(PRESETS);

  var GENERATOR_TYPES = ["triangulated-disk", "icosphere", "triangulated-sphere", "graph", "point-cloud"];
  var LENSES = ["forward", "inverse", "recognition"];
  var MODELS = ["none", "diffusion", "curvature-flow", "reaction-diffusion", "hybrid"];
  var EVENT_TYPES = ["none", "radius-pulse", "value-pulse", "jitter", "puncture", "add-cycle-edge", "remove-edge"];

  function normalizeConfig(config) {
    var source;
    if (config && typeof config === "object" && typeof config.valid === "boolean" && config.config) {
      if (!config.valid) throw new Error("Cannot normalize an invalid validation report: " + (config.errors || []).join("; "));
      config = config.config;
    }
    if (typeof config === "string") {
      if (!PRESETS[config]) throw new Error("Unknown preset: " + config);
      source = PRESETS[config];
    } else if (config && config.preset) {
      if (!PRESETS[config.preset]) throw new Error("Unknown preset: " + config.preset);
      source = mergeDeep(PRESETS[config.preset], config);
    } else source = config || {};
    var normalized = mergeDeep(BASE_CONFIG, source);
    normalized.mode = normalized.lens.charAt(0).toUpperCase() + normalized.lens.slice(1);
    return normalized;
  }

  var CONFIG_FIELDS = {
    top: ["preset", "id", "title", "lens", "mode", "application", "question", "generator", "analysis", "simulation", "event", "locality", "runtimeLocality", "claims", "caveats", "meta"],
    generator: ["type", "rings", "sectors", "seed", "signal", "subdivisions", "radius", "graphType", "shape", "rows", "cols", "count", "chord", "k", "sigma", "disorder", "jitter"],
    analysis: ["curvatureMetric", "volumeMetric", "maxEigenSize", "maxRadius", "sourceLimit", "heatTimes", "walkSteps", "walkSourceLimit", "tolerance", "maxSweeps"],
    simulation: ["model", "dt", "diffusivity", "rate", "targetMode", "targetAmplitude", "targetFrequency", "targetStrength", "targetTotal", "targetCurvatures", "diffusionU", "diffusionV", "feed", "kill"],
    event: ["type", "index", "nodeId", "faceIndex", "edgeIndex", "factor", "weight", "magnitude", "seed"],
    runtimeLocality: ["updateClass", "radius", "synchronous", "reads", "writes", "preRuntimeGlobal", "analysisClass", "globalAnalysis"],
    claims: ["demonstrates", "doesNotDemonstrate"],
    meta: ["title", "mode", "applicationKey", "application", "question", "boundary", "caveat", "mechanism", "observable", "locality", "eventLabel"]
  };

  function unknownConfigFields(config) {
    if (!config || typeof config !== "object" || Array.isArray(config)) return [];
    var errors = [];
    function audit(object, allowed, prefix) {
      if (!object || typeof object !== "object" || Array.isArray(object)) return;
      Object.keys(object).forEach(function (key) { if (allowed.indexOf(key) < 0) errors.push("unknown config field " + prefix + key); });
    }
    audit(config, CONFIG_FIELDS.top, "");
    ["generator", "analysis", "simulation", "event", "runtimeLocality", "claims", "meta"].forEach(function (section) {
      audit(config[section], CONFIG_FIELDS[section], section + ".");
    });
    return errors;
  }

  function checkRange(errors, value, name, lo, hi, integerOnly) {
    if (value == null) return;
    if (typeof value !== "number" || !isFinite(value) || value < lo || value > hi || (integerOnly && !Number.isInteger(value))) {
      errors.push(name + " must be " + (integerOnly ? "an integer " : "a finite number ") + "in [" + lo + ", " + hi + "]");
    }
  }

  function validateConfig(config) {
    var errors = [], warnings = [], normalized;
    if (config && typeof config === "object" && typeof config.valid === "boolean" && config.config) config = config.config;
    if (typeof config !== "string") errors = errors.concat(unknownConfigFields(config));
    if (config && typeof config === "object") {
      var numericFields = {
        generator: ["rings", "sectors", "subdivisions", "radius", "rows", "cols", "count", "chord", "k", "sigma", "disorder", "jitter"],
        analysis: ["maxEigenSize", "maxRadius", "sourceLimit", "walkSteps", "walkSourceLimit", "tolerance", "maxSweeps"],
        simulation: ["dt", "diffusivity", "rate", "targetAmplitude", "targetFrequency", "targetStrength", "targetTotal", "diffusionU", "diffusionV", "feed", "kill"],
        event: ["index", "nodeId", "faceIndex", "edgeIndex", "factor", "weight", "magnitude"]
      };
      Object.keys(numericFields).forEach(function (section) {
        numericFields[section].forEach(function (field) {
          if (config[section] && Object.prototype.hasOwnProperty.call(config[section], field) && (typeof config[section][field] !== "number" || !isFinite(config[section][field]))) {
            errors.push(section + "." + field + " must be a finite number");
          }
        });
      });
    }
    try { normalized = normalizeConfig(config); }
    catch (error) { return { valid: false, errors: [error.message], warnings: [], config: null }; }
    if (typeof normalized.id !== "string" || !normalized.id.trim()) errors.push("id must be a non-empty string");
    if (LENSES.indexOf(normalized.lens) < 0) errors.push("lens must be forward, inverse, or recognition");
    if (!normalized.generator || GENERATOR_TYPES.indexOf(normalized.generator.type) < 0) errors.push("generator.type is unsupported");
    if (["hotspot", "generator", "random", "gradient", "checker"].indexOf(normalized.generator.signal) < 0) errors.push("generator.signal is unsupported");
    if (normalized.generator.graphType != null && ["grid", "ring"].indexOf(normalized.generator.graphType) < 0) errors.push("generator.graphType is unsupported");
    if (normalized.generator.shape != null && ["swiss-roll", "circle", "clusters", "grid", "ring"].indexOf(normalized.generator.shape) < 0) errors.push("generator.shape is unsupported");
    if (!normalized.simulation || MODELS.indexOf(normalized.simulation.model) < 0) errors.push("simulation.model is unsupported");
    if (["uniform", "flat-interior", "boundary-wave", "cap-gradient"].indexOf(normalized.simulation.targetMode) < 0) errors.push("simulation.targetMode is unsupported");
    if (["embedded", "circle-packing"].indexOf(normalized.analysis.curvatureMetric) < 0) errors.push("analysis.curvatureMetric is unsupported");
    if (normalized.analysis.volumeMetric != null && ["intrinsic", "hop"].indexOf(normalized.analysis.volumeMetric) < 0) errors.push("analysis.volumeMetric is unsupported");
    if (normalized.event && EVENT_TYPES.indexOf(normalized.event.type || "none") < 0) errors.push("event.type is unsupported");
    if (normalized.generator.type === "point-cloud" && Number(normalized.generator.k) >= Number(normalized.generator.count)) errors.push("point-cloud k must be less than count");
    if ((normalized.simulation.model === "curvature-flow" || normalized.simulation.model === "hybrid") && ["triangulated-disk", "icosphere", "triangulated-sphere"].indexOf(normalized.generator.type) < 0) {
      errors.push("curvature flow requires a triangular surface generator");
    }
    if (errors.length === 0 && (normalized.simulation.targetTotal != null || Array.isArray(normalized.simulation.targetCurvatures))) {
      try {
        var targetReport = validateCurvatureTarget(generateComplex(normalized.generator), normalized.simulation);
        if (!targetReport.admissible) errors = errors.concat(targetReport.errors);
      } catch (targetError) {
        errors.push("could not validate curvature target: " + targetError.message);
      }
    }
    if (normalized.analysis.maxEigenSize > 240) warnings.push("A large dense eigensolver limit can block the browser UI.");
    if (!normalized.claims || !normalized.claims.demonstrates || !normalized.claims.doesNotDemonstrate) warnings.push("Scientific presets should state both demonstrated and unsupported claims.");
    checkRange(errors, normalized.generator.rings, "generator.rings", 1, 12, true);
    checkRange(errors, normalized.generator.sectors, "generator.sectors", 3, 64, true);
    checkRange(errors, normalized.generator.subdivisions, "generator.subdivisions", 0, 3, true);
    checkRange(errors, normalized.generator.radius, "generator.radius", 0.05, 100, false);
    checkRange(errors, normalized.generator.rows, "generator.rows", 2, 40, true);
    checkRange(errors, normalized.generator.cols, "generator.cols", 2, 40, true);
    checkRange(errors, normalized.generator.count, "generator.count", 4, 300, true);
    checkRange(errors, normalized.generator.k, "generator.k", 1, 20, true);
    checkRange(errors, normalized.generator.chord, "generator.chord", 0, 150, true);
    checkRange(errors, normalized.generator.sigma, "generator.sigma", EPS, 1e6, false);
    checkRange(errors, normalized.generator.disorder, "generator.disorder", 0, 1, false);
    checkRange(errors, normalized.generator.jitter, "generator.jitter", 0, 1, false);
    checkRange(errors, normalized.analysis.maxEigenSize, "analysis.maxEigenSize", 4, 400, true);
    checkRange(errors, normalized.analysis.maxRadius, "analysis.maxRadius", 1, 100, true);
    checkRange(errors, normalized.analysis.sourceLimit, "analysis.sourceLimit", 1, 2000, true);
    checkRange(errors, normalized.analysis.walkSteps, "analysis.walkSteps", 2, 60, true);
    checkRange(errors, normalized.analysis.walkSourceLimit, "analysis.walkSourceLimit", 1, 300, true);
    checkRange(errors, normalized.simulation.dt, "simulation.dt", 0, 1, false);
    checkRange(errors, normalized.simulation.diffusivity, "simulation.diffusivity", 0, 1, false);
    checkRange(errors, normalized.simulation.rate, "simulation.rate", 0, 0.5, false);
    checkRange(errors, normalized.simulation.diffusionU, "simulation.diffusionU", 0, 1, false);
    checkRange(errors, normalized.simulation.diffusionV, "simulation.diffusionV", 0, 1, false);
    checkRange(errors, normalized.simulation.feed, "simulation.feed", 0, 0.2, false);
    checkRange(errors, normalized.simulation.kill, "simulation.kill", 0, 0.2, false);
    checkRange(errors, normalized.simulation.targetAmplitude, "simulation.targetAmplitude", 0, 0.95, false);
    checkRange(errors, normalized.simulation.targetFrequency, "simulation.targetFrequency", 1, 12, true);
    checkRange(errors, normalized.simulation.targetStrength, "simulation.targetStrength", -10, 10, false);
    checkRange(errors, normalized.event.factor, "event.factor", 0.01, 100, false);
    checkRange(errors, normalized.event.weight, "event.weight", EPS, 1e6, false);
    checkRange(errors, normalized.event.magnitude, "event.magnitude", 0, 10, false);
    checkRange(errors, normalized.event.index, "event.index", 0, 1000000, true);
    checkRange(errors, normalized.event.nodeId, "event.nodeId", 0, 1000000, true);
    if (normalized.generator.type === "point-cloud" && normalized.generator.count < 8) errors.push("point-cloud count must be at least 8");
    if (normalized.runtimeLocality.updateClass !== "L0" || normalized.runtimeLocality.radius !== 1 || normalized.runtimeLocality.synchronous !== true) errors.push("runtimeLocality must disclose the implemented synchronous L0 radius-one update contract");
    if (normalized.runtimeLocality.analysisClass !== "L2") errors.push("runtimeLocality.analysisClass must disclose global L2 analysis");
    if (normalized.analysis.heatTimes != null && (!Array.isArray(normalized.analysis.heatTimes) || !normalized.analysis.heatTimes.length || normalized.analysis.heatTimes.some(function (time) { return typeof time !== "number" || !isFinite(time) || time <= 0; }))) errors.push("analysis.heatTimes must be a non-empty array of positive finite numbers");
    if (!Array.isArray(normalized.caveats) || normalized.caveats.some(function (value) { return typeof value !== "string"; })) errors.push("caveats must be an array of strings");
    return { valid: errors.length === 0, errors: errors, warnings: warnings, config: jsonSafe(normalized) };
  }

  function listPresets() {
    return Object.keys(PRESETS).map(function (id) {
      var p = PRESETS[id];
      return { id: id, title: p.title, lens: p.lens, application: p.application, question: p.question };
    });
  }

  function initializeNodeFields(complex, config) {
    var random = seededRandom((config.generator && config.generator.seed) || config.id);
    var signal = config.generator.signal || "generator";
    complex.nodes.forEach(function (node, i) {
      if (signal === "random") node.value = random();
      else if (signal === "gradient") node.value = 0.5 + 0.5 * node.x;
      else if (signal === "checker") node.value = (Math.floor((node.x + 1) * 4) + Math.floor((node.y + 1) * 4)) % 2;
      if (!isFinite(node.value)) node.value = i === 0 ? 1 : 0;
      node.radius = clamp(node.radius * (1 + 0.025 * Math.sin(i * 1.61803398875)), 0.05, 20);
      if (!isFinite(node.u)) node.u = 1;
      if (!isFinite(node.v)) node.v = i % 17 === 0 ? 0.12 : 0;
    });
    var disorder = clamp(finiteNumber(Number(config.generator.disorder), 0), 0, 1);
    if (disorder > 0) {
      var disorderRandom = seededRandom(((config.generator && config.generator.seed) || config.id) + "::disorder");
      complex.nodes.forEach(function (node) {
        node.x += (disorderRandom() - 0.5) * 0.08 * disorder;
        node.y += (disorderRandom() - 0.5) * 0.08 * disorder;
        node.z += (disorderRandom() - 0.5) * 0.08 * disorder;
        node.radius = clamp(node.radius * Math.exp((disorderRandom() - 0.5) * 0.3 * disorder), 0.05, 20);
      });
      complex.edges.forEach(function (edge) {
        edge.length = distance(complex.nodes[edge.source], complex.nodes[edge.target]);
        edge.weight *= Math.exp((disorderRandom() - 0.5) * 0.4 * disorder);
      });
      complex.metadata.disorder = disorder;
      complex.metadata.disorderSemantics = "Seeded bounded perturbation of source coordinates, intrinsic initial lengths/radii, and graph weights; the browser projection itself remains display-only.";
    }
    return complex;
  }

  function stateComplex(state) {
    return canonicalizeComplex({ nodes: state.nodes, edges: state.edges, faces: state.faces, metadata: state.metadata });
  }

  function analyzeState(state, options) {
    options = mergeDeep((state.config && state.config.analysis) || {}, options || {});
    var complex = stateComplex(state);
    var topology = computeBettiNumbers(complex);
    var curvatureMetric = options.curvatureMetric || ((state.config && (state.config.simulation.model === "curvature-flow" || state.config.simulation.model === "hybrid")) ? "circle-packing" : "embedded");
    var curvature = angleDefectCurvature(complex, { metric: curvatureMetric });
    var hasCurvatureTarget = state.config && state.config.simulation && (
      state.config.simulation.model === "curvature-flow" ||
      state.config.simulation.model === "hybrid" ||
      Array.isArray(state.config.simulation.targetCurvatures) ||
      state.config.simulation.targetTotal != null
    );
    if (curvature.available && hasCurvatureTarget) {
      var targetSimulation = (state.config && state.config.simulation) || {};
      curvature.targetAdmissibility = validateCurvatureTarget(complex, targetSimulation);
      curvature.targets = curvatureTargets(complex, curvature, targetSimulation);
      var targetErrors = [];
      curvature.vertices.forEach(function (entry) {
        entry.target = curvature.targets[entry.id];
        entry.error = entry.defect - entry.target;
        targetErrors.push(entry.error);
      });
      curvature.targetRmsError = Math.sqrt(targetErrors.reduce(function (sum, error) { return sum + error * error; }, 0) / Math.max(1, targetErrors.length));
      curvature.rmsError = curvature.targetRmsError;
    }
    var spectrum = normalizedLaplacianSpectrum(complex, options);
    var volume = volumeGrowthProfile(complex, options);
    var walk = walkDimensionProfile(complex, options);
    var spectralProfile = spectrum.available ? spectrum.spectralDimensionProfile : [];
    var diagnostics = [];
    if (curvature.available && Math.abs(curvature.gaussBonnetResidual) > 1e-7) diagnostics.push({ level: "warning", code: "GAUSS_BONNET_RESIDUAL", message: "Residual exceeds the expected floating-point tolerance; inspect degeneracy or non-manifold structure." });
    if (!topology.manifoldCheck.isEdgeManifold) diagnostics.push({ level: "warning", code: "NON_MANIFOLD_EDGE", message: "Some edges have more than two incident faces." });
    if (!spectrum.available) diagnostics.push({ level: "info", code: "SPECTRUM_SKIPPED", message: spectrum.reason });
    return jsonSafe({
      schemaVersion: 1,
      step: state.step || 0,
      topology: topology,
      curvature: curvature,
      dimensions: {
        volumeGrowth: volume.profile,
        spectralProfile: spectralProfile,
        walkProfile: walk.profile,
        volume: volume,
        spectral: { profile: spectralProfile, interpretation: spectrum.interpretation || null, caveat: spectrum.caveat },
        walk: walk
      },
      spectrum: spectrum,
      diagnostics: diagnostics,
      locality: {
        updateClass: state.config && state.config.runtimeLocality ? state.config.runtimeLocality.updateClass : "L0",
        radius: state.config && state.config.runtimeLocality ? state.config.runtimeLocality.radius : 1,
        analysisClass: "L2",
        oneStepConeFromNodeZero: causalCone(complex, [0], 1),
        interpretation: "Runtime updates read only the current node and its adjacent nodes/faces before a synchronous write. Target compilation and global analysis are explicitly outside the L0 runtime.",
        runtimeContract: state.config && state.config.runtimeLocality ? state.config.runtimeLocality : null
      },
      scientificStatus: {
        demonstrated: state.config && state.config.claims ? state.config.claims.demonstrates : BASE_CONFIG.claims.demonstrates,
        notDemonstrated: state.config && state.config.claims ? state.config.claims.doesNotDemonstrate : BASE_CONFIG.claims.doesNotDemonstrate,
        caveats: (state.config && state.config.caveats ? state.config.caveats : []).concat([
          topology.caveat,
          curvature.caveat,
          spectrum.caveat,
          volume.caveat,
          walk.caveat
        ].filter(Boolean))
      }
    });
  }

  function createState(configOrPreset) {
    var validation = validateConfig(configOrPreset);
    if (!validation.valid) throw new Error("Invalid Global Geometry config: " + validation.errors.join("; "));
    var config = validation.config;
    var complex = initializeNodeFields(generateComplex(config.generator), config);
    if (config.simulation.model === "curvature-flow" || config.simulation.model === "hybrid") {
      complex.edges.forEach(function (edge) {
        edge.length = complex.nodes[edge.source].radius + complex.nodes[edge.target].radius;
      });
      complex.metadata.metric = "circle-packing";
      complex.metadata.intrinsicLengthRule = "edge.length = radius(source) + radius(target)";
      var initialCurvature = angleDefectCurvature(complex, { metric: "circle-packing" });
      if (!initialCurvature.available) throw new Error("Curvature simulation requires a valid triangular 2-manifold: " + initialCurvature.caveat);
      config.simulation.targetCurvatures = curvatureTargets(complex, initialCurvature, config.simulation);
      complex.metadata.targetCompilation = "Global pre-runtime normalization enforces Σ target K=2πχ; synchronous runtime updates are radius-one local.";
    }
    var state = {
      version: VERSION,
      config: config,
      step: 0,
      time: 0,
      nodes: complex.nodes,
      edges: complex.edges,
      faces: complex.faces,
      metadata: mergeDeep(complex.metadata, { lens: config.lens, application: config.application }),
      lastEvent: null,
      lastStep: null,
      analysis: null
    };
    state.analysis = analyzeState(state);
    return jsonSafe(state);
  }

  function stepState(state, overrides) {
    var next = cloneJSON(state);
    var simulation = mergeDeep((next.config && next.config.simulation) || BASE_CONFIG.simulation, overrides || {});
    var strength = overrides && overrides.strength != null ? clamp(finiteNumber(Number(overrides.strength), 1), 0, 2) : 1;
    simulation.rate = finiteNumber(Number(simulation.rate), 0.06) * strength;
    simulation.diffusivity = clamp(finiteNumber(Number(simulation.diffusivity), 0.75) * strength, 0, 1);
    if (simulation.diffusionU != null) simulation.diffusionU = clamp(Number(simulation.diffusionU) * strength, 0, 1);
    if (simulation.diffusionV != null) simulation.diffusionV = clamp(Number(simulation.diffusionV) * strength, 0, 1);
    var complex = stateComplex(next), reports = [];
    if (simulation.model === "curvature-flow" || simulation.model === "hybrid") {
      var flow = curvatureFlowStep(complex, simulation); complex = flow.complex; reports.push({ model: "curvature-flow", energyBefore: flow.energyBefore, energyAfter: flow.energyAfter, skipped: flow.skipped || false });
    }
    if (simulation.model === "diffusion" || simulation.model === "hybrid") {
      var diffusion = diffusionStep(complex, simulation); complex = diffusion.complex; reports.push({ model: "diffusion", dt: diffusion.dt, diffusivity: diffusion.diffusivity });
    }
    if (simulation.model === "reaction-diffusion") {
      var reaction = reactionDiffusionStep(complex, simulation); complex = reaction.complex; reports.push({ model: "reaction-diffusion", dt: reaction.dt });
    }
    next.nodes = complex.nodes; next.edges = complex.edges; next.faces = complex.faces; next.metadata = complex.metadata;
    next.step = (next.step || 0) + 1;
    next.time = finiteNumber(next.time, 0) + finiteNumber(Number(simulation.dt), 1);
    next.lastStep = { model: simulation.model, reports: reports };
    next.analysis = overrides && overrides.analyze === false ? null : analyzeState(next);
    return jsonSafe(next);
  }

  function firstMissingEdge(complex) {
    var existing = Object.create(null);
    complex.edges.forEach(function (edge) { existing[edgeKey(edge.source, edge.target)] = true; });
    for (var span = complex.nodes.length - 1; span >= 2; span -= 1) {
      for (var a = 0; a + span < complex.nodes.length; a += 1) {
        var b = a + span;
        if (!existing[edgeKey(a, b)]) return [a, b];
      }
    }
    return null;
  }

  function applyTopologyEvent(state, event) {
    var next = cloneJSON(state);
    event = mergeDeep((next.config && next.config.event) || { type: "none" }, event || {});
    var complex = stateComplex(next);
    var before = computeBettiNumbers(complex);
    var type = event.type || "none", description = "No event applied.";
    if (type === "puncture") {
      if (complex.faces.length) {
        var faceIndex = integer(event.faceIndex, 0, 0, complex.faces.length - 1);
        complex.faces.splice(faceIndex, 1);
        complex = canonicalizeComplex(complex);
        description = "Removed triangular 2-cell " + faceIndex + " while retaining its boundary edges.";
      } else description = "Puncture skipped because the complex has no faces.";
    } else if (type === "add-cycle-edge") {
      var pair = firstMissingEdge(complex);
      if (pair) {
        complex.edges.push({ source: pair[0], target: pair[1], weight: finiteNumber(Number(event.weight), 1), length: distance(complex.nodes[pair[0]], complex.nodes[pair[1]]) });
        complex = canonicalizeComplex(complex);
        description = "Added nonlocal graph edge " + pair[0] + "–" + pair[1] + ".";
      } else description = "Cycle-edge event skipped because the graph is complete.";
    } else if (type === "remove-edge") {
      if (complex.edges.length) {
        var edgeIndex = integer(event.edgeIndex, complex.edges.length - 1, 0, complex.edges.length - 1);
        var removed = complex.edges[edgeIndex];
        complex.edges.splice(edgeIndex, 1);
        complex.faces = complex.faces.filter(function (face) { return !(face.indexOf(removed.source) >= 0 && face.indexOf(removed.target) >= 0); });
        complex = canonicalizeComplex(complex);
        description = "Removed edge " + removed.source + "–" + removed.target + " and incident faces to preserve closure.";
      }
    } else if (type === "radius-pulse") {
      var radiusIndex = integer(event.nodeId, integer(event.index, 0, 0, complex.nodes.length - 1), 0, complex.nodes.length - 1);
      complex.nodes[radiusIndex].radius = clamp(complex.nodes[radiusIndex].radius * finiteNumber(Number(event.factor), 1.8), 0.03, 30);
      description = "Applied a deterministic local metric pulse at node " + radiusIndex + ".";
    } else if (type === "value-pulse") {
      var valueIndex = integer(event.nodeId, integer(event.index, 0, 0, complex.nodes.length - 1), 0, complex.nodes.length - 1);
      complex.nodes[valueIndex].value += finiteNumber(Number(event.magnitude), 0.5);
      complex.nodes[valueIndex].v = clamp(complex.nodes[valueIndex].v + finiteNumber(Number(event.magnitude), 0.3), 0, 1.5);
      description = "Applied a deterministic scalar-field pulse at node " + valueIndex + ".";
    } else if (type === "jitter") {
      var random = seededRandom(event.seed || "jitter");
      var magnitude = clamp(finiteNumber(Number(event.magnitude), 0.02), 0, 0.5);
      complex.nodes.forEach(function (node) { node.x += (random() - 0.5) * 2 * magnitude; node.y += (random() - 0.5) * 2 * magnitude; node.z += (random() - 0.5) * 2 * magnitude; });
      complex.edges.forEach(function (edge) { edge.length = distance(complex.nodes[edge.source], complex.nodes[edge.target]); });
      description = "Applied seeded coordinate jitter with magnitude " + magnitude + ".";
    }
    next.nodes = complex.nodes; next.edges = complex.edges; next.faces = complex.faces; next.metadata = complex.metadata;
    next.analysis = analyzeState(next);
    var after = next.analysis.topology;
    next.lastEvent = {
      type: type,
      description: description,
      beforeBetti: before.betti,
      afterBetti: after.betti,
      beforeEulerCharacteristic: before.eulerCharacteristic,
      afterEulerCharacteristic: after.eulerCharacteristic,
      topologyChanged: JSON.stringify(before.betti.array) !== JSON.stringify(after.betti.array)
    };
    return jsonSafe(next);
  }

  function cloneConfig(config) { return cloneJSON(normalizeConfig(config)); }
  function cloneState(state) { return cloneJSON(state); }

  return {
    VERSION: VERSION,
    PRESETS: PRESETS,
    listPresets: listPresets,
    validateConfig: validateConfig,
    validateComplex: validateComplex,
    cloneConfig: cloneConfig,
    cloneState: cloneState,
    jsonSafe: jsonSafe,
    seededRandom: seededRandom,
    generateComplex: generateComplex,
    generateTriangulatedDisk: generateTriangulatedDisk,
    generateIcosphere: generateIcosphere,
    generateGraph: generateGraph,
    generatePointCloud: generatePointCloud,
    computeBettiNumbers: computeBettiNumbers,
    surfaceValidity: surfaceValidity,
    angleDefectCurvature: angleDefectCurvature,
    normalizedLaplacian: normalizedLaplacian,
    normalizedLaplacianSpectrum: normalizedLaplacianSpectrum,
    volumeGrowthProfile: volumeGrowthProfile,
    walkDimensionProfile: walkDimensionProfile,
    causalCone: causalCone,
    validateCurvatureTarget: validateCurvatureTarget,
    curvatureFlowStep: curvatureFlowStep,
    diffusionStep: diffusionStep,
    reactionDiffusionStep: reactionDiffusionStep,
    createState: createState,
    stepState: stepState,
    analyzeState: analyzeState,
    applyTopologyEvent: applyTopologyEvent
  };
});
