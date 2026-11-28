"""Look at a causal run moment by moment.

Node i lives at moment tau_i = i // (N // NT). Space links join nodes of the same moment; time links
join neighbouring moments (periodic). For a snapshot this prints the spacetime spectral dimension and,
for each moment, how its space links hang together: pieces, largest piece, and the walker's dimension
on that piece.

Usage: python slices.py file.edges [NT=8] [N=512]
"""
import sys
from collections import Counter

import numpy as np
from scipy.sparse.csgraph import connected_components

from analyze import adjacency, giant, spectral_curve, at, torus

path = sys.argv[1]
NT = int(sys.argv[2]) if len(sys.argv) > 2 else 8
N = int(sys.argv[3]) if len(sys.argv) > 3 else 512
per = N // NT
e = np.loadtxt(path, dtype=int, ndmin=2)
tau = np.arange(N) // per
A = adjacency(e, N)
G, nc, sizes = giant(A)
s, ds = spectral_curve(G)
grid = [4, 8, 16, 32]
print(f"{path.split('/')[-2]}/{path.split('/')[-1]}: spacetime pieces={nc} largest={G.shape[0]}  d_s at 4/8/16/32 = "
      + " ".join(f"{v:.2f}" for v in at(s, ds, np.array(grid))))

same = tau[e[:, 0]] == tau[e[:, 1]]
space, time = e[same], e[~same]
fut = Counter(); pst = Counter()
for a, b in time:
    if (tau[b] - tau[a]) % NT == 1:
        fut[a] += 1; pst[b] += 1
    else:
        fut[b] += 1; pst[a] += 1
wl = sum(1 for i in range(N) if fut[i] == 1 and pst[i] == 1)
sdeg = np.bincount(space.ravel(), minlength=N)
print(f"   links: {len(space)} space, {len(time)} time; points with exactly one future and one past link: {wl}/{N}; "
      f"mean space links per point {sdeg.mean():.2f}")
rows = []
for t in range(NT):
    idx = np.flatnonzero(tau == t)
    m = (tau[space[:, 0]] == t)
    sub = space[m] - t * per
    As = adjacency(sub, per) if len(sub) else None
    if As is None or As.nnz == 0:
        rows.append(f"   moment {t}: no space links")
        continue
    Gs, ncs, sz = giant(As)
    sizes_s = [int(x) for x in sz if x > 1]
    lone = int((sz == 1).sum())
    ss, dss = spectral_curve(Gs) if Gs.shape[0] > 2 else (None, None)
    dtxt = " ".join(f"{v:.2f}" for v in at(ss, dss, np.array([2, 4, 8]))) if ss is not None else "-"
    rows.append(f"   moment {t}: pieces {sizes_s} + {lone} lone points; d_s of largest at 2/4/8 = {dtxt}")
print("\n".join(rows))

if "--ref" in sys.argv:
    for name, R in [("8x8 torus (one ideal moment)", torus((8, 8))), ("8x8x8 torus (ideal spacetime)", torus((8, 8, 8)))]:
        s2, d2 = spectral_curve(R)
        print(f"   reference {name}: d_s at 2/4/8 = " + " ".join(f"{v:.2f}" for v in at(s2, d2, np.array([2, 4, 8]))))
