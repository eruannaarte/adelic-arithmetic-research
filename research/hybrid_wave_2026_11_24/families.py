"""Test problems for the two engines. Each builder returns (n, constraints, description)."""
from __future__ import annotations

import sys
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'sudoku_gw_wave_2026_11_24'))


def php(holes, switch=None, offset=0):
    """Pigeonhole: holes+1 pigeons, each in exactly one hole, at most one pigeon per hole.
    Unsatisfiable. Counting kills it; parity reasoning provably needs high degree (Razborov 1998).
    With a switch variable z, the pigeon rules apply only when z = 1."""
    P = holes + 1
    x = lambda i, j: offset + i * holes + j
    cons = [('one', [x(i, j) for j in range(holes)], switch) for i in range(P)]
    cons += [('amo', [x(i, j) for i in range(P)]) for j in range(holes)]
    return P * holes, cons


def gf2_rank_and_solve(rows, nvars):
    """rows: list of (set_of_vars, rhs). Returns (consistent, rank, unique_solution_or_None)."""
    piv = {}
    for vs, b in rows:
        v = sum(1 << k for k in vs) | (b << nvars)
        for k in range(nvars - 1, -1, -1):
            if not (v >> k) & 1:
                continue
            if k in piv:
                v ^= piv[k]
            else:
                piv[k] = v
                break
        else:
            if v >> nvars:
                return False, len(piv), None
    if len(piv) < nvars:
        return True, len(piv), None
    sol = [0] * nvars
    for k in sorted(piv):
        v = piv[k]
        s = (v >> nvars) & 1
        for j in range(k):
            if (v >> j) & 1:
                s ^= sol[j]
        sol[k] = s
    return True, len(piv), sol


def random_xor(nvars, m, rng, unsat=True, k=3):
    """Random k-XOR. unsat=True: random right-hand sides, kept only if inconsistent.
    unsat=False: planted solution, kept only if the solution is unique."""
    while True:
        rows = [(rng.sample(range(nvars), k),) for _ in range(m)]
        if unsat:
            rows = [(r[0], rng.randrange(2)) for r in rows]
        else:
            plant = [rng.randrange(2) for _ in range(nvars)]
            rows = [(r[0], sum(plant[v] for v in r[0]) % 2) for r in rows]
        ok, rank, sol = gf2_rank_and_solve(rows, nvars)
        if unsat and not ok:
            return nvars, [('xor', vs, b) for vs, b in rows]
        if not unsat and sol is not None:
            return nvars, [('xor', vs, b) for vs, b in rows], plant


def coupled(holes, ny, m, rng):
    """Parity part + counting part, glued by one switch variable z (variable 0).
    The parity part (random 3-XOR on z, y_1..y_ny with a unique solution) forces z = 1, but only
    through parity. Once z = 1, the pigeon rules switch on and counting refutes them.
    Unsatisfiable overall."""
    while True:
        n_x, cons_x, plant = random_xor(ny + 1, m, rng, unsat=False)
        if plant[0] == 1:
            break
    n_p, cons_p = php(holes, switch=0, offset=ny + 1)
    return ny + 1 + n_p, cons_x + cons_p


def random_3sat(nvars, ratio, rng):
    from pysat.solvers import Solver
    m = round(ratio * nvars)
    while True:
        cls = [[v + 1 if rng.random() < 0.5 else -(v + 1) for v in rng.sample(range(nvars), 3)]
               for _ in range(m)]
        with Solver(name='cadical195', bootstrap_with=cls) as s:
            if not s.solve():
                return nvars, [('clause', c) for c in cls]


def sudoku(puzzle):
    """9x9 Sudoku after cheap propagation, as exactly-one groups over the remaining candidates.
    Satisfiable with a unique solution; 'solved' means every variable is forced."""
    from gw_scale import Grid
    G = Grid(3)
    doms = G.propagate(G.parse(puzzle))
    cands, idx = G.index(doms)
    groups = G.rules(doms, idx)
    cons = [('one', [k - 1 for k in g], None) for g in groups]
    sol = G.backtrack(G.parse(puzzle), {'guesses': 0}, limit=1)[0]
    truth = [int(sol[c[0]] == c[1]) for c in cands]
    return len(cands), cons, truth
