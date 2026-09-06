"""Exact fixed-decoder admissible preparation/noise half-planes."""
from fractions import Fraction as Q
from pathlib import Path
import argparse,json
import checker as ch
import synthesize
HERE=Path(__file__).resolve().parent

def region(data,outer_rho,delta,eta,revised_rho):
    if not (0<=revised_rho<=outer_rho) or eta<0 or delta<=0:raise ValueError('invalid region')
    contraction=[sum(r,Q(0)) for r in data['R']];h=[sum(r,Q(0)) for r in data['H']];c=data['noise']
    if max(contraction)>=1:raise ValueError('noncontractive decoder')
    if any(x<=0 for x in h):raise ValueError('this boundary routine requires positive preparation support')
    limit=min([outer_rho]+[(delta*(1-k)-2*eta*nc)/(2*hp) for k,nc,hp in zip(contraction,c,h)])
    if limit<0:raise ValueError('noise alone exceeds target')
    lhs=[delta*k+2*(revised_rho*hp+eta*nc) for k,hp,nc in zip(contraction,h,c)]
    return {'row_contraction':contraction,'preparation_gain':h,'noise_gain':c,'outer_preparation_radius':outer_rho,'target':delta,'noise':eta,'maximum_preparation_radius':limit,'revised_preparation_radius':revised_rho,'revised_row_lhs':lhs,'revised_target_passes':all(x<=delta for x in lhs)}

def build(report,nominal,decoders,delta=Q(1,10000),eta=Q(1,10000000),rho=Q(7,1000000)):
    synthesize.verify(report,nominal,decoders);out={}
    for name,shares in ch.DESIGNS.items():
        fixed=ch.ingredients(report,nominal,shares,decoders['designs'][name]['ingredients']['b']);ls=ch.ingredients(report,nominal,shares)
        out[name]={'synthesized':region(fixed,Q(report['preparation_box_radius']),delta,eta,rho),'least_squares':region(ls,Q(report['preparation_box_radius']),delta,eta,rho)}
    return ch.encode({'schema':'preparation-calibration-region-v1','designs':out})

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--verify');ap.add_argument('--output');a=ap.parse_args()
    load=lambda f:json.loads((HERE/f).read_text())
    doc=build(load('cycle2_region.json'),load('nominal.json'),load('cycle2_certificate.json'))
    if a.verify:
        if doc!=json.loads(Path(a.verify).read_text()):raise ValueError('calibration mismatch')
        print('PASS');return
    if a.output:
        with Path(a.output).open('x') as f:json.dump(doc,f,indent=2);f.write('\n')
    print(json.dumps({k:{t:{'radius':float(Q(x['maximum_preparation_radius'])),'rho7e6_passes':x['revised_target_passes']} for t,x in v.items()} for k,v in doc['designs'].items()},indent=2))
if __name__=='__main__':main()
