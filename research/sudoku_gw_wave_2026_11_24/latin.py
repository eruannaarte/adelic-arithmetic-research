"""Hunt for a failure of the one-lift result on Latin squares (Sudoku without the boxes).

Completing a partial Latin square is NP-complete (Colbourn 1984). With only row and column rules
the lift has fewer constraints to grip, so this is a better place to look for a puzzle where
one lift does NOT force the unique answer.

Puzzles: a random Latin square (randomized backtracking), then clues removed at random while the
completion stays unique (a minimal "critical" partial square). Each puzzle gets the lift, the
forcing audit, the LP audit and matrix checks (same code as evaluate.py).

Usage: latin.py <n> <count> <seed> <out.json>
"""
import json
import sys
import time
from pathlib import Path
from random import Random

from gw_scale import Grid
import evaluate as ev

HERE = Path(__file__).resolve().parent


class Latin(Grid):
    def __init__(self, n):
        self.b, self.N = None, n
        rows = [[r * n + c for c in range(n)] for r in range(n)]
        cols = [[r * n + c for r in range(n)] for c in range(n)]
        self.units = rows + cols
        self.cells = n * n
        self.peers = [set().union(*(u for u in self.units if i in u)) - {i} for i in range(n * n)]
        self.digits = range(1, n + 1)

    def random_solution(self, rng):
        def fill(doms):
            doms = self.propagate(doms)
            if doms is None:
                return None
            if self.solved(doms):
                return doms
            i = min((k for k in range(self.cells) if len(doms[k]) > 1), key=lambda k: len(doms[k]))
            opts = sorted(doms[i]); rng.shuffle(opts)
            for d in opts:
                nd = [set(x) for x in doms]; nd[i] = {d}
                out = fill(nd)
                if out is not None:
                    return out
            return None
        return self.values(fill([set(self.digits) for _ in range(self.cells)]))


def main():
    n, count, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    out = HERE / sys.argv[4]
    L = Latin(n)
    ev.G = L                      # evaluate() uses the module-level grid
    rng = Random(seed)
    results = json.loads(out.read_text()) if out.exists() else []
    for k in range(len(results), count):
        t = time.perf_counter()
        clues, sol = L.make_puzzle(rng, budget=20000)
        gen = time.perf_counter() - t
        enc = lambda vals: ''.join('.' if v == 0 else format(v, 'x') for v in vals)
        r = ev.evaluate(enc(clues), enc(sol))
        r.update(n=n, clues=sum(v != 0 for v in clues), generation_seconds=gen, index=k + 1)
        results.append(r)
        out.write_text(json.dumps(results, indent=1))
        Lr, A = r.get('lift', {}), r.get('audit', {})
        print(f"latin{n} #{k + 1} clues={r['clues']} bt={r['backtrack']['guesses']}g "
              f"prop={r.get('propagation_solves', False)} popped={Lr.get('popped')}/{r.get('free_cells')} "
              f"lift={Lr.get('status')} {Lr.get('seconds', 0):.0f}s it={Lr.get('iterations')} "
              f"wrong_sdp={A.get('value')} wrong_lp={r.get('lp_wrong_mass')} forced={r.get('forced')} "
              f"GENUINE_FAILURE={r.get('genuine_failure')}", flush=True)


if __name__ == '__main__':
    main()
