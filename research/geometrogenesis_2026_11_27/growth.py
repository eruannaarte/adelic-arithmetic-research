"""Does the seed grow? Count perfect crystal points snapshot by snapshot.

A point is crystal if it has 6 links, each lying on exactly 4 squares, and none on a triangle (its
neighbourhood looks exactly like the cubic lattice's at this range). Points are split into those that
started inside the seed and those that started in the liquid; crystal points in the liquid mean the
crystal has grown. Also printed: the largest connected cluster of crystal points and the walker's
spectral dimension.

Usage: python growth.py runs/<dir> {slab|cube|none}
"""
import re
import sys
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

from analyze import adjacency, giant, spectral_curve, at

run, shape = Path(sys.argv[1]), sys.argv[2]
N = 512
i = np.arange(N)
x, y, z = i // 64, (i // 8) % 8, i % 8
seed = {"slab": x < 4, "cube": (x < 4) & (y < 4) & (z < 4), "none": np.zeros(N, bool)}[shape]

Ts = {}
for line in (run / "log.txt").read_text().splitlines():
    m = re.match(r"snap (\d+) step \d+ T (\S+) E (\S+)", line)
    if m:
        Ts[int(m.group(1))] = (float(m.group(2)), float(m.group(3)))

print(f"{'snap':>4} {'T':>6} {'E':>7}  crystal: {'in seed':>7} {'in liquid':>9} {'cluster':>7}   d_s@8  d_s@16")
for f in sorted(run.glob("s_*.edges")):
    k = int(f.stem.split("_")[-1])
    e = np.loadtxt(f, dtype=int, ndmin=2)
    A = adjacency(e, N).toarray().astype(np.int32)
    deg = A.sum(1)
    C = A @ A
    S = (C @ A - (deg[:, None] + deg[None, :] - 1)) * A
    ok_link = (S == 4) & (C == 0) | (A == 0)
    crystal = (deg == 6) & ok_link.all(1)
    sub = A[np.ix_(crystal, crystal)]
    cl = 0
    if crystal.any():
        nc, lab = connected_components(csr_matrix(sub), directed=False)
        cl = int(np.bincount(lab).max())
    G, _, _ = giant(adjacency(e, N))
    s, ds = spectral_curve(G)
    d8, d16 = at(s, ds, np.array([8, 16]))
    T, E = Ts.get(k, (float("nan"), float("nan")))
    print(f"{k:>4} {T:>6.3g} {E:>7.0f}  {'':9}{int((crystal & seed).sum()):>7} {int((crystal & ~seed).sum()):>9} {cl:>7}   {d8:5.2f}  {d16:5.2f}")
