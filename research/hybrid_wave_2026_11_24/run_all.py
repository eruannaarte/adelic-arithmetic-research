"""Run the algebra engine, the geometry engine and the wave on every test family.

Usage: run_all.py <section ...>   sections: pigeons parity coupled sudoku sat   (default: all)
Results are appended to results.json (one record per run); progress goes to stdout.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from random import Random

from engines import pc_f2, sdp_lift, wave
import families as fam

HERE = Path(__file__).resolve().parent
OUT = HERE / f'results_{"_".join(sys.argv[1:]) or "all"}.json'   # one file per stream
MAXD = 5


def save(rec):
    data = json.loads(OUT.read_text()) if OUT.exists() else []
    data.append(rec)
    OUT.write_text(json.dumps(data, indent=1))


def min_degree(n, cons, dmax=MAXD, deadline_s=900):
    """Smallest degree at which algebra refutes, or why it stopped."""
    tried = []
    for d in range(1, dmax + 1):
        st, _, info = pc_f2(n, cons, [], d, deadline=time.time() + deadline_s, equivalences=False)
        tried.append({'d': d, 'status': st, **info})
        print(f'    algebra d={d}: {st} {info}', flush=True)
        if st == 'refuted':
            return d, tried
        if st in ('too_big', 'timeout'):
            return None, tried
    return None, tried


def geometry_alone(n, cons):
    st, new, info = sdp_lift(n, cons, [], probe=False)
    print(f'    geometry: {st} {info.get("seconds")}s', flush=True)
    return {'status': st, 'seconds': info.get('seconds')}


def pigeons():
    for h in range(2, 8):
        n, cons = fam.php(h)
        print(f'pigeons {h + 1} into {h} (n={n})', flush=True)
        d, tried = min_degree(n, cons)
        save({'family': 'pigeons', 'holes': h, 'n': n, 'algebra_min_degree': d,
              'algebra': tried, 'geometry': geometry_alone(n, cons)})


def parity():
    rng = Random(20261124)
    for nv in (10, 20, 40, 60, 80):
        for ratio in (1.5, 3.0):
            n, cons = fam.random_xor(nv, round(ratio * nv), rng)
            print(f'parity n={nv} m={len(cons)}', flush=True)
            d, tried = min_degree(n, cons, dmax=1)
            save({'family': 'parity', 'n': n, 'm': len(cons), 'algebra_min_degree': d,
                  'algebra': tried, 'geometry': geometry_alone(n, cons)})


def coupled():
    rng = Random(11)
    for h, ny, m in ((3, 10, 20), (4, 10, 20), (5, 10, 20), (6, 10, 20), (7, 10, 20), (8, 10, 20)):
        n, cons = fam.coupled(h, ny, m, rng)
        print(f'coupled: parity on {ny + 1} vars switches on {h + 1}-into-{h} pigeons (n={n})',
              flush=True)
        d, tried = min_degree(n, cons)
        geo = geometry_alone(n, cons)
        w = {}
        for wd in (1, 2):
            t = time.time()
            res, hist, facts = wave(n, cons, wd, log=lambda s: print('  ' + s, flush=True))
            w[f'd{wd}'] = {'result': res, 'rounds': max(x['round'] for x in hist),
                           'facts': len(facts), 'seconds': round(time.time() - t, 2),
                           'history': hist}
        save({'family': 'coupled', 'holes': h, 'parity_vars': ny + 1, 'parity_eqs': m, 'n': n,
              'algebra_min_degree': d, 'algebra': tried, 'geometry': geo, 'wave': w})


def sudoku():
    src = json.loads((HERE.parent / 'sudoku_gw_wave_2026_11_24' / 'results.json').read_text())
    for r in src:
        if r.get('propagation_only_solves'):
            continue
        n, cons, truth = fam.sudoku(r['puzzle'])
        print(f'sudoku {r["name"]} (n={n})', flush=True)
        rec = {'family': 'sudoku', 'name': r['name'], 'n': n, 'algebra': []}
        for d in (1, 2, 3):
            st, new, info = pc_f2(n, cons, [], d, deadline=time.time() + 900, equivalences=False)
            units = {f[1]: f[2] for f in new if f[0] == 'unit'}
            ok = all(truth[v] == a for v, a in units.items())
            rec['algebra'].append({'d': d, 'status': st, 'forced': len(units), 'of': n,
                                   'consistent_with_solution': ok, **info})
            print(f'    algebra d={d}: {st}, forced {len(units)}/{n} {info}', flush=True)
            if st != 'closed' or len(units) == n:
                break
        save(rec)


def sat():
    rng = Random(4)
    for nv in (12, 16, 20, 25, 30, 40, 50):
        n, cons = fam.random_3sat(nv, 5.0, rng)
        print(f'random 3-SAT n={nv} m={len(cons)} (unsatisfiable)', flush=True)
        d, tried = min_degree(n, cons)
        geo = geometry_alone(n, cons)
        rec = {'family': '3sat', 'n': n, 'm': len(cons), 'algebra_min_degree': d,
               'algebra': tried, 'geometry': geo}
        if d is None or d > 3:
            t = time.time()
            res, hist, facts = wave(n, cons, 3, log=lambda s: print('  ' + s, flush=True),
                                    deadline=time.time() + 900)
            rec['wave_d3'] = {'result': res, 'facts': len(facts), 'seconds': round(time.time() - t, 2),
                              'history': hist}
        save(rec)


if __name__ == '__main__':
    secs = sys.argv[1:] or ['pigeons', 'parity', 'coupled', 'sudoku', 'sat']
    for s in secs:
        globals()[s]()
