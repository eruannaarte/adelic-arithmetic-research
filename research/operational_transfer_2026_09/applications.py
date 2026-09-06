"""Consume both new applications through the unchanged general theorem gates.

The arithmetic residual premises are separately reconstructed by noise/replay.py;
the spatial interval premises are rechecked here. This adapter does not replace
the documented physical-model and infinite-tail reconstructions.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse, hashlib, importlib.util, json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def run(write=False):
    framework=load('_operational_general_transfer',ROOT/'research/transfer_theorem_2026_09/framework/transfer.py')
    spatial=load('_operational_spatial_consumer',HERE/'resolution/check.py')
    tail=load('_operational_tail_gate_consumer',ROOT/'research/transfer_theorem_2026_09/noise/check_certificate.py')
    evidence=json.loads((ROOT/'research/transfer_theorem_2026_09/noise/evidence.json').read_text())
    tail.check(evidence,extended=True)
    spatial_results={};cells=0
    for b in ('8','9'):
        summary=spatial.check(bank=b)
        cert=json.loads((HERE/('resolution/certificate_'+b+'.json')).read_text())
        for cell in cert['cells']:
            for record in cell['records']:
                gamma=Q(cert['center_singular_lower']);e=Q(record['variation_frobenius_upper']);w=Q(record['required_transformed_norm_upper'])
                assert framework.continuous_cell_gate(gamma*gamma,e,w*w)
                cells+=1
        for m in summary['metrics'].values():
            delta=Q(m['total_relative_radius'])
            assert framework.pair_gate(m['pair_approximate_map_floor'],delta,delta)
            assert framework.inverse_gate(m['individual_approximate_map_floor'],delta,m['source_relative_accuracy_target'])
        spatial_results[b]=summary['metrics']
    arithmetic={};coordinates=0
    for design in ('multi','outer'):
        record=next(r for r in evidence['designs'][design]['degrees'] if r['degree']==8)
        f=1-Q(record['augmented_gram_defect']);biases=list(map(Q,record['complete_coefficient_bias_upper']))
        for name in ('moderate','large'):
            key=design+'_'+name
            saved=json.loads((HERE/('noise/result_'+key+'.json')).read_text());cert=saved['certificate']
            assert cert['status']=='certified_under_declared_model'
            rho=Q(cert['normal_residual_upper']);solve_error=framework.normal_residual_error_bound(f,rho)
            total=sum((Q(cert[k]) for k in ('sensor_radius','nonpolynomial_drift_radius','digital_correction_radius')),Q())
            assert total==Q(cert['joint_data_error_radius'])
            for n in range(2,51):
                support_sum=2*(biases[n-1]+n*n*solve_error)
                assert framework.strict_scalar_gate(1,support_sum,Q(n**4)/f,total)
                coordinates+=1
            arithmetic[key]={'coordinate_gates':49,'normal_residual_error_upper':str(solve_error),
                             'joint_data_error_radius':str(total)}
    files=['resolution/certificate_8.json','resolution/certificate_9.json','resolution/obstruction_7.json',
           'noise/data_moderate.json','noise/data_large.json']
    files += ['noise/result_'+d+'_'+n+'.json' for d in ('multi','outer') for n in ('moderate','large')]
    result={'verified':True,'unchanged_framework':'research/transfer_theorem_2026_09/framework/transfer.py',
            'whole_time_cell_transfer_gates':cells,'global_pair_and_inverse_profiles':sum(map(len,spatial_results.values())),
            'arithmetic_coordinate_transfer_gates':coordinates,'arithmetic':arithmetic,'spatial':spatial_results,
            'input_sha256':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in files}}
    if write:(HERE/'applications.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('arithmetic','spatial','input_sha256')},indent=2));return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');run(p.parse_args().write)
