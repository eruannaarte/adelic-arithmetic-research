/*
 * Global Geometry II — deterministic filled-disk preview families.
 *
 * This dependency-free UMD slice implements the four positive U2 construction
 * motifs at browser-preview sizes.  It deliberately stops before statistical
 * ensembles: every generated finite complex receives a mixed finite
 * certificate whose exact combinatorics and binary64 geometry checks remain
 * explicitly separated.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    var extension = null;
    try { extension = require("./global-geometry-ii-core.js"); }
    catch (error) { extension = null; }
    module.exports = factory(require("./global-geometry-core.js"), extension);
  } else {
    root.GlobalGeometryIIEnsembles = factory(root.GlobalGeometryCore, root.GlobalGeometryII || null);
  }
})(typeof self !== "undefined" ? self : this, function (Base, Extension) {
  "use strict";

  if (!Base) throw new Error("Global Geometry II ensembles require GlobalGeometryCore.");

  var VERSION = "0.2.0-alpha.3";
  var FAMILY_SCHEMA = "gg.atlas.family-preview/1";
  var PRNG_CONTRACT = "gg-fnv1a32-mulberry32-v1";
  var MAX_LINEAR_SIZE = 24;
  var MIN_CHARACTERISTIC_SPACING = 1e-5;
  var LOG_FOUR = Math.log(4);
  var GAUSS_BONNET_TOLERANCE = 1e-9;
  var FAMILY_IDS = [
    "square-alternating",
    "triangular-clipped",
    "cell-center-fan",
    "square-hashed-diagonal"
  ];
  var PREVIEW_RESOURCE_POLICY = deepFreeze({
    id: "ggii-family-preview-resource-v1",
    maxVertices: 1250,
    maxEdges: 3600,
    maxFaces: 2400,
    maxDiameterPairs: 750000,
    maxDenseGF2BasisBytesEstimate: 10000000,
    estimateCaveat: "Dense GF(2) bytes count Uint8Array basis payloads only; JavaScript object overhead and transient allocations are excluded."
  });

  function isPlainObject(value) {
    if (!value || typeof value !== "object" || Array.isArray(value)) return false;
    if (Object.prototype.toString.call(value) !== "[object Object]") return false;
    var prototype = Object.getPrototypeOf(value);
    if (prototype === null) return true;
    if (!Object.prototype.hasOwnProperty.call(prototype, "constructor")) return false;
    return typeof prototype.constructor === "function" &&
      Function.prototype.toString.call(prototype.constructor) === Function.prototype.toString.call(Object);
  }

  function finiteNumber(value) {
    return typeof value === "number" && isFinite(value) && !Object.is(value, -0);
  }

  function cloneJSON(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function deepFreeze(value) {
    if (!value || typeof value !== "object" || Object.isFrozen(value)) return value;
    Object.keys(value).forEach(function (key) { deepFreeze(value[key]); });
    return Object.freeze(value);
  }

  function hasOwn(object, key) {
    return Object.prototype.hasOwnProperty.call(object, key);
  }

  function unknownKeys(input, allowed) {
    if (!isPlainObject(input)) return [];
    return Object.keys(input).filter(function (key) { return allowed.indexOf(key) < 0; }).sort();
  }

  function denseArray(value) {
    if (!Array.isArray(value) || Object.keys(value).length !== value.length) return false;
    for (var index = 0; index < value.length; index += 1) {
      if (!Object.prototype.hasOwnProperty.call(value, index)) return false;
    }
    return true;
  }

  function stableStringify(value) {
    function canonical(item, path, depth) {
      path = path || "root";
      depth = depth || 0;
      if (depth > 64) throw new Error(path + " exceeds the maximum serialization depth.");
      if (item === null || typeof item === "string" || typeof item === "boolean") return item;
      if (typeof item === "number") {
        if (!isFinite(item)) throw new Error(path + " contains a non-finite number.");
        if (Math.abs(item) < 1e-15) return 0;
        return Number(item.toPrecision(14));
      }
      if (Array.isArray(item)) {
        if (!denseArray(item)) throw new Error(path + " must be a dense index-only array.");
        if (item.length > 262144) throw new Error(path + " exceeds the maximum array length.");
        return item.map(function (entry, index) { return canonical(entry, path + "[" + index + "]", depth + 1); });
      }
      if (isPlainObject(item)) {
        var out = {};
        var keys = Object.keys(item).sort();
        if (keys.length > 10000) throw new Error(path + " exceeds the maximum object field count.");
        keys.forEach(function (key) {
          if (key === "__proto__" || key === "prototype" || key === "constructor") {
            throw new Error(path + " contains a forbidden object key.");
          }
          if (typeof item[key] === "undefined" || typeof item[key] === "function") {
            throw new Error(path + "." + key + " is not serializable.");
          }
          out[key] = canonical(item[key], path + "." + key, depth + 1);
        });
        return out;
      }
      throw new Error(path + " contains an unsupported value.");
    }
    return JSON.stringify(canonical(value));
  }

  function fnv1a32(text) {
    var hash = 2166136261 >>> 0;
    for (var index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return ("00000000" + (hash >>> 0).toString(16)).slice(-8);
  }

  function digestValue(value) {
    return fnv1a32(stableStringify(value));
  }

  function coordinateHash(streamSeed, objectCanonicalKey) {
    if (typeof streamSeed !== "string" || !streamSeed.length || streamSeed.length > 256) {
      throw new Error("streamSeed must be a non-empty string of at most 256 characters.");
    }
    if (typeof objectCanonicalKey !== "string" || !objectCanonicalKey.length || objectCanonicalKey.length > 512) {
      throw new Error("objectCanonicalKey must be a non-empty string of at most 512 characters.");
    }
    return digestValue([PRNG_CONTRACT, streamSeed, objectCanonicalKey]);
  }

  function coordinateUniform(streamSeed, objectCanonicalKey) {
    return Base.seededRandom(coordinateHash(streamSeed, objectCanonicalKey))();
  }

  function padInteger(value) {
    return ("000000" + String(value)).slice(-6);
  }

  function pointKey(rowCoordinate, columnCoordinate) {
    return "p:" + padInteger(rowCoordinate) + ":" + padInteger(columnCoordinate);
  }

  function cellKey(row, column) {
    return "cell:" + padInteger(row) + ":" + padInteger(column);
  }

  function estimatePreviewResources(familyId, linearSize) {
    if (FAMILY_IDS.indexOf(familyId) < 0) throw new Error("familyId must name a registered filled-disk family.");
    if (!Number.isInteger(linearSize) || linearSize < 2 || linearSize > 1000) {
      throw new Error("linearSize must be an integer in [2, 1000] for a preview resource estimate.");
    }
    var vertices, edges, faces, strips = null;
    if (familyId === "cell-center-fan") {
      vertices = 2 * linearSize * linearSize + 2 * linearSize + 1;
      faces = 4 * linearSize * linearSize;
      edges = vertices + faces - 1;
    } else if (familyId === "triangular-clipped") {
      strips = Math.floor(2 * linearSize / Math.sqrt(3));
      var rowCount = strips + 1;
      var evenRows = Math.ceil(rowCount / 2), oddRows = Math.floor(rowCount / 2);
      vertices = evenRows * (linearSize + 1) + oddRows * linearSize;
      faces = strips * (2 * linearSize - 1);
      edges = vertices + faces - 1;
    } else {
      vertices = (linearSize + 1) * (linearSize + 1);
      faces = 2 * linearSize * linearSize;
      edges = vertices + faces - 1;
    }
    var diameterPairs = vertices * (vertices - 1) / 2;
    var denseGF2BasisBytesEstimate = vertices * Math.min(vertices, edges) +
      edges * Math.min(edges, faces);
    return deepFreeze({
      familyId: familyId,
      linearSize: linearSize,
      triangularStripCount: strips,
      vertices: vertices,
      edges: edges,
      faces: faces,
      simplexCount: vertices + edges + faces,
      diameterPairs: diameterPairs,
      denseGF2BasisBytesEstimate: denseGF2BasisBytesEstimate
    });
  }

  function previewResourceReport(familyId, linearSize) {
    var estimate = estimatePreviewResources(familyId, linearSize), errors = [];
    [
      ["vertices", "maxVertices"],
      ["edges", "maxEdges"],
      ["faces", "maxFaces"],
      ["diameterPairs", "maxDiameterPairs"],
      ["denseGF2BasisBytesEstimate", "maxDenseGF2BasisBytesEstimate"]
    ].forEach(function (fields) {
      if (estimate[fields[0]] > PREVIEW_RESOURCE_POLICY[fields[1]]) {
        errors.push(fields[0] + " " + estimate[fields[0]] + " exceeds preview cap " + PREVIEW_RESOURCE_POLICY[fields[1]]);
      }
    });
    return deepFreeze({
      policyId: PREVIEW_RESOURCE_POLICY.id,
      withinPolicy: errors.length === 0,
      errors: errors,
      estimate: estimate
    });
  }

  function validateFamilySpec(input) {
    var errors = [];
    var allowed = [
      "schema", "familyId", "linearSize", "level", "characteristicSpacing",
      "sigma", "boundaryCondition", "streams"
    ];
    if (!isPlainObject(input)) {
      return { valid: false, errors: ["family spec must be a plain object"], spec: null };
    }
    unknownKeys(input, allowed).forEach(function (key) { errors.push("unknown family field " + key); });

    var familyId = input.familyId;
    var schema = hasOwn(input, "schema") ? input.schema : FAMILY_SCHEMA;
    var linearSize = hasOwn(input, "linearSize") ? input.linearSize : 4;
    var level = hasOwn(input, "level") ? input.level : 0;
    var characteristicSpacing = hasOwn(input, "characteristicSpacing") ? input.characteristicSpacing : 1;
    var sigma = hasOwn(input, "sigma") ? input.sigma : 0;
    var boundaryCondition = hasOwn(input, "boundaryCondition") ? input.boundaryCondition : "reflecting-disk";

    if (schema !== FAMILY_SCHEMA) errors.push("unsupported family schema");
    if (FAMILY_IDS.indexOf(familyId) < 0) errors.push("familyId must name a registered filled-disk family");
    if (!Number.isInteger(linearSize) || linearSize < 2 || linearSize > MAX_LINEAR_SIZE) {
      errors.push("linearSize must be an integer in [2, " + MAX_LINEAR_SIZE + "]");
    }
    if (!Number.isInteger(level) || level < 0 || level > 32) errors.push("level must be an integer in [0, 32]");
    if (!finiteNumber(characteristicSpacing) || characteristicSpacing < MIN_CHARACTERISTIC_SPACING || characteristicSpacing > 100) {
      errors.push("characteristicSpacing must be finite and in [" + MIN_CHARACTERISTIC_SPACING + ", 100]");
    }
    if (!finiteNumber(sigma) || sigma < 0 || sigma > LOG_FOUR) {
      errors.push("sigma must be finite and in [0, log(4)]");
    }
    if (boundaryCondition !== "reflecting-disk") errors.push("boundaryCondition must be reflecting-disk");

    var rawStreams = hasOwn(input, "streams") ? input.streams : {};
    if (!isPlainObject(rawStreams)) {
      errors.push("streams must be a plain object");
      rawStreams = {};
    } else {
      unknownKeys(rawStreams, ["generator", "conductance"]).forEach(function (key) {
        errors.push("unknown stream role " + key);
      });
    }
    var familyForDefaults = FAMILY_IDS.indexOf(familyId) >= 0 ? familyId : "invalid-family";
    var generatorSeed = hasOwn(rawStreams, "generator")
      ? rawStreams.generator
      : "ggii/preview/" + familyForDefaults + "/generator";
    var conductanceSeed = hasOwn(rawStreams, "conductance")
      ? rawStreams.conductance
      : "ggii/preview/" + familyForDefaults + "/conductance";
    [["generator", generatorSeed], ["conductance", conductanceSeed]].forEach(function (entry) {
      if (typeof entry[1] !== "string" || entry[1].length === 0 || entry[1].length > 256) {
        errors.push(entry[0] + " stream seed must be a non-empty string of at most 256 characters");
      }
    });
    if (generatorSeed === conductanceSeed) errors.push("generator and conductance streams must not reuse a seed");

    var resourceReport = null;
    if (FAMILY_IDS.indexOf(familyId) >= 0 && Number.isInteger(linearSize) && linearSize >= 2 && linearSize <= 1000) {
      resourceReport = previewResourceReport(familyId, linearSize);
      resourceReport.errors.forEach(function (error) { errors.push("resource policy: " + error); });
    }

    var normalized = null;
    if (!errors.length) {
      normalized = {
        schema: FAMILY_SCHEMA,
        familyId: familyId,
        linearSize: linearSize,
        level: level,
        characteristicSpacing: characteristicSpacing,
        sigma: sigma,
        boundaryCondition: boundaryCondition,
        streams: { generator: generatorSeed, conductance: conductanceSeed },
        resourceReport: resourceReport
      };
    }
    return { valid: errors.length === 0, errors: errors, spec: normalized };
  }

  function requireFamilySpec(input) {
    var report = validateFamilySpec(input);
    if (!report.valid) throw new Error("Invalid filled-disk family spec: " + report.errors.join("; "));
    return report.spec;
  }

  function pointRecord(key, x, y) {
    return { key: key, x: x, y: y, z: 0 };
  }

  function createSquarePoints(linearSize, spacing, includeCenters) {
    var points = Object.create(null);
    for (var row = 0; row <= linearSize; row += 1) {
      for (var column = 0; column <= linearSize; column += 1) {
        var key = pointKey(2 * row, 2 * column);
        points[key] = pointRecord(key, column * spacing, row * spacing);
      }
    }
    if (includeCenters) {
      for (var cellRow = 0; cellRow < linearSize; cellRow += 1) {
        for (var cellColumn = 0; cellColumn < linearSize; cellColumn += 1) {
          var centerKey = pointKey(2 * cellRow + 1, 2 * cellColumn + 1);
          points[centerKey] = pointRecord(centerKey, (cellColumn + 0.5) * spacing, (cellRow + 0.5) * spacing);
        }
      }
    }
    return points;
  }

  function addSquareDiagonalFaces(spec, points, faceKeys, motifRecords, chooseDiagonal) {
    for (var row = 0; row < spec.linearSize; row += 1) {
      for (var column = 0; column < spec.linearSize; column += 1) {
        var southwest = pointKey(2 * row, 2 * column);
        var southeast = pointKey(2 * row, 2 * (column + 1));
        var northeast = pointKey(2 * (row + 1), 2 * (column + 1));
        var northwest = pointKey(2 * (row + 1), 2 * column);
        var canonicalCell = cellKey(row, column);
        var diagonal = chooseDiagonal(row, column, canonicalCell);
        if (diagonal === "southwest-northeast") {
          faceKeys.push([southwest, southeast, northeast], [southwest, northeast, northwest]);
        } else {
          faceKeys.push([southwest, southeast, northwest], [southeast, northeast, northwest]);
        }
        motifRecords.push({ cellKey: canonicalCell, diagonal: diagonal });
      }
    }
  }

  function squareAlternatingConstruction(spec) {
    var points = createSquarePoints(spec.linearSize, spec.characteristicSpacing, false);
    var faceKeys = [], motifs = [];
    addSquareDiagonalFaces(spec, points, faceKeys, motifs, function (row, column) {
      return (row + column) % 2 === 0 ? "southwest-northeast" : "northwest-southeast";
    });
    return {
      points: points,
      faceKeys: faceKeys,
      motifs: motifs,
      motifName: "parity-alternating-square-diagonal",
      domain: "declared-axis-aligned-square-[0,Lh]^2",
      clipPolicy: "exact square cellulation"
    };
  }

  function squareHashedConstruction(spec) {
    var points = createSquarePoints(spec.linearSize, spec.characteristicSpacing, false);
    var faceKeys = [], motifs = [];
    addSquareDiagonalFaces(spec, points, faceKeys, motifs, function (row, column, canonicalCell) {
      return coordinateUniform(spec.streams.generator, canonicalCell) < 0.5
        ? "southwest-northeast"
        : "northwest-southeast";
    });
    return {
      points: points,
      faceKeys: faceKeys,
      motifs: motifs,
      motifName: "coordinate-hashed-square-diagonal",
      domain: "declared-axis-aligned-square-[0,Lh]^2",
      clipPolicy: "exact square cellulation"
    };
  }

  function cellCenterFanConstruction(spec) {
    var points = createSquarePoints(spec.linearSize, spec.characteristicSpacing, true);
    var faceKeys = [], motifs = [];
    for (var row = 0; row < spec.linearSize; row += 1) {
      for (var column = 0; column < spec.linearSize; column += 1) {
        var southwest = pointKey(2 * row, 2 * column);
        var southeast = pointKey(2 * row, 2 * (column + 1));
        var northeast = pointKey(2 * (row + 1), 2 * (column + 1));
        var northwest = pointKey(2 * (row + 1), 2 * column);
        var center = pointKey(2 * row + 1, 2 * column + 1);
        faceKeys.push(
          [southwest, southeast, center],
          [southeast, northeast, center],
          [northeast, northwest, center],
          [northwest, southwest, center]
        );
        motifs.push({ cellKey: cellKey(row, column), centerKey: center, triangles: 4 });
      }
    }
    return {
      points: points,
      faceKeys: faceKeys,
      motifs: motifs,
      motifName: "four-triangle-cell-center-fan",
      domain: "declared-axis-aligned-square-[0,Lh]^2",
      clipPolicy: "exact square cellulation"
    };
  }

  function triangularClippedConstruction(spec) {
    var points = Object.create(null), faceKeys = [], motifs = [];
    var height = Math.sqrt(3) / 2 * spec.characteristicSpacing;
    var stripCount = Math.floor(spec.linearSize * spec.characteristicSpacing / height);
    function triangularPoint(row, column) {
      return pointKey(row, 2 * column + (row % 2));
    }
    for (var row = 0; row <= stripCount; row += 1) {
      var columns = row % 2 === 0 ? spec.linearSize + 1 : spec.linearSize;
      for (var column = 0; column < columns; column += 1) {
        var key = triangularPoint(row, column);
        points[key] = pointRecord(
          key,
          (column + (row % 2) / 2) * spec.characteristicSpacing,
          row * height
        );
      }
    }
    for (var strip = 0; strip < stripCount; strip += 1) {
      var lowerEven = strip % 2 === 0;
      for (var index = 0; index < spec.linearSize; index += 1) {
        if (lowerEven) {
          faceKeys.push([
            triangularPoint(strip, index),
            triangularPoint(strip, index + 1),
            triangularPoint(strip + 1, index)
          ]);
        } else {
          faceKeys.push([
            triangularPoint(strip, index),
            triangularPoint(strip + 1, index),
            triangularPoint(strip + 1, index + 1)
          ]);
        }
      }
      for (var bridge = 0; bridge < spec.linearSize - 1; bridge += 1) {
        if (lowerEven) {
          faceKeys.push([
            triangularPoint(strip, bridge + 1),
            triangularPoint(strip + 1, bridge + 1),
            triangularPoint(strip + 1, bridge)
          ]);
        } else {
          faceKeys.push([
            triangularPoint(strip, bridge),
            triangularPoint(strip, bridge + 1),
            triangularPoint(strip + 1, bridge + 1)
          ]);
        }
      }
    }
    motifs.push({
      patchKey: "triangular-strip-patch",
      elementaryTriangles: faceKeys.length,
      rowParityOffset: 0.5,
      stripCount: stripCount,
      declaredHeight: spec.linearSize * spec.characteristicSpacing,
      realizedHeight: stripCount * height
    });
    return {
      points: points,
      faceKeys: faceKeys,
      motifs: motifs,
      motifName: "equilateral-triangular-lattice",
      domain: "declared-axis-aligned-square-[0,Lh]^2",
      clipPolicy: "retain the maximal filled elementary-triangle patch inside the declared square"
    };
  }

  function orientFace(face, nodes) {
    var a = nodes[face[0]], b = nodes[face[1]], c = nodes[face[2]];
    var signedDoubleArea = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
    if (signedDoubleArea === 0) throw new Error("Construction produced a degenerate face.");
    return signedDoubleArea > 0 ? face : [face[0], face[2], face[1]];
  }

  function canonicalFaceTuple(face) {
    return face.slice().sort(function (a, b) { return a - b; });
  }

  function canonicalEdgeKey(nodeA, nodeB) {
    return nodeA.label < nodeB.label
      ? nodeA.label + "|" + nodeB.label
      : nodeB.label + "|" + nodeA.label;
  }

  function euclideanDistance(a, b) {
    var dx = a.x - b.x, dy = a.y - b.y, dz = a.z - b.z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }

  function measuredDiameter(nodes) {
    var maximum = 0;
    for (var first = 0; first < nodes.length; first += 1) {
      for (var second = first + 1; second < nodes.length; second += 1) {
        maximum = Math.max(maximum, euclideanDistance(nodes[first], nodes[second]));
      }
    }
    return maximum;
  }

  function planarTriangleArea(nodes, face) {
    var a = nodes[face[0]], b = nodes[face[1]], c = nodes[face[2]];
    return Math.abs((b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)) / 2;
  }

  function realizedDomainDisclosure(spec, construction, nodes, faces, realizedDiameter) {
    var xs = nodes.map(function (node) { return node.x; });
    var ys = nodes.map(function (node) { return node.y; });
    var minX = Math.min.apply(null, xs), maxX = Math.max.apply(null, xs);
    var minY = Math.min.apply(null, ys), maxY = Math.max.apply(null, ys);
    var targetSpan = spec.linearSize * spec.characteristicSpacing;
    var targetArea = targetSpan * targetSpan;
    var realizedArea = faces.reduce(function (sum, face) {
      return sum + planarTriangleArea(nodes, face);
    }, 0);
    if (Math.abs(realizedArea - targetArea) <= 1e-12 * targetArea) realizedArea = targetArea;
    var coverageRatio = realizedArea / targetArea;
    var topCrop = Math.max(0, targetSpan - maxY);
    var alternatingSideInset = spec.familyId === "triangular-clipped"
      ? spec.characteristicSpacing / 2
      : 0;
    var exactTargetCoverage = coverageRatio === 1 && topCrop === 0 && alternatingSideInset === 0;
    return deepFreeze({
      target: {
        id: "axis-aligned-square-[0,Lh]^2",
        nativeBounds: { x: [0, targetSpan], y: [0, targetSpan] },
        area: targetArea,
        diameter: Math.SQRT2 * targetSpan
      },
      realized: {
        nativeBounds: { x: [minX, maxX], y: [minY, maxY] },
        dimensionlessBounds: {
          x: [minX / targetSpan, maxX / targetSpan],
          y: [minY / targetSpan, maxY / targetSpan]
        },
        triangulatedArea: realizedArea,
        areaCoverageRatio: coverageRatio,
        uncoveredAreaFraction: Math.max(0, 1 - coverageRatio),
        measuredDiameter: realizedDiameter
      },
      crop: {
        policy: construction.clipPolicy,
        exactTargetCoverage: exactTargetCoverage,
        topCrop: topCrop,
        alternatingSideInset: alternatingSideInset,
        maximumBoundaryOffset: Math.max(topCrop, alternatingSideInset),
        status: exactTargetCoverage ? "none" : "declared-interior-crop"
      },
      coordinateMaps: {
        native: "(x,y,z)",
        dimensionlessTarget: "(x/(Lh),y/(Lh),z/(Lh))"
      },
      crossFamilyComparison: exactTargetCoverage
        ? "Exact target-square carrier; comparison still requires a declared metric/operator scaling."
        : "Finite carrier does not cover the exact target square; use a registered common-bulk mask and boundary-crop response before cross-family comparison."
    });
  }

  function digestPayloads(complex, familyId) {
    var nodeRows = complex.nodes.map(function (node) {
      return [node.label, node.x, node.y, node.z];
    }).sort(function (a, b) { return a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0; });
    var edgeRows = complex.edges.map(function (edge) {
      var key = canonicalEdgeKey(complex.nodes[edge.source], complex.nodes[edge.target]);
      return [key, edge.length, edge.weight];
    }).sort(function (a, b) { return a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0; });
    var faceRows = complex.faces.map(function (face) {
      return face.map(function (vertex) { return complex.nodes[vertex].label; }).sort();
    }).sort(function (a, b) {
      var left = a.join("|"), right = b.join("|");
      return left < right ? -1 : left > right ? 1 : 0;
    });
    return {
      combinatorial: {
        familyId: familyId,
        nodeKeys: nodeRows.map(function (row) { return row[0]; }),
        edgeKeys: edgeRows.map(function (row) { return row[0]; }),
        faceKeys: faceRows
      },
      realization: {
        familyId: familyId,
        nodes: nodeRows,
        edges: edgeRows,
        faces: faceRows
      }
    };
  }

  function materializeComplex(spec, construction) {
    var pointRecords = Object.keys(construction.points).sort().map(function (key) {
      return construction.points[key];
    });
    var indexByKey = Object.create(null);
    var nodes = pointRecords.map(function (point, index) {
      indexByKey[point.key] = index;
      return {
        id: index,
        label: point.key,
        x: point.x,
        y: point.y,
        z: point.z,
        radius: 1,
        value: 0,
        u: 1,
        v: 0
      };
    });
    var faces = construction.faceKeys.map(function (faceKeys) {
      var face = faceKeys.map(function (key) {
        if (indexByKey[key] == null) throw new Error("Face references missing canonical point " + key + ".");
        return indexByKey[key];
      });
      return orientFace(face, nodes);
    });
    faces.sort(function (a, b) {
      var tupleA = canonicalFaceTuple(a), tupleB = canonicalFaceTuple(b);
      return tupleA[0] - tupleB[0] || tupleA[1] - tupleB[1] || tupleA[2] - tupleB[2];
    });

    var edgeMap = Object.create(null);
    faces.forEach(function (face) {
      [[face[0], face[1]], [face[1], face[2]], [face[2], face[0]]].forEach(function (pair) {
        var source = Math.min(pair[0], pair[1]), target = Math.max(pair[0], pair[1]);
        var numericKey = source + ":" + target;
        if (!edgeMap[numericKey]) {
          var objectKey = canonicalEdgeKey(nodes[source], nodes[target]);
          var uniform = coordinateUniform(spec.streams.conductance, objectKey);
          var weight = Math.exp(spec.sigma * (2 * uniform - 1));
          edgeMap[numericKey] = {
            source: source,
            target: target,
            length: euclideanDistance(nodes[source], nodes[target]),
            weight: weight,
            canonicalKey: objectKey
          };
        }
      });
    });
    var edgeRecords = Object.keys(edgeMap).map(function (key) { return edgeMap[key]; });
    edgeRecords.sort(function (a, b) { return a.source - b.source || a.target - b.target; });
    var canonicalEdgeKeys = edgeRecords.map(function (edge) { return edge.canonicalKey; });
    var edges = edgeRecords.map(function (edge) {
      return { source: edge.source, target: edge.target, length: edge.length, weight: edge.weight };
    });
    var resourceReport = previewResourceReport(spec.familyId, spec.linearSize);
    if (!resourceReport.withinPolicy) {
      throw new Error("Preview resource policy rejected generated family: " + resourceReport.errors.join("; "));
    }
    if (resourceReport.estimate.vertices !== nodes.length ||
        resourceReport.estimate.edges !== edges.length ||
        resourceReport.estimate.faces !== faces.length) {
      throw new Error("Preview resource estimate does not match the materialized carrier.");
    }
    var lowerBound = Math.exp(-spec.sigma), upperBound = Math.exp(spec.sigma);
    var realizedDiameter = measuredDiameter(nodes);
    var domainDisclosure = realizedDomainDisclosure(spec, construction, nodes, faces, realizedDiameter);
    var payloads = digestPayloads({ nodes: nodes, edges: edges, faces: faces }, spec.familyId);
    var combinatorialDigest = digestValue(payloads.combinatorial);
    var realizationDigest = digestValue(payloads.realization);
    return {
      nodes: nodes,
      edges: edges,
      faces: faces,
      metadata: {
        generator: spec.familyId,
        familySchema: FAMILY_SCHEMA,
        familyId: spec.familyId,
        topologyHint: "disk",
        boundaryCondition: spec.boundaryCondition,
        constructionLocality: {
          class: "L0",
          radius: 1,
          coordinateSystem: "integer-cell-coordinates",
          adjacency: "finite local cell template",
          faces: "finite local cell template",
          metric: "embedded Euclidean edge length at initialization",
          measure: "unit vertex counting measure",
          weights: "object-keyed finite-radius conductance rule"
        },
        metricModels: {
          authoritativeEdgeLength: "embedded_euclidean_at_initialization",
          graphObservables: "graph_length",
          surfaceObservables: "piecewise_euclidean",
          displayEmbeddingStatus: "construction coordinates compile edge.length; later display transforms are not intrinsic",
          observableMustSelectMetric: true
        },
        measureModel: "unit_vertex_counting",
        operatorModels: {
          analysis: "weighted_symmetric_normalized_laplacian",
          runtime: "lazy_reversible_nearest_neighbor_random_walk",
          lazyProbability: 0.5,
          conductanceField: "edge.weight",
          status: "declared preview contract; this generator does not evolve state"
        },
        runtimeLocality: {
          class: "L0",
          radius: 1,
          synchronous: true,
          intendedRule: "lazy reversible nearest-neighbor diffusion"
        },
        analysisLocality: "L2",
        construction: {
          motif: construction.motifName,
          domain: construction.domain,
          clipPolicy: construction.clipPolicy,
          domainDisclosure: domainDisclosure,
          motifs: cloneJSON(construction.motifs),
          motifDigest: digestValue(construction.motifs)
        },
        comparisonScope: {
          highestSupportedClaim: "finite_instance_calibration",
          topologyScope: "exact supplied finite triangular complex over GF(2)",
          geometryScope: "binary64 piecewise-Euclidean surface gate on authoritative edge lengths",
          profileScope: "NOT_EVALUATED",
          universalityStatus: "NOT_EVALUATED",
          commonDomainRequirement: domainDisclosure.crop.exactTargetCoverage
            ? "declare metric/operator normalization before cross-family comparison"
            : "apply a registered common-bulk mask and boundary-crop response before cross-family comparison",
          withheldClaims: [
            "refinement convergence",
            "profile equivalence",
            "limit-object equivalence",
            "universality",
            "continuum limit"
          ]
        },
        canonicalization: {
          version: "lexicographic-integer-coordinate-keys-v1",
          nodeIds: "ascending canonical point key",
          edgeIds: "ascending canonical endpoint IDs",
          faces: "counterclockwise, sorted by unoriented vertex triple"
        },
        canonicalNodeKeys: nodes.map(function (node) { return node.label; }),
        canonicalEdgeKeys: canonicalEdgeKeys,
        streams: {
          algorithm: PRNG_CONTRACT,
          separation: "role-and-object-keyed-v1",
          generator: spec.streams.generator,
          conductance: spec.streams.conductance
        },
        disorder: {
          type: "quenched-log-uniform-conductance",
          sigma: spec.sigma,
          formula: "w_e=exp(sigma*(2*u_e-1))",
          uniformEllipticity: [lowerBound, upperBound],
          observedMinimum: edges.reduce(function (value, edge) { return Math.min(value, edge.weight); }, Infinity),
          observedMaximum: edges.reduce(function (value, edge) { return Math.max(value, edge.weight); }, -Infinity),
          strictlyPositive: edges.every(function (edge) { return edge.weight > 0; })
        },
        refinement: {
          kind: "linear-size",
          level: spec.level,
          characteristicSpacing: spec.characteristicSpacing,
          linearSize: spec.linearSize,
          domainDiameter: realizedDiameter,
          realizedDomainDiameter: realizedDiameter,
          targetDomainDiameter: domainDisclosure.target.diameter,
          realizedAreaCoverageRatio: domainDisclosure.realized.areaCoverageRatio,
          vertexCount: nodes.length,
          parentLevel: spec.level === 0 ? null : spec.level - 1,
          restrictionMapDigest: null,
          prolongationMapDigest: null,
          mapStatus: "not-materialized-in-preview-slice"
        },
        resources: {
          policy: PREVIEW_RESOURCE_POLICY,
          estimate: resourceReport.estimate,
          withinPolicy: resourceReport.withinPolicy
        },
        structureDigestAlgorithm: "fnv1a32-canonical-json",
        digestContract: "ggii-ensemble-digests-v2",
        combinatorialDigestAlgorithm: "fnv1a32-canonical-json",
        combinatorialDigest: combinatorialDigest,
        realizationDigestAlgorithm: "fnv1a32-canonical-json",
        realizationDigest: realizationDigest,
        structureDigestScope: "backward-compatible alias of realizationDigest",
        structureDigest: realizationDigest
      }
    };
  }

  function recomputeFamilyDigests(complex) {
    var rawErrors = rawFilledDiskErrors(complex);
    if (rawErrors.length) throw new Error("Cannot recompute family digests: " + rawErrors.join("; "));
    var metadata = complex.metadata;
    if (!isPlainObject(metadata)) throw new Error("Cannot recompute family digests without plain metadata.");
    if (FAMILY_IDS.indexOf(metadata.familyId) < 0) throw new Error("Cannot recompute family digests for an unregistered family.");
    if (!isPlainObject(metadata.construction) || !denseArray(metadata.construction.motifs)) {
      throw new Error("Cannot recompute family digests without a dense construction motif array.");
    }
    var payloads = digestPayloads(complex, metadata.familyId);
    var realization = digestValue(payloads.realization);
    return deepFreeze({
      digestContract: "ggii-ensemble-digests-v2",
      combinatorialDigestAlgorithm: "fnv1a32-canonical-json",
      combinatorialDigest: digestValue(payloads.combinatorial),
      realizationDigestAlgorithm: "fnv1a32-canonical-json",
      realizationDigest: realization,
      structureDigestAlgorithm: "fnv1a32-canonical-json",
      structureDigest: realization,
      structureDigestScope: "backward-compatible alias of realizationDigest",
      motifDigestAlgorithm: "fnv1a32-canonical-json",
      motifDigest: digestValue(metadata.construction.motifs)
    });
  }

  function familyDigestErrors(complex) {
    var errors = [], metadata = complex.metadata;
    if (!isPlainObject(metadata)) return ["metadata must be a plain object with family digest bindings"];
    if (FAMILY_IDS.indexOf(metadata.familyId) < 0) return ["metadata.familyId must name a registered family"];
    if (metadata.digestContract !== "ggii-ensemble-digests-v2") errors.push("metadata digest contract is missing or unsupported");
    ["structureDigestAlgorithm", "combinatorialDigestAlgorithm", "realizationDigestAlgorithm"].forEach(function (field) {
      if (metadata[field] !== "fnv1a32-canonical-json") errors.push("metadata." + field + " must be fnv1a32-canonical-json");
    });
    ["structureDigest", "combinatorialDigest", "realizationDigest"].forEach(function (field) {
      if (!/^[0-9a-f]{8}$/.test(metadata[field] || "")) errors.push("metadata." + field + " must be an eight-character lowercase digest");
    });
    if (!isPlainObject(metadata.construction) || !denseArray(metadata.construction.motifs)) {
      errors.push("metadata construction motifs must be a dense array");
    }
    if (errors.length) return errors;
    var expected;
    try { expected = recomputeFamilyDigests(complex); }
    catch (error) { return [error.message]; }
    if (metadata.combinatorialDigest !== expected.combinatorialDigest) errors.push("metadata combinatorial digest mismatch");
    if (metadata.realizationDigest !== expected.realizationDigest) errors.push("metadata realization digest mismatch");
    if (metadata.structureDigest !== expected.structureDigest) errors.push("metadata structure digest alias mismatch");
    if (metadata.construction.motifDigest !== expected.motifDigest) errors.push("metadata motif digest mismatch");
    return errors;
  }

  function verifyFamilyDigests(complex) {
    var errors = rawFilledDiskErrors(complex);
    if (!errors.length) errors = familyDigestErrors(complex);
    var expected = null;
    if (!errors.length) expected = recomputeFamilyDigests(complex);
    return deepFreeze({ valid: errors.length === 0, errors: errors.slice(), expected: expected });
  }

  function rawFilledDiskErrors(complex) {
    var errors = [];
    if (!isPlainObject(complex)) return ["filled complex must be a plain object"];
    if (!denseArray(complex.nodes) || !complex.nodes.length) errors.push("nodes must be a non-empty dense array");
    if (!denseArray(complex.edges) || !complex.edges.length) errors.push("edges must be a non-empty dense array");
    if (!denseArray(complex.faces) || !complex.faces.length) errors.push("faces must be a non-empty dense array");
    if (errors.length) return errors;

    var labels = Object.create(null);
    complex.nodes.forEach(function (node, index) {
      if (!isPlainObject(node)) {
        errors.push("node " + index + " must be a plain object");
        return;
      }
      if (node.id !== index) errors.push("node " + index + " must have its canonical array index as id");
      if (typeof node.label !== "string" || !node.label.length || node.label.length > 512) {
        errors.push("node " + index + " must have a non-empty bounded canonical label");
      } else if (labels[node.label]) {
        errors.push("node " + index + " duplicates canonical label " + node.label);
      } else {
        labels[node.label] = true;
      }
      ["x", "y", "z"].forEach(function (coordinate) {
        if (!finiteNumber(node[coordinate])) errors.push("node " + index + "." + coordinate + " must be a finite number");
      });
    });

    var edgeKeys = Object.create(null), edgeRecords = [];
    complex.edges.forEach(function (edge, index) {
      if (!isPlainObject(edge)) {
        errors.push("edge " + index + " must be a plain object");
        return;
      }
      var source = edge.source, target = edge.target;
      if (!Number.isInteger(source) || !Number.isInteger(target) || source < 0 || target < 0 || source >= complex.nodes.length || target >= complex.nodes.length || source === target) {
        errors.push("edge " + index + " has invalid exact-integer endpoints");
        return;
      }
      var key = source < target ? source + ":" + target : target + ":" + source;
      if (edgeKeys[key]) errors.push("edge " + index + " duplicates unoriented edge " + key);
      edgeKeys[key] = true;
      edgeRecords.push({ key: key, edge: edge, index: index });
      if (!finiteNumber(edge.length) || edge.length <= 0) errors.push("edge " + index + " length must be finite and positive");
      if (!finiteNumber(edge.weight) || edge.weight <= 0) errors.push("edge " + index + " conductance must be finite and positive");
      var a = complex.nodes[source], b = complex.nodes[target];
      if (isPlainObject(a) && isPlainObject(b) && [a.x, a.y, a.z, b.x, b.y, b.z].every(finiteNumber) && finiteNumber(edge.length)) {
        var embedded = euclideanDistance(a, b);
        if (Math.abs(edge.length - embedded) > 1e-10 * Math.max(1, embedded)) {
          errors.push("edge " + index + " length does not match the declared embedded metric");
        }
      }
    });

    var faceKeys = Object.create(null), faceEdgeKeys = Object.create(null);
    complex.faces.forEach(function (face, index) {
      if (!denseArray(face) || face.length !== 3 || face.some(function (vertex) { return !Number.isInteger(vertex) || vertex < 0 || vertex >= complex.nodes.length; })) {
        errors.push("face " + index + " must contain three exact integer node indices");
        return;
      }
      if (new Set(face).size !== 3) {
        errors.push("face " + index + " is degenerate");
        return;
      }
      var faceKey = face.slice().sort(function (a, b) { return a - b; }).join(":");
      if (faceKeys[faceKey]) errors.push("face " + index + " duplicates unoriented triangular face " + faceKey);
      faceKeys[faceKey] = true;
      [[face[0], face[1]], [face[1], face[2]], [face[2], face[0]]].forEach(function (pair) {
        var key = pair[0] < pair[1] ? pair[0] + ":" + pair[1] : pair[1] + ":" + pair[0];
        faceEdgeKeys[key] = true;
      });
    });
    Object.keys(faceEdgeKeys).forEach(function (key) {
      if (!edgeKeys[key]) errors.push("face side " + key + " is missing from the declared edge list");
    });
    Object.keys(edgeKeys).forEach(function (key) {
      if (!faceEdgeKeys[key]) errors.push("declared edge " + key + " is not incident to a face");
    });
    return errors;
  }

  function validateFilledDisk(complex) {
    var errors = rawFilledDiskErrors(complex);
    if (!errors.length) errors = errors.concat(familyDigestErrors(complex));
    var topology = null, surface = null, curvature = null;
    if (!errors.length) {
      try {
        var baseValidation = Base.validateComplex(complex);
        if (!baseValidation.valid) errors = errors.concat(baseValidation.errors);
        if (!errors.length) {
          topology = Base.computeBettiNumbers(complex);
          surface = Base.surfaceValidity(complex, { metric: "embedded" });
          curvature = Base.angleDefectCurvature(complex, { metric: "embedded" });
          if (topology.betti.array.join(",") !== "1,0,0") errors.push("filled complex does not have disk Betti numbers");
          if (topology.eulerCharacteristic !== 1 || topology.eulerPoincareResidual !== 0) errors.push("Euler--Poincare disk identity failed");
          if (topology.boundary.componentCount !== 1) errors.push("filled complex must have one boundary component");
          if (!topology.manifoldCheck.isEdgeManifold) errors.push("filled complex is not an edge manifold");
          if (!surface.valid || !surface.identityApplicable) errors.push("triangular surface validity gate failed");
          if (!curvature.available || !curvature.identityApplicable) errors.push("angle-defect identity is not applicable");
          if (curvature.available) {
            var scale = Math.max(1, Math.abs(curvature.targetTotal));
            if (Math.abs(curvature.gaussBonnetResidual) >= GAUSS_BONNET_TOLERANCE * scale) {
              errors.push("Gauss--Bonnet residual exceeds the exact-small tolerance");
            }
          }
        }
      } catch (error) { errors.push("base finite gate threw: " + error.message); }
    }
    return {
      valid: errors.length === 0,
      errors: errors,
      evidenceClass: "mixed-finite-certificate",
      sourceCoreVersion: Base.VERSION,
      topology: topology ? {
        evidenceClass: "exact-combinatorial-result",
        simplexCounts: topology.simplexCounts,
        betti: topology.betti.array,
        eulerCharacteristic: topology.eulerCharacteristic,
        eulerPoincareResidual: topology.eulerPoincareResidual,
        boundaryComponents: topology.boundary.componentCount,
        boundaryEdgeCount: topology.boundary.edgeCount,
        isEdgeManifold: topology.manifoldCheck.isEdgeManifold
      } : null,
      surface: surface ? {
        evidenceClass: "finite-combinatorial-and-binary64-gate",
        valid: surface.valid,
        identityApplicable: surface.identityApplicable,
        boundaryComponents: surface.boundaryComponents,
        invalidVertexLinkCount: surface.invalidVertexLinks.length,
        degenerateFaceCount: surface.degenerateFaces.length
      } : null,
      gaussBonnet: curvature ? {
        evidenceClass: "binary64-evaluation-of-proved-finite-identity",
        available: curvature.available,
        identityApplicable: curvature.identityApplicable,
        total: curvature.total,
        targetTotal: curvature.targetTotal,
        residual: curvature.gaussBonnetResidual,
        tolerance: GAUSS_BONNET_TOLERANCE * Math.max(1, Math.abs(curvature.targetTotal || 0))
      } : null
    };
  }

  function generateFamily(input) {
    var spec = requireFamilySpec(input);
    var construction;
    if (spec.familyId === "square-alternating") construction = squareAlternatingConstruction(spec);
    else if (spec.familyId === "triangular-clipped") construction = triangularClippedConstruction(spec);
    else if (spec.familyId === "cell-center-fan") construction = cellCenterFanConstruction(spec);
    else construction = squareHashedConstruction(spec);
    var complex = materializeComplex(spec, construction);
    var validation = validateFilledDisk(complex);
    if (!validation.valid) throw new Error("Generated filled disk failed validation: " + validation.errors.join("; "));
    complex.metadata.exactValidation = validation;
    return deepFreeze(complex);
  }

  function withFamily(familyId, options) {
    options = typeof options === "undefined" ? {} : options;
    if (!isPlainObject(options)) throw new Error("generator options must be a plain object");
    var input = {};
    Object.keys(options).forEach(function (key) { input[key] = options[key]; });
    input.familyId = familyId;
    return generateFamily(input);
  }

  function generateSquareAlternating(options) { return withFamily("square-alternating", options); }
  function generateTriangularClipped(options) { return withFamily("triangular-clipped", options); }
  function generateCellCenterFan(options) { return withFamily("cell-center-fan", options); }
  function generateSquareHashedDiagonal(options) { return withFamily("square-hashed-diagonal", options); }

  return {
    VERSION: VERSION,
    FAMILY_SCHEMA: FAMILY_SCHEMA,
    PRNG_CONTRACT: PRNG_CONTRACT,
    MAX_LINEAR_SIZE: MAX_LINEAR_SIZE,
    MIN_CHARACTERISTIC_SPACING: MIN_CHARACTERISTIC_SPACING,
    PREVIEW_RESOURCE_POLICY: PREVIEW_RESOURCE_POLICY,
    FAMILY_IDS: deepFreeze(FAMILY_IDS.slice()),
    stableStringify: stableStringify,
    digestValue: digestValue,
    digestPayloads: digestPayloads,
    recomputeFamilyDigests: recomputeFamilyDigests,
    verifyFamilyDigests: verifyFamilyDigests,
    estimatePreviewResources: estimatePreviewResources,
    previewResourceReport: previewResourceReport,
    validateFamilySpec: validateFamilySpec,
    coordinateHash: coordinateHash,
    coordinateUniform: coordinateUniform,
    validateFilledDisk: validateFilledDisk,
    generateFamily: generateFamily,
    generateSquareAlternating: generateSquareAlternating,
    generateTriangularClipped: generateTriangularClipped,
    generateCellCenterFan: generateCellCenterFan,
    generateSquareHashedDiagonal: generateSquareHashedDiagonal
  };
});
