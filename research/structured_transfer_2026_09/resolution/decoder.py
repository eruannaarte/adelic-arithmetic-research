"""Exact rational raw decoding with separate forward and inverse uncertainty gates."""
from fractions import Fraction as Q
from pathlib import Path
import argparse, importlib.util, json, sys
import check
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
normalization=load('_structured_potential_normalization',HERE.parents[1]/'refined_transfer_2026_09/normalization/normalize.py')
prior=load('_structured_potential_prior_consumer',HERE.parents[1]/'uncertain_transfer_2026_09/resolution/check.py')

def exact(x):
    if type(x) not in (Q,int,str):raise ValueError('exact rational input required')
    return Q(x)
def solve2(matrix,rhs):
    a,b=matrix[0];c,d=matrix[1];det=a*d-b*c
    if b!=c or a<=0 or det<=0:raise ValueError('positive definite nominal Gram required')
    return ((d*rhs[0]-b*rhs[1])/det,(a*rhs[1]-c*rhs[0])/det)
def evaluate(p,t):
    answer=Q()
    for a in reversed(p):answer=answer*(t-Q(3,2))+a
    return answer

class StructuredBank:
    def __init__(self):
        self.prior_check=prior.check()
        self.directions=check.verify()
        self.profile=check.consequence()
        self.coefficients=check.kernel(check.PRIOR/'kernel.json')
    def matrices(self,t):
        t=exact(t)
        if not 1<=t<=2:raise ValueError('nominal time outside [1,2]')
        return {label:tuple(tuple(evaluate(self.coefficients[abs(row-label)][port],t) for port in (0,1)) for row in check.BANK) for label in range(490,511)}
    def decode(self,raw,nominal_time,actual_time_interval,potential_interval):
        t=exact(nominal_time)
        if type(actual_time_interval) not in (list,tuple) or len(actual_time_interval)!=2:raise ValueError('two exact time endpoints required')
        if type(potential_interval) not in (list,tuple) or len(potential_interval)!=2:raise ValueError('two exact potential endpoints required')
        lo,hi=map(exact,actual_time_interval);glo,ghi=map(exact,potential_interval)
        if not 1<=lo<=t<=hi<=2 or max(t-lo,hi-t)>check.H:raise ValueError('uncertified clock interval')
        if not Q(4,5)-check.DG<=glo<=ghi<=Q(4,5)+check.DG:raise ValueError('uncertified potential interval')
        raw=normalization.vector(raw)
        if len(raw)!=7:raise ValueError('exactly seven readings required')
        packet=normalization.normalize(raw,t,check.ETA,check.XI)
        charge=normalization.verify_packet(raw,packet)
        if charge>check.XI:raise ValueError('unverified normalization budget')
        z=tuple(map(Q,packet['normalized_data']));total=Q(self.profile['label_total_relative_radius']);b2=(total/Q(19,16))**2
        energy=sum((v*v for v in z),Q());accepted=[];estimates={}
        for label,P in self.matrices(t).items():
            G=tuple(tuple(sum((row[i]*row[j] for row in P),Q()) for j in (0,1)) for i in (0,1))
            rhs=tuple(sum((row[i]*value for row,value in zip(P,z)),Q()) for i in (0,1))
            adjusted=tuple(tuple(G[i][j]-b2*int(i==j) for j in (0,1)) for i in (0,1))
            witness=solve2(adjusted,rhs)
            if energy-sum((x*y for x,y in zip(rhs,witness)),Q())<=0:
                accepted.append(label);estimates[label]=solve2(G,rhs)
        status='unique' if len(accepted)==1 else ('abstain' if accepted else 'incompatible')
        return {'schema':'structured-potential-raw-answer-v1','status':status,'feasible_targets':accepted,'source_estimate':list(map(str,estimates[accepted[0]])) if status=='unique' else None,'guaranteed_relative_source_accuracy':'1/1000' if status=='unique' else None,'guaranteed_relative_source_error_upper':self.profile['source_relative_error_upper'] if status=='unique' else None,'nominal_time':str(t),'actual_time_interval':[str(lo),str(hi)],'potential_interval':[str(glo),str(ghi)],'normalization':packet,'transfer_budget':self.profile,'premise':'Actual finite H(g), shared time/potential within supplied intervals, exact fixed preparation/readout, and raw sensor norm <=1.1e-7 times nonzero source norm. Acquisition premises are not inferred from decoder residual.'}

def demonstrate():
    bank=StructuredBank();data=json.loads((HERE/'fixtures.json').read_text());results=[];worst=Q()
    for case in data['cases']:
        nominal=Q(case['nominal_time']);lo=max(Q(1),nominal-check.H);hi=min(Q(2),nominal+check.H)
        result=bank.decode(case['raw_data'],nominal,[lo,hi],[Q(4,5)-check.DG,Q(4,5)+check.DG])
        if result['status']!='unique' or result['feasible_targets']!=[case['source_label']]:raise ValueError('synthetic label recovery failed')
        error=sum((Q(a)-Q(b))**2 for a,b in zip(result['source_estimate'],case['source']))/Q(case['source_norm'])**2
        if not error<Q(1,1000)**2:raise ValueError('synthetic source recovery failed')
        worst=max(worst,error);result['observed_relative_source_error_squared']=str(error);results.append(result)
    return {'verified':True,'cases':results,'case_count':len(results),'maximum_observed_relative_source_error_upper':str(check.sqrtupper(worst)),'all_raw_normalization_budgets_verified':True,'prior_complete_time_floors_rechecked':bank.prior_check['all_case_covers_verified'],'structured_complete_time_directions_rechecked':bank.directions['independent_centered_consumer_verified']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();result=demonstrate()
    if a.write:(HERE/'decoded.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
