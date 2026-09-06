#!/usr/bin/env python3
"""Nonmutating consolidated verification of the unified research package.

--deep adds complete inherited preparation ODE replay and the full finite-graph
diagnostic. New harmonic and polynomial model reconstructions always run.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,platform,re,subprocess,sys,time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
COUNTS={'framework':6,'harmonic':10,'preparation':10,'quadratic':7,'noise':8,'resolution':8}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deep',action='store_true');parser.add_argument('--output',type=Path)
    args=parser.parse_args();base=str(HERE.relative_to(ROOT));jobs=[]
    jobs.append(('framework.three_model_transfer',['-S',f'{base}/framework/check_applications.py']))
    for name,options in [('factored256',[]),('factored384',['--precision','384']),
                         ('raw256',['--independent']),('raw384',['--independent','--precision','384'])]:
        jobs.append((f'harmonic.{name}',[f'{base}/harmonic/uniform_collision.py',*options]))
    jobs.append(('preparation.record',['-S',f'{base}/preparation/calibration_bridge.py']))
    jobs.append(('quadratic.certificate',['-S',f'{base}/quadratic/joint_query.py']))
    jobs.append(('quadratic.independent_fields',['-S',f'{base}/quadratic/audit_independent.py']))
    jobs.append(('noise.exact',['-S',f'{base}/noise/check_certificate.py']))
    for precision in ('192','256'):
        jobs.append((f'noise.full_model_{precision}',[f'{base}/noise/polynomial_drift.py','--precision',precision]))
    for script in ('certificate','check'):
        jobs.append((f'resolution.{script}',['-S',f'{base}/resolution/{script}.py']))
    for chain in COUNTS:
        jobs.append((f'{chain}.tests',['-m','unittest','discover','-s',f'{base}/{chain}','-p','test_*.py','-v']))
    if args.deep:
        jobs.append(('preparation.full_ode_replay',['research/next15_2026_09/preparation/verify.py','--deep']))
        jobs.append(('resolution.full_graph_controls',[f'{base}/resolution/example.py']))
    env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
    start=time.monotonic();results=[];logs=[]
    for name,command_tail in jobs:
        begin=time.monotonic();command=[sys.executable,*command_tail]
        run=subprocess.run(command,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        passed=run.returncode==0;count=None
        if name.endswith('.tests'):
            match=re.search(r'Ran (\d+) tests? in',run.stdout);count=int(match.group(1)) if match else 0
            passed=passed and count==COUNTS[name.split('.')[0]]
        record={'name':name,'command':command,'exit_code':run.returncode,'passed':passed,'seconds':round(time.monotonic()-begin,3)}
        if count is not None:record['tests']=count
        results.append(record);logs.append(f'### {name}\n{run.stdout}\n')
        print(f"{'PASS' if passed else 'FAIL'} {name} ({record['seconds']:.3f}s)",flush=True)
        if not passed:print(run.stdout,flush=True)
    identity={}
    for p in sorted(HERE.rglob('*')):
        if p.is_file() and p.suffix in {'.py','.json'} and not (args.output and p.resolve()==args.output.resolve()):
            identity[str(p.relative_to(HERE))]=hashlib.sha256(p.read_bytes()).hexdigest()
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'python':platform.python_version(),
            'executable':sys.executable,'deep':args.deep,'job_count':len(results),
            'focused_tests':sum(x.get('tests',0) for x in results),'common_transfer_gates':687,
            'all_passed':all(x['passed'] for x in results),'seconds':round(time.monotonic()-start,3),
            'results':results,'file_identity_sha256':identity,
            'scope':'Complete new computations and consequences; unchanged d14 tails and central resolution premises are explicitly inherited. Physical preparation calibration NOT_RUN.'}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2)+'\n');args.output.with_suffix('.log').write_text('\n'.join(logs))
    print(f"{sum(x['passed'] for x in results)}/{len(results)} jobs; {report['focused_tests']} focused tests; {report['seconds']:.3f}s",flush=True)
    return 0 if report['all_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
