"""Common transfer consequences, bound to the separately checked new models.

This adapter consumes the unchanged transfer library. Physical kernel, weighted
norm, and actual normal-residual replays remain separate proof premises.
"""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import argparse, hashlib, importlib.util, json, sys

HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent
ROOT=HERE.parents[2]
PRIOR=ROOT/'research/transfer_theorem_2026_09'


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod
    spec.loader.exec_module(mod);return mod


T=load('_refined_unchanged_common_transfer',PRIOR/'framework/transfer.py')


def need(value,message):
    if not value:raise ValueError(message)


def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ceil_grid(x,denominator=10**12):
    x=Q(x)*denominator
    return Q(-((-x.numerator)//x.denominator),denominator)


def spatial():
    folder=PACKAGE/'resolution'
    consumer=load('_refined_spatial_consumer',folder/'check.py')
    doc=read(folder/'certificate_7.json')
    checked=consumer.check(doc,bank='7')
    need(checked['all_case_covers_verified'] and
         (checked['individual_cases'],checked['pair_cases'])==(21,210),
         'complete physical spatial consumer failed')
    gamma=Q(doc['center_singular_lower']);counts={2:0,4:0}
    # Reuse the established model/cell premises, and independently pass every
    # cell through the common library's square-root-free transfer predicate.
    for cell in doc['cells']:
        for row in cell['records']:
            dim=2*len(row['case'])
            R=[list(map(Q,r)) for r in row['preconditioner']]
            r2=sum((v*v for r in R for v in r),Q())
            f=Q(doc['unnormalized_source_floor' if dim==2 else 'unnormalized_pair_floor'])
            e=Q(row['variation_frobenius_upper'])
            need(T.continuous_cell_gate(gamma*gamma,e,f*r2),
                 'common full-cell transfer differs from spatial consumer')
            counts[dim]+=1
    p=checked['metrics']['L2']
    total=Q(p['total_relative_radius'])
    individual=Q(p['individual_approximate_map_floor'])
    pair=Q(p['pair_approximate_map_floor'])
    accuracy=Q(998507,10**9)
    need(total==Q(51,500000000),'fixed spatial budget changed')
    need(T.pair_gate(pair,total,total),'common target separation fails')
    need(T.inverse_gate(individual,total,accuracy),'common source accuracy fails')
    need(sum(counts.values())==checked['whole_cell_records']==3391,
         'common spatial cell count differs')
    return {'passed':True,'bank_rows':checked['direct_rows'],
            'separate_individual_cases':21,'separate_pair_cases':210,
            'nonempty_cells':checked['nonempty_time_cells'],
            'individual_cell_gates':counts[2],'pair_cell_gates':counts[4],
            'whole_cell_gates':sum(counts.values()),'global_pair_gates':1,'global_inverse_gates':1,
            'sensor_relative_radius':p['sensor_relative_radius'],
            'model_relative_radius':p['operator_relative_radius'],
            'conditional_computed_data_radius':p['conditional_numerical_relative_radius'],
            'total_radius':str(total),'individual_floor':str(individual),'pair_floor':str(pair),
            'strict_source_relative_error_upper':str(accuracy),
            'source_accuracy_squared_fraction_of_target':str(total**2/(individual*Q(1,1000)**2)),
            'pair_noise_squared_fraction_of_floor':str(2*total**2/pair),
            'premise':'complete kernel reconstruction and exact rational normalized data, or separately certified computed-data error'}


def arithmetic():
    folder=PACKAGE/'noise'
    consequence_consumer=load('_refined_weighted_consequences',folder/'consequences.py')
    checked=consequence_consumer.check()
    need(checked['verified'] and checked['integer_gates_checked']==98,
         'weighted arithmetic independent consequences incomplete')
    approximation=read(folder/'approximation.json')
    physical=read(folder/'checked_approximation.json')
    need(approximation['schema']=='weighted-sinusoidal-approximation-v1' and
         physical['schema']=='weighted-sinusoidal-checked-v1','weighted schema changed')
    need([r['design'] for r in approximation['designs']]==['multi','outer'] and
         [r['design'] for r in physical['designs']]==['multi','outer'],
         'weighted design coverage changed')
    need(physical['verified'] and physical['certificate_sha256']==sha(folder/'approximation.json'),
         'weighted physical replay does not bind current approximation')
    need(physical['polynomial_residual_bounds_checked']==24 and
         physical['weighted_moment_bounds_checked']==6 and
         physical['exact_parity_and_physical_symmetry_checked'],
         'weighted full-family physical premises incomplete')
    need(approximation['degree']==8 and approximation['frequency_limit']=='1' and
         approximation['measurement_count']==8900,'family contract changed')
    prior=read(PRIOR/'noise/evidence.json')
    designs=[];gates=0;old_failures=0
    for r in approximation['designs']:
        design=r['design'];result=read(folder/('result_'+design+'.json'))
        cert=result['certificate'];family=result['family_certificate']
        need(cert['status']=='certified_under_declared_model' and cert['degree']==8,
             'actual augmented solve not certified')
        e=next(e for e in prior['designs'][design]['degrees'] if e['degree']==8)
        f=1-Q(e['augmented_gram_defect'])
        need(Q(cert['gram_floor'])==f>0,'Gram floor differs from complete-tail premise')
        rho=Q(cert['normal_residual_upper'])
        eta=Q(cert['sensor_radius']);xi=Q(cert['digital_correction_radius'])
        # Rationally reconstruct the uniform phase/frequency bound from the
        # separately verified polynomial norms and complete remainder moments.
        norms={e['order']:Q(e['weighted_residual_norm_upper']) for e in r['approximants']}
        moments={int(k):Q(v) for k,v in r['weighted_monomial_norm_upper'].items()}
        odd=sum((norms[k]/factorial(k) for k in range(9,20,2)),Q())+moments[21]/factorial(21)
        even=sum((norms[k]/factorial(k) for k in range(10,21,2)),Q())+moments[22]/factorial(22)
        factor=max(odd,even)
        need(factor==Q(r['uniform_phase_frequency_factor']),'uniform family transfer differs')
        need(family['amplitude_bound']=='20000' and family['frequency_limit']=='1' and
             family['phase']=='arbitrary real','applied family differs')
        nu=20000*factor
        need(Q(cert['nonpolynomial_drift_radius'])==Q(family['computed_drift_radius'])==nu,
             'applied physical drift budget differs')
        need(eta==Q(1,25000) and xi==Q(1,10**20),'sensor or correction budget differs')
        radius=eta+nu+xi
        need(radius==Q(cert['joint_data_error_radius']),'joint uncertainty sum differs')
        residual_error=T.normal_residual_error_bound(f,rho)
        bad=0;max_error=Q()
        coordinates={r['n']:r for r in cert['coordinates']}
        need(set(coordinates)==set(range(2,51)),'coordinate coverage')
        for n in range(2,51):
            bias=Q(e['complete_coefficient_bias_upper'][n-1])
            support=2*(bias+n*n*residual_error)
            gain2=Q(n**4)/f
            need(T.strict_scalar_gate(1,support,gain2,radius),
                 'common weighted integer transfer fails')
            # This comparison is failure of an older sufficient bound, never
            # an impossibility claim about the physical data or drift.
            bad+=not T.strict_scalar_gate(1,support,gain2,eta+Q(20000,factorial(9))+xi)
            error=Q(coordinates[n]['coordinate_error_upper'])
            need(error<Q(1,2),'coefficient enclosure exceeds rounding threshold')
            max_error=max(max_error,error);gates+=1
        previous_check=next(c for c in checked['designs'] if c['design']==design)
        need(bad==previous_check['old_pointwise_failed_gates']==47,
             'old pointwise comparison differs')
        old_failures+=bad
        designs.append({'design':design,'degree':8,'unknown_integer_gates':49,
                        'amplitude_bound':'20000','normalized_frequency_limit':'1',
                        'phase':'arbitrary real','uniform_weighted_factor':str(factor),
                        'nonpolynomial_radius':str(nu),'sensor_radius':str(eta),
                        'correction_radius':str(xi),'joint_reading_radius':str(radius),
                        'actual_normal_residual_upper':str(rho),
                        'coefficient_error_upper_rounded_outward':str(ceil_grid(max_error)),
                        'old_pointwise_sufficient_gates_failed':bad})
    need(gates==98,'common arithmetic count differs')
    return {'passed':True,'scalar_integer_gates':gates,'designs':designs,
            'older_sufficient_gates_failed':old_failures,
            'family_factors_reconstructed':2,
            'physical_weighted_norm_premises':{'polynomial_norms':24,'moments':6,'hash_bound':True},
            'premise':'complete infinite tail, known a(1)=1, declared weighted sensor/drift bounds, and physical residual replay on the bound data and proposals'}


def normalization(spatial_result):
    folder=PACKAGE/'normalization';doc=read(folder/'evidence.json')
    mod=load('_refined_physical_normalization',folder/'normalize.py')
    profiles={('7','L2'):Q(1,10**7),('8','L2'):Q(23,10**8),
              ('8','L2_original_noise'):Q(3,10**7),('9','L2'):Q(3,10**7)}
    for bank in ('8','9'):
        for name in ('declared_H1','natural_discrete_H1'):profiles[bank,name]=Q(3,10**8)
    expected={(b,p,t,j) for b,p in profiles for t in ('1','3/2','2') for j in (490,500,510)}
    need(doc['verified'] and doc['case_count']==72 and doc['bank_profiles']==8,
         'raw normalization case contract')
    seen=set();charges=[];seven=[]
    mu=Q(spatial_result['individual_floor']);lam=Q(spatial_result['pair_floor'])
    need((mu,lam)==(Q(13357,1280000000000),Q(361,12800000000000000)),
         'seven-bank transfer floors changed')
    rho=Q(spatial_result['model_relative_radius']);accuracy=Q(spatial_result['strict_source_relative_error_upper'])
    for row in doc['cases']:
        key=(row['bank'],row['profile'],row['time'],row['source_label'])
        need(key in expected and key not in seen,'unknown or duplicate raw normalization case');seen.add(key)
        eta=profiles[key[:2]];packet=row['normalization'];scale=packet['scale']
        need(scale['time']==row['time'] and Q(scale['sensor_relative_radius'])==eta and
             Q(scale['numerical_relative_budget'])==Q(1,10**9),'raw scale profile binding')
        need(len(row['raw_readings'])==int(row['bank']),'physical row count differs')
        charge=mod.verify_packet(row['raw_readings'],packet)
        need(0<=charge<=Q(1,10**9),'raw scale charge exceeds xi')
        charges.append(charge)
        if row['bank']=='7':
            total=eta+rho+charge
            need(T.pair_gate(lam,total,total),'normalized seven-bank target gate')
            need(T.inverse_gate(mu,total,accuracy),'normalized seven-bank source gate')
            seven.append({'time':row['time'],'fixture_source_label':row['source_label'],
                          'source_amplitude_scale':row['source_norm_scale'],
                          'charged_physical_relative_radius':str(charge),
                          'total_relative_radius':str(total),
                          'target_gate_passed':True,'source_gate_passed':True})
    need(seen==expected and len(seven)==9,'raw case coverage incomplete')
    return {'passed':True,'verified_raw_packets':len(seen),'bank_profiles':len(profiles),
            'all_packet_charges_within_xi':True,'maximum_actual_charge':str(max(charges)),
            'seven_bank_pair_gates':len(seven),'seven_bank_inverse_gates':len(seven),
            'seven_bank_cases':seven,
            'premise':'exact raw input and time, declared sensor calibration, and previously proved physical response gain; synthetic fixture promise replay remains separate'}


def add_normalization(result):
    need(result['passed'] and result['successful_common_transfer_gates']==3491,
         'base adapter coverage changed')
    for relative,digest in result['input_sha256'].items():
        need(sha(ROOT/relative)==digest,'base adapter input changed; run full check')
    result['normalization']=normalization(result['spatial'])
    result['successful_common_transfer_gates']+=18
    for p in (PACKAGE/'normalization/evidence.json',PACKAGE/'normalization/normalize.py'):
        result['input_sha256'][str(p.relative_to(ROOT))]=sha(p)
    return result


def check():
    spatial_result=spatial();arithmetic_result=arithmetic()
    inputs=[PRIOR/'framework/transfer.py',PRIOR/'framework/PROOFS.md',
            PRIOR/'resolution/kernel.json',PACKAGE/'resolution/certificate_7.json',
            PACKAGE/'resolution/check.py',PRIOR/'noise/evidence.json',
            PACKAGE/'noise/approximation.json',PACKAGE/'noise/checked_approximation.json',
            PACKAGE/'noise/check_approximation.py',PACKAGE/'noise/data.json',
            PACKAGE/'noise/result_multi.json',PACKAGE/'noise/result_outer.json',
            PACKAGE/'noise/consequences.py']
    result={'schema':'refined-common-transfer-applications-v1','passed':True,
            'unchanged_transfer_library':str((PRIOR/'framework/transfer.py').relative_to(ROOT)),
            'spatial':spatial_result,'arithmetic':arithmetic_result,
            'successful_common_transfer_gates':spatial_result['whole_cell_gates']+2+arithmetic_result['scalar_integer_gates'],
            'input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in inputs},
            'scope':'shared theorem consequences; model reconstruction, calibration, and physical residual verification remain separate premises'}
    if (PACKAGE/'normalization/evidence.json').exists():add_normalization(result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true')
    p.add_argument('--append-normalization',action='store_true',
                   help='extend the existing successful base run after rehashing every bound input')
    args=p.parse_args()
    if args.append_normalization:
        result=read(HERE/'applications.json')
        # This explicitly uses the already completed full consumer run. Every
        # physical and consumer input must be byte-identical to that run.
        result=add_normalization(result)
        result['base_run_reused_for_normalization']={'all_previous_inputs_rehashed_unchanged':True,
            'scope':'3,491 base gates established in the earlier full adapter run; 72 packets and 18 new gates executed now'}
    else:result=check()
    if args.write:(HERE/'applications.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
