"""Independent rational consumer of the degree-eleven transfer consequences."""
from fractions import Fraction as Q
from pathlib import Path
import argparse,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def check(doc=None):
    if doc is None:doc=json.loads((HERE/'evidence.json').read_text())
    if doc['schema']!='complete-degree-eleven-v1' or doc['measurement_count']!=8900 or type(doc['degree']) is not int or doc['degree']!=11:raise ValueError('degree-eleven contract')
    expected=['research/transfer_theorem_2026_09/noise/evidence.json','research/uncertain_transfer_2026_09/noise/approximation.json','research/structured_transfer_2026_09/arithmetic/clock_bound.json']
    if sorted(doc['predecessor_sha256'])!=sorted(expected):raise ValueError('premise coverage')
    for p,h in doc['predecessor_sha256'].items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('predecessor hash mismatch')
    tail=json.loads((ROOT/expected[0]).read_text())
    consumer=load('_degree11_old_independent_consumer',ROOT/'research/transfer_theorem_2026_09/noise/check_certificate.py')
    consumer.check(tail,True)
    app=json.loads((ROOT/expected[1]).read_text())
    if set(doc['designs'])!={'multi','outer'} or [(a['design'],a['degree']) for a in doc['approximations']]!=[('multi',11),('outer',11)]:raise ValueError('design coverage')
    summaries=[]
    for name in ('multi','outer'):
        before=tail['designs'][name];now=doc['designs'][name]
        if now['physical_polynomials']!=before['physical_polynomials'] or len(now['degrees'])!=1:raise ValueError('physical basis or record coverage')
        if now['degrees'][0].get('design')!=name:raise ValueError('inverse design binding')
        cross=[[max(abs(Q(lo)),abs(Q(hi))) for lo,hi in row] for row in before['physical_polynomials']['cross_real_even_imaginary_odd']]
        summary=consumer.derive_and_check(now['degrees'][0],list(map(Q,before['arithmetic_complete_bias_upper'])),
            list(map(Q,before['arithmetic_gram_rows'])),cross,list(map(Q,before['complete_nuisance_channel_upper'])),11,Q(4,10**5))
        a=next(a for a in doc['approximations'] if a['design']==name)
        if [r['order'] for r in a['approximants']]!=list(range(12,33)):raise ValueError('Taylor-channel coverage')
        for r in a['approximants']:
            k=r['order'];p=12 if k%2 else 10
            previous=next(a for a in app['records'] if (a['design'],a['degree'])==(name,p))
            old=next(v for v in previous['approximants'] if v['order']==k)
            poly=list(map(Q,r['rational_polynomial']));old_poly=list(map(Q,old['rational_polynomial']))
            if len(poly)!=12 or any(v for j,v in enumerate(poly) if j%2!=k%2):raise ValueError('degree or parity')
            if any(old_poly[12:]) or poly!=(old_poly+[Q()]*12)[:12]:raise ValueError('approximant provenance')
            if r['inherited_approximant_degree']!=p or r['weighted_residual_norm_upper']!=old['weighted_residual_norm_upper']:raise ValueError('norm provenance')
        old=next(a for a in app['records'] if (a['design'],a['degree'])==(name,12))
        if a['weighted_monomial_norm_upper']!=old['weighted_monomial_norm_upper']:raise ValueError('complete Taylor remainder changed')
        summaries.append({'design':name,**summary})
    return {'verified':True,'degree':11,'records':summaries}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    out=check()
    if args.write:(HERE/'checked.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
