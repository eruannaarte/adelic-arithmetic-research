"""Reproduce package checks with isolated subprocess imports and saved evidence.

Default is the fast mathematical consequence layer. --tests adds all focused
controls. --deep also rebuilds expensive defining-model certificate inputs.
"""
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PREFIX=HERE.relative_to(ROOT)


def main():
    p=argparse.ArgumentParser();p.add_argument('--tests',action='store_true');p.add_argument('--deep',action='store_true');a=p.parse_args()
    jobs=[]
    def add(label,*args):jobs.append((label,[sys.executable,*map(str,args)]))
    def local(name):return PREFIX/name
    add('P1 exact consequence',local('path1_preparation/checker.py'),local('path1_preparation/region.json'),local('path1_preparation/nominal.json'))
    add('P2 full phase and consequence',local('path2_harmonic/certificate_checker.py'))
    add('P3 exact consequence',local('path3_noise/check_consequences.py'))
    add('P4 exact remote and consequence',local('path4_realizability/check_certificate.py'))
    add('P4 refinement consequence',local('path4_realizability/check_certificate.py'),local('path4_realizability/refinement.json'))
    add('P5 exact transfer consequence',local('path5_resolution/check_certificate.py'))
    if a.tests or a.deep:
        add('P1 controls and complete nonlinear replay',local('path1_preparation/validate.py'))
        add('P2 15 controls','-m','unittest','discover','-s',local('path2_harmonic'),'-p','test_certificate.py','-v')
        add('P3 5 controls and weight/Gram replay',local('path3_noise/audit_checks.py'))
        add('P4 17 controls','-m','unittest','discover','-s',local('path4_realizability'),'-p','test_*.py','-v')
        add('P5 16 controls','-m','unittest','discover','-s',local('path5_resolution'),'-p','test_resolution.py','-v')
    if a.deep:
        add('P2 original baseline','arithmetic_observability_full_segre.py','--verify','arithmetic_observability_full_segre_certificate.json')
        add('P3 both remote and single complete replay',local('path3_noise/rebuild_dependencies.py'))
        add('P3 multiscale complete replay','verify_multiscale_certificate.py','--certificate','certificates/arithmetic_sensing_v_multiscale_end_to_end.json','--processes','4')
        add('P4 finite and Gram full replay',local('path4_realizability/query_certificate.py'))
        add('P4 higher-precision full replay',local('path4_realizability/query_certificate.py'),'--precision','256','--output',local('path4_realizability/refinement.json'))
        add('P4 independent check after replay',local('path4_realizability/check_certificate.py'))
        add('P4 refinement check after replay',local('path4_realizability/check_certificate.py'),local('path4_realizability/refinement.json'))
        add('P5 continuum baseline replay',local('path5_resolution/revalidate_baseline.py'))
        for left,right,file in [('1','3/2','cell_1_1p5.json'),('3/2','2','cell_1p5_2.json')]:
            add('P5 full cell '+left+'..'+right,local('path5_resolution/generate_certificate.py'),'--interval',left,right,'--output',local('path5_resolution/'+file))
        add('P5 assemble replay',local('path5_resolution/generate_certificate.py'),'--assemble',local('path5_resolution/cell_1_1p5.json'),local('path5_resolution/cell_1p5_2.json'),'--output',local('path5_resolution/certificate.json'))
        add('P5 independent check after replay',local('path5_resolution/check_certificate.py'))
    records=[];logs=[];start=time.monotonic()
    for name,cmd in jobs:
        t=time.monotonic();r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
        output=r.stdout+r.stderr
        record={'name':name,'command':['python',*cmd[1:]],'exit_code':r.returncode,'seconds':round(time.monotonic()-t,3)}
        records.append(record);logs.append(name+'\n'+output)
        print(('PASS ' if r.returncode==0 else 'FAIL ')+name,flush=True)
        if r.returncode:
            print(output);break
    mode='deep' if a.deep else 'tests' if a.tests else 'quick'
    passed=len(records)==len(jobs) and all(r['exit_code']==0 for r in records)
    record={'verified':passed,'mode':mode,'python':sys.version,'seconds':round(time.monotonic()-start,3),'checks':records}
    (HERE/('validation_'+mode+'.json')).write_text(json.dumps(record,indent=2)+'\n')
    (HERE/('validation_'+mode+'.log')).write_text('\n\n'.join(logs))
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
