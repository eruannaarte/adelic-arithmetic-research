"""Independent unit/provenance checks for exported lab arithmetic profiles."""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial,isqrt,isclose
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
LAB=ROOT/'website/transfer-theorem-lab'

def read(p):return json.loads((ROOT/p).read_text())
def run():
    e=json.loads((LAB/'evidence.json').read_text())
    for p,h in e['inputSha256'].items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('export source hash mismatch')
    tail=read('research/transfer_theorem_2026_09/noise/evidence.json')
    old=read('research/uncertain_transfer_2026_09/noise/approximation.json')
    eleven=read('research/combined_transfer_2026_09/degree11/evidence.json')
    clock=read('research/combined_transfer_2026_09/blocks/orbit_bound.json')
    count=terms=0
    for design in ('multi','outer'):
        cr=next(r for r in clock['records'] if r['design']==design)
        for p in (6,8,10,11,12):
            display=e['arithmetic'][design][str(p)]
            if p==11:
                record=eleven['designs'][design]['degrees'][0]
                app=next(r for r in eleven['approximations'] if r['design']==design)
            else:
                record=next(r for r in tail['designs'][design]['degrees'] if r['degree']==p)
                app=next(r for r in old['records'] if (r['design'],r['degree'])==(design,p))
            f=1-Q(record['augmented_gram_defect']);scale=10**60
            sq=Q(isqrt(f.numerator*scale*scale//f.denominator),scale);gain=2500/sq
            if display['dimension']!=50+p:raise ValueError('wrong augmented dimension')
            checks=[(display['inverseGain'],gain),
                    (display['clockLinear'],gain*Q(cr['linear_clock_coefficient'])),
                    (display['clockQuadratic'],gain*Q(cr['quadratic_clock_coefficient'])),
                    (display['components']['sensor'],gain*Q(1,25000)),
                    (display['components']['mismatch'],gain*Q(1,10**6)),
                    (display['components']['tail'],max(map(Q,record['complete_coefficient_bias_upper'][1:])))]
            for exported,value in checks:
                if not isclose(exported,float(value),rel_tol=2e-14,abs_tol=1e-18):raise ValueError('wrong display units or numerical provenance')
            expected={r['order']:Q(r['weighted_residual_norm_upper'])/factorial(r['order']) for r in app['approximants']}
            expected.update({k:Q(app['weighted_monomial_norm_upper'][str(k)])/factorial(k) for k in (33,34)})
            seen={}
            for parity,key in [(1,'odd'),(0,'even')]:
                for k,value in display[key]:
                    if k%2!=parity or k in seen or k not in expected:raise ValueError('display parity/coverage')
                    if not isclose(value,float(expected[k]),rel_tol=2e-14,abs_tol=0):raise ValueError('Taylor term changed')
                    seen[k]=value;terms+=1
            if set(seen)!=set(expected):raise ValueError('omitted Taylor/remainder channel in display')
            computational=float(gain*Q(1,10**20)+2500*Q(1,10**30)/f)
            if not abs(display['components']['computation']-computational)<1.1e-18:raise ValueError('centering or future residual unit')
            count+=1
    for p in e['paths']:
        if not (ROOT/p['path']).is_file():raise ValueError('research path target missing')
    app=(LAB/'app.js').read_text();html=(LAB/'index.html').read_text()
    if 'Math.ceil(x*100*1e6)' not in app:raise ValueError('strict spatial percentage requires upward display')
    if 'cⱼ &gt; 0 and cₖ &gt; 0' not in html:raise ValueError('positive pair weights missing')
    if 'Source class & question' not in html or 'Real x ∈ [0,4]' not in html:raise ValueError('toy source-class distinction missing')
    if 'complex-modulus bound' not in html or 'rounding applies to the real part' not in html:raise ValueError('complex integer scope missing')
    return {'verified':True,'hashed_model_inputs':len(e['inputSha256']),'arithmetic_profiles':count,
        'complete_display_Taylor_terms':terms,'five_research_paths_have_local_evidence':True,
        'strict_spatial_percentage_rounds_upward':True,'positive_pair_weights_declared':True,
        'toy_source_classes_declared':True,'complex_modulus_and_real_rounding_declared':True,
        'scope':'Exported quantities checked as display estimates; rigorous badges derive from complete saved contracts, not these floating comparisons.'}
if __name__=='__main__':
    out=run();(HERE/'presentation_evidence.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
