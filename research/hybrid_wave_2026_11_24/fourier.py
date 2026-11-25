"""The problem as a wave: Fourier (Walsh-Hadamard) spectra of constraint problems.

On n bits the natural Fourier transform is the Walsh-Hadamard transform. Its "frequencies" are
subsets S of the variables and its waves are the parities chi_S(x) = (-1)^(sum of x_i, i in S).
Write the solution set as an indicator f(x) = 1 if x satisfies every constraint. Then
  f = f_1 * f_2 * ... * f_m        (one factor per constraint)
and multiplying functions means CONVOLVING their spectra. Each constraint alone has a tiny
spectrum (a 3-variable clause has 8 frequencies), but every multiplication spreads the spectrum.

This script tracks how many frequencies are switched on (support of the spectrum) as constraints
are multiplied in, for random 3-SAT (planted, satisfiable) and random 3-XOR (planted), and checks
what the lowest frequencies say about the answer.

Usage: fourier.py <n> <seed>     (memory: 2^n floats; n = 18 is a few MB)
"""
import json
import sys
from pathlib import Path
from random import Random

import numpy as np

HERE = Path(__file__).resolve().parent


def wht(a):
    a = a.astype(float).copy()
    h, n = 1, len(a)
    while h < n:
        a = a.reshape(-1, 2, h)
        a = np.stack((a[:, 0] + a[:, 1], a[:, 0] - a[:, 1]), axis=1).reshape(-1)
        h *= 2
    return a / n                    # f_hat(S) = average of f(x) * chi_S(x)


def run(n, seed):
    rng = Random(seed)
    xs = np.arange(2 ** n)
    bits = [(xs >> i) & 1 for i in range(n)]
    popcount = sum(bits)            # frequency S as a bitmask: its size is the "degree"
    plant = [rng.randrange(2) for _ in range(n)]
    out = {'n': n, 'seed': seed}
    for kind, m in (('3sat', round(4.0 * n)), ('3xor', n + 4)):
        f = np.ones(2 ** n)
        trace = []
        for k in range(1, m + 1):
            vs = rng.sample(range(n), 3)
            if kind == '3sat':      # planted: random signs, redrawn until the plant satisfies it
                while True:
                    sg = [rng.randrange(2) for _ in vs]
                    if any(plant[v] != s for v, s in zip(vs, sg)):
                        break
                fc = 1 - np.prod([(bits[v] == s) for v, s in zip(vs, sg)], axis=0)
            else:
                b = sum(plant[v] for v in vs) % 2
                fc = ((bits[vs[0]] ^ bits[vs[1]] ^ bits[vs[2]]) == b).astype(float)
            f = f * fc
            spec = wht(f)
            support = int(np.sum(np.abs(spec) > 1e-12))
            trace.append({'constraints': k, 'solutions': int(f.sum()), 'support': support,
                          'support_fraction': support / 2 ** n})
        spec = wht(f)
        w = spec ** 2
        by_degree = [float(w[popcount == d].sum() / w.sum()) for d in range(n + 1)]
        # degree-1 frequencies: f_hat({i}) is proportional to (#solutions with x_i = 0) - (#with x_i = 1)
        deg1 = [float(spec[1 << i]) for i in range(n)]
        guess = [int(c < 0) for c in deg1]
        out[kind] = {'constraints': m, 'solutions': int(f.sum()), 'trace': trace,
                     'weight_by_degree': by_degree,
                     'degree1_reads_plant': guess == plant if f.sum() == 1 else None,
                     'support_final': trace[-1]['support']}
        print(f'{kind} n={n}: {m} constraints, {int(f.sum())} solutions, spectrum support '
              f'{trace[-1]["support"]} of {2 ** n}', flush=True)
        for t in trace[:: max(1, m // 8)] + [trace[-1]]:
            print(f'   after {t["constraints"]:3d} constraints: {t["solutions"]:7d} solutions, '
                  f'{t["support"]:7d} frequencies on ({100 * t["support_fraction"]:.1f}%)', flush=True)
    (HERE / f'fourier_n{n}_s{seed}.json').write_text(json.dumps(out, indent=1))


if __name__ == '__main__':
    run(int(sys.argv[1]), int(sys.argv[2]))
