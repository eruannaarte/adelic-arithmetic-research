"""Plant a crystal seed in a melt.

The perfect 8x8x8 crystal labels point i as (x, y, z) = (i // 64, (i // 8) % 8, i % 8). A seed is a
set of those points. The starting network keeps every crystal link that touches the seed and every
melt link between points outside it, so the seed is a piece of perfect crystal embedded in liquid.

Usage: python seed.py crystal.edges melt.edges {slab|cube|none} out.edges
  slab: x < 4 (256 points, two flat faces)   cube: x, y, z < 4 (64 points)   none: the melt alone
"""
import sys

import numpy as np

crystal_path, melt_path, shape, out = sys.argv[1:5]
N = 512
i = np.arange(N)
x, y, z = i // 64, (i // 8) % 8, i % 8
seed = {"slab": x < 4, "cube": (x < 4) & (y < 4) & (z < 4), "none": np.zeros(N, bool)}[shape]

cr = np.loadtxt(crystal_path, dtype=int)
me = np.loadtxt(melt_path, dtype=int)
keep_cr = cr[seed[cr[:, 0]] | seed[cr[:, 1]]]
keep_me = me[~seed[me[:, 0]] & ~seed[me[:, 1]]]
edges = np.vstack([keep_cr, keep_me])
edges = np.unique(np.sort(edges, 1), axis=0)
np.savetxt(out, edges, fmt="%d")
print(f"{shape}: {seed.sum()} seed points, {len(keep_cr)} crystal links, {len(keep_me)} melt links -> {out}")
