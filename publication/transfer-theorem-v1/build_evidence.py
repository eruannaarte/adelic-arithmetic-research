"""Build portable lab data from exact, hash-bound research artifacts."""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial,isqrt
import hashlib,json

ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'website/transfer-theorem-lab'
TAG='transfer-theorem-v1-2026-09-05'
REPO='https://github.com/eruannaarte/adelic-arithmetic-research'
BASE=REPO+'/blob/'+TAG+'/'
inputs={}
def read(name):
    path=ROOT/name;inputs[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    return json.loads(path.read_text())
def upper(q):
    q=Q(q);scale=10**18
    return float(Q(-(-q.numerator*scale//q.denominator),scale))
def url(path):return BASE+path

tail=read('research/transfer_theorem_2026_09/noise/evidence.json')
approx=read('research/uncertain_transfer_2026_09/noise/approximation.json')
eleven=read('research/combined_transfer_2026_09/degree11/evidence.json')
orbit=read('research/combined_transfer_2026_09/blocks/orbit_bound.json')
consequences=read('research/combined_transfer_2026_09/blocks/consequences.json')
degree_result=read('research/combined_transfer_2026_09/degree11/orbit_comparison.json')
spatial=read('research/combined_transfer_2026_09/spatial/checked.json')
assert spatial['source_accuracy_verified'] and spatial['label_separation_verified']
assert Q(spatial['source_relative_error_upper'])<Q('0.000852831068')
arithmetic={}
for design in ('multi','outer'):
    arithmetic[design]={}
    clock=next(r for r in orbit['records'] if r['design']==design)
    for p in (6,8,10,11,12):
        if p==11:
            prior=eleven['designs'][design]['degrees'][0]
            app=next(r for r in eleven['approximations'] if r['design']==design)
        else:
            prior=next(r for r in tail['designs'][design]['degrees'] if r['degree']==p)
            app=next(r for r in approx['records'] if (r['design'],r['degree'])==(design,p))
        f=1-Q(prior['augmented_gram_defect']);scale=10**60
        sf=Q(isqrt(f.numerator*scale*scale//f.denominator),scale);gain=2500/sf
        biases=list(map(Q,prior['complete_coefficient_bias_upper']))
        terms={r['order']:Q(r['weighted_residual_norm_upper'])/factorial(r['order']) for r in app['approximants']}
        terms.update({k:Q(app['weighted_monomial_norm_upper'][str(k)])/factorial(k) for k in (33,34)})
        # The JSON uses double precision for drawing, never for a rigorous gate.
        # Keep tiny Taylor terms as floats; an absolute 1e-18 ceiling would
        # materially inflate high powers at Omega=3.
        entry={'dimension':50+p,'components':{'tail':upper(max(biases[1:])),
            'sensor':upper(gain*Q(1,25000)),'mismatch':upper(gain*Q(1,10**6)),
            'computation':upper(gain*Q(1,10**20)+2500*Q(1,10**30)/f)},
            'inverseGain':float(gain),'clockLinear':float(gain*Q(clock['linear_clock_coefficient'])),
            'clockQuadratic':float(gain*Q(clock['quadratic_clock_coefficient'])),
            'odd':[[k,float(v)] for k,v in sorted(terms.items()) if k%2],
            'even':[[k,float(v)] for k,v in sorted(terms.items()) if not k%2],
            'scope':'Rounded display estimates; badge inherits only the separately checked saved contract.'}
        if p==12:
            row=next(r['budget'] for r in consequences['comparisons'] if r['method']=='orbit' and r['budget']['design']==design and r['budget']['degree']==12 and r['budget']['clock_multiplier']=='120')
            assert row['all_49_strict_rounding_gates'] and Q(row['complete_coefficient_error_maximum'])<Q(1,2)
            entry['certifiedMaximum']=upper(row['complete_coefficient_error_maximum'])
        if p==11:
            r=next(r for r in degree_result['results'] if r['design']==design and r['amplitude_upper']=='500')
            assert r['all_49_strict_rounding_gates']
            # The saved example has a much smaller actual residual. Add the
            # entire future 1e-30 allowance before advertising containment for
            # future verified data, then round the displayed bound upward.
            planned=Q(r['complete_coefficient_error_maximum'])+2500*Q(1,10**30)/f
            assert planned<Q(1,2)
            entry['certifiedMaximumB500']=upper(planned)
        arithmetic[design][str(p)]=entry

paths=[
 {'title':'Preparation & calibration','subtitle':'Make the uncertainty set defensible.',
  'finding':'Grouped pendulum observations can restore a certified information floor after shared clock uncertainty destroys a smaller experiment. Later work gives joint launch-calibration acceptance conditions.',
  'connection':'The transfer theorem needs a justified uncertainty region. The pendulum work explains how preparation and shared instrument corrections enter it. Apparatus calibration remains unperformed.',
  'path':'research/unified_query_2026_09/preparation/README.md'},
 {'title':'Harmonic acquisition','subtitle':'Count readings—and test every source difference.',
  'finding':'A sharp reading count is proved for the labelled product-distribution model. Later short schedules have strong vertex separation but certified interior collisions.',
  'connection':'Pair separation must cover the whole source class. Good endpoint checks do not exclude an unseen ambiguity inside the class.',
  'path':'research/unified_query_2026_09/harmonic/REPORT.md'},
 {'title':'Arithmetic query structure','subtitle':'Answer a discrete question without reconstructing everything.',
  'finding':'Quadratic-field witnesses connect abstract coefficient uncertainty to actual arithmetic. A query decoder uses multiplicative relations and uncertain intermediate labels.',
  'connection':'The answer set can be a singleton even when other source coordinates remain uncertain. Valid realizability and the measurement norm matter.',
  'path':'research/unified_query_2026_09/quadratic/REPORT.md'},
 {'title':'Multiscale arithmetic sensing','subtitle':'Keep the complete infinite tail in the budget.',
  'finding':'Weighted acquisition, polynomial nuisance removal and complete clock blocks give verified integer recovery from 8,900 readings.',
  'connection':'This supplies the integer rounding consequence. Bias, sensor noise, drift, mismatch, clock error and verified residual all share the same strict budget.',
  'path':'research/combined_transfer_2026_09/blocks/REPORT.md'},
 {'title':'Finite-resolution sensing','subtitle':'Compare error with the weakest recoverable direction.',
  'finding':'Finite approximation can preserve a continuum guarantee only at a compatible information scale. Restricted banks now yield six-channel recovery with a declared clock/potential box.',
  'connection':'This supplies continuous source recovery and label separation. Structured directions and weighted pair inequalities preserve information that a coarse scalar bound can lose.',
  'path':'research/combined_transfer_2026_09/spatial/REPORT.md'}]
history=[('five_paths','Five promising paths','Initial theorem, recovery and calibration extensions.'),('next15','Fifteen next-objective cycles','Repeated advances and obstructions across all five paths.'),('unified_query','A common query framework','Whole-source harmonic collisions, arithmetic constraints and calibration.'),('transfer_theorem','Transfer with consequences','Nuisance removal, finite approximation and restricted acquisition.'),('operational_transfer','Operational decoding','Actual observations, verified residuals and raw normalization.'),('refined_transfer','Sharper approximation','Weighted drift families and smaller spatial sensing banks.'),('uncertain_transfer','Uncertain acquisition','Explicit clock and model mismatch budgets.'),('structured_transfer','Directional transfer','Six known-time rows, seven uncertain rows and complete clock pairing.'),('combined_transfer','Combined contracts','Six uncertain rows, complete multiplicative blocks and verified degree eleven.')]
evidence={'schema':'transfer-theorem-lab-evidence-v1','tag':TAG,'release':REPO+'/releases/tag/'+TAG,
 'spatial':{
  'sixJoint':{'rows':[485,493,499,501,507,515],'sensor':3e-8,'clock':1e-8,'potential':1e-8,'error':.000852831068,'source':'research/combined_transfer_2026_09/spatial/REPORT.md'},
  'sixKnown':{'rows':[485,493,499,501,507,515],'sensor':3e-8,'clock':0,'potential':0,'error':.000852151,'source':'research/structured_transfer_2026_09/six_rows/REPORT.md'},
  'sevenJoint':{'rows':[490,492,496,500,504,508,510],'sensor':1.1e-7,'clock':5e-7,'potential':2.5e-6,'error':.000801020,'source':'research/structured_transfer_2026_09/resolution/REPORT.md'}},
 'arithmetic':arithmetic,'paths':[{**r,'url':url(r['path'])} for r in paths],
 'history':[{'title':title,'description':description,'url':url('research/'+name+'_2026_09/REPORT.md')} for name,title,description in history],
 'proofLinks':{'theorem':url('research/combined_transfer_2026_09/framework/PROOFS.md'),'spatial':url('research/combined_transfer_2026_09/spatial/README.md'),'arithmetic':url('research/combined_transfer_2026_09/README.md')},
 'links':[
 {'title':'Public research guide ↗','description':'The question, theorem, model contracts and five research paths.','url':url('TRANSFER_THEOREM_PUBLIC_COMPANION.md')},
 {'title':'Current mathematical report ↗','description':'All three new results, independent checks and precise limitations.','url':url('research/combined_transfer_2026_09/REPORT.md')},
 {'title':'Download the standalone lab ↗','description':'ZIP: open index.html directly; no server or dependencies.','url':REPO+'/releases/download/'+TAG+'/Transfer-Theorem-Lab-v1.zip'},
 {'title':'Reproduce the results ↗','description':'Portable setup, fast checks, full model reconstruction and hashes.','url':url('publication/transfer-theorem-v1/PORTABLE_GUIDE.md')},
 {'title':'Immutable publication release ↗','description':'Source, publication package, checksums and citation.','url':REPO+'/releases/tag/'+TAG},
 {'title':'Independent internal reviews ↗','description':'Reciprocal proof audits and fresh higher-precision model replays.','url':REPO+'/tree/'+TAG+'/research/combined_transfer_2026_09/review'}],
 'inputSha256':inputs}
DEST.mkdir(exist_ok=True)
out=json.dumps(evidence,indent=2,ensure_ascii=False)+'\n'
(DEST/'evidence.json').write_text(out)
(DEST/'evidence.js').write_text('/* Generated by publication/transfer-theorem-v1/build_evidence.py. */\nwindow.TransferEvidence = '+out.rstrip()+';\n')
print(json.dumps({'designDegreeProfiles':10,'hashedInputs':len(inputs),'output':'website/transfer-theorem-lab/evidence.json'}))
