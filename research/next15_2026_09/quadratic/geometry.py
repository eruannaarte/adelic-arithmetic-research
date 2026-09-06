"""Q1: exact closest-label prefix geometry and genuine field witnesses.

The finite checker below needs only Python integers and Fractions. FLINT is
used for candidate discovery/factorization when generating Lucas certificates,
whose mathematical correctness is independently checked from modular powers.
"""
from fractions import Fraction as F
from itertools import combinations
from math import gcd,prod,isqrt
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
PRIMES=(2,3,5,7,11,13,17,19,23,29,31,37,41,43,47)
J=sum((F(1,n**4) for n in (5,20,45)),F())


def prefix(signs,N=50):
    values=[]
    for n in range(1,N+1):
        value=1;rem=n
        for p in PRIMES:
            e=0
            while rem%p==0:rem//=p;e+=1
            if e:value*=sum(signs[p]**k for k in range(e+1))
            if rem==1:break
        if rem!=1:raise ValueError('prime table too short')
        values.append(value)
    return values


def symbol(D,p):
    if D%p==0:return 0
    if p==2:return 1 if D%8 in (1,7) else -1
    x=pow(D%p,(p-1)//2,p)
    return -1 if x==p-1 else x


def lucas_proof(n,cache):
    from flint import fmpz
    if str(n) in cache:return
    if n==2:cache['2']={'base':1,'factors':[]};return
    factors=[(int(p),int(e)) for p,e in fmpz(n-1).factor()]
    for p,e in factors:lucas_proof(p,cache)
    a=2
    while not (pow(a,n-1,n)==1 and all(gcd(pow(a,(n-1)//p,n)-1,n)==1 for p,e in factors)):a+=1
    cache[str(n)]={'base':a,'factors':[[p,e] for p,e in factors]}


def check_prime(n,certificates,checked=None):
    if checked is None:checked=set()
    if n in checked:return
    if type(n) is not int or n<2:raise ValueError('invalid prime')
    row=certificates[str(n)]
    if n==2:
        if row!={'base':1,'factors':[]}:raise ValueError('bad base prime')
        checked.add(n);return
    factors=row['factors'];a=row['base']
    if not factors or len({p for p,e in factors})!=len(factors):raise ValueError('duplicate/empty factorization')
    if any(type(p) is not int or type(e) is not int or not(2<=p<n and e>=1) for p,e in factors):raise ValueError('bad factor')
    if prod(p**e for p,e in factors)!=n-1:raise ValueError('incomplete factorization')
    for p,e in factors:check_prime(p,certificates,checked)
    if type(a) is not int or not(1<a<n) or pow(a,n-1,n)!=1:raise ValueError('bad Lucas base')
    if any(gcd(pow(a,(n-1)//p,n)-1,n)!=1 for p,e in factors):raise ValueError('order condition failed')
    checked.add(n)


def witness(label,proofs):
    from flint import fmpz
    signs={p:(label-1 if p==5 else -1) for p in PRIMES}
    R=5 if label==1 else 1
    residues=[(8,5*pow(R,-1,8)%8)]
    for p in PRIMES[1:]:
        if signs[p]==0:r=1
        else:
            want=signs[p]*symbol(R,p)
            r=1 if want==1 else next(a for a in range(1,p) if symbol(a,p)==-1)
        residues.append((p,r))
    M=prod(m for m,r in residues)
    A=sum(r*(M//m)*pow(M//m,-1,m) for m,r in residues)%M
    q=A
    while q<=50 or not fmpz(q).is_prime():q+=M
    lucas_proof(q,proofs)
    D=R*q
    return {'label':label,'D':D,'R':R,'q':q,'residue':A,'modulus':M,'prefix':prefix(signs)}


def distances():
    return {f'{a}-{b}':str((b-a)**2*J+F((2*(b==2)-2*(a==2))**2,25**4)) for a,b in combinations(range(3),2)}


def check(doc):
    if doc['schema']!='quadratic-prefix-geometry-v1' or doc['N']!=50:raise ValueError('wrong geometry model')
    if F(doc['J'])!=J or doc['distance_squared']!=distances():raise ValueError('wrong exact distances')
    rows=doc['witnesses']
    if [r['label'] for r in rows]!=[0,1,2]:raise ValueError('label cover missing')
    for row in rows:
        q,R,D=row['q'],row['R'],row['D']
        check_prime(q,doc['prime_proofs'])
        if q<=50 or R!=(5 if row['label']==1 else 1) or D!=R*q or D%8!=5:raise ValueError('bad fundamental discriminant')
        signs={p:symbol(D,p) for p in PRIMES}
        if any(x!=(row['label']-1 if p==5 else -1) for p,x in signs.items()):raise ValueError('wrong splitting pattern')
        if row['prefix']!=prefix(signs):raise ValueError('wrong prefix')
    for left,right in combinations(rows,2):
        actual=sum((F((b-a)**2,n**4) for n,(a,b) in enumerate(zip(left['prefix'],right['prefix']),1)),F())
        if actual!=F(doc['distance_squared'][f'{left["label"]}-{right["label"]}']):raise ValueError('witness distance mismatch')
    # Any changed anchor has already more squared distance than every claimed minimum.
    if not all(F(x)<F(1,3**4) for x in doc['distance_squared'].values()):raise ValueError('anchor exclusion failed')
    if F(doc['universal_radius_squared'])!=J/4:raise ValueError('bad half-distance')
    return {'verified':True,'pairs':3,'genuine_fundamental_discriminants':[r['D'] for r in rows],
            'universal_radius_squared':str(J/4),'metric':'Euclidean normalized coefficient prefix; not full zeta samples'}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    target=HERE/'geometry.json'
    if a.write:
        proofs={};rows=[witness(label,proofs) for label in range(3)]
        doc={'schema':'quadratic-prefix-geometry-v1','N':50,'J':str(J),'distance_squared':distances(),
             'universal_radius_squared':str(J/4),'witnesses':rows,'prime_proofs':proofs}
        check(doc);target.write_text(json.dumps(doc,indent=2)+'\n')
    print(json.dumps(check(json.loads(target.read_text())),indent=2))
