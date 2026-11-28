# Geometrogenesis toy: does space condense out of a complete graph?

A small classical experiment in the spirit of quantum graphity (Konopka, Markopoulou, Smolin 2006):
start from the complete graph K_N, where every node touches every other and there is no distance
or dimension, then cool it under local rules and measure what dimension a random walker feels.

## Model (`geo.c`)

- 512 nodes, starting as K_512 (130,816 links).
- Energy, all local:
  - valence `wa·Σ(deg − D0)²`;
  - flatness `wb·Σ_links(squares − S0)²`;
  - `wc·#triangles`.
- The d-dimensional cubic lattice has `D0 = 2d`, `S0 = 2(d−1)` and no triangles, so it has zero energy.
- Moves are local in the graph: remove a link, add a link two steps away, or slide a link's end one
  step. 1% of moves toggle a random pair.
- Metropolis with geometric cooling.
- The incremental bookkeeping is checked against full recounts (`check` argument).
- The optional arguments are `[check] [init.edges|-] [NT] [wt] [keep_whole]`. Any combination
  restarts from a saved snapshot or adds a time direction (see Part 2). The new options consume no
  random numbers when they are off, so the final source should reproduce the earlier runs; this was
  checked bit for bit on two of them. All 512-point runs used seed 1, except `d3slow` (seed 11).

## Measurement (`analyze.py`, `track.py`)

The spectral dimension `d_s(s) = −2 dlnP/dlns` comes from the exact average return probability of a
lazy random walk, computed from eigenvalues with the stationary 1/n subtracted. It is reported for
the largest component.

Reference graphs, all with 512 nodes (6^4 = 1296 for 4D):

| graph | d_s at s=4 | 8 | 16 | 32 |
|---|---|---|---|---|
| complete graph | 5.56 | 11.1 | 22.3 | 44.5 (no plateau: infinite) |
| random 6-regular | 2.88 | 4.28 | 6.75 | 11.3 (no plateau) |
| ring (1D) | 0.94 | 0.98 | 1.00 | 1.01 |
| torus 16×32 (2D) | 2.04 | 2.11 | 2.12 | 2.22 |
| torus 8×8×8 (3D) | 2.78 | 3.33 | 3.58 | 4.45 (finite size bends it up) |

## Results (seed 1, T 3 → 0.02, 2·10^7 moves unless noted)

| run | rule | final energy | what condensed | d_s at s=4 / 8 / 16 / 32 |
|---|---|---|---|---|
| `ctl` | valence only (D0 = 6, no flatness) | 0 | a 6-regular small-world tangle | 2.66 / 3.52 / 4.97 / 7.79, still climbing |
| `d1a` | 1D (D0 = 2, S0 = 0) | 0 (exact ground state) | three separate rings (284, 210, 18 nodes) | 0.95 / 0.99 / 1.01 / 1.03 |
| `d2a` | 2D (D0 = 4, S0 = 2) | 488 | 45 closed bubbles plus a 115-node piece | the giant piece's numbers are not meaningful |
| `d3a` | 3D (D0 = 6, S0 = 4) | 1466 | one connected glass | 2.46 / 2.48 / 2.37 / 2.74, a plateau near 2.4 |
| `d3slow` | 3D, reheated to T = 4 from d3a's first snapshot, 3·10^8 moves | 1262 | grains strung on narrow necks, diameter 21 | 2.44 / 2.16 / 1.28 / 1.04 |

Observations:

1. **The flatness rule is what makes space.** With only a neighbor-count rule the network settles at
   zero energy into a tangle with no dimension. Its d_s keeps rising like a random regular graph's.
   Adding "each link should close squares" produces finite, plateaued dimensions.
2. **1D works perfectly.** The 1D rule reaches its exact ground state: rings, d_s = 1.00. The
   universe split into three disconnected rings, though; nothing in the rule asks for one.
3. **The 2D rule budded off closed bubble universes.** 22 of the 45 pieces are perfect cubes
   (8 nodes, every corner of degree 3, every link on 2 squares). Most other pieces are larger
   square-tiled spheres with exactly 8 degree-3 corners. That count is forced by Euler's formula:
   for a sphere tiled by squares, Σ(4 − deg) = 4χ = 8. Locally flat almost everywhere, each bubble must
   hold its curvature in 8 corners to close up. The flat torus (energy 0) was never reached.
4. **The 3D rule froze before reaching 3.** A fast cooling gives one connected glass. About 2/3 of its
   links sit on exactly 4 squares, a quarter touch a triangle, and the walker reads d_s ≈ 2.4 flat
   across scales. Cooling 15× more slowly lowers the energy, but by making bubbles: dense grains
   joined by necks one or two nodes wide. There d_s is ≈ 2.4 at short range and falls to ≈ 1 at long
   range, because the walker is threading a chain.

These failure modes match the history of dynamical-triangulation quantum gravity. Euclidean
dynamical triangulations found a crumpled phase and a branched-polymer phase of baby universes on
thin necks, not 4D space. Causal dynamical triangulations (Ambjørn, Jurkiewicz, Loll) obtained a
4-dimensional large-scale universe only after imposing a causal time direction, and found d_s ≈ 2
at short scales.

## Part 2: adding a time direction

Causal dynamical triangulations only produced a large-scale 4D universe once spacetime was built
with a time direction. Three versions of that idea were added to `geo.c`, all with the 3D rule
(D0 = 6, S0 = 4):

- **Slices.** Point i lives at moment `i // 64` of 8 periodic moments. Links may only join points in
  the same moment (space links) or neighbouring moments (time links). The start is the causal complete
  graph: every allowed link present (48,896 links instead of 130,816).
- **Worldlines** (`wt`). Each point is asked for exactly one link to the next moment and one to the
  previous.
- **No tearing** (`keep_whole`). A move that would split one moment's space into two pieces is
  refused. This is the graph version of CDT's fixed spatial topology. It is checked with a search
  inside the moment.

`slices.py` measures each moment separately. On the ideal 8×8×8 crystal, every moment is one 64-point
piece with d_s 1.70 / 2.23 / 2.56 at s = 2 / 4 / 8, and all 512 points have one future and one past link.

| run | time rule | moves | final energy | spacetime | each moment's space | d_s at s=4 / 8 / 16 / 32 |
|---|---|---|---|---|---|---|
| `d3a` (part 1) | none | 2·10^7 | 1466 | 1 piece | n/a | 2.46 / 2.48 / 2.37 / 2.74 |
| `c3a` | slices | 2·10^7 | 1670 | 4 pieces | shattered: 4–7 pieces plus loose points | 2.38 / 2.10 / 1.47 / 1.49 |
| `c3b` | slices, worldlines (1) | 2·10^7 | 2634 | 1 piece | 4–7 pieces | 2.30 / 2.01 / 1.46 / 1.48 |
| `c3slow` | slices, worldlines (1) | 2·10^8 | 2584 | 20 pieces, largest 105 | 6–9 pieces | 2.34 / 1.77 / 0.64 / 0.54 |
| `k3a` | slices, no tearing | 2·10^7 | 1504 | 1 piece | one stringy piece, 2.7 space links per point, d_s 1.3–1.6 | 2.44 / 2.40 / 2.24 / 2.60 |
| `k3b` | slices, no tearing, worldlines (1) | 2·10^7 | 2492 | 1 piece | one piece, d_s 1.5–1.8 | 2.38 / 2.28 / 2.11 / 2.45 |
| `k3slow` | same as k3b | 2·10^8 | 2188 | 1 piece | one piece | 2.37 / 2.28 / 2.08 / 2.28 |
| `k3w4` | slices, no tearing, worldlines (4) | 2·10^7 | 3384 | 1 piece, 46% intact worldlines | one piece, d_s ≈ 1.5 | 2.49 / 2.59 / 2.62 / 3.27 |
| `k3w4slow` | same as k3w4 | 2·10^8 | 2732 | 1 piece, 59% intact worldlines | one piece, d_s ≈ 1.5 | 2.54 / 2.72 / 2.84 / 3.58 |
| ideal crystal | | | 0 | 1 piece, all worldlines | 8×8 torus | 2.78 / 3.33 / 3.58 / 4.45 |

Crystal controls, starting from the perfect 8×8×8 crystal:

| run | treatment | result |
|---|---|---|
| `x3` | warm to T = 1.5, cool to 0.02 | survives: energy 42, d_s identical to the crystal |
| `x3t` | same, with slices, no tearing and worldlines (4) | survives better: energy 28, all 512 worldlines intact |
| `melt_1.75` … `melt_2.5` | hold at fixed T for 10^7 moves | melts at every one; at T = 1.75 within 4·10^6 moves |
| `x3hot` | warm to T = 3, cool to 0.02 | refreezes into the glass: energy 1508, d_s 2.43 / 2.36 / 2.08 / 2.26 |

Observations:

1. **A time direction alone does not help.** With slices only, the baby universes move inside the
   moments: each moment's space shatters, and slow cooling shatters spacetime into 20 separate tubes.
2. **No tearing fixes the topology but not the geometry.** Every moment stays one piece, but a stringy,
   nearly tree-like one, and spacetime stays near d_s ≈ 2.4.
3. **Strong worldlines move the number in the right direction.** With every point persisting from
   moment to moment, the spacetime reading climbs toward the crystal's (2.84 at s = 16, against 3.58), but
   each moment's space is still stringy.
4. **3D space is the stable state; the problem is reaching it.** The crystal survives warming to
   T = 1.5, melts between 1.5 and 1.75, and the melt never refreezes into a crystal on cooling. It
   supercools into the same glass the complete graph produces. This is how a first-order transition
   behaves, like water that stays liquid below freezing until something seeds the ice.

CDT avoids this partly because its moves only ever pass through valid spacetimes (simplicial
manifolds), so it never has to escape a tangle. Starting from the complete graph means starting
outside that class. A natural next test is seeding: plant a small crystal in the cooling melt and
see whether it grows.

## Part 3: planting a seed

`seed.py` builds a starting network from a piece of the perfect crystal plus a liquid. It keeps every
crystal link touching the seed and every liquid link between points outside it. `growth.py` counts
**crystal points**: 6 links, each on exactly 4 squares, none on a triangle. It counts them inside the
seed region and in the liquid; crystal points appearing in the liquid would mean growth.

- **Slab:** x < 4, 256 points, 128 of them fully interior, two flat faces. The liquid is the crystal
  melted at T = 2 (`melt_2.0`).
- **Cube:** 4×4×4, 64 points, 8 interior.
- **Time slab:** the same slab, which with time on means moments 0–3 are perfect 8×8 sheets. The
  liquid is the crystal melted at T = 2 under slices, no tearing and worldlines (4) (`tmelt`). Its
  interface is much cleaner: starting energy 3038 against 8498.

Crystal points remaining in the seed's interior (out of 128 for slabs, 8 for the cube), and crystal
points gained in the liquid, at the last snapshot:

| seed | rules | T | moves | left in seed | gained in liquid |
|---|---|---|---|---|---|
| slab | no time | 0.7 | 2·10^8 | ≈ 115 (flat after the first quarter) | 2 |
| slab | no time | 0.8 | 5·10^7 | 117 | 0 |
| slab | no time | 0.85 / 0.9 / 0.95 | 2·10^8 | 87 / 35 / 17 | 0 / 1 / 0 |
| slab | no time | 1.0 / 1.2 / 1.4 | 5·10^7 | 35 / 7 / 3 | 0–1 |
| cube | no time | 0.8 / 0.9 / 1.0 | 5·10^7 | 1 / 0 / 0 | 5 / 9 / 7 scattered, largest cluster ≤ 2 |
| time slab | slices, no tearing, worldlines (4) | 0.8 / 1.0 / 1.2 / 1.4 | 5·10^7 | 101 / 83 / 13 / 0 | 0–1 |
| none (control) | either | 0.8–1.4 | 5·10^7 | n/a | ≤ 14 scattered in total, largest cluster ≤ 3 |
| slab (`cool_slab`) | no time | cooled 0.9 → 0.2 | 2·10^8 | 95 at T 0.67, then heals to 103 | 3 |
| time slab (`cool_tslab`) | slices, no tearing, worldlines (4) | cooled 1.0 → 0.2 | 2·10^8 | 107 at T 0.73, then heals to 122 | 0 |

Observations:

1. **No seed grew at any temperature.** No run turned more than a handful of liquid points into crystal,
   and those were scattered (largest cluster ≤ 3), no more than the unseeded controls produced.
2. **Above about 0.8 the seed melts from its surface.** The perfect crystal with no surface survived
   T = 1.5, but a slab melts even at 0.85–0.95. Melting starts at surfaces, which is why a flawless
   crystal can be superheated.
3. **Small seeds dissolve.** The 4×4×4 cube vanishes at every temperature tried, as nucleation theory
   predicts for a seed below critical size: too much surface for its volume.
4. **Time helps the seed survive, not grow.** At T = 1.0 the time slab keeps 83 interior points against
   35 without time, but the liquid moments never become sheets.
5. **Where the seed stops melting (about 0.7–0.8), the liquid has stopped rearranging.** Moves are
   still accepted (between about 1 in 200 and 1 in 2,000, depending on the run), but the energy sits flat:
   the network jiggles in place. Slow cooling past this point keeps the seed and lets its damaged
   surface heal (the time slab ends with 122 of 128 interior points and spacetime d_s ≈ 3.0–3.1, because
   half of it is crystal), but the liquid half never joins. There is no temperature window where the
   crystal is favoured at its surface and the liquid is still mobile enough to join it.

Why the liquid wins so easily: the number of ways to wire 512 labelled points so each has 6 links is
about e^7421 (Bender–Canfield/McKay estimate). The number of ways to wire them as a perfect 8×8×8
crystal is 512!/|Aut| ≈ e^2676, with |Aut| = 16³·3! = 24,576. Disorder outnumbers order by about
e^4700, so the crystal's energy advantage only wins once the temperature is low. A crude balance puts
that below T ≈ 0.4–0.8, and by then the local moves are frozen. In other words, the model's space can
survive but cannot be born from the tangle. This entropy of disordered graphs is a known obstacle for
emergent-geometry models built on graphs.

## Caveats

- 512 nodes is small. Even a perfect 8×8×8 crystal only shows d_s ≈ 3.3 over a short range.
- One seed per rule.
- Local Metropolis on a glassy landscape. Parallel tempering or larger N might reach the crystal.
- "Dimension" here means what a diffusing walker feels, which is one of several definitions.

## Reproduce

The run snapshots (`runs/`, about 15 MB) and the compiled `geo` binary are not committed; the
commands below regenerate them. `space-from-a-tangle.html` is the source of the interactive page
(a 216-point live version of the model, plus a folding-chain mode using the HP model of protein folding).

```bash
clang -O2 -march=native -o geo geo.c -lm
./geo 512 6 4 1 1 2 3 0.02 20000000 1 runs/d3a/s 20
python track.py runs/d3a 4 8 16 32
# time direction: 8 moments, worldlines weight 4, no tearing
./geo 512 6 4 1 1 2 3 0.02 20000000 1 runs/k3w4/s 20 0 - 8 4 1
python slices.py runs/k3w4/s_020.edges
```
