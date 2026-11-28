"""Measure the dimension of a graph the way a random walker would feel it.

Spectral dimension: a lazy random walker (stays put with probability 1/2) returns to its start
with probability P(s) after s steps. In d dimensions P(s) ~ s^(-d/2), so
    d_s(s) = -2 dlnP/dlns.
P(s), averaged over starting nodes, is exactly (1/n) * sum_k ((1+mu_k)/2)^s where mu_k are the
eigenvalues of D^-1/2 A D^-1/2, so no sampling noise is involved. On a finite graph the walker
eventually fills it (P -> 1/n); we subtract that stationary 1/n so the curve shows the approach.

Hausdorff (ball) dimension: |B(r)| ~ r^d_H, slope of ln|B| against ln r.

Usage: python analyze.py file.edges [more.edges ...]   (prints a table)
       python analyze.py --refs                        (reference graphs)
"""
import sys
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components, shortest_path

S_GRID = np.array([2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64])


def load(path, n=None):
    e = np.loadtxt(path, dtype=int, ndmin=2)
    if n is None:
        n = int(e.max()) + 1 if e.size else 0
    return e, n


def adjacency(edges, n):
    i, j = edges[:, 0], edges[:, 1]
    A = coo_matrix((np.ones(2 * len(i)), (np.r_[i, j], np.r_[j, i])), shape=(n, n)).tocsr()
    A.data[:] = 1.0
    return A


def giant(A):
    nc, lab = connected_components(A, directed=False)
    sizes = np.bincount(lab)
    keep = np.flatnonzero(lab == sizes.argmax())
    return A[keep][:, keep], nc, np.sort(sizes)[::-1]


def spectral_curve(A):
    n = A.shape[0]
    d = np.asarray(A.sum(1)).ravel()
    Dm = 1.0 / np.sqrt(d)
    M = (A.multiply(Dm[:, None]).multiply(Dm[None, :])).toarray()
    mu = np.linalg.eigvalsh(M)
    lam = np.clip((1 + mu) / 2, 0.0, 1.0)
    s = np.exp(np.linspace(np.log(1.5), np.log(80), 200))
    P = np.array([np.sum(lam ** k) / n for k in s]) - 1.0 / n
    P = np.maximum(P, 1e-300)
    ds = -2 * np.gradient(np.log(P), np.log(s))
    return s, ds


def at(s, ds, grid=S_GRID):
    return np.interp(np.log(grid), np.log(s), ds)


def ball_dimension(A):
    D = shortest_path(A, unweighted=True, directed=False)
    D[np.isinf(D)] = -1
    rmax = int(D.max())
    counts = np.array([(D <= r).sum(1).mean() for r in range(1, rmax + 1)])
    r = np.arange(1, rmax + 1)
    slope = np.gradient(np.log(counts), np.log(r)) if rmax > 1 else np.array([np.nan])
    return rmax, counts, slope


def describe(name, A):
    G, nc, sizes = giant(A)
    s, ds = spectral_curve(G)
    rmax, counts, slope = ball_dimension(G)
    row = at(s, ds)
    head = f"{name:<26} n={G.shape[0]:>4} comps={nc:<3} diam={rmax:<3} meandeg={G.sum()/G.shape[0]:.2f}"
    print(head)
    print("   d_s at s=" + " ".join(f"{k:>5}" for k in S_GRID))
    print("            " + " ".join(f"{v:5.2f}" for v in row))
    print("   ball slope r=1..: " + " ".join(f"{v:.2f}" for v in slope[:10]))
    return row


def torus(dims):
    idx = np.arange(int(np.prod(dims))).reshape(dims)
    edges = []
    for ax in range(len(dims)):
        edges.append(np.c_[idx.ravel(), np.roll(idx, -1, axis=ax).ravel()])
    e = np.vstack(edges)
    return adjacency(e, idx.size)


def random_regular(n, k, seed=0):
    rng = np.random.default_rng(seed)
    while True:
        stubs = np.repeat(np.arange(n), k)
        rng.shuffle(stubs)
        e = stubs.reshape(-1, 2)
        if np.any(e[:, 0] == e[:, 1]):
            continue
        key = np.sort(e, 1)
        if len(np.unique(key, axis=0)) == len(key):
            return adjacency(e, n)


def complete(n):
    i, j = np.triu_indices(n, 1)
    return adjacency(np.c_[i, j], n)


if __name__ == "__main__":
    if sys.argv[1:] == ["--refs"]:
        describe("complete K_512", complete(512))
        describe("random 6-regular, 512", random_regular(512, 6))
        describe("cycle 512 (1D)", torus((512,)))
        describe("torus 16x32 (2D)", torus((16, 32)))
        describe("torus 8x8x8 (3D)", torus((8, 8, 8)))
        describe("torus 5x5x5x4... (4D) 6^4", torus((6, 6, 6, 6)))
    else:
        for p in sys.argv[1:]:
            e, n = load(p)
            describe(p.split("/")[-1], adjacency(e, n))
