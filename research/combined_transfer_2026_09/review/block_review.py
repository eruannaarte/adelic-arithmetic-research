"""Independent complete-orbit audit; writes only its optional review output.

Includes a generating-function check of infinite valuation tails and fresh
physical model/data/dual-residual reconstruction, not a replay-flag assertion.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import comb, factorial
import argparse, hashlib, importlib.util, json, sys, time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BLOCK=HERE.parent/'blocks'
OP=ROOT/'research/operational_transfer_2026_09/noise'
sys.path.insert(0,str(OP))
from physical import PhysicalModel
from certify import verify

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def scalar_budget(record,approx,clock,rho,h=120):
    """Direct exact squared gate, independent of both budget implementations."""
    assert record['degree']==approx['degree']==12
    omega=3*(1+Q(h,10**14))
    terms={r['order']:r for r in approx['approximants']}
    assert sorted(terms)==list(range(13,33))
    parity=[]
    for start,tail in ((13,33),(14,34)):
        value=sum((Q(terms[k]['weighted_residual_norm_upper'])*omega**k/factorial(k)
                   for k in range(start,33,2)),Q())
        value+=Q(approx['weighted_monomial_norm_upper'][str(tail)])*omega**tail/factorial(tail)
        parity.append(value)
    timing=h*Q(clock['linear_clock_coefficient'])+h*h*Q(clock['quadratic_clock_coefficient'])
    total=Q(1,25000)+Q(1,10**6)+Q(1,10**20)+4000*max(parity)+timing
    f=1-Q(record['augmented_gram_defect'])
    assert f>0 and 0<=rho<=Q(1,10**30)
    margins=[]
    for n in range(2,51):
        m=Q(1,2)-Q(record['complete_coefficient_bias_upper'][n-1])-n*n*rho/f
        margins.append(m>0 and m*m*f-n**4*total**2>0)
    return {'passing_integer_gates':sum(margins),'complete_reading_radius':str(total),
            'clock_radius':str(timing),'all_gates_pass':all(margins)}

def run():
    started=time.perf_counter()
    initial={p.name:digest(p) for p in BLOCK.iterdir() if p.is_file()}
    orbit=json.loads((BLOCK/'orbit_bound.json').read_text())
    tail=orbit['complete_valuation_tail'];K=tail['block_length']
    assert K==32
    # Negative-binomial generating function, evaluated and differentiated
    # exactly at x=1/4, includes every omitted valuation without a cutoff.
    retained=[Q(comb(k+13,13),4**k) for k in range(K)]
    exact_tail0=Q(4,3)**14-sum(retained,Q())
    exact_tail1=Q(14,3)*Q(4,3)**14-sum((k*u for k,u in enumerate(retained)),Q())
    assert 0<exact_tail0<=Q(tail['omitted_envelope_mass_upper'])
    assert 0<exact_tail1<=Q(tail['omitted_weighted_envelope_mass_upper'])

    consumer=load('_independent_block_review_consumer',BLOCK/'check_orbit.py')
    phase=consumer.check(orbit,bits=448)
    assert phase['verified'] and phase['actual_corner_lag_checks']==248

    fixtures=load('_independent_block_review_fixture',ROOT/'research/uncertain_transfer_2026_09/noise/demonstrate.py')
    fixtures.EPS_A=Q(120,10**14);fixtures.EPS_B=Q(120,10**11)
    approximation=json.loads((ROOT/'research/uncertain_transfer_2026_09/noise/approximation.json').read_text())
    old=json.loads((ROOT/'research/structured_transfer_2026_09/arithmetic/clock_bound.json').read_text())
    saved_data=json.loads((BLOCK/'data_h120.json').read_text())
    publication=json.loads((BLOCK/'publication_budget.json').read_text())
    assert publication['schema']=='orbit-clock-publication-budget-v1'
    assert {k:Q(v) for k,v in publication['fixed_contract'].items()}=={
        'amplitude':Q(4000),'frequency':Q(3),'sensor_radius':Q(1,25000),
        'mismatch_radius':Q(1,10**6),'clock_slope_radius':Q(120,10**14),
        'clock_offset_radius':Q(120,10**11),'correction_radius':Q(1,10**20),
        'normal_residual_upper':Q(1,10**30)}
    results=[]
    for design in ('multi','outer'):
        model=PhysicalModel(design,12,384)
        if design=='multi':
            fresh_data=fixtures.fixture(model)
            assert fresh_data['readings']==saved_data['readings']
            assert fresh_data['data_sha256']==saved_data['data_sha256']
        saved=json.loads((BLOCK/f'result_{design}_h120.json').read_text())
        ar=next(r for r in approximation['records'] if (r['design'],r['degree'])==(design,12))
        cr=next(r for r in orbit['records'] if r['design']==design)
        previous=next(r for r in old['records'] if r['design']==design)
        budget=scalar_budget(model.record,ar,cr,Q(saved['certificate']['normal_residual_upper']))
        assert budget['all_gates_pass']
        assert budget['complete_reading_radius']==saved['uncertainty_budget']['complete_reading_radius']
        nu=Q(budget['complete_reading_radius'])-Q(1,25000)-Q(1,10**20)
        certificate=verify(model,saved_data['readings'],saved['proposal'],Q(1,25000),nu,True)
        assert certificate['status']=='certified_under_declared_model'
        assert certificate['answer_a1_through_a50']==saved_data['truth_a1_through_a50']
        rho=Q(certificate['normal_residual_upper'])
        assert rho<=Q(saved['certificate']['normal_residual_upper'])<Q(1,10**30)
        assert certificate['residual_identity_audit']['componentwise_enclosures_overlap']
        assert scalar_budget(model.record,ar,cr,rho)['all_gates_pass']
        pair=scalar_budget(model.record,ar,previous,rho)
        assert pair['all_gates_pass']==(design=='multi')
        # Independently check every displayed component against its entire
        # coordinate contribution, using exact squared inequalities.
        display=next(r for r in publication['records'] if r['design']==design)
        assert display['degree']==12 and display['clock_multiplier']==120
        components={k:Q(v) for k,v in display['component_upper_bounds'].items()}
        assert set(components)=={'tail','sensor','mismatch','drift','clock','correction','residual'}
        future=scalar_budget(model.record,ar,cr,Q(1,10**30))
        total=Q(future['complete_reading_radius']);clock=Q(future['clock_radius'])
        family=total-clock-Q(1,25000)-Q(1,10**6)-Q(1,10**20)
        floors=1-Q(model.record['augmented_gram_defect'])
        for n in range(2,51):
            assert components['tail']>=Q(model.record['complete_coefficient_bias_upper'][n-1])
            assert components['residual']*floors>=n*n*Q(1,10**30)
            for key,amount in [('sensor',Q(1,25000)),('mismatch',Q(1,10**6)),
                               ('drift',family),('clock',clock),('correction',Q(1,10**20))]:
                assert components[key]>=0 and components[key]**2*floors>=n**4*amount**2
        assert sum(components.values(),Q())==Q(display['sum_component_upper_bounds'])<Q(1,2)
        assert Q(display['exact_coordinate_maximum'])<=sum(components.values(),Q())
        assert Q(display['sum_decimal'])==sum(components.values(),Q())
        assert all(Q(display['decimal_component_upper_bounds'][k])==v for k,v in components.items())
        results.append({'design':design,'raw_readings_reconstructed':8900,
            'physical_reconstruction_bits':384,'dual_residual_recomputed':True,
            'fresh_normal_residual_upper':str(rho),'all_49_integer_answers_verified':True,
            'new_exact_h120_gates':budget['passing_integer_gates'],
            'prior_pair_h120_gates':pair['passing_integer_gates'],
            'publication_component_inequalities_checked':49*7})
    for name,sha in initial.items():assert digest(BLOCK/name)==sha,('changed reviewed artifact',name)
    return {'schema':'independent-complete-orbit-review-v1','verified':True,
        'scope':'complete phase-block theorem and actual h=120 two-window consequence',
        'phase_replay_bits':448,'actual_corner_lag_checks':248,
        'complete_valuation_tails_checked_against_exact_generating_function':True,
        'exact_omitted_mass':str(exact_tail0),'exact_omitted_weighted_mass':str(exact_tail1),
        'all_odd_starting_integers_checked_by_proof':True,
        'arbitrary_allowed_coefficient_amplitudes_checked_by_proof':True,
        'nonlinear_shared_clock_remainder_checked_by_proof':True,
        'actual_inverse_results':results,'reviewed_artifact_sha256':initial,
        'reviewed_files_unchanged':True,'wall_seconds':time.perf_counter()-started}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    result=run()
    if a.write:(HERE/'block_review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='reviewed_artifact_sha256'},indent=2))
