"""The richer shared language: engines that exchange short clauses and short parity equations.

In engines.py the two engines could only hand each other facts of the form "x = a" and
"x = y (+1)". On random 3-SAT neither engine could ever derive one, so the wave never started.

Here the shared language is the constraint language itself:
  ('clause', lits)   up to 3 literals: means the same thing in both worlds, because a clause is the
                     polynomial prod(1 - literal) = 0, valid over F_2 and over the reals
  ('xor', vars, b)   up to 4 variables: native to the algebra; the geometry takes it as a local
                     probability distribution (level 1) or an exact degree-<=4 moment equation
                     (level 2)
Each engine derives every such short fact it can and passes it on as a new constraint.

  algebra_rich    degree-d Polynomial Calculus over F_2 (engines.PC), then a scan for every
                  short clause and short parity equation in the derived span
  geometry_rich   the level-1 vector lift (as in engines.sdp_lift), then a scan for 0/1 beliefs,
                  pair probabilities and local-assignment probabilities that sit at 0, each
                  confirmed by a probe (fix those values, check the lift becomes infeasible)
  level2_lift     a stronger lift: positive semidefinite moment matrix over all monomials of
                  degree <= 2 (Lasserre / sum-of-squares degree 4). Used to refute only.
"""
from __future__ import annotations

import itertools
import time

import cvxpy as cp
import numpy as np
import scipy.sparse as sp

from engines import PC, constraint_polys, poly_mul, allowed


# ----------------------------------------------------------------------------- shared language

def canon(con):
    if con[0] == 'clause':
        return ('clause', tuple(sorted(set(con[1]), key=lambda l: (abs(l), l))))
    if con[0] == 'xor':
        return ('xor', tuple(sorted(con[1])), con[2] % 2)
    return (con[0], tuple(con[1])) + tuple(con[2:])


class Knowledge:
    """Known short facts, with subsumption so the exchange does not repeat itself."""

    def __init__(self, cons):
        self.clauses, self.xors = set(), set()
        for c in cons:
            self.add(c)

    def subsumed(self, con):
        con = canon(con)
        if con[0] == 'clause':
            lits = con[1]
            if any(-l in lits for l in lits):
                return True                                # tautology
            return any(frozenset(s) in self.clauses
                       for k in range(1, len(lits) + 1) for s in itertools.combinations(lits, k))
        if con[0] == 'xor':
            if len(con[1]) == 1:                           # same as a unit clause
                v = con[1][0]
                return self.subsumed(('clause', [v + 1 if con[2] else -(v + 1)]))
            return (con[1], con[2]) in self.xors
        return False

    def add(self, con):
        con = canon(con)
        if con[0] == 'clause':
            self.clauses.add(frozenset(con[1]))
        elif con[0] == 'xor':
            self.xors.add((con[1], con[2]))


def clause_poly_f2(lits):
    p = {()}
    for lit in lits:
        v = abs(lit) - 1
        p = poly_mul(p, {(v,)} if lit < 0 else {(), (v,)})
    return p


# ----------------------------------------------------------------------------- algebra

def algebra_rich(n, cons, d, max_clause=3, max_xor=4, cap=4000, deadline=None):
    t = time.time()
    try:
        pc = PC(n, d)
    except MemoryError as e:
        return 'too_big', [], {'error': str(e)}
    st = pc.run([p for c in cons for p in constraint_polys(c)], deadline)
    info = {'rank': len(pc.pivots), 'monomials': len(pc.monos)}
    if st != 'closed':
        info['seconds'] = round(time.time() - t, 2)
        return st, [], info
    K = Knowledge(cons)
    new = []

    def offer(con):
        if len(new) < cap and not K.subsumed(con):
            K.add(con)
            new.append(canon(con))

    for k in range(1, min(max_clause, d) + 1):             # short clauses, shortest first
        for vs in itertools.combinations(range(n), k):
            for signs in itertools.product((1, -1), repeat=k):
                lits = [s * (v + 1) for s, v in zip(signs, vs)]
                if not K.subsumed(('clause', lits)) and pc.derived(clause_poly_f2(lits)):
                    offer(('clause', lits))
    for k in range(2, min(max_xor, d) + 1):                # short parity equations
        for vs in itertools.combinations(range(n), k):
            lin = {(v,) for v in vs}
            for b in (0, 1):
                if pc.derived(lin ^ ({()} if b else set())):
                    offer(('xor', list(vs), b))
    info['seconds'] = round(time.time() - t, 2)
    return 'closed', new, info


# ----------------------------------------------------------------------------- geometry, level 1

def build_level1(n, cons, local_max=4):
    Y = cp.Variable((n + 1, n + 1), symmetric=True)
    C = [Y >> 0, Y[0, 0] == 1, cp.diag(Y)[1:] == Y[0, 1:], Y >= 0]
    for i in range(1, n + 1):
        C.append(Y[i, 1:] <= Y[0, i])
    C.append(Y[1:, 1:] >= Y[0:1, 1:] + Y[1:, 0:1] - 1)
    locs = []
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
            locs.append((vs, al, p))
        elif con[0] == 'one':
            vs = [v + 1 for v in con[1]]
            C.append(cp.sum(Y[0, vs]) == 1)
            C.append(cp.sum(Y[:, vs], axis=1) == Y[:, 0])
            for a, b in itertools.combinations(vs, 2):
                C.append(Y[a, b] == 0)
        elif con[0] == 'amo':
            for a, b in itertools.combinations([v + 1 for v in con[1]], 2):
                C.append(Y[a, b] == 0)
    return Y, C, locs


INFEASIBLE = ('infeasible', 'infeasible_inaccurate')


def geometry_rich(n, cons, solver='CLARABEL', tol=1e-4, max_probes=400):
    t = time.time()
    Y, C, locs = build_level1(n, cons)

    def solve(extra):
        prob = cp.Problem(cp.Minimize(0), C + extra)
        try:
            prob.solve(solver=solver)
        except cp.error.SolverError:
            return 'solver_error'
        return prob.status

    st = solve([])
    info = {'solves': 1}
    if st in INFEASIBLE:
        info['seconds'] = round(time.time() - t, 2)
        return 'refuted', [], info
    if st not in ('optimal', 'optimal_inaccurate'):
        info['seconds'] = round(time.time() - t, 2)
        return 'solver_error', [], info
    Yv = Y.value
    # Candidates: events whose probability sits at 0 at the (near-central) interior-point solution.
    cand = []
    for v in range(n):
        b = Yv[0, v + 1]
        for a, pr in ((1, b), (0, 1 - b)):
            if pr < tol:
                cand.append(((v, a),))
    for u, v in itertools.combinations(range(n), 2):
        pu, pv, puv = Yv[0, u + 1], Yv[0, v + 1], Yv[u + 1, v + 1]
        for (a, b), pr in (((1, 1), puv), ((1, 0), pu - puv), ((0, 1), pv - puv),
                           ((0, 0), 1 - pu - pv + puv)):
            if pr < tol:
                cand.append(((u, a), (v, b)))
    for vs, al, p in locs:
        if len(vs) == 3:
            for alpha, pr in zip(al, p.value):
                if pr < tol:
                    cand.append(tuple(zip(vs, alpha)))
    K = Knowledge(cons)
    new = []
    for event in sorted(cand, key=len):
        lits = [-(v + 1) if a else (v + 1) for v, a in event]   # clause = "not this event"
        if K.subsumed(('clause', lits)):
            continue
        if info['solves'] > max_probes:
            info['probe_cap_hit'] = True
            break
        info['solves'] += 1
        if solve([Y[0, v + 1] == a for v, a in event]) in INFEASIBLE:
            K.add(('clause', lits))
            new.append(canon(('clause', lits)))
    info['candidates'] = len(cand)
    info['seconds'] = round(time.time() - t, 2)
    return 'feasible', new, info


# ----------------------------------------------------------------------------- geometry, level 2

def real_mul(p, q):
    out = {}
    for a, ca in p.items():
        for b, cb in q.items():
            m = tuple(sorted(set(a) | set(b)))
            out[m] = out.get(m, 0.0) + ca * cb
    return {m: c for m, c in out.items() if abs(c) > 1e-12}


def real_poly(con):
    """The constraint as real polynomial equations (each = 0) on 0/1 variables."""
    if con[0] == 'clause':
        p = {(): 1.0}
        for lit in con[1]:
            v = abs(lit) - 1
            p = real_mul(p, {(v,): 1.0} if lit < 0 else {(): 1.0, (v,): -1.0})
        return [p]
    if con[0] == 'xor':                                    # parity = (1 - prod(1 - 2x)) / 2
        q = {(): 1.0}
        for v in con[1]:
            q = real_mul(q, {(): 1.0, (v,): -2.0})
        p = {m: -c / 2 for m, c in q.items()}
        p[()] = p.get((), 0.0) + 0.5 - (con[2] % 2)
        return [p]
    if con[0] == 'one':
        vs = con[1]
        out = [{**{(v,): 1.0 for v in vs}, (): -1.0}]
        out += [{(a, b): 1.0} for a, b in itertools.combinations(vs, 2)]
        return out
    if con[0] == 'amo':
        return [{(a, b): 1.0} for a, b in itertools.combinations(con[1], 2)]
    raise ValueError(con[0])


def level2_lift(n, cons, solver='CLARABEL', max_n=32):
    """Degree-4 sum-of-squares: refuted or feasible."""
    if n > max_n:
        return 'too_big', {'n': n}
    t = time.time()
    B = [()] + [(i,) for i in range(n)] + list(itertools.combinations(range(n), 2))
    U = [m for k in range(5) for m in itertools.combinations(range(n), k)]
    uidx = {m: i for i, m in enumerate(U)}
    N = len(B)
    rows, cols = [], []
    for i, a in enumerate(B):
        for j, b in enumerate(B):
            rows.append(i * N + j)
            cols.append(uidx[tuple(sorted(set(a) | set(b)))])
    A = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(N * N, len(U)))
    y = cp.Variable(len(U))
    X = cp.Variable((N, N), PSD=True)
    C = [cp.vec(X, order='C') == A @ y, y[0] == 1, y >= 0]
    eq_rows = []
    for con in cons:
        for p in real_poly(con):
            dp = max(len(m) for m in p)
            for k in range(0, 5 - dp):
                for m in itertools.combinations(range(n), k):
                    q = real_mul(p, {m: 1.0})
                    eq_rows.append(q)
    if eq_rows:
        r, c, v = [], [], []
        for i, q in enumerate(eq_rows):
            for m, coef in q.items():
                r.append(i); c.append(uidx[m]); v.append(coef)
        E = sp.csr_matrix((v, (r, c)), shape=(len(eq_rows), len(U)))
        C.append(E @ y == 0)
    prob = cp.Problem(cp.Minimize(0), C)
    try:
        prob.solve(solver=solver)
    except cp.error.SolverError:
        return 'solver_error', {'seconds': round(time.time() - t, 2)}
    st = 'refuted' if prob.status in INFEASIBLE else (
        'feasible' if prob.status in ('optimal', 'optimal_inaccurate') else prob.status)
    return st, {'seconds': round(time.time() - t, 2), 'matrix': N, 'moments': len(U),
                'equations': len(eq_rows)}


# ----------------------------------------------------------------------------- the richer wave

def rich_wave(n, cons, d, max_rounds=12, level2=False, log=print, deadline=None):
    cons = [canon(c) if c[0] in ('clause', 'xor') else c for c in cons]
    history = []
    for r in range(1, max_rounds + 1):
        st, new, info = algebra_rich(n, cons, d, deadline=deadline)
        kinds = {k: sum(c[0] == k for c in new) for k in ('clause', 'xor')}
        history.append({'round': r, 'engine': 'algebra', 'status': st, 'new': kinds, **info})
        log(f'  round {r} algebra(d={d}): {st}, +{kinds["clause"]} clauses '
            f'+{kinds["xor"]} parity eqs ({info.get("seconds")}s)')
        if st == 'refuted':
            return 'refuted_by_algebra', history, cons
        if st != 'closed':
            return st, history, cons
        cons = cons + new
        st, new2, info = geometry_rich(n, cons)
        history.append({'round': r, 'engine': 'geometry', 'status': st, 'new': len(new2), **info})
        log(f'  round {r} geometry(level 1): {st}, +{len(new2)} clauses ({info.get("seconds")}s, '
            f'{info.get("solves")} solves)')
        if st == 'refuted':
            return 'refuted_by_geometry', history, cons
        if st != 'feasible':
            return st, history, cons
        cons = cons + new2
        if level2:
            st2, info2 = level2_lift(n, cons)
            history.append({'round': r, 'engine': 'geometry2', 'status': st2, **info2})
            log(f'  round {r} geometry(level 2): {st2} ({info2.get("seconds")}s)')
            if st2 == 'refuted':
                return 'refuted_by_level2', history, cons
        if not new and not new2:
            return 'stuck', history, cons
    return 'max_rounds', history, cons
