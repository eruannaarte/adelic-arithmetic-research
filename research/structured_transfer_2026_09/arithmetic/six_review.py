"""Second-agent review of weighted source-block separation and raw decoding."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json,sys,time

HERE=Path(__file__).resolve().parent;SIX=HERE.parent/'six_rows'
sys.path.insert(0,str(SIX))
from raw import PhysicalBank

def run():
    started=time.perf_counter();bank=PhysicalBank()
    certificate=json.loads((SIX/'certificate_6.json').read_text())
    delta=Q(3,10**8)+Q(1,10**9)+Q(1,10**9);a0=Q(19,16);sf=Q(1,10**9)
    squared=delta*delta/(a0*a0*sf)
    if squared!=Q(bank.summary['metrics']['L2']['source_relative_error_squared_upper']) or not squared<Q(1,10**6):raise ValueError('source transfer budget')
    identities=0
    for r in certificate['records']:
        if len(r['case'])!=2:continue
        a=Q(r['source_split_weight'])
        if not 0<a<1:raise ValueError('positive source-block split')
        for u,v in ((Q(0),Q(1)),(Q(1),Q(0)),(Q(2,3),Q(5,7))):
            gap=u*u/a+v*v/(1-a)-(u+v)**2
            exact=((1-a)*u-a*v)**2/(a*(1-a))
            if gap!=exact or gap<0:raise ValueError('weighted source norm implication')
            identities+=1
    fixtures=json.loads((SIX/'fixtures.json').read_text())['cases']
    # Endpoint times, outer and central labels, with every source direction
    # and the fixture's widely different source scales retained.
    selected=[r for r in fixtures if r['time'] in ('1','2') and r['source_label'] in (490,500,510)]
    if len(selected)!=24:raise ValueError('review fixture coverage')
    maximum=Q()
    for r in selected:
        answer=bank.decode(r['raw_data'],r['time'])
        if answer['status']!='unique' or answer['feasible_targets']!=[r['source_label']]:raise ValueError('raw target consequence')
        u=list(map(Q,r['source']));estimate=list(map(Q,answer['source_estimate']))
        error=sum((a-b)**2 for a,b in zip(u,estimate))/sum(a*a for a in u)
        if error>squared:raise ValueError('raw source error exceeds full physical budget')
        maximum=max(maximum,error)
        receipt=answer['normalization']['scale']
        from raw import normalization
        charge=normalization.verify_packet(r['raw_data'],answer['normalization'])
        if not 0<=charge<=Q(1,10**9):raise ValueError('physical normalization charge')
    rejected=0
    for action in (
        lambda:bank.decode(fixtures[0]['raw_data'],1.0),
        lambda:bank.decode(fixtures[0]['raw_data'],'1',xi_budget='2/1000000000'),
        lambda:bank.decode(fixtures[0]['raw_data'][:-1],'1')):
        try:action()
        except ValueError:rejected+=1
        else:raise ValueError('invalid physical contract not rejected')
    incompatible=bank.decode(['1','0','0','0','0','0'],'1')
    if incompatible['status']!='incompatible' or incompatible['guaranteed_relative_source_accuracy'] is not None:raise ValueError('unsupported raw data received accuracy claim')
    files=['certify.py','certificate_6.json','decoder.py','raw.py','fixtures.json','PROOFS.md']
    return {'schema':'independent-six-row-source-block-review-v1','verified':True,
            'full_time_polynomial_records_replayed':bank.summary['whole_cell_records'],
            'exact_weighted_source_norm_identity_cases':identities,'endpoint_raw_data_cases':len(selected),
            'invalid_time_budget_dimension_controls_rejected':rejected,
            'incompatible_observation_has_no_accuracy_claim':True,
            'relative_source_error_squared_guarantee':str(squared),'largest_checked_raw_relative_error_squared':str(maximum),
            'wall_seconds':time.perf_counter()-started,
            'artifact_sha256':{name:hashlib.sha256((SIX/name).read_bytes()).hexdigest() for name in files},
            'review':'Weighted Cauchy source-block implication, Sylvester leading-minor whole-cell certificate, exact relative-feasibility quadratic, ordinary least-squares return, and nominal-alpha physical normalization charge checked. Known time/nominal potential only; no six-row timing tolerance inferred.'}

if __name__=='__main__':
    result=run();(HERE/'six_review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
