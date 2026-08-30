# Global Geometry II — outcome-blind evaluation repair audit

Contract ID: `ggii-evaluation-repair-audit-v1`

Status: implementation/provenance audit written without reading screening or
U2 outcome records. This document changes no estimator, margin, gate, control,
random stream, census identity, or scientific failure threshold. It defines
the minimum repair needed before new evaluation artifacts are treated as
publication-grade evidence.

## A. Versioned screening repair

The repaired run must use a new implementation supplement, artifact schema,
and output version. A partial or final artifact from an earlier implementation
is never silently imported into the new evidentiary run.

### A1. Crash-safe chunks and exact resumption

1. Partition the frozen 3,840-record census into contiguous 32-record chunks.
   A chunk identity is the tuple
   `(screeningId, sourceCommit, platformLabel, firstOrdinal, lastOrdinal)`; it
   never contains a PID, wall time, or retry number.
2. Write a chunk to a temporary file, `fsync` it, validate all 32 identities,
   canonical record bytes, hashes, and semantic remeasurements, then publish it
   with an exclusive write/rename. A short final chunk is forbidden because
   3,840 is divisible by 32.
3. An existing chunk is reusable only if its exact expected identity and bytes
   validate. Exact-byte equality is `EXISTING_IDENTICAL`; any other collision
   is `CHUNK_COLLISION` and aborts without overwrite.
4. On resume, validate every contiguous existing chunk from ordinal zero and
   continue at the first absent chunk. Gaps, overlaps, duplicate ordinals,
   mixed source commits, mixed platform labels, and orphan temporary files are
   fail-closed infrastructure findings. They do not create scientific records.
5. Assembly is deterministic: concatenating validated chunk bytes must equal
   the bytes from an uninterrupted run. Resume does not change seeds, record
   hashes, Merkle root, summary, or any independence count.
6. A platform/run lock is acquired exclusively. A concurrent runner for the
   same `(screeningId, sourceCommit, platformLabel)` must refuse to start; it
   must not race on chunks or final outputs.

Required adversarial cases:

- crash after exactly one committed chunk, resume, and compare the final raw
  bytes with an uninterrupted reference;
- same chunk identity with one changed byte;
- valid chunk renamed to the wrong ordinal range;
- missing middle chunk, overlapping chunks, and duplicated record ordinal;
- chunk from another source commit or platform label;
- two concurrent claims for the same run;
- retry after all final artifacts already exist.

### A2. Canonical bytes

The raw artifact is exactly
`canonicalStringify(record[0]) + "\n" + ... + canonicalStringify(record[3839]) + "\n"`.
Validation rejects blank lines, CRLF substitution, missing or extra trailing
newlines, leading/trailing spaces, noncanonical key order, noncanonical number
spelling, and semantically equivalent pretty-printed JSON.

The summary and certificate each have one frozen file encoding. Their
validators compare the actual file bytes with a deterministic serialization,
not merely parsed objects with freshly recomputed content addresses.

### A3. Source and certificate binding

Before a production record is generated, the runner proves that the supplied
40-hex value resolves to an actual commit. The execution certificate binds:

- the full commit ID and its Git tree ID;
- the byte SHA-256 of the evaluator, runner, base manifest, versioned
  supplement, and both implementation/adversarial tests;
- the screening semantic digests and platform label;
- raw, summary, and chunk-index byte digests and lengths;
- Node, OS, architecture, CPU count, start/end times, runtime, peak RSS, and
  failure counts;
- the forced scientific status `UNRESOLVED`.

Every executed evaluation file must match its blob at the bound commit. The
certificate validator checks its own content address, all bound artifact
bytes, the commit/tree relationship, and every relevant file digest.
`--validate-only` and post-write validation must validate the certificate too.

### A4. Independence and count semantics

Every positive cell reports these distinct counts:

- `carrierConstructionRealizationCount`;
- `conductanceRealizationCount`;
- `weightedConstructionRealizationCount`, the preregistered top-level
  independent unit;
- `measurementBatchCount`;
- `randomizedNestedMeasurementBatchCount`;
- `deterministicRepeatEvaluationCount`;
- `uniqueStructureDigestCount`, `uniqueWeightDigestCount`, and
  `uniqueWeightedStructureDigestCount`.

Expected positive-cell semantics are:

| Carrier | sigma | carrier | conductance | weighted | randomized nested |
| --- | ---: | ---: | ---: | ---: | ---: |
| deterministic family | 0 | 1 | 1 | 1 | 32 |
| deterministic family | >0 | 1 | 32 | 32 | 0 |
| hashed diagonal | 0 | 32 | 1 | 32 | 0 |
| hashed diagonal | >0 | 32 | 32 | 32 | 0 |

The 32 deterministic-family sigma-zero batches quantify spatial/root sampling
only and are never called 32 independent geometries. For controls, comb-trap
has one carrier and 32 randomized walk batches; vanishing-neck has one carrier,
one deterministic transport evaluation, and 31 explicitly disclosed repeat
evaluations; small-world and perforated-disk have 32 construction realizations.

### A5. Replay and writes

`replayRecord(record).valid` is true only when the supplied record is
canonically equal to the deterministic rebuild. Comparing a rebuilt hash with
the supplied old hash is insufficient. Full-summary validation regenerates
every aggregate, independence count, failure ledger, randomness audit, census,
raw binding, and gate disclaimer from the validated records.

All chunks, raw data, summaries, certificates, and indices use exclusive
creation. Existing identical outputs may be accepted only after full byte and
semantic validation. Existing different outputs are never truncated,
replaced, or amended.

## B. Strict U2 kernel repair

### B1. Replay every deterministic positive record

Campaign validation deterministically remeasures all 3,072 positive records,
not only replicate zero. It compares the whole canonical run record and
reports `positiveSemanticReplayCount: 3072`. A mutation to any field of any
replicate, including a nonzero replicate followed by regenerated exponent,
cell summaries, Merkle root, and content address, must be rejected.

The validator continues to replay all 768 primary-control records and the
exact Gate 1 record. Replay is validation of implementation fidelity, not new
independent scientific evidence.

### B2. Verify the normalization artifact

Campaign construction and campaign validation both require the complete
calibration artifact. They validate it independently and require:

- exact equality between its content address and `normalizationBinding`;
- the same actual source commit as the campaign;
- the frozen calibration namespace and 384-record census;
- no confirmatory input digest in calibration;
- deterministic deep replay of all calibration records.

The validate-campaign CLI therefore requires an explicit normalization path.
A plausible or freshly readdressed normalization binding without the bound
artifact is rejected.

### B3. Verify an actual committed source boundary

Production does not accept a value merely because it contains 40 hexadecimal
characters. It resolves the exact commit, binds its Git tree ID, and proves
that every executed U2 evaluator/CLI/manifest/decision-contract byte matches
that commit. A nonexistent hash, abbreviated hash, dirty relevant file,
missing bound file, or commit that does not contain the frozen manifest is
rejected before measurement.

### B4. Refuse overwrite

Calibration and campaign writers use exclusive creation. If the requested
output exists, the command refuses before doing expensive work and leaves the
existing bytes unchanged. Validation is a separate explicit mode and never
rewrites the input.

### B5. Required mutation tests

1. Modify a positive record with replicate 31, recompute its local exponent,
   aggregate cell, run Merkle root, and outer address: reject on semantic
   replay.
2. Substitute a separately valid calibration artifact or mutate only
   `normalizationBinding`: reject.
3. Supply forty `a` characters as the source commit: reject as nonexistent.
4. Modify one relevant working-tree source byte relative to the bound commit:
   reject before measurement.
5. Precreate the requested output, attempt production, and verify its bytes
   are unchanged.
6. Validate an unmodified complete campaign and report exactly 3,072 positive,
   768 control, and 384 calibration semantic replays.

## C. Evidence semantics

Any failure in this audit is an infrastructure/provenance failure. It leaves
U2 `UNRESOLVED`; it cannot reject the mathematical candidate and cannot be
converted into a favorable scientific result. Earlier partial chunks are
retained for diagnosis but do not count as an independent rerun or enter the
new versioned campaign.
