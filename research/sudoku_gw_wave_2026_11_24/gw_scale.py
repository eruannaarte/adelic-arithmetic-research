"""Scaling the GW lift: does one vector lift still force the solution on bigger Sudokus?

Same lift as gw_wave.py, written for any box size b (grid N = b*b: 9x9, 16x16, 25x25).
Generalized Sudoku is NP-complete as N grows, so a fixed relaxation like this one has to stop
forcing somewhere unless P = NP. This script looks for where.

Per puzzle it records:
  - backtracking (DFS + singles + fewest-candidates-first): guesses, time, uniqueness
  - the lift from the propagated grid: how many cells popped out, time
  - the forcing audit (uses the known answer only for evaluation): the most belief the lift can
    place on wrong claims; ~0 means the answer is forced
  - the LP control's forcing audit (same rules, no vectors)
  - if the lift did not force everything: the wave (fix what popped, propagate, re-lift,
    branch on the most confident claim) with its lift and branch counts
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from random import Random

import numpy as np
import scipy.sparse as sp
import cvxpy as cp

HERE = Path(__file__).resolve().parent
SURE = 0.99


class Grid:
    def __init__(self, b):
        self.b, self.N = b, b * b
        N, n = self.N, self.N * self.N
        rows = [[r * N + c for c in range(N)] for r in range(N)]
        cols = [[r * N + c for r in range(N)] for c in range(N)]
        boxes = [[(br + r) * N + bc + c for r in range(b) for c in range(b)]
                 for br in range(0, N, b) for bc in range(0, N, b)]
        self.units = rows + cols + boxes
        self.cells = n
        self.peers = [set().union(*(u for u in self.units if i in u)) - {i} for i in range(n)]
        self.digits = range(1, N + 1)

    # ------------------------------------------------------------ basics
    def parse(self, s):
        vals = s if isinstance(s, list) else [0 if ch in '.0' else int(ch, 36) for ch in s]
        return [set(self.digits) if v == 0 else {v} for v in vals]

    def propagate(self, doms):
        doms = [set(d) for d in doms]
        while True:
            queue = [i for i in range(self.cells) if len(doms[i]) == 1]
            seen = set()
            while queue:
                i = queue.pop()
                if i in seen:
                    continue
                seen.add(i)
                d = next(iter(doms[i]))
                for j in self.peers[i]:
                    if d in doms[j]:
                        doms[j].discard(d)
                        if not doms[j]:
                            return None
                        if len(doms[j]) == 1:
                            queue.append(j)
            changed = False
            for u in self.units:
                for d in self.digits:
                    places = [i for i in u if d in doms[i]]
                    if not places:
                        return None
                    if len(places) == 1 and len(doms[places[0]]) > 1:
                        doms[places[0]] = {d}
                        changed = True
            if not changed:
                return doms

    @staticmethod
    def solved(doms):
        return doms is not None and all(len(d) == 1 for d in doms)

    @staticmethod
    def values(doms):
        return [next(iter(d)) for d in doms]

    def backtrack(self, doms, stats, limit=2, budget=None, found=None):
        found = [] if found is None else found
        if budget is not None and stats['guesses'] > budget:
            stats['over_budget'] = True
            return found
        doms = self.propagate(doms)
        if doms is None:
            return found
        if self.solved(doms):
            found.append(self.values(doms))
            return found
        i = min((k for k in range(self.cells) if len(doms[k]) > 1), key=lambda k: len(doms[k]))
        for d in sorted(doms[i]):
            stats['guesses'] += 1
            nd = [set(x) for x in doms]
            nd[i] = {d}
            self.backtrack(nd, stats, limit, budget, found)
            if len(found) >= limit or stats.get('over_budget'):
                break
        return found

    # ------------------------------------------------------------ the lift
    def index(self, doms):
        cands = [(i, d) for i in range(self.cells) if len(doms[i]) > 1 for d in sorted(doms[i])]
        return cands, {c: k + 1 for k, c in enumerate(cands)}

    def rules(self, doms, idx):
        out = [[idx[(i, d)] for d in sorted(doms[i])] for i in range(self.cells) if len(doms[i]) > 1]
        for u in self.units:
            for d in self.digits:
                if any(doms[i] == {d} for i in u):
                    continue
                out.append([idx[(i, d)] for i in u if len(doms[i]) > 1 and d in doms[i]])
        return out

    def clashes(self, cands, idx):
        by_cell, by_digit = {}, {}
        for c in cands:
            by_cell.setdefault(c[0], []).append(c)
            by_digit.setdefault(c[1], []).append(c)
        pairs = set()
        for i, cs in by_cell.items():
            for a in range(len(cs)):
                for b2 in range(a + 1, len(cs)):
                    pairs.add((idx[cs[a]], idx[cs[b2]]))
        for d, cs in by_digit.items():
            pos = {c[0]: idx[c] for c in cs}
            for i, k in pos.items():
                for j in self.peers[i]:
                    if j in pos and j > i:
                        pairs.add((k, pos[j]))
        return sorted(pairs)

    def lift(self, doms, maximize=None, nonneg=True, eps=1e-5, max_iters=20000, checks=False):
        cands, idx = self.index(doms)
        n = len(cands) + 1
        rules = self.rules(doms, idx)
        if any(not r for r in rules):
            return {'status': 'infeasible', 'seconds': 0.0, 'n': n}
        rows, cols, vals, rhs = [], [], [], []
        r = 0

        def add(entries, value):
            nonlocal r
            for (a, b2), w in entries:
                rows.append(r); cols.append(a + b2 * n); vals.append(w)
            rhs.append(value); r += 1
        add([((0, 0), 1.0)], 1.0)
        for k in range(1, n):
            add([((k, k), 1.0), ((0, k), -1.0)], 0.0)
        for rule in rules:
            add([((0, k), 1.0) for k in rule], 1.0)
        for a, b2 in self.clashes(cands, idx):
            add([((a, b2), 1.0)], 0.0)
        A = sp.csr_matrix((vals, (rows, cols)), shape=(r, n * n))
        X = cp.Variable((n, n), PSD=True)
        cons = [A @ cp.vec(X, order='F') == np.array(rhs)]
        if nonneg:
            cons.append(X >= 0)
        obj = cp.Minimize(0)
        if maximize:
            obj = cp.Maximize(cp.sum(cp.hstack([X[0, idx[c]] for c in maximize if c in idx])))
        prob = cp.Problem(obj, cons)
        t = time.perf_counter()
        try:
            prob.solve(solver='SCS', eps_abs=eps, eps_rel=eps, max_iters=max_iters)
        except cp.error.SolverError as e:
            return {'status': f'solver_error: {e}', 'seconds': time.perf_counter() - t, 'n': n}
        out = {'status': prob.status, 'seconds': time.perf_counter() - t, 'n': n}
        if prob.status in ('optimal', 'optimal_inaccurate'):
            out['p'] = {c: float(X.value[0, idx[c]]) for c in cands}
            if maximize:
                out['value'] = float(prob.value)
            if checks:   # is the returned point really a feasible lift?
                Xv = (X.value + X.value.T) / 2
                out['min_eigenvalue'] = float(np.linalg.eigvalsh(Xv).min())
                out['min_entry'] = float(Xv.min())
                out['max_equality_residual'] = float(np.abs(A @ Xv.flatten(order='F') - np.array(rhs)).max())
                out['iterations'] = int(prob.solver_stats.num_iters or 0)
        return out

    def lp(self, doms, maximize=None):
        cands, idx = self.index(doms)
        rules = self.rules(doms, idx)
        if any(not r for r in rules):
            return {'status': 'infeasible'}
        x = cp.Variable(len(cands))
        cons = [x >= 0, x <= 1] + [cp.sum(x[[k - 1 for k in rule]]) == 1 for rule in rules]
        obj = cp.Minimize(0) if not maximize else cp.Maximize(
            cp.sum(x[[idx[c] - 1 for c in maximize if c in idx]]))
        prob = cp.Problem(obj, cons)
        prob.solve(solver='HIGHS')
        return {'status': prob.status, 'value': float(prob.value) if maximize else None}

    # ------------------------------------------------------------ the wave
    def wave(self, doms, st, max_lifts=60, depth=0, **lift_kw):
        doms = self.propagate(doms)
        if doms is None:
            return None
        while not self.solved(doms):
            if st['lifts'] >= max_lifts:
                st['gave_up'] = True
                return None
            st['lifts'] += 1
            res = self.lift(doms, **lift_kw)
            st['lift_seconds'] += res['seconds']
            p = res.get('p')
            if p is None:
                st['refuted_by_lift'] += 1
                return None
            sure = [c for c, v in p.items() if v > SURE]
            if sure:
                for (i, d) in sure:
                    if d not in doms[i]:
                        return None
                    doms[i] = {d}
                doms = self.propagate(doms)
                if doms is None:
                    return None
                continue
            (i, d) = max(p, key=p.get)
            st['branches'] += 1
            trial = [set(x) for x in doms]
            trial[i] = {d}
            out = self.wave(trial, st, max_lifts, depth + 1, **lift_kw)
            if out is not None or st['gave_up']:
                return out
            doms[i].discard(d)
            doms = self.propagate(doms)
            if doms is None:
                return None
        return doms

    # ------------------------------------------------------------ puzzles
    def random_solution(self, rng):
        """A pattern grid scrambled by the Sudoku symmetries (relabel, rows within bands,
        bands, columns within stacks, stacks, transpose). Every result is a valid grid."""
        b, N = self.b, self.N
        base = [[(b * (r % b) + r // b + c) % N for c in range(N)] for r in range(N)]
        label = list(range(1, N + 1)); rng.shuffle(label)
        def order():
            groups = list(range(b)); rng.shuffle(groups)
            out = []
            for g in groups:
                inner = list(range(b)); rng.shuffle(inner)
                out += [g * b + x for x in inner]
            return out
        ro, co = order(), order()
        g = [[label[base[r][c]] for c in co] for r in ro]
        if rng.random() < 0.5:
            g = [list(x) for x in zip(*g)]
        return [v for row in g for v in row]

    def make_puzzle(self, rng, budget, target=0):
        sol = self.random_solution(rng)
        g = list(sol)
        order = list(range(self.cells)); rng.shuffle(order)
        for i in order:
            if sum(v != 0 for v in g) <= target:
                break
            keep = g[i]; g[i] = 0
            st = {'guesses': 0}
            found = self.backtrack(self.parse(g), st, limit=2, budget=budget)
            if len(found) != 1 or st.get('over_budget'):
                g[i] = keep           # not provably unique within budget: keep the clue
        return g, sol


def run_one(G, name, puzzle, solution, audit=True, nonneg=True, wave=True, **lift_kw):
    rec = {'name': name, 'N': G.N, 'clues': sum(v != 0 for v in puzzle), 'puzzle': puzzle}
    st = {'guesses': 0}
    t = time.perf_counter()
    found = G.backtrack(G.parse(puzzle), st, limit=2, budget=2_000_000)
    rec['backtrack'] = {'guesses': st['guesses'], 'seconds': time.perf_counter() - t,
                        'solutions': len(found)}
    if len(found) != 1 or found[0] != solution:
        rec['skipped'] = 'not uniquely solvable'
        return rec
    start = G.propagate(G.parse(puzzle))
    if G.solved(start):
        rec['propagation_solves'] = True
        return rec
    rec['propagation_solves'] = False
    rec['free_cells'] = sum(len(d) > 1 for d in start)
    cands, _ = G.index(start)
    rec['candidates'] = len(cands)
    one = G.lift(start, nonneg=nonneg, **lift_kw)
    rec['lift'] = {k: v for k, v in one.items() if k != 'p'}
    if 'p' in one:
        p = one['p']
        popped = [c for c, v in p.items() if v > SURE]
        rec['lift']['popped_cells'] = len(popped)
        rec['lift']['popped_correct'] = sum(solution[i] == d for i, d in popped)
        rec['lift']['max_fractionality'] = max(min(v, 1 - v) for v in p.values())
    if audit:
        wrong = [c for c in cands if solution[c[0]] != c[1]]
        a = G.lift(start, maximize=wrong, nonneg=nonneg, **lift_kw)
        rec['audit_sdp_wrong_mass'] = a.get('value')
        rec['audit_sdp_status'] = a['status']
        rec['audit_sdp_seconds'] = a['seconds']
        rec['audit_lp_wrong_mass'] = G.lp(start, maximize=wrong)['value']
    forced = rec['lift'].get('popped_cells') == rec['free_cells']
    rec['one_lift_forces'] = bool(forced)
    if not forced and wave:
        w = {'lifts': 0, 'lift_seconds': 0.0, 'branches': 0, 'refuted_by_lift': 0, 'gave_up': False}
        t = time.perf_counter()
        out = G.wave(G.parse(puzzle), w, nonneg=nonneg, **lift_kw)
        w['seconds'] = time.perf_counter() - t
        w['solved'] = out is not None and G.values(out) == solution
        rec['wave'] = w
    return rec


def sweep(b, count, seed, budget, out_name, audit=True, nonneg=True, keep_easy=False):
    G = Grid(b)
    rng = Random(seed)
    path = HERE / out_name
    results = json.loads(path.read_text()) if path.exists() else []
    done = {r['name'] for r in results}
    k = 0
    while k < count:
        name = f'{G.N}x{G.N}-{seed}-{k + 1}'
        t = time.perf_counter()
        puzzle, sol = G.make_puzzle(rng, budget)
        gen_s = time.perf_counter() - t
        k += 1
        if name in done:
            continue
        rec = run_one(G, name, puzzle, sol, audit=audit, nonneg=nonneg)
        rec['generation_seconds'] = gen_s
        results.append(rec)
        path.write_text(json.dumps(results, indent=1))
        if rec.get('propagation_solves'):
            print(f"{name} clues={rec['clues']} propagation solves", flush=True)
            continue
        L = rec.get('lift', {})
        print(f"{name} clues={rec['clues']} free={rec.get('free_cells')} cands={rec.get('candidates')} "
              f"bt={rec['backtrack']['guesses']}g/{rec['backtrack']['seconds']*1000:.0f}ms "
              f"lift={L.get('status')} {L.get('seconds', 0):.1f}s popped={L.get('popped_cells')}/{rec.get('free_cells')} "
              f"wrong_sdp={rec.get('audit_sdp_wrong_mass')} wrong_lp={rec.get('audit_lp_wrong_mass')} "
              f"forces={rec.get('one_lift_forces')} wave={rec.get('wave')}", flush=True)


def ladder_one(b, seed, target, budget, max_iters, out_name):
    """One puzzle at a given clue count; one lift (no audit, no wave), high iteration budget."""
    G = Grid(b)
    rng = Random(seed)
    t = time.perf_counter()
    puzzle, sol = G.make_puzzle(rng, budget, target)
    gen = time.perf_counter() - t
    name = f'{G.N}x{G.N}-seed{seed}-target{target}'
    rec = run_one(G, name, puzzle, sol, audit=False, wave=False, max_iters=max_iters)
    rec['generation_seconds'] = gen
    rec['solution'] = sol
    rec['max_iters'] = max_iters
    (HERE / out_name).write_text(json.dumps(rec, indent=1))
    L = rec.get('lift', {})
    print(f"{name} clues={rec['clues']} free={rec.get('free_cells')} cands={rec.get('candidates')} "
          f"bt={rec['backtrack']['guesses']}g/{rec['backtrack']['seconds']*1000:.0f}ms "
          f"prop_solves={rec.get('propagation_solves')} lift={L.get('status')} {L.get('seconds', 0):.0f}s "
          f"popped={L.get('popped_cells')}/{rec.get('free_cells')} correct={L.get('popped_correct')} "
          f"maxfrac={L.get('max_fractionality')}", flush=True)


if __name__ == '__main__' and sys.argv[1] == 'ladder':
    b, seed, target, budget, max_iters = (int(x) for x in sys.argv[2:7])
    ladder_one(b, seed, target, budget, max_iters, sys.argv[7])
elif __name__ == '__main__':
    b, count, seed, budget = (int(x) for x in sys.argv[1:5])
    out = sys.argv[5]
    flags = set(sys.argv[6:])
    sweep(b, count, seed, budget, out, audit='noaudit' not in flags, nonneg='nononneg' not in flags)
