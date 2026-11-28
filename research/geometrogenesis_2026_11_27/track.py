"""Follow a cooling run snapshot by snapshot: how many dimensions does the walker feel?

Usage: python track.py runs/<name> [s values...]
Prints, per snapshot: temperature, mean degree, components, giant size, and d_s at a few walk lengths.
"""
import re
import sys
from pathlib import Path

import numpy as np

from analyze import adjacency, giant, spectral_curve, at

run = Path(sys.argv[1])
grid = np.array([float(x) for x in sys.argv[2:]] or [4, 8, 16])
log = {}
for line in (run / "log.txt").read_text().splitlines():
    m = re.match(r"snap (\d+) step (\d+) T (\S+) E (\S+) edges (\d+) meandeg (\S+) tri (\d+) meansq (\S+) flat_edges (\S+) lattice_nodes (\S+)", line)
    if m:
        log[int(m.group(1))] = dict(T=float(m.group(3)), E=float(m.group(4)), deg=float(m.group(6)), tri=int(m.group(7)),
                                    sq=float(m.group(8)), flat=float(m.group(9)), latt=float(m.group(10)))
print(f"{'snap':>4} {'T':>7} {'E':>10} {'deg':>6} {'tri':>8} {'sq/edge':>8} {'flat':>5} {'latt':>5} {'comps':>5} {'giant':>5}  "
      + " ".join(f"ds@{int(g):<3}" for g in grid))
for f in sorted(run.glob("s_*.edges")):
    k = int(f.stem.split("_")[-1])
    if k not in log:
        continue
    e = np.loadtxt(f, dtype=int, ndmin=2)
    A = adjacency(e, 512)
    G, nc, sizes = giant(A)
    s, ds = spectral_curve(G)
    vals = at(s, ds, grid)
    L = log[k]
    print(f"{k:>4} {L['T']:>7.3g} {L['E']:>10.4g} {L['deg']:>6.2f} {L['tri']:>8} {L['sq']:>8.2f} {L['flat']:>5.2f} {L['latt']:>5.2f} {nc:>5} {G.shape[0]:>5}  "
          + " ".join(f"{v:6.2f}" for v in vals))
