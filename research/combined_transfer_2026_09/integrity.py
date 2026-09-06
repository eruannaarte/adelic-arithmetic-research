"""Read-only portable integrity and exact integrated-consequence checks.

Only the Python standard library is needed. This checks sealed evidence and
exact consequences; it does not replace the separately recorded physical,
phase, polynomial or infinite-tail reconstructions.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import factorial,isqrt
from urllib.parse import unquote,urlsplit
import argparse,ast,hashlib,json,re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
COMPONENTS={'spatial':('combined-six-spatial-validation-v1','artifact_sha256',25),
            'blocks':('complete-orbit-clock-validation-v1','files',26),
            'degree11':('degree-eleven-validation-v1','files_sha256',33)}
ARCHIVAL_REFERENCES={
  'five_paths_2026_09/path2_harmonic/borsuk_1933_source.pdf':'3437a4a526e6aa295706cb6dd497eb2867b486ee45c48972b09de48fc26d3c1a',
  'five_paths_2026_09/path2_harmonic/borsuk_page1.png':'ccba081b582fa09d2538272aedac0910cd3695f7582d4d5b2b7e13461019a770',
  'five_paths_2026_09/path2_harmonic/borsuk_page2.png':'37f0ca4c4219b85d8029933cac89ef187b668424731296637de9a8dee23a85ea'}

def require(test,message):
    if not test:raise ValueError(message)
def q(value):
    require(type(value) in (str,int,Q),'exact rational metadata required')
    return Q(value)
def read(path):return json.loads(path.read_text())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def files_under(base):
    return {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()
      and not any(part in ('__pycache__','.pytest_cache') for part in p.relative_to(base).parts)
      and p.suffix!='.pyc' and p.name!='.DS_Store'}
def verify_hashes(base,mapping,label):
    require(type(mapping) is dict and mapping,label+' hash mapping')
    for name,expected in mapping.items():
        require(type(name) is str and not Path(name).is_absolute(),label+' portable path')
        target=(base/name).resolve()
        require(target.is_relative_to(base.resolve()),label+' path escapes its declared root')
        require(target.is_file() and type(expected) is str and re.fullmatch('[0-9a-f]{64}',expected) is not None,label+' missing file or invalid digest: '+name)
        require(digest(target)==expected,label+' changed artifact: '+name)
    return len(mapping)

def predecessor_selection(previous,missing):
    """Only these three hash-pinned third-party reference copies may be absent."""
    require(type(previous['count']) is int and previous['count']==660 and len(previous['files'])==660,'all660 predecessor artifacts required')
    for name,expected in ARCHIVAL_REFERENCES.items():
        require(previous['files'].get(name)==expected,'changed archival reference identity: '+name)
    require(set(missing)<=set(ARCHIVAL_REFERENCES),'missing required predecessor proof/evidence: '+', '.join(sorted(set(missing)-set(ARCHIVAL_REFERENCES))))
    return {name:expected for name,expected in previous['files'].items() if name not in missing}

def lineage_and_components():
    previous=read(HERE/'PREVIOUS_ARTIFACTS_SHA256.json')
    missing=sorted(name for name in previous['files'] if not (HERE.parent/name).is_file())
    present=predecessor_selection(previous,missing)
    verify_hashes(HERE.parent,present,'predecessor')
    totals={};manifests={}
    for name,(schema,key,count) in COMPONENTS.items():
        base=HERE/name;doc=read(base/'VALIDATION.json')
        require(doc['schema']==schema and doc['verified'] is True,name+' completed component seal')
        require(len(doc[key])==count,name+' component artifact count')
        verify_hashes(base,doc[key],name)
        require(set(doc[key])==files_under(base)-{'VALIDATION.json'},name+' complete component manifest coverage')
        totals[name]=count;manifests[name]=doc
    require(manifests['spatial']['checks']['unit_tests_passed']==13,'spatial13 tests')
    require(manifests['blocks']['checks']['adverse_and_positive_tests']==10,'block10 tests')
    require(manifests['degree11']['meaningful_controls_passed']==9,'degree11 nine tests')
    verify_hashes(ROOT,manifests['spatial']['dependencies_sha256'],'spatial physical dependencies')
    return {'historical_predecessor_hash_records':660,
      'present_verified_predecessor_files':len(present),'missing_archival_references':missing,
      'archival_reference_scope':'Only the three named, hash-pinned third-party Borsuk reference copies may be absent; all numerical proof sources and evidence remain required.',
      'component_artifacts':totals,'component_tests':32}

def review_bindings():
    block=read(HERE/'review/block_review.json')
    require(block['verified'] is True and block['phase_replay_bits']>=384 and block['actual_corner_lag_checks']==248,'independent block review')
    # Timing-bearing terminal logs are sealed by the component manifest.
    # The independent mathematical review binds its code, evidence and prose
    # inputs; re-running a test log is not a change to a reviewed premise.
    reviewed={p:h for p,h in block['reviewed_artifact_sha256'].items() if not p.endswith('.log')}
    verify_hashes(HERE/'blocks',reviewed,'independent block review input')
    for key in ('complete_valuation_tails_checked_against_exact_generating_function','all_odd_starting_integers_checked_by_proof','arbitrary_allowed_coefficient_amplitudes_checked_by_proof','nonlinear_shared_clock_remainder_checked_by_proof','reviewed_files_unchanged'):
        require(block[key] is True,'complete phase review scope: '+key)
    spatial=read(HERE/'review/spatial_review.json')
    require(spatial['verified'] is True and spatial['bits']>=384 and spatial['all_direction_cells_replayed']==2688 and spatial['all_pair_source_records_replayed']==1280,'independent spatial review coverage')
    require(spatial['directional_source_gate_passes'] is True and spatial['coarse_source_gate_also_passes'] is True,'both spatial inverse controls')
    degree=read(HERE/'review/degree11_review.json')
    require(degree['verified'] is True and degree['exact_strict_gate_checks']==196 and degree['accepted_integer_complex_disk_checks']==98,'independent degree11 query review')
    require(degree['four_saved_upper_residuals_replayed_at_384_bits'] is True and degree['reviewed_evidence_sha256']==digest(HERE/'degree11/evidence.json'),'degree11 reviewed evidence binding')
    for path in ('blocks/checked_orbit.json','blocks/precision_replay.json','blocks/consequences.json','degree11/orbit_comparison.json'):
        doc=read(HERE/path)
        require(doc['orbit_bound_sha256']==digest(HERE/'blocks/orbit_bound.json'),path+' complete clock binding')
    return {'reviewed_block_phase_bits':block['phase_replay_bits'],'reviewed_block_mathematical_inputs':len(reviewed),'reviewed_spatial_bits':spatial['bits'],'degree11_reviewed_gates':196}

def headline_bundle():
    names={'spatial':'spatial/checked.json','directions':'spatial/directions.json',
      'fixtures':'spatial/fixtures.json','decoded':'spatial/decoded.json',
      'orbit':'blocks/orbit_bound.json','publication':'blocks/publication_budget.json',
      'degree11':'degree11/evidence.json','degree11_orbit':'degree11/orbit_comparison.json'}
    data={k:read(HERE/v) for k,v in names.items()}
    data['arithmetic_tail']=read(HERE.parent/'transfer_theorem_2026_09/noise/evidence.json')
    data['approximation']=read(HERE.parent/'uncertain_transfer_2026_09/noise/approximation.json')
    data['results12']={d:read(HERE/f'blocks/result_{d}_h120.json') for d in ('multi','outer')}
    return data

def family_factor(approx,omega):
    degree=approx['degree'];rows=approx['approximants']
    require([r['order'] for r in rows]==list(range(degree+1,33)),'complete Taylor order coverage')
    parts=[Q(),Q()]
    for row in rows:
        k=row['order'];bound=q(row['weighted_residual_norm_upper'])
        require(bound>=0,'nonnegative approximation bound')
        parts[k%2]+=bound*omega**k/factorial(k)
    for k in (33,34):parts[k%2]+=q(approx['weighted_monomial_norm_upper'][str(k)])*omega**k/factorial(k)
    return max(parts)

def integer_budget(tail,approx,clock,budget,multiplier,amplitude):
    require(budget['degree']==approx['degree']==tail['degree'],'actual inverse degree binding')
    require(budget['design']==approx['design']==clock['design'],'arithmetic metric binding')
    if 'design' in tail:require(tail['design']==approx['design'],'tagged inverse metric')
    require(q(budget['amplitude_upper'])==amplitude,'fixed drift amplitude')
    require(q(budget['clock_slope_radius'])==Q(multiplier,10**14) and q(budget['clock_offset_radius'])==Q(multiplier,10**11),'shared clock rectangle')
    require(q(budget['sensor_radius'])==Q(4,10**5) and q(budget['mismatch_radius'])==Q(1,10**6),'fixed absolute sensor/mismatch norm')
    rho=q(budget['normal_residual_upper']);floor=1-q(tail['augmented_gram_defect'])
    require(0<=rho<=Q(1,10**30) and floor>0,'verified normal residual and Gram floor')
    tau=multiplier*q(clock['linear_clock_coefficient'])+multiplier**2*q(clock['quadratic_clock_coefficient'])
    family=amplitude*family_factor(approx,3*(1+Q(multiplier,10**14)))
    total=Q(4,10**5)+Q(1,10**6)+Q(1,10**20)+tau+family
    require(q(budget['clock_radius'])==tau and q(budget['family_radius'])==family and q(budget['complete_reading_radius'])==total,'complete joint uncertainty budget')
    require(q(budget['gram_floor'])==floor,'changed Gram floor')
    scale=10**60;root=Q(isqrt(floor.numerator*scale*scale//floor.denominator),scale)
    errors=[];passed=0
    for n in range(2,51):
        A=q(tail['complete_coefficient_bias_upper'][n-1]);margin=Q(1,2)-A-n*n*rho/floor
        passed+=int(margin>0 and n**4*total**2<margin*margin*floor)
        errors.append(A+n*n*(total/root+rho/floor))
    require(list(map(q,budget['complete_coefficient_error_bounds']))==errors,'coordinate error enclosures')
    require(q(budget['complete_coefficient_error_maximum'])==max(errors),'maximum coefficient enclosure')
    require(budget['passing_gates']==passed and type(budget['all_49_strict_rounding_gates']) is bool and budget['all_49_strict_rounding_gates']==(passed==49),'strict integer query consequence')
    return passed,max(errors)

def check_headlines(data=None):
    data=headline_bundle() if data is None else data
    s=data['spatial'];d=data['directions'];pair=s['weighted_pair_certificate']
    require(s['verified'] is True and d['bank_rows']==[485,493,499,501,507,515],'combined six-row bank')
    require(d['nominal_g']=='4/5' and d['time_interval']==['1','2'] and d['subdivisions']==128,'physical family and full time interval')
    require(pair['channel_count']==6 and pair['individual_cases']==21 and pair['pair_cases']==210 and pair['whole_cell_records']==1280 and pair['all_case_covers_verified'] is True,'all-source label certificate coverage')
    expected=[(j,[str(1+Q(k,128)),str(1+Q(k+1,128))]) for j in range(490,511) for k in range(128)]
    require([(r['target'],r['time_cell']) for r in d['records']]==expected,'all target/time direction cells')
    h=Q(1,10**8);eta=3*h
    require(q(s['sensor_relative_radius'])==eta and q(s['clock_radius'])==h and q(s['potential_radius'])==h and q(d['clock_radius'])==h and q(d['potential_radius'])==h,'predeclared physical uncertainty contract')
    nonlinear=h*h/2+128*h*h+Q(128,3)*h*h+2*h/Q(10**12)
    free=eta+Q(2,10**9)+nonlinear;F=Q(43,10**11);V=Q(17,25000000);mu=Q(361,256000000000)
    require(q(s['remainders']['total_nonlinear_radius'])==nonlinear and s['remainders']['complete_periodic_and_boundary_tails'] is True,'complete physical nonlinear/tail charge')
    require(q(s['unstructured_remainder_radius'])==free and q(s['label_total_relative_radius'])==free+F and q(s['certified_label_tube_radius'])==Q(13,400000000),'combined spatial tube budget')
    require(free+F<Q(13,400000000) and q(s['source_floor'])==mu,'strict spatial label margin')
    error=q(s['source_relative_error_upper'])
    require(q(s['structured_direction_radius'])==F and q(s['structured_inverse_radius'])==V and error>=V and (error-V)**2*mu>=free**2 and error<Q(852831068,10**12),'directional source accuracy headline')
    coarse=q(s['global_inverse_source_error_upper'])
    require(coarse*coarse*mu>=(free+F)**2 and coarse<Q(1,1000) and s['global_inverse_gate_also_passes'] is True,'coarse inverse also passes; no false directional necessity')
    fixtures=data['fixtures']['cases'];decoded=data['decoded']['cases']
    require(len(fixtures)==len(decoded)==24 and data['decoded']['verified'] is True,'24 actual raw decodings')
    for raw,answer in zip(fixtures,decoded):
        require(answer['status']=='unique' and answer['feasible_targets']==[raw['source_label']],'actual target answer')
        u=list(map(q,raw['source']));hat=list(map(q,answer['source_estimate']))
        error2=sum((a-b)**2 for a,b in zip(u,hat))/sum(a*a for a in u)
        require(error2==q(answer['observed_relative_source_error_squared']) and error2<=error*error,'actual relative source consequence')
    clock=data['orbit'];tail=clock['complete_valuation_tail']
    require(clock['measurement_count']==8900 and clock['source_class']=='all integers 0<=a(n)<=d_14(n), a(1)=1, every n>=1','complete arithmetic source class')
    require(tail['block_length']==32 and q(tail['omitted_envelope_mass_upper'])>0 and q(tail['omitted_weighted_envelope_mass_upper'])>0,'32 is a block, not a source cutoff')
    require(clock['predeclared_consequence_multiplier']==120,'predeclared arithmetic consequence')
    outcomes=[]
    for design in ('multi','outer'):
        cr=next(r for r in clock['records'] if r['design']==design)
        require(q(cr['quadratic_clock_coefficient'])>0 and q(cr['linear_clock_coefficient'])+q(cr['quadratic_clock_coefficient'])<Q(2987008,10**14),'complete clock radius headline')
        corners=cr['clock_corners']
        require([(c['slope_sign'],c['offset_sign']) for c in corners]==[(1,1),(1,-1),(-1,1),(-1,-1)],'joint shared clock corner coverage')
        require(all([r['lag'] for r in c['correlations']]==list(range(1,32)) for c in corners),'31 actual phase gaps')
        previous=q(cr['prior_pair_linear_clock_coefficient'])+q(cr['prior_pair_quadratic_clock_coefficient'])
        require(q(cr['linear_clock_coefficient'])+q(cr['quadratic_clock_coefficient'])<Q(4655,10000)*previous,'complete phase-block improvement')
        tail12=next(r for r in data['arithmetic_tail']['designs'][design]['degrees'] if r['degree']==12)
        app12=next(r for r in data['approximation']['records'] if (r['design'],r['degree'])==(design,12))
        result=data['results12'][design];budget=result['uncertainty_budget']
        passed,maximum=integer_budget(tail12,app12,cr,budget,120,4000)
        require(passed==49 and maximum<Q('0.447153367' if design=='multi' else '0.496198708'),'h120 complete degree12 query headline')
        old=dict(cr);old['linear_clock_coefficient']=cr['prior_pair_linear_clock_coefficient'];old['quadratic_clock_coefficient']=cr['prior_pair_quadratic_clock_coefficient']
        oldpassed,oldmaximum=integer_budget(tail12,app12,old,result['prior_pair_comparison'],120,4000)
        if design=='outer':require(oldpassed<49 and oldmaximum>Q('0.506493579'),'old sufficient formula fails at the identical contract')
        public=next(r for r in data['publication']['records'] if r['design']==design)
        components=list(map(q,public['component_upper_bounds'].values()))
        require(min(components)>=0 and sum(components)==q(public['sum_component_upper_bounds']) and maximum<=sum(components)<Q(1,2),'uniform public component enclosure')
        tail11=data['degree11']['designs'][design]['degrees'][0]
        app11=next(r for r in data['degree11']['approximations'] if r['design']==design)
        for amplitude in (4000,500):
            profile=next(r for r in data['degree11_orbit']['results'] if r['design']==design and q(r['amplitude_upper'])==amplitude)
            n,e=integer_budget(tail11,app11,cr,profile,1,amplitude)
            require(n==(32 if amplitude==4000 else 49),'degree11 amplitude-dependent sufficient gate')
            require((e>Q(1,2))==(amplitude==4000),'degree11 conditional conclusion')
        outcomes.append({'design':design,'h120_degree12_gates':passed,'preceding_pair_h120_gates':oldpassed,'degree11_B4000_gates':32,'degree11_B500_gates':49})
    return {'verified':True,'six_rows_full_clock_potential_contract':True,'actual_spatial_decodings':24,
      'all_source_all_time_coverage_recorded':True,'complete_phase_scope':'all odd starts and all omitted valuations; phase gain before the contractive exact nuisance projection',
      'failing_sufficient_gate_is_not_impossibility':True,'arithmetic':outcomes}

def syntax_and_links(allow_unsealed=False):
    parsed=0;links=0;skipped=0;pending=[]
    for path in HERE.rglob('*.py'):
        if '__pycache__' in path.parts:continue
        ast.parse(path.read_text(),filename=str(path));parsed+=1
    for path in HERE.rglob('*.md'):
        for match in re.finditer(r'\]\(\s*(<[^>]*>|[^\s)]+)(?:\s+["\'][^)]*)?\s*\)',path.read_text()):
            raw=match.group(1).strip('<>');url=urlsplit(raw)
            if url.scheme or url.netloc or not url.path:continue
            name=unquote(url.path)
            require(not Path(name).is_absolute(),'new research link must be portable: '+raw)
            target=(path.parent/name).resolve()
            if target.is_relative_to(ROOT/'publication') or target.is_relative_to(ROOT/'website'):
                skipped+=1;continue
            require(target.is_relative_to(ROOT),'research link leaves repository: '+raw)
            if not target.exists() and allow_unsealed and target in (HERE/'REPORT.md',HERE/'README.md'):
                pending.append(target.name);continue
            require(target.exists(),'broken research link in '+str(path.relative_to(HERE))+': '+raw);links+=1
    return {'python_files_parsed':parsed,'relative_research_links_checked':links,'external_publication_links_out_of_scope':skipped,'pending_root_documents':sorted(set(pending))}

def root_seal(allow_unsealed=False):
    path=HERE/'VALIDATION.json'
    if allow_unsealed:
        return {'root_seal_verified':False,'publication_ready':False,
          'construction_mode':'Root seal intentionally not checked while package is being assembled or resealed; all component and predecessor checks still run.'}
    if not path.exists():
        require(allow_unsealed,'root VALIDATION.json absent; --allow-unsealed is construction-only')
        return {'root_seal_verified':False,'publication_ready':False}
    doc=read(path)
    require(doc['all_recorded_checks_passed'] is True,'root recorded checks must pass')
    mapping=doc['validated_artifact_sha256']
    require('VALIDATION.json' not in mapping,'root manifest cannot self-hash')
    verify_hashes(HERE,mapping,'root package')
    require(set(mapping)==files_under(HERE)-{'VALIDATION.json'},'root package complete artifact coverage')
    counts=doc['focused_tests']
    if type(counts) is int:require(counts==33,'33 integrated focused tests required')
    else:
        require(type(counts) is dict and counts.get('total')==33,'33 integrated focused tests required')
    return {'root_seal_verified':True,'publication_ready':True,'new_package_artifacts':len(mapping),'focused_tests':33}

def run(allow_unsealed=False):
    out={'schema':'combined-transfer-integrity-v1','verified':True}
    out.update(lineage_and_components());out.update(review_bindings())
    out['headline_consequences']=check_headlines();out.update(syntax_and_links(allow_unsealed));out.update(root_seal(allow_unsealed))
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--allow-unsealed',action='store_true');args=p.parse_args()
    print(json.dumps(run(args.allow_unsealed),indent=2))
