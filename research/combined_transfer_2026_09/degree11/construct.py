"""Derive degree eleven from complete verified channels, not a degree-12 inverse."""
from fractions import Fraction as Q
from pathlib import Path
import argparse, hashlib, importlib.util, json

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    out=importlib.util.module_from_spec(spec);spec.loader.exec_module(out);return out

def bindings():
    paths=['research/transfer_theorem_2026_09/noise/evidence.json',
           'research/uncertain_transfer_2026_09/noise/approximation.json',
           'research/structured_transfer_2026_09/arithmetic/clock_bound.json']
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}

def build():
    old=module('_degree11_tail_producer',ROOT/'research/transfer_theorem_2026_09/noise/oscillatory_channels.py')
    tail=json.loads((ROOT/'research/transfer_theorem_2026_09/noise/evidence.json').read_text())
    approx=json.loads((ROOT/'research/uncertain_transfer_2026_09/noise/approximation.json').read_text())
    designs={};approximations=[]
    for name in ('multi','outer'):
        data=tail['designs'][name]
        cross=[[max(abs(Q(lo)),abs(Q(hi))) for lo,hi in row] for row in data['physical_polynomials']['cross_real_even_imaginary_odd']]
        record=old.consequences(list(map(Q,data['arithmetic_complete_bias_upper'])),
            list(map(Q,data['arithmetic_gram_rows'])),cross,
            list(map(Q,data['complete_nuisance_channel_upper'])),11,Q(4,10**5))
        record['design']=name
        designs[name]={'physical_polynomials':data['physical_polynomials'],'degrees':[record]}
        lower=next(r for r in approx['records'] if (r['design'],r['degree'])==(name,10))
        upper=next(r for r in approx['records'] if (r['design'],r['degree'])==(name,12))
        records=[]
        for k in range(12,33):
            before=upper if k%2 else lower
            entry=next(a for a in before['approximants'] if a['order']==k)
            poly=list(map(Q,entry['rational_polynomial']))
            if len(poly)>12 and any(poly[12:]):raise ValueError('degree twelve leaked into degree eleven')
            poly=(poly+[Q()]*12)[:12]
            if any(c for j,c in enumerate(poly) if j%2!=k%2):raise ValueError('parity failure')
            records.append({'order':k,'rational_polynomial':list(map(str,poly)),
                            'weighted_residual_norm_upper':entry['weighted_residual_norm_upper'],
                            'inherited_approximant_degree':before['degree']})
        approximations.append({'design':name,'degree':11,'approximants':records,
            'weighted_monomial_norm_upper':upper['weighted_monomial_norm_upper']})
    return {'schema':'complete-degree-eleven-v1','measurement_count':8900,'degree':11,
            'predecessor_sha256':bindings(),'designs':designs,'approximations':approximations,
            'construction':'Recompute the full degree-11 Schur and query bounds using channels 1..11; combine degree-12 odd and degree-10 even approximants by exact parity.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    doc=build();path=HERE/'evidence.json'
    if args.write:path.write_text(json.dumps(doc,indent=2)+'\n')
    elif json.loads(path.read_text())!=doc:raise ValueError('reconstruction differs')
    for name,d in doc['designs'].items():
        r=d['degrees'][0];print(name,'bias',float(max(map(Q,r['complete_coefficient_bias_upper'][1:]))),'floor',float(1-Q(r['augmented_gram_defect'])))
