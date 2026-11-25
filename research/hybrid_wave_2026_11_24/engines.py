"""Two reasoning engines on the same 0/1 constraint problems, and a "wave" that alternates them.

Problem format: variables 0..n-1 (each 0 or 1) and a list of constraints:
  ('clause', [lits])            OR of literals; literal +v+1 means x_v, -(v+1) means NOT x_v
  ('xor', [vars], b)            x_a + x_b + ... = b (mod 2)
  ('one', [vars], switch)       exactly one of vars is 1; if switch is a variable z, only when z = 1
  ('amo', [vars])               at most one of vars is 1

ALGEBRA (pc_f2): degree-d Polynomial Calculus over the two-element field F_2. Each constraint
becomes polynomial equations (x^2 = x is built in). We take all their linear combinations, and
multiply by variables, as long as the degree stays <= d (Gaussian elimination on a big matrix whose
columns are monomials). The problem is refuted if 1 = 0 can be derived; a variable is forced if
x_v = 0 or x_v = 1 can be derived.

GEOMETRY (sdp_lift): the vector lift. A PSD moment matrix Y over (1, x_0, ..., x_{n-1}) with
Y_vv = Y_0v, pairwise bounds, products of linear equations with each variable, and for every
small constraint a local probability distribution over its allowed assignments that agrees with
Y. Refuted if infeasible; a variable is forced if fixing it the other way is infeasible.

Both engines speak one common language: facts "x_v = a" and "x_u = x_v (+1)". The wave passes
facts back and forth until one engine refutes the problem or nothing new appears.
"""
from __future__ import annotations

import itertools
import time
from collections import deque
from math import comb

import cvxpy as cp
import numpy as np


# ----------------------------------------------------------------------------- algebra over F_2

def poly_mul(p, q):
    """Multilinear product over F_2 of polynomials given as sets of monomials (sorted tuples)."""
    out = set()
    for a in p:
        for b in q:
            m = tuple(sorted(set(a) | set(b)))
            out ^= {m}
    return out


def constraint_polys(con):
    """Polynomial equations (each = 0) over F_2 for one constraint."""
    kind = con[0]
    if kind == 'clause':
        p = {()}
        for lit in con[1]:
            v = abs(lit) - 1
            f = {(v,)} if lit < 0 else {(), (v,)}      # NOT-satisfied factor: x (if lit = NOT x) or 1+x
            p = poly_mul(p, f)
        return [p]
    if kind == 'xor':
        p = {(v,) for v in con[1]}
        if con[2] % 2:
            p ^= {()}
        return [p]
    if kind == 'one':
        vs, z = con[1], con[2]
        s = {(v,) for v in vs} ^ {()}                  # sum x + 1 = 0 (odd count) ...
        out = [s if z is None else poly_mul(s, {(z,)})]
        out += [{(a, b)} for a, b in itertools.combinations(vs, 2)]   # ... and no two together
        return out
    if kind == 'amo':
        return [{(a, b)} for a, b in itertools.combinations(con[1], 2)]
    raise ValueError(kind)


def fact_polys(facts):
    out = []
    for f in facts:
        if f[0] == 'unit':                             # x_v = a
            out.append({(f[1],)} ^ ({()} if f[2] else set()))
        else:                                          # x_u + x_v = a
            out.append({(f[1],), (f[2],)} ^ ({()} if f[3] else set()))
    return out


class PC:
    """Degree-d Polynomial Calculus over F_2, polynomials as Python int bitmasks over monomials.
    Monomials are numbered in order of degree, so the highest set bit is a highest-degree term."""

    def __init__(self, n, d, max_monomials=150_000):   # dense rows: memory grows like monomials^2
        total = sum(comb(n, k) for k in range(d + 1))
        if total > max_monomials:
            raise MemoryError(f'{total} monomials')
        self.n, self.d = n, d
        self.monos = [m for k in range(d + 1) for m in itertools.combinations(range(n), k)]
        self.index = {m: i for i, m in enumerate(self.monos)}
        self.low = sum(comb(n, k) for k in range(d))  # monomials of degree <= d-1
        self.pivots = {}

    def vec(self, poly):
        v = 0
        for m in poly:
            v ^= 1 << self.index[m]
        return v

    def reduce(self, v):
        piv = self.pivots
        while v:
            p = piv.get(v.bit_length() - 1)
            if p is None:
                return v
            v ^= p
        return 0

    def times_var(self, v, x):
        out = 0
        while v:
            low = v & -v
            m = self.monos[low.bit_length() - 1]
            v ^= low
            if x not in m:
                m = tuple(sorted(m + (x,)))
            out ^= 1 << self.index[m]
        return out

    def run(self, polys, deadline=None):
        queue = deque(self.vec(p) for p in polys if all(len(m) <= self.d for m in p))
        steps = 0
        while queue:
            steps += 1
            if deadline and steps % 2000 == 0 and time.time() > deadline:
                return 'timeout'
            v = self.reduce(queue.popleft())
            if not v:
                continue
            lead = v.bit_length() - 1
            self.pivots[lead] = v
            if lead == 0:
                return 'refuted'
            if lead < self.low:                        # degree <= d-1: may multiply by a variable
                for x in range(self.n):
                    queue.append(self.times_var(v, x))
        return 'closed'

    def derived(self, poly):
        return self.reduce(self.vec(poly)) == 0


def pc_f2(n, cons, facts, d, deadline=None, equivalences=True):
    """Returns (status, new_facts, info). status: refuted | closed | timeout | too_big."""
    t = time.time()
    try:
        pc = PC(n, d)
    except MemoryError as e:
        return 'too_big', [], {'error': str(e)}
    polys = [p for c in cons for p in constraint_polys(c)] + fact_polys(facts)
    status = pc.run(polys, deadline)
    new = []
    if status == 'closed':
        known = set(facts)
        for v in range(n):
            for a in (0, 1):
                f = ('unit', v, a)
                if f not in known and pc.derived(fact_polys([f])[0]):
                    new.append(f)
        if equivalences and d >= 1:
            fixed = {f[1] for f in list(known) + new if f[0] == 'unit'}
            free = [v for v in range(n) if v not in fixed]
            for u, v in itertools.combinations(free, 2):
                for a in (0, 1):
                    f = ('eq', u, v, a)
                    if f not in known and pc.derived(fact_polys([f])[0]):
                        new.append(f)
    return status, new, {'seconds': round(time.time() - t, 2), 'rank': len(pc.pivots),
                         'monomials': len(pc.monos)}


# ----------------------------------------------------------------------------- vector lift

def allowed(con):
    kind = con[0]
    if kind == 'clause':
        vs = [abs(l) - 1 for l in con[1]]
        sat = lambda a: any((a[i] == 1) == (l > 0) for i, l in enumerate(con[1]))
    elif kind == 'xor':
        vs = list(con[1])
        sat = lambda a: sum(a) % 2 == con[2] % 2
    else:
        return None, None
    return vs, [a for a in itertools.product((0, 1), repeat=len(vs)) if sat(a)]


def sdp_lift(n, cons, facts, probe=True, solver='CLARABEL', local_max=4):
    """Returns (status, new_facts, info). status: refuted | feasible | solver_error."""
    t = time.time()
    Y = cp.Variable((n + 1, n + 1), symmetric=True)
    C = [Y >> 0, Y[0, 0] == 1, cp.diag(Y)[1:] == Y[0, 1:], Y >= 0]
    for i in range(1, n + 1):                         # x_i x_j <= x_i
        C.append(Y[i, 1:] <= Y[0, i])
    C.append(Y[1:, 1:] >= Y[0:1, 1:] + Y[1:, 0:1] - 1)  # x_i x_j >= x_i + x_j - 1
    for con in cons:
        if con[0] in ('clause', 'xor'):
            vs, al = allowed(con)
            if len(vs) > local_max:
                continue
            p = cp.Variable(len(al), nonneg=True)
            A = np.array(al, dtype=float)
            C.append(cp.sum(p) == 1)
            for i, v in enumerate(vs):
                C.append(A[:, i] @ p == Y[0, v + 1])
                for j in range(i + 1, len(vs)):
                    C.append((A[:, i] * A[:, j]) @ p == Y[v + 1, vs[j] + 1])
        elif con[0] == 'one':
            vs, z = [v + 1 for v in con[1]], con[2]
            if z is None:
                C.append(cp.sum(Y[0, vs]) == 1)
                C.append(cp.sum(Y[:, vs], axis=1) == Y[:, 0])     # x_k * (sum x - 1) = 0
            else:
                C.append(cp.sum(Y[z + 1, vs]) == Y[0, z + 1])
            for a, b in itertools.combinations(vs, 2):
                C.append(Y[a, b] == 0)
        elif con[0] == 'amo':
            for a, b in itertools.combinations([v + 1 for v in con[1]], 2):
                C.append(Y[a, b] == 0)

    def fact_con(f):
        if f[0] == 'unit':
            return [Y[0, f[1] + 1] == f[2]]
        u, v = f[1] + 1, f[2] + 1
        if f[3] == 0:
            return [Y[u, u] + Y[v, v] - 2 * Y[u, v] == 0]
        return [Y[u, u] + Y[v, v] + 1 + 2 * Y[u, v] - 2 * Y[0, u] - 2 * Y[0, v] == 0]

    base = C + [c for f in facts for c in fact_con(f)]

    def solve(extra):
        prob = cp.Problem(cp.Minimize(0), base + extra)
        try:
            prob.solve(solver=solver)
        except cp.error.SolverError:
            return 'solver_error'
        return prob.status

    st = solve([])
    info = {'solves': 1}
    if st in ('infeasible', 'infeasible_inaccurate'):
        info['seconds'] = round(time.time() - t, 2)
        return 'refuted', [], info
    if st not in ('optimal', 'optimal_inaccurate'):
        info['seconds'] = round(time.time() - t, 2)
        return 'solver_error', [], info
    belief = np.array(Y.value[0, 1:])
    info['beliefs'] = [round(float(b), 4) for b in belief]
    new = []
    if probe:
        known = {f[1] for f in facts if f[0] == 'unit'}
        # An interior-point solution of a feasibility problem lies near the centre of the feasible
        # set, so only variables sitting at 0 or 1 can be forced. Confirm each with a probe.
        for v in range(n):
            if v in known:
                continue
            b = belief[v]
            if min(b, 1 - b) > 1e-3:
                continue
            a = int(round(b))
            info['solves'] += 1
            if solve([Y[0, v + 1] == 1 - a]) in ('infeasible', 'infeasible_inaccurate'):
                new.append(('unit', v, a))
    info['seconds'] = round(time.time() - t, 2)
    return 'feasible', new, info


# ----------------------------------------------------------------------------- the wave

def wave(n, cons, d, max_rounds=20, log=print, deadline=None):
    facts, history = [], []
    for r in range(1, max_rounds + 1):
        st, new, info = pc_f2(n, cons, facts, d, deadline=deadline)
        history.append({'round': r, 'engine': 'algebra', 'status': st, 'new_facts': len(new),
                        **{k: v for k, v in info.items() if k != 'beliefs'}})
        log(f'  round {r} algebra(d={d}): {st}, +{len(new)} facts')
        if st == 'refuted':
            return 'refuted_by_algebra', history, facts
        if st in ('timeout', 'too_big'):
            return st, history, facts
        facts += new
        st, new2, info = sdp_lift(n, cons, facts)
        history.append({'round': r, 'engine': 'geometry', 'status': st, 'new_facts': len(new2),
                        **{k: v for k, v in info.items() if k != 'beliefs'}})
        log(f'  round {r} geometry: {st}, +{len(new2)} facts')
        if st == 'refuted':
            return 'refuted_by_geometry', history, facts
        if st == 'solver_error':
            return st, history, facts
        facts += new2
        if not new and not new2:
            return 'stuck', history, facts
    return 'max_rounds', history, facts
