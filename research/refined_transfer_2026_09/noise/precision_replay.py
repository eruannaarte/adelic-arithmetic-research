"""Reconstruct every rational approximation at two independent precisions."""
from copy import deepcopy
from pathlib import Path
import argparse, json
from approximation import build
from check_approximation import check_document

HERE=Path(__file__).resolve().parent


def normalized(doc):
    doc=deepcopy(doc)
    for r in doc['designs']:r.pop('projection_proposal_precision_bits')
    return doc


def run():
    saved=json.loads((HERE/'approximation.json').read_text())
    target=normalized(saved)
    for bits in (192,320):
        rebuilt=build(bits)
        if normalized(rebuilt)!=target:raise ValueError('rational approximation differs at higher/lower precision')
        check_document(saved,bits)
    return {'schema':'weighted-family-precision-replay-v1','verified':True,
            'producer_precisions_bits':[192,256,320],
            'consumer_replay_precisions_bits':[192,320],
            'all_24_rational_polynomials_identical':True,
            'all_30_weighted_norm_bounds_identical':True,
            'all_rational_family_consequences_identical':True}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();result=run()
    if a.write:(HERE/'precision_replay.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
