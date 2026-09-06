"""Exact physical normalization with a verified source-relative error charge.

For raw rational y, use z=r*y with rational r near (1+t)^(-1/4). The error
charged to the existing decoder is physical: ||alpha*z-y||, not ||z-y/alpha||.
No unknown source amplitude, label, or floating fourth root is supplied.
"""
from fractions import Fraction as Q
from math import isqrt
import argparse, hashlib, importlib.util, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
GAIN=Q(4,3)


def exact(x):
    if type(x) not in (str,int,Q):raise ValueError('exact rational string, integer, or Fraction required')
    return Q(x)


def vector(data):
    if type(data) not in (list,tuple) or not data:raise ValueError('nonempty exact real vector required')
    return tuple(exact(x) for x in data)


def digest(data):
    return hashlib.sha256(json.dumps(list(map(str,data)),separators=(',',':')).encode()).hexdigest()


def perfect_fourth_root(x):
    k=isqrt(isqrt(x))
    return k if k**4==x else None


def verify_scale(receipt):
    if receipt['schema']!='physical-normalization-scale-v1':raise ValueError('normalization schema')
    fields=('time','sensor_relative_radius','numerical_relative_budget','measured_output_gain_upper',
            'inverse_normalization','relative_multiplier_error_upper','charged_physical_relative_radius')
    if any(type(receipt[k]) is not str for k in fields):raise ValueError('receipt rationals must be strings')
    t,eta,xi,K,r,e,charge=(exact(receipt[k]) for k in fields)
    if not (1<=t<=2 and eta>=0 and 0<=xi<K and r>0 and 0<=e<1):raise ValueError('normalization domains')
    if K!=GAIN+eta:raise ValueError('physical output gain omits a required contribution')
    # Taking positive fourth roots proves |alpha*r-1| <= e exactly.
    v=(1+t)*r**4
    if not ((1-e)**4<=v<=(1+e)**4):raise ValueError('physical multiplier error is not established')
    if charge!=K*e or not charge<=xi:raise ValueError('normalization exceeds physical error budget')
    return charge


def make_scale(tau,eta,xi='1/1000000000',max_refinements=1024):
    t,eta,xi=map(exact,(tau,eta,xi));K=GAIN+eta
    if not (1<=t<=2 and eta>=0 and 0<=xi<K):raise ValueError('invalid time or relative budget')
    if type(max_refinements) is not int or max_refinements<0:raise ValueError('invalid refinement limit')
    q=1+t
    a=perfect_fourth_root(q.numerator);b=perfect_fourth_root(q.denominator)
    if a is not None and b is not None:
        r=Q(b,a);error=Q(0);steps=0
    else:
        if xi==0:raise ValueError('zero budget needs an exact rational normalization')
        lo,hi=Q(3,4),Q(16,19)
        if not q*lo**4<=1<=q*hi**4:raise ValueError('initial inverse-root bracket')
        for steps in range(max_refinements+1):
            r=(lo+hi)/2
            # c=1/alpha is in [lo,hi]; |r/c-1| <= (hi-lo)/(2lo).
            error=(hi-lo)/(2*lo)
            if K*error<=xi:break
            if steps==max_refinements:raise ValueError('normalization refinement budget exhausted')
            if q*r**4<1:lo=r
            elif q*r**4>1:hi=r
            else:lo=hi=r
        else:raise ValueError('normalization failed to terminate')
    receipt={'schema':'physical-normalization-scale-v1','time':str(t),'sensor_relative_radius':str(eta),
             'numerical_relative_budget':str(xi),'measured_output_gain_upper':str(K),
             'inverse_normalization':str(r),'relative_multiplier_error_upper':str(error),
             'charged_physical_relative_radius':str(K*error),'rational_bisection_steps':steps,
             'source_norm_contract':'S>=I; physical sensor error <=eta*||u||_S; known exact time'}
    verify_scale(receipt)
    return receipt


def normalize(data,tau,eta,xi='1/1000000000',max_refinements=1024):
    y=vector(data)
    if not any(y):raise ValueError('zero observations excluded by the nonzero-source certificate')
    receipt=make_scale(tau,eta,xi,max_refinements)
    r=Q(receipt['inverse_normalization']);z=tuple(r*v for v in y)
    return {'scale':receipt,'raw_data_sha256':digest(y),'normalized_data_sha256':digest(z),
            'normalized_data':list(map(str,z))}


def verify_packet(data,packet):
    y=vector(data)
    if not any(y):raise ValueError('zero raw observations')
    charge=verify_scale(packet['scale']);r=Q(packet['scale']['inverse_normalization'])
    z=vector(packet['normalized_data'])
    if z!=tuple(r*v for v in y):raise ValueError('normalized data not the certified exact scaling')
    if packet['raw_data_sha256']!=digest(y) or packet['normalized_data_sha256']!=digest(z):raise ValueError('normalization data binding')
    return charge


def decoder_module(bank):
    """Isolate the predecessor's plain 'check' import without changing files."""
    if bank=='7':directory=HERE.parent/'resolution'
    elif bank in ('8','9'):directory=ROOT/'research/operational_transfer_2026_09/resolution'
    else:raise ValueError('unknown certified bank')
    prefix='_raw_physical_bank_'+bank
    def load(name,path):
        spec=importlib.util.spec_from_file_location(name,path)
        mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
    consumer=load(prefix+'_check',directory/'check.py')
    previous=sys.modules.get('check');sys.modules['check']=consumer
    try:return load(prefix+'_decoder',directory/'decoder.py')
    finally:
        if previous is None:sys.modules.pop('check',None)
        else:sys.modules['check']=previous


class PhysicalBank:
    def __init__(self,bank='8'):
        self.name=bank
        self.decoder=decoder_module(bank).CertifiedBank(bank)
        self.summary=self.decoder.summary

    def decode(self,data,tau,metric='L2',xi_budget='1/1000000000'):
        if metric not in self.decoder.profiles:raise ValueError('uncertified noise/source profile')
        y=vector(data)
        if len(y)!=len(self.decoder.bank):raise ValueError('wrong physical channel count')
        profile=self.decoder.profiles[metric];eta=Q(profile['sensor_relative_radius']);xi=exact(xi_budget)
        if not 0<=xi<=Q(profile['conditional_numerical_relative_radius']):raise ValueError('requested normalization budget outside spatial certificate')
        packet=normalize(y,tau,eta,xi)
        charge=verify_packet(y,packet)
        decision=self.decoder.decode(packet['normalized_data'],tau,metric,numerical_relative_radius=charge)
        return {'schema':'verified-physical-bank-answer-v1','bank':self.name,'profile':metric,
                'status':decision.status,'feasible_targets':list(decision.feasible_targets),
                'source_estimate':None if decision.estimate is None else list(map(str,decision.estimate)),
                'guaranteed_relative_source_accuracy':profile['source_relative_accuracy_target'] if decision.status=='unique' else None,
                'normalization':packet,
                'premise':'exact rational raw readings and time; acquisition error already included in declared sensor bound'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('data',type=Path,help='JSON list of exact unnormalized real readings')
    p.add_argument('--bank',choices=['7','8','9'],default='8');p.add_argument('--time',required=True)
    p.add_argument('--profile',default='L2');p.add_argument('--xi',default='1/1000000000');a=p.parse_args()
    print(json.dumps(PhysicalBank(a.bank).decode(json.loads(a.data.read_text()),a.time,a.profile,a.xi),indent=2))
