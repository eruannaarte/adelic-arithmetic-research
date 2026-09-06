"""Reproduce three models' numerical gates through one exact transfer function.

Model checkers and complete proofs establish the supports and dual gains.
This adapter independently checks their scalar algebra and error semantics.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util
import json
from directional import strict_radius_squared

HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def check():
    joint=load_module('_common_joint',PACKAGE/'quadratic/joint_query.py')
    qc=json.loads((PACKAGE/'quadratic/certificate.json').read_text());joint.check(qc)
    gram_q=F(qc['gram_q']);quadratic_count=0
    for row in qc['strata']:
        for pair in row['pairs']:
            S=F(pair['squared_distance']);h=F(pair['tail_support'])
            actual=strict_radius_squared(S,h,h,S/(1-gram_q))
            if actual!=F(pair['radius_squared_sufficient']):raise ValueError('quadratic transfer mismatch')
            quadratic_count+=1

    noise=load_module('_common_polynomial',PACKAGE/'noise/check_certificate.py')
    nc=json.loads((PACKAGE/'noise/evidence.json').read_text());noise.check(nc)
    xi=F(nc['inputs']['correction_radius']);noise_count=0;design_count=0
    for design in nc['designs'].values():
        for record in design['degrees']:
            if not record['rounding_certified']:continue
            eta=F(record['declared_sensor_radius']);qa=F(record['augmented_gram_defect_upper'])
            bounds=[]
            for n in range(2,51):
                h=F(record['complete_decoded_bias_upper'][n-1]);g2=F(n**4)/(1-qa)
                r2=strict_radius_squared(1,h,h,g2)
                if (eta+xi)**2>=r2:raise ValueError('digital correction/noise gate fails')
                bounds.append(r2);noise_count+=1
            if min(bounds)!=F(record['sufficient_total_radius_squared']):raise ValueError('polynomial transfer mismatch')
            design_count+=1

    prep=load_module('_common_preparation',PACKAGE/'preparation/calibration_bridge.py')
    pc=prep.verify_saved()
    delta=F(pc['record']['target_diameter']);eta=F(pc['record']['readout_noise_radius'])
    local=list(map(F,pc['local_uncertainty_radii']));shared=list(map(F,pc['shared_systematic_radii']))
    limits=[];prep_count=0
    for i in range(3):
        k=F(pc['row_contraction'][i]);gain=F(pc['weighted_noise_gains'][i])
        h=sum((F(v)*r for v,r in zip(pc['local_projected_gains'][i],local)),F())
        h+=sum((F(v)*r for v,r in zip(pc['shared_projected_gains'][i],shared)),F())
        if not 0<=k<1:raise ValueError('nonlinear contraction not valid')
        r2=strict_radius_squared(delta*(1-k),h,h,gain*gain)
        if eta**2>r2:raise ValueError('preparation diameter gate fails')
        limit=(delta*(1-k)/2-h)/gain
        if limit*limit!=r2:raise ValueError('preparation transfer mismatch')
        limits.append(limit);prep_count+=1
    if min(limits)!=F(pc['maximum_weighted_readout_noise_radius']):raise ValueError('calibration noise boundary differs')
    if (quadratic_count,noise_count,design_count,prep_count)!=(243,441,9,3):raise ValueError('incomplete application coverage')
    return {'verified':True,'models':3,'quadratic_pair_gates':quadratic_count,
            'polynomial_coordinate_gates':noise_count,'polynomial_design_degree_pairs':design_count,
            'nonlinear_preparation_gates':prep_count,'total_scalar_gates':quadratic_count+noise_count+prep_count,
            'scope':'exact scalar transfer after separately checked model-specific support and gain premises'}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=check()
    if args.write:(HERE/'application_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
