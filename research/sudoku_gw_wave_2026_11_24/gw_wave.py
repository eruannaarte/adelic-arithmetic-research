"""Goemans-Williamson-style "wave" on Sudoku: lift to vectors, solve, project down, repeat.

LIFT    Every candidate (cell, digit) gets a vector v_{i,d}; v_0 is the "true" direction.
        The Gram matrix X = [v . v] must be positive semidefinite (an SDP), with
          |v_{i,d}|^2 = v_0 . v_{i,d}          (each claim is 0/1 "in spirit")
          sum_d v_0 . v_{i,d} = 1              (one digit per cell)
          sum_{i in unit} v_0 . v_{i,d} = 1    (each digit once per row/column/box)
          v_{i,d} . v_{i,d'} = 0, v_{i,d} . v_{j,d} = 0 for peers (no clashes)
          lifted copies of the two sum rules against every vector, and X >= 0
        p_{i,d} = v_0 . v_{i,d} is the lift's "belief" that cell i holds digit d.
DOWN    (a) GW hyperplane rounding: a random direction r, each cell takes argmax_d v_{i,d} . r
        (b) the wave: fix every claim the lift is sure of (p > 0.99), propagate the
            consequences in the ordinary 81-cell grid, and lift again. If nothing pops out,
            branch on the most confident claim.
CONTROLS
        - plain constraint propagation (naked + hidden singles), no guessing
        - the same relaxation WITHOUT vectors: a linear program (LP) over the p's only
        - an ordinary backtracking solver with propagation (the practical baseline)
Ground truth comes from the backtracking solver, which also checks each puzzle is unique.
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
ROWS = [[r * 9 + c for c in range(9)] for r in range(9)]
COLS = [[r * 9 + c for r in range(9)] for c in range(9)]
BOXES = [[(br + r) * 9 + bc + c for r in range(3) for c in range(3)]
         for br in (0, 3, 6) for bc in (0, 3, 6)]
UNITS = ROWS + COLS + BOXES
PEERS = [set().union(*(u for u in UNITS if i in u)) - {i} for i in range(81)]
SURE = 0.99


# ---------------------------------------------------------------- grid basics
def parse(s: str) -> list[set[int]]:
    s = s.strip().replace('0', '.')
    assert len(s) == 81, s
    doms = [set(range(1, 10)) for _ in range(81)]
    for i, ch in enumerate(s):
        if ch != '.':
            doms[i] = {int(ch)}
    return doms


def eliminate_givens(doms):
    """Remove each fixed digit from its peers (one pass, repeated until stable).

    This is the cheapest possible step and is applied before every lift."""
    doms = [set(d) for d in doms]
    changed = True
    while changed:
        changed = False
        for i in range(81):
            if len(doms[i]) == 1:
                d = next(iter(doms[i]))
                for j in PEERS[i]:
                    if d in doms[j]:
                        doms[j].discard(d)
                        changed = True
                        if not doms[j]:
                            return None
    return doms


def propagate(doms):
    """Naked singles + hidden singles to a fixed point. None on contradiction."""
    doms = [set(d) for d in doms]
    while True:
        doms = eliminate_givens(doms)
        if doms is None:
            return None
        changed = False
        for u in UNITS:
            for d in range(1, 10):
                places = [i for i in u if d in doms[i]]
                if not places:
                    return None
                if len(places) == 1 and len(doms[places[0]]) > 1:
                    doms[places[0]] = {d}
                    changed = True
        if not changed:
            return doms


def solved(doms):
    return doms is not None and all(len(d) == 1 for d in doms)


def grid_of(doms):
    return ''.join(str(next(iter(d))) for d in doms)


# ------------------------------------------------- classical backtracking baseline
def backtrack(doms, stats, limit=2, found=None):
    """DFS + propagation + fewest-candidates-first. Counts guesses in stats['guesses']."""
    found = [] if found is None else found
    doms = propagate(doms)
    if doms is None:
        return found
    if solved(doms):
        found.append(grid_of(doms))
        return found
    i = min((k for k in range(81) if len(doms[k]) > 1), key=lambda k: len(doms[k]))
    for d in sorted(doms[i]):
        stats['guesses'] += 1
        nd = [set(x) for x in doms]
        nd[i] = {d}
        backtrack(nd, stats, limit, found)
        if len(found) >= limit:
            break
    return found


# ------------------------------------------------------------------ the lift
def build_index(doms):
    cands = [(i, d) for i in range(81) if len(doms[i]) > 1 for d in sorted(doms[i])]
    idx = {c: k + 1 for k, c in enumerate(cands)}          # 0 is v_0
    return cands, idx


def linear_rules(doms, idx):
    """The two 'sum = 1' families, over free candidates only (fixed cells are folded in)."""
    rules = []
    for i in range(81):
        if len(doms[i]) > 1:
            rules.append([idx[(i, d)] for d in sorted(doms[i])])
    for u in UNITS:
        for d in range(1, 10):
            if any(doms[i] == {d} for i in u):
                continue
            ks = [idx[(i, d)] for i in u if len(doms[i]) > 1 and d in doms[i]]
            rules.append(ks)
    return rules


def clash_pairs(cands, idx):
    pairs = []
    for a, (i, d) in enumerate(cands):
        for b in range(a + 1, len(cands)):
            j, e = cands[b]
            if (i == j and d != e) or (d == e and j in PEERS[i]):
                pairs.append((a + 1, b + 1))
    return pairs


def lift(doms, lifted=False, eps=1e-5, max_iters=20000, maximize=None):
    """Solve the vector (SDP) relaxation. Returns (status, p dict, X matrix, seconds)."""
    cands, idx = build_index(doms)
    n = len(cands) + 1
    rules = linear_rules(doms, idx)
    if any(len(r) == 0 for r in rules):
        return 'infeasible', None, None, 0.0
    rows, cols, vals, rhs = [], [], [], []
    r = 0

    def add(entries, value):
        nonlocal r
        for (a, b), w in entries:
            rows.append(r); cols.append(a + b * n); vals.append(w)   # column-major vec
        rhs.append(value); r += 1

    add([((0, 0), 1.0)], 1.0)
    for k in range(1, n):
        add([((k, k), 1.0), ((0, k), -1.0)], 0.0)
    for rule in rules:
        add([((0, k), 1.0) for k in rule], 1.0)
        if lifted:
            for m in range(1, n):
                add([((k, m), 1.0) for k in rule] + [((0, m), -1.0)], 0.0)
    for a, b in clash_pairs(cands, idx):
        add([((a, b), 1.0)], 0.0)
    A = sp.csr_matrix((vals, (rows, cols)), shape=(r, n * n))
    X = cp.Variable((n, n), PSD=True)
    obj = cp.Minimize(0)
    if maximize:
        obj = cp.Maximize(cp.sum(cp.hstack([X[0, idx[c]] for c in maximize if c in idx])))
    prob = cp.Problem(obj, [A @ cp.vec(X, order='F') == np.array(rhs), X >= 0])
    t = time.perf_counter()
    try:
        prob.solve(solver='SCS', eps_abs=eps, eps_rel=eps, max_iters=max_iters)
    except cp.error.SolverError:
        return 'solver_error', None, None, time.perf_counter() - t
    sec = time.perf_counter() - t
    if prob.status not in ('optimal', 'optimal_inaccurate'):
        return prob.status, None, None, sec
    Xv = (X.value + X.value.T) / 2
    p = {c: float(Xv[0, idx[c]]) for c in cands}
    if maximize:
        return prob.status, p, float(prob.value), sec
    return prob.status, p, (cands, Xv), sec


def lp(doms, maximize=None):
    """Same linear rules, beliefs only, no vectors: does the lift add anything?"""
    cands, idx = build_index(doms)
    rules = linear_rules(doms, idx)
    if any(len(r) == 0 for r in rules):
        return 'infeasible', None
    x = cp.Variable(len(cands))
    cons = [x >= 0, x <= 1] + [cp.sum(x[[k - 1 for k in rule]]) == 1 for rule in rules]
    obj = cp.Minimize(0)
    if maximize:
        obj = cp.Maximize(cp.sum(x[[idx[c] - 1 for c in maximize if c in idx]]))
    prob = cp.Problem(obj, cons)
    if maximize:
        prob.solve(solver='HIGHS')
    else:   # interior point without crossover: a central point of the LP set, not a corner
        prob.solve(solver='HIGHS', highs_options={'solver': 'ipm', 'run_crossover': 'off'})
    if prob.status not in ('optimal', 'optimal_inaccurate'):
        return prob.status, None
    p = {c: float(x.value[idx[c] - 1]) for c in cands}
    return ('optimal', p, float(prob.value)) if maximize else ('optimal', p)


def popped(p):
    return {c for c, v in p.items() if v > SURE}


def fractionality(p):
    return max(min(v, 1 - v) for v in p.values()) if p else 0.0


def forcing_audit(doms, truth):
    """AUDIT ONLY (uses the known answer): the largest total belief the relaxation can put on
    WRONG claims. 0 means the relaxation's feasible set is exactly the solution: the answer is
    forced, not a lucky landing. Positive means room for fractional / wrong beliefs."""
    cands, _ = build_index(doms)
    wrong = [c for c in cands if int(truth[c[0]]) != c[1]]
    out = {}
    r = lp(doms, maximize=wrong)
    out['lp_max_wrong_mass'] = r[2] if len(r) == 3 else None
    st, _, val, sec = lift(doms, maximize=wrong)
    out['sdp_max_wrong_mass'] = val if isinstance(val, float) else None
    out['sdp_audit_status'] = st
    out['sdp_audit_seconds'] = sec
    return out


# ------------------------------------------------------------- project down
def hyperplane_rounding(doms, lifted_X, truth, trials=200, seed=0):
    """GW rounding. Each claim becomes a unit vector u = 2 v_{i,d} - v_0 (u = +v_0 means
    "true", -v_0 means "false"). A random hyperplane r splits the sphere; a claim counts as true
    on the side where v_0 falls. Each free cell takes its claim deepest on that side."""
    cands, X = lifted_X
    w, V = np.linalg.eigh(X)
    V = V[:, w > 1e-9] * np.sqrt(w[w > 1e-9])
    V = np.vstack([V[:1], 2 * V[1:] - V[:1]])
    rng = np.random.default_rng(seed)
    by_cell = {}
    for k, (i, d) in enumerate(cands):
        by_cell.setdefault(i, []).append((d, k + 1))
    free = sorted(by_cell)
    best = None
    accs = []
    for _ in range(trials):
        rvec = rng.standard_normal(V.shape[1])
        proj = (V @ rvec) * np.sign(V[0] @ rvec)
        g = [next(iter(doms[i])) if len(doms[i]) == 1 else 0 for i in range(81)]
        for i in free:
            g[i] = max(by_cell[i], key=lambda dk: proj[dk[1]])[0]
        clashes = sum(1 for i in range(81) for j in PEERS[i] if j > i and g[i] == g[j])
        acc = sum(g[i] == int(truth[i]) for i in free) / len(free)
        accs.append(acc)
        if best is None or clashes < best[0]:
            best = (clashes, acc)
    return {'trials': trials, 'mean_cell_accuracy': float(np.mean(accs)),
            'best_clashes': best[0], 'accuracy_of_fewest_clash_draw': best[1],
            'exact_solutions_drawn': int(sum(a == 1.0 for a in accs))}


def argmax_marginals(doms, p, truth):
    by_cell = {}
    for (i, d), v in p.items():
        by_cell.setdefault(i, []).append((v, d))
    free = sorted(by_cell)
    return sum(max(by_cell[i])[1] == int(truth[i]) for i in free) / len(free)


# ---------------------------------------------------------------- the wave
def wave(doms, stats, use='sdp', depth=0, max_lifts=120):
    """Lift, fix whatever popped out, propagate, lift again; branch only when stuck."""
    doms = propagate(doms)
    if doms is None:
        return None
    while not solved(doms):
        if stats['lifts'] >= max_lifts:
            stats['gave_up'] = True
            return None
        stats['lifts'] += 1
        if use == 'sdp':
            status, p, _, sec = lift(doms)
            stats['lift_seconds'] += sec
        else:
            t = time.perf_counter()
            status, p = lp(doms)
            stats['lift_seconds'] += time.perf_counter() - t
        if p is None:
            stats['refuted_by_lift'] += 1
            return None
        sure = popped(p)
        if sure:
            stats['popped_claims'] += len(sure)
            for (i, d) in sure:
                if d not in doms[i]:
                    return None
                doms[i] = {d}
            doms = propagate(doms)
            if doms is None:
                stats['popped_contradictions'] += 1
                return None
            continue
        (i, d) = max(p, key=p.get)
        stats['branches'] += 1
        stats['max_depth'] = max(stats['max_depth'], depth + 1)
        trial = [set(x) for x in doms]
        trial[i] = {d}
        res = wave(trial, stats, use, depth + 1, max_lifts)
        if res is not None:
            return res
        doms[i].discard(d)
        doms = propagate(doms)
        if doms is None:
            return None
    return doms


def new_stats():
    return {'lifts': 0, 'lift_seconds': 0.0, 'popped_claims': 0, 'branches': 0,
            'max_depth': 0, 'refuted_by_lift': 0, 'popped_contradictions': 0, 'gave_up': False}


# ------------------------------------------------------------ puzzle set
def random_solution(rng):
    doms = [set(range(1, 10)) for _ in range(81)]

    def fill(doms):
        doms = propagate(doms)
        if doms is None:
            return None
        if solved(doms):
            return doms
        i = min((k for k in range(81) if len(doms[k]) > 1), key=lambda k: len(doms[k]))
        opts = sorted(doms[i]); rng.shuffle(opts)
        for d in opts:
            nd = [set(x) for x in doms]; nd[i] = {d}
            out = fill(nd)
            if out is not None:
                return out
        return None
    return grid_of(fill(doms))


def make_puzzle(rng, target_clues):
    sol = random_solution(rng)
    g = list(sol)
    order = list(range(81)); rng.shuffle(order)
    for i in order:
        if sum(ch != '.' for ch in g) <= target_clues:
            break
        keep = g[i]; g[i] = '.'
        if len(backtrack(parse(''.join(g)), {'guesses': 0}, limit=2)) != 1:
            g[i] = keep
    return ''.join(g), sol


def puzzle_set():
    rng = Random(20261124)
    out = []
    for clues, label, count in ((36, 'generated-36', 3), (30, 'generated-30', 3), (24, 'generated-min', 4)):
        for k in range(count):
            pz, _ = make_puzzle(rng, clues)
            out.append({'name': f'{label}-{k + 1}', 'puzzle': pz})
    hardest = (HERE.parent / 'sudoku_intuition_eth_2026_10_27' / 'hardest.txt').read_text().split()
    for k, pz in enumerate(hardest):
        out.append({'name': f'norvig-hardest-{k + 1}', 'puzzle': pz})
    famous = {
        'inkala-2012': '8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..',
        'easter-monster': '1.......2.9.4...5...6...7...5.9.3.......7.......85..4.7.....6...3...9.8...2.....1',
        'norvig-grid2': '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......',
    }
    out += [{'name': k, 'puzzle': v} for k, v in famous.items()]
    return out


# ------------------------------------------------------------------ driver
def run_one(entry):
    pz = entry['puzzle']
    rec = {'name': entry['name'], 'puzzle': pz, 'clues': sum(ch not in '.0' for ch in pz)}
    st = {'guesses': 0}
    t = time.perf_counter()
    sols = backtrack(parse(pz), st, limit=2)
    rec['backtrack'] = {'solutions_found': len(sols), 'guesses': st['guesses'],
                        'seconds': time.perf_counter() - t}
    if len(sols) != 1:
        rec['skipped'] = 'not uniquely solvable'
        return rec
    truth = sols[0]
    rec['propagation_only_solves'] = solved(propagate(parse(pz)))

    start = propagate(parse(pz))          # cheap singles first; lifts start from here
    if solved(start):
        rec['note'] = 'propagation alone solves it; no lift needed'
        return rec
    rec['free_cells'] = sum(len(d) > 1 for d in start)
    rec['candidates'] = sum(len(d) for d in start if len(d) > 1)

    status, p_lp = lp(start)
    rec['lp_one_shot'] = {'status': status,
                          'popped': len(popped(p_lp)) if p_lp else None,
                          'max_fractionality': fractionality(p_lp) if p_lp else None,
                          'argmax_accuracy': argmax_marginals(start, p_lp, truth) if p_lp else None}

    status, p, lifted_X, sec = lift(start)
    one = {'status': status, 'seconds': sec}
    if p:
        sure = popped(p)
        one.update({'popped': len(sure),
                    'popped_correct': sum(int(truth[i]) == d for i, d in sure),
                    'free_cells': rec['free_cells'],
                    'max_fractionality': fractionality(p),
                    'argmax_accuracy': argmax_marginals(start, p, truth),
                    'rounding': hyperplane_rounding(start, lifted_X, truth)})
    rec['sdp_one_shot'] = one
    rec['forcing_audit'] = forcing_audit(start, truth)

    for use in ('sdp', 'lp'):
        s = new_stats(); t = time.perf_counter()
        res = wave(parse(pz), s, use=use)
        s['seconds'] = time.perf_counter() - t
        s['solved'] = res is not None and grid_of(res) == truth
        rec[f'{use}_wave'] = s
    return rec


def main():
    only = sys.argv[1:]
    entries = [e for e in puzzle_set() if not only or e['name'] in only]
    out_path = HERE / 'results.json'
    results = []
    for e in entries:
        rec = run_one(e)
        results.append(rec)
        sw, lw = rec.get('sdp_wave', {}), rec.get('lp_wave', {})
        print(f"{rec['name']:20s} clues={rec['clues']:2d} bt_guesses={rec['backtrack']['guesses']:4d} "
              f"prop={rec.get('propagation_only_solves')} "
              f"sdp1:{rec.get('sdp_one_shot', {}).get('popped')}/{rec.get('free_cells')} "
              f"sdp_wave lifts={sw.get('lifts')} br={sw.get('branches')} ok={sw.get('solved')} "
              f"{sw.get('seconds', 0):.1f}s | lp_wave lifts={lw.get('lifts')} br={lw.get('branches')} "
              f"ok={lw.get('solved')}", flush=True)
        out_path.write_text(json.dumps(results, indent=1))
    return results


if __name__ == '__main__':
    main()
