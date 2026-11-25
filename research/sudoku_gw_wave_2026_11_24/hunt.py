"""Hunt for a Sudoku where one vector lift does NOT force the answer.

Random clue removal rarely gives truly hard puzzles, so we BREED them. A hill-climber keeps a
fixed solution grid and mutates the clue set:
  - move one clue to another cell (with that cell's solution digit), or add/remove one clue
  - keep only puzzles that are still uniquely solvable
  - drop clues that became redundant (keep the puzzle minimal)
and accepts a mutation when the puzzle gets "harder" by a cheap score.

Two cheap scores, two kinds of climber:
  guesses  backtracking guesses needed to prove the puzzle unique (hard for search)
  lp       the LP control's forcing gap: most belief the LP can put on wrong claims
           (hard for a relaxation that is weaker than the lift)
Each climber saves its hardest puzzles. evaluate.py then runs the real (slow) lift on them.

Usage: hunt.py <kind: guesses|lp> <seed> <seconds> <out.json> [start: easter|inkala]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from random import Random

import cvxpy as cp

from gw_scale import Grid

HERE = Path(__file__).resolve().parent
G = Grid(3)


def unique_and_guesses(clues, budget=200_000):
    st = {'guesses': 0}
    found = G.backtrack(G.parse(clues), st, limit=2, budget=budget)
    if st.get('over_budget'):
        return False, st['guesses']
    return len(found) == 1, st['guesses']


def lp_gap(clues, sol):
    doms = G.propagate(G.parse(clues))
    if doms is None or G.solved(doms):
        return 0.0
    cands, idx = G.index(doms)
    rules = G.rules(doms, idx)
    wrong = [c for c in cands if sol[c[0]] != c[1]]
    x = cp.Variable(len(cands))
    cons = [x >= 0, x <= 1] + [cp.sum(x[[k - 1 for k in r]]) == 1 for r in rules]
    prob = cp.Problem(cp.Maximize(cp.sum(x[[idx[c] - 1 for c in wrong]])), cons)
    prob.solve(solver='HIGHS')
    return float(prob.value)


def minimalize(clues, rng):
    order = [i for i in range(G.cells) if clues[i]]
    rng.shuffle(order)
    for i in order:
        keep = clues[i]; clues[i] = 0
        ok, _ = unique_and_guesses(clues)
        if not ok:
            clues[i] = keep
    return clues


def score(kind, clues, sol):
    ok, g = unique_and_guesses(clues)
    if not ok:
        return None
    if G.solved(G.propagate(G.parse(clues))):
        return (0.0, g)
    if kind == 'guesses':
        return (float(g), g)
    return (lp_gap(clues, sol) + g / 1e6, g)     # tiny tie-break by guesses


FAMOUS = {
    'easter': '1.......2.9.4...5...6...7...5.9.3.......7.......85..4.7.....6...3...9.8...2.....1',
    'inkala': '8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..',
}


def climb(kind, seed, seconds, out_name, start=None):
    rng = Random(seed)
    if start:
        cur = [0 if ch == '.' else int(ch, 16) for ch in FAMOUS[start]]
        sol = G.backtrack(G.parse(cur), {'guesses': 0}, limit=1)[0]
    else:
        sol = G.random_solution(rng)
        cur = minimalize(list(sol), rng)
    cur_s = score(kind, cur, sol)
    best = []
    t0 = time.time()
    steps = accepted = 0
    while time.time() - t0 < seconds:
        steps += 1
        cand = list(cur)
        filled = [i for i in range(G.cells) if cand[i]]
        empty = [i for i in range(G.cells) if not cand[i]]
        r = rng.random()
        if r < 0.6:                       # move a clue
            i, j = rng.choice(filled), rng.choice(empty)
            cand[i] = 0; cand[j] = sol[j]
        elif r < 0.8:                     # add a clue, then let minimalize drop others
            j = rng.choice(empty); cand[j] = sol[j]
        else:                             # move two clues
            for _ in range(2):
                filled = [i for i in range(G.cells) if cand[i]]
                empty = [i for i in range(G.cells) if not cand[i]]
                i, j = rng.choice(filled), rng.choice(empty)
                cand[i] = 0; cand[j] = sol[j]
        ok, _ = unique_and_guesses(cand)
        if not ok:
            continue
        cand = minimalize(cand, rng)
        s = score(kind, cand, sol)
        if s is None:
            continue
        # accept improvements, and sideways/slightly worse moves now and then (escape plateaus)
        if s[0] >= cur_s[0] or rng.random() < 0.05:
            cur, cur_s = cand, s
            accepted += 1
            key = ''.join('.' if v == 0 else format(v, 'x') for v in cur)
            if s[0] > 0 and key not in {b['puzzle'] for b in best}:
                best.append({'puzzle': ''.join('.' if v == 0 else format(v, 'x') for v in cur),
                             'solution': ''.join(format(v, 'x') for v in sol), 'score': s[0],
                             'guesses': s[1], 'clues': sum(v != 0 for v in cur), 'kind': kind,
                             'seed': seed, 'found_at_s': round(time.time() - t0, 1)})
                best.sort(key=lambda b: -b['score'])
                del best[25:]
                (HERE / out_name).write_text(json.dumps(best, indent=1))
    print(f"{kind} seed={seed} steps={steps} accepted={accepted} best={best[0]['score'] if best else None} "
          f"guesses={best[0]['guesses'] if best else None}", flush=True)


if __name__ == '__main__':
    if len(sys.argv) > 5 and sys.argv[5].startswith('latin'):
        from latin import Latin
        G = Latin(int(sys.argv[5][5:]))
        sys.argv = sys.argv[:5]
    climb(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4],
          sys.argv[5] if len(sys.argv) > 5 else None)
