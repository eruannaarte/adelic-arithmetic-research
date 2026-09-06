"""Bounded floating discovery. No output of this program is a proof."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import argparse, json
import numpy as np

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parents[1]/'transfer_theorem_2026_09/resolution'


def sample(bank, values):
    maps = values[:, np.abs(np.array(bank)[None, :]-np.arange(-10,11)[:,None]), :]
    source = np.linalg.eigvalsh(np.einsum('tjmq,tjmr->tjqr',maps,maps))[...,0]
    pairs = list(combinations(range(21),2))
    blocks = np.concatenate((maps[:,[j for j,k in pairs]],-maps[:,[k for j,k in pairs]]),axis=3)
    gram = np.einsum('tjmi,tjmq->tjiq',blocks,blocks)
    pair = np.linalg.eigvalsh(gram)[...,0]
    index = np.unravel_index(np.argmin(pair),pair.shape)
    return {'bank_offsets':list(bank),'sampled_unnormalized_source_floor':float(source.min()),
            'sampled_unnormalized_pair_floor':float(pair.min()),
            'limiting_sample_time':float(np.linspace(1,2,len(values))[index[0]]),
            'limiting_pair':[x-10 for x in pairs[index[1]]]}


def run():
    k = json.loads((PRIOR/'kernel.json').read_text())
    c = np.array([[[float((Q(a)+Q(b))/2) for a,b in p] for p in d] for d in k['coefficient_intervals']])
    times = np.linspace(1,2,33)
    values = np.array([np.polynomial.polynomial.polyval(t-1.5,c.transpose(2,0,1)) for t in times])
    banks = [(-15,-12,-8,-4,0,4,8,12,16),(-14,-10,-6,-2,2,6,10,14),
             (-15,-10,-5,0,5,10,16),(-16,-11,-6,-1,4,9,14),
             (-15,-9,-3,3,9,15),(-16,-10,-4,2,8,14),(-16,-8,0,8,16),(-15,-5,5,15)]
    return {'status':'floating discovery only; no continuum claim','sample_times':list(map(float,times)),
            'cases':[sample(b,values) for b in banks]}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    d=run()
    if args.write:(HERE/'discovery.json').write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps(d['cases'],indent=2))
