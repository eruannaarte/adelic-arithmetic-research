"""An exact witness shows why the old uniform pair-floor gate is insufficient."""
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib,argparse
import obstruction_check as physical
HERE=Path(__file__).resolve().parent
ROWS=(-15,-7,-1,1,7,15);LABELS=(9,10);TIME=Q(1)

def matrix():
    c=physical.coefficients()
    return [[(-1)**side*physical.value(c[abs(row-label)][port],TIME) for side,label in enumerate(LABELS) for port in (0,1)] for row in ROWS]
def propose():
    import numpy as np
    _,_,vh=np.linalg.svd(np.array(matrix(),float),full_matrices=False)
    return {'schema':'six-row-uniform-floor-countercertificate-v1','kernel_sha256':hashlib.sha256(physical.KERNEL.read_bytes()).hexdigest(),
            'bank_offsets':list(ROWS),'target_offsets':list(LABELS),'time':'1','source_pair':[str(Q(format(x,'.18f'))) for x in vh[-1]]}
def verify(document):
    expected={'schema':'six-row-uniform-floor-countercertificate-v1','kernel_sha256':hashlib.sha256(physical.KERNEL.read_bytes()).hexdigest(),
              'bank_offsets':list(ROWS),'target_offsets':list(LABELS),'time':'1'}
    for k,v in expected.items():physical.require(document[k]==v,'comparison contract')
    v=list(map(physical.rational,document['source_pair']));physical.require(len(v)==4,'witness dimension')
    norm=sum((a*a for a in v),Q());physical.require(norm>0,'zero comparison witness')
    response=[sum((a*b for a,b in zip(row,v)),Q()) for row in matrix()]
    rayleigh=sum((r*r for r in response),Q())/norm
    needed=2*(Q(32,10**9)/Q(19,16))**2
    physical.require(rayleigh<needed,'uniform floor is not disproved')
    return {'verified':True,'rayleigh_upper_on_smallest_pair_gram_eigenvalue':str(rayleigh),'uniform_pair_floor_requirement':str(needed),
            'ratio_upper':str(rayleigh/needed),'consequence':'No true lower Gram floor reaches the old uniform sufficient requirement for this bank.',
            'limitation':'This disproves only that sufficient gate. The weighted complete-time certificate proves recovery under the unchanged acquisition contract.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    doc=propose() if a.write else json.loads((HERE/'uniform_comparison.json').read_text());result=verify(doc)
    if a.write:
        (HERE/'uniform_comparison.json').write_text(json.dumps(doc,indent=2)+'\n')
        (HERE/'uniform_comparison_checked.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
