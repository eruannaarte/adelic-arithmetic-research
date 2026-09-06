"""Independent review replay of the six-channel joint transfer contract."""
from fractions import Fraction as Q
from pathlib import Path
from math import isqrt
import hashlib,json,sys,time
HERE=Path(__file__).resolve().parent;SPATIAL=HERE.parent/'spatial'
sys.path.insert(0,str(SPATIAL))
import check

def run():
    before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SPATIAL.iterdir() if p.is_file()}
    start=time.perf_counter();result=check.verify(bits=384)
    # Re-derive the combination independently, without check.consequence().
    h=d=Q(1,10**8);eta=Q(3,10**8);rho=xi=Q(1,10**9)
    F=Q(43,10**11);V=Q(68,10**8);mu=Q(361,256*10**9)
    remainder=h*h/2+128*h*d+Q(128,3)*d*d+(h+d)*Q(1,10**12)
    free=eta+rho+xi+remainder;tube=free+F
    if not tube<Q(13,400000000):raise ValueError('combined tube does not fit enlarged all-pair certificate')
    if not (Q(1,1000)-V)>0 or not free*free<(Q(1,1000)-V)**2*mu:raise ValueError('directional source gate')
    if not tube*tube<Q(1,1000)**2*mu:raise ValueError('coarse inverse comparison not passing')
    if Q(result['source_relative_error_upper'])>=Q(1,1000):raise ValueError('saved consumer accuracy')
    if result['case_cells']!=2688 or result['weighted_pair_certificate']['whole_cell_records']!=1280:raise ValueError('all-time coverage counts')
    rejected=[]
    for parameters in [(Q(2,10**8),d),(h,Q(2,10**8))]:
        try:check.consequence(h=parameters[0],dg=parameters[1])
        except ValueError:rejected.append(True)
        else:raise ValueError('changed uncertainty contract silently accepted')
    after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SPATIAL.iterdir() if p.is_file()}
    if before!=after:raise ValueError('review changed sealed spatial artifacts')
    return {'schema':'independent-six-row-review-v1','verified':True,'bits':384,
        'all_direction_cells_replayed':2688,'all_pair_source_records_replayed':1280,
        'independent_exact_tube_gate':str(tube),'independent_exact_nonlinear_remainder':str(remainder),
        'directional_source_gate_passes':True,'coarse_source_gate_also_passes':True,
        'changed_clock_and_potential_contracts_rejected':len(rejected),'spatial_files_unchanged':len(before),
        'wall_seconds':time.perf_counter()-start}
if __name__=='__main__':
    result=run();(HERE/'spatial_review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
