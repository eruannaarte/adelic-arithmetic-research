"""Random 3-SAT with the richer shared language (engines2.py).

For each unsatisfiable instance: the algebra alone (lowest refuting degree), the level-1 lift
alone, the richer wave at algebra degree 3 (clauses <= 3 literals and parity equations <= 3
variables cross between the engines), and the level-2 lift alone where it is small enough.

Usage: run_rich.py <out.json> <seed> <n ...>    e.g. run_rich.py rich_s4.json 4 12 16 20 25 30 40
With seed 4 and n = 12 16 20 25 30 40 the instances are the same ones as run_all.py sat.
"""
import json
import sys
import time
import warnings
from pathlib import Path
from random import Random

warnings.filterwarnings('ignore')

import families as fam
from engines import pc_f2, sdp_lift
from engines2 import rich_wave, level2_lift

HERE = Path(__file__).resolve().parent


def main():
    out, seed, sizes = HERE / sys.argv[1], int(sys.argv[2]), [int(a) for a in sys.argv[3:]]
    rng = Random(seed)
    data = []
    for nv in sizes:
        n, cons = fam.random_3sat(nv, 5.0, rng)
        print(f'random 3-SAT n={nv} m={len(cons)} seed={seed}', flush=True)
        rec = {'n': n, 'm': len(cons), 'seed': seed, 'algebra_alone': []}
        for d in (3, 4, 5):
            st, _, info = pc_f2(n, cons, [], d, equivalences=False, deadline=time.time() + 900)
            rec['algebra_alone'].append({'d': d, 'status': st, **info})
            print(f'    algebra alone d={d}: {st}', flush=True)
            if st != 'closed':
                break
        st, _, info = sdp_lift(n, cons, [], probe=False)
        rec['level1_alone'] = st
        print(f'    level-1 lift alone: {st}', flush=True)
        t = time.time()
        res, hist, final = rich_wave(n, cons, 3, log=lambda s: print('  ' + s, flush=True),
                                     deadline=time.time() + 1800)
        rec['rich_wave_d3'] = {'result': res, 'rounds': max(h['round'] for h in hist),
                               'facts_added': len(final) - len(cons),
                               'seconds': round(time.time() - t, 1), 'history': hist}
        print(f'    rich wave d=3: {res} after {rec["rich_wave_d3"]["rounds"]} rounds, '
              f'{len(final) - len(cons)} facts, {time.time() - t:.0f}s', flush=True)
        if n <= 16:                      # n = 20 needed about 25 GB; see README
            st, info = level2_lift(n, cons)
            rec['level2_alone'] = {'status': st, **info}
            print(f'    level-2 lift alone: {st} {info}', flush=True)
        data.append(rec)
        out.write_text(json.dumps(data, indent=1))


if __name__ == '__main__':
    main()
