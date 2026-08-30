# Global Geometry II programmable-sheet experiment

## Fabrication-ready protocol, evidence boundary, and acceptance plan

**Release status:** digital fabrication package; passive bench protocol ready
for review; A4 vector and printer-driver dry preflight passed on the frozen
sanitized profile; no print job was submitted; no object was fabricated; no
camera was calibrated; no hardware was connected; no physical result is
claimed.

This package turns the protocol-v2 q-star model into a small, reproducible
experiment about a sharply scoped question:

> Can one local combinatorial choice—the number of equilateral sectors meeting
> at one vertex—program the sign of an exact intrinsic curvature defect, and
> what calibrated global embedding does a particular passive realization then
> select?

The first clause is an exact finite identity. The second is an unperformed
physical experiment. They must never be reported at the same evidence level.

## 1. Evidence ledger

| Layer | Statement | Status |
|---|---|---|
| Ideal intrinsic complex | A disk made from q equilateral triangles has center defect \((6-q)\pi/3\), boundary defect \(\pi/3\) at each outer vertex, and total defect \(2\pi\) | `exact-finite-identity`; proved below and implemented by `createQStar` |
| Printable geometry | Each face in the SVGs is a nominal 60 mm equilateral triangle; face IDs and cyclic seam graph are explicit | Deterministic vector construction; `PASS_DRIVER_PROFILE_DRY_PREFLIGHT_ONLY` with 1.05 mm minimum analytic clearance; physical print scale still unmeasured |
| Fabricated intrinsic geometry | Cut faces approximate the nominal side lengths and angles | `finite-numerical-estimate`; not measured |
| Virtual hinge/height plant | Bounded q-star response implemented by the in-memory HIL emulator | Engineering model; not a constitutive law |
| Camera reconstruction | Proposed calibrated pose and vertex-fusion pipeline | Protocol only; not executed |
| Global 3-D response | q=5 is expected to admit a cone-like response, q=6 a flat state, and q=7 a saddle/fold response | Qualitative experimental hypotheses; embeddings are nonunique and unvalidated |
| Active actuation | Possible future extrinsic-hinge extension | Not authorized, connected, or validated |

The protocol-v2 implementation is
`website/global-geometry-lab/global-geometry-ii-sheet.js`. Its digests bind
digital records and its CRC checks detect transport corruption; neither is an
authentication mechanism.

## 2. Exact intrinsic model

Take q separate equilateral triangles of side \(s=60\,\mathrm{mm}\). Identify
their center corners, and join their radial edges cyclically. The resulting
finite complex is a topological disk with

\[
 |V|=q+1,\qquad |E|=2q,\qquad |F|=q,\qquad
 \chi=|V|-|E|+|F|=1.
\]

Every triangle angle is exactly \(\pi/3\). The interior center defect and each
boundary defect are therefore

\[
 K_c=2\pi-q\frac{\pi}{3}=\frac{(6-q)\pi}{3},
 \qquad
 K_b=\pi-2\frac{\pi}{3}=\frac{\pi}{3}.
\]

Consequently,

\[
 K_c+\sum_{b=1}^{q}K_b
 =\frac{(6-q)\pi}{3}+q\frac{\pi}{3}=2\pi
 =2\pi\chi.
\]

| Template | Exact center defect | Exact defect at each boundary vertex | Exact total | Extrinsic phase to investigate |
|---|---:|---:|---:|---|
| q=5 | \(+\pi/3\) | \(+\pi/3\) | \(2\pi\) | positive cone-like family |
| q=6 | \(0\) | \(+\pi/3\) | \(2\pi\) | flat state available |
| q=7 | \(-\pi/3\) | \(+\pi/3\) | \(2\pi\) | nonplanar saddle/fold family |

This establishes neither a unique embedding nor a material response. In
particular, the q=7 seam cannot be closed while all seven ideal faces remain
flat and nonoverlapping, but many nonplanar fold modes may satisfy the same
intrinsic program.

## 3. Package inventory and drawing contract

The printable files are:

- `artifacts/global-geometry-ii/fabrication/q5-star-template.svg`
- `artifacts/global-geometry-ii/fabrication/q6-star-template.svg`
- `artifacts/global-geometry-ii/fabrication/q7-star-template.svg`

The same directory contains `fabrication-manifest.json`, which records the
protocol binding, dimensions, exact programs, claim boundaries, and SHA-256
digests, plus the read-only `validate-fabrication.js` reproduction audit. It
also contains:

- `physical-preflight-profile-v1.json`, a sanitized A4 printer profile with no
  host, queue, URI, serial number, user, nickname, or timestamp;
- `physical-preflight-v1.json`, the content-addressed dry-preflight evidence;
  and
- `physical-trial-worksheet-v1.json`, a blank, copy-before-use measurement
  record whose authorization, gates, and decision all remain `NOT_RUN`.

Each file is an A4 portrait SVG with `width="210mm"`, `height="297mm"`, and a
matching `viewBox`. It contains q detached faces. Every face uses the nominal
local coordinates

\[
 (0,0),\quad(60,0),\quad(30,30\sqrt3)
 = (30,51.9615242271)\ \mathrm{mm}.
\]

The artwork has no external font, image, script, or web dependency. Print at
100% or “actual size”; never use “fit to page.” The 10 mm and 100 mm scale bars
are acceptance gauges, not decoration.

The `printer-safe-v2` layout was checked analytically against the frozen A4
imaging box and through unscaled 300 and 600 dpi CUPS dry filters. All three
templates have 1.05 mm minimum analytic clearance; the 300 dpi renderer check
has 12 pixels of minimum foreground clearance. These are file/driver
compatibility results only. They establish neither printer connectivity nor
paper feed, ink output, physical scale, cut accuracy, or material response.
The committed preflight artifact keeps each of those fields explicitly
`NOT_RUN`.

Line semantics do not depend on color:

- solid heavy line: cut perimeter;
- long-dash line inside a radial edge: fold/hinge-edge guide after cutting;
- short-dot box: no-cut/no-hinge fiducial clearance;
- dash-dot square: 20 mm fiducial **location placeholder**; and
- dotted center mark: the corner identified with every other center corner.

The drawn placeholder is intentionally not a camera-decodable marker. Before a
camera trial, replace it with a validated 20 mm tag from a frozen marker
dictionary and record the marker-to-face transform. This prevents decorative
art from silently entering the sensing pipeline as calibration data.

Face `face-i` joins cyclically as follows:

\[
 R_i\longleftrightarrow L_{(i+1)\bmod q}.
\]

Join `R_0` through `R_(q-2)` first. The edge pair
`R_(q-1) <-> L_0` is the labeled final seam. The nominal 1.0 mm hinge gap is a
separate assembly dimension and is not subtracted from the 60 mm face.

## 4. Bill of materials—options, not purchases

No option below authorizes buying, cutting, assembly, camera access, or motion.
Use existing materials where possible and approve substitutions before a
physical run.

### Option A: passive paper prototype

| Component | Suggested specification | Function |
|---|---|---|
| Face stock | A4-compatible 250–300 gsm cardstock | Seven rigid-enough faces plus reprints |
| Hinge material | Low-tack drafting/paper tape or thin cloth tape | Reversible radial hinges |
| Final-seam closure | Removable paper tabs, binder clips, lacing, or hook-and-loop dots | Allows q to change without permanent bonding |
| Cutting setup | Scissors, metal ruler, cutting mat | Face preparation |
| Length gauge | Existing metric ruler or caliper | Scale-bar, side, and hinge-gap checks |
| Camera | Existing webcam or phone operating locally | Optional pose acquisition |
| Camera support | Existing tripod or rigid stand | Repeatable view |

### Option B: more durable passive kit

| Component | Suggested specification | Boundary |
|---|---|---|
| Faces | 0.4–0.8 mm polypropylene/PET or approximately 1 mm chipboard | Deburr all rigid cut edges |
| Hinges | Textile or Tyvek strips with removable adhesive | Characterize hysteresis before comparison |
| Closure | Lacing, paper fasteners, or hook-and-loop | Avoid high-strength loose magnets |
| Sensing | One or two existing cameras on fixed stands | Second view is preferred for occlusion |

### Option C: virtual HIL only

The included JavaScript emulator is the only active system presently in
scope. A future servo/tendon tier would require a separate approval, explicit
low-voltage/current-limited hardware design, mechanical stops, guarded pinch
points, a physical power disconnect, and one-channel-at-a-time calibration.
Changing hinge preference changes an extrinsic embedding; it does **not**
change intrinsic curvature unless face angles, edge lengths, or incidence
actually change and are re-audited.

## 5. Print, fabrication, and assembly protocol

### 5.1 Print and face audit

1. Open the appropriate q-template and print one copy at 100%/actual size.
2. Measure the 10 mm and 100 mm bars in both directions available on the page.
3. Reject the print when the 100 mm bar differs from 100 mm by more than
   0.5 mm, unless that measured scale is frozen as a calibration correction.
4. Confirm that the safety banner and every selected face ID are readable.
5. Cut only the solid perimeters. Do not cut the dotted clearance boxes or
   dashed hinge guides.
6. Measure all three edges of every face. Record instrument, resolution,
   operator, environmental notes, and raw values.
7. Provisional fabrication gate: reject or relabel a face whose maximum edge
   error exceeds 0.5 mm. This is an engineering tolerance, not a theorem.
8. Install validated fiducials only after dimensional acceptance. Record their
   actual four corner coordinates in each face frame.

### 5.2 Cyclic assembly

1. Place faces in ascending ID order with all marked center corners coincident.
2. Leave a measured nominal 1.0 mm gap between adjacent radial cut edges.
3. Bridge `R_i` to `L_(i+1)` with a flexible hinge for
   \(i=0,\ldots,q-2\). Keep tape out of the fiducial clearance zones.
4. Leave `R_(q-1) <-> L_0` open and run the incidence audit.
5. For q=5, lift the patch and close the final seam without creasing a face.
6. For q=6, close the final seam on a flat reference plane without forcing it.
7. For q=7, lift the patch into a low-strain nonplanar fold before closing the
   final seam. Never force it flat or permit overlapping faces to be mistaken
   for a valid planar state.
8. Photograph the apparatus-only front and back, and record stock, hinge lot,
   face IDs, gap measurements, assembly order, and a randomization seed.
9. Repeat the exact incidence audit after closure. Only then may a calibrated
   3-D trial begin.

For a future repeatability study, preregister at least five independent
disassembly/reassembly trials of each q and randomize the assembly order. This
tests selection of an embedding, not the symbolic angle sum.

## 6. Calibration and camera/fiducial reconstruction

### 6.1 Frozen calibration record

A physical measurement remains invalid until one versioned record contains:

- print scale and all measured face-edge lengths;
- camera make/model anonymized to a study ID, image resolution, and lens mode;
- at least ten usable planar calibration-board views spanning position and
  tilt, plus all residuals and rejected-view reasons;
- distortion model and camera intrinsic covariance or bootstrap samples;
- marker dictionary, tag size, tag-to-face transforms, and measurement method;
- a flat q=6 reference-plane capture;
- rigid reference wedges at nominal 0, 30, and 60 degree dihedrals; and
- calibration timestamp, validity interval, software commit, and artifact
  digests.

Provisional validity gates inherited from the research specification are:

- camera reprojection RMS at most 1.0 pixel;
- at least 80% of expected tags observed and every target-critical face
  directly observed;
- fused shared-edge endpoint discrepancy at most 1.5 mm or 2% of face side,
  whichever is larger;
- flat q=6 best-fit-plane RMS at most 2.0 mm; and
- rigid-wedge dihedral error at most 3 degrees.

These gates have not been achieved. A failed gate invalidates the trial; it is
not an unfavorable datum to hide.

### 6.2 Reconstruction

For each visible face f, estimate the rigid pose \((R_f,t_f)\) and its
uncertainty. Transform the three recorded local corners into camera/world
coordinates. Fuse a shared mesh vertex v using uncertainty weights:

\[
 \widehat x_v=
 \left(\sum_{f\ni v}W_{vf}\right)^{-1}
 \sum_{f\ni v}W_{vf}x_{vf}.
\]

Always export the unfused per-face estimates and their spread. Averaging must
not conceal incompatible pose estimates. Report dihedral angles, center height,
height range, RMS distance from the best-fit plane, face-normal distribution,
and an aligned point-cloud discrepancy against the declared simulation.

Intrinsic reconstruction is separate. Given measured triangle sides
\((a,b,c)\), compute each corner angle with the cosine law, sum the incident
angles, and form \(2\pi-\sum\theta\) at the center or
\(\pi-\sum\theta\) on the boundary. Preserve the ideal rational defects beside
these finite estimates.

## 7. Uncertainty budget

The first physical report must publish this table with observed values and
distributions filled in. Blank or failed items produce `NOT_RUN` or
`SENSOR_UNOBSERVABLE`, not guessed values.

| Source | Affects | Proposed characterization | Propagation/reporting |
|---|---|---|---|
| Printer scale and anisotropy | Side lengths, tag scale | 10/100 mm bars in page x/y; repeat measurements | Correlated scale variables; do not treat all edges as independent |
| Cut placement and stock deformation | Intrinsic angles | Three side measurements per face, before and after trials | Bootstrap or Monte Carlo through cosine law |
| Hinge gap and tape thickness | Extrinsic embedding; not ideal defect | Gap at both ends of every radial edge; material thickness | Sensitivity analysis; keep separate from face dimensions |
| Fiducial placement | Face pose | Four installed tag-corner coordinates in face frame | Include transform covariance |
| Camera intrinsics/distortion | All 3-D coordinates | Multi-view calibration residuals and bootstrap | Joint camera-parameter samples |
| Tag localization and pose ambiguity | Face pose | Per-corner image residuals; alternative-pose check | Reject unresolved ambiguity; otherwise pose covariance |
| Occlusion | Vertex fusion | Per-frame direct-observation mask | No zero-uncertainty imputation; second view preferred |
| Shared-edge inconsistency | Global mesh | Unfused endpoint spread | Report maximum and RMS before fusion |
| Reference-plane alignment | q=6 flatness and heights | Repeated plane fits to rigid reference | Carry alignment covariance |
| Dihedral reference | Hinge-angle comparison | 0/30/60 degree wedges | Bias and repeatability interval |
| Assembly/reassembly | Selected global mode | At least five independently seeded assemblies per q | Between-assembly distribution, never pooled away |
| Virtual-model parameters | Simulation discrepancy | Frozen parameter set and local sensitivity sweep | Report model-form discrepancy separately from measurement noise |

For each Monte Carlo sample, perturb shared calibration variables jointly,
reconstruct face poses and vertices, and recompute all intrinsic and extrinsic
observables. Publish central estimates, 95% intervals, sample count, seed, and
the full covariance or samples needed to reproduce them. A nominal q=5 or q=7
sign that changes across the declared uncertainty interval does not pass the
physical sign criterion.

## 8. Protocol-v2 HIL connection contract

The present module exposes an **in-memory-only** emulator:

- schema version: `2`;
- protocol: `ggii-hil/2`;
- safety mode: `OBSERVATION_BOUND`;
- transport: `in-memory-only`;
- `virtualOnly: true`, `hardwareAccess: false`; and
- q range: 5 through 7.

There is no serial, USB, camera, network, timer, filesystem, or device-discovery
path in this module. A future physical adapter must not weaken the following
contract:

1. Start `DISARMED`; `HELLO` and `CAPABILITIES` never move the plant.
2. Set a strictly validated, fresh observation bound to `plantId`,
   `stateRevision`, `stateDigest`, and `snapshotDigest`.
3. Send `ARM` with a unique `sessionId` and no `armEpoch`; retain the returned
   non-null arm epoch.
4. Send each `COMMAND` with that arm epoch and the current `plantId`, expected
   state revision, expected state digest, fresh observation digest, and bounded
   channel list.
5. Accept only strictly increasing sequences, unexpired deadlines, known
   channels, finite bounded positions/rates, and one-time consumption of the
   bound observation.
6. Remeasure after every accepted command. Never infer motion or assembly
   success from command acceptance.
7. Enter `HOLD` when the heartbeat reaches—not merely exceeds—the watchdog
   boundary, or on stale/invalid observation, state mismatch, saturation, or
   another interlock.
8. Treat a checksum-valid `ESTOP` with safety priority. The ESTOP state remains
   latched; a `DISARM` message is not an unlatch operation.
9. Persist the complete pre-state, normalized input, response, post-state, and
   SHA-256 hash-chain event. Validate the transcript before using it as
   evidence.

Protocol CRC32 detects accidental frame corruption over exact canonical bytes.
SHA-256 digests make mutation evident in recorded artifacts. Neither protects
against a malicious endpoint; authenticated transport and an independent
physical safety circuit are required before real motion.

The required emulator fault suite includes corrupt checksum, stale sequence,
deadline expiry, watchdog timeout, saturation, sensor dropout, disconnect,
over-current, stuck channel, and latched ESTOP. Each test must end in the
declared safe state and reproduce the same transcript digest for the same
scenario.

## 9. Closed-loop protocols

### 9.1 Passive human-in-the-loop geometry programming

1. Declare target q and target exact center defect before seeing an embedding.
2. Audit current face incidence and calculate the exact current q-star program.
3. Score legal `ADD_SECTOR` or `REMOVE_SECTOR` actions only when they reduce
   target loss after edit cost; nonpositive-benefit actions are inhibited.
4. Display the chosen local edge pair and predicted exact defect change.
5. Wait for explicit operator confirmation; the software does not mark success
   when advice is issued.
6. Re-audit cyclic incidence and all face IDs, then acquire a fresh calibrated
   observation.
7. Stop on exact target, no improving legal action, invalid sensing, topology
   mismatch, or safety hold.

### 9.2 Virtual bounded hinge loop

1. Select q and freeze the emulator configuration and seed.
2. Generate and validate a synthetic observation for the current plant
   snapshot; label it synthetic.
3. Arm a unique session, issue one bounded command, then remeasure.
4. Compare the new observation with the declared extrinsic target. Intrinsic
   success remains tied to q/incidence, not hinge position.
5. Stop on target tolerance, maximum iterations, no positive predicted benefit,
   any validation failure, watchdog hold, fault, or ESTOP.
6. Export and validate the hash-chained transcript and endpoint snapshots.

The virtual loop is a protocol and control demonstration, not evidence that a
cardstock or actuator system follows the virtual plant.

## 10. Demonstrations and preregistered claims

| Demonstration | Local program | Exact claim | Physical/engineering observation to collect |
|---|---|---|---|
| Positive phase | q=5 | center \(+\pi/3\), each boundary \(+\pi/3\), total \(2\pi\) | Embedding family, center height, plane RMS, fold choice, uncertainty |
| Flat-control phase | q=6 | center 0, each boundary \(+\pi/3\), total \(2\pi\) | Whether a low-strain flat state is recovered; plane RMS gate |
| Negative phase | q=7 | center \(-\pi/3\), each boundary \(+\pi/3\), total \(2\pi\) | Nonplanarity and selected saddle/fold family; never claim uniqueness |
| Local rewrite | q=5 -> 6 -> 7 or reverse | center defect changes by exactly \(-\pi/3\) per added sector | Reassembly burden, mode changes, measurement repeatability |
| HIL safety | fixed q, virtual hinge commands | No new geometric theorem | Deterministic accept/hold/fault/ESTOP transitions and transcript replay |

Trial order, assembly order, seeds, exclusion rules, and acceptance thresholds
must be frozen before acquiring target data. All valid trials are retained.

## 11. Acceptance and falsification criteria

### Digital/fabrication artifact gates

The release candidate passes only if:

1. every SVG is well-formed XML, has A4 millimetre dimensions, has no external
   references or executable content, and contains exactly q uniquely labeled
   face groups;
2. every cut triangle has three 60 mm sides within numeric serialization
   tolerance, a 20 mm fiducial-location square, a center mark, L/R labels, a
   boundary label, and an orientation cue;
3. both scale bars measure 10 mm and 100 mm in the SVG coordinate system;
4. the displayed q-specific defect identity matches the protocol-v2
   `createQStar(q)` output; and
5. the q=5,6,7 module tests and HIL fault/replay tests pass from the documented
   clean command.

A failure is a release-blocking implementation defect, not evidence against
Gauss–Bonnet.

### Prospective physical gates

A q trial is valid only when print, face, incidence, camera, visibility,
shared-edge, reference-plane, and wedge gates pass. For valid trials:

- q=5 physical intrinsic sign passes when the declared 95% interval for the
  measured center defect lies strictly above zero and contains \(+\pi/3\);
- q=6 passes when its interval contains zero and the absolute point estimate is
  no larger than its declared expanded uncertainty;
- q=7 passes when its interval lies strictly below zero and contains
  \(-\pi/3\); and
- every q must have a total-defect interval containing \(2\pi\) after the
  recorded boundary convention is applied.

These criteria test whether the fabricated approximation and reconstruction
recover the ideal program. If they fail, inspect print anisotropy, cut geometry,
incidence, calibration, and uncertainty modeling; report the failure without
changing the symbolic result.

No global-shape hypothesis passes merely because a photograph looks cone-like
or saddle-like. Before physical trials, freeze a numerical descriptor and a
tolerance derived from calibration. A model-comparison claim is falsified when
valid, preregistered observations fall outside that tolerance or when competing
embeddings are merged without a disclosed rule. Negative-curvature
nonuniqueness is an outcome to map, not a nuisance to suppress.

### Stop and falsification boundaries

Stop immediately on a damaged face, sharp edge, forced q=7 flattening,
uncontrolled snap-through, failed camera gate, people entering the camera
frame, stale calibration, actuator/power activity, or any state not explicitly
covered by the approved protocol. Active-tier work remains `NOT_RUN` until
separately authorized.

## 12. Safety and privacy

- Prefer scissors-compatible cardstock, a cutting mat, and cuts directed away
  from hands. Rigid plastic or a craft knife requires appropriate supervision,
  eye protection where relevant, and deburring.
- Do not use loose high-strength magnets. Keep clips and small closures away
  from children and pets.
- Do not force q=7 flat or direct a buckled sheet toward a face or eyes.
- Process camera data locally; frame only the apparatus; do not record people,
  audio, or unrelated space. Release derived poses and deliberately selected
  apparatus images rather than ambient raw video.
- No template in this package is a wiring, actuator, load-bearing, medical, or
  safety-control drawing. The SVG safety banner is part of the artifact and
  must remain visible.
- If an active tier is later approved: low-voltage/current-limited power only,
  guarded pinch points, mechanical stops, reachable physical disconnect,
  software position/rate/current limits, watchdog hold, and never unattended.

## 13. Reproduction commands

From the repository root, validate the mathematical/HIL implementation with:

```sh
node website/global-geometry-lab/test-global-geometry-ii-sheet.js
node website/global-geometry-lab/test-global-geometry-ii-physical-preflight.js
node website/global-geometry-lab/generate-global-geometry-ii-physical-preflight.js --validate-only
```

Validate the SVG package with an XML parser and the deterministic geometry
audit used for the release. A physical run additionally needs a frozen
calibration record, raw measurements, observations, HIL transcript if used,
environment record, claim ledger, and SHA-256 checksums. Until those artifacts
exist, every empirical field remains explicitly `NOT_RUN`.
