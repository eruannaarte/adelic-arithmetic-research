"""Run the real lift on bred puzzles and look for a genuine failure to force.

For each puzzle: one lift (beliefs), the forcing audit (most belief on wrong claims), the LP
audit, and feasibility checks of the returned matrix. A puzzle counts as a FAILURE only if
  - the lift converged (status 'optimal') and its matrix passes the checks, and
  - not every empty cell popped out, and the audit's wrong mass is clearly positive (> 0.01).
Suspected failures are re-solved at 100x tighter tolerance before being reported.

Usage: evaluate.py <shard> <nshards> <top_per_file> <out.json> <in1.json> [in2.json ...]
"""
import json
import sys
import time
from pathlib import Path

from gw_scale import Grid

HERE = Path(__file__).resolve().parent
G = Grid(3)


def evaluate(pz, sol, max_iters=100000):
    rec = {'puzzle': pz, 'solution': sol}
    clues = [0 if ch in '.0' else int(ch, 16) for ch in pz]
    solv = [int(ch, 16) for ch in sol]
    st = {'guesses': 0}
    t = time.perf_counter()
    found = G.backtrack(G.parse(clues), st, limit=2)
    rec['backtrack'] = {'guesses': st['guesses'], 'ms': 1000 * (time.perf_counter() - t),
                        'solutions': len(found)}
    start = G.propagate(G.parse(clues))
    if G.solved(start):
        rec['propagation_solves'] = True
        return rec
    free = sum(len(d) > 1 for d in start)
    cands, _ = G.index(start)
    rec.update(free_cells=free, candidates=len(cands))
    one = G.lift(start, max_iters=max_iters, checks=True)
    p = one.pop('p', None)
    rec['lift'] = one
    if p:
        popped = [c for c, v in p.items() if v > 0.99]
        one['popped'] = len(popped)
        one['popped_correct'] = sum(solv[i] == d for i, d in popped)
        one['max_fractionality'] = max(min(v, 1 - v) for v in p.values())
    wrong = [c for c in cands if solv[c[0]] != c[1]]
    a = G.lift(start, maximize=wrong, max_iters=max_iters, checks=True)
    a.pop('p', None)
    rec['audit'] = a
    rec['lp_wrong_mass'] = G.lp(start, maximize=wrong)['value']
    forced = one.get('popped') == free
    suspect = (not forced) or (a.get('value') or 0) > 0.01
    rec['forced'] = forced and not suspect
    if suspect:
        tight = G.lift(start, maximize=wrong, eps=1e-7, max_iters=400000, checks=True)
        tight.pop('p', None)
        rec['audit_tight'] = tight
        rec['genuine_failure'] = (tight['status'] == 'optimal' and (tight.get('value') or 0) > 0.01
                                  and tight.get('min_eigenvalue', -1) > -1e-5
                                  and tight.get('max_equality_residual', 1) < 1e-5
                                  and tight.get('min_entry', -1) > -1e-5)
    return rec


def main():
    shard, nshards, top = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    out = HERE / sys.argv[4]
    pool, seen = [], set()
    for f in sys.argv[5:]:
        items = json.loads(Path(f).read_text())
        items.sort(key=lambda b: (-b['score'], -b['guesses']))
        k = 0
        for b in items:
            if b['puzzle'] in seen:
                continue
            seen.add(b['puzzle'])
            pool.append(dict(b, source=Path(f).name))
            k += 1
            if k >= top:
                break
    mine = pool[shard::nshards]
    results = json.loads(out.read_text()) if out.exists() else []
    done = {r['puzzle'] for r in results}
    for b in mine:
        if b['puzzle'] in done:
            continue
        r = evaluate(b['puzzle'], b['solution'])
        r.update(source=b['source'], kind=b['kind'], score=b['score'], clues=b['clues'])
        results.append(r)
        out.write_text(json.dumps(results, indent=1))
        L, A = r.get('lift', {}), r.get('audit', {})
        print(f"{r['source']:16s} clues={r['clues']} bt={r['backtrack']['guesses']}g "
              f"prop={r.get('propagation_solves', False)} popped={L.get('popped')}/{r.get('free_cells')} "
              f"lift={L.get('status')} {L.get('seconds', 0):.0f}s it={L.get('iterations')} "
              f"wrong_sdp={A.get('value')} wrong_lp={r.get('lp_wrong_mass')} forced={r.get('forced')} "
              f"GENUINE_FAILURE={r.get('genuine_failure')}", flush=True)


if __name__ == '__main__':
    main()
