"""Bounded reuse of a prior numerical candidate; this file proves no floor."""
from pathlib import Path
import importlib.util,json,time
HERE=Path(__file__).resolve().parent
path=HERE.parents[1]/'refined_transfer_2026_09/resolution/discover.py'
spec=importlib.util.spec_from_file_location('_old_bank_discovery',path)
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
started=time.monotonic()
candidate=(-10,-8,-4,0,4,8,10)
result=old.refine(candidate)
output={'status':'floating candidate screening only; all mathematical conclusions use the separate exact certificate',
        'fixed_contract':'seven rows; minimum gap 2; offsets [-16,16]; eta=1.1e-7; relative source error<0.001; all targets and time [1,2]',
        'proposal_source':'A previously screened layout with strong source floor and no detected continuous-time alias',
        'candidates_tested_this_phase':1,'result':result,
        'six_row_search':'not performed after the seven-row improvement contract was certified',
        'elapsed_seconds':time.monotonic()-started}
(HERE/'discovery.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(output,indent=2))
